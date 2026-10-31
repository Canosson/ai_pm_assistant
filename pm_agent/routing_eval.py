"""Routing eval: does a router pick the right skill for a PM prompt?

A router sees only each skill's name and description, like the real agent does. The lexical router
is an offline baseline (a floor). Plug in a model-backed router to measure the real agent.

    python -m pm_agent.routing_eval --min-accuracy 0.9
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
import threading
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Callable, Mapping, Sequence

from pm_agent.skills import Skill, description_tokens, load_skills, routing_text

ROOT = Path(__file__).resolve().parent.parent
Router = Callable[[str, Sequence[Skill]], str]


@dataclass(frozen=True)
class Case:
    prompt: str
    expected: str
    hard: bool = False


@dataclass(frozen=True)
class Confusion:
    prompt: str
    expected: str
    got: str


@dataclass(frozen=True)
class Report:
    total: int
    correct: int
    hard_total: int
    hard_correct: int
    per_skill: Mapping[str, tuple[int, int]]  # skill -> (correct, total)
    confusions: tuple[Confusion, ...]

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    @property
    def hard_accuracy(self) -> float:
        return self.hard_correct / self.hard_total if self.hard_total else 1.0


def load_cases(path: Path) -> tuple[Case, ...]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    cases = []
    for index, item in enumerate(raw):
        for key in ("prompt", "expected"):
            if not item.get(key):
                raise ValueError(f"case {index}: missing '{key}'")
        cases.append(Case(item["prompt"], item["expected"], bool(item.get("hard", False))))
    return tuple(cases)


def _collect_answers(
    router: Router, skills: Sequence[Skill], cases: Sequence[Case], workers: int
) -> list[str]:
    """Router answers in case order. The first failure stops every case that has not started yet, so
    a bad key or an outage cannot burn through (and bill) the rest of a paid run."""
    if workers == 1:
        return [router(case.prompt, skills) for case in cases]
    stop = threading.Event()

    def guarded(case: Case) -> str:
        if stop.is_set():  # an earlier case already failed: do not start (or pay for) this one
            return ""
        try:
            return router(case.prompt, skills)
        except BaseException:
            stop.set()
            raise

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(guarded, case) for case in cases]
        try:
            return [future.result() for future in futures]
        except BaseException:
            stop.set()
            raise


def evaluate(
    router: Router, skills: Sequence[Skill], cases: Sequence[Case], workers: int = 1
) -> Report:
    if workers < 1:
        raise ValueError(f"workers must be at least 1, got {workers}")
    names = {s.name for s in skills}
    per_skill: dict[str, list[int]] = {}
    confusions: list[Confusion] = []
    correct = hard_total = hard_correct = 0
    answers = _collect_answers(router, skills, cases, workers)
    for case, got in zip(cases, answers):
        ok = got in names and got == case.expected
        correct += ok
        hard_total += case.hard
        hard_correct += case.hard and ok
        tally = per_skill.setdefault(case.expected, [0, 0])
        tally[0] += ok
        tally[1] += 1
        if not ok:
            confusions.append(Confusion(case.prompt, case.expected, got))
    return Report(
        total=len(cases), correct=correct, hard_total=hard_total, hard_correct=hard_correct,
        per_skill=MappingProxyType({k: (v[0], v[1]) for k, v in sorted(per_skill.items())}),
        confusions=tuple(confusions),
    )


def _stem(word: str) -> str:
    return word[:-1] if word.endswith("s") and len(word) > 3 else word


def _terms(text: str) -> Counter[str]:
    return Counter(_stem(w) for w in description_tokens(text))


NAME_WEIGHT = 2


def _name_terms(name: str) -> Counter[str]:
    """Words of a skill name, each counted NAME_WEIGHT times (the name is the strongest signal)."""
    return Counter({_stem(w): NAME_WEIGHT for w in description_tokens(name.replace("-", " "))})


def lexical_router(prompt: str, skills: Sequence[Skill]) -> str:
    """TF-IDF cosine between the prompt and each skill's name plus routing text."""
    docs = {s.name: _name_terms(s.name) + _terms(routing_text(s.description)) for s in skills}
    doc_count = len(docs)
    df = Counter(term for terms in docs.values() for term in terms)
    idf = {term: math.log((doc_count + 1) / (count + 1)) + 1 for term, count in df.items()}

    def vector(terms: Counter[str]) -> dict[str, float]:
        return {t: c * idf.get(t, 1.0) for t, c in terms.items()}

    def cosine(a: dict[str, float], b: dict[str, float]) -> float:
        dot = sum(w * b.get(t, 0.0) for t, w in a.items())
        norm = math.sqrt(sum(w * w for w in a.values())) * math.sqrt(sum(w * w for w in b.values()))
        return dot / norm if norm else 0.0

    query = vector(_terms(prompt))
    return max(docs, key=lambda name: (cosine(query, vector(docs[name])), name))


ROUTERS: Mapping[str, Router] = MappingProxyType({"lexical": lexical_router})


def format_report(report: Report, limit: int = 8) -> str:
    worst = sorted(((c / t, name, c, t) for name, (c, t) in report.per_skill.items()))[:limit]
    pairs = Counter((c.expected, c.got) for c in report.confusions).most_common(limit)
    lines = [
        f"accuracy {report.accuracy:.1%} ({report.correct}/{report.total})"
        f"   hard {report.hard_accuracy:.1%} ({report.hard_correct}/{report.hard_total})",
        "weakest skills:",
        *[f"  {name:28} {c}/{t}" for _, name, c, t in worst],
        "most common confusions (expected -> got):",
        *[f"  {n}x {exp} -> {got}" for (exp, got), n in pairs],
    ]
    return "\n".join(lines)


def sample_cases(cases: Sequence[Case], limit: int | None) -> tuple[Case, ...]:
    """Evenly spaced subset, so a small run still touches every part of the case file."""
    if limit is None or limit >= len(cases):
        return tuple(cases)
    return tuple(cases[(i * len(cases)) // limit] for i in range(limit))


def _run_llm(args: argparse.Namespace, skills: Sequence[Skill], cases: Sequence[Case]):
    from pm_agent.llm_router import LLMRouter, estimate_cost, make_client

    average_chars = sum(len(c.prompt) for c in cases) // max(len(cases), 1)
    estimate = estimate_cost(skills, calls=len(cases), prompt_chars=average_chars, model=args.model)
    print(
        f"{estimate.calls} calls to {estimate.model} (effort {args.effort}): estimated "
        f"${estimate.low_usd:.2f}-${estimate.high_usd:.2f} "
        f"(low = prompt caching works, ~150 output tokens per call; "
        f"high = no caching, ~1500 output tokens per call). An estimate, not a quote."
    )
    if args.dry_run:
        return None
    if not args.confirm_spend:
        print("Refusing to spend money without --confirm-spend (use --dry-run to only estimate).",
              file=sys.stderr)
        raise SystemExit(2)
    router = LLMRouter(make_client(), model=args.model, effort=args.effort)
    report = evaluate(router, skills, cases, workers=args.workers)
    usage = router.usage()
    print(f"usage: {usage.calls} calls, {usage.input_tokens} in, {usage.output_tokens} out, "
          f"{usage.cache_read_tokens} cache-read, {usage.failures} unusable replies")
    return report


def main(argv: Sequence[str] | None = None) -> int:
    from pm_agent.llm_router import DEFAULT_EFFORT, DEFAULT_MODEL

    parser = argparse.ArgumentParser(description="Evaluate skill routing.")
    parser.add_argument("--router", choices=[*sorted(ROUTERS), "llm"], default="lexical")
    parser.add_argument("--cases", type=Path, default=ROOT / "evals" / "routing_cases.json")
    parser.add_argument("--skills", type=Path, default=ROOT / "skills")
    parser.add_argument("--min-accuracy", type=float, default=0.0)
    parser.add_argument("--limit", type=int, help="evaluate an evenly spaced subset of N cases")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="llm router only")
    parser.add_argument("--effort", default=DEFAULT_EFFORT, help="llm router only")
    parser.add_argument("--workers", type=int, default=4, help="llm router only: parallel requests")
    parser.add_argument("--dry-run", action="store_true", help="llm router: print the estimate and stop")
    parser.add_argument("--confirm-spend", action="store_true", help="llm router: allow real API calls")
    args = parser.parse_args(argv)
    if args.limit is not None and args.limit < 1:
        parser.error("--limit must be at least 1")
    if args.workers < 1:
        parser.error("--workers must be at least 1")
    skills = load_skills(args.skills)
    cases = sample_cases(load_cases(args.cases), args.limit)
    if not cases:
        parser.error(f"no cases found in {args.cases}")  # an empty set would pass any accuracy gate
    try:
        if args.router == "llm":
            report = _run_llm(args, skills, cases)
            if report is None:
                return 0
        else:
            report = evaluate(ROUTERS[args.router], skills, cases)
    except SystemExit as stop:
        return int(stop.code or 0)
    except Exception as error:  # CLI boundary: show the cause (auth, network, SDK) without a traceback
        print(f"routing eval failed: {type(error).__name__}: {error}", file=sys.stderr)
        return 1
    print(format_report(report))
    return 0 if report.accuracy >= args.min_accuracy else 1


if __name__ == "__main__":
    sys.exit(main())

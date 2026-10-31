"""Routing eval harness: case file integrity, scoring, confusions, lexical baseline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path

import pytest

from pm_agent.routing_eval import Case, evaluate, lexical_router, load_cases, main
from pm_agent.skills import load_skills

ROOT = Path(__file__).resolve().parent.parent
SKILLS = load_skills(ROOT / "skills")
CASES = load_cases(ROOT / "evals" / "routing_cases.json")
NAMES = {s.name for s in SKILLS}


def test_every_expected_skill_exists_and_has_three_plain_cases() -> None:
    assert {c.expected for c in CASES} <= NAMES
    plain = Counter(c.expected for c in CASES if not c.hard)
    assert all(plain[name] >= 3 for name in NAMES), {n: plain[n] for n in NAMES if plain[n] < 3}


MAX_NAME_ECHO_SHARE = 0.10


def test_prompts_are_unique_and_rarely_echo_the_skill_name() -> None:
    # PMs do say "release notes" or "product strategy", so a few echoes are realistic; but if many
    # prompts contain the skill name the eval degrades into string matching.
    prompts = [c.prompt.lower() for c in CASES]
    assert len(prompts) == len(set(prompts))
    echoes = [c.prompt for c in CASES if c.expected.replace("-", " ") in c.prompt.lower()]
    assert len(echoes) / len(CASES) <= MAX_NAME_ECHO_SHARE, echoes


def test_hard_cases_cover_lookalike_boundaries() -> None:
    hard = [c for c in CASES if c.hard]
    assert len(hard) >= 15
    assert len({c.expected for c in hard}) >= 15


def test_perfect_router_scores_100_percent() -> None:
    oracle = {c.prompt: c.expected for c in CASES}
    report = evaluate(lambda prompt, skills: oracle[prompt], SKILLS, CASES)
    assert report.accuracy == 1.0 and report.hard_accuracy == 1.0
    assert report.confusions == ()


def test_wrong_router_records_confusions_per_skill() -> None:
    cases = (Case("a prompt", "rice-prioritization", False), Case("b prompt", "kano-model", True))
    report = evaluate(lambda prompt, skills: "cost-of-delay", SKILLS, cases)
    assert report.accuracy == 0.0
    assert report.hard_accuracy == 0.0
    assert {(c.expected, c.got) for c in report.confusions} == {
        ("rice-prioritization", "cost-of-delay"), ("kano-model", "cost-of-delay")}
    assert report.per_skill["rice-prioritization"] == (0, 1)


def test_router_returning_unknown_skill_counts_as_wrong() -> None:
    report = evaluate(lambda prompt, skills: "not-a-skill", SKILLS, CASES[:3])
    assert report.accuracy == 0.0


def test_load_cases_rejects_bad_file(tmp_path: Path) -> None:
    bad = tmp_path / "cases.json"
    bad.write_text('[{"prompt": "x"}]', encoding="utf-8")
    with pytest.raises(ValueError, match="expected"):
        load_cases(bad)


def test_lexical_baseline_runs_and_beats_random_guessing() -> None:
    report = evaluate(lexical_router, SKILLS, CASES)
    assert report.total == len(CASES)
    assert report.accuracy > 3 / len(SKILLS)  # far above 1/31 random; a floor, not the target


# ---- review fixes -------------------------------------------------------------------------------
import threading


def test_router_failure_stops_a_parallel_run_early() -> None:
    calls, lock = [], threading.Lock()

    def flaky(prompt: str, skills) -> str:
        with lock:
            calls.append(prompt)
            attempt = len(calls)
        if attempt == 3:
            raise RuntimeError("401 invalid key")
        return "kano-model"

    with pytest.raises(RuntimeError, match="401"):
        evaluate(flaky, SKILLS, CASES, workers=2)
    assert len(calls) < len(CASES) // 2  # queued cases were cancelled, not paid for


def test_cli_rejects_non_positive_limit_and_empty_case_sets() -> None:
    with pytest.raises(SystemExit) as stop:
        main(["--limit", "0"])
    assert stop.value.code == 2


def test_lexical_router_weights_skill_names_without_fusing_words() -> None:
    from pm_agent.routing_eval import _terms

    assert _terms("product vision product vision") == _terms("product vision product vision")
    # regression: name.replace('-', ' ') * 2 produced the fused token 'visionproduct'
    from pm_agent.routing_eval import _name_terms

    terms = _name_terms("product-vision")
    assert "vision" in terms and "visionproduct" not in terms and terms["vision"] == 2

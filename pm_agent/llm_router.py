"""Model-backed router: asks Claude which skill fits a prompt, seeing only names and descriptions.

This mirrors what the real agent sees (progressive disclosure: name + description of every skill).
The reply is constrained to a JSON enum of skill names, so it can never name a skill that does not
exist. Needs the `anthropic` SDK >= 1.0 and credentials only for live runs; tests use a fake client.
"""

from __future__ import annotations

import json
import math
import threading
from dataclasses import dataclass
from typing import Any, Sequence

from pm_agent.skills import STAGE_TITLES, STAGES, Skill

DEFAULT_MODEL = "claude-opus-5-5"  # the API reference's default; override with --model
DEFAULT_EFFORT = "medium"  # Opus 5.5 defaults to medium; set explicitly so runs are reproducible
MAX_TOKENS = 8000  # thinking tokens share this budget with the one-line answer

# (input, output) USD per million tokens, from the API reference (cached 2026-10-06). Re-check before
# trusting an estimate; unknown models raise instead of guessing.
PRICES_PER_MTOK = {
    "claude-fable-5-1": (10.0, 50.0),
    "claude-opus-5-5": (4.0, 20.0),
    "claude-sonnet-5-5": (2.0, 10.0),
    "claude-haiku-5-5": (0.10, 0.50),
}
CACHE_READ_FACTOR = 0.1
CACHE_WRITE_FACTOR = 1.25
CHARS_PER_TOKEN = 3.5  # conservative: slightly over-counts tokens
PROMPT_OVERHEAD_TOKENS = 30
OUTPUT_TOKENS_ASSUMED = (150, 1500)  # per call, mostly thinking at medium effort: an assumption

INSTALL_HINT = (
    "The model-backed router needs the Anthropic SDK 1.x. Run it in an isolated environment:\n"
    '  uv run --with "anthropic>=1" python -m pm_agent.routing_eval --router llm --confirm-spend\n'
    "and provide credentials (ANTHROPIC_API_KEY, or `ant auth login`)."
)


@dataclass(frozen=True)
class Usage:
    calls: int
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    failures: int


@dataclass(frozen=True)
class Estimate:
    calls: int
    model: str
    input_tokens: int
    low_usd: float
    high_usd: float


def _ordered(skills: Sequence[Skill]) -> list[Skill]:
    return sorted(skills, key=lambda s: (STAGES.index(s.stage), s.stage_order))


def build_system_prompt(skills: Sequence[Skill]) -> str:
    lines = [
        "You are the routing layer of a product-management assistant. The user will describe a "
        "task. Choose the ONE skill below whose description fits it best.",
        "Each description ends with 'Not for ...' clauses naming a neighbouring skill that fits "
        "better in that case; respect them.",
        "",
    ]
    current = None
    for skill in _ordered(skills):
        if skill.stage != current:
            current = skill.stage
            lines += [f"## {STAGE_TITLES[current]}", ""]
        lines.append(f"- {skill.name}: {skill.description}")
    lines += ["", 'Reply with JSON only: {"skill": "<skill-name>"}.']
    return "\n".join(lines)


def skill_schema(skills: Sequence[Skill]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {"skill": {"type": "string", "enum": [s.name for s in _ordered(skills)]}},
        "required": ["skill"],
        "additionalProperties": False,
    }


def estimate_cost(skills: Sequence[Skill], *, calls: int, prompt_chars: int, model: str) -> Estimate:
    if model not in PRICES_PER_MTOK:
        raise ValueError(f"no price known for model '{model}'; known: {sorted(PRICES_PER_MTOK)}")
    in_price, out_price = (p / 1_000_000 for p in PRICES_PER_MTOK[model])
    system_chars = len(build_system_prompt(skills)) + len(json.dumps(skill_schema(skills)))
    system_tokens = math.ceil(system_chars / CHARS_PER_TOKEN)
    prompt_tokens = math.ceil(prompt_chars / CHARS_PER_TOKEN) + PROMPT_OVERHEAD_TOKENS
    uncached = calls * (system_tokens + prompt_tokens)
    cached = (
        system_tokens * CACHE_WRITE_FACTOR + max(calls - 1, 0) * system_tokens * CACHE_READ_FACTOR
        if calls
        else 0
    ) + calls * prompt_tokens
    low_out, high_out = (calls * tokens * out_price for tokens in OUTPUT_TOKENS_ASSUMED)
    return Estimate(
        calls=calls,
        model=model,
        input_tokens=uncached,
        low_usd=cached * in_price + low_out,
        high_usd=uncached * in_price + high_out,
    )


class LLMRouter:
    """Callable router (prompt, skills) -> skill name. Unusable replies return '' and are counted."""

    def __init__(
        self,
        client: Any,
        *,
        model: str = DEFAULT_MODEL,
        effort: str = DEFAULT_EFFORT,
        max_tokens: int = MAX_TOKENS,
    ) -> None:
        self._client = client
        self._model = model
        self._effort = effort
        self._max_tokens = max_tokens
        self._lock = threading.Lock()
        self._totals = [0, 0, 0, 0, 0, 0]  # calls, in, out, cache read, cache write, failures

    def __call__(self, prompt: str, skills: Sequence[Skill]) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            system=[{
                "type": "text",
                "text": build_system_prompt(skills),
                "cache_control": {"type": "ephemeral"},  # identical for every case: cache it
            }],
            messages=[{"role": "user", "content": prompt}],
            output_config={
                "effort": self._effort,
                "format": {"type": "json_schema", "schema": skill_schema(skills)},
            },
        )
        answer = self._parse(response)
        self._record(response.usage, failed=answer == "")
        return answer

    @staticmethod
    def _parse(response: Any) -> str:
        if response.stop_reason != "end_turn":  # refusal, max_tokens: nothing trustworthy to read
            return ""
        text = next((b.text for b in response.content if b.type == "text"), "")
        try:
            skill = json.loads(text).get("skill")
        except (json.JSONDecodeError, AttributeError):
            return ""
        return skill if isinstance(skill, str) else ""

    def _record(self, usage: Any, *, failed: bool) -> None:
        deltas = (
            1,
            getattr(usage, "input_tokens", 0) or 0,
            getattr(usage, "output_tokens", 0) or 0,
            getattr(usage, "cache_read_input_tokens", 0) or 0,
            getattr(usage, "cache_creation_input_tokens", 0) or 0,
            int(failed),
        )
        with self._lock:
            self._totals = [total + delta for total, delta in zip(self._totals, deltas)]

    def usage(self) -> Usage:
        with self._lock:
            return Usage(*self._totals)


def make_client() -> Any:
    """Anthropic client with default credential resolution; needs the 1.x SDK."""
    try:
        import anthropic
    except ImportError as error:
        raise RuntimeError(INSTALL_HINT) from error
    if int(anthropic.__version__.split(".")[0]) < 1:
        raise RuntimeError(f"anthropic {anthropic.__version__} is too old for output_config.\n{INSTALL_HINT}")
    return anthropic.Anthropic()

"""Model-backed router: request shape, parsing, failure handling, usage and cost. No network."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from pm_agent.llm_router import (
    DEFAULT_MODEL,
    LLMRouter,
    build_system_prompt,
    estimate_cost,
    skill_schema,
)
from pm_agent.routing_eval import Case, evaluate, load_cases, main
from pm_agent.skills import load_skills

ROOT = Path(__file__).resolve().parent.parent
SKILLS = load_skills(ROOT / "skills")
NAMES = [s.name for s in SKILLS]


class FakeClient:
    """Stands in for anthropic.Anthropic(); records requests and replays canned responses."""

    def __init__(self, reply=None, *, stop_reason="end_turn", raises=None, text=None):
        self.requests: list[dict] = []
        self._reply = reply
        self._stop_reason = stop_reason
        self._raises = raises
        self._text = text
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kwargs):
        self.requests.append(kwargs)
        if self._raises:
            raise self._raises
        picked = self._reply(kwargs) if callable(self._reply) else self._reply
        text = self._text if self._text is not None else json.dumps({"skill": picked})
        return SimpleNamespace(
            content=[SimpleNamespace(type="text", text=text)],
            stop_reason=self._stop_reason,
            usage=SimpleNamespace(input_tokens=10, output_tokens=5,
                                  cache_read_input_tokens=100, cache_creation_input_tokens=7),
        )


def test_returns_the_skill_the_model_picked() -> None:
    router = LLMRouter(FakeClient("kano-model"))
    assert router("which features delight users?", SKILLS) == "kano-model"


def test_request_shape_matches_the_api_rules_for_the_default_model() -> None:
    client = FakeClient("kano-model")
    LLMRouter(client)("a prompt", SKILLS)
    (req,) = client.requests
    assert req["model"] == DEFAULT_MODEL == "claude-opus-5-5"
    assert req["messages"] == [{"role": "user", "content": "a prompt"}]
    # Opus 5.5 400s on these; the router must never send them.
    for forbidden in ("thinking", "temperature", "top_p", "top_k", "tool_choice", "tools"):
        assert forbidden not in req
    assert req["output_config"]["effort"] == "medium"
    assert req["max_tokens"] >= 4096  # thinking tokens share the budget with the answer
    fmt = req["output_config"]["format"]
    assert fmt["type"] == "json_schema"
    assert fmt["schema"]["properties"]["skill"]["enum"] == skill_schema(SKILLS)["properties"]["skill"]["enum"]
    assert fmt["schema"]["additionalProperties"] is False and fmt["schema"]["required"] == ["skill"]


def test_system_prompt_is_cached_stable_and_complete() -> None:
    client = FakeClient("kano-model")
    router = LLMRouter(client)
    router("first", SKILLS)
    router("second", tuple(reversed(SKILLS)))  # input order must not change the bytes
    first, second = (r["system"] for r in client.requests)
    assert first == second
    (block,) = first
    assert block["cache_control"] == {"type": "ephemeral"}
    for skill in SKILLS:
        assert skill.name in block["text"] and skill.description in block["text"]


def test_schema_enum_is_in_stage_order_and_covers_every_skill() -> None:
    enum = skill_schema(tuple(reversed(SKILLS)))["properties"]["skill"]["enum"]
    assert sorted(enum) == sorted(NAMES)
    assert enum[0] == "feature-request-triage" and enum[-1] == "post-launch-review"


def test_system_prompt_lists_stage_headings() -> None:
    text = build_system_prompt(SKILLS)
    for stage in ("prioritise", "direction", "discover", "define", "decide", "launch", "measure"):
        assert stage in text.lower()


@pytest.mark.parametrize(
    "client",
    [
        FakeClient("kano-model", stop_reason="refusal"),
        FakeClient("kano-model", stop_reason="max_tokens"),
        FakeClient(text="not json"),
        FakeClient(text='{"skill": 7}'),
        FakeClient(text='{"other": "x"}'),
    ],
)
def test_unusable_responses_become_empty_and_are_counted(client: FakeClient) -> None:
    router = LLMRouter(client)
    assert router("prompt", SKILLS) == ""
    assert router.usage().failures == 1


def test_api_errors_propagate_instead_of_being_scored_as_wrong_answers() -> None:
    router = LLMRouter(FakeClient(raises=RuntimeError("401 invalid key")))
    with pytest.raises(RuntimeError, match="401"):
        router("prompt", SKILLS)


def test_usage_accumulates_tokens_across_calls() -> None:
    router = LLMRouter(FakeClient("kano-model"))
    router("a", SKILLS)
    router("b", SKILLS)
    usage = router.usage()
    assert (usage.calls, usage.input_tokens, usage.output_tokens) == (2, 20, 10)
    assert (usage.cache_read_tokens, usage.cache_write_tokens, usage.failures) == (200, 14, 0)


def test_parallel_evaluation_matches_sequential_and_keeps_order() -> None:
    cases = load_cases(ROOT / "evals" / "routing_cases.json")[:24]
    oracle = {c.prompt: c.expected for c in cases}

    def answer(request: dict) -> str:
        return oracle[request["messages"][0]["content"]]

    sequential = evaluate(LLMRouter(FakeClient(answer)), SKILLS, cases)
    parallel = evaluate(LLMRouter(FakeClient(answer)), SKILLS, cases, workers=6)
    assert sequential == parallel
    assert parallel.accuracy == 1.0


def test_evaluate_rejects_non_positive_workers() -> None:
    with pytest.raises(ValueError, match="workers"):
        evaluate(lambda prompt, skills: "x", SKILLS, (Case("p", "kano-model"),), workers=0)


def test_estimate_cost_is_a_positive_range_that_scales_with_calls() -> None:
    small = estimate_cost(SKILLS, calls=10, prompt_chars=80, model="claude-opus-5-5")
    large = estimate_cost(SKILLS, calls=100, prompt_chars=80, model="claude-opus-5-5")
    assert 0 < small.low_usd < small.high_usd
    assert large.high_usd == pytest.approx(small.high_usd * 10)
    cheaper = estimate_cost(SKILLS, calls=100, prompt_chars=80, model="claude-haiku-5-5")
    assert cheaper.high_usd < large.low_usd


def test_estimate_cost_rejects_unpriced_model() -> None:
    with pytest.raises(ValueError, match="price"):
        estimate_cost(SKILLS, calls=1, prompt_chars=10, model="claude-unknown-9")


def test_cli_dry_run_prints_estimate_without_credentials_or_sdk(capsys) -> None:
    assert main(["--router", "llm", "--dry-run", "--limit", "10"]) == 0
    out = capsys.readouterr().out
    assert "10 calls" in out and "claude-opus-5-5" in out and "$" in out


def test_cli_refuses_live_run_without_spend_confirmation(capsys) -> None:
    assert main(["--router", "llm", "--limit", "5"]) == 2
    assert "--confirm-spend" in capsys.readouterr().err

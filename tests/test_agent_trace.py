"""Trace lines: what the CLI shows about a live run (model, tool calls, usage), without the SDK."""

from __future__ import annotations

from types import SimpleNamespace

from pm_agent.agent_trace import trace_lines


# Stand-ins named like the SDK's classes: the tracer dispatches on type(message).__name__.
class SystemMessage(SimpleNamespace): ...
class AssistantMessage(SimpleNamespace): ...
class ResultMessage(SimpleNamespace): ...
class ToolUseBlock(SimpleNamespace): ...
class TextBlock(SimpleNamespace): ...


def test_init_reports_the_model_and_skill_tool() -> None:
    message = SystemMessage(subtype="init", data={"model": "claude-haiku-5-5", "tools": ["Skill", "mcp__memory__read_product"]})
    lines = trace_lines(message)
    assert any("model=claude-haiku-5-5" in line for line in lines)
    assert any("Skill" in line for line in lines)


def test_assistant_message_shows_model_and_each_tool_call_but_not_plain_text() -> None:
    message = AssistantMessage(model="claude-haiku-5-5", content=[
        TextBlock(text="thinking out loud"),
        ToolUseBlock(name="Skill", input={"skill": "pm-agent:rice-prioritization"}),
        ToolUseBlock(name="mcp__memory__write_artifact", input={"skill": "rice-prioritization", "body": "x" * 500}),
    ])
    lines = trace_lines(message)
    assert any("model=claude-haiku-5-5" in line for line in lines)
    assert any("Skill" in line and "rice-prioritization" in line for line in lines)
    assert any("write_artifact" in line for line in lines)
    assert not any("thinking out loud" in line for line in lines)
    assert all(len(line) < 260 for line in lines)  # long inputs are truncated


def test_result_message_reports_cost_turns_and_per_model_usage() -> None:
    message = ResultMessage(total_cost_usd=0.1974, num_turns=4, is_error=False,
                            usage={"input_tokens": 120, "output_tokens": 900},
                            model_usage={"claude-opus-5-5": {"costUSD": 0.19}, "claude-haiku-5-5": {"costUSD": 0.007}})
    text = "\n".join(trace_lines(message))
    assert "$0.1974" in text and "4 turns" in text
    assert "claude-opus-5-5" in text and "claude-haiku-5-5" in text


def test_missing_optional_fields_do_not_crash() -> None:
    assert trace_lines(ResultMessage()) != []
    assert trace_lines(AssistantMessage(content=[])) == []
    assert trace_lines(SimpleNamespace()) == []


# ---- per-turn usage and tool-result size -------------------------------------------------------
class UserMessage(SimpleNamespace): ...
class ToolResultBlock(SimpleNamespace): ...


def test_assistant_turn_usage_is_reported_even_without_tool_calls() -> None:
    message = AssistantMessage(model="claude-haiku-5-5", content=[TextBlock(text="OK")], usage={
        "input_tokens": 3, "cache_creation_input_tokens": 51000, "cache_read_input_tokens": 120, "output_tokens": 9})
    text = "\n".join(trace_lines(message))
    assert "cache_write=51000" in text and "cache_read=120" in text and "out=9" in text


def test_tool_result_sizes_are_reported_so_huge_results_stand_out() -> None:
    message = UserMessage(content=[
        ToolResultBlock(tool_use_id="toolu_abcdef123456", content="x" * 190_000),
        ToolResultBlock(tool_use_id="toolu_zzz", content=[{"type": "text", "text": "short"}]),
    ])
    lines = trace_lines(message)
    assert any("190000 chars" in line for line in lines)
    import re
    assert any(re.search(r"\[tool-result\] \S+ 5 chars$", line) for line in lines)  # text length, not repr length


def test_user_message_with_plain_text_traces_nothing() -> None:
    assert trace_lines(UserMessage(content="hello")) == []

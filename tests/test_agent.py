"""Main agent wiring: prompt, plugin manifest, subagent loader, SDK options (fake SDK, no network)."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from pm_agent.agent import BUILTIN_TOOLS, MEMORY_SERVER, build_options
from pm_agent.agent_prompt import build_agent_prompt
from pm_agent.agents import load_agent_specs
from pm_agent.memory import init_workspace
from pm_agent.memory_tools import MemoryTools
from pm_agent.skills import load_skills, stage_index

ROOT = Path(__file__).resolve().parent.parent
SKILLS = load_skills(ROOT / "skills")


def fake_sdk():
    """Records what build_options hands to the SDK; mirrors the real names it uses."""
    registered = []

    def tool(name, description, schema):
        def decorate(handler):
            entry = SimpleNamespace(name=name, description=description, schema=schema, handler=handler)
            registered.append(entry)
            return entry
        return decorate

    return SimpleNamespace(
        registered=registered,
        tool=tool,
        create_sdk_mcp_server=lambda name, version="1.0.0", tools=None: {"type": "sdk", "name": name, "tools": tools},
        AgentDefinition=lambda **kw: SimpleNamespace(**kw),
        ClaudeAgentOptions=lambda **kw: SimpleNamespace(**kw),
    )


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    return init_workspace(tmp_path, "acme")


def test_prompt_lists_every_skill_in_stage_order() -> None:
    prompt = build_agent_prompt(SKILLS, product="acme")
    last = -1
    for stage, names in stage_index(SKILLS).items():
        for name in names:
            position = prompt.index(name)
            assert position > last, f"{name} out of order"
            last = position
    assert "acme" in prompt


def test_prompt_states_the_protocol_and_only_names_real_tools(ws: Path) -> None:
    prompt = build_agent_prompt(SKILLS, product="acme")
    tool_names = {s.name for s in MemoryTools(ws, SKILLS).specs}
    for must in ("check_dependencies", "write_artifact", "search_memory"):
        assert must in prompt and must in tool_names
    assert "never invent" in prompt.lower() and "human" in prompt.lower()
    assert "approve_artifact" not in prompt
    assert len(prompt.split()) < 700


def test_plugin_manifest_makes_the_repo_loadable_as_a_plugin() -> None:
    manifest = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert manifest["name"] == "pm-agent" and manifest["version"]


def test_agent_specs_parse_claude_code_subagent_format(tmp_path: Path) -> None:
    (tmp_path / "critic.md").write_text(
        "---\nname: critic\ndescription: Reviews artifacts against a checklist.\n"
        "tools: Read, Grep\nmodel: sonnet\n---\n\nYou are a strict reviewer.\n", encoding="utf-8")
    (spec,) = load_agent_specs(tmp_path)
    assert (spec.name, spec.tools, spec.model) == ("critic", ("Read", "Grep"), "sonnet")
    assert spec.prompt == "You are a strict reviewer."
    assert load_agent_specs(tmp_path / "missing") == ()


def test_agent_spec_rejects_missing_description(tmp_path: Path) -> None:
    (tmp_path / "bad.md").write_text("---\nname: bad\n---\nbody", encoding="utf-8")
    with pytest.raises(ValueError, match="description"):
        load_agent_specs(tmp_path)


def test_options_lock_the_agent_to_memory_tools_only(ws: Path) -> None:
    sdk = fake_sdk()
    options = build_options(ws, product="acme", sdk=sdk)
    # No built-in tools: Read/Glob/Grep are not confined to the workspace, so everything the agent
    # needs goes through the memory tools. "Skill" is mandatory: without it no skill can be invoked.
    assert options.tools == ["Skill"] and BUILTIN_TOOLS == ()
    assert options.permission_mode == "dontAsk"
    assert options.cwd == str(ws)
    assert options.setting_sources == []  # never inherit the developer's ~/.claude config
    assert options.plugins == [{"type": "local", "path": str(ROOT)}]
    # Exactly the 31 PM skills: "all" would also expose Claude Code's bundled skills.
    assert options.skills == [f"pm-agent:{s.name}" for s in SKILLS] and len(options.skills) == 31
    assert options.model == "claude-opus-5-5"
    assert options.max_budget_usd > 0 and options.max_turns > 0


def test_options_register_memory_tools_and_pre_approve_them(ws: Path) -> None:
    sdk = fake_sdk()
    options = build_options(ws, product="acme", sdk=sdk)
    registered = {t.name for t in sdk.registered}
    assert registered == {s.name for s in MemoryTools(ws, SKILLS).specs}
    assert set(options.allowed_tools) == {"Skill"} | {f"mcp__{MEMORY_SERVER}__{n}" for n in registered}
    assert set(options.mcp_servers) == {MEMORY_SERVER}
    assert not any("approve" in name for name in options.allowed_tools)


def test_registered_tool_handlers_run_the_memory_tools(ws: Path) -> None:
    import asyncio

    sdk = fake_sdk()
    build_options(ws, product="acme", sdk=sdk)
    handler = next(t for t in sdk.registered if t.name == "read_product").handler
    result = asyncio.run(handler({}))
    assert result["is_error"] is False and "## Vision" in result["content"][0]["text"]


def test_subagents_are_passed_through_and_unlock_the_agent_tool(ws: Path, tmp_path: Path) -> None:
    agents = tmp_path / "agents"
    agents.mkdir()
    (agents / "critic.md").write_text(
        "---\nname: critic\ndescription: Reviews drafts.\ntools: Read\nmodel: haiku\n---\nReview.\n", encoding="utf-8")
    options = build_options(ws, product="acme", agents_dir=agents, sdk=fake_sdk())
    assert set(options.agents) == {"critic"}
    assert options.agents["critic"].model == "haiku" and options.agents["critic"].tools == ["Read"]
    assert "Agent" in options.tools
    assert build_options(ws, product="acme", agents_dir=tmp_path / "none", sdk=fake_sdk()).agents is None


def test_missing_sdk_gives_an_actionable_error(ws: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import builtins

    real_import = builtins.__import__

    def deny(name, *args, **kwargs):
        if name == "claude_agent_sdk":
            raise ImportError("no module")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", deny)
    with pytest.raises(RuntimeError, match="claude-agent-sdk"):
        build_options(ws, product="acme")

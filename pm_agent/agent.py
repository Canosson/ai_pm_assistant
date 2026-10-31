"""Main PM agent: one agent, 31 skills (loaded as a plugin), memory tools, optional subagents.

Built on the Claude Agent SDK (`pip install claude-agent-sdk`). `build_options` is the only place
that touches the SDK, and takes it as a parameter so the wiring is testable without it.

    python -m pm_agent.agent --product acme "Triage this backlog: ..."
    python -m pm_agent.agent --product acme --check      # show what loaded, no model call
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from contextlib import aclosing
from pathlib import Path
from typing import Any, Sequence

from pm_agent.agent_prompt import build_agent_prompt
from pm_agent.agent_trace import trace_lines
from pm_agent.agents import load_agent_specs
from pm_agent.llm_router import DEFAULT_EFFORT, DEFAULT_MODEL
from pm_agent.memory import init_workspace
from pm_agent.memory_tools import MemoryTools, ToolSpec
from pm_agent.skills import load_skills

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
AGENTS_DIR = ROOT / "agents"
MEMORY_SERVER = "memory"
# No built-in tools. Read/Glob/Grep are not confined to the workspace (they could reach ~/.ssh or
# another product's memory), so everything the agent needs goes through the memory tools, which
# also enforce dependencies and the draft status. No Write/Edit/Bash, no web access.
BUILTIN_TOOLS: tuple[str, ...] = ()
DEFAULT_MAX_TURNS = 40
DEFAULT_MAX_BUDGET_USD = 2.0
SDK_HINT = (
    "The Claude Agent SDK is not installed. Run in an isolated environment:\n"
    '  uv run --no-project --python 3.13 --with claude-agent-sdk python -m pm_agent.agent ...'
)


def _load_sdk() -> Any:
    try:
        import claude_agent_sdk
    except ImportError as error:
        raise RuntimeError(SDK_HINT) from error
    return claude_agent_sdk


def _sdk_tool(sdk: Any, memory: MemoryTools, spec: ToolSpec) -> Any:
    @sdk.tool(spec.name, spec.description, spec.schema)
    async def handler(args: dict[str, Any]) -> dict[str, Any]:
        return memory.call(spec.name, args)

    return handler


def build_options(
    workspace: Path,
    *,
    product: str,
    skills_dir: Path = SKILLS_DIR,
    agents_dir: Path = AGENTS_DIR,
    plugin_root: Path = ROOT,
    model: str = DEFAULT_MODEL,
    effort: str = DEFAULT_EFFORT,
    max_turns: int = DEFAULT_MAX_TURNS,
    max_budget_usd: float = DEFAULT_MAX_BUDGET_USD,
    sdk: Any = None,
) -> Any:
    sdk = sdk or _load_sdk()
    skills = load_skills(skills_dir)
    plugin = json.loads((plugin_root / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))["name"]
    memory = MemoryTools(workspace, skills)
    server = sdk.create_sdk_mcp_server(
        MEMORY_SERVER, tools=[_sdk_tool(sdk, memory, spec) for spec in memory.specs]
    )
    agents = {
        spec.name: sdk.AgentDefinition(
            description=spec.description,
            prompt=spec.prompt,
            tools=list(spec.tools) if spec.tools else None,
            model=spec.model,
        )
        for spec in load_agent_specs(agents_dir)
    } or None
    # "Skill" must be listed explicitly: with `tools` set, the SDK does not add it, and without it the
    # agent cannot invoke any of the skills at all.
    tools = ["Skill", *BUILTIN_TOOLS, *(["Agent"] if agents else [])]
    memory_tools = [f"mcp__{MEMORY_SERVER}__{spec.name}" for spec in memory.specs]
    return sdk.ClaudeAgentOptions(
        tools=tools,
        allowed_tools=[*tools, *memory_tools],
        system_prompt=build_agent_prompt(skills, product),
        mcp_servers={MEMORY_SERVER: server},
        permission_mode="dontAsk",  # anything not pre-approved is denied, never prompted
        cwd=str(workspace),
        setting_sources=[],  # do not inherit the developer's ~/.claude skills, hooks or plugins
        plugins=[{"type": "local", "path": str(plugin_root)}],
        skills=[f"{plugin}:{skill.name}" for skill in skills],  # invocable skills: only ours, not "all"
        agents=agents,
        model=model,
        effort=effort,
        max_turns=max_turns,
        max_budget_usd=max_budget_usd,
    )


EXIT_NO_INIT = 3


async def _run(sdk: Any, prompt: str, options: Any, *, check: bool) -> int:
    async with aclosing(sdk.query(prompt=prompt, options=options)) as stream:
        async for message in stream:
            kind = type(message).__name__
            for line in trace_lines(message):  # model, tool calls and usage go to stderr
                print(line, file=sys.stderr)
            if kind == "SystemMessage" and getattr(message, "subtype", "") == "init":
                if check:
                    data = getattr(message, "data", {}) or {}
                    for key in ("plugins", "skills", "mcp_servers"):
                        print(f"{key}: {data.get(key)}")
                    return 0
            elif kind == "AssistantMessage":
                for block in message.content:
                    if type(block).__name__ == "TextBlock":
                        print(block.text)
            elif kind == "ResultMessage":
                return 1 if getattr(message, "is_error", False) else 0
    return EXIT_NO_INIT if check else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the PM assistant.")
    parser.add_argument("prompt", nargs="?", help="what to ask the assistant")
    parser.add_argument("--product", required=True, help="product slug, e.g. acme")
    parser.add_argument("--root", type=Path, default=ROOT / "workspace", help="workspaces folder")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--effort", default=DEFAULT_EFFORT)
    parser.add_argument("--max-turns", type=int, default=DEFAULT_MAX_TURNS)
    parser.add_argument("--max-budget-usd", type=float, default=DEFAULT_MAX_BUDGET_USD)
    parser.add_argument("--check", action="store_true",
                        help="start a real session, print what loaded, then stop; the session may "
                             "already have sent one brief model request (small cost)")
    args = parser.parse_args(argv)
    if not args.prompt and not args.check:
        parser.error("give a prompt, or use --check")
    try:
        sdk = _load_sdk()
        workspace = init_workspace(args.root, args.product)
        options = build_options(
            workspace, product=args.product, model=args.model, effort=args.effort,
            max_turns=args.max_turns, max_budget_usd=args.max_budget_usd, sdk=sdk,
        )
        return asyncio.run(_run(sdk, args.prompt or "ping", options, check=args.check))
    except (RuntimeError, ValueError) as error:  # missing SDK, or a bad --product slug
        print(error, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

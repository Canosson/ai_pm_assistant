"""Subagent definitions: agents/*.md in Claude Code's subagent format (frontmatter + prompt body)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pm_agent.skills import parse_frontmatter


@dataclass(frozen=True)
class AgentSpec:
    name: str
    description: str
    tools: tuple[str, ...] | None
    model: str | None
    prompt: str


def load_agent_specs(agents_dir: Path) -> tuple[AgentSpec, ...]:
    if not agents_dir.is_dir():
        return ()
    specs = []
    for path in sorted(agents_dir.glob("*.md")):
        fields, body = parse_frontmatter(path.read_text(encoding="utf-8"), path)
        if not fields.get("description"):
            raise ValueError(f"{path}: subagent needs a description")
        tools = tuple(t.strip() for t in fields["tools"].split(",") if t.strip()) if fields.get("tools") else None
        specs.append(AgentSpec(
            name=fields.get("name") or path.stem,
            description=fields["description"],
            tools=tools,
            model=fields.get("model") or None,
            prompt=body.strip(),
        ))
    return tuple(specs)

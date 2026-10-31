"""Skill loader: the single place SKILL.md frontmatter is parsed."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

STAGES = ("prioritise", "direction", "discover", "define", "decide", "launch", "measure")
STAGE_TITLES = {
    "prioritise": "Stage 1: Prioritise and say no",
    "direction": "Stage 2: Set direction",
    "discover": "Stage 3: Discover",
    "define": "Stage 4: Define",
    "decide": "Stage 5: Decide and align",
    "launch": "Stage 6: Launch",
    "measure": "Stage 7: Measure and learn",
}
REQUIRED_FIELDS = ("name", "description", "stage", "stage_order", "version")
STOPWORDS = frozenset(
    "a an and the of to for in on with or not use when is are be by as at it its this that "
    "from into your you what who how why which then than so can will".split()
)
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.S)
_KEY_LINE = re.compile(r"^([a-z_]+):\s*>?\s*(.*)$")


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    stage: str
    stage_order: int
    version: str
    body: str


def parse_frontmatter(text: str, source: Path) -> tuple[dict[str, str], str]:
    """Split a markdown file into (frontmatter fields, body). Handles `key: >` folded values."""
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"{source}: missing frontmatter")
    front, body = match.groups()
    fields: dict[str, str] = {}
    key: str | None = None
    for line in front.splitlines():
        top = None if line.startswith(" ") else _KEY_LINE.match(line)
        if top:
            key = top.group(1)
            fields[key] = top.group(2).strip()
        elif key and line.strip():
            fields[key] = f"{fields[key]} {line.strip()}".strip()
    return fields, body


def _load_one(path: Path) -> Skill:
    fields, body = parse_frontmatter(path.read_text(encoding="utf-8"), path)
    missing = [name for name in REQUIRED_FIELDS if not fields.get(name)]
    if missing:
        raise ValueError(f"{path}: missing fields {missing}")
    if fields["name"] != path.parent.name:
        raise ValueError(f"{path}: name '{fields['name']}' differs from folder '{path.parent.name}'")
    if fields["stage"] not in STAGES:
        raise ValueError(f"{path}: unknown stage '{fields['stage']}'")
    return Skill(
        name=fields["name"],
        description=fields["description"],
        stage=fields["stage"],
        stage_order=int(fields["stage_order"]),
        version=fields["version"],
        body=body,
    )


def load_skills(skills_dir: Path) -> tuple[Skill, ...]:
    return tuple(_load_one(path) for path in sorted(skills_dir.glob("*/SKILL.md")))


def stage_index(skills: Iterable[Skill]) -> dict[str, tuple[str, ...]]:
    """Stage -> skill names in position order, stages in pipeline order."""
    grouped: dict[str, list[Skill]] = {}
    for skill in skills:
        grouped.setdefault(skill.stage, []).append(skill)
    return {
        stage: tuple(s.name for s in sorted(grouped[stage], key=lambda s: s.stage_order))
        for stage in STAGES
        if stage in grouped
    }


def routing_text(description: str) -> str:
    """The part of a description that says what the skill is for (drops the 'Not for' clause)."""
    return re.split(r"\bNot for\b", description)[0]


def description_tokens(text: str) -> frozenset[str]:
    words = re.findall(r"[a-z]+", text.lower())
    return frozenset(w for w in words if w not in STOPWORDS and len(w) > 2)

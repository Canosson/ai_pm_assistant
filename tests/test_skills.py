"""Lint the 31 PM skills: structure, stage counts, cross-references, description overlap."""

from __future__ import annotations

import re
from itertools import combinations
from pathlib import Path

from pm_agent.skills import description_tokens, load_skills, routing_text, stage_index

SKILLS_DIR = Path(__file__).resolve().parent.parent / "skills"
SKILLS = load_skills(SKILLS_DIR)
EXPECTED_STAGE_SIZES = {
    "prioritise": 5, "direction": 5, "discover": 5, "define": 5,
    "decide": 4, "launch": 4, "measure": 3,
}
REQUIRED_SECTIONS = (
    "## When to use", "## Inputs", "## Steps",
    "## Output template", "## Quality checklist", "## Handoff",
)
MAX_DESCRIPTION_CHARS = 450
MAX_LINES = 150
MAX_OVERLAP = 0.35


def test_total_and_stage_counts() -> None:
    assert len(SKILLS) == sum(EXPECTED_STAGE_SIZES.values()) == 31
    index = stage_index(SKILLS)
    assert {stage: len(names) for stage, names in index.items()} == EXPECTED_STAGE_SIZES
    for stage, size in EXPECTED_STAGE_SIZES.items():
        orders = sorted(s.stage_order for s in SKILLS if s.stage == stage)
        assert orders == list(range(1, size + 1)), f"{stage}: orders {orders}"


def test_size_and_required_sections() -> None:
    for skill in SKILLS:
        assert len(skill.description) <= MAX_DESCRIPTION_CHARS, skill.name
        lines = (SKILLS_DIR / skill.name / "SKILL.md").read_text(encoding="utf-8").count("\n") + 1
        assert lines <= MAX_LINES, f"{skill.name}: {lines} lines"
        for section in REQUIRED_SECTIONS:
            assert section in skill.body, f"{skill.name}: missing {section}"


def test_cross_references_resolve() -> None:
    names = {s.name for s in SKILLS}
    for skill in SKILLS:
        for target in re.findall(r"\(use ([a-z-]+)", skill.description):
            assert target in names, f"{skill.name} points at unknown skill {target}"


def test_descriptions_do_not_overlap() -> None:
    for a, b in combinations(SKILLS, 2):
        ta, tb = (description_tokens(routing_text(s.description)) for s in (a, b))
        score = len(ta & tb) / max(1, len(ta | tb))
        assert score <= MAX_OVERLAP, f"{a.name} vs {b.name}: overlap {score:.2f}"

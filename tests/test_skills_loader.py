"""Skill loader: the one place SKILL.md frontmatter is parsed."""

from __future__ import annotations

from pathlib import Path

import pytest

from pm_agent.skills import STAGES, load_skills, stage_index

REAL_SKILLS = Path(__file__).resolve().parent.parent / "skills"


def write_skill(root: Path, name: str, *, stage="prioritise", order=1, desc="Does a thing.") -> None:
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: >\n  {desc}\n  Second line.\n"
        f"stage: {stage}\nstage_order: {order}\nversion: 0.1.0\n---\n\n# Body\n",
        encoding="utf-8")


def test_loads_fields_and_folds_description(tmp_path: Path) -> None:
    write_skill(tmp_path, "alpha", desc="First line.")
    (skill,) = load_skills(tmp_path)
    assert skill.name == "alpha"
    assert skill.description == "First line. Second line."
    assert (skill.stage, skill.stage_order, skill.version) == ("prioritise", 1, "0.1.0")
    assert "# Body" in skill.body


def test_rejects_name_that_differs_from_folder(tmp_path: Path) -> None:
    write_skill(tmp_path, "alpha")
    (tmp_path / "alpha" / "SKILL.md").write_text(
        "---\nname: beta\ndescription: x\nstage: launch\nstage_order: 1\nversion: 1\n---\n",
        encoding="utf-8")
    with pytest.raises(ValueError, match="name"):
        load_skills(tmp_path)


def test_rejects_missing_frontmatter_and_unknown_stage(tmp_path: Path) -> None:
    (tmp_path / "bad").mkdir()
    (tmp_path / "bad" / "SKILL.md").write_text("no frontmatter", encoding="utf-8")
    with pytest.raises(ValueError, match="frontmatter"):
        load_skills(tmp_path)
    other = tmp_path.parent / "other"
    write_skill(other, "gamma", stage="nonsense")
    with pytest.raises(ValueError, match="stage"):
        load_skills(other)


def test_stage_index_orders_by_stage_and_position(tmp_path: Path) -> None:
    write_skill(tmp_path, "second", stage="direction", order=2)
    write_skill(tmp_path, "first", stage="direction", order=1)
    write_skill(tmp_path, "solo", stage="measure", order=1)
    index = stage_index(load_skills(tmp_path))
    assert list(index) == [s for s in STAGES if s in ("direction", "measure")]
    assert index["direction"] == ("first", "second")


def test_real_skills_load_with_expected_shape() -> None:
    skills = load_skills(REAL_SKILLS)
    assert len(skills) == 31
    sizes = {stage: len(names) for stage, names in stage_index(skills).items()}
    assert sizes == {"prioritise": 5, "direction": 5, "discover": 5, "define": 5,
                     "decide": 4, "launch": 4, "measure": 3}

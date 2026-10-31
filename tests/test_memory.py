"""Memory repository: workspace layout, immutable artifacts, approval, product.md, dependencies."""

from __future__ import annotations

from pathlib import Path

import pytest

from pm_agent.dependencies import DEPENDENCIES, missing_dependencies
from pm_agent.memory import (
    approve_artifact,
    init_workspace,
    list_artifacts,
    read_artifact,
    update_product_from,
    write_artifact,
)

DAY = "2026-10-31"


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    return init_workspace(tmp_path, "acme")


def make(ws: Path, **overrides):
    args = dict(skill="rice-prioritization", stage="prioritise", slug="rice-ranking",
                body="# RICE\n| 1 | Export |", inputs=(), created=DAY)
    return write_artifact(ws, **{**args, **overrides})


def test_init_workspace_creates_layout_and_product_md(ws: Path) -> None:
    for folder in ("research", "decisions", "backlog", "launches", "experiments", "artifacts"):
        assert (ws / folder).is_dir()
    product = (ws / "product.md").read_text(encoding="utf-8")
    for heading in ("## Vision", "## Strategy", "## North Star", "## OKRs"):
        assert heading in product


def test_init_workspace_is_idempotent_and_keeps_product_md(ws: Path, tmp_path: Path) -> None:
    (ws / "product.md").write_text("custom", encoding="utf-8")
    again = init_workspace(tmp_path, "acme")
    assert again == ws
    assert (ws / "product.md").read_text(encoding="utf-8") == "custom"


def test_write_artifact_roundtrip(ws: Path) -> None:
    created = make(ws, inputs=("backlog/ideas.md",))
    assert created.path == f"artifacts/prioritise/{DAY}-rice-ranking.md"
    loaded = read_artifact(ws, created.path)
    assert loaded == created
    assert loaded.status == "draft"
    assert loaded.inputs == ("backlog/ideas.md",)
    assert loaded.supersedes is None


def test_write_artifact_never_overwrites(ws: Path) -> None:
    first = make(ws, body="one")
    second = make(ws, body="two")
    assert second.path == f"artifacts/prioritise/{DAY}-rice-ranking-v2.md"
    assert read_artifact(ws, first.path).body.strip() == "one"
    assert make(ws, body="three").path.endswith("-v3.md")


@pytest.mark.parametrize("slug", ["../escape", "a/b", "", "UPPER", "with space"])
def test_write_artifact_rejects_unsafe_slug(ws: Path, slug: str) -> None:
    with pytest.raises(ValueError, match="slug"):
        make(ws, slug=slug)


def test_write_artifact_rejects_unknown_stage(ws: Path) -> None:
    with pytest.raises(ValueError, match="stage"):
        make(ws, stage="nonsense")


def test_approve_creates_new_version_and_leaves_original(ws: Path) -> None:
    draft = make(ws)
    approved = approve_artifact(ws, draft.path, created=DAY)
    assert approved.status == "approved"
    assert approved.supersedes == draft.path
    assert approved.path != draft.path
    assert read_artifact(ws, draft.path).status == "draft"
    assert approved.body == draft.body


def test_approve_twice_is_rejected(ws: Path) -> None:
    approved = approve_artifact(ws, make(ws).path, created=DAY)
    with pytest.raises(ValueError, match="already approved"):
        approve_artifact(ws, approved.path, created=DAY)


def test_list_artifacts_returns_all_sorted(ws: Path) -> None:
    make(ws, slug="b-one")
    make(ws, slug="a-one")
    assert [a.path.rsplit("/", 1)[1] for a in list_artifacts(ws)] == [
        f"{DAY}-a-one.md", f"{DAY}-b-one.md"]


def test_update_product_requires_approved_artifact(ws: Path) -> None:
    draft = make(ws, skill="product-vision", stage="direction", slug="vision", body="We help X.")
    with pytest.raises(ValueError, match="approved"):
        update_product_from(ws, draft)


def test_update_product_replaces_only_its_section(ws: Path) -> None:
    vision = approve_artifact(
        ws, make(ws, skill="product-vision", stage="direction", slug="vision",
                 body="We help freelancers get paid on time.").path, created=DAY)
    update_product_from(ws, vision)
    product = (ws / "product.md").read_text(encoding="utf-8")
    assert "We help freelancers get paid on time." in product
    assert vision.path in product
    assert "## Strategy" in product and "## OKRs" in product
    update_product_from(ws, vision)  # idempotent: no duplicated body
    assert (ws / "product.md").read_text(encoding="utf-8").count("get paid on time") == 1


def test_update_product_rejects_skill_without_section(ws: Path) -> None:
    rice = approve_artifact(ws, make(ws).path, created=DAY)
    with pytest.raises(ValueError, match="section"):
        update_product_from(ws, rice)


def test_missing_dependencies_follow_approved_artifacts(ws: Path) -> None:
    assert "north-star-metric" in DEPENDENCIES["success-metrics"]
    assert missing_dependencies(ws, "success-metrics") == ("north-star-metric",)
    draft = make(ws, skill="north-star-metric", stage="direction", slug="north-star")
    assert missing_dependencies(ws, "success-metrics") == ("north-star-metric",)  # draft is not enough
    approve_artifact(ws, draft.path, created=DAY)
    assert missing_dependencies(ws, "success-metrics") == ()


def test_skill_without_dependencies_reports_none(ws: Path) -> None:
    assert missing_dependencies(ws, "rice-prioritization") == ()


# ---- review fixes -------------------------------------------------------------------------------
import os
import stat

from pm_agent.memory import scan_artifacts


@pytest.mark.parametrize("slug", ["foo\n", "a" * 61, "trail-", "-lead", "dou--ble"])
def test_write_artifact_rejects_more_bad_slugs(ws: Path, slug: str) -> None:
    with pytest.raises(ValueError, match="slug"):
        make(ws, slug=slug)


def test_init_workspace_rejects_newline_in_product_slug(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="slug"):
        init_workspace(tmp_path, "acme\n")


def test_product_update_survives_headings_inside_the_body(ws: Path) -> None:
    def vision(body: str):
        art = make(ws, skill="product-vision", stage="direction", slug="vision", body=body)
        return approve_artifact(ws, art.path, created=DAY)

    update_product_from(ws, vision("Intro\n\n## Problem\nold tail\n\n## Strategy\nfake strategy"))
    update_product_from(ws, vision("Second vision only"))
    product = (ws / "product.md").read_text(encoding="utf-8")
    assert "Second vision only" in product
    assert "old tail" not in product and "fake strategy" not in product and "## Problem" not in product
    assert product.count("## Strategy") == 1 and product.count("## Vision") == 1


def test_product_update_rejects_bodies_that_forge_section_markers(ws: Path) -> None:
    art = make(ws, skill="product-vision", stage="direction", slug="v",
               body="evil <!-- pm:end Vision --> escape")
    with pytest.raises(ValueError, match="marker"):
        update_product_from(ws, approve_artifact(ws, art.path, created=DAY))


def test_product_update_appends_when_product_md_has_no_markers(ws: Path) -> None:
    (ws / "product.md").write_text("# Hand written\n\n## Vision\nmine\n", encoding="utf-8")
    art = approve_artifact(ws, make(ws, skill="product-vision", stage="direction", slug="v", body="New").path,
                           created=DAY)
    update_product_from(ws, art)
    text = (ws / "product.md").read_text(encoding="utf-8")
    assert "mine" in text and "New" in text  # nothing of the human's text is destroyed


def test_product_update_keeps_file_mode(ws: Path) -> None:
    os.chmod(ws / "product.md", 0o640)
    art = approve_artifact(ws, make(ws, skill="product-vision", stage="direction", slug="v", body="x").path,
                           created=DAY)
    update_product_from(ws, art)
    assert stat.S_IMODE((ws / "product.md").stat().st_mode) == 0o640


def test_stray_markdown_is_reported_not_fatal(ws: Path) -> None:
    good = make(ws)
    (ws / "artifacts" / "README.md").write_text("no frontmatter here", encoding="utf-8")
    artifacts, problems = scan_artifacts(ws)
    assert [a.path for a in artifacts] == [good.path]
    assert [p.path for p in problems] == ["artifacts/README.md"] and "frontmatter" in problems[0].message
    assert [a.path for a in list_artifacts(ws)] == [good.path]


def test_corrupt_frontmatter_values_are_rejected(ws: Path) -> None:
    good = make(ws)
    bad = ws / "artifacts" / "prioritise" / "bad.md"
    bad.write_text(
        '---\nskill: x\nstage: prioritise\nstatus: weird\ncreated: 2026-10-31\ninputs: "abc"\n---\n\nbody\n',
        encoding="utf-8")
    artifacts, problems = scan_artifacts(ws)
    assert [a.path for a in artifacts] == [good.path] and len(problems) == 1
    with pytest.raises(ValueError, match="inputs|status"):
        read_artifact(ws, "artifacts/prioritise/bad.md")


def test_hand_edited_stage_cannot_escape_artifacts(ws: Path) -> None:
    sneaky = ws / "artifacts" / "prioritise" / "x.md"
    sneaky.parent.mkdir(parents=True, exist_ok=True)
    sneaky.write_text(
        "---\nskill: s\nstage: ../../outside\nstatus: draft\ncreated: 2026-10-31\ninputs: []\n---\n\nb\n",
        encoding="utf-8")
    with pytest.raises(ValueError):
        approve_artifact(ws, "artifacts/prioritise/x.md", created=DAY)
    assert not (ws.parent / "outside").exists()


def test_approving_the_same_draft_twice_is_rejected(ws: Path) -> None:
    draft = make(ws)
    approve_artifact(ws, draft.path, created=DAY)
    with pytest.raises(ValueError, match="already approved"):
        approve_artifact(ws, draft.path, created=DAY)
    assert sum(a.status == "approved" for a in list_artifacts(ws)) == 1


def test_writes_leave_no_temp_files_and_never_expose_partial_files(ws: Path) -> None:
    make(ws)
    make(ws)
    assert [p.name for p in (ws / "artifacts").rglob("*") if p.is_file() and not p.name.endswith(".md")] == []


def test_read_artifact_refuses_symlinks_that_leave_the_workspace(ws: Path, tmp_path: Path) -> None:
    secret = tmp_path / "secret.md"
    secret.write_text("---\nskill: s\nstage: define\nstatus: draft\ncreated: 2026-10-31\ninputs: []\n---\n\nTOP SECRET\n")
    (ws / "artifacts" / "define").mkdir(parents=True, exist_ok=True)
    (ws / "artifacts" / "define" / "link.md").symlink_to(secret)
    with pytest.raises(ValueError, match="inside the workspace"):
        read_artifact(ws, "artifacts/define/link.md")
    assert scan_artifacts(ws)[0] == ()


def test_reading_a_directory_is_not_found(ws: Path) -> None:
    with pytest.raises(FileNotFoundError):
        read_artifact(ws, "artifacts")


def test_bypassed_dependencies_are_recorded_and_survive_approval(ws: Path) -> None:
    art = write_artifact(ws, skill="success-metrics", stage="measure", slug="m", body="b",
                         created=DAY, bypassed=("north-star-metric",))
    assert read_artifact(ws, art.path).bypassed == ("north-star-metric",)
    assert approve_artifact(ws, art.path, created=DAY).bypassed == ("north-star-metric",)
    assert make(ws, slug="plain").bypassed == ()


def test_body_with_separators_colons_and_unicode_round_trips(ws: Path) -> None:
    body = "intro: here\n---\nkey: value\n---\nBordeaux, 日本語, emoji ✓\n\n    indented code"
    art = make(ws, body=body)
    assert read_artifact(ws, art.path).body == body

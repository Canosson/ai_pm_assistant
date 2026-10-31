"""SQLite index: derived from the files, searchable, with an artifact graph."""

from __future__ import annotations

from pathlib import Path

import pytest

from pm_agent.index import downstream, rebuild_index, search, upstream
from pm_agent.memory import approve_artifact, init_workspace, write_artifact

DAY = "2026-10-31"


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    return init_workspace(tmp_path, "acme")


def add(ws: Path, skill: str, stage: str, slug: str, body: str, inputs=()):
    return write_artifact(ws, skill=skill, stage=stage, slug=slug, body=body,
                          inputs=inputs, created=DAY)


def test_rebuild_creates_index_file(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "freelancers invoices")
    assert rebuild_index(ws) == ws / ".index.sqlite"
    assert (ws / ".index.sqlite").exists()


def test_search_finds_text_and_returns_metadata(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "Help freelancers collect invoices faster")
    add(ws, "rice-prioritization", "prioritise", "rice", "Export to CSV scores highest")
    rebuild_index(ws)
    hits = search(ws, "invoices")
    assert [h.skill for h in hits] == ["product-vision"]
    assert hits[0].stage == "direction" and hits[0].status == "draft"
    assert hits[0].path.endswith("vision.md")


def test_search_filters_by_stage(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "customers pay later")
    add(ws, "rice-prioritization", "prioritise", "rice", "customers want export")
    rebuild_index(ws)
    assert len(search(ws, "customers")) == 2
    assert [h.stage for h in search(ws, "customers", stage="prioritise")] == ["prioritise"]


def test_search_survives_fts_syntax_characters(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "pay-per-use pricing")
    rebuild_index(ws)
    assert search(ws, 'pay-per-use" OR (') != ()
    assert search(ws, "") == ()


def test_graph_tracks_inputs_both_ways(ws: Path) -> None:
    research = add(ws, "interview-synthesis", "discover", "synthesis", "themes")
    ost = add(ws, "opportunity-solution-tree", "discover", "ost", "tree", inputs=(research.path,))
    rebuild_index(ws)
    assert upstream(ws, ost.path) == (research.path,)
    assert downstream(ws, research.path) == (ost.path,)
    assert upstream(ws, research.path) == ()


def test_index_is_derived_state(ws: Path) -> None:
    art = add(ws, "product-vision", "direction", "vision", "unique-token-xyz")
    approve_artifact(ws, art.path, created=DAY)
    rebuild_index(ws)
    first = [(h.path, h.status) for h in search(ws, "unique-token-xyz")]
    (ws / ".index.sqlite").unlink()
    rebuild_index(ws)
    assert [(h.path, h.status) for h in search(ws, "unique-token-xyz")] == first
    assert len(first) == 2  # draft and approved versions both indexed


def test_rebuild_drops_deleted_files(ws: Path) -> None:
    art = add(ws, "product-vision", "direction", "vision", "ephemeral-word")
    rebuild_index(ws)
    (ws / art.path).unlink()
    rebuild_index(ws)
    assert search(ws, "ephemeral-word") == ()


# ---- review fixes -------------------------------------------------------------------------------
from concurrent.futures import ThreadPoolExecutor

import pm_agent.index as index_module


def test_failed_rebuild_keeps_the_previous_index_and_leaves_no_debris(ws: Path, monkeypatch) -> None:
    add(ws, "product-vision", "direction", "vision", "durable-word")
    rebuild_index(ws)

    def boom(_ws):
        raise RuntimeError("disk exploded")

    monkeypatch.setattr(index_module, "scan_artifacts", boom)
    with pytest.raises(RuntimeError, match="disk exploded"):
        rebuild_index(ws)
    monkeypatch.undo()
    assert [h.skill for h in search(ws, "durable-word")] == ["product-vision"]
    assert [p.name for p in ws.iterdir() if p.name.startswith(".index-")] == []


def test_rebuild_tolerates_stray_markdown(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "kept-word")
    (ws / "artifacts" / "README.md").write_text("stray", encoding="utf-8")
    rebuild_index(ws)
    assert len(search(ws, "kept-word")) == 1


def test_concurrent_rebuilds_and_searches_do_not_collide(ws: Path) -> None:
    add(ws, "product-vision", "direction", "vision", "parallel-word")
    rebuild_index(ws)

    def work(_: int):
        rebuild_index(ws)
        return len(search(ws, "parallel-word"))

    with ThreadPoolExecutor(max_workers=8) as pool:
        assert list(pool.map(work, range(24))) == [1] * 24


def test_search_without_an_index_fails_clearly_and_creates_nothing(ws: Path) -> None:
    with pytest.raises(FileNotFoundError, match="rebuild_index"):
        search(ws, "anything")
    assert not (ws / ".index.sqlite").exists()

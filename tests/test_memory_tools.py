"""Memory tools the agent calls: reads, search, and the one write path (drafts only, deps enforced)."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pm_agent.memory import approve_artifact, init_workspace, list_artifacts
from pm_agent.memory_tools import MemoryTools
from pm_agent.skills import load_skills

ROOT = Path(__file__).resolve().parent.parent
SKILLS = load_skills(ROOT / "skills")
TODAY = date.today().isoformat()


@pytest.fixture
def ws(tmp_path: Path) -> Path:
    return init_workspace(tmp_path, "acme")


@pytest.fixture
def tools(ws: Path) -> MemoryTools:
    return MemoryTools(ws, SKILLS)


def ok(result: dict) -> dict:
    assert result["is_error"] is False, result
    return json.loads(result["content"][0]["text"])


def err(result: dict) -> str:
    assert result["is_error"] is True, result
    return result["content"][0]["text"]


def test_specs_expose_exactly_the_agent_facing_tools(tools: MemoryTools) -> None:
    names = {spec.name for spec in tools.specs}
    assert names == {"check_dependencies", "list_artifacts", "read_artifact", "read_product",
                     "search_memory", "write_artifact"}
    assert not any("approve" in name for name in names)  # approval belongs to the human
    for spec in tools.specs:
        assert spec.schema["type"] == "object" and spec.description


def test_write_artifact_creates_a_draft_with_stage_taken_from_the_skill(tools: MemoryTools, ws: Path) -> None:
    result = ok(tools.call("write_artifact", {
        "skill": "rice-prioritization", "slug": "q3-ranking", "body": "# RICE\n| 1 | Export |"}))
    assert result["path"] == f"artifacts/prioritise/{TODAY}-q3-ranking.md"
    assert result["status"] == "draft" and "approval" in result["note"]
    (art,) = list_artifacts(ws)
    assert (art.skill, art.stage, art.status) == ("rice-prioritization", "prioritise", "draft")


def test_write_artifact_rejects_unknown_skill_and_bad_slug(tools: MemoryTools) -> None:
    assert "unknown skill" in err(tools.call("write_artifact", {"skill": "nope", "slug": "x", "body": "b"}))
    assert "slug" in err(tools.call("write_artifact", {"skill": "kano-model", "slug": "../x", "body": "b"}))


def test_write_artifact_requires_fields(tools: MemoryTools) -> None:
    assert "body" in err(tools.call("write_artifact", {"skill": "kano-model", "slug": "x"}))


def test_dependencies_block_writes_until_upstream_is_approved(tools: MemoryTools, ws: Path) -> None:
    assert ok(tools.call("check_dependencies", {"skill": "success-metrics"})) == {
        "skill": "success-metrics", "missing": ["north-star-metric"], "ready": False}
    message = err(tools.call("write_artifact", {"skill": "success-metrics", "slug": "m", "body": "b"}))
    assert "north-star-metric" in message and "acknowledge_missing" in message
    assert list_artifacts(ws) == ()

    draft = ok(tools.call("write_artifact", {"skill": "north-star-metric", "slug": "ns", "body": "WAU"}))
    approve_artifact(ws, draft["path"])
    assert ok(tools.call("check_dependencies", {"skill": "success-metrics"}))["ready"] is True
    assert ok(tools.call("write_artifact", {"skill": "success-metrics", "slug": "m", "body": "b"}))["status"] == "draft"


def test_acknowledging_missing_dependencies_lets_the_user_override(tools: MemoryTools) -> None:
    wrong = err(tools.call("write_artifact", {
        "skill": "success-metrics", "slug": "m", "body": "b", "acknowledge_missing": ["something-else"]}))
    assert "north-star-metric" in wrong
    done = ok(tools.call("write_artifact", {
        "skill": "success-metrics", "slug": "m", "body": "b", "acknowledge_missing": ["north-star-metric"]}))
    assert done["acknowledged_missing"] == ["north-star-metric"]


def test_read_and_list_artifacts(tools: MemoryTools) -> None:
    path = ok(tools.call("write_artifact", {"skill": "kano-model", "slug": "k", "body": "Delighters"}))["path"]
    ok(tools.call("write_artifact", {"skill": "product-vision", "slug": "v", "body": "Vision"}))
    listed = ok(tools.call("list_artifacts", {}))["artifacts"]
    assert {a["skill"] for a in listed} == {"kano-model", "product-vision"}
    only = ok(tools.call("list_artifacts", {"stage": "direction"}))["artifacts"]
    assert [a["skill"] for a in only] == ["product-vision"]
    assert ok(tools.call("read_artifact", {"path": path}))["body"] == "Delighters"


def test_read_artifact_errors_are_clean(tools: MemoryTools) -> None:
    assert "not found" in err(tools.call("read_artifact", {"path": "artifacts/define/missing.md"}))
    assert "relative" in err(tools.call("read_artifact", {"path": "../../etc/passwd"}))


def test_read_product_returns_product_md(tools: MemoryTools) -> None:
    assert "## Vision" in ok(tools.call("read_product", {}))["product_md"]


def test_search_memory_sees_artifacts_written_in_this_session(tools: MemoryTools) -> None:
    ok(tools.call("write_artifact", {"skill": "interview-synthesis", "slug": "s",
                                     "body": "Freelancers hate chasing late invoices"}))
    hits = ok(tools.call("search_memory", {"query": "invoices"}))["hits"]
    assert [h["skill"] for h in hits] == ["interview-synthesis"]
    assert ok(tools.call("search_memory", {"query": "invoices", "stage": "launch"}))["hits"] == []
    assert ok(tools.call("search_memory", {"query": "   "}))["hits"] == []


def test_unknown_tool_is_an_error_not_a_crash(tools: MemoryTools) -> None:
    assert "unknown tool" in err(tools.call("approve_artifact", {"path": "x"}))


# ---- review fixes -------------------------------------------------------------------------------
@pytest.mark.parametrize(
    "tool,args,fragment",
    [
        ("search_memory", {"query": "x", "limit": -1}, "limit"),
        ("search_memory", {"query": "x", "limit": 10_000}, "limit"),
        ("search_memory", {"query": "x", "limit": True}, "limit"),
        ("search_memory", {"query": 5}, "query"),
        ("write_artifact", {"skill": "kano-model", "slug": "x", "body": 123}, "body"),
        ("write_artifact", {"skill": "kano-model", "slug": "x", "body": "b", "inputs": "abc"}, "inputs"),
        ("write_artifact", {"skill": "kano-model", "slug": "x", "body": "b", "acknowledge_missing": "abc"},
         "acknowledge_missing"),
        ("write_artifact", {"skill": "kano-model", "slug": "a" * 200, "body": "b"}, "slug"),
        ("write_artifact", {"skill": "kano-model", "slug": "x", "body": "b", "sneaky": 1}, "sneaky"),
        ("list_artifacts", {"stage": "nonsense"}, "stage"),
        ("read_artifact", {"path": "artifacts"}, "not found"),
        ("read_artifact", {"path": 7}, "path"),
    ],
)
def test_bad_arguments_return_clean_errors_instead_of_crashing(tools: MemoryTools, tool, args, fragment) -> None:
    assert fragment in err(tools.call(tool, args))


def test_acknowledged_bypass_is_written_into_the_artifact(tools: MemoryTools, ws: Path) -> None:
    ok(tools.call("write_artifact", {"skill": "success-metrics", "slug": "m", "body": "b",
                                     "acknowledge_missing": ["north-star-metric"]}))
    (art,) = list_artifacts(ws)
    assert art.bypassed == ("north-star-metric",)
    shown = ok(tools.call("read_artifact", {"path": art.path}))
    assert shown["bypassed"] == ["north-star-metric"]


def test_list_artifacts_surfaces_unreadable_files(tools: MemoryTools, ws: Path) -> None:
    ok(tools.call("write_artifact", {"skill": "kano-model", "slug": "k", "body": "b"}))
    (ws / "artifacts" / "README.md").write_text("stray", encoding="utf-8")
    result = ok(tools.call("list_artifacts", {}))
    assert len(result["artifacts"]) == 1
    assert [p["path"] for p in result["problems"]] == ["artifacts/README.md"]

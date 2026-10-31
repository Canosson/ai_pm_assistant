"""The tools the agent calls to read and write product memory.

Pure logic over memory/index/dependencies (no SDK import), so it is fully testable. Results use
the shape the Agent SDK expects: {"content": [{"type": "text", "text": ...}], "is_error": bool}.
There is deliberately no approve tool: only a human approves an artifact. Every argument is
validated here too (the SDK validates against the schema, but this class is also called directly).
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

from pm_agent.dependencies import missing_dependencies
from pm_agent.index import rebuild_index, search
from pm_agent.memory import MAX_SLUG, read_artifact, scan_artifacts, write_artifact
from pm_agent.skills import STAGES, Skill

MAX_LIST = 100
MAX_SEARCH = 25
DEFAULT_SEARCH = 10


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    schema: dict[str, Any]


def _ok(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}], "is_error": False}


def _fail(message: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": message}], "is_error": True}


def _object(properties: dict[str, Any], required: Sequence[str] = ()) -> dict[str, Any]:
    return {"type": "object", "properties": properties, "required": list(required),
            "additionalProperties": False}


_STRINGS = {"type": "array", "items": {"type": "string"}}

SPECS = (
    ToolSpec(
        "check_dependencies",
        "Before running a skill, check which upstream skills still lack an APPROVED artifact. "
        "Returns {missing, ready}.",
        _object({"skill": {"type": "string"}}, ["skill"]),
    ),
    ToolSpec(
        "list_artifacts",
        "List saved artifacts (path, skill, stage, status, created), optionally filtered. Also "
        "reports files in memory that could not be read.",
        _object({"stage": {"type": "string", "enum": list(STAGES)},
                 "status": {"type": "string", "enum": ["draft", "approved"]}}),
    ),
    ToolSpec(
        "read_artifact",
        "Read one artifact by its workspace-relative path, including its inputs and body.",
        _object({"path": {"type": "string"}}, ["path"]),
    ),
    ToolSpec(
        "read_product",
        "Read product.md: the approved vision, strategy, north star and OKRs for this product.",
        _object({}),
    ),
    ToolSpec(
        "search_memory",
        "Full-text search across all saved artifacts. Use it before asking the user for context.",
        _object({"query": {"type": "string"}, "stage": {"type": "string", "enum": list(STAGES)},
                 "limit": {"type": "integer", "minimum": 1, "maximum": MAX_SEARCH}}, ["query"]),
    ),
    ToolSpec(
        "write_artifact",
        "Save the finished output of a skill as a DRAFT artifact. The stage comes from the skill. "
        "Fails if upstream skills have no approved artifact: call check_dependencies first, and "
        "only pass acknowledge_missing after the user agreed to proceed anyway (the bypass is "
        "recorded in the artifact). A human must approve the draft; you cannot.",
        _object({
            "skill": {"type": "string"},
            "slug": {"type": "string", "maxLength": MAX_SLUG, "description": "lowercase-hyphenated short name"},
            "body": {"type": "string", "description": "the artifact, in the skill's output template"},
            "inputs": {**_STRINGS, "description": "workspace paths of artifacts this one used"},
            "acknowledge_missing": {**_STRINGS, "description": "missing upstream skills the user agreed to skip"},
        }, ["skill", "slug", "body"]),
    ),
)
_SPEC_BY_NAME = {spec.name: spec for spec in SPECS}


def _field_error(name: str, value: Any, schema: Mapping[str, Any]) -> str | None:
    kind = schema.get("type")
    if kind == "string":
        valid = isinstance(value, str)
    elif kind == "integer":
        valid = isinstance(value, int) and not isinstance(value, bool)
    elif kind == "array":
        valid = isinstance(value, list) and all(isinstance(item, str) for item in value)
    else:
        valid = True
    if not valid:
        return f"field '{name}' must be {'a list of strings' if kind == 'array' else f'a {kind}'}"
    if "enum" in schema and value not in schema["enum"]:
        return f"field '{name}' must be one of {schema['enum']}"
    if kind == "integer" and not schema.get("minimum", value) <= value <= schema.get("maximum", value):
        return f"field '{name}' must be between {schema.get('minimum')} and {schema.get('maximum')}"
    if kind == "string" and len(value) > schema.get("maxLength", len(value)):
        return f"field '{name}' is longer than {schema['maxLength']} characters"
    return None


def _validate(spec: ToolSpec, args: Mapping[str, Any]) -> str | None:
    for field in spec.schema["required"]:
        if args.get(field) in (None, ""):
            return f"missing required field '{field}'"
    for name, value in args.items():
        if name not in spec.schema["properties"]:
            return f"unexpected field '{name}'"
        problem = _field_error(name, value, spec.schema["properties"][name])
        if problem:
            return problem
    return None


class MemoryTools:
    def __init__(self, workspace: Path, skills: Sequence[Skill]) -> None:
        self._ws = workspace
        self._skills = {s.name: s for s in skills}
        self._handlers: dict[str, Callable[[Mapping[str, Any]], dict[str, Any]]] = {
            "check_dependencies": self._check_dependencies,
            "list_artifacts": self._list_artifacts,
            "read_artifact": self._read_artifact,
            "read_product": self._read_product,
            "search_memory": self._search_memory,
            "write_artifact": self._write_artifact,
        }

    @property
    def specs(self) -> tuple[ToolSpec, ...]:
        return SPECS

    def call(self, name: str, args: Mapping[str, Any]) -> dict[str, Any]:
        handler = self._handlers.get(name)
        if handler is None:
            return _fail(f"unknown tool '{name}'")
        problem = _validate(_SPEC_BY_NAME[name], args)
        if problem:
            return _fail(problem)
        try:
            return handler(args)
        except FileNotFoundError:
            return _fail(f"artifact not found: {args.get('path')}")
        except ValueError as error:
            return _fail(str(error))
        except (OSError, sqlite3.Error) as error:  # storage trouble: report the kind, not file paths
            return _fail(f"storage error: {type(error).__name__}")

    def _skill(self, name: str) -> Skill:
        skill = self._skills.get(name)
        if skill is None:
            raise ValueError(f"unknown skill '{name}'")
        return skill

    def _check_dependencies(self, args: Mapping[str, Any]) -> dict[str, Any]:
        skill = self._skill(args["skill"])
        missing = list(missing_dependencies(self._ws, skill.name))
        return _ok({"skill": skill.name, "missing": missing, "ready": not missing})

    def _list_artifacts(self, args: Mapping[str, Any]) -> dict[str, Any]:
        artifacts, problems = scan_artifacts(self._ws)
        rows = [
            {"path": a.path, "skill": a.skill, "stage": a.stage, "status": a.status, "created": a.created}
            for a in artifacts
            if args.get("stage") in (None, a.stage) and args.get("status") in (None, a.status)
        ]
        return _ok({
            "artifacts": rows[:MAX_LIST],
            "truncated": len(rows) > MAX_LIST,
            "problems": [{"path": p.path, "message": p.message} for p in problems],
        })

    def _read_artifact(self, args: Mapping[str, Any]) -> dict[str, Any]:
        art = read_artifact(self._ws, args["path"])
        return _ok({
            "path": art.path, "skill": art.skill, "stage": art.stage, "status": art.status,
            "created": art.created, "inputs": list(art.inputs), "supersedes": art.supersedes,
            "bypassed": list(art.bypassed), "body": art.body,
        })

    def _read_product(self, _args: Mapping[str, Any]) -> dict[str, Any]:
        return _ok({"product_md": (self._ws / "product.md").read_text(encoding="utf-8")})

    def _search_memory(self, args: Mapping[str, Any]) -> dict[str, Any]:
        rebuild_index(self._ws)  # cheap at this scale and always reflects files on disk
        hits = search(self._ws, args["query"], stage=args.get("stage"),
                      limit=args.get("limit", DEFAULT_SEARCH))
        return _ok({"hits": [{"path": h.path, "skill": h.skill, "stage": h.stage, "status": h.status}
                             for h in hits]})

    def _write_artifact(self, args: Mapping[str, Any]) -> dict[str, Any]:
        skill = self._skill(args["skill"])
        acknowledged = args.get("acknowledge_missing") or []
        missing = missing_dependencies(self._ws, skill.name)
        unacknowledged = [dep for dep in missing if dep not in acknowledged]
        if unacknowledged:
            return _fail(
                f"missing approved upstream artifacts: {unacknowledged}. Tell the user, and if they "
                f"choose to proceed anyway, call again with acknowledge_missing={unacknowledged}."
            )
        art = write_artifact(
            self._ws, skill=skill.name, stage=skill.stage, slug=args["slug"], body=args["body"],
            inputs=tuple(args.get("inputs") or ()), bypassed=tuple(missing),
        )
        rebuild_index(self._ws)
        result: dict[str, Any] = {
            "path": art.path, "status": art.status,
            "note": "saved as a draft; it needs human approval before it counts",
        }
        if missing:
            result["acknowledged_missing"] = list(missing)
        return _ok(result)

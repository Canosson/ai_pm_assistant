"""SQLite index (FTS5 + artifact graph). Derived from the markdown files; safe to delete and rebuild."""

from __future__ import annotations

import os
import re
import sqlite3
import tempfile
import threading
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from pm_agent.memory import scan_artifacts

INDEX_NAME = ".index.sqlite"
_REBUILD_LOCK = threading.Lock()  # one rebuild at a time per process; the replace below covers processes
_SCHEMA = """
CREATE TABLE artifacts (path TEXT PRIMARY KEY, skill TEXT, stage TEXT, status TEXT, created TEXT);
CREATE VIRTUAL TABLE artifact_fts USING fts5(path UNINDEXED, body);
CREATE TABLE edges (src TEXT NOT NULL, dst TEXT NOT NULL);
CREATE INDEX edges_dst ON edges (dst);
"""


@dataclass(frozen=True)
class Hit:
    path: str
    skill: str
    stage: str
    status: str


def _db(ws: Path) -> Path:
    return ws / INDEX_NAME


def _require_index(ws: Path) -> Path:
    db = _db(ws)
    if not db.exists():  # sqlite3.connect would silently create an empty file
        raise FileNotFoundError(f"no index at {db.name}: call rebuild_index first")
    return db


def rebuild_index(ws: Path) -> Path:
    """Build a fresh index beside the old one and swap it in atomically; a failure keeps the old one."""
    target = _db(ws)
    artifacts, _problems = scan_artifacts(ws)  # unreadable files are reported by scan, not indexed
    with _REBUILD_LOCK:
        fd, tmp = tempfile.mkstemp(dir=ws, prefix=".index-", suffix=".tmp")
        os.close(fd)
        try:
            with closing(sqlite3.connect(tmp)) as conn, conn:
                conn.executescript(_SCHEMA)
                for art in artifacts:
                    conn.execute("INSERT INTO artifacts VALUES (?,?,?,?,?)",
                                 (art.path, art.skill, art.stage, art.status, art.created))
                    conn.execute("INSERT INTO artifact_fts VALUES (?,?)", (art.path, art.body))
                    conn.executemany("INSERT INTO edges VALUES (?,?)", [(art.path, dep) for dep in art.inputs])
            os.replace(tmp, target)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
    return target


def _match_expression(query: str) -> str | None:
    """Quote every word so user text can never be parsed as FTS5 syntax; any word may match."""
    words = re.findall(r"\w+", query)
    return " OR ".join(f'"{word}"' for word in words) if words else None


def search(ws: Path, query: str, *, stage: str | None = None, limit: int = 10) -> tuple[Hit, ...]:
    expression = _match_expression(query)
    if expression is None:
        return ()
    if limit < 1:
        raise ValueError("limit must be at least 1")  # SQLite treats LIMIT -1 as unlimited
    sql = (
        "SELECT a.path, a.skill, a.stage, a.status FROM artifact_fts f "
        "JOIN artifacts a ON a.path = f.path WHERE artifact_fts MATCH ?"
    )
    params: list[object] = [expression]
    if stage:
        sql += " AND a.stage = ?"
        params.append(stage)
    sql += " ORDER BY f.rank, a.path LIMIT ?"
    params.append(limit)
    with closing(sqlite3.connect(_require_index(ws))) as conn:
        return tuple(Hit(*row) for row in conn.execute(sql, params))


def _edges(ws: Path, sql: str, path: str) -> tuple[str, ...]:
    with closing(sqlite3.connect(_require_index(ws))) as conn:
        return tuple(row[0] for row in conn.execute(sql, (path,)))


def upstream(ws: Path, rel_path: str) -> tuple[str, ...]:
    return _edges(ws, "SELECT dst FROM edges WHERE src = ? ORDER BY dst", rel_path)


def downstream(ws: Path, rel_path: str) -> tuple[str, ...]:
    return _edges(ws, "SELECT src FROM edges WHERE dst = ? ORDER BY src", rel_path)

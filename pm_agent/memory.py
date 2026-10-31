"""Memory repository: per-product workspace of immutable, versioned artifacts plus product.md."""

from __future__ import annotations

import json
import logging
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from pm_agent.skills import STAGES

log = logging.getLogger(__name__)

WORKSPACE_DIRS = ("research", "decisions", "backlog", "launches", "experiments", "artifacts")
SLUG_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")  # used with fullmatch: `$` would allow a trailing \n
MAX_SLUG = 60
STATUSES = ("draft", "approved")
PRODUCT_SECTIONS = ("Vision", "Strategy", "North Star", "OKRs")
SECTION_FOR_SKILL = {
    "product-vision": "Vision",
    "product-strategy": "Strategy",
    "north-star-metric": "North Star",
    "product-okrs": "OKRs",
}
_FRONTMATTER = re.compile(r"^---\n(.*?)\n---\n\n?(.*?)\n?$", re.S)
_VERSION_SUFFIX = re.compile(r"-v\d+$")


@dataclass(frozen=True)
class Artifact:
    path: str  # relative to the workspace
    skill: str
    stage: str
    status: str  # draft | approved
    created: str  # ISO date
    inputs: tuple[str, ...]
    supersedes: str | None
    body: str  # stored without leading/trailing blank lines
    bypassed: tuple[str, ...] = ()  # upstream skills skipped on the user's say-so, kept for audit


@dataclass(frozen=True)
class Problem:
    path: str
    message: str


def _check_slug(slug: str) -> None:
    if len(slug) > MAX_SLUG or not SLUG_PATTERN.fullmatch(slug):
        raise ValueError(
            f"invalid slug: use 1-{MAX_SLUG} lowercase letters, digits and single hyphens"
        )


def _check_relative(path: str) -> None:
    parts = Path(path).parts
    if Path(path).is_absolute() or ".." in parts or not parts:
        raise ValueError(f"path must be relative and stay inside the workspace: '{path}'")


def _today() -> str:
    return date.today().isoformat()


def init_workspace(root: Path, product: str) -> Path:
    _check_slug(product)
    ws = root / product
    for folder in WORKSPACE_DIRS:
        (ws / folder).mkdir(parents=True, exist_ok=True)
    product_md = ws / "product.md"
    if not product_md.exists():
        sections = "\n\n".join(
            f"## {name}\n\n{_start(name)}\n_Not set._\n{_end(name)}" for name in PRODUCT_SECTIONS
        )
        product_md.write_text(f"# {product}\n\n{sections}\n", encoding="utf-8")
    return ws


def _serialize(art: Artifact) -> str:
    lines = [
        f"skill: {art.skill}",
        f"stage: {art.stage}",
        f"status: {art.status}",
        f"created: {art.created}",
        f"inputs: {json.dumps(list(art.inputs))}",
    ]
    if art.supersedes:
        lines.append(f"supersedes: {art.supersedes}")
    if art.bypassed:
        lines.append(f"bypassed: {json.dumps(list(art.bypassed))}")
    return "---\n" + "\n".join(lines) + "\n---\n\n" + art.body + "\n"


def _string_list(raw: str, rel_path: str, name: str) -> tuple[str, ...]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError(f"{rel_path}: '{name}' is not valid JSON") from error
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ValueError(f"{rel_path}: '{name}' must be a JSON list of strings")
    return tuple(value)


def _parse(rel_path: str, text: str) -> Artifact:
    match = _FRONTMATTER.match(text)
    if not match:
        raise ValueError(f"{rel_path}: missing frontmatter")
    front, body = match.groups()
    fields = dict(line.split(": ", 1) for line in front.splitlines() if ": " in line)
    for required in ("skill", "stage", "status", "created", "inputs"):
        if required not in fields:
            raise ValueError(f"{rel_path}: missing '{required}' in frontmatter")
    if fields["status"] not in STATUSES:
        raise ValueError(f"{rel_path}: status must be one of {STATUSES}")
    if fields["stage"] not in STAGES:
        raise ValueError(f"{rel_path}: unknown stage '{fields['stage']}'")
    return Artifact(
        path=rel_path,
        skill=fields["skill"],
        stage=fields["stage"],
        status=fields["status"],
        created=fields["created"],
        inputs=_string_list(fields["inputs"], rel_path, "inputs"),
        supersedes=fields.get("supersedes"),
        body=body,
        bypassed=_string_list(fields["bypassed"], rel_path, "bypassed") if "bypassed" in fields else (),
    )


def _write_new(ws: Path, stage: str, stem: str, build) -> Artifact:
    """Create artifacts/<stage>/<stem>[-vN].md atomically; never overwrite an existing file.

    The content is fully written and fsynced to a temp file first, then hard-linked into place:
    the link fails if the target exists (exclusive create), and readers never see a partial file.
    """
    if stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    folder = ws / "artifacts" / stage
    folder.mkdir(parents=True, exist_ok=True)
    version = 1
    while True:
        name = f"{stem}.md" if version == 1 else f"{stem}-v{version}.md"
        rel = f"artifacts/{stage}/{name}"
        art = build(rel)
        fd, tmp = tempfile.mkstemp(dir=folder, prefix=".pending-", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(_serialize(art))
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(tmp, ws / rel)
            except FileExistsError:
                version += 1
                continue
            return art
        finally:
            Path(tmp).unlink(missing_ok=True)


def write_artifact(
    ws: Path,
    *,
    skill: str,
    stage: str,
    slug: str,
    body: str,
    inputs: tuple[str, ...] = (),
    created: str | None = None,
    bypassed: tuple[str, ...] = (),
) -> Artifact:
    _check_slug(slug)
    if stage not in STAGES:
        raise ValueError(f"unknown stage '{stage}'")
    when = date.fromisoformat(created).isoformat() if created else _today()
    for item in inputs:
        _check_relative(item)
    clean = body.strip("\n")
    return _write_new(
        ws, stage, f"{when}-{slug}",
        lambda rel: Artifact(rel, skill, stage, "draft", when, tuple(inputs), None, clean, tuple(bypassed)),
    )


def read_artifact(ws: Path, rel_path: str) -> Artifact:
    _check_relative(rel_path)
    target = (ws / rel_path).resolve()
    if not target.is_relative_to(ws.resolve()):  # a symlink must not lead out of the workspace
        raise ValueError(f"path must stay inside the workspace: '{rel_path}'")
    if not target.is_file():
        raise FileNotFoundError(rel_path)
    return _parse(rel_path, target.read_text(encoding="utf-8"))


def scan_artifacts(ws: Path) -> tuple[tuple[Artifact, ...], tuple[Problem, ...]]:
    """All readable artifacts, plus a report of files that could not be read (never silently dropped)."""
    folder = ws / "artifacts"
    artifacts: list[Artifact] = []
    problems: list[Problem] = []
    for rel in sorted(p.relative_to(ws).as_posix() for p in folder.rglob("*.md")):
        try:
            artifacts.append(read_artifact(ws, rel))
        except (ValueError, OSError) as error:  # includes UnicodeDecodeError
            problems.append(Problem(rel, str(error)))
    return tuple(artifacts), tuple(problems)


def list_artifacts(ws: Path) -> tuple[Artifact, ...]:
    artifacts, problems = scan_artifacts(ws)
    for problem in problems:
        log.warning("skipping unreadable artifact %s: %s", problem.path, problem.message)
    return artifacts


def approve_artifact(ws: Path, rel_path: str, created: str | None = None) -> Artifact:
    """Approval writes a NEW version (status approved, supersedes the original); nothing is edited."""
    original = read_artifact(ws, rel_path)
    if original.status == "approved":
        raise ValueError(f"{rel_path} is already approved")
    existing, _ = scan_artifacts(ws)
    for other in existing:
        if other.supersedes == original.path:
            raise ValueError(f"{rel_path} was already approved as {other.path}")
    when = date.fromisoformat(created).isoformat() if created else _today()
    stem = _VERSION_SUFFIX.sub("", Path(rel_path).stem)
    return _write_new(
        ws, original.stage, stem,
        lambda rel: Artifact(rel, original.skill, original.stage, "approved", when,
                             original.inputs, original.path, original.body, original.bypassed),
    )


def _atomic_write(target: Path, text: str) -> None:
    mode = stat.S_IMODE(target.stat().st_mode) if target.exists() else 0o644
    fd, tmp = tempfile.mkstemp(dir=target.parent, prefix=".tmp-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, target)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def _start(section: str) -> str:
    return f"<!-- pm:start {section} -->"


def _end(section: str) -> str:
    return f"<!-- pm:end {section} -->"


def update_product_from(ws: Path, artifact: Artifact) -> None:
    """Copy an APPROVED artifact into its product.md section.

    Each section is fenced by start/end markers, so a body that contains its own `##` headings can
    never corrupt neighbouring sections. A product.md without markers is appended to, never rewritten.
    """
    if artifact.status != "approved":
        raise ValueError(f"{artifact.path} is not approved; only approved artifacts update product.md")
    section = SECTION_FOR_SKILL.get(artifact.skill)
    if section is None:
        raise ValueError(f"no product.md section for skill '{artifact.skill}'")
    if "<!-- pm:" in artifact.body:
        raise ValueError("artifact body contains reserved product.md markers")
    block = f"{_start(section)}\n{artifact.body}\n\n_Source: {artifact.path}_\n{_end(section)}"
    product_md = ws / "product.md"
    text = product_md.read_text(encoding="utf-8")
    fenced = re.compile(rf"{re.escape(_start(section))}.*?{re.escape(_end(section))}", re.S)
    if fenced.search(text):
        updated = fenced.sub(lambda _: block, text, count=1)
    else:
        updated = f"{text.rstrip(chr(10))}\n\n## {section}\n\n{block}\n"
    _atomic_write(product_md, updated.rstrip("\n") + "\n")

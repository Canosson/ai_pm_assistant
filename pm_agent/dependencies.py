"""Hard dependencies between skills: an upstream skill needs an APPROVED artifact first."""

from __future__ import annotations

from pathlib import Path
from types import MappingProxyType

from pm_agent.memory import list_artifacts

DEPENDENCIES = MappingProxyType({
    "product-roadmap": ("product-okrs",),
    "success-metrics": ("north-star-metric",),
    "experiment-design": ("success-metrics",),
    "launch-readiness-review": ("launch-checklist",),
    "post-launch-review": ("success-metrics",),
})


def missing_dependencies(ws: Path, skill: str) -> tuple[str, ...]:
    """Upstream skills (in declared order) that have no approved artifact yet."""
    required = DEPENDENCIES.get(skill, ())
    if not required:
        return ()
    approved = {a.skill for a in list_artifacts(ws) if a.status == "approved"}
    return tuple(dep for dep in required if dep not in approved)

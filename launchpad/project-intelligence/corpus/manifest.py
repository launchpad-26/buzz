"""One-document one-task corpus manifest -- issue #626.

Turns a caller-supplied plan (one dict per planned canonical or generated
corpus document) into a validated, deterministic `Manifest` -- the input
`launchpad/project-intelligence/corpus/issue_plan.py` (#627, not yet built)
will read to create GitHub tasks without manual rewriting.

This module does not itself decide WHICH documents the corpus needs, what
their titles are, or which template each gets -- that is real product
knowledge (`launchpad/docs/corpus/AGENTS.md`'s per-type standards and
templates, most still unmerged per issue #605) that belongs to whoever
curates the plan, not to a script guessing on their behalf. What this module
owns is turning that plan into a manifest with the structural guarantees
issue #626's definition of done requires: one row per document, every
required field present, no document assigned to two tasks, no task owning
two documents, and no Feature exceeding GitHub's 100-sub-issue limit --
enforced, not assumed.

Run as a library -- `build_manifest(plan)` is the entry point tests and
future callers use. There is no CLI; the plan itself has no fixed source
yet (see #626's "Out of scope": authoring canonical corpus documents is not
this task).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

# GitHub's current sub-issue limit per parent, cited directly in #626's
# definition of done. If GitHub raises this limit, this constant is the one
# place to change it.
_MAX_CHILDREN_PER_FEATURE = 100

_REQUIRED_KEYS = frozenset(
    {
        "path",
        "filename",
        "issue_title",
        "parent_feature",
        "priority",
        "start_date",
        "target_date",
        "effort",
        "blockers",
        "template",
        "purpose",
        "audiences",
        "source_start_points",
    }
)


class ManifestValidationError(Exception):
    """The plan violates one of #626's structural guarantees. Never silently dropped or renamed."""


@dataclass(frozen=True)
class ManifestRow:
    path: str
    filename: str
    issue_title: str
    parent_feature: str
    priority: str
    start_date: str | None
    target_date: str | None
    effort: str
    blockers: tuple[str, ...]
    template: str
    purpose: str
    audiences: tuple[str, ...]
    source_start_points: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "filename": self.filename,
            "issue_title": self.issue_title,
            "parent_feature": self.parent_feature,
            "priority": self.priority,
            "start_date": self.start_date,
            "target_date": self.target_date,
            "effort": self.effort,
            "blockers": list(self.blockers),
            "template": self.template,
            "purpose": self.purpose,
            "audiences": list(self.audiences),
            "source_start_points": list(self.source_start_points),
        }


@dataclass
class Manifest:
    rows: list[ManifestRow] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {"rows": [row.to_dict() for row in self.rows]}
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _row_from_plan_entry(entry: dict) -> ManifestRow:
    missing = _REQUIRED_KEYS - entry.keys()
    if missing:
        raise ManifestValidationError(
            f"plan entry for {entry.get('path', '<no path given>')!r} "
            f"is missing required field(s): {sorted(missing)}"
        )
    return ManifestRow(
        path=entry["path"],
        filename=entry["filename"],
        issue_title=entry["issue_title"],
        parent_feature=entry["parent_feature"],
        priority=entry["priority"],
        start_date=entry["start_date"],
        target_date=entry["target_date"],
        effort=entry["effort"],
        blockers=tuple(entry["blockers"]),
        template=entry["template"],
        purpose=entry["purpose"],
        audiences=tuple(entry["audiences"]),
        source_start_points=tuple(entry["source_start_points"]),
    )


def _check_no_duplicate_paths(rows: list[ManifestRow]) -> None:
    seen: dict[str, ManifestRow] = {}
    for row in rows:
        if row.path in seen:
            raise ManifestValidationError(
                f"document {row.path!r} is assigned to two tasks: "
                f"{seen[row.path].issue_title!r} and {row.issue_title!r}"
            )
        seen[row.path] = row


def _check_no_duplicate_issue_titles(rows: list[ManifestRow]) -> None:
    seen: dict[str, ManifestRow] = {}
    for row in rows:
        if row.issue_title in seen:
            raise ManifestValidationError(
                f"task {row.issue_title!r} would own two hand-authored canonical "
                f"documents: {seen[row.issue_title].path!r} and {row.path!r}"
            )
        seen[row.issue_title] = row


def _check_feature_child_limits(rows: list[ManifestRow]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row.parent_feature] = counts.get(row.parent_feature, 0) + 1
    for feature, count in counts.items():
        if count > _MAX_CHILDREN_PER_FEATURE:
            raise ManifestValidationError(
                f"parent feature {feature!r} would own {count} document tasks, "
                f"exceeding GitHub's {_MAX_CHILDREN_PER_FEATURE}-sub-issue limit"
            )


def build_manifest(plan: list[dict]) -> Manifest:
    """Validate `plan` and return a deterministic Manifest sorted by document path.

    Raises ManifestValidationError on any structural violation -- a missing
    field, a path or issue_title reused across rows, or a Feature exceeding
    the sub-issue limit -- rather than dropping or silently coercing the bad
    row. Re-running against the same `plan` list always returns rows in the
    same order (sorted by path) and therefore the same `to_json()` output.
    """
    rows = [_row_from_plan_entry(entry) for entry in plan]
    _check_no_duplicate_paths(rows)
    _check_no_duplicate_issue_titles(rows)
    _check_feature_child_limits(rows)
    return Manifest(rows=sorted(rows, key=lambda r: r.path))

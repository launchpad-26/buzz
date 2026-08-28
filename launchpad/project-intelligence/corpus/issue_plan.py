"""Idempotent GitHub issue-plan helper -- issue #627.

Turns a #626 manifest into GitHub document tasks: `dry_run` emits every
proposed issue body/metadata/relationship without touching GitHub at all;
`apply` creates only what's missing, using a `GitHubPort` (real `gh`-backed
by default, injectable for tests) to check for an existing issue by exact
title before ever creating one -- the same guard that makes a second,
interrupted-and-resumed run produce zero duplicates rather than a second
document task per row.

Nothing here pretends success it did not achieve: a project field the port
could not write lands in `ApplyResult.manual_actions`, a blocker relationship
the port could not apply (or whose target has not been created yet) lands in
`ApplyResult.unresolved_blockers`, and a sub-issue link is verified by
re-reading the parent's child list after linking, not assumed from the link
call's own success.

Run as a library -- `dry_run(rows)` and `apply(rows, port, repo, ledger)`
are the entry points. There is no CLI in this first implementation.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field


@dataclass(frozen=True)
class PlannedIssue:
    alias: str
    title: str
    body: str
    labels: tuple[str, ...]
    milestone: str | None
    parent_alias: str | None
    project_fields: dict
    blockers: tuple[str, ...]

    def to_dict(self) -> dict:
        return {
            "alias": self.alias,
            "title": self.title,
            "body": self.body,
            "labels": list(self.labels),
            "milestone": self.milestone,
            "parent_alias": self.parent_alias,
            "project_fields": self.project_fields,
            "blockers": list(self.blockers),
        }


def plan_from_manifest(rows: list) -> list[PlannedIssue]:
    """Pure transform: one #626 ManifestRow -> one PlannedIssue, in row order.

    `alias` is the row's `path` -- already guaranteed unique by
    `manifest.build_manifest` (issue #626 rejects duplicate paths), so it
    doubles safely as this planner's stable alias without inventing a
    second identifier scheme.
    """
    planned = []
    for row in rows:
        planned.append(
            PlannedIssue(
                alias=row.path,
                title=row.issue_title,
                body=(
                    f"### Parent PRD\n\n{row.parent_feature}\n\n"
                    f"### Objective\n\n{row.purpose}\n\n"
                    f"### Template\n\n{row.template}\n\n"
                    f"### Audiences\n\n{', '.join(row.audiences)}\n\n"
                    f"### Source start points\n\n"
                    + "\n".join(f"- {s}" for s in row.source_start_points)
                ),
                labels=("by:agent",),
                milestone=None,
                parent_alias=row.parent_feature,
                project_fields={
                    "Priority": row.priority,
                    "Start date": row.start_date,
                    "Target date": row.target_date,
                    "Effort": row.effort,
                },
                blockers=tuple(row.blockers),
            )
        )
    return planned


@dataclass
class DryRunResult:
    planned: list[PlannedIssue] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {"planned": [p.to_dict() for p in self.planned]}
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def dry_run(rows: list) -> DryRunResult:
    """Emit the full plan. Never calls anything on a GitHubPort -- no mutation is possible."""
    return DryRunResult(planned=plan_from_manifest(rows))


class GitHubPort:
    """Read/write GitHub operations this helper needs, via `gh`. Override for tests."""

    def find_issue_by_title(self, repo: str, title: str) -> int | None:
        out = subprocess.run(
            ["gh", "issue", "list", "--repo", repo, "--search", f'"{title}" in:title', "--state", "all", "--json", "number,title"],
            capture_output=True,
            text=True,
            check=True,
        )
        for row in json.loads(out.stdout):
            if row["title"] == title:
                return row["number"]
        return None

    def create_issue(self, repo: str, title: str, body: str, labels: tuple[str, ...]) -> int:
        args = ["gh", "issue", "create", "--repo", repo, "--title", title, "--body", body]
        for label in labels:
            args.extend(["--label", label])
        out = subprocess.run(args, capture_output=True, text=True, check=True)
        url = out.stdout.strip()
        return int(url.rstrip("/").rsplit("/", 1)[-1])

    def __init__(self, project_owner: str | None = None, project_number: int | None = None) -> None:
        self.project_owner = project_owner
        self.project_number = project_number
        self._project_node_id: str | None = None
        self._project_fields_cache: dict | None = None

    def add_sub_issue(self, repo: str, parent_number: int, child_number: int) -> None:
        child_id = self._issue_database_id(repo, child_number)
        subprocess.run(
            ["gh", "api", f"repos/{repo}/issues/{parent_number}/sub_issues", "-X", "POST", "-F", f"sub_issue_id={child_id}"],
            capture_output=True,
            text=True,
            check=True,
        )

    def get_sub_issue_numbers(self, repo: str, parent_number: int) -> list[int]:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}/issues/{parent_number}/sub_issues", "--jq", "[.[].number]"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(out.stdout)

    def _issue_database_id(self, repo: str, number: int) -> int:
        out = subprocess.run(
            ["gh", "api", f"repos/{repo}/issues/{number}", "--jq", ".id"],
            capture_output=True,
            text=True,
            check=True,
        )
        return int(out.stdout.strip())

    def _project_node_id_cached(self) -> str:
        if self._project_node_id is None:
            out = subprocess.run(
                ["gh", "project", "view", str(self.project_number), "--owner", self.project_owner, "--format", "json", "--jq", ".id"],
                capture_output=True,
                text=True,
                check=True,
            )
            self._project_node_id = out.stdout.strip()
        return self._project_node_id

    def _project_fields_cached(self) -> dict:
        if self._project_fields_cache is None:
            out = subprocess.run(
                ["gh", "project", "field-list", str(self.project_number), "--owner", self.project_owner, "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
            )
            data = json.loads(out.stdout)
            self._project_fields_cache = {f["name"]: f for f in data["fields"]}
        return self._project_fields_cache

    def _project_item_id(self, repo: str, issue_number: int) -> str:
        url = f"https://github.com/{repo}/issues/{issue_number}"
        out = subprocess.run(
            ["gh", "project", "item-add", str(self.project_number), "--owner", self.project_owner, "--url", url, "--format", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(out.stdout)["id"]

    # Only these two names are ever written as GitHub Projects Date fields --
    # every other writable field this helper knows about (Priority, Effort)
    # is single-select. Not derived from the field-list response because its
    # JSON does not name the underlying scalar type for a plain
    # ProjectV2Field the way it names "options" for a single-select one.
    _DATE_FIELD_NAMES = {"Start date", "Target date"}

    def set_project_field(self, repo: str, issue_number: int, field_name: str, value) -> bool:
        if self.project_owner is None or self.project_number is None:
            return False
        try:
            field = self._project_fields_cached().get(field_name)
            if field is None:
                return False
            item_id = self._project_item_id(repo, issue_number)
            args = [
                "gh", "project", "item-edit",
                "--project-id", self._project_node_id_cached(),
                "--id", item_id,
                "--field-id", field["id"],
            ]
            if "options" in field:
                option = next((o for o in field["options"] if o["name"] == str(value)), None)
                if option is None:
                    return False
                args += ["--single-select-option-id", option["id"]]
            elif field_name in self._DATE_FIELD_NAMES:
                args += ["--date", str(value)]
            else:
                args += ["--text", str(value)]
            subprocess.run(args, capture_output=True, text=True, check=True)
            return True
        except (subprocess.CalledProcessError, KeyError, json.JSONDecodeError):
            return False

    def set_blocked_by(self, repo: str, issue_number: int, blocker_issue_number: int) -> bool:
        # Deliberately always False: unlike sub-issues, GitHub has no
        # confirmed stable public API for an arbitrary issue-to-issue
        # "blocked by" relationship as of this module's writing -- fabricating
        # a call against an unconfirmed endpoint would be worse than the
        # honest unresolved-dependency path #627's own definition of done
        # names for exactly this case ("otherwise... a deterministic
        # unresolved dependency list rather than pretending success").
        return False


@dataclass
class ApplyResult:
    created: dict = field(default_factory=dict)
    already_existed: dict = field(default_factory=dict)
    manual_actions: list = field(default_factory=list)
    unresolved_blockers: list = field(default_factory=list)
    sub_issue_link_failures: list = field(default_factory=list)


def apply(rows: list, port: GitHubPort, repo: str, alias_ledger: dict | None = None) -> ApplyResult:
    """Create every missing document task from `rows`, idempotently.

    `alias_ledger` is the accumulated alias->issue-number map from a prior
    (possibly interrupted) run -- pass the previous ApplyResult's
    `created | already_existed` back in to resume without re-creating
    anything the ledger, or GitHub's own exact-title search, already knows
    about. A fresh run passes `None` (equivalent to an empty ledger).
    """
    ledger = dict(alias_ledger or {})
    result = ApplyResult()
    planned = plan_from_manifest(rows)

    for issue in planned:
        if issue.alias in ledger:
            result.already_existed[issue.alias] = ledger[issue.alias]
            continue
        existing = port.find_issue_by_title(repo, issue.title)
        if existing is not None:
            result.already_existed[issue.alias] = existing
            ledger[issue.alias] = existing
            continue
        number = port.create_issue(repo, issue.title, issue.body, issue.labels)
        result.created[issue.alias] = number
        ledger[issue.alias] = number

    for issue in planned:
        number = ledger[issue.alias]
        _apply_project_fields(port, repo, number, issue, result)
        _apply_blockers(port, repo, number, issue, ledger, result)

    return result


def _apply_project_fields(port: GitHubPort, repo: str, number: int, issue: PlannedIssue, result: ApplyResult) -> None:
    for field_name, value in issue.project_fields.items():
        if value is None:
            continue
        try:
            wrote = port.set_project_field(repo, number, field_name, value)
        except NotImplementedError:
            wrote = False
        if not wrote:
            result.manual_actions.append(
                f"Manually set {field_name}={value!r} on issue #{number} ({issue.alias})"
            )


def _apply_blockers(
    port: GitHubPort, repo: str, number: int, issue: PlannedIssue, ledger: dict, result: ApplyResult
) -> None:
    for blocker_alias in issue.blockers:
        blocker_number = ledger.get(blocker_alias)
        if blocker_number is None:
            result.unresolved_blockers.append(
                {"alias": issue.alias, "blocker_alias": blocker_alias, "reason": "blocker not yet created"}
            )
            continue
        try:
            applied = port.set_blocked_by(repo, number, blocker_number)
        except NotImplementedError:
            applied = False
        if not applied:
            result.unresolved_blockers.append(
                {
                    "alias": issue.alias,
                    "blocker_alias": blocker_alias,
                    "reason": "port could not apply a blocked-by relationship",
                }
            )


def link_sub_issue(port: GitHubPort, repo: str, parent_number: int, child_number: int) -> bool:
    """Link `child_number` under `parent_number`, then verify by re-reading the parent's children.

    Returns True only if the link call succeeded AND the child now appears
    in the parent's own reported sub-issue list -- the call succeeding is
    not, by itself, taken as proof of anything.
    """
    port.add_sub_issue(repo, parent_number, child_number)
    children = port.get_sub_issue_numbers(repo, parent_number)
    return child_number in children

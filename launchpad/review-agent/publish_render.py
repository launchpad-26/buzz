"""Render the findings body for the one review comment #119 publishes.

A pure function: no network, no subprocess, no posting. This module must never import
``publish`` -- STEP 7 puts ``main`` in publish.py, and if this module also imported
publish for the marker constant the two files would form an import cycle, so the
marker is passed in as an argument instead (see :func:`render_body`).

Two kinds of untrusted text pass through here, and each gets a different treatment:

``defect``/``failure`` are model-authored prose describing a finding. Only
``contain.TOKEN`` is neutralised in them -- not the full :func:`contain.escape`,
because that also doubles every literal tilde, and this fork's own subject matter is
dotfile paths (``~/.claude/...``). Doubled tildes render as GitHub-flavoured-markdown
strikethrough, so escaping ordinary prose the same way evidence is escaped would
visibly corrupt the most likely findings in the one place a human reads them.

``evidence`` (on a dimension finding with an ``entry_point``, and on every containment
finding) is pull-request-authored text quoted verbatim by the author under review. It
is rendered through :func:`contain.escape` and inside a fence sized by
:func:`review.fence_for`, both imported rather than reimplemented, so attacker text
containing a run of backticks cannot close the fence early and spill the remainder of
the review out of its code block. A malformed finding's raw record gets the same
treatment, for the same reason: it is the path a record takes precisely because its
fields did not match the contract, so it is the last place to assume anything is
well-formed.
"""

from __future__ import annotations

import json

import contain
import review

MALFORMED_HEADING = "### Malformed finding"

_VALID_ANCHORS = ("pr", "file", "line")


def _escape_prose(text: str) -> str:
    """Neutralise only the envelope token -- see the module docstring."""
    return text.replace(contain.TOKEN, contain.ESC_TOKEN)


def _is_malformed(finding: dict) -> bool:
    anchor = finding.get("anchor")
    file = finding.get("file")
    line = finding.get("line")
    if anchor == "pr":
        if file is not None or line is not None:
            return True
    elif anchor == "file":
        if file is None or line is not None:
            return True
    elif anchor == "line":
        if file is None or line is None:
            return True
    else:
        return True
    return finding.get("severity") not in review.SEVERITY_ORDER


def _anchor_display(finding: dict) -> str:
    anchor = finding.get("anchor")
    if anchor == "line":
        return f"{finding.get('file')}:{finding.get('line')}"
    if anchor == "file":
        return f"{finding.get('file')}"
    if anchor == "pr":
        return "(pull request)"
    return "(unrecognised anchor)"


def _sort_key(finding: dict) -> tuple:
    return (
        review.SEVERITY_ORDER.get(finding.get("severity"), 9),
        finding.get("dimension") or "",
        finding.get("file") or "",
        finding.get("line") or 0,
        finding.get("finding_id") or "",
    )


def _render_malformed(finding: dict) -> str:
    raw = json.dumps(finding, indent=2, default=str)
    fence = review.fence_for(raw)
    return "\n".join([MALFORMED_HEADING, "", fence, contain.escape(raw), fence, ""])


def _render_finding(finding: dict, dimension_count: int | None) -> str:
    lines = [
        f"### {finding.get('severity')} — {finding.get('dimension')} — "
        f"{_anchor_display(finding)}",
        "",
    ]
    verdict = finding.get("verdict")
    if verdict is not None:
        lines.append(f"**Verdict:** {verdict}")
        lines.append("")
    lines.append(f"Defect: {_escape_prose(finding.get('defect', ''))}")
    lines.append("")
    lines.append(f"Failure: {_escape_prose(finding.get('failure', ''))}")
    lines.append("")
    entry_point = finding.get("entry_point")
    evidence = finding.get("evidence")
    if entry_point is not None and evidence is not None:
        lines.append(f"Entry point: `{entry_point}`")
        lines.append("")
        fence = review.fence_for(evidence)
        lines.append(fence)
        lines.append(contain.escape(evidence))
        lines.append(fence)
        lines.append("")
    if dimension_count is not None:
        lines.append(f"(reported by {dimension_count} dimensions)")
        lines.append("")
    return "\n".join(lines)


def render_body(
    marker: str,
    reports: list[dict],
    stages: dict,
    containment: dict | None,
    head_sha: str,
    merge_base_sha: str,
    duplicate_groups=(),
) -> str:
    """The full review body. ``stages`` is accepted, unused here -- STEP 5's
    incomplete banner reads it; the parameter exists now so that step does not
    change this signature.
    """
    lines = [
        marker,
        "",
        f"Reviewed commit `{head_sha}` against merge base `{merge_base_sha}`.",
        "",
    ]

    if containment is not None:
        contain_findings = [
            contain.Finding(
                kind=f["kind"],
                entry_point=f["entry_point"],
                evidence=f["evidence"],
                severity=f.get("severity", "Blocker"),
            )
            for f in containment.get("findings", [])
        ]
        lines.append(review.render_review(contain_findings, containment.get("states", {})))
        lines.append("")

    all_findings: list[dict] = []
    for report in reports:
        for finding in report.get("findings", []) or []:
            all_findings.append(dict(finding))
    by_id = {f.get("finding_id"): f for f in all_findings if f.get("finding_id") is not None}

    remove_ids: set = set()
    force_malformed_ids: set = set()
    dimension_count_by_id: dict = {}
    for group in duplicate_groups:
        survivor = group.get("survivor")
        duplicates = group.get("duplicates") or []
        if survivor in by_id:
            dimension_count_by_id[survivor] = 1 + len(duplicates)
            remove_ids.update(duplicates)
        else:
            # The intended collapse target does not exist in this render pass.
            # Fail closed: the real duplicate still renders, flagged malformed,
            # rather than being silently dropped from the count or the output.
            for dup_id in duplicates:
                if dup_id in by_id:
                    force_malformed_ids.add(dup_id)

    render_list = [f for f in all_findings if f.get("finding_id") not in remove_ids]
    ordered = sorted(render_list, key=_sort_key)

    for finding in ordered:
        if _is_malformed(finding) or finding.get("finding_id") in force_malformed_ids:
            lines.append(_render_malformed(finding))
        else:
            lines.append(
                _render_finding(finding, dimension_count_by_id.get(finding.get("finding_id")))
            )

    return "\n".join(lines)

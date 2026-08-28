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
INCOMPLETE_HEADING = "## Incomplete"

_VALID_ANCHORS = ("pr", "file", "line")

#: The two stage names #116 and #118 contribute that are NOT dimension slugs --
#: matches the literal names already used elsewhere in this codebase (see
#: test_run_adjudication.py's ``["preflight", "adjudication"]``). Every other
#: manifest entry is presumed to be a dimension slug, checked against
#: ``reports[].dimension`` for condition (7) below -- #117 discovers dimension
#: slugs from disk at runtime, so no fixed dimension list exists to import here.
_NON_DIMENSION_STAGE_NAMES = ("preflight", "adjudication")

#: #117's dimension completion marker, per STEP 5's condition (5): the primary
#: check is the parsed nonce against the document's own ``nonce`` argument, not
#: sibling-to-sibling agreement, because one report is enough to check that way.
_DIMENSION_MARKER_PREFIX = "BUZZ-DIMENSION-COMPLETE"


def _parse_dimension_marker(marker) -> tuple[str, str] | None:
    if not isinstance(marker, str):
        return None
    parts = marker.split(":")
    if len(parts) != 3 or parts[0] != _DIMENSION_MARKER_PREFIX:
        return None
    return parts[1], parts[2]


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


def _reported_dimension_names(reports) -> set:
    """Dimensions that actually produced a report.

    `stages` is the EXPECTED set -- what the run dispatched -- and is what
    condition (7) compares against to ask whether a named dimension failed to
    report at all. The clean-case sentence needs the opposite: what ACTUALLY
    ran. Deriving it from `stages` is wrong in both directions, which is why
    this reads `reports` and not the manifest:

    * before launchpad-26/buzz#565, `stages` carried no dimension entry at all
      (only `adjudication`, from `run_adjudication.py`), so the sentence would
      render "0 dimension(s): none" after real dimensions ran clean;
    * after #565, `stages` names every DISPATCHED dimension, so the sentence
      would credit a dimension that died before producing anything as having
      run clean.

    Both are the "silence reads as a crashed agent" failure this sentence
    exists to prevent, arriving through the wrong source. Stated as a pair
    deliberately: the earlier wording justified this function with the
    pre-#565 fact alone, which made a correct function look like it depended
    on a fact that has since stopped being true, and invited condition (7) to
    be read as dead code.
    """
    return {
        r.get("dimension")
        for r in (reports if isinstance(reports, list) else [])
        if isinstance(r, dict) and r.get("dimension") is not None
    }


def _dimension_stage_names(stages) -> set:
    stage_list = stages if isinstance(stages, list) else []
    return {
        s.get("name")
        for s in stage_list
        if isinstance(s, dict) and s.get("name") not in _NON_DIMENSION_STAGE_NAMES
    }


def _containment_unparseable(containment) -> bool:
    if not isinstance(containment, dict):
        return True
    findings = containment.get("findings")
    if not isinstance(findings, list):
        return True
    for f in findings:
        if not isinstance(f, dict) or not all(k in f for k in ("kind", "entry_point", "evidence")):
            return True
    return not isinstance(containment.get("states"), dict)


def _incomplete_reasons(
    stages, reports, containment, nonce, all_findings: list[dict], reviewer=None
) -> list[str]:
    """Eleven named conditions plus two inherited from STEP 4. The default is
    incomplete: anything this function cannot classify is added as a reason
    rather than silently passed over, per STEP 5's own rule that absence of a
    failure signal is not evidence of success.
    """
    reasons: list[str] = []

    # (11) The document says which reviewer produced it, and the stub produces
    # `{"outcome": "clean", "findings": []}` for every dimension without reading
    # anything. An independent review panel found the publish workflow running
    # exactly that and publishing "No confirmed findings" as though a review had
    # happened -- a false clean is worse than no review, because it is indexed,
    # durable, and looks like a pass. Absent is treated the same as stub, per the
    # default-is-incomplete rule: a document that will not say what reviewed it
    # has not established that anything did.
    if not isinstance(reviewer, dict):
        reasons.append(
            "the document does not record which reviewer produced it, so no "
            "dimension is established to have been reviewed"
        )
    elif reviewer.get("kind") != "injected":
        reasons.append(
            f"no dimension was actually reviewed: the pipeline ran the "
            f"{reviewer.get('name', 'stub')!r} stub reviewer, which reports every "
            "dimension clean without reading it (a real dimension reviewer is #116)"
        )

    if not isinstance(stages, list):
        # A missing or malformed manifest is not "no dimensions expected" --
        # that silent default is exactly how an absent stages key would
        # otherwise render as COMPLETE with nothing to say about it. The
        # real pipeline (run_adjudication.py) always emits a list, so this
        # guards a hand-built or malformed document, not the normal path.
        reasons.append(f"stages manifest is missing or not a list (got {type(stages).__name__})")

    stage_list = stages if isinstance(stages, list) else []
    dimension_stage_names = _dimension_stage_names(stages)
    for stage in stage_list:
        if not isinstance(stage, dict):
            reasons.append("a stage manifest entry could not be parsed")
            continue
        name = stage.get("name")
        status = stage.get("status")
        if status != "complete":  # (1)
            reason = stage.get("reason")
            detail = f", reason: {reason!r}" if reason else ""
            reasons.append(f"stage {name!r} has not completed (status: {status!r}{detail})")

    report_list = reports if isinstance(reports, list) else []
    parsed_nonces: list[tuple[str, str]] = []
    reported_dimensions = set()
    for report in report_list:
        if not isinstance(report, dict):
            reasons.append("a report could not be parsed")  # default-incomplete
            continue
        dimension = report.get("dimension")
        reported_dimensions.add(dimension)
        status = report.get("status")
        if status == "failed":  # (2)
            reasons.append(f"dimension {dimension!r} reported status: failed")
        if status == "complete" and report.get("outcome") is None:  # (8)
            reasons.append(f"dimension {dimension!r} has status: complete but no outcome")

        keys = list(report.keys())
        if "completion_marker" not in report or not keys or keys[-1] != "completion_marker":
            reasons.append(  # (3)
                f"dimension {dimension!r}'s completion_marker is absent or not the last key"
            )
        else:
            parsed = _parse_dimension_marker(report["completion_marker"])
            if parsed is None or parsed[0] != dimension:  # (4)
                reasons.append(
                    f"dimension {dimension!r}'s completion marker names a different dimension"
                )
            else:
                parsed_nonces.append((dimension, parsed[1]))
                if parsed[1] != nonce:  # (5), primary: against the document's nonce
                    reasons.append(
                        f"dimension {dimension!r}'s completion marker nonce does not match "
                        "the run nonce"
                    )

        findings = report.get("findings")
        findings_count = report.get("findings_count")
        if not isinstance(findings, list) or findings_count != len(findings):  # (6)
            reasons.append(f"dimension {dimension!r}'s findings_count does not match its findings")

    if len({n for _, n in parsed_nonces}) > 1:  # (5), secondary: siblings disagree
        reasons.append("reports' completion-marker nonces disagree with each other")

    missing_dimensions = dimension_stage_names - reported_dimensions
    for name in sorted(missing_dimensions, key=lambda n: (n is None, n)):  # (7)
        reasons.append(f"dimension {name!r} is named by the manifest but produced no report")

    if containment is None or _containment_unparseable(containment):  # (9), STEP 4 inherited
        reasons.append("the containment block is absent or unparseable")
    else:
        states = containment.get("states", {})
        actual = set(states)
        expected = set(contain.ENTRY_POINTS)
        if actual != expected:  # (10)
            missing = expected - actual
            extra = actual - expected
            detail = []
            if missing:
                detail.append(f"missing {sorted(missing)}")
            if extra:
                detail.append(f"unexpected {sorted(extra)}")
            reasons.append(
                "containment.states does not name exactly the seven entry points ("
                + "; ".join(detail) + ")"
            )

    for finding in all_findings:  # STEP 4 inherited: out-of-ladder severity
        if finding.get("severity") not in review.SEVERITY_ORDER:
            reasons.append(
                f"finding {finding.get('finding_id')!r} has a severity outside the ladder"
            )

    return reasons


def _render_incomplete_banner(reasons: list[str]) -> str:
    lines = [
        INCOMPLETE_HEADING,
        "",
        "This review is INCOMPLETE and must not be read as a full pass:",
        "",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.append("")
    return "\n".join(lines)


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
    stages: list[dict],
    containment: dict | None,
    head_sha: str,
    merge_base_sha: str,
    duplicate_groups=(),
    nonce=None,
    reviewer=None,
) -> str:
    """The full review body.

    ``nonce`` is the merged document's run nonce (#117), added here rather than
    at STEP 4 because STEP 5's condition (5) is the first thing that needs it --
    defaulted to ``None`` so STEP 4's own tests, which never supplied one, are
    unaffected; a missing document nonce still fails condition (5) honestly for
    any report that carries a completion marker, per the default-is-incomplete
    rule below.
    """
    all_findings: list[dict] = []
    for report in reports if isinstance(reports, list) else []:
        for finding in (report.get("findings", []) or []) if isinstance(report, dict) else []:
            all_findings.append(dict(finding))
    by_id = {f.get("finding_id"): f for f in all_findings if f.get("finding_id") is not None}

    lines = [
        marker,
        "",
        f"Reviewed commit `{head_sha}` against merge base `{merge_base_sha}`.",
        "",
    ]

    reasons = _incomplete_reasons(stages, reports, containment, nonce, all_findings, reviewer)
    if reasons:
        lines.append(_render_incomplete_banner(reasons))

    if containment is not None and not _containment_unparseable(containment):
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

    if not reasons and not ordered:
        # Silence is indistinguishable from a crashed agent -- this path posts
        # explicitly, on the same code path as the findings path, rather than
        # rendering nothing. Not the same input as "incomplete with zero
        # findings": the banner above already covers that case and this
        # sentence is skipped when it fired.
        reported_names = _reported_dimension_names(reports)
        names = ", ".join(sorted(reported_names)) if reported_names else "none"
        lines.append(
            f"No confirmed findings were produced across "
            f"{len(reported_names)} dimension(s): {names}."
        )
        lines.append("")

    return "\n".join(lines)

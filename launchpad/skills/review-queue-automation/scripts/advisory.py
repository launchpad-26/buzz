"""Advisory review output for review-queue-automation.

Advisory mode is the default and the primary product: a review comment carrying
what the panel established, what it could not, and which findings are corroborated
enough to act on. Without this the pipeline runs, spends model tokens, reaches a
decision, and leaves nothing visible on the pull request.

Rules:
- The event is always COMMENT. Approval and change-requests are separate, gated
  actions; nothing here can escalate into one.
- Corroborated and uncorroborated findings are reported in SEPARATE sections and
  never merged. An uncorroborated finding is presented as unconfirmed, because
  presenting it as a defect is how automated review loses a reader's trust.
- The body states the assurance actually achieved and the routes that ran, so a
  reader can weigh the review rather than assume it was thorough.
- Posting is idempotent per job: `github_mutate.post` keys the mutation on
  job + operation, so re-dispatching the same revision does not duplicate.
"""

from __future__ import annotations

from typing import Any

MAX_FINDINGS_SHOWN = 20
MAX_BODY = 60000  # comfortably inside GitHub's comment limit


def _fmt_finding(item: dict[str, Any]) -> list[str]:
    severity = item.get("severity", "?")
    location = item.get("location", "?")
    title = item.get("title") or "(untitled)"
    lines = [f"- **{severity}** `{location}` — {title}"]
    evidence = item.get("evidence")
    if evidence:
        lines.append(f"  - evidence: {evidence}")
    source = item.get("primary_source")
    if source:
        lines.append(f"  - primary source: {source}")
    basis = item.get("basis")
    if basis == "two_provider_families":
        lines.append("  - corroboration: independently reported by two provider families")
    elif basis == "check_failure_corroborated":
        citation = item.get("citation") or "a failing check"
        lines.append(f"  - corroboration: cited failing check `{citation}`")
    return lines


def build_body(
    *,
    repo: str,
    number: int,
    head_sha: str,
    disposition: str,
    verified: list[dict[str, Any]],
    unverified: list[dict[str, Any]],
    routes: list[dict[str, Any]] | None = None,
    assurance: dict[str, Any] | None = None,
    activities: list[str] | None = None,
    failed_gates: list[str] | None = None,
    snapshot_hash: str = "",
) -> str:
    """Render the advisory comment. Deterministic for a given input."""
    lines = [
        "## Automated review",
        "",
        f"Reviewed `{head_sha[:12]}` of {repo}#{number}. This is advisory output: "
        "it approves nothing and requests no changes.",
        "",
    ]

    if verified:
        lines.append(f"### Corroborated findings ({len(verified)})")
        lines.append("")
        for item in verified[:MAX_FINDINGS_SHOWN]:
            lines.extend(_fmt_finding(item))
        if len(verified) > MAX_FINDINGS_SHOWN:
            lines.append(f"- …and {len(verified) - MAX_FINDINGS_SHOWN} more")
        lines.append("")
    else:
        lines.extend(["### Corroborated findings", "",
                      "None. No finding met the corroboration bar.", ""])

    if unverified:
        lines.extend([
            f"### Unconfirmed observations ({len(unverified)})",
            "",
            "Reported by a single provider family without a reproducing check. "
            "Treat these as leads, not defects.",
            "",
        ])
        for item in unverified[:MAX_FINDINGS_SHOWN]:
            lines.extend(_fmt_finding(item))
        if len(unverified) > MAX_FINDINGS_SHOWN:
            lines.append(f"- …and {len(unverified) - MAX_FINDINGS_SHOWN} more")
        lines.append("")

    lines.extend(["### How this review was produced", ""])
    if activities:
        lines.append(f"- Angles covered: {', '.join(activities)}")
    for route in routes or []:
        if not isinstance(route, dict):
            continue
        enforced = route.get("effort_enforced")
        note = "" if enforced in (None, True) else " (effort not enforceable by this transport)"
        lines.append(
            f"- Reviewer: `{route.get('runner', '?')}:{route.get('selector', '?')}` "
            f"at effort {route.get('effort', '?')}{note}"
        )
    if assurance:
        lines.append(
            f"- Assurance: required {assurance.get('required_assurance', '?')}, "
            f"achieved {assurance.get('achieved_assurance', '?')} "
            f"(met: {assurance.get('assurance_met', '?')})"
        )
    lines.append(f"- Outcome: `{disposition}`")
    if failed_gates:
        lines.append(f"- Unmet gates: {', '.join(str(g) for g in failed_gates[:8])}")
    if snapshot_hash:
        lines.append(f"- Policy snapshot: `{snapshot_hash[:12]}`")

    lines.extend([
        "",
        "_A human decides. Corroboration means two independent provider families "
        "agreed, or one cited a check that actually failed._",
    ])

    body = "\n".join(lines)
    if len(body) > MAX_BODY:
        body = body[:MAX_BODY - 40].rstrip() + "\n\n_…truncated._"
    return body


def post_advisory(
    state,
    *,
    local_cfg: dict[str, Any],
    repo: str,
    number: int,
    job_id: str,
    pr_node_id: str,
    body: str,
    login: str = "",
    head_sha: str = "",
    _execute=None,
    _reviews_provider=None,
) -> dict[str, Any]:
    """Post the advisory COMMENT review. Never raises.

    Returns a record describing what happened, so a withheld or failed comment is
    visible in the job result rather than silently absent.
    """
    from authority import mode_for

    mode = mode_for(local_cfg, repo, "comment")
    if mode != "live":
        return {"posted": False, "reason": f"comment authority is {mode}", "mode": mode}
    if not pr_node_id:
        return {"posted": False, "reason": "no cached PR node_id", "mode": mode}

    execute = _execute
    if execute is None:
        from github_mutate import execute_comment_review as execute

    reviews_provider = _reviews_provider
    if reviews_provider is None and login and head_sha:
        try:
            from github_rest import RestReader

            reader = RestReader(local_cfg, state)
            reviews_provider = lambda: reader.pr_reviews(repo, number)  # noqa: E731
        except Exception:
            reviews_provider = None

    try:
        execute(
            state,
            {"pullRequestId": pr_node_id, "body": body},
            job_id,
            rest_probe=reviews_provider,
            login=login or None,
            head_sha=head_sha or None,
        )
    except Exception as exc:
        return {"posted": False, "reason": f"comment failed: {str(exc)[:200]}", "mode": mode}
    return {"posted": True, "mode": mode, "body_chars": len(body)}

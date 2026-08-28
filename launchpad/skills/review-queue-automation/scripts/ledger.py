"""Durable evidence and findings ledger for review-queue-automation.

One append-only record per PR revision answering a single question: WHY did this
job reach the outcome it did? It exists so a reviewer can reconstruct a decision
without re-reading raw model output — and so a failure in shadow mode is
diagnosable rather than a mystery.

Every entry is bound to `repo + number + head_sha + job_id`, so nothing carries
across revisions. Entries are append-only: a correction is a new entry, never an
edit, because an audit trail that can be rewritten is not an audit trail.

Recorded kinds:

    strategy   a strategy was required / attempted / completed, and by which route
    route      which model route executed, and whether effort was enforced
    evidence   what evidence was gathered, by reference (never its content)
    finding    a finding and its corroboration basis, by stable fingerprint
    assurance  required vs achieved assurance and the inputs behind it
    decision   the disposition and which gates failed
    action     what was attempted against GitHub and whether it was verified
    human      a human request or decision

Redaction: payloads pass through the same sanitiser the JSONL logger uses, so no
tokens, PR bodies, or nonce-enveloped evidence can land in the ledger.
"""

from __future__ import annotations

import json
from typing import Any

from common import utcnow
from logging_otel import sanitize_value

STRATEGY = "strategy"
ROUTE = "route"
EVIDENCE = "evidence"
FINDING = "finding"
ASSURANCE = "assurance"
DECISION = "decision"
ACTION = "action"
HUMAN = "human"

KINDS = (STRATEGY, ROUTE, EVIDENCE, FINDING, ASSURANCE, DECISION, ACTION, HUMAN)


class LedgerError(ValueError):
    """Raised when an entry is not recordable (unknown kind, missing identity)."""


def record(
    state,
    *,
    job_id: str,
    repo: str,
    number: int,
    head_sha: str,
    kind: str,
    payload: dict[str, Any],
    entry_key: str = "",
    snapshot_hash: str = "",
    policy_version: str = "",
) -> int:
    """Append one ledger entry. Returns its row id.

    Identity is mandatory: an entry that cannot be attributed to an exact PR
    revision is worse than no entry, because it would appear to explain a decision
    it may not belong to.
    """
    if kind not in KINDS:
        raise LedgerError(f"unknown ledger kind {kind!r} (expected one of {', '.join(KINDS)})")
    if not (job_id and repo and head_sha):
        raise LedgerError("ledger entries require job_id, repo and head_sha")

    safe = {k: sanitize_value(v) for k, v in (payload or {}).items()}
    cursor = state.execute(
        "INSERT INTO ledger_entries(job_id,repo,number,head_sha,recorded_at,kind,"
        "entry_key,payload,snapshot_hash,policy_version) VALUES(?,?,?,?,?,?,?,?,?,?)",
        (job_id, repo, int(number), head_sha, utcnow(), kind, entry_key,
         json.dumps(safe, sort_keys=True), snapshot_hash, policy_version),
    )
    state.db.commit()
    return int(cursor.lastrowid)


def entries(state, job_id: str, *, kind: str | None = None) -> list[dict[str, Any]]:
    """All entries for a job in the order they were recorded."""
    sql = ("SELECT id,job_id,repo,number,head_sha,recorded_at,kind,entry_key,payload,"
           "snapshot_hash,policy_version FROM ledger_entries WHERE job_id=?")
    params: tuple[Any, ...] = (job_id,)
    if kind:
        sql += " AND kind=?"
        params = (job_id, kind)
    sql += " ORDER BY id"
    out: list[dict[str, Any]] = []
    for row in state.db.execute(sql, params).fetchall():
        item = dict(row)
        try:
            item["payload"] = json.loads(item["payload"])
        except (ValueError, TypeError):
            item["payload"] = {"unparseable": True}
        out.append(item)
    return out


def revisions(state, repo: str, number: int) -> list[dict[str, Any]]:
    """Every reviewed revision of a PR, newest last, with its entry count.

    Makes re-review history explicit: each head is a separate row, so nothing
    silently carries between revisions.
    """
    rows = state.db.execute(
        "SELECT head_sha, job_id, COUNT(*) AS entry_count, MIN(recorded_at) AS first_seen, "
        "MAX(recorded_at) AS last_seen FROM ledger_entries WHERE repo=? AND number=? "
        "GROUP BY head_sha, job_id ORDER BY first_seen",
        (repo, int(number)),
    ).fetchall()
    return [dict(r) for r in rows]


def explain(state, job_id: str) -> dict[str, Any]:
    """Reconstruct why a job reached its outcome, from the ledger alone."""
    items = entries(state, job_id)
    if not items:
        return {"job": job_id, "explained": False,
                "reason": "no ledger entries recorded for this job"}

    first = items[0]
    by_kind: dict[str, list[dict[str, Any]]] = {kind: [] for kind in KINDS}
    for item in items:
        by_kind[item["kind"]].append(item)

    decisions = by_kind[DECISION]
    actions = by_kind[ACTION]
    findings = by_kind[FINDING]

    return {
        "job": job_id,
        "explained": True,
        "repo": first["repo"],
        "pull_request": first["number"],
        "head_sha": first["head_sha"],
        "snapshot_hash": first.get("snapshot_hash") or "",
        "policy_version": first.get("policy_version") or "",
        "entry_count": len(items),
        "strategies": [i["payload"] for i in by_kind[STRATEGY]],
        "routes": [i["payload"] for i in by_kind[ROUTE]],
        "evidence": [i["payload"] for i in by_kind[EVIDENCE]],
        "findings": [i["payload"] for i in findings],
        "verified_findings": [
            i["payload"] for i in findings if i["payload"].get("verified") is True
        ],
        "assurance": [i["payload"] for i in by_kind[ASSURANCE]],
        "human": [i["payload"] for i in by_kind[HUMAN]],
        "decisions": [i["payload"] for i in decisions],
        "actions": [i["payload"] for i in actions],
        "final_decision": decisions[-1]["payload"] if decisions else None,
        "final_action": actions[-1]["payload"] if actions else None,
        "timeline": [
            {"at": i["recorded_at"], "kind": i["kind"], "key": i["entry_key"]}
            for i in items
        ],
    }


def render_explanation(report: dict[str, Any]) -> str:
    """A compact 'why did this PR get this outcome?' block for an operator."""
    if not report.get("explained"):
        return f"{report.get('job', '?')}: {report.get('reason', 'nothing recorded')}\n"

    lines = [
        f"{report['repo']}#{report['pull_request']} @ {report['head_sha'][:12]}"
        f"  (job {report['job']})",
        f"  snapshot {report['snapshot_hash'][:12] or '<none>'}"
        f"  policy {report['policy_version'] or '<none>'}",
    ]

    strategies = report.get("strategies") or []
    if strategies:
        names = ", ".join(
            str(s.get("name", "?")) for s in strategies if isinstance(s, dict)
        )
        lines.append(f"  strategies: {names}")

    routes = report.get("routes") or []
    for route in routes:
        if not isinstance(route, dict):
            continue
        enforced = route.get("effort_enforced")
        note = "" if enforced in (None, True) else "  [effort NOT enforced]"
        lines.append(
            f"  route: {route.get('runner', '?')}:{route.get('selector', '?')}"
            f" effort={route.get('effort', '?')}{note}"
        )

    assurance = report.get("assurance") or []
    if assurance:
        last = assurance[-1]
        lines.append(
            f"  assurance: required={last.get('required_assurance', '?')}"
            f" achieved={last.get('achieved_assurance', '?')}"
            f" met={last.get('assurance_met', '?')}"
        )

    verified = report.get("verified_findings") or []
    unverified = [f for f in (report.get("findings") or [])
                  if isinstance(f, dict) and f.get("verified") is False]
    if verified or unverified:
        lines.append(f"  findings: {len(verified)} verified, {len(unverified)} unverified")
        for finding in verified:
            lines.append(
                f"    - {finding.get('severity', '?')} {finding.get('location', '?')}"
                f"  basis={finding.get('basis', '?')}"
            )

    final_decision = report.get("final_decision")
    if isinstance(final_decision, dict):
        failed = final_decision.get("failed_gates") or []
        lines.append(f"  decision: {final_decision.get('disposition', '?')}")
        if failed:
            shown = ", ".join(str(g) for g in list(failed)[:6])
            lines.append(f"    failed gates: {shown}")

    final_action = report.get("final_action")
    if isinstance(final_action, dict):
        lines.append(
            f"  action: {final_action.get('operation', '?')}"
            f" -> {final_action.get('outcome', '?')}"
            f" verified={final_action.get('verified', '?')}"
        )

    for human in report.get("human") or []:
        if isinstance(human, dict):
            lines.append(
                f"  human: {human.get('event', '?')}"
                f" actor={human.get('actor', '-')}"
                f" decision={human.get('decision', '-')}"
            )

    return "\n".join(lines) + "\n"

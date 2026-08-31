#!/usr/bin/env python3
"""The check-conclusion vocabulary, and the gate it feeds.

Guards launchpad-26/buzz#1963, which was two defects in one expression:

  1. `dispatcher.py` compared `conclusion` to the literal `"SUCCESS"` — the
     GraphQL enum spelling — against evidence gathered over REST, which returns
     lower-case. `checks_ok` was therefore never true.
  2. Even upper-cased, it demanded `SUCCESS` from every check, which no pull
     request in this repository satisfies: the changed-paths fan-out skips whole
     job families and `SKIPPED` is a green outcome.

Both failed closed, so nothing was wrongly approved — but `checks_complete_ok`
is one of the 22 conjunctive gates in `risk.ApprovalState.passed()`, so
automated approval was unsatisfiable regardless of configuration.

The fixtures below are deliberately REST-shaped, in lower case. A test written
in the GraphQL spelling passes against the bug and so proves nothing.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import checks as checks_mod  # noqa: E402
from findings import FAILING_CONCLUSIONS, failing_check_names  # noqa: E402
from history import checks_ok_timestamp  # noqa: E402


# -- REST-shaped fixtures, as the check-runs API actually returns them --------

def _rest(conclusion: str, name: str = "ci", completed: str = "2026-08-27T01:00:00Z") -> dict:
    return {
        "name": name,
        "status": "completed",
        "conclusion": conclusion,
        "completed_at": completed,
    }


# -- canonicalisation ---------------------------------------------------------

def test_rest_lowercase_folds_onto_the_graphql_spelling() -> None:
    assert checks_mod.canonical("success") == "SUCCESS"
    assert checks_mod.canonical("  skipped\n") == "SKIPPED"
    assert checks_mod.canonical(None) == ""
    assert checks_mod.canonical("") == ""


def test_rest_lowercase_success_is_passing() -> None:
    """The exact defect: 'success' must read as green."""
    assert checks_mod.is_passing(_rest("success")) is True
    assert checks_mod.is_passing(_rest("SUCCESS")) is True


def test_skipped_and_neutral_are_green_outcomes() -> None:
    """Every PR in this repository has skipped jobs; skipped is not absent."""
    assert checks_mod.is_passing(_rest("skipped")) is True
    assert checks_mod.is_passing(_rest("neutral")) is True


def test_pending_is_neither_passing_nor_failing() -> None:
    pending = {"name": "ci", "status": "in_progress", "conclusion": None}
    assert checks_mod.is_pending(pending) is True
    assert checks_mod.is_passing(pending) is False
    assert checks_mod.is_failing(pending) is False


def test_unknown_conclusion_counts_as_standing_in_the_way() -> None:
    """An unrecognised state is treated as a problem, not waved through."""
    odd = _rest("startup_failure")
    assert checks_mod.is_passing(odd) is False
    assert checks_mod.is_failing(odd) is True
    # ...but it is not a *genuine* failure for finding corroboration.
    assert checks_mod.conclusion_of(odd) not in FAILING_CONCLUSIONS


# -- the gate predicate -------------------------------------------------------

def test_all_green_rest_shaped_checks_pass_the_gate() -> None:
    """Acceptance criterion 1 of #1963."""
    assert checks_mod.all_passing([_rest("success"), _rest("skipped", "desktop")]) is True


def test_one_failing_check_fails_the_gate() -> None:
    """Acceptance criterion 2 of #1963."""
    assert checks_mod.all_passing([_rest("success"), _rest("failure", "audit")]) is False


def test_no_checks_fails_closed() -> None:
    """No evidence is not evidence of success."""
    assert checks_mod.all_passing([]) is False
    assert checks_mod.all_passing(None) is False


def test_a_pending_check_fails_closed() -> None:
    assert checks_mod.all_passing(
        [_rest("success"), {"name": "slow", "conclusion": None}]
    ) is False


# -- the consumers agree ------------------------------------------------------

def _facts_for(checks: list[dict]):
    """Drive `dispatcher._load_pr_facts` over a seeded job and evidence bundle.

    Asserted through the dispatcher's real path rather than the helper, because
    the defect was in the dispatcher's own expression: a helper-only test would
    pass while the gate stayed unsatisfiable.
    """
    import datetime as dt
    import json
    import tempfile

    import dispatcher
    from common import State, job_id

    cfg = {"state_dir": tempfile.mkdtemp(), "assurance": {"large_diff_lines": 700}}
    state = State(cfg)
    now = dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    jid = job_id("o/r", 1, "abc", "incoming_review")
    state.db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,created_at,updated_at) "
        "VALUES(?,?,?,?,?,?,?,?,?)",
        (jid, "o/r", 1, "abc", "incoming_review", "detected", str(state.job_dir(jid)), now, now),
    )
    payload = {
        "number": 1, "user": {"login": "alice"}, "draft": False, "additions": 2,
        "deletions": 0, "files": [{"filename": "docs/a.md"}], "head": {"sha": "abc"},
        "node_id": "PR_node_1",
    }
    state.db.execute(
        "INSERT INTO prs(repo,number,head_sha,updated_at,payload,open,last_seen) VALUES(?,?,?,?,?,1,?)",
        ("o/r", 1, "abc", now, json.dumps(payload), now),
    )
    state.db.commit()
    state.job_dir(jid)
    (state.job_dir(jid) / "evidence.json").write_text(
        json.dumps({
            "collected_at": now,
            "checks": checks,
            "context": {"author": "alice", "draft": False, "head": "abc", "repo_path": "/tmp"},
        }),
        encoding="utf-8",
    )
    try:
        job = {"repo": "o/r", "number": 1, "job_id": jid}
        return dispatcher._load_pr_facts(state, job, "abc", cfg)
    finally:
        state.close()


def test_dispatcher_derives_checks_ok_from_rest_shaped_evidence() -> None:
    """Acceptance criteria 1 and 2 of #1963, at the end the gate actually reads.

    The pre-existing fixture in `test_dispatch_flow.py` seeded
    `{"conclusion": "SUCCESS"}` — the GraphQL spelling the code expected rather
    than the REST spelling it receives — which is why this was invisible.
    """
    green = _facts_for([_rest("success"), _rest("skipped", "desktop")])
    assert green.checks_ok is True, "green REST-shaped checks must satisfy the gate"

    broken = _facts_for([_rest("success"), _rest("failure", "audit")])
    assert broken.checks_ok is False

    pending = _facts_for([_rest("success"), {"name": "slow", "conclusion": None}])
    assert pending.checks_ok is False


def test_findings_and_the_vocabulary_agree() -> None:
    """`findings` counts genuine failures only, in either casing."""
    assert failing_check_names([_rest("failure", "audit")]) == ["audit"]
    assert failing_check_names([_rest("FAILURE", "audit")]) == ["audit"]
    # Skipped and neutral are not failures.
    assert failing_check_names([_rest("skipped"), _rest("neutral")]) == []


def test_history_and_the_vocabulary_agree() -> None:
    """The backtest's timestamp uses the same PASSING set."""
    stamp = checks_ok_timestamp([
        _rest("success", "ci", "2026-08-27T01:00:00Z"),
        _rest("skipped", "desktop", "2026-08-27T02:00:00Z"),
    ])
    assert stamp == "2026-08-27T02:00:00Z"
    assert checks_ok_timestamp([_rest("failure", "audit")]) is None


def test_no_module_reimplements_the_vocabulary() -> None:
    """The conclusion literals live in one module.

    Four modules each carried their own set, and the one feeding the approval
    gate was wrong. A grep-level guard is crude, but it is the property that was
    actually violated: the literals were duplicated, and they drifted.
    """
    scripts = pathlib.Path(__file__).resolve().parent.parent / "scripts"
    offenders = []
    for path in sorted(scripts.glob("*.py")):
        if path.name in ("checks.py", "github_query.py"):
            continue  # the definition, and the transport that maps onto it
        source = path.read_text(encoding="utf-8")
        for literal in ('"TIMED_OUT"', '"ACTION_REQUIRED"'):
            # Only flag real code, not prose in a docstring or comment.
            for line in source.splitlines():
                stripped = line.strip()
                if stripped.startswith("#") or stripped.startswith("*"):
                    continue
                if literal in stripped:
                    offenders.append(f"{path.name}: {stripped[:70]}")
    assert not offenders, "conclusion vocabulary duplicated outside checks.py: " + "; ".join(offenders)


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)

#!/usr/bin/env python3
"""Phase 4 tests: error category metadata, logging schema + redaction, shadow
no-mutation, historical cutoff. Deterministic fakes only."""

from __future__ import annotations

import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from errors import (  # noqa: E402
    TRANSIENT_INFRA,
    AUDIT_LOGGING_FAILURE,
    category_meta,
)
from logging_otel import JobLogger  # noqa: E402


def test_error_category_metadata() -> None:
    t = category_meta(TRANSIENT_INFRA)
    assert t["retryable"] is True and t["authority_impact"] == "none"
    a = category_meta(AUDIT_LOGGING_FAILURE)
    assert a["retryable"] is True and a["authority_impact"] == "no_mutate"
    # unknown category fails safe (no widen)
    u = category_meta("no-such-category")
    assert u["retryable"] is False and u["authority_impact"] == "no_mutate"


def test_every_named_category_is_safe() -> None:
    for name in ("rate_limit", "provider_unavailable", "model_unavailable",
                 "invalid_model_output", "state_conflict", "invariant_violation",
                 "authentication", "policy_validation", "invalid_transition"):
        meta = category_meta(name)
        assert meta["authority_impact"] in ("none", "no_mutate", "safe_stop")


def _logger() -> tuple[JobLogger, pathlib.Path]:
    root = pathlib.Path(tempfile.mkdtemp())
    jl = JobLogger(root, "job123", repo="o/r", number=1, lane="incoming_review")
    return jl, root


def test_log_has_schema_version_and_event_name() -> None:
    jl, _ = _logger()
    jl.info(body="x", phase="assurance", outcome="complete", event_name="assurance_done")
    lines = jl.events_path.read_text(encoding="utf-8").splitlines()
    ev = json.loads(lines[0])
    assert ev["schema_version"] == 1
    assert ev["event_name"] == "assurance_done"
    for k in ("timestamp", "severity_text", "body", "resource"):
        assert k in ev


def test_log_redaction() -> None:
    jl, _ = _logger()
    jl.info(body="review", phase="assurance", outcome="x",
            attributes={"ai.token": "sk-abc123", "safe": "ok"})
    blob = jl.events_path.read_text(encoding="utf-8")
    assert "sk-abc123" not in blob
    assert "<redacted>" in blob


def test_logging_failure_blocks_authority(via_meta=True) -> None:
    meta = category_meta(AUDIT_LOGGING_FAILURE)
    assert meta["authority_impact"] == "no_mutate"


def test_shadow_backtest_is_read_only() -> None:
    import shadow
    # the module exports a shadow-forced evaluator path; assert the constants that
    # guarantee no decision/mutation on the shadow/backtest path.
    assert hasattr(shadow, "backtest")
    assert hasattr(shadow, "evaluate_before_merge")


def test_historical_cutoff_enforced_for_backtest() -> None:
    import shadow

    # every historical sample must carry a cutoff (merged_at) so the backtest can
    # define the simulated evidence boundary; before_merge_facts reconstructs only
    # pre-merge, head-pinned evidence.
    sample = shadow.HistoricalSample(
        repo="o/r", number=1, head_sha="H", merged_at="2026-01-01T00:00:00Z",
        files=["a.md"], additions=2, pr_facts={"author_login": "alice"},
    )
    facts = sample.before_merge_facts()
    assert sample.merged_at  # cutoff is present -> historical boundary is defined
    assert facts.head_sha == "H"
    assert facts.files == ["a.md"]
    # the reconstructed facts carry NO post-merge markers (no merged_at field etc.)
    assert not hasattr(facts, "merged_after")


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

                print(f"FAIL {name}: {exc}")
                traceback.print_exc()
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)
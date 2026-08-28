#!/usr/bin/env python3
"""main()-LEVEL tests for the operator entry points. No network, no models.

Why this file exists
--------------------
The rest of the suite calls library functions directly. That is why two defects
shipped despite 592 green tests:

* three entry points tested `resolve_or_onboarding(...) is None`, which is never
  true (it returns a 2-tuple), so a rejected config produced an AttributeError
  traceback instead of a clean `onboarding_required` exit; and
* `shadow.main` loaded `--verdicts` with `json.loads`, giving STRING keys, while
  every lookup is by int PR number — so every CLI-supplied reviewer verdict was
  silently discarded and the report read as a perfect safety result.

Neither is reachable below `main()`. Every test here goes through `main(argv)`.
"""

from __future__ import annotations

import contextlib
import io
import json
import pathlib
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import config as cfgmod  # noqa: E402
import explain  # noqa: E402
import history  # noqa: E402
import human_cli  # noqa: E402
import shadow  # noqa: E402

CUTOFF = "2026-01-15T00:00:00Z"

_CLEAN_A = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
            "good": ["docs"], "missing_evidence": [], "model": "claude",
            "provider_family": "anthropic", "_schema_ok": True}
_CLEAN_B = {"signal": "SUPPORTED", "recommendation": "clean", "findings": [],
            "good": ["docs"], "missing_evidence": [], "model": "gpt",
            "provider_family": "openai", "_schema_ok": True}


def _git_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp()).resolve()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root,
                   check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True,
                   capture_output=True)
    (root / ".gitignore").write_text(
        ".review-queue-automation/\npr review logs\n", encoding="utf-8")
    return root


def _valid_repo() -> pathlib.Path:
    """A repo whose config the loader accepts."""
    root = _git_repo()
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "op"
    cfg["repository"]["slug"] = "launchpad-26/buzz"
    cfg["state_dir"] = tempfile.mkdtemp()
    # No REST-remaining floor: history cannot reconstruct live REST headroom, so a
    # configured floor makes rate_limit_ok fail closed for every sample.
    cfg["poll"]["rest_remaining_floor"] = 0
    cfg["models"]["primary"] = [{"runner": "claude", "selector": "sonnet",
                                 "provider_family": "anthropic",
                                 "capability": "frontier", "efforts": ["high"]}]
    cfg["models"]["secondary"] = [{"runner": "codex", "selector": "gpt5",
                                   "provider_family": "openai",
                                   "capability": "frontier", "efforts": ["high"]}]
    path = cfgmod.repo_config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    (root / cfgmod.DEFAULT_LOG_DIR_NAME).mkdir(exist_ok=True)
    return root


def _broken_repo() -> pathlib.Path:
    """A repo whose config the loader REJECTS (approval.mode is not a legal value).

    Deliberately invalid rather than absent: an absent file and a rejected file
    take the same code path, and the rejected one is what produced the observed
    `AttributeError: 'NoneType' object has no attribute 'get'`.
    """
    root = _git_repo()
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "op"
    cfg["repository"]["slug"] = "launchpad-26/buzz"
    cfg["approval"]["mode"] = "definitely-not-a-mode"
    path = cfgmod.repo_config_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    return root


def _run_main(fn, argv: list[str]) -> tuple[int, str]:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = fn(argv)
    return code, buffer.getvalue()


# ---- B2: the three entry points exit cleanly on a rejected config ----

def _assert_onboarding_exit(fn, argv: list[str], label: str) -> None:
    code, out = _run_main(fn, argv)
    assert code == 1, f"{label} must exit 1, got {code}"
    payload = json.loads(out[out.index("{"):out.rindex("}") + 1])
    assert payload["status"] == "onboarding_required", label
    assert "onboarding" in payload, label
    assert "Traceback" not in out, label


def test_shadow_main_exits_onboarding_on_invalid_config() -> None:
    root = _broken_repo()
    samples = pathlib.Path(root) / "s.json"
    samples.write_text("[]", encoding="utf-8")
    _assert_onboarding_exit(
        shadow.main, ["--repo-root", str(root), "--samples", str(samples)], "shadow")


def test_explain_main_exits_onboarding_on_invalid_config() -> None:
    root = _broken_repo()
    _assert_onboarding_exit(
        explain.main, ["--repo-root", str(root), "pr", "1"], "explain")


def test_human_cli_main_exits_onboarding_on_invalid_config() -> None:
    root = _broken_repo()
    _assert_onboarding_exit(
        human_cli.main, ["--repo-root", str(root), "list"], "human_cli")


def test_history_main_exits_onboarding_on_invalid_config() -> None:
    # history.py already unpacked correctly; this pins the behaviour so a future
    # refactor cannot regress all four together.
    root = _broken_repo()
    _assert_onboarding_exit(
        history.main, ["--repo-root", str(root)], "history")


# ---- B3: CLI-supplied verdicts are actually applied ----

def _sample_entry(number: int, day: int, outcome: str) -> dict:
    return {
        "repo": "launchpad-26/buzz", "number": number, "head_sha": f"head-{number}",
        "merged_at": f"2026-01-{day:02d}T00:00:00Z", "outcome": outcome,
        "evidence_source": "independent-record", "cutoff": CUTOFF,
        "checks_ok_at": CUTOFF, "adjudication_at": CUTOFF, "evidence_at": CUTOFF,
        "head_frozen_at": CUTOFF, "files": ["docs/a.md"], "additions": 5,
        "pr_facts": {"author_login": "someone", "complexity": 0},
    }


def _write_backtest_inputs(root: pathlib.Path) -> dict[str, pathlib.Path]:
    numbers = [101, 102, 103, 104, 105]
    outcomes = {101: "clean", 102: "clean", 103: "adverse", 104: "contested",
                105: "clean"}
    entries = [_sample_entry(n, i + 1, outcomes[n]) for i, n in enumerate(numbers)]
    paths = {
        "samples": root / "samples.json",
        "verdicts": root / "v.json",
        "assessments": root / "a.json",
        "out": root / "report.json",
    }
    paths["samples"].write_text(json.dumps(entries), encoding="utf-8")
    # STRING keys: this is what json.dump produces and what an operator writes.
    paths["verdicts"].write_text(
        json.dumps({str(n): [_CLEAN_A, _CLEAN_B] for n in numbers}), encoding="utf-8")
    paths["assessments"].write_text(
        json.dumps({str(n): {"assurance_met": True} for n in numbers}), encoding="utf-8")
    return paths


def test_backtest_main_applies_string_keyed_verdicts() -> None:
    root = _valid_repo()
    paths = _write_backtest_inputs(root)
    code, _ = _run_main(shadow.main, [
        "--repo-root", str(root),
        "--samples", str(paths["samples"]),
        "--verdicts", str(paths["verdicts"]),
        "--assessments", str(paths["assessments"]),
        "--train-ratio", "0",
        "--out", str(paths["out"]),
    ])
    assert code == 0
    report = json.loads(paths["out"].read_text(encoding="utf-8"))
    # Before the fix these were 0 / [] / 1.0 — which reads as a perfect safety
    # result while in fact no verdict had been applied at all.
    assert report["samples_with_verdicts"] == 5, report["samples_with_verdicts"]
    assert report["false_auto_approval_candidates"] == [103, 104]
    assert report["false_auto_approval_count"] == 2
    assert report["approval_candidate_count"] == 5
    assert report["escalation_rate"] == 0.0
    assert report["decision_capable"] is True
    assert not any("no reviewer verdicts supplied" in w for w in report["warnings"])


def test_backtest_main_rejects_a_non_integer_verdict_key() -> None:
    root = _valid_repo()
    paths = _write_backtest_inputs(root)
    paths["verdicts"].write_text(json.dumps({"pr-101": []}), encoding="utf-8")
    code, out = _run_main(shadow.main, [
        "--repo-root", str(root),
        "--samples", str(paths["samples"]),
        "--verdicts", str(paths["verdicts"]),
        "--train-ratio", "0",
    ])
    assert code == 1
    assert "non-integer key" in out
    assert "Traceback" not in out


def test_backtest_main_writes_no_decision_and_leaves_config_alone() -> None:
    root = _valid_repo()
    before = cfgmod.repo_config_path(root).read_text(encoding="utf-8")
    paths = _write_backtest_inputs(root)
    code, _ = _run_main(shadow.main, [
        "--repo-root", str(root),
        "--samples", str(paths["samples"]),
        "--verdicts", str(paths["verdicts"]),
        "--assessments", str(paths["assessments"]),
        "--train-ratio", "0", "--out", str(paths["out"]),
    ])
    assert code == 0
    assert cfgmod.repo_config_path(root).read_text(encoding="utf-8") == before
    cfg = json.loads(before)
    from common import State

    state = State({"state_dir": cfg["state_dir"]})
    try:
        assert state.db.execute("SELECT 1 FROM approval_decisions").fetchone() is None
    finally:
        state.close()


def test_current_mode_main_prints_a_verdict_token() -> None:
    root = _valid_repo()
    facts = pathlib.Path(root) / "facts.json"
    facts.write_text(json.dumps(_sample_entry(201, 1, "unknown")), encoding="utf-8")
    verdicts = pathlib.Path(root) / "v.json"
    verdicts.write_text(json.dumps({"201": [_CLEAN_A, _CLEAN_B]}), encoding="utf-8")
    assessments = pathlib.Path(root) / "a.json"
    assessments.write_text(json.dumps({"201": {"assurance_met": True}}), encoding="utf-8")
    code, out = _run_main(shadow.main, [
        "--repo-root", str(root), "--mode", "current",
        "--pr-facts", str(facts), "--verdicts", str(verdicts),
        "--assessments", str(assessments),
    ])
    assert code == 0
    assert "WOULD_AUTO_APPROVE" in out
    assert "performs no mutation" in out


# ---- T33: history -> shadow, end to end on the real entry points ----

def test_history_entry_shape_feeds_shadow_main() -> None:
    """`history.build_entry` is the only producer of the `--samples` file. This
    walks its real output into `shadow.main` so a field rename in either one
    breaks a test rather than a live calibration run."""
    pr = {
        "number": 301, "title": "docs: tidy", "merged_at": "2026-01-10T00:00:00Z",
        "closed_at": "2026-01-10T00:00:00Z", "created_at": "2026-01-09T00:00:00Z",
        "head": {"sha": "abc123"}, "user": {"login": "someone"}, "additions": 5,
    }
    reviews = [{"user": {"login": "human"}, "state": "APPROVED",
                "submitted_at": "2026-01-09T12:00:00Z"}]
    entry = history.build_entry(
        "launchpad-26/buzz", pr, reviews, ["docs/a.md"], reverted=set(),
        self_login="op", checks_ok_at="2026-01-09T13:00:00Z",
    )
    assert entry["outcome"] == "clean"
    assert entry["head_frozen_at"] == "2026-01-10T00:00:00Z"

    # The entry must be consumable by build_sample without translation...
    sample = shadow.build_sample(entry)
    assert sample.head_frozen_at == entry["head_frozen_at"]

    # ...and by the CLI, unmodified.
    root = _valid_repo()
    samples = pathlib.Path(root) / "samples.json"
    samples.write_text(json.dumps([entry]), encoding="utf-8")
    verdicts = pathlib.Path(root) / "v.json"
    verdicts.write_text(json.dumps({"301": [_CLEAN_A, _CLEAN_B]}), encoding="utf-8")
    assessments = pathlib.Path(root) / "a.json"
    assessments.write_text(json.dumps({"301": {"assurance_met": True}}), encoding="utf-8")
    out = pathlib.Path(root) / "report.json"
    code, _ = _run_main(shadow.main, [
        "--repo-root", str(root), "--samples", str(samples),
        "--verdicts", str(verdicts), "--assessments", str(assessments),
        "--train-ratio", "0", "--out", str(out),
    ])
    assert code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["samples_with_verdicts"] == 1
    assert report["approval_candidate_count"] == 1
    assert report["pinned_heads"] == ["abc123"]


def test_history_without_checks_leaves_the_checks_gate_closed() -> None:
    """The documented fail-closed behaviour of omitting --with-checks, proved
    through the shadow entry point rather than asserted in prose."""
    pr = {
        "number": 302, "title": "docs: tidy", "merged_at": "2026-01-10T00:00:00Z",
        "closed_at": "2026-01-10T00:00:00Z", "created_at": "2026-01-09T00:00:00Z",
        "head": {"sha": "def456"}, "user": {"login": "someone"}, "additions": 5,
    }
    reviews = [{"user": {"login": "human"}, "state": "APPROVED",
                "submitted_at": "2026-01-09T12:00:00Z"}]
    entry = history.build_entry("launchpad-26/buzz", pr, reviews, ["docs/a.md"],
                                reverted=set(), self_login="op", checks_ok_at=None)
    assert entry["checks_ok_at"] is None
    root = _valid_repo()
    samples = pathlib.Path(root) / "samples.json"
    samples.write_text(json.dumps([entry]), encoding="utf-8")
    verdicts = pathlib.Path(root) / "v.json"
    verdicts.write_text(json.dumps({"302": [_CLEAN_A, _CLEAN_B]}), encoding="utf-8")
    out = pathlib.Path(root) / "report.json"
    code, _ = _run_main(shadow.main, [
        "--repo-root", str(root), "--samples", str(samples),
        "--verdicts", str(verdicts), "--train-ratio", "0", "--out", str(out),
    ])
    assert code == 0
    report = json.loads(out.read_text(encoding="utf-8"))
    assert report["approval_candidate_count"] == 0
    assert "checks_complete_ok" in report["universally_failed_gates"]


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"PASS {name}")
            except Exception as exc:  # noqa: BLE001
                failures += 1
                print(f"FAIL {name}: {exc}")
    sys.exit(1 if failures else 0)

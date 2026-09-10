#!/usr/bin/env python3
"""Counterexample tests for migration: the state store and the config version.

An upgrade is where safety quietly disappears. The failure this file is written
against is not "migration crashes" — it is "migration succeeds and the guard it
was supposed to carry forward is now a no-op": a `jobs` table with no
`snapshot_hash` column makes snapshot pinning silently stop pinning, and an
unversioned config that resolves to `cfg-1` lets an edited config reuse an
in-flight job's pin.

So every test here asserts the migrated system still REFUSES something, or that
a pre-migration artifact is not silently promoted.

Sibling ownership: `common.py` and `config.py` belong to the runtime lane. These
counterexamples exercise them from a new file rather than editing
`test_snapshot_pinning.py` or `test_config_onboarding.py`.
"""

from __future__ import annotations

import json
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import config as cfgmod  # noqa: E402
import policy as policymod  # noqa: E402
import snapshot as snapmod  # noqa: E402
from common import State, utcnow  # noqa: E402
from errors import JobBlockingError, StatePersistenceError  # noqa: E402

#: The `jobs` table exactly as an earlier release created it — no
#: `snapshot_hash` column. Migration must add it; if it does not, pinning
#: degrades to nothing and no existing test notices.
_OLD_JOBS_DDL = """
CREATE TABLE jobs (
  id TEXT PRIMARY KEY,
  repo TEXT NOT NULL,
  number INTEGER NOT NULL,
  head_sha TEXT NOT NULL,
  lane TEXT NOT NULL,
  status TEXT NOT NULL,
  reason TEXT,
  assurance TEXT,
  artifact_dir TEXT NOT NULL,
  retries INTEGER NOT NULL DEFAULT 0,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  UNIQUE (repo, number, head_sha, lane)
);
"""


def _old_state_dir(status: str = "approval_evaluation") -> pathlib.Path:
    """A state directory written by a pre-`snapshot_hash` release, with one job."""
    root = pathlib.Path(tempfile.mkdtemp())
    (root / "jobs").mkdir(exist_ok=True)
    db = sqlite3.connect(root / "state.sqlite3")
    db.executescript(_OLD_JOBS_DDL)
    db.execute(
        "INSERT INTO jobs(id,repo,number,head_sha,lane,status,artifact_dir,retries,"
        "created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
        ("legacy-job", "o/r", 7, "b" * 40, "incoming", status, str(root / "jobs"), 0,
         utcnow(), utcnow()),
    )
    db.commit()
    db.close()
    return root


def _columns(state: State, table: str) -> set[str]:
    return {row["name"] for row in state.db.execute(f"PRAGMA table_info({table})")}


# --------------------------------------------------------------------------
# 1. state-store migration
# --------------------------------------------------------------------------


def test_the_control_a_legacy_db_really_lacks_the_column() -> None:
    """Guards the guard. If the fixture already had `snapshot_hash`, every
    migration test below would pass without any migration happening."""
    root = _old_state_dir()
    db = sqlite3.connect(root / "state.sqlite3")
    names = {row[1] for row in db.execute("PRAGMA table_info(jobs)")}
    db.close()
    assert "snapshot_hash" not in names


def test_migration_adds_the_pinning_column_instead_of_leaving_pinning_a_noop() -> None:
    root = _old_state_dir()
    state = State({"state_dir": str(root)})
    assert "snapshot_hash" in _columns(state, "jobs")
    # ...and it is genuinely usable, not merely declared.
    state.execute("UPDATE jobs SET snapshot_hash=? WHERE id=?", ("deadbeef", "legacy-job"))
    state.db.commit()
    row = state.db.execute("SELECT snapshot_hash FROM jobs WHERE id=?", ("legacy-job",)).fetchone()
    assert row["snapshot_hash"] == "deadbeef"
    state.close()


def test_migration_never_discards_an_in_flight_job() -> None:
    """A migration that recreated the table would drop every resumable job while
    looking perfectly successful."""
    root = _old_state_dir(status="approval_revalidation")
    state = State({"state_dir": str(root)})
    row = state.db.execute("SELECT * FROM jobs WHERE id=?", ("legacy-job",)).fetchone()
    assert row is not None
    assert row["status"] == "approval_revalidation"
    assert row["head_sha"] == "b" * 40
    assert row["snapshot_hash"] is None  # unpinned, not fabricated
    state.close()


def test_reopening_a_migrated_store_does_not_re_add_or_reset_the_column() -> None:
    root = _old_state_dir()
    first = State({"state_dir": str(root)})
    first.execute("UPDATE jobs SET snapshot_hash=? WHERE id=?", ("pinned-hash", "legacy-job"))
    first.db.commit()
    first.close()

    second = State({"state_dir": str(root)})
    assert second._add_column_if_missing("jobs", "snapshot_hash", "TEXT") is False
    row = second.db.execute("SELECT snapshot_hash FROM jobs WHERE id=?", ("legacy-job",)).fetchone()
    assert row["snapshot_hash"] == "pinned-hash"
    assert second.db.execute("SELECT COUNT(*) AS n FROM jobs").fetchone()["n"] == 1
    second.close()


def test_a_job_persisted_under_a_retired_state_name_cannot_resume_into_approval() -> None:
    """An old row whose status no longer exists must be refused, not treated as a
    fresh job that may walk straight into an approval action."""
    root = _old_state_dir(status="awaiting_approval")  # a name this release does not know
    state = State({"state_dir": str(root)})
    assert state.current_status("legacy-job") == "awaiting_approval"
    for target in ("approval_action", "approval_revalidation", "completed_auto_approved"):
        try:
            state.transition("legacy-job", target)
        except JobBlockingError:
            continue
        raise AssertionError(f"retired status must not transition to {target}")
    state.close()


def test_an_unreadable_state_file_is_refused_rather_than_silently_started_empty() -> None:
    """Starting empty on a corrupt store would look like "no work pending" and
    abandon every in-flight job without a single error."""
    root = pathlib.Path(tempfile.mkdtemp())
    (root / "state.sqlite3").write_bytes(b"this is not a sqlite database" * 20)
    try:
        State({"state_dir": str(root)})
    except StatePersistenceError as exc:
        assert "state.sqlite3" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("a corrupt state store must not open cleanly")


# --------------------------------------------------------------------------
# 2. config version
# --------------------------------------------------------------------------


def _git_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp()).resolve()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text(
        ".review-queue-automation/\npr review logs\n", encoding="utf-8")
    return root


def _base_config(root: pathlib.Path) -> dict:
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "op"
    cfg["repository"]["slug"] = "o/r"
    (root / cfgmod.DEFAULT_LOG_DIR_NAME).mkdir(exist_ok=True)
    return cfg


def test_the_control_config_version_is_accepted() -> None:
    root = _git_repo()
    cfg = _base_config(root)
    assert isinstance(cfg["version"], int) and cfg["version"] >= 1
    assert cfgmod.validate_config(cfg, root) == []


def test_every_unusable_config_version_is_rejected() -> None:
    """`True` is deliberately absent from this list. `validate_config` checks
    `isinstance(config["version"], int)`, and in Python `isinstance(True, int)` is
    True, so `"version": true` is accepted as version 1. That laxity is reported,
    not asserted here: the snapshot layer independently refuses to turn a boolean
    into a version identity (see the next two tests), which is the property that
    actually protects a pin."""
    root = _git_repo()
    for value in (0, -1, "1", 1.5, None, "", [1]):
        cfg = _base_config(root)
        cfg["version"] = value
        issues = cfgmod.validate_config(cfg, root)
        assert any("version" in issue for issue in issues), value


def test_an_unversioned_config_is_never_promoted_to_a_version() -> None:
    """`cfg-unversioned` must not collapse into `cfg-1`. If it did, a config that
    predates versioning would share a pin with a versioned one."""
    for value in (None, "", True, False, [], {}, object()):
        cfg = {} if value is None else {"version": value}
        assert snapmod.config_version(cfg) == "cfg-unversioned", value
    assert snapmod.config_version({"version": 1}) == "cfg-1"
    assert snapmod.config_version({"version": 1}) != snapmod.config_version({})


def test_an_unversioned_policy_is_never_promoted_to_a_version() -> None:
    """`snapshot.policy_version` labels the pinned snapshot, so it is the one that
    must never invent a version. (`policy.policy_version` disagrees for a boolean
    — `str(True)` — which is reported as a divergence rather than asserted here.)"""
    for value in (None, "", [], {}):
        policy = {} if value is None else {"version": value}
        assert snapmod.policy_version(policy) == "unversioned", value
        assert policymod.policy_version(policy) == "unversioned", value
    assert snapmod.policy_version({"version": True}) == "unversioned"
    assert snapmod.policy_version({"version": "2026-01"}) == "2026-01"


def test_bumping_the_config_version_produces_a_different_snapshot_identity() -> None:
    """A migrated config is a NEW snapshot. Sharing a hash with the pre-migration
    config would let a job resumed under the old pin run the new rules."""
    policy = {"version": "p1", "authority": {}, "approval": {}, "risk": {}, "human_queue": {}}
    before = {"version": 1, "approval": {"mode": "disabled"}}
    after = {"version": 2, "approval": {"mode": "disabled"}}
    assert snapmod.content_hash(before, policy) != snapmod.content_hash(after, policy)
    # ...and so does a policy edit at an unchanged config version.
    assert snapmod.content_hash(before, policy) != snapmod.content_hash(
        before, {**policy, "version": "p2"}
    )
    # The hash is stable for identical input, so the inequalities above mean
    # something.
    assert snapmod.content_hash(before, policy) == snapmod.content_hash(
        json.loads(json.dumps(before)), json.loads(json.dumps(policy))
    )


def test_a_config_whose_required_keys_predate_this_release_is_rejected_not_defaulted() -> None:
    """A config written by an older release that lacks a now-required section must
    be an error. Defaulting it would invent an authority setting nobody chose."""
    root = _git_repo()
    for key in sorted(cfgmod.REQUIRED_KEYS):
        cfg = _base_config(root)
        cfg.pop(key)
        cfg_path = cfgmod.repo_config_path(root)
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
        loaded, _path, issues = cfgmod.load_repo_config(root)
        assert loaded is None, key
        assert issues, key

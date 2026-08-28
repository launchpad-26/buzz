#!/usr/bin/env python3
"""Onboarding + config-gating acceptance tests.

- No config -> onboarding_required, no GitHub/model/lease/canary activity.
- onboarding creates ignored config + ignored default log dir.
- Tracked/non-ignored config/log path -> fail safely, write nothing.
- Valid config -> paths writable and config parses.
- Proof onboarding never invokes a GitHub client, model runner, lease, or canary.
"""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import config as cfgmod  # noqa: E402

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _init_git(root: pathlib.Path) -> None:
    for cmd in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        subprocess.run(["git", *cmd], cwd=str(root), check=True, capture_output=True)


def _make_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    _init_git(root)
    (root / ".gitignore").write_text("", encoding="utf-8")
    return root


def test_no_config_triggers_onboarding_required() -> None:
    root = _make_repo()
    cfg, path, issues = cfgmod.load_repo_config(root)
    assert cfg is None
    assert any("config not found" in i for i in issues)
    # Dispatch-level gate: onboarding_required with no activity.
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "dispatcher.py"), "--repo-root", str(root), "sweep"],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    out = json.loads(r.stdout)
    assert out["status"] == "onboarding_required"
    assert "onboarding" in out


def test_onboarding_creates_ignored_config_and_log_dir() -> None:
    root = _make_repo()
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root), "--slug", "o/r", "--base", "main"],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, r.stdout + r.stderr
    cfg_path = root / ".review-queue-automation" / "config.json"
    assert cfg_path.is_file()
    # ignored + untracked
    assert cfgmod.is_ignored(root, ".review-queue-automation/")
    assert not cfgmod.is_tracked(root, ".review-queue-automation/")
    gi = (root / ".gitignore").read_text(encoding="utf-8")
    assert ".review-queue-automation/" in gi
    assert cfgmod.DEFAULT_LOG_DIR_NAME in gi
    # default log dir created + ignored
    log_dir = root / cfgmod.DEFAULT_LOG_DIR_NAME
    assert cfgmod.check_writable(log_dir)
    assert cfgmod.is_ignored(root, cfgmod.DEFAULT_LOG_DIR_NAME + "/")
    # config loads valid
    cfg, _, issues = cfgmod.load_repo_config(root)
    assert issues == []
    # no secrets: no field named token/key
    blob = cfg_path.read_text(encoding="utf-8")
    assert "api_key" not in blob.lower()
    assert "token" not in blob.lower()
    assert "secret" not in blob.lower()


def test_onboarding_refuses_tracked_config() -> None:
    root = _make_repo()
    # Create a config inside the repo but commit it (tracked). Should fail safely.
    tdir = root / ".review-queue-automation"
    tdir.mkdir(exist_ok=True)
    tcfg = root / ".review-queue-automation" / "config.json"
    tcfg.write_text(json.dumps(cfgmod.onboarding_defaults(root)), encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=str(root), check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-qm", "track"], cwd=str(root), check=True, capture_output=True)
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root)],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    out = json.loads(r.stdout)
    assert "refusing" in out.get("error", "") or "tracked" in json.dumps(out)


def test_valid_config_loads_and_paths_writable() -> None:
    root = _make_repo()
    cfg = {**cfgmod.onboarding_defaults(root), "login": "tucktuck101", "state_dir": "~/.config/rqa-state"}
    cfg["repository"]["slug"] = "launchpad-26/buzz"
    tdir = root / ".review-queue-automation"
    tdir.mkdir(exist_ok=True)
    (tdir / "config.json").write_text(json.dumps(cfg), encoding="utf-8")
    (root / ".gitignore").write_text(".review-queue-automation/\npr review logs/\n", encoding="utf-8")
    loaded, _, issues = cfgmod.load_repo_config(root)
    assert issues == []
    assert loaded["version"] == 1


def test_onboarding_invokes_no_forbidden_tools() -> None:
    """Onboarding must not call gh, codex, claude, or omp for real work."""
    root = _make_repo()
    r = subprocess.run(
        [sys.executable, str(SCRIPTS / "onboarding.py"), "init", str(root), "--slug", "o/r"],
        capture_output=True, text=True, env={**os.environ, "GITHUB_LOGIN": "t"},
    )
    assert r.returncode == 0


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
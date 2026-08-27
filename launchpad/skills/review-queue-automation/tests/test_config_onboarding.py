#!/usr/bin/env python3
"""Config + onboarding tests: temp-repo fakes, no gh, no network, no models.

Covers the repaired contract:
- Authoritative config is <repo>/.review-queue-automation/config.json.
- `init` refuses to overwrite an existing config; never runs gh (git only).
- `update` backs up atomically and restores the previous config when the new one
  fails validation; target repo root must equal the on-disk root.
- Runtime-ready requires a non-empty login + usable model pools.
- Recursive secret-key rejection fails closed; secret-looking keys anywhere fail.
- Live approval config is never enabled by omission (fail-closed defaults).
- Risk band continuity and protected-trigger regex errors fail closed.
- The config dir + logs are git-ignored and untracked after onboarding.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

import config as cfgmod  # noqa: E402
import onboarding as onb  # noqa: E402


def _git_repo() -> pathlib.Path:
    root = pathlib.Path(tempfile.mkdtemp())
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=root, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=root, check=True, capture_output=True)
    (root / ".gitignore").write_text("", encoding="utf-8")
    return root


def _cfg_path(root: pathlib.Path) -> pathlib.Path:
    return root / ".review-queue-automation" / "config.json"


def _real_config(root: pathlib.Path) -> dict:
    cfg = cfgmod.onboarding_defaults(root)
    cfg["login"] = "alice"
    cfg["repository"]["slug"] = "a/b"
    cfg.setdefault("models", {})["primary"] = [
        {"runner": "claude", "selector": "sonnet", "provider_family": "anthropic", "capability": "frontier", "efforts": ["high"]}
    ]
    cfg.setdefault("models", {})["secondary"] = [
        {"runner": "codex", "selector": "gpt5", "provider_family": "openai", "capability": "frontier", "efforts": ["high"]}
    ]
    return cfg


def test_authoritative_config_path_is_repo_local() -> None:
    root = _git_repo()
    assert _cfg_path(root) == cfgmod.repo_config_path(root)


def test_init_creates_valid_untracked_ignored_config() -> None:
    root = _git_repo()
    err, summary = onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")
    assert err is None, err
    # init_onboard resolves the repo root (macOS /var -> /private/var), so compare
    # against the resolved config path.
    assert summary["config_path"] == str(pathlib.Path(root).resolve() / ".review-queue-automation" / "config.json")
    # defaults leave model pools empty, so not runtime-ready until pools are added
    assert summary["runtime_ready"] is False
    assert any("pool" in p for p in summary["readiness_issues"])
    # The config is on disk, ignored, untracked.
    cfg_path = _cfg_path(root)
    assert cfg_path.is_file()
    assert "alice" in cfg_path.read_text() and "a/b" in cfg_path.read_text()
    assert cfgmod.is_ignored(root, cfgmod.RQA_CONFIG_DIR + "/")
    assert cfgmod.is_tracked(root, cfgmod.RQA_CONFIG_DIR) is False


def test_init_with_usable_pools_is_runtime_ready() -> None:
    root = _git_repo()
    err, summary = onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")
    assert err is None, err
    cfg = json.loads(_cfg_path(root).read_text())
    cfg["models"] = {"primary": [_real_config(root)["models"]["primary"][0]],
                     "secondary": [_real_config(root)["models"]["secondary"][0]]}
    _cfg_path(root).write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    ready, problems = onb._check_runtime_ready(cfg)
    assert ready is True, problems


def test_config_rejects_parallel_workers_sharing_one_state_dir() -> None:
    root = _git_repo()
    config = _real_config(root)
    config["dispatch"]["incoming_concurrency"] = 2
    problems = cfgmod.validate_config(config, root)
    assert "dispatch.incoming_concurrency must be 1: a state directory has one worker" in problems


def test_init_refuses_existing_config() -> None:
    root = _git_repo()
    first = onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")
    assert first[0] is None
    second = onb.init_onboard(root, slug="different", base="", preflight=None, login="bob")
    assert second[0] is not None
    assert "already exists" in second[0]
    cfg = json.loads(_cfg_path(root).read_text())
    assert cfg["repository"]["slug"] == "a/b"


def test_no_subprocess_gh_during_onboarding() -> None:
    root = _git_repo()
    spawned: list[list[str]] = []
    import subprocess as sp

    # Save ORIGINAL before patching: cfgmod.subprocess IS the shared subprocess
    # module, so overwriting .run and then calling sp.run inside the spy would
    # recurse into the spy itself.
    original_run = sp.run

    def spy(args, **kw):
        spawned.append(list(args) if isinstance(args, (list, tuple)) else args)
        return original_run(args, **kw)

    cfgmod.subprocess.run = spy  # type: ignore[assignment]
    try:
        err, summary = onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")
        assert err is None, err
        assert summary["runtime_ready"] is False  # pools empty by default
    finally:
        cfgmod.subprocess.run = original_run
    ghs = [s for s in spawned if s and s[0] == "gh"]
    assert ghs == [], f"onboarding must never invoke gh: {ghs}"


def test_update_restores_corrupted_config() -> None:
    root = _git_repo()
    assert onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")[0] is None
    cfg_path = _cfg_path(root)
    # Corrupt the on-disk config into a parseable-but-invalid file; update must
    # restore the pre-write file and remove the transient backup.
    cfg = json.loads(cfg_path.read_text())
    cfg.pop("github", None)  # REQUIRED -> structural validation failure
    corrupted = json.dumps(cfg, indent=2)
    cfg_path.write_text(corrupted, encoding="utf-8")

    err, summary = onb.update_config(root, slug="a/b", base="", preflight=None, login="alice")
    assert err is not None
    assert "restored" in err
    assert cfg_path.read_text() == corrupted
    assert not (root / ".review-queue-automation" / "config.json.bak.json").exists()


def test_update_restores_on_secret_key() -> None:
    root = _git_repo()
    assert onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")[0] is None
    cfg_path = _cfg_path(root)
    # Inject a secret-like key into the on-disk config. `update` must refuse to
    # publish the merged (invalid) config and roll back to the file state that
    # existed when update was called (which carries the injected key; rollback
    # undoes the update, not the user's prior edit).
    cfg = json.loads(cfg_path.read_text())
    cfg["api_token"] = "sekret"
    cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    pre_update = cfg_path.read_text()
    err, summary = onb.update_config(root, slug="a/b", base="", preflight=None, login="alice")
    assert err is not None
    assert "restored" in err
    assert cfg_path.read_text() == pre_update
    assert not (root / ".review-queue-automation" / "config.json.bak.json").exists()


def test_update_refuses_root_mismatch() -> None:
    root = _git_repo()
    (root / ".review-queue-automation").mkdir(exist_ok=True)
    other_root = pathlib.Path(tempfile.mkdtemp())
    (root / ".review-queue-automation" / "config.json").write_text(
        json.dumps({"version": 1, "repository": {"root": str(other_root)}}), encoding="utf-8"
    )
    err, _ = onb.update_config(root, slug="a/b", base="", preflight=None, login="alice")
    assert err is not None
    assert "does not match" in err


def test_update_from_other_repo_has_no_config() -> None:
    root = _git_repo()
    onb.init_onboard(root, slug="a/b", base="", preflight=None, login="alice")
    other = pathlib.Path(tempfile.mkdtemp())
    err, _ = onb.update_config(other, slug="x/y", base="", preflight=None, login="alice")
    assert err is not None and "no config to update" in err


def test_runtime_ready_requires_nonempty_login_and_pools() -> None:
    cfg = cfgmod.onboarding_defaults(pathlib.Path(tempfile.mkdtemp()))
    cfg["login"] = ""
    ready, problems = onb._check_runtime_ready(cfg)
    assert ready is False
    assert "login" in " ".join(problems)

    root = _git_repo()
    cfg = _real_config(root)
    cfg["models"] = {"primary": [], "secondary": []}
    cfg["login"] = "alice"
    ready, problems = onb._check_runtime_ready(cfg)
    assert ready is False
    assert any("pool" in p for p in problems)


def test_secret_keys_rejected_recursively() -> None:
    root = _git_repo()
    cfg = _real_config(root)
    cfg["models"]["primary"][0]["api_key"] = "sekret"
    cfg["models"]["secondary"].append({"runner": "x", "selector": "y", "provider_family": "z",
                                        "capability": "w", "efforts": ["low"], "req_secret": "ser"})
    issues = cfgmod.validate_config(cfg, root)
    assert any(("secret" in i or "api_key" in i) for i in issues), issues


def test_live_approval_is_fail_closed() -> None:
    root = _git_repo()
    assert cfgmod.validate_config(cfgmod.onboarding_defaults(root), root) != []
    cfg = _real_config(root)
    cfg["approval"]["mode"] = "live"
    cfg["approval"]["live_canary_approved"] = False
    issues = cfgmod.validate_config(cfg, root)
    assert any("live" in i for i in issues), issues


def test_risk_band_continuity_fails_closed() -> None:
    root = _git_repo()
    cfg = _real_config(root)
    cfg["risk"]["bands"] = {"low": 100, "medium": 50, "high": 40}
    issues = cfgmod.validate_config(cfg, root)
    assert any("band" in i for i in issues), issues


def test_bad_protected_trigger_fails_closed() -> None:
    root = _git_repo()
    cfg = _real_config(root)
    cfg["risk"]["protected_triggers"] = ["(unclosed"]
    issues = cfgmod.validate_config(cfg, root)
    assert any("regex" in i or "trigger" in i for i in issues), issues


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
#!/usr/bin/env python3
"""Contract test: the documented surface must reference only commands,
artifact filenames, mutation names, config paths, and CLI flags that actually
exist in scripts/. Fails when documentation drifts from the code."""

from __future__ import annotations

import pathlib
import re
import sys

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"
DOCS = pathlib.Path(__file__).resolve().parent.parent

sys.path.insert(0, str(SCRIPTS))

import github_mutate  # noqa: E402

PANEL_SRC = (DOCS / "scripts" / "panel.py").read_text(encoding="utf-8", errors="replace")
HUMAN_CLI_SRC = (DOCS / "scripts" / "human_cli.py").read_text(encoding="utf-8", errors="replace")

SLOT_FILES = tuple(re.findall(r'"review-[A-Z]\.txt"', PANEL_SRC))
SLOT_FILES = {ln[1:-1] for ln in SLOT_FILES}  # strip surrounding quotes
SKILL = (DOCS / "SKILL.md").read_text(encoding="utf-8")
CONTRACTS = (DOCS / "references" / "contracts.md").read_text(encoding="utf-8")
ALL_DOCS = SKILL + "\n" + CONTRACTS + "\n" + (DOCS / "references" / "classification.md").read_text(encoding="utf-8")
SHADOW_SRC = (DOCS / "scripts" / "shadow.py").read_text(encoding="utf-8")


def test_panel_artifact_names_match_code() -> None:
    slot_files = set(SLOT_FILES)
    assert slot_files, "panel.py must name the review artifacts"
    for f in slot_files:
        assert ('`%s`' % f) in SKILL, f"SKILL.md must reference {f}"
    assert "review-0.txt" not in SKILL
    assert "review-1.txt" not in SKILL


def test_mutation_names_match_code() -> None:
    mutations = set(github_mutate.MUTATIONS)
    assert "add_comment_review" in mutations
    assert "approve_review" in mutations
    assert github_mutate.fixed_event_of("add_comment_review") == "COMMENT"
    assert "add_review" not in mutations, "no `add_review` mutation exists"
    assert "add_review" not in SKILL, "SKILL.md names a nonexistent mutation `add_review`"
    assert "add_comment_review" in SKILL
    assert "approve_review" in CONTRACTS


def test_shadow_cli_flags_match_shadow_py() -> None:
    for flag in ("--samples", "--verdicts", "--assessments", "--out", "--mode", "--pr-facts", "--train-ratio"):
        assert flag in SHADOW_SRC, f"shadow.py must define {flag} (docs reference it)"
    for phrase in ("--mode current", "--pr-facts", "WOULD_AUTO_APPROVE"):
        assert phrase in SKILL, f"SKILL.md documents {phrase!r} but shadow.py mismatch"
    assert "FAILED_GATES" in SHADOW_SRC  # the verdict token shadow.py actually prints
    assert "no mutation" in SKILL.lower()


def test_repo_local_config_path_is_documented() -> None:
    # config.py uses <repo>/.review-queue-automation/config.json
    from config import RQA_CONFIG_DIR, CONFIG_FILENAME
    assert f"{RQA_CONFIG_DIR}/{CONFIG_FILENAME}" in SKILL


def test_approval_modes_match_evaluate() -> None:
    from approval_evaluate import VALID_DISPOSITIONS
    for mode in VALID_DISPOSITIONS:  # disabled, shadow, human_escalation, live
        assert mode in SKILL, f"SKILL.md must document approval mode {mode}"


def test_documented_scripts_exist() -> None:
    names = set(re.findall(r"scripts/([a-z0-9_]+)\.py", ALL_DOCS))
    names.discard("pr_review_batch")  # repo-side script at launchpad/scripts/, not scripts/
    for m in names:
        assert (SCRIPTS / f"{m}.py").is_file(), f"docs reference scripts/{m}.py which does not exist"


def test_human_cli_commands_match_human_cli_py() -> None:
    src = HUMAN_CLI_SRC
    for cmd in ("list", "show", "decide", "supersede"):
        assert cmd in SKILL, f"SKILL.md must document human_cli subcommand {cmd}"
        assert cmd in src, f"human_cli.py must define subcommand {cmd}"
    for choice in ("approve", "decline", "request_changes"):
        assert choice in src


def test_shadow_is_documented_as_read_only() -> None:
    assert "Read-only" in SKILL or "read-only" in SKILL
    assert "never edits config" in SKILL
    assert "never enables live mode" in SKILL


def test_cutoff_and_merged_doctrine_documented() -> None:
    assert "cutoff" in SKILL
    assert "independent" in SKILL
    assert "unknown" in SKILL  # merged-alone unknown framing
    assert "merged" in SKILL


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
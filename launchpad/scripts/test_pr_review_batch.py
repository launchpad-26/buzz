#!/usr/bin/env python3
"""Controls for pr_review_batch.py -- issue #426.

Every test here drives a pure classifier with literal fixtures. No network, no
`gh`, no git. That is deliberate: the whole point of extracting these rules from
a reviewer's head into a script is that they become testable, and a suite that
shelled out to `gh` would only be testable when GitHub agreed to cooperate.

Each classifier's test set includes the case that was got WRONG by hand during
the 2026-08-21/22 review batches. Those are marked `# regression:` and are the
reason the corresponding rule exists at all -- if one is deleted the rule it
guards has no witness.

Run:  python3 -m unittest test_pr_review_batch    (from launchpad/scripts/)
  or: python3 test_pr_review_batch.py
"""

from __future__ import annotations

import unittest

import pr_review_batch as m

NOW = "2026-08-22T00:00:00Z"


def review(submitted_at, body="", commit_id="aaaaaaaaa", state="CHANGES_REQUESTED"):
    return {
        "state": state,
        "submittedAt": submitted_at,
        "commit_id": commit_id,
        "body": body,
        "author": {"login": "reviewer"},
    }


class ParseTimeTests(unittest.TestCase):
    def test_z_suffix_and_offset_forms_both_parse(self):
        a = m.parse_time("2026-08-21T03:57:00Z")
        b = m.parse_time("2026-08-21T15:57:00+12:00")
        self.assertEqual(a, b)

    def test_unparseable_returns_none_rather_than_raising(self):
        # A classifier that crashes on a malformed timestamp fails the whole
        # batch. Unknown is a verdict; a traceback is not.
        self.assertIsNone(m.parse_time("not a time"))
        self.assertIsNone(m.parse_time(None))


class CitedPathTests(unittest.TestCase):
    def test_extracts_path_line_tokens(self):
        body = "found at `security_audit_tracked_files_check.py:56` and foo/bar.py:12"
        self.assertEqual(
            m.cited_paths(body),
            {"security_audit_tracked_files_check.py", "foo/bar.py"},
        )

    def test_ignores_bare_issue_and_pr_references(self):
        # "#271" and "1.2.3" must not read as paths, or every review looks misfiled.
        self.assertEqual(m.cited_paths("see #271 and version 1.2.3 and PR #275"), set())

    def test_ignores_urls(self):
        self.assertEqual(m.cited_paths("https://example.com/a.py:12"), set())


class StaleReviewTests(unittest.TestCase):
    def test_review_before_head_push_is_stale(self):
        # regression: #262. Blockers were fixed at 03:21; the review restating
        # them was submitted at 03:57 against a body written at 01:38.
        verdict = m.classify_review(
            review("2026-08-21T03:57:00Z"),
            head_committed_at="2026-08-21T04:16:00Z",
            diff_paths={"launchpad/agents/goose_config.py"},
        )
        self.assertEqual(verdict.state, "STALE")
        self.assertIn("head moved", verdict.reason)

    def test_review_after_head_push_is_current(self):
        verdict = m.classify_review(
            review("2026-08-21T20:55:00Z"),
            head_committed_at="2026-08-21T04:16:00Z",
            diff_paths={"launchpad/agents/goose_config.py"},
        )
        self.assertEqual(verdict.state, "CURRENT")

    def test_review_citing_paths_absent_from_the_diff_is_misfiled(self):
        # regression: #271. Its CHANGES_REQUESTED cited two files that exist
        # only in #275 -- the same review posted on the wrong PR. Detected
        # here by the citation/diff mismatch, not by comparing bodies.
        verdict = m.classify_review(
            review(
                "2026-08-21T03:44:36Z",
                body="blockers at `security_audit_tracked_files_check.py:56` "
                     "and `test_security_audit_ignore_coverage_check.py:20`",
            ),
            head_committed_at="2026-08-21T03:00:00Z",
            diff_paths={"launchpad/scripts/security_audit_secrets_check.py"},
        )
        self.assertEqual(verdict.state, "MISFILED")

    def test_a_review_citing_evidence_outside_the_diff_is_not_misfiled(self):
        # regression: the FALSE POSITIVE this script produced on live data
        # before the rule was tightened. Reviewing #374, it called a genuine
        # review MISFILED because the one path token in the body was
        # `launchpad/ARCHITECTURE.md` -- cited as corroborating evidence for a
        # quote, not as a defect site. Reviews cite files outside the diff all
        # the time; that is what checking a claim looks like.
        verdict = m.classify_review(
            review(
                "2026-08-21T21:09:53Z",
                body="`launchpad/ARCHITECTURE.md:99` quotes the row verbatim. "
                     "The four-tier table in 355-what-the-fork-actually-operates.md "
                     "double-counts three files.",
            ),
            head_committed_at="2026-08-21T20:00:00Z",
            diff_paths={"launchpad/Research/355-what-the-fork-actually-operates.md"},
        )
        self.assertEqual(verdict.state, "CURRENT")

    def test_one_cited_path_alone_is_never_misfiled(self):
        # One out-of-diff citation is not a pattern, and treating it as one is
        # how the false positive above happened.
        verdict = m.classify_review(
            review("2026-08-21T03:00:00Z", body="see `elsewhere/only.py:9`"),
            head_committed_at="2026-08-21T09:00:00Z",
            diff_paths={"something/else.py"},
        )
        self.assertEqual(verdict.state, "STALE")

    def test_misfiled_outranks_stale(self):
        # A review that never applied cannot be "addressed by a later push".
        # Reporting STALE would tell the author to expect it to clear on re-review.
        verdict = m.classify_review(
            review(
                "2026-08-21T03:00:00Z",
                body="see `only/in/other.py:9` and `also/elsewhere.py:4`",
            ),
            head_committed_at="2026-08-21T09:00:00Z",
            diff_paths={"something/else.py"},
        )
        self.assertEqual(verdict.state, "MISFILED")

    def test_review_citing_no_paths_is_not_misfiled(self):
        # Absence of citations is not evidence of misfiling -- plenty of real
        # reviews are prose. Falling through to STALE/CURRENT is correct.
        verdict = m.classify_review(
            review("2026-08-21T03:00:00Z", body="this needs more tests"),
            head_committed_at="2026-08-21T09:00:00Z",
            diff_paths={"a.py"},
        )
        self.assertEqual(verdict.state, "STALE")

    def test_unknown_when_a_timestamp_cannot_be_read(self):
        verdict = m.classify_review(
            review("garbage"),
            head_committed_at="2026-08-21T09:00:00Z",
            diff_paths={"a.py"},
        )
        self.assertEqual(verdict.state, "UNKNOWN")

    def test_non_change_request_reviews_are_skipped(self):
        self.assertIsNone(
            m.classify_review(
                review("2026-08-21T03:00:00Z", state="COMMENTED"),
                head_committed_at="2026-08-21T09:00:00Z",
                diff_paths={"a.py"},
            )
        )


class CiTriageTests(unittest.TestCase):
    def test_toolchain_fetch_timeout_is_a_flake(self):
        # regression: #268. setup-mold timed out fetching the linker on a PR
        # that changed one markdown file. Reporting that as REAL sends an
        # author hunting for a defect in someone else's network.
        v = m.classify_failure(
            check_name="Desktop Core",
            failed_step="Run rui314/setup-mold@9c9c13b",
            log_tail="HTTP request sent, awaiting response... Read error (Connection timed out)\n"
            "tar: Error is not recoverable: exiting now",
            diff_paths={"launchpad/decisions/ADR-0018-cohort-relay-vps-specification.md"},
            failing_paths=set(),
        )
        self.assertEqual(v.state, "FLAKE")

    def test_failure_in_files_outside_the_diff_is_pre_existing(self):
        # regression: #288. Four biome items in files the PR never touched,
        # inherited from upstream commits, printed ABOVE the real blocker.
        v = m.classify_failure(
            check_name="Desktop Core",
            failed_step="Desktop lint and format",
            log_tail="src/shared/styles/globals/terminal.css:276:15 lint/complexity/noImportantStyles",
            diff_paths={"desktop/src-tauri/src/lib.rs"},
            failing_paths={"desktop/src/shared/styles/globals/terminal.css"},
        )
        self.assertEqual(v.state, "PRE_EXISTING")

    def test_failure_in_a_file_the_pr_touches_is_real(self):
        v = m.classify_failure(
            check_name="Desktop Core",
            failed_step="Desktop lint and format",
            log_tail="src-tauri/src/lib.rs: 1000 -> 1001 (+1) lines (allowed 1000)",
            diff_paths={"desktop/src-tauri/src/lib.rs"},
            failing_paths={"desktop/src-tauri/src/lib.rs"},
        )
        self.assertEqual(v.state, "REAL")

    def test_real_outranks_pre_existing_when_both_appear(self):
        # regression: #288 again. Its log contained BOTH pre-existing warnings
        # and the real size-guard failure. A classifier that stopped at the
        # first recognised line would have cleared the PR.
        v = m.classify_failure(
            check_name="Desktop Core",
            failed_step="Desktop lint and format",
            log_tail="terminal.css:276 noImportantStyles\n"
            "- src-tauri/src/lib.rs: 1000 -> 1001 (+1) lines (allowed 1000)",
            diff_paths={"desktop/src-tauri/src/lib.rs"},
            failing_paths={
                "desktop/src/shared/styles/globals/terminal.css",
                "desktop/src-tauri/src/lib.rs",
            },
        )
        self.assertEqual(v.state, "REAL")

    def test_no_attributable_paths_is_unknown_not_clean(self):
        # Silence must not read as a pass.
        v = m.classify_failure(
            check_name="Security",
            failed_step="audit",
            log_tail="some output with no file references",
            diff_paths={"a.py"},
            failing_paths=set(),
        )
        self.assertEqual(v.state, "UNKNOWN")


class LogSelectionTests(unittest.TestCase):
    """regression: taking the LAST N lines of a CI log.

    On #288 the tail was checkout teardown and the size-guard line that broke
    the build had scrolled past, so the classifier answered UNKNOWN for a
    failure it should have called REAL. Selection is by content now.
    """

    LOG = "\n".join([
        "Desktop Core  Install desktop dependencies",
        "Desktop Core  + @biomejs/biome 2.4.16",
        "Desktop Core  - src-tauri/src/lib.rs: 1000 -> 1001 (+1) lines (allowed 1000)",
        "Desktop Core  error: Recipe `desktop-check` failed on line 119 with exit code 1",
        "Desktop Core  Post job cleanup.",
        "Desktop Core  [command]/usr/bin/git config --local --unset includeif.gitdir:/x",
        "Desktop Core  Removing credentials config '/home/runner/work/_temp/git-credentials-x'",
        "Desktop Core  Cleaning up orphan processes",
    ])

    def test_the_failure_line_survives_teardown_noise(self):
        kept = relevant = m.relevant_log_lines(self.LOG)
        self.assertIn("1000 -> 1001", kept)
        self.assertIn("exit code 1", kept)

    def test_teardown_chatter_is_dropped(self):
        kept = m.relevant_log_lines(self.LOG)
        for noise in ("git-credentials", "orphan processes", "includeif.gitdir"):
            self.assertNotIn(noise, kept)

    def test_the_real_failure_is_then_classified_real(self):
        # End to end through the two functions, which is the behaviour that
        # actually regressed: selection feeding classification.
        kept = m.relevant_log_lines(self.LOG)
        failing = {mo.group(1) for mo in m._PATH_TOKEN.finditer(kept)}
        verdict = m.classify_failure(
            check_name="Desktop Core",
            failed_step="Desktop lint and format",
            log_tail=kept,
            diff_paths={"src-tauri/src/lib.rs"},
            failing_paths=failing,
        )
        self.assertEqual(verdict.state, "REAL")

    def test_empty_log_yields_empty_selection(self):
        self.assertEqual(m.relevant_log_lines(""), "")
        self.assertEqual(m.relevant_log_lines(None), "")


class IndependenceTests(unittest.TestCase):
    def test_own_commit_in_window_is_a_conflict(self):
        # regression: #265. It carried a commit written in the reviewing
        # session; the conflict was caught by hand, one review too late.
        v = m.classify_independence(
            commits=[
                {"oid": "05a96047", "author_login": "serina-mcfall",
                 "committed_at": "2026-08-21T05:05:18Z"},
            ],
            self_login="serina-mcfall",
            session_since="2026-08-21T00:00:00Z",
        )
        self.assertEqual(v.state, "CONFLICT")
        self.assertIn("05a96047", v.reason)

    def test_own_commit_before_the_window_is_independent(self):
        # Her identity is on every commit in this repo, including ones written
        # weeks ago by other people's sessions. Only the current window counts,
        # or every PR looks conflicted and the flag becomes noise.
        v = m.classify_independence(
            commits=[
                {"oid": "deadbeef", "author_login": "serina-mcfall",
                 "committed_at": "2026-08-01T00:00:00Z"},
            ],
            self_login="serina-mcfall",
            session_since="2026-08-21T00:00:00Z",
        )
        self.assertEqual(v.state, "INDEPENDENT")

    def test_another_authors_commit_is_independent(self):
        v = m.classify_independence(
            commits=[{"oid": "cafe", "author_login": "tucktuck101",
                      "committed_at": "2026-08-21T05:00:00Z"}],
            self_login="serina-mcfall",
            session_since="2026-08-21T00:00:00Z",
        )
        self.assertEqual(v.state, "INDEPENDENT")

    def test_no_session_window_means_no_conflict_claimed(self):
        v = m.classify_independence(
            commits=[{"oid": "05a96047", "author_login": "serina-mcfall",
                      "committed_at": "2026-08-21T05:05:18Z"}],
            self_login="serina-mcfall",
            session_since=None,
        )
        self.assertEqual(v.state, "UNKNOWN")


class LeakScanTests(unittest.TestCase):
    def test_private_tooling_reference_is_found(self):
        # regression: #281 quoted a private hook's header verbatim in a file
        # destined for a public repository.
        hits = m.scan_leaks(
            'diff --git a/x.md b/x.md\n+quotes pr-gate.sh in its header\n',
            patterns=m.DEFAULT_LEAK_PATTERNS,
        )
        self.assertEqual([h.pattern for h in hits], ["pr-gate"])

    def test_only_added_lines_are_scanned(self):
        # A removed reference is a fix, not a leak. Flagging it would punish
        # the commit that cleaned it up.
        hits = m.scan_leaks(
            "diff --git a/x.md b/x.md\n-mentions pr-gate.sh\n+clean now\n",
            patterns=m.DEFAULT_LEAK_PATTERNS,
        )
        self.assertEqual(hits, [])

    def test_diff_header_lines_are_not_scanned(self):
        # `+++ b/launchpad/scripts/verify-gate.sh` is a filename, not content.
        hits = m.scan_leaks(
            "--- a/a\n+++ b/launchpad/scripts/verify-gate.sh\n+ok\n",
            patterns=m.DEFAULT_LEAK_PATTERNS,
        )
        self.assertEqual(hits, [])

    def test_clean_diff_yields_nothing(self):
        self.assertEqual(
            m.scan_leaks("+just some prose\n", patterns=m.DEFAULT_LEAK_PATTERNS), []
        )


class PlacementTests(unittest.TestCase):
    def test_cohort_file_under_launchpad_is_allowed(self):
        self.assertEqual(m.check_placement({"launchpad/Research/x.md"}), [])

    def test_cohort_file_in_upstream_docs_tree_is_flagged(self):
        # AGENTS.md section 3: docs/ and root scripts/ are upstream's trees.
        self.assertEqual(m.check_placement({"docs/x.md"}), ["docs/x.md"])

    def test_root_scripts_is_flagged(self):
        self.assertEqual(m.check_placement({"scripts/x.sh"}), ["scripts/x.sh"])

    def test_upstream_owned_product_paths_are_not_flagged(self):
        # A PR touching crates/ or desktop/ is upstream-shaped work, which is
        # legitimate here; placement only judges cohort files.
        self.assertEqual(m.check_placement({"crates/buzz-relay/src/lib.rs"}), [])

    def test_bare_md_directly_in_launchpad_agents_is_flagged(self):
        # AGENTS.md: a bare .md there is scanned as a subagent roster and
        # blocks the commit. Pack docs belong in a subdirectory.
        self.assertEqual(
            m.check_placement({"launchpad/agents/notes.md"}),
            ["launchpad/agents/notes.md"],
        )

    def test_md_inside_an_agent_pack_subdirectory_is_allowed(self):
        self.assertEqual(
            m.check_placement({"launchpad/agents/the-professor/README.md"}), []
        )


class BriefingTests(unittest.TestCase):
    def test_blocking_when_a_real_failure_exists(self):
        b = m.Briefing(number=1, author="x", title="t", head_sha="abc")
        b.ci.append(m.Attributed("Desktop Core", m.Verdict("REAL", "size guard")))
        self.assertTrue(b.blocks_review())

    def test_blocking_on_an_independence_conflict(self):
        b = m.Briefing(number=1, author="x", title="t", head_sha="abc")
        b.independence = m.Verdict("CONFLICT", "own commit 05a96047")
        self.assertTrue(b.blocks_review())

    def test_flake_and_pre_existing_do_not_block(self):
        b = m.Briefing(number=1, author="x", title="t", head_sha="abc")
        b.ci.append(m.Attributed("Desktop Core", m.Verdict("FLAKE", "setup-mold timeout")))
        b.ci.append(m.Attributed("Desktop", m.Verdict("PRE_EXISTING", "terminal.css")))
        self.assertFalse(b.blocks_review())

    def test_the_briefing_states_no_severity_anywhere(self):
        # The script must not emit severities -- ADR-0019 forbids a model
        # verdict gating, and a script that guessed severity would be worse
        # than the reviewer it replaced. This asserts the absence.
        b = m.Briefing(number=1, author="x", title="t", head_sha="abc")
        b.ci.append(m.Attributed("Desktop Core", m.Verdict("REAL", "something")))
        rendered = b.render().lower()
        for word in ("blocker", "high", "medium", "low", "severity"):
            self.assertNotIn(word, rendered, f"briefing must not grade: {word!r}")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Controls for pr_body_check.

These import the module the workflow actually runs. The suite they replace copied
the logic by hand, so it would have passed unchanged if the real check were
reverted or replaced with `sys.exit(0)` — the defect that made issue #125's fix
unverifiable. Nothing here duplicates a regex.

Run:  python3 -m unittest discover -s launchpad/scripts
"""

from __future__ import annotations

import contextlib
import io
import os
import unittest
from unittest import mock

import pr_body_check as m


def run_main(
    body: str,
    labels: str = "[]",
    closing_refs: str | None = None,
    feature_children: str | None = None,
):
    """Drive main() the way the workflow does, and capture what it prints.

    check() returning the right note is not the same as a reader SEEING it. The
    degraded mode exists so an unverified pass is visible, and that promise lives
    in main()'s output — so it has to be asserted there, not one layer down.
    """
    env = {"BODY": body, "LABELS": labels}
    if closing_refs is not None:
        env["CLOSING_REFS"] = closing_refs
    if feature_children is not None:
        env["FEATURE_CHILDREN"] = feature_children
    buf = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), contextlib.redirect_stdout(buf):
        code = m.main()
    return code, buf.getvalue()


# A single-issue PR writes N/A in Feature — legal under ADR-0052, and the shape most
# of these tests want, since they are about references and code stripping rather than
# batching.
SINGLE = """### Feature
N/A - single-issue PR
"""

AGENT_BODY = """## Summary
Something.

### Issue type
Task

### Feature
N/A - single-issue PR

| Field | Value |
|---|---|
| Harness / provider | Claude Code |
| Model | claude-opus-5 |
| Initiating human | @someone |

### Verification

```
raw output
```

### Authority
N/A - approved by a human directly

### Deferred blockers
none

### Not verified
The relay was not exercised.

### Escalations
none
"""


class ClosingRefsComeFromGitHub(unittest.TestCase):
    """The authoritative path: GitHub answers, no markdown is parsed."""

    def test_github_reporting_a_link_passes(self):
        errors, notes = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n", [], [116])
        self.assertEqual(errors, [])
        self.assertIn("#116", notes[0])

    def test_github_reporting_no_link_fails_even_with_a_keyword_present(self):
        # The heart of #125: the body says Closes, GitHub made no link, so the
        # board will not move. A text search would have passed this.
        errors, _ = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #116\n", [], [])
        self.assertTrue(any("no issue reference github recognises" in e.lower() for e in errors))

    def test_that_failure_explains_the_code_span_cause(self):
        errors, _ = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\n`Closes #116`\n", [], [])
        # The keyword is in the body but stripped from prose, so no hint fires.
        self.assertTrue(any("no issue reference" in e.lower() for e in errors))

    def test_keyword_outside_code_with_no_github_link_gets_the_hint(self):
        errors, _ = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #116\n", [], [])
        self.assertTrue(any("plain text" in e for e in errors))

    def test_refs_passes_when_github_reports_nothing(self):
        errors, notes = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nRefs #116\n", [], [])
        self.assertEqual(errors, [])
        self.assertIn("nothing closes on merge", notes[0])

    def test_no_reference_at_all_fails(self):
        errors, _ = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nNothing here.\n", [], [])
        self.assertTrue(any("no issue reference" in e.lower() for e in errors))


class AbsenceIsNotEvidence(unittest.TestCase):
    """CLOSING_REFS unknown must degrade visibly, never pass silently."""

    def test_unknown_is_not_the_same_as_empty(self):
        self.assertIsNone(m.parse_closing_refs(None))
        self.assertIsNone(m.parse_closing_refs(""))
        self.assertIsNone(m.parse_closing_refs("   "))
        self.assertEqual(m.parse_closing_refs("[]"), [])

    def test_unparseable_is_unknown_not_empty(self):
        self.assertIsNone(m.parse_closing_refs("{not json"))
        self.assertIsNone(m.parse_closing_refs('{"a":1}'))

    def test_non_integers_are_discarded(self):
        self.assertEqual(m.parse_closing_refs('[1,"x",2]'), [1, 2])

    def test_booleans_are_discarded_despite_bool_subclassing_int(self):
        # isinstance(True, int) is True in Python, so without an explicit guard a
        # JSON `true` survives as 1 and prints as "#True".
        self.assertEqual(m.parse_closing_refs("[true]"), [])
        self.assertEqual(m.parse_closing_refs("[1,true,2]"), [1, 2])

    def test_degraded_mode_says_it_is_not_verified(self):
        errors, notes = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #9\n", [], None)
        self.assertEqual(errors, [])
        self.assertIn("NOT verified", notes[0])

    def test_degraded_mode_still_fails_a_body_with_no_reference(self):
        errors, _ = m.check("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nNothing.\n", [], None)
        self.assertTrue(errors)


class WhatMainActuallyPrints(unittest.TestCase):
    """The degraded warning is only worth anything if a reader sees it."""

    def test_a_passing_degraded_run_still_says_it_is_unverified(self):
        # The mutation this exists to catch: printing notes only when there are
        # errors. That leaves a PASSING degraded run silent about being unverified,
        # which defeats the whole point, and check() alone cannot detect it.
        code, out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #9\n", closing_refs=None)
        self.assertEqual(code, 0)
        self.assertIn("NOT verified", out)
        self.assertIn("passed", out)

    def test_a_verified_pass_does_not_claim_to_be_unverified(self):
        code, out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n", closing_refs="[9]")
        self.assertEqual(code, 0)
        self.assertNotIn("NOT verified", out)
        self.assertIn("#9", out)

    def test_a_failing_run_exits_one_and_explains(self):
        code, out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nnothing\n", closing_refs="[]")
        self.assertEqual(code, 1)
        self.assertIn("check failed", out)

    def test_blank_closing_refs_is_treated_as_unknown_not_empty(self):
        # The workflow writes an empty string when the query fails.
        code, out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #9\n", closing_refs="")
        self.assertEqual(code, 0)
        self.assertIn("NOT verified", out)

    def test_degraded_refs_and_degraded_closes_read_differently(self):
        _, closes_out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nCloses #9\n", closing_refs="")
        _, refs_out = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nRefs #9\n", closing_refs="")
        self.assertNotEqual(closes_out, refs_out)
        self.assertIn("nothing was expected to close", refs_out)

    def test_malformed_labels_do_not_crash(self):
        code, _ = run_main("### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n", labels="{not json", closing_refs="[1]")
        self.assertEqual(code, 0)


class CodeStripping(unittest.TestCase):
    """The four shapes that defeated the previous fix, plus the ordering."""

    def test_unterminated_fence_swallows_what_follows(self):
        self.assertNotIn("Closes", m.strip_code("Text\n```\noutput\nCloses #42\n"))

    def test_double_backtick_span_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("See ``Closes #6`` here."))

    def test_quad_fence_with_inner_run_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("````\n``` ex\nCloses #1\n````"))

    def test_indented_lines_are_NOT_stripped(self):
        # Deliberate: stripping every 4-space line deleted ordinary nested markdown
        # and rejected compliant PRs. Accepted cost is an indented `Refs` counting.
        self.assertIn("Closes", m.strip_code("Refs #1\n\n    Closes #999\n"))

    def test_a_nested_bullet_reference_still_passes(self):
        # The false block this replaced: GitHub renders both these lines as prose.
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\n- part of a larger plan:\n    - Refs #116 follows\n"
        errors, _ = m.check(body, [], [])
        self.assertEqual(errors, [], f"a nested-bullet Refs must not be rejected: {errors}")

    def test_a_wrapped_continuation_reference_still_passes(self):
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\n1. Background\n2. Work described in\n    Refs #116\n"
        errors, _ = m.check(body, [], [])
        self.assertEqual(errors, [], f"a continuation-line Refs must not be rejected: {errors}")

    def test_blockquoted_fence_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n> ```\n> Closes #999\n> ```\n"))

    def test_blockquoted_unterminated_fence_does_not_consume_prose_after_the_quote_ends(self):
        # #145: a fence opened with `> ` and never explicitly closed used to stay
        # open past the blockquote's own end, since the fence carried no memory of
        # having opened inside a quote. CommonMark ends the fence when the quote
        # does — a line with no `>` marker closes the quote, and the fence closes
        # with it.
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\n> ```\n> some quoted output\n\nRefs #116 covers the rest.\n"
        stripped = m.strip_code(body)
        self.assertIn("Refs #116", stripped, f"prose after the quote ends must survive: {stripped!r}")
        errors, _ = m.check(body, [], [])
        self.assertEqual(errors, [], f"a compliant Refs after a quoted fence must not be rejected: {errors}")

    def test_blockquoted_unterminated_fence_closes_on_a_bare_top_level_blank_line_too(self):
        # Same defect, blank line spelled with no `>` at all rather than omitted.
        body = "> ```\n> quoted\n\n\nRefs #1\n"
        self.assertIn("Refs #1", m.strip_code(body))

    def test_a_properly_closed_blockquoted_fence_still_closes_at_its_own_closer(self):
        # Regression guard: the fix must not make every quoted fence run to the
        # quote's end — one that closes explicitly, still inside the quote, must
        # close there and nowhere later.
        body = "> ```\n> Closes #999\n> ```\n\nRefs #1\n"
        stripped = m.strip_code(body)
        self.assertNotIn("Closes", stripped)
        self.assertIn("Refs #1", stripped)

    def test_fence_with_an_info_string_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n```python\nCloses #9\n```\n"))

    def test_fence_opener_indented_up_to_three_spaces_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n   ```\n   Closes #9\n   ```\n"))

    def test_a_backtick_fence_is_not_closed_by_a_tilde_run(self):
        # CommonMark forbids it, so the fence stays open and swallows the rest.
        self.assertNotIn("Closes", m.strip_code("```\nx\n~~~\nCloses #9\n"))

    def test_a_closer_with_trailing_junk_is_not_a_closer(self):
        # Accepting it ended the block early (leaking code) and opened a spurious
        # new fence (swallowing real prose after it).
        out = m.strip_code("```\nfirst\n```not a closer\nCloses #1\n```\n\nRefs #2\n")
        self.assertNotIn("Closes", out)
        self.assertIn("Refs #2", out)

    def test_a_closer_may_carry_trailing_whitespace(self):
        self.assertNotIn("Closes", m.strip_code("```\nCloses #9\n```   \n"))

    def test_balanced_fence_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n```\nCloses #1\n```\n"))

    def test_tilde_fence_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n~~~\nCloses #1\n~~~\n"))

    def test_prose_outside_code_survives(self):
        self.assertIn("Refs #1", m.strip_code("Refs #1\n\n```\ncode\n```\n"))

    def test_reference_after_a_balanced_fence_survives(self):
        self.assertIn("Closes #12", m.strip_code("```\nout\n```\n\nCloses #12\n"))

    def test_html_comment_is_removed_before_anything_else(self):
        self.assertNotIn("Closes", m.strip_comments("<!-- Closes #116 -->"))


class SectionsAndAgentRules(unittest.TestCase):
    def edited(self, old: str, new: str) -> str:
        """AGENT_BODY with one substring swapped, asserting the swap happened.

        `str.replace` no-ops silently when its target drifts, which turns a test
        into a check on an unmodified fixture and reports the wrong cause when it
        fails. Four tests below depend on the edit landing, so it is verified.
        """
        self.assertIn(old, AGENT_BODY, f"fixture drifted: {old!r} is no longer present")
        out = AGENT_BODY.replace(old, new, 1)
        self.assertNotEqual(out, AGENT_BODY, "the fixture edit did not change anything")
        return out

    def test_missing_issue_type_is_an_error(self):
        errors, _ = m.check("Refs #1\n", [], [])
        self.assertTrue(any("Issue type" in e for e in errors))

    def test_unrecognised_issue_type_is_an_error(self):
        errors, _ = m.check("### Issue type\nWidget\n\nRefs #1\n", [], [])
        self.assertTrue(any("must be one of" in e for e in errors))

    def test_empty_body_is_an_error(self):
        errors, _ = m.check("", [], [])
        self.assertTrue(any("empty" in e for e in errors))

    def test_a_complete_agent_body_passes(self):
        errors, _ = m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertEqual(errors, [], f"unexpected: {errors}")

    def test_agent_body_missing_provenance_fails(self):
        body = self.edited("| Model | claude-opus-5 |", "| Model |  |")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("Model" in e for e in errors))

    def test_agent_body_with_hollow_not_verified_fails(self):
        body = self.edited("The relay was not exercised.", "nothing")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("Not verified" in e for e in errors))

    def test_agent_body_without_a_fence_fails(self):
        body = self.edited("```\nraw output\n```", "raw output")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("fenced code block" in e for e in errors))

    def test_the_fence_rule_reads_the_unstripped_body(self):
        # If it read stripped prose the fence would be gone and this could never
        # pass — the reason `check` keeps two strings.
        errors, _ = m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertFalse(any("fenced code block" in e for e in errors))

    def test_human_body_is_not_held_to_agent_rules(self):
        errors, _ = m.check(
            "### Issue type\nBug\n\n### Feature\nN/A - single-issue PR\n\nRefs #1\n", [], []
        )
        self.assertEqual(errors, [])


class FeatureBatching(unittest.TestCase):
    """ADR-0052 part C: a batch names one Feature and closes only its children."""

    HEAD = "### Issue type\nFeature\n\n### Feature\n#587\n"

    def test_feature_is_now_a_legal_issue_type(self):
        # Regression: ISSUE_TYPES omitted Feature, so every Feature PR failed while
        # 07-feature.yml and the AGENTS.md type table both named it.
        errors, _ = m.check(self.HEAD, [], [1])
        self.assertNotIn(
            True, [("Issue type must be one of" in e) for e in errors], msg=str(errors)
        )

    def test_all_closed_issues_children_of_the_named_feature_passes(self):
        errors, notes = m.check(self.HEAD, [], [101, 102], [101, 102, 103])
        self.assertEqual(errors, [])
        self.assertTrue(any("children of Feature #587" in n for n in notes), notes)

    def test_a_stray_issue_outside_the_feature_is_rejected(self):
        errors, _ = m.check(self.HEAD, [], [101, 999], [101, 102])
        self.assertTrue(any("#999" in e and "not a child" in e for e in errors), errors)

    def test_closing_the_feature_itself_is_allowed(self):
        # The batch that finishes a Feature closes the Feature too; it is not its
        # own child, so an unguarded membership test would reject the normal case.
        errors, _ = m.check(self.HEAD, [], [587, 101], [101])
        self.assertEqual(errors, [])

    def test_a_named_feature_with_an_unreadable_child_list_fails_closed(self):
        # Changed deliberately after panel review: this used to pass with a note. With no
        # second human in the merge path, a membership check that passes because it could
        # not run is a bypass, so an unreadable child list is now an error.
        errors, _ = m.check(self.HEAD, [], [101, 102], None)
        self.assertTrue(any("fails closed" in e for e in errors), errors)

    def test_na_feature_with_unknown_closing_refs_does_not_assert_single_issue(self):
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\nRefs #1\n"
        errors, notes = m.check(body, [], None, None)
        self.assertEqual(errors, [])
        self.assertTrue(any("NOT verified" in n for n in notes), notes)

    def test_na_feature_with_several_closed_issues_is_rejected(self):
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n"
        errors, _ = m.check(body, [], [101, 102], [101, 102])
        self.assertTrue(any("closes 2 issues" in e for e in errors), errors)

    def test_a_feature_section_naming_two_issues_is_rejected(self):
        body = "### Issue type\nFeature\n\n### Feature\n#587 and #588\n"
        errors, _ = m.check(body, [], [101], [101])
        self.assertTrue(any("exactly one issue" in e for e in errors), errors)

    def test_a_missing_feature_section_is_rejected(self):
        errors, _ = m.check("### Issue type\nTask\n\nRefs #1\n", [], [])
        self.assertTrue(any("Missing '### Feature'" in e for e in errors), errors)


class DelegatedAuthority(unittest.TestCase):
    """ADR-0052 part A: an agent-exercised approval has to show its warrant."""

    def body(self, authority: str, deferred: str = "none") -> str:
        return AGENT_BODY.replace(
            "### Authority\nN/A - approved by a human directly",
            f"### Authority\n{authority}",
        ).replace("### Deferred blockers\nnone", f"### Deferred blockers\n{deferred}")

    def test_na_authority_passes_for_a_human_approved_pr(self):
        errors, _ = m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertEqual(errors, [])

    def test_a_quote_with_a_link_passes(self):
        b = self.body("> merge it\n\nSaid on https://github.com/o/r/issues/1#issuecomment-2")
        errors, _ = m.check(b, ["by:agent"], [1])
        self.assertEqual(errors, [])

    def test_a_claim_with_no_quote_is_rejected(self):
        b = self.body("The operator told me to merge. https://github.com/o/r/issues/1")
        errors, _ = m.check(b, ["by:agent"], [1])
        self.assertTrue(any("quotes nothing" in e for e in errors), errors)

    def test_a_quote_with_no_link_is_accepted(self):
        # Changed on the operator's instruction: requiring a linked comment was ceremony.
        # An agent running under a human's token links a comment authored by that same
        # token, so the link adds no attribution the quote does not already carry.
        errors, _ = m.check(self.body("> merge it"), ["by:agent"], [1])
        self.assertEqual(errors, [])

    def test_an_empty_authority_section_is_rejected(self):
        errors, _ = m.check(self.body("tbd"), ["by:agent"], [1])
        self.assertTrue(any("'Authority' is empty" in e for e in errors), errors)

    def test_deferred_blockers_must_name_issues(self):
        b = self.body("N/A - approved by a human directly", "the headings are wrong")
        errors, _ = m.check(b, ["by:agent"], [1])
        self.assertTrue(any("must reference its issue" in e for e in errors), errors)

    def test_deferred_blockers_with_issue_numbers_pass(self):
        b = self.body("N/A - approved by a human directly", "#1490 - headings not reconciled")
        errors, _ = m.check(b, ["by:agent"], [1])
        self.assertEqual(errors, [])

    def test_a_human_pr_is_not_asked_for_authority(self):
        errors, _ = m.check("### Issue type\nBug\n\n### Feature\nN/A - x\n\nRefs #1\n", [], [])
        self.assertEqual(errors, [])


class PartEIsEnforced(unittest.TestCase):
    """ADR-0052 part E, the half that is checkable at PR time.

    A Feature that closes while holding open deferred blockers is the parallel-queue
    failure the rule exists to prevent, and GitHub closes it the moment the batch merges.
    """

    def body(self, deferred: str, feature: str = "#587") -> str:
        return AGENT_BODY.replace("### Feature\nN/A - single-issue PR", f"### Feature\n{feature}").replace(
            "### Deferred blockers\nnone", f"### Deferred blockers\n{deferred}"
        )

    def test_closing_the_feature_while_deferring_is_rejected(self):
        errors, _ = m.check(
            self.body("#900 - unfixed"), ["by:agent"], [587, 101], [101, 900]
        )
        self.assertTrue(any("part E" in e for e in errors), errors)

    def test_deferring_without_closing_the_feature_is_allowed(self):
        errors, _ = m.check(self.body("#900 - unfixed"), ["by:agent"], [101], [101, 900])
        self.assertEqual(errors, [])

    def test_more_than_five_deferred_blockers_is_rejected(self):
        listed = "\n".join(f"#{900 + i} - x" for i in range(6))
        errors, _ = m.check(
            self.body(listed), ["by:agent"], [101], [101] + [900 + i for i in range(6)]
        )
        self.assertTrue(any("ceiling of 5" in e for e in errors), errors)

    def test_exactly_five_is_allowed(self):
        listed = "\n".join(f"#{900 + i} - x" for i in range(5))
        errors, _ = m.check(
            self.body(listed), ["by:agent"], [101], [101] + [900 + i for i in range(5)]
        )
        self.assertEqual(errors, [])

    def test_a_deferred_blocker_outside_the_feature_is_rejected(self):
        errors, _ = m.check(self.body("#7777 - invented"), ["by:agent"], [101], [101])
        self.assertTrue(any("#7777" in e and "not children" in e for e in errors), errors)

    def test_an_empty_deferred_section_is_rejected(self):
        errors, _ = m.check(self.body(""), ["by:agent"], [101], [101])
        self.assertTrue(any("is empty" in e for e in errors), errors)


class BatchCapIsEnforced(unittest.TestCase):
    """ADR-0052 part C. Left in prose the cap reproduced what it was meant to prevent."""

    HEAD = "### Issue type\nFeature\n\n### Feature\n#587\n"

    def test_a_batch_over_the_line_cap_is_rejected(self):
        errors, _ = m.check(self.HEAD, [], [101, 102], [101, 102], 1501, 3)
        self.assertTrue(any("exceeds the cap" in e for e in errors), errors)

    def test_a_batch_over_the_file_cap_is_rejected(self):
        errors, _ = m.check(self.HEAD, [], [101, 102], [101, 102], 10, 11)
        self.assertTrue(any("exceeds the cap" in e for e in errors), errors)

    def test_a_batch_within_both_caps_passes(self):
        errors, notes = m.check(self.HEAD, [], [101, 102], [101, 102], 1500, 10)
        self.assertEqual(errors, [])
        self.assertTrue(any("within 1500/10" in n for n in notes), notes)

    def test_a_single_issue_pr_is_not_capped(self):
        # Part C bounds batches. Capping focused single-issue work would block ordinary
        # large changes the decision says nothing about.
        body = "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n"
        errors, _ = m.check(body, [], [101], [101], 99999, 500)
        self.assertEqual(errors, [])

    def test_missing_size_numbers_degrade_visibly(self):
        errors, notes = m.check(self.HEAD, [], [101, 102], [101, 102], None, None)
        self.assertEqual(errors, [])
        self.assertTrue(any("NOT verified" in n for n in notes), notes)


class CheckActuallyCallsItsSubChecks(unittest.TestCase):
    """Panel finding: the suite pinned each function but not the wiring in check().

    A check() edited to stop calling check_batch or check_delegated would have kept every
    other test green. These fail if the call is dropped.
    """

    def test_check_invokes_check_batch(self):
        called = {}
        real = m.check_batch

        def spy(*a, **k):
            called["batch"] = True
            return real(*a, **k)

        with mock.patch.object(m, "check_batch", spy):
            m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertTrue(called.get("batch"), "check() no longer calls check_batch")

    def test_check_invokes_check_delegated_for_agent_prs(self):
        called = {}
        real = m.check_delegated

        def spy(*a, **k):
            called["delegated"] = True
            return real(*a, **k)

        with mock.patch.object(m, "check_delegated", spy):
            m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertTrue(called.get("delegated"), "check() no longer calls check_delegated")

    def test_check_invokes_check_cap(self):
        called = {}
        real = m.check_cap

        def spy(*a, **k):
            called["cap"] = True
            return real(*a, **k)

        with mock.patch.object(m, "check_cap", spy):
            m.check(AGENT_BODY, ["by:agent"], [1, 2])
        self.assertTrue(called.get("cap"), "check() no longer calls check_cap")


class LabelStrippingDoesNotBypass(unittest.TestCase):
    """Removing `by:agent` used to switch off every strict check at once."""

    def test_provenance_table_triggers_agent_rules_without_the_label(self):
        stripped = AGENT_BODY.replace("### Authority\nN/A - approved by a human directly\n\n", "")
        errors, _ = m.check(stripped, [], [1])
        self.assertTrue(any("Authority" in e for e in errors), errors)

    def test_missing_label_is_itself_reported(self):
        errors, _ = m.check(AGENT_BODY, [], [1])
        self.assertTrue(any("no 'by:agent' label" in e for e in errors), errors)

    def test_an_authority_claim_alone_triggers_the_rules(self):
        body = (
            "### Issue type\nTask\n\n### Feature\nN/A - single-issue PR\n\n"
            "### Authority\n> merge it\n\nhttps://example.com/c/1\n"
        )
        errors, _ = m.check(body, [], [1])
        self.assertTrue(any("Deferred blockers" in e for e in errors), errors)

    def test_a_genuine_human_pr_is_still_not_held_to_agent_rules(self):
        body = "### Issue type\nBug\n\n### Feature\nN/A - single-issue PR\n\nRefs #1\n"
        errors, _ = m.check(body, [], [])
        self.assertEqual(errors, [])

    def test_a_human_pr_writing_na_authority_stays_human(self):
        body = (
            "### Issue type\nBug\n\n### Feature\nN/A - single-issue PR\n\n"
            "### Authority\nN/A - approved by a human directly\n\nRefs #1\n"
        )
        errors, _ = m.check(body, [], [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

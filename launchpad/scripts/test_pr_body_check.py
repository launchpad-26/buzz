#!/usr/bin/env python3
"""Controls for pr_body_check.

These import the module the workflow actually runs. The suite they replace copied
the logic by hand, so it would have passed unchanged if the real check were
reverted or replaced with `sys.exit(0)` — the defect that made issue #125's fix
unverifiable. Nothing here duplicates a regex.

Run:  python3 -m unittest discover -s launchpad/scripts
"""

from __future__ import annotations

import unittest

import pr_body_check as m

AGENT_BODY = """## Summary
Something.

### Issue type
Task

| Field | Value |
|---|---|
| Harness / provider | Claude Code |
| Model | claude-opus-5 |
| Initiating human | @someone |

### Verification

```
raw output
```

### Not verified
The relay was not exercised.

### Escalations
none
"""


class ClosingRefsComeFromGitHub(unittest.TestCase):
    """The authoritative path: GitHub answers, no markdown is parsed."""

    def test_github_reporting_a_link_passes(self):
        errors, notes = m.check("### Issue type\nTask\n", [], [116])
        self.assertEqual(errors, [])
        self.assertIn("#116", notes[0])

    def test_github_reporting_no_link_fails_even_with_a_keyword_present(self):
        # The heart of #125: the body says Closes, GitHub made no link, so the
        # board will not move. A text search would have passed this.
        errors, _ = m.check("### Issue type\nTask\n\nCloses #116\n", [], [])
        self.assertTrue(any("no issue reference github recognises" in e.lower() for e in errors))

    def test_that_failure_explains_the_code_span_cause(self):
        errors, _ = m.check("### Issue type\nTask\n\n`Closes #116`\n", [], [])
        # The keyword is in the body but stripped from prose, so no hint fires.
        self.assertTrue(any("no issue reference" in e.lower() for e in errors))

    def test_keyword_outside_code_with_no_github_link_gets_the_hint(self):
        errors, _ = m.check("### Issue type\nTask\n\nCloses #116\n", [], [])
        self.assertTrue(any("plain text" in e for e in errors))

    def test_refs_passes_when_github_reports_nothing(self):
        errors, notes = m.check("### Issue type\nTask\n\nRefs #116\n", [], [])
        self.assertEqual(errors, [])
        self.assertIn("nothing closes on merge", notes[0])

    def test_no_reference_at_all_fails(self):
        errors, _ = m.check("### Issue type\nTask\n\nNothing here.\n", [], [])
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

    def test_degraded_mode_says_it_is_not_verified(self):
        errors, notes = m.check("### Issue type\nTask\n\nCloses #9\n", [], None)
        self.assertEqual(errors, [])
        self.assertIn("NOT verified", notes[0])

    def test_degraded_mode_still_fails_a_body_with_no_reference(self):
        errors, _ = m.check("### Issue type\nTask\n\nNothing.\n", [], None)
        self.assertTrue(errors)


class CodeStripping(unittest.TestCase):
    """The four shapes that defeated the previous fix, plus the ordering."""

    def test_unterminated_fence_swallows_what_follows(self):
        self.assertNotIn("Closes", m.strip_code("Text\n```\noutput\nCloses #42\n"))

    def test_double_backtick_span_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("See ``Closes #6`` here."))

    def test_quad_fence_with_inner_run_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("````\n``` ex\nCloses #1\n````"))

    def test_indented_block_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n    Closes #999\n"))

    def test_tab_indented_block_is_stripped(self):
        self.assertNotIn("Closes", m.strip_code("Refs #1\n\n\tCloses #999\n"))

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
        body = AGENT_BODY.replace("| Model | claude-opus-5 |", "| Model |  |")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("Model" in e for e in errors))

    def test_agent_body_with_hollow_not_verified_fails(self):
        body = AGENT_BODY.replace("The relay was not exercised.", "nothing")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("Not verified" in e for e in errors))

    def test_agent_body_without_a_fence_fails(self):
        body = AGENT_BODY.replace("```\nraw output\n```", "raw output")
        errors, _ = m.check(body, ["by:agent"], [1])
        self.assertTrue(any("fenced code block" in e for e in errors))

    def test_the_fence_rule_reads_the_unstripped_body(self):
        # If it read stripped prose the fence would be gone and this could never
        # pass — the reason `check` keeps two strings.
        errors, _ = m.check(AGENT_BODY, ["by:agent"], [1])
        self.assertFalse(any("fenced code block" in e for e in errors))

    def test_human_body_is_not_held_to_agent_rules(self):
        errors, _ = m.check("### Issue type\nBug\n\nRefs #1\n", [], [])
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)

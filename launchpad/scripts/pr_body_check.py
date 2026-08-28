#!/usr/bin/env python3
"""Validate a pull request body against this fork's conventions.

WHY THIS IS A SCRIPT AND NOT INLINE YAML

It used to be a Python heredoc inside `.github/workflows/launchpad-pr-check.yml`.
Two consequences, both real:

  1. NOTHING COULD TEST IT. Logic embedded in YAML is not importable, so the only
     way to check a change was to open a PR and watch. The suite written for
     issue #125 had to copy the regexes by hand, which meant it would have passed
     unchanged if the real check were reverted or replaced with `sys.exit(0)`.
  2. THE MARKDOWN PARSING WAS WRONG, AND QUIETLY SO. See below.

WHY GITHUB ANSWERS THE CLOSING QUESTION, NOT A REGEX

The check's purpose is "will the board update when this merges?". A regex over the
body cannot answer that, because GitHub ignores references written inside code and
CommonMark has more code forms than anyone enumerates on the first attempt.
Measured against the previous fix on 2026-08-12, all four of these smuggled a
keyword past it while GitHub created no link:

    an unterminated ``` fence          (the template mandates pasted output, so
                                        a missing closing fence is the single most
                                        likely authoring slip in this repo)
    a ``double-backtick`` span         (no run-length matching)
    a ````quad fence```` with an
      inner shorter run                (non-greedy match closes early)
    a 4-space indented block           (not a delimiter the regex knew about)

So the authoritative answer comes from GitHub's own `closingIssuesReferences`,
passed in by the workflow. There is no markdown to misparse.

`Refs #n` still needs a text search, because it is a convention of ours that
GitHub knows nothing about. A false positive there is cheap: `Refs` makes no claim
that the board will move, so the worst case is a PR that named its issue in an
unusual place. The fence stripping below is therefore best-effort by design, and
its one hard case — the unterminated fence — is handled.

ABSENCE IS NOT EVIDENCE

`CLOSING_REFS` unset means the query did not run or failed. That is NOT the same as
"GitHub found no closing reference", and it must never read as either a pass or a
silent failure: the check degrades to a text search and says so on stdout, so a
reader can tell a verified result from a guessed one.

Usage:
    BODY=... LABELS='["by:agent"]' CLOSING_REFS='[116]' python3 pr_body_check.py

Exit: 0 = the body is acceptable, 1 = it is not.
"""

from __future__ import annotations

import json
import os
import re
import sys

CLOSING_RE = re.compile(r"\b(Closes|Fixes|Resolves)\s+#\d+", re.I)
REFS_RE = re.compile(r"\bRefs\s+#\d+", re.I)
ISSUE_REF_RE = re.compile(r"#(\d+)")
URL_RE = re.compile(r"https?://\S+")

# `Feature` was missing here until 2026-08-28, which failed every Feature PR with
# "Issue type must be one of [...]" while `.github/ISSUE_TEMPLATE/07-feature.yml` and
# AGENTS.md's own type table both named it. ADR-0052 makes Feature the primary PR type,
# so the omission went from a papercut to a blocker.
ISSUE_TYPES = frozenset({"PRD", "Feature", "Task", "Enhancement", "Bug", "ADR"})
PROVENANCE_FIELDS = ("Harness / provider", "Model", "Initiating human")
EMPTY_NOT_VERIFIED = frozenset({"nothing", "none", "n/a", ""})

# A section whose whole text is one of these is unfilled, not answered.
PLACEHOLDER = frozenset({"", "none", "n/a", "nothing", "tbd", "todo"})

# ADR-0052 parts C and E, as numbers rather than judgements.
CAP_ADDITIONS = 1500
CAP_FILES = 10
DEFERRED_CEILING = 5


def strip_comments(body: str) -> str:
    """Remove HTML comments so unfilled template placeholders never count."""
    return re.sub(r"<!--.*?-->", "", body, flags=re.S)


BLOCKQUOTE = re.compile(r"^(?: {0,3}>)+ ?")
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})")
# A closing fence carries nothing but its run and trailing whitespace. An opener
# may carry an info string (```python); a closer may not, so they need different
# patterns — accepting junk after a closing run ends the block early and starts a
# spurious new one, which both leaks code as prose and swallows real prose as code.
FENCE_CLOSE = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*$")


def _strip_fences(text: str) -> str:
    """Drop fenced blocks, honouring CommonMark's run-length rule.

    A regex cannot do this. A closing fence must be *at least as long* as the one
    that opened it, and `re` has no "backreference, or longer" — so a non-greedy
    ```` ```.*?``` ```` closes early on any shorter run inside a longer fence, which
    is how a ````quad fence```` wrapping a ``` example leaked a keyword into prose.
    An unterminated fence runs to the end of the document, so it consumes the rest.

    A fence must also close with the character it opened with: ``` is not closed by
    ~~~, however long the run.

    Blockquote markers are stripped before matching, so a fence quoted with `> `
    is recognised. Without that, quoting someone else's fenced output left its
    contents standing as prose.

    A FENCE OPENED INSIDE A QUOTE CLOSES WITH THE QUOTE. CommonMark ends a block
    quote lazily — a line with no `>` marker (a blank line included, since a bare
    `>` strips to empty) closes it, the same way a blank line ends one at the top
    level. A fence keeps no memory of the container it opened in, so one opened
    with `> ` and never explicitly closed used to stay open to the end of the
    document once the quote ended, silently consuming every line after it —
    including a `Refs #<n>` GitHub would render as ordinary prose (#145).
    """
    out: list[str] = []
    fence: str | None = None
    fence_in_quote = False
    for line in text.splitlines(keepends=True):
        if fence is not None and fence_in_quote and not BLOCKQUOTE.match(line):
            # The quote that contained this fence just ended. The fence closes
            # with it, so this line is evaluated fresh below — as prose, or as
            # the start of a new fence — not as content of the old one.
            fence, fence_in_quote = None, False

        probe = BLOCKQUOTE.sub("", line)
        if fence is None:
            m = FENCE_OPEN.match(probe)
            if m:
                fence = m.group(1)
                fence_in_quote = bool(BLOCKQUOTE.match(line))
                continue
            out.append(line)
        else:
            closer = FENCE_CLOSE.match(probe)
            if closer and closer.group(1)[0] == fence[0] and len(closer.group(1)) >= len(fence):
                fence, fence_in_quote = None, False
    return "".join(out)


def strip_code(text: str) -> str:
    """Best-effort removal of code so a text search sees prose only.

    Fences go first: run the inline-span pattern first and it eats a fence's
    delimiters piecemeal, leaving the fence body behind as prose.

    DELIBERATELY NOT HANDLED: four-space indented code blocks. Stripping every
    line that starts with four spaces looked right and was worse than the bug it
    was meant to help — CommonMark ties the four-space rule to the *container's*
    content column, so ordinary markdown that GitHub renders as prose was being
    deleted:

        - part of a larger plan:
            - Refs #116 covers the follow-up

    That reference vanished and the check rejected a compliant PR for having no
    reference at all. A false block is worse than the false pass this file exists
    to fix: the false pass merely failed to catch something, while this actively
    obstructed an author who had done nothing wrong. Since the closing question is
    now answered by GitHub, the only cost of not stripping indented code is a
    `Refs` written inside an indented block being counted, which claims nothing
    about the board.
    """
    out = _strip_fences(text)
    # Run-length matched spans: the backreference forces the closing run to equal
    # the opening one, so ``x`` is one span rather than two empty ones around x.
    return re.sub(r"(`+)([^\n]*?)\1", "", out)


def section(visible: str, name: str) -> str | None:
    """Text under a '### name' heading, up to the next heading."""
    m = re.search(
        rf"^#+\s*{re.escape(name)}\s*$(.*?)(?=^#+\s|\Z)",
        visible,
        flags=re.M | re.S,
    )
    return m.group(1).strip() if m else None


def parse_closing_refs(raw: str | None) -> list[int] | None:
    """GitHub's answer, or None when we do not have one.

    None is returned for an unset, blank or unparseable value. It means "unknown",
    never "none found" — the caller degrades and says so rather than deciding.
    """
    if raw is None or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, list):
        return None
    # `bool` subclasses `int`, so a JSON `true` would otherwise survive as 1 and be
    # printed as "#True". Not reachable through the workflow's jq expression today,
    # which yields plain integers, but a hand-set CLOSING_REFS could hit it.
    return [n for n in parsed if isinstance(n, int) and not isinstance(n, bool)]


def check_reference(prose: str, closing_refs: list[int] | None) -> tuple[list[str], str]:
    """Does this PR name an issue? Returns (errors, one line about how we know)."""
    refs = bool(REFS_RE.search(prose))

    if closing_refs is None:
        # Degraded: no authoritative answer, so fall back to the text search that
        # this script exists to stop relying on. Say so out loud, and say WHICH form
        # matched — one identical note for both was untestable and told a reader
        # less than it appeared to.
        if CLOSING_RE.search(prose):
            return [], (
                "reference: a closing keyword was found by text search only — "
                "GitHub's answer was unavailable, so 'the board updates on merge' "
                "is NOT verified"
            )
        if refs:
            return [], (
                "reference: 'Refs' found by text search; GitHub's answer was "
                "unavailable, but nothing was expected to close anyway"
            )
        return [
            "No issue reference found. Use 'Closes #<n>' when this PR completes the "
            "issue, or 'Refs #<n>' when it does not."
        ], "reference: absent by text search; GitHub's answer was unavailable"

    if closing_refs:
        joined = ", ".join(f"#{n}" for n in closing_refs)
        return [], f"reference: GitHub will close {joined} on merge"
    if refs:
        return [], "reference: 'Refs' present; nothing closes on merge, as intended"

    hint = ""
    if CLOSING_RE.search(prose):
        hint = (
            " A closing keyword appears in the body but GitHub created no link from "
            "it, which happens when it sits inside a code span or fenced block — "
            "write it as plain text."
        )
    return [
        "No issue reference GitHub recognises. Use 'Closes #<n>' when this PR "
        "completes the issue so the board updates on merge, or 'Refs #<n>' when it "
        "does not." + hint
    ], "reference: none — GitHub reports no closing link and no 'Refs' was found"


def check_batch(
    visible: str, closing_refs: list[int] | None, feature_children: list[int] | None
) -> tuple[list[str], int | None, list[str]]:
    """ADR-0052: a batch PR names one Feature, and closes only that Feature's children.

    A single-issue PR is still legal and writes "N/A" in the Feature section, so this
    only bites once a PR closes more than one issue — which is exactly when getting the
    parentage wrong stops being obvious to a reader.

    `feature_children` is supplied by the workflow, the same way `closing_refs` is, so
    this stays a pure function with no network. None means "we were not told" — and for a
    NAMED Feature that is now an error, not a note. ADR-0052 removes the second human, so
    a membership check that passes because it could not run is a bypass.

    Returns (errors, feature_number_or_None, notes). The number is returned so the
    deferred-blocker rules in `check_delegated` can be checked against the same Feature
    without parsing the section twice.
    """
    errors: list[str] = []
    notes: list[str] = []

    feature = section(visible, "Feature")
    named = ISSUE_REF_RE.findall(feature or "")
    multi = closing_refs is not None and len(closing_refs) > 1

    if feature is None:
        errors.append("Missing '### Feature' section. ADR-0052 makes a Feature the PR unit.")
        return errors, None, notes

    if feature.strip().lower().startswith("n/a"):
        if multi:
            errors.append(
                f"'Feature' says N/A but this PR closes {len(closing_refs)} issues. "
                "A batch must name the Feature its children belong to."
            )
        elif closing_refs is None:
            # Degraded: we cannot count what GitHub will close, so we cannot know this
            # is the single-issue case the N/A answer claims. Say so; do not assert it.
            notes.append(
                "batch: 'Feature' says N/A, but GitHub's closing list was unavailable, "
                "so 'this is a single-issue PR' is NOT verified"
            )
        else:
            notes.append("batch: single-issue PR, no Feature required")
        return errors, None, notes

    if len(named) != 1:
        errors.append(
            f"'Feature' must name exactly one issue as '#<n>'. Found {len(named)}."
        )
        return errors, None, notes

    fnum = int(named[0])

    if feature_children is None:
        # Fail closed, deliberately. Under ADR-0052 an agent may merge with no second
        # human, so a membership check that passes when it could not run is a bypass
        # wearing a warning's clothes. A named Feature whose children cannot be read is
        # an error; re-run once the API answers.
        errors.append(
            f"Feature #{fnum} is named but its child list could not be read, so batch "
            "membership is unverifiable. This fails closed: with no second human in the "
            "merge path an unverified batch is not an acceptable pass. Re-run the check."
        )
        return errors, fnum, notes

    allowed = set(feature_children) | {fnum}
    strays = sorted(set(closing_refs or []) - allowed)
    if strays:
        joined = ", ".join(f"#{n}" for n in strays)
        errors.append(
            f"{joined} closed by this PR but not a child of Feature #{fnum}. Either "
            "re-parent them under that Feature, or split them into their own batch."
        )
    elif closing_refs is None:
        notes.append(
            f"batch: Feature #{fnum} named and its children read, but GitHub's closing "
            "list was unavailable, so membership is NOT verified"
        )
    else:
        notes.append(
            f"batch: all {len(closing_refs)} closed issue(s) are children of "
            f"Feature #{fnum}"
        )
    return errors, fnum, notes


def parse_int(raw: str | None) -> int | None:
    """A count from the workflow, or None when we were not told. Never a guess."""
    if raw is None or not raw.strip():
        return None
    try:
        return int(raw.strip())
    except ValueError:
        return None


def looks_agent_authored(visible: str) -> bool:
    """Does the BODY betray an agent, whatever the labels say?

    The `by:agent` label used to be the only switch into the stricter checks, which made
    removing one label enough to drop provenance, Not verified, Authority, Deferred
    blockers and (in infra) Host steps all at once. A label is metadata anyone can edit
    after the fact; the body is the artifact under review. So the label is now one signal
    of three, not the gate.

    Fully evading this means also deleting the provenance table and the Authority claim —
    at which point the pull request visibly carries no agent evidence at all, which is a
    much louder act than unticking a label and is exactly what a reviewer would notice.
    """
    if any(re.search(rf"\|\s*{re.escape(f)}\s*\|", visible) for f in PROVENANCE_FIELDS):
        return True
    auth = section(visible, "Authority")
    if auth is not None:
        text = auth.strip().lower()
        if text and text not in PLACEHOLDER and not text.startswith("n/a"):
            return True
    return False


def check_cap(
    closing_refs: list[int] | None, additions: int | None, changed_files: int | None
) -> tuple[list[str], list[str]]:
    """ADR-0052 part C: a batch is capped at 1,500 added lines or 10 changed files.

    The cap exists because ADR-0052 rejected unbatched review on the grounds that a giant
    PR makes the human gate a rubber stamp. Left in prose it reproduced the thing it was
    meant to prevent, so it is enforced here from the numbers GitHub already reports.

    Scope: this applies to BATCHES — a PR closing more than one issue. A single-issue PR
    is not what part C bounds, and capping it would block ordinary large-but-focused work
    (a corpus node, a ported script) that the decision says nothing about.
    """
    errors: list[str] = []
    notes: list[str] = []

    if closing_refs is None or len(closing_refs) <= 1:
        return errors, notes
    if additions is None or changed_files is None:
        notes.append(
            "cap: batch size was not supplied, so the 1,500-line / 10-file cap is "
            "NOT verified"
        )
        return errors, notes

    if additions > CAP_ADDITIONS or changed_files > CAP_FILES:
        errors.append(
            f"Batch exceeds the cap: +{additions} lines across {changed_files} files "
            f"(cap {CAP_ADDITIONS} lines or {CAP_FILES} files, whichever binds first). "
            "Split the Feature into sequential batch PRs — ADR-0052 part C."
        )
    else:
        notes.append(
            f"cap: batch is +{additions} lines across {changed_files} files, within "
            f"{CAP_ADDITIONS}/{CAP_FILES}"
        )
    return errors, notes


def check_delegated(
    visible: str,
    closing_refs: list[int] | None = None,
    feature_num: int | None = None,
    feature_children: list[int] | None = None,
) -> list[str]:
    """ADR-0052 part A: an agent-exercised approval or merge must show its warrant.

    The quote itself cannot be verified by any script — nothing here proves the text
    matches what a human said. What this does enforce is that a warrant was offered at
    all, in a shape a reader can follow to its source.
    """
    errors: list[str] = []

    auth = section(visible, "Authority")
    if auth is None:
        errors.append(
            "by:agent PR missing '### Authority' section. State the instruction you "
            "acted on, or 'N/A - approved by a human directly'."
        )
    elif auth.strip().lower() in PLACEHOLDER:
        errors.append(
            "'Authority' is empty. Either quote the instruction and link where it was "
            "given, or write 'N/A - approved by a human directly'."
        )
    elif not auth.strip().lower().startswith("n/a"):
        if not any(line.lstrip().startswith(">") for line in auth.splitlines()):
            errors.append(
                "'Authority' claims delegated authority but quotes nothing. Quote the "
                "human's instruction verbatim as a blockquote."
            )
        # A link is welcome but not required. While the agent runs under the human's
        # token, any comment it could link is authored by the same account as this body,
        # so demanding one bought ceremony rather than attribution. What is required is
        # that the instruction is quoted here and the person who gave it is named in the
        # provenance table, which the agent-mode checks above already enforce.

    deferred = section(visible, "Deferred blockers")
    if deferred is None:
        errors.append(
            "by:agent PR missing '### Deferred blockers' section. List them, or 'none'."
        )
        return errors

    if deferred.strip().lower() in PLACEHOLDER - {"none", "n/a"}:
        # An empty section is not the same answer as "none". Authority already draws
        # this line; without it here, deleting the content passes.
        errors.append(
            "'Deferred blockers' is empty. Write 'none', or list the issues as "
            "'#<n> - description'."
        )
        return errors

    if deferred.strip().lower() in {"none", "n/a"}:
        return errors

    bad = [
        ln.strip()
        for ln in deferred.splitlines()
        if ln.strip() and not ISSUE_REF_RE.search(ln)
    ]
    if bad:
        errors.append(
            "Every 'Deferred blockers' line must reference its issue as '#<n>'. "
            f"Offending line: {bad[0][:60]!r}"
        )

    listed = sorted({int(n) for n in ISSUE_REF_RE.findall(deferred)})

    # Part E, first half: a Feature may not close while it holds open deferred blockers.
    # This is the only part of E that is checkable at PR time, and it is the parallel-queue
    # failure the rule exists to prevent — GitHub closes the Feature the moment this merges.
    if feature_num is not None and closing_refs and feature_num in closing_refs and listed:
        joined = ", ".join(f"#{n}" for n in listed)
        errors.append(
            f"This PR closes Feature #{feature_num} while deferring {joined}. ADR-0052 "
            "part E: a Feature may not close while it holds open deferred blockers. "
            "Either fix them here, or drop the Feature from the closing keywords and "
            "close it once they are done."
        )

    # Part E, second half: the ceiling.
    if len(listed) > DEFERRED_CEILING:
        errors.append(
            f"{len(listed)} deferred blockers exceeds the ceiling of {DEFERRED_CEILING} "
            "(ADR-0052 part E). Clear some before adding more."
        )

    # Part D: a deferred blocker is filed as a child of this PR's Feature. When the child
    # list is known, an issue outside it is either mis-parented or invented.
    if feature_num is not None and feature_children is not None:
        allowed = set(feature_children)
        outside = sorted(n for n in listed if n not in allowed)
        if outside:
            joined = ", ".join(f"#{n}" for n in outside)
            errors.append(
                f"{joined} listed as deferred blockers but not children of Feature "
                f"#{feature_num}. ADR-0052 part D requires them parented to it, so the "
                "Feature cannot close while they are open."
            )
    return errors


def check(
    body: str,
    labels: list[str],
    closing_refs: list[int] | None,
    feature_children: list[int] | None = None,
    additions: int | None = None,
    changed_files: int | None = None,
) -> tuple[list[str], list[str]]:
    """Return (errors, notes). Empty errors means the body is acceptable."""
    visible = strip_comments(body)
    prose = strip_code(visible)
    labelled_agent = "by:agent" in labels
    body_says_agent = looks_agent_authored(visible)
    is_agent = labelled_agent or body_says_agent
    errors: list[str] = []
    notes: list[str] = []

    if not visible.strip():
        errors.append("PR body is empty. Use the PR template.")

    ref_errors, ref_note = check_reference(prose, closing_refs)
    errors.extend(ref_errors)
    notes.append(ref_note)

    batch_errors, feature_num, batch_notes = check_batch(
        visible, closing_refs, feature_children
    )
    errors.extend(batch_errors)
    notes.extend(batch_notes)

    cap_errors, cap_notes = check_cap(closing_refs, additions, changed_files)
    errors.extend(cap_errors)
    notes.extend(cap_notes)

    itype = section(visible, "Issue type")
    if not itype:
        errors.append("Missing '### Issue type' section.")
    elif not any(v.lower() in itype.lower() for v in ISSUE_TYPES):
        errors.append(f"Issue type must be one of {sorted(ISSUE_TYPES)}. Found: {itype!r}")

    if body_says_agent and not labelled_agent:
        # Rule 3 requires the label, and its absence is the shape a stripped label leaves.
        # The strict checks already ran above regardless; this makes the omission visible
        # rather than letting the body and the metadata disagree quietly.
        errors.append(
            "This body carries agent provenance or an Authority claim but no 'by:agent' "
            "label. Add it. Removing the label does not remove the requirements — they "
            "are keyed on the body now, not only on metadata."
        )

    if is_agent:
        for field in PROVENANCE_FIELDS:
            m = re.search(rf"\|\s*{re.escape(field)}\s*\|(.*?)\|", visible)
            if not m or not m.group(1).strip():
                errors.append(f"by:agent PR missing provenance value for '{field}'.")

        nv = section(visible, "Not verified")
        if not nv:
            errors.append("by:agent PR missing '### Not verified' section.")
        elif nv.lower().strip(" .") in EMPTY_NOT_VERIFIED:
            errors.append(
                "'Not verified' must name something specific. "
                "There is always something that was not checked."
            )

        # Deliberately reads `visible`, not `prose`: this rule REQUIRES a fence to
        # be present, so stripping code first would make it unsatisfiable.
        if "```" not in visible:
            errors.append("by:agent PR must paste raw command output in a fenced code block.")

        errors.extend(
            check_delegated(visible, closing_refs, feature_num, feature_children)
        )

    return errors, notes


def main() -> int:
    body = os.environ.get("BODY") or ""
    try:
        labels = json.loads(os.environ.get("LABELS") or "[]")
    except json.JSONDecodeError:
        labels = []
    closing_refs = parse_closing_refs(os.environ.get("CLOSING_REFS"))
    feature_children = parse_closing_refs(os.environ.get("FEATURE_CHILDREN"))
    additions = parse_int(os.environ.get("PR_ADDITIONS"))
    changed_files = parse_int(os.environ.get("PR_CHANGED_FILES"))

    errors, notes = check(
        body, labels, closing_refs, feature_children, additions, changed_files
    )
    for note in notes:
        print(f"  {note}")

    if errors:
        print("\nPR body check failed:\n")
        for e in errors:
            print(f"  - {e}")
        print("\nHuman PRs: .github/PULL_REQUEST_TEMPLATE.md")
        print("Agent PRs: launchpad/AGENT_PR_TEMPLATE.md")
        return 1

    kind = "agent" if "by:agent" in labels else "human"
    print(f"\nPR body check passed. ({kind})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

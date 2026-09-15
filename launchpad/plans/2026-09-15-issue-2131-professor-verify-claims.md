Issue #2131 — feature: Professor claim-verification gate — verify-claims and roster-name dispatch

Stated size: none — this repo's issue templates carry no Size line → cap: 12 steps

Self-sized "more than an hour" because the Feature's six child tasks (#2137–#2142) touch
four SKILL.md files, one Python module, its test harness, and two demonstration runs that
each need real model dispatches. Sized here rather than blocked on, matching every prior
plan in launchpad/plans/.

Planned on branch `feature/2131-professor-verify-claims`, worktree
`__worktrees/feature-2131-verify-claims`, off `origin/launchpad` at `5089c83fb6`.

DECIDED 2026-09-15, by Serina — the re-dispatch observable (was OPEN item 1)

  Each pass stamps a fresh per-pass run identifier alongside its verdicts. A verdict
  carrying a prior pass's identifier is a replay, not a re-run. Chosen over comparing the
  two passes' raw stdout, which fails against the exact thing #2139 asks it to detect: a
  deterministic verifier returning byte-identical output twice is the healthy case, so
  matching bytes cannot tell a real re-run from a cache hit.

  Named limitation, to be written into the skill rather than left to read as solved: a
  fresh identifier proves a dispatch happened, not that it was independent of the first
  pass's reasoning. An agent could re-dispatch carrying the first pass's context and still
  stamp a new identifier. This is the same shape of honest limit the skill already records
  for claim identification.

  Lands in verify-claims/SKILL.md at step 2 of this plan, and in the design doc at
  step 11.

DECIDED 2026-09-15, by Serina — the roster-names finding shape (was OPEN item 2)

  screen-content keeps emitting disposition `redact` for every roster-names candidate,
  and gains an explicit flag on the finding marking it as one a dispatch must resolve.
  The skill dispatches on that flag and drops ATTRIBUTION candidates from its outcome.

  This is the only option that serves both consumers. A session following
  screen-sensitive/SKILL.md sees the flag, dispatches, and un-flags attribution names, so
  #2140's "not flagged at all" holds. Anything reading screen-content's JSON directly —
  CI, a script, the scheduled workflow — never dispatches and still sees `redact`, so
  #2110's fail-closed floor holds too. Replacing `redact` with a neutral needs-dispatch
  disposition was rejected: it reintroduces the exact fail-open shape #2110 closed five
  days earlier, where a consumer has no defined action and can drop the finding silently.

  Accepted cost, stated rather than discovered later: the finding shape is a contract, and
  this adds a field to it. check_professor.py must assert the new field, and every
  consumer of that JSON has to tolerate it.

ALREADY TRUE  (verified against the worktree, not against notes)

  This section most changes the shape of this Feature. Three of the six child issues are
  partly already satisfied by text that shipped in Phase 1 and in PR #2133.

  skills/verify-claims/SKILL.md exists and is 179 lines. It already states:
    - the mandatory/unskippable decision and the gate's third position (lines 8–25)
    - $PROFESSOR_VERIFIER_CMD as the dispatch mechanism, no suite-applied default,
      `claude --print` named only as recommended (lines 27–38)
    - the run-twice decision and that the doubled per-claim cost is accepted (lines
      40–46) — this is #2139's criterion 4, already met
    - UNSOURCED decided in step 1, before any dispatch (lines 70–75) — #2137's
      criterion 5, already met
    - exactly what each dispatch receives and the explicit withhold list (lines 77–91)
      — #2137's criterion 2, already met
    - the three post-dispatch verdicts and the never-round-up rule (lines 93–104)
    - blocking with no partial-write path, and the finding shape (lines 106–121)
    - step 4, the final independent pass (lines 123–132) — #2139's criterion 1, met on
      this file, not on draft-page/update-page

  skills/screen-sensitive/SKILL.md already documents the whole roster-names dispatch
  protocol — ATTRIBUTION not flagged, ROSTER_DATA → redact, AMBIGUOUS → redact (lines
  48–80) — and already merges those verdicts into the single outcome (lines 137, 147).
  #2140's criteria 1, 2 and 3 are text-complete. What remains on this file is the interim
  paragraph at lines 82–100, which #2140 criterion 4 requires removing.

  tools/professor_lib/localcmd.py lines 1316–1348 emits every roster-names candidate with
  a hardcoded "disposition": "redact" and a message reading "Phase 1b, #2131, not yet
  built". That message becomes false the moment this Feature lands.

  skills/draft-page/SKILL.md does not wire the gate. Its only mention of verify-claims is
  line 227, inside a history note — not its procedure. skills/update-page/SKILL.md
  contains zero occurrences of verify-claims.

  The fail-loud shape #2137 must match is real and already asserted verbatim.
  tools/professor.py:63 emits the $PROFESSOR_PACK_ROOT unset message;
  tools/check_professor.py:205 asserts that exact string, and lines 229–252 prove a
  non-zero exit when the variable is set to empty.

  Nothing in the pack parses verifier stdout. No file states what output counts as which
  verdict. This is the single largest genuine gap in the Feature.

  Dispatch is deliberately not a professor.py subcommand (§4's diagram note), so most of
  this Feature is procedure text plus one Python change — not a code build.

STEP 1  verify-claims/SKILL.md — the three missing contract pieces          [independent]
        Add, to the existing step 2: the verbatim message emitted when
        $PROFESSOR_VERIFIER_CMD is unset, modelled on professor.py:63's
        $PROFESSOR_PACK_ROOT wording; the exact stdout form that counts as each of
        SUPPORTED, NOT_SUPPORTED, PARTIALLY_SUPPORTED; and the outcome when stdout
        matches none of them.
        done when: verify-claims/SKILL.md contains a quoted unset message naming
        $PROFESSOR_VERIFIER_CMD; a stated recognition rule a reader could apply to a raw
        stdout string to pick exactly one of the three verdicts; and an explicit
        non-matching outcome whose text is not SUPPORTED. Closes #2137 criteria 1, 3, 4.

STEP 2  verify-claims/SKILL.md — the re-dispatch observable                   [needs 1]
        State, in step 4, that each pass stamps a fresh per-pass run identifier alongside
        its verdicts, and that a verdict carrying a prior pass's identifier is a replay
        rather than a re-run. Name the limitation in the same breath: a fresh identifier
        proves a dispatch happened, not that it was independent of the first pass's
        reasoning. Per the DECIDED note above.
        done when: step 4 names the per-pass run identifier as the observable, states
        what an inspector looks at to tell a re-run from a replay, and names the
        independence limitation rather than implying it is solved. Closes #2139's
        criterion 3.

STEP 3  First real dispatch, end to end                        [needs 1]  ← RUNS HERE
        Configure $PROFESSOR_VERIFIER_CMD to a real headless CLI. Take one real behaviour
        claim about a file in this repository, with a real commit+path+span citation, and
        run step 1–2's procedure by hand: dispatch, capture raw stdout, apply STEP 1's
        recognition rule.
        done when: a transcript records the configured command, the claim sentence, the
        cited span, the verbatim stdout, and which verdict the recognition rule assigns
        it — with the verdict derived from the rule, not asserted alongside it.

STEP 4  draft-page/SKILL.md — third gate and final pass                       [needs 2]
        Add verify-claims to the procedure as the third gate after check-page and
        screen-sensitive; state that any non-SUPPORTED verdict on any claim stops the
        write with no partial-write path; state the finding shape, matching
        screen-sensitive's; state the zero-behaviour-claims case explicitly; and add the
        final independent pass as its own last step before the write, with the
        first-is-advisory / second-is-the-gate-of-record reasoning.
        done when: `grep -c verify-claims draft-page/SKILL.md` exceeds its current 1, the
        gate appears in the numbered procedure rather than only in the history note at
        line 227, and all four of #2138's criteria plus #2139's criteria 1–2 are each
        traceable to a line in this file.

STEP 5  update-page/SKILL.md — third gate and final pass                      [needs 2]
        The same as the previous step, against a file that currently has zero mentions.
        done when: the same four #2138 criteria and #2139 criteria 1–2 are traceable to
        lines in update-page/SKILL.md, and the gate's position is stated as after
        check-page and screen-sensitive, never parallel.

STEP 6  screen-sensitive/SKILL.md — retire the interim rule                   [needs 1]
        Delete the interim paragraph at lines 82–100 and bind the already-documented
        dispatch protocol to the now-concrete contract, so the same recognition rule
        covers ATTRIBUTION/ROSTER_DATA/AMBIGUOUS stdout.
        State that the skill dispatches on the finding's requires-dispatch flag, and that
        an ATTRIBUTION verdict removes the candidate from this skill's outcome even
        though screen-content reported it as redact — per the DECIDED note above.
        done when: no paragraph in the file claims the dispatch "does not exist yet";
        #2110 no longer appears as a live interim rule; the file names the
        requires-dispatch flag as what it dispatches on and states that ATTRIBUTION
        overrides the script's redact; and the file states what happens when a
        roster-names dispatch returns unrecognised stdout. Closes #2140's criterion 4.

STEP 7  localcmd.py roster-names finding, and its regression coverage         [needs 6]
        Per the DECIDED note above: keep disposition `redact`, add the explicit
        requires-dispatch flag to the roster-names finding at lines 1316–1348, and
        rewrite its message so it no longer claims Phase 1b is unbuilt but names the
        dispatch the consumer must now run. Add check_professor.py assertions over both
        the retained disposition and the new field.
        done when: `./tools/professor.py screen-content` on a roster-shaped fixture emits
        a finding that still carries disposition `redact`, carries the requires-dispatch
        flag, and whose message names the dispatch rather than "not yet built";
        `./tools/check_professor.py --offline` reports ALL CHECKS PASSED; and reverting
        either the flag or the retained `redact` alone makes that harness fail — the
        second is the fail-closed floor #2110 established, so it needs its own test, not
        shared coverage with the flag.

STEP 8  Demonstrate all four verdicts                                      [needs 3, 4]
        Construct four genuinely distinct claims against real source — one truly
        supported, one whose citation resolves but does not say what is asserted, one
        supported in part only, one with no citation at all — and record each verdict.
        Then run a draft containing one non-SUPPORTED claim through draft-page's
        procedure and show the write does not happen.
        done when: four distinct claim sentences are recorded with four distinct verdicts
        and their raw stdout; UNSOURCED is reached without a dispatch;
        PARTIALLY_SUPPORTED is not rounded up; and the blocked run shows no file written
        at the target path plus a reported finding. Closes #2141.

STEP 9  Prove $PROFESSOR_VERIFIER_CMD resolution and its unset failure        [needs 4]
        With the variable unset, run a draft down the real draft-page path — not the
        dispatch alone — and capture the failure. Then run the same draft with a
        configured command that is not `claude --print` and show it works.
        done when: the unset run fails with a message naming the variable, is not a
        generic empty-command crash, and does not skip the gate; the non-default run
        returns a real verdict; and both transcripts show the draft path, not a direct
        dispatch call. Closes #2142.

STEP 10 Demonstrate the roster-names dispatch resolving every candidate    [needs 6, 7]
        Run screen-sensitive's full procedure over a page carrying both an attribution
        name and an access-control roster, and show each candidate reaching a resolved
        verdict.
        done when: the attribution name is not flagged in the final outcome, the roster
        name resolves to redact, and no candidate reaches the outcome unresolved. Closes
        #2140's criteria 1–3 and 5 in fact, not only in text.

STEP 11 Reconcile the design doc with what is now true                  [needs 4, 5, 6]
        launchpad/Research/the-professor-skill-suite-redesign.md's phase table still reads
        "| 1 | ... | 0 | Not started |" — Phase 1 shipped on 2026-09-08. Correct Phase 1's
        status, set Phase 1b's, and re-check §6.7 against what the editing steps wrote.
        done when: no phase row in the table contradicts a merged PR; every §N
        cross-reference in the file still resolves to a real heading; and the three
        mermaid diagrams are still present.

PARALLEL
  Steps 4, 5 and 6 may run as parallel subagents — three different SKILL.md files, no
  shared file. Steps 1 and 2 must not: both edit verify-claims/SKILL.md, and step 2's
  wording depends on step 1's contract. Step 7 cannot run beside step 6 — its message
  text must match what step 6 leaves in the skill. Steps 8, 9 and 10 are demonstration
  runs that each consume a wired procedure and must follow it. Step 11 must come last of
  the editing steps; it reports what the others actually wrote.

GATES
  review-skill after steps 4, 5 and 6 (four SKILL.md diffs — the bulk of the Feature).
  review-code and review-tests after step 7, the only Python change; the tests gate
  matters disproportionately here, because PR #2106's review proved four security fixes
  in this exact module had zero regression coverage. review-docs after step 11.
  review-adjudicate over all reviewer output, then review-final over the whole branch.
  Codex runs in the pipeline regardless — standing instruction, and its .raw output gets
  read.

  qa explore mode applies, after step 9. There is a real runtime interface to exercise:
  professor.py's subcommands, and $PROFESSOR_VERIFIER_CMD resolution with hostile values
  — empty string, whitespace, a command that exits non-zero, a command that prints
  nothing, a command that prints a verdict-shaped string inside other prose. That last
  one is exactly what step 1's recognition rule has to survive.

BUDGET
  Step 8. Four genuinely distinct claims is the expensive part, and the issue forecloses
  the cheap version: "one clean pass repeated four ways does not satisfy this."
  PARTIALLY_SUPPORTED is the hardest to construct honestly — it needs a real claim
  asserting several things against a citation that supports only some of them, which
  means reading real source carefully rather than writing a claim to fit a verdict. Every
  claim also costs a real model call, twice, under the run-twice rule.

OPEN
  1. RESOLVED 2026-09-15 by Serina — see the DECIDED note above the steps. Kept numbered
     here so a reader of this section alone does not think it was never asked.
  2. RESOLVED 2026-09-15 by Serina — see the second DECIDED note above the steps. Kept
     numbered here so a reader of this section alone does not think it was never asked.
  3. What #2142's fourth criterion actually demonstrates. "A harness with no headless
     single-turn CLI available is confirmed to fail loudly" — setting the variable to a
     non-existent command is a different failure from a harness that has no such CLI. The
     issue does not say which is being asked for.

LEFT OUT
  Cost work — batching, caching, a cheaper model tier — named by the design doc as a
  build/ops problem and explicitly not a reason to weaken the gate; OPEN item 1 is the
  detector for exactly that. A tools/professor.py subcommand for dispatch, kept out of
  the toolkit's four subcommands by §4's diagram note. Reconciling the remaining stale
  SKILL.md drafts beyond the gate step and the final re-run. Producing a publishable page
  for a real target repo, which is Phase 2 and depends on this Feature. Re-litigating any
  of the decisions Serina resolved on 2026-09-04 — mandatory-and-unskippable, the fourth
  UNSOURCED verdict, the run-twice rule, and no suite-applied default for
  $PROFESSOR_VERIFIER_CMD. A real gap found here gets reported back, not re-decided.

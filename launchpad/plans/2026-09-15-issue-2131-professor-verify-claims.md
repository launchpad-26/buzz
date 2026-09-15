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

DECIDED 2026-09-15, by Serina — candidate identity in a roster-names finding

  Raised by the Codex review of this plan, not by the issues. A roster-names finding
  carries a line number and `match: null`, so two candidates on the same line are
  indistinguishable — a contributor and an allowlisted person, one line apart in column
  only, produce two identical-looking findings. Applying the contributor's ATTRIBUTION
  verdict to the wrong finding silently removes protection from the roster name, on the
  one category that exists to stop an access-control list being published.

  Decision: the finding's location gains column offsets alongside its line number.
  `match` stays null. Offsets are coordinates, not content, so they do not reopen the
  content leak that made `match` null in Phase 1; echoing the matched name back would.
  localcmd.py already computes the span and throws it away at line 1336, so detection
  does not change at all.

  An opaque per-finding id was considered and not taken: it identifies the finding rather
  than the position, so a human reading the JSON still could not tell which name it meant.
  Leaving the shape alone and having the skill track document order was rejected outright
  — correctness would depend on an agent maintaining ordering across a loop.

  Semantics pinned 2026-09-15 after Codex round 2 found "column offsets" underspecified.
  The offsets are LINE-RELATIVE, measured in Unicode characters (not bytes), ZERO-BASED,
  with the end offset EXCLUSIVE — matching the shape approved with this decision
  (`{"line": 42, "col_start": 17, "col_end": 29}`) and the half-open spans
  `_roster_names_matches` already yields. They address the scratch file screening ran
  against, so any edit to that file invalidates them.

  The offsets must also reach the dispatch, not only the finding. Codex round 2: the
  dispatch input is currently "the name and its containing sentence", so the SAME name
  appearing twice in ONE sentence in different roles produces two identical verifier
  inputs even though the two findings now differ. Carrying the offset into the input, and
  requiring the verdict to come back against it, is what closes that; offsets on the
  finding alone do not.

DECIDED 2026-09-15, by Serina — what #2142's fourth criterion proves (was OPEN item 3)

  Two scenarios, both demonstrated. First, $PROFESSOR_VERIFIER_CMD set to a command that
  is not on PATH: fails at launch. Second, and the one that matters, a command that runs
  to completion but is not a headless single-turn verifier — it hangs on input, or returns
  prose containing no recognisable verdict. That second case is the degrade the criterion
  names: nothing crashes, and a careless reading could treat the output as a pass.

  Reading the criterion as the unset case was rejected: that is criterion 1 of the same
  issue, and it would make criterion 4 a duplicate rather than a distinct proof.

  This matters more than it looks, because dispatch deliberately does not go through
  professor_lib/proc.py — §4 keeps it out of the toolkit's four subcommands, so the agent
  runs $PROFESSOR_VERIFIER_CMD by following the skill's prose. proc.py's structured
  handling of a missing binary, a timeout and an OS refusal therefore does not cover
  dispatch at all. Step 1's unrecognised-stdout rule is the only thing standing between
  "the verifier returned something unparseable" and "the claim passed", which is exactly
  what the second scenario tests.

  Honesty requirement on the evidence, so it is not overclaimed: what gets demonstrated is
  the two observable consequences of a harness with no headless single-turn CLI, not the
  absence of one. The design doc names that limitation as real and unsolved; this shows it
  fails safely, not that it has been fixed.

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

  skills/draft-page/SKILL.md wires the gate in ONE mode only — corrected 2026-09-15 after
  the Codex review caught this plan mischaracterising it. Its single mention of
  verify-claims, at line 227, is not a history note: it is inside BASELINE MODE's numbered
  step 5 (lines 225–229), which already names verify-claims and the mandatory final
  independent pass for that mode. The ordinary drafting path is still unwired, so no work
  disappears — but any test phrased as "the gate appears in a numbered procedure rather
  than only in the history note" is false as written, because it already appears in one.
  skills/update-page/SKILL.md contains zero occurrences of verify-claims.

  tools/check_professor.py ALREADY asserts the roster-names redact floor — lines 186–194
  expect `roster-names: redact` for both roster fixtures, and the disposition check covers
  every matching finding. Reverting `redact` already fails the harness today. Do not plan
  that assertion as new work.

  The fail-loud shape #2137 must match is real and already asserted verbatim.
  tools/professor.py:63 emits the $PROFESSOR_PACK_ROOT unset message;
  tools/check_professor.py:205 asserts that exact string, and lines 229–252 prove a
  non-zero exit when the variable is set to empty.

  Nothing in the pack parses verifier stdout. No file states what output counts as which
  verdict. This is the single largest genuine gap in the Feature.

  Dispatch is deliberately not a professor.py subcommand (§4's diagram note), so most of
  this Feature is procedure text plus one Python change — not a code build.

STEP 1  verify-claims/SKILL.md — the dispatch response contract             [independent]
        Add, to the existing step 2: the verbatim message emitted when
        $PROFESSOR_VERIFIER_CMD is unset, modelled on professor.py:63's
        $PROFESSOR_PACK_ROOT wording; a positive acceptance form for each of SUPPORTED,
        NOT_SUPPORTED and PARTIALLY_SUPPORTED; and the outcome for every response that
        does not match one.

        Both reviews made this the plan's most serious finding, independently, so the
        acceptance bar below is deliberately strict.

        SUBSTRING CONTAINMENT IS THE TRAP. `SUPPORTED` is a substring of both
        `NOT_SUPPORTED` and `PARTIALLY_SUPPORTED`. A rule that scans for `SUPPORTED`
        first marks a correctly-formed `NOT_SUPPORTED: the citation contradicts the
        claim` as supported — the gate's own silent-wrongness failure, reproduced inside
        the mechanism built to catch it. Longest-token-first fixes that collision and
        still accepts negated prose such as "this claim cannot be classified as SUPPORTED
        because the citation contradicts it".

        NON-COMPLETION IS NOT A VERDICT. A stdout-only rule never governs how the command
        exited. A verifier can print a perfectly-formed SUPPORTED and then exit non-zero,
        or print it and hang. proc.py's handling does not cover dispatch (§4 keeps it out
        of the four subcommands), so the contract itself has to say what these mean.

        MATCH THE WHOLE RESPONSE, DO NOT SEARCH INSIDE IT. Round 2 of the Codex review
        found the first fix still permitted a parser that finds a standalone SUPPORTED
        line somewhere inside unrelated multi-line output. Forbidding substring
        containment is not enough; the contract needs a grammar the ENTIRE response is
        matched against, so anything outside that grammar is a parse failure by
        construction rather than something to be scanned past. §6.7 and the skill's own
        step 2 already require a verdict plus a one-sentence reason, so the grammar has
        both to describe.

        COMPLETION MUST BE BOUNDED BY SOMETHING. Dispatch does not go through proc.py, so
        no timeout exists unless this contract creates one. "Hangs past the timeout" is
        meaningless until the skill names a concrete default, says who applies it (the
        dispatching agent, since there is no wrapper), and says it is what turns a hang
        into a blocking failure rather than an indefinite wait.

        done when: verify-claims/SKILL.md contains a quoted unset message naming
        $PROFESSOR_VERIFIER_CMD; specifies a complete-response grammar covering the
        verdict and its reason, states that the whole response is matched against it, and
        states that a response not wholly matching is a parse failure — wording a builder
        cannot satisfy with a containment or line-scanning check; pins case sensitivity
        and how leading/trailing whitespace is treated, so two builders cannot read it
        differently; carries at least three explicit REJECTION examples, including
        `NOT_SUPPORTED: ...`, a verdict token inside negating prose, and a valid verdict
        line surrounded by other output; states that a parse failure blocks, naming the
        disposition, and that its text is not SUPPORTED; names a concrete default timeout
        value and the agent as its enforcer; and states that a non-zero exit, that
        timeout, and a response that ends without completing the grammar each block on
        their own, independently of anything stdout contained. Closes #2137 criteria 1,
        3, 4.

STEP 2  verify-claims/SKILL.md — the re-dispatch observable                   [needs 1]
        State, in step 4, that each pass stamps a fresh per-pass run identifier alongside
        its verdicts, and that a verdict carrying a prior pass's identifier is a replay
        rather than a re-run. Name the limitation in the same breath: a fresh identifier
        proves a dispatch happened, not that it was independent of the first pass's
        reasoning. Per the DECIDED note above.
        The identifier must be bound to a recorded invocation, not merely stamped on a
        verdict — otherwise an agent can attach a fresh identifier to cached output and
        satisfy the observable without re-dispatching, which is the exact evasion #2139
        exists to detect.
        A pass is one invocation PER CITED CLAIM, not one invocation. Codex round 2: the
        earlier wording let a pass with several claims and a single fresh dispatch satisfy
        the observable. The reconciliation has to be per claim, in both passes.
        done when: step 4 names the per-pass run identifier as the observable; requires
        one recorded invocation of $PROFESSOR_VERIFIER_CMD per cited claim per pass, so a
        pass whose invocation count does not equal its cited-claim count is detectable;
        states that a verdict bearing an identifier with no matching invocation record for
        that claim in that pass is a replay and blocks; states what an inspector looks at
        to tell a re-run from a replay; and names the independence limitation rather than
        implying it is solved. Closes #2139's criterion 3.

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
        Baseline mode's numbered step 5 already names the gate and the final pass. Wire
        the ORDINARY drafting path, and leave baseline mode consistent with it rather
        than describing the gate two different ways in one file.
        THE FINAL PASS RE-RUNS ALL THREE GATES, NOT JUST THIS ONE. Codex round 2 found
        both skills would otherwise re-run only verify-claims, leaving check-page and
        screen-sensitive holding verdicts about a draft that changed after they ran — so
        a repair made in response to the advisory pass could introduce sensitive content
        after screening and still reach the write. The design doc's §6 flow note (line
        571) already says every gate runs twice; this is fidelity to Serina's 2026-09-04
        decision 9, not a new requirement. It stays inside #2138's "the gate step and its
        sequencing" scope because it IS the sequencing.
        done when: the gate appears in the ordinary drafting path's own numbered
        procedure, cited by line and distinct from baseline mode's step 5 at lines
        225–229; the final pass re-runs check-page, screen-sensitive and verify-claims in
        that order against the finished content; the text states that any edit after that
        sequence invalidates its results and requires the whole sequence again; baseline
        mode's existing wording is confirmed to still agree with the ordinary path's, or
        is updated so it does; and all four of #2138's criteria plus #2139's criteria 1–2
        are each traceable to a line in this file.

STEP 5  update-page/SKILL.md — third gate and final pass                      [needs 2]
        The same as the previous step, against a file that currently has zero mentions —
        including the all-three-gates final pass and the edit-invalidates-the-sequence
        rule, which this file needs just as much and has no baseline-mode head start on.
        done when: the same four #2138 criteria and #2139 criteria 1–2 are traceable to
        lines in update-page/SKILL.md; the gate's position is stated as after check-page
        and screen-sensitive, never parallel; and the final pass re-runs all three gates
        in order against the finished content, with any later edit invalidating it.

STEP 6  screen-sensitive/SKILL.md — retire the interim rule                   [needs 1]
        Delete the interim paragraph at lines 82–100 and bind the already-documented
        dispatch protocol to the now-concrete contract, so the same recognition rule
        covers ATTRIBUTION/ROSTER_DATA/AMBIGUOUS stdout.
        State that the skill dispatches on the finding's requires-dispatch flag, and that
        an ATTRIBUTION verdict removes the candidate from this skill's outcome even
        though screen-content reported it as redact — per the DECIDED note above.
        ONLY a successfully parsed ATTRIBUTION verdict, resolving that exact candidate,
        may remove protection. Every other outcome keeps the underlying redact. Both
        reviews flagged that "state what happens" alone permits a skill to report an
        unresolved candidate separately and drop it from the combined outcome — which is
        #2110's undefined-consumer-action fail-open, reappearing at the skill layer where
        the script's retained redact cannot reach it.
        done when: no paragraph in the file claims the dispatch "does not exist yet";
        #2110 no longer appears as a live interim rule; the file names the
        requires-dispatch flag as what it dispatches on, identifies the candidate by the
        finding's line and column offsets, and carries those offsets into the dispatch
        input so two occurrences of one name in one sentence are distinguishable to the
        verifier; the file states that ATTRIBUTION overrides the script's redact ONLY on
        a dispatch that both COMPLETED and PARSED successfully for that exact candidate;
        and it states the retention rule as a default rather than a list — every outcome
        that is not such an ATTRIBUTION retains the underlying redact and appears in the
        combined outcome, never reported separately and never dropped — with
        unrecognised stdout, a parse failure, a non-zero exit, a timeout, a response that
        ended without completing the grammar, and a candidate never dispatched at all
        each named as instances of that default rather than as its full extent. Closes
        #2140's criterion 4.

STEP 7  localcmd.py roster-names finding, and its regression coverage         [needs 6]
        Per the DECIDED notes above: keep disposition `redact`, add the explicit
        requires-dispatch flag, add column offsets to the finding's location, and rewrite
        its message so it no longer claims Phase 1b is unbuilt but names the dispatch the
        consumer must now run. The finding block is at lines 1316–1348; it already
        computes `name_span` and discards everything but the line number at line 1336, so
        the offsets are available without changing detection at all. `_roster_names_matches`
        yields document-wide Python string spans, so converting to the line-relative form
        the DECIDED note fixes is a computation, not a detection change.
        `match` stays null. The offsets are coordinates, not content — that is precisely
        why they are safe, and why echoing the matched name instead would reopen the
        content-leak Phase 1 closed.
        Do NOT add a retained-redact assertion: check_professor.py lines 186–194 already
        cover it (see ALREADY TRUE). Add coverage for the flag and the offsets only.
        A NEW same-line fixture is required. Corrected 2026-09-15 after Codex round 2 ran
        the matcher: `dispatch-roster-names-two-pairs.md` puts its two candidates on lines
        11 and 16, NOT one line, and check_professor.py:1189 pins those two line numbers.
        It therefore cannot prove same-line candidates are distinguishable, and
        repurposing it would delete existing coverage.
        done when: `./tools/professor.py screen-content` on a roster-shaped fixture emits
        a finding that still carries disposition `redact`, carries the requires-dispatch
        flag, carries offsets in the units the DECIDED note fixes, and whose message names
        the dispatch rather than "not yet built"; a NEW fixture carrying two roster-names
        candidates on a SINGLE line yields two findings that share a line number and
        differ only in their offsets; `dispatch-roster-names-two-pairs.md` and its
        existing line-[11,16] expectations are left untouched; `./tools/check_professor.py
        --offline` reports ALL CHECKS PASSED; and reverting the flag alone, and the
        offsets alone, each make that harness fail.

STEP 8  Demonstrate all four verdicts                                      [needs 3, 4]
        Construct four genuinely distinct claims against real source — one truly
        supported, one whose citation resolves but does not say what is asserted, one
        supported in part only, one with no citation at all — and record each verdict.
        Then run a draft containing one non-SUPPORTED claim through draft-page's
        procedure and show the write does not happen.
        "No file at the target path" proves nothing on its own — it is equally true if an
        earlier gate blocked, or if the run never attempted a write. The evidence has to
        rule those out.
        done when: four distinct claim sentences are recorded with four distinct verdicts
        and their raw stdout; UNSOURCED is reached without a dispatch and its transcript
        shows no invocation for that claim; PARTIALLY_SUPPORTED is not rounded up; and
        for the blocked run — check-page and screen-sensitive are recorded as having
        passed first, so verify-claims is demonstrably what blocked; the target path is
        observed before and after, absent both times; and the reported finding names the
        specific claim and verdict. Closes #2141.

STEP 9  Prove $PROFESSOR_VERIFIER_CMD resolution and its unset failure        [needs 4]
        With the variable unset, run a draft down the real draft-page path — not the
        dispatch alone — and capture the failure. Then run the same draft with a
        configured command that is not `claude --print` and show it works. Then the two
        degrade scenarios from the DECIDED note: a command not on PATH, and a command
        that runs but returns prose carrying no recognisable verdict. Then the two
        non-completion cases step 1's contract now governs: a command that prints a
        well-formed SUPPORTED and exits non-zero, and one that prints it and then hangs
        past the timeout.
        done when: the unset run fails with a message naming the variable, is not a
        generic empty-command crash, and does not skip the gate; the non-default run
        returns a real verdict; the not-on-PATH run fails at launch; the unparseable-
        output run is caught by step 1's recognition rule and blocks rather than passing;
        the non-zero-exit and hanging runs each block despite their stdout reading
        SUPPORTED; all six transcripts show the draft path, not a direct dispatch call;
        and the write-up says it demonstrated the consequences of a harness without a
        headless CLI, not the absence of one. Closes #2142.

STEP 10 Demonstrate the roster-names dispatch resolving every candidate    [needs 6, 7]
        Run screen-sensitive's full procedure over a page carrying both an attribution
        name and an access-control roster, and show each candidate reaching a resolved
        verdict.
        Put both names on ONE line, so the demonstration actually exercises the mapping
        the offsets exist for. "The attribution name is not flagged" is vacuous unless it
        was flagged as a candidate in the first place — start from the raw candidate list
        and reconcile counts.
        THE DEMONSTRATION PAGE MUST USE SYNTHETIC PLACEHOLDER NAMES, and the recorded
        evidence must be content-free. Codex round 2 caught the previous wording requiring
        each candidate's "recorded input" — which is the name and its sentence — in direct
        violation of screen-sensitive/SKILL.md:164–172, which forbids a flagged span
        surviving into a log or a tool call's arguments. Recording it would breach the
        rule this very step exists to demonstrate. Existing fixtures already model the
        way out: `dispatch-roster-names-two-pairs.md` uses "Alex Example" and "Taylor
        Sample" and says in the page itself that they are placeholders.
        done when: the page uses synthetic placeholder names, stated as such in the page;
        screen-content's raw output is recorded first, showing both names as separate
        candidates on the same line with different column offsets; each candidate has its
        own invocation record identified by line and offsets and by the returned verdict,
        with no flagged span reproduced in that record; the count of candidates in equals
        the count resolved out; the attribution name is absent from the final outcome and
        the roster name resolves to redact; and a deliberately unresolvable candidate is
        shown retaining redact rather than being dropped. Closes #2140's criteria 1–3 and
        5 in fact, not only in text.

STEP 11 Reconcile the design doc with what is now true       [needs 4, 5, 6, 7, 8, 9, 10]
        launchpad/Research/the-professor-skill-suite-redesign.md's phase table still reads
        "| 1 | ... | 0 | Not started |" — Phase 1 shipped on 2026-09-08. Correct Phase 1's
        status, set Phase 1b's, and re-check §6.7 against what the editing steps wrote.
        Also record all FOUR 2026-09-15 decisions where the doc's other eleven live, so
        they survive this plan.
        Dependency corrected 2026-09-15: this was tagged [needs 4, 5, 6], which permitted
        it to set Phase 1b's status before step 7 changed the code and before steps 8–10
        produced any evidence. §9's Phase 1b review gate makes those demonstrations part
        of the gate, so the status row cannot honestly be set until they exist.
        done when: no phase row in the table contradicts a merged PR or an undemonstrated
        criterion; the run-identifier decision and its independence limitation, the
        roster-names flag-plus-offsets shape, and #2142's two-scenario reading are each
        recorded in the doc; every §N cross-reference still resolves to a real heading;
        and the three mermaid diagrams are still present.

PARALLEL
  Steps 4, 5 and 6 may run as parallel subagents — three different SKILL.md files, no
  shared file. Steps 1 and 2 must not: both edit verify-claims/SKILL.md, and step 2's
  wording depends on step 1's contract. Step 7 cannot run beside step 6 — its message
  text must match what step 6 leaves in the skill. Steps 8, 9 and 10 are demonstration
  runs that each consume a wired procedure and must follow it. Step 11 must come last of
  ALL steps, not just the editing ones — corrected 2026-09-15, because its old [needs 4,
  5, 6] tag let it set Phase 1b's status in the design doc before step 7 changed any code
  and before steps 8–10 produced a single piece of evidence, which §9's own Phase 1b
  review gate requires. It reports what the others actually did, so it cannot precede
  them.

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
  3. RESOLVED 2026-09-15 by Serina — see the third DECIDED note above the steps. Kept
     numbered here so a reader of this section alone does not think it was never asked.

  No live open items remain. The three above were put to Serina one at a time on
  2026-09-15 and answered. A FOURTH decision — candidate identity in a roster-names
  finding — was raised by the Codex review of this plan rather than by the issues, put to
  her the same day, and answered; it has its own DECIDED note above the steps and was
  never an OPEN item here. Each answer is carried into the step it changes. A builder
  finding a genuinely new gap reports it back rather than deciding it here.

  REVIEW HISTORY — two rounds, 2026-09-15, sixteen findings, all applied.

  Round 1: review-plan (Sonnet) and Codex, independently. Eight findings. Both converged
  on step 1's parsing rule as the worst defect — Blocker from one, High from the other.
  Codex alone found the candidate-identity hole that became the fourth decision. One
  disagreement was adjudicated against the files: the draft-page line-227 claim, which
  Sonnet passed and Codex correctly failed.

  Round 2: Codex again, over the revised plan. It rated five of its own eight round-1
  findings only PARTLY fixed, and added three more. The pattern worth carrying forward:
  every round-1 fix that named a failure without making it executable came back. Round 2
  required a whole-response grammar rather than "not by substring"; a concrete timeout
  value and a named enforcer rather than "a timeout blocks"; offset units, indexing and
  end-inclusivity rather than "column offsets"; and per-claim rather than per-pass
  invocation reconciliation. It also caught two errors this plan introduced in round 1 —
  a regression test pointed at a fixture whose candidates are on different lines, and an
  evidence requirement that would have breached screen-sensitive's own no-content-logging
  rule.

  Nothing in either round re-argued a DECIDED note, and none needed to be reopened.

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

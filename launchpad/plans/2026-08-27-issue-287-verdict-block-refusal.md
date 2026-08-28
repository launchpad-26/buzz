Issue #287 — refuse a comment set carrying more than one verdict block
Stated size: no `Size` line on the issue — asked Serina directly → 30–60 minutes → cap: 8 steps

ALREADY TRUE  (verified against git and the live repo, not notes)
  No code in `launchpad/review-agent/` parses PR comment bodies for a fenced `verdict`
  block today. `grep -rn` across every `.py` file in that directory found only:
  `fetch.py`'s `fetch_all()` retrieving comment surfaces for *containment* scanning
  (untrusted-text detection, `contain.py`'s domain), and `verdicts.py` validating the
  adjudication *stage's output document* structure — a different JSON document, not raw
  comment text. There is no existing "parse a fenced block out of a GitHub comment" code
  in this repository to extend.

  The ` ```verdict ` fence convention is real and already in production use. Pulled the
  actual bodies of PR #261 and #264 via `gh api repos/launchpad-26/buzz/issues/<n>/comments
  --paginate --slurp`: rows are tab-separated `VERDICT<TAB>SEVERITY<TAB>file:line<TAB>
  description`. It is written down nowhere in ADJUDICATION.md, FINDINGS.md, CONTAINMENT.md,
  or PUBLISHING.md — the format exists only as a convention reviewers already follow.

  The exact double-block scenario the issue describes is reproduced in the wild, not
  hypothetical:
    #261 — comment `5364185647` (01:45:48Z) and `5364261676` (01:58:30Z), same author
           (`ciaran-slow`), 13 minutes apart. Both are full 4-row restatements; row 2's
           severity moved Medium → Low between them.
    #264 — comment `5364221899` (01:51:51Z) and `5364504768` (02:36:23Z), same author,
           45 minutes apart. Both are full 3-row restatements; row 1's severity moved
           High → Blocker between them — the named promotion the issue cites.
  In both real cases the later comment is a **complete restatement**, not a delta. No
  supersedes marker exists anywhere in the two samples — this is the evidence behind the
  Option-B decision below.

  A near-neighbour already exists, but outside this repository and for a different input
  shape: `review-gate.sh`'s `cmd_verdict` (reached via the `serina-skills` plugin cache —
  canonical home is `serina-mcfall/serina-skills`, not part of `block/buzz`; corrected
  during review-plan, which found `~/.claude/skills/review-pr/review-gate.sh` doesn't
  exist and the earlier `launchpad-26/skills` attribution was wrong) already refuses more
  than one opening fence, distinguishes a present-and-empty block from an absent one,
  requires the fence to close, and accepts rows with **4 or more** tab-separated fields
  (`cut -f4-` joins field 4 onward as the description — corrected from an earlier
  "4-tab rows" misreading). It operates on **one local file** (`review-gate.sh verdict
  <file>`) — a single already-adjudicated report on disk before push — not a set of
  already-posted GitHub PR comments. Its multi-block check is a bare
  `grep -c '^```verdict$'` with no blockquote/indent lookalike guard, because a single
  local file written by one adjudicator in one pass doesn't need one. #287's input
  (comments from potentially several authors, reachable by anyone who can comment on the
  PR) does.

  `pr_body_check.py`'s `_strip_fences` (`launchpad/scripts/pr_body_check.py`) is this
  repo's only existing CommonMark-run-length-aware fence parser, but review-plan measured
  its blockquote handling directly and it does the **opposite** of what STEP 2 needs:
  `_strip_fences` strips blockquote markers *before* matching, specifically so a fence
  quoted with `> ` **is recognised** as real (its own docstring says so, and a live
  probe confirmed `_strip_fences` consumes a `> ```verdict` line as a genuine fence).
  STEP 2 needs the opposite disposition — a quoted fence must be *excluded*, not
  recognised — so only `_strip_fences`'s `FENCE_OPEN`/`FENCE_CLOSE` run-length matching is
  reusable; the blockquote disposition must be inverted, not copied.

  `fetch.py:140` (`fetch_all`) already knows the retrieval mechanics — `gh api --paginate
  --slurp` against both `issues/{pr}/comments` and `pulls/{pr}/comments`, plus the
  `UNREADABLE = ("absent", "oversized", "unparseable")` states and the
  `CAP_PER_ENTRY_POINT` size cap — but its `Surface`/`_joined()` abstraction **flattens
  every comment into one joined string** and discards comment id, author, and creation
  time entirely. That is not reusable for #287, which needs per-comment boundaries to
  resolve which block is "the last one" and to refuse a same-comment double-block.
  #287 needs a new per-comment fetch that borrows `fetch.py`'s pagination and
  unreadable-state handling, not its `Surface` type.

  #119 (this repo's other in-flight branch, PR #1460) touches `publish.py`,
  `run_dimensions.py`, `check_publish_*.py`, the two `launchpad-review-agent-*.yml`
  workflows, and — confirmed via the full `gh pr diff 1460 --name-only`, not the earlier
  partial read of it — `launchpad/review-agent/ADJUDICATION.md`, `CONTAINMENT.md`,
  `FINDINGS.md`, and `PUBLISHING.md` too. STEP 1 below edits `ADJUDICATION.md`, so there
  **is** file overlap with #1460 on that one file. This plan is on its own branch
  (`task/287-verdict-block-refusal`, off `origin/launchpad`, not stacked on #1460), so the
  overlap is an ordinary same-file-two-branches situation resolved by a normal rebase at
  merge time — not a logical dependency, and not a reason to wait on #1460. The earlier
  claim of "no file overlap" was wrong and is corrected here rather than left standing.

  No plan file existed for #287 before this one (`launchpad/plans/` checked).

DECISION RECORDED HERE, PER SERINA (issue asks for this explicitly; two readings were
surfaced and she chose)
  Reading A: a later comment may amend an earlier block, but only via a new explicit
  "supersedes" marker; anything without it is refused as ambiguous.
  Reading B: no amendment concept — a reviewer must re-post the complete block, and the
  parser deterministically takes the last complete, closed, well-formed block by comment
  order; a second block that is anything other than that (malformed, unclosed, or not a
  full row-set) is still refused.
  → Serina chose B: no new marker syntax, matches both real double-block cases observed
  above, and needs no reviewer-side change.

STEP 1  Record the Option-B decision in ADJUDICATION.md.                 [independent]
        Cite #261/#264 as the evidence.
        done when: ADJUDICATION.md gains a section stating the rule from the DECISION
        block above verbatim in substance, naming comment ids `5364185647`/`5364261676`
        (#261) and `5364221899`/`5364504768`(#264) as the production evidence it rests on.

STEP 2  Build the fenced-block locator.                                  [independent]
        Given one comment body's raw text, return every top-level ` ```verdict ` fence
        with its start/end line, closed/unclosed state, and raw row text. Reuse
        `pr_body_check.py`'s `FENCE_OPEN`/`FENCE_CLOSE` run-length-matching regexes for
        the fence boundary itself, but invert its blockquote disposition: `_strip_fences`
        strips `> ` before matching so a quoted fence *counts* as real (correct for its
        own job — hiding quoted code from prose scanning); this locator's job is the
        opposite, so a line matching `BLOCKQUOTE` must *disqualify* that fence rather than
        have its marker stripped first. Also capture the info string (`_strip_fences`
        only captures the backtick run, not what follows it) so ` ```verdict ` can be
        distinguished from an unrelated fence, and report closed/unclosed explicitly
        (`_strip_fences` has no such state — an unterminated fence there just runs to EOF).
        done when: a control suite proves, on synthetic bodies: zero blocks → empty list;
        one closed block → one entry; one unclosed block → flagged unclosed, not silently
        dropped or silently treated as empty; a `> ```verdict` blockquoted fence → not
        matched as a top-level block; a 4-space-indented ` ```verdict ` → not matched.

STEP 3  Build the row parser.                                            [needs 2]
        Given one located block's raw row text, parse each line into `{verdict, severity,
        location, description}`. A row needs **4 or more** tab-separated fields — not
        exactly 4 — with fields 4 onward rejoined as `description` (mirrors
        `review-gate.sh`'s `cut -f4-`; a description containing a literal tab is legal on
        the emitter side and must not be misread as malformed). Validate `verdict` is one
        of `verdicts.VERDICTS` (imported, not re-declared) and `severity` is one of
        `review.SEVERITY_ORDER` (imported the same way `verdicts.py:25` does) — marking a
        malformed row distinctly from a merely-empty block, not silently dropping or
        coercing it.
        done when: a control proves a well-formed 4-field row parses to the four named
        fields; a <4-field row is flagged malformed with the row's own text in the
        message; a 5-field row (tab inside the description) parses with fields 4–5 joined,
        not flagged malformed; a row whose first field isn't in `verdicts.VERDICTS`, or
        whose second field isn't in `review.SEVERITY_ORDER`, is flagged malformed rather
        than silently accepted.

STEP 4  Fetch one PR's full comment set and locate every block.  [needs 2]  ← RUNS HERE
        `fetch.py`'s `Surface`/`_joined()` flattens every comment into one string and
        discards comment id/author/time — not reusable here. Build a new per-comment
        fetch against both `issues/{pr}/comments` and `pulls/{pr}/comments`
        (`gh api --paginate --slurp`, same incantation `fetch.py` uses), keeping each
        comment's `id`, `created_at`, and `user` intact, and reusing `fetch.py`'s
        `UNREADABLE = ("absent", "oversized", "unparseable")` state model and
        `CAP_PER_ENTRY_POINT` so a failed or oversized fetch is a distinguishable state,
        not silently empty. Run STEP 2's locator over each comment's own, un-joined body,
        each result tagged with its source comment id, surface (`issue` vs `review`),
        `created_at`, and position within that comment.
        done when: run against the real PRs #261 and #264 over the live API, output shows
        exactly the two blocks found in each, tagged with comment ids matching
        `5364185647`/`5364261676` (#261) and `5364221899`/`5364504768` (#264) — the first
        point this plan produces something demonstrable against real data rather than
        synthetic fixtures. A forced-unreadable run (e.g. an invalid PR number, or
        `fetch.py`'s own `--degrade` pattern applied to this fetch) reports a distinct
        `unreadable` state rather than "zero comments".

STEP 5  Implement the Option-B resolution rule.                    [needs 1, 3, 4]
        Over STEP 4's tagged, STEP 3-parsed blocks for one PR, in this order — order
        matters, since two of these cases can match the same input and the first match
        must win:
          the comment fetch itself was unreadable (STEP 4's `absent`/`oversized`/
                                       `unparseable` states)   → refuse as `unreadable`,
                                       distinct from "none found"; never render the same
                                       as a clean zero-block PR (mirrors CONTAINMENT.md's
                                       "absence of evidence is never reported as evidence")
          two+ blocks **within the same comment**       → always refuse, regardless of
                                       whether every block in it is individually closed
                                       and well-formed. Two fences posted in one write
                                       can't be a temporal amendment of each other, so
                                       Option B's ordering rule never applies to this
                                       shape — refuse and name both positions. This branch
                                       must be checked **before** the accept-last branch
                                       below, since a same-comment pair that is also
                                       well-formed would otherwise match both
          any other malformed case (a malformed row anywhere, or an unclosed block, in
          any comment)                                   → refuse, naming every block's
                                       comment id, surface, and position — not only the
                                       offending one
          a well-formed, closed block found on the **review** (inline code-comment)
          surface                                         → refuse outright, naming the
                                       whole evaluated set (not only the review-surface
                                       block) — added post-review-final (see ADDENDUM
                                       below): resolves this section's own earlier
                                       "merged across both surfaces" wording and the OPEN
                                       item on review-comment scope, in the direction of
                                       never letting a partial inline annotation silently
                                       outrank or silently supersede a real issue-comment
                                       block
          zero blocks                                    → a distinguishable "none found"
                                       result, not an error
          one closed, well-formed block                  → accept it
          two+ blocks, all closed and fully well-formed, in **different** comments, all
          on the **issue-comment surface** (the review branch above already removed any
          review-surface block from contention)           → accept the block with the
                                       highest `(created_at, comment_id)` pair —
                                       `created_at` is only second-resolution, so
                                       `comment_id` (monotonically increasing on GitHub)
                                       is the deciding tie-break, not "position within a
                                       comment" (that tie-break only ever applied to the
                                       always-refused same-comment case, so it's dropped
                                       rather than kept as dead code). Report every
                                       earlier one as superseded, naming its comment id,
                                       surface, and position

ADDENDUM (post-build, after two review-final passes): this section originally said the
accept branch's ordering was "merged across both surfaces". Review-final's second pass
(finding 1, High) correctly caught that the shipped code instead refuses any well-formed
review-surface block outright — a stricter, evidence-backed answer to the OPEN item below,
not an oversight — and that this section hadn't been updated to say so. Fixed here rather
than left contradicting the code: only the issue-comment surface can supply an
authoritative block; a well-formed block on the review surface always refuses. See
ADJUDICATION.md's #287 section for the same decision recorded where a consumer would
actually read it.
        done when: run against #261's real comment set → resolves to `5364261676`'s block,
        reports `5364185647` as superseded; against #264 → resolves to `5364504768`'s
        block (the Blocker promotion), reports `5364221899` as superseded; a synthetic
        case with two **well-formed, closed** blocks in one comment → refused (not
        accepted via the last-wins branch), naming both positions; a synthetic case with
        one malformed row in the second of two otherwise-clean blocks in different
        comments → refused, naming both locations; STEP 4's `unreadable` state → refused
        as `unreadable`, distinguishable in the return value from the "none found" case.

STEP 6  Add the issue's five named control shapes, plus STEP 5's sixth.  [needs 5]
        As their own automated suite: zero blocks, one block, two **well-formed, closed**
        blocks in one comment (not a malformed pair — that would pass through the
        malformed-catch-all instead of proving the same-comment branch specifically), two
        blocks across two comments, a fenced block inside a quoted-or-indented context
        that only looks like one, and an unreadable/absent comment fetch — using #261 and
        #264 as real fixtures (recorded, not re-fetched live in the suite) plus synthetic
        cases for the rest.
        done when: the control script reports PASS on all six shapes; the #261/#264
        fixtures are recorded under this project's existing convention — `fixtures/
        adjudication/PROVENANCE.md` plus `fixtures/adjudication/generate.py` and
        `fixtures/adjudication/recordings/FALSIFIABILITY.md` (not `testdata/README.md`,
        which doesn't exist under `launchpad/review-agent/` — that convention belongs to
        `launchpad/scripts/testdata/`) — so a future re-record can refresh them from the
        live PRs.

STEP 7  Expose one clear entry point documenting the consumer contract.  [needs 5]
        E.g. a `resolve_verdict(pr, ...) -> Resolution`-shaped function, with a docstring
        stating the DoD's consumer requirement as a contract for whoever builds it next —
        #119's banner path does not currently read PR comments at all (confirmed: its
        scope is publishing a review it composes itself, not consuming other reviewers'
        comments), and STEP 11 is unrelated (`check_step11.py` is the CI-workflow-trigger
        control, not a comment consumer). There is no live consumer to migrate today,
        which the issue itself states ("fixing this now is cheap: there is no consumer yet
        to migrate") — so this step documents the contract rather than rewiring code that
        doesn't exist.
        done when: the module exports one importable entry point, its docstring names
        the two candidate future callers (#119's banner path, #426's pre-review packet)
        and states neither currently calls it, and a control asserts the function's
        signature/return shape stays stable (a smoke-level regression guard, not a
        behavioural one).

PARALLEL  STEP 1 (docs) and STEP 2 (locator) touch disjoint files and can run as parallel
  subagents. STEP 3 (row parser) and STEP 4 (fetch + locate-across-comments) both need
  STEP 2's output but can be written as separate functions/files and run in parallel with
  each other; they only need to agree on STEP 2's return shape, not on each other's code.
  STEPs 5, 6, 7 are strictly sequential from STEP 5 onward — 6 and 7 both read the whole
  resolver STEP 5 produces, and 7's docstring should reflect what 6's fixtures actually
  proved. Nothing here is dispatched by this plan; the decision to fan out belongs to
  whoever executes it.

GATES  No automated verify gate fires on its own in this checkout (per the sibling #118
  plan's own note, still true — `.claude/settings.json` / `.claude/settings.local.json`
  are both absent). Gates below are manual invocations before push, per
  `run-reviewers-before-pushing-not-after`.
  serina:review-code applies after STEPs 2–5 land (the parser and resolver).
  serina:review-tests applies after STEP 6 (the control suite) — check specifically for
  the five named shapes actually being distinct tests, not one test asserting all five.
  serina:review-plan ran once against this file (independent dispatch, Opus, this
  plan's own author excluded per the skill's requirement) and found 1 Blocker, 3 High,
  4 Medium, 2 Low — all applied to this revision. Verified against the live API and real
  code rather than assumed; see the STEP/ALREADY-TRUE text above for what changed.
  qa explore mode applies lightly: STEP 4 already is the "exercise the real interface"
  step (run against live PRs #261/#264), so a separate qa pass mainly needs to try
  additional real PRs beyond the two already used as fixtures, to catch a comment shape
  neither #261 nor #264 happened to exhibit.

BUDGET  STEP 5 is the step most likely to eat the budget, more so after review-plan's
  findings — it now has six ordered branches (unreadable-fetch / same-comment-refuse /
  malformed-anywhere / zero / one / clean-multi-in-different-comments) where branch order
  is itself load-bearing, not just branch content, and three of the plan's five real-PR-
  or-forced-state assertions depend on getting it right.

OPEN  Not for a builder to decide silently:
  RESOLVED (post-build, see STEP 5's ADDENDUM): whether GitHub *review-line* comments
  (`pulls/{pr}/comments`, inline code comments) are in scope. Both surfaces are fetched
  (STEP 4), but only the issue-comment surface can supply an authoritative block — a
  well-formed block found on the review surface always refuses, never silently accepted,
  never silently merged into the ordering, never silently dropped. Both real double-block
  examples (#261, #264) only ever used the issue-comment surface, which is the evidence
  this rests on.
  Whether an actual consumer (#119's banner path or #426's pre-review packet) gets wired
  to call STEP 7's entry point, and when — deliberately left to whichever of those issues
  builds next, per the issue's own "no consumer yet to migrate."

LEFT OUT  Deliberately excluded, per the issue's own Out of scope section:
  Changing how any individual reviewer's harness composes its output — this plan is only
  about the consuming side.
  Adjudicating whether the specific 2026-08-21 double-block reports were themselves
  correct — they were; the defect is the format not distinguishing amendment from
  duplication, which this plan fixes going forward, not retroactively.
  A supersedes-marker syntax (Reading A) — decided against; see DECISION RECORDED above.
  Rewiring any real consumer — none exists yet (see OPEN).

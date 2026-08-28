Issue #1343 — task: define the invariant corpus template
Stated size: no `Size` line on the issue -> cap: 12 steps (treated as "more than
an hour" per the skill default; this is a single-documentation-file task with an
unusually deep evidence-ledger requirement — see batch precedent PR #1541, 463
lines — so the cap is generous rather than binding).

ALREADY TRUE (verified against git and the worktree, not notes)
  - Worktree exists at __worktrees/task-1343-corpus-template-invariant, branch
    task/1343-corpus-template-invariant, HEAD == origin/launchpad ==
    a44cf52fc740ebebbdd671427480d14f0bce0115 (git rev-parse confirms both).
  - launchpad/docs/corpus/templates/ does not exist yet in this worktree or on
    origin/launchpad (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
    lists AGENTS.md, README.md, schema/**, standards/confidence.md,
    standards/decision-references.md only — no templates/ subtree).
  - Sibling PR #1541 (task/1342-corpus-template-interface) already created
    launchpad/docs/corpus/templates/interface.md at this exact base commit,
    open and non-draft, not merged. It is the direct structural precedent for
    "template" node shape (evidence ledger + Scope and authority + industry
    models considered + boundary + required-sections skeleton + evidence
    expectations + relationships + Note on Definition of Done + Scope and
    omissions). Read via `gh pr diff 1541 --repo launchpad-26/buzz`.
  - node.schema.json, AGENTS.md, schema/README.md, standards/confidence.md
    already read in full this session — front-matter contract, evidence-class
    rules, and one worked standards-track node are known, not assumed.
  - Repo-native invariant examples confirmed present by grep (not yet read at
    exact line numbers): crates/buzz-core/src/tenant.rs, crates/buzz-db/src/thread.rs:271,311,
    crates/buzz-audit/src/hash.rs:203, crates/buzz-relay/src/state.rs:187,
    crates/buzz-db/src/push.rs:1197, crates/buzz-acp/src/pool.rs:1441.
  - Design-by-contract web sources fetched this session: se.inf.ethz.ch (Meyer's
    own ETH Zurich page, names the three DbC constructs) and eiffel.com (Eiffel
    Software's own DbC/precondition/postcondition/invariant definitions). Meyer's
    original 1992 IEEE Computer paper could NOT be extracted as text in this
    environment (no pdftotext/poppler-utils, no pypdf, WebFetch returned only
    binary-PDF summaries) — this is a real, standing gap, not something to
    paper over.
  - PR #1518 (normative-language standard, issue #1320) diff already read in
    full — gives the exact boundary text needed to distinguish an invariant
    (a property of the system) from that standard (a rule about MUST/SHOULD/MAY
    wording in corpus prose itself).

STEP 1  [independent] Read the six repo-native invariant sites at their exact
        lines and record each one's file:line-range citation and a one-sentence
        paraphrase.
        done when: a scratch note (scratchpad/i1343/invariant-sources.md) lists
        all six with verified file:line ranges pulled from the actual file
        content (not the earlier grep's approximate line numbers), plus at
        least one additional candidate found by re-grepping
        `grep -rn "invariant" crates/ -i` for anything stronger that the first
        pass missed.

STEP 2  [independent] Confirm the relationships question: enumerate
        origin/launchpad's corpus tree fresh (git ls-tree -r --name-only
        origin/launchpad -- launchpad/docs/corpus) and decide, in writing,
        whether any of the four existing nodes is a legitimate `references`
        target for an invariant template (precedent: PR #1541 declared none,
        reasoning that all four are meta/procedural).
        done when: scratchpad/i1343/relationships-decision.md states the
        conclusion and the one-line reason, matching or explicitly diverging
        from PR #1541's reasoning.

STEP 3  [needs 1, 2] Draft the front matter (id: corpus-template-invariant,
        type: governance, status: active, origin: launchpad, audiences:
        agent/developer/reviewer) and the full evidence ledger, following
        node.schema.json's FACT/INFERENCE/TEAM_KNOWLEDGE rules, citing: commit
        a44cf52f (provenance), node.schema.json's type enum (no template/policy
        value — governance is the closest fit, matching all four merged nodes
        + PR #1541's template), the six repo-native invariant citations from
        Step 1, the two DbC web sources, PR #1518/#1320's boundary language,
        and issue #1343's own stale-DoD boilerplate (as TEAM_KNOWLEDGE, per PR
        #1541's "Note on Definition of Done" pattern).
        done when: the evidence array is written to
        scratchpad/i1343/frontmatter-draft.yaml (or inline in a working copy of
        the target file) and every FACT/INFERENCE entry's cited source has
        actually been opened this session (not assumed from Step 1's notes).

STEP 4  [needs 3] ← RUNS HERE. Write the body: title, "Scope and authority", "Industry model adapted:
        Design by Contract" (precondition/postcondition/class invariant,
        adapted rather than adopted wholesale — note Meyer's constructs apply
        to one class/routine, while a corpus invariant node may span multiple
        Rust types/modules, so state what's kept and what's reshaped), "A note
        on `type`", "Boundary: what this template is not" (vs #1320's
        normative-language standard: a rule about corpus MUST/SHOULD wording,
        not a system property; vs a not-yet-existing policy template: an
        invariant states what always holds, a policy states what participants
        must do), "Required sections" with a fenced template skeleton (must
        include: the invariant statement itself stated as a condition, not a
        goal; scope — which states/operations/types it binds; how it is
        enforced today — code/type-system/test/review, distinguished from
        "documented but not enforced"; consequence of violation; a boundary
        paragraph), "Evidence expectations" (an invariant claim is a FACT only
        if the cited code/test actually enforces it, not merely mentions it —
        mirror interface.md's "an operation-table row is a FACT or nothing"
        pattern), "Relationships" guidance, "Note on Definition of Done"
        (reusing PR #1541's exact reasoning pattern, re-pointed at #1343),
        "Scope and omissions" with the not-covered table and an honest
        "Expected but not verified" list that names the Meyer-paper gap from
        Step 1.
        done when: launchpad/docs/corpus/templates/invariant.md exists with
        complete front matter and body; this is the first point at which
        anything runs/validates.

STEP 5  [needs 4] Run the schema tests and the corpus validator; fix anything
        either one reports.
        done when:
        `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py" -v`
        exits 0 (unpiped) AND `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, run from the repo root inside the worktree.

STEP 6  [needs 5] review-plan pass over this plan itself (adversarial: does the
        plan's step order actually produce a schema-valid, evidence-honest
        node, or does it defer a load-bearing decision to "later" without
        saying so).
        done when: findings are either resolved with a plan edit or explicitly
        deferred with a stated reason.

STEP 7  [needs 5] build-change execution is Steps 1-5 above, already covered;
        this step is the review-code pass on the finished file: check every
        FACT cites a source that was actually opened, every INFERENCE carries
        a confidence and visible reasoning, no relationship targets an
        unmerged/sibling node, and the file does not silently duplicate
        content that AGENTS.md/node.schema.json already own.
        done when: findings list produced; Blockers fixed in the file itself
        before Step 8.

STEP 8  [needs 5] review-tests: N/A — this issue adds no test code, only a
        documentation node validated by the existing schema tests. Skipped,
        stated as a skip rather than silently omitted.
        done when: this step's N/A status is recorded in the PR body's
        pipeline description.

STEP 9  [needs 7] review-adjudicate: consolidate Step 6/7 findings, re-rate
        severity, decide Blocker (fix in this file) vs. escalate (new issue on
        launchpad-26/buzz, linked to parent PRD #605, named in PR's
        Escalations) per the brief's findings policy. Search for duplicate
        escalation issues first (#1532, #1538 already known; check for others
        specific to "invariant").
        done when: every finding is classified and, for Blockers, fixed and
        re-validated (re-run Step 5's two commands).

STEP 10 [needs 9] Cross-model final pass substitute: Codex is down (#1467), so
        this is a same-model adversarial self-review reading the finished file
        cold against parent PRD #605's acceptance sentence and against the
        boundary claims in "Boundary: what this template is not" — check they
        hold up against a skeptical re-read, not just against the sources
        cited when written.
        done when: the PR body states this substitution explicitly, per the
        brief's §6 requirement.

STEP 11 [needs 10] Commit (git commit -s, message via -F on a scratch file, no
        backticks in -m), then open the draft PR from AGENT_PR_TEMPLATE.md,
        filling the provenance table, a real `### Issue type` -> Task heading,
        a non-empty "Not verified" naming the Meyer-paper-text gap and
        anything else from Step 10, and Escalations naming any Step 9
        non-Blocker findings.
        done when: `gh pr create --draft --base launchpad --head
        task/1343-corpus-template-invariant --title ... -F body.md` succeeds
        as a lone command and returns a PR number.

STEP 12 [needs 11] Confirm CI: poll `gh pr checks <N> --repo launchpad-26/buzz`
        until the `check` job (Validate PR body) reports success; if it fails,
        read why and fix the PR body (not the workaround), re-push, re-check.
        done when: `gh pr checks <N> --repo launchpad-26/buzz` shows the
        `check` job with conclusion SUCCESS in its own output, observed
        directly (not assumed from a green icon description).

PARALLEL  Steps 1 and 2 are independent of each other (different files, no
          shared state) and could run as parallel subagents; every step from 3
          onward is sequential because each edits or depends on the same
          target file (invariant.md) or its immediate predecessor's output.
          Given the single-file, single-agent nature of this task, no step is
          actually being dispatched to a subagent here — this row states what
          *could* parallelize, not what will.
GATES     review-plan after Step 5 (Step 6), review-code after Step 5 (Step 7),
          review-tests explicitly skipped as N/A (Step 8) — a docs-only change
          with no test code, review-adjudicate after Step 7 (Step 9), a
          same-model cross-model-substitute final pass after Step 9 (Step 10).
          `qa` explore mode does not apply: this issue has no runtime
          interface to exercise — it is a Markdown document validated by a
          deterministic schema checker, not a running program.
BUDGET    Step 4 (writing the body) is most likely to eat the budget — matching
          PR #1541's actual scope (~350 lines of body prose plus ~20 evidence
          entries), the industry-model section and the required-sections
          skeleton both need real drafting, not templated filler.
OPEN      Whether `type: governance` is the durably correct enum value for an
          invariant template specifically (vs. e.g. a future `reference` or
          `verification`-shaped value if the enum grows) is not this task's to
          decide — node.schema.json's COMPATIBILITY.md governs adding enum
          values, and this task reuses the existing precedent (all four merged
          nodes + PR #1541 use governance) rather than proposing a new one.
          Whether `implements` or `references` is the corpus-wide convention
          for a node's self-link back to its own template is unsettled (noted
          by PR #1541 itself) and is not resolved here either.
LEFT OUT  Drafting an actual instance node (e.g. documenting the thread-counter
          invariant as a real corpus node using this template) — out of scope
          per the issue's own "Out of scope" section ("Creating or materially
          editing a second hand-authored canonical corpus document"). Deciding
          whether `launchpad/decisions/` ADR authoring should itself use this
          template for stating system invariants inside ADRs — not this
          issue's question, and no existing ADR was found doing so.

Issue #960 — task: document ingestion/git-history.md
Stated size: no `Size` line  →  cap: 5 steps (Feature #620 batch brief)

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-960-ingestion-git-history` is on branch
    `task/960-ingestion-git-history`, based on `origin/launchpad`, HEAD
    `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`, working tree clean.
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` shows the full
    standards/ and templates/ tracks now merged (not the earlier partial snapshot #650's
    and #954's own ledgers recorded), but still no `ingestion/*.md` or `agents/*.md`
    sibling under Feature #620 except `agents/invariants.md` — none of the 32 siblings,
    including #650 and #954, is a valid relationship target.
  Sibling `agents/repository-navigation.md` (#650, unmerged local commit,
    `__worktrees/task-650-agents-repository-navigation`, read in full) covers *locating*
    a symbol/commit/history in the wider repository — `git grep`, `git log --follow`,
    `--diff-filter=R`, `git blame` — as a search technique. It does not address the
    evidentiary weight of what is found once found.
  Sibling `ingestion/commits.md` (#954, unmerged local commit,
    `__worktrees/task-954-ingestion-commits`, read in full) covers the how-to procedure
    for citing *one specific* commit's message/diff as evidence of design rationale —
    deciding FACT vs INFERENCE for that single artifact — and explicitly names this
    node (#960) in its own Boundary/Scope-and-omissions as owning "the broader
    git-log/blame/bisect toolset for locating and dating changes generally," flagging
    the overlap risk as unresolved since no coordination was possible.
  Re-reading #954 closely narrows that flag: #954 already substantially covers the
    *search-and-cite-one-commit* procedure (mechanics), so re-building "the broader
    git-log/blame/bisect toolset" here would duplicate #650 (locating) and #954
    (citing one commit). The genuinely open gap, matching #960's own DoD tail being
    policy-shaped (MUST/SHOULD/enforcement) while #650 and #954 are procedure-shaped, is
    narrower and real: neither sibling, nor any merged `standards/*.md`, states the
    *evidentiary-weight/admissibility policy* for git-history-derived claims generally
    — specifically (a) that a commit message/diff documents intent *at that revision*
    and never by itself establishes *current* behavior at `HEAD` (code may have drifted
    since — the exact trap ADR-0029 was written to prevent), and (b) whether a
    `git blame`-derived fact (attribution, age, commit/author count over a range) may
    support a behavioral or design-stability claim, versus only an attribution/history
    fact. Confirmed by grep: `standards/decision-references.md` applies ADR-0029's
    intent-vs-behavior split to *decision records vs. code*, not to git-history
    artifacts; `standards/provenance.md` governs only the one mandatory
    recorded-revision commit citation; `standards/code-references.md` and
    `standards/test-references.md` govern citing code/test files themselves, not
    git-log/blame output about them. No merged node states this policy.
  `launchpad/docs/corpus/templates/policy.md` (merged, `id: corpus-template-policy`)
    is the genuinely-fitting template: six required sections (Scope and authority,
    MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions), P1-P10
    binding any instance, and its own worked precedent (`standards/provenance.md`) for
    a policy node that governs one specific commit-citation convention rather than the
    whole evidence contract.
  `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` (read in full) is the
    accepted decision this node's MUST rules apply: executable evidence outranks
    history/inference for *current-behavior* claims; accepted decisions outrank
    drifted code for *intent/authorization* claims; same-claim-type conflicts escalate
    to `status: flagged` rather than resolving by recency ("latest wins" explicitly
    rejected).
  `corpus-agents` (AGENTS.md), `corpus-template-policy`, `corpus-standard-provenance`,
    and `corpus-standard-decision-references` are all merged, real relationship
    targets this node's own reasoning genuinely depends on or references.

STEP 1  [independent]  Create `launchpad/docs/corpus/ingestion/git-history.md` with
        schema-valid front matter only: `id: ingestion-git-history`, `type: ingestion`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, reviewer]`, an
        `evidence` array whose first entry is the mandatory recorded-revision FACT
        (`commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`), no `relationships` key yet.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        with the new file present; front matter parses with `id == ingestion-git-history`,
        `type == ingestion`.

STEP 2  [needs 1]  Write the evidence ledger: cite `AGENTS.md`'s FACT/INFERENCE/
        TEAM_KNOWLEDGE contract and citation-shape table (FACT, already opened);
        cite ADR-0029 directly for the current-behavior/intent split and the
        no-recency-tiebreak rule (FACT, already opened); cite
        `decision-references.md` and `provenance.md` as the two merged siblings
        already applying ADR-0029/citation convention to an adjacent-but-different
        evidence type, to justify why this node does not restate their content
        (FACT); add a TEAM_KNOWLEDGE entry attributing the #650/#954 boundary
        narrowing to their own worktree text, named by title; add a TEAM_KNOWLEDGE
        entry for #960's own DoD tail versus Feature #620's real acceptance bar.
        done when: `validate.py` exits 0; every entry's class/field combination is
        schema-legal; every FACT's cited path or commit was actually opened this
        session.

STEP 3  [needs 2]  Write the body against `templates/policy.md`'s six required
        sections: Scope and authority (governs the evidentiary-weight/admissibility
        policy for claims derived from git-history artifacts — commit message/diff,
        `git blame` attribution/age, log-derived rename/authorship counts — authority
        derived from ADR-0029; ADR-0029 wins on any disagreement); MUST (the
        drift trap — a git-history claim about a past revision is not automatically a
        current-behavior claim; blame attribution/age is not automatically a
        stability/correctness claim; a current-behavior FACT needs an independent
        current-source citation alongside any git-history one; a conflicting
        same-claim-type pair of git-history-derived claims escalates, never
        recency-wins); SHOULD (cite current code alongside history when implying
        continuity; flag blame/log evidence used only as corroborating context;
        record commit/age counts as revision-dependent); Enforcement (nothing
        automated — `validate.py` discards the body and reports every commit
        citation `UNVERIFIED` regardless of which claim type it supports); Exceptions
        and escalation (none from the MUSTs; disputed application is a reviewer
        judgment call; open questions go to a `type:adr` issue against #620/#605);
        Scope and omissions naming #650, #954, `decision-references.md`,
        `provenance.md`, `code-references.md`, `test-references.md` by title and what
        each owns instead, plus what was expected but not verified.
        done when: `validate.py` exits 0; all six `##` sections present in relative
        order per P1; MUST/SHOULD occupy separate sections (P3); every requirement
        carries a stable identifier (P4); the H1 is `# Policy: <subject>` (P10); the
        Boundary/Scope-and-omissions explicitly names #650 and #954 by title and
        states this node's narrower angle against both.

STEP 4  [needs 3]  Add `relationships`: `depends-on: corpus-agents` (this node's
        FACT/INFERENCE/TEAM_KNOWLEDGE and citation-shape authority is AGENTS.md's, not
        original); `implements: corpus-template-policy` (built from that template's
        required shape); `references: corpus-standard-decision-references` and
        `references: corpus-standard-provenance` (adjacent siblings this node's own
        Scope-and-omissions distinguishes itself from and draws conceptual grounding
        from, per templates/policy.md's own relationships guidance). Confirm all four
        targets resolve against `origin/launchpad` (not the local worktree). Then
        audit: every substantive body claim maps to an evidence entry; body does not
        restate schema/validator/ADR-0029/sibling-standard content — links instead.
        done when: `validate.py` exits 0 with the four relationships present and
        resolving; `git diff --stat` shows exactly one new file under
        `launchpad/docs/corpus/` plus this plan file.

STEP 5  [needs 4]  Run the corpus test suite as its own last command (verify-gate
        stamp), then commit with `-s`.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK` as
        the sole command in its tool call; `git log --format=%B -1` shows a
        `Signed-off-by:` trailer and a message referencing `(#960)`.

PARALLEL  None. Steps 1-4 all build the same single file; strictly sequential.

GATES     Self-review (STEP 4's audit) plus an attempted `review-code`/
          `serina:review-code` pass per the batch brief — this is a single-document
          corpus task, matching the pattern used by prior corpus-doc plans in this
          batch. `review-tests` does not apply — no test file is added or changed.
          `qa` does not apply — no runtime interface exists to exercise.

BUDGET    STEP 3. The hard part is stating the drift-trap MUST precisely enough that
          it adds real, non-duplicative content beyond ADR-0029 and
          `decision-references.md`'s existing decision-vs-code application of the
          same split, while still naming ADR-0029 as the actual authority rather than
          restating it.

OPEN      Whether this node's narrower angle (evidentiary weight/admissibility of
          git-history artifacts) still leaves genuine daylight from #954 once #954
          merges with possibly-revised text. Named explicitly in Scope and omissions
          as unverified, since no coordination with #954's eventual merged content is
          possible from here.

LEFT OUT  Rebuilding #650's search technique or #954's single-commit-citation
          procedure. Rebuilding `decision-references.md`'s decision-vs-code
          application of ADR-0029, or `provenance.md`'s recorded-revision rule.
          Encoding any of this policy's MUST rules into `validate.py` — named as
          unenforced-by-tooling, matching every other policy-shaped node's own
          Enforcement section.

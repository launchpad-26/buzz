Issue #954 — task: document ingestion/commits.md
Stated size: no `Size` line  →  cap: 5 steps (Feature #620 batch brief)

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-954-ingestion-commits` is on branch
    `task/954-ingestion-commits`, based on `origin/launchpad`, HEAD
    `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`, working tree clean.
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` shows no
    `ingestion/*.md` or `agents/*.md` sibling merged yet except `agents/invariants.md`
    — none of Feature #620's 32 children is a valid relationship target.
  `launchpad/docs/corpus/standards/provenance.md` (merged) already owns the mandatory
    per-node "recorded revision" commit citation, its `commit <sha>` shape, the
    `git cat-file -e <sha>` check, and the revision-move rule in full — not to be
    rebuilt here.
  `launchpad/docs/corpus/AGENTS.md`'s citation-shape table names "Commit reference" as
    one of six shapes, always `UNVERIFIED`, never opened by `validate.py`; its
    "Nothing enforces this" subsection states a second/third commit-only `FACT` in the
    same ledger produces only extra non-fatal `UNVERIFIED` notices — the checker
    cannot tell a provenance entry from any other commit citation apart by shape alone.
  Sibling `agents/repository-navigation.md` (#650, unmerged, local commit at
    `__worktrees/task-650-agents-repository-navigation`) covers using `git log`,
    `git log --follow`, `--diff-filter=R`, and `git blame` to *locate* code/history —
    a search tool. It does not cover citing one commit's own message/diff as the
    evidentiary content of a claim. Read directly (not just its title) to draw this
    boundary.
  Sibling `ingestion/git-history.md` (#960) is not yet built in this batch run — no
    coordination possible; this document must state its own working boundary against
    it rather than silently building the broader subject.
  Two real, verifiable worked examples exist on this branch's own history:
    `commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41` ("fix(lefthook): resolve
    file-size-check base...") states its rationale in prose (a wrong merge-base
    reference point, confirmed repo-wide) directly in the message body — reachable
    from `origin/launchpad` (`git merge-base --is-ancestor` confirms).
    `commit 6d45f98665004d314468d98e50084996f4046cdf` ("ci: make file-size policy a
    first-class gate") carries an explicit `## Why` section stating the rationale
    directly (contract drift between the Desktop ratchet's scope and the pre-push
    path filter) — same repository, same reachability check applies.
  Issue #954's own DoD tail is the same generic MUST/SHOULD/enforcement/exceptions
    boilerplate independently found copied across many corpus-plan tasks (confirmed
    by reading `templates/policy.md`, `templates/procedure.md`, `templates/reference.md`,
    each of which overrides it with a "Note on Definition of Done" once the boilerplate
    did not fit the node's real shape); Feature #620's actual acceptance criteria
    (schema/graph/provenance validation, a genuinely-fitting template, no broad-overview
    duplication, independent traversability) are the real bar.
  Reasoned choice of shape: the subject — locating the commit that explains a design
    choice, reading its message/diff, classifying the resulting claim, and writing the
    citation — is goal-oriented sequenced technique, the same shape
    `agents/repository-navigation.md` (#650) already uses successfully for an adjacent
    ingestion technique. `templates/procedure.md`'s Required sections (Overview,
    Before you start, numbered task sequence(s), See also, Boundary, Relationships,
    Scope and omissions) fit better than `templates/policy.md`'s MUST/SHOULD/Enforcement
    shape (there is no corpus-wide binding rule to state — AGENTS.md and provenance.md
    already own the only MUST/SHOULD content about commit citations) or
    `templates/reference.md`'s lookup-table shape (the content is sequenced technique,
    not a catalogue of facts to look up).

STEP 1  [independent]  Create `launchpad/docs/corpus/ingestion/commits.md` with
        schema-valid front matter only: `id: ingestion-commits`, `type: ingestion`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, reviewer]`, an
        `evidence` array whose first entry is the mandatory recorded-revision FACT
        (`commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`), no `relationships` key
        yet.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        with the new file present; a YAML parse of the front matter reports
        `id == ingestion-commits`, `type == ingestion`, `relationships` absent.

STEP 2  [needs 1]  Write the evidence ledger: cite `provenance.md` and `AGENTS.md`'s
        citation-shape table and "Nothing enforces this" subsection (FACT, already
        opened above); cite the two worked commits (FACT, message states rationale
        directly, both confirmed reachable from `origin/launchpad`); add one
        INFERENCE entry (confidence-rated) covering the general case where a commit's
        *diff* carries intent the message does not state outright, so the claim
        depends on the author's own reasoning rather than a quoted sentence; add one
        TEAM_KNOWLEDGE entry for #954's own DoD tail, attributed to the issue.
        done when: `validate.py` exits 0; every entry's `entry_class` field
        combination (FACT forbids confidence/provided_by, INFERENCE requires
        confidence, TEAM_KNOWLEDGE requires provided_by) is schema-legal; every FACT's
        cited path or commit was actually opened in this session (traceable to a Bash
        call already run).

STEP 3  [needs 2]  Write the body against `templates/procedure.md`'s required
        sections: Overview (one line: citing a commit's own message/diff as evidence
        of *why*, not the provenance bookkeeping entry); Before you start (know the
        difference from `provenance.md`'s mandatory entry); a numbered task sequence
        (locate the commit that explains the design choice — `git log --follow`,
        `git blame`, a referenced issue/PR number; read the message body and diff;
        decide FACT vs INFERENCE depending on whether the message states the rationale
        or the diff alone implies it; write the `commit <sha>` citation and note it is
        `UNVERIFIED` by `validate.py`, checked only by a human `git cat-file -e`); See
        also; Boundary (explicit paragraph: not `provenance.md`'s recorded-revision
        entry; not the broader git-log/blame-as-search-tool subject
        `agents/repository-navigation.md` and the not-yet-built
        `ingestion/git-history.md` cover — state the working split explicitly since
        `git-history.md` has no built text to check against); Relationships; Scope and
        omissions (including the DoD-boilerplate note, per Step-0's finding, and the
        unbuilt-sibling tension named explicitly rather than resolved).
        done when: `validate.py` exits 0; every `##` section `templates/procedure.md`
        requires is present in relative order; the Boundary section names both
        `provenance.md` (merged, real target) and `ingestion/git-history.md` (unmerged,
        named in prose only, not a relationship target).

STEP 4  [needs 3]  Audit the finished node: every substantive body claim maps to an
        `evidence` entry; no entry cites a source that was not actually opened in this
        session; the H1 and section shape match `templates/procedure.md`'s skeleton;
        no relationship target is declared (none of Feature #620's siblings merged
        per Already-True); body does not restate `provenance.md`'s or `AGENTS.md`'s
        citation-shape table content — links instead.
        done when: `validate.py` exits 0; a written audit note maps each ledger entry
        to the body claim it supports, naming any entry that supports none; `git diff
        --stat` shows exactly one new file under `launchpad/docs/corpus/` plus this
        plan file.

STEP 5  [needs 4]  Run the corpus test suite as its own last command (verify-gate
        stamp), then commit with `-s`.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK` as
        the sole command in its tool call; `git log --format=%B -1` shows a
        `Signed-off-by:` trailer and a message referencing `(#954)`.

PARALLEL  None. Steps 1-4 all build the same single file; strictly sequential.

GATES     Self-review (STEP 4's audit) in place of an independent `review-code` pass —
          this is a single-document corpus task, matching the pattern used by prior
          corpus-doc plans in this batch. `review-tests` does not apply — no test file
          is added or changed. `qa` does not apply — no runtime interface exists to
          exercise; the only executable surface touched is `validate.py`, called but
          not modified.

BUDGET    STEP 3. The hard part is stating the boundary against the not-yet-built
          `ingestion/git-history.md` honestly — naming the tension rather than
          quietly picking the broader scope, since no coordination with that sibling
          is possible.

OPEN      Whether `developer` belongs in `audiences`. Planned choice: `agent`,
          `reviewer` only — an author using this technique acts as agent, a person
          checking the resulting citation acts as reviewer; a developer reading corpus
          prose is not addressed differently by this document than by the other two
          audiences. Stated so a reviewer can overturn it cheaply.

LEFT OUT  Any `relationships` edge — no Feature #620 sibling is merged and
          `agents/invariants.md`'s type-reasoning precedent does not create a genuine
          content dependency for this node's body. Rebuilding any part of
          `provenance.md`'s recorded-revision rule. Resolving the
          `ingestion/git-history.md` boundary definitively — named as an explicit,
          unresolved tension instead, since that sibling has no text yet to check
          against.

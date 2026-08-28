Issue #1307 — task: document corpus standard for atomicity
Stated size: none stated  →  cap: 5 steps (set by the feature #605 task brief: these are
single documents against conventions already settled by #636, not the first node)

Target file: `launchpad/docs/corpus/standards/atomicity.md`
Node id: `corpus-standard-atomicity` (assigned by the issue brief; permanent)
Base branch: `origin/task/636-corpus-agents-md` (AGENTS.md is unmerged — PR #1462)

ALREADY TRUE  (verified against git at 60d4947b7145a6ef25f185b9c25d43e43d99de3c, not notes)
  `git status --short` in this worktree reports exactly one entry, `?? ` on this plan
    file itself. No corpus content is part-built.
  `launchpad/docs/corpus/` contains exactly two entries: `AGENTS.md` and `schema/`.
  `launchpad/docs/corpus/standards/` does not exist; this task creates it.
  `AGENTS.md` is the only authored corpus node, and it declares no `relationships`.
  `node.schema.json` requires id, type, status, origin, audiences, evidence; permits
    `relationships`; `additionalProperties: false` rejects everything else — so there is
    no `provenance` field and the revision belongs in the `evidence` ledger.
  `validate.py` enforces: schema validity, duplicate ids, unresolved relationship
    targets, citation form, non-canonical (symlinked) nodes, non-`.md` files. It checks
    nothing about how many ideas a node holds.
  `.github/workflows/launchpad-corpus-validate.yml` runs that validator in CI.
  Sibling standards #1308–#1325 are all OPEN; none has merged, so no sibling id exists
    to point a `relationships[].target` at.
  `AGENTS.md` already states the rule in brief ("One node is one independently
    maintainable idea") and lists per-type standards under its own not-covered table as
    owned by #1307–#1351. This node is the canonical treatment that entry points at.

STEP 1  Create the node file with schema-valid front matter          [independent]
        Create `launchpad/docs/corpus/standards/atomicity.md` with schema-valid front
        matter — `id: corpus-standard-atomicity`, `type: governance`, `status: active`,
        `origin: launchpad`, `audiences: [agent, reviewer]` — plus the single permitted
        commit-only FACT recording revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c,
        and a body carrying only the "Scope and authority" section: what the policy
        governs (how many nodes a subject becomes), where its authority comes from, and
        the four adjacent subjects it does not decide (taxonomy #1324, identifiers
        #1317, naming #1319, linking #1318).
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0 with the new file on disk, and
                   `git cat-file -e 60d4947b7145a6ef25f185b9c25d43e43d99de3c` exits 0,
                   which is what makes that ledger entry a FACT rather than an
                   UNVERIFIED assertion.

STEP 2  Write the normative core and the decision procedure  [needs 1]  ← RUNS HERE
        Write the normative core: a MUST table and a SHOULD table, kept visually and
        structurally separate, and the decision procedure — the ordered tests an author
        applies to decide whether they are holding one node or two. The tests are
        derived from single-valued front-matter fields (`type`, `status`, `origin` each
        admit exactly one value per node), from the ledger carrying one recorded
        revision for the whole node, and from edges attaching to whole nodes. Add one
        `evidence` entry per substantive claim, classified honestly: schema
        single-valuedness is FACT against `node.schema.json`; "therefore two nodes" is
        INFERENCE with a confidence; the DoD's file-it-separately clause is
        TEAM_KNOWLEDGE attributed to issue #1307.
        done when: validator exits 0; every row of both tables has a matching `evidence`
                   entry (checked by reading the ledger against the tables and listing
                   the pairing in the commit message); and no MUST or SHOULD row
                   restates a schema enum member list.

STEP 3  Write the boundary cases and the mid-draft procedure            [needs 2]
        Write the boundary cases — the calls the procedure does not make by itself: a
        concept plus the procedure that uses it; a rule plus its exception; a subject
        whose two halves are on different maintenance clocks; a `flagged` half beside a
        healthy half; a node small enough that its body cannot stand without inlining a
        neighbour's. Then the mid-draft procedure: what an author does at the moment the
        second concept surfaces, including that the split is recorded rather than left
        implicit.
        done when: validator exits 0, and each boundary case states which way it
                   resolves plus why, with no case left as "it depends".

STEP 4  Write enforcement, escalation, and scope-and-omissions          [needs 3]
        Write enforcement and escalation: that no automated check enforces atomicity
        (enumerate what `validate.py` does check, and cite it), that enforcement is
        therefore the pull-request review ADR-0028 relies on, what a reviewer looks for,
        and the escalation path when author and reviewer disagree — including that
        `status: flagged` is *not* that path, because the schema defines it as ADR-0029's
        same-claim-type evidence conflict specifically. Then the scope-and-omissions
        section and the explicit statement that this node declares no `relationships`,
        with the reason.
        done when: validator exits 0; the file's front matter carries no `relationships`
                   key — `grep -c '^relationships:' launchpad/docs/corpus/standards/atomicity.md`
                   PRINTS `0` (read the printed count, not the exit status: `grep -c`
                   exits 1 on a zero count, so chaining this with `&&` reports failure
                   on exactly the state we want); and the body states the absence with
                   its reason, checked by
                   `grep -n 'declares no .relationships.' launchpad/docs/corpus/standards/atomicity.md`
                   printing at least one line. The second check is on a specific
                   sentence, not on the bare word, which would match any incidental
                   mention.

STEP 5  Audit the finished node against its own ledger                  [needs 4]
        Audit the finished node against its own ledger and against AGENTS.md's create
        procedure, step by step: every body claim has an entry, every entry backs a body
        claim, exactly one commit-only FACT exists, every FACT's source was actually
        opened, no schema enum list or field-combination matrix is restated in prose,
        and the document does not merely repeat AGENTS.md. Fix what the audit finds.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0; `cd <worktree> && python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
                   reports OK; and `grep -c "commit " launchpad/docs/corpus/standards/atomicity.md`
                   shows exactly one commit citation in the ledger.

PARALLEL  None. All five steps edit the same single file, and the skill's own rule is
          that two steps touching one file are sequential regardless of how unrelated
          they look. There is no second artefact to fan out to — the issue's Definition
          of Done caps this task at exactly one hand-authored document.

GATES     `review-plan` on this plan before STEP 1 — self-run, therefore not independent,
          and the report must say so. `review-code` on the finished diff after STEP 5.
          `review-tests` does **not** apply: the diff adds one Markdown file and one
          plan file and touches no test file (STEP 5 *runs* the existing corpus suite
          but does not modify it). `review-adjudicate` over every finding both reviewers
          report. A mandatory cross-model Codex final pass after adjudication, required
          to run the validator rather than read prose, and to hunt for holes the fixes
          opened. `qa` explore mode does **not** apply: this change adds no runtime
          interface — the only executable surface is `validate.py`, which is unchanged
          and is already exercised as every step's own done-when.

BUDGET    STEP 2. The decision procedure is the part of this document that does not
          already exist anywhere — AGENTS.md states the rule but not how to apply it —
          so it must be derived from the schema and the ADRs rather than summarised from
          a source. Getting each test grounded in evidence that genuinely supports it,
          without promoting reasoning to FACT, is where the time goes. The specific
          trap: a policy choice cited to a file that does not discuss policy is not an
          INFERENCE. That exact move was caught on #636 and reclassified.

OPEN      Whether `developer` belongs in `audiences`. The issue does not say, and the
          brief marks it deliberately unsettled. Resolved here as **no**: the audiences
          for a rule about corpus node granularity are the agent authoring the node and
          the reviewer holding the rule at the pull request, which is the same pair
          AGENTS.md carries. A developer reading Buzz source is not the addressee. If a
          later standard establishes that corpus policy nodes address developers, this
          is a one-line change, not a re-authoring.

          Whether atomicity owns "state what this node does not cover" in general, or
          only "state what you split off". Resolved narrowly as the latter — the general
          scope-section convention is #1313's (documentation standard) — so this node
          requires only that a declined boundary is recorded, not that every node
          carries a scope section.

LEFT OUT  Any `relationships` edges. Every sibling standard is unmerged, and a
          `relationships[].target` naming an id no loaded node carries is a hard
          validation error. The absence is stated in the body with its reason, as
          AGENTS.md does, and edges are a follow-up once the set has landed.

          A second hand-authored corpus document, of any kind. The issue's out-of-scope
          list forbids it explicitly, and this standard's own rule would forbid it too.

          Normative-language vocabulary — what MUST and SHOULD mean, and which other
          keywords are permitted. That is #1320's, and defining it here would create the
          second copy this standard exists to prevent. This node *uses* MUST and SHOULD
          and links #1320 rather than defining them.

          Editing `launchpad/docs/corpus/AGENTS.md`, including to point its
          not-covered table at this node. The brief forbids touching it; the pointer is
          a follow-up once this merges.

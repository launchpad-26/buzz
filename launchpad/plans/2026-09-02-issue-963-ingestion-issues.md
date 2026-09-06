Issue #963 — task: document ingestion/issues.md
Stated size: no `Size` line  →  cap: 5 steps (shared brief for Feature #620's document
tasks: single documents against conventions already settled by #636/#605)

Repo: launchpad-26/buzz · Branch: task/963-ingestion-issues
Base: origin/launchpad
Worktree: /home/serina/Launchpad/buzz/__worktrees/task-963-ingestion-issues

ALREADY TRUE  (verified against git and gh at aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90)
  `git rev-parse HEAD` = aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90; working tree clean.
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
    `ingestion/` directory — this node has no merged sibling under `ingestion/` to
    follow as type precedent. It DOES list, among many others: `AGENTS.md`
    (`corpus-agents`), `agents/invariants.md` (`agents-invariants`),
    `standards/evidence.md` (`corpus-standard-evidence`),
    `standards/decision-references.md` (`corpus-standard-decision-references`),
    `templates/policy.md` (`corpus-template-policy`). All five ids are confirmed real
    by reading each file's own front matter at this revision.
  Neither `#957` (`ingestion/decision-extraction.md`) nor `#962`
    (`ingestion/issue-comments.md`) — this task's sibling — is merged. Both are
    unbuilt or locally-drafted only; neither is a valid `relationships` target.
  `node.schema.json` requires id/type/status/origin/audiences/evidence, permits
    `relationships`, `additionalProperties: false`. `type` enum includes `ingestion`,
    described as the corpus *surface*, not the document's normative shape.
  Issue #963's own DoD asks for "states scope and authority/source of the policy",
    "separates MUST from SHOULD", "defines enforcement/checks and exception/escalation
    process", "links decisions or higher-order policy instead of duplicating them" —
    the same policy-shape checklist `templates/policy.md` itself formalizes. Template:
    **policy**, confirmed by reading `templates/policy.md` in full.
  `standards/evidence.md` already states, in its own body: "When the only source is an
    issue, a pull request, or a conversation... Use `TEAM_KNOWLEDGE` with `provided_by`
    naming the issue." This node's job is to operationalize that one sentence for the
    specific case of citing an issue's own title/body/state/labels — not to restate or
    re-derive the class choice.
  `standards/decision-references.md` governs citing an **accepted decision record**
    (an ADR) once one exists; it does not cover citing the raw issue that discussed the
    decision before it was written up. Real worked boundary case, checked live via
    `gh`: `launchpad-26/buzz#307` (`type:adr`, `CLOSED` at `2026-08-31T08:25:07Z`) was
    closed by batch PR `#1978` ("accept the 11 vendor-drop ADRs — daily-cadence
    decision set"), which closed 11 issues in one merge; the issue's own label set was
    applied once, at creation (`2026-08-21T12:03:15Z` per its GitHub timeline), never
    changed after.
  `launchpad/project-intelligence/corpus/validate.py` checks citation *shape* only —
    it never confirms `provided_by` names a real issue, never re-fetches an issue's
    state, and never distinguishes a body claim from a comment claim. Confirmed by
    reading the module.
  Review gates available as skills: review-code, review-adjudicate. `review-tests`
    does not apply (no test file touched). `qa` explore mode does not apply (no
    runtime interface added).

STEP 1  Record the evidence base before drafting                          [independent]
        Per AGENTS.md "Creating a node" step 3: the revision, every source path/issue
        to be cited, and every item expected but not verifiable. Confirm real `gh`
        evidence for: issue #963 itself (DoD), a `type:adr` issue's body-vs-comment gap
        (#307, already fetched above), and the batch-closing-PR nuance (#1978).
        Working notes go to the session scratchpad, never the repo tree.
        done when: notes list (a) HEAD sha, (b) each source path/issue that will be
        cited, (c) each expected-but-unverified item; `git cat-file -e
        aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` exits 0.

STEP 2  Create the node with complete front matter and a skeleton body   [needs 1]
        `launchpad/docs/corpus/ingestion/issues.md`, id `ingestion-issues`, type
        `ingestion`, status `draft`, origin `launchpad`, audiences `agent` +
        `reviewer`, one `evidence` entry per intended substantive claim including
        exactly one commit-only FACT for the revision, `relationships`: `depends-on
        corpus-standard-evidence`, `implements corpus-template-policy`, `references
        corpus-standard-decision-references`, `references corpus-agents` (all four
        ids confirmed present on `origin/launchpad` above).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
        and names the new node.

STEP 3  Write the body's first half                                      [needs 2]
        `# Policy: citing a GitHub issue`; scope and authority (governs citing an
        issue's own title/body/state/labels/closing-PR as evidence; authority derived
        from `standards/evidence.md`'s existing TEAM_KNOWLEDGE-for-issues rule and from
        this task's own DoD); the explicit boundary against #962 (individual comments),
        against `standards/decision-references.md` (citing a landed ADR), and against
        `ingestion/decision-extraction.md` #957 (noticing a decision exists, not citing
        an issue generally); MUST and SHOULD in separate sections covering: the
        TEAM_KNOWLEDGE/provided_by rule; recording observed state + date because state
        is mutable; re-checking state immediately before finalizing a state-dependent
        claim; separating a DoD/acceptance-criteria checklist claim from a free-text
        discussion claim; `type:adr` issues never being cited as settled-decision
        authority; a batch-closing PR not being treated as confirming the specific
        change without its own citation; naming which field (title/body/state/labels)
        an entry drew from.
        done when: validator exits 0; headings for scope/authority, boundary, MUST,
        SHOULD all present; every MUST/SHOULD sentence's factual basis has a matching
        `evidence` entry (one pass, ledger against prose).

STEP 4  Write the second half                                            [needs 3]
        Enforcement (nothing automated checks any of this — cite validate.py's actual
        behaviour); exceptions and escalation (no exemption from TEAM_KNOWLEDGE; a
        genuine same-claim-type conflict escalates per `ADR-0029`/evidence.md, not
        resolved here); scope-and-omissions table naming #962, decision-references.md,
        decision-extraction.md, evidence.md, code-references.md and the undefined
        "ratified spec" gap by name; the `relationships` section explaining why each of
        the four edges resolves and why no edge targets #957 or #962.
        done when: validator exits 0; scope-and-omissions table present with all named
        owners; `relationships` section states each edge's resolution check.

STEP 5  Re-verify every FACT, run both checks, commit                    [needs 4]
        Re-verify every FACT against its live source (files and `gh` calls) at the
        recorded revision. Commit with `-s`.
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` exits `OK` (run as
        its own command, last, so the verify-gate stamp lands); validator exits 0;
        `git log -1 --format=%B` shows a `Signed-off-by` trailer.

PARALLEL  None. Steps 3-5 edit the same single file in sequence; step 1 produces the
          input every later step consumes. No subagent fan-out for this issue.

GATES     After STEP 5: `review-code` on the diff (the artefact is a policy document;
          the code reviewer is the right lens for internal contradiction, over-claiming
          and boundary leakage against #962/#957/decision-references.md). If a
          dedicated `review-code` dispatch is genuinely unreachable, self-review against
          the same checklist and re-run `validate.py`.

OPEN      1. **`audiences`.** `agent` + `reviewer`, matching `agents-invariants` and
             `corpus-standard-decision-references` (both address whoever authors or
             reviews a corpus node); `developer` is left out because nothing here
             addresses someone writing application code.
          2. **Whether `references: corpus-agents` or `depends-on: corpus-agents`.**
             Chosen `references`, following `ingestion-decision-extraction`'s own
             reasoning: this node's procedure stays accurate even if AGENTS.md's later
             steps are reworded, so the coupling is loose, not a dependency for this
             node's own claims to hold.

LEFT OUT  - Individual comments on an issue — #962's territory, sibling, unmerged, no
            edge declared.
          - Noticing/screening that a decision exists inside an issue thread —
            #957's territory, sibling, unmerged, no edge declared.
          - Citing an accepted decision record once one exists — wholly
            `standards/decision-references.md`'s territory; referenced, not restated.
          - The general evidence/classification contract and citation-shape table —
            wholly `standards/evidence.md`'s territory; depended-on, not restated.
          - Citing code, tests, config — `standards/code-references.md`'s territory.
          - Encoding any of this in the schema or validator — no issue owns that today
            for this specific subject; named as unenforced in *Enforcement*.

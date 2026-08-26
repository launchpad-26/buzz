Issue #1310 — task: document corpus standard for decision references
Stated size: no `Size` line  →  cap: 5 steps (set by the shared brief for feature #605's
document tasks: single documents against conventions already settled by #636)

Repo: launchpad-26/buzz · Branch: task/1310-corpus-standard-decision-references
Base: origin/task/636-corpus-agents-md (AGENTS.md is unmerged — PR #1462)
Worktree: /home/serina/Launchpad/buzz/__worktrees/task-1310-corpus-standard-decision-references

REBASED AFTER PLANNING — the base branch advanced while this was being built.
  `origin/task/636-corpus-agents-md` moved from 60d4947b7 to a1e8bbcd0
  ("docs(corpus): stop asserting provenance policy this node cannot source (#636)"),
  which rewrote `launchpad/docs/corpus/AGENTS.md` — the only cited source that moved.
  The branch was rebased onto a1e8bbcd0 and the node's recorded revision moved to it
  after re-verifying every claim there. The facts below were verified at 60d4947b7 and
  remain true at a1e8bbcd0 except where AGENTS.md's own wording changed; see the
  node's ledger for what was re-checked. Two consequences of that commit are handled
  in the node: it deleted the AGENTS.md sentence one FACT quoted, and it narrowed the
  TEAM_KNOWLEDGE definition so one entry's class became illegal.

ALREADY TRUE  (verified against git and the filesystem at 60d4947b7145a6ef25f185b9c25d43e43d99de3c)
  `git rev-parse HEAD` = 60d4947b7145a6ef25f185b9c25d43e43d99de3c; working tree clean.
  `launchpad/docs/corpus/` contains exactly one authored node, `AGENTS.md` (id
    `corpus-agents`), plus the excluded `schema/` subtree. `standards/` does not exist.
  `launchpad/docs/corpus/schema/node.schema.json` requires id/type/status/origin/
    audiences/evidence, permits `relationships`, sets `additionalProperties: false`, and
    carries `flagged` in the `status` enum.
  `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` is Accepted and states the
    contextual-precedence rule and the same-claim-type escalation rule.
  `launchpad/decisions/` holds 43 ADRs: 18 `Accepted`, 20 `Proposed`, 5
    `Superseded by ADR-0050`. Verified by reading each file's front-matter `status`.
  `launchpad/decisions/README.md` states the supersession procedure: write a new record,
    set the old one's `status` to `Superseded by ADR-YYYY`, name it in the new record's
    `Supersedes`.
  `launchpad/project-intelligence/corpus/validate.py` `_classify_repo_path` accepts a
    bare repo-relative citation only if it resolves, inside the repo, to a real **file**
    (`candidate.is_file()`). It never opens the file's contents.
  Nothing in `validate.py` reads an ADR's front matter. `launchpad/scripts/
    adr_boundary_check.py` and `.github/workflows/launchpad-adr-check.yml` check ADR-0005's
    sanctioned-file list only.
  `launchpad/AGENTS.md` is the governing contributor guide; `launchpad/docs/corpus/
    AGENTS.md` is the nearest AGENTS.md for this change and governs it. Agents may write
    code and docs in this workspace (`/home/serina/Launchpad/CLAUDE.md`).
  Review gates available as skills: review-plan, review-code, review-tests,
    review-adjudicate, review-final, qa.

STEP 1  Record the evidence base before drafting                          [independent]
        Per AGENTS.md "Creating a node" step 3: the revision, every source path to be
        cited, and every item expected but not verifiable. Working notes go to the
        session scratchpad, never the repo tree.
        done when: the notes file exists and lists (a) the HEAD sha, (b) each source path
        that will appear as a citation, (c) each expected-but-unverified item; and
        `git cat-file -e 60d4947b7145a6ef25f185b9c25d43e43d99de3c` exits 0.

STEP 2  Create the node with complete front matter and a skeleton body   [needs 1]  ← RUNS HERE
        `launchpad/docs/corpus/standards/decision-references.md`, with id
        `corpus-standard-decision-references`, type `governance`, status `active`, origin
        `launchpad`, audiences `agent` + `reviewer`, and one `evidence` entry per intended
        substantive claim including exactly one commit-only FACT for the revision.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, and its output names the new node.

STEP 3  Write the body's first half                                          [needs 2]
        Scope and authority; the decision procedure an author uses to tell a
        *current-behaviour* claim from an *intended-or-authorized* claim; MUST
        requirements and SHOULD guidance in separate, separately headed sections.
        done when: validator exits 0; the file contains headings for scope/authority, the
        claim-type procedure, MUST and SHOULD; and every MUST/SHOULD sentence's factual
        basis has a matching `evidence` entry (checked by reading the ledger against the
        prose, one pass).

STEP 4  Write the second half                                                [needs 3]
        Two accepted decisions of the same claim type in conflict (authoring behaviour
        only — enforcement is #1410's); superseded decisions; what the validator does and
        does not establish about a decision citation; exceptions and escalation;
        scope-and-omissions including the deliberate absence of `relationships`.
        done when: validator exits 0; the file names #1410 as the owner of flagged-state
        schema/validator enforcement; the file states that it declares no `relationships`
        and why; and `grep -c '^relationships:' <file>` returns 0.

STEP 5  Re-verify every FACT, re-run both checks, commit                     [needs 4]
        Verify every FACT against its source at the recorded revision, then commit with
        `-s` using `-F <message-file>` (never `-m`, per the brief's backtick trap).
        done when: `cd <worktree> && python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` exits 0 (run as the
        last segment of its command, so the verify-gate stamp lands); the validator exits
        0; the ledger contains exactly one entry whose only citation matches
        `^commit [0-9a-f]{40}$`; and `git log -1 --format=%B` shows a `Signed-off-by`
        trailer.

PARALLEL  None. Every step after 1 edits the same single file, and steps 3 and 4 each
          depend on the front matter written in step 2. Step 1 writes only to the
          scratchpad but produces the input every later step consumes, so it cannot be
          overlapped either. No subagent fan-out for this issue.

GATES     After STEP 5: `review-code` on the diff (the artefact is a policy document, and
          the code reviewer is the right lens for internal contradiction, over-claiming and
          boundary leakage). `review-tests` **does not apply** — the diff adds one Markdown
          file and touches no test file; if that changes, it applies. Then
          `review-adjudicate` over every finding. Then a mandatory Codex cross-model final
          pass (`codex exec -c model_reasoning_effort="high" -s workspace-write`) requiring
          an explicit APPROVE / REQUEST_CHANGES verdict and the line `REVIEW COMPLETE`.
          **`qa` explore mode does not apply**: this change adds no runtime interface. The
          only executable surface it touches is `validate.py`, which every step above
          already exercises as its own done-condition, and which this change does not
          modify.

BUDGET    STEP 3 is most likely to overrun. Making "which kind of claim is this?" decidable
          by an author who does not already know the answer is the hard part of the issue,
          and ADR-0029 states the *rule* without giving a procedure for applying it. The
          risk is drifting into restating ADR-0029 instead of operationalising it — the
          settled convention is to link a decision, never to duplicate it.

OPEN      1. **`audiences`.** Whether `developer` belongs is deliberately unsettled across
             this batch. This plan chooses `agent` + `reviewer`, matching #636: the
             document addresses whoever authors or reviews a corpus node, and says nothing
             to a developer writing an ADR. If a reviewer disagrees, that is a one-line
             front-matter change, not a rewrite.
          2. **`type`.** `governance` is chosen over `development`: the node states policy
             about the corpus itself rather than describing a development surface. The
             schema's own description calls the enum "the corpus surface this node
             documents", and the surface here is the corpus's own governance.
          3. **What counts as a "ratified spec".** ADR-0029 grants intent/authorization
             authority to "accepted normative decisions (ADRs, ratified specs)" but no
             repository convention defines ratification for a spec.
             `launchpad/project-intelligence/CONTRACT.md` calls itself "proposed, not
             ratified", which shows the state exists but not how it is conferred. The
             document will state this as an open question rather than invent an answer.
          4. **Whether a `Proposed` ADR may ever be cited.** ADR-0029 gives authority to
             *accepted* decisions only, and 20 of 43 ADRs are `Proposed`. The document
             will say a Proposed ADR is not an authority for an intent claim; whether it
             may be cited at all as context is left to the evidence standard (#1314).

LEFT OUT  - Encoding claim type or `status: flagged` in the schema or validator. That is
            #1410's issue; this document describes the authoring behaviour and says the
            enforcement side is deferred.
          - How to cite **code** — #1308 owns `standards/code-references.md`.
          - The general evidence/classification standard — #1314 owns `standards/evidence.md`.
          - The generated-content contract — #1316.
          - Any `relationships` edge. Every sibling standard is unmerged and a target no
            loaded node carries is a hard validation error. Edges land in a follow-up once
            the set exists.
          - Editing `launchpad/docs/corpus/AGENTS.md`, any ADR, or any second corpus
            document. Out of scope by the issue and by the brief.

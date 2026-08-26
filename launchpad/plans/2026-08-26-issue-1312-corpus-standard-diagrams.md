Issue #1312 — task: document corpus standard for diagrams
Stated size: no `Size` line  ->  cap: 5 steps

The issue carries no `Size` line. Per the batch brief governing #1307-#1325, the cap is
5 steps and is not a question to stop on: these are single documents written against
conventions #636 already settled, not the first node in an unsettled corpus.

Deliverable: `launchpad/docs/corpus/standards/diagrams.md`, node id
`corpus-standard-diagrams` (assigned in the task prompt, permanent).

ALREADY TRUE  (verified against git and against measured tool output, not notes)

  Worktree `__worktrees/task-1312-corpus-standard-diagrams`, branch
  `task/1312-corpus-standard-diagrams`, cut from `origin/task/636-corpus-agents-md`
  at `ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109`. `git status --porcelain` is empty.

  `launchpad/docs/corpus/` contains exactly `AGENTS.md` and `schema/`. There is no
  `standards/` directory; this task creates it.

  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` returns only
  `schema/**`. The merge target therefore carries NO loadable corpus node: `schema/` is
  named in `EXCLUDED_TOP_LEVEL_DIRS` in `launchpad/project-intelligence/corpus/validate.py`.
  `corpus-agents` is loadable from this branch's base and absent from `origin/launchpad`
  (`git cat-file -e origin/launchpad:launchpad/docs/corpus/AGENTS.md` -> fatal).

  Measured, not assumed — `validate.py --root <scratch corpus>`:
    * a `.png` under `generated/` -> FAIL, exit 1 ("no corpus generator exists yet")
    * an `.svg` outside `generated/` -> FAIL, exit 1 ("non-.md file outside generated/")
    * a node whose body carries a ```mermaid fence asserting an invented topology,
      Mermaid's own `---` front-matter block inside that fence, and a Markdown link to
      a file that does not exist -> `PASS corpus validation clean`, exit 0
    * `Justfile:999999` against a 1005-line `Justfile` -> no error (#1459)
    * a bare directory citation `launchpad/docs/corpus` -> FAIL

  So the hard constraint this document is written under is established by measurement:
  a corpus diagram cannot be an image file today, and a diagram in body prose is
  invisible to every check that exists.

  `launchpad/plans/` is the plan location (root `docs/` and root `scripts/` are
  upstream's trees). Agents may write code and documents in this workspace —
  `Launchpad/CLAUDE.md` states the scoped exception explicitly.

STEP 1  Fix the evidence base and the citation set, then write it to scratch.       [independent]
        Re-read ADR-0028 (Context: "reviewed at the pull request that changes it ...
        has to be something a human reviewer can read comfortably in a PR diff"),
        ADR-0029 (contextual precedence; same-claim-type conflict -> flagged),
        `node.schema.json` (`evidence` = "The node's provenance ledger. One entry per
        claim"), `CONTRACT.md` §3 (six citation shapes), `validate.py`
        (`_load_frontmatter`, `find_ownership_violations`, `_classify_citation`),
        `.github/workflows/launchpad-corpus-validate.yml`, and the existing
        diagram-as-text precedent in this repository. **Count it, do not estimate it.**
        An earlier draft of this step asserted "the two existing diagram-as-text sites";
        `git grep -l -E '[U+250C...U+253C]' -- '*.md'` returns 20 tracked Markdown files,
        `README.md` among them, and `git grep -l '```mermaid' -- '*.md'` returns one. A
        completeness claim that a reviewer can refute with one grep is the exact "FACT
        cited to a source that does not support it" failure this corpus has already shipped
        twice; any precedent claim in the node states the measured counts and the command
        that produced them, or is not made.
        Decide the citation set under one hard rule: **cite nothing absent from
        `origin/launchpad`.** #1473 is an open bug where a sibling node's four
        `launchpad/docs/corpus/AGENTS.md` citations become hard validator errors on the
        merge target; this node avoids that class entirely by sourcing every claim to a
        primary file instead of to `AGENTS.md`.
        done when: `scratchpad/i1312/evidence-base.md` exists and, for every path in the
        intended citation set, `git cat-file -e origin/launchpad:<path>` exits 0 — the
        loop's output pasted in, zero `fatal` lines.

STEP 2  Write the front matter and the evidence ledger.                             [needs 1]
        `id: corpus-standard-diagrams`, `status: active`, `origin: launchpad`.
        `type: governance` — the schema calls `type` "the corpus surface this node
        documents" and #1312's objective calls this "the single canonical policy node";
        `governance` is the policy surface. `audiences: [agent, reviewer]` — the document
        addresses whoever authors a corpus node and the reviewer who is its only
        enforcement; `developer` is deliberately omitted and the omission is stated in the
        body rather than left silent. No `relationships`, and the reason recorded is merge
        order, not an empty corpus: `corpus-agents` is loadable here and absent from
        `origin/launchpad`, so an edge to it would validate locally and be a hard error in
        CI. One commit-only FACT — the revision — and no second one. Issue-sourced claims
        (which sibling task owns a deferred subject) go to TEAM_KNOWLEDGE with
        `provided_by`, never to FACT on a tool-result citation.
        done when: a `python3 -` script parses ONLY the front-matter block with
        `yaml.safe_load`, reports zero errors from
        `jsonschema.Draft202012Validator(node.schema.json).iter_errors()`, and — counting
        over parsed `evidence[].evidence` citation STRINGS, never over raw file text —
        reports exactly one entry whose citations are all commit references
        (`re.match(r"^commit\s+[0-9a-fA-F]{7,40}\b", c)`). A `grep -c "commit "` over the
        file cannot do this: run against `AGENTS.md` it returns 12, because the word
        "commit" occurs inside evidence *statements* as ordinary prose.

STEP 3  Write the body.                                       [needs 2]  <- RUNS HERE
        Nine sections, each answering one clause of #1312's definition of done:
        (1) what this standard governs; (2) authority and scope — ADR-0028 for
        representation, `node.schema.json` for the ledger, `validate.py` for what is
        actually enforced, ADR-0029 for conflict, linked and not restated; (3) **form** —
        a diagram MUST be diagram-as-text in a fenced block, MUST NOT be an image file,
        with the measured validator output as the reason and the image question deferred to
        #1316; (4) when a node carries one (MUST/SHOULD separated); (5) **the evidence
        obligation** — a diagram asserting a relationship is a substantive claim, the
        ledger is one entry per claim, and the body is invisible to the checker, so the
        rule is that a diagram MUST NOT be the only place a claim appears: it projects
        claims the ledger already carries; (6) staleness — bare paths only, never
        `path:line` (#1459), diagram and ledger edited together, automated detection
        deferred to #556; (7) enforcement — the validator's one relevant check plus human
        PR review, which is the same mechanism ADR-0028 says the whole corpus depends on;
        (8) exceptions and escalation — an image cannot be granted locally because the
        validator fails closed by design, and a diagram whose edges two same-claim-type
        authorities dispute is not drawn but recorded, per ADR-0029; (9) scope, omissions,
        and what could not be verified.
        Do not restate enum member lists or the schema's field-combination matrix — link
        the schema. Do not propose changing the validator or ADR-0028.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, and every `##` heading in the new file maps to a named clause of #1312's
        definition of done in a mapping table written to `scratchpad/i1312/dod-map.md`.

STEP 4  Prove the node is safe on the merge target, not just here.                  [needs 3]
        Reproduce #1473's method in reverse: check out `origin/launchpad` into a throwaway
        directory, copy in only `standards/diagrams.md`, and run the validator there. This
        is the check no local run can make, because the local tree carries `AGENTS.md` and
        `origin/launchpad` does not.
        done when: the validator run against the `origin/launchpad` checkout with this node
        copied in exits 0, output pasted into `scratchpad/i1312/merge-target-run.txt`.

STEP 5  Self-audit against #1312's definition of done and the create procedure.      [needs 4]
        Walk #1312's eleven done-criteria one at a time and record, for each, the specific
        evidence that satisfies it or the reason it cannot be satisfied. Then walk
        `launchpad/docs/corpus/AGENTS.md`'s ten-step create procedure literally, recording
        every point where following it as written produced a wrong or impossible result —
        that record is a required output of this task, not a byproduct. Re-check the base
        (`git fetch origin task/636-corpus-agents-md`); if it moved, merge (never rebase —
        the branch is pushed), re-run the validator and the corpus unit suite, and
        re-verify any claim that rests on a file the merge touched.
        done when: `scratchpad/i1312/dod-audit.md` has an entry for all eleven criteria and
        all ten procedure steps; and, as the last segment of its own command,
        `cd <worktree> && python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        exits 0.

PARALLEL  Nothing may fan out. STEP 1 is the only independent step, and STEPs 2, 3 and 5
          all write `launchpad/docs/corpus/standards/diagrams.md` or depend on its final
          content — two steps editing one file are sequential regardless of how unrelated
          they look. STEP 4 needs the finished file. A single agent runs all five.

GATES     `review-code` after STEP 5 (the diff is a document plus a plan; `review-code` is
          the reviewer the batch brief names for it). `review-tests` does NOT apply — this
          diff adds no test and changes none; if that becomes false, it applies.
          `review-a11y` does not apply: no UI. Then `review-adjudicate` over every finding.
          Then the mandatory cross-model final pass, which is currently unavailable
          (`codex exec` -> out of credits, tracked as #1467) — attempt it, record the
          failure, and run `review-final` as a labelled same-vendor stand-in rather than
          presenting the gate as discharged.
          **Saying that is not enough to make it true.** `pr-gate.sh` lets a non-draft PR
          through on a recorded `ready` verdict and has no way to tell a cross-vendor
          review-final from a same-vendor one, so a stand-in that records `ready` opens a
          normal PR that LOOKS fully gated. The mechanism, not the disclaimer, is what
          holds: **the PR is created with `--draft`** (`pr-gate.sh` requires no verdict from
          a draft), the undischarged #1467 gate is named in the PR body's "Not verified"
          section as its single most important line, and marking it ready is Serina's call.
          This matches what #1307 did. `qa` explore mode does NOT apply: this change
          adds one Markdown document and has no runtime interface to exercise. The
          validator and the corpus unit suite are the only executable checks, and they run
          inside STEPs 3, 4 and 5 rather than as a gate afterwards.

BUDGET    STEP 3 will eat the budget. Sections 5 and 8 are the two places this document has
          to decide something rather than report it — what evidence obligation a diagram
          carries, and what an author does when no legal form exists — and both have to
          land as a rule an author can follow while staying inside what ADR-0028, the
          schema and the validator actually establish. Section 5 in particular is the
          genuinely open question the task prompt flags; getting it wrong means either
          inventing a ledger shape the schema does not have, or waving the obligation away.

OPEN      Three things #1312 does not decide, and this plan does not resolve silently.

          1. **Whether a diagram needs its own ledger entry at all.** The task prompt names
             this as the open question. Two readings are live. (a) A diagram is a claim, so
             each relationship it asserts needs an entry — honest, and it makes a
             six-edge diagram a six-entry ledger addition. (b) A diagram is a *rendering*
             of claims made elsewhere in the node, so it needs no entry of its own,
             provided nothing in it is unsourced. The plan takes (b) and makes it a MUST
             ("a diagram is never the only place a claim appears"), because (a) invents a
             ledger granularity the schema does not describe and the checker cannot see
             either way. That is a choice, argued in the body, not a fact — and if a
             reviewer prefers (a), the fix is one section, not a rewrite.
          2. **Whether `developer` belongs in `audiences`.** The batch brief says the
             question is deliberately unsettled. The plan omits it and states why in the
             body. A reviewer may disagree; the disagreement should be recorded, not
             resolved by copying a sibling.
          3. **Whether diagrams are within #1324's taxonomy remit or this node's.** #1324
             ("standard for taxonomy") could be read as owning which node types carry
             which figures. The plan reads #1312 as owning the diagram policy and #1324 as
             owning node classification, and says so in the scope section so the boundary
             is visible rather than assumed.

LEFT OUT  * **Any change to `validate.py`, `node.schema.json` or ADR-0028.** The task
            prompt puts it out of scope, and the generated-content contract that would
            permit an image file is #1316's to write.
          * **Any edit to `launchpad/docs/corpus/AGENTS.md`.** Out of scope by instruction.
            Defects found while following it literally are reported (STEP 5), not fixed.
          * **A new check that reads body prose.** The gap is real and is named in the
            body as a gap. Building the check is a separate task and would be a second
            deliverable in a task whose first done-criterion is "exactly one hand-authored
            canonical corpus document".
          * **A second corpus node.** Any second concept found while writing is filed as
            its own issue under #605, per the standing findings policy.
          * **Restating the schema's enums or its FACT/INFERENCE/TEAM_KNOWLEDGE field
            matrix in prose.** The validator never reads body prose, so a copy would stay
            green forever after it went stale. The schema is linked instead.

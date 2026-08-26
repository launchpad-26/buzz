Issue #1311 — task: document corpus standard for deprecation
Stated size: none  ->  cap: 5 steps

The issue carries no `Size` line. `plan-issue` says to ask before writing; the
coordinating brief for this batch answered in advance — 5 steps, because these are
single documents written against conventions #636 already settled, unlike #636 itself
which was granted 8 as the first node. Recorded here rather than re-asked.

ALREADY TRUE  (verified against git and against runs, not notes)
  Worktree `__worktrees/task-1311-corpus-standard-deprecation` is on branch
    `task/1311-corpus-standard-deprecation` at ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109,
    a clean tree (`git status --short` empty). `git cat-file -e` on that sha exits 0.
  `launchpad/docs/corpus/standards/` does not exist. `launchpad/docs/corpus/` holds
    `AGENTS.md` and `schema/` only.
  The merge target has no corpus node to point at. `git ls-tree -r --name-only
    origin/launchpad -- launchpad/docs/corpus` lists `schema/` files only, and
    `schema/` is excluded from validation by name (validate.py's
    `EXCLUDED_TOP_LEVEL_DIRS`). `corpus-agents` exists on this branch and NOT on
    `launchpad` — PR #1462 is open, not merged.
  Nothing reads a node's `status`. `grep -n status validate.py` returns only the
    `CitationVerdict.status` field ("ok"/"error"/"unverified"), never a node's. The
    only check on the field anywhere is enum membership in `node.schema.json`.
  Probe run, retire versus delete: a node with `status: retired` plus an inbound
    `supersedes` edge validates PASS/exit 0; moving that node's FILE away turns the
    same edge into `FAIL ... relationship target 'probe-old' does not match any known
    node id`, exit 1.
  Probe run, status is inert: six nodes — one per status value plus an `active` node
    declaring `depends-on` a `deprecated` node and `references` a `retired` one —
    validate PASS/exit 0 together.
  `node.schema.json` and `schema/README.md` document the meaning of `flagged` and of
    no other status value.
  Neighbour issues exist and are open: #1323 (`standards/status.md`), #1318
    (`standards/linking.md`), #1314 (`standards/evidence.md`), #1321
    (`standards/provenance.md`), #1316 (generated content), #1410 (encoding the
    flagged state).
  Five sibling PRs are open on this same base (#1470, #1480, #1477, #1468, #1469), so
    the base may advance while this runs.

STEP 1  Write `launchpad/docs/corpus/standards/deprecation.md` — complete front       [independent]
        matter (`id: corpus-standard-deprecation`, `type: governance`,
        `status: active`, `origin: launchpad`, `audiences: [agent, reviewer]`, one
        `evidence` entry per body claim including exactly one commit-only FACT for
        the revision, and NO `relationships`) plus the normative body: scope and
        authority, the active -> deprecated -> retired lifecycle and what each status
        asserts, MUST separated from SHOULD, what a green run does and does not
        establish, exceptions and escalation, neighbouring-node boundaries, and a
        scope-and-omissions section carrying both the boundary and the
        expected-but-not-verified list.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0 with the new file on disk, AND a scratch script over the new front
        matter reports (a) every bare-path citation resolving to an existing file
        (`test -f` exits 0 for each) with the count of such citations **>= 5** — a
        loop over zero citations passes vacuously otherwise, and TEAM_KNOWLEDGE
        entries need no `evidence` array at all, so a document could reach this gate
        with nothing checked; (b) exactly **one** evidence entry whose citations are
        all `commit ...` — the convention AGENTS.md states no check will ever hold;
        and (c) `grep -c "^relationships:"` on the new file returning 0.

STEP 2  Prove the document's central negative claim against the committed tree        [needs 1]
        rather than against a scratch fixture: re-run both probes with `--root`, and
        confirm each MUST/SHOULD sentence that asserts tool behaviour matches the
        observed output. Correct the document where they disagree — the document
        loses, not the probe.
        done when: the all-statuses probe prints `PASS` and exits 0, the
        deleted-target probe prints `FAIL ... does not match any known node id` and
        exits 1, both transcripts are saved under `scratchpad/i1311/`, and no
        sentence in the document contradicts either transcript.
        ← RUNS HERE

STEP 3  Land it: run the corpus validator suite as the last segment of its own        [needs 2]
        command so the verify-gate stamp is earned, then commit in a separate call
        with `-s` and a message written to a file (no backticks, no `$(...)`).
        done when: `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK,
        `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p
        "test_*.py"` reports OK, and `git log --oneline -1` shows the new commit with
        a `Signed-off-by` trailer (`git log -1 --format=%B | grep -c Signed-off-by`
        returns 1).

STEP 4  Re-check the moving parts before review: re-fetch                             [needs 3]
        `origin/task/636-corpus-agents-md`, merge it if it advanced (merge, never
        rebase — the branch is pushed), and re-verify every claim this document makes
        ABOUT `AGENTS.md` or about the merge target against the post-merge tree.
        done when: `git rev-parse origin/task/636-corpus-agents-md` is an ancestor of
        HEAD (`git merge-base --is-ancestor` exits 0), `git ls-tree -r --name-only
        origin/launchpad -- launchpad/docs/corpus` still lists no non-`schema/` node
        (or the `relationships` decision is revisited and recorded if it does), and
        the validator plus both suites are re-run to exit 0 after any merge.

PARALLEL  Nothing may fan out. All four steps touch the same single file, and steps
          2-4 each depend on the state the previous one left. STEP 1 is tagged
          `[independent]` because nothing precedes it, not because it could run
          beside anything.

GATES     `review-plan` on this plan before STEP 1. After STEP 3: `review-code` on
          the diff, then `review-adjudicate` over every finding. `review-tests` does
          NOT apply — the diff adds no test file and changes none; if STEP 2 forces a
          fixture or test change, it applies and this line is wrong. A cross-model
          `codex exec` final pass is required by the batch brief and is expected to
          fail on credits (#1467); if it does, `review-final` runs as a labelled
          same-vendor stand-in, not as the gate discharged. `qa` explore mode does
          NOT apply: this change adds one Markdown document and no runtime interface
          to exercise. The runnable surface it does touch — the validator — is
          covered by STEP 2's probes and STEP 3's suites.

BUDGET    STEP 1. The whole risk of this issue is in one paragraph of it: stating what
          `deprecated` and `retired` each oblige an author to do, when no source in
          the repository defines either value. `node.schema.json` and
          `schema/README.md` describe `flagged` and nothing else. Every honest route
          out of that is narrow — a FACT sourced to a file that does not discuss the
          claim is the exact failure #636 was corrected for, and #1323 owns the status
          field's general standard, so this node cannot quietly annex it. Expect the
          time to go on classifying those sentences, not on writing them.

OPEN      1. Does the `deprecated`/`retired` distinction belong to this node at all,
             or entirely to #1323? Read as written, #1311 owns the deprecation
             *policy* and #1323 owns the *status field*, which leaves the meaning of
             two enum values on the seam. This plan's answer: state the obligations
             that attach when a node stops being current, attribute them to this
             issue's definition of done as TEAM_KNOWLEDGE, and defer the field's
             general standard — including `draft` and `flagged` — to #1323 by name.
             If a reviewer reads that as annexing #1323's subject, the section goes
             and the node links out instead.
          2. Is `developer` an audience? Excluded here: corpus nodes are authored
             under `AGENTS.md` by agents, and the unenforced conventions land on a
             reviewer. Nothing in the deprecation lifecycle addresses product code.
             The batch brief records this question as deliberately unsettled.
          3. `relationships` is empty for a reason that expires. The merge target
             carries no node to point at because #1462 has not merged — merge order,
             not an empty corpus. When it merges, `references`/`part-of` edges to
             `corpus-agents` and `corpus-standard-status` become correct, and adding
             them is a later pass, not this one.

LEFT OUT  Encoding the lifecycle in the schema or the checker — status is metadata
          today and #1410 owns making `flagged` mean something to tooling. This
          document describes authoring behaviour only.
          A retirement of any existing node. Nothing in the corpus is being
          deprecated by this change; the document is the deliverable.
          `standards/status.md`, `standards/linking.md` and any second document. One
          hand-authored node per the issue's out-of-scope list.
          Touching `launchpad/docs/corpus/AGENTS.md`. Forbidden by the batch brief;
          defects found in it are reported, not fixed here.

Issue #939 — implementation reference corpus document for `buzz-test-client`
Stated size: not stated on the issue (corpus-batch-author dispatch fixes it) → cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  Worktree exists at __worktrees/task-939-buzz-test-client, branch task/939-buzz-test-client,
    tracking origin/launchpad, HEAD 76a0a4ebbe4bc4d852b0d04362ed768620da34b3.
  launchpad/docs/corpus/implementation/crates/buzz-test-client.md does not exist
    (`ls` reports "No such file or directory").
  No `implementation/` or `verification/`-typed node exists anywhere in the corpus yet
    (`git ls-tree -r --name-only HEAD -- launchpad/docs/corpus` lists only architecture/,
    schema/, standards/, templates/, AGENTS.md, README.md) — this is the first node of
    either surface, so there is no sibling instance to pattern-match against.
  launchpad/docs/corpus/architecture/containers/relay.md (id: architecture-containers-relay)
    exists, is merged on origin/launchpad, and already names
    "crates/buzz-test-client/tests/e2e_relay.rs and sibling e2e suites" as the relay's own
    Verification evidence — a real, checked candidate `references` target.
  crates/buzz-test-client/Cargo.toml describes the crate as "Integration test client and
    E2E test suite for Buzz"; src/lib.rs exports `BuzzTestClient` (connect, authenticate,
    send_event, subscribe, recv_event, collect_until_eose, disconnect) plus re-exports from
    buzz-ws-client (RelayMessage, OkResponse, WsClientError, parse_relay_message).
  All 19 files under crates/buzz-test-client/tests/ are `#[ignore]`d integration suites
    requiring a live relay (confirmed by reading e2e_relay.rs's module doc and
    conformance_multitenant.rs's `#[tokio::test] #[ignore]` attributes directly).
  `just test` (scripts/run-tests.sh) never invokes `cargo test -p buzz-test-client` at any
    verbosity level (grepped the whole script) — the crate's own test suite is exercised
    only by the documented manual command `cargo test -p buzz-test-client -- --ignored`
    against a running relay, per TESTING.md:12-16.
  buzz-relay declares `buzz-test-client` as a [dev-dependencies] path dependency
    specifically for examples/mesh_relay_lifecycle_smoke.rs (comment at
    crates/buzz-relay/Cargo.toml:91-94); src/bin/mention.rs and src/bin/wamp_bench.rs are
    the crate's own manual-testing/benchmarking binaries that also import `BuzzTestClient`.

STEP 1  Draft launchpad/docs/corpus/implementation/crates/buzz-test-client.md following      [independent]
        templates/implementation-reference.md's required sections (Realization statement,
        Target, Implementation surface, Divergences, Verification, Relationships, Scope and
        omissions), with id: implementation-crates-buzz-test-client, type: verification
        (chosen over implementation because the crate's own Cargo.toml description and this
        repo's root AGENTS.md both name it as test/E2E infrastructure, not product code —
        node.schema.json's enum carries both as siblings for exactly this distinction),
        status: draft, origin: launchpad, a `references` edge to architecture-containers-relay
        (verified merged above), and no `implements` edge (the crate's realization target —
        the repo's own testing approach, described in TESTING.md/ARCHITECTURE.md prose — has
        no corpus node id yet, so per AGENTS.md step 9 the template's Target section names it
        by path instead of inventing an edge).
        done when: the file exists, its YAML front matter parses, and every one of issue
        #939's Definition-of-Done bullets has a corresponding sentence or section in the body.

STEP 2  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.  [needs 1] ← RUNS HERE
        If it exits non-zero, `git stash` the new file, re-run to capture the pre-existing
        baseline failure count/list, `git stash pop`, and diff — only new FAIL lines
        attributable to the new node get fixed here.
        done when: the run reports zero FAIL entries whose node id is
        implementation-crates-buzz-test-client (baseline failures, if any, are unchanged
        before/after and are not this node's to fix).

STEP 3  As the sole command in its own tool call, run                                        [needs 2]
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"`.
        done when: the command's final line is `OK`.

STEP 4  In a separate tool call, `git add` the two new files (the corpus node and this plan)  [needs 3]
        and `git commit -s -m "docs(corpus): add buzz-test-client implementation reference
        (#939)"`.
        done when: `git log -1 --format=%H` returns a new commit sha on
        task/939-buzz-test-client whose diffstat lists exactly those two files, and the
        commit trailer contains a `Signed-off-by` line (the `-s` flag).

STEP 5  Re-read the committed diff against issue #939's Definition-of-Done checklist line by [needs 4]
        line, and re-open every cited source (not just the citation string) to confirm it
        actually supports its statement. Run the corpus-review skill on the node if reachable
        in this session; otherwise record that a careful self-review substituted for it and
        why.
        done when: every DoD bullet is checked off against the actual file content (not the
        plan), and either corpus-review's output or the self-review's findings are recorded
        in the final report.

PARALLEL  None of these steps may run as parallel subagents — steps 2-5 each depend on the
          previous step's file-on-disk state (validate.py needs the drafted file, the unittest
          gate needs a clean validate.py run per AGENTS.md's commit-gate convention, the commit
          needs the gate to pass, and the review needs the commit to exist). This is a single
          serial chain, one file at a time.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (step 2, schema/citation
          check) and `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
          -p "test_*.py"` (step 3, the commit gate) are the two mechanical gates this plan needs.
          corpus-review (step 5) is the substantive review gate for a drafted corpus node,
          used in place of review-code, which targets implementation diffs, not corpus prose.
          qa explore mode does not apply — this is a docs-only Markdown node with no runtime
          interface to exercise.
BUDGET    Step 1 is where the budget goes: choosing `type: verification` correctly, writing an
          honest FACT/INFERENCE/TEAM_KNOWLEDGE evidence ledger with real citations for every
          claim (especially the "just test never runs buzz-test-client's own suite" divergence,
          which is easy to get backwards), and getting the `references`-only relationship
          right without inventing an `implements` edge to a target with no corpus id yet.
OPEN      Whether `type: verification` or `type: implementation` is the better long-run choice
          for this node is a judgment call, not a settled rule — node.schema.json documents
          both as valid surfaces and the template explicitly allows either; this plan resolves
          it from the crate's own stated purpose but a later corpus pass could reasonably
          revisit it once sibling implementation-reference nodes exist for comparison.
LEFT OUT  Adding a reverse `references`/`implemented-by` edge from architecture-containers-relay.md
          back to this new node — issue #939 scopes this task to exactly one hand-authored
          canonical document; editing a second merged node is out of scope here.
          Running `just corpus-validate` via the Hermit-activated environment — the direct
          `python3 launchpad/project-intelligence/corpus/validate.py` invocation AGENTS.md
          documents as equivalent and Hermit-independent is used instead, since this session
          is not running through `just`.
          `git push` / `gh pr create` — explicitly out of scope; this batch integrates all 37
          documents into one Feature-level draft PR in a later, separate phase.

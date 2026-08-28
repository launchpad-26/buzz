Issue #696 — task: document architecture/principles/relay-orchestrates-subsystems.md
Parent PRD #608. Single-document task; no `Size` line on the issue, so this plan is kept
to the minimum steps rather than padded to a cap.

ALREADY TRUE
  `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
  are merged on `origin/launchpad` (HEAD a44cf52fc740ebebbdd671427480d14f0bce0115), and
  `launchpad/docs/corpus/architecture/principles/relay-orchestrates-subsystems.md` does
  not exist yet.

STEP 1  [independent]  Gather evidence for the invariant directly from the crate graph:
        read `crates/buzz-relay/src/state.rs` (`AppState`, `AppState::new`), and the
        `Cargo.toml` of `buzz-core`, `buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`,
        `buzz-audit`, `buzz-media`, `buzz-relay` and `buzz-admin` to establish the actual
        dependency direction (which crate depends on which) rather than assuming it.
        done when: for each subsystem crate, grep for a `buzz-relay` line in its
        `Cargo.toml` returns no match, and `buzz-relay`'s own `Cargo.toml` is confirmed to
        list all six subsystem crates as dependencies.

STEP 2  [needs 1]  ← RUNS HERE  Write the node: front matter (`id:
        architecture-principles-relay-orchestrates-subsystems`, `type: architecture`,
        `status: draft`, `origin: launchpad`, `audiences`, an `evidence` ledger with only
        citations actually opened in STEP 1, no `relationships`) and a body satisfying the
        issue's DoD plus the category tail: the invariant as one MUST/MUST-NOT property,
        its scope (which crates, which dependency edges), enforcement points and observable
        failure, and at least one verification/conformance link or an explicit statement
        that verification is missing.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

STEP 3  [needs 2]  Self-audit the finished node against the issue's DoD checklist line by
        line and against the category tail, confirming every evidence entry supports its
        statement and no second canonical document was created.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK and `validate.py` still exits 0.

STEP 4  [needs 3]  Commit and open a draft PR.
        done when: `gh pr create --draft` returns a PR URL against base `launchpad`.

PARALLEL  None — one file, four sequential steps.

GATES     `validate.py` and the corpus unittest suite (STEP 3), run locally in this
          worktree. `review-adjudicate` and a cross-model final pass are explicitly
          deferred to the batch owner's morning review, per this task's own briefing —
          not run here.

BUDGET    STEP 2. The hard part is stating the dependency-direction invariant precisely
          enough to survive the one real complication found in STEP 1: `buzz-admin` also
          depends directly on every subsystem crate, and `buzz-pubsub` depends on
          `buzz-auth`. Both are real and must be scoped into the invariant, not hidden.

OPEN      The issue's DoD asks for "typed relationships appropriate to the node" but also
          says relationships are optional and a target naming an id no loaded node carries
          is a hard validation error. No sibling `architecture/*` node is merged yet, so no
          target id exists to point at. Handling: omit `relationships`, same precedent as
          `corpus-standard-confidence`, and say so in the node rather than inventing a
          target.

LEFT OUT  Any second authored document. Any change to runtime code, `node.schema.json`, or
          `AGENTS.md`. Resolving whether `buzz-admin`'s direct subsystem access is itself a
          desired architecture — that is a design question for elsewhere, not this node's
          job; the node records the fact and its scope boundary, not a verdict on it.

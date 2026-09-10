Issue #924 — implementation/crates/buzz-core.md
Stated size: not stated in issue body (no `Size` line) → cap: 5 steps, per this task's explicit batch-dispatch instruction

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/implementation/` does not exist yet (`ls` fails); the target file
  `launchpad/docs/corpus/implementation/crates/buzz-core.md` does not exist.
  `launchpad/docs/corpus/templates/implementation-reference.md`, `AGENTS.md`, and
  `schema/node.schema.json` are merged on `origin/launchpad` at HEAD
  (1ed55e980b0043f92d9c652e6a39a8e49345389c).
  109 corpus nodes already exist under `launchpad/docs/corpus/` at this revision
  (`git ls-tree -r --name-only HEAD -- launchpad/docs/corpus`), including
  `architecture-principles-signed-events` and `architecture-principles-host-selects-community`,
  both of which already cite `crates/buzz-core/src/verification.rs` and
  `crates/buzz-core/src/tenant.rs` respectively as part of their own evidence ledgers.
  `crates/buzz-core/Cargo.toml` declares zero I/O dependencies (no tokio/sqlx/redis/axum);
  16 crates under `crates/` declare a real `buzz-core` dependency in their own `Cargo.toml`.

STEP 1  Confirm the two candidate relationship targets by re-reading                [independent]
        `architecture-principles-signed-events.md` and
        `architecture-principles-host-selects-community.md` in full, and confirm
        `architecture-principles-nostr-first.md` does NOT qualify (it cites
        `buzz-core/src/kind.rs` only as a location named by a relay-level design
        procedure, not as something buzz-core itself realizes).
        done when: for each of the three principle nodes, a yes/no `implements`
        decision is recorded with the specific evidence line that justifies it.

STEP 2  Verify the two concrete divergences already found in exploration — the      [independent]
        locally-duplicated `KIND_PUSH_LEASE` constant in
        `crates/buzz-relay/src/handlers/push_lease.rs` (vs. the canonical one in
        `crates/buzz-core/src/kind.rs`) and the locally-duplicated `KIND_LONG_FORM`
        constant (as `u16`) in `crates/buzz-cli/src/commands/notes.rs` (vs. the
        canonical `u32` in `crates/buzz-core/src/kind.rs`) — by re-running the greps
        that found them and confirming both files still exist unchanged at HEAD.
        done when: `grep -n "pub const KIND_" crates/*/Cargo.toml` — sorry, the real
        commands — `grep -rn "pub const KIND_" --include="*.rs" crates/ | grep -v
        buzz-core/src/kind.rs` returns exactly the two lines already recorded, at the
        same line numbers.

STEP 3  [needs 1, 2] ← RUNS HERE  Write                                             [needs 1, 2]
        `launchpad/docs/corpus/implementation/crates/buzz-core.md`: front matter
        (`id: implementation-crates-buzz-core`, `type: implementation`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, an `evidence`
        ledger with one entry per substantive claim classified FACT/INFERENCE/
        TEAM_KNOWLEDGE, and the `relationships` decided in STEP 1) plus the template's
        seven required body sections (Realization statement, Target, Implementation
        surface, Divergences, Verification, Relationships, Scope and omissions).
        done when: the file exists, contains all seven required sections by heading
        text, and every FACT-classified claim cites a path this session actually
        opened.

STEP 4  [needs 3] Validate: run                                                     [needs 3]
        `python3 launchpad/project-intelligence/corpus/validate.py` from the worktree
        root and compare its failure count against the same command run against
        `origin/launchpad` (via `git stash` or a second checkout) to isolate any
        failures introduced by this node specifically. Then run, as the sole command
        in its own tool call, `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
        done when: `validate.py` reports zero FAIL entries whose node is
        `implementation-crates-buzz-core`, and the unittest run prints `OK`.

STEP 5  [needs 4] Commit: `git add                                                  [needs 4]
        launchpad/docs/corpus/implementation/crates/buzz-core.md
        launchpad/plans/2026-09-01-issue-924-buzz-core.md` then `git commit -s -m
        "docs(corpus): add buzz-core implementation reference (#924)"` in a separate
        tool call from the `add`. Do not push, do not open a PR.
        done when: `git log -1 --stat` shows a new commit on
        `task/924-buzz-core` containing exactly those two files, and `git status`
        reports a clean tree.

PARALLEL: Steps 1 and 2 are independent of each other (different files, no shared
state) and could run as parallel subagents, but both are small re-verification checks
already substantially done during exploration, so running them serially in one session
costs less than the coordination overhead of dispatching them. Steps 3-5 are strictly
sequential: each edits or depends on the artifact the previous step produced.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit clean for
this node specifically (a pre-existing ~21-failure baseline unrelated to this node
already exists on `origin/launchpad` and is not this task's to fix). `python3 -m
unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must
report `OK` before the commit gate. `corpus-review` (not `review-code`) is the intended
downstream reviewer for this docs-only node if reachable; otherwise a documented
self-review against issue #924's Definition of Done stands in. `qa` explore mode does
not apply — this is a docs-only change with no runtime interface to exercise.

BUDGET: STEP 3 is the step most likely to eat the budget — buzz-core is a large,
15-module, foundational crate, and resisting the temptation to itemize every module in
the Implementation surface table (rather than a representative subset, with the rest
named honestly in Scope and omissions) is the main risk to both quality and time.

OPEN: Whether `type: implementation` or `type: interfaces-events` is the better surface
value for buzz-core — resolved to `implementation` because buzz-core's own `lib.rs` doc
comment describes it as supplying types, verification, and matching logic consumed by
other crates' handlers, not itself hosting a protocol/wire-level handler surface (the
template's own guidance reserves `interfaces-events` for code realizing "how a handler
realizes a wire-level NIP"). Whether an `implements` edge toward
`architecture-principles-host-selects-community` overclaims, given that node's own text
treats `crates/buzz-core/src/tenant.rs` and `crates/buzz-relay/src/tenant.rs` jointly as
"the implementation" and the actual host-resolution mechanism (`bind_community`) lives
only in `buzz-relay` — resolved by declaring the edge (buzz-core's types are a real,
cited part of that node's own evidence ledger) while stating explicitly in this node's
Divergences section that buzz-core supplies only the type-level fence, not the
resolution mechanism itself.

LEFT OUT: Not itemizing all ~15 of buzz-core's modules in the Implementation surface
table — `kind`, `verification`, `filter`, `event`, `tenant`, and `error` get dedicated
rows as the modules with direct, verified corpus-node evidence trails; `agent_turn_metric`,
`engram`, `git_perms`, `invite`, `nip10`, `observer`, `pairing`, `presence`,
`private_managed_agent`, `relay`, `channel`, and `network` are named as present but not
individually evidenced, in Scope and omissions rather than silently dropped. No
`implements` edge toward `architecture-principles-nostr-first` — that principle governs a
relay-level design choice buzz-core's kind registry merely supports, not something
buzz-core itself realizes. No fix to either constant-duplication divergence recorded by
step 2 (`KIND_PUSH_LEASE`, `KIND_LONG_FORM`) — reported only, per issue #924's own "Out
of scope: changing runtime product behavior" instruction. No relationship toward any
other architecture/principles node beyond the two justified above.

Issue #1061 — task: document layers/data/consistency-model.md

Stated size: issue #1061 carries no explicit Size line (checked its body directly); the dispatching batch brief caps a single corpus document at 5 steps -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum contains `layers`
  (among 13 surfaces), matching the target path's `layers/` root directory.
- `launchpad/docs/corpus/templates/concept.md` exists and matches this task's own
  Objective line ("the single canonical concept node for consistency model") —
  its *Required sections* (Definition, optional Background/Visual aid, Use cases,
  optional Comparison, Related resources, Scope and omissions) are the shape to
  follow, not `node.schema.json` cold.
- `launchpad/docs/corpus/layers/data/consistency-model.md` does not exist yet
  (confirmed with `test -f`) and no file under `launchpad/docs/corpus/layers/`
  exists at all yet — this is the first `layers`-typed node.
- `launchpad/docs/corpus/architecture/principles/relay-is-source-of-truth.md`
  (`id: architecture-principles-relay-is-source-of-truth`) is merged on
  `origin/launchpad` at this worktree's checkout revision and is a legitimate
  `references` target — the write-path consistency guarantees this node
  documents rest on that principle (single-writer Postgres authority) without
  duplicating its content.
- Source evidence for the concept itself is already read and pinned to this
  revision (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`):
  `crates/buzz-db/src/lib.rs` (`replace_parameterized_event`, advisory-lock +
  LWW stale-write rejection), `crates/buzz-db/src/event.rs`
  (`get_latest_global_replaceable`, `soft_delete_by_coordinate`),
  `crates/buzz-core/src/engram.rs` (`select_head`, `monotonic_created_at`),
  `crates/buzz-db/src/thread.rs` (`insert_thread_metadata`, one-transaction
  counter updates), `crates/buzz-db/src/replica_fence.rs` (module doc, replica
  read-freshness fence), and `CLAUDE.md:219` (buzz-cli exit code 5 = write
  conflict, NIP-33 LWW).

STEP 1 — Write the front matter and Definition/Background sections [independent]

Create `launchpad/docs/corpus/layers/data/consistency-model.md`. <- RUNS HERE
Front matter: `id: layers-data-consistency-model`, `type: layers`,
`status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator, reviewer]`, one `relationships` entry
(`references` -> `architecture-principles-relay-is-source-of-truth`). Body
opens with a one-sentence Definition (DoD: "defines the term in one sentence
before deeper explanation"), then Background covering: Postgres as the sole
durable store behind the relay; per-coordinate last-write-wins for NIP-33
parameterized-replaceable events (`(kind, pubkey, d_tag)`, highest
`created_at`, ties broken by lowest event id, serialized by a Postgres
advisory transaction lock); the same NIP-01/NIP-16 tiebreak reimplemented
independently in `buzz-core`'s engram/memory subsystem; transactionally
consistent materialized thread counters; and the replica read-freshness
fence for bounded-staleness reads.
done when: the file exists with schema-required front matter fields present and a Definition section stating the concept in one sentence, each Background claim backed by a ledger entry citing a source opened this session.

STEP 2 — Write Use cases, boundary/non-goals, and Related resources [needs 1]

Use cases: why a developer or agent needs this model (e.g. why a `buzz` CLI
write can return exit code 5, why a read against a replica can silently route
to the writer). Boundary/non-goals (DoD: "states boundaries/non-goals or what
the concept must not be confused with"): explicit that Nostr provides no
global total order across signers ("even same-signer ordering is advisory" —
`soft_delete_by_coordinate`'s own doc comment), that this node does not cover
Redis pub/sub fan-out delivery guarantees, and does not cover
`buzz-relay-mesh`'s inter-pod gossip (out of scope, per the already-merged
`relay-is-source-of-truth` node's own disclosure). Related resources as the
one `relationships` edge plus prose citations to the source files above.
done when: the body contains a Use cases section and an explicit boundary/non-goals passage naming at least the three exclusions above, each with a citation.

STEP 3 — Write Scope and omissions, run the validator, fix until clean [needs 2]

Two-part Scope and omissions section per the template's required section 8:
what this node does not cover (pub/sub delivery semantics, multi-relay/mesh
consistency, search-index consistency — none inspected for this task) and,
separately, anything expected but not verified (e.g. whether `buzz-search`'s
FTS index is kept consistent with `events` transactionally or asynchronously
was not checked here and is named as a gap, not silently assumed). Then run
`python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root and fix any reported error until it exits 0.
done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and the Scope and omissions section carries both the coverage table and the expected-but-not-verified list.

PARALLEL

None of the three steps are parallel — STEP 2 depends on the front matter and
Definition STEP 1 establishes, and STEP 3's validator run depends on the full
body STEP 2 writes. This is a single small document built as one continuous
pass, not a fan-out.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`, run alone in its own tool call, before committing.
- Every `FACT`/`INFERENCE` evidence entry cites a source actually opened this session; no invented line numbers.

BUDGET

One document, capped at 3 build steps (STEP 1-3 above). No template file is
being authored -- `concept.md` already exists -- so this stays small.

OPEN

- Whether the corpus should eventually also document search-index and
  pub/sub consistency as sibling `layers`-typed nodes is not decided here;
  named as a gap in the document's own Scope and omissions, not resolved.

LEFT OUT

- No second corpus document. No edits to `concept.md`, `node.schema.json`, or
  any already-merged corpus node (including
  `architecture-principles-relay-is-source-of-truth`, which is only linked,
  not edited).
- No investigation of `buzz-search`, `buzz-pubsub` delivery semantics, or
  `buzz-relay-mesh` beyond what is already cited in the merged
  `relay-is-source-of-truth` node -- those are named exclusions, not silently
  dropped.

# Plan: issue #1276 — document platforms/relay/mesh-bootstrap

## ALREADY TRUE

- Repository revision `131b02f989684117d9ab1dd426f1673fa638e523` on `origin/launchpad`.
- `launchpad/docs/corpus/platforms/relay/mesh-bootstrap.md` does not exist yet.
- No `platforms/` directory exists anywhere in the corpus tree on `origin/launchpad`
  (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
- No corpus node under `architecture/flows/**` or `architecture/deployment/**`
  documents mesh bootstrap specifically (`grep -ril mesh launchpad/docs/corpus/`
  turns up context/principle/deployment nodes that mention mesh in passing —
  e.g. `architecture/containers/relay.md`, `architecture/deployment/multi-relay.md`
  — none of which walks `boot_mesh`'s own startup sequence).
- No `platforms.md`-shaped template is merged on `origin/launchpad`; per finding #4,
  siblings in this Feature use `type: platforms` (a real, thirteen-member enum
  value in `node.schema.json`) borrowing `templates/component.md`'s section shape
  (Responsibility / Public interface / Dependencies / Boundary / Relationships /
  Scope and omissions) as an explicit INFERENCE, since no platforms-specific
  template exists.
- The actual mesh bootstrap logic lives in
  `crates/buzz-relay/src/mesh_boot.rs` (`boot_mesh`, `MeshHandle`,
  `MeshInboundDispatcher`, `wire_mesh_consumers`), backed by the
  `crates/buzz-relay-mesh` crate (`MeshConfig`, `MeshEndpoint`, `MeshMembership`,
  `MeshRuntime`, `ReadyRegistry`/`ReadyRecord`, `spawn_registry_heartbeat`), wired
  from `crates/buzz-relay/src/main.rs` (calls `boot_mesh` then `wire_consumers`,
  sets `AppState.mesh` OnceLock) and exposed at `GET /_mesh`
  (`crates/buzz-relay/src/router.rs:299`, `mesh_status_handler`).
- Config surface: `BUZZ_MESH`, `BUZZ_MESH_BIND_ADDR`, `BUZZ_MESH_ADVERTISE_ADDR`,
  `BUZZ_MESH_DEMO_ECHO` (`crates/buzz-relay/src/config.rs:680-705`).

## STEP 1 — Scaffold front matter by hand (no merged platforms template)

Write YAML front matter directly against `node.schema.json`: `id:
platforms-relay-mesh-bootstrap`, `type: platforms`, `status: draft`, `origin:
launchpad`, `audiences: [agent, developer, operator]`, one provenance `FACT`
evidence entry citing the recorded commit. State in the body that no
platforms-specific template exists yet, borrowing `component.md`'s shape per
Feature #614 convention (matches finding #4).

Done when: front matter parses as valid YAML and matches the seven allowed
top-level keys.

## STEP 2 — Write the body: responsibility, boot sequence, config, consumers

Cover, each cited to real source:
- Purpose/scope paragraph naming `boot_mesh` and the mesh subsystem.
- Responsibility, cited to `mesh_boot.rs`'s crate-level `//!` doc comment.
- The boot sequence as an ordered list matching `boot_mesh`'s real steps: kill
  switch check → endpoint bind → advertise-address resolution → gossip
  record/capabilities → membership with relay-pubkey anchor → ready-registry
  publish (fatal on error) → heartbeat spawn → `MeshRuntime::start` →
  `reconcile_now` → drain-watcher spawn → dispatcher install → `MeshHandle`
  return.
- Public interface table: `boot_mesh`, `MeshHandle`, `MeshHandle::status`,
  `MeshHandle::wire_consumers`, `MeshInboundDispatcher`, `AppState::mesh()`.
- Dependencies (depends-on: `buzz-relay-mesh`, `buzz_db`, `deadpool_redis`,
  `nostr`, cited to `Cargo.toml`; depended-on-by: `main.rs`'s boot call,
  `router.rs`'s `/_mesh` route, `audio::mesh`/`audio::join` consumers).
- Boundary: excludes wire protocol internals (`buzz-relay-mesh` internals:
  gossip/membership/transport implementation), huddle-audio session logic, and
  install/usage instructions.

Done when: every substantive claim has a citation to a file I opened this
session, and public-interface rows cite real declarations, not descriptions.

## STEP 3 — Relationships and scope/omissions

Declare no `relationships` (checked: zero nodes on `origin/launchpad` target
this subject; the closest neighbors — `architecture/containers/relay.md`,
`architecture/deployment/multi-relay.md` — are container/deployment-level, not
this bootstrap procedure, and adding an edge to either would assert an overlap
neither node claims). State this explicitly rather than asserting the
generic "nothing to point at yet" line the AGENTS.md itself warns is a common
false justification — the count was actually checked this session.

Write Scope and omissions: excludes wire-format/gossip-algorithm internals (own
future component node), huddle audio session mechanics, non-Rust equivalents
(none — this is relay-only). Note what was expected but not independently
verified: live end-to-end mesh formation across pods (only source-level
control-flow was read, not exercised at runtime).

Done when: the two distinct sub-lists (owner table + "expected but not
verified") both exist, per `AGENTS.md`'s "Creating a node" step 8.

## STEP 4 — Validate: zero new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py`, capture output.
Temporarily move the new file aside, re-run, confirm the FAIL set is identical
to the pre-existing baseline, then restore the file.

Done when: new file produces zero new FAIL lines relative to baseline.

## STEP 5 — Commit

Run the corpus unittest suite as the sole content of one Bash call, then stage
and commit both the node and this plan file with `-s`, per the task's exact
two-call sequence.

Done when: `git log -1` shows the new commit on
`task/1276-relay-mesh-bootstrap`.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with no
  new FAIL entries versus the pre-existing baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` reports `OK`.
- Every evidence citation points to a real file actually opened this session.

## OPEN

- Whether a future `platforms.md` template (once merged) will ask for
  different section names than `component.md`'s borrowed shape — flagged in
  the node's own body as expected-but-not-verified, not resolved here.

## LEFT OUT

- Documenting `buzz-relay-mesh`'s internal wire protocol, gossip algorithm
  (phi-accrual failure detection), or QUIC/iroh transport details — those are
  a second concept (the mesh transport crate itself) and belong in a future,
  separate node, not folded into this bootstrap-procedure document.
- Documenting huddle-audio-specific consumer logic (`audio::mesh`,
  `audio::join`) beyond naming them as dependents — that is huddle audio's own
  domain, already partially covered by `architecture/flows/huddle-audio.md`.
- Any change to runtime behavior, config defaults, or the `/_mesh` endpoint.

# Plan: issue #802 — document capabilities/pairing/pairing-relay.md

## ALREADY TRUE

- `crates/buzz-pair-relay` exists: `src/lib.rs` (1025 lines) implements the
  relay logic, `src/main.rs` (27 lines) is the binary entrypoint, and
  `tests/integration.rs` (1393 lines) exercises the protocol.
- The crate is a workspace member (`Cargo.toml:27`) and is built into the
  main container image (`Dockerfile:80,87,179,186`).
- The Helm chart ships an optional `pairingRelay` Deployment/Service
  (`deploy/charts/buzz/templates/pairing-relay.yaml`,
  `deploy/charts/buzz/values.yaml:214-230`), disabled by default
  (`enabled: false`).
- `launchpad/docs/corpus/capabilities/pairing/pairing-relay.md` does not
  exist yet (confirmed via `test -f`). No `capabilities/` directory exists
  in the corpus at all on `origin/launchpad` yet, so no sibling capability
  node (device-pairing, pairing-cli, pairing-session) is loadable — no
  `relationships` block is safe to declare.
- Several already-merged corpus nodes describe `buzz-pair-relay` from other
  angles (context/deployment), which are usable as corroborating evidence
  but not as `relationships` targets (none of them are `type: capabilities`
  nodes for this specific capability): `architecture/context/nostr-network.md`,
  `architecture/deployment/{hosted-topology,multi-relay,single-relay}.md`,
  `architecture/containers/mobile.md`.
- A known, already-documented discrepancy exists between the crate's doc
  comment ("binds loopback only") and the Helm chart's actual bind
  (`0.0.0.0`, `deploy/charts/buzz/templates/pairing-relay.yaml:38`) — flagged
  in `launchpad/docs/audits/audit-2026-08-18-full-ecosystem.md` (M23). This
  belongs in the capability doc's boundary/scope section as an accuracy
  caveat, not silently smoothed over.
- 21 pre-existing `validate.py` FAIL entries exist on `origin/launchpad`
  unrelated to any capability doc (tracked in #1951) — baseline, not
  something this task fixes.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/pairing/pairing-relay.md` using
`launchpad/docs/corpus/templates/capability.md`'s skeleton:
`id: capabilities-pairing-pairing-relay`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
operator, reviewer]`. Body: capability statement (what pairing a second
device does for a user, via `buzz-pair-relay`), maturity (shipped — cite
crate, Dockerfile, Helm chart, tests), boundary (not NIP-AB protocol
itself, not `buzz-pairing-cli`, not the device-pairing capability overview,
not how it's deployed/operated), relationships (none — no capability
sibling nodes merged yet), scope and omissions (including the loopback vs.
`0.0.0.0` chart discrepancy as "expected but not verified"/caveat).

Evidence: `path:line`/`path:start-end` citations only, no `#symbol=`
fragments. FACT claims cite crate source, `Cargo.toml`, `Dockerfile`,
Helm chart files, and `crates/buzz-core/src/pairing/NIP-AB.md`.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm
zero new FAIL entries beyond the known 21 pre-existing ones (#1951).

## STEP 3 — Commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Only then stage the new doc + this plan file and commit with
`git commit -s`.

## GATES

- `validate.py` introduces zero new FAIL entries.
- `unittest discover` on corpus tests reports `OK`.
- Exactly one hand-authored canonical document created.

## BUDGET

Single file, single commit. No code changes, no PR, no push.

## OPEN

- Whether `buzz-pair-relay`'s loopback-doc-vs-chart-0.0.0.0 discrepancy
  (M23) gets its own follow-up issue is not this task's call — it is noted
  as a caveat in the new node's scope/omissions section only.

## LEFT OUT

- No `relationships` block: no capability-shaped sibling node
  (device-pairing, pairing-cli, pairing-session) is merged to
  `origin/launchpad` at this revision.
- No edits to any other corpus file.
- No fix to the loopback/0.0.0.0 discrepancy itself — documented as a caveat
  only, per this task's scope (docs, not runtime behavior).

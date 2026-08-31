# Plan: issue #803 — document capabilities/pairing/pairing-session.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/pairing/pairing-session.md` does not exist
  (confirmed: `launchpad/docs/corpus/capabilities/` has no `pairing/` subdirectory yet).
- `node.schema.json`'s `type` enum has no `data-entity` value — the four sibling
  issues (#800-#803) all carry the identical corpus-plan DoD boilerplate
  ("States the capability and primary actors/outcomes... Links verification
  demonstrating the capability"), which is the `type: capabilities` shape per
  `launchpad/docs/corpus/templates/capability.md`. This resolves the dispatch
  note's data-entity-vs-capabilities ambiguity: `type: capabilities` is correct.
- The pairing session state machine lives at
  `crates/buzz-core/src/pairing/session.rs` (`PairingSession`, `Role`,
  `SessionState`), used by both `crates/buzz-pairing-cli/src/main.rs` (Rust
  interop test tool) and `desktop/src-tauri/src/commands/pairing.rs` (shipped
  desktop feature). Mobile (`mobile/lib/features/pairing/`) is an independent
  Dart re-implementation of the client side, not a consumer of this Rust type.
- Two merged corpus nodes on `origin/launchpad` already discuss device pairing
  at the architecture level: `architecture-context-nostr-network` (context
  diagram: pairing peers talk to `buzz-pair-relay`) and
  `architecture-containers-mobile` (mobile's `PairingSocket`). Both are valid
  `references` targets.

## STEP 1 — Draft the corpus node

Write `launchpad/docs/corpus/capabilities/pairing/pairing-session.md`,
`type: capabilities`, describing the pairing-session capability: two ephemeral
per-session secp256k1 keypairs, a 32-byte session secret, HKDF-derived
session ID / SAS / transcript hash, the `SessionState` state machine
(Waiting → Confirming/AwaitingConfirmation → Transferring →
PayloadExchanged → Completed, or Aborted from any non-terminal state), the
120s hard timeout, and the actors (source device holding the secret, target
device receiving it). Cite `crates/buzz-core/src/pairing/session.rs`,
`crypto.rs`, `mod.rs` (PairingError), `qr.rs`, and the NIP-AB spec doc.
Follow the capability template's required sections (Capability statement /
Maturity / Boundary / Relationships / Scope and omissions).

Done when: file exists, front matter schema-valid by inspection against
`node.schema.json`, every DoD bullet in #803 addressed.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Fix anything it flags. Confirm zero *new* FAIL entries versus the
21-error baseline tracked in #1951.

Done when: exit code inspected and new-FAIL-count is 0.

## STEP 3 — Earn the commit gate and commit

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then `git add` the node + this plan file and commit with
`git commit -s`.

Done when: commit SHA exists on `task/803-pairing-session`.

## PARALLEL

None — single-file task, no parallelizable sub-work.

## GATES

- `validate.py` clean (no new FAIL).
- `unittest discover` on corpus tests prints `OK` before commit.
- Commit is signed off (`-s`); no `--no-verify`.

## BUDGET

Single node, capped at the three steps above. No second document, no
relationship to unmerged sibling issues (#800-#802).

## OPEN

- Whether `#800`/`#801`/`#802` will later add relationships back to this node
  once all four merge — not this task's decision; AGENTS.md step 9 requires
  relationship targets to already be merged on the branch being merged into.

## LEFT OUT

- No changes to `crates/buzz-pair-relay` or `crates/buzz-pairing-cli` docs —
  those are #802 and #801's own nodes.
- No relationship declared to `#800`/`#801`/`#802` (device-pairing,
  pairing-cli, pairing-relay) — unmerged siblings, not valid targets today.

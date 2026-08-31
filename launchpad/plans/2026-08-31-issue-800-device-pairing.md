# Plan: issue #800 — document capabilities/pairing/device-pairing.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/pairing/device-pairing.md` does not exist (confirmed via `test -e`).
- No `capabilities/` directory exists anywhere under `launchpad/docs/corpus/` yet on `origin/launchpad` — this is the corpus's first capability-shaped node.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`) is merged and gives a required skeleton: Capability statement, Maturity, Boundary, Relationships, Scope and omissions.
- The protocol is fully specified at `crates/buzz-core/src/pairing/NIP-AB.md` (NIP-AB, `draft`/`optional`, kind `24134`) and implemented across `buzz-core::pairing` (crypto/qr/session/types, 71 tests), `buzz-pair-relay` (sidecar relay, integration tests), `buzz-pairing-cli` (interop CLI: `source`/`target`/`test-vectors`), desktop (`commands/pairing.rs`, `MobilePairingCard.tsx` send-identity flow, `IdentityRecoveryPairing.tsx` recover-identity flow) and mobile (`lib/features/pairing/*`, 4 test files).
- Three merged corpus nodes already describe pieces of this from their own surface: `architecture-context-nostr-network` (context diagram, pairing-relay peer), `architecture-containers-mobile` (mobile pairing feature detail), `architecture-deployment-multi-relay` (pairing-relay's k8s deployment). This capability node references them rather than repeating their content.
- Siblings #801 (pairing-cli), #802 (pairing-relay), #803 (pairing-session) are separate, not-yet-drafted tasks — out of scope here, named as gaps in Scope and omissions, not folded in.

## STEP 1 — Draft the capability node

Write `launchpad/docs/corpus/capabilities/pairing/device-pairing.md` against the `capability.md` template: Capability statement (what a user/agent can do — move a Nostr identity or bootstrap a signer session to a second device, without trusting the relay), Maturity (implementation ships across desktop/mobile/CLI with tests; the underlying NIP itself is `draft`/`optional` and unaudited — state both, cited), Boundary (not architecture/how-it's-built, not an interface node — none exists yet for pairing's CLI/Tauri surface — not the step-by-step flow, not operations), Relationships (`references` the three existing nodes above), Scope and omissions (naming #801/#802/#803 as the not-yet-drafted neighbors).

**Done when:** file exists, front matter validates against `node.schema.json`'s seven fields, every DoD bullet in issue #800 is addressed in the body.

## STEP 2 — Validate and test-gate

Run `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAIL entries beyond the tracked 21 pre-existing (issue #1951). Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own call — must print `OK`.

**Done when:** both commands pass cleanly.

## STEP 3 — Self-review and commit

Re-read the diff against #800's DoD line by line, re-open every cited source, confirm no second canonical document was created, confirm relationship targets resolve against `origin/launchpad`. Commit with `git commit -s`. Do not push, do not open a PR — a later integration phase folds this into one Feature #613 PR.

**Done when:** commit exists on `task/800-device-pairing`, working tree clean.

## GATES

- `node.schema.json` front-matter validation (via `validate.py`).
- `launchpad/project-intelligence/corpus/tests` unit suite must print `OK` before commit.
- No `relationships[].target` may name an id absent from `origin/launchpad`'s corpus tree.

## BUDGET

3 steps, single node, no code changes — this is a documentation-only task capped well under any size ceiling.

## OPEN

- Whether `#1338` (flow template, not yet drafted) will later host a step-by-step pairing flow node this capability node could `references` — left as a named gap, not resolved here.

## LEFT OUT

- Interface-level documentation of `buzz-pairing-cli`'s subcommands or the desktop Tauri command surface (`start_pairing`, `confirm_pairing_sas`, `cancel_pairing`, `start_identity_recovery_pairing`) — that is #801/an interface node's territory, not this capability node's.
- Any change to runtime pairing behavior, the NIP-AB spec text, or its audit status.
- Re-litigating the three existing corpus nodes' content — cited via `references`, not restated.

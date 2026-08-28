# Plan: issue #1029 — document layers/authentication/nip-98-authentication.md

## ALREADY TRUE

- Parent PRD #607, feature F04-IDENTITY-SECURITY. Issue #1029's DoD is the
  generic corpus-node checklist plus concept-shaped bullets (define the term,
  state boundaries, link related concepts, examples clarify only).
- `launchpad/docs/corpus/layers/authentication/` does not exist yet on
  `origin/launchpad` — this is the first node in that directory.
- `launchpad/docs/corpus/templates/concept.md` is merged and its Required
  Sections map directly onto #1029's concept-shaped DoD bullets.
- Sibling issue #1027 (`bearer-token.md`) targets the same directory but its
  file does not exist on disk yet — checked via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, so
  no relationship can target it.
- `architecture-flows-websocket-authentication` (NIP-42) already exists on
  `origin/launchpad` and is a legitimate `references` target for the
  HTTP-vs-WebSocket boundary.
- Real source evidence for the mechanism lives in `crates/buzz-auth/src/nip98.rs`
  (`verify_nip98_event`), `crates/buzz-auth/src/nip98_replay.rs` (replay guard),
  `crates/buzz-relay/src/api/bridge.rs` (generic HTTP bridge), and
  `crates/buzz-relay/src/api/git/transport.rs` (git smart HTTP, with two
  documented deviations from the generic path).

## STEP 1 — Gather evidence

Read `nip98.rs`, `nip98_replay.rs`, `bridge.rs`, `git/transport.rs`,
`buzz-media/src/auth.rs` (the sibling Blossom kind:24242 mechanism, to state
the boundary correctly), `buzz-core/src/kind.rs` (kind 27235 constant), the
client-side signer in `buzz-cli/src/client.rs`, and
`docs/multi-tenant-conformance.md`'s NIP-98 row. Record `git rev-parse HEAD`.
Done when: every claim in the drafted evidence ledger cites a source that was
actually opened.

## STEP 2 — Scaffold and draft the node

Hand-build the manifest row (no persisted ledger file exists for this batch;
reconstructed from the issue body and the concept template's fit) and call
`scaffold.scaffold_node` with `template="concept"`, `node_type="layers"`,
`origin="upstream"`. Fix the derived `id` to the task-mandated
`layers-authentication-nip-98-authentication`. Write the body: Definition,
a Mermaid sequence diagram, Use cases, a Comparison table (NIP-98 vs NIP-42
vs Blossom vs dev-mode `X-Pubkey`), the replay-protection and multi-tenant
sections, and Scope and omissions (naming the #1027 gap and the unverified
client call sites). Add one `references` relationship to
`architecture-flows-websocket-authentication`.
Done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

## STEP 3 — Verify against the DoD

Re-read the diff against every #1029 checklist bullet and re-open every cited
source to confirm it supports its claim. Confirm no second hand-authored
canonical document exists in the diff.
Done when: every DoD bullet has a concrete answer and `validate.py` is clean.

## STEP 4 — Test, commit, PR

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own command, confirm `OK`, then commit (`git commit -s`) and open a
draft PR closing #1029.
Done when: PR is open, draft, and its body states validation + unittest
results and that review is self-review pending the batch owner's pass.

## GATES

- `validate.py` exit 0 (STEP 2, re-confirmed STEP 3).
- Corpus unittest suite `OK` (STEP 4), run as the sole command in its own
  tool call, no `--no-verify`.

## OPEN

- Whether #1027's `bearer-token.md` should later add a relationship back to
  this node once both exist — left for whichever author merges second.

## LEFT OUT

- Documenting the general bearer-token pattern (#1027's scope).
- Documenting Blossom's kind:24242 auth event in full (a separate node's
  scope; only contrasted here).
- Any runtime behavior change — this is documentation only.

# Plan: issue #1169 — document layers/security/cryptographic-boundary.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/security/cryptographic-boundary.md` does not exist
  anywhere in this worktree or on `origin/launchpad`.
- `launchpad/docs/corpus/templates/invariant.md` exists and is the closest-fitting
  template: issue #1169's DoD (state the invariant as one unambiguous property,
  explain scope, name enforcement points and observable failure behavior, link a
  verification/conformance mechanism or record it missing) is verbatim the same
  shape `invariant.md` prescribes and that `architecture/principles/signed-events.md`
  and `architecture/principles/community-is-security-boundary.md` already use.
  No `security` or `layers`-specific template exists, so `invariant.md` is used as
  reference structure, written directly against `node.schema.json`.
- `architecture-principles-signed-events` (signature verification) and
  `architecture-principles-community-is-security-boundary` (host-derived tenancy,
  not itself cryptographic) both exist on `origin/launchpad` and are valid
  `relationships[].target` values today.
- Three concrete cryptographic mechanisms were located and read directly at
  revision `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`:
  1. Event signature verification — `crates/buzz-core/src/verification.rs`
     (`verify_event`), already the subject of `signed-events.md`.
  2. Audit-log hash chain — `crates/buzz-audit/src/hash.rs` (`compute_hash`) and
     `crates/buzz-audit/src/service.rs` (`AuditService::log`, `verify_chain`).
     `verify_chain` has no production caller anywhere under `crates/` (confirmed
     by repo-wide grep) — only its own unit tests and one `#[ignore]`d
     integration test in `buzz-relay/src/handlers/event.rs` call it.
  3. NIP-AB device-pairing payload encryption — `crates/buzz-core/src/pairing/session.rs`
     (`nip44::encrypt` in `build_event`, `nip44::decrypt` in `decrypt_message`),
     specified in `crates/buzz-core/src/pairing/NIP-AB.md`.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/layers/security/cryptographic-boundary.md`:
`id: layers-security-cryptographic-boundary`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`. State one
boundary property: exactly three things in Buzz are cryptographically verified
(event signature/id, audit-log entry hash-chain integrity, NIP-AB pairing-payload
confidentiality under NIP-44 v2) and everything else is trusted, not proven. Cite
only sources opened this session. `references` to the two existing sibling nodes
above; no other relationships (nothing else on `origin/launchpad`'s corpus tree is
a topical neighbor).

**Done when:** file exists, front matter is schema-valid by inspection, every
evidence entry cites a source actually opened this session.

## STEP 2 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py` (expect exit 0),
then `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own command (expect `OK`).

**Done when:** both commands pass with no edits needed, or edits are made and
both are re-run clean.

## STEP 3 — Commit, push, open draft PR

`git commit -s`, push branch, `gh pr create --draft` with `Closes #1169`, noting
self-review only and the batch-owner deferred-review line.

**Done when:** PR URL exists and issue number is reported back.

## GATES

- `validate.py` exit 0 before commit.
- Corpus unittest suite `OK` before commit (commit-gate stamp).
- No second hand-authored canonical document created.

## OPEN

- Whether `verify_chain`'s complete lack of a production/operator caller should
  itself become a separate follow-up issue (e.g., an admin CLI command) is noted
  in the node's scope-and-omissions but not filed as a new task here — it is an
  existing gap, not a newly discovered second concept this node's own scope needs
  to fold in.

## LEFT OUT

- No new tests, no runtime changes, no second corpus document.
- Not auditing every `AuditService::log` call site's `actor_pubkey` provenance
  exhaustively — noted as a verification gap in the node instead.

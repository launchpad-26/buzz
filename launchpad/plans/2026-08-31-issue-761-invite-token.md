# Plan: issue #761 — document capabilities/invites/invite-token.md

## ALREADY TRUE

- `crates/buzz-core/src/invite.rs` defines the v2 opaque invite-code contract
  (`V2_PREFIX`, `V2_SECRET_LEN`, `encode_v2_code`, `validate_v2_code`, `hash_v2_code`)
  shared by relay and DB layers.
- `crates/buzz-relay/src/invite_token.rs` defines the v1 stateless HMAC-signed
  bearer token (`InvitePayload { c, r, e, n }`, `derive_invite_key`, `verify_invite`)
  and a separate `PolicyAcceptancePayload` HMAC receipt. `mint_invite` (v1 minting)
  is `#[cfg(test)]`-only; production minting is v2.
- `migrations/0025_relay_invites.sql` defines `relay_invites` (community_id, id,
  token_hash BYTEA(32), role pinned 'member', max_uses, use_count, expires_at,
  created_by, created_at) storing only the SHA-256 hash of a v2 code.
- `crates/buzz-relay/src/api/invites.rs` routes `claim_invite` by prefix: `v2.` →
  DB-backed path, everything else → v1 HMAC verification (no v1 minting route
  remains).
- No corpus node yet exists for any invite-related subject on `origin/launchpad`
  (confirmed via `git ls-tree -r origin/launchpad -- launchpad/docs/corpus`), so
  no `relationships` target is available.
- `node.schema.json`'s `type` enum has 13 members; issue #761's own DoD text
  ("States the capability and primary actors/outcomes... Links verification
  demonstrating the capability") is the capability-shaped DoD boilerplate, not
  the data-entity-shaped one (identity/attributes/invariants/relationships/
  provenance/storage) — `templates/capability.md` is the applicable template,
  so `type: capabilities`.

## STEP 1 — Confirm target path is free and scope boundary

`launchpad/docs/corpus/capabilities/invites/invite-token.md` does not exist.
Scope: the invite token's own structure and lifecycle (two formats: v1
stateless HMAC bearer, v2 opaque database-backed; what each carries; how each
is verified/looked up) — explicitly excluding expiry policy mechanics (#759),
the redemption/claim transaction workflow (#760), and the overall invite
capability bundling mint+claim+policy (#762).

Done-when: `ls` confirms no existing file at that path; the four sibling issue
numbers are recorded here as the boundary.

## STEP 2 — Draft the node

Front matter: `id: capabilities-invites-invite-token`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
no `relationships` (nothing to target on `origin/launchpad`). Evidence ledger
cites `crates/buzz-core/src/invite.rs`, `crates/buzz-relay/src/invite_token.rs`,
`migrations/0025_relay_invites.sql`, `crates/buzz-relay/src/api/invites.rs`, and
the shipped-PR commits for maturity.

Body follows `templates/capability.md`'s required sections: Capability
statement, Maturity, Boundary, Relationships, Scope and omissions.

Done-when: file exists with schema-shaped front matter and all required
sections present.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.

Done-when: exit 0, and the new node introduces zero new FAIL entries (21
pre-existing FAILs on `origin/launchpad`, tracked in #1951, are out of scope).

## STEP 4 — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call; confirm `OK`.
Then `git add` the new doc + this plan file and `git commit -s`.

Done-when: commit created locally; no push, no PR.

## STEP 5 — Self-review

Re-read the diff against #761's DoD line by line; re-open every cited source;
confirm no second canonical doc was created; confirm no new validate.py FAIL
entries; note `review-code`/`review-adjudicate` were not run (deferred per
batch mode).

## PARALLEL

None — single-file, single-issue task.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`.

## BUDGET

Small: one new corpus doc (~150-250 lines), one plan file, one commit.

## OPEN

- Whether `type: capabilities` is the durable right fit for a token-shaped
  subject is unresolved by any merged standard (`corpus-standard-taxonomy.md`
  is not yet merged to `origin/launchpad`); disclosed in the node's own Scope
  and omissions section per the taxonomy standard's own guidance for an
  imperfect fit.

## LEFT OUT

- Expiry TTL bounds/defaults and their policy rationale (#759's scope).
- The claim/redemption transaction (rate limiting, `FOR UPDATE`, atomic
  use_count increment, membership insertion) (#760's scope).
- The invite capability as a whole (mint + claim + join-policy acceptance
  bundled) (#762's scope).

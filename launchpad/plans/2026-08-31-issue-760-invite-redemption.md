# Plan: issue #760 — document capabilities/invites/invite-redemption.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/invites/invite-redemption.md` does not exist
  on `origin/launchpad` (confirmed: `find` on a fresh worktree returns nothing).
- No `capabilities/invites/` directory exists yet in the corpus tree — this is the
  first node under that path.
- `launchpad/docs/corpus/templates/flow.md` is merged to `origin/launchpad`
  (`corpus-template-flow`, `type: governance`) and is the authoritative shape for a
  step-by-step flow node: `type: architecture` (schema has no `flow` enum member),
  required sections Flow statement / Sequence / Diagram (Mermaid `sequenceDiagram`)
  / Outcome / Boundary statement / Relationships / Scope and omissions.
- The redemption code path is fully read and understood:
  - `crates/buzz-relay/src/api/invites.rs::claim_invite` (line 357) — the HTTP
    handler, NIP-98-authenticated, rate-limited per `(community, pubkey)`.
  - v2 (current) path: `validate_v2_code` → `hash_v2_code` →
    `buzz_db::store::relay_invite::claim_relay_invite` (transactional, `FOR UPDATE`,
    checks expiry → membership → capacity → insert → increment).
  - v1 (legacy HMAC) path: `invite_token::verify_invite` (line 156) → optional
    join-policy receipt check → `claim_relay_membership`.
  - Success side effects: `publish_nip43_member_added` /
    `publish_nip43_membership_list` (NIP-43 deltas), only on `Joined`.
  - Client callers: `desktop/src/shared/api/invites.ts` +
    `desktop/src/features/onboarding/useClaimInvite.ts` (Tauri/desktop),
    `web/src/features/invite/invite-api.ts` (browser, NIP-07 signing).
  - Tests: `claim_rejects_invalid_code`, `claim_rejects_expired_code`,
    `claim_rejects_replayed_nip98_auth`, `claim_rate_limit_fires_on_repeat_pubkey`,
    `bounded_v2_claims_publish_side_effects_only_for_joined`,
    `owner_mints_and_new_pubkey_claims`.
  - Route: `POST /api/invites/claim` (`crates/buzz-relay/src/router.rs:123`).
- Four `architecture-containers-*` nodes already merged and relevant as `references`
  targets for this flow's actors: `architecture-containers-relay`,
  `architecture-containers-postgres`, `architecture-containers-desktop`,
  `architecture-containers-web`. No `capabilities`- or `interfaces-events`-typed
  sibling node exists yet (issues #759/#761/#762 are separate, unmerged tasks), so
  no relationship targets them.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/invites/invite-redemption.md` following
the flow template skeleton exactly: front matter (`id:
capabilities-invites-invite-redemption`, `type: architecture`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`), evidence ledger
citing the commit and every code path read above, `relationships` to the four
architecture container nodes. Body: Flow statement, Sequence (v2 path as primary,
v1 path noted as legacy), Diagram (Mermaid `sequenceDiagram`), Outcome (success +
each failure/rejection branch: invalid, expired, exhausted, already_member,
join_policy_required, rate-limited, NIP-98 replay), Boundary statement (not
architecture, not capability, not interface, not event-kind — scoped strictly to
the redemption flow, distinct from #759 expiry-as-a-concept and #761
invite-token-as-a-data-entity), Relationships, Scope and omissions.

**Done when:** file exists, front matter is schema-valid, every substantive claim
has a citation opened for real, all DoD bullets in issue #760 are satisfied.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with zero new
  FAIL entries versus the known 21-error baseline (issue #1951).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.

## BUDGET

One step. No parallelism needed — single hand-authored file.

## OPEN

- None — the code path, template, and target path are all unambiguous.

## LEFT OUT

- The invite capability itself (#762), the invite-token data entity (#761), and
  invite expiry as its own concept (#759) — this node only `references` them if
  they already exist merged (they do not yet), and never restates their content.
- Any runtime behavior change. Documentation only.

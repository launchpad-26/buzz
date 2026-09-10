# Plan: issue #1274 — document platforms/relay/invite-api.md

## ALREADY TRUE

- Parent Feature #614 ("runtime platform corpus exists") batch, target document
  `launchpad/docs/corpus/platforms/relay/invite-api.md` does not yet exist
  (confirmed: `launchpad/docs/corpus/platforms/` has no `relay/` subdirectory
  on this branch, checked out from `origin/launchpad` at
  `131b02f989684117d9ab1dd426f1673fa638e523`).
- No `templates/platforms.md` exists in `launchpad/docs/corpus/templates/`
  (verified by listing the directory). Per sibling-batch convention (finding
  #4 in this task's brief), documents under `platforms/**` use
  `type: platforms` with `component.md`'s section shape borrowed as an
  INFERENCE, since no platforms-specific template has landed.
- `launchpad/docs/corpus/architecture/containers/web.md` (id
  `architecture-containers-web`) already documents the invite-related surface
  from the **web client's** side: the `/invite/<code>` landing route and
  `web/src/features/invite/invite-api.ts`'s `POST {relay}/api/invites/claim`
  call. It explicitly does not cover the relay-side handler implementation.
- `launchpad/docs/corpus/architecture/flows/git-push.md` names "the
  invite/community-provisioning flow that makes a pusher a channel member" as
  an explicit gap, owned by "separate architecture/flow nodes, none of which
  exist in the merged corpus at this revision" — still true; no flow node
  covers relay-side invite handling either.
- The relay's actual invite HTTP API lives in
  `crates/buzz-relay/src/api/invites.rs` (handlers + routes), backed by two
  token schemes: `crates/buzz-relay/src/invite_token.rs` (stateless v1 HMAC
  codes, compatibility-only path) and `crates/buzz-db/src/store/relay_invite.rs`
  (durable v2 opaque database-backed codes, the production minting path).
  Shared constants/validation live in `crates/buzz-core/src/invite.rs`. Routes
  are registered in `crates/buzz-relay/src/router.rs`.

## STEP 1 — Gather evidence

Read, in full: `crates/buzz-relay/src/api/invites.rs` (handlers, request/
response shapes, auth, rate limiting), `crates/buzz-relay/src/invite_token.rs`
(v1 HMAC format, key derivation, security properties), `crates/buzz-db/src/
store/relay_invite.rs` (v2 schema, atomic claim transaction, `ClaimOutcome`),
`crates/buzz-core/src/invite.rs` (shared constants, v2 code validation), the
route table in `crates/buzz-relay/src/router.rs`, and `JoinPolicyConfig` in
`crates/buzz-relay/src/config.rs`. Record repository revision
`131b02f989684117d9ab1dd426f1673fa638e523`.

**Done when:** every substantive claim in the drafted node traces to a file
and line/symbol actually opened above.

## STEP 2 — Draft the node

Hand-author `launchpad/docs/corpus/platforms/relay/invite-api.md` against
`node.schema.json` directly (no `platforms.md` template exists — say so in
the body per `AGENTS.md`'s documented no-template path), borrowing
`component.md`'s section shape (Responsibility / Public interface /
Dependencies / Boundary / Relationships / Scope and omissions) per this
Feature's settled sibling convention. Front matter: `id:
platforms-relay-invite-api`, `type: platforms`, `status: draft`, `origin:
launchpad`, `audiences: [agent, developer, reviewer]`, one evidence entry per
claim plus the commit-citation provenance entry.

**Done when:** front matter validates against the schema shape and every DoD
bullet from issue #1274 is addressed in the body (responsibility/boundary,
dependencies/collaborators, source+test links, component-level scope only).

## STEP 3 — Relationships

Add `references: architecture-containers-web` (confirmed present on
`origin/launchpad`) since that node already covers the client-side half of
the same flow and this node is scoped to not duplicate it. No other existing
corpus node covers relay-side invite handling, so no other relationship
target is available yet.

**Done when:** `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` confirms the target file exists there.

## STEP 4 — Validate and earn the commit gate

Run the corpus unittest suite, confirm `validate.py` introduces zero new FAIL
lines versus the pre-existing baseline (stash-and-compare), then commit in
two separate tool calls per this task's fixed procedure.

**Done when:** unittest discover reports `OK`, `validate.py`'s FAIL set is
unchanged from baseline, and the commit succeeds with a verification stamp.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK
- `python3 launchpad/project-intelligence/corpus/validate.py` → zero new FAILs vs. baseline
- Commit gate stamp present

## OPEN

- Whether a future `architecture-flows-invite` (or similarly named) node will
  want to `depends-on` or `references` this node once written — not resolved
  here; today no such node exists to link.
- Whether v1 HMAC invite codes are fully retired before this node's recorded
  revision goes stale — the source comments call the v1 path a "compatibility
  drain window" without a concrete removal date.

## LEFT OUT

- No new corpus node for `invite_token.rs`'s v1 format or `relay_invite.rs`'s
  v2 schema as *separate* nodes — both are internal implementation detail of
  the one platform-level invite API surface this task scopes to, not
  independently maintainable ideas of their own.
- No relay_invites table schema/migration node — out of scope per issue
  #1274's "Out of scope" section (no second hand-authored canonical document).

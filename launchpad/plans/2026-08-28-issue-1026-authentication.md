# Issue #1026: docs(corpus) — layers/authentication/authentication.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `AGENTS.md`, and
`launchpad/docs/corpus/templates/concept.md` (merged, real) are present at HEAD
`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`. The target file
`launchpad/docs/corpus/layers/authentication/authentication.md` does not exist (the
`layers/` directory itself does not exist yet on `origin/launchpad`). No sibling
mechanism docs (api-token, bearer-token, nip-42-authentication, nip-98, etc.) exist in
the corpus yet — confirmed via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`. One directly relevant sibling node already exists and is
mergeable to reference: `architecture/flows/websocket-authentication.md`
(id `architecture-flows-websocket-authentication`), which already documents the NIP-42
challenge/response flow end-to-end. This node must not duplicate that content — it
covers the *shared shape of authentication in Buzz* (identity model, the multiple
mechanisms, the common invariants) and defers flow-level detail to that sibling and to
future mechanism-specific nodes.

STEP 1 — gather evidence (done during planning, re-confirmed before drafting): read
`crates/buzz-auth/src/lib.rs` (module doc: NIP-42/NIP-98 paths table, security
invariants, `AuthContext`, `AuthService`), `crates/buzz-auth/src/error.rs`
(`AuthError` variants), `crates/buzz-auth/src/scope.rs` (`Scope` enum, `all_known`,
`all_non_admin`, dev-mode X-Pubkey comment), `crates/buzz-auth/src/access.rs`
(`ChannelAccessChecker`, `require_scope`), `crates/buzz-core/src/kind.rs`
(`KIND_AUTH`=22242, `KIND_HTTP_AUTH`=27235), `crates/buzz-relay/src/api/bridge.rs`
(`verify_bridge_auth_with_options`: NIP-98 first, X-Pubkey dev-mode fallback only when
`require_auth_token` is false), `crates/buzz-db/src/api_token.rs` (API token storage:
create/list/revoke, `(community_id, token_hash)` scoping), and
`crates/buzz-test-client/tests/conformance_multitenant.rs` (api_tokens row — notes no
self-service mint HTTP route exists, and a test-comment claim that `media.rs:638`
consumes API tokens via an `X-Auth-Token` header). Grepped `X-Auth-Token` repo-wide:
**zero matches in any non-test source file** — the test comment does not match current
`media.rs` (line 638 there is Blossom/NIP-98 `authenticate_media_read`, not API-token
consumption). This is recorded as an unverified/stale claim in the node's scope
section, not asserted as fact.

STEP 2 — write front matter: `id: layers-authentication-authentication`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`, evidence ledger with one commit-citation FACT for the revision plus one
FACT/INFERENCE per substantive claim above, classified honestly (the api_tokens
consumption claim becomes an explicit "expected but not verified" note, not a FACT).
One `relationships` entry: `references` → `architecture-flows-websocket-authentication`
(confirmed present on `origin/launchpad`).

STEP 3 — write the body against `templates/concept.md`'s required sections
(Definition, Use cases, Scope/omissions; Background and Related-resources as useful):
define authentication as proof-of-identity via a Nostr keypair signature (no
passwords/JWTs/sessions/IdP), name the two current mechanisms (NIP-42 WebSocket
challenge/response, NIP-98 HTTP Authorization header) plus the API-token storage layer
and the dev-only X-Pubkey fallback, state the shared invariants (fail-closed on DB
error, community-scoped, authentication answers "who" while separate
scope/membership/ban gates answer "may they"), and explicitly route detail to the
sibling nip-42/nip-98/api-token/bearer-token nodes as *expected future siblings*
without fabricating their content. RUNS HERE.

STEP 4 — validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0 against the full corpus tree including the new file.

STEP 5 — earn the commit gate: run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call and confirm `OK`, then in a separate call stage and
commit the plan file plus the new document with `git commit -s`.

PARALLEL: none — single file, single task.

GATES: `validate.py` exits 0. The unittest suite above reports `OK` (required by the
repo's verify-gate hook, distinct from and in addition to `validate.py`). No
`check-plan.sh` was found anywhere under this worktree or session — proceeding without
it per the task's own instruction to not block on a missing tool.

BUDGET: single document, no code changes, no test changes; comparable in size to the
sibling `websocket-authentication.md` node but narrower in depth (category-level, not
flow-level).

OPEN: whether the `X-Auth-Token`/api_tokens HTTP consumption path described in
`conformance_multitenant.rs`'s comment ever existed at the referenced line, or was
aspirational/stale when written, is unresolved — this document states the discrepancy
rather than resolving it. Whether `type: layers` is the best-fitting enum value for an
authentication concept (versus `architecture` or `capabilities`) is judged against
`standards/taxonomy.md`'s guidance and the issue's own stated `layers/` target path,
and is disclosed as a judgment call in the node's scope section per that standard's
step-4 fallback ("if the fit is still imperfect after that, say so").

LEFT OUT: no runtime/product code change; no second canonical document; no
relationships to sibling mechanism nodes that do not exist yet on `origin/launchpad`
(api-token, bearer-token, nip-42-authentication, nip-98-authentication — named in prose
as expected future siblings instead); no per-type "layers" template exists as a
distinct thing beyond `concept.md`, so this node is written against `concept.md` plus
`node.schema.json` directly; `review-code`/cross-model adjudication deferred to the
batch owner per the task's own instructions.

# Issue #1023 — corpus doc: layers/authentication/api-token.md

ALREADY TRUE: `node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, and
`launchpad/docs/corpus/templates/concept.md` are merged on `launchpad`;
`launchpad/docs/corpus/layers/authentication/api-token.md` does not exist yet
(confirmed: no `layers/` directory exists under the corpus tree at all — this
is the first `type: layers` node). The issue's DoD tail ("defines the term in
one sentence", "states boundaries/non-goals", "links related concepts", "uses
examples only to clarify") matches the concept template's shape, so this node
is written as a concept, with `type: layers` per PRD #602's surface taxonomy
(the template's own note: `type` names the corpus surface, not the doc form).

STEP 1 — gather evidence: read `crates/buzz-db/src/api_token.rs` (CRUD,
community-scoped `(community_id, token_hash)` lookup, 10-token quota,
revocation), `migrations/0001_initial_schema.sql` (`api_tokens` table DDL),
`crates/buzz-auth/src/scope.rs` (the `Scope` enum tokens carry), and
`crates/buzz-relay/src/api/bridge.rs` (`require_auth_token` gates NIP-98 vs
`X-Pubkey` dev-mode fallback — a different mechanism, not api-token
consumption). Confirm via `crates/buzz-test-client/tests/conformance_multitenant.rs`
(`api_tokens_nip98_replay` module) and `git show 0701f47f4` (PR #1444, "remove
media bearer-token auth") that api tokens are currently **unconsumed**: no
`/tokens` mint route exists in `crates/buzz-relay/src/router.rs`, and the one
former consumer (`media.rs`'s `X-Auth-Token` scope check) was deleted by
#1444, leaving `get_api_token_by_hash`/`_including_revoked` called only from
`buzz-db`'s own unit tests. RUNS HERE — done; grep confirms zero production
callers remain outside `buzz-db/src/api_token.rs`.

STEP 2 — write front matter (`id: layers-authentication-api-token`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences:
[agent, developer, reviewer]`) and a concept-shaped body: one-sentence
definition, the token's shape (`buzz_*` string, SHA-256 hash stored,
community-scoped, pubkey-owned, scoped, revocable, quota-limited), its
boundary against NIP-98/NIP-42 signed-event auth (api-token is a would-be
secondary bearer credential, not Buzz's primary auth — that's Nostr-first
signed events per `architecture-principles-signed-events`), and the current
"implemented but unconsumed" status as the load-bearing fact a reader most
needs. `relationships`: `references` targeting
`architecture-flows-media-upload` (its history is the direct evidence for the
unconsumed-status claim) and `architecture-principles-community-is-security-boundary`
(the `(community_id, token_hash)` scoping is that principle's instance here)
— both ids confirmed present on `origin/launchpad` in Step 1's `ls`.

STEP 3 — run `python3 launchpad/project-intelligence/corpus/validate.py`;
fix and re-run until exit 0 against the full tree.

STEP 4 — run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
command in its own call, confirm `OK`, then commit (plan + doc), push, and
open a draft PR against `launchpad`.

PARALLEL: none — single hand-authored file, one worktree.

GATES: `validate.py` must exit 0. The corpus unittest suite must report `OK`
to earn the commit verification stamp. review-adjudicate and the cross-model
final-review pass are explicitly deferred to the batch owner's review — not
run in this worktree.

BUDGET: single document, no code changes, no test changes — small.

OPEN: none — two live relationship targets exist and are used (unlike some
sibling corpus-doc tasks written before any architecture-track node merged).

LEFT OUT: no per-type template for `type: layers` concept nodes beyond the
generic `concept.md` template exists yet, so this is written against
`node.schema.json` + `concept.md` + `AGENTS.md` directly, per `AGENTS.md`'s
own instruction, and may be reshaped by a later per-type template task.
Corpus generated indexes are not touched — none exist yet to regenerate.
Whether api tokens will ever gain a mint route or a new consumer is a product
decision this node does not make; it states the current fact and defers that
question, naming it explicitly as an omission in the body.

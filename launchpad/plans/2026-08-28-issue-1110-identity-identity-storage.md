# Issue #1110 — layers/identity/identity-storage.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md` is merged on `origin/launchpad`; no
`layers`-specific template exists in `launchpad/docs/corpus/templates/` (26 templates
present, none named `layers*`). `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` confirms `launchpad/docs/corpus/layers/` does not exist on
`origin/launchpad` at all — every sibling identity node (#1102 actor, #1103
agent-identity, #1105 device-pairing, #1106 human-identity, #1107 identity-archive,
#1108 identity-invariants) is still only an open, unmerged PR (#1803–#1812), so this
node cannot carry any `relationships` entry. `launchpad/docs/corpus/layers/identity/
identity-storage.md` does not exist yet in this worktree. Sibling PR #1808 (#1106,
human-identity) hand-authored its node directly against `node.schema.json` using the
`concept.md` template's shape (no per-type template exists), following the same
"absent altogether" path this node must take too.

STEP 1 Gather evidence across every custody surface. Desktop: `desktop/src-tauri/src/
secret_store.rs` (single-blob OS keychain, `SecretStore::load`/`store_all`/
`delete_all_with_legacy_cleanup`, legacy per-key DPK/keyring migration, cross-process
`flock`/mutex locking) and `desktop/src-tauri/src/managed_agents/storage.rs`
(`agent_keyring_name`, `migrate_inline_key`/`hydrate_keys`/`persist_agent_keys`: keyring
first, `0o600` JSON-file (`atomic_write_json_restricted`) inline-key fallback when the
keyring is unreachable, `spawn_key_refusal` fail-closed on an empty key). Mobile:
`mobile/lib/shared/community/community_storage.dart` (`flutter_secure_storage`, one
`buzz_communities` blob holding all `Community` records, each with its own `nsec`
field; legacy single-community migration). CLI: `crates/buzz-cli/src/lib.rs`
(`BUZZ_PRIVATE_KEY` env/`--private-key` arg, `hide_env_values`, required). Server/agent
surfaces: `crates/buzz-backend-kubernetes/src/env.rs` (`AUTHORITATIVE_KEYS`,
`BUZZ_PRIVATE_KEY`/`NOSTR_PRIVATE_KEY` written into a pod's env from
`agent.private_key_nsec`, never touching the provider's own disk) and
`docs/remote-agents.md` (`§System Model`, I1 identity-fail-closed, I2 "no secrets in
configuration", the deploy payload "never persisted by D and never rendered", the
K8s-Secret residual-exposure paragraph). Agent/git surface: `crates/buzz-dev-mcp/
src/shim.rs` (`write_keyfile_atomic`, ephemeral `0o600` `.nostr-key` file per session)
and `crates/git-sign-nostr/src/lib.rs` (env-var priority, `std::env::remove_var` after
consuming). Encrypted-at-rest event format: `crates/buzz-core/src/
private_managed_agent.rs` (`PrivateIdentity.private_key_nsec`, NIP-44 owner-self
decrypt, `KIND_PRIVATE_MANAGED_AGENT = 30179` in `crates/buzz-core/src/kind.rs`) —
confirm via `grep -rln "private_managed_agent\|PRIVATE_MANAGED_AGENT" --include="*.rs"
.` that no caller outside its own module/tests currently builds or decrypts one, so
this is named as a defined-but-unwired format, not a live path. ← RUNS HERE

STEP 2 [needs 1] Write front matter (schema-valid: id `layers-identity-identity-storage`,
type `layers` per the issue title, status `draft`, origin `launchpad`, audiences
`[agent, developer, reviewer]`, no `relationships` — nothing to link to per ALREADY
TRUE) using the `concept.md` template's shape (Definition, per-surface mechanics,
Comparison table, Scope and omissions) since no `layers`-specific template exists, and
say so explicitly in the body per `AGENTS.md`'s documented no-template path. Classify
every claim: source citations opened directly are FACT; any synthesis across surfaces
(e.g. "no surface persists a raw key beyond the shortest span its consumer needs") is
INFERENCE with a stated confidence; issue #1110's own DoD requirements are
TEAM_KNOWLEDGE. State explicitly that this node is the canonical, comprehensive
identity-storage treatment and that #1106 (human-identity) should end up referencing
this node rather than duplicating it — without editing #1106's file, which lives in a
different worktree/PR.

STEP 3 [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix
and re-run until exit 0.

STEP 4 [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole prior command
to earn the verification stamp, then commit the plan + document in a separate call,
push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model final review pass are deferred to the batch
owner's review — not run here (self-review only, stated explicitly in the PR body).

BUDGET: small-to-medium — one document, no code changes, evidence gathering spans
~9 source files/docs across desktop, mobile, CLI, and server/agent surfaces (wider
than a single-surface sibling node because this is explicitly the canonical
cross-surface treatment).

OPEN: Whether `crates/buzz-core/src/private_managed_agent.rs`'s NIP-44-encrypted
`KIND_PRIVATE_MANAGED_AGENT` (30179) event format has a caller this search missed, or
is genuinely unwired scaffolding, could not be fully resolved by grep alone — named as
"expected but not verified" rather than asserted either way. Whether Kubernetes'
own Secret-at-rest encryption (etcd-level, cluster-operator concern per
`docs/remote-agents.md`'s Non-Goals) belongs in this node at all, versus being purely a
substrate concern out of Buzz's control, is left as a boundary statement rather than
described in depth.

LEFT OUT: No relationship to any sibling identity node (#1102–#1108) — none are merged
on `origin/launchpad` yet. No description of the Kubernetes deploy state machine,
Secret garbage collection, or reconciliation loop beyond what establishes where the
key sits at each hop — that is `docs/remote-agents.md`'s own subject, cited but not
restated. No code changes to any storage/keyring/env-var path — documentation only.

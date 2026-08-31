# Plan: issue #684 — corpus doc `architecture/flows/push-notification.md`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`, and
`launchpad/docs/corpus/architecture/flows/push-notification.md` does not exist
at that tip (confirmed via `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus` — only `AGENTS.md`, `README.md`,
`standards/confidence.md`, `standards/decision-references.md` are present, no
`architecture/` subtree at all).

STEP 1 (RUNS HERE): Gather evidence for the push-notification flow — read
`docs/nips/NIP-PL.md` (normative spec), `docs/push-gateway-deployment.md`
(deployment/ops), `docs/formal/nip-pl/NOTE.md` and
`docs/formal/STATEFUL_GATEWAY.md` (formal models), the relay handlers
(`crates/buzz-relay/src/handlers/push_lease.rs`,
`crates/buzz-relay/src/push_runtime.rs`), the gateway crate
(`crates/buzz-push-gateway/src/{http,model,authority,apns,token}.rs`), the kind
registry (`crates/buzz-core/src/kind.rs`), and the DB trigger migrations
(`migrations/0018_push_match_queue.sql`, `migrations/0023_push_match_gate.sql`).
Cross-check git history to catch a stale claim (the formal note says the relay
matcher/worker is "not-yet-shipped"; git log shows it shipped later the same
day the note was added — the note is stale on this point).

STEP 2: Write front matter (id
`architecture-flows-push-notification`, type `architecture`, status `draft`,
origin `launchpad`, audiences `[developer, operator, agent]`, no
`relationships` — no architecture node exists yet to point at) and a body
covering: trigger/preconditions/termination, ordered interactions and
data/state movement, auth/trust-boundary crossings, and failure/abort/rollback
behavior with linked verification, per the issue DoD and the flows category
tail.

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py` from
repo root; fix and re-run until it exits 0.

STEP 4: Earn the verification stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole prior command, then commit the plan + node file in a separate
call.

PARALLEL: none — single document, single file, no fan-out.

GATES: `validate.py` must exit 0 locally before commit. The corpus unittest
suite (STEP 4) is the one that reliably earns this worktree's commit
verification stamp. `review-adjudicate` and any cross-model review pass are
explicitly deferred to the batch owner's morning review, not run in this
session.

BUDGET: single document, single commit, single draft PR — no fan-out, no
generated-index regeneration expected.

OPEN: the mobile (Flutter) and desktop (Tauri) apps have no push-lease client
code in this repository as of the recorded revision — no `30350`/`push_lease`/
App Attest references anywhere under `mobile/lib` or `desktop/src`, and no
push/notification feature directory in the mobile app. The relay + gateway
server-side flow is fully implemented and tested; client-side lease creation
exists only as normative spec text in `docs/nips/NIP-PL.md`. The issue's DoD
does not resolve whether this gap belongs in this flow node's scope-and-
omissions section or should be filed as a separate finding — this plan treats
it as an explicit omission in the node body rather than silently describing an
unbuilt client flow as if it existed.

LEFT OUT: no relationships to other corpus nodes (none exist yet to target);
no attempt to model the NIP-PL formal Python test suite's internals beyond
citing it as representative verification; no changes to generated corpus
indexes (none exist in this repo yet per AGENTS.md's `generated/` gap, #1316).

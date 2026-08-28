# Issue #1102 — layers/identity/actor.md

ALREADY TRUE: `launchpad/docs/corpus/templates/concept.md` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/layers/identity/actor.md` does not exist yet (confirmed: `launchpad/docs/corpus/layers/` has no `identity/` subdirectory). `architecture-principles-humans-and-agents-are-peers.md` is merged on `origin/launchpad` and states the invariant that authorization never branches on human/agent identity. Sibling tasks #1103 (agent-identity) and #1106 (human-identity) are open, undrafted — no files to link to yet.

STEP 1  Gather evidence: grep the codebase for the literal term `actor` (case-insensitive, whole word) across `crates/` and `docs/spec/`. Read the hits in `docs/spec/MultiTenantRelay.tla` (`Actors` as a formal CONSTANT — "finite set of pubkeys/actors"), `crates/buzz-conformance/src/lib.rs` (`ActorLabel`, `AbstractState.actor`), `crates/buzz-relay/src/conformance/mod.rs` (`state_for_request`/`actor_label`, derived from `nostr::PublicKey`), `crates/buzz-db/src/user.rs` (`is_agent_owner`'s `actor_pubkey` param), `crates/buzz-db/src/archived_identities.rs` (`ArchivedIdentity.actor`), and `crates/buzz-relay/src/handlers/moderation_commands.rs` (`actor = event.pubkey...`). Confirm `VISION.md` has zero occurrences of "actor" (it is an implementation/spec term, not product vocabulary). Re-open `migrations/0001_initial_schema.sql`'s `users` table and the peers node to confirm the human/agent-unification claim already established there before restating it here. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-identity-actor`, type `layers` per the issue title, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, one `relationships` entry: `references` → `architecture-principles-humans-and-agents-are-peers`, confirmed present on `origin/launchpad`) using the `concept.md` template's required sections (Definition, Use cases, Comparison, Related resources via `relationships`, Scope and omissions). Classify every claim honestly: the spec/code citations are FACT; "actor is a cross-cutting naming convention, not a distinct Rust type" is INFERENCE with a stated confidence; issue #1102's own DoD requirements are TEAM_KNOWLEDGE.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole prior command to earn the verification stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review — not run here (self-review only, stated explicitly in the PR body).

BUDGET: small — one document, no code changes, evidence gathering scoped to ~6 source files plus one TLA+ spec file already identified above.

OPEN: Whether "actor" should eventually gain a dedicated Rust type (e.g. a newtype wrapping the authenticated pubkey) is a real design question this node surfaces but does not answer — it is out of scope for a documentation task. Sibling identity nodes (#1103 agent-identity, #1106 human-identity, #1111 keypair, #1112/#1113 private/public-key) do not exist on `origin/launchpad` yet, so this node cannot link to them; the gap is named in Scope and omissions rather than worked around.

LEFT OUT: No new Rust type or refactor of any `actor`/`actor_pubkey` parameter naming — this is documentation of the existing term, not a proposal to formalize it in code. No relationships to the not-yet-merged sibling identity nodes. No attempt to reconcile every one of the ~15+ `actor`/`actor_pubkey` call sites found by the grep in STEP 1 — a representative, evidence-checked subset across spec, conformance, moderation, and archived-identity code is cited; the node's own scope section says so explicitly rather than implying exhaustive coverage.

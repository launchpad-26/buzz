# Issue #1033 — layers/authorization/channel-roles.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; `launchpad/docs/corpus/layers/authorization/channel-roles.md` does not exist yet (confirmed: `test -f` on the worktree checkout reports missing). No `layers/` directory exists in the corpus tree on `origin/launchpad` at all yet — this is the first node under that `type`. `launchpad/docs/corpus/templates/concept.md` is the closest matching template (defines a term, states boundaries, links related concepts, uses examples only to clarify — matching the issue's four extra DoD bullets verbatim); no `channel-roles`-specific template exists.

STEP 1  Gather evidence: read `crates/buzz-core/src/channel.rs` (`MemberRole` enum: Owner/Admin/Member/Guest/Bot, `permission_level`, `has_at_least`, `is_elevated`), `crates/buzz-relay/src/handlers/side_effects.rs::validate_admin_event` (role-gated NIP-29 admin kinds 9000 PUT_USER, 9001 REMOVE_USER, 9002 EDIT_METADATA, 9005 DELETE_EVENT), and `crates/buzz-core/src/git_perms.rs` (`channel role = repo role` — `default_min_role`, `push_role`, Bot/Guest excluded from `push:<role>`). Check `crates/buzz-db/src/channel.rs` for the stored `MemberRecord.role` string representation and `crates/buzz-core/src/kind.rs` for the NIP-29 kind constants. Record the commit SHA. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `layers-authorization-channel-roles`, type `layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, no `relationships` — the only corpus nodes with any topical adjacency, `architecture/principles/community-is-security-boundary.md` and `architecture/principles/fail-closed-boundaries.md`, document the *community*-level tenant boundary, a different layer, not channel-scoped role authorization; no other merged node's subject overlaps) and the body per `concept.md`'s required sections: one-sentence definition, the role hierarchy and its boundary (Bot excluded from the linear hierarchy), a worked example of a role-gated action drawn from `validate_admin_event`, and a scope-and-omissions section.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite (`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as the sole command in its own call to earn the verification stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must report `OK`. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review — not run here (self-review only).

BUDGET: small — one document, no code changes, evidence scoped to three source files (`channel.rs`, `side_effects.rs`, `git_perms.rs`) plus two supporting lookups (`buzz-db/src/channel.rs`, `kind.rs`).

OPEN: Two `buzz-core::channel::MemberRole` re-exports exist in the codebase (`buzz_db::channel::MemberRole` is a `pub use` of the same `buzz_core` type per `buzz-db/src/lib.rs`/`channel.rs`) — the issue names `buzz-core::channel` as the grounding source, which this plan follows; the document will note the re-export rather than treat it as a second, independent role type. No other corpus node currently merged on `origin/launchpad` is a legitimate `relationships` target for this subject, so `relationships` is omitted per the schema's own guidance.

LEFT OUT: No claim about workflow-engine or agent-specific authorization (`buzz-workflow`, `buzz-persona`) beyond where they consume `MemberRole` directly — out of scope for a channel-roles node. No attempt to document every role-gated relay handler exhaustively; `validate_admin_event`'s kind 9000/9001/9002/9005 cases are used as the representative worked example, not an exhaustive catalogue (a reference-type node would own that). No changes to runtime behavior or to `MemberRole` itself.

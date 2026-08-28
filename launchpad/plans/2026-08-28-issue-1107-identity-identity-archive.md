# Issue #1107 — layers/identity/identity-archive.md

ALREADY TRUE: `launchpad/docs/corpus/templates/concept.md` and `launchpad/docs/corpus/AGENTS.md`
are merged on `origin/launchpad`. `launchpad/docs/corpus/layers/identity/identity-archive.md`
does not exist yet (confirmed: `launchpad/docs/corpus/layers/` has no subdirectory at all on
this checkout of `origin/launchpad`). A real, implemented mechanism exists for this concept:
NIP-IA (`docs/nips/NIP-IA.md`), a relay-scoped identity archival protocol with its own event
kinds (`9035`/`9036` requests, `8002`/`8003` deltas, `13535` snapshot — all defined in
`crates/buzz-core/src/kind.rs`), a Postgres table (`archived_identities`, `migrations/0001_initial_schema.sql`),
a relay handler (`crates/buzz-relay/src/handlers/identity_archive.rs`) implementing three consent
paths (self/owner/admin), SDK builders (`crates/buzz-sdk/src/builders.rs`), and a desktop UI
surface (`desktop/src-tauri/src/commands/identity_archive.rs`, `desktop/src/features/identity-archive/`).
Sibling task #1102 (`layers/identity/actor.md`, PR #1803, open/unmerged) already cites
`crates/buzz-db/src/archived_identities.rs` in passing and confirms `layers/identity/` has no
subdirectory yet on `origin/launchpad` — no sibling identity node exists there to link to.

STEP 1 Gather evidence: read `docs/nips/NIP-IA.md` in full (abstract, motivation, non-goals,
kinds table, event formats, consent-path policy, relay processing algorithm, client behavior,
security/privacy considerations, examples). Cross-check against the implementation: read
`crates/buzz-db/src/archived_identities.rs` (table shape, `archive`/`unarchive`/`is_archived`/
`list_archived`), `migrations/0001_initial_schema.sql`'s `archived_identities` table (community-scoped
PK, `consent_path` CHECK constraint, comment "conformance: archive cannot hide a key in another
community"), `crates/buzz-relay/src/handlers/identity_archive.rs` (`determine_consent_path`,
`verify_owner_consent`, freshness window, `replaced-by` validation), `crates/buzz-core/src/kind.rs`
(kind constants), `crates/buzz-relay/src/handlers/ingest.rs` (scope = `UsersWrite` not `AdminUsers`,
and the "must not be channel-scoped" global-event handling), and `desktop/src-tauri/src/commands/identity_archive.rs`
(desktop's read/write surface). Confirm no dedicated e2e test file exists for NIP-IA under
`crates/buzz-test-client/tests/` (grep returned no hits) — record as a verification gap rather than
asserting untested coverage exists. ← RUNS HERE

STEP 2 [needs 1] Write front matter (schema-valid: `id: layers-identity-identity-archive`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`
— operator included because the admin consent path is an operator-facing action; no
`relationships`, since no other `layers/identity/*` node exists on `origin/launchpad` and the one
candidate architecture node inspected, `architecture-principles-humans-and-agents-are-peers`, is
about authorization parity rather than the archive mechanism itself — record that check explicitly
rather than asserting "nothing to link" by default) using the `concept.md` template's required
sections: Definition (one sentence first, what NIP-IA archival is and is not — not a ban, not a
deletion, not global reputation), Use cases (self key rotation, owner archiving a zombie agent,
admin archive + NIP-43 ban composition, self-unarchive anti-shadowban path), Comparison (against
NIP-09 deletion, NIP-51 mute lists, NIP-43 membership removal — the NIP's own Motivation section
already draws these distinctions), Scope and omissions. Classify every claim: NIP text and source
code citations are FACT; anything reasoned beyond what a source states outright (e.g. "no dedicated
e2e coverage" as a completeness inference) is INFERENCE with a stated confidence; issue #1107's own
DoD requirements are TEAM_KNOWLEDGE.

STEP 3 [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run
until exit 0.

STEP 4 [needs 3] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`) as
the sole command in its own call to earn the verification stamp, then commit the plan + document in
a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`review-adjudicate` and the cross-model final review pass are deferred to the batch owner's review —
not run here (self-review only, stated explicitly in the PR body).

BUDGET: small — one document, no code changes, evidence gathering scoped to the NIP spec plus
~6 already-identified source files.

OPEN: Whether `replaced-by` (the key-rotation hint tag) deserves its own corpus node distinct from
this one (`identity-recovery.md` is #1109, a filed sibling task, and may be the better home for
rotation semantics specifically) is a real boundary question; this node documents `replaced-by` as
part of the archive mechanism's own wire format and defers deeper rotation semantics to that sibling
rather than duplicating them. No sibling `layers/identity/*` node exists yet to link to or to check
that boundary against directly.

LEFT OUT: No changes to NIP-IA, the relay handler, or any other implementation code — this is
documentation of the existing mechanism, not a proposal to change it. No relationships to
not-yet-merged sibling identity nodes (#1102 actor, #1109 identity-recovery, #1111 keypair, etc.) —
none exist on `origin/launchpad` yet. No attempt to write a second node for `capabilities/archive/identity-archive.md`
(issue #718) — that is a distinct, capability-shaped task under a different parent PRD (#613) and is
explicitly out of scope for this layers-shaped concept task.

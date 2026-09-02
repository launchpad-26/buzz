# Issue #858 — development/event-kind-changes.md

ALREADY TRUE: `launchpad/docs/corpus/development/event-kind-changes.md` does not exist (`ls launchpad/docs/corpus/development/` returns exactly `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`). `crates/buzz-core/src/kind.rs`, `crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-relay/src/handlers/side_effects.rs`, `desktop/src/shared/constants/kinds.ts`, `mobile/lib/shared/relay/nostr_models.dart` and `CONTRIBUTING.md` § "How to Add a New Event Kind" all exist at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`. Three relationship targets resolve on `origin/launchpad`: `corpus-template-procedure`, `architecture-principles-event-driven-extension`, `architecture-flows-event-ingestion`.

STEP 1  Gather evidence: read `CONTRIBUTING.md` § "How to Add a New Event Kind" (lines 415–479) and verify each of its nine steps against the code it names — `kind.rs` (`ALL_KINDS`, `no_duplicate_kind_values`, the range predicates and their compile-time asserts), `ingest.rs` `required_scope_for_kind` including its default arm, `side_effects.rs` `handle_side_effects`, the `search_tsv` definition in `migrations/0008` and `schema/schema.sql`, and the `kind.rs` test module. Count the three client-side registries and search the tree for anything that enforces parity between them. ← RUNS HERE

STEP 2  [needs 1] Write the front matter — id `development-event-kind-changes`, type `development`, status `draft`, origin `launchpad`, audiences `[agent, developer]`, one evidence entry per substantive claim, first entry recording revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`, and three typed relationships (`implements` → `corpus-template-procedure`; `references` → `architecture-principles-event-driven-extension` and `architecture-flows-event-ingestion`), each confirmed with `git show origin/launchpad:<path>`.

STEP 3  [needs 2] Write the body in procedure shape per `launchpad/docs/corpus/templates/procedure.md`: goal, before-you-start prerequisites and allowed scope, one ordered executable sequence with a fork for the optional client-facing branch, success verification, rollback/cleanup, See also, Boundary, Relationships, Scope and omissions naming every gap found in STEP 1.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py` until it exits 0, then re-read the diff against the issue's DoD line by line and re-open every citation — before committing, because `git commit --amend` is blocked.

STEP 5  [needs 4] Run the corpus unittest suite bare and unpiped as the sole command in its own call to earn the stamp, then `git add` document + plan and `git commit -s` in a separate call. Stop at the commit.

PARALLEL: none — one document, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK, run bare. No push, no PR — review is the batch owner's.

BUDGET: small — one document, no code changes. Evidence scoped to one Rust registry file, two relay handler files, two client registries, two migrations, `schema/schema.sql`, and `CONTRIBUTING.md`.

OPEN: `standards/naming.md` MUST 3 prescribes a `corpus-` id prefix, but 157 of 160 merged content nodes use `<directory>-<stem>`, and the four merged `development/` nodes are themselves inconsistent (`corpus-development-build`, `debugging`, `development-hermit`, `development-prerequisites`). This node follows the measured majority as instructed; the standard's divergence is already tracked in #2029 and no new issue is filed here. Whether a fresh migration-bootstrapped database and a `pgschema`-bootstrapped one should agree about `search_tsv` is not this task's to settle — the divergence is reported as fact.

LEFT OUT: No change to `CONTRIBUTING.md`, even though its step 6 describes a search-exclusion list that migration 0008 inverted into an allowlist for fresh installs — documenting that drift is in scope, fixing it is not. No change to `kind.rs`, `push_lease.rs` or any code, including the duplicate `KIND_PUSH_LEASE` declaration found in STEP 1. No parity check built between the three kind registries. No reference node cataloguing individual kind integers — that is `corpus-template-event-kind`'s shape, not this procedure's.

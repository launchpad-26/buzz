---
id: development-event-kind-changes
type: development
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "CONTRIBUTING.md carries a section titled 'How to Add a New Event Kind' listing nine numbered steps -- define the kind constant in buzz-core/src/kind.rs, define the payload type, register the required scope in required_scope_for_kind, handle post-storage side effects in handle_side_effects, persist to the database, index for search, audit, write tests, document -- and it is linked from the file's own table of contents."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "CONTRIBUTING.md's architecture summary states 'Event kinds are the only switch. Every action in the system -- a message, a reaction, a workflow step, a canvas update -- is a Nostr event with a kind integer. Adding a new feature means defining a new kind.'"
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "crates/buzz-core/src/kind.rs declares every kind integer as a `pub const KIND_*: u32`, collects them into `pub const ALL_KINDS: &[u32]` documented as 'All registered kind constants -- used for duplicate detection and iteration', and its test module contains `no_duplicate_kind_values`, which inserts every ALL_KINDS entry into a HashSet and asserts each insert is new."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "kind.rs declares 129 `pub const KIND_*` constants but ALL_KINDS lists only 126 of them; the three absent are KIND_AUTH, KIND_NOSTR_IDENTITY_BINDING and KIND_PUSH_LEASE, so the no_duplicate_kind_values test cannot see a collision involving any of the three."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep_count(pattern='^pub const KIND_', path='crates/buzz-core/src/kind.rs') -> 129, against 126 entries in the ALL_KINDS body; the three names present only in the former are KIND_AUTH, KIND_NOSTR_IDENTITY_BINDING and KIND_PUSH_LEASE"
  - statement: "KIND_PUSH_LEASE = 30350 is declared twice in the workspace: once in crates/buzz-core/src/kind.rs and again as `pub const KIND_PUSH_LEASE: u32 = 30_350;` in crates/buzz-relay/src/handlers/push_lease.rs, and required_scope_for_kind imports the relay-local copy via the path `super::push_lease::KIND_PUSH_LEASE` rather than the buzz-core one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "crates/buzz-relay/src/handlers/push_lease.rs"
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "kind.rs carries twenty-eight compile-time assertions of the form `const _: () = assert!(...)` that pin range membership and the u16 ceiling for named kinds -- for example `assert!(is_parameterized_replaceable(KIND_PERSONA))` and `assert!(KIND_AUTH <= u16::MAX as u32)` -- so a kind number placed in the wrong NIP range for its declared behavior fails to compile rather than failing a test."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "grep_count(pattern='^const _: () = assert', path='crates/buzz-core/src/kind.rs') -> 28"
  - statement: "launchpad/docs/corpus/AGENTS.md instructs that when two sources of the same claim type conflict, the author records the conflict rather than averaging them, picking the newer one, or resolving it themselves, and names ADR-0029 as the full rule."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "kind.rs defines the range predicates is_ephemeral (20000-29999), is_replaceable (`matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA | 10000..=19999)`, where KIND_CHANNEL_METADATA is 41 and annotated 'Not used by Buzz today') and is_parameterized_replaceable (30000-39999, NIP-33, keyed by (pubkey, kind, d_tag)), and names the bounds as EPHEMERAL_KIND_MIN/MAX and the NIP-33 lower/upper bound constants; its test module asserts the parameterized-replaceable boundary at 29999/30000/39999/40000 and asserts across the whole 0..=65535 space that replaceable and parameterized-replaceable are disjoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "required_scope_for_kind in crates/buzz-relay/src/handlers/ingest.rs is a match over the kind integer mapping each registered kind to a Scope, and its final arm is `_ => Err(\"restricted: unknown event kind\")`, so a kind with no arm is rejected at ingest rather than admitted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
  - statement: "handle_side_effects in crates/buzz-relay/src/handlers/side_effects.rs is a match over the kind integer dispatching to per-kind handlers, and its final arm is `_ => Ok(())`, so a kind with no arm produces no side effect and no error."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/side_effects.rs"
  - statement: "A contributor who omits the required_scope_for_kind arm sees the event rejected on the first submission, while a contributor who omits the handle_side_effects arm sees the event stored and fanned out with the derived state silently absent."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs"
      - "crates/buzz-relay/src/handlers/side_effects.rs"
    confidence: 0.9
  - statement: "Buzz keeps three hand-maintained kind registries in three languages: crates/buzz-core/src/kind.rs (129 constants), desktop/src/shared/constants/kinds.ts (65 `export const KIND_*` bindings) and mobile/lib/shared/relay/nostr_models.dart (40 `static const` members of `abstract final class EventKind`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "desktop/src/shared/constants/kinds.ts"
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "grep_count(pattern='^export const KIND_', path='desktop/src/shared/constants/kinds.ts') -> 65, and grep_count(pattern='static const', path='mobile/lib/shared/relay/nostr_models.dart') -> 40"
  - statement: "The only stated sync obligation between the client registries is a doc comment on mobile/lib/shared/relay/nostr_models.dart reading 'Keep in sync with `desktop/src/shared/constants/kinds.ts`.'; the mobile file names the desktop file, and neither client file names crates/buzz-core/src/kind.rs."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "desktop/src/shared/constants/kinds.ts"
  - statement: "desktop/src/shared/constants/kinds.test.mjs contains eight tests, all of them exercising isConversationalUnreadKind's include/exclude behavior against named kind constants; none of them compares any kind value against the Rust or Dart registry."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.test.mjs"
  - statement: "No check in the repository compares the three kind registries against one another; a search across Rust, TypeScript, Dart, JavaScript, Python and workflow YAML for references to the client registry filenames and for sync-obligation phrasing returns only import statements, the one Dart doc comment, and unrelated 'stay in sync' comments about message ids, mention names and keyboard shortcuts."
    entry_class: INFERENCE
    evidence:
      - "grep_recursive(pattern='kinds.ts OR nostr_models OR stay in sync OR kept in sync OR must stay in sync', languages='rs,ts,dart,mjs,js,yml,py', exclude='node_modules') -> import statements only, plus the one Dart doc comment, plus unrelated sync comments about message ids, mention names and keyboard shortcuts; no citation compares two kind registries"
      - "desktop/src/shared/constants/kinds.test.mjs"
      - "mobile/lib/shared/relay/nostr_models.dart"
    confidence: 0.85
  - statement: "The desktop Tauri Rust side does not hold a fourth registry: it imports kind constants from buzz-core, for example `pub(crate) const KIND: u16 = buzz_core_pkg::kind::KIND_NOSTR_IDENTITY_BINDING as u16;` and `use buzz_core_pkg::kind::KIND_PERSONA;`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/nostr_bind.rs"
      - "desktop/src-tauri/src/event_sync.rs"
  - statement: "The web client holds no kind constants; the only occurrence of the word in web/src/shared is the optional `kinds?: number[]` field on the Nostr filter type in web/src/shared/lib/nostr-client.ts."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
  - statement: "CONTRIBUTING.md step 6 states that 'Postgres FTS indexes persisted events automatically via the events.search_tsv generated column' and that excluding a kind means adding it to the 'CASE WHEN kind IN (...) exclusion in the search_tsv definition (see the initial schema migration)'."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "migrations/0008_fresh_install_search_allowlist.sql replaces search_tsv on an empty events table with a positive allowlist -- `CASE WHEN kind IN (0, 9, 40002, 45001, 45003) THEN to_tsvector('simple', content) ELSE NULL::tsvector END` -- and its header states that existing installations keep their current expression until an operator runs scripts/maintenance/nip_rs_search_allowlist.sql out of band."
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
  - statement: "schema/schema.sql defines search_tsv with the opposite polarity -- a negative exclusion list, `CASE WHEN kind IN (1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200) THEN NULL::tsvector ELSE to_tsvector('simple', content) END` -- above a comment reading 'Keep in sync with migrations (final state: 0001 + 0005 + 0014 + 0033)', which does not list migration 0008."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
  - statement: "The divergence is a history artifact, not a stated design: commit 1b4703021dbfd37dc31845223dba9ba182e4647f ('Bound NIP-RS retention and search indexing (#1771)') introduced migration 0008 alongside migrations 0007 and 0009-0011 and changed nine files, none of which was schema/schema.sql, so the desired-state schema was never updated to match the allowlist that commit gave fresh installs."
    entry_class: FACT
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "schema/schema.sql"
      - "git_show_stat(commit='1b4703021dbfd37dc31845223dba9ba182e4647f') -> 9 files changed, including migrations/0007 through migrations/0011, and not schema/schema.sql"
  - statement: "A newly added kind is full-text searchable on a schema.sql-bootstrapped database, because that expression indexes everything not on its exclusion list, but is not searchable on a fresh migration-bootstrapped database, because migration 0008's allowlist admits only five kinds and migrations 0014 and 0033 wrap that expression with further exclusions rather than replacing it."
    entry_class: INFERENCE
    evidence:
      - "migrations/0008_fresh_install_search_allowlist.sql"
      - "migrations/0033_private_managed_agent_fts.sql"
      - "schema/schema.sql"
    confidence: 0.85
  - statement: "migrations/0033_private_managed_agent_fts.sql documents the cost of changing search_tsv: PostgreSQL cannot alter a generated expression in place, so the migration captures the current expression from pg_attrdef, drops the column and re-adds it wrapped, which 'rewrites the entire events heap and then rebuilds the GIN index, all under an ACCESS EXCLUSIVE lock inside the migration transaction (CREATE INDEX CONCURRENTLY is not possible here), with no lock_timeout'."
    entry_class: FACT
    evidence:
      - "migrations/0033_private_managed_agent_fts.sql"
  - statement: "The migrations directory contains only forward migrations -- forty numbered .sql files with no down, revert or rollback counterpart -- and crates/buzz-db/src/runtime/migration.rs runs them under a lock, describing migration 0007 as 'checksum-frozen'."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/runtime/migration.rs"
      - "ls_count(path='migrations', pattern='down OR revert', ignore_case=true) -> 0 matches among forty numbered forward .sql files"
  - statement: "kind.rs doc comments point Buzz-custom kinds at a specification file under docs/nips/ -- KIND_AGENT_ENGRAM cites 'docs/nips/NIP-AE.md' and KIND_PROJECT cites 'docs/nips/NIP-MP.md' -- and that directory holds the Buzz-custom NIP documents including NIP-AA.md, NIP-AE.md, NIP-AM.md, NIP-AO.md, NIP-AP.md, NIP-CW.md, NIP-DV.md and NIP-ER.md."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
      - "docs/nips/NIP-AE.md"
      - "docs/nips/NIP-MP.md"
  - statement: "crates/buzz-test-client/tests/ holds the integration suite CONTRIBUTING.md step 8 points at, with per-feature end-to-end files including e2e_relay.rs, e2e_nostr_interop.rs, e2e_event_reminder.rs, e2e_persona.rs, e2e_team.rs, e2e_project.rs and e2e_long_form.rs -- the pattern being one file per kind-backed feature."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
      - "crates/buzz-test-client/tests/e2e_event_reminder.rs"
      - "crates/buzz-test-client/tests/e2e_project.rs"
  - statement: "The Justfile defines `check` as fmt-check, clippy, desktop-check, desktop-tauri-fmt-check, desktop-tauri-clippy, web-check, mobile-check, security-review-check and file-size-check; `ci` as check plus test-unit, desktop-test, desktop-build, desktop-tauri-check, desktop-tauri-test, web-build and mobile-test; `test-unit` as a no-infrastructure run preferring cargo-nextest; and `test` as ./scripts/run-tests.sh all."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "AGENTS.md instructs that relay queries must specify kinds because omitting the kinds filter triggers the p-gate and returns 403, so a new kind is only reachable by a filter that names it explicitly."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "AGENTS.md states that new event kind integers are defined in buzz-core/src/kind.rs first and then handled in buzz-relay, that new features get new kind integers, and that a new operation should be modeled as a Nostr event rather than a new HTTP endpoint."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "kind.rs records superseded kind numbers in comments rather than reusing them -- for example 'V1 used kind:10001 (replaceable range -- wrong), then 40001', 'V1 used kind:10002 (replaceable range -- wrong)', 'V1 used kind:10004 (replaceable range + NIP-51 collision -- wrong)' and 'V1 used addressable range (30001-30003) -- wrong' -- and KIND_CHANNEL_METADATA = 41 is annotated 'Not used by Buzz today.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs"
  - statement: "launchpad/docs/corpus/development/ contains exactly four merged nodes at the recorded revision -- build.md, debugging.md, hermit.md and prerequisites.md -- carrying the ids corpus-development-build, debugging, development-hermit and development-prerequisites; none of them documents event kinds."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/debugging.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "launchpad/docs/corpus/development/prerequisites.md"
  - statement: "The three relationship targets declared by this node resolve on origin/launchpad at the recorded revision: launchpad/docs/corpus/templates/procedure.md carries id corpus-template-procedure, launchpad/docs/corpus/architecture/principles/event-driven-extension.md carries id architecture-principles-event-driven-extension, and launchpad/docs/corpus/architecture/flows/event-ingestion.md carries id architecture-flows-event-ingestion."
    entry_class: FACT
    evidence:
      - "git_show(ref='origin/launchpad', path='launchpad/docs/corpus/templates/procedure.md') -> front matter line 2 reads id: corpus-template-procedure"
      - "git_show(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/principles/event-driven-extension.md') -> front matter line 2 reads id: architecture-principles-event-driven-extension"
      - "git_show(ref='origin/launchpad', path='launchpad/docs/corpus/architecture/flows/event-ingestion.md') -> front matter line 2 reads id: architecture-flows-event-ingestion"
  - statement: "launchpad/docs/corpus/templates/procedure.md states that a node built from it 'should declare implements targeting corpus-template-procedure (this node's id) once this node is merged', citing relationships.schema.json's own worked example of 'a template instance of a standard'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
  - statement: "launchpad/docs/corpus/architecture/principles/event-driven-extension.md states as a MUST that a new client-facing capability in Buzz's relay surface be modeled as a new Nostr event kind registered in buzz-core/src/kind.rs and handled through the relay's generic event-storage path, rather than as a new endpoint-specific HTTP/JSON API."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/event-driven-extension.md"
  - statement: "launchpad/docs/corpus/templates/event-kind.md is the template for a node whose subject is one Nostr kind integer and its wire contract -- referenced NIP, tag shape, content-field semantics, access-control and storage model -- which is a reference form rather than a procedure form."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/event-kind.md"
  - statement: "No open or closed launchpad-26/buzz issue was found owning any of the three gaps this node names: the search_tsv polarity divergence, the duplicate KIND_PUSH_LEASE declaration, or a parity check across the three kind registries."
    entry_class: FACT
    evidence:
      - "gh_issue_list(repo='launchpad-26/buzz', search='search_tsv allowlist schema.sql', state='all') -> []"
      - "gh_issue_list(repo='launchpad-26/buzz', search='KIND_PUSH_LEASE duplicate', state='all') -> []"
      - "gh_issue_list(repo='launchpad-26/buzz', search='event kind registry parity sync', state='all') -> []"
  - statement: "Issue #858 requires that this node state goal, prerequisites and allowed environment/scope; provide ordered executable project-specific steps; define success verification and rollback/cleanup where relevant; and link authoritative commands and configuration rather than giving generic advice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#858 definition of done"
  - statement: "Issue #858 requires that a newly discovered second concept, contract or procedure be filed as a separate task rather than folded into this document, and names its parent PRD as #619."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#858 definition of done"
relationships:
  - type: implements
    target: corpus-template-procedure
  - type: references
    target: architecture-principles-event-driven-extension
  - type: references
    target: architecture-flows-event-ingestion
---

# Adding or changing a Nostr event kind

How to introduce a new Nostr event kind into Buzz, or change an existing one,
across the Rust registry that defines it, the relay handlers that admit and act on
it, the storage and search paths that keep it, and the two client registries that
must learn about it by hand. Perform this whenever a feature needs a new action on
the wire — which, per `architecture-principles-event-driven-extension`, is every
new client-facing relay capability, since adding an HTTP endpoint instead is
excluded by a MUST.

## Before you start

**Prerequisites.**

- A working Buzz development environment. Activate the pinned toolchain first:
  `. ./bin/activate-hermit`, then `just setup`. Toolchain and dependency detail is
  owned by `development-prerequisites` and `corpus-development-build`, not
  restated here.
- Postgres and Redis running, if you intend to run the integration suite. `just
  test-unit` needs neither; `just test` needs both.
- Write access to `crates/buzz-core`, `crates/buzz-relay`, `desktop/` and
  `mobile/`. A kind always touches the first two; whether it touches the client
  trees depends on whether a client must recognise it.

**Allowed environment and scope.**

- **This is a source change in `block/buzz`'s application code**, made on a branch
  and merged by pull request. It is not an operational change: nothing here is
  applied to a running relay by hand.
- **Kind integers are permanent.** `kind.rs` records superseded numbers in
  comments — `V1 used kind:10001 (replaceable range — wrong), then 40001`,
  `V1 used addressable range (30001–30003) — wrong` — rather than reusing them.
  Treat a spent number as spent.
- **Adding a kind is additive by design.** `CONTRIBUTING.md` frames event kinds as
  "the only switch" precisely so that a new feature means a new kind and there are
  "no breaking changes to existing clients." Changing the meaning of a kind that
  clients already send is the case this procedure does *not* make safe; see
  *Boundary* below.
- **The relay applies migrations on startup and there is no down migration.** The
  `migrations/` directory holds forty forward-only files with no revert
  counterpart, and `crates/buzz-db/src/runtime/migration.rs` describes at least
  one as checksum-frozen. Plan the schema half of the change accordingly, and see
  *Rollback and cleanup*.

## Adding a new event kind

The ten steps below expand `CONTRIBUTING.md`'s nine-step list, each verified
against the code it names at the recorded revision, and add the two failure modes,
the compile-time guard and the three-registry obligation that list does not
surface. `CONTRIBUTING.md` § "How to Add a New Event Kind" remains the
authoritative source; where this node departs from or adds to it, it says so.

1. **Choose the number, then let the compiler check it.** Pick from the sub-range
   whose semantics you want: 20000–29999 is ephemeral (never stored), 10000–19999
   is replaceable (`is_replaceable` also matches the legacy singletons 0, 3 and
   41 — those are not available to you), 30000–39999 is NIP-33 parameterized
   replaceable keyed by `(pubkey, kind, d_tag)`, and Buzz's own
   command and system ranges are commented inline in `crates/buzz-core/src/kind.rs`.
   The range is not decoration — `is_ephemeral`, `is_replaceable` and
   `is_parameterized_replaceable` in that file are pure functions of the integer,
   so the number you choose *is* the storage behavior you get. Kinds must fit
   `u16`; `kind.rs` asserts that ceiling at compile time.

2. **Declare the constant** in `crates/buzz-core/src/kind.rs`, with a doc comment
   naming its NIP (standard or Buzz-custom) and its ownership/scoping shape, then
   **add it to `ALL_KINDS`**. The array is documented as "All registered kind
   constants — used for duplicate detection and iteration", and the
   `no_duplicate_kind_values` test in the same file is the only collision check
   there is. **A constant declared but omitted from `ALL_KINDS` is invisible to
   that test** — three already are (`KIND_AUTH`,
   `KIND_NOSTR_IDENTITY_BINDING`, `KIND_PUSH_LEASE`), so do not treat the omission
   as an established convention for never-stored kinds.

3. **Pin the range membership with a compile-time assertion**, alongside the
   existing block in `kind.rs`:

   ```rust
   const _: () = assert!(is_parameterized_replaceable(KIND_MY_FEATURE));
   ```

   This is the cheapest guard in the file — it turns a wrong-range number into a
   build failure rather than a runtime surprise, and `kind.rs` already carries
   twenty-eight of them.

4. **Define the payload type** in the appropriate `crates/buzz-core/src/` module
   if the `content` field is structured JSON, per `CONTRIBUTING.md` step 2.

5. **Register the required scope** in `required_scope_for_kind` in
   `crates/buzz-relay/src/handlers/ingest.rs`. **Do not skip this and expect a
   default**: the match's final arm is `_ => Err("restricted: unknown event
   kind")`, so an unregistered kind is refused at ingest. This is the fail-loud
   half of the change — you will find out immediately.

6. **Add the side-effect arm**, if the kind has post-storage consequences, in
   `handle_side_effects` in `crates/buzz-relay/src/handlers/side_effects.rs`.
   **This is the fail-silent half.** That match's final arm is `_ => Ok(())`, so a
   kind with no arm stores and fans out cleanly while every derived effect —
   notification, cache invalidation, counter update — simply never happens. There
   is no error to notice. If your kind has side effects, this step is the one to
   verify by observation, not by absence of failure.

7. **Persist and query.** Add the handler in `crates/buzz-db/src/` if the event
   must be queryable beyond the generic event store, per `CONTRIBUTING.md` step 5.
   Remember that a client can only reach the new kind through a filter that names
   it: `AGENTS.md` records that omitting `kinds` from a relay query trips the
   p-gate and returns 403.

8. **Decide the search policy explicitly — do not assume the default.**
   `CONTRIBUTING.md` step 6 says FTS indexing is automatic and describes excluding
   a kind from a `CASE WHEN kind IN (...)` list. That describes only one of the two
   bootstrap paths:

   - `schema/schema.sql` uses a **negative exclusion list** — everything not named
     is indexed. A new kind is searchable here by default.
   - `migrations/0008_fresh_install_search_allowlist.sql` replaces `search_tsv` on
     an empty `events` table with a **positive allowlist** of five kinds
     (`0, 9, 40002, 45001, 45003`). Later FTS migrations (`0014`, `0033`) wrap that
     expression with further exclusions rather than replacing it, so a new kind is
     **not** searchable on a freshly migrated database.

   The two disagree because of how they were written, not by design: the commit
   that added migration 0008 (`1b4703021`, "Bound NIP-RS retention and search
   indexing (#1771)") changed nine files and `schema/schema.sql` was not among
   them, so the desired-state schema still carries the pre-0008 polarity. Its own
   comment says "Keep in sync with migrations (final state: 0001 + 0005 + 0014 +
   0033)" and does not list 0008.

   If your kind must be searchable, add it deliberately and say which path you
   changed. If it carries ciphertext or private routing data, exclude it —
   `migrations/0033` is the worked example for a brownfield exclusion, and it
   documents the price: dropping and re-adding a generated column "rewrites the
   entire events heap and then rebuilds the GIN index, all under an ACCESS
   EXCLUSIVE lock inside the migration transaction ... with no `lock_timeout`."

9. **Update the client registries by hand — all of them.** Buzz keeps three kind
   registries in three languages and **nothing in the repository checks them
   against each other**:

   | Registry | Shape | Constants at the recorded revision |
   |---|---|---|
   | `crates/buzz-core/src/kind.rs` | `pub const KIND_*: u32` + `ALL_KINDS` | 129 declared, 126 registered |
   | `desktop/src/shared/constants/kinds.ts` | `export const KIND_*` | 65 |
   | `mobile/lib/shared/relay/nostr_models.dart` | `static const` on `abstract final class EventKind` | 40 |

   The only stated obligation is one doc comment in the Dart file — "Keep in sync
   with `desktop/src/shared/constants/kinds.ts`" — which names the desktop file
   and not the Rust one. `desktop/src/shared/constants/kinds.test.mjs` tests
   `isConversationalUnreadKind`'s include/exclude behavior and compares nothing
   across languages. Two trees need no edit: `desktop/src-tauri/` imports from
   `buzz_core_pkg::kind` rather than redeclaring, and the web client holds no kind
   constants at all. Add the constant to whichever clients must recognise the
   kind, and expect no check to catch you if you forget.

10. **Write the tests and the specification.** A unit test for payload
    serialization in `buzz-core`, and an integration test in
    `crates/buzz-test-client/tests/` — the existing pattern is one `e2e_*.rs` per
    kind-backed feature (`e2e_event_reminder.rs`, `e2e_persona.rs`,
    `e2e_project.rs`, `e2e_long_form.rs`). For a Buzz-custom kind, write the wire
    contract as a `docs/nips/NIP-XX.md` document and cite it from the constant's
    doc comment, the way `KIND_AGENT_ENGRAM` cites `docs/nips/NIP-AE.md` and
    `KIND_PROJECT` cites `docs/nips/NIP-MP.md`.

## Changing an existing event kind

Take this branch when the kind integer already exists and clients already send it.
The steps above still apply to whatever you touch; these three constraints
additionally bind.

1. **Do not repurpose the number.** Adding a field to a payload is a change;
   changing what the kind means is a new kind. `kind.rs`'s own history shows the
   pattern — superseded numbers are annotated and abandoned, not reused.
2. **Re-check the range predicates.** If the change alters storage semantics
   (ephemeral, replaceable, addressable), the number itself may now be in the
   wrong range, and the range is not a label — it is what `is_ephemeral` and its
   siblings compute from the integer. A new number in the correct range is the
   fix; a compile-time assertion is how you prove it.
3. **Fan the change out to every registry that names the kind.** Grep all three
   registries for the constant before assuming the Rust change was the whole
   change.

## Success verification

Run these from the repository root, in this order — the earlier ones fail fastest.

1. `just check` — formatting, clippy across the workspace and Tauri, desktop and
   web checks, `mobile-check`, `security-review-check` and `file-size-check`. A
   wrong-range kind number fails here, at compile time, via the `const _: ()`
   assertions.
2. `just test-unit` — no infrastructure required. This is where
   `no_duplicate_kind_values`, the range-boundary tests and the
   replaceable/parameterized disjointness test in `kind.rs` run, along with the
   `buzz-core` payload serialization test you added.
3. `just test` — the full suite via `./scripts/run-tests.sh all`, requiring
   Postgres and Redis. This is where your `crates/buzz-test-client/tests/e2e_*.rs`
   integration test actually submits an event of the new kind and asserts the
   relay's behavior. **Run this one.** It is the only step that distinguishes "the
   side-effect arm works" from "the side-effect arm is missing and
   `_ => Ok(())` swallowed it."
4. `just ci` — the full local gate (`check` plus `test-unit`, desktop tests and
   build, Tauri check and test, web build, mobile test). `AGENTS.md` requires this
   before every pull request.

**Verify by observation, not by silence.** Because `handle_side_effects` returns
`Ok(())` for an unmatched kind, a green suite proves nothing about a side effect
you never asserted on. The integration test must assert the *derived* state — the
row written, the notification emitted, the counter incremented — not merely that
the event was accepted.

## Rollback and cleanup

- **Before merge**, rollback is ordinary: drop the branch. No kind number has been
  spent, because nothing has shipped that references it.
- **After merge, the code half reverts and the number does not.** Revert the
  commit to remove the constant, the handler arms and the client entries. Do not
  re-issue the number to a different feature afterwards — treat it as spent, per
  the annotated-and-abandoned pattern in `kind.rs`.
- **The migration half does not revert.** `migrations/` is forward-only — forty
  numbered files, no down counterpart — and the relay applies migrations on
  startup. Undoing a `search_tsv` change means writing a *new* forward migration
  that restores the previous expression, using `migrations/0033`'s
  capture-drop-re-add shape. On a populated database that is a full heap rewrite
  and GIN index rebuild under an `ACCESS EXCLUSIVE` lock; schedule a window rather
  than reverting casually.
- **Clean up the client registries.** A reverted Rust constant leaves orphaned
  entries in `kinds.ts` and `nostr_models.dart` that no check will report. Remove
  them in the same revert.

## See also

- `architecture-principles-event-driven-extension` — the MUST that makes a new
  kind, rather than a new HTTP endpoint, the required shape for a new capability.
- `architecture-flows-event-ingestion` — what the relay does with an event once
  this procedure has registered its kind.
- `corpus-development-build` and `development-prerequisites` — the toolchain and
  build environment this procedure assumes.
- `CONTRIBUTING.md` § "How to Add a New Event Kind" — the authoritative nine-step
  list this procedure verifies and extends.
- `crates/buzz-core/src/kind.rs` — the authoritative registry of every kind
  integer, its sub-ranges, and its predicates.
- `docs/nips/` — the Buzz-custom NIP specifications a new custom kind needs.

## Boundary

This node does not describe:

- **What any particular kind means on the wire** — its tag shape, content
  semantics, NIP reference, or access-control model. That is reference content
  per node, and `corpus-template-event-kind` is its template. This procedure
  tells you how to add a kind, not what any existing kind is.
- **How to acquire the underlying skills from scratch** — Rust, Nostr, NIP-29
  group semantics, or Buzz's crate layout. This is written for a contributor who
  can already build and test the workspace.
- **Why Buzz is event-driven at all**, or why an event beats an endpoint. That
  rationale is `architecture-principles-event-driven-extension`'s, stated there as
  a MUST with its own evidence.
- **Migrating clients already in the field across a semantic change to a live
  kind.** The additive path is safe by construction; the breaking path is not made
  safe by this procedure and has no owner named here.

## Relationships

- `implements` → `corpus-template-procedure`. The procedure template names an
  instance node's `implements` edge back to itself as the intended relationship,
  citing `relationships.schema.json`'s own worked example of "a template instance
  of a standard". This node is that first instance for the `development` surface.
- `references` → `architecture-principles-event-driven-extension`. The principle
  supplies the MUST that makes this procedure the required path; this node does
  not restate the rationale.
- `references` → `architecture-flows-event-ingestion`. The ingestion flow owns
  what happens to the event after registration; this node cites it rather than
  duplicating it.

All three targets were resolved against `origin/launchpad` with
`git show origin/launchpad:<path>` at the recorded revision, not against the
authoring worktree.

## Scope and omissions

**This node covers** the ordered, executable sequence for adding a new Nostr event
kind to Buzz and the additional constraints for changing an existing one: range
selection and its compile-time guards, registration in `ALL_KINDS`, the two relay
match arms and their opposite failure modes, the storage and search decision
including the two disagreeing bootstrap paths, the three hand-maintained client
registries and the absence of any parity check, the test and specification
obligations, the commands that verify the change, and what can and cannot be rolled
back.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The wire contract of any individual kind | a per-kind reference node built from `corpus-template-event-kind`; none exists at the recorded revision |
| Why a capability must be an event rather than an endpoint | `architecture-principles-event-driven-extension` |
| What the relay does with an event after ingest | `architecture-flows-event-ingestion` |
| Toolchain, Hermit activation and build setup | `development-hermit`, `corpus-development-build`, `development-prerequisites` |
| Diagnosing a kind that misbehaves at runtime | `debugging` |
| Reconciling `schema/schema.sql`'s exclusion list with migration 0008's allowlist | unowned at the recorded revision — no issue found and none filed by this task |
| The duplicate `KIND_PUSH_LEASE` declaration in `buzz-core` and `buzz-relay` | unowned at the recorded revision |
| Building any automated parity check across the three kind registries | unowned at the recorded revision |

**Expected but not verified when this node was written:**

- **No step in this procedure was executed.** The sequence is reconstructed from
  reading `CONTRIBUTING.md` against the code it names, not from adding a kind and
  watching it work. The procedure template's own evidence expectations call for
  citing an executed workflow where practical; that was not practical here, and the
  claims about the two default arms' *consequences* are marked `INFERENCE` in this
  node's provenance ledger accordingly. The first contributor to follow this
  procedure end to end should correct it.
- **The claim that nothing enforces registry parity is a negative from search.** It
  rests on a cross-language grep for the registry filenames and for sync-obligation
  phrasing, plus reading `kinds.test.mjs` in full. A check that never names the
  files it compares would not have been found.
- **The search-indexing consequence was not observed against a live database.**
  Migration 0008's allowlist and `schema.sql`'s exclusion list were read; neither
  bootstrap path was executed, and no NIP-50 query was run to confirm that a
  newly added kind is unsearchable on a freshly migrated database.
- **`scripts/maintenance/nip_rs_search_allowlist.sql`, the out-of-band script
  migration 0008's header names for populated installations, was not opened.** Its
  effect on an existing database's search policy is cited here only as migration
  0008 describes it.
- **No claim is made about which of the two `search_tsv` polarities is intended.**
  Two executable sources of the same class — a migration and the desired-state
  schema — disagree about a system behavior. This node reports both faithfully
  and takes no position, which is what `launchpad/docs/corpus/AGENTS.md` requires
  of an author who finds a same-class conflict. The node's `status` stays `draft`
  rather than `flagged` because the conflict is in the repository being described,
  not between two sources for a claim this node asserts.

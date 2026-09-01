---
id: implementation-crates-buzz-audit
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 1ed55e980b0043f92d9c652e6a39a8e49345389c."
    entry_class: FACT
    evidence:
      - "commit 1ed55e980b0043f92d9c652e6a39a8e49345389c"
  - statement: "buzz-audit's Cargo.toml describes it as \"Hash-chain audit log for Buzz\" and its lib.rs crate doc states it is a tamper-evident, per-community hash-chain audit log where each community owns an independent chain keyed (community_id, seq), seq is monotonic within a community, and each entry chains to the previous entry of the same community via SHA-256."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-audit/src/lib.rs"
  - statement: "buzz-audit's lib.rs crate doc states community_id is folded into the hash so a row lifted out of one community's chain can never verify inside another's, and explicitly ties this to \"the audit half of the non-interference floor (auditHeads[c] in MultiTenantRelay.tla)\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/lib.rs"
  - statement: "docs/spec/MultiTenantRelay.tla declares auditHeads as \"function: community -> current audit head\", threads it through the model's state variables, and updates it only via a step that requires newHead # auditHeads[c] before setting auditHeads' = [auditHeads EXCEPT ![c] = newHead], with a comment naming the file's own goal as a \"two-execution non-interference theorem\" -- confirming auditHeads is a real, present component of this specification, not an invented citation."
    entry_class: FACT
    evidence:
      - "docs/spec/MultiTenantRelay.tla"
  - statement: "docs/multi-tenant-conformance.md's \"Audit log and observability\" conformance-matrix row states the model as \"One hash-chain audit log records event/channel/auth/media actions; errors are sanitized before reaching clients\", requires the audit_log key/sequence/head to include community_id with uniqueness (community_id, seq) and (community_id, hash), and requires that audit reads verify only one community chain and that error strings not include cross-community IDs, constraint names, or existence facts -- this is the conformance target buzz-audit's schema and error type are checked against below."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "migrations/0001_initial_schema.sql creates audit_log with columns community_id UUID NOT NULL REFERENCES communities(id), seq BIGINT NOT NULL, hash BYTEA NOT NULL, prev_hash BYTEA, action VARCHAR(64) NOT NULL, actor_pubkey BYTEA, object_id TEXT, detail JSONB, created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(), PRIMARY KEY (community_id, seq), plus a unique index idx_audit_log_hash on (community_id, hash) -- matching the conformance row's required key/uniqueness shape exactly, and owned by the migration, not by the buzz-audit crate, which ships no DDL of its own (stated directly in lib.rs's crate doc)."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql"
      - "crates/buzz-audit/src/lib.rs"
  - statement: "migrations/0029_community_deletion.sql calls SELECT attach_community_write_fence('audit_log') alongside every other tenant-scoped table (events, channels, moderation_actions, moderation_reports, and more), so audit_log is also enforced at the database level as a community-fenced table, independent of the application-level community_id hashing buzz-audit performs."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql"
  - statement: "AuditService::log (crates/buzz-audit/src/service.rs) acquires a per-community Postgres advisory lock (pg_advisory_lock(hashtextextended(lock_key, 0)) where lock_key is \"buzz_audit:\" plus the community id), reads the community's current chain head (seq, hash) ordered by seq DESC LIMIT 1 scoped to community_id, computes the next entry with seq = prev_seq + 1 and prev_hash set from the head (or None for a community's first entry), calls compute_hash, inserts the row inside a transaction, commits, and releases the advisory lock in every outcome (including a caught panic, via std::panic::AssertUnwindSafe(...).catch_unwind())."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "AuditService::verify_chain(community, from_seq, to_seq) reads exactly one community's rows ordered by seq ascending, returns Ok(false) for an empty range, and otherwise recomputes each row's hash and checks it against the stored hash (AuditError::HashMismatch on failure) and checks each row's prev_hash against the previous row's recomputed hash (AuditError::ChainViolation on failure); AuditService::get_entries(community, from_seq, limit) similarly scopes its WHERE clause to community_id and never returns another community's rows."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/service.rs"
  - statement: "compute_hash (crates/buzz-audit/src/hash.rs) is SHA-256 over a fixed field order -- community_id first (\"tenant binding\"), then seq (big-endian bytes), then created_at normalized through to_storage_precision and rendered as RFC 3339, then action, then actor_pubkey (with an explicit presence tag byte distinguishing Some(empty) from None), then object_id (same presence-tag pattern), then detail serialized via a hand-written canonical_json helper that sorts object keys via a BTreeMap for deterministic output, then prev_hash (or the all-zero GENESIS_HASH sentinel for a community's first entry)."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs"
  - statement: "to_storage_precision truncates a DateTime<Utc> to 6 fractional digits (chrono's trunc_subsecs(6)) because Postgres TIMESTAMPTZ round-trips at microsecond resolution while Utc::now() on Linux returns nanosecond resolution, and chrono's to_rfc3339() emits a variable digit count (0/3/6/9) that follows the value -- hashing an untruncated timestamp therefore produces a digest that can never be recomputed from the stored row; compute_hash calls to_storage_precision internally so every caller gets this normalization even if a write path forgot to truncate before storing, and hash.rs's own test suite pins this exact failure mode (rfc3339_sub_second_width_follows_the_value, compute_hash_normalizes_sub_microsecond_timestamps)."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs"
  - statement: "AuditError (crates/buzz-audit/src/error.rs) has five variants -- Database, ChainViolation{seq}, HashMismatch{seq}, UnknownAction, Serialization -- and its own doc comment states these are \"operator-internal\" diagnostics \"never relayed to a client on the wire\" and that \"no variant embeds a community_id or any cross-community object identifier\"; a same-file unit test (audit_error_text_carries_no_community_id_or_constraint) asserts the rendered Display text of every chain-derived variant contains neither a concrete community UUID (standard or simple form) nor any of the substrings community_id, audit_log_pkey, constraint, communities, and separately asserts the seq field IS present in ChainViolation/HashMismatch text so the assertion is not vacuous."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/error.rs"
  - statement: "NewAuditEntry (crates/buzz-audit/src/entry.rs) types its community_id field as buzz_core::CommunityId rather than a raw Uuid, and its doc comment states this is deliberate: the only ways to obtain a CommunityId are host resolution or a server-scoped DB row, never a value parsed from client input, and the type is not Serialize/Deserialize so no client-supplied blob can become a NewAuditEntry; its detail field's doc comment states detail must never carry bearer-token material and that AuthSuccess/AuthFailure entries carry only outcome metadata, never the token itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/entry.rs"
  - statement: "AuditAction (crates/buzz-audit/src/action.rs) is an 11-variant enum (EventCreated, EventDeleted, ChannelCreated, ChannelUpdated, ChannelDeleted, MemberAdded, MemberRemoved, AuthSuccess, AuthFailure, RateLimitExceeded, MediaUploaded) with a hand-written as_str/FromStr pair (not derived, e.g. via strum) whose stable snake_case strings are both the hash input and the stored action column value; a round-trip test (roundtrip_all_variants) parses every variant's own as_str() output back through FromStr and asserts equality."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/action.rs"
  - statement: "crates/buzz-relay/src/main.rs constructs the audit pool only when config.audit_enabled is true, as a direct sqlx::postgres::PgPoolOptions pool (max 5, min 1 connections) on config.database_url, wrapped in AuditService::new; when disabled it logs \"Audit logging disabled by BUZZ_AUDIT_ENABLED\" and leaves the Option<AuditService> as None -- confirming this is one of the two additional independent Postgres pools buzz-relay opens beside buzz-db's, as also recorded in the architecture-containers-postgres corpus node."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "launchpad/docs/corpus/architecture/containers/postgres.md"
  - statement: "crates/buzz-relay/src/config.rs's audit_enabled field doc comment states \"Whether tamper-evident event/media audit logging is enabled. Defaults to true. This does not control the separate moderation_actions audit trail\", and parses BUZZ_AUDIT_ENABLED via parse_bool(\"BUZZ_AUDIT_ENABLED\", true); TESTING.md's environment-variable reference table gives the same default (true) and the same distinction (\"Does not disable the separate moderation audit trail\")."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "TESTING.md"
  - statement: "crates/buzz-relay/src/state.rs's AppState does not call AuditService::log synchronously from request handlers. AppState::new spawns a background audit worker task reading from a bounded mpsc::channel(1000) of buzz_audit::NewAuditEntry (audit_tx on AppState, held alongside audit: Option<Arc<AuditService>>); the worker drains entries with log_audit_entry, and on a cancellation signal calls audit_rx.close() then drains whatever was already buffered before exiting, logging drained on completion; AppState::new returns an AuditShutdownHandle the caller must drain during graceful shutdown so buffered entries are flushed before process exit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs"
  - statement: "crates/buzz-relay/src/handlers/event.rs's enqueue_event_created_audit sends onto audit_tx with try_send-style backpressure handling: a comment states \"if the queue is full ... this is intentional: the audit advisory lock already serializes writes (at most 1 in-flight), so a full queue means the audit [db is overloaded]\", and a failed send increments the buzz_audit_send_errors_total metrics counter rather than failing the request; the same file's dispatch_persistent_event path returns to its caller after only the bounded audit enqueue has completed, not after the audit DB write itself, so audit persistence is decoupled from request latency."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-relay/src/handlers/event.rs contains two audit-specific tests requiring Postgres/Redis: audit_records_caller_actor_not_relay_signer_for_relay_signed_event (asserts the audit_log.actor_pubkey column records the caller-supplied actor, not the relay's own signing key, for a relay-signed event) and audit_chain_is_isolated_per_tenant_through_relay_ingest (drives dispatch_persistent_event under two tenants against a shared Postgres pool and asserts chain isolation at the integrated ingest path, not just at AuditService::log in isolation)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs's mod audit_log is a doc-only module (no runnable assertions in this file) whose own doc comment states buzz-audit has \"no client-reachable wire surface at all\" -- there is no /audit route in crates/buzz-relay/src/router.rs -- so unlike every other row in that conformance suite (which asserts a wire-level response denies a cross-community oracle), this row instead cites where the two halves of the isolation obligation are proven: (1) chain isolation, via buzz_audit::service::tests::chains_are_independent_per_community plus the integrated buzz_relay::handlers::event::tests::audit_chain_is_isolated_per_tenant_through_relay_ingest; (2) error non-leakage, via buzz_audit::error::tests::audit_error_text_carries_no_community_id_or_constraint. Both cited test function names were confirmed present at their stated paths."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-audit/src/error.rs"
      - "crates/buzz-relay/src/handlers/event.rs"
  - statement: "buzz-admin/Cargo.toml declares buzz-audit as a workspace dependency, but crates/buzz-admin/src/main.rs and crates/buzz-admin/src/deletions.rs (the crate's only two source files) contain zero references to buzz_audit, AuditService, or any audit-related identifier -- a real divergence between conformance_multitenant.rs's own prose, which describes AuditService::{verify_chain, get_entries} as \"operator-internal (consumed by buzz-admin)\", and the crate's actual current code, which does not consume it."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/Cargo.toml"
      - "crates/buzz-admin/src/main.rs"
      - "crates/buzz-admin/src/deletions.rs"
  - statement: "buzz-audit's Cargo.toml declares dependencies on buzz-core, buzz-datastore-tracing, sqlx, tokio, serde, serde_json, uuid, chrono, tracing, metrics, thiserror, sha2, hex and futures-util; a search of the crate's own five src/*.rs files for hex:: found no call sites, so the hex dependency's use in this crate could not be located from source read for this node -- hashes are stored and compared as raw BYTEA/Vec<u8>, not as hex strings, in the code this node inspected."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/Cargo.toml"
      - "crates/buzz-audit/src/lib.rs"
      - "crates/buzz-audit/src/service.rs"
      - "crates/buzz-audit/src/hash.rs"
      - "crates/buzz-audit/src/entry.rs"
      - "crates/buzz-audit/src/error.rs"
      - "crates/buzz-audit/src/action.rs"
  - statement: "architecture-containers-relay (launchpad/docs/corpus/architecture/containers/relay.md, merged on origin/launchpad) states buzz-relay \"is the only crate in the workspace that imports and orchestrates buzz-db, buzz-auth, buzz-pubsub, buzz-search, buzz-audit and buzz-workflow directly; those crates never call each other, so every cross-subsystem coordination path runs through the relay,\" and separately lists buzz-audit's hash-chain log among AppState's directly-held connections and among the crates \"each is its own container/node once authored; this node names them only as directly connected systems\" -- the basis for this node's part-of edge back to it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/relay.md"
  - statement: "No corpus node currently merged on origin/launchpad documents docs/multi-tenant-conformance.md or docs/spec/MultiTenantRelay.tla as their own node with a stable id, so no implements edge toward either can be declared without inventing a target id that resolves to nothing -- checked directly against `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists no other implementation/crates/* sibling and no verification-type node either."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**; no implementation/ subtree and no node documenting docs/multi-tenant-conformance.md or docs/spec/MultiTenantRelay.tla"
---

# `buzz-audit`: implementation reference

`crates/buzz-audit` is the Rust crate implementing Buzz's tamper-evident,
per-community hash-chain audit log. It claims to realize two targets: the
"Audit log and observability" row of this repository's own
`docs/multi-tenant-conformance.md` conformance matrix (the human-readable
per-tenant-isolation contract every subsystem in the multi-tenant migration is
checked against), and, per the crate's own doc comment, "the audit half of the
non-interference floor" modeled as `auditHeads[c]` in the formal TLA+
specification `docs/spec/MultiTenantRelay.tla`. Neither target currently has
its own corpus node id, so this node names them by path rather than declaring
an `implements` edge to an id that would resolve to nothing.

## Target

- **`docs/multi-tenant-conformance.md`**, "Audit log and observability" row.
  States the model as: one hash-chain audit log records event/channel/auth/
  media actions; errors are sanitized before reaching clients; every
  tenant-observable audit entry is labeled with the resolved community; the
  `audit_log` key/sequence/head includes `community_id` with uniqueness
  `(community_id, seq)` and `(community_id, hash)`; audit reads verify only
  one community's chain; error strings must not leak cross-community IDs,
  constraint names, or existence facts. No corpus node id exists for this
  document yet — open it directly at the path above.
- **`docs/spec/MultiTenantRelay.tla`**, the `auditHeads` state variable.
  Modeled as a function from community to current audit head, updated only
  when the new head differs from the current one, threaded through the
  file's stated "two-execution non-interference theorem." No corpus node id
  exists for this specification yet — open it directly at the path above.

## Public interfaces and dependencies

**Public entry points** (`crate::` re-exports from `lib.rs`): `AuditService::
{new, log, verify_chain, get_entries}` (construction and the three
operations described in *Implementation surface* below), `AuditAction` (the
11-variant action enum), `AuditEntry`/`NewAuditEntry` (stored-row and
write-input types), `AuditError` (the five-variant error type), and
`compute_hash`/`GENESIS_HASH` (the hashing primitives, exposed so a caller —
today, only this crate's own tests — can recompute a digest without going
through `AuditService`).

**Important dependencies**, per `Cargo.toml`, and why each is load-bearing
rather than incidental: `buzz-core` (for `CommunityId`, the typed,
server-resolved tenant identifier `NewAuditEntry.community_id` depends on to
keep client input out of the chain); `buzz-datastore-tracing` (the
`#[datastore_span]` macro instrumenting `log`/`verify_chain`/`get_entries`);
`sqlx` (the Postgres driver `AuditService` holds a `PgPool` through — the
crate ships no DDL of its own, per its own crate doc); `sha2` (`Sha256`, the
hash primitive `compute_hash` is built on); `hex` (declared but not directly
called in the five `src/*.rs` files read for this node — hashes are stored
as raw `BYTEA`/`Vec<u8>`, not hex strings, so this dependency's actual call
site was not located); `chrono` (`DateTime<Utc>` and `trunc_subsecs`, the
timestamp-precision mechanism in *Divergences* below depends on); `uuid`,
`serde`/`serde_json`, `tracing`, `metrics`, `thiserror`, and `futures-util`
(the `catch_unwind`/`FutureExt` combinator `AuditService::log` uses to
release its advisory lock even across a panic) round out the crate's own
dependency list.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `crates/buzz-audit/src/lib.rs` | Crate-level statement of the hash-chain design and its explicit tie to `auditHeads[c]` | Ships no DDL — the `audit_log` table is owned by `migrations/0001_initial_schema.sql` |
| `migrations/0001_initial_schema.sql` (`CREATE TABLE audit_log`, `idx_audit_log_hash`) | The conformance row's required key shape: `PRIMARY KEY (community_id, seq)`, unique `(community_id, hash)` | Migration-owned, not crate-owned |
| `migrations/0029_community_deletion.sql` (`attach_community_write_fence('audit_log')`) | Database-level tenant fencing, independent of the crate's own hashing | Confirms isolation is enforced at two layers, not one |
| `crates/buzz-audit/src/service.rs` — `AuditService::log` | Per-community advisory lock (`pg_advisory_lock(hashtextextended(...))`), monotonic `seq`, chain-linked `prev_hash`, lock released on every exit path including a caught panic | The write half of the chain |
| `crates/buzz-audit/src/service.rs` — `AuditService::verify_chain`, `get_entries` | Reads scoped to one `community_id`; recomputes and compares hashes; detects `ChainViolation`/`HashMismatch` | The read/verify half; both are operator-internal, no client-reachable route calls them |
| `crates/buzz-audit/src/hash.rs` — `compute_hash`, `to_storage_precision`, `canonical_json` | SHA-256 over a fixed field order with `community_id` first ("tenant binding"); microsecond timestamp normalization so the digest survives a Postgres round-trip; deterministic JSON key ordering | The tamper-evidence mechanism itself |
| `crates/buzz-audit/src/error.rs` — `AuditError` | The conformance row's "errors are sanitized" and "must not leak cross-community IDs, constraint names, or existence facts" requirements | Enforced structurally (no variant has a `community_id` field) and pinned by a same-file test |
| `crates/buzz-audit/src/entry.rs` — `NewAuditEntry.community_id: CommunityId` | The conformance row's "every tenant-observable audit entry is labeled with the resolved community" requirement, plus the "server-resolved, never client input" provenance rule shared with the rest of the multi-tenant model | Not `Deserialize`, deliberately, per its own doc comment |
| `crates/buzz-audit/src/action.rs` — `AuditAction` | The conformance row's "records event/channel/auth/media actions" requirement | 11 variants; hand-written `as_str`/`FromStr`, not derived |
| `crates/buzz-relay/src/main.rs` (audit pool construction) | Wires the crate into the relay process, gated on `BUZZ_AUDIT_ENABLED` | 5 max / 1 min connection pool, independent of `buzz-db`'s pool |
| `crates/buzz-relay/src/state.rs` (`AppState::audit`, `audit_tx`, `AuditShutdownHandle`) | The relay's actual write path: a bounded `mpsc` queue and background worker, not a synchronous call into `AuditService::log` | See *Divergences* |
| `crates/buzz-relay/src/handlers/event.rs` (`enqueue_event_created_audit`, `dispatch_persistent_event`) | The integrated ingest path that turns a relay-accepted event into a queued audit entry | Also where the two integrated audit tests live |

## Divergences

- **The crate's own public API is synchronous; the relay's actual write path
  is not.** `AuditService::log` is an `async fn` that itself awaits a
  Postgres round trip under an advisory lock, but `crates/buzz-relay/src/
  handlers/event.rs` never calls it directly from a request handler. Instead
  it sends a `NewAuditEntry` onto a bounded `mpsc::channel(1000)`
  (`AppState::audit_tx`), and a single background worker
  (`state.rs`'s `audit_worker_handle`) is the only caller of `AuditService::
  log`/`log_audit_entry`. This is a deliberate, commented design (decouple
  request latency from audit-DB latency; the per-community advisory lock
  already serializes at most one in-flight write, so a full queue signals an
  overloaded audit DB) rather than drift — but it means reading
  `AuditService::log`'s doc comment in isolation understates the real
  request-to-audit-row path, which this node's *Implementation surface*
  table names explicitly for that reason.
- **A full audit queue drops the entry rather than blocking or failing the
  request.** `enqueue_event_created_audit`'s own comment states this is
  intentional. The conformance row's stated model does not address
  queue-drop behavior at all — it is neither confirmed nor contradicted by
  `docs/multi-tenant-conformance.md`'s text, so this is recorded as an
  implementation decision the target document is silent on, not as a
  violation of it.
- **`buzz-admin` declares a dependency on `buzz-audit` it does not use.**
  `crates/buzz-admin/Cargo.toml` lists `buzz-audit` as a workspace
  dependency, but neither of `buzz-admin`'s two source files
  (`main.rs`, `deletions.rs`) references `buzz_audit` or `AuditService` at
  all. `crates/buzz-test-client/tests/conformance_multitenant.rs`'s own
  `audit_log` module states the operator-internal read methods are
  "consumed by `buzz-admin`" — that claim does not currently hold against
  `buzz-admin`'s source. This node records the code as the fact and flags
  the conformance test's prose as stale on this one point, per this
  document's own evidence-precedence rule (code over documentation for
  current behavior); it does not attempt to fix either side.
- **No divergence found in the hash-chain design itself against either
  target.** The table/index shape, the community-first hash field order, the
  advisory-lock serialization, and the error-sanitization behavior were each
  checked directly against `docs/multi-tenant-conformance.md`'s stated model
  (see *Implementation surface* above) and found to match; `auditHeads[c]`'s
  non-interference framing in the TLA+ spec was checked for presence and
  purpose, not re-derived as a full proof — this node does not attempt to
  independently verify the TLA+ model's own correctness, only that the crate
  cites it accurately and that the crate's cross-community hash binding
  (`community_id` hashed first, folded into every entry) is the same
  property `auditHeads` is a function *of* community.

## Verification

- **Automated, no infrastructure:** `crates/buzz-audit/src/hash.rs`,
  `action.rs`, and `error.rs` each carry `#[cfg(test)]` unit tests that run
  under `just test-unit` with no Postgres — timestamp-precision handling,
  action string round-tripping, and the error-text non-leakage assertion.
- **Automated, requires Postgres:** `crates/buzz-audit/src/service.rs`
  carries five `#[ignore = "requires Postgres"]` async tests exercising
  chain start/link behavior, per-community independence under interleaved
  writes, tamper detection, and cross-community replay rejection — these run
  under `just test` (the integration suite), not `just test-unit`.
- **Integrated, requires Postgres + Redis:** `crates/buzz-relay/src/
  handlers/event.rs`'s two audit-specific tests exercise the real ingest
  path (`dispatch_persistent_event`) rather than `AuditService` in
  isolation.
- **Conformance suite, doc-only for this subsystem:** `crates/buzz-test-
  client/tests/conformance_multitenant.rs`'s `mod audit_log` deliberately
  contains no assertions of its own. Its own doc comment explains why: audit
  has no client-reachable wire route, so there is no black-box wire response
  to assert a denial against, unlike every other row in that suite. It
  instead names the two tests above as where the two halves of the
  isolation obligation are actually proven — this node independently
  confirmed both named test functions exist at their stated paths rather
  than taking the citation on trust.
- **No CI gate specific to this crate was found** beyond the workspace-wide
  `just ci`/`just test`/`just test-unit` targets that already cover it as
  part of the full test run; no crate-specific Justfile target or GitHub
  Actions job was found scoped to `buzz-audit` alone.

## Relationships

- part-of: architecture-containers-relay
- references: architecture-containers-postgres

## Scope and omissions

**This node covers** what `crates/buzz-audit` is responsible for (the
hash-chain audit log's design, its public `AuditService` surface, and the
`audit_log` table shape it depends on), how the crate is wired into
`buzz-relay` at runtime (pool construction, the bounded-queue write path,
graceful-shutdown draining), what evidence backs its claimed realization of
`docs/multi-tenant-conformance.md`'s audit row and `docs/spec/
MultiTenantRelay.tla`'s `auditHeads`, and where each layer of that claim is
actually verified today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The separate `moderation_actions`/`moderation_reports` audit trail (operator moderation actions, not the tamper-evident event/media chain this node documents) | `crates/buzz-db/src/store/admin_moderation.rs`; `BUZZ_AUDIT_ENABLED=false` does not disable it, per that file's own comment and `TESTING.md` |
| The `audit_log` table's schema and its community-fence trigger (`attach_community_write_fence`) | `migrations/0001_initial_schema.sql`, `migrations/0029_community_deletion.sql` — DDL this crate deliberately does not ship |
| The multi-tenant conformance model as a whole, beyond the one audit row this node checks the crate against | `docs/multi-tenant-conformance.md` |
| The formal non-interference proof `auditHeads[c]` is part of | `docs/spec/MultiTenantRelay.tla` — this node cites the model's existence and shape, not a re-derivation of its proof |
| `buzz-relay`'s own responsibility, technology and boundary as a container | `architecture-containers-relay` (`part-of`) |
| Postgres's own responsibility, connection-pooling ownership and topology as a container, including the audit pool's sizing from Postgres's side | `architecture-containers-postgres` (`references`) |
| Whether the unused `buzz-audit` dependency in `buzz-admin/Cargo.toml` should be removed or the `conformance_multitenant.rs` prose corrected | Recorded as a divergence above; not filed as a separate issue by this task |

**No `implements` relationship is declared.** Both targets this node
documents a realization of — `docs/multi-tenant-conformance.md`'s audit row
and `docs/spec/MultiTenantRelay.tla`'s `auditHeads` — are real files this
node opened directly, but neither is itself a corpus node with a stable id
at the recorded revision (checked against `origin/launchpad`'s corpus tree).
Per `AGENTS.md`, an edge to a nonexistent id is a hard validation error, not
a soft placeholder — the *Target* section above names both by path instead.

**No relationship toward any other `implementation/crates/*` sibling is
declared.** This is the first node in that subdirectory; no sibling exists
on `origin/launchpad` to point at.

**Expected but not verified when this node was written:**

- **Whether `docs/multi-tenant-conformance.md`'s "Audit log and
  observability" row was checked against `buzz-audit` by the same author who
  wrote both**, or independently derived twice and found to agree, was not
  established — this node only confirms the two currently agree at this
  revision, not the history of how they came to.
- **`docs/spec/MultiTenantRelay.tla`'s own model-checking status** (whether
  `MultiTenantRelay.cfg` has actually been run through TLC, and what it
  proved) was not checked — this node confirms `auditHeads` is a real,
  present component of the specification with the stated shape, not that
  the specification itself has been mechanically verified.
- **Whether the unused `buzz-audit` dependency in `buzz-admin/Cargo.toml`
  reflects planned-but-unbuilt operator tooling or is simply stale** was not
  established from source alone; no issue or PR discussing it was found by
  this task.

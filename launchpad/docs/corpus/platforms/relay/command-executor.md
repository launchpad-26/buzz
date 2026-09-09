---
id: platforms-relay-command-executor
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The module's own crate-doc-style comment states its responsibility verbatim: 'Command executor — transactional event processing for command kinds. Command kinds (41010–41012, 30620, 46020, 46030–46031) are processed transactionally: validate → begin tx → insert event → execute mutations → commit,' and further states it is only reachable after the ingest pipeline has verified event signature, timestamp freshness, pubkey/auth identity match, and per-kind scope authorization."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1-10"
  - statement: "handle_command is the single dispatch entry point: it first calls state.db.ensure_user to satisfy a foreign-key requirement, then matches the event's kind against exactly seven constants (KIND_DM_OPEN, KIND_DM_ADD_MEMBER, KIND_DM_HIDE, KIND_WORKFLOW_DEF, KIND_WORKFLOW_TRIGGER, KIND_APPROVAL_GRANT, KIND_APPROVAL_DENY), routing each to its own handler function; any other kind reaching it is rejected as 'unknown command kind'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:36-77"
  - statement: "is_command_kind, in buzz-core, defines the exact same seven kinds as 'a Buzz command kind that requires transactional execution,' and buzz-relay/src/handlers/ingest.rs's ingest_event_inner calls this function and routes matching events to command_executor::handle_command only after signature verification, timestamp-drift, content-size, pubkey/auth-identity and per-kind scope checks have all already passed — the code's own comment states this ordering is deliberate ('never before')."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:815-826"
      - "crates/buzz-relay/src/handlers/ingest.rs:2277-2279"
  - statement: "required_scope_for_kind maps all seven command kinds to the single transport-level scope Scope::MessagesWrite, so the ingest pipeline's scope gate only proves the caller can submit message writes at all; per-command authorization (channel membership, workflow ownership, approver identity) is enforced separately inside each handler below, not by the scope gate."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:542-544"
  - statement: "persist_command_event is the shared idempotency/CAS boundary every handler calls before executing its domain mutation: it opens a transaction, acquires buzz_deletion's community write-fence guard, and then either inserts a plain event (non-replaceable command kinds) or, for a NIP-33 d-tagged event (workflow definitions), calls buzz_db::replace_parameterized_event_in_transaction with a precondition derived from an optional expected-revision tag — returning PersistResult::Duplicate on a replay/loss and PersistResult::Inserted(tx) with an open transaction the caller must commit after its own mutation succeeds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:79-196"
  - statement: "parse_expected_workflow_revision only applies its 32-byte-hex validation to KIND_WORKFLOW_DEF events; for every other command kind it returns Ok(None) unconditionally, which is what lets the same persist_command_event path serve both replaceable (workflow) and non-replaceable (DM, approval, trigger) command kinds without a second code path."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:198-219"
  - statement: "handle_dm_open validates 1-8 other participants from p tags, persists the command event for idempotency, then calls db.open_dm with the deduplicated participant set; only if the DM channel was newly created does it emit cache invalidation, a system message, group-discovery events and per-participant membership notifications as post-commit, best-effort side effects — a re-open of an existing DM instead republishes the caller's own NIP-DV visibility snapshot."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:297-429"
  - statement: "handle_dm_add_member requires the caller to already be a cached member of the target channel and that channel to be of type \"dm\"; because DM participant sets are immutable, it does not mutate the existing DM but calls db.open_dm again with the existing members plus the new p-tag pubkeys (capped at 9 total), which returns a new channel row when the expanded set does not already exist."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:431-566"
  - statement: "handle_dm_hide requires the caller to be a member of the target DM channel, then calls db.hide_dm for the caller only (not the whole channel) and republishes that caller's own NIP-DV visibility snapshot as a post-commit side effect so the DM can be filtered out of their own sidebar."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:568-639"
  - statement: "handle_workflow_def requires only channel membership to save an ordinary workflow definition, but a definition whose parsed WorkflowDef::requires_elevated_authority() is true (i.e. it contains a call_webhook step) additionally requires the caller's channel role to be owner or admin, checked via db.get_member_role with a fail-closed error path; an existing workflow at the same d-tag UUID owned by a different pubkey or channel is rejected rather than silently reassigned."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:641-813"
  - statement: "handle_workflow_def preserves a workflow's existing webhook secret across updates (only generating a new one the first time a definition gains a Webhook trigger), computes the definition hash after secret injection, and upserts by the NIP-33 d-tag UUID against tenant.community() — the request's server-bound tenant — rather than any client-supplied value, with a code comment explaining this prevents a colliding channel UUID in a different community from taking ownership of the wrong tenant's workflow."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:714-793"
  - statement: "handle_workflow_trigger (manual trigger, kind 46020) requires the caller's pubkey to exactly equal workflow.owner_pubkey — channel membership alone is explicitly stated as insufficient — and also requires the workflow to be enabled and Active before re-checking the owner's current channel authority via workflow_engine.check_owner_authority; only after all of that does it persist the command event (scoped to the workflow's own channel, not a global event) and call db.create_workflow_run, then tokio::spawn the shared executor's execute_from_step starting at step 0."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:815-986"
  - statement: "check_approver_spec enforces a fail-closed rule for who may act on an approval: an empty string or the literal \"any\" allows any authenticated caller, a 64-character hex string allows only the pubkey it names (case-insensitive), and any other spec — including anything role-based — is rejected as 'not yet supported' rather than being interpreted permissively."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:988-1018"
  - statement: "handle_approval_grant and handle_approval_deny share an identical validation shape (approval must be Pending and not past expires_at, caller must pass check_approver_spec) before persisting the command event and calling db.update_approval_by_stored_hash; a false return from that update (the approval was already acted on by a concurrent request) is rejected as 'approval already acted on (race)' rather than treated as success, which is this handler's specific defense against a grant/deny race."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1020-1270"
  - statement: "On grant, handle_approval_grant spawns resume_workflow_after_approval (community_id, run_id, workflow_id, approval.step_index + 1) after its own transaction commits; on deny, handle_approval_deny instead spawns a task that re-fetches the run, requires its status to still be RunStatus::WaitingApproval, and marks it RunStatus::Cancelled with error code 'approval_denied' — denial never resumes step execution."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1100-1256"
  - statement: "resume_workflow_after_approval re-fetches the run and refuses to act unless its status is still RunStatus::WaitingApproval, reconstructs a step_outputs map from the run's own execution_trace JSON, restores the original TriggerContext from the run's stored trigger_context, and calls buzz_workflow::executor::execute_from_step at the given resume_index before handing the result to engine.finalize_run — the same finalize_run entry point the referenced workflow-execution flow node documents as the single place every execution path's terminal state is decided."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1272-1367"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Three plain #[test] unit tests exercise parse_expected_workflow_revision directly and run in the default test suite with no external infrastructure: workflow_revision_parser_accepts_create_and_valid_update (tagless and valid-hex cases), workflow_revision_parser_rejects_malformed_values (non-hex and wrong-length values), and revision_tag_does_not_change_other_command_kinds (a non-workflow kind ignores the tag entirely)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1430-1467"
  - statement: "Two #[tokio::test] integration tests are marked #[ignore = \"requires Postgres\"] and are not part of the default unit-test run: workflow_persistence_preserves_replays_and_rejects_dominated_cas_updates (exact replays stay idempotent, a stale expected-revision is rejected, a distinct dominated CAS update is rejected rather than silently reported as duplicate) and workflow_persistence_replays_legacy_malformed_revision_before_validation (a pre-existing malformed revision tag can still be exactly replayed, but a distinct event with the same malformed tag is rejected)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:1471-1630"
  - statement: "buzz-relay/Cargo.toml declares direct dependencies on buzz-core, buzz-db, buzz-datastore-tracing, buzz-deletion and buzz-workflow (with its \"reqwest\" feature) — the crates this module's imports (buzz_core::kind, buzz_core::tenant, buzz_db::workflow/DbError, the #[datastore_span] macro, buzz_deletion::store, buzz_workflow::executor::TriggerContext and buzz_workflow::WorkflowEngine/WorkflowDef/TriggerDef) draw on."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:19-23"
      - "crates/buzz-relay/Cargo.toml:65"
  - statement: "A crate-wide grep for \"command_executor\" outside its own file finds exactly two references: the pub mod declaration in handlers/mod.rs and the single call site in handlers/ingest.rs's ingest_event_inner — no other crate in the workspace depends on buzz-relay at all (confirmed by grepping every other crate's Cargo.toml for a leading \"buzz-relay\" dependency line and finding none), so this module's only collaborator, in either direction beyond its own file, is the relay's own ingest pipeline."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/mod.rs:8"
      - "crates/buzz-relay/src/handlers/ingest.rs:2279"
  - statement: "architecture-flows-workflow-execution, already merged on origin/launchpad, states its own scope as the three trigger paths (channel event, schedule, webhook) and the shared executor they call into, and its channel-event trigger path is explicitly conditioned on the stored event NOT being a command kind -- so it does not cover command-kind dispatch, the manual-trigger path (kind 46020), or the approval-resume path, all of which live in this module; this node references it rather than re-describing execute_steps/execute_from_step, the mechanism it already documents in full."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
    confidence: 0.85
  - statement: "type: platforms, borrowing templates/component.md's section shape (Responsibility, Public interface, Dependencies, Boundary, Relationships, Scope and omissions), is the convention sibling in-flight nodes under platforms/** have adopted for this Feature, since no platforms-specific template is merged yet; this node follows that convention rather than inventing an independent shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz Feature #614 batch dispatch brief (sibling platforms/** node convention, relayed by the orchestrating task)"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Component: relay command executor

`crates/buzz-relay/src/handlers/command_executor.rs` is the relay's single
transactional dispatcher for Buzz's seven "command" Nostr event kinds — the
subset of writes that require validate → begin-transaction → insert-event →
execute-domain-mutation → commit, rather than plain event storage and
fan-out. This node answers: which event kinds reach it, what each one does,
what authorization each enforces beyond the transport-level scope gate, and
how it hands off to (without re-documenting) the shared workflow
step-execution engine.

## Responsibility

The module's own header comment states it plainly: *"Command executor —
transactional event processing for command kinds. Command kinds (41010–41012,
30620, 46020, 46030–46031) are processed transactionally: validate → begin
tx → insert event → execute mutations → commit."* It also documents its own
precondition: it is reachable only after the ingest pipeline has verified
event signature, timestamp freshness, pubkey/auth identity match, and
per-kind scope authorization — this module never re-does those checks itself.

`handle_command` is the one entry point. It ensures the authenticated pubkey
has a `users` row (a foreign-key requirement other command mutations depend
on), then matches the event's kind against exactly seven constants and routes
to one handler each; any other kind reaching it is rejected as an internal
error ("unknown command kind"), which should be unreachable given the caller
below always pre-filters with `is_command_kind`.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `handle_command` | `pub async fn` | Routes a command-kind `Event` to its handler by `kind`; the only symbol called from outside this module | `crates/buzz-relay/src/handlers/command_executor.rs:36-77` |
| `KIND_DM_OPEN` (41010) | dispatched kind | Open (or re-open) a DM with 1-8 other participants | `crates/buzz-relay/src/handlers/command_executor.rs:297-429` |
| `KIND_DM_ADD_MEMBER` (41011) | dispatched kind | Add participants to an existing DM by creating a new DM at the expanded, immutable participant set | `crates/buzz-relay/src/handlers/command_executor.rs:431-566` |
| `KIND_DM_HIDE` (41012) | dispatched kind | Hide a DM for the calling participant only | `crates/buzz-relay/src/handlers/command_executor.rs:568-639` |
| `KIND_WORKFLOW_DEF` (30620) | dispatched kind | Create/update a workflow definition (NIP-33 upsert by `d`-tag UUID) | `crates/buzz-relay/src/handlers/command_executor.rs:641-813` |
| `KIND_WORKFLOW_TRIGGER` (46020) | dispatched kind | Manually fire a workflow run as its owner | `crates/buzz-relay/src/handlers/command_executor.rs:815-986` |
| `KIND_APPROVAL_GRANT` (46030) | dispatched kind | Grant a pending approval gate and resume the suspended run | `crates/buzz-relay/src/handlers/command_executor.rs:1020-1130` |
| `KIND_APPROVAL_DENY` (46031) | dispatched kind | Deny a pending approval gate and cancel the suspended run | `crates/buzz-relay/src/handlers/command_executor.rs:1132-1270` |
| `is_command_kind` | `pub const fn` (buzz-core) | Defines the same seven kinds as requiring transactional execution; the ingest pipeline's routing predicate | `crates/buzz-core/src/kind.rs:815-826` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `buzz-core` | Kind constants (`buzz_core::kind::*`), `TenantContext`/`CommunityId` | `crates/buzz-relay/Cargo.toml:19` |
| `buzz-db` | `Db`, `DbError`, workflow/approval record types, the `replace_parameterized_event_in_transaction` CAS primitive | `crates/buzz-relay/Cargo.toml:21` |
| `buzz-datastore-tracing` | `#[datastore_span]` instrumentation on `persist_command_event` | `crates/buzz-relay/Cargo.toml:22` |
| `buzz-deletion` | `guard_transaction` community write-fence, acquired before every domain mutation | `crates/buzz-relay/Cargo.toml:23` |
| `buzz-workflow` | `WorkflowEngine`, `WorkflowDef`, `TriggerDef`, `executor::{TriggerContext, execute_from_step}` — the shared step-execution engine this module hands off to | `crates/buzz-relay/Cargo.toml:65` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `crates/buzz-relay/src/handlers/ingest.rs` (`ingest_event_inner`) | The sole caller: routes any event whose kind satisfies `is_command_kind` to `handle_command` after signature/timestamp/auth/scope checks pass | `crates/buzz-relay/src/handlers/ingest.rs:2277-2279` |

No other crate in the workspace declares a dependency on `buzz-relay` at all,
so this module has no consumer beyond the relay's own ingest pipeline.

## Boundary

This node does not describe:
- **Workflow step execution itself** — the `if:` condition evaluation,
  template resolution, per-step timeout, and terminal-state mapping
  (`finalize_run`) that `handle_workflow_trigger`, `handle_approval_grant`
  (via `resume_workflow_after_approval`) and `resume_workflow_after_approval`
  itself all hand off into. That mechanism, shared with the channel-event and
  schedule/webhook trigger paths, is `architecture-flows-workflow-execution`'s
  subject; see *Relationships*.
- **Workflow YAML/schema validation rules** as their own subject (`WorkflowDef`
  parsing, `requires_elevated_authority()`'s exact rule set) beyond the calls
  this module makes into them.
- **The container-level decomposition of `buzz-relay`** with a diagram — no
  `architecture-component` node for the relay exists yet to be `part-of`.
- **How this component satisfies any spec/decision/contract** as a
  traceability artifact — no `implementation-reference` template is merged
  yet.
- **The relay ingest pipeline's general (non-command) event path** — signature
  verification, timestamp/content-size checks, and scope authorization in
  `ingest_event_inner` are read here only as this module's documented
  precondition, not as this node's own subject.

## Relationships

- `references: architecture-flows-workflow-execution` — the workflow
  step-execution engine this module's `handle_workflow_trigger` and
  `resume_workflow_after_approval` both call into and resume; documented
  there, not duplicated here.

No `depends-on` or `part-of` relationship is declared. `depends-on` would
require another corpus node whose claims this one's own claims rest on for
their own currency — the crates this module depends on (`buzz-core`,
`buzz-db`, `buzz-deletion`, `buzz-datastore-tracing`, `buzz-workflow`) have no
corpus node of their own yet on `origin/launchpad`, so there is nothing to
target. `part-of` would require an `architecture-component` node for
`buzz-relay` decomposing it into building blocks; none exists yet.

## Scope and omissions

**This node covers** the relay's command-kind dispatch entry point, the seven
event kinds it routes, the shared idempotency/CAS persistence pattern every
handler uses, each handler's own domain mutation and authorization logic
beyond the transport-level scope gate, and the hand-off points into the
shared workflow executor (without duplicating that executor's own documented
behavior).

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Workflow step-execution mechanics (`execute_steps`/`execute_from_step`, template resolution, timeouts, `finalize_run`) | `architecture-flows-workflow-execution` |
| Workflow YAML schema and `WorkflowDef::validate()`'s own rules | Not yet a corpus node |
| `buzz-relay`'s container-level decomposition | Not yet a corpus node (no `architecture-component` template merged) |
| The general (non-command) ingest pipeline in `ingest.rs` | Not yet a corpus node |

**Expected but not verified when this node was written:**

- The two `#[ignore = "requires Postgres"]` integration tests
  (`workflow_persistence_preserves_replays_and_rejects_dominated_cas_updates`,
  `workflow_persistence_replays_legacy_malformed_revision_before_validation`)
  were read in full but not executed against a live Postgres instance in this
  task — their assertions are cited as what the test *code* asserts, not as a
  confirmed-passing run.
- Whether any client (desktop, mobile, CLI) currently relies on the exact
  `"response:{...}"` message-string convention these handlers return was not
  checked; this node only establishes what the relay-side handlers produce.

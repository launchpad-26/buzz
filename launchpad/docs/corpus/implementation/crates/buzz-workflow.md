---
id: implementation-crates-buzz-workflow
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "crates/buzz-workflow has exactly five source files under src/ (lib.rs 2090 lines, executor.rs 1969, schema.rs 1001, error.rs 114, action_sink.rs 73), no README.md, and no separate tests/ directory -- all tests are inline #[cfg(test)] mod tests blocks in error.rs and executor.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs"
      - "crates/buzz-workflow/src/executor.rs"
      - "crates/buzz-workflow/src/schema.rs"
      - "crates/buzz-workflow/src/error.rs"
      - "crates/buzz-workflow/src/action_sink.rs"
  - statement: "lib.rs's own module doc comment states the crate's four-module architecture (schema: YAML/JSON definition types; executor: sequential execution, template resolution, condition evaluation; error: WorkflowError; and WorkflowEngine itself as 'top-level handle; lives in AppState') and gives a canonical usage example: WorkflowEngine::new, parse_yaml, engine.on_event(...), and tokio::spawn(engine.run())."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1-29"
  - statement: "crates/buzz-workflow/Cargo.toml declares dependencies on buzz-core, buzz-db, buzz-deletion, evalexpr (v11), cron (v0.16), nostr, and an optional reqwest feature (feature name 'reqwest', gating dep:reqwest) -- buzz-db is a direct dependency, so buzz-workflow does not merely receive a database handle from its caller, it links the persistence crate itself."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/Cargo.toml"
  - statement: "crates/buzz-relay/Cargo.toml and crates/buzz-admin/Cargo.toml both declare buzz-workflow as a workspace dependency; grepping crates/buzz-admin/src for buzz_workflow found zero call sites, so this node reports the buzz-admin dependency as a Cargo.toml fact only, without claiming it reflects actual runtime usage."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-admin/Cargo.toml"
  - statement: "crates/buzz-relay/src/workflow_sink.rs implements the crate's ActionSink trait as RelayActionSink (impl ActionSink for RelayActionSink), and crates/buzz-relay/src/main.rs constructs the engine (WorkflowEngine::new(db.clone(), workflow_config)) and wires the sink (workflow_engine.set_action_sink(action_sink)) -- the only non-test construction/wiring site in the relay binary; every other WorkflowEngine::new call found in buzz-relay is inside a #[cfg(test)] module."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/workflow_sink.rs:172"
      - "crates/buzz-relay/src/main.rs:436"
      - "crates/buzz-relay/src/main.rs:644"
  - statement: "crates/buzz-db/src/store/workflow.rs owns all workflow persistence: WorkflowRecord/WorkflowRunRecord/ScheduledWorkflowFireClaim/ApprovalRecord row types and every CRUD/query function (create_workflow, upsert_workflow, list_enabled_channel_workflows, claim_scheduled_workflow_fire, create_workflow_run, update_workflow_run, create_approval, and others) -- buzz-workflow's own source tree contains no SQL and no table definition."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs"
  - statement: "crates/buzz-relay/src/router.rs registers POST /hooks/{id} against api::bridge::workflow_webhook; buzz-workflow's own source tree contains no HTTP route registration and no axum handler -- the crate is invoked by the relay's handler, not the reverse."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:132"
  - statement: "crates/buzz-relay/src/handlers/command_executor.rs is the kind:30620 workflow-definition-save path: it calls buzz_workflow::WorkflowEngine::parse_yaml on the command event's content to validate a submitted definition before persisting it, derives the webhook shared secret only when the parsed trigger matches buzz_workflow::TriggerDef::Webhook, and calls buzz_workflow::executor::execute_from_step directly for the approval-resume code path -- buzz-workflow itself owns none of the kind:30620 authority/save logic, only the parse/validate function and the executor entry point that command_executor.rs calls into."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:672"
      - "crates/buzz-relay/src/handlers/command_executor.rs:716"
      - "crates/buzz-relay/src/handlers/command_executor.rs:960"
      - "crates/buzz-relay/src/handlers/command_executor.rs:1354"
  - statement: "WorkflowEngine::new(db, config) builds a WorkflowConfig-sized tokio::sync::Semaphore (run_semaphore), an empty DashMap (last_fired, keyed (CommunityId, Uuid) for interval-trigger liveness), a OnceLock<Arc<dyn ActionSink>> (action_sink, late-initialized via set_action_sink and panicking if set twice), and a moka::sync::Cache keyed (CommunityId, Uuid) with max_capacity 10_000 and a 10-second time_to_live (workflow_cache) for the per-channel enabled-workflow list; invalidate_channel_workflows(community_id, channel_id) drops one cache entry and its own doc comment states it must be called after any write to a workflow's trigger eligibility or channel binding."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:73-131"
  - statement: "WorkflowConfig has two fields, max_concurrent (default 100) and default_timeout_secs (default 300), both via a Default impl; WorkflowEngine::new floors max_concurrent at 1 (config.max_concurrent.max(1)) before sizing the semaphore, so a caller passing 0 still gets a usable engine rather than a permanently-starved one."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:56-71"
      - "crates/buzz-workflow/src/lib.rs:107-113"
  - statement: "check_owner_authority is documented in its own doc comment as the 'fail-closed pre-run authority gate (SEC-006)': it looks up the owner's current channel role via self.db.get_member_role, and any lookup error is mapped to WorkflowError::Unauthorized rather than propagated as a different error class or allowed to pass -- the doc comment states this explicitly: 'a removed owner must never keep exfiltration authority because a membership read happened to fail.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:141-179"
  - statement: "WorkflowDef::requires_elevated_authority returns true iff any step's action matches ActionDef::CallWebhook; owner_authority_allows (called by check_owner_authority) is the function architecture-flows-workflow-execution's own evidence ledger already documents as encoding the three-case authority rule (not-a-member denies; member allows an ordinary definition; call_webhook additionally requires owner/admin) -- not re-verified independently by this node beyond confirming requires_elevated_authority's own definition, to avoid duplicating that sibling node's already-cited claim."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:161-169"
  - statement: "WorkflowDef::validate() enforces: non-empty name; at least one step; every step id non-empty, <=64 chars, matching only ASCII alphanumerics and underscore (because step ids become evalexpr variable names of the form steps_{id}_output_{field}), and unique within the definition; reply_in_thread rejected at definition time unless the trigger is MessagePosted/ReactionAdded/DiffPosted (schedule and webhook triggers have no triggering message to reply to); and for a Schedule trigger, exactly one of cron/interval is required (both-or-neither is InvalidDefinition), a supplied cron string is parsed by the cron crate via a 5/6/7-field normalizer (normalize_cron), and a supplied interval below 60 seconds is rejected because the cron loop itself only ticks once a minute."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:169-273"
  - statement: "parse_yaml(yaml) deserializes into WorkflowDef via serde_yaml, calls def.validate(), and re-serializes to canonical JSON via serde_json -- validate() is unconditionally on the parse path, so no code path can obtain a WorkflowDef from YAML without it also passing validation; WorkflowEngine::parse_yaml (the crate's public re-export used by buzz-relay's command_executor.rs) is a thin pub fn that forwards to schema::parse_yaml."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:305-315"
      - "crates/buzz-workflow/src/lib.rs:196-202"
  - statement: "evalexpr condition evaluation is deliberately bounded, per two named constants and their surrounding comments in executor.rs: EVAL_TIMEOUT (100ms, tokio::time::timeout around a tokio::task::spawn_blocking evaluation, because 'evalexpr is not designed for adversarial input -- a deeply nested or recursive expression can spin indefinitely') and MAX_EXPR_LEN (4096 bytes, rejected before evaluation even starts, because the spawn_blocking thread cannot be cancelled by the timeout and will run to completion even after it fires -- length-limiting is what actually bounds worst-case O(2^n) evaluation paths, the timeout alone does not)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:355-395"
  - statement: "build_eval_context registers four custom evalexpr functions not shipped by evalexpr v11 itself (str_contains, str_starts_with, str_ends_with, str_len) and populates trigger_* variables (trigger_text, trigger_author, trigger_channel_id, trigger_timestamp, trigger_emoji, trigger_message_id, trigger_is_reply) plus steps_{id}_output_{field} variables from prior step outputs; webhook body fields are registered first, under a trigger_ prefix, and any webhook field literally named trigger_* or steps_* is skipped during that first pass specifically so a standard trigger field inserted afterward always overwrites and cannot be spoofed by webhook input -- verified by reading the loop and its comment directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:229-323"
  - statement: "condition_exceeding_max_expr_len_is_rejected is a unit test in executor.rs's own test module that constructs a 5000-byte expression (\"true || \".repeat(625)) and asserts evaluate_condition returns a WorkflowError::ConditionError whose message contains 'exceeds' or 'limit' -- representative verification for the MAX_EXPR_LEN safety bound above."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1527-1543"
  - statement: "condition_true_when_text_contains_p1 is a unit test asserting evaluate_condition(\"str_contains(trigger_text, \\\"P1\\\")\", ...) returns true against a TriggerContext whose text field contains 'P1' -- representative verification that the custom str_contains function registered by build_eval_context is reachable from an actual if: expression, not merely defined."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1412-1420"
  - statement: "ActionSink is a Send + Sync trait with one method, send_message(community_id, channel_id, text, author_pubkey, reply_to) -> Pin<Box<dyn Future<...> + Send>>, whose doc comment states it 'replaces the HTTP loopback where the executor POSTed to the relay's REST API (which failed with 401 auth errors)' and that community_id is always the run's own owning community, never the deployment default, so a workflow in community B posts into B even without an inbound connection to bind to; ActionSinkError (InvalidInput, ChannelNotFound, ChannelArchived, EventBuild, Database, EmptyContent) converts into WorkflowError::WebhookError via a From impl."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/action_sink.rs"
  - statement: "WorkflowError has nine variants (InvalidYaml, InvalidDefinition, ConditionError, TemplateError, StepTimeout{step_id,timeout_secs}, WebhookError, CapacityExceeded, Database, Unauthorized) and a From<buzz_db::error::DbError> impl mapping DB errors into the Database variant; error.rs's own unit test module (mod tests) verifies at least one property of WorkflowError's behavior directly in-crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs"
  - statement: "This is the first node under launchpad/docs/corpus/implementation/ -- git ls-tree -r --name-only HEAD -- launchpad/docs/corpus at the recorded revision lists no implementation/ entries at all, so no sibling implementation-reference instance exists yet to cross-link against."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='76a0a4ebbe4bc4d852b0d04362ed768620da34b3', path='launchpad/docs/corpus') -> no implementation/ entries"
  - statement: "launchpad/docs/corpus/architecture/flows/workflow-execution.md (id architecture-flows-workflow-execution, type architecture, status draft) is merged on origin/launchpad and already documents crates/buzz-workflow's three trigger paths, the shared sequential executor, trust-boundary crossings (SEC-006 authority, webhook shared-secret, SSRF-guarded call_webhook), and failure/abort/rollback behavior in detail with its own representative-test citations -- this node deliberately does not restate those claims, citing the sibling node instead per its Scope and omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Issue #941's Definition of Done (copied from the corpus-batch-author task manifest) requires stating implementation responsibility and what it deliberately does not own, naming public interfaces/entry points and important dependencies, and linking owned source paths and representative tests without restating domain semantics already canonical in capability/layer/interface nodes -- this is the acceptance bar this node's Implementation surface and Scope and omissions sections are built against."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#941 definition of done"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# buzz-workflow: implementation reference

`crates/buzz-workflow` is the YAML-as-code workflow engine that parses and validates
workflow definitions, matches them against trigger events, and sequentially executes
their steps with template resolution, `evalexpr` condition evaluation, timeouts, and an
execution trace. It does not implement a single named spec, decision, or ADR document —
no NIP, ADR, or standalone specification enumerates "what a Buzz workflow must do" as a
normative target this crate realizes. Its closest corpus counterpart is
`architecture-flows-workflow-execution`, which documents the same subsystem's runtime
*behavior* (trigger paths, ordered interactions, trust-boundary crossings, failure
handling) as an architecture flow. This node instead documents the crate as a piece of
code: its own module boundaries, public interfaces, dependencies, and — critically — what
it does *not* own, deferring every behavioral claim already established there rather than
re-deriving it.

## Target

There is no spec/decision/contract document with its own corpus node id (or repository
path) that this crate implements in the ISTQB traceability sense the
`implementation-reference` template calls for. The nearest documentation target is
`launchpad/docs/corpus/architecture/flows/workflow-execution.md` — a description of
intended and observed runtime behavior, not a normative contract the crate was built
*against*. Per the template's own guidance ("if the realizing artifact is itself a
protocol/contract surface... an author may reasonably choose [a different surface]"),
this node treats that sibling node as a `references` target (supporting context) rather
than an `implements` target (concrete realization of a named spec), because declaring
`implements` here would assert a directionality — "this crate is the concrete realization
of that document" — that does not hold; the architecture doc was itself derived by reading
this crate's code, not the other way around.

## Implementation surface

| Component / file / symbol | Responsibility | Note |
|---|---|---|
| `crates/buzz-workflow/src/lib.rs` — `WorkflowEngine` | Top-level handle: owns the DB pool reference, run-concurrency semaphore, interval last-fired map, action sink, and the per-channel enabled-workflow cache; `on_event`/`run`/`finalize_run`/`check_owner_authority`/`parse_yaml` entry points | Lives in the relay's `AppState`; constructed once in `main.rs`, `Arc`-shared |
| `crates/buzz-workflow/src/schema.rs` — `WorkflowDef`, `TriggerDef`, `Step`, `ActionDef` | YAML/JSON definition types and `WorkflowDef::validate()` — the sole gate a definition must pass before any trigger path can ever run it | `parse_yaml()` calls `validate()` unconditionally; no code path bypasses it |
| `crates/buzz-workflow/src/executor.rs` — `TriggerContext`, `resolve_template`, `build_eval_context`, `evaluate_condition`, `resolve_step_templates`, `dispatch_action`, `execute_run`, `execute_from_step` | Sequential step execution: condition evaluation, template resolution, timeout-bounded action dispatch, trace accumulation | Owns the `evalexpr` safety bounds (`EVAL_TIMEOUT`, `MAX_EXPR_LEN`) and all `ActionDef` dispatch logic |
| `crates/buzz-workflow/src/error.rs` — `WorkflowError`, `PartialProgress` | The crate's single error enum and the partial-trace-on-failure carrier | `From<buzz_db::error::DbError>` maps DB errors into `WorkflowError::Database` |
| `crates/buzz-workflow/src/action_sink.rs` — `ActionSink` trait, `ActionSinkError` | The seam between the executor and side-effecting I/O; `Send + Sync`, dyn-compatible (`Pin<Box<dyn Future>>` return) | Implemented by `crates/buzz-relay/src/workflow_sink.rs`'s `RelayActionSink`; late-bound via `set_action_sink` after `AppState` construction |

## Divergences

None found, checked specifically against the crate's own doc comments for
self-acknowledged gaps: `lib.rs`'s module doc, the `EVAL_TIMEOUT`/`MAX_EXPR_LEN`
comments in `executor.rs`, and `check_owner_authority`'s doc comment were all read and
each matches the code beneath it (the doc comment claims and the executable behavior
agree — e.g. the `check_owner_authority` doc comment's "any lookup error denies" claim
matches the `map_err(...) -> WorkflowError::Unauthorized` beneath it). This node does not
independently re-verify `architecture-flows-workflow-execution`'s own divergence findings
(reserved kinds 46001–46012 never emitted, `SendDm`/`SetChannelTopic` permanently
`NotImplemented`, `RequestApproval` mapped to `Failed` rather than `WaitingApproval`) —
those are that sibling node's claims to maintain, not restated here as this node's own.

## Verification

Automated, all in-crate: `error.rs` and `executor.rs` each carry a `#[cfg(test)] mod
tests` block (no separate `tests/` directory). Representative examples opened directly:
`condition_exceeding_max_expr_len_is_rejected` (`executor.rs`) exercises the
`MAX_EXPR_LEN` rejection path with a 5000-byte expression; `condition_true_when_text_contains_p1`
(`executor.rs`) exercises the custom `str_contains` evalexpr function end-to-end through
`evaluate_condition`. No `tests/` integration suite exists inside `buzz-workflow` itself;
cross-crate integration coverage (multi-tenant confinement, channel-override rejection)
lives in `crates/buzz-test-client/tests/conformance_multitenant.rs`, already cited by
`architecture-flows-workflow-execution`'s own Verification section and not re-cited here
to avoid duplicating that ledger.

## Relationships

- references: `architecture-flows-workflow-execution` — the sibling corpus node
  documenting this crate's runtime behavior (trigger paths, ordered interactions,
  trust-boundary crossings, failure handling) in depth; this node does not restate those
  claims.
- implements: none declared. No spec/decision/contract corpus node or repository document
  exists yet for this crate to `implements` toward, per the *Target* section above.
- part-of: none declared. `buzz-workflow` is not documented here as a sub-component of a
  broader implementation-reference node, because no broader crate/service-level
  implementation node exists yet in the merged corpus.

## Scope and omissions

**This node covers** `crates/buzz-workflow`'s own responsibility boundary, public
interfaces and entry points, its dependency surface (`buzz-core`, `buzz-db`,
`buzz-deletion`, `evalexpr`, `cron`, `nostr`), the `evalexpr` safety bounds it owns
(`EVAL_TIMEOUT`, `MAX_EXPR_LEN`, the custom function registrations), and representative
in-crate tests.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Trigger-path behavior, ordered interactions, trust-boundary crossings, failure/abort/rollback semantics | `architecture-flows-workflow-execution` |
| Workflow persistence: `WorkflowRecord`/`WorkflowRunRecord`/`ScheduledWorkflowFireClaim`/`ApprovalRecord` row shapes and all CRUD/query functions | `crates/buzz-db/src/store/workflow.rs` |
| The `POST /hooks/{id}` route registration and HTTP surface | `crates/buzz-relay/src/router.rs`, `crates/buzz-relay/src/api/bridge.rs` |
| The `kind:30620` workflow-definition-save command's own save-time authority/validation flow (as opposed to the `parse_yaml`/`validate()` function it calls into) | `crates/buzz-relay/src/handlers/command_executor.rs` |
| Actual side-effect execution against the database and Nostr event construction for `SendMessage` | `crates/buzz-relay/src/workflow_sink.rs` (`RelayActionSink`) |
| The approval-gate *resume* flow's product behavior (WF-08, not implemented) | `architecture-flows-workflow-execution`'s own Scope and omissions section |

**Expected but not verified when this node was written:**

- Whether `crates/buzz-admin`'s `Cargo.toml` dependency on `buzz-workflow` reflects any
  actual runtime call site was not established — a grep of `crates/buzz-admin/src` for
  `buzz_workflow` found no matches, so this dependency is reported as a build-graph fact
  only, not as evidence of a fourth entry point.
- Whether the `reqwest` feature flag on `buzz-workflow`'s `Cargo.toml` is enabled by
  `buzz-relay`'s own feature selection, and therefore whether `call_webhook`'s SSRF-guard
  code path (documented in depth by `architecture-flows-workflow-execution`, not
  independently re-verified here) is compiled into the production relay binary, was not
  checked from this node — that dependency-feature-resolution question is out of this
  node's scope.

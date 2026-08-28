# Plan: issue #688 -- corpus node for workflow execution flow

ALREADY TRUE: schema/node.schema.json and docs/corpus/AGENTS.md are merged on
origin/launchpad; the target file architecture/flows/workflow-execution.md does not
exist yet.

STEP 1 -- Gather evidence: read crates/buzz-workflow/src/lib.rs (WorkflowEngine::
on_event, run, check_owner_authority, finalize_run, should_fire_workflow,
owner_authority_allows, trigger_matches_event, build_trigger_context),
crates/buzz-workflow/src/executor.rs (execute_run, execute_from_step, execute_steps,
dispatch_action, check_ssrf, call_webhook_impl), crates/buzz-workflow/src/schema.rs
(WorkflowDef::validate, requires_elevated_authority, TriggerDef/ActionDef),
crates/buzz-workflow/src/error.rs (WorkflowError, PartialProgress),
crates/buzz-relay/src/api/bridge.rs (workflow_webhook handler), crates/buzz-relay/src/
handlers/event.rs (the on_event call site in the post-store hook), crates/buzz-db/src/
workflow.rs (RunStatus, WorkflowStatus), crates/buzz-core/src/kind.rs (the 46001-46012
workflow-execution kind range and is_workflow_execution_kind), and representative tests
in buzz-workflow's own unit tests (error.rs's workflow_error_codes_are_stable_...,
executor.rs's send_message_rejects_cross_channel_override_for_bound_workflow) and
buzz-test-client/tests/conformance_multitenant.rs's `mod workflows` (workflow_trigger_
is_community_confined, approval_token_is_community_confined). RUNS HERE.

STEP 2 -- Write front matter (id architecture-flows-workflow-execution, type
architecture, status draft, origin launchpad, audiences agent+developer, one evidence
entry per claim, no relationships -- no sibling node in the merged corpus carries an id
this flow would target) and the body: the three trigger paths (event-driven, cron/
interval, webhook) with their preconditions and termination/outcome states, ordered
interactions and data/state movement per path, the community/tenant and owner-authority
trust-boundary crossings (SEC-006) plus the webhook secret and SSRF crossings, and
failure/abort/rollback behavior (fail-closed authority checks, capacity/timeout,
partial-trace persistence, the reserved-but-unemitted 46001-46012 telemetry kinds) with
links to representative verification.

STEP 3 -- Run validate.py; fix and re-run until it exits 0.

STEP 4 -- Earn the verification stamp with the corpus unittest suite as the sole
command in its own tool call, then finalize the plan file and the new node in a
separate tool call.

PARALLEL: none -- single file, single agent.

GATES: validate.py must exit 0. review-adjudicate and any cross-model pass are
explicitly deferred to the batch owner's morning review -- not run here.

BUDGET: single document, target under 280 lines of body Markdown; evidence gathering
capped at the source files listed in STEP 1.

OPEN: the issue's DoD asks for typed relationships appropriate to the node, but the
merged corpus carries no other node this flow could target -- relationships is
correctly omitted per node.schema.json's hard-error rule on unresolved targets, and
this is stated as a real ambiguity rather than resolved by inventing a target. Also
open: whether the reserved workflow-execution kinds (46001-46012) are ever actually
emitted is documented as a verified absence (grepped, not found), not as a promise
about future work.

LEFT OUT: no per-type flows template exists yet (0 of 26 merged per AGENTS.md) -- the
node is written directly against node.schema.json and is expected to be reshaped by a
later template task, per AGENTS.md's own instruction. Approval-gate execution (WF-08)
is out of scope for this flow document beyond noting it suspends and is not yet
resumable/emitted -- that is a separate, not-yet-built capability.

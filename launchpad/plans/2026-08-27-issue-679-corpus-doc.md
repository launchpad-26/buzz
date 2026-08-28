# Plan: issue #679 -- corpus node for HTTP event submission flow

ALREADY TRUE: schema/node.schema.json and docs/corpus/AGENTS.md are merged on
origin/launchpad; the target file architecture/flows/http-event-submission.md does
not exist yet.

STEP 1 -- Gather evidence: read crates/buzz-relay/src/api/bridge.rs (submit_event,
submit_event_authed, verify_bridge_auth_with_options, check_nip98_replay_with_guard,
enforce_http_admission), crates/buzz-relay/src/handlers/ingest.rs (ingest_event,
ingest_event_inner), crates/buzz-relay/src/handlers/event.rs (dispatch_persistent_event),
crates/buzz-relay/src/tenant.rs (bind_community), crates/buzz-relay/src/router.rs
(the /events route registration), and representative tests in
crates/buzz-test-client/tests/e2e_relay.rs and buzz-relay/src/api/bridge.rs's own
unit tests. RUNS HERE.

STEP 2 -- Write front matter (id architecture-flows-http-event-submission, type
architecture, status draft, origin launchpad, audiences agent+developer, one evidence
entry per claim, no relationships -- no sibling node in the merged corpus carries an
id this flow would target) and the body: trigger/preconditions/termination, ordered
interactions with data/state movement, the host-to-community trust-boundary crossing
and the NIP-98 auth crossing, and failure/abort/rollback behavior with links to
representative tests.

STEP 3 -- Run validate.py; fix and re-run until it exits 0.

STEP 4 -- Earn the verification stamp with the corpus unittest suite as the sole
command in its own tool call, then finalize the plan file and the new node in a
separate tool call.

PARALLEL: none -- single file, single agent.

GATES: validate.py must exit 0. review-adjudicate and any cross-model pass are
explicitly deferred to the batch owner's morning review -- not run here.

BUDGET: single document, target under 250 lines of body Markdown; evidence gathering
capped at the source files listed in STEP 1.

OPEN: the issue's DoD asks for typed relationships appropriate to the node, but the
merged corpus carries no other node this flow could target -- relationships is
correctly omitted per node.schema.json's hard-error rule on unresolved targets, and
this is stated as a real ambiguity rather than resolved by inventing a target.

LEFT OUT: no per-type flows template exists yet (0 of 26 merged per AGENTS.md) -- the
node is written directly against node.schema.json and is expected to be reshaped by a
later template task, per AGENTS.md's own instruction.

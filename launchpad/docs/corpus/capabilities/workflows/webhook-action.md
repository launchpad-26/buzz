---
id: capabilities-workflows-webhook-action
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "The `call_webhook` action is one variant of `buzz-workflow`'s `ActionDef` enum: an HTTP request to an operator-supplied `url`, with an optional `method` (default `POST`), optional `headers`, and an optional `body` template; the field doc comment states the URL 'must be a public HTTPS endpoint.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:126-139"
  - statement: "`WorkflowDef::requires_elevated_authority` returns true whenever any step's action matches `ActionDef::CallWebhook`, and its own doc comment explains this is because such a step 'can exfiltrate channel data to an arbitrary external destination.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:157-169"
  - statement: "`WorkflowDef::validate()` (the full precondition check every definition must pass before it can be saved or run) contains no check of the `call_webhook` step's URL scheme, host, or reachability — it validates only the definition's name, step count, step-id uniqueness/charset, `reply_in_thread`-requires-a-message-trigger, and `Schedule`-trigger cron/interval well-formedness. The field doc comment's 'must be a public HTTPS endpoint' is therefore not enforced at definition-validation time; a `call_webhook` step with a plain `http://` URL to a public host passes `validate()` unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:173-278"
  - statement: "`WorkflowEngine::check_owner_authority` re-derives the workflow owner's *current* role in the workflow's channel and calls `owner_authority_allows(role, def.requires_elevated_authority())`; any role-lookup error is mapped to `WorkflowError::Unauthorized` (fail-closed), and the function's own doc comment states this check runs immediately before every run-creation door, not trusted from workflow-save time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:138-171"
  - statement: "`owner_authority_allows` implements the exact rule: no current membership denies unconditionally regardless of `needs_elevated`; an active member with an ordinary (non-`call_webhook`) definition is allowed; an active member with a `call_webhook`-containing definition is allowed only for the `owner` or `admin` role."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1018-1035"
  - statement: "Unit tests `owner_authority_requires_elevated_role_for_exfiltration_definitions` and `requires_elevated_authority_detects_call_webhook` are representative verification for the elevated-authority gate and for `requires_elevated_authority`'s detection of a `call_webhook` step specifically."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1862-1867"
      - "crates/buzz-workflow/src/lib.rs:1869-1887"
  - statement: "`dispatch_action` — the single entry point every step action (including `call_webhook`) is run through — acquires a durable community write fence (`buzz_deletion::acquire_serving_write`) and calls `.verify()` on it before touching any action, because, per its own comment, 'the workflow engine can outlive the serving request that spawned it'; a fence acquisition or verification failure is mapped to `WorkflowError::WebhookError` and denies the action rather than letting a stale run act on a community whose write lease has moved on."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:537-566"
  - statement: "The `CallWebhook` match arm in `dispatch_action` logs the resolved method and URL, then (when the crate's `reqwest` feature is compiled in) calls `call_webhook_impl(url, method_str, headers, body)`; when that feature is not compiled in, it instead logs a warning and returns a placeholder `{status: 0, body: null, skipped: true}` output without making any request."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:682-711"
  - statement: "`buzz-relay`'s own `Cargo.toml` depends on `buzz-workflow` with `features = [\"reqwest\"]` enabled, so in the relay binary a `call_webhook` step always takes the real HTTP-request path (`call_webhook_impl`), never the feature-gated skip stub."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:65"
  - statement: "`call_webhook_impl` parses the resolved URL, extracts host and port (defaulting to 443/80 by scheme), calls `check_ssrf(host, port)` to obtain a validated IP, then builds a per-call `reqwest::Client` with a 10-second timeout, the system proxy disabled, HTTP redirects disabled, and DNS pinned to the already-validated IP via `.resolve(host, ...)` — the client comment states this defeats a second, unpinned DNS resolution inside the HTTP client returning a different (DNS-rebinding) address than the one already checked. It then sends the resolved method/headers/body, and reads the response body incrementally in a loop, aborting with `WorkflowError::WebhookError` the moment accumulated bytes exceed `WEBHOOK_MAX_RESPONSE_BYTES` (1 MiB) rather than buffering the whole body first."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:862-950"
      - "crates/buzz-workflow/src/executor.rs:859"
  - statement: "`check_ssrf` resolves the host via the OS resolver on a blocking threadpool (`spawn_blocking`), fails closed with `WorkflowError::WebhookError` if resolution errors or returns zero addresses, and rejects the call if `buzz_core::network::is_private_ip` reports any resolved address as private/reserved — returning the first validated address for the caller to pin."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:817-855"
  - statement: "`is_private_ip` rejects, for IPv4: loopback, RFC1918 private ranges, link-local, `0.0.0.0/8`, broadcast, CGNAT (`100.64.0.0/10`), and the benchmarking range (`198.18.0.0/15`); for IPv6 it recurses into the embedded-IPv4 rules for IPv4-mapped/compatible, NAT64, and legacy SIIT-translated addresses, and separately rejects loopback, unspecified, ULA, link-local, multicast, Teredo, 6to4, and the RFC 3849 documentation range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/network.rs:46-95"
  - statement: "`is_private_ip` carries its own dedicated unit-test module (e.g. `test_loopback_v4`, `test_private_10`) exercising each rejected range individually — representative verification for the SSRF address-filtering claim above, independent of any test of `check_ssrf`/`call_webhook_impl` themselves, which have no dedicated unit or integration test found in this repository (see *Scope and omissions*)."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/network.rs:102-109"
  - statement: "A step's dispatch (any action, including `call_webhook`) runs inside `tokio::time::timeout(step.timeout_secs or engine.config.default_timeout_secs (300s), dispatch_action(...))` in `execute_steps`; on elapse this constructs `WorkflowError::StepTimeout { step_id, timeout_secs }`, distinct from and independent of the 10-second per-request timeout `call_webhook_impl`'s own `reqwest::Client` sets internally — whichever elapses first determines whether the failure surfaces as `step_timeout` or `webhook_failed`."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1164"
      - "crates/buzz-workflow/src/executor.rs:1217-1255"
  - statement: "`WorkflowError::code()` maps `WebhookError` to the stable classification `\"webhook_failed\"` and `StepTimeout` to `\"step_timeout\"`; these are the two distinct persisted `error_code` values a failed `call_webhook` step can produce, per `finalize_run`'s mapping of any step error to a `Failed` run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:68-82"
  - statement: "`ServingWriteGuard::protect` races the wrapped operation (here, the entire `dispatch_action` match block including `call_webhook_impl`'s HTTP call) against the guard's own lease-heartbeat-lost signal via `tokio::select!`, dropping the in-flight operation future and returning `ServingWriteLeaseLost` if the heartbeat is lost mid-call — a second, independent abort path beyond the step timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-deletion/src/lib.rs:66-105"
  - statement: "`dispatch_action` calls `serving_write.finish()` after `protect()` resolves, releasing the lease; on the success path a release failure is propagated as an error, but on the action-error path the release's own result is explicitly discarded (`let _ = release;`) so the original action error is what the caller sees. If the surrounding step-timeout instead cancels the whole `dispatch_action` future before `finish()` ever runs, `ServingWriteGuard`'s `Drop` implementation still spawns a best-effort background release of the same lease, so a timed-out `call_webhook` step does not durably strand the community write fence."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:754-770"
      - "crates/buzz-deletion/src/lib.rs:131-157"
  - statement: "The already-merged `architecture-flows-workflow-execution` node documents the whole workflow-execution flow (all three trigger paths and the shared executor) at a coarser grain, including a summary-level mention of `call_webhook`'s SSRF guard; this node is the atomic, action-level detail beneath it, not a duplicate of its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "Corrected during Feature #613's whole-branch review, after all ~70 sibling nodes existed side by side: this node's own reasoning had already identified `architecture/flows/*` → `type: architecture` as the only directly relevant merged precedent, then chose `type: capabilities` anyway by extending directory placement rather than content shape. This node's body (trigger/preconditions/ordered-interactions/failure-rollback, per issue #836's own DoD) is that same flow shape, and true siblings send-dm-action, send-message-action and needs-action already carry `type: architecture` for it. `type: architecture` is the consistent answer."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
      - "launchpad/docs/corpus/capabilities/workflows/send-dm-action.md"
    confidence: 0.8
  - statement: "Issue #836 (this task) requires the document to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify auth/authorization/trust-boundary crossings, and document failure/abort/rollback behavior with links to representative verification."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#836 definition of done"
  - statement: "Sibling task #837 (not opened for its full content beyond the title/DoD, which is publicly viewable) targets `launchpad/docs/corpus/capabilities/workflows/webhook-trigger.md` and covers the *inbound* direction — the relay receiving an HTTP webhook that starts a workflow run — the opposite direction from this node's *outbound* `call_webhook` action."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#837 title and definition of done, and this task's own dispatch instructions distinguishing #836 from #837"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: part-of
    target: architecture-flows-workflow-execution
---

# Webhook action (`call_webhook`)

The `call_webhook` action lets a workflow step make an outbound HTTP request to
an operator-supplied URL — the one action in `buzz-workflow` capable of sending
channel-derived data to an arbitrary external destination. This node documents
that one action step's own trigger, preconditions, ordered execution, trust
boundaries and failure behavior. It is the *outbound* direction; the *inbound*
direction — an external caller's `POST /hooks/{id}` request starting a workflow
run — is sibling task #837's `webhook-trigger.md`, not this node.

**Scope.** This node covers `ActionDef::CallWebhook`'s shape
(`crates/buzz-workflow/src/schema.rs`), the elevated-authority precondition it
triggers (`WorkflowDef::requires_elevated_authority`,
`WorkflowEngine::check_owner_authority`), and its dispatch and SSRF-guarded HTTP
execution (`crates/buzz-workflow/src/executor.rs`'s `dispatch_action` `CallWebhook`
arm and `call_webhook_impl`). It does not re-describe the workflow-execution flow
as a whole (all three trigger paths, the shared step loop's condition/template
resolution, the other four action types) — that is
`architecture-flows-workflow-execution`'s territory, which this node is
`part-of`. It does not cover the inbound webhook trigger — that is #837.

## A note on `type`

`capabilities` is chosen here as an explicit `INFERENCE`, not a restatement of an
established rule: `node.schema.json`'s type enum names no surface specific to one
workflow-engine action step, and the only merged directory-to-`type` precedent in
this corpus (`architecture/flows/*` → `type: architecture`) was set for a
different directory than the one this task's own corpus-plan assigned
(`capabilities/workflows/`). See the evidence ledger for the full reasoning and
its 0.65 confidence. If a corpus-standards task later settles this directory's
`type` differently, this node's front matter should follow that decision rather
than this one's own inference.

## Trigger, preconditions, termination/outcome

**Trigger.** A `call_webhook` step is dispatched when `execute_steps` reaches it
in step order, its optional `if:` condition (if present) evaluates true, and its
template placeholders (`{{trigger.X}}`, `{{steps.ID.output.X}}`) resolve
successfully — the same shared pre-dispatch sequence every action type goes
through, documented in full by `architecture-flows-workflow-execution.md`'s own
*Ordered interactions* section. `dispatch_action`'s `CallWebhook` match arm is
the entry point specific to this action (`crates/buzz-workflow/src/executor.rs:682-711`).

**Preconditions, specific to this action:**

1. **Elevated owner authority.** Any workflow definition containing a
   `call_webhook` step is flagged by `WorkflowDef::requires_elevated_authority`
   (`crates/buzz-workflow/src/schema.rs:157-169`). `check_owner_authority`
   re-derives the owner's *current* channel role and denies the run unless that
   role is `owner` or `admin` (`crates/buzz-workflow/src/lib.rs:138-171,
   1018-1035`) — re-checked immediately before every run-creation door, not
   trusted from the time the workflow was saved.
2. **Community write fence.** `dispatch_action` acquires and verifies a durable
   community write fence before touching any action, because the executor
   instance can outlive the request that spawned it
   (`crates/buzz-workflow/src/executor.rs:537-566`).
3. **No URL-scheme or reachability precondition.** `WorkflowDef::validate()` — the
   full precondition gate every definition must pass to be saved or run — does
   not check the `call_webhook` URL's scheme, host, or reachability at all
   (`crates/buzz-workflow/src/schema.rs:173-278`). The schema field's own doc
   comment describes the URL as needing to be "a public HTTPS endpoint," but
   nothing enforces the HTTPS part; only the runtime SSRF check (below) narrows
   which *hosts* are reachable, independent of scheme.

**Termination/outcome.** On success, dispatch returns
`StepResult::Completed({"status": <u16>, "body": <string>})`
(`crates/buzz-workflow/src/executor.rs:862-950`), which `execute_steps` records
into a `"completed"` trace entry and `step_outputs`, addressable by later steps
as `steps.<id>.output.status` / `.body`. On failure, the step aborts the run
(`execute_steps` returns `Err`) with one of two possible stable error codes —
`webhook_failed` (`WorkflowError::WebhookError`, e.g. invalid URL, DNS/SSRF
rejection, connection/response error, or the 1 MiB response cap) or
`step_timeout` (`WorkflowError::StepTimeout`, if the step's own timeout or the
300-second engine default elapses first) — via `WorkflowError::code()`
(`crates/buzz-workflow/src/error.rs:68-82`). `finalize_run` maps either outcome
into the run's persisted `RunStatus`/`error_code`, the same mapping
`architecture-flows-workflow-execution.md` documents for every action type.

## Ordered interactions and data/state movement

1. `execute_steps` evaluates the step's `if:` condition and resolves its
   `{{trigger.X}}`/`{{steps.ID.output.X}}` template placeholders in `url`,
   `headers`, and `body` before dispatch (shared pre-dispatch sequence, not
   specific to `call_webhook`).
2. `dispatch_action` acquires and verifies the community write fence
   (`crates/buzz-workflow/src/executor.rs:537-566`), then runs the rest of this
   sequence inside `ServingWriteGuard::protect`
   (`crates/buzz-deletion/src/lib.rs:66-105`).
3. The `CallWebhook` arm logs the resolved method/URL and — because
   `buzz-relay` compiles `buzz-workflow` with its `reqwest` feature enabled
   (`crates/buzz-relay/Cargo.toml:65`) — calls `call_webhook_impl`
   (`crates/buzz-workflow/src/executor.rs:682-711`).
4. `call_webhook_impl` parses the URL and extracts host/port, then calls
   `check_ssrf(host, port)`: the host is resolved via the OS resolver on a
   blocking threadpool, and any resolved address that `buzz_core::network::is_private_ip`
   flags as private/reserved (RFC1918, loopback, link-local, CGNAT,
   benchmarking, and the IPv6 equivalents/embedded-IPv4 cases) is rejected
   before any request is sent (`crates/buzz-workflow/src/executor.rs:817-855`;
   `crates/buzz-core/src/network.rs:46-95`).
5. A per-call `reqwest::Client` is built pinned to the validated IP via
   `.resolve(host, ...)`, with the system proxy disabled, HTTP redirects
   disabled, and a 10-second timeout — then the resolved method, headers and
   body are sent (`crates/buzz-workflow/src/executor.rs:862-950`).
6. The response is read incrementally, chunk by chunk, aborting with
   `WebhookError` the instant accumulated bytes exceed the 1 MiB
   `WEBHOOK_MAX_RESPONSE_BYTES` cap rather than buffering the full body first
   (`crates/buzz-workflow/src/executor.rs:862-950,859`).
7. On success, `{"status", "body"}` becomes the step's JSON output, entering
   `step_outputs` for later steps to read; `dispatch_action` then calls
   `serving_write.finish()` to release the community write fence
   (`crates/buzz-workflow/src/executor.rs:754-770`).

## Trust-boundary crossings

- **Owner authority (SEC-006), fail-closed.** A `call_webhook`-containing
  definition additionally requires the owner/admin role, re-checked at fire
  time from the owner's *current* standing authority, not from save time; any
  authority-lookup error denies rather than passing through
  (`crates/buzz-workflow/src/lib.rs:138-171, 1018-1035`).
- **Community write fence.** The fence is re-verified immediately before this
  external side effect specifically because the executor can outlive the
  request that spawned it; a stale or lost fence denies the call rather than
  letting it proceed under an expired write lease
  (`crates/buzz-workflow/src/executor.rs:537-566`;
  `crates/buzz-deletion/src/lib.rs:66-105`).
- **Outbound SSRF, the crossing this action exists to guard.** This is the one
  action that sends a request to an operator-supplied external URL, which can
  carry channel-derived content (via template resolution) to that destination.
  The host is DNS-resolved and validated against a private/reserved-address
  denylist before the request is made; the HTTP client is pinned to that
  already-validated IP (defeating a DNS-rebinding TOCTOU against a second,
  unpinned resolution inside the client); the system proxy and HTTP redirects
  are both disabled; and the response body is capped at 1 MiB, read
  incrementally (`crates/buzz-workflow/src/executor.rs:817-855, 862-950`;
  `crates/buzz-core/src/network.rs:46-95`).
- **No scheme boundary.** Despite the field's own doc comment describing the
  URL as needing to be "a public HTTPS endpoint," nothing in `validate()` or
  `call_webhook_impl` rejects a plain `http://` URL to a public host — the only
  enforced boundary is the destination *address*, not the transport's
  confidentiality/integrity guarantees (`crates/buzz-workflow/src/schema.rs:173-278`).

## Failure, abort, rollback behavior

- **Two distinct stable failure codes.** `webhook_failed` covers invalid URL,
  DNS/SSRF rejection, connection/response errors, and the 1 MiB response-size
  cap; `step_timeout` covers the step's own timeout or the 300-second engine
  default elapsing before the call (including its own internal 10-second
  request timeout) completes
  (`crates/buzz-workflow/src/error.rs:68-82`;
  `crates/buzz-workflow/src/executor.rs:1164, 1217-1255`).
- **No compensating action.** Neither `dispatch_action` nor `execute_steps`
  attempts to undo or retry a `call_webhook` call that already reached the
  external server before failing later (e.g. a slow response that then exceeds
  the size cap) — the same no-rollback behavior
  `architecture-flows-workflow-execution.md` documents for every action type in
  this engine.
- **Release errors are swallowed on the failure path.** `dispatch_action` calls
  `serving_write.finish()` after the action completes, whether it succeeded or
  failed. On the success path, a `finish()` error is propagated to the caller.
  On the failure path, `finish()`'s own result is explicitly discarded
  (`let _ = release;`) so the original action error — not a masked
  lease-release error — is what the caller sees
  (`crates/buzz-workflow/src/executor.rs:754-770`).
- **A step-timeout cancellation still releases the fence.** If the surrounding
  `tokio::time::timeout` in `execute_steps` elapses first, the entire
  `dispatch_action` future — including any in-flight `call_webhook_impl` HTTP
  call — is dropped before `serving_write.finish()` can run. `ServingWriteGuard`'s
  `Drop` implementation spawns a best-effort background release of the same
  lease in that case, so a timed-out `call_webhook` step does not durably
  strand the community write fence (`crates/buzz-deletion/src/lib.rs:131-157`).
- **A lease-heartbeat loss aborts mid-call, independent of the step timeout.**
  `ServingWriteGuard::protect` races the wrapped operation against its own
  lease-heartbeat-lost signal; losing the heartbeat while a `call_webhook`
  request is in flight drops that request and returns `ServingWriteLeaseLost`,
  a second, independent abort path from the step timeout above
  (`crates/buzz-deletion/src/lib.rs:66-105`).
- **Representative verification:**
  - `owner_authority_requires_elevated_role_for_exfiltration_definitions` and
    `requires_elevated_authority_detects_call_webhook`
    (`crates/buzz-workflow/src/lib.rs:1862-1867, 1869-1887`) — the
    elevated-authority precondition claims above.
  - `is_private_ip`'s dedicated unit-test module, e.g. `test_loopback_v4` and
    `test_private_10` (`crates/buzz-core/src/network.rs:102-109`) — the SSRF
    address-filtering claim, though only at the address-classification level;
    see *Scope and omissions* for what this does not verify.

## Scope and omissions

**This node covers** the `call_webhook` action's own shape, its
elevated-authority precondition, its SSRF-guarded HTTP execution, the trust
boundaries it crosses, and its distinct failure/timeout/fence-release behavior.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The workflow-execution flow as a whole (all three trigger paths, the shared step loop's condition/template-resolution mechanics, the other four action types) | `architecture-flows-workflow-execution` |
| The inbound webhook *trigger* path (`POST /hooks/{id}` starting a run) | task #837, `capabilities/workflows/webhook-trigger.md` |
| The workflow *definition* save/authoring path's own authority checks (as opposed to the run-time recheck this node covers) | not yet a corpus node at the time of writing |
| Whether any operator-facing documentation states the "HTTPS-only" expectation more strongly than the code enforces, or whether that gap is an intended product change | not investigated here — this node states the current code behavior only, per its own out-of-scope boundary against changing runtime product behavior |

**Expected but not verified when this node was written:**

- **No dedicated unit or integration test for `check_ssrf` or `call_webhook_impl`
  themselves was found.** `is_private_ip`'s own unit tests verify the address
  classification `check_ssrf` depends on, but no test in this repository was
  located that exercises DNS-rebinding pinning, proxy/redirect disabling, or
  the 1 MiB response cap end to end against a real or mocked HTTP server —
  those specific integration behaviors are verified by direct code reading
  only, not by a passing test this node can cite.
- **Whether the field doc comment's "must be a public HTTPS endpoint" reflects
  an intended-but-unimplemented validation, or stale documentation for a
  deliberately address-only guard, was not determined** — no linked decision,
  issue, or commit message explaining the comment's origin was found while
  drafting this node.
- **Whether `dispatch_action`'s discarded-release-error-on-action-failure
  path** (`let _ = release;`, `crates/buzz-workflow/src/executor.rs:754-770`)
  **can leave a lease in a state requiring the `ServingWriteGuard`'s `Drop`
  fallback to clean up in practice** — both code paths were read and both
  release the lease, but no test exercising a `call_webhook` failure followed
  by an assertion on lease state was found.

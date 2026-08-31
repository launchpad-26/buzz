# Plan: issue #1285 — platforms/relay/workflow-api

## ALREADY TRUE

- Issue #1285 (parent Feature #614) asks for exactly one hand-authored corpus
  node at `launchpad/docs/corpus/platforms/relay/workflow-api.md`, documenting
  the relay's workflow webhook HTTP API.
- `launchpad/docs/corpus/platforms/relay/workflow-api.md` does not exist yet;
  no `platforms/` directory exists at all in `origin/launchpad`'s corpus tree.
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md` already
  exists (status: draft) and documents all three workflow trigger paths
  end-to-end, including the webhook path's request handling, tenant binding,
  secret auth, authority recheck, and response shape, with citations into
  `crates/buzz-relay/src/api/bridge.rs` and `crates/buzz-workflow/`. Per
  finding #5, this node must be `references`d rather than duplicated.
- `launchpad/docs/corpus/templates/component.md` is the closest-fitting
  template (responsibility / public interface / dependencies / boundary /
  relationships / scope-and-omissions shape); per finding #4, sibling
  `platforms/**` nodes use `type: platforms` instead of the template's own
  `type: implementation` suggestion.
- The webhook API's real source is `crates/buzz-relay/src/router.rs:132`
  (route registration), `crates/buzz-relay/src/api/bridge.rs:1990-2175`
  (`WebhookQuery`, `workflow_webhook` handler), and
  `crates/buzz-relay/src/webhook_secret.rs` (secret generation/verification).
  Save-time secret provisioning lives in
  `crates/buzz-relay/src/handlers/command_executor.rs:697-812`.
- Repository revision for this node: `46eb901e5aa928aa147fdaef9a509b636218653f`.

## STEP 1 — Confirm no direct route-level test exists, to scope evidence honestly

Searched `crates/buzz-test-client/` and `crates/buzz-relay/` for a test that
actually issues an HTTP request against `/hooks/{id}`. Found none — the only
hit is a doc-comment enumerating the relay's full route list in
`conformance_multitenant.rs`, and that suite's own webhook-trigger workflow
fires via the `kind:46020` command door, explicitly not the webhook door.
`webhook_secret.rs`'s unit tests cover the secret generate/inject/extract/
verify primitives only. This gap is recorded as "expected but not verified."

## STEP 2 — Draft the node body

Structure (component.md shape, `type: platforms`):
1. Purpose/scope paragraph naming the endpoint.
2. Responsibility — what the webhook API is for, cited to the route
   registration comment and the handler's own doc comment.
3. Public interface — request (method, path, headers, query param, body),
   response (202 success envelope; 400/401/404/500 error envelope), cited to
   `bridge.rs` line spans.
4. Dependencies — depends on `buzz-workflow` (`executor::execute_from_step`,
   `finalize_run`), `webhook_secret` module, `buzz_db::workflow`; depended on
   by nothing else (it is the outermost HTTP entry point).
5. Boundary — explicitly excludes internal execution semantics (owned by
   `architecture-flows-workflow-execution`), definition authoring/validation,
   and the `call_webhook` outbound action.
6. Relationships — `references: architecture-flows-workflow-execution`.
7. Scope and omissions, including the untested-route gap from Step 1.

## STEP 3 — Write front matter and evidence ledger

One FACT per substantive claim, each citing an opened file; one commit FACT
for provenance. No INFERENCE expected (the endpoint's behavior is directly
readable), but any reasoning step will be marked INFERENCE with confidence.

## STEP 4 — Validate no new corpus FAILs

Run `validate.py` with the new file present, then with it stashed, and diff
the FAIL sets per the task's known-findings gate.

## STEP 5 — Earn the commit gate and stop

Run the corpus unittest suite as the sole content of one Bash call, then
`git add` + `git commit -s` as the sole content of the next. No push, no PR.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` introduces zero
  new FAIL lines versus the same run with the new file removed.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- Every DoD bullet in #1285 satisfied; every evidence citation opened and read.

## OPEN

- Whether a future integration test will exercise `POST /hooks/{id}` directly
  is unresolved upstream; not this task's scope to add.

## LEFT OUT

- Re-documenting workflow execution internals (trigger matching, step
  execution, SSRF guarding for `call_webhook`) — already owned by
  `architecture-flows-workflow-execution`.
- Workflow definition authoring/validation (`kind:30620` save path) beyond
  the one fact needed to explain where the webhook secret comes from.
- Any change to runtime behavior.

# Plan: issue #843 — document capabilities/workflows/workflow-trigger.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/workflow-trigger.md` does not exist yet (confirmed).
- `launchpad/docs/corpus/architecture/flows/workflow-execution.md` (id
  `architecture-flows-workflow-execution`, `type: architecture`) already exists on
  `origin/launchpad` and documents the *full* run lifecycle across all three trigger
  paths: channel-event (`on_event`), cron (`run()`), webhook (`workflow_webhook`),
  plus the shared step executor, trust boundaries, and failure/rollback. It already
  states the `TriggerDef` enum maps 1:1 onto the three code paths.
- No sibling trigger-type docs (`message-trigger.md`, `reaction-trigger.md`,
  `schedule-trigger.md`, `webhook-trigger.md` — issues #829/#831/#832/#837) exist in
  the corpus tree yet, so no relationship can target them.
- `TriggerDef` (5 variants: `MessagePosted`, `ReactionAdded`, `DiffPosted`,
  `Schedule`, `Webhook`) lives in `crates/buzz-workflow/src/schema.rs:38-71`.
- The corpus's `capability.md` template explicitly excludes "the step-by-step path
  one interaction through a capability takes" from `type: capabilities`, naming that
  flow's territory; the `flow.md` template states flow-shaped instance nodes carry
  `type: architecture`. Issue #843's own DoD bullets (trigger/preconditions/
  termination; ordered interactions/data movement; auth/trust-boundary crossings;
  failure/abort/rollback) are the flow template's four required sections, and match
  `architecture-flows-workflow-execution.md`'s own section headings verbatim.

## STEP 1 — Scope the node to the trigger *abstraction*, not the full run

Atomicity requires this node not duplicate `architecture-flows-workflow-execution`'s
already-thorough coverage. Scope: the `TriggerDef` enum as the umbrella type, the
three engine entry points that each independently decide whether a definition's
trigger fires (`on_event`'s `trigger_matches_event` + `should_fire_workflow`;
`run()`'s direct `TriggerDef::Schedule` pattern match; `workflow_webhook`'s
`matches!(.., TriggerDef::Webhook)` gate), and the trigger-shaped preconditions in
`WorkflowDef::validate()` (Schedule's cron/interval XOR rule, `reply_in_thread`
requiring a message-based trigger). Explicitly boundary out the shared step executor,
full trust-boundary/failure narrative (owned by the existing flow node, `references`d
not restated), and each variant's own full semantics (owned by unmerged siblings).

Done when: a body outline exists naming what's in vs. deferred, before any front
matter is written.

## STEP 2 — Choose `type`, with the choice recorded as an explicit INFERENCE

Directory placement (`capabilities/workflows/`) does not dictate schema `type`; the
task brief says pick based on DoD shape. Since the DoD bullets are the flow
template's own four sections, and the flow template's own precedent sets
`type: architecture` for flow-shaped instances (never `capabilities`, which its own
boundary section defers this exact content to flow), the node will carry
`type: architecture`. Record this reasoning as an `INFERENCE` evidence entry citing
`node.schema.json`'s enum, the flow/capability templates' boundary text, and
`architecture-flows-workflow-execution.md`'s own `type: architecture` precedent.

Done when: the INFERENCE entry is drafted with a confidence value.

## STEP 3 — Draft the node

Front matter: `id: capabilities-workflows-workflow-trigger`, `type: architecture`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
evidence ledger (commit citation + one FACT per substantive claim, each opened and
cited `path:line`/`path:start-end`), one `relationships: references` entry to
`architecture-flows-workflow-execution` (resolves in `origin/launchpad`'s corpus
tree — confirmed present). Body sections mirror the DoD: trigger/preconditions/
termination (per-variant fire conditions + `validate()` preconditions), ordered
interactions (the three dispatch call sites, each independent), trust-boundary
statement (explicitly deferred to the flow node — trigger *matching* itself crosses
no additional boundary beyond what SEC-006/webhook-secret already cover downstream),
failure/abort behavior local to trigger evaluation (filter-eval error = skip, not
abort; parse failure = skip), and a Scope-and-omissions table.

Done when: `launchpad/docs/corpus/capabilities/workflows/workflow-trigger.md` exists
and every DoD bullet in #843 maps to a body section.

## STEP 4 — Validate and gate

Run `python3 launchpad/project-intelligence/corpus/validate.py`; confirm zero new
FAIL entries beyond the known 21 pre-existing (#1951). Run, as the sole command in
its own call, `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
and confirm `OK`.

Done when: both commands pass with the stated evidence.

## STEP 5 — Commit, self-review, stop

`git add` the new node + this plan file; `git commit -s`. Re-read the diff against
#843's DoD line by line; re-open every cited source; confirm no second canonical
document was created; confirm `review-code`/`review-adjudicate` were not run
(deferred per batch mode). Do not push, do not open a PR.

## PARALLEL

None — single-file task, no independent sub-tasks to parallelize.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0, zero new FAIL
  entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  prints `OK`, run as the sole command in its own tool call.

## BUDGET

Single document, ~15-20 evidence entries, capped at one session. No code changes,
no test-suite changes beyond running the existing corpus test suite as the gate.

## OPEN

- Whether `type: architecture` vs `type: capabilities` will later need reconciling
  once #605's per-type standards land (per AGENTS.md, this is unsettled batch-wide,
  not just for this node) — flagged in the node's own INFERENCE entry, not resolved
  here.

## LEFT OUT

- No relationship to sibling trigger-type docs (#829/#831/#832/#837) — none are
  merged to `origin/launchpad` yet.
- No changes to `crates/buzz-workflow` or any other source — documentation only.

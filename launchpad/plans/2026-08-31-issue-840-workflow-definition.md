# Issue #840: document capabilities/workflows/workflow-definition.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/workflows/` does not exist on
  `origin/launchpad` — no sibling node (workflow, workflow-run, workflow-step,
  workflow-trigger) is merged yet, so no precedent exists for `type` and no
  relationship target under `capabilities/` exists to link to.
- `launchpad/docs/corpus/templates/capability.md` is merged and states
  `type: capabilities` is the dedicated PRD #602 surface for capability nodes,
  with required sections: capability statement, maturity, boundary,
  relationships, scope and omissions.
- `crates/buzz-workflow/src/schema.rs` defines `WorkflowDef` (name,
  description, trigger, steps, enabled), `TriggerDef` (5 variants),
  `ActionDef` (7 variants), `Step`, `validate()`, and `parse_yaml()` — the
  full YAML-authored, JSON-canonicalized definition shape this node
  documents.
- `crates/buzz-core/src/kind.rs:442` defines `KIND_WORKFLOW_DEF = 30620`, a
  NIP-33 parameterized-replaceable kind; `crates/buzz-relay/src/handlers/
  command_executor.rs`'s `handle_workflow_def` is the live handler wired to
  it (`command_executor.rs:69`).
- `architecture-flows-workflow-execution` is a merged corpus node id on
  `origin/launchpad` that already documents the runtime execution flow and
  cites the same `schema.rs` — a valid `references` relationship target.
- `VISION_PROJECTS.md:250` marks "Workflow engine (triggers, traces,
  conditional logic)" as "Ships today" — usable maturity evidence.
- A discrepancy exists between `command_executor.rs`'s `handle_workflow_def`
  (requires and errors on a missing `d` tag) and an `#[ignore]`d integration
  test's own comments in `crates/buzz-test-client/tests/
  conformance_multitenant.rs` (claims the server generates the workflow id
  and no `d` tag is used). The ignored test is not exercised in CI, so it is
  not "passing test" evidence under AGENTS.md's precedence rule; the node
  will state the code's current behavior as FACT and name the ignored test's
  contradictory comment as an unresolved gap, not silently pick a side as if
  no conflict existed.

## STEP 1 — Hand-author front matter

`type: capabilities` (directory precedent: `architecture/**` nodes already
use `type: architecture`; no sibling under `capabilities/workflows/` exists
yet, so this is an explicit INFERENCE documented in the node body, not a
copied precedent). `status: draft`, `origin: launchpad`, `audiences: [agent,
developer, reviewer]`. One evidence entry per substantive claim below,
classified FACT (opened source) or TEAM_KNOWLEDGE (issue-only). No
`relationships` except `references: architecture-flows-workflow-execution`
(id confirmed present on `origin/launchpad`).

Done when: front matter validates against `node.schema.json` in isolation
(no schema errors from `validate.py`).

## STEP 2 — Write the body per the capability template's required sections

Capability statement (what a workflow author can declare), Maturity (cite
`VISION_PROJECTS.md:250`), Boundary (not the run/step/trigger siblings, not
the execution flow, not the engine capability as a whole), behavioral rules
(trigger variants, action variants, `validate()`'s invariants, SEC-006
elevated-authority gate), Relationships, Scope and omissions (including the
ignored-test discrepancy as "expected but not verified").

Done when: every DoD bullet in issue #840 is addressed by a named section.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Confirm exit 0 and zero *new* FAIL entries beyond the 21
pre-existing ones tracked by issue #1951.

Done when: validator output confirms this.

## STEP 4 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Only then stage and commit with `git commit -s`.

Done when: `OK` printed, commit created.

## STEP 5 — Self-review

Re-read the diff against #840's DoD line by line; re-open every cited
source; confirm no second canonical document was created; confirm the
validator shows zero new FAIL entries.

Done when: all four checks pass.

## PARALLEL

None — single file, single task.

## GATES

- `validate.py` exit 0, zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.

## BUDGET

One file (`capabilities/workflows/workflow-definition.md`) + this plan file.

## OPEN

- Whether `command_executor.rs`'s `d`-tag requirement or the ignored test's
  server-generated-id comment reflects intended behavior is left to a human;
  this node states the code's current behavior and flags the ignored test's
  claim as unverified drift rather than resolving it.

## LEFT OUT

- No changes to `command_executor.rs`, `schema.rs`, or the ignored test —
  investigating/fixing that discrepancy is out of scope for a documentation
  task and would be a second, unrelated change.
- No `workflow`, `workflow-run`, `workflow-step`, `workflow-trigger` nodes
  (siblings #844, #841, #842, #843) — each is its own task.

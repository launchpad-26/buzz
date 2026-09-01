---
id: capabilities-workflows-workflow-condition
type: capabilities
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
  - statement: "Conditional logic is one evalexpr-based evaluation mechanism (evaluate_condition, built on build_eval_context) reused at two independent gate points: a step's optional `if:` expression, evaluated in the sequential step loop, and a trigger's optional `filter` expression, evaluated before a run is even created."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:363-398"
      - "crates/buzz-workflow/src/schema.rs:75-90"
      - "crates/buzz-workflow/src/lib.rs:883-931"
  - statement: "A step's `if:` field (schema field name `if`, Rust field `if_expr`) is an optional evalexpr expression; when present it is evaluated first in the step loop, before template resolution or action dispatch, against the trigger context and the outputs of steps executed so far in the same run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:73-90"
      - "crates/buzz-workflow/src/executor.rs:1176-1204"
  - statement: "A trigger's optional `filter` expression exists on the MessagePosted, ReactionAdded and DiffPosted trigger variants (not Schedule or Webhook), and is evaluated once per candidate event, before any workflow run is created, against the trigger context only — no step outputs exist yet at that point, so `steps_*` variables are never available to a trigger filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:36-71"
      - "crates/buzz-workflow/src/lib.rs:883-931"
  - statement: "Both gate points build their evalexpr context through the same function, build_eval_context, which exposes six trigger fields as string variables named `trigger_text`, `trigger_author`, `trigger_channel_id`, `trigger_timestamp`, `trigger_emoji` and `trigger_message_id`, plus a seventh boolean variable `trigger_is_reply`; a webhook trigger's arbitrary request-body fields are additionally exposed as `trigger_<key>`, but any body key that would collide with the `trigger_` or `steps_` prefix is silently skipped so a webhook payload cannot spoof a standard trigger field."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:207-328"
  - statement: "A prior step's JSON output is exposed to a condition as `steps_<step_id>_output_<field>` — one evalexpr variable per top-level JSON object field, converted from serde_json::Value to evalexpr::Value (string/bool/int/float; non-scalar values fall back to their JSON string form) — the identical variable-naming scheme condition expressions and `{{steps.ID.output.X}}` templates both use, just with dots replaced by underscores because evalexpr identifiers cannot contain dots."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:207-328"
  - statement: "build_eval_context registers four custom functions that evalexpr v11 does not ship by default: str_contains(haystack, needle), str_starts_with(s, prefix), str_ends_with(s, suffix) and str_len(s) (returning an int) — without these, condition expressions would be limited to evalexpr's own built-in comparison and boolean operators."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:233-280"
  - statement: "A condition expression must evaluate to a boolean (evalexpr::eval_boolean_with_context) — a syntactically valid expression that evaluates to a non-boolean value is a condition-evaluation error, not a value the engine coerces."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:363-398"
  - statement: "Two limits bound every condition evaluation regardless of call site: the expression string is capped at 4096 bytes (rejected before evaluation begins, to bound worst-case exponential evaluation paths), and the evaluation itself runs on a spawn_blocking thread under a 100-millisecond tokio::time::timeout — with the engine's own comment noting that spawn_blocking cannot be cancelled by that timeout, so a pathological expression that exceeds it keeps running to completion on its own thread even though the caller already receives a timeout error."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:350-381"
  - statement: "The two gate points diverge on what a condition-evaluation error does to the run: a step's `if:` error aborts the entire workflow run (returned as WorkflowError::ConditionError, captured with the partial execution trace up to that point), while a trigger's `filter` error is logged and treated as a non-match — only that one candidate workflow is skipped, and no run is ever created for it, so the error never surfaces as a failed run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1176-1204"
      - "crates/buzz-workflow/src/lib.rs:904-928"
  - statement: "A step whose `if:` evaluates false is skipped rather than failed: the step loop records a `\"skipped\"` execution-trace entry for it and moves to the next step without resolving its templates, dispatching its action, or consuming its configured timeout."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1176-1204"
  - statement: "Representative unit tests in crates/buzz-workflow/src/executor.rs exercise str_contains/str_starts_with/str_ends_with/str_len, and/or/not boolean composition, step-output field comparison across bool/string/integer types, literal true/false expressions, rejection of a syntactically invalid expression (ConditionError), and rejection of an expression exceeding the 4096-byte limit (ConditionError) — covering both the custom-function surface and the two documented safety limits."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "VISION_PROJECTS.md's own capability status table lists 'Workflow engine (triggers, traces, conditional logic)' as 'Ships today', naming conditional logic as part of an already-shipped capability rather than a designed or in-progress one."
    entry_class: FACT
    evidence:
      - "VISION_PROJECTS.md:250"
  - statement: "architecture-flows-workflow-execution (merged on origin/launchpad) already documents the shared step loop's overall lifecycle, including a brief mention that the `if:` expression is evaluated first each step iteration, at the level of the whole run's trigger/preconditions/termination and trust-boundary crossings — not the condition mechanism's own contract of variables, functions, limits and the failure-handling divergence between its two call sites, which is this node's own subject."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "This node carries `type: capabilities` rather than `type: architecture`, chosen because no merged sibling node exists yet under capabilities/workflows/ to establish an in-Feature precedent (issues #829 and #831, this batch's message-trigger and reaction-trigger tasks, are both still open and unmerged at the recorded revision) — the choice instead follows `templates/capability.md`'s own guidance that a capability node names something the product can do at the level VISION_PROJECTS.md's status table already states it (here, the 'conditional logic' clause of the 'Workflow engine' row), while `architecture-flows-workflow-execution` already owns the *how* (the executor's control flow) at `type: architecture`."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/capability.md"
      - "VISION_PROJECTS.md:250"
    confidence: 0.75
  - statement: "Issue #839's own Definition of Done requires stating the capability and primary actors/outcomes, defining behavioral rules/constraints/variants, linking major flows/interfaces/data/platform implementation, and linking verification demonstrating the capability — which is why this node is organized around a capability statement, a rules/variables/limits section, a link to the architecture flow node, and a verification section rather than a general prose narrative."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#839 definition of done"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: references
    target: architecture-flows-workflow-execution
---

# Workflow condition: capability

A Buzz workflow can gate a step, or an entire trigger match, behind a boolean
expression written in [evalexpr](https://docs.rs/evalexpr) syntax over the
triggering event and any prior step's output. This lets a workflow author write
one definition that behaves differently depending on message content, reaction
emoji, webhook payload fields, or an earlier step's result — without branching
the workflow into multiple separate definitions.

## Maturity

Shipped. VISION_PROJECTS.md's own capability status table lists "Workflow
engine (triggers, traces, conditional logic)" as "Ships today", and the
mechanism is implemented, tested, and exercised at both of its call sites in
`crates/buzz-workflow`.

## The two call sites

Both use the same underlying mechanism (`executor::evaluate_condition`, built
on `executor::build_eval_context`), but at different points in a workflow's
lifecycle and with different data available:

| | Step `if:` | Trigger `filter` |
|---|---|---|
| Field | `Step.if_expr` (YAML key `if`) | `TriggerDef::{MessagePosted,ReactionAdded,DiffPosted}.filter` |
| When evaluated | Once per step, in run order, before that step's templates resolve or its action dispatches | Once per candidate event, before any run is created |
| Data available | Trigger context **and** every prior step's output (`steps_*` variables) | Trigger context only — no step outputs exist yet |
| Available on | Every step, regardless of the workflow's trigger | `message_posted`, `reaction_added`, `diff_posted` triggers only — `schedule` and `webhook` triggers carry no `filter` field |
| False result | That step is skipped (not failed); a `"skipped"` trace entry is recorded and the run continues with the next step | That one candidate workflow does not fire; no run is created for it |
| Evaluation error | The whole run aborts, returned as `WorkflowError::ConditionError` with the partial trace up to that point | The candidate workflow is treated as a non-match and skipped; no run is created, and the error never becomes a failed run |

## Expression language and available variables

A condition expression is evalexpr syntax and **must evaluate to a boolean** —
a syntactically valid expression that evaluates to a non-boolean value is a
condition-evaluation error, not a value the engine coerces or truthies.

**Trigger fields**, exposed as string variables (one boolean exception):

| Variable | Source |
|---|---|
| `trigger_text` | Message content |
| `trigger_author` | Event author's pubkey (hex) |
| `trigger_channel_id` | Channel UUID |
| `trigger_timestamp` | Unix timestamp of the triggering event |
| `trigger_emoji` | Reaction emoji name |
| `trigger_message_id` | Triggering message's event ID (hex) |
| `trigger_is_reply` | **Boolean** — true when the triggering event carries a NIP-10 reply/root marker |

A webhook trigger's JSON body fields are additionally exposed as
`trigger_<key>` for each top-level key — but any body key that would collide
with the `trigger_` or `steps_` prefix is silently dropped before the standard
trigger fields are set, so a webhook payload can never spoof `trigger_text` or
a step's output.

**Step outputs**, available only to a step's own `if:` (never to a trigger
`filter`): each prior step's completed JSON output is exposed as
`steps_<step_id>_output_<field>`, one variable per top-level JSON field,
converted to the matching evalexpr type (string, bool, int, float; anything
else falls back to its JSON string form). This is the same
`steps.<id>.output.<field>` addressing `{{...}}` templates use, with dots
replaced by underscores because evalexpr identifiers cannot contain dots.

**Custom functions.** evalexpr v11 does not ship string-matching helpers, so
four are registered into every condition context:

- `str_contains(haystack, needle)` → bool
- `str_starts_with(s, prefix)` → bool
- `str_ends_with(s, suffix)` → bool
- `str_len(s)` → int

Standard evalexpr comparison operators (`==`, `!=`, `>`, `>=`, `<`, `<=`) and
boolean operators (`&&`, `||`, `!`) are available on top of these.

## Constraints

Two limits bound every condition evaluation, at either call site, without
exception:

- **4096-byte expression length cap**, enforced before evaluation starts, to
  bound worst-case exponential evaluation paths a long or deeply nested
  expression could otherwise trigger. An expression over the limit is rejected
  as a condition error without being evaluated at all.
- **100-millisecond wall-clock timeout**, via `tokio::time::timeout` around a
  `spawn_blocking` task. The engine's own comment on this timeout is explicit
  that `spawn_blocking` cannot actually be cancelled: a pathological expression
  that runs past 100ms keeps executing to completion on its own blocking
  thread even though the caller has already received a timeout error. The
  length cap exists specifically to make that residual risk small rather than
  to eliminate it.

## Boundary

This node does not describe:
- The trigger types themselves (`message_posted`, `reaction_added`,
  `diff_posted`, `schedule`, `webhook`) — their own matching rules, payload
  shapes and configuration are #829's and #831's subject (message-trigger,
  reaction-trigger), not this node's.
- The overall workflow-run lifecycle (trigger → precondition checks → step
  loop → terminal status) — that is `architecture-flows-workflow-execution`'s
  subject; this node only expands the one step of that lifecycle where a
  condition is evaluated.
- `{{trigger.X}}` / `{{steps.ID.output.X}}` template-variable resolution — a
  separate mechanism (`resolve_template`) that runs *after* a step's
  condition has already passed, not part of condition evaluation itself.

## Relationships

- `references`: `architecture-flows-workflow-execution` — the flow node
  documents the shared executor's full step loop and the three trigger paths
  that feed it; this node expands the condition-evaluation step of that loop
  in detail without re-describing the rest of the lifecycle.

## Scope and omissions

**This node covers** the evalexpr-based condition-evaluation mechanism shared
by a step's `if:` and a trigger's `filter`: what variables and functions are
available at each call site, the two safety limits that bound every
evaluation, and how the two call sites diverge on what a false result and an
evaluation error each do to a run.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The trigger types and their own matching semantics | #829 (message-trigger), #831 (reaction-trigger) |
| The full workflow-run lifecycle and trust-boundary crossings | `architecture-flows-workflow-execution` |
| Template-variable resolution (`{{...}}`) | Not yet a corpus node at the recorded revision |
| Workflow *definition* authoring/validation (the `kind:30620` command, YAML schema) | Not yet a corpus node at the recorded revision |

**Expected but not verified when this node was written:**

- Whether any workflow currently deployed in this repository's own communities
  uses a `filter` or `if:` expression referencing a webhook-sourced
  `trigger_<key>` variable was not checked — this node establishes only that
  the mechanism supports it.
- The `evalexpr` v11 crate's own full operator and built-in-function surface
  beyond the four custom string helpers was not exhaustively enumerated; only
  what `build_eval_context` explicitly registers and what the test suite
  exercises is described here.

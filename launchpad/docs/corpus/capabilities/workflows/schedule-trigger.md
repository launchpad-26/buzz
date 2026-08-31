---
id: capabilities-workflows-schedule-trigger
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "node.schema.json's type enum has no member named flow, schedule, trigger or cron; the merged corpus already has one node narrating the same three workflow trigger paths this node narrows to one (the Schedule path) and that node carries type: architecture, not a capabilities-family value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "This node's own type: architecture extends that precedent to a single-trigger deep dive rather than the capabilities enum member its own directory segment (capabilities/workflows/) might suggest, because AGENTS.md states a node's location under launchpad/docs/corpus is independent of its front-matter type, and this node's body narrates one path's ordered runtime interactions (trigger match, durable claim, run creation) rather than a product-level 'what the product can do' statement of the shape corpus-template-capability's own Required Sections (Capability statement / Maturity / Boundary) call for."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/templates/capability.md"
      - "launchpad/docs/corpus/templates/flow.md"
    confidence: 0.75
  - statement: "Issue #832's own Definition of Done requires this node to state trigger/preconditions/termination, ordered interactions and data/state movement, authentication/authorization/trust-boundary crossings, and failure/abort/rollback behavior with links to representative verification — the same four-part shape architecture-flows-workflow-execution.md already used for its own #688 category, which is why this node is organized the same way."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#832 definition of done"
  - statement: "TriggerDef::Schedule carries two mutually-exclusive optional fields, cron (a UTC cron expression) and interval (a simple duration string like '1h' or '30m')."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:60-68"
  - statement: "WorkflowDef::validate() rejects a Schedule trigger unless exactly one of cron or interval is set, parses a set cron expression through the cron crate (via validate_cron), and rejects an interval below 60 seconds because the background loop that fires it only ticks once a minute."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:244-278"
  - statement: "validate() also rejects, at definition time, a SendMessage step with reply_in_thread: true under a Schedule (or Webhook) trigger, because neither trigger carries a triggering message to reply to."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:216-242"
  - statement: "normalize_cron pads a 5-field cron expression (prepend seconds, append year) and a 6-field expression (append year) to the 7-field sec/min/hour/dom/month/dow/year form the cron crate requires; a 7-field expression passes through unchanged."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:294-306"
  - statement: "WorkflowEngine::run() is a background loop that sleeps 60 seconds, loads every enabled workflow across all communities via list_all_enabled_workflows, and for each one parses its definition, skips it if disabled or if it has no bound channel_id, and otherwise resolves its trigger — non-Schedule triggers are skipped with 'continue' because they are handled by on_event() instead."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:489-599"
  - statement: "For a cron-triggered workflow, cron_fire_instant finds the scheduled instant that fell inside a 60-second window ending at 'now' (schedule.after(now - 60s).next() <= now) instead of testing 'now' directly, so a delayed tick still catches a minute-granularity cron expression; the returned instant is the cron's own scheduled time, not 'now', so every pod evaluating the same expression computes the same value."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:752-785"
  - statement: "For an interval-triggered workflow, interval_fire_instant quantizes 'now' to a deterministic bucket boundary (floor(now / interval) * interval from the Unix epoch), so every pod evaluating the same interval in the same bucket computes the identical claim anchor."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:787-822"
  - statement: "interval_should_fire treats a missing last-fired anchor as 'last = now' (so a freshly-created interval workflow waits a full interval rather than firing immediately); interval_prefilter_should_fire additionally seeds the in-memory anchor to 'now' the first time it suppresses on a None anchor, so a subsequent tick has a real anchor to measure elapsed time against instead of suppressing forever."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:445-461"
      - "crates/buzz-workflow/src/lib.rs:824-876"
  - statement: "On the first tick after a process restart, the interval anchor is seeded from the durable latest_scheduled_workflow_fire read (not the in-memory map, which is lost on restart), and a read failure is treated as a suppressed tick (fail closed) rather than a pass-through; the engine's own field comment states that fires missed entirely during downtime are not replayed, called acceptable for MVP."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:80-86"
      - "crates/buzz-workflow/src/lib.rs:559-583"
  - statement: "Owner channel authority (SEC-006) is rechecked via check_owner_authority immediately before the durable claim, deliberately placed before rather than after it, because the claim is never re-fired once taken: gating after the claim would let a revoked owner's workflow permanently consume that fire slot and deny a legitimate re-enable later."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:601-615"
  - statement: "check_owner_authority looks up the owner's current role via get_member_role, fails closed (denies) on a lookup error rather than passing through, and otherwise defers to owner_authority_allows: no membership denies unconditionally, plain membership is enough for an ordinary definition, and a definition whose steps require elevated authority (e.g. contains call_webhook) needs an owner/admin role."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:148-171"
      - "crates/buzz-workflow/src/lib.rs:1025-1035"
  - statement: "claim_scheduled_workflow_fire performs a single INSERT ... SELECT ... FROM workflows WHERE community_id = $1 AND id = $2 ... ON CONFLICT (community_id, workflow_id, scheduled_for) DO NOTHING RETURNING ..., which both resolves community_id from the workflow row itself (never trusting a client-supplied value) and makes the cross-pod at-most-once claim a single atomic statement rather than a check-then-insert."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:495-533"
  - statement: "scheduled_workflow_fires' primary key is (community_id, workflow_id, scheduled_for) — the exact tuple claim_scheduled_workflow_fire's ON CONFLICT targets — with a foreign key to workflows(community_id, id) ON DELETE CASCADE and a foreign key to workflow_runs(community_id, id) ON DELETE NO ACTION, the latter guarding against a run being deleted out from under a claim that still references it."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:451-462"
  - statement: "latest_scheduled_workflow_fire reads MAX(scheduled_for) from scheduled_workflow_fires (not from workflow_runs), because the claim table, not the run table, is the source of truth for schedule deduplication and therefore for the interval restart anchor."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:535-560"
  - statement: "attach_scheduled_workflow_run links a won claim row to the run id it produced via an UPDATE guarded by WHERE workflow_run_id IS NULL, making a repeated attach a no-op; the function's own doc comment states this link is for ops/audit forensics only, and that the claim row itself (not this link) remains the dedupe boundary."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:562-593"
  - statement: "On the schedule path, create_workflow_run is called with no trigger event (None) and a TriggerContext populated with only channel_id and timestamp — none of the text/author/emoji/message_id fields the channel-event path's TriggerContext carries, because a schedule tick has no originating message."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:649-674"
  - statement: "If run creation fails after a claim was already won, the claim row is left in place with workflow_run_id still NULL rather than being retried or released, deliberately preserving at-most-once firing over exactly-once execution on a transient insert failure."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:676-690"
  - statement: "scheduled_workflow_fires has a community write fence attached via attach_community_write_fence, so claim inserts on it are subject to the same per-community write-fence gate as other community-scoped tables during a community deletion/lease transition."
    entry_class: FACT
    evidence:
      - "migrations/0029_community_deletion.sql:569"
  - statement: "Representative unit tests for the cron/interval fire-instant and liveness claims above: cron_fire_instant_matches_within_window, cron_fire_instant_returns_none_for_invalid_expr, cron_fire_instant_at_exact_minute_boundary and cron_fire_instant_within_drift_window_anchors_on_scheduled_time cover the window-based cron match; interval_fire_instant_quantizes_to_bucket_boundary, interval_should_fire_returns_false_on_first_tick, interval_should_fire_returns_true_after_interval_elapsed and interval_should_fire_at_exact_boundary cover interval bucketing and cold-start liveness."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1054-1146"
      - "crates/buzz-workflow/src/lib.rs:1147-1235"
  - statement: "Representative unit tests for the definition-time Schedule validation claims above: parse_schedule_trigger and parse_schedule_with_interval_instead_of_cron cover parsing; validate_rejects_invalid_cron and validate_rejects_schedule_without_cron_or_interval cover the exactly-one-of-cron-or-interval rule; validate_rejects_reply_in_thread_on_schedule_trigger and validate_allows_reply_in_thread_false_on_schedule cover the reply_in_thread rejection; validate_accepts_valid_5_field_cron/6_field_cron/7_field_cron and the normalize_cron_* tests cover cron-field normalization."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:351-357"
      - "crates/buzz-workflow/src/schema.rs:481-500"
      - "crates/buzz-workflow/src/schema.rs:538-566"
      - "crates/buzz-workflow/src/schema.rs:621-629"
      - "crates/buzz-workflow/src/schema.rs:828-846"
      - "crates/buzz-workflow/src/schema.rs:925-946"
  - statement: "Representative DB-layer tests for the claim table's trust-boundary and concurrency claims above: claim_confined_to_its_community asserts a claim in one community never consumes the same (workflow_id, scheduled_for) instant in a different community sharing that UUID; concurrent_same_window_claims_exactly_one_wins spawns eight concurrent claim attempts for the same tuple and asserts exactly one wins; attach_links_run_to_claim_and_is_idempotent asserts a second attach is a no-op. All three are #[ignore = \"requires Postgres\"] and are not part of the default unit-test run."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/workflow.rs:2272-2321"
      - "crates/buzz-db/src/store/workflow.rs:2328-2357"
      - "crates/buzz-db/src/store/workflow.rs:2367-2400"
relationships:
  - type: part-of
    target: capabilities-workflows-workflow
  - type: part-of
    target: architecture-flows-workflow-execution
---

# Workflow Schedule Trigger

How a `Schedule`-triggered workflow definition (a cron expression or a simple
interval) goes from a 60-second background tick to a created workflow run: what a
definition must satisfy to be eligible, how the engine computes a fire instant
deterministically across relay pods, where the cross-pod at-most-once claim lives,
what authority is re-checked and when, and what happens when a tick, a claim, or a
run-creation call fails.

**Scope.** This node covers only the Schedule trigger path in
`crates/buzz-workflow`'s `WorkflowEngine::run()` background loop and the schema-level
preconditions a `Schedule` definition must satisfy before that loop will ever act on
it. It does not cover the channel-event or webhook trigger paths, and it does not
cover the shared sequential step executor a schedule-created run is handed to once
`create_workflow_run` succeeds — `architecture-flows-workflow-execution` already
documents both, and this node declares `part-of` that node rather than repeating its
content (see *Relationships*).

## Trigger, preconditions, termination

**Trigger.** Every 60 seconds, `WorkflowEngine::run()` wakes, loads every currently
enabled workflow across every community, and for each one whose parsed definition
carries a `Schedule` trigger, computes whether this tick is the moment it should fire
(`crates/buzz-workflow/src/lib.rs:489-599`). A definition with any other trigger kind
is skipped in this loop — it is handled by the channel-event path instead
(`crates/buzz-workflow/src/lib.rs:598`).

**Preconditions, checked in this order:**

1. **The definition must parse and be enabled, and must have a bound channel.** A
   definition that fails to deserialize, is disabled, or has no `channel_id` is
   skipped for this tick with a warning, not retried later
   (`crates/buzz-workflow/src/lib.rs:505-534`).
2. **The `Schedule` trigger must satisfy `WorkflowDef::validate()`'s own rules**,
   enforced once at save time rather than on every tick: exactly one of `cron` or
   `interval` must be set (not both, not neither), a set `cron` expression must parse
   under the `cron` crate after 5/6-field normalization, and a set `interval` must be
   a parseable duration of at least 60 seconds — shorter is rejected outright because
   the loop that would need to observe it only ticks once a minute
   (`crates/buzz-workflow/src/schema.rs:244-278`, `294-306`). A `Schedule` trigger
   also cannot combine with a step's `reply_in_thread: true`, since neither a cron
   tick nor a webhook call carries a message to reply to
   (`crates/buzz-workflow/src/schema.rs:216-242`).
3. **A fire instant must actually be due this tick.** `cron_fire_instant` (for `cron`)
   or `interval_fire_instant` (for `interval`) must return `Some` deterministic
   instant; otherwise the workflow is skipped for this tick with `continue`
   (`crates/buzz-workflow/src/lib.rs:541-599`, `752-822`).
4. **The owner must currently hold sufficient channel authority.** Re-checked fresh on
   every tick, not trusted from when the definition was saved (see *Trust-boundary
   crossings*).
5. **The deterministic instant must still be unclaimed.** The durable
   `(community_id, workflow_id, scheduled_for)` claim must not already exist (see
   *Ordered interactions*).

**Termination / outcome.** A won claim leads to `create_workflow_run` inserting a
`workflow_runs` row (`Pending`, scoped to the workflow's own community), which
`architecture-flows-workflow-execution` documents as the shared entry point every
trigger path hands off to; this node's own scope ends at that hand-off. If run
creation itself fails, the claim row is left standing with `workflow_run_id` still
`NULL` — the tick produces no run, but the fire instant is not retried
(`crates/buzz-workflow/src/lib.rs:676-690`).

## Ordered interactions and data/state movement

1. **Tick.** `run()` sleeps 60 seconds, then calls `list_all_enabled_workflows` across
   all communities (`crates/buzz-workflow/src/lib.rs:489-503`).
2. **Per-workflow trigger resolution.** For a `cron` definition, `cron_fire_instant`
   finds the scheduled time inside a 60-second window ending at `now`
   (`schedule.after(now - 60s).next() <= now`) rather than testing `now` directly, so
   a delayed tick still catches a minute-granularity expression, and every pod
   evaluating the same expression computes the same instant
   (`crates/buzz-workflow/src/lib.rs:752-785`). For an `interval` definition,
   `interval_fire_instant` first quantizes `now` to a deterministic bucket boundary
   (`floor(now / interval) * interval`), and a cheap in-memory prefilter
   (`interval_prefilter_should_fire`) skips the claim attempt entirely when the
   in-memory clock says the interval clearly has not elapsed — seeding a `None`
   anchor to `now` on a cold start so the workflow does not suppress forever
   (`crates/buzz-workflow/src/lib.rs:445-461`, `787-822`, `824-876`). On the first
   tick after a process restart, that in-memory anchor is absent, so the prefilter
   reads the durable `latest_scheduled_workflow_fire` instead — a read failure is
   treated as "suppress this tick," not "fire" (`crates/buzz-workflow/src/lib.rs:559-583`).
3. **Owner authority recheck (SEC-006).** `check_owner_authority` is called *before*
   the durable claim, deliberately: the claim is never re-fired once taken, so
   checking after it would let a revoked owner's workflow consume the slot and
   silently deny a legitimate future re-enable (`crates/buzz-workflow/src/lib.rs:601-615`).
4. **Durable at-most-once claim.** `claim_scheduled_workflow_fire` issues one
   `INSERT ... SELECT ... FROM workflows WHERE community_id = $1 AND id = $2 ...
   ON CONFLICT (community_id, workflow_id, scheduled_for) DO NOTHING RETURNING ...`
   — a single atomic statement, not a check-then-insert, and it re-derives
   `community_id` from the `workflows` row itself rather than trusting a
   caller-supplied value (`crates/buzz-db/src/store/workflow.rs:495-533`). A losing
   pod (or an already-fired instant) gets `Ok(None)` back and moves on without
   creating a run or any side effect (`crates/buzz-workflow/src/lib.rs:629-639`).
5. **Run creation.** On a won claim, a minimal `TriggerContext` is built — only
   `channel_id` and `timestamp`, since a schedule tick has no originating message —
   and passed to `create_workflow_run` with no trigger event
   (`crates/buzz-workflow/src/lib.rs:649-674`).
6. **Best-effort audit link.** `attach_scheduled_workflow_run` updates the claim row
   to point at the new run id, guarded by `WHERE workflow_run_id IS NULL` so a repeat
   call is a no-op; its own doc comment states this link exists for ops/audit
   forensics only — the claim row, not this link, is what enforces dedupe
   (`crates/buzz-db/src/store/workflow.rs:562-593`).
7. **Hand-off.** The run is spawned into the shared executor
   (`crates/buzz-workflow/src/lib.rs:723-730`), which `architecture-flows-workflow-execution`
   documents from this point forward.

## Trust-boundary crossings

- **Owner authority, fail-closed (SEC-006).** `check_owner_authority` looks up the
  owner's *current* role via `get_member_role` and treats a lookup error as a denial,
  never a pass-through. `owner_authority_allows` then applies: no membership denies
  unconditionally; plain membership is enough for an ordinary definition; a
  definition whose steps require elevated authority (for example, one containing a
  `call_webhook` step, which can reach an arbitrary external host) additionally needs
  an `owner`/`admin` role (`crates/buzz-workflow/src/lib.rs:148-171`, `1025-1035`).
  This recheck happens on every tick a fire instant is due, not once at save time, so
  an owner demoted after saving the definition loses the ability to fire it going
  forward without needing the definition itself to change.
- **Tenant confinement of the claim.** The claim's `INSERT ... SELECT ... FROM
  workflows WHERE community_id = $1 AND id = $2` join means a claim can only ever be
  taken against the community that actually owns that workflow row — the same
  workflow UUID reused in a second community claims its own, independent instant
  (`crates/buzz-db/src/store/workflow.rs:495-533`; verified by
  `claim_confined_to_its_community`, `crates/buzz-db/src/store/workflow.rs:2272-2321`).
- **Community write fence.** `scheduled_workflow_fires` carries a community write
  fence via `attach_community_write_fence`, so a claim insert is subject to the same
  per-community write-fence gate as other community-scoped tables during a community
  deletion or lease transition (`migrations/0029_community_deletion.sql:569`). This
  node does not re-verify the fence's own mechanics; see
  `architecture-flows-workflow-execution`'s treatment of `dispatch_action`'s write
  fence for the executor-side half of that boundary.

## Failure, abort, rollback behavior

- **A malformed or disabled definition is skipped silently (with a log), not
  retried.** A definition that fails to deserialize, that is disabled, or that has no
  bound `channel_id` is skipped for the current tick; nothing marks it for retry, so
  it is simply reconsidered on the next 60-second tick
  (`crates/buzz-workflow/src/lib.rs:505-534`).
- **An owner-authority failure skips the tick, not the workflow permanently.** A
  denied authority check logs a warning and skips this tick's fire; because the claim
  is checked *after* authority, no fire slot is consumed, so the workflow can fire on
  a later tick once authority is restored (`crates/buzz-workflow/src/lib.rs:606-615`).
- **A lost claim race produces no error and no duplicate run.** `Ok(None)` from
  `claim_scheduled_workflow_fire` means another pod (or an earlier tick on this pod)
  already claimed the instant; the losing attempt just advances its in-memory
  interval clock (for `interval` triggers only) and moves on
  (`crates/buzz-workflow/src/lib.rs:629-639`; verified by
  `concurrent_same_window_claims_exactly_one_wins`,
  `crates/buzz-db/src/store/workflow.rs:2328-2357`).
- **A failed run-creation call after a won claim is not retried, and the claim is not
  released.** The claim row stays with `workflow_run_id` left `NULL`, deliberately:
  at-most-once firing is preserved over exactly-once execution, so a transient
  `create_workflow_run` failure costs that fire entirely rather than risking a second,
  duplicate run for the same instant on a later tick
  (`crates/buzz-workflow/src/lib.rs:676-690`).
- **The audit link is best-effort and its own failure does not undo the run.** If
  `attach_scheduled_workflow_run` fails after a run was already created, the run
  proceeds; only a warning is logged, because the claim row (not this link) is the
  actual dedupe record (`crates/buzz-workflow/src/lib.rs:694-704`;
  `crates/buzz-db/src/store/workflow.rs:562-593`, idempotence verified by
  `attach_links_run_to_claim_and_is_idempotent`,
  `crates/buzz-db/src/store/workflow.rs:2367-2400`).
- **A missed fire during downtime is not made up.** The in-memory `last_fired` map
  used for the interval prefilter is lost on process restart; the engine's own field
  comment states plainly that fires missed entirely while the process was down are
  not replayed, and calls this acceptable for MVP
  (`crates/buzz-workflow/src/lib.rs:80-86`). The durable claim table only prevents a
  *duplicate* fire across a restart — it does not reconstruct a fire that never
  happened while the process was offline.
- **Everything past run creation is out of this node's scope.** A step-level failure
  once the run enters the shared executor (condition-evaluation error, template
  error, action dispatch failure, timeout) is `architecture-flows-workflow-execution`'s
  own *Failure, abort, rollback behavior* section, not repeated here.

## Relationships

- **part-of**: `architecture-flows-workflow-execution` — this node narrates one of
  the three trigger paths (`Schedule`) that node's own *Trigger, preconditions,
  termination* table already names, going deeper into schedule-specific mechanics
  (cron/interval computation, the claim table, restart liveness) than that node's
  three-way comparison does. `relationships.schema.json` states `part-of`'s
  directionality as "source is a constituent section/child of target," which fits: this
  node is a detailed elaboration of one section of that broader flow, not an
  independent scenario.

## Scope and omissions

**This node covers** the `Schedule` trigger's definition-time preconditions
(`WorkflowDef::validate()`'s cron/interval rules and the `reply_in_thread`
restriction), the 60-second background loop's deterministic fire-instant
computation for both `cron` and `interval` forms, the durable cross-pod
at-most-once claim and its schema, the owner-authority recheck and its ordering
relative to the claim, and the failure/abort behavior at each step up to run
creation.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The channel-event and webhook trigger paths | `architecture-flows-workflow-execution` |
| The shared sequential step executor a schedule-created run is handed to | `architecture-flows-workflow-execution` |
| Workflow *definition* authoring/saving (the `kind:30620` command) beyond the run-time preconditions checked here | not yet drafted as its own node |
| The `call_webhook` action's own SSRF guarding | `architecture-flows-workflow-execution` |
| Retention/pruning of old claim rows (`prune_scheduled_workflow_fires_before`) as an operational concern | the `operations` corpus surface, not yet drafted |

**Expected but not verified when this node was written:**

- **No live Postgres run of the claim-table tests was performed.**
  `claim_confined_to_its_community`, `concurrent_same_window_claims_exactly_one_wins`
  and `attach_links_run_to_claim_and_is_idempotent` are all `#[ignore = "requires
  Postgres"]` and were read as source, not executed, for this node.
- **Behavior when the same relay process runs multiple `WorkflowEngine::run()`
  loops concurrently** (as opposed to multiple separate relay pods) was not traced;
  this node assumes the documented multi-pod claim behavior covers that case
  identically, but did not find a test exercising it directly.
- **Whether `list_all_enabled_workflows` paginates or loads every enabled workflow
  in one query** at deployment scale was not checked beyond reading its call site;
  this node makes no claim about behavior at very large workflow counts.

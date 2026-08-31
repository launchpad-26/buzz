---
id: capabilities-workflows-message-trigger
type: capabilities
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
  - statement: "TriggerDef::MessagePosted is a variant of buzz-workflow's serde-internally-tagged trigger enum (tag `on: message_posted`), carrying one optional field: `filter`, an evalexpr expression string over flat variable names such as `trigger_text`."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:36-44"
  - statement: "trigger_matches_event is the sole kind-matching gate for a channel event reaching a message_posted-triggered workflow: it returns true only when the stored event's kind equals KIND_STREAM_MESSAGE (9), and false for every other kind, including KIND_REACTION (7) and KIND_STREAM_MESSAGE_DIFF (40008); this check runs before any filter is evaluated and does not depend on the filter's presence or content."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1037-1046"
      - "crates/buzz-core/src/kind.rs:474-479"
  - statement: "message_posted_matches_kind_9_only asserts trigger_matches_event(MessagePosted, 9) is true and is false for kind 7 (reaction), 45001 (forum post) and 40002 (stream message v2)."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1437-1448"
  - statement: "message_posted_does_not_match_kind_40008 asserts a message_posted trigger does not match the diff-posted kind (40008) even though both are channel content kinds."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1540-1545"
  - statement: "message_posted_with_filter_still_matches_kind_9 asserts that a non-empty filter string on a MessagePosted trigger has no effect on trigger_matches_event's kind check -- the filter is evaluated separately, later, in should_fire_workflow, not folded into kind matching."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1476-1484"
  - statement: "on_event -- the relay's per-stored-event entry point into the workflow engine -- returns immediately without any workflow lookup for an event carrying no channel_id, before the kind is even read; a message_posted trigger (like every channel-event trigger) is therefore unreachable for any event stored outside a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:320-332"
  - statement: "on_event next excludes any event whose kind falls in the reserved workflow-execution range (46001-46012) via is_workflow_execution_kind, before the per-channel enabled-workflow list is read from a 10-second TTL cache keyed (community_id, channel_id); this exclusion, the cache, and the tenant/community scoping it enforces are shared by all three channel-event triggers and are documented in architecture-flows-workflow-execution, not repeated here."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:334-354"
  - statement: "For each cached workflow, on_event parses its stored JSON definition back into a WorkflowDef (skipping and logging a warning on parse failure), then requires both def.enabled and trigger_matches_event(&def.trigger, kind_u32) before calling should_fire_workflow; only after should_fire_workflow returns true does the loop proceed to the SEC-006 owner-authority recheck and run creation."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:370-385"
  - statement: "should_fire_workflow applies the message_posted trigger's optional filter by matching def.trigger against the shared MessagePosted | ReactionAdded { .. } | DiffPosted arm, extracting `filter.as_ref()`, then -- if a filter string is present -- calling executor::evaluate_condition against the built TriggerContext; Ok(true) proceeds, Ok(false) or Err both return false from should_fire_workflow (logged at debug and warn level respectively), meaning a filter evaluation error skips the workflow exactly like a filter that evaluated to false, rather than failing the run."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:883-931"
  - statement: "reaction_filter_matches_target_message exercises this same should_fire_workflow filter arm (shared verbatim by MessagePosted, ReactionAdded and DiffPosted) end to end via a parsed YAML workflow definition and an evalexpr filter string, asserting both the filter-matches and filter-does-not-match outcomes; no MessagePosted-specific should_fire_workflow test exists, so this is representative rather than message_posted-specific verification of the shared filter arm."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1376-1404"
  - statement: "build_trigger_context maps a stored message event into the TriggerContext a message_posted filter or later step reads: `text` is the event content, `author` the signer's pubkey hex (explicitly not an `actor` tag, because workflow conditions make authorization-relevant decisions from trigger_author and an actor tag is signer-controlled metadata that cannot speak for another pubkey), `channel_id` the channel UUID as a string, `timestamp` the Unix timestamp as a string, `emoji` empty (populated only for KIND_REACTION events), `message_id` the event's own hex id (the reaction-target-id special case does not apply to a plain message), and `is_reply` computed by event_is_reply, delegating to buzz_core::nip10::parse_thread_markers for a valid NIP-10 `reply` marker."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:933-1003"
      - "crates/buzz-workflow/src/lib.rs:1005-1016"
      - "crates/buzz-workflow/src/executor.rs:27-46"
  - statement: "build_trigger_context_message_event asserts every TriggerContext field's mapping from a plain kind:9 message with no e-tags: text, author, channel_id, timestamp and message_id match the source event, emoji is empty, webhook_fields is empty, and is_reply is false."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1592-1607"
  - statement: "build_trigger_context_is_reply_true_for_threaded_message asserts is_reply becomes true when the message event carries both a NIP-10 root e-tag and a reply e-tag, confirming a message_posted filter can select or exclude threaded replies via `trigger_is_reply`."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/lib.rs:1609-1631"
  - statement: "build_eval_context (called by evaluate_condition, which should_fire_workflow awaits for a message_posted filter) exposes six TriggerContext string fields as evalexpr variables named trigger_text, trigger_author, trigger_channel_id, trigger_timestamp, trigger_emoji and trigger_message_id, plus a seventh boolean variable trigger_is_reply -- the doc comment states trigger_is_reply exists specifically so a filter can write `trigger_is_reply == false` to select only top-level messages."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:282-314"
  - statement: "condition_trigger_is_reply_selects_top_level_only asserts evaluate_condition(\"trigger_is_reply == false\", ...) returns true for a top-level message context and false for a threaded-reply context, using the same evaluate_condition path should_fire_workflow calls for a message_posted filter."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1433-1453"
  - statement: "evaluate_condition bounds every filter evaluation, including a message_posted trigger's filter: an expression longer than MAX_EXPR_LEN (4096 bytes) is rejected with a ConditionError before evaluation starts (because the spawn_blocking evaluation thread cannot be cancelled once running), and evaluation itself runs on a blocking thread under a 100ms tokio::time::timeout (EVAL_TIMEOUT), with a timeout, a panicked eval task, or an evalexpr evaluation error all mapped to the same ConditionError variant."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:350-397"
  - statement: "WorkflowDef::validate() -- the precondition every definition must pass before any trigger path (including message_posted) can ever run it -- rejects a `reply_in_thread: true` SendMessage step when the trigger is not one of MessagePosted, ReactionAdded or DiffPosted, because Schedule and Webhook triggers have no triggering message to reply to; validate() performs no syntax check of a message_posted trigger's own `filter` string, so a malformed filter is only ever discovered at fire time, via the should_fire_workflow skip path above, not at save time."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:173-242"
  - statement: "KIND_STREAM_MESSAGE_V2 (kind:40002) is a second, actively-used channel-message kind -- referenced alongside KIND_STREAM_MESSAGE in buzz-db's feed/mention queries and accepted by the relay's ingest handler under the same MessagesWrite scope as kind:9 -- that trigger_matches_event's MessagePosted arm does not match; no design document, ADR, or issue found while drafting this node explains whether that exclusion is intentional or an unaddressed gap in message_posted's trigger coverage."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/kind.rs:480-481"
      - "crates/buzz-db/src/store/feed.rs:107"
      - "crates/buzz-relay/src/handlers/ingest.rs:470-484"
      - "crates/buzz-workflow/src/lib.rs:1037-1046"
    confidence: 0.55
  - statement: "architecture-flows-workflow-execution (launchpad/docs/corpus/architecture/flows/workflow-execution.md) is present in origin/launchpad's merged corpus tree at the recorded revision and documents the shared step-loop executor, the SEC-006 owner-authority recheck, and the community/tenant write-fence all three channel-event triggers (including message_posted) run through after should_fire_workflow returns true -- this node references it rather than restating that content, per git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') showing the file present and validate.py-clean."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md"
  - statement: "This node's directory placement (capabilities/workflows/) follows the repository's own observed convention that a corpus node's top-level directory matches its front-matter `type` field -- confirmed by sampling all 21 nodes currently under architecture/ (type: architecture) and standards/ (type: governance) in origin/launchpad's merged corpus tree, with zero exceptions found -- rather than following the already-drafted, unmerged flow.md template's type: architecture recommendation for step-by-step interaction narratives, since this node's own issue explicitly places it under capabilities/, a directory with no type: architecture precedent."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/principles/nostr-first.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/templates/flow.md"
    confidence: 0.6
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# Message trigger: capabilities/workflows

How `buzz-workflow`'s `message_posted` trigger decides whether a newly stored channel
message causes a workflow to run: the kind it matches, the optional filter that narrows
it further, the trigger-specific data it hands to the rest of the run, and what happens
when that filter is malformed, slow, or absent.

**Scope.** This node covers `TriggerDef::MessagePosted` end to end: its own shape,
`trigger_matches_event`'s kind check, `should_fire_workflow`'s filter narrowing,
`build_trigger_context`'s field mapping for a message event, and `evaluate_condition`'s
bounds on the filter expression itself. It does not cover the shared step-loop executor,
the owner-authority recheck, or the community/tenant write fence every channel-event
trigger (message, reaction, diff) runs through after firing -- see *Boundary* below.

## Trigger, preconditions, termination

**Trigger.** `TriggerDef::MessagePosted { filter: Option<String> }` fires when a stored
event's kind equals `KIND_STREAM_MESSAGE` (9) -- NIP-29 group chat message -- in a channel
with at least one enabled workflow whose trigger is `message_posted`. The `filter` field,
when present, is an evalexpr boolean expression over flat variable names
(`trigger_text`, `trigger_is_reply`, etc.); it narrows *which* kind:9 messages fire the
workflow but plays no part in the kind match itself.

**Preconditions, in the order they are actually checked:**

1. The stored event must carry a `channel_id` — `on_event` returns immediately for any
   event with none, before the kind is even read.
2. The event's kind must not fall in the reserved workflow-execution range
   (46001–46012) — this exclusion is shared by all channel-event triggers and prevents a
   workflow's own emitted messages from re-triggering workflows.
3. The channel must have at least one enabled workflow in the 10-second TTL
   `(community_id, channel_id)` cache — an empty list short-circuits before a
   `TriggerContext` is even built.
4. The workflow's stored definition must parse back into a `WorkflowDef`, and
   `def.enabled` must be true.
5. `trigger_matches_event` must return true for the pair — for `MessagePosted`, this
   is exactly `kind_u32 == 9`, independent of whether `filter` is set.
6. If `filter` is `Some`, `should_fire_workflow`'s call to `evaluate_condition` must
   return `Ok(true)` — see *Failure, abort, rollback* for what happens on `Ok(false)`
   or `Err`.
7. Downstream of this node's scope: the SEC-006 owner-authority recheck and run-creation
   race handling documented in `architecture-flows-workflow-execution`.

**Termination/outcome, within this node's scope.** `should_fire_workflow` returning
`false` is this trigger's own terminal outcome — the candidate workflow is skipped with
no run ever created, no error surfaced, and no trace left beyond a debug/warn log line.
`should_fire_workflow` returning `true` hands control to the owner-authority recheck and
run creation covered by `architecture-flows-workflow-execution`; this node does not
narrate the run's own `Pending → Running → Completed/Failed` lifecycle.

## Ordered interactions and data/state movement

1. The relay's post-store event handler spawns `on_event(community_id, &stored_event)`
   for the stored message event (`crates/buzz-workflow/src/lib.rs:320`).
2. `on_event` reads `event.channel_id`; `None` returns immediately
   (`crates/buzz-workflow/src/lib.rs:325-332`).
3. `on_event` checks `is_workflow_execution_kind(kind_u32)`; a match returns
   immediately (`crates/buzz-workflow/src/lib.rs:334-339`).
4. `on_event` reads (or populates) the per-`(community_id, channel_id)` enabled-workflow
   cache; an empty list returns immediately
   (`crates/buzz-workflow/src/lib.rs:341-358`).
5. `build_trigger_context(event)` constructs the `TriggerContext` once for the event,
   shared across every candidate workflow in the channel: `text`, `author`,
   `channel_id`, `timestamp`, `emoji` (empty for a message), `message_id` (the message's
   own id), and `is_reply` from `event_is_reply`
   (`crates/buzz-workflow/src/lib.rs:360`, `933-1016`).
6. For each cached workflow: parse its definition; skip if disabled or if
   `trigger_matches_event(&def.trigger, kind_u32)` is false — for `MessagePosted` this
   is `kind_u32 == 9` (`crates/buzz-workflow/src/lib.rs:370-379`, `1037-1046`).
7. Call `should_fire_workflow(&def, &trigger_ctx, workflow.id)`. For a `MessagePosted`
   trigger with `filter: Some(expr)`, this resolves to
   `evaluate_condition(expr, trigger_ctx, &HashMap::new())`
   (`crates/buzz-workflow/src/lib.rs:383`, `883-931`).
8. `evaluate_condition` builds an evalexpr context exposing `trigger_text`,
   `trigger_author`, `trigger_channel_id`, `trigger_timestamp`, `trigger_emoji`,
   `trigger_message_id` (strings) and `trigger_is_reply` (boolean), rejects the
   expression outright above 4096 bytes, then evaluates it on a blocking thread under a
   100ms timeout (`crates/buzz-workflow/src/executor.rs:282-314`, `350-397`).
9. A `true` result lets the loop continue to the SEC-006 owner-authority recheck and
   `create_workflow_run` — out of this node's scope, see
   `architecture-flows-workflow-execution`
   (`crates/buzz-workflow/src/lib.rs:387-439`).

## Trust-boundary crossings

- **Message content and authorship cross into workflow-condition and template
  evaluation.** `build_trigger_context` takes `author` from the event's cryptographic
  signature (`event.event.pubkey`), never from an `actor` tag, specifically because
  workflow filters and later step templates make authorization-adjacent decisions from
  `trigger_author` and an `actor` tag is ordinary signer-controlled metadata that cannot
  speak for another pubkey (`crates/buzz-workflow/src/lib.rs:946-949`).
- **The filter expression is untrusted-shape but not sandboxed against resource abuse
  beyond length and time.** A workflow owner authors the `filter` string; it is bounded
  to 4096 bytes and a 100ms wall-clock budget, but a `spawn_blocking` task already
  running past that budget is not cancelled — only the caller stops waiting on it — so
  the length cap is the actual defense against a pathological expression, not the
  timeout alone (`crates/buzz-workflow/src/executor.rs:371-381`).
- **No community/tenant or owner-authority crossing is decided within this node's
  scope.** Both are re-checked immediately after `should_fire_workflow` returns true,
  documented in `architecture-flows-workflow-execution`, not here.

## Failure, abort, rollback behavior

- **A missing or unmatched channel_id, kind, or cached-workflow list is a silent skip,
  not a failure.** None of these preconditions produce an error, a log above `debug`
  level, or any persisted state — the event is simply never looked at further by this
  trigger.
- **A filter that evaluates to `false` skips the candidate workflow with a debug log**;
  no run is created, and this is indistinguishable in the database from a workflow that
  was never a candidate at all.
- **A filter evaluation error (parse error, undefined variable, timeout, or the 4096-byte
  length rejection) also skips the workflow, logged at `warn`** — `should_fire_workflow`
  treats `Ok(false)` and `Err(_)` identically, both returning `false`. This differs from
  a step's own `if:` condition later in the same run, where an evaluation error *aborts*
  the run instead of merely skipping a step — a message_posted trigger's filter error is
  fail-closed at the *trigger* stage (never fires), while a step's condition error is
  fail-stop at the *execution* stage (partial trace, run marked `Failed`). No dedicated
  test exercises the filter-error-skip path specifically for `should_fire_workflow`;
  this is stated as a gap, not verified behavior.
- **No compensating action exists for a workflow that should not have fired.** Once a
  filter evaluates `true` and a run is created, this node's scope ends; any rollback
  after that point is `architecture-flows-workflow-execution`'s concern.
- **Representative verification:**
  - `message_posted_matches_kind_9_only`, `message_posted_does_not_match_kind_40008`,
    `message_posted_with_filter_still_matches_kind_9`
    (`crates/buzz-workflow/src/lib.rs:1437-1448`, `1540-1545`, `1476-1484`) — the kind
    match is exact and independent of the filter's presence.
  - `build_trigger_context_message_event`,
    `build_trigger_context_is_reply_true_for_threaded_message`
    (`crates/buzz-workflow/src/lib.rs:1592-1607`, `1609-1631`) — the field mapping a
    filter or later step actually reads.
  - `condition_trigger_is_reply_selects_top_level_only`
    (`crates/buzz-workflow/src/executor.rs:1433-1453`) — `trigger_is_reply` usable in a
    message_posted filter.
  - `reaction_filter_matches_target_message`
    (`crates/buzz-workflow/src/lib.rs:1376-1404`) — the shared `should_fire_workflow`
    filter arm `MessagePosted` also uses, exercised via the sibling trigger since no
    `MessagePosted`-specific instance of this test exists.

## Boundary

This node does not describe:
- The shared sequential step executor, the SEC-006 owner-authority recheck, or the
  community/tenant write fence — all covered by `architecture-flows-workflow-execution`,
  which every channel-event trigger (including this one) runs through after firing.
- The `reaction_added` and `diff_posted` triggers' own kind- and emoji-matching
  specifics — siblings of this trigger family, each its own corpus task (`#831` for
  `reaction_added`; `diff_posted` is not yet a separately tracked task at the time this
  node was written).
- The `schedule` and `webhook` triggers, which never match a channel event at all —
  `#832` and `#837`.
- Workflow *action* dispatch (what happens once a run's steps execute) — out of scope
  for a trigger-focused node.

## Relationships

- `references`: `architecture-flows-workflow-execution` — the flow node this trigger's
  matched-and-fired output feeds into; declared because that node is present and
  validate.py-clean on `origin/launchpad` at the recorded revision.

## Scope and omissions

**This node covers** `TriggerDef::MessagePosted`'s own kind match, its optional
evalexpr filter and the trigger-context fields that filter reads, the preconditions
checked before either runs, and the fail-closed-at-the-trigger-stage failure mode a
filter error produces — grounded in `crates/buzz-workflow/src/schema.rs`,
`crates/buzz-workflow/src/lib.rs` and `crates/buzz-workflow/src/executor.rs` at the
commit recorded above.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Shared step executor, owner-authority recheck, tenant/community fencing | `architecture-flows-workflow-execution` |
| `reaction_added` trigger specifics | `#831` (reaction-trigger, not yet drafted) |
| `schedule` / `webhook` trigger specifics | `#832` / `#837` (not yet drafted) |
| Workflow action dispatch | out of scope for this node |

**Expected but not verified when this node was written:**
- **Whether `KIND_STREAM_MESSAGE_V2` (kind:40002) messages are intentionally excluded
  from `message_posted` triggers is unresolved.** Both kinds are treated as live
  channel messages elsewhere (buzz-db's feed/mention queries, the relay's ingest
  scope check), but `trigger_matches_event`'s `MessagePosted` arm matches only kind:9.
  No design document, ADR, or issue explaining this was found while drafting this node
  — see the `INFERENCE` evidence entry above.
- **No dedicated test exercises a filter-evaluation error (as opposed to a
  filter-evaluates-false) specifically for `should_fire_workflow`.** The code path
  (`Err(_) => { warn!(...); false }`) was read directly and is unambiguous, but its
  behavior is not independently pinned by a unit test the way the false-path and the
  kind-match path are.
- **Whether any workflow-authoring UI or CLI validates a `message_posted` filter's
  evalexpr syntax before save was not checked** — `WorkflowDef::validate()` itself
  performs no such check, but a client-side check outside `buzz-workflow` was not
  ruled out.

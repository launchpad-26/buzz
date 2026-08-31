# Issue #701: document capabilities/activity/needs-action.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/activity/needs-action.md` does not exist
  (confirmed: `find launchpad/docs/corpus/capabilities` errors "No such file or
  directory" — no `capabilities/` directory exists anywhere in the corpus yet).
- The corpus's `flow.md` template (`launchpad/docs/corpus/templates/flow.md`)
  already prescribes required sections for exactly this shape of node (a
  step-by-step, cited, multi-actor runtime interaction) and its own worked
  precedent, `architecture/flows/push-notification.md` (merged, `type:
  architecture`, `status: draft`), shows a fully-realized instance to model
  structure from.
- The real mechanism is grounded and read directly at commit
  `cad6c375fdcc590158c1456c9fc7875f0f84a844`:
  - `crates/buzz-db/src/store/feed.rs` — `build_needs_action_query` /
    `query_needs_action` / `Db::query_feed_needs_action_routed` select events of
    kind `KIND_WORKFLOW_APPROVAL_REQUESTED` (46010) or `KIND_STREAM_REMINDER`
    (40007) joined against `event_mentions` for the caller's pubkey, scoped to
    accessible channels, capped at `FEED_MAX_LIMIT` (100).
  - `crates/buzz-relay/src/api/bridge.rs` (`query_events_authed`, lines
    ~1000-1246) is the actual trigger: `POST /query`, NIP-98 authenticated,
    dispatches on a `feed_types: ["needs_action", ...]` extension field on a
    Nostr filter (`extract_feed_types`), checked against relay membership,
    channel access, and `reader_authorized_for_event` before returning JSON.
  - `crates/buzz-cli/src/commands/feed.rs` (`cmd_get_feed`) is the CLI-side
    caller building the same `feed_types` filter.
  - `crates/buzz-db/src/store/event.rs:1351-1370` (`Db::insert_event`) shows
    `insert_mentions` runs in a **separate** transaction after the event
    insert commits, and a failure there is only `tracing::warn!`-logged — the
    event is durably stored either way. This is a real, citable failure mode:
    mention indexing (and therefore needs_action visibility) is best-effort,
    not atomic with storage.
  - `crates/buzz-workflow/src/executor.rs:724-729` — the `RequestApproval`
    step returns `Suspended` but its own comment reads `// TODO (WF-08):
    create approval record in DB, emit kind:46010.` — kind:46010 is **never
    emitted** anywhere in the repository today. Already independently
    documented and verified by the merged sibling node
    `architecture-flows-workflow-execution` (evidence entry citing the same
    fact), so this node will `references` it rather than re-deriving the
    finding.
  - `crates/buzz-relay/src/handlers/ingest.rs` confirms `KIND_STREAM_REMINDER`
    (40007) is an ordinary, channel-scoped (`requires_h_channel_scope`),
    `MessagesWrite`-scope client-authored event — no special server-side
    creation logic beyond generic ingest (unlike kind 30300's NIP-ER
    `not_before` validation, a *different*, unrelated reminder kind).
- Relevant merged sibling nodes exist and are safe `references` targets (on
  `origin/launchpad`, confirmed via the checked-out worktree tree):
  `architecture-flows-workflow-execution`,
  `architecture-flows-http-event-submission`,
  `architecture-containers-relay`. No existing corpus node documents the
  feed/`event_mentions`/`feed_types` mechanism itself — nothing to duplicate.
- No `type: capabilities` node exists yet in the corpus; the flow template's
  own precedent (`architecture-flows-*`, all `type: architecture`) is the only
  established convention for a flow-shaped instance node, so this node follows
  that precedent despite living under `capabilities/activity/` rather than
  `architecture/flows/` (the issue names this exact path).

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/activity/needs-action.md` following
`flow.md`'s required sections (Flow statement, Sequence, Diagram, Outcome,
Boundary, Relationships, Scope and omissions), scoped narrowly to **the
needs-action retrieval flow**: how an already-stored kind:46010 or kind:40007
event becomes visible to its target user through `feed_types: ["needs_action"]`
on `POST /query`. Front matter: `id: capabilities-activity-needs-action`,
`type: architecture` (INFERENCE, confidence noted, same reasoning
`architecture-flows-*` already established), `status: draft`, `origin:
launchpad`, `audiences: [agent, developer, reviewer]`, evidence ledger built
only from sources read in this session, `relationships: references
architecture-flows-workflow-execution` (for the WF-08 gap, not re-derived) and
`references architecture-flows-http-event-submission` (for the shared
`/query`/NIP-98 bridge mechanics, not re-derived).

Done when: file exists, front matter is schema-shaped, every claim in the body
has a corresponding evidence-ledger entry classified honestly.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root. Fix any schema violation, bad citation, or unresolved relationship
target; re-run until exit 0.

Done when: exit code 0.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK` in the output before touching git.

Done when: `OK` appears and exit code is 0.

## STEP 4 — Commit (local only, no push, no PR)

`git add` the new corpus file and this plan file; commit with
`git commit -s -m "docs(corpus): document capabilities/activity/needs-action (#701)"`.
Per this batch's process, stop here — no push, no PR.

Done when: `git log` shows the new commit on `task/701-needs-action`.

## STEP 5 — Self-review

Re-read the diff against issue #701's DoD checklist line by line; re-open each
cited source to confirm it actually supports its claim; confirm no second
hand-authored canonical document was created; re-run `validate.py` to confirm
it still exits 0. `review-code`/`review-adjudicate` are deliberately **not**
run in this batch mode — this step is a self-review substitute, and the final
report says so explicitly.

## PARALLEL

None — this is a single-file, single-agent task with no independent lanes.

## GATES

- `validate.py` must exit 0 before commit.
- The unittest discover command must print `OK` before commit — this is the
  batch's commit gate, not optional, and must run as its own isolated tool
  call per the dispatch instructions.

## BUDGET

Single node, ~1 file, capped at the 5 steps above. No code changes, no test
changes outside the corpus tree.

## OPEN

- Whether `type: architecture` is the right long-term home for a node living
  under `capabilities/` rather than `architecture/flows/` is genuinely
  unsettled — flagged as an explicit INFERENCE in the evidence ledger, not
  papered over.

## LEFT OUT

- Re-deriving the WF-08 workflow-approval-not-emitted finding from scratch —
  `architecture-flows-workflow-execution` already established and verified it;
  this node cites and references that node instead.
- The full NIP-PL-style protocol-level detail of kind:30300 (`KIND_EVENT_REMINDER`,
  NIP-ER) — a distinct, unrelated reminder mechanism from kind:40007
  (`KIND_STREAM_REMINDER`), confirmed by reading `crates/buzz-core/src/kind.rs`
  and `crates/buzz-relay/src/handlers/ingest.rs`; out of scope for this node
  and not to be confused with it.
- Any client-side (desktop/mobile) rendering detail beyond what is needed to
  state the flow's outcome — that is UI/component territory, not this flow's
  concern.

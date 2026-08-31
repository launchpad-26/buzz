---
id: capabilities-reminders-reminder
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "NIP-ER defines kind:30300 as an encrypted, author-only, addressable reminder event: the reminder's target, note, and status are NIP-44-encrypted to the author, a public not_before tag tells supporting relays when the reminder becomes due, and the spec's own Non-Goals section states it does not define recurrence, shared reminders, push notifications, calendar events, or cryptographic time-locking."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md"
      - "docs/nips/NIP-ER.md:23"
      - "crates/buzz-core/src/kind.rs:96-102"
  - statement: "KIND_EVENT_REMINDER (30300) is registered in AUTHOR_ONLY_KINDS, the set of kinds whose stored events the relay must never reveal to anyone but the authenticated author, and a compile-time assertion checks that it falls in the parameterized-replaceable 30000-39999 range."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:129-130"
      - "crates/buzz-core/src/kind.rs:862"
  - statement: "Reminders are created and managed entirely by clients submitting kind:30300 events; there is no buzz-workflow trigger and no buzz-cli subcommand for reminders -- buzz-cli's top-level command enum lists Agents, Messages, Channels, Canvas, Reactions, Emoji, Dms, Users, Workflows, Feed, Social, Notes, Repos, Projects, Patches, Issues, Pr, Media, Upload, Mem, Pack, and Moderation, with no reminders variant among them."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:176-243"
  - statement: "The relay's background reminder scheduler polls query_due_reminders on an interval (default 10 seconds, SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS) for kind:30300 rows whose not_before has passed and whose delivered_at is still NULL, atomically claims each one with claim_due_reminder_with_stamp before publishing, and publishes the claimed reminder over Redis pub/sub so it fans out only to the reminder's own author's live subscription; a failed publish releases the claim via release_due_reminder so a later tick can retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:769-891"
      - "crates/buzz-db/src/store/reminder.rs:39-70"
      - "crates/buzz-db/src/store/reminder.rs:120-142"
  - statement: "A due-reminder row's channel_id is documented in code as always None, because reminders are global, author-scoped events rather than channel posts -- the scheduler delivers a due reminder back to its own author, never into a channel."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/reminder.rs:32-33"
  - statement: "The desktop reminders feature creates, snoozes, completes, and cancels reminders by publishing kind:30300 events through reminderService.ts, and a separate hook fires a local desktop notification (not a channel message) when a reminder becomes due."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderService.ts:8"
      - "desktop/src/features/reminders/lib/reminderService.ts:146-274"
      - "desktop/src/features/reminders/useReminderNotifications.ts:79-90"
  - statement: "Desktop's own dedicated /reminders route now does nothing but redirect to the inbox, per its code comment: reminders became a filter option inside the inbox dropdown rather than a standalone page."
    entry_class: FACT
    evidence:
      - "desktop/src/app/routes/reminders.tsx:1-9"
  - statement: "Mobile carries an independent Flutter implementation of kind:30300 reminder creation alongside the same encrypted-content shape desktop uses."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/reminders/reminder_service.dart"
  - statement: "CHANGELOG.md records the reminders capability's build-out in upstream history this fork inherits: PR #934 implemented relay-side NIP-ER support for kind:30300, PR #963 added the desktop NIP-ER reminder UI (create, view, manage encrypted reminders), and PR #1093 added desktop reminder notifications, snooze, an overlay, and an inbox view mode -- i.e. the capability is shipped, not merely designed."
    entry_class: FACT
    evidence:
      - "CHANGELOG.md:1685"
      - "CHANGELOG.md:1683"
      - "CHANGELOG.md:1668"
  - statement: "crates/buzz-test-client/tests/e2e_event_reminder.rs exercises kind:30300 end to end: not_before/d-tag/expiration validation and rejection, author-only read/query/subscription isolation over both HTTP and WebSocket, and replacement (snooze) semantics -- representative verification for the capability's create/schedule/receive behavior."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_event_reminder.rs"
  - statement: "The relay's kind registry additionally declares a second, distinct kind, KIND_STREAM_REMINDER (40007), documented as 'a reminder attached to a stream message or time,' which the relay's needs-action feed query and the desktop inbox's label/preview rendering both handle as a display case, but no source file anywhere in the repository constructs, signs, or publishes an event of that kind outside a hardcoded mock feed item in the desktop end-to-end test bridge -- this kind has a read path and no write path."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:491"
      - "crates/buzz-db/src/store/feed.rs:191-193"
      - "desktop/src/features/home/lib/inbox.ts:146-148"
      - "desktop/src/testing/e2eBridge.ts:7811-7813"
  - statement: "At the recorded revision, the merged corpus under launchpad/docs/corpus/ carries no capabilities/, architecture, or interface node about reminders, and issue #813 (reminder-lifecycle, a flow node) is not merged, so this node has no relationships target to declare."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no capabilities/ directory and no node mentioning reminders anywhere in the tree, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Issue #814 scopes this document to the overall reminder capability (creating, scheduling, and receiving reminders), distinct from sibling issue #813's reminder-lifecycle flow node, which this document cross-references without duplicating."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#814 objective and definition of done; launchpad-26/buzz#813 objective, both read directly via gh issue view"
---

# Reminders: capability

Buzz lets a user privately remind themselves about something -- optionally
pointing at a specific message in a channel for context -- and be notified again
once a chosen time arrives, without exposing to anyone else what the reminder is
about or that it exists at all. This is implemented as NIP-ER: an encrypted,
author-only, addressable `kind:30300` event whose only public field is a
`not_before` due-time tag. A user can create a reminder, snooze it to a later
time, mark it done, or cancel it; the relay's own background scheduler is
responsible for recognizing when a reminder becomes due and delivering it back
to its author.

## Maturity

**Shipped**, across all three client-facing layers. The relay implements
`kind:30300` ingest, storage, and a due-reminder delivery scheduler; the desktop
app implements a full reminders feature (create, snooze, complete, cancel, local
notification on due); and the mobile app carries an independent Flutter
implementation of the same `kind:30300` creation and encrypted-content shape.
`CHANGELOG.md` records this build-out in the upstream history this fork
inherits, starting with the relay's NIP-ER support and the desktop reminder UI,
followed by desktop notification/snooze/overlay polish.

## Boundary

This node does not describe:

- **How the relay, desktop, and mobile clients are built internally** -- the
  scheduler's polling/claim-and-publish implementation, the desktop React hook
  composition, or the Flutter provider wiring. No architecture node exists yet
  for this capability to `references`.
- **The interface(s) this capability is exposed through.** No interface node
  exists yet. Notably, there is no CLI surface: `buzz-cli`'s top-level command
  enum has no `reminders` subcommand, so a reminder can only be created through
  the desktop or mobile client, or by hand-crafting a `kind:30300` event
  directly against the relay.
- **The step-by-step lifecycle a single reminder goes through** -- create,
  pending, snooze/complete/cancel, scheduler claim, delivery, and the races and
  failure modes along the way. That is issue #813's own flow node
  (`reminder-lifecycle`), not duplicated here. No `relationships` edge targets
  it because it is not merged into the corpus yet.
- **A second, separate, declared-but-unproduced kind.** The relay's kind
  registry also declares `KIND_STREAM_REMINDER` (`40007`), described as "a
  reminder attached to a stream message or time." It has a read path -- the
  relay's needs-action feed query and the desktop inbox's label/preview
  rendering both handle it -- but no code anywhere in the repository
  constructs, signs, or publishes an event of that kind outside a hardcoded
  mock fixture in the desktop end-to-end test bridge. This is a distinct,
  unfinished concept with no write path, so it is named here as a boundary
  rather than folded into the capability statement above, which describes only
  the shipped `kind:30300` primitive.
- **How the running scheduler is operated in production** -- its interval and
  batch-size tuning, deployment, and scaling. That is the `operations` corpus
  surface, not this one.

## Relationships

Declared: none. At the recorded revision the merged corpus carries no
`capabilities/`, architecture, or interface node about reminders to
`references`, and issue #813's `reminder-lifecycle` flow node -- the natural
`references` or sibling target -- is not merged, so its `id` does not resolve.
This is a fact about the corpus's current contents, checked directly rather
than assumed; the first architecture, interface, or flow node for this
capability to land is the moment to add the corresponding edge.

## Scope and omissions

**This node covers** what the reminders capability lets a user do, its shipped
maturity across relay/desktop/mobile, and its boundary against the lifecycle
flow, the (nonexistent) interface and architecture nodes, and the operational
surface.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The step-by-step reminder lifecycle (create, snooze, complete, cancel, delivery race handling) | #813 (`reminder-lifecycle`, not yet merged) |
| How the relay scheduler, desktop client, or mobile client are internally built | No architecture node yet |
| The interface surface (there is currently none for the CLI) | No interface node yet |
| `KIND_STREAM_REMINDER` (40007), the declared-but-unproduced channel-visible reminder kind | No issue was found or opened for it while drafting this node |
| Operating the scheduler in production (tuning, deployment, scaling) | The `operations` corpus surface |
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating, and retiring a node procedurally | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- Whether the desktop client's OS-level notification permission handling was
  exercised end to end -- only the in-app toast/watermark logic in
  `useReminderNotifications.ts` was read.
- Whether mobile's due-reminder delivery path polls independently or otherwise
  depends on the same relay scheduler push that desktop relies on --
  `reminder_service.dart`'s read path was not traced against
  `crates/buzz-relay/src/main.rs`'s scheduler in the same depth as desktop's was.
- Whether any GitHub issue already tracks `KIND_STREAM_REMINDER` (40007) as
  unfinished work -- the issue tracker was not searched for it while drafting
  this node.

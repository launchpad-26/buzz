---
id: capabilities-reminders-reminder-lifecycle
type: architecture
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
  - statement: "node.schema.json's type enum has no member named flow, dynamic, or sequence; the merged flow template (launchpad/docs/corpus/templates/flow.md) resolves this by giving flow-shaped instance nodes type: architecture, extending the precedent the merged C4 architecture-triad templates set, with the flow node references-ing the capability/interface/event-kind nodes it narrates a path across rather than being typed capabilities itself. The one real merged flow instance in this corpus, architecture-flows-websocket-authentication, follows exactly that: type: architecture, no relationships to a capability node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "This node's type: architecture choice, and its placement under capabilities/reminders/ rather than architecture/flows/, follows the target path issue #813 itself specifies rather than a corpus-wide directory convention; no authority stronger than the flow template's own template-node judgment call (confidence 0.6, per that template's own evidence ledger) settles whether type: architecture or type: capabilities is the better long-term fit for a flow-shaped node filed under a capabilities/ directory."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/templates/flow.md"
    confidence: 0.6
  - statement: "kind:30300 is registered as KIND_EVENT_REMINDER, documented in the kind registry as NIP-ER Event Reminder: a parameterized-replaceable, author-only event addressed by (pubkey, kind, d_tag), with a public not_before tag and NIP-44-encrypted target/note/status."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:96-102"
      - "crates/buzz-core/src/kind.rs:862"
  - statement: "KIND_EVENT_REMINDER is one of three entries in AUTHOR_ONLY_KINDS, a set the kind registry documents as kinds whose stored events the relay must never reveal -- existence, count, tags, content, schedule, or search matches -- to anyone but the authenticated author, shared across both the ingest write path and the REQ/COUNT read path."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:120-133"
  - statement: "NIP-ER's Content section requires the decrypted plaintext to be a JSON object with a status of pending, done, or cancelled, an optional target object and/or note, and requires a pending reminder to carry either a valid target reference or a non-empty note."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md:79-113"
  - statement: "NIP-ER's State section defines four common transitions as NIP-01 addressable-event replacements on the same (pubkey, 30300, d) address: create and snooze keep status pending (snooze sets a later not_before), while complete and cancel set a terminal status, omit not_before, and add an expiration tag."
    entry_class: FACT
    evidence:
      - "docs/nips/NIP-ER.md:114-129"
  - statement: "The desktop client's createReminder generates a fresh 128-bit-entropy d tag, encrypts the pending-status content to the author's own key via nip44EncryptToSelf, attaches a not_before tag, signs, and publishes a kind:30300 event."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderService.ts:26-33"
      - "desktop/src/features/reminders/lib/reminderService.ts:155-184"
  - statement: "completeReminder and cancelReminder each republish the same d-tag address with status done or cancelled respectively, omit the not_before tag, and set an expiration tag jittered to 30-90 days out for later cleanup, matching NIP-ER's requirement that terminal states omit not_before and SHOULD carry a jittered expiration."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderService.ts:15-19"
      - "desktop/src/features/reminders/lib/reminderService.ts:186-214"
      - "desktop/src/features/reminders/lib/reminderService.ts:246-274"
  - statement: "snoozeReminder republishes the same d-tag address with status pending and a later not_before, rather than creating a new reminder address, so a snooze is a NIP-33 replacement of the existing head."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderService.ts:216-244"
  - statement: "The desktop client's decryptReminder and parseReminderContent fail closed: undecryptable ciphertext, non-JSON plaintext, an unrecognized status, or a target object missing a required field all cause the reminder to be dropped (returned as null and filtered out) rather than surfaced to the user in a partially-trusted state."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderService.ts:58-94"
      - "desktop/src/features/reminders/lib/reminderService.ts:117-142"
  - statement: "The relay's ingest handler runs validate_event_reminder on every kind:30300 write before NIP-33 replacement is applied, rejecting the event with \"invalid: <reason>\" for a missing, empty, or duplicate d tag; a malformed, duplicate, or out-of-range not_before; a not_before beyond the horizon configured by SPROUT_MAX_NOT_BEFORE_DELTA (default one year); or an expiration at or before not_before."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1956-1974"
      - "crates/buzz-relay/src/handlers/ingest.rs:1985-2054"
      - "crates/buzz-relay/src/handlers/ingest.rs:2770-2773"
  - statement: "The relay enforces author-only reads for kind 30300 at three points: an unauthenticated REQ is closed with an auth-required message before any filter is evaluated; a filter targeting only author-only kinds whose authors do not resolve to the requester's own pubkey is closed with a restricted message; and, for a mixed-kind filter that passes that pre-filter gate, the per-event delivery predicate silently omits any author-only-kind event whose author is not the requester."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/req.rs:83-93"
      - "crates/buzz-relay/src/handlers/req.rs:235-241"
      - "crates/buzz-relay/src/handlers/req.rs:1339-1345"
      - "crates/buzz-relay/src/handlers/req.rs:1382-1404"
  - statement: "The relay's NIP-11 relay-information document unconditionally advertises the nip-er supported_extensions entry, a due_delivery_mode of \"push\", and a max_not_before_delta drawn from the SPROUT_MAX_NOT_BEFORE_DELTA environment variable (defaulting to 31,536,000 seconds / one year), the same limit validate_event_reminder enforces on write."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs:105-110"
      - "crates/buzz-relay/src/nip11.rs:124-143"
      - "crates/buzz-relay/src/nip11.rs:192"
  - statement: "A background scheduler task spawned in the relay's startup path polls query_due_reminders every SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS (default 10 seconds), atomically claims each due reminder via claim_due_reminder_with_stamp so only one relay pod delivers it, and publishes the due event over Redis pub/sub for cross-pod WebSocket fan-out; a failed publish releases the claim so a later tick (this pod or another) can retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:769-891"
  - statement: "The desktop client does not rely on relay due-signal timing alone: useReminderNotifications polls on a fixed interval (30 seconds, per REMINDER_NOTIFICATION_POLL_INTERVAL_MS) and fires a toast only for pending reminders whose not_before crossed strictly after a persisted watermark and at or before the current time; the watermark is seeded to \"now\" (not zero) on first-ever launch specifically so a user's entire reminder history is never replayed as toasts."
    entry_class: FACT
    evidence:
      - "desktop/src/features/reminders/lib/reminderNotificationPoll.ts:1-11"
      - "desktop/src/features/reminders/useReminderNotifications.ts:32-49"
      - "desktop/src/features/reminders/useReminderNotifications.ts:118-148"
      - "desktop/src/features/reminders/lib/reminderFilters.ts:32-44"
  - statement: "The mobile client independently implements the same wire contract in Dart -- kind-30300 events, the same NIP-44 self-encryption conversation-key derivation, and the same d-tag/not_before tag construction -- with its own source comments stating the plaintext shape is built to match desktop's reminderService.ts#createReminder exactly so reminders created on either client are readable by both."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/reminders/reminder_service.dart:11-13"
      - "mobile/lib/shared/reminders/reminder_service.dart:42-53"
      - "mobile/lib/shared/reminders/reminder_service.dart:61-74"
  - statement: "Issue #813's own Definition of Done, and its flow-specific tail, require this document to state trigger/preconditions/termination, list ordered interactions and data/state movement, identify authentication/authorization/trust-boundary crossings where relevant, and document failure/abort/rollback behavior linked to representative verification -- the same four bullets issue #686's Definition of Done used for the corpus's one other merged flow instance, architecture-flows-websocket-authentication, whose section structure this document follows directly."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#813 definition of done"
relationships:
  - type: part-of
    target: capabilities-reminders-reminder
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-containers-desktop
---

# Flow: Reminder Lifecycle (NIP-ER)

How a Buzz reminder moves from creation through becoming due, being
snoozed, completed, or cancelled, and what the relay and each client
enforce at every step. This is the step-by-step narration NIP-ER
(`docs/nips/NIP-ER.md`) specifies and `kind:30300` implements; it is
distinct from a not-yet-drafted capability-level node that would state
what "reminders" let a user do, and from an interface-level node that
would document the CLI/HTTP/WebSocket surface in general, durable terms.

## Trigger, preconditions, and termination

**Trigger.** A user (via desktop or mobile) attaches a reminder to a
message, or creates a standalone note-only reminder, choosing a due time.
The client builds a fresh, opaque `d` tag with 128 bits of entropy and
signs a `kind:30300` event carrying a public `not_before` tag and a
NIP-44-ciphertext-encrypted-to-self payload.

**Preconditions.**

- The author holds a Nostr keypair capable of NIP-44 self-encryption and
  Schnorr signing.
- The client is authenticated to the relay (NIP-42) before it may read its
  own reminders back or receive a due signal -- `kind:30300` is one of
  three `AUTHOR_ONLY_KINDS` the relay must never reveal to a non-author.
- The chosen `not_before` is within the relay's configured horizon
  (`SPROUT_MAX_NOT_BEFORE_DELTA`, default one year); a reminder scheduled
  further out is rejected at ingest, not silently truncated.

**Termination / outcome.** A reminder's `(pubkey, 30300, d)` address ends
in exactly one of:

1. **Terminal `done`** -- the user acknowledged it (`completeReminder`).
   `not_before` is omitted and a jittered 30-90 day `expiration` is set.
2. **Terminal `cancelled`** -- the user dismissed it without completing it
   (`cancelReminder`). Same `not_before`-omitted, jittered-`expiration`
   shape as `done`.
3. **Hard-deleted** -- a NIP-09 deletion request referencing the
   `30300:<pubkey>:<d>` address, per NIP-ER's own guidance to publish a
   `cancelled` replacement first, since a `kind:5` deletion is not
   guaranteed to reach a held due-reminder path before it fires.

A reminder that is merely snoozed does **not** terminate: it stays
`pending` at the same address with a later `not_before`, and the lifecycle
above still applies to it going forward.

## Ordered interactions and data/state movement

1. **Client: build and encrypt.** The client constructs the plaintext
   `{"target"?, "note"?, "status": "pending"}`, NIP-44-encrypts it to the
   author's own pubkey, and attaches `["d", <128-bit-entropy id>]` and
   `["not_before", "<unix-seconds>"]` tags.
2. **Client: sign and publish.** The client signs the event and publishes
   it to the relay (`relayClient.publishEvent`).
3. **Relay: validate the public envelope.** Before NIP-33 replacement is
   applied, the ingest handler's `validate_event_reminder` checks the `d`
   tag (exactly one, non-empty), the `not_before` tag (well-formed decimal,
   at most one, within the configured horizon), and -- when both are
   present -- that `expiration` is strictly after `not_before`. The relay
   never decrypts the content to do this; only the public tags are
   inspected.
4. **Relay: replace the address.** A valid event becomes the new head for
   `(pubkey, 30300, d)`, replacing (not appending to) any prior version at
   the same address, per NIP-01 parameterized-replaceable semantics.
5. **Relay: schedule the due signal.** A background scheduler task polls
   `query_due_reminders` every ~10 seconds (`SPROUT_REMINDER_SCHEDULER_INTERVAL_SECS`),
   finds reminders whose `not_before` has passed, atomically claims each
   one (so exactly one relay pod delivers it even when several are
   running), and publishes the due event over Redis pub/sub.
6. **Relay: fan out.** Every pod's existing local pub/sub consumer picks
   up the published due event and delivers it to matching live
   subscriptions, re-applying the author-only read gate on delivery.
7. **Client: detect due-ness locally.** Independent of relay delivery
   timing, each client (desktop, and by the same contract mobile) polls
   its own fetched reminder set on an interval, comparing each pending
   reminder's `not_before` against a persisted watermark and the current
   time, and fires a notification only for reminders that newly crossed
   that boundary since the last check.
8. **Client: act on the reminder.** The user snoozes (replace at the same
   address with a later `not_before` and status still `pending`),
   completes, or cancels (replace with a terminal status, no `not_before`,
   a jittered `expiration`) -- looping back to step 1 for the new
   replacement event.

## Trust-boundary and authorization crossings

- **Relay is schedule-aware but content-blind.** The relay reads and
  validates the public `not_before`/`d`/`expiration` tags to schedule due
  signals, but the target, note, and status live only in NIP-44 ciphertext
  the relay never decrypts. This is a deliberate privacy boundary NIP-ER
  states explicitly: the relay learns *that* an author has a reminder due
  at a time, never *what* it is about.
- **Author-only read boundary (NIP-42).** `kind:30300` reads cross a
  stricter boundary than an ordinary channel-scoped event: an
  unauthenticated subscription is closed outright
  (`"auth-required: authenticate before subscribing"`), and an
  authenticated subscription for another author's reminders is closed
  with `"restricted: author-only kinds require authors=[self]"`. A
  mixed-kind filter that also touches `kind:30300` does not get closed,
  but the per-event delivery loop silently omits any reminder that is not
  the requester's own, rather than surfacing an error that would itself
  leak the reminder's existence.
- **Write-side identity binding.** As with every other event kind, the
  relay's ingest path binds a published event's `pubkey` to the connection's
  authenticated identity before accepting it, so a reminder cannot be
  created, snoozed, completed, or cancelled on behalf of a different
  author's address.

## Failure, abort, and rollback behavior

| Failure | Detected by | Resulting state | Representative verification |
|---|---|---|---|
| Missing / empty / duplicate `d` tag | `validate_event_reminder` | Event rejected (`"invalid: missing d tag"` / `"empty d tag"` / `"duplicate d tag"`); no replacement occurs | `crates/buzz-relay/src/handlers/ingest.rs` unit tests (`missing d tag`, `empty d tag`, `duplicate d tag` cases); `test_reminder_rejected_missing_d_tag`, `test_reminder_rejected_empty_d_tag`, `test_reminder_rejected_duplicate_d_tag` in `crates/buzz-test-client/tests/e2e_event_reminder.rs` |
| Malformed `not_before` (non-digits, leading zero, above `Number.MAX_SAFE_INTEGER`, duplicate tag) | `validate_not_before` / `validate_event_reminder` | Event rejected (`"invalid: malformed not_before"`) | `not_before_rejects_*` unit tests in `ingest.rs`; `test_reminder_rejected_malformed_not_before_leading_zero`, `test_reminder_rejected_malformed_not_before_non_digits`, `test_reminder_rejected_not_before_above_max_safe_integer`, `test_reminder_rejected_duplicate_not_before` in `e2e_event_reminder.rs` |
| `not_before` beyond the configured horizon | `validate_event_reminder` | Event rejected (`"invalid: not_before too far in future"`) | `test_reminder_not_before_max_safe_integer_rejected_too_far_in_future` in `e2e_event_reminder.rs` |
| `expiration` at or before `not_before` | `validate_event_reminder` | Event rejected (`"invalid: expiration before not_before"`) | `test_reminder_rejected_expiration_before_not_before`, `test_reminder_rejected_expiration_equal_to_not_before` in `e2e_event_reminder.rs` |
| Client cannot decrypt, or decrypts to non-JSON / unknown-status / malformed-target plaintext | `decryptReminder` / `parseReminderContent` | Reminder dropped client-side (returned `null`, filtered out of the list); no relay-visible effect | `parseReminderContent_invalid_json_returns_null`, `parseReminderContent_unknown_status_returns_null`, `parseReminderContent_malformed_target_returns_null` in `desktop/src/features/reminders/lib/reminderService.test.mjs` |
| Unauthenticated read of `kind:30300` | REQ handler auth-state check | Subscription closed, `"auth-required: ..."` | `crates/buzz-relay/src/handlers/req.rs:83-93` (WS-level behavior; no dedicated e2e test opened for this specific unauthenticated-30300 case) |
| Authenticated read of another author's reminders | `author_only_filters_authorized` / per-event `is_author_only_event` | Subscription closed (single-kind) or reminder silently omitted (mixed-kind), `"restricted: ..."` | `test_other_user_cannot_query_reminders_http`, `test_other_user_subscription_closed_for_author_only_kind_ws`, `test_mixed_kind_filter_omits_other_authors_reminders_ws`, `test_fanout_isolation_other_user_does_not_receive_reminder` in `e2e_event_reminder.rs` |
| Relay pod publish-after-claim failure during scheduled due delivery | scheduler's claim/publish/release sequence | Claim released so a later tick (any pod) retries; no reminder is lost, but delivery may be delayed | `crates/buzz-relay/src/main.rs:855-887` (no dedicated e2e test opened for this specific race path) |
| Snooze/complete/cancel racing a stale local copy | NIP-01 replacement ordering (highest `created_at`, tie-break lowest `id`) | The relay's stored head always reflects the latest valid replacement regardless of client race; a client acting on a stale copy still only ever produces another valid replacement | `test_reminder_replacement_semantics` in `e2e_event_reminder.rs` |

Two rows above name the relevant source but not a dedicated automated test
opened while writing this node -- that gap is named here rather than
implied to be covered.

## Verification

- **Relay-side unit tests, tag-envelope validation:** `crates/buzz-relay/src/handlers/ingest.rs`'s
  `#[cfg(test)]` module covers `validate_not_before` (zero, typical
  timestamp, max-safe-integer boundary, leading zero, empty, non-digit) and
  `validate_event_reminder` (accepted-with-`not_before`, accepted-missing-`not_before`,
  duplicate/malformed `not_before`, `d`-tag cardinality, `expiration`
  ordering).
- **Desktop unit tests, client-side parsing:** `desktop/src/features/reminders/lib/reminderService.test.mjs`
  covers `parseReminderContent` (valid target, note-only, done/cancelled
  statuses, invalid JSON, non-object, unknown status, missing target-and-note,
  malformed target, unknown-field tolerance) and `parseNotBefore`.
- **Desktop unit tests, due-detection logic:** `desktop/src/features/reminders/lib/reminderFilters.test.mjs`
  covers `isDue`, `countDue`, `dueSince` (including the strict watermark
  lower bound and inclusive `now` upper bound), and `groupReminders`
  (overdue/today/upcoming bucketing, cancelled reminders never surfaced).
- **End-to-end, write-path validation:** `test_reminder_accepted_with_valid_not_before`,
  `test_reminder_accepted_missing_not_before`, `test_reminder_accepted_with_expiration_after_not_before`,
  and the rejection-path tests named in the table above, in
  `crates/buzz-test-client/tests/e2e_event_reminder.rs`.
- **End-to-end, author-only read boundary:** `test_author_can_query_own_reminders_http`,
  `test_other_user_cannot_query_reminders_http`, `test_author_can_count_own_reminders_http`,
  `test_other_user_cannot_count_reminders_http`, `test_author_can_subscribe_to_own_reminders_ws`,
  `test_other_user_subscription_closed_for_author_only_kind_ws`,
  `test_mixed_kind_filter_omits_other_authors_reminders_ws`,
  `test_ws_search_isolation_other_user_cannot_find_reminder`, in the same
  file.
- **End-to-end, replacement and fan-out:** `test_reminder_replacement_semantics`
  and `test_fanout_isolation_other_user_does_not_receive_reminder`, in the
  same file.

`e2e_event_reminder.rs`'s tests are marked `#[ignore]` -- this repository's
convention for tests that require a live relay plus Postgres and Redis, run
via `just test` rather than `just test-unit` -- so this document links them
as representative coverage rather than asserting they were executed while
authoring it.

## Scope and omissions

**This document covers** the `kind:30300` reminder lifecycle as NIP-ER
specifies and as the relay, desktop client, and mobile client actually
implement it: creation, the relay's public-tag validation gate, the
author-only read/subscribe boundary, scheduled due delivery and its
cross-pod claim/release mechanics, client-side local due-detection, and
the snooze/complete/cancel/delete state transitions.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What "reminders" let a user or agent do, stated at a product-stakeholder level (the capability-level "what") | A capability-shaped sibling node under `capabilities/reminders/`, not yet drafted at this revision |
| The general, durable CLI/HTTP/WebSocket surface a reminder is exposed through, independent of this one scenario | An interface-shaped node, not yet drafted at this revision |
| The standing container/component structure of the relay and desktop app that this flow's steps move between, beyond what `architecture-containers-relay` and `architecture-containers-desktop` already document | Those two nodes, referenced from this one's front matter |
| The full CLI reminder subcommand surface, if `buzz-cli` exposes one, was not searched for while writing this node | Not yet verified |
| NIP-40 `expiration`'s own general semantics, used here only for the two terminal-state cleanup timestamps | Not documented in this corpus at this revision |
| NIP-09 deletion's own general semantics, used here only for the reminder hard-delete case | Not documented in this corpus at this revision |

**Expected but not verified when this node was written:**

- **No dedicated automated test was located, or was opened, for the
  unauthenticated single-kind-30300 REQ closing with `auth-required`, nor
  for the scheduler's own publish-failure/claim-release race.** Both
  behaviors are named directly from the source they are implemented in
  (see the *Failure, abort, and rollback* table), not from a passing test
  observed during authoring.
- **Mobile's reminder lifecycle beyond event construction was not read in
  depth.** `mobile/lib/shared/reminders/reminder_service.dart` was opened
  far enough to confirm wire-shape parity with desktop (same kind, same
  NIP-44 self-encryption pattern, same tag construction), but its own
  due-detection, notification, and snooze/complete/cancel UI flow were not
  independently traced the way desktop's were.
- **Whether `buzz-cli` exposes a reminder subcommand was not checked.**
  AGENTS.md's own convention is that agent-facing operations live in
  `buzz-cli`; this node makes no claim either way about reminders there.
- **The relay's Redis pub/sub cross-pod fan-out mechanism itself (`buzz-pubsub`)
  was read only far enough to confirm the scheduler calls `publish_event`
  with `EventTopic::Global`; the general fan-out container/mechanism is
  not independently documented by this node.**

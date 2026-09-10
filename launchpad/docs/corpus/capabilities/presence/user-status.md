---
id: capabilities-presence-user-status
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "buzz-core's kind.rs defines KIND_USER_STATUS = 30315 with a doc comment identifying it as NIP-38 user status (general, music, or custom d-tag), parameterized replaceable (NIP-33, the 30000-39999 range) and stored globally (channel_id = NULL) as user-owned personal data, not channel-scoped."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:67-70"
  - statement: "buzz-sdk's build_user_status(text, emoji) trims both inputs, rejects text over 64KiB via check_content, always writes a `[\"d\", \"general\"]` tag, adds an `[\"emoji\", ...]` tag only when the trimmed emoji is non-blank, and its own doc comment states that blank text with no emoji is the shape clients read as \"no status\" (kind 30315 is parameterized-replaceable, so a fresh event with an empty d:general coordinate simply replaces whatever status existed)."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:1716-1730"
  - statement: "buzz-sdk's own unit tests confirm build_user_status's shape directly: text and emoji both land on the signed event (d:general, emoji tag) and are trimmed; a blank emoji is omitted rather than written as an empty tag; emoji survives when text is blank; the fully-blank \"clear\" shape carries empty content and exactly one tag (d:general); and text over 64*1024 bytes is rejected with SdkError::ContentTooLarge."
    entry_class: FACT
    evidence:
      - "crates/buzz-sdk/src/builders.rs:4119-4162"
  - statement: "buzz-relay's ingest.rs required_scope_for_kind maps KIND_USER_STATUS to Scope::UsersWrite (the same scope as profile and contact-list writes), and is_global_only_kind includes KIND_USER_STATUS among the kinds where a stray client-supplied `h` tag is ignored for scoping purposes -- a user-status event is never channel-scoped even if one is present on the wire."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:345-353"
      - "crates/buzz-relay/src/handlers/ingest.rs:529-548"
  - statement: "buzz-relay's own ingest.rs unit tests assert exactly this: user_status_requires_users_write_scope, user_status_is_global_only, and user_status_does_not_require_h_tag."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:3465-3480"
  - statement: "buzz-db has no user-status-specific module or table. Storage is entirely the crate's generic NIP-33 parameterized-replaceable-event handling: event.rs extracts a `d` tag for any kind in the 30000-39999 range (empty string if absent, per NIP-33), and lib.rs's replace_parameterized_replaceable path atomically replaces the row keyed on (kind, pubkey, d_tag) globally -- channel_id is deliberately not part of the key -- rather than any code path naming kind 30315 or user status directly."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/event.rs:167-190"
      - "crates/buzz-db/src/store/replaceable.rs:546-556"
  - statement: "buzz-cli exposes `users set-status --text <text> --emoji <emoji> --clear` (mutually exclusive `--clear` vs. `--text`/`--emoji`, `--text` required unless `--clear`), whose dispatch substitutes empty text and no emoji when `--clear` is set and otherwise passes the given text/emoji through unchanged; cmd_set_status builds the event via buzz_sdk::build_user_status and submits it over the same authenticated HTTP bridge path as an ordinary (non-ephemeral) write, unlike set-presence which publishes over the raw WebSocket connection."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:876-888"
      - "crates/buzz-cli/src/commands/users.rs:516-530"
      - "crates/buzz-cli/src/commands/users.rs:561-570"
  - statement: "buzz-cli's own tests assert the `--clear` conflict rules directly: set_status_clear_rejects_text_and_emoji and set_status_requires_text_or_clear."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs:2145-2167"
  - statement: "buzz-cli has no command to read another user's status. cmd_get_users (the only read path in crates/buzz-cli/src/commands/users.rs) queries exclusively kind:0 profile-metadata events; a repository-wide search for KIND_USER_STATUS in crates/buzz-cli finds only the import and the two set-status call sites, no read/query usage."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/users.rs:15-55"
      - "grep_case_insensitive('KIND_USER_STATUS', path='crates/buzz-cli/**') -> crates/buzz-cli/src/lib.rs:15 (import), crates/buzz-cli/src/commands/users.rs:525 (build_user_status call), run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "Desktop's user-status feature (desktop/src/features/user-status/hooks.ts) queries the `d:general` coordinate of kind:30315 via relayClient.fetchEvents for a snapshot (useUserStatusQuery, a 2-minute focused-poll backstop) and separately subscribes to live kind:30315/d:general deltas with no backfill (useUserStatusSubscription -> relayClient.subscribeToUserStatusUpdates), merging whichever value has the newer created_at into a shared React Query cache keyed [\"user-status\", ...pubkeys]; useSetUserStatusMutation publishes through relayClient.publishUserStatus and optimistically writes the same cache before the server round-trip completes."
    entry_class: FACT
    evidence:
      - "desktop/src/features/user-status/hooks.ts:1-96"
      - "desktop/src/features/user-status/hooks.ts:168-199"
  - statement: "Desktop's relayClientSession.ts publishUserStatus builds the event with only a `[\"d\", \"general\"]` tag plus an optional `[\"emoji\", ...]` tag -- it never writes an `expiration` tag -- and subscribeToUserStatusUpdates subscribes live-only (`limit: 0`) with no historical backfill."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts:381-403"
  - statement: "Desktop's parseUserStatusEvent (hooks.ts) extracts only pubkey, text (event.content), emoji (from an `emoji` tag) and updatedAt (created_at) from a kind:30315 event; it does not read or check any `expiration` tag."
    entry_class: FACT
    evidence:
      - "desktop/src/features/user-status/hooks.ts:24-39"
  - statement: "Desktop's SetStatusDialog.tsx offers five fixed presets (In a meeting, Commuting, Out sick, Vacationing, Working remotely, each pairing text with an emoji), an emoji picker for a custom glyph or `:shortcode:`, a text input that saves on Enter, a Save button disabled until either field is non-empty, and a Clear-status button shown only when a status already exists -- with no duration or expiration control of any kind."
    entry_class: FACT
    evidence:
      - "desktop/src/features/user-status/ui/SetStatusDialog.tsx:1-196"
  - statement: "Desktop's StatusEmoji.tsx renders a status emoji from its stored string: a value matching `^:([^:\\s]+):$` is looked up against the community's custom-emoji set and rendered as an `<img>` through the media proxy if a match is found; any other value (a native glyph, or an unmatched `:shortcode:`) renders as plain text -- the component's own doc comment states every display site renders through it so the shortcode-to-image resolution cannot drift across call sites."
    entry_class: FACT
    evidence:
      - "desktop/src/features/user-status/ui/StatusEmoji.tsx:1-67"
  - statement: "Mobile's UserStatus model (mobile/lib/features/profile/user_status.dart) parses a NIP-40 `expiration` tag from a kind:30315 event into an `expiresAt` unix-seconds field (and a clamped `expirationDateTime` getter), and exposes `isExpiredAt(now)`; the model's own doc comment identifies the type as \"a user's NIP-38 status (kind:30315, d=general)\"."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/user_status.dart:1-55"
  - statement: "Mobile's UserStatusNotifier.setStatus accepts an optional `expiresAt: DateTime`, and when given one, adds an `[\"expiration\", \"<unix-seconds>\"]` tag to the published event alongside `d:general` and the optional `emoji` tag; UserStatusCacheNotifier and UserStatusNotifier both call `_scheduleExpiration`, which arms a local Timer that, on firing, sets that provider's own in-memory state to null (clearing the *displayed* status) without publishing any new event to the relay -- the underlying kind:30315 event on the relay is left exactly as submitted, unmodified and unreplaced."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/user_status_provider.dart:68-161"
      - "mobile/lib/features/profile/user_status_cache_provider.dart:195-236"
  - statement: "Mobile's UserStatusCacheNotifier applies the same `isExpiredAt` filtering to every other tracked user's status it fetches or receives over its live subscription (lines 113/117/180/183), not only to the current user's own status, so an expired status is hidden from mobile's own rendering of another participant regardless of who set it."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/user_status_cache_provider.dart:100-190"
  - statement: "Desktop never sets, reads, or displays an `expiration` tag on a kind:30315 event (its build path in relayClientSession.ts omits it entirely, and its parse path in hooks.ts does not extract it), while buzz-cli's `set-status` command and buzz-sdk's build_user_status accept no expiration input either -- expiration is a mobile-client-only feature, both to set and to honor."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/shared/api/relayClientSession.ts:381-403"
      - "desktop/src/features/user-status/hooks.ts:24-39"
      - "crates/buzz-cli/src/lib.rs:876-888"
      - "crates/buzz-sdk/src/builders.rs:1716-1730"
      - "mobile/lib/features/profile/user_status_provider.dart:68-161"
    confidence: 0.85
  - statement: "Because mobile's expiration handling only clears local UI state and never republishes an event, a status set with an expiration on mobile remains visible, unexpired, to a desktop client (or the CLI, or any other reader) reading that same kind:30315 event directly from the relay after the mobile-side deadline has passed, since desktop never evaluates the expiration tag at all."
    entry_class: INFERENCE
    evidence:
      - "mobile/lib/features/profile/user_status_provider.dart:143-161"
      - "desktop/src/features/user-status/hooks.ts:24-39"
    confidence: 0.75
  - statement: "buzz-relay's only NIP-40 `expiration`-tag handling found in a repository-wide search of crates/buzz-relay is scoped to event-reminder validation (an ordering check that `expiration` must be strictly after a reminder's own `not_before` tag) -- no generic expiration-driven purge, hide, or rejection mechanism for arbitrary event kinds, including kind:30315, was found."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/ingest.rs:1762-1828"
      - "grep_case_insensitive('expiration', path='crates/buzz-relay/src/**') -> only event-reminder validation and its own tests, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "crates/buzz-test-client/tests/e2e_user_status.rs (all `#[ignore]`, requiring a running relay) exercises: acceptance of a kind:30315 event, retrievability via a kind+author REQ filter, NIP-33 replacement (a second event on the same d-tag replaces the first, confirmed by querying back exactly one surviving event), independent coexistence of two different d-tag coordinates (\"general\" and \"music\") under the same author, and NIP-33 stale-write protection (an older-timestamped event on the same d-tag does not replace a newer one already stored)."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_user_status.rs:1-273"
  - statement: "desktop/tests/e2e/profile-custom-emoji-status.spec.ts contains a Playwright test, \"profile popover renders a custom emoji status as an image\", verifying StatusEmoji's shortcode-to-image resolution end to end in the mock-bridge desktop app."
    entry_class: FACT
    evidence:
      - "desktop/tests/e2e/profile-custom-emoji-status.spec.ts:24"
  - statement: "mobile/test/features/profile/set_status_sheet_test.dart and mobile/test/features/profile/user_status_provider_test.dart contain widget/unit tests covering the set-status sheet's duration picker (including \"opens with an out-of-range remote expiration\" and \"clamps an existing custom date to the Android picker range\") and the provider's expiration scheduling (including \"ignores an out-of-range expiration in the shared cache scheduler\")."
    entry_class: FACT
    evidence:
      - "mobile/test/features/profile/set_status_sheet_test.dart:14-196"
      - "mobile/test/features/profile/user_status_provider_test.dart:10-132"
  - statement: "capabilities-presence-presence (a sibling capability node documenting online/away/offline presence, kind:20001/40902) exists only on the unmerged branch task/806-presence at the time this node was authored -- it is absent from origin/launchpad's corpus tree -- so it is not a valid relationships target for this node; that same unmerged node's own body already names \"NIP-38 user status (kind:30315)\" as a related-but-separate capability it deliberately does not fold in, which is the boundary this node completes from the other side."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus/capabilities/presence') -> no such path, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
      - "git_show('68cbb95295d1c76809b5f1595411bbe87d5deede:launchpad/docs/corpus/capabilities/presence/presence.md') -> body's Boundary and Scope-and-omissions sections both list \"NIP-38 user status (kind:30315)\" as a separate, not-yet-drafted sibling"
  - statement: "Issue #808's definition of done requires this node to state the capability and primary actors/outcomes, define behavioral rules/constraints/variants, link major flows/interfaces/data/platform implementation, and link verification demonstrating the capability."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#808 definition of done"
---

# User status: capability

Buzz lets a user or agent publish a short, self-described status -- free text and an
optional emoji, shown as the "status line" on their profile -- and lets every other
participant read it. The primary actor is the account setting its own status (a human
on desktop or mobile, or an agent via `buzz-cli`); every other participant who views
that account's profile or profile card is the reader. Unlike presence (online/away/
offline, an automatic signal derived from connection activity), a user status is
always explicit: nothing sets or changes it except the account's own deliberate write,
and it persists until that account writes a new one or clears it -- it does not expire
on its own the way presence does, except on mobile's own client-local display, which
this node documents as a platform variant below.

## Maturity

**Shipped**, with one platform-specific variant. The event kind, its replacement
semantics, and read/write support are wired end to end: the shared kind definition
(`crates/buzz-core/src/kind.rs`), the SDK builder (`crates/buzz-sdk/src/builders.rs`),
the relay's scope and channel-scoping rules (`crates/buzz-relay/src/handlers/ingest.rs`),
generic NIP-33 storage in `buzz-db` (no user-status-specific code exists there), a CLI
write-only command (`crates/buzz-cli`), a full desktop read/write UI
(`desktop/src/features/user-status/`), and a mobile read/write UI that additionally
supports an optional self-expiring duration (`mobile/lib/features/profile/`). The
expiring-duration feature is mobile-only, both to set and to honor -- see *Behavioral
rules, constraints and variants* below.

## Behavioral rules, constraints and variants

- **One coordinate in active use: `d:general`.** Every writer in this repository
  (buzz-cli, desktop, mobile) always writes `d:general`, and every reader filters on
  it. NIP-38 itself permits other `d` values (the shared kind doc comment mentions
  "music" as an example, and the relay/e2e test coverage confirms multiple independent
  `d`-tag coordinates coexist under the same author at the protocol level), but no
  shipped Buzz surface reads or writes anything other than `general`.
- **Blank text and no emoji is "clear," not "empty."** Because kind 30315 is NIP-33
  parameterized-replaceable, publishing a fresh event on `d:general` with empty content
  and no `emoji` tag is exactly how every surface (SDK builder, CLI `--clear`, desktop's
  clear button, mobile's `clearStatus()`) represents "no status" -- there is no separate
  delete/tombstone shape.
- **Text and emoji are independent; either alone is a valid status.** A caller may set
  emoji with no text (kept exactly as given) or text with no emoji (the emoji tag is
  simply omitted, never written as blank) -- confirmed by both the SDK's own unit tests
  and desktop's Save button, which enables on either field being non-empty.
  A status emoji is a bare string, not a companion-URL pair the way message reactions
  are: desktop's `StatusEmoji` component resolves a `:shortcode:` value against the
  community's custom-emoji set at render time and falls back to plain text for a native
  glyph or an unresolvable shortcode.
- **Global, not channel-scoped, and always the account's own `UsersWrite` scope.**
  The relay treats kind:30315 as global user-owned data (like a profile or contact
  list) rather than message content: it maps to `Scope::UsersWrite`, and a stray `h`
  tag on the wire is ignored for scoping purposes rather than binding the status to a
  channel.
- **Two different transports for the write, deliberately.** Presence (kind:20001) is
  ephemeral and is only accepted over an authenticated WebSocket connection; user
  status (kind:30315) is an ordinary parameterized-replaceable write and goes through
  the same HTTP-bridge submit path as any other stored event. `buzz-cli`'s
  `set-presence` and `set-status` subcommands reflect this split at the transport
  level, not just in which event kind they build.
- **Write-only on the CLI.** `buzz-cli` can set or clear a status but has no command
  to read another account's status; the only CLI read of user data queries kind:0
  profile metadata, never kind:30315. An agent working through `buzz-cli` alone can
  publish a status but cannot query one back.
- **Mobile-only expiring duration, and it is a purely local UI behavior.** Only
  mobile's set-status sheet offers a duration control (1 hour / 8 hours / 1 day / 1
  week / a custom date), which is encoded as a NIP-40 `expiration` tag on the published
  event. When that deadline passes, mobile's own provider clears its *local* displayed
  state for that status -- both for the current user's own status and for any other
  tracked user's cached status -- but it never republishes a clear event to the relay.
  Desktop's build and parse paths, buzz-cli's `set-status`, and the SDK's
  `build_user_status` all ignore the `expiration` tag entirely (neither writing nor
  reading it), and no generic expiration-driven purge exists in the relay itself (the
  only `expiration`-tag handling found there is scoped to a different feature,
  event-reminder ordering validation). The practical consequence: a status set with an
  expiration on mobile can still read as active, unexpired, to a desktop client or the
  CLI reading the same event directly from the relay after mobile's own deadline has
  passed -- expiration is enforced only by whichever mobile client evaluates it
  locally, not by the relay and not by desktop.
- **NIP-33 replacement and stale-write protection apply exactly as they do to any
  other parameterized-replaceable kind**, verified end to end against a live relay: a
  newer event on the same `(kind, pubkey, d_tag)` replaces an older one, and an
  older-timestamped event does not replace a newer one already stored.

## Boundary

This node does not describe:
- **Presence (online/away/offline, kind:20001/40902)** -- an automatic, connection-
  derived signal on a wholly different transport (ephemeral WebSocket-only) and
  storage mechanism (Redis with a TTL, never Postgres). It is a related but distinct
  capability, not folded into this node. See the sibling capability node for presence
  (unmerged at the time of writing -- see *Relationships* below).
- **How Postgres stores parameterized-replaceable events in general** -- kind:30315
  uses the same generic NIP-33 machinery every other kind in the 30000-39999 range
  uses; `buzz-db` has no code path specific to user status. An architecture-level node
  documenting that generic mechanism, if one exists, is the right place for it, not
  here.
- **The interface surfaces (CLI, REST) that expose this capability, as command/route
  catalogues in their own right** -- this node cites the specific `set-status`
  subcommand and the relay's write path as evidence the capability exists and is
  reachable, not as an exhaustive interface reference.
- **Custom emoji as a feature in its own right** (the `:shortcode:` resolution
  `StatusEmoji` performs) -- that mechanism is shared with message reactions and other
  surfaces; this node only describes how a status value is interpreted when rendered,
  not how the community's custom-emoji set itself is managed.
- **How the running system is operated** -- deployment, monitoring, or incident
  response for the relay paths this capability depends on.

## Major flows, interfaces and platform implementation

- **Data:** one Nostr event kind, kind:30315 (NIP-38, parameterized replaceable,
  `d:general`), defined in `crates/buzz-core/src/kind.rs`.
- **Interfaces:**
  - `buzz-cli users set-status --text <text> --emoji <emoji> --clear`
    (`crates/buzz-cli/src/commands/users.rs`, `crates/buzz-cli/src/lib.rs`) -- write
    only, submitted over the authenticated HTTP bridge.
  - The relay's generic `POST /events` (submit) and `POST /query`/WebSocket REQ (read)
    paths, with no kind:30315-specific HTTP route -- read/write for this capability
    rides the same generic Nostr bridge every other event kind uses.
- **Platform implementation:**
  - Event construction and validation: `buzz-sdk`'s `build_user_status`
    (`crates/buzz-sdk/src/builders.rs`).
  - Scope and channel-scoping rules: `buzz-relay`'s ingest handler
    (`crates/buzz-relay/src/handlers/ingest.rs`).
  - Storage: `buzz-db`'s generic NIP-33 parameterized-replaceable-event path
    (`crates/buzz-db/src/store/event.rs`, `crates/buzz-db/src/store/replaceable.rs`) -- no
    user-status-specific module exists.
  - Desktop: `desktop/src/features/user-status/` (query/subscription/mutation hooks,
    the set-status dialog, and status-emoji rendering).
  - Mobile: `mobile/lib/features/profile/` (`user_status.dart`,
    `user_status_provider.dart`, `user_status_cache_provider.dart`,
    `set_status_sheet.dart`) -- the only platform implementing the expiring-duration
    variant.

## Verification

- `crates/buzz-sdk/src/builders.rs`'s unit tests for `build_user_status` (text/emoji
  round-trip, trimming, blank-emoji omission, emoji-without-text, the fully-blank
  clear shape, and the 64KiB content-size rejection).
- `crates/buzz-relay/src/handlers/ingest.rs`'s unit tests confirming kind:30315 maps to
  `UsersWrite` scope, is treated as global-only, and does not require an `h` tag.
- `crates/buzz-cli/src/lib.rs`'s unit tests confirming `--clear` conflicts with
  `--text`/`--emoji` and that a bare `set-status` invocation (no `--clear`, no `--text`)
  is rejected.
- `crates/buzz-test-client/tests/e2e_user_status.rs` (`#[ignore]`, requires a running
  relay) -- acceptance, retrievability, NIP-33 replacement, multi-`d`-tag coexistence,
  and stale-write protection, all against a real relay instance.
- `desktop/tests/e2e/profile-custom-emoji-status.spec.ts` -- a Playwright test
  confirming a custom-emoji status renders as an image in the profile popover.
- `mobile/test/features/profile/set_status_sheet_test.dart` and
  `mobile/test/features/profile/user_status_provider_test.dart` -- widget/unit
  coverage of the duration picker and expiration scheduling, including out-of-range
  and clamped-date edge cases.

## Relationships

Declared: none.

**Checked, not assumed.** `git ls-tree` against `origin/launchpad` at the recorded
revision shows the `launchpad/docs/corpus/capabilities/` directory does not exist yet
on that branch, so `capabilities-presence-presence` -- the sibling node documenting
presence, which this node's *Boundary* section distinguishes itself from -- is not a
valid relationships target: it exists only on the unmerged branch `task/806-presence`.
No architecture node inspected (`architecture-containers-postgres`) discusses NIP-33
parameterized-replaceable storage specifically enough to warrant a `references` edge
without restating content this node already attributes directly to `buzz-db`'s source.
The first moment either of those becomes true -- presence merges to `origin/launchpad`,
or an architecture node is found or written that actually documents NIP-33 storage --
is the moment to revisit this section, not a reason to invent an edge now.

## Scope and omissions

**This node covers** user status as a capability: what it lets an account do, its
current maturity including the mobile-only expiring-duration variant, the behavioral
rules and constraints that hold (or deliberately differ) across every surface, the
major flow/interface/data/platform implementation it touches, and the verification
that demonstrates it works.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Presence (online/away/offline) as a capability | `capabilities-presence-presence` (unmerged at the time of writing) |
| Generic NIP-33 parameterized-replaceable storage mechanics in Postgres | an architecture-level node, if one exists or is later written |
| The CLI's or REST bridge's command/route surface in general | an interface-shaped node for `buzz-cli` or the relay's HTTP bridge, if one exists |
| Custom-emoji shortcode management as its own capability | a custom-emoji-shaped node, if one exists |
| How the relay/Postgres/CLI/desktop/mobile are operated or deployed | the `operations` corpus surface |

**Expected but not verified when this node was written:**
- **No live run against a real relay was performed for this node.** The
  `crates/buzz-test-client/tests/e2e_user_status.rs` suite is marked `#[ignore]`
  (requires a running relay) and was read, not executed, for this node.
- **Whether any open issue tracks unifying expiration handling across desktop, mobile,
  and the CLI** was not searched for; the cross-platform gap is recorded here purely
  from reading the three clients' own source, not from an issue search.
- **Whether NIP-38's "music" `d`-tag coordinate (or any coordinate besides `general`)
  is used anywhere outside test code** was checked only by searching Buzz's own
  clients (desktop, mobile, CLI) and the relay/e2e test suite; none of them write or
  read any coordinate other than `general` in shipped product code, but a broader
  search across every crate was not performed.

---
id: capabilities-notifications-notification-preferences
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "VISION.md states 'Zero is the default. You opt in to noise, not out,' and its Surfaces table gives Stream and Forum a 'Zero-notification default,' DMs 'URGENT only,' and Workflows 'Approvals only' -- the product-level intent this capability's per-category toggles and mutes exist to implement."
    entry_class: FACT
    evidence:
      - "VISION.md:15-29"
      - "VISION.md:131"
  - statement: "desktop/src/shared/constants/kinds.ts documents that kind 30078 is one NIP-78 application-specific-data kind reused for several distinct blobs distinguished only by their `d` tag -- 'read-state:<slotId>', 'channel-sections', 'channel-mutes', 'channel-stars', 'channel-sort', 'community-theme' -- so KIND_CHANNEL_MUTES is not a dedicated kind integer, it is kind 30078 read under the 'channel-mutes' d-tag specifically."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/constants/kinds.ts:44-51"
  - statement: "Desktop's ChannelMuteSyncManager (channelMutesSync.ts) publishes and reads the user's channel-mute map as a kind:30078, d-tag:'channel-mutes' event whose content is NIP-44 self-encrypted (nip44EncryptToSelf/nip44DecryptFromSelf); on publish it first fetches its own current remote blob, merges per-channel by the entry with the newer updatedAt (last-write-wins per channel, not whole-document), and only then publishes, debounced 2 seconds, so the preference is a synced, cross-device Nostr event rather than a device-local setting."
    entry_class: FACT
    evidence:
      - "desktop/src/features/sidebar/lib/channelMutesSync.ts:1-29"
      - "desktop/src/features/sidebar/lib/channelMutesSync.ts:57-83"
      - "desktop/src/features/sidebar/lib/channelMutesSync.ts:103-134"
      - "desktop/src/features/sidebar/lib/channelMutesStorage.ts:111-130"
  - statement: "The Flutter mobile app's ChannelMutesManager independently implements the same wire contract -- kind 30078 (EventKind.readState = 30078), d-tag 'channel-mutes', NIP-44 self-encryption via a derived conversation key, and the same newer-updatedAt-wins per-channel merge -- so a channel mute set on one platform is readable and mergeable on the other."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_mutes/channel_mutes_manager.dart:126-165"
      - "mobile/lib/features/channels/channel_mutes/channel_mutes_manager.dart:173-201"
      - "mobile/lib/shared/relay/nostr_models.dart:26"
  - statement: "Thread-level muting (a user muting one specific thread rather than a whole channel) is tracked separately from channel mutes, in a device-local store keyed 'buzz-thread-muted.v1' with no relay publish or cross-device sync anywhere in its read/write path."
    entry_class: FACT
    evidence:
      - "desktop/src/features/channels/useUnreadChannels.ts:85"
      - "desktop/src/features/channels/useUnreadChannels.ts:212"
      - "desktop/src/features/channels/useUnreadChannels.ts:284"
      - "desktop/src/features/channels/useUnreadChannels.ts:517-530"
  - statement: "shouldNotifyForEvent (desktop) resolves whether one incoming event should alert the user in a fixed precedence: a broadcast-reply always notifies; a direct @mention of the current pubkey always notifies; a muted channel suppresses regardless of anything else; a root-less (non-reply) event notifies; a muted thread suppresses; otherwise a threaded reply notifies only if the user participated in, follows, or authored that thread's root."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/lib/shouldNotify.ts:28-76"
  - statement: "Desktop's NotificationSettings additionally gates alerting by event category, not just by channel or thread: eight SOUND_SLOTS (dm, mention, thread_reply, needs_action, job_accepted, job_progress, job_result, job_error) each carry an independent on/off toggle (slotAlertsEnabled) and an independent chosen sound (sounds); the four job_* slots are wired end-to-end (resolver, defaults, settings UI) but rendered disabled with a 'Coming soon' badge because, per the code comment, 'nothing emits the events yet -- buzz-acp publishes plain stream messages.'"
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/lib/sound.ts:26-58"
      - "desktop/src/features/settings/ui/NotificationSettingsCard.tsx:175-234"
  - statement: "NotificationSettings also carries desktopEnabled (master switch for native desktop alerts), notifyWhileViewing (also alert for DMs in the conversation currently open) and homeBadgeEnabled (Home sidebar badge for mentions/needs-action), all rendered in NotificationSettingsCard.tsx and persisted device-locally in window.localStorage under a per-pubkey key ('buzz-notification-settings.v2:<pubkey>') -- there is no relay event or cross-device sync for any of these four settings, unlike channel mutes."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/hooks.ts:38-63"
      - "desktop/src/features/notifications/hooks.ts:93-95"
      - "desktop/src/features/settings/ui/NotificationSettingsCard.tsx:83-113"
      - "desktop/src/features/settings/ui/NotificationSettingsCard.tsx:261-287"
  - statement: "DEFAULT_SLOT_ALERTS_ENABLED ships dm, mention, thread_reply and needs_action all defaulted to true (alerts on) out of the box, which is the opposite default from VISION.md's stated 'Zero is the default. You opt in to noise, not out' for Stream/Forum activity -- a real tension between the shipped default and the stated product intent, not a claim this node resolves."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/features/notifications/lib/sound.ts:96-105"
      - "VISION.md:131"
    confidence: 0.75
  - statement: "Channels backing an active huddle are force-silenced regardless of the user's own mute settings: AppShell.tsx passes the huddle-backing channel id set as silentChannelIds into the notification pipeline, and shouldPlayNotificationSound suppresses sound for any channel in that set -- a system-imposed suppression distinct from, and layered on top of, the user-controlled channel/thread mutes and per-slot toggles this node otherwise describes."
    entry_class: FACT
    evidence:
      - "desktop/src/app/AppShell.tsx:340"
      - "desktop/src/features/notifications/lib/sound.ts:131-136"
  - statement: "The mobile Settings page (SettingsPage in settings_page.dart) composes exactly four sections -- profile header, community, appearance, connection, plus a remove-community row -- and contains no notification, mute, or alert-preference section of any kind; the only notification-adjacent capability implemented on mobile is the channel-mute sync manager itself, reached from elsewhere in the channel UI rather than from Settings."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/settings/settings_page.dart:78-92"
  - statement: "Neither crates/buzz-relay/src/push_runtime.rs nor crates/buzz-relay/src/handlers/push_lease.rs contains any reference to kind 30078, to 'channel-mutes', or to the word 'mute' -- the NIP-PL push-wake matching path (architecture-flows-push-notification) evaluates only each lease's own client-supplied filters and gift-wrap self-#p authorization, so a channel or thread a user has muted while connected is not consulted when deciding whether to wake that user's device while disconnected."
    entry_class: FACT
    evidence:
      - "grep_recursive('30078|channel-mutes|mute', paths='crates/buzz-relay/src/push_runtime.rs,crates/buzz-relay/src/handlers/push_lease.rs') -> no matches, run 2026-08-31 at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
relationships:
  - type: references
    target: architecture-flows-push-notification
---

# Notification preferences: capability

Buzz lets a signed-in user control which activity actually interrupts them while
connected, at three independent granularities: per event **category** (direct
messages, @mentions, thread replies, needs-action items, agent job updates --
each with its own on/off toggle and chosen sound), per **channel** (mute a whole
channel), and per **thread** (mute one specific thread without muting its whole
channel). A master switch, a "notify while viewing" override for open DM
conversations, and a Home sidebar badge toggle sit alongside these. This is the
mechanism VISION.md's stated intent -- "Zero is the default. You opt in to
noise, not out." -- is implemented through, whether or not the shipped defaults
currently match that stated intent (see the evidence ledger and *Scope and
omissions* below).

## Maturity

**Channel-level mute: shipped on both desktop and mobile, and synced across a
user's devices.** Both clients read and write the same wire contract -- a
kind:30078 (NIP-78) event, `d`-tagged `channel-mutes`, whose content is NIP-44
self-encrypted -- and merge per-channel on whichever entry has the newer
`updatedAt`, so muting a channel on one device is reflected on another without
either device needing to be online at the same moment.

**Per-category alert/sound toggles, thread-level mute, the master switch,
"notify while viewing", and the Home badge toggle: shipped on desktop only, and
device-local.** None of these five publishes anything to the relay; they live
in `window.localStorage` (per-slot toggles and the master settings) or a
dedicated local store (thread mutes), keyed per pubkey, with no merge or sync
logic at all. Four of the eight alert categories (`job_accepted`,
`job_progress`, `job_result`, `job_error`) are wired through the resolver,
defaults and settings UI but render with a "Coming soon" badge, because the
event kinds they target are defined and queryable but nothing in this
repository currently emits them.

**Not present on mobile at all: a notification-preferences settings screen.**
Mobile's Settings page has no notification section; a mobile user can mute a
channel (from the channel UI, not Settings) but cannot see or change a
category toggle, a sound, the master switch, "notify while viewing", or the
Home badge -- because none of those five desktop-only settings has a mobile
counterpart to expose.

## Boundary

This node does not describe:
- **How a disconnected client is woken via Apple Push Notification service.**
  That is `architecture-flows-push-notification`'s territory, and per that
  node's own evidence, and confirmed independently here, the push-wake match
  path does not consult any of the preferences this node describes -- it
  matches only against the push lease's own filters. A user who has muted a
  channel while connected can still be woken for an event in that channel
  while disconnected; this node states that gap, it does not close it.
- **The general wire schema of kind 30078 / NIP-78 application data.** This
  node covers only the `channel-mutes` `d`-tag use of that kind; the sibling
  uses (`read-state:<slotId>`, `channel-sections`, `channel-stars`,
  `channel-sort`, `community-theme`) are separate concepts with their own
  bodies, not restated here.
- **How unread counts and badges are computed in general** (read markers,
  per-message vs. per-thread state). This node covers only the Home badge
  on/off *toggle*, not the counting logic it gates.
- **Whether a huddle-backing channel's forced silence is itself a user-facing
  capability.** It is mentioned only to distinguish a system-imposed
  suppression from the user-controlled preferences that are this node's
  actual subject.

## Relationships

- references: `architecture-flows-push-notification` -- the push-wake delivery
  flow this capability's preferences do **not** currently reach into (see
  *Boundary* and the push-runtime grep evidence above).

## Scope and omissions

**This node covers** the three preference granularities a Buzz user can set
(category, channel, thread), which of them sync across devices and which are
device-local, the desktop settings surface that exposes them, the fixed
decision precedence `shouldNotifyForEvent` applies to an in-app event, the
system-imposed huddle-silence rule layered on top of user preference, and the
gap between mobile's settings surface and desktop's.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The APNs push-wake delivery mechanics | `architecture-flows-push-notification` |
| The general NIP-78 (kind 30078) wire contract and its other `d`-tag uses | not yet a corpus node |
| Unread-count and read-marker computation in general | not yet a corpus node |
| The channel/thread mute UI's own interaction design | not yet a corpus node |

**Expected but not verified when this node was written:**
- **Whether the mismatch between VISION.md's "Zero is the default" and the
  shipped `DEFAULT_SLOT_ALERTS_ENABLED` (dm/mention/thread_reply/needs_action
  all default-on) is a deliberate, already-made product decision or an
  unresolved drift** was not established -- no VISION document, ADR, or issue
  addressing that specific default was found in the sources checked for this
  node. It is recorded above as an `INFERENCE` naming the tension, not
  resolved as either "intended" or "a bug."
- **Whether push-wake's disregard of mute state (see *Boundary*) is
  intentional or an unimplemented gap** was likewise not established from any
  source found while drafting this node -- `docs/nips/NIP-PL.md` was not
  independently re-read for this node beyond what
  `architecture-flows-push-notification` already cites.
- **Android-specific push/notification behavior** was not investigated;
  mobile evidence here covers the cross-platform Flutter/Dart mute manager
  only, not any platform channel or OS-level notification-permission code.

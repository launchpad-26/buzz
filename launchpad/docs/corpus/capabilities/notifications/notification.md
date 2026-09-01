---
id: capabilities-notifications-notification
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
  - statement: "VISION.md's own 'Surfaces' table carries a 'Default Notifications' column stating a per-surface default: Stream and Forum are 'Zero', DMs are 'URGENT only', and Workflows are 'Approvals only' -- a product-level policy for how loud each surface is allowed to be by default, not a per-user preference."
    entry_class: FACT
    evidence:
      - "VISION.md:15-22"
  - statement: "VISION.md's 'Home Feed & Notifications' section states 'Zero is the default. You opt in to noise, not out,' and describes the Home Feed as the personalized entry point (@mentions, items needing action, channel activity, agent updates), fan-out-on-read and assembled at query time, with agents reading the same feed via MCP rather than through a separate agent-only surface."
    entry_class: FACT
    evidence:
      - "VISION.md:129-135"
  - statement: "The desktop Notification Settings card exposes: a master 'Desktop alerts' switch; a DM-scoped 'Notify while viewing' switch (also alert for DMs in the conversation currently open); a master 'Sound' switch plus per-event-type ('slot') alert toggles and a sound picker per slot, some slots marked 'Coming soon' and hidden by default; and a 'Home badge' switch."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/NotificationSettingsCard.tsx"
  - statement: "Desktop notification preferences (desktopEnabled, homeBadgeEnabled, notifyWhileViewing, per-slot sounds and alert toggles) are persisted client-side only, to browser localStorage under a per-pubkey key ('buzz-notification-settings.v2:<pubkey>') -- not as a Nostr event, and not to any server-side record -- so today a user's notification preferences do not sync across devices or clients."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/hooks.ts:38"
      - "desktop/src/features/notifications/hooks.ts:93-95"
      - "desktop/src/features/notifications/hooks.ts:126-157"
  - statement: "Turning desktop alerts on requests OS-level Notification permission and forces desktopEnabled back to false if permission is not granted; a separate effect also disables desktopEnabled automatically whenever the OS permission state is later observed as denied or unsupported -- the feature disables itself rather than silently failing to alert."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/hooks.ts:236-243"
      - "desktop/src/features/notifications/hooks.ts:245-298"
  - statement: "Home-badge counting excludes a feed item whose channel is muted, unless the item's own category is 'mention' -- a mention in a muted channel still counts toward the badge, while other muted-channel activity does not."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/hooks.ts:479-484"
  - statement: "Desktop native notification delivery is implemented per-OS in the Tauri backend and documents a specific workaround: on GNOME 46+ (Ubuntu 24.04+, Fedora 41+), tauri-plugin-notification's default posting path drops the D-Bus connection immediately after posting, which dismisses the notification the instant it appears, so Buzz posts from a dedicated thread that holds the D-Bus connection open until the notification closes, forwarding the resulting click action back to the frontend."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/notifications.rs"
  - statement: "sendDesktopNotification treats a thrown Notification constructor as a delivery miss, not a crash: it logs a warning and returns false, and a subsequent call with a working backend still succeeds -- one failed alert does not disable the feature for later events."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/lib/desktop.test.mjs"
  - statement: "desktop/src/features/notifications/hooks.test.mjs carries unit tests for home-badge counting specifically: excluding thread activity already shown in a channel preview, excluding channel-counted high-priority items from the subtotal, counting non-DM thread-only rows, per-message and per-channel read-marker precedence, and counting locally-unread rows before channel exclusion."
    entry_class: FACT
    evidence:
      - "desktop/src/features/notifications/hooks.test.mjs"
  - statement: "Mobile's shouldNotifyForEvent treats a `broadcast` tag or a `p`-tag mention of the local user as unconditionally notify-worthy, checked and returned before the muted-channel and muted/participated/followed/authored-root-thread rules are evaluated -- so a broadcast or a direct mention is notify-worthy even in a muted channel, while an ordinary thread reply is suppressed by channel mute or thread mute unless the local user participated in, follows, or authored that thread."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/unread_badge/should_notify_for_event.dart"
  - statement: "No test file under mobile/test exercises shouldNotifyForEvent directly, as of the recorded revision -- searched by filename (*notify*, *should_notify*) and by grepping mobile/test for the symbol name, both with zero results."
    entry_class: FACT
    evidence:
      - "grep_recursive('shouldNotifyForEvent', paths='mobile/test') -> no matches, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "kind:44100 and kind:44101 are relay-signed 'notification' events for channel-membership add/remove, stored globally (no channel_id) with a p-tag naming the affected pubkey and an h-tag naming the channel -- a data event a client's feed/activity surface consumes to learn about a membership change, distinct from the alert/delivery capability (desktop/native alert, sound, badge, out-of-app push wake) this node documents; this node's scope does not extend to kind:44100/44101's own semantics."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/kind.rs:530-536"
  - statement: "As of the recorded revision, no file under mobile/lib or desktop/src matches kind:30350, push_lease, PushLease, App Attest, or apns (case-insensitive) -- independently confirming, at this node's own recorded revision, that neither the mobile nor the desktop client implements the NIP-PL push-lease/App-Attest client half of push notification delivery."
    entry_class: FACT
    evidence:
      - "grep_recursive('30350|push_lease|PushLease|App ?Attest|apns', paths='mobile/lib desktop/src', case_insensitive=true) -> zero matches, run against commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The merged corpus node architecture-flows-push-notification documents the shipped relay-side and gateway-side path that wakes an installed iOS client through APNs under NIP-PL when the client is disconnected: durable match-and-deliver via a Postgres-queued job, a fixed and content-blind reconnect payload (no relay-supplied byte, event id, or content ever enters it), and lossy/best-effort delivery -- the client always resyncs authoritative content afterward over ordinary authenticated REQ, never from the wake itself."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
  - statement: "The merged corpus node architecture-containers-push-gateway documents buzz-push-gateway as the standalone service that is the sole holder of APNs provider credentials, deliberately separated from the relay image so relays receive only opaque delegation capabilities, never a raw APNs device token or provider credential."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/push-gateway.md"
relationships:
  - type: references
    target: architecture-flows-push-notification
  - type: references
    target: architecture-containers-push-gateway
---

# Notifications: capability

The product's mechanism for telling a user (or an agent acting on their
behalf) that something needs their attention without requiring them to poll
for it -- across a spectrum from a silent in-app badge, to a native OS alert
while the app is running, to an out-of-app wake delivered through a platform
push transport while the client is disconnected. Buzz states this
capability's governing policy explicitly at the product level: **zero is the
default, and a user opts in to noise, not out**, with the exact default
varying by surface (`Zero` for Stream and Forum, `URGENT only` for DMs,
`Approvals only` for Workflows).

Primary actors: the pubkey-holding user (or the agent reading the same Home
Feed via MCP on their behalf) who is the recipient; the desktop/mobile client
that renders an alert, sound, or badge; the relay, which durably matches
accepted events against a user's active leases and authorization; and, for
the out-of-app wake, `buzz-push-gateway`, which holds the platform push
credentials the relay never sees. The outcome in every variant is the same
shape: the recipient learns something changed at the intensity their surface
and their own preferences allow, and any content they see is fetched from the
relay through their own authenticated read access -- never carried inside the
notification signal itself for the out-of-app case.

## Maturity

**In-app and native desktop alerting: shipped.** The desktop settings surface
(`NotificationSettingsCard.tsx`), its preference model and persistence
(`hooks.ts`), OS permission handling, per-OS native alert delivery
(`desktop/src-tauri/src/commands/notifications.rs`), and Home-badge counting
all exist as working code with unit test coverage
(`hooks.test.mjs`, `desktop.test.mjs`).

**Mobile in-app notify-worthiness: shipped as local logic, unverified by an
automated test.** `shouldNotifyForEvent` exists and is used for mobile's
unread-badge decisions, but no test file under `mobile/test` exercises it
directly as of the recorded revision.

**Out-of-app push wake (NIP-PL / APNs): server-side shipped, client-side not
built.** `architecture-flows-push-notification` and
`architecture-containers-push-gateway` (both merged) document a complete,
tested relay-and-gateway path. Independently re-checked for this node at its
own recorded revision: no file under `mobile/lib` or `desktop/src` implements
the client half (push-lease creation/rotation, App Attest enrollment). A
reader should not infer from this capability existing in the relay and
gateway that a real user's phone or desktop client can currently receive a
push wake.

**No corresponding VISION_PROJECTS.md status row.** Unlike several other
capabilities, VISION_PROJECTS.md's "Capability | Status" table carries no row
for notifications specifically; this node's maturity claims above are
therefore grounded directly in code and tests, not in a VISION status
marker.

## Behavioral rules, constraints, and variants

- **Zero-by-default, opt-in policy.** Stated at the product level in
  VISION.md, and reflected in code: desktop's own defaults ship
  `desktopEnabled: true` but every per-event-type ("slot") alert is something
  the user can turn off per row, and several slots ship `Coming soon` and are
  hidden until the user opts to reveal them.
- **Mute suppresses, but a mention or a broadcast overrides mute.** On
  desktop, a muted channel's activity does not add to the Home badge count
  *unless* the item's own category is `mention`. On mobile,
  `shouldNotifyForEvent` checks a `broadcast` tag and a direct `p`-tag mention
  *before* it ever checks channel or thread mute state, so both bypass mute
  entirely; an ordinary thread reply, by contrast, is suppressed by channel or
  thread mute unless the recipient participated in, follows, or authored that
  thread.
- **Permission-gated, and fails closed.** Desktop native alerts require OS
  notification permission; the client requests it when the user turns alerts
  on, and a later observed `denied`/`unsupported` permission state
  automatically flips the preference back off rather than silently
  continuing to fail.
- **A failed delivery attempt does not disable the feature.** A thrown
  `Notification` constructor is treated as one missed alert (logged, `false`
  returned), and the very next alert attempt with a working backend still
  succeeds.
- **Preferences are local and per-pubkey, not synced.** Desktop notification
  preferences live in browser `localStorage` keyed by pubkey; there is no
  Nostr event and no server-side record for them today, so switching devices
  or clients does not carry a user's notification preferences with them.
- **The out-of-app push wake is content-blind by construction.** Per
  `architecture-flows-push-notification`, the APNs payload is one fixed,
  compiled-in reconnect signal; no relay-supplied byte, event id, or message
  content is ever part of it, and delivery is lossy/best-effort -- the
  recipient's client always re-fetches authoritative content afterward over
  its own authenticated `REQ`, so a dropped or suppressed wake degrades
  latency, never confidentiality.
- **"Notification" is also used, elsewhere in this codebase, for a different
  concept.** `kind:44100`/`kind:44101` are relay-signed data events reporting
  a channel-membership add/remove -- consumed by a client's feed/activity
  surface as *content*, not a delivery/alert mechanism. This node's scope is
  the alert/delivery capability; it does not cover those event kinds' own
  semantics.

## Boundary

This node does not describe:

- **How the out-of-app push wake is built** -- the relay's durable
  match-and-deliver pipeline, the NIP-PL lease protocol, and the
  `buzz-push-gateway` container's App Attest/APNs boundary. See
  `architecture-flows-push-notification` and
  `architecture-containers-push-gateway` (both `references`d above).
- **The specific wire/interface contract each push-related concern uses** --
  App Attest enrollment, endpoint installation/rotation, the push-lease event
  shape, or a machine-checkable notification-preferences storage contract.
  Several sibling documents under `capabilities/notifications/` are planned
  to cover exactly these concerns (APNs, App Attest, endpoint installation,
  notification preferences, the push capability itself, push leases, and the
  push-notification flow one more time at capability-taxonomy depth); none
  of them is merged into the corpus as of this node's own recorded revision,
  so none is a valid `relationships` target yet, and this node does not
  re-derive their depth.
- **The step-by-step path any one notification takes.** The out-of-app push
  wake's own step-by-step flow is `architecture-flows-push-notification`'s
  territory, already `references`d. This node states that in-app alerting
  and Home-badge counting exist and their governing rules, not their
  step-by-step internals.
- **`kind:44100`/`kind:44101` membership-notification event semantics** --
  named above only to disambiguate the term "notification" as used elsewhere
  in this codebase, not described further here.
- **How the running push gateway is operated** (deployment, secrets,
  alerting) -- `docs/push-gateway-deployment.md`, cited by
  `architecture-containers-push-gateway`.

## Relationships

- `references`: `architecture-flows-push-notification` -- the out-of-app push
  wake's own trigger-to-delivery flow, already merged.
- `references`: `architecture-containers-push-gateway` -- the container that
  holds APNs credentials on the relay's behalf, already merged.

No `part-of`, `depends-on`, `supersedes`, or `implements` relationship is
declared: no broader "notifications" capability exists yet for this node to
sit under, no other corpus node depends on or is superseded by it, and this
is an instance node rather than a template, so `implements` toward
`corpus-template-capability` was considered and left out (the choice is
optional per that template and adds no information the node's own shape
doesn't already show).

## Scope and omissions

**This node covers** the notifications capability as a product-level
overview and taxonomy: what it is, its primary actors and outcome, its
current maturity per delivery surface (in-app/native desktop, mobile local
notify-worthiness, out-of-app push wake), the zero-by-default policy and the
mute/mention/broadcast override rules that hold across in-app and mobile
alerting, the permission-gating and fail-closed/fail-soft behavior of desktop
native alerts, the local-only/per-pubkey nature of today's preference
storage, and the disambiguation against the unrelated `kind:44100`/`44101`
membership-notification events.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The out-of-app push wake's own trigger-to-delivery mechanics | `architecture-flows-push-notification` |
| The push gateway container's responsibilities and boundary | `architecture-containers-push-gateway` |
| App Attest, endpoint installation/rotation, push-lease wire shape, a notification-preferences storage contract | Planned sibling documents under `capabilities/notifications/` -- not merged as of this node's recorded revision |
| Push gateway deployment, secrets, and alerting | `docs/push-gateway-deployment.md` |
| `kind:44100`/`kind:44101` membership-notification semantics | Not written yet |

**Expected but not verified when this node was written:**

- **Whether `shouldNotifyForEvent`'s rules are exercised by any automated
  test.** Searched by filename and by grepping `mobile/test` for the symbol
  name; both returned zero matches. The rules stated above (broadcast/mention
  bypass mute; ordinary replies gated by participation/follow/authorship) are
  read directly from the function's own source, not confirmed against a
  passing test.
- **Whether desktop's per-slot "Coming soon" alert types have a shipped event
  producer yet.** `NotificationSettingsCard.tsx` renders them behind a
  toggle-to-reveal control, but this node did not trace which, if any, event
  types those slots correspond to in the relay's kind registry.
- **Whether Android push (FCM) or any UnifiedPush profile has any client-side
  presence.** Only iOS/APNs was checked, following
  `architecture-flows-push-notification`'s own scope; this node makes no
  claim about Android push readiness in either direction.

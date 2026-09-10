---
id: platforms-mobile-navigation
type: platforms
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
  - statement: "No platforms-specific corpus template exists yet, so this node follows templates/component.md's shape (purpose, responsibility, public interface, dependencies in both directions, boundary, relationships, scope and omissions) even though that template itself prescribes type: implementation for its subject."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/component.md"
  - statement: "Sibling nodes authored under platforms/** in the same batch (Feature #614) have converged on type: platforms for documents in that directory, in preference to component.md's own type: implementation recommendation, because node.schema.json's type enum already carries platforms as one of PRD #602's named in-scope surfaces and a document about one platform's internal behavior fits it more directly than the implementation surface a template written for a single Rust crate assumed."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
  - statement: "mobile/pubspec.yaml declares no go_router dependency, and the app's single MaterialApp in mobile/lib/app.dart is built with one navigatorKey and navigated imperatively via Navigator.push/pop/maybePop/pushReplacement throughout the feature tree, rather than through a declarative router."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml"
      - "mobile/lib/app.dart:287"
      - "mobile/lib/app.dart:360-395"
  - statement: "The three top-level destinations (Home, Activity, Search) are switched by HomePage's own tabIndex widget state driving an IndexedStack, not by pushing or popping routes on the app's Navigator; only lazily-visited tabs (Activity, Search) are built at all, tracked by a visitedTabs set."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/home/home_page.dart:90-108"
      - "mobile/lib/features/home/home_page.dart:160-164"
      - "mobile/lib/features/home/home_page.dart:190-218"
  - statement: "DeepLinkDispatcher wraps the authenticated HomePage subtree with dispatchMessageLinks left at its default true, and separately wraps the pre-authentication PairingPage with dispatchMessageLinks: false, so a message/channel deep link is held rather than dispatched until the user is authenticated, while invite links are still processed pre-auth."
    entry_class: FACT
    evidence:
      - "mobile/lib/app.dart:379-393"
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:24-38"
  - statement: "parseBuzzDeepLink(Uri) is the single entry point that tries parseInviteDeepLink, then parseChannelDeepLink, then parseMessageDeepLink in order, returning the first non-null match or null for anything unrecognized; parseEntityDeepLink (buzz://repo|pr|issue permalinks) is a separate, not-navigable parser used for inline presentation rather than routing."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/deeplink/deep_link.dart:293-297"
      - "mobile/lib/shared/deeplink/deep_link.dart:315-354"
  - statement: "PendingDeepLinkNotifier (pendingDeepLinkProvider) subscribes to AppLinks().uriLinkStream (or a debug override) for buzz:// URI taps and to the pendingPushNotificationLink ValueNotifier for notification taps, and queues unresolved links FIFO in a Queue<BuzzDeepLink> so a later link never silently replaces an earlier undispatched one; consume() advances to the next queued link."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:23-50"
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:62-68"
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:99-105"
  - statement: "The native push bridge feeds pendingPushNotificationLink through two paths: installBuzzPushMethodHandler's 'notificationOpened' method-channel case for a warm tap while the app is running, and syncPendingBuzzPushNotificationResponse's 'takePendingNotificationResponse' call for a cold-start tap that iOS buffered before the Flutter method handler attached; both build a MessageDeepLink carrying a communityId, channelId and eventId from the native payload."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:104-137"
      - "mobile/lib/shared/push/push_bridge.dart:296-326"
  - statement: "For a MessageDeepLink carrying a communityId (a notification-originated link; canonical shared buzz://message links omit it because community IDs are device-local), DeepLinkDispatcher first calls pendingDeepLinkProvider's prepareCommunity, which switches the active community via communityListProvider.switchCommunity if the link's community exists but is not already active; a switch causes the community-scoped app subtree to remount and consume the still-parked link once its channels load, rather than the dispatcher navigating directly."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:71-97"
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:85-111"
  - statement: "_dispatchNavigableLink resolves a ChannelDeepLink or resolved MessageDeepLink's channelId against the currently loaded channelsProvider list; if channels have not loaded yet it returns without consuming the link (channelsProvider's own listener re-attempts dispatch once channels arrive), and if the channel ID is not found in the loaded list it shows a snackbar and consumes (drops) the link rather than leaving it queued forever."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:113-142"
  - statement: "_pushChannel dispatches by calling Navigator.of(context).push(MaterialPageRoute(builder: (_) => ChannelDetailPage(channel: ..., initialMessageId: ..., initialThreadRootId: ...))), landing every dispatched deep link on the single app-wide Navigator regardless of which HomePage tab is currently selected, since IndexedStack tab switching and Navigator route pushes are independent stacks."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:144-158"
  - statement: "ChannelDetailPage accepts optional initialMessageId and initialThreadRootId constructor parameters plus an InitialThreadRouteBehavior (push by default, or replaceCurrentRoute) that controls whether an automatically opened thread route sits on top of the channel route (Back returns to the channel) or replaces it (Back returns to whatever opened the channel)."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_detail_page.dart:243-265"
  - statement: "Inside ChannelDetailPage's message list, a useEffect keyed on initialThreadRootId finds the matching thread head among already-loaded messages, then in a post-frame callback guarded by ModalRoute.of(context)?.isCurrent (to avoid double-navigating if the channel route is no longer the active route) pushes or pushReplaces a MaterialPageRoute building a ThreadDetailPage, per the InitialThreadRouteBehavior passed in; a message-only deep link (no threadRootId) instead jumps the list to the target message index once it is found, tracked by a separate didJumpToInitialMessage guard."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_detail_page/message_list.dart:577-610"
  - statement: "Manual (non-deep-link) in-app channel navigation uses the same Navigator.of(context).push(MaterialPageRoute(... ChannelDetailPage)) shape as the deep-link dispatcher: openChannelLink() (used for inline channel mentions/links) and ChannelsPage's own channel-row tap handler both push ChannelDetailPage directly, with no involvement from pendingDeepLinkProvider or DeepLinkDispatcher."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channel_link_navigation.dart:8-38"
      - "mobile/lib/features/channels/channels_page.dart:260-262"
  - statement: "A small number of destinations that manage their own enter/exit transition (for example ProfileEditPage from the settings profile-photo flow) are pushed with immediatePageRoute(), a PageRouteBuilder with zero transition/reverseTransition duration, instead of the default MaterialPageRoute platform transition."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/widgets/immediate_page_route.dart"
      - "mobile/lib/features/settings/settings_page.dart:138-140"
  - statement: "architecture-containers-mobile documents the buzz:// deep-link URI shapes as one of the mobile container's inbound interfaces (message, invite/join, channel-only links, mirroring desktop's deep_link.rs), but does not describe how a parsed link is queued, matched against loaded channels, used to switch communities, or turned into a Navigator push -- that dispatch mechanism is this node's own subject and is not duplicated from the container node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "architecture-flows-push-notification documents the server-side push lease and delivery pipeline (buzz-relay, buzz-push-gateway, NIP-PL) but does not describe client-side notification-tap routing, so no relationship is declared toward it; the client-side half of that flow (installBuzzPushMethodHandler, pendingPushNotificationLink) is covered here instead."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
  - statement: "Tests exercising this dispatch pipeline exist at mobile/test/features/channels/deep_link_dispatcher_test.dart (dispatcher behavior against fake providers), mobile/test/shared/deeplink/deep_link_test.dart (parser shapes), and mobile/test/shared/deeplink/pending_deep_link_provider_test.dart (queueing and community preparation)."
    entry_class: FACT
    evidence:
      - "mobile/test/features/channels/deep_link_dispatcher_test.dart"
      - "mobile/test/shared/deeplink/deep_link_test.dart"
      - "mobile/test/shared/deeplink/pending_deep_link_provider_test.dart"
relationships:
  - type: part-of
    target: architecture-containers-mobile
---

# Mobile navigation and deep-link routing

This node documents how the Flutter mobile app moves the user between
screens: the single-`Navigator` route-stack model, how the three top-level
tabs are switched without touching that stack, and how a parsed `buzz://`
deep link or a tapped push notification is queued, matched against loaded
state, and turned into a concrete pushed route. It answers "how does a link
or tap actually land on a specific screen", not "what does a `buzz://` URI
look like" (that is `architecture-containers-mobile`'s Inbound interfaces
section) and not "what happens when the app is backgrounded and resumed"
(that is issue #1253's application-lifecycle subject, unmerged at the time of
writing).

## Responsibility

The mobile app has no declarative router (`go_router` is not a dependency).
`App` (`mobile/lib/app.dart`) builds one `MaterialApp` with one
`navigatorKey`, and every screen transition in the app -- opening a channel,
opening a thread, opening settings, editing a profile -- is an imperative
`Navigator.push`/`pop`/`pushReplacement`/`maybePop` call against that single
route stack. There is no per-tab or per-feature `Navigator`.

Sitting above that stack, the three primary destinations (Home, Activity,
Search) are not routes at all: `HomePage` holds a local `tabIndex` and
renders an `IndexedStack` over the three tab bodies, lazily building
Activity and Search only once they have been visited. Switching tabs never
pushes or pops anything on the app's `Navigator` -- it is pure widget state.
This means a deep-link-triggered `Navigator.push` (for example, opening a
channel) always lands on top of whichever tab is currently showing, because
the tab `IndexedStack` and the route stack are independent.

Layered on top of both, `DeepLinkDispatcher` is the component that turns an
already-parsed deep link (or a tapped push notification, funneled through the
same pipeline) into an actual navigation action once the data it needs --
loaded channels, an active community -- is available.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `DeepLinkDispatcher` | widget (`ConsumerStatefulWidget`) | Wraps a subtree; watches `pendingDeepLinkProvider` and (when `dispatchMessageLinks` is true) `channelsProvider`, and pushes the target screen once both are ready. `dispatchMessageLinks: false` holds message/channel links (used pre-authentication) while still processing invite links. | `mobile/lib/features/channels/deep_link_dispatcher.dart:24-38` |
| `pendingDeepLinkProvider` / `PendingDeepLinkNotifier` | Riverpod `NotifierProvider<PendingDeepLinkNotifier, BuzzDeepLink?>` | Holds the current link to dispatch (`state`) plus a FIFO queue of the rest; `open(Uri)` parses and enqueues, `consume()` advances to the next queued link, `prepareCommunity(link)` performs the community switch a notification-originated `MessageDeepLink` may require. | `mobile/lib/shared/deeplink/pending_deep_link_provider.dart:23-105` |
| `parseBuzzDeepLink(Uri)` | top-level function | Returns the first of `InviteDeepLink`, `ChannelDeepLink`, `MessageDeepLink` that matches, or `null`. The sole entry point `PendingDeepLinkNotifier.open` uses. | `mobile/lib/shared/deeplink/deep_link.dart:293-297` |
| `ChannelDetailPage({initialMessageId, initialThreadRootId, initialThreadRouteBehavior})` | widget constructor contract | The landing contract every navigation path into a channel uses: which message/thread to reveal, and whether an auto-opened thread route replaces or sits atop the channel route. | `mobile/lib/features/channels/channel_detail_page.dart:243-265` |
| `openChannelLink({context, ref, channelId, currentChannelId})` | top-level function | Manual (non-deep-link) channel navigation: resolves a channel ID against `channelsProvider` and pushes `ChannelDetailPage`, or shows a snackbar if the channel is not found. | `mobile/lib/features/channels/channel_link_navigation.dart:8-38` |
| `immediatePageRoute<T>({builder})` | top-level function | Zero-duration `PageRouteBuilder` for destinations (e.g. the settings profile-photo editor) that animate their own transition instead of using the platform's default route transition. | `mobile/lib/shared/widgets/immediate_page_route.dart` |
| `pendingPushNotificationLink` | `ValueNotifier<MessageDeepLink?>` | The join point between the native push bridge and the deep-link pipeline: set by a warm `notificationOpened` method-channel call or a cold-start `takePendingNotificationResponse` fetch, and consumed by `PendingDeepLinkNotifier`. | `mobile/lib/shared/push/push_bridge.dart:104-137` |

## Dependencies

**Depends on** (this routing mechanism requires these to work):

| Component | Why | Evidence |
|---|---|---|
| `app_links` package | Supplies `AppLinks().uriLinkStream`, the OS-level source of both cold-start and warm `buzz://` URI taps that `PendingDeepLinkNotifier` subscribes to. | `mobile/pubspec.yaml:43` |
| `hooks_riverpod` | `pendingDeepLinkProvider`, `channelsProvider`, `communityListProvider` and `activeCommunityProvider` are all Riverpod providers `DeepLinkDispatcher` and `PendingDeepLinkNotifier` read/watch/listen. | `mobile/lib/features/channels/deep_link_dispatcher.dart:1-12`, `mobile/lib/shared/deeplink/pending_deep_link_provider.dart:1-11` |
| `channelsProvider` (`mobile/lib/features/channels/channels_provider.dart`) | Provides the loaded channel list `_dispatchNavigableLink` and `openChannelLink` resolve a deep link's/tap's `channelId` against. | `mobile/lib/features/channels/deep_link_dispatcher.dart:119-127` |
| `communityListProvider` / `activeCommunityProvider` (`mobile/lib/shared/community/community_provider.dart`) | `prepareCommunity` reads and switches these for a notification-originated `MessageDeepLink` carrying a `communityId`. | `mobile/lib/shared/deeplink/pending_deep_link_provider.dart:71-97` |
| `inviteJoinProvider` (`mobile/lib/features/invites/invite_join_provider.dart`) | `_maybeDispatchInvite` prepares and confirms an `InviteDeepLink` through this provider before showing the invite-join sheet. | `mobile/lib/features/channels/deep_link_dispatcher.dart:160-220` |
| Native push bridge method channel (`mobile/lib/shared/push/push_bridge.dart`) | Supplies notification-tap targets (`MessageDeepLink`) from the iOS side into `pendingPushNotificationLink`, which `PendingDeepLinkNotifier` treats as another link source. | `mobile/lib/shared/push/push_bridge.dart:104-137,296-326` |

**Depended on by** (these require this routing mechanism):

| Component | Why | Evidence |
|---|---|---|
| `App` (`mobile/lib/app.dart`) | The composition root: wraps the authenticated `HomePage` in `DeepLinkDispatcher` and, pre-authentication, wraps `PairingPage` in the same dispatcher with `dispatchMessageLinks: false`, and starts `pendingDeepLinkProvider` watching immediately so a cold-start link survives until the authenticated UI can dispatch it. | `mobile/lib/app.dart:379-393` |
| `ChannelDetailPage`'s message list (`mobile/lib/features/channels/channel_detail_page/message_list.dart`) | Consumes `ChannelDetailPage`'s `initialThreadRootId`/`initialThreadRouteBehavior` contract to auto-open the target `ThreadDetailPage` once its messages are loaded. | `mobile/lib/features/channels/channel_detail_page/message_list.dart:577-610` |
| `channels_page.dart`, `channel_link_navigation.dart` | Both push `ChannelDetailPage` directly for manual (non-deep-link) navigation, using the same `Navigator.push(MaterialPageRoute(...))` shape the dispatcher uses. | `mobile/lib/features/channels/channels_page.dart:260-262`, `mobile/lib/features/channels/channel_link_navigation.dart:33-37` |

## Boundary

This node does not describe:
- **The `buzz://` URI shapes themselves** (what parameters a message, channel,
  invite, or entity link carries, and how each is validated) -- that is
  `architecture-containers-mobile`'s Inbound interfaces section and
  `deep_link.dart`'s own parsing functions; this node cites them but does not
  restate their grammar.
- **Application lifecycle transitions** (foreground/background, cold start vs.
  resume) -- issue #1253's `platforms/mobile/application-lifecycle.md`
  subject, unmerged at the time of writing.
- **Server-side push notification delivery** (lease acceptance, matcher,
  APNs dispatch) -- `architecture-flows-push-notification`'s subject. This
  node covers only the client-side consumption of a tap once native code has
  already decided to hand the app a target.
- **The native (Swift) implementation** of the push method channel or the
  Android/iOS platform link-registration configuration -- only the Dart-side
  contract each exposes was inspected (see *Scope and omissions*).
- **`MobileHuddleShell`'s own use of the shared root `navigatorKey`** for its
  huddle overlay -- confirmed to exist but not investigated as part of this
  node's routing subject.
- **Install/usage instructions for running the mobile app** -- `mobile/README.md`,
  when relevant, not restated here.

## Relationships

- `part-of`: `architecture-containers-mobile` -- this node documents one
  behavior area (routing/screen-stack mechanics) inside the mobile container
  that node already names as an "Inbound interfaces" surface without
  describing its dispatch mechanics.

No other relationship targets exist on `origin/launchpad` at the recorded
revision: `architecture-flows-push-notification` was checked and found to
cover a different (server-side) half of the same overall feature, not a
claim this node's own claims depend on being true, so no `depends-on` or
`references` edge is declared toward it. Issue #1253's sibling node does not
exist on `origin/launchpad` yet, so no relationship targets it either.

## Scope and omissions

**This node covers** the mobile app's single-`Navigator` route-stack model,
the `IndexedStack`-based top-level tab switch that sits outside that stack,
the deep-link/push-notification queueing and dispatch pipeline
(`PendingDeepLinkNotifier`, `DeepLinkDispatcher`), how a dispatched link is
matched against loaded channel/community state, how it becomes a concrete
`Navigator.push`, and the `InitialThreadRouteBehavior` mechanic controlling
whether an automatically opened thread route replaces or sits atop its
channel route.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `buzz://` URI grammar and validation rules | `architecture-containers-mobile` (container node) and `deep_link.dart` itself |
| Application lifecycle transitions | `#1257`'s sibling task `#1253` (`platforms/mobile/application-lifecycle.md`), unmerged at time of writing |
| Server-side push lease and delivery pipeline | `architecture-flows-push-notification` |
| Front-matter contract, node lifecycle, evidence classification | `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/schema/node.schema.json` |

**Expected but not verified when this node was written:**

- **Whether Android's native intent-filter configuration for `buzz://` links
  mirrors iOS exactly.** Only the shared Dart-side `app_links` stream
  consumption (`AppLinks().uriLinkStream`) was inspected; the platform-level
  Android manifest / iOS `Info.plist` registration was not opened.
- **The native (Swift) side of the push-notification method channel**
  (what calls `notificationOpened` and what native state
  `takePendingNotificationResponse` reads) was not inspected -- only the
  Dart-side contract in `push_bridge.dart`.
- **`MobileHuddleShell`'s interaction with the shared root `navigatorKey`**
  for its overlay was not investigated beyond confirming the class exists
  and is passed the same key as `MaterialApp`.

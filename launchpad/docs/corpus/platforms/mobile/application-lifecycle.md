---
id: platforms-mobile-application-lifecycle
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523 on the launchpad branch."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "node.schema.json's type enum has no platforms-specific value beyond the bare 'platforms' surface, and no platforms-specific template exists yet in launchpad/docs/corpus/templates/; this node instead adapts templates/component.md's required-sections shape (responsibility, public interface, dependencies in both directions, boundary statement, relationships, scope and omissions), which is the closest existing template to issue #1253's own Definition of Done bullets (states responsibility and interface/boundary; names dependencies and collaborators; links source implementation and tests; explains only component-level behavior)."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/component.md"
    confidence: 0.7
  - statement: "AppLifecycleNotifier (mobile/lib/shared/relay/app_lifecycle_provider.dart:11-50) is a Riverpod Notifier<AppLifecycleState>, not a StatefulWidget, carrying the doc comment 'Tracks the app lifecycle state and drives websocket connect/disconnect behavior for mobile battery efficiency.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/app_lifecycle_provider.dart:9-11"
  - statement: "AppLifecycleNotifier.build() wraps Flutter's AppLifecycleListener (onStateChange: _onStateChange) and separately subscribes to Connectivity().onConnectivityChanged, calling RelaySessionNotifier.onAppResumed() again whenever network is restored while state is already AppLifecycleState.resumed; both the listener and the connectivity subscription are disposed in ref.onDispose."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/app_lifecycle_provider.dart:16-33"
  - statement: "AppLifecycleNotifier._onStateChange maps AppLifecycleState.resumed to RelaySessionNotifier.onAppResumed(), maps both paused and detached to RelaySessionNotifier.onAppPaused(), and treats inactive and hidden as explicit no-ops with the inline comment 'Brief transition states -- no action.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/app_lifecycle_provider.dart:35-49"
  - statement: "RelaySessionNotifier.onAppPaused() (doc comment: 'Called by the app lifecycle provider when the app goes to background.') does not disconnect immediately: it records _backgroundedAt and starts a Timer for _backgroundGraceDuration, a 5-second constant, before running any pause work."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart:416-423"
      - "mobile/lib/shared/relay/relay_session.dart:107"
  - statement: "When the background grace timer fires, _pauseAfterCallbacks() awaits every callback registered via registerBeforePause (Future.wait), then calls _pauseNow(), which sets _paused, cancels the reconnect timer, cancels all in-flight history and pending requests with 'App moved to background', disconnects the socket, and sets session state to SessionStatus.disconnected."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart:425-443"
  - statement: "registerBeforePause (doc comment: 'Registers work that must settle before the background grace disconnect.') lets other subsystems register async cleanup that must complete before the socket is torn down; it returns an unregister callback."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart:409-414"
  - statement: "RelaySessionNotifier.onAppResumed() (doc comment: 'Called by the app lifecycle provider when the app returns to foreground.') clears _paused, and returns without reconnecting only if the app was backgrounded for less than the 5-second grace duration AND the session status is already SessionStatus.connected; otherwise it cancels any pending reconnect-backoff timer, resets the reconnect delay to its base value, and calls _connect(config)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart:445-467"
  - statement: "_connect() creates a new socket via the injected _socketFactory and, on successful connection, _handleConnected() sets session state to SessionStatus.connected and awaits _replayLiveSubscriptions(generation), so a resume-triggered reconnect also re-establishes prior live subscriptions."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_session.dart:469-502"
  - statement: "channels_provider.dart listens to appLifecycleProvider and calls refresh() whenever the state transitions to AppLifecycleState.resumed, with the inline comment 'Re-fetch when the app returns to foreground so channels created on another device while mobile was backgrounded appear immediately.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/channels_provider.dart:129-135"
  - statement: "PresenceNotifier (mobile/lib/features/profile/profile_provider.dart:293-298, doc comment: sends a 60s heartbeat while active and 'away' when backgrounded) watches appLifecycleProvider in build(): on AppLifecycleState.resumed it starts the heartbeat and publishes presence 'online'; on paused or detached it cancels the heartbeat and publishes 'away'."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/profile/profile_provider.dart:293-298"
      - "mobile/lib/features/profile/profile_provider.dart:321"
      - "mobile/lib/features/profile/profile_provider.dart:335-342"
  - statement: "BuzzPushAuthorizationStatusNotifier.build() listens to appLifecycleProvider and calls refresh() only on a transition into AppLifecycleState.resumed (previous != resumed && next == resumed), to re-check iOS notification authorization status after the user may have changed it in system Settings while the app was backgrounded."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:44-53"
  - statement: "MobileHuddleController registers _leaveForBackground as a before-pause callback via RelaySessionNotifier.registerBeforePause, and separately listens to appLifecycleProvider directly, calling _leaveForBackground() immediately on paused or detached -- independent of, and not gated by, the socket's 5-second background grace period."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/mobile_huddle_controller.dart:105-108"
      - "mobile/lib/features/channels/mobile_huddle_controller.dart:120-124"
  - statement: "read_state_provider.dart listens to appLifecycleProvider and calls unawaited(manager.flush()) on paused, detached, or hidden, persisting read-state before or during backgrounding rather than waiting on the socket's background grace timer."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/read_state/read_state_provider.dart:122-127"
  - statement: "mobile/lib/main.dart's runBuzzApp() calls installBuzzPushMethodHandler() and then awaits syncPendingBuzzPushNotificationResponse() before SharedPreferences load and runApp(), so a cold-start notification response is retrieved before the widget tree is built."
    entry_class: FACT
    evidence:
      - "mobile/lib/main.dart:13-17"
  - statement: "syncPendingBuzzPushNotificationResponse() returns immediately on any platform other than iOS (defaultTargetPlatform != TargetPlatform.iOS), otherwise invokes the native method 'takePendingNotificationResponse' on MethodChannel('buzz/push') and, if it parses to a link, sets pendingPushNotificationLink.value; the doc comment states native iOS 'buffers cold-start responses until Dart asks for them.'"
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:15"
      - "mobile/lib/shared/push/push_bridge.dart:98-101"
      - "mobile/lib/shared/push/push_bridge.dart:126-135"
  - statement: "installBuzzPushMethodHandler()'s 'notificationOpened' case handles a warm-launch tap (app already running, native bridge already attached): it parses call.arguments via _pushNotificationLink and, when non-null, sets pendingPushNotificationLink.value the same way the cold-start path does."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:296-320"
  - statement: "_pushNotificationLink() requires eventId, communityId, and channelId to all be non-empty strings in the native payload map, returning null otherwise, and on success constructs a MessageDeepLink(communityId, channelId, messageId: eventId)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:104-121"
  - statement: "PendingDeepLinkNotifier (doc comment: 'Holds supported deep links until they can be dispatched... Listens to [AppLinks.uriLinkStream], which delivers both the cold-start link... and links received while running.') additionally registers a listener on pendingPushNotificationLink in build() that enqueues any new value into the same FIFO queue used for app_links-based deep links, via the private _enqueue method."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:14-22"
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:32-40"
      - "mobile/lib/shared/deeplink/pending_deep_link_provider.dart:99-105"
  - statement: "DeepLinkDispatcher (doc comment: 'Routes pending buzz://message deep links into the channel view... Links are held (not dropped) while channels are still loading, so cold-start links dispatch as soon as the first channel fetch completes.') listens to both pendingDeepLinkProvider and channelsProvider, and for a MessageDeepLink calls prepareCommunity() (which may switch the active community) before pushing ChannelDetailPage on the enclosing Navigator with the link's initialMessageId."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:14-20"
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:67-83"
      - "mobile/lib/features/channels/deep_link_dispatcher.dart:85-111"
  - statement: "NIP-PL's push payload is 'a fixed transport-authored reconnect signal, never relay-supplied content, and the client fetches authoritative events over ordinary authenticated REQ after waking,' which is why a notification tap only carries enough structured data (eventId, communityId, channelId) to construct a navigation target, not message content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/push-notification.md"
  - statement: "mobile/pubspec.yaml declares connectivity_plus ^7.0.0 and app_links ^6.4.0 as dependencies, and declares no firebase_messaging or flutter_local_notifications dependency; push notification delivery and tap-handling on this platform is implemented entirely through the custom native MethodChannel('buzz/push') bridge in push_bridge.dart, not a cross-platform Flutter push plugin."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml:26"
      - "mobile/pubspec.yaml:43"
      - "mobile/lib/shared/push/push_bridge.dart:15"
  - statement: "mobile/test/shared/relay/relay_session_test.dart contains 'resume reconnects a stale connected session after a long pause' (calls onAppPaused(), advances a fake clock 5 minutes, calls onAppResumed(), and asserts a second socket was created and the first disposed) and 'resume keeps a connected session within the background grace period' (same shape but a 4-second advance, asserting no new socket and status remains connected)."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/relay/relay_session_test.dart:521-575"
      - "mobile/test/shared/relay/relay_session_test.dart:577-632"
  - statement: "Sibling task #1259 targets launchpad/docs/corpus/platforms/mobile/relay-connection.md, scoped to the relay-connection component (RelaySessionNotifier's own reconnect/backoff/subscription-replay mechanics) as a component distinct from this node's subject; at the time this node was written that file, and its corresponding node id, do not exist on origin/launchpad, so no relationships[] entry can target it yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1259 (unmerged task issue)"
relationships:
  - type: part-of
    target: architecture-containers-mobile
  - type: references
    target: architecture-flows-push-notification
---

# Application lifecycle (mobile)

This node documents one component of the Flutter mobile app: how it reacts to
OS-level foreground/background transitions (`AppLifecycleState`), including
the resume-triggered relay reconnect, the background-pause sequence, and how
a tap on a push notification reaches the app whether it was already running
or had to cold-start. It answers "what happens, in this app, when the OS
changes the app's lifecycle state or a notification launches it" -- not how
the mobile container fits into Buzz as a whole (see
`architecture-containers-mobile`) and not the relay-side reconnect or push
delivery mechanics those transitions trigger (see *Boundary* below).

## Responsibility

`AppLifecycleNotifier`, in
`mobile/lib/shared/relay/app_lifecycle_provider.dart`, is the single
component responsible for observing OS lifecycle state and translating it
into calls on other subsystems. Its own doc comment states this precisely:
*"Tracks the app lifecycle state and drives websocket connect/disconnect
behavior for mobile battery efficiency."* It is implemented as a Riverpod
`Notifier<AppLifecycleState>` wrapping Flutter's `AppLifecycleListener` --
consistent with this repository's ban on `StatefulWidget` for mobile state.
It is not itself a socket, a presence tracker, or a notification handler; it
is the single dispatch point those subsystems subscribe to or are called
from.

## Interface / boundary

`AppLifecycleNotifier` exposes `appLifecycleProvider`
(`NotifierProvider<AppLifecycleNotifier, AppLifecycleState>`), whose current
value is one of Flutter's five `AppLifecycleState` values. Its
`_onStateChange` handler treats those five states as three groups:

| State(s) | Action |
|---|---|
| `resumed` | Calls `RelaySessionNotifier.onAppResumed()` |
| `paused`, `detached` | Calls `RelaySessionNotifier.onAppPaused()` |
| `inactive`, `hidden` | No-op ("Brief transition states -- no action.") |

`build()` additionally subscribes to `Connectivity().onConnectivityChanged`
and calls `onAppResumed()` again whenever network is restored while the
notifier's own state is already `resumed` -- a resume-shaped reconnect
trigger that is not itself an OS lifecycle transition. Both the
`AppLifecycleListener` and the connectivity subscription are torn down in
`ref.onDispose`.

Any other provider or widget observes lifecycle transitions the same way:
`ref.listen(appLifecycleProvider, ...)` or `ref.watch(appLifecycleProvider)`.
There is no separate public API beyond that provider and
`RelaySessionNotifier.registerBeforePause` (see *Dependencies*).

### Resume (foreground)

`RelaySessionNotifier.onAppResumed()` clears the paused flag and skips
reconnecting only when both conditions hold: the app was backgrounded for
less than `RelaySessionNotifier`'s 5-second background-grace duration, *and*
the session is still `SessionStatus.connected`. In every other case it
cancels any pending reconnect-backoff timer, resets the reconnect delay to
its base value, and calls `_connect`, which on success (`_handleConnected`)
sets status to `connected` and replays live subscriptions. In short: a brief
backgrounding (app-switcher glance) is invisible to the relay session; a
longer one forces an immediate reconnect rather than waiting out any
exponential backoff already in progress.

### Pause (background)

`RelaySessionNotifier.onAppPaused()` does not disconnect immediately. It
records the time and starts a 5-second grace timer. When that timer fires,
every callback registered via `registerBeforePause` is awaited
(`Future.wait`) before the socket is actually torn down, in-flight
history/pending requests are cancelled with an `'App moved to background'`
error, and session status becomes `disconnected`. The 5-second grace exists
so a brief background/foreground cycle (e.g. a system alert, switching apps
briefly) does not tear down and immediately rebuild the socket.

## Dependencies

**Depends on** (this component requires these to do its job):

| Component | Why | Evidence |
|---|---|---|
| `RelaySessionNotifier` (`relay_session.dart`) | `onAppResumed()`/`onAppPaused()` are the two entry points this component calls on every lifecycle transition; it contains no socket code of its own | `mobile/lib/shared/relay/relay_session.dart:416-467` |
| `connectivity_plus` (`Connectivity`) | Detects network restoration to trigger a resume-shaped reconnect independent of OS lifecycle state | `mobile/pubspec.yaml:26` |
| Flutter's `AppLifecycleListener` / `AppLifecycleState` | The OS-level lifecycle signal this component wraps | `mobile/lib/shared/relay/app_lifecycle_provider.dart:17` |

**Depended on by** (other components that watch or call into this one):

| Component | Why | Evidence |
|---|---|---|
| `channels_provider.dart` | Re-fetches the channel list on resume | `mobile/lib/features/channels/channels_provider.dart:129-135` |
| `profile_provider.dart` (`PresenceNotifier`) | Starts/stops the presence heartbeat and publishes `online`/`away` | `mobile/lib/features/profile/profile_provider.dart:321,335-342` |
| `push_bridge.dart` (`BuzzPushAuthorizationStatusNotifier`) | Re-checks iOS notification authorization status on resume | `mobile/lib/shared/push/push_bridge.dart:44-53` |
| `mobile_huddle_controller.dart` | Registers a before-pause callback, and also leaves a huddle immediately on `paused`/`detached`, ahead of the socket's own grace period | `mobile/lib/features/channels/mobile_huddle_controller.dart:105-108,120-124` |
| `read_state_provider.dart` | Flushes unsaved read-state on `paused`/`detached`/`hidden` | `mobile/lib/shared/read_state/read_state_provider.dart:122-127` |

## Notification-launch handling

A notification tap reaches the app through a custom native bridge
(`MethodChannel('buzz/push')` in `push_bridge.dart`), not a cross-platform
Flutter push plugin -- `mobile/pubspec.yaml` declares no `firebase_messaging`
or `flutter_local_notifications` dependency.

- **Cold start** (app not running): `main.dart`'s `runBuzzApp()` calls
  `installBuzzPushMethodHandler()` and then *awaits*
  `syncPendingBuzzPushNotificationResponse()` before building the widget
  tree. That function is iOS-only; it asks native code for a buffered
  `'takePendingNotificationResponse'` and, if present, parses it into a
  `MessageDeepLink` and sets the module-level `pendingPushNotificationLink`.
- **Warm tap** (app already running): native code calls the installed method
  handler's `'notificationOpened'` case directly, which parses the same
  payload shape and sets the same `pendingPushNotificationLink`.
- Either way, `PendingDeepLinkNotifier` (a separate component; see
  *Boundary*) is listening on `pendingPushNotificationLink` and enqueues the
  link into its own FIFO queue, and `DeepLinkDispatcher` consumes that queue,
  optionally switches the active community, and pushes `ChannelDetailPage` on
  the `Navigator` once the target channel is available.
- A tapped notification's payload carries only `eventId`, `communityId`, and
  `channelId` -- enough to navigate, not message content. This matches
  NIP-PL's design, cited from `architecture-flows-push-notification`: the
  push payload is *"a fixed transport-authored reconnect signal, never
  relay-supplied content"*; the client fetches the real event after waking.

## Boundary

This node does not describe:

- **How `RelaySessionNotifier` itself reconnects** -- its socket factory,
  exponential backoff, and subscription-replay internals are sibling task
  #1259's subject (`platforms/mobile/relay-connection.md`, unmerged at the
  time of writing). This node names the two entry points it calls
  (`onAppResumed`, `onAppPaused`) and what triggers each, not how the
  reconnect itself is implemented.
- **How a push notification is produced and delivered** -- lease
  acceptance, matching, and the delivery worker are relay-side and already
  documented in `architecture-flows-push-notification`, referenced above
  rather than restated.
- **General deep-link parsing and community-switching logic** -- `app_links`
  URI parsing, the full `PendingDeepLinkNotifier`/`DeepLinkDispatcher`
  contract for non-notification links (e.g. shared `buzz://` links opened
  from outside the app), and `prepareCommunity`'s community-switch branches
  are a broader deep-linking concern than this lifecycle-scoped node covers;
  only the slice needed to show how a notification tap reaches the UI is
  described here.
- **The entire mobile container** -- responsibilities, dependencies, and
  architecture beyond application-lifecycle handling belong to
  `architecture-containers-mobile`.

## Relationships

- `part-of`: `architecture-containers-mobile` -- this node documents one
  lifecycle-handling component inside the mobile container that node
  describes at a higher level.
- `references`: `architecture-flows-push-notification` -- cited above for
  the NIP-PL payload-shape claim that explains why a notification tap
  carries only navigation coordinates, not content. This node does not
  restate that flow's relay-side mechanics.

## Tests

- `mobile/test/shared/relay/relay_session_test.dart:521-575` --
  `'resume reconnects a stale connected session after a long pause'`: calls
  `onAppPaused()`, advances a fake clock 5 minutes, calls `onAppResumed()`,
  and asserts a second socket was created and the first disposed.
- `mobile/test/shared/relay/relay_session_test.dart:577-632` --
  `'resume keeps a connected session within the background grace period'`:
  same shape with only a 4-second advance, asserting no new socket and
  status remains `connected`.
- Several feature-level test suites override `appLifecycleProvider` to drive
  their own lifecycle-gated behavior (presence, channel refresh, read-state
  flush, push-authorization refresh) rather than testing
  `AppLifecycleNotifier` directly; no dedicated
  `app_lifecycle_provider_test.dart` exists at the time of writing.

## Scope and omissions

**This node covers** how the mobile app's `AppLifecycleNotifier` observes OS
lifecycle transitions, what it calls into `RelaySessionNotifier` for resume
and pause (without documenting that notifier's own reconnect internals), the
other components that independently watch the same lifecycle state, and how
a notification tap -- cold-start or warm -- reaches navigable app state.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| `RelaySessionNotifier`'s reconnect/backoff/subscription-replay mechanics | `#1259` (`platforms/mobile/relay-connection.md`), unmerged at time of writing |
| Relay-side push lease acceptance, matching, and delivery | `architecture-flows-push-notification` |
| General deep-link parsing and community-switch semantics beyond notification routing | Not yet a corpus node |
| The mobile container's full architecture and responsibilities | `architecture-containers-mobile` |

**Expected but not verified when this node was written:**

- **Whether Android will ever get an equivalent native push bridge.** Today
  `push_bridge.dart`'s `syncPendingBuzzPushNotificationResponse()` returns
  immediately on any non-iOS platform, and no Flutter push plugin is
  declared in `pubspec.yaml`, so cold-start/warm notification-launch handling
  as described here is iOS-only. Whether Android has, or is planned to have,
  a parallel native implementation was not investigated.
- **Whether `AppLifecycleState.inactive`/`hidden` ever need lifecycle-driven
  behavior on Android or web form factors**, where those states can mean
  something different than a brief iOS transition. This node states only
  what the code does today (no-op for both), not whether that is correct
  for every platform Flutter targets.

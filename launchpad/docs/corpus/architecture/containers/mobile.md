---
id: architecture-containers-mobile
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "The mobile app is a Flutter client for Buzz, using Riverpod plus flutter_hooks for state management, with feature code isolated under lib/features/ and shared code under lib/shared/; feature modules must not import from other feature modules, only from shared/."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
      - "CLAUDE.md"
  - statement: "The mobile app's Nostr event-kind constants (EventKind in lib/shared/relay/nostr_models.dart) are documented as required to stay in sync with desktop/src/shared/constants/kinds.ts, so both clients speak the same wire vocabulary."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/nostr_models.dart"
      - "CLAUDE.md"
  - statement: "RelaySocket (lib/shared/relay/relay_socket.dart) is the low-level WebSocket connection: it connects to the relay's ws(s):// endpoint and performs NIP-42 challenge/response authentication using the community's nsec, sending and receiving JSON frames; it does not itself handle reconnection, which is RelaySessionNotifier's responsibility."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_socket.dart"
  - statement: "RelayConfig (lib/shared/relay/relay_provider.dart) derives both the WebSocket URL and the HTTP base URL used for media from a single configured baseUrl, which comes from the active Community's relayUrl, falling back to an Env.relayUrl compiled in via String.fromEnvironment when no community is active."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart"
  - statement: "RelayClient (lib/shared/relay/relay_client.dart) documents that in the pure-nostr architecture all data flow happens over the relay WebSocket, and that this HTTP client exists only to provide the base URL and shared http.Client for the media upload endpoint -- the one remaining HTTP path, because Blossom media uses kind:24242 NIP-98-style auth on a regular HTTP PUT."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_client.dart"
  - statement: "Outbound media flows use two distinct HTTP paths against the relay's Blossom-style endpoint: an authenticated PUT to /upload (with legacy fallback /media/upload) built in lib/shared/relay/media_upload.dart using a kind:24242 auth event, and authenticated GET requests for relay-hosted media URLs built in lib/shared/relay/media_auth.dart (MediaGetAuthService), which builds BUD-01 Blossom t=get auth headers and returns no headers at all for non-relay URLs so Buzz credentials are never sent to third-party hosts."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/media_upload.dart"
      - "mobile/lib/shared/relay/media_auth.dart"
  - statement: "A Community (lib/shared/community/community.dart) is the mobile app's unit of connected relay identity: id, display name, relayUrl, optional pubkey/nsec, a per-community sensitive-action policy, and an addedAt timestamp; CommunityStorage (lib/shared/community/community_storage.dart) persists the list of communities and the active community id in FlutterSecureStorage, including a one-time migration path from legacy single-community keys (buzz_workspaces, buzz_relay_url, buzz_token, buzz_pubkey, buzz_nsec)."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community.dart"
      - "mobile/lib/shared/community/community_storage.dart"
  - statement: "The app supports multiple communities, each backed by a different relay, matching the desktop app's community-switching model described for that container."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community.dart"
      - "CLAUDE.md"
  - statement: "Inbound deep links (buzz:// custom scheme, parsed in lib/shared/deeplink/deep_link.dart) mirror the desktop handler in desktop/src-tauri/src/deep_link.rs: a message link (buzz://message?channel=<uuid>&id=<hex>[&thread=<hex>]) references a thread, an invite link (canonical https://<relay>/invite/<code>, or buzz://join?relay=<ws(s)://relay>&code=<code> as an installed-app handoff from the web landing page) carries relay URL, code and an optional policy receipt, and a channel-only link (buzz://channel/<channel-uuid>) targets a single channel; required parameters missing or empty make the link invalid rather than partially handled."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/deeplink/deep_link.dart"
  - statement: "Device pairing (lib/features/pairing/) is a separate, ephemeral outbound WebSocket connection distinct from the app's community relay connection: PairingSocket (lib/features/pairing/pairing_socket.dart) is documented as single-use, disposed after the pairing session completes, and tolerates a target relay that sends no NIP-42 challenge (\"dedicated pairing relays may be open\")."
    entry_class: FACT
    evidence:
      - "mobile/lib/features/pairing/pairing_socket.dart"
  - statement: "The repository's crate map identifies buzz-pair-relay as an ephemeral sidecar relay purpose-built for NIP-AB device pairing, which is the counterpart the mobile pairing feature's ephemeral socket is designed to talk to."
    entry_class: INFERENCE
    evidence:
      - "mobile/lib/features/pairing/pairing_socket.dart"
      - "CLAUDE.md"
    confidence: 0.75
  - statement: "SensitiveActionAuthorizer (lib/shared/security/sensitive_action_authorizer.dart) wraps the local_auth plugin to gate sensitive actions -- identity export/sharing to desktop and enabling biometric protection -- behind on-device biometric or passcode authorization, returning a coarse DeviceAuthResult (success, cancelled, unavailable, lockedOut, failed) that deliberately discards OS-specific error detail."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/security/sensitive_action_authorizer.dart"
  - statement: "Cryptographic key material and community credentials (pubkey, nsec) are stored via flutter_secure_storage rather than plain SharedPreferences, so they use the OS-backed secure storage (Keychain on iOS, Keystore-backed EncryptedSharedPreferences on Android) rather than being written to unencrypted app storage."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart"
      - "mobile/pubspec.yaml"
  - statement: "The mobile app implements Nostr NIP-44 encryption and ECDH/HKDF key derivation locally (lib/shared/crypto/nip44.dart, ecdh.dart, hkdf.dart, nip_oa.dart) rather than delegating those primitives to the relay, so private message content is encrypted client-side before it leaves the device."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/crypto/nip44.dart"
      - "mobile/lib/shared/crypto/ecdh.dart"
      - "mobile/lib/shared/crypto/hkdf.dart"
      - "mobile/lib/shared/crypto/nip_oa.dart"
  - statement: "Mobile release builds are produced by a private Buzz mobile Buildkite pipeline from an exact, immutable mobile-vX.Y.Z-rc.N git tag published by scripts/mobile-release.sh; OSS CI in this repository cannot trigger that pipeline, there is no mobile release branch or stable tag alias, and iOS and Android can ship different candidate numbers for the same version (e.g. mobile-v0.5.0-rc.2 for iOS, mobile-v0.5.0-rc.3 for Android)."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "mobile/pubspec.yaml's version field (0.0.0+1) is deliberately kept as a non-release placeholder; the release pipeline injects the real version and build number rather than reading them from the checked-in pubspec.yaml."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
      - "mobile/pubspec.yaml"
  - statement: "The ecosystem map in this repository's AGENTS.md places buzz-releases as the repo that produces Block-signed desktop and mobile builds pushed to Artifactory, GitHub and the mobile release stores, downstream of this OSS source repository rather than inside it."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "Debug builds run from a git worktree get a worktree-scoped app identifier and display name (via scripts/mobile-worktree-overrides.sh, applied through just mobile-dev) so multiple worktrees can install side by side without clobbering each other's login state; release and profile builds always keep the production identity."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
      - "CLAUDE.md"
  - statement: "Quality gates for this container are dart format --output=none --set-exit-if-changed ., flutter analyze and flutter test (or just mobile-fmt / just mobile-check / just mobile-test from the repo root), and a file-size guard (mobile/scripts/check-file-sizes.mjs, run via just mobile-check) enforces a 1000-line-per-file ceiling on widget files."
    entry_class: FACT
    evidence:
      - "mobile/README.md"
      - "CLAUDE.md"
---

# Mobile Client Container

## Responsibility

The mobile container (`mobile/`) is the Flutter client for Buzz: a native iOS and
Android app that lets a user join one or more Buzz communities and participate in
their channels, threads, direct messages, and related NIP-29 community activity
from a phone. It is one of several client containers built against the same relay
protocol surface -- alongside the desktop app (`desktop/`) and the agent-facing CLI
(`crates/buzz-cli`) -- and, like desktop, is a *pure-Nostr* client: nearly all
read/write traffic is Nostr events over a WebSocket, with HTTP reserved for the
narrow set of paths that genuinely need it (media, in this container's case).

## Technology

- **Framework:** Flutter (Dart), targeting iOS and Android from one codebase.
- **State management:** Riverpod (`hooks_riverpod`) combined with `flutter_hooks`
  (`HookConsumerWidget`) for local widget state. The project convention is to avoid
  `StatefulWidget` entirely in favor of this pattern.
- **Structure:** feature code under `lib/features/` (one directory per surface --
  `activity`, `channels`, `forum`, `home`, `invites`, `pairing`, `profile`, `pulse`,
  `search`, `settings`), cross-cutting code under `lib/shared/` (`auth`, `community`,
  `crypto`, `custom_emoji`, `deeplink`, `emoji`, `mentions`, `read_state`, `relay`,
  `reminders`, `security`, `theme`, `utils`, `widgets`). Feature modules import only
  from `shared/`, never from each other, keeping the feature boundary enforced by
  convention rather than by a build-time gate.
- **Wire protocol:** the `nostr` package for event construction/signing, a hand-rolled
  `RelaySocket` over `web_socket_channel` for the relay connection, and local
  implementations of NIP-44 encryption and ECDH/HKDF key derivation
  (`lib/shared/crypto/`) rather than delegating those primitives elsewhere.
- **Secure storage:** `flutter_secure_storage` for community credentials (relay URL,
  pubkey, nsec) instead of plain `shared_preferences`; `local_auth` for
  device-level biometric/passcode gating of sensitive actions.

## Ownership boundary

This container owns the mobile client application only -- Flutter/Dart code under
`mobile/`, its iOS/Android platform shells, and its own build/release tooling. It does
not own the relay it talks to, the event kinds it consumes (defined centrally in
`buzz-core/src/kind.rs` and mirrored here in `EventKind`), or any server-side
behavior. Changes to wire-level contracts are made in the relay/core crates and
mirrored into this container's `EventKind` constants and models -- this document
does not duplicate that contract, only names where the mirror lives.

## Inbound interfaces

- **Deep links** (`lib/shared/deeplink/deep_link.dart`): the `buzz://` custom URL
  scheme, mirroring the desktop handler (`desktop/src-tauri/src/deep_link.rs`).
  Three forms are recognized: a message/thread link
  (`buzz://message?channel=<uuid>&id=<hex>[&thread=<hex>]`), an invite handoff
  (`buzz://join?relay=<ws(s)://relay>&code=<code>`, with the canonical form being an
  `https://<relay>/invite/<code>` web link), and a channel-only link
  (`buzz://channel/<channel-uuid>`). Malformed or incomplete links are rejected
  rather than partially resolved.
- **QR code scan** (`lib/features/pairing/pairing_qr_scanner*`): the user-initiated
  entry point for NIP-AB device pairing, feeding `PairingSocket`.
- **Relay push/subscription frames**: once connected, `RelaySocket` receives JSON
  frames (EVENT, OK, NOTICE, etc.) pushed over the open WebSocket from the relay it
  is authenticated to.

## Outbound interfaces and directly connected systems

- **Buzz relay, WebSocket (primary):** `RelaySocket` connects to the active
  community's `wsUrl` (derived from `RelayConfig.baseUrl`, itself sourced from the
  active `Community.relayUrl` or an `Env.relayUrl` compile-time default) and
  authenticates via NIP-42 challenge/response using the community's `nsec`. This is
  the channel for essentially all read and write traffic: notes, reactions, presence,
  typing indicators, membership, threads, and the rest of the NIP-29-scoped event
  surface represented in `EventKind`.
- **Buzz relay, Blossom media HTTP:** two authenticated HTTP paths against the same
  relay host -- `PUT /upload` (with legacy fallback `/media/upload`) for uploads,
  authorized with a signed kind:24242 event, and `GET` requests for relay-hosted
  media authorized with BUD-01 `t=get` headers built per-request by
  `MediaGetAuthService`. Non-relay media URLs never receive these headers, so Buzz
  credentials are not leaked to third-party image/video hosts.
- **buzz-pair-relay (inferred; see evidence ledger):** `PairingSocket` opens a
  separate, single-use WebSocket for NIP-AB device pairing that tolerates a target
  which sends no NIP-42 challenge, consistent with this repository's ephemeral
  pairing-sidecar relay described in `CLAUDE.md`'s crate map, though this document
  did not open `buzz-pair-relay`'s own source to confirm the endpoint directly.
- **Desktop app (via pairing flow):** the pairing feature exists to link a mobile
  identity to a desktop session; `SensitiveActionAuthorizer.authorizeIdentityAction`
  gates that hand-off behind on-device biometric/passcode confirmation
  ("Confirm sending your Buzz identity to desktop").

## Deployment implications

Mobile is released independently of this repository's normal CI. `just ci` and this
container's own `just mobile-check` / `just mobile-test` gate changes in OSS CI, but
shipping to users is a separate, private pipeline: `scripts/mobile-release.sh
candidate X.Y.Z` publishes an immutable `mobile-vX.Y.Z-rc.N` tag from the exact
remote `main` commit, which a private Buzz mobile Buildkite pipeline builds and signs
via the `buzz-releases` repository (see this repository's ecosystem table). There is
no mobile release branch, no stable tag alias, and no mobile GitHub Release; iOS and
Android can publish different candidate numbers for the same version. The checked-in
`mobile/pubspec.yaml` version (`0.0.0+1`) is a deliberate placeholder -- the release
pipeline injects the real version, not this file. Locally, debug builds run from a
git worktree get a worktree-scoped app identifier and display name so multiple
in-progress branches can be installed side by side without clobbering each other's
session.

## Data and security implications

- Community credentials (relay URL, pubkey, `nsec`) and any legacy single-community
  credentials are persisted through `flutter_secure_storage`, which is backed by
  Keychain (iOS) and Keystore-backed encrypted storage (Android) rather than plain
  app-local storage.
- NIP-44 message encryption and the ECDH/HKDF key derivation it depends on are
  implemented client-side in this container (`lib/shared/crypto/`); private content
  is encrypted before it leaves the device, not by the relay.
- Sensitive actions -- exporting/sharing identity to desktop during pairing, and
  enabling biometric protection itself -- are gated behind `local_auth` device
  authorization, with outcomes collapsed to a small `DeviceAuthResult` enum that
  intentionally discards platform-specific error detail rather than surfacing it to
  callers.
- Outbound media-fetch authorization headers are scoped to relay-hosted URLs only;
  the same request builder returns no headers for third-party hosts, which is the
  mechanism preventing credential leakage described above.

## Implementation paths

- `mobile/lib/shared/relay/` -- relay WebSocket connection, session/reconnect
  handling, Nostr event/model definitions (`EventKind`), Blossom media upload/auth.
- `mobile/lib/shared/community/` -- community model, secure storage, active-community
  provider.
- `mobile/lib/shared/deeplink/` -- `buzz://` link parsing.
- `mobile/lib/shared/crypto/` -- NIP-44, ECDH, HKDF.
- `mobile/lib/shared/security/` -- device-authorization gate for sensitive actions.
- `mobile/lib/features/pairing/` -- NIP-AB device pairing flow (QR scan, pairing
  socket, pairing crypto).
- `mobile/README.md` -- setup, run, and worktree-identity instructions for this
  container.
- `RELEASING.md` (§ Mobile) -- the release/build pipeline this container feeds into;
  not owned by this container's source tree.

This document links to those paths rather than restating their contents; see the
files themselves for current implementation detail.

## Scope and omissions

**Covers:** the mobile app's responsibility, technology choices, ownership boundary,
inbound/outbound interfaces, directly connected systems, and the deployment/security
implications visible from this container's own source and from `RELEASING.md`.

**Does not cover:** the relay-side implementation of any event kind or the Blossom
protocol itself (owned by `buzz-relay`/`buzz-core`); the desktop container's own
architecture (a sibling node, not yet written at this revision); per-feature detail
inside `lib/features/*` (each feature's internal design, if it warrants its own node,
is a separate task rather than folded in here); and the mobile app's test suite
structure, which was not inventoried beyond confirming `flutter test` is the gate.

**Expected but not verified at this revision:**

- `buzz-pair-relay`'s own source was not opened, so the claim that `PairingSocket`
  connects to it specifically is recorded as INFERENCE, not FACT -- it rests on this
  repository's crate-map description in `CLAUDE.md` plus the pairing socket's own
  documented tolerance for a no-challenge relay, not on reading `buzz-pair-relay`
  itself.
- No corpus sibling node existed at authoring time to relate this one to (no
  `architecture/` directory existed in the corpus tree before this change), so no
  `relationships` entries are declared. The desktop container, the relay container,
  and the event-kind registry are all natural future `references`/`depends-on`
  targets once those nodes exist.
- The mobile app's automated test coverage for the interfaces described here
  (`mobile/test/shared/relay`, `mobile/test/shared/community`, etc.) was located but
  not read in detail; this node describes what the code does, not how thoroughly it
  is tested.

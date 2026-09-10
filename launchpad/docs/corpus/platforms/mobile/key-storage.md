---
id: platforms-mobile-key-storage
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
  - statement: "The mobile app declares a dependency on flutter_secure_storage version ^10.0.0."
    entry_class: FACT
    evidence:
      - "mobile/pubspec.yaml:21"
  - statement: "CommunityStorage is the class responsible for persisting the mobile app's list of Community records (including each community's optional nsec private-signing-key field) and the currently active community id, using a FlutterSecureStorage instance -- created with no explicit AndroidOptions/IOSOptions/KeychainAccessibility, i.e. the plugin's own default configuration -- as its only backing store."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart:7-22"
  - statement: "CommunityStorage.loadAll persists the whole community list as one JSON-encoded blob under a single secure-storage key (buzz_communities) and the active community id under a second key (buzz_active_community_id), rather than one secure-storage entry per community or per secret."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart:8-9"
      - "mobile/lib/shared/community/community_storage.dart:26-70"
      - "mobile/lib/shared/community/community_storage.dart:108-111"
  - statement: "CommunityStorage.loadAll migrates two older on-device layouts the first time it runs: a prior buzz_workspaces/buzz_active_workspace_id pair (same shape, different key names), and, before that, an original flat single-community layout stored under buzz_relay_url/buzz_token/buzz_pubkey/buzz_nsec. Both migrations delete the legacy keys immediately after copying their values into the new buzz_communities entry."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart:11-17"
      - "mobile/lib/shared/community/community_storage.dart:30-67"
  - statement: "Community (the record CommunityStorage persists) carries an optional nsec field alongside id, name, relayUrl, pubkey and push-subscription state; toJson/fromJson omit the nsec key entirely from the serialized JSON when it is null rather than writing an explicit null."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community.dart:21-53"
      - "mobile/lib/shared/community/community.dart:109-160"
  - statement: "CommunityStorage's public interface is five async methods against the FlutterSecureStorage-backed store: loadAll() (read + migrate), save(Community) (upsert by id), remove(String id), loadActiveId()/saveActiveId(String)/clearActiveId() for the separately tracked active-community pointer."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart:26-99"
  - statement: "communityStorageProvider is a Riverpod Provider<CommunityStorage> that constructs exactly one CommunityStorage() (with the plugin default FlutterSecureStorage) shared across the app; every other community/auth/relay provider reads storage through this single provider rather than constructing its own CommunityStorage."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_provider.dart:76-78"
  - statement: "CommunityListNotifier.build (the Riverpod AsyncNotifier backing the community list UI) loads its initial state directly from CommunityStorage.loadAll(), and its removeCommunity path persists the storage-level removal (storage.remove(id)) before triggering any remote cleanup network I/O, making the local secure-storage mutation the operation's durability boundary."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_provider.dart:236-242"
      - "mobile/lib/shared/community/community_provider.dart:300-309"
  - statement: "RelayConfig (lib/shared/relay/relay_provider.dart) carries the nsec used to drive NIP-42 relay authentication and Nostr event signing, and its own doc comment states this explicitly: the two secrets the mobile app cares about are baseUrl and nsec. RelayConfigNotifier.build derives RelayConfig.nsec from the active community by watching activeCommunityProvider, which itself resolves through CommunityStorage."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart:7-19"
      - "mobile/lib/shared/relay/relay_provider.dart:80-93"
  - statement: "pubkeyFromNsec (lib/shared/relay/relay_provider.dart) derives the hex public key from a stored bech32 nsec on demand via Nip19.decode, and myPubkeyProvider exposes that derived pubkey to the rest of the app -- the public key is not independently persisted as the source of truth when a private key is present, it is computed from the stored nsec each time it is read."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/relay/relay_provider.dart:104-120"
  - statement: "AuthNotifier.build (lib/shared/auth/auth_provider.dart) reads communityStorageProvider directly (bypassing the community list/active providers, by its own comment, to avoid a circular dependency) to restore authentication state at app startup, and treats a community whose nsec fails _hasValidNsec as unauthenticated -- removing that community from storage and continuing to the next one -- rather than treating a missing/invalid signing key as merely degraded."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/auth/auth_provider.dart:17-52"
  - statement: "mobile/test/shared/community/community_storage_test.dart is a real, executable test suite (not merely a scaffold) that exercises CommunityStorage against a FakeSecureStorage in-memory fake, covering save/loadAll round-trips, active-id persistence, and all three migration paths (buzz_workspaces migration, legacy flat-key migration, and the no-legacy-data case) including the fact that legacy keys are deleted after a successful migration and that migration does not repeat on a second load."
    entry_class: FACT
    evidence:
      - "mobile/test/shared/community/community_storage_test.dart:91-317"
  - statement: "registerBuzzPushCommunitySnapshot (lib/shared/push/push_bridge.dart) is a separate code path that, on iOS only and only for communities with pushNotificationsEnabled, decodes each community's nsec to raw key bytes and sends them to native code over a MethodChannel so the notification service extension can verify push payloads; it is invoked from community_provider.dart's syncCommunitySnapshot flow, not from CommunityStorage itself."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/push/push_bridge.dart:254-294"
  - statement: "No file under mobile/lib constructs FlutterSecureStorage with a non-default AndroidOptions, AppleOptions/IOSOptions, or KeychainAccessibility argument; every call site (CommunityStorage and the unrelated BuzzPushLeaseRevocationStorage) uses the plugin's zero-argument default."
    entry_class: FACT
    evidence:
      - "mobile/lib/shared/community/community_storage.dart:21-22"
      - "mobile/lib/shared/push/push_lease_revocation_outbox.dart:168-169"
  - statement: "Because no call site configures platform-specific secure-storage options, the actual on-disk protection for the persisted nsec (Keychain on iOS/macOS, an encrypted keystore-backed store on Android, and weaker guarantees on desktop-class platforms the plugin also targets) is whatever flutter_secure_storage's own per-platform default implements, which this repository does not vendor or override -- so a claim about the specific cryptographic protection applied is an inference from the plugin's declared dependency and the absence of any overriding configuration, not a fact this repository's own source establishes."
    entry_class: INFERENCE
    evidence:
      - "mobile/pubspec.yaml:21"
      - "mobile/lib/shared/community/community_storage.dart:21-22"
    confidence: 0.6
  - statement: "architecture-containers-mobile is a corpus node id already present on origin/launchpad's corpus tree at the recorded revision, documenting the mobile app as a whole container; no platforms/** corpus node is merged yet, so this is the only existing node this task's node can validly declare a relationship toward."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/mobile.md"
  - statement: "Issue #1256's Definition of Done requires that the document 'explains only component-level behavior, not the entire containing platform,' 'states responsibility and well-defined interface/boundary,' 'names dependencies and collaborators,' and 'links source implementation and tests' -- language that maps onto the merged component.md corpus template's Required Sections (Responsibility, Public interface, Dependencies in both directions, Boundary, Relationships, Scope and omissions) rather than onto architecture-component.md's container-decomposition-with-diagram shape, even though no platforms-specific template exists yet to require either shape."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1256 definition of done, read against launchpad/docs/corpus/templates/component.md and launchpad/docs/corpus/templates/architecture-component.md"
  - statement: "This batch's sibling platforms/** document tasks (issues #1252-#1260, all children of parent Feature #614) use type: platforms as a working convention for corpus nodes whose path sits under platforms/**, since no platforms-specific template or accepted standard has settled the question yet."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#614 (parent Feature) batch dispatch convention, communicated by the orchestrating session for this batch"
relationships:
  - type: part-of
    target: architecture-containers-mobile
---

# Mobile: key storage

This node documents how the Buzz mobile app (Flutter) stores the user's
Nostr private signing key (`nsec`) on-device: which class owns that
responsibility, its public interface, what it depends on and who depends on
it, and its boundary against neighboring concerns. It answers the question
"where does the mobile app keep the user's private key, and what touches
it?" -- not the mobile app's full architecture (that is
`architecture-containers-mobile`) and not every consumer of a decoded signing
key throughout the app.

**No `platforms`-specific corpus template exists yet** (checked:
`launchpad/docs/corpus/templates/` has no `platforms-*.md` file, and no
`platforms/**` node is merged on `origin/launchpad` to follow as precedent).
Per `AGENTS.md`'s documented no-template path, this node is written directly
against `node.schema.json`, structured on the merged `component.md`
template's Required Sections (the closest existing fit to issue #1256's own
Definition of Done -- see the `TEAM_KNOWLEDGE` evidence entry above), and
expects a later task to reshape it once a `platforms`-specific template
lands.

## Responsibility

`CommunityStorage` (`mobile/lib/shared/community/community_storage.dart`) is
the class responsible for persisting the mobile app's list of `Community`
records -- each of which may carry the user's `nsec` (bech32-encoded Nostr
private key) alongside `pubkey`, `relayUrl` and push-subscription state --
plus the id of whichever community is currently active. It has no
class-level doc comment of its own; the responsibility above is drawn from
reading its full method surface, not from an authored summary, and that
absence is itself worth noting rather than papering over.

It stores the entire community list as a single JSON-encoded blob under one
secure-storage key (`buzz_communities`), and the active community id under a
separate key (`buzz_active_community_id`) -- not one secure-storage entry per
community or per secret.

Its only backing store is a `FlutterSecureStorage` instance
(`flutter_secure_storage: ^10.0.0`), constructed with no explicit
`AndroidOptions`, `AppleOptions`/`IOSOptions`, or `KeychainAccessibility`
argument anywhere in `mobile/lib` -- so every call uses the plugin's own
default per-platform backend. This repository does not vendor or override
that plugin's internal implementation, so the exact on-disk protection
(Keychain-backed on iOS/macOS, an encrypted keystore-backed store on
Android, and whatever the plugin does on its other supported platforms) is
inferred from the dependency declaration and the absence of overriding
configuration, not established as fact by anything in this repository's own
source.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `loadAll()` | `Future<List<Community>>` | Reads and JSON-decodes the `buzz_communities` blob; on first call with no such blob, migrates one of two older on-device layouts (see *Migration* below) before returning. | `mobile/lib/shared/community/community_storage.dart:26-70` |
| `save(Community)` | `Future<void>` | Upserts one community into the persisted list by `id`, then re-writes the whole `buzz_communities` blob. | `mobile/lib/shared/community/community_storage.dart:72-81` |
| `remove(String id)` | `Future<void>` | Removes one community by `id` from the persisted list, then re-writes the whole blob. | `mobile/lib/shared/community/community_storage.dart:83-87` |
| `loadActiveId()` / `saveActiveId(String)` / `clearActiveId()` | `Future<String?>` / `Future<void>` / `Future<void>` | Read/write/delete the separately tracked active-community pointer (`buzz_active_community_id`). | `mobile/lib/shared/community/community_storage.dart:89-99` |

`Community.toJson()`/`Community.fromJson()`
(`mobile/lib/shared/community/community.dart:109-160`) define the persisted
shape; `nsec` is omitted from the serialized JSON entirely when `null`
(`community.dart:109-122`), rather than written as an explicit null.

`pubkeyFromNsec` (`mobile/lib/shared/relay/relay_provider.dart:104-114`) is
the one place the stored `nsec` is decoded back to a hex public key on
demand -- the public key is not independently persisted as the source of
truth whenever a private key is present; it is derived from the stored
secret each time it is needed.

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `flutter_secure_storage` (`^10.0.0`) | Sole backing store for both the community-list blob and the active-id pointer; no in-repo alternative persistence path exists for these keys. | `mobile/pubspec.yaml:21` |

**Depended on by** (these require this component):

| Component | Why | Evidence |
|---|---|---|
| `communityStorageProvider` (`community_provider.dart`) | Riverpod `Provider<CommunityStorage>` constructing the single shared `CommunityStorage()` instance every other provider reads through. | `mobile/lib/shared/community/community_provider.dart:76-78` |
| `CommunityListNotifier` (`community_provider.dart`) | Loads its initial state from `loadAll()`; its removal path persists `storage.remove(id)` before any remote cleanup network I/O, making the local secure-storage write the operation's durability boundary. | `mobile/lib/shared/community/community_provider.dart:236-242,300-309` |
| `RelayConfigNotifier` (`relay_provider.dart`) | Derives `RelayConfig.nsec` -- the key driving NIP-42 relay auth and Nostr event signing -- from the active community, which resolves through this component. | `mobile/lib/shared/relay/relay_provider.dart:7-19,80-93` |
| `AuthNotifier` (`auth_provider.dart`) | Reads `communityStorageProvider` directly (bypassing the community list/active providers, per its own comment, to avoid a circular dependency) to restore auth state at startup, and removes any community whose `nsec` fails validation rather than treating it as merely degraded. | `mobile/lib/shared/auth/auth_provider.dart:17-52` |

Beyond these three direct collaborators, dozens of feature-level providers
read the *derived* `nsec` off `relayConfigProvider`/`RelayConfig` throughout
`mobile/lib/features/**` for event signing. Those are consumers of
`RelayConfig`, one layer removed from this component, and are not
enumerated here -- doing so would describe the entire platform's signing
surface rather than this one storage boundary, which the *Boundary* section
below states explicitly.

## Migration

`loadAll()` runs a one-time migration the first time it finds no
`buzz_communities` blob (`community_storage.dart:26-70`):

1. If a `buzz_workspaces`/`buzz_active_workspace_id` pair exists (an earlier
   version of the same list-of-communities shape, under old key names), it is
   decoded, re-saved under the new keys, and the old keys are deleted.
2. Otherwise, if the original flat single-community keys exist
   (`buzz_relay_url`, `buzz_token`, `buzz_pubkey`, `buzz_nsec`), a single
   `Community` is constructed from them (with
   `SensitiveActionPolicy.disabledByUser`), saved as the sole entry, marked
   active, and the four legacy keys are deleted.
3. Otherwise, an empty list is returned and nothing is written.

`mobile/test/shared/community/community_storage_test.dart:91-317` exercises
all three branches, including that legacy keys are actually deleted after a
successful migration and that a second `loadAll()` call does not re-run
migration.

## Boundary

This node does not describe:
- **The native iOS push-notification snapshot export.**
  `registerBuzzPushCommunitySnapshot`
  (`mobile/lib/shared/push/push_bridge.dart:254-294`) is a separate code path
  that, on iOS only and only for push-enabled communities, decodes a
  community's `nsec` to raw key bytes and sends them to native code over a
  `MethodChannel` for the notification service extension to use. It is a
  second export of key material outside this component's own
  `FlutterSecureStorage` boundary, invoked from `community_provider.dart`'s
  snapshot-sync flow rather than from `CommunityStorage` itself, and it is
  sibling issue #1258's (`platforms/mobile/push-integration.md`) subject, not
  this one's.
- **The ephemeral session secrets used during device pairing.**
  `mobile/lib/features/pairing/pairing_crypto.dart` derives short-lived
  session/SAS/transcript secrets for the NIP-AB pairing handshake; those are
  never written through `CommunityStorage` and are a distinct concept from
  the long-lived `nsec` this node covers.
- **The mobile app's full architecture.** How the mobile container fits
  Buzz's overall system, or its other internal building blocks, is
  `architecture-containers-mobile`'s subject, not this node's -- this node
  only names the one component decomposed here.
- **The dozens of feature-level consumers of the derived signing key.** See
  *Dependencies* above: this node stops at the components that read storage
  directly, not every downstream consumer of the value they expose.

## Relationships

- `part-of`: `architecture-containers-mobile` -- this component is a
  constituent part of the mobile container that node documents, and that id
  is confirmed present on `origin/launchpad`'s corpus tree at the recorded
  revision.
- No `depends-on` relationship is declared: `flutter_secure_storage` is a
  third-party package dependency, not a corpus node, and no other corpus
  node currently documents it.
- No `references` relationship toward a template node is declared. This
  node's shape is adapted from `component.md`'s Required Sections (see
  *Scope and authority* above) but carries `type: platforms`, not
  `component.md`'s own `type: implementation` recommendation -- see *Scope
  and omissions* for why that divergence is left open rather than resolved
  here.

## Scope and omissions

**This node covers** the `CommunityStorage` class: its responsibility, its
public interface, its sole storage dependency (`flutter_secure_storage`, at
plugin defaults), the components that depend on it directly
(`communityStorageProvider`, `CommunityListNotifier`, `RelayConfigNotifier`,
`AuthNotifier`), its three-generation key migration behavior, and its test
coverage.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The native iOS push-notification snapshot export of decoded signing-key bytes | #1258 (`platforms/mobile/push-integration.md`), open and not yet drafted at time of writing |
| Ephemeral device-pairing session secrets (`pairing_crypto.dart`) | Not yet filed as a distinct corpus task at time of writing |
| The mobile app's overall architecture and its other internal components | `architecture-containers-mobile` |
| The dozens of feature-level consumers of the derived signing key throughout `mobile/lib/features/**` | Not enumerated here; each reads `relayConfigProvider`, one layer removed from this component |
| A `platforms`-specific corpus template's required sections, evidence expectations, and industry model | Not yet filed as its own task at time of writing; this node instead follows `component.md`'s shape, per the *Scope and authority* section above |
| Whether `type: platforms` or `type: implementation` is this corpus's eventual settled choice for a `component.md`-shaped node whose path sits under `platforms/**` | Not resolved here -- flagged as open below, not silently picked |

**Expected but not verified when this node was written:**

- **The exact per-platform storage backend `flutter_secure_storage` selects
  by default was not verified against that plugin's own source**, because
  the plugin is a third-party pub.dev dependency this repository does not
  vendor; the *Responsibility* section's claim about Keychain/Keystore-backed
  defaults is stated as an `INFERENCE` from the dependency declaration and
  the absence of overriding configuration, not confirmed by opening the
  plugin's own implementation.
- **Whether `type: platforms` is the corpus's durable, accepted convention
  for a `platforms/**` node, versus a batch-local working convention that a
  later standards task revises, was not settled by this task.** It is
  recorded here as `TEAM_KNOWLEDGE` attributed to the batch dispatch, per
  `AGENTS.md`'s own guidance not to promote an uncorroborated convention to
  `FACT`.
- **Whether any consumer of the derived signing key beyond the four named in
  *Dependencies* reads `CommunityStorage` directly (rather than through
  `relayConfigProvider`) was not exhaustively checked.** A targeted search
  for `communityStorageProvider` usage found the four named above; a full
  audit of every read path was out of scope for a component-level node.

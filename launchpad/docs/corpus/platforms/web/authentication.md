---
id: platforms-web-authentication
type: platforms
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 46eb901e5aa928aa147fdaef9a509b636218653f."
    entry_class: FACT
    evidence:
      - "commit 46eb901e5aa928aa147fdaef9a509b636218653f"
  - statement: "web/src/shared/lib/nostr-signer.ts's signNostrEvent is the one signing function every web-client auth mechanism (NIP-42, NIP-98) is built on: it prefers a NIP-07 browser-extension provider (window.nostr) when hasNip07Provider() is true, and validates the extension's returned event against the unsigned template (pubkey matches the extension's own getPublicKey(), kind/created_at/content/tags match, and id/sig are present) before trusting it, throwing if the extension returns something inconsistent."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-signer.ts"
  - statement: "When no NIP-07 provider is present, signNostrEvent falls back to an ephemeral, page-lifetime secret key generated once via a module-level singleton (getEphemeralSecretKey/generateSecretKey) and signed with finalizeEvent -- unless the caller passes { requireNip07: true }, in which case the fallback is refused and a Nip07UnavailableError is thrown instead."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-signer.ts"
  - statement: "The ephemeral fallback exists, per signNostrEvent's own doc comment, to preserve anonymous browsing on open relays; the comment explicitly states that flows creating durable membership (not just read-only queries) must set requireNip07 so a page reload cannot orphan a relay-membership row tied to a key nothing but that browser tab ever held."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-signer.ts"
  - statement: "web/src/shared/lib/nostr-client.ts's queryEvents is the web client's NIP-42 relay-authentication call site: on WebSocket open it starts a 100ms timer before sending REQ, sending REQ immediately if the relay never AUTH-challenges within that window (its own comment notes Buzz relays always send AUTH, but the client tolerates one that does not)."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
  - statement: "On receiving an AUTH challenge, queryEvents builds the kind:22242 auth event via nostr-tools/nip42's makeAuthEvent(wsUrl, challenge), signs it with signNostrEvent (no requireNip07 -- read-only relay queries accept the ephemeral identity), sends it back as [\"AUTH\", signed], and only sends the pending REQ once the relay replies [\"OK\", <that event id>, true]; an OK-false reply or a mismatched signing failure rejects the whole query instead of silently degrading to an unauthenticated request."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
  - statement: "The server-side half of this NIP-42 exchange -- challenge generation, verify_nip42_event, AuthState transitions, and the 5-second AUTH_TIMEOUT -- is documented in architecture-flows-websocket-authentication, not restated here; this node's NIP-42 section covers only the web client's own call site."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/websocket-authentication.md"
  - statement: "web/src/shared/lib/nip98.ts's makeNip98AuthHeader builds a kind:27235 NIP-98 event carrying u (the target URL) and method tags, signs it via signNostrEvent, base64-encodes the resulting signed-event JSON, and returns it as an `Nostr <base64>` Authorization header value; when the caller passes a body option it additionally adds a payload tag (SHA-256 hex digest of the body, computed via crypto.subtle.digest) and a nonce tag (crypto.randomUUID())."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nip98.ts"
  - statement: "web/src/features/repos/git-client.ts's authHeaders() is one of two NIP-98 call sites in the web client: it always calls makeNip98AuthHeader(repoAuthUrl(owner, repoName), \"GET\") with the literal string \"GET\", regardless of whether the actual isomorphic-git HTTP request being authenticated is the initial GET to info/refs or a subsequent POST carrying pack data; the module's own comment on repoAuthUrl states the URL must match what the relay's transport.rs expects after stripping /info/refs, /git-upload-pack, and /git-receive-pack."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
  - statement: "The relay's GitAuth extractor (used by both the info_refs and upload_pack handlers the web client's clone/fetch traffic reaches) intentionally does not check the signed event's method tag against the actual HTTP request method -- its own source comment states this is deliberate because git's credential protocol signs once with GET and reuses the same token for the following POST -- which is exactly why git-client.ts's hardcoded \"GET\" authenticates both request phases without needing to distinguish them."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "architecture-flows-git-push documents this same GitAuth gate in full (NIP-98 verification with body: None, the repo-root-scoped u tag, the NIP-43 relay-membership check) for the git-push direction, and its own scope table explicitly states that git clone/fetch (info_refs, upload_pack) is a separate read flow that shares only GitAuth and tenant/repo resolution with the push flow it documents; this node references it rather than re-describing GitAuth, since the web client only ever exercises the read (clone/fetch) side."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/git-push.md"
      - "crates/buzz-relay/src/api/git/transport.rs"
  - statement: "web/src/features/invite/invite-api.ts's claimInviteInBrowser is the web client's second NIP-98 call site: it calls makeNip98AuthHeader(url, \"POST\", { body, requireNip07: true }) when POSTing to {relay}/api/invites/claim -- the requireNip07 flag means this call site, unlike the git-client.ts and nostr-client.ts call sites, refuses the ephemeral-identity fallback outright and throws Nip07UnavailableError if no browser extension is present."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/invite-api.ts"
  - statement: "The relay's POST /api/invites/claim handler (claim_invite) authenticates via a shared authenticate() helper that calls bridge::verify_bridge_auth_with_options (the same NIP-98 bridge verification path documented in architecture-flows-http-event-submission for POST /events, /query, /count) followed by bridge::check_nip98_replay for replay protection; this node references that flow node for the server-side verification mechanics rather than re-describing buzz_auth::verify_nip98_event."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/invites.rs"
      - "launchpad/docs/corpus/architecture/flows/http-event-submission.md"
  - statement: "web/src/shared/lib/relay-url.ts derives the relay's WebSocket URL (used as both the NIP-42 connection target and, converted to HTTP, the base for every NIP-98-authenticated request) from a build-time VITE_RELAY_URL env var if set, otherwise from the current page's own window.location (same-origin default)."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/relay-url.ts"
  - statement: "web/src/shared/lib/pubkey.ts's truncatePubkey is a display helper only; its own comment states a truncated pubkey is a recognition aid, never an identity proof, and that it mirrors desktop's equivalent -- it plays no role in the signing or verification path this node documents."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/pubkey.ts"
  - statement: "web/tests/e2e/smoke.spec.ts, the web client's only test suite, covers page-load rendering and the invite age/legal-consent gate with mocked HTTP routes; no unit or e2e test in the web/ tree was found that exercises nostr-signer.ts's NIP-07/ephemeral signing branch, nostr-client.ts's NIP-42 challenge/response handling, or nip98.ts's header construction directly."
    entry_class: FACT
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
  - statement: "Because no web/-tree test was found exercising the three signing/auth modules directly, and because this node's author did not locate one by searching the whole web/ tree for a matching test file name, it is a real coverage gap for this specific mechanism rather than an artifact of an incomplete search -- though only a full run of the existing suites (not performed for this documentation task) would fully rule out an indirect exercise of this code through a differently named spec."
    entry_class: INFERENCE
    evidence:
      - "web/tests/e2e/smoke.spec.ts"
    confidence: 0.7
relationships:
  - type: references
    target: architecture-containers-web
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: architecture-flows-http-event-submission
  - type: references
    target: architecture-flows-git-push
---

# Web client authentication

How the browser web client (`web/`) establishes and proves a user's Nostr
identity across its three outbound channels -- NIP-42 relay WebSocket auth,
and two independent NIP-98 HTTP call sites (git smart HTTP, invite claim).
This node documents the client-side signing mechanics only: which module
signs what, when it prefers a NIP-07 browser extension over an ephemeral
fallback identity, and where each mechanism's server-side counterpart is
already documented elsewhere in this corpus.

## Responsibility

The web client has no server-issued session, cookie, or bearer token of its
own. Every authenticated request it makes is a fresh Nostr event, signed
client-side and carried in-band (a NIP-42 `AUTH` frame, or a NIP-98
`Authorization: Nostr <base64>` header) -- there is no persisted credential
beyond whatever identity produced the signature. `nostr-signer.ts`'s
`signNostrEvent` is the single choke point every other module in this node
calls through; it decides, per call, whether a real user identity (NIP-07)
or a throwaway page-lifetime one is used.

## Identity: NIP-07 first, ephemeral fallback

`hasNip07Provider()` checks for a `window.nostr` browser-extension provider.
`signNostrEvent` prefers it when present: it asks the extension to sign the
unsigned event template, then validates the extension's response against
that template (matching pubkey, kind, `created_at`, `content`, `tags`, and
the presence of `id`/`sig`) before trusting it, throwing on any mismatch
rather than accepting a signature for content it didn't ask for.

When no extension is present, `signNostrEvent` falls back to an ephemeral
secret key -- generated once per page load and cached in a module-level
singleton -- unless the caller opted into `{ requireNip07: true }`, in which
case the fallback is refused and `Nip07UnavailableError` is thrown instead.
Per the module's own doc comment, the ephemeral fallback exists to preserve
anonymous browsing on open relays; callers that create durable server-side
state (a relay-membership row) must set `requireNip07` so a page reload
can't orphan that state under a key nothing but the closed tab ever held.

| Call site | `requireNip07` | Effect |
|---|---|---|
| `nostr-client.ts` (NIP-42 relay auth) | not set | Ephemeral identity accepted -- read-only queries work with no extension |
| `git-client.ts` (NIP-98 git smart HTTP) | not set | Ephemeral identity accepted |
| `invite-api.ts` (NIP-98 invite claim) | `true` | Extension required -- throws if absent |

## NIP-42: relay WebSocket authentication

`nostr-client.ts`'s `queryEvents` is the client's only NIP-42 call site. On
`WebSocket` open it waits up to 100ms for an `AUTH` challenge before sending
`REQ` unprompted (tolerating a relay that never challenges, though the
client's own comment notes Buzz relays always do). On receiving `["AUTH",
<challenge>]`, it builds the kind:22242 event via `nostr-tools/nip42`'s
`makeAuthEvent(wsUrl, challenge)`, signs it through `signNostrEvent` (no
`requireNip07`), sends `["AUTH", <signed>]`, and only proceeds to send the
pending `REQ` once the relay replies `["OK", <that event's id>, true]`. An
`OK`-false reply, or a signing failure, rejects the whole query rather than
silently falling through to an unauthenticated request.

This node does not restate the server side of that exchange --
`architecture-flows-websocket-authentication` already documents challenge
generation, `verify_nip42_event`, the connection's `AuthState` machine, and
the 5-second `AUTH_TIMEOUT` in full.

## NIP-98: HTTP request authentication

`nip98.ts`'s `makeNip98AuthHeader(url, method, options)` is the one function
both HTTP call sites use. It signs a kind:27235 event carrying `u` (target
URL) and `method` tags; when the caller passes a `body`, it additionally
signs a `payload` tag (SHA-256 hex of the body) and a fresh `nonce` tag. The
signed event is JSON-serialized, base64-encoded, and returned as an
`Authorization: Nostr <base64>` header value.

### Call site 1 -- git smart HTTP (`git-client.ts`)

`authHeaders()` always signs with the literal method `"GET"`, never the
request's actual verb. This is deliberate, not an oversight: the relay's
`GitAuth` extractor -- which gates every git HTTP request, including the
`info_refs` (GET) and `upload_pack` (POST) handlers this client's clone/fetch
traffic reaches -- intentionally does not check the signed event's `method`
tag against the real request method, because git's own credential protocol
signs once with GET and reuses that token across the following POST. Hard-
coding `"GET"` here matches that server-side tolerance rather than fighting
it. `repoAuthUrl()`'s own comment states the signed `u` URL must be the
repo-root URL (`{relay}/git/{owner}/{repo}.git`), matching what the relay
strips its endpoint suffixes down to before comparing.

`architecture-flows-git-push` documents this `GitAuth` gate in full for the
push direction, and its own scope table states that clone/fetch is a
separate read flow sharing only `GitAuth` and tenant/repo resolution with the
push flow -- this node references it rather than re-describing `GitAuth`,
since the web client (a read-only browser) never exercises push.

### Call site 2 -- invite claim (`invite-api.ts`)

`claimInviteInBrowser` calls `makeNip98AuthHeader(url, "POST", { body,
requireNip07: true })` when POSTing to `{relay}/api/invites/claim`. Unlike
the other two call sites, `requireNip07: true` here means the ephemeral
fallback is refused outright -- joining a community from the browser
requires a real NIP-07 identity, not a throwaway one.

Server-side, `claim_invite`'s `authenticate()` helper calls
`bridge::verify_bridge_auth_with_options` -- the same NIP-98 bridge path
`architecture-flows-http-event-submission` documents for `POST /events`,
`/query`, and `/count` -- followed by `bridge::check_nip98_replay`. This node
references that flow node for the verification mechanics rather than
re-describing `buzz_auth::verify_nip98_event`.

## URL derivation

Both the NIP-42 WebSocket target and the NIP-98 HTTP base URL come from
`relay-url.ts`: a build-time `VITE_RELAY_URL` env var if set, otherwise the
current page's own `window.location` (same-origin default). There is no
separate, independently configurable auth endpoint -- every authenticated
request targets whatever relay served (or is configured to talk to) the
page itself.

## Boundary

This node does not cover:
- The server-side verification logic for NIP-42, or the two NIP-98 paths
  (bridge and git) -- see `architecture-flows-websocket-authentication`,
  `architecture-flows-http-event-submission`, and `architecture-flows-git-push`
  respectively.
- The `architecture-containers-web` node's broader container-level treatment
  of this container's responsibility, technology, deployment, and data
  implications -- this node goes one level deeper into the auth mechanics
  specifically and does not restate that node's summary.
- NIP-07, NIP-42, and NIP-98 as protocols in their own right -- see the
  Nostr NIPs themselves (https://github.com/nostr-protocol/nips).
- Desktop, mobile, or CLI client authentication -- separate platforms, with
  no corresponding corpus nodes found in this checkout to reference.
- IndexedDB/`LightningFS` clone-cache lifecycle -- already flagged as
  unverified in `architecture-containers-web` and not re-litigated here.
- Relay-membership authorization decisions (allowlists, bans, NIP-43
  membership) that run *after* a signature verifies -- these are enforced
  server-side and are the concern of the flow nodes referenced above, not of
  how the client signs.

## Relationships

- `references: architecture-containers-web` -- the container-level node this
  one elaborates one specific mechanic of (its own Security implications
  section summarizes the same three call sites at a higher level).
- `references: architecture-flows-websocket-authentication` -- server-side
  NIP-42 verification this node's client-side NIP-42 section depends on.
- `references: architecture-flows-http-event-submission` -- server-side
  NIP-98 bridge verification the invite-claim call site depends on.
- `references: architecture-flows-git-push` -- server-side `GitAuth` gate the
  git smart HTTP call site depends on (for its shared read/fetch path).

All four targets were confirmed present in this worktree, freshly checked
out from `origin/launchpad`, before being declared.

## Scope and omissions

**This node covers** the web client's own authentication mechanics: identity
selection (NIP-07 vs. ephemeral fallback) in `nostr-signer.ts`, the NIP-42
relay-auth call site in `nostr-client.ts`, the NIP-98 header builder in
`nip98.ts` and its two call sites (`git-client.ts`, `invite-api.ts`), and the
same-origin URL derivation all three depend on.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Server-side NIP-42 verification, `AuthState`, `AUTH_TIMEOUT` | `architecture-flows-websocket-authentication` |
| Server-side NIP-98 bridge verification for `/events`, `/query`, `/count`, `/api/invites/claim` | `architecture-flows-http-event-submission` |
| Server-side `GitAuth` gate, NIP-43 relay-membership enforcement on git routes | `architecture-flows-git-push` |
| Container-level responsibility, technology, deployment, data implications of `web` as a whole | `architecture-containers-web` |
| NIP-07, NIP-42, NIP-98 as protocols | The Nostr NIPs (https://github.com/nostr-protocol/nips) |
| Desktop, mobile, CLI client authentication | Separate platforms; not yet documented in this corpus |
| IndexedDB/`LightningFS` clone-cache lifecycle | Flagged unverified in `architecture-containers-web`; not re-litigated here |

**Expected but not verified when this node was written:**

- **No test exercising `nostr-signer.ts`, `nostr-client.ts`, or `nip98.ts`
  directly was found.** `web/tests/e2e/smoke.spec.ts` is the only test file
  in the `web/` tree and covers page-load rendering and the invite
  age/consent gate, not the signing or NIP-42/NIP-98 mechanics this node
  documents. This is treated as a real coverage gap rather than papered
  over, though the existing suites were not actually run to rule out an
  indirect exercise of this code through a differently-named spec.
- **Whether any deployment currently disables `BUZZ_SERVE_GIT_WEB_GUI`
  end-to-end for a given community**, which would mean the git-client.ts
  NIP-98 call site is never reachable in that deployment, was not checked --
  `architecture-containers-web` already flags this as unverified and it is
  not re-checked here.

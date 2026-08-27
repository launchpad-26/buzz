---
id: architecture-containers-web
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "web/ is a Vite + React 19 + TypeScript single-page application named buzz-web in its own package.json, built with `tsc && vite build` via `pnpm -C web build`."
    entry_class: FACT
    evidence:
      - "web/package.json"
  - statement: "The application's routes are TanStack Router file routes under web/src/app/routes: index, root, invite.$code, repos, repos.$repoId, and repos.$repoId.blob.$."
    entry_class: FACT
    evidence:
      - "web/src/app/routes/index.tsx"
      - "web/src/app/routes/root.tsx"
      - "web/src/app/routes/invite.$code.tsx"
      - "web/src/app/routes/repos.tsx"
      - "web/src/app/routes/repos.$repoId.tsx"
      - "web/src/app/routes/repos.$repoId.blob.$.tsx"
  - statement: "The application has two feature areas organized under web/src/features/: invite (join-by-code landing) and repos (in-browser Git repository browser)."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/invite-api.ts"
      - "web/src/features/repos/git-client.ts"
  - statement: "web/src/features/repos/git-client.ts implements an isomorphic-git client that clones and fetches from the relay's smart HTTP git transport at `{relayHttpBaseUrl()}/git/{owner}/{repoName}.git`, persists working data in an IndexedDB-backed LightningFS scoped per owner/repo, and authenticates each request with a NIP-98 header."
    entry_class: FACT
    evidence:
      - "web/src/features/repos/git-client.ts"
  - statement: "web/src/shared/lib/nostr-client.ts implements a minimal Nostr client (NIP-01 REQ/EVENT queries, NIP-42 AUTH) that opens a WebSocket to a relay URL, authenticates via NIP-07 when available or an ephemeral page-lifetime identity otherwise, and collects EVENTs until EOSE."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nostr-client.ts"
  - statement: "web/src/shared/lib/nip98.ts builds a NIP-98 (kind:27235) Authorization header for HTTP requests to the relay, including a payload-digest tag and nonce when the request carries a signed body."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/nip98.ts"
  - statement: "web/src/features/invite/invite-api.ts POSTs to `{relayHttpBaseUrl()}/api/invites/claim` with a NIP-98 Authorization header (requiring a NIP-07 signer) to join a community from an invite code, optionally carrying a join-policy receipt."
    entry_class: FACT
    evidence:
      - "web/src/features/invite/invite-api.ts"
  - statement: "web/src/shared/lib/relay-url.ts derives the relay's WebSocket URL from a build-time VITE_RELAY_URL or, when unset, from the current page's own origin (same-origin derivation), then converts it to the equivalent HTTP base URL."
    entry_class: FACT
    evidence:
      - "web/src/shared/lib/relay-url.ts"
  - statement: "buzz-relay's config carries an optional web_dir field, sourced from env var BUZZ_WEB_DIR, that must contain an index.html; when set, the relay logs that it is serving the web UI from that directory, and when unset no static file serving of this bundle happens."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "In buzz-relay's router, a single fallback service serves the built web bundle: requests under /assets/ are served as static files via tower_http::services::ServeDir, and requests matching should_serve_spa (an invite-landing path, or a Git-browser path when serve_git_web_gui is enabled) return the bundle's index.html for client-side routing."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "should_serve_spa treats /invite/<code> as always eligible for the SPA fallback, and treats /, /repos and /repos/* as eligible only when serve_git_web_gui (env BUZZ_SERVE_GIT_WEB_GUI, defaulting to false per config.rs's own default-value assertion) is true, so the invite landing page and the Git repository browser are independently gated surfaces of the same static bundle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The root request handler (nip11_or_ws_handler) checks the admin host first and never falls through to the public web bundle for that host; for a non-admin host it upgrades to a relay WebSocket, serves the NIP-11 document for application/nostr+json, and otherwise (HTML accept, WebSocket upgrade failed) serves the web bundle's index.html only when serve_git_web_gui is enabled, else falls back to the NIP-11 document."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The relay applies a CORS layer (build_cors_layer) and a request-body size limit over the merged router, both established ahead of the static-bundle fallback in the router-construction order that registers the fallback service."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs"
  - statement: "The production Docker image builds web/dist and admin-web/dist in a shared builder stage (pnpm -C web build && pnpm -C admin-web build) and copies web/dist into the runtime image at /srv/buzz/web, setting ENV BUZZ_WEB_DIR=/srv/buzz/web; admin-web/dist is copied separately to /srv/buzz/admin-web and is a distinct bundle disambiguated at request time by host, not merged with the web bundle."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "`just relay-web` builds the web bundle (`pnpm -C web build`) and then starts buzz-relay in the same shell with BUZZ_WEB_DIR=./web/dist, so locally the web container has no independent server process — it is compiled to static assets and served entirely by buzz-relay's own HTTP router."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "web/playwright.config.ts runs its `smoke` project against a Vite preview server bound to 127.0.0.1:4173, and web/package.json's test:e2e / test:e2e:smoke scripts build the bundle before invoking Playwright."
    entry_class: FACT
    evidence:
      - "web/playwright.config.ts"
      - "web/package.json"
  - statement: "The repository's root contributor guide describes web/ as the browser web client (repo browser, served by the relay) inside block/buzz, the OSS source repository; build/deploy pipelines for signed artifacts and the staging cluster are owned by separate sibling repositories (buzz-releases, sprout-oss, block-coder-tf-stacks) rather than by this repository."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
  - statement: "Because this bundle is compiled to static assets and served by buzz-relay's own process rather than run as an independent server, it is not itself deployed, versioned, or exposed as a separate container at runtime — it ships and scales as part of whichever relay deployment sets BUZZ_WEB_DIR, and its own container boundary is therefore an artifact-and-code boundary (a distinct build target and source tree) rather than a distinct runtime process boundary."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/router.rs"
      - "crates/buzz-relay/src/config.rs"
      - "Dockerfile"
      - "Justfile"
    confidence: 0.8
---

# Container: `web` — browser web client

The in-browser Buzz client: an invite-acceptance landing page and a read-only
Git repository browser, compiled to static assets and served by `buzz-relay`
itself rather than run as its own process.

## Responsibility, technology and ownership boundary

**Responsibility.** Two independent user-facing surfaces, both reachable
without installing the desktop or mobile app:

- **Invite landing** (`/invite/<code>`) — accept a relay invite code from a
  browser and join a community.
- **Git repository browser** (`/`, `/repos`, `/repos/*`) — clone, browse
  trees/blobs/refs/commits, and view READMEs for repositories hosted by the
  relay's git smart-HTTP transport, entirely client-side.

Both surfaces are optional at the relay's discretion (see *Deployment
implications*), and the two are gated independently, not as one on/off switch.

**Technology.** Vite + React 19 + TypeScript, routed with TanStack Router,
styled with Tailwind CSS, using `isomorphic-git` (via `@isomorphic-git/lightning-fs`,
an IndexedDB-backed virtual filesystem) for in-browser Git operations and
`nostr-tools` for Nostr primitives. See `web/package.json` for the exact
dependency set.

**Ownership boundary.** This container is source in `block/buzz`
(this repository), the OSS upstream — not a build, signing, or deployment
pipeline. Those live in sibling repositories per the repository's own
ecosystem table: `buzz-releases` builds signed desktop/mobile artifacts,
`sprout-oss` builds and pushes the relay's Docker image (which is what bakes
this bundle in — see *Deployment implications*), and
`block-coder-tf-stacks` deploys that image to the staging cluster. This node
covers only the source tree and how `buzz-relay` serves the bundle it
produces; it does not cover how or when that image is built or deployed.

**Runtime boundary, and why it is unusual for a "container".** In the
C4/architecture sense this repository's taxonomy targets, `web` is normally
expected to be an independently running process. It is not: `vite build`
produces a static asset directory, and the only thing that ever serves those
assets at runtime is `buzz-relay`'s own HTTP router, behind one flag
(`BUZZ_WEB_DIR`) and one further gate (`BUZZ_SERVE_GIT_WEB_GUI`) for the
repository-browser routes specifically. There is no `web`-specific server,
port, or deployment unit distinct from the relay's. Its container boundary is
therefore a source-and-build boundary — its own `package.json`, its own
`pnpm -C web build`, its own directory — not a distinct runtime process
boundary. A reader expecting a `docker run`-able `web` service will not find
one.

## Inbound interfaces

The browser is the only inbound caller into this code; `web` has no server of
its own to receive inbound requests. What a user's browser loads is decided
entirely by `buzz-relay`'s router:

- `GET /assets/*` — static JS/CSS/asset files, served via `ServeDir` when
  `BUZZ_WEB_DIR` is configured.
- `GET /invite/<code>` — always returns the bundle's `index.html` (client-side
  routed from there) when `BUZZ_WEB_DIR` is set, independent of the
  Git-browser gate.
- `GET /`, `GET /repos`, `GET /repos/*` — return the bundle's `index.html`
  only when `BUZZ_SERVE_GIT_WEB_GUI` is also enabled; otherwise these paths do
  not serve this bundle at all (the root path folds into the relay's own
  content-negotiated handler, which upgrades to a relay WebSocket connection,
  serves the NIP-11 document, or serves `index.html` conditionally — see
  `crates/buzz-relay/src/router.rs`'s `nip11_or_ws_handler`).
- Any other path, with neither directory configured, is a relay 404 — the
  fallback service itself is only registered when at least one of the web or
  admin bundle directories is set.

## Outbound interfaces and directly connected containers/systems

Once loaded, the browser code calls back out to `buzz-relay` over three
channels, all same-origin by default (`relay-url.ts` derives the relay's
WebSocket/HTTP base URL from `window.location` unless a build-time
`VITE_RELAY_URL` overrides it):

- **Relay WebSocket** (`ws(s)://<host>`) — NIP-01 `REQ`/`EVENT` queries and
  NIP-42 `AUTH`, via `nostr-client.ts`. Used to read community/channel/event
  data needed by the UI.
- **Git smart HTTP** (`{relay}/git/<owner>/<repo>.git`) — clone/fetch traffic
  from `isomorphic-git`, authenticated per-request with a NIP-98
  (kind:27235) `Authorization` header built by `nip98.ts`. Served relay-side
  by `buzz-relay`'s own `git_router` (`crates/buzz-relay/src/router.rs`
  registers it alongside the API, media, and git-policy routers).
- **Invite claim API** (`POST {relay}/api/invites/claim`) — a single REST
  call, also NIP-98-authenticated (and requiring a NIP-07 signer), to accept
  an invite code and join a community.

There is no other outbound system this container talks to — no third-party
service, no direct database or media-store access. All three channels
terminate in the same `buzz-relay` process that serves the bundle itself.

## Deployment implications

`web` produces no independent deployment artifact — it is a build input to
`buzz-relay`'s image, not a service of its own. The production `Dockerfile`
builds `web/dist` and the separate `admin-web/dist` in one builder stage,
copies `web/dist` into the runtime image at `/srv/buzz/web`, and sets
`BUZZ_WEB_DIR=/srv/buzz/web` by default — so the invite landing page is
served out of the box in that image. The Git-browser routes are not: the
Dockerfile's own comment states the repository-browser routes require the
separate `BUZZ_SERVE_GIT_WEB_GUI=true` opt-in, which is unset by default.
Locally, `just relay-web` reproduces the same shape in one shell command:
build the bundle, then run the relay with `BUZZ_WEB_DIR` pointed at it — there
is no separate `web` process to start or stop.

The `admin-web` bundle is a sibling, not a variant of this one: a distinct
source tree (`admin-web/`), a distinct build, and a distinct served directory
(`BUZZ_ADMIN_WEB_DIR`), disambiguated from `web` at request time by the
request's `Host` header (`api::admin::is_admin_host`) rather than by path.
This node does not document `admin-web`.

## Data implications

This container holds no server-side state of its own. In the browser, cloned
Git repository data is persisted client-side in an IndexedDB-backed virtual
filesystem, scoped per repository (`buzz-git-<owner>-<repoName>`, from
`git-client.ts`'s `getFs`), so browsing history and cloned objects are local
to one browser profile and not synchronized anywhere. No corpus node was
found describing eviction, size limits, or clearing of that IndexedDB store;
treat that as unverified rather than assumed absent (see *Scope and
omissions*).

## Security implications

Every authenticated outbound call from this container is signed with the
user's own Nostr key via NIP-98 (git smart HTTP requests, the invite-claim
POST) — there is no separate web-specific credential or session token, and
the invite-claim call specifically requires a NIP-07 browser extension signer
rather than accepting the ephemeral fallback identity `nostr-client.ts` uses
for read-only relay queries. Because the bundle is same-origin with the relay
it talks to by default, most requests need no CORS allowance; the relay does
apply a CORS layer over the whole merged router (including this bundle's
fallback), which matters for the cross-origin case (a custom
`VITE_RELAY_URL`, or another origin embedding an invite link). This node does
not evaluate the CORS policy's specific allow-list — see
`crates/buzz-relay/src/router.rs`'s `build_cors_layer` and its own
configuration for that.

## Implementation paths

- Source tree: `web/`
- Routes: `web/src/app/routes/`
- Feature code: `web/src/features/repos/`, `web/src/features/invite/`
- Shared client libraries: `web/src/shared/lib/` (`nostr-client.ts`,
  `nip98.ts`, `relay-url.ts`, `nostr-signer.ts`, `pubkey.ts`)
- Relay-side serving: `crates/buzz-relay/src/router.rs`, `crates/buzz-relay/src/config.rs`
- Build/runtime wiring: `Dockerfile` (image build + `ENV BUZZ_WEB_DIR`),
  `Justfile` (`relay-web`, `web-build`, `web`, `web-check`, `web-e2e-smoke`
  targets)
- E2E verification: `web/playwright.config.ts`, `web/tests/e2e/smoke.spec.ts`

This node does not restate what those files contain; read them for
implementation detail.

## Scope and omissions

**This node covers** the `web` container's responsibility, technology,
ownership boundary, inbound and outbound interfaces, its directly connected
containers, and its deployment, data, and security implications, as of the
recorded revision.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `admin-web` bundle (separate source tree, separate serve path, host-disambiguated) | Not yet documented in this corpus |
| The relay's own architecture, its `git_router`/`api`/`media` routers in full, and the CORS/rate-limit configuration surface | Not yet documented in this corpus |
| NIP-98, NIP-42, and NIP-07 as protocols in their own right | The Nostr NIPs themselves (https://github.com/nostr-protocol/nips), not restated here |
| Desktop and mobile clients | Separate containers, not yet documented in this corpus |
| Build/signing/deployment pipelines for the relay image this bundle ships inside | `squareup/sprout-oss` and `squareup/block-coder-tf-stacks`, private sibling repositories outside this corpus's reach |

**No `relationships` in this node's front matter.** No sibling
`architecture/containers/*` node, and no `architecture-relay` or similar node,
is merged on `origin/launchpad` at the recorded revision — this task is one of
several concurrently in-flight, unmerged sibling documentation tasks, and a
`relationships[].target` naming an id no loaded node carries is a hard
validation error. The absence is a fact about this moment, not a claim that
nothing here is relationship-worthy: a `references` edge to whichever relay
container node lands first, and a `part-of` edge to any parent architecture
overview node, are the first candidates once either exists.

**Expected but not verified when this node was written:**

- **IndexedDB lifecycle** (eviction, size limits, explicit clearing) for the
  per-repository `LightningFS` store — no source describing this was found in
  `web/src/features/repos/`.
- **The CORS allow-list's actual contents** and how restrictive it is by
  default versus in the shipped Docker image — `build_cors_layer` was located
  but its own implementation and default configuration were not opened.
- **Whether any deployment currently sets `BUZZ_SERVE_GIT_WEB_GUI=true`** in
  practice — the Dockerfile leaves it unset by default; live configuration in
  staging or production is set in `block-coder-tf-stacks`, outside this
  repository.
- **Browser compatibility and offline behavior** of the IndexedDB-backed git
  client — not exercised by the smoke E2E spec inspected for this node.

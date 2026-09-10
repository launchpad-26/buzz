---
id: platforms-web-relay-serving
type: platforms
status: draft
origin: launchpad
audiences:
  - developer
  - agent
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 22078443c0988e9e4149a9856195ac1f4599c96b."
    entry_class: FACT
    evidence:
      - "commit 22078443c0988e9e4149a9856195ac1f4599c96b"
  - statement: "buzz-relay's Config carries an optional web_dir field, populated from env var BUZZ_WEB_DIR, and an independent serve_git_web_gui boolean field, populated from env var BUZZ_SERVE_GIT_WEB_GUI (true when the value is \"true\" or \"1\", defaulting to false when unset)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:1174-1181"
  - statement: "When BUZZ_WEB_DIR is set, config loading rejects it unless the directory contains an index.html file, and otherwise logs an info line stating the relay will serve the web UI from that directory."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:1183-1191"
  - statement: "In build_router, when either the admin bundle directory or the public web_dir is configured, one fallback service is installed on the merged router. It first checks whether the request's Host header matches the configured admin host (is_admin_host); the admin branch is checked first so a request to the admin host can never fall through to the public web bundle."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:157-187"
  - statement: "For a non-admin host, the fallback serves any path under /assets/ from the public web_dir via tower_http::services::ServeDir, serves the bundle's index.html when should_serve_spa(path, serve_git_web_gui) is true, and otherwise returns 404. If neither the admin nor the public directory is configured at all, the fallback service itself is never registered on the router."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:189-201"
  - statement: "should_serve_spa(path, serve_git_web_gui) returns true for any /invite/<code> path (is_invite_landing_path: exactly one non-empty path segment after /invite/) regardless of serve_git_web_gui, and additionally returns true for /, /repos, and /repos/* (is_git_web_gui_path) only when serve_git_web_gui is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:238-249"
  - statement: "The root path / is registered as an explicit relay route (nip11_or_ws_handler) and therefore never reaches the fallback service above. For a non-admin host on that handler: an application/nostr+json Accept header returns the NIP-11 document; a successful WebSocket upgrade attaches the connection to a Nostr relay session; on a failed upgrade, the handler serves the web bundle's index.html only when serve_git_web_gui is true and the client's Accept header contains text/html, and otherwise falls back to the NIP-11 document."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:304-389"
  - statement: "The merged router applies a request-tracking metrics layer, an HTTP trace layer, and a CORS layer (build_cors_layer, driven by the configured cors_origins list) over the entire router, including the static/SPA fallback service, in that order after the fallback is registered."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:200-206"
  - statement: "should_serve_spa's gating is covered by three unit tests: invite_landing_path_requires_exactly_one_nonempty_code_segment, git_web_gui_paths_are_explicit, and invite_is_always_served_but_git_gui_requires_opt_in, which together assert that /invite/<code> is always eligible while / and /repos/* are eligible only when serve_git_web_gui is true."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:522-550"
  - statement: "The integration test the_public_spa_is_untouched_by_the_admin_csp builds a full router via build_router with both an admin and a public bundle configured, requests /invite/payload.mac and /assets/app.js against a non-admin Host header, and asserts both return 200 with no Content-Security-Policy header set — exercising the public-bundle serving path (not just should_serve_spa in isolation) end to end through the real router construction."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:677-696"
  - statement: "config.rs's defaults_are_valid test asserts that Config::from_env(), with no relevant env vars set, produces serve_git_web_gui == false, corroborating the field's documented default."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:1338-1387"
  - statement: "The production Dockerfile copies the built web/dist output into the runtime image at /srv/buzz/web and sets ENV BUZZ_WEB_DIR=/srv/buzz/web, so the shipped relay image serves the invite-landing surface of this bundle by default; BUZZ_SERVE_GIT_WEB_GUI is not set in the Dockerfile and therefore stays at its false default in that image."
    entry_class: FACT
    evidence:
      - "Dockerfile:153"
      - "Dockerfile:159-160"
  - statement: "The Justfile's relay-web recipe builds the web bundle (pnpm -C web build) and then runs buzz-relay in the same shell with BUZZ_WEB_DIR=./web/dist, so locally there is no separate web server process — buzz-relay's own HTTP router is the only thing that ever serves this bundle, in every environment inspected (local dev and the production image)."
    entry_class: FACT
    evidence:
      - "Justfile:475-484"
  - statement: "architecture-containers-web (launchpad/docs/corpus/architecture/containers/web.md) already documents the web container's full inbound/outbound interfaces, deployment, data, and security implications, including this same relay-serving mechanism at container-grain. This node exists to give that one mechanism its own component-grain, test-linked treatment for an implementation-facing reader, and points at that node rather than restating its prose, per the corpus convention that a canonical claim is not duplicated across nodes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/architecture/containers/web.md"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.85
relationships:
  - type: references
    target: architecture-containers-web
---

# Platform component: relay-serving of the `web` bundle

How `buzz-relay` turns the built `web/` static bundle into HTTP responses:
which paths are served as files, which are served as the SPA's `index.html`,
which are relay routes that never reach this mechanism at all, and what
config controls each branch. This node documents that one relay-side
mechanism as a standalone, test-linked knowledge unit; it is the
component-grain counterpart to the container-grain view already recorded in
`architecture-containers-web`.

## Responsibility

`buzz-relay` is the only process that ever serves the `web/` bundle. There is
no independent `web` server, port, or deployment unit — the bundle is a
build output (`web/dist`, produced by `pnpm -C web build`) that `buzz-relay`
reads from disk at request time via one fallback service on its axum router.
This component's responsibility is exactly that fallback service and the two
config flags that gate it:

- `BUZZ_WEB_DIR` — points at the built bundle directory; must contain
  `index.html` or config loading fails; controls whether the fallback service
  exists at all for the public (non-admin) host.
- `BUZZ_SERVE_GIT_WEB_GUI` — an independent opt-in (`"true"`/`"1"`, default
  `false`) that widens which paths serve the bundle's `index.html`, on top of
  the invite-landing path that is always eligible.

## Public interface

Requests are handled in this order (admin-host handling is a separate,
already-documented branch this node does not restate — see *Boundary*):

| Path shape | Served as | Condition |
|---|---|---|
| `/` | Explicit relay route (`nip11_or_ws_handler`) — WebSocket upgrade, NIP-11 JSON, or (fallback within that same handler) the bundle's `index.html` | Only serves `index.html` when `serve_git_web_gui` is true **and** the client's `Accept` header contains `text/html` **and** no WebSocket upgrade occurred |
| `/assets/*` | Static file, via `tower_http::services::ServeDir` over `BUZZ_WEB_DIR` | `BUZZ_WEB_DIR` configured |
| `/invite/<code>` (exactly one non-empty segment) | Bundle's `index.html` (`should_serve_spa` → `is_invite_landing_path`) | `BUZZ_WEB_DIR` configured; independent of `serve_git_web_gui` |
| `/repos`, `/repos/*` | Bundle's `index.html` (`should_serve_spa` → `is_git_web_gui_path`) | `BUZZ_WEB_DIR` configured **and** `serve_git_web_gui` is true |
| Anything else, non-admin host | `404 NOT_FOUND` | Always, when the fallback service is registered |
| Any path, no bundle directory configured at all | Fallback service is never registered; requests fall through to whatever other route matches, else axum's own default `404` | `BUZZ_WEB_DIR` and the admin bundle directory both unset |

The root path (`/`) is the one exception worth calling out explicitly: it is
registered as its own relay route ahead of the fallback service, so it never
executes the `should_serve_spa` logic in the table above — its `index.html`
branch is a separate `if` inside `nip11_or_ws_handler` with its own,
independent condition (`serve_git_web_gui` plus an `Accept: text/html`
header, evaluated only after a WebSocket upgrade attempt has already failed).

## Dependencies and collaborators

**Depends on:**

- The `web/` build output (`web/dist`, produced by `pnpm -C web build`) —
  this component reads that directory's `index.html` and asset files; it
  contains no knowledge of what the bundle's routes or features are, only
  that the directory shape (`index.html` at its root) is valid.
- `Config::web_dir` and `Config::serve_git_web_gui`
  (`crates/buzz-relay/src/config.rs`), themselves sourced from
  `BUZZ_WEB_DIR` and `BUZZ_SERVE_GIT_WEB_GUI`.
- `tower_http::services::ServeDir` and axum's `Router::fallback_service`, the
  library primitives the fallback is built from.

**Collaborates with, but is not:**

- The admin-bundle fallback branch (`BUZZ_ADMIN_WEB_DIR`, `is_admin_host`),
  checked first in the same fallback closure so an admin-host request can
  never fall through to this component's branch. That bundle's own serving
  rules (CSP header, static-path allowlist) are a sibling mechanism this node
  does not document.
- `crate::api::admin` (`is_admin_host`) — called by this component's fallback
  closure but owned and documented by the admin surface, not by this node.

**Depended on by:** nothing in-repo calls into this mechanism directly; it is
reached only via inbound HTTP requests from a browser. The production
Docker image and the `just relay-web` local recipe both configure it (see
*Build and runtime wiring*), but neither is a code-level caller.

## Boundary

This node does not describe:

- **The `web/` application itself** — its routes, features, Nostr/Git
  clients, or UI. That is `architecture-containers-web`'s subject at
  container grain, and sibling tasks #1286 (application), #1287
  (authentication), #1288 (invite-ui), and #1290 (repository-browser) at
  component grain.
- **The admin bundle's serving mechanism** (`BUZZ_ADMIN_WEB_DIR`,
  `is_admin_host`, the admin CSP) — a distinct, host-disambiguated sibling
  path through the same fallback closure, already scoped out by
  `architecture-containers-web`'s own body.
- **NIP-11, NIP-42, or the relay's WebSocket protocol** — `/`'s non-SPA
  branches (NIP-11 JSON, WebSocket upgrade) are relay protocol surfaces
  outside this component's responsibility; they are named above only because
  they are the reason `/` never reaches `should_serve_spa`.
- **CORS policy contents** — `build_cors_layer` is named because it wraps
  this component's responses along with everything else on the merged
  router, but its allow-list configuration and defaults are not evaluated
  here.
- **Deployment/staging topology** — the Docker image and `just relay-web`
  are cited as this component's two known runtime configurations, not as a
  deployment or infrastructure description; that is owned by
  `squareup/sprout-oss` and `squareup/block-coder-tf-stacks`, outside this
  repository.

## Build and runtime wiring

- Production image: `Dockerfile` copies `web/dist` to `/srv/buzz/web` and
  sets `ENV BUZZ_WEB_DIR=/srv/buzz/web` by default; `BUZZ_SERVE_GIT_WEB_GUI`
  is not set there, so it stays at its `false` default in that image — the
  shipped image serves the invite-landing surface out of the box, not the
  Git-browser routes.
- Local development: `just relay-web` builds the bundle then runs
  `buzz-relay` with `BUZZ_WEB_DIR=./web/dist` in the same shell — there is no
  separate `web` process to start, stop, or monitor independently of the
  relay.

## Implementation paths

- `crates/buzz-relay/src/config.rs` — `web_dir`, `serve_git_web_gui` fields
  and their env parsing/validation (lines 1174-1191).
- `crates/buzz-relay/src/router.rs` — `build_router`'s fallback-service
  construction (lines 145-207), `should_serve_spa`/`is_invite_landing_path`/
  `is_git_web_gui_path` (lines 238-249), `nip11_or_ws_handler` (lines
  304-389), `build_cors_layer` (lines 481-505).
- `Dockerfile` — build-stage copy and `ENV BUZZ_WEB_DIR` (lines 153, 159-160).
- `Justfile` — `relay-web` recipe (lines 475-484).

## Tests

- `crates/buzz-relay/src/router.rs:522-550` — unit tests for
  `should_serve_spa` and its two path predicates.
- `crates/buzz-relay/src/router.rs:677-696` —
  `the_public_spa_is_untouched_by_the_admin_csp`, an integration-style test
  that builds the real router (`build_router`) and asserts the public
  bundle's `/invite/*` and `/assets/*` paths return `200` with no admin CSP
  header, exercising this component's serving path end to end rather than
  only its predicate functions.
- `crates/buzz-relay/src/config.rs:1338-1387` — `defaults_are_valid`,
  asserting `serve_git_web_gui` defaults to `false`.

This node does not restate what those files contain beyond the claims cited
above; read them for full implementation and test detail.

## Relationships

- `references`: `architecture-containers-web` — the container-grain node
  that already documents this same mechanism as part of the whole `web`
  container's inbound interfaces and deployment implications. This node adds
  a component-grain, test-linked treatment rather than duplicating that
  prose.

No `depends-on`, `part-of`, or `supersedes` relationship is declared: no
`platforms/web/*` sibling node (`#1286`–`#1288`, `#1290`) is merged on
`origin/launchpad` at the recorded revision, so there is no valid target for
either. The first of those to land is the natural point to revisit this.

## Scope and omissions

**This node covers** the relay-side mechanism that serves the `web/` bundle
as static assets and as a client-side-routed SPA — the config flags that gate
it, the exact path-matching rules, the ordering relative to the admin bundle
and the relay's own `/` route, its build/runtime wiring, and the tests that
exercise it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The `web/` application's own routes, features, and client libraries | `architecture-containers-web`; sibling tasks #1286, #1287, #1288, #1290 |
| The admin bundle's serving mechanism (`BUZZ_ADMIN_WEB_DIR`, CSP, static-path allowlist) | `architecture-containers-web`; not yet a dedicated `platforms/` node |
| NIP-11, NIP-42, and the relay WebSocket protocol | The Nostr NIPs themselves; not restated here |
| CORS policy contents and defaults | `crates/buzz-relay/src/router.rs`'s `build_cors_layer`, not evaluated in this node |
| Deployment/staging topology for the image this bundle ships inside | `squareup/sprout-oss`, `squareup/block-coder-tf-stacks`, outside this repository's corpus reach |

**Expected but not verified when this node was written:**

- **No `config.rs` unit test exercises the `BUZZ_WEB_DIR`-without-`index.html`
  error path or `BUZZ_SERVE_GIT_WEB_GUI`'s env-value parsing directly** — only
  `defaults_are_valid`'s default-`false` assertion was found; the validation
  error branch (lines 1183-1191) and the `"true"`/`"1"` parsing branch (line
  1179-1181) are exercised only indirectly, if at all, by the test suite
  inspected for this node.
- **Whether any current deployment sets `BUZZ_SERVE_GIT_WEB_GUI=true`** in
  practice is not established here — the Dockerfile leaves it unset by
  default; live configuration in staging or production is set in
  `block-coder-tf-stacks`, outside this repository.

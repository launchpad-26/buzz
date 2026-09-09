---
id: platforms-desktop-deep-links
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "The desktop app's Tauri configuration registers a single OS-level deep-link scheme, 'buzz', for the desktop platforms via the `deep-link.desktop.schemes` array."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:46-50"
  - statement: "desktop/src-tauri/Cargo.toml depends on tauri-plugin-deep-link version 2, and on tauri-plugin-single-instance version 2 with its 'deep-link' feature enabled."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:75"
      - "desktop/src-tauri/Cargo.toml:77"
  - statement: "desktop/src-tauri/src/lib.rs registers tauri_plugin_single_instance::init with a callback that, on a duplicate app launch, focuses the existing 'main' webview window and forwards any argv entry starting with 'buzz://' into handle_deep_link_url; it separately registers tauri_plugin_deep_link::init() as a Tauri plugin."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:122-135"
  - statement: "desktop/src-tauri/src/lib.rs calls deep_link::install_deep_link_handlers(app) during app setup, and separately calls .manage() to register PendingCommunityDeepLinks, PendingNavigationDeepLinks and PendingEntityDeepLinks as managed Tauri state."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:225-227"
      - "desktop/src-tauri/src/lib.rs:438"
  - statement: "install_deep_link_handlers registers an on_open_url callback via the tauri_plugin_deep_link::DeepLinkExt trait that calls handle_deep_link_url for every URL in the event, and on Windows and Linux only, additionally reads app.deep_link().get_current() once at startup and replays any URL found there through the same function, to cover a link that launched the process cold."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:285-306"
  - statement: "handle_deep_link_url parses the incoming string as a URL, rejects any scheme other than 'buzz', and then dispatches on the URL's host to one of seven arms: connect, join, add-community, channel, message, one of repo/project/pr/issue, and nostr-bind; an unrecognized or missing host is logged to stderr and dropped."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:594-710"
  - statement: "Six of the seven dispatch arms (all but nostr-bind) call activate_main_window before emitting anything, which looks up the webview window labeled 'main', and best-effort unminimizes, shows and focuses it, logging any individual step's failure to stderr without aborting the others."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:240-254"
  - statement: "The connect, join, add-community and channel/message arms additionally call one of queue_community_deep_link or queue_navigation_deep_link before emitting a Tauri event, pushing a de-duplicated record onto one of two Mutex<VecDeque> queues (PendingCommunityDeepLinks, PendingNavigationDeepLinks) keyed by managed Tauri state; the repo/project/pr/issue arm instead calls queue_entity_deep_link, which enqueues onto a third queue, PendingEntityDeepLinks."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:203-238"
      - "desktop/src-tauri/src/deep_link.rs:96-171"
  - statement: "Each of the three pending-link queues exposes take/acknowledge Tauri commands (plus, for the navigation queue, a clear command) that let the frontend pull the queue head without removing it, then explicitly acknowledge that exact id to pop it -- a consumer that is torn down before acknowledging leaves the same item at the head for the next listener to pick up."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:76-95"
      - "desktop/src-tauri/src/deep_link.rs:173-201"
  - statement: "All seven Tauri commands exposed by deep_link.rs (take/acknowledge for each of the three queues, plus clear_pending_navigation_deep_links) are registered in lib.rs's invoke_handler generate_handler! list."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:529-535"
  - statement: "Dedicated parser functions validate each URL shape before an event is ever queued or emitted: parse_channel_deep_link (path-segment channel/message form), parse_message_deep_link (query-string channel/id/thread form), parse_join_deep_link and parse_add_community_deep_link (both requiring parse_websocket_relay_param to resolve a ws/wss relay URL), parse_entity_deep_link (repo/project/pr/issue share links, validating host, path, and query keys against fixed allow-lists), and parse_nostr_bind_deep_link (which additionally calls into the sibling nostr_bind module to validate challenge_id, nonce, verification_code, protocol fields, origin and expiry, and cross-checks callback_url's scheme/host/port against origin)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:256-283"
      - "desktop/src-tauri/src/deep_link.rs:316-365"
      - "desktop/src-tauri/src/deep_link.rs:412-459"
      - "desktop/src-tauri/src/deep_link.rs:468-486"
      - "desktop/src-tauri/src/deep_link.rs:519-587"
      - "desktop/src-tauri/src/nostr_bind.rs"
  - statement: "A malformed URL for any arm is dropped with an stderr log line and no event is emitted, so the frontend never observes a half-formed deep-link payload; this validation policy is stated explicitly in a doc comment on parse_message_deep_link and mirrored by every other arm's `let Some(...) = parse_...(&url) else { ...; return; }` pattern."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:308-338"
  - statement: "desktop/src/shared/deep-link.ts is the frontend bridge: listenForDeepLinks drains PendingCommunityDeepLinks (connect/join/add-community events) by invoking take/acknowledge in a loop against injected DeepLinkDeps callbacks; listenForNavigationDeepLinks drains PendingNavigationDeepLinks (channel/message events) against caller-supplied onOpenChannel/onOpenMessage callbacks, serializing drains through a shared promise tail and supporting a generation counter so resetNavigationDeepLinkDrain can fail closed while a community switch is clearing native state; listenForEntityDeepLinks drains PendingEntityDeepLinks; listenForNostrBindDeepLinks is a plain event listener with no queue, since nostr-bind deep links carry no activate-and-replay requirement."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/deep-link.ts:1-231"
      - "desktop/src/shared/deep-link.ts:279-338"
  - statement: "Two React hooks consume the navigation and entity listeners: useMessageDeepLinks routes accepted channel/message payloads through useAppNavigation's goChannel, and useEntityDeepLinks parses accepted entity-link payloads with parseEntityLink and routes them through useOpenEntityLink; both are combined by useAppDeepLinks and mounted together in AppShell.tsx, gated off while a huddle room is active."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/useMessageDeepLinks.ts"
      - "desktop/src/shared/useEntityDeepLinks.ts"
      - "desktop/src/shared/useAppDeepLinks.ts"
      - "desktop/src/app/AppShell.tsx:669"
  - statement: "The community-link listener (listenForDeepLinks, covering connect/join/add-community) is wired directly in App.tsx rather than through useAppDeepLinks, because it needs to run above the router and before a community is necessarily selected."
    entry_class: FACT
    evidence:
      - "desktop/src/app/App.tsx:751"
  - statement: "desktop/src-tauri/src/deep_link_tests.rs unit-tests the Rust-side parsers and queues directly: entity-link acceptance/rejection against a golden fixture, FIFO ordering, exact-intent deduplication and acknowledge-only-at-head semantics for all three pending queues, mutex-poisoning recovery for the navigation queue, and per-parser accept/reject cases for channel, message, join and add-community links."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link_tests.rs"
  - statement: "desktop/src/shared/deep-link.test.mjs is a 451-line TypeScript-side test file covering the frontend bridge in desktop/src/shared/deep-link.ts."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/deep-link.test.mjs"
  - statement: "The corpus already carries a container-level node for the desktop app, architecture-containers-desktop, whose evidence ledger states the app registers a buzz:// OS-level deep-link scheme via tauri-plugin-deep-link, and whose body names community, entity and navigation deep links in one summary paragraph without decomposing the mechanism into its constituent parts."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "The `platforms` corpus type in node.schema.json's enum is a coarser, platform-wide surface than the internal decomposition this node performs; this node instead follows the architecture-component template (type: architecture), which is the merged template whose required sections (purpose/container-scoping, component diagram, notation legend, building-block table with responsibility/interface/evidence, boundary, relationships, scope-and-omissions) match issue #1240's Definition of Done bullets -- responsibility and interface/boundary, dependencies and collaborators, source and test links, and component-level (not whole-platform) scope."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/architecture-component.md"
    confidence: 0.75
  - statement: "Issue #1240 requires that exactly one hand-authored canonical corpus document be created for this task, and that any newly discovered second concept be filed as a separate task rather than folded in; no second concept surfaced while authoring this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1240 definition of done"
relationships:
  - type: part-of
    target: architecture-containers-desktop
---

# Desktop deep links: component view

This node decomposes one component inside the `architecture-containers-desktop`
container: the OS-level `buzz://` deep-link mechanism -- how a link opened outside
the app (from a browser, another app, or a duplicate app launch) reaches the running
Tauri app, gets parsed and validated, and is routed to the right piece of frontend
state. It answers "what actually happens between a user clicking a `buzz://` link and
the desktop app reacting to it," which `architecture-containers-desktop`'s own single
summary paragraph on the subject does not detail.

## Notation legend

| Shape | Meaning |
|---|---|
| Rectangle | A Rust module, function, or TypeScript module inside the desktop app |
| Cylinder | A stateful queue (Tauri-managed `Mutex<VecDeque<...>>`) |
| Dashed arrow | Emits/invokes across the Tauri IPC boundary (Rust <-> TypeScript) |
| Solid arrow | A direct in-process call |

## Component diagram

```mermaid
flowchart TB
    subgraph OS["OS / other process"]
        Link["buzz://... URL opened,\nor duplicate app launch argv"]
    end

    subgraph Rust["desktop/src-tauri (Rust)"]
        Plugin["tauri-plugin-deep-link\n+ single-instance argv forwarding"]
        Handle["handle_deep_link_url\n(scheme + host dispatch)"]
        Parsers["per-shape parsers:\nparse_channel_deep_link\nparse_message_deep_link\nparse_join_deep_link\nparse_add_community_deep_link\nparse_entity_deep_link\nparse_nostr_bind_deep_link"]
        Activate["activate_main_window"]
        QCommunity[("PendingCommunityDeepLinks")]
        QNav[("PendingNavigationDeepLinks")]
        QEntity[("PendingEntityDeepLinks")]
        NostrBind["nostr_bind module\n(challenge/nonce/origin validation)"]
    end

    subgraph TS["desktop/src (TypeScript + React)"]
        Bridge["shared/deep-link.ts\nlistenForDeepLinks\nlistenForNavigationDeepLinks\nlistenForEntityDeepLinks\nlistenForNostrBindDeepLinks"]
        MsgHook["useMessageDeepLinks\n-> useAppNavigation.goChannel"]
        EntityHook["useEntityDeepLinks\n-> useOpenEntityLink"]
        AppTsx["App.tsx\n(community onboarding)"]
    end

    Link --> Plugin
    Plugin --> Handle
    Handle --> Parsers
    Parsers --> Handle
    Handle --> Activate
    Handle -->|nostr-bind only| NostrBind
    Handle -.->|enqueue| QCommunity
    Handle -.->|enqueue| QNav
    Handle -.->|enqueue| QEntity
    Handle -.->|emit event| Bridge
    Bridge -.->|take/acknowledge invoke| QCommunity
    Bridge -.->|take/acknowledge invoke| QNav
    Bridge -.->|take/acknowledge invoke| QEntity
    Bridge --> MsgHook
    Bridge --> EntityHook
    Bridge --> AppTsx
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| Scheme registration | Registers `buzz` as the OS-level scheme the desktop app can be launched or focused from | `tauri.conf.json` `deep-link.desktop.schemes` config, read by the Tauri deep-link plugin at build/install time | `desktop/src-tauri/tauri.conf.json:46-50` |
| Plugin + single-instance wiring | Installs the deep-link plugin's open-URL callback; on a duplicate launch, forwards any `buzz://` argv into the same handler instead of spawning a second window | `tauri_plugin_deep_link::init()`, `tauri_plugin_single_instance::init(...)` registered on the `tauri::Builder` | `desktop/src-tauri/src/lib.rs:122-135` |
| `install_deep_link_handlers` | Registers the plugin's `on_open_url` callback; on Windows/Linux only, also replays a launch-time URL via `get_current()` for a cold start | Called once from app setup; takes `&mut tauri::App` | `desktop/src-tauri/src/deep_link.rs:285-306` |
| `handle_deep_link_url` | Parses the URL, enforces `buzz` scheme, dispatches by host to one of seven arms | `pub(crate) fn handle_deep_link_url(app: &AppHandle, url_str: &str)` | `desktop/src-tauri/src/deep_link.rs:594-710` |
| Per-shape parsers | Validate and normalize one URL shape each (`connect`/`join`/`add-community` relay params, path-segment `channel`, query-string `message`, allow-listed `repo/project/pr/issue`, and `nostr-bind`'s protocol fields) before anything is queued or emitted | One `parse_*(&Url) -> Option<...>` / `Result<...>` function per shape | `desktop/src-tauri/src/deep_link.rs:256-283,316-365,412-459,468-486,519-587` |
| `activate_main_window` | Best-effort unminimize/show/focus of the `"main"` webview window before a link is surfaced to the frontend | `fn activate_main_window(app: &AppHandle)`, called from six of the seven dispatch arms | `desktop/src-tauri/src/deep_link.rs:240-254` |
| `PendingCommunityDeepLinks` / `PendingNavigationDeepLinks` / `PendingEntityDeepLinks` | Managed Tauri state holding a de-duplicated FIFO queue per link category, drained via take/acknowledge commands so a torn-down listener leaves the head intact for the next one | `Mutex<VecDeque<...>>` behind `#[tauri::command]` take/acknowledge (and, for navigation, clear) functions | `desktop/src-tauri/src/deep_link.rs:20-238` |
| `nostr_bind` module (collaborator) | Validates `nostr-bind` deep-link fields (challenge id, nonce, verification code, protocol tuple, origin, expiry, callback URL) -- owned by the Nostr identity-binding flow, not this component | `nostr_bind::validate_*` functions called from `parse_nostr_bind_deep_link` | `desktop/src-tauri/src/nostr_bind.rs` |
| `shared/deep-link.ts` | Frontend bridge: drains each Rust-side queue via `invoke`, exposes `listenForDeepLinks`, `listenForNavigationDeepLinks`, `listenForEntityDeepLinks`, `listenForNostrBindDeepLinks` | Exported async functions returning a Tauri `UnlistenFn` | `desktop/src/shared/deep-link.ts:1-231,279-338` |
| `useMessageDeepLinks` / `useEntityDeepLinks` (collaborators) | React hooks that accept drained payloads and route them into the app's router (`useAppNavigation.goChannel`) or entity-link opener (`useOpenEntityLink`) | React hooks, combined by `useAppDeepLinks` and mounted in `AppShell.tsx` | `desktop/src/shared/useMessageDeepLinks.ts`, `desktop/src/shared/useEntityDeepLinks.ts`, `desktop/src/shared/useAppDeepLinks.ts`, `desktop/src/app/AppShell.tsx:669` |
| Community-link wiring in `App.tsx` (collaborator) | Consumes `listenForDeepLinks` directly (not through `useAppDeepLinks`) because community onboarding must run above the router, before any community is necessarily selected | `App.tsx`'s own effect calling `listenForDeepLinks` | `desktop/src/app/App.tsx:751` |

## Boundary

This node does not describe:
- **The desktop container's own deployment topology, bundle identity or other
  container-level concerns** -- see `architecture-containers-desktop` for those; this
  node only decomposes its deep-link mechanism.
- **External actors that open a `buzz://` link** (a browser, the relay's invite
  landing page, another instance of the app) -- that is the architecture-context
  layer, not this component-level node.
- **Class/function-internal design of any single parser or queue** -- building-block
  rows above name functions and modules only as existence/responsibility evidence,
  not as a walkthrough of their internal logic.
- **The CLI's own `buzz://message?...` consumption** (`crates/buzz-cli`) -- a
  different container's deep-link handling entirely, unrelated to this desktop
  component beyond sharing the same URL vocabulary for message links.
- **In-app rendering of `buzz://` links inside message content** (e.g. Markdown
  link rendering) -- a message-content concern, not the OS-level deep-link entry
  path this node documents.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the desktop app's OS-level `buzz://` deep-link mechanism end to
end: scheme registration, plugin wiring (including single-instance argv forwarding
and the Windows/Linux cold-launch replay), the seven-way dispatch in
`handle_deep_link_url`, each per-shape parser, the three pending-link queues and
their take/acknowledge/clear Tauri commands, the TypeScript bridge that drains them,
and the two React hooks (plus `App.tsx`'s own listener) that route the results into
the app.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The desktop container's deployment topology and bundle identity | `architecture-containers-desktop` |
| External actors that open a deep link (browser, relay invite page, OS shell) | A future architecture-context node, if one is written for this flow |
| The CLI's own `buzz://message` handling | `crates/buzz-cli` (a different container; not covered by any corpus node checked here) |
| The `nostr_bind` module's own validation rules in full | Out of scope; only its role as a collaborator called from `parse_nostr_bind_deep_link` is named here |
| Code/class-internal design of any parser or queue | Not attempted; C4's Code level is explicitly optional per the template this node follows |

**Expected but not verified when this node was written:**

- **Whether any corpus node yet documents the `crates/buzz-cli` deep-link consumer
  named in root `CLAUDE.md`.** `git ls-tree` of `origin/launchpad`'s corpus tree at
  the recorded revision shows no `platforms/cli` or equivalent node; this is named as
  a gap rather than linked, since no such node currently exists to point at.
- **Whether the Mermaid flowchart notation above faithfully reproduces C4's own
  component-diagram visual conventions** was not checked against a rendered
  reference -- the architecture-component template itself flags this as an open
  question for any node built from it.

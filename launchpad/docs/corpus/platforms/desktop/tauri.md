---
id: platforms-desktop-tauri
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
  - statement: "desktop/src-tauri/tauri.conf.json declares exactly one entry in `app.windows`, carrying no explicit `label` key; every runtime reference to that window elsewhere in the backend (window lifecycle handlers, tray, deep-link focus) addresses it by the string `\"main\"`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:16-36"
      - "desktop/src-tauri/src/lib.rs:130"
  - statement: "The main window's config sets `visible: false`, `maximized: true`, a macOS `titleBarStyle` of `Overlay` with `hiddenTitle: true` and an explicit `trafficLightPosition`, `dragDropEnabled: false`, `backgroundThrottling: \"disabled\"`, and `minWidth`/`minHeight` of 800x500 — the window is created hidden and revealed only after the app's own startup sequencing decides it is ready."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:16-36"
  - statement: "`app.macOSPrivateApi` is `true` and `app.security.csp` is a single explicit Content-Security-Policy string restricting `default-src`, `script-src`, `style-src`, `font-src`, `connect-src`, `img-src`, `media-src` and `worker-src` to a named allowlist (self, the `ipc:`/`http://ipc.localhost` IPC transport, the `buzz-media:` custom scheme, a pinned `cdn.jsdelivr.net` script source for `@mediapipe`, and broad `https:`/`http:`/`wss:`/`ws:` for outbound relay/media connections)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:37-40"
  - statement: "`app.plugins` configures the bundled `updater` plugin with an empty `endpoints` array (endpoint is supplied at build time instead, per the `buzz_updater_enabled` evidence below) and the `deep-link` plugin with `desktop.schemes: [\"buzz\"]`, registering the `buzz://` custom URL scheme with the OS."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:42-51"
  - statement: "desktop/src-tauri/capabilities/default.json scopes windows `\"main\"` and `\"huddle-*\"` to one named permission allowlist of 21 entries spanning `core:default` plus explicit `core:webview`/`core:window` grants, `notification:default`, `opener:default`, `websocket:default`, `window-state:default`, `dialog:default`, three `updater:allow-*` grants, `process:allow-restart`, and three `global-shortcut:allow-*` grants; no `deep-link:*` permission appears in this list."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/capabilities/default.json:1-31"
  - statement: "`run()`'s `tauri::Builder` chain registers, in order, `tauri_plugin_single_instance` (focuses the existing window and forwards `buzz://` argv on a duplicate launch), `tauri_plugin_deep_link`, `tauri_plugin_notification`, `tauri_plugin_opener`, `tauri_plugin_window_state` (built with `StateFlags::all() & !StateFlags::VISIBLE`, deliberately excluding visibility so the custom reveal plugin controls first-paint), an inline anonymous plugin named `\"initial-window-reveal\"`, `native_websocket::init()` (this crate's own inlined `websocket` plugin, declared to `tauri-build` with `default_permission(AllowAllCommands)`), `tauri_plugin_dialog`, and `tauri_plugin_process`, before `ptt_shortcut::install` conditionally adds `tauri_plugin_global_shortcut`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:122-201"
      - "desktop/src-tauri/build.rs:108-116"
  - statement: "The inline `\"initial-window-reveal\"` plugin's `on_webview_ready` hook enables Linux/WebKitGTK media-capture permission handling for the main webview, then on macOS waits for both stable outer window geometry (`wait_for_stable_initial_window_geometry`, polling up to 120 times at 16ms with 4 consecutive stable reads required) and a frontend-fired `\"initial-render-ready\"` event (5-second timeout) before calling `reveal_initial_window`, which shows and focuses the window; non-macOS platforms call `reveal_initial_window` immediately with no wait."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:145-198"
      - "desktop/src-tauri/src/initial_window.rs:1-78"
  - statement: "`app.run(...)`'s `RunEvent` handler hides (rather than closes) the `\"main\"` window on `WindowEvent::CloseRequested` via `api.prevent_close()` on macOS only, so the app stays resident for tray reopen; a `CloseRequested` on any window whose label starts with `\"huddle-\"` instead checks whether that window's ephemeral channel is still the active huddle and, if so, emits `\"huddle-companion-returned\"` to restore the main window's drawer presentation rather than ending the huddle."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:873-912"
  - statement: "`huddle::window::open_huddle_window` creates a companion window at runtime via `WebviewWindowBuilder::new(&app, label, WebviewUrl::App(\"index.html\".into()))` with `label` formatted as `\"huddle-{ephemeral_channel_id}\"`, an inner size of 960x720 and a minimum of 720x520; this label pattern is exactly what `capabilities/default.json`'s `\"huddle-*\"` glob is written to match, and `close_huddle_window` looks the same window up by the identical label format to close it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/window.rs:9-67"
  - statement: "`app_menu::install` replaces Tauri's auto-installed `Menu::default()` on macOS only (a no-op on other platforms) with a hand-built menu that reproduces every default submenu except the `close_window` item in the File and Window submenus, because macOS resolves that item's Cmd+W key equivalent before the webview ever receives the keypress, which would prevent the frontend's own conditional Cmd+W handling (huddle-close-requested vs. normal-window-close) from ever running."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_menu.rs:1-111"
  - statement: "`ptt_shortcut::install` installs `tauri_plugin_global_shortcut` with a handler closure (non-test builds only; a no-op in test builds because linking the plugin crashes the lib-test binary on Windows) that reads `AppState`'s huddle phase/voice-input-mode on every shortcut event and only acts when a huddle is connected/active and in push-to-talk mode; `sync_registration` separately registers or unregisters the fixed `Ctrl+Space` shortcut with the OS to match current huddle state, rather than reserving the key combination for the app's entire lifetime."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/ptt_shortcut.rs:1-152"
  - statement: "`build.rs` emits `cargo:rustc-cfg=buzz_updater_enabled` only when both `BUZZ_UPDATER_PUBLIC_KEY` and `BUZZ_UPDATER_ENDPOINT` were set as build-time environment variables; `run()` then gates `tauri_plugin_updater`'s registration on that same `#[cfg(buzz_updater_enabled)]`, and even within a build compiled with that cfg, the plugin is installed into the builder only when `cfg!(debug_assertions)` is false — a debug-profile binary never installs the updater plugin regardless of build-time env vars."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/build.rs:21"
      - "desktop/src-tauri/build.rs:113-117"
      - "desktop/src-tauri/src/lib.rs:208-214"
  - statement: "`deep_link::install_deep_link_handlers`, called from `run()`'s `.setup()` closure, registers an `on_open_url` callback via `tauri_plugin_deep_link`'s `DeepLinkExt` trait that forwards every received URL to `handle_deep_link_url`, and on Windows/Linux additionally drains any deep link present at cold-launch (`app.deep_link().get_current()`) through the same function; what `handle_deep_link_url` then does with a URL (routing it into pending-community/entity/navigation state consumed by frontend commands) is the frontend/backend bridge's concern, not this node's."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/deep_link.rs:285-304"
      - "desktop/src-tauri/src/lib.rs:438"
  - statement: "Cargo.toml pins `tauri = { version = \"2\", features = [\"macos-private-api\", \"tray-icon\"] }` and declares `tauri-plugin-deep-link`, `tauri-plugin-opener`, `tauri-plugin-single-instance` (with its own `deep-link` feature), `tauri-plugin-window-state`, `tauri-plugin-dialog`, `tauri-plugin-updater`, `tauri-plugin-process`, `tauri-plugin-global-shortcut`, and `tauri-plugin-notification` (pinned to `2.3.3`) as direct dependencies — every plugin `run()` registers is a real, versioned build-time dependency, not an assumed one."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/Cargo.toml:74-81"
      - "desktop/src-tauri/Cargo.toml:127-128"
  - statement: "launchpad/docs/corpus/architecture/containers/desktop.md (id architecture-containers-desktop) already states, at container level, that the desktop container is a Tauri 2 application pairing a Rust backend crate with a React 19 + Vite frontend; this node documents one internal mechanism of that same container (the Tauri shell/runtime itself) one level deeper, rather than restating the container's own claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "The already-authored sibling node `platforms-desktop-frontend-backend-bridge` (issue #1241, unmerged branch `task/1241-desktop-frontend-backend-bridge`) documents the frontend/backend IPC command-and-event mechanism inside this same desktop container — the `invoke_handler!` dispatch, `AppState`, the `invokeTauri` frontend wrapper, and the event-emit/listen channel; this node deliberately does not restate any of that content, and instead documents the surrounding shell (window lifecycle, plugin registration, capability/CSP boundaries) that mechanism runs inside."
    entry_class: FACT
    evidence:
      - "git_show(ref='task/1241-desktop-frontend-backend-bridge', path='launchpad/docs/corpus/platforms/desktop/frontend-backend-bridge.md') -> full document read at commit cd312b9e52cbccc073397d925e673cbac3535064"
  - statement: "PRD #602's own acceptance criteria enumerate 'platforms' as an in-scope corpus surface distinct from 'architecture', among thirteen total surfaces."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 (PRD acceptance criteria)"
  - statement: "Because the already-authored sibling node `platforms-desktop-frontend-backend-bridge` (#1241) already set `type: platforms` for a `platforms/desktop/*` node describing one internal mechanism of the desktop container, and because this node's own subject (the surrounding Tauri shell) is the same kind of container-internal-mechanism content, using `type: platforms` here keeps the batch internally consistent rather than introducing a second convention (`type: architecture`, which the architecture-component template's own text directs toward) for materially the same kind of document."
    entry_class: INFERENCE
    evidence:
      - "git_show(ref='task/1241-desktop-frontend-backend-bridge', path='launchpad/docs/corpus/platforms/desktop/frontend-backend-bridge.md') -> full document read at commit cd312b9e52cbccc073397d925e673cbac3535064"
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.6
---

# Desktop: Tauri shell and runtime

This node documents one internal mechanism of the **desktop container**
(`architecture-containers-desktop`): the Tauri 2 shell itself — window
creation and lifecycle, the plugin registration chain that assembles the
running application, and the two independent security boundaries (the
capability/permission allowlist and the Content-Security-Policy) that gate
what any webview may do — as distinct from what runs *through* that shell.
The frontend/backend IPC command-and-event mechanism (`invoke_handler!`
dispatch, `AppState`, the `invokeTauri` wrapper) is `platforms-desktop-
frontend-backend-bridge`'s subject, not this node's; this node answers *what
hosts and constrains that bridge*, not what the bridge itself carries.

## Responsibility

The Tauri shell is responsible for: creating and revealing the application's
window(s) at the right moment and in the right state; assembling the running
process from Tauri core plus a fixed set of first-party and third-party
plugins declared in `Cargo.toml`; and enforcing two independently-checked
boundaries around every webview regardless of what application code inside
it tries to do — a Content-Security-Policy restricting what the webview may
load or connect to, and a capability/permission allowlist restricting which
Tauri core/plugin APIs a given window may invoke at all. It also owns
platform-specific integration that has nothing to do with any one IPC
command: the macOS application menu, the `buzz://` OS URL-scheme
registration, and a push-to-talk global keyboard shortcut whose OS-level
reservation is toggled by application state rather than held for the
process's whole lifetime.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `app.windows[0]` (`tauri.conf.json`) | Static window declaration | One window, no explicit `label` (addressed as `"main"` everywhere else in the backend); created `visible: false`, `maximized: true`, macOS `titleBarStyle: "Overlay"` with `hiddenTitle: true`, `minWidth`/`minHeight` 800x500 | `desktop/src-tauri/tauri.conf.json:16-36` |
| `app.security.csp` | Static configuration | Single CSP string scoping `script-src`/`connect-src`/`img-src`/`media-src`/etc. to `'self'`, the IPC transport, the `buzz-media:` scheme, one pinned CDN script origin, and broad `https/http/wss/ws` for relay/media | `desktop/src-tauri/tauri.conf.json:37-40` |
| `capabilities/default.json` | Static configuration | Names windows `"main"`/`"huddle-*"` and grants exactly 21 named permissions across `core`, `notification`, `opener`, `websocket`, `window-state`, `dialog`, `updater`, `process`, `global-shortcut` — a permission or command not listed here is unreachable from the webview no matter what the Rust side registers | `desktop/src-tauri/capabilities/default.json:1-31` |
| `tauri::Builder::plugin(...)` chain | Ordered builder calls in `run()` | Registers `tauri_plugin_single_instance`, `tauri_plugin_deep_link`, `tauri_plugin_notification`, `tauri_plugin_opener`, `tauri_plugin_window_state`, the inline `"initial-window-reveal"` plugin, `native_websocket::init()`, `tauri_plugin_dialog`, `tauri_plugin_process`, `ptt_shortcut`'s `tauri_plugin_global_shortcut`, and conditionally `tauri_plugin_updater` | `desktop/src-tauri/src/lib.rs:122-215` |
| `huddle::window::open_huddle_window` / `close_huddle_window` | Runtime window creation/teardown | Creates/looks up a `WebviewWindowBuilder` window labeled `"huddle-{ephemeral_channel_id}"`, matching the capability file's `"huddle-*"` glob | `desktop/src-tauri/src/huddle/window.rs:9-67` |
| `app_menu::install` | macOS-only builder call | Replaces Tauri's default menu, dropping the `close_window` items so the frontend can own Cmd+W conditionally | `desktop/src-tauri/src/app_menu.rs:1-111` |
| `ptt_shortcut::install` / `sync_registration` | Plugin install + runtime (un)registration | Installs `tauri_plugin_global_shortcut`; `sync_registration` registers/unregisters `Ctrl+Space` to match live huddle phase/voice-input-mode, never held statically | `desktop/src-tauri/src/ptt_shortcut.rs:1-152` |
| `RunEvent` handler in `app.run(...)` | Process-lifetime event match | Hides (not closes) `"main"` on macOS `CloseRequested`; restores the huddle drawer on an active `"huddle-*"` window's `CloseRequested`; drives shutdown on `ExitRequested`/`Exit` | `desktop/src-tauri/src/lib.rs:873-936` |

## Dependencies

**Depends on** (this shell requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `tauri` (v2, `macos-private-api` + `tray-icon` features) | Core application/window/runtime framework this whole node documents | `desktop/src-tauri/Cargo.toml:74` |
| `tauri-plugin-single-instance`, `tauri-plugin-deep-link`, `tauri-plugin-notification`, `tauri-plugin-opener`, `tauri-plugin-window-state`, `tauri-plugin-dialog`, `tauri-plugin-process`, `tauri-plugin-updater`, `tauri-plugin-global-shortcut` | Every plugin the `run()` builder chain installs | `desktop/src-tauri/Cargo.toml:75-81`, `:127` |
| `tauri-plugin-notification` (pinned `2.3.3`, not a bare `"2"`) | Same plugin family, individually version-pinned rather than following the shared `"2"` range every other plugin above uses | `desktop/src-tauri/Cargo.toml:128` |
| `tauri-build` (build-dependency) | Declares this crate's own inlined `websocket` plugin (`default_permission(AllowAllCommands)`) at build time, which `native_websocket::init()` registers into the shell | `desktop/src-tauri/build.rs:108-116` |
| `BUZZ_UPDATER_PUBLIC_KEY` / `BUZZ_UPDATER_ENDPOINT` build-time env vars | Gate whether `tauri_plugin_updater` is even compiled in (`buzz_updater_enabled` cfg); absent in a plain local build | `desktop/src-tauri/build.rs:21`, `:113-117` |

**Depended on by** (these require this shell to exist):

| Component | Why | Evidence |
|---|---|---|
| `platforms-desktop-frontend-backend-bridge`'s IPC surface | Every `#[tauri::command]` the bridge dispatches only reaches the webview if the capability allowlist this node documents grants it, and only crosses the wire if the CSP this node documents permits the `ipc:` connection | `desktop/src-tauri/capabilities/default.json:1-31`, `desktop/src-tauri/tauri.conf.json:37-40` |
| Huddle companion UI (`open_huddle_window`) | Cannot open a second webview window without the shell's window-creation API, and that window's own webview cannot invoke anything unless its label matches the `"huddle-*"` capability grant | `desktop/src-tauri/src/huddle/window.rs:9-67`, `desktop/src-tauri/capabilities/default.json:5` |

## Boundary

This node does not describe:
- The frontend/backend IPC command-and-event mechanism itself — the
  `invoke_handler!` registration, individual `#[tauri::command]` handlers,
  `AppState`, the frontend's `invokeTauri` wrapper, or the event-emit/listen
  channel. That is `platforms-desktop-frontend-backend-bridge`'s (#1241)
  subject; this node documents the shell that mechanism runs inside, not the
  mechanism.
- The desktop container's own deployment topology, bundling, release lane, or
  its outbound interfaces to the relay and managed-agent subprocesses — see
  `architecture-containers-desktop` for those. This node cites `bundle.*` in
  `tauri.conf.json` only implicitly through the plugin/dependency lists above,
  never as its own subject.
- What a received deep link is used *for* once `handle_deep_link_url` routes
  it into pending-community/entity/navigation state — that state is consumed
  by frontend-facing commands and belongs to the IPC bridge node, not this
  one. This node's concern stops at the OS-level scheme registration and the
  `on_open_url` → `handle_deep_link_url` handoff.
- Any individual plugin's internal implementation (e.g., how
  `tauri-plugin-window-state` persists geometry to disk) — only the
  configuration and call sites this repository controls are in scope.
- Whether the current CSP or capability grants are correct, complete, or
  should change. This is a documentation task; deciding to tighten or loosen
  either is a separate, implementation-owned change.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the Tauri shell's window declaration and lifecycle
(static config, first-frame reveal sequencing, hide-to-tray, dynamic huddle
companion windows), the ordered plugin registration chain that assembles the
running application, the two independently-enforced security boundaries
(capability/permission allowlist, CSP), the macOS menu customization, the
push-to-talk global-shortcut lifecycle, the conditional release-only updater
plugin, and the `buzz://` OS URL-scheme registration up to the point a
received URL is handed off to application state.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The frontend/backend IPC command-and-event mechanism | `platforms-desktop-frontend-backend-bridge` (#1241) |
| The desktop container's deployment topology, bundling, and release lane | `architecture-containers-desktop` |
| What a routed deep link does inside application state, and which frontend commands consume it | `platforms-desktop-frontend-backend-bridge` (#1241) or a future deep-link-specific node |
| Any individual command's business logic | Future per-feature corpus nodes (none yet exist in the merged corpus) |
| Whether the CSP or capability grants should change | An implementation decision, not a documentation task |

**Expected but not verified when this node was written:**

- **Runtime behavior of the plugin chain was not exercised.** This node
  documents what `run()` registers and how `tauri.conf.json`/
  `capabilities/default.json` are written, from static source reading — it
  does not report having launched the app and observed, for example, the
  first-frame reveal timing described in `initial_window.rs` actually
  settling within its poll budget on a real machine.
- **Windows- and Linux-specific plugin behavior was not independently
  checked beyond what the source comments state.** The macOS-specific paths
  (menu customization, tray, private API, `titleBarStyle: "Overlay"`,
  `#[cfg(target_os = "macos")]`-gated reveal/backing logic) are the most
  heavily commented and therefore the best-understood; the non-macOS reveal
  path (`initial_window.rs`'s `#[cfg(not(target_os = "macos"))]` branch) and
  Windows/Linux deep-link cold-launch handling were read but not run.
- **Whether `type: platforms` is this corpus's eventual settled convention**
  for the `platforms/desktop/*` batch (as opposed to `type: architecture`)
  is inherited, unresolved, from `platforms-desktop-frontend-backend-bridge`'s
  own evidence ledger — not re-litigated here.
- **The absence of any `deep-link:*` permission in
  `capabilities/default.json` was observed but its cause was not
  investigated** — whether that is because the deep-link plugin exposes no
  invokable command surface to the webview, or an intentional omission for
  another reason, was not confirmed against Tauri's own plugin documentation.

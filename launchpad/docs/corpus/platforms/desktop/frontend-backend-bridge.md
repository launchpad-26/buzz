---
id: platforms-desktop-frontend-backend-bridge
type: platforms
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
  - statement: "The desktop backend's `invoke_handler(tauri::generate_handler![...])` registration in lib.rs lists 336 non-blank, non-attribute command-path entries between the opening bracket and its closing `])`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/lib.rs:519-863"
  - statement: "A Tauri command function is declared with the `#[tauri::command]` attribute, takes `state: State<'_, AppState>` as a parameter to reach shared process state, and returns `Result<T, String>` — for example `get_presence` (pubkeys lookup) and `archive_channel` (single-argument mutation)."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/profile.rs:337-341"
      - "desktop/src-tauri/src/commands/channels.rs:510"
  - statement: "AppState (desktop/src-tauri/src/app_state.rs, lines 19-133) is a single struct of Mutex/AtomicX/Arc-wrapped fields — identity keys, HTTP clients, managed-agent process tables, huddle state, an optional AppHandle — constructed once and handed to every command invocation through Tauri's `State<'_, AppState>` extractor; it is the one shared mutable surface every command in the bridge reaches through."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/app_state.rs:19-133"
  - statement: "Tauri's command macro case-converts a command's own top-level parameter names between the frontend's camelCase call and the Rust function's snake_case parameter names: `get_thread_replies` declares `root_event_id`/`channel_id` (snake_case) while its frontend call site in tauri.ts passes `rootEventId`/`channelId` (camelCase) for the same values."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/commands/messages.rs:244-251"
      - "desktop/src/shared/api/tauri.ts:495-518"
  - statement: "That automatic case conversion does not reach inside a nested argument struct unless the struct itself opts in: `ThreadCursor` (desktop/src-tauri/src/models.rs, lines 324-330) has no `#[serde(rename_all = \"camelCase\")]` attribute, so its wire field names stay `created_at`/`event_id`; the same call site that relies on automatic top-level conversion for `rootEventId`/`channelId` has to hand-convert `cursor.createdAt`/`cursor.eventId` into `created_at`/`event_id` before sending it, and workflows.rs shows the alternative — an argument struct that does carry `#[serde(rename_all = \"camelCase\")]` (line 870) and therefore needs no such hand conversion."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/models.rs:324-330"
      - "desktop/src/shared/api/tauri.ts:495-518"
      - "desktop/src-tauri/src/commands/messages.rs:870"
  - statement: "desktop/src/shared/api/tauri.ts's `invokeTauri<T>()` (lines 296-309) is the sole call site of `@tauri-apps/api/core`'s `invoke` used by the domain API modules under desktop/src/shared/api/; it normalizes a rejected invocation into a `TauriInvokeError` (lines 249-282, carrying the raw wire payload) and inspects the resulting message for a `relay rate-limited:` prefix to activate the shared TS relay client's rate-limit gate."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/tauri.ts:296-309"
      - "desktop/src/shared/api/tauri.ts:249-282"
      - "desktop/src/shared/api/tauri.ts:284-294"
  - statement: "Domain-scoped frontend modules (desktop/src/shared/api/tauri*.ts — e.g. tauriEvents.ts, tauriChannels.ts, tauriMessages.ts, tauriIdentity.ts) each wrap invokeTauri for one functional area and perform their own Raw*-to-domain-type field mapping; tauriEvents.ts's getEventById/getEventsByIds is a minimal complete example of the pattern."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/api/tauriEvents.ts:1-14"
  - statement: "The backend pushes state to the frontend independently of any command's return value via `AppHandle::emit(event_name, payload)` (Tauri's Emitter trait), paired with the frontend's `listen(event_name, callback)` from `@tauri-apps/api/event`; the huddle module's `emit_huddle_state` emits `\"huddle-state-changed\"`, and two independent frontend components (HuddleIndicator.tsx, HuddleRoomHeader.tsx) each call `listen(\"huddle-state-changed\", ...)` to receive it."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/huddle/state.rs:540-544"
      - "desktop/src/features/huddle/components/HuddleIndicator.tsx:204"
      - "desktop/src/features/huddle/components/HuddleRoomHeader.tsx:92"
  - statement: "At the recorded revision, 49 `AppHandle::emit(...)` call sites (via the `Emitter` trait, called as `app.emit(...)`/`app_handle.emit(...)`/`handle.emit(...)`/`self.app.emit(...)`) exist across 24 distinct files under desktop/src-tauri/src (deep-link routing, pairing status, huddle state/audio, managed-agent/persona data-changed signals, tray actions, prevent-sleep expiry, media-upload progress, mesh-llm download progress, native-notification activation), each firing on a bare string or named-constant event identifier rather than through any typed/generated event registry."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='\\.emit\\(', scope='desktop/src-tauri/src/**/*.rs') -> 49 matching lines across 24 files, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "desktop/src-tauri/capabilities/default.json scopes the `main` and `huddle-*` windows to an explicit permission allowlist (core:default plus named window/webview/notification/opener/websocket/dialog/updater/process/global-shortcut permissions) — a command or plugin API not covered by one of these permissions is not reachable from the webview regardless of what the Rust side registers in `invoke_handler!`."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/capabilities/default.json:1-31"
  - statement: "desktop/src-tauri/tauri.conf.json's Content-Security-Policy `connect-src` directive explicitly includes `ipc:` and `http://ipc.localhost`, which is the transport origin the webview's `invoke` calls travel over; without that grant the CSP would block the IPC channel itself, independently of the capabilities file's per-permission allowlist."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/tauri.conf.json:39"
  - statement: "desktop/src/testing/e2eBridge.ts defines a mock `window.__TAURI_INTERNALS__` (including its own `invoke` implementation) that Playwright E2E specs install in place of the real Tauri IPC bridge; it also re-implements `emit`/`listen` semantics used elsewhere in the file (e.g. re-emitting \"huddle-state-changed\") so a UI under test observes the same command/event contract without a real Rust backend process."
    entry_class: FACT
    evidence:
      - "desktop/src/testing/e2eBridge.ts:14604-14611"
      - "desktop/src/testing/e2eBridge.ts:3596"
  - statement: "A production (non-`--mode e2e`) build strips the mock bridge entirely, so `window.__TAURI_INTERNALS__` is only ever defined by Tauri's real webview runtime in that build, or by e2eBridge.ts's install routine in an E2E build — per this repository's own CLAUDE.md, mixing the two (testing against a `pnpm run build` output) makes every mock-mode spec fail with the same misleading symptom."
    entry_class: FACT
    evidence:
      - "CLAUDE.md"
      - "desktop/src/main.tsx:111-132"
  - statement: "launchpad/docs/corpus/architecture/containers/desktop.md (id architecture-containers-desktop) already states, at container level, that the frontend communicates with the Rust backend exclusively through Tauri's IPC (invoke_handler commands) and Tauri events, and never talks to the relay directly — this node documents that same boundary one level deeper (the command/event mechanism itself) rather than restating the container's own claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/desktop.md"
  - statement: "PRD #602's own acceptance criteria enumerate 'platforms' as an in-scope corpus surface distinct from 'architecture', among thirteen total surfaces."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 (PRD acceptance criteria)"
  - statement: "This task's own target path (platforms/desktop/frontend-backend-bridge.md) places it under the `platforms` surface's directory, even though the architecture-component template this node's structure follows was itself written for nodes filed under architecture/ (matching architecture-containers-desktop's own placement) and directs its instances toward `type: architecture`. Because validate.py performs no cross-check between a node's `type` and its directory, and node.schema.json's own type enum lists `platforms` as a member alongside `architecture`, `type: platforms` is the better fit for what this node is actually cataloguing (one platform's internal mechanism, per PRD #602's surface list above) even though it borrows the architecture-component template's shape rather than inventing a new one."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/architecture-component.md"
    confidence: 0.55
---

# Desktop: frontend/backend bridge (component view)

This node decomposes one internal mechanism of the **desktop container**
(`architecture-containers-desktop`): the Tauri IPC boundary that lets the
React 19 frontend and the Rust backend crate (`buzz_lib`) call into and
signal each other, both compiled into the same process and shipped as one
binary. It answers: *what actually crosses the frontend/backend boundary,
in which direction, through which mechanism, and what gate keeps something
from crossing it uninvited?*

This node was written from `launchpad/docs/corpus/templates/architecture-component.md`.
No prior node has yet been authored from that template (confirmed against
`origin/launchpad`'s corpus tree at the recorded revision), so this is the
first real-world test of its required-sections shape; see *Scope and
omissions* for where that shape ran into this bridge's actual complexity.

## Notation legend

| Shape | Meaning |
|---|---|
| Rounded box | A building block documented in this node |
| Solid arrow | Frontend → backend command call (request/response) |
| Dashed arrow | Backend → frontend event push (fire-and-forget) |
| Dotted box | Boundary enforced independently of application code (CSP, capability allowlist) |

## Component diagram

```mermaid
flowchart LR
    subgraph Frontend["Frontend (desktop/src)"]
        UI["React components / hooks"]
        DomainAPI["Domain API modules\n(shared/api/tauri*.ts)"]
        InvokeWrap["invokeTauri()\n(shared/api/tauri.ts)"]
        Listeners["listen() callbacks\n(@tauri-apps/api/event)"]
        MockBridge["E2E mock bridge\n(testing/e2eBridge.ts)"]
    end

    subgraph Transport["Transport (webview-enforced)"]
        CSP[["CSP connect-src: ipc:"]]
        Caps[["capabilities/default.json\npermission allowlist"]]
    end

    subgraph Backend["Backend (desktop/src-tauri/src)"]
        Handler["invoke_handler!\ncommand dispatch (lib.rs)"]
        Cmd["#[tauri::command] fn\n-> Result<T, String>"]
        State["AppState\n(app_state.rs)"]
        Emit["AppHandle::emit(event, payload)"]
    end

    UI --> DomainAPI --> InvokeWrap
    InvokeWrap -. real build .-> CSP --> Caps --> Handler
    MockBridge -. e2e build only .-> UI
    Handler --> Cmd
    Cmd <--> State
    Cmd -- "Result<T, String>" --> InvokeWrap
    Emit -. dashed: event push .-> Listeners
    State -.-> Emit
```

## Building blocks

| Component | Responsibility | Interface | Evidence |
|---|---|---|---|
| `invoke_handler!` registration | Backend-side allowlist of every callable command; maps a command-name string to its Rust function | `tauri::generate_handler![...]`, one macro invocation | `desktop/src-tauri/src/lib.rs:519-863` |
| `#[tauri::command]` handler functions | One request/response operation each; reads/mutates `AppState`, returns `Result<T, String>` | Plain async fn per command, snake_case top-level params (auto camelCase-converted from the frontend call) | `desktop/src-tauri/src/commands/profile.rs:337-341`, `desktop/src-tauri/src/commands/channels.rs:510` |
| `AppState` | Process-lifetime shared state (identity keys, HTTP clients, managed-agent process table, huddle state, `AppHandle`) injected into every command via `State<'_, AppState>` | Struct of `Mutex`/`Atomic*`/`Arc` fields | `desktop/src-tauri/src/app_state.rs:19-133` |
| `invokeTauri<T>()` wrapper | Sole frontend call site of `@tauri-apps/api/core`'s `invoke`; normalizes rejections to `TauriInvokeError` and triggers the shared rate-limit gate on relay 429s | `invokeTauri(command: string, args?: Record<string, unknown>): Promise<T>` | `desktop/src/shared/api/tauri.ts:296-309`, `:249-282` |
| Domain API modules (`shared/api/tauri*.ts`) | Per-feature-area façade over `invokeTauri`; owns Raw*↔domain-type field mapping (snake_case wire ↔ camelCase domain) | One exported async function per command, one module per feature area | `desktop/src/shared/api/tauriEvents.ts:1-14` |
| Backend→frontend event channel | Fire-and-forget state push independent of any command's return value | `AppHandle::emit(name, payload)` (Rust) ↔ `listen(name, cb)` / `emit(name, payload)` (`@tauri-apps/api/event`, frontend) | `desktop/src-tauri/src/huddle/state.rs:540-544`, `desktop/src/features/huddle/components/HuddleIndicator.tsx:204` |
| Capability allowlist | Restricts which Tauri core/plugin permissions (not commands — see *Boundary*) the `main`/`huddle-*` webviews may invoke at all | `desktop/src-tauri/capabilities/default.json` | `desktop/src-tauri/capabilities/default.json:1-31` |
| CSP `connect-src: ipc:` grant | Transport-level permission for the IPC channel itself, enforced by the webview independently of the capability allowlist | `tauri.conf.json`'s `security.csp` | `desktop/src-tauri/tauri.conf.json:39` |
| E2E mock bridge | Replaces `window.__TAURI_INTERNALS__` (including `invoke`) in E2E builds so specs exercise the same command/event contract without a real backend process | `desktop/src/testing/e2eBridge.ts`, installed by `main.tsx`'s `installE2eBridgeIfConfigured` | `desktop/src/testing/e2eBridge.ts:14604-14611`, `desktop/src/main.tsx:111-132` |

## Boundary

This node does not describe:
- The desktop container's own deployment topology, release lane, or its
  outbound interfaces to the relay and managed-agent subprocesses — see
  `architecture-containers-desktop` for those.
- External actors (human owner, relay operator) — see the architecture-context
  layer, not yet instantiated in this corpus.
- Any individual command's business logic (channels, messages, identity,
  agents, media, etc.) — each is its own future corpus node; this node
  documents the mechanism they are all built on, not what any one of them
  does.
- Whether the `capabilities/default.json` allowlist or the `invoke_handler!`
  registration is the "real" gate: they are **both** enforced, independently
  — a command absent from `invoke_handler!` cannot be dispatched at all, and
  a plugin/core API absent from the capability file is refused by Tauri's
  permission layer even if a command tried to use it internally. This node
  treats them as two separate boundary components (see the building-block
  table) rather than collapsing them into one.

## Relationships

- part-of: architecture-containers-desktop

## Scope and omissions

**This node covers** the mechanism by which the desktop frontend and backend
processes call into and signal each other: the command registration and
dispatch path, the shared `AppState` every command reaches through, the
frontend-side `invokeTauri` wrapper and its per-feature domain modules, the
wire-format case-conversion behavior (and its one identified inconsistency),
the backend→frontend event-push channel, the two independently-enforced
access boundaries (capability allowlist, CSP transport grant), and the E2E
mock substitute for the whole bridge.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Any individual command's business logic or domain data model | A future per-feature corpus node (channels, messages, identity, agents, media, etc. — none yet exist in the merged corpus) |
| The desktop container's deployment, release lane, and outbound relay/subprocess interfaces | `architecture-containers-desktop` |
| The mesh-llm feature-gated commands' own coordination protocol | Out of scope per `architecture-containers-desktop`'s own stated boundary; this node only counted them among the 336 registered commands, did not inspect their internals |
| The React frontend's component/feature architecture beyond its API-layer call sites | Not yet owned by any merged corpus node |
| Whether `#[serde(rename_all = "camelCase")]`'s inconsistent use across command-argument structs should be standardized | An implementation decision, not a documentation task; out of scope per issue #1241's own "Out of scope" section |

**Expected but not verified when this node was written:**

- **Not every one of the 336 registered commands was individually read.** The
  building-block table's claims rest on a representative sample
  (`get_presence`, `archive_channel`, `get_thread_replies`) plus the
  mechanical count of registered entries; a command whose signature departs
  from the `State<'_, AppState>` / `Result<T, String>` pattern observed in
  the sample would not have been caught.
- **The full population of `AppHandle::emit` call sites was counted by a
  structural grep, not read individually.** The `huddle-state-changed`
  pairing was verified end-to-end (backend emit, two independent frontend
  listeners); the other 48 emit sites were not each traced to a confirmed
  frontend listener.
- **Whether `type: platforms` is this corpus's eventual settled convention**
  for the `platforms/desktop/*` batch (as opposed to `type: architecture`,
  which the template this node borrows its shape from directs toward) is
  recorded here as an `INFERENCE`, not resolved — see this node's own
  evidence ledger.
- **The capability allowlist's completeness was not cross-checked against
  every command's own internal use of Tauri plugin APIs** — this node
  confirms the allowlist exists and is scoped to specific windows and
  permissions, not that every command's actual runtime behavior stays
  within it.

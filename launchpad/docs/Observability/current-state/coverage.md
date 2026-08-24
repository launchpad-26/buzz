# Canonical component coverage inventory

> Stage-1 completeness record tracked by
> [issue #462](https://github.com/launchpad-26/buzz/issues/462).

## Contract and evidence

This inventory assigns every shipped or runnable, non-mobile, Buzz-controlled product
emission or diagnostic boundary to one current-state assessment group. It is an inventory,
not a component assessment, desired state, gap analysis, strategy, or implementation plan.
The stable component IDs below are the canonical owners used by the reconciliation
registers later in this document; there is no miscellaneous owner.

All repository-inspection evidence has cutoff **2026-08-22** and is pinned to
[`26920e5c30d8a07a3d59c306d4e2b9056750e762`](https://github.com/launchpad-26/buzz/tree/26920e5c30d8a07a3d59c306d4e2b9056750e762)
(`26920e5c`). The completed web assessment is pinned separately to
[`678008ea49e790ada52e84d54b47f47dd77c6b38`](https://github.com/launchpad-26/buzz/tree/678008ea49e790ada52e84d54b47f47dd77c6b38)
(`678008ea`) — the repository revision that assessment inspected, as declared in
[web.md](web.md)'s verification metadata; the completed document itself landed later, in
`26920e5c`. Inspection covered Cargo metadata and manifests, release and container
packaging, process entry points, router and protocol registrations, Tauri invoke/event/
channel registrations, frontend route trees, ACP/MCP dispatch, CLI parsers, worker
spawns, adapters, subprocess calls, and signal/export registrations. Source inspection
establishes a bounded component and its owner; it is not runtime proof.

The PRD's terminal evidence states are:

- **Assessed** — component-level current-state evidence is complete in the assigned issue.
- **Bounded unknown** — the assigned assessment examined the component's current behavior,
  but could not establish a named property; the row records that specific uncertainty and
  the evidence boundary.
- **Excluded** — the row was examined and is outside PRD #289, with the reason and owner
  of any adjacent work recorded.

During stage-1 execution the matrix also uses one transitional workflow state:

- **Pending assessment** — the component boundary and assessment owner are verified, but
  the assigned component-level assessment has not completed. This is not a bounded
  unknown. Each pending row must become Assessed, Bounded unknown, or Excluded from the
  evidence produced by its assigned issue before Gate 2 can pass.

## Coverage matrix

### Relay

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| R01 | Relay process | Transport ingress and host routing | HTTP listener, WebSocket upgrade, NIP-11/NIP-05, tenant host resolution, middleware, and static web/admin fallbacks | `crates/buzz-relay/src/main.rs`; `router.rs`; `tenant.rs`; `connection.rs`; `api/mod.rs` | [#463](https://github.com/launchpad-26/buzz/issues/463) | `26920e5c` source registration | Pending assessment | Included product ingress; component runtime signal behavior awaits #463. |
| R02 | Relay process | Authentication and admission | NIP-42/NIP-98 verification, authorization, membership, connection/event/query gates, rate and concurrency limits | `crates/buzz-auth`; `buzz-relay/src/admission.rs`; `connection.rs`; `handlers/auth.rs` | [#463](https://github.com/launchpad-26/buzz/issues/463) | `26920e5c` source registration | Pending assessment | Included product security boundary; component runtime signal behavior awaits #463. |
| R03 | Relay process | Invite and join-policy service | Invite creation/claim, public policy, acceptance, terms, and privacy surfaces | `buzz-relay/src/api/invites.rs`; `invite_token.rs`; `router.rs` | [#463](https://github.com/launchpad-26/buzz/issues/463) | `26920e5c` source registration | Pending assessment | Included product admission feature; component runtime signal behavior awaits #463. |
| R04 | Relay process | Event ingestion and event-kind dispatch | WebSocket `EVENT`, HTTP event submission, verification, kind routing, persistence side effects, and thread counters | `buzz-relay/src/connection.rs`; `api/events.rs`; `handlers/{event,ingest,side_effects}.rs`; `crates/buzz-core` | [#464](https://github.com/launchpad-26/buzz/issues/464) | `26920e5c` source registration | Pending assessment | Included product event path; component runtime signal behavior awaits #464. |
| R05 | Relay process | Query, count, and search execution | WebSocket `REQ`/`COUNT`, HTTP query/count, filters, NIP-50 full-text search, and response streaming | `buzz-relay/src/connection.rs`; `api/bridge.rs`; `handlers/{req,count}.rs`; `crates/buzz-search` | [#464](https://github.com/launchpad-26/buzz/issues/464) | `26920e5c` source registration | Pending assessment | Included product read path; component runtime signal behavior awaits #464. |
| R06 | Relay process | Subscriptions and event fan-out | Subscription registry, `CLOSE`, initial/end-of-stored-events delivery, live fan-out, backpressure, and connection delivery | `buzz-relay/src/subscription.rs`; `connection.rs`; `handlers/close.rs`; `state.rs` | [#464](https://github.com/launchpad-26/buzz/issues/464) | `26920e5c` source registration | Pending assessment | Included realtime product path; component runtime signal behavior awaits #464. |
| R07 | Relay process | Presence and typing realtime service | Presence, typing indicators, local/Redis propagation, and timeout/state cleanup | `crates/buzz-pubsub`; `buzz-relay/src/main.rs`; `handlers/side_effects.rs` | [#464](https://github.com/launchpad-26/buzz/issues/464) | `26920e5c` source registration | Pending assessment | Included realtime product state; component runtime signal behavior awaits #464. |
| R08 | Relay process | Huddle admission and room lifecycle | Huddle authorization, room membership, participant state, and active-room lifecycle | `buzz-relay/src/audio/{join,handler,room}.rs` | [#465](https://github.com/launchpad-26/buzz/issues/465) | `26920e5c` source registration | Pending assessment | Included product huddle boundary; component runtime signal behavior awaits #465. |
| R09 | Relay process | Huddle audio transport | Audio WebSocket frames, local broadcast, mesh/tunnel forwarding, and audio-session cleanup | `buzz-relay/src/audio/{handler,mesh,wire}.rs`; `tunnel/` | [#465](https://github.com/launchpad-26/buzz/issues/465) | `26920e5c` source registration | Pending assessment | Included product media transport; component runtime signal behavior awaits #465. |
| R10 | Relay process and Git children | Git smart HTTP and policy | Upload/receive pack, repository resolution, policy hook, Git child processes, and repository storage | `buzz-relay/src/api/git/{transport,policy,store,hook}.rs` | [#466](https://github.com/launchpad-26/buzz/issues/466) | `26920e5c` source registration | Pending assessment | Included product Git and subprocess boundary; component runtime signal behavior awaits #466. |
| R11 | Relay process | Media and object service | Blossom/media upload, download, range/head, metadata, thumbnail/object-store operations, and S3-compatible adapter calls | `crates/buzz-media`; `buzz-relay/src/api/media.rs` | [#466](https://github.com/launchpad-26/buzz/issues/466) | `26920e5c` source registration | Pending assessment | Included product media and Buzz-owned adapter boundary; component runtime signal behavior awaits #466. |
| R12 | Relay process | Workflow engine and scheduler | Definitions, webhook/event/cron triggers, conditions, approvals, run state, and action/event sinks | `crates/buzz-workflow`; `buzz-relay/src/api/workflows.rs`; `workflow_sink.rs`; `main.rs` | [#467](https://github.com/launchpad-26/buzz/issues/467) | `26920e5c` source registration | Pending assessment | Included product automation boundary; component runtime signal behavior awaits #467. |
| R13 | Relay process | Relay-side agent integration | Agent registration/ownership/auth, observer frames, profiles, presence, wake, and turn/usage events | `buzz-relay/src/handlers/{auth,event,ingest,req,side_effects}.rs`; `workflow_sink.rs` | [#467](https://github.com/launchpad-26/buzz/issues/467) | `26920e5c` source registration | Pending assessment | Included product agent boundary; component runtime signal behavior awaits #467. |
| R14 | Relay process | Operator and community administration | Operator community create/archive/unarchive/transfer/availability and membership administration | `buzz-relay/src/api/operator.rs`; `api/admin/`; `handlers/relay_admin.rs`; `router.rs` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source registration | Pending assessment | Included operator product boundary; component runtime signal behavior awaits #468. |
| R15 | Relay process | Moderation and product feedback | Reports, decisions, restricted state, notices, feedback, and feedback attachments | `buzz-relay/src/handlers/{moderation_authz,moderation_commands,moderation_notices,product_feedback,report}.rs`; `api/admin/` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source registration | Pending assessment | Included product/operator diagnostic boundary; component runtime signal behavior awaits #468. |
| R16 | Relay process and database | Audit record and integrity service | Audit record schema/production, tamper-evident hash chain, storage/query, and integrity outcomes | `crates/buzz-audit`; relay audit call sites | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source registration | Pending assessment | Included Buzz-controlled audit record/integrity boundary; component runtime signal behavior awaits #468. |
| R17 | Relay process and database | Deletion, recovery, and identity archive | Deletion requests, lifecycle transitions, recovery, archive/unarchive, and cleanup | `crates/buzz-deletion`; `buzz-relay/src/handlers/{command_executor,event,ingest,side_effects,identity_archive}.rs` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source registration | Pending assessment | Included product lifecycle boundary; component runtime signal behavior awaits #468. |
| R18 | Relay process | Process startup and shutdown | Configuration, migration, listener binding, state assembly, startup gates, and graceful-shutdown orchestration | `crates/buzz-relay/src/main.rs`; `config.rs`; `state.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included product process lifecycle; component runtime signal behavior awaits #469. |
| R19 | Relay tasks | Background maintenance workers | Membership/channel reconciliation, workflow cron, reapers, reminders, community revalidation, storage/usage/pool pollers, and serving leases | `buzz-relay/src/main.rs`; `storage_sweep.rs`; worker spawns named in the startup register below | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included product background execution; component runtime signal behavior awaits #469. |
| R20 | Relay process and PostgreSQL | PostgreSQL adapter and data access | Pools/read replica, migrations, repositories, partition management, datastore spans, and replica fencing | `crates/buzz-db`; `crates/buzz-datastore-tracing`; `buzz-relay/src/main.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included Buzz-owned adapter; call-outcome/correlation/export evidence awaits #469, while PostgreSQL internals are X04. |
| R21 | Relay tasks and Redis | Redis pub/sub and control adapter | Connection pools, event fan-out, presence/typing, cache invalidation, and connection-control consumers | `crates/buzz-pubsub`; `buzz-relay/src/main.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included Buzz-owned adapter; consumer-liveness/correlation/export evidence awaits #469, while Redis internals are X04. |
| R22 | Relay tasks and peers | Relay mesh, tunnel, and peer adapter | Mesh boot, peer registry/heartbeat, sessions, tunnels, status, and testbed echo route | `crates/buzz-relay-mesh`; `buzz-relay/src/mesh_boot.rs`; `tunnel/`; `api/mesh_demo.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included Buzz-owned adapter; peer-call/session/correlation/export evidence awaits #469, while peer internals are X04. |
| R23 | Relay tasks and push endpoint | Relay-side push matching and delivery adapter | Push-subscription matching, delivery queue, retry, wake, and push-gateway HTTP boundary | `buzz-relay/src/push_runtime.rs`; `main.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included non-mobile relay adapter; the mobile-only gateway runtime is excluded in X02. |
| R24 | Relay process | Structured logging and trace export | JSON stdout subscriber, span/event filters, trace context, optional OTLP/gRPC export, and shutdown flush | `buzz-relay/src/telemetry.rs`; instrumentation call sites | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included explicit product signal/export surface; component-level reassessment awaits #469. |
| R25 | Relay process | Metrics, health, and diagnostic endpoints | Prometheus recorder/listener, metric pollers, liveness/readiness/status/mesh diagnostics, and dependency checks | `buzz-relay/src/metrics.rs`; `main.rs`; `router.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included explicit product signal/diagnostic surface; component-level reassessment awaits #469. |
| R26 | Relay background task | Audit writer lifecycle | Bounded audit queue, asynchronous writer task, backpressure/failure behavior, shutdown signal, drain, and flush | `crates/buzz-audit`; `buzz-relay/src/state.rs`; `main.rs` | [#469](https://github.com/launchpad-26/buzz/issues/469) | `26920e5c` source registration | Pending assessment | Included background execution boundary distinct from R16 record integrity; runtime signal behavior awaits #469. |

### Admin browser client

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| O01 | Admin browser tab | Admin web shell, routing, and API adapter | React bootstrap, history routing, same-origin authenticated fetch, resource state, and API errors | `admin-web/src/main.tsx`; `App.tsx`; `api.ts`; `useResource.ts` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source/packaging registration | Pending assessment | Included shipped operator browser boundary; component runtime signal behavior awaits #468. |
| O02 | Admin browser tab | Moderation report console | Report list/detail views, target/message rendering, access-denied state, retry, and navigation | `admin-web/src/App.tsx`; `types.ts`; relay `api/admin/` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source/packaging registration | Pending assessment | Included shipped operator/moderation surface; component runtime signal behavior awaits #468. |
| O03 | Admin browser tab | Product-feedback console and local state | Feedback list/detail/filtering, attachment proxy links, acted-on local storage, loading/error/retry UI, and browser diagnostics | `admin-web/src/App.tsx`; `api.ts`; relay `api/admin/` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source/packaging registration | Pending assessment | Included shipped operator/diagnostic surface; component runtime signal behavior awaits #468. |

### Desktop native and frontend

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| D01 | Desktop native parent | Native lifecycle, plugins, windows, and tray | Tauri startup, app state, plugins, window creation, single-instance behavior, tray/menu, updater, and shutdown | `desktop/src-tauri/src/main.rs`; `lib.rs`; `initial_window.rs`; `app_menu.rs`; `tray_menu.rs`; `shutdown.rs` | [#470](https://github.com/launchpad-26/buzz/issues/470) | `26920e5c` source registration | Pending assessment | Included shipped desktop parent; component runtime signal behavior awaits #470. |
| D02 | Desktop native parent | Relay transport, signing, and native WebSocket | Relay URL/auth/signing/query/publish, reconnect hook, HTTP bridge, and plugin WebSocket channels | `desktop/src-tauri/src/relay.rs`; `relay_admission.rs`; `nostr_bind.rs`; `native_websocket.rs`; `commands/relay_reconnect.rs` | [#470](https://github.com/launchpad-26/buzz/issues/470) | `26920e5c` source registration | Pending assessment | Included desktop transport boundary; component runtime signal behavior awaits #470. |
| D03 | Desktop native parent | Identity and community lifecycle | Keys, backup/import, profiles, BuilderLab auth/community operations, membership, sign-out, and identity archive | `desktop/src-tauri/src/{identity_storage,key_backup,builderlab,secret_store}.rs`; `commands/{identity,profile,relay_members,identity_archive}.rs` | [#470](https://github.com/launchpad-26/buzz/issues/470) | `26920e5c` source registration | Pending assessment | Included desktop security/product state; component runtime signal behavior awaits #470. |
| D04 | Desktop native parent | Local archive, migrations, and saved subscriptions | SQLite/archive initialization, event/observer/usage persistence, save subscriptions, and legacy storage migration | `desktop/src-tauri/src/archive/`; `migration.rs`; `commands/{legacy_storage,observer_archive,agent_metric_archive}.rs` | [#470](https://github.com/launchpad-26/buzz/issues/470) | `26920e5c` source registration | Pending assessment | Included Buzz-controlled diagnostic/product persistence; component runtime signal behavior awaits #470. |
| D05 | Desktop native parent | Platform integration and navigation | Deep links, native notifications, clipboard, workspace, media proxy/link preview, sleep prevention, pairing, haptics, and OS idle state | `desktop/src-tauri/src/deep_link.rs`; `macos_notifications.rs`; `media_proxy.rs`; `prevent_sleep.rs`; `commands/{notifications,workspace,pairing,clipboard}.rs` | [#470](https://github.com/launchpad-26/buzz/issues/470) | `26920e5c` source registration | Pending assessment | Included desktop platform boundary; component runtime signal behavior awaits #470. |
| D06 | Desktop webview | Frontend bootstrap, routes, and application shell | React/TanStack bootstrap, providers, route tree, navigation, layouts, query client, and root error boundary | `desktop/src/main.tsx`; `app/App.tsx`; `app/router.tsx`; `app/routeTree.gen.ts`; `app/routes/` | [#471](https://github.com/launchpad-26/buzz/issues/471) | `26920e5c` source registration | Pending assessment | Included shipped webview runtime; component runtime signal behavior awaits #471. |
| D07 | Desktop webview | Conversation and realtime feature UI | Channels, chat, messages, forum, home, feed, search, pulse, reminders, presence, status, emoji, and sidebar | `desktop/src/features/{channels,chat,messages,forum,home,search,pulse,reminders,presence,user-status,custom-emoji,sidebar}` | [#471](https://github.com/launchpad-26/buzz/issues/471) | `26920e5c` source registration | Pending assessment | Included product feature boundary; component runtime signal behavior awaits #471. |
| D08 | Desktop webview | Agent, project, workflow, and archive feature UI | Agent/project/workflow screens, memory, local archive, channel templates, mesh compute, and terminal UI orchestration | `desktop/src/features/{agents,agent-memory,projects,workflows,local-archive,channel-templates,mesh-compute,terminal}` | [#471](https://github.com/launchpad-26/buzz/issues/471) | `26920e5c` source registration | Pending assessment | Included product feature boundary; component runtime signal behavior awaits #471. |
| D09 | Desktop webview | Community, identity, settings, and moderation UI | Community switching/members, onboarding, profile, settings, moderation, notifications, and identity archive views | `desktop/src/features/{communities,community-members,onboarding,profile,settings,moderation,notifications,identity-archive}` | [#471](https://github.com/launchpad-26/buzz/issues/471) | `26920e5c` source registration | Pending assessment | Included product feature boundary; component runtime signal behavior awaits #471. |
| D10 | Desktop webview | Frontend state and diagnostic surfaces | Query caches, local/session storage, DOM event bus, console output, toasts, inline errors, and root recovery UI | `desktop/src/shared/`; `app/RootErrorBoundary.tsx`; feature hooks/stores | [#471](https://github.com/launchpad-26/buzz/issues/471) | `26920e5c` source registration | Pending assessment | Included product emission/diagnostic boundary; component runtime signal behavior awaits #471. |
| D11 | Desktop native parent and huddle window | Huddle lifecycle and audio session | Start/join/leave/end, companion window, capture/playout, reconnect, speaker/PTT state, and cross-window audio events | `desktop/src-tauri/src/huddle/`; `desktop/src/features/huddle/` | [#472](https://github.com/launchpad-26/buzz/issues/472) | `26920e5c` source registration | Pending assessment | Included desktop media workflow; component runtime signal behavior awaits #472. |
| D12 | Desktop native parent and model children | Voice, STT, and TTS pipeline | Voice models, device selection, transcription, synthesis, preview/import, agent voice, and model subprocesses | `crates/buzz-voice`; `desktop/src-tauri/src/huddle/{stt,tts*,voice*}.rs` | [#472](https://github.com/launchpad-26/buzz/issues/472) | `26920e5c` source registration | Pending assessment | Included desktop voice/subprocess boundary; component runtime signal behavior awaits #472. |
| D13 | Desktop native parent | Desktop media transfer | Pick/upload/download/fetch/cancel/release, clipboard/image save, and progress/phase events | `desktop/src-tauri/src/commands/media*.rs`; `commands/clipboard.rs`; `lib.rs` registration | [#472](https://github.com/launchpad-26/buzz/issues/472) | `26920e5c` source registration | Pending assessment | Included desktop media boundary; component runtime signal behavior awaits #472. |
| D14 | Desktop native parent and managed child | Agent discovery, installation, and supervision | ACP/provider discovery, prerequisite probes, install/config, restore/start/stop/restart, readiness, status, and retained child logs | `desktop/src-tauri/src/managed_agents/`; `commands/agent_discovery/`; `commands/{agents,agent_logs,agent_providers}.rs` | [#473](https://github.com/launchpad-26/buzz/issues/473) | `26920e5c` source registration | Pending assessment | Included desktop-managed subprocess boundary; component runtime signal behavior awaits #473. |
| D15 | Desktop native parent and PTY child | Terminal runtime | `buzz-terminal`, PTY spawn/attach/input/resize/scroll/ack/focus/close, and typed Tauri channel output | `crates/buzz-terminal`; `desktop/src-tauri/src/terminal_runtime.rs` | [#473](https://github.com/launchpad-26/buzz/issues/473) | `26920e5c` source registration | Pending assessment | Included desktop subprocess/IPC boundary; component runtime signal behavior awaits #473. |
| D16 | Desktop native parent and child processes | Project Git, shell, compute, and provider subprocesses | Clone/sync/branch/merge/terminal recovery, external tools, backend/provider probes, mesh model process, and child I/O | `desktop/src-tauri/src/commands/project_git*.rs`; `commands/project_terminal.rs`; `mesh_llm/`; `managed_agents/backend.rs` | [#473](https://github.com/launchpad-26/buzz/issues/473) | `26920e5c` source registration | Pending assessment | Included desktop subprocess boundary; component runtime signal behavior awaits #473. |

### Browser web client

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| W01 | Browser tab | Web bootstrap, route tree, and error UI | React bootstrap and routes for home, invite, repository list/detail, and blob views | `web/src/main.tsx`; `app/router.tsx`; `app/routeTree.gen.ts`; `app/routes/` | [#460](https://github.com/launchpad-26/buzz/issues/460) | `678008ea` component assessment | Assessed | Included; current-state evidence completed by #460. |
| W02 | Browser tab | Invite and join-policy flow | Invite lookup/claim, terms/privacy, policy acceptance, and rendered errors | `web/src/features/invite/invite-api.ts`; `features/invite/ui/` | [#460](https://github.com/launchpad-26/buzz/issues/460) | `678008ea` component assessment | Assessed | Included; current-state evidence completed by #460. |
| W03 | Browser tab | Nostr relay transport and signer | Browser WebSocket, filters, NIP-42, signing, NIP-98 authorization, connection state, and query failures | `web/src/shared/lib/{nostr-client,nostr-signer,nip98}.ts` | [#460](https://github.com/launchpad-26/buzz/issues/460) | `678008ea` component assessment | Assessed | Included; current-state evidence completed by #460. |
| W04 | Browser tab | Repository browser and Git transport | Repository queries, isomorphic-git fetch/read, release downloads, and UI/query errors | `web/src/features/repos/`; `web/src/shared/lib/buzz-download.ts` | [#460](https://github.com/launchpad-26/buzz/issues/460) | `678008ea` component assessment | Assessed | Included; current-state evidence completed by #460. |
| W05 | Browser tab and IndexedDB | Browser storage and diagnostic/export boundary | LightningFS/IndexedDB state, rendered/loading errors, console and DevTools visibility, and absence of a telemetry exporter | `web/src/features/repos/git-client.ts`; feature query/error paths; `features/repos/ui/RepoDetailPage.tsx` | [#460](https://github.com/launchpad-26/buzz/issues/460) | `678008ea` component assessment | Assessed | Included; current-state evidence completed by #460. |

### ACP harness

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| A01 | `buzz-acp` process | Harness startup, configuration, and setup | Environment/config validation, identity/auth setup, agent command selection, and process lifecycle | `crates/buzz-acp/src/main.rs`; `config.rs`; `setup_mode.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included shipped harness boundary; component runtime signal behavior awaits #474. |
| A02 | `buzz-acp` process | Relay transport and reconnect | NIP-42 WebSocket/HTTP, reconnect, subscriptions, channel discovery, heartbeat, presence, and publish | `buzz-acp/src/relay.rs`; `main.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included relay-facing harness boundary; component runtime signal behavior awaits #474. |
| A03 | `buzz-acp` process | Event filter and authorization gate | Event-kind/channel/author filtering, ownership checks, validation, and deduplication | `buzz-acp/src/filter.rs`; `relay.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included product admission boundary; component runtime signal behavior awaits #474. |
| A04 | `buzz-acp` process | Prompt queue and steering | Bounded queue, duplicate suppression, turn dispatch, cancellation, and steering/coalescing | `buzz-acp/src/queue.rs`; `main.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included product execution boundary; component runtime signal behavior awaits #474. |
| A05 | `buzz-acp` parent and agent child | ACP client and child supervision | Spawn/process group, stdin/stdout JSON-RPC, size bounds, crash/restart/circuit behavior, and session pool | `buzz-acp/src/acp.rs`; `pool.rs`; `main.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included subprocess/protocol boundary; component runtime signal behavior awaits #474. |
| A06 | `buzz-acp` process | ACP method bridge | Initialize/authenticate, session create/config/model/prompt/cancel/steer, updates, and permission requests | `buzz-acp/src/acp.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included ACP protocol family; component runtime signal behavior awaits #474. |
| A07 | `buzz-acp` process | Observer, usage, and turn-signal bridge | Observer events, Engram fetch/context, usage extraction, agent metrics, turn timing, and publish results | `buzz-acp/src/observer.rs`; `usage.rs`; `engram_fetch.rs`; `main.rs` | [#474](https://github.com/launchpad-26/buzz/issues/474) | `26920e5c` source registration | Pending assessment | Included explicit product signal boundary; component runtime signal behavior awaits #474. |

### Buzz agent and developer MCP

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| G01 | `buzz-agent` process | Agent ACP server | ACP initialize/session create/prompt/model/cancel/steer dispatch and session-update/usage notifications | `crates/buzz-agent/src/lib.rs`; `main.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included shipped ACP server; component runtime signal behavior awaits #475. |
| G02 | `buzz-agent` process | Agent session and model loop | Session state, history, turns, tool budget, compaction/handoff, cancellation, and output updates | `buzz-agent/src/{agent,builtin,handoff,hints}.rs`; `lib.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included product execution boundary; component runtime signal behavior awaits #475. |
| G03 | `buzz-agent` process and provider APIs | LLM provider adapters and model catalog | OpenAI, Anthropic, Databricks, OpenRouter, OpenAI-compatible providers, authentication, retry, and model discovery | `buzz-agent/src/llm.rs`; `auth.rs`; `catalog.rs`; `config.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included Buzz-owned adapters; call/retry/correlation/export evidence awaits #475, while provider internals are X04. |
| G04 | `buzz-agent` parent and MCP children | MCP client and child supervision | MCP server discovery/spawn, initialize, tool list/call, hooks, restart/backoff, and child I/O | `buzz-agent/src/mcp.rs`; `config.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included subprocess/protocol boundary; component runtime signal behavior awaits #475. |
| M01 | `buzz-dev-mcp` process | Developer MCP protocol server | stdio MCP initialization, capabilities, tool enumeration/calls, shutdown, and multicall dispatch | `crates/buzz-dev-mcp/src/{main,lib}.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included shipped MCP server; component runtime signal behavior awaits #475. |
| M02 | `buzz-dev-mcp` process and shell children | Shell tool boundary | `shell` execution, environment/workdir, timeout, output, exit, and child-process behavior | `buzz-dev-mcp/src/shell.rs`; `lib.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included tool/subprocess boundary; component runtime signal behavior awaits #475. |
| M03 | `buzz-dev-mcp` process | File and image tools | `read_file`, `view_image`, and `str_replace` access, validation, results, and errors | `buzz-dev-mcp/src/{read_file,view_image,str_replace}.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included tool/diagnostic boundary; component runtime signal behavior awaits #475. |
| M04 | `buzz-dev-mcp` process | Turn-control, paths, and shim lifecycle | `todo`, `_Stop`, `_PostCompact`, artifact paths, executable shims, key setup, and server-side diagnostics | `buzz-dev-mcp/src/{todo,paths,shim}.rs`; `main.rs` | [#475](https://github.com/launchpad-26/buzz/issues/475) | `26920e5c` source registration | Pending assessment | Included tool/control boundary; component runtime signal behavior awaits #475. |

### First-party tools and shared seams

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| T01 | `buzz` CLI process | Agent-first CLI command surface | All top-level command families and output/exit contracts enumerated below | `crates/buzz-cli/src/lib.rs`; `client.rs`; command modules | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included shipped first-party client; component runtime signal behavior awaits #476. |
| T02 | First-party tool process (in-process libraries) | Nostr WebSocket and event-builder seam | Authenticated connect/query/publish, typed event construction, transport/protocol failures, and results used by first-party runtimes | `crates/buzz-ws-client`; `crates/buzz-sdk` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included through the consuming tool runtime because the seam owns material transport/protocol failure boundaries; runtime signal behavior awaits #476. |
| T03 | Agent process (in-process library) | Persona pack seam | Persona filesystem discovery, parsing, resolution, packaging, and failure results used by agent runtimes | `crates/buzz-persona` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included because the shared library owns a material file/parse failure boundary; runtime signal behavior awaits #476. |
| T04 | `buzz-admin` process | Admin bootstrap and maintenance CLI | Key generation, migrations, and channel reconciliation not owned by relay lifecycle assessment | `crates/buzz-admin/src/main.rs` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included shipped operator CLI boundary; component runtime signal behavior awaits #476. |
| T05 | `buzz-admin` process | Admin lifecycle and feedback CLI | Membership, feedback, and deletion/recovery commands against relay lifecycle surfaces | `crates/buzz-admin/src/main.rs`; `deletions.rs` | [#468](https://github.com/launchpad-26/buzz/issues/468) | `26920e5c` source registration | Pending assessment | Included operator client for R14/R15/R17; component runtime signal behavior awaits #468. |
| T06 | `buzz-pair` process | Pairing interoperability CLI | Source, target, and test-vector command families for device-pairing interop | `crates/buzz-pairing-cli/src/main.rs` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included runnable first-party protocol client; component runtime signal behavior awaits #476. |
| T07 | `buzz-pair-relay` process | Ephemeral pairing sidecar relay | NIP-AB pairing relay listener, session forwarding, expiry, and process lifecycle | `crates/buzz-pair-relay/src/main.rs`; `lib.rs` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included shipped relay-image sidecar; component runtime signal behavior awaits #476. |
| T08 | Git helper processes | Nostr Git credential and signing helpers | Git credential protocol, Nostr-authenticated fetch/push credentials, and Nostr git-object signatures | `crates/git-credential-nostr`; `crates/git-sign-nostr` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source registration | Pending assessment | Included shipped/runnable subprocess boundaries; component runtime signal behavior awaits #476. |
| T09 | `sprig` multicall process | Bundled agent harness runtime | Multicall startup and personalities for ACP, agent, dev MCP, CLI, Git helpers, `rg`, and `tree` | `crates/sprig/src/main.rs`; `Dockerfile.sprig`; `scripts/bundle-sidecars.sh` | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source/packaging registration | Pending assessment | Included shipped composite; dispatch/stdout/stderr evidence awaits #476, while child components retain their own IDs. |
| T10 | `buzz-backend-kubernetes` process | Kubernetes backend provider | One-request stdin/stdout provider protocol, `Info`, `Deploy`, Kubernetes API/config adapter, reconciliation, and exit behavior | `crates/buzz-backend-kubernetes/src/main.rs`; `client.rs`; `reconcile.rs`; desktop sidecar packaging | [#476](https://github.com/launchpad-26/buzz/issues/476) | `26920e5c` source/packaging registration | Pending assessment | Included shipped desktop sidecar; component runtime signal behavior awaits #476. |

### Explicit exclusions

| ID | Runtime | Stable component name | Responsibility | Implementation entry points | Assigned assessment issue | Evidence revision | Current state | Inclusion/exclusion reason |
|---|---|---|---|---|---|---|---|---|
| X01 | Flutter/iOS/Android | Mobile application | All mobile product emission and diagnostic boundaries | `mobile/` | [PRD #289](https://github.com/launchpad-26/buzz/issues/289) | `26920e5c` scope decision | Excluded | PRD #289 explicitly excludes mobile; no mobile assessment was performed. |
| X02 | `buzz-push-gateway` process | Mobile push gateway | APNs/FCM-facing mobile notification delivery runtime | `crates/buzz-push-gateway`; `Dockerfile.push-gateway`; `helm/buzz-push-gateway/` | [PRD #289](https://github.com/launchpad-26/buzz/issues/289) | `26920e5c` source/packaging registration | Excluded | Mobile-only instrumentation is excluded. The non-mobile relay adapter remains R23. |
| X03 | Test/build/example processes | Validation and development fixtures | Conformance/test clients, fake MCP, benchmarks, examples, E2E bridges, build scripts, and screenshot tooling | `crates/buzz-conformance`; `buzz-test-client`; `fake-mcp`; `countdown-bot`; `tests/`; examples; build scripts | [PRD #289](https://github.com/launchpad-26/buzz/issues/289) | `26920e5c` source/target registration | Excluded | PRD #289 covers shipped/runnable product boundaries, not validation, fixtures, examples, or build tooling. |
| X04 | Third-party services | Dependency internals | PostgreSQL, Redis, object store, relay peers, push endpoint, LLM providers, Git, Kubernetes, OS, and browser internals | External processes/services beyond R11/R20-R23, G03, D05, D12, D16, and T10 adapter edges | [PRD #289](https://github.com/launchpad-26/buzz/issues/289) | `26920e5c` boundary inspection | Excluded | Only Buzz-controlled adapters and emitted boundary signals are in scope; dependency internals are not. |
| X05 | Operations platform | Collection, storage, querying, dashboards, alerts, retention, and deployment | Infrastructure after product export surfaces | Separate `buzz-infrastructure` repository and deployed systems | [buzz-infrastructure#113](https://github.com/launchpad-26/buzz-infrastructure/issues/113) | `26920e5c` boundary decision | Excluded | PRD #289 routes infrastructure collection/storage/dashboards/alerts/retention/deployment to #113. |

## Reconciliation registers

These registers prove that the matrix above was derived from the repository's enumerable
surfaces. A register entry maps to one stable component ID; shared container packages
may host several already-owned components, but do not create another assessment group.

### Rust workspace crates and binary targets

`cargo metadata --no-deps --format-version 1` was run for the root workspace and for
`desktop/src-tauri/Cargo.toml`. Every returned package and binary target is accounted for:

| Package or target | Binary target(s) | Canonical owner |
|---|---|---|
| `buzz-relay` | `buzz-relay` | R01-R26 (container); process lifecycle R18 |
| `buzz-audit` | — | R16 record service and R26 consuming worker runtime |
| `buzz-core` | — | R04 |
| `buzz-datastore-tracing` | — | R20 |
| `buzz-auth` | — | R02 |
| `buzz-conformance` | — | X03 |
| `buzz-db` | — | R20 |
| `buzz-deletion` | — | R17 |
| `buzz-media` | — | R11 |
| `buzz-pubsub` | — | R21 |
| `buzz-relay-mesh` | — | R22 |
| `buzz-sdk` | — | T02 through its consuming first-party runtime |
| `buzz-search` | — | R05 |
| `buzz-workflow` | — | R12 |
| `buzz-test-client` | `buzz-test-cli`, `mention`, `wamp_bench` | X03 |
| `buzz-ws-client` | — | T02 |
| `buzz-push-gateway` | `buzz-push-gateway` | X02 |
| `buzz-acp` | `buzz-acp` | A01-A07 (container); process lifecycle A01 |
| `buzz-persona` | — | T03 |
| `buzz-agent` | `buzz-agent`; `fake-mcp` test target | G01-G04; `fake-mcp` is X03 |
| `sprig` | `sprig` | T09 |
| `buzz-dev-mcp` | `buzz-dev-mcp` | M01-M04 (container); process lifecycle M01 |
| `buzz-cli` | `buzz` | T01 |
| `git-credential-nostr` | `git-credential-nostr` | T08 |
| `git-sign-nostr` | `git-sign-nostr` | T08 |
| `buzz-admin` | `buzz-admin` | T04/T05, partitioned by command family below |
| `buzz-pairing-cli` | `buzz-pair` | T06 |
| `buzz-pair-relay` | `buzz-pair-relay` | T07 |
| `buzz-voice` | — | D12 |
| `buzz-backend-kubernetes` | `buzz-backend-kubernetes` | T10 |
| `countdown-bot` | `countdown-bot` | X03 |
| `buzz-terminal` | — | D15 |
| `buzz-desktop` | `buzz-desktop` | D01-D16 (container); process lifecycle D01 |

Cargo examples (`compute_auth_tag`, relay-mesh smoke/example targets, and similar), tests,
benchmarks, build scripts, and generated E2E executables are X03. Packaging inspection
also reconciled the production boundary: the relay image contains `buzz-relay`,
`buzz-admin`, and `buzz-pair-relay` plus the public `web` and `admin-web` bundles; the
desktop external binaries contain `buzz-acp`,
`buzz-agent`, `buzz-backend-kubernetes` where supported, `buzz-dev-mcp`,
`git-credential-nostr`, and `buzz`; and the Sprig image exposes T09's multicall
personalities including `git-sign-nostr`, `rg`, and `tree`.

`buzz-conformance` is a production dependency, so it appears in the crate register. The
shipped relay binds `NoopTracer`; its JSONL emitter is expressly for conformance tests and
the CI replay job. The emitting path is therefore X03 rather than shipped product
telemetry. Pure shared libraries without a materially distinct diagnostic/export boundary,
such as `buzz-core`, are assigned through the consuming runtime shown above.

### Relay HTTP routes and WebSocket families

| Registered surface | Canonical owner |
|---|---|
| `GET /` (NIP-11 or WebSocket), `GET /info`, `GET /.well-known/nostr.json`, static admin/web fallback | R01 |
| `POST /events` | R04 |
| `POST /query`, `POST /count` | R05 |
| `GET /workflows/{workflow_id}/runs`, `GET /workflows/{workflow_id}/runs/{run_id}/approvals`, `POST /hooks/{id}` | R12 |
| `/operator/communities` create/list plus archive, unarchive, availability, and transfer routes | R14 |
| `POST /api/invites`, `GET /api/join-policy`, terms/privacy, policy acceptance, and invite claim routes | R03 |
| moderation reports/audit/restricted routes and `/api/admin/v1` report/feedback/attachment routes | R15 |
| `WS /huddle/{channel_id}/audio` | R09 |
| `PUT /upload`, `PUT /media/upload`, `GET/HEAD /media/{sha256_ext}` | R11 |
| Git `info/refs`, `git-upload-pack`, `git-receive-pack`, and `POST /internal/git/policy` | R10 |
| `POST /_mesh/demo/echo` (registered but feature-gated testbed path) | R22 |
| Application `GET /health`, `GET /_liveness`, `GET /_readiness`; separate listener `/_liveness`, `/_readiness`, `/_status`, `/_mesh`; metrics listener `GET /metrics` | R25 |

| WebSocket message family | Canonical owner |
|---|---|
| Client `AUTH`; relay `AUTH` challenge and protocol-level `NOTICE`/`OK` framing | R02 |
| Client `EVENT`; event acceptance/rejection and relay `OK` semantics | R04 |
| Client `REQ` and `COUNT`; relay stored `EVENT`, `EOSE`, and `COUNT` results | R05 |
| Client `CLOSE`; live relay `EVENT` delivery and `CLOSED` subscription result | R06 |

Feature-specific rejection text can be emitted through shared protocol frames without
changing the owning feature component. The table assigns the registered message family,
not every possible message string.

### Desktop entry points, Tauri commands, events, and channels

The native entry is `desktop/src-tauri/src/main.rs` -> `buzz_desktop::run`; the frontend
entry is `desktop/src/main.tsx`. The generated route tree registers `/`, `/agents`,
`/projects`, `/pulse`, `/reminders`, `/settings`, `/workflows`,
`/channels/$channelId`, `/messages/new`, `/projects/$projectId`,
`/workflows/$workflowId`, and `/channels/$channelId/posts/$postId`; these map to D06-D09.

The complete `tauri::generate_handler!` registration is partitioned as follows:

| Tauri command family | Canonical owner |
|---|---|
| `terminal_attach/detach/close/input/resize/scroll/ack/viewport_ready/focus` | D15 |
| pending community/navigation/entity deep links; title-bar, native notifications, pairing, clipboard, workspace, sleep, haptic, OS-idle, updater/vibrancy/tray commands | D05 |
| BuilderLab auth/community, identity/key/backup/import/profile, membership, sign-out, and identity archive commands | D03 |
| relay URL/config, signing/encryption/auth events, channel/message/feed/social/workflow relay operations, and reconnect hook | D02 |
| native WebSocket plugin `connect`, `send`, `disconnect`, `disconnect_all` | D02 |
| archive events/observer rows/usage series, saved subscriptions, archive defaults, and legacy workspace storage | D04 |
| project repository snapshot/diff/sync/clone/branch/push/pull/merge and project terminal/recovery commands | D16 |
| ACP/provider/prerequisite discovery, runtime installation/custom harness, and managed-agent lifecycle/config/models/personas/teams/cards/snapshots | D14 |
| Backend provider probes plus mesh model/node commands | D16 |
| media pick/upload/download/fetch/cancel/release/save/clipboard and snapshot-byte commands | D13 |
| huddle lifecycle/window/audio/reconnect/PTT/agent-participant commands | D11 |
| STT/transcription/model download/status, TTS/voice registry/preview/import, speech, input mode, and audio-output device commands | D12 |

Registered Tauri event names are also fully partitioned:

| Event names | Canonical owner |
|---|---|
| `initial-render-ready`, `mouse-nav` | D01 |
| `deep-link-connect`, `deep-link-join`, `deep-link-add-community`, `deep-link-channel`, `deep-link-message`, `deep-link-entity`, `deep-link-nostr-bind`, `native-notification-activated`, `prevent-sleep-expired`, `pairing-error`, `pairing-aborted`, `pairing-sas-received`, `pairing-complete`, `legacy-nest-migrated`, `repos-dir-error`, `tray-action-available` | D05 |
| `huddle-audio-disconnected`, `huddle-state-changed`, `huddle-companion-returned`, `huddle-active-speakers`, `huddle-speaker-levels`, `ptt-state`, plus frontend cross-window `huddle-audio-command/state/level` | D11 |
| `huddle-tts-speaker-level` | D12 |
| `agents-data-changed`, `managed-agent-runtime-status`, `acp-install-output` | D14 |
| `mesh-download-progress` | D16 |
| `media-upload-progress`, `media-upload-phase` | D13 |

The two typed Tauri channel families are `Channel<TerminalMessage>` (D15) and the native
WebSocket `Channel<serde_json::Value>` (D02). Frontend `buzz:*` DOM custom events are D10,
not unregistered Tauri channels.

### Browser entry points and routes

| Browser bundle | Entry point and routes | Canonical owner |
|---|---|---|
| Public `web` | `web/src/main.tsx`; `/`, `/invite/$code`, `/repos`, `/repos/$repoId`, `/repos/$repoId/blob/$` | W01-W05, partitioned by the matrix rows |
| Operator `admin-web` | `admin-web/src/main.tsx`; `/reports`, `/reports/:id`, `/feedback`, `/feedback/:id` (unknown paths fall back to reports) | O01-O03, partitioned by the matrix rows |

### ACP and MCP methods

| Protocol method family | Canonical owner |
|---|---|
| ACP outbound `initialize`, `authenticate` | A06 |
| ACP outbound `session/new`, `session/set_config_option`, `session/set_model`, `session/prompt`, `session/cancel`, `_goose/unstable/session/steer`, `_session/steering`, and `_goose/unstable/session/system-prompt/set` | A06 |
| ACP inbound `session/update`, `_goose/unstable/session/update`, `session/request_permission` | A06 |
| Agent ACP handlers `initialize`, `session/new`, `session/prompt`, `session/set_model`, `session/cancel`, and Goose steer; outbound session update and usage notifications | G01 |
| MCP client `initialize`/initialized handshake, `tools/list`, `tools/call`, `notifications/cancelled`, hidden hook calls, restart, and transport close | G04 |
| Developer MCP server `initialize`/initialized handshake, `ping`, `tools/list`, `tools/call`, cancellation, and transport close | M01 |
| Developer MCP tools `shell`, `read_file`, `view_image`, `str_replace`, `todo`, `_Stop`, `_PostCompact` | M02-M04, partitioned by the matrix rows |

### CLI command families

| Process | Command families | Canonical owner |
|---|---|---|
| `buzz` | `agents`, `messages`, `channels`, `canvas`, `reactions`, `emoji`, `dms`, `users`, `workflows`, `feed`, `social`, `notes`, `repos`, `projects`, `patches`, `issues`, `pr`, `media`, `upload`, `mem`, `pack`, `moderation` | T01 |
| `buzz-admin` | `add-member`, `remove-member`, `list-members`, `product-feedback`, `deletions` | T05 |
| `buzz-admin` | `generate-key`, `migrate`, `reconcile-channels` | T04 |
| `buzz-pair` | `source`, `target`, `test-vectors` | T06 |
| `buzz-backend-kubernetes` | stdin/stdout provider operations `Info`, `Deploy` | T10 |

### Startup tasks, workers, adapters, and subprocess boundaries

| Boundary | Canonical owner |
|---|---|
| Configuration, pools, migrations, state, listeners, and graceful-shutdown orchestration | R18 |
| Telemetry subscriber/exporter startup and flush | R24 |
| Audit bounded writer task and shutdown drain | R26 |
| PostgreSQL read-pool boot ping and replica-fence probe | R20 |
| Redis event subscriber, cache-invalidation subscriber, connection-control subscriber, and local consumers | R21 |
| Mesh boot consumers, registry heartbeat, sessions, and tunnel lifecycle | R22 |
| Git object conformance startup gate and Git pack/policy child processes | R10 |
| Membership snapshot startup/periodic reconciliation and optional channel discovery reconciliation | R19 |
| Workflow cron scheduler | R12 |
| Ephemeral channel reaper, NIP-ER reminder scheduler, community revalidator, serving-lease reaper/stats | R19 |
| NIP-PL push matcher and delivery worker | R23 |
| Pool, usage, storage, and relay metrics pollers | R25 |
| PostgreSQL/read-replica/migration/partition/fence adapter | R20 |
| S3-compatible object-store adapter | R11 |
| ACP-spawned agent child and bounded stdio JSON-RPC | A05 |
| Agent-spawned MCP children and provider HTTP adapters | G04 and G03 respectively |
| Desktop-managed ACP/agent/backend/mesh/model children and retained child logs/status | D14/D16 |
| Desktop PTY children | D15 |
| Desktop voice model/STT/TTS children | D12 |
| Dev-MCP shell children | M02 |
| Sprig multicall personalities | T09 |
| Kubernetes API/service boundary | T10 |

### Product signal, diagnostic, and export surfaces

| Surface | Canonical owner |
|---|---|
| Relay structured JSON stdout and optional OTLP/gRPC spans/events | R24 |
| Relay Prometheus `/metrics`, liveness, readiness, status, and mesh diagnostics | R25 |
| Relay audit records/integrity and worker flush/error boundary | R16 and R26 respectively |
| Desktop native stdout/stderr and parent lifecycle diagnostics | D01 |
| Desktop frontend console, toasts, inline errors, root error recovery, query and browser state | D10 |
| Desktop managed-child status and retained output | D14 |
| Desktop archive/save-subscription/agent-usage persistence | D04 |
| Desktop native WebSocket and terminal typed channels | D02 and D15 respectively |
| Admin-web same-origin fetch errors, loading/access/retry UI, local feedback status, and browser DevTools | O01/O03 by source |
| Web rendered errors, console/DevTools, IndexedDB state, and no product telemetry exporter | W05 |
| ACP stderr/protocol output, observer frames, usage, heartbeat/presence, agent-metric and turn events | A01/A02/A07 by source |
| Agent ACP updates/usage, provider/MCP errors, and stdio protocol boundary | G01/G03/G04 by source |
| Dev MCP stdio, tool results/errors, artifact/shim state, and child output | M01-M04 by source |
| First-party WebSocket/SDK/persona transport, construction, file, and parse failures returned to their consuming processes | T02/T03 |
| CLI stdout/stderr, structured result formats, and exit status | T01/T04-T10 by process |

Collection, durable storage, querying, dashboards, alerts, retention, and deployment after
these product boundaries are X05 and belong to
[buzz-infrastructure#113](https://github.com/launchpad-26/buzz-infrastructure/issues/113).

## Completeness statement

Every Cargo package/binary target, production package boundary, desktop/public-web/
admin-web entry point, relay route and WebSocket family, Tauri command/event/channel
family, ACP/MCP method family, CLI family, registered startup/background task,
first-party dependency adapter, subprocess edge, and product signal/export surface found
at the pinned revision maps to a named ID above. Mobile, mobile push,
test/build/example processes, dependency internals, and observability infrastructure are
examined exclusions X01-X05. There is no anonymous component bucket.

At this inventory checkpoint the matrix contains **5 Assessed**, **70 Pending
assessment**, and **5 Excluded** rows. Component assignment is complete; current-state
assessment is not. Issues #463-#476 own the pending assessments. As their evidence lands,
each assigned row must move to Assessed or to a specifically evidenced Bounded unknown
(or to Excluded if the assessment establishes that the inventory boundary was wrong).
Gate 2 cannot pass while any row remains Pending assessment.

Back to the [current-state overview](overview.md). Existing evidence deep dives remain
available for the [relay](relay.md), [desktop](desktop.md), and [web](web.md).

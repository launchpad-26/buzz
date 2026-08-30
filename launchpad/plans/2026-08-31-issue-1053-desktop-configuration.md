Issue #1053 — task: document layers/configuration/desktop-configuration.md
Stated size: no `Size` line -> cap: 5 steps (single hand-authored document, configuration.md template)

ALREADY TRUE  (verified against git, not notes)
  On `origin/launchpad` tip 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5 (task/1053-desktop-configuration
    branched from it); `launchpad/docs/corpus/layers/configuration/desktop-configuration.md` does not
    exist and `launchpad/docs/corpus/layers/` does not exist yet; `launchpad/docs/corpus/templates/
    configuration.md` (`corpus-template-configuration`) is merged; `launchpad/docs/corpus/architecture/
    containers/desktop.md` (`architecture-containers-desktop`) is merged and already documents the
    desktop container's relay-URL override chain and identity-storage backends at a higher altitude —
    a `references` target, not a duplicate. No `layers-*` node exists yet on `origin/launchpad`, so this
    is the first of its type.

STEP 1  [independent]  Gather evidence for desktop-app-level configuration (already substantially done in this
        session): `desktop/src-tauri/src/relay.rs` (env-var/build-time/workspace-override precedence
        for relay WS + HTTP URLs), `desktop/src-tauri/src/app_state.rs` (`BUZZ_PRIVATE_KEY` identity
        resolution precedence), `desktop/src-tauri/src/commands/identity.rs` (`get_default_relay_url`,
        `auto_connect_default_relay_enabled`), `desktop/src-tauri/src/commands/workspace.rs`
        (`apply_workspace`, `validate_repos_dir`), `desktop/src-tauri/src/managed_agents/repos.rs`
        (`.repos-dir` dotfile persistence), `desktop/src-tauri/src/managed_agents/nest.rs` (dev/prod
        nest-directory split), `desktop/src-tauri/tauri.conf.json` + `tauri.dev.conf.json` +
        `tauri.windows.conf.json` (build-time app manifest and its dev/platform overlays),
        `desktop/src/features/communities/communityStorage.ts` and `types.ts` (localStorage-persisted
        `Community` record shape), `desktop/src/features/communities/useCommunityInit.ts` (applies
        community config to the Tauri backend — the pattern this repo's root `CLAUDE.md` names under
        "Community Switching"), and `.env.example` (documents `BUZZ_PRIVATE_KEY`/`BUZZ_RELAY_URL` in
        the ACP-harness section, not desktop-specific). Record the one already-found open question:
        `Community.token` is threaded through `applyCommunity()`'s call to `apply_workspace`, but
        `apply_workspace`'s Rust signature has no `token` parameter, so the value is not applied to
        backend state on that path.
        done when: each source above has been opened and a one-line note taken naming the claim it
        will support; the `token` discrepancy is confirmed by re-reading both the TS call site and the
        Rust command signature side by side.

STEP 2  [needs 1]  <- RUNS HERE  Write `launchpad/docs/corpus/layers/configuration/desktop-
        configuration.md` from `templates/configuration.md`: schema-valid front matter (`id: layers-
        configuration-desktop-configuration`, `type: layers`, `status: draft`, `origin: launchpad`,
        `audiences`, an `evidence` ledger whose first entry is the HEAD commit citation, one
        `references` relationship to `architecture-containers-desktop`), plus the template's required
        sections: configuration description (desktop app process configuration — env vars read at
        process start, compile-time `BUZZ_DESKTOP_BUILD_*` constants, and the UI-configured/localStorage
        -persisted per-community settings applied to the Tauri backend via `apply_workspace`), a
        structured settings table (`BUZZ_RELAY_URL`, `BUZZ_RELAY_HTTP`, `BUZZ_PRIVATE_KEY`,
        `BUZZ_DESKTOP_BUILD_RELAY_URL`, `BUZZ_DESKTOP_BUILD_RELAY_HTTP`,
        `BUZZ_DESKTOP_BUILD_AUTO_CONNECT_DEFAULT_RELAY`, `Community.relayUrl`, `Community.reposDir`,
        plus the dev/prod/platform `tauri.conf.json` overlay identifiers), a litmus-test paragraph
        naming what was excluded (static CSP/window/bundle values that do not vary between deploys of
        the same build), a secrets-discipline paragraph (no live nsec/token quoted), a boundary
        paragraph naming `agentManagedProfiles`/per-agent env config as #1051/#1055's scope not this
        node's, the `token` discrepancy from STEP 1 as an honest note (not silently fixed or hidden),
        and scope-and-omissions.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with the file
        present, and every settings-table row has a matching `evidence` entry.

STEP 3  [needs 2]  Self-audit the finished node against issue #1053's DoD checklist line by line
        (type/shape/source/default/required/validation per row; secret/environment-specific/restart-
        required/reloadable; effects/failure/compatibility; links without embedding secrets), confirm
        every evidence entry's citation was actually opened in STEP 1, confirm the `references` edge
        to `architecture-containers-desktop` resolves against `origin/launchpad`, and confirm no second
        canonical document was created.
        done when: the audit is written inline in this session's notes (not committed) and
        `validate.py` still exits 0.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole prior
        command, then commit in a separate call.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` reports OK, and `git commit -s` succeeds without a "no verification stamp" block.

PARALLEL  None. One target file, sequential steps.

GATES     Corpus validator (`validate.py`) and the corpus unittest suite, both run locally in this
          session. `review-adjudicate` and a cross-model final pass are explicitly deferred to the
          batch owner's review of this dispatch — not run here, and the final report says so.

BUDGET    STEP 2. The hard part is keeping the settings table to desktop-app-level configuration
          (env vars the desktop process itself reads, its own compile-time build constants, and its
          own per-community backend-apply settings) without drifting into managed-agent env
          configuration (#1051), default values as a subject in their own right (#1052), the
          `BUZZ_*` env vars as a cross-cutting environment reference (#1054), or feature flags like
          `agentManagedProfiles` (#1055) — all four are sibling nodes in this same dispatch batch and
          not yet merged, so none can be a `relationships` target either.

OPEN      Whether `Community.token`'s dead parameter into `apply_workspace` is a genuine implementation
          gap (dead code) or the invite-token flow is fully handled elsewhere (a join-request event
          this pass did not trace) is reported as an honest "expected but not verified" gap in the
          node's own scope-and-omissions section, not resolved here — tracing the full onboarding/
          invite flow is a second investigation this task does not own.

LEFT OUT  No `relationships` to any of this batch's four sibling configuration documents (#1051, #1052,
          #1054, #1055) — none are merged on `origin/launchpad` yet, per `AGENTS.md`'s explicit warning
          against targeting a branch's own unmerged siblings. No attempt to fix the `Community.token`/
          `apply_workspace` discrepancy found in STEP 1 — that is implementation work, not corpus
          authoring, and is named as a candidate follow-up in the final report instead. No full
          inventory of every `BUZZ_DESKTOP_BUILD_*` compile-time constant (e.g. the agent-provider ones
          in `managed_agents/agent_env.rs`) — those are #1051's agent-configuration surface.

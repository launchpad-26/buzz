---
id: layers-configuration-feature-flags
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "The only runtime feature-flag system found in this repository lives under desktop/src/shared/features/: types.ts, manifest.ts, resolveEnabled.ts, store.ts, useFeatureEnabled.ts, FeatureGate.tsx and index.ts."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/types.ts"
      - "desktop/src/shared/features/manifest.ts"
      - "desktop/src/shared/features/resolveEnabled.ts"
      - "desktop/src/shared/features/store.ts"
      - "desktop/src/shared/features/useFeatureEnabled.ts"
      - "desktop/src/shared/features/FeatureGate.tsx"
      - "desktop/src/shared/features/index.ts"
  - statement: "A repository-wide, case-insensitive grep for feature_flag, \"feature flag\" and FeatureFlag/featureFlag across crates/, desktop/src, desktop/src-tauri and mobile/lib found matches only inside desktop/src/shared/features/*, plus the literal phrase \"feature flag\" as prose in four unrelated Rust files (git-sign-nostr/src/lib.rs, buzz-relay/src/conformance/tracers.rs, buzz-relay/src/handlers/auth.rs, buzz-relay/src/api/mod.rs) that discuss Rust's own compile-time feature mechanism or explicitly state that no flag is needed for a given check; zero matches appeared anywhere under mobile/lib."
    entry_class: FACT
    evidence:
      - "grep_search(pattern='feature_flag|feature flag|FeatureFlag|featureFlag', paths='crates/,desktop/src,desktop/src-tauri,mobile/lib', at_revision='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> matches confined to desktop/src/shared/features/* plus four Rust prose comments (git-sign-nostr/src/lib.rs, buzz-relay/src/conformance/tracers.rs, buzz-relay/src/handlers/auth.rs, buzz-relay/src/api/mod.rs); zero matches under mobile/lib"
  - statement: "types.ts defines the manifest contract (FeaturesManifest.features: FeatureDefinition[], each with id, name, description, optional defaultEnabled, optional platforms restricting a feature to \"desktop\" and/or \"mobile\") and its own doc comment states the manifest lists ONLY preview features: \"Anything not in the manifest is treated as stable and renders unconditionally (fail-open).\""
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/types.ts"
  - statement: "manifest.ts loads preview-features.json (imported through the @features-manifest module alias) through a zod schema (FeaturesManifestSchema); on schema-validation failure it logs a console.warn prefixed \"[FeatureFlags]\" and falls back to an empty manifest ({version: 1, features: []}) instead of throwing, and exposes allFeatures, desktopFeatures (features with no platforms array or one that includes \"desktop\") and getFeature(id)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/manifest.ts"
  - statement: "resolveEnabled(featureId, overrides, defaultEnabled = false) returns the caller's explicit override for that id when one exists, else the manifest's defaultEnabled value, else false; its own test suite (resolveEnabled.test.mjs) asserts exactly that precedence, including that an explicit opt-out overrides an enabled default and that an override for one id never affects another id."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/resolveEnabled.ts"
      - "desktop/src/shared/features/resolveEnabled.test.mjs"
  - statement: "store.ts persists per-user feature overrides in window.localStorage under a key derived from the manifest's own version field (`buzz-feature-overrides-v${manifest.version}`, exported as OVERRIDES_KEY), so bumping manifest.version orphans the previous key rather than needing migration logic; getOverrides() parses that key defensively (try/catch around JSON.parse, rejects non-object and array values, returns {} on any failure) and filters entries to ids present in the current manifest, silently dropping unknown/removed feature ids on read without rewriting storage -- store.test.mjs asserts this filtering happens without a write."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/store.ts"
      - "desktop/src/shared/features/store.test.mjs"
  - statement: "useFeatureEnabled.ts subscribes to override state via React's useSyncExternalStore, mirrors localStorage writes across other open windows through a \"storage\" event listener on OVERRIDES_KEY (its own comment says this mirrors the pattern used by useChannelSections/useChannelStars/useChannelMutes/useThreadFollows), and useFeatureEnabled(featureId) returns true unconditionally -- fail-open -- for any featureId absent from the manifest, logging a dev-only console.warn (\"[FeatureFlags] Unknown feature id...\") gated on import.meta.env.DEV; useFeatureToggle's toggle function calls setOverride then synchronously calls emitChange, so a toggle takes effect immediately with no app restart."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/useFeatureEnabled.ts"
  - statement: "FeatureGate is a React component that calls useFeatureEnabled(feature) and renders its children when the feature resolves enabled, else an optional fallback (default null)."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/FeatureGate.tsx"
  - statement: "The manifest data file is preview-features.json at the repository root (not under desktop/); at the recorded revision it is version 1 with five features -- workflows, projects, pulse, forum, agentManagedProfiles -- every one scoped to platforms: [\"desktop\"] and none declaring a defaultEnabled value, so every one of them currently resolves disabled by default per resolveEnabled's `?? false` fallback. It is wired into the desktop build as the @features-manifest alias in desktop/vite.config.ts and desktop/tsconfig.json, and typed by an ambient module declaration in desktop/src/features-manifest.d.ts."
    entry_class: FACT
    evidence:
      - "preview-features.json"
      - "desktop/vite.config.ts"
      - "desktop/tsconfig.json"
      - "desktop/src/features-manifest.d.ts"
  - statement: "Confirmed UI consumers: ExperimentalFeaturesCard.tsx renders one toggle row per desktop feature in Settings -> Experiments, and for the \"agentManagedProfiles\" id specifically also calls the setAgentManagedProfiles Tauri command as a side effect of the toggle; AppSidebar.tsx gates the \"forum\" feature; AppSidebarPinnedHeader.tsx gates \"pulse\", \"projects\" and \"workflows\"; UserProfilePrimaryActions.tsx calls useFeatureEnabled(\"pulse\") to decide whether to show a follow action."
    entry_class: FACT
    evidence:
      - "desktop/src/features/settings/ui/ExperimentalFeaturesCard.tsx"
      - "desktop/src/features/sidebar/ui/AppSidebar.tsx"
      - "desktop/src/features/sidebar/ui/AppSidebarPinnedHeader.tsx"
      - "desktop/src/features/profile/ui/UserProfilePrimaryActions.tsx"
  - statement: "git log --oneline -- desktop/src/shared/features preview-features.json shows the system was introduced by commit ae430d4dd, \"feat: preview features (experiments settings UI) (#888)\", and has since been touched by community-rail commits (#1902, #1995, #1858), the agent-managed-profiles feature (#2009), an inbox refactor (#2045) and a localStorage-bounding fix (#5454)."
    entry_class: FACT
    evidence:
      - "git_log(paths='desktop/src/shared/features,preview-features.json', at_revision='338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5') -> ae430d4dd 'feat: preview features (experiments settings UI) (#888)' earliest, then 55a46b063 (#1902), f06b59ff1 (#1995), 3e76481a1 (#1858), 7b3513a34 (#2009), 2bd4c24b7 (#2045), 9c074bb89 (#5454)"
  - statement: "Because preview-features.json reaches the app through a Vite resolve.alias (@features-manifest) rather than a runtime fetch, its content is bundled into the desktop app's JavaScript at build time, so changing which features exist, their names/descriptions, platform scoping or defaultEnabled value ships only in a new desktop build -- unlike a per-user override, which store.ts/useFeatureEnabled.ts apply live via localStorage with no restart."
    entry_class: INFERENCE
    evidence:
      - "desktop/vite.config.ts"
      - "desktop/src/shared/features/manifest.ts"
    confidence: 0.8
  - statement: "Neither preview-features.json nor the localStorage override object stores anything beyond feature ids, human-readable names/descriptions, platform tags and booleans; no field in FeatureDefinition, FeaturesManifest or FeatureOverrides (types.ts) is credential-, token- or hostname-shaped."
    entry_class: FACT
    evidence:
      - "desktop/src/shared/features/types.ts"
      - "preview-features.json"
      - "desktop/src/shared/features/store.ts"
  - statement: "crates/buzz-core, crates/buzz-auth, crates/buzz-relay and crates/buzz-workflow each declare a Cargo [features] section (test-utils; test-utils and dev; dev; reqwest, respectively), consumed via #[cfg(feature = \"...\")] conditional compilation -- confirmed for buzz-workflow's reqwest feature at seven sites in crates/buzz-workflow/src/executor.rs -- which is a compile-time mechanism selected when a crate is built, not a runtime, deploy-varying or user-toggleable setting."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/Cargo.toml"
      - "crates/buzz-auth/Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-workflow/Cargo.toml"
      - "crates/buzz-workflow/src/executor.rs"
  - statement: "At repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus contains no layers/ subdirectory and no other configuration-instance node; the only merged node this document's relationships could target is corpus-template-configuration (launchpad/docs/corpus/templates/configuration.md), which is present."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> no layers/ entries; templates/configuration.md present with front-matter id corpus-template-configuration"
  - statement: "Issue #1055 requires this document to be the single canonical configuration node for feature flags, scoped specifically to feature-flag configuration and distinct from four sibling configuration-node tasks dispatched in the same batch (#1051 agent-configuration, #1052 defaults, #1053 desktop-configuration, #1054 environment-configuration), none of which are merged onto origin/launchpad at this node's recorded revision."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1055 Objective and Impacted components"
  - statement: "Issue #1055 names launchpad-26/buzz#611 as the Parent PRD dispatching this batch of configuration corpus nodes, without stating scope beyond the Objective and Definition of done already quoted in this node's evidence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1055, Parent PRD field"
relationships:
  - type: implements
    target: corpus-template-configuration
---

# Buzz desktop: preview-feature (feature flag) configuration

This node catalogues Buzz's one runtime feature-flag system: the desktop
app's **preview features**, defined in `preview-features.json` at the
repository root and resolved by `desktop/src/shared/features/`. A "feature
flag" here is a named boolean gate that decides whether a piece of already-shipped
desktop UI renders. It applies to the Buzz desktop (Tauri) app only. No
equivalent runtime mechanism was found for the relay, CLI or other Rust
crates, or for the Flutter mobile app -- see *Boundary* below for what that
absence does and does not establish.

## Settings

| Setting | Type | Default | Required | Secret | Effect |
|---|---|---|---|---|---|
| `version` (root field of `preview-features.json`) | integer | none -- must be present | Yes | No | Selects the localStorage override key (`buzz-feature-overrides-v<version>`); bumping it orphans every prior per-user override rather than migrating them. |
| `workflows` (manifest feature id) | boolean (resolved) | disabled -- no `defaultEnabled` declared | No -- `defaultEnabled`/`platforms` are optional on `FeatureDefinition` | No | Gates the Workflows entry point in `AppSidebarPinnedHeader.tsx`. |
| `projects` | boolean (resolved) | disabled | No | No | Gates the Projects entry point in `AppSidebarPinnedHeader.tsx`. |
| `pulse` | boolean (resolved) | disabled | No | No | Gates the Pulse entry point in `AppSidebarPinnedHeader.tsx` and the follow action in `UserProfilePrimaryActions.tsx`. |
| `forum` | boolean (resolved) | disabled | No | No | Gates Forum Channels in `AppSidebar.tsx`. |
| `agentManagedProfiles` | boolean (resolved) | disabled | No | No | Gates its row in `ExperimentalFeaturesCard.tsx`; toggling it on also invokes the `setAgentManagedProfiles` Tauri command as a side effect. |
| `buzz-feature-overrides-v<version>` (localStorage key, `OVERRIDES_KEY` in `store.ts`) | JSON object `{ [featureId]: boolean }` | `{}` -- no overrides | No | No | Per-user, per-browser-profile override. When present for a known feature id it wins over that feature's manifest default; unknown ids are silently dropped on read. |

Row order matches `preview-features.json`'s own declaration order (`version`,
then `features` in array order), with the derived `OVERRIDES_KEY` storage
row placed last because it is a runtime artifact computed from `version`
rather than a field declared in the source file itself.

## Litmus test

The Twelve-Factor litmus test this corpus adapts is "whether the codebase
could be made open source at any moment, without compromising any
credentials." Every row above passes trivially: none of them is a
credential, key, token or hostname (see *Secrets discipline* below), so
nothing here fails the test on confidentiality grounds.

Whether this surface is "config" in Twelve-Factor's fuller sense --
*"everything that is likely to vary between deploys"* -- is a weaker fit,
and this node states that honestly rather than forcing it: `preview-features.json`
is not read from an environment variable and does not vary by deployment
target (staging vs. production, one relay community vs. another); it varies
by **desktop app build/version** (a feature's existence, name or manifest
default changes only when a new build ships it) and, independently, by
**end user** (the localStorage override layered on top). That is a
narrower kind of variance than Twelve-Factor's per-deploy framing, but it is
still a value the codebase does not hard-code into behavior -- it is read
from a separate JSON file and from browser storage, not compiled into
component logic -- which is why it is documented as configuration rather
than as internal application config. Considered and excluded on that same
basis: Cargo `[features]` compile-time toggles in `crates/buzz-core`,
`buzz-auth`, `buzz-relay` and `buzz-workflow` (see *Boundary*), which do not
vary at all after a crate is compiled and so fail Twelve-Factor's exclusion
for internal application config outright.

## Secrets discipline

No row in the table above is marked `Secret: yes`, and none quotes or needs
a placeholder value: every field in `FeatureDefinition`, `FeaturesManifest`
and the `FeatureOverrides` type is an id, a human-readable name/description,
a platform tag, or a boolean. Nothing in `preview-features.json` or the
`buzz-feature-overrides-v<version>` localStorage object is credential-shaped.

## Reload, restart and environment behavior

Two different reload stories apply to two different rows above, and
conflating them would misstate both:

- **The manifest itself** (`version`, and each feature's `name`/
  `description`/`defaultEnabled`/`platforms`) is bundled into the desktop
  app's JavaScript at build time through the `@features-manifest` Vite
  alias. Changing `preview-features.json` therefore only takes effect in a
  new desktop build -- it is not hot-reloaded or re-fetched by a running,
  packaged app (INFERENCE from how the Vite alias resolves a static JSON
  import, not from building and running a packaged app to observe it; see
  *Scope and omissions*).
- **A per-user override** (the `buzz-feature-overrides-v<version>`
  localStorage entry) applies immediately, with no restart: `useFeatureToggle`
  writes it via `setOverride` and calls `emitChange` synchronously, and
  `useFeatureEnabled`'s `useSyncExternalStore` subscription re-renders gated
  UI in the same tick. A `storage` event listener additionally propagates a
  toggle made in one open window to every other open window of the same
  profile.

Nothing in this surface is environment-specific in the sense of "differs
between a staging and a production relay" -- the manifest is the same for
every relay community a given desktop build connects to; only the build
itself and the local user's overrides vary it.

## Failure behavior and compatibility

- **Malformed or schema-invalid `preview-features.json`**: `manifest.ts`'s
  zod validation fails closed to an *empty* manifest (`{version: 1,
  features: []}`), logs one `console.warn`, and the app keeps running --
  every feature id then falls through `useFeatureEnabled`'s fail-open branch
  (see below) and renders as if stable.
- **An id used at a call site but absent from the manifest** (removed
  feature, typo, or a manifest that failed to load): `useFeatureEnabled`
  returns `true` unconditionally -- fail-open, so a stale `<FeatureGate
  feature="removed-id">` never hides UI -- and logs a dev-only warning
  (`import.meta.env.DEV` gated) rather than throwing.
  Compatibility-wise, this means **removing** a feature id from the
  manifest is a safe, non-breaking edit for any component still gating on
  that id (it starts rendering unconditionally rather than erroring), while
  **adding** a new id starts it hidden by default (no `defaultEnabled`)
  until a caller opts it in.
- **Malformed localStorage content** (corrupted JSON, non-object, array):
  `getOverrides()` catches the failure and returns `{}`, so a corrupted
  override store degrades to "every feature at its manifest default," not a
  crash.
- **A `version` bump in `preview-features.json`**: changes `OVERRIDES_KEY`,
  so every previously stored per-user override is orphaned (not read, not
  migrated) rather than reinterpreted against the new manifest -- documented
  in `store.ts`'s own header comment as the deliberate mechanism for a
  "clean reset" instead of migration logic.

## Boundary

This node does not describe:

- **The four sibling configuration nodes dispatched in the same batch**
  (agent-configuration, defaults, desktop-configuration,
  environment-configuration -- issues #1051-#1054). None of their ids exist
  on `origin/launchpad` at this node's recorded revision, so no
  relationship to them is declared; see *Relationships*.
- **Cargo `[features]` compile-time toggles** (`test-utils`, `dev`,
  `reqwest` across `buzz-core`, `buzz-auth`, `buzz-relay`,
  `buzz-workflow`). These select code at compile time, not at runtime or
  per-deploy, and are excluded from the litmus test above on that basis.
  They share the words "feature flag" with this node's subject in casual
  usage but are a different mechanism entirely, and are not catalogued
  here.
- **A full implementation-reference node** for `desktop/src/shared/
  features/*`'s internals -- `useSyncExternalStore`'s snapshot-caching
  strategy, the exact `storage`-event cross-window sync implementation, or
  `usePreviewFeatureWarning`'s toast-notification behavior beyond what is
  needed above to state each setting's default, reload and failure
  behavior. A node describing that implementation in full, if one is
  written, may `references` this one rather than this one absorbing it.
- **Mobile.** No equivalent preview-feature mechanism was found under
  `mobile/lib` (see the grep evidence above); this node does not assert one
  exists, and does not speculate about mobile feature-flagging plans.
- **Any settings surface documented by this batch's other configuration
  nodes** once they merge (relay `buzz-relay/src/config.rs` environment
  variables, desktop-wide settings, or repository-level defaults) -- this
  node's subject is specifically the preview-feature gate system, not
  configuration in general.

## Relationships

- `implements` -> `corpus-template-configuration`: this node is an instance
  of the configuration template, whose id is confirmed present on
  `origin/launchpad` at the recorded revision, matching that template's own
  guidance that an instance "should declare `implements`... once this node
  is merged."

No other relationship is declared. A `references` edge toward an
`implementation`-typed node describing `desktop/src/shared/features/*`'s
internals in full, and `references`/`part-of` edges toward the four sibling
configuration nodes (#1051-#1054) and toward the generic reference template
(`corpus-template-reference`, if merged), are candidates for a follow-up
edit once those nodes exist on `origin/launchpad` -- adding them now would
target ids no loaded node currently carries, which `validate.py` treats as a
hard error.

## Scope and omissions

**This node covers** the desktop preview-feature system as a configuration
surface: the `preview-features.json` manifest's fields, the resolution
precedence (explicit override, then manifest default, then disabled), the
localStorage override mechanism and its versioned key, which UI each
current feature id gates, fail-open behavior for unknown ids and for a
manifest that fails to load, build-time-versus-runtime reload behavior, and
why Cargo `[features]` compile-time toggles are a different, excluded
mechanism.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The four sibling configuration nodes for this batch (agent, defaults, desktop, environment) | #1051, #1052, #1053, #1054 |
| `buzz-relay`'s environment-variable configuration (`crates/buzz-relay/src/config.rs`) | Not this node's subject; a candidate for one of #1051-#1054 or a future node |
| A full implementation-reference for `desktop/src/shared/features/*`'s hook/caching internals | corpus's `implementation` surface; no specific issue found for it |
| The generic reference and configuration templates themselves | `launchpad/docs/corpus/templates/reference.md`, `launchpad/docs/corpus/templates/configuration.md` |
| Whether a parallel feature-flag mechanism should exist for mobile | Product decision, not documented here because none exists today |

**Expected but not verified when this node was written:**

- **The build-time-bundling claim in *Reload, restart and environment
  behavior* was not confirmed by building and running a packaged desktop
  app.** It is classified `INFERENCE` (confidence 0.8) from reading
  `desktop/vite.config.ts`'s alias configuration and how `manifest.ts`
  imports it, not from observing a shipped build fail to pick up an edited
  `preview-features.json`.
- **The mobile-absence claim rests on a literal-string grep** (`feature_flag`,
  `"feature flag"`, `FeatureFlag`/`featureFlag`) across `mobile/lib`, not on
  reading every file in that tree. A differently named mechanism using
  different vocabulary would not have been caught by this search.
- **No end-to-end test was run against `ExperimentalFeaturesCard.tsx`'s
  `setAgentManagedProfiles` side effect** (the Tauri command it invokes when
  the `agentManagedProfiles` toggle changes); its existence and call site
  were confirmed by reading the component, not by exercising the toggle in
  a running app.
- **Whether `#1346`'s generic reference template, or `#1051`-`#1054`'s
  eventual merged content, draw this node's boundary the same way it draws
  itself was not checked**, since none of those are merged at the time this
  node was written.

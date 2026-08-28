Issue #551 — task: scaffold the knowledge crate with nested AGENTS.md and Settings entry
Stated size: none given (confirmed with Serina 2026-08-27)  →  cap: 8 steps

ALREADY TRUE  (verified against git and GitHub, not notes)
  `launchpad/crates/` does not exist yet — this is the first crate there.
  Root `Cargo.toml` `members` list has no `knowledge` entry (30 existing members, all under `crates/`).
  `desktop/src/features/settings/ui/SettingsPanels.tsx` has exactly the 4 hardcoded
    registration sites ADR-0051 names: `SettingsSection` union (:82-98),
    `SETTINGS_SECTION_VALUES` (:102-119), `settingsSections` descriptor array (:~150),
    `renderSettingsSection` switch with `exhaustiveCheck: never` default (:819-883).
    No registration seam exists yet.
  No cohort-owned frontend code exists anywhere under `desktop/src/` yet — this is the
    first fork-owned TS/React surface, mirroring `launchpad/crates/` being the first
    fork-owned Rust surface.
  ADR-0045 (crate location, PR #1497) and ADR-0051 (Settings seam, PR #1503) are both
    `Accepted` in their branch content, decided by @serina-mcfall on 2026-08-27 in #1409
    and #1502 — not yet merged, but the decisions themselves are made, not pending.
  No branch or worktree exists yet for #551.
  Precedent for a scoped nested AGENTS.md: `desktop/src/features/agents/AGENTS.md`
    (a `Scope:` line + one governing rule, not a full contributor guide).
  Precedent for a minimal crate: `crates/buzz-persona` (small `Cargo.toml`, flat `src/`).

STEP 1  [independent] Create the branch: `git checkout launchpad && git pull && git
        checkout -b task/551-knowledge-crate-scaffold`.
        done when: branch exists, tracks no unrelated commits (current HEAD == `origin/launchpad` HEAD).

STEP 2  [independent] Scaffold `launchpad/crates/knowledge/`: minimal `Cargo.toml`
        (package name `knowledge`, no runtime deps beyond what a stub needs), `src/lib.rs`
        with a single public no-op item (e.g. a doc comment and an empty placeholder
        function or const — no seeded content, no `knowledge.*` interface — that is
        F22/#552's scope, explicitly out of scope here). Add `"crates/knowledge"` to root
        `Cargo.toml` `members`.
        done when: `cargo build -p knowledge` succeeds from repo root.

STEP 3  [needs 2] Add `launchpad/crates/knowledge/AGENTS.md` following the
        `desktop/src/features/agents/AGENTS.md` shape: a `Scope:` line naming the crate
        path, and the one rule that will govern it once #552/#553 land (e.g. "this crate
        reads a static, committed corpus artefact — it must not run the Python corpus
        pipeline, re-parse source, or re-derive embeddings" — Ruling 11's language, cited
        so a future contributor knows the constraint exists even before #578 is decided).
        done when: file exists at that path with a `Scope:` line matching the crate dir.

STEP 4  [needs 1] ← RUNS HERE Add the registration seam to `SettingsPanels.tsx`: widen
        `SettingsSection` to `UpstreamSettingsSection | CohortSettingsSectionId`, where
        `UpstreamSettingsSection` is the existing 16-literal union (renamed, not removed)
        and `CohortSettingsSectionId` is imported from one new cohort-owned registry
        module. Add a `cohortSettingsSections: SettingsSectionDescriptor[]` array read from
        that registry and merged into `settingsSections`. In `renderSettingsSection`, check
        the registry first (by id) and return its renderer; fall through to the existing
        `switch` only for `UpstreamSettingsSection`, keeping the `exhaustiveCheck: never`
        default intact for upstream's own 16 cases.
        done when: `pnpm --dir desktop exec tsc --noEmit` passes with zero new errors, and
        the existing 16 upstream sections still render (spot-check `profile` unaffected).

STEP 5  [needs 4] Create the cohort-owned registry module at
        `desktop/src/launchpad/settings/registry.ts`: exports `CohortSettingsSectionId`
        (starts as `never`, widened by each cohort panel module augmenting it) and a
        `registerCohortSettingsSection(descriptor)` function backing the array read in step
        4. This is the reusable seam; the knowledge panel is its first and only registrant
        right now.
        done when: the file exists, compiles, and `SettingsPanels.tsx` imports from it
        rather than defining cohort types inline.

STEP 6  [needs 5] Create `desktop/src/launchpad/settings/KnowledgeSettingsPanel.tsx`: a
        placeholder component (e.g. "Help — coming soon" or similar, matching existing
        Settings card visual style via `SettingsOptionGroup`) and register it against the
        registry from step 5 with a nav label and icon (e.g. `BookOpen` from
        `lucide-react`, already a dependency). No corpus content, no `knowledge.*` calls —
        out of scope per #551's own text.
        done when: the section appears in the Settings sidebar nav and clicking it renders
        the placeholder panel, verified via `just desktop-screenshot --name
        knowledge-settings-placeholder --click open-settings`.

STEP 7  [needs 6] Keyboard/focus check on the new nav entry and panel: confirm the
        sidebar item is reachable by Tab/Arrow (matching the existing nav's own pattern —
        no new widget type introduced, so no new ARIA role is needed) and that opening the
        panel does not trap or lose focus. This is a nav item + static panel, not a custom
        interactive widget, so no dialog/combobox APG pattern applies here.
        done when: keyboard-only navigation reaches and opens the panel; focus lands inside
        the panel content on selection, same as an existing section (e.g. `updates`).

STEP 8  [needs 3, 6, 7] Run `just ci` (or at minimum `cargo build -p knowledge`, `pnpm
        --dir desktop exec tsc --noEmit`, `pnpm --dir desktop lint`) and fix anything the
        new files trip.
        done when: `just ci` passes, or the narrower command set above passes with no
        new warnings attributable to the new files.

PARALLEL  Steps 1 and 2 are independent of each other (branch creation vs. crate scaffold
          content) but 2 needs 1 to exist as a commit target. Step 3 only needs 2 (same
          crate directory, no shared file with step 4/5/6). Steps 4→5→6 are strictly
          sequential — each edits or imports the previous step's output. Step 7 needs a
          rendered panel (6). Given the small size (8 steps, ~30-60 min), running these as
          separate subagents is unlikely to save wall-clock time over doing them in one
          session; the one genuinely separable unit is STEP 3 (crate AGENTS.md) alongside
          STEP 4 (frontend seam), since they touch disjoint files (Rust crate doc vs. TSX).

GATES     `review-code` after step 8 (the seam's type-widening is the part most likely to
          hide a subtle bug — e.g. a cohort id colliding with an upstream literal).
          `review-a11y` after step 7 (new Settings nav entry + panel, per this repo's
          accessibility-first rule — even though it's a simple static panel, confirm focus
          management explicitly rather than assuming it inherits correctly).
          `qa` explore mode applies: after step 6, click through Settings — open the panel,
          switch away and back, resize the window — since there is a runtime UI surface to
          exercise, however small.
          `review-final` once #551 merges and before starting #552, since #552 depends on
          this scaffold existing.

BUDGET    Step 4 (the registration seam) is most likely to eat the budget. ADR-0051 itself
          flags the union-widening-without-losing-exhaustiveness problem as unsolved design
          work landing on #551, not a known-good pattern being copied. If the "registry
          checked before the switch, exhaustiveness kept only for upstream literals"
          approach doesn't type-check cleanly, expect to spend time on alternatives (a
          discriminated wrapper type, or a type predicate narrowing `SettingsSection` to
          `UpstreamSettingsSection` before the switch).

OPEN      Issue #578 (open, undecided) says PRD #4 currently asserts a contradiction between
          Ruling 11 (crate re-derives nothing), Ruling 12 (desktop build never runs the
          corpus pipeline), and `knowledge.find`'s free-text query needing live resolution —
          and explicitly warns "If either is rejected, #551's scaffolding assumptions
          change." This plan treats #551 as a genuinely empty scaffold (no query surface,
          no seeded content) specifically so it does not need #578 resolved first — but if
          #578 lands on an answer that changes what "the knowledge crate" fundamentally is
          (e.g. it becomes a thin FFI shim rather than a data-holding crate), step 2's
          `Cargo.toml`/`lib.rs` shape may need revisiting. Flagged, not resolved, per this
          skill's ambiguity rule.
          Exact naming/location of the cohort-owned frontend registry module
          (`desktop/src/launchpad/settings/`) is this plan's proposal, not dictated by any
          ADR — ADR-0051 says cohort code "lives under `launchpad/`" but there is no existing
          precedent for fork-owned frontend code's location, since this is the first one.
          Confirm the path during step 5 rather than treating it as fixed.
          Whether the placeholder panel needs any copy beyond "coming soon" — not specified
          by #551's DoD, left to whoever builds step 6.

LEFT OUT  Seeding any real help content — explicitly out of scope per #551's own issue text
          (separate task, #552). The `knowledge.*` programmatic interface — explicitly out
          of scope (F22, #553/#211). Registering a second cohort Settings panel (e.g. #524's
          telemetry-profiles crate) — the seam supports it, but only the knowledge panel is
          registered now; a second registrant is proof-of-concept work for whoever builds
          #524, not this issue.

Issue #1055 — Create feature-flags.md as the single canonical configuration node for feature flags
Stated size: not stated on the issue → cap: 5 steps (dispatch instruction for this corpus-authoring batch caps every task at 5 steps)

ALREADY TRUE  (verified against git, not notes)
  launchpad/docs/corpus/layers/ does not exist anywhere on origin/launchpad (git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus has no layers/ entry).
  launchpad/docs/corpus/layers/configuration/feature-flags.md does not exist in this worktree (checked out from origin/launchpad).
  desktop/src/shared/features/ is a real, working, runtime feature-flag system: types.ts, manifest.ts, resolveEnabled.ts, store.ts, useFeatureEnabled.ts, FeatureGate.tsx, index.ts, plus resolveEnabled.test.mjs and store.test.mjs.
  The manifest data file is preview-features.json at the repo root, aliased as "@features-manifest" in desktop/vite.config.ts and desktop/tsconfig.json, declared in desktop/src/features-manifest.d.ts.
  preview-features.json currently lists 5 features (workflows, projects, pulse, forum, agentManagedProfiles), all platforms: ["desktop"], none carrying defaultEnabled (so all default to disabled per resolveEnabled's `?? false`).
  grep across crates/, desktop/src, mobile/lib for feature_flag / FeatureFlag / "feature flag" found no server-side (Rust) or mobile (Dart) runtime feature-flag system — only this desktop TS system, plus unrelated Cargo [features] compile-time toggles (buzz-core: test-utils; buzz-auth: test-utils, dev; buzz-relay: dev; buzz-workflow: reqwest) that are a different, compile-time mechanism.
  Introducing commit for the desktop system is PR #888 "feat: preview features (experiments settings UI)" (git log --oneline -- desktop/src/shared/features preview-features.json).
  Consumers confirmed via grep: ExperimentalFeaturesCard.tsx (Settings UI), AppSidebar.tsx (forum gate), AppSidebarPinnedHeader.tsx (pulse/projects/workflows gates), UserProfilePrimaryActions.tsx (pulse-gated action).
  node.schema.json requires id/type/status/origin/audiences/evidence, type enum includes "layers", status enum includes "draft"; relationships is optional and every target must resolve against origin/launchpad's currently-loaded nodes.
  The four sibling configuration-node issues in this batch (#1051 agent-configuration, #1052 defaults, #1053 desktop-configuration, #1054 environment-configuration) are not on origin/launchpad yet (confirmed by the same git ls-tree), so this node must declare no relationships to them.
  launchpad/docs/corpus/templates/configuration.md is a merged, active template (id: corpus-template-configuration) with a mandatory skeleton: description paragraph, Settings table, Litmus test, Secrets discipline, Boundary, Relationships, Scope and omissions.

STEP 1  Confirm evidence is complete and re-verify nothing has moved                          [independent]
        done when: every file cited in ALREADY TRUE above has been opened in this worktree at HEAD
        (338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5), and no additional runtime feature-flag
        mechanism turns up in a final grep pass across crates/, desktop/, mobile/ for
        feature_flag|FeatureFlag|"feature flag"|featureFlag.

STEP 2  Draft launchpad/docs/corpus/layers/configuration/feature-flags.md               [needs 1]
        using launchpad/docs/corpus/templates/configuration.md's required sections        ← RUNS HERE
        (description, Settings table ordered to match preview-features.json's declaration
        order, Litmus test, Secrets discipline, Boundary naming Cargo [features] as
        explicitly out of scope, Relationships: none declared with the reason stated,
        Scope and omissions with an Expected-but-not-verified list).
        Front matter: id: layers-configuration-feature-flags, type: layers, status: draft,
        origin: launchpad, audiences per template precedent, evidence ledger classifying
        each claim FACT/INFERENCE/TEAM_KNOWLEDGE, relationships: implements ->
        corpus-template-configuration only (that id is confirmed present on
        origin/launchpad; the template's own guidance says an instance "should declare
        implements... once this node is merged," and it already is).
        done when: the file exists at that path, front matter parses as YAML, and every
        settings-table row cites the manifest.ts/types.ts/resolveEnabled.ts/store.ts code
        that backs its default/required/secret/effect claims rather than a recollection.

STEP 3  Run python3 launchpad/project-intelligence/corpus/validate.py and fix until it       [needs 2]
        exits 0.
        done when: the command's exit status is 0 and its output names zero errors for
        layers-configuration-feature-flags.

STEP 4  Run python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests    [needs 3]
        -p "test_*.py" as the sole command in its own tool call, confirm OK, then commit
        with `git commit -s`.
        done when: the unittest run prints OK and `git log -1` shows a new signed commit
        on task/1055-feature-flags containing exactly the new corpus file (plus the plan
        file from this step's own prerequisite work, if not already committed).

STEP 5  Self-review the diff against issue #1055's Definition-of-done checklist line by     [needs 4]
        line, confirm no second hand-authored corpus document was created, confirm
        validate.py still exits 0, and write the final report.
        done when: every DoD bullet has a stated yes/no with evidence, and the report names
        HEAD SHA, document path/id/template, status, a summary, "Not verified" content, and
        any candidate follow-up issues found but not filed.

PARALLEL  None of the five steps are independent of each other in practice — steps 2-5 form
          one linear chain (draft → validate → test/commit → review) and step 1 is evidence
          gathering that step 2 consumes directly. This is a single-document authoring task
          with one file in play; there is no second independent unit of work to fan out to
          a parallel subagent.
GATES     corpus-review's structural/evidence-honesty/duplication/public-boundary checks
          apply, informally, via Step 3 (validate.py) and Step 5 (self-review against the
          DoD checklist) — no separate review-* skill invocation is planned beyond that,
          per the task's own Step 5/6 instructions. qa explore mode does not apply: this is
          a documentation-only change with no runtime interface to exercise.
BUDGET    Step 2 (drafting the node body) is the step most likely to eat the budget — five
          required template sections, a settings table needing per-row code citations, and
          an honest Scope-and-omissions/Expected-but-not-verified section all have to be
          written and cross-checked against the actual source files in the same step.
OPEN      Whether Cargo [features] compile-time toggles deserve their own future corpus
          node (a different mechanism, out of scope here) is left for a human to decide,
          not resolved by this plan.
LEFT OUT  Linking to the four sibling configuration nodes (#1051-#1054) is deliberately
          excluded: none of their ids exist on origin/launchpad yet, and a relationships[]
          target naming an id no loaded node carries is a hard validate.py error. The
          only relationship declared is implements -> corpus-template-configuration,
          whose id is confirmed present on origin/launchpad already.

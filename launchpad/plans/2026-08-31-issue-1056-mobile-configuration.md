Issue #1056 — task: document layers/configuration/mobile-configuration.md
Stated size: no `Size` line -> single-document corpus task, cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1056-mobile-configuration`, based on `origin/launchpad` at
    `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`, worktree created clean.
  `launchpad/docs/corpus/layers/configuration/mobile-configuration.md` does NOT exist.
  `launchpad/docs/corpus/templates/configuration.md` (id `corpus-template-configuration`)
    is merged and is the template this node's Objective calls for ("the single
    canonical configuration node for mobile configuration").
  `launchpad/docs/corpus/architecture/containers/mobile.md` (id
    `architecture-containers-mobile`) is merged and already documents
    `RelayConfig`/`Env.relayUrl` at container-overview depth -- a legitimate
    `references` target for this specialization, and one this node must not
    duplicate.
  Sibling configuration-node issues (#1051-#1055, #1057-#1059) are open, unmerged
    draft PRs -- their ids are not on `origin/launchpad`, so no relationship may
    target them regardless of subject-matter overlap.
  Repo evidence for "mobile configuration" resolves to: a compile-time
    `--dart-define` surface (`mobile/lib/shared/relay/relay_provider.dart`'s `Env`
    class: `BUZZ_RELAY_URL`, dev-only fallback), a debug-only feature flag
    (`BUZZ_MOCK_DM_DIRECTORY` in `channel_management_provider.dart`, owned by
    #1055 not here), Android release-signing environment variables consumed by
    `mobile/android/app/build.gradle.kts` (`BUZZ_ANDROID_UPLOAD_KEYSTORE_PATH`,
    `_PASSWORD`, `_KEY_ALIAS`, `_KEY_PASSWORD`, `BUZZ_ANDROID_RELEASE_SIGNING`),
    and worktree-scoped debug-identity overrides written by
    `scripts/mobile-worktree-overrides.sh` into two gitignored files
    (`mobile/ios/Flutter/WorktreeOverrides.xcconfig`,
    `mobile/android/worktree.properties`) plus a developer-owned
    `AppOverrides.xcconfig` override point. Runtime per-community relay
    selection (`Community`/`CommunityStorage`, secure-storage-backed) is user
    data seeded via pairing/invite, not deploy-time configuration, and is
    already covered by `architecture-containers-mobile` -- named here as
    considered-and-excluded, not silently omitted.

STEP 1  [independent]  Gather evidence (already done in this session; recorded
        complete at plan-write time): read `mobile/lib/shared/relay/
        relay_provider.dart`, `mobile/.env.json.example`, `mobile/lib/features/
        channels/channel_management_provider.dart` (`BUZZ_MOCK_DM_DIRECTORY`),
        `mobile/README.md` (worktree identity + Android release signing
        sections), `scripts/mobile-worktree-overrides.sh`,
        `mobile/android/app/build.gradle.kts`, `mobile/ios/Flutter/
        Debug.xcconfig`, `mobile/ios/Runner/Info.plist`, `Justfile`'s Mobile
        section, `.github/workflows/mobile-release-candidate.yml`,
        `RELEASING.md`'s Mobile rows, and `launchpad/docs/corpus/
        architecture/containers/mobile.md` in full.
        done when: every claim in the drafted document cites one of the paths
        above (or another path actually opened) and no claim rests on
        inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/layers/
        configuration/mobile-configuration.md` from `templates/configuration.md`:
        schema-valid front matter (`id: layers-configuration-mobile-configuration`,
        `type: layers`, `status: draft`, `origin: launchpad`, `audiences:
        [agent, developer, operator, reviewer]`, `relationships: [references:
        architecture-containers-mobile, implements: corpus-template-
        configuration]`) plus the template's seven required body sections
        (configuration description, structured settings table in source
        declaration order, litmus-test statement, secrets discipline, boundary
        statement, relationships, scope and omissions) scoped explicitly to
        mobile-app-level configuration and excluding runtime per-community
        relay selection, the `BUZZ_MOCK_DM_DIRECTORY` feature flag (owned by
        #1055), and the parsing/validation implementation itself.
        done when: the file exists, front matter parses, and every template
        required-section bullet has a corresponding heading.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/
        corpus/validate.py` must exit 0 against the full tree including the
        new file. Fix and re-run on any failure.
        done when: the command exits 0.

STEP 4  [needs 3]  Earn the commit verification stamp by running `python3 -m
        unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole prior command, then commit the plan + document
        with `git commit -s`. Do not push and do not open a PR (batch
        integration cherry-picks this commit separately).
        done when: the unittest run reports OK, the commit carries a
        `Signed-off-by:` trailer, and `git log` shows it on
        `task/1056-mobile-configuration`.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must
          exit 0, this session). `review-adjudicate` and a cross-model final
          review pass are deferred to the batch owner's integration review --
          not run in this session, per Feature #611's batch instructions.

BUDGET    STEP 2. The hard part is drawing an honest boundary between
          deploy-time configuration (the `Env`/dart-define surface, Android
          signing env vars, worktree-identity overrides) and the adjacent
          runtime state (`Community` secure-storage records) and feature flag
          (`BUZZ_MOCK_DM_DIRECTORY`) that share the same files but belong to
          other nodes, without silently folding either in.

OPEN      Whether worktree-identity overrides (`WorktreeOverrides.xcconfig`,
          `worktree.properties`) genuinely pass the Twelve-Factor litmus test
          used by `templates/configuration.md` -- they vary per developer
          worktree, not per deploy target, and are gitignored/generated rather
          than deploy-supplied. Planned handling: include them in the settings
          table with an explicit note that they are dev-tooling values keyed to
          worktree identity rather than classic deploy-variance, so a reader is
          not misled into thinking the boundary was applied uncritically.

LEFT OUT  Editing `launchpad/docs/corpus/architecture/containers/mobile.md` or
          any other existing corpus node. Documenting the `BUZZ_MOCK_DM_DIRECTORY`
          feature flag in depth (owned by #1055, this batch, unmerged). Any
          `relationships` edge to sibling configuration nodes (#1051-#1059) --
          none exist on `origin/launchpad` yet. Documenting the Android
          upload-keystore *contents* or the `buzz-releases` private pipeline's
          own build steps -- out of this repository's OSS source tree and this
          node's ownership boundary. Filing a follow-up issue for the deep-link
          `buzz://` scheme registration (`CFBundleURLSchemes`,
          `AndroidManifest.xml` intent filter) as a possible interface-layer
          node -- noted as a candidate in the final report, not filed here.

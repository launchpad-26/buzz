Issue #949 — task: document implementation/mobile/feature-map.md
Stated size: no `Size` line, single hand-authored document, batch task under parent Feature #615 (PRD #602)  →  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  On branch `task/949-mobile-feature-map`, based on `origin/launchpad` HEAD 76a0a4ebbe4bc4d852b0d04362ed768620da34b3,
    working tree clean. `node.schema.json`, `relationships.schema.json` and `launchpad/docs/corpus/AGENTS.md` are
    merged and authoritative. `launchpad/docs/corpus/templates/implementation-reference.md` is merged and is the
    required template. `launchpad/docs/corpus/architecture/containers/mobile.md` (id `architecture-containers-mobile`,
    status `draft`) is merged and is a legitimate `part-of` target. `launchpad/docs/corpus/implementation/mobile/`
    does not exist yet; `feature-map.md` does not exist yet.

STEP 1  [independent]  ← RUNS HERE  Gather evidence: enumerate `mobile/lib/features/*` (10 directories: activity,
        channels, forum, home, invites, pairing, profile, pulse, search, settings), skim each feature's top-level
        page/provider files and per-feature file counts, and identify each feature's entry point and how `app.dart`
        / `home_page.dart` wire it in. Verify the CLAUDE.md-stated "feature modules must not import from other
        feature modules, only from shared/" rule directly (not by restating the doc) with a full grep-based scan of
        every `import` line under `mobile/lib/features/**/*.dart`, resolving both `package:buzz/features/...` and
        relative `../<feature>/...` forms against the importing file's own feature. Confirm whether any automated
        gate (`analysis_options.yaml`, `custom_lint`/`riverpod_lint` config) enforces the rule.
        done when: a feature→directory table with file counts and entry points is drafted, and the cross-feature
        import scan's raw counts (violating lines, distinct files, importing→imported feature pairs) are recorded.

STEP 2  [needs 1]  Write `launchpad/docs/corpus/implementation/mobile/feature-map.md` with schema-valid front
        matter (`id: implementation-mobile-feature-map`, `type: implementation`, `status: draft`, `origin:
        launchpad`, `audiences: [agent, developer, reviewer]`, an `evidence` ledger with a commit-provenance FACT
        plus one entry per substantive claim, `relationships: [{type: part-of, target:
        architecture-containers-mobile}]`) and the implementation-reference template's required sections, scoped as
        a breadth map rather than a deep-dive: Realization statement (this node maps `mobile/lib/features/*` against
        the feature-isolation contract stated in `CLAUDE.md`), Target (`CLAUDE.md:599-600`, not itself a corpus
        node), Implementation surface (the feature→directory table from STEP 1, one row per feature: directory,
        file count, entry point, what it does, its own outbound feature-boundary imports if any), Divergences (the
        cross-feature import violations found in STEP 1, reported as counts and representative examples — not
        silently omitted), Verification ("none" — confirmed no `analysis_options.yaml`/`custom_lint` rule enforces
        it, only `mobile/test/features/<feature>/` test coverage per feature), Relationships, and Scope and
        omissions stating explicitly that #950 (Flutter app internals, this same batch) owns the depth this node
        does not attempt.
        done when: the file exists with every required template section populated and every DoD bullet from
        issue #949 addressed by a distinct part of the document.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.
        done when: the command exits 0 with zero FAIL entries for this node (a pre-existing ~21-failure baseline
        unrelated to this node may still be present on `origin/launchpad`; confirmed via `git stash` diff rather
        than assumed).

STEP 4  [needs 3]  Self-verify the diff line-by-line against issue #949's Definition of Done checklist and against
        the template's required-sections list; confirm every evidence entry's citation was actually opened and
        supports its claim, and that no second canonical document was created.
        done when: the audit is complete and `validate.py` still exits 0 on the current tree.

STEP 5  [needs 4]  Earn the verification stamp with the corpus unittest suite as the sole command in its own tool
        call, then commit the plan and the new document together in a separate call. Do not push, do not open a PR.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports `OK` and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file, steps are strictly sequential (evidence gathers before the body cites it; the
          body must exist before it can be validated or audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report
          `OK` before commit. `review-adjudicate` and the cross-model final review pass are deferred to the batch
          owner's integration phase — not run in this worktree; a self-review (and `corpus-review` if reachable)
          substitutes here.

BUDGET    STEP 1 and STEP 2 together. The evidence-gathering scan (grepping every import line across ~250 mobile
          `.dart` files under `lib/features/`) is mechanical but must be done fully, not sampled, because the
          Divergences section's honesty depends on a complete count rather than a spot-check.

OPEN      Whether the cross-feature import violations found in STEP 1 (real, current, non-trivial — dozens of
          lines across most of the ten features) should also be filed as a separate implementation issue against
          `mobile/` is a judgment call this task does not resolve; this node reports the divergence honestly in its
          own Divergences section per the template's evidence-expectations rule, and leaves filing a fix (or a
          follow-up issue) to a human or a separate task, consistent with this batch's scope being documentation
          only. Whether `pulse/` (a feature directory with its own tests but, per STEP 1's grep, no reference from
          `home_page.dart`, `app.dart`, or any other wiring point found) is dead/unwired code or reachable through a
          path this scan missed is reported as an observation, not resolved as a defect claim, since resolving it
          would require broader investigation than a feature map warrants.

LEFT OUT  Per-file internals of any single feature (routing logic, provider implementation detail, widget trees) —
          that depth is issue #950's (Flutter app internals, same batch). Any `implements` relationship to a
          spec/decision/contract corpus node — none exists yet for mobile feature architecture; `CLAUDE.md` is
          named as the target in prose per the template's own instruction not to invent an edge to a nonexistent
          node id. Fixing the cross-feature import violations found, or updating `CLAUDE.md`/the mobile README to
          reflect that the rule is convention-only and currently violated — that is implementation/documentation
          work, not this corpus-authoring task. A second canonical document (e.g. a separate node about `pulse/`'s
          apparent unwired state) — if that finding warrants its own investigation, it is a separate task.

Issue #1059 — task: document layers/configuration/validation.md
Stated size: no `Size` line  ->  cap: 5 steps (single hand-authored document, batch task under parent PRD #611).

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1059-configuration-validation`, based on `origin/launchpad` HEAD
    338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, working tree clean. `node.schema.json`,
    `launchpad/docs/corpus/AGENTS.md` and `launchpad/docs/corpus/templates/configuration.md`
    are merged and authoritative. `launchpad/docs/corpus/layers/configuration/` does not
    exist yet (no `layers/configuration/*` node has merged) — this will be the directory's
    first file. Sibling tasks #1051-#1058 (agent/defaults/desktop/environment/feature-flags/
    mobile/relay-configuration/secrets) are open, unmerged batch siblings — not linkable.

STEP 1  [independent]  Gather evidence for the configuration *validation mechanism* across
        Buzz surfaces, deliberately scoped to the cross-cutting contract rather than any one
        surface's settings list (that is #1051-#1058's job). Read `crates/buzz-relay/src/
        config.rs` in full (`Config::from_env`, `ConfigError`, `parse_bind_addr`,
        `parse_operator_api_origin`, `parse_push_gateway_delivery_url`, the
        `RELAY_OPERATOR_PUBKEYS`/`RELAY_OPERATOR_API_ORIGIN` cross-field check, the
        `BUZZ_REPLICA_HEAD_MAX_AGE_SECS` renamed-var hard-fail); `crates/buzz-relay/src/
        main.rs` lines ~140-155 (`Config::from_env().map_err` propagated via `?` through
        `anyhow::Result` main) and ~425-454 (the `BUZZ_RELAY_PRIVATE_KEY`/
        `BUZZ_REQUIRE_AUTH_TOKEN` cross-field check enforced by `panic!`, not `ConfigError`,
        and the `media.validate()` call site); `crates/buzz-media/src/config.rs`
        (`MediaConfig::validate`, its structural + cross-field rules); and
        `crates/buzz-backend-kubernetes/src/config.rs` in full (`parse`, `optional_string`,
        `optional_u64`, `valid_namespace`, the `inactivity_seconds: 0` refusal, the I2
        credential-field-has-no-effect test, `config_schema()`'s JSON-Schema-driven UI
        validation, and the round-trip tests tying the schema default to `parse`). Confirm
        no config-reload/SIGHUP mechanism exists in the relay (`rg -i "reload|SIGHUP"` over
        `config.rs`/`main.rs` returns nothing) to support a restart-required claim.
        done when: every claim planned for the body has a specific opened source (path +
        symbol, and for tests, the test name) recorded, and the two distinct crates'
        validation mechanisms (env-var startup config vs. JSON `provider_config`) are each
        traced from parse through the caller that surfaces the failure.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/layers/configuration/
        validation.md` using `templates/configuration.md`'s required sections (adapted: this
        node catalogues the *validation contract itself*, not one surface's settings, so its
        "Structured entries" table rows are the distinct validation mechanisms/failure modes
        found in STEP 1, not individual variables). Front matter: `id:
        layers-configuration-validation`, `type: layers`, `status: draft`, `origin:
        launchpad`, `audiences: [agent, developer, operator, reviewer]`, an `evidence` ledger
        with a commit-provenance FACT (`338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`) plus one
        entry per substantive claim, classified honestly (FACT for opened code/tests,
        INFERENCE with `confidence` for reasoned generalizations like "no reload mechanism
        exists", TEAM_KNOWLEDGE with `provided_by` for anything attributed to the issue
        text). `relationships: [{type: implements, target: corpus-template-configuration}]`
        only — no sibling `layers/configuration/*` node exists on `origin/launchpad` to link.
        Body sections per the template: configuration description (scope: the validation
        mechanism/contract, cross-cutting, explicitly not any one surface's defaults),
        structured entries (the mechanisms: type/shape checking, required-vs-defaulted,
        cross-field/semantic validation, secret-shaped values never validated by content),
        litmus test (why these are deploy-varying config surfaces per Twelve-Factor, per the
        template's own convention), secrets discipline (name env vars/fields, never values),
        boundary (not the settings catalogs owned by #1051-#1058, not the JSON front-matter
        schema `node.schema.json`), relationships, scope and omissions (including desktop/
        mobile config validation as an honest gap if STEP 1 did not reach them, and the
        `#1059` DoD's four type-specific bullets: type/shape+source+default/required+
        validation; secret/environment-specific/restart/reload; effects/failure behavior +
        compatibility/deprecation; links without embedding secrets).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and
        every issue-1059 DoD bullet plus the template's four type-specific bullets is
        addressed by a distinct, identifiable section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against the issue's DoD checklist and
        the template's required sections; confirm every evidence entry supports its claim
        with an opened source, no second canonical document was created, and validate.py
        still passes.
        done when: the audit is written (in the final report, not a new file) and
        validate.py exits 0 on the current tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        command in its own tool call, then commit the plan and the new document together.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/
        tests -p "test_*.py"` reports OK and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file; steps are strictly sequential (evidence gathers before the
          body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
          commit. `review-adjudicate` and the cross-model final review pass are deferred to
          the batch owner's morning review — not run in this worktree.

BUDGET    STEP 1 and STEP 2. The hard part is describing the validation *contract* honestly
          as cross-cutting (fail-fast `Result`/`?`, a bare `panic!` for one cross-field
          check, `warn!`-and-ignore for `RELAY_OWNER_PUBKEY`, clamping for
          `BUZZ_DRAIN_JITTER_MS`) without silently smoothing over that these are genuinely
          different failure modes within the *same* file, and without duplicating the full
          settings catalogs #1051-#1058 own.

OPEN      Whether desktop's (Tauri/React) and mobile's (Flutter/Riverpod) own config-loading
          surfaces have an equivalent validation mechanism was not checked before this plan
          was written — STEP 1 checks it, and if desktop/mobile evidence is thin or absent,
          the node says so as a named gap (per `AGENTS.md` step 8) rather than inventing
          parity with the relay's mechanism. The issue's DoD bullet "states whether
          dynamically reloadable" is answered from the *absence* of a reload mechanism in
          the relay (an `rg` search, not an exhaustive negative proof) — classified
          INFERENCE with a stated confidence, not FACT.

LEFT OUT  Any `relationships` edge to the eight in-flight sibling `layers/configuration/*`
          nodes (#1051-#1058) — none are merged on `origin/launchpad` yet, and pointing at an
          unmerged id is a hard validation error in CI even if it resolves locally. A full
          settings catalog for any one surface (relay env vars, agent config, desktop/mobile
          config, feature flags, secrets, defaults) — that is #1051-#1058's job, not this
          node's. Editing `launchpad/docs/corpus/AGENTS.md`, `node.schema.json`, or
          `templates/configuration.md`. A second canonical document for any second
          concept/procedure discovered while writing (e.g. a config-schema-for-UI pattern in
          `buzz-backend-kubernetes::config_schema()` is described in prose here as evidence
          for the JSON-config mechanism, but is not spun into its own node).

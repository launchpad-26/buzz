Issue #1051 — task: document layers/configuration/agent-configuration.md
Stated size: no `Size` line on the issue — single-document corpus task per the task brief -> cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1051-agent-configuration`, rebased onto `origin/launchpad` at
    `ed133f4c5` ("Merge pull request #1923 from launchpad-26/sync-upstream-2026-08-31"),
    working tree clean.
  `launchpad/docs/corpus/schema/node.schema.json` is merged and authoritative
    (required: id, type, status, origin, audiences, evidence; relationships optional;
    `type` enum includes `layers`).
  `launchpad/docs/corpus/templates/configuration.md` (`corpus-template-configuration`)
    is merged and is this task's named template per the issue's Objective, and its own
    note-on-`type` section states a configuration-shaped node takes whichever `type`
    its subject's surface calls for, not a dedicated "configuration" type value.
  `launchpad/docs/corpus/layers/configuration/agent-configuration.md` does NOT exist.
    `launchpad/docs/corpus/layers/configuration/` itself does not exist on
    `origin/launchpad` yet, but a sibling task's own worktree
    (`task-1058-configuration-secrets`) has already drafted (uncommitted-to-launchpad)
    `layers/configuration/secrets.md` with `id: layers-configuration-secrets`,
    `type: layers` — read directly from that worktree as concrete precedent for this
    node's own front matter, not invented.
  `launchpad/docs/corpus/architecture/containers/agent-runtime.md`
    (`architecture-containers-agent-runtime`) is merged on `origin/launchpad` and
    describes the agent-runtime container at architecture-container altitude — a
    legitimate `references` target distinct from this node's configuration-catalog
    altitude.
  Evidence already gathered this session (paths actually opened, not recollected):
    `crates/buzz-acp/src/config.rs` (full CLI/env `CliArgs`/`Config`, `BUZZ_ACP_*`
    behavior knobs, `propagate_legacy_env_vars`), `crates/buzz-agent/src/config.rs`
    (`Config::from_env`, `BUZZ_AGENT_*` provider/timeout/budget knobs, provider
    selection, `validate()`), `desktop/src-tauri/src/managed_agents/env_vars.rs`
    (precedence doc comment, `DERIVED_PROVIDER_MODEL_ENV_KEYS`,
    `is_well_formed_env_key`, `MAX_ENV_VALUE_BYTES`/`MAX_ENV_TOTAL_BYTES`),
    `desktop/src-tauri/src/managed_agents/reserved_env_keys.rs` (`RESERVED_ENV_KEYS`,
    its own comment naming behavior knobs as freely overridable), `desktop/src-tauri/
    src/managed_agents/global_config/mod.rs` (precedence doc comment: baked build env
    < global < definition/instance < Buzz-identity), `desktop/src-tauri/src/
    managed_agents/effective_config/mod.rs` (`ConfigSource`, `resolve_linked`/
    `resolve_definition_less` precedence).
  `launchpad/docs/corpus/layers/configuration/secrets.md` (draft, sibling task #1058,
    not merged) already catalogues `BUZZ_PRIVATE_KEY`, `BUZZ_AUTH_TAG`,
    `BUZZ_ACP_PRIVATE_KEY`→`BUZZ_PRIVATE_KEY`, and the desktop's reserved-key
    stripping mechanism as the secret-shaped subset of this same surface — this node
    must not re-catalogue those rows, and cites that overlap in its boundary section
    without declaring a `relationships` edge to it (unmerged, not a valid target).
  No other merged corpus node under `origin/launchpad` covers agent-configuration
    (buzz-agent / buzz-acp / managed_agents env-config) handling; the sibling
    configuration nodes for #1052-#1059 are open, unmerged draft PRs and are NOT valid
    relationship targets per `AGENTS.md` step 9.

STEP 1  [independent]  Gather any remaining evidence needed beyond what is already
        recorded above: confirm the desktop `managed_agents` precedence chain
        (global < definition/persona < agent env, reserved-key rejection) against its
        own source rather than only its doc comments, and re-confirm which
        `BUZZ_AGENT_*` / `BUZZ_ACP_*` variables are genuinely deploy-varying per the
        Twelve-Factor litmus test vs. compile-time constants. Already substantially
        done in this session (this plan is written after gathering, not before).
        done when: every claim planned for the drafted document cites a path actually
        opened in this session, and no claim rests on inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/layers/configuration/agent-configuration.md` using
        `launchpad/docs/corpus/templates/configuration.md`'s required sections
        (configuration description, structured settings table, litmus-test statement,
        secrets discipline, boundary statement, relationships, scope and omissions).
        Scope: `buzz-agent`'s `Config::from_env` surface, `buzz-acp`'s CLI/env harness
        behavior knobs, and the desktop `managed_agents` env/config precedence and
        derived-key protections — excluding every row `layers/configuration/secrets.md`
        already owns (identity/secret env vars) and every surface owned by sibling
        tasks #1052 (defaults), #1053 (desktop), #1054 (environment), #1056 (mobile),
        #1057 (relay), #1059 (validation). Front matter: `id:
        layers-configuration-agent-configuration`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`,
        evidence ledger with a commit-citation provenance entry plus one entry per
        substantive claim classified FACT/INFERENCE/TEAM_KNOWLEDGE, `relationships:
        [{type: references, target: architecture-containers-agent-runtime}, {type:
        implements, target: corpus-template-configuration}]`. No secret value is ever
        quoted — only variable names, code paths, and placeholder sources; any
        genuinely secret-shaped var this surface owns (e.g. provider API keys) is
        marked `Secret: yes` and cites where the value comes from, never the value.
        done when: the file exists, front matter parses, every template-required
        section is present, and no line in the file contains a live credential/key/
        token value.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full tree including the new file. Fix and re-run on
        any failure.
        done when: the command exits 0.

STEP 4  [needs 3]  Earn the commit verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole prior command, confirm `OK`, then commit the plan +
        document with `git commit -s` in a separate call. Do not push, do not open a
        PR (integration happens in a separate batch step per Feature #611's revised
        one-PR-for-all-36 plan).
        done when: the unittest run reports OK, and the commit carries a
        `Signed-off-by:` trailer on the local `task/1051-agent-configuration` branch.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
          this session). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must report OK,
          this session, as the sole command run immediately before commit). No
          `review-adjudicate` or cross-model pass in this session — deferred to the
          batch owner per Feature #611's batch instructions.

BUDGET    STEP 2. The hard part is the boundary section: drawing a clean line against
          `layers/configuration/secrets.md` (identity/secret env vars),
          `architecture/containers/agent-runtime.md` (architecture altitude, not
          configuration catalog), and the six other in-flight configuration siblings,
          while still covering `buzz-agent`, `buzz-acp`, and `managed_agents`
          env/config surfaces at the depth the template's required sections demand.

OPEN      Whether `ANTHROPIC_API_KEY` / `OPENAI_COMPAT_API_KEY` / `OPENROUTER_API_KEY` /
          `DATABRICKS_TOKEN` (buzz-agent's own LLM-provider credential vars) belong in
          this node or are implicitly claimed by sibling `configuration-secrets`
          (#1058), whose merged scope-and-omissions section does not name them.
          Planned handling: include them here, marked `Secret: yes`, since they are
          genuinely part of buzz-agent's own configuration surface and no sibling
          node's evidence claims them — and name the potential overlap explicitly in
          this node's own boundary section rather than silently assuming ownership.

LEFT OUT  Editing `launchpad/docs/corpus/layers/configuration/secrets.md` or any other
          existing/sibling corpus node. Any `relationships` edge to the unmerged
          sibling configuration nodes (#1052-#1059) or to `layers/configuration/
          secrets.md` — not valid targets until merged. Full field-by-field
          enumeration of every `buzz-acp` CLI flag (60+ fields) or every
          `managed_agents` module — scoped to the settings that are genuinely
          deploy-varying agent configuration, with desktop-general settings and
          non-agent environment configuration left to the sibling nodes that own them.
          Deciding the open `ANTHROPIC_API_KEY`-ownership question above — reported as
          a named, deliberate choice, not silently resolved.

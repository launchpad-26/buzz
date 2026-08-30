Issue #1058 — task: document layers/configuration/secrets.md
Stated size: no `Size` line on the issue — single-document corpus task per the task brief, capped at 5 steps -> cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1058-configuration-secrets`, based on `origin/launchpad` at
    `338b4d0cf` ("Merge pull request #1779 from launchpad-26/task/605-corpus-batch-b"),
    working tree clean.
  `launchpad/docs/corpus/schema/node.schema.json` is merged and authoritative (required:
    id, type, status, origin, audiences, evidence; relationships optional; type enum
    includes `layers`).
  `launchpad/docs/corpus/templates/configuration.md` (`corpus-template-configuration`) is
    merged and is this task's named template per the issue's Objective.
  `launchpad/docs/corpus/layers/configuration/secrets.md` does NOT exist, and no
    `launchpad/docs/corpus/layers/` directory exists yet on `origin/launchpad` — this is
    the first `layers`-typed node.
  Evidence already gathered this session (paths actually opened, not recollected):
    `.env.example`, `.gitignore` (secrets exclusions), `crates/buzz-relay/src/config.rs`
    (`BUZZ_RELAY_PRIVATE_KEY` optional, dev-fallback, fail-closed panic paths),
    `crates/buzz-relay/src/main.rs` (fail-closed checks around `relay_private_key`),
    `crates/buzz-backend-kubernetes/src/env.rs` (`AUTHORITATIVE_KEYS`,
    `MAX_SECRET_BYTES`, POSIX-key validation), `crates/buzz-backend-kubernetes/src/pod.rs`
    (`build_secret`, `immutable: true`), `crates/buzz-backend-kubernetes/src/gc.rs`
    (`ORPHAN_SECRET_MIN_AGE_SECS`, clock-gated orphan sweep), `docs/remote-agents.md`
    (I1 identity fail-closed, I2 no secrets in configuration, the pre-secret negotiation
    staging-file gate, provider-output redaction), `crates/buzz-agent/src/mcp.rs`
    (subprocess env allowlist for `BUZZ_PRIVATE_KEY`), `desktop/src-tauri/src/
    secret_store.rs` (OS keyring blob store for the human's nsec, explicitly not on the
    env-read path), `desktop/src-tauri/src/managed_agents/env_vars.rs` (reserved-key
    stripping, POSIX-shape validation), `launchpad/AGENT_PR_TEMPLATE.md` (line 82, the
    "no secrets... in tracked files" checklist item).
  `launchpad/docs/corpus/architecture/deployment/kubernetes.md`
    (`architecture-deployment-kubernetes`) is merged and already documents the Helm
    chart's `secrets.existingSecret` / `secret-chart.yaml` mechanism at deployment-
    topology altitude — a legitimate `references` target for this node, which covers the
    same subject at configuration-catalog altitude instead (BUZZ_PRIVATE_KEY handling,
    the pre-secret staging gate, `buzz-backend-kubernetes` Secret creation/GC, `.env`
    separation) without duplicating it.
  No other merged corpus node under `origin/launchpad` covers secret-configuration
    handling; the sibling configuration nodes for #1051-#1057/#1059 are open, unmerged
    draft PRs and are NOT valid relationship targets per `AGENTS.md` step 9.

STEP 1  [independent]  Gather any remaining evidence needed beyond what is already
        recorded above: confirm `BUZZ_AUTH_TAG` and `BUZZ_S3_*` handling as
        deploy-varying settings, and re-confirm the litmus-test boundary (which
        `.env.example` values are secrets vs. non-secret deploy config) against the
        template's own required distinction. Already substantially done in this session
        (this plan is written after gathering, not before).
        done when: every claim planned for the drafted document cites a path actually
        opened in this session, and no claim rests on inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/layers/configuration/secrets.md` using
        `launchpad/docs/corpus/templates/configuration.md`'s required sections
        (configuration description, structured settings table, litmus-test statement,
        secrets discipline, boundary statement, relationships, scope and omissions).
        Front matter: `id: layers-configuration-secrets`, `type: layers`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator,
        reviewer]`, evidence ledger with a commit-citation provenance entry plus one
        entry per substantive claim classified FACT/INFERENCE/TEAM_KNOWLEDGE,
        `relationships: [{type: references, target: architecture-deployment-kubernetes},
        {type: implements, target: corpus-template-configuration}]`. No secret value is
        ever quoted — only variable names, code paths, and placeholder sources.
        done when: the file exists, front matter parses, every template-required section
        is present, and no line in the file contains a live credential/key/token value.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full tree including the new file. Fix and re-run on any
        failure.
        done when: the command exits 0.

STEP 4  [needs 3]  Earn the commit verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole prior command, confirm `OK`, then commit the plan +
        document with `git commit -s` in a separate call. Do not push, do not open a PR
        (integration happens in a separate batch step).
        done when: the unittest run reports OK, and the commit carries a
        `Signed-off-by:` trailer on the local `task/1058-configuration-secrets` branch.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
          this session). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must report OK,
          this session, as the sole command run immediately before commit). No
          `review-adjudicate` or cross-model pass in this session — deferred to the
          batch owner per Feature #611's batch instructions.

BUDGET    STEP 2. The hard part is the secrets-discipline section: every settings-table
          row marked `Secret: yes` must cite where the value comes from (env var name,
          loading code path, `.env.example`'s placeholder) and never the value itself,
          and the pre-secret staging gate / redaction mechanism from `docs/remote-
          agents.md` must be summarized accurately without restating its wire contract
          verbatim.

OPEN      Whether `BUZZ_AUTH_TAG` counts as a "secret" under the Twelve-Factor litmus
          test or as a non-secret signed attestation — `crates/buzz-agent/src/mcp.rs`'s
          own comment calls it "a non-secret signed ownership attestation." Planned
          handling: document it in the settings table with `Secret: no` and cite that
          comment, rather than defaulting every credential-shaped-sounding name to
          `Secret: yes`.

LEFT OUT  Editing `launchpad/docs/corpus/architecture/deployment/kubernetes.md` or any
          other existing corpus node. Any `relationships` edge to the unmerged sibling
          configuration nodes (#1051-#1057, #1059) — not valid targets until merged.
          Full field-by-field enumeration of every env var in
          `crates/buzz-relay/src/config.rs` (87 call sites) — scoped to the
          secret-shaped subset per this template's litmus test, with non-secret
          deploy-config left to the sibling configuration nodes that own it.
          Deciding whether `docs/remote-agents.md`'s pre-secret staging gate is fully
          implemented today (issue text already flags Known Defect 5 as open) — reported
          as a documented gap, not resolved here.

# Issue #1054 — layers/configuration/environment-configuration.md

Stated size: no `Size` line in the issue -> cap: 5 steps (per dispatch instructions).

ALREADY TRUE: `launchpad/docs/corpus/templates/configuration.md` (id `corpus-template-configuration`) is merged on `origin/launchpad`. `launchpad/docs/corpus/layers/configuration/environment-configuration.md` does not exist yet. The corpus tree on `origin/launchpad` currently holds only meta/governance nodes (`AGENTS.md`, `README.md`, `architecture/**`, `standards/**`) plus the `templates/**` tree — no other configuration-surface node is merged, so this is the first instance node built from the template. Sibling batch tasks #1051/#1052/#1053/#1055 are still open, unmerged PRs and are not valid relationship targets.

STEP 1  [independent] Gather evidence: read `.env.example` (repo root) in full; read `AGENTS.md`'s "Agent CLI (`buzz-cli`)" section on `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` auto-injection; read `desktop/src-tauri/src/managed_agents/agent_env.rs`, `env_vars.rs`, `reserved_env_keys.rs`, and the six-layer env-assembly comments/code in `desktop/src-tauri/src/managed_agents/readiness.rs` (`resolve_effective_agent_env_with_def`, ~lines 217-286) and `runtime.rs` (`spawn_agent_child`, descriptor.env write-order ~lines 558-568). Record `git rev-parse HEAD`. Note any conflicts found (none expected, but record if found) rather than resolving them silently. ← RUNS HERE
done when: the commit sha is recorded and every listed source has been opened and its content noted for use in STEP 2/3.

STEP 2  [needs 1] Write front matter: id `layers-configuration-environment-configuration`, type `layers`, status `draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, one evidence entry per substantive claim (FACT for opened sources, INFERENCE with confidence for reasoned claims, TEAM_KNOWLEDGE with provided_by for anything else), including the provenance FACT citing the STEP 1 commit. Relationships: `implements` -> `corpus-template-configuration` only (the template's own doc directs instance nodes to declare this; it is the only merged node that is a legitimate target).
done when: the file exists with schema-shaped front matter and every claim planned for the body has a matching evidence entry.

STEP 3  [needs 2] Write the body per `templates/configuration.md`'s required sections: configuration description (scope: environment-variable-based configuration only, explicitly excluding desktop UI settings, agent-persona config, defaults catalogued elsewhere, and feature flags — those are siblings #1053/#1052/#1055's scope, not yet merged), structured settings entries (relay `.env.example` vars + ACP harness vars + the six-layer desktop precedence), litmus-test statement, secrets discipline (no live credential values quoted), boundary statement, relationships section, and scope-and-omissions naming what was expected but not verified (e.g. full row-by-row coverage of `crates/buzz-relay/src/config.rs`'s ~87 call sites was not exhaustively audited).
done when: all seven required sections from `templates/configuration.md` are present and every DoD bullet from the issue is addressed somewhere in the document.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.
done when: the command exits 0.

STEP 5  [needs 4] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own call to earn the verify-gate stamp; confirm `OK`. Then, in a separate call, `git commit -s`. Do not push, do not open a PR.
done when: the unittest run reports `OK` and `git log` shows one new signed-off commit on `task/1054-environment-configuration` with no push and no PR opened.

PARALLEL: none — single file, single task, no dependency on the sibling batch tasks.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus unittest suite must report `OK` before commit. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner's later review — not run here.

BUDGET: small — one document, no code changes; evidence gathering scoped to `.env.example`, the ACP env section of `AGENTS.md`, and ~6 files under `desktop/src-tauri/src/managed_agents/`.

OPEN: Whether `implements -> corpus-template-configuration` is the right (only) relationship, given no other configuration-instance node exists yet to `references`/`part-of` — the template's own body explicitly recommends this edge for a merged instance, so this plan takes that as settled rather than reopening it. Whether the six-layer desktop precedence (baked -> runtime-metadata -> definition -> global -> persona -> agent) belongs in this node at all, since it configures *managed agent subprocesses* rather than the relay itself — this plan includes it because the issue's own dispatch instructions name it explicitly as in-scope evidence to walk, and because `BUZZ_PRIVATE_KEY`/`BUZZ_RELAY_URL` auto-injection is itself environment-variable configuration of an agent process, squarely inside "environment-variable-based configuration."

LEFT OUT: No coverage of desktop UI-persisted settings, agent persona configuration structures, or feature-flag values — those are siblings #1053, #1051/#1052, and #1055's scope respectively, not folded in here. No exhaustive row-by-row audit of every field in `crates/buzz-relay/src/config.rs` (dozens of fields) — a representative, evidence-backed sample is documented instead, with the gap named explicitly in scope-and-omissions. No attempt to fix or annotate any drift found between `.env.example` and the loading code's actual defaults — reported as-is, not resolved.

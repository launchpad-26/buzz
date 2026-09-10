# Issue #1206 — operations/deployment/local-development.md

Stated size: issue #1206 gives no explicit size line; parent Feature #618 dispatches one document per agent -> cap: 4 steps.

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/procedure.md`, `launchpad/docs/corpus/architecture/deployment/local-development.md` (id `architecture-deployment-local-development`), `launchpad/docs/corpus/development/hermit.md` (id `development-hermit`) and `launchpad/docs/corpus/development/prerequisites.md` (id `development-prerequisites`) are merged on `origin/launchpad`. `launchpad/docs/corpus/operations/deployment/local-development.md` does not exist yet (confirmed by `ls`). No `operations/**` node exists on `origin/launchpad` at recorded revision `473205a7457b208455f188847bfb27b01aa83cac` (confirmed against `<SCRATCH>/existing-node-ids.txt`), so this is the first operations node and #1203 (Docker-Compose deployment, sibling) is not a valid relationship target yet.

STEP 1 [independent] Gather evidence: read `Justfile` (`bootstrap`, `setup`, `hooks`, `down`, `ps`, `logs`, `reset`, `relay`, `relay-web`, `dev`, `desktop-dev`, `mobile-dev`, `migrate`, and internal `_ensure-services`/`_ensure-migrations`/`_ensure-sidecar-stubs`), `docker-compose.yml`, `.env.example`, `scripts/dev-setup.sh`, `scripts/dev-reset.sh`, `scripts/ensure-local-relay-key.sh`, `crates/buzz-relay/src/config.rs` (health/metrics port defaults, `BUZZ_AUTO_MIGRATE`), and `CONTRIBUTING.md`'s "Setting Up the Development Environment" section. Confirm the `/_readiness` verification mechanism `just dev` itself uses. ← RUNS HERE
done when: every cited file has been opened in this session and its relevant recipe/section text is in hand to cite verbatim.

STEP 2 [needs 1] Write front matter (id `operations-deployment-local-development`, type `operations`, status `draft`, origin `launchpad`, audiences `[operator, developer, agent]`, relationships: `implements: corpus-template-procedure`, `references: architecture-deployment-local-development`, `references: development-hermit`, `references: development-prerequisites` — all four ids confirmed present in `<SCRATCH>/existing-node-ids.txt`) and the body per the procedure template: Overview, Before you start, numbered task sections (first-time setup, start the relay, start a client, verify the relay is serving, stop/reset), See also, Boundary, Relationships, Scope and omissions. Link rather than restate the architecture node's topology/network-boundary content and the development nodes' toolchain content. State the boundary against #1203 (Docker-Compose deployment) in prose without linking it (no node exists yet).
done when: the file exists at `launchpad/docs/corpus/operations/deployment/local-development.md` with schema-shaped front matter and every Required section the procedure template lists.

STEP 3 [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until exit 0.
done when: the command's own exit code is 0.

STEP 4 [needs 3] Run the corpus unittest suite as the sole command in its own Bash call to earn the verification stamp, then commit (`git commit -s`) in a separate call. Do not push, do not open a PR.
done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK` and `git log -1` on this branch shows the new commit containing both the plan file and the node file.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK` as the sole command in its own call before commit. `review-adjudicate` and the cross-model final review pass are deferred to the batch owner — not run here.

BUDGET: small — one document, no code changes; evidence gathering scoped to the Justfile, docker-compose.yml, .env.example, three dev scripts, one config.rs excerpt, and CONTRIBUTING.md.

OPEN: Whether `just relay-web`, `just admin`, and `just mobile-dev`/`mobile-build-android` belong in this node's task sequence or are a level of detail this how-to should defer to `See also`/prose mention only — resolved by keeping the numbered tasks to the four paths the issue names explicitly (Hermit, `.env`, `just setup`, `just relay`, docker-compose services, `just dev`/`just desktop-dev`/`just mobile-dev`, and relay verification) and mentioning `relay-web`/`admin` only as a boundary note, not a numbered task, since they are not named in the issue's subject-matter list.

LEFT OUT: No relationship to `operations-deployment-docker-compose` (#1203) — not merged, would be a hard CI error if declared. No restatement of the architecture node's network-boundary/persistence/failure-recovery content (linked, not duplicated). No new corpus node for `just relay-web` or `just admin` — mentioned in prose only as adjacent paths this node does not cover. No attempt to execute `just setup`/`just dev`/`just relay` live in this session; evidence is read from source, and that gap is named in the node's own scope-and-omissions section, matching `architecture-deployment-local-development`'s own equivalent disclosure.

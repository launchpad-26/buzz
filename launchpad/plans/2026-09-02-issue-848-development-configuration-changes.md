# Plan — issue #848: `development/configuration-changes.md`

**Issue:** launchpad-26/buzz#848 (parent Feature #619)
**Branch:** `task/848-development-configuration-changes`
**Base revision:** `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`origin/launchpad`)
**Target:** `launchpad/docs/corpus/development/configuration-changes.md`
**Node shape:** procedure (`launchpad/docs/corpus/templates/procedure.md`)

---

## ALREADY TRUE

Verified against the worktree at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`:

- **The target file does not exist.** `launchpad/docs/corpus/development/` holds
  exactly `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`.
- **The corpus is large and merged.** 233-ish content nodes on `origin/launchpad`,
  including a full `layers/configuration/` shelf: `environment-configuration`,
  `relay-configuration`, `desktop-configuration`, `mobile-configuration`,
  `agent-configuration`, `secrets`, `defaults`, `feature-flags`, `validation`.
  Those catalogue **what** the configuration surface *is*. This node is the
  **how a contributor changes it** procedure — the duplication risk is real and
  the boundary must be stated explicitly.
- **Confirmed-resolvable relationship targets** (present on `origin/launchpad`):
  `development-prerequisites`, `development-hermit`,
  `layers-configuration-environment-configuration`,
  `layers-configuration-relay-configuration`, `layers-configuration-validation`,
  `layers-configuration-secrets`, `layers-configuration-feature-flags`,
  `corpus-template-procedure`.
- **ID convention settled by the dispatch brief:** `development-configuration-changes`.
  `standards/naming.md` MUST 3 prescribes a `corpus-` prefix, but its own evidence
  entry was written when only four meta-documents existed; every content node since
  uses `<directory>-<stem>`. Follow practice; note the tension in the report.
- **`.env.example` is 311 lines** and is the repository's configuration template.
- **`Config::from_env` in `crates/buzz-relay/src/config.rs`** (2378 lines) is the
  relay's env-var reader; `crates/buzz-relay/src/main.rs:152` fails startup on
  `ConfigError`.
- **`just bootstrap` copies `.env.example` to `.env` only when `.env` is absent**
  (`Justfile:42-44`) — so a new variable never reaches an existing developer's `.env`.
- **No automated parity check exists** between `.env.example` and `Config::from_env`.
  Searching the repo for `env.example` outside the corpus finds only: `.gitleaks.toml`
  (allowlist), `.github/workflows/ci.yml:1054` (dead-token grep), `Justfile`,
  `scripts/dev-setup.sh`, `scripts/test-ensure-local-relay-key.sh`, `README.md`,
  `AGENTS.md`, `CONTRIBUTING.md`, `.dockerignore`, `deploy/compose/`.

## STEP 1 — Record provenance and fix the ledger spine

Write the front matter: `id: development-configuration-changes`, `type: development`,
`status: draft`, `origin: launchpad`, `audiences: [developer, agent, reviewer]`.
First evidence entry is the FACT recording revision
`aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` as a `commit <sha>` citation.

**Done when:** front matter parses and `git cat-file -e` confirms the revision.

## STEP 2 — Write the ordered procedure

Body, exactly one `#` H1. Sections per the procedure template: Overview,
Before you start, the numbered task sequences (relay env var; desktop preview
feature flag; mobile compile-time default), Verify, Roll back, See also,
Boundary, Relationships, Scope and omissions.

Every step cites a file actually opened: `.env.example`,
`crates/buzz-relay/src/config.rs` (`Config::from_env`, `parse_bool`,
`positive_u64_from_env`, `inert_env_vars`, the `ENV_MUTEX`/`env_of` test pattern),
`crates/buzz-relay/src/main.rs`, `Justfile`, `scripts/ensure-local-relay-key.sh`,
`scripts/dev-setup.sh`, `preview-features.json`,
`desktop/src/shared/features/manifest.ts`, `resolveEnabled.ts`,
`desktop/vite.config.ts`, `mobile/lib/shared/relay/relay_provider.dart`,
`.gitleaks.toml`, `.github/workflows/ci.yml`, `CONTRIBUTING.md`.

**Done when:** every DoD bullet in #848 has a section that answers it, including
the procedure tail (goal, prerequisites, ordered executable steps, success
verification, rollback, authoritative links, explicit scope-and-omissions).

## STEP 3 — Relationships, checked against the merge target

Declare only `references` edges whose targets were confirmed by
`git ls-tree -r --name-only origin/launchpad`. Prefer few; back the rest with a
prose *See also*.

**Done when:** every declared target appears in the merged id list.

## STEP 4 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm PASS
(UNVERIFIED notices acceptable, errors not). Confirm the file is under the
1000-line repository ceiling.

**Done when:** validate.py exits 0.

## STEP 5 — Earn the gate, then commit

Run the corpus test suite as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm OK. Then `git add` + `git commit -s` in a separate call. Stop at the commit.

**Done when:** one commit exists on the branch; nothing pushed.

## PARALLEL

None. Steps 1-5 are strictly sequential — the ledger must exist before the body
cites it, and the gate must pass before the commit.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` → exit 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
- File under 1000 lines (repository-wide `just file-size-check`).
- Exactly one hand-authored canonical document changed, plus this plan.

## BUDGET

Five steps. One new corpus document plus this plan. No source changes, no
generated outputs, no second canonical node.

## OPEN

- Whether the `corpus-` id prefix tension (naming.md MUST 3 versus corpus-wide
  practice) should be resolved in the standard or in practice. **Not decided
  here, and not filed here** — reported to the dispatcher instead.
- Whether the absent `.env.example` ↔ `Config::from_env` parity check should
  become a CI gate. Stated as a gap in the node; not proposed as a change.

## LEFT OUT

- Deployment-time configuration (`deploy/compose/`, `launchpad/deploy/`,
  Kubernetes/Helm) — that is an operations surface, not a development procedure.
- Cataloguing the configuration surface itself — owned by the
  `layers/configuration/` nodes already merged.
- Any change to runtime behaviour, CI, or the naming standard.

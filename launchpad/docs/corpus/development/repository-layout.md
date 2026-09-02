---
id: development-repository-layout
type: development
status: draft
origin: launchpad
audiences:
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "At the recorded revision the tracked repository root holds 74 entries, of which 27 are directories; the layout tables in this node were derived from that listing rather than copied from any prose inventory."
    entry_class: FACT
    evidence:
      - "git_ls_tree(HEAD, top level) -> 74 entries; git_ls_tree(-d, HEAD, top level) -> 27 directories"
  - statement: "crates/ contains exactly 30 subdirectories, and the root Cargo.toml's [workspace] members array contains exactly 32 entries: those same 30 crates/ paths plus launchpad/crates/knowledge and examples/countdown-bot; a set difference in both directions between the crates/ directory listing and the crates/-rooted member paths is empty, so every crates/ subdirectory is a workspace member and no member path under crates/ is missing from disk."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "python3_setdiff(git ls-tree -d --name-only HEAD crates/ vs Cargo.toml [workspace] members) -> total members: 32; under crates/: 30; not under crates/: ['launchpad/crates/knowledge', 'examples/countdown-bot']; dirs not in members: []; member crates/ paths not dirs: []"
  - statement: "The root Cargo.toml carries exclude = [\"desktop/src-tauri\"] as a sibling key of members, so the desktop app's Tauri (Rust) backend is deliberately outside the root workspace and is a separate Cargo project."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
  - statement: "launchpad/crates/ contains exactly one entry, launchpad/crates/knowledge, and launchpad/AGENTS.md records cohort Rust crates in the root workspace as a named, accepted exception to the fork's file-placement rule, with the members list gaining one append-only entry per cohort crate under launchpad/crates/."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "git_ls_tree(HEAD, 'launchpad/crates/') -> launchpad/crates/knowledge"
  - statement: "pnpm-workspace.yaml lists exactly three packages -- desktop, web, admin-web -- and additionally declares allowBuilds, overrides and patchedDependencies keys, the last of which points at files under patches/."
    entry_class: FACT
    evidence:
      - "pnpm-workspace.yaml"
  - statement: "migrations/ contains 40 SQL files named 0001_initial_schema.sql through 0040_push_message_kinds.sql, numbered contiguously with a four-digit zero-padded prefix."
    entry_class: FACT
    evidence:
      - "migrations/0040_push_message_kinds.sql"
      - "git_ls_tree(HEAD, 'migrations/') -> 40 entries, 0001_initial_schema.sql .. 0040_push_message_kinds.sql"
  - statement: "The top-level schema/ directory contains exactly one file, schema.sql, and is distinct from launchpad/docs/corpus/schema/, which holds the corpus front-matter JSON Schemas."
    entry_class: FACT
    evidence:
      - "schema/schema.sql"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "The repository has both a plural scripts/ directory (shell, Node, Python and SQL developer tooling) and a singular script/ directory whose sole tracked entry is script/start."
    entry_class: FACT
    evidence:
      - "script/start"
      - "scripts/dev-setup.sh"
      - "git_ls_tree(HEAD, 'script/') -> script/start (one entry)"
  - statement: "15 tracked directories named scripts exist at any depth -- the top-level scripts/ plus 14 others, including .github/scripts, desktop/scripts, web/scripts, mobile/scripts, launchpad/scripts, launchpad/deploy/scripts, launchpad/deploy/archived/scripts, benchmarks/harbor-buzz-orchestra/scripts, and six under launchpad/skills/ -- so an unqualified reference to \"scripts\" in this repository is ambiguous."
    entry_class: FACT
    evidence:
      - ".github/scripts/codex-security-review.js"
      - "launchpad/scripts/preflight_core.py"
      - "git_ls_tree(-r, -d, --name-only, HEAD, filter=basename equals scripts) -> 15 paths: .github/scripts, benchmarks/harbor-buzz-orchestra/scripts, desktop/scripts, launchpad/deploy/archived/scripts, launchpad/deploy/scripts, launchpad/scripts, six under launchpad/skills/ (analysis-technique, evidence-reduce, gh-admin, rca-report, review-queue-automation, root-cause-analysis), mobile/scripts, scripts, web/scripts"
  - statement: "bin/ is a Hermit environment directory: bin/README.hermit.md states the symlinks in it are managed by Hermit and automatically download and install Hermit and its packages, bin/hermit.hcl contains manage-git = true, and git ls-tree reports mode 120000 (symlink) for the tool entries such as bin/node and bin/just while bin/activate-hermit is a mode 100755 regular file."
    entry_class: FACT
    evidence:
      - "bin/README.hermit.md"
      - "bin/hermit.hcl"
      - "git_ls_tree(HEAD, 'bin/node' 'bin/just' 'bin/activate-hermit') -> 120000 blob bin/node; 120000 blob bin/just; 100755 blob bin/activate-hermit"
  - statement: ".github/workflows/ contains 30 workflow files, of which exactly 10 carry the launchpad- filename prefix (adr-check, agents-tests, corpus-schema-tests, corpus-validate, issue-check, pr-check, review-agent-controls, review-agent-publish, rqa-tests, security-audit)."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
      - "git_ls_tree(HEAD, '.github/workflows/') -> 30 entries, 10 matching 'launchpad'"
  - statement: "examples/ contains three tracked entries: README.md, countdown-bot/ (a Cargo project and the only examples/ path in the root workspace members list) and meadow-core/ (an agent plugin directory holding .plugin, README.md, agents/, instructions.md and skills/, with no Cargo.toml)."
    entry_class: FACT
    evidence:
      - "examples/countdown-bot/Cargo.toml"
      - "examples/meadow-core/instructions.md"
      - "git_ls_tree(HEAD, 'examples/') -> README.md, countdown-bot, meadow-core"
  - statement: "Four agent-harness dot-directories exist at the root -- .agents/, .claude/, .codex/, .goose/ -- each containing only a skills/ subdirectory; .agents, .codex and .goose resolve to the identical git tree object 29ac008e0cca9003af93386e56944e52f80165e1 (each holding desktop-screenshot and sprout-cli), while .claude resolves to a different tree, ec3d203640bd7b6fddbf78038ff29f39a259b1c0, holding eight skills including the corpus-author, corpus-plan and corpus-review packs."
    entry_class: FACT
    evidence:
      - ".agents/skills/sprout-cli/SKILL.md"
      - ".codex/skills/sprout-cli/SKILL.md"
      - ".goose/skills/desktop-screenshot/SKILL.md"
      - ".claude/skills/corpus-author/SKILL.md"
      - "git_ls_tree(HEAD, .agents .claude .codex .goose) -> .agents/.codex/.goose all tree 29ac008e0cca9003af93386e56944e52f80165e1; .claude tree ec3d203640bd7b6fddbf78038ff29f39a259b1c0"
      - "git_ls_tree(HEAD, one call per dot-directory skills subtree) -> .agents/.codex/.goose each desktop-screenshot plus sprout-cli; .claude agentic-debugging, corpus-author, corpus-batch-author, corpus-plan, corpus-review, desktop-screenshot, review-final, sprout-cli"
  - statement: "Because three of the four harness directories are byte-identical git trees while the fourth is a strict superset in subject matter, the three are best read as mirrored copies of one shared skill pair kept in step for three harnesses, and .claude/ as the harness that additionally carries cohort-specific corpus tooling; no file in the repository was found stating that this mirroring is maintained deliberately or by what mechanism."
    entry_class: INFERENCE
    evidence:
      - ".agents/skills/sprout-cli/SKILL.md"
      - ".claude/skills/corpus-author/SKILL.md"
      - "git_ls_tree(HEAD, .agents .claude .codex .goose) -> three identical tree hashes, one distinct"
      - "git_ls_tree(HEAD, one call per dot-directory skills subtree) -> identical two-entry listings for .agents/.codex/.goose"
    confidence: 0.75
  - statement: "The root configuration files this node catalogues carry the contents attributed to them: Justfile declares build, check, ci, test and clean recipes; rust-toolchain.toml declares [toolchain] with channel = \"1.95.0\" and profile = \"default\"; lefthook.yml declares three hook lanes, pre-commit, commit-msg and pre-push; deny.toml declares [advisories] and [licenses] sections for cargo-deny; and biome.json's top-level keys are $schema, vcs, files, formatter, linter, assist, javascript and css."
    entry_class: FACT
    evidence:
      - "Justfile"
      - "rust-toolchain.toml"
      - "lefthook.yml"
      - "deny.toml"
      - "biome.json"
  - statement: "The repository root carries three generated lockfiles -- Cargo.lock, pnpm-lock.yaml and (one level down) mobile/pubspec.lock -- which are tool-produced resolutions of the hand-authored manifests Cargo.toml, the pnpm package.json files and mobile/pubspec.yaml."
    entry_class: FACT
    evidence:
      - "Cargo.lock"
      - "pnpm-lock.yaml"
      - "mobile/pubspec.lock"
  - statement: "CLAUDE.md at the repository root is not a regular file: git ls-tree reports mode 120000 for it and git cat-file -p HEAD:CLAUDE.md prints the single line AGENTS.md, so it is a symlink to AGENTS.md rather than a second copy of that guidance."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "git_ls_tree(HEAD) -> 120000 blob 47dc3e3d863cfb5727b87d785d09abf9743c0a72 CLAUDE.md; git_cat_file(-p, HEAD:CLAUDE.md) -> AGENTS.md"
  - statement: "AGENTS.md carries a fenced cohort block delimited by the HTML comments 'launchpad-26 fork: begin' and 'launchpad-26 fork: end' which states that this repository is a fork of block/buzz operated by the launchpad-26 cohort, that everything above the block is upstream's contributor guide, and that launchpad/README.md and launchpad/AGENTS.md supersede it for anything under launchpad/ and .github/workflows/launchpad-*."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
  - statement: "LAUNCHPAD.md states it is Launchpad-specific and not upstream, and gives the reason it exists as a separate root file: AGENTS.md is maintained by block/buzz and changes often, so editing it would create a merge conflict on every upstream sync."
    entry_class: FACT
    evidence:
      - "LAUNCHPAD.md"
  - statement: "launchpad/AGENTS.md §3 'Where cohort files go' states 'Never move or rename upstream files', gives upstream's size as roughly 3,800 files, and then enumerates named, knowingly accepted exceptions including .github/ISSUE_TEMPLATE/, .github/PULL_REQUEST_TEMPLATE.md, the Hermit lefthook pin (bin/lefthook and bin/.lefthook-*.pkg, per ADR-0017), five named deployment-provenance files (deploy/compose/compose.yml, deploy/compose/.env.example, deploy/compose/README.md, Dockerfile, .github/workflows/docker.yml, per ADR-0005), root MCP server registration in .mcp.json (per ADR-0046), and cohort Rust crates in the root workspace."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "desktop/src/launchpad/ exists inside upstream's desktop source tree and holds exactly two tracked files, settings/registry.ts and settings/knowledge/KnowledgeSettingsPanel.tsx; the former's own header comment describes itself as the registration seam granted by ADR-0051 and amended by ADR-0053, under which a cohort Settings section is added there rather than by editing upstream's SettingsPanels.tsx registration sites."
    entry_class: FACT
    evidence:
      - "desktop/src/launchpad/settings/registry.ts"
      - "launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md"
      - "launchpad/decisions/ADR-0053-settings-seam-owns-nav-groups.md"
  - statement: "desktop/src/launchpad/ is cohort-owned code sitting inside an upstream-owned directory, which means the upstream/fork split is not cleanly expressible as a top-level path partition; launchpad/AGENTS.md's own enumerated exception list does not name it, so the list read alone under-describes where cohort code actually lives."
    entry_class: INFERENCE
    evidence:
      - "desktop/src/launchpad/settings/registry.ts"
      - "launchpad/AGENTS.md"
      - "launchpad/decisions/ADR-0051-cohort-settings-registration-seam.md"
    confidence: 0.8
  - statement: "launchpad/AGENTS.md's directory map lists an entry 'upstream-intel/   upstream tracking tooling', but no such path exists at the recorded revision: ls launchpad/upstream-intel reports 'No such file or directory' and git ls-tree HEAD launchpad/ does not list it."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "ls(launchpad/upstream-intel) -> 'cannot access launchpad/upstream-intel: No such file or directory'; git_ls_tree(HEAD, 'launchpad/') -> AGENTS.md, AGENT_PR_TEMPLATE.md, ARCHITECTURE.md, ENVIRONMENTS.md, README.md, REQUIREMENTS.md, Research, SECURITY-POSTURE.md, VISION.md, agents, crates, decisions, deploy, docs, labels.yml, plans, project-intelligence, review-agent, scripts, skills, sync-labels.sh"
  - statement: "The nonexistent upstream-intel/ entry in launchpad/AGENTS.md's directory map is already tracked as its own issue and is not re-filed by this node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2033"
  - statement: "ADR-0046 grants that a .mcp.json at the repository root may register cohort MCP servers, but no .mcp.json exists at the recorded revision: it is absent from git ls-tree HEAD's 74 top-level entries and ls reports 'No such file or directory' for it -- so that exception is a standing permission rather than a description of a present file."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0046-root-mcp-registration-exception.md"
      - "git_ls_tree(HEAD, '.mcp.json') -> no output; ls(.mcp.json) -> 'cannot access .mcp.json: No such file or directory'"
  - statement: "launchpad/ holds 21 tracked entries at its own top level, and its directory children carry these tracked-entry counts: Research 54, agents 6, crates 1, decisions 57, docs 3, plans 81, project-intelligence 37, review-agent 57, scripts 47, skills 7; a listing of each child's first entries shows plans/ holding dated issue-plan Markdown, Research/ holding numbered research notes, decisions/ holding ADR-NNNN-*.md files, project-intelligence/ holding CONTRACT.md alongside Python modules, review-agent/ holding the review agent's own documents, and skills/ holding one directory per skill."
    entry_class: FACT
    evidence:
      - "launchpad/README.md"
      - "launchpad/project-intelligence/CONTRACT.md"
      - "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md"
      - "git_ls_tree(HEAD, one call per launchpad child, first three entries) -> plans: 2026-08-12-issue-116-pr-review-preflight.md, 2026-08-12-issue-117-review-dimensions.md, 2026-08-12-issue-119-publish-one-review.md; Research: 314-huddle-join-attribution.md, 315-desktop-stdout-destination.md, 316-frontend-error-retention.md; review-agent: .gitignore, ADJUDICATION.md, CONTAINMENT.md; project-intelligence: CONTRACT.md, answer.py, assemble.py; agents: goose_config.py, project-pack.py, requirements.txt; skills: analysis-technique, evidence-reduce, gh-admin; decisions: ADR-0001-handbook-repository-location-and-publication-target.md, ADR-0002-handbook-source-repository-scope.md, ADR-0003-handbook-page-provenance-contract.md"
      - "git_ls_tree(HEAD, launchpad/) -> 21 entries; git_ls_tree(HEAD, one call per launchpad child directory) -> Research 54, agents 6, crates 1, decisions 57, docs 3, plans 81, project-intelligence 37, review-agent 57, scripts 47, skills 7"
  - statement: "launchpad/docs/ contains exactly three entries -- Observability, audits and corpus -- so the corpus this node belongs to is one of three siblings under the cohort documentation tree, not the whole of it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "git_ls_tree(HEAD, 'launchpad/docs/') -> Observability, audits, corpus"
  - statement: "Both a top-level deploy/ (charts/, compose/, local/ -- upstream's Helm charts and Compose bundles) and a launchpad/deploy/ (ansible/, archived/, docker/, runbooks/, its own AGENTS.md and README.md -- the cohort's host configuration and hardening) exist, and likewise both a top-level docs/ and a launchpad/docs/; the duplicated names are the fork boundary expressed as parallel trees, not a single tree split in two."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "git_ls_tree(HEAD, 'deploy/') -> charts, compose, local (3 entries); git_ls_tree(HEAD, 'launchpad/deploy/') -> .gitignore, AGENTS.md, CLAUDE.md, README.md, VPS-DEPLOYMENT-AUDIT.md, ansible, archived, docker, run.sh, runbooks, scripts, temp-handoff.md, test-run-guard.sh, virtual-box (14 entries)"
  - statement: "git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus, run against the merge target before this node's front matter was finalized, returns 233 paths and contains no launchpad/docs/corpus/development/repository-layout.md; the development/ directory on that branch holds exactly four nodes: build.md, debugging.md, hermit.md and prerequisites.md."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/development/hermit.md"
      - "git_ls_tree(-r, --name-only, origin/launchpad, 'launchpad/docs/corpus') -> 233 paths; development/ = {build.md, debugging.md, hermit.md, prerequisites.md}; no development/repository-layout.md"
  - statement: "Of the 158 content nodes on origin/launchpad (the corpus tree excluding schema/, standards/, templates/, AGENTS.md and README.md), 157 carry an unprefixed <directory>-<stem> id and exactly one -- development/build.md, id corpus-development-build -- carries a corpus- prefix."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "python3_id_census(git ls-tree -r origin/launchpad -- launchpad/docs/corpus, excluding schema//standards//templates//AGENTS.md/README.md) -> content nodes: 158; corpus- prefixed: 1 [development/build.md -> corpus-development-build]; unprefixed: 157"
  - statement: "launchpad/docs/corpus/standards/naming.md MUST 3 states that a document's id must be recognizable on sight as its filename and that, concretely at its own recorded revision, this means: strip .md, lowercase the stem, prefix with corpus-, and for a document one level below the corpus root inside a purpose-named subdirectory insert that subdirectory's singular form before the stem."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
  - statement: "The divergence between naming.md MUST 3's literal corpus- prefix and the unprefixed form 157 of 158 merged content nodes use is already tracked as its own issue; this node follows the measured content-node convention and does not re-file the discrepancy."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2029"
  - statement: "launchpad/docs/corpus/templates/reference.md (id corpus-template-reference) is merged on origin/launchpad and prescribes the body sections a Diátaxis Reference-form node carries: a reference description, structured entries, an optional Commands section, a boundary statement, relationships, and scope-and-omissions."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/reference.md"
      - "git_show(origin/launchpad:launchpad/docs/corpus/templates/reference.md) -> id: corpus-template-reference"
  - statement: "Issue #871, 'task: document development/workspace.md', is open and unwritten at the time this node was checked, so Cargo/pnpm workspace mechanics in depth are that task's subject rather than this one's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#871"
  - statement: "Issue #863's Definition of Done requires this node to be structured for lookup rather than narrative teaching, to contain only facts supported by current source while labelling generated versus authored values, to define its scope and omissions, and to link authoritative source, schema and config."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#863 definition of done"
relationships:
  - type: references
    target: corpus-development-build
  - type: references
    target: development-hermit
---

# Repository layout: reference

What lives where in this repository, at the top level and one level down. Every
table below was derived from `git ls-tree` against the recorded revision, not
transcribed from an existing prose inventory -- see *How these tables were produced*
for why that distinction is load-bearing here. This node catalogues **placement**: it
does not say what a crate does, how to build it, or how the Cargo workspace resolves.
Those boundaries are named in *Boundary* below.

This checkout is the **launchpad-26 fork of `block/buzz`**. Ownership does not follow
directory nesting cleanly, so *Upstream versus cohort ownership* is a section of its
own rather than a column in the tables.

## How these tables were produced

| Value | Status |
|---|---|
| Every path, count and file mode in this node | **Authored**, transcribed by hand from a named `git ls-tree`, `ls`, or `git cat-file` run recorded in this node's provenance ledger |
| Any part of this document | **Not generated.** The corpus has no generator; `launchpad/docs/corpus/AGENTS.md` records that every non-`.md` file under the corpus root is rejected today because no generator exists to reproduce it |

Separately, some of the **repository content** catalogued below is itself tool-generated
rather than hand-authored, and that distinction matters when deciding whether to edit a
file directly:

| Repository path | Generated or authored |
|---|---|
| `Cargo.lock`, `pnpm-lock.yaml`, `mobile/pubspec.lock` | **Generated** — resolver output for the authored manifests `Cargo.toml`, the pnpm `package.json` files, and `mobile/pubspec.yaml` |
| `bin/node`, `bin/just`, `bin/cargo`, and the other tool entries in `bin/` | **Generated** — mode `120000` symlinks managed by Hermit, per `bin/README.hermit.md` |
| `bin/activate-hermit`, `bin/hermit.hcl`, `bin/README.hermit.md` | **Authored** (mode `100755` / `100644` regular files) |
| Everything else in the tables below | **Authored** |

## Top-level layout

74 tracked entries, 27 of them directories. Directories first, then the root files
worth locating.

| Path | What it holds |
|---|---|
| `crates/` | The Rust workspace's 30 crates — see *The Rust workspace* |
| `desktop/` | Tauri 2 + React desktop app; `src/` (frontend) and `src-tauri/` (Rust backend, **outside** the root workspace) |
| `web/` | Browser web client — Vite + React, `src/{app,assets,features,shared}` |
| `admin-web/` | Operator admin UI — the smallest frontend: `src/` holds 7 files, no `features/` split |
| `mobile/` | Flutter app — `lib/`, `android/`, `ios/`, `assets/`, `test/`, `scripts/` |
| `migrations/` | 40 SQL migrations, `0001_initial_schema.sql` … `0040_push_message_kinds.sql` |
| `schema/` | One file: `schema.sql` (desired-state Postgres schema). Not the corpus schema |
| `scripts/` | Developer tooling — shell, Node, Python, SQL, plus `cutover/` and `maintenance/` |
| `script/` | **Singular, and separate.** One tracked entry: `script/start`. 15 directories named `scripts` exist repo-wide; qualify the path |
| `bin/` | Hermit environment — pinned toolchain symlinks plus `activate-hermit` |
| `.github/` | `workflows/` (30 files), `scripts/`, `hooks/`, `ISSUE_TEMPLATE/` (8), `CODEOWNERS`, `PULL_REQUEST_TEMPLATE.md` |
| `examples/` | `README.md`, `countdown-bot/` (Cargo project, a workspace member), `meadow-core/` (agent plugin, no `Cargo.toml`) |
| `launchpad/` | **The cohort's own tree** — see *The cohort tree* |
| `deploy/` | Upstream deployment assets: `charts/`, `compose/`, `local/` |
| `docs/` | Upstream documentation: `nips/`, `spec/`, `formal/`, `admin/`, `assets/`, plus loose `.md` files |
| `benchmarks/` | `buzz-dataset/`, `harbor-buzz-orchestra/` |
| `perf/` | `RELAY_BUS_SCALING.md` and its Python harness + test |
| `patches/` | Two pnpm patch files, referenced by `pnpm-workspace.yaml`'s `patchedDependencies` |
| `test-fixtures/` | One file: `entity-links.json` |
| `.agents/`, `.codex/`, `.goose/` | Agent-harness skill directories; all three are the **same git tree object**, each holding `skills/{desktop-screenshot,sprout-cli}` |
| `.claude/` | A **different** tree: `skills/` with 8 entries, adding `agentic-debugging`, `corpus-author`, `corpus-batch-author`, `corpus-plan`, `corpus-review`, `review-final` |
| `.cargo/` | `config.toml` |
| `.intersect/` | `sadscan.yaml` |
| `.release/` | `desktop-candidate.json` |
| `.vscode/` | `settings.json` |

Root files that answer "where is the authoritative X":

| File | Authority for |
|---|---|
| `Cargo.toml` | Rust workspace membership and exclusions; shared dependency versions |
| `Cargo.lock` | Resolved Rust dependency graph (generated) |
| `rust-toolchain.toml` | The pinned Rust channel `rustup` resolves inside this repository |
| `pnpm-workspace.yaml` | The three pnpm packages, plus `overrides` and `patchedDependencies` |
| `pnpm-lock.yaml` | Resolved JS dependency graph (generated) |
| `Justfile` | Every task recipe (`just build`, `just ci`, `just test`, …) |
| `lefthook.yml`, `lefthook-local.yml` | Git hook lanes — `pre-commit`, `commit-msg`, `pre-push` |
| `biome.json` | JS/TS lint + format configuration (`formatter`, `linter`, `assist`, `javascript`, `css` keys) |
| `deny.toml` | `cargo-deny` policy — `[advisories]` and `[licenses]` sections |
| `.env.example` | Environment-variable template |
| `docker-compose.yml`, `docker-compose.harness.yml` | Local service stacks |
| `Dockerfile`, `Dockerfile.push-gateway`, `Dockerfile.sprig` | Container builds |
| `AGENTS.md` | Contributor/agent guide. **`CLAUDE.md` is a `120000` symlink to it**, not a second copy |
| `LAUNCHPAD.md` | Fork orientation, kept out of `AGENTS.md` to avoid a merge conflict on every upstream sync |

## The Rust workspace

`crates/` holds **30** subdirectories. The root `Cargo.toml` `[workspace] members`
array holds **32** entries: those same 30, plus two paths that live outside `crates/`.
A set difference in both directions is empty — no `crates/` subdirectory is missing
from `members`, and no `crates/`-rooted member path is missing from disk.

| Members entry | Where it lives |
|---|---|
| 30 × `crates/<name>` | `crates/` |
| `launchpad/crates/knowledge` | The cohort tree — the only entry in `launchpad/crates/` |
| `examples/countdown-bot` | `examples/` |

The 30 crates, as `git ls-tree` lists them:

```
buzz-acp                buzz-conformance        buzz-persona            buzz-voice
buzz-admin              buzz-core               buzz-pubsub             buzz-workflow
buzz-agent              buzz-datastore-tracing  buzz-push-gateway       buzz-ws-client
buzz-audit              buzz-db                 buzz-relay              git-credential-nostr
buzz-auth               buzz-deletion           buzz-relay-mesh         git-sign-nostr
buzz-backend-kubernetes buzz-dev-mcp            buzz-sdk                sprig
buzz-cli                buzz-media              buzz-search
buzz-pair-relay         buzz-pairing-cli        buzz-test-client
```

**`desktop/src-tauri` is excluded.** `Cargo.toml` carries
`exclude = ["desktop/src-tauri"]` as a sibling key of `members`, so the desktop app's
Rust backend is a separate Cargo project with its own manifest. A workspace-wide
`cargo` invocation from the repository root does not reach it; it needs
`--manifest-path desktop/src-tauri/Cargo.toml`.

**`launchpad/crates/knowledge` is a member.** Cohort Rust code participating in
upstream's workspace is one of the named exceptions in `launchpad/AGENTS.md` §3, which
records the `members` list as gaining one append-only entry per cohort crate under
`launchpad/crates/`.

## Frontend and mobile trees, one level down

| Tree | One level down |
|---|---|
| `desktop/src/` | `app/`, `features/`, `shared/`, `testing/`, `types/`, `launchpad/`, `main.tsx`, four `.d.ts` files |
| `desktop/` (other) | `src-tauri/`, `scripts/`, `public/`, `tests/`, four `playwright.*.config.ts` files, `package.json`, `vite.config.ts`, `tailwind.config.js`, `biome.json` |
| `web/src/` | `app/`, `assets/`, `features/`, `shared/`, `main.tsx`, `vite-env.d.ts` |
| `admin-web/src/` | Flat: `App.tsx`, `api.ts`, `main.tsx`, `styles.css`, `types.ts`, `useResource.ts`, `vite-env.d.ts` |
| `mobile/lib/` | `features/`, `shared/`, `app.dart`, `main.dart` |
| `mobile/` (other) | `android/`, `ios/`, `assets/`, `test/`, `scripts/`, `pubspec.yaml`, `pubspec.lock`, `analysis_options.yaml` |

`desktop/`, `web/` and `admin-web/` are the three packages `pnpm-workspace.yaml` lists,
sharing one root `pnpm-lock.yaml`. `mobile/` is outside that workspace and resolves via
`pubspec.yaml` / `pubspec.lock`.

**`desktop/src/launchpad/` is cohort code inside upstream's tree** — see
*Upstream versus cohort ownership*.

## The cohort tree: `launchpad/`

21 tracked entries. This is where `launchpad/AGENTS.md` §3 directs cohort files —
see *Upstream versus cohort ownership* for the named exceptions that sit elsewhere.

The "What it holds" column below is `launchpad/AGENTS.md`'s own directory map where
that map covers the entry (`AGENTS.md`, `AGENT_PR_TEMPLATE.md`, `labels.yml`,
`sync-labels.sh`, `agents/`, `skills/`, `decisions/`, `docs/`, `deploy/`); for the
entries its map omits (`Research/`, `plans/`, `project-intelligence/`,
`review-agent/`, `scripts/`, `crates/`) it is derived from a listing of that
directory's first entries. The counts are `git ls-tree` totals in every row.

| Entry | What it holds | Tracked entries |
|---|---|---|
| `AGENTS.md` | Cohort contributor guide; §3 governs file placement | — |
| `README.md` | Cohort entry point | — |
| `AGENT_PR_TEMPLATE.md` | PR body schema for agent-authored PRs | — |
| `ARCHITECTURE.md`, `ENVIRONMENTS.md`, `REQUIREMENTS.md`, `SECURITY-POSTURE.md`, `VISION.md` | Cohort planning documents | — |
| `labels.yml`, `sync-labels.sh` | Label source of truth and its applier | — |
| `Research/` | Research notes | 54 |
| `agents/` | Persona packs for Buzz-native agents | 6 |
| `crates/` | Cohort Rust crates — one: `knowledge` | 1 |
| `decisions/` | ADRs, once accepted | 57 |
| `deploy/` | Host configuration and hardening: `ansible/`, `docker/`, `runbooks/`, `scripts/`, `virtual-box/`, `archived/` | 14 |
| `docs/` | `Observability/`, `audits/`, `corpus/` | 3 |
| `plans/` | Implementation plans | 81 |
| `project-intelligence/` | Evidence contract and the corpus validator | 37 |
| `review-agent/` | Review-agent implementation | 57 |
| `scripts/` | Cohort tooling (e.g. `preflight_core.py`) | 47 |
| `skills/` | `launchpad-26` organization skills | 7 |

**This node lives at `launchpad/docs/corpus/development/repository-layout.md`** — one
of three siblings under `launchpad/docs/`, not the whole cohort documentation tree.

**`launchpad/AGENTS.md` and `launchpad/agents/` are different things.** The first is
the contributor guide; the second holds persona packs.

## Upstream versus cohort ownership

`AGENTS.md` carries a fenced block delimited by `<!-- launchpad-26 fork: begin -->` and
`<!-- launchpad-26 fork: end -->`. Inside it: this repository is a fork of `block/buzz`
operated by the launchpad-26 cohort; everything above the block is upstream's guide;
`launchpad/README.md` and `launchpad/AGENTS.md` supersede it for anything under
`launchpad/` and `.github/workflows/launchpad-*`.

**The general rule**, from `launchpad/AGENTS.md` §3: cohort files go under
`launchpad/`, and upstream files are never moved or renamed — upstream is roughly
3,800 files and merges from it are regular, so a rename turns every future merge into
manual work.

**Cohort-owned paths outside `launchpad/`**, each a named exception:

| Path | Basis |
|---|---|
| `.github/workflows/launchpad-*.yml` (10 of 30 workflows) | Named in `AGENTS.md`'s fork block |
| `.github/ISSUE_TEMPLATE/` | Replaces upstream's, which pointed at `block/buzz` |
| `.github/PULL_REQUEST_TEMPLATE.md` | One added section |
| `bin/lefthook`, `bin/.lefthook-*.pkg` | Hermit pin diverging from upstream — ADR-0017 |
| `deploy/compose/compose.yml`, `deploy/compose/.env.example`, `deploy/compose/README.md`, `Dockerfile`, `.github/workflows/docker.yml` | Deployment image provenance — ADR-0005. Settled; adding a sixth file changes that record |
| `.mcp.json` | Root MCP server registration — ADR-0046. **Granted but unused:** no `.mcp.json` exists at this revision |
| `launchpad/crates/*` in `Cargo.toml` `members` | Cohort Rust crates in the root workspace |
| `desktop/src/launchpad/` | Settings registration seam — ADR-0051, amended by ADR-0053 |

The last row is why ownership is not a top-level path partition. `desktop/src/launchpad/`
holds two tracked files (`settings/registry.ts`, `settings/knowledge/KnowledgeSettingsPanel.tsx`)
and sits inside upstream's desktop source tree; `settings/registry.ts`'s own header names the ADRs
that grant it. It is **not** in `launchpad/AGENTS.md` §3's enumerated exception list, so
reading that list alone under-describes where cohort code lives.

The duplicated top-level names — `deploy/` and `launchpad/deploy/`, `docs/` and
`launchpad/docs/` — are this boundary expressed as parallel trees, not one tree split.

## Known error in an existing layout map

`launchpad/AGENTS.md`'s own directory map lists:

```
  upstream-intel/      upstream tracking tooling
```

**No such path exists** at the recorded revision. `ls launchpad/upstream-intel` reports
"No such file or directory", and `git ls-tree HEAD launchpad/` does not list it. This is
already tracked as its own issue (see the provenance ledger); it is recorded here so a
reader comparing the two maps knows which one the tree supports, and it is deliberately
absent from the `launchpad/` table above.

## Boundary

This node does not describe:

- **What any crate, package or module does.** Placement only. Subject-matter coverage
  belongs to the `architecture/containers/*` nodes (`relay`, `desktop`, `mobile`,
  `cli`, `postgres`, `redis`, `push-gateway`, `object-storage`, `agent-runtime`, `web`),
  which are merged on `origin/launchpad`.
- **How to build anything here.** `development/build.md` is the canonical build
  procedure; this node does not restate its commands, its member counts, or its
  verification steps.
- **Cargo/pnpm workspace mechanics in depth** — resolver behaviour, feature
  unification, how `exclude` interacts with `--workspace`. This node states only the
  membership and exclusion facts a reader needs to locate code. Issue #871
  (`development/workspace.md`) owns the mechanics and is open and unwritten.
- **Why the layout is the way it is.** The reasoning behind crate boundaries or the
  `src-tauri` exclusion is explanation, not reference; no such node exists yet.
- **How to install the toolchains** the tables mention — `development/hermit.md` and
  `development/prerequisites.md` own that.
- **File-level inventory below one directory deep**, except where a directory's whole
  content is small enough to enumerate exactly (`schema/`, `script/`, `test-fixtures/`,
  `patches/`, `desktop/src/launchpad/`, `launchpad/crates/`).
- **Untracked paths.** Every listing is `git ls-tree` against a commit, so build output
  (`target/`, `node_modules/`, `mobile/build/`) and any gitignored local file is out of
  scope by construction.

## Relationships

Two `references` edges are declared. Both targets were resolved against
`origin/launchpad` with `git show origin/launchpad:<path>`, not against this worktree:

- `corpus-development-build` — `launchpad/docs/corpus/development/build.md`. This node
  states *where* the workspace members are; that node states *how* to compile them.
  `references` is the right type: no ownership or currency dependency, and this node's
  layout tables stay accurate whether or not that node's build commands change.
- `development-hermit` — `launchpad/docs/corpus/development/hermit.md`. This node
  catalogues `bin/` as a Hermit environment directory of managed symlinks; that node
  owns Hermit itself.

**Checked and not declared.** `development-prerequisites` and `debugging` are the other
two `development/` nodes on `origin/launchpad`; neither is cited by this node's body, and
an edge asserting supporting context that the prose does not actually use would be noise.
The `architecture/containers/*` nodes are named in *Boundary* as the owners of
per-component subject matter, but this node cites none of them as evidence for a
placement claim, so no edge is declared toward them either. No `depends-on`, `part-of`,
`implements` or `supersedes` edge applies: this node is independently maintainable, it
replaces nothing, and it implements no specification.

## Scope and omissions

**This node covers** the tracked contents of the repository root and one level below it
at the recorded revision: the 30 crates and the 32-entry Cargo workspace membership
(including the `desktop/src-tauri` exclusion and the `launchpad/crates/knowledge`
member), the four frontend/mobile trees, `migrations/`, `schema/`, both `scripts/` and
`script/`, `bin/`, `.github/`, `examples/`, the agent-harness dot-directories, the
cohort `launchpad/` tree, which repository values are tool-generated rather than
authored, and where the upstream/fork ownership line actually falls.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| What each crate/package does | `launchpad/docs/corpus/architecture/containers/*.md` |
| Compiling any of it | `launchpad/docs/corpus/development/build.md` |
| Cargo/pnpm workspace mechanics in depth | #871 `development/workspace.md` — open, unwritten |
| Installing the toolchains | `launchpad/docs/corpus/development/hermit.md`, `launchpad/docs/corpus/development/prerequisites.md` |
| Why the layout is shaped this way | No explanation node exists for this |
| Deployment topology of `deploy/` and `launchpad/deploy/` | `launchpad/docs/corpus/architecture/deployment/*.md` |
| What each `Justfile` recipe does | No reference node exists for the `Justfile` |
| The corpus front-matter contract this node's own header obeys | `launchpad/docs/corpus/schema/node.schema.json` |
| Whether `desktop/src/launchpad/` belongs in `launchpad/AGENTS.md` §3's exception list | Not this node's to settle — the ADRs grant the seam; the list's completeness is a separate question |

**A note on this node's `id`.** It is `development-repository-layout` — the unprefixed
`<directory>-<stem>` form. `standards/naming.md` MUST 3 literally prescribes a `corpus-`
prefix, but a census of `origin/launchpad` shows 157 of 158 merged content nodes use the
unprefixed form and exactly one (`development/build.md`) does not. This node follows the
measured convention. The discrepancy is already tracked as its own issue and is recorded
here rather than re-filed.

**Expected but not verified when this node was written:**

- **No listing was made against `block/buzz` itself.** The upstream/cohort split above
  is taken from this repository's own declarations — `AGENTS.md`'s fenced block,
  `LAUNCHPAD.md`, `launchpad/AGENTS.md` §3 and the ADRs it cites. Whether every path
  outside `launchpad/` is in fact byte-identical to upstream was not checked, and the
  "roughly 3,800 files" figure is quoted from `launchpad/AGENTS.md`, not recounted here.
- **`launchpad/AGENTS.md` §3's exception list was not audited for completeness.**
  `desktop/src/launchpad/` was found by walking the tree and is absent from that list;
  whether other cohort-owned paths outside `launchpad/` are likewise unlisted was not
  established. This node's evidence reaches one level below each top-level directory,
  which is exactly how `desktop/src/launchpad/` surfaced; cohort code sitting deeper
  than that — as its own `settings/knowledge/` subtree does — would not have been seen.
- **No directory below the second level was enumerated**, except where a whole subtree
  was small enough to state exactly. `crates/<name>/src/`, `desktop/src/features/`,
  `mobile/lib/features/` and their peers are out of reach of this node's evidence.
- **The mirroring of `.agents/`, `.codex/` and `.goose/` is inferred from three
  identical git tree hashes**, not from any file stating that they are kept in step, or
  by what mechanism. Nothing was found that would tell a reader which of the four
  harness directories is the source and which are copies.
- **Untracked working-tree state was not inspected.** Every count is `git ls-tree`
  against the recorded commit; a developer's actual checkout will contain more.

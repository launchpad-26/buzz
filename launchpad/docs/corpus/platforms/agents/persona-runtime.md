---
id: platforms-agents-persona-runtime
type: architecture
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision cad6c375fdcc590158c1456c9fc7875f0f84a844."
    entry_class: FACT
    evidence:
      - "commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "buzz-persona's Cargo.toml describes it as 'Parser and loader for Buzz persona pack files (.persona.md)', and its only runtime dependencies are external crates -- serde (with the derive feature), serde_json, serde_yaml and thiserror -- with tempfile as its sole dev-dependency; it declares no dependency on any other buzz-* crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/Cargo.toml"
  - statement: "crates/buzz-persona/src/lib.rs contains no crate-level `//!` doc comment; it consists of exactly six `pub mod` declarations (manifest, merge, pack, persona, resolve, validate) with no other content."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/lib.rs"
  - statement: "Of the six modules, four (manifest.rs, persona.rs, resolve.rs, validate.rs) open with a genuine module-level `//!` doc comment stating that module's responsibility; the other two (pack.rs, merge.rs) open only with an outer `///` doc comment attached to the following item, not a module-level `//!` comment, so the crate's overall responsibility is reconstructed from four of six modules' own doc comments plus the Cargo.toml description, not from one authoritative crate-level statement."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/manifest.rs:1-14"
      - "crates/buzz-persona/src/persona.rs:1-13"
      - "crates/buzz-persona/src/resolve.rs:1-11"
      - "crates/buzz-persona/src/validate.rs:1-10"
      - "crates/buzz-persona/src/pack.rs:1-15"
      - "crates/buzz-persona/src/merge.rs:1-8"
  - statement: "resolve.rs's module doc states that resolve_pack() is the crate's main entry point: it loads a pack directory, applies merge policy, composes prompts, merges MCP servers and projects env vars, producing a ResolvedPack designed backward from ACP's Config so that every field maps directly to what the agent runtime consumes; it further states the module is pure (no env access, no network, no side effects)."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:1-11"
  - statement: "pack::load_pack(pack_dir: &Path) -> Result<LoadedPack, PackError> reads a pack directory (.plugin/plugin.json manifest, each listed .persona.md file, optional instructions.md, optional .mcp.json, and an optional skills/ directory) and returns a LoadedPack; every relative path it resolves is passed through safe_resolve(), which rejects a leading '/' or Windows drive letter, rejects any '..' path component before canonicalization, and rejects a canonicalized result that does not have pack_root as a prefix."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/pack.rs:117-241"
      - "crates/buzz-persona/src/pack.rs:317-364"
  - statement: "pack::resolve_skills(pack_dir: &Path, personas: &[LoadedPersona]) -> HashMap<String, Vec<String>> assigns each on-disk skill directory to personas: a skill named in at least one persona's `skills:` array goes only to the personas that named it, and a skill named in no persona's `skills:` array goes to every persona."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/pack.rs:243-315"
  - statement: "resolve::resolve_pack(pack_dir: &Path) -> Result<ResolvedPack, PackError> calls pack::load_pack() and then resolve_loaded_pack(), which runs semantic validation (rejects zero personas, duplicate persona names, and persona names with characters outside [a-zA-Z0-9_-] or over 64 characters) before producing one ResolvedPersona per persona with system_prompt, resolved model/provider split, merged MCP servers, resolved triggers, and projected runtime_env_vars."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:104-254"
  - statement: "resolve::resolve_persona_by_name(pack_dir: &Path, name: &str) -> Result<ResolvedPersona, PackError> is a convenience wrapper that calls resolve_pack() and then looks up one persona by name, returning PackError::PersonaNotFound if absent."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:184-194"
  - statement: "runtime_env_vars() in resolve.rs is a pure function (explicitly documented as not reading the current process environment) that projects a persona's model/temperature/max_context_tokens into child-process environment variables, branching on the persona's declared `runtime` field: `runtime: \"buzz-agent\"` emits BUZZ_AGENT_MODEL/BUZZ_AGENT_PROVIDER, any other value (including none, which the crate's own test names 'no_runtime_defaults_to_goose') emits GOOSE_PROVIDER/GOOSE_MODEL, and both branches additionally emit GOOSE_TEMPERATURE and GOOSE_CONTEXT_LIMIT when those fields are set."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:361-400"
      - "crates/buzz-persona/src/resolve.rs:604-610"
  - statement: "validate::validate_pack(pack_dir: &Path) -> ValidationReport delegates all structural checks to pack::load_pack() per its own module doc ('if loading succeeds, the pack is structurally valid by definition'), then runs advisory checks for things the typed parsers silently drop, such as unknown keys; ValidationReport::exit_code() returns 0 for no diagnostics, 1 if any Error diagnostic is present, and 2 if only Warning diagnostics are present."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/validate.rs:1-10"
      - "crates/buzz-persona/src/validate.rs:33-72"
      - "crates/buzz-persona/src/validate.rs:143"
  - statement: "manifest::parse_manifest(content: &str) -> Result<PackManifest, ManifestError> and manifest::parse_manifest_file(path: &Path) -> Result<PackManifest, ManifestError> parse a `.plugin/plugin.json` pack manifest into a typed PackManifest, whose module doc states that every persona pack ships this file to describe OPS metadata and tell Buzz where to find personas, hooks and MCP config."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/manifest.rs:1-14"
      - "crates/buzz-persona/src/manifest.rs:152-193"
  - statement: "persona::parse_persona_md(content: &str) -> Result<PersonaConfig, PersonaError>, persona::parse_persona_file(path: &Path) -> Result<PersonaConfig, PersonaError>, persona::split_frontmatter(content: &str) -> Result<(&str, &str), PersonaError> and persona::split_model(model: &str) -> (Option<&str>, &str) are persona.rs's public functions; persona.rs's module doc states a `.persona.md` file is YAML frontmatter between `---` delimiters followed by a markdown body that becomes the system prompt, and the module defines MAX_FRONTMATTER_BYTES (1 MiB) and MAX_BODY_BYTES (256 KiB) as public size-limit constants."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/persona.rs:1-24"
      - "crates/buzz-persona/src/persona.rs:208-330"
  - statement: "merge::merge_behavioral_config() and merge::resolve_persona_config() implement precedence levels 3-5 of the crate's 5-level model (per-persona frontmatter, then pack-level `defaults`, then hardcoded built-in defaults), per merge.rs's own doc comment, which states levels 1-2 (operator env vars, desktop UI overrides) are resolved outside this crate, at runtime."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/merge.rs:1-9"
      - "crates/buzz-persona/src/merge.rs:47-85"
  - statement: "PERSONA_PACK_SPEC.md documents the full precedence model as five levels -- operator env vars, Desktop UI per-agent overrides, per-persona frontmatter, pack-level defaults, built-in defaults, highest wins -- and states that buzz-acp resolves levels 3-5 at deploy time while levels 1-2 are applied at runtime and are outside the pack's control; merge.rs's own module doc corroborates the levels-3-5 boundary this crate implements."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:632-658"
      - "crates/buzz-persona/src/merge.rs:1-9"
  - statement: "crates/buzz-cli/Cargo.toml and crates/buzz-acp/Cargo.toml each declare `buzz-persona = { path = \"../buzz-persona\" }`, and desktop/src-tauri/Cargo.toml declares the same crate under a renamed package alias, `buzz_persona_pkg = { package = \"buzz-persona\", path = \"../../crates/buzz-persona\" }`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/Cargo.toml"
      - "crates/buzz-acp/Cargo.toml:22"
      - "desktop/src-tauri/Cargo.toml:106"
  - statement: "crates/buzz-cli/src/commands/pack.rs actually calls into buzz-persona: buzz_persona::validate::validate_pack(), buzz_persona::validate::ValidationDiagnostic (both Error and Warning variants), buzz_persona::resolve::resolve_pack(), and buzz_persona::resolve::ResolvedPack are all referenced there, backing buzz-cli's `buzz pack` subcommands."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/pack.rs:25"
      - "crates/buzz-cli/src/commands/pack.rs:29-32"
      - "crates/buzz-cli/src/commands/pack.rs:67"
      - "crates/buzz-cli/src/commands/pack.rs:97"
  - statement: "desktop/src-tauri/src/migration.rs actually calls buzz_persona_pkg::persona::split_frontmatter() to separate a persona file's YAML frontmatter from its markdown body during a migration routine."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/migration.rs:1126"
  - statement: "Grepping every .rs file under crates/buzz-acp/src for the literal string 'buzz_persona' returns zero matches, despite buzz-acp's Cargo.toml declaring a direct path dependency on buzz-persona; buzz-acp's own source instead uses a same-named field, `config.persona_env_vars`, and free-text comments mentioning 'persona', neither of which is a call into the buzz-persona crate's own API."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='buzz_persona', scope='crates/buzz-acp/src/**/*.rs') -> no matches, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
      - "crates/buzz-acp/Cargo.toml:22"
  - statement: "Because buzz-acp declares a direct Cargo.toml dependency on buzz-persona but its source tree contains no reference to any of the crate's public items, either buzz-acp's persona-pack loading currently happens through a path this search did not cover (for example a build script, a re-export chain, or a dependency declared for a future integration not yet wired up), or the dependency is presently unused; which of these is true was not established here, and no runtime-behavior claim is made about how buzz-acp currently obtains persona configuration."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-acp/Cargo.toml:22"
      - "grep_repo(pattern='buzz_persona', scope='crates/buzz-acp/src/**/*.rs') -> no matches, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
    confidence: 0.55
  - statement: "launchpad/docs/corpus/architecture/containers/agent-runtime.md (id: architecture-containers-agent-runtime, type: architecture, status: draft) is merged on origin/launchpad and already states as FACT that buzz-persona is a direct path dependency of buzz-acp, resolved harness-side before the agent subprocess is prompted, and links crates/buzz-persona/PERSONA_PACK_SPEC.md for the persona-pack format; this node is the component-level detail one level below that container-level claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
  - statement: "At the recorded revision, git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus lists no node anywhere under a platforms/ path and no second architecture-typed node besides the ten architecture/containers/*.md files, the architecture/context/*.md files, the architecture/deployment/*.md files, the architecture/flows/*.md files and the architecture/principles/*.md files -- none of which is a component-level node this one could declare part-of, depends-on or references toward without misstating buzz-persona's actual containment."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, at commit cad6c375fdcc590158c1456c9fc7875f0f84a844"
  - statement: "Issue #1233's Definition of Done requires this node to state responsibility and a well-defined interface/boundary, name dependencies and collaborators, link source implementation and tests, and explain only component-level behavior rather than the entire containing platform."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1233 definition of done"
  - statement: "crates/buzz-persona/tests/integration.rs (650 lines) and crates/buzz-persona/tests/e2e_env_flow.rs (371 lines) are the crate's two integration test files; integration.rs includes full_pipeline_load_and_validate, resolve_full_pipeline, resolve_multi_persona_pack, resolve_persona_by_name_found/not_found, validation_catches_missing_required_fields, validation_catches_unknown_behavioral_keys and operator_config_fields_rejected_in_frontmatter, while e2e_env_flow.rs includes resolve_pack_goose_persona_emits_correct_runtime_env_vars, resolve_pack_buzz_agent_persona_emits_buzz_agent_vars and full_pipeline_two_runtimes_different_env_vars."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/tests/integration.rs"
      - "crates/buzz-persona/tests/e2e_env_flow.rs"
---

# Component: `buzz-persona` (persona runtime)

`buzz-persona` is the crate that parses, merges and resolves a **persona
pack** -- a portable bundle of one or more agent personas, skills, MCP server
configuration and pack-level instructions -- into the fully-resolved,
ACP-ready form `buzz-acp` needs to run an agent. This node documents it as
one component, one level below the container-level claim already made by
[`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md);
see [`node.schema.json`](../../schema/node.schema.json) for the field contract
this front matter satisfies and [`AGENTS.md`](../../AGENTS.md) for how this
node was authored and checked. No per-type template governs a
`platforms/agents/*` node yet (`launchpad/docs/corpus/templates/`'s
`architecture-component.md` and `component.md` exist but disagree with each
other on `type`, and neither is named authoritative by `AGENTS.md`'s own gap
table); this node instead follows the shape and evidence discipline the
merged `agent-runtime.md` container node already established, scaled down to
one component.

## Responsibility

No single `//!` crate-level doc comment states `buzz-persona`'s
responsibility -- `src/lib.rs` is six bare `pub mod` declarations and nothing
else. The responsibility below is reconstructed from `Cargo.toml`'s
description plus the module-level `//!` doc comments that four of the six
modules do carry (`manifest.rs`, `persona.rs`, `resolve.rs`, `validate.rs`;
`pack.rs` and `merge.rs` open with an outer `///` comment on the next item
instead, not a module doc):

- **Parse.** `manifest.rs` parses a pack's `.plugin/plugin.json`; `persona.rs`
  parses one `.persona.md` file's YAML frontmatter plus its markdown-body
  system prompt.
- **Merge.** `merge.rs` resolves precedence levels 3-5 of the pack's 5-level
  behavioral-config model (per-persona frontmatter, then pack-level
  `defaults`, then built-in defaults) -- levels 1-2 (operator env vars,
  Desktop UI overrides) are explicitly out of this crate's scope, resolved by
  the caller at runtime instead.
- **Load.** `pack.rs`'s `load_pack()` reads a whole pack directory (manifest,
  every listed persona file, optional `instructions.md`/`.mcp.json`/`skills/`)
  into a typed `LoadedPack`, resolving every relative path through a
  traversal-safe resolver.
- **Resolve.** `resolve.rs`'s `resolve_pack()` is the crate's main entry
  point: load, merge, compose prompts, merge MCP servers and project env
  vars into a `ResolvedPack` -- per its own doc comment, "designed backward
  from ACP's `Config`" so every field maps directly to what the agent
  runtime consumes, and explicitly pure (no env access, no network, no side
  effects).
- **Validate.** `validate.rs`'s `validate_pack()` backs the `buzz pack
  validate` command: it delegates all structural checks to `load_pack()`
  ("if loading succeeds, the pack is structurally valid by definition," per
  its own doc comment) and layers advisory warnings on top for things the
  typed parsers silently drop, such as unknown keys.

The full authoring contract for a persona pack -- directory layout,
`.persona.md` schema, the two-layer prompt architecture, MCP/hooks/skills
delivery, distribution and migration -- is
[`crates/buzz-persona/PERSONA_PACK_SPEC.md`](../../../../../crates/buzz-persona/PERSONA_PACK_SPEC.md),
not this node; see *Boundary* below.

## Public interface

| Item | Kind | Contract | Evidence |
|---|---|---|---|
| `pack::load_pack(dir: &Path)` | fn | Loads a pack directory into a `LoadedPack`; rejects path traversal via `safe_resolve()`. | `crates/buzz-persona/src/pack.rs:125` |
| `pack::resolve_skills(dir, personas)` | fn | Assigns each on-disk skill to the personas that claimed it, or to every persona if none claimed it. | `crates/buzz-persona/src/pack.rs:249` |
| `resolve::resolve_pack(dir: &Path)` | fn | Load + merge + compose + project, in one call; the crate's main entry point. | `crates/buzz-persona/src/resolve.rs:110` |
| `resolve::resolve_persona_by_name(dir, name)` | fn | Convenience wrapper: resolve the whole pack, then find one persona by name. | `crates/buzz-persona/src/resolve.rs:188` |
| `resolve::ResolvedPack` / `ResolvedPersona` | struct | ACP-ready output shape; every field maps directly to what the agent runtime consumes. | `crates/buzz-persona/src/resolve.rs:22-102` |
| `validate::validate_pack(dir: &Path)` | fn | Structural + advisory validation; backs `buzz pack validate`. | `crates/buzz-persona/src/validate.rs:143` |
| `validate::ValidationReport` | struct | `exit_code()`: 0 clean, 1 has errors, 2 warnings only. | `crates/buzz-persona/src/validate.rs:35-72` |
| `manifest::parse_manifest(content: &str)` / `parse_manifest_file(path)` | fn | Parses `.plugin/plugin.json` into a typed `PackManifest`. | `crates/buzz-persona/src/manifest.rs:152-193` |
| `persona::parse_persona_md(content: &str)` / `parse_persona_file(path)` | fn | Parses one `.persona.md` file (frontmatter + body) into `PersonaConfig`. | `crates/buzz-persona/src/persona.rs:208-262` |
| `persona::split_frontmatter(content: &str)` | fn | Splits raw `.persona.md` text into `(frontmatter, body)`; the one function an external consumer (Desktop) calls directly. | `crates/buzz-persona/src/persona.rs:277` |
| `persona::split_model(model: &str)` | fn | Splits a `"provider:model-id"` string into `(Option<provider>, model_id)`. | `crates/buzz-persona/src/persona.rs:324` |
| `merge::merge_behavioral_config` / `resolve_persona_config` | fn | Precedence levels 3-5 of the 5-level behavioral-config model. | `crates/buzz-persona/src/merge.rs:47-85` |
| `PackError` / `ManifestError` / `PersonaError` | enum | `thiserror`-derived error types for load/manifest/persona-parse failures respectively. | `crates/buzz-persona/src/pack.rs:25-54`, `manifest.rs:23-32`, `persona.rs:27-48` |

## Dependencies

**Depends on** (this component requires these to build/run):

| Component | Why | Evidence |
|---|---|---|
| `serde` (derive feature) | `Serialize`/`Deserialize` for every pack/persona/config type. | `crates/buzz-persona/Cargo.toml` |
| `serde_json` | `.plugin/plugin.json` and `.mcp.json` parsing; JSON `Value` used for raw MCP/defaults passthrough. | `crates/buzz-persona/Cargo.toml` |
| `serde_yaml` | `.persona.md` YAML frontmatter parsing. | `crates/buzz-persona/Cargo.toml` |
| `thiserror` | Derives `PackError`, `ManifestError`, `PersonaError`. | `crates/buzz-persona/Cargo.toml` |
| `tempfile` (dev-only) | Test fixtures build real temp-directory packs. | `crates/buzz-persona/Cargo.toml` |

`buzz-persona` declares no dependency on any other `buzz-*` crate in this
repository -- it is a leaf in the internal dependency graph.

**Depended on by** (these require this component):

| Component | Real usage confirmed? | Evidence |
|---|---|---|
| `buzz-cli` | Yes -- `buzz_persona::validate::validate_pack`, `ValidationDiagnostic`, `resolve::resolve_pack`, `resolve::ResolvedPack` are all called from `commands/pack.rs`, backing the `buzz pack` subcommands. | `crates/buzz-cli/Cargo.toml`, `crates/buzz-cli/src/commands/pack.rs:25-97` |
| `desktop` (`src-tauri`, package alias `buzz_persona_pkg`) | Yes -- `buzz_persona_pkg::persona::split_frontmatter` is called from a migration routine. | `desktop/src-tauri/Cargo.toml:106`, `desktop/src-tauri/src/migration.rs:1126` |
| `buzz-acp` | **Declared, not confirmed.** The Cargo.toml path dependency exists, but grepping every file under `crates/buzz-acp/src` for `buzz_persona` returns zero matches. Whether the harness reaches this crate through a path this node did not find, or the dependency is currently unused, is not established here -- see *Scope and omissions*. | `crates/buzz-acp/Cargo.toml:22` |

## Boundary

This node does not describe:
- **The persona-pack authoring contract in full** -- directory layout, the
  `.persona.md` field reference, the two-layer `[Base]`/`[System]` prompt
  architecture, MCP/hooks/skills delivery mechanics, distribution phases, or
  V6/JSON migration. `PERSONA_PACK_SPEC.md` is the canonical source; this
  node cites it rather than restating it.
- **What `buzz-acp` does with a resolved pack** -- prompt assembly, dispatch,
  subprocess spawning, env-var injection ordering, and the operator-precedence
  rule (operator env vars always win) are `buzz-acp`'s own behavior, described
  in its own README and in the container-level
  [`architecture-containers-agent-runtime`](../../architecture/containers/agent-runtime.md)
  node -- not this crate's, and (per the dependency gap above) not
  demonstrably wired to this crate's API today.
- **The agent-runtime container's full decomposition** -- this node documents
  one component (`buzz-persona`) standing alone, not the container `buzz-acp`
  runs inside, its other components, or its inbound/outbound interfaces.
- **`buzz-cli`'s own `pack` subcommand surface** (`buzz pack validate`,
  `buzz pack inspect`, `buzz pack build`) -- that CLI surface is `buzz-cli`'s
  own component, which happens to call into this one.

## Relationships

**Declared: none.** Checked, not assumed:

- `buzz-persona` is depended on (by Cargo.toml, with confirmed real usage in
  two of three cases) by **three different containers** --
  `buzz-acp`/agent-runtime, `buzz-cli`, and `desktop` -- at the recorded
  revision. A `part-of` edge naming any one of them would misstate this
  crate as scoped to that container alone, when it is shared infrastructure
  used across at least two confirmed and one declared consumer.
- No node anywhere under `launchpad/docs/corpus/platforms/` exists yet on
  `origin/launchpad` (confirmed with `git ls-tree -r --name-only
  origin/launchpad -- launchpad/docs/corpus`), so there is no sibling
  component node to `depends-on` or `references`.
- The only existing `architecture`-typed node that could plausibly relate --
  `architecture-containers-agent-runtime` -- is a container-level node, not a
  component-level one; nothing in `relationships.schema.json`'s five types
  cleanly describes "one of several consumers of this component" without
  overclaiming exclusivity. This mirrors the precedent `agent-runtime.md`
  itself already set for declaring no relationships when the available
  targets do not actually fit.
- A `relationships[].target` naming an id no node in the merge-target corpus
  carries is a hard validation error (`AGENTS.md` step 9); none of the above
  targets were treated as safe to guess around.

## Scope and omissions

**This node covers** the `buzz-persona` crate's responsibility as
reconstructed from its own module doc comments and `Cargo.toml`; its public
interface (parse/merge/load/resolve/validate functions and their core
types); its build-time dependencies and its confirmed and declared
dependents; and an explicit boundary against the persona-pack authoring
spec, `buzz-acp`'s own runtime behavior, and the agent-runtime container's
full decomposition.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full persona-pack authoring contract (layout, prompt architecture, MCP/hooks/skills delivery, distribution, migration) | `crates/buzz-persona/PERSONA_PACK_SPEC.md` |
| `buzz-acp`'s prompt assembly, dispatch and env-injection behavior | `crates/buzz-acp/README.md`, `architecture-containers-agent-runtime` |
| The agent-runtime container's full decomposition (all its components, its inbound/outbound interfaces) | `architecture-containers-agent-runtime` |
| `buzz-cli`'s own `pack` subcommand CLI surface | A future `platforms/*` node for `buzz-cli`, not filed as of this writing |
| The four sibling `platforms/agents/*` component tasks (`acp-harness`, `buzz-agent`, `dev-mcp`, `kubernetes-backend`) and `sprig` | `launchpad-26/buzz#1229`, `#1230`, `#1231`, `#1232`, `#1234` respectively |

**Expected but not verified when this node was written:**

- **How `buzz-acp` actually obtains persona/pack configuration at runtime,
  given its declared-but-apparently-unused dependency on this crate.** This
  node states the grep result as `FACT` and reasons about three possible
  explanations as `INFERENCE` (confidence 0.55) without resolving which is
  true. A follow-up investigation, not this documentation task, would need
  to trace `buzz-acp`'s actual pack-loading code path (if any exists today)
  to close this gap.
- **Whether any consumer besides the three found here (`buzz-cli`, Desktop,
  and the declared-but-unconfirmed `buzz-acp`) depends on this crate.** Only
  a repository-wide `Cargo.toml` grep was run; a crate consumed only via a
  workspace-level default-members change or a not-yet-committed branch would
  not have been found.
- **Whether `pack.rs` and `merge.rs`'s missing `//!` module doc comments (in
  contrast to the other four modules) are an intentional omission or a gap**
  was not investigated; both modules are documented here from their public
  function signatures and doc comments on individual items instead.

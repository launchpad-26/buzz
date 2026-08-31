---
id: implementation-crates-buzz-persona
type: implementation
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 76a0a4ebbe4bc4d852b0d04362ed768620da34b3."
    entry_class: FACT
    evidence:
      - "commit 76a0a4ebbe4bc4d852b0d04362ed768620da34b3"
  - statement: "crates/buzz-persona/Cargo.toml describes the crate as 'Parser and loader for Buzz persona pack files (.persona.md)', with no runtime/network dependencies beyond serde, serde_json, serde_yaml and thiserror."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/Cargo.toml"
  - statement: "crates/buzz-persona/src/lib.rs declares exactly six public modules: manifest, merge, pack, persona, resolve, validate — no other module exists in the crate."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/lib.rs"
  - statement: "persona.rs parses one `.persona.md` file (YAML frontmatter between `---` delimiters, followed by a Markdown body that becomes the system prompt) via `parse_persona_md`/`parse_persona_file`/`split_frontmatter`, enforcing a 1 MiB frontmatter cap (MAX_FRONTMATTER_BYTES) and a 256 KiB body cap (MAX_BODY_BYTES)."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/persona.rs:1-27"
      - "crates/buzz-persona/src/persona.rs:200-213"
  - statement: "persona.rs's private `Frontmatter` struct (the one `parse_persona_md` actually deserializes into) carries `#[serde(deny_unknown_fields)]`, so a `.persona.md` file setting an operator-level field such as `idle_timeout`, `max_turn_duration`, `agents`, `heartbeat_interval` or `permission_mode` fails to parse rather than being silently accepted; `tests/integration.rs`'s `operator_config_fields_rejected_in_frontmatter` asserts exactly this for all five field names."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/persona.rs:174-198"
      - "crates/buzz-persona/tests/integration.rs:634-650"
  - statement: "manifest.rs parses the pack-level `.plugin/plugin.json` manifest (`parse_manifest`/`parse_manifest_file`/`PackManifest`), which PERSONA_PACK_SPEC.md describes as a valid Open Plugin Spec (OPS) package with Buzz-specific extensions (`personas`, `defaults`, `pack_instructions`, `hooks_config`, `mcp_config`) alongside the OPS-standard fields."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/manifest.rs:1-14"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:1-26"
  - statement: "merge.rs implements levels 3-5 of a 5-level behavioral-config precedence model, per its own doc comment: (3) per-persona frontmatter wins, (4) pack-level defaults from plugin.json's `defaults` block, (5) hardcoded built-in defaults; levels 1-2 (operator env vars, desktop UI) are explicitly out of this crate's scope and are resolved at runtime by a caller."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/merge.rs:1-8"
  - statement: "pack.rs's `load_pack` loads a full pack directory (manifest, every persona file the manifest lists, optional pack_instructions.md, optional shared .mcp.json) and validates every resolved path stays within the pack root, rejecting path traversal (`PackError::PathTraversal`/`PathEscape`); `PackManifestData` deliberately omits `hooks_config`, with the source comment stating hooks are 'a runtime concern loaded separately by buzz-acp, not a pack-parsing concern.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/pack.rs:1-15"
      - "crates/buzz-persona/src/pack.rs:26-53"
      - "crates/buzz-persona/src/pack.rs:100-124"
  - statement: "resolve.rs's `resolve_pack` is the crate's main entry point: it loads a pack directory, applies merge policy, composes prompts, merges MCP servers and projects environment variables into a `ResolvedPack`/`ResolvedPersona` shaped 1:1 for ACP consumption; its own doc comment states the function is pure (no env access, no network, no side effects)."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:1-11"
      - "crates/buzz-persona/src/resolve.rs:104-113"
  - statement: "`ResolvedPersona.hooks` and `.skills` are populated by resolve.rs but are source-commented as 'reserved for future use, not yet wired' — the crate parses and carries these fields through without any consumer in this repository executing an on_start/on_stop/on_message hook or a skill from them."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:59-63"
  - statement: "`ResolvedMcpServer`'s env/args are passed through as literal strings; resolve_pack's own doc comment states MCP servers are 'merged with literal env passthrough (no `${VAR}` interpolation)' — this crate does not resolve a pack-declared secret-shaped value against any environment or secret store."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/resolve.rs:69-76"
      - "crates/buzz-persona/src/resolve.rs:104-109"
  - statement: "validate.rs's `validate_pack` (the engine behind `buzz pack validate`) delegates all structural checks to `load_pack()` per its own doc comment ('if loading succeeds, the pack is structurally valid by definition'), then runs advisory-only checks — unknown manifest/behavioral keys, naming-convention drift — that are reported as warnings, not hard failures."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/src/validate.rs:1-10"
      - "crates/buzz-persona/src/validate.rs:135-143"
  - statement: "Three crates in this repository declare a Cargo.toml dependency on buzz-persona: buzz-acp (path dependency), buzz-cli (path dependency), and desktop/src-tauri (path dependency aliased `buzz_persona_pkg`)."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml:19-22"
      - "crates/buzz-cli/Cargo.toml:70"
      - "desktop/src-tauri/Cargo.toml:106"
  - statement: "buzz-cli's `crates/buzz-cli/src/commands/pack.rs` is a real, load-bearing consumer: `cmd_validate` calls `buzz_persona::validate::validate_pack`, and `cmd_inspect` calls `buzz_persona::resolve::resolve_pack` and serializes its `ResolvedPack` (with MCP secrets redacted) for `buzz pack validate` / `buzz pack inspect --format json`."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/commands/pack.rs:1-107"
  - statement: "desktop/src-tauri's `src/migration.rs` is a real, load-bearing consumer: `rewrite_legacy_persona_md_runtime` calls `buzz_persona_pkg::persona::split_frontmatter` to rewrite a legacy `runtime: sprout-agent` value to `buzz-agent` in on-disk `.persona.md` files as a one-off migration."
    entry_class: FACT
    evidence:
      - "desktop/src-tauri/src/migration.rs:1124-1134"
  - statement: "Despite buzz-acp's Cargo.toml declaring a direct path dependency on buzz-persona, no source file under crates/buzz-acp/src calls any `buzz_persona::` item; buzz-acp's own persona-related fields (`persona_env_vars` in config.rs, persona-supplied CODEX_CONFIG merging in acp.rs) are computed by buzz-acp's own code, not by calling into this crate's resolve/merge/validate functions. This was checked twice at the same recorded revision (once during initial exploration, once as this node's own re-verification step) with identical results."
    entry_class: FACT
    evidence:
      - "grep(pattern='buzz_persona', path='crates/buzz-acp/src/**', ref='76a0a4ebbe4bc4d852b0d04362ed768620da34b3') -> no matches, exit 1"
      - "crates/buzz-acp/Cargo.toml:19-22"
  - statement: "No file under .github/workflows/ names buzz-persona, and no Justfile recipe invokes `-p buzz-persona`; `just test-unit` (the recipe CI's 'Unit Tests' job runs) enumerates specific crates by name — buzz-core, buzz-auth, buzz-voice, buzz-cli, buzz-db, buzz-conformance, buzz-push-gateway, buzz-backend-kubernetes, buzz-agent, and a filtered slice of buzz-relay — and buzz-persona is not among them."
    entry_class: FACT
    evidence:
      - "Justfile:316-383"
      - ".github/workflows/ci.yml:126-148"
  - statement: "The `test-unit` recipe's own comments state plainly, three times, that 'nothing in CI runs `cargo test --workspace`' and that each crate's tests must therefore be enumerated explicitly to run at all; buzz-persona was not one of the crates given that explicit enumeration, so its test suite — six inline `#[cfg(test)] mod tests` blocks (in manifest.rs, merge.rs, pack.rs, persona.rs, resolve.rs, validate.rs) plus two top-level integration files (tests/integration.rs, 13 tests; tests/e2e_env_flow.rs, 5 tests) — does not execute in any CI job found in this repository."
    entry_class: FACT
    evidence:
      - "Justfile:350"
      - "Justfile:358"
      - "Justfile:366"
      - "crates/buzz-persona/tests/integration.rs"
      - "crates/buzz-persona/tests/e2e_env_flow.rs"
  - statement: "`cargo clippy --workspace --all-targets -- -D warnings` (the `just clippy` recipe CI's 'Rust Lint' job runs) does cover buzz-persona and its test targets, so a test that fails to compile or trips a lint is caught — but `--all-targets` compiles and lints test code without executing any test's assertions, so this is not equivalent to the crate's tests having run."
    entry_class: FACT
    evidence:
      - "Justfile:121-122"
      - ".github/workflows/ci.yml:105-123"
  - statement: "`architecture-containers-agent-runtime` (merged on origin/launchpad) declares that buzz-persona is a direct dependency of buzz-acp resolved harness-side, and links crates/buzz-persona/PERSONA_PACK_SPEC.md as the persona-pack format reference; both underlying facts — the Cargo.toml dependency and the spec file's existence — were independently re-checked at this node's own recorded revision and still hold, so a `part-of` edge toward that container is accurate as of this writing."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md"
      - "crates/buzz-acp/Cargo.toml:19-22"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md"
relationships:
  - type: part-of
    target: architecture-containers-agent-runtime
---

# buzz-persona: implementation reference

`crates/buzz-persona` is a pure, dependency-light Rust library that parses, merges,
validates and resolves Buzz persona pack files (`.plugin/plugin.json` manifests plus
`.persona.md` persona definitions) into an ACP-shaped `ResolvedPack` a harness or CLI can
consume directly. It claims no formal spec, decision or ADR as its target — the closest
thing to one is its own in-tree specification, `PERSONA_PACK_SPEC.md`, which this node
treats as the target it realizes, per *A note on `type`* in the
[implementation-reference template](../../templates/implementation-reference.md): the
crate is the concrete parser/loader implementation of the format that document defines.

## Target

**`crates/buzz-persona/PERSONA_PACK_SPEC.md`** — the persona pack format specification.
It has no corpus node id yet, so this node names it by its real repository path rather
than inventing an `implements` edge to an id that does not exist (per the template's own
rule and `AGENTS.md`'s creation procedure, step 9). The spec states a persona pack is a
superset of the [Open Plugin Spec](https://open-plugin-spec.org): every valid persona
pack is a valid OPS package, and Buzz-specific extensions (`personas`, `defaults`,
`pack_instructions`, `hooks_config`, `mcp_config`) sit alongside the OPS-standard
manifest fields.

## Implementation surface

| Component / file / symbol | Realizes | Note |
|---|---|---|
| `src/manifest.rs` — `parse_manifest`, `parse_manifest_file`, `PackManifest`, `BehavioralDefaults` | Spec §2's `.plugin/plugin.json` manifest, including the OPS-standard fields and the pack-wide `defaults` block | `PackManifest` deserializes with `#[serde(rename_all = "snake_case")]`, no `deny_unknown_fields` at this level (unknown manifest keys are an advisory `validate.rs` warning, not a hard parse error) |
| `src/persona.rs` — `parse_persona_md`, `parse_persona_file`, `split_frontmatter`, `PersonaConfig`, `MAX_FRONTMATTER_BYTES`, `MAX_BODY_BYTES` | Spec's `.persona.md` format: YAML frontmatter + Markdown body as system prompt | The private `Frontmatter` struct it deserializes into carries `deny_unknown_fields` — an operator-level key in a persona file is a hard parse error, not a warning |
| `src/merge.rs` — `merge_behavioral_config`, `resolve_persona_config`, `ResolvedConfig` | Spec's 5-level behavioral-config precedence, levels 3-5 only (persona > pack defaults > built-in defaults) | Levels 1-2 (operator env vars, desktop UI) are out of this module's scope by its own doc comment — resolved by a caller at runtime |
| `src/pack.rs` — `load_pack`, `resolve_skills`, `LoadedPack`, `LoadedPersona`, `PackManifestData` | Spec's whole-pack loading: manifest + every listed persona + optional pack instructions + optional shared `.mcp.json`, with path-traversal rejection | Intentionally does not load `hooks_config` — the source comment attributes hook loading to buzz-acp as a separate runtime concern |
| `src/resolve.rs` — `resolve_pack`, `resolve_loaded_pack`, `resolve_persona_by_name`, `ResolvedPack`, `ResolvedPersona` | Produces the fully resolved, ACP-ready output: merged config, composed prompt, merged MCP servers, projected runtime env vars (e.g. `GOOSE_MODEL`, `BUZZ_AGENT_PROVIDER`) | Pure by design (no env/network access); hooks and skills pass through unexecuted, "reserved for future use, not yet wired" |
| `src/validate.rs` — `validate_pack`, `ValidationReport`, `ValidationDiagnostic` | The engine behind `buzz pack validate`: structural validity by delegation to `load_pack`, plus advisory naming/unknown-key checks | Errors are hard failures (`exit_code() == 1`); advisory findings are warnings (`exit_code() == 2`), never block loading |

## Divergences

- **Declared dependency, no call site.** `buzz-acp`'s `Cargo.toml` declares a direct path
  dependency on `buzz-persona`, and the already-merged
  `architecture-containers-agent-runtime` corpus node cites exactly that dependency as
  evidence that "persona-pack resolution is a harness-side responsibility performed
  before the agent subprocess is prompted." At this node's recorded revision, no source
  file under `crates/buzz-acp/src` actually calls any `buzz_persona::` item — buzz-acp's
  `persona_env_vars` field and its `CODEX_CONFIG` merge logic are computed by buzz-acp's
  own code in `config.rs`/`acp.rs`, not by calling this crate's `resolve`/`merge`
  functions. Whether this is dead dependency weight, a wiring gap mid-migration, or a
  deliberate declaration ahead of an intended future call site was not determined here —
  recorded as a verified fact, not adjudicated, per this task's scope.
- **Hooks and skills parsed but not executed.** `ResolvedPersona.hooks` and `.skills` are
  populated by `resolve_pack`, but the source itself documents both as "reserved for
  future use, not yet wired." No consumer found in this repository executes an
  `on_start`/`on_stop`/`on_message` hook or loads a named skill from these fields.
- **No secret interpolation.** MCP server `env`/`args` are carried through as literal
  strings; a pack author writing a real-looking secret value into either field is passed
  through unresolved, not redacted or interpolated by this crate (redaction, where it
  exists, is `buzz-cli`'s `redact_mcp_secrets`, applied only to JSON-format CLI output —
  not part of this crate).

## Verification

**The honest answer is "not run in CI."** No `.github/workflows/*.yml` file names
buzz-persona, and no Justfile recipe invokes `-p buzz-persona`. `just test-unit` — the
recipe CI's "Unit Tests" job runs — enumerates specific workspace crates by name, and its
own comments state three times that "nothing in CI runs `cargo test --workspace`," so a
crate's tests run only if explicitly listed there. buzz-persona is not listed. Its test
suite — six inline `#[cfg(test)] mod tests` blocks (one per `src/` module) plus two
top-level integration files, `tests/integration.rs` (13 tests) and
`tests/e2e_env_flow.rs` (5 tests) — is real and runnable locally
(`cargo nextest run -p buzz-persona`, not executed as part of authoring this node) but is
not gated on by any CI job found in this repository.

`cargo clippy --workspace --all-targets -- -D warnings` (CI's "Rust Lint" job) does reach
buzz-persona's test code — a test that fails to *compile*, or trips a lint, fails CI — but
`--all-targets` never executes a test's assertions, so a test whose logic silently passes
nothing still ships green.

Representative tests, by what they guard:
- `operator_config_fields_rejected_in_frontmatter` (`tests/integration.rs:634-650`) — the
  ownership-boundary regression: five operator-level field names must fail to parse in a
  persona file.
- `full_pipeline_load_and_validate` / `defaults_merge_persona_overrides` /
  `resolve_full_pipeline` (`tests/integration.rs`) — the load → merge → resolve pipeline
  end to end.
- `resolve_pack_goose_persona_emits_correct_runtime_env_vars` /
  `resolve_pack_buzz_agent_persona_emits_buzz_agent_vars` (`tests/e2e_env_flow.rs`) — the
  per-runtime environment-variable projection introduced in PRs #783/#794, per that file's
  own header comment.

## Relationships

- `part-of`: `architecture-containers-agent-runtime` — buzz-persona is one of the crates
  that container's own corpus node describes, and both underlying facts it cites (the
  buzz-acp Cargo.toml dependency, the `PERSONA_PACK_SPEC.md` link) were independently
  re-verified against this node's own recorded revision.
- No `implements` edge — `PERSONA_PACK_SPEC.md` has no corpus node id of its own yet; see
  *Target* above.
- No `references` edge — no verification/test-strategy corpus node exists yet for this
  crate's test suite to point at.

## Scope and omissions

**This node covers** what `crates/buzz-persona` is responsible for (parsing, merging,
validating and resolving persona pack files into ACP-shaped output), its public
module/function surface, its three declared consumers and which of them actually call
into it, the verified divergence in buzz-acp's dependency, and — found directly rather
than assumed — the gap between this crate having a real test suite and that suite
actually running in CI.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The full persona pack file format and its precedence rules | `crates/buzz-persona/PERSONA_PACK_SPEC.md` |
| How buzz-acp actually computes and consumes persona-derived env vars and `CODEX_CONFIG` merging | A future implementation-reference node for `buzz-acp` (not yet written) |
| buzz-cli's `pack` subcommand surface and its JSON output shape/redaction behavior | A future implementation-reference node for `buzz-cli` (not yet written) |
| Desktop's one-off legacy runtime-rename migration | `desktop/src-tauri/src/migration.rs` itself |
| Whether buzz-acp's declared-but-uncalled dependency is intentional, drift, or scheduled for removal | Unresolved by this node — see *Divergences* |

**Expected but not verified when this node was written:**

- Whether buzz-persona's own test suite currently *passes* at the recorded revision —
  this node establishes that the suite is not run in CI and is real in shape (test
  names, file locations), but authoring it did not include invoking
  `cargo nextest run -p buzz-persona` to confirm green.
- Whether any deployment configuration causes buzz-acp to call into buzz-persona at a
  point not visible to a static source grep (for example, behind a feature flag or a
  build script) — not found, but not exhaustively ruled out.

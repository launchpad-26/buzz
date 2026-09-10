# Plan: issue #1233 — document platforms/agents/persona-runtime.md

## ALREADY TRUE

- Worktree isolated at `__worktrees/task-1233-agents-persona-runtime`, branch
  `task/1233-agents-persona-runtime`, based on `origin/launchpad` at
  `cad6c375fdcc590158c1456c9fc7875f0f84a844`.
- `launchpad/docs/corpus/platforms/agents/persona-runtime.md` confirmed absent
  (`test -f` — not found). No `platforms/` directory exists yet anywhere in
  the corpus on `origin/launchpad`.
- `node.schema.json` and `AGENTS.md` read. No per-type template covers a
  `platforms/agents/*` component node today: `templates/architecture-component.md`
  and `templates/component.md` exist in this checkout but are recently-landed
  and neither is cited by AGENTS.md's own gap table as authoritative yet, and
  their front-matter type choices disagree with each other (`architecture` vs
  `implementation`) and with the issue's own wording. The issue's own Objective
  sentence calls this "the single canonical **architecture component** node,"
  matching the type every existing merged `architecture/**` node already uses
  (`architecture/containers/*.md`, all `type: architecture`, `status: draft`).
  Decision: `type: architecture`, following that live precedent rather than
  either unmerged template.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (merged,
  `id: architecture-containers-agent-runtime`) already states as `FACT` that
  `buzz-persona` is a direct path dependency of `buzz-acp`, resolved
  harness-side, and links `crates/buzz-persona/PERSONA_PACK_SPEC.md`. This
  node is the component-level detail one level below that claim.
- `crates/buzz-persona` fully read: `Cargo.toml`, `src/lib.rs`,
  `src/pack.rs`, `src/resolve.rs`, `src/manifest.rs`, `src/merge.rs`,
  `src/persona.rs`, `src/validate.rs`, `PERSONA_PACK_SPEC.md`,
  `tests/integration.rs`, `tests/e2e_env_flow.rs` (line counts only for the
  last two; full read for everything else).
- Dependents confirmed by grep, not assumed: `buzz-acp` and `buzz-cli`
  declare a Cargo.toml path dependency; `desktop/src-tauri` declares one
  under the renamed package alias `buzz_persona_pkg`. Real symbol usage
  found in `buzz-cli/src/commands/pack.rs` (`validate::validate_pack`,
  `resolve::resolve_pack`, `resolve::ResolvedPack`) and
  `desktop/src-tauri/src/migration.rs`
  (`buzz_persona_pkg::persona::split_frontmatter`). **Surprising, verified
  fact**: `buzz-acp/src` contains zero `buzz_persona::` references anywhere
  despite the Cargo.toml dependency — grepped directly, not inferred. This
  goes in the node as an honest gap, not smoothed over.

## STEP 1 — Front matter

`id: platforms-agents-persona-runtime`, `type: architecture`,
`status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]` (matches the audience set already
used by both unmerged component-style templates). Evidence ledger includes a
commit citation for `cad6c375fdcc590158c1456c9fc7875f0f84a844` as the
provenance entry.

## STEP 2 — Body: responsibility, public interface, dependencies

Responsibility cited to `Cargo.toml`'s `description` field and
`resolve.rs`'s crate-level-equivalent `//!` doc comment (the crate's actual
`lib.rs` carries no `//!`, so the nearest equivalent is used and that
absence is stated, per `AGENTS.md`'s evidence-honesty rule). Public
interface table covers the modules actually read: `pack::load_pack`,
`resolve::resolve_pack`/`resolve_persona_by_name`, `validate::validate_pack`,
`manifest::parse_manifest`, `persona::parse_persona_md`/`split_model`.
Dependencies table split both directions: build-time deps from `Cargo.toml`
(serde/serde_json/serde_yaml/thiserror; dev-dep tempfile), and real
dependents from grep evidence (`buzz-cli`, `desktop/src-tauri` with real
usage; `buzz-acp` with a declared-but-apparently-unused dependency, stated
as found, not explained away).

## STEP 3 — Boundary and relationships

Boundary paragraph: this node covers the `buzz-persona` crate only, not the
full persona-pack authoring workflow (`PERSONA_PACK_SPEC.md` owns that), not
`buzz-acp`'s own prompt-assembly/dispatch behavior, and not the
container-level agent-runtime decomposition (owned by the merged
`architecture-containers-agent-runtime` node). No `relationships` entry:
`buzz-persona` is consumed by three different containers
(agent-runtime via `buzz-acp`, `cli`, `desktop`) at the recorded revision, so
a single `part-of` edge toward any one of them would misstate it as scoped
to that container alone. No sibling `platforms/agents/*` node exists yet on
`origin/launchpad` to `depends-on`/`references` either (checked directly with
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, not
assumed). This mirrors the precedent the merged `agent-runtime.md` node
itself already sets for the same reason.

## STEP 4 — Validate and gate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root; fix anything it flags. Then, as two separate tool calls per the task
instructions: the corpus unittest discovery run, then `git add` + signed
commit.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether `buzz-acp`'s declared-but-apparently-unused `buzz-persona`
  dependency is dead weight or mid-flight integration work is not resolved
  here — stated as a verified gap in the node's own Scope and omissions,
  not investigated further (out of this task's scope per the issue's own
  "no runtime product behavior changes" boundary).

## LEFT OUT

- The five sibling `platforms/agents/*.md` tasks (`#1229` acp-harness,
  `#1230` buzz-agent, `#1231` dev-mcp, `#1232` kubernetes-backend, `#1234`
  sprig) — separate issues, separate nodes, not folded in here.
- Full persona-pack authoring/spec content (`PERSONA_PACK_SPEC.md` already
  owns that canonically; this node cites it rather than restating it).
- Any `relationships` edges, per Step 3 above.

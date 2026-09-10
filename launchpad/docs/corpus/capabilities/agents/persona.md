---
id: capabilities-agents-persona
type: capabilities
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 131b02f989684117d9ab1dd426f1673fa638e523."
    entry_class: FACT
    evidence:
      - "commit 131b02f989684117d9ab1dd426f1673fa638e523"
  - statement: "VISION.md's own Status table marks 'Agent personas and teams — desktop-managed, built-in defaults, operator-defined' with a shipped (✅) marker, and its 'Agent Personas & Teams' section states: 'A persona bundles a model and a system prompt. A team is a named group of personas — deploy Ralph for code review, Scout for research, Reviewer for crossfire. Built-in personas ship with the desktop client; operators define their own.'"
    entry_class: FACT
    evidence:
      - "VISION.md:167-169"
      - "VISION.md:228"
  - statement: "A Persona Pack is defined as 'a portable, self-contained bundle that defines one or more AI agent personas for deployment in Buzz,' containing personas (identity + system prompt), skills, MCP server config, pack-level instructions, lifecycle hooks, and distribution metadata; it is stated as a superset of the Open Plugin Spec (every valid Persona Pack is also a valid OPS package)."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:1-10"
  - statement: "A persona file (`.persona.md`) is markdown with YAML front matter: identity fields (name, display_name, avatar, description), skills, per-persona mcp_servers, behavioral config (subscribe, triggers, model, temperature, max_context_tokens, thread_replies, broadcast_replies), and harness-managed hooks; the markdown body after the closing `---` is the persona's system-prompt text."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:143-220"
  - statement: "Pack-wide defaults (model, temperature, max_context_tokens, triggers, subscribe, thread_replies, broadcast_replies) live in the pack manifest's `defaults` object and are overridden per-persona; the full precedence order buzz-acp applies at deploy time, highest first, is: operator env vars, Desktop UI per-agent overrides, per-persona frontmatter, pack-level defaults, then buzz-acp's built-in defaults."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:574-653"
  - statement: "The buzz-persona crate (Cargo.toml description: 'Parser and loader for Buzz persona pack files (.persona.md)') exposes manifest, merge, pack, persona, resolve and validate modules, and buzz-cli's `buzz pack validate <path>` and `buzz pack inspect <path> [--format human|json]` subcommands call `buzz_persona::validate::validate_pack` and `buzz_persona::resolve::resolve_pack` directly to check and preview a pack's fully resolved, effective per-persona configuration before deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/Cargo.toml:1-5"
      - "crates/buzz-persona/src/lib.rs:1-6"
      - "crates/buzz-cli/src/commands/pack.rs:16-47"
      - "crates/buzz-cli/src/commands/pack.rs:87-98"
      - "crates/buzz-cli/src/lib.rs:1882-1918"
  - statement: "`buzz-acp` depends on `buzz-persona` as a path dependency in its own Cargo.toml, but a repository-wide search of `crates/buzz-acp/src/` finds no `buzz_persona::` call sites — persona-pack resolution reaches buzz-acp's actual runtime config not through an in-process crate call, but through `buzz pack inspect --format json`'s output, which a separate, launchpad-specific projector script maps onto the CLI flags/env vars buzz-acp's own Config already reads (for example `system_prompt`, `team_instructions`) — a gap this node names explicitly in Boundary below rather than assuming the Cargo.toml dependency alone proves in-process wiring."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/Cargo.toml:22"
      - "grep('buzz_persona::', path='crates/buzz-acp/src/**/*.rs') -> no matches"
      - "launchpad/agents/project-pack.py:1-20"
      - "crates/buzz-acp/src/config.rs:1094-1146"
  - statement: "Three concrete parts of the pack spec are stated as designed but not yet implemented at authoring time: (1) the persona prompt is currently delivered as a `[System]`-prefixed block in the user message on every turn rather than injected once at session creation; (2) skill path resolution to a `SKILL.md`'s `name:` field and runtime copying into `$AGENT_CWD/.agents/skills/` is planned for a future release, not yet built; (3) `${VAR_NAME}` interpolation in `mcp_servers[].env` is planned but not yet implemented — values are passed through as literal strings today; and (4) lifecycle hooks (`on_start`/`on_stop`/`on_message`) are parsed and validated at pack load time but not yet executed by any harness."
    entry_class: FACT
    evidence:
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:149"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:312-314"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:476-478"
      - "crates/buzz-persona/PERSONA_PACK_SPEC.md:510-511"
  - statement: "The merged architecture node `architecture-containers-agent-runtime` already states that `buzz-acp` depends on `buzz-persona` directly while `buzz-agent`'s Cargo.toml carries no such dependency, so 'persona-pack resolution is a harness-side responsibility performed before the agent subprocess is prompted, not something the agent process does itself,' and links `PERSONA_PACK_SPEC.md` as the persona-pack format and merge-rules reference — this capability node references that architecture node rather than re-describing its content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:46"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:279"
      - "launchpad/docs/corpus/architecture/containers/agent-runtime.md:298"
  - statement: "No `interfaces-events` corpus node currently merged on origin/launchpad documents `buzz-cli`'s `pack` subcommand group (or any CLI surface at all), and no `capabilities/` directory of any kind existed on origin/launchpad before this node — checked via `git ls-tree -r origin/launchpad -- launchpad/docs/corpus/` at the recorded revision, which lists only `architecture/` and `standards/` subtrees plus the top-level AGENTS.md/README.md — so this node declares no `references` edge toward an interface node for the pack CLI, since none exists yet to reference."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, architecture/**, schema/**, standards/**, templates/**, at commit 131b02f989684117d9ab1dd426f1673fa638e523"
relationships:
  - type: part-of
    target: capabilities-agents-agent
  - type: references
    target: architecture-containers-agent-runtime
  - type: implements
    target: corpus-template-capability
---

# Agent personas: capability

Buzz lets an operator define **agent personas** — named AI agents with a distinct
identity, system prompt, model choice, and channel-participation rules — and deploy
them as a **team** through a portable, self-contained bundle called a persona pack.
Because this capability exists, an operator can stand up several differently-behaved
agents (for example a security reviewer, a researcher, and a crossfire reviewer) from
one pack, override any agent's model or behavior individually, and validate or inspect
a pack's fully resolved configuration before deploying it — without hand-writing
per-agent harness configuration from scratch.

A persona pack is a superset of the Open Plugin Spec: every valid persona pack is
also a valid OPS package, so OPS-compatible tooling can discover and inspect Buzz
persona packs, ignoring the Buzz-specific extensions (`personas`, `defaults`,
`pack_instructions`, `mcp_config`, `hooks_config`) it doesn't understand. A pack
bundles one or more `.persona.md` files (identity, system prompt, behavioral config),
optional shared skills and MCP server config, optional pack-level instructions and
lifecycle hooks, and OPS distribution metadata.

## Maturity

**Shipped.** VISION.md's own Status table marks "Agent personas and teams —
desktop-managed, built-in defaults, operator-defined" as shipped, and its "Agent
Personas & Teams" section describes the same capability in product terms: a persona
bundles a model and a system prompt, and a team is a named group of personas. The
`buzz-persona` crate parses, merges, resolves and validates pack and persona files,
and `buzz-cli`'s `pack validate` and `pack inspect` subcommands expose that machinery
directly to an operator today.

**Shipped with named gaps.** The pack spec itself is explicit that four pieces of the
design are not yet built: the persona's system prompt is currently re-delivered as a
`[System]`-prefixed block on every turn rather than injected once at session start;
declared skills are not yet resolved to their `SKILL.md` `name:` field or copied into
an agent's working directory at runtime; `${VAR_NAME}` interpolation inside a
persona's `mcp_servers[].env` is not yet implemented (values pass through as literal
strings); and lifecycle hooks are parsed and validated at load time but never
executed. None of these gaps block deploying a pack — they scope what "shipped"
currently means for this capability, and a maturity claim for any one of them
individually should cite the spec section above, not this summary.

**How resolution reaches the running agent is a harness-side responsibility, not
proven in-process wiring.** `buzz-acp` (the harness that spawns and prompts agent
processes) depends on `buzz-persona` in its own `Cargo.toml`, but no `buzz_persona::`
call site exists anywhere in `buzz-acp`'s source. The path from a resolved pack to a
running agent's actual config today is: `buzz pack inspect --format json` emits the
fully resolved per-persona configuration, and a separate, launchpad-specific
projector script maps that JSON onto the CLI flags and environment variables
`buzz-acp`'s own `Config` already reads (`system_prompt`, `team_instructions`, and
related fields) at process spawn time. This node states that fact rather than
assuming the Cargo.toml dependency alone proves the wiring is direct.

## Boundary

This node does not describe:
- **How it is built.** The container-level architecture — that `buzz-acp` depends on
  `buzz-persona` directly while `buzz-agent` does not, and that persona-pack
  resolution is therefore a harness-side responsibility — is documented by
  `architecture-containers-agent-runtime`, referenced below, not repeated here.
- **The interface(s) it is exposed through.** `buzz-cli`'s `pack validate` and
  `pack inspect` subcommands are the operator-facing surface for this capability, but
  no interface-type corpus node yet exists to name as their canonical documentation —
  this is a real gap, not an omission by choice; see Scope and omissions.
- **The step-by-step flow through it.** How a pack is authored, validated, resolved,
  projected into harness config, and ultimately shapes one agent turn is a flow-level
  narrative, not a capability-level one; no flow node for this exists yet.
- **How it is operated day to day** (deploying, rotating, or retiring a running
  persona-backed agent) — that is the `operations` corpus surface's territory, not
  this node's.

## Relationships

- references: `architecture-containers-agent-runtime` — the container-level
  documentation of how `buzz-acp`, `buzz-agent`, `buzz-dev-mcp` and `buzz-persona`
  relate, including the specific dependency fact this node's Maturity section builds
  on.
- implements: `corpus-template-capability` — this node is drafted from that template's
  required-sections skeleton (Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions).

## Scope and omissions

**This node covers** what the agent-persona capability lets an operator and a
deployed agent do: define one or more named personas with distinct identity, system
prompt, model and behavioral configuration in a portable OPS-compatible pack;
override pack-wide defaults per persona; and validate or inspect a pack's fully
resolved configuration before deployment. It also states, with citations, which
parts of that design are shipped versus explicitly planned-but-not-built, and names
the one confirmed gap between a Cargo.toml dependency and actual in-process wiring.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Container-level architecture of the agent runtime and buzz-persona's place in it | `architecture-containers-agent-runtime` |
| The `buzz-cli` `pack` command surface as a documented interface | no interface node exists yet — a gap, not a choice |
| The step-by-step flow from pack authoring through one agent turn | no flow node exists yet — a gap, not a choice |
| Day-to-day operation of persona-backed deployed agents | the `operations` corpus surface |
| The pack/persona file format itself, field by field | `crates/buzz-persona/PERSONA_PACK_SPEC.md` |

**Expected but not verified when this node was written:**
- **The launchpad-specific projector script (`launchpad/agents/project-pack.py`) was
  read only far enough to confirm its stated purpose and inputs/outputs** (it calls
  `buzz pack inspect --format json` and emits env vars for `buzz-acp` and the agent
  runtime); its full behavior, and whether it is the only such projector in use, was
  not exhaustively verified.
- **Whether any deployment today actually exercises the full pack pipeline
  end-to-end** (author a pack, validate it, resolve it, project it into a running
  `buzz-acp` process) was not directly observed — the claim above is built from
  reading the code and script headers describing that pipeline, not from watching
  a live deployment.
- **The discrepancy between `PERSONA_PACK_SPEC.md`'s own `[System]` layer name and
  the `[Agent Instructions]` section header found in `buzz-acp`'s test fixtures** was
  noticed but deliberately left unexamined here — that is architecture-level detail
  for `architecture-containers-agent-runtime` or a flow node to resolve, not this
  capability node's concern.

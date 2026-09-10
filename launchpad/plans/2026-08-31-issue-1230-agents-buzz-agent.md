# Plan: issue #1230 — platforms/agents/buzz-agent corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/agents/buzz-agent.md` does not exist yet (confirmed with `test -f`).
- `launchpad/docs/corpus/templates/component.md` (merged on `origin/launchpad`) is the fitting
  template: one software component, standing alone, `type: implementation`, sections
  Responsibility / Public interface / Dependencies / Boundary / Relationships / Scope and
  omissions. It explicitly is not the architecture-component (container decomposition)
  template and not a crate README replacement.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
  `architecture-containers-agent-runtime`, `type: architecture`, merged on `origin/launchpad`)
  already documents the container `buzz-agent` sits inside, names `buzz-agent` as one of its
  three crates, and explicitly excludes "the agent's exact LLM-provider selection and
  model-capability logic" and "agent loop, security model, size limits" — pointing at
  `crates/buzz-agent/src/model_capabilities.rs`, `src/catalog.rs` and
  `crates/buzz-agent/README.md` as the deeper detail. This is exactly this task's subject, and
  it is a valid `part-of` relationship target (confirmed present in
  `git ls-tree origin/launchpad`).
- `crates/buzz-agent/src/lib.rs` carries no crate-level `//!` doc comment. The nearest
  equivalent responsibility statement is `crates/buzz-agent/README.md`'s opening lines and the
  `description` field in `crates/buzz-agent/Cargo.toml`.
- `buzz-agent` has zero internal Buzz-crate dependencies (Cargo.toml lists only external
  crates: tokio, serde(_json/_yaml), reqwest, rmcp, arc-swap, getrandom, tracing(-subscriber),
  async-trait, axum, base64, hex, sha2, url, urlencoding, webbrowser, dirs, nix). Only
  `crates/sprig/Cargo.toml` depends on it internally (`buzz-agent = { path = "../buzz-agent" }`).

## STEP 1 — Draft front matter

`id: platforms-agents-buzz-agent`, `type: implementation` (per `templates/component.md`'s own
reasoning for a component-scale node), `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`, one commit-citation FACT for provenance, plus one
evidence entry per substantive claim in the body (crate-level doc-comment absence, public
interface rows, dependency rows in both directions, security/config facts from the README).
`relationships: [{type: part-of, target: architecture-containers-agent-runtime}]` — confirmed
resolvable in `origin/launchpad`'s corpus tree.

## STEP 2 — Write the body against `templates/component.md`'s required sections

Purpose/scope paragraph; Responsibility (cited to README + Cargo.toml description, noting the
absent `//!` comment); Public interface table (`run`, `authenticate_databricks`, `Provider`,
`AgentError`, `ModelEntry`/`discover_databricks_models`, `Config::from_env`, `auth::TokenSource`
+ PKCE types, `model_capabilities::resolve`, plus the `buzz-agent` ACP-over-stdio binary
surface); Dependencies both directions (Cargo.toml citations); Boundary (not
architecture-component, not implementation-reference, not a second README); Relationships;
Scope and omissions (naming what is left to `crates/buzz-agent/README.md`,
`docs/MCP_DRIVEN_HOOKS.md`, and the container node).

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root; fix any
reported errors.

## STEP 4 — Earn the commit gate

Run the corpus unittest suite as its own command, confirm `OK`, then commit in a second,
separate command.

## STEP 5 — Verify

Re-read the diff against issue #1230's Definition of Done line by line; re-open every cited
file/line; confirm exactly one new hand-authored file plus this plan; re-run validate.py.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.

## OPEN

- Whether `architecture-containers-agent-runtime`'s "Technology" table counts as the
  "architecture-component node's building-block table" the component template's `part-of`
  guidance literally names, since no dedicated `architecture-component` instance node exists
  yet for this container. Read as the closest available fit: `buzz-agent` is a documented row
  of that container node's own decomposition table, and the target id demonstrably resolves.
- No node has yet been authored from `templates/component.md`; this is the first, so the
  template's own required-sections/evidence-expectations shape is being tested here for real
  rather than merely quoted.

## LEFT OUT

- Any second concept (e.g. a dedicated node for `docs/MCP_DRIVEN_HOOKS.md`'s hook-tool
  contract, or for the ACP wire protocol itself) — those stay separate tasks per `AGENTS.md`'s
  one-node-one-idea rule.
- Editing `architecture/containers/agent-runtime.md` — out of scope per issue #1230's own
  "Out of scope" list (no second hand-authored canonical document).
- Restating `crates/buzz-agent/README.md`'s install/usage/configuration content — cited, not
  duplicated, per the component template's Boundary section.

# Plan: issue #811 — document capabilities/projects/project-repository.md

## ALREADY TRUE

- `launchpad/docs/corpus/templates/capability.md` is merged on `origin/launchpad` and
  defines the required body shape (`type: capabilities`) for this node.
- No `launchpad/docs/corpus/capabilities/**` node exists yet on `origin/launchpad`, so
  siblings #809 (branch-as-room), #810 (project-channel) and #812 (project capability)
  are not merged and cannot be `relationships` targets.
- The target file `launchpad/docs/corpus/capabilities/projects/project-repository.md`
  does not exist (confirmed by `test -f`).
- The binding is `kind:30621` (NIP-MP, `crates/buzz-core/src/kind.rs:632`), which
  groups `kind:30617` NIP-34 repository announcements via `a` tag coordinates
  (`30617:<owner-hex>:<repo-d>`), documented in full at `docs/nips/NIP-MP.md`.
- `buzz-cli`'s `buzz projects` command group implements the write path:
  `add-repo` / `remove-repo` (`crates/buzz-cli/src/commands/projects.rs:510,522`),
  coordinate parsing (`crates/buzz-sdk/src/builders.rs:2001` `ProjectMemberCoord`),
  and relay ingest validation (`crates/buzz-relay/src/handlers/ingest.rs:1609`
  `validate_project_envelope`). E2E coverage exists in
  `crates/buzz-test-client/tests/e2e_project.rs`.
- `VISION_PROJECTS.md`'s own status table (lines 254-255) marks "Project binding" and
  "Multi-repo projects" as "📋 Designed", not "✅ Ships today" — this is the product-level
  maturity marker even though the underlying code and tests exist and pass.

## STEP 1 — Draft the node

Hand-author front matter against `node.schema.json`:
- `id: capabilities-projects-project-repository`
- `type: capabilities`
- `status: draft`
- `origin: launchpad`
- `audiences: [agent, developer, reviewer]`
- `evidence`: provenance FACT (commit `cad6c375fdcc590158c1456c9fc7875f0f84a844`) plus
  one FACT per substantive claim (kind number, tag grammar, CLI commands, ingest
  validation, maturity marker).
- No `relationships` (nothing to target on `origin/launchpad`).

Body follows the capability template's required sections: Capability statement,
Maturity, Boundary, Relationships (declared: none, with reasoning), Scope and
omissions.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Confirm exit 0 and that the only prior FAIL entries are the 21 pre-existing ones
tracked in #1951 — zero new FAILs from this node.

## STEP 3 — Earn the commit gate and commit

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then `git add` the new doc + this plan and `git commit -s`.

## GATES

- `validate.py` exits 0, zero new FAIL entries vs. the #1951 baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` prints `OK`.

## BUDGET

Single file plus this plan. No code changes.

## OPEN

- Whether `status: draft` or `active` is more appropriate — chosen `draft` since this
  is the first node in `capabilities/` and no review pass has happened yet.

## LEFT OUT

- Documenting `#809` (branch-as-room), `#810` (project-channel) or `#812` (project,
  overall capability) — separate tasks, separate nodes.
- Any relationship edges — no capability/interface/architecture node exists yet on
  `origin/launchpad` to point at.

# Plan: issue #812 — document capabilities/projects/project.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/projects/project.md` does not exist (confirmed).
- `launchpad/docs/corpus/templates/capability.md` exists and defines the required
  body sections (capability statement, maturity, boundary, relationships, scope
  and omissions) for `type: capabilities` nodes.
- `node.schema.json`'s `type` enum uses `capabilities` (plural), not `capability`.
- NIP-MP (`docs/nips/NIP-MP.md`) specifies `kind:30621`, the addressable "project"
  event: a named, signer-owned grouping of `kind:30617` repository announcements,
  with no authority over members.
- The capability is shipped, not merely designed, contrary to
  `VISION_PROJECTS.md`'s own status table (`📋 Designed`, line 255): relay ingest
  validates the envelope (`crates/buzz-relay/src/handlers/ingest.rs`,
  `validate_project_envelope`, with a fixture-backed unit test suite), `buzz-sdk`
  builds the event (`crates/buzz-sdk/src/builders.rs`), `buzz-cli` exposes a full
  `projects` subcommand group (`crates/buzz-cli/src/lib.rs` `ProjectsCmd`,
  `crates/buzz-cli/src/commands/projects.rs`), and the desktop app has a whole
  `desktop/src/features/projects/` module (creation, deletion, membership,
  ownership, sidebar). Per `AGENTS.md`'s evidence rule, executable evidence
  outranks a stale VISION status line for "how the system currently behaves."
- Siblings #809 (branch-as-room), #810 (project-channel), #811
  (project-repository) are open, unmerged, so no `relationships` may target
  them — none exist as corpus node ids on `origin/launchpad`.
- Corpus tree on `origin/launchpad` currently holds only meta/governance nodes
  (`AGENTS.md`, `README.md`, `standards/*`, `architecture/*`, `templates/*`) —
  no capability-shaped node to `references` yet, so this node also declares no
  `relationships`.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/projects/project.md` following
`templates/capability.md`'s skeleton:
- Front matter: `id: capabilities-projects-project`, `type: capabilities`,
  `status: draft`, `origin: upstream` (this documents a block/buzz product
  capability, not launchpad-cohort process), `audiences: [agent, developer,
  reviewer]`, no `relationships`.
- Body: capability statement (multi-repo grouping via kind:30621), maturity
  (shipped — cite relay ingest validation, sdk builder, cli, desktop feature
  dir), boundary (excludes branch-as-room, project-channel binding mechanics,
  project-repository attach/detach mechanics, architecture/interface/flow,
  operations — named as siblings #809-#811 without linking, since unmerged),
  relationships section stating none declared and why, scope-and-omissions.
- Evidence: FACT entries citing `docs/nips/NIP-MP.md` (bare path, spot lines
  for specific claims), `crates/buzz-core/src/kind.rs:632`,
  `crates/buzz-relay/src/handlers/ingest.rs` (validate_project_envelope + its
  tests), `crates/buzz-sdk/src/builders.rs`, `crates/buzz-cli/src/lib.rs` /
  `commands/projects.rs`, `desktop/src/features/projects/*`, plus a commit
  citation for provenance. One TEAM_KNOWLEDGE-style note is not needed here —
  all claims are code/spec-backed FACTs; no INFERENCE or TEAM_KNOWLEDGE
  entries are anticipated but may be added if a claim needs them.

**Done when:** file exists, schema-shaped, every claim has an evidence entry.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root. Confirm zero new FAIL entries beyond the 21 pre-existing ones tracked in
#1951.

**Done when:** validator output shows no new FAIL rows attributable to the
new file.

## STEP 3 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then `git add` the new doc + this plan, and
`git commit -s -m "docs(corpus): document capabilities/projects/project (#812)"`.

**Done when:** commit created locally, gate output confirms `OK` before commit.

## STEP 4 — Self-review

Re-read the diff against issue #812's DoD checklist line by line; re-open every
cited source; confirm no second canonical document was created; confirm no new
validate.py FAIL entries; note that review-code/review-adjudicate were not run
(deferred per batch mode).

**Done when:** each DoD bullet is checked off against the actual diff.

## PARALLEL

None — single file, single commit, no independent work streams.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with no
  new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  prints `OK`, run alone, before commit.

## BUDGET

Single node, ~5 evidence-backed sections. No code changes. One commit, no PR.

## OPEN

- Whether `origin: upstream` vs `origin: launchpad` is the better call for a
  capability node describing product behavior authored/reviewed inside the
  launchpad fork — resolved here as `upstream` because the capability itself
  (NIP-MP, kind:30621) is block/buzz product behavior, not launchpad cohort
  process, matching ADR-0003's per-claim origin vocabulary.

## LEFT OUT

- No `relationships` entries (nothing mergeable to point at yet).
- No edits to VISION_PROJECTS.md's stale status marker — out of scope per
  issue #812's own "Out of scope: changing runtime product behavior... unless
  a separately linked implementation issue owns that change" and this is a
  docs-status discrepancy, not runtime behavior; flagging it in the new node's
  evidence is enough.
- No second corpus document for branch-as-room, project-channel, or
  project-repository — those are #809/#810/#811's own tasks.

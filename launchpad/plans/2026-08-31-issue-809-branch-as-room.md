# Plan: issue #809 — document capabilities/projects/branch-as-room.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad` — this
  is the first node under `capabilities/`.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`) is
  merged on `origin/launchpad` and defines the required body shape: Capability
  statement, Maturity, Boundary, Relationships, Scope and omissions.
- VISION_PROJECTS.md's "Branches as Channels" section (lines 77-97) describes the
  intended design: creating a branch creates a channel; patches, CI, review and merge
  live there; the channel archives on merge.
- VISION_PROJECTS.md's own Status table (lines 245-259) marks "Project binding
  (kind:30617 + `buzz-` tags)" as "📋 Designed", not shipped — the mechanism the
  branch-channel vision depends on.
- The actual codebase implements exactly one channel bound to an entire repository
  (a single `buzz-channel` tag on the kind:30617 announcement, resolved by
  `resolve_repo_binding` in `crates/buzz-relay/src/api/git/binding.rs`), not one
  channel per branch. Desktop's `projectBranchErrors.ts` and
  `projectRepositoryCreation.ts` both operate on this repo-level binding.
- No non-test call site creates a channel triggered by a branch create/push operation
  (grepped `create_channel`/`create_channel_with_id` across `crates/`); channel
  creation is generic NIP-29 `create_group` handling
  (`crates/buzz-relay/src/handlers/side_effects.rs::handle_create_group`) and
  h-tag pre-creation in `ingest.rs`, neither branch-specific.
- `launchpad/docs/corpus/architecture/flows/git-push.md` (id
  `architecture-flows-git-push`) is already merged and documents this same
  repo-level channel-binding authorization model — a valid `references` target.
- Git history shows no removed/prior implementation of per-branch channel creation;
  "channel-first" branches found in history are about the repo-level project-channel
  binding, consistent with the above.

## STEP 1 — Confirm target path is free and gather remaining line citations

Confirm `launchpad/docs/corpus/capabilities/projects/branch-as-room.md` does not
exist. Pin exact line numbers for: `binding.rs` RepoBinding enum,
`projectBranchErrors.ts` token/copy, `projectRepositoryCreation.ts`
`buildRepositoryChannelBindingTemplate`. Done-when: citation list finalized, all
bare-path (no `#symbol=`/`#line=` fragments).

## STEP 2 — Draft the node

Write the capability node with front matter (`id:
capabilities-projects-branch-as-room`, `type: capabilities`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`) and body per the
template skeleton: Capability statement (the vision), Maturity (designed, not
shipped — cited), Boundary (not architecture/interface/flow/operations, and
explicitly not the already-implemented repo-level channel binding), Relationships
(`references: architecture-flows-git-push`, optional `implements:
corpus-template-capability`), Scope and omissions. Classify the "no per-branch
creation code exists" claim as `INFERENCE` (absence reasoned from an exhaustive
grep), not `FACT`. Done-when: file written, no fabricated behavior.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Done-when: exit 0, and the new node adds zero new FAIL entries versus the known
21-error baseline (issue #1951).

## STEP 4 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then `git add` the new node + this plan file and commit with
`git commit -s`. Done-when: commit created, no push, no PR.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `unittest discover` on `launchpad/project-intelligence/corpus/tests` prints `OK`.
- Exactly one hand-authored file added (plus this plan).

## BUDGET

Single node, ~1 sitting. No sub-agents.

## OPEN

- Whether a GitHub issue/roadmap item formally tracks future implementation of
  per-branch channel automation was not exhaustively searched — noted as an
  unverified gap in the node's own Scope and omissions rather than left silent.

## LEFT OUT

- Any edits to `projects/project-channel.md`, `projects/project-repository.md`, or
  the overall `projects/project.md` capability node — siblings #810/#811/#812,
  out of scope for #809 and not yet merged, so not valid relationship targets here.
- Any runtime code change implementing per-branch channels — out of scope per
  issue #809's own "Out of scope" section.

# Issue #798: document capabilities/onboarding/first-identity.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/onboarding/first-identity.md` does not exist
  (confirmed: `launchpad/docs/corpus/capabilities/` has no tree at all on
  `origin/launchpad` at revision `cad6c375fdcc590158c1456c9fc7875f0f84a844`).
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`)
  defines the required body shape: Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions.
- `node.schema.json` requires `id`, `type`, `status`, `origin`, `audiences`,
  `evidence`; `type` must be one of its 13 enum values (`capabilities` fits).
- Desktop's identity flow is implemented and tested:
  `desktop/src-tauri/src/app_state.rs` (`build_app_state`,
  `resolve_persisted_identity`, `load_or_create_identity`,
  `resolve_identity_with_store`, `generate_and_persist`) and
  `desktop/src-tauri/src/commands/identity.rs` (`import_identity`,
  `commit_imported_identity`, `persist_current_identity`, `sign_out`).
- Sibling nodes `capabilities/onboarding/{first-channel,first-community,onboarding}.md`
  (#796/#797/#799) are separate, not-yet-merged tasks — no `relationships` target
  them. `architecture-containers-desktop` and `architecture-containers-mobile`
  are already merged and are valid `references` targets.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/onboarding/first-identity.md` following
the capability template: front matter (`id: capabilities-onboarding-first-identity`,
`type: capabilities`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`), Capability statement, Maturity
(shipped, cited to `app_state.rs`/`identity.rs`/tests), Boundary (not backup,
not device pairing itself, not profile/avatar/community steps), Relationships
(`references` the two merged architecture container nodes), Scope and omissions.
Evidence entries use `path:line` or `path:start-end` citations only.

**Done when:** file exists, front matter is schema-shaped, every FACT has a
real citation re-opened and confirmed correct.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree. Confirm the new node produces zero new FAIL entries (21 pre-existing
FAILs on `origin/launchpad`, tracked in #1951, are expected and unrelated).

**Done when:** validator output shows no new FAIL referencing this file.

## STEP 3 — Earn the commit gate

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`.

**Done when:** test run prints `OK`.

## STEP 4 — Commit

`git add` the new corpus file and this plan file; `git commit -s` with message
`docs(corpus): document capabilities/onboarding/first-identity (#798)`.

**Done when:** commit exists on `task/798-first-identity`, nothing pushed.

## STEP 5 — Self-review

Re-read the diff against #798's DoD line by line; re-open every cited source;
confirm no second canonical document was created; confirm validate.py shows
zero new FAILs; note `review-code`/`review-adjudicate` were skipped (batch
mode) and this is a self-review substitute.

**Done when:** self-review notes are ready to report.

## GATES

- `validate.py` — zero new FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — must print `OK` before commit.

## BUDGET

Single file, ~1 sitting. No sub-agents.

## OPEN

- Whether a future `capabilities-onboarding-onboarding` node (#799) will want
  a `part-of` edge from this node once merged — left for that node's own
  authoring pass, per the template's guidance not to declare edges to
  unmerged siblings.

## LEFT OUT

- Backup/recovery mechanics (NIP-49 `ncryptsec`, keyring migration internals)
  — implementation detail of the identity capability, not restated here beyond
  what establishes maturity.
- Device pairing protocol details (NIP-AB) — mobile's own identity-acquisition
  path is noted as a boundary, not documented here.

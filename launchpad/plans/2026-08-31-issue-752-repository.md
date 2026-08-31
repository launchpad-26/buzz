# Plan: issue #752 — document capabilities/git/repository.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad` (no
  `capabilities/git/*` siblings are merged: #745 git-hosting, #750
  repository-announcement, and this task are all unmerged in parallel).
- `node.schema.json`'s `type` enum has 13 members and **no `data-entity` value**.
  The corpus's own `templates/data-entity.md` states a real data-entity instance
  "most plausibly takes `type: implementation`," never `type: capabilities` and
  never an invented `data-entity` value.
- Issue #752's own DoD tail is the generic **capability** boilerplate ("States the
  capability and primary actors/outcomes... Links verification demonstrating the
  capability"), not the data-entity template's identity/attributes/invariants
  shape. Per the task's own instruction to ground the type in what the DoD asks
  for, this settles `type: capabilities`.
- `crates/buzz-db/src/store/git_repo.rs` (`reserve_repo_name`, `repo_name_owner`,
  `count_repos_for_owner`, `release_repo_name`) is the repository name/ownership
  registry; `crates/buzz-relay/src/handlers/side_effects.rs`
  (`handle_git_repo_announcement_inner`) is the kind:30617 handler that drives it;
  `migrations/0002_git_repo_names.sql` is the backing table.
- No relationships are available: no sibling corpus node exists in
  `origin/launchpad`'s corpus tree to point at.

## STEP 1 — Write `launchpad/docs/corpus/capabilities/git/repository.md`

Front matter: `id: capabilities-git-repository`, `type: capabilities`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
no `relationships`. Body follows the capability template shape (capability
statement / maturity / boundary / scope-and-omissions), scoped to repository
**identity, naming and ownership** — distinct from git-hosting's storage/transport
mechanics (#745) and repository-announcement's event/tag wire shape (#750).

Done when: file exists, front matter is schema-legal, every claim has an
evidence entry classed honestly.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root. Done when it exits 0 with zero new FAIL entries beyond the
tracked 21-error baseline (#1951).

## STEP 3 — Earn the commit gate

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as the sole command in its own tool call. Done when `OK`.

## STEP 4 — Commit

`git add` the new node + this plan file; `git commit -s`. Done when the commit
exists on `task/752-repository`. No push, no PR.

## GATES

- `validate.py` exit 0, zero new FAIL entries.
- `unittest discover` on corpus tests: OK.

## BUDGET

Single pass, no iteration expected — this is one small, evidence-backed node.

## OPEN

- Whether "repository identity/naming/ownership" deserves its own capability
  distinct from "Git hosting" in VISION_PROJECTS.md's status table (which lists
  only one "Git hosting" row) is not settled anywhere; this node states that as
  an explicit, cited inference rather than asserting independent product status.

## LEFT OUT

- Storage/transport mechanics (object storage, manifest pointer CAS) — #745.
- The kind:30617/30618 wire shape (tags, content, protection rules, channel
  binding) — #750.
- Any step-by-step flow through repository creation — not in this batch.

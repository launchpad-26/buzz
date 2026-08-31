# Plan: issue #744 — document capabilities/git/credential-helper.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/git/credential-helper.md` does not exist
  (verified: `test -f` on worktree at `cad6c375f`).
- `launchpad/docs/corpus/templates/capability.md` exists and is the assigned
  template for `type: capabilities` nodes.
- `crates/git-credential-nostr` is the implementation: `src/lib.rs` (the
  helper logic), `src/main.rs` (thin binary entry), `README.md` (setup/usage/
  troubleshooting), `tests/integration.rs` (8 subprocess-level behavior tests).
- `architecture-flows-git-push` is already merged on `origin/launchpad` and
  already documents `git-credential-nostr`'s role as the client-side signer
  in the `git push` flow — a valid `references` target.
- `VISION_PROJECTS.md`'s Status table marks "Git hosting (smart HTTP +
  NIP-34)" as "Ships today" — the maturity evidence for this capability.
- Sibling tasks in Feature #613 (#748 nostr-git-authentication, #7xx
  smart-http, git-hosting, git-signing) are NOT merged and NOT read in
  depth — this node stays scoped to the client-side credential helper tool
  only, not the server-side auth gate or the smart-HTTP transport.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/credential-helper.md`:
- Front matter: `id: capabilities-git-credential-helper`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer,
  operator]` (operator included — Setup/Troubleshooting is operator-facing),
  `evidence` ledger with FACT entries citing `crates/git-credential-nostr/
  src/lib.rs`, `README.md`, `tests/integration.rs`, `VISION_PROJECTS.md`,
  `architecture-flows-git-push`'s own evidence. `relationships: [{type:
  references, target: architecture-flows-git-push}]` only — no other target
  resolves on `origin/launchpad`.
- Body per the capability template: Capability statement, Maturity, Boundary,
  Relationships, Scope and omissions. Cover: what the helper does (signs
  NIP-98 kind:27235 events from a git credential-helper protocol call),
  requirements (git 2.46+, `credential.helper nostr`, `useHttpPath true`),
  key file vs env var precedence and permission check, NIP-OA auth-tag
  passthrough, graceful-decline behavior for non-Buzz remotes / old git,
  and fail-closed error paths — each grounded in a specific test or code path.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm the
known 21 pre-existing FAIL baseline (#1951) is unchanged and the new node
adds zero new FAIL entries.

## STEP 3 — Earn the gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` alone. On `OK`, commit the new file + this plan with
`git commit -s`.

## GATES

- `validate.py` exits 0 for the new node; no new FAIL vs. baseline.
- `unittest discover` reports `OK`.
- Every FACT/INFERENCE cites an opened source; no TEAM_KNOWLEDGE without
  `provided_by`.

## BUDGET

One document, one commit. No second canonical file.

## OPEN

- Whether `nostr-git-authentication` (sibling, unmerged) will later absorb
  the server-side `GitAuth` detail this node currently only cites via
  `architecture-flows-git-push` — left for that node's own author.

## LEFT OUT

- Server-side NIP-98 verification internals (`GitAuth`, `verify_nip98_event`)
  — already covered by `architecture-flows-git-push`; cited, not restated.
- `git-sign-nostr` (commit/tag object signing) — an orthogonal, separate
  capability (sibling task #? git-signing).
- Smart-HTTP transport mechanics — sibling task (smart-http.md).

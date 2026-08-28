# Plan: issue #1038 — document layers/authorization/operator-authorization.md

## ALREADY TRUE

- Parent PRD #607 exists; issue #1038 asks for exactly one hand-authored corpus node
  at `launchpad/docs/corpus/layers/authorization/operator-authorization.md`.
- `launchpad/docs/corpus/layers/authorization/operator-authorization.md` does not exist
  on `origin/launchpad` or in this worktree (confirmed via `test -f`).
- No `type: layers` node exists anywhere in the corpus yet (confirmed via grep), so
  there is no sibling to duplicate or conflict with.
- `node.schema.json` and `AGENTS.md` govern front matter; no per-type template exists
  for `layers`-typed content nodes yet, so the node is written directly against the
  schema, following the shape the `concept.md` template documents for explanation-form
  content (definition first, boundary/non-goals, evidence-backed background,
  illustrative-only examples, scope-and-omissions).
- Real source evidence identified and opened directly: `crates/buzz-relay/src/api/admin/auth.rs`
  and `admin/mod.rs` (read-only deployment-admin HTTP gate), `crates/buzz-relay/src/api/operator.rs`
  (deployment-operator HTTP API, pubkey allowlist), `crates/buzz-relay/src/handlers/relay_admin.rs`
  (NIP-43 kinds 9030–9033 permission matrix), `crates/buzz-admin/src/main.rs` (operator CLI trust
  boundary), and `crates/buzz-relay/src/handlers/moderation_authz.rs` (the separate
  community/channel moderation seam this node must not conflate with operator authorization).
- Existing merged corpus nodes relevant as `references` targets:
  `architecture-context-relay-operator` (names `buzz-admin` and relay membership as
  touchpoints but explicitly defers their security model), `architecture-principles-fail-closed-boundaries`,
  `architecture-principles-community-is-security-boundary`.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/layers/authorization/operator-authorization.md` with
schema-valid front matter (`id: layers-authorization-operator-authorization`,
`type: layers`, `status: draft`, `origin: launchpad`, `audiences: [developer, operator,
reviewer]`), an evidence ledger citing only sources actually opened, and a body that:
defines the term in one sentence, states the boundary against community/channel
moderation explicitly, documents the four concrete authorization mechanisms found in
code, gives one illustration-only example, links related corpus nodes via
`relationships` plus explanatory prose, and closes with scope-and-omissions.

**Done when:** file exists, front matter matches the schema by inspection, every FACT
citation names a file actually opened during research.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root and
confirm exit 0.

**Done when:** validator exits 0 with no errors.

## STEP 3 — Verify against the issue's Definition of Done

Re-read the drafted node against every DoD checklist bullet in issue #1038, and
re-open each cited source to confirm it actually supports the claim sitting on it.
Confirm no second hand-authored corpus document was created.

**Done when:** every DoD bullet is satisfied and every citation re-checked.

## STEP 4 — Earn the commit gate and open the PR

Run the corpus unittest suite as the sole command in its own tool call
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`),
confirm `OK`, commit with `git commit -s`, push, and open a draft PR closing #1038.

**Done when:** PR is open as a draft, body states `Closes #1038`, states both checks
passed, states verification was self-review, and carries the deferred-review line.

## GATES

- `validate.py` must exit 0 before commit.
- The corpus unittest suite must print `OK` before commit, run as a lone command.
- No second hand-authored canonical corpus document.

## OPEN

- Whether a future community/channel-moderation corpus node should carry a
  `references` edge back to this one — left for that node's own author, per this
  node's own scope-and-omissions.

## LEFT OUT

- Documenting `authorize_moderation_action()` / community-channel moderation itself —
  a separate, already-implied future corpus node, explicitly out of scope per the
  issue's own out-of-scope list ("Creating or materially editing a second hand-authored
  canonical corpus document").
- Documenting `buzz-auth::Scope` (`admin:channels`/`admin:users`) — a different,
  token-scope axis, deliberately excluded to avoid a second concept in one node.
- Any change to runtime behavior — this is a documentation-only task.

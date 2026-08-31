# Plan: issue #759 — document capabilities/invites/invite-expiry.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/invites/invite-expiry.md` does not exist yet.
- No sibling invite node (#760 redemption, #761 invite-token, #762 invite) has any
  commits in this batch — their worktrees are clean at `cad6c375f`. No relationship
  target exists yet, so this node ships with no `relationships`.
- The corpus's `flow.md` template establishes precedent that a runtime-flow instance
  node carries `type: architecture` (no `flow` enum member exists); the merged
  `architecture/flows/websocket-authentication.md` node uses exactly this issue's DoD
  section shape (Trigger/preconditions/termination, Ordered interactions, Trust-boundary
  crossings, Failure/abort/rollback, Verification, Scope and omissions) with no Mermaid
  diagram, so that document is the structural precedent to follow, placed instead under
  `capabilities/invites/` per this issue's explicit path and id
  (`capabilities-invites-invite-expiry`).
- Source of truth for expiry behavior read and confirmed at `cad6c375fdcc590158c1456c9fc7875f0f84a844`:
  `crates/buzz-relay/src/invite_token.rs` (v1 stateless HMAC, expiry embedded in signed
  payload), `crates/buzz-core/src/invite.rs` (shared TTL bounds), `crates/buzz-db/src/store/relay_invite.rs`
  (v2 database-backed mint/claim/reap), `crates/buzz-relay/src/api/invites.rs` (HTTP mapping),
  `crates/buzz-relay/src/main.rs` (leader-only periodic reap tick), `migrations/0025_relay_invites.sql`
  (schema), plus desktop/mobile client error-string handling.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/invites/invite-expiry.md` with schema-valid
front matter (`id: capabilities-invites-invite-expiry`, `type: architecture`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer]`) and an evidence
ledger of FACT entries citing the files above, plus one TEAM_KNOWLEDGE entry for issue
#759's own DoD tail. Body sections: Trigger/preconditions/termination (mint bounds +
soft claim-time expiry vs. hard retention-sweep deletion as two distinct terminations),
Ordered interactions (v1 stateless check-at-claim path and v2 stored-expiry path),
Trust-boundary crossings (MAC-before-expiry ordering, expiry-before-membership ordering,
cross-tenant `(community_id, token_hash)` scoping, quiescing-community exclusion from
the sweep), Failure/abort/rollback (typed `Expired` outcomes, transaction rollback, reap
failure isolation), Verification (named tests), Scope and omissions (defers redemption
mechanics, the invite-token entity, mint authorization, and revocation to sibling tasks
not yet in the corpus).

Done when: the file exists, matches the shape above, and every substantive claim has a
citation.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root.

Done when: the new node adds zero new FAIL entries beyond the 21 pre-existing baseline
failures tracked in issue #1951.

## STEP 3 — Self-review

Re-read the drafted file against #759's DoD checklist line by line; re-open every cited
source to confirm it says what the statement claims; confirm exactly one hand-authored
file was added.

Done when: every DoD bullet has a corresponding section/evidence entry, and no cited
file was misread.

## STEP 4 — Earn the commit gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call; confirm `OK`. Then `git add` the new doc plus
this plan file and commit with `-s`.

Done when: the test run prints `OK` and the commit is created locally (no push, no PR).

## PARALLEL

None — single-file task, no independent sub-work to parallelize.

## GATES

- `validate.py` exits 0 with zero new FAIL entries.
- `unittest discover` on the corpus test suite prints `OK`.
- Commit is signed off (`-s`) and local only.

## BUDGET

Single node, ~5 evidence-backed sections. No code changes, no test files, no PR.

## OPEN

- Whether `type: architecture` (flow precedent) vs. `type: capabilities` (directory
  precedent) is the intended reading for a flow-shaped node placed under
  `capabilities/`. Resolved by following the corpus's own governance precedent in
  `templates/flow.md`'s "A note on `type`" section, since no capability-shaped
  alternative treats this DoD's section list at all.

## LEFT OUT

- A Mermaid `sequenceDiagram` (flow.md's generic template asks for one, but this
  issue's actual DoD and its merged sibling precedent do not, so it is left out to
  avoid drifting from the DoD that governs this task).
- `relationships` to #760/#761/#762 — none of those ids are merged yet.

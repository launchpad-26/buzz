# Plan: issue #1184 — document layers/tenancy/community-membership.md

Parent PRD: #607. Batch sibling (different task, different taxonomy path,
not authored here): issue #1034, `layers/authorization/community-membership.md`
(PR #1799, open, not merged — its file does not exist on disk in this worktree).

## ALREADY TRUE

- `launchpad/docs/corpus/layers/tenancy/community-membership.md` does not
  exist (confirmed: `find launchpad/docs/corpus -type f`; the `layers/`
  directory itself does not exist yet in this worktree).
- `launchpad/docs/corpus/layers/authorization/community-membership.md` (the
  #1034 sibling) also does not exist on disk here — PR #1799 is open, not
  merged. No `relationships` edge can target it.
- No `concept.md`-shaped or `layers`-specific template exists yet in
  `launchpad/docs/corpus/templates/` (only architecture/component/etc.
  templates, none named for a `layers` node) — write directly against
  `node.schema.json` per `AGENTS.md`'s "Until the standards land" guidance.
- `launchpad/docs/corpus/AGENTS.md` read in full (this session).
- Real code evidence located and read, establishing the TENANCY boundary
  ("is this pubkey admitted to this community at all"), distinct from
  #1034's AUTHORIZATION boundary ("what may an admitted member do"):
  - `crates/buzz-relay/src/api/mod.rs` (`relay_members` module) —
    `check_relay_membership`/`enforce_relay_membership`, the single
    admission gate for all authenticated entry points; NIP-OA owner
    delegation (`extract_nip_oa_owner`, `materialize_nip_oa_owner`).
  - `migrations/0001_initial_schema.sql:574-584` — `relay_members` table
    (NIP-43), `PRIMARY KEY (community_id, pubkey)`, `role TEXT CHECK (role
    IN ('owner','admin','member'))`.
  - `crates/buzz-db/src/relay_members.rs` — `is_relay_member`,
    `get_relay_member`, `add_relay_member`, `claim_relay_membership`,
    `remove_relay_member`/`remove_relay_member_if_role` (atomic,
    owner-protected), `bootstrap_owner`, `transfer_ownership`
    (`MAX_COMMUNITIES_PER_OWNER`), plus tests proving community confinement.
  - `crates/buzz-relay/src/api/invites.rs` (`claim_invite`) — invite-driven
    admission, v1 HMAC token path and v2 DB-backed path, join-policy
    acceptance recorded atomically with the membership row.
  - `crates/buzz-relay/src/handlers/relay_admin.rs` — kind:9030/9031/9032
    admin commands (add/remove/change-role), inline sender-role gate
    (admin-or-owner), owner-removal and self-removal guards.
  - `crates/buzz-relay/src/handlers/ingest.rs:2351-2412` — kind:28936
    (`KIND_NIP43_LEAVE_REQUEST`) self-service removal from `relay_members`.
  - `crates/buzz-core/src/kind.rs:387-404` — the NIP-43 kind constants
    (9030-9032 admin commands, 8000/8001 delta announcements, 13534
    membership snapshot, 28936 leave request).
  - `crates/buzz-relay/src/config.rs:143-147,590-592` —
    `require_relay_membership` (env `BUZZ_REQUIRE_RELAY_MEMBERSHIP`,
    default false/open relay).
  - PR #1799's own diff for `layers/authorization/community-membership.md`
    — read directly (not assumed) to confirm the boundary it draws and
    that it explicitly defers to this task for the tenancy side.
- Repository revision to record: `git rev-parse HEAD` = `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- No `check-plan.sh` script found anywhere in the worktree — proceeding
  without it per the task instructions.

## STEP 1 — Draw the tenancy/authorization boundary explicitly, in writing

Open with a one-sentence definition: tenancy community membership is whether
a `relay_members` row exists for a pubkey in a community at all — admission
and removal — never what a member may do once admitted (that is #1034's
subject, cited but not linked since its file isn't merged yet).

Done when: the Definition section states the boundary and names the sibling
concept without duplicating its content.

## STEP 2 — Write front matter against node.schema.json

`id: layers-tenancy-community-membership`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Build the
`evidence` ledger: one commit-citation FACT for the recorded revision, one
FACT per substantive claim (table schema, gate function, invite flow, admin
commands, leave request, config flag), one INFERENCE for the
tenancy/authorization split rationale (confidence stated), one
TEAM_KNOWLEDGE citing issue #1184's own DoD for the boundary requirement. No
`relationships` — the only candidate target (#1034's node) is unmerged.

Done when: every FACT cites a real, opened path; the INFERENCE carries
`confidence`; the TEAM_KNOWLEDGE carries `provided_by` and no `confidence`.

## STEP 3 — Write the body

Sections: Definition, Background (why a single gate — `enforce_relay_membership`'s
own doc comment), Use cases (invite claim, admin add/remove, self-leave,
NIP-OA delegation, owner bootstrap/transfer), a small comparison table
(admission paths: invite claim vs admin command vs self-leave vs owner
bootstrap), and Scope and omissions (channel-level membership /
`channel_members`, authorization/role capability, NIP-OA delegation
mechanics beyond the admission decision, join-policy acceptance mechanics).

Done when: every DoD bullet in issue #1184 is satisfiable by a section of
the body.

## STEP 4 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo
root; fix until exit 0. Run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own command; confirm `OK`.

Done when: both commands pass cleanly and no second hand-authored document
was created.

## STEP 5 — Commit, push, open draft PR

`git commit -s`, push branch, open a draft PR closing #1184, body noting
self-review only and "adjudicate/cross-model pass deferred to the batch
owner's review before merge."

Done when: PR URL exists and is reported back.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports `OK`.
- Commit gate (`git commit -s`) succeeds without touching the stamp file.

## OPEN

- Whether `layers/authorization/community-membership.md` (#1034/#1799)
  merges before or after this PR — if it merges first, a follow-up edit
  could add a `relationships` edge, but that is out of this task's scope
  per `AGENTS.md` step 9 (only link to nodes present on the branch being
  merged into).

## LEFT OUT

- Any edit to `layers/authorization/community-membership.md` itself.
- Channel-level (`channel_members`) admission/removal — a distinct,
  channel-scoped tenancy question, left as a named omission for a future
  task rather than folded in here.
- Deciding or restating role-based authorization rules — covered by #1034.

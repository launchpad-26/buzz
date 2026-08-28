# Plan: issue #1034 — document layers/authorization/community-membership.md

Parent PRD: #607. Batch sibling (different task, different taxonomy path,
not authored here): issue #1184, `layers/tenancy/community-membership.md`.

## ALREADY TRUE

- `launchpad/docs/corpus/layers/authorization/community-membership.md` does
  not exist (confirmed: `find launchpad/docs/corpus -type f`).
- `launchpad/docs/corpus/layers/tenancy/community-membership.md` (the #1184
  sibling) does not exist either — nothing to link to yet.
- The `concept.md` corpus template is merged at
  `launchpad/docs/corpus/templates/concept.md` and applies directly: this
  node explains one concept (what a member may *do*), not a reference
  catalogue or a procedure.
- `launchpad/docs/corpus/AGENTS.md` read in full (this session).
- Real code evidence located and read:
  - `crates/buzz-core/src/channel.rs` — `MemberRole` enum
    (Owner/Admin/Member/Guest/Bot), `permission_level`, `has_at_least`,
    `is_elevated`.
  - `crates/buzz-relay/src/handlers/moderation_authz.rs` —
    `authorize_moderation_action`/`decide_authority`, the single policy seam
    for every moderation capability, keyed off `relay_members.role` (owner/
    admin) with channel-role fallback for `DeleteMessage`/`Kick`.
  - `crates/buzz-core/src/git_perms.rs` — `default_min_role`, gating git ref
    writes by `MemberRole`.
  - `crates/buzz-db/src/channel.rs` — `get_member_role`, `is_member`
    (channel-scoped membership/role reads).
  - `crates/buzz-relay/src/api/mod.rs` (`relay_members` module) —
    `check_relay_membership`/`enforce_relay_membership`: the tenancy-side
    gate ("is this pubkey admitted to the community at all"), explicitly
    the boundary this node draws against, not this node's own subject.
  - `migrations/0001_initial_schema.sql` — `member_role` enum
    (`owner, admin, member, guest, bot`) backing `channel_members.role`;
    `relay_members.role` is a narrower `TEXT CHECK (role IN ('owner',
    'admin', 'member'))` on the same vocabulary.
- Repository revision to record: `git rev-parse HEAD` at draft time.

## STEP 1 — Confirm scope boundary against #1184, in writing

Read `moderation_authz.rs`'s own doc comment distinguishing "is a member"
(relay_members presence, tenancy) from "what can a member do" (role →
capability grid, authorization). State this boundary explicitly in the
node's Definition section, and note #1184's target id/path without adding a
`relationships` edge (its file does not exist on `origin/launchpad`).
Done-when: Definition section names both the tenancy question and the
authorization question and says which one this node answers.

## STEP 2 — Draft front matter by hand against `node.schema.json`

No `scaffold.py` fixture data (task metadata) beyond the issue body itself
is available, and this is a `concept.md`-templated instance, not a
templates-track task — hand-author front matter directly:
`id: layers-authorization-community-membership`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]` (operator omitted — this concept is code-authorization, not an
operator runbook), one provenance FACT evidence entry citing the recorded
commit. Done-when: front matter parses and matches the schema's required
field set with no extra keys.

## STEP 3 — Write the body per `concept.md`'s required sections

Definition (role hierarchy + capability-grid concept, with the tenancy
boundary from Step 1), Background (why community-level owner/admin also
carries channel-wide authority — cite `moderation_authz.rs`'s own doc
comment on the Phase 1 contract), Use cases (moderation commands, git ref
push permission, channel administration), Comparison (channel-level
`MemberRole` five-value enum vs. community-level `relay_members` three-value
role — same vocabulary subset, different table/scope), Scope and omissions
(explicitly: does not cover tenancy/membership admission, does not cover
the join/invite flow, does not cover git protection-tag parsing beyond
citing the role floor). One evidence entry per substantive claim, each
opened and read this session — no citation added without having read the
source. Done-when: every claim in the body has a matching `evidence` array
entry and every `FACT` entry's source was actually opened above.

## STEP 4 — Validate and test

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root; fix anything it names; re-run to exit 0. Then, as the sole
command in its own tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
and confirm `OK`. Done-when: both commands pass cleanly.

## STEP 5 — Commit, push, open draft PR

`git commit -s`, push the branch, open a **draft** PR against
`launchpad-26/buzz` with `Closes #1034`, noting both checks passed, that
verification was self-review only (no `review-code` skill invoked), and the
required "Draft — adjudicate/cross-model pass deferred to the batch owner's
review before merge" line. Done-when: PR URL exists and is reported back.

## GATES

- `validate.py` exits 0 (Step 4).
- `unittest discover` reports `OK` (Step 4), run as a lone command.
- No second hand-authored canonical document created.
- No `relationships` entry added (nothing on `origin/launchpad` to target).

## OPEN

- Whether #1184's `layers/tenancy/community-membership.md` lands before or
  after this PR is out of this task's control; either order is fine since
  no relationship edge is being added in either direction.

## LEFT OUT

- Any change to runtime authorization behavior — this task is documentation
  only.
- A `references` edge to a tenancy node that does not exist yet on the
  merge target — named as a gap in Scope and omissions instead.
- Full treatment of `git_perms.rs`'s protection-tag parsing — cited once for
  the role-floor concept, not exhaustively documented (that is reference-doc
  territory, not this concept node's job).

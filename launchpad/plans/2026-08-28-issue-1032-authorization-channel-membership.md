# Plan: issue #1032 — document layers/authorization/channel-membership.md

## ALREADY TRUE

- `launchpad/docs/corpus/layers/authorization/channel-membership.md` does not exist
  (`test -f` confirmed). No `layers/` directory exists under the corpus yet — this
  node is the first `type: layers` instance.
- `launchpad/docs/corpus/templates/concept.md` is merged on `origin/launchpad`. The
  DoD bullets ("defines the term in one sentence," "states boundaries/non-goals,"
  "links to related concepts," "examples clarify, don't introduce a second concept")
  match `concept.md`'s required-sections list exactly, so this node is authored as a
  `concept` instance, `type: layers` (the corpus surface, per PRD #602's list — not
  the documentation form).
- No open PR targets branch `task/1032-authorization-channel-membership` or
  references issue #1032 (`gh pr list --search "1032 in:title"` → empty).
- `launchpad/docs/corpus/AGENTS.md` (full text read) governs node creation; where it
  and `corpus-author`/`corpus-plan` skills disagree, `AGENTS.md` wins.
- Source evidence gathered directly from code at `git rev-parse HEAD` (recorded in
  Step 2 below):
  - `crates/buzz-core/src/kind.rs:422-426` — `KIND_NIP29_GROUP_METADATA` (39000),
    `KIND_NIP29_GROUP_ADMINS` (39001), `KIND_NIP29_GROUP_MEMBERS` (39002).
  - `crates/buzz-db/src/channel.rs` — `is_member` (L643), `membership_pairs` (L666),
    `get_members` (L698), `get_accessible_channel_ids` (L754, the UNION of explicit
    `channel_members` rows with all `open`-visibility channels — this is the core
    membership-resolution mechanism), `add_member` (L382) and `remove_member` (L560)
    with their role-escalation and last-owner guards.
  - `crates/buzz-auth/src/access.rs` — `ChannelAccessChecker` trait, `check_read_access`
    / `check_write_access`, tenant-scoping contract and its S1 cross-community fence.
  - `crates/buzz-relay/src/handlers/req.rs` — `handle_req`'s membership-gated flow:
    cached `accessible_channels` (10s TTL), request-local repair via
    `resolve_request_local_access` (L526), `p_gated_filters_authorized` (the p-gate
    from `AGENTS.md`/`CLAUDE.md`).
  - `crates/buzz-relay/src/state.rs:1231-1249` —
    `get_accessible_channel_ids_cached`, the cache wrapper around
    `get_accessible_channel_ids`.
  - `crates/buzz-relay/src/handlers/side_effects.rs:1040-1168` —
    `group_members_tags` and `emit_group_discovery_events`: kind:39002 is relay-signed,
    `d`-tagged with the channel UUID, `p`-tagged per active member with role, and
    stored channel-scoped so private-channel rosters stay access-controlled.
  - `architecture-principles-community-is-security-boundary` (merged on
    `origin/launchpad`) is the one existing corpus node whose subject is adjacent
    enough for a `references` edge.

## STEP 1 — Confirm scope and template, no file changes

Re-derive: this node's subject is "channel membership" as one concept — how a
channel's active member set is stored, computed and enforced at the authorization
boundary — not channel *creation*, not role/permission semantics beyond what
membership itself gates. If drafting reveals role-based authorization (owner/admin
elevation rules) needs its own document, name that as a discovered second concept
and file it as a new task rather than folding it in here — do not draft its content.

**Done when:** scope sentence is fixed before any Markdown is written.

## STEP 2 — Record revision, gather evidence, hand-author front matter

Run `git rev-parse HEAD` in this worktree and use that SHA as the provenance
citation. `templates/concept.md` is merged, but `scaffold.py` (issue #632) is not
present in this checkout — hand-author the front matter directly against
`node.schema.json`, matching what `scaffold_node` would have produced (one
provenance evidence entry citing the recorded commit) plus one evidence entry per
substantive claim from the ALREADY TRUE evidence list above. Classify per
`AGENTS.md`: FACT for statements the cited file itself asserts, INFERENCE with
`confidence` for reasoned claims (e.g. why open-channel access needs no explicit
row), TEAM_KNOWLEDGE with `provided_by` only if a claim rests on an issue/PR/commit
message rather than an openable file.

**Done when:** front matter validates in isolation (`id: layers-authorization-
channel-membership`, `type: layers`, `status: draft`, `origin: launchpad`,
`audiences`, `evidence` array with >=1 entry per claim used in the body).

## STEP 3 — Write the body against `templates/concept.md`'s required sections

Sections: optional intro, required **Definition** (what "channel membership" is —
the `channel_members` row plus the open-channel-implies-access rule — and its
boundary against role/permission semantics), optional Mermaid diagram only if it
clarifies the membership-resolution flow (REQ → cached lookup → DB confirm → repair),
optional Background (why open channels need no explicit row — INFERENCE), required
**Use cases** (why a reader — agent or developer — needs this: understanding REQ
access gating, `#h` filter scoping, kind:39002 snapshot semantics), optional
Comparison (open vs. private channel membership resolution — this one is concrete
enough to include), **Related resources** as a `references` relationship to
`architecture-principles-community-is-security-boundary` (only target that exists
on `origin/launchpad` and is topically adjacent) rather than a prose link, and the
required **Scope and omissions** section naming both what this node does not cover
(role/permission escalation rules, DM participant membership peculiarities, the
p-gate's non-membership authorization layer) and what was expected but not
independently verified (e.g. the redis cross-pod cache-invalidation path referenced
in `state.rs`'s doc comments was read but not executed/traced at runtime).

**Done when:** every required section from `concept.md` is present, every
substantive sentence has a matching `evidence` entry, and the boundary section
explicitly states this node covers *membership*, not role-based authorization or
channel visibility/creation policy.

## STEP 4 — Validate and earn the commit gate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root
(exit 0 required). Then, as the sole command in its own tool call, run
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` and confirm `OK`. Only after both pass, commit with `git commit -s`.

**Done when:** both commands exit clean and are shown, not just claimed.

## STEP 5 — Push and open the draft PR

Push `task/1032-authorization-channel-membership`, open a **draft** PR against
`launchpad-26/buzz` (title `docs(corpus): document channel membership (#1032)`),
body states `Closes #1032`, that `validate.py` and the corpus unittest suite both
passed, that verification was self-review only, and the deferred-review sentence
per the task brief.

**Done when:** PR URL exists and is reported back.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — exit 0, run twice
  (after drafting and again after final self-review).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
  "test_*.py"` — `OK`, run as the sole command in its own tool call before
  committing.

## OPEN

- Whether `scaffold.py` (issue #632) exists in this checkout was checked once, at
  worktree creation — if it has since merged, prefer it; this plan hand-authors
  as the documented fallback either way, per `corpus-author`'s skill instructions.
- Exact wording of the Definition/boundary split against role-based authorization
  is a drafting decision, not fixed here — Step 3's scope sentence is the anchor
  to draft against.

## LEFT OUT

- Role/permission escalation semantics (owner/admin grant rules in `add_member`) —
  adjacent but a distinct concept; not folded into this node.
- Any change to runtime behavior. This is a documentation-only task.
- A second canonical document of any kind.

Issue #1078 — task: document layers/data/postgres/channels-table.md
Stated size: dispatch brief caps this task at 5 steps (one small corpus document) -> cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and
`launchpad/docs/corpus/AGENTS.md` are merged on `origin/launchpad`; the target file
`launchpad/docs/corpus/layers/data/postgres/channels-table.md` (confirmed from the
issue's own Objective sentence, not the dispatch guess) does not exist yet, and
`origin/launchpad`'s corpus tree carries no other node under `layers/data/postgres/`
or naming `channels`, `communities`, `datastore` or `data-entity` (checked with
`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`) — so no
`relationships` target exists yet for this node.

**Template-shape correction from the dispatch brief.** The brief's guess that
`templates/datastore.md` is "likely the right shape" does not hold up against the
issue's own DoD bullets ("Defines identity/key and semantic ownership", "Summarizes
fields by meaning without duplicating generated schema detail", "Defines
relationships, lifecycle and invariants", "Links authoritative migration/schema and
read/write code paths") — those four map near-verbatim onto
`templates/data-entity.md`'s six required sections (Identity, Attributes and shape,
Invariants, Relationships, Provenance, Storage pointer), not onto `datastore.md`'s
whole-instance sections (technology/attachment profile, schema/namespace inventory
across many tables, migration mechanism, access-pattern summary, operational
characteristics). `datastore.md` documents a whole running Postgres instance;
`data-entity.md` documents one domain concept — and "the channels table" is one
table mapping onto one domain concept (`Channel`), the shape `data-entity.md` exists
for. This node is built against `data-entity.md`'s required sections. The
`type: layers` precedent from the dispatch brief still applies regardless of which
template's section list is followed (see STEP 2) — read directly off the merged-once
siblings `layers/data/object-storage/s3.md` and `media-objects.md` (open PR
launchpad-26/buzz#1873, worktree `__worktrees/batch-610-3`), both of which override
their own template's `type: architecture`/`type: implementation` suggestion the same
way and disclose it in their own ledgers, citing `standards/taxonomy.md` step 4.

STEP 1 Gather evidence.                                                [independent]
Read `migrations/0001_initial_schema.sql` (the `channels` table definition, its
`channel_type`/`channel_visibility` enums, its `(community_id, id)` primary key, its
`chk_channels_id_not_nil` check and `channels_community_id_immutable` trigger, and
the `channel_members` FK with `ON DELETE CASCADE`), `migrations/0022_event_ttl_refresh.sql`
and `migrations/0024_event_ttl_refresh_shared_lock.sql` (TTL-refresh-on-message-insert
mechanism and its advisory-lock ordering), `migrations/0027_channels_id_lookup_index.sql`
(the "`id` alone is not unique" note and its covering index), `migrations/0029_community_deletion.sql`
(`attach_community_write_fence('channels')`), `crates/buzz-core/src/channel.rs`
(`ChannelVisibility`, `ChannelType`, `MemberRole` enums and `canonical_channel_name`),
`crates/buzz-db/src/channel.rs` (`ChannelRecord`, `create_channel`,
`create_channel_with_id`, `get_channel`, `update_channel`, `archive_channel`,
`unarchive_channel`, `soft_delete_channel`, `reap_expired_ephemeral_channels`),
`crates/buzz-core/src/kind.rs` (`KIND_NIP29_CREATE_GROUP` = 9007,
`KIND_NIP29_GROUP_METADATA`/`_ADMINS`/`_MEMBERS` = 39000-39002),
`crates/buzz-relay/src/handlers/side_effects.rs` (`create_channel` called from kind
9007 ingest; `emit_group_discovery_events` synthesizing kind 39000/39001/39002 from
the table after creation/metadata/membership changes), root `CLAUDE.md`'s "Channel
scoping" gotcha, `launchpad/docs/corpus/templates/data-entity.md`, and
`launchpad/docs/corpus/standards/taxonomy.md`'s disclosure rule (step 4).
done when: every source above has been opened this session (not recalled), and each
substantive fact intended for the node's evidence ledger has a specific path/line or
symbol it will cite, not a generic file reference.

STEP 2 Write the node's front matter and body.                            [needs 1]
Front matter: `id: layers-data-postgres-channels-table`, `type: layers` (overriding
`data-entity.md`'s own worked-instance guidance of `type: implementation`, for the
batch-consistency reason `s3.md` gives for its identical override of
`datastore.md`'s `type: architecture` suggestion, disclosed in the ledger per
`standards/taxonomy.md` step 4), `status: draft`, `origin: launchpad`, `audiences:
[agent, developer, reviewer]`, no `relationships` (nothing merged yet to target —
checked in ALREADY TRUE, not assumed). Body structured against `data-entity.md`'s
six required sections: Identity (`(community_id, id)` composite PK, the immutability
trigger), Attributes and shape (fields by meaning, not the raw DDL), Invariants
(id-not-nil, community immutability, per-community uniqueness of
`nip29_group_id`/`participant_hash`), Relationships (FK to `communities`,
`channel_members` cascade, the moderation-table FK), Provenance (row created by relay
ingest of kind 9007; kind 39000/39001/39002 are relay-signed derived projections
emitted *from* the row — the inverse of `thread_metadata`'s event-sourced shape),
Storage pointer (table `channels`, the migrations from STEP 1, and the
`buzz-db/src/channel.rs` read/write surface). Plus a scope-and-omissions section
naming `channel_members`'s own columns (#1077), `communities` (#1079) and
`datastore`-level mechanics as explicitly out of scope.
done when: the file exists at
`launchpad/docs/corpus/layers/data/postgres/channels-table.md`, every claim in the
body has a matching `evidence` entry classified FACT/INFERENCE/TEAM_KNOWLEDGE per
`AGENTS.md`'s rules, and the file contains no `relationships` key.

STEP 3 Validate.                                                          [needs 2]
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repository
root; fix and re-run until exit 0.
done when: the command's own exit code is 0, observed directly (not inferred from
its printed output).

STEP 4 Earn the gate and commit.                                    [needs 3] <- RUNS HERE
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole, bare, unpiped command in its own tool call; confirm it
reports OK. Only then, in a separate tool call, `git add` the plan and the node file
and `git commit -s`. Do not push and do not open a PR — this task's scope ends at a
committed worktree; a later batch step bundles it with its siblings.
done when: the unittest command's own output contains `OK` and its exit code is 0;
`git log -1 --oneline` on this branch shows exactly one (or, if a follow-up fix was
needed, two) new commit(s) ahead of `origin/launchpad` touching only the plan file
and the target corpus document.

STEP 5 Self-review.                                                       [needs 4]
Re-read `git diff origin/launchpad -- .` against every DoD bullet in #1078's body
line by line; confirm every evidence entry actually supports its statement; confirm
no second canonical document was created; re-run `validate.py` and confirm it still
exits 0.
done when: each DoD bullet from the issue body is matched to the specific section or
front-matter field that satisfies it, written down in this session, and
`validate.py` exits 0 on the final diff.

PARALLEL: none — single file, single worktree, no dependency on sibling batch tasks.
`#1077`/`channel_members` and `#1079`/`communities` are explicitly out of scope per
#1078's own Out-of-scope bullet and are only checked not to exist yet on
`origin/launchpad`, never read for content.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK, run bare and unpiped, before commit. `review-adjudicate`
and the cross-model final-review pass are explicitly deferred to the batch owner's
review — not run in this session, and this task does not push or open a PR at all
per its own dispatch brief (isolate/plan/build/verify/commit only).

BUDGET: single document, one sitting — no multi-hour scope expected.

OPEN: whether kind 39000/39001/39002's relay-signed, derived-from-the-row status
(rather than the row being derived from an event, as `thread_metadata` is) needs its
own explicit boundary sentence against a future `#1337`/event-kind node once one
exists for those kinds — recorded as a Provenance-section observation, not resolved
here, since no event-kind corpus node exists yet to link against.

LEFT OUT: no `relationships` edges (no sibling entity, datastore, or event-kind node
merged yet to target — checked via `git ls-tree`, not assumed); no description of
`channel_members`'s own columns beyond the one FK relationship it forms with
`channels` (that table's own fields are #1077's document, explicitly out of scope
here); no attempt to resolve whether `.env.example`-style datastore-level facts
(replication, backup posture) belong in this node — those are `datastore.md`'s
territory per its own boundary section, and this node does not restate storage
mechanics beyond naming the table and linking the migrations that define it; no push,
no PR — out of scope for this task per its own dispatch brief.

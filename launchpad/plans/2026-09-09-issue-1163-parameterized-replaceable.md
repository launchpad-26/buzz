# Plan — issue #1163: parameterized-replaceable events corpus node

**Issue:** launchpad-26/buzz#1163 (parent Feature #609)
**Target:** `launchpad/docs/corpus/layers/protocol/parameterized-replaceable-event.md`
**Node id:** `layers-protocol-parameterized-replaceable-event`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1163-parameterized-replaceable`, branch `task/1163-parameterized-replaceable`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` in the worktree; confirmed with `git cat-file -e`, exit 0)

## Size

Small — one hand-authored Markdown node, no runtime change.

## Step 1 — evidence pass (done before drafting)

Read, in full or at the relevant symbols:

- `crates/buzz-db/src/store/replaceable.rs` — the substance. The dispatch prompt named
  `crates/buzz-relay/src/handlers/replaceable.rs`; **no such file exists**. Supersession
  and dominance live in buzz-db.
- `crates/buzz-core/src/kind.rs` — `is_parameterized_replaceable`,
  `PARAM_REPLACEABLE_KIND_MIN`/`MAX`, `is_replaceable` (the sibling class), the
  compile-time asserts and the disjointness test.
- `crates/buzz-db/src/store/event.rs` — `extract_d_tag`, `D_TAG_MAX_LEN`,
  `soft_delete_by_coordinate`.
- `crates/buzz-relay/src/handlers/ingest.rs` — the routing branch and the
  `duplicate:` response on a non-insert.
- `crates/buzz-cli/src/commands/mod.rs`, `notes.rs`, `error.rs` — `Conflict` → exit 5.
- `schema/schema.sql`, `migrations/0001_initial_schema.sql` — `idx_events_parameterized`.

**Done when:** the dominance comparison, the tie-break direction, and the
DB-uniqueness question are each answered from a file actually opened.

## Step 2 — verify the uniqueness claim myself

Do not inherit the sibling's finding. Grep for a `UNIQUE` index or constraint over
`(community_id, kind, pubkey, d_tag)` on `events` in both `schema/schema.sql` and
`migrations/`. Confirm `idx_events_parameterized` is `CREATE INDEX`, not
`CREATE UNIQUE INDEX`, and that it is partial.

**Done when:** an absence claim exists that a tool-result citation can carry in the
shape `identifier(args) -> result`.

## Step 3 — pick relationships against `origin/launchpad` only

Grep the merged-id list for each candidate before writing it. No #609 sibling —
`#1164` (plain replaceable) is committed but unmerged and must not be targeted.

**Done when:** every `relationships[].target` appears in the merged-id list.

## Step 4 — draft the node

Concept-template shape: definition first, then the disambiguation against plain
replaceable (`(pubkey, kind)`, no `d`) that the template's required Definition
section demands, then the coordinate, the write outcomes, the dominance rule,
what is and is not enforced by the database, use cases, and a two-part
scope-and-omissions section.

Front matter: `type: layers`, `status: draft`, `origin: launchpad`, one commit-only
provenance FACT, honest classes throughout. Link neighbours rather than restating
the events table, its indexes, or channel metadata.

**Done when:** `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.

## Step 5 — self-review, stamp, commit

Re-read every evidence entry against its source before the stamp. Then run the
corpus test suite as the sole foreground command with a 600000 ms timeout, confirm
the final line is `OK`, and commit with `-s`. No push, no PR.

**Done when:** the suite ends `OK` and one signed commit exists on the branch.

## Out of scope

- Plain replaceable events (#1164) beyond the one-paragraph disambiguation.
- The `events` table's columns and index catalogue — owned by
  `layers-data-postgres-events-table` and `layers-data-postgres-indexes`.
- NIP-RS read-state and buzz-mesh-status hard-delete behaviour — a second concept;
  named as a follow-up candidate, not folded in.
- Any runtime change.

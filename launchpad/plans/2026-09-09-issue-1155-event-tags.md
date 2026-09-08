Issue #1155 — task: create `launchpad/docs/corpus/layers/protocol/event-tags.md`, the canonical concept node for event tags

Stated size: no `Size` line — `.github/ISSUE_TEMPLATE/02-task.yml` carries none. Sized from
the issue's own deliverable: exactly one corpus Markdown node, no code change. → **cap: 5 steps**,
which is also the dispatch brief's ceiling.

ALREADY TRUE  (verified against the worktree and the actual files, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1155-event-tags`, branch
  `task/1155-event-tags`, fresh off `origin/launchpad` at `29ca9b189bd3f639ba09c972b57c70538c0860c6`
  (`git cat-file -e` exits 0 — that is this node's provenance revision).
  `launchpad/docs/corpus/layers/protocol/` does not exist; no `layers/protocol/**` node is
  merged on `origin/launchpad` (checked against the merged-id list). Every relationship target
  must therefore come from outside that directory.
  `crates/buzz-core/src/filter.rs` holds `filter_match_one`, the in-memory NIP-01 matcher, which
  iterates `Filter::generic_tags` and compares `Tag::content()` against each filter value.
  `crates/buzz-relay/src/handlers/req.rs`'s `filter_fully_pushable` enumerates, in its own doc
  comment and match arms, exactly which tag keys reach SQL and which force a Rust post-filter.
  `crates/buzz-db/src/store/event.rs` holds `EventQuery` (`e_tags`, `custom_tag`, `d_tag(s)`,
  `channel_ids`, `p_tag_hex`, `shared_gated_reader`), the `tags @>` containment pushdowns,
  `extract_d_tag`, `extract_not_before`, and the superset-containment note on `shared_gated_reader`.
  `crates/buzz-db/src/runtime/mod.rs`'s `insert_mentions_in_transaction` reads `tag_vec[0]`/`tag_vec[1]`.
  `migrations/0001_initial_schema.sql` declares `tags JSONB NOT NULL` plus the `channel_id`,
  `d_tag` and `not_before` columns and the `event_mentions` table; `migrations/0004_events_tags_gin.sql`
  creates `idx_events_tags_gin` (GIN, `jsonb_path_ops`);
  `migrations/0011_nip_rs_exact_tag_cardinality.sql` enforces exact tag cardinality for one kind
  at the trigger level.
  `crates/buzz-relay/src/nip11.rs`'s `RelayLimitation` advertises eleven limits, none of them a
  tag count or tag-value length.
  `crates/buzz-acp/src/relay.rs`'s `query_raw` doc comment states `nostr::Filter` only encodes
  single-letter generic tags; `crates/buzz-relay/src/api/bridge.rs`'s `extract_buzz_channel` is
  the raw-JSON escape hatch that reaches `EventQuery::custom_tag`.
  `docs/nips/` contains no `NIP-01.md` (`ls` exits 2; repo-wide `find -name 'NIP-01*'` is empty),
  so no upstream spec text is citable as a repo path.
  Merged and legal as relationship targets: `layers-data-postgres-events-table`,
  `layers-data-postgres-indexes`, `capabilities-search-search-query`,
  `implementation-crates-buzz-core`, `implementation-crates-buzz-db`,
  `implementation-crates-buzz-relay`.

STEP 1  Fix the node's boundary before drafting a line of prose.                 [independent]
        The subject is the tag *mechanism*: the array-of-arrays shape, the
        single-letter filter-key convention, and how a tag becomes a queryable
        dimension. What any individual tag *means* — `d`, `e`, `h`, `p` — is
        four sibling tasks' territory and is named only as a boundary, by
        subject, never explained. The merged `layers-data-postgres-indexes`
        already owns the index inventory and
        `layers-data-postgres-events-table` owns the `events` row shape; both
        are linked, never restated.
        done when: a written boundary list exists naming, for each of the four
        sibling tag subjects and the three adjacent merged nodes, the one
        sentence this node is allowed to say about it.

STEP 2  Draft the front matter against `schema/node.schema.json`.                   [needs 1]
        `id: layers-protocol-event-tags`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer]`. Exactly one
        commit-only FACT — the provenance entry naming
        `29ca9b189bd3f639ba09c972b57c70538c0860c6`. Every other FACT cites a
        bare repo-relative path that was actually opened; the two claims that
        rest on reading a third-party crate's behaviour from Buzz's call sites,
        not from the crate source, are INFERENCE with honest `confidence`; the
        absence of upstream NIP text is a tool-result citation quoting the real
        command output. `relationships` names only ids grepped out of the merged
        list in ALREADY TRUE.
        done when: every `evidence[].evidence` path resolves under the worktree
        root, and the ledger contains exactly one commit-only FACT.

STEP 3  Write the body to `templates/concept.md`'s required sections.               [needs 2]
        Definition first (one sentence, then the array-of-arrays structure),
        then the single-letter indexing convention, then the promotion table —
        the four routes by which a tag becomes queryable (dedicated column,
        side table, JSONB containment pushdown, Rust post-filter) — then
        cardinality and length, then Scope and omissions carrying its two
        distinct halves. No enumeration of what any single tag means.
        done when: every required section from `templates/concept.md` is
        present, and no paragraph explains the semantics of `d`, `e`, `h` or `p`.

STEP 4  Self-review the whole node against the issue's own definition of done.       [needs 3]
        Re-open every cited file and confirm it says what its statement claims —
        the validator never does this. Re-check that no relationship targets an
        unmerged sibling. Confirm the two "expected but could not verify"
        disclosures are real and specific, not filler.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py`
        exits 0, and every DoD checkbox in issue #1155 has been walked
        individually.

STEP 5  Stamp, then commit.                                                          [needs 4]
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole foreground command, 600000ms timeout, no pipe.
        Then `git add` + `git commit -s` in a separate call. No push, no PR.
        done when: the suite's final line is `OK` and the commit exists on
        `task/1155-event-tags`.

OPEN
  Whether `nostr::Tag::content()` returns positional element 1 for a tag with three or more
  elements could not be established from the crate source — no cargo registry cache exists on
  this machine (`find / -type d -name nostr-0.45.1` returns nothing). The claim is carried as
  INFERENCE from Buzz's own call sites, and the gap is disclosed in the node body.

Issue #1153 — document the event kind as a corpus concept node
Stated size: no `Size` line on the issue (corpus-plan document task) -> cap: 5 steps (batch brief's cap)

ALREADY TRUE  (verified against the real repository, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/task-1153-event-kind`, branch
  `task/1153-event-kind`, branched from `origin/launchpad` at
  `29ca9b189bd3f639ba09c972b57c70538c0860c6` (`git rev-parse HEAD` inside the worktree;
  `git cat-file -e` on that sha exits 0).
  `launchpad/docs/corpus/layers/protocol/` does not exist on `origin/launchpad` —
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus/layers/` lists
  compute/, configuration/, data/ and others, no protocol/. So this file is a create.
  `crates/buzz-core/src/kind.rs` is 1087 lines. Its module doc calls it "the authoritative
  source for Buzz kind numbers". It declares the four range constants
  (`EPHEMERAL_KIND_MIN`/`MAX` = 20000/29999, `PARAM_REPLACEABLE_KIND_MIN`/`MAX` =
  30000/39999), three classification helpers (`is_ephemeral`, `is_replaceable`,
  `is_parameterized_replaceable`), `ALL_KINDS`, and ~28 `const _: () = assert!(...)`
  compile-time range guards.
  `is_ephemeral` and `is_parameterized_replaceable` are pure range comparisons.
  `is_replaceable` is **not** — it is `matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA |
  10000..=19999)`. There is no `is_regular` predicate at all.
  `docs/nips/` holds only Buzz's own two-letter NIPs (NIP-AA, NIP-AM, NIP-IA, NIP-MP, …).
  `ls docs/nips/NIP-01.md` -> "No such file or directory"; `find . -name 'NIP-0*.md'` ->
  no output. No upstream numbered NIP text is in this repository.
  Merged neighbours confirmed present on `origin/launchpad` (grepped from the batch's
  merged-id list): `implementation-crates-buzz-core`, `development-event-kind-changes`,
  `corpus-template-event-kind`, `layers-data-postgres-events-table`,
  `architecture-principles-event-driven-extension`.
  `layers-data-postgres-events-table` already documents the events row shape and the
  replaceable/parameterized-replaceable *storage identity* from the table's side, and
  says explicitly that what a kind's tags or content mean is "each kind's own event-kind
  node's job". `development-event-kind-changes` owns the add/change *procedure*.
  `corpus-template-event-kind` owns how to document one kind.

BOUNDARY (decided before drafting, so the node does not drift)
  Mine: what a kind *is*, the class-by-number semantics, the effective numeric ceiling,
  Buzz's own allocation policy, and where the registry lives.
  Not mine: the add-a-kind procedure (`development-event-kind-changes`), the per-kind
  documentation shape (`corpus-template-event-kind`), the row/column contract
  (`layers-data-postgres-events-table`), any catalogue of individual kinds (that is
  reference territory the concept template explicitly warns against).

STEP 1 — Confirm the concept boundary against the three merged neighbours
  Read `development/event-kind-changes.md`'s Boundary and Scope sections and
  `templates/event-kind.md`'s Boundary section in full, and the parts of
  `layers/data/postgres/events-table.md` that mention `kind`.
  done-when: I can name, in one sentence each, what each of the three owns that this node
  must link to rather than restate, and no section I intend to write duplicates one of them.

STEP 2 — Settle the two factual questions the dispatch flagged
  (a) Does Buzz classify kinds by range or per kind? Read all three helpers, the
      `replaceable_and_parameterized_are_disjoint` test, and every call site in
      `crates/buzz-relay/src/handlers/ingest.rs`, `crates/buzz-relay/src/handlers/event.rs`
      and `crates/buzz-db/src/store/event.rs`.
  (b) Does the "kind 41 unused" claim in `CLAUDE.md` hold? Read `KIND_CHANNEL_METADATA`'s
      doc comment and grep every reference to the constant across the workspace.
  done-when: both answers are written down with the exact code that settles them, including
  the nuance if the answer is "both" rather than one or the other.

STEP 3 — Write the node
  Create `launchpad/docs/corpus/layers/protocol/event-kind.md` with front matter per
  `node.schema.json` (`id: layers-protocol-event-kind`, `type: layers`, `status: draft`,
  `origin: launchpad`), exactly one commit-only FACT (the provenance entry), the absence of
  upstream NIP text recorded as a tool-result citation, and the concept template's required
  sections — Definition first, then Background, Use cases, Comparison (the four storage
  classes), Related resources as typed relationships, and Scope and omissions carrying both
  what it does not cover *and* what could not be verified.
  done-when: the file exists, every FACT cites a source I opened in step 1 or 2, and no
  section is a catalogue of kind numbers.

STEP 4 — Validate
  Run `python3 launchpad/project-intelligence/corpus/validate.py`.
  done-when: exit status 0, and every relationship target resolves against
  `origin/launchpad` rather than only against this worktree.

STEP 5 — Self-review, stamp, commit
  Re-read every evidence entry against its cited source and every DoD bullet on #1153
  before stamping, because editing after the commit clears the stamp. Then run the corpus
  test suite as the sole foreground command with a 600000ms timeout, confirm the final line
  is `OK`, and commit with `-s` in a separate call. Do not push; do not open a PR.
  done-when: suite ends `OK` and the commit exists on `task/1153-event-kind`.

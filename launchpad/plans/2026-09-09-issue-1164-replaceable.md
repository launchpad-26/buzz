# Plan — issue #1164: document replaceable events

**Issue:** launchpad-26/buzz#1164 (Feature #609)
**Target:** `launchpad/docs/corpus/layers/protocol/replaceable-event.md`
**Node id:** `layers-protocol-replaceable-event`
**Template:** `launchpad/docs/corpus/templates/concept.md`
**Worktree:** `__worktrees/task-1164-replaceable`, branch `task/1164-replaceable`
**Provenance revision:** `29ca9b189bd3f639ba09c972b57c70538c0860c6` (confirmed with `git cat-file -e`)

## Step 1 — Evidence: the predicate (DONE before drafting)

Establish, by reading `crates/buzz-core/src/kind.rs`, that `is_replaceable` is an
**enumerated set**, not a range check: `matches!(kind, 0 | 3 | KIND_CHANNEL_METADATA |
10000..=19999)`. Contrast with `is_ephemeral` and `is_parameterized_replaceable`, both of
which are two-sided comparisons against named `*_MIN`/`*_MAX` constants. Confirm
`KIND_CHANNEL_METADATA = 41` and its "Not used by Buzz today" doc comment.

**Done when:** the predicate body, both sibling predicates, the constant, and the
compile-time assertions have been read in the worktree.

## Step 2 — Evidence: supersession and tie-break

Read `crates/buzz-db/src/store/replaceable.rs#replace_addressable_event` and
`crates/buzz-relay/src/handlers/ingest.rs` (the single production call site of
`is_replaceable`). Establish the replacement key, the highest-`created_at` rule, the
same-second tie-break, the soft-delete, the advisory lock, and the duplicate-id rollback.
Read `crates/buzz-db/src/store/event.rs#extract_d_tag` for the `d_tag`-stays-NULL fact.

**Done when:** the tie-break expression has been read literally, not paraphrased from a
doc comment.

## Step 3 — Evidence: scoping and gaps

Confirm which replaceable kinds `is_global_only_kind` forces to `channel_id = NULL`, and
record the documented stray-`h`-tag read-path limitation. Record two gaps as tool results:
no test exercises `replace_addressable_event` with an `is_replaceable` kind, and no
upstream NIP-01/NIP-16 text exists in this repository.

**Done when:** each absence has a real command and its real output.

## Step 4 — Draft the node

Write the file against `templates/concept.md`'s required sections, with `type: layers`,
`status: draft`, `origin: launchpad`. Disambiguate against parameterized-replaceable
(#1163, unmerged — no relationship edge to it) in the Definition. Relationships only to
ids grepped from the merged-ids list. Scope and omissions carries both required parts.

**Done when:** every substantive body claim has a matching ledger entry, and every FACT
cites a file opened in step 1–3.

## Step 5 — Validate, stamp, commit

`python3 launchpad/project-intelligence/corpus/validate.py` exits 0. Complete self-review.
Then the unittest stamp as sole foreground command at `timeout: 600000`, ending `OK`.
Then `git add` + `git commit -s`. No push, no PR.

**Done when:** validator exits 0, suite ends `OK`, one commit exists on the branch.

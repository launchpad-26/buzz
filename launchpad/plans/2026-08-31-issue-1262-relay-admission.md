# Plan: issue #1262 — platforms/relay/admission corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/relay/admission.md` does not exist; no `platforms/`
  directory exists at all on `origin/launchpad` yet (confirmed: `ls` on
  `launchpad/docs/corpus/` shows only `AGENTS.md`, `README.md`, `architecture/`,
  `schema/`, `standards/`, `templates/`).
- `architecture-flows-event-ingestion` (`launchpad/docs/corpus/architecture/flows/event-ingestion.md`)
  already documents the full ordered write-path ingest pipeline in
  `crates/buzz-relay/src/handlers/ingest.rs` step by step (community write fence,
  categorical rejections, signature/timestamp checks, pubkey match, scope check,
  channel resolution/membership, storage, fan-out).
- `architecture-flows-historical-query` and `architecture-flows-search-query`
  already document the read-path pre-DB authorization gates
  (`p_gated_filters_authorized`, `engram_filters_authorized`,
  `author_only_filters_authorized`) in `crates/buzz-relay/src/handlers/req.rs`.
- `crates/buzz-auth/src/access.rs` defines `check_read_access`/`check_write_access`/
  `ChannelAccessChecker`, but a repo-wide grep shows these are never called from
  anywhere outside `buzz-auth` itself — dead/unwired code, not the live admission
  mechanism. Excluded from this node to avoid a FACT built on unused code.
- The templates directory has no `platforms`-specific template; per prior batch
  precedent (this Feature's earlier sibling tasks), documents under `platforms/**`
  use `type: platforms` as an inference, since `node.schema.json`'s `type` enum
  includes `platforms` with no finer subtype.
- The issue's Definition-of-Done bullets ("states responsibility and well-defined
  interface/boundary", "names dependencies and collaborators", "links source
  implementation and tests", "explains only component-level behavior") map almost
  verbatim onto `templates/component.md`'s required-sections shape (Responsibility,
  Public interface, Dependencies, Boundary), even though that template's own
  front matter prescribes `type: implementation` — this node follows the
  `platforms/**` path convention for `type` instead, and borrows only the section
  shape from `component.md`.

## STEP 1 — Confirm scope and boundary against existing flow nodes

Read `event-ingestion.md`, `historical-query.md`, `search-query.md` in full to
confirm which admission mechanics they already own, so this node references
rather than repeats their step-by-step account. Done when the boundary between
"admission as a cross-cutting component" (this node: what the functions are, what
they decide, who calls them) and "admission as one step in an ordered flow"
(those nodes: the full pipeline) is written down explicitly in this node's own
Boundary section.

## STEP 2 — Read the real admission-mechanics source

Read `crates/buzz-relay/src/handlers/ingest.rs` (`required_scope_for_kind`,
`check_channel_membership`, `check_token_channel_access`, the moderation
ban/timeout re-check, the `is_serving_active` write fence call site),
`crates/buzz-db/src/store/deletion.rs` (`is_serving_active`),
`crates/buzz-relay/src/handlers/req.rs` (the read-path scope check at
`handle_req`, `p_gated_filters_authorized`), and `crates/buzz-auth/src/scope.rs`
(`Scope`). Done when every function this node names has been opened and its
real signature/behavior confirmed, not assumed from the ingestion node's prose.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/admission.md` using
`component.md`'s section shape (Responsibility, Public interface table,
Dependencies, Boundary, Relationships, Scope and omissions), front matter
`type: platforms`, `status: draft`, `origin: launchpad`, evidence citing only
opened sources. Relationships: `part-of` → `architecture-containers-relay`,
`references` → `architecture-flows-event-ingestion`,
`architecture-flows-historical-query`, `architecture-flows-search-query` (all
four confirmed present in this worktree, which is checked out from
`origin/launchpad`). Done when every DoD bullet in #1262 is satisfied by a
named section.

## STEP 4 — Validate and diff-isolate

Run the corpus unit tests, then run `validate.py` twice — once with the new file
present, once with it stashed — and confirm the FAIL set is identical (no new
FAIL introduced). Done when both runs are compared and the diff is empty.

## STEP 5 — Commit

Two separate Bash calls: the bare unittest-discover command, then
`git add` + `git commit -s`. Done when the commit succeeds or the two-retry
rule in the dispatch brief is exhausted.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` → identical FAIL set with and without this file.
- Every evidence citation points to a file actually opened during Step 2.
- Every declared relationship target resolves against this worktree (== `origin/launchpad`).

## OPEN

- Whether a future `platforms`-specific template (once authored) will ask for a
  different section shape than the `component.md` borrow used here — this node
  may need reshaping when that template lands.
- Whether `check_read_access`/`check_write_access`/`ChannelAccessChecker` in
  `buzz-auth::access` are dead code, reserved-for-future-use, or a
  not-yet-wired parallel path — not resolved here; flagged as a gap in this
  node's own Scope and omissions rather than guessed at.

## LEFT OUT

- Re-documenting the full ordered ingest pipeline (owned by
  `architecture-flows-event-ingestion`).
- Re-documenting the full ordered query/subscription flow (owned by
  `architecture-flows-historical-query` and `architecture-flows-search-query`).
- NIP-42/NIP-98 authentication mechanics themselves (a distinct concern from
  authorization/admission; owned by `architecture-flows-websocket-authentication`
  and `crates/buzz-auth/src/nip42.rs` / `nip98.rs`, not opened for this node).
- The per-kind structural validators inside `ingest_event_inner` (already an
  explicit, named gap in `architecture-flows-event-ingestion`).

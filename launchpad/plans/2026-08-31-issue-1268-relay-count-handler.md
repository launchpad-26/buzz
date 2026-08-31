# Plan: issue #1268 — document platforms/relay/count-handler

## ALREADY TRUE

- Issue #1268's DoD requires exactly one hand-authored canonical corpus node
  at `launchpad/docs/corpus/platforms/relay/count-handler.md`, schema-valid,
  evidence-cited, checked against a recorded revision, and scoped to
  component-level behavior (not the whole platform).
- `launchpad/docs/corpus/platforms/relay/count-handler.md` does not yet
  exist; `platforms/` does not yet exist as a directory in this worktree.
- `node.schema.json` requires `id`, `type`, `status`, `origin`, `audiences`,
  `evidence`; `type` is a closed enum with no `platforms`-specific member
  distinct from the others — per prior batch convention (finding #4),
  `type: platforms` is used for `platforms/**` documents, an INFERENCE
  borrowing `templates/component.md`'s section shape since no
  platforms-specific template exists yet.
- `launchpad/docs/corpus/architecture/flows/historical-query.md`
  (`id: architecture-flows-historical-query`) already exists on
  `origin/launchpad` and explicitly scopes OUT `POST /count` /
  `crates/buzz-relay/src/handlers/count.rs` in its own Scope and omissions
  section, naming it as sharing filter-authorization/access-resolution code
  but having "different fast-path/fallback semantics" — confirming this node
  should `references` that flow node rather than re-document the shared REQ
  pipeline pieces (auth, p-gated/engram/author-only filter gates, channel
  access resolution) that node already covers.
- The real COUNT handler lives in two places: the WS `COUNT` verb
  (`crates/buzz-relay/src/handlers/count.rs::handle_count`, dispatched from
  `crates/buzz-relay/src/connection.rs:618-638`) and the HTTP bridge
  `POST /count` (`crates/buzz-relay/src/api/bridge.rs::count_events` /
  `count_events_authed`, lines ~1499-1800ish). Both were read in full.
- Investigated and will cite: `crates/buzz-relay/src/handlers/req.rs` (shared
  helpers: `filter_fully_pushable`, `filter_can_match_author_only_kinds`,
  `filter_can_match_shared_gated_kinds`, `filter_can_match_result_gated_kinds`,
  `result_gated_count_safe_for_pushdown`, `apply_count_fallback_limit`,
  `count_fallback_exceeded`, `COUNT_FALLBACK_CANDIDATE_LIMIT`), `crates/
  buzz-core/src/kind.rs` (gated-kind constants), `crates/buzz-db/src/store/
  event.rs` (`count_events_routed`, `query_events_routed_bounded` — bounded-
  only replica routing, never covered-arm), `crates/buzz-relay/src/
  protocol.rs` (COUNT wire format, `RelayMessage::count`), `crates/
  buzz-relay/src/nip11.rs` (`SUPPORTED_NIPS` does NOT list 45, though COUNT
  is implemented — a real, citable discrepancy), `crates/buzz-db/src/
  runtime/tests.rs::count_events_routed_is_bounded_only` (ignored, needs
  Postgres, pins the bounded-only routing rule).
- Repository revision for provenance: `git rev-parse HEAD` at worktree
  creation = `131b02f989684117d9ab1dd426f1673fa638e523`.

## STEP 1 — Confirm scope boundary against historical-query.md

Re-read `historical-query.md`'s Scope/omissions once more while drafting to
make sure every claim this node makes about *shared* REQ-pipeline mechanics
(auth requirement, p-gated/engram/author-only filter gates, channel-access
resolution/repair) is stated only briefly, with a `references` relationship
pointing at `architecture-flows-historical-query`, rather than re-derived
from scratch. Done when the node's Boundary/Scope section names that flow
node explicitly instead of duplicating its evidence.

## STEP 2 — Draft front matter and body

Write `launchpad/docs/corpus/platforms/relay/count-handler.md` with:
`type: platforms`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer]`, a commit-citation provenance FACT, and one
evidence entry per substantive claim (WS vs HTTP entry points and their
distinct trigger/response shape; the shared pre-DB gates reused from `req.rs`;
the fast-path exact-count pushability decision via `filter_fully_pushable`
plus the three additional per-COUNT existence-leak guards for author-only,
shared-gated and result-gated kinds; the bounded-candidate fallback with its
5,000-row budget and hard rejection past it; the bounded-only replica-routing
rule that never uses the covered arm; the WS-only scoped-token channel
narrowing that the HTTP path does not perform; the NIP-45-not-advertised
discrepancy). Body follows `templates/component.md`'s section shape
(Responsibility / Public interface / Dependencies / Boundary / Relationships
/ Scope and omissions), adapted for a handler-pair rather than a whole crate.
Done when every DoD bullet has a corresponding section and every claim has a
citation to a file actually opened above.

## STEP 3 — Declare relationships

Add `relationships: [{type: references, target: architecture-flows-historical-query}]`.
Confirm that id resolves on `origin/launchpad` (already read above — it does).
No other corpus node in this batch is confirmed merged on `origin/launchpad`,
so no further relationships are declared. Done when the only declared target
is one personally confirmed to resolve on `origin/launchpad`.

## STEP 4 — Validate zero new FAILs

Run `python3 launchpad/project-intelligence/corpus/validate.py` with the new
file present, then temporarily move it out, re-run, and diff the FAIL sets —
confirm identical, then restore the file. Done when the new file contributes
zero new FAIL lines.

## STEP 5 — Earn the commit gate

Run the corpus unittest command alone, then stage + commit with `-s`. Retry
once per finding #6 if the stamp check refuses.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAIL
  lines versus the pre-existing baseline.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` —
  must print `OK`, run as the sole content of its own Bash call.
- Every DoD bullet in issue #1268 satisfied; every FACT citation opened and
  read; the one declared relationship target confirmed present on
  `origin/launchpad`.

## OPEN

- Whether the HTTP bridge `/count` path's lack of scoped-token channel
  narrowing (present only in the WS handler) is deliberate — because NIP-98
  bridge auth does not carry the same scoped-token concept as a WS
  connection — or a latent gap, was not settled by reading `count.rs` and
  `bridge.rs` alone; the node states the code-level asymmetry as fact and
  flags the "why" as unverified rather than asserting a cause.
- Whether NIP-45 not appearing in `SUPPORTED_NIPS` (`crates/buzz-relay/src/
  nip11.rs:15`) despite COUNT being implemented is an intentional omission or
  an oversight was not resolved; stated as an observed fact only.

## LEFT OUT

- Re-documenting the shared REQ-pipeline auth/access mechanics already owned
  by `architecture-flows-historical-query` (auth, p-gated/engram/author-only
  gates, channel membership cache/repair) — referenced, not duplicated.
- NIP-50 search-filter handling — owned by `search-query.md`, not touched by
  COUNT's own code paths.
- Deep investigation of `buzz-auth`'s scoped-token model beyond what
  `count.rs`/`bridge.rs` themselves reveal — left as an OPEN item above
  rather than expanded into a second concept.

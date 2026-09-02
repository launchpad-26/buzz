# Plan: issue #1282 — platforms/relay/req-handler corpus node

## ALREADY TRUE

- Issue #1282 (parent Feature #614) asks for exactly one new file,
  `launchpad/docs/corpus/platforms/relay/req-handler.md`, documenting the
  relay's REQ handler module.
- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad --
  launchpad/docs/corpus/platforms/` — empty output) and no
  `platforms-specific` template exists in `launchpad/docs/corpus/templates/`.
  Per known finding #4, sibling batch tasks under `platforms/**` have settled
  on `type: platforms` in front matter, borrowing `component.md`'s section
  shape as the closest existing template (Responsibility / Public interface /
  Dependencies / Boundary / Relationships / Scope and omissions).
- `launchpad/docs/corpus/architecture/flows/historical-query.md` (id
  `architecture-flows-historical-query`) and
  `launchpad/docs/corpus/architecture/flows/search-query.md` (id
  `architecture-flows-search-query`) already exist on `origin/launchpad` and
  document the end-to-end WS-REQ-and-HTTP-/query request/response flow
  (trigger, auth, per-filter query construction, delivery, termination) in
  deep, already-cited detail, including most of `handle_req`'s own body.
  Duplicating that would violate the "one independently maintainable idea"
  rule in `launchpad/docs/corpus/AGENTS.md`.
- Reading `crates/buzz-relay/src/handlers/req.rs` (2374 lines) shows it is
  **not only** the WS REQ handler: of its ~24 top-level functions, only
  `handle_req` is called from the WS message dispatcher
  (`crates/buzz-relay/src/connection.rs:612`). Fourteen more are `pub` or
  `pub(crate)` and are reused directly by `crates/buzz-relay/src/api/bridge.rs`
  (HTTP `/query` and `/count`) and `crates/buzz-relay/src/handlers/count.rs`
  (WS `COUNT`) — e.g. `build_event_query_from_filter`,
  `filter_fully_pushable`, the three sensitive-kind gate functions, and the
  channel-scope/access-repair helpers. This shared-toolkit role, and the
  handler's own internal dispatch order (auth/scope gate → channel
  resolution/access-repair → sensitive-kind gates → search-vs-historical
  branch → subscription-registry replace-on-resub → 3-phase filtered read
  pipeline), is exactly the "handler-level dispatch mechanics" ground the two
  flows nodes do not detail — they cite `req.rs` for the request/response
  flow but do not describe the module as a component with its own public
  surface and consumers.

## STEP 1 — Confirm target file does not exist and gather structural evidence

Done: `launchpad/docs/corpus/platforms/relay/req-handler.md` is absent; read
`node.schema.json`, `AGENTS.md`, `templates/component.md`, both existing flows
nodes, `req.rs` in full structurally (function list + key sections),
`connection.rs`'s dispatch branch, `subscription.rs`'s
`register_scoped`/`register_channels_scoped`/`register_with_scope`, and
grepped every external caller of `req.rs`'s `pub`/`pub(crate)` items across
`bridge.rs` and `count.rs`. Confirmed `buzz-relay/Cargo.toml` declares every
crate dependency the module imports (buzz-core, buzz-db, buzz-pubsub,
buzz-auth, nostr, hex, futures-util, tracing, metrics, tokio, uuid).

## STEP 2 — Draft the node

Front matter: `id: platforms-relay-req-handler`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer,
reviewer]`. Body follows `component.md`'s shape (Purpose, Responsibility,
Public interface, Dependencies, Boundary, handler-level dispatch mechanics,
Relationships, Scope and omissions), scoped explicitly away from the
request/response flow content the two flows nodes already own.

`relationships`: `references` targeting `architecture-flows-historical-query`
and `architecture-flows-search-query` (both confirmed present on
`origin/launchpad`) — this node cites them as the flow-level detail it does
not restate, per the `references` type's directionality ("source cites
target as supporting context; no ownership or currency dependency implied").

## STEP 3 — Corpus-validate: confirm zero new FAILs

Run `validate.py` with the new file present, then with it moved aside, and
diff the FAIL sets — must be identical (the ~21-23 pre-existing FAILs on a
clean checkout).

## STEP 4 — Earn the commit gate

Run the corpus unittest suite as the sole content of one Bash call, then
`git add` + `git commit -s` as a second, separate call, both `cd`-prefixed to
the worktree.

## STEP 5 — Verify

Re-read the diff against every Definition of Done bullet in #1282; re-open
every cited file/line one more time; confirm the validate.py FAIL-set
comparison from STEP 3 still holds.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — new file
  contributes zero new FAIL lines (compared file-in vs. file-out).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
  -p "test_*.py"` — must report `OK`, as the sole content of its own Bash
  call.
- Every DoD bullet in issue #1282 satisfied by the drafted body.

## OPEN

- Whether `type: platforms` is the final settled convention for this subtree
  is itself an inference (finding #4) — no `platforms`-specific template has
  landed yet, so this node may need reshaping once one does (same
  "write it now, expect a later reshape" posture `AGENTS.md` states for any
  node written ahead of its per-type standard).

## LEFT OUT

- Re-describing the end-to-end historical-query / search-query request flows
  — already owned by the two existing `architecture-flows-*` nodes, cited via
  `references` rather than duplicated.
- The `COUNT` / `/count` flow itself (`handlers/count.rs`'s own trigger,
  termination, fallback semantics) — it is named here only as a *consumer* of
  `req.rs`'s shared toolkit functions, not documented as its own flow.
- Any change to runtime behavior; this is a documentation-only node.

# Plan: issue #1284 — document platforms/relay/subscription-registry.md

## ALREADY TRUE

- `crates/buzz-relay/src/subscription.rs` exists and defines `SubscriptionRegistry`,
  a `DashMap`-backed, community-scoped registry of active REQ subscriptions with
  five in-memory fan-out indexes (`subs`, `channel_kind_index`,
  `channel_wildcard_index`, `global_kind_index`, `global_p_kind_index`,
  `global_wildcard_index`).
- `crates/buzz-relay/src/state.rs` holds it as `AppState.sub_registry: Arc<SubscriptionRegistry>`,
  constructed once via `SubscriptionRegistry::new()`.
- Callers already identified by grep: `handlers/req.rs` (register), `handlers/close.rs`
  (remove_subscription), `handlers/event.rs` (fan_out_scoped), `connection.rs`
  (remove_connection), `handlers/side_effects.rs` (remove_channel_subscriptions_scoped,
  channel_subscriber_conns_scoped), `main.rs` (per_community_subscriptions).
- `launchpad/docs/corpus/architecture/flows/live-fanout.md` (id
  `architecture-flows-live-fanout`) already documents `fan_out_scoped`'s role in the
  live fan-out flow in detail — this node must reference it, not restate it.
- No `launchpad/docs/corpus/platforms/` directory exists yet on `origin/launchpad`;
  sibling issues #1282 (`platforms-relay-req-handler`) and #1264
  (`platforms-relay-close-handler`) are drafted locally (unmerged) using
  `type: platforms`, borrowing `templates/component.md`'s section shape — this node
  follows the same convention for consistency, per known finding #4.
- Target file `launchpad/docs/corpus/platforms/relay/subscription-registry.md` does
  not exist yet.
- `python3 launchpad/project-intelligence/corpus/validate.py` has a pre-existing
  baseline of FAILs on a clean `origin/launchpad` checkout unrelated to this task.

## STEP 1 — Read and confirm scope

Read issue #1284's DoD checklist verbatim. Read `node.schema.json`,
`launchpad/docs/corpus/AGENTS.md` (Creating a node, §309-351), and
`templates/component.md` in full. Confirm no existing corpus node documents
`SubscriptionRegistry` specifically. **Done when:** template/schema fully read,
no duplicate node found.

## STEP 2 — Investigate the real data structure and its callers

Read `crates/buzz-relay/src/subscription.rs` in full (already done: struct fields,
every public method, its test module). Grep every call site of `sub_registry.` and
`SubscriptionRegistry` across `crates/buzz-relay/src` (already done: req.rs, close.rs,
event.rs, connection.rs, side_effects.rs, main.rs). Confirm `dashmap` is a real
Cargo.toml dependency of `buzz-relay`. **Done when:** every public method has at
least one real call-site citation or is marked test-only/internal.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/relay/subscription-registry.md` using
`component.md`'s section shape (Purpose, Responsibility, Public interface,
Dependencies, Boundary, Relationships, Scope and omissions), front matter:
`id: platforms-relay-subscription-registry`, `type: platforms`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Declare
`references: architecture-flows-live-fanout` (confirmed present on
`origin/launchpad`). Every FACT cites an opened file/line; no INFERENCE unless
actually reasoning beyond direct evidence. **Done when:** every DoD bullet in
#1284 has a corresponding section/citation in the drafted file.

## STEP 4 — Verify zero new validate.py FAILs

Run `validate.py` on the clean origin/launchpad baseline (file removed/stashed),
record the FAIL set; restore the file; re-run; diff the two FAIL sets are
identical. **Done when:** diff is empty.

## STEP 5 — Test, commit

Run the corpus unittest suite as its own sole Bash call; confirm `OK`. Then, in a
second separate Bash call, `git add` both new files and commit with `-s`.
**Done when:** commit succeeds (or BLOCKED is reported per finding #7 after one
retry).

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK
- `validate.py` new-FAIL diff → empty
- Every evidence citation opened and read directly (no RepoQL-only citations)
- Commit gate: `git commit -s` succeeds without "COMMIT BLOCKED"

## OPEN

- Whether `platforms-relay-req-handler` / `platforms-relay-close-handler` land
  first, after, or never — this node deliberately declares no relationship toward
  either, since both are unmerged and per AGENTS.md step 9 a relationship target
  must resolve on the branch being merged into.

## LEFT OUT

- No changes to `crates/buzz-relay/src/subscription.rs` or any other runtime code.
- No second hand-authored corpus document.
- No relationship to the still-unmerged req-handler/close-handler sibling nodes.
- No fix to the pre-existing validate.py FAIL baseline.

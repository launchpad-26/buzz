# Issue #699 — corpus doc: capabilities/activity/activity-feed.md

ALREADY TRUE: `node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and the
`corpus-template-capability` template (`launchpad/docs/corpus/templates/capability.md`)
are merged on `launchpad`. `launchpad/docs/corpus/capabilities/` does not exist yet —
this is the first `type: capabilities` instance node in the corpus. Sibling batch
issues #700 (mentions-feed), #701 (needs-action) and #702 (pulse) target the same
`capabilities/activity/` directory but are separate tasks/nodes, not this one's scope.
In code: `crates/buzz-db/src/store/feed.rs` implements three distinct feed categories
(`query_mentions`, `query_needs_action`, `query_activity`); `query_activity` and its
replica-routed wrapper `query_feed_activity_routed` are the "activity" category
specifically — recent stream messages, forum posts, and agent job events (kinds
9/40002/45001/43001/43003/43004, per `buzz-core/src/kind.rs`) across accessible
channels, explicitly excluding
workflow-execution kinds "to avoid noise" (feed.rs doc comment). `buzz-cli`'s `feed get
--types activity` (`crates/buzz-cli/src/commands/feed.rs`, `FeedCmd::Get` in
`crates/buzz-cli/src/lib.rs:978`) and the relay bridge's `feed_types` extension
(`crates/buzz-relay/src/api/bridge.rs:332` `extract_feed_types`, dispatch at
`:1213`-`:1223`) are the interface; the desktop Home feed
(`desktop/src/shared/api/types.ts` `HomeFeed.activity`, `FeedItemCategory: "activity"`,
`desktop/src/features/home/lib/inbox.ts` `categoryLabelFor` → `"Activity"`) is the
consumer. This is distinct from `desktop/src/features/pulse/` (issue #702's subject —
a separate screen), and distinct from mentions/needs-action (issues #700/#701).

STEP 1 — confirm scope boundary against the three sibling issues (#700/#701/#702) and
against `desktop/src/features/pulse/`, so this node covers only the `activity`
feed-type/category, not the whole Home Feed or Pulse. RUNS HERE (already done during
research: `gh issue view 700/701/702`, `grep` for `pulse` under `desktop/src`).

STEP 2 — write `launchpad/docs/corpus/capabilities/activity/activity-feed.md` against
`corpus-template-capability`'s required sections (Capability statement, Maturity,
Boundary, Relationships, Scope and omissions), with front matter `id
capabilities-activity-activity-feed`, `type: capabilities`, `status: draft`, `origin:
launchpad`, `audiences: agent, developer, reviewer`. Cite `feed.rs`'s
`build_activity_query`/`query_activity`/`query_feed_activity_routed`, `bridge.rs`'s
`extract_feed_types` and dispatch arm, `buzz-cli`'s `feed.rs`/`lib.rs` `FeedCmd`, and
`crates/buzz-cli/TESTING.md`'s `6.10 Feed` live-test section as maturity evidence.
State the CLI-default nuance precisely: plain `buzz feed get` (no `--types`) sends a
bare `#p`-tag Nostr filter with no `feed_types` key, so it never reaches
`query_activity` — only `--types activity` (or `agent_activity`, canonicalized to
`activity` in bridge.rs:1176) does. `relationships`: `references` toward
`architecture-containers-relay` and `architecture-containers-cli` (both merged,
`status: draft`, confirmed present in this worktree's `origin/launchpad` checkout).

STEP 3 — run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0 against the full tree.

STEP 4 — commit (plan + doc) once
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` reports OK. Per this batch's process, do NOT push and do NOT open a PR —
leave the commit local on `task/699-activity-feed` for a later integration PR.

PARALLEL: none — single hand-authored file, one worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0.
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` must report OK to earn the commit verification stamp. `review-code` /
`review-adjudicate` are explicitly deferred to the later integration phase — this
worktree performs a self-review instead (see report).

BUDGET: single document, no code changes, no test changes — small.

OPEN: the capability template's own precedent (declining `relationships` to its own
unmerged siblings) does not apply here in the same way, because
`architecture-containers-relay` and `architecture-containers-cli` genuinely are already
merged on `origin/launchpad` — confirmed by reading them in this worktree, which was
freshly fetched from `origin/launchpad`. Whether `references` is the right relationship
type (vs. no relationship at all, matching the template's own caution) is a judgment
call; `references`' directionality ("cites target as supporting context; no ownership
or currency dependency implied" per `relationships.schema.json`) fits a capability
citing the containers that realize it, per the template's own guidance section.

LEFT OUT: no relationship to sibling nodes #700/#701/#702 (mentions-feed,
needs-action, pulse) — none are merged yet, and per `AGENTS.md` step 9 a target must
resolve against the merge-target branch, not the author's own worktree. No
`generated/` index files touched — none exist yet to regenerate. Full production code
review of `feed.rs`/`bridge.rs` beyond what's needed to support cited claims is out of
scope; this is a documentation task, not an implementation change.

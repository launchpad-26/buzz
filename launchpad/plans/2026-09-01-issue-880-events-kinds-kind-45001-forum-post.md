Issue #880 — Corpus node: events/kinds/kind-45001-forum-post.md
Stated size: no `Size` line on issue #880; the dispatching task brief explicitly caps this as "a small single-document task"  →  cap: 5 steps

ALREADY TRUE  (verified against git and the repo, not notes)
  Worktree `__worktrees/task-880-events-kinds-kind-45001-forum-post` exists, checked out on
    branch `task/880-events-kinds-kind-45001-forum-post` from `origin/launchpad`, HEAD
    `a8b5021efb92264e724366d08b47b2a3839eb90a` (`git rev-parse HEAD`).
  Target file `launchpad/docs/corpus/events/kinds/kind-45001-forum-post.md` does not exist —
    `find launchpad/docs/corpus -iname "*kind*" -o -iname "*event*"` returns only
    `architecture/flows/event-ingestion.md`, `architecture/flows/http-event-submission.md`,
    `architecture/principles/event-driven-extension.md`, `architecture/principles/signed-events.md`,
    and `templates/event-kind.md` — no `events/` or `events/kinds/` subtree exists yet.
  `crates/buzz-core/src/kind.rs:550` defines `pub const KIND_FORUM_POST: u32 = 45001;` under a
    `// Forum / social (45000–45999)` heading whose preceding comment states
    `// V1 used addressable range (30001–30003) — wrong.`
  `crates/buzz-sdk/src/builders.rs:284-296` defines `build_forum_post`, the authoritative wire-shape
    source: one `h` tag (channel id), optional deduped `p`-tag mentions (capped at
    `crate::mentions::MENTION_CAP = 50`), optional raw `imeta` tags, plaintext content capped at
    64 KiB client-side (`SdkError::ContentTooLarge`), `.allow_self_tagging()`. No `e` tag is emitted
    (it is the thread root) — contrast with the sibling `build_forum_comment` (kind 45003, line
    300), which adds NIP-10 `e` tags via `thread_tags`.
  `crates/buzz-relay/src/handlers/ingest.rs` confirms server-side facts: `KIND_FORUM_POST` maps to
    `Scope::MessagesWrite` (line 482-484), is in `requires_h_channel_scope` (line 716-718), is
    absent from `AUTHOR_ONLY_KINDS`/`P_GATED_KINDS`/`SHARED_GATED_KINDS`/`RESULT_GATED_KINDS` in
    `kind.rs`, and the relay enforces a generic 256 KB `MAX_EVENT_CONTENT_BYTES` cap for any kind
    (line 2233) independent of the SDK's stricter 64 KiB client-side cap.
  `schema/schema.sql:223-227`'s `search_tsv` generated column excludes kinds
    `1059, 30179, 30300, 30350, 30622, 44100, 44101, 44200` from full-text search; 45001 is not in
    that list, so forum posts are NIP-50-searchable.
  `launchpad/docs/corpus/templates/event-kind.md` is a validated corpus node (front matter
    `id: corpus-template-event-kind`, `status: active`) — not excluded from `validate.py` (only the
    top-level `schema/` dir is excluded per `launchpad/project-intelligence/corpus/validate.py`'s
    `EXCLUDED_TOP_LEVEL_DIRS`) — so this id resolves in the loaded corpus and is a legitimate
    `implements` relationship target per that template's own §9 guidance.
  `docs/nips/*.md` (16 files) contains no NIP proposal document naming kind 45001, 45002, or 45003 —
    forum post is a Buzz-custom kind with no external spec document.

STEP 1  Draft `launchpad/docs/corpus/events/kinds/kind-45001-forum-post.md` with schema-valid       [independent]  ← RUNS HERE
        front matter (id `events-kinds-kind-45001-forum-post`, type `interfaces-events`, status
        `draft`, origin, audiences, evidence ledger with correctly classed FACT/INFERENCE/
        TEAM_KNOWLEDGE entries, one `implements` relationship to `corpus-template-event-kind`) and
        body sections covering: kind identity/number, classification (regular/persistent — not
        ephemeral, not replaceable, not parameterized-replaceable, per `kind.rs`'s own helpers),
        required/optional tags (`h` required; `p` mentions and `imeta` optional; no `e` tag),
        content shape (plaintext, 64 KiB SDK cap / 256 KB relay cap), access control (unlisted in
        every gated-kinds set — world-readable within channel membership), producers/consumers
        (`buzz-cli messages post --kind 45001` → `build_forum_post`; feed/mentions/activity-feed
        SQL in `buzz-db/src/store/feed.rs`), persistence/fanout/search/audit treatment, a worked
        example JSON event, and versioning history (the 30001–30003 → 45001 renumbering).
        done when: the file exists, `python3 -c "import yaml,sys; yaml.safe_load(open(sys.argv[1]).read().split('---')[1])" launchpad/docs/corpus/events/kinds/kind-45001-forum-post.md`
        parses without error, and every Definition-of-done bullet from `gh issue view 880` has a
        corresponding section or explicit statement in the file (checked by re-reading the issue
        body against the draft line by line).

STEP 2  Run the corpus validator and confirm the new node introduces zero additional errors.        [needs 1]
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` runs, and the set of
        FAIL lines it prints is exactly the 21 known pre-existing errors from issue #1951
        (architecture-containers-postgres, architecture-context-human-user,
        architecture-flows-event-ingestion, architecture-flows-workflow-execution,
        architecture-principles-community-is-security-boundary, and the `corpus-template-*` files)
        plus zero new ones — confirmed by diffing the printed error set against that known list.

STEP 3  Run the corpus test-suite gate as its own isolated command.                                 [needs 1]
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        prints `OK` with no failures or errors.

STEP 4  Commit the new corpus node and this plan file together.                                     [needs 2, 3]
        done when: `git commit -s` succeeds (not rejected for a missing gate stamp) and
        `git show --stat HEAD` lists exactly
        `launchpad/docs/corpus/events/kinds/kind-45001-forum-post.md` and
        `launchpad/plans/2026-09-01-issue-880-events-kinds-kind-45001-forum-post.md` as the
        changed files.

PARALLEL  None of these four steps can run as independent parallel subagents: step 1 is the sole
          content-producing step every later step depends on (validate, test, commit all read the
          file step 1 writes), so 2/3/4 are strictly sequential after 1. Steps 2 and 3 could in
          principle run concurrently (they read the same tree but do not write it), but the task
          brief requires step 3 (the unittest gate) to run as the sole command in its own tool call
          immediately before the commit, so this plan keeps 2 then 3 sequential for auditability
          rather than claiming a parallelism that would complicate the gate-then-commit ordering.

GATES     No `review-code`/`review-tests` — this is a documentation-only corpus node, no product
          code changes. `corpus-review` (the skill built specifically to review a drafted corpus
          node) is the applicable gate in general, but the dispatching task brief substitutes an
          explicit manual self-review step (re-reading the diff against the issue's DoD checklist
          and re-opening every cited file/line) instead of invoking it — that is a deliberate
          instruction from the dispatch brief, not an omission. `qa` explore mode does not apply:
          there is no runtime interface (CLI, API, UI) this change adds or touches to exercise.

BUDGET    Step 1 is the step most likely to eat the budget — writing an evidence-backed claim for
          every required section (especially access-control and persistence/fanout/search/audit
          treatment, which the event-kind template itself calls "the one most often reasoned about
          rather than read") requires re-opening several source files rather than summarizing from
          memory.

OPEN      Whether kind 45001 should eventually get its own `docs/nips/NIP-XX.md` proposal document
          (like `NIP-AM.md` for kind 44200), versus staying spec'd only by `kind.rs` + the SDK
          builder, is not decided here — `corpus-template-event-kind.md` itself names this as an
          unfiled gap, and issue #880 does not ask this task to resolve it.
          Whether this node's `implements` edge to `corpus-template-event-kind` is the only
          relationship worth adding now, versus also linking sibling forum-vote (45002) /
          forum-comment (45003) nodes once those exist, is left for whichever task authors those
          siblings — no such node exists yet to link to.

LEFT OUT  Authoring corpus nodes for `KIND_FORUM_VOTE` (45002) or `KIND_FORUM_COMMENT` (45003) —
          issue #880's own scope is exactly one document for kind 45001; a second hand-authored
          canonical document is explicitly out of scope per its "Out of scope" section.
          Any runtime/product behavior change to forum-post handling, ingestion, or storage.
          Resolving the unsettled event-kind-vs-interface boundary that `corpus-template-event-kind.md`
          itself flags as unresolved against issue #1342 — this document states its kind-identity
          content per the event-kind template and does not adjudicate that open cross-template
          question.

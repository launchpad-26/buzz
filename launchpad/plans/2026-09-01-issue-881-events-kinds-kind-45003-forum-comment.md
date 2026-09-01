Issue #881 — task: document events/kinds/kind-45003-forum-comment.md

Stated size: small, single-document corpus task -> cap: 5 steps

ALREADY TRUE

- `launchpad/docs/corpus/events/kinds/kind-45003-forum-comment.md` does not exist.
  Checked: `find launchpad/docs/corpus/events -type f` returns nothing, and no
  `events/` directory exists anywhere under `launchpad/docs/corpus/` at
  `origin/launchpad` HEAD `a8b5021efb92264e724366d08b47b2a3839eb90a`. This will be
  the first node under `events/`.
- `crates/buzz-core/src/kind.rs` defines `KIND_FORUM_COMMENT: u32 = 45003` (line 554),
  in a block comment "Forum / social (45000–45999)" alongside `KIND_FORUM_POST` (45001)
  and `KIND_FORUM_VOTE` (45002), with a block-level note "V1 used addressable range
  (30001–30003) — wrong."
- `is_ephemeral`, `is_replaceable`, `is_parameterized_replaceable` (kind.rs lines
  769-785) all evaluate false for 45003 — it is outside every numeric band those
  helpers check, so by Buzz's own classification it is a plain regular/persistent
  kind, not ephemeral/replaceable/parameterized-replaceable.
- 45003 appears in none of `AUTHOR_ONLY_KINDS`, `P_GATED_KINDS`, `SHARED_GATED_KINDS`,
  or `RESULT_GATED_KINDS` (confirmed by grep across kind.rs) — no special read gate
  beyond ordinary channel-membership access.
- `buzz-relay/src/handlers/ingest.rs` requires an `h` tag for kind 45003
  (`requires_h_channel_scope`, tested at line ~3665) and assigns it
  `Scope::MessagesWrite` (line 484) for the write-authorization check.
- `buzz-relay/src/handlers/ingest.rs::validate_forum_vote_target` (line ~1219) shows
  45003 (alongside 45001) is a legal vote target for kind 45002 votes, and must share
  the vote's channel.
- `buzz-sdk/src/builders.rs::build_forum_comment` (line 301) is the canonical event
  builder: tags an `h` (channel), NIP-10-style `e` thread tags via `thread_tags`
  (root+reply, or reply-only if root==parent), `p` mention tags (capped at
  `MENTION_CAP = 50`, `buzz-sdk/src/mentions.rs:38`), and optional `imeta` media
  tags; content is plaintext capped at 64 KiB (`check_content`); kind is
  `Kind::Custom(45003)`.
- `buzz-cli/src/commands/messages.rs` (~line 685-700) is the producer surface:
  `messages send --kind 45003 --reply-to <parent>` requires `--reply-to`
  (CLI-level validation, "`--reply-to is required for forum comments (kind 45003)`")
  and calls `build_forum_comment`.
- `buzz-db/src/store/feed.rs` includes 45003 in the Home-feed mentions query
  (kind list at line 108, dedicated test `mentions_query_includes_stream_message_kind`
  at line ~849 asserting `KIND_FORUM_COMMENT` membership).
- `desktop/src/shared/constants/kinds.ts` mirrors `KIND_FORUM_COMMENT = 45003`
  (line 33), includes it in `CHANNEL_MESSAGE_EVENT_KINDS` (unread-trigger set, line
  ~93-95) and therefore `HOME_MENTION_EVENT_KINDS`, but explicitly *excludes* it from
  `CHANNEL_TIMELINE_CONTENT_KINDS` with the comment "Forum kinds (45001/45003) are
  excluded: forum channels use a different query path, not this timeline" (line
  ~135-136) — consumed instead via `desktop/src/features/forum/` (`ForumThreadPanel.tsx`,
  `ForumComposer.tsx`, `desktop/src/shared/api/forum.ts`).
- No hits for "FORUM"/"forum" anywhere under `crates/buzz-search` or
  `crates/buzz-audit` — no dedicated search/audit code path for this kind beyond
  ordinary Postgres FTS eligibility implied by its absence from `P_GATED_KINDS`
  (which is the set whose persistent members get `search_tsv` NULLed out).
- No `reply_count`/`descendant_count` hits reference `FORUM` anywhere in the repo —
  the root AGENTS.md thread-counter convention (materialized on thread-root events)
  does not apply to kind 45003; forum threading is carried by the `e`-tag pair from
  `thread_tags`, not by relay-maintained counters.
- `launchpad/docs/corpus/templates/event-kind.md` (`corpus-template-event-kind`) is
  merged on `origin/launchpad` and gives the required-sections shape for an
  event-kind instance node; `node.schema.json`'s `type` enum includes
  `interfaces-events`, the value that template's own text (section 1) says a real
  instance would carry.

STEP 1 — Draft the corpus node [independent]

Create `launchpad/docs/corpus/events/kinds/kind-45003-forum-comment.md` with
schema-valid front matter (`id: events-kinds-kind-45003-forum-comment`,
`type: interfaces-events`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`, no `relationships` — no sibling
event-kind node exists yet to point at) and a body covering, each backed by an
`evidence` entry citing the file/symbol actually opened above: kind number/name and
constant; NIP-01 range classification (regular, cross-checked against the three
`is_*` helpers); required/optional tag shape (`h`, `e` root/reply pair, `p`
mentions, `imeta`) and content shape (plaintext, 64 KiB cap); producers
(`buzz-sdk::build_forum_comment`, `buzz-cli messages send --kind 45003`);
consumers (desktop forum feature, Home-feed mentions query); authorization
(`Scope::MessagesWrite`, `requires_h_channel_scope`); persistence/access model
(regular stored event, no gated-set membership); fanout notes (unread-trigger
set but excluded from the main channel timeline); the forum-vote relationship
(45003 as a legal vote target) stated as prose since no `kind-45002-forum-vote`
node exists yet to link as a typed relationship; a worked-example JSON event; and
a scope-and-omissions section naming what was expected but not verified (no
dedicated NIP/spec document for the forum kind range beyond the inline kind.rs
comment; no `docs/nips/NIP-*.md` file exists for kind 45001-45003 at this
revision — confirmed by `ls docs/nips/*.md` not listing a forum-prefixed name).
done when: the file exists at that path, `head -40` shows parseable YAML front
matter with exactly the required fields, and every DoD bullet from issue #881's
own checklist has a corresponding section in the body.

STEP 2 — Validate against the corpus checker [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and compare its FAIL-line count against the 21 known
pre-existing failures on `origin/launchpad` (issue #1951: the five
`architecture-*` nodes plus the `corpus-template-*` files). Fix anything the
new node introduces and re-run until the new-node delta is zero.
done when: `validate.py`'s output, diffed against a baseline run on
`origin/launchpad` before this file existed, shows the same 21 pre-existing
FAIL lines and zero additional ones attributable to
`kind-45003-forum-comment.md`.

STEP 3 — Run the corpus test suite [needs 2]

Run, as the sole command in its own shell invocation,
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
done when: the command's final line is `OK`.

STEP 4 — Commit [needs 3]

Stage exactly `launchpad/docs/corpus/events/kinds/kind-45003-forum-comment.md`
and this plan file, then `git commit -s` with a message referencing #881.
done when: `git log -1 --format=%s` names kind 45003 and #881, and
`git show --stat HEAD` lists only those two files.

STEP 5 — Self-review against the DoD checklist [needs 4]

Re-read the committed diff line by line against issue #881's Definition-of-done
checklist and re-open every cited source in the `evidence` ledger to confirm it
actually says what its `statement` claims. Confirm no second hand-authored
canonical corpus document was created, and confirm the `validate.py` delta from
step 2 is still zero at the final commit.
done when: every DoD bullet is checked off against a specific body section, and
every FACT/INFERENCE citation has been re-opened and confirmed to say what the
statement claims.

PARALLEL

None of steps 2-5 can run before their predecessor; this is a single-document
task with no independent workstream to parallelize. Step 1 is the only
`[independent]` step.

RUNS HERE: STEP 1 runs in this worktree
(/home/serina/Launchpad/buzz/__worktrees/task-881-events-kinds-kind-45003-forum-comment),
on branch task/881-events-kinds-kind-45003-forum-comment, and every later step
runs there too — there is no second workstream to isolate.

GATES

- `validate.py` exit code and FAIL-line diff against the 21 known pre-existing
  failures (step 2) — the corpus-content merge gate.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  printing `OK` (step 3) — the commit gate; if a stamp/hook rejects the commit
  with no gate stamp found, that is reported as a finding, never routed around
  with `--no-verify` or a self-authored stamp file.
- No push, no PR, no merge — out of scope per the task's own step 7.

BUDGET

One document (~150-250 lines of Markdown), one plan file, roughly 10-15 tool
calls beyond what has already been spent on research (kind.rs, ingest.rs,
builders.rs, feed.rs, kinds.ts already read). No code changes, no test-suite
runtime beyond the two gate commands above.

OPEN

- Whether a `docs/nips/NIP-*.md` proposal document should exist for the
  45000-45999 forum/social kind range before or alongside this corpus node —
  not settled by any source found, and named as a gap in the node's own
  scope-and-omissions section rather than decided here.
- Whether the 30001-30003 -> 45001-45003 renumbering inference (from the single
  block comment "V1 used addressable range (30001–30003) — wrong") maps
  one-to-one in the order stated — no commit or PR was found that states the
  mapping explicitly; the node states this as `INFERENCE`, not `FACT`.

LEFT OUT

- Creating a `kind-45001-forum-post.md` or `kind-45002-forum-vote.md` sibling
  node — each is its own task per issue #881's own out-of-scope list
  ("Creating or materially editing a second hand-authored canonical corpus
  document"); this plan documents only 45003 and mentions the other two only
  as prose context, never as a `relationships` target (neither node exists yet
  to resolve against).
- Declaring `relationships: implements -> corpus-template-event-kind` — the
  template node's own guidance (section 9) treats this as available, but
  confirming `corpus-template-event-kind` actually resolves in the loaded
  corpus at merge time, and whether the reviewing task wants that edge, is
  deferred to step 1's drafting judgment rather than pre-decided here; if
  declared, step 2's validation run is what proves it resolves.
- Any change to `crates/buzz-core/src/kind.rs`, `buzz-sdk`, `buzz-relay`, or
  desktop/mobile forum code — this is a documentation-only task; no runtime
  behavior changes.

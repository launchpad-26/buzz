Issue #879 — Corpus node: events/kinds/kind-43001-job-request
Stated size: not stated on the issue  →  cap: 5 steps (task dispatch fixed this as a small single-document task)

ALREADY TRUE  (verified against git and the worktree, not notes)
  `launchpad/docs/corpus/events/` does not exist anywhere in this worktree
    (verified: `find launchpad/docs/corpus/events -type f` errored "No such file or
    directory") and does not exist on the merge target (verified:
    `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
    `events/` path) — the target file is new, not an edit.
  `launchpad/docs/corpus/templates/event-kind.md` (id `corpus-template-event-kind`)
    is merged on `origin/launchpad` and states the required sections, evidence
    expectations, and industry model for an event-kind instance node.
  `launchpad/docs/corpus/architecture/context/ai-agent.md` (id
    `architecture-context-ai-agent`) is merged on `origin/launchpad` and its own
    Scope and omissions table names exactly this gap: "The agent job protocol's
    (`KIND_JOB_REQUEST` family) message shapes, auth-chain depth/breadth rules, and
    NIP-90-vs-Buzz rationale | A future interfaces/events-level corpus node, not yet
    authored."
  `crates/buzz-core/src/kind.rs` defines `KIND_JOB_REQUEST: u32 = 43001` (line 518)
    under the "Agent job protocol (43000-43999)" section, with sibling kinds
    KIND_JOB_ACCEPTED (43002), KIND_JOB_PROGRESS (43003), KIND_JOB_RESULT (43004),
    KIND_JOB_CANCEL (43005), KIND_JOB_ERROR (43006), and the comment "Not using
    NIP-90 kinds (5000-6999) -- Buzz requires auth chains (depth <= 3, breadth <= 10)."
  43001 is not a member of `AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`,
    `P_GATED_KINDS`, or `SHARED_GATED_KINDS` in kind.rs (grepped each list body
    directly), and `is_ephemeral`/`is_replaceable`/`is_parameterized_replaceable`
    each return false for it by range.
  `crates/buzz-relay/src/handlers/ingest.rs` places 43001 in neither
    `is_global_only_kind` nor `requires_h_channel_scope`; its channel_id is derived
    from an optional `h` tag via `extract_channel_id` (default path, ~line 2453).
  `crates/buzz-db/src/store/feed.rs` includes KIND_JOB_REQUEST (with
    KIND_JOB_PROGRESS, KIND_JOB_RESULT but not ACCEPTED/CANCEL/ERROR) in
    `build_activity_query`'s Home Feed "activity" kind filter.
  Desktop (`desktop/src/shared/constants/kinds.ts`, `inbox.ts`, `FeedSection.tsx`,
    `SearchResultItem.tsx`) and mobile (`mobile/lib/shared/relay/nostr_models.dart`,
    `activity_provider.dart`, `feed_item.dart`) already render/query kind 43001 as a
    live consumer, but `desktop/src/features/notifications/lib/sound.ts` states
    outright: "The agent job protocol (kinds 43001-43006) is defined and queryable
    but nothing emits the events yet -- buzz-acp publishes plain stream messages."
  No `docs/nips/NIP-*.md` file specifies the job protocol (grepped all 21 files
    under `docs/nips/` for "43001"/"job"; only an unrelated match in NIP-PL.md).
  `python3 launchpad/project-intelligence/corpus/validate.py` on the current
    worktree (before this node is added) is the baseline to diff against: 21 known
    pre-existing FAIL lines (issue #1951), none touching this node's path.

STEP 1  Write front matter (id, type, status, origin, audiences) and the evidence     [independent]
        ledger, citing every source already inspected above (kind.rs lines,
        ingest.rs's is_global_only_kind/requires_h_channel_scope, feed.rs's
        build_activity_query, sound.ts's no-emitter note, the absence of a
        docs/nips file, and the two relationship targets' merged status).
        done when: the file's front-matter block parses as valid YAML with exactly
        the seven schema-permitted keys, `id: events-kinds-kind-43001-job-request`,
        `type: interfaces-events`, and one evidence entry per claim used in the body.

STEP 2  Write the body per the event-kind template's nine required-section shape:    [needs 1]
        kind identity, referenced spec (none exists -- say so), range/classification
        cross-check, tag shape (h optional, no d tag, access-control set membership),
        content semantics, access control/storage, one worked-example JSON event,
        versioning (none), relationships (implements the template, references
        architecture-context-ai-agent), plus a Scope and omissions section naming
        the no-producer-yet gap and the unresolved NIP-90-vs-Buzz auth-chain detail
        as gaps rather than silence.
        done when: every one of issue #879's Definition-of-done bullets has a
        corresponding section in the body, checked line by line against the issue.

STEP 3  Run `python3 launchpad/project-intelligence/corpus/validate.py` and diff      [needs 2]  ← RUNS HERE
        its FAIL-line output against the 21-line pre-existing baseline recorded
        above.
        done when: the new node introduces zero FAIL lines beyond those 21 (a node
        that fails structurally is caught here, before anything is committed).

STEP 4  Run `python3 -m unittest discover -s                                         [needs 3]
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole
        command in its own call, confirm it prints `OK`, then stage and commit
        both files with `git commit -s`.
        done when: the unittest run prints `OK` and `git rev-parse HEAD` returns a
        commit whose tree contains both the new corpus node and this plan file.

STEP 5  Self-review: re-read the committed diff against issue #879's Definition-of-   [needs 4]
        done checklist line by line, re-open every cited file to confirm its
        evidence entry is actually supported, and re-confirm no second
        hand-authored canonical document was created.
        done when: every DoD bullet is checked off against the actual diff (not
        against memory of writing it), and `git status` shows a clean tree.

PARALLEL  None of these five steps can run as independent subagents: steps 2-5 each
  read or build on the immediately preceding step's output (front matter before
  body, body before validation, a passing validation before the commit gate, a
  real commit before self-review), and all five touch the same two files. Step 1
  is tagged [independent] only in the sense that nothing else is running
  concurrently in this worktree to conflict with it -- it still executes first in
  sequence.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (step 3) is
  the structural gate for this change; `python3 -m unittest discover -s
  launchpad/project-intelligence/corpus/tests -p "test_*.py"` (step 4) is the
  commit gate the task instructions require verbatim, run alone in its own tool
  call before any git command. No `review-*` skill or `qa` explore mode applies:
  this is a documentation-only corpus node with no runtime interface, UI, or code
  path to exercise.
BUDGET    Step 2 (writing the body) is most likely to eat the budget -- it is the
  only step synthesizing prose against nine required template sections plus the
  issue's own DoD bullets, and getting the FACT/INFERENCE/TEAM_KNOWLEDGE
  classification honest for each claim (especially the access-control and
  channel-scoping claims, which rest on reading ingest.rs's set membership rather
  than a single doc comment) takes more care than any other step.
OPEN      The issue does not decide whether the current no-producer-yet state
  (sound.ts's "nothing emits the events yet") should be stated as a limitation of
  *this* node or deferred entirely to a future producer-side node -- this plan
  states it in Scope and omissions as a gap, per the event-kind template's own
  instruction to say when a documented kind is proposed/wired but not yet live.
  The issue also does not decide whether a `docs/nips/NIP-JR.md`-style proposal
  document should exist before this corpus node, given no NIP file names the job
  protocol today -- the event-kind template treats this as optional per-kind, not
  mandatory, and this plan does not create one.
LEFT OUT  Documenting the other five job-protocol kinds (43002-43006) as their own
  corpus nodes -- issue #879 and the task instructions scope this document to
  kind 43001 only; a second concept folded in here would violate the corpus's own
  one-node-one-idea rule (`corpus-standard-atomicity`, requirement A3). Any
  generated corpus index or knowledge-crate projection touching this node --
  out of scope per the issue's own Impacted components list ("mechanical only, if
  changed"), and no such generator exists yet per AGENTS.md.

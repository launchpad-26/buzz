Issue #875 — Corpus doc: kind 39001 channel admins
Stated size: no explicit `Size` line on the issue; dispatch instructions call it a small single-document task → cap: 5 steps

(No `Size` line exists on issue #875 itself. The dispatch brief that assigned this
task explicitly capped it at 5 steps and named it "a small single-document task,"
matching every other single-node corpus task in this batch, so that cap is used
here rather than stopping to ask a question the dispatcher already answered.)

ALREADY TRUE  (verified against git and the repo tree, not notes)
  - `launchpad/docs/corpus/events/kinds/kind-39001-channel-admins.md` does not
    exist (`find launchpad/docs/corpus -type f` lists no `events/` subtree at all).
  - `launchpad/docs/corpus/templates/event-kind.md` exists and states the
    required sections for an event-kind node, even though `AGENTS.md`'s own gap
    table doesn't yet list it as landed — it is real and applicable regardless.
  - `crates/buzz-core/src/kind.rs:424` defines
    `pub const KIND_NIP29_GROUP_ADMINS: u32 = 39001;` with the doc comment
    "NIP-29: Addressable group admins list."
  - `kind.rs:452,454,784` establish `PARAM_REPLACEABLE_KIND_MIN..MAX = 30000..=39999`
    and `is_parameterized_replaceable`, so 39001 is addressable/parameterized-
    replaceable, not regular/replaceable/ephemeral.
  - 39001 is absent from `AUTHOR_ONLY_KINDS`, `RESULT_GATED_KINDS`,
    `P_GATED_KINDS`, and `SHARED_GATED_KINDS` (`kind.rs:129-215`) — no special
    read gate applies beyond ordinary channel-scoped storage access.
  - The producer is `emit_group_discovery_events` in
    `crates/buzz-relay/src/handlers/side_effects.rs:1127`, called (relay-signed)
    from `handle_edit_metadata`, `handle_put_user`, `handle_remove_user`,
    `handle_create_group`, `handle_join_request`, `handle_leave_request`,
    `moderation_notices.rs`, and `command_executor.rs`; `buzz-admin`'s
    `reconcile_channels` (`crates/buzz-admin/src/main.rs:588`) also emits it as a
    backfill/repair path.
  - Persistence is `Db::replace_addressable_event`
    (`crates/buzz-db/src/store/replaceable.rs:374`), keyed by
    `(community_id, kind, pubkey, channel_id)` with highest-`created_at`-wins and
    same-timestamp lowest-id tiebreak.
  - `grep` across `desktop/src`, `web/src`, `mobile/lib`, `crates/buzz-cli/src`,
    `crates/buzz-sdk/src` for `39001`/`GROUP_ADMINS` returns no matches — no
    client-side consumer of kind 39001 exists in this repository today.
  - No test in the repo (`buzz-relay`, `buzz-test-client`, or inline `#[cfg(test)]`
    modules) references `KIND_NIP29_GROUP_ADMINS` or the literal `39001`.

STEP 1  Draft the corpus node                                   [independent]
        Write `launchpad/docs/corpus/events/kinds/kind-39001-channel-admins.md`
        with schema-valid front matter (`id: events-kinds-kind-39001-channel-admins`,
        `type: interfaces-events`, `status: draft`, `origin: launchpad`,
        `audiences`, `evidence`, no `relationships`) and a body following
        `templates/event-kind.md`'s required sections, using only the facts
        gathered above plus a worked-example JSON event.
        done when: the file exists at that path and contains a YAML front-matter
        block with all six required top-level keys.

STEP 2  Validate against the corpus schema                 [needs 1]  ← RUNS HERE
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        repo root and fix anything it reports.
        done when: the command exits 0.

STEP 3  Earn the commit gate                                     [needs 2]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own call.
        done when: the command's output includes `OK` and its exit code is 0.

STEP 4  Self-review against the issue's own checklist             [needs 3]
        Re-read the diff line by line against every bullet in issue #875's
        Definition-of-done, and re-open each cited source to confirm the evidence
        entry it supports actually says what the statement claims.
        done when: every DoD bullet has been checked off against the actual file
        content (not assumed), and `validate.py` still exits 0 after any fixes.

STEP 5  Commit                                                    [needs 4]
        `git add` the two files and commit with `git commit -s`.
        done when: `git log -1` on the branch shows the new commit and
        `git status` reports a clean working tree for these two files.

PARALLEL  None of these five steps can run as parallel subagents — they are one
          file, one validator, one gate, and one commit, each depending on the
          previous step's output existing on disk. This is a single-document task
          with no independent surface to split across agents.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (step 2) and
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
          (step 3, the mandatory pre-commit gate named in the dispatch instructions)
          are the only checks this task needs. No `review-*` skill applies — this
          is a documentation-only corpus node, not an implementation diff, test
          suite, or UI change. `qa` explore mode does not apply: there is no
          runtime interface to exercise, only a Markdown file to validate.
BUDGET    Step 1 is the step most likely to overrun — gathering and honestly
          classifying evidence for every required section (tag shape, content
          semantics, access control, producers/consumers) takes longer than
          writing the front matter itself, and rushing it is what produces an
          UNVERIFIED-only "FACT."
OPEN      Whether any client is expected to consume kind 39001 at all today is not
          settled by the issue — the repository shows zero consumers, which the
          node states as a fact rather than resolving into an invented consumer.
          Whether a `docs/nips/NIP-XX.md` file is expected for this kind is also
          unresolved corpus-wide (per `templates/event-kind.md`'s own gap table)
          — 39001 already has NIP-29 as its governing external spec, so this node
          treats that as sufficient and does not propose writing a new NIP-XX file.
LEFT OUT  Documenting kind 39000 (channel metadata) or kind 39002 (membership) —
          each is its own node per `AGENTS.md`'s one-idea-per-node rule and is out
          of scope for issue #875. Adding a `relationships` entry — no sibling
          `events/kinds/*` node exists on `origin/launchpad` at this revision to
          point at, so declaring one would be a hard validation error, not
          thoroughness. Proposing new client-consumer code for kind 39001 — this
          task documents the existing wire contract, it does not add a feature
          that uses it.

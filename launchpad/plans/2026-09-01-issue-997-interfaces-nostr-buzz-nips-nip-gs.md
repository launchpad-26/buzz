Issue #997 -- task: document interfaces/nostr/buzz-nips/nip-er.md
Stated size: no `Size` line in the issue; dispatch instructions cap this task explicitly -> cap: 5 steps.

ALREADY TRUE  (verified against git and gh, not notes)
  On branch `task/997-interfaces-nostr-buzz-nips-nip-gs`, worktree
    `__worktrees/task-997-interfaces-nostr-buzz-nips-nip-gs`, based on `origin/launchpad`
    at `650354eab` ("Merge pull request #1787 from launchpad-26/delete-board-automation-workflow"),
    working tree clean.
  **Naming mismatch, resolved in favor of the issue body.** The dispatch instructions for
    this task named the target as `nip-gs.md` and used `nip-gs` in the worktree/branch
    names. `gh issue view 997` shows the real issue title is "task: document
    interfaces/nostr/buzz-nips/nip-er.md", its HTML comment is
    `alias:DOC:interfaces/nostr/buzz-nips/nip-er.md`, and its Objective/Impacted-components
    both name `nip-er.md`. Per the dispatch instructions' own rule ("the issue body is the
    input" / "do not re-derive scope from the parent Feature or PRD"), the issue body wins:
    this plan documents **NIP-ER**, not NIP-GS. Both `docs/nips/NIP-ER.md` and
    `docs/nips/NIP-GS.md` exist on disk, so this is not a case of the wrong spec being
    missing -- the dispatch prompt simply named the wrong NIP for issue #997. The
    worktree/branch names keep the `-nip-gs` suffix already created in step 1 of the
    dispatch instructions (before the issue was read); only the document's content and
    target path follow the issue.
  `launchpad/docs/corpus/schema/node.schema.json` is merged and authoritative: required
    fields id/type/status/origin/audiences/evidence; `type` enum has no `interface` value,
    only the combined `interfaces-events` (confirmed both in the schema file and in
    `launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section).
  `launchpad/docs/corpus/templates/interface.md` exists and is the applicable template
    (required sections: Interface description, Operations, Contract and stability,
    Boundary, Relationships, Scope and omissions).
  `launchpad/docs/corpus/interfaces/` does not exist anywhere in the tree yet (`ls`/`find`
    both fail with "No such file or directory") -- the target file and its parent dirs are
    a clean creation, not an update.
  `docs/nips/NIP-ER.md` exists at repo root and is the authoritative spec: kind:30300
    addressable "Event Reminder" events, NIP-44-encrypted content, public `not_before`
    scheduling tag, NIP-42 author-only relay reads, draft/optional/relay status.
  The NIP-ER spec is implemented, not merely aspirational: `KIND_EVENT_REMINDER = 30300`
    in `crates/buzz-core/src/kind.rs` (also listed in `AUTHOR_ONLY_KINDS`); ingest-side
    `not_before`/`expiration`/`d`-tag validation in
    `crates/buzz-relay/src/handlers/ingest.rs` (`validate_not_before`,
    `validate_event_reminder`, both unit-tested); author-only read enforcement in
    `crates/buzz-relay/src/handlers/req.rs` (`author_only_filters_authorized`,
    `is_author_only_event`, `event_visible_to_reader`, with documented `auth-required:` /
    `restricted:` close reasons); NIP-11 advertisement in `crates/buzz-relay/src/nip11.rs`
    (`supported_extensions: ["nip-er"]`, `limitation.due_delivery_mode: "push"`,
    `limitation.max_not_before_delta`); DB materialization/query/claim/release in
    `crates/buzz-db/src/store/{event.rs,reminder.rs}` (`extract_not_before`,
    `query_due_reminders`, `claim_due_reminder_with_stamp`, `release_due_reminder`); the
    push-mode scheduler loop in `crates/buzz-relay/src/main.rs` (~lines 769-891); and a
    35-plus-test E2E suite in `crates/buzz-test-client/tests/e2e_event_reminder.rs`
    covering acceptance/rejection, author-only WS/HTTP query and count, replacement
    semantics, and fan-out isolation.

STEP 1  [independent]  Gather evidence (already performed this session before writing
        this plan -- recorded here per `AGENTS.md`'s step-3 rule, not repeated as future
        work): read `docs/nips/NIP-ER.md` in full; `launchpad/docs/corpus/AGENTS.md`,
        `schema/node.schema.json`, `templates/interface.md` in full; and, in the crates
        tree, `buzz-core/src/kind.rs` (kind constant + `AUTHOR_ONLY_KINDS`),
        `buzz-relay/src/handlers/ingest.rs` (`validate_not_before`/
        `validate_event_reminder` + their unit tests), `buzz-relay/src/handlers/req.rs`
        (author-only filter/read-gate functions and their doc comments naming the close
        reasons), `buzz-relay/src/nip11.rs` (NIP-11 advertisement fields),
        `buzz-db/src/store/event.rs` and `store/reminder.rs` (materialization + due-query/
        claim/release), `buzz-relay/src/main.rs` (scheduler wiring), and the test-name
        listing of `buzz-test-client/tests/e2e_event_reminder.rs`.
        done when: every claim planned for STEP 2's document cites one of the paths above
        (or another path actually opened in this session) and no claim rests on inference
        presented as fact.

STEP 2  [needs 1]  <- RUNS HERE  Write
        `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-er.md`: schema-valid front
        matter (`id: interfaces-nostr-buzz-nips-nip-er`, `type: interfaces-events`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
        no `relationships` -- no node in the merged corpus at `origin/launchpad` is a
        plausible target, and this is the corpus's first interface-shaped instance node
        so there is no sibling to point at either) plus a body following
        `templates/interface.md`'s required sections (Interface description; Operations;
        Contract and stability; Boundary; Relationships; Scope and omissions) and
        satisfying every bullet of issue #997's own Definition-of-done checklist: exactly
        one hand-authored node; schema-valid front matter with typed relationships where
        applicable; one independently maintainable idea; every substantive claim
        FACT/INFERENCE/TEAM_KNOWLEDGE-classified and cited; links to implementation,
        verification and the spec without duplicating their content; inputs/outputs/
        error-rejection behavior; auth/versioning/ordering-idempotency; a link to the
        authoritative spec (`docs/nips/NIP-ER.md`); at least one valid and one failure
        example.
        done when: the file exists at that exact path, front matter parses against
        `node.schema.json`'s field set, and every DoD bullet above has a corresponding
        section or explicit statement in the body.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full tree including the new file. Fix and re-run on any
        failure; treat any FAIL not caused by the new node as a fresh finding to report,
        not something to silently work around.
        done when: the command exits 0 with no FAIL lines (UNVERIFIED notices are
        acceptable).

STEP 4  [needs 3]  Earn the commit gate, then commit: run
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole command in its own tool call and confirm it prints `OK`;
        only then, in a separate tool call, `git add` the plan + node and
        `git commit -s -m "docs(corpus): document Buzz NIP-ER interface (#997)"`. If the
        commit is rejected for a missing gate stamp, do not touch the stamp file and do
        not use `--no-verify` -- report it as a finding instead.
        done when: the unittest run prints `OK`, and `git log -1` on the resulting commit
        shows a `Signed-off-by:` trailer and the two intended files staged.

STEP 5  [needs 4]  Self-review: re-read the diff against issue #997's DoD checklist line
        by line; re-open every cited file to confirm each evidence entry actually supports
        its claim; confirm no second hand-authored canonical corpus document was created;
        re-run `validate.py` to confirm it still exits 0.
        done when: every DoD bullet is checked off against the actual diff (not
        recollection) and `validate.py` exits 0 on the post-commit tree.

PARALLEL  None. Single target file, single worktree, strictly sequential steps -- this is
          a solo single-document task with no batch siblings in this dispatch.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0, this
          session). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (must print `OK`,
          run alone in its own tool call, before the commit). No PR is opened and nothing
          is pushed per the dispatch instructions (step 7: "Do not open a PR. Do not
          push."); `review-adjudicate` and any cross-model review pass are therefore not
          part of this task's scope at all, not merely deferred.

BUDGET    STEP 2. NIP-ER is a substantial spec (event schema, content schema, replacement
          state machine, relay due-time delivery modes, client notification profile,
          privacy/security considerations, six worked examples) backed by real,
          well-tested code across five crates. The work is compressing that faithfully
          into the interface template's six required sections -- pointing at the kind
          constant, the validation functions, the NIP-11 fields and the DB/scheduler
          implementation, plus the spec itself -- without re-encoding the wire format a
          second time in Markdown (the template's own stated anti-pattern) and without
          drifting into `#1337`'s event-kind-template territory by spending the ledger on
          kind:30300's tag shape alone.

OPEN      Whether the corpus document should also describe `KIND_STREAM_REMINDER = 40007`
          (a similarly-named but structurally distinct kind found while reading
          `kind.rs`). Planned handling: it is out of scope -- NIP-ER's own spec text names
          only `kind:30300`, and folding in an unrelated kind would violate the issue's
          own "one independently maintainable idea" bullet. Named here rather than
          silently omitted, since the name collision is easy to trip over later.

LEFT OUT  Editing `launchpad/docs/corpus/AGENTS.md`, `schema/node.schema.json`, or
          `templates/interface.md`. Any `relationships` edge -- no merged corpus node is a
          plausible target and this is the first interface-shaped instance, so there is no
          sibling either. Deep documentation of `KIND_STREAM_REMINDER` (40007) as part of
          this node -- see OPEN above. Opening a PR or pushing the branch -- the dispatch
          instructions explicitly reserve that for a later step outside this task's scope.
          Re-deriving scope from parent Feature #616 or PRD #602 -- the issue body is the
          sole input per the dispatch instructions.

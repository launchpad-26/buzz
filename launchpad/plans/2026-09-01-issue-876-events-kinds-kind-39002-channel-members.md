Issue #876 — task: document events/kinds/kind-39002-channel-members.md
Stated size: issue carries no `Size` field; dispatching task instructions cap this explicitly ("small single-document task") -> cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-876-events-kinds-kind-39002-channel-members` on branch
    `task/876-events-kinds-kind-39002-channel-members`, based on `origin/launchpad` HEAD
    a8b5021efb92264e724366d08b47b2a3839eb90a, working tree clean.
    `launchpad/docs/corpus/events/` does not exist at all yet (no `events` directory under
    `launchpad/docs/corpus/`), so `launchpad/docs/corpus/events/kinds/kind-39002-channel-members.md`
    does not exist. `node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
    `launchpad/docs/corpus/templates/event-kind.md` (id `corpus-template-event-kind`) and
    `corpus-agents` are all merged and present in this worktree (== origin/launchpad).
    `crates/buzz-core/src/kind.rs` defines `KIND_NIP29_GROUP_MEMBERS: u32 = 39002` (line 426),
    in the addressable range 39000-39003, and it is not a member of `AUTHOR_ONLY_KINDS`,
    `RESULT_GATED_KINDS`, `P_GATED_KINDS`, or `SHARED_GATED_KINDS`.

STEP 1  [independent]  Gather evidence: `crates/buzz-core/src/kind.rs` (KIND_NIP29_GROUP_MEMBERS
        definition, ALL_KINDS membership, absence from every access-control set,
        `is_parameterized_replaceable`); `crates/buzz-relay/src/handlers/side_effects.rs`
        (`group_members_tags`, `store_group_members_event`, `dispatch_group_members_event`,
        `emit_group_discovery_events` and its callers across join/leave/create/edit-metadata/
        moderation-notice/roster-reconciliation paths); `crates/buzz-db/src/store/channel_members.rs`
        (`LockedMemberSnapshot::replace_member_event`, `MemberRecord`, `LargeChannelRoster`);
        `crates/buzz-relay/src/handlers/ingest.rs` (`required_scope_for_kind`'s absence of any
        39000-39003 arm, confirming client-authored kind:39002 falls to the `_ => Err("restricted:
        unknown event kind")` catch-all); `crates/buzz-relay/src/handlers/event.rs`
        (`dispatch_persistent_event`/`dispatch_persistent_event_inner`, channel-scoped fan-out
        topic, audit enqueue); `desktop/src-tauri/src/commands/channels/fetch.rs`
        (`fetch_channels`'s `#p`/`#d` queries against kind:39002, `collect_members_by_channel`);
        `migrations/0001_initial_schema.sql` / `schema/schema.sql` (`member_role` enum, the
        `search_tsv` generated column's kind exclusion list, which does NOT include 39002); the
        repo root `AGENTS.md`'s "Event kinds" and "Channel scoping" sections; and
        `launchpad/docs/corpus/templates/event-kind.md`'s nine required sections.
        done when: every claim planned for the evidence ledger has a specific opened source
        (path + symbol or line) recorded, and it is confirmed whether a `docs/nips/NIP-*.md`
        file exists for kind 39002 (expected: no, since it follows NIP-29 directly).

STEP 2  [needs 1]  <- RUNS HERE  Write `launchpad/docs/corpus/events/kinds/kind-39002-channel-members.md`
        with schema-valid front matter (`id: events-kinds-kind-39002-channel-members` per the
        dispatching task instruction, `type: interfaces-events` per node.schema.json's dedicated
        protocol/event-surface value and the event-kind template's own section-1 guidance,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, a
        `relationships` entry `implements -> corpus-template-event-kind` since that id is
        confirmed loadable in this worktree/merge-target, and an `evidence` ledger with a
        commit-provenance FACT plus one entry per substantive claim) and a body following the
        template's nine required sections: (1) title/kind identity (KIND_NIP29_GROUP_MEMBERS =
        39002, kind.rs line 426), (2) referenced NIP (NIP-29, pinned commit SHA), (3) kind range/
        delivery classification (addressable/parameterized-replaceable, 30000-39999, cross-checked
        against `is_parameterized_replaceable`), (4) tag shape (exactly one `d` = channel/group id;
        zero or more `p` tags shaped `[p, pubkey-hex, "", role]`, no `h` tag), (5) content semantics
        (always empty string), (6) access control/storage (world-readable by default — absent from
        every gated-kind set — but stored channel-scoped so existing per-channel access control
        applies; relay-authored only via the dedicated `replace_member_event`/`LockedMemberSnapshot`
        lock path, never the generic `replace_addressable_event` path used by kind 39000/39001;
        client-authored publishes are rejected at ingest as an "unknown event kind" side effect of
        having no `required_scope_for_kind` arm, not a purpose-built anti-spoof rule — state that
        distinction honestly), (7) one complete worked-example JSON event, (8) versioning/
        supersession (state none known, or the gap if unverified), (9) the `implements` relationship
        declared above. Satisfy every DoD bullet from the issue body, including producers/consumers/
        authorization/persistence/fanout/search/audit treatment and links to handler/registry/tests.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and every
        issue-876 DoD bullet is addressed by a distinct, evidence-backed section.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix any
        schema violation, unresolved relationship, or bad citation path and re-run until it exits 0.
        done when: the command prints a clean pass (exit 0) with no errors, only permissible
        `UNVERIFIED` notices.

STEP 4  [needs 3]  Self-review the diff line-by-line against the issue's DoD checklist; re-open
        every cited file/line to confirm each evidence entry actually supports its statement (not
        merely concerns the same subject); confirm no second hand-authored canonical corpus document
        was created; confirm `validate.py` still exits 0 after any fix.
        done when: the line-by-line audit is complete, no unsupported FACT/INFERENCE remains, and
        validate.py exits 0 on the current tree.

STEP 5  [needs 4]  Earn the commit gate by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own tool call and confirming it prints `OK`; only then, in a
        separate tool call, `git add` the two files and `git commit -s` with the message
        `docs(corpus): document kind 39002 channel members event (#876)`.
        done when: the unittest run reports `OK`, and `git commit -s` succeeds without `--no-verify`
        and without touching any stamp file directly.

PARALLEL  None — single new file, strictly sequential (evidence before body; body before
          validation; validation before self-review; self-review before the commit gate).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
          The corpus unittest suite (`python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"`) must print `OK` as the sole
          command in its own tool call immediately before commit, per the dispatching instructions —
          if the commit is then rejected for a missing gate stamp, that is reported back as a
          finding rather than routed around with `--no-verify` or a hand-edited stamp file.
          `review-adjudicate` and the cross-model final review pass are deferred to the batch
          owner's later review — not run in this worktree.

BUDGET    STEP 1 and STEP 2 carry the weight. STEP 1 must pin down the access-control story
          precisely: kind 39002 is unusually layered (world-readable by kind.rs's gated-set
          membership, yet channel-scoped by storage, yet relay-authored only via a bespoke lock
          path, yet rejected outright at ingest for any client attempt) and each of those four
          facts needs its own citation rather than being collapsed into one blanket claim.

OPEN      The dispatching task instruction fixes `id: events-kinds-kind-39002-channel-members`
          directly, which does not match the general naming standard's
          (`corpus-standard-naming`) filename-to-id correspondence convention (that standard would
          suggest a `corpus-`-prefixed id, e.g. `corpus-events-kinds-kind-39002-channel-members`).
          This plan follows the explicit, unambiguous instruction given directly for this task
          rather than the general standard, since the instruction is specific-over-general and was
          handed down for this exact node; it is named here as a real tension rather than silently
          reconciled. Whether every Buzz-proposed kind needs a `docs/nips/NIP-XX.md` file before a
          corpus event-kind node exists is explicitly left unsettled by the template itself
          (`corpus-template-event-kind`'s own gap table) — this task does not create one for kind
          39002, since it already has a governing community NIP (NIP-29) and needs no Buzz-proposed
          extension document.

LEFT OUT  Any `docs/nips/NIP-*.md` authoring for kind 39002 — out of scope; NIP-29 already governs
          it. A second `relationships` edge beyond `implements -> corpus-template-event-kind` (e.g.
          to a hypothetical kind-39000/39001 sibling node) — no such sibling node exists yet in this
          corpus, so no other target resolves. Editing `launchpad/docs/corpus/AGENTS.md`,
          `node.schema.json`, or any other existing merged node. Documenting kind 39000
          (channel metadata) or 39001 (channel admins) as part of this node — each is its own
          independently maintainable idea per `AGENTS.md`'s one-node-one-idea rule and, if needed,
          is a separate task. Any change to relay/desktop runtime behavior.

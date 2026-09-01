Issue #1005 — task: document interfaces/nostr/buzz-nips/nip-wp.md
Stated size: no `Size` line on the issue → cap: 5 steps (per dispatching task instruction, which caps this corpus-doc task at 5 steps)

ALREADY TRUE  (verified against git and the worktree, not notes)
  `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-wp.md` does not exist
  (confirmed with `test -f`, branch is a fresh checkout of `origin/launchpad`).
  `docs/nips/NIP-WP.md` exists at repo root and is the authoritative spec text
  (read in full — Abstract, Motivation, Kinds table, Event Format, Relay
  Processing Algorithm, Client Behavior, Security Considerations, Relation to
  Other NIPs).
  `crates/buzz-core/src/kind.rs:395` defines
  `RELAY_ADMIN_SET_WORKSPACE_PROFILE: u32 = 9033`.
  `crates/buzz-relay/src/handlers/relay_admin.rs` implements the kind:9033
  command handler (`execute_relay_admin_command`, `may_set_workspace_profile`,
  `validate_workspace_icon`) plus its module-doc permission matrix.
  `crates/buzz-relay/src/nip11.rs` serves the icon in the NIP-11 `icon` field
  (`RelayInfo.icon`, `workspace_icon_for_host`).
  `crates/buzz-db/src/store/community.rs:227-270` persists the icon
  (`get_community_icon`, `set_community_icon`) against the `communities.icon`
  column.
  `crates/buzz-test-client/tests/regression_relay_admin_ban_gate.rs` is a live
  regression test exercising a valid 9033 accept and a banned-admin 9033
  rejection (403, `blocked:` prefix), usable as the example pair the DoD asks
  for.
  Three originating commits found by `git log`: `5bfd5ca27` (feat #1463, adds
  the icon + kind), `e2e007910` (fix #3128, ban gate for 9030-9033),
  `5765fc74b` (fix #3998, rosterless-open-relay admit).
  `node.schema.json`'s `type` enum has no `interface` value; the interface-
  shaped value is `interfaces-events` (confirmed against the enum list and
  against `launchpad/docs/corpus/templates/interface.md`, which documents
  exactly this convention and prescribes the required-sections shape used
  below).
  No sibling `buzz-nips` corpus node exists yet in this worktree or on
  `origin/launchpad` (`find launchpad/docs/corpus -iname '*nip*'` returns only
  templates, none under `interfaces/nostr/buzz-nips/`) — so no
  `relationships` entry can resolve; any mention of NIP-11/NIP-43/NIP-86 must
  be prose-only.

STEP 1  Draft `launchpad/docs/corpus/interfaces/nostr/buzz-nips/nip-wp.md`   [independent]
        Front matter: id `interfaces-nostr-buzz-nips-nip-wp`, type
        `interfaces-events`, status `draft`, origin `launchpad`, audiences
        `[agent, developer, reviewer]`, no `relationships` block (nothing
        resolves yet). Body follows the `interface` template's required
        sections: Interface description, Operations (table citing
        `kind.rs:395`, `relay_admin.rs`, `nip11.rs`, `community.rs`, and
        `docs/nips/NIP-WP.md` itself), Contract and stability (versioning via
        the NIP's own `draft`/`optional` status, error/rejection via the
        403+`blocked:` regression test and the `Rejected`/`Internal` error
        categories in `relay_admin.rs`, ordering via "last accepted command
        wins", auth via the admin/owner-or-rosterless-open-relay rule),
        Boundary statement, Relationships (prose-only, naming NIP-11/NIP-43/
        NIP-86 by filename, no machine edges), Scope and omissions. Include
        one valid example (a signed kind:9033 event with an `icon` tag,
        accepted) and one failure example (banned admin's 9033 rejected with
        403 `blocked:`, cited from the regression test).
        done when: the file exists at that path with schema-required front
        matter fields present and no `relationships` key.

STEP 2  Validate corpus-wide                                    [needs 1]  ← RUNS HERE
        Run `python3 launchpad/project-intelligence/corpus/validate.py`.
        done when: the command exits 0 and prints no `FAIL` line (any FAIL not
        traceable to this new node is reported as a separate finding, not
        silently patched around).

STEP 3  Self-review against the issue's Definition of Done       [needs 2]
        Re-read the drafted node line by line against issue #1005's checklist
        (exactly one hand-authored doc; schema-valid front matter with stable
        id/type/status/origin/audiences/evidence; one independently
        maintainable node; every claim traceable and FACT/INFERENCE/
        TEAM_KNOWLEDGE not conflated; links implementation/spec without
        duplicating it; checked against the recorded revision; validate.py
        clean; inputs/outputs/error behavior defined; auth/versioning/
        ordering defined; spec link present; one valid + one failure
        example present).
        done when: every DoD bullet has a specific location in the drafted
        file it is satisfied by, written down, with no bullet left
        unaddressed.

STEP 4  Earn the commit gate                                     [needs 3]
        Run `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the
        sole command in its own tool call.
        done when: the command prints `OK`.

STEP 5  Commit                                                    [needs 4]
        `git add` the new corpus doc and this plan file, then
        `git commit -s -m "docs(corpus): document Buzz NIP-WP interface
        (#1005)"`.
        done when: `git log -1 --format=%H` on the worktree branch names a
        new commit containing exactly those two files (`git show --stat
        HEAD`), and if the commit is instead rejected for a missing gate
        stamp, that rejection is reported as a finding rather than bypassed
        with `--no-verify` or a self-authored stamp file.

PARALLEL  None of these steps can run as parallel subagents: STEP 1 is the
          only content-producing step and everything downstream reads its
          output; STEP 2-5 are a strictly sequential gate chain (validate,
          then self-review, then test-gate, then commit) each depending on
          the previous step's file state.
GATES     No `review-*` skill applies — this task is a single corpus
          documentation node with its own validate.py/unittest gates named
          in STEP 2 and STEP 4, not a code change with runtime behavior.
          `qa` explore mode does not apply: there is no runtime interface to
          exercise, only a Markdown document and a schema/unit-test check.
BUDGET    STEP 1 (the draft) is the step most likely to eat the budget —
          citing exact line numbers/symbols for every Operations-table row
          and Contract-and-stability claim, and writing an honest valid +
          failure example pair, is the bulk of the work; STEPS 2-5 are
          mechanical gate-running.
OPEN      Whether a future `buzz-nips` sibling node (e.g. for NIP-43 or
          NIP-11) should later gain a `references`/`part-of` edge back to
          this node is left for whoever authors that node — not decided
          here, since none exists yet to declare it against.
LEFT OUT  No second hand-authored corpus document is created (per the
          issue's own out-of-scope list). No runtime product behavior is
          changed — this task only documents existing behavior. No ADR or
          decision is made about the rosterless-open-relay admit rule found
          in `relay_admin.rs`; it is documented as observed behavior, not
          adjudicated.

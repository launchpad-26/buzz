Issue #1011 — task: document interfaces/nostr/nip-25.md
Stated size: no `Size` line on the issue -> cap: 5 steps (single-document corpus task,
same convention as the #608/#616 corpus-doc batch)

ALREADY TRUE  (verified against git and the working tree, not notes)
  Worktree `__worktrees/task-1011-interfaces-nostr-nip-25` on branch
    `task/1011-interfaces-nostr-nip-25`, based on `origin/launchpad` at
    `650354eab8d41ab6ce1a71de079a6c6d95c69052` (`git rev-parse HEAD` confirmed).
  `launchpad/docs/corpus/interfaces/nostr/nip-25.md` does not exist -- there is no
    `launchpad/docs/corpus/interfaces/` directory at all yet (`find launchpad/docs/corpus
    -type f -name "*.md"` lists no `interfaces/*` path).
  `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum is exactly:
    architecture, layers, capabilities, platforms, implementation, interfaces-events,
    verification, operations, development, release, governance, agent, ingestion. There
    is no bare "interface" value -- the correct value for an interface-shaped node is
    the combined `interfaces-events` token, confirmed by
    `launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section,
    which states a node built from that template "carries `type: interfaces-events`".
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`) exists,
    is merged, and prescribes six required body sections: Interface description,
    Operations, Contract and stability, Boundary statement, Relationships, Scope and
    omissions.
  Three existing merged nodes resolve as valid `relationships` targets today:
    `corpus-template-interface` (the template above), `architecture-flows-websocket-
    authentication` (`launchpad/docs/corpus/architecture/flows/websocket-authentication.md`),
    and `architecture-containers-relay`
    (`launchpad/docs/corpus/architecture/containers/relay.md`) -- all three ids were read
    directly from their front matter in this worktree.
  `events/kinds/kind-7-reaction.md` (issue #882's sibling node documenting the kind:7
    wire contract itself) is NOT present anywhere in this worktree/branch (confirmed by
    `find`), so per `AGENTS.md`'s rule that a `relationships` target must already resolve
    on the branch being merged into, it cannot be a relationship target here -- it will
    be named in prose/boundary text only.
  `crates/buzz-core/src/kind.rs` defines `KIND_REACTION: u32 = 7` with doc comment
    "NIP-25: Content is emoji char or `+`/`-`." and separately defines
    `KIND_HUDDLE_REACTION: u32 = 24810`, an unrelated ephemeral huddle-emoji-burst kind
    that must be explicitly excluded in the Boundary section.
  The reaction ingest/storage/removal/query implementation was read directly:
    `crates/buzz-relay/src/handlers/ingest.rs` (scope mapping, `derive_reaction_channel`,
    `validate_reaction_emoji`, the reaction insert/dedup branch, the
    `reactions_do_not_require_h_tag` test), `crates/buzz-db/src/store/reaction.rs`
    (`ReactionEventInsertOutcome`, the `ON CONFLICT` dedup SQL and its doc comment "One
    reaction per user per emoji per event. Soft-delete via removed_at."),
    `crates/buzz-relay/src/handlers/side_effects.rs` (kind:5-deletes-a-reaction removal
    path), `crates/buzz-sdk/src/builders.rs` (`build_reaction`,
    `build_custom_emoji_reaction`, `build_remove_reaction`), and
    `crates/buzz-cli/src/commands/reactions.rs` (`reactions add|remove|get`).

STEP 1  [independent]  Gather any remaining evidence gaps: re-confirm the exact
        rejection-message strings and their call sites in `ingest.rs` (already located:
        "reaction must reference a target event via e tag", "reaction target event not
        found", "malformed reaction target id", "reaction emoji exceeds 64 characters",
        "long custom emoji reaction shortcode must be canonical lowercase") and the
        success-path `IngestResult { accepted: true, message: String::new() }` shape, so
        every claim in STEP 2's evidence ledger is opened, not paraphrased from memory.
        No corpus file changes in this step.
        done when: every substantive claim planned for the node's body has a specific
        source path/symbol already opened in this session, and anything expected but not
        verified (e.g. the upstream NIP-25 spec text itself was not fetched) is named for
        the body's scope-and-omissions section rather than silently assumed.

STEP 2  [needs 1]  <- RUNS HERE  Write
        `launchpad/docs/corpus/interfaces/nostr/nip-25.md`: schema-valid front matter
        (`id: interfaces-nostr-nip-25`, `type: interfaces-events`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, an `evidence`
        ledger opening with a commit citation for `650354eab8d41ab6ce1a71de079a6c6d95c69052`
        and one entry per substantive claim, classified honestly per FACT/INFERENCE/
        TEAM_KNOWLEDGE, plus `relationships: implements corpus-template-interface,
        references architecture-flows-websocket-authentication, part-of
        architecture-containers-relay`), and the six required body sections from the
        interface template: Interface description, an Operations table (add/remove/query,
        each citing its defining code symbol), Contract and stability (auth/authz scope
        mapping, channel-derivation-from-target, ON-CONFLICT dedup/idempotency, every
        rejection message and its cause, the success-response shape), a Boundary section
        explicitly excluding `KIND_HUDDLE_REACTION` and the unmerged kind-7-reaction.md
        node, Relationships, and Scope and omissions (including the NIP-25 spec-text gap
        from STEP 1). Includes one valid CLI-add example and one failure example (missing
        `e` tag) with their concrete request/response shapes.
        done when: the file exists, `type` is `interfaces-events` (not an invented value),
        every DoD bullet from the issue (inputs/messages, outputs/responses, error/
        rejection behavior, authn/authz, versioning/compatibility, ordering/idempotency,
        a link to upstream NIP-25, one valid + one failure example) has a corresponding
        body section, and no second hand-authored canonical corpus document was created.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        the repository root; fix anything it reports and re-run until it exits 0.
        done when: the command's own exit status (`$?`) is 0, confirmed after the run,
        and any FAIL line not caused by this new node is recorded as a fresh finding
        rather than silently worked around.

STEP 4  [needs 3]  Self-audit the finished node line by line against issue #1011's own
        Definition-of-done checklist and against `templates/interface.md`'s Boundary
        section, confirm every evidence entry actually supports the claim it sits under,
        confirm the node does not duplicate `kind-7-reaction.md`'s canonical wire-contract
        claims, and re-run `validate.py` once more after any fix.
        done when: the audit note maps each DoD bullet to the exact body section that
        satisfies it, and `validate.py` exits 0 on the final version.

STEP 5  [needs 4]  Earn the verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"` as the sole command in its own call, confirm it prints `OK`, then in
        a separate call stage and commit the plan file and the new document with
        `git commit -s`. No push, no PR (per this task's explicit instruction).
        done when: the unittest run reports `OK`; the commit succeeds without a "no
        verification stamp" rejection; `git rev-parse HEAD` afterward names a new commit
        containing exactly the two intended files.

PARALLEL  None. One target file (`launchpad/docs/corpus/interfaces/nostr/nip-25.md`) plus
          this plan file, strictly sequential, single worktree, single agent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 3, re-run in
          STEP 4) and `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (STEP 5) are the two
          automated gates run in this session. `review-code`, `review-adjudicate`, and a
          cross-model final pass are not run here -- this task explicitly stops at commit,
          with no PR opened.

BUDGET    STEP 2. The hard part is describing the ingest/storage/removal contract
          accurately (dedup semantics, the two distinct "not found" rejection points,
          channel derivation from the target event) without drifting into restating
          kind:7's own wire-format contract, which belongs to the sibling (unmerged)
          event-kind node instead.

OPEN      Whether the upstream NIP-25 specification text
          (github.com/nostr-protocol/nips/blob/master/25.md) should be fetched and read
          directly in this session, versus linked as an external URL and relied on
          indirectly through the source doc comment and validated builder behavior. This
          plan links it as an external URL (reported UNVERIFIED by validate.py, per
          AGENTS.md's citation-shape table) and records the gap explicitly in Scope and
          omissions, rather than fetching the live document -- the wire-shape claims made
          here are all independently backed by this repository's own code and tests.

LEFT OUT  A `relationships` edge to `events-kinds-kind-7-reaction` -- that node lives on
          an unmerged branch (issue #882) and does not resolve against
          `origin/launchpad`; it is named in prose/Boundary text only, per AGENTS.md's
          rule against targeting a node that only resolves in another worktree.
          Any restatement of kind:7's own tag shape / content semantics as a canonical
          claim -- that is `events/kinds/kind-7-reaction.md`'s territory, referenced here
          rather than duplicated.
          Field-by-field cataloguing of every `buzz reactions --help` flag -- that is the
          reference/API-Reference-depth gap `#1346`/`#1532` describe as unresolved, not
          this template's job.
          Opening a pull request, pushing the branch, or running any review skill --
          explicitly out of scope per this task's own instructions.

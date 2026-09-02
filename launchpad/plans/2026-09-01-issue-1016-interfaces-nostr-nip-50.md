Issue #1016 — task: document interfaces/nostr/nip-50.md
Stated size: no explicit Size line on the issue; docs-only single-node task, cap set by the dispatching task instructions  →  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  Worktree __worktrees/task-1016-interfaces-nostr-nip-50 is checked out from
    origin/launchpad at commit c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f
    (`git rev-parse HEAD`).
  `launchpad/docs/corpus/interfaces/nostr/nip-50.md` does not exist
    (`test -f` on that path returns false); no `interfaces/` directory exists
    under `launchpad/docs/corpus/` yet at all (`find launchpad/docs/corpus
    -maxdepth 2 -type d` lists no `interfaces` entry), so this is the first node
    of that shape.
  `launchpad/docs/corpus/architecture/flows/search-query.md` (id
    `architecture-flows-search-query`, status `draft`) already exists in this
    checkout and documents the WS-REQ / HTTP-POST-/query NIP-50 request/response
    lifecycle end to end (trigger, preconditions, ordered interactions, auth
    crossings, failure table). Because this checkout is branched directly from
    `origin/launchpad`, that node's id resolves as a valid relationship target
    without a further merge-base check.
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`)
    exists in the same checkout, is not under the schema-excluded `schema/`
    subtree (`validate.py`'s `EXCLUDED_TOP_LEVEL_DIRS = {"schema"}` does not
    cover `templates/`), and therefore is itself a validated, resolvable
    relationship target.
  `node.schema.json`'s `type` enum contains `interfaces-events` (not a bare
    `interface` value) as the single combined interfaces/events surface, per
    Feature #602's success criteria and confirmed by the interface template's
    own front matter (`type: interfaces-events`).
  `crates/buzz-relay/src/nip11.rs:15` statically advertises NIP-50 in
    `SUPPORTED_NIPS`; `crates/buzz-search/src/query.rs`,
    `crates/buzz-relay/src/handlers/req.rs` and
    `crates/buzz-relay/src/api/bridge.rs` implement the search-filter contract;
    `crates/buzz-cli/src/commands/messages.rs::cmd_search` and
    `resolve_author` are the CLI-side consumers. All were opened this session.

STEP 1  Draft `launchpad/docs/corpus/interfaces/nostr/nip-50.md` as one          [independent]
        hand-authored interface node: front matter (id
        `interfaces-nostr-nip-50`, type `interfaces-events`, status `draft`,
        origin `upstream`, audiences, evidence ledger with a provenance commit
        citation for c34e62d16781dac3fa45cdedf0f09d4e1d8bbe8f, and
        `relationships` limited to `references: architecture-flows-search-query`
        plus optionally `implements: corpus-template-interface`) and a body
        following the interface template's required sections (interface
        description, operations table, contract and stability, boundary
        statement, relationships, scope and omissions) with one valid example
        (a WS `REQ` with a `search` field) and one failure example (mixed
        search/non-search filters rejected).
        done when: the file exists at that path, is valid YAML+Markdown, and
        every Definition-of-done bullet in issue #1016 has a corresponding
        section or evidence entry in the body (checked by re-reading the diff
        against the issue's checklist line by line).

STEP 2  Run corpus validation.                                    [needs 1]  ← RUNS HERE
        `python3 launchpad/project-intelligence/corpus/validate.py`
        done when: the command exits 0, and any FAIL line printed is not
        attributable to the new node (a FAIL attributable to it is fixed before
        this step is considered done; a pre-existing FAIL unrelated to this node
        is reported, not silently absorbed into this step).

STEP 3  Earn the commit gate and commit.                          [needs 2]
        Run, alone in its own shell invocation:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        Then, only after confirming `OK` in that output, in a separate command:
        `git add launchpad/docs/corpus/interfaces/nostr/nip-50.md
         launchpad/plans/2026-09-01-issue-1016-interfaces-nostr-nip-50.md`
        `git commit -s -m "docs(corpus): document NIP-50 interface (#1016)"`
        done when: the unittest command's output contains a line reading `OK`,
        and `git log -1 --format=%H` on this branch names a new commit whose
        tree contains both files (i.e. the commit succeeded without being
        rejected for a missing gate stamp). If the commit is rejected for a
        missing gate stamp, this step is not done and the rejection is reported
        as a finding rather than routed around with `--no-verify` or a
        hand-edited stamp file.

PARALLEL  None of the three steps may run as parallel subagents: step 2 reads
          the file step 1 writes, and step 3's commit stages exactly those two
          files and depends on step 2's validate.py pass plus its own
          unittest-gate run. All three touch or depend on the same single
          artifact, so the chain is sequential by construction, not by
          arbitrary choice.
GATES     No `review-*` skill runs inside this plan — the task's own step 6
          ("Self-review") is the only review gate specified by the dispatching
          instructions, and it is a manual re-read against the issue's
          Definition-of-done checklist, not an automated `review-code`/
          `review-a11y` pass. `qa` explore mode does not apply: this is a
          docs-only corpus node with no runtime interface (CLI, API, or UI) to
          exercise: the change touches Markdown and YAML front matter only, and
          the actual `buzz-search`/`buzz-relay`/`buzz-cli` code this node
          describes is not modified.
BUDGET    Step 1 is the step most likely to eat the budget: writing an evidence
          ledger where every FACT is honestly checked against an opened source
          (not merely a plausible-looking citation) is the slow part, and the
          interface template's *Boundary* section warns explicitly against
          drifting into the neighboring flow-node or event-kind-node shapes
          while drafting it.
OPEN      The issue does not decide whether `implements: corpus-template-interface`
          is worth declaring (the template says either `implements` or
          `references` is schema-legal and unsettled corpus-wide) — this plan
          treats it as optional and defers the final call to step 1's drafting,
          not to this plan.
          The issue also does not decide whether a `references` edge toward
          `architecture-flows-search-query` is the right direction given that
          node's own front matter currently declares no `relationships` back —
          this plan treats a one-directional `references` edge as valid per
          `relationships.schema.json`'s stated semantics ("no ownership or
          currency dependency implied"), not as something requiring a
          reciprocal edge.
LEFT OUT  A second corpus node for the `COUNT`/`/count` variant of NIP-50-style
          filtering is explicitly out of scope: the flow node's own "Scope and
          omissions" table already names it as "a separate flow node, not yet
          written," and issue #1016's own Out-of-scope section forbids creating
          a second hand-authored canonical corpus document in this task.
          Re-deriving scope from parent Feature #616 or PRD #602 is left out
          per the dispatching instructions, which state the issue body alone is
          the spec for this task.

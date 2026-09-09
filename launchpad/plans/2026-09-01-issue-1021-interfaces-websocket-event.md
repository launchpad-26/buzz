Issue #1021 — document interfaces/websocket/event.md
Stated size: no Size line in issue body -> cap: 5 steps (per dispatch instruction capping this plan at 5 steps)

ALREADY TRUE  (verified against git and the repository, not notes)
  Issue #1021's title and body (`gh issue view 1021 --repo launchpad-26/buzz`) confirm the
  target is `launchpad/docs/corpus/interfaces/websocket/event.md`, a canonical interface
  node for "event" -- matches the dispatch premise. Not blocked.

  `launchpad/docs/corpus/interfaces/` does not exist anywhere in this worktree
  (`find launchpad/docs/corpus/interfaces -name "*.md"` returns nothing), worktree
  checked out at `origin/launchpad` commit b5dd39acb7ade0a33692edaebe674a1212111dd5.
  There is no `interfaces/http/events.md` (issue #979) on this branch either -- it has
  not merged, so there is nothing to cross-link by `relationships[]`, only by filename
  mention in prose, per the dispatch note.

  `node.schema.json`'s `type` enum has thirteen members; the only interface-shaped one
  is `interfaces-events` (confirmed in the schema file itself and in
  `templates/interface.md`'s own "A note on `type`" section, which states a node built
  from that template "therefore carries `type: interfaces-events`").

  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
  `status: active`) already exists on `origin/launchpad` and is the corpus's own settled
  template for exactly this document shape -- required sections: Interface description,
  Operations, Contract and stability, Boundary, Relationships, Scope and omissions. This
  supersedes the dispatch note's assumption that "no template exists yet"; the template
  landed since that note was written, and following it is more grounded than inventing a
  fresh structure.

  Candidate `relationships[]` targets that already resolve on `origin/launchpad` at this
  revision (confirmed by reading each file's front matter): `corpus-template-interface`
  (governance/active), and four `architecture` flow nodes --
  `architecture-flows-event-ingestion`, `architecture-flows-live-fanout`,
  `architecture-flows-websocket-connection`, `architecture-flows-websocket-authentication`
  (all `status: draft`).

  Primary source material already read in `crates/buzz-relay/`:
  - `src/protocol.rs` -- `ClientMessage::Event(Event)` (parse), `RelayMessage::ok`,
    `RelayMessage::notice`, `RelayMessage::event` (push-direction wire format).
  - `src/handlers/event.rs` -- `handle_event` (ingest dispatch, auth/scope gating, OK
    responses), `fan_out_event_to_local_subscribers` and `fan_out_pubsub_event`
    (push-direction fan-out, same-node and cross-node), `filter_fanout_by_access`
    (shared access-control gate).
  - `src/handlers/ingest.rs` -- `IngestResult`/`IngestError`, the standardized
    machine-readable message-prefix convention (`duplicate:`, `invalid:`, `restricted:`,
    `blocked:`, `auth-required:`, `error:`).
  - `src/connection.rs` -- `handle_text_message` (parse-error -> NOTICE),
    `ConnectionState`, NIP-42 `AuthState`, `AUTH_TIMEOUT`.
  - root `AGENTS.md:145-160` confirms Buzz's primary API is NIP-29 over WebSocket.

STEP 1  Write the node body against templates/interface.md's skeleton         [independent]
        Create `launchpad/docs/corpus/interfaces/websocket/event.md` with front matter
        (`id: interfaces-websocket-event`, `type: interfaces-events`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer]`) and a body covering, per
        the template's Required sections: (1) Interface description -- both directions,
        client->relay `["EVENT", <signed-event>]` (NIP-01) and relay->client
        `["EVENT", <subscription_id>, <event>]`; (2) Operations table pointing at
        `ClientMessage::parse`/`Event`, `handlers::event::handle_event`,
        `RelayMessage::event`, `fan_out_event_to_local_subscribers`,
        `fan_out_pubsub_event`, and NIP-01 itself; (3) Contract and stability -- the OK
        shape, the message-prefix convention, NIP-42 auth-required gating, AUTH_TIMEOUT
        ordering, and `duplicate:` idempotency; (4) Boundary statement -- not a single
        event kind's wire contract, not a parameter catalogue, not the HTTP equivalent
        (named by filename in prose, not `relationships[]`, since #979 is unmerged);
        (5) Relationships -- `implements: corpus-template-interface`, `references`
        toward the four flow nodes; (6) Scope and omissions. Include one valid example
        (successful EVENT -> OK true -> push to a subscriber) and one failure example
        (e.g. `auth-required:` rejection), both grounded in exact strings observed in
        `handlers/event.rs`. Classify every evidence entry FACT/INFERENCE/TEAM_KNOWLEDGE
        honestly, citing only sources actually opened.
        done when: the file exists at
        `launchpad/docs/corpus/interfaces/websocket/event.md` with front matter
        containing exactly `id`, `type`, `status`, `origin`, `audiences`, `evidence`,
        `relationships` (schema-legal fields only) and a body with all six required
        sections, satisfying every Definition-of-done bullet in issue #1021.

STEP 2  Validate                                                    [needs 1]  <- RUNS HERE
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        repository root. Fix any FAIL line the new node introduces (schema errors,
        unresolved `relationships[].target`, bad citation shapes). UNVERIFIED notices
        are expected and acceptable.
        done when: the command exits 0, and any FAIL lines present are pre-existing
        (not attributable to the new file) -- if a pre-existing FAIL exists, it is
        reported as a finding, not silently worked around.

STEP 3  Earn the commit gate                                        [needs 2]
        Run, as the sole command in its own tool call:
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        done when: the command prints `OK` (unittest's success marker).

STEP 4  Commit                                                      [needs 3]
        <!-- COPY -->
        ```
        git add launchpad/docs/corpus/interfaces/websocket/event.md launchpad/plans/2026-09-01-issue-1021-interfaces-websocket-event.md
        git commit -s -m "docs(corpus): document WebSocket EVENT interface (#1021)"
        ```
        done when: `git log -1` shows the new commit with a `Signed-off-by` trailer and
        `git status` shows a clean tree. If the commit is rejected for a missing gate
        stamp, do not touch any stamp file and do not use `--no-verify` -- report it as
        a finding instead.

STEP 5  Self-review                                                 [needs 4]
        Re-read the diff against issue #1021's Definition-of-done checklist line by
        line. Confirm every evidence entry supports its claim, confirm no second
        hand-authored canonical corpus document was created, and re-run `validate.py`
        to confirm it still exits 0.
        done when: all DoD bullets are checked off against the actual file content, and
        `validate.py` exits 0 on the final tree.

PARALLEL  None of steps 1-5 are parallelizable -- each depends on the previous step's
          artifact (the node file, then its validation, then its test-gate stamp, then
          the commit, then the re-review of the committed diff).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          (step 2). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
          (step 3), run alone in its own tool call before the commit. `git commit -s`
          must succeed without `--no-verify` (step 4). No `review-*` skill applies --
          this is a documentation-only corpus change with no code diff and no runtime
          behavior to exercise, so `qa` explore mode does not apply.

BUDGET    Step 1 (writing the node body) is the step most likely to eat the budget --
          drafting an accurate Operations table and Contract-and-stability section that
          cites real code symbols correctly is the bulk of the work.

OPEN      Whether `interfaces/http/events.md` (issue #979) will declare a
          `relationships[]` edge back to this node once it merges -- left to that
          node's own author, per the corpus's "add edges once both sides exist"
          convention. Whether a future event-kind node (e.g. for kind:1 or kind:9002)
          should gain a `references` edge from this interface node -- deferred until
          such a node exists.

LEFT OUT  No changes to `interfaces/http/events.md` or any other corpus node besides
          the plan and the new interface node -- issue #1021 scopes exactly one
          hand-authored document. No runtime/product code changes -- this is
          documentation only. No relationship to `interfaces-http-events` -- unmerged,
          would be a hard validation error against `origin/launchpad`.

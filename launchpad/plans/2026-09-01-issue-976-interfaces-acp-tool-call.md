Issue #976 — task: document interfaces/acp/tool-call.md
Stated size: none stated  →  cap: 5 steps (the issue's own dispatch instructions call
this "a small single-document task" and cap plans at 5 steps)

Target file: `launchpad/docs/corpus/interfaces/acp/tool-call.md`
Node id: `interfaces-acp-tool-call` (assigned by the dispatch brief; permanent)
Base branch: `origin/launchpad` at 650354eab8d41ab6ce1a71de079a6c6d95c69052

ALREADY TRUE  (verified against git at 650354eab8d41ab6ce1a71de079a6c6d95c69052, not notes)
  `git status --short` in this worktree is empty before this plan file is added; HEAD
    equals `origin/launchpad` exactly (`git rev-parse HEAD origin/launchpad` both print
    650354eab8d41ab6ce1a71de079a6c6d95c69052).
  `launchpad/docs/corpus/interfaces/` does not exist anywhere in the merged corpus tree
    (`git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists no
    `interfaces/` prefix) — this task creates the directory and is the corpus's first
    interface-shaped instance node.
  `node.schema.json`'s `type` enum has 13 members and no bare `interface` value; the
    combined value is `interfaces-events`. `templates/interface.md`'s own front matter
    confirms this reading directly ("A node built from this template therefore carries
    `type: interfaces-events`").
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
    status `active`) is merged on `origin/launchpad` and prescribes: Interface
    description, Operations (table pointing at code symbols/spec methods, never
    restating them), Contract and stability, Boundary, Relationships, Scope and
    omissions. It documents this template node itself under `type: governance`, not
    `interfaces-events` — that value is reserved for instance nodes like this one.
  `corpus-template-interface` is therefore a valid `relationships[].target` today
    (resolves against `origin/launchpad`, the merge target), which the template
    itself flags as optional via an `implements` edge.
  Issues #973–975 (protocol/message/session siblings) are not present in
    `origin/launchpad`'s corpus tree — no id from any of them is a valid
    `relationships[].target` yet; they are mentioned in prose by filename only, per
    the dispatch brief's explicit instruction.
  `crates/buzz-acp/src/acp.rs` implements the ACP client (`buzz-acp` is the ACP
    *client*; the spawned agent subprocess — goose / codex-acp / claude-agent-acp /
    buzz-agent — is the ACP *server*). Tool-call reporting arrives as `session/update`
    notifications with `sessionUpdate: "tool_call"` (handled at
    `handle_session_update`, matched at acp.rs:1762) and `"tool_call_update"`
    (acp.rs:1774); permission gating arrives as a `session/request_permission`
    *request*, handled by `handle_permission_request` (acp.rs:1934), which always
    searches for the `allow_once` option by `kind` and never hardcodes an
    `optionId`, falling back to `reject_once` if absent, and returning
    `AcpError::Protocol` if neither exists.
  `build_client_capabilities()` (acp.rs:393) advertises only `auth.terminal` and two
    `_meta` extensions (goose custom notifications, claude-agent-acp terminal-auth) —
    no `fs` or `terminal` client capability is advertised, so buzz-acp never executes
    a tool call itself; it only observes and approves/rejects.
  `initialize()` (acp.rs:611) always requests `protocolVersion: 2` but never checks
    the value the agent returns; `lib.rs:4703` and `lib.rs:4795` read it only for
    logging/observability (`unwrap_or(1)` on absence), matching the ACP spec's own
    negotiation contract (fetched from https://agentclientprotocol.com/protocol/schema:
    the agent may return the client's version "if supported ... or the latest
    protocol version supported by the agent").
  Unit tests already exercise the exact claims above: `find_allow_once_by_kind_not_by_option_id`
    (acp.rs:2400), `find_allow_once_returns_none_when_absent` (acp.rs:2423),
    `find_reject_once_fallback_when_no_allow_once` (acp.rs:2440),
    `permission_request_with_string_id` (acp.rs:2659),
    `permission_cancelled_response_preserves_id_type` (acp.rs:2688), and
    `tool_call_resets_idle_then_silence_times_out` (acp.rs:3419-3452, a live-process
    test proving a `tool_call` notification resets the idle timer).

STEP 1  Create the file and directory with schema-valid front matter          [independent]
        Create `launchpad/docs/corpus/interfaces/acp/tool-call.md` (new directories
        `interfaces/` and `interfaces/acp/`) with front matter: `id:
        interfaces-acp-tool-call`, `type: interfaces-events`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, one
        `relationships` entry (`type: implements`, `target:
        corpus-template-interface`), and the commit-only FACT recording revision
        650354eab8d41ab6ce1a71de079a6c6d95c69052. Body carries only a one-line H1 and
        a placeholder Interface-description paragraph so the file is schema-valid
        before the remaining sections exist.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0
                   with the new file on disk, and `git cat-file -e
                   650354eab8d41ab6ce1a71de079a6c6d95c69052` exits 0.

STEP 2  Write Interface description and Operations          [needs 1]  ← RUNS HERE
        Write the Interface description paragraph (ACP JSON-RPC 2.0 over NDJSON
        stdio; buzz-acp is the client, the spawned agent process is the server; the
        boundary this node covers is the agent reporting a tool invocation and
        buzz-acp observing/gating it — buzz-acp never executes the tool itself,
        evidenced by `build_client_capabilities()` advertising no `fs`/`terminal`
        capability). Write the Operations table: `session/update` (`tool_call`,
        `tool_call_update`) and `session/request_permission`, each row citing the
        acp.rs symbol/line that handles it plus the ACP spec page fetched for that
        method, never restating the full field list from memory.
        done when: validator exits 0; every Operations row has a matching `evidence`
                   entry classified FACT and citing an acp.rs line opened in this
                   session (checked by re-opening each cited line).

STEP 3  Write Contract and stability, plus valid/failure examples          [needs 2]
        Write Contract and stability: the `allow_once`-by-kind /
        `reject_once`-fallback rule (never `allow_always`/`reject_always`, an
        INFERENCE with confidence, since the code never searches for those two kinds
        but no comment states why); the double-response guard ("write the response
        first, then mark as responded", acp.rs:1996-2010) and its cancellation path
        (`cancel_with_cleanup` sends `outcome: cancelled` for a still-pending
        permission request); the protocol-version negotiation behavior from
        ALREADY TRUE; and the two concrete outcomes as evidence, not paraphrase:
        one valid example (a `tool_call` notification resetting the idle timer, from
        `tool_call_resets_idle_then_silence_times_out`) and one failure example (no
        `allow_once` and no `reject_once` present, which `handle_permission_request`
        turns into `AcpError::Protocol`, terminating the read loop with an error
        rather than hanging).
        done when: validator exits 0; the body names at least one valid example and
                   one failure example, each citing a specific test function; and no
                   sentence in this section asserts a guarantee no cited source
                   makes (checked by re-reading each cited acp.rs span against the
                   sentence above it).

STEP 4  Write Boundary, Relationships, and Scope and omissions          [needs 3]
        Write the Boundary section using the template's own two exclusions (not a
        single event kind's wire contract — none exists to reference yet; not a
        domain-expert parameter catalogue) plus this node's own: it does not cover
        the ACP session-lifecycle methods (`session/new`, `session/prompt`,
        `session/cancel`) that issues #974/#975 own, named by filename
        (`interfaces/acp/session.md`, `interfaces/acp/message.md`) rather than by
        relationship edge, since neither id resolves against `origin/launchpad` yet.
        Write the Relationships section restating the one declared edge and stating
        why no others are declared. Write Scope and omissions per `AGENTS.md` step
        8: what this node does not cover (who owns it) and, separately, what was
        expected but not verified — the ACP spec's own JSON Schema document was
        fetched via two page-scoped queries, not downloaded and diffed against
        acp.rs field-by-field.
        done when: validator exits 0; the Boundary section names both template
                   exclusions plus the session-lifecycle one; and `grep -c
                   '^relationships:' launchpad/docs/corpus/interfaces/acp/tool-call.md`
                   prints `1`.

STEP 5  Audit the finished node, run the full gate, commit          [needs 4]
        Re-read the whole diff against issue #976's Definition-of-done checklist
        line by line: exactly one hand-authored document; schema-valid front
        matter; one independently maintainable idea (no session/prompt or
        session/new content folded in); every substantive claim has a correctly
        classified evidence entry; links to implementation (acp.rs lines) and the
        authoritative spec (agentclientprotocol.com) without restating either;
        checked against the recorded revision; at least one valid and one failure
        example present. Fix anything the audit finds, then run the corpus
        validator and the corpus schema test suite, then commit.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits
                   0; `python3 -m unittest discover -s
                   launchpad/project-intelligence/corpus/tests -p "test_*.py"`
                   prints `OK`; and `git log -1 --format=%H` on this branch shows a
                   new commit containing exactly
                   `launchpad/docs/corpus/interfaces/acp/tool-call.md` and this plan
                   file.

PARALLEL  None. All five steps edit the same single file (STEP 1 also creates its
          two parent directories), and the skill's own rule is that steps touching
          one file are sequential regardless of how unrelated they look. There is no
          second artefact to fan out to — the issue's Definition of Done caps this
          task at exactly one hand-authored document, and the sibling nodes
          (#973-975) are separate issues being written in parallel, not part of this
          plan.

GATES     Self-run `check-plan.sh` on this plan before STEP 1 (already run once
          below this file is written; re-run after any edit). No `review-plan`,
          `review-code`, or `review-tests` subagent pass is dispatched for this
          task — the enclosing task instructions specify a fixed self-review step
          (STEP 5 above) rather than the separate reviewer-agent gate, and this
          plan does not override that. `review-tests` does not apply regardless:
          the diff adds one Markdown file and one plan file and touches no test
          file (STEP 5 *runs* the existing corpus test suite but does not modify
          it). The commit itself is the gate that matters here: the enclosing
          instructions require the corpus unit-test suite to print `OK` in its own
          isolated command before `git commit -s` is attempted, and forbid working
          around a rejected commit (no stamp-file edits, no `--no-verify`).

BUDGET    STEP 3. Getting the permission-kind fallback and the protocol-version
          negotiation behavior right requires distinguishing "what the ACP spec
          permits" (fetched from agentclientprotocol.com) from "what buzz-acp's code
          actually does" (a narrower subset — only two of four permission kinds,
          no negotiated-version enforcement) without asserting a guarantee neither
          source makes. The specific trap this template's own evidence-expectations
          section names: an operation-table row or contract claim is a FACT or
          nothing, never an assumption dressed as one.

OPEN      Whether `interfaces-acp-tool-call` should `references` a
          not-yet-existing event-kind node for any Nostr event this flow touches.
          Resolved here as no: tool-call reporting is pure ACP JSON-RPC (stdio),
          carries no Nostr event of its own, and citing a kind that does not
          participate would be exactly the "wrong subject" case the interface
          template's own Boundary section warns against.

          Whether the INFERENCE about buzz-acp intentionally restricting itself to
          single-use permission kinds (never `allow_always`/`reject_always`) is
          confident enough to state plainly. Resolved here as INFERENCE with a
          stated confidence rather than FACT, because no code comment or commit
          message gives the reason directly — only the absence of those two kinds
          from the search predicate is observed.

LEFT OUT  Any `references` edge to the sibling protocol/message/session nodes
          (#973-975). None of their ids resolve against `origin/launchpad` today;
          the dispatch brief requires prose/filename mentions instead, and adding
          the edges is a natural follow-up once any of those three merge.

          A second hand-authored corpus document of any kind, including editing
          `launchpad/docs/corpus/templates/interface.md` to record this as its
          first instance. The issue's own out-of-scope list forbids a second
          canonical document, and the template needs no edit to remain accurate.

          Re-deriving buzz-dev-mcp's MCP tool-call wire format (the shell/file-edit
          tools the agent may call via MCP once the ACP layer has approved the turn).
          That is a distinct protocol from ACP's own tool-call reporting and, per
          the interface template's Boundary guidance, a different interface node's
          subject if the corpus ever documents it.

          Enumerating every ACP `ToolKind` value (read/edit/delete/move/search/
          execute/think/fetch/other) as a table. acp.rs treats `kind` as an opaque
          string it only logs; restating the spec's own closed enum here would be
          exactly the re-encoding the interface template's *Industry models
          considered* section warns against for an externally owned protocol.

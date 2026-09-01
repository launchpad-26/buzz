# Plan: issue #988 — corpus node `interfaces-mcp-protocol`

Stated size: none given (single-document corpus task per issue #988's own title/DoD)  ->  cap: 5 steps

ALREADY TRUE  (verified against git and GitHub, not notes)
  `launchpad/docs/corpus/interfaces/mcp/protocol.md` does not exist — confirmed via
    direct `ls` in this worktree (checked out from `origin/launchpad`).
  `launchpad/docs/corpus/schema/node.schema.json`'s `type` enum has 13 members and the
    only interface-shaped one is `interfaces-events` (single hyphenated token; PRD #602
    lists "interfaces/events" as one combined surface, not two).
  `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`,
    `status: active`) is already merged on `origin/launchpad` and requires: an interface
    description paragraph, an Operations table pointing at (never restating) defining
    sources, a Contract-and-stability section, a Boundary statement, Relationships, and
    Scope-and-omissions.
  `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
    `architecture-containers-agent-runtime`, `status: draft`) is already merged on
    `origin/launchpad` and already names `buzz-dev-mcp` as the container's MCP tool
    surface — a valid `part-of` target.
  `crates/buzz-dev-mcp/src/lib.rs` implements the MCP **server** side: `rmcp`'s
    `transport::stdio()`, a `#[tool_router]`/`#[tool_handler]` server (`DevMcp`), and
    `ServerInfo` advertising `Implementation::new("buzz-dev-mcp", env!("CARGO_PKG_VERSION"))`
    with `enable_tools()` only (no resources/prompts capability).
  `crates/buzz-agent/src/mcp.rs` implements the MCP **client** side: `TokioChildProcess`
    transport, `env_clear()` + an explicit `PASSTHROUGH_ENV` allowlist per spawned server,
    qualified `server__tool` naming, `list_all_tools()`, `CallToolRequestParams` calls,
    `notifications/cancelled` on cancel (fire-and-forget), transport-error vs.
    application-level-JSON-RPC-error handling, and backoff/restart with a max-attempts
    budget.
  Root `Cargo.toml:136` pins `rmcp = { version = "1.1.0", features = ["server",
    "transport-io", "macros"] }`; `Cargo.lock` resolves it to `1.8.0`.
  `crates/buzz-dev-mcp/src/shim.rs` shows `NOSTR_PRIVATE_KEY` is deliberately excluded
    from the trust boundary the protocol otherwise relies on: written to a 0600 keyfile,
    then removed from the server's own process env before any shell child is spawned.
  The official MCP spec (fetched directly: `/specification/2025-06-18/basic/transports`
    and `/basic/lifecycle`) documents stdio framing (newline-delimited JSON-RPC, stdout
    reserved for protocol messages, stderr for logs), the `initialize`/`initialized`
    handshake with `protocolVersion` negotiation, and a stdio shutdown sequence
    (close stdin -> SIGTERM -> SIGKILL) that matches this repo's own `killpg`-based
    teardown in shape, not text.
  No sibling corpus node for #987 (file-edit tools) or #989 (shell tool) is merged on
    `origin/launchpad` yet — they are not valid `relationships` targets.

STEP 1  [independent] Write `launchpad/docs/corpus/interfaces/mcp/protocol.md`: front
        matter with `id: interfaces-mcp-protocol`, `type: interfaces-events`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
        a commit-citation provenance entry for the revision recorded in ALREADY TRUE, one
        `evidence` entry per substantive claim (classified FACT/INFERENCE/TEAM_KNOWLEDGE
        per `AGENTS.md`'s rules — no `confidence` on FACT/TEAM_KNOWLEDGE, no
        `provided_by` on FACT/INFERENCE), and `relationships: [{type: implements, target:
        corpus-template-interface}, {type: part-of, target:
        architecture-containers-agent-runtime}]` (both targets confirmed merged in
        ALREADY TRUE). Body follows the template's required sections: Interface
        description, Operations table (rmcp-mediated `initialize`/`tools/list`/
        `tools/call`/`notifications/cancelled`, each pointing at the citing code or the
        MCP spec, never restating the wire format), Contract and stability (transport,
        versioning via the `rmcp` pin, error/rejection split between transport-fatal and
        application-level JSON-RPC errors, restart/backoff behavior, cancellation being
        best-effort per spec and per code), Boundary (excludes: the shell/file-edit/
        view_image/todo tool-specific contracts owned by #987/#989; a domain-expert
        parameter catalogue; front matter/procedure, owned by `node.schema.json`/
        `AGENTS.md`), Relationships, and Scope and omissions naming what was expected but
        not verified (e.g. the exact `protocolVersion` string `rmcp` 1.8.0 negotiates was
        not independently confirmed against `rmcp`'s own source). Include one valid
        example (a successful `shell` tool call round-trip) and one failure example
        (malformed/non-object arguments rejected before any transport send, per
        `validate_arg_shape`, and a JSON-RPC application error surfaced as `is_error:
        true` text rather than killing the server). RUNS HERE.
        done when: the file exists at that path and is well-formed YAML+Markdown (no
        parse error from `python3 launchpad/project-intelligence/corpus/validate.py`).

STEP 2  [needs 1] Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        the repo root and fix any FAIL it reports on the new node (broken relationship
        target, invalid citation shape, schema violation). UNVERIFIED notices on
        commit/URL citations are expected and not a failure.
        done when: the command exits 0.

STEP 3  [needs 2] Run `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` alone, in its own
        call, to earn the commit-gate stamp.
        done when: the command prints `OK`.

STEP 4  [needs 3] `git add` the plan and the new node file, then `git commit -s` with a
        `docs(corpus): document MCP protocol interface (#988)` message.
        done when: `git log -1` shows the new commit with a `Signed-off-by` trailer and
        `git status` shows a clean tree.

STEP 5  [needs 4] Self-review the diff line-by-line against issue #988's Definition-of-
        done checklist (inputs/messages, outputs/responses, error/rejection behavior,
        auth/authz, versioning/compatibility, ordering/idempotency, spec link, valid +
        failure examples, exactly one hand-authored canonical document, no runtime code
        changes) and re-confirm every `evidence` entry against the source it cites.
        done when: every DoD bullet is traceable to a specific section/citation in the
        committed file, and `validate.py` still exits 0 on the committed tree.

PARALLEL  None. Single file, single worktree, no fan-out — steps are strictly sequential
          (write -> validate -> test-gate -> commit -> self-review).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before
          commit (step 2). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`,
          run alone in its own call, before commit (step 3) — this is the commit-gate
          stamp, not a substitute for validate.py. No `--no-verify`; if the commit hook
          still rejects for a missing gate stamp, that is reported as a finding, not
          routed around. Cross-model/adjudication review is explicitly deferred to the
          batch owner, per this corpus batch's established convention — not run in this
          session.

BUDGET    One corpus Markdown file, one plan file, one commit. No code changes, no
          generated-index regeneration (none exist yet to regenerate), no second
          hand-authored document.

OPEN      Whether `rmcp` 1.8.0's negotiated `protocolVersion` string exactly matches
          `2025-06-18` (the spec version fetched for this plan) was not independently
          verified against `rmcp`'s own source — the node will record this as an
          expected-but-unverified gap rather than assert a version it did not confirm.
          Whether a corpus-wide convention prefers `implements` or `references` for a
          node's optional self-link to its own template is unsettled (per the template's
          own Scope-and-omissions) — this plan follows the template's own stated
          preference (`implements`) rather than resolving that convention question.

LEFT OUT  No relationship to #987 (file-edit tools) or #989 (shell tool) — neither is
          merged on `origin/launchpad` yet, so no valid target id exists; those nodes will
          `references` this one once merged, not the reverse, per the interface
          template's own guidance on interface-to-neighbor edges. No restatement of the
          MCP specification's full wire format (cited, not re-encoded, per the template's
          evidence expectations). No change to `buzz-dev-mcp` or `buzz-agent` runtime
          code — this task documents the existing contract, it does not modify it. No
          field-by-field parameter catalogue for every tool's schema (that is #987/#989's
          territory, or a future reference-depth node per `#1346`/`#1532`).

Issue #989 — task: document interfaces/mcp/shell-tool.md
Stated size: issue #989 carries no explicit `Size` line; the dispatching task instructions cap this single-document task at 5 steps  ->  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  Worktree `__worktrees/task-989-interfaces-mcp-shell-tool` on branch `task/989-interfaces-mcp-shell-tool`,
    based on `origin/launchpad` HEAD 650354eab8d41ab6ce1a71de079a6c6d95c69052, working tree clean.
    `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
    `launchpad/docs/corpus/templates/interface.md` (id `corpus-template-interface`) are merged and
    authoritative. `node.schema.json`'s `type` enum's interface-shaped value is the single token
    `interfaces-events` (no separate `interface` value exists). `launchpad/docs/corpus/interfaces/`
    does not exist at all yet on `origin/launchpad` — this will be the first node under it.
    `architecture-containers-agent-runtime` (`launchpad/docs/corpus/architecture/containers/agent-runtime.md`)
    is merged and names `buzz-dev-mcp` as one of the agent runtime's three crates, making it a valid
    `part-of` target. The sibling MCP interface nodes for issues #987 (protocol) and #988
    (file-edit-tool) are NOT merged on `origin/launchpad` and are being written in parallel worktrees,
    so they are not valid `relationships` targets and are mentioned by filename in prose only.
    `crates/buzz-dev-mcp/src/shell.rs` (1503 lines), `src/shim.rs` (695 lines) and `src/lib.rs`
    (213 lines, the `#[tool(name = "shell", ...)]` registration) have been read in full.

STEP 1  [independent]  Re-confirm the evidence already gathered against current HEAD: `shell.rs`'s
        `ShellParams` (command/workdir/timeout_ms), `run()`'s spawn/timeout/cancel/kill-group control
        flow, the `finalize_stream` truncation-to-artifact behavior, the `resolve_bash`/`BUZZ_SHELL`
        dialect resolution; `shim.rs`'s per-session shim directory, PATH prepending, and
        `NOSTR_PRIVATE_KEY` removal from the process env; `lib.rs`'s tool registration string (the
        MCP tool's own advertised description) and `run()`'s `SharedState::new` wiring; and
        `buzz-acp/src/lib.rs`'s `build_mcp_servers` (the only non-test `McpServer` construction site),
        which spawns `buzz-dev-mcp` over stdio per agent session with `BUZZ_RELAY_URL`,
        `BUZZ_PRIVATE_KEY` and optionally `BUZZ_AUTH_TAG` injected as env vars — the authorization
        boundary the node must describe precisely (OS-process trust, not a caller-auth check inside
        the tool itself).
        done when: every claim planned for the body has a specific opened source (path + symbol,
        or line range) recorded, including the constants `DEFAULT_TIMEOUT_MS`/`MAX_TIMEOUT_MS`/
        `MAX_COMMAND_BYTES`/`CAPTURE_CAP`/`MAX_BYTES`/`MAX_LINES`/`TAIL_BYTES` and both a passing
        (`basic_echo`) and failing (`timeout_fires`) test in `shell.rs`'s own test module.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/interfaces/mcp/shell-tool.md` per
        `corpus-template-interface`'s required sections (Interface description, Operations, Contract
        and stability, Boundary, Relationships, Scope and omissions). Front matter: `id:
        interfaces-mcp-shell-tool`, `type: interfaces-events`, `status: draft`, `origin: launchpad`,
        `audiences: [agent, developer, reviewer]`, `relationships: [{type: implements, target:
        corpus-template-interface}, {type: part-of, target: architecture-containers-agent-runtime}]`.
        Body must satisfy issue #989's own DoD checklist: the tool-call input schema (`command`,
        `workdir`, `timeout_ms` with their defaults/caps), the JSON response shape (`exit_code`,
        `stdout`/`stderr` with truncation-to-artifact behavior, `timed_out`, `duration_ms`,
        `*_truncated`, `*_artifact`, `notes`), error/rejection behavior (invalid params vs. tool-error
        content vs. cancellation), the authorization boundary (per-session subprocess spawn with
        injected relay/key env vars — no in-tool caller authentication), versioning/compatibility
        (no MCP protocol version pin found; note as a gap if so), ordering/idempotency (each call
        spawns an independent ephemeral process — no ordering guarantee across calls), a link to the
        authoritative spec (the `ShellParams`/`#[tool(...)]` registration in code, since no separate
        JSON Schema artifact exists), and one valid example (`basic_echo`-style) plus one failure
        example (`timeout_fires`-style) grounded in the actual test module.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and every
        issue-989 DoD bullet is addressed by a distinct, evidenced section.

STEP 3  [needs 2]  Re-run `python3 launchpad/project-intelligence/corpus/validate.py` after any
        fixes prompted by STEP 2's own validation pass, confirming no FAIL line is introduced by
        this new node (pre-existing FAILs elsewhere, if any, are reported as a finding, not silently
        worked around).
        done when: the command exits 0, or any surviving FAIL is confirmed to be pre-existing and
        unrelated to this node and is reported in the final message.

STEP 4  [needs 3]  Self-review the diff line-by-line against issue #989's DoD checklist: confirm
        every evidence entry's citation actually supports its statement (re-open the source), confirm
        exactly one hand-authored corpus document was created, and confirm no second canonical
        document exists in the diff.
        done when: the line-by-line audit is complete and `validate.py` still exits 0 on the current
        tree.

STEP 5  [needs 4]  Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own tool call to earn the commit gate's
        verification stamp; confirm it prints `OK`. Only then, in a separate tool call, `git add` the
        plan and the new document and `git commit -s`.
        done when: the unittest run reports `OK` and `git commit -s` succeeds without `--no-verify`;
        if the commit is rejected for a missing gate stamp, that is reported as a finding rather than
        routed around.

PARALLEL  None — single new file under a not-yet-existing `interfaces/` subtree; steps are strictly
          sequential (evidence gathers before the body cites it; the body must exist before it can be
          validated or audited). Issues #987 and #988 are separate parallel worktrees authoring
          sibling MCP interface nodes with no file overlap and no relationship edges between any of
          the three (none of the three is merged yet, so none is a valid target for the others).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
          `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
          "test_*.py"` must print `OK` immediately before the commit, as the commit gate's own
          verification stamp. `review-adjudicate` and the cross-model final review pass are deferred
          to the batch owner's review — not run in this worktree. No PR is opened by this task.

BUDGET    STEP 2. The hard part is describing the authorization boundary precisely — this is a
          shell-execution tool with no in-tool caller authentication; the actual boundary is
          "whoever can launch the `buzz-dev-mcp` subprocess and speak MCP stdio to it runs arbitrary
          shell commands as the host OS user of that process" — without either overstating a
          sandbox that does not exist or understating the real env-scoping (`NOSTR_PRIVATE_KEY`
          stripped from the process env, PATH shimmed to a 0700 per-session tempdir) that does.

OPEN      Issue #989's DoD bullet on "versioning/compatibility" has no clear code-level answer:
          no MCP protocol version pin or `shell` tool schema version was found anywhere in
          `buzz-dev-mcp` or its `Cargo.toml` (only the crate's own `CARGO_PKG_VERSION`, which
          versions the binary, not the tool contract). This is reported as a genuine gap in the
          node's own evidence rather than resolved by inventing a versioning scheme the code does
          not have.

LEFT OUT  Any `references` edge to a Nostr event-kind node — the shell tool has no Nostr event-kind
          identity; it is a pure MCP tool-call surface, so no event-kind template subject applies.
          Editing `launchpad/docs/corpus/architecture/containers/agent-runtime.md` or any other
          existing node. A second canonical document for the sibling `read_file`/`str_replace`/
          `view_image`/`rg`/`tree`/`todo` MCP tools in the same crate — each is (or will be) its own
          task; this node documents only the `shell` tool operation. Windows-specific shell-resolution
          internals (`resolve_bash`'s registry/PATH probing, `KillGroup`'s Job Object mechanics)
          beyond what the Contract and stability section needs to state the cross-platform guarantee
          — those are implementation detail, not interface contract, and are cited by file/symbol
          rather than restated.

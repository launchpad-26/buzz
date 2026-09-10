Issue #987 — task: document interfaces/mcp/file-edit-tool.md
Parent Feature #616. No `Size` label on the issue (labels: type:task, area:docs,
by:agent). Per the task brief this plan is capped at 5 steps as a small
single-document task rather than guessed at from a missing Size line.
Stated size: no Size label on issue #987; task brief caps this single-document task -> cap: 5 steps.

ALREADY TRUE
  `launchpad/docs/corpus/schema/node.schema.json` (type enum includes
  `interfaces-events`, no bare `interface`/`interfaces` value), `launchpad/docs/corpus/AGENTS.md`,
  and `launchpad/docs/corpus/templates/interface.md` (`id: corpus-template-interface`,
  the interface-node skeleton) are all merged on `origin/launchpad`
  (HEAD 650354eab8d41ab6ce1a71de079a6c6d95c69052). No `launchpad/docs/corpus/interfaces/`
  directory exists yet anywhere in the corpus tree — confirmed via
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`, which lists
  zero paths under `interfaces/`. `crates/buzz-dev-mcp/src/str_replace.rs` implements the
  `str_replace` MCP tool (registered in `lib.rs` lines 74-83), backed by
  `crates/buzz-dev-mcp/src/paths.rs` (`resolve_path`, `read_text_file`, `MAX_FILE_BYTES`)
  and `crates/buzz-dev-mcp/src/shell.rs` (`SharedState`, default `workdir`). Root
  `Cargo.toml` pins `rmcp = { version = "1.1.0", features = ["server", "transport-io",
  "macros"] }`.

STEP 1  [independent]  Confirm the target does not exist and finish evidence-gathering
        for the node: re-open `crates/buzz-dev-mcp/src/lib.rs` (the `str_replace` tool's
        registered name/description, lines 74-83, and `DevMcp::get_info`/`run()` for
        transport and server-info), `str_replace.rs` in full (params struct, error paths,
        atomic-write behavior, both the "outside workspace" and "file too large" tests),
        `paths.rs` in full (`resolve_path`'s explicit no-containment posture and its doc
        comment, `MAX_FILE_BYTES`, `read_text_file`'s stat/size/UTF-8 checks), and
        `shell.rs` for `SharedState`'s `cwd` field and how `workdir: None` falls back to
        it. Record the exact line ranges that will back each evidence-ledger claim.
        done when: `test ! -e launchpad/docs/corpus/interfaces/mcp/file-edit-tool.md`
        exits 0, and every file above has been re-opened in this session (not assumed
        from an earlier read).

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/interfaces/mcp/file-edit-tool.md` following
        `templates/interface.md`'s required sections: front matter (`id:
        interfaces-mcp-file-edit-tool` — matching the `<top-dir>-<subdir>-<stem>`
        pattern precedent set by `architecture-containers-relay` etc., `type:
        interfaces-events`, `status: draft`, `origin: launchpad`, `audiences: [agent,
        developer, reviewer]`, an `evidence` ledger citing only sources opened in STEP 1
        plus one commit citation for the recorded revision, and `relationships: [{type:
        implements, target: corpus-template-interface}]` — the only target confirmed
        loadable from `origin/launchpad`); and a body with: Interface description
        (MCP tool-call boundary between an MCP client, e.g. `buzz-agent`, and the
        `buzz-dev-mcp` server process over stdio), an Operations table naming `str_replace`
        only (citing `lib.rs`'s tool registration and `str_replace.rs`'s `run` function),
        Contract and stability (error/rejection behavior enumerated from STEP 1's error
        paths, the no-sandbox/no-containment posture as the authorization boundary,
        atomic-write ordering guarantee, the absence of any app-level protocol-version
        pin beyond the `rmcp` crate version), a Boundary paragraph excluding the sibling
        `read_file`/`shell`/`view_image`/`todo` tools and the MCP/Model Context Protocol
        specification itself, a Relationships section, and a Scope-and-omissions section
        naming `interfaces/mcp/protocol.md` and `interfaces/mcp/shell-tool.md` (issues
        #988/#989, sibling nodes written in parallel, not yet merged) by filename only —
        no `relationships` edge to either. Include one valid `str_replace` example and one
        failure example (old_str not found, or matched multiple locations).
        done when: the file exists, every `FACT`/`INFERENCE` entry cites a source actually
        opened in STEP 1, every `INFERENCE` carries `confidence`, and every
        `TEAM_KNOWLEDGE` entry carries `provided_by`.

STEP 3  [needs 2]  Validate the node against the corpus schema and checker.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0,
        with no FAIL line attributable to `interfaces-mcp-file-edit-tool` (a FAIL on any
        other node is reported as a fresh finding, not silently worked around).

STEP 4  [needs 3]  Earn the commit gate, then commit.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        prints `OK`, and `git commit -s` (no `--no-verify`) on the staged plan + node
        succeeds.

STEP 5  [needs 4]  Self-review the finished diff against issue #987's Definition-of-done
        checklist line by line, confirming no second hand-authored canonical corpus
        document was created and every evidence entry still supports its statement.
        done when: each DoD bullet is checked against the actual committed file and
        `python3 launchpad/project-intelligence/corpus/validate.py` still exits 0.

PARALLEL  None — single file, five sequential steps. Sibling issues #988
          (`interfaces/mcp/protocol.md`) and #989 (`interfaces/mcp/shell-tool.md`) are
          written by other agents in parallel over the same `interfaces/mcp/` directory
          but touch different filenames, so there is no file-level collision; this plan
          does not depend on either landing first and declares no relationship toward
          either.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
          (STEP 3). `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print `OK`
          before the commit gate will accept the commit (STEP 4). `review-adjudicate`
          and the cross-model final review pass are deferred to the batch owner's
          review, matching the precedent set by the #695-#698 corpus-doc plans — not
          run here.

BUDGET    STEP 2 is the hard part. The file-edit tool's actual behavior (no path
          containment, explicit by design per `paths.rs`'s own doc comment and proven by
          its own `run_allows_path_outside_workspace` test) is a real, verified fact that
          must be stated plainly as the authorization boundary rather than assumed to be
          sandboxed. Evidence scope: 4 source files in `crates/buzz-dev-mcp/src/`
          (`lib.rs`, `str_replace.rs`, `paths.rs`, `shell.rs`), 2 `Cargo.toml` files, and
          the already-read `node.schema.json` / `AGENTS.md` / `templates/interface.md`.

OPEN      Whether an `INFERENCE` claim that `rmcp`'s `#[tool_router]`/`#[tool(...)]`
          macros generate the MCP `inputSchema` from `StrReplaceParams`'s
          `schemars::JsonSchema` derive is confident enough to state without having read
          the `rmcp` crate's own source (not vendored in this checkout, not found under
          `~/.cargo`) — handled by stating it as `INFERENCE` with a confidence reflecting
          that it was reasoned from the crate's declared `macros` feature and the derive
          usage, not read directly, rather than omitted or asserted as `FACT`.

LEFT OUT  Any second hand-authored canonical corpus document. Documenting `read_file`,
          `view_image`, `shell`, or `todo`/`_Stop`/`_PostCompact` — each is a distinct
          MCP tool with its own contract and belongs in its own node (`shell` is #989's
          job) rather than folded into this one per `AGENTS.md`'s one-idea-per-node rule.
          Fixing or relaxing `paths.rs`'s no-containment posture — that is implementation
          work with its own issue, not something this documentation task owns or should
          silently paper over. Declaring `relationships` toward #988/#989's nodes before
          either merges — the same merge-order hazard `AGENTS.md` step 9 and
          `standards/evidence.md` both name for a target absent from the current merge
          base.

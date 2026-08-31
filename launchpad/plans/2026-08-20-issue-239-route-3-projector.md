# Issue #239 — Route 3 projector: resolve a pack into a write-capable runtime

Stated size on #239: none given — asked pattern from #8/#74 applies: exceeds an
hour on its face (new script, new merge-write logic that does not exist anywhere
in the repo, a real end-to-end proof). Cap: 11 steps.

Repository: `block/buzz`. All impacted components live here — unlike #74, this
is not cross-repo.

---

ALREADY TRUE — verified against the repository, not notes

- `crates/buzz-persona/src/resolve.rs:108`'s `resolve_pack()` is real, tested,
  and already returns everything a projector needs: `ResolvedPersona` (lines
  22-65) carries `model`, `llm_provider`, `temperature`, `max_context_tokens`,
  `mcp_servers: Vec<ResolvedMcpServer>` (already a list — pack + persona
  merged), `triggers`, and `runtime_env_vars: Vec<(String, String)>`
  (pre-projected pairs). Nothing needs to be re-derived; it needs to be
  *consumed*, for the first time anywhere in this repo.
- **No code anywhere calls `resolve_pack()` except `buzz pack
  validate`/`inspect` (human-facing, `println!` only, no JSON) and
  `buzz-persona`'s own tests.** Confirmed by grep: zero hits in
  `crates/buzz-acp`, `crates/buzz-agent`, `desktop/src-tauri`.
- `buzz-acp`'s actual spawn-time config comes from CLI flags/env vars only
  (`crates/buzz-acp/src/config.rs:191-201,250-262,504-556`) — `agent_command`,
  `agent_args`, `mcp_command: String` (singular), `model`, and
  `persona_env_vars: Vec<(String,String)>` (declared, but nothing today
  populates it from a pack — `config.rs:1058-1070` only ever pushes a
  Codex-specific sandbox var into it). This is the exact seam a projector's
  *env-var* half plugs into.
- **`buzz-acp` is capped at exactly one MCP server**, and the cap is narrower
  than either the protocol or the persona layer: `NewSessionRequest.mcp_servers`
  (`acp.rs:654,660,695,700`) and `ResolvedPersona.mcp_servers`
  (`resolve.rs:55`) are both already `Vec`. The cap is specifically
  `Config.mcp_command: String` (singular) and `build_mcp_servers`
  (`lib.rs:5122-5177`), which can only ever produce 0 or 1 `McpServer`. The
  Professor's own pack has exactly one MCP server (`professor-tools`), so this
  does not block this issue — but widening it is real, separate engineering.
  See LEFT OUT.
- **Goose's write/shell capability is a config-FILE toggle, not an env var.**
  `desktop/src-tauri/src/managed_agents/config_bridge/goose.rs:106-136` parses
  an `extensions:` map from `~/.config/goose/config.yaml` (or
  `$GOOSE_PATH_ROOT/config/config.yaml`, resolved at `goose.rs:157-163`), where
  `developer: {type: builtin, enabled: true}` is the literal shape (confirmed
  by that file's own test at `goose.rs:234-254`). Grepped for
  `GOOSE_ENABLE_EXTENSIONS` and equivalents repo-wide: zero hits. There is no
  env-var route to this at all.
- **No merge-write logic for that YAML file exists anywhere in this repo.**
  `goose.rs` (312 lines) is entirely read-only — no `write`/`save`/
  `serde_yaml::to_writer` for goose's config anywhere, confirmed by a
  repo-wide grep. A projector that needs to *enable* the developer extension
  without clobbering an operator's existing goose config (other providers,
  other extensions) has to build read-merge-write from scratch. `goose_config_path()`
  (`goose.rs:157-163`) is reusable for path resolution; nothing else is.
- The Professor's own persona (`personas/the-professor.persona.md:9-13`) has
  every trigger off: `mentions: false`, `keywords: []`, `all_messages: false`
  — a deliberate choice made building #9 (commit history: "Step 9: Wire
  draft-page skill and turn triggers fully off"). #239's own DoD bullet 3
  ("mention it in a channel") cannot be satisfied without enabling one, even
  temporarily, for the proof run.
- #239's own "Out of scope" section already answers where that proof runs:
  "Production-grade relay hosting for The Professor running live inside Buzz
  — #9 used a throwaway local relay to prove drafting behaviour only; live
  operation answering channels is PRD stage 4." So the end-to-end proof
  reuses #9's own throwaway-local-relay precedent, not live Buzz — this
  plan does not need to invent that answer, only follow the issue's own text.
- `buzz pack inspect` (`crates/buzz-cli/src/commands/pack.rs:52-147`) is
  `println!`-only, no `--format json` or any machine-readable mode. Confirmed
  by reading the whole function.

## The scope decision #239's own DoD demands an explicit answer to

**Recommendation: this first pass targets the handbook's existing
page-contract-shaped drafting only — the same scope #9 already proved — not
the broader "any codebase, any task type" scribe role.**

Why: the write-path gap this issue fixes is orthogonal to *what* is being
drafted. Solving it for the already-built, already-proven handbook role is the
minimal-scope path, and the projector itself (pack → runtime config, pack →
goose write-capability) is *not* Professor-specific at all — building it
generic (STEP 3 below) means the broader scribe role, whenever it is designed,
reuses this same projector rather than needing its own. Building the broader
role's design *and* this write-path simultaneously would conflate two
separable, both-real pieces of engineering. This is a recommendation, not a
decision already taken — flagged here per the DoD's own instruction that
silence is not acceptable either way.

---

STEP 1   Add `--format json` to `buzz pack inspect`                              [independent]
         (`crates/buzz-cli/src/commands/pack.rs`). Reuses `resolve_pack()`'s
         already-tested resolution faithfully — the alternative, a second
         script re-parsing pack YAML independently, would duplicate
         precedence-resolution logic (operator env > frontmatter > pack
         defaults, PERSONA_PACK_SPEC.md §10) in a second language, and the two
         would drift the first time either changed. Emits the full
         `ResolvedPersona` shape as JSON (one object per persona in the pack).
         done when: `buzz pack inspect --format json launchpad/agents/the-professor`
         emits valid JSON containing `model`, `temperature`, `mcp_servers`,
         `triggers`, matching what `--format` (human) already prints for the
         same pack.

STEP 2   `launchpad/agents/project-pack.py` (or `.sh` — pick whichever reads      [needs 1]
         cleaner given the goose YAML work in step 4): a GENERIC projector, not
         hardcoded to The Professor. Takes a pack directory and a persona name;
         calls `buzz pack inspect --format json <dir>`; for the chosen
         persona, emits an env-var file (`GOOSE_PROVIDER`/`GOOSE_MODEL`
         split from `model`+`llm_provider`, `GOOSE_TEMPERATURE`,
         `GOOSE_CONTEXT_LIMIT`, `BUZZ_ACP_AGENT_COMMAND`/`_AGENT_ARGS`,
         `BUZZ_ACP_MCP_COMMAND`) per PERSONA_PACK_SPEC.md §10's exact mapping.
         **Operator env vars must win** — the projector must check
         `os.environ` before writing a value, mirroring the spec's own
         precedence rule and `buzz-acp`'s own `std::env::var(key)` check
         (spec line 653/831), or a human's explicit override gets silently
         clobbered by the projector.
         done when: run against The Professor's pack, the emitted file's
         values match `buzz pack inspect --format json`'s output exactly, and
         a pre-set `GOOSE_MODEL` in the calling shell survives untouched.

STEP 3   MCP-server projection, and the plurality gap named rather than          [needs 2]
         worked around. The Professor's pack has exactly one MCP server, so
         `BUZZ_ACP_MCP_COMMAND=<that command>` fully projects it today.
         Explicitly does NOT attempt to make `buzz-acp` accept multiple MCP
         servers — that needs `Config.mcp_command: String` widened to a list
         and `build_mcp_servers` rewritten, which is `buzz-acp`'s own
         cross-cutting change, not a projector-script concern. Documented here
         so the cap is stated, not silently inherited. See LEFT OUT.
         done when: the emitted `BUZZ_ACP_MCP_COMMAND` matches
         `.mcp.json`'s one entry; a fixture pack with two persona-level
         `mcp_servers` entries makes the projector fail loudly (not silently
         drop the second one) rather than pretend it projected both.

STEP 4   Goose config.yaml read-merge-write, built from scratch since nothing    [independent, converges with 2-3 at step 5]
         reusable exists (confirmed: `goose.rs` is 100% read-only). Reads the
         file at `goose_config_path()` if it exists (empty mapping if not),
         preserves every existing key untouched, sets
         `extensions.developer = {type: builtin, enabled: true}`, writes to a
         temp file in the same directory and renames over the original —
         atomic, so a crash mid-write cannot leave a half-written config an
         operator's next `goose` invocation trips over.
         done when: run twice against a fixture config.yaml carrying an
         unrelated provider block and one other extension — both survive
         byte-for-byte except the added/updated `developer` entry, and running
         it a second time is a no-op (idempotent, not append-again).

STEP 5   Wire steps 2-4 into one invocation: `project-pack.py the-professor`     [needs 3, 4]
         does the env-var emission and the goose-config patch in one
         deterministic run — "the pack changed, run this, the runtime
         matches it," no other human step, per #239's own DoD bullet 1.
         done when: a single command run against a freshly-cloned repo with no
         prior goose config produces both a sourceable env file and a
         `developer`-enabled `config.yaml`.

STEP 6   Enable a trigger for the proof run ONLY, not for committed defaults.    [needs 5]
         Temporarily set `triggers.mentions: true` (or add one keyword) on a
         **copy** of the persona used for the local proof session — the
         committed `the-professor.persona.md` in this repo keeps
         `mentions: false` afterward. Live, cohort-wide trigger enablement is
         PRD stage 4 per #239's own Out-of-scope section, not this step.
         done when: the proof session's runtime genuinely responds to a
         mention; the committed pack file is unchanged by this step.

STEP 7   End-to-end proof, reusing #9's Step 16 precedent exactly: a throwaway   [needs 6]
         local relay, `buzz-acp` launched with step 5's projected env vars and
         patched goose config, a real mention posted in a local test channel.
         done when: The Professor drafts, SAVES the draft to disk via goose's
         now-enabled developer extension (not by hand, unlike #9's Step 16),
         and replies — zero controller intervention, matching #239's DoD
         bullet 3 word for word. Raw transcript/log evidence captured for the
         PR, same discipline as #9's own Step 16 evidence.

STEP 8   Revert step 6's temporary trigger change; confirm the repo's own       [needs 7]
         `git status` is clean of it. Re-run `buzz pack inspect` against the
         committed pack to reconfirm `triggers.mentions: false` is what ships.
         done when: `git diff` shows no persona-file change from this issue's
         work, only the new projector/CLI code.

STEP 9   `scripts`/tests for the projector and the CLI addition: unit tests for  [needs 1, 2, 3, 4 — can start once each lands]
         the env-var mapping (mirrors PERSONA_PACK_SPEC.md §10's table
         exactly, one test per mapped field plus the operator-override case),
         the goose-config merge (the two-run idempotency case from step 4,
         plus a "no existing file" case), and a `cargo test` for the new
         `--format json` flag's output shape.
         done when: every case above has its own test, and mutating the
         precedence check (operator wins) makes exactly one test fail.

STEP 10  Update `README.md`'s Runtime Route section from "Route 3 filed as a    [needs 7, 8]
         future issue" to present tense: name the projector, link this issue,
         and add one explicit sentence that the credential question for
         *unattended* operation (already flagged in the Credential Policy
         section) is still unanswered — this proof used a human-triggered
         local session under BYOK, not unattended operation.
         done when: the section names the real script path and the Step 16
         gap it closes, without overstating what was proven (a local,
         human-initiated session, not live cohort deployment).

STEP 11  Acceptance sweep against #239's four DoD boxes, evidence pasted into   [needs 7, 8, 9, 10]
         the PR body — including the raw transcript from step 7's proof run,
         not a summary of it.

---

PARALLEL  Steps 1 and 4 are genuinely independent of everything (4 needs no
          pack-resolution data at all — it operates on a fixture config.yaml
          until step 5 wires it to the real projector). Step 2 needs 1; step 3
          needs 2. Steps 6-8 are a strict chain (enable → prove → revert) and
          cannot be reordered. Step 9's sub-parts can start as soon as their
          corresponding step (1, 2, 3, or 4) lands, rather than waiting for
          all four.

GATES     `review-code` after step 4 (file-write logic touching a real local
          config file is exactly the class of change that deserves adversarial
          review — see #9's own PR #238, where `review-code` found a real
          security bug in far less risky read-only code) and after step 7 (the
          end-to-end run, since it is the first time this pack's runtime has
          real write/shell capability at all). `review-final` before merge.

BUDGET    Step 4 (goose-config merge-write) and step 7 (the live proof) are
          where the unknowns are: no prior art for the merge logic in this
          repo, and a live ACP+goose session is exactly the kind of thing that
          surprises on first real run (per #9's own Step 16 experience, which
          took multiple debug passes before the actual capability gap was
          understood). Budget accordingly.

DECIDED   Carried forward, not re-litigated: BYOK credential policy for a
          human-triggered local session (README, Credential Policy section) —
          this proof still uses that, unchanged. The proof environment is a
          throwaway local relay, not live Buzz (#239's own Out-of-scope text).

OPEN      1. **The scope-decision this plan recommends** (handbook-only first
             pass, see above) is a recommendation, not yet Serina's decision —
             #239's own DoD requires it be stated explicitly either way.
          2. **Who arbitrates whether goose's `developer` extension is safe
             enough to enable for a live/unattended run later** — not decided
             here. The README's Credential Policy section already flags that
             unattended operation needs its own credential decision; this plan
             adds that it also needs its own *write-capability* risk decision,
             since a live, unattended agent with real shell access is a
             materially different blast radius than a human-triggered local
             session under BYOK.

LEFT OUT  Widening `buzz-acp`'s `Config.mcp_command: String` to accept multiple
          MCP servers — real, separate engineering in `buzz-acp` itself
          (`config.rs`, `build_mcp_servers`), not a projector-script concern,
          and not needed for The Professor's own single-MCP-server pack. Worth
          its own issue if a future pack ever needs more than one.
          The broader "any codebase, any task type" scribe role — this plan's
          own scope recommendation defers it; #211 (The Librarian) is a
          separate agent and a separate concern per #239's own Out-of-scope
          text.
          Live, cohort-wide trigger enablement and production relay hosting —
          PRD stage 4, per #239's own Out-of-scope text, not reopened here.

SMALLER   Flagged because this exceeds an hour. Two shippable pieces live
VERSIONS  inside it: **(a)** steps 1-5 and 9 — the projector itself, fully
          testable offline against fixtures, useful and reviewable without
          ever running a live proof; **(b)** steps 6-8, 10-11 — the live proof
          and the documentation update, which need (a) merged first. Splitting
          is Serina's call, not this plan's; it is planned as one issue as
          written, matching #239's own single-issue framing.

Issue #9 — handbook D: The Professor, the drafting agent persona (v2, per launchpad/Research/the-professor-design.md)
Stated size: More than an hour (issue has no Size line; user-confirmed, revised upward twice — once for the tool-server requirement, once for standing up a real relay for Route 2)  →  cap: 21 steps

ALREADY TRUE  (verified against git and the live repos, not notes)
  #6, #7, #8, #10, #11 (PRD #4's other handbook sub-issues) are all CLOSED. #9 is the last
    open sub-issue. #87 (fenced ALL-CAPS misdetected as .env) is CLOSED. #90 (three container
    shapes bypass the claim rules) is OPEN — a detection gap (claims inside those shapes go
    unchecked), not something that blocks a correctly-written page from passing.
  `launchpad/Research/the-professor-design.md` (this session's commit b17078164, content
    brought forward from an orphaned branch `docs/the-professor-design`, 2026-08-12,
    independently checked by three reviewers per its own account) is now on this branch and
    is this plan's primary source, alongside issue #9 itself.
  The design doc's central, load-bearing finding: **no runtime in this fork today consumes
    resolved persona-pack configuration.** Traced through the desktop app's migration code
    (`migration/detach.rs` actively strips directory-backed team fields), the team-snapshot
    import path (rejects a persona-pack zip by magic bytes with an explicit message), and the
    absence of any `--pack` flag or `buzz_persona::` caller outside `buzz-cli`. A pack is
    authorable and validatable (`buzz pack validate`/`inspect`) but not runnable — this is by
    design on the desktop side, not a gap awaiting a patch.
  The design doc's recommendation for #9: Route 1 (manually recreate the persona in the
    desktop app from `inspect` output) or Route 2 (run a plain `buzz-acp` process, configured
    from the environment to match the pack's resolved values, with the pack's README stating
    plainly it is "a specification the runtime is configured to match"). Route 3 (a projector
    that resolves the pack and emits `buzz-acp` config, making the pack genuinely load-bearing)
    is explicitly named as its own future issue, not #9's job.
  The design doc's tool-design argument: a raw `github` MCP server risks an LLM writing a
    plausible-but-wrong 40-char commit SHA from memory ("a hallucination with a checksum's
    shape"). It specifies five purpose-built tools instead: `resolve_pin(repo, ref)` → full
    SHA, `path_exists_at(repo, commit, path)` → bool, `read_contract()` → the live page
    contract text (read at call time, never quoted into the prompt), `list_categories()` → the
    eleven nav slots, `check_page(draft)` → the gate's findings for a draft.
  `crates/buzz-dev-mcp` is upstream's own generic dev-tool crate (shell, grep, file read/write,
    view-image) shared via the root Cargo workspace — it is not Professor-specific and adding
    cohort-specific tools to it, or adding a new crate under `crates/` at all, blurs
    `launchpad/AGENTS.md`'s "we operate Buzz, we do not develop Buzz" boundary and entangles
    upstream's workspace member list with cohort code. `launchpad/review-agent/` is this fork's
    actual precedent for cohort-owned agent tooling: a plain Python script tree living entirely
    under `launchpad/`, not a Rust crate under `crates/`.
  Discovered this session, not in the design doc (which predates it): `check-models.sh`, a
    global hook invoked by this session's `verify-gate.sh` pre-commit check, treats ANY
    directory literally named `agents/` **at any nesting depth** as a Claude-Code-style
    subagent roster — `verify-gate.sh` selects roster directories via
    `grep -E '(^|/)agents/[^/]+\.md$'` over staged paths, not just top-level. A nested
    `launchpad/agents/the-professor/agents/the-professor.persona.md` (the design doc's own
    literal recommendation) DOES trigger it, and fails either way: with no `model:` set it's
    "inherits the dispatching session's model"; with the spec's own provider-prefixed format
    (`anthropic:claude-sonnet-4-...`) it fails `check-models.sh`'s model-ID regex, which only
    accepts Claude Code aliases/IDs, never Buzz's format. Fix used in this plan: `load_pack`
    does not require the inner persona directory be named `agents/` — the manifest's
    `personas` field is a `Vec<String>` of arbitrary relative paths, and the crate's own test
    helper (`crates/buzz-persona/src/pack.rs`, `make_pack`) uses `personas/{name}.persona.md`,
    matching the doc comment's own example layout (`pack.rs:10`, `///   personas/`) — the
    spec's "agents/pip.persona.md" is one example, not a requirement. This plan therefore names
    the pack's inner persona directory `personas/`, not `agents/`, while keeping the outer pack
    location at `launchpad/agents/the-professor/` per the design doc's directory choice. No
    bare `.md` is ever created directly inside `launchpad/agents/` itself (see Step 2).
  `launchpad/AGENTS.md` §3's directory table currently lists only: `AGENTS.md`,
    `AGENT_PR_TEMPLATE.md`, `labels.yml`, `sync-labels.sh`, `decisions/`, `docs/`, `deploy/`,
    `upstream-intel/`. No `agents/` row exists yet.
  The page contract, the five source repos/prefixes, ADR-0015's hybrid-authoring decision, the
    persona pack spec's actual field behaviour (env-var interpolation is literal passthrough,
    not implemented; `triggers: {}` resolves `mentions` to its built-in `true`; `buzz pack
    validate` does not check `skills:` paths resolve or that the persona body is non-empty),
    and `check_provenance.py`/`page_index.py`'s actual CLI usage and three-outcome model were
    all independently verified in this session's prior review round (commit 30540ee54) and
    still hold — the design doc does not contradict any of them.
  `buzz` is not on PATH in a fresh checkout; `cargo build --release -p buzz-cli` is required
    first. Current branch `task/9-the-professor-persona` (commit b17078164) has no
    `launchpad/agents/` directory yet.

STEP 1  Scaffold the pack directory and manifest.                            [independent]
        what: `launchpad/agents/the-professor/.plugin/plugin.json` (id, name, version,
        description, `personas: ["personas/the-professor.persona.md"]`, `mcp_config:
        ".mcp.json"` — the manifest field Step 7's server must be declared under) and a
        placeholder `personas/the-professor.persona.md` with complete frontmatter but a
        one-line stub body marked `<!-- VOICE: Serina writes this -->`. The inner persona
        directory is named `personas/`, not `agents/` (see ALREADY TRUE) — this is what keeps
        `check-models.sh` from ever scanning this pack's files, not the outer directory name.
        done when: `cargo build --release -p buzz-cli` has produced `./target/release/buzz`,
        AND `./target/release/buzz pack validate launchpad/agents/the-professor` exits 0.

STEP 2  Update `launchpad/AGENTS.md` §3 with the `agents/` row and its rules.  [independent]
        what: add the `agents/` row and the naming-collision + no-bare-.md rule, instead of a
        separate `launchpad/agents/README.md`. add `agents/            persona packs for Buzz-native agents (see
        launchpad/Research/the-professor-design.md)` to the directory-table code block, and
        one paragraph stating: (a) `launchpad/AGENTS.md` (contributor guide) and
        `launchpad/agents/` (persona packs) are different things with adjacent names, and
        (b) no bare `.md` file may sit directly in `launchpad/agents/` — this session's
        `check-models.sh` hook scans that exact shape as a Claude Code subagent roster and
        blocks the commit; pack documentation belongs inside each pack's own subdirectory
        (e.g. `launchpad/agents/the-professor/README.md`), never at the top level.
        done when: `git diff launchpad/AGENTS.md` shows the new row and paragraph, and
        `grep -c '^  agents/' launchpad/AGENTS.md` returns 1.

STEP 3  Build the tool-server skeleton with `read_contract` and `list_categories`. [needs 1] ← RUNS HERE
        what: `launchpad/agents/the-professor/tools/` (Python, mirroring
        `launchpad/review-agent/`'s convention — plain scripts under `launchpad/`, not a new
        Rust crate; the entry script must be executable with its own shebang, since Step 7's
        `buzz-acp` wiring can only spawn a single bare command, no arguments — see Step 7), a
        stdio JSON-RPC MCP server exposing `read_contract()` (fetches `launchpad-26/handbook`'s
        `docs/page-contract.md` live, never quotes it into a prompt) and `list_categories()`
        (parsed from the handbook's live `mkdocs.yml` nav at call time, per the design doc's
        own default — "nothing quoted from a document that changes" — NOT hardcoded: PRD #4
        Ruling 3 names eleven categories, but the live `mkdocs.yml` nav currently has 13
        entries including Home and The page contract, which are not user-need categories in
        Ruling 3's sense — state which entries `list_categories` excludes and why, rather than
        asserting a literal count here that the live site may no longer match).
        done when: invoking the server's `list_categories` method directly (e.g. via a small
        test harness sending one JSON-RPC request over stdio) returns a category list matching
        whatever the live `mkdocs.yml` nav actually contains at call time (verify by diffing
        the tool's output against a fresh fetch of `mkdocs.yml`, not against a number fixed in
        this plan), AND `read_contract` returns text containing the literal string
        "The claim rule" fetched from the live handbook — first genuinely running artifact in
        this plan.

STEP 4  Implement `resolve_pin(repo, ref)`.                                   [needs 3]
        what: calls the GitHub API (`GET /repos/{repo}/commits/{ref}`) and returns the full
        40-character SHA. Requires `GITHUB_TOKEN` exported — an unauthenticated call risks the
        same rate-limit-looks-like-a-defect trap found in this plan's prior review round.
        done when: calling `resolve_pin("block/buzz", "main")` returns a 40-hex-character
        string that `git ls-remote https://github.com/block/buzz main` confirms is a real,
        current commit on that branch.

STEP 5  Implement `path_exists_at(repo, commit, path)`.                       [needs 3]
        what: calls the GitHub contents API at the pinned commit, returns a bool.
        done when: `path_exists_at("block/buzz", <a known-good SHA>, "crates/buzz-persona/PERSONA_PACK_SPEC.md")`
        returns true, AND the same call with a fabricated path returns false (both cases
        exercised, not just the happy path).

STEP 6  Implement `check_page(draft)` by calling the gate directly.           [needs 3]
        what: obtain a local checkout of `launchpad-26/handbook`'s `scripts/` AND
        `tests/fixtures/` (both — `check_provenance.py`'s imports resolve from `scripts/`
        alone, but the fixtures used to prove this step live under `tests/fixtures/`, a
        separate top-level directory). Requires `GITHUB_TOKEN`/`GH_TOKEN` exported and PyYAML
        installed (`page_index.py` imports it) — an unauthenticated or missing-dependency run
        fails for reasons unrelated to `check_page` itself. `check_provenance.py` only accepts
        a directory (`rglob`s for `*.md`), so each fixture under test must be copied into its
        own scratch directory containing nothing else — pointing at `tests/fixtures/` wholesale
        runs all 16 fixtures at once and `tests/fixtures/README.md` (no frontmatter) reports as
        `skipped`. Per the design doc's own open question 5: call the real gate, do not
        reimplement its rules — a second parser drifts from the first.
        done when: `check_page` run against `tests/fixtures/compliant.md` (isolated in its own
        scratch dir) returns zero findings AND zero skipped, AND run against
        `tests/fixtures/broken-03-prefix-repo-mismatch.md` (isolated the same way) returns a
        `prefix-repo-mismatch` finding. (NOT `broken-01-behaviour-claim-unsourced.md` — that
        fixture isolates a judgement-engine rule per `tests/fixtures/README.md`'s own
        engine-column, which `check_provenance.py`'s docstring says explicitly it does not
        implement; running it returns zero findings regardless of whether `check_page` works,
        so it cannot serve as a negative control. `broken-03`, `-04`, `-05`, `-07`, `-08`,
        `-09` and `-13` are all script-engine fixtures and fire deterministically.)

STEP 7  Wire `.mcp.json` to launch this tool server instead of raw `github` MCP. [needs 1, 4, 5, 6]
        what: `launchpad/agents/the-professor/.mcp.json`, `mcpServers.professor-tools.command`
        pointing at the `tools/` server's executable entry script directly (per Step 3's note,
        one bare path — `buzz-acp`'s `mcp_command` takes a single command string with no args,
        so the script needs its own shebang and execute bit, not a `python3 <path>` two-token
        invocation). No `${VAR_NAME}` for `GITHUB_TOKEN` at all: since interpolation is not
        implemented (literal passthrough, per prior review round), the tool server instead
        reads `GITHUB_TOKEN` directly from its OWN process environment at startup — which it
        inherits from whatever spawns it (`buzz-acp`, in turn inheriting the shell's exported
        env), sidestepping the interpolation gap entirely rather than working around it.
        done when: `.mcp.json` parses as valid JSON, contains no literal secret, `buzz pack
        validate` exits 0, AND `buzz pack inspect launchpad/agents/the-professor` reports a
        non-zero MCP server count (`validate` alone does not prove the manifest's
        `mcp_config` field was actually declared and read — see ALREADY TRUE's Step-1 update).

STEP 8  Write the drafting skill.                                            [needs 1]
        what: `skills/draft-page/SKILL.md` (required `name:`/`description:` frontmatter),
        instructing the agent to call `resolve_pin`/`path_exists_at` rather than write a SHA
        from memory, to call `read_contract` rather than assume the contract's shape, to tag
        every behaviour claim with an origin prefix and attribute every opinion claim to
        `author`, and to call `check_page` on its own draft before declaring the task done.
        done when: the SKILL.md file exists with non-empty `name:`/`description:` frontmatter.

STEP 9  Wire `skills:` and turn triggers fully off.                          [needs 7, 8]
        what: list `draft-page` in the persona's `skills:` using the exact path step 8 wrote
        it to; set `subscribe: []` and `triggers: {mentions: false, keywords: [],
        all_messages: false}` explicitly (an empty `triggers: {}` resolves `mentions` back to
        its built-in `true` — not "off").
        done when: `buzz pack validate` exits 0; `buzz pack inspect
        launchpad/agents/the-professor` lists `draft-page` under skills with no active
        trigger; AND `test -f launchpad/agents/the-professor/skills/draft-page/SKILL.md`
        succeeds (`validate` alone does not check the path resolves).

STEP 10 Set identity + temperature with a written, reasoned starting value.   [needs 9]
        what: fill `name`, `display_name`, `description`, `author`, `model`, `temperature`.
        The empirical observation design doc §6 requires cannot exist until a real drafting
        attempt happens (Step 15) — this step records the REASONED starting choice only (the
        tension between factual synthesis wanting it low and voice wanting room, and which way
        this pack leans and why); Step 18 adds what was actually observed once Step 15 has run,
        so the plan does not ask for evidence before the evidence can exist.
        done when: `temperature` is set in the frontmatter AND
        `launchpad/agents/the-professor/README.md` states the chosen value and the reasoned
        justification (not yet an observation); `buzz pack validate` still exits 0.

STEP 11 Decide and document the runtime route: Route 2.                     [needs 10]
        what: Route 2 (plain `buzz-acp` process, configured from the environment to match
        this pack's resolved values) over Route 1 (manual desktop-app recreation), because
        Route 2 is scriptable and testable in this session and Route 1 is a GUI action that
        is not. State plainly in the README (extending Step 10's file, not overwriting it):
        "this pack is a specification the runtime is configured to match, not configuration
        the runtime reads" — the design doc's own honest framing. Route 3 (a projector making
        the pack genuinely load-bearing) is filed as a separate follow-up issue in Step 19,
        not built here.
        done when: the README states the chosen route and the specification-vs-configuration
        caveat in those or equivalent words.

STEP 12 Decide and document where the draft goes.                            [needs 6]
        what: the design doc's OWN conclusion on this question is the opposite of what this
        step chooses — it argues the provenance gate only truly enforces on pull requests, so
        "only a pull request against the handbook puts the output where the enforcement
        already is," and a scratch-path draft is "a draft nothing checks." This plan diverges
        from that deliberately, for #9's bounded acceptance only: #9's acceptance criteria
        ("drafts a page... passes the gate without hand-editing") does not itself require a PR,
        Steps 16-17 run the gate manually against the scratch draft, and a real write path
        against a private repository is a separate permission-boundary decision the design doc
        says is unscoped (its Open question 2) — not something to back into via #9's PR.
        Confirm the tool server built in Steps 3-6 has no write tool, so this divergence
        doesn't accidentally acquire write capability it was never scoped for.
        done when: the README (extended, not overwritten) states this decision, AND a review
        of the five tool functions confirms none performs a write, push, or PR-create call.

STEP 13 Hand the persona voice to Serina.                          [needs 8, 9, 10, 11, 12]
        what: replace the `<!-- VOICE -->` stub in the persona's markdown body with the real
        prompt. NOT done by whoever implements this plan — per issue #9's explicit exclusion
        and the standing rule that creative/voice content here is Serina's to write. Steps 11
        and 12 (which block the persona body per the design doc's own framing of its two open
        questions) must be resolved before this step, not treated as later cleanup — reflected
        in the dependency tag itself now, not only in this prose.
        done when: the markdown body no longer contains the stub comment, `buzz pack validate`
        still exits 0, AND `buzz pack inspect launchpad/agents/the-professor` reports a
        non-zero `System prompt` character count.

STEP 14 Stand up a real local relay for the Route 2 proof.                   [needs 11]
        what: `buzz-acp` has no offline mode — `relay_url` and a private key are required
        arguments on its only runnable path (confirmed against `crates/buzz-acp/src/lib.rs`
        and `config.rs`; the `models`/`auth-methods`/`authenticate` subcommands are the only
        ones that bypass this, and none of them run an agent session) — so Route 2 needs a
        real relay, not a workaround. Per root `CLAUDE.md`: `. ./bin/activate-hermit`, `just
        setup` (installs deps, runs migrations), `just relay` (starts the relay at
        `ws://localhost:3000`). Generate a Nostr keypair for `BUZZ_PRIVATE_KEY` (confirm the
        exact mechanism here — no dedicated `buzz keys generate` subcommand was found in
        planning; `nostr_sdk::Keys::generate()` via a throwaway snippet, or an existing
        `buzz-test-client` fixture key, are the two candidates to check first) and export
        `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY`/`BUZZ_AUTH_TAG` per `.env.example`'s documented
        shape.
        done when: `just relay` is running and reachable (e.g. a WebSocket connection to
        `ws://localhost:3000` succeeds), AND a generated keypair's public key can be resolved
        against the running relay (confirms the key is usable, not just syntactically valid).

STEP 15 Start a real `buzz-acp` process per the Route 2 decision.           [needs 13, 14]
        what: export `GOOSE_PROVIDER`/`GOOSE_MODEL`/`GOOSE_TEMPERATURE` matching the values
        `buzz pack inspect` reports for this persona, point `buzz-acp` at the Step 7 MCP
        config and the Step 14 relay/keypair, and start the agent session.
        done when: the process connects to the Step 14 relay without error and the persona
        prompt (Step 13) is confirmed loaded — e.g. via whatever startup log or inspection
        `buzz-acp` provides.

STEP 16 Draft ONE real page using the running agent and its tools.         [needs 12, 15]
        what: `[upstream] Persona Pack format`, citing `block/buzz`
        (`crates/buzz-persona/PERSONA_PACK_SPEC.md`) pinned via `resolve_pin` (not memory —
        the specific failure mode Steps 3-6 exist to remove), plus one `[launchpad]` claim
        citing `launchpad-26/buzz` at a commit already on `refs/heads/launchpad` — e.g.
        `launchpad/AGENTS.md`'s §3 directory-table rules, or `launchpad/review-agent/`'s
        existence as this fork's agent-tooling precedent. NOT this plan's own branch commit:
        `resolve_pin`/`path_exists_at` resolve against the real GitHub API, and an unmerged
        branch commit is neither an ancestor of `refs/heads/launchpad` (fails `pin-not-
        ancestor`, a real gate FINDING, not `unchecked`) nor does the pack path exist yet on
        that ref (fails `pin-path-missing`) — citing anything this branch itself creates is
        gate-unpassable until after Step 19 merges it, which Step 19 cannot reach first.
        Written to a scratch path per Step 12's decision, not the live handbook nav.
        done when: a markdown file with complete frontmatter (all #7 fields) and at least two
        behaviour claims, each with a correct origin prefix and a `resolve_pin`-sourced
        full-SHA link **to already-merged content**, exists at a known scratch path.

STEP 17 Run `check_page` and `page_index.py` against the draft.             [needs 16]
        what: call the Step 6 tool (not a fresh ad hoc invocation) against the scratch
        directory containing exactly the one drafted page, plus `page_index.py` for
        frontmatter completeness (which `check_provenance.py` does not check).
        done when: `findings: []` AND `skipped: []` from `check_page`, AND `page_index.py`
        exits 0 — confirm the scratch directory holds exactly one page first, so an empty or
        wrong directory cannot masquerade as a clean run.

STEP 18 Fix any finding directly in the draft page.                         [needs 17]
        what: read each finding's message first — "could not be checked" or a network/rate-
        limit failure means the CHECK failed, not the page: fix the token/network and re-run
        Step 17 exactly, do not touch the page. Every other finding, or a `page_index.py`
        missing-field report, gets fixed in the page itself — no hand-edit around the gate.
        done when: re-running Step 17's exact commands reports zero findings, zero skipped,
        and a zero exit from `page_index.py`, with no manual exception added to either gate.

STEP 19 Extend the README with the observed behaviour + proof pointer.  [needs 10, 11, 12, 18]
        what: add to the SAME file Steps 10-12 wrote to (do not overwrite it): what was
        ACTUALLY observed running Step 10's chosen temperature against the real Step 16
        drafting attempt (design doc §6: "write down what you observed, not what you
        reasoned" — this is the step where an observation finally exists to write down),
        whether it reached the Route 2 runtime or not, one paragraph on what The Professor is,
        and the exact scratch path of the passing draft page (Steps 16-18) as evidence.
        done when: the README contains the temperature rationale (10), the observed behaviour
        from this step, the runtime-route caveat (11), the draft-destination decision (12),
        AND this step's additions, all in one file.

STEP 20 Open the PR closing #9, and file Route 3 as its own issue.          [needs 19]
        what: PR against `launchpad-26/buzz`; follow `launchpad/AGENT_PR_TEMPLATE.md`'s
        provenance table; link the Step 17 gate-pass output as evidence rather than
        re-asserting it in prose; file a new GitHub issue for the Route 3 projector (make the
        pack genuinely load-bearing) per the design doc's own recommendation, referencing this
        PR and the design doc.
        done when: `gh pr view` shows a PR with `Closes #9`, the provenance table filled in,
        gate JSON output linked, AND a new issue number exists for the Route 3 follow-up.

STEP 21 Record the merge-to-nav decision explicitly.                         [needs 18]
        what: decide whether the Step 16 draft page also merges into the live
        `launchpad-26/handbook` nav as real content, or stays proof-only — this is #10's
        territory (already closed) reopening if content changes, so it must be a stated
        decision in the PR description, not a silent merge.
        done when: a one-line decision is recorded in the PR description (merge to handbook
        nav now / leave as proof-only for now) — either answer is acceptable, silence is not.

PARALLEL  Steps 1 and 2 touch different files (the pack directory vs. `launchpad/AGENTS.md`)
          and have no dependency on each other — independent. Steps 4, 5 and 6 all depend on
          Step 3's server skeleton but implement separate tool functions in separate files
          (e.g. `tools/resolve_pin.py`, `tools/path_exists.py`, `tools/check_page.py`) — file-
          independent of each other, though `subagent-driven-development`'s own rule against
          parallel implementer dispatch means they would still be executed one at a time in
          practice, not concurrently, regardless of this file-level independence. Step 7
          (`.mcp.json`) needs all three tool implementations plus Step 1's manifest. Steps 10,
          11 and 12 all extend the same README file started in Step 10 — sequential by file,
          despite differing `needs` tags. Step 14 (relay standup) needs only Step 11's route
          decision and touches no pack file, so it could in principle run alongside Steps 12-13
          — but Step 15 needs both 13 and 14 regardless, so there is no wall-clock benefit
          worth the coordination cost. Steps 13 (Serina's own writing) through 21 are
          inherently sequential: voice → relay → runtime start → draft → gate → fix →
          document → PR.

GATES     serina:review-code after Step 8 (the tool server touches GitHub API calls, token
          handling, and subprocess invocation of the handbook's own gate scripts — real
          security surface, unlike the old docs-only plan). serina:review-plan on this plan
          itself before Step 1, per its own trigger — this plan has already been through one
          review round that found 3 Blockers and 3 High findings, all fixed above; a second
          pass before dispatch is warranted given the scale of the rework, not merely
          procedural. qa explore mode DOES apply here, unlike the prior version of this plan —
          there is a real runtime interface now (the MCP tool server's stdio protocol, and the
          Step 15 `buzz-acp` process against a real Step 14 relay) that must be exercised
          directly (Steps 3-6's done-when conditions already require this), not simulated.
          review-a11y does not apply (no UI surface). serina:review-final once the PR is
          ready, before merge, per standing practice on this repo.

BUDGET    Steps 3-6 (the tool server) and Step 14 (standing up a real relay: Docker/Postgres/
          Redis, migrations, a generated keypair) are both real candidates for eating the
          budget — the tool server is new engineering the original plan did not contain at
          all, closing the SHA-hallucination risk the design doc identified; the relay standup
          is infrastructure this plan only needs because `buzz-acp` has no offline mode, and
          getting a fresh local relay running correctly (migrations applied, a usable keypair,
          the port actually reachable) is exactly the kind of environmental setup that looks
          simple and rarely is on a first attempt.

OPEN      The exact mechanism for generating a usable Nostr keypair for Step 14's
          `BUZZ_PRIVATE_KEY` — no dedicated CLI subcommand was found during planning; the
          implementer must confirm one (a throwaway `nostr_sdk::Keys::generate()` snippet, or
          reusing an existing `buzz-test-client` fixture key) rather than the plan prescribing
          one it didn't verify. The exact `temperature` value (Step 10 requires it be chosen
          with a reasoned starting justification, then revised against Step 16's real
          drafting attempt at Step 19 — not prescribed here). Whether `launchpad-26/rhizomorph`
          is public or private (unverified in this or either prior planning pass — the gate's
          `unchecked` outcome absorbs either answer, so it does not block execution). Which
          `mkdocs.yml` nav entries `list_categories` should exclude as non-category (Step 3
          requires stating which were excluded and why, not asserting a fixed count).

LEFT OUT  Route 3 (the projector making the pack genuinely load-bearing) — real engineering
          the design doc itself defers to a separate issue, filed in Step 20. Zip-file
          packaging (`.buzzpack`/`.sha256`) and `pack.lock` — not required by #9's acceptance.
          Live-channel operation beyond the explicit off-state — excluded per issue #9 as PRD
          stage 4 (the Librarian job). A real write path / PR-against-handbook drafting flow —
          Step 12's decision diverges from the design doc's own preference for this reason,
          stated explicitly rather than silently. Writing the persona's actual voice —
          Serina's, at Step 13. The librarian-facing tools (`search_pages`, `page_by_category`,
          `page_sources`) the design doc lists for PRD stage 4 — not this issue's job.
          Production-grade relay hardening for Step 14 — this is a throwaway local instance for
          proving the drafting behaviour, not a deployed service; `launchpad/deploy/` already
          owns the real VPS relay and this plan does not touch it.

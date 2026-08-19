Issue #9 — handbook D: The Professor, the drafting agent persona (v2, per launchpad/Research/the-professor-design.md)
Stated size: More than an hour (issue has no Size line; user-confirmed, revised upward once the design doc's tool-server requirement surfaced)  →  cap: 20 steps

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
    directory literally named `agents/` anywhere in a commit as a Claude-Code-style subagent
    roster. It scans `"$dir"/*.md` **non-recursively** and requires every such file to carry
    `name:`/`model:` YAML frontmatter, or the commit is blocked ("does not belong in an agents
    directory"). Nested pack files (e.g.
    `launchpad/agents/the-professor/agents/the-professor.persona.md`) are NOT top-level `.md`
    in `launchpad/agents/` and do not trigger it — but the design doc's own recommended
    `launchpad/agents/README.md` (a bare prose file directly in that directory) WOULD trigger
    it. This plan avoids ever creating that specific file (see Step 2).
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
        description, `personas: ["agents/the-professor.persona.md"]`) and a placeholder
        `agents/the-professor.persona.md` with complete frontmatter but a one-line stub body
        marked `<!-- VOICE: Serina writes this -->`. Nothing bare-`.md` is created directly in
        `launchpad/agents/` itself (only inside the `the-professor/` subdirectory), so
        `check-models.sh` never scans this pack's files.
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
        Rust crate), a stdio JSON-RPC MCP server exposing `read_contract()` (fetches
        `launchpad-26/handbook`'s `docs/page-contract.md` live, never quotes it into a prompt)
        and `list_categories()` (the eleven nav slots, read from the handbook's `mkdocs.yml`
        nav or hardcoded from PRD #4 Ruling 3 — state which).
        done when: invoking the server's `list_categories` method directly (e.g. via a small
        test harness sending one JSON-RPC request over stdio) returns exactly 11 category
        names, AND `read_contract` returns text containing the literal string
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
        what: shells out to a local checkout of `launchpad-26/handbook`'s `scripts/` (obtain
        it here, not deferred to a later step — `check_provenance.py` is not self-contained,
        per the prior review round) and runs both `check_provenance.py` and `page_index.py`
        against the draft, returning their combined findings. Per the design doc's own open
        question 5: call the real gate, do not reimplement its rules — a second parser drifts
        from the first.
        done when: `check_page` run against the handbook's own `tests/fixtures/compliant.md`
        fixture (a page already known to satisfy the contract) returns zero findings, AND run
        against `tests/fixtures/broken-01-behaviour-claim-unsourced.md` returns at least one
        finding naming that specific rule.

STEP 7  Wire `.mcp.json` to launch this tool server instead of raw `github` MCP. [needs 1, 4, 5, 6]
        what: `launchpad/agents/the-professor/.mcp.json`, stdio command pointing at the
        `tools/` server, `GITHUB_TOKEN` via `${VAR_NAME}` (still a literal per the spec's
        current limitation — documented, not fixed here).
        done when: `.mcp.json` parses as valid JSON, contains no literal secret, and
        `buzz pack validate` exits 0.

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

STEP 10 Set identity + temperature with a written, evidence-based reason.     [needs 9]
        what: fill `name`, `display_name`, `description`, `author`, `model`, `temperature`.
        Per the design doc §6's rule: name the runtime first (Step 11 does this), confirm
        whether the setting reaches it, choose empirically against a small fixed set of
        drafting tasks rather than from first principles, and write down what was observed —
        not a number copied from `examples/meadow-core`'s Bana/Lev without re-testing here.
        done when: `temperature` is set in the frontmatter AND
        `launchpad/agents/the-professor/README.md` states the chosen value, what was actually
        observed at that value on a real drafting attempt, and whether it reaches the chosen
        runtime (Step 11) or not; `buzz pack validate` still exits 0.

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
        what: a scratch-path proof satisfies #9's stated acceptance ("drafts a page... passes
        the gate without hand-editing") without needing write access to
        `launchpad-26/handbook`. A real PR-against-the-handbook write path is the design doc's
        own "Route 3-scale" engineering and is out of scope for #9 (filed alongside Route 3 in
        Step 19). Confirm the tool server built in Steps 3-6 has no write tool.
        done when: the README (extended, not overwritten) states this decision, AND a review
        of the five tool functions confirms none performs a write, push, or PR-create call.

STEP 13 Hand the persona voice to Serina.                                    [needs 8, 9, 10]
        what: replace the `<!-- VOICE -->` stub in the persona's markdown body with the real
        prompt. NOT done by whoever implements this plan — per issue #9's explicit exclusion
        and the standing rule that creative/voice content here is Serina's to write. Steps 11
        and 12 (which block the persona body per the design doc's own framing of its two open
        questions) must be resolved before this step, not treated as later cleanup.
        done when: the markdown body no longer contains the stub comment, `buzz pack validate`
        still exits 0, AND `buzz pack inspect launchpad/agents/the-professor` reports a
        non-zero `System prompt` character count.

STEP 14 Start a real `buzz-acp` process per the Route 2 decision.            [needs 11, 13]
        what: export `GOOSE_PROVIDER`/`GOOSE_MODEL`/`GOOSE_TEMPERATURE` matching the values
        `buzz pack inspect` reports for this persona, point `buzz-acp` at the Step 7 MCP
        config, and start it as a one-shot agent session (no live relay connection required
        for this proof — confirm whether `buzz-acp` can run standalone; if it cannot, this is
        a real finding for OPEN, not a silent workaround).
        done when: the process starts without error and the persona prompt (Step 13) is
        confirmed loaded — e.g. via whatever startup log or inspection `buzz-acp` provides.

STEP 15 Draft ONE real page using the running agent and its tools.          [needs 12, 14]
        what: `[upstream] Persona Pack format`, citing `block/buzz`
        (`crates/buzz-persona/PERSONA_PACK_SPEC.md`) pinned via `resolve_pin` (not memory —
        the specific failure mode Steps 3-6 exist to remove), plus one `[launchpad]` claim
        about this cohort's own pack layout citing `launchpad-26/buzz` at this plan's own
        commit SHA, also via `resolve_pin`. Written to a scratch path per Step 12's decision,
        not the live handbook nav.
        done when: a markdown file with complete frontmatter (all #7 fields) and at least two
        behaviour claims, each with a correct origin prefix and a `resolve_pin`-sourced
        full-SHA link, exists at a known scratch path.

STEP 16 Run `check_page` and `page_index.py` against the draft.             [needs 15]
        what: call the Step 6 tool (not a fresh ad hoc invocation) against the scratch
        directory containing exactly the one drafted page, plus `page_index.py` for
        frontmatter completeness (which `check_provenance.py` does not check).
        done when: `findings: []` AND `skipped: []` from `check_page`, AND `page_index.py`
        exits 0 — confirm the scratch directory holds exactly one page first, so an empty or
        wrong directory cannot masquerade as a clean run.

STEP 17 Fix any finding directly in the draft page.                         [needs 16]
        what: read each finding's message first — "could not be checked" or a network/rate-
        limit failure means the CHECK failed, not the page: fix the token/network and re-run
        Step 16 exactly, do not touch the page. Every other finding, or a `page_index.py`
        missing-field report, gets fixed in the page itself — no hand-edit around the gate.
        done when: re-running Step 16's exact commands reports zero findings, zero skipped,
        and a zero exit from `page_index.py`, with no manual exception added to either gate.

STEP 18 Extend the README with what The Professor is + the proof pointer.  [needs 10, 11, 12, 17]
        what: add to the SAME file Steps 10-12 wrote to (do not overwrite it): one paragraph
        on what The Professor is, and the exact scratch path of the passing draft page (Steps
        15-17) as evidence.
        done when: the README contains the temperature rationale (10), the runtime-route
        caveat (11), the draft-destination decision (12), AND this step's additions, all in
        one file.

STEP 19 Open the PR closing #9, and file Route 3 as its own issue.           [needs 18]
        what: PR against `launchpad-26/buzz`; follow `launchpad/AGENT_PR_TEMPLATE.md`'s provenance table; link the Step 16
        gate-pass output as evidence rather than re-asserting it in prose; file a new GitHub
        issue for the Route 3 projector (make the pack genuinely load-bearing) per the design
        doc's own recommendation, referencing this PR and the design doc.
        done when: `gh pr view` shows a PR with `Closes #9`, the provenance table filled in,
        gate JSON output linked, AND a new issue number exists for the Route 3 follow-up.

STEP 20 Record the merge-to-nav decision explicitly.                         [needs 17]
        what: decide whether the Step 15 draft page also merges into the live
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
          despite differing `needs` tags. Steps 13 (Serina's own writing) through 20 are
          inherently sequential: voice → runtime start → draft → gate → fix → document → PR.

GATES     serina:review-code after Step 8 (the tool server touches GitHub API calls, token
          handling, and subprocess invocation of the handbook's own gate scripts — real
          security surface, unlike the old docs-only plan). serina:review-plan on this plan
          itself before Step 1, per its own trigger. qa explore mode DOES apply here, unlike
          the prior version of this plan — there is a real runtime interface now (the MCP tool
          server's stdio protocol, and the Step 14 `buzz-acp` process) that must be exercised
          directly (Steps 3-6's done-when conditions already require this), not simulated.
          review-a11y does not apply (no UI surface). serina:review-final once the PR is
          ready, before merge, per standing practice on this repo.

BUDGET    Steps 3-6 (the tool server) are most likely to eat the budget — this is real new
          engineering (GitHub API integration, subprocess orchestration of another repo's gate
          scripts, a working stdio MCP protocol implementation) that the original plan did not
          contain at all; it exists specifically to close the SHA-hallucination risk the design
          doc identified, and getting the GitHub API error handling and rate-limit behaviour
          right is exactly the kind of ground this plan's prior review round found expensive
          the first time (see the prior round's High findings on rate-limit-vs-defect
          confusion).

OPEN      Whether `buzz-acp` can run as a genuine one-shot standalone process with no live
          relay connection (Step 14 assumes yes; if it cannot, Route 2 itself needs revisiting
          before Step 14 can complete — this is a real technical unknown neither this plan nor
          the design doc verified against the running binary). The exact `temperature` value
          (Step 10 requires it be chosen empirically against real drafting attempts, not
          prescribed here). Whether `launchpad-26/rhizomorph` is public or private (unverified
          in this or the prior planning pass — the gate's `unchecked` outcome absorbs either
          answer, so it does not block execution). Whether `list_categories`' eleven slots
          should be hardcoded or fetched live from the handbook's `mkdocs.yml` nav (Step 3
          requires stating which was chosen, not which is correct).

LEFT OUT  Route 3 (the projector making the pack genuinely load-bearing) — real engineering
          the design doc itself defers to a separate issue, filed in Step 19. Zip-file
          packaging (`.buzzpack`/`.sha256`) and `pack.lock` — not required by #9's acceptance.
          Live-channel operation beyond the explicit off-state — excluded per issue #9 as PRD
          stage 4 (the Librarian job). A real write path / PR-against-handbook drafting flow —
          Step 12's decision defers this as Route-3-scale. Writing the persona's actual voice —
          Serina's, at Step 13. The librarian-facing tools (`search_pages`, `page_by_category`,
          `page_sources`) the design doc lists for PRD stage 4 — not this issue's job.

Issue #9 — handbook D: The Professor, the drafting agent persona
Stated size: More than an hour (issue has no Size line; user-confirmed)  →  cap: 12 steps

ALREADY TRUE  (verified against git and the live repos, not notes)
  #6 (repo + Pages), #7 (page contract), #8 (CI provenance/secret-scan gate), #10 (first
    content set), #11 (staleness + page index) are all CLOSED. #9 is the last open
    sub-issue of PRD #4.
  `launchpad-26/handbook` exists, private, org-restricted Pages, scaffold status
    ("Status — scaffold only" per its README) — pages exist but nothing is authoritative yet.
  The page contract (#7) is live at `launchpad-26/handbook/docs/page-contract.md`: required
    frontmatter is `title, summary, category, author, sources[].{repo,ref,commit,paths},
    reviewed.{by,date}, runnable, last_verified`; the claim rule requires every behaviour
    claim to carry an origin prefix (`[upstream] [launchpad] [cohort] [supporting]`) and a
    full-SHA source link, and every opinion claim to be attributed to `author`.
  The gate script is `launchpad-26/handbook/scripts/check_provenance.py [DOCS_DIR]
    [--format text|json]`, exit 0 = no findings, exit 1 = at least one finding. It reports
    three outcomes: finding (fails), unchecked (private-repo citations it cannot verify over
    the network — does not fail the build), skipped (no valid frontmatter — not a pass).
  The five source repos and origin prefixes (from #10): `block/buzz` → `[upstream]`,
    `launchpad-26/buzz` → `[launchpad]`, `launchpad-26/launchpad` → `[cohort]`,
    `launchpad-26/skills` → `[supporting]`, `launchpad-26/rhizomorph` → `[supporting]`.
  ADR-0015 (`launchpad/decisions/ADR-0015-handbook-page-authoring-mode.md`) decided hybrid
    authoring: The Professor drafts, the gate checks, a human reviews and merges every page
    (100% review until 30 pages or a second regular author) — no unattended publication.
  The persona pack format is specified in `crates/buzz-persona/PERSONA_PACK_SPEC.md` §4 and
    implemented in `crates/buzz-persona/src/{persona,manifest,pack,validate}.rs`; `buzz pack
    validate` exists (`crates/buzz-cli/src/commands/pack.rs`, PF-2 "Implemented").
  A working example pack already exists in this repo at `examples/meadow-core/` (`.plugin/plugin.json`
    + `agents/*.persona.md`) — the pattern to mirror, not invent.
  `launchpad/review-agent/` is this repo's existing precedent for a cohort-owned agent
    implementation living under `launchpad/`, not in a separate repo.
  Issue #9 explicitly excludes "The personality itself. Voice is authored, not specified —
    Serina writes the persona body." Only identity, wiring, and drafting behaviour are this
    issue's job.
  Current branch `task/9-the-professor-persona` is freshly cut off `origin/launchpad` — no
    Professor-related files exist anywhere in the tree yet (confirmed: no `*.persona.md` for
    a Professor, no `launchpad/personas/` directory).
  `buzz` is not on PATH in a fresh checkout — it must be built first: `cargo build --release
    -p buzz-cli`, then invoke `./target/release/buzz`.
  `buzz pack validate` only checks frontmatter shape (required identity fields, behavioral
    config types) — it does NOT check that `skills:` paths resolve to a real directory, and
    it does NOT check that the markdown body (the persona prompt) is non-empty. A pack with
    a dangling skill path or a zero-length prompt still validates clean.
  Per `PERSONA_PACK_SPEC.md` §7 and `crates/buzz-persona/src/resolve.rs`, MCP `${VAR_NAME}`
    env interpolation is "planned but not yet implemented" — such strings are passed through
    as **literal text** to the agent runtime today. A `.mcp.json` written now cannot actually
    authenticate; it can only be validated as well-formed and secret-free.
  Per `PERSONA_PACK_SPEC.md` §10, `triggers: {}` is NOT "off" — an empty object still
    overrides the pack default, but each sub-field then falls to ITS OWN built-in default,
    and `triggers.mentions`'s built-in default is `true`. The off state is
    `triggers: {mentions: false, keywords: [], all_messages: false}`, written explicitly.
  The page contract's frontmatter completeness (all required fields present, non-empty) is
    NOT checked by `check_provenance.py` — that script only checks claim-level rules (source
    refs, origin prefixes, secrets, structure). Frontmatter completeness is
    `launchpad-26/handbook/scripts/page_index.py`'s job; it refuses to emit an index and
    reports `missing required field: <name>` per missing field, exiting non-zero, for any
    page missing one of `title, summary, category, author, runnable, last_verified`.
  `check_provenance.py` reports a network failure or exhausted GitHub rate limit as a
    `finding` (not `unchecked`) — its own module docstring: "unavailable -> FINDING... Re-run
    it; do not merge past it." Running it without `GITHUB_TOKEN`/`GH_TOKEN` exported risks
    exactly this, indistinguishable in the findings array from a real page defect unless the
    message text is read.
  `check_provenance.py` is not self-contained — it imports a local `provenance` package (7
    modules) and, transitively, `page_index.py`. Running it requires a checkout of
    `launchpad-26/handbook`'s `scripts/` directory, not just the one file.
  A page whose YAML frontmatter fails to parse, or a docs directory containing no pages at
    all, produces `findings: []` from `check_provenance.py` — an empty `findings` array alone
    does not prove a page was checked. Proof requires `skipped: []` too, plus confirming the
    run actually saw the one page (e.g. asserting the scratch directory's page count).

STEP 1  Scaffold the `the-professor` pack directory and manifest.            [independent]
        what: `launchpad/personas/the-professor/.plugin/plugin.json` (id, name, version,
        description, `personas: ["agents/the-professor.persona.md"]`, no `defaults` needed
        for a single-persona pack); the persona file's frontmatter complete but its markdown
        body a one-line stub marked `<!-- VOICE: Serina writes this -->`.
        done when: `cargo build --release -p buzz-cli` has produced `./target/release/buzz`,
        AND `./target/release/buzz pack validate launchpad/personas/the-professor` exits 0.

STEP 2  Set identity + `temperature` with a written reason.                  [needs 1]
        what: fill `name`, `display_name`, `description`, `author`, `model`, `temperature`
        in the persona frontmatter. Issue #9 names the tension explicitly — factual synthesis
        wants low temperature, voice wants room — so pick one number and justify it in prose
        rather than leaving the choice implicit.
        done when: `temperature` is set in the frontmatter AND
        `launchpad/personas/the-professor/README.md` states the chosen value and the
        one-paragraph reason; `buzz pack validate` still exits 0.

STEP 3  Wire the `github` MCP server config for reading the five source repos. [needs 1] ← RUNS HERE
        what: `.mcp.json` with a `github` entry (stdio, `GITHUB_PERSONAL_ACCESS_TOKEN` via
        `${VAR_NAME}`, never a literal), scoped to read access. Per ALREADY TRUE, `${VAR_NAME}`
        interpolation is not implemented yet — this step produces well-formed, secret-free
        config, NOT working authentication; record that limitation in step 10's README rather
        than treating this as functional end-to-end wiring.
        done when: `launchpad/personas/the-professor/.mcp.json` parses as valid JSON, contains
        no literal secret, and `buzz pack validate` still exits 0 — first point the pack is a
        loadable artifact, not a proof that it can authenticate.

STEP 4  Write the drafting skill `skills/draft-page/SKILL.md`.               [needs 1]
        what: required `name:` + `description:` frontmatter per the pack spec; body walks the
        agent through reading the page contract, picking/confirming a `category`, pinning
        every cited source at a full 40-char commit SHA, tagging every behaviour claim with
        its origin prefix, attributing every opinion claim to `author`, and never asserting
        both for one claim.
        done when: the SKILL.md file exists with non-empty `name:` and `description:`
        frontmatter, and is listed in the Professor persona's `skills:` array.

STEP 5  Set `skills:`, `subscribe: []`, and `triggers` fully off.            [needs 4]
        what: list `draft-page` in `skills:` using the exact pack-relative path step 4 wrote
        it to (e.g. `./skills/draft-page/`); per issue #9's non-goal ("The Professor running
        live inside Buzz... is not required by #4"), set `subscribe: []` and
        `triggers: {mentions: false, keywords: [], all_messages: false}` explicitly —
        per ALREADY TRUE, `triggers: {}` alone resolves `mentions` back to its built-in
        default of `true`, which is not "off".
        done when: frontmatter has `subscribe: []` and the fully-off `triggers` object above;
        `buzz pack validate` exits 0; `buzz pack inspect launchpad/personas/the-professor`
        lists `draft-page` under skills AND `Triggers:` shows no active trigger; AND
        `test -f launchpad/personas/the-professor/skills/draft-page/SKILL.md` succeeds (the
        path in frontmatter actually resolves — `pack validate` does not check this).

STEP 6  Hand the persona voice to Serina to write.                          [needs 1]
        what: replace the `<!-- VOICE -->` stub in `agents/the-professor.persona.md`'s
        markdown body with the real prompt. NOT done by whoever implements this plan — per
        issue #9's explicit exclusion and the standing rule that creative/voice content here
        is Serina's to write.
        done when: the markdown body no longer contains the stub comment, `buzz pack validate`
        still exits 0, AND `buzz pack inspect launchpad/personas/the-professor` reports a
        non-zero `System prompt` character count — `validate` alone does not check the body
        is non-empty, so this second check is required to prove step 6 actually happened.

STEP 7  Draft ONE real page using the persona + skill as instructions.        [needs 2, 6]
        what: pick the smallest defensible target — `[upstream] Persona Pack format` (NOT
        `[launchpad]` — `PERSONA_PACK_SPEC.md` is upstream product behaviour in `block/buzz`,
        and the gate's `prefix-repo-mismatch` rule rejects a `[launchpad]` prefix citing
        `block/buzz`), citing `block/buzz` (`crates/buzz-persona/PERSONA_PACK_SPEC.md`, pinned
        to current `block/buzz` main SHA). Add one `[launchpad]` claim citing
        `launchpad-26/buzz` (this repo, this plan's own commit SHA once committed) about this
        cohort's specific pack layout under `launchpad/personas/`, so the page demonstrates
        multi-prefix synthesis, not just one. Write to a scratch path, not the live handbook
        nav yet.
        done when: a markdown file with complete frontmatter (all required #7 fields) and at
        least one behaviour claim carrying an origin prefix and a full-SHA source link exists
        at a known scratch path.

STEP 8  Run the real gate AND the index build against the draft.            [needs 7]
        what: obtain a checkout of `launchpad-26/handbook`'s `scripts/` directory (it is not
        self-contained — `check_provenance.py` imports the local `provenance` package and
        `page_index.py`), export `GITHUB_TOKEN` before running (an unauthenticated run risks
        rate-limit findings indistinguishable from real defects unless read closely — see
        step 9), then run BOTH `python3 check_provenance.py <scratch-docs-dir> --format json`
        AND `python3 page_index.py <scratch-docs-dir> -o /dev/null` against a scratch
        directory containing EXACTLY the one drafted page (confirm the page count, so an
        empty or wrong directory cannot masquerade as a clean run).
        done when: `check_provenance.py`'s JSON shows `findings: []` AND `skipped: []` (a
        `skipped` page was never checked at all — not a pass) — `unchecked` entries remain
        acceptable — AND `page_index.py` exits 0 (confirms all required frontmatter fields
        are present and non-empty, which `check_provenance.py` does not check).

STEP 9  Fix any finding directly in the draft page.                         [needs 8]
        what: if step 8 reports a `check_provenance.py` finding, first read its message —
        one whose text contains "could not be checked" or names a network/rate-limit failure
        means the CHECK failed, not the page; fix the token/network and re-run step 8 exactly,
        do not touch the page. For every other finding, or any `page_index.py` missing-field
        report, fix the page itself — do not hand-edit around the gate, and do not weaken the
        skill's instructions just to dodge one rule.
        done when: re-running step 8's exact commands reports zero findings, zero skipped,
        and a zero exit from `page_index.py`, with no manual exception added to either gate.

STEP 10 Extend the README.md step 2 started — do not overwrite it.          [needs 2, 9]
        what: step 2 already created `launchpad/personas/the-professor/README.md` with the
        `temperature` rationale; ADD to that same file (not a fresh write that could drop
        step 2's paragraph): what The Professor is, what is/isn't in scope per issue #9 (no
        live-channel operation, `.mcp.json` is config-only per step 3's limitation note), and
        a pointer to the step 7-9 proof.
        done when: the README contains BOTH step 2's temperature paragraph AND the new
        sections, and names the exact scratch path of the passing draft page as evidence.

STEP 11 Open the PR against `launchpad-26/buzz` closing #9.                [needs 10]
        what: follow `launchpad/AGENT_PR_TEMPLATE.md`'s provenance table; link the draft
        page's gate-pass output (step 8) as evidence rather than re-asserting it in prose.
        done when: `gh pr view` shows a PR with `Closes #9`, the provenance table filled in,
        and the gate JSON output (or a link to it) attached as evidence.

STEP 12 Record the merge-to-nav decision explicitly.                        [needs 9]
        what: decide whether the step-7 draft page also merges into the live
        `launchpad-26/handbook` nav as real content, or stays proof-only — this is #10's
        territory (already closed) reopening if content changes, so it must be a stated
        decision, not a silent merge under #9's PR.
        done when: a one-line decision is recorded in the PR description (merge to handbook
        nav now / leave as proof-only for now) — either answer is acceptable, silence is not.

PARALLEL  Step 1 has no prior dependency and can start immediately. Steps 2-5 all edit the
          same `agents/the-professor.persona.md` frontmatter file, so despite different
          `needs` tags they are effectively sequential in practice (same-file edits) — note
          this explicitly rather than parallelizing subagents against one file. Step 3
          (`.mcp.json`) and step 4 (`skills/draft-page/SKILL.md`) touch different files and
          could run as parallel subagents once step 1 lands, provided step 5 (which edits the
          persona file again) is deferred until both finish. Steps 7-9 are inherently
          sequential (draft → gate → fix-and-recheck). Step 6 (Serina's own writing) blocks
          step 7 and cannot be parallelized or delegated by design.

GATES     serina:review-code after step 9 (the drafting skill and any wiring code / scripts
          touched). serina:review-plan should run on this plan itself before step 1 starts,
          per its own "use after a plan is written and before the first implementer is
          dispatched" trigger. qa explore mode does not apply in the interactive-UI sense —
          there is no UI here — but the equivalent runtime check IS step 8 (running the real
          gate script against real output) and must not be skipped or simulated. review-a11y
          does not apply (no UI surface). serina:review-final once the PR is ready, before
          merge, per standing practice on this repo.

BUDGET    Step 7 (producing one real compliant draft page) is the step most likely to eat the
          budget — the page contract's claim rule (source-vs-opinion, full-SHA pinning,
          correct origin prefix per claim) is exactly the discipline #7's own sub-issue found
          hardest to get right the first time, and a persona prompt has to induce that
          discipline through instructions alone, with no code-level enforcement until step 8.

OPEN      Where does the actual DRAFTING happen at runtime — a live buzz-acp session against
          the real relay (requiring `BUZZ_RELAY_URL`/`BUZZ_PRIVATE_KEY` and a running Buzz
          instance), or a standalone agent session (e.g. this harness) using the persona
          prompt as system context, with no live Buzz plumbing at all? Issue #9's acceptance
          criteria ("it drafts a page... passes the gate without hand-editing") is satisfiable
          either way; this plan assumes the standalone route for steps 7-9 because issue #9
          explicitly excludes "The Professor running live inside Buzz" as out of scope, but
          the issue does not say which proof mechanism counts. Surfaced, not resolved.
          Whether `launchpad-26/rhizomorph` is public or private was not verified against the
          live repo in this planning pass — the gate's `unchecked` outcome absorbs either
          answer, so it does not block execution, but confirm before writing step 3's MCP
          scope note into anything more permanent than this plan.

LEFT OUT  Zip-file packaging (`.buzzpack` + `.sha256`) and `pack.lock` — issue #9's acceptance
          criteria only requires the pack to validate and draft, not to be distributed; Phase
          1 packaging is real work but not this issue's job. Live-channel operation (`subscribe`,
          `triggers` beyond the explicit empty-override) — excluded per issue #9 itself as PRD
          stage 4. Writing the persona's actual voice/prompt — excluded per issue #9 and handed
          to Serina at step 6. Merging the step-7 proof page into the live handbook nav as
          authoritative content — deferred to the explicit decision point at step 12 rather than
          assumed.

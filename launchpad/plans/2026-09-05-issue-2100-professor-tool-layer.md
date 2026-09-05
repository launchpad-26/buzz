Issue #2100 — feature: Professor tool layer — professor.py replaces the MCP server
Stated size: no `Size` line — this repo's Feature/Task issue templates (`.github/ISSUE_TEMPLATE/02-task.yml`, `07-feature.yml`) don't carry one at all, so there's nothing to read. Sized instead from the two child Tasks' own bodies (#2101, #2102), each naming concrete file-level deliverables that individually exceed a 30–60 minute unit of work → **more than an hour → cap: 12 steps**.

ALREADY TRUE  (verified against git and the actual files, not notes)
  Worktree `/home/serina/Launchpad/buzz/__worktrees/feature-2100-professor-tool-layer`,
  branch `feature/2100-professor-tool-layer`, fresh off `origin/launchpad` at `305e7a4b1`
  (the merge commit for PR #2097). `git status --short` is clean.
  `launchpad/agents/the-professor/tools/server.py` exists: five `@mcp.tool()` functions
  (`read_contract`, `list_categories`, `resolve_pin`, `path_exists_at`, `check_page`),
  MCP stdio transport, hardcoded to `launchpad-26/handbook`.
  `launchpad/agents/the-professor/tools/check_server.py` exists: spawns `server.py` as a
  real subprocess over stdio via the MCP client, cross-checks `resolve_pin` against
  `git ls-remote`, exercises `path_exists_at` true/false, runs `check_page` against two
  real fixtures fetched live from `launchpad-26/handbook`'s `tests/fixtures/`.
  `launchpad/agents/the-professor/.mcp.json` and `.plugin/plugin.json`'s `mcp_config`
  field both still point at `server.py`.
  `launchpad/agents/the-professor/tools/contract/page-contract.md` and
  `sensitive-patterns.md` exist (the suite-default specs `check-page`/`screen-content`
  must implement) — no gate script implements either one yet, by design (the design
  doc's own Phase 9 status note says so).
  No `tests/fixtures/` (or equivalent) directory exists yet anywhere under
  `launchpad/agents/the-professor/` — every fixture `check_professor.py` needs is new.
  `launchpad/agents/the-professor/README.md` already says "Phase 0 resolved, Phases 1–7
  not yet built" and still describes `tools/server.py` as the current tool layer (lines
  16, 24, 208) — accurate today, becomes stale the moment this plan's steps land.

STEP 1  Scaffold `tools/professor.py`'s CLI shell: four subcommands             [independent]
        (`resolve-pin`, `path-exists-at`, `check-page`, `screen-content`) wired
        through `argparse`, each routed through one shared helper that reads
        `$PROFESSOR_PACK_ROOT`, and fails loud with a specific, actionable
        message (not a stack trace) before any subcommand logic runs if it's
        unset. Subcommand bodies may be stubs at this step.
        done when: `PROFESSOR_PACK_ROOT= python3 tools/professor.py check-page x.md`
        (unset) prints a specific message naming `PROFESSOR_PACK_ROOT` and exits
        non-zero, for all four subcommands; with it set to any value, each
        subcommand is reachable without crashing on argument parsing.

STEP 2  Port `resolve-pin`/`path-exists-at` from `server.py`'s `resolve_pin`/       [needs 1]
        `path_exists_at`: same validation (40-hex-char SHA check, the
        `_RATE_LIMIT_OR_AUTH_STATUSES` handling, `path`'s `?`/`&` rejection,
        `commit` shape check), same `gh api` calls, minus `@mcp.tool()` and the
        `mcp` import — `resolve-pin <repo> <ref>` and
        `path-exists-at <repo> <commit> <path>` as positional args, matching
        every documented invocation in `skills/draft-page/SKILL.md` and
        `skills/update-page/SKILL.md` exactly (**corrected 2026-09-06,
        superseding this step's own earlier `--repo`/`--ref`/`--commit`/`--path`
        flag decision** — see the OPEN section's own updated note below for
        why the flag shape was wrong and how it was found). `resolve-pin`'s
        output is a JSON object `{"commit", "commit_author", "commit_at",
        "pr"}` (also corrected 2026-09-06 — the original design doc always
        specified this structured shape for Phase 1, §4/§8; it was missed in
        the first build pass and caught by a whole-branch review, not a
        per-diff one).
        This subcommand pair is always the network-backed, GitHub-API path —
        §4 places both in the `netcmd` (network) half of the tool-call diagram,
        for citing sources genuinely external to whatever repo is being
        documented; step 4 below must NOT reuse this logic for a citation to
        the target repo's own tree (see that step's own note on why).
                                                                    ← RUNS HERE
        done when: from a `/tmp` working directory outside this checkout,
        `PROFESSOR_PACK_ROOT=/tmp python3 <abs-path>/tools/professor.py resolve-pin
        block/buzz main` prints a JSON object whose `commit` field is a 40-char
        SHA matching `git ls-remote https://github.com/block/buzz main`
        independently (verified directly: `git ls-remote https://github.com/
        block/buzz launchpad` returns nothing — `launchpad` is this **fork**'s
        default branch name, not a ref on upstream `block/buzz` — so the worked
        example must resolve a ref that actually exists on the repo it names);
        the same session's `path-exists-at block/buzz <that-sha> Cargo.toml`
        prints `true`, and `path-exists-at block/buzz <that-sha>
        this-path-does-not-exist` prints `false`.

STEP 3  Author the `check-page` fixture set under                              [independent]
        `launchpad/agents/the-professor/tools/contract/fixtures/`: fixtures that
        exercise every rule `page-contract.md`'s "What a gate checking this
        contract should flag" section lists, PLUS both citation kinds §4
        distinguishes (a citation to the target repo's own tree, checked
        locally, vs. a citation to a genuinely external repo, checked over the
        network) — nine fixtures total, written from the contract's own spec
        and §4's local/external split, not from whatever `check-page` ends up
        doing:
          - `compliant-local.md` — cites a real path/commit inside THIS repo's
            own history (e.g. a real line range in `tools/server.py` at a real
            commit reachable in this checkout) — the common case §4 says must
            never touch the network.
          - `compliant-external.md` — cites a real path/commit in a genuinely
            external public repo (e.g. `block/buzz`) — the one fixture that
            proves the network-backed check-path (step 2's logic) actually
            gets exercised by `check-page`, not just by `check_professor.py`
            calling `path-exists-at` directly.
          - `broken-nonexistent-citation.md` — a behaviour claim citing a path
            that does NOT exist at a real commit in THIS repo's own history
            (page-contract.md's rule 1, "a citation whose path does not exist
            in the repo/commit it names" — absent from the original fixture
            list; a `check-page` whose path-existence check is broken, unwired,
            or a silent no-op would otherwise pass every fixture in this set).
          - `broken-missing-citation.md` — a behaviour claim with no citation
            at all (rule 2).
          - `broken-out-of-bounds-range.md` — an `#L<n>-L<m>` citation out of
            bounds for the cited file at the cited commit (rule 3).
          - `broken-no-provenance-marker.md` — a section with no inline
            provenance marker directly above its heading (rule 4a).
          - `broken-mismatched-marker.md` — a marker whose `sources` don't
            match the section's actual citations (rule 4b).
          - `broken-mixed-claim.md` — a sentence that reads as both a
            behaviour claim and an opinion claim (rule 5).
          - `broken-frontmatter.md` — missing or unparseable frontmatter
            (rule 6).
        done when: 9 files exist under `tools/contract/fixtures/`, named as
        above (mirroring `check_server.py`'s own `broken-NN-<rule-name>.md`
        naming precedent), every citation in every fixture pointing at a real,
        independently-verifiable path/commit (local or external, matching
        which fixture it is) — never a fabricated ref.

STEP 4  Implement `check-page <file> --target <root>` against                  [needs 1, 3]
        `page-contract.md`'s full rule list, using step 3's fixtures as the
        acceptance check: missing/unparseable frontmatter short-circuits the
        rest (same `skipped` semantics `server.py`'s `check_page` already uses);
        out-of-bounds line range; missing/mismatched provenance marker;
        mixed-claim sentence. **Citation path/commit existence is NOT a single
        reused code path** — this was the plan's own defect until this
        revision, verified against §4's mermaid diagram and its surrounding
        prose (`check-page`/`screen-content` are in the diagram's `localcmd`
        subgraph, explicitly labelled "no network, runs on every write";
        `resolve-pin`/`path-exists-at` are in `netcmd`, "external citations
        only") and against §1's own claim that reading the target's own tree
        needs "no GitHub API, no network call... for the bulk of the work."
        A citation to `--target <root>`'s own repo is checked with a plain
        local operation (e.g. `git -C <root> cat-file -e <commit>:<path>`, or
        an equivalent filesystem/git-plumbing check against the local
        checkout) — no `gh api` call, ever, for this case. Only a citation
        naming a *different* repo than `--target` reuses step 2's
        `path-exists-at` logic (in-process, not a self-subprocess call) — the
        one case that is genuinely external and was always meant to be
        network-backed. Deliberately does **not** check for a matching
        provenance *ledger* record — `page-contract.md`'s own "Deliberately
        not on this list" section places that with `library-index sweep`, not
        here.
        done when: run against each of step 3's 9 fixtures, `compliant-local.md`
        and `compliant-external.md` both return zero findings — and a network
        capture/mock during the `compliant-local.md` run shows zero outbound
        `gh api`/GitHub calls, proving the local path never touches the
        network — while `compliant-external.md`'s run does make a real
        `path-exists-at`-shaped call; the seven broken fixtures each return a
        finding whose rule name matches what that fixture was built to trip —
        no fixture trips more than the rule it targets, and none silently
        passes.

STEP 5  Author the `screen-content` fixture set under the same                 [independent]
        `tools/contract/fixtures/` directory: one clean fixture with no
        sensitive content, one per `[pattern]` **block** category from
        `sensitive-patterns.md` (API key/token shape, PEM private-key marker,
        password/connection-string shape, webhook URL with an embedded token —
        4 fixtures), one per `[pattern]` **redact** category (email outside an
        attribution context, internal hostname/private IP, physical address —
        3 fixtures), and one exercising the single `[dispatch]` category
        (a roster-shaped list of names used as access-control data) to prove
        step 6 reports it as unevaluated rather than silently dropping it —
        9 fixtures total, all fabricated/placeholder values, never real secrets.
        done when: 9 files exist, named for the category each targets, using
        obviously-fake values (e.g. `sk-FAKE...`, `192.168.0.0/16`-range IPs,
        `example.com` addresses) so nothing here is a real credential.

STEP 6  Implement `screen-content <file>` against every `[pattern]` category    [needs 1, 5]
        in `sensitive-patterns.md` as real regex/entropy/structure matching,
        reporting the correct `block`/`redact` disposition per category. The
        one `[dispatch]` category (roster names) is explicitly **not**
        evaluated here — it needs `$PROFESSOR_VERIFIER_CMD`'s model dispatch,
        which Phase 1b (a separate, not-yet-filed Feature) builds — so any span
        that structurally matches that category is reported as
        "not evaluated, needs dispatch" rather than silently passed as clean.
        done when: run against each of step 5's 9 fixtures, the clean one
        returns no findings; each block fixture returns a `block` finding
        naming its category; each redact fixture returns a `redact` finding
        whose replacement is `[REDACTED: <category>]`; the dispatch fixture
        returns neither a pass nor a block/redact verdict, but an explicit
        "not evaluated" result naming why.

STEP 7  Write `tools/check_professor.py`, a real-subprocess test harness       [needs 2, 4, 6]
        matching `check_server.py`'s own rigor: `resolve-pin`'s output
        cross-checked against `git ls-remote` independently (not a recorded
        value); `path-exists-at` exercised for both the true and false case;
        `check-page` and `screen-content` each run against every fixture from
        steps 3 and 5, asserting the specific expected verdict per fixture (not
        just "some finding exists"); at least one call made from a working
        directory outside this checkout with `$PROFESSOR_PACK_ROOT` set to an
        arbitrary path, proving pack-root resolution actually works away from
        this fork; a separate run with `$PROFESSOR_PACK_ROOT` unset, asserting
        the exact required error text from step 1, for all four subcommands.
        done when: `python3 tools/check_professor.py` exits 0 and prints
        "ALL CHECKS PASSED"; deliberately breaking one check (e.g. commenting
        out a fixture assertion) makes the harness fail with a message naming
        which specific check failed, not a bare non-zero exit.

STEP 8  Delete `tools/server.py`, `tools/check_server.py`, `.mcp.json`;         [needs 7]
        remove `.plugin/plugin.json`'s `mcp_config` field.
        done when: `git status --short` inside
        `launchpad/agents/the-professor/` shows exactly these three files
        deleted and `plugin.json` modified (plus the new files from steps 1–7
        added); `grep -c mcp_config launchpad/agents/the-professor/.plugin/plugin.json`
        returns `0`; `python3 tools/check_professor.py` (step 7) still exits 0
        after the deletion (proving nothing it needs was actually in the
        deleted files).

STEP 9  Update `README.md`'s tool-layer section (the "Phase 0 resolved,           [needs 8]
        Phases 1–7 not yet built" line, and the "tools/server.py, an MCP
        server..." paragraph, and the "All five tools in
        .../tools/server.py are read-only" line) to describe `professor.py`'s
        four subcommands as current and Phase 1 as done — not listed in the
        design doc's own Phase 1 "Files touched," but leaving it stale the
        moment this lands would misdescribe the pack to the next reader; a
        judgement call, flagged here rather than silently added or silently
        skipped.
        done when: `grep -n "server.py\|not yet built" README.md` no longer
        matches any sentence describing the current state as MCP-based; the
        five-tools count is corrected to professor.py's four subcommands.

PARALLEL  Steps 3 and 5 (fixture authoring) touch only new files under
          `tools/contract/fixtures/` and depend only on the two contract spec
          docs, not on any professor.py code — they can run as subagents in
          parallel with each other and with step 2 (which only touches
          `tools/professor.py`'s resolve-pin/path-exists-at bodies). Steps 4
          and 6 cannot start until their own fixtures (3, 5 respectively) and
          the CLI skeleton (1) exist. Steps 7, 8, 9 are strictly sequential —
          each reads the output of the one before it (the harness must exist
          before the files it tests are deleted; the deletion must happen
          before the README can truthfully say it happened).
GATES     `review-code` and `review-tests` both apply after step 7 (real
          implementation + real test harness exist by then) — run them before
          step 8's deletion, not after, so a defect found there doesn't force
          re-adding files just deleted. `qa` explore mode applies: `professor.py`
          is a CLI with a real runtime interface (four subcommands, real
          argument parsing, real subprocess/network behavior for two of them)
          — worth a hostile-input pass (malformed `--commit`, a `--path`
          containing `../`, a `check-page` target that isn't valid UTF-8)
          before this Feature's batch PR opens, not just the fixture set above.
          `review-a11y` does not apply — no UI surface.
BUDGET    Step 4 (`check-page`'s full rule implementation) is the step most
          likely to eat the budget — six distinct rule checks against real
          citation/commit/line-range data, not a single mechanical port like
          step 2.
OPEN      Whether `check-page`'s citation-existence check should cache
          `path-exists-at` results within one run (a single draft can cite the
          same file/commit repeatedly) — the design doc doesn't specify this,
          and step 4 doesn't need it to pass step 3's fixtures, so it's left as
          an implementation detail for whoever builds step 4, not decided here.
          **RESOLVED 2026-09-06, superseding the 2026-09-05 entry below.**
          `check-page` takes `--target <root>`; `resolve-pin`/`path-exists-at`
          take **positional** `<repo> <ref>` / `<repo> <commit> <path>` — this
          plan's original `--repo`/`--ref`/`--commit`/`--path` flag choice was
          wrong, found by a whole-branch `review-final` pass (not a per-diff
          reviewer, which had no reason to compare the tool's CLI against the
          `SKILL.md` files that actually call it) against
          `skills/draft-page/SKILL.md`/`skills/update-page/SKILL.md`, which
          both document positional args and were never wrong — the flag
          choice below was the plan's own error, invented from §4's prose
          without checking the two files that actually invoke this interface.
          `resolve-pin`'s output is also corrected: a JSON object
          `{"commit", "commit_author", "commit_at", "pr"}`, per the design
          doc's own explicit (and previously missed) "output schema changes"
          requirement — not the bare SHA this plan originally assumed.

          *(2026-09-05 entry, superseded above, kept for history):* Exact CLI
          flag names/shapes beyond what §4 states explicitly were not
          specified in the design doc; this plan used
          `--repo`/`--ref`/`--commit`/`--path` as a reading of §4's prose, and
          issues #2100/#2101 were edited the same day to match that flag
          shape. Both the plan's choice and that edit were wrong — corrected
          2026-09-06 back to positional args, and issues #2100/#2101 have been
          re-edited again to match. A builder reading either issue directly
          now sees the same positional shape this plan and the shipped code
          both implement.
LEFT OUT  Everything Task #2100's own "Out of scope" section already names:
          `verify-claims`' `$PROFESSOR_VERIFIER_CMD` dispatch (Phase 1b, separate
          Feature); reconciling the six known-stale `SKILL.md` drafts against
          decisions made after they were written (lands with Phases 1b/2/5,
          whichever actually needs each skill); `#1402`'s own branch/PR,
          procedurally untouched by this plan.

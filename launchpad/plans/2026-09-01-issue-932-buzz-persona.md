Issue #932 — corpus node: implementation/crates/buzz-persona.md
Stated size: none given in the issue body → cap: 5 steps

ALREADY TRUE  (verified against git at 76a0a4ebbe4bc4d852b0d04362ed768620da34b3)
  launchpad/docs/corpus/schema/node.schema.json, launchpad/docs/corpus/AGENTS.md and
    launchpad/docs/corpus/templates/implementation-reference.md are all merged on
    origin/launchpad.
  The target file launchpad/docs/corpus/implementation/crates/buzz-persona.md does not
    exist (checked with `ls`), and no `implementation/` subtree exists in the corpus at
    all yet — this is the first `implementation`-typed node, so it can declare no
    sibling `implementation` node as a relationship target.
  launchpad/docs/corpus/architecture/containers/agent-runtime.md (id
    `architecture-containers-agent-runtime`) is merged and already carries several FACT
    claims specifically about buzz-persona: it is a direct path dependency of buzz-acp's
    Cargo.toml, it is resolved "harness-side, before the agent subprocess is prompted",
    and its spec file is linked from that node's own "Where each rule lives" table. This
    is the one real `part-of` candidate for the new node, pending re-verification of each
    claim at current HEAD before the edge is declared.
  crates/buzz-persona is a 6-module crate (lib.rs, manifest.rs, merge.rs, pack.rs,
    persona.rs, resolve.rs, validate.rs) plus PERSONA_PACK_SPEC.md and two test files
    (tests/integration.rs, tests/e2e_env_flow.rs). Its Cargo.toml description is "Parser
    and loader for Buzz persona pack files (.persona.md)".
  Three crates declare a Cargo.toml dependency on buzz-persona: buzz-acp, buzz-cli, and
    desktop/src-tauri (aliased `buzz_persona_pkg`). A source grep shows buzz-cli
    (crates/buzz-cli/src/commands/pack.rs) and desktop (src/migration.rs) both actually
    call into it (validate_pack, resolve_pack, split_frontmatter); a grep of
    crates/buzz-acp/src for `buzz_persona` returns zero matches (exit 1) despite the
    Cargo.toml dependency — a real, verified divergence between "depends on" and "calls",
    to be re-confirmed and recorded, not silently smoothed over.
  No dedicated CI workflow names buzz-persona; it is a cargo workspace member covered
    generically by `just test-unit` (cargo-nextest) in .github/workflows/ci.yml's "Unit
    Tests" job — the only verification mechanism found for this crate.

STEP 1  [independent]  Re-verify the crate's responsibility, public API, ownership
        boundary and consumers against current HEAD.
        Read crates/buzz-persona/src/lib.rs (module list) and the doc comment plus every
        `pub` item in manifest.rs, persona.rs, pack.rs, merge.rs, resolve.rs, validate.rs
        (already enumerated once above; re-open each at current HEAD, do not reuse the
        earlier read as evidence). Read PERSONA_PACK_SPEC.md §1–2 for the pack format
        this crate parses. Read tests/integration.rs and tests/e2e_env_flow.rs test names
        to identify representative tests, including
        operator_config_fields_rejected_in_frontmatter (persona.rs's
        `#[serde(deny_unknown_fields)]` Frontmatter struct at persona.rs:174-198), which
        is direct evidence of what the crate deliberately does NOT own (operator-level
        config like idle_timeout, permission_mode). Re-grep buzz-acp/buzz-cli/desktop for
        buzz_persona usage to confirm the STEP-0 divergence still holds. Record
        `git rev-parse HEAD` for the provenance ledger entry.
        done when: every `pub fn`/`pub struct`/`pub enum` cited in the node's
        Implementation-surface table has been opened at current HEAD in this step, not
        carried over from an earlier read; the buzz-acp no-call-site finding is
        re-confirmed with a fresh `grep -rn buzz_persona crates/buzz-acp/src/` exiting 1;
        and the recorded HEAD sha matches `git rev-parse HEAD` run in this step.

STEP 2  [needs 1]  Write the corpus node's front matter and body against the
        implementation-reference template.
        id: `implementation-crates-buzz-persona` (mirrors the file's own path, per the
        precedent set by `corpus-agents`/`corpus-readme` naming). type: `implementation`
        — the template's default, and buzz-persona is ordinary Rust library code with no
        protocol/contract surface that would justify `interfaces-events` instead. status:
        `draft`. origin: `launchpad`. audiences: [agent, developer, reviewer]. One
        evidence entry per substantive claim, classified FACT (opened source) or
        INFERENCE (reasoned, with confidence) — no TEAM_KNOWLEDGE expected, since every
        claim traces to code opened directly. relationships: `part-of:
        architecture-containers-agent-runtime` only if STEP 1's re-verification confirms
        that node's buzz-persona claims still hold at current HEAD; otherwise declare no
        relationships and say why in Scope and omissions. Body sections exactly per the
        template skeleton: Realization statement / Target / Implementation surface
        (table: module/symbol → what it does, evidenced per-row) / Divergences
        (buzz-acp's declared-but-uncalled dependency, stated as a fact found, not
        adjudicated) / Verification (the `just test-unit` / ci.yml Unit Tests job, named
        as the only mechanism found) / Relationships / Scope and omissions (what the
        crate owns — pack/persona parsing, merge precedence, validation, ACP-shaped
        resolution — vs. what it explicitly does not — hooks execution, MCP server
        spawning, operator-level runtime config, all of which the module doc comments and
        the deny_unknown_fields test attribute to buzz-acp instead).
        done when: the file exists at
        launchpad/docs/corpus/implementation/crates/buzz-persona.md; every DoD bullet
        from issue #932 (responsibility + what it does not own, public interfaces/entry
        points + dependencies, owned source paths + representative tests) is satisfied by
        a named section; and every FACT evidence entry cites a source opened in STEP 1 or
        this step, not asserted from memory.

STEP 3  Run corpus validation and fix until it exits 0 for this node.        [needs 2]
        Run `python3 launchpad/project-intelligence/corpus/validate.py`. If it exits
        non-zero, confirm via `git stash` (stashing only this node's uncommitted addition)
        and re-running whether the same FAIL count and node ids appear on unmodified
        origin/launchpad — the task brief records a pre-existing ~21-failure baseline
        there — before assuming any FAIL is this node's own. Un-stash and fix only
        FAILs that name this node's id or file path.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0,
        or exits non-zero with every FAIL naming a node id/path other than
        `implementation-crates-buzz-persona` / this node's file, confirmed also present in
        the stashed (baseline) run.

STEP 4  [needs 3]  Earn the commit gate and self-review the diff against the issue's DoD.
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own tool call; confirm `OK`. In a
        separate tool call, `git add` the node and this plan file and
        `git commit -s -m "docs(corpus): add buzz-persona implementation reference
        (#932)"`. Do not push; do not open a PR — this batch integrates via a single
        later Feature-level PR. After the commit exists, re-read the diff line by line
        against every issue #932 DoD checklist bullet and confirm each citation actually
        supports its claim (open the file, don't trust the path resolving). Use the
        `corpus-review` skill if reachable in-session for a docs-only corpus node;
        otherwise perform and report this as a careful self-review. ← RUNS HERE
        done when: the unittest run reports `OK`; `git log -1` shows the new commit with
        both files staged; and the DoD line-by-line check is written into the final
        report, naming which review path (corpus-review or self-review) was actually
        used.

PARALLEL  None. STEP 1 touches no repository file and is the only step with no upstream
          dependency; STEPs 2–4 are strictly sequential (each edits or gates the single
          target file/commit). No other in-flight batch document depends on or is
          depended on by this one — the issue's DoD explicitly forbids materially editing
          a second hand-authored corpus document in the same task.

GATES     python3 launchpad/project-intelligence/corpus/validate.py must exit 0 for this
          node (STEP 3). python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py" must report OK before
          commit (STEP 4). corpus-review (or a documented self-review if the skill is
          unreachable) runs after the commit exists, before the task is reported done.
          review-adjudicate and cross-model review-final are explicitly deferred to the
          batch's later integration-PR phase, per the task brief — not run in this
          session.

BUDGET    STEP 1's re-verification is the step most likely to be quietly skipped in favor
          of reusing the earlier exploratory read — it is the one with no automated check
          behind it (validate.py is structural, not evidential, per AGENTS.md), so it is
          named explicitly with its own done-when rather than folded into STEP 2.

OPEN      Whether buzz-acp's declared-but-apparently-uncalled buzz-persona path
          dependency is genuine drift, a build-time-only usage a static source grep
          cannot see, or a dependency scheduled for removal is not resolved by this
          node — it is recorded as a Divergence with the evidence found in STEP 1, not
          adjudicated. A builder must not silently omit it because it looks like noise;
          nor may a builder decide it is a bug and "fix" buzz-acp — that is implementation
          work, explicitly out of scope per the issue's own "Out of scope: Changing
          runtime product behavior" bullet.

LEFT OUT  No relationship type other than `part-of` toward the agent-runtime container —
          no verification/test-strategy or interfaces-events corpus node exists yet for
          buzz-persona to `references`. No second corpus document, even though buzz-cli's
          `pack` subcommand and desktop's migration shim are both real, verified consumers
          that could eventually earn their own implementation-reference nodes — filing
          those is left for a future task, per the issue's "Out of scope: Creating or
          materially editing a second hand-authored canonical corpus document." No attempt
          to fix or file an issue for the buzz-acp dependency divergence itself — recording
          it in the node's Divergences section is the full extent of this task's DoD.

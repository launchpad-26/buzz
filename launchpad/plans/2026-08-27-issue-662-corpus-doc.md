Issue #662 — task: document architecture/context/ai-agent.md
Stated size: no `Size` line -> cap: 5 steps (single-document corpus task, per #608 batch convention)

ALREADY TRUE  (verified against git, not notes)
  On branch `task/662-corpus-doc`, based on `origin/launchpad` at
    `a44cf52fc740ebebbdd671427480d14f0bce0115` (`git log -1 --oneline` confirmed).
  `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are
    merged on `origin/launchpad`. `type: architecture` is in the schema's closed enum (no
    finer container/context/deployment/flow/principle sub-enum exists).
  `launchpad/docs/corpus/architecture/context/ai-agent.md` does not exist anywhere in the
    worktree (`test -f` confirmed absent).
  The only hand-authored nodes merged on `origin/launchpad` today are `AGENTS.md`,
    `README.md`, `standards/confidence.md`, `standards/decision-references.md` — no
    `architecture/*` node exists yet, so no `relationships` target in that namespace can
    resolve.
  `ARCHITECTURE.md` (repo root) documents the relay, its crates, and `buzz-acp` as "Agent
    Communication Protocol Harness"; `crates/buzz-acp/README.md`, `crates/buzz-agent/README.md`,
    `crates/buzz-persona/PERSONA_PACK_SPEC.md`, `crates/sprig/Cargo.toml`, and
    `crates/buzz-core/src/kind.rs` (KIND_AGENT_PROFILE, KIND_MANAGED_AGENT, KIND_JOB_REQUEST
    family) together describe the AI-agent actor's boundary and its relationships to Buzz.

STEP 1  [independent]  Gather evidence: read `ARCHITECTURE.md` §buzz-acp, `crates/buzz-acp/README.md`,
        `crates/buzz-agent/README.md`, `crates/buzz-persona/PERSONA_PACK_SPEC.md`,
        `crates/buzz-dev-mcp/Cargo.toml`, `crates/sprig/Cargo.toml`,
        `crates/buzz-core/src/kind.rs` (agent-related kind constants), and
        `desktop/src-tauri/src/managed_agents/mod.rs` (module list only, not internals).
        Record the actor/system boundary: AI Agent (external ACP-speaking process, e.g.
        goose/codex/claude/buzz-agent), LLM Provider (external HTTP API), buzz-acp (harness,
        part of Buzz), Buzz CLI (part of Buzz, the agent's write path), buzz-dev-mcp (tool
        server, part of Buzz), Buzz Desktop's managed_agents module (part of Buzz, spawns/
        supervises local agent runtimes), and the Buzz Relay itself. This is evidence-gathering;
        no corpus file changes in this step.
        done when: every claim used in STEP 2's body has a source path opened in this step,
        and any DoD-relevant fact not found in the repo is named as a gap for the body's
        scope-and-omissions section rather than guessed.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/architecture/context/ai-agent.md`:
        schema-valid front matter (`id: architecture-context-ai-agent`, `type: architecture`,
        `status: draft`, `origin: launchpad`, `audiences`, an `evidence` ledger with a commit
        citation for `a44cf52fc740ebebbdd671427480d14f0bce0115` first, one entry per substantive
        claim, no `relationships` — see OPEN), and a body satisfying the issue's DoD plus the
        category tail: the system/actor boundary, every directly relevant actor/system and its
        relationship to Buzz, a Mermaid diagram-as-code view, and no container/component
        internals (no per-module breakdown of buzz-acp's relay.rs/queue.rs/pool.rs, no
        managed_agents submodule internals).
        done when: the file exists with schema-required keys present and every `##` section
        named in this step exists.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
        root and fix anything it reports until it exits 0.
        done when: the command's own exit code is 0, confirmed by reading `$?` after the run,
        not inferred from absence of error text.

STEP 4  [needs 3]  Self-audit the finished node line by line against the issue's DoD checklist
        and the category tail (boundary defined, every actor/system named with its relationship
        to Buzz, diagram present, no container/component descent), confirm every evidence entry
        supports the claim it sits under, confirm no second hand-authored corpus document was
        created, and re-run validate.py once more after any fix.
        done when: the audit note maps each DoD bullet to where the body satisfies it, and
        `validate.py` exits 0 on the final version.

STEP 5  [needs 4]  Earn the verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole prior command, confirm `OK`, then in a separate call stage and commit the
        plan file and the new document with `-s`, then push and open a draft PR.
        done when: the unittest run reports `OK`; the commit succeeds without a "no
        verification stamp" block; `git push -u origin task/662-corpus-doc` succeeds; and
        `gh pr create --draft` returns a PR URL.

PARALLEL  None. This is one target file (`launchpad/docs/corpus/architecture/context/ai-agent.md`)
          plus the plan file that documents it — strictly sequential, single worktree, single
          agent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 3, re-run in STEP 4)
          is the only automated gate run in this session. `review-code`, `review-adjudicate`,
          and a cross-model final pass are explicitly deferred to the batch owner's morning
          review per the task brief — none of them run here, and the PR body says so plainly
          rather than implying one ran.

BUDGET    STEP 2. The hard part is drawing the actor/system boundary correctly — which
          Buzz-owned pieces (buzz-acp, buzz-dev-mcp, managed_agents) count as "Buzz" versus
          which pieces (the AI agent process itself, the LLM provider) sit outside it — without
          drifting into the container-level detail the DoD tail explicitly excludes.

OPEN      Whether a `relationships` edge to `corpus-agents` (id of the merged `AGENTS.md`
          governance node) belongs here. `corpus-agents` documents corpus-authoring process,
          not Buzz's runtime AI-agent architecture — the two sibling standards already merged
          (`confidence.md`, `decision-references.md`) both had that same id available and both
          chose to omit any relationship, reasoning that the edge set is better added in one
          pass once thematically-related siblings (other `architecture/*` nodes) land. This
          plan follows that same precedent and omits `relationships` entirely; a reviewer who
          disagrees can add the edge cheaply since it does not change the body.
          Whether "AI Agent" here should also enumerate Buzz Desktop's specific mesh/shared-
          compute agent variant in the same depth as the standalone `buzz-acp` deployment
          path. The issue's DoD asks for "every directly relevant actor/system," and both are
          directly relevant (`buzz-agent/README.md`'s Reply Guard section documents mesh
          agents explicitly), so the plan includes both but at the same context-level altitude,
          not descending into `managed_agents`' internal modules. Left for STEP 4's audit to
          confirm the altitude is even across both.

LEFT OUT  Any per-module description of `buzz-acp` internals (`relay.rs`, `queue.rs`, `pool.rs`,
          `acp.rs`, `filter.rs`) or of `desktop/src-tauri/src/managed_agents/`'s individual
          files — container/component detail the category tail excludes from this node.
          A second corpus node for "AI agent" at container level (e.g. an
          `architecture/containers/agent-runtime.md`-shaped document) — out of scope for #662,
          which is exactly one canonical document.
          Deep verification of the NIP-AE/NIP-PMA/NIP-OA protocol documents referenced from
          `kind.rs` doc comments — the kind constants and their doc comments were opened and
          cited directly; the linked NIP spec files themselves were not opened, and any claim
          resting only on the doc comment is scoped accordingly.
          Editing `ARCHITECTURE.md`, any crate README, or any other file outside the one target
          document and this plan.

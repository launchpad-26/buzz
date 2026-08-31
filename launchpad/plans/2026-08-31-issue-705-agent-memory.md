Issue #705 — task: document capabilities/agents/agent-memory.md
Stated size: no `Size` line -> cap: 5 steps (single-document corpus task, per #608 batch convention)

ALREADY TRUE  (verified against git, not notes)
  On branch `task/705-agent-memory`, based on `origin/launchpad` at
    `131b02f989684117d9ab1dd426f1673fa638e523` (`git rev-parse HEAD` confirmed).
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
    `launchpad/docs/corpus/templates/capability.md` are merged on `origin/launchpad`.
    `type: capabilities` is the schema's dedicated enum member for this surface.
  `launchpad/docs/corpus/capabilities/agents/agent-memory.md` does not exist anywhere in the
    worktree (`test -f` confirmed absent), and no `capabilities/` directory exists at all yet
    under the corpus root (`find` confirmed) -- this is the first capability-shaped node.
  No other hand-authored node under `origin/launchpad`'s corpus tree targets or is targeted by
    an id this node would declare, so no `relationships` can resolve yet (checked
    `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`).
  NIP-AE (`docs/nips/NIP-AE.md`) defines agent engrams: kind:30174 addressable, NIP-44-encrypted
    memory records keyed by `(pubkey_a, pubkey_o, slug)`, with `core` (identity/rules/goals) and
    `mem/...` (arbitrary entries) record types, head selection by greatest `created_at`, and
    tombstones for deletion.
  `crates/buzz-core/src/engram.rs` implements the NIP-AE envelope (build/validate/decrypt,
    head selection, monotonic `created_at`). `crates/buzz-cli/src/commands/mem.rs` exposes
    `buzz mem {ls,get,hash,set,patch,rm}` as the agent-facing write/read surface.
    `crates/buzz-acp/src/engram_fetch.rs` auto-injects the agent's `core` engram into every new
    ACP session's prompt (or an onboarding nudge if absent). `crates/buzz-relay/src/handlers/
    {ingest.rs,req.rs}` enforce engram-specific envelope validation and read-authorization
    (only the agent or its declared owner may enumerate a given pair's engrams).
    `desktop/src/features/agent-memory/` is a read-only owner-facing viewer.

STEP 1  [independent]  Gather evidence: read `docs/nips/NIP-AE.md` in full;
        `crates/buzz-core/src/engram.rs` (CORE_SLUG, NIP44_PLAINTEXT_MAX, build_event,
        validate_and_decrypt, select_head, monotonic_created_at); `crates/buzz-cli/src/
        commands/mem.rs` (all five subcommands + dispatch) and `crates/buzz-cli/README.md`'s
        `mem` rows; `crates/buzz-acp/src/engram_fetch.rs` (session-start core injection);
        `crates/buzz-relay/src/handlers/req.rs` (`engram_filters_authorized`) and
        `crates/buzz-relay/src/handlers/ingest.rs` (`validate_engram_envelope`, scope/channel-
        scoping treatment of `KIND_AGENT_ENGRAM`); `crates/buzz-core/src/kind.rs`'s
        `KIND_AGENT_ENGRAM` constant and doc comment; `desktop/src/features/agent-memory/ui/
        MemorySection.tsx`'s header comment; and `VISION_REMOTE_AGENTS.md`'s "durable memory is
        engrams on the relay" line. Record the maturity evidence (shipped, cited to code) and
        any gap (no direct evidence was sought for `desktop/src-tauri/src/commands/engrams.rs`
        beyond its `KIND_AGENT_ENGRAM` reference, or for `buzz-persona`'s use of memory, if any
        -- name explicitly if unread). This is evidence-gathering; no corpus file changes here.
        done when: every claim used in STEP 2's body has a source path (and line number where
        precise) opened in this step, and anything expected but not verified is named for the
        body's scope-and-omissions section rather than guessed.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/capabilities/agents/agent-memory.md`
        following `launchpad/docs/corpus/templates/capability.md`'s skeleton: front matter
        (`id: capabilities-agents-agent-memory`, `type: capabilities`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, an `evidence` ledger
        with a commit citation for `131b02f989684117d9ab1dd426f1673fa638e523` first, one entry
        per substantive claim, no `relationships`), then the body: Capability statement (what
        an agent and its owner get: durable, encrypted, cross-session memory that survives a
        restarted process, auto-loaded at session start), Maturity (shipped, cited to the code
        paths above), Boundary (not the NIP-AE wire spec itself -- that's `docs/nips/NIP-AE.md`;
        not architecture/component internals; not the interface contract of `buzz mem` itself
        as a CLI surface in isolation -- covered by a future interface node if drafted; not the
        step-by-step flow of one write), Relationships (none, per ALREADY TRUE), Scope and
        omissions per the template's two-part requirement, satisfying every DoD bullet from
        issue #705 (single canonical node, schema-valid front matter, one idea, FACT/INFERENCE/
        TEAM_KNOWLEDGE not conflated, links implementation/verification without duplicating,
        checked against the recorded revision, capability statement + actors/outcomes,
        behavioral rules/constraints/variants, links flows/interfaces/data/platform, links
        verification).
        done when: the file exists with every schema-required key present and every `##`
        section the template and issue DoD name.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        repo root and fix anything it reports until it exits 0. Confirm the only FAIL entries
        remaining are the 21 pre-existing ones tracked by issue #1951 (unrelated to this node).
        done when: the command's own exit code is 0 (or its only FAILs match the #1951
        baseline), confirmed by reading `$?`, not inferred from absence of error text.

STEP 4  [needs 3]  Self-audit the finished node line by line against issue #705's DoD checklist
        and the capability template's required sections; re-open every cited source to confirm
        it actually supports the claim it sits under; confirm no second hand-authored corpus
        document was created; re-run `validate.py` once more after any fix.
        done when: the audit maps each DoD bullet to where the body satisfies it, and
        `validate.py`'s FAIL count has not grown versus the #1951 baseline.

STEP 5  [needs 4]  Earn the commit gate by running, as the sole prior command,
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
        "test_*.py"`, confirm `OK`, then in a separate call stage the plan file and the new
        document and commit with `-s`. Per this task's process note: local commit only, no
        push, no PR -- a later integration phase folds this into Feature #613's PR.
        done when: the unittest run reports `OK`; the commit succeeds without a "no
        verification stamp" block; no push or PR is attempted.

PARALLEL  None. One target file (`launchpad/docs/corpus/capabilities/agents/agent-memory.md`)
          plus this plan file -- strictly sequential, single worktree, single agent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 3, re-run in STEP 4)
          and `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
          "test_*.py"` (STEP 5) are the only automated gates run in this session. Cross-model
          review and CI are deferred to the Feature #613 integration PR, not run here.

BUDGET    STEP 2. The hard part is stating the capability at product-stakeholder altitude (per
          the template's BIZBOK-derived "what, not how" habit) while still citing the concrete
          NIP-AE/engram.rs/mem.rs/engram_fetch.rs evidence precisely enough that every claim is
          a real FACT, not a paraphrase of the spec.

OPEN      Whether a future interface node (for `buzz mem`'s CLI surface specifically) or a flow
          node (for one write/read cycle) gets drafted is out of scope here -- this node's
          Boundary section names both as gaps rather than folding them in, per the template.

LEFT OUT  Any relationships to sibling capability/architecture nodes, since none are merged on
          `origin/launchpad` yet (see ALREADY TRUE). Push and PR creation, per the task's
          explicit process note -- a later integration phase handles that.

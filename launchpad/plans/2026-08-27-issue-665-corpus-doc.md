Issue #665 — task: document architecture/context/human-user.md
Parent: #608 (corpus batch). One of 47 overnight corpus-node tasks, 5 in flight at a time.

ALREADY TRUE  (verified against git, not notes)
  Worktree is on branch `task/665-corpus-doc`, based on `origin/launchpad`,
    HEAD `a44cf52fc740ebebbdd671427480d14f0bce0115`, working tree clean.
    `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are
    merged; `type: architecture` is a real enum member. The only merged authored nodes are
    `AGENTS.md`, `README.md`, `standards/confidence.md`, `standards/decision-references.md` —
    none owns "human user" or the architecture-context surface, and none is a validated
    `relationships` target for this node. `launchpad/docs/corpus/architecture/context/human-user.md`
    does not exist yet, and neither does `architecture/context/` as a directory.

STEP 1  [independent]  Gather evidence for the human-user actor/boundary: the `users` table
        schema and `agent_owner_pubkey`/`agent_type` columns (`migrations/0001_initial_schema.sql`,
        `crates/buzz-db/src/user.rs`), the NIP-OA owner-attestation mechanism that names the
        human as `auth`-tag signer for an agent (`crates/buzz-sdk/src/nip_oa.rs`,
        `crates/buzz-test-client/tests/e2e_human_edit_agent_content.rs`), the shared-identity
        model and NIP-42/NIP-98 split stated in `VISION.md`, and the client/relay boundary
        diagrams in `README.md` and `ARCHITECTURE.md`. Record anything expected but not
        verifiable (e.g. `agent_type` is defined in schema and read once in
        `crates/buzz-db/src/channel.rs` but nothing in the current crates writes it).
        done when: every claim planned for the body has a citation opened and read, not just
        located.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/architecture/context/human-user.md`:
        schema-valid front matter (`type: architecture`, `status: draft`, `origin: launchpad`,
        `audiences`, an `evidence` ledger with a commit-provenance FACT plus one entry per
        substantive claim, no `relationships` — nothing merged is a legitimate target), and a
        body that defines the human-user/Buzz boundary, names every directly relevant
        actor/system (human, agent, relay, community/tenant boundary) and its relationship to
        Buzz, includes a Mermaid context diagram, and stays at context level (no
        container/component internals). Scope section names the gap above and defers the
        NIP-42/NIP-98-by-role split to VISION.md's stated intent rather than asserting it as
        enforced implementation, since that line was not independently verified in code.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and every
        `##` section the DoD/category-tail requires is present.

STEP 3  [needs 2]  Validate and earn the commit stamp: run `validate.py`, then run the corpus
        unittest suite as the sole prior command, then commit.
        done when: `validate.py` exits 0; `python3 -m unittest discover -s
        launchpad/project-intelligence/corpus/tests -p "test_*.py"` reports OK; the commit is
        created with `git commit -s`.

STEP 4  [needs 3]  Self-review the diff line-by-line against #665's DoD checklist and the
        category tail, push, and open a draft PR.
        done when: the PR is open in draft state against `launchpad`, its body contains
        "Closes #665", confirms both checks passed, states self-review was performed with no
        automated review-code pass, and carries the required deferral line verbatim.

PARALLEL  None. One file (plus the plan file). Nothing here is dispatchable as a subagent.

GATES     `validate.py` (STEP 3) and the corpus unittest suite (STEP 3) are the only gates run
          in this session. `review-adjudicate` and the cross-model final pass are explicitly
          deferred to the batch owner's morning review — not run here, and the PR body says so.

BUDGET    STEP 2. The hard part is describing the human/agent boundary honestly at context
          level — real from the `users` schema and NIP-OA, without overclaiming the
          NIP-42-vs-NIP-98 role split as enforced when only VISION.md was verified stating it
          as intent.

OPEN      #665's own DoD does not say whether "human user" means the person operating a Buzz
          client directly, or also covers the human as *owner* of an agent (the NIP-OA
          relationship). Left genuinely open in the body rather than resolved silently: this
          node covers both, since the schema and NIP-OA evidence make the owner relationship
          the only mechanically enforced human-vs-agent distinction that exists today.

LEFT OUT  Any `relationships` edge — no merged node is a legitimate target yet.
          Container/component-level detail on auth pipelines, desktop/mobile client internals,
          or the relay's request handling — owned by lower corpus layers per the category tail.
          Fixing or extending `agent_type` (unwritten in current code) — that is an
          implementation gap, not something this node's scope authorizes changing.

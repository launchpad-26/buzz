Issue #1047 — task: document layers/compute/provider-model.md
Stated size: no `Size` line on the issue -> single-document corpus task -> cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1047-provider-model`, based on `origin/launchpad` at `338b4d0cf`
    ("Merge pull request #1779 from launchpad-26/task/605-corpus-batch-b"), working
    tree clean.
  `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
    are merged and authoritative.
  `launchpad/docs/corpus/templates/concept.md` exists and is the correct template
    (issue #1047's Objective names this "the single canonical concept node for
    provider model").
  `launchpad/docs/corpus/layers/compute/provider-model.md` does NOT exist.
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` shows no
    `layers/compute/*` path at all today -- the five sibling compute documents
    (#1041 backend-provider, #1042 kubernetes-provider, #1045 local-agent-compute,
    #1046 mesh-compute, #1048 remote-agent-compute) are open draft PRs from the same
    batch, not merged. `relationships` therefore has no legal target and is omitted.
  Repo evidence for "provider model" resolves to one real, general abstraction:
    `docs/remote-agents.md`'s "Provider Protocol" (discovery, `info`/`deploy`
    operations, invariants I1-I5) is the formal spec, and
    `desktop/src-tauri/src/managed_agents/backend.rs` (`discover_provider_candidates`,
    `resolve_provider_binary`, `invoke_provider`, `provider_deploy`,
    `validate_provider_info`, `validate_provider_config`,
    `PROVIDER_PROTOCOL_VERSION = 1`) is its desktop-side implementation. The
    `BackendKind` enum (`desktop/src-tauri/src/managed_agents/types.rs:6-13`,
    `Local` vs `Provider { id, config }`) is the record-level discriminator that
    selects it. `crates/buzz-backend-kubernetes/src/main.rs` and `wire.rs` confirm a
    second, independent binary conforms to the identical stdin/stdout `info`/`deploy`
    contract, which is the evidence that the contract is genuinely substrate-agnostic
    and not merely a K8s-specific interface documented as if general.

STEP 1  [independent]  Gather evidence: read `docs/remote-agents.md` in full
        (Abstract, Scope and Non-Goals, System Model, Launchers, Invariants I1-I5,
        Provider Protocol: Discovery/Invocation/Provider Output/info/deploy/Launch
        data/Deploy State Machine down through Stop and Delete),
        `desktop/src-tauri/src/managed_agents/backend.rs` in full,
        `desktop/src-tauri/src/managed_agents/types.rs` (`BackendKind`),
        `desktop/src-tauri/src/commands/agent_providers.rs` (`discover_backend_providers`,
        `probe_backend_provider`), `desktop/src-tauri/src/commands/agents/provider_deploy.rs`,
        and `crates/buzz-backend-kubernetes/src/{main,wire}.rs` to confirm the
        conforming-second-implementation claim. Already done in this session (this
        plan is written after gathering, not before) -- STEP 1 is recorded as
        complete at plan-write time.
        done when: every claim in the drafted document cites one of the paths above
        (or another path actually opened this session) and no claim rests on
        inference presented as fact.

STEP 2  [needs 1]  ← RUNS HERE  Write
        `launchpad/docs/corpus/layers/compute/provider-model.md` from
        `templates/concept.md`'s required sections (Definition, Use cases,
        Boundary/non-goals, Related resources, Scope and omissions): front matter
        (`id: layers-compute-provider-model`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [agent, developer, reviewer]`, no
        `relationships`) plus a body that defines the provider model as the
        abstract discovery + `info`/`deploy` contract (what is fixed: the wire
        shape, the two operations, the protocol-version gate, the `Local`/
        `Provider{id,config}` discriminator, the invariants that bind every
        conforming binary; what varies: the substrate a given `buzz-backend-<id>`
        binary deploys into, its `config_schema`, its binding-specific policy).
        Explicit non-goals section names the Kubernetes binding's reconciliation
        details, the local-spawn path, mesh compute, and lifecycle/liveness
        specifics as owned by the (unmerged) sibling documents, not duplicated
        here. Classify every claim FACT (cites the spec text or the exact
        function/const/struct read in STEP 1), INFERENCE (with `confidence`), or
        TEAM_KNOWLEDGE (with `provided_by`) -- do not conflate.
        done when: the file exists, front matter parses, every required
        `concept.md` section is present, and every substantive claim in the body
        has a corresponding `evidence` entry.

STEP 3  [needs 2]  Validate: `python3 launchpad/project-intelligence/corpus/validate.py`
        must exit 0 against the full tree including the new file. Fix and re-run on
        any failure.
        done when: the command exits 0.

STEP 4  [needs 3]  Earn the commit verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole prior command in its own tool call, confirm `OK`,
        then commit the plan + document with `git commit -s` in a separate tool
        call. Per the batch-run brief for issue #1047, do NOT push and do NOT open a
        PR -- the commit stays local on `task/1047-provider-model` for a later
        cherry-pick into a shared batch PR.
        done when: the unittest run reports OK, the commit carries a
        `Signed-off-by:` trailer, and `git log` shows it on
        `task/1047-provider-model` with no corresponding remote push.

PARALLEL  None. Single target file, strictly sequential steps.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (must exit 0,
          this session). `review-adjudicate` and a cross-model final review pass are
          explicitly deferred to the batch owner's later integration step -- not run
          in this session.

BUDGET    STEP 2. The hard part is staying at the abstract/general layer (the
          contract itself: discovery, the two operations, what's fixed vs. what a
          binding supplies) without drifting into any one binding's specifics --
          that drift is the named risk the issue's boundary note warns against.

OPEN      Whether "provider model" should also cover the `BackendKind::Local` path
          as a first-class alternative binding, or treat `Local` purely as "no
          provider" (the absence of the model). Planned handling: document `Local`
          as the trivial/degenerate case in the Comparison section (no discovery, no
          `info`/`deploy` round trip, direct spawn) since the spec itself frames
          `Local` vs `Provider{id,config}` as the one discriminator every agent
          record carries -- but the full local-spawn mechanics are `local-agent-
          compute.md`'s (#1045) subject, not restated here.

LEFT OUT  Editing `launchpad/docs/corpus/AGENTS.md` or any other existing corpus
          node. Any `relationships` edge to `layers-compute-backend-provider`,
          `layers-compute-kubernetes-provider`, `layers-compute-local-agent-compute`,
          `layers-compute-mesh-compute`, or `layers-compute-remote-agent-compute` --
          none is merged on `origin/launchpad` yet, so none is a legal target; the
          issue itself instructs against linking them for exactly this reason.
          Kubernetes-binding specifics (pod shape, GC, fingerprinting, Secret
          scheme), local-spawn env resolution mechanics, mesh transport rewrite
          details, and lifecycle/liveness (I3/I5) depth -- named as related but
          owned by the sibling documents, to keep this node to one concept per
          `AGENTS.md`'s "one node is one independently maintainable idea" rule.

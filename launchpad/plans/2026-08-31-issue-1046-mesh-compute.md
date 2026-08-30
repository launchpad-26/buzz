Issue #1046 — task: document layers/compute/mesh-compute.md (parent PRD #611)
Stated size: issue carries no explicit Size line; task brief caps this plan at 5 steps  ->  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  Worktree __worktrees/task-1046-mesh-compute exists on branch task/1046-mesh-compute,
  checked out from origin/launchpad at commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5.
  Target path launchpad/docs/corpus/layers/compute/mesh-compute.md does not exist on
  origin/launchpad (checked via `test -f` in the worktree) — no layers/ subtree exists
  in the corpus yet at all, so this task also creates that subtree.
  launchpad/docs/corpus/templates/concept.md is merged and present — the template to
  use, per the issue's own Objective wording ("the single canonical concept node").
  Investigation already located the real subject: Buzz's MeshLLM-based shared LLM
  compute, embedded in the desktop app (desktop/src-tauri/src/mesh_llm/,
  desktop/src/features/mesh-compute/), gated behind the Cargo mesh-llm feature and
  pinned to github.com/Mesh-LLM/mesh-llm tag v0.75.1. It is a distinct subsystem from
  crates/buzz-relay-mesh (the inter-relay QUIC mesh, BUZZ_MESH env seam) even though
  both use the word "mesh" — this is a boundary the node must state explicitly.
  Sibling compute-provider docs (#1041 backend-provider, #1042 kubernetes-provider,
  #1045 local-agent-compute, #1048 remote-agent-compute) are open drafts, NOT on
  origin/launchpad yet — confirmed via `find launchpad/docs/corpus -iname "*mesh*"` and
  a full corpus tree listing returning nothing under layers/. No relationship may
  target them.
  architecture-containers-desktop, architecture-containers-agent-runtime, and
  architecture-containers-relay exist on origin/launchpad and are legitimately
  related (mesh compute is embedded in the desktop container, is consumed by the
  agent-runtime's buzz-agent as an LLM provider, and uses the relay only as a generic
  Nostr store for discovery/membership).

STEP 1  Draft the node                                              [independent]
        Hand-author launchpad/docs/corpus/layers/compute/mesh-compute.md against
        node.schema.json and the concept.md template's required sections (definition,
        use cases, scope/omissions, etc.), id: layers-compute-mesh-compute,
        type: layers, status: draft, origin: launchpad. Cite real evidence already
        gathered from desktop/src-tauri/src/mesh_llm/*, desktop/src/features/mesh-compute/*,
        crates/buzz-test-client/tests/e2e_mesh_llm.rs, desktop/src-tauri/Cargo.toml,
        docs/buzz-shared-compute-dev.md, and crates/buzz-core/src/kind.rs. State the
        boundary against buzz-relay-mesh and against the sibling compute-provider docs
        explicitly in the scope section. Add references relationships only to the
        three already-merged container nodes named above.
        done when: the file exists with schema-shaped front matter and a body covering
        definition, use cases, boundary/non-goals, and scope-and-omissions.
STEP 2  Validate                                                    [needs 1]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
        worktree root. Fix any reported error (duplicate id, bad relationship target,
        malformed evidence entry) and re-run until clean.
        done when: the command exits 0.
STEP 3  Earn the verify-gate stamp and commit          [needs 2]  <- RUNS HERE
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own tool call and confirm OK. Then
        commit with `git commit -s -m "docs(corpus): document mesh compute (#1046)"`
        in a separate call. Do not touch the stamp file directly and do not use
        --no-verify.
        done when: the test suite reports OK and the commit exists on
        task/1046-mesh-compute with a Signed-off-by trailer.
STEP 4  Self-review against the DoD                                 [needs 3]
        Re-read the committed diff line by line against issue #1046's Definition-of-done
        checklist. Confirm exactly one hand-authored canonical document was added (no
        second concept folded in), confirm validate.py still exits 0, and note any
        second concept/contract discovered during drafting as a candidate follow-up
        (not filed here).
        done when: every DoD checklist line is confirmed satisfied or explicitly noted
        as N/A, and validate.py is re-run clean one final time.

PARALLEL  None. Steps 1-4 are strictly sequential: draft, validate, stamp+commit,
          self-review. There is only one document to author, so no fan-out applies.
GATES     corpus-review would normally follow authoring a node, but this task's own
          instructions route straight to the batch's shared integration PR instead of
          opening one here — no review-* skill runs in this worktree. qa explore mode
          does not apply: this is a documentation-only change with no runtime interface
          to exercise.
BUDGET    STEP 1 (drafting) is most likely to eat the budget — it is the only step with
          real judgement calls (evidence classification, boundary wording).
OPEN      Whether type: layers (vs. capabilities) is the best-fit enum value for a
          compute-sharing concept is a judgement call this plan makes but does not
          re-litigate per node — the issue's own target path (layers/compute/mesh-compute.md)
          already commits to layers, so this plan follows that rather than deciding it
          fresh.
          Whether the sibling compute-provider docs, once merged, should later gain a
          references edge back to this node is left to whichever of those tasks lands
          after this one — this node cannot add a forward-dangling relationship to an
          unmerged id.
LEFT OUT  No second corpus document (e.g. a separate node for buzz-relay-mesh, the
          inter-relay mesh) is created here, even though it surfaced during
          investigation as a distinct, documentable subsystem — it is a candidate
          follow-up issue, not folded in.
          No relationships to the not-yet-merged sibling compute-provider docs (#1041,
          #1042, #1045, #1048) — they do not exist on origin/launchpad yet, so any edge
          to them would be a hard validator error in CI even if it resolved locally.
          No changes to runtime product behavior, Cargo features, or the MeshLLM SDK
          pin — this is documentation-only.

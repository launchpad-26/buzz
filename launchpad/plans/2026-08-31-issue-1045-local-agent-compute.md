# Plan: issue #1045 — document layers/compute/local-agent-compute.md

Issue: launchpad-26/buzz#1045 ("task: document layers/compute/local-agent-compute.md")
Parent PRD: #611

Stated size: single small corpus document, DoD checklist only -> cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-1045-local-agent-compute` exists on branch
  `task/1045-local-agent-compute`, created from `origin/launchpad` at
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- The target file `launchpad/docs/corpus/layers/compute/local-agent-compute.md`
  does NOT exist yet (confirmed by `ls`) — no second canonical document
  collision.
- `launchpad/docs/corpus/templates/concept.md` is merged on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`)
  — this is a real, present template, not the "no template yet" path.
- `node.schema.json`'s `type` enum includes `layers`, matching the issue's own
  `type: layers` instruction from the batch-run brief.
- Evidence already gathered by reading the real source: the local-compute path
  lives in `desktop/src-tauri/src/managed_agents/` — `types.rs` (`BackendKind`
  enum: `Local` / `Provider{id,config}`), `runtime.rs`
  (`spawn_agent_child`, the `std::process::Command` spawn call and env-var
  assembly), `storage.rs` (`spawn_key_refusal`, the I1 identity-fail-closed
  check), `runtime_commands.rs` (`start_pair` refuses non-`Local` backends —
  "managed runtime pairs require a local agent"), `restore.rs` (launch-restore
  filters to `backend == BackendKind::Local`), `runtime/orphan_sweep.rs` and
  `runtime/instance_reaper.rs` (local-only process supervision via the
  `BUZZ_MANAGED_AGENT` env marker), `reserved_env_keys.rs`/`env_vars.rs`
  (spawn-time env layering and the reserved-key strip). `docs/remote-agents.md`
  is the formal spec for the sibling remote/provider path and explicitly scopes
  itself away from "the local machine" — it is a boundary source, not local
  compute's own definition.
- Two existing, merged corpus nodes are genuinely on-topic and safe
  `references` targets (ids confirmed present on `origin/launchpad`):
  `architecture-containers-desktop` (the app that performs local spawn) and
  `architecture-containers-agent-runtime` (the `buzz-acp` harness process
  being spawned).
- No open PR already targets issue #1045 (`gh pr list --search "1045"` ->
  empty).
- Repository revision for provenance: `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`
  (`git rev-parse HEAD` in the worktree).

STEP 1 — Draft front matter and evidence ledger [independent]

<- RUNS HERE

Write `launchpad/docs/corpus/layers/compute/local-agent-compute.md` front
matter by hand, directly against `node.schema.json` (equivalent in shape to
what `scaffold_node` would produce for a merged template). Fields: `id:
layers-compute-local-agent-compute`, `type: layers`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, reviewer]`. Evidence
ledger: one commit-citation FACT for the revision, then one FACT entry per
substantive claim about `spawn_agent_child`, `BackendKind::Local`,
`spawn_key_refusal`, the `start_pair`/`restore.rs` local-only gates,
orphan-sweep/instance-reaper supervision, and the reserved-env-key strip —
each citing the real file already read in ALREADY TRUE, classified FACT
(opened and read) or INFERENCE (reasoned, with `confidence`) per
`AGENTS.md`.

done when: the file exists with schema-shaped front matter (`id`, `type:
layers`, `status: draft`, `origin`, `audiences`, `evidence` non-empty) and
every evidence entry cites a path this step actually opened.

STEP 2 — Write the concept.md body sections [needs 1]

Follow `concept.md`'s required-section order: Title/intro, Definition
(one-sentence: local agent compute is Buzz Desktop launching, configuring
and supervising an agent's `buzz-acp` harness as a native OS subprocess on
the desktop's own machine, gated by `BackendKind::Local`), an optional
Mermaid diagram of the spawn/supervise/reap lifecycle, Background (why a
`Local`/`Provider` discriminator exists — cite `docs/remote-agents.md`'s
"one launcher among many" framing as the source), Use cases (default
managed-agent path; what a developer/operator needs to know about it),
Comparison (Local vs remote Provider — env re-resolution on every spawn vs.
no-op on live pods, `BUZZ_MANAGED_AGENT` marker only existing locally, the
`start_pair`/`restore.rs` local-only gates), and Scope and omissions naming
the sibling tasks (#1046 remote-agent-compute, #1041 backend-provider, #1042
kubernetes-provider, #1049 sprig-runtime) as explicitly out of scope, plus
anything expected but not verified.

done when: every required concept.md section is present, the Definition
section states one sentence defining the term before elaborating, and Scope
and omissions names both what this node excludes and what could not be
verified.

STEP 3 — Add relationships and self-check duplication [needs 2]

Add `relationships: [{type: references, target:
architecture-containers-desktop}, {type: references, target:
architecture-containers-agent-runtime}]` to the front matter (both ids
confirmed present on `origin/launchpad` in ALREADY TRUE). Re-read the drafted
body against the issue's DoD checklist line by line (defines the term in one
sentence; states boundaries/non-goals; links related concepts/implementation/
verification; examples don't introduce a second concept) and confirm no
second canonical document was created anywhere else in the diff.

done when: `relationships` is present and both targets are real ids on
`origin/launchpad`; a line-by-line pass against the issue's DoD checklist
finds no unmet bullet.

STEP 4 — Validate and earn the verify-gate stamp [needs 3]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and iterate on any reported error until exit 0. Then, as the
sole command in its own tool call, run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` and confirm
`OK`.

done when: `validate.py` exits 0 and the unittest discover run reports `OK`
with no failures or errors.

STEP 5 — Commit [needs 4]

`git commit -s -m "docs(corpus): document local agent compute (#1045)"` in
the worktree. Do not push, do not open a PR (this task's output is folded
into a later shared batch PR by a separate process).

done when: `git log -1` in the worktree shows the new commit on
`task/1045-local-agent-compute`, and `git status` shows a clean tree.

PARALLEL

None — five sequential steps, each depending on the previous one's file
state (front matter -> body -> relationships/self-check -> validation ->
commit). Nothing here is independent of the drafted content.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  (Step 4) before any commit.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must report `OK`, run as the sole command in its own tool call, before
  committing (Step 4/5) — this is the verify-gate stamp condition.
- No `git push` and no `gh pr create` under any circumstance for this task.

BUDGET

One document, one commit, no code changes, no test-suite changes beyond
running the existing corpus test discovery. Evidence-gathering reads are
already complete (see ALREADY TRUE); remaining work is authoring and
validation only.

OPEN

- Whether `scaffold.py`/`evidence.py`'s helper functions should have been
  invoked programmatically rather than front matter being hand-authored
  directly against `node.schema.json` — both produce schema-identical output
  for a merged template, and this plan chooses hand-authoring for
  auditability of each evidence citation; a builder must not second-guess
  this by trying to script scaffold_node mid-draft.
- Whether the Comparison section's Local-vs-Provider table duplicates
  content that more properly belongs in the future #1046
  (remote-agent-compute) node — left to the author's judgment in Step 2;
  Comparison must stay framed from local compute's own vantage point, not
  restate the provider protocol in full.

LEFT OUT

- Documenting the provider protocol, Kubernetes binding, or `sprig` runtime
  in any depth — those are #1046, #1041, #1042, #1049's own tasks; this node
  only names them as siblings in Scope and omissions.
- Any code change to `desktop/src-tauri/src/managed_agents/` — this is a
  documentation-only task; the "Impacted components" list in the issue names
  only the corpus doc and mechanical generated indexes.
- Filing any follow-up issue for a second concept discovered while
  drafting — none was found; if one turns up during Step 2, it is reported
  in the final summary, not filed by this task.

Issue #1143 — task: document layers/observability/readiness.md (child of Feature #611)

Stated size: not stated on the issue itself -> cap: 5 steps (batch instruction cap for this corpus-batch-author run)

ALREADY TRUE

- Repo is at commit ed133f4c5dbd546a67d963f11ffa630a4513b228 (origin/launchpad), worktree
  `__worktrees/task-1143-readiness` on branch `task/1143-readiness`.
- `launchpad/docs/corpus/layers/observability/readiness.md` does not exist yet (confirmed:
  `ls` on that path fails; `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus`
  lists no `layers/` directory at all yet).
- The readiness probe itself is real, implemented code: `readiness_handler` in
  `crates/buzz-relay/src/router.rs` (lines 409-449), registered at `GET /_readiness` on both
  the app router and the health-only router (`build_health_router`, port `config.health_port`,
  default 8080, doc'd at `crates/buzz-relay/src/config.rs:194-195`).
- The sibling task #1138 (`layers/observability/liveness.md`) has **not** merged to
  `origin/launchpad` and has no open PR either (`gh pr list` search for its title/number
  returned nothing at time of check) — the batch-dispatch note calling it "already merged"
  does not hold at this revision. There is therefore no `id` to link a `relationships` edge
  to yet; this plan treats that as "nothing to link to" per `AGENTS.md` step 9, not as an
  oversight.
- `node.schema.json`'s `type` enum has no per-layer breakdown; `layers` is the single closed
  value for "the corpus surface this node documents" and fits directly, since the target path
  is literally under `layers/`.
- No per-type template for `layers` exists yet; `templates/concept.md` is the closest
  existing template (Diátaxis Explanation form) and is the shape this node follows, since a
  readiness probe is exactly a mechanism a reader needs explained, not a field reference.

STEP 1 [independent]
Read issue #1143's own DoD checklist (already fetched) and the three related sources:
`node.schema.json`, `AGENTS.md`, `templates/concept.md`. Confirm target file absence and the
current `type` enum. done when: the plan's ALREADY TRUE section above reflects fresh
`git ls-tree`/`ls` output, not assumption.

STEP 2 [needs 1] <- RUNS HERE
Read the readiness implementation end to end: `router.rs` (`readiness_handler`,
`liveness_handler`, `build_health_router`), `state.rs` (`shutting_down`, `redis_pool` field
docs), `main.rs` (SIGTERM handling / grace window / `serve`), `config.rs` (`health_port` doc),
`crates/buzz-db/src/runtime/mod.rs` (`Db::ping`), and
`crates/buzz-db/src/store/deletion.rs` (`validate_serving_catalog` /
`validate_deletion_serving_catalog`). Cross-check against
`deploy/charts/buzz/values.yaml` (readinessProbe/livenessProbe block) and
`deploy/charts/buzz/README.md` (object-storage startup-probe interaction). done when: every
claim planned for the node's evidence ledger has a real file/line/symbol behind it, opened
directly, not recalled from the batch-dispatch note.

STEP 3 [needs 2]
Draft `launchpad/docs/corpus/layers/observability/readiness.md` using the `concept.md`
template shape (Definition, Background, Use cases, boundary-against-liveness in the
Definition/scope sections, Scope and omissions). Front matter: `id:
layers-observability-readiness`, `type: layers`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator, reviewer]`, one evidence entry per claim
(FACT for direct-code claims like the handler's own logic; TEAM_KNOWLEDGE for the issue's own
DoD requirements; no INFERENCE unless a claim is genuinely reasoned rather than read
directly). No `relationships` entry, per ALREADY TRUE's finding that the liveness id does not
exist on `origin/launchpad` yet. done when: the file exists, every DoD bullet in #1143's body
is satisfiable by re-reading the draft, and the doc stays scoped to the readiness probe
specifically (not re-deriving liveness, not becoming the `health-checks` umbrella #1137 owns).

STEP 4 [needs 3]
Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root and confirm
it reports zero FAILs for the new node (pre-existing FAILs/UNVERIFIED elsewhere are known and
out of scope). Fix anything the new node fails on. done when: validate.py's output contains no
FAIL line naming `readiness.md` / `layers-observability-readiness`.

STEP 5 [needs 4]
Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call; confirm `OK`. In a separate tool call, `git add` the
new doc plus this plan file and `git commit -s` with message
`docs(corpus): document readiness probe (#1143)`. done when: the test command alone prints
`OK`, and the commit exists containing only the two intended files (`git show --stat HEAD`).

PARALLEL

- None of the 5 steps run concurrently with each other in this task; sibling issues
  (#1135-#1137, #1140-#1142, #1144-#1145) are being authored by other agents in their own
  worktrees at the same time, which is why STEP 3 deliberately does not add a relationships
  edge to any of them (none are merged yet) and stays disciplined about scope (readiness only,
  not liveness or the health-checks umbrella).

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must show zero FAILs for the new
  node (STEP 4).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  must print `OK`, run as the sole command in its own tool call, separate from the commit
  (STEP 5). This substitutes for a commit-gate hook per the batch instructions.
- No `git push`, no `gh pr create` — this commit is cherry-picked onto a shared batch branch
  later by the batch owner.

BUDGET

- One corpus document (`launchpad/docs/corpus/layers/observability/readiness.md`) plus this
  plan file. No source code changes — this is a documentation-only task.

OPEN

- Whether `layers-observability-liveness` (issue #1138) lands with that exact `id` is not
  this task's decision; when it merges, a `references` (or similar) edge from this node to it
  is a natural follow-up, left for whoever runs the deferred-relationships backfill (the
  batch's version of the pattern `AGENTS.md`/#1489 describe for corpus standards nodes).
- Whether `type: layers` is the definitively "best" fit versus some future narrower
  observability-specific type value is a taxonomy question this task does not have standing
  to resolve (per `corpus-standard-taxonomy`'s own guidance) — `layers` is the direct, named
  fit today and is used without further hedging.

LEFT OUT

- No edit to any sibling observability document (`liveness.md`, `health-checks` umbrella,
  `logging.md`, etc.) — each is its own task, authored by a different agent in this batch.
- No change to the actual readiness probe implementation (`router.rs`) — this is a
  documentation task only; any implementation gap found while reading is a candidate for a
  new issue, not a fix folded in here.
- No relationships edge to the liveness node, since it is unmerged at this revision (see
  ALREADY TRUE and OPEN above) — adding one now would fail validation the moment CI resolves
  against `origin/launchpad`, per `AGENTS.md` step 9's exact warning.

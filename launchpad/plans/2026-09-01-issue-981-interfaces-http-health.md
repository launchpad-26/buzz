# Plan: issue #981 — interfaces/http/health corpus node

Issue #981 (launchpad-26/buzz), parent Feature #616.
Stated size: single hand-authored corpus document -> cap: 5 steps.

ALREADY TRUE

- `launchpad/docs/corpus/interfaces/http/health.md` does not exist. Confirmed with
  `ls launchpad/docs/corpus/interfaces` (No such file or directory) and
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` (no
  `interfaces/` entry at all), both run from this worktree at
  HEAD `650354eab8d41ab6ce1a71de079a6c6d95c69052`.
- The worktree `__worktrees/task-981-interfaces-http-health` on branch
  `task/981-interfaces-http-health` already exists, checked out from
  `origin/launchpad` at the same revision. RUNS HERE.
- `node.schema.json`'s `type` enum has 13 members; the only interface-shaped one is
  `interfaces-events` (confirmed by reading the schema file directly and by
  `launchpad/docs/corpus/templates/interface.md`'s own "A note on `type`" section,
  which states a node built from that template "therefore carries
  `type: interfaces-events`").
- The relay's health-probe HTTP surface is fully read and understood from source:
  `crates/buzz-relay/src/router.rs` defines `/health` (app router only, always 200),
  `/_liveness` (app + health-only router, always 200), `/_readiness` (app +
  health-only router, checks shutdown flag + Postgres ping + Redis pool + deletion
  serving catalog under a 2s timeout, 200/503), `/_status` (health-only router only,
  service/version/uptime/build JSON), and `/_mesh` (health-only router only, mesh
  peer status JSON, `{"enabled": false}` when mesh is off). `build_health_router`'s
  doc comment states "No metrics middleware, no auth, no CORS, no body limit" and no
  auth/CORS/metrics layer is applied to `api_router` either, so none of the five
  routes require authentication.
- `deploy/charts/buzz/values.yaml:143-164` is the authoritative machine spec: K8s
  `livenessProbe`/`readinessProbe`/`startupProbe` wired to `/_liveness` and
  `/_readiness` on the `health` container port, with concrete thresholds
  (`initialDelaySeconds`, `periodSeconds`, `timeoutSeconds`, `failureThreshold`).
  `deploy/charts/buzz/templates/service.yaml:18` and
  `deploy/charts/buzz/templates/deployment.yaml:114,119` wire `Values.service.healthPort`
  (`values.yaml:238` = `8080`) to the container's `health` port and
  `BUZZ_HEALTH_PORT` env var, matching `crates/buzz-relay/src/config.rs`'s
  `health_port` default of `8080` and `crates/buzz-relay/src/main.rs`'s
  `serve()` binding it as `Listener 3`.
- The merged corpus tree at `origin/launchpad` already contains
  `corpus-template-interface` (`launchpad/docs/corpus/templates/interface.md`) and
  `architecture-deployment-kubernetes`
  (`launchpad/docs/corpus/architecture/deployment/kubernetes.md`) — both valid
  `relationships[].target`s, confirmed against the `git ls-tree` listing above, not
  against this worktree. No sibling `interfaces/http/*.md` node exists on
  `origin/launchpad`, so no such sibling can be a relationship target yet.
- `python3 launchpad/project-intelligence/corpus/validate.py` and
  `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
  both run from the repo root with plain `python3` (no Hermit activation
  required for the direct form, per `AGENTS.md`'s "Running the check" section).

STEP 1 [independent]

Draft `launchpad/docs/corpus/interfaces/http/health.md`: front matter
(`id: interfaces-http-health`, `type: interfaces-events`, `status: draft`,
`origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`, an
`evidence` ledger with a commit-citation provenance entry plus one entry per
substantive claim below, classified FACT/INFERENCE/TEAM_KNOWLEDGE per
`AGENTS.md`'s rules, and `relationships` to `corpus-template-interface`
(`implements`) and `architecture-deployment-kubernetes` (`references`)); and a body
following `templates/interface.md`'s required sections (Interface description,
Operations table for all five routes, Contract and stability, Boundary, a valid
example + a failure example for `/_readiness`, Relationships, Scope and omissions)
that satisfies every Definition-of-done bullet in issue #981: inputs, outputs,
error/rejection behavior, authentication (state plainly that none is required),
versioning/compatibility, ordering/idempotency (state plainly whether it applies),
the Helm-chart probe spec link, and the two examples.

done when: the file exists at that path, is the only new hand-authored file under
`launchpad/docs/corpus/`, and every DoD bullet from issue #981's body is addressed
somewhere in its front matter or prose (manually checked line by line against the
issue body captured in step 2 of the task brief).

STEP 2 [needs 1]

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo root
and fix any FAIL line the new node introduces (UNVERIFIED notices are expected and
acceptable).

done when: the command exits 0.

STEP 3 [needs 2]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own tool call.

done when: the command prints `OK` and exits 0.

STEP 4 [needs 3]

Stage exactly the two files (`launchpad/docs/corpus/interfaces/http/health.md`,
this plan file) and commit with `git commit -s`.

done when: `git log -1` shows a new commit on `task/981-interfaces-http-health`
signed off, containing only those two files (`git show --stat HEAD`).

STEP 5 [needs 4]

Self-review: re-read the diff against issue #981's DoD checklist line by line,
re-open every source cited as FACT/INFERENCE to confirm it says what the claim
says, confirm no second hand-authored canonical corpus document was created, and
re-run `validate.py` to confirm it still exits 0.

done when: all four checks above pass and are reported in the final summary.

PARALLEL

None of these steps can run in parallel with each other — steps 2-5 each depend on
the previous step's file state or exit status. Step 1 is the only `[independent]`
step because it has no prior step to depend on within this plan.

GATES

- `validate.py` exit 0 (step 2) gates the commit.
- `python3 -m unittest discover ... -p "test_*.py"` printing `OK` (step 3) gates the
  commit, run as its own isolated tool call per the task brief so its exit status is
  unambiguous.
- The commit itself is gated by whatever pre-commit hook is installed in this
  worktree; if `git commit -s` is rejected for a missing gate stamp, that is reported
  as a finding, not routed around with `--no-verify` or a hand-authored stamp file.

BUDGET

One file created, one plan file created, two tool-gated check runs, one commit. No
code changes, no CI triggers beyond the corpus-validate workflow on push (this
branch is not pushed by this plan).

OPEN

- Whether `ordering/idempotency` needs its own dedicated evidence entry beyond
  "these are read-only GET probes with no state mutation, so ordering/idempotency
  does not meaningfully apply" is a judgment call left to step 1's drafting, not
  decided here.
- Whether the eventual `interfaces/http/*` sibling nodes (events/query/count bridge,
  media, git, admin, etc.) should later `references` this node, or vice versa, is
  explicitly out of scope per issue #981's "Out of scope" section and is not
  decided by this plan.

LEFT OUT

- No relationship to a sibling HTTP interface node is added, because none exists on
  `origin/launchpad` yet (per AGENTS.md's merge-target rule) — adding one now would
  either fail validation or silently point at a node that does not yet exist in CI.
- No change to `crates/buzz-relay` source, `deploy/charts/buzz`, or any other
  runtime/deployment artifact — issue #981 is documentation-only and any behavior
  change belongs to a separately linked implementation issue.
- No generated corpus index is touched; none exists yet for this corpus subtree.

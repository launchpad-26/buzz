Issue #1220 — task: document operations/runbooks/high-error-rate.md
Stated size: no `Size` label on issue #1220; the corpus-batch-author dispatch brief caps this single-document authoring task  →  cap: 5 steps

ALREADY TRUE  (verified against git and the worktree, not notes)
  Worktree /home/serina/Launchpad/buzz/__worktrees/task-1220-runbooks-high-error-rate exists,
    branch task/1220-runbooks-high-error-rate is checked out and, per `git status`, up to date
    with origin/launchpad — no rebase needed.
  `git rev-parse HEAD` in that worktree returns 473205a7457b208455f188847bfb27b01aa83cac.
  `ls launchpad/docs/corpus/operations/runbooks/` fails with "No such file or directory" — the
    target file does not exist yet, and neither does its parent directory.
  `launchpad/docs/corpus/templates/runbook.md` exists and its "Required sections" enumerate:
    Trigger, Severity and impact, Diagnosis, Mitigation and resolution, Escalation, and Scope
    and omissions (six items; the last one folds in "what was expected but could not be
    verified").
  `launchpad/docs/corpus/schema/node.schema.json` requires exactly `id`, `type`, `status`,
    `origin`, `audiences`, `evidence`, and permits only `relationships` besides those — no other
    front-matter key validates.
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` lists
    `launchpad/docs/corpus/layers/observability/{metrics,readiness,liveness,health-checks,
    logging,structured-logging,prometheus,opentelemetry,tracing}.md` as already-merged files,
    so their corresponding node ids (e.g. `layers-observability-metrics`,
    `layers-observability-readiness`) are legal `relationships` targets today.
  `crates/buzz-relay/src/metrics.rs` defines `track_metrics` middleware that records
    `http_requests_total{code,caller,action}` and explicitly skips `/_*`, `/health`, and
    `/metrics` paths.
  `crates/buzz-relay/src/router.rs` defines `readiness_handler` (checks the shutdown flag,
    Postgres, Redis, and the deletion-serving catalog) and it contains no `metrics::counter!`
    call on any branch — a readiness failure is invisible to `http_requests_total`.
  `prometheus.yml` (repo root) and `docker-compose.yml`'s `prometheus` service together show a
    local-only Prometheus at `http://127.0.0.1:9090` scraping `host.docker.internal:9102`; no
    Alertmanager config or `*.rules.yml` file exists anywhere in the repository.
  `launchpad/ENVIRONMENTS.md` marks the only internet-facing environment ("Cohort VPS") as
    `OPEN`, not `IMPLEMENTED` — there is no live production relay this runbook could name an
    on-call rotation or paging tool for.

STEP 1  Write the corpus node's front matter and body at                    [independent]
        launchpad/docs/corpus/operations/runbooks/high-error-rate.md, following
        runbook.md's six required sections and citing only sources actually opened
        during evidence-gathering (crates/buzz-relay/src/{metrics,router,connection,
        telemetry,config}.rs, crates/buzz-relay/src/handlers/{event,auth,count,req}.rs,
        docker-compose.yml, prometheus.yml, Justfile, ENVIRONMENTS.md).                ← RUNS HERE
        done when: the file exists at that path, has schema-shaped front matter (id
        `operations-runbooks-high-error-rate`, type `operations`, status `draft`), and
        a body with a heading for each of runbook.md's six required sections.
STEP 2  Run the corpus validator and fix whatever it reports, iterating until   [needs 1]
        it exits clean.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0.
STEP 3  Run the corpus test suite as the sole command in its own Bash call      [needs 2]
        (no pipe, no chained `cd`) and confirm it stamps the verify gate.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` prints `OK` and the subsequent commit is not refused for a
        missing stamp.
STEP 4  Commit the new node and this plan file locally with a DCO sign-off.     [needs 3]
        done when: `git log -1` shows a commit whose subject matches
        `docs(corpus): ... (#1220)` and whose trailer includes `Signed-off-by`, and
        `git status` reports a clean tree.
STEP 5  Self-review the commit's diff against every Definition of Done bullet   [needs 4]
        on issue #1220 (including the runbook-specific tail bullets), and prepare the
        step-8 report the dispatch brief specifies.
        done when: each DoD bullet is explicitly marked satisfied, or named as not
        satisfied, in the report handed back.

PARALLEL  None of these five steps can run as independent subagents: 2 needs the file 1
          writes, 3 needs 2's clean validation before the commit gate means anything, 4
          needs 3's stamp, and 5 needs 4's actual commit SHA to review against. This is a
          single-document, single-agent task by the batch brief's own design (issue #1220
          is one node in a fan-out where each sibling issue is its own agent), so there is
          no fan-out inside this plan either.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 (end of
          step 2) before the commit gate in step 3 is attempted. The corpus unit-test
          suite (step 3) is the verify-gate stamp this branch's commit hook checks for —
          it must run as a lone, unpiped command or the hook refuses the stamp. No
          `review-*` skill applies inside this plan: the batch brief routes review to the
          orchestrator once all sibling documents are integrated into one Feature PR. `qa`
          explore mode does not apply — this is a documentation-only change with no
          runtime interface (CLI, API, UI) to exercise.
BUDGET    Step 1 is the step most likely to eat the budget: honestly scoping what this
          repository does *not* implement (no alerting rule, no Alertmanager, no
          production host yet per ENVIRONMENTS.md) while still citing only sources
          actually opened takes more care than describing a mechanism that exists.
OPEN      Whether the eventual Cohort VPS deployment (ENVIRONMENTS.md, status `OPEN`) will
          reuse today's default ports (health 8080, metrics 9102) and today's manual
          Prometheus-query diagnosis, or introduce a real alerting/paging tool, is not
          decided by any merged source; this runbook documents today's mechanism and
          names the gap rather than guessing the future one. Whether a Prometheus
          alerting rule for elevated error rate will ever be added to this repository is
          likewise undecided.
LEFT OUT  No Prometheus alerting rule, Grafana dashboard, or Alertmanager route is added —
          none exists today, the issue's Definition of Done does not ask for one, and
          inventing one would be exactly the fabricated-procedure failure mode the batch
          brief warns against. No second corpus node is created (e.g. a runbook for a
          different alert) — that would violate "exactly one hand-authored corpus
          document." No relay runtime change (such as adding a metric on readiness
          failure) is made here — that is implementation work for a separate issue, and
          if it surfaces while drafting it is reported, not folded in.

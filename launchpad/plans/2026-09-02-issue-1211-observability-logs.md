# Issue #1211 — operations/observability/logs.md

Stated size: none given on the issue itself; the batch dispatch brief caps every task at one document  ->  cap: 5 steps

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
`launchpad/docs/corpus/templates/reference.md`, and the merged `layers/observability/` nodes
(`layers-observability-logging`, `layers-observability-structured-logging`, plus
`architecture-deployment-docker-compose` and `architecture-deployment-kubernetes`) are present
on `origin/launchpad` at `HEAD` (`473205a7457b208455f188847bfb27b01aa83cac`, confirmed via
`git rev-parse HEAD` and `ls`); `launchpad/docs/corpus/operations/observability/logs.md` does
not exist yet (confirmed: `ls` reports no `operations/` directory under the corpus root at all).

STEP 1  [independent] Gather evidence: read `crates/buzz-relay/src/main.rs` (tracing
subscriber install, `RUST_LOG`/`BUZZ_OTEL_FILTER` wiring) and `crates/buzz-relay/src/telemetry.rs`
(JSON formatter, `trace_id`/`span_id` injection, its own test module's asserted JSON keys);
`.env.example` and `deploy/compose/.env.example` (RUST_LOG defaults per environment);
`Justfile`'s `logs` recipe; `deploy/compose/run.sh`'s `logs` case and `launchpad/deploy/run.sh`'s
exec-wrapper relationship to it; `deploy/charts/buzz` (no log-shipping sidecar, no chart-level
`RUST_LOG` override, `extraEnv`/`extraEnvFrom` as the only operator knob);
`crates/buzz-relay/src/config.rs` (`KlipyConfig`'s redacted `Debug` impl vs. `Config`'s derived,
unredacted `Debug`, and confirmation no call site logs the whole `Config`); and the pre-existing
(non-corpus) `launchpad/docs/Observability/current-state/relay.md` research doc's "Logs",
"Export boundaries", and "Sensitive-data handling" sections. ← RUNS HERE
done when: every path above has been opened and read (not just grepped), the revision is
recorded (`git rev-parse HEAD`), and a list of claims-with-citations exists to draft STEP 2 from.

STEP 2  [needs 1] Write the front matter (`id: operations-observability-logs`,
`type: operations`, `status: draft`, `origin: launchpad`, `audiences: [operator, developer,
agent]`, one `evidence` entry per substantive claim, `relationships: references` toward the
four already-merged nodes named above) and the body per `templates/reference.md`'s required
sections: Reference description; a structured-entries table for `RUST_LOG` /
`BUZZ_OTEL_FILTER` / `OTEL_EXPORTER_OTLP_ENDPOINT` / the JSON field set / the one redaction
mechanism found; a Commands table for `just logs`, `deploy/compose/run.sh logs` (and its
`launchpad/deploy/run.sh` wrapper), `docker compose logs`, `kubectl logs`; an explicit Boundary
paragraph naming metrics/traces/alerts/dashboards as sibling in-flight nodes (named in prose,
not linked — they are not merged); Relationships; and Scope and omissions carrying both the
ownership table and the not-verified-here list (CAKE retention, staging cluster log handling,
whether `Config`'s unredacted `database_url` field is ever logged by a path this review did not
find).
done when: `launchpad/docs/corpus/operations/observability/logs.md` exists, matches the
template's required-sections list, and every claim in its body has a corresponding `evidence`
entry citing a source actually opened in STEP 1.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root; fix whatever it names and re-run until exit 0.
done when: the command's exit status is 0 in the same terminal output being read.

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own Bash call to earn the verify-gate stamp.
done when: the command's own output contains `OK` and nothing was piped or chained around it.

STEP 5  [needs 4] In a separate tool call, `git add -A && git commit -s -m "docs(corpus): document operations/observability/logs.md (#1211)"`. Commit locally only — no push, no PR (batch orchestrator integrates later).
done when: `git log -1` shows the new commit with a `Signed-off-by` trailer and `git status`
reports a clean working tree.

PARALLEL: none — single file, single task, one worktree.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The unittest
discover run in STEP 4 must print `OK` before the commit in STEP 5. Cross-model final review is
deferred to the batch orchestrator, not run here.

BUDGET: small — one reference document, no code changes; evidence gathering scoped to
`buzz-relay`'s tracing/telemetry modules, `Justfile`, two `.env.example` files, `deploy/`
compose+chart material, and one pre-existing research doc already open at authoring time.

OPEN: Whether `Config`'s derived (unredacted) `Debug` impl is ever actually reached by a log
call anywhere outside `crates/buzz-relay` was checked only within that crate's own source — a
grep found no call site logging the whole struct, but this is not an exhaustive
workspace-wide proof. Reported as a gap in the body's scope section, not silently assumed safe.

LEFT OUT: No relationship declared toward the sibling `operations/observability/{metrics,
traces,alerts,dashboards}` nodes — they are being authored in parallel in this same batch run
and are not merged on `origin/launchpad`, so naming them as a `relationships.target` would be a
hard CI failure per `AGENTS.md`'s own worked example of exactly this mistake. No attempt to
resolve whether Block's internal CAKE log pipeline applies retention or redaction — that
infrastructure is outside this repository. No re-litigation of `layers-observability-logging`'s
or `layers-observability-structured-logging`'s content — this node links them rather than
repeating their per-surface survey or JSON-mechanics detail.

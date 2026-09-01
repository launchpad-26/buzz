Issue #1213 — task: document operations/observability/traces.md
Stated size: no `Size` line -> cap: 5 steps (single-document corpus task, per the batch dispatch brief)

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1213-observability-traces`, based on `origin/launchpad` at
    `473205a7457b208455f188847bfb27b01aa83cac` (`git rev-parse HEAD` confirmed).
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
    `launchpad/docs/corpus/templates/reference.md` are merged on `origin/launchpad`.
  `layers-observability-tracing`, `layers-observability-opentelemetry` and
    `layers-observability-datastore-tracing` are merged on `origin/launchpad` (confirmed
    against `<SCRATCH>/existing-node-ids.txt` and by reading each file directly in this
    worktree) — they cover, respectively, `tracing`-crate span instrumentation, the
    OTEL SDK/exporter wiring, and the datastore proc-macro's policy mechanics, all from a
    developer/implementation angle.
  `launchpad/docs/corpus/operations/observability/traces.md` and its parent `operations/`
    directory do not exist anywhere in the worktree (`test -f` and `ls` both confirmed
    absent).

STEP 1  [independent]  Gather evidence directly rather than borrowing the three merged
        `layers/observability` nodes' citations: read `crates/buzz-relay/src/telemetry.rs`
        in full, `crates/buzz-relay/src/main.rs` lines ~85-149, `.env.example` lines
        ~174-183, the workspace `Cargo.toml` OTEL dependency block, `crates/buzz-relay/
        src/connection.rs` lines ~555-600, `crates/buzz-relay/src/handlers/event.rs` lines
        ~598-620, `crates/buzz-relay/src/router.rs` lines ~200-221, and CONTRIBUTING.md's
        "Logging and Tracing" section. Grep the workspace plus `deploy/` and
        `launchpad/deploy/` for `traceparent`, `otel`, `opentelemetry`, `jaeger`, and
        `collector` to independently confirm which crate(s) export spans, whether any
        collector is configured anywhere in this repository's own deployment material,
        and whether cross-process trace-context propagation exists.
        done when: every claim the node will make has a source opened in this step, and
        each absence claim (no collector config, no header propagation) has a recorded
        search and a zero-match result rather than an assumption.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/operations/observability/
        traces.md`: schema-valid front matter (`id: operations-observability-traces`,
        `type: operations`, `status: draft`, `origin: launchpad`, `audiences` including
        `operator`, an `evidence` ledger with a commit citation first, one entry per
        substantive claim, `relationships` limited to `references` toward the three
        merged `layers/observability` siblings from ALREADY TRUE) and a body against
        `templates/reference.md`'s required sections: reference description, a
        structured-entry table of the trace-related environment variables an operator
        sets, an optional Commands table of verification commands, a boundary statement
        distinguishing this operator-facing config/verification reference from the three
        merged developer-facing `layers/` nodes, and a scope-and-omissions section
        carrying both the ownership boundary (naming the logs/metrics/alerts/dashboards
        siblings in prose only, per the dispatch brief, since none of their nodes resolve
        on `origin/launchpad` yet) and what was expected but could not be verified (the
        staging Kubernetes collector configuration lives in the private
        `squareup/block-coder-tf-stacks` repository, not this one).
        done when: the file exists at the assigned path with every schema-required key
        present and every `##` section this step names actually in the body.

STEP 3  [needs 2]  Run `python3 launchpad/project-intelligence/corpus/validate.py` from
        the repository root and fix anything it reports until it exits 0.
        done when: the command's own exit code is 0, confirmed by reading `$?` after the
        run, not inferred from absent error text.

STEP 4  [needs 3]  Self-audit the finished node line by line against issue #1213's DoD
        checklist and the operations/reference tail bullets (structured for lookup,
        facts-only with generated-vs-authored labelled, scope and omissions defined,
        authoritative source/schema/config linked), confirm every evidence entry
        supports the claim it sits under, confirm no second hand-authored corpus document
        was created, and re-run `validate.py` once more after any fix.
        done when: the audit maps each DoD bullet to where the body satisfies it, and
        `validate.py` exits 0 on the final version.

STEP 5  [needs 4]  Earn the verification stamp by running
        `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        as the sole command in its own tool call (no pipe, no chained `cd`), confirm `OK`,
        then in a separate tool call stage and commit the plan file and the new document
        with `git commit -s`. No push, no PR — this task stops at a local commit per the
        dispatch brief.
        done when: the unittest run reports `OK`; the commit succeeds without a
        "no verification stamp" refusal; `git log -1` on the branch shows the new commit
        with a `Signed-off-by` trailer.

PARALLEL  None. One target file plus this plan file, strictly sequential, single
          worktree, single agent.

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (STEP 3, re-run in
          STEP 4) and the corpus unittest suite (STEP 5) are the only automated gates run
          in this session. `review-code`, `review-adjudicate`, and any cross-model final
          pass are explicitly deferred to the batch orchestrator's later integration and
          review pass — none of them run here.

BUDGET    STEP 2. The hard part is keeping this node operator-facing (config knobs,
          verification, what exists versus what does not in deployment) without
          re-narrating the two merged `layers/` nodes' developer-facing instrumentation
          and exporter-internals content. Evidence gathering is capped at the source
          paths listed in STEP 1 plus whatever the absence-claim greps touch.

OPEN      Whether a `part-of` or reciprocal `references` edge should later be added from
          the `layers/observability` nodes back to this one, once this node merges — this
          plan only adds the forward edges this node is itself allowed to declare today,
          and does not edit the three already-merged sibling nodes.

LEFT OUT  Any `relationships` target naming the logs (#1211), metrics (#1212), alerts
          (#1209) or dashboards (#1210) sibling operations nodes — they are being
          authored in parallel in separate worktrees this same batch run and do not
          resolve on `origin/launchpad` yet, so a target at any of their ids would
          validate here and become a hard CI failure once merged. The boundary with
          logging (request correlation without an exported trace) is named in prose
          instead, per the dispatch brief.
          Standing up or configuring an actual OTLP collector — out of scope; this node
          documents what the repository does and does not provide today, not a
          recommended deployment.

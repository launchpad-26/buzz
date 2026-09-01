Issue #1218 — task: document operations/reliability/object-storage-failure.md
Stated size: no `Size` line -> cap: 4 steps (single hand-authored document, category: operations/reference)

ALREADY TRUE  (verified against git, not notes)
  Worktree HEAD is 473205a7457b208455f188847bfb27b01aa83cac, branch `task/1218-reliability-object-storage-failure`
    tracking `origin/launchpad`. `launchpad/docs/corpus/operations/` does not exist at all (no
    `operations`-typed node has merged yet); `launchpad/docs/corpus/operations/reliability/object-storage-failure.md`
    does not exist. `launchpad/docs/corpus/architecture/containers/object-storage.md`
    (`architecture-containers-object-storage`) is merged on `origin/launchpad` and is a legal
    `relationships` target. The sibling runbook, issue #1223
    (`operations/runbooks/object-storage-unavailable.md`), is unmerged — named in prose only,
    never linked or targeted.

STEP 1  [independent]  Gather evidence on object-storage failure behavior across both consumers. Read
        `crates/buzz-media/src/storage.rs` (MediaStorage: no retry logic, no client-side
        timeout config, error mapping to `MediaError::{NotFound, StorageError}`),
        `crates/buzz-media/src/error.rs` (`MediaError`'s `IntoResponse`: `NotFound`->404,
        `StorageError`/`Internal`/`Io`->500 generic "internal error", `ServiceUnavailable`->503
        exists as a variant but is not constructed from a storage failure), `crates/buzz-relay/src/api/media.rs`
        (`upload_blob`/`get_blob`/`head_blob` propagate `MediaError` via `?` with no
        storage-specific handling), `crates/buzz-relay/src/api/git/store.rs` (`StoreError`,
        `run_conformance_probe`/A3 gate), `crates/buzz-relay/src/main.rs` (the conformance probe
        is fatal at startup — `BUZZ_GIT_CONFORMANCE_PROBE`), `crates/buzz-relay/src/api/git/transport.rs`
        (`hydrate_error_to_response`: backend failure -> 500, resource limit -> 413;
        `finalize_push_inner`: CAS conflict -> 409, backend error -> 500, deletion-fence
        loss -> 503), `crates/buzz-relay/src/storage_sweep.rs` (hourly sweep: bounded timeout,
        non-fatal failure, stale-cache-serving on transient blips), `crates/buzz-relay/src/router.rs`
        (`readiness_handler`: checks Postgres/Redis/deletion-catalog only — object storage is
        never part of the readiness signal), and `docs/git-on-object-storage.md` (durability
        theorems, the A1-A3 axioms, "retry is policy, not safety", client-side re-push as the
        only safe retry). Record what a documented request timeout would look like for the
        media path, since none was found in `MediaConfig`. ← RUNS HERE
        done when: every source named above has been opened and a one-line note taken naming
        the claim it will support.

STEP 2  [needs 1]  Write `launchpad/docs/corpus/operations/reliability/object-storage-failure.md`
        against the reference template (`launchpad/docs/corpus/templates/reference.md`):
        schema-valid front matter (`id: operations-reliability-object-storage-failure`,
        `type: operations`, `status: draft`, `origin: launchpad`,
        `audiences: [operator, developer, reviewer]`, one `references` relationship to
        `architecture-containers-object-storage`, an `evidence` ledger with the HEAD commit
        citation plus one entry per substantive claim from STEP 1). Body: Reference
        description paragraph; a structured-entries table of failure surfaces (media
        upload/download, git read, git write/CAS, storage sweep, startup conformance probe)
        each with observed HTTP status / process behavior and citation; a Boundary section
        naming this as failure-mode reference only (not the runbook — name issue #1223 by
        number in prose, no link, since it is unmerged); a scope-and-omissions section
        carrying both what the node does not cover (owner-named) and what was expected but
        could not be verified (e.g. no found repository evidence of a client-side S3 request
        timeout on the media path, unlike the git pack-capture and storage-sweep timeouts that
        do exist).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 with
        the file present, and every table row and MUST-adjacent claim has a matching
        `evidence` entry that was actually opened in STEP 1.

STEP 3  [needs 2]  Self-audit the finished node against issue #1218's DoD checklist bullet by
        bullet (including the four reference-specific tail bullets: structured for lookup;
        facts-only with generated-vs-authored labelling — n/a here, no generated values;
        scope and omissions defined; authoritative source/schema/config linked), confirm no
        citation rests on a file that was not opened, and confirm no second concept (e.g. the
        recovery runbook itself) was folded in.
        done when: the audit is written inline in this session's notes (not committed) and
        `validate.py` still exits 0.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        prior command, then commit the plan + document in a separate call. Do not push, do
        not open a PR — orchestrator integrates this branch into the Feature PR later.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports OK, and `git commit -s` succeeds without a "no verification stamp" block.

PARALLEL  None. One target file, sequential steps, single worktree already assigned.

GATES     Corpus validator (`validate.py`) and the corpus unittest suite, both run locally in
          this session. `review-adjudicate` and a cross-model final pass are explicitly
          deferred to the batch orchestrator's later integration review — not run here.

BUDGET    STEP 1/2. The hard part is keeping the document to failure-mode *reference* — what
          degrades, how, and what the client observes — without drifting into the sibling
          runbook's operator-response-procedure territory, and without asserting operational
          practice (alerting thresholds, on-call steps) this repository does not implement.

OPEN      Whether a client-side S3 request timeout exists on the media path at all. No
          `MediaConfig` field or `rust-s3`/`reqwest` client-builder call setting one was found
          in `crates/buzz-media`, unlike the explicit `tokio::time::timeout` wrappers around
          the storage sweep and the git pack-capture/compaction/subprocess paths. This is
          reported as a named gap in the node's scope-and-omissions section rather than
          asserted either way.

LEFT OUT  The operator response procedure (diagnosis, mitigation, recovery steps, escalation)
          for an object-storage outage — that is issue #1223's runbook, not this reference
          node, and is named but never linked (unmerged). Any `relationships` edge beyond
          `references: architecture-containers-object-storage` — no other operations-typed
          sibling exists yet on `origin/launchpad`. Alerting/dashboard configuration, since no
          Prometheus alert rule or dashboard definition for object-storage health was found in
          this repository at STEP 1 evidence-gathering time (reported as an honest absence in
          the body, not invented).

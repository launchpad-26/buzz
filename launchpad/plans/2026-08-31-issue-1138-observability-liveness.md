Issue #1138 — task: document layers/observability/liveness.md
Stated size: none stated  →  cap: 5 steps (feature #611 corpus batch: single concept
  document against conventions already settled by #636/AGENTS.md, not the first node)

Target file: `launchpad/docs/corpus/layers/observability/liveness.md`
Node id: `layers-observability-liveness` (assigned by the issue brief; permanent)
Base branch: `origin/launchpad` at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5

ALREADY TRUE  (verified against git at 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5, not notes)
  `git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus` carries no
    `layers/` subtree at all — this task creates `layers/observability/`.
  `launchpad/docs/corpus/layers/observability/liveness.md` does not exist; no collision.
  `crates/buzz-relay/src/router.rs` defines `liveness_handler` (line 370) as an
    unconditional `(StatusCode::OK, "ok")` with no dependency checks — registered twice,
    once on the main app router (`build_router`, line 69) and once on the dedicated
    health-only router (`build_health_router`, line 247-254, doc-commented "K8s probes,
    port 8080 in CAKE"). `readiness_handler` (line 375) is a separate handler that checks
    the `shutting_down` flag plus Postgres/Redis/deletion-catalog connectivity — a
    materially different mechanism from liveness.
  `deploy/charts/buzz/values.yaml` (lines 141-148) sets `relay.livenessProbe` to an
    `httpGet` against path `/_liveness` on the `health` named port, with
    `initialDelaySeconds: 5, periodSeconds: 10, timeoutSeconds: 3, failureThreshold: 3`;
    `deploy/charts/buzz/templates/deployment.yaml` (lines 230-231) wires that value into
    the pod spec's `livenessProbe`.
  `launchpad/docs/corpus/architecture/containers/relay.md` (id `architecture-containers-relay`,
    status `draft`, already merged to origin/launchpad) already documents the relay's whole
    health surface — the four listeners, `build_health_router`, the readiness dependency
    checks, and the Helm probe wiring — as FACT evidence citing this same router.rs. It is
    the natural `references` target: this node explains the liveness *concept*, that node
    is the architectural container description the concept sits inside.
  Two sibling issues in this same #611 batch are open and unmerged: #1044 ("layers/compute/
    liveness.md" — a *different* concept, compute-instance/managed-agent liveness answered
    via relay presence, not this HTTP probe) and #1137 ("layers/observability/health-checks.md"
    — the general health-check umbrella concept this node is one instance of). #1143
    ("layers/observability/readiness.md") is also open and unmerged. None of their ids exist
    on `origin/launchpad`, so none can be a `relationships` target yet — confirmed by the
    same `git ls-tree` command above.
  `node.schema.json` requires id/type/status/origin/audiences/evidence, permits
    `relationships`, and `additionalProperties: false` rejects a `provenance` field — the
    revision goes in the `evidence` ledger as a commit-only FACT, per AGENTS.md's
    documented convention.
  `templates/concept.md` requires: Definition (mandatory, doubles as scope statement),
    Use cases (mandatory), Scope-and-omissions (mandatory, two-part: boundary/ownership
    and expected-but-unverified), with Background/Comparison/Related-resources/Visual-aid
    optional. It also mandates the reference-vs-procedure-vs-glossary-term boundary section.

STEP 1  Create the node file with schema-valid front matter and provenance   [independent]
        Create `launchpad/docs/corpus/layers/observability/liveness.md` with
        `id: layers-observability-liveness`, `type: layers`, `status: draft`,
        `origin: launchpad`, `audiences: [developer, operator, reviewer]`, and a single
        commit-only FACT recording revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5. Add
        one `relationships` entry: `references` → `architecture-containers-relay` (the
        merged node that already documents the concrete health surface this concept
        explains).
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0 with the new file on disk, and
                   `git cat-file -e 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5` exits 0.

STEP 2  Write Definition and Use cases from opened source              [needs 1]  ← RUNS HERE
        Write the Definition section: liveness is the process-level question "is this
        relay process itself alive and able to respond at all" (not "is it ready to serve
        traffic", not "is a compute substrate for an agent alive"), answered by
        `liveness_handler` returning an unconditional 200 with no dependency checks. Cite
        `crates/buzz-relay/src/router.rs` (line and symbol) as FACT for the handler body
        and its double registration. Write Use cases: why an orchestrator needs a
        liveness probe distinct from readiness — restart-on-hang vs. remove-from-service —
        grounded in the Helm chart's `livenessProbe` config and `initialDelaySeconds`/
        `periodSeconds`/`failureThreshold` semantics (FACT, citing `values.yaml` and
        `deployment.yaml`). One `evidence` entry per substantive claim, classified
        honestly.
        done when: validator exits 0; every claim in Definition and Use cases has a
                   matching `evidence` entry; `grep -n 'liveness_handler' launchpad/docs/corpus/layers/observability/liveness.md`
                   prints at least one line (the concept is grounded in the actual symbol,
                   not described from memory).

STEP 3  Write the boundary/non-goals section against #1044 and #1137        [needs 2]
        Write the boundary section explicitly separating this node from: (a) #1044's
        compute-instance liveness (a different question — is a managed agent's compute
        substrate alive, answered via relay presence — not this HTTP probe; state it is a
        sibling task, not yet merged, so no `relationships` edge exists to it); (b) #1137's
        health-checks umbrella (this node is one instance of that general concept, not a
        restatement of it); (c) readiness (#1143, separate probe with dependency checks,
        distinguish `liveness_handler` vs `readiness_handler` by what each actually
        executes, citing both). Record any discovered second concept as a candidate
        follow-up in the body's expected-but-unverified subsection rather than folding it
        in.
        done when: validator exits 0; the boundary section names #1044, #1137, and #1143
                   explicitly with why each is out of scope (checked by
                   `grep -cE '#(1044|1137|1143)' launchpad/docs/corpus/layers/observability/liveness.md`
                   printing at least 3).

STEP 4  Write scope-and-omissions and finish the evidence ledger            [needs 3]
        Write the required two-part scope-and-omissions section: what this node does not
        cover and who owns it (readiness, health-checks umbrella, compute liveness — with
        issue numbers), and separately what was expected to be verified and could not be
        (e.g. whether the CAKE-specific comment in router.rs names a system this corpus
        does not yet document; whether the Kubernetes deployment corpus node
        (`architecture-deployment-kubernetes`) needed its own relationship edge or is
        adequately covered via the relay node). Audit that FACT claims were opened, not
        assumed, and that INFERENCE claims carry `confidence`.
        done when: validator exits 0; the scope-and-omissions section is present and
                   two-part (checked by reading it against AGENTS.md step 8); no evidence
                   entry is FACT without an opened citation.

STEP 5  Full validation, corpus test suite, and self-review against the DoD  [needs 4]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` to exit 0, then run
        the corpus unit test suite as the sole command in its own call. Re-read the diff
        against issue #1138's Definition of Done checklist line by line. Confirm exactly
        one hand-authored document was created.
        done when: `cd <worktree> && python3 launchpad/project-intelligence/corpus/validate.py`
                   exits 0; `cd <worktree> && python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
                   reports OK; `git status --short` shows exactly one new corpus Markdown
                   file plus this plan file.

PARALLEL  None. All five steps edit the same single file (front matter created in STEP 1,
          body sections layered on in STEP 2-4, verification in STEP 5), and two steps
          touching one file are sequential per the skill's own rule regardless of how
          unrelated the sections look. There is no second artefact to fan out to — the
          issue's Definition of Done caps this task at exactly one hand-authored document.

GATES     `review-plan` on this plan before STEP 1 — self-run, therefore not independent,
          and the report must say so. `review-code` on the finished diff after STEP 5.
          `review-tests` does not apply: the diff adds one Markdown corpus node and one
          plan file, and touches no test file (STEP 5 *runs* the existing corpus suite but
          does not modify it). A mandatory cross-model final pass is out of scope for this
          single-worker batch task per the dispatch brief — integration-level review
          happens when the batch PR is assembled, not per-worker. `qa` explore mode does
          not apply: this change adds no runtime interface.

BUDGET    STEP 3, the boundary section against three concurrently-drafted siblings (#1044,
          #1137, #1143). Getting the liveness-vs-readiness distinction right requires
          reading both handler bodies side by side (done in ALREADY TRUE) and stating the
          difference precisely — "no dependency checks at all" vs. "checks shutdown flag
          plus Postgres/Redis/deletion-catalog" — rather than a vague "different purpose"
          gloss that would blur exactly the line #1138's scope note calls out.

OPEN      Whether `architecture-deployment-kubernetes` (which discusses readiness and
          migration-freshness at length but mentions liveness only via the shared
          three-port table) also deserves a `references` edge. Resolved here as **no** for
          this pass — the deeper, handler-level liveness detail lives in
          `architecture-containers-relay`, and a second edge there would be a citation
          duplicate rather than a substantive link; noted as a candidate follow-up if a
          later reviewer disagrees.

LEFT OUT  `relationships` edges to #1044, #1137, or #1143's node ids — none exist on
          `origin/launchpad` yet (all three issues are open, unmerged siblings in this
          same batch). The boundary is drawn in prose instead, per AGENTS.md step 9's
          explicit warning against linking to a branch-local, not-yet-merged id.

          Any change to `crates/buzz-relay/src/router.rs`, the Helm chart, or runtime
          probe behavior. This is a documentation-only task; the issue's out-of-scope list
          forbids runtime changes without a separately linked implementation issue.

          A second hand-authored corpus document of any kind, including filing #1044/#1137
          overlap as a new corpus task — any newly discovered second concept is reported in
          the final message as a candidate follow-up, not filed by this worker.

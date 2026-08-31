Issue #1137 — task: document layers/observability/health-checks.md
Stated size: no `Size` line on the issue; self-assessed as a single hand-authored document → cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1137-health-checks`, based on `origin/launchpad` HEAD ed133f4c5dbd546a67d963f11ffa630a4513b228,
    working tree clean. `launchpad/docs/corpus/schema/node.schema.json` and
    `launchpad/docs/corpus/AGENTS.md` are merged and authoritative; `type: layers` is a valid
    enum member. `launchpad/docs/corpus/layers/` does not exist at all yet on `origin/launchpad`
    (confirmed by directory listing) — this task's own document is the first `layers/` node to
    merge. Issue #1138 (`layers/observability/liveness.md`) and #1143
    (`layers/observability/readiness.md`) are both still OPEN with no merged content: #1138's PR
    (#1903) is itself still an open draft and documents **compute liveness** (agent-process
    presence, `layers/compute/liveness.md`, id `layers-compute-liveness`) — a different concept
    from the relay's own `/_liveness` HTTP probe — and its own body says #1138's scope for the
    relay probes "not yet drafted at this node's recorded revision." So there is no existing
    sibling content to avoid duplicating; this document states the probe-surface facts directly
    and flags the future deep-dive docs as where the internals belong.

STEP 1  [independent]  Gather evidence for the health-check surface: read
        `crates/buzz-relay/src/router.rs` (`build_router`'s three health routes at lines 68-70:
        `/health`, `/_liveness`, `/_readiness`; `build_health_router` at lines 291-301: the
        dedicated no-auth/no-CORS/no-metrics health-only router adding `/_status` and `/_mesh`;
        handler bodies `health_handler`, `liveness_handler`, `readiness_handler` at lines
        401-449), `crates/buzz-relay/src/main.rs` (the four-listener diagram and shutdown budget
        doc-comment at lines 1244-1287, `serve()`'s health-listener bind at lines 1296-1302, and
        the SIGTERM handler setting `shutting_down` at lines 1336-1343), `crates/buzz-relay/src/
        config.rs` (`BUZZ_HEALTH_PORT` default 8080, line ~818), `crates/buzz-relay/src/
        metrics.rs` (health-path exclusion from metrics cardinality, lines 155-179),
        `deploy/charts/buzz/values.yaml` (liveness/readiness/startup probe wiring at lines
        143-164, `service.healthPort: 8080` at line 238) and `deploy/charts/buzz/templates/
        deployment.yaml` + `service.yaml` (the `health` named container/service port). Cross-check
        already-merged sibling nodes `architecture-containers-relay` (already states the
        four-listener shape and the health-only router at a high level) and
        `architecture-deployment-kubernetes` (already flags that the readiness probe checks DB
        connectivity only, not schema freshness) for relationship targets and to avoid
        contradicting their existing claims.
        done when: every claim planned for the body has a specific opened source (path + line)
        recorded, and the liveness-vs-readiness behavioral difference (unconditional 200 vs.
        Postgres/Redis/deletion-catalog-checked with a 2s timeout) is confirmed from the handler
        bodies themselves, not inferred.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/layers/observability/health-checks.md`
        with schema-valid front matter (`id: layers-observability-health-checks`, `type: layers`,
        `status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`,
        an `evidence` ledger with a commit-provenance FACT plus one entry per substantive claim,
        and `relationships: [{type: references, target: architecture-containers-relay},
        {type: references, target: architecture-deployment-kubernetes}]` — both targets are
        merged on `origin/launchpad` today) and a body that is the **umbrella/overview** of the
        health-check surface: which endpoints exist (`/health`, `/_liveness`, `/_readiness` on
        the main app listener; `/_liveness`, `/_readiness`, `/_status`, `/_mesh` on the dedicated
        health-only listener), why two listeners carry overlapping routes, how each is wired
        into the Helm chart's liveness/readiness/startup probes, and how the endpoints relate to
        each other and to graceful shutdown (`shutting_down` flag flips `/_readiness` to 503
        before the drain begins; `/_liveness` never fails, which is why the startup probe also
        targets it). Explicitly scope out deep internals of any single probe's dependency checks
        as the future territory of #1138 (liveness) and #1143 (readiness), and note that no
        relationship edge is declared to either since neither exists as a mergeable node yet.
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and every
        issue-1137 DoD bullet plus the four category-tail bullets (one-sentence definition,
        stated boundaries/non-goals, links to related/implementation/verification nodes,
        examples that clarify rather than introduce a second concept) is addressed by a distinct
        section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against the issue's DoD checklist and the
        category tail; confirm every evidence entry supports its claim, no second canonical
        document was created (`git show --stat` shows only this document + this plan), the
        liveness/readiness split is stated accurately, and validate.py still passes.
        done when: the audit is written and validate.py exits 0 on the current tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole command
        in its own tool call, then commit the plan and the new document together (no push, no PR
        — this ships as part of one shared batch PR for all of #611's children per the batch
        owner's plan change).
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` reports OK and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file; steps are strictly sequential (evidence gathers before the
          body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
          `review-adjudicate` and the cross-model final review pass are deferred to the batch
          owner's later review of the shared PR — not run in this worktree.

BUDGET    STEP 2. The hard part is stating the two-listener, overlapping-route shape (main app
          router vs. dedicated health-only router) and the liveness/readiness behavioral split
          accurately as an overview, without drifting into either probe's dependency-check
          internals — that restraint is what keeps this an umbrella document rather than a
          duplicate of #1138/#1143's future deep dives.

OPEN      Whether `/_status` and `/_mesh` (present on the health-only listener but not wired to
          any Kubernetes probe in `values.yaml`) belong inside this node's scope at all, since
          they share a port but are not "health checks" in the probe sense. This document
          mentions them as sharing the health-only listener (accurate, sourced) but does not
          treat them as part of the health-*check* surface proper, and does not claim ownership
          of documenting their own behavior in depth — left genuinely open rather than silently
          folded in or silently omitted.

LEFT OUT  Any `relationships` edge to `layers-observability-liveness` (#1138) or
          `layers-observability-readiness` (#1143) — neither exists as a mergeable node on
          `origin/launchpad` yet (confirmed: no `layers/` directory present at all), so declaring
          either would be a hard validation error once this merges before them, and per
          `AGENTS.md`'s own worked warning, a target that resolves in one's own worktree but not
          on the branch being merged into is the exact trap to avoid. Any deep-dive content on
          the readiness probe's specific dependency checks (Postgres/Redis/deletion-catalog,
          2s timeout budget) or the liveness probe's unconditional-200 rationale beyond what is
          needed to explain *why* two different probe types exist — that belongs to #1143 and
          #1138 respectively. Any claim about `/_mesh` or `/_status` response payload internals —
          out of scope, not owned by this task. Editing `architecture-containers-relay` or
          `architecture-deployment-kubernetes` even though both already mention pieces of this
          surface — updating them is not this task's job.

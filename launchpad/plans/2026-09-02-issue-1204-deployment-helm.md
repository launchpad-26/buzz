Issue #1204 — task: document operations/deployment/helm.md
Stated size: no `Size` line  →  single hand-authored document, batch task under parent Feature #618, brief caps at cap: 5 steps.

ALREADY TRUE  (verified against git, not notes)
  On branch `task/1204-deployment-helm`, based on `origin/launchpad` HEAD 473205a7457b208455f188847bfb27b01aa83cac,
    working tree clean. `node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
    `launchpad/docs/corpus/templates/procedure.md` are merged and authoritative.
    `launchpad/docs/corpus/operations/` does not exist yet — this is the first node under that
    surface, and `launchpad/docs/corpus/operations/deployment/helm.md` does not exist.
    `deploy/charts/buzz` is a real Helm chart (Chart.yaml, values.yaml, values.schema.json,
    templates/, README.md, examples/, ci/, tests/) already present in this repository;
    `deploy/charts/buzz-push-gateway` is a sibling chart out of this task's scope.

STEP 1  [independent]  Gather evidence for the chart's install/upgrade/validation surface: read
        `deploy/charts/buzz/Chart.yaml` (dependencies, versioning), `README.md` (profiles,
        required inputs, S3 addressing, HA/Redis requirement, upgrades, backups, releasing),
        `values.yaml` (every top-level key group), `templates/_validate.tpl` (every hard-fail
        guard, in particular the exact three-way OR condition — `redis.enabled` /
        `externalRedis.url` / `secrets.existingSecret` — that gates the `replicaCount`/
        `autoscaling.minReplicas` > 1 Redis requirement, via the `buzz.minimumReplicas` helper
        in `templates/_helpers.tpl`), `templates/NOTES.txt`, `tests/validation_test.yaml` (the
        `helm-unittest` case `fails when replicaCount>1 without Redis` that exercises that exact
        guard), `tests/secrets_test.yaml`, `tests/fixtures/ha-values.yaml` and
        `production-existing-secret-values.yaml`, `ci/quickstart-values.yaml`,
        `examples/argocd-app.yaml`, `examples/flux-helmrelease.yaml`, `examples/secret-sample.yaml`,
        and `.github/workflows/helm-chart.yml` (lint/unittest/render-matrix job, the
        install-on-kind gated job, and the publish job's `helm package`/`helm push` and
        chart-v* tag/version-match logic — the closest this repository has to a canonical
        install/upgrade/rollback command set). Cross-check the already-merged
        `launchpad/docs/corpus/architecture/deployment/kubernetes.md` and
        `.../multi-relay.md` to confirm scope does not duplicate their architecture-level
        content and to identify legitimate `references` targets.
        done when: every claim planned for the body has a specific opened source (path, and
        symbol/section where applicable) recorded, and the exact Redis-validation condition is
        confirmed against both `_validate.tpl`'s logic and `validation_test.yaml`'s passing test
        case rather than restated from the sibling agent's summary.

STEP 2  [needs 1]  ← RUNS HERE  Write `launchpad/docs/corpus/operations/deployment/helm.md`
        against the `procedure.md` template's Required sections (Overview; Before you start;
        one numbered task sequence per logical goal — install, upgrade, rollback/uninstall,
        each as its own sequence since they are separate operator goals, not sub-steps of one
        task; See also; Boundary; Relationships; Scope and omissions), with schema-valid front
        matter (`id: operations-deployment-helm`, `type: operations`, `status: draft`,
        `origin: launchpad`, `audiences: [operator, developer]`, an `evidence` ledger with one
        commit-provenance FACT plus one entry per substantive claim including the template
        citation, `relationships: references` toward `architecture-deployment-kubernetes` for
        the K8s architecture background this procedure assumes, and toward
        `architecture-deployment-multi-relay` for the HA/Redis invariant this procedure's
        upgrade-to-HA step depends on — both confirmed present in `origin/launchpad`'s corpus
        tree). The body states the install/upgrade/rollback commands actually in this
        repository (`helm install`/`helm upgrade --install`/`helm rollback`/`helm uninstall`
        against the chart's local path or its published `oci://ghcr.io/block/buzz/charts/buzz`
        artifact), the required values (`relayUrl`, `ownerPubkey` conditionally, a Postgres/
        Redis/S3 source, `secrets.existingSecret` for GitOps), the chart's own hard-fail
        validation rules from `_validate.tpl` stated precisely (not as a blanket "replicaCount
        > 1 always fails" claim), and a boundary section drawing the line against Kubernetes
        cluster-side concerns (left to the sibling #1205 procedure, mentioned in prose without
        a link since that node does not exist on `origin/launchpad` yet).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0 and every
        issue-1204 DoD bullet plus the four procedure-template tail bullets (goal/prerequisites/
        scope; ordered executable steps; success verification and rollback/cleanup; links to
        authoritative commands/config) is addressed by a distinct section.

STEP 3  [needs 2]  Self-verify the diff line-by-line against issue #1204's DoD checklist and the
        procedure template's Required sections; confirm every evidence citation was actually
        opened and supports its statement, that the Redis/replicaCount claim matches
        `_validate.tpl` exactly (not the sibling agent's summary), that no second
        hand-authored canonical document was created, and that `validate.py` still passes.
        done when: the audit is written and `validate.py` exits 0 on the current tree.

STEP 4  [needs 3]  Earn the verification stamp with the corpus unittest suite as the sole
        command in its own tool call (no pipe, cwd already inside this worktree), then commit
        the plan and the new document together in a separate call.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
        reports `OK` and `git commit -s` succeeds without `--no-verify`.

PARALLEL  None — single new file, steps are strictly sequential (evidence gathers before the
          body cites it; the body must exist before it can be audited).

GATES     `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 before commit.
          `review-adjudicate` and the cross-model final review pass are deferred to the batch
          owner's later review — not run in this worktree.

BUDGET    STEP 2. The hard part is stating the Redis/`replicaCount` validation precisely (it is
          a three-way OR across `redis.enabled`, `externalRedis.url` and `secrets.existingSecret`,
          not an unconditional fail above one replica) and drawing the chart/Kubernetes boundary
          against the sibling #1205 procedure without linking a node that does not exist yet.

OPEN      Whether the reserved-but-unimplemented `migrate.preUpgradeJob.enabled` knob (README:
          "on the chart roadmap") belongs in this node's upgrade sequence at all — this document
          states it as a documented future capability, not as an executable step, since the
          chart does not implement it today.

LEFT OUT  Any relationship to a Kubernetes cluster-operations node (#1205) — not merged on
          `origin/launchpad` at this revision, so no `relationships[].target` can name it; the
          boundary is instead stated in prose per the dispatch brief. Any relationship to
          `architecture-deployment-docker-compose`, `-hosted-topology`, `-multi-community`, or
          `-single-relay` — read for scope-boundary confirmation but not load-bearing to this
          node's own claims, so not declared as edges. The `deploy/charts/buzz-push-gateway`
          chart and its own `helm-chart.yml` lint job — a separate chart, out of this task's
          named subject matter. Editing `launchpad/docs/corpus/AGENTS.md`, `node.schema.json`,
          or any existing merged corpus node.

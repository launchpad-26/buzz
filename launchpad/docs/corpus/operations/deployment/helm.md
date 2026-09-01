---
id: operations-deployment-helm
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - agent
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "deploy/charts/buzz is a Helm chart (apiVersion v2, name buzz, version 0.1.8, appVersion 0.1.0) that deploys a single relay binary serving WebSocket, REST and the web UI, backed by PostgreSQL, Redis and S3-compatible object storage; a separate sibling chart, deploy/charts/buzz-push-gateway, exists in this repository and is out of this node's scope."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/Chart.yaml"
      - "deploy/charts/buzz/README.md"
  - statement: "The chart declares two optional subchart dependencies, postgres and redis, both from oci://registry-1.docker.io/cloudpirates, each gated by its own postgresql.enabled / redis.enabled condition; Chart.lock pins them to postgres 0.19.5 and redis 0.30.3."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/Chart.yaml"
      - "deploy/charts/buzz/Chart.lock"
  - statement: "The chart has two operating profiles selected by values: production (default) uses external managed Postgres/Redis/S3 and secrets.existingSecret with no chart-side secret autogeneration, and is HA-capable at replicaCount >= 2; quickstart (eval) bundles in-cluster Postgres, Redis and MinIO subcharts/Deployments, autogenerates relay and service secrets via Helm's lookup pattern, and is intended for a single replica only."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The quickstart profile is opted into per-service (postgresql.enabled, redis.enabled, minio.enabled) rather than by the quickstart=true value alone, which is only an intent marker surfaced in NOTES.txt; ci/quickstart-values.yaml is the exact value set the chart's own CI installs against a kind cluster."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/ci/quickstart-values.yaml"
  - statement: "templates/_validate.tpl is included from every rendered template (via {{- include \"buzz.validate\" . -}} at the top of each) so its fail guards fire at helm install / helm upgrade / helm template time regardless of which manifest Helm renders first, before any resource is applied."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
      - "deploy/charts/buzz/templates/secret-chart.yaml"
      - "deploy/charts/buzz/templates/pvc-git.yaml"
  - statement: "_validate.tpl hard-fails with 'relayUrl is required' when .Values.relayUrl is empty; this is the one value the chart requires unconditionally."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
  - statement: "The Redis requirement is precisely conditional, not an unconditional fail above one replica: _validate.tpl computes buzz.minimumReplicas as autoscaling.minReplicas when autoscaling.enabled is true, else replicaCount, and fails only when that minimum exceeds 1 AND none of redis.enabled, externalRedis.url, or secrets.existingSecret is set -- providing any one of those three satisfies the guard, even without externalRedis.url itself, because secrets.existingSecret is trusted to carry a REDIS_URL key."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
      - "deploy/charts/buzz/templates/_helpers.tpl"
  - statement: "helm-unittest's own suite exercises this exact guard and confirms the verdict: setting replicaCount: 3 with externalPostgresql.url set but no redis.enabled, externalRedis.url, or secrets.existingSecret fails template rendering with the error 'minimum replica count 3 requires Redis for buzz-pubsub...'; the sibling ha-values.yaml fixture (replicaCount: 3, secrets.existingSecret: buzz-secrets, externalRedis.url set) is a case that renders because it satisfies the same guard."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/tests/validation_test.yaml"
      - "deploy/charts/buzz/tests/fixtures/ha-values.yaml"
  - statement: "_validate.tpl also hard-fails, independently of the Redis guard: ownerPubkey missing while relay.requireRelayMembership is true (the default); ownerPubkey present but not exactly 64 lowercase hex characters; pairingRelay.enabled true with pairingRelay.url empty; ingress.enabled and httproute.enabled both true; no Postgres source configured (none of postgresql.enabled, externalPostgresql.url, secrets.existingSecret); no S3/object-storage source configured (none of minio.enabled, s3.endpoint, secrets.existingSecret); and, when autoscaling.enabled, minReplicas < 1, maxReplicas < minReplicas, or websocketMetricEnabled true with websocketMetricName empty."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/_validate.tpl"
  - statement: "values.schema.json additionally rejects an s3.addressingStyle other than path or virtual at template-render time, independent of the _validate.tpl guards, per helm-unittest's own 'rejects an invalid S3 addressing style' case."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.schema.json"
      - "deploy/charts/buzz/tests/validation_test.yaml"
  - statement: "The README's quickstart install command installs the chart from its published OCI artifact, oci://ghcr.io/block/buzz/charts/buzz, pinned to a --version, with --set flags for quickstart=true, postgresql.enabled=true, redis.enabled=true, minio.enabled=true, relayUrl, and ownerPubkey; this brings up every bundled dependency in-cluster with no external services required."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "For production/GitOps installs the chart is designed for ArgoCD (examples/argocd-app.yaml, a native-OCI-source Application with repoURL set to the full chart artifact path and path: \".\") and Flux (examples/flux-helmrelease.yaml, a HelmRepository of type oci plus a HelmRelease), both of which set secrets.existingSecret and both of which the README states must avoid chart-side secret autogeneration because helm template (what ArgoCD/Flux render with) makes Helm's lookup function return empty."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/examples/argocd-app.yaml"
      - "deploy/charts/buzz/examples/flux-helmrelease.yaml"
      - "deploy/charts/buzz/README.md"
  - statement: "templates/secret-chart.yaml renders the chart-managed Secret only when secrets.existingSecret is empty, reads any existing values via a Helm lookup against the same Secret name so a value already present is preserved across upgrades rather than rotated, and generates the rest with randAlphaNum / sha256sum -- exactly the behavior the README and NOTES.txt warn is unsafe under GitOps tools that render with helm template, since lookup returns empty there and every sync would mint fresh random secrets."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/secret-chart.yaml"
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/templates/NOTES.txt"
  - statement: "The chart-managed Secret carries the annotation helm.sh/resource-policy: keep, so Helm leaves it in place on helm uninstall rather than deleting it with the rest of the release's resources."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/secret-chart.yaml"
  - statement: "The git-scratch PersistentVolumeClaim (templates/pvc-git.yaml, created when persistence.git.enabled is true and no existingClaim is given) carries no resource-policy annotation by default -- only whatever the operator supplies via persistence.git.annotations -- so it is deleted along with the rest of the release on helm uninstall unless the operator adds that annotation themselves."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/pvc-git.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The chart's own README and NOTES.txt are inconsistent about the git PVC's data-loss risk: the 'Backups -- save these' list in both documents names the Git PVC as item 4, 'repo on-disk state ... losing any of them is data loss', while the same README's HA section and the persistence.git values.yaml comment both state that git ref/object state is object-store-backed, each request hydrates an ephemeral repo from S3-compatible storage, and 'no persistent git state lives here' -- this node states both passages as found and does not resolve the contradiction."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/templates/NOTES.txt"
      - "deploy/charts/buzz/values.yaml"
  - statement: "Schema migrations are embedded in the relay binary (sqlx::migrate!) and run automatically at pod startup, gated by BUZZ_AUTO_MIGRATE which defaults to true and is race-safe across multiple replicas behind a Postgres advisory lock; the README states 'helm upgrade is the entire upgrade procedure' under this default."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/values.yaml"
  - statement: "40 forward-only, sequentially numbered .sql files exist under migrations/ at the recorded revision (0001_initial_schema.sql through 0040_push_message_kinds.sql), and no file or naming convention for a down/reverse migration was found there."
    entry_class: FACT
    evidence:
      - "list_migrations(migrations/*.sql) -> 40 files, 0001_initial_schema.sql..0040_push_message_kinds.sql; list_migrations(migrations/, grep -i down) -> no matches, exit 1, at commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-admin's CLI defines a Migrate subcommand (crates/buzz-admin/src/main.rs), which the README names as the command an operator runs against the database before every helm install / helm upgrade when migrate.autoMigrate is set to false; in that mode the chart does not run migrations itself, readiness probes verify only DB connectivity and not schema freshness, and the values knob migrate.preUpgradeJob.enabled is reserved but not yet implemented by any chart template ('on the chart roadmap' per the README)."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs"
      - "deploy/charts/buzz/README.md"
      - "deploy/charts/buzz/values.yaml"
  - statement: "No occurrence of the word 'rollback' was found in deploy/charts/buzz/README.md, RELEASING.md, CONTRIBUTING.md, ARCHITECTURE.md, or TESTING.md at the recorded revision; the chart defines no rollback-specific template, job, or documented procedure of its own."
    entry_class: FACT
    evidence:
      - "grep_rollback(deploy/charts/buzz/README.md, RELEASING.md, CONTRIBUTING.md, ARCHITECTURE.md, TESTING.md) -> no matches, exit 1, at commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "Because schema migrations run forward-only and automatically at every pod start with no down-migration mechanism found in this repository, a `helm rollback` to a chart/image revision that predates a since-applied migration reverts the Deployment's Pod template but not the database schema those older Pods expect -- the older relay code then runs against a newer schema, which this repository's own migration story gives no rollback path out of."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz/README.md"
      - "migrations/0001_initial_schema.sql"
    confidence: 0.75
  - statement: "The chart's CI (.github/workflows/helm-chart.yml) runs ct lint, helm unittest deploy/charts/buzz, and a helm template render of every ci/*-values.yaml and tests/fixtures/*-values.yaml fixture on every pull request and push to main; a separate install-on-kind job runs ct install --config ct.yaml --charts deploy/charts/buzz against a real kind cluster, gated to workflow_dispatch only; only a chart-v* tag push (or a version-carrying workflow_dispatch) runs the publish job, which builds dependencies, runs helm package, and pushes the artifact with helm push to oci://ghcr.io/block/buzz/charts, failing loudly if the tag version and Chart.yaml's version disagree."
    entry_class: FACT
    evidence:
      - ".github/workflows/helm-chart.yml"
      - "ct.yaml"
  - statement: "The README's own Development section gives the equivalent commands for a contributor to run locally: rendering every ci/tests fixture with helm template, running helm unittest . after installing the helm-unittest plugin, and running ct lint --config ../../../ct.yaml --charts . after helm dependency build ."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md"
  - statement: "The already-merged corpus node architecture-deployment-kubernetes documents this same chart's Pod/Service/Ingress/HTTPRoute/pairing-relay topology, trust boundary, and data-store mapping as Kubernetes architecture; this node does not restate that content and instead covers the chart's own operator-facing install/upgrade/rollback lifecycle and validation rules."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/kubernetes.md"
  - statement: "The already-merged corpus node architecture-deployment-multi-relay documents the same replicaCount/Redis invariant this node's validation section states, from the architecture side rather than the operator-procedure side."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/deployment/multi-relay.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped corpus node to carry an Overview, an optional Before you start, one numbered task sequence per logical goal, a See also section, an explicit Boundary statement, Relationships, and a Scope and omissions section."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-deployment-multi-relay
---

# Installing and upgrading Buzz with its Helm chart

How to install, upgrade, and roll back or uninstall a Buzz relay release using the
chart at `deploy/charts/buzz` -- which values it requires, what it validates at
render time before anything is applied, and what its backup/rollback story actually
covers today.

## Before you start

- A Helm 3 client and `kubectl` access to the target namespace.
- A decision between the two supported profiles: **quickstart** (bundles Postgres,
  Redis and MinIO in-cluster, autogenerates secrets, single replica, eval only) or
  **production** (external Postgres/Redis/S3, `secrets.existingSecret`, HA-capable).
  See *Boundary* for what each profile assumes you already have.
- For quickstart: registry access to pull the `postgres` and `redis` subcharts from
  `oci://registry-1.docker.io/cloudpirates` (`Chart.lock` pins `postgres 0.19.5`,
  `redis 0.30.3`).
- For production: a pre-created Kubernetes `Secret` matching the schema in
  `deploy/charts/buzz/examples/secret-sample.yaml`, and external Postgres/Redis/S3
  endpoints (or their URLs recorded in that Secret).
- The public `wss://` URL clients will use (`relayUrl`), and, unless you are running
  an intentionally open relay (`relay.requireRelayMembership=false`), the relay
  operator's 64-character lowercase hex Nostr pubkey (`ownerPubkey`).

## Install (quickstart / evaluation profile)

1. Confirm you do not need GitOps or HA for this install -- quickstart autogenerates
   secrets via Helm's `lookup` pattern, which is not safe under `helm template`
   (see *Boundary*).
2. Run:

   ```sh
   helm install buzz oci://ghcr.io/block/buzz/charts/buzz --version 0.1.8 \
     --create-namespace --namespace buzz \
     --set quickstart=true \
     --set postgresql.enabled=true \
     --set redis.enabled=true \
     --set minio.enabled=true \
     --set relayUrl=wss://buzz.example.com \
     --set ownerPubkey=<64-char-hex-pubkey>
   ```

   Enabling the three `*.enabled` flags is what actually brings up in-cluster
   Postgres, Redis and MinIO; `quickstart=true` alone is only an intent marker
   surfaced in `NOTES.txt`.
3. Read the printed `NOTES.txt` output. It states the effective profile, the
   backups you now own (see *Boundary*), and any degradation warnings (for example
   `relay.requireAuthToken=false` or an open relay).
4. Verify success: `kubectl -n buzz port-forward svc/<release>-buzz 8080:8080` then
   `curl http://localhost:8080/_readiness` (both commands are printed in `NOTES.txt`
   for your actual release name and health port).

## Install (production / GitOps profile)

1. Create the Secret named by `secrets.existingSecret` (schema in
   `examples/secret-sample.yaml`) via SealedSecrets, SOPS, External Secrets, or
   Vault -- anything that keeps the unencrypted form out of git.
2. Choose ArgoCD or Flux and adapt the matching example manifest
   (`examples/argocd-app.yaml` or `examples/flux-helmrelease.yaml`) with your
   `relayUrl`, `ownerPubkey`, `replicaCount`, external Postgres/Redis/S3 values (or
   leave them blank and rely on the Secret), and ingress configuration.
3. Apply the ArgoCD `Application` or Flux `HelmRelease` manifest through your
   platform's normal GitOps flow (`kubectl apply -f`, or a Git push the
   controller reconciles).
4. Verify success the same way as quickstart: port-forward the Service and curl
   `/_readiness`, or check your GitOps controller's own sync/health status for the
   release.

## Upgrade

1. Update the chart version or your values (image tag/digest, replica count,
   feature flags) in whichever install path you used above -- a `helm upgrade`
   invocation, or a new commit for GitOps.
2. Run the upgrade:

   ```sh
   helm upgrade --install buzz oci://ghcr.io/block/buzz/charts/buzz \
     --version <new-version> --namespace buzz -f <your-values.yaml>
   ```

   or let your GitOps controller reconcile the updated manifest.
3. By default (`migrate.autoMigrate=true`), no separate migration step is needed:
   each relay pod runs `sqlx::migrate!` at startup behind a Postgres advisory lock,
   so `helm upgrade` is the entire upgrade procedure.
4. If you have set `migrate.autoMigrate=false`, run `buzz-admin migrate` (as a
   one-shot Job or separate Pod) against the database **before** this `helm
   upgrade`. The chart does not do this for you in that mode, and readiness
   probes check only DB connectivity, not schema freshness -- a pod can appear
   healthy against an unmigrated schema and then fail under load.
5. Verify success: watch `kubectl -n buzz rollout status deployment/<release>-buzz`
   to completion, then re-check `/_readiness`.

## Roll back or uninstall

1. Decide what you actually need: reverting the Deployment's Pod template
   (`helm rollback`) versus removing the release entirely (`helm uninstall`).
2. To revert to a prior release revision: `helm rollback <release> <revision> -n
   <namespace>`. **Caution:** this repository has no down-migration mechanism (40
   forward-only files under `migrations/`, `sqlx::migrate!` applies them forward
   only) and no rollback-specific chart logic was found. Rolling back past a
   revision that already applied a schema migration runs older relay code against
   a newer schema -- there is no chart- or repository-provided path back from that.
3. To remove the release: `helm uninstall <release> -n <namespace>`. The
   chart-managed Secret (when `secrets.existingSecret` is unset) carries
   `helm.sh/resource-policy: keep` and survives uninstall; the git-scratch PVC
   (`persistence.git.enabled: true`) carries no such annotation by default and is
   deleted with the rest of the release unless you added one yourself via
   `persistence.git.annotations`.
4. Before either action, save what the chart's own `NOTES.txt` calls out as
   backups (see *Boundary* for the one item this node found under dispute):
   `BUZZ_RELAY_PRIVATE_KEY` (rotating it changes the relay's federation identity),
   the PostgreSQL database, the S3 media bucket, and the owner private key held
   by the operator (not the chart -- restored by reinstalling with the same
   `ownerPubkey`).

## See also

- Kubernetes-side cluster concerns (namespaces, node pools, ingress controllers,
  cluster networking, and the rest of what runs *around* this chart's resources)
  are a neighboring operations concern this node does not cover -- see *Boundary*.
- The corpus's Kubernetes architecture node documents this chart's Pod/Service/
  Ingress/HTTPRoute/pairing-relay topology and trust boundary in more depth than
  this procedure repeats.
- The corpus's multi-relay architecture node documents the same Redis/`replicaCount`
  invariant this node's validation section states, from the architecture side.

## Boundary

This node does not describe:

- **Kubernetes cluster-side operations** -- provisioning a cluster, node pools,
  cluster networking/CNI, cluster-level ingress controller installation, or
  cluster upgrades. Those are a distinct operational surface from installing and
  upgrading *this chart's release* on top of an already-running cluster, and are
  not covered by any node merged on `origin/launchpad` as of this writing.
- **How the chart's Kubernetes resources are structured or how they trust each
  other** -- Pod topology, container ports, ServiceAccount and security context,
  and the auth/trust boundary are architecture, not procedure; see
  `architecture-deployment-kubernetes`.
- **Why this design exists** -- for example, why git state is object-store-backed
  rather than shared-filesystem-backed. See the same architecture node and
  `docs/git-on-object-storage.md` (referenced from the chart's own README) for
  that discussion; this node only states the operational consequence (no
  ReadWriteMany volume is required for HA).
- **A general Helm/Kubernetes tutorial.** This procedure assumes the reader
  already knows how to run `helm` and `kubectl` against a cluster they have
  access to.
- **The chart-managed Secret's exact key list, or the sibling
  `buzz-push-gateway` chart** -- see `examples/secret-sample.yaml` for the
  former; the latter is a separate chart in this repository, out of this node's
  named subject matter.
- **A resolved answer to whether the git PVC is safe to lose.** The chart's own
  README and NOTES.txt list it under "Backups -- save these... losing any of them
  is data loss," while the same README's HA section and the `persistence.git`
  values comment both describe it as ephemeral, object-store-backed scratch space
  with no persistent git state. This node states the discrepancy as found; it
  does not decide which passage is stale.

## Relationships

- `references`: `architecture-deployment-kubernetes` -- the cluster-topology and
  trust-boundary background this procedure assumes but does not restate.
- `references`: `architecture-deployment-multi-relay` -- the HA/Redis invariant
  this procedure's upgrade-to-multiple-replicas path depends on, stated there
  from the architecture side.

## Scope and omissions

**This node covers** installing the chart under both its quickstart and
production/GitOps profiles, upgrading a release (including the automatic- versus
manual-migration paths), rolling back or uninstalling a release and what the
chart's own annotations do and do not preserve when you do, and the chart's
render-time validation rules stated precisely rather than as a blanket
`replicaCount > 1` prohibition.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Kubernetes cluster-side provisioning and operation (node pools, cluster networking, cluster-level ingress) | No corpus node merged on `origin/launchpad` as of this writing; tracked as issue #1205 in this repository's issue tracker, not yet a merged node this document can link |
| The chart's Kubernetes resource topology, trust boundary, and data-store mapping | `architecture-deployment-kubernetes` |
| The Redis/`replicaCount` HA invariant, from the architecture side | `architecture-deployment-multi-relay` |
| The `buzz-push-gateway` sibling chart | Not this node's subject matter |
| Relay-proxied GIF search (`BUZZ_KLIPY_API_KEY`) and the git-on-object-storage design | `docs/gif-search.md` and `docs/git-on-object-storage.md`, referenced from the chart's own README |

**Expected but not verified when this node was written:**

- **No `helm install`, `helm upgrade`, or `helm rollback` was actually executed
  against a live cluster while writing this node.** `helm` is not installed in
  this authoring environment; every command above is transcribed from the
  chart's own README, examples, and CI workflow rather than exercised directly,
  which is weaker than the procedure template's own guidance to test a how-to
  "from start to finish." The chart's CI (`.github/workflows/helm-chart.yml`)
  does exercise `helm template` against every fixture and, on a gated
  `workflow_dispatch`, a real `ct install` against a kind cluster -- that is the
  closest verification this repository provides today.
- **Whether the git PVC's Backups-list entry or its ephemeral-scratch-space
  description is the stale one** was not resolved -- see *Boundary*.
- **The `migrate.preUpgradeJob.enabled` values knob's eventual behavior**, since
  the chart does not implement it yet; this node describes it only as a
  documented, reserved, not-yet-built feature.

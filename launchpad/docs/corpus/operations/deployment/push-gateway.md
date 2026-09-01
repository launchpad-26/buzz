---
id: operations-deployment-push-gateway
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-push-gateway is built as its own binary from Dockerfile.push-gateway, a multi-stage build that compiles only the buzz-push-gateway binary target and produces a slim runtime image exposing ports 8080 and 8081, deliberately separate from the relay image."
    entry_class: FACT
    evidence:
      - "Dockerfile.push-gateway"
  - statement: "At startup the gateway requires DATABASE_URL, BUZZ_PUSH_PUBLIC_DELIVERY_URL, BUZZ_PUSH_MAX_GRANT_LIFETIME_SECONDS, BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH, BUZZ_PUSH_GRANT_KEYS, BUZZ_PUSH_TOKEN_KEYS, and a dogfood application profile (BUZZ_PUSH_DOGFOOD_APP_ATTEST_APP_ID, BUZZ_PUSH_DOGFOOD_APNS_TOPIC, BUZZ_PUSH_DOGFOOD_APNS_CERT_PATH), refusing to start if any is missing, malformed, or if a grant key and a token key share an id or key material; BUZZ_PUSH_MAX_INSTALLATION_LIFETIME_SECONDS, BUZZ_PUSH_DOGFOOD_APNS_ENVIRONMENT, BUZZ_PUSH_BIND_ADDR, BUZZ_PUSH_HEALTH_ADDR, and the two endpoint-quota variables are optional with stated defaults."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The gateway owns a scoped migration (crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql) that creates exactly six tables: push_gateway_challenges, push_gateway_installations, push_gateway_delegations, push_gateway_endpoint_quotas, push_gateway_delivery_auth_replays, and push_gateway_delivery_request_replays."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
  - statement: "The gateway's Helm chart (deploy/charts/buzz-push-gateway) is a distinct chart from the main buzz chart, with its own Chart.yaml, a Deployment, a pre-install/pre-upgrade migration Job, a Service, an optional HTTPRoute, a PodDisruptionBudget, NetworkPolicies, and opt-in PodMonitor/PrometheusRule templates."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
      - "deploy/charts/buzz-push-gateway/templates/deployment.yaml"
      - "deploy/charts/buzz-push-gateway/templates/migration-job.yaml"
      - "deploy/charts/buzz-push-gateway/templates/service.yaml"
      - "deploy/charts/buzz-push-gateway/templates/httproute.yaml"
      - "deploy/charts/buzz-push-gateway/templates/pdb.yaml"
      - "deploy/charts/buzz-push-gateway/templates/networkpolicy.yaml"
      - "deploy/charts/buzz-push-gateway/templates/podmonitor.yaml"
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
  - statement: "The chart's default values.yaml sets replicaCount 2, image.repository ghcr.io/block/buzz-push-gateway with tag main, existingSecret buzz-push-gateway for runtime credentials, migration.existingSecret buzz-push-gateway-migrations with migration.runtimeDatabaseRole defaulting to buzz_push_gateway_runtime, httpRoute.enabled false, and podMonitor/prometheusRule/networkPolicy.monitoring all disabled by default so a default install exposes no scrape surface and no externally attached route."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/values.yaml"
  - statement: "The checked-in deploy/charts/buzz-push-gateway/values-production.yaml deliberately leaves image.tag, image.digest, and profiles.dogfood.appAttestAppId empty while enabling httpRoute for host push.buzz.xyz, so this file cannot render a working deployment on its own and a production renderer must inject the missing environment-owned values."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/values-production.yaml"
  - statement: "The chart's migration Job runs the gateway binary with --migrate-only, sources DATABASE_URL and BUZZ_PUSH_RUNTIME_DATABASE_ROLE from migration.existingSecret/migration.runtimeDatabaseRole, and carries Helm hook annotations helm.sh/hook: pre-install,pre-upgrade with hook-weight -5, so Helm runs and waits on this Job before touching the Deployment on every install or upgrade."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/migration-job.yaml"
  - statement: "The Deployment template wires BUZZ_PUSH_BIND_ADDR/BUZZ_PUSH_HEALTH_ADDR/BUZZ_PUSH_PUBLIC_DELIVERY_URL/BUZZ_PUSH_MAX_GRANT_LIFETIME_SECONDS/BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH/the dogfood-profile variables as plain values, and DATABASE_URL/BUZZ_PUSH_GRANT_KEYS/BUZZ_PUSH_TOKEN_KEYS from existingSecret via secretKeyRef; it mounts the App Attest root and the dogfood APNs certificate as read-only Secret volumes, sets a RollingUpdate strategy with maxSurge 1 and maxUnavailable 0, and defines livenessProbe/readinessProbe/startupProbe all as HTTP GETs against the health port's /_liveness or /_readiness paths."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/deployment.yaml"
  - statement: "deploy/charts/buzz-push-gateway/tests/render.sh runs helm lint and helm template against both the chart's defaults and a values-production.yaml override set with real digest/appAttestAppId/parentRefs/postgresEgressCidrs placeholders substituted, asserts a series of structural invariants (Service/Deployment/Job label selectors, the migration Job's pre-install/pre-upgrade hook and --migrate-only args, the default render exposing no PodMonitor/PrometheusRule and no pod ingress on port 8081, an HTTPRoute only appearing under the production override), and separately asserts that helm template against the checked-in values-production.yaml with no overrides fails -- proving that file is intentionally undeployable until CI or an operator injects the missing values."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/tests/render.sh"
  - statement: "This repository's .github/workflows/docker.yml gates both the push-gateway-build and push-gateway-merge (publish) jobs with if: github.repository == 'block/buzz', with an inline comment stating 'Launchpad does not operate the separate APNs gateway. Preserve the inherited lane for upstream while preventing fork publication attempts' -- so this fork (launchpad-26/buzz) never builds or publishes a buzz-push-gateway image through its own CI, regardless of what changes on this branch."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "docs/push-gateway-deployment.md documents verifying a published image's digest before deploying it with `gh attestation verify oci://ghcr.io/block/buzz-push-gateway@sha256:<64-lowercase-hex> --owner block`, then setting that verified digest as the chart's image.digest value so the rendered manifest uses an immutable, attested reference rather than the mutable main tag."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: ".github/workflows/push-gateway-helm-chart.yml runs a validate job (deploy/charts/buzz-push-gateway/tests/render.sh and tests/release-contract.sh) on every pull request touching the chart or the workflow, and a separate publish job -- triggered by a push-chart-v<version> tag or manual dispatch, and carrying no github.repository-scoped gate -- that verifies the tag matches the chart's declared version before packaging and pushing it to oci://ghcr.io/block/buzz/charts."
    entry_class: FACT
    evidence:
      - ".github/workflows/push-gateway-helm-chart.yml"
  - statement: "docs/push-gateway-deployment.md documents the chart release mechanics: bump both version and appVersion in deploy/charts/buzz-push-gateway/Chart.yaml, run tests/render.sh, open a same-repository PR from a branch named exactly push-chart-release/X.Y.Z, and once that PR merges .github/workflows/auto-tag-on-release-pr-merge.yml creates tag push-chart-vX.Y.Z and dispatches the publish workflow against it; a manually pushed push-chart-vX.Y.Z tag is the documented rescue path."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "docs/push-gateway-deployment.md documents the PostgreSQL role split the migration Job enforces: the migration role is DDL-capable and, after running scoped migrations, revokes database CREATE from itself and schema CREATE from both PUBLIC and the runtime role, leaving the runtime role (default buzz_push_gateway_runtime) with only CONNECT/USAGE plus SELECT/INSERT/UPDATE/DELETE on the six gateway tables; it also states that all replicas must share one PostgreSQL database because delivery authority, replay admission, and endpoint-quota reservation are transactional there."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "docs/push-gateway-deployment.md documents that a background reaper sweeps expired challenges, replay rows, idle quota rows, expired/revoked delegations, and retention-eligible installations (including their encrypted token ciphertext) at startup and every five minutes, and that rollback does not require deleting credentials or mutating existing leases: setting BUZZ_PUSH_ENABLED=false on the enabled relays stops advertisement, lease acceptance, matching, and new gateway traffic first, and only after that should the gateway deployment itself be disabled if it is unhealthy, after which existing leases and gateway authorities expire naturally via the reaper."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "docs/push-gateway-deployment.md documents that AEAD/APNs certificate rotation requires an explicit rolling restart after a secret-manager update (Kubernetes does not restart pods when referenced Secret bytes change), for example `kubectl rollout restart deployment/<release>-buzz-push-gateway`, followed by readiness verification before removing predecessor keys, and that the sole accepted Apple App Attest root artifact is pinned by both a certificate SHA-256 fingerprint and an exact PEM-file SHA-256, with startup rejecting any byte mismatch."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "The relay side of this integration is a separate, explicit deployment opt-in: .env.example ships BUZZ_PUSH_ENABLED=false by default and a commented-out BUZZ_PUSH_GATEWAY_DELIVERY_URL, with a comment stating that when enabled and the URL is absent, the canonical https://push.buzz.xyz/v1/deliveries/apns endpoint is used."
    entry_class: FACT
    evidence:
      - ".env.example"
  - statement: "Justfile's unit-test job runs `cargo nextest run -p buzz-push-gateway` alongside a comment that gateway unit and black-box HTTP tests are infra-free, while Postgres-backed contract/race tests run in a dedicated CI job, so a gateway code or configuration change can be exercised locally with this one command before any deployment step."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "No file under this repository's launchpad/ tree (searched for push-gateway, buzz-push-gateway, and push_gateway across *.tf, *.yaml, and *.yml, and separately for any file named like Terraform or ArgoCD material) provisions, deploys, or references a live push-gateway instance, and no launchpad-scoped push-gateway deployment manifest, Terraform stack, or ArgoCD application was found anywhere in the repository."
    entry_class: FACT
    evidence:
      - "grep_recursive('push-gateway|buzz-push-gateway|push_gateway', paths='launchpad/', includes='*.tf,*.yaml,*.yml') -> matches only under launchpad/docs/corpus and launchpad/plans; find(launchpad, iname='*terraform*' or iname='*argocd*') -> no results"
  - statement: "Given the chart's declared inputs (image.repository/tag/digest, existingSecret, migration.existingSecret, publicDeliveryUrl, profiles.dogfood, appAttestRoot, resources, networkPolicy, httpRoute) and Helm's own hook-ordering semantics for pre-install/pre-upgrade Jobs, the applicable operator command to install or upgrade a release is a standard `helm upgrade --install <release> deploy/charts/buzz-push-gateway -f deploy/charts/buzz-push-gateway/values-production.yaml -f <environment-overrides.yaml>` invocation; no literal command of this shape is written anywhere in this repository, so this is reasoned from the chart's structure rather than read from a documented example."
    entry_class: INFERENCE
    evidence:
      - "deploy/charts/buzz-push-gateway/values.yaml"
      - "deploy/charts/buzz-push-gateway/values-production.yaml"
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
    confidence: 0.75
  - statement: "This fork (launchpad-26/buzz) operates deployment, CI/CD, documentation and cohort process for Buzz rather than developing Buzz's Rust crates or React features, per this repository's own fork-scope notice."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "CLAUDE.md (this repository's fork-scope notice, 'This checkout is the launchpad-26 fork')"
  - statement: "Issue #1225 ('task: document operations/runbooks/push-delivery-failure.md') is the sibling task that owns incident-response procedure for a push notification failing to deliver, and is out of scope for this deployment/configuration node."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1225 title, read via gh issue view"
  - statement: "Issue #1207's dispatch brief instructs that if the gateway is external or not-yet-implemented in this repository, this node should say so plainly with the searches that establish it, and should not invent a deployment this repository does not support."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1207 dispatch brief"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped operations node to carry an Overview, an optional Before you start, one or more numbered task sequences, a See also section, a Boundary statement, a Relationships section, and a Scope and omissions section distinguishing what the node does not cover from what was expected but could not be verified."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
---

# Push gateway deployment: how-to

How an operator builds, configures, deploys or upgrades, verifies, and rolls
back `buzz-push-gateway` — the standalone service that holds Apple Push
Notification service (APNs) credentials for Buzz — using this repository's
own Dockerfile, Helm chart, and configuration surface. Perform this
procedure when standing up a new gateway environment, rolling out a chart or
image change, rotating a credential that requires a restart, or disabling
push delivery.

This node names, but does not restate, two architecture nodes covering the
same subject from a different angle: a container-level description of the
gateway's responsibility, interfaces, and trust boundaries, and a flow-level
description of the end-to-end push-notification delivery path. See *See
also* below.

## Before you start

- A dedicated PostgreSQL database for the gateway, separate from the relay's
  database — the gateway's migration history and the relay's must not share
  a database.
- Two Kubernetes Secrets prepared out of band: a runtime secret (chart
  default name `buzz-push-gateway`) holding `DATABASE_URL` (DML-only
  role), `BUZZ_PUSH_GRANT_KEYS`, `BUZZ_PUSH_TOKEN_KEYS`, the Apple App
  Attest root certificate PEM, and the dogfood APNs identity certificate
  PEM; and a migration secret (chart default name
  `buzz-push-gateway-migrations`) holding a DDL-capable `DATABASE_URL`.
- The Apple App Attest root certificate (pinned by fingerprint), a
  server-owned APNs topic and certificate identity, and the exact
  Apple `TEAMID.bundle-id` for the profile being deployed — none of these
  can be supplied by a client or a relay.
- Helm 3.16 or newer, and (only if verifying an upstream-published image
  digest) the `gh` CLI authenticated against GitHub.
- Awareness that this fork's own CI does not build or publish a
  `buzz-push-gateway` image or chart from `block/buzz`'s gated lanes — see
  *Boundary* below before assuming a fresh image or chart version is already
  available.

## Deploy or upgrade the gateway

1. Obtain an image to deploy. If deploying an image `block/buzz`'s own CI
   published, verify its digest before use:
   `gh attestation verify oci://ghcr.io/block/buzz-push-gateway@sha256:<digest> --owner block`.
   This fork's `push-gateway-build`/`push-gateway-merge` jobs in
   `.github/workflows/docker.yml` do not run here, so this repository's own
   CI does not produce that image; building `Dockerfile.push-gateway`
   directly is the alternative when no attested upstream image applies.
2. Provision the runtime and migration Secrets described in *Before you
   start*, named to match `existingSecret` and `migration.existingSecret` in
   `deploy/charts/buzz-push-gateway/values.yaml` (or override those value
   paths to match secrets you have already created).
3. Prepare a values override supplying every field
   `deploy/charts/buzz-push-gateway/values-production.yaml` leaves empty
   for a production render: `image.digest` (the verified digest from step
   1), `profiles.dogfood.appAttestAppId`, `httpRoute.parentRefs` (if
   attaching to a Gateway API `Gateway`), and
   `networkPolicy.postgresEgressCidrs` (narrowed to the actual database
   network — the shipped example range is illustrative only).
4. Validate the render before installing:
   `deploy/charts/buzz-push-gateway/tests/render.sh` lints and renders both
   the chart's defaults and a production-shaped override, and separately
   confirms the checked-in `values-production.yaml` alone still fails to
   render — a passing run on your own override file is the signal that the
   required fields are actually supplied.
5. Install or upgrade the release with your prepared values file(s) layered
   over `values-production.yaml`. Helm runs the chart's pre-install/
   pre-upgrade migration Job (`--migrate-only`, sourced from
   `migration.existingSecret`) and waits for it to succeed before touching
   the `Deployment`, so scoped migrations always run ahead of new replicas.
6. Confirm the migration Job completed and that the runtime role it left
   behind carries no elevated grant — the documented contract is
   `CONNECT`/`USAGE` plus `SELECT, INSERT, UPDATE, DELETE` on the six
   `push_gateway_*` tables only, with database and schema `CREATE` revoked.
7. Confirm rollout health: both `_liveness` and `_readiness` on the private
   health port must be passing (the `Deployment`'s liveness/readiness/
   startup probes already gate this), replica count is at least 2 sharing
   the one database, and the `PodDisruptionBudget` is satisfied.
8. If `httpRoute.enabled=true`, confirm the rendered `HTTPRoute` attaches to
   the intended Gateway API `Gateway` and that `push.buzz.xyz` (or your
   configured hostname) resolves to it; otherwise confirm your own ingress
   path reaches the chart's `Service` on port 8080.
9. Opt in the relay side only once the gateway is healthy: set
   `BUZZ_PUSH_ENABLED=true` on the relay deployments that should use it,
   leaving `BUZZ_PUSH_GATEWAY_DELIVERY_URL` unset to use the canonical
   `https://push.buzz.xyz/v1/deliveries/apns`, or overriding it to another
   exact `https://.../v1/deliveries/apns` URL that resolves to this
   deployment.

## Roll back

1. Set `BUZZ_PUSH_ENABLED=false` on every relay that opted in. This stops
   NIP-PL advertisement, lease acceptance, matching, and new gateway traffic
   without deleting credentials or mutating existing leases.
2. Only after relay delivery is disabled, if the gateway deployment itself
   must come down (for example, it is unhealthy), scale it down or roll
   back its release. Existing leases and gateway installations/delegations
   then expire naturally through the retention reaper rather than requiring
   explicit deletion.
3. To revert a key rotation, keep the previous AEAD key as a decrypt-only
   predecessor in `BUZZ_PUSH_GRANT_KEYS`/`BUZZ_PUSH_TOKEN_KEYS` rather than
   removing it immediately — remove a predecessor only once every capability
   or token encrypted under it has expired or been re-encrypted.
4. After any Secret rotation (AEAD keys or the APNs certificate), perform an
   explicit rolling restart — Kubernetes does not restart pods when a
   referenced Secret's bytes change — and confirm readiness before removing
   the predecessor key.

## See also

- The container-level description of the gateway's responsibility,
  ownership boundary against the relay, and interfaces: the
  `architecture/containers/push-gateway.md` node (id
  `architecture-containers-push-gateway`).
- The end-to-end push-notification delivery flow this gateway participates
  in, including the relay-side matcher and delivery worker: the
  `architecture/flows/push-notification.md` node (id
  `architecture-flows-push-notification`).
- The full, variable-by-variable operator reference — every environment
  variable, the metrics and alerting tables, and the chart release mechanics
  in one place: `docs/push-gateway-deployment.md`. This node deliberately
  does not restate that reference's tables; it sequences the actions an
  operator takes and points there for the authoritative detail behind each
  one.
- Responding to a push notification that failed to deliver once the
  gateway is already running: a separate runbook node, not yet written at
  this revision (tracked as issue #1225).

## Boundary

This node does not describe: looking up a specific environment variable's
type, default, or bound outside the sequence above — that is
`docs/push-gateway-deployment.md`'s reference table, not this how-to's job.
It does not describe the NIP-PL wire protocol, the relay's own internal
matcher/delivery-worker behavior, or how a client obtains a delegation
capability — those are the flow node's and a future NIP-PL interfaces-events
node's subject matter. It is not a runbook: it walks through planned,
operator-initiated deployment and rollback, not a response to an
already-firing alert or an already-failed delivery (issue #1225 owns that).
It does not decide whether this fork should ever operate a live push-gateway
deployment — see *Scope and omissions* for what was found and not found on
that question.

## Relationships

None declared. The two natural targets — `architecture-containers-push-gateway`
and `architecture-flows-push-notification` — are both `status: draft` at the
recorded revision and their presence on `origin/launchpad` at merge time is
not established here; declaring an edge to either risks resolving in this
worktree while hard-failing validation on the branch this task merges into,
exactly the trap `AGENTS.md`'s *Creating a node* step 9 and the naming/linking
standards warn against. Both are named in prose above instead. A future edit
may add `references` edges to both once each is confirmed present on
`origin/launchpad`.

## Scope and omissions

**This node covers** the operator-facing procedure for building or obtaining
an image, provisioning secrets, rendering and installing/upgrading the Helm
chart, verifying a successful rollout, opting the relay side in, and rolling
back — grounded in this repository's own `Dockerfile.push-gateway`, Helm
chart, chart tests, and CI workflows.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Every environment variable's exact type, default, and bound; the metrics and alerting reference tables | `docs/push-gateway-deployment.md` |
| Incident response for a push notification that failed to deliver | A future runbook node — issue #1225, not yet written at this revision |
| The gateway's architecture, ownership boundary, and interfaces | `architecture-containers-push-gateway` |
| The end-to-end delivery flow and its trust-boundary crossings | `architecture-flows-push-notification` |
| The NIP-PL wire protocol itself | A future interfaces-events node — not written yet |
| Whether this fork should ever operate a live push-gateway deployment | Not decided here — see below for what was checked |

**Expected but not verified when this node was written:**

- **Whether this fork (launchpad-26/buzz) operates, or intends to operate, a
  live push-gateway deployment against any of its own hosts.** No
  launchpad-scoped deployment manifest, Terraform stack, or ArgoCD
  application referencing the push gateway was found anywhere in this
  repository, and `.github/workflows/docker.yml` explicitly gates the
  gateway's own image-build and publish jobs to `github.repository ==
  'block/buzz'` with a comment stating this fork does not operate the
  gateway. This node therefore documents the deployment mechanism this
  repository actually ships — the Dockerfile, the Helm chart, and their
  own tests — as an operator would use it against any target cluster,
  while stating plainly that no evidence was found of this fork using it
  against a live host of its own.
- **No `helm upgrade --install` (or equivalent) command was actually run
  against a real cluster while writing this node.** The install/upgrade
  step is grounded in the chart's declared values, its migration Job's
  Helm hook annotations, and `tests/render.sh`'s lint/template assertions
  — all of which were executed — not in an executed deployment, and the
  exact invocation shape in step 5 above is recorded as an `INFERENCE`,
  not a `FACT`, for that reason.
- **Whether `deploy/charts/buzz-push-gateway/tests/release-contract.sh`
  passes at this revision was not independently re-run here**; its
  contents were read to confirm what the publish workflow's gating
  actually requires, but the script itself was not executed as part of
  authoring this node.
- **Whether `architecture-containers-push-gateway` and
  `architecture-flows-push-notification` will have merged to
  `origin/launchpad` by the time this node's own branch integrates** was
  not established — both are `status: draft` in this worktree, which is
  why *Relationships* above declares neither as an edge.

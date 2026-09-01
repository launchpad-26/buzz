---
id: operations-deployment-relay
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
  - statement: "The relay image is a multi-stage Docker build (`ARG RUST_VERSION=1.95`) that compiles the `buzz-relay`, `buzz-admin`, and `buzz-pair-relay` binaries and the `web`/`admin-web` static bundles, assembles them into a `debian-slim` runtime that keeps a real `git` binary on `PATH` (the relay shells out to it for repo hydrate/receive-pack/upload-pack), runs as a non-root `buzz:buzz` user (uid/gid 1000), sets `ENTRYPOINT [\"/usr/local/bin/buzz-relay\"]`, and declares `EXPOSE 3000 8080 9102`."
    entry_class: FACT
    evidence:
      - "Dockerfile"
  - statement: "`.github/workflows/docker.yml` builds and publishes this fork's own relay image to `ghcr.io/launchpad-26/buzz`: every push to the `launchpad` branch publishes `:launchpad` and `:sha-<full-commit>` (plus `:debug-*` variants with line-table debug info for profiling), and a `relay-v*.*.*` tag additionally publishes `:{version}`, `:{major.minor}`, `:{major}`, and — for a stable (non-prerelease) version — moves `:latest`; `workflow_dispatch` exists only to rescue-publish an already-tagged commit and rejects a dispatch whose ref, checked-out HEAD, and tag do not resolve to the same commit."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "`RELEASING.md`'s own relay row states the published artifact is `ghcr.io/block/buzz` — the upstream image name. That is upstream's own image; this fork's `.github/workflows/docker.yml` (opened directly, see the evidence entry above) publishes to `ghcr.io/launchpad-26/buzz` instead, matching the same correction the merged `architecture-containers-relay` node already recorded for this fork."
    entry_class: INFERENCE
    evidence:
      - "RELEASING.md"
      - ".github/workflows/docker.yml"
    confidence: 0.85
  - statement: "The relay release lane, per `RELEASING.md`'s own \"Relay\" walkthrough, is: `just release-relay` runs on `main`, bumps `crates/buzz-relay/Cargo.toml`, regenerates `Cargo.lock`, and opens/updates a `relay-release/<version>` PR; merging that PR causes `auto-tag-on-release-pr-merge` to push a `relay-v<version>` tag; that tag triggers `docker.yml`, which (for a stable release) updates the version aliases and `:latest` and publishes a matching `debug-<version>` image. Every push to `main` separately publishes the rolling `:main`/`:sha-<7>` (and `:debug-main`/`:debug-sha-<7>`) tags regardless of any release."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "`Db::new` (writer/reader pool setup) and, when `BUZZ_AUTO_MIGRATE` is truthy, `db.migrate()` both run and must succeed before `main()` proceeds; a database connection failure or a failing migration is propagated with `?` before any listener binds, so the relay process exits rather than serving traffic in a degraded state."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:179-211"
  - statement: "`buzz_auto_migrate_enabled` recognizes `true`/`1`/`yes`/`on` (case-insensitive, trimmed) as enabling automatic migration on startup; anything else, including unset or an empty string, leaves pending migrations unapplied and logs \"Skipping database migrations because BUZZ_AUTO_MIGRATE is not enabled\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:201-211"
  - statement: "Manual migration outside the auto-migrate path is `buzz-admin migrate`: the `Command::Migrate` arm connects to the database and calls the same `db.migrate()` method the relay's own boot path uses, then prints \"Database migrations complete.\"."
    entry_class: FACT
    evidence:
      - "crates/buzz-admin/src/main.rs:79-80"
      - "crates/buzz-admin/src/main.rs:151-156"
  - statement: "After the database connects and migrations resolve, `main()` connects an audit-log Postgres pool, then `PubSubManager::new` opens the Redis connection (\"Redis pub/sub connected\"), then a separate search-database pool connects, then `buzz_media::MediaStorage::new` connects to S3-compatible object storage (\"Media storage connected\") — establishing every backing dependency before either the health-only or app TCP listener is bound."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:370-444"
  - statement: "Unless explicitly disabled with `BUZZ_GIT_CONFORMANCE_PROBE=false` (any other value, including unset, leaves it enabled), the relay runs a git object-storage conformance probe (\"A3 gate\") against the configured S3/MinIO backend before serving; the probe's own comment states failure is fatal because \"a backend that cannot satisfy pointer CAS invalidates the manifest-pointer protocol\", and a failed probe surfaces as an error propagated with `?`, before either listener binds."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:489-525"
  - statement: "The relay binds a dedicated health-only TCP listener (`config.health_port`) before the app router's own TCP/Unix-domain-socket listeners, and serves that health router with its own `axum::serve` call independent of the app router's listener(s)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1296-1301"
      - "crates/buzz-relay/src/main.rs:1371-1433"
  - statement: "`readiness_handler` returns 503 immediately if the in-process `shutting_down` flag is set; otherwise it concurrently checks a Postgres ping, a Redis pool acquisition, and the deletion-serving catalog, and only reports ready when all three succeed. `liveness_handler` returns `200 ok` unconditionally with no dependency checks at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:397-424"
      - "crates/buzz-relay/src/router.rs:400-403"
  - statement: "The relay's own graceful-shutdown contract, stated in `main.rs`'s doc comment on its restart handler: on `SIGTERM`, `shutting_down` flips true (readiness starts returning 503) and a fixed 5s grace period runs before listeners close and the hard drain begins; the hard drain (`GRACEFUL_DRAIN_TIMEOUT` = 30s) closes live WebSocket connections with up to `MAX_DRAIN_JITTER_MS` (20s) of per-connection jitter plus a close-frame acknowledgment wait, for a documented worst case of 5s + 30s = 35s from signal to forced exit."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs:1254-1287"
  - statement: "A Buzz community (tenant) is resolved from the connecting request's HTTP `Host` header before any AUTH/EVENT/REQ/REST/media/git/search/workflow/pub-sub handling runs (`bind_community`'s row-zero binding); an empty or unmapped host fails closed with a generic rejection, and there is deliberately no fallback or default community a request can land in."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/tenant.rs:1-88"
  - statement: "The `communities` table (`host` column, `UNIQUE(lower(host))`) is created by the initial schema migration with no seed data — no migration, Compose file, or Helm template inserts a row into it — so a freshly migrated database maps no host to any community until one is created by some other means."
    entry_class: FACT
    evidence:
      - "migrations/0001_initial_schema.sql:53-61"
  - statement: "`scripts/start-relay-for-tests.sh` states explicitly, in its own comment, that \"the relay never auto-seeds a community\"; the only in-repository tooling that inserts a `communities` row are three developer/test scripts (`scripts/seed-local-community.sh`, `scripts/setup-desktop-test-data.sh`, `scripts/start-relay-for-tests.sh`), each of which runs a direct `INSERT INTO communities (host) ...` against the database via `psql`, none of which is wired into `deploy/compose/` or `deploy/charts/buzz/`."
    entry_class: FACT
    evidence:
      - "scripts/start-relay-for-tests.sh:115"
      - "scripts/seed-local-community.sh:86-93"
  - statement: "The only production-capable path found in this repository for creating a community/host mapping is `POST /operator/communities`: a NIP-98-signed request, verified against `RELAY_OPERATOR_API_ORIGIN`, from a pubkey in `RELAY_OPERATOR_PUBKEYS`, with a JSON body `{\"host\": \"<domain>\", \"initial_owner_pubkey\": \"<hex>\"}`, which atomically creates the community row and bootstraps its initial owner. Both `RELAY_OPERATOR_PUBKEYS` and `RELAY_OPERATOR_API_ORIGIN` default to unset, at which point the deployment-wide provisioning endpoints reject every request rather than falling back to any default community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:137-193"
      - "crates/buzz-relay/src/config.rs:249-273"
  - statement: "No documented operator runbook in this repository (`deploy/compose/README.md`, `deploy/charts/buzz/README.md`, `RELEASING.md`) walks through calling `POST /operator/communities` for a first production deployment; the capability was found by reading `crates/buzz-relay/src/api/operator.rs` directly, not by following any deployment document to it."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/operator.rs:137-148"
  - statement: "The relay's `relay_url` config field (env `RELAY_URL`) is documented in code as \"Public WebSocket URL of this relay, advertised in NIP-11\"; `deploy/compose/.env.example` additionally sets `BUZZ_DOMAIN` (used by the optional Caddy TLS overlay and URL-derived settings) and `BUZZ_CORS_ORIGINS` alongside it for a production single-domain deployment."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:165-166"
      - "deploy/compose/.env.example:9-14"
  - statement: "The relay's NIP-11 relay-information document is served from `GET /` when the request sends `Accept: application/nostr+json` (or, on a non-WebSocket, non-nostr+json request, as the router's own HTML/NIP-11 fallback), built per-request from the resolved tenant and the relay's own config; a plain WebSocket upgrade request to the same path instead completes the WS handshake."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/router.rs:303-334"
      - "crates/buzz-relay/src/router.rs:380-387"
      - "crates/buzz-relay/src/nip11.rs:222-231"
  - statement: "`crates/buzz-relay/src/config.rs`'s documented required/central runtime inputs include `DATABASE_URL`, `REDIS_URL`, `BUZZ_S3_*` (endpoint/access key/secret key/bucket), `RELAY_URL`, and an optional `BUZZ_RELAY_PRIVATE_KEY` (a fresh keypair is generated at startup if absent, which is explicitly not durable identity); `deploy/compose/.env.example` names the same set as production secrets that must be generated once and preserved, alongside `RELAY_OWNER_PUBKEY` and `BUZZ_GIT_HOOK_HMAC_SECRET`."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs:144-190"
      - "deploy/compose/.env.example:16-36"
  - statement: "`deploy/compose/run.sh`'s `require_env` refuses to start the stack (`start`/`restart`/`pull`/`upgrade`/`config`) when `.env` is missing or still contains a `CHANGE_ME` placeholder, so an operator cannot boot the relay against unresolved secrets by accident on that platform."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:19-36"
  - statement: "`deploy/compose/run.sh upgrade` runs `docker compose pull` then `docker compose up -d --wait` and prints a backup-hint checklist (`.env` secrets, the owner private key, a Postgres snapshot, the object-storage bucket, the git-data volume, and — with TLS enabled — the Caddy data/config volumes) every time; `deploy/compose/README.md` documents that rollback is restoring the previous immutable `BUZZ_IMAGE` value and re-running the same check/upgrade commands, and states that an image-only rollback is safe only when the intervening database migrations were backward-compatible, otherwise the database and object/git state must be restored together as one coordinated recovery."
    entry_class: FACT
    evidence:
      - "deploy/compose/run.sh:38-73"
      - "deploy/compose/README.md:91-98"
  - statement: "`deploy/charts/buzz/README.md`'s own Upgrades section states schema migrations are embedded via `sqlx::migrate!`, run at startup gated by `BUZZ_AUTO_MIGRATE` (chart default `true`), made race-safe across replicas by a Postgres advisory lock, and that \"`helm upgrade` is the entire upgrade procedure\" in that mode; decoupling migrations (`migrate.autoMigrate=false`) instead requires the operator to run `buzz-admin migrate` out-of-band before every `helm install`/`helm upgrade`, and the chart's own readiness probes verify only database connectivity, not schema freshness, so a pod can report healthy while serving against an unmigrated schema in that mode."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/README.md:219-225"
  - statement: "`deploy/compose/README.md`'s own \"Validation\" section verifies a fresh install by running the platform's start command and then curling the relay's `/_liveness` endpoint directly, followed by a status command — i.e. the platform-agnostic verification concern is \"can I reach `/_liveness` (or `/_readiness`) and does it return `200`\", with the exact command being Compose-specific."
    entry_class: FACT
    evidence:
      - "deploy/compose/README.md:100-109"
  - statement: "This node was written using launchpad/docs/corpus/templates/procedure.md, which was already merged on origin/launchpad at the recorded revision and directs a how-to-shaped corpus node to carry an Overview, an optional Before-you-start, one numbered task sequence (or decimal sub-tasks) per logical goal, a See-also section, an explicit Boundary statement, a Relationships section, and a Scope-and-omissions section distinguishing exclusions from unverified gaps."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/procedure.md"
relationships:
  - type: references
    target: architecture-containers-relay
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-deployment-hosted-topology
---

# Deploy the relay: how-to

How to bring up one running instance of the `buzz-relay` binary — obtaining its
image, supplying what it needs to boot, giving it a domain and at least one
community, sequencing it against its backing services, confirming it is
actually serving, and planning its next upgrade — at the level that holds true
whether the container runs under Docker Compose, Helm/Kubernetes, or a raw
`docker run`. A reader performs this the first time a relay goes up for a new
domain, and again, in the parts that differ (upgrade/rollback), on every
subsequent release.

## Before you start

- A place to run the container: a host with Docker Engine (for Compose), or a
  Kubernetes cluster (for the Helm chart) — which platform to use, and that
  platform's own command surface, is a decision this node does not make; see
  *Boundary*.
- Reachable Postgres, Redis, and S3-compatible object storage the relay's
  network namespace can connect to. This node does not choose how you run
  them — only that the relay's own boot sequence requires them, in order (see
  step 4 below).
- A domain or hostname the relay will be reached at, and the ability to point
  DNS at wherever the container is exposed.
- The ability to generate and durably store a fresh Nostr keypair (for
  `BUZZ_RELAY_PRIVATE_KEY`) and, if you already know who should own the first
  community, that owner's public key.

## Deploy the relay

1. **Obtain the relay image.** Either pull this fork's published image from
   `ghcr.io/launchpad-26/buzz` — `:launchpad` and `:sha-<full-commit>` track
   every push to the `launchpad` branch, and a `relay-v<version>` tag
   additionally publishes `:<version>`, `:<major.minor>`, `:<major>`, and, for
   a stable release, moves `:latest` — or build the repository's own
   `Dockerfile` yourself. The image is a non-root (`buzz:buzz`) `debian-slim`
   runtime that bundles `buzz-relay`, `buzz-admin`, `buzz-pair-relay`, the
   `web`/`admin-web` static frontends, and a real `git` binary the relay
   shells out to for its git-hosting feature; it declares `EXPOSE 3000 8080
   9102` and its `ENTRYPOINT` is `buzz-relay` itself. Prefer an immutable tag
   (a digest or the full `:sha-<commit>` form) over a floating tag like
   `:launchpad` or `:latest` for anything you intend to run twice — see step 6.
2. **Supply the environment and secrets the relay needs to start.** At minimum:
   `DATABASE_URL` (Postgres), `REDIS_URL` (Redis), the `BUZZ_S3_*` family
   (endpoint, access key, secret key, bucket) for object storage, and a
   durable `BUZZ_RELAY_PRIVATE_KEY` — if you leave it unset, the relay
   generates a fresh keypair every boot, which is not stable identity and
   should never be relied on past a single process lifetime. Set
   `RELAY_OWNER_PUBKEY` if you already know who owns this deployment; it is
   bootstrapped into `relay_members` with the `owner` role on first startup.
   Whether these values live in a `.env` file, a Kubernetes `Secret`, or
   something else is the platform's own concern, not this node's.
3. **Give the deployment a domain, and provision at least one community for
   it.** Set `RELAY_URL` to the relay's own public WebSocket URL — it is
   advertised in the NIP-11 document served at `GET /` — and route your
   domain's DNS and any TLS termination at wherever the container is exposed.
   A request's `Host` header is resolved to a community *before* any other
   handling runs, and an unmapped host is rejected, with no default or
   fallback community to land in — so the relay will run and respond to
   `/_liveness` immediately, but every real Nostr/API request against an
   unrecognized host fails closed until a `communities` row exists for it.
   Nothing in this repository seeds that row automatically: the only
   production-capable path found is a NIP-98-signed `POST
   /operator/communities` request (body `{"host", "initial_owner_pubkey"}`)
   from a pubkey listed in `RELAY_OPERATOR_PUBKEYS`, verified against
   `RELAY_OPERATOR_API_ORIGIN` — both unset by default, which fails the
   provisioning endpoints closed rather than falling back to an implicit
   community. See *Scope and omissions* for what this node could not verify
   about that path.
4. **Let dependencies come up before the relay, and let the relay's own boot
   sequence run in order.** The relay's `main()` connects to Postgres first
   (fatal on failure), then applies pending migrations only if
   `BUZZ_AUTO_MIGRATE` is truthy (`true`/`1`/`yes`/`on`, case-insensitive) —
   otherwise migrations are skipped and must be applied out-of-band with
   `buzz-admin migrate` before the schema is current. It then connects an
   audit-log pool, opens the Redis pub/sub connection, connects a
   search-database pool, and connects to object storage — in that order,
   each one fatal on failure. Unless explicitly disabled
   (`BUZZ_GIT_CONFORMANCE_PROBE=false`), it then runs a conformance probe
   against the object-storage backend before serving git traffic, and a
   failed probe is also fatal. Only after all of that does it bind its
   health-only listener and then its app listener(s) — so whatever mechanism
   your platform uses to sequence container startup (health checks,
   init containers, `depends_on`) exists to keep the relay from being asked
   to serve before its own boot sequence would let it anyway; it does not
   need to replicate the ordering above, only avoid fighting it.
5. **Verify the relay is actually serving.** Two independent things to check,
   both platform-agnostic:
   - `GET /_readiness` on the health port returns `200` only when the
     shutdown flag is clear and Postgres, Redis, and the deletion-serving
     catalog all check out; `GET /_liveness` on the same port returns `200`
     unconditionally once the process is up, with no dependency checks — so
     a healthy liveness probe on a relay that is not yet ready is expected
     during startup, not a fault.
   - `GET /` with `Accept: application/nostr+json` against the domain you
     configured in step 3 returns the relay's NIP-11 document. If it 404s or
     the WebSocket handshake at the same path fails, re-check that the
     request's `Host` actually maps to a community per step 3.
6. **Plan the upgrade path before you need it, not during an incident.**
   Pin to an immutable image reference — a digest or the full
   `:sha-<commit>` tag — never a floating tag, so that redeploying the exact
   same reference twice is guaranteed to run the exact same code. Back up
   the relay's private key, the Postgres database, and the object-storage
   bucket before upgrading. A schema-compatible upgrade (new relay code
   against an unchanged or additive schema) is a plain image swap; an
   upgrade that ships new migrations is safe to roll back only if those
   migrations are backward-compatible — otherwise rolling back the image
   alone leaves a newer schema under older code, and the coordinated
   recovery is restoring the database and object/git state to match the
   image, not the image alone.

## See also

- The relay as a deployable unit — its responsibility, inbound/outbound
  interfaces, and technology boundary — is `architecture-containers-relay`
  (`launchpad/docs/corpus/architecture/containers/relay.md`); this node
  assumes that shape rather than restating it.
- The concrete single-node/VPS topology (`architecture-deployment-single-relay`)
  and the Kubernetes-native topology (`architecture-deployment-hosted-topology`)
  describe, respectively, the Docker Compose bundle under `deploy/compose/`
  and the Helm chart under `deploy/charts/buzz/` in full — container/volume
  layout, network boundaries, and each platform's own failure/recovery
  behavior. This node names the steps that are true regardless of which one
  you read next.
- A platform-specific how-to for actually running the Compose bundle, the
  Helm chart, or a raw Kubernetes manifest set is a separate procedure per
  platform (tracked as this Feature's own tasks); none is merged into the
  corpus at the recorded revision, so none is linked here by path — see
  *Boundary*.
- A runbook for an already-unhealthy relay (readiness failing, `/_liveness`
  down, a pod crash-looping) is a distinct, separately tracked concern this
  node does not cover — see *Boundary*.

## Boundary

This node does not describe:

- **Any single platform's own command surface.** Docker Compose's exact
  `docker compose` invocations, the Helm chart's values schema and
  `helm install`/`helm upgrade` mechanics, and a raw Kubernetes manifest set
  are each a separate how-to's territory once written; this node states the
  relay-specific concern (what image, what env, what ordering, what to
  verify) that every one of those platforms has to satisfy, not how any one
  of them satisfies it.
- **Responding to a relay that has already stopped serving.** A runbook is
  for a condition that has already occurred and demands a response; this
  node is for a task an operator chooses to perform on their own schedule —
  standing up a new relay, or rolling one forward. Neither Postgres, Redis,
  nor object storage being *stood up* is covered either — this node assumes
  they exist and are reachable, and describes only the order the relay
  connects to them in.
- **How the relay's container image itself is architected, or why the
  single-relay/hosted-topology shapes look the way they do.** Those are
  `architecture-containers-relay`'s and the two deployment-topology nodes'
  own territory, linked above rather than restated.
- **A newcomer's first exposure to what a Nostr relay is or does.** This
  guide assumes the reader already knows what they are trying to accomplish
  (stand up or upgrade a running relay) and only sequences the steps to do
  it correctly — it is not a tutorial introducing relay concepts from
  scratch.

## Relationships

- `references`: `architecture-containers-relay` — this procedure assumes the
  relay's own responsibility, interfaces, and technology boundary as
  described there rather than restating them.
- `references`: `architecture-deployment-single-relay` — the concrete
  Docker Compose topology a reader following step 1 onward, on that
  platform, lands in.
- `references`: `architecture-deployment-hosted-topology` — the concrete
  Kubernetes/Helm topology a reader following step 1 onward, on that
  platform, lands in.

All three targets exist on `origin/launchpad` at the recorded revision (see
the provenance evidence entry). No `part-of` edge is declared toward a
broader `operations` capability node: no such node exists yet on the merge
branch to point at.

## Scope and omissions

**This node covers** the relay-specific deployment concerns that hold
regardless of the hosting platform: obtaining the image, the environment and
secrets the relay's own boot sequence requires, the host-derived community
boundary and NIP-11/domain configuration a fresh deployment must resolve
before it serves real traffic, the relay's actual startup ordering against
Postgres/Redis/object storage, the two independent things "is it serving"
means (readiness/liveness and a working NIP-11 response), and the
platform-agnostic shape of an upgrade/rollback.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Docker Compose's own command surface and file layout | a separate procedure node for that platform (this Feature's own task, not yet merged) |
| The Helm chart's values schema and `helm`/ArgoCD/Flux mechanics | a separate procedure node for that platform (this Feature's own task, not yet merged) |
| A raw Kubernetes manifest deployment path | a separate procedure node for that platform (this Feature's own task, not yet merged) |
| Responding to a relay that is already failing its readiness/liveness probes | a runbook (this Feature's own task, not yet merged) |
| The relay's internal architecture, responsibility, and interfaces | `architecture-containers-relay` |
| The concrete single-node and Kubernetes-native topologies in full | `architecture-deployment-single-relay`, `architecture-deployment-hosted-topology` |
| Block's internal `squareup/sprout-oss` → ECR → `squareup/block-coder-tf-stacks` deployment pipeline named in root `CLAUDE.md`'s ecosystem table | that pipeline, outside this checkout and not independently verified here |

**Expected but not verified when this node was written:**

- **Whether `POST /operator/communities` is actually how any real deployment
  in this fork's history has provisioned its first community.** The endpoint
  exists in code and was read directly (`crates/buzz-relay/src/api/operator.rs`),
  but no deployment document (`deploy/compose/README.md`,
  `deploy/charts/buzz/README.md`, `RELEASING.md`) walks an operator through
  calling it, and it was not exercised against a running relay for this node.
  An operator following this guide today has a documented mechanism but no
  documented example of using it end to end.
- **Whether a platform's own startup-ordering primitive (Compose
  `depends_on: condition: service_healthy`, a Kubernetes init container, or
  similar) is actually wired up to wait for the relay's dependencies in every
  deployment path this repository ships**, versus only the ones the two
  merged topology nodes describe. This node states what the relay's own code
  requires in what order; whether every platform-specific bundle enforces
  that ordering for you, or merely permits you to, is each platform node's
  claim to verify, not re-verified here.
- **Whether Docker Compose's own default `stop_grace_period` (used when no
  override is set) comfortably exceeds the relay's documented 35-second
  worst-case graceful-shutdown window.** Not opened for this node; the
  merged `architecture-deployment-single-relay` node already flags the same
  gap for the Compose bundle specifically.

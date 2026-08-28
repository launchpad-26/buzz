---
id: architecture-containers-push-gateway
type: architecture
status: draft
origin: launchpad
audiences:
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "buzz-push-gateway is described in its own manifest as a blind, capability-gated NIP-PL gateway for the Buzz mobile app, and its lib.rs module doc calls it a stateful, capability-gated APNs last hop for NIP-PL."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml"
      - "crates/buzz-push-gateway/src/lib.rs"
  - statement: "The gateway is built as its own binary crate (buzz-push-gateway) with its own Dockerfile (Dockerfile.push-gateway), separate from the relay image; the deployment doc states explicitly not to run it in the relay image or give relays APNs credentials."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/Cargo.toml"
      - "Dockerfile.push-gateway"
      - "docs/push-gateway-deployment.md"
  - statement: "The public API is seven POST routes -- /v1/installations/challenges, /v1/installations, /v1/delegations, /v1/delegations/revoke, /v1/installations/endpoint, /v1/installations/revoke, /v1/deliveries/apns -- served on a public router with a request body size limit, a concurrency limit, and a request timeout layered on top."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "A separate private health router serves GET /_liveness and GET /_readiness, and additionally GET /metrics in Prometheus text format when a metrics handle is supplied; the module doc states metrics live only on the private router, never on the public port."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "The public listener defaults to 0.0.0.0:8080 (BUZZ_PUSH_BIND_ADDR) and the private health listener defaults to 0.0.0.0:8081 (BUZZ_PUSH_HEALTH_ADDR); the deployment doc instructs operators to route https://push.buzz.xyz to the public port and never expose the health port publicly."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
      - "docs/push-gateway-deployment.md"
  - statement: "Readiness fails when the PostgreSQL authority store is unavailable or the process has stopped accepting new requests; shutdown flips an accepting flag, stops the public listener with a bounded 30-second drain, then stops the health listener and aborts the retention reaper task."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/main.rs"
  - statement: "The gateway requires DATABASE_URL, BUZZ_PUSH_PUBLIC_DELIVERY_URL, BUZZ_PUSH_MAX_GRANT_LIFETIME_SECONDS, BUZZ_PUSH_ENABLED_PROFILES, BUZZ_PUSH_APP_ATTEST_APP_ID, BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH, BUZZ_PUSH_APNS_KEY_PATH, BUZZ_PUSH_APNS_KEY_ID, BUZZ_PUSH_APNS_TEAM_ID, BUZZ_PUSH_APNS_TOPIC, BUZZ_PUSH_GRANT_KEYS, and BUZZ_PUSH_TOKEN_KEYS at startup, and refuses to start if any is missing or malformed."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "BUZZ_PUSH_PUBLIC_DELIVERY_URL is validated to be exactly an https scheme, host push.buzz.xyz, no port, path /v1/deliveries/apns, and no query, fragment, username, or password -- a malformed or non-matching URL fails startup rather than being accepted loosely."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The gateway holds two independently keyed AEAD keyrings -- BUZZ_PUSH_GRANT_KEYS for delegation capabilities returned to clients/relays, and BUZZ_PUSH_TOKEN_KEYS for APNs device-token custody in PostgreSQL -- and startup rejects any configuration where a grant key and a token key share an id or key material, so the two trust boundaries cannot collapse into one."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
      - "crates/buzz-push-gateway/src/grant.rs"
  - statement: "The grant keyring's own module doc states the gateway is stateless with respect to delegation capabilities: relays retain the opaque AEAD-sealed ciphertext and present it on each delivery attempt, rather than the gateway tracking it server-side."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/grant.rs"
  - statement: "Despite being stateless for delegation capabilities, the gateway persists installation, delegation, challenge, and replay-admission state in PostgreSQL via a PostgresAuthorityStore, so the container as a whole is not stateless -- state and capability-opacity are two different properties documented in two different modules."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-push-gateway/src/grant.rs"
      - "crates/buzz-push-gateway/src/postgres.rs"
      - "crates/buzz-push-gateway/src/main.rs"
    confidence: 0.85
  - statement: "The gateway owns a scoped SQL migration (0001_push_gateway_authority.sql) that creates six push_gateway_* tables: push_gateway_challenges, push_gateway_installations, push_gateway_delegations, push_gateway_endpoint_quotas, push_gateway_delivery_auth_replays, and push_gateway_delivery_request_replays."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql"
  - statement: "The service reaps expired challenges and replay rows, idle quota rows, expired/revoked delegations, and retention-eligible installations (including their encrypted token ciphertext) at startup and every five minutes via a background reaper task."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs"
  - statement: "The deployment doc states that database backups therefore contain APNs-token ciphertext plus authority metadata and must receive the same access controls and retention treatment as the service secrets, and that the migration role is DDL-capable while the runtime role is restricted to CONNECT/USAGE/SELECT/INSERT/UPDATE/DELETE on only the six gateway tables, with database/schema CREATE revoked from the runtime role after migration."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "The gateway's only outbound network dependencies at runtime are its own PostgreSQL database and Apple's APNs HTTP/2 service; the ApnsTransport module builds provider-JWT-authenticated APNs requests and classifies APNs responses into a sanitized DeliveryOutcome (Accepted, InvalidEndpoint, Retry, RefreshCredential, ConfigurationFault, PermanentRequestFault) so raw provider response bodies never cross into gateway logs or metrics."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "The relay is the gateway's sole inbound client for delivery: buzz-relay's push_runtime module builds a DeliveryRequest carrying the opaque endpoint_grant, signs a NIP-98 (HTTP Auth) header over it with the relay's own keypair, and POSTs it to the relay-configured push_gateway_delivery_url, which the deliver handler verifies with nostr::nips::nip98::verify_auth_header before opening the grant."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "buzz-relay's push_gateway_delivery_url config option defaults to the gateway's own advertised public delivery URL (https://push.buzz.xyz/v1/deliveries/apns) unless BUZZ_PUSH_GATEWAY_DELIVERY_URL is set; operators can point it at another exact HTTPS /v1/deliveries/apns URL or disable NIP-PL push entirely by setting the variable to an empty string, in which case the relay's matcher and delivery worker are not started."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay advertises a NIP-PL push descriptor and a nip-pl supported_extensions entry in its NIP-11 document only when a gateway delivery URL is configured, so a relay with no gateway configured advertises no push capability at all."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The relay-side push lease is a NIP-PL kind:30350 addressable event; crates/buzz-relay/src/handlers/push_lease.rs performs strict envelope/plaintext validation of that event, and the relay never routes a lease-derived event through the gateway when push_gateway_delivery_url is unset."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/push_lease.rs"
  - statement: "The gateway's client-facing enrollment/delegation flow authenticates with Apple App Attest (challenge, attestation, and per-request assertions verified against a pinned Apple App Attest root certificate loaded from BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH), not with a Nostr key -- distinguishing the client-to-gateway trust boundary (App Attest) from the relay-to-gateway trust boundary (NIP-98)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "The deployment doc states relays retain lease matching, authorization, coalescing, durable jobs/retries, and generation checks, and receive only opaque capabilities from the gateway -- never APNs tokens or provider credentials -- which is the ownership boundary between the two containers."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "The gateway is published as its own OCI image (ghcr.io/block/buzz-push-gateway) by a dedicated push-gateway-build/push-gateway-merge job pair in .github/workflows/docker.yml, triggered by changes to Dockerfile.push-gateway, and deployed via a separate Helm chart (deploy/charts/buzz-push-gateway) with its own release lane distinct from the main buzz chart."
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
      - "docs/push-gateway-deployment.md"
  - statement: "Metrics emitted (push_gateway_apns_deliveries_total, push_gateway_apns_delivery_seconds, push_gateway_apns_credential_refreshes_total, push_gateway_admissions_total, push_gateway_delivery_errors_total, push_gateway_reaper_failures_total, push_gateway_readiness_failures_total) use only closed-set label values -- no endpoint, device token, relay pubkey, or request id is ever used as a label -- per the deployment doc, and scraping is opt-in via a PodMonitor/NetworkPolicy pair rather than on by default."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "This fork (launchpad-26/buzz) operates deployment, CI/CD, documentation and cohort process for Buzz rather than developing Buzz's Rust crates or React features, and does not currently deploy the push gateway to any launchpad-operated host -- the deployment doc describes upstream's production/staging deployment model, not something verified as running under this fork's own infrastructure."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "CLAUDE.md (this repository's fork-scope notice, 'This checkout is the launchpad-26 fork')"
---

# Container: push gateway (`buzz-push-gateway`)

## Responsibility, technology, and ownership boundary

`buzz-push-gateway` is a standalone Rust service (Axum + Tokio + SQLx/PostgreSQL)
that is the sole holder of Apple Push Notification service (APNs) provider
credentials in the Buzz system. Its own crate description calls it a "blind,
capability-gated NIP-PL gateway for the Buzz mobile app"; its library module doc
calls it a "stateful, capability-gated APNs last hop for NIP-PL." Both are true of
different parts of the same container: the *delegation capabilities* it issues are
opaque, AEAD-sealed blobs that relays hold and present back (the gateway does not
track them server-side), while the *installation/delegation/admission* bookkeeping
behind those capabilities is genuinely stateful, persisted in the gateway's own
PostgreSQL database.

It is built and shipped as its own binary and its own container image
(`Dockerfile.push-gateway` → `ghcr.io/block/buzz-push-gateway`), deliberately
separate from the relay image. The deployment doc is explicit that the relay image
must never run it and must never hold APNs credentials. That separation *is* the
ownership boundary: the relay owns lease matching, per-origin authorization,
coalescing, durable retry, and generation bookkeeping; the gateway owns App
Attest verification, APNs token custody, delegation-capability issuance, replay/quota
admission, and the actual APNs send. Relays receive only opaque capabilities from
the gateway, never a raw APNs device token or a provider credential.

Two independently keyed AEAD keyrings enforce that boundary inside the gateway
itself: `BUZZ_PUSH_GRANT_KEYS` seals the delegation capabilities that leave the
process (toward relays), and `BUZZ_PUSH_TOKEN_KEYS` seals APNs device tokens that
never leave the process except to Apple. Startup fails closed if a grant key and a
token key ever share an id or key bytes, so the two boundaries cannot be
accidentally collapsed into one keyring.

## Inbound and outbound interfaces, and directly connected containers

**Inbound, public (port `BUZZ_PUSH_BIND_ADDR`, default `0.0.0.0:8080`):**
seven `POST` routes under `/v1/` — `installations/challenges`, `installations`,
`delegations`, `delegations/revoke`, `installations/endpoint`,
`installations/revoke`, and `deliveries/apns`. The first six are the client
enrollment/delegation/rotation/revocation flow, authenticated with Apple App
Attest (challenge → attestation → per-request assertion, verified against a
pinned Apple App Attest root certificate). The last, `/v1/deliveries/apns`, is
the relay-facing delivery endpoint, authenticated with NIP-98 (a signed Nostr
HTTP-auth event) instead of App Attest — a second, distinct trust boundary on the
same container.

**Inbound, private (port `BUZZ_PUSH_HEALTH_ADDR`, default `0.0.0.0:8081`):**
`GET /_liveness`, `GET /_readiness`, and — only when a Prometheus metrics handle
is wired in — `GET /metrics`. This listener is documented as never to be exposed
publicly; readiness is what a load balancer or Kubernetes Service should gate
traffic on.

**Directly connected containers/systems:**

| Peer | Direction | Interface |
|---|---|---|
| Buzz relay (`buzz-relay`) | Inbound | `POST /v1/deliveries/apns`, NIP-98-authenticated, carrying an opaque `endpoint_grant` the relay received from a client's delegation flow |
| iOS/mobile client (Buzz app) | Inbound | The six App Attest-authenticated enrollment/delegation/rotation/revocation routes |
| PostgreSQL (gateway's own database) | Outbound | Authority/admission store: installations, delegations, challenges, quotas, replay fences — six `push_gateway_*` tables from one scoped migration |
| Apple APNs | Outbound | HTTP/2, provider-JWT authenticated; the gateway classifies every response into a small sanitized outcome enum before it touches logs or metrics, so raw APNs response bodies never leak into observability surfaces |

The relay side of the relay↔gateway interface lives in `buzz-relay`'s
`push_runtime` (the delivery worker that builds and sends the `DeliveryRequest`)
and `handlers/push_lease` (which validates the NIP-PL `kind:30350` lease event
that seeds a delivery). The relay advertises push support in its NIP-11 document
(a `nip-pl` extension entry and a push descriptor) only when it has a gateway
delivery URL configured; with no gateway configured, the relay advertises no push
capability and never starts the matcher/delivery worker.

## Deployment, data, and security implications

**Deployment.** The gateway has its own CI publish lane
(`push-gateway-build`/`push-gateway-merge` jobs in `.github/workflows/docker.yml`,
triggered by `Dockerfile.push-gateway` changes) and its own Helm chart
(`deploy/charts/buzz-push-gateway`) with a release process independent of the
main `buzz` chart. All replicas must share one PostgreSQL database, because
delivery authority, replay admission, and endpoint-quota reservation are
transactional there — replica count does not multiply the abuse ceiling.

**Data.** The six `push_gateway_*` tables hold AEAD-encrypted APNs tokens and
delegation/admission metadata, not plaintext tokens. A background reaper sweeps
expired challenges, replay rows, idle quota rows, expired/revoked delegations,
and retention-eligible installations (including their ciphertext) at startup and
every five minutes. Because the stored tokens are ciphertext, database backups
still require the same access-control and retention treatment as the service's
other secrets — encryption at rest in the schema does not relax that requirement,
it only bounds what a raw table dump exposes.

**Security.** Three separately-authenticated trust boundaries meet in this one
container: App Attest (client enrollment/delegation), NIP-98 (relay delivery),
and a PostgreSQL migration-role/runtime-role split (DDL-capable role runs
migrations and then revokes its own future `CREATE` grants; the runtime role gets
only `CONNECT`/`USAGE` plus DML on the six gateway tables). Grant-key and
token-key material must never overlap, and this is enforced at startup, not just
documented. Prometheus metrics use closed-set label values only — no endpoint,
device token, relay pubkey, or request id ever becomes a label — and metric
scraping is opt-in, not default-on.

## Implementation and further reading

- Gateway crate: `crates/buzz-push-gateway/` (`http.rs` for routes, `apns.rs` for
  the APNs transport, `grant.rs`/`token.rs` for the two AEAD keyrings,
  `app_attest.rs` for client attestation, `postgres.rs`/`authority.rs` for the
  PostgreSQL authority store, `config.rs` for environment configuration).
- Migration: `crates/buzz-push-gateway/migrations/0001_push_gateway_authority.sql`.
- Relay-side integration: `crates/buzz-relay/src/push_runtime.rs` (matcher +
  delivery worker), `crates/buzz-relay/src/handlers/push_lease.rs` (NIP-PL
  `kind:30350` lease validation), `crates/buzz-relay/src/config.rs` (the
  `BUZZ_PUSH_GATEWAY_DELIVERY_URL` relay-side setting), `crates/buzz-relay/src/nip11.rs`
  (push capability advertisement).
- Full operator runbook — network/health, every required environment variable,
  key rotation procedure, PostgreSQL role/grant model, metrics/alerting
  thresholds, and the Helm production-input contract: `docs/push-gateway-deployment.md`.
  This node deliberately does not restate that runbook's variable-by-variable
  detail; it names the interfaces and boundaries and points there for procedure.

## Scope and omissions

**This node covers** the push gateway as an architectural container: its
responsibility and technology, its ownership boundary against the relay, its
inbound/outbound interfaces and directly connected systems, and the deployment/
data/security implications of that boundary.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Step-by-step operator procedure (every environment variable, key rotation, Helm chart release mechanics) | `docs/push-gateway-deployment.md` |
| The NIP-PL protocol itself (`kind:30350` lease semantics, wire formats) | A future interfaces-events corpus node — not written yet |
| The relay's own container (matcher, delivery worker, lease validation as relay-side behavior rather than as a gateway peer) | A future architecture-containers node for the relay — not written yet |
| Whether this fork (launchpad-26/buzz) actually runs the push gateway against a live host | Not verified here — this fork operates deployment/CI/docs/process, not Buzz's Rust crates, and no evidence of a launchpad-operated push-gateway deployment was found while writing this node |

**No `relationships` are declared.** The only other corpus nodes merged at the
recorded revision (`corpus-readme`, `corpus-agents`,
`corpus-standard-confidence`, `corpus-standard-decision-references`) are all
`governance` nodes about the corpus itself, not architecture nodes this
container doc would meaningfully link to. The absence is a fact about this
moment — enumerated by listing the corpus tree at the recorded revision — not a
general rule; the relay's own container node and a NIP-PL interfaces-events node
are the natural first edges once they exist.

**Expected but not verified when this node was written:**

- **Whether this fork deploys the push gateway to any live host.** No
  `launchpad/`-scoped push-gateway deployment manifest, Terraform stack, or
  ArgoCD application was found during authoring; the deployment doc describes
  upstream's production model, which this node cites for its content but does
  not claim this fork operates.
- **Line-level behavior of every handler in `http.rs`.** The routes, their
  authentication boundary, and the delivery admission/finish flow were read; the
  full validation logic of every request field was not exhaustively traced
  field-by-field for this node, since that duplicates `http.rs` itself rather
  than describing the container.

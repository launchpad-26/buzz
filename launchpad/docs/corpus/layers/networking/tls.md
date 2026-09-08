---
id: layers-networking-tls
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
evidence:
  - statement: "This node was authored and checked against repository revision 29ca9b189bd3f639ba09c972b57c70538c0860c6."
    entry_class: FACT
    evidence:
      - "commit 29ca9b189bd3f639ba09c972b57c70538c0860c6"
  - statement: "The relay's serve() function binds every listener in the clear: tokio::net::TcpListener::bind(&config.bind_addr) for the application router, tokio::net::TcpListener::bind((\"0.0.0.0\", config.health_port)) for health probes, and an optional tokio::net::UnixListener for BUZZ_UDS_PATH, handing each to axum::serve unwrapped, with no TLS acceptor between socket and router."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "serve()'s own doc comment enumerates the process's listeners as 'Listener 1: TCP BUZZ_BIND_ADDR:3000 (app router)', 'Listener 2: UDS BUZZ_UDS_PATH', 'Listener 3: TCP 0.0.0.0:8080 (health only)' and 'Listener 4: TCP 0.0.0.0:9102 (metrics)' — four listeners, all described as TCP or UDS, none as TLS."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
  - statement: "The relay's rustls dependency exists for outbound connections, not inbound ones: buzz-relay/Cargo.toml's own comment says 'Redis TLS (rediss://, e.g. ElastiCache) uses rustls, which needs a process CryptoProvider', and main()'s first statement installs rustls::crypto::ring::default_provider() with the comment 'Required before any rustls TLS connection (rediss:// to ElastiCache, wss://, S3 over TLS)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-relay/src/main.rs"
  - statement: "No server-side TLS acceptor exists anywhere in the Rust workspace: a search of every .rs file under crates/ for bind_rustls, TlsAcceptor, tls_rustls, axum_server and rustls::ServerConfig returns no matches, and every rustls reference that does appear is either a client-side CryptoProvider installation or client-side handshake-error classification."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/Cargo.toml"
      - "crates/buzz-acp/src/relay.rs"
      - "grep_recursive(pattern='bind_rustls|TlsAcceptor|tls_rustls|axum_server|rustls::ServerConfig', scope='crates/', include='*.rs') -> zero matches at the recorded revision; the separate rustls search returns 67 matches across 9 files, every one a CryptoProvider install or a client handshake-error match"
    confidence: 0.9
  - statement: "SECURITY.md's 'Transport Security' section states: 'All production deployments should terminate TLS at the relay or a reverse proxy in front of it. The relay itself does not enforce TLS — this is intentional to allow flexible deployment behind load balancers and ingress controllers.'"
    entry_class: FACT
    evidence:
      - "SECURITY.md"
  - statement: "The 'at the relay' half of SECURITY.md's sentence is not reachable with the shipped binary — there is no configuration path that gives buzz-relay a certificate or a TLS listener — so for how the system currently behaves, ADR-0029's rule that executable evidence outranks documentation makes the code authoritative and leaves that clause a documentation defect rather than an available deployment option."
    entry_class: INFERENCE
    evidence:
      - "SECURITY.md"
      - "crates/buzz-relay/src/main.rs"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
    confidence: 0.85
  - statement: "RELAY_URL is read as std::env::var(\"RELAY_URL\").unwrap_or_else(|_| \"ws://localhost:3000\".to_string()) with no parsing and no scheme check, while BUZZ_PAIRING_RELAY_URL — loaded in the immediately following statement of the same function — is parsed with url::Url::parse and rejected with ConfigError::InvalidValue unless its scheme is ws or wss and it carries a host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "Two auth helpers derive their expected-URL scheme from RELAY_URL's literal prefix: nip42_expected_relay_url returns \"wss\" when config_relay_url starts with \"wss://\" and \"ws\" otherwise, and nip98_expected_url returns \"https\" under the same condition and \"http\" otherwise — in both cases the host comes from the resolved TenantContext, never from RELAY_URL."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "buzz-auth's NIP-42 comparison does not normalize the scheme: its private normalize_relay_url folds localhost and ::1 to 127.0.0.1 and strips a trailing slash and nothing else, and verify_nip42_event returns AuthError::RelayUrlMismatch whenever normalize_relay_url(relay) differs from normalize_relay_url(relay_url)."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "A deployment fronted by TLS termination but left on RELAY_URL's ws:// default therefore rejects every NIP-42 AUTH event from a client that correctly signs the wss:// URL it connected to, because the relay computes a ws:// expected URL and the scheme difference survives both sides' normalization."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-auth/src/nip42.rs"
    confidence: 0.85
  - statement: "The same prefix test appears a third time in relay_url_for_tenant_host, which picks wss or ws for the relay URL advertised in a NIP-05 response, using the configured scheme with the per-tenant host substituted."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/nip05.rs"
  - statement: "verify_nip98_event's doc comment instructs its caller that for reverse-proxy deployments the expected_url parameter should be reconstructed from X-Forwarded-Proto and X-Forwarded-Host before being passed in."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip98.rs"
  - statement: "The relay does not follow that instruction: nip98_expected_url builds its scheme from RELAY_URL's literal prefix and its host from the resolved TenantContext, and across every .rs file under crates/ the sole occurrence of any forwarded-header, Strict-Transport-Security or Set-Cookie name is that one doc comment — so no code reads a proxy-supplied transport indication, and nip11_or_ws_handler correspondingly takes the client address from ConnectInfo<SocketAddr>, the terminating proxy's socket rather than the end client's."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-auth/src/nip98.rs"
      - "crates/buzz-relay/src/router.rs"
      - "grep_recursive(pattern='x-forwarded|forwarded-proto|forwarded_for|real-ip|strict-transport|hsts|Set-Cookie', scope='crates/', include='*.rs', ignore_case=true) -> exactly one match at the recorded revision, the nip98.rs doc comment"
    confidence: 0.85
  - statement: "On the single-host Compose profile, TLS termination is a separate container: compose.caddy.yml adds a caddy:2-alpine service publishing ${CADDY_HTTP_PORT:-80} and ${CADDY_HTTPS_PORT:-443}, resets the relay's own published ports with ports: !reset [], and mounts a Caddyfile whose entire content is a {$BUZZ_DOMAIN} site block doing reverse_proxy relay:3000; run.sh layers that overlay in only when BUZZ_COMPOSE_TLS=true."
    entry_class: FACT
    evidence:
      - "deploy/compose/compose.caddy.yml"
      - "deploy/compose/Caddyfile"
      - "deploy/compose/run.sh"
  - statement: "On Kubernetes the chart emits .Values.ingress.tls verbatim into the Ingress spec's tls field and ships that value as an empty list in values.yaml, so the chart routes TLS configuration through to the cluster's ingress controller without provisioning, issuing or renewing any certificate itself."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/templates/ingress.yaml"
      - "deploy/charts/buzz/values.yaml"
  - statement: "The chart's worked TLS example uses cert-manager with a Let's Encrypt HTTP-01 ClusterIssuer and states in its own header comment that the chart neither manages the ClusterIssuer nor depends on cert-manager — 'that is a cluster operator decision'."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/examples/ingress-cert-manager.yaml"
  - statement: "values.yaml documents relayUrl as 'Required. The wss:// URL clients use to connect', but the chart's only enforcement is that it is non-empty (buzz.validate fails with 'relayUrl is required'), and buzz.relayHost then strips any of wss://, ws://, https:// or http:// before taking the first path segment — so the chart accepts all four schemes and never checks that the one chosen matches whether an ingress will terminate TLS."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/values.yaml"
      - "deploy/charts/buzz/templates/_validate.tpl"
      - "deploy/charts/buzz/templates/_helpers.tpl"
  - statement: "Outbound TLS is configured through dependency features rather than through relay code: the workspace manifest gives sqlx tls-rustls, redis tokio-rustls-comp, reqwest rustls, kube rustls-tls, opentelemetry-otlp tls-ring and tokio-tungstenite rustls-tls-webpki-roots, while the rust-s3 dependency carrying tokio-rustls-tls is declared per-crate in buzz-relay's own manifest rather than in the workspace one."
    entry_class: FACT
    evidence:
      - "Cargo.toml"
      - "crates/buzz-relay/Cargo.toml"
  - statement: "Whether an individual outbound connection actually uses TLS is decided by the URL an operator supplies, not by the relay: the chart's sample Secret sets DATABASE_URL with ?sslmode=require, and BUZZ_PUSH_GATEWAY_DELIVERY_URL is the one outbound URL whose scheme the relay validates, rejecting anything that is not an exact HTTPS /v1/deliveries/apns URL."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz/examples/secret-sample.yaml"
      - "crates/buzz-relay/src/config.rs"
  - statement: "Issue #1133 requires exactly one hand-authored canonical corpus document for this subject, with any newly discovered second concept filed as its own task rather than folded in."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1133 definition of done"
relationships:
  - type: references
    target: architecture-deployment-single-relay
  - type: references
    target: architecture-deployment-kubernetes
  - type: references
    target: architecture-deployment-hosted-topology
  - type: references
    target: layers-configuration-relay-configuration
  - type: references
    target: implementation-crates-buzz-auth
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: verification-security-authentication
  - type: references
    target: governance-security-policy
---

# TLS

**The Buzz relay does not terminate TLS.** Every listener the `buzz-relay` process
opens is a plaintext TCP socket (or a Unix domain socket), and no build, flag or
environment variable turns any of them into a TLS listener. Transport encryption for
Buzz is terminated by a separate component in front of the relay — a reverse proxy, an
ingress controller or a load balancer — and the relay's only awareness of that fact is
a single configured string it never validates.

Read this node for what the relay itself does and does not do about transport
encryption. Read the deployment nodes for *where* the terminating component sits in
any particular topology; this node deliberately does not restate that.

## Definition

TLS, in the Buzz system, is a property of the network hop **in front of** the relay,
not a feature of the relay. Concretely, at the recorded revision:

- `serve()` binds the application router with
  `tokio::net::TcpListener::bind(&config.bind_addr)`, the health probe with
  `tokio::net::TcpListener::bind(("0.0.0.0", config.health_port))`, and — when
  `BUZZ_UDS_PATH` is set — a `tokio::net::UnixListener`. Each is handed to
  `axum::serve` unwrapped. There is nothing between the accepted socket and the router.
- `serve()`'s own doc comment draws the process's four listeners as TCP and UDS, never
  as TLS.
- The workspace contains no server-side TLS acceptor at all. Searching every `.rs`
  file under `crates/` for `bind_rustls`, `TlsAcceptor`, `tls_rustls`, `axum_server`
  and `rustls::ServerConfig` returns nothing.

**`rustls` in the relay is a client, not a server.** `buzz-relay`'s explicit `rustls`
dependency exists so that `main()` can install a process-level `CryptoProvider` before
the first *outbound* TLS connection; the crate's own comment names the reason as
`rediss://` (ElastiCache), and `main()`'s comment names `rediss://`, `wss://` and "S3
over TLS". Seeing `rustls` in `Cargo.toml` is the single easiest way to reach the wrong
conclusion about this subject.

**Do not confuse this with "Buzz does not use TLS."** Production Buzz is expected to be
reached over `wss://` — the chart's own `relayUrl` comment calls it "Required. The
`wss://` URL clients use to connect." The distinction is *who holds the certificate*:
never the relay process.

## Use cases

Reach for this node when:

- **You are configuring a deployment.** Knowing that the relay terminates nothing tells
  you the certificate is your ingress's or proxy's job, and that `RELAY_URL`'s scheme is
  a claim you are making about that proxy which nothing will check for you.
- **Every client fails to authenticate against a working relay.** The URL-mismatch
  failure below looks like an auth bug and is a TLS-posture misconfiguration; that
  mapping is the single most expensive thing on this page to not know.
- **You are reading `SECURITY.md` or a `rustls` dependency and drawing a conclusion.**
  Both point the wrong way on their own, and both are addressed explicitly here.
- **You are proposing a change that assumes the relay can see transport state** — the
  client's real IP, whether the request arrived over TLS, a `Secure` cookie. It cannot,
  and the reasons are enumerated below.

## What the relay does do about TLS

Exactly one thing: it reads the **scheme** of `RELAY_URL` as a deployment-wide
declaration of TLS posture, and uses it to build the URLs that authentication
comparisons are made against.

| Consumer | Derivation | Consequence |
|---|---|---|
| `nip42_expected_relay_url` | `wss://` prefix → `wss`, otherwise `ws` | The scheme of the URL a NIP-42 AUTH event's `relay` tag must match |
| `nip98_expected_url` | `wss://` prefix → `https`, otherwise `http` | The scheme of the URL a NIP-98 `u` tag must match |
| `relay_url_for_tenant_host` | `wss://` prefix → `wss`, otherwise `ws` | The scheme of the relay URL advertised in a NIP-05 response |

In all three the **host** comes from the resolved tenant, not from `RELAY_URL` — only
the scheme is taken from configuration.

**This flag is unvalidated, and getting it wrong fails closed and silently.**
`RELAY_URL` is loaded with a bare `std::env::var(...).unwrap_or_else(...)` defaulting
to `ws://localhost:3000` — no parse, no scheme check. The very next statement in the
same function parses `BUZZ_PAIRING_RELAY_URL` and refuses to start unless it is a
`ws://` or `wss://` URL with a host, so the asymmetry is a gap in one setting rather
than an absent convention.

The failure mode follows from `buzz-auth`'s comparison. Its `normalize_relay_url` folds
`localhost` and `::1` to `127.0.0.1` and strips a trailing slash — and leaves the
scheme alone. `verify_nip42_event` then rejects with `AuthError::RelayUrlMismatch` on
any difference. So a deployment correctly fronted by TLS termination, but left on the
`ws://` default, computes a `ws://` expected URL while every client signs the `wss://`
URL it actually connected to, and **every** NIP-42 AUTH fails — with an error that
names a URL mismatch, not a TLS misconfiguration. The AUTH exchange itself is owned by
`architecture-flows-websocket-authentication`; what belongs here is that its scheme
input is a TLS-posture setting nothing checks.

## What the relay does not do about TLS

- **It does not read any proxy-supplied transport indication — though its own auth
  crate says it should.** `verify_nip98_event`'s doc comment tells callers that "for
  reverse-proxy deployments" the expected URL should be reconstructed from
  `X-Forwarded-Proto` / `X-Forwarded-Host` before being passed in. The relay's caller
  does not do that: `nip98_expected_url` takes the scheme from `RELAY_URL`'s prefix and
  the host from the resolved tenant. That doc comment is in fact the **only** place any
  forwarded-header, `Strict-Transport-Security` or `Set-Cookie` name appears in any
  `.rs` file under `crates/` — advice, never an implementation.
- **It does not emit transport-security response headers.** No
  `Strict-Transport-Security`, and no `Set-Cookie` at all — Buzz authenticates with
  signed Nostr events, so there is no session cookie whose `Secure` attribute would
  need setting.
- **It cannot see the end client's address.** `nip11_or_ws_handler` takes the peer from
  `ConnectInfo<SocketAddr>`, which behind a terminating proxy is the proxy's socket.
- **It does not refuse plaintext.** There is no "require TLS" mode; a relay reached
  directly over `ws://` behaves identically to one reached through a terminating proxy,
  except for the scheme its auth comparisons expect.

## Where termination actually happens

The in-repo deployment surfaces show it, and every one of them puts the certificate in
a component the relay never sees. **Those nodes own the topology; the rows below exist
only to say which node to read:**

| Surface | Terminator | Owned by |
|---|---|---|
| Single-host Compose | An optional `caddy:2-alpine` container publishing 80/443, layered in by `BUZZ_COMPOSE_TLS=true`, which resets the relay's own published ports to nothing and reverse-proxies to `relay:3000` | `architecture-deployment-single-relay` |
| Kubernetes | The cluster's ingress controller, via `.Values.ingress.tls` passed through verbatim into the `Ingress` spec | `architecture-deployment-kubernetes` |
| Hosted / GitOps | An `nginx` `IngressClass` with cert-manager-issued certificates | `architecture-deployment-hosted-topology` |

Two properties of that arrangement are this node's, not theirs:

1. **The chart issues no certificates.** `ingress.tls` ships as an empty list, and the
   worked cert-manager example states in its own header that the chart neither manages
   the `ClusterIssuer` nor depends on cert-manager — "that is a cluster operator
   decision."
2. **Nothing cross-checks the scheme against the topology.** The chart's only
   `relayUrl` validation is that it is non-empty; `buzz.relayHost` then strips any of
   `wss://`, `ws://`, `https://` or `http://` before taking the host. A chart install
   with `ingress.tls` populated and `relayUrl: ws://...` renders cleanly and produces
   the silent AUTH failure described above.

## Outbound TLS

The relay is a TLS **client** in several directions, and this is configured entirely
through dependency features — the workspace manifest gives `sqlx` `tls-rustls`, `redis`
`tokio-rustls-comp`, `reqwest` `rustls`, `kube` `rustls-tls`, `opentelemetry-otlp`
`tls-ring` and `tokio-tungstenite` `rustls-tls-webpki-roots`, and `buzz-relay`'s own
manifest adds `rust-s3` with `tokio-rustls-tls`. Whether a given connection is
encrypted is then decided by
the URL an operator supplies (`postgres://…?sslmode=require`, `rediss://…`,
`https://…`), not by relay code. The one exception is
`BUZZ_PUSH_GATEWAY_DELIVERY_URL`, which the relay validates as an exact HTTPS
`/v1/deliveries/apns` URL and refuses otherwise — the only place the relay enforces TLS
on anything.

## Scope and omissions

**This node covers** where transport encryption is terminated for Buzz, that the relay
process terminates none of it, the one TLS-relevant input the relay does consume
(`RELAY_URL`'s scheme) and what a mismatch costs, what the relay explicitly does not do
(proxy headers, transport headers, plaintext refusal), and the shape of the relay's
outbound TLS.

**It does not cover, and these are boundaries rather than silence:**

| Not covered here | Owned by |
|---|---|
| Which container or ingress object sits in front of the relay in each topology | `architecture-deployment-single-relay`, `architecture-deployment-kubernetes`, `architecture-deployment-hosted-topology` |
| The full `RELAY_URL` configuration entry alongside every other relay setting | `layers-configuration-relay-configuration` |
| The NIP-42 AUTH exchange as a flow | `architecture-flows-websocket-authentication` |
| The NIP-42 verification implementation | `implementation-crates-buzz-auth` |
| What the `RelayUrlMismatch` rejection path is actually tested by | `verification-security-authentication` |
| Security disclosure, scanning and review process | `governance-security-policy` |
| TLS in the desktop, mobile and web clients | Not established — no client-side transport node was identified at the recorded revision |

**The terminating component is genuinely outside this repository.** In a real
deployment the certificate, the cipher suites, the TLS version floor, the HSTS policy
and the renewal schedule all live in an nginx/Caddy/cloud-load-balancer configuration
this repository does not contain. `deploy/compose/Caddyfile` and
`deploy/charts/buzz/examples/ingress-cert-manager.yaml` are the closest things to a
terminator config in-tree, and neither is what a hosted deployment actually runs. That
is a real gap, not an omission this node could close by reading more of the repo.

**Expected but not verified when this node was written:**

- **No test asserts that the relay has no TLS listener**, and none asserts the
  `RELAY_URL`-scheme-to-AUTH-failure path end to end. The unit tests in
  `crates/buzz-relay/src/api/bridge.rs` pin that `nip42_expected_relay_url` and
  `nip98_expected_url` derive scheme from config and host from tenant; nothing exercises
  a deployment whose configured scheme disagrees with its actual termination. Searched
  for one and did not find it.
- **The two negative findings above rest on searches, not on a file that states them.**
  "No server-side TLS acceptor exists" and "no proxy transport header is read" are
  classified `INFERENCE` for exactly that reason: a search proves absence only as well
  as its own patterns cover the space.
- **Whether the `nip98.rs` doc comment describes an intended-but-unbuilt behaviour or a
  stale instruction was not established.** No issue, ADR or commit explaining the gap
  between that advice and `nip98_expected_url`'s actual derivation was found, and the
  question is not resolved here.
- **`SECURITY.md` contradicts the code and was not fixed here.** Its "terminate TLS at
  the relay or a reverse proxy in front of it" offers an option the binary does not
  implement. This node records the discrepancy under ADR-0029's precedence rule; the
  documentation fix is a separate change and is not made here.
- **No live deployment was inspected.** Everything above is read from source and from
  the in-repo deployment surfaces at the recorded revision. What the cohort's actual
  hosted relay terminates TLS with, and on what TLS version, was not checked.

---
id: layers-networking-relay-url
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
  - statement: "verify_nip42_event reads the AUTH event's relay tag and accepts it only when normalize_relay_url of that tag equals normalize_relay_url of the URL the caller passed as expected, returning AuthError::RelayUrlMismatch both when the tag is absent and when the two normalized forms differ."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "normalize_relay_url parses its input with the url crate and returns the input string unchanged when parsing fails, rewrites a host of exactly localhost or ::1 to 127.0.0.1, trims trailing / characters from the path, and returns the re-serialized URL — it applies no case-folding, port-elision or trailing-dot handling of its own beyond whatever the url crate's own parse-and-serialize does."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "nip42.rs's own unit tests assert that ws://localhost:3030 and ws://127.0.0.1:3030 normalize equal and that wss://relay.example.com/ and wss://relay.example.com normalize equal, and cover a wrong-relay rejection; no test in that module exercises the ::1 branch or the parse-failure fallback."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
  - statement: "The relay does not pass its configured URL to verification: handlers/auth.rs computes the expected URL as nip42_expected_relay_url(&state.config.relay_url, &conn.tenant) and passes that to AuthService::verify_auth_event, which forwards it to verify_nip42_event on a blocking thread."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/auth.rs"
      - "crates/buzz-auth/src/lib.rs"
  - statement: "nip42_expected_relay_url takes only the scheme from the configured relay URL — wss when the trimmed string starts with the literal wss://, ws otherwise — and formats scheme://{tenant.host()}, so the configured URL's host, port and path never reach the comparison."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "bridge.rs's own doc comment states the rationale: verifying against the deployment-wide config.relay_url both admits an AUTH event signed against community A's host on a connection bound to community B and rejects every legitimate AUTH whose tenant host is not the single configured one, and names this the WebSocket sibling of the NIP-98 conformance row 44 obligation."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "bridge.rs's unit tests pin both directions of that rule — changing the tenant host changes the expected URL while changing the config host does not — pin the wss/ws scheme derivation, and assert that an AUTH event signed for host A is rejected with RelayUrlMismatch on a connection whose tenant resolved to host B even when the config URL is host A."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
  - statement: "crates/buzz-test-client/tests/nip42_host_binding_live.rs is an #[ignore]d live two-host proof of the same rule, requiring a running multi-tenant relay with two seeded communities and asserting that a relay tag naming host A is rejected on a connection to host B."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/nip42_host_binding_live.rs"
  - statement: "The relay loads its own URL from the RELAY_URL environment variable with the fallback ws://localhost:3000, and applies no parse or scheme validation to it — unlike BUZZ_PAIRING_RELAY_URL in the same function, which is rejected at startup unless it parses as a ws:// or wss:// URL with a host."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The two places that describe RELAY_URL disagree with each other: .env.example comments it as the public WebSocket URL used in NIP-42 auth challenges, while config.rs's doc comment on the same field calls it the public WebSocket URL of this relay, advertised in NIP-11."
    entry_class: FACT
    evidence:
      - ".env.example"
      - "crates/buzz-relay/src/config.rs"
  - statement: "The NIP-11 document's relay_self field carries the relay's own signing pubkey in hex rather than a URL, and the only path by which config.relay_url reaches NIP-11 is push_descriptor, which reads its wss:// prefix for a scheme and takes the host from the tenant bound to the request."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/nip11.rs"
  - statement: "The configured URL's authority is used outside the per-request paths: main.rs derives the deployment community's host from it with relay_url_authority at startup, failing fast when that authority is empty and relay membership is required, and operator.rs compares an archive request's host against the same derived authority to refuse archiving the deployment community."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/api/operator.rs"
  - statement: "main.rs's fatal startup message names the variable BUZZ_RELAY_URL when reporting that no community host could be derived, while the value it describes is loaded from RELAY_URL in config.rs."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/main.rs"
      - "crates/buzz-relay/src/config.rs"
  - statement: "relay_url_authority extracts the host with url::Host (re-adding IPv6 brackets), appends an explicit port when present, and passes the result through normalize_host, which ASCII-lowercases, strips a single :443 or :80 suffix and strips a single trailing dot; neither function contains any localhost-to-127.0.0.1 equivalence, and an unparseable URL yields the empty string on which callers fail closed."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs"
  - statement: "Because tenant resolution and the AUTH relay-tag check normalize hosts with two different functions, localhost and 127.0.0.1 are a single URL to the AUTH check but two distinct community hosts to tenant resolution, so on a deployment that had seeded both loopback spellings as separate communities an AUTH event signed for one would satisfy a connection bound to the other."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-auth/src/nip42.rs"
      - "crates/buzz-core/src/tenant.rs"
      - "crates/buzz-relay/src/api/bridge.rs"
    confidence: 0.6
  - statement: "Because the expected scheme is a deployment-wide flag read from RELAY_URL's literal prefix rather than from the connection that arrived, a relay left on the ws://localhost:3000 default behind TLS termination computes a ws:// expected URL while its clients connect over wss:// and sign wss://, so every NIP-42 AUTH on that deployment fails with RelayUrlMismatch."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-relay/src/api/bridge.rs"
      - "crates/buzz-relay/src/config.rs"
      - "crates/buzz-ws-client/src/connection.rs"
    confidence: 0.75
  - statement: "A client's relay tag is the connect URL it was handed, verbatim: NostrWsConnection::connect stores url.to_string(), authenticate passes that stored string to build_auth_event, and build_auth_event parses it with RelayUrl::parse and hands it to EventBuilder::auth."
    entry_class: FACT
    evidence:
      - "crates/buzz-ws-client/src/connection.rs"
      - "crates/buzz-ws-client/src/message.rs"
  - statement: "BUZZ_RELAY_URL is a client-side variable whose default scheme differs by binary — buzz-cli defaults it to http://localhost:3000 and treats it as an HTTP base URL, while the ACP harness defaults it to ws://localhost:3000 — and buzz-cli derives its WebSocket URL from it with to_ws_url, a substring replacement of https:// with wss:// and http:// with ws://."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/src/lib.rs"
      - "crates/buzz-acp/src/config.rs"
      - "crates/buzz-cli/src/client.rs"
  - statement: ".env.example states explicitly that the relay itself uses RELAY_URL and that BUZZ_RELAY_URL is the ACP harness's connection target, noting that the two happen to point at the same place in local development."
    entry_class: FACT
    evidence:
      - ".env.example"
relationships:
  - type: references
    target: architecture-flows-websocket-authentication
  - type: references
    target: verification-security-authentication
  - type: references
    target: layers-configuration-relay-configuration
  - type: references
    target: implementation-crates-buzz-auth
  - type: references
    target: implementation-crates-buzz-ws-client
  - type: references
    target: verification-formal-multi-tenant-auth
  - type: references
    target: layers-data-postgres-communities-table
---

# The relay URL

A **relay URL** is the `ws://` or `wss://` address at which a Buzz relay is reached —
the string a client dials, and the string a client asserts, under signature, that it
believes it is talking to.

That second role is what makes it a security concept rather than a configuration
detail. NIP-42 authentication is not only "prove you hold this key"; it is "prove you
hold this key *and* that you meant to present it to **this** relay." The AUTH event
carries a `relay` tag naming the URL the client dialled, the relay checks that tag
against the URL it believes it is serving, and a mismatch is rejected. Without that
check, a hostile relay could forward its victim's challenge to a real relay and replay
the victim's signed AUTH event there — the substitution attack the tag exists to stop.

## Definition, and what it is not

The relay URL is a **scheme plus authority** — `wss://relay.example.com`,
`ws://a.localhost:3100` — with no meaningful path component. Three things share the
name and are not the same value:

| Name | Who reads it | What it means |
|---|---|---|
| `RELAY_URL` | the relay process | the relay's *own* URL, as configured |
| `BUZZ_RELAY_URL` | clients — the CLI, the ACP harness | the URL a client *dials* |
| the AUTH `relay` tag | the relay, at verification | the URL a client *claims* it dialled |

`BUZZ_RELAY_URL` is not a second spelling of `RELAY_URL`. `.env.example` says so
directly, and their defaults do not even agree on a scheme: the ACP harness defaults it
to `ws://localhost:3000`, while `buzz-cli` defaults it to `http://localhost:3000` and
treats it as an HTTP base URL, converting to `ws`/`wss` only when it opens a WebSocket
(`to_ws_url`, a substring replacement). Read the variable's owner before reading its
value.

The relay URL is also **not the tenant host**. On this multi-tenant relay a connection
resolves to a community from its request `Host` header, and it is *that* host — not
the configured URL — the AUTH check compares against. The rest of this node is largely
about the consequences of that separation.

## What the relay actually reads from `RELAY_URL`

This is the part most likely to be assumed wrongly. `RELAY_URL` is loaded in
`crates/buzz-relay/src/config.rs` with the fallback `ws://localhost:3000`, and — unlike
`BUZZ_PAIRING_RELAY_URL` a few lines below it, which fails startup unless it parses as
a `ws`/`wss` URL with a host — it is never parsed or validated at load. What happens to
it afterwards splits cleanly in two:

**Its scheme is a per-request flag.** `nip42_expected_relay_url` reads whether the
trimmed string starts with the literal `wss://`, yielding `wss` or `ws`, and then
formats `scheme://{tenant.host()}`. The host, port and path of the configured URL never
reach the NIP-42 comparison at all. The sibling `nip98_expected_url` does the same for
HTTP, mapping `wss://` to `https` and everything else to `http`; so does
`push_descriptor` when it builds the NIP-11 push `origin`. In all three the configured
URL contributes exactly one bit — TLS posture — and the authority comes from the
connection.

**Its authority is a startup and operator value.** `main.rs` derives the deployment
community's host from it with `relay_url_authority`, seeding that community before any
membership backfill and failing fast when the derived authority is empty and relay
membership is required; `operator.rs` compares an archive request's host against the
same derived authority to refuse archiving the deployment community.

Neither of the two prose descriptions of the variable captures this. `.env.example`
calls it *"used in NIP-42 auth challenges"* and `config.rs`'s doc comment on the same
field calls it *"advertised in NIP-11"*. The first overstates: only its scheme reaches
NIP-42. The second is inaccurate as written — NIP-11's `relay_self` field is the
relay's signing **pubkey**, not a URL, and the only route by which the configured URL
touches NIP-11 is the push descriptor's scheme.

## The comparison rule, exactly

For a WebSocket connection bound to tenant `T`, the relay accepts an AUTH event's
`relay` tag if and only if:

```
normalize_relay_url(tag)  ==  normalize_relay_url("<ws|wss>://" + T.host())
```

where the scheme is `wss` when `RELAY_URL` starts with the literal `wss://` and `ws`
otherwise, and `T.host()` is already `normalize_host`-normalized.

`normalize_relay_url` (in `crates/buzz-auth/src/nip42.rs`) does four things, in order:

1. **Parse with the `url` crate.** If parsing fails, the *input string is returned
   unchanged* — the comparison then degrades to a byte-exact match rather than
   erroring.
2. **Collapse loopback spellings.** A host of exactly `localhost` or `::1` is rewritten
   to `127.0.0.1`.
3. **Strip trailing slashes** from the path.
4. **Re-serialize**, inheriting whatever normalization the `url` crate performs at
   parse time (ASCII case-folding of scheme and host, elision of a default port).

Scheme is therefore compared and a `ws`/`wss` mismatch is fatal; host case and a
default port are not. There is no `Host`-header-derived escape hatch and no wildcard:
`crates/buzz-relay/src/api/bridge.rs` pins both directions in unit tests — changing the
tenant's host changes the expected URL, changing the configured host does not — and
asserts that an event signed for host A is rejected with `RelayUrlMismatch` on a
connection bound to host B *even when the configured URL is host A*, which is precisely
the attacker-knowable case.

## Two normalizers, one concept

Buzz normalizes "the same" host twice, in two crates, by two different rules. This is
the single most useful thing to know about the relay URL, because neither function's
name warns you about the other.

| | `normalize_relay_url` (`buzz-auth`) | `normalize_host` / `relay_url_authority` (`buzz-core`) |
|---|---|---|
| Used for | the AUTH `relay` tag check | tenant resolution, community seeding |
| `localhost` ≡ `127.0.0.1` ≡ `::1` | **yes** | **no** — three distinct hosts |
| trailing FQDN dot (`relay.example.`) | not handled explicitly | **stripped** |
| `:80` / `:443` | elided by the `url` crate | **stripped** explicitly |
| ASCII case | folded by the `url` crate | folded explicitly |
| IPv6 brackets | via `url` re-serialization | **re-added explicitly**, because `url::Host` drops them |
| unparseable input | returned verbatim | empty string, callers fail closed |

The loopback row is the one with teeth. A deployment that had seeded both
`localhost:3000` and `127.0.0.1:3000` as separate communities would have two distinct
tenants that the AUTH check cannot tell apart — an AUTH event signed for one loopback
spelling satisfies a connection bound to the other. That is loopback-only and needs an
unusual seeding to reach, so it is a sharp edge rather than a live hole; it is recorded
here because the asymmetry is invisible from either function alone.

The scheme rule has a blunter consequence, and it is an operations one. Because the
expected scheme is a deployment-wide flag read from a configured string rather than
from the connection that actually arrived, a relay left on the `ws://localhost:3000`
default while sitting behind TLS termination will compute `ws://…` for every
connection, while its clients connect over `wss://` and sign `wss://…`. Every
authentication on that deployment fails with `RelayUrlMismatch`, and nothing at startup
warns about it — `RELAY_URL` is the one URL-shaped setting in that function with no
validation at all. **If NIP-42 is failing everywhere after a TLS change, check
`RELAY_URL`'s scheme first.**

## Where a client's claim comes from

A client does not compute the tag; it echoes what it was given. `NostrWsConnection`
stores the connect URL verbatim as a string, `authenticate` passes that stored string
to `build_auth_event`, and `build_auth_event` parses it with `RelayUrl::parse` before
`EventBuilder::auth` places it in the tag. So the tag is only ever as correct as the
URL the operator or the environment handed the client — which is why the two variables
above being different values, with different defaults, matters more than it looks.

## Scope and omissions

**This node covers** what a relay URL is, the three distinct values that share the
name, what the relay reads from its own configured URL, the exact rule by which a
NIP-42 `relay` tag is compared, and the divergence between the two host normalizers.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The NIP-42 handshake sequence, its ordering and its error-to-response mapping | `architecture-flows-websocket-authentication` |
| NIP-42's verification obligations and which of them are covered by which tests | `verification-security-authentication` |
| The `RELAY_URL` row in the relay's environment-variable table, and every other relay setting | `layers-configuration-relay-configuration` |
| Multi-tenant host resolution and the community-binding seam as subjects in their own right | `verification-formal-multi-tenant-auth`, `layers-data-postgres-communities-table` |
| The NIP-98 HTTP expected-URL rule, which is a sibling of this check on a different transport | Not filed as its own corpus task at the recorded revision |
| The pairing relay's own URL (`BUZZ_PAIRING_RELAY_URL`), which is validated at startup and serves a different flow | Not filed as its own corpus task at the recorded revision |

**Expected but not verified when this node was written:**

- **No Rust code was compiled or executed.** Every claim above rests on reading source
  in this repository. Claims that depend on the `url` crate's own behaviour rather than
  on Buzz's code — that `Url::to_string()` folds host case, that it elides a default
  port for `ws`/`wss`, and what it does with a trailing FQDN root dot — were **not**
  confirmed against `url` 2.5.8. The trailing-dot row of the comparison table is
  therefore stated as "not handled explicitly" (what `nip42.rs` contains) rather than
  as a behavioural claim about the result.
- **The `::1` branch of `normalize_relay_url` was not shown to be reachable.** It
  compares `Url::host_str()` against the bare string `::1`, and whether `host_str()`
  yields `::1` or the bracketed `[::1]` for an IPv6 URL decides whether that branch
  ever fires. `crates/buzz-core/src/tenant.rs` asserts in a comment that `host_str()`
  strips IPv6 brackets, which would make it reachable, but that comment was not
  independently confirmed and **no test in `nip42.rs` exercises the branch** — the
  module's only loopback test uses `localhost`.
- **The parse-failure fallback was not exercised.** `normalize_relay_url` returning its
  input verbatim on an unparseable string is read from the code, not from a test; no
  test in `nip42.rs` passes it an unparseable URL.
- **The TLS-misconfiguration consequence was reasoned, not reproduced.** No relay was
  run behind TLS termination with a `ws://` `RELAY_URL` to observe the resulting
  `RelayUrlMismatch`; the claim is an INFERENCE from three files, at confidence 0.75.
- **The live two-host proof was not run.** `nip42_host_binding_live.rs` is `#[ignore]`d
  and needs a multi-tenant relay with two seeded communities; only its source was read.

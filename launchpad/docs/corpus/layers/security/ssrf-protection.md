---
id: layers-security-ssrf-protection
type: layers
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5."
    entry_class: FACT
    evidence:
      - "commit 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5"
  - statement: "`ActionDef::CallWebhook` is documented as an 'HTTP POST to an external URL' whose `url` field 'must be a public HTTPS endpoint', and `WorkflowDef::requires_elevated_authority` states in its own doc comment that it is 'True when any step performs an action that can exfiltrate channel data to an arbitrary external destination (`call_webhook`)' — the one workflow action that sends an outbound request to a URL an operator supplies in the workflow definition, as opposed to a fixed, deployment-configured endpoint."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/schema.rs:119-131"
      - "crates/buzz-workflow/src/schema.rs:149-161"
  - statement: "The `CallWebhook` dispatch arm in `WorkflowEngine::execute_from_step` calls `call_webhook_impl` only under `#[cfg(feature = \"reqwest\")]`; without that feature it logs and returns a `skipped: true` placeholder instead of making any request."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:638-667"
  - statement: "`crates/buzz-relay/Cargo.toml` depends on `buzz-workflow` with `features = [\"reqwest\"]` enabled, and `crates/buzz-workflow/Cargo.toml` wires that feature to the optional `reqwest` dependency (`reqwest = [\"dep:reqwest\"]`) — so in the relay binary that is actually built and deployed, `CallWebhook` takes the guarded HTTP path, not the compiled-out placeholder."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/Cargo.toml:65"
      - "crates/buzz-workflow/Cargo.toml:28"
      - "crates/buzz-workflow/Cargo.toml:31"
  - statement: "`check_ssrf(host, port)` resolves `host:port` to IP addresses using the OS resolver, run on a blocking threadpool via `tokio::task::spawn_blocking` so it does not block the async runtime; it returns an error if resolution itself fails or if resolution succeeds but yields zero addresses, and it returns an error naming the offending host and address if ANY resolved address is classified private/reserved by `is_private_ip` — only if every resolved address is public does it return `Ok` with the first validated address."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:774-811"
  - statement: "`is_private_ip` classifies an `IpAddr` as private/reserved for IPv4 loopback, private (`10/8`, `172.16/12`, `192.168/16`), link-local, the `0.x.x.x` unspecified range, broadcast, CGNAT (`100.64.0.0/10`, RFC 6598), and benchmarking (`198.18.0.0/15`, RFC 2544); and for IPv6 loopback, unspecified, ULA (`fc00::/7`), link-local (`fe80::/10`), multicast (`ff00::/8`), the RFC 3849 documentation range (`2001:db8::/32`), Teredo (`2001::/32`) and 6to4 (`2002::/16`) prefixes, plus IPv4-mapped, IPv4-compatible, NAT64 well-known (`64:ff9b::/96`), NAT64 local-use (`64:ff9b:1::/48`) and legacy SIIT-translated (`::ffff:0:0:0/96`) IPv6 forms — each of the last four resolved by recursively re-checking their embedded IPv4 address against the same IPv4 rules."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/network.rs:22-84"
  - statement: "`is_private_ip`'s own doc comment names the CGNAT range as blocked specifically because it is 'Dangerous in cloud environments (AWS, GCP) where CGNAT can route to metadata services' — the cloud-metadata SSRF target this guard is explicitly written to close, not merely an incidental range exclusion."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/network.rs:33-34"
  - statement: "`call_webhook_impl` builds a fresh, per-call `reqwest::Client` — deliberately not the shared pooled client used elsewhere — pinned via `.resolve(host, SocketAddr::new(safe_ip, port))` to the exact address `check_ssrf` already validated; the adjacent comment states this is 'required for SSRF safety: without pinning, reqwest performs its own DNS resolution which could return a different address than the one validated above (DNS rebinding TOCTOU)'."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:837-852"
  - statement: "The same per-call client disables the system HTTP proxy via `.no_proxy()` (a configured proxy would resolve the original hostname itself, bypassing the pinned address) and disables HTTP redirects via `.redirect(reqwest::redirect::Policy::none())`, with an adjacent comment stating 'a redirect to an internal host bypasses the SSRF check' — a redirect target is never re-validated by `check_ssrf`, so honoring one would silently undo the guard."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:845-852"
  - statement: "`call_webhook_impl` bounds two further properties of the response: a 10-second request timeout (`Client::builder().timeout(Duration::from_secs(10))`) and an incremental read of the response body via repeated `resp.chunk()` calls that aborts with an error the moment buffered bytes exceed `WEBHOOK_MAX_RESPONSE_BYTES` (1 MiB, `1024 * 1024`), rather than buffering an attacker-controlled response in full before checking its size."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:813-815"
      - "crates/buzz-workflow/src/executor.rs:843-844"
      - "crates/buzz-workflow/src/executor.rs:876-898"
  - statement: "`cargo test -p buzz-core --lib network::` reports 35 tests passed and 0 failed at the recorded revision, exercising `is_private_ip` against every blocked range named above (IPv4 loopback/private/link-local/unspecified/broadcast/CGNAT/benchmarking; IPv6 loopback/unspecified/ULA/link-local/multicast/documentation/NAT64/6to4/Teredo boundaries) and confirming public addresses in both families (`8.8.8.8`, `2606:4700::1`) are NOT classified private."
    entry_class: FACT
    evidence:
      - "cargo_test(package=buzz-core, module=network::tests, commit=338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) -> 35 passed; 0 failed; 0 ignored"
  - statement: "No test anywhere in the repository references `check_ssrf` or `call_webhook_impl` by name, and `crates/buzz-workflow/src/executor.rs`'s own `#[cfg(test)] mod tests` block contains no test constructing a `CallWebhook` step and asserting on its SSRF behavior against a real or mocked address; the only executed, passing test coverage for this invariant is `is_private_ip`'s own pure classification logic, not the DNS-resolve-then-pin-then-fetch integration built on top of it."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='check_ssrf|call_webhook_impl', scope='.', file_type='rs') -> matches only crates/buzz-workflow/src/executor.rs:649,782,818,837 (the definitions and their one call site), no test file"
  - statement: "Workflow definitions containing a `call_webhook` step additionally require the workflow owner to currently hold the `owner` or `admin` role in the destination channel before the definition may even be *saved*: `command_executor.rs`'s ingest handler calls `WorkflowDef::requires_elevated_authority()` and rejects with `forbidden: workflows with call_webhook actions require the owner or admin role` for any other role, failing closed (an internal error, not a silent pass) if the role lookup itself errors — this is an authorization control on who may configure an outbound-URL step at all, layered above and independent of the network-level SSRF guard this node documents, and is SEC-006's territory, not this node's."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/handlers/command_executor.rs:748-763"
      - "crates/buzz-workflow/src/schema.rs:149-161"
  - statement: "When `check_ssrf` (or any other failure inside `call_webhook_impl`) returns `Err`, `dispatch_action` propagates it via `?`, and `execute_steps` returns `Err((WorkflowError, PartialProgress))` with `step_index` set to the failing step and `trace` containing only the entries for steps completed before it — the run stops at the rejected `call_webhook` step rather than continuing to later steps, and no `StepResult::Completed` trace entry is ever recorded for it."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:1176-1211"
      - "crates/buzz-workflow/src/error.rs:5-15"
  - statement: "`WorkflowError::code()` classifies an SSRF rejection identically to any other outbound-request failure (a malformed URL, a DNS failure, a timeout) as the stable string `\"webhook_failed\"`, deliberately separate from the `Display`/diagnostic message that carries the specific host or address — the error module's own test, `workflow_error_codes_are_stable_and_separate_from_diagnostics`, asserts exactly this separation for a `WebhookError` carrying `\"secret-bearing detail\"` (`code()` does not contain that detail); a caller observing only the run-level code cannot distinguish an SSRF rejection from an ordinary webhook failure without the diagnostic message."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/error.rs:45-47"
      - "crates/buzz-workflow/src/error.rs:69-84"
      - "crates/buzz-workflow/src/error.rs:96-113"
  - statement: "`launchpad/docs/corpus/architecture/flows/workflow-execution.md` (merged, id `architecture-flows-workflow-execution`) already cites this same SSRF guard, in less detail, as one of four 'Trust-boundary crossings' supporting its own SEC-006 authority-gating claim — it does not present itself as the canonical SSRF-protection node, and this node does not restate its SEC-006 content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/flows/workflow-execution.md:320-326"
  - statement: "`buzz-media`'s source under `crates/buzz-media/src/` contains no outbound HTTP client construction and no fetch-by-URL code path (grepped for `reqwest`, `.get(` against a URL, `Url::parse`, and `http::` client usage); Blossom media handling is client-initiated upload/download of blob bytes the caller sends directly, not the relay fetching a client-supplied URL on its own."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='reqwest|Url::parse', scope='crates/buzz-media/src/*.rs') -> zero matches for outbound-request construction"
  - statement: "`buzz-push-gateway`'s APNs client sends to `production_base_url`/`sandbox_base_url`, which default to the hardcoded literal `https://api.push.apple.com` (or an equivalent sandbox constant) and are fixed at client construction, not read from any per-notification or per-request user-supplied field — push delivery is not a user-controlled-destination outbound-request surface."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs:110-128"
      - "crates/buzz-push-gateway/src/apns.rs:217-223"
  - statement: "The `AddReaction` workflow action also makes an outbound HTTP call (`add_reaction_impl`), but its destination is `{base_url}/api/messages/{message_id}/reactions` where `base_url` comes from the `BUZZ_RELAY_BASE_URL` environment variable (defaulting to `http://localhost:3000`) — an operator-configured loopback target fixed at deployment time, not a per-workflow user-supplied URL — so it is a different outbound-request surface than `call_webhook` and is out of scope for this node."
    entry_class: FACT
    evidence:
      - "crates/buzz-workflow/src/executor.rs:923-943"
  - statement: "Because DNS resolution happens once inside `check_ssrf` on a blocking threadpool and the resulting IP is then pinned directly into the `reqwest::Client` via `.resolve()` rather than the client re-resolving the hostname itself, the design closes the classic 'validate-then-refetch-by-hostname' TOCTOU window a naive check-then-connect implementation would leave open to DNS rebinding; this is a structural property read from the code rather than something confirmed by attempting a live DNS-rebinding attack against a running relay."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-workflow/src/executor.rs:837-852"
    confidence: 0.75
  - statement: "Issue #1178's definition of done requires this node to state the invariant as one unambiguous property using MUST/MUST NOT only where normative, explain its scope and the states/operations it applies to, name enforcement points and observable failure behavior, and link at least one verification/conformance mechanism or explicitly record that verification is missing."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1178 definition of done"
relationships:
  - type: references
    target: architecture-flows-workflow-execution
---

# SSRF protection on outbound workflow webhooks

## The invariant

When the relay executes a workflow's `call_webhook` step, it **MUST NOT** open a
connection to a target whose resolved IP address is private, loopback, link-local,
unspecified, broadcast, carrier-grade-NAT, benchmarking, or otherwise reserved. The
relay **MUST** resolve the target host and classify every resulting address *before*
connecting, and **MUST** pin the connection to the exact address it validated — a
hostname **MUST NOT** be re-resolved by the HTTP client after validation, and an
HTTP redirect returned by the destination **MUST NOT** be followed, because neither
a second resolution nor a redirect target is re-checked against the same
classification.

This is stated as one property because every enforcement point below exists to hold
the same guarantee at a different point in the request lifecycle: classify the
address, pin the connection to what was classified, and never let a later step in
the same request (client-side re-resolution, a followed redirect) substitute an
address that was never classified.

## Scope

**Applies to:** the `call_webhook` workflow action
(`ActionDef::CallWebhook` in `crates/buzz-workflow/src/schema.rs`), specifically its
dispatch arm and the `check_ssrf` / `call_webhook_impl` functions in
`crates/buzz-workflow/src/executor.rs`. This is the only workflow action, and the
only outbound-request surface found in this repository, whose network destination is
a URL an operator supplies in the workflow definition rather than a fixed,
deployment-configured endpoint. The relay's own production build compiles this path
in live (`crates/buzz-relay/Cargo.toml` enables `buzz-workflow`'s `reqwest`
feature) — it is not a stub only present in tests.

**Applies at:** every `call_webhook` step execution, unconditionally — there is no
allowlist, no distinction between first-party and third-party destination hosts, and
no bypass for a previously-successful call to the same URL (DNS can change between
calls, so a cached "already validated" result would reopen the rebinding window this
guard exists to close).

**Does not apply to, and are separate outbound-request surfaces:**

- **Media (Blossom) upload/download.** `crates/buzz-media/src` has no fetch-by-URL
  code path at all — the relay never fetches a client-supplied URL on its own; blob
  bytes are always sent directly by the uploading client. There is nothing here for
  an SSRF guard to protect.
- **Push notification delivery.** `buzz-push-gateway`'s APNs client sends to a
  hardcoded, deployment-fixed base URL (`https://api.push.apple.com` or its sandbox
  equivalent), never a per-notification or per-request user-supplied destination.
- **`AddReaction`'s internal HTTP call.** This workflow action also performs an
  outbound request (`add_reaction_impl`), but its destination is built from the
  `BUZZ_RELAY_BASE_URL` environment variable — an operator-configured loopback
  target fixed at deployment time — not a per-workflow user-supplied URL. A
  different surface, not covered here.
- **Who may configure a `call_webhook` step (SEC-006).** A separate,
  authorization-layer control requires the workflow owner to hold the `owner` or
  `admin` channel role before a definition containing `call_webhook` can even be
  saved (`crates/buzz-relay/src/handlers/command_executor.rs`). That gate gets its
  own canonical treatment in `architecture-flows-workflow-execution` (see
  *Relationships*) and is not restated here — this node covers only what happens to
  the network request once a `call_webhook` step is allowed to run.

## Enforcement points

| Point | What it does |
|---|---|
| `check_ssrf` (`crates/buzz-workflow/src/executor.rs:774-811`) | DNS-resolves `host:port` via the OS resolver off the async runtime (`spawn_blocking`); fails closed on a resolution error or zero addresses; rejects if **any** resolved address is private/reserved; returns the first validated address for pinning. |
| `is_private_ip` (`crates/buzz-core/src/network.rs:46-84`) | The classifier `check_ssrf` calls. Covers IPv4 loopback/private/link-local/unspecified/broadcast/CGNAT/benchmarking and IPv6 loopback/unspecified/ULA/link-local/multicast/documentation/NAT64/6to4/Teredo, including embedded-IPv4 forms checked recursively. |
| Per-call pinned client (`crates/buzz-workflow/src/executor.rs:843-852`) | A fresh (non-pooled) `reqwest::Client` built per request, resolved via `.resolve(host, SocketAddr::new(safe_ip, port))` to the already-validated address — closing the DNS-rebinding TOCTOU a shared, self-resolving client would reopen. |
| Proxy and redirect disabled (`crates/buzz-workflow/src/executor.rs:847,849`) | `.no_proxy()` prevents a configured system proxy from resolving the original hostname itself; `.redirect(Policy::none())` prevents a redirect response from sending the request to a second, unvalidated target. |
| Response bounds (`crates/buzz-workflow/src/executor.rs:813-815,843-844,876-898`) | A 10-second request timeout, plus an incremental `resp.chunk()` read loop that aborts once the buffered body exceeds `WEBHOOK_MAX_RESPONSE_BYTES` (1 MiB) rather than buffering an unbounded response first. |

## Observable failure behavior

A rejected target does not produce a `StepResult::Completed` with a non-2xx status —
it never reaches an HTTP exchange at all. `check_ssrf`'s error propagates through
`dispatch_action` and aborts the run at that step: `execute_steps` returns with the
failing step's index and a trace containing only the steps completed before it, so
the workflow run stops there rather than continuing to later steps. At the run
level, the error is classified by `WorkflowError::code()` as the stable string
`"webhook_failed"` — the same code any other outbound-request failure (a malformed
URL, a DNS failure, a request timeout) produces. The diagnostic detail — which host
or address triggered the rejection — lives only in the error's `Display` message,
deliberately kept separate from that stable code (verified by the error module's own
test for a webhook error carrying "secret-bearing detail"), so a caller relying on
the run-level code alone cannot distinguish an SSRF rejection from an ordinary
webhook failure without also having access to the diagnostic message.

## Consequence of violation

If any of these points were removed or bypassed, a workflow's `call_webhook` step —
configurable by any channel owner/admin, per the SEC-006 gate noted in *Scope* —
could direct the relay to make outbound HTTP requests, from inside the deployment's
own network position, to addresses the operator never intended to expose: loopback
services on the relay host itself, other internal services on the deployment's
private network, or cloud provider metadata endpoints. `is_private_ip`'s own doc
comment calls out this last case explicitly for the CGNAT range it blocks — "Dangerous
in cloud environments (AWS, GCP) where CGNAT can route to metadata services" — the
canonical SSRF outcome (credential or configuration exfiltration via a cloud
metadata service) this guard exists to close. A working redirect-based bypass would
have the same effect via a destination that answers the first request cleanly, then
redirects to an internal target the code never re-validates.

## Verification

`is_private_ip`'s classification logic is unit-tested exhaustively: `cargo test -p
buzz-core --lib network::` reports **35 passed, 0 failed** at the recorded revision,
covering every blocked range named in *Enforcement points* above in both address
families, plus the embedded-IPv4 recursive forms (IPv4-mapped, IPv4-compatible,
NAT64 well-known and local-use, and the translated-prefix form), and confirming two
representative public addresses (`8.8.8.8`, `2606:4700::1`) are correctly *not*
classified private.

**This does not cover the integration this node actually documents.** No test in
this repository — in `buzz-workflow`'s own `#[cfg(test)] mod tests`, or in
`buzz-test-client`'s integration suite — references `check_ssrf` or
`call_webhook_impl` by name, or constructs a `CallWebhook` step and exercises it
against a real or mocked private-IP target. What is verified above is the pure
classifier `check_ssrf` depends on; the DNS-resolve-then-pin-then-fetch sequence
built on top of it — including whether the pinned `.resolve()` call, the disabled
proxy/redirect settings, and the incremental body cap actually behave as the code
reads — has no automated test and is, at this revision, verified only by reading
the source directly. That is an open verification gap, not a claim this node makes
that the integration is tested.

## Relationships

- **references** `architecture-flows-workflow-execution` — the merged flow node
  that documents workflow execution end to end and cites this same SSRF guard, at
  lower detail, as one of four trust-boundary crossings supporting its own SEC-006
  authority-gating claim. This node is the deeper, canonical treatment of the SSRF
  guard itself; the flow node's citation of it is supporting context, not a
  duplicate claim this node needs to reconcile with.

## Scope and omissions

**This node covers:** the SSRF invariant on the `call_webhook` workflow action —
its statement as one property, the surface it applies to, each enforcement point at
the current revision, what breaks if the guard is bypassed, and what is and is not
verified by an automated test today.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Who may configure a `call_webhook` step at all (SEC-006 owner/admin gate) | `architecture-flows-workflow-execution` |
| Workflow execution end to end (triggers, templating, step dispatch, suspension/approval) | `architecture-flows-workflow-execution` |
| The webhook *inbound* trigger path (`/hooks/{id}`, shared-secret authentication) | Not yet documented as its own corpus node |
| Media upload/download and push notification delivery in general | Not this node's subject — see *Scope* for why they are excluded |

**Expected but not verified when this node was written:**

- **No automated test exercises `check_ssrf` or `call_webhook_impl` end to end.**
  See *Verification* above — this is the primary open gap, recorded rather than
  rounded up from the classifier's own test coverage.
- **Whether a live DNS-rebinding attempt against a running relay is actually
  defeated by the pinned `.resolve()` call was not attempted.** The INFERENCE in
  the evidence ledger above reasons from the code's structure (resolve once, pin
  the result) that the TOCTOU window is closed, but this was not empirically
  tested against a live attack.
- **Whether every possible SSRF vector (e.g. IPv6 zone IDs, unusual URL schemes,
  or non-HTTP redirect-adjacent behavior in `reqwest` itself) is covered was not
  independently audited beyond what `is_private_ip`'s own range table and the
  `call_webhook_impl` code path show.**

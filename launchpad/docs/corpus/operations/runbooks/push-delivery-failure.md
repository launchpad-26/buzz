---
id: operations-runbooks-push-delivery-failure
type: operations
status: draft
origin: launchpad
audiences:
  - operator
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 473205a7457b208455f188847bfb27b01aa83cac."
    entry_class: FACT
    evidence:
      - "commit 473205a7457b208455f188847bfb27b01aa83cac"
  - statement: "buzz-push-gateway is a standalone binary crate, built from its own Dockerfile.push-gateway rather than the relay image, and has its own Helm chart under deploy/charts/buzz-push-gateway; it creates only its own six push_gateway_* authority tables plus SQLx's migration-history table, never relay migrations."
    entry_class: FACT
    evidence:
      - "Dockerfile.push-gateway"
      - "deploy/charts/buzz-push-gateway/Chart.yaml"
      - "docs/push-gateway-deployment.md"
  - statement: "The relay-side push delivery path is: buzz-relay/src/push_runtime.rs runs a continuous matcher over accepted events, enqueues a durable 'wake' per matching lease, and a delivery worker (deliver_one) revalidates the wake, re-checks channel membership and the community serving lease, then POSTs a delivery capability to the configured gateway URL and interprets its HTTP response."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "crates/buzz-push-gateway/src/apns.rs's classify() function maps an APNs HTTP status code and reason string to exactly five outcomes: Accepted (200), InvalidEndpoint (410 Unregistered, with APNs' unregistered_at timestamp when supplied), ConfigurationFault (400 BadDeviceToken/DeviceTokenNotForTopic, 403, or 429 TooManyProviderTokenUpdates), Retry (429/500/503 or IdleTimeout/InternalServerError/ServiceUnavailable/Shutdown/TooManyRequests, plus any transport-level send error), and PermanentRequestFault (everything else)."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "apns.rs's own comment states that 400 BadDeviceToken and DeviceTokenNotForTopic are deliberately classified as ConfigurationFault rather than InvalidEndpoint because both codes are ambiguous with a deployment profile mistake (environment or topic mismatch); only 410 Unregistered crosses the permanent endpoint-invalidation boundary, so a ConfigurationFault never causes an endpoint to be disabled."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/apns.rs"
  - statement: "On the relay side, push_runtime.rs's retry_or_fail gives up after MAX_ATTEMPTS = 8 attempts (marking the wake 'exhausted'); until then it schedules the next attempt after delay * 2^(attempt-1), with the exponent clamped to at most 6, so the backoff multiplier grows 1x, 2x, 4x ... up to 64x before the wake is retried again."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "The gateway exposes exactly seven Prometheus series: push_gateway_apns_send_attempts_total (counter, no labels, recorded before every transport call), push_gateway_apns_deliveries_total (counter, label outcome in {accepted, invalid_endpoint, retry, configuration_fault, permanent_request_fault}), push_gateway_apns_delivery_seconds (histogram, APNs round-trip latency), push_gateway_admissions_total (counter, label result in {admitted, rejected, unavailable}), push_gateway_delivery_errors_total (counter, label class, a closed set of static exit-class strings), push_gateway_reaper_failures_total (counter, no labels), and push_gateway_readiness_failures_total (counter, label cause in {not_accepting, authority})."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "push_gateway_delivery_errors_total is intentionally narrow: crates/buzz-push-gateway/src/http.rs's deliver() handler records it only for post-admission exit classes -- invalid_grant, rate_limited, temporarily_unavailable (all at the authorize_delivery admission seam), profile_mismatch, profile_disabled, token_custody (endpoint-token decrypt failure), and finish_failed (detached disposition task failed or was cancelled) -- not for enrollment, delegation, rotation, or revocation handler failures."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "On the relay side, push_runtime.rs and main.rs together emit: buzz_push_enabled (gauge, 1 only when the deployment opt-in is active), buzz_push_match_jobs_total (counter, result in {matched, unmatched, error, context_error}), buzz_push_wakes_total (counter, result), buzz_push_wake_enqueue_errors_total (counter, no labels), buzz_push_wake_queue_seconds and buzz_push_match_queue_seconds (histograms), buzz_push_gateway_requests_total and buzz_push_gateway_request_seconds (transport seam to the gateway), and buzz_push_deliveries_total (counter, outcome in a closed set including accepted, retry, exhausted, suppressed, invalid_endpoint, replay_terminal, failed, worker_error, and configuration_error)."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
      - "crates/buzz-relay/src/main.rs"
  - statement: "GET /metrics is served only on the gateway's private health router (BUZZ_PUSH_HEALTH_ADDR, default 0.0.0.0:8081), and only when a PrometheusHandle is passed to router_with_metrics -- it is never reachable on the public router (BUZZ_PUSH_BIND_ADDR, default 0.0.0.0:8080) that serves enrollment, delegation, and delivery requests."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "The gateway's /_readiness handler fails closed for two distinct, separately counted reasons: the process is draining and no longer accepting traffic (ReadinessFailure::NotAccepting, label cause=not_accepting), or the PostgreSQL authority store's own readiness check returned an error (ReadinessFailure::Authority, label cause=authority). /_liveness always reports alive and does not consult the authority store."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
      - "crates/buzz-push-gateway/src/metrics.rs"
  - statement: "deliver()'s admission step maps AuthorityError::Rejected to HTTP 404 invalid_grant, AuthorityError::RateLimited to HTTP 429 rate_limited, and AuthorityError::Unavailable to HTTP 503 temporarily_unavailable, recording the matching push_gateway_admissions_total{result=...} and, for RateLimited and Unavailable, a push_gateway_delivery_errors_total{class=...} entry as well."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/http.rs"
  - statement: "On the relay side, deliver_one's response handling is not symmetric: a gateway 503 or 429 response, or a transport timeout/connect error, goes through retry_or_fail (bounded retry with backoff); a 410 response disables the endpoint when its generation matches and marks the wake failed (not retried); a 404 after more than one attempt is treated as a replay of an already-terminal request and marked complete; every other response status -- including a 401 from a NIP-98 authorization mismatch (for example a relay whose BUZZ_PUSH_GATEWAY_DELIVERY_URL does not match the gateway's expected audience) or a 400 invalid_request -- falls through to the generic branch that marks the wake failed outright, with no retry."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/push_runtime.rs"
  - statement: "The gateway requires, among other environment variables, BUZZ_PUSH_GRANT_KEYS, BUZZ_PUSH_TOKEN_KEYS, BUZZ_PUSH_PUBLIC_DELIVERY_URL (must be exactly https://push.buzz.xyz/v1/deliveries/apns), BUZZ_PUSH_DOGFOOD_APP_ATTEST_APP_ID, BUZZ_PUSH_DOGFOOD_APNS_CERT_PATH, BUZZ_PUSH_DOGFOOD_APNS_TOPIC, BUZZ_PUSH_APP_ATTEST_ROOT_CERT_PATH, and DATABASE_URL; BUZZ_PUSH_DOGFOOD_APNS_ENVIRONMENT defaults to production if unset and is rejected if set to anything other than production or sandbox. Only variable names are named here; no value is reproduced."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/config.rs"
  - statement: "On the relay, push is an explicit deployment opt-in: BUZZ_PUSH_ENABLED defaults to false, and BUZZ_PUSH_GATEWAY_DELIVERY_URL, when set, must be an exact HTTPS URL with path /v1/deliveries/apns and no credentials, query, or fragment; when unset it resolves to the canonical https://push.buzz.xyz/v1/deliveries/apns."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/config.rs"
  - statement: "The gateway's retention reaper runs once at startup and then every 300 seconds (5 minutes); a failed sweep increments push_gateway_reaper_failures_total and logs a warning, but does not stop the process, so a single transient failure self-heals on the next tick."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs"
  - statement: "On shutdown, the gateway flips an 'accepting' flag to false (causing /_readiness to start failing with cause=not_accepting), stops accepting new public-listener connections, waits up to 30 seconds for in-flight requests to drain, then stops the health listener and aborts the reaper task."
    entry_class: FACT
    evidence:
      - "crates/buzz-push-gateway/src/main.rs"
  - statement: "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml ships exactly five alerting rules, gated behind prometheusRule.enabled (disabled by default, per the standard Helm '{{- if .Values.prometheusRule.enabled }}' guard): PushGatewayConfigurationFault (any configuration_fault rate over 5m, for 10m, critical), PushGatewayAdmissionUnavailable (any admission unavailable rate over 5m, for 5m, critical), PushGatewayReadinessAuthorityFailing (any authority readiness-failure rate over 5m, for 5m, warning), PushGatewayReaperFailing (reaper failures increase >= 2 over 30m, for 5m, warning), and PushGatewayHighApnsRetryRate (retry fraction over a 10m window above a configurable threshold, default 0.25, gated on a minimum sample count, default 20, held for 15m, warning)."
    entry_class: FACT
    evidence:
      - "deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml"
  - statement: "No PrometheusRule, alert, or equivalent alerting configuration exists anywhere else in this repository for the relay-side buzz_push_* metrics (buzz_push_enabled, buzz_push_match_jobs_total, buzz_push_wakes_total, buzz_push_wake_enqueue_errors_total, buzz_push_gateway_requests_total, buzz_push_deliveries_total): the only PrometheusRule template in the repository is the gateway's own, and it defines rules over push_gateway_* series exclusively; deploy/charts/buzz's relay chart carries no PrometheusRule at all."
    entry_class: INFERENCE
    evidence:
      - "grep(alert:, deploy/) -> only deploy/charts/buzz-push-gateway/templates/prometheusrule.yaml; find(-iname *prometheusrule*) -> only that same file; deploy/charts/buzz has no templates/prometheusrule.yaml"
    confidence: 0.85
  - statement: ".github/workflows/docker.yml gates both push-gateway-build and push-gateway-merge (the jobs that build and then publish ghcr.io/block/buzz-push-gateway) behind 'if: github.repository == ...block/buzz...', with an inline comment on the build job reading: 'Launchpad does not operate the separate APNs gateway. Preserve the inherited lane for upstream while preventing fork publication attempts.'"
    entry_class: FACT
    evidence:
      - ".github/workflows/docker.yml"
  - statement: "Because this fork's CI cannot build or publish the production push-gateway image, and this repository contains no credentials, cluster access, or deployment workflow for a real push.buzz.xyz environment, this fork cannot itself execute the Kubernetes rollout-restart, key-rotation, or image-verification mitigations that docs/push-gateway-deployment.md documents for a live incident -- those apply to whichever environment Block operates from an image built by the upstream block/buzz repository, not to this fork."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/docker.yml"
      - "docs/push-gateway-deployment.md"
    confidence: 0.8
  - statement: "docs/push-gateway-deployment.md documents rollback as: setting BUZZ_PUSH_ENABLED=false on the affected relays stops lease advertisement, lease acceptance, matching, workers, and new gateway traffic without deleting credentials or mutating existing leases; existing leases and gateway authorities then expire naturally; if the gateway itself is unhealthy, disable the gateway deployment only after relay delivery has already been turned off."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "docs/push-gateway-deployment.md states that Kubernetes does not restart pods when a referenced Secret's bytes change, so AEAD-key or APNs-certificate rotation requires an explicit rolling restart after the secret manager update, followed by readiness verification before removing predecessor keys."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "docs/push-gateway-deployment.md states that APNs acceptance of a delivery cannot prove device presentation, and recommends recording a small manual physical-device sample with event-created, banner-visible, and notification-tap timestamps, verifying that the visible content came from fetched, signature-verified relay content and that the tap opened the exact triggering message."
    entry_class: FACT
    evidence:
      - "docs/push-gateway-deployment.md"
  - statement: "As of this node's recorded revision, the capabilities-notifications-push-notification node reports that neither mobile/lib nor desktop/src contains any code that creates, rotates, or revokes a push lease, performs Apple App Attest enrollment, or references kind:30350 -- the client half of NIP-PL exists only as spec text, not as shipped Buzz client code, so real end-to-end delivery failures are necessarily scoped to the single compiled-in xyz.block.buzz.dogfood.mobile identity described in docs/push-gateway-deployment.md, not a general Buzz client population."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/capabilities/notifications/push-notification.md"
  - statement: "This node was written using launchpad/docs/corpus/templates/runbook.md, which was already merged on origin/launchpad at the recorded revision and directs a runbook's body to carry, in order, a trigger, severity and impact, diagnosis, mitigation and resolution, escalation, and a scope-and-omissions section, grounded in the Google SRE Workbook's playbook definition."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/runbook.md"
relationships:
  - type: implements
    target: corpus-template-runbook
  - type: references
    target: capabilities-notifications-push-notification
  - type: references
    target: architecture-containers-push-gateway
  - type: references
    target: architecture-flows-push-notification
  - type: references
    target: layers-observability-prometheus
---

# Runbook: push delivery failure

Push notifications (APNs wakes delivered through `buzz-push-gateway` on behalf of
a NIP-PL push lease) are not reaching the devices they are meant to wake. This
node is the concrete realization of
[`corpus-template-runbook`](../../templates/runbook.md) for that one failure
mode, following its five required sections plus scope-and-omissions.

**Who this is for, read first.** This repository is `launchpad-26/buzz`, a
fork. `.github/workflows/docker.yml` gates the jobs that build and publish
`ghcr.io/block/buzz-push-gateway` behind `github.repository == 'block/buzz'`,
with a comment on the build job stating plainly that "Launchpad does not
operate the separate APNs gateway" and that the fork-gate exists to prevent
publication attempts from here. This fork cannot build, publish, or roll out
the production gateway image, and this repository holds no credentials or
cluster access for a real `push.buzz.xyz` deployment. Concretely: the
diagnosis steps below (reading metrics, logs, and code) are fully usable in
any environment running these crates, including a local or staging deployment
raised from this repository; the mitigation steps that assume a live
production `push.buzz.xyz` (a `kubectl rollout restart`, a secret-manager key
rotation, an `oci://ghcr.io/block/buzz-push-gateway` digest verification) are
Block-operated actions this fork cannot itself perform and are described here
for completeness and for use against a self-hosted deployment, not as
something an agent or operator in this fork can execute against the real
service.

## Trigger

Two distinct trigger paths exist, because alerting is opt-in:

1. **One of the gateway's five Prometheus alerts fires**, if the deployment
   has set `prometheusRule.enabled=true` on the `buzz-push-gateway` Helm
   chart (it is disabled by default):
   - `PushGatewayConfigurationFault` — any `configuration_fault` outcome rate
     over 5 minutes, sustained 10 minutes (critical).
   - `PushGatewayAdmissionUnavailable` — any admission `unavailable` rate
     over 5 minutes, sustained 5 minutes (critical).
   - `PushGatewayReadinessAuthorityFailing` — any readiness failure with
     `cause=authority`, rate over 5 minutes, sustained 5 minutes (warning).
   - `PushGatewayReaperFailing` — reaper failures increasing by 2 or more
     within 30 minutes, sustained 5 minutes (warning).
   - `PushGatewayHighApnsRetryRate` — the retryable fraction of APNs
     attempts over a 10-minute window exceeds `apnsRetryRatioThreshold`
     (default `0.25`), above a minimum sample count (`apnsRetryMinSamples`,
     default `20`), sustained 15 minutes (warning).
2. **A report that notifications are not arriving, with no alert firing.**
   Because alerting is disabled by default and no relay-side `buzz_push_*`
   alert exists in this repository at all (see *Scope and omissions*), the
   more common trigger in this repository's current state is a bug report or
   manual observation, not a page. In that case, start from the gateway's
   `/metrics` (served only on its private health listener,
   `BUZZ_PUSH_HEALTH_ADDR`, default `0.0.0.0:8081`) and the relay's own
   Prometheus endpoint, per *Diagnosis* below.

## Severity and impact

Impact is bounded by NIP-PL's own design: a push wake is a fixed
"reconnect" instruction, never event content, so a delivery failure means a
device does not promptly reconnect and fetch new messages — it does not mean
messages are lost, corrupted, or delivered to the wrong recipient. Severity
varies by which failure mode is active:

- **`PushGatewayConfigurationFault` (critical).** APNs is rejecting every (or
  most) delivery attempts for a certificate, topic, or environment reason.
  No endpoint is being invalidated, but nothing is delivering — every
  in-flight wake queues for the relay's own bounded retry (see
  *Diagnosis*) and eventually exhausts.
- **`PushGatewayAdmissionUnavailable` (critical).** The gateway's
  PostgreSQL authority store — the transactional fence for replay and
  quota admission across all replicas — is unreachable. New deliveries are
  rejected at admission before ever reaching APNs.
- **`PushGatewayReadinessAuthorityFailing` (warning, escalates toward
  critical as it persists).** Replicas are being pulled out of the Service
  by their own readiness probe. If enough replicas fail this simultaneously,
  it degrades into a full outage of the delivery path.
- **`PushGatewayReaperFailing` (warning).** A slow-burn condition: expired
  reservations and rows are not being swept, growing a bounded-until-expiry
  window and leaking storage. Not itself a delivery outage.
- **`PushGatewayHighApnsRetryRate` (warning).** Per the alert's own
  description, deliveries are delayed, not lost.
- **Relay-side exhaustion with no alert.** A wake that exhausts its 8
  attempts (see *Diagnosis*) on one relay is invisible to every alert in
  this repository — there is no relay-side equivalent of the gateway's
  `PrometheusRule`. Sustained, silent exhaustion is a real failure this
  runbook's *Trigger* path 2 exists to catch.

## Diagnosis

1. **Confirm the relay actually has push enabled.** `BUZZ_PUSH_ENABLED`
   defaults to `false`; if it is `false` for the relay in question, the
   absence of deliveries is expected behavior by design, not a failure.
   Check the relay's own `buzz_push_enabled` gauge (`1` only when the
   opt-in is active) before treating anything else as a symptom.
2. **Localize the failure to relay, gateway, or transport.** Read the
   relay's Prometheus endpoint in order along the pipeline:
   `buzz_push_match_jobs_total{result=...}` (is the matcher seeing and
   matching events at all?) → `buzz_push_wakes_total{result=...}` (are
   wakes being enqueued, or rejected as `duplicate`/`inactive_lease`?) →
   `buzz_push_gateway_requests_total` /
   `buzz_push_gateway_request_seconds` (is the relay reaching the gateway's
   transport seam at all?) → `buzz_push_deliveries_total{outcome=...}`
   (the terminal outcome distribution: `accepted`, `retry`, `exhausted`,
   `suppressed`, `invalid_endpoint`, `replay_terminal`, `failed`,
   `worker_error`, `configuration_error`).
3. **If requests are reaching the gateway, read its own `/metrics`**
   (`GET /metrics` on `BUZZ_PUSH_HEALTH_ADDR`, never on the public
   `BUZZ_PUSH_BIND_ADDR`): `push_gateway_admissions_total{result=...}` for
   the `authorize_delivery` fence outcome, `push_gateway_apns_deliveries_total{outcome=...}`
   for the terminal APNs classification, and
   `push_gateway_delivery_errors_total{class=...}` for the narrow set of
   post-admission exit classes (`invalid_grant`, `rate_limited`,
   `temporarily_unavailable`, `profile_mismatch`, `profile_disabled`,
   `token_custody`, `finish_failed`) — this metric does not cover
   enrollment, delegation, rotation, or revocation handler failures.
4. **Check `/_readiness` on the gateway** if admissions show
   `unavailable`: a `not_ready` response with `cause=authority` confirms the
   PostgreSQL authority store's own readiness check is failing, not a
   transient blip; `cause=not_accepting` instead means the process is mid
   graceful-shutdown, not unhealthy.
5. **Read the outcome class, not just "it failed."** APNs classification
   (`crates/buzz-push-gateway/src/apns.rs`) distinguishes:
   - `invalid_endpoint` (410 Unregistered) — this specific device token is
     dead; expected under normal churn, not a systemic incident.
   - `configuration_fault` (400 `BadDeviceToken`/`DeviceTokenNotForTopic`,
     403, or 429 `TooManyProviderTokenUpdates`) — by design, no endpoint is
     invalidated for this class, because both 400 reasons are ambiguous
     with a server-side certificate/topic/environment mistake rather than a
     genuinely dead token. A sudden, broad shift to this class points at
     the APNs credential, topic, or environment configuration, not at
     device churn.
   - `retry` (429/500/503, or `IdleTimeout`/`InternalServerError`/
     `ServiceUnavailable`/`Shutdown`/`TooManyRequests`, or any transport
     send error) — transient; correlate with
     `PushGatewayHighApnsRetryRate`'s ratio if alerting is enabled.
   - `permanent_request_fault` — the locally generated request itself was
     malformed; more likely a code defect than an operator-actionable
     condition.
6. **On the relay side, distinguish retried from unretried failures.**
   `deliver_one`'s response handling only retries a gateway 503, a 429, or
   a transport timeout/connect error (via `retry_or_fail`, bounded to 8
   attempts with exponential backoff — delay multiplied by `2^(attempt-1)`,
   clamped at `2^6`). A 410 disables the endpoint (when the generation
   matches) and does not retry. A 404 after more than one attempt is
   treated as a replay of an already-terminal request. **Every other
   status — including a 401 from a NIP-98 authorization mismatch (for
   example, a relay's `BUZZ_PUSH_GATEWAY_DELIVERY_URL` not matching the
   audience the gateway expects) or a 400 `invalid_request` — is marked
   failed immediately, with no retry at all.** A misconfigured delivery
   URL on the relay therefore does not show up as a retry storm; it shows
   up as a steady `failed` count with no corresponding gateway-side signal,
   because the gateway rejects the request before `authorize_delivery` ever
   runs.
7. **Confirm the relay's configured gateway URL.**
   `BUZZ_PUSH_GATEWAY_DELIVERY_URL`, if set, must be an exact HTTPS URL
   with path `/v1/deliveries/apns` and no credentials, query, or fragment;
   left unset, it resolves to the canonical
   `https://push.buzz.xyz/v1/deliveries/apns`. A relay pointed at the wrong
   gateway, or a gateway whose own `BUZZ_PUSH_PUBLIC_DELIVERY_URL` does not
   match, produces the unretried-failure pattern in step 6.
8. **A reaper failure is a distinct, slower-burn signal**, not a delivery
   outage by itself: it runs once at startup and then every 5 minutes;
   a single failed sweep self-heals on the next tick and only warrants
   attention once it recurs (the alert's own threshold is 2 failures within
   30 minutes).

## Mitigation and resolution

- **`configuration_fault` dominating the outcome distribution.** The APNs
  certificate, topic, or environment configuration is unhealthy. In an
  environment this fork can operate directly (e.g. a local or self-hosted
  deployment), correct the `BUZZ_PUSH_DOGFOOD_APNS_CERT_PATH` /
  `BUZZ_PUSH_DOGFOOD_APNS_TOPIC` / `BUZZ_PUSH_DOGFOOD_APNS_ENVIRONMENT`
  configuration (names only — no value is reproduced here) and restart the
  gateway; Kubernetes does not restart pods when a referenced Secret's
  bytes change on their own, so a rotation needs an explicit rolling
  restart, followed by verifying `/_readiness` before removing any
  predecessor key. Against the real `push.buzz.xyz`, this is a Block-owned
  action this fork cannot perform — see *Escalation*.
- **`push_gateway_admissions_total{result="unavailable"}` or
  `push_gateway_readiness_failures_total{cause="authority"}`.** The
  PostgreSQL authority store is unreachable. Because all replicas share one
  database transactionally, restarting gateway replicas alone does not fix
  a database outage — restore database connectivity first. This is
  infrastructure/DBA-owned work, not a gateway code or config change.
- **`PushGatewayReaperFailing`.** Check database write availability; a
  single failed sweep is expected to self-heal on its next 5-minute tick,
  so act only once the recurrence threshold (2 failures within 30 minutes)
  is met.
- **`PushGatewayHighApnsRetryRate` / a rising `retry` outcome fraction.**
  Per the alert's own description this means deliveries are delayed, not
  lost. No repository-defined mitigation exists beyond the relay's own
  bounded exponential backoff (up to 8 attempts) already running; this
  runbook does not invent an additional manual mitigation the repository
  does not implement.
- **Relay-side wakes reaching `exhausted` with no alert visible.** Because
  no relay-side `PrometheusRule` exists in this repository (see *Scope and
  omissions*), an operator must query
  `buzz_push_deliveries_total{outcome="exhausted"}` directly rather than
  wait for a page. There is no repository-defined automatic remediation for
  an exhausted wake beyond what already ran; a recurring pattern of
  exhaustion for the same installation points back at steps 3–7 of
  *Diagnosis* for the underlying cause.
- **A misconfigured `BUZZ_PUSH_GATEWAY_DELIVERY_URL` (unretried `failed`
  outcomes with no matching gateway-side signal).** Correct the relay's
  `BUZZ_PUSH_GATEWAY_DELIVERY_URL` (or unset it to fall back to the
  canonical URL) and redeploy the relay.
- **Rollback, without touching credentials or leases.** Set
  `BUZZ_PUSH_ENABLED=false` on the affected relay(s). This stops lease
  advertisement, lease acceptance, matching, the delivery worker, and new
  gateway traffic; existing leases and gateway authorities then expire
  naturally. If the gateway itself is unhealthy, disable the gateway
  deployment only after relay delivery has already been turned off, so a
  half-disabled state does not leave relays retrying against a gateway that
  is intentionally down.

## Escalation

- **This fork cannot action a real `push.buzz.xyz` incident directly.**
  `.github/workflows/docker.yml` gates the gateway's image build and
  publish jobs to `github.repository == 'block/buzz'`, with an explicit
  comment stating the fork-gate exists specifically to prevent this fork
  from publishing that image. For a production incident on the real
  service, escalation is to whoever operates Block's deployment of the
  image built from `block/buzz` — outside this fork's repository and
  authority. This runbook remains directly usable here for local/staging
  reproduction of the same crates and for code-level diagnosis.
- **A suspected defect in the shared crates** (for example, in
  `apns.rs`'s classification, `push_runtime.rs`'s retry/backoff logic, or
  either crate's config validation) is contribution work: escalate as an
  issue or PR against `block/buzz` through the normal upstream contribution
  path, since a fix benefits both the real production deployment and any
  use of these crates from this fork.
- **No escalation timer, on-call rotation, or paging destination for push
  delivery is defined anywhere in this repository.** How long a responder
  should attempt the steps above alone before escalating is not established
  here — see *Scope and omissions*.

## Verification of recovery

- If alerting is enabled, confirm the firing alert(s) have cleared.
- Confirm `push_gateway_apns_deliveries_total{outcome="accepted"}` is
  incrementing again and that `configuration_fault` / `retry` rates have
  fallen back to their prior baseline.
- Confirm the relay's `buzz_push_deliveries_total{outcome="accepted"}` is
  incrementing again and that `exhausted` / `failed` counts have stopped
  growing.
- Confirm `/_readiness` returns `ready` on every gateway replica.
- Recovery of the metrics above does not by itself prove a device
  presented a notification. Per `docs/push-gateway-deployment.md`, APNs
  acceptance is not proof of device delivery; where physical confirmation
  matters, record a small manual sample of event-created,
  banner-visible, and notification-tap timestamps against the specific
  `xyz.block.buzz.dogfood.mobile` build and confirm the visible content and
  tap target came from the fetched, signature-verified relay content.

## Scope and omissions

**This runbook covers** the delivery path only — matching, waking, and
transporting an already-issued delivery capability from a relay through
`buzz-push-gateway` to APNs — its metrics, its response classification, its
retry/backoff behavior, its opt-in alerting, and its rollback procedure.

**It does not cover, and this is a boundary, not a gap:**

| Not covered here | Owner |
|---|---|
| Installation enrollment, delegation, endpoint rotation, and revocation (the `challenge`/`enroll`/`delegate`/`rotate_endpoint`/`revoke_*` handlers) — a device/App Attest identity problem, not a delivery-path problem | Not owned by any node merged at this node's recorded revision; a neighbouring concern this runbook only cites in passing |
| Client-side notification presentation once APNs has accepted a delivery (banner rendering, the Notification Service Extension) | The mobile client, outside these two crates |
| Whether a runbook may itself trigger `buzz-workflow` automation rather than only describe manual steps | Left open by `corpus-template-runbook` itself, not settled here |

**Expected but could not verify when this node was written:**

- **Whether any alert on the relay-side `buzz_push_*` metrics exists
  anywhere outside this repository.** Within this repository, a search
  (`grep` for `alert:` under `deploy/`, and a filename search for
  `*prometheusrule*`) found exactly one `PrometheusRule` template, the
  gateway's own, and it defines rules over `push_gateway_*` series only;
  `deploy/charts/buzz` (the relay's own chart) carries no `PrometheusRule`
  at all. This runbook cannot confirm whether Block's own operational
  tooling outside this repository fills that gap.
- **Whether an App Attest root-certificate mismatch actually fails gateway
  startup.** `docs/push-gateway-deployment.md` states that it does; this
  was not independently re-verified by reading
  `crates/buzz-push-gateway/src/app_attest.rs`'s startup path for this
  node, since App Attest enrollment sits outside this runbook's delivery-path
  scope.
- **Whether the alerts this node describes are wired to any real receiver
  or paging destination.** This repository's chart defines the
  `PrometheusRule` object only; no Alertmanager routing or receiver
  configuration is present anywhere in this repository to check.
- **Real-world timing for the mitigations against a live `push.buzz.xyz`
  deployment** (for example, how long a rolling restart or a database
  failover actually takes) — this fork has no access to that environment
  to measure it, per the *Escalation* section above.

# Delivering browser telemetry without an internet-exposed collector

**Title:** How browser OTLP/RUM telemetry is normally delivered without exposing an unauthenticated collector
**Summary:** Four approaches exist and only one authenticates, because a browser cannot hold a secret — API keys and CORS are anti-spam controls, not authentication. OpenTelemetry's own security guidance does not cover the exposed case at all; its answer is "bind to localhost". For Buzz the answer is unusually cheap: the web client is served by the relay, so a same-origin path needs no CORS, no new public endpoint, and reuses NIP-42 — and it is the only option compatible with a collector that has no public address.
**Tags:** `observability` `browser` `otlp` `faro` `security` `cors` `rum`
**Reviewed:** 2026-08-22 · **Answers:** [#321](https://github.com/launchpad-26/buzz/issues/321)

---

## Finding

**Four approaches exist, and only one of them actually authenticates.** A browser cannot hold a secret, so the API keys and bearer tokens that look like authentication are anti-spam speed bumps. Real authentication comes from putting the telemetry endpoint on an origin that already knows who the user is.

**OpenTelemetry's own security guidance does not cover this case.** Its answer to "how do I expose a receiver safely" is "don't" — bind to `localhost`. Everything past approach A below is practitioner consensus, not specification, and the cohort should know that before relying on it.

**For Buzz the answer is unusually easy**, because the web client is served by the relay. A same-origin path needs no CORS, adds no internet-facing service, reuses NIP-42, and is the only one of the four compatible with a collector on a maintainer's laptop.

---
## The four approaches

### A. Harden the receiver in place — Grafana Alloy `faro.receiver`

First-party for the chosen stack, and it ships the controls already. Defaults, from the component reference:

| Argument | Default |
|---|---|
| `listen_address` | `"127.0.0.1"` |
| `listen_port` | `12347` |
| `cors_allowed_origins` | `[]` |
| `api_key` | `""` |
| `max_allowed_payload_size` | `"5MiB"` |
| `rate_limiting.enabled` | `true` |
| `rate_limiting.rate` | `50` |
| `rate_limiting.burst_size` | `100` |

Rate limiting is **on by default** (token bucket, 50/s refill, 100 burst) and the bind address is **loopback by default** — both good defaults. Authentication is off by default:

> *"When the `api_key` argument is non-empty, client requests must have an HTTP header called `X-API-Key` matching the value of the `api_key` argument. Requests that are missing the header or have the wrong value are rejected with an `HTTP 401 Unauthorized` status code."* — and when empty, *"no authentication checks are performed, and the `X-API-Key` HTTP header is ignored."*

**What it cannot express:** the `api_key` is shipped to the browser, so anyone who opens devtools has it. It raises the cost of casual abuse; it does not authenticate. `cors_allowed_origins` is likewise a browser-enforced control — it stops *other pages* using the endpoint, not a script with `curl`.

### B. Reverse proxy in front of the collector

The practitioner consensus, and the OpenTelemetry blog's own recommendation for web applications:

> *"It is recommended that you do not expose your collector directly, but that you put a reverse proxy (NGINX, Apache HTTP Server, …) in front of it. The reverse proxy can take care of SSL-offloading, setting the right CORS headers, and many other features specific to web applications."*

The same source flags a subtlety that matters if anyone reaches for gRPC: *"given that gRPC connections are typically long-lived, the HTTP authentication could potentially become obsolete while the connection is still open. A more secure solution would be to validate the authentication data on a per-RPC basis."* Not a browser concern — browsers cannot speak OTLP/gRPC — but it disqualifies the relay's transport from being reused here.

**What it cannot express:** the proxy still has no way to know *who* the browser is, unless it shares a session with something that does. It moves the TLS and CORS problem, not the identity problem.

### C. Backend-for-frontend — the browser never talks to the collector

The browser posts telemetry to the application's own origin, which forwards it. This is the only option where the request carries a real identity, because it rides the session the app already established.

The hardening literature recommends it together with short-lived tokens rather than as an alternative — mint at `/auth/rum-token` on your own origin before initialising the SDK.

**What it cannot express:** nothing about authentication — this is the strong option. Its costs are elsewhere: the app server is now on the telemetry path, and telemetry volume becomes load on it.

### D. Short-lived, origin-bound tokens

The middle path, and the sharpest formulation of the whole problem I found:

> *"Browser ingest cannot hold a long-lived secret, but it can hold a short-lived token issued by your origin."*

Mint a ~15-minute JWT server-side, bound to the user's session and the page origin, and pass it where the SDK expects an API key. Real authentication, no standing secret in the page.

**What it cannot express:** it needs an origin that can mint tokens — so it presupposes most of C. It is C's authentication step, usable when you want the browser to keep talking to the collector directly.

---

## Where the sources disagree, or say nothing

**OpenTelemetry's official security guidance is silent on the exposed case.** I fetched it looking for reverse-proxy, CORS and public-exposure guidance and it contains none. What it says is the opposite:

> *"For server-like receivers and extensions, you can protect your Collector from exposure to the public internet or to wider networks than necessary by binding these components' endpoints to addresses that limit connections to authorized users."* … *"Try to always use specific interfaces, such as a pod's IP, or `localhost` instead of `0.0.0.0`."*

That is a real disagreement in posture rather than a gap in my reading: the specification-adjacent source says *don't do this*, and the practitioner sources explain *how to do it anyway*. Worth knowing that approaches B, C and D carry no official standing.

**The hardening literature is stricter than the vendor documentation.** Grafana documents `api_key` without qualification; the hardening write-up treats a static key as insufficient and requires short-lived origin-bound tokens plus schema validation. Both are cited below; the cohort should know it is choosing between them, not reading a consensus.

---

## Known failure modes, from the sources rather than reasoned

1. **A real SSRF in this exact component.** [grafana/agent#6683](https://github.com/grafana/agent/issues/6683), opened 2024-03-14, now **closed** (fix PR #6686): the Faro receiver attempted to fetch URLs taken from stacktrace frame filenames, and the documented `download = false` setting *was not respected by the code*. A crafted payload made the receiver fetch arbitrary URLs — from inside the network the collector sits in. This is the most instructive item on the list: the component the cohort would deploy had a default-on SSRF reachable by anyone who could post to it.
2. **Cost and signal amplification.** An unauthenticated ingest endpoint can be spammed to inflate storage and drown real signal. On a self-hosted stack the bill is a maintainer's disk rather than an invoice — see [#331](https://github.com/launchpad-26/buzz/issues/331) and [#312](https://github.com/launchpad-26/buzz/issues/312).
3. **The endpoint is an exfiltration channel.** *"any XSS, malicious extension, or compromised npm dependency in the page can read or modify telemetry — and can use the RUM endpoint as an exfiltration channel."* Because the ingest accepts arbitrary attributes with no schema validation, exfiltrated data looks exactly like telemetry. This is #289's own security warning arriving from the opposite direction: not "telemetry leaks secrets outward" but "an attacker uses the telemetry path as their outward channel".
4. **CSP will silently block it.** The OTLP endpoint's domain must appear in `connect-src`, or the browser drops the requests. Conversely, an explicit `connect-src` allowlist is itself a mitigation for (3): *"connect-src enumerates the RUM endpoint explicitly. An XSS-injected exfil to attacker.example is blocked."*
5. **Payload limits are a control, not a tuning knob.** Recommended: cap attribute length ~1 KB, reject events over ~16 KB, per-IP and per-session rate limits (~600 events/min/IP). Alloy's 5 MiB default `max_allowed_payload_size` is generous by comparison.

---

## What this means for #289

1. **Buzz gets option C nearly for free, and should probably take it.** The web client is served by the relay (`BUZZ_WEB_DIR`), so browser and telemetry endpoint can be **same origin**. That removes CORS entirely, adds no new internet-facing service, and lets the relay — which already authenticates with NIP-42 — decide whose telemetry it accepts. None of the other three options can authenticate a browser at all.
2. **It is also the only option compatible with the stack living on a maintainer's laptop.** A browser can only reach a publicly-addressable endpoint. A/B/D all require exposing the collector to the internet; C requires only that the relay be reachable, which it must be anyway. That makes this question and [#334](https://github.com/launchpad-26/buzz/issues/334) the same question for the web client, and C answers both.
3. **The relay's existing OTLP transport cannot be reused for browsers regardless.** `crates/buzz-relay/src/telemetry.rs` builds its exporter with `.with_tonic()` — gRPC only — and browsers cannot speak OTLP/gRPC. Whatever is chosen, browser ingest is a second, HTTP-terminating path.
4. **Criterion 6's filtering policy has to cover ingest, not just egress.** Failure mode (3) means the filtering policy is bidirectional: it governs what the cohort collects *and* what an attacker can push in. Schema validation at ingest is a criterion-6 control that nobody has framed as one.
5. **Whatever is deployed should be pinned and watched.** Failure mode (1) is a reminder that this component has had a default-on SSRF. A version and an update path are part of the deployment, not an afterthought.

---

## Confidence and what is still unknown

**High confidence** on the Alloy defaults and the `api_key` semantics — quoted from the current component reference. **High confidence** on the OTel security page's silence: I fetched it specifically to look for this guidance and it is not there.

**Moderate confidence** on the hardening recommendations in approach D and failure modes (3) and (5). They come from a single practitioner source. The reasoning is sound and the "a browser cannot hold a long-lived secret" framing is simply correct, but the specific numbers — 15-minute tokens, 1 KB attributes, 16 KB events, 600 events/min/IP — are one author's recommended thresholds and should be treated as a starting point rather than a standard.

**Not verified:** I ran nothing. No collector was stood up, no `faro.receiver` was configured, no CORS behaviour was observed, and the SSRF issue was read rather than reproduced (it is closed, and I did not confirm which Alloy version carries the fix — anyone deploying should check the version they pin rather than trust that a 2024 fix is present).

**Not researched:** `otelcol.receiver.otlp`'s own CORS block as an alternative to `faro.receiver`, which would matter if the cohort prefers plain OTLP over the Faro SDK; whether the Faro Web SDK can be made to work with a same-origin relay path without modification, which is the practical question behind recommendation 1 and which I did not check; authenticator extensions (`bearertokenauth`, `oidcauth`, `basicauth`) beyond noting they exist, because none of them solves the browser-cannot-hold-a-secret problem; and any option involving a CDN or WAF in front, which was outside the scope of what I searched.

## Sources

- [faro.receiver — Grafana Alloy documentation](https://grafana.com/docs/alloy/latest/reference/components/faro/faro.receiver/) — defaults, `api_key`, `cors_allowed_origins`, `rate_limiting`
- [Collector configuration best practices — OpenTelemetry](https://opentelemetry.io/docs/security/config-best-practices/) — the bind-to-localhost posture, and the absence of exposed-collector guidance
- [Securing your OpenTelemetry Collector — Juraci Paixão Kröhling, OpenTelemetry on Medium](https://medium.com/opentelemetry/securing-your-opentelemetry-collector-1a4f9fa5bd6f) — reverse proxy for web apps, SSL offloading, CORS, the gRPC long-lived-connection caveat
- [Frontend RUM Security: Grafana Faro, Session Replay, and Browser Telemetry — systemshardening.com](https://www.systemshardening.com/articles/observability/frontend-rum-security-grafana-faro/) — short-lived origin-bound tokens, CSP `connect-src`, payload validation, exfiltration channel, rate-limit thresholds
- [grafana/agent#6683 — Faro receiver is vulnerable to SSRF by default](https://github.com/grafana/agent/issues/6683) — closed, fix PR #6686
- [otelcol.receiver.faro — Grafana Alloy documentation](https://grafana.com/docs/alloy/latest/reference/components/otelcol/otelcol.receiver.faro/) — the OTLP-pipeline variant, noted but not researched

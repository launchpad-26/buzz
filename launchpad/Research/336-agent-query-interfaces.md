# What an agent would query, and what credential it needs

**Title:** Query interfaces the Grafana stack exposes to a non-browser client, and their credentials
**Summary:** Two paths, and only one can be scoped. Direct access to Loki, Prometheus and Tempo carries no authentication at all — Loki's own guidance is that you run an authenticating reverse proxy in front. Through Grafana, one service account token reaches all three signals, and the Viewer role is genuinely read-only. So criterion 4's credential has a workable answer — one Grafana service account token with the Viewer role — subject to two unsettled caveats: nobody has confirmed a Viewer can reach the datasource proxy, and on OSS Grafana that read is organisation-wide rather than per-datasource, because resource scoping is an Enterprise feature.
**Tags:** `observability` `grafana` `credentials` `agents` `loki` `least-privilege`
**Reviewed:** 2026-08-22 · **Answers:** [#336](https://github.com/launchpad-26/buzz/issues/336)

---

## Finding

**Two paths, and only one of them can be scoped.**

**Direct to each store** — Loki's LogQL, Prometheus's PromQL, Tempo's HTTP API — is available to any non-browser client and **carries no authentication of its own**. Loki's guidance is explicit: *"Loki does not have an authentication layer. Instead, you are expected to run an authenticating reverse proxy in front of your services."* There is no credential to scope because there is no credential.

**Through Grafana** — one HTTP API, one **service account token**, reaching all three signals through the datasource proxy. And the answer that matters most for criterion 4: **yes, read-only can be granted** — the **Viewer** role is exactly that.

So the agent's credential is **one Grafana service account token with the Viewer role**: not three store credentials, and not direct store access, which cannot be restricted at all.

**Two caveats belong here rather than 60 lines down, because this document's conclusion depends on them and neither is settled.**

- **The precondition is untested.** Nobody has confirmed that a Viewer-role token can actually reach the **datasource proxy**. If it cannot, the read-only recommendation does not work at all and criterion 4 needs a different answer. This is the first thing to test.
- **"Read-only" is org-wide, not resource-scoped, on OSS Grafana.** Per-datasource restriction is a **Grafana Enterprise** feature — *"Data source permissions enable you to restrict data source query permissions to specific Users, Service Accounts, and Teams"* is listed under Enterprise. On the self-hosted stack #289 implies, a Viewer token reaches **every datasource and dashboard in its organisation**.

  That is acceptable **only under a stated assumption**: this Grafana instance is dedicated to the telemetry stack, so org-wide Viewer *is* telemetry-only Viewer today. The failure mode is concrete and silent — add one unrelated datasource to the same org later and the "least-privilege" token gains read access to it with nobody revisiting the decision. Genuine resource-scoping needs Enterprise, or a Grafana instance dedicated to this stack.

---
## The two paths

### Direct to the stores — available, and unauthenticated

| Store | Interface | Query language |
|---|---|---|
| Loki | HTTP API | LogQL |
| Prometheus | HTTP API | PromQL |
| Tempo | HTTP API (port 3200 in the reference image) | TraceQL |

All reachable without a browser. **None of them authenticates.** For Loki this is documented and unambiguous — *"Grafana Loki does not include built-in authentication by default"*, and the recommended pattern is an nginx or OAuth2 proxy in front. There is an ecosystem of third-party auth proxies precisely because the gap is real.

I confirmed this for **Loki** specifically. Tempo and Prometheus follow the same architectural pattern in the same stack, but I did not confirm each independently — see the confidence section.

**What this means practically:** if the agent talks to Loki directly, "what credential does it require" has no answer, and neither does "can it be read-only". Anything that can reach the port can read everything and, for Prometheus and Loki write paths, potentially write.

### Through Grafana — one credential, scopeable

Grafana's HTTP API fronts all three stores through its datasource proxy, so a single token queries logs, metrics and traces.

**Service accounts** exist for exactly this case — they *"enable automated workloads in Grafana without requiring a user login"* and authenticate *"applications accessing the Grafana HTTP API"*. Tokens are *"generated random string[s] that act[s] as an alternative to a password"*, function identically to API keys, and inherit their parent account's permissions.

| Role | What it grants |
|---|---|
| **Viewer** | **Read-only** |
| Editor | Modification |
| Admin | Full |
| **None** (since Grafana 10.2.0) | No default permissions at all |

Grafana Enterprise adds fine-grained RBAC on top.

**Token lifetime is the weak default.** Tokens *"lack expiration by default"*. Two mitigations exist: `token_expiration_day_limit` to enforce expiry server-side, and a manual expiry at creation time. Grafana's own recommendation is to set a token *"to expire after a short time, such as a few hours or less"*.

---

## What this means for #289

1. **Criterion 4's credential has a clean answer: a Grafana service account token with the Viewer role.** One credential, all three signals, read-only, no ability to modify dashboards, alerts or data.
2. **#289's own security note is largely answered — subject to the two caveats above.** It warns that *"the agent's query path is a credential… read access to the cohort's full telemetry picture, held by an automated process"*. Read access is what Viewer grants, and no write access — provided the agent goes through Grafana. It is **not** "nothing more": on OSS Grafana that read is organisation-wide, so the claim is bounded by the dedicated-instance assumption stated in the Finding.
3. **The agent must not be given direct store access.** It is the tempting shortcut — no Grafana in the way, simpler queries — and it is unauthenticated by design, so it cannot be scoped, revoked per-consumer, or audited.
4. **Set an expiry.** Non-expiring tokens are the default and Grafana itself recommends against them. A token that never expires, held by an automated process, on a machine the cohort does not fully control, is the shape of a long-lived leaked credential.
5. **This has a deployment consequence.** If the agent must go through Grafana, then Grafana — not the raw stores — is what needs to be reachable from wherever the agent runs, which feeds back into [#334](https://github.com/launchpad-26/buzz/issues/334)'s reachability options.

---

## Confidence and what is still unknown

**High confidence** on Grafana service accounts, the three roles, the `None` role, token semantics and the expiry defaults — all from Grafana's own administration documentation.

**High confidence on Loki having no authentication layer**, which is documented by the project and corroborated by the existence of several third-party auth proxies built to fill the gap.

**Lower confidence on Tempo and Prometheus specifically.** My search returned Loki material and the summary explicitly noted that Tempo and Prometheus documentation *"was not prominently featured in these results"*. I have generalised from the shared architecture rather than confirming each, and **someone should check before relying on it** — though the conclusion (use Grafana, not direct access) does not change either way.

<sub>Revised per [#416](https://github.com/launchpad-26/buzz/issues/416). The first version described this as "a clean answer" and "exactly the scope criterion 4 needs and no more" in its Summary and Finding, while recording the untested datasource-proxy precondition only in this section, 60 lines below. What surfaces to a future implementer is the headline, so both caveats now sit in the Finding. The Enterprise scoping limit was flagged by the reviewer against Grafana's own documentation, having been listed here as unverified.</sub>

**Not verified: nothing was run.** No service account was created, no token issued, no query executed against any store, and the Viewer role's read-only behaviour was not tested — in particular I did not check whether a Viewer can still reach the datasource proxy, which is the one place a read-only role could plausibly be *too* restrictive and break criterion 4 entirely. **That is the single most important thing to test before this is relied on.**

**Not researched:** whether the reference stack exposes the store ports outside its container at all, which would make direct access moot; Grafana's `/api/ds/query` request shape, which is what an agent would actually post; rate limiting or query cost controls on the Grafana side; and whether anonymous access is enabled by default in the reference image, which would undercut the whole credential discussion.

## Sources

- [Service accounts — Grafana documentation](https://grafana.com/docs/grafana/latest/administration/service-accounts/) — roles, token semantics, expiry defaults and recommendations
- [How to Secure Loki with Authentication — OneUptime](https://oneuptime.com/blog/post/2026-01-21-loki-authentication/view) — Loki's lack of built-in authentication
- [loki/docs/operations.md — grafana/loki](https://github.com/grafana/loki/blob/v0.3.0/docs/operations.md) — *"you are expected to run an authenticating reverse proxy in front of your services"*
- [MyUnisoft/loki-reverse-proxy](https://github.com/MyUnisoft/loki-reverse-proxy) and [mmohamed/loki-auth-proxy](https://github.com/mmohamed/loki-auth-proxy) — third-party proxies filling the gap
- [grafana/docker-otel-lgtm](https://github.com/grafana/docker-otel-lgtm) — the ports each store listens on in the reference deployment

# The minimum Grafana-stack component set for logs, metrics and traces

**Title:** Which components a self-hosted Grafana observability stack actually needs
**Summary:** Five components, and the LGTM acronym misleads — for a single host it is Prometheus, not Mimir. Alerting needs no additional service because it lives inside Grafana. Pyroscope ships switched on in the obvious starting point and is a fourth signal #289 does not ask for. A first-party reference deployment exists, `grafana/otel-lgtm`, and it explicitly disclaims the use this PRD has in mind, pointing production users at the hosted product the PRD rejected on cost.
**Tags:** `observability` `grafana` `loki` `tempo` `prometheus` `docker-compose` `lgtm`
**Reviewed:** 2026-08-22 · **Answers:** [#327](https://github.com/launchpad-26/buzz/issues/327)

---

## Finding

**Five components. The acronym misleads: for a single host it is Prometheus, not Mimir.**

| Signal | Component | Mandatory? |
|---|---|---|
| Metrics | **Prometheus** (Mimir only at scale) | Yes |
| Logs | **Loki** | Yes |
| Traces | **Tempo** | Yes |
| Query, dashboards, **alerting** | **Grafana** | Yes |
| Ingest | **OpenTelemetry Collector** or **Alloy** | Yes |
| Profiles | Pyroscope | **No** — a fourth signal #289 does not ask for |

A first-party reference deployment exists — `grafana/otel-lgtm`, one image, `docker run -v /your/path:/data grafana/otel-lgtm`. **It carries a caveat that matters more than the component list:** Grafana states it is *"intended for development, demo, and testing environments"* and points production users at Grafana Cloud, the hosted product #289 rejected on cost.

---
## The components, and what omitting each costs

### Metrics: Prometheus, not Mimir

The "M" in LGTM is Mimir, and reaching for it here would be a mistake. Mimir *"excels at handling large-scale metrics storage and querying"* — horizontally scalable, multi-tenant, object-storage backed. That is the problem it solves, and the cohort does not have it. Grafana's own reference image ships **Prometheus** on port 9090 instead, which is the correct choice for one host.

This also lines up with what already exists: the relay exposes Prometheus metrics on `:9102`, so a Prometheus scrape needs no translation layer.

**Omitting it:** no metrics, and no numeric alert conditions — which takes criterion 5 with it.

### Logs: Loki

*"efficient log aggregation and querying without requiring complex indexing"*. Loki indexes labels rather than content, which is why it is cheap to run on one machine.

**Omitting it:** loses criterion 2 outright. The witnessed error that vanishes is a log line, not a span.

### Traces: Tempo (3200)

**Omitting it:** loses criterion 3's cross-vantage-point comparison, and makes the relay's existing OTLP span exporter pointless — the one piece of #289's evidence that the relay side is "closer to configuration than construction".

### Query, dashboards and alerting: Grafana (3000)

Worth stating explicitly because the issue asks where alerting lives: **Grafana Alerting is part of Grafana**, not a separate component. Criterion 5 needs no fifth service — the rule evaluation, the contact points and the webhook that fires the issue pipeline are all in the box that is already mandatory for querying. [#324](https://github.com/launchpad-26/buzz/issues/324) and [#325](https://github.com/launchpad-26/buzz/issues/325) both assume this.

### Ingest: a collector

The reference image bundles the **OpenTelemetry Collector** on 4317 (gRPC) and 4318 (HTTP). #289's direction is **Alloy** on each participating machine, which is a different thing in a different place: Alloy is the per-machine agent, the collector is the central receiver. They are not alternatives here — the per-machine agents ship to the central receiver.

Two things this must terminate, from the sibling questions: the relay's exporter is **gRPC-only** (`.with_tonic()`), so 4317 is required; and browsers cannot speak gRPC, so 4318 or a same-origin path is required as well ([#321](https://github.com/launchpad-26/buzz/issues/321)).

### Optional: Pyroscope (4040) — profiles

Bundled in the reference image. **A fourth signal #289 does not ask for.** Omitting it costs continuous profiling, which nothing in the PRD's criteria requires. Worth naming precisely because it comes switched on in the obvious starting point — see below.

---

## The reference deployment, and its caveat

`grafana/docker-otel-lgtm` is first-party and complete:

```bash
docker run grafana/otel-lgtm:latest
docker run -v /your/path:/data grafana/otel-lgtm      # persist across restarts
```

Grafana at `http://127.0.0.1:3000`, default credentials `admin/admin`. All backend data lives under `/data`.

**Version pinning, per [#415](https://github.com/launchpad-26/buzz/issues/415).** Everything above describes the floating tag `grafana/otel-lgtm:latest`, whose bundled component versions change without notice. This document records the component *set*, which is stable; it should not be read as recording the *versions*, which are not. Anything the cohort deploys should pin a digest, and [#331](https://github.com/launchpad-26/buzz/issues/331) records that its own measurements were taken against an unpinned tag.

**The caveat, quoted:** *"If you are looking for a production-ready, out-of-the box solution to monitor applications and minimize MTTR (mean time to resolution) with OpenTelemetry and Prometheus, you should try Grafana Cloud Application Observability."* The image is *"intended for development, demo, and testing environments."*

That is not a reason to avoid it — it is the fastest way to have the whole stack running, and it is the right way to answer [#331](https://github.com/launchpad-26/buzz/issues/331)'s cost question. It **is** a reason not to treat "we ran the reference image" as equivalent to "we deployed the stack". Criterion 8 asks for something portable to a second host; a bundle-everything-in-one-container image explicitly scoped to demos is a starting point, not a destination.

The honest framing for #289: **use it to learn the shape and measure the cost; expect to unbundle it into a real Compose file with separate services, pinned versions and declared volumes** before it holds anything anyone depends on.

---

## What this means for #289

1. **Five services, one of them optional and switched on by default.** Anyone starting from the reference image should decide about Pyroscope deliberately rather than inherit a fourth signal that criterion 6 then has to write a policy for.
2. **Prometheus, not Mimir.** Cheaper, matches the relay's existing `:9102`, and the thing Mimir buys is scale the cohort does not have.
3. **Criterion 5 needs no additional component.** Alerting is inside Grafana.
4. **The obvious reference deployment disclaims the intended use**, and the vendor's suggested alternative is the hosted product this PRD rejected on cost. Worth stating plainly in the PRD rather than discovering later.
5. **The collector must terminate both OTLP transports** — gRPC for the relay, HTTP for browsers.

---

## Confidence and what is still unknown

**High confidence** on the component list, ports and the production caveat — all quoted from `grafana/docker-otel-lgtm`'s own documentation.

**Moderate confidence** on the Mimir-versus-Prometheus framing. It follows from Mimir's stated purpose and from Grafana's own choice of Prometheus in the reference image, but **I did not find a source stating a threshold** at which Mimir becomes worthwhile, so "not at cohort scale" is inference from the components' descriptions rather than a cited rule.

**Not verified: I did not run it.** At the time of writing the image is pulling for [#331](https://github.com/launchpad-26/buzz/issues/331)'s measurement; nothing here is based on a running stack. In particular I have not confirmed that the bundled versions are current, that `/data` persistence behaves as documented, or that the container starts cleanly on this platform.

**Not researched:** whether Loki, Tempo and Prometheus have single-binary modes suitable for a hand-written Compose file and what each needs configuring (the unbundling path recommended above); retention configuration for any of the three, which is criterion 6's other half; whether Grafana Alerting in a self-hosted install has feature gaps against Grafana Cloud, which matters for [#325](https://github.com/launchpad-26/buzz/issues/325)'s "Keep firing for"; and object-storage backends, which are irrelevant on one host but relevant to criterion 8's "move to a second host later".

## Sources

- [grafana/docker-otel-lgtm](https://github.com/grafana/docker-otel-lgtm) — component list, ports, `/data` volume, the production caveat
- [LGTM Stack for Observability: A Complete Guide — DrDroid](https://drdroid.io/engineering-tools/lgtm-stack-for-observability-a-complete-guide/) — per-component purpose, Mimir's scale positioning
- [Self-Hosted Grafana Observability Backends: Loki vs Mimir vs Tempo vs Cortex — Pi Stack](https://www.pistack.xyz/posts/2026-05-17-self-hosted-grafana-observability-backends-loki-mimir-tempo-cortex-guide/) — backend comparison, surfaced but not read in full
- [How to Build a Complete LGTM Stack with OpenTelemetry — OneUptime](https://oneuptime.com/blog/post/2026-02-06-lgtm-stack-opentelemetry/view) — Compose-based deployment for smaller setups

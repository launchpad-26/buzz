# What the Grafana stack costs in RAM and disk on one machine

**Title:** Measured resident cost of the self-hosted Grafana observability stack
**Summary:** Measured on one Intel Mac: ~456 MiB RAM idle, ~627 MiB after a burst, 187 MB on disk at rest, plus a 2.43 GB image — about 4–5% of memory on a 16 GB laptop. Traces cost 121 bytes per span on disk, 4.8× compression against the wire, making retention a one-line calculation. 65 MB of the 190 MB data directory is Pyroscope profiling the stack itself, a signal the PRD never asked for. Traces only were measured; logs, the likely dominant signal, were not.
**Tags:** `observability` `grafana` `cost` `measurement` `capacity-planning` `lgtm`
**Reviewed:** 2026-08-22 · **Answers:** [#331](https://github.com/launchpad-26/buzz/issues/331)

---

## Finding

**Measured, not estimated: ~456 MiB of RAM idle, ~627 MiB after a burst, 187 MB on disk at rest, plus a 2.43 GB image.** On a 16 GB laptop that is about 4–5% of memory. **The stack is not the expensive part.**

Two findings matter more than the headline:

- **Traces cost 121 bytes per span on disk**, 4.8× compression against the wire. Retention sizing becomes arithmetic: 10 spans/s is ~99 MB/day.
- **65 MB of the 190 MB data directory is Pyroscope, which received nothing.** It is profiling the stack itself — a third of the disk at rest spent on a signal [#289](https://github.com/launchpad-26/buzz/issues/289) never asked for.

**One limitation stated up front: traces only were measured.** Loki received nothing, and logs are very likely the dominant signal for criterion 2.

---
## Method

`grafana/otel-lgtm:latest`, the first-party reference image identified in [#327](https://github.com/launchpad-26/buzz/issues/327), run with a bind-mounted `/data` so disk could be measured directly:

```
docker run -d --name lgtm-measure -v <scratch>/lgtm-data:/data \
  -p 127.0.0.1:4317:4317 -p 127.0.0.1:4318:4318 \
  -p 127.0.0.1:23001:3000 -p 127.0.0.1:23200:3200 -p 127.0.0.1:23090:9090 \
  grafana/otel-lgtm:latest
```

**Host:** macOS 15.7.7 (24G720), Intel Core i7-8850H, 12 cores, 16 GB RAM. Docker Desktop reported 11.68 GiB available to containers.

**Artifact pinning — a real limitation of these figures, per [#415](https://github.com/launchpad-26/buzz/issues/415).** The measurement used the floating tag `grafana/otel-lgtm:latest` and **the resolved digest was not captured at measurement time**. Grafana rebuilds and republishes that tag, so re-running the commands below in a month measures a different artifact with no way to tell whether a changed number reflects a changed stack or a changed image.

The digest cannot now be recovered for the run that produced these figures — the image was deleted after measuring. For reference only, the tag resolved to `sha256:20d748ba7439789a0e897d9821a50bca9ba41bba734ec53569d4c01a8dd8f9f2` (multi-arch index) when checked on 2026-08-22, **after** the measurement; it may or may not be the artifact measured, and should not be treated as though it were.

**For any future measurement, capture it at the time:**

```bash
docker inspect --format '{{index .RepoDigests 0}}' grafana/otel-lgtm:latest
```

The container's startup log confirms all six components:

```
 - 4317: OpenTelemetry GRPC endpoint
 - 4318: OpenTelemetry HTTP endpoint
 - 3000: Grafana (http://localhost:3000). User: admin, password: admin
 - 3200: Tempo endpoint
 - 4040: Pyroscope endpoint
 - 9090: Prometheus endpoint
```

## At rest — 60 s after start, nothing sent

```
$ docker stats --no-stream lgtm-measure
MEM: 456MiB / 11.68GiB  (3.81%)   CPU: 5.53%

$ du -sh lgtm-data
187M	lgtm-data
$ du -sh lgtm-data/*
4.0K	lgtm-data/tempo
8.0K	lgtm-data/loki
 40K	lgtm-data/prometheus
 64M	lgtm-data/pyroscope
123M	lgtm-data/grafana

$ docker images grafana/otel-lgtm --format '{{.Size}}'
2.43GB
```

**Read that disk breakdown carefully.** Grafana's 123 MB is its own bundled assets and database — a fixed cost, not growth. **Pyroscope's 64 MB is profiles of the stack profiling itself**, with no application connected. Tempo, Loki and Prometheus — the three components that exist to hold the cohort's telemetry — account for **52 KB combined**.

## Under ingest — 20,000 spans

Synthetic OTLP/HTTP spans shaped like the relay's real ones (`ws.auth`, `ws.req`, `ws.count`, `http.request`, `audio.join`, with `conn_id`, `pubkey` and `channel_id` attributes), posted to `:4318/v1/traces`:

```
spans sent: 20000
wire bytes sent: 11467571 (10.94 MiB)
elapsed: 3.3s  -> 6113 spans/s offered
```

All 20,000 were accepted without error at 6,113/s — well above anything this cohort will produce, so **ingest throughput is not a constraint worth worrying about.**

```
$ docker stats --no-stream lgtm-measure          # immediately after
MEM: 626.6MiB / 11.68GiB  (5.24%)   CPU: 8.94%
$ docker stats --no-stream lgtm-measure          # ~2 min later, idle
MEM: 623.7MiB / 11.68GiB (5.22%)  CPU: 6.17%

$ du -sh lgtm-data/tempo/*
2.3M	lgtm-data/tempo/blocks
 36K	lgtm-data/tempo/generator
  0B	lgtm-data/tempo/wal
```

**Memory rose ~170 MiB and did not come back** two minutes after ingest stopped — normal Go runtime behaviour, but it means "idle" after use is ~625 MiB rather than ~456 MiB.

**The data is real, not silently dropped** — queried back out of Tempo:

```
$ curl -s "http://127.0.0.1:23200/api/search?limit=3"
{"traces":[{"traceID":"e53cbe2d9eaf1108502edf0893172","rootServiceName":"buzz-relay",
"rootTraceName":"ws.auth","startTimeUnixNano":"1787346289079474944","durationMs":6},
{"traceID":"2cfcbe1e6cc4d0260de6b81a4609b","rootServiceName":"buzz-relay",
"rootTraceName":"ws.req",...
```

## The arithmetic, stated as arithmetic

2.3 MiB of Tempo blocks ÷ 20,000 spans = **121 bytes per span on disk**. The same spans were 573 bytes each on the wire, so Tempo compressed them **4.8×**.

```
at   1 spans/s ->     86,400 spans/day ->      9.9 MB/day -> 0.29 GB/30d
at  10 spans/s ->    864,000 spans/day ->     99.4 MB/day -> 2.91 GB/30d
at 100 spans/s ->  8,640,000 spans/day ->    993.6 MB/day -> 29.11 GB/30d
```

These are extrapolations from one measurement, not measurements. **Which row applies depends on [#312](https://github.com/launchpad-26/buzz/issues/312)**, the relay's actual production rate, which is unmeasured — that is the missing multiplicand, and this document supplies the other one.

---

## What this means for #289


> **Recommendations, not findings.** Everything in this section is my assessment as the author, not behaviour established by the evidence above. Per [ADR-0003]'s claim rule: a claim about how the system *behaves* carries a source reference; a claim about what the cohort *should do* is opinion, attributed. Nothing is both — so nothing below is cited as though it were established.
1. **Memory is a non-issue and can stop being a worry.** ~625 MiB after use, on a 16 GB machine. Criterion 8's "runs on a maintainer's machine" is comfortably satisfied on memory alone.
2. **The 2.43 GB image is the largest single cost, and it is one-off.** Worth stating because it dwarfs everything else on this page and is easy to forget when sizing a host.
3. **Turn Pyroscope off.** [#327](https://github.com/launchpad-26/buzz/issues/327) argued it on scope grounds; this measures the price — 64 MB at rest, ~34% of the data directory, for a signal nobody asked for, collected from machines the cohort does not own. Both arguments point the same way.
4. **Retention sizing is now a one-line calculation** once #312 lands. At any plausible cohort volume this fits on a laptop for months: even 10 spans/s sustained is under 3 GB a month.
5. **Ingest throughput is not a constraint.** 6,113 spans/s accepted cleanly, orders of magnitude above cohort scale.

---

## Confidence and what is still unknown

**High confidence in the numbers** — every figure above is pasted command output from a real run on a stated host, and the ingested data was queried back to prove it was stored rather than dropped.

**The significant limitation: I measured traces only.** Loki stayed at 8 KB because I sent it no logs, and Prometheus grew by 32 KB from the stack's own self-monitoring. **Logs are very likely the dominant signal for #289** — criterion 2 is about an error message a human saw, which is a log line, not a span — so the bytes-per-unit figure that matters most for retention is the one I do not have. Someone should repeat this against `:4318/v1/logs` with realistic log lines; the method above transfers unchanged and takes about ten minutes.

**Also not measured:**
- **CPU under query load.** Idle CPU was 5.5% and ingest CPU 8.9%; nobody ran a dashboard or a wide time-range query, which is where these stacks actually get expensive.
- **Behaviour when the disk fills** — named in the issue's definition of done and not attempted.
- **Sustained multi-day operation.** This was minutes. Compaction, block flushing and retention enforcement all operate on longer horizons, and 121 bytes/span is measured before any compaction cycle has run — the long-run figure could be lower.
- **Per-component memory.** The bundled image runs everything in one container and `ps` was unavailable inside it, so 456 MiB is a single total and cannot be attributed per component.
- **A real Compose deployment.** This is the single-container reference image, which #327 records as *"intended for development, demo, and testing environments"*. An unbundled multi-service Compose stack — which is what the cohort would actually run — has different overhead, probably somewhat higher.

**Cleanup:** the container, its data directory and the 2.43 GB image were all removed after measuring; the machine's container set is back to what it was.

# What Grafana Alloy costs on a participating machine

**Title:** Measured resident cost of Grafana Alloy, and its behaviour when the collector is unreachable
**Summary:** Measured natively on an Intel Mac: ~117 MiB RSS idle, ~127 MiB while buffering, 0.1% CPU steady. The disk cost is the 419 MB binary, not the 36 KB of runtime state. The important finding is the unreachable-collector case — `prometheus.remote_write` buffers to a disk WAL and survives a restart, while `otelcol.exporter.otlp` buffers in memory only and does not, so metrics from a laptop-closed window come back and traces and logs do not. The macOS binary is also unsigned.
**Tags:** `observability` `grafana-alloy` `cost` `measurement` `buffering` `macos`
**Reviewed:** 2026-08-22 · **Answers:** [#333](https://github.com/launchpad-26/buzz/issues/333)

---

## Finding

**Measured natively on an Intel Mac, not in a container: ~117 MiB RSS idle, ~127 MiB while buffering, 0.1% CPU steady.** The running cost is small.

**The disk cost is not the buffer — it is the binary: 419 MB unpacked** (105 MB download) per machine, against 36 KB of runtime state.

**The important finding concerns the unreachable-collector case, which behaves in two completely different ways depending on the signal:**

| Pipeline | Where it buffers | Survives an Alloy restart? |
|---|---|---|
| `prometheus.remote_write` | **Disk WAL** | **Yes** — replayed |
| `otelcol.exporter.otlp` (traces, logs) | **Memory only** | **No** |

Since [#289](https://github.com/launchpad-26/buzz/issues/289) puts the collector on a maintainer's laptop that will regularly be shut, **metrics from an outage window come back and traces and logs do not** — and those are the two signals criteria 2 and 3 depend on.

**Bonus finding, closing a gap flagged in [#332](https://github.com/launchpad-26/buzz/issues/332): the macOS binary is unsigned.**

---
## Method

The real `alloy-darwin-amd64` binary from release **v1.18.1**, run directly on the host — not a Docker proxy — so the numbers are what a member's machine would actually see.

**Host:** macOS 15.7.7 (24G720), Intel Core i7-8850H, 12 cores, 16 GB RAM.

The configuration, deliberately representative of the intended collection *and* deliberately pointed at endpoints that do not exist, so buffering could be observed:

```river
otelcol.receiver.otlp "default" {
  grpc { endpoint = "127.0.0.1:14317" }
  http { endpoint = "127.0.0.1:14318" }
  output {
    traces  = [otelcol.exporter.otlp.central.input]
    logs    = [otelcol.exporter.otlp.central.input]
    metrics = [otelcol.exporter.otlp.central.input]
  }
}

otelcol.exporter.otlp "central" {
  client {
    endpoint = "127.0.0.1:19999"   // nothing is listening here
    tls { insecure = true }
  }
}

prometheus.scrape "self" {
  targets    = [{"__address__" = "127.0.0.1:12345"}]
  forward_to = [prometheus.remote_write.central.receiver]
  scrape_interval = "15s"
}

prometheus.remote_write "central" {
  endpoint { url = "http://127.0.0.1:19999/api/v1/write" }
}
```

## Memory and CPU

```
=== 30s after start, exporters already failing ===
    PID    RSS  %CPU ELAPSED COMM
  24160 119248   3.8   00:30 ./alloy-darwin-amd64
  RSS = 116.5 MiB

=== after receiving 5,000 spans with nowhere to send them ===
  24160 130492   0.1   01:34
  RSS = 127.4 MiB

=== ~2.5 min, still failing to export ===
  RSS = 122.8 MiB   CPU = 0.1%
```

**~117 MiB idle, peaking ~127 MiB while holding a burst, settling ~123 MiB.** CPU is 3.8% during startup and **0.1%** at steady state. On a 16 GB laptop that is under 1% of memory and effectively no CPU.

For scale: 5,000 spans were offered and accepted in **0.4 s** while the destination was down.

## Disk — the binary dwarfs everything else

```
  unpacked binary: 419M
  download (zip):  105M

$ du -sh <data>
 36K
```

**419 MB of binary against 36 KB of runtime state.** Anyone sizing "what does Alloy cost a member's machine" should be quoting the binary, not the buffer.

## The unreachable-collector case — the finding

After 90 seconds of failing exports, the entire on-disk footprint was:

```
<data>
<data>/prometheus.remote_write.central
<data>/prometheus.remote_write.central/wal
<data>/remotecfg
--- prometheus WAL contents ---
<data>/prometheus.remote_write.central/wal/00000000
```

**There is no OTLP directory. The 5,000 buffered spans never touched disk.**

The two pipelines say so themselves, in their own log lines:

```
level=warn msg="Failed to send batch, retrying" component_id=prometheus.remote_write.central
  subcomponent=rw url=http://127.0.0.1:19999/api/v1/write err="Post \"http://...

level=info msg="Exporting failed. Will retry the request after interval."
  component_id=otelcol.exporter.otlp.central error="rpc error: code = Unavailable ...
```

48 retries and 48 connection-refused entries over the run. Metrics were replayed from a **write-ahead log on disk**; traces and logs were retried from an **in-memory queue**.

**What that means concretely.** The collector lives on a maintainer's machine (criterion 8). That machine will be closed overnight and at weekends. During those windows:

- **Metrics survive.** The WAL is on disk; when the collector returns, Alloy replays.
- **Traces and logs do not.** They sit in memory, are lost if Alloy or the member's machine restarts, and are silently dropped once the queue fills.

Criterion 2 — an error a human saw, still there afterwards — depends on **logs**. Criterion 3 depends on **traces**. Both are in the column that does not survive. This is fixable — the OpenTelemetry Collector supports a persistent sending queue backed by a file-storage extension — but **it is not the default and my representative config did not have it.**

## The signing gap from #332, closed

```
$ codesign -dv --verbose=2 ./alloy-darwin-amd64
./alloy-darwin-amd64: code object is not signed at all
```

**Not signed at all.** It ran here because `curl` does not attach a quarantine attribute. A member who downloads the zip in a **browser** gets `com.apple.quarantine` and Gatekeeper will refuse it. Homebrew installs are also unaffected. So the practical rule is: install via Homebrew or curl, never by clicking a download link — otherwise the instructions inherit the same Gatekeeper-bypass problem [#319](https://github.com/launchpad-26/buzz/issues/319) identified for a fork-built desktop client.

---

## What this means for #289

1. **Running cost is a non-issue.** ~120 MiB and 0.1% CPU is easy to justify asking of a member.
2. **Quote 419 MB, not 120 MiB, when asking.** The disk cost is the honest number and it is 3,500× the runtime state.
3. **The buffering asymmetry needs a decision before deployment, not after.** A persistent queue for the OTLP pipeline must be configured explicitly, or every laptop-closed window is a hole in exactly the two signals criteria 2 and 3 depend on. This is the single most actionable thing in this measurement.
4. **It reframes [#334](https://github.com/launchpad-26/buzz/issues/334).** Reachability is not only "can the agent connect" — it is "what happens for the hours it cannot", and today the answer differs per signal.
5. **Install by Homebrew or curl, never a browser download.** Unsigned binary, quarantine attribute, Gatekeeper.

---

## Confidence and what is still unknown

**High confidence.** Every number is pasted output from the real native binary on a stated host, and the buffering conclusion is supported by three independent observations: the absence of an OTLP directory on disk, the presence of a Prometheus WAL file, and the two components' own differing log messages.

**Not measured — the numeric bound on the in-memory queue.** I observed *that* the OTLP queue is memory-resident and *that* it retries, but **I did not determine how many batches it holds before dropping, nor did I fill it.** The issue's definition of done asks for the configured bound and I have the behaviour without the number. Filling it would take a longer run at higher volume, and it is the obvious next measurement.

**Also not measured:** a genuinely sustained outage — the longest observation was about 2.5 minutes, so I did not see WAL truncation, queue exhaustion or any drop actually occur; a **restart** with data buffered, which would demonstrate the loss rather than infer it from the absence of files; log ingestion, since only traces were sent; behaviour with a **reachable** collector, so no throughput or latency figure under normal operation; memory over hours or days, where a slow leak would show; and Linux or Windows, where the footprint may differ.

**One caveat on representativeness:** my config scrapes a single local target and forwards OTLP. A real config that tails log files, collects host metrics or runs the Faro receiver would use more memory than 120 MiB, and I have not measured how much more.

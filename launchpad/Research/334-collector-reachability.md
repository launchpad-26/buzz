# Reaching a collector that has no public address

**Title:** Options for getting telemetry to a collector on a machine with no public address
**Summary:** Four workable options and one that looks obvious and fails. They split on a rule the literature states directly — admin-only access to an overlay network, public-shareable to a tunnel — which maps exactly onto the cohort's desktop-versus-browser split. The most important finding is not an option but a constraint applying to all of them: no tunnel wakes a sleeping laptop, and #333 measured that metrics survive that window from a disk WAL while traces and logs, buffered only in memory, do not.
**Tags:** `observability` `networking` `tailscale` `cloudflare-tunnel` `nat` `availability`
**Reviewed:** 2026-08-22 · **Answers:** [#334](https://github.com/launchpad-26/buzz/issues/334)

---

## Finding

**Four workable options and one that looks obvious and does not work.** They split cleanly on a rule the literature states directly: *"Admin-only access → Tailscale. Public-shareable → Cloudflare Tunnel."*

That maps onto this cohort's two client types, and the mapping is grounded in Buzz's own transport rather than in the generic rule alone:

- **Desktop agents are admin-only.** The desktop client is a native process — a Tauri binary (`desktop/src-tauri/tauri.conf.json`, `productName: "Buzz"`) whose relay socket is `tokio_tungstenite` (`desktop/src-tauri/src/native_websocket.rs:7`). A native process can join an overlay network and reach a private address. Nothing need be exposed publicly.
- **Browsers are public-shareable.** The web client's transport is `new WebSocket(wsUrl)` (`web/src/shared/lib/nostr-client.ts:45`) inside a browser sandbox, which cannot install VPN software and cannot reach a tailnet address unless the machine it runs on is already joined. It needs a publicly resolvable endpoint, or the same-origin relay path from [#321](https://github.com/launchpad-26/buzz/issues/321).
- **And the relay's own exporter cannot serve a browser regardless.** `crates/buzz-relay/src/telemetry.rs:243-244` builds its OTLP exporter with `.with_tonic()` — gRPC only — and browsers cannot speak OTLP/gRPC. So browser ingest is a separate HTTP-terminating path under every option below.

**The most important finding is a constraint applying to all four.** No tunnel wakes a sleeping laptop, and [#333](https://github.com/launchpad-26/buzz/issues/333) measured what happens during those hours: `prometheus.remote_write` buffers to a disk WAL and replays; `otelcol.exporter.otlp` buffers in memory only and loses everything on restart. Reachability is not "can the agent connect" but "what survives the hours it cannot" — and that answer differs per signal.

---
## The four options

### A. Overlay network — Tailscale / WireGuard

| | |
|---|---|
| **Installed on** | Both: the collector's machine and every member's machine |
| **Reachable** | Only devices in the tailnet. Nothing is exposed to the internet at all |
| **Authenticates** | WireGuard keys plus the overlay's own identity layer; *"every connection is encrypted and authenticated using the WireGuard protocol"* |
| **Cost** | Free tier covers this scale — reported as 3 users / 100 devices, and a Personal plan (April 2026 pricing) of 6 users with unlimited user-owned devices. A third party in the **control plane**, not the data path: it forms *"a peer-to-peer mesh"* |
| **Asleep** | Device simply unreachable. Agents buffer per #333 |
| **Browser?** | **Only from a machine already on the tailnet.** A web client served to an arbitrary browser cannot reach it |

The strongest fit for the desktop agents, and the only option where the collector never becomes internet-facing — which matters because #289 calls it *"the most valuable single target the cohort runs"*.

### B. Outbound-only tunnel — Cloudflare Tunnel / ngrok

| | |
|---|---|
| **Installed on** | The collector's machine only (a connector); nothing on members' machines |
| **Reachable** | A **public hostname**. Anyone who learns it can reach the endpoint unless something else gates it |
| **Authenticates** | Nothing by default — Cloudflare Access adds it, free up to 50 users |
| **Cost** | Free tier; *"limits on data transfer and log retention"* apply. A third party **in the data path** — all telemetry transits Cloudflare |
| **Asleep** | Tunnel drops; the hostname fails |
| **Browser?** | **Yes** — this is the only option that gives a browser a reachable endpoint without involving the relay |

*"Cloudflare Tunnel enhances security by allowing local services to be exposed to the internet without opening firewall ports"* — outbound-only, no public IP needed. The trade is a third party seeing the cohort's full telemetry stream, against a PRD whose stated value is that the cohort owns its own infrastructure.

### C. Hop through the host that already has a public address — the VPS

| | |
|---|---|
| **Installed on** | A forwarding collector on the cohort VPS; agents point at it |
| **Reachable** | Whatever the VPS firewall permits |
| **Authenticates** | Whatever the cohort configures |
| **Cost** | VPS memory and disk (#331: ~456 MiB and 187 MB for the full stack, less for a forwarder), plus **an ingress exception in a deny-by-default firewall** — ADR-0014 territory, and #30/#44 |
| **Asleep** | **Does not apply.** A VPS does not close its lid — the only option with no availability gap |
| **Browser?** | **Yes** |

The catch is that the VPS does not exist yet — `launchpad/ENVIRONMENTS.md` marks it `OPEN` and #2 is open. And #289's criterion 8 deliberately starts on a maintainer's machine. So this is the option the PRD has already deferred, not one it rejected.

### D. Same-origin through the relay — [#321](https://github.com/launchpad-26/buzz/issues/321)'s conclusion

| | |
|---|---|
| **Installed on** | Nothing new. The relay already terminates public traffic |
| **Reachable** | Only the relay, which is already internet-facing by necessity |
| **Authenticates** | **NIP-42** — the relay already knows who the client is. The only option with real client identity |
| **Cost** | Relay load on the telemetry path; relay code changes (upstream files → #273 register) |
| **Asleep** | The relay stays up; the *collector* behind it may not, so the relay would need its own buffer |
| **Browser?** | **Yes, and it is the only option that authenticates the browser** |

Arrived at independently by #321 (browser security) and #323 (trace propagation). Three questions pointing at one design.

### The one that does not work: pull-based inversion

Prometheus's native model is the collector **scraping** targets, which would remove the need for agents to reach anything. **It fails here for the same reason the question exists:** contributor machines are behind NAT too. A collector on a laptop cannot scrape a laptop on someone else's home network. Worth stating because it is the first thing a Prometheus-shaped instinct reaches for.

---

## The constraint that applies to every option

None of them wakes a sleeping machine. Whichever is chosen, telemetry produced while the collector is unavailable has to survive on the member's machine — and #333 measured that it half does:

- **Metrics survive** — `prometheus.remote_write` writes a WAL to disk and replays it.
- **Traces and logs do not** — `otelcol.exporter.otlp` retries from an in-memory queue with nothing on disk, lost on restart and dropped once the queue fills.

Criterion 2 depends on logs; criterion 3 depends on traces. **Both are in the column that does not survive.** A persistent sending queue must be configured explicitly, or the reachability question is answered and the availability question is quietly not.

---

## What this means for #289

1. **A hybrid is the natural shape, not a compromise.** Tailscale for the desktop agents (nothing exposed, real identity, free at this scale) plus the same-origin relay path for browsers (#321). Neither makes the collector internet-facing.
2. **The single-option instinct — Cloudflare Tunnel for everything — is the one with the worst fit for the PRD's stated values.** It works, it is free, it is easy, and it puts a third party in the data path of a cohort whose stated value is owning its own infrastructure. That is a legitimate choice, but it should be made rather than defaulted into.
3. **Availability, not reachability, is the harder half** — and it is per-signal, not global. Any child that picks a tunnel should also pick a buffering policy.
4. **The VPS option is deferred, not dead.** Criterion 8's "moves to a second host later" is exactly option C. Worth writing the agent configuration so the destination is one variable.
5. **Option A's free tier should be re-checked before it is relied on.** Two different figures were reported (3 users/100 devices; 6 users/unlimited user-owned devices at April 2026 pricing) and vendor free tiers move.

---

## Confidence and what is still unknown

**High confidence** on the architectural distinctions — mesh versus reverse proxy, outbound-only, what each exposes — which are consistent across the sources and are properties of how the products work.

**The desktop/browser split is now grounded in this repository**, not only in the vendors' generic rule: the Tauri binary and `tokio_tungstenite` on one side, `new WebSocket` in a browser sandbox and the relay's gRPC-only exporter on the other, all cited by file and line above.

<sub>Revised per [#419](https://github.com/launchpad-26/buzz/issues/419). The first version derived the split from a third-party comparison plus the general observation that a VPN cannot run in a browser, and cited no `crates/`, `desktop/` or `web/` paths — so a reader could have taken generic client-type reasoning for an architecture-specific finding about Buzz. The conclusion is unchanged; its provenance is now checkable.</sub>

**Low confidence on the pricing specifics**, and I would not act on them without checking. The two Tailscale free-tier figures came from different sources and disagree; the Cloudflare limits were described as *"limits on data transfer and log retention that you should check on Cloudflare's current pricing page"*, which is the source telling you not to trust a secondhand figure. **Vendor free tiers are exactly the thing a research document goes stale on.**

**Not verified: I set none of these up.** No tailnet, no tunnel, no measurement of added latency or overhead, and no test of what actually happens to an agent mid-send when the far end disappears. The buffering behaviour is carried over from #333, where it *was* measured.

**Not researched:** self-hosted alternatives — Headscale, Pangolin, plain WireGuard — which avoid the third-party control plane entirely and which one source raised; whether Tailscale's free tier permits the *tagged-resource* usage a shared collector would need, as distinct from user-owned devices; what an overlay network implies for #43's agent-containment boundary, since putting every member's machine on one flat network is a decision with a blast radius beyond telemetry; and mTLS with a public endpoint, a fifth option I did not develop.

## Sources

- [Cloudflare Tunnel vs. ngrok vs. Tailscale — DEV Community](https://dev.to/mechcloud_academy/cloudflare-tunnel-vs-ngrok-vs-tailscale-choosing-the-right-secure-tunneling-solution-4inm) — the three-way comparison and the admin-only/public-shareable rule
- [Tailscale vs Cloudflare Tunnel: Network Security and Zero Trust Compared](https://saasvssaas.com/tailscale-vs-cloudflare-tunnel/) — mesh versus reverse proxy, WireGuard authentication
- [Pangolin vs Cloudflare Tunnels vs Tailscale: Which Should You Self-Host?](https://contabo.com/blog/pangolin-vs-cloudflare-tunnels-vs-tailscale/) — self-hosted alternatives, free-tier figures
- [Tailscale vs Cloudflare Tunnel for home remote access — HomeTechOps](https://hometechops.com/guides/home-remote-access-tailscale-vs-cloudflare-tunnel/) — outbound-only, no public IP, free-tier notes
- [#333](https://github.com/launchpad-26/buzz/issues/333) — the measured buffering behaviour that applies to all options

---
status: Accepted
date: 2026-08-21
issue: launchpad-26/buzz#21
decided_in: launchpad-26/buzz#21
supersedes: none
---

# ADR-0018 — The cohort relay runs on the offered VPS specification, as-is

## Decision

**Accept the offered specification unchanged**: 1 vCPU, 1.9 Gi RAM, 496 MB swap, 49.5 G disk.

This **ratifies a state already in production**. The relay has been serving from that host on
that specification for days; this record makes the choice explicit rather than leaving an
internet-facing host whose sizing was never written down.

The two measurements this ADR named as gating — #18 (does the stack fit 1 vCPU and 1.9 Gi) and
#39 (relay capacity under concurrent load) — are **reframed as post-hoc validation**. If either
reports that the host cannot hold a realistic cohort load, the response is a ceilings decision
and/or a resize recorded in a new ADR, not a retroactive reversal of this one.

Rejected alternatives:

- **Reduce the stack** (external or dropped MinIO) — unnecessary; the full stack runs.
- **Request more RAM, or more RAM and vCPU** — no evidence yet that it is needed, and the
  procurement delay the original filing warned about was the larger risk to M0.
- **Run the relay from a source build on this host** — was filed as an expected rejection and
  remains one. The deployment already requires an explicit prebuilt image: `BUZZ_IMAGE` has no
  default and Compose fails without it (`deploy/compose/compose.yml` uses
  `${BUZZ_IMAGE:?...}`; `deploy/compose/README.md` states it plainly). Compiling roughly 30
  Rust crates on 1 vCPU with 2 GB would thrash or OOM.

## Context

#21 was filed on 2026-08-10 to settle sizing *before* the deployment work in #2 began, on the
reasoning that an undersized host should be discovered on a destroyable VM rather than on the
cohort's server. Its *Decision outcome* was left deliberately blank pending measurement, per the
agents-draft-humans-decide rule.

The measurements never completed. #18 and #39 are still open. The deployment happened anyway.
Verified on 2026-08-21: `https://launchpad-buzz.devacademy.nz` answers NIP-11, and a desktop
client authenticated over `wss://` and loaded 6 channels. The gate was overtaken by events, not
resolved by argument.

The failure mode the ADR most feared did **not** occur. It warned that a host unable to fit both
Buzz and its hardening baseline would, under milestone pressure, get the hardening dropped.
Instead #20 (hardening overhead measured) closed 2026-08-20 and #5 (reproducible, hardened
deployment) closed 2026-08-17. Hardening landed.

## Consequences

**Good.** The written record now matches production. M0 stops waiting on a load test nobody has
started. Hardening was kept rather than traded away for headroom. #18 and #39 remain useful — as
evidence for the ceilings question below rather than as blockers on a live host.

**Bad, stated honestly.**

- This decision is ratified **without the measurements it named**. No figure for peak memory
  under load exists for this host, and none is cited here. The precedent is uncomfortable: an ADR
  filed specifically to gate work was outrun by the work, and ratifying is the least-bad
  response, not a good one.
- The live relay is very likely running **cluster-sized defaults**. `BUZZ_MAX_CONNECTIONS`
  defaults to 10,000, `BUZZ_SEND_BUFFER` to 1,000 messages *per connection*, and
  `BUZZ_MAX_CONCURRENT_HANDLERS` to 1,024 (`crates/buzz-relay/src/config.rs`).
  `deploy/compose/compose.yml` declares no memory limits on any service, so nothing bounds
  overcommit. The only place the cohort ever templated `BUZZ_MAX_CONNECTIONS` is
  `launchpad/deploy/archived/ansible/roles/relay_config/templates/env.j2` — **archived** — and the
  archived hardening spec explicitly instructed setting it to a measured ceiling rather than the
  default. With 496 MB of swap as the only cushion, exceeding it means the OOM killer, not
  gradual slowness.
- **Disk sizing remains an estimate**, not a measurement. The local VM's disk is deliberately much
  smaller, so it could never settle this, and nothing since has.

**Follow-up, not decided here.** The relay's connection, send-buffer and Postgres pool ceilings,
plus per-service memory limits in compose, need their own ADR. That is the more useful question
now that the host is fixed: not "will it fit" but "what limits do we set so it cannot not-fit".
#18 and #39 supply its evidence.

## Security implications

The sizing-versus-hardening trade this ADR was written to prevent was not made — #20 and #5 both
closed, so the baseline is in place.

What remains is availability, not confidentiality. While the ceilings sit at their cluster-sized
defaults on a 1.9 Gi host, resource exhaustion is cheaper than it should be: the relay will
accept far more load than the host can hold before any limit trips, and the Postgres writer and
reader pools default to 50 each, exactly exhausting Postgres's own default `max_connections=100`.
That is a real exposure for an internet-facing host, and it is the reason the follow-up ADR above
should not wait on #39.

## Provenance

Decided by @tucktuck101 in conversation on 2026-08-21, after asking for and receiving a
recommendation to ratify rather than continue holding for #39.

Drafted by an AI agent (Claude Opus 5). Relay reachability and client authentication were verified
in that session. Configuration defaults were read from `crates/buzz-relay/src/config.rs` and
`deploy/compose/compose.yml`. **No resource figure on the live host was measured** — neither for
this record nor before the deployment it ratifies.

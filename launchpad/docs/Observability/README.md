# Buzz observability

Vendor-neutral documentation of Buzz product instrumentation and monitorability: what
the product emits, what context it carries, how signals correlate, what can be diagnosed,
where export boundaries sit, and what remains unknown.

Platform and operations design is separate. These pages do not prescribe collection or
storage products, retention infrastructure, or deployment topology.

## Current state

- [Coverage inventory](current-state/coverage.md) — the canonical component coverage and assessment-progress record ([issue #462](https://github.com/launchpad-26/buzz/issues/462))
- [Overview](current-state/overview.md) — the high-level read for a time-constrained reader ([issue #457](https://github.com/launchpad-26/buzz/issues/457))
- [Relay](current-state/relay.md) — relay instrumentation and monitorability ([issue #458](https://github.com/launchpad-26/buzz/issues/458))
- [Desktop](current-state/desktop.md) — desktop instrumentation and monitorability ([issue #459](https://github.com/launchpad-26/buzz/issues/459))
- [Web](current-state/web.md) — browser instrumentation and monitorability ([issue #460](https://github.com/launchpad-26/buzz/issues/460))

The coverage inventory is the canonical record that every in-scope component has an
assessment owner and whether its current-state evidence is complete. Component assignment
is complete; most component assessments are still pending. The runtime pages contain the
current evidence while keeping decisions and future implementation out of these documents.

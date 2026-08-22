# Buzz observability

Vendor-neutral documentation of Buzz product instrumentation and monitorability: what
the product emits, what context it carries, how signals correlate, what can be diagnosed,
where export boundaries sit, and what remains unknown.

Platform and operations design is separate. These pages do not prescribe collection or
storage products, retention infrastructure, or deployment topology.

## Current state

- [Overview](current-state/overview.md) — the high-level read for a time-constrained reader ([issue #457](https://github.com/launchpad-26/buzz/issues/457))
- [Relay](current-state/relay.md) — relay instrumentation and monitorability ([issue #458](https://github.com/launchpad-26/buzz/issues/458))
- [Desktop](current-state/desktop.md) — desktop instrumentation and monitorability ([issue #459](https://github.com/launchpad-26/buzz/issues/459))
- [Web](current-state/web.md) — browser instrumentation and monitorability ([issue #460](https://github.com/launchpad-26/buzz/issues/460))

Each current-state page is an evidence-backed documentation scaffold. Its tracking issue
owns replacing the placeholders with verified findings while keeping decisions and future
implementation out of the document.

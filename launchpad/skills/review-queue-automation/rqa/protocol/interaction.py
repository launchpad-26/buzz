"""`PROBE_MARKER` and the probe-invocation contract note (E-19/E-24).

`PROBE_MARKER` is the name of the marker file E-24's liveness probe places in an
otherwise-empty bundle directory in place of real PR content and the review
protocol. Per the published E-19 interaction contract, a conforming harness invoked
against a directory containing only this file — no PR content, no protocol
definition, nothing to review — is being probed for liveness, not asked to review
anything: it MUST exit `0` and write no `verdict.json` to the (empty) output path.

`rqa.supply`'s `HarnessProber.probe()` (E-24) judges exactly those two facts against
the harness's own process exit and output directory. P-04 supplies only the marker
name here; it never invokes a harness, assembles a bundle, reads a bundle directory,
or resolves an output path itself (P-04 §4, §7) — this module holds no I/O.
"""

from __future__ import annotations

#: Filename placed alone in an otherwise-empty bundle directory for an E-24 probe.
PROBE_MARKER = "PROBE_ONLY"

"""`rqa.harness` — P-06, `architecture/code/P-06-harness-interface.md`.

The only part of RQA that hands pull-request bytes to a model. It plans the obligations
a review must regenerate, owns the whole finite panel loop, obtains a fresh P-05
reservation immediately before every invocation including the one permitted transient
retry, nonce-envelopes every PR byte, enforces the E-19 provider-role and
injection-conformance contract, validates each verdict through E-08, attests and reports
every attempt, and returns one `PanelResult` whose evidence cutoff is captured after the
final attempt.

**The public surface is exactly §1's six names** — `plan`, `run`, `SupplyPort`,
`HarnessAdapter`, `BundleFailure` and `HarnessError`. Everything else this package needs
is a submodule name: the adapter registry, the conformance suite, the bundle writer, the
process routine, the classification table, the two other error types. "No extra public
surface" is a contract clause, not a preference, and the surface test enforces it.

**Two of those six are imports, not declarations.** `BundleFailure` is `CONTRACTS.md`
§5's shared E-07 return alternative and `SupplyPort` is the Protocol `rqa/edges.py`
landed from §9's E-07 comment. The seam rule is absolute: the shared vocabulary has
exactly one definition and a lane imports it. So `panel.py` imports `SupplyPort` from
`rqa.contracts` rather than restating the three-method Protocol §2 prints, and this file
re-exports it. An import is not a declaration; `rqa.supply`'s `__init__` makes the same
arrangement for the six §5 types it hands back.

**What this package calls, and nothing else** (§1): `rqa.protocol.paths.matches()` for
every path comparison, E-08 `validate`, `RecordWriter.append`, and the methods of the
injected `SupplyPort`. It never imports or calls P-05's `route`, `reserve` or `consumed`
directly — P-02 constructs the port over them — and it never judges, decides a
disposition, submits GitHub output, mutates job state, probes a route, or manufactures a
fallback (§7).
"""

from __future__ import annotations

from rqa.contracts import BundleFailure, SupplyPort
from rqa.harness.adapters import HarnessAdapter
from rqa.harness.errors import HarnessError
from rqa.harness.panel import run
from rqa.harness.risk import plan

__all__ = [
    "plan",
    "run",
    "SupplyPort",
    "HarnessAdapter",
    "BundleFailure",
    "HarnessError",
]

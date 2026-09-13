"""P-06's programming and deployment errors — `code/P-06-harness-interface.md` §2.

Exactly the three the contract names, and no fourth. `CONTRACTS.md`'s preamble draws
the line this module sits on: *policy, availability and budget outcomes are values,
programming errors are `*Error` exceptions*. Nothing here is ever returned, recorded
as an outcome, or converted into a `PanelResult`; a caller that sees one of these has
a defect in itself or in its deployment, not an unlucky review.

`HarnessError` is also the catch-all the loop raises when a collaborator breaks its
own contract — a `SupplyPort.reserve` answering with neither a `Reservation` nor a
`Refusal` (§3.2 step 3), a `SupplyPort.route` handing back a route the cursor already
excludes (§3.2 step 1, the clause that makes the ladder finite), or a route that is
neither a built-in alias nor an operator-declared `command` (§3.3). Those are the
`JobBlockingError` sites U-RESILIENCE-04 carries into this part: a misconfiguration
stops the job rather than walking silently down the ladder.

**Nothing raised here may carry PR bytes or a credential.** Every message in this
package is built from RQA-generated identifiers — route fields RQA itself selected,
bundle-relative artifact names, reason *codes* — never from pull-request content,
harness stdout, or a validator reason string, and every `raise` inside an `except`
that could have untrusted or secret bytes in scope uses `from None` so the traceback
chain cannot carry them either.
"""

from __future__ import annotations

__all__ = ["EmptyPlanError", "HarnessError", "ProtocolVersionUnknown"]


class HarnessError(Exception):
    """A programming or deployment defect in the panel loop or one of its collaborators."""


class EmptyPlanError(HarnessError):
    """`run()` was called with a `Plan` that planned no obligation.

    §3.1's closing sentence: "A caller invoking `run()` with no planned obligation gets
    `EmptyPlanError`, never an invented evidence outcome." Lifecycle skips `run()` when
    nothing was regenerated; reaching it anyway is P-02's defect, and answering with an
    empty complete panel would manufacture exactly the successful outcome RQA-FR-037
    forbids.
    """


class ProtocolVersionUnknown(HarnessError):
    """The pinned `Snapshot.protocol_hash` is not the protocol this build packages.

    The bundle manifest binds a review to the exact protocol definition it ran under,
    and §3.3 hands the harness "the immutable protocol instruction" this build ships.
    When the snapshot pins a different one, the two cannot both be true: RQA cannot
    supply a protocol it does not have, and emitting the one it does have under the
    pinned hash would silently review under an unpinned contract. There is no
    negotiation and no multi-version dispatch (`rqa/protocol/version.py`), so this is a
    deployment error rather than a `BundleFailure` — a `BundleFailure` says the bundle
    could not be written, not that the build is wrong.
    """

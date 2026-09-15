"""`raise_()` and `pending()` — the E-11 entry points — `code/P-11-escalation.md` §3.

**No transport.** Neither function sends mail, writes a file outside the store, executes
a command, or opens a network connection. RQA-FR-025/RQA-BR-013 are met structurally:
there is no notification code path in this module for any cause. The escalation *is*
the durable human request; `pending()` is the whole of the human-facing read, on the
human's own schedule (U-AUTHORITY-12's binning).

**A closed cause vocabulary and a specific question, always.** `raise_` step 1 rejects
anything outside the five `EscalationCause` values (RQA-FR-026: no `other`, no sixth
value coerced past the enum); step 2 rejects a blank or all-whitespace question, because
a blank string can never be the specific unresolved decision, conflicting judgement,
evidence gap, required information or authority requirement RQA-FR-026 requires.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime, timezone

from rqa.contracts import Escalation, EscalationCause, Job, RecordWriter

from rqa.escalation.store import EscalationStore

__all__ = ["EscalationError", "raise_", "pending", "utcnow"]

#: Membership against this plain `frozenset`, not `cause not in EscalationCause`:
#: `EnumType.__contains__` raises `TypeError` for a non-member value under Python 3.11
#: (the acceptance venv), and only stops raising — returning `False` instead — from
#: 3.12. A `str, Enum` member equals and hashes as its own string value, so membership
#: here is identical for both a real member and a raw matching string, and version-safe
#: either way. Because the check treats the two shapes identically, `raise_` coerces a
#: passing value with `EscalationCause(cause)` immediately afterwards (F-T2): the
#: membership gate's own documented intent — tolerate a matching raw string exactly
#: like the real member — only holds if the rest of the function receives the real
#: member too, since everything past this gate calls `cause.value`.
_VALID_CAUSES = frozenset(EscalationCause)


class EscalationError(Exception):
    """Programming error: `raise_()` or `decide()` received a value outside the shared
    contract (§2) — a cause outside the five, a blank question, a nameless actor or
    basis, an outcome outside the closed vocabulary, or an outcome recorded against a
    cause that is not `authority_requirement`. Never a policy or availability outcome:
    the caller passed something the closed contract already rules out."""


def utcnow() -> datetime:
    """The default wall clock: an aware UTC timestamp."""
    return datetime.now(timezone.utc)


def raise_(
    *,
    job: Job,
    cause: EscalationCause,
    question: str,
    context: Mapping,
    record: RecordWriter,
    store: EscalationStore,
) -> Escalation:
    """§3 E-11 `raise_`, in order. Every branch returns or raises."""
    if cause not in _VALID_CAUSES:
        # F-T1: `context`/`question` are unused on this branch and can carry
        # PR-derived text; unbind them before raising so neither is reachable from
        # this frame once the exception is introspected (`del` before `raise`, not
        # after: control never returns to this frame afterwards). `cause` stays
        # bound — it is not PR-derived free text, and the message and T2 both name it.
        del question, context
        raise EscalationError(f"{cause!r} is not one of the five EscalationCause values")
    # F-T2: the gate above tolerates a raw string equal to a canonical value exactly
    # like the real member (its own comment says so); coerce here so that tolerance
    # holds all the way through, instead of crashing on `cause.value` below with an
    # uncontracted `AttributeError` for that one input shape. A no-op for an
    # already-real member: `EscalationCause(member) is member`.
    cause = EscalationCause(cause)
    if question.strip() == "":
        del context  # F-T1: unused on this branch; unbind before raising.
        raise EscalationError("a raised escalation must name a specific, non-blank question")

    raised_at = utcnow()

    # AppendFailed propagates unchanged: the caller's transition fails with it (E-13),
    # and no pending index row is ever written without a record entry behind it (§3).
    entry = record.append(
        job.id,
        kind="escalation",
        payload={
            "cause": cause.value,
            "question": question,
            "context": dict(context),
            "head_sha": job.head_sha,
            "snapshot_hash": job.snapshot_hash,
        },
    )

    escalation_id = store.insert(
        job_id=job.id,
        entry_seq=entry.seq,
        cause=cause,
        question=question,
        context=context,
        head_sha=job.head_sha,
        snapshot_hash=job.snapshot_hash,
        raised_at=raised_at,
    )
    return Escalation(
        id=escalation_id,
        job_id=job.id,
        cause=cause,
        question=question,
        context=context,
        head_sha=job.head_sha,
        snapshot_hash=job.snapshot_hash,
        entry_seq=entry.seq,
        raised_at=raised_at,
    )


def pending(*, store: EscalationStore) -> tuple[Escalation, ...]:
    """§3 E-11 `pending`: every open row, oldest first, as a complete `Escalation`.

    One branch: always returns, an empty state directory yields an empty tuple. This is
    the whole of the human-facing surface `rqa status`/the `decide` CLI reads before
    asking the operator which escalation they mean.
    """
    return tuple(
        Escalation(
            id=row.id,
            job_id=row.job_id,
            cause=row.cause,
            question=row.question,
            context=row.context,
            head_sha=row.head_sha,
            snapshot_hash=row.snapshot_hash,
            entry_seq=row.entry_seq,
            raised_at=row.raised_at,
        )
        for row in store.pending()
    )

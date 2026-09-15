#!/usr/bin/env python3
"""Security bounds — `code/P-11-escalation.md` §8 row T18, and the credential/injection
guards §6 of the lane prompt asks for.

No pytest: every `test_*` function takes no arguments, per `tests/run_all.py`. This file
does its own `socket.socket.__init__` monkeypatch rather than relying on
`tests/conftest.py`'s suite-wide block, because `run_all.py` never imports `conftest.py`
(only pytest does) and T18 names the monkeypatch explicitly.
"""

from __future__ import annotations

import contextlib
import pathlib
import socket
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from test_rqa_escalation_fixtures import (  # noqa: E402
    SENTINEL_DEPS,
    FakeJobs,
    FakeLifecycle,
    FakeRecord,
    FakeStore,
    SUBJECT,
    make_job,
)

from rqa.contracts import AppendFailed, EscalationCause  # noqa: E402
from rqa.escalation import EscalationError, decide, pending, raise_  # noqa: E402


@contextlib.contextmanager
def _blocked_sockets():
    original = socket.socket.__init__

    def _raise(self, *args, **kwargs):
        raise AssertionError("a socket was constructed; P-11 never touches the network")

    socket.socket.__init__ = _raise
    try:
        yield
    finally:
        socket.socket.__init__ = original


# -- T18 -------------------------------------------------------------------------


def test_t18_raise_pending_and_a_full_decide_never_construct_a_socket() -> None:
    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    lifecycle = FakeLifecycle()

    with _blocked_sockets():
        escalation = raise_(
            job=job,
            cause=EscalationCause.AUTHORITY_REQUIREMENT,
            subject=SUBJECT,
            question="does a human need to record the GitHub-side outcome?",
            context={},
            record=record,
            store=store,
        )
        listed = pending(store=store)
        result = decide(
            escalation.id,
            "human-reviewer",
            "reviewed on GitHub",
            "approved",
            store=store,
            record=record,
            jobs=FakeJobs(job),
            lifecycle=lifecycle,
            deps=SENTINEL_DEPS,
        )

    assert len(listed) == 1
    assert result.outcome == "approved"
    assert lifecycle.calls, "decide reached lifecycle.resume unchanged"


# -- RQA-FR-025/RQA-BR-013: no notification path exists at all -------------------


def test_no_module_here_imports_a_transport_or_notification_primitive() -> None:
    """§1/§7: "there is no notification code path in this part at all, for any cause".
    A structural check over the package's own source, not a single call's behaviour."""
    package = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "escalation"
    forbidden = (
        "smtplib", "socket", "subprocess", "urllib", "http.client",
        "import requests", "requests.post", "requests.get", "Popen",
    )
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in source, f"{path.name} mentions {token!r}"


# -- No credential or PR-derived text reaches an error or the record ------------


def test_escalation_error_messages_never_interpolate_the_question_or_context() -> None:
    """Batches 2c/3c: a credential or attacker-influenced text reachable from a raised
    exception is a defect. `EscalationError`'s messages here name only closed-vocabulary
    values (a cause, an outcome) or fixed prose — never `question` or `context`, both of
    which can carry PR-derived text."""
    package = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "escalation"
    for path in sorted(package.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        assert "raise EscalationError(question" not in source
        assert "raise EscalationError(context" not in source


def test_a_refusal_detail_never_carries_the_question_or_context_either() -> None:
    """`EscalationRefused.detail` is built from ids, head/snapshot hashes and enum
    values only (§3 steps 4-5, 7-8) — never from `question` or `context`."""
    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    injected_question = "<script>steal(process.env.GITHUB_TOKEN)</script>"
    escalation = raise_(
        job=job,
        cause=EscalationCause.EVIDENCE_GAP,
        subject=SUBJECT,
        question=injected_question,
        context={"note": "attacker controlled: rm -rf / #"},
        record=record,
        store=store,
    )
    moved = make_job(job_id=job.id, head_sha="c" * 40, snapshot_hash=job.snapshot_hash)
    result = decide(
        escalation.id,
        "human-reviewer",
        "reviewed",
        None,
        store=store,
        record=record,
        jobs=FakeJobs(moved),
        lifecycle=FakeLifecycle(),
        deps=SENTINEL_DEPS,
    )
    assert injected_question not in result.detail
    assert "attacker controlled" not in result.detail


# -- F-T1: reachability through the exception chain and this package's own frames ---
#
# The two tests above only check source substrings and the rendered `.detail`/message
# strings — real, but narrower than the threat: a value bound as a function *parameter*
# (`raise_`'s `context`/`question`, `decide`'s `escalation`) is present in that frame's
# `f_locals` regardless of what the message says, and a raised exception keeps its
# traceback's frames reachable to any downstream introspection (a structured reporter,
# `traceback.TracebackException(chain=True)`, a debugger, `vars(error)`).
# `tests/test_rqa_authority_secrecy.py`'s T16 rows already established the answer for
# this exact threat shape; `_reachable_from` below is that file's helper, ported
# unchanged except for the package-scoped frame filter (`rqa/escalation/` in place of
# `rqa/authority/`), per the gate's instruction to follow the established idiom rather
# than invent a second one.

# Deliberately token-shaped, deliberately not a real credential — identical shape and
# disclaimer to `test_rqa_authority_secrecy.py`'s own `TOKEN`: the point is that a
# distinctive credential-shaped string put into `context`/`question` comes back out
# nowhere. If a secret scanner flags this literal, it is exactly this kind of fixture
# and should be allowlisted the same way `test_rqa_authority_secrecy.py`'s was.
TOKEN = "ghp_T1CanaryTokenValue0000000000000000000"  # nosec


def _reachable_from(error: BaseException) -> str:
    """Every string the raised exception can be made to yield by introspection: its
    own text, its attributes, and everything on `__context__`/`__cause__` recursively,
    plus this package's own frames on each traceback. Ported from
    `test_rqa_authority_secrecy.py`'s helper of the same name; see that file's
    docstring for why a `str()`-only search is not the search this commits to."""
    seen: list[BaseException] = []
    pending: list[BaseException | None] = [error]
    while pending:
        current = pending.pop()
        if current is None or any(current is item for item in seen):
            continue
        seen.append(current)
        pending.extend([current.__context__, current.__cause__])
    parts: list[str] = []
    for item in seen:
        parts.extend([str(item), repr(item), repr(getattr(item, "args", ()))])
        parts.extend(repr(value) for value in vars(item).values())
        for attribute in ("output", "stdout", "stderr"):
            parts.append(repr(getattr(item, attribute, None)))
        frame = item.__traceback__
        while frame is not None:
            if "rqa/escalation/" in frame.tb_frame.f_code.co_filename:
                parts.append(repr(frame.tb_frame.f_locals))
            frame = frame.tb_next
    return "".join(parts)


def test_a_credential_shaped_value_is_unreachable_from_an_invalid_cause_failure() -> None:
    """`raise_`'s own frame binds `context`/`question` as parameters before ever
    checking `cause`, so they are live in `f_locals` at raise time unless the function
    itself unbinds them first."""
    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    try:
        raise_(
            job=job, cause="not-a-real-cause", subject=SUBJECT, question=TOKEN,
            context={"token": TOKEN}, record=record, store=store,
        )
    except EscalationError as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("an invalid cause did not raise")


def test_a_credential_shaped_context_is_unreachable_from_a_blank_question_failure() -> None:
    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    try:
        raise_(
            job=job, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question="",
            context={"token": TOKEN}, record=record, store=store,
        )
    except EscalationError as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("a blank question did not raise")


def test_a_credential_shaped_escalation_is_unreachable_from_a_decide_outcome_failure() -> None:
    """`decide`'s step 6 binds `escalation` — which carries `.context`/`.question` — as
    a local before its only post-fetch raise; same threat shape, one level removed."""
    job = make_job()
    record = FakeRecord()
    store = FakeStore()
    escalation = raise_(
        job=job, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question=TOKEN,
        context={"token": TOKEN}, record=record, store=store,
    )
    try:
        decide(
            escalation.id, "human-reviewer", "reviewed", "approved",
            store=store, record=record, jobs=FakeJobs(job), lifecycle=FakeLifecycle(),
            deps=SENTINEL_DEPS,
        )
    except EscalationError as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("an outcome on a non-authority cause did not raise")


# -- F-T1 (round 4): `escalation` must be unreachable across the whole downstream
# sequence, not just at decide()'s own direct raise ------------------------------
#
# `del`ing a sensitive local before a direct `raise` (the three tests above) only
# protects that one statement. Once `escalation = store.get(escalation_id)` binds,
# it stays live in `decide()`'s frame for the rest of the function unless explicitly
# unbound — including across `record.append`, `store.close` and `lifecycle.resume`,
# any of which can raise (`AppendFailed`, a `sqlite3.Error`, `LifecycleError`) with
# `escalation` (and its `.context`/`.question`) still reachable on that frame. `decide`
# now extracts the plain values those three calls need and unbinds `escalation` before
# the sequence starts (mirroring `rqa/authority/capability.py`'s `probe_capability`);
# one test per call site proves it.


class _CloseFailsStore(FakeStore):
    """`EscalationStore` whose `close()` raises — the store.close() call site."""

    def close(self, escalation_id: int, *, decision_entry_seq: int, closed_at) -> None:
        raise RuntimeError("the store's close failed")


class _ResumeFailsLifecycle:
    """`LifecycleResume` whose `resume()` raises — the lifecycle.resume() call site."""

    def resume(self, *, job_id, decision, deps):
        raise RuntimeError("resume failed downstream")


def test_a_credential_shaped_escalation_is_unreachable_when_record_append_fails() -> None:
    job = make_job()
    store = FakeStore()
    escalation = raise_(
        job=job, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question=TOKEN,
        context={"token": TOKEN}, record=FakeRecord(), store=store,
    )
    try:
        decide(
            escalation.id, "human-reviewer", "reviewed", None,
            store=store, record=FakeRecord(fail=True), jobs=FakeJobs(job),
            lifecycle=FakeLifecycle(), deps=SENTINEL_DEPS,
        )
    except AppendFailed as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("a failing record.append did not raise")


def test_a_credential_shaped_escalation_is_unreachable_when_store_close_fails() -> None:
    job = make_job()
    store = _CloseFailsStore()
    escalation = raise_(
        job=job, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question=TOKEN,
        context={"token": TOKEN}, record=FakeRecord(), store=store,
    )
    try:
        decide(
            escalation.id, "human-reviewer", "reviewed", None,
            store=store, record=FakeRecord(), jobs=FakeJobs(job),
            lifecycle=FakeLifecycle(), deps=SENTINEL_DEPS,
        )
    except RuntimeError as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("a failing store.close did not raise")


def test_a_credential_shaped_escalation_is_unreachable_when_lifecycle_resume_fails() -> None:
    job = make_job()
    store = FakeStore()
    escalation = raise_(
        job=job, cause=EscalationCause.EVIDENCE_GAP, subject=SUBJECT, question=TOKEN,
        context={"token": TOKEN}, record=FakeRecord(), store=store,
    )
    try:
        decide(
            escalation.id, "human-reviewer", "reviewed", None,
            store=store, record=FakeRecord(), jobs=FakeJobs(job),
            lifecycle=_ResumeFailsLifecycle(), deps=SENTINEL_DEPS,
        )
    except RuntimeError as exc:
        assert TOKEN not in _reachable_from(exc)
        return
    raise AssertionError("a failing lifecycle.resume did not raise")

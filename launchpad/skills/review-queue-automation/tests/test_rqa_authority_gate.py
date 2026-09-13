#!/usr/bin/env python3
"""`rqa.authority.gate` — `code/P-08-authority-gate.md` §8 rows T1-T13 and T15.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Every test drives the real `Gate` against fakes for `RecordWriter`, `GithubProbe` and
`CapabilityStore`, which is what §8 asks for. Three things these tests deliberately do
NOT do:

* They never reach GitHub, and never run `gh`. The probe is injected, as E-04 injects
  it; `credential()` is never on the path because the fake probe replaces the module
  function that calls it.
* They never assert that `rqa.remediation` is absent, and never assert that the
  mechanical tool registry is empty. P-10 (Task #2194) lands that module in a later
  batch, and a test pinned to today's `ImportError` would have to be deleted then. T7
  exercises membership against a *substituted* registry instead, which is the behaviour
  the contract fixes forever: a configured tool in the set passes, one outside it is
  `TOOL_NOT_IN_SET`.
* They never assert that some other package under `rqa/` is absent. `rqa.github`
  (#2193) lands in this same wave.
"""

from __future__ import annotations

import contextlib
import importlib
import pathlib
import sys
from datetime import datetime, timezone

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.authority.gate as gate_module  # noqa: E402
from rqa.authority.capability import CapabilityProof  # noqa: E402
from rqa.authority.gate import Gate, GateError  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    AppendFailed,
    Blocking,
    Budget,
    CapabilityReading,
    Category,
    Deny,
    DenyReason,
    Entry,
    External,
    GithubUnavailable,
    Grant,
    Mechanical,
    Policy,
    RemediationPolicy,
    Snapshot,
)

REPO = "launchpad-26/buzz"
JOB = "job-1"
HASH = "a" * 64
ALL_CAPABILITIES = frozenset(
    {"pulls:read", "pulls:write", "contents:read", "contents:write", "checks:read", "issues:write"}
)
PROBED_AT = datetime(2026, 9, 12, 8, 30, 15, tzinfo=timezone.utc)


# -- fakes --------------------------------------------------------------------


class FakeRecord:
    """`RecordWriter`. Keeps every appended row so a test can read the entry the
    returned `Grant`/`Deny` points at."""

    def __init__(self, *, fail_on: str | None = None):
        self.rows: list[tuple[str, str, dict]] = []
        self.fail_on = fail_on

    def append(self, job_id: str, kind: str, payload: dict) -> Entry:
        if self.fail_on is not None and kind == self.fail_on:
            raise AppendFailed(f"the record refused a {kind} entry")
        self.rows.append((job_id, kind, dict(payload)))
        seq = len(self.rows)
        return Entry(seq=seq, hash=f"{seq:064d}")

    def kinds(self, kind: str) -> list[dict]:
        return [payload for _, entry_kind, payload in self.rows if entry_kind == kind]


class FakeProbe:
    """`GithubProbe`. Counts calls so T10, T11 and T12 can assert on probing itself."""

    def __init__(self, *, capabilities: frozenset[str] = ALL_CAPABILITIES, unavailable: bool = False):
        self.capabilities = capabilities
        self.unavailable = unavailable
        self.calls: list[str] = []
        self.credentials: list[str] = []

    def probe(self, *, repo: str, credential: str):
        self.calls.append(repo)
        self.credentials.append(credential)
        if self.unavailable:
            return GithubUnavailable(op="probe", reason="unreachable", retriable=True)
        return CapabilityReading(
            capabilities=self.capabilities,
            attested_not_proven=frozenset({"admin:org"}),
            login="rqa-operator",
        )


class FakeStore:
    """`CapabilityStore`, in memory, with the §5 `(repo, job_id)` uniqueness."""

    def __init__(self):
        self.rows: dict[tuple[str, str], CapabilityProof] = {}
        self.next_id = 1

    def current(self, repo: str, job_id: str) -> CapabilityProof | None:
        return self.rows.get((repo, job_id))

    def put(self, proof: CapabilityProof) -> int:
        key = (proof.repo, proof.job_id)
        existing = self.rows.get(key)
        identifier = existing.id if existing is not None else self.next_id
        if existing is None:
            self.next_id += 1
        from dataclasses import replace

        self.rows[key] = replace(proof, id=identifier)
        return identifier


# -- builders -----------------------------------------------------------------


def snapshot(
    *,
    repo: str = REPO,
    enabled: frozenset[Activity] = frozenset(),
    categories: frozenset[Category] = frozenset({Category.MECHANICAL, Category.PROCEDURAL}),
    tools: frozenset[str] = frozenset({"ruff"}),
) -> Snapshot:
    return Snapshot(
        hash=HASH,
        repo=repo,
        protocol_hash="b" * 64,
        authority={activity: activity in enabled for activity in Activity},
        routes=(),
        external=External(allowed=False, deny_label=""),
        policy=Policy(
            version="unversioned",
            obligations=(),
            blocking=Blocking(categories=frozenset(), severities=frozenset(), corroboration=1),
            mechanical=Mechanical(categories=categories, tools=tools),
            assurance={},
            remediation=RemediationPolicy(allow_forks=False),
        ),
        budget=Budget(per_pr_tokens=None, per_repo_daily_tokens=None, per_model_daily_tokens=None),
    )


def gate(*, repos: frozenset[str] = frozenset({REPO})) -> Gate:
    return Gate(repos=repos)


FAKE_TOKEN = "gho_fake_token_for_the_gate_suite"  # nosec - a sentinel, not a credential


@contextlib.contextmanager
def no_real_credential():
    """Substitute E-22 for the duration of one call.

    Every test in this file runs inside this: the gate resolves a credential through
    `capability.credential()` before it probes, and no test in this skill may launch a
    real `gh` or reach GitHub. `capability`'s own tests exercise the real function
    against a substituted process instead.
    """
    capability = importlib.import_module("rqa.authority.capability")
    original = capability.credential
    capability.credential = lambda: FAKE_TOKEN
    try:
        yield
    finally:
        capability.credential = original


def ask(
    *,
    activity: Activity = Activity.REVIEW,
    snap: Snapshot | None = None,
    repo: str = REPO,
    job_id: str = JOB,
    categories: frozenset[Category] | None = None,
    record: FakeRecord | None = None,
    github: FakeProbe | None = None,
    store: FakeStore | None = None,
    subject: Gate | None = None,
):
    with no_real_credential():
        return (subject or gate()).grant(
            repo=repo,
            activity=activity,
            snapshot=snap,
            job_id=job_id,
            categories=categories,
            record=record or FakeRecord(),
            github=github or FakeProbe(),
            store=store or FakeStore(),
        )


@contextlib.contextmanager
def tool_set(registry: dict):
    """Substitute P-10's registry lookup for the duration of one test.

    The lookup point, not the module: the gate resolves the registry at call time
    precisely so this substitution is possible whether or not P-10 is present.
    """
    original = gate_module._mechanical_tool_set
    gate_module._mechanical_tool_set = lambda: registry
    try:
        yield
    finally:
        gate_module._mechanical_tool_set = original


def stored_proof(store: FakeStore, *, repo: str = REPO, job_id: str = JOB) -> CapabilityProof:
    proof = store.current(repo, job_id)
    assert proof is not None, "expected a persisted capability proof"
    return proof


# -- T1: no snapshot ----------------------------------------------------------


def test_t1_every_activity_without_a_snapshot_is_denied_no_snapshot() -> None:
    for activity in Activity:
        record = FakeRecord()
        answer = ask(activity=activity, snap=None, record=record)
        assert isinstance(answer, Deny), activity
        assert answer.reason is DenyReason.NO_SNAPSHOT, activity
        assert answer.activity is activity
        assert len(record.kinds("grant")) == 1, activity


def test_t1_no_snapshot_never_probes_and_the_detail_names_the_repository() -> None:
    probe = FakeProbe()
    answer = ask(activity=Activity.MERGE, snap=None, github=probe)
    assert probe.calls == []
    assert REPO in answer.detail


# -- T2: everything disabled --------------------------------------------------


def test_t2_a_snapshot_with_all_six_disabled_denies_all_six_not_enabled() -> None:
    # `remediate` is asked with a category set and a tool the registry knows, because
    # §3 runs step 4 before step 6: a remediation call that fails its category or tool
    # check never reaches the enabled check, and this row is about the enabled check.
    for activity in Activity:
        categories = frozenset({Category.MECHANICAL}) if activity is Activity.REMEDIATE else None
        with tool_set({"ruff": object()}):
            answer = ask(activity=activity, snap=snapshot(), categories=categories)
        assert isinstance(answer, Deny), activity
        assert answer.reason is DenyReason.NOT_ENABLED, activity


def test_t2_a_disabled_activity_is_never_probed() -> None:
    probe = FakeProbe()
    ask(activity=Activity.APPROVE, snap=snapshot(), github=probe)
    assert probe.calls == []


# -- T3: independence (RQA-NFR-017) -------------------------------------------


def test_t3_exactly_one_enabled_activity_grants_that_one_and_denies_the_other_five() -> None:
    for enabled in Activity:
        snap = snapshot(enabled=frozenset({enabled}))
        for activity in Activity:
            categories = (
                frozenset({Category.MECHANICAL}) if activity is Activity.REMEDIATE else None
            )
            with tool_set({"ruff": object()}):
                answer = ask(activity=activity, snap=snap, categories=categories)
            if activity is enabled:
                assert isinstance(answer, Grant), (enabled, activity)
                assert answer.activity is activity
            else:
                assert isinstance(answer, Deny), (enabled, activity)
                assert answer.reason is DenyReason.NOT_ENABLED, (enabled, activity)


def test_t3_merge_is_never_implied_by_approve() -> None:
    """The two are separately configured and separately required (RQA-NFR-017)."""
    snap = snapshot(enabled=frozenset({Activity.APPROVE}))
    assert isinstance(ask(activity=Activity.APPROVE, snap=snap), Grant)
    merge = ask(activity=Activity.MERGE, snap=snap)
    assert isinstance(merge, Deny)
    assert merge.reason is DenyReason.NOT_ENABLED


def test_t3_approve_is_never_implied_by_merge() -> None:
    snap = snapshot(enabled=frozenset({Activity.MERGE}))
    assert isinstance(ask(activity=Activity.MERGE, snap=snap), Grant)
    approve = ask(activity=Activity.APPROVE, snap=snap)
    assert isinstance(approve, Deny)
    assert approve.reason is DenyReason.NOT_ENABLED


# -- T4: a capability the credential does not have ----------------------------


def test_t4_a_missing_required_capability_is_denied_with_the_missing_set_in_detail() -> None:
    snap = snapshot(enabled=frozenset({Activity.MERGE}))
    probe = FakeProbe(capabilities=frozenset({"pulls:write"}))  # contents:write is absent
    answer = ask(activity=Activity.MERGE, snap=snap, github=probe)
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.CAPABILITY_MISSING
    assert "contents:write" in answer.detail
    assert "pulls:write" not in answer.detail


def test_t4_an_unavailable_adapter_denies_every_activity_capability_missing() -> None:
    """§4: `GithubUnavailable` is persisted as an empty capability set, so nothing is
    granted on trust until a later job re-probes."""
    for activity in Activity:
        snap = snapshot(enabled=frozenset({activity}))
        categories = frozenset({Category.MECHANICAL}) if activity is Activity.REMEDIATE else None
        store = FakeStore()
        with tool_set({"ruff": object()}):
            answer = ask(
                activity=activity,
                snap=snap,
                categories=categories,
                github=FakeProbe(unavailable=True),
                store=store,
            )
        assert isinstance(answer, Deny), activity
        assert answer.reason is DenyReason.CAPABILITY_MISSING, activity
        assert stored_proof(store).capabilities == frozenset(), activity


# -- T5: remediation without categories ---------------------------------------


def test_t5_remediate_without_categories_is_category_required() -> None:
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}))
    for categories in (None, frozenset()):
        answer = ask(activity=Activity.REMEDIATE, snap=snap, categories=categories)
        assert isinstance(answer, Deny), categories
        assert answer.reason is DenyReason.CATEGORY_REQUIRED, categories


def test_t5_category_required_precedes_the_enabled_check_and_never_probes() -> None:
    probe = FakeProbe()
    answer = ask(activity=Activity.REMEDIATE, snap=snapshot(), categories=None, github=probe)
    assert answer.reason is DenyReason.CATEGORY_REQUIRED
    assert probe.calls == []


# -- T6: a category that is not mechanical, or not configured -----------------


def test_t6_a_substantive_category_is_category_not_mechanical() -> None:
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}))
    answer = ask(
        activity=Activity.REMEDIATE,
        snap=snap,
        categories=frozenset({Category.MECHANICAL, Category.SECURITY}),
    )
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.CATEGORY_NOT_MECHANICAL
    assert "security" in answer.detail


def test_t6_a_mechanical_category_the_policy_did_not_configure_is_refused() -> None:
    """`CREATION_TIME` is in `MECHANICAL_GROUP` but not in this policy's set."""
    snap = snapshot(
        enabled=frozenset({Activity.REMEDIATE}), categories=frozenset({Category.MECHANICAL})
    )
    answer = ask(
        activity=Activity.REMEDIATE, snap=snap, categories=frozenset({Category.CREATION_TIME})
    )
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.CATEGORY_NOT_MECHANICAL
    assert "creation_time" in answer.detail


def test_t6_every_member_of_the_set_is_verified_not_just_the_first() -> None:
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}))
    answer = ask(
        activity=Activity.REMEDIATE,
        snap=snap,
        categories=frozenset({Category.MECHANICAL, Category.PROCEDURAL, Category.CORRECTNESS}),
    )
    assert answer.reason is DenyReason.CATEGORY_NOT_MECHANICAL
    assert "correctness" in answer.detail


# -- T7: a configured tool outside MECHANICAL_TOOL_SET ------------------------


def test_t7_a_configured_tool_outside_the_registry_is_tool_not_in_set() -> None:
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}), tools=frozenset({"rustfmt"}))
    with tool_set({"ruff": object()}):
        answer = ask(
            activity=Activity.REMEDIATE, snap=snap, categories=frozenset({Category.MECHANICAL})
        )
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.TOOL_NOT_IN_SET
    assert "rustfmt" in answer.detail


def test_t7_a_configured_tool_inside_the_registry_passes_the_membership_check() -> None:
    """The other side of the same substitution: membership is what decides, not the
    presence or absence of P-10."""
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}), tools=frozenset({"ruff"}))
    with tool_set({"ruff": object()}):
        answer = ask(
            activity=Activity.REMEDIATE, snap=snap, categories=frozenset({Category.MECHANICAL})
        )
    assert isinstance(answer, Grant)
    assert answer.categories == frozenset({Category.MECHANICAL})


def test_t7_the_tool_check_runs_after_the_category_checks() -> None:
    """§3 step 4's order: an unknown tool beside a substantive category still reports
    the category, so the operator fixes the more serious refusal first."""
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}), tools=frozenset({"rustfmt"}))
    with tool_set({"ruff": object()}):
        answer = ask(
            activity=Activity.REMEDIATE, snap=snap, categories=frozenset({Category.SECURITY})
        )
    assert answer.reason is DenyReason.CATEGORY_NOT_MECHANICAL


# -- T8: categories on a non-remediation activity -----------------------------


def test_t8_non_remediation_with_non_null_categories_raises_gate_error() -> None:
    snap = snapshot(enabled=frozenset(Activity))
    for activity in Activity:
        if activity is Activity.REMEDIATE:
            continue
        for categories in (frozenset({Category.MECHANICAL}), frozenset()):
            try:
                ask(activity=activity, snap=snap, categories=categories)
            except GateError:
                continue
            raise AssertionError(f"{activity} with categories={categories!r} did not raise")


def test_t8_a_wrong_shape_call_records_nothing() -> None:
    """A programming error is not a decision, so it leaves no `grant` entry to explain."""
    record = FakeRecord()
    try:
        ask(
            activity=Activity.APPROVE,
            snap=snapshot(enabled=frozenset(Activity)),
            categories=frozenset({Category.MECHANICAL}),
            record=record,
        )
    except GateError:
        pass
    assert record.rows == []


# -- T9: a snapshot pinned to another repository ------------------------------


def test_t9_a_snapshot_for_another_repository_raises_gate_error() -> None:
    try:
        ask(snap=snapshot(repo="launchpad-26/other"))
    except GateError as error:
        assert "launchpad-26/other" in str(error)
        return
    raise AssertionError("a mismatched snapshot repo did not raise")


def test_t9_the_mismatch_is_checked_before_any_authority_is_read() -> None:
    probe = FakeProbe()
    record = FakeRecord()
    try:
        ask(snap=snapshot(repo="launchpad-26/other", enabled=frozenset(Activity)), github=probe, record=record)
    except GateError:
        pass
    assert probe.calls == []
    assert record.rows == []


# -- T10: an unmanaged repository ---------------------------------------------


def test_t10_an_unconfigured_repository_is_denied_before_any_probe() -> None:
    probe = FakeProbe()
    record = FakeRecord()
    answer = ask(
        repo="attacker/repo",
        snap=None,
        github=probe,
        record=record,
        subject=gate(repos=frozenset({REPO})),
    )
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.REPO_NOT_MANAGED
    assert probe.calls == []
    assert len(record.kinds("grant")) == 1
    assert record.kinds("attestation") == []


def test_t10_repo_not_managed_precedes_even_a_fully_enabling_snapshot() -> None:
    """Step 1 is first so a snapshot cannot make the gate answer for a repository the
    operator never configured."""
    probe = FakeProbe()
    answer = ask(
        repo="attacker/repo",
        snap=snapshot(repo="attacker/repo", enabled=frozenset(Activity)),
        activity=Activity.MERGE,
        github=probe,
        subject=gate(repos=frozenset({REPO})),
    )
    assert answer.reason is DenyReason.REPO_NOT_MANAGED
    assert probe.calls == []


def test_t10_a_gate_with_no_configured_repositories_answers_for_none() -> None:
    answer = ask(snap=snapshot(enabled=frozenset(Activity)), subject=gate(repos=frozenset()))
    assert answer.reason is DenyReason.REPO_NOT_MANAGED


# -- T11 and T12: one probe per job, per repository ---------------------------


def test_t11_two_calls_in_one_job_probe_once_and_reuse_the_stored_proof() -> None:
    snap = snapshot(enabled=frozenset({Activity.REVIEW, Activity.COMMENT}))
    probe = FakeProbe()
    store = FakeStore()
    record = FakeRecord()
    first = ask(activity=Activity.REVIEW, snap=snap, github=probe, store=store, record=record)
    second = ask(activity=Activity.COMMENT, snap=snap, github=probe, store=store, record=record)
    assert isinstance(first, Grant) and isinstance(second, Grant)
    assert probe.calls == [REPO]
    assert first.capability_proof_id == second.capability_proof_id
    assert len(record.kinds("attestation")) == 1
    assert len(record.kinds("grant")) == 2


def test_t12_two_jobs_on_one_repository_probe_twice() -> None:
    snap = snapshot(enabled=frozenset({Activity.REVIEW}))
    probe = FakeProbe()
    store = FakeStore()
    record = FakeRecord()
    ask(snap=snap, job_id="job-1", github=probe, store=store, record=record)
    ask(snap=snap, job_id="job-2", github=probe, store=store, record=record)
    assert probe.calls == [REPO, REPO]
    assert len(record.kinds("attestation")) == 2
    assert store.current(REPO, "job-1").id != store.current(REPO, "job-2").id


def test_t12_the_attestation_carries_what_is_attested_but_not_proven() -> None:
    """ADR-0062 §3: the residual is recorded, not hidden."""
    snap = snapshot(enabled=frozenset({Activity.REVIEW}))
    record = FakeRecord()
    ask(snap=snap, record=record)
    attestation = record.kinds("attestation")[0]
    assert attestation["login"] == "rqa-operator"
    assert attestation["attested_not_proven"] == ["admin:org"]
    assert attestation["capabilities"] == sorted(ALL_CAPABILITIES)
    assert "probed_at" in attestation


# -- T13: the record refuses the entry ----------------------------------------


def test_t13_an_append_failure_propagates_instead_of_returning_an_answer() -> None:
    snap = snapshot(enabled=frozenset({Activity.REVIEW}))
    try:
        ask(snap=snap, record=FakeRecord(fail_on="grant"))
    except AppendFailed:
        return
    raise AssertionError("AppendFailed did not propagate out of grant()")


def test_t13_an_append_failure_on_a_deny_propagates_too() -> None:
    try:
        ask(snap=None, record=FakeRecord(fail_on="grant"))
    except AppendFailed:
        return
    raise AssertionError("AppendFailed did not propagate out of a denied grant()")


def test_t13_an_append_failure_on_the_attestation_propagates() -> None:
    snap = snapshot(enabled=frozenset({Activity.REVIEW}))
    try:
        ask(snap=snap, record=FakeRecord(fail_on="attestation"))
    except AppendFailed:
        return
    raise AssertionError("AppendFailed did not propagate out of the attestation append")


# -- T15: determinism ---------------------------------------------------------


def test_t15_the_same_inputs_twice_give_the_same_answer_and_two_grant_entries() -> None:
    snap = snapshot(enabled=frozenset({Activity.REVIEW}))
    store = FakeStore()
    record = FakeRecord()
    probe = FakeProbe()
    first = ask(snap=snap, store=store, record=record, github=probe)
    second = ask(snap=snap, store=store, record=record, github=probe)
    assert isinstance(first, Grant) and isinstance(second, Grant)
    assert first.activity == second.activity
    assert first.repo == second.repo
    assert first.snapshot_hash == second.snapshot_hash
    assert first.capability_proof_id == second.capability_proof_id
    assert first.categories == second.categories
    assert first.entry_seq != second.entry_seq
    assert len(record.kinds("grant")) == 2


def test_t15_a_denied_answer_is_equally_repeatable() -> None:
    record = FakeRecord()
    first = ask(snap=snapshot(), record=record)
    second = ask(snap=snapshot(), record=record)
    assert (first.reason, first.detail) == (second.reason, second.detail)
    assert len(record.kinds("grant")) == 2


# -- the recorded payload (§6) ------------------------------------------------


def test_every_result_records_one_grant_entry_with_the_six_documented_fields() -> None:
    snap = snapshot(enabled=frozenset({Activity.REMEDIATE}))
    record = FakeRecord()
    with tool_set({"ruff": object()}):
        answer = ask(
            activity=Activity.REMEDIATE,
            snap=snap,
            categories=frozenset({Category.PROCEDURAL, Category.MECHANICAL}),
            record=record,
        )
    payload = record.kinds("grant")[0]
    assert set(payload) == {
        "activity",
        "snapshot_hash",
        "categories",
        "capability_proof_id",
        "decision",
        "reason",
        "detail",
    }
    assert payload["activity"] == "remediate"
    assert payload["snapshot_hash"] == HASH
    assert payload["categories"] == ["mechanical", "procedural"]
    assert payload["decision"] == "granted"
    assert payload["reason"] is None
    assert payload["capability_proof_id"] == answer.capability_proof_id


def test_a_denial_records_its_reason_and_its_detail() -> None:
    record = FakeRecord()
    answer = ask(snap=None, record=record)
    payload = record.kinds("grant")[0]
    assert payload["decision"] == "denied"
    assert payload["reason"] == DenyReason.NO_SNAPSHOT.value
    assert payload["detail"] == answer.detail
    assert payload["snapshot_hash"] is None
    assert payload["capability_proof_id"] is None


def test_the_returned_value_carries_the_entry_seq_of_its_own_entry() -> None:
    record = FakeRecord()
    first = ask(snap=None, record=record)
    second = ask(snap=None, record=record)
    assert (first.entry_seq, second.entry_seq) == (1, 2)


# -- wrong-shape calls --------------------------------------------------------


def test_an_activity_outside_the_closed_vocabulary_raises_gate_error() -> None:
    for bogus in ("review", None, 3):
        try:
            ask(activity=bogus, snap=snapshot())
        except GateError:
            continue
        raise AssertionError(f"activity={bogus!r} did not raise")


def test_an_empty_repo_or_job_id_raises_gate_error() -> None:
    for kwargs in ({"repo": ""}, {"job_id": ""}):
        try:
            ask(snap=None, **kwargs)
        except GateError:
            continue
        raise AssertionError(f"{kwargs} did not raise")


# -- the free function and its configured set ---------------------------------


def test_the_free_grant_is_fail_closed_when_no_configured_set_is_wired() -> None:
    """`_configured_repositories()` is empty unwired, so the module-level entry point
    answers for no repository at all."""
    answer = gate_module.grant(
        repo=REPO,
        activity=Activity.REVIEW,
        snapshot=snapshot(enabled=frozenset(Activity)),
        job_id=JOB,
        categories=None,
        record=FakeRecord(),
        github=FakeProbe(),
        store=FakeStore(),
    )
    assert isinstance(answer, Deny)
    assert answer.reason is DenyReason.REPO_NOT_MANAGED


def test_the_free_grant_answers_through_the_same_gate_once_the_set_is_wired() -> None:
    original = gate_module._configured_repositories
    gate_module._configured_repositories = lambda: frozenset({REPO})
    try:
        with no_real_credential():
            answer = gate_module.grant(
                repo=REPO,
                activity=Activity.REVIEW,
                snapshot=snapshot(enabled=frozenset({Activity.REVIEW})),
                job_id=JOB,
                categories=None,
                record=FakeRecord(),
                github=FakeProbe(),
                store=FakeStore(),
            )
    finally:
        gate_module._configured_repositories = original
    assert isinstance(answer, Grant)
    assert answer.activity is Activity.REVIEW

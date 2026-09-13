"""`LifecycleDeps` and the neighbour `Protocol`s — `code/P-02-lifecycle.md` §2 and §4.

`CONTRACTS.md` §9 declares `LifecycleDeps` as an empty `Protocol` whose docstring says
"Its shape is P-02's (`code/P-02-lifecycle.md`) to state". This module states it: the
concrete frozen dataclass of §2, with exactly its fifteen fields. P-01 constructs it with
those fifteen keyword arguments (`code/P-01-intake.md` §3 step 5) and hands it to
`admit`; the contained clients are the only way this part reaches another.

**Every `Protocol` below repeats a `CONTRACTS.md` §9 signature verbatim, for injection.**
§4: "P-02 defines no exchanged type and no alternative convenience overload." Not one
exchanged value type is declared here — every one of them is imported from
`rqa.contracts`, which is the single declaration site for the whole seam. These
declarations exist so a neighbour can be injected and type-checked, not so this part can
have its own view of a shared type.

**`repr` is deliberately field-free.** A frozen dataclass renders every field in its
`repr`, and a `repr` of this bundle appears in a traceback frame, a debugger, a log line
or a chained exception's context. Nine of the fifteen fields are live clients — the
GitHub client holds a credential for the duration of a call, and the authority client
reaches one through E-22. Batches 2c and 3c both found credentials reachable exactly that
way (frame locals and `__context__`), so this class renders its arity and nothing else.
`dataclasses` does not overwrite a `__repr__` defined in the class body, so §2's
`@dataclass(frozen=True)` stays verbatim and the safe renderer still wins.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal, Protocol

from rqa.contracts import (
    Activity,
    Attempt,
    BreakerStore,
    BundleFailure,
    CapabilityStore,
    CarryOver,
    Category,
    Decision,
    Deny,
    Escalation,
    EscalationCause,
    EscalationStore,
    Facts,
    Finding,
    GithubProbe,
    GithubUnavailable,
    Grant,
    HarnessProber,
    Job,
    Judgement,
    LeaseTaken,
    Mutation,
    PanelResult,
    Plan,
    ProcessRunner,
    RecordReader,
    RecordWriter,
    Refusal,
    RemediationPushed,
    RemediationRefused,
    Reservation,
    Route,
    RouteCursor,
    RouteUnavailable,
    Snapshot,
    SnapshotStore,
    Spend,
    SpendStore,
    Stale,
    SupplyPort,
    ValidationFailure,
)

__all__ = [
    "LifecycleDeps",
    "PolicyClient",
    "AuthorityClient",
    "ReuseClient",
    "SupplyClient",
    "HarnessClient",
    "JudgementClient",
    "RemediationClient",
    "EscalationClient",
    "GithubClient",
]


# --------------------------------------------------------------------------
# §4. Dependencies consumed — every signature is `CONTRACTS.md` §9's, verbatim.
# --------------------------------------------------------------------------


class PolicyClient(Protocol):
    def snapshot_for(
        self,
        *,
        repo: str,
        job: Job | None,
        store: SnapshotStore,
        record: RecordWriter | None,
    ) -> Snapshot | ValidationFailure: ...


class AuthorityClient(Protocol):
    def grant(
        self,
        *,
        repo: str,
        activity: Activity,
        snapshot: Snapshot | None,
        job_id: str,
        categories: frozenset[Category] | None,
        record: RecordWriter,
        github: GithubProbe,
        store: CapabilityStore,
    ) -> Grant | Deny: ...


class ReuseClient(Protocol):
    def carry_over(
        self,
        *,
        job: Job,
        prior: RecordReader,
        facts: Facts,
        snapshot: Snapshot,
        record: RecordWriter,
    ) -> CarryOver: ...


class SupplyClient(Protocol):
    def route(
        self,
        *,
        job: Job,
        obligation: str,
        snapshot: Snapshot,
        facts: Facts,
        cursor: RouteCursor,
        prober: HarnessProber,
        breakers: BreakerStore,
    ) -> tuple[Route, RouteCursor] | RouteUnavailable: ...

    def reserve(
        self,
        *,
        job: Job,
        plan: Plan,
        route: Route,
        snapshot: Snapshot,
        spend: SpendStore,
    ) -> Reservation | Refusal: ...

    def consumed(
        self,
        *,
        job: Job,
        attempt: Attempt,
        reading: int | None,
        reservation: Reservation,
        record: RecordWriter,
        spend: SpendStore,
        breakers: BreakerStore,
    ) -> Spend: ...


class HarnessClient(Protocol):
    def plan(
        self,
        *,
        job: Job,
        facts: Facts,
        snapshot: Snapshot,
        carry: CarryOver,
        record: RecordWriter,
    ) -> Plan: ...

    def run(
        self,
        *,
        job: Job,
        plan: Plan,
        facts: Facts,
        snapshot: Snapshot,
        supply: SupplyPort,
        state_dir: Path,
        record: RecordWriter,
    ) -> PanelResult | BundleFailure: ...


class JudgementClient(Protocol):
    def judge(
        self,
        *,
        job: Job,
        plan: Plan,
        panel: PanelResult,
        carry: CarryOver,
        facts: Facts,
        snapshot: Snapshot,
        decision: Decision | None,
        record: RecordWriter,
    ) -> Judgement: ...


class RemediationClient(Protocol):
    def remediate(
        self,
        *,
        job: Job,
        finding: Finding,
        grant: Grant,
        facts: Facts,
        snapshot: Snapshot,
        state_dir: Path,
        runner: ProcessRunner,
        record: RecordWriter,
    ) -> RemediationPushed | RemediationRefused: ...


class EscalationClient(Protocol):
    def raise_(
        self,
        *,
        job: Job,
        cause: EscalationCause,
        question: str,
        context: Mapping,
        record: RecordWriter,
        store: EscalationStore,
    ) -> Escalation: ...

    def pending(self, *, store: EscalationStore) -> tuple[Escalation, ...]: ...


class GithubClient(Protocol):
    def submit_review(
        self,
        *,
        job: Job,
        state: Literal["APPROVE", "REQUEST_CHANGES"],
        body: str,
        grant: Grant,
        record: RecordWriter,
    ) -> Mutation | Stale | GithubUnavailable: ...

    def comment(
        self, *, job: Job, body: str, grant: Grant, record: RecordWriter
    ) -> Mutation | GithubUnavailable: ...

    def merge(
        self, *, job: Job, grant: Grant, record: RecordWriter
    ) -> Mutation | Stale | GithubUnavailable: ...

    def facts(self, *, job: Job, record: RecordWriter) -> Facts | GithubUnavailable: ...


# --------------------------------------------------------------------------
# §2. The dependency bundle.
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class LifecycleDeps:
    """P-02's dependency bundle, constructed by P-01 (§2).

    `runner` is the E-26 `ProcessRunner` that E-10 requires; it is carried with the
    state-directory execution context and is not a second remediation API. `record` and
    `connection` are the *same* writer and connection every neighbour call receives, so
    a neighbour's entry and this part's transition commit or roll back together
    (`P-12-record.md` §3.1).
    """

    policy: PolicyClient
    authority: AuthorityClient
    supply: SupplyClient
    harness: HarnessClient
    judgement: JudgementClient
    remediation: RemediationClient
    escalation: EscalationClient
    github: GithubClient
    reuse: ReuseClient
    record: RecordWriter
    connection: sqlite3.Connection
    state_dir: Path
    runner: ProcessRunner
    # P-01-owned E-01 callbacks; result types are P-09's, never defined by P-02.
    claim_lease: Callable[..., Mutation | LeaseTaken | GithubUnavailable]
    release_lease: Callable[..., Mutation | GithubUnavailable]

    def __repr__(self) -> str:
        """Arity, never contents: a bundle of live clients must not render itself into a
        traceback, a log line or a chained exception's context. See the module docstring."""
        return f"LifecycleDeps(<{len(fields(self))} injected collaborators; fields elided>)"

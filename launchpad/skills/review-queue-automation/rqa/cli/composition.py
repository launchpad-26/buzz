"""The E-17/E-21 composition root: wires every landed RQA part into one real,
non-mock set of collaborators over one state directory.

`rqa/edges.py`'s E-17 comment states the CLI's job precisely: it is a command
surface, "and adds no logic of its own" (the issue, verbatim). Building the
eighteen collaborators `rqa.intake.tick` and the E-11 `decide()`/`resume()`
round trip need is *not* logic about a disposition, a record, a config or an
escalation — it is wiring, and it is this module's whole job. Every class
below is a thin adapter that forwards to a real, already-landed module-level
function or store; none of them decides anything `rqa/lifecycle/steps.py`
does not already decide.

**Why the `*Client` wrapper classes exist at all.** Each `*Client` Protocol in
`rqa/lifecycle/deps.py` names only a method (`snapshot_for`, `grant`, `route`/
`reserve`/`consumed`, ...), but `rqa/lifecycle/steps.py` and `rqa/lifecycle/
rest.py` also read `.store`/`.github`/`.prober`/`.breakers`/`.spend` straight
off whatever object `tick()` was handed as `policy=`/`authority=`/`supply=`/
`escalation=` (see `tests/test_rqa_intake_tick.py`'s `FakePolicyClient`/
`FakeAuthorityClient` docstrings, which document this exact convention for
the fakes). The wrappers here carry the same attributes for the real stores.

**The one dual role `policy=` must play.** `rqa/intake/tick.py`'s own
admission check calls `_check_admission(repo, store=policy, record=record)` —
it passes tick's whole `policy=` argument where a bare `SnapshotStore` is
expected (`.get`/`.activate`), not `policy.store`. `PolicyClient` below is
therefore both the `PolicyClient` `LifecycleDeps.policy` needs *and* a
`SnapshotStore` by delegation, so the identical object satisfies both of
tick.py's already-landed call sites.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Callable, Mapping
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rqa import authority as authority_mod
from rqa import escalation as escalation_mod
from rqa import harness as harness_mod
from rqa import judgement as judgement_mod
from rqa import policy as policy_mod
from rqa import remediation as remediation_mod
from rqa import reuse as reuse_mod
from rqa import supply as supply_mod
from rqa.authority import SqliteCapabilityStore
from rqa.contracts import (
    Grant,
    Job,
    Plan,
    RecordWriter,
    Reservation,
    Route,
    RouteCursor,
    Spend,
)
from rqa.escalation import SqliteEscalationStore
from rqa.github import (
    GithubAdapter,
    SqliteApiCallStore,
    SqliteEtagStore,
    SqliteMutationStore,
    Transport,
)
from rqa.github import ensure_schema as github_ensure_schema
from rqa.intake import (
    Lease,
    SqliteJobStore,
    SqliteLeaseStore,
    SqlitePrFactsStore,
)
from rqa.intake import ensure_schema as intake_ensure_schema
from rqa.lifecycle import LifecycleDeps
from rqa.policy import SnapshotStore, SqliteSnapshotStore
from rqa.record import SQLiteRecordWriter, anchor_job
from rqa.supply import (
    BreakerStore,
    SpendStore,
    SqliteBreakerStore,
    SqliteSpendStore,
    SubprocessHarnessProber,
    SubprocessProcessRunner,
)

__all__ = ["Composition", "build_composition", "utcnow"]


def utcnow() -> datetime:
    """The one clock every constructor below defaults to, mirroring every
    other part's own `utcnow()`."""
    return datetime.now(timezone.utc)


class PolicyClient:
    """`LifecycleDeps.policy` and, by delegation, the `SnapshotStore`
    `rqa.intake.tick._check_admission` passes this same object as."""

    def __init__(self, store: SnapshotStore) -> None:
        self.store = store

    def snapshot_for(self, **kwargs: Any) -> Any:
        return policy_mod.snapshot_for(**kwargs)

    def get(self, hash: str) -> Any:  # SnapshotStore delegation
        return self.store.get(hash)

    def activate(self, hash: str, raw: Mapping[str, Any], at: datetime) -> Any:
        return self.store.activate(hash, raw, at)


class AuthorityClient:
    """`LifecycleDeps.authority` — carries `.github`/`.store` the way
    `rqa/lifecycle/rest.py`/`steps.py` read them off `deps.authority`."""

    def __init__(self, *, github: GithubAdapter, store: SqliteCapabilityStore,
                 repos: tuple[str, ...] = ()) -> None:
        self.github = github
        self.store = store
        self.gate = authority_mod.Gate(repos=frozenset(repos))

    def grant(self, **kwargs: Any) -> Grant | Any:
        return self.gate.grant(**kwargs)


class SupplyClient:
    """`LifecycleDeps.supply` — carries `.prober`/`.breakers`/`.spend` the way
    `steps.py`'s `_Port` closures read them off `deps.supply`."""

    def __init__(
        self,
        *,
        prober: SubprocessHarnessProber,
        breakers: BreakerStore,
        spend: SpendStore,
    ) -> None:
        self.prober = prober
        self.breakers = breakers
        self.spend = spend

    def route(self, **kwargs: Any) -> tuple[Route, RouteCursor] | Any:
        return supply_mod.route(**kwargs)

    def reserve(self, **kwargs: Any) -> Reservation | Any:
        return supply_mod.reserve(**kwargs)

    def consumed(self, **kwargs: Any) -> Spend:
        return supply_mod.consumed(**kwargs)


class HarnessClient:
    """`LifecycleDeps.harness` — `plan`/`run` are pure over the injected
    `SupplyPort`; nothing extra rides this client."""

    def plan(self, **kwargs: Any) -> Plan:
        return harness_mod.plan(**kwargs)

    def run(self, **kwargs: Any) -> Any:
        return harness_mod.run(**kwargs)


class JudgementClient:
    """`LifecycleDeps.judgement`."""

    def judge(self, **kwargs: Any) -> Any:
        return judgement_mod.judge(**kwargs)


class RemediationClient:
    """`LifecycleDeps.remediation`."""

    def remediate(self, **kwargs: Any) -> Any:
        return remediation_mod.remediate(**kwargs)


class EscalationClient:
    """`LifecycleDeps.escalation` — carries `.store` the way `steps.py`'s
    `_escalate` helper reads `ctx.deps.escalation.store`."""

    def __init__(self, *, store: SqliteEscalationStore) -> None:
        self.store = store

    def raise_(self, **kwargs: Any) -> Any:
        return escalation_mod.raise_(**kwargs)

    def pending(self, **kwargs: Any) -> tuple[Any, ...]:
        return escalation_mod.pending(**kwargs)


class ReuseClient:
    """`LifecycleDeps.reuse`."""

    def carry_over(self, **kwargs: Any) -> Any:
        return reuse_mod.carry_over(**kwargs)


class JobReaderAdapter:
    """`rqa.escalation.decide`'s `JobReader` — P-01's read-only view of
    `jobs.head_sha`/`jobs.snapshot_hash`, over the real `SqliteJobStore`."""

    def __init__(self, jobs: SqliteJobStore) -> None:
        self._jobs = jobs

    def current(self, job_id: str) -> Job | None:
        return self._jobs.get(job_id)


class LifecycleResumeAdapter:
    """`rqa.escalation.decide`'s `LifecycleResume` — the E-11 reverse edge,
    over the real `rqa.lifecycle.resume`."""

    def resume(self, **kwargs: Any) -> Any:
        from rqa.lifecycle import resume as lifecycle_resume

        return lifecycle_resume(**kwargs)


@dataclass(frozen=True)
class AnchorOutcome:
    """What one `rqa anchor` run did. Every field is an observed outcome, never a
    claim: `pending` above zero means the anchor exists locally but never left the
    machine, which still detects a removed tail offline."""

    job_id: str
    anchored_seq: int | None
    published: int
    pending: int
    detail: str | None


@dataclass
class Composition:
    """Every real collaborator the E-17 command surface and the E-21 `tick`
    entry point need, built once per process over one state directory.

    Nothing here is a mock, a stub or a `types.SimpleNamespace`: every field
    is the same concrete class a deployment runs, over the same shared
    `connection` (jobs/pr_facts/leases/record_entries/human_requests/
    capabilities/providers/circuit_breakers/spend/etags/api_calls/mutations),
    with the one documented exception `rqa.policy.store.SqliteSnapshotStore`
    is (`container.md` §5: the `snapshots` row manages its own connection to
    the same `state.db` file, `archive`-then-`pointer`).
    """

    state_dir: Path
    connection: sqlite3.Connection
    clock: Callable[[], datetime]
    jobs: SqliteJobStore
    pr_facts: SqlitePrFactsStore
    leases: SqliteLeaseStore
    record: RecordWriter
    github: GithubAdapter
    runner: SubprocessProcessRunner
    policy: PolicyClient
    authority: AuthorityClient
    supply: SupplyClient
    harness: HarnessClient
    judgement: JudgementClient
    remediation: RemediationClient
    escalation: EscalationClient
    reuse: ReuseClient
    escalation_store: SqliteEscalationStore
    snapshot_store: SqliteSnapshotStore

    def __repr__(self) -> str:
        """Arity, never live collaborator contents."""
        return f"Composition(<{len(fields(self))} injected collaborators; fields elided>)"


    def lifecycle_deps(self) -> LifecycleDeps:
        """A fresh `LifecycleDeps`, exactly as `rqa/intake/tick.py` builds one
        per job: `claim_lease`/`release_lease` are bound through a fresh
        `Lease` over this composition's own `leases`/`github`/`clock`."""
        lease = Lease(leases=self.leases, github=self.github, clock=self.clock)
        return LifecycleDeps(
            policy=self.policy,
            authority=self.authority,
            supply=self.supply,
            harness=self.harness,
            judgement=self.judgement,
            remediation=self.remediation,
            escalation=self.escalation,
            github=self.github,
            reuse=self.reuse,
            record=self.record,
            connection=self.connection,
            state_dir=self.state_dir,
            runner=self.runner,
            claim_lease=lease.claim_lease,
            release_lease=lease.release_lease,
        )

    def job_reader(self) -> JobReaderAdapter:
        return JobReaderAdapter(self.jobs)

    def lifecycle_resume(self) -> LifecycleResumeAdapter:
        return LifecycleResumeAdapter()


def build_composition(
    state_dir: Path,
    *,
    clock: Callable[[], datetime] = utcnow,
    repos: tuple[str, ...] = (),
) -> Composition:
    """Bootstrap every table this state directory needs and wire every real
    collaborator over it. Idempotent: every store's own constructor runs its
    own `CREATE TABLE IF NOT EXISTS`, so calling this again against the same
    directory (the normal case — one process per `rqa` invocation) never
    loses or duplicates schema.
    """
    state_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(state_dir / "state.db"))

    intake_ensure_schema(connection)
    jobs = SqliteJobStore(connection, clock=clock)
    pr_facts = SqlitePrFactsStore(connection)
    leases = SqliteLeaseStore(connection)

    record: RecordWriter = SQLiteRecordWriter(connection, clock=clock)

    github_ensure_schema(connection)
    transport = Transport(
        etags=SqliteEtagStore(connection),
        api_calls=SqliteApiCallStore(connection),
    )
    github = GithubAdapter(
        transport=transport,
        mutations=SqliteMutationStore(connection),
        clock=clock,
    )

    snapshot_store = SqliteSnapshotStore(state_dir)
    policy = PolicyClient(snapshot_store)

    capability_store = SqliteCapabilityStore(connection)
    authority = AuthorityClient(github=github, store=capability_store, repos=repos)

    prober = SubprocessHarnessProber()
    breakers = SqliteBreakerStore(connection=connection)
    spend = SqliteSpendStore(connection=connection)
    supply = SupplyClient(prober=prober, breakers=breakers, spend=spend)

    harness = HarnessClient()
    judgement = JudgementClient()
    remediation = RemediationClient()

    escalation_store = SqliteEscalationStore(connection)
    escalation = EscalationClient(store=escalation_store)

    reuse = ReuseClient()
    runner = SubprocessProcessRunner()

    return Composition(
        state_dir=state_dir,
        connection=connection,
        clock=clock,
        jobs=jobs,
        pr_facts=pr_facts,
        leases=leases,
        record=record,
        github=github,
        runner=runner,
        policy=policy,
        authority=authority,
        supply=supply,
        harness=harness,
        judgement=judgement,
        remediation=remediation,
        escalation=escalation,
        reuse=reuse,
        escalation_store=escalation_store,
        snapshot_store=snapshot_store,
    )
def anchor_job_for(comp: "Composition", job_id: str) -> "AnchorOutcome":
    """Publish this job's chain head where the reviewed agent cannot rewrite it.

    **Order matters, and it is the whole reason this lives here rather than
    inside `rqa/record/`.** `authority.grant` records a `grant` entry (E-04), so
    minting the grant *moves the head*. The grant is therefore minted **first**
    and the head read **after**, so the anchor covers its own grant entry and
    nothing is appended behind it. Mint it the other way round and every anchor
    run leaves the head one entry ahead of the anchor, for ever.

    Returns an outcome rather than raising: an unanchorable job — unknown, not yet
    on GitHub, or a repository with no comment authority — is a reportable state,
    never a reason to fail a review. ADR-0066: anchoring cannot break anything.
    """
    from rqa.contracts import Activity, Deny, Grant
    from rqa.github.anchor_publisher import GithubAnchorPublisher

    job = comp.jobs.get(job_id)
    if job is None:
        return AnchorOutcome(job_id=job_id, anchored_seq=None, published=0, pending=0,
                             detail="no such job")

    answer = comp.authority.grant(
        repo=job.repo,
        activity=Activity.COMMENT,
        snapshot=None,
        job_id=job.id,
        categories=None,
        record=comp.record,
        github=comp.authority.github,
        store=comp.authority.store,
    )
    grant = answer if isinstance(answer, Grant) else None
    detail = None
    if isinstance(answer, Deny):
        # Fail-closed, and say so. The anchor is still recorded locally, which is
        # what detects a crash-truncated log offline; it simply never leaves the
        # machine. An advisory-only repository lands here by design.
        detail = f"not published: {answer.reason.value if hasattr(answer.reason, 'value') else answer.reason}"

    publisher = GithubAnchorPublisher(adapter=comp.github, job=job, grant=grant)
    result = anchor_job(comp.connection, job.id, publisher=publisher, clock=comp.clock)
    return AnchorOutcome(
        job_id=job.id,
        anchored_seq=result.anchored_seq,
        published=result.published,
        pending=result.pending,
        detail=detail or (result.failures[0] if result.failures else None),
    )

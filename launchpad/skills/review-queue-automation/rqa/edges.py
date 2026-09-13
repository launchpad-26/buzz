"""Edge signatures — `architecture/code/CONTRACTS.md` §9, one per E-NN, verbatim.

This module is the §9 half of the seam: every cross-part call signature and every
edge Protocol, copied character-for-character from `code/CONTRACTS.md` §9. The
declarations are the contract, not the behaviour — every body is `...`, and the
behaviour behind an edge belongs to the part lane that owns it.

Ownership note: `rqa/contracts.py` owns §1 and §§3-8, and the guard in
`tests/test_rqa_contracts_guard.py` forbids that module from *declaring* any §9
name ("§9 … belongs to the edge lane") while blessing re-exports by
construction. §9 is therefore declared here, and `rqa/contracts.py` re-exports
every name below so a provider and its consumers import the whole seam from
`rqa.contracts`. The machine-checkable account of all 26 `components.md` §6 edge
rows (`EDGES`) lives in `rqa/contracts.py` beside those re-exports.

Conventions (`CONTRACTS.md` preamble): Python 3.12; every function keyword-only;
dependency injection is by keyword; every provider takes `record: RecordWriter`
if it appends. `Mapping` is `collections.abc`. `from __future__ import
annotations` keeps every annotation a string, exactly as documented, so this
module imports cleanly whether or not `rqa.protocol` exists yet; the
`TYPE_CHECKING` imports below serve type checkers only.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from collections.abc import Mapping
    from pathlib import Path
    from typing import Literal

    from rqa.contracts import (
        Activity,
        Attempt,
        BundleFailure,
        CapabilityReading,
        CarryOver,
        CheckRun,
        Decision,
        Deny,
        Escalation,
        EscalationCause,
        ExplanationUnavailable,
        Facts,
        GithubUnavailable,
        Grant,
        Job,
        JobStatus,
        Judgement,
        LeaseTaken,
        Mutation,
        PanelResult,
        Plan,
        PrFacts,
        ProcessResult,
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
        Spend,
        Stale,
        ValidationFailure,
    )
    from rqa.protocol import Category, Finding, Invalid, Valid


# --------------------------------------------------------------------------
# Collaborator Protocols named in §9 signatures.
#
# §9 names each of these in a signature's annotation, so each needs a name that
# resolves for introspection. `SupplyPort`'s three methods are spelled out in
# §9's E-07 comment; for the stores and bundles, §9 states no method, so each is
# an empty Protocol whose docstring names the part that owns its shape. That
# shape is that part's to fill in its own lane — nothing here narrows it.
# --------------------------------------------------------------------------


class LifecycleDeps(Protocol):
    """LifecycleDeps bundles every neighbour P-02 calls (`CONTRACTS.md` §9, E-02
    comment). Its shape is P-02's (`code/P-02-lifecycle.md`) to state."""


class SnapshotStore(Protocol):
    """The snapshot store `snapshot_for` (E-03) reads and writes. Its shape is
    P-03's (`code/P-03-policy.md`) to state."""


class GithubProbe(Protocol):
    """P-08's view of P-09's E-16 capability probe, injected into `grant`
    (E-04). Its shape is P-08's (`code/P-08-authority.md`) to state."""


class CapabilityStore(Protocol):
    """The per-job capability cache `grant` (E-04) consults. Its shape is
    P-08's (`code/P-08-authority.md`) to state."""


class SpendStore(Protocol):
    """The spend ledger behind `reserve` (E-06) and `consumed` (E-15). Its
    shape is P-05's (`code/P-05-supply.md`) to state."""


class BreakerStore(Protocol):
    """The availability-breaker state behind `route` (E-06) and `consumed`
    (E-15). Its shape is P-05's (`code/P-05-supply.md`) to state."""


class EscalationStore(Protocol):
    """The escalation index behind `raise_` and `pending` (E-11). Its shape is
    P-11's (`code/P-11-escalation.md`) to state."""


class SupplyPort(Protocol):
    """P-06's view of E-06 + E-15, constructed by P-02 over P-05's functions
    (`CONTRACTS.md` §9, E-07 comment). The three methods and their returns are
    exactly the comment's; the parameter types restate the underlying E-06
    (`route`, `reserve`) and E-15 (`consumed`) signatures, nothing more."""

    def route(self, obligation: str, cursor: RouteCursor) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
    def reserve(self, plan: Plan, route: Route) -> Reservation | Refusal: ...
    def consumed(self, attempt: Attempt, reading: int | None, reservation: Reservation) -> Spend: ...


class Explanation(Protocol):
    """Named by `CONTRACTS.md` §9's E-17 prose line (`explain` → `Explanation |
    ExplanationUnavailable`) but defined nowhere in `CONTRACTS.md`. Its shape is
    P-12's (`code/P-12-record.md` §3.3) to state."""


# --------------------------------------------------------------------------
# §9 edge signatures, verbatim.
# Provider implements exactly this; consumer calls exactly this.
# --------------------------------------------------------------------------


# E-01  P-09 provides, P-01 consumes
def inventory(*, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable: ...
def claim_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable: ...
def release_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...


# E-02  P-02 provides, P-01 consumes
def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus: ...
# LifecycleDeps bundles every neighbour P-02 calls.


# E-03  P-03 provides, P-02 consumes
def snapshot_for(*, repo: str, job: Job | None, store: SnapshotStore,
                 record: RecordWriter | None) -> Snapshot | ValidationFailure: ...


# E-04  P-08 provides, P-02 consumes
def grant(*, repo: str, activity: Activity, snapshot: Snapshot | None, job_id: str,
          categories: frozenset[Category] | None, record: RecordWriter, github: GithubProbe,
          store: CapabilityStore) -> Grant | Deny: ...


# E-05  P-13 provides, P-02 consumes
def carry_over(*, job: Job, prior: RecordReader, facts: Facts, snapshot: Snapshot, record: RecordWriter) -> CarryOver: ...


# E-06  P-05 provides, P-06 consumes (P-02 constructs the cursor; P-06 advances it)
def route(*, job: Job, obligation: str, snapshot: Snapshot, facts: Facts, cursor: RouteCursor,
          prober: HarnessProber, breakers: BreakerStore) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
def reserve(*, job: Job, plan: Plan, route: Route, snapshot: Snapshot, spend: SpendStore) -> Reservation | Refusal: ...


# E-07  P-06 provides, P-02 consumes.  P-06 OWNS the panel loop; P-02 makes exactly one run() call per review.
def plan(*, job: Job, facts: Facts, snapshot: Snapshot, carry: CarryOver, record: RecordWriter) -> Plan: ...
def run(*, job: Job, plan: Plan, facts: Facts, snapshot: Snapshot, supply: SupplyPort, state_dir: Path,
        record: RecordWriter) -> PanelResult | BundleFailure: ...
#   SupplyPort is P-06's view of E-06 + E-15, constructed by P-02 over P-05's functions:
#     route(obligation, cursor) -> tuple[Route, RouteCursor] | RouteUnavailable
#     reserve(plan, route) -> Reservation | Refusal
#     consumed(attempt, reading, reservation) -> Spend


# E-08  P-04 provides, P-06 consumes
def validate(*, path: Path, attempt_id: str) -> Valid | Invalid: ...          # Valid.verdict: Verdict


# E-09  P-07 provides, P-02 consumes
def judge(*, job: Job, plan: Plan, panel: PanelResult, carry: CarryOver, facts: Facts, snapshot: Snapshot,
          decision: Decision | None, record: RecordWriter) -> Judgement: ...
#   `panel.evidence_cutoff` is captured and recorded after the final attempt; no later attestation counts.
#   When panel.attempts is empty and carry.regenerated is empty, judge() materialises the Judgement
#   from carry.reused alone — this is the zero-reviewer-call path, and it still records a `judgement` entry.


# E-10  P-10 provides, P-02 consumes
def remediate(*, job: Job, finding: Finding, grant: Grant, facts: Facts, snapshot: Snapshot,
              state_dir: Path, runner: ProcessRunner, record: RecordWriter) -> RemediationPushed | RemediationRefused: ...


# E-11  P-11 provides, P-02 consumes (reverse edge: P-11 calls P-02.resume)
def raise_(*, job: Job, cause: EscalationCause, question: str, context: Mapping, record: RecordWriter,
           store: EscalationStore) -> Escalation: ...
def pending(*, store: EscalationStore) -> tuple[Escalation, ...]: ...
def resume(*, job_id: str, decision: Decision, deps: LifecycleDeps) -> JobStatus: ...     # P-02 provides


# E-12  P-09 provides, P-02 consumes
def submit_review(*, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str, grant: Grant,
                  record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
def comment(*, job: Job, body: str, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...
def merge(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...


# E-13  P-12 provides, every part except P-04 consumes
# RecordWriter.append(job_id, kind, payload) -> Entry
# E-13 is a method on §7's `RecordWriter` Protocol, declared in `rqa/contracts.py`,
# not a free function — nothing to declare here.


# E-14  P-09 provides internally to its E-23 fact capture
def checks(*, repo: str, sha: str) -> tuple[CheckRun, ...] | GithubUnavailable: ...


# E-15  P-05 provides, P-06 consumes through SupplyPort
def consumed(*, job: Job, attempt: Attempt, reading: int | None, reservation: Reservation,
             record: RecordWriter, spend: SpendStore, breakers: BreakerStore) -> Spend: ...


# E-16  P-09 provides, P-08 consumes
def probe(*, repo: str, credential: str) -> CapabilityReading | GithubUnavailable: ...


# E-17  CLI: P-02 status; P-12 explain → Explanation | ExplanationUnavailable; P-11 decide/pending; P-03 onboard; P-01 tick
#
# E-17 is a command surface, not one signature. §9 states it as the prose line
# above — the concrete provider callables and, for `explain`, its return union;
# nothing more. Each callable below therefore declares only that: an open
# keyword-only (**kwargs) surface — the CONTRACTS.md preamble's "every function
# keyword-only" rule binds free functions, with `rqa.protocol.paths.matches` its
# single named exception. The full parameter list is its provider part's
# contract to state (P-02 §3.4 `status`, P-12 §3.3 `explain`, P-11 `decide`,
# P-03 `onboard`, P-01 §3 `tick`) and that part's lane to implement; nothing
# here narrows it. E-17's `pending` IS P-11's E-11 `pending()` (components.md
# §6 row E-17) — declared above, never a second declaration.
def status(**kwargs): ...
def explain(**kwargs) -> Explanation | ExplanationUnavailable: ...
def decide(**kwargs): ...
def onboard(**kwargs): ...
def tick(**kwargs): ...


# E-18  P-09 → GitHub: HTTPS REST v3 / GraphQL v4 with the operator's `gh auth token`; the only HTTP client import in RQA
# E-19  P-06 → review harness: published role-separated interaction and injection-conformance contract; process execution
# E-20  P-10 → GitHub: `git fetch <sha>` and `git push <remote> HEAD:refs/heads/<head_ref>` over smart HTTP; never `--force`
# E-21  OS scheduler → P-01: process launch `rqa tick`; no payload
# E-22  P-08 → GitHub CLI: process execution `gh auth token`; value held in memory for one probe, never persisted
# Prose-only external edges — no Python signature to declare. Their entries in
# `rqa.contracts.EDGES` carry the reason strings.


# E-23  P-09 provides, P-02 consumes
def facts(*, job: Job, record: RecordWriter) -> Facts | GithubUnavailable: ...   # one coherent GitHub fact capture


# E-24  P-05 consumes (HarnessProber, implemented in P-06 over the same invoke() as E-19)
class HarnessProber(Protocol):
    def probe(self, route: Route, *, timeout: float) -> bool: ...


# E-25  P-12 consumes — the OS keychain (ADR-F key)          NEW: surfaced by review
class KeyStore(Protocol):
    def read(self, name: str) -> bytes | None: ...            # None: key absent → verify/explain report unverifiable, append proceeds unkeyed and says so


# E-26  P-10 consumes — local tool processes (MECHANICAL_TOOL_SET binaries)   NEW: surfaced by review
class ProcessRunner(Protocol):
    def run(self, *, cwd: Path, argv: tuple[str, ...], timeout: float) -> ProcessResult: ...

"""`grant()` — the one entry point, E-04, `code/P-08-authority-gate.md` §3.

Answers *may RQA perform this activity on this repository, for this job, right now?*
from the pinned snapshot and a proven capability, never from anything else, and
records the answer. Nothing here reads a file, an environment variable or a
configuration: the snapshot is the only policy source (§7).

**Fail-closed, branch by branch.** §3's eight steps run in order and every one of them
either returns a value or raises. There is no fall-through, no partial grant and no
default-allow tail: a `Deny` is indistinguishable in effect from an absent grant. A
malformed or unreadable policy reaches this function as `snapshot is None`, and step 2
turns that into `Deny(NO_SNAPSHOT)` whatever the activity — which is how "a malformed
or unreadable policy must never widen authority" is implemented (RQA-NFR-018).

**Values against errors.** Policy and capability refusals are `Deny` values; only a
wrong-shape call raises `GateError`. `AppendFailed` from the record is never caught: a
decision RQA cannot write down is not a decision it may act on (§3, T13).

**Two call-time resolutions, both deliberate.**

* `_mechanical_tool_set()` reaches P-10's registry (`rqa.remediation`) at call time.
  That part need not be present for this gate to be correct, and an unimportable one
  is an *empty* registry, so every configured tool id fails `TOOL_NOT_IN_SET` — the
  fail-closed answer rather than an import error. This duplicates the check
  `rqa.policy.validate` already makes on the same ids, on purpose: `P-03-policy.md` §4
  fixes that P-08 checks membership again, independently, when granting `remediate`.
  This module may not import `rqa.policy` (§1), so it resolves the registry itself.
* `_capability()` reaches this package's own `capability` module at call time.
  `capability.py` imports `GateError` from here to declare
  `CredentialGithubUnavailable` as its subclass (§4), so a module-level import in this
  direction would close a cycle whose resolution depended on which of the two modules
  Python happened to load first. Resolving at call time makes the pair
  order-independent.

**`rqa.github` is not imported here.** §1 permits it; the probe arrives instead through
E-04's injected `github: GithubProbe`, which is the only form P-02 ever calls and the
form every test here exercises. The two values the probe may return —
`CapabilityReading` and `GithubUnavailable` — are `CONTRACTS.md` §4 types, imported from
the seam like everything else.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from rqa.authority.activities import REQUIRED_CAPABILITY
from rqa.contracts import (
    MECHANICAL_GROUP,
    Activity,
    Category,
    Deny,
    DenyReason,
    Grant,
    RecordWriter,
    Snapshot,
)

if TYPE_CHECKING:  # annotation-only; never imported at runtime, so no import cycle
    from rqa.authority.capability import CapabilityProof, GithubProbe
    from rqa.authority.store import CapabilityStore

__all__ = ["Gate", "GateError", "grant"]


class GateError(Exception):
    """Programming error: the gate was called wrongly. Policy/capability refusals are
    Deny values."""


def _capability() -> Any:
    """This package's `capability` module, resolved at call time (see the module
    docstring for why the import is not at the top of this file)."""
    from rqa.authority import capability

    return capability


def _mechanical_tool_set() -> Mapping[str, Any]:
    """P-10's closed registry, resolved now rather than at import.

    Absent module, absent attribute, or an attribute that is not a mapping: an empty
    registry, so every configured tool id fails `TOOL_NOT_IN_SET`. Substituting this
    function is how a test exercises membership without depending on whether P-10 is
    present.
    """
    try:
        from rqa import remediation
    except ImportError:
        return {}
    registry = getattr(remediation, "MECHANICAL_TOOL_SET", None)
    return registry if isinstance(registry, Mapping) else {}


def _configured_repositories() -> frozenset[str]:
    """The configured set of managed repositories, resolved at call time.

    P-08 reads no configuration and no environment (§7), and E-04's signature has no
    room for the set, so the free `grant()` takes it from this one substitutable seam.
    `P-01-intake.md` §3 describes the same arrangement from the other side: the managed
    set "is a parameter, not a record this file reads ... the same way
    `code/P-08-authority-gate.md`'s `grant()` takes `repo: str` without describing where
    the caller's configured set comes from".

    Unwired it is empty, and then every repository is `REPO_NOT_MANAGED`: a gate that
    does not know which repositories it governs must answer for none of them. Real
    wiring constructs `Gate(repos=...)` and injects its bound `grant` as P-02's
    `AuthorityClient` (`code/P-02-lifecycle.md` §4).
    """
    return frozenset()


class Gate:
    """The gate implementation behind E-04.

    The configured set of managed repositories is a constructor dependency, never an
    E-04 parameter — §3 fixes that signature verbatim and names constructor
    dependencies as where anything else belongs. `grant` below is exactly P-02's
    `AuthorityClient.grant` (`code/P-02-lifecycle.md` §4).

    This object holds no decision state. Every call re-reads its supplied snapshot and
    its per-job proof, so the same `(repo, activity, snapshot, categories, proof)`
    always gives the same answer and the gate has no memory of previous answers beyond
    the record (§3, §7).
    """

    def __init__(self, *, repos: frozenset[str]):
        self.repos = frozenset(repos)

    # -- E-04 ------------------------------------------------------------------

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
    ) -> Grant | Deny:
        """§3's eight steps, in order. Every branch returns a value or raises."""
        # Wrong-shape calls raise before any branch: a call that names no activity has
        # no decision to record, and a `grant` entry whose `activity` is unreadable is
        # worse than no entry. These are the only raises other than §3 steps 3 and 5.
        if not isinstance(activity, Activity):
            raise GateError(f"activity must be an Activity member, got {activity!r}")
        if not isinstance(repo, str) or not repo:
            raise GateError(f"repo must be a non-empty string, got {repo!r}")
        if not isinstance(job_id, str) or not job_id:
            raise GateError(f"job_id must be a non-empty string, got {job_id!r}")

        # Step 1. Checked first so the gate can never be asked about, let alone answer
        # for, an unmanaged repository — before any probe, which is what keeps the
        # credential away from a repository RQA does not manage (T10).
        if repo not in self.repos:
            return self._deny(
                repo=repo,
                activity=activity,
                snapshot=snapshot,
                job_id=job_id,
                categories=categories,
                record=record,
                reason=DenyReason.REPO_NOT_MANAGED,
                detail=f"{repo} is not in the configured set of managed repositories",
            )

        # Step 2. No snapshot, no grant, whatever the activity (RQA-NFR-018).
        if snapshot is None:
            return self._deny(
                repo=repo,
                activity=activity,
                snapshot=None,
                job_id=job_id,
                categories=categories,
                record=record,
                reason=DenyReason.NO_SNAPSHOT,
                detail=(
                    f"no pinned policy snapshot for {repo}: an unreadable or malformed "
                    "policy never widens authority"
                ),
            )

        # Step 3. A snapshot for another repository is a programming error, not a
        # policy answer: answering it either way would be answering from the wrong
        # repository's policy.
        if snapshot.repo != repo:
            raise GateError(
                f"snapshot is pinned to {snapshot.repo!r} but the gate was asked about {repo!r}"
            )

        if activity is Activity.REMEDIATE:
            # Step 4.
            refusal = self._remediation_refusal(snapshot=snapshot, categories=categories)
            if refusal is not None:
                reason, detail = refusal
                return self._deny(
                    repo=repo,
                    activity=activity,
                    snapshot=snapshot,
                    job_id=job_id,
                    categories=categories,
                    record=record,
                    reason=reason,
                    detail=detail,
                )
        elif categories is not None:
            # Step 5. Only remediation is category-scoped; categories anywhere else
            # means the caller has confused two activities.
            raise GateError(
                f"categories are only meaningful for {Activity.REMEDIATE.value}; "
                f"{activity.value} was called with {categories!r}"
            )

        # Step 6. Disabled is the default: `.get` rather than `[...]` so a snapshot
        # missing a key denies instead of raising (RQA-NFR-017, RQA-NFR-026).
        if not snapshot.authority.get(activity, False):
            return self._deny(
                repo=repo,
                activity=activity,
                snapshot=snapshot,
                job_id=job_id,
                categories=categories,
                record=record,
                reason=DenyReason.NOT_ENABLED,
                detail=(
                    f"{activity.value} is not enabled for {repo} by snapshot {snapshot.hash}"
                ),
            )

        # Step 7. The per-job capability proof: read it if this job already has one,
        # probe once and record the attestation if it does not.
        proof = self._proof(repo=repo, job_id=job_id, record=record, github=github, store=store)
        missing = REQUIRED_CAPABILITY[activity] - proof.capabilities
        if missing:
            return self._deny(
                repo=repo,
                activity=activity,
                snapshot=snapshot,
                job_id=job_id,
                categories=categories,
                record=record,
                reason=DenyReason.CAPABILITY_MISSING,
                detail=(
                    f"the credential cannot {activity.value} on {repo}: missing "
                    f"{sorted(missing)}"
                ),
                proof=proof,
            )

        # Step 8.
        entry = self._append(
            record=record,
            job_id=job_id,
            activity=activity,
            snapshot=snapshot,
            categories=categories,
            proof=proof,
            decision="granted",
            reason=None,
            detail="",
        )
        return Grant(
            activity=activity,
            repo=repo,
            job_id=job_id,
            snapshot_hash=snapshot.hash,
            capability_proof_id=proof.id,
            categories=categories,
            entry_seq=entry.seq,
        )

    # -- step 4 ----------------------------------------------------------------

    def _remediation_refusal(
        self, *, snapshot: Snapshot, categories: frozenset[Category] | None
    ) -> tuple[DenyReason, str] | None:
        """§3 step 4's three refusals, in order, or `None` when remediation may proceed.

        Every member of `categories` is verified: P-08 never sees a `Finding`, so the
        complete category set it is handed is the whole of what it can check (§7).
        """
        if categories is None or not categories:
            return (
                DenyReason.CATEGORY_REQUIRED,
                "remediate requires the complete category set of the finding it would fix",
            )
        configured = snapshot.policy.mechanical.categories
        outside = sorted(
            category.value
            for category in categories
            if category not in MECHANICAL_GROUP or category not in configured
        )
        if outside:
            return (
                DenyReason.CATEGORY_NOT_MECHANICAL,
                (
                    f"{outside} is not mechanical or is not configured mechanical for "
                    f"{snapshot.repo} by snapshot {snapshot.hash}"
                ),
            )
        registry = _mechanical_tool_set()
        unknown = sorted(tool for tool in snapshot.policy.mechanical.tools if tool not in registry)
        if unknown:
            return (
                DenyReason.TOOL_NOT_IN_SET,
                f"{unknown} is not a member of MECHANICAL_TOOL_SET",
            )
        return None

    # -- step 7 ----------------------------------------------------------------

    def _proof(
        self,
        *,
        repo: str,
        job_id: str,
        record: RecordWriter,
        github: GithubProbe,
        store: CapabilityStore,
    ) -> CapabilityProof:
        """This job's capability proof for this repository, probed at most once.

        The cache read lives here rather than in `probe_capability` because §6 writes
        one `attestation` per *probe*, and only the caller that decided to probe knows
        that a probe happened. A second grant in the same job reads the stored proof
        and writes no second attestation (T11); a second job probes again (T12).
        """
        stored = store.current(repo, job_id)
        if stored is not None:
            return stored
        proof = _capability().probe_capability(repo, github, store, job_id)
        # ADR-0062 §3: what the credential is reported to have but the probe could not
        # exercise is recorded, not hidden. The credential itself is not in this
        # payload and is nowhere in this package's writes (RQA-NFR-025, T16).
        record.append(
            job_id,
            "attestation",
            {
                "login": proof.login,
                "capabilities": sorted(proof.capabilities),
                "attested_not_proven": sorted(proof.attested_not_proven),
                "probed_at": proof.probed_at.isoformat(),
            },
        )
        return proof

    # -- recording -------------------------------------------------------------

    def _deny(
        self,
        *,
        repo: str,
        activity: Activity,
        snapshot: Snapshot | None,
        job_id: str,
        categories: frozenset[Category] | None,
        record: RecordWriter,
        reason: DenyReason,
        detail: str,
        proof: CapabilityProof | None = None,
    ) -> Deny:
        """One recorded refusal. `detail` is written to carry the whole of what an
        authority-requirement escalation needs (§3)."""
        entry = self._append(
            record=record,
            job_id=job_id,
            activity=activity,
            snapshot=snapshot,
            categories=categories,
            proof=proof,
            decision="denied",
            reason=reason,
            detail=detail,
        )
        return Deny(
            activity=activity,
            repo=repo,
            job_id=job_id,
            reason=reason,
            detail=detail,
            entry_seq=entry.seq,
        )

    def _append(
        self,
        *,
        record: RecordWriter,
        job_id: str,
        activity: Activity,
        snapshot: Snapshot | None,
        categories: frozenset[Category] | None,
        proof: CapabilityProof | None,
        decision: str,
        reason: DenyReason | None,
        detail: str,
    ):
        """§6's `grant` row, one per returned result. `AppendFailed` propagates."""
        return record.append(
            job_id,
            "grant",
            {
                "activity": activity.value,
                "snapshot_hash": snapshot.hash if snapshot is not None else None,
                "categories": (
                    None if categories is None else sorted(category.value for category in categories)
                ),
                "capability_proof_id": None if proof is None else proof.id,
                "decision": decision,
                "reason": None if reason is None else reason.value,
                "detail": detail,
            },
        )


def grant(*, repo: str, activity: Activity, snapshot: Snapshot | None, job_id: str,
          categories: frozenset[Category] | None, record: RecordWriter, github: GithubProbe,
          store: CapabilityStore) -> Grant | Deny:
    """E-04, verbatim from `CONTRACTS.md` §9.

    The managed set comes from `_configured_repositories()`; unwired it is empty and
    every call is `Deny(REPO_NOT_MANAGED)`. A caller holding the set builds a `Gate`
    and injects its bound `grant` instead — the two are the same code path.
    """
    return Gate(repos=_configured_repositories()).grant(
        repo=repo,
        activity=activity,
        snapshot=snapshot,
        job_id=job_id,
        categories=categories,
        record=record,
        github=github,
        store=store,
    )

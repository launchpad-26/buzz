"""`snapshot_for()` — E-03, the one entry point into pinned policy.

`code/P-03-policy.md` §3 (E-03) and `CONTRACTS.md` §9. Discovery, live read,
validation, canonicalisation, hashing, and orchestration of `store.activate()`.

**Pinned once per job, re-read never.** A job that already carries a
`snapshot_hash` is answered from the store alone: no live read happens on that
branch at all, so an edited `.rqa/config.json` cannot reach it however many times
this function is called (§8 T11). A job without a pin — and an admission-time call
with `job=None`, which P-01 makes before any job exists — reads the file fresh,
every call, from a path recomputed from `repo` and never cached (U-POLICY-01,
U-QUEUE-06; §8 T9, T10).

**The hash covers the entire config, not just `policy`** (U-QUEUE-10): one digest
answers both "did the policy change" and "reproduce exactly what this job ran
under". Two repositories whose configs are byte-identical after canonicalisation
therefore share one archived snapshot, and neither can see the other's `repo`
(§8 T8, T14).

**The caller, not `rqa.policy`, writes `job.snapshot_hash`.** P-03 owns no column of
`jobs`. Its only outbound call, ever, is `record.append`.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from dataclasses import replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from rqa.contracts import (
    Job,
    RecordWriter,
    Snapshot,
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.policy.types import PolicyError, SnapshotStoreCorrupted, ValidatedConfig, utcnow
from rqa.policy.validate import validate
from rqa.protocol import protocol_hash

if TYPE_CHECKING:  # annotation-only: store.py imports this module at runtime
    from rqa.policy.store import SnapshotStore

__all__ = [
    "snapshot_for",
    "config_path",
    "canonical_bytes",
    "digest_of",
    "snapshot_from_verified_archive",
    "snapshot_from_unverified_config",
]

#: The repo-local configuration, relative to the repository root (`container.md` §5).
CONFIG_DIR = ".rqa"
CONFIG_FILENAME = "config.json"


def config_path(repo: str) -> Path:
    """`<repo's root>/.rqa/config.json`, recomputed from `repo` on every call.

    Never cached and never memoised: recomputing the path per call is half of why a
    configuration edit takes effect on the next review with no build, reinstall or
    redeploy (RQA-FR-004, RQA-NFR-005; U-POLICY-01, U-RESILIENCE-09).
    """
    return Path(repo) / CONFIG_DIR / CONFIG_FILENAME


def canonical_bytes(raw: Mapping[str, Any]) -> bytes:
    """The canonical encoding of an entire config — all five sections together.

    `json.dumps(raw, sort_keys=True, separators=(",", ":"))`, UTF-8 encoded. These
    are the exact bytes the store archives, which is what lets `SnapshotStore.get`
    recompute a snapshot's digest over the file it read and detect damage.
    """
    return json.dumps(raw, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest_of(raw: Mapping[str, Any]) -> str:
    """SHA-256 hex digest over `canonical_bytes(raw)` — the snapshot's identity."""
    return hashlib.sha256(canonical_bytes(raw)).hexdigest()


def snapshot_from_verified_archive(
    *, raw: Mapping[str, Any], digest: str, repo: str, protocol: str
) -> Snapshot:
    """Rebuild the shared `Snapshot` that hash-verified archived bytes were pinned as.

    **Only for a read whose caller has just recomputed SHA-256 over the archived
    file's own bytes and matched it against `digest`.** That re-hash is the entitlement
    to everything this function relaxes; a write path has no such proof and must call
    `snapshot_from_unverified_config` instead. `protocol` is the protocol hash recorded
    at activation, not today's — a pinned job must see the protocol definition it ran
    under.

    **What is not re-checked: membership in `MECHANICAL_TOOL_SET`.** That registry is
    P-10's and can change between the process that pinned a snapshot and a later
    process that reads it (`rqa tick` is a fresh launch per E-21), and a pinned read
    that re-resolved it would start failing for a job whose pin had already succeeded
    — which §5 ("a job pinned to an older hash keeps reading it ... for the life of
    the state directory") and §7 ("a snapshot already pinned to an in-flight job stays
    readable forever") forbid. §7's no-fallback rule governs an invalid **live** read,
    and §3 branch 1 performs no live read at all. Every structural and shape rule is
    still applied; each is pure over these bytes and the packaged protocol vocabulary.
    Do not restore full live validation here.

    Bytes that hash correctly but are not structurally a config are a data-integrity
    fault, so this raises `SnapshotStoreCorrupted` — the one failure §5 names for a
    stored read — never a `ValidationFailure` and never a fresh live read.
    """
    validated = validate(raw, repo, trusted_archive=True)
    if isinstance(validated, ValidationFailure):
        raise SnapshotStoreCorrupted(
            f"archived snapshot {digest} is not a structurally valid config: {validated.errors}"
        )
    return _snapshot(validated=validated, digest=digest, repo=repo, protocol=protocol)


def snapshot_from_unverified_config(
    *, raw: Mapping[str, Any], digest: str, repo: str, protocol: str
) -> Snapshot:
    """Build the shared `Snapshot` for a config nothing has vouched for yet.

    **The write path's entry point.** `raw` is caller-supplied and has no
    hash-verified read-back behind it, so the full validator runs, registry membership
    included: §4 checks `MECHANICAL_TOOL_SET` on three sides of a remediation decision
    precisely because no single check may be trusted alone to have made it correctly,
    and a store that archived a tool id on its caller's word would be a fourth site
    relying on someone else having looked. Redundant with §3 step 3 on the documented
    E-03 path, and deliberately so.

    A config that does not validate is a caller/invariant error — `SnapshotStore` is
    handed policy that was supposed to have validated — so this raises `PolicyError`,
    never a `ValidationFailure`: an operator's malformed config is refused at §3 step
    3, long before anything reaches a store.
    """
    validated = validate(raw, repo)
    if isinstance(validated, ValidationFailure):
        raise PolicyError(
            f"refusing to build snapshot {digest}: config does not validate: {validated.errors}"
        )
    return _snapshot(validated=validated, digest=digest, repo=repo, protocol=protocol)


def snapshot_for(
    *, repo: str, job: Job | None, store: SnapshotStore, record: RecordWriter | None
) -> Snapshot | ValidationFailure:
    """The pinned, content-hashed `Snapshot` a job runs against for its lifetime.

    `job=None` is P-01's admission-time gate: a live read and full validation with
    nothing recorded, which admits nothing without a valid repo-local policy.
    """
    # 1. This job already has a pin: answer from the store, with no live read.
    if job is not None and job.snapshot_hash is not None:
        stored = store.get(job.snapshot_hash)
        if stored is None:
            # A pinned job citing a hash the store cannot produce is a
            # data-integrity fault, never a value: it cannot arise from anything a
            # repository's config does, and re-reading config cannot repair it.
            raise SnapshotStoreCorrupted(
                f"job {job.id} is pinned to snapshot {job.snapshot_hash}, which the store "
                "cannot produce"
            )
        return replace(stored.snapshot, repo=repo)

    # 2. A live read, unconditionally, every call.
    path = config_path(repo)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return _unreadable(repo, f"{path} could not be read: {exc}")
    except UnicodeDecodeError as exc:
        return _unreadable(repo, f"{path} is not valid UTF-8: {exc}")
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        return _unreadable(repo, f"{path} is not valid JSON: {exc}")

    # 3. Fail-closed validation. An invalid config is refused outright; it is never
    #    served the last-known-good snapshot instead (§7).
    validated = validate(raw, repo)
    if isinstance(validated, ValidationFailure):
        return validated

    # 4. Canonicalise and hash the entire config.
    digest = digest_of(raw)

    # 5. Activate: idempotent, archive-before-pointer, nothing already active touched.
    stored = store.activate(digest, raw, at=utcnow())

    # 6. Build the shared Snapshot.
    snapshot = _snapshot(
        validated=validated, digest=digest, repo=repo, protocol=protocol_hash()
    )

    # 7. Admission-time call: nothing job-scoped exists yet to record against.
    if job is None:
        return snapshot

    # 8. A job pin without its required durable record is a caller error.
    if record is None:
        raise PolicyError("job pin requires RecordWriter")

    # 9. This job's first pin. `AppendFailed` propagates (E-13): `snapshot_for` never
    #    returns a Snapshot that was not recorded against the job it was pinned for.
    record.append(
        job.id,
        kind="snapshot",
        payload={
            "hash": digest,
            "repo": repo,
            "policy_version": validated.policy.version,
            "protocol_hash": snapshot.protocol_hash,
            "activated_at": stored.activated_at.isoformat(),
        },
    )
    return snapshot


def _snapshot(
    *, validated: ValidatedConfig, digest: str, repo: str, protocol: str
) -> Snapshot:
    """`CONTRACTS.md` §3's `Snapshot`, from validated shared values only. No local
    snapshot-tree type and no route conversion is involved (§2)."""
    return Snapshot(
        hash=digest,
        repo=repo,
        protocol_hash=protocol,
        authority=validated.authority,
        routes=validated.routes,
        external=validated.external,
        policy=validated.policy,
        budget=validated.budget,
    )


def _unreadable(repo: str, detail: str) -> ValidationFailure:
    """No store write, no append: a config that cannot be read is a repository
    refusal, and refusing costs nothing durable (§3 step 2)."""
    return ValidationFailure(
        repo,
        (ValidationError(code=ValidationErrorCode.UNREADABLE, path="", detail=detail),),
    )

"""Canonical serialization, the entry hash, and the two `prev_hash` sentinels —
`code/P-12-record.md` §1, §2 and §5 [ADR-F assumed].

Everything a stored row's identity depends on is computed here, so there is exactly
one place where "the same entry" can be decided. §5 fixes both halves:

    canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"),
                                ensure_ascii=True)
    hash           = sha256(f"{job}|{seq}|{kind}|{at}|{canonical_json(payload)}|"
                            f"{prev_hash_for_hash}"), UTF-8, hex

**Why the payload is walked before it is dumped.** `json.dumps` renders several
values this part must refuse: a `str`-valued `Enum` dumps as its text, a `set` fails
with a message about the encoder rather than about the caller, and a `float('nan')`
is not JSON at all. §2 states the admissible set positively — `str`, `int`, `float`,
`bool`, `None`, `list`, `dict`, or a `tuple` of these, "in particular, no Enum, no
dataclass, no other part's type" — so the walk checks exact types and converts
`Mapping`/`tuple` to `dict`/`list` before dumping. That is what makes
`PayloadNotSerializable` a statement about the caller's payload rather than about
whichever encoder branch happened to fail first, and it is what keeps a hash
reproducible from the stored text alone.
"""

from __future__ import annotations

import hashlib
import hmac as _hmac
import json
import re
from collections.abc import Mapping
from typing import Any

from rqa.record.kinds import RecordProgrammingError

__all__ = [
    "GENESIS_PREV_HASH",
    "LEGACY_PREV_HASH",
    "NO_PARENT",
    "PayloadNotSerializable",
    "canonical_json",
    "compute_hash",
    "compute_hmac",
    "hmac_matches",
    "is_hex_digest",
    "prev_hash_for_hash",
]

#: §5: `prev_hash` is NULL on the first row of a chain.
GENESIS_PREV_HASH: str | None = None

#: §5 and §6: every migrated row carries this instead of a parent hash, which is
#: what keeps it out of `verify`'s walk and out of `explain`'s `verified=True`.
LEGACY_PREV_HASH = "legacy"

#: §5: the hashed stand-in for a NULL `prev_hash`. The hash formula never sees NULL.
NO_PARENT = ""

#: A payload nested deeper than this is refused rather than followed. A cycle would
#: otherwise be a `RecursionError` out of a function documented to raise one error.
_MAX_DEPTH = 64

#: What a stored SHA-256 hex digest looks like, for the "malformed" branch of §3.2.
_HEX_DIGEST = re.compile(r"[0-9a-f]{64}")


class PayloadNotSerializable(RecordProgrammingError):
    """`payload` contains a value canonical_json() cannot render (anything other than str,
    int, float, bool, None, list, dict, or tuple of these — in particular, no Enum, no
    dataclass, no other part's type). The caller must convert its own values to plain
    JSON-safe data first."""


def _plain(value: Any, *, path: str, depth: int) -> Any:
    """`value` as plain JSON data, or `PayloadNotSerializable` naming where it failed.

    Exact type tests, not `isinstance`: `JobStatus.QUEUED` is a `str`, a namedtuple is
    a `tuple`, and `True` is an `int`. Admitting them would store another part's type
    under a shape this part promised to define itself (§1).
    """
    if depth > _MAX_DEPTH:
        raise PayloadNotSerializable(
            f"payload at {path} nests deeper than {_MAX_DEPTH} levels or refers to itself"
        )
    kind = type(value)
    if value is None or kind is bool or kind is int or kind is float or kind is str:
        return value
    if isinstance(value, Mapping):
        plain: dict[str, Any] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise PayloadNotSerializable(
                    f"payload at {path} has a non-string key {key!r} of type "
                    f"{type(key).__name__}"
                )
            plain[key] = _plain(item, path=f"{path}.{key}", depth=depth + 1)
        return plain
    if kind is list or kind is tuple:
        return [
            _plain(item, path=f"{path}[{index}]", depth=depth + 1)
            for index, item in enumerate(value)
        ]
    raise PayloadNotSerializable(
        f"payload at {path} is a {type(value).__name__}, which is not JSON-safe data; "
        "convert it to str, int, float, bool, None, list, dict or tuple first"
    )


def canonical_json(*, payload: Mapping) -> str:
    """`payload` as the one canonical JSON text §5 names, or `PayloadNotSerializable`.

    Deterministic by construction: keys sorted, no insertion-order dependence, no
    incidental whitespace, ASCII-escaped. Two mappings with equal keys and values
    therefore produce byte-identical text and byte-identical hashes (§8 T17).
    """
    if not isinstance(payload, Mapping):
        raise PayloadNotSerializable(
            f"payload is a {type(payload).__name__}; append takes a Mapping of JSON-safe data"
        )
    plain = _plain(payload, path="payload", depth=0)
    try:
        return json.dumps(plain, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    except (TypeError, ValueError) as exc:  # pragma: no cover - the walk precedes it
        raise PayloadNotSerializable(f"payload cannot be rendered as canonical JSON: {exc}") from exc


def prev_hash_for_hash(*, prev_hash: str | None) -> str:
    """§5: `""` for a NULL parent, otherwise the stored value verbatim.

    A migrated row therefore hashes over the literal `"legacy"`, which is exactly
    why its hash cannot be confused with a chained row's.
    """
    return NO_PARENT if prev_hash is None else prev_hash


def compute_hash(
    *,
    job: str,
    seq: int,
    kind: str,
    at: str,
    payload: Mapping,
    prev_hash: str | None,
) -> str:
    """The §5 entry hash, as UTF-8 hex.

    `prev_hash` is the value as it is stored — `None`, `"legacy"`, or the parent's
    hash — and is mapped through `prev_hash_for_hash` here so that no caller has to
    remember the NULL rule.
    """
    material = (
        f"{job}|{seq}|{kind}|{at}|{canonical_json(payload=payload)}|"
        f"{prev_hash_for_hash(prev_hash=prev_hash)}"
    )
    return hashlib.sha256(material.encode("utf-8")).hexdigest()


def compute_hmac(*, key: bytes, job: str, seq: int, hash: str) -> str:
    """§3.1 step 5: `HMAC-SHA256(key, f"{job_id}|{seq}|{hash}")`, hex.

    The key is used and dropped: it is never stored, never returned, never logged and
    never part of an error message anywhere in this package (ADR-F — the key is the
    operator's and never RQA's to write into the record).
    """
    material = f"{job}|{seq}|{hash}".encode("utf-8")
    return _hmac.new(key, material, hashlib.sha256).hexdigest()


def is_hex_digest(*, value: object) -> bool:
    """True for the 64-character lowercase hex text a SHA-256 digest is written as.

    §3.2 step 3 distinguishes a keyed row whose `hmac` is "missing or malformed" —
    an immediate `HMAC_MISMATCH` — from one that merely fails to authenticate, so
    "malformed" needs a definition that does not depend on the key being available.
    """
    return type(value) is str and _HEX_DIGEST.fullmatch(value) is not None


def hmac_matches(*, stored: str, recomputed: str) -> bool:
    """Constant-time comparison of two hex HMACs (§3.2 step 3)."""
    return _hmac.compare_digest(stored, recomputed)

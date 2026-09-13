#!/usr/bin/env python3
"""Canonical serialization and the entry hash — `code/P-12-record.md` §5 and §8 row T17.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.
"""

from __future__ import annotations

import hashlib
import hmac as hmac_module
import json
import pathlib
import sys
from datetime import datetime, timezone
from enum import Enum
from types import MappingProxyType

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.record import PayloadNotSerializable  # noqa: E402
from rqa.record.hashing import (  # noqa: E402
    GENESIS_PREV_HASH,
    LEGACY_PREV_HASH,
    NO_PARENT,
    canonical_json,
    compute_hash,
    compute_hmac,
    hmac_matches,
    is_hex_digest,
    prev_hash_for_hash,
)


def refuses(payload) -> bool:
    try:
        canonical_json(payload=payload)
    except PayloadNotSerializable:
        return True
    return False


# -- §5's canonical form -------------------------------------------------------


def test_canonical_json_is_the_exact_form_section_five_states() -> None:
    assert canonical_json(payload={"b": 1, "a": [1, 2]}) == '{"a":[1,2],"b":1}'
    assert canonical_json(payload={"é": "ü"}) == '{"\\u00e9":"\\u00fc"}', "ensure_ascii"
    assert canonical_json(payload={}) == "{}"


def test_t17_insertion_order_does_not_change_the_hash() -> None:
    """T17: two payload dicts with identical key/value pairs built in different insertion
    order → `compute_hash` returns byte-identical results for both."""
    first = {}
    first["zeta"] = [1, {"b": 2, "a": 1}]
    first["alpha"] = {"nested": {"y": False, "x": True}}
    second = {}
    second["alpha"] = {"nested": {"x": True, "y": False}}
    second["zeta"] = [1, {"a": 1, "b": 2}]

    assert canonical_json(payload=first) == canonical_json(payload=second)
    fields = dict(job="job-1", seq=4, kind="plan", at="2026-09-12T08:30:15.123456+00:00")
    assert compute_hash(payload=first, prev_hash="a" * 64, **fields) == compute_hash(
        payload=second, prev_hash="a" * 64, **fields
    )


def test_a_tuple_is_rendered_as_the_list_it_is_equal_to() -> None:
    """§2 admits "a `tuple` of these"; JSON has one sequence, so a tuple and the list
    with the same members are the same stored value."""
    assert canonical_json(payload={"a": (1, 2)}) == canonical_json(payload={"a": [1, 2]})


def test_every_admissible_scalar_is_accepted() -> None:
    payload = {"s": "text", "i": -3, "f": 1.5, "t": True, "n": None, "l": [], "d": {}}
    assert json.loads(canonical_json(payload=payload)) == payload


def test_a_mapping_that_is_not_a_dict_is_still_plain_json_data() -> None:
    assert canonical_json(payload=MappingProxyType({"a": 1})) == '{"a":1}'


# -- what §2 refuses -----------------------------------------------------------


def test_a_datetime_a_set_and_bytes_are_refused() -> None:
    assert refuses({"at": datetime.now(timezone.utc)})
    assert refuses({"tags": {"a", "b"}})
    assert refuses({"blob": b"bytes"})


def test_an_enum_is_refused_even_when_it_is_a_string() -> None:
    """§2: "in particular, no Enum". A `str`-valued enum would otherwise dump as its
    value and silently store another part's type."""

    class OtherPartsState(str, Enum):
        QUEUED = "queued"

    assert refuses({"status": OtherPartsState.QUEUED})


def test_a_dataclass_is_refused() -> None:
    from rqa.contracts import Entry

    assert refuses({"entry": Entry(seq=1, hash="a" * 64)})


def test_a_non_string_key_is_refused() -> None:
    assert refuses({1: "one"})


def test_a_payload_that_is_not_a_mapping_is_refused() -> None:
    assert refuses([{"a": 1}])
    assert refuses("a string")
    assert refuses(None)


def test_a_self_referential_payload_is_refused_rather_than_a_recursion_error() -> None:
    payload: dict = {"a": 1}
    payload["self"] = payload
    assert refuses(payload)


def test_the_error_names_where_in_the_payload_it_failed() -> None:
    """A caller's defect is only actionable if it says which field."""
    try:
        canonical_json(payload={"outer": {"inner": [1, {"bad": object()}]}})
    except PayloadNotSerializable as exc:
        assert "payload.outer.inner[1].bad" in str(exc)


# -- the hash formula ----------------------------------------------------------


def test_compute_hash_is_the_sha256_of_the_documented_material() -> None:
    payload = {"to_state": "queued"}
    expected = hashlib.sha256(
        (
            "job-1|1|transition|2026-09-12T08:30:15.123456+00:00|"
            '{"to_state":"queued"}|'
        ).encode("utf-8")
    ).hexdigest()
    assert (
        compute_hash(
            job="job-1",
            seq=1,
            kind="transition",
            at="2026-09-12T08:30:15.123456+00:00",
            payload=payload,
            prev_hash=GENESIS_PREV_HASH,
        )
        == expected
    )


def test_the_null_parent_hashes_as_the_empty_string_and_legacy_hashes_as_itself() -> None:
    """§5: "`prev_hash_for_hash` is `""` for `NULL`, otherwise the stored value"."""
    assert prev_hash_for_hash(prev_hash=None) == NO_PARENT == ""
    assert prev_hash_for_hash(prev_hash=LEGACY_PREV_HASH) == "legacy"
    assert prev_hash_for_hash(prev_hash="a" * 64) == "a" * 64
    assert GENESIS_PREV_HASH is None


def test_every_hashed_field_changes_the_hash() -> None:
    """If a field did not reach the digest, altering it would be undetectable."""
    base = dict(
        job="job-1",
        seq=1,
        kind="transition",
        at="2026-09-12T08:30:15.123456+00:00",
        payload={"to_state": "queued"},
        prev_hash=None,
    )
    reference = compute_hash(**base)
    for field, altered in (
        ("job", "job-2"),
        ("seq", 2),
        ("kind", "plan"),
        ("at", "2026-09-12T08:30:15.123457+00:00"),
        ("payload", {"to_state": "approved"}),
        ("prev_hash", "b" * 64),
    ):
        assert compute_hash(**{**base, field: altered}) != reference, field


# -- the keyed layer -----------------------------------------------------------


def test_compute_hmac_is_hmac_sha256_over_job_seq_and_hash() -> None:
    key = b"a-test-key-that-never-leaves-this-process"
    entry_hash = "a" * 64
    assert compute_hmac(key=key, job="job-1", seq=3, hash=entry_hash) == hmac_module.new(
        key, f"job-1|3|{entry_hash}".encode("utf-8"), hashlib.sha256
    ).hexdigest()


def test_a_different_key_produces_a_different_hmac() -> None:
    arguments = dict(job="job-1", seq=3, hash="a" * 64)
    assert compute_hmac(key=b"one", **arguments) != compute_hmac(key=b"two", **arguments)


def test_is_hex_digest_accepts_only_a_sha256_hex_string() -> None:
    assert is_hex_digest(value="a" * 64)
    assert not is_hex_digest(value="A" * 64)
    assert not is_hex_digest(value="a" * 63)
    assert not is_hex_digest(value="a" * 65)
    assert not is_hex_digest(value=None)
    assert not is_hex_digest(value=b"a" * 64)
    assert not is_hex_digest(value="not-a-digest")


def test_hmac_comparison_is_the_constant_time_one() -> None:
    assert hmac_matches(stored="a" * 64, recomputed="a" * 64)
    assert not hmac_matches(stored="a" * 64, recomputed="b" * 64)
    source = pathlib.Path(
        pathlib.Path(__file__).resolve().parent.parent / "rqa" / "record" / "hashing.py"
    ).read_text(encoding="utf-8")
    assert "compare_digest" in source

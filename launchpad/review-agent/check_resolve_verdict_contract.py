"""#287 STEP 7 control: `resolve_verdict`'s signature and `Resolution`'s shape.

Smoke-level, not behavioural, per STEP 7's own `done when`: this does not
assert what any particular PR resolves to -- STEP 5's `check_verdict_
resolution.py` and STEP 6's `test_verdict_resolution.py` already do that.
This asserts the ONE importable entry point and its return type's shape do
not silently drift out from under a future consumer that has not been
written yet (#119's banner path or #426's pre-review packet -- see
`resolve_verdict`'s own docstring). No network needed.
"""

from __future__ import annotations

import dataclasses
import inspect
import sys

import verdict_resolution as vr

FAILURES: list[str] = []


def check(label: str, condition: bool, detail: str = "") -> None:
    if condition:
        print(f"PASS  {label}")
    else:
        FAILURES.append(label)
        print(f"FAIL  {label}  {detail}")


def test_entry_point_exists_and_is_callable() -> None:
    check("verdict_resolution exports resolve_verdict", hasattr(vr, "resolve_verdict"))
    check("resolve_verdict is callable", callable(getattr(vr, "resolve_verdict", None)))


def test_entry_point_docstring_names_both_candidate_callers() -> None:
    doc = vr.resolve_verdict.__doc__ or ""
    check("docstring names #119's banner path", "#119" in doc)
    check("docstring names #426's pre-review packet", "#426" in doc)
    check(
        "docstring states neither currently calls it",
        "neither calls this today" in doc or "no consumer yet" in doc,
        doc,
    )


def test_entry_point_signature_stable() -> None:
    sig = inspect.signature(vr.resolve_verdict)
    names = list(sig.parameters.keys())
    check("resolve_verdict(pr, repo=...) -- exactly these two parameters", names == ["pr", "repo"], f"got {names}")
    if "repo" in sig.parameters:
        check(
            "repo has a default value",
            sig.parameters["repo"].default is not inspect.Parameter.empty,
        )


def test_resolution_shape_stable() -> None:
    fields = {f.name for f in dataclasses.fields(vr.Resolution)}
    expected = {"outcome", "reason", "accepted", "superseded", "refused_locations"}
    check("Resolution carries exactly the documented fields", fields == expected, f"got {fields}")


def test_resolved_block_shape_stable() -> None:
    fields = {f.name for f in dataclasses.fields(vr.ResolvedBlock)}
    expected = {"location", "rows"}
    check("ResolvedBlock carries exactly the documented fields", fields == expected, f"got {fields}")


def test_block_location_shape_stable() -> None:
    fields = {f.name for f in dataclasses.fields(vr.BlockLocation)}
    expected = {"comment_id", "surface", "position", "created_at"}
    check("BlockLocation carries exactly the documented fields", fields == expected, f"got {fields}")


def test_outcomes_constant_stable() -> None:
    check(
        "OUTCOMES lists exactly the four documented outcomes",
        set(vr.OUTCOMES) == {"unreadable", "refused", "none_found", "accepted"},
        f"got {vr.OUTCOMES}",
    )


def main() -> int:
    test_entry_point_exists_and_is_callable()
    test_entry_point_docstring_names_both_candidate_callers()
    test_entry_point_signature_stable()
    test_resolution_shape_stable()
    test_resolved_block_shape_stable()
    test_block_location_shape_stable()
    test_outcomes_constant_stable()

    if FAILURES:
        print(f"\n{len(FAILURES)} failed: {FAILURES}")
        return 1
    print("\nall STEP 7 contract checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())

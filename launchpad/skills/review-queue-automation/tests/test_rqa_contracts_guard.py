#!/usr/bin/env python3
"""Ownership guard: one declaration site per shared name.

`architecture/code/CONTRACTS.md` is the seam truth only while exactly one module
declares each of its types. This guard fails when any module under `rqa/` other
than `rqa/contracts.py` declares a name `rqa/contracts.py` owns — a second
declaration of `Route` or `Judgement` anywhere in the package is a split seam,
whatever it is called.

It is deliberately a source scan (`ast`), not an import: it must work before the
modules it inspects exist, and must not care whether they import cleanly.

The converse is guarded too. §2 (the protocol types) belongs to `rqa.protocol`
per `code/P-04-protocol.md` §1 and §9 (the edge signatures and their Protocols)
belongs to the edge lane, so `rqa/contracts.py` declaring one of *those* names
fails here as well. A later re-export (`from rqa.protocol import Category`) is
an import, not a declaration, and is therefore allowed by construction.
"""

from __future__ import annotations

import ast
import pathlib

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
CONTRACTS = RQA / "contracts.py"

# `CONTRACTS.md` §2 — owner `rqa.protocol` (`code/P-04-protocol.md` §1).
SECTION_2_NAMES = frozenset(
    {
        "EvidenceState",
        "Category",
        "MECHANICAL_GROUP",
        "SUBSTANTIVE_GROUP",
        "Location",
        "Remedy",
        "Finding",
        "InjectionAttempt",
        "HarnessIdentity",
        "Verdict",
        "Valid",
        "Invalid",
        "Obligation",
        "matches",
    }
)

# `CONTRACTS.md` §9 — the edge signatures and the Protocols declared with them.
# §7's `RecordWriter`/`RecordReader` are NOT here: those are declared in §7.
SECTION_9_NAMES = frozenset(
    {
        "inventory",
        "claim_lease",
        "release_lease",
        "admit",
        "snapshot_for",
        "grant",
        "carry_over",
        "route",
        "reserve",
        "plan",
        "run",
        "validate",
        "judge",
        "remediate",
        "raise_",
        "pending",
        "resume",
        "submit_review",
        "comment",
        "merge",
        "checks",
        "consumed",
        "probe",
        "facts",
        "HarnessProber",
        "KeyStore",
        "ProcessRunner",
        "LifecycleDeps",
        "SupplyPort",
        "SnapshotStore",
        "CapabilityStore",
        "SpendStore",
        "BreakerStore",
        "EscalationStore",
        "GithubProbe",
    }
)

# A sample of what §1 and §§3-8 own, so the guard fails if the owned set is
# computed from a file that stopped declaring them.
MUST_BE_OWNED = frozenset(
    {
        "Job",
        "JobStatus",
        "Activity",
        "Snapshot",
        "Facts",
        "Route",
        "PanelResult",
        "Judgement",
        "CarryOver",
        "EntryKind",
        "ENTRY_KINDS",
        "RecordWriter",
        "RecordReader",
        "AppendFailed",
        "VerifiedRecordPrefix",
        "RecordUntrusted",
        "Grant",
        "ProcessResult",
    }
)


def _declared_names(source: str) -> set[str]:
    """Top-level names a module declares: classes, functions and assignments.

    Statements nested in a top-level `if` (a `TYPE_CHECKING` block) or `try`
    count too — a declaration is a declaration wherever the module body puts it.
    Class attributes and function locals do not: a field named `hash` inside a
    dataclass is not a declaration of the module-level name `hash`. Imports are
    not declarations either, which is what makes a re-export legal.
    """
    names: set[str] = set()

    def visit(body: list[ast.stmt]) -> None:
        for node in body:
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name):
                    names.add(node.target.id)
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
            elif isinstance(node, ast.If):
                visit(node.body)
                visit(node.orelse)
            elif isinstance(node, ast.Try):
                visit(node.body)
                visit(node.orelse)
                visit(node.finalbody)
                for handler in node.handlers:
                    visit(handler.body)

    visit(ast.parse(source).body)
    return {name for name in names if not name.startswith("__")}


def _owned_names() -> set[str]:
    return _declared_names(CONTRACTS.read_text(encoding="utf-8"))


def _redeclarations(source: str, owned: set[str]) -> set[str]:
    return _declared_names(source) & owned


def test_contracts_module_exists_and_owns_its_documented_names() -> None:
    assert CONTRACTS.is_file(), f"{CONTRACTS} is missing"
    missing = MUST_BE_OWNED - _owned_names()
    assert missing == set(), f"contracts.py no longer declares: {sorted(missing)}"


def test_no_other_rqa_module_declares_a_name_contracts_owns() -> None:
    owned = _owned_names()
    offences: list[str] = []
    for path in sorted(RQA.rglob("*.py")):
        if path == CONTRACTS:
            continue
        for name in sorted(_redeclarations(path.read_text(encoding="utf-8"), owned)):
            offences.append(f"{path.relative_to(RQA.parent)}: {name}")
    assert offences == [], (
        "CONTRACTS.md §1 and §§3-8 types are declared once, in rqa/contracts.py; "
        f"these modules redeclare them: {offences}"
    )


def test_guard_fires_on_a_redeclaration() -> None:
    """A guard that cannot fail is not a guard."""
    owned = _owned_names()
    assert _redeclarations("class Job:\n    pass\n", owned) == {"Job"}
    assert _redeclarations("ENTRY_KINDS = frozenset()\n", owned) == {"ENTRY_KINDS"}


def test_guard_ignores_the_protocol_part_declaring_its_own_section_two_names() -> None:
    """`rqa/protocol` declaring §2 is correct, not an offence."""
    protocol_source = (
        "class EvidenceState(str, Enum):\n"
        "    VERIFIED = 'verified'\n"
        "\n"
        "class Category(str, Enum):\n"
        "    MECHANICAL = 'mechanical'\n"
        "\n"
        "MECHANICAL_GROUP: frozenset[Category] = frozenset()\n"
        "\n"
        "@dataclass(frozen=True)\n"
        "class Finding:\n"
        "    id: str\n"
        "\n"
        "def matches(path: str, pattern: str) -> bool: ...\n"
    )
    assert _redeclarations(protocol_source, _owned_names()) == set()


def test_guard_ignores_imports_and_re_exports() -> None:
    """A part importing a shared type is the intended use, not a redeclaration."""
    consumer = (
        "from rqa.contracts import Job, Route, ENTRY_KINDS\n"
        "from rqa.contracts import Judgement as J\n"
    )
    assert _redeclarations(consumer, _owned_names()) == set()


def test_guard_ignores_fields_and_locals_sharing_a_shared_name() -> None:
    """Only module-level declarations count."""
    incidental = (
        "class Holder:\n"
        "    plan: str\n"
        "    Job = 1\n"
        "\n"
        "def build():\n"
        "    Route = object()\n"
        "    return Route\n"
    )
    assert _redeclarations(incidental, _owned_names()) == set()


def test_contracts_declares_no_section_two_or_section_nine_name() -> None:
    owned = _owned_names()
    intruders = sorted(owned & (SECTION_2_NAMES | SECTION_9_NAMES))
    assert intruders == [], (
        "rqa/contracts.py owns CONTRACTS.md §1 and §§3-8 only; §2 belongs to "
        f"rqa/protocol and §9 to the edge lane, but it declares: {intruders}"
    )

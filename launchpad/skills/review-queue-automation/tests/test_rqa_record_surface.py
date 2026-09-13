#!/usr/bin/env python3
"""`rqa.record`'s public surface and its exclusions — `code/P-12-record.md` §1, §5, §7,
and §8's closing property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**Why the module and export assertions name two states.** §1 specifies eleven modules
and twenty-eight re-exports for the finished package. The `explain`/`migrate` half —
`explain.py`, `migrate.py`, `reader.py`'s `resolve_job`, and their thirteen names — is a
sibling lane's, landing separately. A test frozen to the nine-module / fifteen-name
state this lane produces would have to be edited when that lane merges, and a test
frozen to the finished state would fail until it does. Asserting membership of exactly
those two real states catches both a lane adding surface §1 does not specify and a
botched merge that lands half a package — while never asserting that a sibling's
contract-required work is absent.
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.record  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
RECORD = RQA / "record"

#: §1's module list, split by the lane that builds each module.
APPEND_MODULES = frozenset(
    {"__init__", "kinds", "hashing", "keychain", "store", "writer", "verify", "reader", "trace"}
)
EXPLAIN_MODULES = frozenset({"explain", "migrate"})
ALL_MODULES = APPEND_MODULES | EXPLAIN_MODULES

#: §1's re-export list, split the same way.
APPEND_EXPORTS = frozenset(
    {
        "RecordWriter",
        "RecordReader",
        "Entry",
        "RecordRow",
        "EntryKind",
        "AppendFailed",
        "RecordProgrammingError",
        "UnknownEntryKind",
        "PayloadNotSerializable",
        "ENTRY_KINDS",
        "KeyStore",
        "KeyStoreExplanationUnavailable",
        "verify",
        "VerifyResult",
        "BreakKind",
    }
)
EXPLAIN_EXPORTS = frozenset(
    {
        "explain",
        "explain_job",
        "resolve_job",
        "ResolvedJob",
        "NoRecord",
        "AmbiguousHead",
        "Explanation",
        "ExplanationUnavailable",
        "ReuseResolutionError",
        "migrate_legacy",
        "MigrationSummary",
        "MigrationTableResult",
        "LegacySource",
    }
)
ALL_EXPORTS = APPEND_EXPORTS | EXPLAIN_EXPORTS


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(RECORD.glob("*.py"))
    }


def _imported(source: str, *, top_level_only: bool = False) -> set[str]:
    """Every module and name this source imports, as dotted strings.

    From the syntax tree, not a text scan: several docstrings here quote the names this
    part must not use — "never imports `rqa.policy`" is exactly the promise being
    checked — and a text scan would report the documentation of a rule as a breach of it.
    """
    tree = ast.parse(source)
    nodes = tree.body if top_level_only else list(ast.walk(tree))
    names: set[str] = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


def _identifiers(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
    return names


def _statement_literals(source: str) -> list[str]:
    """Every string literal the module *executes*, docstrings excluded.

    The same reason `_imported` reads the syntax tree: `store.py`'s docstring says in
    terms that there is no purge, delete or vacuum statement here, and a raw text scan
    would report that promise as the breach of itself.
    """
    tree = ast.parse(source)
    docstrings: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            body = getattr(node, "body", [])
            first = body[0] if body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))
    return [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
    ]


# -- §1: the package surface ---------------------------------------------------


def test_the_module_set_is_one_of_the_two_states_section_one_specifies() -> None:
    found = frozenset(path.stem for path in RECORD.glob("*.py"))
    assert found in (APPEND_MODULES, ALL_MODULES), (
        f"rqa/record holds {sorted(found)}; §1 specifies {sorted(ALL_MODULES)}, of which "
        f"{sorted(APPEND_MODULES)} is the pre-explain state"
    )


def test_all_is_one_of_the_two_states_section_one_specifies() -> None:
    exported = list(rqa.record.__all__)
    assert len(exported) == len(set(exported)), f"duplicate re-export: {exported}"
    assert frozenset(exported) in (APPEND_EXPORTS, ALL_EXPORTS), (
        f"__all__ is {sorted(exported)}; §1 specifies {sorted(ALL_EXPORTS)}"
    )


def test_every_re_exported_name_actually_resolves() -> None:
    missing = [name for name in rqa.record.__all__ if not hasattr(rqa.record, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"


def test_the_implementations_are_not_public_package_surface() -> None:
    """§1's re-export list names no implementation class: `SQLiteRecordWriter`,
    `SQLiteRecordReader`, `OSKeyStore` and `UnverifiableSegment` stay module names, the
    way `rqa.policy` keeps `SnapshotStore` a `rqa.policy.store` name. They remain
    importable from their own modules — a sibling lane imports `UnverifiableSegment`
    from `rqa.record.verify`."""
    for name in ("SQLiteRecordWriter", "SQLiteRecordReader", "OSKeyStore", "UnverifiableSegment"):
        assert name not in rqa.record.__all__, name

    from rqa.record.keychain import OSKeyStore
    from rqa.record.reader import SQLiteRecordReader
    from rqa.record.verify import UnverifiableSegment
    from rqa.record.writer import SQLiteRecordWriter

    for implementation in (OSKeyStore, SQLiteRecordReader, UnverifiableSegment, SQLiteRecordWriter):
        assert isinstance(implementation, type), implementation


def test_the_package_declares_nothing_it_only_re_exports() -> None:
    """§1: the shared record vocabulary has exactly one definition, in `rqa.contracts`."""
    tree = ast.parse((RECORD / "__init__.py").read_text(encoding="utf-8"))
    declarations = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert declarations == []


def test_the_seam_types_are_the_ones_contracts_declares() -> None:
    import rqa.contracts as contracts

    for name in (
        "RecordWriter",
        "RecordReader",
        "Entry",
        "RecordRow",
        "EntryKind",
        "AppendFailed",
        "ENTRY_KINDS",
        "KeyStore",
    ):
        assert getattr(rqa.record, name) is getattr(contracts, name), name


def test_the_closed_set_is_section_sixs_fourteen_kinds() -> None:
    """§2's assertion, as a test rather than as a runtime `assert` that `-O` removes."""
    assert rqa.record.ENTRY_KINDS == frozenset(
        {
            "transition",
            "plan",
            "carry_over",
            "bundle",
            "attestation",
            "spend",
            "panel",
            "judgement",
            "grant",
            "action",
            "escalation",
            "decision",
            "snapshot",
            "legacy",
        }
    )


def test_no_module_here_is_a_stub() -> None:
    """A stub would satisfy §1's module list while hiding an unbuilt entry point."""
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name


# -- §8's closing property and §5's single writer ------------------------------

_RECORD_INSERT = re.compile(r"INSERT INTO record_entries|INSERT INTO record_heads")


def test_only_the_record_store_writes_the_two_record_tables() -> None:
    """§8: `grep -rn "INSERT INTO record_entries\\|INSERT INTO record_heads" rqa/
    --include=*.py` returns hits only inside `rqa/record/store.py`.

    Written as §8 states it — a scan of the whole `rqa/` tree — so it keeps holding
    when the migration lands: §6 has the one-time migration write through `store.py`'s
    own primitives, not through a second insert of its own.
    """
    writers = sorted(
        str(path.relative_to(RQA.parent))
        for path in RQA.rglob("*.py")
        if _RECORD_INSERT.search(path.read_text(encoding="utf-8"))
    )
    assert writers == ["rqa/record/store.py"], writers


def test_no_module_here_deletes_purges_or_vacuums_anything() -> None:
    """§5 and §7: "Retention: none" — U-DISPATCH-06 is binned and there is no delete,
    purge, vacuum or compaction statement anywhere in `rqa/record/`."""
    for name, source in _sources().items():
        for literal in _statement_literals(source):
            upper = literal.upper()
            for statement in ("DELETE FROM", "DROP TABLE", "VACUUM", "TRUNCATE"):
                assert statement not in upper, f"{name} contains {statement}"


def test_no_module_here_reads_a_table_another_part_owns() -> None:
    """§7: P-12 does not read `jobs`, `pr_facts`, `leases`, `snapshots`, `capabilities`,
    `mutations`, `spend`, `breakers` or `human_requests`."""
    others = (
        "jobs",
        "pr_facts",
        "leases",
        "snapshots",
        "capabilities",
        "mutations",
        "spend",
        "breakers",
        "human_requests",
    )
    pattern = re.compile(r"\bFROM\s+(\w+)|\bINTO\s+(\w+)|\bUPDATE\s+(\w+)", re.IGNORECASE)
    for name, source in _sources().items():
        for literal in _statement_literals(source):
            for match in pattern.finditer(literal):
                table = next(group for group in match.groups() if group)
                assert table not in others, f"{name} touches {table}"


# -- §7: what this part does not do --------------------------------------------


def test_nothing_here_catches_append_failed_or_swallows_a_failure() -> None:
    """§7: "Does not catch `AppendFailed` anywhere inside `rqa.record`; every raise site
    in §3.1 lets it propagate to the caller unmodified."

    The scan is wider than the prohibition on purpose: a bare `except`, or one catching
    `Exception`, is how U-DISPATCH-20's defect was written — `except Exception: pass`
    around a ledger write — and it would catch `AppendFailed` without naming it.
    """
    offences: list[str] = []
    for name, source in _sources().items():
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.ExceptHandler):
                continue
            if node.type is None:
                offences.append(f"{name}: bare except")
                continue
            caught = {
                child.id for child in ast.walk(node.type) if isinstance(child, ast.Name)
            }
            for forbidden in ("AppendFailed", "Exception", "BaseException"):
                if forbidden in caught:
                    offences.append(f"{name}: except {forbidden}")
    assert offences == [], offences


def test_no_module_here_reaches_the_network_a_model_or_a_vcs() -> None:
    """§1: "Nothing in this package opens a socket, spawns `gh` or `git`, or invokes a
    model." §8's T7 proves the same property behaviourally; this catches the import that
    would make it possible."""
    forbidden = ("socket", "urllib", "http", "http.client", "requests", "httpx", "ssl")
    for name, source in _sources().items():
        imported = _imported(source)
        for module in forbidden:
            assert module not in imported, f"{name} imports {module}"
        for tool in ("gh", "git", "gh auth token"):
            assert f'"{tool}"' not in source, f"{name} names {tool}"


def test_the_only_subprocess_in_this_package_is_the_local_keychain_command() -> None:
    """§1: "`keychain.py`'s one subprocess (`security`, macOS's local keychain CLI) is
    local-only"."""
    for name, source in _sources().items():
        if name.endswith("keychain.py"):
            assert "subprocess" in _imported(source)
            assert '"security"' in source
            continue
        assert "subprocess" not in _imported(source), name


def test_no_module_here_imports_another_parts_package() -> None:
    """§1: "No module in `rqa.record` imports from any other part's package". The seam
    modules `rqa.contracts` and `rqa.edges` are not a part's package."""
    parts = (
        "rqa.policy",
        "rqa.protocol",
        "rqa.lifecycle",
        "rqa.queue",
        "rqa.github",
        "rqa.supply",
        "rqa.harness",
        "rqa.judgement",
        "rqa.authority",
        "rqa.remediation",
        "rqa.escalation",
        "rqa.reuse",
    )
    for name, source in _sources().items():
        imported = _imported(source)
        for part in parts:
            assert not any(entry.startswith(part) for entry in imported), f"{name}: {part}"


def test_no_authoritative_module_here_reads_the_trace() -> None:
    """§7: "Does not read `jobs/<job>/trace.jsonl` for any purpose, including `explain`;
    the trace is written-only from this part and never authoritative"."""
    for name, source in _sources().items():
        if name.endswith("trace.py"):
            continue
        assert "rqa.record.trace" not in _imported(source), name
        assert "trace_lines" not in _identifiers(source), name


def test_this_part_never_writes_generates_or_rotates_the_operator_key() -> None:
    """§7 and ADR-F. The key is read, used, and dropped."""
    for name, source in _sources().items():
        identifiers = _identifiers(source)
        for forbidden in ("token_bytes", "urandom", "generate_key", "rotate"):
            assert forbidden not in identifiers, f"{name} calls {forbidden}"

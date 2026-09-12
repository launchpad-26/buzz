#!/usr/bin/env python3
"""`rqa.intake`'s public surface and its exclusions — `code/P-01-intake.md`
§1, §5, §7.

Wave-invariant by construction (the issue's §4). This lane implements §§1-2
and §5's queue primitives and store: five of §1's ten modules and eleven of
its fourteen re-exports. The sibling lane (`admission.py`, `inventory.py`,
`lease.py`, `batch.py`, `tick.py`, plus `tick`/`Lease`/`GithubAdapter`) lands
after this one merges. Every assertion below checks membership of exactly one
of the two legitimate states — this lane's state, or the full state once the
sibling lands — never a subset relation, never "at least these", and never
that a sibling file or name is absent.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.intake as intake  # noqa: E402
from rqa.intake.store import JobStore, LeaseStore, PrFactsStore  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
INTAKE = RQA / "intake"

#: §1's ten-module list, split by lane. Never assert the sibling's files are
#: absent; assert membership of one of these two sets instead.
MODULES_THIS_LANE = frozenset({"__init__", "identity", "lock", "store", "types"})
MODULES_FULL = MODULES_THIS_LANE | frozenset({"admission", "inventory", "lease", "batch", "tick"})

#: §1's fourteen-name re-export list, split the same way.
EXPORTS_THIS_LANE = frozenset(
    {
        "TickResult", "AdmissionRefusal", "JobFailure", "job_id", "stable_hash",
        "JobStore", "PrFactsStore", "LeaseStore", "PrFactsRow", "LeaseRow", "IntakeError",
    }
)
EXPORTS_FULL = EXPORTS_THIS_LANE | frozenset({"tick", "Lease", "GithubAdapter"})

#: §1: the only parts this package may import at all, at any point in the wave.
ALLOWED_PART_PREFIXES = ("rqa.contracts", "rqa.record", "rqa.policy", "rqa.github", "rqa.intake")


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(INTAKE.rglob("*.py"))
    }


def _tree_sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(RQA.rglob("*.py"))
    }


def _imported_modules(source: str) -> set[str]:
    imported: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


# -- §1: module set and re-export list, membership of exactly one of two states ----


def test_the_module_set_is_one_of_the_two_legitimate_wave_states() -> None:
    found = frozenset(path.stem for path in INTAKE.glob("*.py"))
    assert found in (MODULES_THIS_LANE, MODULES_FULL), sorted(found)


def test_all_is_one_of_the_two_legitimate_export_states() -> None:
    exported = frozenset(intake.__all__)
    assert exported in (EXPORTS_THIS_LANE, EXPORTS_FULL), sorted(exported)
    assert len(intake.__all__) == len(set(intake.__all__))


def test_every_re_exported_name_resolves() -> None:
    missing = [name for name in intake.__all__ if not hasattr(intake, name)]
    assert missing == []


def test_job_and_jobstatus_are_imported_never_redefined_here() -> None:
    """`Job`/`JobStatus` are `CONTRACTS.md` §1's one definition."""
    for name, source in _sources().items():
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ClassDef) and node.name in ("Job", "JobStatus"):
                raise AssertionError(f"{name} redefines {node.name}")


def test_store_protocols_are_the_shape_this_lane_declares_not_a_second_copy() -> None:
    assert intake.JobStore is JobStore
    assert intake.PrFactsStore is PrFactsStore
    assert intake.LeaseStore is LeaseStore


# -- §1: forbidden/allowed imports, a forever property ------------------------------


def test_no_module_here_imports_a_part_section_one_forbids() -> None:
    offenders = []
    for name, source in _sources().items():
        for module in _imported_modules(source):
            if not module.startswith("rqa"):
                continue
            if any(module == prefix or module.startswith(prefix + ".") for prefix in ALLOWED_PART_PREFIXES):
                continue
            offenders.append((name, module))
    assert offenders == [], offenders


def test_only_rqa_github_writes_imports_intake_identity_directly() -> None:
    """§1's one documented exception, the other direction: nothing outside
    `rqa/github/writes.py` imports `rqa.intake` directly."""
    offenders = []
    for name, source in _tree_sources().items():
        if name == "rqa/github/writes.py" or name.startswith("rqa/intake/"):
            continue
        imported = _imported_modules(source)
        if any(module == "rqa.intake" or module.startswith("rqa.intake.") for module in imported):
            offenders.append(name)
    assert offenders == [], offenders


# -- §5: this package alone writes jobs, pr_facts and leases ------------------------


def test_only_the_intake_store_writes_jobs_pr_facts_and_leases() -> None:
    """`P-01-intake.md` §5/§7: `set_status`/`set_snapshot_hash` exist only so
    `code/P-02-lifecycle.md` can call them, and `jobs`'s "written by P-01" in
    `container.md` §5 means row creation — those two columns are documented
    exceptions lifecycle owns after the initial `INSERT`. `P-02-lifecycle.md`
    §5's write protocol is exactly the two `UPDATE jobs` statements in
    `rqa/lifecycle/transition.py`. So `rqa/lifecycle/transition.py` writing
    `jobs` is the contract, not drift; this stays an exact-set assertion so a
    fifth, unauthorised writer is still caught.
    """
    writers = []
    for name, source in _tree_sources().items():
        lowered = source.lower()
        for table in ("jobs", "pr_facts", "leases"):
            for verb in (f"insert into {table}", f"update {table} set", f"delete from {table}"):
                if verb in lowered:
                    writers.append((name, table))
                    break
    assert sorted(set(writers)) == [
        ("rqa/intake/store.py", "jobs"),
        ("rqa/intake/store.py", "leases"),
        ("rqa/intake/store.py", "pr_facts"),
        ("rqa/lifecycle/transition.py", "jobs"),
    ], writers


def test_only_lock_py_names_the_sweep_lock_filename() -> None:
    """`flock(...)` alone is not this property: `rqa.record`'s own sidecar
    trace lock is an unrelated file. This checks the one thing §5 actually
    fixes — `<state_dir>/lock`, the sweep lock's own filename."""
    offenders = [
        name
        for name, source in _tree_sources().items()
        if name != "rqa/intake/lock.py" and ('"lock"' in source or "'lock'" in source)
    ]
    assert offenders == [], offenders


# -- conventions ---------------------------------------------------------------------


def test_no_pep_695_type_alias_statements_anywhere_in_the_package() -> None:
    """`type X = ...` is a parse-time SyntaxError on Python 3.11, which the CI
    gate runs against."""
    for name, source in _sources().items():
        for node in ast.walk(ast.parse(source)):
            assert type(node).__name__ != "TypeAlias", f"{name} uses a PEP-695 alias"


def test_store_protocol_methods_preserve_their_documented_positional_form() -> None:
    """§5's `Protocol` methods are written positionally in P-01's own
    contract text (e.g. `def current_for_pr(self, repo: str, number: int)`),
    an explicit, documented exception to the "every function keyword-only"
    convention — preserved exactly, never converted to keyword-only."""
    for protocol, methods in (
        (JobStore, ("create", "get", "current_for_pr", "select_batch", "pending_followup", "set_status", "set_snapshot_hash")),
        (PrFactsStore, ("upsert", "get")),
        (LeaseStore, ("current", "put", "delete")),
    ):
        for method_name in methods:
            parameters = list(inspect.signature(getattr(protocol, method_name)).parameters.values())[1:]
            assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in parameters), (
                protocol.__name__,
                method_name,
            )


def test_job_id_and_stable_hash_are_the_contracts_signature_shape() -> None:
    """`stable_hash` is documented as variadic; `job_id` is called
    positionally at its one P-01 §3 call site (`job_id(repo, pf.number,
    pf.head_sha)`) — neither is forced keyword-only."""
    stable_hash_params = list(inspect.signature(intake.stable_hash).parameters.values())
    assert stable_hash_params[0].kind is inspect.Parameter.VAR_POSITIONAL

    job_id_params = list(inspect.signature(intake.job_id).parameters.values())
    assert [p.name for p in job_id_params] == ["repo", "number", "head_sha"]
    assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in job_id_params)

#!/usr/bin/env python3
"""`rqa.lifecycle`'s public surface and its exclusions — `code/P-02-lifecycle.md` §1, §2,
§4, §5, §7, and §8's closing property.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

**Why the module and export assertions name two states.** §1 specifies nine modules and
fourteen re-exports for the finished package. The cascade half — `steps.py`, `rest.py`,
`resume.py` and the `resume` re-export — is a sibling lane's, landing separately. A test
frozen to the seven-module / thirteen-name state this lane produces would have to be
edited when that lane merges, and a test frozen to the finished state would fail until it
does. Asserting membership of exactly those two real states catches both a lane adding
surface §1 does not specify and a botched merge that lands half a package — while never
asserting that a sibling's contract-required work is absent.

**Why the `jobs.status` property is asserted twice, two different ways.** §8's closing
property is a literal grep: `jobs.status\\s*=` must hit nothing outside
`rqa/lifecycle/transition.py`. That regex does not match the SQL either this part or
P-01's `JobStore.set_status` actually executes (`UPDATE jobs SET status = ?`), so on its
own it is nearly vacuous — and tightening it tree-wide would fail the moment
`rqa/intake/store.py` lands with the `set_status`/`set_snapshot_hash` writers P-01 §5
declares. So the documented regex is checked tree-wide, exactly as written, and the
structural claim — one module in this package issues one `UPDATE jobs` — is checked
scoped to `rqa/lifecycle/*.py`, where it is this part's own invariant and stays true when
the sibling modules land.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import re
import sqlite3
import sys
from dataclasses import FrozenInstanceError, fields, is_dataclass
from importlib import import_module

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.lifecycle  # noqa: E402
import rqa.lifecycle.deps as deps_module  # noqa: E402
from rqa.contracts import Job, JobStatus  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
LIFECYCLE = RQA / "lifecycle"

#: §1's module list, split by the lane that builds each module.
KERNEL_MODULES = frozenset(
    {"__init__", "states", "errors", "deps", "transition", "status", "admit"}
)
CASCADE_MODULES = frozenset({"steps", "rest", "resume"})
ALL_MODULES = KERNEL_MODULES | CASCADE_MODULES

#: §1's re-export list, split the same way.
KERNEL_EXPORTS = frozenset(
    {
        "admit",
        "status",
        "transition",
        "JobStatus",
        "TRANSITIONS",
        "Disposition",
        "DISPOSITION",
        "StatusReport",
        "NotFound",
        "StaleDecisionError",
        "LifecycleError",
        "IllegalTransitionError",
        "UnknownJobError",
    }
)
CASCADE_EXPORTS = frozenset({"resume"})
ALL_EXPORTS = KERNEL_EXPORTS | CASCADE_EXPORTS

#: §2's fifteen `LifecycleDeps` fields, in §2's order. P-01 constructs this bundle with
#: fifteen keyword arguments (`code/P-01-intake.md` §3 step 5); a renamed or reordered
#: field breaks a part this one never sees.
DEPS_FIELDS = (
    "policy",
    "authority",
    "supply",
    "harness",
    "judgement",
    "remediation",
    "escalation",
    "github",
    "reuse",
    "record",
    "connection",
    "state_dir",
    "runner",
    "claim_lease",
    "release_lease",
)


def _sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(LIFECYCLE.glob("*.py"))
    }


def _tree_sources() -> dict[str, str]:
    return {
        str(path.relative_to(RQA.parent)): path.read_text(encoding="utf-8")
        for path in sorted(RQA.rglob("*.py"))
    }


def _imported(source: str) -> set[str]:
    """Every module and name this source imports, as dotted strings.

    From the syntax tree, not a text scan: the docstrings here quote the names this part
    must not import — "never imports another part's package" is exactly the promise being
    checked — and a text scan would report the documentation of a rule as a breach of it.
    """
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            names.add(module)
            names.update(f"{module}.{alias.name}" for alias in node.names)
    return names


def _statement_literals(source: str) -> list[str]:
    """Every string literal the module *executes*, docstrings excluded."""
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
    found = frozenset(path.stem for path in LIFECYCLE.glob("*.py"))
    assert found in (KERNEL_MODULES, ALL_MODULES), (
        f"rqa/lifecycle holds {sorted(found)}; §1 specifies {sorted(ALL_MODULES)}, of "
        f"which {sorted(KERNEL_MODULES)} is the pre-cascade state"
    )


def test_all_is_one_of_the_two_states_section_one_specifies() -> None:
    exported = list(rqa.lifecycle.__all__)
    assert len(exported) == len(set(exported)), f"duplicate re-export: {exported}"
    assert frozenset(exported) in (KERNEL_EXPORTS, ALL_EXPORTS), (
        f"__all__ is {sorted(exported)}; §1 specifies {sorted(ALL_EXPORTS)}"
    )


def test_every_re_exported_name_actually_resolves() -> None:
    missing = [name for name in rqa.lifecycle.__all__ if not hasattr(rqa.lifecycle, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"


def test_lifecycle_deps_is_importable_from_the_package_without_being_exported() -> None:
    """§1's re-export list does not name `LifecycleDeps`, and `code/P-01-intake.md` §3
    step 5 constructs it as `from rqa.lifecycle import LifecycleDeps, admit`. Binding the
    name without listing it in `__all__` is what satisfies both."""
    assert rqa.lifecycle.LifecycleDeps is deps_module.LifecycleDeps
    assert "LifecycleDeps" not in rqa.lifecycle.__all__


def test_the_shared_status_type_is_the_one_contracts_declares() -> None:
    """§2: `JobStatus` is `CONTRACTS.md` §1's type, imported and re-exported, never
    redefined. An independent enum with the same members would compare unequal to every
    stored value in the rest of RQA."""
    assert rqa.lifecycle.JobStatus is contracts.JobStatus
    assert len(list(contracts.JobStatus)) == 13


def test_this_package_declares_no_shared_type() -> None:
    """§2: every value P-02 exchanges is imported from `CONTRACTS.md`. Only the
    P-02-local types §2 names, and §4's injection Protocols, are declared here.

    Module-level classes only: §4's Protocols legitimately carry methods named after the
    §9 edge callables they repeat (`grant`, `judge`, `facts`), and `admit`/`status` are
    §9 signatures this part *provides* — implementing an edge is the opposite of
    redeclaring a shared type."""
    local = {
        "Disposition",
        "StatusReport",
        "NotFound",
        "LifecycleError",
        "StaleDecisionError",
        "IllegalTransitionError",
        "UnknownJobError",
        "LifecycleDeps",
        "PolicyClient",
        "AuthorityClient",
        "ReuseClient",
        "SupplyClient",
        "HarnessClient",
        "JudgementClient",
        "RemediationClient",
        "EscalationClient",
        "GithubClient",
    }
    shared = {
        name
        for name in contracts.__all__
        if isinstance(getattr(contracts, name), type) and name not in local
    }
    offences = [
        f"{name} declares {node.name}"
        for name, source in _sources().items()
        for node in ast.parse(source).body
        if isinstance(node, ast.ClassDef) and node.name in shared
    ]
    assert offences == [], offences


def test_no_module_here_imports_another_parts_package() -> None:
    """§1: "No module in `rqa.lifecycle` imports from another part's package". The seam
    is `rqa.contracts`; reaching a neighbour's implementation directly would make one
    part's proof depend on another's internals."""
    forbidden = (
        "rqa.protocol",
        "rqa.policy",
        "rqa.authority",
        "rqa.github",
        "rqa.supply",
        "rqa.harness",
        "rqa.judgement",
        "rqa.reuse",
        "rqa.remediation",
        "rqa.intake",
        "rqa.escalation",
    )
    for name, source in _sources().items():
        imported = _imported(source)
        for part in forbidden:
            assert not any(entry.startswith(part) for entry in imported), f"{name}: {part}"


def test_no_module_here_is_a_stub() -> None:
    """A stub would satisfy §1's module list while hiding an unbuilt entry point."""
    for name, source in _sources().items():
        for marker in ("TODO", "FIXME", "NotImplementedError"):
            assert marker not in source, f"{name} contains {marker}"


def test_no_module_here_reaches_the_network_a_model_a_vcs_or_a_subprocess() -> None:
    """§7: every external effect is a listed neighbour edge. This part calls GitHub, a
    harness and a model only through the injected clients in `LifecycleDeps`."""
    for name, source in _sources().items():
        imported = _imported(source)
        for module in ("socket", "subprocess", "http", "urllib", "requests"):
            assert not any(entry.split(".")[0] == module for entry in imported), (
                f"{name} imports {module}"
            )


# -- §5 and §8: the one column, and the one writer of it -----------------------

#: §8's closing property, verbatim, including its unescaped `.`.
JOBS_STATUS_ASSIGNMENT = re.compile(r"jobs.status\s*=")
UPDATE_JOBS = re.compile(r"UPDATE\s+jobs\b", re.IGNORECASE)


def test_the_documented_grep_property_holds_across_the_whole_tree() -> None:
    """§8: `grep -rn "jobs.status\\s*=" rqa/ --include=*.py` returns hits only inside
    `rqa/lifecycle/transition.py`. Asserted over every `.py` under `rqa/`, so a future
    part that starts assigning that column fails here."""
    hits = sorted(
        name for name, source in _tree_sources().items() if JOBS_STATUS_ASSIGNMENT.search(source)
    )
    assert hits == ["rqa/lifecycle/transition.py"], hits


def test_one_module_in_this_package_issues_the_one_jobs_write() -> None:
    """§5's write protocol, as a structural claim the documented regex cannot make: among
    this package's modules, only `transition.py` executes a statement against `jobs`."""
    writers = sorted(
        name
        for name, source in _sources().items()
        if any(UPDATE_JOBS.search(literal) for literal in _statement_literals(source))
    )
    assert writers == ["rqa/lifecycle/transition.py"], writers


def test_the_only_columns_written_are_status_and_the_snapshot_pin() -> None:
    """§5: this part owns no DDL and writes exactly `jobs.status` on every transition and
    `jobs.snapshot_hash` once. No insert, no delete, no schema statement anywhere."""
    for name, source in _sources().items():
        for literal in _statement_literals(source):
            upper = literal.upper()
            for statement in ("INSERT INTO", "DELETE FROM", "DROP ", "CREATE TABLE", "ALTER TABLE"):
                assert statement not in upper, f"{name} contains {statement}"
            if UPDATE_JOBS.search(literal):
                assert "SET STATUS" in upper or "SET SNAPSHOT_HASH" in upper, literal


def test_no_module_here_reads_a_table_this_part_may_not_read() -> None:
    """§1 and §7: only `jobs`, `pr_facts`, `leases` and `record_entries`."""
    forbidden = (
        "snapshots",
        "capabilities",
        "spend",
        "breakers",
        "mutations",
        "etags",
        "api_calls",
        "human_requests",
    )
    for name, source in _sources().items():
        for literal in _statement_literals(source):
            lowered = literal.lower()
            if "select" not in lowered and "update" not in lowered:
                continue
            for table in forbidden:
                assert f" {table}" not in lowered, f"{name} touches {table}"


def test_nothing_here_swallows_a_failure() -> None:
    """§5 and the security constraint behind this whole part: a persistence or audit
    failure becomes a safe stop, never a silent continue. A bare `except:`, an
    `except Exception:` or a handler whose body is `pass` is the U-DISPATCH-20 shape this
    part was rewritten to remove."""
    offences: list[str] = []
    for name, source in _sources().items():
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.ExceptHandler):
                continue
            if node.type is None or (
                isinstance(node.type, ast.Name) and node.type.id in {"Exception", "BaseException"}
            ):
                offences.append(f"{name}: over-broad except")
            if all(isinstance(statement, ast.Pass) for statement in node.body):
                offences.append(f"{name}: except with a `pass` body")
    assert offences == [], offences


# -- §3 and §4: the signatures this part must implement verbatim ---------------


def test_admit_is_the_e02_signature_contracts_declares() -> None:
    """E-02, `rqa/edges.py:150`: `def admit(*, job: Job, deps: LifecycleDeps) -> JobStatus`."""
    declared = inspect.signature(contracts.admit)
    implemented = inspect.signature(rqa.lifecycle.admit)
    assert [p.name for p in implemented.parameters.values()] == [
        p.name for p in declared.parameters.values()
    ]
    assert [p.kind for p in implemented.parameters.values()] == [
        p.kind for p in declared.parameters.values()
    ]
    assert all(
        p.kind is inspect.Parameter.KEYWORD_ONLY for p in implemented.parameters.values()
    )


def test_status_keeps_the_positional_form_section_three_four_states() -> None:
    """E-17 is prose-only in `CONTRACTS.md` §9, so §3.4 is authoritative for this
    callable's form: `status(repo, number, *, connection)`. `repo` and `number` are
    positional — the keyword-only convention does not override a documented exception."""
    parameters = list(inspect.signature(rqa.lifecycle.status).parameters.values())
    assert [p.name for p in parameters] == ["repo", "number", "connection"]
    assert parameters[0].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters[1].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters[2].kind is inspect.Parameter.KEYWORD_ONLY


def test_transition_takes_job_and_to_positionally_and_offers_the_snapshot_pin() -> None:
    """§8 T1's form is `transition(job, to, ...)`. The keyword-only `snapshot_hash` is
    what makes §5's "writes `jobs.snapshot_hash` exactly once — immediately after a
    successful first E-03 pin, in the same transaction as that transition" expressible by
    the step that pins."""
    parameters = list(inspect.signature(rqa.lifecycle.transition).parameters.values())
    assert [p.name for p in parameters[:2]] == ["job", "to"]
    assert all(p.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for p in parameters[:2])
    rest = {p.name: p for p in parameters[2:]}
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in rest.values())
    assert "snapshot_hash" in rest and rest["snapshot_hash"].default is None


def test_lifecycle_deps_is_section_twos_fifteen_frozen_fields() -> None:
    """§2's bundle. P-01 constructs it with these fifteen keyword arguments."""
    assert is_dataclass(deps_module.LifecycleDeps)
    assert tuple(f.name for f in fields(deps_module.LifecycleDeps)) == DEPS_FIELDS
    bundle = deps_module.LifecycleDeps(**{name: object() for name in DEPS_FIELDS})
    try:
        bundle.policy = object()
    except FrozenInstanceError:
        pass
    else:  # pragma: no cover - the assert below is the failure report
        raise AssertionError("LifecycleDeps is not frozen")


def test_every_neighbour_protocol_repeats_its_contracts_signature() -> None:
    """§4: "These protocol declarations repeat those signatures verbatim for injection;
    P-02 defines no exchanged type and no alternative convenience overload." Compared
    against `rqa.edges`'s own declaration of each edge, parameter for parameter."""
    edges = {
        "PolicyClient": {"snapshot_for": contracts.snapshot_for},
        "AuthorityClient": {"grant": contracts.grant},
        "ReuseClient": {"carry_over": contracts.carry_over},
        "SupplyClient": {
            "route": contracts.route,
            "reserve": contracts.reserve,
            "consumed": contracts.consumed,
        },
        "HarnessClient": {"plan": contracts.plan, "run": contracts.run},
        "JudgementClient": {"judge": contracts.judge},
        "RemediationClient": {"remediate": contracts.remediate},
        "EscalationClient": {"raise_": contracts.raise_, "pending": contracts.pending},
        "GithubClient": {
            "submit_review": contracts.submit_review,
            "comment": contracts.comment,
            "merge": contracts.merge,
            "facts": contracts.facts,
        },
    }
    for protocol_name, methods in edges.items():
        protocol = getattr(deps_module, protocol_name)
        for method_name, declared_function in methods.items():
            declared = inspect.signature(declared_function)
            implemented = inspect.signature(getattr(protocol, method_name))
            assert [p.name for p in implemented.parameters.values()][1:] == [
                p.name for p in declared.parameters.values()
            ], f"{protocol_name}.{method_name}"
            assert [p.kind for p in implemented.parameters.values()][1:] == [
                p.kind for p in declared.parameters.values()
            ], f"{protocol_name}.{method_name}"


def test_the_error_hierarchy_is_section_twos() -> None:
    for error in (
        rqa.lifecycle.StaleDecisionError,
        rqa.lifecycle.IllegalTransitionError,
        rqa.lifecycle.UnknownJobError,
    ):
        assert issubclass(error, rqa.lifecycle.LifecycleError)
    assert issubclass(rqa.lifecycle.LifecycleError, Exception)


# -- the security constraint: nothing here renders a credential ----------------


class _CredentialBearingClient:
    """A neighbour client holding a token, the way P-09's GitHub client holds one for the
    duration of a call and P-08's authority client reaches one through E-22."""

    def __init__(self) -> None:
        self.token = "ghp_thisMustNeverBeRendered"

    def __repr__(self) -> str:  # pragma: no cover - exercised through LifecycleDeps
        return f"<GithubClient token={self.token}>"


def _bundle_with_credential() -> tuple[object, str]:
    client = _CredentialBearingClient()
    values = dict.fromkeys(DEPS_FIELDS, object())
    values["github"] = client
    values["authority"] = client
    return deps_module.LifecycleDeps(**values), client.token


def test_the_deps_bundle_never_renders_its_clients() -> None:
    """Batches 2c and 3c both found credentials reachable from a traceback frame's
    locals. `deps` is in this part's frames by construction — E-02 takes it — so the
    bundle renders its arity and nothing else."""
    bundle, token = _bundle_with_credential()
    rendered = repr(bundle)
    assert token not in rendered, rendered
    assert "github" not in rendered and "token" not in rendered, rendered
    assert rendered == "LifecycleDeps(<15 injected collaborators; fields elided>)"


def test_a_contained_failure_records_a_type_not_a_message() -> None:
    """The reason string a contained persistence failure writes into the durable record
    carries the exception's *type*, never its message: a message can carry a URL, a
    response body or a credential picked up from whatever raised it."""
    # `rqa.lifecycle.admit` the attribute is the re-exported function; the module is
    # reached through the import system, not through the package namespace.
    admit_module = import_module("rqa.lifecycle.admit")

    reason = admit_module._contained_reason(
        sqlite3.OperationalError("attempt to write a readonly database ghp_secret")
    )
    assert reason == "persistence failure contained (OperationalError)"
    assert "ghp_secret" not in reason


def test_no_lifecycle_error_carries_a_client_a_job_or_a_payload() -> None:
    """`errors.py`: every class is a plain `Exception` with a message and no attributes.
    A structured error would be one more object a traceback renders."""
    for error in (
        rqa.lifecycle.LifecycleError,
        rqa.lifecycle.StaleDecisionError,
        rqa.lifecycle.IllegalTransitionError,
        rqa.lifecycle.UnknownJobError,
    ):
        assert error.__init__ is Exception.__init__, error
        instance = error("a message")
        assert instance.args == ("a message",)
        assert not [name for name in vars(instance)], vars(instance)


def test_an_illegal_transition_message_names_states_not_objects() -> None:
    """The one message this part builds from caller-supplied data. `Job` carries a repo,
    a number and two SHAs — never a credential — and the message quotes only its id."""
    job = Job(
        id="job-1",
        repo="owner/name",
        number=7,
        head_sha="a" * 40,
        base_sha="b" * 40,
        head_repo="owner/name",
        head_ref="feature",
        predecessor_job=None,
        predecessor_head_sha=None,
        snapshot_hash=None,
        status=JobStatus.MERGED,
    )
    try:
        rqa.lifecycle.transition(
            job, JobStatus.APPROVED, reason="r", connection=object(), record=object()
        )
    except rqa.lifecycle.IllegalTransitionError as exc:
        message = str(exc)
    else:  # pragma: no cover - the assert below is the failure report
        raise AssertionError("merged -> approved was accepted")
    assert "merged" in message and "approved" in message and "job-1" in message
    assert "Connection" not in message and "LifecycleDeps" not in message

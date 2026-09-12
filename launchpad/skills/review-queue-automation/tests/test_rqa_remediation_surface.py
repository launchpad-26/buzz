#!/usr/bin/env python3
"""`rqa.remediation`'s public surface, its seam and its exclusions —
`code/P-10-remediation.md` §1, §5, §6, §7 and the security bounds §8 closes over.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

These are structural guards, and each is here because the property it holds is one a
reviewer would otherwise have to re-derive by reading the whole package:

* the package exports exactly §1's list, so a later change cannot widen the surface;
* `git push` argv is built in exactly one file, so "never force-push" is a property of the
  source, not of a code path someone remembered to avoid;
* `worktrees` is written by this package alone, so §5's isolation claim is tree-wide;
* nothing here imports a path matcher, a subprocess primitive, an HTTP client, the
  environment or another part's implementation.
"""

from __future__ import annotations

import ast
import inspect
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.contracts as contracts  # noqa: E402
import rqa.remediation  # noqa: E402
from rqa import edges  # noqa: E402

RQA = pathlib.Path(__file__).resolve().parent.parent / "rqa"
REMEDIATION = RQA / "remediation"

#: §1's module list, in full. This package is one lane's work, so this is the finished
#: set, not a stage of it.
MODULES = frozenset({"__init__", "tools", "worktree", "push", "remediate"})

#: §1's re-export list: `remediate` and shared remediation outcomes, `MECHANICAL_TOOL_SET`,
#: `ToolSpec`, `RemediationError`.
EXPORTS = [
    "remediate",
    "RemediationPushed",
    "RemediationRefused",
    "RemediationRefusalReason",
    "MECHANICAL_TOOL_SET",
    "ToolSpec",
    "RemediationError",
]

#: §6: the only entry kind P-10 writes.
ENTRY_KINDS_WRITTEN = frozenset({"action"})


def _sources() -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8") for path in sorted(REMEDIATION.glob("*.py"))}


def _imported(source: str) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
            for alias in node.names:
                names.add(f"{node.module}.{alias.name}")
    return names


def _identifiers(source: str) -> set[str]:
    """Every name the source references, including string-indirected ones."""
    names: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            names.add(node.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            names.add(node.value)
    return names


def _string_literals(source: str) -> list[str]:
    return [
        node.value
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]


def _argv_literals(source: str) -> list[str]:
    """String literals short enough to be an argument, an option or a path template.

    Prose is excluded deliberately: a docstring that says "never force-push" is the
    documentation of the guarantee, not a violation of it, and a scan that cannot tell
    them apart is a scan nobody can keep green.
    """
    return [
        literal
        for literal in _string_literals(source)
        if len(literal) < 60 and "\n" not in literal
    ]


def _appended_kinds(source: str) -> set[str]:
    """The literal `kind` of every `record.append(job_id, kind, payload)` call."""
    kinds: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.Call):
            continue
        function = node.func
        if not isinstance(function, ast.Attribute) or function.attr != "append":
            continue
        if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
            kinds.add(node.args[1].value)
    return kinds


# -- §1: modules and re-exports -------------------------------------------------


def test_the_module_set_is_exactly_the_one_section_one_lists() -> None:
    found = frozenset(path.stem for path in REMEDIATION.glob("*.py"))
    assert found == MODULES, f"§1 lists {sorted(MODULES)}; the package has {sorted(found)}"


def test_all_is_exactly_section_ones_re_export_list() -> None:
    assert list(rqa.remediation.__all__) == EXPORTS


def test_every_re_exported_name_resolves_and_nothing_else_is_surface() -> None:
    missing = [name for name in rqa.remediation.__all__ if not hasattr(rqa.remediation, name)]
    assert missing == [], f"__all__ names that do not resolve: {missing}"
    for internal in ("build_argv", "validate_remedy_paths", "semantic_fingerprint", "push_head",
                     "checkout_head", "resolve_target", "check_passed"):
        assert internal not in rqa.remediation.__all__, internal


def test_the_seam_types_are_the_ones_contracts_declares() -> None:
    for name in ("RemediationPushed", "RemediationRefused", "RemediationRefusalReason"):
        assert getattr(rqa.remediation, name) is getattr(contracts, name), name


def test_the_package_init_declares_nothing_it_only_re_exports() -> None:
    tree = ast.parse((REMEDIATION / "__init__.py").read_text(encoding="utf-8"))
    declarations = [
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert declarations == []


def test_no_module_here_is_a_stub() -> None:
    for name, source in _sources().items():
        assert "NotImplementedError" not in source, name
        assert "TODO" not in source, name


def test_remediate_matches_the_contracts_md_edge_signature_exactly() -> None:
    assert inspect.signature(rqa.remediation.remediate) == inspect.signature(edges.remediate)


def test_push_head_matches_the_signature_section_four_states() -> None:
    from rqa.remediation.push import push_head

    parameters = inspect.signature(push_head).parameters
    assert [name for name in parameters] == ["runner", "worktree", "head_repo", "head_ref"]
    assert all(
        parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values()
    )
    assert inspect.signature(push_head).return_annotation == "ProcessResult"


def _declarations(text: str) -> dict[str, str]:
    """Every `def` in `text`, joined onto one line and whitespace-normalized."""
    found: dict[str, str] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("def "):
            buffer = line
            while buffer.count("(") > buffer.count(")") and index + 1 < len(lines):
                index += 1
                buffer = f"{buffer} {lines[index].strip()}"
            normalized = " ".join(buffer.split())
            if normalized.endswith("..."):
                normalized = normalized[: -len("...")].strip()
            found[normalized[4 : normalized.index("(")]] = normalized.rstrip(":").strip()
        index += 1
    return found


def test_every_signature_the_part_contract_states_is_implemented_character_for_character() -> None:
    """§2, §3 and §4 state five Python signatures. A lane may not retype one of them, so
    they are compared with the contract text itself rather than with a copy of it."""
    contract = (
        RQA.parent / "architecture" / "code" / "P-10-remediation.md"
    ).read_text(encoding="utf-8")
    stated = _declarations(contract)
    implemented: dict[str, str] = {}
    for source in _sources().values():
        implemented.update(_declarations(source))
    assert set(stated) == {
        "build_argv",
        "validate_remedy_paths",
        "semantic_fingerprint",
        "remediate",
        "push_head",
    }, sorted(stated)
    for name, declaration in sorted(stated.items()):
        assert implemented.get(name) == declaration, (
            f"{name} is implemented as {implemented.get(name)!r}, "
            f"the contract states {declaration!r}"
        )


def test_every_public_function_here_is_keyword_only() -> None:
    """`CONTRACTS.md` preamble: every function keyword-only — unconditionally, with no
    exemption list (G2194-P10-F8)."""
    import importlib

    for suffix in ("tools", "worktree", "push", "remediate"):
        module = importlib.import_module(f"rqa.remediation.{suffix}")
        for name in module.__all__:
            member = getattr(module, name)
            if not inspect.isfunction(member):
                continue
            positional = [
                parameter
                for parameter in inspect.signature(member).parameters.values()
                if parameter.kind
                in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
            ]
            assert positional == [], f"{module.__name__}.{name} takes {positional}"


# -- the no-force-push bound ----------------------------------------------------


def test_git_push_argv_is_built_in_exactly_one_file() -> None:
    """§4: `push_head()` is the only function that builds `git push` argv. One
    construction site is the whole of the guarantee."""
    builders = sorted(name for name, source in _sources().items() if "push" in _argv_literals(source))
    assert builders == ["push.py"], builders


def test_no_module_here_can_construct_a_force_a_second_refspec_or_another_ref() -> None:
    """Over argv-shaped literals: a docstring explaining the guarantee is not a breach of
    it, but a literal short enough to be an argument is exactly what would be."""
    for name, source in _sources().items():
        for literal in _argv_literals(source):
            for forbidden in (
                "--force",
                "force-with-lease",
                "--mirror",
                "--delete",
                "--no-verify",
                "refs/heads/*",
                "+refs",
                "merge",
            ):
                assert forbidden not in literal, f"{name} contains {literal!r}"


def test_the_only_refspec_template_is_the_pr_head_branch() -> None:
    templates = sorted(
        {
            literal
            for source in _sources().values()
            for literal in _argv_literals(source)
            if "refs/heads" in literal
        }
    )
    assert templates == ["HEAD:refs/heads/"], templates


# -- §5: the isolation bound ----------------------------------------------------


def test_this_package_is_the_only_writer_of_worktrees_in_the_tree() -> None:
    """§5's store row, checked tree-wide rather than package-locally."""
    writers = sorted(
        path.relative_to(RQA).as_posix()
        for path in RQA.rglob("*.py")
        if any("worktrees" in literal for literal in _argv_literals(path.read_text(encoding="utf-8")))
    )
    assert writers == ["remediation/worktree.py"], writers


def test_the_worktree_path_is_state_dir_worktrees_job_id() -> None:
    import tempfile

    from rqa.remediation.worktree import path_for

    with tempfile.TemporaryDirectory() as directory:
        state_dir = pathlib.Path(directory)
        assert path_for(state_dir=state_dir, job_id="job-1") == state_dir / "worktrees" / "job-1"


def test_a_job_id_that_is_not_one_path_segment_never_becomes_a_path() -> None:
    from rqa.remediation import RemediationError
    from rqa.remediation.worktree import path_for

    for job_id in ("../escape", "/absolute", "a/b", "", ".", "..", "a\x00b"):
        try:
            path_for(state_dir=pathlib.Path("/tmp"), job_id=job_id)
        except RemediationError:
            continue
        raise AssertionError(f"path_for accepted {job_id!r}")


# -- §7: what P-10 does not do --------------------------------------------------


def test_no_module_here_calls_a_path_matcher() -> None:
    """§1: "it imports no path matcher because remedies name exact files, not patterns";
    §3 step 8: "no glob matcher exists here"."""
    for name, source in _sources().items():
        imported = _imported(source)
        for forbidden in ("glob", "fnmatch", "rqa.protocol.paths", "pathlib.PurePath.match"):
            assert forbidden not in imported, f"{name} imports {forbidden}"
        identifiers = _identifiers(source)
        for forbidden in ("fnmatch", "matches", "glob", "rglob", "iglob"):
            assert forbidden not in identifiers, f"{name} uses {forbidden}"


def test_no_module_here_launches_a_process_itself_or_opens_a_socket() -> None:
    """E-26 is injected; E-20 is git run through that same injected runner. P-05 owns the
    one `subprocess` implementation of the `ProcessRunner` shape."""
    for name, source in _sources().items():
        imported = _imported(source)
        for forbidden in ("subprocess", "os.system", "socket", "http", "urllib", "requests"):
            assert forbidden not in imported, f"{name} imports {forbidden}"
        assert "Popen" not in _identifiers(source), name


def test_no_module_here_reads_configuration_the_environment_or_a_credential() -> None:
    """§7: P-10 does not read live policy; the snapshot is the only policy source. No
    credential is read, held, logged or recorded (RQA-NFR-025)."""
    for name, source in _sources().items():
        identifiers = _identifiers(source)
        for forbidden in ("environ", "getenv", "putenv"):
            assert forbidden not in identifiers, f"{name} uses {forbidden}"
        for forbidden in ("GITHUB_TOKEN", "GH_TOKEN", "Authorization", "auth token", "config.json"):
            assert forbidden not in source, f"{name} mentions {forbidden}"


def test_no_module_here_imports_another_parts_implementation() -> None:
    """§1: cross-part values come only from `rqa.contracts`."""
    allowed = {"rqa.contracts", "rqa.remediation"}
    for name, source in _sources().items():
        for module in _imported(source):
            if not module.startswith("rqa"):
                continue
            root = ".".join(module.split(".")[:2])
            assert root in allowed, f"{name} imports {module}"


def test_no_module_here_writes_a_transition_or_touches_job_status() -> None:
    """§6: "P-10 writes no `transition` and never changes job status."."""
    kinds: set[str] = set()
    for name, source in _sources().items():
        assert "transition" not in _argv_literals(source), name
        assert "JobStatus" not in _identifiers(source), name
        kinds |= _appended_kinds(source)
    assert kinds == ENTRY_KINDS_WRITTEN, kinds


def test_no_module_here_owns_a_store() -> None:
    """§5: "P-10 owns no queryable store."."""
    for name, source in _sources().items():
        for forbidden in ("sqlite3", "json", "pickle"):
            assert forbidden not in _imported(source), f"{name} imports {forbidden}"


def test_the_package_ships_no_pep_695_type_alias() -> None:
    """CI gates on Python 3.11, where `type X = A | B` is a parse-time `SyntaxError`.

    Parsing each module is itself the proof on 3.11; on 3.12+ the node type is checked
    explicitly so the guard does not silently become a no-op on a newer interpreter.
    """
    alias = getattr(ast, "TypeAlias", None)
    for name, source in _sources().items():
        tree = ast.parse(source)
        if alias is not None:
            assert not any(isinstance(node, alias) for node in ast.walk(tree)), name

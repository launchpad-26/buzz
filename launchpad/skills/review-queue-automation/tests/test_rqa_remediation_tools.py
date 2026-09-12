#!/usr/bin/env python3
"""`rqa.remediation.tools` — `code/P-10-remediation.md` §8 row T15, §4's closed registry
and §2's argv/path helpers.

T15 is the row that makes `CONTRACTS.md` §11 real: for **every** registered tool, over a
paired behavior-preserving and semantic-change fixture, the oracle accepts only the former,
and no tool is registered without an oracle. Where an oracle has no in-process parser it
accepts *neither* — which is the fail-closed direction, and the end-to-end tests below prove
that such a tool cannot reach a branch at all.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`. Nothing
here runs a real formatter; the fixtures are literal bytes of what a formatter would emit.
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import test_rqa_remediation_fixtures as fx  # noqa: E402
from rqa.contracts import Location, ProcessResult, RemediationRefused  # noqa: E402
from rqa.contracts import RemediationRefusalReason as REASON  # noqa: E402
from rqa.remediation import MECHANICAL_TOOL_SET, RemediationError, ToolSpec  # noqa: E402
from rqa.remediation.remediate import remediate  # noqa: E402
from rqa.remediation.tools import (  # noqa: E402
    build_argv,
    check_passed,
    semantic_fingerprint,
    validate_remedy_paths,
)

#: §4's table, transcribed from the contract rather than from the implementation.
SECTION_FOUR = {
    "ruff-format": (frozenset({".py", ".pyi"}), ("ruff", "format"), ("ruff", "format", "--check"), "python_ast_v1"),
    "prettier": (
        frozenset({".js", ".jsx", ".ts", ".tsx"}),
        ("prettier", "--write"),
        ("prettier", "--check"),
        "typescript_estree_v1",
    ),
    "gofmt": (frozenset({".go"}), ("gofmt", "-w"), ("gofmt", "-d"), "go_ast_v1"),
    "rustfmt": (frozenset({".rs"}), ("rustfmt",), ("rustfmt", "--check"), "rust_syn_v1"),
    "dart-format": (
        frozenset({".dart"}),
        ("dart", "format"),
        ("dart", "format", "--output=none", "--set-exit-if-changed"),
        "dart_analyzer_v1",
    ),
}

#: `(extension, original, behavior-preserving reformat, semantic change)` per tool.
PAIRS = {
    "ruff-format": (".py", fx.PY_BEFORE, fx.PY_AFTER, fx.PY_ADVERSARIAL),
    "prettier": (
        ".ts",
        b"const a = {x:1,\n  y : 2}\n",
        b"const a = { x: 1, y: 2 };\n",
        b"const a = { x: 1, y: 3 };\n",
    ),
    "gofmt": (
        ".go",
        b"package main\nfunc main( ){\nx:=1\n_ = x\n}\n",
        b"package main\n\nfunc main() {\n\tx := 1\n\t_ = x\n}\n",
        b"package main\n\nfunc main() {\n\tx := 2\n\t_ = x\n}\n",
    ),
    "rustfmt": (
        ".rs",
        b'fn main(){let x=1;println!("{}",x);}\n',
        b'fn main() {\n    let x = 1;\n    println!("{}", x);\n}\n',
        b'fn main() {\n    let x = 2;\n    println!("{}", x);\n}\n',
    ),
    "dart-format": (
        ".dart",
        b"void main(){var x=1;print(x);}\n",
        b"void main() {\n  var x = 1;\n  print(x);\n}\n",
        b"void main() {\n  var x = 2;\n  print(x);\n}\n",
    ),
}


def fingerprint(spec: ToolSpec, extension: str, content: bytes) -> bytes | None:
    return semantic_fingerprint(
        oracle=spec.equivalence_id, path=f"src/subject{extension}", content=content
    )


# -- §4: the registry is exactly the contract's table --------------------------


def test_the_registry_is_exactly_section_fours_five_rows() -> None:
    assert sorted(MECHANICAL_TOOL_SET) == sorted(SECTION_FOUR)
    for tool_id, (extensions, fix_argv, check_argv, oracle) in SECTION_FOUR.items():
        spec = MECHANICAL_TOOL_SET[tool_id]
        assert spec.id == tool_id
        assert spec.extensions == extensions, tool_id
        assert spec.fix_argv == fix_argv, tool_id
        assert spec.check_argv == check_argv, tool_id
        assert spec.equivalence_id == oracle, tool_id
        assert spec.check_id and spec.check_id != tool_id, tool_id
        assert spec.neutrality_contract, tool_id


def test_the_registry_cannot_be_extended_or_rewritten_at_runtime() -> None:
    """§4: policy can remove entries; it can neither add a tool nor weaken an oracle."""
    for mutate in (
        lambda: MECHANICAL_TOOL_SET.__setitem__("black", object()),
        lambda: MECHANICAL_TOOL_SET.pop("ruff-format"),
        lambda: MECHANICAL_TOOL_SET.clear(),
    ):
        try:
            mutate()
        except (TypeError, AttributeError):
            continue
        raise AssertionError("the registry is mutable")


def test_no_registered_tool_sorts_or_fixes_imports() -> None:
    """§4: "Import sorting/fixing is absent." An import move is not formatting."""
    for spec in MECHANICAL_TOOL_SET.values():
        argv = " ".join(spec.fix_argv + spec.check_argv).lower()
        for forbidden in ("isort", "--fix", "organize", "sort-imports", "--select"):
            assert forbidden not in argv, (spec.id, forbidden)


def test_every_spec_names_a_registered_oracle() -> None:
    """"No sound equivalence check means the tool is not in MECHANICAL_TOOL_SET"
    (`CONTRACTS.md` §11): an unknown oracle id would silently fingerprint as `None`, so
    the oracle table and the registry's `equivalence_id` set must be the same set."""
    from rqa.remediation import tools

    assert set(tools._ORACLES) == {spec.equivalence_id for spec in MECHANICAL_TOOL_SET.values()}
    assert semantic_fingerprint(oracle="no_such_oracle_v1", path="a.py", content=b"x=1\n") is None


# -- T15: paired fixtures, every registered tool -------------------------------
#
# Registration is not availability (ruling on E-B3c-2, launchpad-26/buzz#2243: all five
# rows stay registered, and the seam will be amended to distinguish the two). So T15 pins
# *which* rows have an oracle that can run in this process as an explicit per-row
# expectation, and then holds each row to the behaviour its expectation implies. Neither
# half is discovered by asking the oracle and believing the answer — that is what made the
# previous version skip four rows and stay green when the one working oracle was removed
# (G2194-P10-F7).

#: The expectation, per registry row. Only `python_ast_v1` can be computed here: the
#: standard library parses Python and ships no parser for TypeScript, Go, Rust or Dart.
ORACLE_AVAILABLE = {
    "ruff-format": True,
    "prettier": False,
    "gofmt": False,
    "rustfmt": False,
    "dart-format": False,
}


def test_t15_the_availability_expectation_covers_every_registered_row() -> None:
    """The table and the registry cannot drift apart silently."""
    assert sorted(ORACLE_AVAILABLE) == sorted(MECHANICAL_TOOL_SET)
    assert sorted(PAIRS) == sorted(MECHANICAL_TOOL_SET)
    assert any(ORACLE_AVAILABLE.values()), "no row can be exercised at all"


def test_t15_each_rows_oracle_is_the_implementation_its_expectation_names() -> None:
    """Structural, so it holds whatever a fixture happens to parse as.

    A row expected unavailable must be bound to `_unavailable` itself, and a row expected
    available must not be — which catches drift in *both* directions: the working oracle
    being swapped out, and an oracle-less row being quietly wired to something that runs.
    """
    from rqa.remediation import tools

    for tool_id, spec in sorted(MECHANICAL_TOOL_SET.items()):
        implementation = tools._ORACLES[spec.equivalence_id]
        if ORACLE_AVAILABLE[tool_id]:
            assert implementation is not tools._unavailable, (
                f"{tool_id} is expected to have a working oracle, but {spec.equivalence_id} "
                "is the unavailable one"
            )
        else:
            assert implementation is tools._unavailable, (
                f"{tool_id} is expected to have no in-process oracle, but "
                f"{spec.equivalence_id} resolves to {implementation!r}"
            )


def test_t15_every_registered_tool_accepts_only_the_behavior_preserving_pair() -> None:
    """Every row, held to its own expectation — no row is skipped.

    An available row must produce a fingerprint, must call the behaviour-preserving
    reformat equivalent, and must call the semantic change different. An unavailable row
    must produce `None` for all three, which is the fail-closed answer and is why such a
    row can never reach a branch (the test below).
    """
    for tool_id, spec in sorted(MECHANICAL_TOOL_SET.items()):
        extension, before, equivalent, adversarial = PAIRS[tool_id]
        original = fingerprint(spec, extension, before)
        preserved = fingerprint(spec, extension, equivalent)
        changed = fingerprint(spec, extension, adversarial)
        if ORACLE_AVAILABLE[tool_id]:
            assert original is not None, f"{tool_id} produced no fingerprint at all"
            assert original == preserved, f"{tool_id} rejected a behavior-preserving reformat"
            assert original != changed, f"{tool_id} accepted a semantic change"
        else:
            assert (original, preserved, changed) == (None, None, None), (
                f"{tool_id} has no in-process oracle, so it must fingerprint nothing"
            )


def test_t15_a_tool_whose_oracle_is_unavailable_can_never_push() -> None:
    """The registry contains no tool that can reach a branch without a passing oracle."""
    for tool_id, spec in sorted(MECHANICAL_TOOL_SET.items()):
        if ORACLE_AVAILABLE[tool_id]:
            continue
        extension, before, equivalent, _ = PAIRS[tool_id]
        path = f"src/subject{extension}"
        finding = fx.make_finding(
            remedy=fx.make_remedy(tool=tool_id, paths=(path,), check=spec.check_id),
            location=Location(path=path, line=1),
        )
        with fx.sandbox() as state_dir:
            arguments = fx.call(
                finding=finding,
                facts=fx.make_facts(files={path: before}),
                runner=fx.FakeRunner(seed={path: before}, on_fix=fx.writes(equivalent, path=path)),
            )
            result = remediate(state_dir=state_dir, **arguments)
        assert isinstance(result, RemediationRefused), (tool_id, result)
        assert result.reason is REASON.INVALID_PATH, (tool_id, result)
        assert arguments["runner"].ran(spec.fix_argv[0]) == [], tool_id


def test_t15_an_available_row_really_does_reach_the_branch() -> None:
    """The mirror of the test above, so "unavailable refuses" is not vacuously true of
    every row: the one available row pushes over the same paired fixtures."""
    tool_id = "ruff-format"
    assert ORACLE_AVAILABLE[tool_id]
    spec = MECHANICAL_TOOL_SET[tool_id]
    extension, before, equivalent, adversarial = PAIRS[tool_id]
    path = f"src/subject{extension}"
    finding = fx.make_finding(
        remedy=fx.make_remedy(tool=tool_id, paths=(path,), check=spec.check_id),
        location=Location(path=path, line=1),
    )
    for produced, expected in ((equivalent, None), (adversarial, REASON.BEHAVIOUR_CHANGED)):
        with fx.sandbox() as state_dir:
            arguments = fx.call(
                finding=finding,
                facts=fx.make_facts(files={path: before}),
                runner=fx.FakeRunner(seed={path: before}, on_fix=fx.writes(produced, path=path)),
            )
            result = remediate(state_dir=state_dir, **arguments)
        if expected is None:
            assert not isinstance(result, RemediationRefused), result
        else:
            assert isinstance(result, RemediationRefused), result
            assert result.reason is expected, result


# -- the python oracle in detail -----------------------------------------------


def python(content: bytes) -> bytes | None:
    return semantic_fingerprint(oracle="python_ast_v1", path="src/widget.py", content=content)


def test_the_python_oracle_ignores_exactly_what_a_formatter_may_change() -> None:
    baseline = python(b"x = [1, 2]\ny = 'a'\n")
    for equivalent in (
        b"x = [\n    1,\n    2,\n]\ny = 'a'\n",
        b'x = [1, 2]\ny = "a"\n',
        b"x = ((([1, 2])))\ny = 'a'\n",
        b"x = [1, 2]\r\ny = 'a'\r\n",
        b"x = [1, 2,]\ny = 'a'\n",
    ):
        assert python(equivalent) == baseline, equivalent


def test_the_python_oracle_sees_every_change_that_could_matter() -> None:
    baseline = python(b"# note\nx = [1, 2]\n")
    for different in (
        b"# note\nx = [1, 3]\n",  # literal value
        b"# note\nx = [2, 1]\n",  # order
        b"# note\nx = [1, 2.0]\n",  # literal type
        b"# note\nx = [1, True]\n",
        b"x = [1, 2]\n",  # comment dropped
        b"# other\nx = [1, 2]\n",  # comment rewritten
        b"# note\nx = [1, 2]\nimport os\n",  # statement added
        b'"""doc"""\n# note\nx = [1, 2]\n',  # docstring added
    ):
        assert python(different) != baseline, different


def test_the_python_oracle_refuses_rather_than_guessing() -> None:
    for unusable in (b"def (:\n", b"\xff\xfe\x00", b"x = (\n", b"  indented\n"):
        assert python(unusable) is None, unusable


def test_the_python_oracle_is_stable_across_calls_and_paths() -> None:
    assert python(fx.PY_BEFORE) == python(fx.PY_BEFORE)
    assert python(fx.PY_BEFORE) == semantic_fingerprint(
        oracle="python_ast_v1", path="elsewhere/other.py", content=fx.PY_BEFORE
    )


# -- build_argv ------------------------------------------------------------------


def test_build_argv_appends_exactly_the_paths_and_nothing_else() -> None:
    assert build_argv(prefix=("ruff", "format"), paths=("a.py", "b/c.py")) == (
        "ruff",
        "format",
        "a.py",
        "b/c.py",
    )


def test_build_argv_refuses_anything_that_is_not_an_exact_file_path() -> None:
    for paths in (
        ("--force",),
        ("-rf",),
        ("/etc/passwd",),
        ("../escape.py",),
        ("a/../b.py",),
        ("*.py",),
        ("a\x00b.py",),
        ("a\nb.py",),
        (":(glob)a.py",),
        ("",),
        (),
        ("~/secret.py",),
    ):
        try:
            build_argv(prefix=("ruff", "format"), paths=paths)
        except RemediationError:
            continue
        raise AssertionError(f"build_argv accepted {paths!r}")


# -- validate_remedy_paths --------------------------------------------------------


def test_validate_remedy_paths_accepts_the_exact_captured_target() -> None:
    assert validate_remedy_paths(
        remedy=fx.make_remedy(), facts=fx.make_facts(), finding=fx.make_finding()
    )


def test_validate_remedy_paths_requires_the_tools_own_registered_check_and_suffix() -> None:
    facts = fx.make_facts(files={fx.TARGET: fx.PY_BEFORE, "src/widget.rs": b"fn main(){}\n"})
    assert not validate_remedy_paths(
        remedy=fx.make_remedy(check="rustfmt-check"), facts=facts, finding=fx.make_finding()
    )
    assert not validate_remedy_paths(
        remedy=fx.make_remedy(paths=("src/widget.rs",)),
        facts=facts,
        finding=fx.make_finding(location=Location(path="src/widget.rs", line=1)),
    )
    assert not validate_remedy_paths(
        remedy=fx.make_remedy(tool="black"), facts=facts, finding=fx.make_finding()
    )


# -- check_passed ------------------------------------------------------------------


def test_check_passed_reads_the_registered_check_the_way_section_four_registers_it() -> None:
    """`gofmt -d` prints the diff it would apply and still exits zero, so §4 registers the
    check as an *empty* `gofmt -d`; every other row is its exit status."""
    gofmt = MECHANICAL_TOOL_SET["gofmt"]
    ruff = MECHANICAL_TOOL_SET["ruff-format"]
    clean = ProcessResult(returncode=0, stdout=b"", stderr=b"")
    noisy = ProcessResult(returncode=0, stdout=b"--- a.go\n+++ b.go\n", stderr=b"")
    failed = ProcessResult(returncode=1, stdout=b"", stderr=b"")
    assert check_passed(spec=gofmt, result=clean)
    assert not check_passed(spec=gofmt, result=noisy)
    assert not check_passed(spec=gofmt, result=failed)
    assert check_passed(spec=ruff, result=clean)
    assert check_passed(spec=ruff, result=ProcessResult(returncode=0, stdout=b"1 file\n", stderr=b""))
    assert not check_passed(spec=ruff, result=failed)


# -- Round 2: G2194-P10-F5, the source's own declared encoding -------------------
#
# A PEP 263 header changes what the bytes of a string literal *mean*. Under
# `# coding: latin-1` the bytes `C3 A9` are the two characters `Ã©`, while the escape
# `\xe9` is the one character `é` — two different runtime values. An oracle that assumed
# UTF-8 decoded the first as `é` and called the pair equivalent, which would have passed a
# behaviour-changing edit as behaviour-preserving in the one oracle of five that runs.

LATIN1_RAW_BYTES = b"# coding: latin-1\nVALUE = '\xc3\xa9'\n"
LATIN1_ESCAPE = b"# coding: latin-1\nVALUE = '\\xe9'\n"


def test_f5_the_declared_encoding_decides_what_a_literal_means() -> None:
    """The values really do differ under CPython's own rules; the oracle must agree."""
    import ast as ast_module

    raw_value = ast_module.parse(LATIN1_RAW_BYTES).body[0].value.value
    escaped_value = ast_module.parse(LATIN1_ESCAPE).body[0].value.value
    assert raw_value != escaped_value, (raw_value, escaped_value)
    assert raw_value == "Ã©" and escaped_value == "é"
    assert python(LATIN1_RAW_BYTES) is not None
    assert python(LATIN1_RAW_BYTES) != python(LATIN1_ESCAPE)


def test_f5_a_declared_encoding_does_not_break_an_honest_reformat() -> None:
    """Still an oracle, not a refusal machine: whitespace changes under the same header
    remain equivalent."""
    spaced = b"# coding: latin-1\nVALUE   =    '\xc3\xa9'\n"
    assert python(LATIN1_RAW_BYTES) == python(spaced)


def test_f5_an_undeclared_source_is_still_utf_8() -> None:
    assert python(b"VALUE = '\xc3\xa9'\n") is not None
    assert python(b"VALUE = '\xc3\xa9'\n") == python(b"VALUE   =   '\xc3\xa9'\n")


def test_f5_bytes_that_no_declared_encoding_can_decode_are_refused() -> None:
    for unusable in (
        b"# coding: ascii\nVALUE = '\xc3\xa9'\n",
        b"# coding: no-such-encoding-v9\nVALUE = 1\n",
        b"\xff\xfeVALUE = 1\n",
    ):
        assert python(unusable) is None, unusable

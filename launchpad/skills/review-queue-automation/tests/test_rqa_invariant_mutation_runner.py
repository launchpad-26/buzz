"""Focused failure-mode tests for the standalone invariant mutation runner."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
import tempfile


SCRIPT = pathlib.Path(__file__).resolve().parent.parent / "integrity/run_mutations.py"
SPEC = importlib.util.spec_from_file_location("rqa_invariant_mutations", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)


def case(*, before: str = "answer = False", after: str = "answer = True") -> dict:
    return {
        "id": "B-INV-TEST",
        "invariant": "a test invariant",
        "source": {"path": "rqa/example.py", "line": 1},
        "test": "tests/test_example.py::test_guard",
        "expected_assertion": "guard caught mutation",
        "mutation": {
            "path": "rqa/example.py",
            "before": before,
            "after": after,
        },
    }


def test_git_context_is_scrubbed_instead_of_retargeting_the_operator_repository() -> None:
    clean = runner._clean_env(
        {
            "PATH": "/bin",
            "GIT_DIR": "/operator/.git",
            "GIT_WORK_TREE": "/operator",
            "GIT_INDEX_FILE": "/operator/.git/index",
            "GIT_COMMON_DIR": "/operator/.git",
            "GIT_OBJECT_DIRECTORY": "/operator/.git/objects",
            "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/operator/elsewhere",
        }
    )
    assert clean == {"PATH": "/bin"}


def test_stale_or_ambiguous_mutation_anchor_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        target = root / "rqa/example.py"
        target.parent.mkdir()
        target.write_text("answer = False\nanswer = False\n", encoding="utf-8")
        try:
            runner._apply_mutation(root, case())
        except runner.RunnerError as error:
            assert "expected 1 match, found 2" in str(error)
        else:
            raise AssertionError("an ambiguous mutation anchor was accepted")
        assert target.read_text(encoding="utf-8") == "answer = False\nanswer = False\n"


def test_a_mutation_that_breaks_python_syntax_is_an_error() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        target = root / "rqa/example.py"
        target.parent.mkdir()
        target.write_text("answer = False\n", encoding="utf-8")
        try:
            runner._apply_mutation(root, case(after="answer = ("))
        except runner.RunnerError as error:
            assert "does not preserve valid Python" in str(error)
        else:
            raise AssertionError("a syntax-breaking mutation was accepted")
        assert target.read_text(encoding="utf-8") == "answer = False\n"


def test_only_the_expected_invariant_assertion_counts_as_a_kill() -> None:
    examples = [
        (runner.TestResult(0, "1 passed"), "guard caught mutation", "SURVIVED"),
        (runner.TestResult(-1, "", timed_out=True), "guard caught mutation", "ERROR"),
        (runner.TestResult(2, "collection error"), "guard caught mutation", "ERROR"),
        (runner.TestResult(1, "RuntimeError: dependency failed"), "guard caught mutation", "ERROR"),
        (runner.TestResult(1, "AssertionError: another assertion"), "guard caught mutation", "ERROR"),
        (
            runner.TestResult(1, "AssertionError: guard caught mutation"),
            "guard caught mutation",
            "KILLED",
        ),
    ]
    for result, expected, outcome in examples:
        assert runner._classify_mutant(result, expected)[0] == outcome


def test_inventory_rejects_a_test_file_without_an_exact_node() -> None:
    with tempfile.TemporaryDirectory() as directory:
        inventory = {
            "version": 1,
            "cases": [{**case(), "test": "tests/test_example.py"}],
        }
        path = pathlib.Path(directory) / "invariants.json"
        path.write_text(__import__("json").dumps(inventory), encoding="utf-8")
        try:
            runner._load_inventory(path)
        except runner.RunnerError as error:
            assert "exact pytest node id" in str(error)
        else:
            raise AssertionError("an inexact pytest node id was accepted")

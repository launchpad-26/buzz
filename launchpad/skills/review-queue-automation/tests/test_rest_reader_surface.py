#!/usr/bin/env python3
"""Every `RestReader` method its callers use must exist.

WHY THIS IS A WHOLE FILE. `RestReader.changed_files` did not exist while three
modules called it:

  - `evidence.py:47`  evidence-bundle assembly, on the critical path of EVERY
                      review job, so no job could ever complete
  - `history.py:240`  `--with-files` ingest, so every historical sample lost its
                      protected-trigger and file-limit evidence
  - `queue.py:105`    the reconciler (#1962)

#1962 added a guard for `queue.py` only, by parsing that one file. It also
recorded — wrongly — that the method appeared "exactly once in the entire source
tree"; a `grep` whose output was truncated by `__pycache__` noise hid the other
two. A guard scoped to one file, written from a claim about the whole tree, is
how the same defect survived its own fix.

This one is scoped to the tree. It finds every variable assigned a `RestReader`
in every script, collects every attribute used on it, and asserts the real class
provides all of them. Tests use fakes, so a missing method is invisible until it
runs against GitHub — which is exactly when it is most expensive to discover.
"""

from __future__ import annotations

import ast
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "scripts"))

from github_rest import RestReader  # noqa: E402

SCRIPTS = pathlib.Path(__file__).resolve().parent.parent / "scripts"


def _reader_attribute_uses(tree: ast.AST) -> set[str]:
    """Attributes used on any local bound to `RestReader(...)`.

    Also follows the `self.rest = RestReader(...)` shape, and the pattern
    `reader = RestReader(cfg, state)` used throughout these scripts.
    """
    bound: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        value = node.value
        if not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "RestReader"
        ):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                bound.add(target.id)

    used: set[str] = set()
    if not bound:
        return used
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id in bound
        ):
            used.add(node.attr)
    return used
def _rest_reader_surface() -> set[str]:
    """Everything a `RestReader` instance actually exposes.

    `dir()` on the class misses attributes bound in `__init__` — `self.rest` is
    one, and `lease.py` legitimately uses it. A guard that only knew the class
    surface would report that as missing, which is a false alarm about real
    code and exactly the kind of noise that gets a guard deleted.
    """
    surface = set(dir(RestReader))
    source = (SCRIPTS / "github_rest.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if not (isinstance(node, ast.ClassDef) and node.name == "RestReader"):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Assign):
                continue
            for target in inner.targets:
                if (
                    isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "self"
                ):
                    surface.add(target.attr)
    return surface


def test_every_rest_reader_method_used_anywhere_exists() -> None:
    surface = _rest_reader_surface()
    missing: list[str] = []
    checked: list[str] = []
    for path in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        uses = _reader_attribute_uses(tree)
        if not uses:
            continue
        checked.append(path.name)
        for attr in sorted(uses):
            if attr not in surface:
                missing.append(f"{path.name}: RestReader.{attr}")

    assert checked, "no module was found constructing a RestReader; this guard would be vacuous"
    assert not missing, "callers use RestReader methods that do not exist: " + "; ".join(missing)


def test_the_guard_sees_the_modules_that_actually_use_a_reader() -> None:
    """Names the files, so a refactor that hides the usage fails loudly.

    Without this, a change that stopped matching the `RestReader(...)` assignment
    shape would make the guard above silently check nothing.
    """
    seen = set()
    for path in sorted(SCRIPTS.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        if _reader_attribute_uses(tree):
            seen.add(path.name)

    # The three that carried the defect, plus the transport itself.
    for expected in ("evidence.py", "history.py", "lease.py"):
        assert expected in seen, f"{expected} no longer appears to use a RestReader: {sorted(seen)}"


def test_changed_files_specifically_exists_and_is_paginated() -> None:
    """The method whose absence broke every job.

    Pinned by name rather than left to the sweep above, because its absence had
    three distinct consequences and a regression should say which method went.
    """
    assert hasattr(RestReader, "changed_files")
    source = (SCRIPTS / "github_rest.py").read_text(encoding="utf-8")
    body = source.split("def changed_files", 1)[1].split("def ", 1)[0]
    assert "paginate=True" in body, "a truncated file list understates the change"
    assert "/files" in body


if __name__ == "__main__":
    failures = 0
    passed = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                passed += 1
            except Exception as exc:
                failures += 1
                import traceback
                traceback.print_exc()
                print(f"FAIL {name}: {exc}")
    print(f"{passed} passed, {failures} failed")
    sys.exit(1 if failures else 0)

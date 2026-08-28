#!/usr/bin/env python3
"""Run the review-queue-automation test suite without a pytest dependency.

Usage:

    python3 launchpad/skills/review-queue-automation/tests/run_all.py \
            [skill-root]

`skill-root` defaults to the directory containing this file's parent (i.e. the
skill root), so the runner also works when invoked with no arguments.

Discovery rules:

* every ``tests/test_*.py`` file is imported by path with ``importlib``;
* every zero-argument ``test_*`` function *defined in that module* is run;
* a test function that requires an argument (a pytest fixture) is a hard error —
  this suite is deliberately fixture-free so it can run anywhere Python 3 does.

``scripts/`` is placed on ``sys.path`` before importing so tests can
``import shadow`` and friends directly.
"""

from __future__ import annotations

import importlib.util
import inspect
import pathlib
import sys
import traceback


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args:
        root = pathlib.Path(args[0]).resolve()
    else:
        root = pathlib.Path(__file__).resolve().parent.parent

    tests = root / "tests"
    scripts = root / "scripts"
    if not tests.is_dir():
        print(f"no tests directory under {root}")
        return 1
    sys.path.insert(0, str(scripts))

    passed = 0
    failed: list[str] = []
    for path in sorted(tests.glob("test_*.py")):
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for name, function in inspect.getmembers(module, inspect.isfunction):
            if not name.startswith("test_") or function.__module__ != module.__name__:
                continue
            required = [
                parameter
                for parameter in inspect.signature(function).parameters.values()
                if parameter.default is inspect.Parameter.empty
            ]
            if required:
                raise RuntimeError(f"{path.name}:{name} requires pytest fixtures")
            try:
                function()
            except Exception:  # noqa: BLE001 - report every failure, keep going
                failed.append(f"{path.name}:{name}\n{traceback.format_exc()}")
            else:
                passed += 1

    if failed:
        print(f"FAILED: {len(failed)} test(s); passed: {passed}")
        print("\n".join(failed))
        return 1
    print(f"PASSED: {passed} test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

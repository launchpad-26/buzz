#!/usr/bin/env python3
"""Decide which launchpad/skills suites CI runs, and refuse to let one vanish.

WHY THIS EXISTS. Six of the seven skills under `launchpad/skills/` shipped test
suites that no CI job had ever executed (issue #2018). A suite nothing runs is a
claim, not a check. The gap was not theoretical: PR #1954 merged-ready with a
genuinely red test in `evidence-reduce` -- `timeline --tz -07:00` was rejected by
argparse -- while every check on the pull request was green, because no lane ran
the test that was catching it. A human found it by hand.

THREE THINGS THIS MODULE GUARDS, each a way the gap could reopen:

1. A NEW SKILL LANDS UNCOVERED. `check` compares the skills on disk against
   skill_test_floors.json and fails on any skill that appears in neither map.
   Adding a skill therefore forces a deliberate answer to "who runs its tests",
   rather than silence defaulting to nobody.

2. A SUITE SHRINKS TO NOTHING. `assert_floor` counts test CASES, not files.
   It counts cases because a file-counting guard is satisfied by renaming every
   `test_*` function to `check_*`, leaving the files in place and zero cases
   collected -- launchpad-agents-tests.yml records learning that the hard way.
   An empty run and a passing run look identical in a CI summary, which is
   exactly the shape of the gap being closed.

3. AN EXCLUSION BECOMES A LIE. A skill listed in `covered_elsewhere` names the
   workflow that covers it. `check` opens that workflow and fails unless it
   actually mentions the skill's path. Without this, deleting a dedicated
   workflow would silently un-cover a skill while the manifest still claimed
   otherwise.

WHY PYTEST IS THE RUNNER, and this is not a style preference. The suites do not
share a layout. `gh-admin/tests` holds seven pytest-style bare `test_*`
functions and no `unittest.TestCase`; run under `unittest discover` it reports
"Ran 0 tests" and exits 0 -- seven controls silently uncounted, by the very
mechanism guard 2 exists to catch. `software-change-impact-assessment/tests` and
`gh-admin/tests` also lack `__init__.py`, so `unittest discover -t .` cannot
import them at all. pytest collects every layout in the tree, including plain
`unittest.TestCase` classes, so one runner covers all of them honestly.

Standard library only, and it neither reads the network nor shells out to git,
so its own controls run under `env -i`.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
SKILLS_DIR = REPO_ROOT / "launchpad" / "skills"
MANIFEST = pathlib.Path(__file__).resolve().parent / "skill_test_floors.json"

#: pytest's collection summary, e.g. "25 tests collected in 0.03s" or
#: "1 test collected". Anchored on the count so a path containing digits cannot
#: be mistaken for one.
_COLLECTED = re.compile(r"(\d+) tests? collected")

#: An empty suite gets its own phrasing with no digit in it -- pytest prints
#: "no tests collected in 0.03s". Without this it falls through to "no usable
#: summary", which fails for the right reason but names the wrong cause. This is
#: the exact output produced by renaming every `test_*` function to `check_*`,
#: so it is the message a reader is most likely to meet.
_NONE_COLLECTED = re.compile(r"no tests collected")

#: pytest reports import failures as "errors" alongside a collected count, so a
#: partially-broken suite can still print a number. Treated as a hard failure:
#: a module that does not import is not a passing control.
_ERRORS = re.compile(r"(\d+) errors?")


def load_manifest(path=MANIFEST):
    """Return (run_here, covered_elsewhere) from the floors manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["run_here"], data["covered_elsewhere"]


def discover_skills(skills_dir=SKILLS_DIR):
    """Every skill directory that contains a tests/ folder, sorted.

    Discovery is by directory, not by manifest, so the manifest can be checked
    against reality rather than defining it.
    """
    if not skills_dir.is_dir():
        return []
    return sorted(
        entry.name
        for entry in skills_dir.iterdir()
        if entry.is_dir() and (entry / "tests").is_dir()
    )


def coverage_problems(discovered, run_here, covered_elsewhere, repo_root=REPO_ROOT):
    """Every way the manifest and the tree can disagree. Empty means consistent."""
    problems = []
    declared = set(run_here) | set(covered_elsewhere)

    for skill in discovered:
        if skill not in declared:
            problems.append(
                f"{skill} has a tests/ directory but appears in neither "
                f"'run_here' nor 'covered_elsewhere' in {MANIFEST.name}. Add it "
                f"to 'run_here' with a floor equal to its current case count, or "
                f"to 'covered_elsewhere' naming the workflow that runs it."
            )

    for skill in sorted(set(run_here) & set(covered_elsewhere)):
        problems.append(
            f"{skill} is in both 'run_here' and 'covered_elsewhere'. It must be "
            f"in exactly one, or its suite runs twice and a failure reports "
            f"against two different checks."
        )

    for skill in sorted(declared):
        if skill not in discovered:
            problems.append(
                f"{skill} is declared in {MANIFEST.name} but has no "
                f"launchpad/skills/{skill}/tests directory. Remove the entry, or "
                f"restore the suite."
            )

    for skill, floor in sorted(run_here.items()):
        if not isinstance(floor, int) or floor < 1:
            problems.append(
                f"{skill} has floor {floor!r}; a floor must be a positive "
                f"integer. A floor of 0 would pass on an empty suite."
            )

    for skill, workflow in sorted(covered_elsewhere.items()):
        path = repo_root / workflow
        if not path.is_file():
            problems.append(
                f"{skill} claims coverage by {workflow}, which does not exist. "
                f"Either that workflow was deleted -- in which case the skill is "
                f"now uncovered and belongs in 'run_here' -- or the path is wrong."
            )
            continue
        if f"launchpad/skills/{skill}" not in path.read_text(encoding="utf-8"):
            problems.append(
                f"{skill} claims coverage by {workflow}, but that workflow never "
                f"mentions launchpad/skills/{skill}. The exclusion is not true."
            )

    return problems


def parse_collected(output):
    """Cases pytest collected, or None when it reported no usable summary."""
    if _ERRORS.search(output):
        return None
    matches = _COLLECTED.findall(output)
    if matches:
        return int(matches[-1])
    if _NONE_COLLECTED.search(output):
        return 0
    return None


def cmd_check(args):
    run_here, covered_elsewhere = load_manifest()
    problems = coverage_problems(discover_skills(), run_here, covered_elsewhere)
    for problem in problems:
        print(f"::error::{problem}")
    if problems:
        return 1
    total = len(run_here) + len(covered_elsewhere)
    print(f"skill test coverage is consistent: {total} skill(s) accounted for")
    return 0


def cmd_matrix(args):
    run_here, _ = load_manifest()
    entries = [
        {"skill": skill, "floor": floor} for skill, floor in sorted(run_here.items())
    ]
    print(json.dumps(entries))
    return 0


def cmd_assert_floor(args):
    run_here, _ = load_manifest()
    if args.skill not in run_here:
        print(f"::error::{args.skill} is not in 'run_here'; nothing to assert")
        return 1
    floor = run_here[args.skill]
    output = sys.stdin.read()
    count = parse_collected(output)
    if count is None:
        print(
            f"::error::pytest reported no usable collection summary for "
            f"{args.skill} -- a module failed to import, or collection did not "
            f"run. Not treating that as a pass."
        )
        return 1
    print(f"{args.skill}: discovered {count} test case(s), floor {floor}")
    if count < floor:
        print(
            f"::error::{args.skill} collected {count} test case(s) but its floor "
            f"is {floor}. This job would otherwise have reported success on a "
            f"suite that stopped covering the skill. Restore the tests; do not "
            f"lower the floor."
        )
        return 1
    return 0


def build_parser():
    parser = argparse.ArgumentParser(
        prog="skill_test_matrix.py",
        description="Coverage guard and CI matrix for launchpad/skills test suites.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser(
        "check", help="fail if any skill's suite is covered by nobody"
    ).set_defaults(func=cmd_check)

    sub.add_parser(
        "matrix", help="emit the GitHub Actions matrix as JSON"
    ).set_defaults(func=cmd_matrix)

    floor = sub.add_parser(
        "assert-floor",
        help="read pytest --collect-only output on stdin and enforce the floor",
    )
    floor.add_argument("--skill", required=True)
    floor.set_defaults(func=cmd_assert_floor)

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

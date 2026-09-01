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


#: A workflow must invoke a test runner before it can be claimed as coverage.
_TEST_COMMAND = re.compile(r"\b(pytest|unittest)\b")


def load_manifest(path=MANIFEST):
    """Return (run_here, covered_elsewhere) from the floors manifest."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["run_here"], data["covered_elsewhere"]


def load_floor_drops(path=MANIFEST):
    """Declared, reasoned exceptions to the no-lowering rule. Usually empty."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("floor_drops", {})


def trigger_paths(text):
    """Every entry under a `paths:` key, without importing a YAML parser.

    PyYAML is not guaranteed on the runner that executes this module -- the
    `scripts` job in launchpad-pr-check.yml uses the system python with no
    pip install -- so the block is read structurally rather than parsed.
    `paths-ignore` is deliberately not collected: it is the opposite claim.
    """
    found = []
    in_block = False
    block_indent = 0
    for raw in text.splitlines():
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        if in_block:
            if stripped.startswith("- ") and indent > block_indent:
                found.append(stripped[2:].strip().strip("\"'"))
                continue
            in_block = False
        if stripped in ("paths:", "paths-ignore:"):
            in_block = stripped == "paths:"
            block_indent = indent
    return found


def exclusion_problems(skill, workflow, repo_root=REPO_ROOT):
    """Why `covered_elsewhere: {skill: workflow}` is not a believable claim.

    An earlier version opened the named file and searched the whole text for
    the skill's path. A cross-model review showed that accepts anything --
    `{"alpha": "not-a-workflow.txt"}` passed with that file containing only
    the comment `# launchpad/skills/alpha`. Reproduced, then narrowed to the
    three properties that make the claim mean something.

    What this still does NOT prove: that the named workflow's test step really
    executes that skill's suite. It proves the file is a workflow, that a
    change to the skill triggers it, and that it invokes a test runner. Stated
    rather than glossed, because the gap is real.
    """
    problems = []
    prefix = f"launchpad/skills/{skill}"

    if not workflow.startswith(".github/workflows/"):
        problems.append(
            f"{skill} claims coverage by {workflow}, which is not under "
            f".github/workflows/. Only a workflow can run a suite."
        )
        return problems
    if not workflow.endswith((".yml", ".yaml")):
        problems.append(
            f"{skill} claims coverage by {workflow}, which is not a .yml or "
            f".yaml file."
        )
        return problems

    path = repo_root / workflow
    if not path.is_file():
        problems.append(
            f"{skill} claims coverage by {workflow}, which does not exist. "
            f"Either that workflow was deleted -- in which case the skill is "
            f"now uncovered and belongs in 'run_here' -- or the path is wrong."
        )
        return problems

    text = path.read_text(encoding="utf-8", errors="replace")
    if not any(p.startswith(prefix) for p in trigger_paths(text)):
        problems.append(
            f"{skill} claims coverage by {workflow}, but that workflow has no "
            f"trigger path under {prefix}. A change to this skill would not "
            f"start it, so it does not cover the skill."
        )
    if not _TEST_COMMAND.search(text):
        problems.append(
            f"{skill} claims coverage by {workflow}, but that workflow invokes "
            f"no test runner. Coverage means running the suite."
        )
    return problems


def floor_drop_problems(base_run_here, run_here, floor_drops=None):
    """Floors may rise or hold. Lowering one must be declared, with a reason.

    Until a cross-model review pointed it out, the ONLY thing preventing a
    lowered floor was the sentence "do not lower the floor" in an error
    message. So a change could delete 89 of evidence-reduce's 90 cases, set
    its floor to 1, and every check would pass -- precisely the shrinkage the
    floors exist to catch. Prose is not a ratchet; this is.
    """
    drops = floor_drops or {}
    problems = []

    for skill, base_floor in sorted(base_run_here.items()):
        if skill not in run_here:
            continue  # a removed skill is coverage_problems' business
        new_floor = run_here[skill]
        if isinstance(new_floor, bool) or not isinstance(new_floor, int):
            continue  # a malformed floor is coverage_problems' business
        if not isinstance(base_floor, int) or isinstance(base_floor, bool):
            continue
        if new_floor < base_floor and not drops.get(skill):
            problems.append(
                f"{skill}'s floor drops from {base_floor} to {new_floor}. A "
                f"floor may rise or hold, never fall on its own -- that is what "
                f"makes it a ratchet. If tests were deliberately removed, add "
                f'"{skill}": "<why>" to \'floor_drops\' in {MANIFEST.name} so '
                f"the reason is visible in this diff."
            )

    for skill, reason in sorted(drops.items()):
        base_floor = base_run_here.get(skill)
        new_floor = run_here.get(skill)
        falling = (
            isinstance(base_floor, int)
            and isinstance(new_floor, int)
            and new_floor < base_floor
        )
        if not falling:
            problems.append(
                f"'floor_drops' still holds an entry for {skill} ({reason!r}) "
                f"but its floor is not falling in this change. Remove it -- a "
                f"stale exemption silently permits the next real drop."
            )

    return problems


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

    if not run_here:
        problems.append(
            "'run_here' is empty, so this lane would build a matrix with no legs "
            "and run no suite at all. If every skill really is covered elsewhere, "
            "delete this workflow rather than leaving one that reports success "
            "for running nothing."
        )

    for skill, floor in sorted(run_here.items()):
        # `bool` subclasses `int`, so a JSON `true` would otherwise survive as
        # floor 1 and let a 90-test suite shrink to one case unnoticed. The same
        # trap is guarded in pr_body_check.py's closing-ref parser.
        if isinstance(floor, bool) or not isinstance(floor, int) or floor < 1:
            problems.append(
                f"{skill} has floor {floor!r}; a floor must be a positive "
                f"integer. A floor of 0 would pass on an empty suite."
            )

    for skill, workflow in sorted(covered_elsewhere.items()):
        problems.extend(exclusion_problems(skill, workflow, repo_root))

    return problems


def summary_line(output):
    """pytest's last non-empty line, which is always its collection summary.

    Verified against pytest 8.3.4 for all three outcomes:
        healthy   "3 tests collected in 0.00s"
        error     "3 tests collected, 1 error in 0.07s"
        empty     "no tests collected in 0.00s"

    ONLY THIS LINE IS PARSED, and that is the whole point. `-q --collect-only`
    prints one node id per collected test above the summary, and a node id can
    contain arbitrary text from a parametrize id -- pytest renders
    `@pytest.mark.parametrize("msg", ["1 error"])` as the literal line
    `tests/test_probe.py::test_reports[1 error]`, spaces intact. Scanning the
    whole output therefore let one parametrized test id in a perfectly healthy
    suite match the error pattern and fail the build red. Reproduced end to end
    before this was narrowed.
    """
    for line in reversed(output.splitlines()):
        if line.strip():
            return line
    return ""


def parse_collected(output):
    """Cases pytest collected, or None when it reported no usable summary."""
    summary = summary_line(output)
    if _ERRORS.search(summary):
        return None
    match = _COLLECTED.search(summary)
    if match:
        return int(match.group(1))
    if _NONE_COLLECTED.search(summary):
        return 0
    return None


def cmd_check(args):
    run_here, covered_elsewhere = load_manifest()
    problems = coverage_problems(discover_skills(), run_here, covered_elsewhere)

    base = getattr(args, "base_manifest", None)
    if base:
        base_path = pathlib.Path(base)
        if not base_path.is_file():
            print(
                f"::error::--base-manifest {base} does not exist. Without the "
                f"base manifest the no-lowering rule cannot be checked, and a "
                f"silently skipped ratchet is worse than none."
            )
            return 1
        base_run_here, _ = load_manifest(base_path)
        problems.extend(
            floor_drop_problems(base_run_here, run_here, load_floor_drops())
        )
    else:
        print(
            "note: no --base-manifest given, so the no-lowering rule was not "
            "checked. That is expected on a push to the trunk, where there is "
            "no base to compare against."
        )

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

    check = sub.add_parser(
        "check", help="fail if any skill's suite is covered by nobody"
    )
    check.add_argument(
        "--base-manifest",
        help="the base branch's copy of the manifest; enables the no-lowering "
        "rule, which cannot be checked without something to compare against",
    )
    check.set_defaults(func=cmd_check)

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

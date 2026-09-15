#!/usr/bin/env python3
"""Guard for ``CUTOVER.md``, the legacy-estate-to-replacing-part map (#2212).

This file is discovered and run by ``tests/run_all.py`` automatically: any
``tests/test_*.py`` is imported and every zero-argument ``test_*`` function it
defines is run (see ``run_all.py``'s own module docstring). No edit to
``run_all.py`` was needed or made.

Three independent failure conditions, matching #2212's issue text exactly:

1. a file present under ``scripts/`` or ``tests/`` (excluding the new estate —
   ``test_rqa_*.py`` and ``lifecycle_cascade_bench.py``, both a stable naming
   convention this run enforced everywhere, not a pinned list of legacy
   filenames) has no row in ``CUTOVER.md``'s map table;
2. a row's ``replacement`` cell names something that does not resolve — a
   dotted ``rqa.*`` path with no matching file under ``rqa/``, or a
   ``tests/test_rqa_*.py`` path that is absent;
3. a row's ``status`` disagrees with the filesystem in either direction, or two
   rows for the same file disagree with each other on ``status``.

Condition 1's file-present set is read from the filesystem with ``os.listdir``
at run time on every invocation — never a hard-coded enumeration of the 118
legacy files this map happens to name today. Condition 2 resolves a dotted
``rqa.*`` path to a file path under ``rqa/`` and checks it exists on disk;
it never imports ``rqa.*`` (an import would couple this guard to import-time
behaviour and make it a census of what is importable *today*, exactly the
fixture shape this run's own lessons forbid a guard from resting on).

Document rows outside the map's deletion authority (the ten root/docs/schema
files in ``CUTOVER.md`` §6 — ``SKILL.md``, ``OPERATORS.md``,
``onboarding/SKILL.md``, ``config.example.json``, every ``references/*.md``
file and both ``schemas/*.json`` files) are exempt from condition 2's
replacement-format check: their ``replacement`` cell deliberately carries a
non-authorization caveat rather than a bare dotted path or test path, and
`CUTOVER.md` §6 is explicit that this map never authorises their deletion.
They are not exempt from condition 1 (they are outside its scope by
directory, since condition 1 only walks ``scripts/`` and ``tests/``) or
condition 3 (their ``status`` still has to agree with the filesystem).
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent          # .../tests
SKILL = HERE.parent                                       # .../review-queue-automation
CUTOVER_PATH = SKILL / "CUTOVER.md"

# The stable naming convention this whole run enforced for its own new estate,
# established in every landed lane's own touched-file list: every new test
# module is named ``test_rqa_*.py``, and the one pre-existing exception
# (``lifecycle_cascade_bench.py``, added by the P-02 lifecycle lane, commit
# ``028ef9211`` — see CUTOVER.md §1) is named and reasoned about there, not
# invented here. This guard's own file is a second, self-evident exception —
# it is new estate this lane (#2212) added, derived from ``__file__`` rather
# than a second hard-coded name. None of the three is a census of legacy
# files: all describe what is NOT legacy, so the legacy set condition 1
# checks is still derived from the filesystem at run time.
NEW_ESTATE_TEST_PREFIX = "test_rqa_"
NEW_ESTATE_TEST_FILES = {"lifecycle_cascade_bench.py", pathlib.Path(__file__).name}

TABLE_HEADER = "| file | part | lane (issue #) | unit(s) | disposition | replacement | status |"


def _read_cutover_text() -> str:
    return CUTOVER_PATH.read_text(encoding="utf-8")


def parse_map_rows(text: str) -> list[dict[str, str]]:
    """Parse the one map table in ``CUTOVER.md`` (identified by its exact
    seven-column header, which disambiguates it from the document's other
    tables — the §3 fifteen-table quote, the §7.1 omissions table and the
    §9 unit table all have different header cells or column counts)."""
    lines = text.splitlines()
    start = None
    for i, line in enumerate(lines):
        if line.strip() == TABLE_HEADER:
            start = i
            break
    if start is None:
        raise AssertionError("CUTOVER.md: map table header not found")

    rows: list[dict[str, str]] = []
    # lines[start] is the header, lines[start + 1] is the "|---|---|...|" rule.
    i = start + 2
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            break
        cells = [c.strip() for c in stripped[1:-1].split("|")]
        if len(cells) != 7:
            raise AssertionError(f"CUTOVER.md line {i + 1}: expected 7 cells, got {len(cells)}: {line!r}")
        file_, part, lane, units, disposition, replacement, status = cells
        file_ = file_.strip("`")
        rows.append(
            {
                "file": file_,
                "part": part,
                "lane": lane,
                "units": units,
                "disposition": disposition,
                "replacement": replacement,
                "status": status,
            }
        )
        i += 1
    return rows


def _is_new_estate_test(name: str) -> bool:
    return name.startswith(NEW_ESTATE_TEST_PREFIX) or name in NEW_ESTATE_TEST_FILES


def legacy_files_on_disk() -> set[str]:
    """Every file under ``scripts/`` or ``tests/`` this map is responsible
    for, read fresh from the filesystem — never a stored list."""
    files: set[str] = set()
    scripts_dir = SKILL / "scripts"
    tests_dir = SKILL / "tests"
    for name in sorted(entry.name for entry in scripts_dir.iterdir() if entry.is_file()):
        files.add(f"scripts/{name}")
    for name in sorted(entry.name for entry in tests_dir.iterdir() if entry.is_file()):
        if _is_new_estate_test(name):
            continue
        files.add(f"tests/{name}")
    return files


def _resolve_rqa_dotted(dotted: str) -> bool:
    rel = dotted.strip().replace(".", "/")
    return (SKILL / f"{rel}.py").is_file() or (SKILL / rel / "__init__.py").is_file()


def _resolve_test_rqa_path(path: str) -> bool:
    return (SKILL / path.strip()).is_file()


DOC_SCHEMA_FILES = {
    "SKILL.md",
    "OPERATORS.md",
    "config.example.json",
    "onboarding/SKILL.md",
    "references/classification.md",
    "references/contracts.md",
    "references/model-fallbacks.md",
    "references/runtime-ops.md",
    "schemas/author-triage.json",
    "schemas/reviewer-verdict.json",
}


def _is_scripts_or_tests(file_: str) -> bool:
    return file_.startswith("scripts/") or file_.startswith("tests/")


def check_every_legacy_file_has_a_row() -> list[str]:
    rows = parse_map_rows(_read_cutover_text())
    mapped = {r["file"] for r in rows if _is_scripts_or_tests(r["file"])}
    required = legacy_files_on_disk()
    missing = sorted(required - mapped)
    return [f"no CUTOVER.md row for {f}" for f in missing]


def check_every_replacement_resolves() -> list[str]:
    """Parses ``replacement`` as ``;``-separated clauses (a mixed row — part of
    the file's responsibility migrated, part did not — states each half as its
    own clause, e.g. ``scripts/logging_otel.py``'s: ``rqa.record.trace (...);
    none (binned: U-DISPATCH-19 ...)``); a single-clause cell with no ``;`` is
    the common case and behaves exactly as before. Within a clause that is not
    a ``none (binned: ...)`` declaration, a further ``,``-separated list of
    real paths is still supported (unchanged from round 1)."""
    rows = parse_map_rows(_read_cutover_text())
    problems: list[str] = []
    for r in rows:
        if r["file"] in DOC_SCHEMA_FILES:
            continue  # exempt: §6's non-authorization caveat is not this format
        if not _is_scripts_or_tests(r["file"]):
            continue
        repl = r["replacement"]
        for clause in repl.split(";"):
            clause = clause.strip()
            if not clause:
                problems.append(f"{r['file']} ({r['part']}, {r['lane']}): empty replacement clause")
                continue
            if clause.startswith("none (binned:"):
                continue
            for part in clause.split(","):
                part = part.strip()
                if not part:
                    problems.append(f"{r['file']} ({r['part']}, {r['lane']}): empty replacement segment")
                    continue
                if part.startswith("rqa."):
                    # a bare dotted path may carry a trailing "(U-XXX-NN)" annotation
                    dotted = part.split("(", 1)[0].strip()
                    if not _resolve_rqa_dotted(dotted):
                        problems.append(f"{r['file']} ({r['part']}, {r['lane']}): {dotted!r} does not resolve under rqa/")
                elif part.startswith("tests/"):
                    path = part.split("(", 1)[0].strip()
                    if not _resolve_test_rqa_path(path):
                        problems.append(f"{r['file']} ({r['part']}, {r['lane']}): {path!r} is absent")
                else:
                    problems.append(f"{r['file']} ({r['part']}, {r['lane']}): unrecognised replacement format {part!r}")
    return problems


def check_status_matches_filesystem_and_is_self_consistent() -> list[str]:
    """``status`` is one of ``present`` | ``deleted`` | ``retained``. A
    ``deleted`` row's file must genuinely be absent; a ``present`` or
    ``retained`` row's file must genuinely exist (the two differ in what wave 2
    may do with it, not in whether it is on disk today — see CUTOVER.md §0)."""
    rows = parse_map_rows(_read_cutover_text())
    problems: list[str] = []
    by_file: dict[str, list[str]] = {}
    for r in rows:
        by_file.setdefault(r["file"], []).append(r["status"])

    for file_, statuses in by_file.items():
        if any(s not in ("present", "deleted", "retained") for s in statuses):
            problems.append(f"{file_}: status must be 'present', 'deleted' or 'retained', got {sorted(set(statuses))}")
            continue
        if len(set(statuses)) != 1:
            problems.append(f"{file_}: rows disagree on status: {statuses}")
            continue
        claimed = statuses[0]
        on_disk = (SKILL / file_).is_file()
        if claimed == "deleted":
            if on_disk:
                problems.append(f"{file_}: row says status='deleted' but the file is actually present")
        else:  # 'present' or 'retained' both assert the file exists
            if not on_disk:
                problems.append(f"{file_}: row says status={claimed!r} but the file is actually deleted")
    return problems


def check_doc_schema_status_is_always_present() -> list[str]:
    """The fourth condition (ruling E-B6-1, round 2 addendum): every
    ``DOC_SCHEMA_FILES`` row must say ``status: present`` — checked against the
    row text alone, never against the filesystem. This is deliberately
    independent of ``check_status_matches_filesystem_and_is_self_consistent``:
    that check would happily accept a doc/schema file that was genuinely
    deleted with its row honestly flipped to 'deleted' in the same commit —
    exactly the mutation a review seat used to show the guard could be
    defeated silently. A doc/schema row can never legitimately claim anything
    but 'present', full stop, regardless of what is on disk; if one ever does,
    this fails independently of whatever check 3 says."""
    rows = parse_map_rows(_read_cutover_text())
    problems: list[str] = []
    for r in rows:
        if r["file"] in DOC_SCHEMA_FILES and r["status"] != "present":
            problems.append(f"{r['file']}: doc/schema row must say status='present', got {r['status']!r}")
    return problems


CHECKS = (
    ("condition 1 (every legacy file has a row)", check_every_legacy_file_has_a_row),
    ("condition 2 (every replacement resolves)", check_every_replacement_resolves),
    ("condition 3 (status matches the filesystem, and rows agree)", check_status_matches_filesystem_and_is_self_consistent),
    ("condition 4 (every doc/schema row says status=present, unconditionally)", check_doc_schema_status_is_always_present),
)


# --------------------------------------------------------------------------- #
# tests/run_all.py + pytest discovery: zero-argument test_* functions only.
# --------------------------------------------------------------------------- #

def test_cutover_map_parses_and_is_non_empty() -> None:
    rows = parse_map_rows(_read_cutover_text())
    assert len(rows) > 100, f"expected the full map, got {len(rows)} rows"


def test_no_row_says_unknown() -> None:
    text = _read_cutover_text()
    rows = parse_map_rows(text)
    for r in rows:
        for key, value in r.items():
            assert "unknown" not in value.lower(), f"{r['file']} ({key}): 'unknown' is forbidden — {value!r}"


def test_every_legacy_file_has_a_row() -> None:
    problems = check_every_legacy_file_has_a_row()
    assert not problems, "\n".join(problems)


def test_every_replacement_resolves() -> None:
    problems = check_every_replacement_resolves()
    assert not problems, "\n".join(problems)


def test_status_matches_filesystem_and_is_self_consistent() -> None:
    problems = check_status_matches_filesystem_and_is_self_consistent()
    assert not problems, "\n".join(problems)


def test_doc_schema_status_is_always_present() -> None:
    problems = check_doc_schema_status_is_always_present()
    assert not problems, "\n".join(problems)


def test_no_mapped_and_migrated_module_is_still_present() -> None:
    """A row whose disposition is migrated/rewritten/retired (i.e. wave 2 is
    licensed to delete it) but whose status still says present is exactly
    right *today* (wave 2 has not run yet — see CUTOVER.md's own out-of-scope
    line). This test instead pins the inverse defect the issue actually names:
    once a row's status flips to 'deleted', the underlying file must really be
    gone, and every row for that file must agree — already covered by
    ``check_status_matches_filesystem_and_is_self_consistent``, exercised here
    under its own name so the issue's own words ("a mapped-and-migrated module
    is still present") map onto a named, independently-run test."""
    rows = parse_map_rows(_read_cutover_text())
    problems = []
    for r in rows:
        if r["status"] != "deleted":
            continue
        if not _is_scripts_or_tests(r["file"]):
            continue
        if (SKILL / r["file"]).is_file():
            problems.append(f"{r['file']}: disposition={r['disposition']} status=deleted but the file is still present")
    assert not problems, "\n".join(problems)


# --------------------------------------------------------------------------- #
# standalone script entry point — "a guard script", per the issue's own words.
# --------------------------------------------------------------------------- #

def main() -> int:
    failed = False
    for label, fn in CHECKS:
        problems = fn()
        if problems:
            failed = True
            print(f"FAIL — {label}: {len(problems)} issue(s)")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"PASS — {label}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Guard for ``CUTOVER.md``, the legacy-estate-to-replacing-part map (#2212).

This file is discovered and run by ``tests/run_all.py`` automatically: any
``tests/test_*.py`` is imported and every zero-argument ``test_*`` function it
defines is run (see ``run_all.py``'s own module docstring). No edit to
``run_all.py`` was needed or made.

Six independent failure conditions. The first three match #2212's issue text
exactly; conditions 4-6 close bypasses that review found in them:

1. a file present under ``scripts/`` or ``tests/`` (excluding the new estate —
   ``test_rqa_*.py`` and ``lifecycle_cascade_bench.py``, both a stable naming
   convention this run enforced everywhere, not a pinned list of legacy
   filenames) has no row in ``CUTOVER.md``'s map table;
2. a row's ``replacement`` cell names something that does not resolve — a
   dotted ``rqa.*`` path with no matching file under ``rqa/``, or a
   ``tests/test_rqa_*.py`` path that is absent;
3. a row's ``status`` disagrees with the filesystem in either direction, or two
   rows for the same file disagree with each other on ``status``;
4. a doc/schema row says anything but ``status: present``, checked against the
   row text alone rather than against the filesystem;
5. a file the map never authorises the deletion of has no row at all — the
   bypass conditions 1-4 share, since each of them compares a row that exists
   against a file that exists, and deleting both halves in one edit leaves
   nothing to be inconsistent with;
6. a bare ``rqa.*`` replacement citation resolves on disk but no collected test
   module imports it — the unenforced half of this map's own deletion rule,
   which is that a file may go only once its replacement is named *and
   exercised*.

Condition 1's file-present set is read from the filesystem with ``os.listdir``
at run time on every invocation — never a hard-coded enumeration of the 118
legacy files this map happens to name today. Condition 2 resolves a dotted
``rqa.*`` path to a file path under ``rqa/`` and checks it exists on disk;
it never imports ``rqa.*`` (an import would couple this guard to import-time
behaviour and make it a census of what is importable *today*, exactly the
fixture shape this run's own lessons forbid a guard from resting on).

Document rows outside the map's deletion authority are exempt from condition
2's replacement-format check. That set is ``DOC_SCHEMA_FILES`` below, and it
is an enumeration rather than a rule: an earlier draft of this docstring said
"every ``references/*.md`` file", which was not true of the literal beside it —
``references/architecture.md`` was in neither, so a maintainer reading this
paragraph believed a file was protected while nothing protected it. The
literal is the only claim this guard can keep, so the prose now points at it
instead of restating it.

Those rows' ``replacement`` cell deliberately carries a non-authorization
caveat rather than a bare dotted path or test path, and `CUTOVER.md` §6 is
explicit that this map never authorises their deletion.
They are not exempt from condition 1 (they are outside its scope by
directory, since condition 1 only walks ``scripts/`` and ``tests/``) or
condition 3 (their ``status`` still has to agree with the filesystem).
"""

from __future__ import annotations

import ast
import fnmatch
import pathlib
import re
import sys
import tempfile

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


#: A §2 map row: a table line whose first cell is a backticked path. Used by the
#: count assertion below, which walks §2's raw lines rather than the parsed rows
#: so that it is measuring the table a reader sees.
ROW_RE = re.compile(r"^\| `([^`]+)` \|")


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
    "references/architecture.md",
    "references/classification.md",
    "references/contracts.md",
    "references/model-fallbacks.md",
    "references/runtime-ops.md",
    "schemas/author-triage.json",
    "schemas/reviewer-verdict.json",
}

# Files this map must carry a row for *unconditionally*, and the exact status
# that row must claim — a row-identity *and* row-content baseline, deliberately
# a literal rather than anything derived from ``CUTOVER.md`` or the filesystem.
#
# Conditions 1-3 all quantify over rows that exist in ``CUTOVER.md`` today, or
# over files that exist on disk today. None of them asserts that a row was ever
# there, so deleting a file *and its own row in the same edit* left nothing for
# them to be inconsistent with: condition 1 only walks files still on disk and
# condition 3 only reads rows still in the table.
#
# Requiring the row to *exist* was not enough either, and that is the round-2
# lesson this literal now carries. A row bearing the right name satisfied
# "has a row at all" whatever it said, so the file could still go in one edit
# by flipping its own row from ``retained`` to ``deleted`` — and condition 3
# then actively helped, because once the file is gone it *requires* the flipped
# row. The status a never-deletable file's row may claim is therefore fixed
# here, checked against the row text alone.
#
# The set is every file the map is explicitly forbidden from authorising the
# deletion of: the eleven root/docs/schema files of CUTOVER.md §6;
# ``scripts/logging_otel.py``, which §7.3 keeps as the reference implementation
# for #2273's unmigrated U-DISPATCH-19 half; and the two files that run the
# suite itself. Those last two were `present` rows outside the baseline, which
# meant the runner and its conftest could be deleted with their rows and leave
# all six conditions green — the same shape as the ``logging_otel.py`` bypass,
# one step further out, found by asking which *other* rows claim a file is on
# disk. Membership is anchored on that non-authorisation, not on the word
# "retained" appearing in a ``status`` cell: a row that has been deleted has no
# ``status`` cell to read, which is precisely the defect.
ALWAYS_MAPPED_STATUS: dict[str, str] = {
    **{f: "present" for f in DOC_SCHEMA_FILES},
    "scripts/logging_otel.py": "retained",
    "tests/conftest.py": "present",
    "tests/run_all.py": "present",
}

ALWAYS_MAPPED_FILES = frozenset(ALWAYS_MAPPED_STATUS)


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


def check_always_mapped_status_is_exact(rows: list[dict] | None = None) -> list[str]:
    """The fourth condition: every row for a file in ``ALWAYS_MAPPED_STATUS``
    must claim exactly the status recorded there — checked against the row text
    alone, never against the filesystem.

    This is deliberately independent of
    ``check_status_matches_filesystem_and_is_self_consistent``: that check would
    happily accept a never-deletable file that was genuinely deleted with its
    row honestly flipped to 'deleted' in the same commit, because once the file
    is gone it *requires* exactly that flip. A doc/schema row can never
    legitimately claim anything but 'present', ``scripts/logging_otel.py``'s can
    never claim anything but 'retained', and if one ever does, this fails
    independently of whatever condition 3 says.

    ``rows`` is injectable so the negative cases below can be stated against a
    synthetic map rather than by mutating the repository.
    """
    rows = parse_map_rows(_read_cutover_text()) if rows is None else rows
    problems: list[str] = []
    for r in rows:
        required = ALWAYS_MAPPED_STATUS.get(r["file"])
        if required is not None and r["status"] != required:
            problems.append(
                f"{r['file']}: this row must say status={required!r}, got "
                f"{r['status']!r} — CUTOVER.md never authorises deleting this file"
            )
    return problems


COLLECTED_TEST_GLOB = "test_rqa_*.py"

# The four bare ``rqa.*`` citations that no collected test module imports
# directly today, each exercised one hop away through the module named beside
# it. They are listed here, by name, so that the exemption is visible to a
# reader of the guard rather than implied by a laxer rule: condition 6 below
# would otherwise have to accept *every* transitively-reachable module, which
# is nearly the whole package and closes nothing.
#
# Condition 6 keeps this set honest in two directions. An entry still has to be
# reachable at one hop from a directly-imported module, so the set cannot hide
# a citation that nothing exercises at all; and because it is a literal, it
# cannot grow silently -- a new unexercised citation fails until someone adds
# it here in a reviewable diff.
INDIRECTLY_EXERCISED = {
    "rqa.github.reads": "rqa.github.types",
    "rqa.judgement.evidence": "rqa.judgement.judge",
    "rqa.judgement.findings": "rqa.judgement.judge",
    "rqa.policy.schema": "rqa.policy.validate",
}


def _module_source(dotted: str) -> pathlib.Path | None:
    rel = dotted.strip().replace(".", "/")
    for candidate in (SKILL / f"{rel}.py", SKILL / rel / "__init__.py"):
        if candidate.is_file():
            return candidate
    return None


def _rqa_imports_in(path: pathlib.Path) -> set[str]:
    """Every ``rqa.*`` module a source file imports at any point in its body.

    Parsed with ``ast`` rather than executed: this guard must not import the
    test estate it is reasoning about. Both spellings the estate actually uses
    are recognised -- ``import rqa.x.y`` / ``from rqa.x import y`` statements,
    and ``importlib.import_module("rqa.x.y")`` with a literal argument, which
    is how ``test_rqa_intake_tick.py`` reaches ``rqa.intake.tick``.
    """
    found: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "rqa" or alias.name.startswith("rqa."):
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level == 0 and node.module and (node.module == "rqa" or node.module.startswith("rqa.")):
                found.add(node.module)
                for alias in node.names:
                    found.add(f"{node.module}.{alias.name}")
        elif isinstance(node, ast.Call):
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr == "import_module"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and node.args[0].value.startswith("rqa.")
            ):
                found.add(node.args[0].value)
    return found


def directly_exercised_modules() -> set[str]:
    """Every ``rqa.*`` module imported by a test module ``run_all.py`` collects.

    Read from the filesystem at run time, exactly as condition 1 reads the
    legacy set -- never a stored list. A module in this set is loaded whenever
    the suite runs, because ``run_all.py`` imports every one of these files.
    """
    exercised: set[str] = set()
    for path in sorted((SKILL / "tests").glob(COLLECTED_TEST_GLOB)):
        exercised |= _rqa_imports_in(path)
    return exercised


def cited_rqa_modules() -> set[str]:
    """Every bare dotted ``rqa.*`` path the map names as a replacement."""
    rows = parse_map_rows(_read_cutover_text())
    cited: set[str] = set()
    for r in rows:
        if r["file"] in DOC_SCHEMA_FILES or not _is_scripts_or_tests(r["file"]):
            continue
        for clause in r["replacement"].split(";"):
            clause = clause.strip()
            if not clause or clause.startswith("none (binned:"):
                continue
            for part in clause.split(","):
                part = part.strip()
                if part.startswith("rqa."):
                    cited.add(part.split("(", 1)[0].strip())
    return cited


def collected_test_functions(path: pathlib.Path) -> int:
    """How many zero-argument ``test_*`` functions ``tests/run_all.py`` would
    collect from this file.

    Counted with ``ast`` rather than by importing, for the same reason
    condition 2 resolves dotted paths without importing them. The rule mirrors
    ``run_all.py``: a module-level ``test_*`` function defined in that module
    whose every parameter has a default. ``run_all.py`` additionally skips
    functions imported from elsewhere (``function.__module__ !=
    module.__name__``); a module-level ``FunctionDef`` is defined where it is
    written, so walking only ``tree.body`` is the static equivalent.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"))
    collected = 0
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        args = node.args
        positional = list(args.posonlyargs) + list(args.args)
        required = len(positional) - len(args.defaults)
        required += sum(1 for default in args.kw_defaults if default is None)
        if required == 0:
            collected += 1
    return collected


def cited_test_paths() -> dict[str, set[str]]:
    """Every ``tests/…`` path the map names as a replacement, mapped to the
    files whose deletion it authorises.

    A row that names *itself* is excluded: ``tests/run_all.py``'s row cites
    ``tests/run_all.py`` because the runner carried over unchanged, which is a
    statement that the file survived, not a claim that some other test now
    covers a deletion. Nothing can be deleted on the strength of such a row —
    condition 3 requires a ``present`` row's file to be on disk — so holding it
    to "names a replacement that is exercised" would be asking it a question it
    is not answering.
    """
    rows = parse_map_rows(_read_cutover_text())
    cited: dict[str, set[str]] = {}
    for r in rows:
        if r["file"] in DOC_SCHEMA_FILES or not _is_scripts_or_tests(r["file"]):
            continue
        for clause in r["replacement"].split(";"):
            clause = clause.strip()
            if not clause or clause.startswith("none (binned:"):
                continue
            for part in clause.split(","):
                part = part.strip()
                if not part.startswith("tests/"):
                    continue
                path = part.split("(", 1)[0].strip()
                if path == r["file"]:
                    continue  # carried over, not replaced — see the docstring
                cited.setdefault(path, set()).add(r["file"])
    return cited


def check_every_always_mapped_file_has_a_row() -> list[str]:
    """Condition 5: the row-identity baseline.

    Every file in ``ALWAYS_MAPPED_FILES`` must appear in the map by name,
    unconditionally -- whatever the row says, and whatever is on disk. Deleting
    such a file together with its own row is the one edit conditions 1-4 cannot
    see, because both halves of every comparison they make disappear at once.
    """
    rows = parse_map_rows(_read_cutover_text())
    mapped = {r["file"] for r in rows}
    return [
        f"{f}: no CUTOVER.md row at all — this file's row may never be removed "
        f"(CUTOVER.md never authorises deleting it)"
        for f in sorted(ALWAYS_MAPPED_FILES - mapped)
    ]


def check_every_cited_replacement_is_exercised() -> list[str]:
    """Condition 6: a cited replacement must be exercised, not merely present.

    CUTOVER.md's deletion rule is that a legacy file may go only once the map
    names its replacement *and that replacement is exercised*. Condition 2
    enforces the first half and stops there — it resolves a dotted path or a
    test path to a file on disk. Something that exists but that the suite never
    runs satisfies condition 2 while leaving the deletion it authorises
    untested.

    The map cites replacements in two shapes and both are checked here. Round 2
    covered only the first, which left the second — 19 ``tests/…`` citations —
    verified by ``is_file()`` alone: a cited test module could be emptied to a
    docstring, collect nothing, and keep every condition green while the
    deletions it authorised lost their coverage. A citation is only worth what
    it runs, whichever shape it is written in.
    """
    exercised = directly_exercised_modules()
    problems: list[str] = []
    for dotted in sorted(cited_rqa_modules()):
        if dotted in exercised:
            continue
        via = INDIRECTLY_EXERCISED.get(dotted)
        if via is None:
            problems.append(
                f"{dotted}: cited as a replacement but no collected "
                f"{COLLECTED_TEST_GLOB} module imports it"
            )
            continue
        # The exemption is only as good as the hop it names.
        if via not in exercised:
            problems.append(
                f"{dotted}: exempted as exercised via {via!r}, but no collected "
                f"{COLLECTED_TEST_GLOB} module imports {via!r} either"
            )
            continue
        source = _module_source(via)
        if source is None:
            problems.append(f"{dotted}: exempted via {via!r}, which does not resolve under rqa/")
        elif dotted not in _rqa_imports_in(source):
            problems.append(
                f"{dotted}: exempted as exercised via {via!r}, but {via!r} does not import it"
            )
    return problems


def check_every_cited_test_is_exercised(cited: dict[str, set[str]] | None = None) -> list[str]:
    """Condition 7: condition 6's rule, in the map's other citation shape.

    The map cites replacements two ways — 50 bare ``rqa.*`` paths and 20
    ``tests/…`` paths — and until now only the first was held to "named *and*
    exercised". For the second, condition 2 resolved the path on disk and
    stopped, so a cited test module could be emptied to a docstring and keep
    every condition green while the deletions it authorised lost their
    coverage. It is a separate condition rather than a branch inside condition
    6 so that its name states one quantifier and its body walks exactly that
    one; a condition whose name is wider than its body is the defect this whole
    round is about.

    ``cited`` is injectable so the negative cases below can be stated without
    touching the repository.
    """
    cited = cited_test_paths() if cited is None else cited
    problems: list[str] = []
    for path, claimants in sorted(cited.items()):
        source = SKILL / path
        if not source.is_file():
            continue  # condition 2 already reports an absent citation
        authorises = ", ".join(sorted(claimants))
        if not fnmatch.fnmatch(pathlib.PurePosixPath(path).name, "test_*.py"):
            problems.append(
                f"{path}: cited as the replacement for {authorises}, but "
                f"tests/run_all.py never collects it — only tests/test_*.py"
            )
            continue
        if collected_test_functions(source) == 0:
            problems.append(
                f"{path}: cited as the replacement for {authorises}, but it "
                f"collects no zero-argument test_* function — the citation "
                f"exercises nothing"
            )
    return problems


CHECKS = (
    ("condition 1 (every legacy file has a row)", check_every_legacy_file_has_a_row),
    ("condition 2 (every replacement resolves)", check_every_replacement_resolves),
    ("condition 3 (status matches the filesystem, and rows agree)", check_status_matches_filesystem_and_is_self_consistent),
    ("condition 4 (every never-deletable row claims its exact status, unconditionally)", check_always_mapped_status_is_exact),
    ("condition 5 (every never-deletable file still has a row at all)", check_every_always_mapped_file_has_a_row),
    ("condition 6 (every cited rqa.* replacement is exercised by a collected test)", check_every_cited_replacement_is_exercised),
    ("condition 7 (every cited tests/… replacement collects at least one test)", check_every_cited_test_is_exercised),
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


def test_always_mapped_status_is_exact() -> None:
    problems = check_always_mapped_status_is_exact()
    assert not problems, "\n".join(problems)


def test_every_always_mapped_file_has_a_row() -> None:
    problems = check_every_always_mapped_file_has_a_row()
    assert not problems, "\n".join(problems)


def test_every_cited_replacement_is_exercised() -> None:
    problems = check_every_cited_replacement_is_exercised()
    assert not problems, "\n".join(problems)


def test_every_cited_test_is_exercised() -> None:
    problems = check_every_cited_test_is_exercised()
    assert not problems, "\n".join(problems)


def test_indirectly_exercised_exemptions_are_all_still_needed() -> None:
    """The exemption list may not outlive its reason. Once a collected test
    imports one of these directly, its entry has to go, or the list slowly
    becomes a place where unexercised citations can be parked."""
    exercised = directly_exercised_modules()
    stale = sorted(d for d in INDIRECTLY_EXERCISED if d in exercised)
    assert not stale, (
        "these are now imported directly by a collected test and must be "
        f"removed from INDIRECTLY_EXERCISED: {stale}"
    )


def test_indirectly_exercised_exemptions_are_all_cited() -> None:
    """And it may not grow entries for citations the map no longer makes."""
    cited = cited_rqa_modules()
    orphaned = sorted(d for d in INDIRECTLY_EXERCISED if d not in cited)
    assert not orphaned, (
        "these are no longer cited as a replacement and must be removed from "
        f"INDIRECTLY_EXERCISED: {orphaned}"
    )


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
# The conditions' own negative cases.
#
# Every bypass found in review so far had the same shape: a condition whose
# name described an invariant and whose body quantified over something
# narrower, so the reproduction that exposed it got closed and the invariant
# did not. Asserting that the real map passes cannot catch that — a condition
# narrowed to nothing still passes. These state what each condition must
# *reject*, against synthetic input, so the next narrowing fails here.
# --------------------------------------------------------------------------- #

def _row(file_: str, status: str) -> dict:
    return {
        "file": file_, "part": "—", "lane": "—", "unit": "—",
        "disposition": "kept", "replacement": "—", "status": status,
    }


def test_condition_four_rejects_a_never_deletable_row_with_a_flipped_status() -> None:
    """The round-2 bypass: delete ``scripts/logging_otel.py`` and flip its own
    row from ``retained`` to ``deleted`` in the same edit. Condition 3 cannot
    object — once the file is gone it *requires* that flip — and a condition
    that only asks whether a row exists is satisfied by the flipped one."""
    problems = check_always_mapped_status_is_exact(
        [_row("scripts/logging_otel.py", "deleted")]
    )
    assert problems, "a flipped never-deletable status must be rejected"
    assert "must say status='retained'" in problems[0], problems


def test_condition_four_rejects_a_doc_schema_row_with_a_flipped_status() -> None:
    problems = check_always_mapped_status_is_exact([_row("SKILL.md", "deleted")])
    assert problems, "a flipped doc/schema status must be rejected"
    assert "must say status='present'" in problems[0], problems


def test_condition_four_accepts_the_status_each_baseline_file_must_claim() -> None:
    rows = [_row(f, status) for f, status in sorted(ALWAYS_MAPPED_STATUS.items())]
    assert not check_always_mapped_status_is_exact(rows)


def test_collected_test_functions_counts_only_what_run_all_would_run() -> None:
    """Mirrors ``run_all.py``: a module-level ``test_*`` function every one of
    whose parameters has a default. Anything else is not collected, so citing
    a module made only of those exercises nothing."""
    with tempfile.TemporaryDirectory() as directory:
        source = pathlib.Path(directory) / "test_rqa_example.py"
        source.write_text(
            "def test_collected() -> None: ...\n"
            "def test_also_collected(seed: int = 1) -> None: ...\n"
            "def test_not_collected(fixture) -> None: ...\n"
            "def test_not_collected_kwonly(*, fixture) -> None: ...\n"
            "def helper() -> None: ...\n"
            "class Thing:\n"
            "    def test_method_is_not_collected(self) -> None: ...\n",
            encoding="utf-8",
        )
        assert collected_test_functions(source) == 2


def test_an_emptied_cited_test_module_collects_nothing() -> None:
    """The round-2 bypass in its other citation shape: a cited ``tests/…``
    replacement emptied to a docstring still exists on disk, so condition 2 is
    satisfied while the deletions it authorises lose their coverage."""
    with tempfile.TemporaryDirectory() as directory:
        source = pathlib.Path(directory) / "test_rqa_emptied.py"
        source.write_text('"""emptied — collects nothing"""\n', encoding="utf-8")
        assert collected_test_functions(source) == 0


def test_condition_seven_rejects_an_emptied_cited_test_module() -> None:
    """The wiring, not just the helper. ``collected_test_functions`` counting
    correctly is worth nothing if the condition never calls it, which is the
    shape of every bypass found so far."""
    with tempfile.TemporaryDirectory() as directory:
        emptied = pathlib.Path(directory) / "tests" / "test_rqa_emptied.py"
        emptied.parent.mkdir()
        emptied.write_text('"""emptied — collects nothing"""\n', encoding="utf-8")
        original = globals()["SKILL"]
        globals()["SKILL"] = pathlib.Path(directory)
        try:
            problems = check_every_cited_test_is_exercised(
                {"tests/test_rqa_emptied.py": {"scripts/gone.py"}}
            )
        finally:
            globals()["SKILL"] = original
    assert problems, "an emptied cited test module must be rejected"
    assert "collects no zero-argument test_* function" in problems[0], problems


def test_condition_seven_rejects_a_citation_run_all_would_never_collect() -> None:
    with tempfile.TemporaryDirectory() as directory:
        helper = pathlib.Path(directory) / "tests" / "helpers.py"
        helper.parent.mkdir()
        helper.write_text("def test_looks_like_one() -> None: ...\n", encoding="utf-8")
        original = globals()["SKILL"]
        globals()["SKILL"] = pathlib.Path(directory)
        try:
            problems = check_every_cited_test_is_exercised(
                {"tests/helpers.py": {"scripts/gone.py"}}
            )
        finally:
            globals()["SKILL"] = original
    assert problems, "a citation run_all.py never collects must be rejected"
    assert "never collects it" in problems[0], problems


def test_every_condition_is_registered_in_checks() -> None:
    """A condition that is not in ``CHECKS`` is not a guard — ``main()`` never
    runs it and the standalone script stays green. Registration is pinned by
    name so that unwiring one fails here rather than passing silently."""
    registered = {fn.__name__ for _, fn in CHECKS}
    assert registered == {
        "check_every_legacy_file_has_a_row",
        "check_every_replacement_resolves",
        "check_status_matches_filesystem_and_is_self_consistent",
        "check_always_mapped_status_is_exact",
        "check_every_always_mapped_file_has_a_row",
        "check_every_cited_replacement_is_exercised",
        "check_every_cited_test_is_exercised",
    }, sorted(registered)


def test_section_zeros_binned_counts_match_the_table() -> None:
    """§0 states three numbers about §2's ``none (binned: …)`` rows. Four
    different counts have been offered for that sentence and no two agreed,
    because each was taken with a different unstated predicate. The predicate
    is now written in §0 and asserted here, so a disagreement fails the suite
    rather than reaching a reviewer."""
    text = _read_cutover_text()
    section_two = text.split("## 2. The map")[1].split("## 3.")[0]
    rows = [l for l in section_two.split("\n") if ROW_RE.match(l)]
    marked = [l for l in rows if "none (binned:" in l]
    files = {ROW_RE.match(l).group(1) for l in marked}
    units: set[str] = set()
    for line in marked:
        units |= set(re.findall(r"U-[A-Z]+-\d+", line.split("|")[6]))

    claim = "**22 rows in §2, spanning 19 files and 14 disposition\n    units**"
    assert claim in text, "§0 no longer states the counts this test asserts"
    assert (len(marked), len(files), len(units)) == (22, 19, 14), (
        f"§0 claims 22 rows / 19 files / 14 units; the table has "
        f"{len(marked)} / {len(files)} / {len(units)}"
    )


def test_every_baseline_file_exists_on_disk() -> None:
    """The baseline is a literal, so it can drift from the tree. A name that no
    longer exists protects nothing and hides that it protects nothing."""
    missing = sorted(f for f in ALWAYS_MAPPED_STATUS if not (SKILL / f).is_file())
    assert not missing, f"ALWAYS_MAPPED_STATUS names files that do not exist: {missing}"


def test_the_baseline_covers_every_row_that_claims_its_file_is_on_disk() -> None:
    """The generalisation, and the reason this is a test rather than a third
    pass over the two reproductions.

    ``tests/run_all.py`` and ``tests/conftest.py`` were ``present`` rows outside
    the baseline: deleting either with its row left all six conditions green,
    the same shape as the ``logging_otel.py`` bypass one step further out. Any
    row asserting its file is on disk can be removed together with that file,
    so every such row belongs in the baseline. Adding one to ``CUTOVER.md``
    without adding it here fails now, rather than being found by the next
    review."""
    rows = parse_map_rows(_read_cutover_text())
    live = {r["file"] for r in rows if r["status"] in ("present", "retained")}
    uncovered = sorted(live - set(ALWAYS_MAPPED_STATUS))
    assert not uncovered, (
        "these rows claim their file is on disk but are not in "
        f"ALWAYS_MAPPED_STATUS, so file and row can be deleted together: {uncovered}"
    )


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

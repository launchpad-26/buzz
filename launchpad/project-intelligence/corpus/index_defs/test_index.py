"""Builder for generated/test-index.md -- the repository test index (#905).

Subject: the repository's test suites and test files (Rust `#[test]`/
`#[tokio::test]` files under `crates/*/tests/` and inline `#[cfg(test)]`
module files, this corpus tooling's own `launchpad/project-intelligence/
corpus/tests/`, and desktop/mobile test files such as `*.test.mjs` and
`*_test.dart`). Like `generated/crate-index.md` (#893) and `generated/
code-to-doc-map.md` (#888), this is a CROSS-REFERENCE (known test file -> which
canonical nodes cite it as evidence), not a listing of canonical nodes
filtered by front-matter `type`.

Two candidate corpus-side signals were checked against the real corpus at the
base revision before choosing the citation-based rule below, following
#894/#899's precedent of naming the rejected signal(s) rather than picking the
first one that occurred to the author:

- `implements -> corpus-template-test-contract` or `implements ->
  corpus-template-test-strategy` (`launchpad/docs/corpus/templates/
  test-contract.md` and `.../templates/test-strategy.md`, both merged,
  `type: governance`): a `grep` of every corpus node's `relationships[].target`
  for either id found zero matches at this revision -- no canonical node has
  yet been authored *from* either template. A filter over this signal would
  render an honestly empty index, same as database-index.py's rejected
  `implements` candidates.
- Front-matter `type`: node.schema.json's type enum's `verification` value is
  carried by exactly the two templates above and by no other node at this
  revision (`grep -l '^type: verification$'` over the corpus), so it also
  yields nothing to list, and conceptually names verification-strategy
  documents, not raw test files.

Because both candidate corpus-side signals are unpopulated, this builder uses
the same mechanical evidence-citation classifier `index_defs/crate_index.py`
and `index_defs/code_to_doc_map.py` already established, layered with one
additional path-pattern predicate that decides whether a resolved citation
names a *test* file rather than ordinary source. The corpus already holds many
such citations today (e.g. `capabilities/search/search.md` cites
`crates/buzz-search/tests/fts_integration.rs:1-1509`, `capabilities/
notifications/notification-preferences.md` cites `desktop/src/features/
notifications/lib/shouldNotify.test.mjs`), so this listing populates
non-trivially rather than rendering an empty table.

Test-path-matching pattern (deterministic, character-shape only, stated here
in full so a reader knows exactly what counts as a "test path" versus
ordinary source -- see `_is_test_path` below for the executable form):
a resolved, existing repository path counts as a test path if and only if
EITHER (a) any of its directory components (every path segment except the
final filename) is spelled exactly `tests`, OR (b) its filename (the final
path segment) matches one of the three glob patterns `test_*`, `*_test.*`,
`*.test.*` (case-sensitive, `fnmatch.fnmatchcase`). This is a path-pattern
rule, not file-content parsing: it does not open any file to look for
`#[test]`, `#[cfg(test)]`, `def test_`, or similar markers, so a file with
inline tests but an ordinary name (e.g. `authority.rs`'s own `#[cfg(test)]`
module, cited by `capabilities/notifications/endpoint-installation.md`) is
NOT counted -- named explicitly in the exclusion bullets below and in "It does
not cover".

Citation resolution reuses crate_index.py/code_to_doc_map.py's mechanical
shape test (reject whitespace/parentheses/`->`/`://`, strip one trailing
`:N`/`:N-M` line suffix, reject absolute paths and `..` components, require
the stripped path to resolve to a real file in the working tree) verbatim,
duplicated locally rather than imported -- the same choice crate_index.py
documents, since builder modules are independently loadable and never import
each other. Unlike code_to_doc_map.py, this builder does NOT exclude
citations under `launchpad/docs/corpus/`: the corpus's own schema test file
(`launchpad/docs/corpus/schema/tests/test_schema.py`) is a genuine test file
nested inside the docs tree, and excluding that prefix wholesale would drop it
from a document whose entire subject is test files. A survey of the corpus at
authoring time found no non-test Markdown node living under a path segment
literally named `tests` or matching the three filename patterns, so this
looser scope does not pull in ordinary corpus prose.

node_type choice: `governance`, matching crate_index.py and code_to_doc_map.py
exactly -- this document's rows are repository test files, not canonical
corpus nodes of one front-matter type. `verification` was considered (it
reads as the most subject-appropriate enum value) and rejected: at this
revision it is carried only by the two governance-about-verification
templates named above, never by a node describing an actual verification
artifact, so it does not name what a row here actually is.

Determinism note (the same wrinkle crate_index.py and code_to_doc_map.py
disclose): both "which files exist" and "which citations resolve" are checked
against the working tree, which the framework's input digest (canonical
corpus nodes only) does not cover. At a fixed repository revision the index is
fully deterministic; the generated document discloses this in its "Expected
but not verified" section.
"""

from __future__ import annotations

import fnmatch
import re
import sys
from pathlib import Path
from pathlib import PurePosixPath

# indexes.py loads validate.py as "corpus_validate" before any builder module
# is imported, so this lookup always succeeds under the framework and under
# the test suite (both load indexes.py first).
_validate = sys.modules["corpus_validate"]

_LINE_SUFFIX_RE = re.compile(r":\d+(?:-\d+)?$")

# Filename-shape half of the test-path pattern. fnmatchcase is used (not
# fnmatch) so matching never depends on the host platform's case-folding
# rules -- determinism across machines, not just across runs.
_TEST_FILENAME_PATTERNS = ("test_*", "*_test.*", "*.test.*")

_EMPTY_MESSAGE = (
    "No canonical corpus node currently cites a path-shaped evidence citation "
    "that resolves to a repository test file under this builder's "
    "test-path-matching pattern. This index is empty because no such "
    "citations exist yet -- an honest empty fact, not an omission. It will "
    "populate automatically as nodes citing test files merge."
)


def _repo_root() -> Path:
    return _validate.repo_root().resolve()


def _resolved_path(citation, repo_root: Path):
    """Return the repo-relative posix path a citation names, or None.

    Purely mechanical: character-shape tests plus a filesystem existence
    check against `repo_root`. The same classifier
    `index_defs/crate_index.py` and `index_defs/code_to_doc_map.py` use,
    duplicated here rather than imported since builder modules never import
    one another.
    """
    if not isinstance(citation, str) or not citation:
        return None
    if any(ch in citation for ch in " \t\n()") or "->" in citation:
        return None  # tool-result / prose shape (includes "commit <sha>")
    if "://" in citation:
        return None  # URL
    stripped = _LINE_SUFFIX_RE.sub("", citation)
    if ":" in stripped:
        return None  # residual colon: not a plain relative path
    pure = PurePosixPath(stripped)
    if pure.is_absolute() or ".." in pure.parts or not pure.parts:
        return None
    rel = pure.as_posix()
    if not (repo_root / pure).is_file():
        return None  # does not resolve to a real file in this tree
    return rel


def _is_test_path(rel: str) -> bool:
    """True iff `rel` is a test path under this builder's stated pattern:
    a `tests` directory component anywhere above the filename, OR a filename
    matching `test_*`, `*_test.*` or `*.test.*`. Path-pattern only -- never
    opens the file to look for test markers inside it."""
    parts = PurePosixPath(rel).parts
    if not parts:
        return False
    if "tests" in parts[:-1]:
        return True
    name = parts[-1]
    return any(fnmatch.fnmatchcase(name, pat) for pat in _TEST_FILENAME_PATTERNS)


def _test_citations(ctx):
    """{test path -> sorted node ids citing it}, over every valid canonical
    node's evidence citations that resolve to a real, test-shaped file."""
    repo_root = _repo_root()
    found: dict[str, set[str]] = {}
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                rel = _resolved_path(citation, repo_root)
                if rel is None or not _is_test_path(rel):
                    continue
                found.setdefault(rel, set()).add(node.id)
    return {path: tuple(sorted(ids)) for path, ids in found.items()}


def _generate(ctx):
    by_path = _test_citations(ctx)
    lines = ["## Test index", ""]
    if by_path:
        lines += ["| Test path | Citing node(s) |", "|---|---|"]
        for path in sorted(by_path):
            node_ids = ", ".join(by_path[path])
            lines.append(f"| `{path}` | {node_ids} |")
    else:
        lines += [_EMPTY_MESSAGE]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "one row per distinct repository test path cited by at least one "
            "valid canonical node's front-matter `evidence[].evidence` "
            "citation, where the citation is path-shaped (no whitespace, "
            "parentheses, `->` or `://`; an optional single trailing `:N` / "
            "`:N-M` line suffix is stripped) and resolves to a real file in "
            "the repository's working tree",
            "a resolved path counts as a test path when either (a) any "
            "directory component of the path (every segment except the "
            "final filename) is spelled exactly `tests`, or (b) the "
            "filename matches `test_*`, `*_test.*`, or `*.test.*` "
            "(case-sensitive) -- a path-pattern rule, never file-content "
            "parsing",
            "the row's citing-node column lists every distinct valid node "
            "id whose evidence cites that path, sorted",
        ],
        "excludes": [
            "tool-result and prose-shaped citations (anything containing "
            "whitespace, parentheses or `->`), including bare `commit <sha>` "
            "refs -- a commit is not a test path",
            "bare URLs (any citation containing `://`)",
            "absolute paths, paths with `..` components, and path-shaped "
            "citations that do not resolve to a regular file in the current "
            "working tree",
            "files that contain tests (e.g. an inline `#[cfg(test)] mod "
            "tests` block) but whose own path matches neither half of the "
            "pattern above -- this index never opens a file to look inside "
            "it",
            "citations under a directory literally named `test` (singular) "
            "whose filename also fails both filename patterns -- only the "
            "plural `tests` directory name and the three filename patterns "
            "are matched",
        ],
        "ordering": (
            "rows sorted lexicographically by test path; each row's "
            "citing-node list sorted by node id"
        ),
        "not_covered": [
            "Whether a listed test file still exercises the behavior a "
            "citing node's statement describes -- resolution checks "
            "existence and path shape only, never test content or pass/fail "
            "status.",
            "Test files with zero citing canonical node -- this is a "
            "cross-reference driven by existing evidence citations, not an "
            "independent enumeration of every test file in the working "
            "tree the way crate_index.py enumerates `crates/*/Cargo.toml`.",
            "The reverse view (which capability/architecture a given test "
            "file actually covers) beyond what reading this table backwards "
            "provides.",
        ],
        "unverified": [
            "Existence of cited files and their test-path shape are checked "
            "against the working tree at generation time, which the input "
            "digest (canonical corpus nodes only) does not cover; renaming, "
            "moving or deleting a cited test file changes this index "
            "without changing the digest.",
        ],
    }


def _extra_evidence(ctx):
    by_path = _test_citations(ctx)
    node_count = len({n for ids in by_path.values() for n in ids})
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, the canonical "
                f"nodes' evidence citations yield exactly {len(by_path)} "
                f"distinct test path(s) across {node_count} distinct citing "
                "node(s), decided by the mechanical citation classifier and "
                "test-path-matching pattern in this builder module, never by "
                "prose judgement. A relationships-target search for "
                "`corpus-template-test-contract` and "
                "`corpus-template-test-strategy` across the corpus at this "
                "revision found zero implementing nodes, so this index uses "
                "the citation-based rule rather than an `implements` filter."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/test_index.py"
            ],
        }
    ]


SPEC = {
    "name": "test-index",
    "output_path": "generated/test-index.md",
    "node_id": "generated-test-index",
    "title": "Test index: generated cross-reference of repository test files and citing nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the repository's test suites and test files (Rust tests under "
        "crates/*/tests/, this corpus tooling's own tests/, desktop/mobile "
        "test files), cross-referenced against the canonical corpus nodes "
        "that cite them as evidence"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}

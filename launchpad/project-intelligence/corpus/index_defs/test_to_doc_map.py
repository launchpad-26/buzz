"""Builder for generated/test-to-doc-map.md -- the test-to-doc mapping (#906).

This document is the TEST-FILTERED SUBSET of generated/code-to-doc-map.md
(#888, index_defs/code_to_doc_map.py): the exact same underlying (code path,
node id) pairs that document computes, kept only where the code path is
test-shaped (see `_is_test_path` below). It is NOT an independent extraction
-- it reuses #888's citation classifier directly, following #897's precedent
(index_defs/doc_to_code_map.py) of loading a sibling builder module by its
own fixed path and calling that module's private `_pairs(ctx)` rather than
re-implementing the citation-parsing logic. code_to_doc_map.py is not edited
to enable this. See `_load_code_to_doc_map` below for why this is safe
regardless of builder discovery order.

Base inclusion rule (identical to code_to_doc_map.py's, restated here for a
reader of this document alone): walk every valid canonical node's
``evidence[].evidence`` citation strings and keep exactly those that are
path-shaped and resolve to a real file in this repository, outside the corpus
root and outside ``launchpad/decisions/``. "Path-shaped" is decided entirely
by code_to_doc_map.py's mechanical classifier -- character shape and
filesystem resolution only, never prose judgement.

Test-path filter (this module's own addition, applied on top of the base
rule above): a code path is test-shaped, per `_is_test_path`, if EITHER of
these mechanical, path-string-only checks holds --

1. Directory check: any path segment, compared case-insensitively, is exactly
   ``test`` or ``tests``, OR ends with the exact substring ``Test`` or
   ``Tests`` with a capital ``T`` (the camelCase/PascalCase test-directory
   convention seen in this repository: ``androidTest``, ``RunnerTests``,
   ``BuzzPushKitTests``). The capital-T requirement deliberately excludes an
   all-lowercase segment such as ``latest``, which ends with the substring
   ``test`` but is not a test directory.
2. Filename check: the final path segment matches one of --
   - ``test_*.py`` or ``*_test.py`` (Python unittest convention, both
     prefix and suffix forms seen in this repository);
   - ``*.test.<ext>`` or ``*.spec.<ext>`` for ``ext`` in
     ``{js, jsx, ts, tsx, mjs}`` (JS/TS unit-test and Playwright-spec
     convention);
   - ``*_test.dart`` (Dart test convention).

Neither check inspects file content or corpus front matter -- only the
character shape of the path string, matching the mechanical spirit of
code_to_doc_map.py's own `_code_path`. `index_defs/test_index.py` (#905) does
not exist on this builder's base branch (verified at authoring time), so this
pattern is defined independently rather than reused from that task; if #905
later settles on a different pattern, reconciling the two is a follow-up, not
a retroactive change made here.

Deliberately NOT treated as code paths in the first place (inherited from
code_to_doc_map.py, each shape is named in the generated document's exclusion
section too):
- tool-result / prose citations -- anything containing whitespace, parentheses
  or ``->`` (this also catches ``commit <sha>`` refs, which carry a space);
- bare URLs (anything containing ``://``);
- citations under ``launchpad/docs/corpus/`` (doc-to-doc references, not code)
  and under ``launchpad/decisions/`` (decision records, the decisions index's
  subject, #845);
- absolute paths, paths with ``..`` components, and path-shaped strings that do
  not resolve to a regular file in the current working tree.

node_type choice: ``governance``, for the identical reason code_to_doc_map.py
and doc_to_code_map.py give for their own choice: the listing's rows are
repository files and corpus node ids, not corpus nodes of one subject type,
so no subject-specific enum value fits the way ``interfaces-events`` fits
api-index; this map is corpus-about-corpus traceability machinery.

relationships: only ``references -> corpus-agents``, matching both precedent
builders. ``implements -> corpus-template-generated-index`` is deliberately
omitted for the same reason those documents state: the generated-index
template's own "Boundary against the rest of the generated/*.md family" table
classifies ``*-map`` documents as mappings needing their own per-type
template, so an ``implements`` edge toward the index template would
contradict the template's own text.

Determinism note (identical wrinkle to code_to_doc_map.py's): membership
depends on the presence of cited files in the working tree, which the
framework's input digest (corpus nodes only) does not cover. At a fixed
repository revision the mapping is fully deterministic; the generated
document discloses the wrinkle in its unverified section.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path, PurePosixPath

_HERE = Path(__file__).resolve().parent
_CODE_TO_DOC_MAP_PATH = _HERE / "code_to_doc_map.py"


def _load_code_to_doc_map():
    """Load code_to_doc_map.py (#888) under a private sys.modules key so this
    module can call its `_pairs(ctx)` directly instead of re-implementing the
    citation classifier.

    A private key -- not the `corpus_index_def_code_to_doc_map` name
    indexes.py's own discover_builders() registers it under -- avoids
    colliding with, or depending on the load order of, that discovery loop:
    this loader always resolves code_to_doc_map.py by its own fixed path on
    disk, the same way indexes.py itself loads validate.py by fixed path
    rather than relying on import machinery to find it, and the same way
    doc_to_code_map.py (#897) already does for this exact module. Safe to
    call from module scope: whatever caused this module to be imported
    (indexes.py's discovery, or a test loading indexes.py first, per
    code_to_doc_map.py's own documented assumption) has already registered
    "corpus_validate" in sys.modules, which code_to_doc_map.py's own top
    level requires.
    """
    key = "corpus_test_to_doc_map_shared_code_to_doc_map"
    existing = sys.modules.get(key)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(key, _CODE_TO_DOC_MAP_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


_code_to_doc_map = _load_code_to_doc_map()

_PY_TEST_FILENAME_RE = re.compile(r"^(test_.+\.py|.+_test\.py)$")
_DART_TEST_FILENAME_RE = re.compile(r"^.+_test\.dart$")
_JS_TEST_FILENAME_RE = re.compile(
    r"^.+\.(?:test|spec)\.(?:js|jsx|ts|tsx|mjs)$"
)


def _is_test_dir_segment(segment: str) -> bool:
    lowered = segment.lower()
    if lowered in ("test", "tests"):
        return True
    return segment.endswith("Test") or segment.endswith("Tests")


def _is_test_filename(name: str) -> bool:
    return bool(
        _PY_TEST_FILENAME_RE.match(name)
        or _DART_TEST_FILENAME_RE.match(name)
        or _JS_TEST_FILENAME_RE.match(name)
    )


def _is_test_path(rel: str) -> bool:
    """Mechanical, path-string-only test-shape classifier -- see the module
    docstring's "Test-path filter" section for the exact rule this
    implements."""
    pure = PurePosixPath(rel)
    if any(_is_test_dir_segment(part) for part in pure.parts[:-1]):
        return True
    return _is_test_filename(pure.name)


def _pairs(ctx):
    """The test-shaped subset of code_to_doc_map._pairs(ctx), unchanged sort
    order (code path, then node id) -- the same sort that document uses."""
    return [
        (path, node_id)
        for path, node_id in _code_to_doc_map._pairs(ctx)
        if _is_test_path(path)
    ]


def _generate(ctx):
    pairs = _pairs(ctx)
    lines = ["## Test-to-doc mapping", ""]
    if pairs:
        lines += ["| Test path | Corpus node id |", "|---|---|"]
        for rel, node_id in pairs:
            lines.append(f"| `{rel}` | {node_id} |")
    else:
        lines += [
            "No canonical corpus node currently cites a test-shaped code",
            "path (see the inclusion rule above) as evidence. This mapping is empty",
            "because no such citations exist yet -- an empty fact, not an",
            "omission. It will populate automatically as nodes citing test",
            "files merge.",
        ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "This document is the TEST-FILTERED SUBSET of "
            "generated/code-to-doc-map.md (#888), not an independent "
            "extraction: it reuses that document's builder "
            "(index_defs/code_to_doc_map.py, `_pairs`) directly, then keeps "
            "only pairs whose code path is test-shaped.",
            "one row per distinct (code path, node id) pair from "
            "generated/code-to-doc-map.md's own pair set, kept only where "
            "the code path is test-shaped: a path segment (case-insensitive) "
            "equal to `test`/`tests`, or ending in `Test`/`Tests` with a "
            "capital T (e.g. `androidTest`, `RunnerTests`); OR a filename "
            "matching `test_*.py`/`*_test.py`, `*.test.<ext>`/`*.spec.<ext>` "
            "for ext in {js,jsx,ts,tsx,mjs}, or `*_test.dart`",
        ],
        "excludes": [
            "every non-test-shaped pair from generated/code-to-doc-map.md -- "
            "this document narrows that mapping, it does not widen it",
            "an all-lowercase directory segment that merely ends with the "
            "substring `test` (e.g. `latest`) -- the capital-T requirement "
            "on the camelCase/PascalCase form excludes it deliberately",
            "tool-result and prose-shaped citations (anything containing "
            "whitespace, parentheses or `->`), including bare `commit <sha>` "
            "refs -- a commit is not a code path (inherited from "
            "code_to_doc_map.py's base rule)",
            "bare URLs (any citation containing `://`)",
            "citations under `launchpad/docs/corpus/` -- doc-to-doc "
            "references, not code",
            "citations under `launchpad/decisions/` -- decision records, the "
            "decisions index's subject, not code",
            "absolute paths, paths with `..` components, and path-shaped "
            "citations that do not resolve to a regular file in the current "
            "working tree",
        ],
        "ordering": (
            "mapping rows sorted lexicographically by code path, then by "
            "node id -- the identical sort generated/code-to-doc-map.md "
            "uses, since this document is a filtered view of that one's "
            "pairs; duplicate (path, node) pairs arising from multiple "
            "line-suffixed citations of one file collapse into one row, the "
            "same way they do there"
        ),
        "not_covered": [
            "Whether each cited test file still supports the citing node's "
            "statement -- resolution checks existence only, never content.",
            "Test files cited only inside tool-result strings (e.g. "
            "`grep_recursive(...) -> ...`) -- those citation shapes are "
            "excluded wholesale rather than mined for embedded paths.",
            "Any test-path convention not covered by the pattern this "
            "module states explicitly -- for example a repository test file "
            "using a naming convention outside the checked shapes would not "
            "appear here even if cited.",
            "The reverse view (which corpus nodes a given test path maps to) "
            "beyond what reading this table backwards provides.",
        ],
        "unverified": [
            "Existence of cited files is checked against the working tree at "
            "generation time, which the input digest (corpus nodes only) "
            "does not cover; deleting a cited file without touching any "
            "corpus node changes this mapping without changing the digest.",
            "Whether `index_defs/test_index.py` (#905), if and when it "
            "merges, defines a test-path pattern different from this "
            "module's `_is_test_path` -- this module was authored before "
            "#905 existed on this base branch and does not depend on it.",
        ],
    }


def _extra_evidence(ctx):
    pairs = _pairs(ctx)
    all_pairs = _code_to_doc_map._pairs(ctx)
    paths = {p for p, _ in pairs}
    nodes = {n for _, n in pairs}
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, filtering "
                f"generated/code-to-doc-map.md's {len(all_pairs)} (code "
                f"path, node id) pair(s) to test-shaped code paths yields "
                f"exactly {len(pairs)} pair(s) across {len(paths)} distinct "
                f"test path(s) and {len(nodes)} distinct node(s); this "
                "document is the test-filtered subset of that mapping, not "
                "an independent extraction, and membership is decided by "
                "code_to_doc_map.py's citation classifier plus this "
                "module's own mechanical `_is_test_path` check, never by "
                "prose judgement."
            ),
            "entry_class": "FACT",
            "evidence": [
                "launchpad/project-intelligence/corpus/index_defs/code_to_doc_map.py",
                "launchpad/project-intelligence/corpus/validate.py",
            ],
        }
    ]


SPEC = {
    "name": "test-to-doc-map",
    "output_path": "generated/test-to-doc-map.md",
    "node_id": "generated-test-to-doc-map",
    "title": "Test-to-doc map: generated mapping from test paths to corpus nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the test-shaped repository code paths cited as evidence by "
        "canonical corpus nodes, mapped to the nodes citing them -- the "
        "test-filtered subset of generated/code-to-doc-map.md"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}

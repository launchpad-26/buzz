"""Builder for generated/code-to-doc-map.md -- the code-to-doc mapping (#888).

This document is a MAPPING (code path -> corpus node), not a flat listing of
nodes of one type: each row is a (repository path, node id) pair, derived from
the canonical nodes' own front-matter evidence citations.

Inclusion rule (deterministic, schema-grounded): walk every valid canonical
node's ``evidence[].evidence`` citation strings and keep exactly those that are
path-shaped and resolve to a real file in this repository, outside the corpus
root and outside ``launchpad/decisions/``. "Path-shaped" is decided by the
mechanical classifier in :func:`_code_path` below -- character shape and
filesystem resolution only, never prose judgement. One table row is emitted per
distinct (code path, citing node id) pair, sorted by code path then node id.
A citation may carry one trailing ``:N`` or ``:N-M`` line suffix (the corpus's
established line-anchor shape); the suffix is stripped so all line-level
citations of one file collapse into one row for that (file, node) pair.

Deliberately NOT treated as code paths (each shape is named in the generated
document's exclusion section too):
- tool-result / prose citations -- anything containing whitespace, parentheses
  or ``->`` (this also catches ``commit <sha>`` refs, which carry a space);
- bare URLs (anything containing ``://``);
- citations under ``launchpad/docs/corpus/`` (doc-to-doc references, not code)
  and under ``launchpad/decisions/`` (decision records, the decisions index's
  subject, #845);
- absolute paths, paths with ``..`` components, and path-shaped strings that do
  not resolve to a regular file in the current working tree.

node_type choice: ``governance``. The listing's rows are repository files, not
corpus nodes of one subject type, so no subject-specific enum value fits the
way ``interfaces-events`` fits api-index; this map is corpus-about-corpus
traceability machinery, the same reasoning README.md and the standards nodes
give for their own ``type: governance``.

relationships: only ``references -> corpus-agents`` (the node whose evidence
rules define the citation shapes this map classifies). ``implements ->
corpus-template-generated-index`` is deliberately omitted: that template's own
"Boundary against the rest of the generated/*.md family" table classifies
``*-map`` documents as mappings needing their own per-type template, so an
implements edge would contradict the template's text.

Determinism note: membership depends on the presence of cited files in the
working tree, which the framework's input digest (corpus nodes only) does not
cover. At a fixed repository revision the mapping is fully deterministic; the
generated document discloses the wrinkle in its unverified section.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from pathlib import PurePosixPath

# indexes.py loads validate.py as "corpus_validate" before any builder module
# is imported, so this lookup always succeeds under the framework and under
# the test suite (both load indexes.py first).
_validate = sys.modules["corpus_validate"]

_LINE_SUFFIX_RE = re.compile(r":\d+(?:-\d+)?$")

_EXCLUDED_PREFIXES = ("launchpad/docs/corpus/", "launchpad/decisions/")


def _repo_root() -> Path:
    return _validate.repo_root().resolve()


def _code_path(citation, repo_root: Path):
    """Return the repo-relative posix path a citation names, or None.

    Purely mechanical: character-shape tests plus a filesystem existence check
    against ``repo_root``. Every rejection branch corresponds to one named
    exclusion in the generated document.
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
    if rel.startswith(_EXCLUDED_PREFIXES):
        return None
    if not (repo_root / pure).is_file():
        return None  # does not resolve to a real file in this tree
    return rel


def _pairs(ctx):
    """All distinct (code path, node id) pairs, sorted by path then node id."""
    repo_root = _repo_root()
    found = set()
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                rel = _code_path(citation, repo_root)
                if rel is not None:
                    found.add((rel, node.id))
    return sorted(found)


def _generate(ctx):
    pairs = _pairs(ctx)
    lines = ["## Code-to-doc mapping", ""]
    if pairs:
        lines += ["| Code path | Corpus node id |", "|---|---|"]
        for rel, node_id in pairs:
            lines.append(f"| `{rel}` | {node_id} |")
    else:
        lines += [
            "No canonical corpus node currently cites a path-shaped evidence",
            "citation that resolves to a repository file outside the corpus",
            "root and outside `launchpad/decisions/`. This mapping is empty",
            "because no such citations exist yet -- an empty fact, not an",
            "omission. It will populate automatically as nodes citing code",
            "merge.",
        ]
    return {
        "sections": "\n".join(lines),
        "includes": [
            "one row per distinct (code path, node id) pair, where the code "
            "path comes from a valid canonical node's front-matter "
            "`evidence[].evidence` citation that is path-shaped (no "
            "whitespace, parentheses, `->` or `://`; an optional single "
            "trailing `:N` / `:N-M` line suffix is stripped) and resolves to "
            "a real file in this repository's working tree",
        ],
        "excludes": [
            "tool-result and prose-shaped citations (anything containing "
            "whitespace, parentheses or `->`), including bare `commit <sha>` "
            "refs -- a commit is not a code path",
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
            "node id; duplicate (path, node) pairs arising from multiple "
            "line-suffixed citations of one file collapse into one row"
        ),
        "not_covered": [
            "Whether each cited file still supports the citing node's "
            "statement -- resolution checks existence only, never content.",
            "Code files cited only inside tool-result strings (e.g. "
            "`grep_recursive(...) -> ...`) -- those citation shapes are "
            "excluded wholesale rather than mined for embedded paths.",
            "The reverse view (which corpus nodes a given doc maps to code "
            "from) beyond what reading this table backwards provides.",
        ],
        "unverified": [
            "Existence of cited files is checked against the working tree at "
            "generation time, which the input digest (corpus nodes only) "
            "does not cover; deleting a cited file without touching any "
            "corpus node changes this mapping without changing the digest.",
        ],
    }


def _extra_evidence(ctx):
    pairs = _pairs(ctx)
    paths = {p for p, _ in pairs}
    nodes = {n for _, n in pairs}
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, the canonical "
                f"nodes' evidence citations yield exactly {len(pairs)} "
                f"(code path, node id) pair(s) across {len(paths)} distinct "
                f"repository path(s) and {len(nodes)} distinct node(s); "
                "membership is decided by the mechanical citation classifier "
                "in the builder module and a file-existence check against "
                "the working tree, never by prose judgement."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/validate.py"],
        }
    ]


SPEC = {
    "name": "code-to-doc-map",
    "output_path": "generated/code-to-doc-map.md",
    "node_id": "generated-code-to-doc-map",
    "title": "Code-to-doc map: generated mapping from repository paths to corpus nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the repository code paths cited as evidence by canonical corpus "
        "nodes, mapped to the nodes citing them"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}

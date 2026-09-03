"""Builder for generated/doc-to-code-map.md -- the doc-to-code mapping (#897).

This document is the INVERSE VIEW of generated/code-to-doc-map.md (#888,
index_defs/code_to_doc_map.py): the exact same underlying (code path, node id)
pairs, regrouped by node id instead of by code path and sorted (node id, code
path) instead of (code path, node id). It is a MAPPING (corpus node id ->
repository code path), not a flat listing of nodes of one type.

Same-relationship, same-rules: to keep the two views honestly consistent --
they describe one relationship read in two directions, not two independent
extractions that could quietly drift apart -- this module does not
re-implement the citation classifier. It loads code_to_doc_map.py (#888) by
its own fixed path (the same pattern indexes.py itself uses to load
validate.py) and calls that module's private `_pairs(ctx)` directly, then
regroups the result. code_to_doc_map.py is not edited to enable this: the
citation-parsing logic (`_code_path`, `_pairs`) lives in exactly one place in
the repository, this module merely reads it. See `_load_code_to_doc_map`
below for why this is safe regardless of builder discovery order.

Inclusion rule (identical to code_to_doc_map.py's, restated here for a reader
of this document alone): walk every valid canonical node's
``evidence[].evidence`` citation strings and keep exactly those that are
path-shaped and resolve to a real file in this repository, outside the corpus
root and outside ``launchpad/decisions/``. "Path-shaped" is decided by
code_to_doc_map.py's mechanical classifier -- character shape and filesystem
resolution only, never prose judgement. One table row is emitted per distinct
(node id, code path) pair, sorted by node id then code path. A citation may
carry one trailing ``:N`` or ``:N-M`` line suffix (the corpus's established
line-anchor shape); the suffix is stripped so all line-level citations of one
file collapse into one row for that (node, file) pair.

Deliberately NOT treated as code paths, for the same reasons
code_to_doc_map.py excludes them (each shape is named in the generated
document's exclusion section too):
- tool-result / prose citations -- anything containing whitespace, parentheses
  or ``->`` (this also catches ``commit <sha>`` refs, which carry a space);
- bare URLs (anything containing ``://``);
- citations under ``launchpad/docs/corpus/`` (doc-to-doc references, not code)
  and under ``launchpad/decisions/`` (decision records, the decisions index's
  subject, #845);
- absolute paths, paths with ``..`` components, and path-shaped strings that do
  not resolve to a regular file in the current working tree.

node_type choice: ``governance``, for the identical reason code_to_doc_map.md
gives for its own choice: the listing's rows are repository files and corpus
node ids, not corpus nodes of one subject type, so no subject-specific enum
value fits the way ``interfaces-events`` fits api-index; this map is
corpus-about-corpus traceability machinery, the same reasoning README.md,
AGENTS.md and the standards nodes give for their own ``type: governance``.

relationships: only ``references -> corpus-agents``, matching
code_to_doc_map.py exactly. ``implements -> corpus-template-generated-index``
is deliberately omitted for the same reason that document states: the
generated-index template's own "Boundary against the rest of the
generated/*.md family" table classifies ``*-map`` documents (naming
``doc-to-code-map.md`` explicitly, issue #897) as mappings needing their own
per-type template, so an ``implements`` edge toward the index template would
contradict the template's own text.

Determinism note (identical wrinkle to code_to_doc_map.py's): membership
depends on the presence of cited files in the working tree, which the
framework's input digest (corpus nodes only) does not cover. At a fixed
repository revision the mapping is fully deterministic; the generated
document discloses the wrinkle in its unverified section.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

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
    rather than relying on import machinery to find it. Safe to call from
    module scope: whatever caused this module to be imported (indexes.py's
    discovery, or a test loading indexes.py first, per code_to_doc_map.py's
    own documented assumption) has already registered "corpus_validate" in
    sys.modules, which code_to_doc_map.py's own top level requires.
    """
    key = "corpus_doc_to_code_map_shared_code_to_doc_map"
    existing = sys.modules.get(key)
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location(key, _CODE_TO_DOC_MAP_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


_code_to_doc_map = _load_code_to_doc_map()


def _pairs_by_node(ctx):
    """The same (code path, node id) pairs code_to_doc_map._pairs(ctx)
    computes, regrouped as (node id, code path) and sorted by node id then
    code path -- the inverse ordering of that document's own sort."""
    return sorted((node_id, path) for path, node_id in _code_to_doc_map._pairs(ctx))


def _generate(ctx):
    pairs = _pairs_by_node(ctx)
    lines = ["## Doc-to-code mapping", ""]
    if pairs:
        lines += ["| Corpus node id | Code path |", "|---|---|"]
        for node_id, rel in pairs:
            lines.append(f"| {node_id} | `{rel}` |")
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
            "one row per distinct (node id, code path) pair, where the code "
            "path comes from that valid canonical node's front-matter "
            "`evidence[].evidence` citation that is path-shaped (no "
            "whitespace, parentheses, `->` or `://`; an optional single "
            "trailing `:N` / `:N-M` line suffix is stripped) and resolves to "
            "a real file in this repository's working tree -- the identical "
            "inclusion rule generated/code-to-doc-map.md (#888) applies, "
            "read the other way around",
        ],
        "excludes": [
            "This document is the INVERSE of generated/code-to-doc-map.md "
            "(#888): the same (code path, node id) pairs, regrouped by node "
            "id instead of by code path. It reuses that document's builder "
            "(index_defs/code_to_doc_map.py, `_pairs`) directly rather than "
            "re-deriving the pairs, so the two documents cannot drift apart "
            "on which citations qualify.",
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
            "mapping rows sorted lexicographically by node id, then by code "
            "path -- the inverse of generated/code-to-doc-map.md's own "
            "(code path, node id) sort; duplicate (node, path) pairs arising "
            "from multiple line-suffixed citations of one file collapse into "
            "one row, the same way they do there"
        ),
        "not_covered": [
            "Whether each cited file still supports the citing node's "
            "statement -- resolution checks existence only, never content.",
            "Code files cited only inside tool-result strings (e.g. "
            "`grep_recursive(...) -> ...`) -- those citation shapes are "
            "excluded wholesale rather than mined for embedded paths.",
            "The forward view (which code paths a given node cites) beyond "
            "what reading this table backwards provides -- that is "
            "generated/code-to-doc-map.md's own subject.",
        ],
        "unverified": [
            "Existence of cited files is checked against the working tree at "
            "generation time, which the input digest (corpus nodes only) "
            "does not cover; deleting a cited file without touching any "
            "corpus node changes this mapping without changing the digest.",
        ],
    }


def _extra_evidence(ctx):
    pairs = _pairs_by_node(ctx)
    nodes = {n for n, _ in pairs}
    paths = {p for _, p in pairs}
    return [
        {
            "statement": (
                f"At input digest sha256:{ctx.input_digest}, the canonical "
                f"nodes' evidence citations yield exactly {len(pairs)} "
                f"(node id, code path) pair(s) across {len(nodes)} distinct "
                f"node(s) and {len(paths)} distinct repository path(s) -- the "
                "same pair count generated/code-to-doc-map.md reports at the "
                "same digest, since both documents are computed from the "
                "identical `_pairs(ctx)` call; membership is decided by the "
                "mechanical citation classifier in code_to_doc_map.py and a "
                "file-existence check against the working tree, never by "
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
    "name": "doc-to-code-map",
    "output_path": "generated/doc-to-code-map.md",
    "node_id": "generated-doc-to-code-map",
    "title": "Doc-to-code map: generated mapping from corpus nodes to repository paths",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the canonical corpus nodes that cite repository code paths as "
        "evidence, mapped to the paths they cite -- the inverse view of "
        "generated/code-to-doc-map.md"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": ({"type": "references", "target": "corpus-agents"},),
}

"""Builder: generated/configuration-index.md -- issue #890 (parent PRD #621).

A generated index of every canonical corpus node that documents configuration,
selected by the corpus-root-relative path prefix ``layers/configuration/``.

Why the path prefix is the rule -- the three candidate signals were checked
against the real corpus at the base revision, and only the path delimits the
set exactly:

- Front-matter ``type``: node.schema.json's type enum has no ``configuration``
  value; every configuration node carries ``type: layers``, but so do the
  nodes under ``layers/compute/``, ``layers/lifecycle/`` and
  ``layers/observability/`` -- a type rule over-includes the whole layers
  surface.
- ``implements -> corpus-template-configuration``: 8 of the 9 configuration
  nodes declare it, but ``layers/configuration/defaults.md`` declares no
  relationships at all (its own body records that the template was still
  unmerged when it was authored), so a relationship rule silently drops a
  real configuration node.
- The path prefix ``layers/configuration/`` matches exactly the 9 real
  configuration nodes and nothing else.

Both rejected signals stay visible instead of being forgotten: every listing
row states whether the node declares the template ``implements`` edge, and two
divergence subsections surface (a) listed nodes whose ``type`` is not
``layers`` and (b) template implementers living outside the prefix -- so if
path and schema signals ever drift apart, the generated document says where.

``node_type`` choice: this index node carries ``type: layers`` -- the subject
nodes' own enum value, following the capability-index precedent that a
subject-specific index takes its subject's type (README/standards use
``governance`` only for nodes that govern the corpus itself; this document
governs nothing, it is a derived view of the configuration slice of the
layers surface).

Contract: module-level ``SPEC`` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets.
"""

from __future__ import annotations

_PATH_PREFIX = "layers/configuration/"
_TEMPLATE_ID = "corpus-template-configuration"
_EXPECTED_TYPE = "layers"


def _implements_template(node) -> bool:
    """Whether the node's own front matter declares a forward
    ``implements -> corpus-template-configuration`` edge."""
    for rel in node.data.get("relationships") or ():
        if (
            isinstance(rel, dict)
            and rel.get("type") == "implements"
            and rel.get("target") == _TEMPLATE_ID
        ):
            return True
    return False


def _generate(ctx):
    included = sorted(
        (n for n in ctx.valid_nodes if ctx.rel_path(n).startswith(_PATH_PREFIX)),
        key=ctx.rel_path,
    )
    type_divergent = [n for n in included if n.data.get("type") != _EXPECTED_TYPE]
    outside_implementers = sorted(
        (
            n
            for n in ctx.valid_nodes
            if not ctx.rel_path(n).startswith(_PATH_PREFIX)
            and _implements_template(n)
        ),
        key=ctx.rel_path,
    )

    lines = [
        "## Configuration index",
        "",
        f"{len(included)} canonical corpus node(s) live under "
        f"`{_PATH_PREFIX}` at this revision.",
        "",
        "| Id | Path | Status | Implements configuration template |",
        "|---|---|---|---|",
    ]
    for node in included:
        rel = ctx.rel_path(node)
        status = node.data.get("status", "")
        implements = "yes" if _implements_template(node) else "no"
        lines.append(f"| {node.id} | `{rel}` | {status} | {implements} |")

    lines += [
        "",
        f"### Listed nodes whose type is not `{_EXPECTED_TYPE}`",
        "",
        "The path prefix is the inclusion rule, so a node under "
        f"`{_PATH_PREFIX}` with a different front-matter `type` is still "
        "listed above; this subsection surfaces any such divergence:",
        "",
    ]
    if type_divergent:
        lines += ["| Path | Type |", "|---|---|"]
        for node in type_divergent:
            lines.append(f"| `{ctx.rel_path(node)}` | {node.data.get('type')} |")
    else:
        lines.append("- None at this revision.")

    lines += [
        "",
        f"### `{_TEMPLATE_ID}` implementers outside `{_PATH_PREFIX}`",
        "",
        "A valid node elsewhere in the corpus that declares "
        f"`implements -> {_TEMPLATE_ID}` would signal configuration "
        "documentation living outside the tree this index covers:",
        "",
    ]
    if outside_implementers:
        lines += ["| Id | Path |", "|---|---|"]
        for node in outside_implementers:
            lines.append(f"| {node.id} | `{ctx.rel_path(node)}` |")
    else:
        lines.append("- None at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node whose corpus-root-relative "
            f"path starts with `{_PATH_PREFIX}` -- the path prefix is the "
            "whole rule, because it is the only signal that exactly delimits "
            "the configuration nodes at this revision (there is no "
            "`configuration` type-enum value, `type: layers` spans other "
            "layers subtrees, and one real configuration node declares no "
            f"`implements -> {_TEMPLATE_ID}` edge)"
        ],
        "excludes": [
            "nodes selected by front-matter `type` alone: `type: layers` "
            "also covers `layers/compute/`, `layers/lifecycle/` and "
            "`layers/observability/`, which are not configuration nodes",
            f"nodes selected by `implements -> {_TEMPLATE_ID}` alone: "
            "`layers/configuration/defaults.md` declares no relationships, "
            "so that rule would silently drop a real configuration node -- "
            "each listing row instead states whether the node declares the "
            "edge, and implementers outside the prefix are surfaced in "
            "their own subsection rather than listed",
            "nodes the validator rejects (a parse or schema error): an "
            "invalid node has no trustworthy path-independent identity to "
            "list",
        ],
        "ordering": (
            "listing rows sorted by corpus-root-relative path; both "
            "divergence subsections use the same sort"
        ),
        "not_covered": [
            "What each configuration surface actually does -- the listed "
            "nodes themselves own their content; this index only locates "
            "them.",
        ],
    }


SPEC = {
    "name": "configuration-index",
    "output_path": "generated/configuration-index.md",
    "node_id": "generated-configuration-index",
    "title": "Configuration index: generated index",
    "node_type": _EXPECTED_TYPE,
    "audiences": ["agent", "developer", "operator", "reviewer"],
    "subject": (
        "every canonical corpus node under layers/configuration/"
    ),
    "generate": _generate,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": _TEMPLATE_ID},
    ),
}

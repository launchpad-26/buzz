"""Builder: generated/database-index.md -- issue #894 (parent PRD #621).

A generated index of every canonical corpus node that documents database or
schema subject matter -- selected by a forward ``implements`` edge to either
``corpus-template-datastore`` or ``corpus-template-data-entity``, the two
per-type templates the corpus already carries for this subject
(``launchpad/docs/corpus/templates/datastore.md`` and
``.../templates/data-entity.md``).

Why the ``implements`` edge is the rule -- three candidate signals were
checked against the real corpus at the base revision, following the
configuration-index precedent (#890) of naming the rejected signals rather
than picking the first one that occurred to the author:

- Front-matter ``type``: node.schema.json's type enum has no
  ``database``/``datastore``/``storage`` value. A real instance of the
  datastore template would carry ``type: architecture`` (per that template's
  own evidence ledger) -- but ``architecture`` also covers 50+ unrelated
  nodes across ``architecture/containers/``, ``context/``, ``deployment/``,
  ``flows/`` and ``principles/``. A real instance of the data-entity
  template would carry ``type: implementation`` -- but zero nodes of that
  type exist in the corpus at all today. Neither type value delimits a
  database-specific set.
- Path prefix: no ``layers/storage/`` or ``layers/database/`` subtree
  exists (``layers/`` holds only ``compute/``, ``configuration/``,
  ``lifecycle/`` and ``observability/``). The nearest candidate,
  ``architecture/containers/``, holds 10 nodes (postgres, redis,
  object-storage, relay, cli, desktop, mobile, web, agent-runtime,
  push-gateway) -- only 3 of which are actually datastores, and nothing in
  the path distinguishes them from the other 7.
- ``implements -> corpus-template-datastore`` or
  ``implements -> corpus-template-data-entity``: the only signal that does
  not over-include. At this revision it matches zero nodes -- no canonical
  node has yet been authored *from* either template -- so the primary
  listing is honestly empty rather than widened to look fuller, per this
  task's own dispatch brief.

Because the primary listing is empty today, a second, purely
front-matter-derived subsection is rendered alongside it: every valid node
under ``architecture/containers/`` (the prefix considered and rejected
above), each marked whether it declares either template's ``implements``
edge. This is not a second inclusion rule -- nothing in that subsection is
counted in the index -- it is a deterministic watch list, in the same spirit
as configuration-index's divergence subsections, that makes it visible the
day a real datastore or data-entity node is authored without the edge.

``node_type`` choice: this index node carries ``type: governance``. Unlike
capability-index or configuration-index, no single subject-type enum value
fits: a real datastore instance takes ``architecture``, a real data-entity
instance takes ``implementation`` -- two different types for one subject.
This follows the concept-index/glossary/coverage precedent of ``governance``
for a mixed-type subject, not capability-index's single-type precedent.

Contract: module-level ``SPEC`` per indexes.py's IndexSpec; the framework
renders all front matter and the templates/generated-index.md body skeleton.
This module supplies only the subject-specific listing and the
inclusion/exclusion bullets.
"""

from __future__ import annotations

_DATASTORE_TEMPLATE_ID = "corpus-template-datastore"
_DATA_ENTITY_TEMPLATE_ID = "corpus-template-data-entity"
_TEMPLATE_IDS = (_DATASTORE_TEMPLATE_ID, _DATA_ENTITY_TEMPLATE_ID)
_WATCHLIST_PREFIX = "architecture/containers/"


def _implemented_template(node) -> str | None:
    """The database template id this node declares a forward ``implements``
    edge to, or None if it declares neither."""
    for rel in node.data.get("relationships") or ():
        if (
            isinstance(rel, dict)
            and rel.get("type") == "implements"
            and rel.get("target") in _TEMPLATE_IDS
        ):
            return rel["target"]
    return None


def _generate(ctx):
    included = sorted(
        (n for n in ctx.valid_nodes if _implemented_template(n) is not None),
        key=ctx.rel_path,
    )
    watchlist = sorted(
        (n for n in ctx.valid_nodes if ctx.rel_path(n).startswith(_WATCHLIST_PREFIX)),
        key=ctx.rel_path,
    )

    lines = [
        "## Database index",
        "",
        f"{len(included)} canonical corpus node(s) declare a forward "
        f"`implements` edge to `{_DATASTORE_TEMPLATE_ID}` or "
        f"`{_DATA_ENTITY_TEMPLATE_ID}` at this revision.",
        "",
    ]
    if included:
        lines += ["| Id | Path | Status | Template implemented |", "|---|---|---|---|"]
        for node in included:
            rel = ctx.rel_path(node)
            status = node.data.get("status", "")
            template = _implemented_template(node)
            lines.append(f"| {node.id} | `{rel}` | {status} | `{template}` |")
    else:
        lines.append(
            "No canonical corpus node declares either edge yet. This is not "
            "a generator gap: no node has been authored from "
            f"`{_DATASTORE_TEMPLATE_ID}` or `{_DATA_ENTITY_TEMPLATE_ID}` at "
            "this revision, so an honest empty listing is the correct "
            "output -- the rule is not widened to include a node that "
            "merely discusses a database informally."
        )

    lines += [
        "",
        "### Architecture containers watch list",
        "",
        "Not part of the index above -- this subsection lists every valid "
        f"canonical node under `{_WATCHLIST_PREFIX}` (the path prefix "
        "considered and rejected as the inclusion rule, because it mixes "
        "database and non-database containers with no field to filter on), "
        "so that a future datastore node added under this prefix without "
        "the `implements` edge stays visible rather than silently "
        "excluded from the index above:",
        "",
    ]
    if watchlist:
        lines += ["| Id | Path | Implements a database template |", "|---|---|---|"]
        for node in watchlist:
            template = _implemented_template(node)
            implements = f"`{template}`" if template else "no"
            lines.append(f"| {node.id} | `{ctx.rel_path(node)}` | {implements} |")
    else:
        lines.append(f"- No valid node exists under `{_WATCHLIST_PREFIX}` at this revision.")

    return {
        "sections": "\n".join(lines),
        "includes": [
            "every valid canonical corpus node that declares a forward "
            f"`implements` edge whose target is `{_DATASTORE_TEMPLATE_ID}` "
            f"or `{_DATA_ENTITY_TEMPLATE_ID}` -- the only signal checked "
            "that does not over-include: there is no `database` type-enum "
            "value, `type: architecture` spans 50+ non-database nodes and "
            "`type: implementation` has zero nodes at all, and no "
            "`layers/storage/` or equivalent path prefix exists",
        ],
        "excludes": [
            "nodes selected by front-matter `type` alone: neither "
            "`architecture` nor `implementation` (the types a real "
            "datastore or data-entity instance would carry) delimits a "
            "database-specific set on this corpus",
            f"nodes selected by the path prefix `{_WATCHLIST_PREFIX}` "
            "alone: it holds 10 containers, only 3 of which are "
            "datastores, with nothing in the path to distinguish them -- "
            "those 10 are instead surfaced, unfiltered, in the watch list "
            "below the index as a deterministic (not name-matched) "
            "cross-check",
            "nodes the validator rejects (a parse or schema error): an "
            "invalid node has no trustworthy path-independent identity to "
            "list",
        ],
        "ordering": (
            "listing rows sorted by corpus-root-relative path; the watch "
            "list uses the same sort"
        ),
        "not_covered": [
            "What each database or schema surface actually documents -- "
            "the listed nodes themselves own their content; this index "
            "only locates them.",
            "Whether a container in the watch list ought to eventually be "
            "rewritten from the datastore template -- that is a "
            "hand-authored canonical-node decision, not this generator's.",
        ],
    }


SPEC = {
    "name": "database-index",
    "output_path": "generated/database-index.md",
    "node_id": "generated-database-index",
    "title": "Database index: generated index",
    "node_type": "governance",
    "audiences": ["agent", "developer", "operator", "reviewer"],
    "subject": (
        "every canonical corpus node implementing corpus-template-datastore "
        "or corpus-template-data-entity"
    ),
    "generate": _generate,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
        {"type": "references", "target": _DATASTORE_TEMPLATE_ID},
        {"type": "references", "target": _DATA_ENTITY_TEMPLATE_ID},
    ),
}

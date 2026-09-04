"""Builder modules for the corpus index/graph generator (issue #633).

One module per generated document, discovered by
launchpad/project-intelligence/corpus/indexes.py in sorted module-name order.
This package deliberately ships EMPTY: each generated document is its own
follow-up issue, and adding one is add-a-file-only -- never an edit to
indexes.py or to another builder's module.

A builder module exposes a module-level ``SPEC``: either a
``corpus_indexes.IndexSpec`` (the framework registers itself in sys.modules as
``corpus_indexes`` before loading builders) or a plain dict/object with the
same fields:

    name           CLI name, used by --only
    output_path    corpus-root-relative .md path, e.g. "generated/api-index.md"
    node_id        front-matter id of the generated node (kebab-case)
    title          the document's H1
    node_type      a node.schema.json type enum value
    audiences      non-empty subset of node.schema.json's audience enum
    subject        one line: what the document is a generated view of
    generate       generate(ctx) -> GeneratedBody or dict with at least
                   'sections' (the listing markdown) and 'includes' (bullets);
                   optionally 'excludes', 'ordering', 'not_covered',
                   'unverified'
    extra_evidence optional: extra_evidence(ctx) -> list of front-matter
                   evidence entries (dicts)
    relationships  optional: ({"type": <forward enum>, "target": <id>}, ...)

``ctx`` is a GenerationContext: corpus_root, nodes / valid_nodes / node_ids,
forward_edges, inverse_edges (the schema's generated inverse types, derived),
broken_edges, orphans, input_digest, output_paths, and rel_path(node).

Modules whose name starts with ``_`` (and this ``__init__.py``) are skipped by
discovery.
"""

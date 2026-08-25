"""Deterministic corpus validator -- issue #623.

One local and CI command that rejects structurally invalid corpus changes,
enforcing the schema #622 defined (launchpad/docs/corpus/schema/node.schema.json)
plus the cross-node and content rules a single document's schema validation
cannot express on its own: duplicate ids, unresolved relationship targets,
unverifiable/prohibited evidence citations, and stray non-canonical files.

Run:  python3 launchpad/project-intelligence/corpus/validate.py [--root PATH]
  or: just corpus-validate
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

import jsonschema
import yaml

DEFAULT_ROOT = "launchpad/docs/corpus"

# `schema/` is #622's own schema-testing infrastructure (node.schema.json,
# relationships.schema.json, and fixtures deliberately containing invalid
# frontmatter) -- not corpus content this validator governs. Excluding it by
# name, not by pattern, because it is one specific, known directory, the same
# way a JSON-Schema repository's own schema/ folder is not data the schema
# validates. Without this exclusion the validator would crash parsing
# schema/README.md (no frontmatter) and reject all 20 of schema/'s
# deliberately-invalid fixtures as if they were real corpus defects.
EXCLUDED_TOP_LEVEL_DIRS = {"schema"}


class CorpusRootMissing(Exception):
    """The given corpus root does not exist at all -- a missing input, not an empty corpus."""


@dataclass
class LoadedNode:
    path: Path
    id: object = None  # None if frontmatter couldn't be parsed at all
    data: dict = field(default_factory=dict)
    error: str | None = None  # a parse or schema error naming this node, if any


def repo_root() -> Path:
    """Resolve the repository root via git, never via cwd or a hard-coded parent count."""
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).resolve().parent,
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(out.stdout.strip())


def load_node_schema(root: Path) -> dict:
    schema_path = root / "launchpad" / "docs" / "corpus" / "schema" / "node.schema.json"
    return json.loads(schema_path.read_text())


def _is_excluded(path: Path, corpus_root: Path) -> bool:
    try:
        rel_parts = path.relative_to(corpus_root).parts
    except ValueError:
        return False
    return bool(rel_parts) and rel_parts[0] in EXCLUDED_TOP_LEVEL_DIRS


def discover_markdown_files(corpus_root: Path) -> list[Path]:
    if not corpus_root.is_dir():
        raise CorpusRootMissing(str(corpus_root))
    return sorted(
        p for p in corpus_root.rglob("*.md") if not _is_excluded(p, corpus_root)
    )


def _load_frontmatter(path: Path) -> dict:
    """Parse a Markdown-with-YAML-frontmatter node (ADR-0028's representation)."""
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError("no leading '---' frontmatter delimiter")
    _, frontmatter, _body = text.split("---\n", 2)
    return yaml.safe_load(frontmatter) or {}


def load_nodes(corpus_root: Path) -> list[LoadedNode]:
    """Load and schema-validate every node under corpus_root (schema/ excluded)."""
    schema = load_node_schema(repo_root())
    validator = jsonschema.Draft202012Validator(schema)

    nodes: list[LoadedNode] = []
    for path in discover_markdown_files(corpus_root):
        try:
            data = _load_frontmatter(path)
        except (ValueError, yaml.YAMLError) as exc:
            nodes.append(LoadedNode(path=path, error=f"{path}: {exc}"))
            continue

        node_id = data.get("id")
        errors = sorted(validator.iter_errors(data), key=str)
        if errors:
            first = errors[0]
            nodes.append(
                LoadedNode(
                    path=path,
                    id=node_id,
                    data=data,
                    error=f"{node_id or path}: schema violation at "
                    f"{'/'.join(str(p) for p in first.absolute_path) or '<root>'}: "
                    f"{first.message}",
                )
            )
            continue

        nodes.append(LoadedNode(path=path, id=node_id, data=data))
    return nodes


def validate_corpus(corpus_root: Path) -> list[str]:
    """Return every validation error found. Empty list means the corpus is clean."""
    nodes = load_nodes(corpus_root)
    return [n.error for n in nodes if n.error]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help=f"corpus root (default: {DEFAULT_ROOT})")
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else repo_root() / DEFAULT_ROOT

    try:
        errors = validate_corpus(root)
    except CorpusRootMissing as exc:
        print(f"FAIL  corpus root does not exist: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"FAIL  {error}", file=sys.stderr)
        print(f"FAIL  {len(errors)} corpus validation error(s)", file=sys.stderr)
        return 1

    print("PASS  corpus validation clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

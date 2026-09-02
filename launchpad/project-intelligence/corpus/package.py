"""Package the canonical documentation corpus into one generated JSON
artifact -- issue #552.

This is the out-of-band generation step `launchpad/crates/knowledge/AGENTS.md`'s
"one rule" requires: it runs once, by a human or CI, and commits its output. It
reuses `validate.load_nodes()` for discovery/parsing rather than
re-implementing corpus walking or YAML parsing (`validate.py` already owns
that). Neither the `knowledge` crate's Rust build nor the desktop build
invokes this script -- see `launchpad/crates/knowledge/AGENTS.md`.

Run:  python3 launchpad/project-intelligence/corpus/package.py
  or: just knowledge-package
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

DEFAULT_CORPUS_ROOT = "launchpad/docs/corpus"

# Two committed copies from the same generation run: the crate's own copy,
# and an identical desktop-facing copy the Settings panel imports directly
# (step 5, launchpad/plans/2026-08-28-issue-552-knowledge-crate-corpus.md) --
# a static asset rather than new Tauri IPC wiring, since #551's own AGENTS.md
# leaves the crate unreachable from desktop/src-tauri without editing a file
# ADR-0045's granted exception does not cover.
DEFAULT_OUTPUTS = (
    "launchpad/crates/knowledge/generated/corpus.json",
    "desktop/src/launchpad/settings/knowledge/generated/corpus.json",
)

# package.py lives in a directory (project-intelligence/corpus/) that isn't a
# package (no __init__.py, matching this repo's existing project-intelligence/
# convention -- see corpus/tests/test_validate.py), so validate.py is loaded
# by path rather than imported by dotted name.
_VALIDATE_PATH = Path(__file__).resolve().parent / "validate.py"
_spec = importlib.util.spec_from_file_location("corpus_validate", _VALIDATE_PATH)
validate = importlib.util.module_from_spec(_spec)
sys.modules["corpus_validate"] = validate
_spec.loader.exec_module(validate)


class PackagingError(Exception):
    """A node failed to load, parse, or schema-validate and cannot be safely
    packaged. Packaging refuses to run rather than silently dropping the
    offending node -- a dropped node would make the generated artifact look
    complete while quietly missing content."""


def _extract_body(text: str) -> str:
    """Everything after the closing '---' of the YAML frontmatter block.

    `validate.load_nodes` already proved this file starts with the leading
    '---\\n' delimiter and parses as YAML frontmatter (a node reaching this
    function has no `error` set), so the same split `_load_frontmatter` uses
    is safe to repeat here for the body half it doesn't return.
    """
    _, _frontmatter, body = text.split("---\n", 2)
    return body.lstrip("\n")


# Fields copied from each node's validated frontmatter into the packaged
# artifact, in the order node.schema.json declares them. `relationships` is
# optional in the schema (a node may have none), so it defaults to `[]` rather
# than being omitted -- keeping every packaged node's shape uniform for
# consumers.
_PACKAGED_FIELDS = ("id", "type", "status", "origin", "audiences", "evidence")


def package_corpus(corpus_root: Path) -> list[dict]:
    """Build the packaged node list, sorted by `id` for determinism.

    Raises `PackagingError` naming every node that failed to load or
    schema-validate, rather than silently omitting it -- a corpus change that
    breaks one node must fail packaging, not ship a quietly incomplete
    artifact.
    """
    nodes = validate.load_nodes(corpus_root)

    failed = [node for node in nodes if node.error]
    if failed:
        raise PackagingError(
            "refusing to package -- the following node(s) failed to load or "
            "validate: " + "; ".join(node.error for node in failed)
        )

    packaged = []
    for node in nodes:
        entry = {field: node.data[field] for field in _PACKAGED_FIELDS}
        entry["relationships"] = node.data.get("relationships", [])
        entry["body"] = _extract_body(node.path.read_text(encoding="utf-8"))
        packaged.append(entry)

    packaged.sort(key=lambda entry: entry["id"])
    return packaged


def generate_corpus_json(corpus_root: Path) -> str:
    """The packaged corpus, serialized deterministically (sorted keys, sorted
    node order, trailing newline) so two runs against unchanged input produce
    byte-identical output -- what the drift guard compares against."""
    packaged = package_corpus(corpus_root)
    return json.dumps(packaged, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help=f"corpus root (default: {DEFAULT_CORPUS_ROOT})")
    parser.add_argument(
        "--out",
        action="append",
        default=None,
        help="output path, repo-relative or absolute (repeatable); "
        f"default: {', '.join(DEFAULT_OUTPUTS)}",
    )
    args = parser.parse_args(argv)

    repo_root = validate.repo_root()
    root = Path(args.root) if args.root else repo_root / DEFAULT_CORPUS_ROOT
    outputs = args.out if args.out else list(DEFAULT_OUTPUTS)

    try:
        content = generate_corpus_json(root)
    except validate.CorpusRootMissing as exc:
        print(f"FAIL  corpus root does not exist: {exc}", file=sys.stderr)
        return 1
    except PackagingError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    node_count = len(json.loads(content))
    for out in outputs:
        out_path = Path(out)
        if not out_path.is_absolute():
            out_path = repo_root / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(content, encoding="utf-8")
        print(f"wrote {node_count} node(s) to {out_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

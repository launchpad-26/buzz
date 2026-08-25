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
from pathlib import Path, PurePosixPath

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


def find_duplicate_ids(nodes: list[LoadedNode]) -> list[str]:
    """Every node's `id` must be unique across the corpus."""
    paths_by_id: dict[object, list[Path]] = {}
    for node in nodes:
        if node.id is None:
            continue
        paths_by_id.setdefault(node.id, []).append(node.path)

    errors = []
    for node_id, paths in paths_by_id.items():
        if len(paths) > 1:
            joined = ", ".join(str(p) for p in paths)
            errors.append(f"{node_id}: duplicate id used by {len(paths)} nodes: {joined}")
    return errors


def find_unresolved_relationship_targets(nodes: list[LoadedNode]) -> list[str]:
    """Every `relationships[].target` must match some loaded node's `id`.

    Nodes with `node.error` already set (a schema violation, e.g. a malformed
    `relationships` entry) are skipped here -- they're already reported, and their
    unvalidated `data` isn't safe to assume well-shaped. The `isinstance` guard is
    defense-in-depth on top of that, not the primary protection: node.schema.json
    already requires each relationship to be an object, so a schema-invalid node
    is the only way a non-dict entry reaches here at all.
    """
    known_ids = {node.id for node in nodes if node.id is not None}

    errors = []
    for node in nodes:
        if node.error:
            continue
        for relationship in node.data.get("relationships") or []:
            if not isinstance(relationship, dict):
                continue
            target = relationship.get("target")
            if target is not None and target not in known_ids:
                errors.append(
                    f"{node.id or node.path}: relationship target {target!r} "
                    "does not match any known node id"
                )
    return errors


# A SHORT, EXACT list of credential-shaped filenames/extensions -- deliberately NOT
# broad substring words like *auth*/*token*/*secret*/*credential*. An earlier draft
# of this validator's plan proposed exactly those substrings; serina:review-plan
# caught that *auth* alone would reject `crates/buzz-auth/...`, a real, ordinary,
# non-secret crate this repo publicly ships. Short substring wildcards over
# legitimate source paths are exactly the "match on exact names, never sweep with a
# wildcard" mistake this project's own credential-handling rule warns about.
_CREDENTIAL_LIKE_BASENAME_PREFIXES = ("id_rsa", "id_ed25519")
_CREDENTIAL_LIKE_EXTENSIONS = {".pem", ".key"}
# Conventional non-secret .env suffixes -- exempted so a real, tracked, public
# template like .env.example (this repo's own AGENTS.md says `cp .env.example
# .env`) is never rejected as a prohibited credential. The same over-broad-match
# mistake already caught once for crates/buzz-auth, recurring here for .env
# specifically until an independent review-code pass found it.
_ENV_SAFE_SUFFIXES = (".example", ".sample", ".template")


def _is_prohibited_citation(citation: str) -> bool:
    name = PurePosixPath(citation).name
    if name == ".env":
        return True
    if name.startswith(".env.") and not name.endswith(_ENV_SAFE_SUFFIXES):
        return True
    if any(name.startswith(prefix) for prefix in _CREDENTIAL_LIKE_BASENAME_PREFIXES):
        return True
    if PurePosixPath(citation).suffix in _CREDENTIAL_LIKE_EXTENSIONS:
        return True
    if ".ssh" in PurePosixPath(citation).parts:
        return True
    return False


def find_citation_problems(nodes: list[LoadedNode], repo_root_path: Path) -> list[str]:
    """Every evidence citation is either a URL, a prohibited credential-like path
    (rejected without echoing it -- the DoD's "without leaking private source
    content"), or a repo-relative path that must resolve to a real file.

    URLs are checked FIRST, before the credential blocklist -- a public URL whose
    path happens to contain a blocklisted substring (e.g. a blog post titled
    "id_rsa-security-best-practices") must still be accepted as-is, per this
    validator's plan. Checking the blocklist first (an earlier revision did)
    silently rejected such URLs, contradicting that stated rule.

    ADR-0003's citation convention is a commit-pinned markdown link -- a URL --
    never a bare commit hash, so a bare SHA is correctly treated as a
    repo-relative path and rejected as non-existent: it isn't an
    ADR-0003-compliant citation either way.

    An absolute path (e.g. /etc/passwd) is rejected explicitly rather than
    existence-checked: pathlib's `/` operator silently discards the left operand
    when the right is absolute, so `repo_root_path / "/etc/passwd"` would
    otherwise evaluate to `/etc/passwd` itself and "validate" against the host
    filesystem instead of the repo.

    Nodes with `node.error` already set are skipped -- see
    find_unresolved_relationship_targets's docstring for why.
    """
    errors = []
    for node in nodes:
        if node.error:
            continue
        for entry in node.data.get("evidence") or []:
            if not isinstance(entry, dict):
                continue
            for citation in entry.get("evidence") or []:
                if not isinstance(citation, str):
                    continue
                if citation.startswith("http://") or citation.startswith("https://"):
                    continue
                if _is_prohibited_citation(citation):
                    errors.append(
                        f"{node.id or node.path}: an evidence citation matches a "
                        "prohibited credential-like pattern"
                    )
                    continue
                if PurePosixPath(citation).is_absolute():
                    errors.append(
                        f"{node.id or node.path}: an evidence citation must be a "
                        "repo-relative path, not absolute"
                    )
                    continue
                if not (repo_root_path / citation).exists():
                    errors.append(
                        f"{node.id or node.path}: an evidence citation does not "
                        "resolve to a real file"
                    )
    return errors


def find_ownership_violations(corpus_root: Path) -> list[str]:
    """Every non-`.md` file (schema/ excluded) must live under a `generated/`
    subdirectory -- ADR-0028's canonical-vs-generated boundary: hand-authored
    content is Markdown+frontmatter, anything else must be clearly segregated as a
    generated projection, never interleaved with authored nodes."""
    errors = []
    for path in sorted(corpus_root.rglob("*")):
        if path.is_dir() or path.suffix == ".md" or _is_excluded(path, corpus_root):
            continue
        rel = path.relative_to(corpus_root)
        if "generated" in rel.parts[:-1]:
            continue
        errors.append(
            f"{rel}: non-.md file outside generated/ -- misplaced generated "
            "artifact, or hand-authored content in the wrong format"
        )
    return errors


def validate_corpus(corpus_root: Path) -> list[str]:
    """Return every validation error found. Empty list means the corpus is clean."""
    root = repo_root()
    nodes = load_nodes(corpus_root)
    errors = [n.error for n in nodes if n.error]
    errors.extend(find_duplicate_ids(nodes))
    errors.extend(find_unresolved_relationship_targets(nodes))
    errors.extend(find_citation_problems(nodes, root))
    errors.extend(find_ownership_violations(corpus_root))
    return errors


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

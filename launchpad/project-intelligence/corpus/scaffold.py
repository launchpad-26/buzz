"""One-node corpus scaffold helper -- issue #632.

Creates exactly one corpus Markdown file from a manifest row (#626), with
front matter populated only from values `scaffold_node`'s caller supplies
and `node.schema.json` itself validates against -- never invented. It
leaves all SUBSTANTIVE evidence to the authoring skill (#629): the one
`evidence` entry this module writes is the provenance/revision citation
`launchpad/docs/corpus/AGENTS.md`'s "Creating a node" step 6 describes as
mechanical ("Run `git cat-file -e <sha>`... and the entry is a FACT"), never
a claim about the node's subject.

`type`, `origin`, `status` and `audiences` are validated against the actual
enums in `node.schema.json` -- read from the file at call time, not
hardcoded here, so this module can never silently drift from the schema it
is scaffolding against. `id` is derived from the manifest row's filename and
validated against the schema's own kebab-case pattern.

"Unknown templates fail closed" (#632's definition of done) is implemented
by reading the real template registry: every `*.md` file directly under
`launchpad/docs/corpus/templates/`. That directory does not exist yet in
this repository (issue #605's templates track is still landing), so today
every call correctly refuses with "unknown template" -- not a bug in this
module, an accurate reflection of what has and hasn't merged. It starts
recognising templates automatically as issue #605 lands them, with no
change needed here.

Run as a library -- there is no CLI; `scaffold_node` is the entry point
tests and future callers (the corpus-plan skill, issue #628) use.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import yaml

_CORPUS_DIR = Path(__file__).resolve().parent
_MANIFEST_PATH = _CORPUS_DIR / "manifest.py"
_spec = importlib.util.spec_from_file_location("corpus_manifest", _MANIFEST_PATH)
manifest = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("corpus_manifest", manifest)
_spec.loader.exec_module(manifest)

_ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# Corpus placement rule from AGENTS.md: "Anywhere under launchpad/docs/corpus/,
# except schema/ -- that subtree is the schema's own testing infrastructure
# and is deliberately skipped by the checker." Enforced here too, so a
# scaffolded node is never created somewhere validate.py will never see it.
_CORPUS_ROOT_PREFIX = "launchpad/docs/corpus/"
_EXCLUDED_SUBTREE_PREFIX = _CORPUS_ROOT_PREFIX + "schema/"

_TEMPLATES_DIR_RELATIVE = "launchpad/docs/corpus/templates"


class ScaffoldError(Exception):
    """A scaffold request cannot be satisfied -- always fails closed, never guesses."""


def load_node_schema(root: Path) -> dict:
    schema_path = root / "launchpad" / "docs" / "corpus" / "schema" / "node.schema.json"
    return json.loads(schema_path.read_text())


def _known_templates(root: Path) -> frozenset[str]:
    templates_dir = root / _TEMPLATES_DIR_RELATIVE
    if not templates_dir.is_dir():
        return frozenset()
    return frozenset(p.stem for p in templates_dir.glob("*.md"))


def scaffold_node(
    root: Path,
    row: "manifest.ManifestRow",
    *,
    node_type: str,
    origin: str,
    revision: str,
    status: str = "draft",
    mode: str = "create",
) -> Path:
    """Create (or, with mode="update", overwrite) the one file `row` describes.

    Raises ScaffoldError for every way a request can be invalid: an unknown
    template, a type/origin/status/audience value the schema does not
    accept, a path outside the corpus (or inside schema/), a malformed
    derived id, or (in "create" mode) a file that already exists. Nothing
    here falls back to a default when a value is invalid -- fail closed.
    """
    if mode not in {"create", "update"}:
        raise ScaffoldError(f"unknown mode {mode!r}; must be 'create' or 'update'")

    schema = load_node_schema(root)
    valid_types = set(schema["properties"]["type"]["enum"])
    valid_origins = set(schema["properties"]["origin"]["enum"])
    valid_statuses = set(schema["properties"]["status"]["enum"])
    valid_audiences = set(schema["properties"]["audiences"]["items"]["enum"])

    if row.template not in _known_templates(root):
        raise ScaffoldError(
            f"unknown template {row.template!r} -- no "
            f"{_TEMPLATES_DIR_RELATIVE}/{row.template}.md exists yet"
        )
    if node_type not in valid_types:
        raise ScaffoldError(f"unknown type {node_type!r}; schema allows: {sorted(valid_types)}")
    if origin not in valid_origins:
        raise ScaffoldError(f"unknown origin {origin!r}; schema allows: {sorted(valid_origins)}")
    if status not in valid_statuses:
        raise ScaffoldError(f"unknown status {status!r}; schema allows: {sorted(valid_statuses)}")
    unknown_audiences = set(row.audiences) - valid_audiences
    if unknown_audiences:
        raise ScaffoldError(f"unknown audience(s) {sorted(unknown_audiences)}; schema allows: {sorted(valid_audiences)}")
    if not row.audiences:
        raise ScaffoldError("manifest row carries no audiences; schema requires at least one")

    if not row.path.startswith(_CORPUS_ROOT_PREFIX):
        raise ScaffoldError(f"path {row.path!r} is not under {_CORPUS_ROOT_PREFIX}")
    if row.path.startswith(_EXCLUDED_SUBTREE_PREFIX):
        raise ScaffoldError(f"path {row.path!r} is under schema/, which validate.py never checks")

    node_id = Path(row.filename).stem
    if not _ID_PATTERN.match(node_id):
        raise ScaffoldError(f"filename {row.filename!r} does not derive a valid kebab-case id ({node_id!r})")

    target = root / row.path
    if mode == "create" and target.exists():
        raise ScaffoldError(f"{row.path} already exists; pass mode='update' to overwrite deliberately")
    if mode == "update" and not target.exists():
        raise ScaffoldError(f"{row.path} does not exist; mode='update' requires an existing file")

    front_matter = {
        "id": node_id,
        "type": node_type,
        "status": status,
        "origin": origin,
        "audiences": list(row.audiences),
        "evidence": [
            {
                "statement": f"This node was authored and checked against repository revision {revision}.",
                "entry_class": "FACT",
                "evidence": [f"commit {revision}"],
            }
        ],
    }

    yaml_text = yaml.safe_dump(front_matter, sort_keys=False, default_flow_style=False)
    body = (
        f"\n# {row.purpose}\n\n"
        "<!-- Scaffolded by scaffold.py (#632). Front matter is populated; the body,\n"
        "     including all substantive evidence entries above the provenance one, is\n"
        "     left for the corpus-author skill (#629) -- see AGENTS.md's \"Creating a\n"
        "     node\" steps 7-8. -->\n"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f"---\n{yaml_text}---\n{body}")
    return target

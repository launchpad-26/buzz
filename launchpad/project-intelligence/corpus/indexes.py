"""Deterministic corpus index/graph generator framework -- issue #633.

Generates Markdown corpus nodes that are derived views (indexes, graphs, listings)
of the canonical corpus, from canonical nodes only. This module is the FRAMEWORK:
it owns discovery of builder modules, the canonical-input contract, the input
digest, graph derivation (including the generated inverse edges
relationships.schema.json marks `generated`), and the rendering of schema-valid
front matter plus the body skeleton templates/generated-index.md prescribes.

It deliberately ships ZERO builders. Each generated document is its own issue;
adding one is add-a-file-only: drop a module into `index_defs/` exposing a `SPEC`
(see IndexSpec) and never edit this file. Builders are discovered in sorted
module-name order, so extension by parallel tasks cannot collide here.

Canonical inputs reuse validate.py's own "what counts as a node" contract
(discover_markdown_files + load_nodes) rather than inventing a second discovery
that could drift from the one CI checks -- templates/generated-index.md states
that requirement explicitly. Every registered builder's output path is excluded
from the inputs, so a generated view is reproducible from canonical nodes only
and no output ever feeds itself.

Outputs embed a source revision as a sha256 digest over the sorted
(relative path, bytes) of the canonical inputs -- never a timestamp and never a
git HEAD SHA, so a no-change rerun at the same revision is byte-identical.

Run:  python3 launchpad/project-intelligence/corpus/indexes.py --list
  or: ... --all            (regenerate every builder's output)
  or: ... --only NAME      (repeatable; regenerate selected builders)
  or: ... --check [--only NAME]  (diff in-memory regeneration against disk;
                                  nonzero exit on any difference)
  or: ... --root PATH --defs-dir PATH   (both for tests)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Callable

# ---------------------------------------------------------------------------
# validate.py is the single source of the node contract. It lives in a
# non-package directory, so it is loaded by path -- the same pattern its own
# test suite uses -- and cached in sys.modules so this module, the tests and
# any builder all see one instance.
# ---------------------------------------------------------------------------
_VALIDATE_PATH = Path(__file__).resolve().parent / "validate.py"


def _load_validate():
    existing = sys.modules.get("corpus_validate")
    if existing is not None:
        return existing
    spec = importlib.util.spec_from_file_location("corpus_validate", _VALIDATE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["corpus_validate"] = module
    spec.loader.exec_module(module)
    return module


validate = _load_validate()

# Builder modules are loaded by path, so they cannot `import indexes` by dotted
# name. This alias lets a builder write `import corpus_indexes` if it wants the
# dataclasses; plain dicts with the same fields are equally accepted, so a
# builder can also depend on nothing at all.
sys.modules.setdefault("corpus_indexes", sys.modules[__name__])

DEFAULT_DEFS_DIR = Path(__file__).resolve().parent / "index_defs"
GENERATOR_PATH = "launchpad/project-intelligence/corpus/indexes.py"

_NODE_ID_RE = validate._SAFE_ID_RE


class SpecError(Exception):
    """A builder module's SPEC (or its generated body) violates the contract."""


# ---------------------------------------------------------------------------
# Schema-derived vocabularies. Read from the committed schemas, never
# hand-maintained here, so this framework cannot drift from what the validator
# enforces -- including which inverse relationship types are `generated`.
# ---------------------------------------------------------------------------
_ENUM_CACHE: dict[str, object] = {}


def _schema_enums() -> dict[str, object]:
    if _ENUM_CACHE:
        return _ENUM_CACHE
    root = validate.repo_root()
    node_schema = validate.load_node_schema(root)
    relationships_schema = json.loads(
        (
            root / "launchpad" / "docs" / "corpus" / "schema" / "relationships.schema.json"
        ).read_text()
    )
    meta = relationships_schema["relationshipMeta"]
    _ENUM_CACHE.update(
        {
            "types": frozenset(node_schema["properties"]["type"]["enum"]),
            "audiences": frozenset(
                node_schema["properties"]["audiences"]["items"]["enum"]
            ),
            "relationship_types": frozenset(
                node_schema["$defs"]["relationship"]["properties"]["type"]["enum"]
            ),
            # forward type -> generated inverse name, derived from the schema's
            # own `inverse: generated` markers (currently depended-on-by,
            # superseded-by, implemented-by, has-part; referenced-by is
            # `authored` and therefore never derived here).
            "generated_inverses": {
                forward: m["inverseType"]
                for forward, m in sorted(meta.items())
                if m.get("inverse") == "generated"
            },
        }
    )
    return _ENUM_CACHE


# ---------------------------------------------------------------------------
# The SPEC contract a builder module exposes, and the body it returns.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class IndexSpec:
    """One builder's declaration. A builder module exposes SPEC as an IndexSpec,
    or as any object/dict carrying the same fields -- both are accepted."""

    name: str  # CLI name (--only NAME)
    output_path: str  # corpus-root-relative posix path, e.g. "generated/api-index.md"
    node_id: str  # front-matter `id` of the generated node
    title: str  # H1 / document title
    node_type: str  # front-matter `type`; must be a node.schema.json enum value
    audiences: tuple[str, ...]  # front-matter `audiences`
    subject: str  # one line: what this document is a generated view of
    generate: Callable  # generate(ctx) -> GeneratedBody (or equivalent dict)
    extra_evidence: Callable | None = None  # extra_evidence(ctx) -> list[dict]
    relationships: tuple = ()  # front-matter relationships: ({"type","target"},...)
    # Module path recorded by discovery; builders never set this themselves.
    module_path: Path | None = field(default=None, compare=False)


@dataclass(frozen=True)
class GeneratedBody:
    """What generate(ctx) returns: the subject-specific parts of the body.
    The framework renders everything around them."""

    sections: str  # the listing itself (one or more markdown sections)
    includes: tuple[str, ...]  # bullets: what qualifies an item for a listing entry
    excludes: tuple[str, ...] = ()  # bullets: what is deliberately left out
    ordering: str = (
        "canonical inputs are provided in sorted path order; the listing states "
        "its own sort rule inline"
    )
    not_covered: tuple[str, ...] = ()  # extra "It does not cover" bullets
    unverified: tuple[str, ...] = ()  # extra "Expected but not verified" bullets


@dataclass(frozen=True)
class Edge:
    source: str  # source node id
    type: str  # forward relationship type
    target: str  # declared target id


@dataclass(frozen=True)
class BrokenEdge:
    source: str  # source node id, or its path label if the id is unusable
    type: str
    target: str  # the declared target that resolves to no node id


@dataclass(frozen=True)
class GenerationContext:
    """Everything a builder's generate(ctx) may read. All sequences are sorted
    deterministically; all content derives from canonical inputs only."""

    corpus_root: Path
    nodes: tuple  # every canonical LoadedNode (sorted path order), errors included
    valid_nodes: tuple  # the subset with node.error is None
    node_ids: tuple  # sorted ids of valid nodes
    forward_edges: tuple  # Edge, sorted (source, type, target)
    inverse_edges: dict  # generated-inverse type -> {node id -> (source ids, sorted)}
    broken_edges: tuple  # BrokenEdge, sorted -- reported, never a crash
    orphans: tuple  # sorted ids of valid nodes with no in- or out-edges
    input_digest: str  # sha256 hex over sorted (rel path, bytes) of canonical inputs
    output_paths: tuple  # every registered builder's output_path, sorted

    def rel_path(self, node) -> str:
        """A node's corpus-root-relative posix path, for listings."""
        return node.path.relative_to(self.corpus_root).as_posix()


# ---------------------------------------------------------------------------
# Builder discovery
# ---------------------------------------------------------------------------
def _spec_field(raw, name: str, module_path: Path):
    if isinstance(raw, dict):
        if name not in raw:
            raise SpecError(f"{module_path.name}: SPEC is missing field {name!r}")
        return raw[name]
    if not hasattr(raw, name):
        raise SpecError(f"{module_path.name}: SPEC is missing field {name!r}")
    return getattr(raw, name)


def _spec_optional(raw, name: str, default):
    if isinstance(raw, dict):
        return raw.get(name, default)
    return getattr(raw, name, default)


def _coerce_spec(raw, module_path: Path) -> IndexSpec:
    """Normalize and validate one module's SPEC. Every rejection names the
    module, so a bad builder in a batch of thirty is findable."""
    enums = _schema_enums()

    def fail(detail: str) -> SpecError:
        return SpecError(f"{module_path.name}: SPEC {detail}")

    name = _spec_field(raw, "name", module_path)
    if not isinstance(name, str) or not name:
        raise fail("field 'name' must be a non-empty string")

    output_path = _spec_field(raw, "output_path", module_path)
    if not isinstance(output_path, str) or not output_path.endswith(".md"):
        raise fail("field 'output_path' must be a corpus-root-relative .md path")
    pure = PurePosixPath(output_path)
    if pure.is_absolute() or ".." in pure.parts:
        raise fail("field 'output_path' must stay inside the corpus root")

    node_id = _spec_field(raw, "node_id", module_path)
    if not isinstance(node_id, str) or not _NODE_ID_RE.match(node_id):
        raise fail("field 'node_id' must be a kebab-case node id")

    title = _spec_field(raw, "title", module_path)
    if not isinstance(title, str) or not title.strip():
        raise fail("field 'title' must be a non-empty string")

    node_type = _spec_field(raw, "node_type", module_path)
    if node_type not in enums["types"]:
        raise fail(
            "field 'node_type' must be one of node.schema.json's type enum values"
        )

    audiences = tuple(_spec_field(raw, "audiences", module_path))
    if not audiences or any(a not in enums["audiences"] for a in audiences):
        raise fail(
            "field 'audiences' must be a non-empty subset of node.schema.json's "
            "audience enum"
        )

    subject = _spec_field(raw, "subject", module_path)
    if not isinstance(subject, str) or not subject.strip() or "\n" in subject:
        raise fail("field 'subject' must be one non-empty line")

    generate = _spec_field(raw, "generate", module_path)
    if not callable(generate):
        raise fail("field 'generate' must be callable")

    extra_evidence = _spec_optional(raw, "extra_evidence", None)
    if extra_evidence is not None and not callable(extra_evidence):
        raise fail("field 'extra_evidence' must be callable when present")

    relationships = tuple(_spec_optional(raw, "relationships", ()) or ())
    for rel in relationships:
        if (
            not isinstance(rel, dict)
            or set(rel) != {"type", "target"}
            or rel["type"] not in enums["relationship_types"]
            or not isinstance(rel["target"], str)
            or not _NODE_ID_RE.match(rel["target"])
        ):
            raise fail(
                "field 'relationships' entries must be {'type': <forward enum "
                "value>, 'target': <kebab-case id>} -- inverse edge names are "
                "generated, never authored (relationships.schema.json)"
            )

    return IndexSpec(
        name=name,
        output_path=pure.as_posix(),
        node_id=node_id,
        title=title.strip(),
        node_type=node_type,
        audiences=audiences,
        subject=subject.strip(),
        generate=generate,
        extra_evidence=extra_evidence,
        relationships=relationships,
        module_path=module_path,
    )


def discover_builders(defs_dir: Path | None = None) -> list[IndexSpec]:
    """Load every builder module under `defs_dir` (default index_defs/), in
    sorted module-name order, and return their validated SPECs.

    One module = one builder. `__init__.py` and `_`-prefixed modules are
    skipped. Duplicate builder names or output paths across modules are a hard
    error -- two parallel follow-up tasks colliding must fail loudly, not have
    one silently shadow the other."""
    directory = defs_dir if defs_dir is not None else DEFAULT_DEFS_DIR
    if not directory.is_dir():
        return []

    specs: list[IndexSpec] = []
    for module_path in sorted(directory.glob("*.py"), key=lambda p: p.name):
        if module_path.name == "__init__.py" or module_path.name.startswith("_"):
            continue
        module_name = f"corpus_index_def_{module_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except SpecError:
            raise
        except Exception as exc:  # a broken builder must name itself
            raise SpecError(f"{module_path.name}: failed to import ({exc})") from exc
        raw = getattr(module, "SPEC", None)
        if raw is None:
            raise SpecError(f"{module_path.name}: module exposes no SPEC")
        specs.append(_coerce_spec(raw, module_path))

    seen_names: dict[str, str] = {}
    seen_outputs: dict[str, str] = {}
    for s in specs:
        module_name = s.module_path.name if s.module_path else "<unknown>"
        if s.name in seen_names:
            raise SpecError(
                f"duplicate builder name {s.name!r} in {seen_names[s.name]} "
                f"and {module_name}"
            )
        if s.output_path in seen_outputs:
            raise SpecError(
                f"duplicate output_path {s.output_path!r} in "
                f"{seen_outputs[s.output_path]} and {module_name}"
            )
        seen_names[s.name] = module_name
        seen_outputs[s.output_path] = module_name
    return specs


# ---------------------------------------------------------------------------
# Canonical inputs and the graph
# ---------------------------------------------------------------------------
def canonical_input_paths(corpus_root: Path, specs: list[IndexSpec]) -> list[Path]:
    """Every corpus node file, per validate.py's discovery contract, minus every
    registered builder's output path. Sorted (discovery already sorts)."""
    excluded = {s.output_path for s in specs}
    return [
        p
        for p in validate.discover_markdown_files(corpus_root)
        if p.relative_to(corpus_root).as_posix() not in excluded
    ]


def compute_input_digest(corpus_root: Path, paths: list[Path]) -> str:
    """sha256 over sorted (relative posix path, bytes) of the canonical inputs.
    No timestamps, no git state -- same inputs, same digest, byte-identical
    outputs on a no-change rerun."""
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: p.relative_to(corpus_root).as_posix()):
        digest.update(path.relative_to(corpus_root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_context(corpus_root: Path, specs: list[IndexSpec]) -> GenerationContext:
    """Load canonical nodes and derive the graph. Broken edges (targets that
    resolve to no node id) are reported, never raised; builders decide how to
    render them. Orphans are valid nodes with no in- or out-edges."""
    excluded = {s.output_path for s in specs}
    input_paths = canonical_input_paths(corpus_root, specs)
    nodes = tuple(
        node
        for node in validate.load_nodes(corpus_root)
        if node.path.relative_to(corpus_root).as_posix() not in excluded
    )
    valid_nodes = tuple(n for n in nodes if n.error is None)
    known_ids = {n.id for n in valid_nodes if isinstance(n.id, str)}

    forward: list[Edge] = []
    broken: list[BrokenEdge] = []
    enums = _schema_enums()
    for node in valid_nodes:
        source = node.id if isinstance(node.id, str) else str(
            node.path.relative_to(corpus_root)
        )
        for rel in node.data.get("relationships") or []:
            if not isinstance(rel, dict):
                continue
            rel_type = rel.get("type")
            target = rel.get("target")
            if not isinstance(rel_type, str) or not isinstance(target, str):
                continue
            if target in known_ids:
                forward.append(Edge(source=source, type=rel_type, target=target))
            else:
                broken.append(BrokenEdge(source=source, type=rel_type, target=target))

    forward.sort(key=lambda e: (e.source, e.type, e.target))
    broken.sort(key=lambda e: (e.source, e.type, e.target))

    generated_inverses: dict[str, str] = enums["generated_inverses"]
    inverse_edges: dict[str, dict[str, tuple]] = {
        inverse_type: {} for inverse_type in sorted(generated_inverses.values())
    }
    accumulating: dict[str, dict[str, set]] = {
        inverse_type: {} for inverse_type in generated_inverses.values()
    }
    for edge in forward:
        inverse_type = generated_inverses.get(edge.type)
        if inverse_type is None:
            continue  # `references` -> referenced-by is authored, never derived
        accumulating[inverse_type].setdefault(edge.target, set()).add(edge.source)
    for inverse_type, by_target in accumulating.items():
        inverse_edges[inverse_type] = {
            target: tuple(sorted(sources))
            for target, sources in sorted(by_target.items())
        }

    has_out = {e.source for e in forward} | {e.source for e in broken}
    has_in = {e.target for e in forward}
    orphans = tuple(sorted(known_ids - has_out - has_in))

    return GenerationContext(
        corpus_root=corpus_root,
        nodes=nodes,
        valid_nodes=valid_nodes,
        node_ids=tuple(sorted(known_ids)),
        forward_edges=tuple(forward),
        inverse_edges=inverse_edges,
        broken_edges=tuple(broken),
        orphans=orphans,
        input_digest=compute_input_digest(corpus_root, input_paths),
        output_paths=tuple(sorted(s.output_path for s in specs)),
    )


# ---------------------------------------------------------------------------
# Rendering. The framework, not the builder, renders front matter and the
# standard skeleton templates/generated-index.md prescribes.
# ---------------------------------------------------------------------------
_EVIDENCE_KEY_ORDER = ("statement", "entry_class", "evidence", "confidence", "provided_by")


def _yaml_str(value: str) -> str:
    # JSON string syntax is a YAML subset; json.dumps gives one deterministic,
    # always-safe quoting for every scalar this framework emits.
    return json.dumps(value, ensure_ascii=False)


def _render_evidence_entry(entry: dict, lines: list[str]) -> None:
    unknown = set(entry) - set(_EVIDENCE_KEY_ORDER)
    if unknown:
        raise SpecError(
            f"evidence entry carries unknown field(s): {sorted(unknown)}"
        )
    first = True
    for key in _EVIDENCE_KEY_ORDER:
        if key not in entry:
            continue
        prefix = "  - " if first else "    "
        first = False
        value = entry[key]
        if key == "evidence":
            lines.append(f"{prefix}{key}:")
            for citation in value:
                lines.append(f"      - {_yaml_str(citation)}")
        elif key == "confidence":
            lines.append(f"{prefix}{key}: {json.dumps(value)}")
        else:
            lines.append(f"{prefix}{key}: {_yaml_str(value)}")


def _builder_module_citation(spec: IndexSpec) -> str:
    """Cite the builder module by repo-relative path when it lives in this
    repository; otherwise fall back to CONTRACT.md's tool-result citation form,
    which the validator reports UNVERIFIED rather than rejecting."""
    if spec.module_path is not None:
        try:
            return spec.module_path.resolve().relative_to(
                validate.repo_root().resolve()
            ).as_posix()
        except ValueError:
            pass
    return (
        f"discover_builders({spec.name!r}) -> builder module resolved outside "
        "this repository"
    )


def _framework_evidence(spec: IndexSpec, ctx: GenerationContext) -> list[dict]:
    entries = [
        {
            "statement": (
                f"This document was generated by {GENERATOR_PATH} from "
                f"{len(ctx.nodes)} canonical corpus node(s); input digest "
                f"sha256:{ctx.input_digest}."
            ),
            "entry_class": "FACT",
            "evidence": [GENERATOR_PATH],
        },
        {
            "statement": (
                f"The subject-specific listing was produced by builder "
                f"{spec.name!r}; the framework rendered the front matter and "
                "body skeleton."
            ),
            "entry_class": "FACT",
            "evidence": [_builder_module_citation(spec)],
        },
    ]
    if spec.extra_evidence is not None:
        extra = spec.extra_evidence(ctx)
        if not isinstance(extra, (list, tuple)):
            raise SpecError(
                f"{spec.name}: extra_evidence(ctx) must return a list of entries"
            )
        entries.extend(extra)
    return entries


def _render_front_matter(spec: IndexSpec, ctx: GenerationContext) -> str:
    lines = ["---"]
    lines.append(f"id: {_yaml_str(spec.node_id)}")
    lines.append(f"type: {_yaml_str(spec.node_type)}")
    lines.append('status: "draft"')
    lines.append('origin: "launchpad"')
    lines.append("audiences:")
    for audience in spec.audiences:
        lines.append(f"  - {_yaml_str(audience)}")
    lines.append("evidence:")
    for entry in _framework_evidence(spec, ctx):
        _render_evidence_entry(entry, lines)
    if spec.relationships:
        lines.append("relationships:")
        for rel in spec.relationships:
            lines.append(f"  - type: {_yaml_str(rel['type'])}")
            lines.append(f"    target: {_yaml_str(rel['target'])}")
    lines.append("---")
    return "\n".join(lines)


def _coerce_body(raw, spec: IndexSpec) -> GeneratedBody:
    if isinstance(raw, GeneratedBody):
        return raw

    def get(name: str, default=None):
        if isinstance(raw, dict):
            return raw.get(name, default)
        return getattr(raw, name, default)

    sections = get("sections")
    includes = get("includes")
    if not isinstance(sections, str) or not sections.strip():
        raise SpecError(f"{spec.name}: generate(ctx) returned no 'sections' text")
    if not includes:
        raise SpecError(f"{spec.name}: generate(ctx) returned no 'includes' bullets")
    defaults = GeneratedBody(sections="x", includes=("x",))
    return GeneratedBody(
        sections=sections,
        includes=tuple(includes),
        excludes=tuple(get("excludes", ()) or ()),
        ordering=get("ordering", defaults.ordering) or defaults.ordering,
        not_covered=tuple(get("not_covered", ()) or ()),
        unverified=tuple(get("unverified", ()) or ()),
    )


def render_document(spec: IndexSpec, ctx: GenerationContext) -> str:
    """Render one builder's complete document: front matter + the standard body
    skeleton (templates/generated-index.md) around the builder's own sections.
    LF line endings, exactly one trailing newline, no timestamps."""
    body = _coerce_body(spec.generate(ctx), spec)
    module_citation = _builder_module_citation(spec)

    parts: list[str] = [_render_front_matter(spec, ctx), ""]
    parts.append(f"# {spec.title}")
    parts.append("")
    parts.append(
        f"> **Generated -- do not edit by hand.** Produced by `{GENERATOR_PATH}`"
    )
    parts.append(
        f"> (builder `{spec.name}`), from the canonical corpus nodes under the"
    )
    parts.append(
        "> corpus root, excluding every registered generated output. Edits made"
    )
    parts.append(
        "> directly to this file are overwritten on the next regeneration; change"
    )
    parts.append("> the generator or its inputs instead.")
    parts.append("")
    parts.append("## Generator")
    parts.append("")
    parts.append(
        f"- **Script**: `{GENERATOR_PATH}` (builder `{spec.name}`, `{module_citation}`)"
    )
    parts.append(
        f"- **Inputs**: the {len(ctx.nodes)} canonical corpus node(s) discovered "
        "by `validate.py`'s"
    )
    parts.append(
        "  `discover_markdown_files` contract (sorted walk, `schema/` excluded, "
        "symlinks resolved),"
    )
    parts.append(
        f"  minus the {len(ctx.output_paths)} registered generated output path(s)"
    )
    parts.append(f"- **Ordering**: {body.ordering}")
    parts.append(
        f"- **Source revision**: input digest `sha256:{ctx.input_digest}` over the"
    )
    parts.append("  sorted (relative path, bytes) of the canonical inputs")
    parts.append("")
    parts.append("## Inclusion and exclusion rules")
    parts.append("")
    parts.append("This index includes:")
    for bullet in body.includes:
        parts.append(f"- {bullet}")
    parts.append("")
    parts.append("This index deliberately excludes:")
    for bullet in body.excludes:
        parts.append(f"- {bullet}")
    parts.append(
        "- The `schema/` subtree, for the same reason `validate.py` excludes it: "
        "schema-testing"
    )
    parts.append("  infrastructure, not corpus content")
    if ctx.output_paths:
        joined = ", ".join(f"`{p}`" for p in ctx.output_paths)
        parts.append(
            f"- Every registered generated output path ({joined}), so no generated"
        )
        parts.append("  view feeds itself")
    parts.append("")
    parts.append(body.sections.strip("\n"))
    parts.append("")
    parts.append("## Relationships")
    parts.append("")
    if spec.relationships:
        for rel in spec.relationships:
            parts.append(f"- {rel['type']}: {rel['target']}")
    else:
        parts.append("- None declared.")
    parts.append("")
    parts.append("## Scope and omissions")
    parts.append("")
    parts.append(
        f"**This node covers** a generated listing of {spec.subject}, as of input"
    )
    parts.append(f"digest `sha256:{ctx.input_digest}`.")
    parts.append("")
    parts.append("**It does not cover, and these are gaps rather than silence:**")
    parts.append("")
    parts.append(
        "- Hand-authored corpus content and policy -- the canonical nodes "
        "themselves own that."
    )
    for bullet in body.not_covered:
        parts.append(f"- {bullet}")
    parts.append("")
    parts.append("**Expected but not verified when this node was written:**")
    parts.append("")
    if body.unverified:
        for bullet in body.unverified:
            parts.append(f"- {bullet}")
    else:
        parts.append(
            "- Nothing -- every canonical input this generator read was discovered"
        )
        parts.append("  and parsed by the validator's own contract.")
    return "\n".join(parts).rstrip("\n") + "\n"


# ---------------------------------------------------------------------------
# CLI (conventions follow validate.py: argparse, main(argv) -> int)
# ---------------------------------------------------------------------------
def _select(specs: list[IndexSpec], only: list[str] | None) -> list[IndexSpec]:
    if not only:
        return specs
    by_name = {s.name: s for s in specs}
    unknown = sorted(set(only) - set(by_name))
    if unknown:
        known = ", ".join(sorted(by_name)) or "<none>"
        raise SpecError(
            f"unknown builder name(s): {', '.join(unknown)} (known: {known})"
        )
    return [s for s in specs if s.name in set(only)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", default=None, help=f"corpus root (default: {validate.DEFAULT_ROOT})"
    )
    parser.add_argument(
        "--defs-dir",
        default=None,
        help="builder package directory (default: index_defs/ beside this script; "
        "for tests)",
    )
    parser.add_argument(
        "--list", action="store_true", help="list registered builders and exit"
    )
    parser.add_argument(
        "--only",
        action="append",
        default=None,
        metavar="NAME",
        help="restrict to this builder (repeatable)",
    )
    parser.add_argument(
        "--all", action="store_true", help="regenerate every builder's output"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="regenerate in memory and diff against the files on disk; nonzero "
        "exit on any difference",
    )
    args = parser.parse_args(argv)

    if args.all and args.only:
        parser.error("--all and --only are mutually exclusive")
    if args.list and (args.all or args.only or args.check):
        parser.error("--list takes no other action flags")
    if not (args.list or args.all or args.only or args.check):
        parser.error("choose an action: --list, --all, --only NAME, or --check")

    corpus_root = (
        Path(args.root) if args.root else validate.repo_root() / validate.DEFAULT_ROOT
    )
    defs_dir = Path(args.defs_dir) if args.defs_dir else None

    try:
        specs = discover_builders(defs_dir)
    except SpecError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    if args.list:
        for spec in specs:
            print(f"{spec.name}\t{spec.output_path}")
        if not specs:
            print("no builders registered", file=sys.stderr)
        return 0

    try:
        selected = _select(specs, args.only)
    except SpecError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    if not selected:
        # No builders installed: nothing to generate and nothing can be stale.
        print("PASS  no builders registered; nothing to generate")
        return 0

    try:
        ctx = build_context(corpus_root, specs)
        rendered = [(spec, render_document(spec, ctx)) for spec in selected]
    except validate.CorpusRootMissing as exc:
        print(f"FAIL  corpus root does not exist: {exc}", file=sys.stderr)
        return 1
    except SpecError as exc:
        print(f"FAIL  {exc}", file=sys.stderr)
        return 1

    if args.check:
        stale = 0
        for spec, text in rendered:
            target = corpus_root / PurePosixPath(spec.output_path)
            if not target.is_file():
                print(
                    f"FAIL  {spec.name}: {spec.output_path} is missing on disk",
                    file=sys.stderr,
                )
                stale += 1
            elif target.read_bytes() != text.encode():
                print(
                    f"FAIL  {spec.name}: {spec.output_path} differs from a fresh "
                    "regeneration",
                    file=sys.stderr,
                )
                stale += 1
        if stale:
            print(f"FAIL  {stale} generated file(s) out of date", file=sys.stderr)
            return 1
        print(f"PASS  {len(rendered)} generated file(s) up to date")
        return 0

    for spec, text in rendered:
        target = corpus_root / PurePosixPath(spec.output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        print(f"PASS  wrote {spec.output_path} ({spec.name})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

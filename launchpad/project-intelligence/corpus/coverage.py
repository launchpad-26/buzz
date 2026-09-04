"""Corpus completeness and source-coverage accounting -- issue #634.

Compares three things this tree already knows how to produce -- the source
inventory (`inventory.py`, issue #624), a #626 manifest (`manifest.py`), and
the canonical corpus nodes (`validate.py`'s discovery and front-matter
contract) -- and assigns every in-scope inventory item exactly ONE positive
disposition:

- ``documented``            a canonical node's file/position evidence citation
                            covers the item, or a manifest row's
                            `source_start_points` name it. The row links every
                            covering node id and task alias.
- ``represented-elsewhere`` recorded in the auditable dispositions registry,
                            naming the node ids / task aliases where the item
                            is represented.
- ``generated-only``        recorded in the registry with a reason.
- ``explicitly-excluded``   recorded in the registry with a reason.

Anything that cannot be POSITIVELY assigned is a visible ``GAP``. There is no
"not examined" or "unknown" state at all: the registry rejects any such
spelling, and a GAP never counts toward completeness --
``CoverageReport.complete`` is true exactly when the report has zero GAP rows.
`inventory.py`'s ``unrecognized_areas`` (top-level directories the inventory
neither discovers nor deliberately ignores) are always GAP rows: the fix for
one is teaching inventory.py, never papering over it here.

The registry is an INPUT this module reads and validates but never writes --
an exclusion must be recorded somewhere auditable by a human (issue #634:
"never invented by coverage.py itself"). Its JSON shape is
``{"dispositions": [{"source_key": ..., "disposition": ..., "reason": ...,
"accounted_by": [...]}]}``; see `load_registry`.

Output is deterministic -- rows stable-sorted by (category, source_key), links
sorted, no timestamps -- so two runs over an unchanged tree are
byte-identical on stdout. The summary and advisory findings go to stderr so
stdout stays machine-readable (TSV by default, ``--format markdown`` for
review).

Exit codes, for the later CI job (#621's coverage gate) to route on:

- 0  report produced; gaps, if any, are advisory in this default mode.
- 1  ``--strict`` was given and the report has gaps or advisory findings --
     the completeness gate, opt-in so CI can adopt it deliberately.
- 2  input error: missing corpus root, malformed manifest, or malformed
     dispositions registry. Always hard, never advisory.

Python API (what #892's generated/coverage.md builder calls, no CLI needed):
``build_coverage(root, corpus_root, manifest_rows=(), registry=None)`` returns
a `CoverageReport` whose ``rows`` are structured `CoverageRow`s.
`load_manifest_rows` and `load_registry` parse the two optional file inputs.

Run:  python3 launchpad/project-intelligence/corpus/coverage.py
          [--root PATH] [--corpus-root PATH] [--manifest PATH]
          [--dispositions PATH] [--format tsv|markdown] [--strict]
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath


def _load_sibling(name: str):
    """Load a sibling module by path, sharing the cache the tests already use.

    `project-intelligence` is not a legal Python package name (hyphen), so the
    established convention -- test_validate.py, test_inventory.py -- is
    `importlib.util.spec_from_file_location` under a `corpus_<name>` module
    name. Reusing exactly those names means a test that loaded inventory.py
    first and this module second shares one module object, not two.
    """
    module_name = f"corpus_{name}"
    if module_name in sys.modules:
        return sys.modules[module_name]
    path = Path(__file__).resolve().parent / f"{name}.py"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


inventory = _load_sibling("inventory")
manifest = _load_sibling("manifest")
validate = _load_sibling("validate")

DEFAULT_CORPUS_ROOT = validate.DEFAULT_ROOT

# The four positive dispositions plus the one visible failure state. GAP is
# deliberately NOT a member of _POSITIVE_DISPOSITIONS: nothing in this module
# ever treats it as accounting for an item, which is the mechanical form of
# issue #634's "no `not examined` state can satisfy completeness".
DOCUMENTED = "documented"
REPRESENTED_ELSEWHERE = "represented-elsewhere"
GENERATED_ONLY = "generated-only"
EXPLICITLY_EXCLUDED = "explicitly-excluded"
GAP = "GAP"

_POSITIVE_DISPOSITIONS = frozenset(
    {DOCUMENTED, REPRESENTED_ELSEWHERE, GENERATED_ONLY, EXPLICITLY_EXCLUDED}
)
# Only these may appear in the registry. `documented` must be EARNED by a
# node citation or manifest mapping, never asserted by hand -- a registry that
# could declare an item documented would be a quieter way to invent coverage.
_REGISTRY_DISPOSITIONS = frozenset(
    {REPRESENTED_ELSEWHERE, GENERATED_ONLY, EXPLICITLY_EXCLUDED}
)


class CoverageInputError(Exception):
    """A malformed input (manifest or registry). Always a hard failure, exit 2 --
    a bad registry silently ignored would let an unexamined item look excluded."""


@dataclass(frozen=True)
class RegistryEntry:
    source_key: str
    disposition: str
    reason: str
    accounted_by: tuple[str, ...] = ()


@dataclass(frozen=True)
class CoverageRow:
    """One in-scope source item and the single disposition assigned to it.

    `nodes` and `aliases` are the linkage issue #634's DoD requires: the
    canonical node id(s) and/or task alias(es) that account for the item.
    For registry-backed dispositions they carry the entry's `accounted_by`;
    for a GAP they are empty, because nothing accounts for a gap.
    """

    category: str
    source_key: str
    path: str
    disposition: str
    nodes: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    detail: str = ""


@dataclass
class CoverageReport:
    rows: list[CoverageRow] = field(default_factory=list)
    findings: list[str] = field(default_factory=list)

    @property
    def gaps(self) -> list[CoverageRow]:
        return [row for row in self.rows if row.disposition == GAP]

    @property
    def complete(self) -> bool:
        """True exactly when every item is positively dispositioned.

        Defined over the GAP rows and nothing else -- there is no code path
        that can mark an item complete without one of the four positive
        dispositions, and no representable "not examined" state to launder one
        through (see load_registry's rejection of unknown disposition values).
        """
        return not self.gaps

    def to_tsv(self) -> str:
        lines = ["category\tsource_key\tdisposition\tnodes\taliases\tdetail"]
        for row in self.rows:
            lines.append(
                "\t".join(
                    (
                        row.category,
                        row.source_key,
                        row.disposition,
                        ",".join(row.nodes),
                        ",".join(row.aliases),
                        row.detail,
                    )
                )
            )
        return "\n".join(lines) + "\n"

    def to_markdown(self) -> str:
        lines = [
            "| category | source_key | disposition | nodes | aliases | detail |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for row in self.rows:
            cells = (
                row.category,
                row.source_key,
                row.disposition,
                ", ".join(row.nodes),
                ", ".join(row.aliases),
                row.detail,
            )
            lines.append("| " + " | ".join(c.replace("|", "\\|") for c in cells) + " |")
        return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Path coverage
# ---------------------------------------------------------------------------
# Inventory item paths come in three shapes (see inventory.py): a directory
# ("crates/buzz-relay"), a file ("migrations/0001_init.sql"), and a
# file-with-line ("crates/buzz-core/src/kind.rs:219"). Citations add ranges
# ("...:219-221"). Both sides are split into (path, start, end) once, and
# coverage is judged on the pieces.


def _split_position(text: str) -> tuple[str, int | None, int | None]:
    """Split "path[:start[-end]]" using validate.py's file-position grammar."""
    match = validate._FILE_POSITION_RE.match(text)
    if not match:
        return text, None, None
    start = int(match.group("start"))
    end = int(match.group("end")) if match.group("end") else start
    return match.group("path"), start, end


def _path_contains(ancestor: str, descendant: str) -> bool:
    """True when `descendant` equals `ancestor` or lies beneath it."""
    a = PurePosixPath(ancestor)
    d = PurePosixPath(descendant)
    return a == d or a in d.parents


def _citation_covers_item(
    cite_path: str, cite_start: int | None, cite_end: int | None, item_path: str
) -> bool:
    """Does a file/position citation cover an inventory item?

    - The same file covers the item; when BOTH sides carry line positions the
      item's line must fall inside the citation's range, so one node citing
      kind.rs:219-221 documents exactly the event kinds declared there rather
      than all of them.
    - A citation to a file beneath a directory-shaped item covers the
      directory item (citing crates/buzz-relay/src/router.rs accounts for the
      buzz-relay crate). The reverse is impossible for node citations --
      validate.py rejects a citation that is not a real file.
    """
    ipath, istart, _iend = _split_position(item_path)
    if cite_path == ipath:
        if cite_start is not None and istart is not None:
            return cite_start <= istart <= (cite_end or cite_start)
        return True
    return _path_contains(ipath, cite_path)


def _start_point_covers_item(start_point: str, item) -> bool:
    """Does a manifest row's source_start_point name an inventory item?

    An exact `source_key` match is checked first, so a manifest can be precise
    without path arithmetic ("event_kind:KIND_MESSAGE"). Otherwise the start
    point is a path, and containment runs in BOTH directions: a start point
    may be a file inside a crate-shaped item, or a directory enclosing a
    file-shaped item. Both are explicit, auditable statements in the manifest.
    """
    if start_point == item.source_key:
        return True
    sp_path, sp_start, sp_end = _split_position(start_point)
    if _citation_covers_item(sp_path, sp_start, sp_end, item.path):
        return True
    ipath, _s, _e = _split_position(item.path)
    return _path_contains(sp_path, ipath)


def _node_file_citations(node) -> list[tuple[str, int | None, int | None]]:
    """Every openable file/position citation in one loaded node.

    Only CONTRACT.md's three openable forms name repository files; URLs,
    commit references, graph edges and tool results name nothing on disk and
    therefore never document an inventory item here. Markdown links unwrap
    first, mirroring validate._classify_citation's routing order.
    """
    citations: list[tuple[str, int | None, int | None]] = []
    for entry in node.data.get("evidence") or []:
        if not isinstance(entry, dict):
            continue
        for citation in entry.get("evidence") or []:
            if not isinstance(citation, str):
                continue
            text = citation.strip()
            link = validate._MARKDOWN_LINK_RE.match(text)
            if link:
                text = link.group("target")
            if text.startswith(validate._URL_PREFIXES):
                continue
            if (
                validate._COMMIT_CITATION_RE.match(text)
                or validate._GRAPH_EDGE_RE.match(text)
                or validate._TOOL_RESULT_RE.match(text)
            ):
                continue
            if not text or any(ch.isspace() for ch in text):
                continue
            citations.append(_split_position(text))
    return citations


# ---------------------------------------------------------------------------
# Input loading
# ---------------------------------------------------------------------------


def load_manifest_rows(path: Path) -> list:
    """Read a manifest JSON file into validated ManifestRows.

    Accepts either `manifest.Manifest.to_json()`'s shape ({"rows": [...]}) or
    a bare plan list, and routes both through `manifest.build_manifest` so
    every structural guarantee #626 enforces holds here too -- a manifest this
    module accepts is exactly one issue_plan.py would accept.
    """
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise CoverageInputError(f"manifest {path}: {exc.__class__.__name__}: unreadable or not JSON") from exc
    if isinstance(payload, dict):
        payload = payload.get("rows")
    if not isinstance(payload, list):
        raise CoverageInputError(f"manifest {path}: expected a list of rows or {{\"rows\": [...]}}")
    try:
        return manifest.build_manifest(payload).rows
    except manifest.ManifestValidationError as exc:
        raise CoverageInputError(f"manifest {path}: {exc}") from exc


def load_registry(path: Path) -> list[RegistryEntry]:
    """Read and validate the auditable dispositions registry.

    Fail-closed on every malformation: an unknown disposition (including any
    "not-examined"/"unknown" spelling -- issue #634's rule that no such state
    exists), `documented` (must be earned, never asserted), a duplicate
    source_key, a missing reason, or `represented-elsewhere` without
    `accounted_by` naming where the item IS represented. A registry problem is
    a CoverageInputError, never a silently skipped entry.
    """
    try:
        payload = json.loads(path.read_text())
    except (OSError, ValueError) as exc:
        raise CoverageInputError(f"registry {path}: {exc.__class__.__name__}: unreadable or not JSON") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("dispositions"), list):
        raise CoverageInputError(f"registry {path}: expected {{\"dispositions\": [...]}}")

    entries: list[RegistryEntry] = []
    seen: set[str] = set()
    for index, raw in enumerate(payload["dispositions"], start=1):
        if not isinstance(raw, dict):
            raise CoverageInputError(f"registry {path}: entry {index} is not an object")
        source_key = raw.get("source_key")
        disposition = raw.get("disposition")
        reason = raw.get("reason")
        accounted_by = raw.get("accounted_by", [])
        if not isinstance(source_key, str) or not source_key:
            raise CoverageInputError(f"registry {path}: entry {index} has no source_key")
        if source_key in seen:
            raise CoverageInputError(
                f"registry {path}: duplicate entry for source_key {source_key!r}"
            )
        seen.add(source_key)
        if disposition not in _REGISTRY_DISPOSITIONS:
            allowed = ", ".join(sorted(_REGISTRY_DISPOSITIONS))
            raise CoverageInputError(
                f"registry {path}: entry {source_key!r} has disposition "
                f"{disposition!r}; the only recordable dispositions are {allowed} "
                "-- there is no 'not examined' state, and 'documented' must be "
                "earned by a node citation or manifest mapping"
            )
        if not isinstance(reason, str) or not reason.strip():
            raise CoverageInputError(
                f"registry {path}: entry {source_key!r} has no reason -- an "
                "exclusion without a recorded reason is not auditable"
            )
        if not isinstance(accounted_by, list) or not all(
            isinstance(a, str) and a for a in accounted_by
        ):
            raise CoverageInputError(
                f"registry {path}: entry {source_key!r} has a malformed accounted_by"
            )
        if disposition == REPRESENTED_ELSEWHERE and not accounted_by:
            raise CoverageInputError(
                f"registry {path}: entry {source_key!r} is represented-elsewhere "
                "but names no node id or task alias in accounted_by"
            )
        entries.append(
            RegistryEntry(
                source_key=source_key,
                disposition=disposition,
                reason=reason.strip(),
                accounted_by=tuple(accounted_by),
            )
        )
    return entries


# ---------------------------------------------------------------------------
# The accounting itself
# ---------------------------------------------------------------------------


def build_coverage(
    root: Path,
    corpus_root: Path,
    manifest_rows: list | tuple = (),
    registry: list[RegistryEntry] | None = None,
    excluded_output_paths: frozenset[str] | set[str] | None = None,
) -> CoverageReport:
    """Account for every in-scope inventory item; the API #892 renders from.

    Raises CorpusRootMissing (validate.py's, re-raised untouched) when
    `corpus_root` does not exist, and CoverageInputError when a registry entry
    names a source_key the inventory does not contain -- a stale registry is
    input drift, not something to skip past.

    `excluded_output_paths` names corpus-root-relative posix paths of
    registered generated-document outputs (`indexes.py`'s own
    `ctx.output_paths`). A generated document's own evidence citations prove
    that IT was produced correctly -- they are not independent confirmation
    that some OTHER in-scope file its rendered content happens to name is
    documented. Without this exclusion, a future builder whose evidence cites
    an in-scope source file directly would silently mark that file
    `documented`, laundering a real gap through a generated artifact -- the
    same self-feeding `indexes.py`'s own canonical-input contract already
    guards against for its own listings. Omit (the default) to preserve prior
    behavior for a caller with no generator registry to pass.
    """
    report = CoverageReport()
    inv = inventory.run_inventory(root)
    nodes = validate.load_nodes(corpus_root)
    excluded = frozenset(excluded_output_paths or ())
    if excluded:
        nodes = [
            node
            for node in nodes
            if node.path.relative_to(corpus_root).as_posix() not in excluded
        ]

    # Nodes that failed to parse or validate contribute no citations: their
    # coverage claims are not trustworthy, and losing them fails in the safe
    # direction -- items they might have documented become VISIBLE gaps, and
    # the finding below says why. Never a silent pass.
    usable_nodes = []
    for node in nodes:
        if node.error:
            report.findings.append(
                f"node {node.path} was skipped (failed to load or validate); "
                "any coverage it claims is not counted"
            )
            continue
        if not isinstance(node.id, str) or not node.id:
            report.findings.append(
                f"node {node.path} has no usable id; its citations cannot be "
                "linked and are not counted"
            )
            continue
        usable_nodes.append(node)

    node_citations = [(node.id, _node_file_citations(node)) for node in usable_nodes]

    registry_by_key = {entry.source_key: entry for entry in registry or []}
    inventory_keys = {item.source_key for item in inv.items}
    stale = sorted(set(registry_by_key) - inventory_keys)
    if stale:
        raise CoverageInputError(
            "registry names source_key(s) the inventory does not contain "
            f"(stale or mistyped): {', '.join(stale)}"
        )

    for item in sorted(inv.items, key=lambda i: (i.category, i.source_key)):
        covering_nodes = sorted(
            {
                node_id
                for node_id, citations in node_citations
                if any(
                    _citation_covers_item(cpath, cstart, cend, item.path)
                    for cpath, cstart, cend in citations
                )
            }
        )
        covering_aliases = sorted(
            {
                row.path
                for row in manifest_rows
                if any(_start_point_covers_item(sp, item) for sp in row.source_start_points)
            }
        )

        entry = registry_by_key.get(item.source_key)
        if covering_nodes or covering_aliases:
            if entry is not None:
                report.findings.append(
                    f"{item.source_key}: registry records it as {entry.disposition} "
                    "but it is documented by "
                    f"{', '.join(covering_nodes + covering_aliases)}; the registry "
                    "entry is redundant or stale"
                )
            report.rows.append(
                CoverageRow(
                    category=item.category,
                    source_key=item.source_key,
                    path=item.path,
                    disposition=DOCUMENTED,
                    nodes=tuple(covering_nodes),
                    aliases=tuple(covering_aliases),
                )
            )
            continue

        if entry is not None:
            report.rows.append(
                CoverageRow(
                    category=item.category,
                    source_key=item.source_key,
                    path=item.path,
                    disposition=entry.disposition,
                    nodes=(),
                    aliases=entry.accounted_by,
                    detail=entry.reason,
                )
            )
            continue

        report.rows.append(
            CoverageRow(
                category=item.category,
                source_key=item.source_key,
                path=item.path,
                disposition=GAP,
                detail="no node citation, manifest mapping, or recorded disposition accounts for this item",
            )
        )

    # Unrecognized top-level areas are unconditional gaps: unmapped new/changed
    # source areas must be VISIBLE (issue #634 DoD), and the only fix is
    # teaching inventory.py to recognise or deliberately ignore them.
    for area in sorted(inv.unrecognized_areas):
        report.rows.append(
            CoverageRow(
                category="unrecognized_area",
                source_key=f"unrecognized_area:{area}",
                path=area,
                disposition=GAP,
                detail="top-level directory inventory.py neither discovers nor deliberately ignores",
            )
        )

    report.rows.sort(key=lambda r: (r.category, r.source_key))
    report.findings.sort()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=None, help="Repository root (default: resolved via git)")
    parser.add_argument(
        "--corpus-root",
        type=Path,
        default=None,
        help=f"Corpus root (default: <root>/{DEFAULT_CORPUS_ROOT})",
    )
    parser.add_argument("--manifest", type=Path, default=None, help="Manifest JSON (#626 shape); optional")
    parser.add_argument(
        "--dispositions", type=Path, default=None, help="Auditable dispositions registry JSON; optional"
    )
    parser.add_argument("--format", choices=("tsv", "markdown"), default="tsv")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 when the report has gaps or advisory findings (the CI completeness gate)",
    )
    args = parser.parse_args(argv)

    root = args.root or inventory.repo_root()
    corpus_root = args.corpus_root or root / DEFAULT_CORPUS_ROOT

    try:
        manifest_rows = load_manifest_rows(args.manifest) if args.manifest else []
        registry = load_registry(args.dispositions) if args.dispositions else []
        report = build_coverage(root, corpus_root, manifest_rows, registry)
    except CoverageInputError as exc:
        print(f"ERROR  {exc}", file=sys.stderr)
        return 2
    except validate.CorpusRootMissing as exc:
        print(f"ERROR  corpus root does not exist: {exc}", file=sys.stderr)
        return 2

    sys.stdout.write(report.to_markdown() if args.format == "markdown" else report.to_tsv())

    for finding in report.findings:
        print(f"FINDING  {finding}", file=sys.stderr)
    gaps = len(report.gaps)
    if report.complete:
        print(f"COMPLETE  all {len(report.rows)} in-scope items positively dispositioned", file=sys.stderr)
    else:
        print(
            f"INCOMPLETE  {gaps} gap(s) out of {len(report.rows)} in-scope items",
            file=sys.stderr,
        )

    if args.strict and (gaps or report.findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

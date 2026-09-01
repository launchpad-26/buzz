"""Deterministic corpus validator -- issue #623.

One local and CI command that rejects structurally invalid corpus changes,
enforcing the schema #622 defined (launchpad/docs/corpus/schema/node.schema.json)
plus the cross-node and content rules a single document's schema validation
cannot express on its own: duplicate ids, unresolved relationship targets,
unverifiable/prohibited evidence citations, and stray non-canonical files.

Citations are parsed against CONTRACT.md section 3's six forms before anything is
checked. Offline mode performs deterministic local checks only; URL citations are
reported as UNVERIFIED and still block the run. --check-links additionally opens
HTTP(S) citations so reachable links can pass and unreachable links fail.

Run:  python3 launchpad/project-intelligence/corpus/validate.py [--root PATH]
  or: python3 launchpad/project-intelligence/corpus/validate.py --check-links
  or: just corpus-validate
"""

from __future__ import annotations

import importlib.util
import argparse
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

import jsonschema
import yaml



def _load_evidence_parser():
    module_name = "_corpus_evidence_parser"
    existing = sys.modules.get(module_name)
    if existing is not None:
        return existing
    parser_path = Path(__file__).with_name("evidence.py")
    spec = importlib.util.spec_from_file_location(module_name, parser_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load evidence parser from {parser_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_EVIDENCE_PARSER = _load_evidence_parser()
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


@dataclass
class ValidationReport:
    """What one validation run found.

    Two channels, deliberately separate. `errors` are hard failures: the run exits
    non-zero. `unverified` names citation forms this validator RECOGNISES as
    legitimate but genuinely cannot check offline -- a commit reference, a graph
    edge, a tool result, an external URL. `launchpad/project-intelligence/CONTRACT.md`
    section 3 states that discipline directly: "parse what is parseable, and report
    the rest as unverified rather than skipping it". Silently passing them (what an
    earlier revision did) makes a clean PASS mean less than it claims.

    The channel is for forms that are unverifiable BY NATURE, never for things the
    validator merely failed to establish. Anything matching no known form is an
    error, and so is a generated artifact whose provenance cannot be established
    (see find_ownership_violations) -- an earlier revision of that check routed it
    here, which a cross-model review-final pass correctly called a fail-open.
    """

    errors: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)


# Every message names its node through this helper, and the guarantee is about the
# SHAPE of what gets printed, not about whether the node passed schema validation.
# A schema-invalid node can carry any string at all in `id`, including a path the
# DoD's "without leaking private source content" forbids echoing -- so the label is
# either a string already matching the schema's kebab-case id pattern (no slashes,
# dots or spaces, therefore not a path and not a citation value) or else the file
# path, which is a location inside this repository the run already walked.
#
# Deliberately NOT gated on `node.error`: a kebab-case id from a node that failed
# validation for some unrelated reason is still just a corpus identifier, and
# degrading every such message to a path would make the common case harder to act
# on for no gain. An independent cross-model review-final pass read the earlier
# wording of this comment as promising a post-validation guarantee it never made;
# the invariant above is the one the code actually enforces.
_SAFE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _label(node_id: object, path: Path) -> str:
    if isinstance(node_id, str) and _SAFE_ID_RE.match(node_id):
        return node_id
    return str(path)


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


def _is_canonical_location(path: Path, root: Path) -> bool:
    """True if `path` genuinely lives beneath `root` once symlinks are followed.

    `rglob` yields symlinked files without dereferencing them, so a symlink placed
    inside the corpus pointing at a Markdown node elsewhere on disk was walked,
    parsed and validated as though it were canonical corpus content. ADR-0028 makes
    the corpus tree itself the canonical source; content that only appears to live
    there is not canonical, and validating it lends it authority it does not have.
    A cross-model review-final pass found this by symlinking a valid node in from
    outside and watching the run print PASS.

    Resolution failure counts as non-canonical rather than propagating: a symlink
    loop makes `.resolve()` raise RuntimeError, and an earlier revision of this
    check let that escape as a traceback. A traceback names no node, which the DoD
    forbids -- the same review-final pass found the crash by committing a
    self-referential link.

    The sibling check for citation *targets* lives in evidence.py's
    `_verify_local` (reached through `_EVIDENCE_PARSER.verify_citation`); this
    one governs which files are corpus content in the first place.
    """
    try:
        return path.resolve().is_relative_to(root)
    except (OSError, RuntimeError):
        return False


def discover_markdown_files(corpus_root: Path) -> list[Path]:
    """Every `.md` file that is genuinely corpus content (schema/ excluded)."""
    if not corpus_root.is_dir():
        raise CorpusRootMissing(str(corpus_root))
    resolved_root = corpus_root.resolve()
    return sorted(
        p
        for p in corpus_root.rglob("*.md")
        if not _is_excluded(p, corpus_root)
        and _is_canonical_location(p, resolved_root)
    )


def find_non_canonical_nodes(corpus_root: Path) -> list[str]:
    """Report `.md` files inside the corpus that do not actually live there.

    discover_markdown_files excludes them so they are never validated as corpus
    content; this reports them so excluding them is not the same as ignoring them.
    A cross-model review-final pass made exactly that distinction: an escaping
    symlink that is silently dropped still leaves the run printing PASS while a
    file sits in the tree that nothing checked, which is a quieter version of the
    problem the exclusion was added to fix.
    """
    if not corpus_root.is_dir():
        raise CorpusRootMissing(str(corpus_root))
    resolved_root = corpus_root.resolve()
    errors = []
    for path in sorted(corpus_root.rglob("*.md")):
        if _is_excluded(path, corpus_root):
            continue
        if _is_canonical_location(path, resolved_root):
            continue
        errors.append(
            f"{path.relative_to(corpus_root)}: is not canonical corpus content -- "
            "it resolves outside the corpus root, or cannot be resolved at all "
            "(ADR-0028)"
        )
    return errors


def _load_frontmatter(path: Path, known_keys: frozenset[str] = frozenset()) -> dict:
    """Parse a Markdown-with-YAML-frontmatter node (ADR-0028's representation)."""
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError("no leading '---' frontmatter delimiter")
    _, frontmatter, _body = text.split("---\n", 2)

    duplicate = _find_duplicate_key(yaml.compose(frontmatter))
    if duplicate is not None:
        key, mark = duplicate
        named = f" '{key}'" if key in known_keys else ""
        raise ValueError(
            f"duplicate frontmatter key{named} at line {mark.line + 2}, "
            f"column {mark.column + 1}"
        )

    return yaml.safe_load(frontmatter) or {}


def _parse_failure(exc: Exception) -> str:
    """Describe a frontmatter parse failure WITHOUT echoing the frontmatter.

    PyYAML's exception text quotes the source line it choked on -- so a malformed
    node whose frontmatter contains a credential-shaped path printed that path
    straight into CI output. This is the same leak the schema-error path already
    closed (see _schema_constraint), reached through a different door: a document
    that fails to parse never reaches schema validation, so that fix could not help
    it. An independent cross-model review-final pass found it.

    ONLY `problem_mark` is printed -- line and column, positions rather than
    content. `problem` looks safe (it is usually a fixed token-level description
    like "expected <block end>, but found ':'"), and an earlier revision of this
    fix printed it for exactly that reason. It is not safe: for an undefined alias
    or an unknown tag, PyYAML interpolates the document's own identifier into that
    string -- `found undefined alias 'PRIVATE_SOURCE_ID_RSA'`. A second cross-model
    review-final pass found the residual leak by feeding those two shapes in, after
    the ordinary malformations (indentation, tabs, quotes, control characters, long
    lines) had all come back clean. A field that is content-free in most cases and
    content-bearing in some is content-bearing.
    """
    mark = getattr(exc, "problem_mark", None)
    if mark is not None:
        # +1 twice: PyYAML marks are 0-based, and the frontmatter block starts on
        # the line after the opening '---' delimiter.
        return (
            "could not be parsed as YAML at frontmatter line "
            f"{mark.line + 2}, column {mark.column + 1}"
        )
    if isinstance(exc, ValueError) and not isinstance(exc, yaml.YAMLError):
        # Our own structural ValueErrors, raised with fixed strings that never
        # interpolate document content -- see _load_frontmatter.
        return str(exc)
    return "could not be parsed as YAML"


def _schema_property_names(schema: dict) -> frozenset[str]:
    """Every property name node.schema.json defines, at any depth.

    A duplicate-key error echoes the key only if it appears here. An earlier
    revision matched the key's SHAPE instead (`^[a-z][a-z0-9_]*$`), which a third
    cross-model review-final pass defeated immediately: `id_rsa` and
    `private_source_id_rsa` are both perfectly good-looking field names, so the
    shape test let exactly the content it existed to withhold straight through.
    Shape is a guess about what a value means; membership of a committed, public
    schema is a fact about it.
    """
    names: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            properties = node.get("properties")
            if isinstance(properties, dict):
                names.update(key for key in properties if isinstance(key, str))
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(schema)
    return frozenset(names)


def _find_duplicate_key(
    node: yaml.Node, seen_nodes: set[int] | None = None
) -> tuple[str, yaml.Mark] | None:
    """Return the first duplicate mapping key in a composed YAML tree, if any.

    PyYAML resolves `id: first` / `id: second` silently to the last one, so a node
    could carry two different values for the same field and pass validation, with
    the reader and the parser disagreeing about which is canonical. A second
    cross-model review-final pass found this. Detection happens on the composed
    node tree rather than through a loader hook because the tree is inspectable
    without executing PyYAML's construction machinery, and it reports positions
    directly.

    `seen_nodes` guards against a YAML anchor that refers to its own container --
    `loop: &loop {self: *loop}` is legal YAML and composes to a CYCLIC node graph,
    not a tree, so a plain recursive walk descends forever and dies with an
    uncaught RecursionError. A third cross-model review-final pass found that.
    Identity, not equality: two structurally identical mappings are genuinely two
    nodes and both must be checked.
    """
    if seen_nodes is None:
        seen_nodes = set()
    if id(node) in seen_nodes:
        return None
    seen_nodes.add(id(node))

    if isinstance(node, yaml.MappingNode):
        seen_keys: set[str] = set()
        for key_node, value_node in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                if key_node.value in seen_keys:
                    return (key_node.value, key_node.start_mark)
                seen_keys.add(key_node.value)
            nested = _find_duplicate_key(value_node, seen_nodes)
            if nested is not None:
                return nested
    elif isinstance(node, yaml.SequenceNode):
        for item in node.value:
            nested = _find_duplicate_key(item, seen_nodes)
            if nested is not None:
                return nested
    return None


def _schema_constraint(error: jsonschema.ValidationError) -> str:
    """Describe a schema violation using SCHEMA-side facts only, never the instance.

    jsonschema's rendered `error.message` quotes the offending value verbatim --
    `'private/path/id_rsa' is not of type 'array'`. That echoes exactly the content
    the DoD says must not leak, and it bypasses the citation checks' own redaction,
    because a node with a schema error never reaches them. An independent
    cross-model review panel found this by supplying a credential-shaped path where
    the schema required an array.

    `error.validator` (the failed keyword) and `error.validator_value` (what the
    schema demanded) both come from node.schema.json, which is committed, public,
    and contains no instance data -- so they are safe to print, and they still say
    what the author has to change.
    """
    constraint = json.dumps(error.validator_value, sort_keys=True, default=str)
    if len(constraint) > 200:
        constraint = constraint[:200] + "..."
    return f"failed {str(error.validator)!r} constraint (schema requires: {constraint})"


def load_nodes(corpus_root: Path) -> list[LoadedNode]:
    """Load and schema-validate every node under corpus_root (schema/ excluded)."""
    schema = load_node_schema(repo_root())
    validator = jsonschema.Draft202012Validator(schema)
    known_keys = _schema_property_names(schema)

    nodes: list[LoadedNode] = []
    for path in discover_markdown_files(corpus_root):
        try:
            data = _load_frontmatter(path, known_keys)
        except OSError:
            # A dangling symlink whose target name resolves lexically inside the
            # root passes the canonical-location check and then fails to open. A
            # third cross-model review-final pass found the uncaught
            # FileNotFoundError; the exception's own text names the target path,
            # so it is not echoed.
            nodes.append(LoadedNode(path=path, error=f"{path}: could not be read"))
            continue
        except (ValueError, yaml.YAMLError) as exc:
            nodes.append(LoadedNode(path=path, error=f"{path}: {_parse_failure(exc)}"))
            continue

        # Frontmatter is valid YAML but not a mapping (a bare list, string, number,
        # or bool -- all valid YAML, none of them a schema violation jsonschema
        # would ever see, since that check happens below and needs a dict to run
        # against). An independent review-final pass found this crashes here with
        # an unhandled AttributeError, one line before the safety net the earlier
        # fix round relied on for malformed *entries inside* an already-parsed
        # dict -- this is the sibling case at the top level, caught before ever
        # reaching jsonschema.
        if not isinstance(data, dict):
            nodes.append(
                LoadedNode(
                    path=path,
                    error=f"{path}: frontmatter is not a mapping (got {type(data).__name__})",
                )
            )
            continue

        node_id = data.get("id")
        # Sorted on schema-side coordinates only (where the violation is, and which
        # keyword failed) rather than on str(error), whose rendering embeds the
        # offending instance value -- see the redaction note below.
        errors = sorted(
            validator.iter_errors(data),
            key=lambda e: (str(list(e.absolute_path)), str(e.validator)),
        )
        if errors:
            first = errors[0]
            nodes.append(
                LoadedNode(
                    path=path,
                    id=node_id,
                    data=data,
                    error=f"{_label(node_id, path)}: schema violation at "
                    f"{'/'.join(str(p) for p in first.absolute_path) or '<root>'}: "
                    f"{_schema_constraint(first)}",
                )
            )
            continue

        nodes.append(LoadedNode(path=path, id=node_id, data=data))
    return nodes


def find_duplicate_ids(nodes: list[LoadedNode]) -> list[str]:
    """Every node's `id` must be unique across the corpus."""
    # Keyed on str ids only. `id` is unvalidated at this point -- duplicate detection
    # deliberately includes schema-invalid nodes -- and YAML happily produces a list
    # or dict there, which is unhashable: `id: [some/path]` crashed this dict with an
    # unhandled TypeError instead of the controlled, node-naming failure the DoD
    # requires. A non-str id is already reported by its own schema violation, so
    # skipping it here loses nothing. An independent cross-model review-final pass
    # found this.
    paths_by_id: dict[str, list[Path]] = {}
    for node in nodes:
        if not isinstance(node.id, str):
            continue
        paths_by_id.setdefault(node.id, []).append(node.path)

    errors = []
    for node_id, paths in paths_by_id.items():
        if len(paths) > 1:
            joined = ", ".join(str(p) for p in paths)
            # Labelled through _label: duplicate detection deliberately includes
            # schema-invalid nodes (two nodes can collide on an id neither of which
            # validates), so the id reaching this message is not yet trustworthy.
            errors.append(
                f"{_label(node_id, paths[0])}: duplicate id used by "
                f"{len(paths)} nodes: {joined}"
            )
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
    # `isinstance(..., str)`, not `is not None`: an unvalidated `id` can be a YAML
    # list or dict, and putting one in a set raises TypeError. This is the sibling
    # of the same crash in find_duplicate_ids -- a review-final pass named that one;
    # this second site surfaced when its fixture was run against the whole
    # validator rather than that one function. A relationship target is
    # schema-constrained to a kebab-case string, so a non-str id could never have
    # been a legitimate match anyway.
    known_ids = {node.id for node in nodes if isinstance(node.id, str)}

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


# The unopenable forms embed paths inside expressions -- a tool result's arguments
# are the obvious case -- so the blocklist runs over each token rather than over
# the whole string. Testing the whole string got it wrong in both directions at
# once, which a third cross-model review-final pass demonstrated: it MISSED
# `find_references('private/path/.env', ...) -> no callers`, whose basename is the
# trailing prose, and it FALSELY REJECTED a tool result mentioning `.env.example`,
# whose exemption depends on reading the token as a filename rather than as the
# suffix of a sentence.
_CITATION_TOKEN_SPLIT_RE = re.compile(r"[\s'\"(),=\[\]{}<>]+")


def _contains_prohibited_reference(text: str) -> bool:
    return any(
        _is_prohibited_citation(token)
        for token in _CITATION_TOKEN_SPLIT_RE.split(text)
        if token
    )


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


# ---------------------------------------------------------------------------
# Citation forms
# ---------------------------------------------------------------------------
# CONTRACT.md section 3 enumerates SIX citation shapes, and only three of them
# name an openable file: a file range (`crates/buzz-core/src/kind.rs:219-221`), a
# file line (`...:1077`), and a bare path (`Justfile`). The other three -- a graph
# edge, a tool result, a commit reference -- name nothing on disk. That section
# also states the rule for the remainder outright: "parse what is parseable, and
# report the rest as unverified rather than skipping it."
#
# An earlier revision honoured none of that: every non-URL citation went verbatim
# to Path.exists(), so the two positional forms and all three unopenable forms
# were reported as missing files, while `startswith("http")` waved every URL
# through unchecked. A cross-model review panel found both halves at once.
_MARKDOWN_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<target>[^)\s]+)\)$")
# GitHub URL syntax (pin/verb/path rules) and the network probe now live in
# evidence.py's `_verify_url` -- `_classify_url` below is a delegate. See that
# module's git history for the review passes that shaped each rule.
_COMMIT_CITATION_RE = re.compile(r"^commit\s+[0-9a-fA-F]{7,40}\b")
_FILE_POSITION_RE = re.compile(r"^(?P<path>\S+?):(?P<start>\d+)(?:-(?P<end>\d+))?$")
# CONTRACT.md's two unopenable non-commit forms, matched by SHAPE rather than by
# the bare presence of " -> ". An earlier revision treated any string containing
# that separator as a recognised citation and downgraded it to the non-fatal
# channel, so `private/path/id_rsa -> not a real citation` laundered arbitrary
# text -- including a prohibited path -- past every check and exited 0. An
# independent cross-model review-final pass found that fail-open.
#   graph edge:  `is_shared_gated_kind -> is_unshared_gated_event (1 hop)`
#   tool result: `find_references('x', crate='buzz-core') -> no callers here`
#
# A graph edge's endpoints are SYMBOL names, so they are matched as identifiers
# rather than as `\S+`. The looser form still accepted
# `private/path/id_rsa -> target (1 hop)`: adding a syntactically valid suffix to a
# path re-opened the same laundering the shape check was added to close, which a
# second cross-model review-final pass found. Identifiers cannot contain a path
# separator, which is what makes the difference.
_SYMBOL = r"[A-Za-z_][A-Za-z0-9_.:]*"
_GRAPH_EDGE_RE = re.compile(rf"^{_SYMBOL} -> {_SYMBOL} \(\d+ hops?\)$")
_TOOL_RESULT_RE = re.compile(rf"^{_SYMBOL}\(.*\) -> .+$")


@dataclass(frozen=True)
class CitationVerdict:
    """One citation's outcome. `detail` NEVER contains the citation value itself --
    every message this module emits is safe to print in CI logs."""

    status: str  # "ok" | "error" | "unverified"
    detail: str = ""



def _classify_url(url: str, *, check_links: bool) -> CitationVerdict:
    """Delegate a URL citation to evidence.py's registered verifier.

    The GitHub pin/verb/path syntax rules and the bounded HEAD-then-ranged-GET
    network probe live in evidence.py now, alongside every other evidence kind
    this module already routes through `_EVIDENCE_PARSER`. This function stays
    as a distinct call site so `_classify_citation`'s routing table does not
    need to change shape.
    """
    parsed = _EVIDENCE_PARSER.parse_citation(url)
    result = _EVIDENCE_PARSER.verify_citation(parsed, repo_root(), check_links=check_links)
    return CitationVerdict(result.status, result.detail)

def _classify_citation(
    citation: str, repo_root_path: Path, *, check_links: bool = False
) -> CitationVerdict:
    """Route one citation to the rule for its form (CONTRACT.md section 3).

    Order matters. Markdown links unwrap first, because ADR-0003's own reference
    format is one and its target -- not its prose label -- is what gets judged.
    URLs are judged before the credential blocklist, so a public URL whose path
    merely resembles a credential filename (a post titled
    "id_rsa-security-best-practices") is still accepted; an earlier revision ran
    the blocklist first and silently rejected them.
    """
    text = citation.strip()
    if not text:
        return CitationVerdict("error", "is empty")

    link = _MARKDOWN_LINK_RE.match(text)
    if link:
        text = link.group("target")

    parsed = _EVIDENCE_PARSER.parse_citation(text)
    if parsed.kind in (
        _EVIDENCE_PARSER.EvidenceKind.GITHUB_URL,
        _EVIDENCE_PARSER.EvidenceKind.EXTERNAL_URL,
    ):
        return _classify_url(text, check_links=check_links)

    if parsed.kind in (
        _EVIDENCE_PARSER.EvidenceKind.LOCAL_FILE_LINE,
        _EVIDENCE_PARSER.EvidenceKind.LOCAL_FILE_RANGE,
    ):
        if parsed.start_line is None or parsed.end_line is None:
            return CitationVerdict("error", "carries an incomplete line position")
        if parsed.start_line < 1 or parsed.end_line < parsed.start_line:
            return CitationVerdict("error", "carries a malformed line position")

    if parsed.kind in (
        _EVIDENCE_PARSER.EvidenceKind.LOCAL_FILE,
        _EVIDENCE_PARSER.EvidenceKind.LOCAL_FILE_LINE,
        _EVIDENCE_PARSER.EvidenceKind.LOCAL_FILE_RANGE,
        _EVIDENCE_PARSER.EvidenceKind.COMMIT,
    ):
        result = _EVIDENCE_PARSER.verify_citation(parsed, repo_root_path)
        return CitationVerdict(result.status, result.detail)

    if parsed.kind in (
        _EVIDENCE_PARSER.EvidenceKind.GRAPH_EDGE,
        _EVIDENCE_PARSER.EvidenceKind.TOOL_RESULT,
    ):
        if _contains_prohibited_reference(text):
            return CitationVerdict(
                "error", "matches a prohibited credential-like pattern"
            )
        return CitationVerdict(
            "unverified",
            "is a graph-edge or tool-result citation, which names no openable file",
        )

    return CitationVerdict(
        "error",
        "matches none of CONTRACT.md's six supported citation forms",
    )
def find_citation_problems(
    nodes: list[LoadedNode], repo_root_path: Path, *, check_links: bool = False
) -> tuple[list[str], list[str]]:
    """Classify every evidence citation; return (errors, unverified)."""
    errors: list[str] = []
    unverified: list[str] = []
    for node in nodes:
        if node.error:
            continue
        label = _label(node.id, node.path)
        for entry_index, entry in enumerate(node.data.get("evidence") or [], start=1):
            if not isinstance(entry, dict):
                continue
            citations = entry.get("evidence") or []
            for citation_index, citation in enumerate(citations, start=1):
                if not isinstance(citation, str):
                    continue
                verdict = _classify_citation(citation, repo_root_path, check_links=check_links)
                if verdict.status == "ok":
                    continue
                message = (
                    f"{label}: evidence entry {entry_index}, citation "
                    f"{citation_index}: {verdict.detail}"
                )
                if verdict.status == "error":
                    errors.append(message)
                else:
                    unverified.append(message)
    return errors, unverified


def find_non_finite_confidence(nodes: list[LoadedNode]) -> list[str]:
    """Reject a NaN or Infinity `confidence`, which node.schema.json cannot.

    JSON Schema's `minimum`/`maximum` keywords compare numerically, and every
    comparison against NaN is false, so the range assertion never fires -- NaN
    satisfies `"minimum": 0.0, "maximum": 1.0` and passes schema validation clean.
    `launchpad/project-intelligence/memory.py`'s `__post_init__` rejects the
    identical value via `not (0.0 <= confidence <= 1.0)`, which is also
    False-for-every-comparison-safe against NaN, but this validator never imports
    memory.py, so nothing reconciled the two paths before this (#1463).

    Runs only over nodes that already passed schema validation (`node.error` is
    None) -- a schema-invalid node's `confidence` isn't safe to assume numeric.
    """
    errors: list[str] = []
    for node in nodes:
        if node.error:
            continue
        label = _label(node.id, node.path)
        for entry_index, entry in enumerate(node.data.get("evidence") or [], start=1):
            if not isinstance(entry, dict):
                continue
            confidence = entry.get("confidence")
            if isinstance(confidence, (int, float)) and not math.isfinite(confidence):
                errors.append(
                    f"{label}: evidence entry {entry_index}: confidence must be a "
                    "finite number within [0.0, 1.0] -- NaN and Infinity pass "
                    "node.schema.json's minimum/maximum check but are rejected here"
                )
    return errors


def find_ownership_violations(corpus_root: Path) -> list[str]:
    """Enforce ADR-0028's canonical-vs-generated boundary.

    Every non-`.md` file (schema/ excluded) must live under a `generated/`
    subdirectory: hand-authored content is Markdown+frontmatter, anything else must
    be clearly segregated as a generated projection, never interleaved with
    authored nodes.

    Placement is only half of what ADR-0028 asks, and it is the only half a
    directory name can prove. The other half -- derived views are "never
    hand-authored, always reproducible from canonical Markdown" -- needs a
    generator to regenerate from and compare against, and none exists yet. A file
    hand-written straight into `generated/` is, today, indistinguishable from a
    real projection.

    So both cases fail, with different messages. An earlier revision of this fix
    reported the `generated/` case as a non-fatal notice instead, which an
    independent cross-model review-final pass rejected: a hand-authored artifact
    would print one line and still exit 0, permitting exactly the state ADR-0028
    forbids and the validator cannot rule out. Failing closed costs nothing today
    (the corpus contains no such artifact) and forces the provenance contract to
    exist before the first one lands. Defining that contract belongs to #1316,
    "document corpus standard for generated content", whose own done-criteria
    include the enforcement and exception process -- this validator refuses what it
    cannot establish rather than deciding it, which the issue puts out of scope.
    """
    errors: list[str] = []
    for path in sorted(corpus_root.rglob("*")):
        if path.is_dir() or path.suffix == ".md" or _is_excluded(path, corpus_root):
            continue
        rel = path.relative_to(corpus_root)
        if "generated" in rel.parts[:-1]:
            errors.append(
                f"{rel}: generated artifact whose provenance and reproducibility "
                "cannot be established -- no corpus generator exists yet to "
                "reproduce it from canonical Markdown (ADR-0028); see #1316"
            )
            continue
        errors.append(
            f"{rel}: non-.md file outside generated/ -- misplaced generated "
            "artifact, or hand-authored content in the wrong format"
        )
    return errors


def validate_corpus(corpus_root: Path, *, check_links: bool = False) -> ValidationReport:
    """Validate the corpus at `corpus_root`, returning errors and unverified notices."""
    root = repo_root()
    nodes = load_nodes(corpus_root)

    report = ValidationReport(errors=[n.error for n in nodes if n.error])
    report.errors.extend(find_duplicate_ids(nodes))
    report.errors.extend(find_unresolved_relationship_targets(nodes))
    report.errors.extend(find_non_finite_confidence(nodes))

    citation_errors, citation_unverified = find_citation_problems(nodes, root, check_links=check_links)
    report.errors.extend(citation_errors)
    report.unverified.extend(citation_unverified)

    report.errors.extend(find_non_canonical_nodes(corpus_root))
    report.errors.extend(find_ownership_violations(corpus_root))

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help=f"corpus root (default: {DEFAULT_ROOT})")
    parser.add_argument(
        "--check-links",
        action="store_true",
        help="open HTTP(S) citations and fail unreachable targets",
    )
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else repo_root() / DEFAULT_ROOT

    try:
        report = validate_corpus(root, check_links=args.check_links)
    except CorpusRootMissing as exc:
        print(f"FAIL  corpus root does not exist: {exc}", file=sys.stderr)
        return 1

    for notice in report.unverified:
        print(f"UNVERIFIED  {notice}", file=sys.stderr)

    if report.errors or report.unverified:
        for error in report.errors:
            print(f"FAIL  {error}", file=sys.stderr)
        if report.unverified:
            print(
                f"FAIL  {len(report.unverified)} unverified citation(s) block validation",
                file=sys.stderr,
            )
        if report.errors:
            print(f"FAIL  {len(report.errors)} corpus validation error(s)", file=sys.stderr)
        return 1

    print("PASS  corpus validation clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

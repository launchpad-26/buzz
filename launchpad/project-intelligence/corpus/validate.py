"""Deterministic corpus validator -- issue #623.

One local and CI command that rejects structurally invalid corpus changes,
enforcing the schema #622 defined (launchpad/docs/corpus/schema/node.schema.json)
plus the cross-node and content rules a single document's schema validation
cannot express on its own: duplicate ids, unresolved relationship targets,
unverifiable/prohibited evidence citations, and stray non-canonical files.

Citations are parsed against CONTRACT.md section 3's six forms before anything is
checked, and reported in two channels -- hard errors, and an `UNVERIFIED` channel
for the forms that name nothing openable (see ValidationReport). Exit status is 1
for any error, 0 otherwise; unverified notices never fail a run, but they always
print, so a PASS never claims more than was actually checked.

Run:  python3 launchpad/project-intelligence/corpus/validate.py [--root PATH]
  or: just corpus-validate
"""

from __future__ import annotations

import argparse
import json
import re
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


@dataclass
class ValidationReport:
    """What one validation run found.

    Two channels, deliberately separate. `errors` are hard failures: the run exits
    non-zero. `unverified` names what this validator recognised as a legitimate
    citation or artifact but genuinely cannot check offline -- a commit reference,
    a graph edge, a tool result, an external URL, a generated projection with no
    generator to reproduce it from. `launchpad/project-intelligence/CONTRACT.md`
    section 3 states that discipline directly: "parse what is parseable, and report
    the rest as unverified rather than skipping it". Silently passing them (what an
    earlier revision did) makes a clean PASS mean less than it claims.
    """

    errors: list[str] = field(default_factory=list)
    unverified: list[str] = field(default_factory=list)


# A node's `id` is only trustworthy for display AFTER schema validation -- the
# schema constrains it to kebab-case, but a node that fails schema validation can
# carry any string at all, including a path the DoD's "without leaking private
# source content" forbids echoing. So every message names the node through this
# helper: a schema-shaped id, or else the file path (never private content -- it
# is a path inside this repository, which the run already walked).
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

    nodes: list[LoadedNode] = []
    for path in discover_markdown_files(corpus_root):
        try:
            data = _load_frontmatter(path)
        except (ValueError, yaml.YAMLError) as exc:
            nodes.append(LoadedNode(path=path, error=f"{path}: {exc}"))
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
    paths_by_id: dict[object, list[Path]] = {}
    for node in nodes:
        if node.id is None:
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
_URL_PREFIXES = ("http://", "https://")
_MARKDOWN_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<target>[^)\s]+)\)$")
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
# GitHub's two file-URL shapes. The capture is the ref segment -- a branch, a tag,
# or a commit SHA -- which ADR-0003 requires to be a full SHA.
_GITHUB_FILE_URL_RE = re.compile(
    r"^https://github\.com/[^/\s]+/[^/\s]+/(?:blob|raw|tree)/(?P<ref>[^/\s]+)/\S+$"
)
_RAW_GITHUB_URL_RE = re.compile(
    r"^https://raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/(?P<ref>[^/\s]+)/\S+$"
)
_COMMIT_CITATION_RE = re.compile(r"^commit\s+[0-9a-fA-F]{7,40}\b")
_FILE_POSITION_RE = re.compile(r"^(?P<path>\S+?):(?P<start>\d+)(?:-(?P<end>\d+))?$")
# Graph edges (`a -> b (1 hop)`) and tool results (`find_references(...) -> none`)
# share this separator, and neither names a file.
_CITATION_ARROW = " -> "


@dataclass(frozen=True)
class CitationVerdict:
    """One citation's outcome. `detail` NEVER contains the citation value itself --
    every message this module emits is safe to print in CI logs."""

    status: str  # "ok" | "error" | "unverified"
    detail: str = ""


def _classify_url(url: str) -> CitationVerdict:
    """A repository file link must be pinned to a full commit SHA; other URLs can't be.

    ADR-0003 fixes the reference format as "a markdown link to the cited file at the
    pinned commit, using the full SHA. Never `blob/main`", and the schema README
    repeats it. A `blob/main` link is evidence that can change underneath a green
    validation run, which is the whole failure mode provenance exists to prevent.

    A URL that is not a repository file link (a spec, a blog post, an upstream
    issue) has no commit to pin to and no offline way to check it, so it is
    reported unverified rather than either failed or silently passed.
    """
    for pattern in (_GITHUB_FILE_URL_RE, _RAW_GITHUB_URL_RE):
        match = pattern.match(url)
        if match:
            if _FULL_SHA_RE.match(match.group("ref")):
                return CitationVerdict("ok")
            return CitationVerdict(
                "error",
                "is a repository file link pinned to a mutable ref rather than a "
                "full commit SHA (ADR-0003)",
            )
    return CitationVerdict(
        "unverified", "is an external URL this validator can neither pin nor open"
    )


def _classify_repo_path(path_text: str, repo_root_path: Path) -> CitationVerdict:
    """A repo-relative citation must resolve to a real file INSIDE the repository.

    Three distinct rejections, in order:

    Prohibited credential-like names are rejected first and without echoing the
    value -- the DoD's "without leaking private source content".

    An absolute path (e.g. /etc/passwd) is rejected explicitly rather than
    existence-checked: pathlib's `/` operator silently discards the left operand
    when the right is absolute, so `repo_root_path / "/etc/passwd"` would otherwise
    evaluate to `/etc/passwd` itself and "validate" against the host filesystem.

    Containment is then enforced on the RESOLVED path, not the literal one. An
    earlier revision checked only `(repo_root_path / citation).exists()`, so
    `../../../../etc/passwd` escaped the repository entirely and a bare directory
    name like `launchpad` passed as though it were a file. Resolving first also
    means a symlink pointing out of the tree is caught, not followed.
    """
    if _is_prohibited_citation(path_text):
        return CitationVerdict(
            "error", "matches a prohibited credential-like pattern"
        )
    if PurePosixPath(path_text).is_absolute():
        return CitationVerdict(
            "error", "must be a repo-relative path, not absolute"
        )

    root = repo_root_path.resolve()
    candidate = (root / path_text).resolve()
    if not candidate.is_relative_to(root):
        return CitationVerdict(
            "error", "resolves outside the repository"
        )
    if not candidate.is_file():
        return CitationVerdict(
            "error", "does not resolve to a real file in the repository"
        )
    return CitationVerdict("ok")


def _classify_citation(citation: str, repo_root_path: Path) -> CitationVerdict:
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

    if text.startswith(_URL_PREFIXES):
        return _classify_url(text)

    if _COMMIT_CITATION_RE.match(text):
        return CitationVerdict(
            "unverified", "is a commit reference, which names no openable file"
        )

    if _CITATION_ARROW in text:
        return CitationVerdict(
            "unverified",
            "is a graph-edge or tool-result citation, which names no openable file",
        )

    position = _FILE_POSITION_RE.match(text)
    if position:
        start = int(position.group("start"))
        end = position.group("end")
        # Only the position's internal consistency is checked, not whether the file
        # is actually that long. Bounds-checking line numbers against file contents
        # is real staleness detection and belongs with the staleness work, not here.
        if start < 1 or (end is not None and int(end) < start):
            return CitationVerdict("error", "carries a malformed line position")
        return _classify_repo_path(position.group("path"), repo_root_path)

    if any(character.isspace() for character in text):
        return CitationVerdict(
            "error",
            "matches none of CONTRACT.md's six supported citation forms",
        )

    return _classify_repo_path(text, repo_root_path)


def find_citation_problems(
    nodes: list[LoadedNode], repo_root_path: Path
) -> tuple[list[str], list[str]]:
    """Classify every evidence citation; return (errors, unverified).

    Citations are located by position -- "evidence entry 2, citation 1" -- rather
    than by quoting them, so an author can find the offender without this validator
    ever printing a value it was asked to reject.

    Nodes with `node.error` already set are skipped -- see
    find_unresolved_relationship_targets's docstring for why.
    """
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
                verdict = _classify_citation(citation, repo_root_path)
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


def find_ownership_violations(corpus_root: Path) -> tuple[list[str], list[str]]:
    """Enforce ADR-0028's canonical-vs-generated boundary; return (errors, unverified).

    Every non-`.md` file (schema/ excluded) must live under a `generated/`
    subdirectory: hand-authored content is Markdown+frontmatter, anything else must
    be clearly segregated as a generated projection, never interleaved with
    authored nodes. That placement rule is an error when broken.

    Placement is only half of what ADR-0028 asks, though. It also requires derived
    views to be "never hand-authored, always reproducible from canonical Markdown",
    and placement alone proves neither -- a file hand-written straight into
    `generated/` is indistinguishable from a real projection. Verifying the rest
    means regenerating and comparing, and no corpus generator exists yet to
    regenerate from. So each artifact is reported unverified rather than passed in
    silence: the check that cannot run yet stays visible instead of reading as a
    check that ran and was satisfied. Deciding the provenance contract those
    artifacts should carry is a corpus-generator decision, explicitly out of this
    issue's scope ("deciding unresolved ADR outcomes").
    """
    errors: list[str] = []
    unverified: list[str] = []
    for path in sorted(corpus_root.rglob("*")):
        if path.is_dir() or path.suffix == ".md" or _is_excluded(path, corpus_root):
            continue
        rel = path.relative_to(corpus_root)
        if "generated" in rel.parts[:-1]:
            unverified.append(
                f"{rel}: generated artifact whose generator provenance and "
                "reproducibility cannot be checked -- no corpus generator exists "
                "yet to reproduce it from canonical Markdown (ADR-0028)"
            )
            continue
        errors.append(
            f"{rel}: non-.md file outside generated/ -- misplaced generated "
            "artifact, or hand-authored content in the wrong format"
        )
    return errors, unverified


def validate_corpus(corpus_root: Path) -> ValidationReport:
    """Validate the corpus at `corpus_root`, returning errors and unverified notices."""
    root = repo_root()
    nodes = load_nodes(corpus_root)

    report = ValidationReport(errors=[n.error for n in nodes if n.error])
    report.errors.extend(find_duplicate_ids(nodes))
    report.errors.extend(find_unresolved_relationship_targets(nodes))

    citation_errors, citation_unverified = find_citation_problems(nodes, root)
    report.errors.extend(citation_errors)
    report.unverified.extend(citation_unverified)

    ownership_errors, ownership_unverified = find_ownership_violations(corpus_root)
    report.errors.extend(ownership_errors)
    report.unverified.extend(ownership_unverified)

    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=None, help=f"corpus root (default: {DEFAULT_ROOT})")
    args = parser.parse_args(argv)

    root = Path(args.root) if args.root else repo_root() / DEFAULT_ROOT

    try:
        report = validate_corpus(root)
    except CorpusRootMissing as exc:
        print(f"FAIL  corpus root does not exist: {exc}", file=sys.stderr)
        return 1

    # Printed whether or not the run fails: an unverified citation is not a defect,
    # but a run that hid them would let "PASS" claim more than it checked.
    for notice in report.unverified:
        print(f"UNVERIFIED  {notice}", file=sys.stderr)

    if report.errors:
        for error in report.errors:
            print(f"FAIL  {error}", file=sys.stderr)
        print(f"FAIL  {len(report.errors)} corpus validation error(s)", file=sys.stderr)
        return 1

    if report.unverified:
        print(
            f"PASS  corpus validation found no errors; {len(report.unverified)} "
            "item(s) reported unverified"
        )
    else:
        print("PASS  corpus validation clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())

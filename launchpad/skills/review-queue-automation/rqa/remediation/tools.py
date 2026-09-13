"""The closed formatter registry, the exact argv builder and the behavior-equivalence
oracles — `code/P-10-remediation.md` §2 and §4.

Nothing here decides whether a finding *should* be remediated; `rqa.policy` decides what
a repository may configure and `rqa.judgement` decides candidacy. This module decides the
narrower question `CONTRACTS.md` §11 makes unweakenable: which tools RQA is willing to run
at all, exactly which argv each one is allowed to be invoked with, and whether the bytes a
tool actually produced are provably behavior-equivalent to the bytes it was given.

Three properties this module exists to hold:

* **Closed.** `MECHANICAL_TOOL_SET` is a `MappingProxyType` over five literal rows. Policy
  can name a subset of them; it cannot add a row, change a row's argv, or point a row at a
  different oracle. There is no registration hook, no entry-point scan and no environment
  read — adding a tool is a source change reviewed against §4's table.
* **Exact.** `build_argv` appends only paths that already passed `validate_remedy_paths`,
  and re-checks their syntax itself. A remedy path is attacker-influenced data: it never
  becomes an option, never becomes a pathspec magic word, and never becomes a glob.
* **Fail-closed.** `semantic_fingerprint` returns `None` for a parse error, an unsupported
  construct, an unavailable oracle or any internal failure, and `None` is always a
  refusal at the call site — never an optimistic pass.

**Oracle availability.** Only `python_ast_v1` can be computed in this process: the standard
library ships a Python parser and ships no parser for TypeScript, Go, Rust or Dart. The
other four oracles are registered, named and closed, but return `None` here because no
sound in-process implementation exists, and `None` refuses. That is deliberate and is the
fail-closed direction: an oracle RQA cannot run is an oracle RQA does not trust, so its
tool cannot reach a branch. Shelling out to an unregistered parser would be the opposite —
a behavior claim made by a process this module has not vouched for.
"""

from __future__ import annotations

import ast
import hashlib
import io
import posixpath
import tokenize
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from rqa.contracts import Facts, Finding, ProcessResult, Remedy

__all__ = [
    "MECHANICAL_TOOL_SET",
    "RemediationError",
    "ToolSpec",
    "build_argv",
    "check_passed",
    "semantic_fingerprint",
    "validate_remedy_paths",
]


class RemediationError(Exception):
    """Programming error: E-10 received a wrong grant or internally inconsistent facts."""


@dataclass(frozen=True)
class ToolSpec:
    """One registry row. §2's field list exactly; nothing is added to it."""

    id: str
    fix_argv: tuple[str, ...]  # exact validated file paths appended
    check_id: str  # must equal Remedy.check
    check_argv: tuple[str, ...]  # exact validated file paths appended
    extensions: frozenset[str]
    equivalence_id: str  # names one closed semantic_fingerprint implementation
    neutrality_contract: str


# --------------------------------------------------------------------------
# §4's closed registry — five rows, verbatim.
# --------------------------------------------------------------------------

#: The neutrality claim every oracle makes, quoted from §4 so a reviewer comparing the
#: table with this file compares the same sentence.
_NEUTRALITY = (
    "rejects parse errors and hashes a normalized parser AST with source positions "
    "removed while retaining literal values, directives, ordered comments/doc "
    "attributes and macro token trees; any unsupported construct refuses remediation; "
    "import sorting/fixing is absent"
)

MECHANICAL_TOOL_SET: Mapping[str, ToolSpec] = MappingProxyType(
    {
        "ruff-format": ToolSpec(
            id="ruff-format",
            fix_argv=("ruff", "format"),
            check_id="ruff-format-check",
            check_argv=("ruff", "format", "--check"),
            extensions=frozenset({".py", ".pyi"}),
            equivalence_id="python_ast_v1",
            neutrality_contract=_NEUTRALITY,
        ),
        "prettier": ToolSpec(
            id="prettier",
            fix_argv=("prettier", "--write"),
            check_id="prettier-check",
            check_argv=("prettier", "--check"),
            extensions=frozenset({".js", ".jsx", ".ts", ".tsx"}),
            equivalence_id="typescript_estree_v1",
            neutrality_contract=_NEUTRALITY,
        ),
        "gofmt": ToolSpec(
            id="gofmt",
            fix_argv=("gofmt", "-w"),
            check_id="gofmt-check",
            # §4: the check is an *empty* `gofmt -d`. `gofmt -d` exits zero whether or
            # not it printed a diff, so `check_passed` requires empty stdout for this
            # row; a returncode alone would accept an unformatted file.
            check_argv=("gofmt", "-d"),
            extensions=frozenset({".go"}),
            equivalence_id="go_ast_v1",
            neutrality_contract=_NEUTRALITY,
        ),
        "rustfmt": ToolSpec(
            id="rustfmt",
            fix_argv=("rustfmt",),
            check_id="rustfmt-check",
            check_argv=("rustfmt", "--check"),
            extensions=frozenset({".rs"}),
            equivalence_id="rust_syn_v1",
            neutrality_contract=_NEUTRALITY,
        ),
        "dart-format": ToolSpec(
            id="dart-format",
            fix_argv=("dart", "format"),
            check_id="dart-format-check",
            check_argv=("dart", "format", "--output=none", "--set-exit-if-changed"),
            extensions=frozenset({".dart"}),
            equivalence_id="dart_analyzer_v1",
            neutrality_contract=_NEUTRALITY,
        ),
    }
)

#: Rows whose registered check reports through stdout rather than through its exit
#: status. `gofmt -d` prints the diff it would apply and still exits zero.
_EMPTY_STDOUT_CHECKS: frozenset[str] = frozenset({"gofmt"})


def check_passed(*, spec: ToolSpec, result: ProcessResult) -> bool:
    """Did the registered check argv report a clean tree?

    Zero exit for every row, and additionally empty stdout for the rows in
    `_EMPTY_STDOUT_CHECKS`, because §4 registers `gofmt`'s check as an *empty* `gofmt -d`.
    """
    if result.returncode != 0:
        return False
    if spec.id in _EMPTY_STDOUT_CHECKS:
        return result.stdout == b""
    return True


# --------------------------------------------------------------------------
# Exact path syntax. A remedy path is untrusted data authored by the PR's own
# reviewer input, so every rule here is about what it may never become.
# --------------------------------------------------------------------------

#: Glob metacharacters. P-10 calls no path matcher (§1, §7), so a path that could be
#: read as a pattern by anything downstream is refused rather than expanded.
_GLOB_METACHARACTERS = frozenset("*?[]{}")

#: Characters that change an argument's meaning to git or to a shell-like consumer.
_FORBIDDEN_CHARACTERS = frozenset("\\:\x00")

_MAX_PATH_LENGTH = 1024


def _exact_repository_path(path: object) -> bool:
    """Is `path` an exact, normalized, repository-relative file path?

    Never an option, never absolute, never a pathspec magic word, never a glob, never a
    traversal, never a directory, never anything a terminal or a log would have to
    escape.
    """
    if not isinstance(path, str) or not path or len(path) > _MAX_PATH_LENGTH:
        return False
    if any(character < " " or character == "\x7f" for character in path):
        return False
    if _FORBIDDEN_CHARACTERS & set(path):
        return False
    if _GLOB_METACHARACTERS & set(path):
        return False
    if path.startswith("-") or path.startswith("/") or path.startswith("~"):
        return False
    segments = path.split("/")
    if any(segment in ("", ".", "..") for segment in segments):
        return False
    if any(segment != segment.strip() for segment in segments):
        return False
    return posixpath.normpath(path) == path


def build_argv(*, prefix: tuple[str, ...], paths: tuple[str, ...]) -> tuple[str, ...]:
    """Append only paths already accepted by validate_remedy_paths."""
    if not isinstance(paths, tuple) or not paths:
        raise RemediationError("build_argv requires a non-empty tuple of paths")
    for path in paths:
        if not _exact_repository_path(path):
            raise RemediationError(f"{path!r} is not an exact repository-relative file path")
    return tuple(prefix) + paths


def validate_remedy_paths(*, remedy: Remedy, facts: Facts, finding: Finding) -> bool:
    """Exact, unique normalized changed files; known bytes; location included; tool/check/extensions match."""
    spec = MECHANICAL_TOOL_SET.get(remedy.tool)
    if spec is None or remedy.check != spec.check_id:
        return False
    paths = remedy.paths
    if not isinstance(paths, tuple) or not paths:
        return False
    if len(set(paths)) != len(paths):
        return False
    for path in paths:
        if not _exact_repository_path(path):
            return False
        if path not in facts.changed_paths or path not in facts.files:
            return False
        if posixpath.splitext(path)[1] not in spec.extensions:
            return False
    return finding.location.path in paths


# --------------------------------------------------------------------------
# Behavior-equivalence oracles (`CONTRACTS.md` §11).
# --------------------------------------------------------------------------


def _python_comments(text: str) -> tuple[str, ...] | None:
    """Every comment token in source order, trailing whitespace removed.

    Python's AST carries no comments, and `# fmt: off`-style directives are comments, so
    an AST-only fingerprint would call a formatter that dropped or reordered one
    equivalent. `None` when the source does not tokenize.
    """
    comments: list[str] = []
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                comments.append(token.string.rstrip())
    except (tokenize.TokenError, SyntaxError, IndentationError, ValueError, MemoryError):
        return None
    return tuple(comments)


def _python_source_text(content: bytes) -> str | None:
    """`content` decoded under the encoding the *source itself* declares (PEP 263).

    Assuming UTF-8 is a soundness hole, not a simplification (G2194-P10-F5): under a
    `# coding: latin-1` header the bytes `C3 A9` are the two characters `Ã©`, while a
    UTF-8 decode makes them the one character `é` — so two sources whose real string
    values differ would fingerprint identically and a behavior-changing edit would pass as
    behavior-preserving. `None` when no declared encoding can decode the bytes.
    """
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(content).readline)
        return content.decode(encoding)
    except (SyntaxError, UnicodeDecodeError, ValueError, LookupError, MemoryError):
        return None


def _python_ast_v1(*, path: str, content: bytes) -> bytes | None:
    """Normalized CPython AST plus ordered comments, positions removed.

    Literal values, docstrings, argument order, decorators and directives are all in the
    digest; line breaks, indentation, quote style, magic trailing commas and parentheses
    are not — which is exactly the set a formatter is permitted to change.

    The parse is over the **bytes**, so `compile()` applies the source's own PEP 263
    encoding declaration and every literal in the AST carries the value CPython would give
    it at runtime. The comment stream is read from the same bytes decoded the same way.
    """
    try:
        tree = ast.parse(content, filename=path)
        dumped = ast.dump(tree, annotate_fields=True, include_attributes=False)
    except (SyntaxError, ValueError, RecursionError, MemoryError):
        return None
    text = _python_source_text(content)
    if text is None:
        return None
    comments = _python_comments(text)
    if comments is None:
        return None
    digest = hashlib.sha256()
    digest.update(b"python_ast_v1\x00")
    digest.update(dumped.encode("utf-8"))
    for comment in comments:
        digest.update(b"\x00")
        digest.update(comment.encode("utf-8"))
    return digest.digest()


def _unavailable(*, path: str, content: bytes) -> None:
    """A registered oracle with no in-process parser available.

    Returning `None` refuses the remediation. An oracle that cannot be computed must never
    be reported as equivalence: `CONTRACTS.md` §11 requires the check to *prove* the actual
    before/after pair equivalent before P-10 may commit or push.
    """
    return None


_ORACLES: Mapping[str, Callable[..., bytes | None]] = MappingProxyType(
    {
        "python_ast_v1": _python_ast_v1,
        "typescript_estree_v1": _unavailable,
        "go_ast_v1": _unavailable,
        "rust_syn_v1": _unavailable,
        "dart_analyzer_v1": _unavailable,
    }
)


def semantic_fingerprint(*, oracle: str, path: str, content: bytes) -> bytes | None:
    """Parser-derived behavior fingerprint; None on parse/unsupported/error."""
    implementation = _ORACLES.get(oracle)
    if implementation is None:
        return None
    try:
        return implementation(path=path, content=content)
    except Exception:  # noqa: BLE001 - an oracle that fails is an oracle that refuses
        return None

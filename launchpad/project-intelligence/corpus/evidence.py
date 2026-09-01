"""Git and GitHub evidence bundle collection for corpus nodes -- issue #625.

Assembles a reproducible bundle of evidence for ONE planned corpus node: code,
tests and specs read from this repository, plus commits, pull-request reviews,
pull-request comments and issue discussion pulled through a `GitHubClient`.
This is a working-notes artifact for whoever authors the node next (issue
#629's corpus-author skill) -- it is not the node's own front-matter
`evidence:` ledger, and it does not itself classify anything FACT, INFERENCE
or TEAM_KNOWLEDGE. `launchpad/docs/corpus/AGENTS.md` reserves that judgment
for whoever opens the sources and writes the node.

What this module guarantees instead, per #625's definition of done:

- Every entry carries a stable identifier (a repo-relative path, a commit
  SHA, a `pr:<n>`/`issue:<n>` reference, or a comment id) and a URL where one
  exists, never unattributed copied prose.
- `evidence_class` keeps code, commits, PR reviews, PR comments, issue
  discussion and ADRs distinguishable from each other.
- `fact_eligible` is always `False` for the three discussion classes
  (`pr_review`, `pr_comment`, `issue_discussion`) -- historical discussion can
  be bundled for context, but this module never marks it eligible for
  promotion to `FACT`; only a human opening the source does that, and only
  for classes where opening the source means something (code, tests, specs,
  commits, ADRs).
- Two entries sharing a `claim_key` with different `value`s are always
  surfaced in `conflicts`, never silently resolved -- `AGENTS.md`'s citation
  of ADR-0029: "record the conflict and leave the node flagged for a human
  rather than resolving it yourself."
- A code/test/spec path matching a credential-shaped name is refused, not
  bundled -- the same short, exact list `validate.py` uses, not a broad
  substring guess (see `_is_credential_like_path`).

Run as a library, not a CLI -- callers (the future corpus-author skill,
tests) construct entries with `collect_*` and assemble them with
`build_bundle`. There is no `main()`.
"""

from __future__ import annotations

import http.client
import json
import enum
import re
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath

# The same short, exact credential-shaped list validate.py uses (see its
# _is_prohibited_citation) -- deliberately not broad substrings like
# *auth*/*token*/*secret*, which would reject real, ordinary, non-secret
# paths such as crates/buzz-auth/. Kept in sync by hand; both modules cite
# the same rationale so a future edit to one is a prompt to check the other.
_CREDENTIAL_LIKE_BASENAME_PREFIXES = ("id_rsa", "id_ed25519")
_CREDENTIAL_LIKE_EXTENSIONS = {".pem", ".key"}
_ENV_SAFE_SUFFIXES = (".example", ".sample", ".template")

# Discussion classes never eligible for FACT promotion by this module --
# opening the source (a review or a comment) never establishes present
# repository truth, only that someone said something at some point.
# Code/test/spec/commit/ADR classes ARE eligible -- eligible, not
# automatically FACT; the author still has to open the source, per
# AGENTS.md.
_TEAM_KNOWLEDGE_ONLY_CLASSES = {"pr_review", "pr_comment", "issue_discussion"}

_VALID_CLASSES = {
    "code",
    "test",
    "spec",
    "commit",
    "pr_review",
    "pr_comment",
    "issue_discussion",
    "adr",
}


class EvidenceKind(enum.Enum):
    LOCAL_FILE = "local_file"
    LOCAL_FILE_LINE = "local_file_line"
    LOCAL_FILE_RANGE = "local_file_range"
    COMMIT = "commit"
    GITHUB_URL = "github_url"
    EXTERNAL_URL = "external_url"
    GRAPH_EDGE = "graph_edge"
    TOOL_RESULT = "tool_result"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ParsedCitation:
    kind: EvidenceKind
    path: str | None = None
    start_line: int | None = None
    end_line: int | None = None
    commit: str | None = None
    url: str | None = None
    # Tool-result citations only. `tool_assertion` is captured so a detail can
    # say it went uncompared -- never so a verifier can judge it. See
    # `_verify_git_tool` for why comparing it is not on offer.
    tool: str | None = None
    tool_args: str | None = None
    tool_assertion: str | None = None


_PARSE_URL_PREFIXES = ("http://", "https://")
_PARSE_MARKDOWN_LINK_RE = re.compile(r"^\[[^\]]*\]\((?P<target>[^)\s]+)\)$")
_PARSE_COMMIT_RE = re.compile(r"^commit\s+(?P<sha>[0-9a-fA-F]{7,40})\b")
_PARSE_FILE_POSITION_RE = re.compile(
    r"^(?P<path>\S+?):(?P<start>\d+)(?:-(?P<end>\d+))?$"
)
_PARSE_SYMBOL = r"[A-Za-z_][A-Za-z0-9_.:]*"
_PARSE_GRAPH_EDGE_RE = re.compile(
    rf"^{_PARSE_SYMBOL} -> {_PARSE_SYMBOL} \(\d+ hops?\)$"
)
_PARSE_TOOL_RESULT_RE = re.compile(
    rf"^(?P<tool>{_PARSE_SYMBOL})\((?P<args>.*)\) -> (?P<assertion>.+)$"
)


def _parse_url_target(text: str) -> str:
    return text.split()[0].rstrip(",.;")


def parse_citation(citation: str) -> ParsedCitation:
    """Parse one citation into a typed, normalized evidence reference.

    Parsing identifies the evidence kind only. It does not claim the source is
    valid or reachable; that is the verifier layer's responsibility.
    """
    text = citation.strip()
    link = _PARSE_MARKDOWN_LINK_RE.match(text)
    if link:
        text = link.group("target")
    if text.startswith(_PARSE_URL_PREFIXES):
        target = _parse_url_target(text)
        kind = (
            EvidenceKind.GITHUB_URL
            if "github.com/" in target or "raw.githubusercontent.com/" in target
            else EvidenceKind.EXTERNAL_URL
        )
        return ParsedCitation(kind=kind, url=target)
    commit = _PARSE_COMMIT_RE.match(text)
    if commit:
        return ParsedCitation(kind=EvidenceKind.COMMIT, commit=commit.group("sha"))
    if _PARSE_GRAPH_EDGE_RE.match(text):
        return ParsedCitation(kind=EvidenceKind.GRAPH_EDGE)
    tool_result = _PARSE_TOOL_RESULT_RE.match(text)
    if tool_result:
        return ParsedCitation(
            kind=EvidenceKind.TOOL_RESULT,
            tool=tool_result.group("tool"),
            tool_args=tool_result.group("args"),
            tool_assertion=tool_result.group("assertion"),
        )
    position = _PARSE_FILE_POSITION_RE.match(text)
    if position:
        end = position.group("end")
        return ParsedCitation(
            kind=(
                EvidenceKind.LOCAL_FILE_RANGE
                if end is not None
                else EvidenceKind.LOCAL_FILE_LINE
            ),
            path=position.group("path"),
            start_line=int(position.group("start")),
            end_line=int(end) if end is not None else int(position.group("start")),
        )
    if text and not any(character.isspace() for character in text):
        return ParsedCitation(kind=EvidenceKind.LOCAL_FILE, path=text)
    return ParsedCitation(kind=EvidenceKind.UNKNOWN)



@dataclass(frozen=True)
class VerificationResult:
    status: str  # "ok" | "error" | "unverified"
    detail: str = ""


# The verdict for an evidence kind no verifier covers. Shared with `validate.py`
# so the two modules cannot drift apart on the wording, which corpus nodes quote
# verbatim as a FACT about checker behaviour
# (`standards/test-references.md`). Change it in one place or not at all.
UNVERIFIABLE_KIND_DETAIL = (
    "is a graph-edge or tool-result citation, which names no openable file"
)


def _verification_line_count(path: Path) -> int:
    data = path.read_bytes()
    return data.count(b"\n") + bool(data and not data.endswith(b"\n"))


def _verify_local(parsed: ParsedCitation, repo_root: Path) -> VerificationResult:
    assert parsed.path is not None
    if _is_credential_like_path(parsed.path):
        return VerificationResult("error", "matches a prohibited credential-like pattern")
    if PurePosixPath(parsed.path).is_absolute():
        return VerificationResult("error", "must be a repo-relative path, not absolute")
    resolved_root = repo_root.resolve()
    try:
        candidate = (resolved_root / parsed.path).resolve()
    except (OSError, RuntimeError):
        return VerificationResult("error", "cannot be resolved to a path")
    if not candidate.is_relative_to(resolved_root):
        return VerificationResult("error", "resolves outside the repository")
    if not candidate.is_file():
        return VerificationResult("error", "does not resolve to a real file in the repository")
    if parsed.end_line is not None and parsed.end_line > _verification_line_count(candidate):
        return VerificationResult("error", "line position exceeds the cited file's length")
    return VerificationResult("ok")


def _verify_commit(parsed: ParsedCitation, repo_root: Path) -> VerificationResult:
    assert parsed.commit is not None
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{parsed.commit}^{{commit}}"],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0:
        return VerificationResult("ok")
    return VerificationResult("error", "names a commit that does not exist in this repository")


# Tool-result citations naming read-only git plumbing. This verifier is
# deliberately FAIL-ONLY: it can report `error` when a cited source is gone, and
# otherwise leaves the citation blocking as `unverified`. It never returns `ok`.
#
# The reason is measured, not stylistic. Across the corpus's 80 `git_ls_tree` /
# `git_show` citations, only ONE asserted result is a machine-comparable list.
# 41 carry negations ("no layers/ directory present"), 30 are partial-list
# hedges ("includes ..."), 33 use globs (`schema/**`), 36 append provenance
# ("run 2026-08-27"). A strict comparator would fail ~79 true citations; a
# lenient one would pass vacuously on every "includes" and could not evaluate a
# negation at all. Neither earns a pass, so neither is offered.
#
# What IS checkable is whether the cited source still resolves, and that has
# immediate teeth: 10 of the 14 distinct refs cited across the corpus name
# task branches deleted after their PRs merged.
_GIT_TOOL_NAMES = {"git_ls_tree", "git.ls_tree", "git_show"}

# Refused before any process is spawned. Corpus prose is the input here, so a
# citation is untrusted text; these never appear in a legitimate ref or path
# (measured: 0 occurrences across all 80 citations).
_GIT_ARG_SHELL_METACHARACTERS = (";", "$(", "`", "|", "&", "\n", "\r", ">", "<")

_GIT_KWARG_RE = re.compile(r"(?:^|,)\s*(?P<key>ref|path|commit)\s*=\s*(?P<value>[^,]+)")


def _strip_argument_quotes(value: str) -> str:
    return value.strip().strip("'\"").strip()


def _parse_git_tool_arguments(args: str) -> tuple[str, str] | None:
    """Reduce a citation's argument text to a `(ref, path)` pair, or `None`.

    Three shapes occur in the corpus and all three are accepted: keyword
    (`ref=..., path=...`, quoted or not), `git_show`'s combined
    `'<sha>:<path>'`, and bare positional. A third argument is ignored -- it is
    always a human annotation ("run 2026-08-27"), never an argument git takes.
    """
    text = args.strip()
    if not text:
        return None

    keywords = {
        match.group("key"): _strip_argument_quotes(match.group("value"))
        for match in _GIT_KWARG_RE.finditer(text)
    }
    if keywords:
        ref = keywords.get("ref") or keywords.get("commit")
        path = keywords.get("path")
        if ref and path:
            return (ref, path)
        return None

    fields = [_strip_argument_quotes(field) for field in text.split(",")]
    fields = [field for field in fields if field]
    if len(fields) == 1 and ":" in fields[0]:
        ref, _, path = fields[0].partition(":")
        if ref and path:
            return (ref, path)
        return None
    if len(fields) >= 2 and fields[0] and fields[1]:
        return (fields[0], fields[1])
    return None


def _git_object_exists(repo_root: Path, revision: str) -> bool:
    """Resolve a revision through git plumbing, as an argument list.

    Never a shell string, and never with the citation's text in command
    position -- the value only ever lands in an argument slot after the
    metacharacter and option-shape guards in `_verify_git_tool` have passed.
    """
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", revision],
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def _is_shallow_repository(repo_root: Path) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() == "true"


def _remote_tracking_refs_present(repo_root: Path, remote: str) -> bool:
    result = subprocess.run(
        ["git", "for-each-ref", "--format=%(refname)", f"refs/remotes/{remote}/"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    return bool(result.stdout.strip())


def _missing_ref_is_conclusive(repo_root: Path, ref: str) -> bool:
    """Whether this checkout has standing to call a missing ref an error.

    Shallowness truncates history DEPTH, not the ref LIST -- a `--depth 1`
    clone of one branch has neither, but a clone that fetched every branch and
    shortened their history has a complete ref list. So the two cases split:

    - a remote-tracking NAME (`origin/task/...`): conclusive whenever this
      checkout holds any refs for that remote, because then the branch list was
      fetched and this name is not in it.
    - a bare SHA: conclusive only in a full clone, since a shortened history is
      exactly what makes an old commit unreachable here but real upstream.

    Without this split the verifier either accuses citations a shallow CI
    checkout cannot judge, or -- worse -- silently stops reporting genuine rot
    to anyone whose clone happens to be shallow.
    """
    remote, _, branch = ref.partition("/")
    if branch and _remote_tracking_refs_present(repo_root, remote):
        return True
    return not _is_shallow_repository(repo_root)


def _verify_git_tool(parsed: ParsedCitation, repo_root: Path) -> VerificationResult:
    assert parsed.tool_args is not None
    if any(token in parsed.tool_args for token in _GIT_ARG_SHELL_METACHARACTERS):
        return VerificationResult(
            "unverified",
            "names read-only git plumbing but its arguments contain a shell "
            "metacharacter, so it was not replayed",
        )
    arguments = _parse_git_tool_arguments(parsed.tool_args)
    if arguments is None:
        return VerificationResult(
            "unverified",
            "names read-only git plumbing but its arguments could not be parsed "
            "into a ref and a path, so it was not replayed",
        )
    ref, path = arguments
    if ref.startswith("-") or path.startswith("-"):
        return VerificationResult(
            "unverified",
            "names read-only git plumbing but an argument is option-shaped, so "
            "it was not replayed",
        )
    if not _git_object_exists(repo_root, f"{ref}^{{commit}}"):
        if not _missing_ref_is_conclusive(repo_root, ref):
            return VerificationResult(
                "unverified",
                "cites a git ref this checkout cannot resolve and cannot rule "
                "out either, because its history is shallow",
            )
        return VerificationResult(
            "error",
            "cites a git ref that no longer exists in this repository",
        )
    if not _git_object_exists(repo_root, f"{ref}:{path}"):
        return VerificationResult(
            "error",
            "cites a path that does not exist at the cited ref",
        )
    return VerificationResult(
        "unverified",
        "source is reachable at the cited ref, but the asserted result is prose "
        "and was not compared",
    )


# Why each remaining tool family has no verifier. Every string here is a fixed
# constant: a detail is printed on a passing run, so it must never interpolate
# citation text, which is untrusted document prose and could carry anything.
# A test asserts no detail echoes its citation.
_UNSUPPORTED_TOOL_FAMILIES = (
    (
        ("shell", "run_command", "run_python_check"),
        "names an arbitrary shell command. Replaying it would execute text "
        "taken from a corpus document, so no verifier exists and none is "
        "planned -- cite the file or commit the command inspected instead",
    ),
    (
        ("webfetch", "curl_fetch", "http_get", "fetch"),
        "names a network fetch. Its result is remote content that changes "
        "independently of this repository, so a replay could not confirm the "
        "state cited -- cite the URL form instead, which --check-links checks",
    ),
    (
        ("github_api", "gh"),
        "names GitHub API state. Pull request and issue state is mutable and "
        "needs authentication, so a replay would report today's state rather "
        "than the state that was cited",
    ),
    (
        ("git_log", "git_log_oneline", "git_log_last_commit", "git_diff_name_only",
         "git_grep", "git_blame", "git_diff"),
        "names read-only git plumbing that has no verifier yet. Its asserted "
        "result is prose rather than a checkable verdict, so a replay would "
        "produce nothing to compare against",
    ),
)


def _unsupported_tool_detail(tool: str | None) -> str:
    """The blocking detail for a tool family no verifier covers.

    Matches on the family, never on the citation's arguments, so the returned
    string is always one of the constants above.
    """
    if tool is None:
        return UNVERIFIABLE_KIND_DETAIL
    for names, detail in _UNSUPPORTED_TOOL_FAMILIES:
        if tool in names or any(tool.startswith(f"{name}_") for name in names):
            return detail
    return UNVERIFIABLE_KIND_DETAIL


# Tool-result citations naming a grep. Also fail-only, and additionally
# restricted to citations that pin `ref=` to a full 40-hex SHA present locally
# -- 8 of the corpus's 78 grep citations today. The other 70 name a branch or
# no ref at all, and replaying those against a moving tree cannot distinguish a
# false citation from ordinary drift, so they are left blocking rather than
# judged on evidence that does not support a judgement.
_GREP_TOOL_NAMES = {
    "grep",
    "grep_repo",
    "grep_recursive",
    "grep_case_sensitive",
    "grep_case_insensitive",
    "grep_recursive_case_insensitive",
    "grep_extended_regex",
}
_CASE_INSENSITIVE_GREP_TOOLS = {
    "grep_case_insensitive",
    "grep_recursive_case_insensitive",
}

# Only the ref and the paths are guarded this way. The PATTERN is deliberately
# exempt: `|`, `(`, `$` and friends are ordinary regex there, it reaches git in
# an argument slot behind `-e`, and no shell ever sees it. Guarding it would
# silently stop checking the alternation patterns that make up most pinned
# citations -- a test pins that distinction.
_GREP_PATH_SHELL_METACHARACTERS = (";", "$(", "`", "|", "&", "\n", "\r", ">", "<")

_FULL_SHA_CITATION_RE = re.compile(r"^[0-9a-f]{40}$")
# The bracketed alternative must come first: `paths=['a', 'b']` contains commas
# INSIDE its value, and a plain `[^,]+` stops at the first one. That silently
# dropped every path after the first, which biases an absence claim toward
# looking true -- searching less than was cited is the one error this verifier
# must never make.
_GREP_KWARG_RE = re.compile(
    r"(?:^|,)\s*(?P<key>pattern|path|paths|ref|scope|glob)\s*=\s*"
    r"(?P<value>\[[^\]]*\]|[^,]+)"
)
# `scope=` and `glob=` name a pathspec pattern (`crates/**/*.rs`), not a path.
# They are recognised so the citation can be reported accurately, and
# deliberately NOT replayed: a glob cannot be resolved by the path-existence
# guard below, and letting one through would mean an absence claim could be
# "confirmed" by a pattern that matched no files at all.
_GREP_GLOB_SCOPE_KEYS = ("scope", "glob")
_ASSERTED_NO_MATCHES_RE = re.compile(r"^\s*(?:zero|no)\s+(?:matches|results|hits)\b", re.I)
_ASSERTED_SOME_MATCHES_RE = re.compile(r"^\s*(?P<count>\d+)\s+(?:matches|hits)\b", re.I)


def _parse_grep_citation(parsed: ParsedCitation) -> dict | None:
    """Reduce a grep citation to `{pattern, paths, ref}`, or `None`."""
    assert parsed.tool_args is not None
    text = parsed.tool_args.strip()
    if not text:
        return None
    keywords = {
        match.group("key"): _strip_argument_quotes(match.group("value"))
        for match in _GREP_KWARG_RE.finditer(text)
    }
    pattern = keywords.get("pattern")
    if pattern is None:
        leading = text.split(",", 1)[0]
        if "=" in leading:
            return None
        pattern = _strip_argument_quotes(leading)
    raw_paths = keywords.get("paths") or keywords.get("path") or ""
    # `paths='mobile/lib desktop/src'` packs several pathspecs into one value,
    # and `paths=['a', 'b']` occurs too. Both split on whitespace once the list
    # punctuation is stripped.
    separated = raw_paths.strip("[]")
    for punctuation in ("'", '"', ","):
        separated = separated.replace(punctuation, " ")
    paths = [_strip_argument_quotes(fragment) for fragment in separated.split()]
    if not pattern or not paths:
        return None
    return {"pattern": pattern, "paths": paths, "ref": keywords.get("ref", "")}


def _asserted_match_verdict(assertion: str) -> bool | None:
    """`True` if the citation asserts matches exist, `False` if it asserts none,
    `None` if it asserts something this verifier cannot check."""
    if _ASSERTED_NO_MATCHES_RE.match(assertion):
        return False
    some = _ASSERTED_SOME_MATCHES_RE.match(assertion)
    if some:
        return int(some.group("count")) > 0
    return None


def _verify_grep_tool(parsed: ParsedCitation, repo_root: Path) -> VerificationResult:
    assert parsed.tool_assertion is not None
    blocked = lambda detail: VerificationResult("unverified", detail)  # noqa: E731

    citation = _parse_grep_citation(parsed)
    if citation is None:
        if any(f"{key}=" in parsed.tool_args for key in _GREP_GLOB_SCOPE_KEYS):
            return blocked(
                "names a grep scoped by a glob rather than a path, which is not "
                "replayed because a glob matching no files is indistinguishable "
                "from a search that found nothing"
            )
        return blocked(
            "names a grep but its arguments could not be parsed into a pattern "
            "and a path, so it was not replayed"
        )
    if not _FULL_SHA_CITATION_RE.match(citation["ref"]):
        return blocked(
            "names a grep that is not pinned to a full commit SHA, so replaying "
            "it would search a different tree than the one cited"
        )
    asserted = _asserted_match_verdict(parsed.tool_assertion)
    if asserted is None:
        return blocked(
            "names a grep but its asserted result carries no checkable match "
            "verdict, so it was not replayed"
        )
    if any(
        token in value
        for value in [citation["ref"], *citation["paths"]]
        for token in _GREP_PATH_SHELL_METACHARACTERS
    ):
        return blocked(
            "names a grep but its ref or path contains a shell metacharacter, "
            "so it was not replayed"
        )
    if any(path.startswith("-") for path in citation["paths"]):
        return blocked(
            "names a grep but a path is option-shaped, so it was not replayed"
        )
    if not _git_object_exists(repo_root, f"{citation['ref']}^{{commit}}"):
        return blocked(
            "names a grep pinned to a commit that is not present in this "
            "repository, so it was not replayed"
        )
    # The vacuous-pass guard, and the reason this verifier is worth having at
    # all. `git grep` reports no matches for a path that does not exist, so
    # without this check every absence claim carrying a typo would look
    # confirmed by the very command that never searched anything.
    for path in citation["paths"]:
        if not _git_object_exists(repo_root, f"{citation['ref']}:{path}"):
            return blocked(
                "names a grep whose cited path does not exist at the pinned "
                "commit, so a no-match result would prove nothing"
            )

    command = ["git", "grep", "-q", "-E"]
    if parsed.tool in _CASE_INSENSITIVE_GREP_TOOLS:
        command.append("-i")
    # `-e` keeps a pattern that begins with `-` in the pattern slot instead of
    # being read as an option; `--` separates pathspecs from revisions.
    command += ["-e", citation["pattern"], citation["ref"], "--", *citation["paths"]]
    result = subprocess.run(
        command,
        cwd=repo_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode not in (0, 1):
        return blocked(
            "names a grep that could not be replayed at the pinned commit, so "
            "its asserted result was not checked"
        )
    found = result.returncode == 0
    if asserted and not found:
        return VerificationResult(
            "error",
            "asserts matches, but replaying it at the pinned commit finds none",
        )
    if not asserted and found:
        return VerificationResult(
            "error",
            "asserts no matches, but replaying it at the pinned commit finds matches",
        )
    return VerificationResult(
        "unverified",
        "replayed at the pinned commit and the match verdict agrees, but the "
        "claim it was cited to support was not compared",
    )


# GitHub repository URLs. `verb` decides whether the URL names a FILE (ADR-0003's
# subject) or some other repository view; `ref` is the branch, tag or commit it is
# pinned to. Both schemes are matched -- `http://` and `https://` -- so a mutable
# blob link cannot dodge the pin check by dropping the `s`. The trailing path is
# optional to MATCH (so a truncated `.../blob/main` still reaches the pin check)
# and required to PASS (a pinned link naming no file cites a repository, not "the
# cited file" ADR-0003 requires). Moved here from `validate.py` unchanged --
# see that module's git history for the review passes that shaped each rule.
_GITHUB_URL_RE = re.compile(
    r"^https?://github\.com/[^/\s]+/[^/\s]+/"
    r"(?P<verb>blob|raw|tree|blame|commits|edit)/(?P<ref>[^/\s]+)"
    r"(?:/(?P<path>\S*))?$"
)
_RAW_GITHUB_URL_RE = re.compile(
    r"^https?://raw\.githubusercontent\.com/[^/\s]+/[^/\s]+/(?P<ref>[^/\s]+)"
    r"(?:/(?P<path>\S*))?$"
)
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
# Only these two name a file's contents. `tree` is a directory listing and `blame`,
# `commits` and `edit` are views of a file rather than a citation of it.
_GITHUB_FILE_VERBS = {"blob", "raw"}

_URL_CHECK_TIMEOUT_SECONDS = 5
_URL_CHECK_USER_AGENT = "buzz-corpus-validator/1.0"


def _url_resolves(url: str) -> bool:
    """Return True only when an HTTP(S) citation resolves to content.

    The citation value is deliberately kept out of diagnostics: callers report the
    evidence entry and citation index instead, matching the rest of this module's
    no-leak output contract.
    """
    headers = {"User-Agent": _URL_CHECK_USER_AGENT}
    for method, extra_headers in (("HEAD", {}), ("GET", {"Range": "bytes=0-0"})):
        request = urllib.request.Request(
            url,
            headers={**headers, **extra_headers},
            method=method,
        )
        try:
            with urllib.request.urlopen(
                request, timeout=_URL_CHECK_TIMEOUT_SECONDS
            ) as response:
                return 200 <= response.status < 400
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in {405, 501}:
                continue
            return False
        except (OSError, TimeoutError, ValueError, http.client.HTTPException):
            return False
    return False


def _verify_url(url: str, *, check_links: bool) -> VerificationResult:
    """A URL citation must satisfy syntax rules, then resolve in link-check mode.

    Repository file links still have the strongest structural requirement: full
    commit SHA, file-content verb, and a non-empty path. Other HTTP(S) URLs have
    no commit pin, but they are not unverifiable by nature; check_links can at
    least establish that the referenced source exists at validation time.
    """
    target = _parse_url_target(url)
    match = _GITHUB_URL_RE.match(target) or _RAW_GITHUB_URL_RE.match(target)
    if match:
        if not _FULL_SHA_RE.match(match.group("ref")):
            return VerificationResult(
                "error",
                "is a repository link pinned to a mutable ref rather than a "
                "full commit SHA (ADR-0003)",
            )
        verb = match.groupdict().get("verb") or "raw"
        if verb not in _GITHUB_FILE_VERBS:
            return VerificationResult(
                "error",
                f"is a repository '{verb}' view rather than a link to the cited "
                "file itself (ADR-0003)",
            )
        if not match.groupdict().get("path"):
            return VerificationResult(
                "error", "is pinned but names no file within the repository"
            )
    if not check_links:
        return VerificationResult(
            "unverified", "requires --check-links to verify reachable content"
        )
    if not _url_resolves(target):
        return VerificationResult("error", "does not resolve to reachable content")
    return VerificationResult("ok")


def verify_citation(
    parsed: ParsedCitation, repo_root: Path, *, check_links: bool = False
) -> VerificationResult:
    """Verify locally provable citation kinds without executing citation prose.

    `check_links` gates the one kind that reaches the network: URL citations pass
    their syntax rules unconditionally, then are only fetched when the caller
    opts in. Graph edges, tool results, and unknown forms have no replay
    implementation here and remain blocking `unverified` results.
    """
    if parsed.kind in {
        EvidenceKind.LOCAL_FILE,
        EvidenceKind.LOCAL_FILE_LINE,
        EvidenceKind.LOCAL_FILE_RANGE,
    }:
        return _verify_local(parsed, repo_root)
    if parsed.kind is EvidenceKind.COMMIT:
        return _verify_commit(parsed, repo_root)
    if parsed.kind in {EvidenceKind.EXTERNAL_URL, EvidenceKind.GITHUB_URL}:
        assert parsed.url is not None
        return _verify_url(parsed.url, check_links=check_links)
    if parsed.kind is EvidenceKind.TOOL_RESULT and parsed.tool in _GIT_TOOL_NAMES:
        return _verify_git_tool(parsed, repo_root)
    if parsed.kind is EvidenceKind.TOOL_RESULT and parsed.tool in _GREP_TOOL_NAMES:
        return _verify_grep_tool(parsed, repo_root)
    if parsed.kind is EvidenceKind.TOOL_RESULT:
        return VerificationResult("unverified", _unsupported_tool_detail(parsed.tool))
    if parsed.kind is EvidenceKind.GRAPH_EDGE:
        return VerificationResult("unverified", UNVERIFIABLE_KIND_DETAIL)
    return VerificationResult("error", "no verifier exists for this evidence kind")

class ProhibitedPathError(Exception):
    """A caller tried to bundle a credential-shaped path as evidence."""


def _is_credential_like_path(path: str) -> bool:
    name = PurePosixPath(path).name
    if name == ".env":
        return True
    if name.startswith(".env.") and not name.endswith(_ENV_SAFE_SUFFIXES):
        return True
    if any(name.startswith(prefix) for prefix in _CREDENTIAL_LIKE_BASENAME_PREFIXES):
        return True
    return PurePosixPath(name).suffix in _CREDENTIAL_LIKE_EXTENSIONS


@dataclass(frozen=True)
class EvidenceEntry:
    evidence_class: str
    claim_key: str
    value: str
    source_id: str
    url: str | None
    fact_eligible: bool

    def __post_init__(self) -> None:
        if self.evidence_class not in _VALID_CLASSES:
            raise ValueError(f"unknown evidence_class: {self.evidence_class!r}")
        expected_fact_eligible = self.evidence_class not in _TEAM_KNOWLEDGE_ONLY_CLASSES
        if self.fact_eligible != expected_fact_eligible:
            raise ValueError(
                f"fact_eligible={self.fact_eligible!r} is inconsistent with "
                f"evidence_class={self.evidence_class!r}; construct entries "
                "through the collect_* helpers, which set this correctly"
            )


@dataclass
class EvidenceBundle:
    entries: list[EvidenceEntry] = field(default_factory=list)
    conflicts: list[dict] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "entries": [
                {
                    "evidence_class": e.evidence_class,
                    "claim_key": e.claim_key,
                    "value": e.value,
                    "source_id": e.source_id,
                    "url": e.url,
                    "fact_eligible": e.fact_eligible,
                }
                for e in sorted(self.entries, key=lambda e: (e.claim_key, e.evidence_class, e.source_id))
            ],
            "conflicts": sorted(self.conflicts, key=lambda c: c["claim_key"]),
        }
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"


class GitHubClient:
    """Thin wrapper over `gh api`, read-only. Override for tests -- see FakeGitHubClient."""

    def _get(self, path: str) -> dict:
        out = subprocess.run(
            ["gh", "api", path],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(out.stdout)

    def get_commit(self, repo: str, sha: str) -> dict:
        return self._get(f"repos/{repo}/commits/{sha}")

    def get_pull_request(self, repo: str, number: int) -> dict:
        return self._get(f"repos/{repo}/pulls/{number}")

    def get_pull_request_reviews(self, repo: str, number: int) -> list[dict]:
        return self._get(f"repos/{repo}/pulls/{number}/reviews")

    def get_issue(self, repo: str, number: int) -> dict:
        return self._get(f"repos/{repo}/issues/{number}")

    def get_issue_comments(self, repo: str, number: int) -> list[dict]:
        return self._get(f"repos/{repo}/issues/{number}/comments")


def _resolve_contained_path(root: Path, path: str) -> Path:
    """Resolve a repository-relative citation path, enforcing containment.

    Mirrors `validate.py`'s `_classify_repo_path`. An earlier revision here
    checked only `(root / path).exists()`, so `../../../../etc/passwd`
    escaped the repository entirely and a bare directory name like
    `launchpad` passed as though it were a file -- pathlib's `/` operator
    also silently discards the left operand when the right is absolute, so
    an absolute path must be rejected explicitly rather than existence
    checked. Containment is enforced on the RESOLVED path, not the literal
    one, so a symlink pointing out of the tree is caught rather than
    followed.
    """
    if PurePosixPath(path).is_absolute():
        raise FileNotFoundError(f"no such file under repo root: {path}")
    resolved_root = root.resolve()
    try:
        candidate = (resolved_root / path).resolve()
    except (OSError, RuntimeError) as exc:
        raise FileNotFoundError(f"no such file under repo root: {path}") from exc
    if not candidate.is_relative_to(resolved_root):
        raise FileNotFoundError(f"no such file under repo root: {path}")
    if not candidate.is_file():
        raise FileNotFoundError(f"no such file under repo root: {path}")
    return candidate


def collect_code_evidence(
    root: Path,
    path: str,
    claim_key: str,
    value: str,
    *,
    evidence_class: str = "code",
    line: int | None = None,
) -> EvidenceEntry:
    """Bundle one repository-relative path (or `path:line`) as code/test/spec evidence."""
    if evidence_class not in {"code", "test", "spec"}:
        raise ValueError(f"collect_code_evidence only accepts code/test/spec, got {evidence_class!r}")
    if _is_credential_like_path(path):
        raise ProhibitedPathError(f"refusing to bundle credential-shaped path: {path}")
    _resolve_contained_path(root, path)
    source_id = f"{path}:{line}" if line is not None else path
    return EvidenceEntry(
        evidence_class=evidence_class,
        claim_key=claim_key,
        value=value,
        source_id=source_id,
        url=None,
        fact_eligible=True,
    )


def collect_adr_evidence(root: Path, adr_path: str, claim_key: str, value: str) -> EvidenceEntry:
    if _is_credential_like_path(adr_path):
        raise ProhibitedPathError(f"refusing to bundle credential-shaped path: {adr_path}")
    _resolve_contained_path(root, adr_path)
    return EvidenceEntry(
        evidence_class="adr",
        claim_key=claim_key,
        value=value,
        source_id=adr_path,
        url=None,
        fact_eligible=True,
    )


def collect_commit_evidence(
    repo: str, sha: str, claim_key: str, value: str, client: GitHubClient
) -> EvidenceEntry:
    commit = client.get_commit(repo, sha)
    resolved_sha = commit.get("sha", sha)
    return EvidenceEntry(
        evidence_class="commit",
        claim_key=claim_key,
        value=value,
        source_id=f"sha:{resolved_sha}",
        url=commit.get("html_url"),
        fact_eligible=True,
    )


def collect_pr_review_evidence(
    repo: str, pr_number: int, claim_key: str, value: str, client: GitHubClient
) -> list[EvidenceEntry]:
    """One entry per review left on the PR -- reviews are the class DoD names, not general PR comments."""
    reviews = client.get_pull_request_reviews(repo, pr_number)
    entries = []
    for review in reviews:
        review_id = review.get("id")
        entries.append(
            EvidenceEntry(
                evidence_class="pr_review",
                claim_key=claim_key,
                value=value,
                source_id=f"pr:{pr_number}#review:{review_id}",
                url=review.get("html_url"),
                fact_eligible=False,
            )
        )
    return entries


def collect_pr_comment_evidence(
    repo: str, pr_number: int, comment: dict, claim_key: str, value: str
) -> EvidenceEntry:
    """One entry for one already-fetched PR (issue-style) comment dict."""
    comment_id = comment.get("id")
    return EvidenceEntry(
        evidence_class="pr_comment",
        claim_key=claim_key,
        value=value,
        source_id=f"pr:{pr_number}#comment:{comment_id}",
        url=comment.get("html_url"),
        fact_eligible=False,
    )


def collect_issue_discussion_evidence(
    repo: str, issue_number: int, claim_key: str, value: str, client: GitHubClient
) -> list[EvidenceEntry]:
    """The issue body plus every comment, each its own entry -- never merged into one blob."""
    issue = client.get_issue(repo, issue_number)
    entries = [
        EvidenceEntry(
            evidence_class="issue_discussion",
            claim_key=claim_key,
            value=value,
            source_id=f"issue:{issue_number}",
            url=issue.get("html_url"),
            fact_eligible=False,
        )
    ]
    for comment in client.get_issue_comments(repo, issue_number):
        comment_id = comment.get("id")
        entries.append(
            EvidenceEntry(
                evidence_class="issue_discussion",
                claim_key=claim_key,
                value=value,
                source_id=f"issue:{issue_number}#comment:{comment_id}",
                url=comment.get("html_url"),
                fact_eligible=False,
            )
        )
    return entries


def find_conflicts(entries: list[EvidenceEntry]) -> list[dict]:
    """Any two entries sharing a claim_key with a different value -- always reported, never resolved.

    Per ADR-0029 as AGENTS.md cites it: "When two sources of the same claim
    type conflict, stop: record the conflict... rather than resolving it
    yourself." This function is the "record", not a resolver -- it ranks
    nothing and picks no winner, regardless of evidence_class.
    """
    by_key: dict[str, list[EvidenceEntry]] = {}
    for entry in entries:
        by_key.setdefault(entry.claim_key, []).append(entry)

    conflicts = []
    for claim_key, group in by_key.items():
        distinct_values = sorted({e.value for e in group})
        if len(distinct_values) > 1:
            conflicts.append(
                {
                    "claim_key": claim_key,
                    "values": distinct_values,
                    "source_ids": sorted(e.source_id for e in group),
                }
            )
    return conflicts


def build_bundle(entries: list[EvidenceEntry]) -> EvidenceBundle:
    return EvidenceBundle(entries=list(entries), conflicts=find_conflicts(entries))

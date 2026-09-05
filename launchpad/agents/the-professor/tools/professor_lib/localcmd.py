"""`check-page` / `screen-content` -- the local-only half of professor.py's tool
layer (redesign doc §4's `localcmd` subgraph: "no network, runs on every write").

`check-page` implements `tools/contract/page-contract.md`'s full rule list against
this build's own inline claim-tagging convention (documented on `_TAG_RE` below,
since neither the design doc nor page-contract.md specifies how an individual
sentence's claim type is distinguished mechanically -- flagged for reviewer
attention, not silently invented scope: a mechanical check for "a behaviour claim
with no citation" needs *some* explicit signal in the source text, since prose
alone cannot carry that distinction deterministically).

Citation existence (rule 1) is NOT a single reused code path, per this plan's
step 4: a citation to `--target`'s own repo is checked with a plain local
`git cat-file` call -- no network, ever, for that case. Only a citation naming a
genuinely different, external repo reuses `netcmd.path_exists_at_bool` in-process.
"""

import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_FIELDS = ["title", "category", "author", "generated_by", "generated_at"]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

SECTION_MARKER_RE = re.compile(
    r'^<!--\s*professor:section\s+sources="([^"]*)"\s+updated_by=\S+\s+updated_at=\S+\s*-->\s*$'
)
HEADING_RE = re.compile(r"^#+\s+.*$")

# CommonMark recognizes both ``` and ~~~ as fence markers (step 6 of the
# 2026-09-05 fix round -- the original FENCE_RE only matched backticks).
# Matches a candidate fence marker line: leading whitespace, then a run of
# 3+ backticks or 3+ tildes, then whatever follows (an info string for an
# opener, or -- for a valid closer -- nothing but trailing whitespace,
# checked by the caller via CommonMark's own closing-fence rule).
FENCE_MARKER_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")

SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")

# This build's own inline claim-tagging convention (see module docstring).
# A behaviour claim: `(behaviour: <citation>)` where <citation> is one of
#   <path>@<40-hex-sha>                       -- self (--target's own tree)
#   <path>@<40-hex-sha>#L<n>[-L<m>]            -- self, line-specific
#   <repo>:<path>@<40-hex-sha>[#L<n>[-L<m>]]   -- external
#   none                                       -- explicitly no citation (rule 2)
# An opinion claim: `(opinion)`, no citation.
BEHAVIOUR_TAG_RE = re.compile(r"\(behaviour:\s*([^)]*)\)")
OPINION_TAG_RE = re.compile(r"\(opinion\)")

CITATION_RE = re.compile(
    r"^(?:(?P<repo>[^:@#]+):)?(?P<path>[^@#]+)@(?P<sha>[0-9a-f]{40})"
    r"(?:#L(?P<start>\d+)(?:-L(?P<end>\d+))?)?$"
)

# Marker `sources="..."` entries: `[repo:]path@shortsha[#Lx[-Ly]]`, semicolon-separated.
MARKER_SOURCE_RE = re.compile(
    r"^(?:(?P<repo>[^:@#]+):)?(?P<path>[^@#]+)@(?P<shortsha>[0-9a-f]+)"
    r"(?:#L(?P<start>\d+)(?:-L(?P<end>\d+))?)?$"
)


def _finding(rule: str, message: str) -> dict:
    return {"rule": rule, "message": message}


def _parse_frontmatter(content: str):
    """Returns (frontmatter_dict, body, findings). frontmatter_dict is None if
    missing/unparseable/missing a required field -- caller must short-circuit.
    """
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None, content, [
            _finding("frontmatter", "no frontmatter block found at the start of the file")
        ]

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, content[match.end():], [
            _finding("frontmatter", f"frontmatter block is not valid YAML: {exc}")
        ]

    if not isinstance(parsed, dict):
        return None, content[match.end():], [
            _finding("frontmatter", "frontmatter block did not parse to a mapping")
        ]

    missing = [f for f in REQUIRED_FRONTMATTER_FIELDS if f not in parsed or parsed[f] in (None, "")]
    if missing:
        return None, content[match.end():], [
            _finding("frontmatter", f"frontmatter is missing required field(s): {', '.join(missing)}")
        ]

    return parsed, content[match.end():], []


def _local_citation_exists(target: str, commit: str, path: str) -> tuple[bool | None, str | None]:
    """Plain local git check -- no network, ever, for a citation to --target's
    own tree. This is the whole point of step 4's local/external split.

    Returns `(True, None)` if `path` exists at `commit`, `(False, None)` if
    `commit` is confirmed to exist locally but `path` genuinely does not (a
    real citation defect), or `(None, message)` if the check itself could
    not be completed -- a missing or non-git `--target` directory, or
    `commit` simply absent from this local clone's own history. That last
    case is deliberately NOT the same outcome as a confirmed-absent path: a
    shallow clone (this checkout's own repo is one -- see CLAUDE.md) can be
    missing a commit that is entirely real upstream, so "can't find this
    commit locally" must never be reported as "this citation is wrong".
    `path_exists_at_bool` (netcmd.py) already makes this same True/False/None
    distinction on the network side (prior fix round's step 1); this was the
    matching, until-now-uncorrected gap on the local side (step 4 of the
    2026-09-05 round).

    Checked in two stages so the two failure modes can't be confused with
    each other: first whether `commit` itself resolves at all
    (`git cat-file -e <commit>^{commit}`, which fails distinctly for "no
    such directory", "not a git repo", and "no such commit in this repo's
    history"), and only once that succeeds, whether `path` exists within it.
    """
    commit_check = subprocess.run(
        ["git", "-C", target, "cat-file", "-e", f"{commit}^{{commit}}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if commit_check.returncode != 0:
        stderr = commit_check.stderr.strip()
        if "cannot change to" in stderr:
            return None, (
                f"_local_citation_exists({target!r}, {commit!r}, {path!r}): "
                f"--target does not exist as a directory: {stderr}"
            )
        if "not a git repository" in stderr:
            return None, (
                f"_local_citation_exists({target!r}, {commit!r}, {path!r}): "
                f"--target is not a git repository: {stderr}"
            )
        return None, (
            f"_local_citation_exists({target!r}, {commit!r}, {path!r}): commit "
            "could not be confirmed present in --target's local history "
            "(a shallow clone can be missing a commit that is real "
            f"upstream): {stderr}"
        )

    result = subprocess.run(
        ["git", "-C", target, "cat-file", "-e", f"{commit}:{path}"],
        capture_output=True,
        timeout=15,
    )
    return result.returncode == 0, None


def _local_file_line_count(target: str, commit: str, path: str) -> int | None:
    result = subprocess.run(
        ["git", "-C", target, "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    if result.returncode != 0:
        return None
    # A trailing newline means the last line still counts; splitlines() handles
    # both a trailing-newline file and one without correctly.
    return len(result.stdout.splitlines())


def _fence_marker(line: str):
    """Returns `(char, length, trailing)` if `line` looks like a fence marker
    line, else `None`. `char` is `` ` `` or `~`, `length` is how many of that
    character opened it, `trailing` is whatever follows the run (an info
    string for an opener; must be blank for a valid closer).
    """
    match = FENCE_MARKER_RE.match(line)
    if not match:
        return None
    run = match.group(1)
    return run[0], len(run), match.group(2)


def _strip_fenced_lines(text: str) -> str:
    """Returns `text` with every line inside a fenced (``` or ~~~) code
    block removed, including the fence marker lines themselves -- so claim
    scanning never sees fenced example content at all: neither checked for
    a missing citation, nor contributing an example citation to the
    section's marker-matching set (step 7 of the 2026-09-05 fix round).

    Recomputes fence state from scratch over `text` (a single section's own
    body), using the same fence-matching rule `_split_sections` uses (step
    6): a closing fence must use the same character and be at least as long
    as the opener. A section's text runs strictly between two headings, and
    heading detection is itself fence-aware, so a real fence can never
    straddle a section boundary -- recomputing per section is equivalent to,
    and simpler than, carrying state over from the splitter.
    """
    lines = text.splitlines()
    kept = []
    in_fence = False
    fence_char = None
    fence_len = 0
    for line in lines:
        marker = _fence_marker(line)
        if in_fence:
            if marker is not None:
                char, length, trailing = marker
                if char == fence_char and length >= fence_len and trailing.strip() == "":
                    in_fence = False
                    fence_char = None
                    fence_len = 0
            continue
        if marker is not None:
            fence_char, fence_len, _ = marker
            in_fence = True
            continue
        kept.append(line)
    return "\n".join(kept)


def _split_sections(body: str):
    """Yield (marker_line_or_None, heading_line_or_None, section_text) for
    each heading in `body`, in order, plus one leading entry for any text
    that precedes the first heading. `section_text` runs from just after the
    heading to just before the next heading (or end of body).

    Fence-aware: a `#`-prefixed comment line inside a fenced (``` or ~~~)
    code block is not a markdown heading, and must not be treated as one --
    otherwise a Python/shell/etc. example containing a `#` comment mis-splits
    the real section around it, orphaning its citations. Tracks the actual
    marker character and length opened, per CommonMark's own closing-fence
    rule (same character, length >= the opener's), so a shorter or
    different-character marker nested inside an outer fence (e.g. a 4-
    backtick block containing a 3-backtick example) doesn't prematurely
    close it (step 6 of the 2026-09-05 fix round).

    Any tagged claim text before the document's first heading used to fall
    into no section at all and was never checked (step 3 of the 2026-09-05
    fix round). The span before the first heading is yielded here as an
    implicit preamble unit -- `heading_line=None` signals it to
    `_check_section` below, which still scans it for claims/citations like
    any section's body, but never requires a provenance marker for it: the
    contract's marker rule is specifically "directly above its heading", and
    a preamble structurally has none. Extending the marker model to a
    heading-less span would be the larger change; treating the preamble as
    an implicit unit that only the claim rule applies to is the smaller one.
    """
    lines = body.splitlines()
    heading_indices = []
    in_fence = False
    fence_char = None
    fence_len = 0
    for i, line in enumerate(lines):
        marker = _fence_marker(line)
        if in_fence:
            if marker is not None:
                char, length, trailing = marker
                if char == fence_char and length >= fence_len and trailing.strip() == "":
                    in_fence = False
                    fence_char = None
                    fence_len = 0
            continue
        if marker is not None:
            fence_char, fence_len, _ = marker
            in_fence = True
            continue
        if HEADING_RE.match(line):
            heading_indices.append(i)

    if heading_indices and heading_indices[0] > 0:
        preamble_text = "\n".join(lines[: heading_indices[0]])
        if preamble_text.strip():
            yield None, None, preamble_text

    for pos, idx in enumerate(heading_indices):
        heading_line = lines[idx]
        marker_line = None
        if idx > 0 and SECTION_MARKER_RE.match(lines[idx - 1].strip()):
            marker_line = lines[idx - 1].strip()

        end = heading_indices[pos + 1] if pos + 1 < len(heading_indices) else len(lines)
        section_text = "\n".join(lines[idx + 1 : end])
        yield marker_line, heading_line, section_text


def _parse_citation_string(raw: str):
    match = CITATION_RE.match(raw.strip())
    if not match:
        return None
    return {
        "repo": match.group("repo"),
        "path": match.group("path"),
        "sha": match.group("sha"),
        "start": int(match.group("start")) if match.group("start") else None,
        "end": int(match.group("end")) if match.group("end") else None,
    }


def _citation_key(citation: dict) -> tuple:
    """Normalized key for comparing a body citation against a marker source
    entry: (repo, path, full-40-char-sha, span-string-or-None).

    The SHA is kept at its full length here, not truncated to a fixed 7
    characters -- a marker may legitimately use an 8+ character abbreviation
    of the same commit, and truncating both to a hardcoded length would make
    an equivalent abbreviation compare unequal. See `_keys_match` below, which
    does the actual length-tolerant comparison at match time instead.
    """
    span = None
    if citation["start"] is not None:
        span = f"L{citation['start']}" if citation["end"] is None else f"L{citation['start']}-L{citation['end']}"
    return (citation["repo"], citation["path"], citation["sha"], span)


def _keys_match(expected_keys: set, actual_keys: set) -> bool:
    """Length-tolerant comparison between a marker's parsed source keys
    (possibly-abbreviated SHAs, any length >= 1 hex char) and a section's
    actual citation keys (always a full 40-char SHA). Two SHA abbreviations
    of the same commit can legitimately differ in length (a marker using an
    8-character shortsha vs. another using 7), so equality is judged by
    truncating both sides to the shorter of the two lengths for each
    candidate pair, not by requiring identical-length strings. Every expected
    key must match exactly one actual key and vice versa (a true bijection),
    same strength as the plain `==` this replaces.
    """
    if len(expected_keys) != len(actual_keys):
        return False
    remaining_actual = set(actual_keys)
    for repo, path, sha, span in expected_keys:
        match = None
        for candidate in remaining_actual:
            c_repo, c_path, c_sha, c_span = candidate
            if repo != c_repo or path != c_path or span != c_span:
                continue
            shared_len = min(len(sha), len(c_sha))
            if sha[:shared_len] == c_sha[:shared_len]:
                match = candidate
                break
        if match is None:
            return False
        remaining_actual.discard(match)
    return True


def _parse_marker_sources(sources_attr: str) -> tuple[set, list]:
    """Returns `(keys, malformed_entries)`. A `sources` entry that fails to
    match `MARKER_SOURCE_RE` is a real parse failure, not an absent one --
    it must never be silently discarded as if it were an empty-but-valid
    entry, which previously left `keys` looking "empty and therefore
    matching" even when the marker's actual text was garbage (step 8 of the
    2026-09-05 fix round). `malformed_entries` carries each such raw entry so
    the caller can flag it distinctly, rather than mistaking "nothing left
    to compare" for "correctly compared and found equal".
    """
    keys = set()
    malformed_entries = []
    for entry in sources_attr.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        match = MARKER_SOURCE_RE.match(entry)
        if not match:
            malformed_entries.append(entry)
            continue
        span = None
        if match.group("start"):
            span = (
                f"L{match.group('start')}"
                if not match.group("end")
                else f"L{match.group('start')}-L{match.group('end')}"
            )
        keys.add((match.group("repo"), match.group("path"), match.group("shortsha"), span))
    return keys, malformed_entries


def _check_section(marker_line, heading_line, section_text, target: str) -> list:
    findings = []

    if heading_line is None:
        # The implicit preamble unit (step 3): no heading exists for a
        # marker to sit "directly above", so the marker requirement simply
        # doesn't apply here -- only the claim rule below does.
        heading_name = "(preamble, before first heading)"
        marker_sources_attr = None
    else:
        heading_name = heading_line.strip()
        if marker_line is None:
            findings.append(
                _finding(
                    "missing-provenance-marker",
                    f"section {heading_name!r} has no provenance marker directly above its heading",
                )
            )
            marker_sources_attr = None
        else:
            marker_match = SECTION_MARKER_RE.match(marker_line)
            marker_sources_attr = marker_match.group(1)

    body_citation_keys = set()

    for sentence in SENTENCE_SPLIT_RE.split(_strip_fenced_lines(section_text)):
        behaviour_matches = list(BEHAVIOUR_TAG_RE.finditer(sentence))
        opinion_matches = list(OPINION_TAG_RE.finditer(sentence))

        if behaviour_matches and opinion_matches:
            findings.append(
                _finding(
                    "mixed-claim",
                    f"section {heading_name!r} has a sentence reading as both a "
                    f"behaviour claim and an opinion claim: {sentence.strip()!r}",
                )
            )
            # Deliberately does NOT `continue` here: the sentence's citation is
            # still a real citation the section's provenance marker accounts
            # for, and skipping it would make an unrelated rule (mismatched
            # marker) fire alongside mixed-claim -- "no fixture trips more
            # than the rule it targets" (step 4's own done-when). The
            # citation is still registered/verified below like any other.

        if not behaviour_matches:
            continue

        for behaviour_match in behaviour_matches:
            raw = behaviour_match.group(1).strip()
            if raw == "none" or raw == "":
                findings.append(
                    _finding(
                        "missing-citation",
                        f"section {heading_name!r} has a behaviour claim with no "
                        f"citation at all: {sentence.strip()!r}",
                    )
                )
                continue

            citation = _parse_citation_string(raw)
            if citation is None:
                findings.append(
                    _finding(
                        "missing-citation",
                        f"section {heading_name!r} has an unparseable citation: {raw!r}",
                    )
                )
                continue

            body_citation_keys.add(_citation_key(citation))

            if citation["repo"] is None:
                exists, error_message = _local_citation_exists(
                    target, citation["sha"], citation["path"]
                )
            else:
                from professor_lib.netcmd import path_exists_at_bool

                exists, error_message = path_exists_at_bool(
                    citation["repo"], citation["sha"], citation["path"]
                )

            if exists is None:
                # A rate-limited/auth-failed/otherwise-erroring API response is
                # NOT the same outcome as a confirmed 404 -- collapsing them
                # would silently misreport a transient API failure as a real
                # documentation defect. Surface it as its own outcome instead.
                findings.append(
                    _finding(
                        "citation-check-error",
                        f"section {heading_name!r} cites {raw!r}: could not be "
                        f"verified -- {error_message}",
                    )
                )
                continue

            if not exists:
                findings.append(
                    _finding(
                        "citation-not-found",
                        f"section {heading_name!r} cites {raw!r}, which does not "
                        "exist at that commit",
                    )
                )
                continue

            if citation["start"] is not None and citation["repo"] is None:
                total_lines = _local_file_line_count(target, citation["sha"], citation["path"])
                end = citation["end"] or citation["start"]
                if total_lines is None or citation["start"] < 1 or end > total_lines or end < citation["start"]:
                    findings.append(
                        _finding(
                            "out-of-bounds-range",
                            f"section {heading_name!r} cites {raw!r}, a line range "
                            f"out of bounds for a file of {total_lines} lines",
                        )
                    )

    if marker_line is not None:
        expected_keys, malformed_entries = _parse_marker_sources(marker_sources_attr)
        actual_keys = body_citation_keys
        if malformed_entries:
            # A sources entry that failed to parse is a real parse failure,
            # never an absent-but-valid one -- flagging it distinctly means
            # it can never be silently absorbed into "matches, because
            # there's nothing left to compare" (step 8 of the 2026-09-05 fix
            # round). Reported instead of, not alongside, the bijection
            # check below: with part of the marker unparseable, that
            # comparison can't be meaningfully run at all.
            findings.append(
                _finding(
                    "malformed-provenance-marker",
                    f"section {heading_name!r}'s provenance marker has unparseable "
                    f"sources entr{'y' if len(malformed_entries) == 1 else 'ies'}: "
                    f"{malformed_entries!r}",
                )
            )
        elif not _keys_match(expected_keys, actual_keys):
            findings.append(
                _finding(
                    "mismatched-provenance-marker",
                    f"section {heading_name!r}'s provenance marker sources "
                    f"{expected_keys!r} don't match its actual citations {actual_keys!r}",
                )
            )

    return findings


def check_page(file_path: str, target: str, pack_root: str) -> int:
    path = Path(file_path)
    if not path.is_file():
        print(f"check-page: no such file: {file_path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8")
    _, body, frontmatter_findings = _parse_frontmatter(content)

    if frontmatter_findings:
        print(json.dumps({"findings": frontmatter_findings, "skipped": True}, indent=2))
        return 0

    findings = []
    for marker_line, heading_line, section_text in _split_sections(body):
        findings.extend(_check_section(marker_line, heading_line, section_text, target))

    print(json.dumps({"findings": findings, "skipped": False}, indent=2))
    return 0


API_KEY_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9]{10,}\b"),
    re.compile(r"\bAKIA[A-Z0-9]{8,}\b"),
    re.compile(r"\bghp_[A-Za-z0-9]{10,}\b"),
    re.compile(r"\bxox[bp]-[A-Za-z0-9-]{6,}\b"),
]

PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----")

CONNECTION_STRING_RE = re.compile(r"://[^\s:@/]+:[^\s@/]+@[^\s/]+")
PASSWORD_LITERAL_RE = re.compile(r"\b(?:password|passwd|pwd)\s*[:=]\s*\S+", re.IGNORECASE)

WEBHOOK_URL_RE = re.compile(
    r"https?://[^\s]*(?:hook|webhook)[^\s]*/[A-Za-z0-9_/-]{10,}", re.IGNORECASE
)

# sensitive-patterns.md's actual spec for this category is "a URL whose query
# string or path segment is itself an auth token" -- the "hook"/"webhook"
# substring check above is not that; it just happens to catch the common
# case where a webhook domain also carries one. This regex finds any URL,
# independent of what its domain contains, so its query string and path can
# be inspected for an embedded high-entropy value (step 2 of the 2026-09-05
# fix round). Excludes backtick and other Markdown delimiter characters so a
# URL wrapped in `...` doesn't swallow the closing backtick into the match.
URL_RE = re.compile(r"https?://[A-Za-z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+", re.IGNORECASE)

# A query-string param named token/key/secret/auth (case-insensitive) --
# reuses the same high-entropy-adjacent-to-keyword idea as step 1's
# HIGH_ENTROPY_KEYWORD_RE, but scoped to a URL's own `name=value` shape
# rather than freeform prose, since a query param's name IS the adjacency
# signal here (no separate window search needed).
URL_AUTH_QUERY_PARAM_RE = re.compile(r"[?&](?:token|key|secret|auth)=([^&\s]+)", re.IGNORECASE)

# sensitive-patterns.md's "[pattern] API keys / access tokens" category has a
# second clause beyond the fixed-prefix table above: "a high-entropy opaque
# string adjacent to words like key/token/secret" (2026-09-05 fix round, step
# 1). The keyword must appear as its own word -- \b-bounded on both sides --
# never merely as a substring inside the candidate token itself, or an
# ordinary identifier like API_KEY or access_token would false-positive on
# its own name every time (no separator between the keyword and the rest of
# the identifier means no real word boundary there).
HIGH_ENTROPY_KEYWORD_RE = re.compile(r"\b(?:key|token|secret|password)\b", re.IGNORECASE)

# A candidate opaque string: 20+ run of letters/digits/underscore/hyphen.
# Real secrets in the wild (API tokens, generated passwords) are usually
# 20+ characters; shorter runs are too easily an ordinary word or
# identifier fragment for entropy alone to distinguish reliably.
OPAQUE_STRING_RE = re.compile(r"\b[A-Za-z0-9_\-]{20,}\b")

# Threshold picked from this pack's own fixture corpus, not an arbitrary
# round number: hex commit SHAs (real "opaque-looking" strings already in
# the fixtures) measure ~3.6-3.7 bits/char, ordinary identifiers/prose words
# measure ~3.0-3.4, and a genuinely random 32-character alphanumeric secret
# (this step's own reproduction fixture) measures ~5.0. 4.0 sits comfortably
# above every non-secret string already in this corpus and comfortably below
# a real random token, leaving margin on both sides rather than sitting on
# either boundary.
HIGH_ENTROPY_THRESHOLD = 4.0

# "same line, or within a small token window" (step 1's own done-when
# wording) -- 40 characters comfortably spans a short assignment like
# `token = <value>` or `API_KEY: <value>` without reaching into an unrelated
# neighboring sentence.
HIGH_ENTROPY_WINDOW_CHARS = 40

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

INTERNAL_HOST_RE = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|[\w-]+\.internal)\b"
)

PHYSICAL_ADDRESS_RE = re.compile(
    r"\b\d{1,6}\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?\s+"
    r"(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr)\b"
)

# [dispatch] category (sensitive-patterns.md): recognizing "used as
# access-control data" is a semantic judgment this pattern match cannot make --
# this only detects the *structural* shape (an access-control-sounding phrase
# near a list of Title-Case name-like tokens), then reports it as
# "not_evaluated" rather than a pass or a verdict. The real judgment needs
# $PROFESSOR_VERIFIER_CMD dispatch, built in Phase 1b (a separate, not-yet-filed
# Feature per this plan's LEFT OUT) -- explicitly out of scope here.
ROSTER_CONTEXT_RE = re.compile(
    r"\b(?:allowlist|roster|restricted to|access list|hardcoded reviewer list)\b",
    re.IGNORECASE,
)
NAME_LIST_RE = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")

# The two patterns above must co-occur within a localized window (roughly a
# sentence) to count as a real roster-in-context match -- matching them
# file-wide means any page with an unrelated Title-Case phrase anywhere and
# an unrelated roster-context phrase anywhere else spuriously triggers this
# category. 120 characters comfortably spans a single sentence's own
# roster-phrase-to-name-list gap without spanning separate sentences/sections.
ROSTER_NAME_WINDOW_CHARS = 120

MARKER_COMMENT_RE = re.compile(r"<!--\s*professor:section.*?-->", re.DOTALL)

# sensitive-patterns.md's email carve-out is narrower than "the whole
# frontmatter block" -- it's specifically "a citation's `author` frontmatter
# field, or inside a `professor:section` provenance comment" (step 5 of the
# 2026-09-05 fix round). Matches the `author:` line's value only, within the
# already-captured frontmatter body text.
AUTHOR_FIELD_RE = re.compile(r"^author:[ \t]*(.*)$", re.MULTILINE)


def _spans_within_window(span_a: tuple, span_b: tuple, window: int) -> bool:
    """True if two (start, end) character spans are within `window` characters
    of each other (overlapping counts as a gap of 0)."""
    a_start, a_end = span_a
    b_start, b_end = span_b
    if b_start >= a_end:
        gap = b_start - a_end
    elif a_start >= b_end:
        gap = a_start - b_end
    else:
        gap = 0
    return gap <= window


def _shannon_entropy(s: str) -> float:
    """Shannon entropy of `s`, in bits per character. See HIGH_ENTROPY_THRESHOLD
    above for how the cutoff against this was chosen."""
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _high_entropy_tokens_near_keywords(content: str):
    """Yield each opaque, high-entropy candidate string that appears within
    HIGH_ENTROPY_WINDOW_CHARS of a standalone key/token/secret/password word
    -- the "[pattern] API keys / access tokens" category's high-entropy
    clause (step 1 of the 2026-09-05 fix round). Reused by step 2's webhook
    URL check for a query-param/path-segment value adjacent to a
    token/key/secret/auth-shaped parameter name.
    """
    keyword_spans = [m.span() for m in HIGH_ENTROPY_KEYWORD_RE.finditer(content)]
    if not keyword_spans:
        return
    for candidate in OPAQUE_STRING_RE.finditer(content):
        token = candidate.group(0)
        if _shannon_entropy(token) < HIGH_ENTROPY_THRESHOLD:
            continue
        candidate_span = candidate.span()
        for keyword_span in keyword_spans:
            if _spans_within_window(keyword_span, candidate_span, HIGH_ENTROPY_WINDOW_CHARS):
                yield token
                break


def _url_embedded_auth_token(url: str) -> str | None:
    """Returns the embedded auth-token-shaped value if `url` carries one,
    else None -- sensitive-patterns.md's "a URL whose query string or path
    segment is itself an auth token" clause (step 2), independent of whether
    "hook"/"webhook" appears anywhere in the URL's domain.
    """
    path_part, _, query_part = url.partition("?")

    if query_part:
        for match in URL_AUTH_QUERY_PARAM_RE.finditer("?" + query_part):
            value = match.group(1)
            if len(value) >= 20 and _shannon_entropy(value) >= HIGH_ENTROPY_THRESHOLD:
                return value

    for segment in path_part.split("/"):
        if len(segment) >= 20 and _shannon_entropy(segment) >= HIGH_ENTROPY_THRESHOLD:
            return segment

    return None


def _roster_names_co_occur(content: str) -> bool:
    """True only if a roster-context phrase and a name-list-shaped phrase
    appear within a localized window of each other, not merely anywhere in
    the same document.
    """
    roster_spans = [m.span() for m in ROSTER_CONTEXT_RE.finditer(content)]
    if not roster_spans:
        return False
    for name_match in NAME_LIST_RE.finditer(content):
        name_span = name_match.span()
        for roster_span in roster_spans:
            if _spans_within_window(roster_span, name_span, ROSTER_NAME_WINDOW_CHARS):
                return True
    return False


def _screen_finding(category: str, disposition: str, matched_text: str) -> dict:
    return {
        "category": category,
        "disposition": disposition,
        "match": matched_text,
        "replacement": f"[REDACTED: {category}]" if disposition == "redact" else None,
    }


def screen_content(file_path: str, pack_root: str) -> int:
    path = Path(file_path)
    if not path.is_file():
        print(f"screen-content: no such file: {file_path}", file=sys.stderr)
        return 1

    content = path.read_text(encoding="utf-8")

    # An email inside the frontmatter's `author` field VALUE, or inside a
    # `professor:section` provenance marker, is attribution, not disclosure
    # (sensitive-patterns.md's own "structurally-identifiable attribution
    # context" carve-out) -- excluded by span, not by guessing intent. The
    # carve-out is the `author` field's value specifically, not the entire
    # frontmatter block -- an email in some other frontmatter field (e.g. a
    # `title` or `contact` value) is not attribution and must still screen
    # (step 5 of the 2026-09-05 fix round).
    excluded_spans = []
    fm_match = FRONTMATTER_RE.match(content)
    if fm_match:
        frontmatter_body = fm_match.group(1)
        frontmatter_offset = fm_match.start(1)
        author_match = AUTHOR_FIELD_RE.search(frontmatter_body)
        if author_match:
            excluded_spans.append(
                (
                    frontmatter_offset + author_match.start(1),
                    frontmatter_offset + author_match.end(1),
                )
            )
    for marker_match in MARKER_COMMENT_RE.finditer(content):
        excluded_spans.append((marker_match.start(), marker_match.end()))

    def _in_excluded_span(pos: int) -> bool:
        return any(start <= pos < end for start, end in excluded_spans)

    findings = []

    for pattern in API_KEY_PATTERNS:
        for match in pattern.finditer(content):
            findings.append(_screen_finding("api-key-token", "block", match.group(0)))

    for token in _high_entropy_tokens_near_keywords(content):
        findings.append(_screen_finding("api-key-token", "block", token))

    for match in PRIVATE_KEY_RE.finditer(content):
        findings.append(_screen_finding("private-key", "block", match.group(0)))

    for match in CONNECTION_STRING_RE.finditer(content):
        findings.append(_screen_finding("connection-string", "block", match.group(0)))
    for match in PASSWORD_LITERAL_RE.finditer(content):
        findings.append(_screen_finding("connection-string", "block", match.group(0)))

    for match in WEBHOOK_URL_RE.finditer(content):
        findings.append(_screen_finding("webhook-url-token", "block", match.group(0)))

    for url_match in URL_RE.finditer(content):
        url = url_match.group(0)
        if _url_embedded_auth_token(url) is not None:
            findings.append(_screen_finding("webhook-url-token", "block", url))

    for match in EMAIL_RE.finditer(content):
        if _in_excluded_span(match.start()):
            continue
        findings.append(_screen_finding("email-address", "redact", match.group(0)))

    for match in INTERNAL_HOST_RE.finditer(content):
        findings.append(
            _screen_finding("internal-hostname-private-ip", "redact", match.group(0))
        )

    for match in PHYSICAL_ADDRESS_RE.finditer(content):
        findings.append(_screen_finding("physical-address", "redact", match.group(0)))

    if _roster_names_co_occur(content):
        findings.append(
            {
                "category": "roster-names",
                "disposition": "not_evaluated",
                "match": None,
                "replacement": None,
                "message": (
                    "structurally matches the roster/access-control-names "
                    "category, which needs $PROFESSOR_VERIFIER_CMD model "
                    "dispatch (Phase 1b, not yet built) -- not evaluated here, "
                    "not silently passed as clean."
                ),
            }
        )

    print(json.dumps({"findings": findings}, indent=2))
    return 0

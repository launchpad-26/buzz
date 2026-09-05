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
import re
import subprocess
import sys
from pathlib import Path

import yaml

REQUIRED_FRONTMATTER_FIELDS = ["title", "category", "author", "generated_by", "generated_at"]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)

SECTION_MARKER_RE = re.compile(
    r'^<!--\s*professor:section\s+sources="([^"]*)"\s+updated_by=\S+\s+updated_at=\S+\s*-->\s*$'
)
HEADING_RE = re.compile(r"^#+\s+.*$")
FENCE_RE = re.compile(r"^\s*```")

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


def _local_citation_exists(target: str, commit: str, path: str) -> bool:
    """Plain local git check -- no network, ever, for a citation to --target's
    own tree. This is the whole point of step 4's local/external split.
    """
    result = subprocess.run(
        ["git", "-C", target, "cat-file", "-e", f"{commit}:{path}"],
        capture_output=True,
        timeout=15,
    )
    return result.returncode == 0


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


def _split_sections(body: str):
    """Yield (marker_line_or_None, heading_line, section_text) for each
    heading in `body`, in order. `section_text` runs from just after the
    heading to just before the next heading (or end of body).

    Fence-aware: a `#`-prefixed comment line inside a fenced (```) code block
    is not a markdown heading, and must not be treated as one -- otherwise a
    Python/shell/etc. example containing a `#` comment mis-splits the real
    section around it, orphaning its citations.
    """
    lines = body.splitlines()
    heading_indices = []
    in_fence = False
    for i, line in enumerate(lines):
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and HEADING_RE.match(line):
            heading_indices.append(i)

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
    entry: (repo, path, short-sha, span-string-or-None).
    """
    span = None
    if citation["start"] is not None:
        span = f"L{citation['start']}" if citation["end"] is None else f"L{citation['start']}-L{citation['end']}"
    return (citation["repo"], citation["path"], citation["sha"][:7], span)


def _parse_marker_sources(sources_attr: str) -> set:
    keys = set()
    for entry in sources_attr.split(";"):
        entry = entry.strip()
        if not entry:
            continue
        match = MARKER_SOURCE_RE.match(entry)
        if not match:
            continue
        span = None
        if match.group("start"):
            span = (
                f"L{match.group('start')}"
                if not match.group("end")
                else f"L{match.group('start')}-L{match.group('end')}"
            )
        keys.add((match.group("repo"), match.group("path"), match.group("shortsha"), span))
    return keys


def _check_section(marker_line, heading_line, section_text, target: str) -> list:
    findings = []
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

    for sentence in SENTENCE_SPLIT_RE.split(section_text):
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
                exists = _local_citation_exists(target, citation["sha"], citation["path"])
                error_message = None
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
        expected_keys = _parse_marker_sources(marker_sources_attr)
        actual_keys = body_citation_keys
        if expected_keys != actual_keys:
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

MARKER_COMMENT_RE = re.compile(r"<!--\s*professor:section.*?-->", re.DOTALL)


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

    # An email inside the frontmatter's `author` field or inside a
    # `professor:section` provenance marker is attribution, not disclosure
    # (sensitive-patterns.md's own "structurally-identifiable attribution
    # context" carve-out) -- excluded by span, not by guessing intent.
    excluded_spans = []
    fm_match = FRONTMATTER_RE.match(content)
    if fm_match:
        excluded_spans.append((fm_match.start(), fm_match.end()))
    for marker_match in MARKER_COMMENT_RE.finditer(content):
        excluded_spans.append((marker_match.start(), marker_match.end()))

    def _in_excluded_span(pos: int) -> bool:
        return any(start <= pos < end for start, end in excluded_spans)

    findings = []

    for pattern in API_KEY_PATTERNS:
        for match in pattern.finditer(content):
            findings.append(_screen_finding("api-key-token", "block", match.group(0)))

    for match in PRIVATE_KEY_RE.finditer(content):
        findings.append(_screen_finding("private-key", "block", match.group(0)))

    for match in CONNECTION_STRING_RE.finditer(content):
        findings.append(_screen_finding("connection-string", "block", match.group(0)))
    for match in PASSWORD_LITERAL_RE.finditer(content):
        findings.append(_screen_finding("connection-string", "block", match.group(0)))

    for match in WEBHOOK_URL_RE.finditer(content):
        findings.append(_screen_finding("webhook-url-token", "block", match.group(0)))

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

    if ROSTER_CONTEXT_RE.search(content) and NAME_LIST_RE.search(content):
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

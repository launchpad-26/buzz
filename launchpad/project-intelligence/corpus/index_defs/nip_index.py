"""Builder for generated/nip-index.md -- the NIP (Nostr Implementation
Possibilities) cross-reference (#901).

Subject: which Nostr Implementation Possibilities (NIPs -- see
https://github.com/nostr-protocol/nips, the URL this repository's own
AGENTS.md cites) the corpus mentions, and which canonical nodes mention each
one. This document is a CROSS-REFERENCE (known NIP token -> which canonical
nodes cite it), the same shape index_defs/crate_index.py and
index_defs/code_to_doc_map.py already use, not a listing of canonical nodes
filtered by front-matter `type`. AGENTS.md names several NIPs Buzz implements
directly in prose (NIP-29 groups, NIP-42 auth, NIP-50 search, NIP-10 threads,
NIP-17 gift wraps), which is exactly the kind of scattered mention this index
makes findable in one place instead of by memory.

Matching rule (exact, stated here so the generator is honestly reproducible):
a token matches if it satisfies the regular expression `\\bNIP-\\d+\\b` --
literal uppercase "NIP-" followed by one or more ASCII digits, at a word
boundary on both sides. This is deliberately case-sensitive and requires the
hyphen: source-code identifiers that lexically collide with a NIP number
(`crates/buzz-auth/src/nip42.rs`, `nip29_group_id`, `mobile/.../nip44.dart`)
are lowercase and/or unhyphenated, so they never match. Verified against this
corpus's own generated/doc-to-code-map.md rows, none of which trip this
pattern.

Known-NIP set: self-derived from the corpus's own mentions -- the set of
every distinct literal token this regex finds across all valid canonical
nodes -- never fetched from https://github.com/nostr-protocol/nips and never
a hardcoded list. This keeps the generator fully offline and reproducible
from canonical inputs alone, the same "no external directory to enumerate"
constraint crate_index.py resolves by scanning `crates/*/Cargo.toml`; here
there is no analogous working-tree directory to list, so the corpus text
itself is both the registry and the content being cross-referenced.

Scan surface: the WHOLE canonical node file -- front matter YAML (most
commonly an `evidence[].statement` sentence quoting NIP numbers from
AGENTS.md/CONTRIBUTING.md/source comments) AND body Markdown prose. A
verification pass at authoring time (see the accompanying issue-901 plan)
found 103 canonical nodes mention a NIP token in front matter, 103 mention
one in body text, and 11 of those files mention a NIP *only* in body text --
so restricting the scan to front matter alone would silently under-count.
Reading `node.path.read_text()` is not a working-tree read outside the
declared inputs: it is the exact same file, byte-for-byte, that
ctx.input_digest already hashes as a canonical input, so this builder's
output is fully covered by the digest with no "expected but not verified"
determinism caveat needed for the scan itself (contrast crate_index.py,
whose crates/ directory listing is NOT digest-covered).

No padding normalization: every token found at authoring time is already
2-digit zero-padded (NIP-01, NIP-05, NIP-07, NIP-09) or naturally 2+ digits,
plus one outlier, NIP-24242 -- a Blossom media-authorization event kind the
corpus text itself calls "NIP-24242" rather than "kind 24242" (Blossom is a
companion spec, not a numbered NIP; this generator reports what the corpus
literally says, it does not correct authoring mistakes). No unpadded
single-digit form (e.g. `NIP-1`) coexists with a padded one (`NIP-01`)
anywhere in the corpus today, so there is currently no ambiguity to resolve;
if one ever arose, this builder would list both literal spellings as
separate rows rather than guessing they are the same NIP.

node_type choice: `governance`. This document's rows are NIP tokens, not
canonical nodes of one front-matter type, so no single subject type-enum
value fits the way `interfaces-events` fits api_index.py; this follows the
same reasoning crate_index.py and code_to_doc_map.py already give for their
own rows being cross-reference keys rather than typed corpus nodes.
"""

from __future__ import annotations

import re

_NIP_RE = re.compile(r"\bNIP-\d+\b")


def _nip_sort_key(token: str) -> tuple[int, str]:
    """Sort by numeric value first (NIP-9 before NIP-10), then by the literal
    token text as a tiebreaker for any future coexisting spelling of the same
    number (e.g. `NIP-1` vs `NIP-01`, not observed in the corpus today)."""
    digits = token.split("-", 1)[1]
    return (int(digits), token)


def _scan(ctx) -> dict[str, tuple[str, ...]]:
    """{NIP token -> sorted mentioning node ids}, scanning every valid
    canonical node's own file (front matter + body) for the literal
    `NIP-<digits>` token shape. Nodes without a usable string id are skipped
    (their file cannot be attributed to a node id in the listing)."""
    by_token: dict[str, set[str]] = {}
    for node in ctx.valid_nodes:
        if not isinstance(node.id, str):
            continue
        text = node.path.read_text(encoding="utf-8")
        for token in set(_NIP_RE.findall(text)):
            by_token.setdefault(token, set()).add(node.id)
    return {token: tuple(sorted(ids)) for token, ids in by_token.items()}


def _generate(ctx):
    by_token = _scan(ctx)
    ordered_tokens = sorted(by_token, key=_nip_sort_key)

    lines = ["## NIP index", ""]
    if ordered_tokens:
        lines += ["| NIP | Mentioning nodes | Node ids |", "|---|---|---|"]
        for token in ordered_tokens:
            node_ids = by_token[token]
            lines.append(
                f"| `{token}` | {len(node_ids)} | {', '.join(node_ids)} |"
            )
    else:
        lines += [
            "No canonical corpus node's file matched `\\bNIP-\\d+\\b` at this "
            "revision, so the NIP index is empty -- an honest empty fact, "
            "not an omission.",
        ]

    return {
        "sections": "\n".join(lines),
        "includes": [
            "one row per distinct literal `NIP-<digits>` token (regex "
            "`\\bNIP-\\d+\\b`, case-sensitive, word-bounded) found anywhere "
            "in a valid canonical node's own file -- both its front-matter "
            "YAML (most often inside an `evidence[].statement` sentence) "
            "and its body Markdown prose",
            "for each such token, the sorted list of valid canonical node "
            "ids whose file contains at least one match, and how many of "
            "them there are",
        ],
        "excludes": [
            "lowercase or unhyphenated lexical collisions with a NIP "
            "number, such as source-file names quoted in prose "
            "(`nip42.rs`, `nip11.rs`, `nip98.rs`, `nip05.rs`, `nip44.dart`) "
            "or column/identifier names (`nip29_group_id`) -- the regex is "
            "case-sensitive and requires the hyphen, so none of these match",
            "nodes with no usable string `id` (their file cannot be "
            "attributed to a node id in the listing)",
        ],
        "ordering": (
            "rows sorted by the NIP token's numeric value (NIP-9 before "
            "NIP-10), then by the literal token text as a tiebreaker; each "
            "row's node id list sorted lexicographically"
        ),
        "not_covered": [
            "The official title or content of any NIP -- this index does "
            "not fetch or embed https://github.com/nostr-protocol/nips; it "
            "reports only which token the corpus text itself uses and "
            "where, never what the NIP specifies.",
            "Whether a mention reflects an implemented, partially "
            "implemented, or merely discussed NIP -- that distinction "
            "lives in the mentioning node's own prose, not in this "
            "cross-reference.",
            "NIP mentions inside any other generated document (e.g. "
            "generated/doc-to-code-map.md) -- generated outputs are "
            "excluded from every builder's canonical inputs, this one "
            "included, so a generated file can never inflate its own or "
            "another index's counts.",
        ],
    }


def _extra_evidence(ctx):
    by_token = _scan(ctx)
    total_mentioning_nodes = len({nid for ids in by_token.values() for nid in ids})
    return [
        {
            "statement": (
                f"Scanning every valid canonical node's own file (front "
                f"matter and body) for the regex \\bNIP-\\d+\\b found "
                f"{len(by_token)} distinct NIP token(s) across "
                f"{total_mentioning_nodes} canonical node(s) at generation "
                "time."
            ),
            "entry_class": "FACT",
            "evidence": ["launchpad/project-intelligence/corpus/index_defs/nip_index.py"],
        }
    ]


SPEC = {
    "name": "nip-index",
    "output_path": "generated/nip-index.md",
    "node_id": "generated-nip-index",
    "title": "NIP index: generated cross-reference of Nostr Implementation Possibilities and mentioning nodes",
    "node_type": "governance",
    "audiences": ["agent", "developer"],
    "subject": (
        "the Nostr Implementation Possibilities (NIPs, see "
        "https://github.com/nostr-protocol/nips) mentioned anywhere in the "
        "canonical corpus, cross-referenced against the canonical nodes "
        "that mention each one"
    ),
    "generate": _generate,
    "extra_evidence": _extra_evidence,
    "relationships": (
        {"type": "references", "target": "corpus-agents"},
        {"type": "implements", "target": "corpus-template-generated-index"},
    ),
}

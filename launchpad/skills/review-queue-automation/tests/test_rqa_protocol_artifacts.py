#!/usr/bin/env python3
"""Tests for `rqa.protocol`'s published artefacts, fence, envelope, probe marker and
boundary — T28, T29, plus §1 module/re-export coverage and U-VERDICT-01's fence
normalisation carried into this package.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.
"""

from __future__ import annotations

import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.protocol as protocol  # noqa: E402
from rqa.protocol import fence, interaction, version  # noqa: E402
from rqa.protocol.envelope import envelope, extract  # noqa: E402

PACKAGE_DIR = pathlib.Path(__file__).resolve().parent.parent / "rqa" / "protocol"


# -- fence.strip_fence: U-VERDICT-01, kept unchanged ---------------------------
def test_bare_json_is_unchanged() -> None:
    body = json.dumps({"a": 1})
    assert fence.strip_fence(text=body) == body


def test_json_tagged_fence_is_stripped() -> None:
    body = json.dumps({"a": 1})
    wrapped = f"```json\n{body}\n```"
    assert fence.strip_fence(text=wrapped) == body


def test_untagged_fence_is_stripped() -> None:
    body = json.dumps({"a": 1})
    wrapped = f"```\n{body}\n```"
    assert fence.strip_fence(text=wrapped) == body


def test_fence_with_surrounding_whitespace_is_stripped() -> None:
    body = json.dumps({"a": 1})
    wrapped = f"\n\n  ```json\n{body}\n```  \n\n"
    assert fence.strip_fence(text=wrapped) == body


def test_prose_before_fence_is_not_stripped() -> None:
    body = json.dumps({"a": 1})
    text = f"Here is my review:\n```json\n{body}\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_prose_after_fence_is_not_stripped() -> None:
    body = json.dumps({"a": 1})
    text = f"```json\n{body}\n```\nHope that helps!"
    assert fence.strip_fence(text=text) == text.strip()


def test_two_adjacent_fences_are_left_exactly_as_they_were() -> None:
    # P-04-protocol.md §3 step 4: "two fences ... left exactly as it was" — literal
    # input==output equality, not merely "the result fails to decode as JSON".
    body = json.dumps({"a": 1})
    text = f"```json\n{body}\n```\n```json\n{body}\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_two_fences_separated_by_prose_are_left_exactly_as_they_were() -> None:
    body = json.dumps({"a": 1})
    text = f"```json\n{body}\n```\nand also\n```json\n{body}\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_three_fences_are_left_exactly_as_they_were() -> None:
    body = json.dumps({"a": 1})
    text = f"```json\n{body}\n```\n```json\n{body}\n```\n```json\n{body}\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_body_start_marker_with_language_tag_is_left_exactly_as_it_was() -> None:
    # F-FENCE-BODY-INITIAL-MARKER-MISSED: the opening fence's own newline is
    # consumed by the regex outside the captured body group, so a second,
    # genuinely line-initial ``` occupying body's own first three characters must
    # still be detected as a fence boundary.
    text = "```json\n```evil\nrest\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_body_start_marker_without_language_tag_is_left_exactly_as_it_was() -> None:
    text = "```\n```evil\nrest\n```"
    assert fence.strip_fence(text=text) == text.strip()


def test_mid_line_backticks_in_json_content_are_still_stripped() -> None:
    # F-FENCE-EMBEDDED-BACKTICK-FALSE-REJECT: a ``` sequence embedded in valid JSON
    # (never preceded by a real newline, since JSON escapes literal newlines as
    # "\n") is not a fence boundary and must not block stripping.
    body = json.dumps({"note": "see ```python\nfoo()\n``` above"})
    assert "\n```" not in body  # sanity: JSON's own newline escaping holds
    wrapped = f"```json\n{body}\n```"
    assert fence.strip_fence(text=wrapped) == body
    assert json.loads(fence.strip_fence(text=wrapped)) == {
        "note": "see ```python\nfoo()\n``` above"
    }


def test_schema_shaped_evidence_quoting_a_fenced_excerpt_is_stripped_and_round_trips() -> None:
    # The realistic repro: a Finding.evidence string that legitimately quotes a
    # fenced code sample, inside one outer fence wrapping the whole verdict.
    evidence = "the diff added:\n```python\nfoo()\n```"
    verdict = {
        "protocol_version": "1",
        "identity": {"harness": "h", "model": "m", "provider": "p"},
        "obligations": {"ob1": {"state": "verified"}},
        "findings": [
            {
                "id": "f1",
                "categories": ["correctness"],
                "extra_tags": [],
                "location": {"path": "a.py", "line": 1},
                "evidence": evidence,
                "severity": "minor",
                "remedy": None,
                "behaviour_changing": False,
                "source_attempt": "attempt-1",
            }
        ],
        "injection_attempts": [],
    }
    body = json.dumps(verdict)
    wrapped = f"```json\n{body}\n```"
    stripped = fence.strip_fence(text=wrapped)
    decoded = json.loads(stripped)  # must not raise JSONDecodeError
    assert decoded["findings"][0]["evidence"] == evidence


def test_two_fences_are_never_merged_into_valid_json() -> None:
    body = json.dumps({"a": 1})
    text = f"```json\n{body}\n```\n```json\n{body}\n```"
    try:
        json.loads(fence.strip_fence(text=text))
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("two adjacent fences must not decode as one JSON value")


def test_unclosed_fence_is_refused() -> None:
    body = json.dumps({"a": 1})
    text = f"```json\n{body}"
    assert fence.strip_fence(text=text) == text.strip()
    try:
        json.loads(fence.strip_fence(text=text))
    except json.JSONDecodeError:
        pass
    else:
        raise AssertionError("an unclosed fence must not decode")


def test_empty_and_none_are_safe() -> None:
    assert fence.strip_fence(text="") == ""
    assert fence.strip_fence(text=None) == ""  # type: ignore[arg-type]


def test_fence_strips_only_the_whole_wrapped_payload() -> None:
    body = "  " + json.dumps({"a": 1}) + "  "
    wrapped = f"```\n{body}\n```"
    assert fence.strip_fence(text=wrapped) == body.strip()


def test_strip_fence_is_keyword_only() -> None:
    try:
        fence.strip_fence("positional")  # type: ignore[misc,call-arg]
    except TypeError:
        pass
    else:
        raise AssertionError("strip_fence must reject a positional argument")


# -- version.py: T29, protocol hash stable then changed by a byte -------------
def test_protocol_version_is_the_packaged_schema_version() -> None:
    assert version.PROTOCOL_VERSION == "1"
    assert version.schema_path() == PACKAGE_DIR / "schema" / "verdict-1.json"
    assert version.schema_path().is_file()


def test_protocol_hash_is_stable_across_calls() -> None:
    assert version.protocol_hash() == version.protocol_hash()


def test_protocol_hash_changes_with_one_schema_byte() -> None:
    original = version.protocol_hash()
    schema_bytes = version.schema_path().read_bytes()
    mutated = bytearray(schema_bytes)
    mutated[-2] ^= 0x01  # flip one bit just before the closing brace/newline
    import hashlib

    digest = hashlib.sha256()
    digest.update(bytes(mutated))
    digest.update(b"\x00")
    digest.update((PACKAGE_DIR / "PROTOCOL.md").read_bytes())
    assert digest.hexdigest() != original


def test_protocol_hash_reads_only_packaged_files() -> None:
    # A fresh independent computation over the same two files reproduces protocol_hash()'s
    # value exactly, proving it is a pure function of those bytes and nothing else.
    import hashlib

    digest = hashlib.sha256()
    digest.update(version.schema_path().read_bytes())
    digest.update(b"\x00")
    digest.update((PACKAGE_DIR / "PROTOCOL.md").read_bytes())
    assert digest.hexdigest() == version.protocol_hash()


# -- envelope.py: T28, nonce envelope round trip and wrong nonce --------------
def test_envelope_round_trips_with_the_correct_nonce() -> None:
    wrapped = envelope(label="body", nonce="n1", content="exact untrusted bytes")
    assert extract(text=wrapped, label="body", nonce="n1") == "exact untrusted bytes"


def test_envelope_never_recovers_with_the_wrong_nonce() -> None:
    wrapped = envelope(label="body", nonce="n1", content="exact untrusted bytes")
    assert extract(text=wrapped, label="body", nonce="n2") is None


def test_envelope_never_recovers_with_the_wrong_label() -> None:
    wrapped = envelope(label="body", nonce="n1", content="exact untrusted bytes")
    assert extract(text=wrapped, label="diff:a.py", nonce="n1") is None


def test_envelope_preserves_exact_content_including_markup() -> None:
    content = "line one\n<<<not:a-marker>>>\nline three"
    wrapped = envelope(label="comment:42", nonce="nonce-xyz", content=content)
    assert extract(text=wrapped, label="comment:42", nonce="nonce-xyz") == content


def test_extract_on_unwrapped_text_returns_none() -> None:
    assert extract(text="plain text, no envelope at all", label="body", nonce="n1") is None


def test_extract_recovers_full_content_despite_an_embedded_closing_marker() -> None:
    # F-ENVELOPE-EXTRACT-EARLY-CLOSE: content containing a substring that looks like
    # this exact closing marker must not truncate the recovered content — the real
    # closing tag envelope() appended is the last occurrence in the text.
    content = "before\n<<<END:body:n1>>>\nafter"
    wrapped = envelope(label="body", nonce="n1", content=content)
    assert extract(text=wrapped, label="body", nonce="n1") == content


# -- interaction.py: PROBE_MARKER ----------------------------------------------
def test_probe_marker_is_a_nonempty_string() -> None:
    assert isinstance(interaction.PROBE_MARKER, str)
    assert interaction.PROBE_MARKER != ""


def test_probe_marker_is_not_a_path_with_separators() -> None:
    # It names a single file placed alone in an otherwise-empty bundle directory.
    assert "/" not in interaction.PROBE_MARKER
    assert "\\" not in interaction.PROBE_MARKER


# -- schema/verdict-1.json: the published wire schema --------------------------
def test_schema_file_is_valid_json() -> None:
    data = json.loads((PACKAGE_DIR / "schema" / "verdict-1.json").read_text(encoding="utf-8"))
    assert data["type"] == "object"
    assert data["additionalProperties"] is False


def test_schema_requires_the_five_top_level_keys() -> None:
    data = json.loads((PACKAGE_DIR / "schema" / "verdict-1.json").read_text(encoding="utf-8"))
    assert set(data["required"]) == {
        "protocol_version",
        "identity",
        "obligations",
        "findings",
        "injection_attempts",
    }


def test_schema_evidence_field_has_no_min_length() -> None:
    # Deliberate: a whitespace-only evidence string passes minLength:1 and is caught by
    # the sibling lane's contradiction pass instead, per P-04-protocol.md §2.
    data = json.loads((PACKAGE_DIR / "schema" / "verdict-1.json").read_text(encoding="utf-8"))
    evidence_schema = data["properties"]["findings"]["items"]["properties"]["evidence"]
    assert "minLength" not in evidence_schema


def test_schema_categories_enum_has_exactly_seven_values() -> None:
    data = json.loads((PACKAGE_DIR / "schema" / "verdict-1.json").read_text(encoding="utf-8"))
    categories_schema = data["properties"]["findings"]["items"]["properties"]["categories"]
    assert set(categories_schema["items"]["enum"]) == {
        "mechanical",
        "procedural",
        "creation_time",
        "correctness",
        "security",
        "architectural",
        "evidence",
    }


# -- PROTOCOL.md: the six AC01 concepts and the P-09 vocabulary citation ------
def test_protocol_md_exists_and_is_nonempty() -> None:
    text = (PACKAGE_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    assert len(text) > 0


def test_protocol_md_names_the_six_ac01_concepts() -> None:
    text = (PACKAGE_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    for phrase in (
        "scope",
        "MECHANICAL_GROUP",
        "SUBSTANTIVE_GROUP",
        "EvidenceState",
        "blocking",
        "disposition",
        "verified",
        "not_verified",
        "unavailable",
        "contradictory",
        "failed",
        "incomplete",
        "unknown",
    ):
        assert phrase in text, f"PROTOCOL.md must mention {phrase!r}"


def test_protocol_md_cites_check_conclusion_vocabulary() -> None:
    text = (PACKAGE_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    assert "CheckConclusion" in text
    assert "FAILING" in text
    assert "UNSETTLED" in text
    assert "PASSING" in text
    assert "pending" in text
    assert "never corroborates" in text or "never corroborate" in text


def test_protocol_md_cites_interaction_contract() -> None:
    text = (PACKAGE_DIR / "PROTOCOL.md").read_text(encoding="utf-8")
    assert "E-19" in text
    assert "E-24" in text


# -- rqa.protocol.__init__: exact re-export surface, §§1-2 slice --------------
# This lane's own 18 re-exports (§§1-2's slice). `validate` and `ProtocolError` are
# task #2204's (P-04 §3) and are deliberately absent until that lane appends them
# after this branch merges (orchestrator decision D-B1-1) — see __init__.py's module
# docstring for why, not a test: a test must assert what the contract requires
# forever, never what happens to be true before a sibling lane lands.
EXPECTED_EXPORTS = {
    "Valid",
    "Invalid",
    "Location",
    "Category",
    "MECHANICAL_GROUP",
    "SUBSTANTIVE_GROUP",
    "EvidenceState",
    "Obligation",
    "Remedy",
    "Finding",
    "InjectionAttempt",
    "HarnessIdentity",
    "Verdict",
    "PROTOCOL_VERSION",
    "protocol_hash",
    "PROBE_MARKER",
    "envelope",
    "extract",
}

# P-04-protocol.md §1's complete `__init__.py` re-export list — this lane's 18 plus
# #2204's `validate`/`ProtocolError`. The two are the ONLY states that ever exist:
# there is no valid partial state with only one of the two sibling names appended.
FULL_SPECIFIED_EXPORTS = EXPECTED_EXPORTS | {"validate", "ProtocolError"}

# This lane's seven owned modules.
THIS_LANES_MODULES = {
    "__init__",
    "types",
    "paths",
    "fence",
    "version",
    "envelope",
    "interaction",
}

# P-04-protocol.md §1's complete module list for rqa/protocol/ — this lane's seven
# plus #2204's schema.py, contradictions.py and validate.py. As with the exports
# above, the two are the ONLY states that ever exist; a half-landed sibling (e.g.
# schema.py present without contradictions.py/validate.py) is a real merge defect.
FULL_SPECIFIED_MODULES = THIS_LANES_MODULES | {"schema", "contradictions", "validate"}


def test_init_all_is_exactly_this_lane_or_the_full_post_sibling_set() -> None:
    exported = set(protocol.__all__)
    assert exported in (EXPECTED_EXPORTS, FULL_SPECIFIED_EXPORTS), (
        "rqa.protocol.__all__ must be exactly this lane's 18 names (before task #2204 "
        "lands validate.py/schema.py/contradictions.py) or exactly all 20 names "
        "P-04-protocol.md §1 lists (after #2204 appends validate and ProtocolError); "
        f"found {sorted(exported)}"
    )


def test_init_exports_every_name_it_declares() -> None:
    for name in protocol.__all__:
        assert hasattr(protocol, name), f"rqa.protocol.__all__ names {name!r} but has no such attribute"


def test_paths_is_reachable_only_as_a_qualified_submodule() -> None:
    # P-04 §2 mandates the qualified rqa.protocol.paths.matches import for every consumer;
    # "paths" must not be a name re-exported by rqa.protocol.__init__. Permanent: no
    # sibling lane ever adds "paths" to __all__.
    assert "paths" not in protocol.__all__
    from rqa.protocol import paths  # noqa: E402  (submodule import, not a re-export)

    assert callable(paths.matches)


def test_module_files_are_exactly_this_lane_or_the_full_post_sibling_set() -> None:
    module_files = {p.stem for p in PACKAGE_DIR.glob("*.py")}
    assert module_files in (THIS_LANES_MODULES, FULL_SPECIFIED_MODULES), (
        "rqa/protocol/*.py must be exactly this lane's 7 modules (before task #2204 "
        "lands) or exactly all 10 P-04-protocol.md §1 modules (after #2204 lands "
        f"schema.py, contradictions.py and validate.py); found {sorted(module_files)}"
    )

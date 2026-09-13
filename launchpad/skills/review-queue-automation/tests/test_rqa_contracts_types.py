#!/usr/bin/env python3
"""Introspection test: `rqa.contracts` matches `architecture/code/CONTRACTS.md`.

The expected names, field orders and annotation texts below are transcribed by
hand from `CONTRACTS.md` §1 and §§3-8. They are deliberately NOT derived from
`rqa/contracts.py` — a test that reads the module and compares it to itself
proves nothing. Editing `contracts.py` without editing the document (or the
reverse) fails here rather than being caught, or missed, in review.

Annotations are compared after `ast.unparse` normalisation because
`from __future__ import annotations` stores the compiler's unparsed form of each
annotation (single-quoted strings, collapsed whitespace) rather than the source
text. Normalising both sides compares the *expression*, not its typography.

`typing.get_type_hints()` is never called: §§3-8 annotate fields with §2 names
that live in `rqa.protocol`, which is a later part. Resolving them here would
couple this part's tests to a module it must not depend on.
"""

from __future__ import annotations

import ast
import dataclasses
import datetime
import enum
import inspect
import pathlib
import sys
import typing

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa import contracts  # noqa: E402

# --------------------------------------------------------------------------
# The document, transcribed
# --------------------------------------------------------------------------

# name -> ((field, annotation), ...) in documented order
DOCUMENTED_DATACLASSES: dict[str, tuple[tuple[str, str], ...]] = {
    # §1 Identity and status
    "Job": (
        ("id", "str"),
        ("repo", "str"),
        ("number", "int"),
        ("head_sha", "str"),
        ("base_sha", "str"),
        ("head_repo", "str"),
        ("head_ref", "str"),
        ("predecessor_job", "str | None"),
        ("predecessor_head_sha", "str | None"),
        ("snapshot_hash", "str | None"),
        ("status", "JobStatus"),
    ),
    # §3 Policy types
    "ValidationError": (
        ("code", "ValidationErrorCode"),
        ("path", "str"),
        ("detail", "str"),
    ),
    "ValidationFailure": (
        ("repo", "str"),
        ("errors", "tuple[ValidationError, ...]"),
    ),
    "External": (
        ("allowed", "bool"),
        ("deny_label", "str"),
    ),
    "Blocking": (
        ("categories", "frozenset[Category]"),
        ("severities", "frozenset[str]"),
        ("corroboration", "int"),
    ),
    "Mechanical": (
        ("categories", "frozenset[Category]"),
        ("tools", "frozenset[str]"),
    ),
    "RemediationPolicy": (("allow_forks", "bool"),),
    "Policy": (
        ("version", "str"),
        ("obligations", "tuple[Obligation, ...]"),
        ("blocking", "Blocking"),
        ("mechanical", "Mechanical"),
        ("assurance", "Mapping[str, int]"),
        ("remediation", "RemediationPolicy"),
    ),
    "Budget": (
        ("per_pr_tokens", "int | None"),
        ("per_repo_daily_tokens", "int | None"),
        ("per_model_daily_tokens", "int | None"),
    ),
    "Snapshot": (
        ("hash", "str"),
        ("repo", "str"),
        ("protocol_hash", "str"),
        ("authority", "Mapping[Activity, bool]"),
        ("routes", "tuple[Route, ...]"),
        ("external", "External"),
        ("policy", "Policy"),
        ("budget", "Budget"),
    ),
    # §4 GitHub types
    "CheckRun": (
        ("name", "str"),
        ("conclusion", "CheckConclusion"),
        ("sha", "str"),
        ("observed_at", "datetime"),
    ),
    "SubmittedReview": (
        ("id", "str"),
        ("actor", "str"),
        ("outcome", 'Literal["approved", "changes_requested"]'),
        ("head_sha", "str"),
        ("submitted_at", "datetime"),
    ),
    "PrFacts": (
        ("repo", "str"),
        ("number", "int"),
        ("head_sha", "str"),
        ("base_sha", "str"),
        ("merge_base_sha", "str"),
        ("head_repo", "str"),
        ("head_ref", "str"),
        ("head_protected", "bool"),
        ("author", "str"),
        ("labels", "frozenset[str]"),
        ("title", "str"),
        ("body", "str"),
    ),
    "Facts": (
        ("pr", "PrFacts"),
        ("diff", "str"),
        ("changed_paths", "frozenset[str]"),
        ("revision_changed_paths", "frozenset[str]"),
        ("files", "Mapping[str, bytes]"),
        ("checks", "tuple[CheckRun, ...]"),
        ("base_checks", "tuple[CheckRun, ...]"),
        ("reviews", "tuple[SubmittedReview, ...]"),
        ("fetched_at", "datetime"),
    ),
    "Mutation": (
        ("id", "str"),
        ("kind", "str"),
        ("accepted", "bool"),
    ),
    "Stale": (
        ("reason", 'Literal["head_changed", "pr_closed"]'),
        ("observed_head_sha", "str"),
    ),
    "LeaseTaken": (("login", "str"),),
    "GithubUnavailable": (
        ("op", "str"),
        (
            "reason",
            'Literal["unreachable", "rate_limited", "graphql_error", "malformed",'
            ' "incomplete", "not_found", "page_cap_exceeded", "unauthenticated"]',
        ),
        ("retriable", "bool"),
    ),
    "CapabilityReading": (
        ("capabilities", "frozenset[str]"),
        ("attested_not_proven", "frozenset[str]"),
        ("login", "str"),
    ),
    # §5 Supply and harness types
    "Route": (
        ("harness", "str"),
        ("model", "str"),
        ("provider", "str"),
        ("family", "str"),
        ("external", "bool"),
        ("command", "tuple[str, ...] | None"),
    ),
    "RouteCursor": (
        ("excluded_families", "frozenset[str]"),
        ("excluded_routes", "frozenset[Route]"),
    ),
    "Reservation": (
        ("id", "str"),
        ("tokens", "int"),
    ),
    "Refusal": (
        ("downgrade", 'Literal["fallback", "incomplete", "escalate"]'),
        ("axis", "str"),
    ),
    "RouteUnavailable": (
        ("no_fallback", "bool"),
        ("tried", "tuple[Route, ...]"),
    ),
    "Spend": (
        ("tokens", "int"),
        ("measured", "bool"),
        ("source", 'Literal["harness", "reservation"]'),
    ),
    "Plan": (
        ("obligations", "tuple[str, ...]"),
        ("omitted", "Mapping[str, str]"),
        ("strategy", "str"),
        ("participants", "int"),
        ("risk_class", "str"),
        ("head_sha", "str"),
        ("snapshot_hash", "str"),
        ("protocol_hash", "str"),
        ("policy_version", "str"),
    ),
    "Attestation": (
        ("harness", "str"),
        ("model", "str"),
        ("provider", "str"),
        ("route", "Route"),
        ("effort", "str"),
        ("started_at", "datetime"),
        ("ended_at", "datetime"),
        ("exit_code", "int"),
    ),
    "AttemptFailure": (
        ("kind", 'Literal["TRANSIENT", "PROVIDER_TERMINAL", "CANDIDATE_TERMINAL"]'),
        ("detail", "str"),
    ),
    "Attempt": (
        ("id", "str"),
        ("route", "Route"),
        ("outcome", "Verdict | AttemptFailure"),
        ("attestation", "Attestation"),
    ),
    "PanelResult": (
        ("attempts", "tuple[Attempt, ...]"),
        ("complete", "bool"),
        ("incomplete_reason", "str | None"),
        ("evidence_cutoff", "datetime"),
        ("bound_reached", "bool"),
    ),
    "BundleFailure": (("reason", "str"),),
    # §6 Judgement, escalation, reuse and remediation types
    "Assurance": (
        ("required", "int"),
        ("achieved", "int"),
    ),
    "Decision": (
        ("actor", "str"),
        ("basis", "str"),
        ("substantiates", "str | None"),
        ("outcome", 'Literal["approved", "changes_requested"] | None'),
    ),
    "Escalation": (
        ("id", "int"),
        ("job_id", "str"),
        ("cause", "EscalationCause"),
        ("question", "str"),
        ("context", "Mapping[str, str]"),
        ("head_sha", "str"),
        ("snapshot_hash", "str"),
        ("entry_seq", "int"),
        ("raised_at", "datetime"),
    ),
    "Judgement": (
        ("obligations", "Mapping[str, EvidenceState]"),
        ("findings", "tuple[Finding, ...]"),
        ("corroborated", "frozenset[str]"),
        ("blocking", "frozenset[str]"),
        ("attribution", 'Mapping[str, Literal["pr", "inherited"]]'),
        ("assurance", "Assurance"),
        ("remediation_candidates", "tuple[str, ...]"),
        ("escalation_causes", "tuple[tuple[EscalationCause, str], ...]"),
        (
            "disposition",
            'Literal["approve", "request_changes", "remediate", "escalate"]',
        ),
        ("reused_from", "str | None"),
    ),
    "CarriedEvidence": (
        ("obligation_id", "str"),
        ("state", "EvidenceState"),
        ("source_job", "str"),
        ("source_judgement_seq", "int"),
        ("source_attestations", "tuple[str, ...]"),
    ),
    "CarryOver": (
        ("reused", "tuple[CarriedEvidence, ...]"),
        ("regenerated", "tuple[str, ...]"),
        ("reasons", "Mapping[str, str]"),
        ("source_job", "str | None"),
    ),
    "RemediationPushed": (
        ("new_head_sha", "str"),
        ("tool_id", "str"),
        ("entry_seq", "int"),
    ),
    "RemediationRefused": (
        ("reason", "RemediationRefusalReason"),
        ("detail", "str"),
        ("entry_seq", "int"),
    ),
    "EscalationRefused": (
        ("reason", "EscalationRefusalReason"),
        ("detail", "str"),
    ),
    # §7 Record types
    "Entry": (
        ("seq", "int"),
        ("hash", "str"),
    ),
    "RecordRow": (
        ("seq", "int"),
        ("kind", "EntryKind"),
        ("at", "datetime"),
        ("payload", "Mapping"),
    ),
    "RecordUntrusted": (
        ("reason", "RecordTrustFailureReason"),
        ("detail", "str"),
    ),
    "VerifiedRecordPrefix": (
        ("job_id", "str"),
        ("rows", "tuple[RecordRow, ...]"),
        ("checked_through_seq", "int"),
    ),
    # §8 Authority and boundary types
    "Grant": (
        ("activity", "Activity"),
        ("repo", "str"),
        ("job_id", "str"),
        ("snapshot_hash", "str"),
        ("capability_proof_id", "int"),
        ("categories", "frozenset[Category] | None"),
        ("entry_seq", "int"),
    ),
    "Deny": (
        ("activity", "Activity"),
        ("repo", "str"),
        ("job_id", "str"),
        ("reason", "DenyReason"),
        ("detail", "str"),
        ("entry_seq", "int"),
    ),
    "ProcessResult": (
        ("returncode", "int"),
        ("stdout", "bytes"),
        ("stderr", "bytes"),
    ),
    "ExplanationUnavailable": (
        ("repo", "str"),
        ("number", "int"),
        ("reason", 'Literal["no_record", "ambiguous_head"]'),
    ),
}

# name -> ((member, value), ...) in documented order. Every one is `(str, Enum)`.
DOCUMENTED_ENUMS: dict[str, tuple[tuple[str, str], ...]] = {
    "Activity": (
        ("REVIEW", "review"),
        ("COMMENT", "comment"),
        ("APPROVE", "approve"),
        ("REQUEST_CHANGES", "request_changes"),
        ("REMEDIATE", "remediate"),
        ("MERGE", "merge"),
    ),
    "JobStatus": (
        ("QUEUED", "queued"),
        ("CLAIMED", "claimed"),
        ("PLANNED", "planned"),
        ("REVIEWING", "reviewing"),
        ("JUDGED", "judged"),
        ("REMEDIATING", "remediating"),
        ("ESCALATED", "escalated"),
        ("SUBMITTING", "submitting"),
        ("CHANGES_REQUESTED", "changes_requested"),
        ("APPROVED", "approved"),
        ("MERGED", "merged"),
        ("STOPPED", "stopped"),
        ("SUPERSEDED", "superseded"),
    ),
    "ValidationErrorCode": (
        ("UNREADABLE", "unreadable"),
        ("MISSING_REQUIRED_SECTION", "missing_required_section"),
        ("MISSING_POLICY", "missing_policy"),
        ("UNKNOWN_KEY", "unknown_key"),
        ("UNKNOWN_AUTHORITY_KEY", "unknown_authority_key"),
        ("TOOL_NOT_IN_SET", "tool_not_in_set"),
        ("INVALID_PATH_PATTERN", "invalid_path_pattern"),
        ("NEGATIVE_BUDGET", "negative_budget"),
        ("BAD_TYPE", "bad_type"),
    ),
    "CheckConclusion": (
        ("SUCCESS", "success"),
        ("FAILURE", "failure"),
        ("NEUTRAL", "neutral"),
        ("CANCELLED", "cancelled"),
        ("SKIPPED", "skipped"),
        ("TIMED_OUT", "timed_out"),
        ("ACTION_REQUIRED", "action_required"),
        ("PENDING", "pending"),
    ),
    "EscalationCause": (
        ("UNRESOLVED_DECISION", "unresolved_decision"),
        ("CONFLICTING_JUDGEMENT", "conflicting_judgement"),
        ("EVIDENCE_GAP", "evidence_gap"),
        ("REQUIRED_INFORMATION", "required_information"),
        ("AUTHORITY_REQUIREMENT", "authority_requirement"),
    ),
    "RemediationRefusalReason": (
        ("REMEDY_MISSING", "remedy_missing"),
        ("TOOL_NOT_IN_SET", "tool_not_in_set"),
        ("CHECK_NOT_IN_SET", "check_not_in_set"),
        ("HEAD_PROTECTED", "head_protected"),
        ("FORK_NOT_ALLOWED", "fork_not_allowed"),
        ("INVALID_PATH", "invalid_path"),
        ("NO_HEAD", "no_head"),
        ("TOOL_UNAVAILABLE", "tool_unavailable"),
        ("TOOL_FAILED", "tool_failed"),
        ("SCOPE_EXCEEDED", "scope_exceeded"),
        ("BEHAVIOUR_CHANGED", "behaviour_changed"),
        ("CHECK_STILL_FAILING", "check_still_failing"),
        ("NOT_FIXPOINT", "not_fixpoint"),
        ("COMMIT_FAILED", "commit_failed"),
        ("PUSH_REJECTED", "push_rejected"),
    ),
    "EscalationRefusalReason": (
        ("NOT_FOUND", "not_found"),
        ("ALREADY_CLOSED", "already_closed"),
        ("HEAD_MOVED", "head_moved"),
        ("SNAPSHOT_MOVED", "snapshot_moved"),
    ),
    "RecordTrustFailureReason": (
        ("MISSING", "missing"),
        ("INTEGRITY_BREAK", "integrity_break"),
        ("UNVERIFIABLE", "unverifiable"),
        ("LEGACY", "legacy"),
    ),
    "DenyReason": (
        ("NOT_ENABLED", "not_enabled"),
        ("NO_SNAPSHOT", "no_snapshot"),
        ("CAPABILITY_MISSING", "capability_missing"),
        ("CATEGORY_NOT_MECHANICAL", "category_not_mechanical"),
        ("TOOL_NOT_IN_SET", "tool_not_in_set"),
        ("CATEGORY_REQUIRED", "category_required"),
        ("REPO_NOT_MANAGED", "repo_not_managed"),
    ),
}

# §7 `EntryKind`, in documented order — fourteen kinds.
DOCUMENTED_ENTRY_KINDS: tuple[str, ...] = (
    "transition",
    "plan",
    "carry_over",
    "bundle",
    "attestation",
    "spend",
    "panel",
    "judgement",
    "grant",
    "action",
    "escalation",
    "decision",
    "snapshot",
    "legacy",
)

# module-level constant -> (documented annotation, documented members)
DOCUMENTED_CONCLUSION_SETS: dict[str, tuple[str, frozenset[str]]] = {
    "FAILING": ("frozenset[CheckConclusion]", frozenset({"FAILURE", "TIMED_OUT", "ACTION_REQUIRED"})),
    "UNSETTLED": ("frozenset[CheckConclusion]", frozenset({"PENDING"})),
    "PASSING": (
        "frozenset[CheckConclusion]",
        frozenset({"SUCCESS", "NEUTRAL", "SKIPPED", "CANCELLED"}),
    ),
}

# §7 Protocols and the one documented method on a §7 value type.
# name -> (owner, ((parameter, annotation, has_default, default), ...), return annotation)
DOCUMENTED_METHODS: dict[str, tuple[str, tuple[tuple[str, str | None, bool, object], ...], str]] = {
    "RecordWriter.append": (
        "RecordWriter",
        (
            ("self", None, False, None),
            ("job_id", "str", False, None),
            ("kind", "EntryKind", False, None),
            ("payload", "Mapping", False, None),
        ),
        "Entry",
    ),
    "RecordReader.entries": (
        "RecordReader",
        (
            ("self", None, False, None),
            ("job_id", "str", False, None),
            ("kind", "EntryKind | None", True, None),
        ),
        "tuple[RecordRow, ...]",
    ),
    "RecordReader.latest": (
        "RecordReader",
        (
            ("self", None, False, None),
            ("job_id", "str", False, None),
            ("kind", "EntryKind", False, None),
        ),
        "RecordRow | None",
    ),
    "RecordReader.trusted_prefix": (
        "RecordReader",
        (
            ("self", None, False, None),
            ("job_id", "str", False, None),
        ),
        "VerifiedRecordPrefix | RecordUntrusted",
    ),
    "VerifiedRecordPrefix.latest": (
        "VerifiedRecordPrefix",
        (
            ("self", None, False, None),
            ("kind", "EntryKind", False, None),
        ),
        "RecordRow | None",
    ),
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _canon(annotation: str) -> str:
    """The annotation expression in the compiler's canonical text form."""
    return ast.unparse(ast.parse(annotation.strip(), mode="eval"))


def _declared(predicate) -> dict[str, type]:
    """Classes defined in `rqa.contracts` itself (never imported ones)."""
    return {
        name: value
        for name, value in vars(contracts).items()
        if isinstance(value, type)
        and getattr(value, "__module__", None) == contracts.__name__
        and predicate(value)
    }


def _is_enum(value: type) -> bool:
    return issubclass(value, enum.Enum)


def _is_value_type(value: type) -> bool:
    return dataclasses.is_dataclass(value)


# --------------------------------------------------------------------------
# Dataclasses
# --------------------------------------------------------------------------


def test_declared_dataclasses_are_exactly_the_documented_ones() -> None:
    declared = set(_declared(_is_value_type))
    documented = set(DOCUMENTED_DATACLASSES)
    assert declared - documented == set(), f"undocumented value types: {sorted(declared - documented)}"
    assert documented - declared == set(), f"missing value types: {sorted(documented - declared)}"


def test_dataclass_field_names_and_order_match_the_document() -> None:
    for name, fields in DOCUMENTED_DATACLASSES.items():
        declared = tuple(f.name for f in dataclasses.fields(getattr(contracts, name)))
        assert declared == tuple(f[0] for f in fields), f"{name} fields differ: {declared}"


def test_dataclass_field_annotations_match_the_document() -> None:
    for name, fields in DOCUMENTED_DATACLASSES.items():
        cls = getattr(contracts, name)
        annotations = {f.name: f.type for f in dataclasses.fields(cls)}
        for field, documented in fields:
            actual = annotations[field]
            assert isinstance(actual, str), f"{name}.{field} annotation was evaluated, not deferred"
            assert _canon(actual) == _canon(documented), (
                f"{name}.{field} is {actual!r}, document says {documented!r}"
            )


def test_every_documented_value_type_is_a_frozen_dataclass() -> None:
    for name in DOCUMENTED_DATACLASSES:
        cls = getattr(contracts, name)
        assert cls.__dataclass_params__.frozen, f"{name} is not frozen"


def test_route_command_is_the_only_defaulted_field_and_defaults_to_none() -> None:
    defaulted = [
        f"{name}.{field.name}"
        for name in DOCUMENTED_DATACLASSES
        for field in dataclasses.fields(getattr(contracts, name))
        if field.default is not dataclasses.MISSING
        or field.default_factory is not dataclasses.MISSING
    ]
    assert defaulted == ["Route.command"], f"unexpected defaults: {defaulted}"
    assert dataclasses.fields(contracts.Route)[-1].default is None


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------


def test_declared_enums_are_exactly_the_documented_ones() -> None:
    declared = set(_declared(_is_enum))
    documented = set(DOCUMENTED_ENUMS)
    assert declared - documented == set(), f"undocumented enums: {sorted(declared - documented)}"
    assert documented - declared == set(), f"missing enums: {sorted(documented - declared)}"


def test_enum_members_values_and_order_match_the_document() -> None:
    for name, members in DOCUMENTED_ENUMS.items():
        cls = getattr(contracts, name)
        assert issubclass(cls, str), f"{name} is not a str enum"
        declared = tuple((member.name, member.value) for member in cls)
        assert declared == members, f"{name} members differ: {declared}"


# --------------------------------------------------------------------------
# §7 record kinds and §4 conclusion sets
# --------------------------------------------------------------------------


def test_entry_kind_literal_carries_the_fourteen_documented_kinds_in_order() -> None:
    assert typing.get_args(contracts.EntryKind) == DOCUMENTED_ENTRY_KINDS
    assert len(DOCUMENTED_ENTRY_KINDS) == 14


def test_entry_kinds_constant_is_the_frozenset_of_those_kinds() -> None:
    assert isinstance(contracts.ENTRY_KINDS, frozenset)
    assert contracts.ENTRY_KINDS == frozenset(DOCUMENTED_ENTRY_KINDS)
    assert _canon(contracts.__annotations__["ENTRY_KINDS"]) == _canon("frozenset[EntryKind]")


def test_check_conclusion_sets_match_the_document() -> None:
    for name, (annotation, members) in DOCUMENTED_CONCLUSION_SETS.items():
        value = getattr(contracts, name)
        assert isinstance(value, frozenset), f"{name} is not a frozenset"
        assert {member.name for member in value} == members, f"{name} differs: {value}"
        assert all(isinstance(member, contracts.CheckConclusion) for member in value)
        assert _canon(contracts.__annotations__[name]) == _canon(annotation)


# --------------------------------------------------------------------------
# §7 protocols, exception and the one documented method body
# --------------------------------------------------------------------------


def test_record_protocols_are_protocols() -> None:
    assert getattr(contracts.RecordWriter, "_is_protocol", False)
    assert getattr(contracts.RecordReader, "_is_protocol", False)


def test_documented_method_signatures_match_the_document() -> None:
    for qualified, (owner, parameters, returns) in DOCUMENTED_METHODS.items():
        method = getattr(getattr(contracts, owner), qualified.split(".")[1])
        signature = inspect.signature(method)
        declared = tuple(signature.parameters)
        assert declared == tuple(p[0] for p in parameters), f"{qualified} parameters: {declared}"
        for parameter, annotation, has_default, default in parameters:
            actual = signature.parameters[parameter]
            assert actual.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD, (
                f"{qualified}.{parameter} is {actual.kind}, the document writes it positionally"
            )
            if annotation is None:
                assert actual.annotation is inspect.Parameter.empty
            else:
                assert _canon(actual.annotation) == _canon(annotation), (
                    f"{qualified}.{parameter} is {actual.annotation!r}"
                )
            if has_default:
                assert actual.default == default, f"{qualified}.{parameter} default"
            else:
                assert actual.default is inspect.Parameter.empty
        assert _canon(signature.return_annotation) == _canon(returns), f"{qualified} return"


def test_append_failed_is_an_exception() -> None:
    assert issubclass(contracts.AppendFailed, Exception)
    try:
        raise contracts.AppendFailed("chain break")
    except contracts.AppendFailed as failure:
        assert str(failure) == "chain break"
    else:  # pragma: no cover - `raise` above always raises
        raise AssertionError("AppendFailed did not propagate")


def test_verified_record_prefix_latest_searches_only_its_own_rows() -> None:
    at = datetime.datetime(2026, 1, 1)
    first = contracts.RecordRow(seq=1, kind="plan", at=at, payload={})
    second = contracts.RecordRow(seq=2, kind="judgement", at=at, payload={})
    third = contracts.RecordRow(seq=3, kind="plan", at=at, payload={"n": 2})
    prefix = contracts.VerifiedRecordPrefix(
        job_id="j", rows=(first, second, third), checked_through_seq=3
    )
    assert prefix.latest("plan") is third
    assert prefix.latest("judgement") is second
    assert prefix.latest("attestation") is None
    assert contracts.VerifiedRecordPrefix(job_id="j", rows=(), checked_through_seq=0).latest("plan") is None

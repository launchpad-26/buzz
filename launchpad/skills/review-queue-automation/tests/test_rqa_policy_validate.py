#!/usr/bin/env python3
"""`rqa.policy.validate` — `code/P-03-policy.md` §8 rows T1-T6 and T18-T21.

No pytest: every `test_*` function here takes no arguments, per `tests/run_all.py`.

Two things these tests deliberately do NOT do:

* They never assert that `rqa.remediation` is absent, and never assert that the
  mechanical tool registry is empty. P-10 (Task #2194) lands that module in a later
  batch, and a test pinned to today's `ImportError` would have to be deleted then.
  Membership is exercised against a *substituted* registry instead, which is the
  behaviour the contract fixes forever: an id in the set validates, an id outside it
  is `TOOL_NOT_IN_SET`.
* They never re-implement a glob matcher to decide which patterns are valid.
  `rqa.protocol.paths.matches` is the only matcher in RQA and its `PathGlobError` is
  the definition of an invalid pattern.
"""

from __future__ import annotations

import contextlib
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import rqa.policy.validate as policy_validate  # noqa: E402
from rqa.contracts import (  # noqa: E402
    Activity,
    Category,
    Route,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.policy.types import ValidatedConfig  # noqa: E402

CODE = ValidationErrorCode


def _config() -> dict:
    """A valid, maximally sparse config: the starter document itself."""
    return policy_validate.starter_config()


def _codes(failure: ValidationFailure) -> list[ValidationErrorCode]:
    return [error.code for error in failure.errors]


def _failure(config: dict) -> ValidationFailure:
    outcome = policy_validate.validate(config)
    assert isinstance(outcome, ValidationFailure), f"expected a ValidationFailure, got {outcome}"
    return outcome


def _validated(config: dict) -> ValidatedConfig:
    outcome = policy_validate.validate(config)
    assert isinstance(outcome, ValidatedConfig), f"expected a ValidatedConfig, got {outcome}"
    return outcome


@contextlib.contextmanager
def _tool_set(registry: dict):
    """Substitute P-10's registry lookup for the duration of one test.

    The lookup point, not the module: `validate()` resolves the registry at call
    time precisely so this substitution is possible whether or not P-10 is present.
    """
    original = policy_validate._mechanical_tool_set
    policy_validate._mechanical_tool_set = lambda: registry
    try:
        yield
    finally:
        policy_validate._mechanical_tool_set = original


# -- T1: an unknown top-level key ---------------------------------------------


def test_t1_unknown_top_level_key_is_one_unknown_key_error_naming_it() -> None:
    config = _config()
    config["webhooks"] = {"url": "https://example.invalid"}
    failure = _failure(config)
    assert _codes(failure) == [CODE.UNKNOWN_KEY]
    assert failure.errors[0].path == "webhooks"
    assert "webhooks" in failure.errors[0].detail


def test_t1_a_sixth_top_level_key_is_rejected_even_when_all_five_are_present() -> None:
    config = _config()
    config["strategies"] = {"active": "shadow"}
    # The legacy estate's `config.strategies.active` was read by nothing, so
    # configured policy was silently ignored. A key this validator accepts is a key
    # it materialises; anything else is UNKNOWN_KEY.
    assert _codes(_failure(config)) == [CODE.UNKNOWN_KEY]


# -- T2: no policy section ----------------------------------------------------


def test_t2_missing_policy_is_exactly_one_error_with_no_deeper_policy_errors() -> None:
    config = _config()
    del config["policy"]
    failure = _failure(config)
    assert _codes(failure) == [CODE.MISSING_POLICY]
    assert failure.errors[0].path == "policy"
    assert [error for error in failure.errors if error.path.startswith("policy.")] == []


def test_a_config_omitting_budget_is_as_invalid_as_one_naming_a_sixth_key() -> None:
    config = _config()
    del config["budget"]
    failure = _failure(config)
    assert _codes(failure) == [CODE.MISSING_REQUIRED_SECTION]
    assert failure.errors[0].path == "budget"


# -- T3: a tool outside MECHANICAL_TOOL_SET -----------------------------------


def test_t3_tool_outside_the_mechanical_tool_set_is_tool_not_in_set_naming_it() -> None:
    config = _config()
    config["policy"]["mechanical"]["tools"] = ["rustfmt"]
    with _tool_set({"ruff": object()}):
        failure = _failure(config)
    assert _codes(failure) == [CODE.TOOL_NOT_IN_SET]
    assert failure.errors[0].path == "policy.mechanical.tools[0]"
    assert "rustfmt" in failure.errors[0].detail


def test_t3_a_tool_inside_the_substituted_set_validates_and_reaches_the_policy() -> None:
    config = _config()
    config["policy"]["mechanical"]["tools"] = ["ruff"]
    with _tool_set({"ruff": object(), "gofmt": object()}):
        validated = _validated(config)
    assert validated.policy.mechanical.tools == frozenset({"ruff"})


def test_tool_membership_is_the_only_thing_read_from_the_registry() -> None:
    """§4: `rqa.policy` tests membership and never reads a `ToolSpec`."""

    class _Probe(dict):
        def __init__(self):
            super().__init__({"ruff": object()})
            self.item_reads = 0

        def __getitem__(self, key):  # pragma: no cover - a read here is the defect
            self.item_reads += 1
            return super().__getitem__(key)

    probe = _Probe()
    config = _config()
    config["policy"]["mechanical"]["tools"] = ["ruff"]
    with _tool_set(probe):
        _validated(config)
    assert probe.item_reads == 0


def test_trusted_archive_skips_registry_membership_and_nothing_else() -> None:
    """M3's mechanism, bounded. The trusted-archive path exists so a pinned read
    cannot fail because P-10's registry changed after the pin; it must not become a
    way to accept a structurally invalid config."""
    tooled = _config()
    tooled["policy"]["mechanical"]["tools"] = ["ruff"]
    with _tool_set({}):
        # A live read of the same bytes is still fail-closed.
        assert isinstance(policy_validate.validate(tooled), ValidationFailure)
        trusted = policy_validate.validate(tooled, trusted_archive=True)
        assert isinstance(trusted, ValidatedConfig)
        assert trusted.policy.mechanical.tools == frozenset({"ruff"})

    for broken, where in (
        ({"webhooks": {}}, "an unknown top-level key"),
        (None, "a missing policy section"),
    ):
        config = _config()
        if broken is None:
            del config["policy"]
        else:
            config.update(broken)
        assert isinstance(
            policy_validate.validate(config, trusted_archive=True), ValidationFailure
        ), where
    miscategorised = _config()
    miscategorised["policy"]["blocking"]["categories"] = ["vibes"]
    assert isinstance(
        policy_validate.validate(miscategorised, trusted_archive=True), ValidationFailure
    )
    unstructured_tool = _config()
    unstructured_tool["policy"]["mechanical"]["tools"] = [""]
    assert isinstance(
        policy_validate.validate(unstructured_tool, trusted_archive=True), ValidationFailure
    )


# -- T4: a seventh authority key ----------------------------------------------


def test_t4_seventh_authority_key_is_unknown_authority_key_naming_it() -> None:
    config = _config()
    config["authority"]["triage"] = True
    failure = _failure(config)
    assert _codes(failure) == [CODE.UNKNOWN_AUTHORITY_KEY]
    assert failure.errors[0].path == "authority.triage"
    assert "triage" in failure.errors[0].detail


def test_an_absent_authority_key_is_false_never_widened() -> None:
    config = _config()
    config["authority"] = {"review": True}
    validated = _validated(config)
    assert validated.authority[Activity.REVIEW] is True
    assert all(
        validated.authority[activity] is False
        for activity in Activity
        if activity is not Activity.REVIEW
    )


def test_a_non_boolean_authority_value_is_bad_type_not_a_truthy_grant() -> None:
    config = _config()
    config["authority"]["merge"] = "yes"
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "authority.merge"


# -- T5, T6: budget axes and error collection ---------------------------------


def test_t5_negative_budget_axis_is_negative_budget_naming_that_axis() -> None:
    config = _config()
    config["budget"]["per_repo_daily_tokens"] = -1
    failure = _failure(config)
    assert _codes(failure) == [CODE.NEGATIVE_BUDGET]
    assert failure.errors[0].path == "budget.per_repo_daily_tokens"


def test_one_omitted_budget_axis_is_uncapped_and_the_others_keep_their_values() -> None:
    """M4, ruled 2026-09-11: each `budget` axis is optional and an omitted axis is
    equivalent to an explicit `null` — no configured ceiling on that axis.
    `CONTRACTS.md` §3 types every axis `int | None`, so "uncapped" is a policy an
    operator can express, not a fallback this validator invents."""
    config = _config()
    config["budget"] = {"per_pr_tokens": 1000, "per_repo_daily_tokens": 20000}
    budget = _validated(config).budget
    assert budget.per_model_daily_tokens is None
    assert budget.per_pr_tokens == 1000
    assert budget.per_repo_daily_tokens == 20000


def test_an_explicit_null_axis_and_an_omitted_axis_agree() -> None:
    omitted = _config()
    del omitted["budget"]["per_pr_tokens"]
    explicit = _config()
    explicit["budget"]["per_pr_tokens"] = None
    assert _validated(omitted).budget == _validated(explicit).budget


def test_t6_every_error_is_collected_never_only_the_first() -> None:
    config = _config()
    config["webhooks"] = {}
    config["budget"]["per_repo_daily_tokens"] = -1
    failure = _failure(config)
    assert set(_codes(failure)) == {CODE.UNKNOWN_KEY, CODE.NEGATIVE_BUDGET}
    paths = {error.path for error in failure.errors}
    assert paths == {"webhooks", "budget.per_repo_daily_tokens"}


def test_t6_errors_from_four_different_sections_arrive_together() -> None:
    config = _config()
    config["authority"]["triage"] = False
    config["policy"]["mechanical"]["tools"] = ["nope"]
    config["budget"]["per_pr_tokens"] = -5
    config["external"]["allowed"] = "true"
    with _tool_set({}):
        failure = _failure(config)
    assert set(_codes(failure)) == {
        CODE.UNKNOWN_AUTHORITY_KEY,
        CODE.TOOL_NOT_IN_SET,
        CODE.NEGATIVE_BUDGET,
        CODE.BAD_TYPE,
    }


def test_a_non_object_config_root_is_bad_type_not_a_crash() -> None:
    failure = _failure(["authority"])
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == ""


def test_validate_carries_the_repo_it_was_given_onto_the_failure() -> None:
    config = _config()
    del config["policy"]
    outcome = policy_validate.validate(config, "owner/name")
    assert isinstance(outcome, ValidationFailure)
    assert outcome.repo == "owner/name"


# -- T18: an obligation path pattern the matcher rejects ----------------------


def test_t18_invalid_path_pattern_is_reported_at_its_indexed_config_path() -> None:
    config = _config()
    config["policy"]["obligations"] = [
        {
            "id": "tests-changed",
            "paths": ["src/**/*.py", "../etc/passwd"],
            "required_for": ["high"],
            "evidence": "a test exercising the change",
        }
    ]
    failure = _failure(config)
    assert _codes(failure) == [CODE.INVALID_PATH_PATTERN]
    assert failure.errors[0].path == "policy.obligations[0].paths[1]"
    # The detail is the matcher's own message, not a message this part invented.
    assert "'..'" in failure.errors[0].detail


def test_a_valid_obligation_survives_into_the_shared_protocol_type() -> None:
    config = _config()
    config["policy"]["obligations"] = [
        {
            "id": "tests-changed",
            "paths": ["src/**/*.py"],
            "required_for": ["high", "medium"],
            "evidence": "a test exercising the change",
        }
    ]
    validated = _validated(config)
    obligation = validated.policy.obligations[0]
    assert obligation.id == "tests-changed"
    assert obligation.paths == ("src/**/*.py",)
    assert obligation.required_for == frozenset({"high", "medium"})


# -- T19, T20, T21: policy.remediation ----------------------------------------


def test_t19_absent_remediation_materialises_to_allow_forks_false() -> None:
    config = _config()
    del config["policy"]["remediation"]
    assert _validated(config).policy.remediation.allow_forks is False


def test_t20_configured_allow_forks_true_is_preserved() -> None:
    config = _config()
    config["policy"]["remediation"]["allow_forks"] = True
    assert _validated(config).policy.remediation.allow_forks is True


def test_t21_non_boolean_allow_forks_is_bad_type_at_the_remediation_path() -> None:
    config = _config()
    config["policy"]["remediation"]["allow_forks"] = "yes"
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "policy.remediation.allow_forks"


def test_t21_an_extra_remediation_key_is_unknown_key_at_the_remediation_path() -> None:
    config = _config()
    config["policy"]["remediation"]["allow_pushes_to_main"] = True
    failure = _failure(config)
    assert _codes(failure) == [CODE.UNKNOWN_KEY]
    assert failure.errors[0].path == "policy.remediation.allow_pushes_to_main"


def test_an_explicit_null_remediation_is_bad_type_not_a_silent_default() -> None:
    """M5: `dict.get` cannot tell an absent key from `"remediation": null`, so
    presence is tested rather than inferred. A present-but-non-object value is
    `BAD_TYPE` here like every other typed field in this validator."""
    config = _config()
    config["policy"]["remediation"] = None
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "policy.remediation"


def test_a_non_object_remediation_is_bad_type_whatever_its_type() -> None:
    for value in (False, 0, "", [], "allow"):
        config = _config()
        config["policy"]["remediation"] = value
        failure = _failure(config)
        assert _codes(failure) == [CODE.BAD_TYPE], value
        assert failure.errors[0].path == "policy.remediation", value


def test_an_explicit_null_optional_leaf_is_bad_type_except_for_a_budget_axis() -> None:
    """The absent-versus-explicit-null distinction, checked across every optional key
    this validator reads. Only a budget axis treats `null` as equivalent to omission,
    and that equivalence is §2's ruled behaviour rather than an oversight."""
    for path, key in (
        (("policy",), "version"),
        (("external",), "allowed"),
        (("external",), "deny_label"),
        (("policy", "remediation"), "allow_forks"),
    ):
        config = _config()
        section = config
        for step in path:
            section = section[step]
        section[key] = None
        failure = _failure(config)
        assert _codes(failure) == [CODE.BAD_TYPE], (path, key)
    for axis in ("per_pr_tokens", "per_repo_daily_tokens", "per_model_daily_tokens"):
        config = _config()
        config["budget"][axis] = None
        assert getattr(_validated(config).budget, axis) is None


# -- the shared boundaries: routes and categories -----------------------------


def test_a_route_missing_family_is_refused_not_defaulted() -> None:
    config = _config()
    config["routes"] = [
        {"harness": "claude", "model": "opus", "provider": "anthropic", "external": False}
    ]
    failure = _failure(config)
    assert _codes(failure) == [CODE.MISSING_REQUIRED_SECTION]
    assert failure.errors[0].path == "routes[0].family"


def test_an_empty_family_string_is_bad_type_not_an_accepted_route() -> None:
    config = _config()
    config["routes"] = [
        {
            "harness": "claude",
            "model": "opus",
            "provider": "anthropic",
            "family": "",
            "external": False,
        }
    ]
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "routes[0].family"


def test_an_operator_declared_command_becomes_route_command_as_a_tuple() -> None:
    config = _config()
    config["routes"] = [
        {
            "harness": "in-house",
            "model": "local",
            "provider": "local",
            "family": "in-house",
            "external": False,
            "command": ["review-harness", "--json"],
        }
    ]
    validated = _validated(config)
    assert validated.routes == (
        Route(
            harness="in-house",
            model="local",
            provider="local",
            family="in-house",
            external=False,
            command=("review-harness", "--json"),
        ),
    )


def test_an_empty_command_list_cannot_name_an_executable() -> None:
    config = _config()
    config["routes"] = [
        {
            "harness": "in-house",
            "model": "local",
            "provider": "local",
            "family": "in-house",
            "external": False,
            "command": [],
        }
    ]
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "routes[0].command"


def test_a_category_name_outside_the_seven_is_bad_type() -> None:
    config = _config()
    config["policy"]["blocking"]["categories"] = ["mechanical", "vibes"]
    failure = _failure(config)
    assert _codes(failure) == [CODE.BAD_TYPE]
    assert failure.errors[0].path == "policy.blocking.categories[1]"


def test_blocking_categories_materialise_as_a_frozenset_of_category() -> None:
    config = _config()
    config["policy"]["blocking"]["categories"] = ["security", "correctness"]
    categories = _validated(config).policy.blocking.categories
    assert categories == frozenset({Category.SECURITY, Category.CORRECTNESS})
    assert all(isinstance(category, Category) for category in categories)


def test_a_missing_blocking_section_is_refused_rather_than_defaulted_to_nothing() -> None:
    config = _config()
    del config["policy"]["blocking"]
    failure = _failure(config)
    assert _codes(failure) == [CODE.MISSING_REQUIRED_SECTION]
    assert failure.errors[0].path == "policy.blocking"


def test_an_absent_policy_version_falls_back_to_the_generators_own_literal() -> None:
    config = _config()
    del config["policy"]["version"]
    assert _validated(config).policy.version == policy_validate.POLICY_VERSION_DEFAULT


# -- the starter document and the validator share one literal source ----------


def test_the_starter_config_validates_with_zero_errors() -> None:
    validated = _validated(policy_validate.starter_config())
    assert all(value is False for value in validated.authority.values())
    assert validated.routes == ()
    assert validated.external.allowed is False
    assert validated.policy.remediation.allow_forks is False
    assert validated.budget == validated.budget.__class__(None, None, None)


def test_starter_config_returns_a_fresh_document_each_call() -> None:
    first = policy_validate.starter_config()
    first["policy"]["version"] = "edited"
    assert policy_validate.starter_config()["policy"]["version"] == (
        policy_validate.POLICY_VERSION_DEFAULT
    )


def test_the_starter_carries_an_inline_policy_because_pinning_is_fail_closed() -> None:
    # A starter without an inline `policy` would leave every job the operator later
    # runs unpinned: `snapshot_for` is fail-closed on a missing policy (§3 step 3).
    assert "policy" in policy_validate.starter_config()
    assert set(policy_validate.starter_config()) == {
        "authority",
        "routes",
        "external",
        "policy",
        "budget",
    }

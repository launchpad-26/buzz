"""Task #2215 — the executable half of the end-to-end lifecycle conformance proof.

WHAT THIS FILE IS, AND IS NOT.

The narrative half of this proof — a recorded run of the composed `rqa` CLI against
real GitHub pull requests, with pasted, redacted output — lives in the skill's
`TESTING.md`. It records what the product *did* on one operator machine on one day.
It needs a network, a credential and macOS, so none of it can live here: this suite
runs in CI on Linux with no credentials, and `tests/conftest.py` replaces
`socket.socket` so that any attempt at egress is an error rather than a slow test.

This file asserts the complement: the parts of PRD #2006's acceptance criteria that
are **contract-permanent** — true of every build of RQA forever, not merely true of
the build measured on 2026-09-14. That distinction is load-bearing. RQA currently
carries three known defects (#2274 the authority gate can never grant, #2272 the
record cannot be appended off macOS, #2273 no validated milestone-event registry),
and a test that pinned any of those — asserting `_configured_repositories()` is
empty, or that `explain` reports `verified: false` — would promote a defect to a
contract and force its own deletion by whoever fixes it. Today's broken state is
*recorded evidence* in `TESTING.md`, dated and commit-pinned. It is not a test.

Nothing here constructs a stand-in for a part of RQA in order to reach a criterion.
Every value checked is read from the product's own published surface.

FALSIFIABILITY. Each criterion below is checked by a module-level `_..._violations`
helper that is pure in its inputs and returns the violations it found. The product's
real values are passed in by the `test_*` function; deliberately perturbed values are
passed in by `test_rqa_conformance_lifecycle_mutation.py`, which asserts that every
helper *does* report a violation when handed a system that does not conform. A
conformance check that cannot fail has proved nothing.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from rqa.contracts import EvidenceState  # noqa: E402
from rqa.judgement.evidence import compute_assurance  # noqa: E402
from rqa.lifecycle.states import DISPOSITION, Disposition, JobStatus  # noqa: E402
from rqa.policy import SqliteSnapshotStore, snapshot_for  # noqa: E402
from rqa.policy.snapshot import config_path  # noqa: E402
from rqa.policy.validate import starter_config  # noqa: E402
from rqa.protocol import PROTOCOL_VERSION, Valid, protocol_hash, validate  # noqa: E402
from rqa.record.explain import DISPOSITION_TABLE, Explanation  # noqa: E402

# --------------------------------------------------------------------------------
# The criteria, as data. Each list is quoted from PRD #2006's normative extract
# (`requirements/prd-2006-normative-extract.md`), never derived from what the code
# happens to expose today — deriving the expectation from the implementation would
# make every one of these checks unfalsifiable.
# --------------------------------------------------------------------------------

#: RQA-FR-016's six operator-facing answers, verbatim from AC08.
FR016_DISPOSITIONS: frozenset[str] = frozenset(
    {
        "being reviewed",
        "blocked",
        "awaiting remediation",
        "awaiting human judgement",
        "review-complete",
        "unable to progress",
    }
)

#: AC05's closed evidence-state vocabulary, verbatim.
AC05_EVIDENCE_STATES: frozenset[str] = frozenset(
    {"verified", "not_verified", "unavailable", "contradictory", "failed", "incomplete", "unknown"}
)

#: AC06's enumerated reconstruction elements, in the criterion's own order: "the exact
#: PR revision, protocol and policy in force, reviewer identity and type, harness,
#: model, provider, evidence examined, findings produced, decision basis and
#: disposition".
AC06_RECONSTRUCTION_ELEMENTS: tuple[str, ...] = (
    "pr_revision",
    "protocol_hash",
    "policy_version",
    "reviewer_identity",
    "reviewer_type",
    "harness",
    "model",
    "provider",
    "evidence",
    "findings",
    "decision_basis",
    "disposition",
)

#: AC06 reconstructs "for any authoritative review outcome". An outcome whose record
#: could not be authenticated is not authoritative, so a reconstruction that cannot
#: say whether it was authenticated cannot honour the criterion: the disclosure is
#: part of the answer, not decoration.
TRUST_DISCLOSURE_FIELDS: tuple[str, ...] = ("verified", "hmac_checked", "unverifiable", "legacy")


# --------------------------------------------------------------------------------
# AC08 — one command returns a disposition from the closed FR-016 vocabulary.
# --------------------------------------------------------------------------------


def _disposition_vocabulary_violations(
    *, declared: frozenset[str], mapping: dict[str, str]
) -> list[str]:
    """AC08: the answer comes from a closed six-value vocabulary, and every internal
    state `status()` can return has an answer in it.

    Two failure modes, both reported: a declared vocabulary that is not exactly the
    six, and a mapped answer outside it. The second is the one that bites — a new
    internal state whose operator-facing answer was invented rather than mapped.
    """
    violations: list[str] = []
    if declared != FR016_DISPOSITIONS:
        violations.append(
            f"declared vocabulary is not FR-016's six: "
            f"extra={sorted(declared - FR016_DISPOSITIONS)} "
            f"missing={sorted(FR016_DISPOSITIONS - declared)}"
        )
    for state, answer in sorted(mapping.items()):
        if answer not in FR016_DISPOSITIONS:
            violations.append(f"internal state {state!r} answers {answer!r}, outside FR-016")
    return violations


def test_ac08_status_answers_from_the_closed_fr016_vocabulary() -> None:
    violations = _disposition_vocabulary_violations(
        declared=frozenset(member.value for member in Disposition),
        mapping={status.value: answer.value for status, answer in DISPOSITION.items()},
    )
    assert violations == [], violations


def _disposition_drift(*, canonical: dict[str, str], reconstructed: dict[str, str]) -> list[str]:
    """AC08 read together with AC06: `status` and `explain` are two commands that
    answer the same question about the same job, from two different tables.

    `rqa status` renders `rqa.lifecycle.states.DISPOSITION`; `rqa explain` renders
    `rqa.record.explain.DISPOSITION_TABLE`. Nothing in the type system ties them
    together, so they can drift apart silently and hand an operator two different
    answers for one outcome. Every state the canonical table maps must get the same
    answer from the reconstruction table.

    A state the reconstruction table carries and the canonical one does not is not a
    violation: `superseded` is deliberately outside FR-016 (a superseded job is never
    the one the disposition command answers for) and `explain` renders its raw name
    rather than forcing it into one of the six.
    """
    return [
        f"{state!r}: status says {answer!r}, explain says {reconstructed.get(state)!r}"
        for state, answer in sorted(canonical.items())
        if reconstructed.get(state) != answer
    ]


def test_ac08_status_and_explain_never_disagree_about_a_disposition() -> None:
    drift = _disposition_drift(
        canonical={status.value: answer.value for status, answer in DISPOSITION.items()},
        reconstructed=dict(DISPOSITION_TABLE),
    )
    assert drift == [], drift


# --------------------------------------------------------------------------------
# AC06 — one command reconstructs the whole outcome.
# --------------------------------------------------------------------------------


def _missing_reconstruction_elements(*, fields: frozenset[str]) -> list[str]:
    """AC06 enumerates what a reconstruction must name. Each element must be a field
    of the reconstruction the command returns — an element the type cannot carry can
    never be reported, whatever the record happens to contain."""
    return [element for element in AC06_RECONSTRUCTION_ELEMENTS if element not in fields]


def test_ac06_reconstruction_names_every_element_the_criterion_enumerates() -> None:
    fields = frozenset(field.name for field in dataclasses.fields(Explanation))
    missing = _missing_reconstruction_elements(fields=fields)
    assert missing == [], missing


def _missing_trust_disclosure(*, fields: frozenset[str]) -> list[str]:
    """A reconstruction that silently asserts trust it has not established is worse
    than one that refuses: it launders an unauthenticated record into an
    authoritative-looking answer. The reconstruction must be able to say so."""
    return [name for name in TRUST_DISCLOSURE_FIELDS if name not in fields]


def test_ac06_reconstruction_can_report_unverifiability_rather_than_assume_trust() -> None:
    fields = frozenset(field.name for field in dataclasses.fields(Explanation))
    missing = _missing_trust_disclosure(fields=fields)
    assert missing == [], missing


# --------------------------------------------------------------------------------
# AC05 / AC14 — fail-closed: no successful outcome while an obligation is unsatisfied.
# --------------------------------------------------------------------------------


def _evidence_vocabulary_violations(*, declared: frozenset[str]) -> list[str]:
    if declared == AC05_EVIDENCE_STATES:
        return []
    return [
        f"evidence vocabulary is not AC05's seven: "
        f"extra={sorted(declared - AC05_EVIDENCE_STATES)} "
        f"missing={sorted(AC05_EVIDENCE_STATES - declared)}"
    ]


def test_ac05_every_obligation_carries_a_state_from_the_closed_seven() -> None:
    violations = _evidence_vocabulary_violations(
        declared=frozenset(member.value for member in EvidenceState)
    )
    assert violations == [], violations


def _fail_closed_violations(*, assurance_of) -> list[str]:
    """AC05/AC14's core, and the single property this whole programme most needs to
    hold: "no successful disposition can be produced while any required obligation is
    unsatisfied".

    Expressed against the calculation the disposition rule consumes. For a policy
    demanding assurance (`required >= 1`) over a universe in which one obligation is
    unsatisfied, the achieved assurance must fall short of the required — that
    shortfall is what raises the evidence gap that forbids `approve`. `verified` is
    included as the control: a fully satisfied universe must *not* fall short, or the
    check would be trivially true and would pass against a system that always refuses.
    """
    violations: list[str] = []
    for member in EvidenceState:
        satisfied = member is EvidenceState.VERIFIED
        result = assurance_of(states={"O-1": member}, required=1)
        short = result.achieved < result.required
        if satisfied and short:
            violations.append(
                f"a fully satisfied universe ({member.value}) fell short: "
                f"{result.achieved}/{result.required}"
            )
        if not satisfied and not short:
            violations.append(
                f"unsatisfied obligation state {member.value!r} still reached full assurance "
                f"{result.achieved}/{result.required}: a successful disposition is producible"
            )
    return violations


def test_ac05_an_unsatisfied_obligation_cannot_reach_full_assurance() -> None:
    violations = _fail_closed_violations(assurance_of=compute_assurance)
    assert violations == [], violations


def test_ac05_a_partly_unsatisfied_universe_falls_short_of_a_higher_bar() -> None:
    """The same property at a bar above one: three obligations, one unverified,
    against a policy requiring three. Guards the floor() arithmetic rather than only
    the single-obligation case."""
    mixed = {
        "O-1": EvidenceState.VERIFIED,
        "O-2": EvidenceState.VERIFIED,
        "O-3": EvidenceState.NOT_VERIFIED,
    }
    result = compute_assurance(states=mixed, required=3)
    assert result.achieved < result.required, result
    whole = dict.fromkeys(mixed, EvidenceState.VERIFIED)
    assert compute_assurance(states=whole, required=3).achieved == 3


# --------------------------------------------------------------------------------
# AC02 — a policy edit takes effect on the next review, with no rebuild.
# --------------------------------------------------------------------------------


def _policy_reread_violations(*, first: str, second: str, third: str) -> list[str]:
    """AC02's mechanism: "a policy change takes effect on the next review with no
    rebuild, reinstall or redeploy".

    Three reads of one repository's policy within one live process and one unchanged
    import of `rqa`: before an edit, after it, and again after reverting it. The
    middle read must differ (the edit reached the running system) and the third must
    return to the first (the identity is a pure function of the file's content, not a
    monotonic counter or a cache that merely missed). Anything caching the config
    across calls fails the second; anything deriving identity from time or call order
    fails the third.
    """
    violations: list[str] = []
    if first == second:
        violations.append(
            f"an edited policy produced the identical pin {first[:16]}…: the running "
            "system did not observe the edit without a restart"
        )
    if third != first:
        violations.append(
            f"reverting the edit produced {third[:16]}…, not the original {first[:16]}…: "
            "the pin is not a pure function of the configuration's content"
        )
    return violations


def _write_blocking(path: pathlib.Path, config: dict, blocking: dict) -> None:
    config["policy"]["blocking"] = blocking
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def test_ac02_a_policy_edit_is_observed_without_a_rebuild_or_restart() -> None:
    original = {"categories": ["correctness"], "severities": ["high"], "corroboration": 1}
    edited = {"categories": ["correctness", "security"], "severities": ["high"], "corroboration": 2}
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        repo = str(root / "owner" / "name")
        path = config_path(repo)
        path.parent.mkdir(parents=True)
        store = SqliteSnapshotStore(root / "state")
        config = starter_config()

        _write_blocking(path, config, original)
        first = snapshot_for(repo=repo, job=None, store=store, record=None)
        _write_blocking(path, config, edited)
        second = snapshot_for(repo=repo, job=None, store=store, record=None)
        _write_blocking(path, config, original)
        third = snapshot_for(repo=repo, job=None, store=store, record=None)

        for label, snapshot in (("first", first), ("second", second), ("third", third)):
            assert hasattr(snapshot, "hash"), f"{label} read did not validate: {snapshot!r}"
        violations = _policy_reread_violations(
            first=first.hash, second=second.hash, third=third.hash
        )
        assert violations == [], violations
        assert second.policy.blocking.corroboration == 2, second.policy.blocking


# --------------------------------------------------------------------------------
# AC01 / AC17 — one published protocol, invariant under the route that produced it.
# --------------------------------------------------------------------------------


def _protocol_invariance_violations(*, pins: dict[str, str]) -> list[str]:
    """AC17: "removing that provider from configuration leaves RQA's review protocol
    and semantics unchanged", and AC01's "one published protocol definition".

    Every configuration, whatever providers it names, must pin the same protocol. A
    protocol identity that moved when a provider was added or removed would mean the
    definition a verdict validates against is a function of who produced the verdict —
    which is exactly what AC01's single published definition forbids.
    """
    distinct = sorted(set(pins.values()))
    if len(distinct) <= 1:
        return []
    return [
        f"provider configuration changed the protocol pin: "
        + ", ".join(f"{name}={pin[:16]}…" for name, pin in sorted(pins.items()))
    ]


def _snapshot_with_routes(root: pathlib.Path, name: str, routes: list, external: dict):
    repo = str(root / name)
    path = config_path(repo)
    path.parent.mkdir(parents=True)
    config = starter_config()
    config["routes"] = routes
    config["external"] = external
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    return snapshot_for(repo=repo, job=None, store=SqliteSnapshotStore(root / name / "state"),
                        record=None)


def test_ac17_removing_a_provider_leaves_the_protocol_unchanged() -> None:
    free_route = {
        "harness": "custom",
        "model": "local-review-model",
        "provider": "local",
        "family": "local",
        "external": False,
        "command": ["local-review-cli"],
    }
    paid_route = {
        "harness": "claude",
        "model": "claude-sonnet-4-5",
        "provider": "anthropic",
        "family": "claude",
        "external": True,
    }
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        enabled = _snapshot_with_routes(
            root, "with-provider", [paid_route, free_route],
            {"allowed": True, "deny_label": "no-external-review"},
        )
        removed = _snapshot_with_routes(
            root, "without-provider", [free_route], {"allowed": False, "deny_label": ""}
        )
        # The configurations really did differ, or the invariance below is vacuous.
        assert enabled.hash != removed.hash, "the two configurations were identical"
        assert [route.provider for route in enabled.routes] == ["anthropic", "local"]
        assert [route.provider for route in removed.routes] == ["local"]

        violations = _protocol_invariance_violations(
            pins={"provider-enabled": enabled.protocol_hash, "provider-removed": removed.protocol_hash}
        )
        assert violations == [], violations
        assert enabled.protocol_hash == protocol_hash()


def _concept_semantics(result) -> tuple:
    """The concept-level content of a verdict, with the route that produced it
    deliberately excluded: the obligation ids and their states, and each finding's id,
    categories, severity and behaviour-changing flag."""
    verdict = result.verdict
    return (
        verdict.protocol_version,
        tuple(sorted((name, state.value) for name, state in verdict.obligations.items())),
        tuple(
            sorted(
                (
                    finding.id,
                    tuple(sorted(category.value for category in finding.categories)),
                    finding.severity,
                    finding.behaviour_changing,
                )
                for finding in verdict.findings
            )
        ),
    )


def _semantic_divergence(*, left: tuple, right: tuple) -> list[str]:
    """AC01: "two reviews of the same PR by different harnesses, models or providers
    carry the same concept semantics". The same reported content, routed through two
    different harness/model/provider identities, must reduce to the same concepts —
    the protocol definition is one definition, not one per route."""
    if left == right:
        return []
    return [f"two routes produced divergent concept semantics: {left!r} != {right!r}"]


def _validated_under(identity: dict, directory: str, attempt_id: str):
    payload = {
        "protocol_version": PROTOCOL_VERSION,
        "identity": identity,
        "obligations": {
            "O-security": {"state": "verified", "findings": []},
            "O-correctness": {"state": "not_verified", "findings": ["f1"]},
        },
        "findings": [
            {
                "id": "f1",
                "categories": ["correctness"],
                "extra_tags": [],
                "location": {"path": "src/main.py", "line": 12},
                "evidence": "The added branch is unreachable.",
                "severity": "high",
                "remedy": None,
                "behaviour_changing": True,
                "source_attempt": "untrusted-harness-value",
            }
        ],
        "injection_attempts": [],
    }
    path = pathlib.Path(directory) / f"{attempt_id}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return validate(path=path, attempt_id=attempt_id)


def test_ac01_two_routes_reporting_the_same_review_carry_the_same_semantics() -> None:
    with tempfile.TemporaryDirectory() as directory:
        first = _validated_under(
            {"harness": "claude", "model": "claude-sonnet-4-5", "provider": "anthropic"},
            directory,
            "attempt-anthropic",
        )
        second = _validated_under(
            {"harness": "custom", "model": "local-review-model", "provider": "local"},
            directory,
            "attempt-local",
        )
        assert isinstance(first, Valid), getattr(first, "reasons", first)
        assert isinstance(second, Valid), getattr(second, "reasons", second)
        # The routes genuinely differed — otherwise the equality below proves nothing.
        assert first.verdict.identity != second.verdict.identity
        divergence = _semantic_divergence(
            left=_concept_semantics(first), right=_concept_semantics(second)
        )
        assert divergence == [], divergence


def test_ac01_exactly_one_protocol_definition_is_published() -> None:
    """AC01 validates every verdict against "one published protocol definition". Two
    packaged schemas would mean two definitions and a dispatch decision nobody made."""
    packaged = sorted(
        path.name
        for path in (pathlib.Path(__file__).resolve().parent.parent / "rqa" / "protocol" / "schema")
        .glob("verdict-*.json")
    )
    assert packaged == [f"verdict-{PROTOCOL_VERSION}.json"], packaged

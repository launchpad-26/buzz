"""Risk classification and deterministic plan selection — `code/P-06-harness-interface.md` §3.1.

`plan()` is total and deterministic for its inputs: the same `facts`, `snapshot` and
`carry` produce the identical `Plan` and the identical `plan` record payload, on any
machine, at any time. Nothing here reads a clock, the environment, a file, `random` or
`uuid`, and nothing here calls a model. That is U-DISPATCH-24's determinism property
carried as-is — "a model-derived or environment-derived plan cannot be replayed, so two
reviews of the same change cannot be compared" — and U-DISPATCH-24's second property,
symmetry of the record, is `Plan.omitted`: every non-carried policy obligation appears
exactly once in `obligations` or in `omitted`, each omission carrying its own reason, so
the record can show a reader that a question was deliberately not asked.

**Strategy comes from the policy's stated assurance and nothing else** (U-POLICY-08's
rework, U-DOCS-21's and U-DOCS-36's). The incumbent selector walked twelve named
strategies from the review's own internal signals — specialist need, prior disagreement,
complexity — which is precisely the input set RQA-FR-019 says cannot establish
proportionality, because none of it is the policy's assurance statement. Here
`snapshot.policy.assurance` is the *only* input to strategy and participant count, so
"no more costly than required" is decidable from the pinned snapshot alone. The three
named strategies replace the registry of twelve: the registry's fine grain was never
observable in a `PanelResult`, and a selector with one input does not need twelve
outputs.

**One selector, one answer** — U-POLICY-08's most easily lost property. P-05's
`reserve()` prices an attempt from `plan.participants` (`rqa/supply/budget.py`), and the
panel loop counts distinct provider families to the same `plan.participants`. Both read
the one `Plan` this module returns and P-02 pins, so a job cannot be reserved against one
strategy and executed under another.

Every path comparison in this module is `rqa.protocol.paths.matches()` (P-04). §7 admits
no other matcher, and none is imported here: no `fnmatch`, no `PurePath.match`, no regex.
A `changed_paths` member outside P-04's normalized grammar raises `PathGlobError` out of
`plan()` rather than being skipped — silently dropping an unparseable path would
under-classify risk, and a security class that quietly fails to match is the one failure
mode this classification exists to prevent.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

from rqa.contracts import Plan
from rqa.protocol.paths import matches

if TYPE_CHECKING:  # annotation-only; resolved by type checkers, never at import
    from rqa.contracts import CarryOver, Facts, Job, Obligation, RecordWriter, Snapshot

__all__ = [
    "BASELINE_RISK_CLASS",
    "RISK_CLASSES",
    "RISK_PATTERNS",
    "STRATEGIES",
    "Strategy",
    "matched_classes",
    "plan",
    "selection",
]

#: §2, verbatim. Order is meaning, not presentation: "the first matching class is the
#: recorded class", so the tuple reads most-consequential first.
RISK_CLASSES: tuple[str, ...] = ("security", "migration", "infrastructure", "standard")

#: The class every review is in. It is not pattern-matched: a review whose changed-path
#: set is empty, or whose paths match none of the three specific classes, is still a
#: review, and `RISK_CLASSES` has to be total for `Plan.risk_class` to be total.
BASELINE_RISK_CLASS = "standard"

#: PathGlob patterns per specific risk class, matched only by P-04 `matches()`.
#: Deliberately broad, in U-DISPATCH-24's own terms: a false positive costs one extra
#: obligation, a false negative skips it entirely.
RISK_PATTERNS: Mapping[str, tuple[str, ...]] = {
    "security": (
        "**/auth/**",
        "**/authz/**",
        "**/security/**",
        "**/*auth*",
        "**/*secret*",
        "**/*credential*",
        "**/*token*",
        "**/*password*",
        "**/*.pem",
        "**/*.key",
    ),
    "migration": (
        "**/migrations/**",
        "**/migrate/**",
        "**/*migration*",
        "**/*.sql",
        "**/schema/**",
    ),
    "infrastructure": (
        ".github/**",
        "**/Dockerfile",
        "**/docker-compose*.yml",
        "**/docker-compose*.yaml",
        "**/*.tf",
        "**/helm/**",
        "**/k8s/**",
        "**/kubernetes/**",
        "**/Makefile",
        "**/justfile",
        "**/*.nomad",
    ),
}

#: The two classes whose review, at three or more participants, is a
#: `challenge_and_verify` rather than an `independent_panel` (§3.1).
ADVERSARIAL_RISK_CLASSES = frozenset({"security", "migration"})


@dataclass(frozen=True)
class Strategy:
    """A named strategy's fixed minimum participant count and requested effort (§2)."""

    name: str
    minimum_participants: int
    effort: str


#: §2: `STRATEGIES` maps the three names to their fixed minimum participant counts and
#: requested effort. The efforts are *requested*; what a transport can actually enforce
#: is the adapter's answer (`adapters.resolved_effort`), and the attestation records the
#: enforced one — U-DISPATCH-25's effort honesty.
STRATEGIES: Mapping[str, Strategy] = {
    "single_pass": Strategy(name="single_pass", minimum_participants=1, effort="medium"),
    "independent_panel": Strategy(name="independent_panel", minimum_participants=2, effort="high"),
    "challenge_and_verify": Strategy(name="challenge_and_verify", minimum_participants=3, effort="xhigh"),
}

#: §3.1: "A missing assurance entry falls back only to the snapshot's `standard` value,
#: then to one." One, never zero: a review with no participant is not a review, so a
#: configured zero is read as this floor rather than as a strategy with no invocation.
MINIMUM_PARTICIPANTS = 1

#: `Plan.omitted` reasons. Fixed prefixes so a reader — and a test — can tell the two
#: deterministic omission causes apart without parsing prose.
CARRIED_REASON = "carried"
RISK_REASON_PREFIX = "risk_class_not_required:"
PATH_REASON = "no_changed_path_matches"


def matched_classes(*, changed_paths: frozenset[str]) -> tuple[str, ...]:
    """The risk classes `changed_paths` matches, in `RISK_CLASSES` order.

    Always contains `BASELINE_RISK_CLASS`, so the result is never empty and
    `matched[0]` is always a defined recorded class.
    """
    ordered = sorted(changed_paths)
    matched: list[str] = []
    for risk_class in RISK_CLASSES:
        if risk_class == BASELINE_RISK_CLASS:
            matched.append(risk_class)
            continue
        patterns = RISK_PATTERNS[risk_class]
        if any(matches(path, pattern) for path in ordered for pattern in patterns):
            matched.append(risk_class)
    return tuple(matched)


def _required_assurance(*, assurance: Mapping[str, int], risk_class: str) -> int:
    """One class's required participant count: its own entry, else `standard`, else one."""
    for key in (risk_class, BASELINE_RISK_CLASS):
        value = assurance.get(key)
        if value is not None:
            return max(MINIMUM_PARTICIPANTS, int(value))
    return MINIMUM_PARTICIPANTS


def selection(*, changed_paths: frozenset[str], assurance: Mapping[str, int]) -> tuple[str, str, int]:
    """`(risk_class, strategy, participants)` from the changed paths and stated assurance.

    §3.1, clause by clause: the maximum required assurance across all matched classes is
    the participant count; `single_pass` for one participant; `challenge_and_verify` for a
    security or migration review requiring at least three; `independent_panel` otherwise.
    Because `RISK_CLASSES` is ordered most-consequential first, "the first matching class"
    is `security` or `migration` exactly when one of them matched at all, so the recorded
    class is the right thing to test the adversarial condition against.
    """
    matched = matched_classes(changed_paths=changed_paths)
    risk_class = matched[0]
    participants = max(
        _required_assurance(assurance=assurance, risk_class=candidate) for candidate in matched
    )
    if participants == 1:
        strategy = "single_pass"
    elif participants >= 3 and risk_class in ADVERSARIAL_RISK_CLASSES:
        strategy = "challenge_and_verify"
    else:
        strategy = "independent_panel"
    return risk_class, strategy, participants


def _omission(
    *,
    obligation: Obligation,
    reused: frozenset[str],
    matched: tuple[str, ...],
    changed_paths: frozenset[str],
) -> str | None:
    """This obligation's omission reason, or `None` when it is planned.

    §3.1's four steps, in order and mutually exclusive: carried first, so a carried
    obligation is never planned whatever else is true of it; then the risk-class test;
    then the path test, which applies only to an obligation that states patterns.
    """
    if obligation.id in reused:
        return CARRIED_REASON
    if not (set(obligation.required_for) & set(matched)):
        return RISK_REASON_PREFIX + ",".join(matched)
    if obligation.paths and not any(
        matches(path, pattern) for path in sorted(changed_paths) for pattern in obligation.paths
    ):
        return PATH_REASON
    return None


def plan(*, job: Job, facts: Facts, snapshot: Snapshot, carry: CarryOver, record: RecordWriter) -> Plan:
    """E-07, verbatim from `CONTRACTS.md` §9. §3.1, in order.

    Appends the whole `Plan` as a `plan` entry and returns it. `AppendFailed` propagates:
    a plan whose durable record does not hold it is not a plan anything may be reserved
    or executed against.
    """
    risk_class, strategy, participants = selection(
        changed_paths=facts.changed_paths, assurance=snapshot.policy.assurance
    )
    matched = matched_classes(changed_paths=facts.changed_paths)
    reused = frozenset(carried.obligation_id for carried in carry.reused)

    obligations: list[str] = []
    omitted: dict[str, str] = {}
    for obligation in snapshot.policy.obligations:
        reason = _omission(
            obligation=obligation,
            reused=reused,
            matched=matched,
            changed_paths=facts.changed_paths,
        )
        if reason is None:
            obligations.append(obligation.id)
        else:
            omitted[obligation.id] = reason

    planned = Plan(
        obligations=tuple(obligations),
        omitted=omitted,
        strategy=strategy,
        participants=participants,
        risk_class=risk_class,
        head_sha=job.head_sha,
        snapshot_hash=snapshot.hash,
        protocol_hash=snapshot.protocol_hash,
        policy_version=snapshot.policy.version,
    )
    # §3.1, verbatim: "P-06 appends `asdict(plan)` as `plan` and returns it". The whole
    # `Plan`, field for field, so the record carries the pins as well as the selection.
    record.append(job.id, "plan", asdict(planned))
    return planned

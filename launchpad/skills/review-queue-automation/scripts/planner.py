"""Deterministic review planner for review-queue-automation.

Decides WHICH review activities a pull request requires, and records why. This is
orthogonal to `strategies.py`, which describes HOW participants are composed
(direct, adversarial, panel, ...); an activity is the question being asked.

Every selection is derived from observable PR facts, never from model judgement,
so the plan is reproducible and auditable. Selection reasons are recorded for
both included AND omitted activities: a review that quietly skipped the security
question is indistinguishable from one that asked it and found nothing, unless
the omission is written down.

The plan is consumed by the reviewer prompt, so a selected activity actually
changes what the reviewer is asked to establish.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ---- activities -----------------------------------------------------------
DECOMPOSE = "decompose"
VALIDATE_INTENT = "validate_intent"
FALSIFY_CORRECTNESS = "falsify_correctness"
VERIFY_EVIDENCE = "verify_evidence"
INVESTIGATE_HYPOTHESIS = "investigate_hypothesis"
RED_TEAM_SECURITY = "red_team_security"
PREMORTEM_RELIABILITY = "premortem_reliability"
CHECK_COMPATIBILITY = "check_compatibility"
DEBATE_ARCHITECTURE = "debate_architecture"
JUDGE_FINDINGS = "judge_findings"
REFINE_REMEDIATION = "refine_remediation"
REGRESSION_REREVIEW = "regression_rereview"


@dataclass(frozen=True)
class Activity:
    name: str
    #: What the reviewer must establish. Injected into the prompt verbatim.
    question: str
    #: True when this runs on every review regardless of change shape.
    baseline: bool = False


ACTIVITIES: tuple[Activity, ...] = (
    Activity(DECOMPOSE,
             "Identify what this change actually does, component by component.",
             baseline=True),
    Activity(VALIDATE_INTENT,
             "State whether the change accomplishes what its description and any "
             "linked issue claim, and name any gap.",
             baseline=True),
    Activity(FALSIFY_CORRECTNESS,
             "Actively try to find an input, ordering, or state under which this "
             "change is wrong. Report a defect only with evidence.",
             baseline=True),
    Activity(VERIFY_EVIDENCE,
             "Check the supplied evidence supports the claims made: do the cited "
             "tests and checks actually exercise the changed behaviour?",
             baseline=True),
    Activity(JUDGE_FINDINGS,
             "For every candidate defect, decide whether the evidence is sufficient "
             "to call it a defect, and drop the ones that are not.",
             baseline=True),
    Activity(RED_TEAM_SECURITY,
             "Attack this change: authentication, authorization, secrets handling, "
             "injection, and privilege boundaries."),
    Activity(CHECK_COMPATIBILITY,
             "Determine whether this change breaks an existing contract: API shape, "
             "schema, migration ordering, or dependency expectations."),
    Activity(PREMORTEM_RELIABILITY,
             "Assume this change is deployed and something fails. Name the most "
             "likely failure mode and whether the change makes it more likely."),
    Activity(DEBATE_ARCHITECTURE,
             "Assess whether this change fits the system's existing structure, and "
             "state the strongest argument against its approach."),
    Activity(INVESTIGATE_HYPOTHESIS,
             "A check is failing or the cause is unclear. Establish the cause from "
             "evidence before judging the change."),
    Activity(REGRESSION_REREVIEW,
             "This revision follows an earlier reviewed one. Establish whether the "
             "previously raised concerns are addressed and nothing new regressed."),
    Activity(REFINE_REMEDIATION,
             "A verified blocking defect exists. Describe the smallest correct fix "
             "without widening scope."),
)

ACTIVITY_BY_NAME: dict[str, Activity] = {a.name: a for a in ACTIVITIES}
BASELINE = tuple(a.name for a in ACTIVITIES if a.baseline)


# ---- change classification ------------------------------------------------
#: Path patterns that imply a specific review question. Deliberately broad: a
#: false positive costs one extra question, a false negative skips it entirely.
CHANGE_CLASSES: dict[str, re.Pattern[str]] = {
    "security": re.compile(
        r"(^|/)(security|auth|authentication|authorization|credentials?|secrets?|crypto)(/|\.|$)",
        re.IGNORECASE),
    "contract": re.compile(
        r"(^|/)(migrations?|schema|proto|openapi|graphql)(/|\.|$)"
        r"|\.(sql|prisma|graphql|proto)$",
        re.IGNORECASE),
    "dependency": re.compile(
        r"(^|/)(package\.json|pnpm-lock\.yaml|package-lock\.json|Cargo\.toml|"
        r"Cargo\.lock|go\.mod|go\.sum|requirements[^/]*\.txt|pyproject\.toml|"
        r"Gemfile(\.lock)?)$",
        re.IGNORECASE),
    "infrastructure": re.compile(
        r"(^|/)(deploy|provisioning|terraform|helm|charts|k8s|kubernetes|ansible)(/|$)"
        r"|(^|/)Dockerfile|\.(tf|tfvars)$",
        re.IGNORECASE),
    "ci": re.compile(r"(^|/)\.github/workflows/|(^|/)(Jenkinsfile|\.gitlab-ci\.yml)$",
                     re.IGNORECASE),
    "concurrency": re.compile(
        r"(^|/)(queue|worker|scheduler|lock|mutex|async|concurrent|thread)",
        re.IGNORECASE),
    "docs": re.compile(r"\.(md|mdx|rst|txt|adoc)$|(^|/)docs?/", re.IGNORECASE),
    "tests": re.compile(r"(^|/)(tests?|spec|__tests__)/|(_test|\.test|\.spec)\.",
                        re.IGNORECASE),
}

#: Classes whose files are not product code; a change made only of these is
#: mechanically narrower and does not need the deep code questions.
NON_CODE_CLASSES = frozenset({"docs", "tests"})


def classify_changes(files: list[str]) -> dict[str, list[str]]:
    """Group changed paths by the review question they imply."""
    grouped: dict[str, list[str]] = {}
    for path in files or []:
        text = str(path)
        for name, pattern in CHANGE_CLASSES.items():
            if pattern.search(text):
                grouped.setdefault(name, []).append(text)
    return grouped


@dataclass
class ReviewPlan:
    activities: list[str] = field(default_factory=list)
    reasons: dict[str, list[str]] = field(default_factory=dict)
    omitted: dict[str, str] = field(default_factory=dict)
    change_classes: dict[str, list[str]] = field(default_factory=dict)
    head_sha: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "activities": list(self.activities),
            "reasons": {k: list(v) for k, v in self.reasons.items()},
            "omitted": dict(self.omitted),
            "change_classes": {k: list(v)[:20] for k, v in self.change_classes.items()},
            "head_sha": self.head_sha,
        }

    def questions(self) -> list[tuple[str, str]]:
        return [(name, ACTIVITY_BY_NAME[name].question)
                for name in self.activities if name in ACTIVITY_BY_NAME]


def plan_review(
    *,
    files: list[str] | None = None,
    additions: int = 0,
    deletions: int = 0,
    large_diff_lines: int = 700,
    checks_failing: bool = False,
    is_rereview: bool = False,
    prior_disagreement: bool = False,
    verified_blocker: bool = False,
    head_sha: str = "",
) -> ReviewPlan:
    """Select the review activities this change requires.

    Deterministic: identical inputs always produce an identical plan, and every
    activity is either selected with a reason or omitted with one.
    """
    files = list(files or [])
    grouped = classify_changes(files)
    plan = ReviewPlan(change_classes=grouped, head_sha=head_sha)

    def select(name: str, reason: str) -> None:
        if name not in plan.activities:
            plan.activities.append(name)
        plan.reasons.setdefault(name, []).append(reason)

    code_paths = [
        f for f in files
        if not any(f in grouped.get(cls, []) for cls in NON_CODE_CLASSES)
    ]
    docs_or_tests_only = bool(files) and not code_paths

    for name in BASELINE:
        # A docs/tests-only change still gets intent and evidence checks, but the
        # deep correctness questions would be noise.
        if docs_or_tests_only and name in (FALSIFY_CORRECTNESS, DECOMPOSE):
            plan.omitted[name] = "change touches only documentation and tests"
            continue
        select(name, "baseline activity for every review")

    if "security" in grouped:
        select(RED_TEAM_SECURITY, f"security-sensitive paths changed: {len(grouped['security'])}")
    else:
        plan.omitted[RED_TEAM_SECURITY] = "no security-sensitive path changed"

    contract_reasons = [cls for cls in ("contract", "dependency") if cls in grouped]
    if contract_reasons:
        select(CHECK_COMPATIBILITY, f"contract-bearing changes: {', '.join(contract_reasons)}")
    else:
        plan.omitted[CHECK_COMPATIBILITY] = "no schema, migration or dependency change"

    reliability_reasons = [cls for cls in ("infrastructure", "ci", "concurrency")
                           if cls in grouped]
    if reliability_reasons:
        select(PREMORTEM_RELIABILITY,
               f"operational surface changed: {', '.join(reliability_reasons)}")
    else:
        plan.omitted[PREMORTEM_RELIABILITY] = "no infrastructure, CI or concurrency change"

    total = int(additions) + int(deletions)
    if total > large_diff_lines:
        select(DEBATE_ARCHITECTURE,
               f"change is large: {total} lines exceeds {large_diff_lines}")
    elif len(code_paths) >= 15:
        select(DEBATE_ARCHITECTURE,
               f"change is broad: {len(code_paths)} code files")
    else:
        plan.omitted[DEBATE_ARCHITECTURE] = "change is neither large nor broad"

    if checks_failing:
        select(INVESTIGATE_HYPOTHESIS, "a required check is failing")
    else:
        plan.omitted[INVESTIGATE_HYPOTHESIS] = "no failing check to explain"

    if is_rereview:
        select(REGRESSION_REREVIEW, "a previous revision of this PR was reviewed")
    else:
        plan.omitted[REGRESSION_REREVIEW] = "first reviewed revision"

    if prior_disagreement:
        select(DEBATE_ARCHITECTURE, "reviewers previously disagreed")

    if verified_blocker:
        select(REFINE_REMEDIATION, "a verified blocking defect needs a minimal fix")
    else:
        plan.omitted[REFINE_REMEDIATION] = "no verified blocking defect"

    return plan


def render_activities(plan: ReviewPlan) -> str:
    """The activity hint injected into the reviewer prompt.

    Terse by measurement, not by taste. Injecting each activity's full question
    made the reviewer narrate its analysis: against the same model and change,
    response time went from 11s to 183-229s and the output stopped being
    schema-valid JSON (truncated objects, prose in enum fields), because the
    narration competed with the JSON-only instruction. Naming the angles and
    explicitly suppressing the write-up restored compliance at 29s while still
    directing coverage.

    The full questions remain available via `ReviewPlan.questions()` for the
    ledger and for operator explanation; they are deliberately not prompt text.
    """
    names = [name for name, _ in plan.questions()]
    if not names:
        return ""
    return (
        f"Cover these angles internally ({', '.join(names)}). "
        "Do NOT write out that analysis; the verdict JSON is your only output."
    )

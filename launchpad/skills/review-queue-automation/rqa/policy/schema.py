"""The `.rqa/config.json` schema as data — `code/P-03-policy.md` §1, §2.

The allowed and required key sets at every level of `architecture.md` §11's
normative shape, and nothing else: no validation logic, no default values. A key
that is not named here is `UNKNOWN_KEY`, which is how the dead
`config.strategies.active` failure — a configured key the runtime read from
nowhere, so configured policy was silently ignored — cannot recur: a key this
file accepts is a key `validate()` actually materialises into the snapshot.

`AUTHORITY_KEYS` is derived from `CONTRACTS.md` §1's `Activity` rather than
restated, so the six activity keys cannot drift from the six the authority gate
grants against.
"""

from __future__ import annotations

from rqa.contracts import Activity

__all__ = [
    "TOP_LEVEL_KEYS",
    "AUTHORITY_KEYS",
    "ROUTE_REQUIRED_KEYS",
    "ROUTE_OPTIONAL_KEYS",
    "EXTERNAL_KEYS",
    "POLICY_REQUIRED_KEYS",
    "POLICY_OPTIONAL_KEYS",
    "OBLIGATION_KEYS",
    "BLOCKING_KEYS",
    "MECHANICAL_KEYS",
    "REMEDIATION_KEYS",
    "BUDGET_AXES",
]

#: Exactly five top-level sections, every one of them required: a config that omits
#: `budget` is as invalid as one naming a sixth top-level key (§2).
TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {"authority", "routes", "external", "policy", "budget"}
)

#: The six activity keys, each `true`/`false` and defaulting to `false` (§2).
AUTHORITY_KEYS: frozenset[str] = frozenset(activity.value for activity in Activity)

#: Every `routes[*]` entry carries all five shared `Route` fields (§2: fail-closed at
#: the shared boundaries, including a non-empty `family`).
ROUTE_REQUIRED_KEYS: frozenset[str] = frozenset(
    {"harness", "model", "provider", "family", "external"}
)
#: `command` is the operator-declared argv for a harness RQA ships no alias for.
ROUTE_OPTIONAL_KEYS: frozenset[str] = frozenset({"command"})

EXTERNAL_KEYS: frozenset[str] = frozenset({"allowed", "deny_label"})

#: `policy.version` is not here: it falls back to `validate.POLICY_VERSION_DEFAULT`
#: (U-POLICY-04's kept mechanism). Everything below is required, because every
#: absent one of them would *widen* what a review has to satisfy — an absent
#: `blocking` blocks nothing, an absent `obligations` obliges nothing.
POLICY_REQUIRED_KEYS: frozenset[str] = frozenset(
    {"obligations", "blocking", "mechanical", "assurance"}
)
#: `policy.remediation` is optional and materialises to `allow_forks=False`; §2
#: states that default, so it is the one policy subsection with a fallback.
POLICY_OPTIONAL_KEYS: frozenset[str] = frozenset({"version", "remediation"})

#: `rqa.protocol.Obligation`'s own fields (P-04 owns the shape).
OBLIGATION_KEYS: frozenset[str] = frozenset({"id", "paths", "required_for", "evidence"})

BLOCKING_KEYS: frozenset[str] = frozenset({"categories", "severities", "corroboration"})
MECHANICAL_KEYS: frozenset[str] = frozenset({"categories", "tools"})
REMEDIATION_KEYS: frozenset[str] = frozenset({"allow_forks"})

#: Ordered so a failure report lists budget axes the same way every time.
BUDGET_AXES: tuple[str, ...] = (
    "per_pr_tokens",
    "per_repo_daily_tokens",
    "per_model_daily_tokens",
)

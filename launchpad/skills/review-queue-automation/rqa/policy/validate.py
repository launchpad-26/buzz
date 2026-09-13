"""`validate()` — the fail-closed schema and semantic checker, plus the one set of
default literals this package binds every fallback to.

`code/P-03-policy.md` §1, §2, §3 step 3, §4. This is E-03's dependency, not an edge
of its own: nothing outside `rqa.policy` calls it.

**Fail-closed, and collected.** Every error class is gathered and returned together
(§8 T6); a validator that stopped at the first one would hide the rest, and an
operator fixing a config one error per run is an operator who never learns the whole
shape. No branch here degrades to a permissive default: a section whose type is
wrong is an error, never an empty stand-in, and the only fallbacks that exist are
the narrow ones §2 names — a missing `authority` key is `False`, a missing
`policy.remediation` is `allow_forks=False`, a missing `policy.version` is
`"unversioned"`.

**One literal source (U-POLICY-05).** `starter_config()` builds the starter document
from the same module constants this validator falls back to, so `onboard()`'s
generator and this validator can never disagree about what a default is. A derived
policy is a copy of what validated; there is no second default table that could
carry a wider value.

**The mechanical tool registry is resolved at call time, never at import.**
`MECHANICAL_TOOL_SET` is P-10's (`code/P-10-remediation.md`), a part that need not be
present for policy validation to be correct. An unimportable `rqa.remediation` is an
*empty* registry, so every configured tool id fails `TOOL_NOT_IN_SET` — the
fail-closed answer (§7) rather than an import error at admission. When P-10 lands,
membership resolves for real with no edit here. Only membership is ever tested: this
module never reads a `ToolSpec` and never runs a tool (§4).
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Any

from rqa.contracts import (
    Activity,
    Blocking,
    Budget,
    Category,
    External,
    Mechanical,
    Obligation,
    Policy,
    RemediationPolicy,
    Route,
    ValidationError,
    ValidationErrorCode,
    ValidationFailure,
)
from rqa.policy.schema import (
    AUTHORITY_KEYS,
    BLOCKING_KEYS,
    BUDGET_AXES,
    EXTERNAL_KEYS,
    MECHANICAL_KEYS,
    OBLIGATION_KEYS,
    POLICY_OPTIONAL_KEYS,
    POLICY_REQUIRED_KEYS,
    REMEDIATION_KEYS,
    ROUTE_OPTIONAL_KEYS,
    ROUTE_REQUIRED_KEYS,
    TOP_LEVEL_KEYS,
)
from rqa.policy.types import PolicyError, ValidatedConfig
from rqa.protocol import paths

__all__ = ["validate", "starter_config"]

# -- the one set of default literals (§1, U-POLICY-05) -------------------------

#: Every activity an operator has not enabled is disabled.
AUTHORITY_DEFAULT = False
#: U-POLICY-04's kept mechanism: an unversioned policy is still a pinnable policy.
POLICY_VERSION_DEFAULT = "unversioned"
EXTERNAL_ALLOWED_DEFAULT = False
DENY_LABEL_DEFAULT = ""
ALLOW_FORKS_DEFAULT = False
#: One corroborating finding, i.e. the finding itself.
CORROBORATION_DEFAULT = 1
#: No configured ceiling on a budget axis.
BUDGET_AXIS_DEFAULT: int | None = None

#: A valid one-segment repository-relative path, passed to `paths.matches` purely so
#: the matcher parses and validates the *pattern* beside it (§4). The Boolean result
#: is discarded: P-03 never interprets an obligation's paths.
_PATTERN_PROBE_PATH = "a"

_CODE = ValidationErrorCode


def starter_config() -> dict[str, Any]:
    """The starter `.rqa/config.json` document, built from this module's literals.

    `onboard()` (E-17, `code/P-03-policy.md` §3 step 1.2) writes exactly this and
    then re-validates it, so generator and validator share one literal source. Every
    section is present — in particular an inline `policy`, because `snapshot_for` is
    fail-closed on a missing one and a starter without it would leave every job the
    operator later runs unpinned. A fresh mutable dict per call: a caller editing the
    result must not be editing the defaults.
    """
    return {
        "authority": {key: AUTHORITY_DEFAULT for key in sorted(AUTHORITY_KEYS)},
        "routes": [],
        "external": {
            "allowed": EXTERNAL_ALLOWED_DEFAULT,
            "deny_label": DENY_LABEL_DEFAULT,
        },
        "policy": {
            "version": POLICY_VERSION_DEFAULT,
            "obligations": [],
            "blocking": {
                "categories": [],
                "severities": [],
                "corroboration": CORROBORATION_DEFAULT,
            },
            "mechanical": {"categories": [], "tools": []},
            "assurance": {},
            "remediation": {"allow_forks": ALLOW_FORKS_DEFAULT},
        },
        "budget": {axis: BUDGET_AXIS_DEFAULT for axis in BUDGET_AXES},
    }


def validate(
    raw: Mapping[str, Any], repo: str = "", *, trusted_archive: bool = False
) -> ValidatedConfig | ValidationFailure:
    """Check `raw` against §2's normative shape and semantic rules, fail-closed.

    Returns a `ValidatedConfig` when every rule holds, or a `ValidationFailure`
    carrying **every** error found — never the first one alone.

    `repo` is carried onto the returned `ValidationFailure` so a caller's failure
    names the repository it came from, exactly as §3 step 2's `UNREADABLE` failure
    does. It defaults to `""`, which keeps §3's documented `validate(raw)` call form
    (and `onboard`'s, which has no repository to name) working unchanged.

    `trusted_archive` is for one caller only: rebuilding the `Snapshot` of an
    already-pinned config out of `snapshots/<hash>.json`, whose SHA-256 has just been
    recomputed over its own bytes and matched against its name. Those bytes are
    provably the ones that validated at pin time, so membership in
    `MECHANICAL_TOOL_SET` — the one check here that depends on state outside these
    bytes, and that can therefore change after a pin — is not re-tested. Every
    structural and shape rule still runs; they are pure over `raw` and the packaged
    protocol vocabulary. A pinned read that re-resolved the live registry could start
    failing for a job that had already pinned successfully, which §5 and §7 forbid:
    a snapshot pinned to an in-flight job stays readable for the life of the state
    directory. Never pass this for a live read (§3 step 2/3).
    """
    errors: list[ValidationError] = []
    if not isinstance(raw, Mapping):
        return ValidationFailure(
            repo, (_err(_CODE.BAD_TYPE, "", "config root must be a JSON object"),)
        )

    present = set(raw)
    for key in _sorted(present - TOP_LEVEL_KEYS):
        errors.append(_err(_CODE.UNKNOWN_KEY, str(key), f"unknown top-level key {key!r}"))
    if "policy" not in present:
        # Exactly one error, and no deeper `policy.*` errors: there is no policy
        # section to check (§8 T2).
        errors.append(_err(_CODE.MISSING_POLICY, "policy", "no policy section"))
    for key in _sorted(TOP_LEVEL_KEYS - present - {"policy"}):
        errors.append(
            _err(_CODE.MISSING_REQUIRED_SECTION, key, f"required section {key!r} is absent")
        )

    authority = _authority(raw["authority"], errors) if "authority" in present else None
    routes = _routes(raw["routes"], errors) if "routes" in present else None
    external = _external(raw["external"], errors) if "external" in present else None
    # `None` means "these bytes already validated; do not re-test membership".
    registry = None if trusted_archive else _mechanical_tool_set()
    policy = _policy(raw["policy"], errors, registry) if "policy" in present else None
    budget = _budget(raw["budget"], errors) if "budget" in present else None

    if errors:
        return ValidationFailure(repo, tuple(errors))
    if authority is None or routes is None or external is None or policy is None or budget is None:
        # Unreachable: every None above appended at least one error first. Raising
        # rather than returning a half-built config keeps that invariant checkable
        # instead of silently handing out a snapshot nothing validated.
        raise PolicyError("validate() produced neither a config nor an error")
    return ValidatedConfig(
        authority=authority, routes=routes, external=external, policy=policy, budget=budget
    )


# -- sections ------------------------------------------------------------------


def _authority(value: Any, errors: list[ValidationError]) -> Mapping[Activity, bool] | None:
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, "authority", "authority must be an object"))
        return None
    ok = True
    for key in _sorted(set(value) - AUTHORITY_KEYS):
        ok = False
        errors.append(
            _err(
                _CODE.UNKNOWN_AUTHORITY_KEY,
                f"authority.{key}",
                f"{key!r} is not one of the six activities: {sorted(AUTHORITY_KEYS)}",
            )
        )
    granted: dict[Activity, bool] = {}
    for activity in Activity:
        # Absent means disabled: an operator who has not written a key has not
        # granted the activity (§2, §5's fail-closed authority gate).
        flag = _flag(value, "authority", activity.value, AUTHORITY_DEFAULT, errors)
        if flag is None:
            ok = False
            continue
        granted[activity] = flag
    return MappingProxyType(granted) if ok else None


def _routes(value: Any, errors: list[ValidationError]) -> tuple[Route, ...] | None:
    if not isinstance(value, (list, tuple)):
        errors.append(_err(_CODE.BAD_TYPE, "routes", "routes must be an ordered list"))
        return None
    built: list[Route] = []
    ok = True
    for index, entry in enumerate(value):
        route = _route(index, entry, errors)
        if route is None:
            ok = False
            continue
        built.append(route)
    # Order is meaning: the first route is preferred, the rest are fallbacks (§2).
    return tuple(built) if ok else None


def _route(index: int, entry: Any, errors: list[ValidationError]) -> Route | None:
    base = f"routes[{index}]"
    if not isinstance(entry, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, base, "a route must be an object"))
        return None
    ok = _keys(entry, base, ROUTE_REQUIRED_KEYS, ROUTE_OPTIONAL_KEYS, errors)
    harness = _text_field(entry, base, "harness", errors)
    model = _text_field(entry, base, "model", errors)
    provider = _text_field(entry, base, "provider", errors)
    # Fail-closed at the shared boundary: `family` is what keeps a fallback ladder
    # from re-trying the same provider family, so an empty one is not a route.
    family = _text_field(entry, base, "family", errors)
    external = None
    if "external" in entry:
        external = _flag(entry, base, "external", None, errors)
        if external is None:
            ok = False
    command: tuple[str, ...] | None = None
    if "command" in entry:
        command = _argv(entry["command"], f"{base}.command", errors)
        if command is None:
            ok = False
    if not ok or harness is None or model is None or provider is None or family is None:
        return None
    return Route(
        harness=harness,
        model=model,
        provider=provider,
        family=family,
        external=external,
        command=command,
    )


def _external(value: Any, errors: list[ValidationError]) -> External | None:
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, "external", "external must be an object"))
        return None
    ok = _keys(value, "external", frozenset(), EXTERNAL_KEYS, errors)
    allowed = _flag(value, "external", "allowed", EXTERNAL_ALLOWED_DEFAULT, errors)
    if allowed is None:
        ok = False
    deny_label = value.get("deny_label", DENY_LABEL_DEFAULT)
    if not isinstance(deny_label, str):
        ok = False
        errors.append(
            _err(_CODE.BAD_TYPE, "external.deny_label", "external.deny_label must be a string")
        )
    return External(allowed=allowed, deny_label=deny_label) if ok else None


def _policy(
    value: Any, errors: list[ValidationError], registry: Mapping[str, Any] | None
) -> Policy | None:
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, "policy", "policy must be an object"))
        return None
    ok = _keys(value, "policy", POLICY_REQUIRED_KEYS, POLICY_OPTIONAL_KEYS, errors)

    version = value.get("version", POLICY_VERSION_DEFAULT)
    if not isinstance(version, str) or not version:
        ok = False
        errors.append(
            _err(_CODE.BAD_TYPE, "policy.version", "policy.version must be a non-empty string")
        )

    obligations = _obligations(value["obligations"], errors) if "obligations" in value else None
    blocking = _blocking(value["blocking"], errors) if "blocking" in value else None
    mechanical = (
        _mechanical(value["mechanical"], errors, registry) if "mechanical" in value else None
    )
    assurance = _assurance(value["assurance"], errors) if "assurance" in value else None
    if "remediation" in value:
        # Present: it must be an object with only `allow_forks`. `null` is not an
        # object, and is BAD_TYPE like every other present-but-wrongly-typed field —
        # `dict.get` cannot tell an absent key from an explicit null, so presence is
        # tested here rather than inferred from the value.
        remediation = _remediation(value["remediation"], errors)
    else:
        # The one optional subsection: absent is `allow_forks=False`, never wider
        # (§8 T19), bound to the same literal the starter document writes.
        remediation = RemediationPolicy(allow_forks=ALLOW_FORKS_DEFAULT)

    if (
        not ok
        or obligations is None
        or blocking is None
        or mechanical is None
        or assurance is None
        or remediation is None
    ):
        return None
    return Policy(
        version=version,
        obligations=obligations,
        blocking=blocking,
        mechanical=mechanical,
        assurance=assurance,
        remediation=remediation,
    )


def _obligations(value: Any, errors: list[ValidationError]) -> tuple[Obligation, ...] | None:
    if not isinstance(value, (list, tuple)):
        errors.append(
            _err(_CODE.BAD_TYPE, "policy.obligations", "policy.obligations must be a list")
        )
        return None
    built: list[Obligation] = []
    ok = True
    for index, entry in enumerate(value):
        obligation = _obligation(index, entry, errors)
        if obligation is None:
            ok = False
            continue
        built.append(obligation)
    return tuple(built) if ok else None


def _obligation(index: int, entry: Any, errors: list[ValidationError]) -> Obligation | None:
    base = f"policy.obligations[{index}]"
    if not isinstance(entry, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, base, "an obligation must be an object"))
        return None
    ok = _keys(entry, base, OBLIGATION_KEYS, frozenset(), errors)
    identifier = _text_field(entry, base, "id", errors)
    globs = _globs(entry["paths"], f"{base}.paths", errors) if "paths" in entry else None
    required_for = (
        _texts(entry["required_for"], f"{base}.required_for", errors)
        if "required_for" in entry
        else None
    )
    evidence = None
    if "evidence" in entry:
        evidence = entry["evidence"]
        if not isinstance(evidence, str):
            ok = False
            errors.append(
                _err(_CODE.BAD_TYPE, f"{base}.evidence", f"{base}.evidence must be a string")
            )
    if not ok or identifier is None or globs is None or required_for is None or evidence is None:
        return None
    return Obligation(
        id=identifier,
        paths=globs,
        # Risk-class names stay P-04/P-07 business: nothing here re-checks that a
        # `required_for` value names a risk class anything else recognises (§7).
        required_for=frozenset(required_for),
        evidence=evidence,
    )


def _blocking(value: Any, errors: list[ValidationError]) -> Blocking | None:
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, "policy.blocking", "policy.blocking must be an object"))
        return None
    base = "policy.blocking"
    ok = _keys(value, base, BLOCKING_KEYS, frozenset(), errors)
    categories = (
        _categories(value["categories"], f"{base}.categories", errors)
        if "categories" in value
        else None
    )
    severities = (
        _texts(value["severities"], f"{base}.severities", errors) if "severities" in value else None
    )
    corroboration = (
        _count(value["corroboration"], f"{base}.corroboration", errors)
        if "corroboration" in value
        else None
    )
    if not ok or categories is None or severities is None or corroboration is None:
        return None
    return Blocking(
        categories=categories,
        severities=frozenset(severities),
        corroboration=corroboration,
    )


def _mechanical(
    value: Any, errors: list[ValidationError], registry: Mapping[str, Any] | None
) -> Mechanical | None:
    if not isinstance(value, Mapping):
        errors.append(
            _err(_CODE.BAD_TYPE, "policy.mechanical", "policy.mechanical must be an object")
        )
        return None
    base = "policy.mechanical"
    ok = _keys(value, base, MECHANICAL_KEYS, frozenset(), errors)
    categories = (
        _categories(value["categories"], f"{base}.categories", errors)
        if "categories" in value
        else None
    )
    tools = _tools(value["tools"], errors, registry) if "tools" in value else None
    if not ok or categories is None or tools is None:
        return None
    return Mechanical(categories=categories, tools=tools)


def _tools(
    value: Any, errors: list[ValidationError], registry: Mapping[str, Any] | None
) -> frozenset[str] | None:
    """Tool ids, structurally checked always and for membership only on a live read.

    `registry is None` is the trusted-archive path: these bytes have already been
    hash-verified against the name they were pinned under, so they are the bytes that
    passed membership at pin time, and re-testing membership against a registry that
    may have changed since would make a successful pin fail later.
    """
    base = "policy.mechanical.tools"
    if not isinstance(value, (list, tuple)):
        errors.append(_err(_CODE.BAD_TYPE, base, f"{base} must be a list of tool ids"))
        return None
    ok = True
    accepted: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item:
            ok = False
            errors.append(
                _err(_CODE.BAD_TYPE, f"{base}[{index}]", "a tool id must be a non-empty string")
            )
            continue
        if registry is not None and item not in registry:
            ok = False
            errors.append(
                _err(
                    _CODE.TOOL_NOT_IN_SET,
                    f"{base}[{index}]",
                    f"{item!r} is not a member of MECHANICAL_TOOL_SET",
                )
            )
            continue
        accepted.add(item)
    return frozenset(accepted) if ok else None


def _mechanical_tool_set() -> Mapping[str, Any]:
    """P-10's closed registry, resolved now rather than at import (§4).

    Absent module, absent attribute, or an attribute that is not a mapping: an empty
    registry. Every configured tool id then fails `TOOL_NOT_IN_SET`, which is the
    fail-closed answer — a policy naming a tool RQA cannot vouch for is refused, not
    accepted on trust. Substituting this function is how a test exercises membership
    without depending on whether P-10 is present.
    """
    try:
        from rqa import remediation
    except ImportError:
        return {}
    registry = getattr(remediation, "MECHANICAL_TOOL_SET", None)
    return registry if isinstance(registry, Mapping) else {}


def _assurance(value: Any, errors: list[ValidationError]) -> Mapping[str, int] | None:
    base = "policy.assurance"
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, base, f"{base} must be an object"))
        return None
    ok = True
    required: dict[str, int] = {}
    for key in _sorted(set(value)):
        if not isinstance(key, str) or not key:
            ok = False
            errors.append(_err(_CODE.BAD_TYPE, base, "a risk class must be a non-empty string"))
            continue
        participants = _count(value[key], f"{base}.{key}", errors)
        if participants is None:
            ok = False
            continue
        required[key] = participants
    return MappingProxyType(required) if ok else None


def _remediation(value: Any, errors: list[ValidationError]) -> RemediationPolicy | None:
    """A *present* `policy.remediation`. Absence is handled by `_policy`, which is
    the only place that can tell an absent key from an explicit `null`."""
    base = "policy.remediation"
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, base, f"{base} must be an object"))
        return None
    ok = _keys(value, base, frozenset(), REMEDIATION_KEYS, errors)
    allow_forks = _flag(value, base, "allow_forks", ALLOW_FORKS_DEFAULT, errors)
    if allow_forks is None:
        ok = False
    return RemediationPolicy(allow_forks=allow_forks) if ok else None


def _budget(value: Any, errors: list[ValidationError]) -> Budget | None:
    if not isinstance(value, Mapping):
        errors.append(_err(_CODE.BAD_TYPE, "budget", "budget must be an object"))
        return None
    ok = _keys(value, "budget", frozenset(), frozenset(BUDGET_AXES), errors)
    # Each axis is optional and an omitted axis is equivalent to an explicit `null`:
    # no configured ceiling on that axis (§2, ruled 2026-09-11). `CONTRACTS.md` §3
    # types every axis `int | None`, so "uncapped" is an expressible policy rather
    # than a widening this validator invents.
    axes: dict[str, int | None] = {}
    for axis in BUDGET_AXES:
        limit = value.get(axis, BUDGET_AXIS_DEFAULT)
        if limit is None:
            axes[axis] = None
            continue
        if not isinstance(limit, int) or isinstance(limit, bool):
            ok = False
            errors.append(
                _err(_CODE.BAD_TYPE, f"budget.{axis}", f"budget.{axis} must be an integer or null")
            )
            continue
        if limit < 0:
            ok = False
            errors.append(
                _err(_CODE.NEGATIVE_BUDGET, f"budget.{axis}", f"budget.{axis} is negative: {limit}")
            )
            continue
        axes[axis] = limit
    return Budget(**axes) if ok else None


# -- leaf helpers --------------------------------------------------------------


def _err(code: ValidationErrorCode, path: str, detail: str) -> ValidationError:
    return ValidationError(code=code, path=path, detail=detail)


def _sorted(keys: Any) -> list[Any]:
    """Deterministic order for a key set that a non-JSON caller may have made
    heterogeneous. Every failure report lists the same errors in the same order."""
    return sorted(keys, key=repr)


def _keys(
    value: Mapping[str, Any],
    base: str,
    required: frozenset[str],
    optional: frozenset[str],
    errors: list[ValidationError],
) -> bool:
    """Unknown keys and absent required keys at one level. True when the level's key
    set is acceptable; each value itself is its caller's business."""
    ok = True
    allowed = required | optional
    prefix = f"{base}." if base else ""
    for key in _sorted(set(value) - allowed):
        ok = False
        errors.append(
            _err(_CODE.UNKNOWN_KEY, f"{prefix}{key}", f"unknown key {key!r} under {base or 'root'}")
        )
    for key in _sorted(required - set(value)):
        ok = False
        errors.append(
            _err(
                _CODE.MISSING_REQUIRED_SECTION,
                f"{prefix}{key}",
                f"required key {key!r} is absent under {base or 'root'}",
            )
        )
    return ok


def _flag(
    value: Mapping[str, Any],
    base: str,
    key: str,
    default: bool | None,
    errors: list[ValidationError],
) -> bool | None:
    """A strictly Boolean config value. `default` is used when the key is absent;
    pass `None` when the caller has already reported the absence itself."""
    if key not in value:
        return default
    flag = value[key]
    if flag is not True and flag is not False:
        errors.append(
            _err(_CODE.BAD_TYPE, f"{base}.{key}", f"{base}.{key} must be true or false")
        )
        return None
    return flag


def _text(value: Any, path: str, errors: list[ValidationError]) -> str | None:
    if not isinstance(value, str) or not value:
        errors.append(_err(_CODE.BAD_TYPE, path, f"{path} must be a non-empty string"))
        return None
    return value


def _text_field(
    entry: Mapping[str, Any], base: str, key: str, errors: list[ValidationError]
) -> str | None:
    """A required non-empty string field. An absent key was already reported by
    `_keys`, so it produces no second error here."""
    if key not in entry:
        return None
    return _text(entry[key], f"{base}.{key}", errors)


def _texts(value: Any, path: str, errors: list[ValidationError]) -> tuple[str, ...] | None:
    if not isinstance(value, (list, tuple)):
        errors.append(_err(_CODE.BAD_TYPE, path, f"{path} must be a list of strings"))
        return None
    ok = True
    items: list[str] = []
    for index, item in enumerate(value):
        text = _text(item, f"{path}[{index}]", errors)
        if text is None:
            ok = False
            continue
        items.append(text)
    return tuple(items) if ok else None


def _argv(value: Any, path: str, errors: list[ValidationError]) -> tuple[str, ...] | None:
    """`command`: the operator-declared argv, each element a non-empty string, the
    first the executable (§2). Whether a harness alias may carry one at all is
    P-05/P-06's registry question, not this validator's."""
    argv = _texts(value, path, errors)
    if argv is None:
        return None
    if not argv:
        errors.append(_err(_CODE.BAD_TYPE, path, f"{path} must name an executable"))
        return None
    return argv


def _categories(value: Any, path: str, errors: list[ValidationError]) -> frozenset[Category] | None:
    """Every entry must name a `Category`, materialised as `frozenset[Category]` —
    never a string set, which is what makes `Snapshot.policy` the shared tree (§2)."""
    names = _texts(value, path, errors)
    if names is None:
        return None
    ok = True
    categories: set[Category] = set()
    for index, name in enumerate(names):
        try:
            categories.add(Category(name))
        except ValueError:
            ok = False
            errors.append(
                _err(
                    _CODE.BAD_TYPE,
                    f"{path}[{index}]",
                    f"{name!r} is not one of the seven finding categories",
                )
            )
    return frozenset(categories) if ok else None


def _globs(value: Any, path: str, errors: list[ValidationError]) -> tuple[str, ...] | None:
    """`PathGlob` patterns, parsed by `rqa.protocol.paths.matches` and nothing else.

    P-03 defines no glob semantics: it uses neither `fnmatch` nor `PurePath.match`
    nor a regex over patterns (§4, §7). The matcher's own `PathGlobError` is what
    makes a pattern invalid, and its message is the error's detail.
    """
    patterns = _texts(value, path, errors)
    if patterns is None:
        return None
    ok = True
    for index, pattern in enumerate(patterns):
        try:
            paths.matches(_PATTERN_PROBE_PATH, pattern)
        except paths.PathGlobError as exc:
            ok = False
            errors.append(_err(_CODE.INVALID_PATH_PATTERN, f"{path}[{index}]", str(exc)))
    return patterns if ok else None


def _count(value: Any, path: str, errors: list[ValidationError]) -> int | None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        errors.append(_err(_CODE.BAD_TYPE, path, f"{path} must be a non-negative integer"))
        return None
    return value

"""Structural validation for the packaged verdict schema."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from functools import cache
from typing import cast

from .version import schema_path


_JSON_TYPES: Mapping[str, type[object] | tuple[type[object], ...]] = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "boolean": bool,
    "null": type(None),
    "number": (int, float),
}


@cache
def _load_schema() -> Mapping[str, object]:
    loaded = json.loads(schema_path().read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise RuntimeError("packaged verdict schema is not an object")
    return cast(Mapping[str, object], loaded)


def structural_reasons(*, data: Mapping[str, object]) -> tuple[str, ...]:
    """Return every structural violation in ``data`` in deterministic order."""
    reasons: list[str] = []
    _validate(value=data, rule=_load_schema(), path="", reasons=reasons)
    return tuple(sorted(reasons))


def _validate(
    *,
    value: object,
    rule: Mapping[str, object],
    path: str,
    reasons: list[str],
) -> None:
    declared_type = rule.get("type")
    if declared_type is not None and not _matches_type(
        value=value, declared_type=declared_type
    ):
        reasons.append(
            _at(
                path=path,
                message=f"must be {_type_description(declared_type=declared_type)}",
            )
        )
        return

    enum = rule.get("enum")
    if isinstance(enum, list) and value not in enum:
        choices = ", ".join(repr(item) for item in enum)
        reasons.append(
            _at(path=path, message=f"must be one of {choices}; got {value!r}")
        )

    if isinstance(value, dict):
        _validate_object(value=value, rule=rule, path=path, reasons=reasons)
    elif isinstance(value, list):
        _validate_array(value=value, rule=rule, path=path, reasons=reasons)
    elif isinstance(value, str):
        _validate_string(value=value, rule=rule, path=path, reasons=reasons)
    elif isinstance(value, int) and not isinstance(value, bool):
        minimum = rule.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            reasons.append(_at(path=path, message=f"must be at least {minimum}"))


def _validate_object(
    *,
    value: Mapping[str, object],
    rule: Mapping[str, object],
    path: str,
    reasons: list[str],
) -> None:
    required = rule.get("required", ())
    if isinstance(required, list):
        for key in required:
            if isinstance(key, str) and key not in value:
                reasons.append(
                    _at(path=path, message=f"missing required field: {key}")
                )

    minimum = rule.get("minProperties")
    if isinstance(minimum, int) and len(value) < minimum:
        count = "one" if minimum == 1 else str(minimum)
        noun = "property" if minimum == 1 else "properties"
        reasons.append(_at(path=path, message=f"must contain at least {count} {noun}"))

    raw_properties = rule.get("properties", {})
    properties = (
        cast(Mapping[str, object], raw_properties)
        if isinstance(raw_properties, dict)
        else {}
    )
    additional = rule.get("additionalProperties", True)
    for key, item in value.items():
        child_path = _child(path=path, key=key)
        child_rule = properties.get(key)
        if isinstance(child_rule, dict):
            _validate(
                value=item,
                rule=cast(Mapping[str, object], child_rule),
                path=child_path,
                reasons=reasons,
            )
        elif additional is False:
            reasons.append(
                _at(path=path, message=f"unexpected property {key!r}")
            )
        elif isinstance(additional, dict):
            _validate(
                value=item,
                rule=cast(Mapping[str, object], additional),
                path=child_path,
                reasons=reasons,
            )


def _validate_array(
    *,
    value: Sequence[object],
    rule: Mapping[str, object],
    path: str,
    reasons: list[str],
) -> None:
    minimum = rule.get("minItems")
    if isinstance(minimum, int) and len(value) < minimum:
        count = "one" if minimum == 1 else str(minimum)
        noun = "item" if minimum == 1 else "items"
        reasons.append(_at(path=path, message=f"must contain at least {count} {noun}"))

    if rule.get("uniqueItems") is True:
        for index, item in enumerate(value):
            if any(item == previous for previous in value[:index]):
                reasons.append(
                    _at(path=path, message=f"must contain unique items; duplicate {item!r}")
                )
                break

    items = rule.get("items")
    if isinstance(items, dict):
        item_rule = cast(Mapping[str, object], items)
        for index, item in enumerate(value):
            _validate(
                value=item,
                rule=item_rule,
                path=f"{path}[{index}]",
                reasons=reasons,
            )


def _validate_string(
    *,
    value: str,
    rule: Mapping[str, object],
    path: str,
    reasons: list[str],
) -> None:
    minimum = rule.get("minLength")
    if isinstance(minimum, int) and len(value) < minimum:
        count = "one" if minimum == 1 else str(minimum)
        noun = "character" if minimum == 1 else "characters"
        reasons.append(_at(path=path, message=f"must contain at least {count} {noun}"))

    pattern = rule.get("pattern")
    if (
        isinstance(pattern, str)
        and re.search(_python_pattern(pattern=pattern), value) is None
    ):
        reasons.append(_at(path=path, message=f"must match pattern {pattern!r}"))


def _python_pattern(*, pattern: str) -> str:
    if not pattern.endswith("$"):
        return pattern
    prefix = pattern[:-1]
    preceding_backslashes = len(prefix) - len(prefix.rstrip("\\"))
    if preceding_backslashes % 2:
        return pattern
    return pattern[:-1] + r"\Z"


def _matches_type(*, value: object, declared_type: object) -> bool:
    names: Sequence[object]
    if isinstance(declared_type, list):
        names = declared_type
    else:
        names = (declared_type,)
    return any(
        isinstance(name, str) and _is_json_type(value=value, name=name)
        for name in names
    )


def _is_json_type(*, value: object, name: str) -> bool:
    expected = _JSON_TYPES.get(name)
    if expected is None:
        raise RuntimeError(f"unsupported schema type: {name!r}")
    if name in {"integer", "number"} and isinstance(value, bool):
        return False
    return isinstance(value, expected)


def _type_description(*, declared_type: object) -> str:
    if isinstance(declared_type, list):
        return " or ".join(str(item) for item in declared_type)
    return str(declared_type)


def _child(*, path: str, key: str) -> str:
    return f"{path}.{key}" if path else key


def _at(*, path: str, message: str) -> str:
    return f"{path}: {message}" if path else message

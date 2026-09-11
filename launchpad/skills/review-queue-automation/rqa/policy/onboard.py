"""`onboard()` — E-17, the operator CLI's starter-config and migration entry point.

`code/P-03-policy.md` §1, §2, §3 E-17. This is the other half of `rqa.policy`'s
public surface, built against `validate.py` and `types.py` from #2201's merged
half of the package. Nothing here contacts GitHub, a model, or a lease; nothing
here writes a record entry, `jobs.status`, or `jobs.snapshot_hash` (§7).

**One literal source (U-POLICY-05).** The starter document this module writes is
exactly `rqa.policy.validate.starter_config()` — the same module constants
`validate()` itself falls back to — so generator and validator can never
disagree about what a default is. This file defines no second copy of those
literals.

**Validate before writing, always.** Both the plain-mode starter and the
migrated document are checked with `validate()` before any byte reaches disk.
Migrate mode never repairs a write after the fact: on a rejected conversion the
original file is left exactly as it was (U-POLICY-06's rework finding).
"""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from rqa.contracts import ValidationError, ValidationFailure
from rqa.policy.snapshot import config_path
from rqa.policy.types import PolicyError, utcnow
from rqa.policy.validate import starter_config, validate

__all__ = ["onboard", "OnboardResult", "Written", "OnboardRefusal", "OnboardRefusalReason"]


class OnboardRefusalReason(str, Enum):
    ALREADY_EXISTS = "already_exists"  # plain mode: a config already exists
    NO_CONFIG_TO_MIGRATE = "no_config_to_migrate"  # --migrate: nothing to convert
    UNREADABLE_EXISTING = "unreadable_existing"  # --migrate: existing file unreadable/not JSON
    MIGRATED_CONFIG_INVALID = "migrated_config_invalid"  # --migrate: converted result fails validate()


@dataclass(frozen=True)
class Written:
    path: str


@dataclass(frozen=True)
class OnboardRefusal:
    reason: OnboardRefusalReason
    detail: str
    errors: tuple[ValidationError, ...] = ()  # populated only for MIGRATED_CONFIG_INVALID


OnboardResult = Written | OnboardRefusal

#: Notification-transport and retention-window keys, dropped wherever nested
#: (`container.md` §5: "four key groups removed"; §3 of this file's contract).
_DROPPED_KEYS = frozenset({"notifications", "retention"})

#: `authority` keys the old shape never named, so migration sets them `False`
#: unconditionally — "everything not previously live is false" (architecture.md §14).
_NEVER_PREVIOUSLY_LIVE = ("comment", "approve", "request_changes", "merge")


def onboard(
    *,
    repo: str,
    migrate: bool = False,
    clock: Callable[[], datetime] = utcnow,
) -> OnboardResult:
    """Write a starter `.rqa/config.json`, or convert an existing old-shape one.

    `clock` is accepted for the same reason every other entry point in this
    package takes one (a fixed, injectable notion of "now"); no branch below
    needs a timestamp, since `onboard` writes no record entry and no
    `snapshots` row (§6, §7).
    """
    del clock  # accepted per the fixed signature; no branch here needs "now"
    path = config_path(repo)
    if not migrate:
        return _onboard_plain(path)
    return _onboard_migrate(path)


def _onboard_plain(path: Path) -> OnboardResult:
    if path.exists():
        # The existing file is never opened for writing — refused outright,
        # bytes untouched (U-POLICY-06; §8 T23).
        return OnboardRefusal(OnboardRefusalReason.ALREADY_EXISTS, detail=str(path))

    starter = starter_config()
    validated = validate(starter)
    if isinstance(validated, ValidationFailure):
        # The generator producing a config its own validator rejects is this
        # module's own bug, never an operator-visible outcome (§3 step 1.3).
        raise PolicyError(
            f"starter_config() produced a config validate() rejects: {validated.errors}"
        )
    _atomic_write(path, _canonical(starter))
    return Written(path=str(path))


def _onboard_migrate(path: Path) -> OnboardResult:
    if not path.exists():
        return OnboardRefusal(OnboardRefusalReason.NO_CONFIG_TO_MIGRATE, detail=str(path))

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return OnboardRefusal(OnboardRefusalReason.UNREADABLE_EXISTING, detail=str(exc))
    if not isinstance(raw, Mapping):
        return OnboardRefusal(
            OnboardRefusalReason.UNREADABLE_EXISTING,
            detail="parsed JSON is not an object",
        )

    migrated = migrate_config(raw)
    validated = validate(migrated)
    if isinstance(validated, ValidationFailure):
        # Validated before any write is attempted; the original file on disk
        # is untouched (§3 step 2.4, U-POLICY-06's rework finding).
        return OnboardRefusal(
            OnboardRefusalReason.MIGRATED_CONFIG_INVALID,
            detail="migrated config is invalid",
            errors=validated.errors,
        )
    _atomic_write(path, _canonical(migrated))
    return Written(path=str(path))


def migrate_config(old: Mapping[str, Any]) -> dict[str, Any]:
    """`architecture.md` §14, `container.md` §5's `config` row. A pure function,
    no side effects: never opens a file, never writes, never raises for
    malformed input — an unrecognised leftover key surfaces later, as
    `MIGRATED_CONFIG_INVALID` from `validate()`, never repaired here.
    """
    stripped = _drop_nested(old)
    migrated: dict[str, Any] = dict(stripped)

    old_authority = old.get("authority", {})
    old_authority = old_authority if isinstance(old_authority, Mapping) else {}
    authority: dict[str, Any] = {key: False for key in _NEVER_PREVIOUSLY_LIVE}
    authority["review"] = bool(old_authority.get("review", False))
    authority["remediate"] = bool(old_authority.get("fix", False))
    # `authority.triage`, if present, is read and discarded: the lane it gated
    # is not carried forward at all, by any name.
    migrated["authority"] = authority
    return migrated


def _drop_nested(value: Any) -> Any:
    """Every notification-transport key and the retention-window key, wherever
    nested, dropped; everything else copied through unchanged."""
    if isinstance(value, Mapping):
        return {
            key: _drop_nested(inner) for key, inner in value.items() if key not in _DROPPED_KEYS
        }
    if isinstance(value, list):
        return [_drop_nested(item) for item in value]
    return value


def _canonical(document: Mapping[str, Any]) -> bytes:
    return json.dumps(document, sort_keys=True, indent=2).encode("utf-8") + b"\n"


def _atomic_write(path: Path, body: bytes) -> None:
    """U-RESILIENCE-14's mechanism, the same one `store.py` uses for
    `snapshots/<hash>.json`: same-directory temp file, flush, fsync, atomic
    rename onto `config.json`. A reader sees either no file or the whole file,
    never a truncated one."""
    directory = path.parent
    directory.mkdir(parents=True, exist_ok=True)
    temporary = directory / f"{path.name}.tmp"
    try:
        with open(temporary, "wb") as handle:
            handle.write(body)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise
    handle_fd = os.open(directory, os.O_RDONLY)
    try:
        os.fsync(handle_fd)
    except OSError:
        # Some filesystems refuse to fsync a directory; the rename is already
        # atomic, only its durability across a power loss is weaker here.
        pass
    finally:
        os.close(handle_fd)

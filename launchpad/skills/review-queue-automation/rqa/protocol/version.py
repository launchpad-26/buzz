"""`PROTOCOL_VERSION`, `schema_path()`, `protocol_hash()`.

The published artefact — `schema/verdict-<PROTOCOL_VERSION>.json` and `PROTOCOL.md` —
is packaged with the RQA source tree under version control, not written or read from
`state/`. It changes only when a maintainer publishes a new protocol version, never
at runtime: there is no migration, negotiation, or multi-version dispatch.

`protocol_hash()` reads only these two packaged files and is not an E-NN call; it
never touches the network, the environment, another job's files, or GitHub.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

#: The one protocol version this build packages. `validate()` (P-04 §3, owned by the
#: sibling lane) checks every payload against exactly this value.
PROTOCOL_VERSION = "1"

_PACKAGE_DIR = Path(__file__).resolve().parent


def schema_path() -> Path:
    """Path to the packaged JSON Schema for `PROTOCOL_VERSION`."""
    return _PACKAGE_DIR / "schema" / f"verdict-{PROTOCOL_VERSION}.json"


def protocol_hash() -> str:
    """Stable SHA-256 hex digest over the published schema plus `PROTOCOL.md`.

    Deterministic across runs for the same packaged bytes, and changed by a single
    byte anywhere in either file — this is what ties `Snapshot.protocol_hash` to the
    exact protocol definition a job ran under.
    """
    digest = hashlib.sha256()
    digest.update(schema_path().read_bytes())
    digest.update(b"\x00")
    digest.update((_PACKAGE_DIR / "PROTOCOL.md").read_bytes())
    return digest.hexdigest()

"""E-25: the operator-held HMAC key, read from the platform keychain —
`code/P-12-record.md` §2, §4, §7 [ADR-F assumed].

`KeyStore` is defined only in `CONTRACTS.md` §9 and imported here; `OSKeyStore` is
the implementation, and it is the whole of this part's cross-boundary surface.

**What this module may do, and what it may never do.** It reads one item,
`rqa-record-hmac`, through the local keychain command. It never writes, rotates,
generates or logs a key — ADR-F: "the key is the operator's and never RQA's to write
into the record" — and no key byte is ever put into a return value other than the
key itself, an exception message, a docstring or the record. The backends invoke `security` on macOS or `secret-tool` on Linux.
They query the local keychain service and perform no remote network operation.

**Absent is not broken.** An absent item returns `None`, and the callers treat that
as a specified outcome: `append` proceeds unkeyed and says so (`keyed=0`,
`hmac=NULL`) and `verify` opens an `unverifiable: no key` segment (ADR-0063). A
keychain that cannot be *asked* is a different thing and raises
`KeyStoreExplanationUnavailable`, which `append` converts to `AppendFailed` (§3.1
step 5) and `verify` reports as the same `unverifiable: no key` run (§3.2 step 3).
The two are deliberately not unified: one means "the operator has no key", the other
means "this machine could not answer", and inventing a key for either is not an
option this part has.
"""

from __future__ import annotations

import subprocess
import sys
from collections.abc import Callable, Sequence

from rqa.contracts import KeyStore

__all__ = ["KEY_NAME", "KeyStoreExplanationUnavailable", "OSKeyStore", "KeyStore"]

#: The one keychain item this part reads (§3.1 step 5, §3.2 step 3).
KEY_NAME = "rqa-record-hmac"

#: `security` exits 44 for "the item you asked for is not in the keychain". That is
#: the absent-item answer, not a failure to ask.
_ITEM_NOT_FOUND = 44

#: Seconds. A local keychain read that has not answered by now is a machine fault,
#: not a slow answer; it becomes `KeyStoreExplanationUnavailable` like any other.
_TIMEOUT = 10.0


class KeyStoreExplanationUnavailable(Exception):
    """The platform keychain command could not be invoked or queried. This differs from an
    absent item, for which `KeyStore.read()` returns None."""


def _run_security(argv: Sequence[str]) -> tuple[int, bytes]:
    """Run the local keychain command, returning `(returncode, stdout)`.

    `stderr` is captured and dropped rather than inherited: the command writes the
    item's attributes there on some paths, and this part has no business forwarding
    keychain contents to a log.
    """
    completed = subprocess.run(  # noqa: S603 - fixed local argv, never shell
        list(argv),
        capture_output=True,
        timeout=_TIMEOUT,
        check=False,
    )
    return completed.returncode, completed.stdout


def _run_secret_tool(argv: Sequence[str]) -> tuple[int, bytes, bool]:
    """Read Secret Service; preserve only whether diagnostics were emitted."""
    completed = subprocess.run(
        list(argv), stdin=subprocess.DEVNULL, capture_output=True,
        timeout=_TIMEOUT, check=False,
    )
    return completed.returncode, completed.stdout, bool(completed.stderr)


class OSKeyStore:
    """Reads only `rqa-record-hmac` through the platform keychain command. It returns None only for
    that absent item and never writes, rotates, generates, or logs a key."""

    def __init__(self, *, runner: Callable[[Sequence[str]], tuple[int, bytes]] = _run_security,
                 linux_runner: Callable[[Sequence[str]], tuple[int, bytes, bool]] = _run_secret_tool):
        # Injectable so §8's tests can exercise every branch without a real keychain
        # and without a key ever existing on the machine running them.
        self._runner = runner
        self._linux_runner = linux_runner

    def read(self, name: str) -> bytes | None:
        """The operator's key bytes, `None` when the item is absent.

        Raises `KeyStoreExplanationUnavailable` when the keychain could not be asked:
        no platform command here, a command that would not run, or a non-zero exit
        that is not the absent-item code.
        """
        if name != KEY_NAME:
            raise KeyStoreExplanationUnavailable(
                f"this key store serves only {KEY_NAME!r}, not {name!r}"
            )
        if sys.platform == "linux":
            return self._read_linux(name)
        if sys.platform != "darwin":
            raise KeyStoreExplanationUnavailable(
                f"unsupported keychain platform {sys.platform!r}; use macOS Keychain "
                "or Linux Secret Service; no record was appended"
            )
        argv = ("security", "find-generic-password", "-w", "-s", name)
        try:
            returncode, stdout = self._runner(argv)
        except (OSError, subprocess.SubprocessError) as exc:
            raise KeyStoreExplanationUnavailable(
                f"the keychain command could not be run: {exc}"
            ) from exc
        if returncode == _ITEM_NOT_FOUND:
            return None
        if returncode != 0:
            # Deliberately without the command's own output: it can carry item
            # contents, and this message reaches logs and `AppendFailed`.
            raise KeyStoreExplanationUnavailable(
                f"the keychain command exited {returncode} reading {name!r}"
            )
        secret = stdout.strip()
        if not secret:
            raise KeyStoreExplanationUnavailable(
                f"the keychain returned an empty value for {name!r}"
            )
        return secret

    def _read_linux(self, name: str) -> bytes | None:
        """Distinguish an absent item from a failed query or a locked match.

        secret-tool lookup uses status 1 for both absence and errors. Errors
        emit diagnostics. A matching locked item may also have no readable
        secret, so an empty lookup requires an empty metadata search too.
        """
        try:
            code, value, diagnostics = self._linux_runner(
                ("secret-tool", "lookup", "service", name)
            )
            if code == 0 and value and not diagnostics:
                return value
            if code == 1 and not value and not diagnostics:
                code, matches, diagnostics = self._linux_runner(
                    ("secret-tool", "search", "--all", "service", name)
                )
                if code in (0, 1) and not matches and not diagnostics:
                    return None
        except (OSError, subprocess.SubprocessError):
            raise KeyStoreExplanationUnavailable(
                "Linux keychain unavailable: install secret-tool and start an unlocked "
                "Secret Service session; no record was appended"
            ) from None
        raise KeyStoreExplanationUnavailable(
            "Linux keychain did not return a readable key or confirm its absence; "
            "check the Secret Service session and unlock the keyring; no record was appended"
        )

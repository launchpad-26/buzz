#!/usr/bin/env python3
"""Suite-wide isolation: no real credential, no network.

WHY THIS FILE EXISTS. Nine tests in the legacy suite passed only because the
machine running them had a working `gh auth token`. They injected a fake sender
and never used a token, but the legacy transport resolved one anyway and fell
back to shelling out to `gh auth token`.
On a developer machine that returns a real credential and the tests go green; in
CI it fails and they do not. A suite whose result depends on ambient credentials
is not testing the code, it is testing the machine.

Setting a sentinel here fixes it everywhere rather than only in CI. Handing CI a
real `GITHUB_TOKEN` would have turned the job green while leaving the tests
reaching for live credentials on every machine — the opposite of the point.

The sentinel is deliberately not token-shaped: nothing may be tempted to send
it, and a secret scanner should not have to decide whether it is real.

NETWORK. Every GitHub transport in this skill takes an injectable sender
precisely so its tests can prove they never call out. Replacing `socket.socket`
asserts that property for the whole suite instead of trusting each test to
inject. Verified: the suite passes unchanged with this in place, which means no
test was relying on real egress.
"""

from __future__ import annotations

import os
import socket

# Must be set before any test invokes a subprocess. `rqa.harness.invoke` and
# `rqa.supply.probe` both build the child environment from an allow-list, so a
# test that these two names never reach a child is only meaningful when this
# process actually has them.
os.environ["GITHUB_TOKEN"] = "not-a-real-token-suite-sentinel"
os.environ["GH_TOKEN"] = "not-a-real-token-suite-sentinel"


class _BlockedSocket(socket.socket):
    """Any attempt to open a socket during the suite is a defect, not a slow test."""

    def __init__(self, *args, **kwargs):
        raise RuntimeError(
            "the review-queue-automation suite attempted a network connection; "
            "every GitHub transport here takes an injectable sender and its "
            "tests must inject one"
        )


socket.socket = _BlockedSocket

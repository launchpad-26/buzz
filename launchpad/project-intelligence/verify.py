"""Decision logic stage 2 -- issue #211, STEP 6.

"Verify important claims even when confident." A claim that will be asserted as
settled fact is confirmed by a live Investigator call first, and a claim whose
confirmation comes back empty is downgraded rather than asserted.

Two rules, both from § Reasoning Rules and both load-bearing:

  1. Cached agreement is not confirmation. ProjectMemory agreeing with a claim
     changes nothing about whether the claim is still true -- memory records
     what was true when it was written. So the Investigator call happens even
     when stage 1 reported confident.
  2. An unconfirmed claim is never a FACT. It becomes an INFERENCE carrying the
     failed confirmation as its own evidence, so the answer says "I could not
     confirm this" instead of quietly asserting it.

Every FACT is verified, with no significance threshold. The plan's OPEN says
why: "significant enough to re-verify" is not mechanically decidable, one
read_file is cheap, and the failure mode of guessing wrong is asserting an
unverified fact -- the exact thing this layer exists to prevent.
"""

from __future__ import annotations

import investigator
from answer import Claim
from trace import Trace

# Confidence attached to a claim that could not be confirmed. Deliberately
# below a half: the evidence for it is a failed lookup, which is weaker than
# any evidence that pointed somewhere real.
UNCONFIRMED_CONFIDENCE = 0.3


def confirm_text_at(
    path: str,
    start_line: int,
    end_line: int,
    expected: str,
    trace: Trace,
    read_file=investigator.read_file,
) -> bool:
    """Read the exact cited range and check it contains what the claim says.

    This is the check that catches a citation which resolves but does not
    support its claim -- a real defect found at STEP 3, where a statement about
    tests cited the symbol's own definition ~850 lines from the test. Asking
    only "does the path exist" passes that; asking "does this range contain
    this text" does not.
    """
    # Reads through the caller's reader, defaulting to the real Investigator.
    # Cross-model review found the injection seam was SPLIT: investigation used
    # agent.tools while this function called the process-global investigator, so
    # a test driving an injected repository had its definition confirmed against
    # the real worktree instead -- silently downgrading a claim that the
    # injected data supported.
    try:
        text = read_file(path, start_line, end_line)
    except (OSError, ValueError) as exc:
        # A failed read is a failed confirmation, not a crash -- but it is also
        # not a silent pass. Recorded as not-found with the reason.
        trace.record(
            "read_file",
            f"{path}:{start_line}-{end_line}",
            found=False,
            detail=f"unreadable: {exc}",
        )
        return False

    found = expected in text
    trace.record(
        "read_file",
        f"{path}:{start_line}-{end_line}",
        found=found,
        detail=(f"contains {expected!r}" if found else f"does not contain {expected!r}"),
    )
    return found


def verified_fact(
    statement: str,
    expected: str,
    path: str,
    start_line: int,
    end_line: int,
    trace: Trace,
    read_file=investigator.read_file,
) -> Claim:
    """Emit a FACT only if the cited range confirms it; otherwise an INFERENCE.

    Never returns None. A dropped claim leaves an answer quietly shorter, and a
    reader cannot see the difference between "nothing to say" and "could not
    confirm what I was going to say" -- the downgrade keeps the failure visible.
    """
    citation = f"{path}:{start_line}-{end_line}"
    if confirm_text_at(path, start_line, end_line, expected, trace, read_file):
        return Claim(statement=statement, entry_class="FACT", evidence=(citation,))
    return Claim(
        statement=statement,
        entry_class="INFERENCE",
        evidence=(f"unconfirmed -- {citation} does not contain {expected!r}",),
        confidence=UNCONFIRMED_CONFIDENCE,
    )

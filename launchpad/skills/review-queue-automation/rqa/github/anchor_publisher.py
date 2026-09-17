"""E-27's GitHub implementation: publish an anchor as a pull-request review comment.

P-12 owns the anchor (`rqa/record/anchor.py`) and never imports GitHub. This module is
the other side of that seam, and it lives here — on P-09's side — for two reasons that
are easy to get wrong.

**It does not go through `rqa/github/writes.py`, and that is deliberate.** Every
mutation in that module routes through `_dispatch`, which calls
`record.append(job, "action", ...)`. Publishing an anchor through it would append an
entry, which moves the head, which needs a new anchor, which publishes again — for
ever. So this reaches `transport.mutate` directly.

**Which means it must check the grant itself.** `_dispatch` is also where
`_require_grant` runs, so bypassing it bypasses the authority gate too. Authority in
RQA is per-activity and fail-closed (#2006), and an advisory-only repository may hold
no comment authority at all. This module therefore calls `_require_grant` explicitly,
with `Activity.COMMENT`, before it sends anything. Skipping that check would widen
authority silently, which is the more serious of the two failure modes.

**What is published is a digest, never content.** The body carries the job id, the
sequence and the chain hash. A hash is a digest, so an anchor discloses nothing about
what the record says — which is what makes it safe to send to a pull request when the
record itself must never go there. `RQA-NFR-023`/`027`/`029` govern external sends;
this is the narrowest possible one, and an operator who has not configured comment
authority sends nothing at all.
"""

from __future__ import annotations

from rqa.contracts import Activity, Grant, Job
from rqa.github import transport as transport_module
from rqa.github.writes import _COMMENT_MUTATION, _read_pr_node, _require_grant
from rqa.record import Anchor, PublishFailed

__all__ = ["GithubAnchorPublisher", "anchor_body", "review_locator"]

#: Marks the comment as a machine-written anchor rather than review prose, so an
#: operator reading the thread knows what it is and RQA can find it again.
ANCHOR_MARKER = "<!-- rqa:record-anchor -->"


def review_locator(review_id: str) -> str:
    """The immutable GitHub node locator for one published review."""
    return f"github:pull-request-review:{review_id}"


def anchor_body(*, anchor: Anchor) -> str:
    """The published text. Job, sequence and hash — nothing from any payload."""
    return (
        f"{ANCHOR_MARKER}\n"
        f"RQA record anchor\n\n"
        f"- job: `{anchor.job}`\n"
        f"- seq: `{anchor.seq}`\n"
        f"- chain head: `{anchor.hash}`\n"
        f"- anchored at: `{anchor.at}`\n\n"
        f"This attests that the review record for this job held {anchor.seq} "
        f"entries ending in that hash. Entries appended after it are not covered."
    )


class GithubAnchorPublisher:
    """`AnchorPublisher` over one pull request. One mutation, no record write."""

    def __init__(self, *, adapter, job: Job, grant: Grant | None):
        self._adapter = adapter
        self._job = job
        self._grant = grant

    def publish(self, *, anchor: Anchor) -> str:
        """Post the anchor and return its destination locator.

        Raises `PublishFailed` for a refused grant or an unreachable GitHub — both are
        "the anchor did not land", which leaves the local row pending for retry. It
        never raises anything the caller has to special-case, and never returns a
        destination it did not actually write to.
        """
        try:
            _require_grant(self._grant, Activity.COMMENT, self._job)
        except Exception as exc:  # AdapterError, and anything a future gate adds
            raise PublishFailed(
                f"no authority to publish an anchor to {self._job.repo}#{self._job.number}: {exc}"
            ) from exc

        try:
            node = _read_pr_node(self._adapter, job=self._job, operation="anchor")
            response = self._adapter.transport.mutate(
                _COMMENT_MUTATION,
                {"pullRequestId": node.pr_id, "body": anchor_body(anchor=anchor)},
                operation="anchor",
            )
            result = response.get("addPullRequestReview") if hasattr(response, "get") else None
            review = result.get("pullRequestReview") if hasattr(result, "get") else None
            review_id = review.get("id") if hasattr(review, "get") else None
            if not isinstance(review_id, str) or not review_id:
                raise ValueError("anchor mutation returned no review id")
        except transport_module.Unavailable as failure:
            raise PublishFailed(f"GitHub was unavailable: {failure}") from failure
        except Exception as failure:  # noqa: BLE001 - the containment boundary
            # **This is where a misbehaving adapter is contained, and it is here rather
            # than in `rqa/record/` for a reason.** P-12 forbids `except Exception`
            # anywhere in its package (U-DISPATCH-20's defect was a swallowed failure
            # around a ledger write), so `anchor_job` catches only `PublishFailed`.
            # That makes honouring the contract this class's job: whatever the adapter
            # or transport throws, the caller sees a failed publish — the anchor stays
            # pending and is retried — never an exception that could fail a review.
            #
            # `BaseException` is deliberately not caught: KeyboardInterrupt and
            # SystemExit are the operator stopping the process, not a publish outcome.
            raise PublishFailed(
                f"publishing the anchor failed: {type(failure).__name__}: {failure}"
            ) from failure

        return review_locator(review_id)

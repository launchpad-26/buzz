"""RQA — the review-queue-automation implementation package.

Sub-packages own disjoint parts of `architecture/code/`:

* `rqa.contracts` — the shared type set of `code/CONTRACTS.md` §1 and §§3-8.
* `rqa.protocol`  — `code/CONTRACTS.md` §2, owned by `code/P-04-protocol.md`.

The package root deliberately re-exports nothing: a part imports the module that
owns a type, so there is exactly one declaration site per name.
"""

from __future__ import annotations

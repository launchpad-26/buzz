"""`rqa.intake` — P-01, `architecture/code/P-01-intake.md`.

Finds the work and holds the queue: gates every configured repository on a
valid, resolvable snapshot before touching it, holds the machine's exclusive
sweep lock, reads GitHub's PR inventory, creates at most one job per revision,
detects a head change and hands Lifecycle the superseded predecessor's id,
provides the GitHub-verified review-lease mechanism a `Grant` authorises
Lifecycle to drive, and hands a bounded, fairly-ordered batch of jobs to
Lifecycle — never deciding what a job means, only that it exists and whose
turn it is.

No other module in RQA imports from `rqa.intake` except through this file,
with one documented exception: `rqa.github` imports `rqa.intake.identity`
directly for `stable_hash` (§1). The public surface is §1's fourteen-name
re-export list — `tick`, `TickResult`, `AdmissionRefusal`, `JobFailure`,
`job_id`, `stable_hash`, `GithubAdapter`, `Lease`, `JobStore`, `PrFactsStore`,
`LeaseStore`, `PrFactsRow`, `LeaseRow`, `IntakeError` — plus the concrete
stores a composition root must construct: `SqliteJobStore`,
`SqlitePrFactsStore`, `SqliteLeaseStore` and `ensure_schema`.

**Why the stores are surface.** `tick()` takes `jobs=`/`pr_facts=`/`leases=` as
parameters and nothing inside `rqa/intake/` ever builds one, so something
outside this package always must; duplicating the schema in the caller is
independently forbidden by §5's sole-writer rule. The operator CLI's
composition root (#2211) is the first module in RQA whose job is exactly that
construction, and it is what falsified the sentence above — the clause held
only because no such module existed yet. Publishing the four names keeps that
import a front-door one. `ensure_schema` is P-01's own: each part publishes its
own through its own package, so `rqa.intake.ensure_schema` and
`rqa.github.ensure_schema` are distinct front doors and no collision arises.

`GithubAdapter` is re-exported from the already-landed `rqa.github`, never
redefined. An import is not a declaration: this file defines nothing.
"""

from __future__ import annotations

from rqa.github import GithubAdapter
from rqa.intake.identity import job_id, stable_hash
from rqa.intake.lease import Lease
from rqa.intake.store import (
    JobStore,
    LeaseStore,
    PrFactsStore,
    SqliteJobStore,
    SqliteLeaseStore,
    SqlitePrFactsStore,
    ensure_schema,
)
from rqa.intake.types import (
    AdmissionRefusal,
    IntakeError,
    JobFailure,
    LeaseRow,
    PrFactsRow,
    TickResult,
)
from rqa.intake.tick import tick

__all__ = [
    "tick",
    "TickResult",
    "AdmissionRefusal",
    "JobFailure",
    "job_id",
    "stable_hash",
    "GithubAdapter",
    "Lease",
    "JobStore",
    "PrFactsStore",
    "LeaseStore",
    "PrFactsRow",
    "LeaseRow",
    "IntakeError",
    "SqliteJobStore",
    "SqlitePrFactsStore",
    "SqliteLeaseStore",
    "ensure_schema",
]

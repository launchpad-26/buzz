# P-09 GitHub adapter — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-09 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Every byte RQA sends to or reads from GitHub crosses this one
adapter and no other; every write it performs carries proof, passed in by the caller, that an activity
was already granted, and is idempotent by a deterministic id.

**Depends on.** ADR-E ([#2158](https://github.com/launchpad-26/buzz/issues/2158), assumed): one
ephemeral `gh auth token` path and the recorded broader-repository residual. P-09's behavior is
otherwise independent of ADR-D/F/G.

## 1. Modules

```
rqa/github/
  __init__.py        re-exports the §4 shared imports plus GithubAdapter, CheckConclusion, FAILING,
                      UNSETTLED, PASSING, MutationKind, Stale, LeaseTaken, GithubUnavailable,
                      CapabilityReading, and AdapterError
  types.py           P-09-private result/implementation types; imports §4 shared types unchanged
  conclusions.py      the canonical CheckConclusion vocabulary and total normalisation functions
                      (U-VERDICT-06)
  transport.py        the ONLY module in RQA that imports an HTTP client (`urllib.request`,
                      stdlib); owns this adapter's private credential resolution [ADR-E assumed],
                      the ETag cache, paginated REST GET, GraphQL POST, and rate-limit recording
                      from response headers
  reads.py           E-01 `inventory`, E-14 `checks`, and one assembled E-23 `facts`
  writes.py          E-01 `claim_lease`/`release_lease`, E-12 `submit_review`/`comment`/`merge`:
                      the fixed `MutationKind` enum, the deterministic `client_mutation_id`, and
                      the shared `Grant` check every write starts with
  capability.py      E-16 `probe`
  store.py           the `mutations`, `etags`, `api_calls` tables and their read/write Protocols
  testing.py         U-DOCS-24: `NON_TOKEN_CREDENTIAL` and `raising_socket()`, imported by every
                      test in this package and by any other part's fakes for this adapter
```

No other module in RQA imports from `rqa.github` except through `__init__`. `rqa.github` imports only
`rqa.record` (to append, E-13) and, for types only, `rqa.authority`'s `__init__` (`Grant`, `Activity`)
and `rqa.intake`'s `Job` type. It also imports `rqa.intake.identity.stable_hash(*parts: str) -> str`
(§3 preamble) rather than re-implementing a hash: P-01 owns job/mutation identity (U-RESILIENCE-13),
components.md §7 credits it as "the deterministic mutation-id half...used by P-09", and P-01 has fixed
its definition as `sha256("\x1f".join(parts).encode()).hexdigest()`. It imports nothing else in RQA —
no `rqa.policy`, `rqa.lifecycle`, `rqa.judgement`, `rqa.remediation`, or any other part
— and `transport.py` is the **only** module anywhere in RQA that imports an HTTP client: every other
part reaches GitHub only by calling a function in this package. `rqa.authority` (P-08) separately reads
`gh auth token` for its own use (E-22); this package's private credential resolution in `transport.py`
is a second, independent read of the same underlying command, never routed through P-08 — see §4.

## 2. Types

`PrFacts`, `Facts`, `CheckRun`, `Mutation`, `Stale`, `LeaseTaken`, `GithubUnavailable`, and
`CapabilityReading` are boundary values defined only in [`CONTRACTS.md`](CONTRACTS.md) §4 and
imported unchanged. `PrFacts.head_repo` and `head_ref` identify the actual PR-head destination,
including a fork; `head_protected` is the fail-closed protection reading for that destination.
`Facts.fetched_at` is the coherent fact-capture time, not the later evidence cutoff.

```python
# types.py — the mutation discriminator and programming error remain private implementation details.
class MutationKind(str, Enum):
    ASSIGNEE_ADD = "assignee_add"
    ASSIGNEE_REMOVE = "assignee_remove"
    COMMENT = "comment"
    REVIEW_SUBMIT = "review_submit"
    MERGE = "merge"

class AdapterError(Exception):
    """Programming error: a handle is bound to the wrong job, or a write lacks its matching Grant."""
```

`conclusions.py` implements the canonical `CheckConclusion`, `FAILING`, `UNSETTLED`, and `PASSING`
definitions from `CONTRACTS.md` §4 without redefining a neighbour-facing type here. The three sets are
disjoint/exhaustive. Unknown GitHub values normalize to `ACTION_REQUIRED`; pending never
corroborates, blocks, or inherits.

`Grant`, `Activity`, `Job`, `RecordWriter`, and `Entry` are shared contracts defined only in
[`CONTRACTS.md`](CONTRACTS.md) §§1, 7, and 8. Every write reads only `grant.activity`, `grant.repo`,
`grant.job_id`, `job.id`, `job.repo`, `job.number`, and `job.head_sha`.

## 3. Entry points — E-01, E-12, E-14, E-16, E-23

All public edges in this section have exactly the signatures in
[`CONTRACTS.md`](CONTRACTS.md) §9. `GithubAdapter` may use repository-bound private helpers, but those
helpers are not a neighbour-facing Protocol and never expose a second shape for an E-NN.

**Shared write discipline (U-AUTHORITY-09).** Every write first calls
`_require_grant(grant, activity, job)`. If `grant is None`, `grant.activity is not activity`,
`grant.repo != job.repo`, or `grant.job_id != job.id`, it raises `AdapterError` before any GitHub call
or record append. It then derives
`client_mutation_id = stable_hash(job.id, kind.value, canonical_json(payload))`, returns an existing
terminal mutation without an HTTP call or append, or performs the fixed mutation and appends exactly
one `action` entry through its supplied `record`. `AppendFailed` propagates.

### 3.1 E-01 — inventory and lease writes

```python
def inventory(*, repo: str) -> tuple[PrFacts, ...] | GithubUnavailable: ...
def claim_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | LeaseTaken | GithubUnavailable: ...
def release_lease(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...
```

`inventory` paginates open PRs (50 per page, cap five) and returns `()` when there are none. A null
repository returns `GithubUnavailable(op="inventory", reason="not_found", retriable=False)`; a transport,
rate-limit, or GraphQL error returns the corresponding `GithubUnavailable`; a page-cap overrun or malformed
required PR field returns `GithubUnavailable(reason="page_cap_exceeded"|"malformed", retriable=False)`.
For every returned PR, it captures the actual `head_repo`/`head_ref` and queries GraphQL
`repository(owner: head_owner, name: head_name).ref(qualifiedName:
"refs/heads/<head_ref>").branchProtectionRule`. A readable exact ref with non-null rule is protected;
a readable exact ref with null rule is definitively unprotected. Missing ref, GraphQL errors,
authorization/rate-limit/transport failure or malformed shape sets `head_protected=True`. A failed
read therefore never becomes writable, while a real unprotected branch is representable.

Both lease writes require `Activity.REVIEW`. `claim_lease` reads the current assignees; an unreadable
read returns `GithubUnavailable`, another login returns `LeaseTaken`, an existing operator assignment returns
the completed no-op `Mutation`, and otherwise it sends the fixed add-assignee mutation. Its mandatory
re-read returns the accepted completed `Mutation` only when the operator is present; absence returns
`GithubUnavailable(reason="incomplete", retriable=True)`. `release_lease` mirrors this with remove-assignee:
operator absent is its completed no-op/success condition, while every non-success transport or
verification outcome returns `GithubUnavailable`. These are total branches.

### 3.2 E-12 — review, comment, and merge writes

```python
def submit_review(*, job: Job, state: Literal["APPROVE", "REQUEST_CHANGES"], body: str, grant: Grant,
                  record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
def comment(*, job: Job, body: str, grant: Grant, record: RecordWriter) -> Mutation | GithubUnavailable: ...
def merge(*, job: Job, grant: Grant, record: RecordWriter) -> Mutation | Stale | GithubUnavailable: ...
```

`submit_review` requires `Activity.APPROVE` for `"APPROVE"` and `Activity.REQUEST_CHANGES` for
`"REQUEST_CHANGES"`. It uses two fixed GraphQL literals (`APPROVE` and `CHANGES_REQUESTED`), never an
interpolated event. For APPROVE it freshly reads the PR: a changed head or closed PR returns `Stale`;
otherwise it sends the mutation and performs the mandatory review visibility post-check. A failed
send or unreadable post-check returns `GithubUnavailable`; a visible matching APPROVED review returns the
accepted `Mutation`. REQUEST_CHANGES sends its fixed event after the shared discipline and returns
either the accepted `Mutation` or `GithubUnavailable`. No branch returns an untyped ambiguous result.

`comment` requires `Activity.COMMENT`, sends only the fixed COMMENT mutation, and returns an accepted
`Mutation` or `GithubUnavailable`. `merge` requires `Activity.MERGE`, sends
`mergePullRequest` with `expectedHeadOid=job.head_sha`, returns `Stale` on GitHub's head mismatch,
and otherwise returns its accepted `Mutation` or `GithubUnavailable`.

### 3.3 E-14 — checks

```python
def checks(*, repo: str, sha: str) -> tuple[CheckRun, ...] | GithubUnavailable: ...
```

It ETag-caches and paginates `check-runs` plus legacy `status`, normalises every documented or unknown
source value to exactly one `CheckConclusion`, and lets a check-run win a same-name legacy collision.
Either unreadable source returns `GithubUnavailable`; no check from either source returns `()`; otherwise it
returns the deduplicated tuple. `facts()` calls this edge internally exactly twice: at `job.head_sha`
and at the captured `merge_base_sha`.

### 3.4 E-16 — capability probe

```python
def probe(*, repo: str, credential: str) -> CapabilityReading | GithubUnavailable: ...
```

This is read-only and needs no grant. An unreadable/unauthenticated user endpoint returns
`GithubUnavailable(op="probe", reason="unauthenticated", retriable=False)`; an unreadable repository caused
by transport or rate limit returns the matching retriable `GithubUnavailable`; 403/404 returns the empty
capability reading. Otherwise it derives the proven read and attested write capabilities from GitHub's
repository permissions and returns `CapabilityReading`.

### 3.5 E-23 — one assembled fact capture

```python
def facts(*, job: Job, record: RecordWriter) -> Facts | GithubUnavailable: ...
```

This is the only P-02-facing fact read. It performs one coherent capture: PR representation;
base/merge-base-to-head compare and files; predecessor-head-to-current-head compare when
`job.predecessor_head_sha` exists; head and merge-base checks; submitted reviews; labels. It returns
one shared `Facts`; consumers make no separate fact calls.

1. Job/PR identity mismatch, missing required fields, compare count/path inconsistency, vanished blob,
   malformed review/check timestamps, or malformed response returns `GithubUnavailable`; transport,
   rate-limit and GraphQL failures do likewise. Nothing partial is returned.
2. Read the exact head ref's `branchProtectionRule`; readable null is `False`, unknown is `True`.
3. `changed_paths` is the base compare's complete PR-wide set. `revision_changed_paths` is the exact
   compare from `job.predecessor_head_sha` to `job.head_sha`; without a predecessor it equals
   `changed_paths`. Compare failure fails the whole capture. E-05 alone uses the revision set.
4. Terminal check `observed_at` is GitHub's immutable `completed_at`; unsettled checks use capture time
   but never corroborate or block. Capture submitted APPROVED/CHANGES_REQUESTED reviews with database
   id, actor login, reviewed commit SHA, and immutable submitted time.
5. After all reads complete set UTC `fetched_at`. P-06 later records the evidence cutoff.

## 4. Dependencies consumed

`RecordWriter` and `Entry` are referenced exactly as defined in [`CONTRACTS.md`](CONTRACTS.md) §7;
`Activity` and `Grant` exactly as §8; and `Job` exactly as §1. P-09 imports these types rather than
declaring a local Protocol, partial dataclass, or alternate shape. Every non-terminal write calls the
provided `record.append(job.id, "action", payload)` exactly once, and `AppendFailed` propagates.

**External boundary — E-18 (REST v3 + GraphQL v4).** `https://api.github.com` (REST) and
`https://api.github.com/graphql` (GraphQL v4), both HTTPS, `Authorization: Bearer <credential>`,
`Accept: application/vnd.github+json` (or `application/vnd.github.v3.diff` for the one diff-text read
in §3.5), `X-GitHub-Api-Version` pinned to a fixed value this file owns. The credential on every call
is resolved by this file's own private, per-call `transport._credential()` — a subprocess call to
`gh auth token`, structurally identical to but independent of P-08's E-22 read: E-22 is P-08's, never
this file's, and this file never imports `rqa.authority` to reach it, so P-08 (which calls *into* this
file to probe) is never itself a runtime dependency *of* this file [ADR-E assumed]. The one declared
exception is `probe()` (§3.4), whose `credential` argument the caller (P-08) supplies explicitly, since
P-08 wants to attest the exact value it already read via its own E-22, not trust that this file resolved
the identical one. Nothing this file reads, writes, or resolves ever leaves this process as a stored
value: `transport._credential()`'s return is held in a local variable for the lifetime of one HTTP
call and discarded (U-DOCS-24; test-time guard in §1/§8).

## 5. Store

```sql
CREATE TABLE etags (
  cache_key   TEXT PRIMARY KEY,   -- URL, or "<url>\u0001<accept>" for distinct representations
  etag        TEXT NOT NULL,
  body        TEXT NOT NULL,      -- the cached response body, verbatim
  link        TEXT,               -- the cached Link header, so a 304 does not lose pagination
  updated_at  TEXT NOT NULL
);

CREATE TABLE api_calls (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  called_at   TEXT NOT NULL,
  transport   TEXT NOT NULL,      -- "rest" | "graphql"
  operation   TEXT NOT NULL,      -- the §3 entry point this call served
  status      INTEGER NOT NULL,   -- HTTP status code
  resource    TEXT,               -- X-RateLimit-Resource: "core" | "graphql" | ...
  rate_limit  INTEGER,            -- X-RateLimit-Limit
  remaining   INTEGER,            -- X-RateLimit-Remaining
  used        INTEGER,            -- X-RateLimit-Used
  reset_at    TEXT                -- X-RateLimit-Reset, converted to ISO-8601 UTC
);

CREATE TABLE mutations (
  client_mutation_id TEXT PRIMARY KEY,  -- sha256(job_id, kind, canonical_json(payload))
  job_id      TEXT NOT NULL,
  kind        TEXT NOT NULL,            -- a MutationKind value
  state       TEXT NOT NULL,            -- "completed" | "pending" | "verified" | "uncertain"
  response    TEXT,                     -- JSON, GitHub's own payload; null on a Stale/GithubUnavailable
                                        -- outcome, where no mutation was ever sent
  created_at  TEXT NOT NULL,
  updated_at  TEXT NOT NULL
);
```

```python
class EtagStore(Protocol):
    def get(self, cache_key: str) -> tuple[str, str, str | None] | None: ...  # (etag, body, link)
    def put(self, cache_key: str, etag: str, body: str, link: str | None) -> None: ...

class ApiCallStore(Protocol):
    def record(self, transport: str, operation: str, status: int, headers: Mapping[str, str]) -> None: ...
    # parses X-RateLimit-* from headers; inserts one row; never raises on a missing header

class MutationStore(Protocol):
    def find(self, client_mutation_id: str) -> "MutationRow | None": ...
    def put(self, row: "MutationRow") -> None: ...   # INSERT ... ON CONFLICT DO UPDATE
```

**Read protocol.** `etags`: read before every REST GET, by `cache_key`; written after every REST GET
that returns a fresh (non-304) `ETag`. Read and written only inside `transport.py`; no other module in
this file, and no other part, reads it. `api_calls`: written after **every** call this file makes to
GitHub, REST or GraphQL, successful or not, from response headers alone — never from an estimate. Read
by P-05 directly (a row scan; container.md §5 names P-05 as a reader; no P-09 function serves this —
it is a raw table read of shared local state, the same way `capabilities` is read by P-02). `mutations`:
read before every write, by `client_mutation_id`, for the shared discipline's dedupe check (§3
preamble); written after. Read by no other part.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `action` | every call to `claim_lease`, `release_lease`, `submit_review`, `comment`, `merge` that is not a terminal-cache no-op | `client_mutation_id`, `kind`, `outcome` (`"submitted"\|"stale"\|"unavailable"\|"lease_taken"`), `response` (GitHub's payload, or `null` when refused before any mutation was sent) |

Nothing else in this file appends. `inventory`, `checks`, `probe`, and `facts` are reads with no
record kind of their own; a deduplicated no-op write returns the prior `Mutation` without a second
`action` entry. `AppendFailed` always propagates; a write whose `action` entry could not be written
does not return a value.

## 7. What P-09 does not do

- Does not decide authority. It never calls E-04, never reads `.rqa/config.json`, never interprets
  `snapshot.authority`. A `Grant`'s *correctness* — was this activity actually enabled for this
  repository? — is P-08's alone; this file checks only that one is present and matches.
- Does not attribute a failing check to the pull request or its base. `checks()` returns the same
  canonical vocabulary for a head read and a base read; comparing them by name is P-07's, through E-14.
- Does not decide *when* to call a write, or what a `Stale`/`GithubUnavailable` outcome should make a job do
  next. Those are values; P-02's transition table interprets them.
- Does not retry a network failure or a `Stale` outcome itself. A caller sees the value and decides
  whether a later sweep may retry.
- Does not guarantee exactly-once delivery to GitHub across a process crash between sending a mutation
  and writing its own `mutations` row. GitHub's `clientMutationId` is an echo field the API does not
  deduplicate by; the `mutations` table is the *only* de-duplication boundary this design has, and a
  crash inside that narrow window is a residual risk shared with the estate's own `github_mutate.py`.
- Does not store, log, or persist the credential anywhere. It is resolved fresh, per call, held in a
  local variable for the duration of one HTTP request, and discarded (§4; U-DOCS-24 guard in §8).
- Does not scope or narrow the credential itself. It is the operator's own `gh auth token`; what it can
  reach on a repository outside the configured set is an accepted residual [ADR-E assumed]. This file's
  only contribution to the ceiling is that it never *addresses* a repository outside the configured
  set — every call is repo- or `Grant.repo`-checked against a caller who already confined it there.
- Does not run remediation's git push. This adapter is the REST/GraphQL API only; P-10's git-transport
  work (E-20) shares no code, credential handling, or table with this file.
- Does not carry the estate's `create_issue`, `add_labels`, `request_review`, or `thread_reply` mutation
  kinds. The frozen specification names none of them; `MutationKind` has exactly five members.
- Does not merge, approve, request changes, or comment without a `Grant` for that exact activity, repo,
  and job — `AdapterError` first, every time (§3 preamble, T1/T2).

## 8. Tests that prove it

Each is a unit test against a fake `EtagStore`/`ApiCallStore`/`MutationStore`/`RecordWriter` and a fake
HTTP layer (fixture responses, no network).

| # | Given | Then |
|---|---|---|
| T1 | each of `claim_lease`, `release_lease`, `submit_review`, `comment`, and `merge` is called with `grant=None` | each raises `AdapterError`; zero GitHub calls and zero record appends |
| T2 | each write is called with a wrong activity, repo, or job id in its `Grant` | each raises `AdapterError`; zero GitHub calls and zero record appends |
| T3 | `submit_review` is called twice with identical `(job, state, body)`, the first already terminal | the second returns the byte-identical `Mutation`; zero new GitHub calls and `action` entries |
| T4 | a REST GET repeats with a cached ETag and GitHub returns 304 | the cached body and Link pagination are used; no body re-fetch |
| T5 | every GitHub call has realistic `X-RateLimit-*` headers | one `api_calls` row records the header-derived values, never an estimate |
| T6 | each named and unknown GitHub conclusion plus each legacy status is normalised | exactly one `CheckConclusion`, never an exception; `FAILING={failure,timed_out,action_required}`, `UNSETTLED={pending}`, and `PASSING={success,neutral,skipped,cancelled}`; pending never corroborates or blocks |
| T7 | APPROVE's fresh PR read has a different head | `Stale(reason="head_changed", ...)`; zero GraphQL mutation |
| T8 | APPROVE's post-check is unreadable or lacks the matching visible review | `GithubUnavailable`; no alternate ambiguous result is exposed |
| T9 | `probe` uses a fake transport whose mutation helper raises if invoked | it returns `CapabilityReading`; zero write calls |
| T10 | any read uses `NON_TOKEN_CREDENTIAL` with `raising_socket()` | the socket exception propagates; no live connection completes |
| T11 | `merge` receives GitHub's expected-head mismatch | `Stale(reason="head_changed", ...)`; no separate pre-check REST call |
| T12 | `claim_lease` finds another login | `LeaseTaken(login=...)`; zero mutation |
| T13 | fork head `alice/fork:feature` | protection query targets that exact repository/ref; returned facts retain both values |
| T14 | exact ref is readable with null rule; then missing/error/rate-limit/malformed | first yields `head_protected=False`; every unknown case yields `True` |
| T15 | E-23 succeeds for successor head B after A | Facts contains PR-wide and A→B path sets, check observation times, submitted reviews, files/labels and UTC capture time; malformed/missing compare or review data fails atomically |

## 9. Requirements this part answers for

**Accountable (2).**

- **RQA-FR-029.** Fit criterion: "One repository configured to merge-after-review merges following a
  successful disposition; a second repository configured not to does not, on an otherwise identical
  successful disposition — both directions of the biconditional are exercised, not merely the enabled
  case." `merge()` (§3.2) is the only code in RQA that can produce a merge, and it is unreachable
  without a `Grant(Activity.MERGE)` (§3 preamble, T1/T2) — a grant P-08 issues only when the snapshot's
  per-repository configuration enables it. This file exercises both directions of the biconditional by
  construction: called under a grant, it merges (T-implicit success case); never called (the
  not-configured repository), nothing happens, because nothing here runs unsolicited.
- **RQA-NFR-011.** Fit criterion: "The system's review-lifecycle requirements are demonstrated against
  a GitHub-hosted repository; a system that supports GitHub review as this specification requires
  satisfies this row regardless of whether it also supports a second source-control platform, since
  C8/Non-goal 1 release cross-SCM support as out of scope rather than prohibiting it." This whole file
  is the single, exclusive transport (§1, §4): every review-lifecycle read and write in the other
  twelve parts is demonstrated only through E-01/E-12/E-14/E-16/E-23, all of them GitHub REST v3 and
  GraphQL v4 (E-18). No second transport exists anywhere in this file for a second platform.

**Contributes to (11).**

- **RQA-BR-007** (no duplicated review work across an unchanged revision) — the deterministic
  `client_mutation_id` and the `mutations` dedupe (§3 preamble, §5) are the GitHub-side half of "the
  same effect never repeats"; T3, T13.
- **RQA-BR-009 / RQA-FR-014 / RQA-FR-036** (attribution for a failing signal; inherited checks excluded
  from blocking) — E-23 captures the normalised checks at `head_sha` and `merge_base_sha`; P-07 compares
  those immutable fields, while P-09 supplies the total normalisation and never the classification; T6,
  T15.
- **RQA-FR-021** (resource consumption measured, never estimated) — `api_calls` (§5) records the
  credential's actual, header-reported rate-limit consumption on every single call; T5.
- **RQA-FR-028** (submit APPROVED/CHANGES_REQUESTED when satisfied) — `submit_review()` (§3.2) is the
  mechanism that performs the submission reliably, pre- and post-checked for APPROVE, once P-02 decides
  to call it; T7, T8.
- **RQA-NFR-008** (merge-after-review configurable per repository) — same mechanism as FR-029 above:
  `merge()` executes only under a per-repository `Grant`.
- **RQA-NFR-021** (remediation never force-pushes, merges, or bypasses protection) — E-23 binds
  `Facts.pr.head_repo`, `head_ref`, and fail-closed `head_protected` to the captured PR head, so P-10
  can refuse before constructing a wrong/fork/protected destination; T13, T14.
- **RQA-NFR-024 / RQA-NFR-030** (credential scope floor and ceiling) — `probe()`'s vocabulary and
  `attested_not_proven` split (§3.4) is the exact, minimal evidence P-08 checks a `Grant`'s required
  capability against; T9.
- **RQA-NFR-029** (deny one change's content to an external provider even where the repository allows
  it) — E-23 captures labels in `Facts.pr.labels`, which P-05 receives as a fact and never as an
  instruction.

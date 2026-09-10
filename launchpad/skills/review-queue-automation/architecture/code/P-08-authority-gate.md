# P-08 Authority gate — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). Shared types and every cross-part signature are defined once in
[`CONTRACTS.md`](CONTRACTS.md); this file references them and never redefines them. An agent implementing P-08 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Answer the question *may RQA perform this activity on this
repository, for this job, right now?* — from the pinned snapshot and a proven capability, never from
anything else — and record the answer.

**Depends on.** ADR-E ([#2158](https://github.com/launchpad-26/buzz/issues/2158), assumed) for credentials and ADR-G ([#2160](https://github.com/launchpad-26/buzz/issues/2160), assumed) for remediation categories.

## 1. Modules

```
rqa/authority/
  __init__.py        re-exports: grant, Activity, Grant, Deny, GateError
  activities.py      the closed Activity enum and its capability requirements
  gate.py            grant(): the one entry point
  capability.py      credential resolution (gh auth token) and per-repository probing
  store.py           the `capabilities` table
```

No other module in RQA imports from `rqa.authority` except through `__init__`. No module in
`rqa.authority` imports from any other part except `rqa.record` (to append) and `rqa.github` (to
probe). In particular it never imports `rqa.policy` or `rqa.lifecycle`: the snapshot arrives as an
argument.

## 2. Types

```python
# activities.py
# `Activity` is defined in CONTRACTS.md §1 and re-exported here. REVIEW covers the assignee lease
# claim/release and every read; the other five are the GitHub writes they name.
from rqa.contracts import Activity

# What each activity must be able to do on GitHub for a grant to be possible.
# Probed by capability.probe(); the values are the adapter's capability vocabulary (E-16).
REQUIRED_CAPABILITY: dict[Activity, frozenset[str]] = {
    Activity.REVIEW:          frozenset({"pulls:read", "contents:read", "checks:read", "issues:write"}),  # issues:write = assignee
    Activity.COMMENT:         frozenset({"pulls:write"}),
    Activity.APPROVE:         frozenset({"pulls:write"}),
    Activity.REQUEST_CHANGES: frozenset({"pulls:write"}),
    Activity.REMEDIATE:       frozenset({"contents:write"}),
    Activity.MERGE:           frozenset({"pulls:write", "contents:write"}),
}
```

```python
# gate.py — every boundary value is imported from the seam truth.
from rqa.contracts import Grant, Deny, DenyReason, Category

class GateError(Exception):
    """Programming error: the gate was called wrongly. Policy/capability refusals are Deny values."""
```

`Snapshot` is P-03's type, consumed here read-only. The fields P-08 reads, and the only ones:

```python
snapshot.hash: str
snapshot.repo: str
snapshot.authority: Mapping[Activity, bool]      # all six keys always present after validation
snapshot.policy.mechanical.categories: frozenset[Category]
snapshot.policy.mechanical.tools: frozenset[str]  # tool ids; validated by P-03 against MECHANICAL_TOOL_SET
```

## 3. Entry point — E-04

```python
def grant(*, repo: str, activity: Activity, snapshot: Snapshot | None, job_id: str,
          categories: frozenset[Category] | None, record: RecordWriter, github: GithubProbe,
          store: CapabilityStore) -> Grant | Deny: ...
```

The signature is verbatim. Test clocks are constructor dependencies of the gate implementation, not
additional E-04 parameters.

**Behaviour, in order. Every branch records one `grant` entry and returns.**

1. `repo` not in the configured set → `Deny(REPO_NOT_MANAGED)`. Checked first so the gate can never
   be asked about, let alone answer for, an unmanaged repository.
2. `snapshot is None` → `Deny(NO_SNAPSHOT)`. This is how "a malformed or unreadable policy never widens
   authority" is implemented: no snapshot, no grant, whatever the activity.
3. `snapshot.repo != repo` → raise `GateError`. A programming error, not a policy answer.
4. `activity is REMEDIATE`:
   - `categories is None or not categories` → `Deny(CATEGORY_REQUIRED)`.
   - any category outside `MECHANICAL_GROUP` or outside
     `snapshot.policy.mechanical.categories` → `Deny(CATEGORY_NOT_MECHANICAL)`.
   - any configured tool outside `MECHANICAL_TOOL_SET` → `Deny(TOOL_NOT_IN_SET)`.
5. For another activity, non-`None` categories raise `GateError`.
6. Disabled activity → `Deny(NOT_ENABLED)`.
7. Load/probe the per-job capability proof; missing required capability →
   `Deny(CAPABILITY_MISSING)`.
8. Otherwise return `Grant(..., categories=categories, ...)`.

**Recording.** Every result appends `activity`, `snapshot_hash`, sorted `categories` or null,
capability proof, decision, reason and detail. The returned value carries the entry seq; append
failure propagates.

**Guarantees.**
- Same `(repo, activity, snapshot, categories, proof)` gives the same answer.
- Every call re-reads its supplied snapshot and per-job proof.
- Policy/capability reasons are values; only wrong-shape calls raise `GateError`.
- It reads no configuration/environment itself; the snapshot is the only policy source.
- A `Deny.detail` is sufficient for the authority-requirement escalation.

## 4. Capability — E-16 and E-22

```python
# capability.py
@dataclass(frozen=True)
class CapabilityProof:
    id: int
    repo: str
    job_id: str
    capabilities: frozenset[str]     # adapter vocabulary, e.g. "pulls:write"
    login: str                       # the GitHub login the token belongs to (for the record; never for auth decisions)
    probed_at: datetime
    attested_not_proven: frozenset[str]   # capabilities GitHub reports but the probe could not exercise (ADR-E)

def credential() -> str:
    """E-22. Runs `gh auth token` and returns its stdout, stripped. Raises CredentialGithubUnavailable
    (a GateError subclass) if gh is absent, not logged in, or exits non-zero. The value is held in
    memory for the duration of one probe and never written anywhere — not to the store, not to the
    record, not to logs."""

def probe_capability(repo: str, github: GithubProbe, store: CapabilityStore, job_id: str) -> CapabilityProof:
    """Wraps P-09's E-16 `probe(*, repo, credential) -> CapabilityReading | GithubUnavailable` (CONTRACTS.md §9),
    persists the reading as a CapabilityProof for this job, and returns it. `GithubUnavailable` from the adapter
    is persisted as an empty capability set, so every activity is denied `CAPABILITY_MISSING` until a later
    job re-probes."""

def _probe_signature_for_reference(*, repo: str, credential: str) -> CapabilityReading | GithubUnavailable:
    """E-16. Asks the adapter what the credential can do on `repo`, persists the result for this job,
    returns it. The adapter's probe is read-only against GitHub: it inspects the authenticated
    user's permission level on the repository and the token's reported scopes; it performs no write
    to establish a write capability."""
```

The mapping from GitHub's reported permission (`admin` / `maintain` / `write` / `triage` / `read`)
and token scopes to the capability vocabulary lives in `rqa.github` (P-09), not here: P-08 consumes
the vocabulary, P-09 owns how GitHub expresses it.

## 5. Store

```sql
CREATE TABLE capabilities (
  id            INTEGER PRIMARY KEY,
  repo          TEXT NOT NULL,
  job_id        TEXT NOT NULL,
  capabilities  TEXT NOT NULL,          -- JSON array of strings
  attested      TEXT NOT NULL,          -- JSON array of strings (ADR-E residual)
  login         TEXT NOT NULL,
  probed_at     TEXT NOT NULL,          -- ISO-8601 UTC
  UNIQUE (repo, job_id)
);
```

```python
class CapabilityStore(Protocol):
    def current(self, repo: str, job_id: str) -> CapabilityProof | None: ...
    def put(self, proof: CapabilityProof) -> int: ...   # returns id; UNIQUE violation → replace
```

Written only by P-08. Read by P-02 (to include the proof in escalations) — read-only, through
`current()`.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `grant` | every call to `grant()` | `activity`, `snapshot_hash`, sorted `categories` or null, `capability_proof_id`, `decision`, `reason`, `detail` |
| `attestation` | every `probe()` | `login`, `capabilities`, `attested_not_proven`, `probed_at` — this is where ADR-E's "attested, not proven" residual is written down |

P-08 writes no `transition` and never touches `jobs.status`.

## 7. What P-08 does not do

- Does not read `.rqa/config.json`, the environment, or any file. (Policy is P-03's.)
- Does not decide *whether to ask*: P-02 asks before every action, and P-08 answers. It has no memory
  of previous answers beyond the record.
- Does not perform any GitHub write, including the probe.
- Does not store, log, or return the token.
- Does not know a `Finding`; remediation receives its complete category set and verifies every member.
- Does not escalate. It returns a `Deny`; P-02 decides that a `Deny` becomes an escalation.

## 8. Tests that prove it

Each is a unit test with fakes for `RecordWriter`, `GithubProbe` and `CapabilityStore`.

| # | Given | Then |
|---|---|---|
| T1 | every activity, `snapshot=None` | `Deny(NO_SNAPSHOT)` for all six; one `grant` entry each |
| T2 | snapshot with all six `false` | `Deny(NOT_ENABLED)` for all six |
| T3 | snapshot enabling exactly one activity, proof sufficient | `Grant` for that one, `Deny(NOT_ENABLED)` for the other five — independence (RQA-NFR-017) |
| T4 | activity enabled, proof missing one required capability | `Deny(CAPABILITY_MISSING)` with the missing set in `detail` |
| T5 | `REMEDIATE`, categories missing/empty | `Deny(CATEGORY_REQUIRED)` |
| T6 | any remediation category is substantive or outside configured mechanical categories | `Deny(CATEGORY_NOT_MECHANICAL)` |
| T7 | all categories mechanical/configured but policy names unknown tool | `Deny(TOOL_NOT_IN_SET)` |
| T8 | non-remediation with non-null categories | `GateError` |
| T9 | `snapshot.repo != repo` | `GateError` |
| T10 | repo not configured | `Deny(REPO_NOT_MANAGED)` before any probe; `github.probe` not called |
| T11 | two calls in one job | one probe, second call reads the stored proof |
| T12 | two jobs, same repo | two probes |
| T13 | `record.append` raises `AppendFailed` | exception propagates; no `Grant`/`Deny` returned |
| T14 | `gh auth token` exits non-zero | `CredentialGithubUnavailable`; nothing persisted |
| T15 | same inputs called twice | identical answer; two `grant` entries |
| T16 | full-text search of the token value across store, record and log fixtures after any call | zero occurrences |

Property that must hold across the suite: `grep -rn "authority\[" rqa/ --include=*.py` returns hits
only under `rqa/authority/` and `rqa/policy/` (validation). No other part reads an authority setting.

## 9. Requirements this part answers for

Accountable: RQA-NFR-017, RQA-NFR-018, RQA-NFR-019, RQA-NFR-024, RQA-NFR-025, RQA-NFR-026,
RQA-NFR-030. Each maps to a behaviour above: 017/026 → steps 6 and T3; 018 → step 2 and T1;
019 → step 4 and T5–T7; 024 → step 7 and T4; 025 → §4 `credential()` and T16; 030 → step 1, T10,
and the `attested_not_proven` field (accepted residual, ADR-E).

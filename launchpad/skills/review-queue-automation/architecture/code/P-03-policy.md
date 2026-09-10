# P-03 Policy — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-03 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Turn a repository's `.rqa/config.json` into the one pinned,
content-hashed `Snapshot` a job runs against for its entire lifetime — reading it fresh on every call,
validating it fail-closed against the schema and semantic rules below, deriving the policy as a copy
of what validated (never inventing a wider fallback), and activating it atomically with every
previously activated snapshot kept byte-for-byte intact — and, separately, writing a starter
configuration on `onboard`, never overwriting an operator's file.

**Depends on.** ADR-G ([#2160](https://github.com/launchpad-26/buzz/issues/2160), assumed) for the
closed tool/oracle registry P-03 validates. Its only outbound edge is E-13; P-04 path matching and
shared vocabulary imports are not alternate neighbour contracts.

## 1. Modules

```
rqa/policy/
  __init__.py     re-exports CONTRACTS.md §3's Snapshot, Route, External, Policy, Blocking,
                  Mechanical and Budget, plus snapshot_for, onboard, ValidationError,
                  ValidationErrorCode, ValidationFailure, OnboardResult, Written, OnboardRefusal,
                  OnboardRefusalReason, PolicyError, SnapshotStoreCorrupted
  schema.py       the config JSON schema sketch as data: the allowed/required key sets at every
                  level (§2's normative shape)
  validate.py     validate(): the fail-closed schema+semantic checker (E-03's dependency, not an
                  edge of its own); the one set of default literals both this and onboard.py bind
                  fallbacks to (U-POLICY-05)
  types.py        validation outcomes, internal ValidatedConfig, PolicyError and its subclasses;
                  imports Snapshot and all shared snapshot vocabulary from CONTRACTS.md §3
  snapshot.py     snapshot_for(): the one entry point (E-03) — discovery, live read, validation,
                  canonicalisation, hashing, and orchestration of store.activate()
  store.py        SnapshotStore: the snapshots table plus snapshots/<hash>.json, atomic activation,
                  last-known-good retention (U-QUEUE-09, U-QUEUE-10)
  onboard.py      onboard(): the other entry point (E-17) — starter-config write, --migrate
                  conversion of the old three authority keys, refuse-overwrite, atomic write
```

No other module in RQA imports from `rqa.policy` except through `__init__`. No module in `rqa.policy`
imports from any other part except `rqa.record` (to append, E-13) and `rqa.protocol` for shared
vocabulary (`Obligation`, `Category`, `Snapshot` tree imports, and `protocol_hash()`) plus the one
authoritative `paths.matches` validation call. It imports `rqa.authority` only for `Activity` and
`rqa.remediation` only for `MECHANICAL_TOOL_SET` membership. It never imports `rqa.lifecycle`,
`rqa.github` or `rqa.judgement`: nothing here decides an authority question or interprets a finding.

## 2. Types

**The normative config shape (architecture.md §11, reproduced).** This is what `validate()` checks a
parsed `.rqa/config.json` against; nothing here may drift from it without a version bump the operator
notices at admission.

```
authority:   { review, comment, approve, request_changes, remediate, merge }   each true/false, default false
routes:      ordered list of { harness, model, provider, family, external: bool, command?: [str] },
             first is preferred, rest are fallbacks. `command` is the operator-declared argv for a
             harness RQA ships no alias for; it is REQUIRED for such a route and REJECTED for a
             built-in alias. Each element is a non-empty string; the first is the executable
external:    { allowed: bool, deny_label: "<label>" }
policy:      { version, obligations: [ { id, paths, required_for, evidence } ],
               blocking: { categories, severities, corroboration },
               mechanical: { categories, tools: [ "<tool id from RQA's closed set>" ] },
               assurance: { <risk class>: participants },
               remediation: { allow_forks: bool } }
budget:      { per_pr_tokens, per_repo_daily_tokens, per_model_daily_tokens }
```

Exactly five top-level keys — `authority`, `routes`, `external`, `policy`, `budget` — no more, no
fewer; every one of the five is required (a config that omits `budget` entirely is as invalid as one
naming a sixth top-level key). `policy.obligations[*].id/paths/required_for/evidence` are
`rqa.protocol.Obligation`'s own fields
(P-04 owns the shape); `policy.mechanical.tools[*]` values are tool ids checked against
`rqa.remediation.MECHANICAL_TOOL_SET` (P-10 owns the registry); `policy.remediation` is optional and
defaults to `{"allow_forks": false}`; this file owns validation of everything else in the shape above.

Validation is fail-closed at the shared boundaries: every route entry must contain all five `Route`
fields, including a non-empty `family`; every `policy.mechanical.categories` entry must name a
`Category` and is materialised as `frozenset[Category]`; and, when present, `policy.remediation` has
only the boolean `allow_forks` key. A missing `policy.remediation` is materialised as
`allow_forks=False`; an unknown key or non-boolean value is respectively `UNKNOWN_KEY` or `BAD_TYPE`.

**`Snapshot` and the shared tree it exposes are defined only by
[`CONTRACTS.md`](CONTRACTS.md) §3.** `rqa.policy` imports and returns that exact `Snapshot`; it does
not redefine `Snapshot`, `Route`, `External`, `Policy`, `Blocking`, `Mechanical`, `Budget`, or
`Obligation`. In particular, `Snapshot.routes` is `tuple[Route, ...]`, and
`Snapshot.policy.mechanical.categories` is `frozenset[Category]`. The validator constructs those
shared values after checking the config; it neither substitutes a local configured-route type nor
widens any shared field.

The validator additionally supplies the optional policy detail consumed by P-10:

```python
# This is config validation detail, not a redefinition of the CONTRACTS.md §3 Snapshot tree.
policy.remediation.allow_forks: bool = False
```

```python
# types.py — boundary values come from the seam truth; only the successful intermediate is local.
from rqa.contracts import ValidationErrorCode, ValidationError, ValidationFailure

# Everything a Snapshot needs except hash, repo and protocol_hash. Never crosses a part boundary.
@dataclass(frozen=True)
class ValidatedConfig:
    authority: Mapping[Activity, bool]
    routes: tuple[Route, ...]
    external: External
    policy: Policy
    budget: Budget

class PolicyError(Exception):
    """Programming error: rqa.policy was called wrongly, or its own invariants are broken. Never
    raised for malformed repository configuration — that is a shared ValidationFailure."""

class SnapshotStoreCorrupted(PolicyError):
    """A pinned hash is missing or its archived bytes no longer hash to their own name."""
```

```python
# onboard.py — the onboard() result family
class OnboardRefusalReason(str, Enum):
    ALREADY_EXISTS           = "already_exists"            # plain mode: a config already exists
    NO_CONFIG_TO_MIGRATE     = "no_config_to_migrate"      # --migrate: nothing to convert
    UNREADABLE_EXISTING      = "unreadable_existing"       # --migrate: existing file unreadable/not JSON
    MIGRATED_CONFIG_INVALID  = "migrated_config_invalid"   # --migrate: the converted result fails validate()

@dataclass(frozen=True)
class Written:
    path: str

@dataclass(frozen=True)
class OnboardRefusal:
    reason: OnboardRefusalReason
    detail: str
    errors: tuple[ValidationError, ...] = ()   # populated only for MIGRATED_CONFIG_INVALID

type OnboardResult = Written | OnboardRefusal
```

`Job` is P-01's type, consumed here read-only. The fields P-03 reads, and the only ones:

```python
job.id: str
job.repo: str
job.snapshot_hash: str | None
```

## 3. Entry points — E-03 and E-17

### E-03 — `snapshot_for`

```python
def snapshot_for(*, repo: str, job: Job | None, store: SnapshotStore, record: RecordWriter | None) -> Snapshot | ValidationFailure: ...
```

**Behaviour, in order. Every branch returns a value or raises a named `PolicyError` subclass; nothing here ever calls another part.**

1. `job is not None and job.snapshot_hash is not None` — this job already has a pin. `stored =
   store.get(job.snapshot_hash)`.
   - `stored is None` → raise `SnapshotStoreCorrupted`. A pinned job citing a hash the store cannot
     produce is a data-integrity fault, never a value: it cannot arise from anything a repository's
     config does.
   - Otherwise return `stored.snapshot` built with `repo=repo`. **No live read happens on this
     branch** — this is the whole of "pinned once per job, re-read never" (`components.md` §6, E-03):
     an edited `.rqa/config.json` cannot reach a job that already has a hash, however many more times
     this function is called for it.
2. Otherwise (`job is None` — an admission-time check before any job exists, per
   `flow-review-lifecycle.md` §3 step 1 — or `job.snapshot_hash is None` — this job's first pin): a
   live read, unconditionally, every call, from `<repo's root>/.rqa/config.json`, the path recomputed
   from `repo` on this call and never cached (U-POLICY-01, U-QUEUE-06).
   - The file cannot be opened and read as UTF-8, or does not parse as JSON → `ValidationFailure(repo,
     errors=(ValidationError(UNREADABLE, path="", detail=<why>),))`. No store write, no append.
3. `validated = validate(raw)` (§4 of this file's own `validate.py`, not a part edge).
   - Returns `ValidationFailure` → return it unchanged. Every one of the five documented classes —
     unknown key, missing `policy`, a tool outside `MECHANICAL_TOOL_SET`, an authority key outside the
     six, a negative budget axis — surfaces here, collected together rather than one at a time (§8
     T1–T6). No store write, no append.
   - Returns `ValidatedConfig` → continue.
4. `canonical = json.dumps(raw, sort_keys=True, separators=(",", ":"))` over the **entire** raw config
   — all five sections together, never `policy` alone (U-QUEUE-10: this is what lets one hash answer
   both "did the policy change" and "reproduce exactly what a job ran under"). `digest =
   sha256(canonical.encode()).hexdigest()`.
5. `stored = store.activate(digest, raw, at=utcnow())` (§5). Idempotent: a `digest` already archived —
   by this repo or, since the hash carries no repo, by any other with byte-identical content — is
   returned unchanged, nothing is written twice.
6. Build the shared `Snapshot` exactly as specified by `CONTRACTS.md §3`, using the validated shared
   `Route`, `External`, `Policy`, `Budget`, `Activity`, and `Category` values and
   `protocol_hash()`. No local snapshot-tree type or route conversion is involved.
7. `job is None` → return `snapshot`. Nothing job-scoped exists yet to record against.
8. `job is not None and record is None` → raise `PolicyError("job pin requires RecordWriter")`. A job
   pin without its required durable record is a caller/invariant error, not an operator config result.
9. Otherwise (this job's first pin) →
   `record.append(job.id, kind="snapshot", payload={"hash": digest, "repo": repo, "policy_version":
   validated.policy.version, "protocol_hash": snapshot.protocol_hash, "activated_at":
   stored.activated_at.isoformat()})`. If this raises `AppendFailed`, it propagates: the caller's
   transition fails with it, per E-13; `snapshot_for` never returns a `Snapshot` that was not recorded
   against the job it was pinned for. Otherwise return `snapshot`.

**The caller, not `rqa.policy`, writes `job.snapshot_hash`.** P-03 owns no column of `jobs`; P-02
persists the returned `hash` onto the job row after a successful first pin (`container.md` §5: `jobs`
is written by P-01, `job_state` by P-02). A crash between this function returning and that write means
the next call still lands on branch 2 and produces the same `digest` from the same (still unedited, or
by-then-edited) config — never a different job silently keeping a stale pin, because there was never a
pin to begin with until the write actually lands.

### E-17 — `onboard`

```python
def onboard(
    *,
    repo: str,
    migrate: bool = False,
    clock: Callable[[], datetime] = utcnow,
) -> OnboardResult:
```

**Behaviour, in order. Every branch returns a value or raises; nothing here contacts GitHub, a model,
or a lease (U-POLICY-06).**

1. `migrate is False` (plain onboarding):
   1. `<repo>/.rqa/config.json` already exists → `OnboardRefusal(ALREADY_EXISTS, detail=path)`. The
      existing file is not opened for writing at all (U-POLICY-06: never overwritten, §8 T12).
   2. Build the starter dict from the same literal defaults `validate.py` falls back to for a maximally
      sparse config (U-POLICY-05): all six `authority` keys `false`, `routes: []`, `external:
      {allowed: false, deny_label: ""}`, an inline `policy` with `version: "unversioned"`, empty
      `obligations`, `blocking: {categories: [], severities: [], corroboration: 1}`, `mechanical:
      {categories: [], tools: []}`, `assurance: {}`, `remediation: {allow_forks: false}`, and `budget`
      with all three axes `null`. The generated dict carries every section — in particular an inline
      `policy`, because `snapshot_for` is fail-closed on a missing one (step 3 above) and a starter
      without one would leave every job the operator later runs unpinned.
   3. `validate(starter)` — must succeed, since generator and validator share one literal source
      (`validate.py`'s defaults, §1). A `ValidationFailure` here is `raise PolicyError(...)`: the
      generator producing a config its own validator rejects is this module's own bug, never an
      operator-visible outcome.
   4. Atomic write (temp file inside `.rqa/`, `fsync`, rename onto `config.json`; U-RESILIENCE-14's
      mechanism) → `Written(path)`.
2. `migrate is True` (converting an existing old-shape config, architecture.md §14):
   1. No file exists at `<repo>/.rqa/config.json` → `OnboardRefusal(NO_CONFIG_TO_MIGRATE,
      detail=path)`. Nothing written.
   2. The file exists but cannot be opened as UTF-8 or does not parse as JSON →
      `OnboardRefusal(UNREADABLE_EXISTING, detail=<why>)`. Nothing written.
   3. `migrated = migrate_config(old)` (below) — a pure transform, no validation yet.
   4. `validate(migrated)`.
      - `ValidationFailure` → `OnboardRefusal(MIGRATED_CONFIG_INVALID, detail="migrated config is
        invalid", errors=failure.errors)`. **The original file on disk is untouched** — validated
        before any write is attempted, never write-then-repair (U-POLICY-06's rework finding: a
        backup-and-restore discipline is not needed when nothing is written until validation passes).
      - Valid → atomic write (same mechanism as 1.4, same destination) → `Written(path)`.

**`migrate_config(old: Mapping) -> dict`, this file's defined mapping (architecture.md §14,
`container.md` §5's `config` row).** A pure function, no side effects:

- `authority`: built fresh as the six-key model. `review = bool(old.get("authority", {}).get("review",
  False))`; `remediate = bool(old.get("authority", {}).get("fix", False))`; `comment = approve =
  request_changes = merge = False` — nothing in the old shape names any of these four, and "everything
  not previously live is false" (architecture.md §14) is exactly this. The old `authority.triage` key,
  if present, is read and discarded: the lane it gated is not carried forward at all, by any name.
- Every notification-transport key and the retention-window key, wherever nested, are dropped
  (`container.md` §5: "four key groups removed").
- `budget.per_model_daily_tokens`, if present, is carried through unchanged — it is retained and is now
  enforced (architecture.md §14), never re-derived.
- Every other key present in `old` — `routes`, `external`, `policy`, and any `budget` axis besides the
  one named above — is copied through unchanged. A leftover key `validate()` no longer recognises
  (for example a fifth `authority` key this mapping does not name) is not repaired here: it surfaces as
  `MIGRATED_CONFIG_INVALID` in step 2.4, which is the fail-closed answer to a config this mapping does
  not fully know how to convert.

## 4. Dependencies consumed

**`Obligation`, `Category`, `matches()`, and `protocol_hash()`, owned by P-04.** Consumed as shared
vocabulary and P-04's one path-matcher. `Obligation`'s fields (`id`, `paths`, `required_for`,
`evidence`) are structurally validated by `rqa.policy.validate`. For every string in
`policy.obligations[*].paths`, validation calls only
`rqa.protocol.paths.matches(path, pattern)` to parse and validate `pattern`; an invalid pattern is
collected as `ValidationError(INVALID_PATH_PATTERN, path=<indexed config path>, detail=<matcher
error>)`. P-03 defines no glob semantics, uses neither `fnmatch` nor `PurePath.match`, and does not
otherwise interpret `paths`. Risk-class names in `required_for` remain P-04/P-07 business.

**`Activity`, owned by P-08.** Consumed as a value only, to key `Snapshot.authority`. `rqa.policy`
never calls `grant()` and never imports anything else from `rqa.authority`.

**`MECHANICAL_TOOL_SET`, owned by P-10 `[ADR-G assumed]`.** A `Mapping[str, ToolSpec]`; `rqa.policy`
only tests membership (`tool_id in MECHANICAL_TOOL_SET`) when validating `policy.mechanical.tools` —
it never reads a `ToolSpec`'s `fix_argv`/`check_argv` and never runs a tool. P-08 checks the same
membership again independently when granting `remediate` (`code/P-08-authority-gate.md` §3 step 4),
and P-10 checks it a third time before running anything (`code/P-10-remediation.md` §3 step 2):
belt-and-braces on all three sides of a decision no single check may be trusted alone to have made
correctly.

**`RecordWriter.append`, owned by P-12 (E-13).** Its sole definition is
[`CONTRACTS.md`](CONTRACTS.md) §7. `AppendFailed` always propagates (§3).

## 5. Store

```sql
CREATE TABLE snapshots (
  hash            TEXT PRIMARY KEY,     -- sha256 hex digest over the entire canonical config
  repo            TEXT NOT NULL,        -- the repo of first activation; informational, not a key
  policy_version  TEXT NOT NULL,
  protocol_hash   TEXT NOT NULL,
  activated_at    TEXT NOT NULL,        -- ISO-8601 UTC, first time this hash was ever seen
  path            TEXT NOT NULL         -- "snapshots/<hash>.json", relative to the state directory
);
```

```python
# store.py
@dataclass(frozen=True)
class StoredSnapshot:
    snapshot: Snapshot           # repo is a placeholder ("") here; snapshot_for() rebuilds it with
                                 # the caller's own repo before returning
    activated_at: datetime

class SnapshotStore(Protocol):
    def get(self, hash: str) -> StoredSnapshot | None: ...
    def activate(self, hash: str, raw: Mapping[str, Any], at: datetime) -> StoredSnapshot: ...
```

**Read protocol.** `get(hash)`: if no row exists for `hash`, return `None`. Otherwise read
`snapshots/<hash>.json`, recompute its SHA-256 over its own bytes, and compare against `hash` — a
mismatch (a truncated or externally damaged file) raises `SnapshotStoreCorrupted` rather than returning
a value; a snapshot whose bytes cannot be trusted is not a policy answer, it is a data-integrity fault.
On a match, parse the JSON, rebuild the full `Snapshot`, and return it wrapped in `StoredSnapshot`.

**Activation protocol (`activate`), atomic and crash-safe (U-QUEUE-09, U-QUEUE-10).**

1. `get(hash)` already returns a row → return it unchanged. Content-addressed: identical bytes never
   get a second archive or a second row, whichever repository or job first produced them.
2. Otherwise, **archive before pointer**: write the canonical JSON to a temp file inside
   `snapshots/`, `fsync`, then atomically rename it onto `snapshots/<hash>.json` (U-RESILIENCE-14's
   mechanism). Only once that file exists complete-or-not-at-all does step 3 run.
3. Insert the `snapshots` row referencing `hash`.

If the process is interrupted between steps 2 and 3, the archived file is already complete and
byte-for-byte correct; the next call to `snapshot_for` for the same config produces the same `hash`
and step 1 above will find no row yet, so it repeats step 2 (a no-op rewrite of identical bytes) and
completes step 3 — nothing is ever left half-written, and nothing already active is ever touched.
**Last-known-good retention** is exactly this: no snapshot file or row is ever deleted, updated in
place, or superseded by activating a different hash — a job pinned to an older hash keeps reading it,
unaffected by every activation that happens after it, for the life of the state directory
(`architecture.md` §10: "immutable once written").

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `snapshot` | the call to `snapshot_for` that performs a job's first pin (E-03 §3 step 8) — never on an admission-time call with `job=None`, and never again for a job that already has one | `hash`, `repo`, `policy_version`, `protocol_hash`, `activated_at` |

`onboard` writes no record entry: it runs before any job exists and has no `job_id` to write against
(`components.md` §6, E-17: an operator CLI command, not a job-scoped decision).

## 7. What it does not do

- Does not decide whether a finding blocks, corroborates, or what any member of its category set
  means at judgement time. It validates and pins policy content; P-07 interprets it.
- Does not call P-08, P-05, P-06, P-07, P-09 or any other part. Its only outbound call, ever, is
  `record.append`.
- Does not write `jobs.status` or `jobs.snapshot_hash`. Those columns belong to P-01/P-02; P-03 hands
  back a `hash` and never touches the `jobs` table itself.
- Does not fall back to an older snapshot when a live read is invalid. An invalid config is a
  `ValidationFailure`; the repository is refused outright at admission (`architecture.md` §4, §12), it
  is never silently served its last-known-good policy instead. "Last-known-good retention" (§5) means
  only that a snapshot already pinned to an in-flight job stays readable forever, never that a broken
  edit is quietly ignored in favour of an earlier one.
- Does not probe, hold or read any credential. `gh auth token` is P-08's concern (E-22) exclusively.
- Does not run a mechanical tool or decide a finding's remedy is safe to run; it only checks that a
  configured tool id is a member of `MECHANICAL_TOOL_SET` (§4). Running it is P-10's.
- Does not validate an obligation's semantic correctness against the protocol beyond its structural
  shape and whether each `paths` entry is accepted by `rqa.protocol.paths.matches`; whether a
  `required_for` value names a risk class anything else recognises is not re-checked here.
- Does not send a notification, contact GitHub, or hold a lease. `onboard` writes exactly one file, or
  none.
- Does not cache a live-read result across calls or across ticks; every call that reaches §3 E-03
  step 2 re-reads the file from disk.

## 8. Tests that prove it

Each is a unit test with a fake `SnapshotStore` and `RecordWriter`, and a real filesystem fixture for
`.rqa/config.json` (or an in-memory path substitute).

| # | Given | Then |
|---|---|---|
| T1 | a config with a top-level key the schema does not name (e.g. `"webhooks"`) | `ValidationFailure` with one `UNKNOWN_KEY` error naming `webhooks` |
| T2 | a config with no `policy` key at all | `ValidationFailure` with exactly one `MISSING_POLICY` error — no deeper `policy.*` errors are produced, since there is no `policy` section to check |
| T3 | a valid-shaped config whose `policy.mechanical.tools` names an id outside `MECHANICAL_TOOL_SET` | `ValidationFailure` with one `TOOL_NOT_IN_SET` error naming the offending id |
| T4 | a config whose `authority` object has a seventh key (e.g. `"triage"`) alongside the six | `ValidationFailure` with one `UNKNOWN_AUTHORITY_KEY` error naming `triage` |
| T5 | a config with `budget.per_repo_daily_tokens: -1` | `ValidationFailure` with one `NEGATIVE_BUDGET` error naming that axis |
| T6 | a config with both an unknown top-level key and a negative budget axis | `ValidationFailure` with **both** errors present — proves "every error", not fail-fast on the first |
| T7 | valid configs whose `policy.mechanical.categories` contain `Category.MECHANICAL` and whose route entries contain every shared `Route` field including `family` | each returned `Snapshot` is the `CONTRACTS.md §3` tree: its routes are `tuple[Route, ...]` and its mechanical categories are `frozenset[Category]`, not local configured-route or string-set values |
| T8 | one repo with `external.allowed: true`, a second with `external.allowed: false`, from one running process | each repo's `Snapshot.external.allowed` matches its own config — RQA-NFR-013, RQA-NFR-023 |
| T9 | `snapshot_for(repo, job=None, ...)` called twice with no edit to the file between calls | identical `Snapshot`, identical `hash`, both times — no admission-time caching artefact, just a stable read |
| T10 | `snapshot_for(repo, job=None, ...)` called, the config edited on disk, then called again | the second call's `Snapshot` and `hash` reflect the edit — proves live re-read, no in-process memoisation (U-QUEUE-06) — this is RQA-FR-004/RQA-NFR-005's "next review" boundary |
| T11 | `job.snapshot_hash is None`; `snapshot_for` returns `hash=H1`; the caller sets `job.snapshot_hash = H1`; the config is then edited on disk; `snapshot_for` is called again with the same `job` | the second call returns branch 1 (§3): the exact `H1` payload, unaffected by the edit — the pin holds for the job's lifetime even though a live read right now would differ |
| T12 | `job.snapshot_hash` set to a hash the fake `store.get` reports as missing | `SnapshotStoreCorrupted` raised, never a `ValidationFailure` |
| T13 | `store.activate` simulated to raise after step 2 (file written) but before step 3 (row inserted) | the archived file is present, complete and correctly hashed; a retried `snapshot_for` call with the identical config reaches the same `hash` and completes activation on the retry |
| T14 | two repositories whose configs are byte-identical after canonicalisation | both produce the same `hash`; the store archives and inserts a row for it exactly once |
| T15 | `record.append` raises `AppendFailed` on a job's first pin | the exception propagates; no `Snapshot` is returned; the store has already been activated (idempotent, harmless) but no `snapshot` record entry exists |
| T16 | a job whose `snapshot_hash` is already set, called twice more | zero further `record.append` calls — the append happens only on the first pin (§6) |
| T17 | `snapshot_for` receives a first-pin `job` and `record=None` | `PolicyError` is raised; no unrecorded job snapshot is returned |
| T18 | a config whose `policy.obligations[0].paths[0]` is rejected by `rqa.protocol.paths.matches` | `ValidationFailure` contains `INVALID_PATH_PATTERN` at that indexed config path; P-03 uses no matcher of its own |
| T19 | a valid config omits `policy.remediation` | the returned snapshot policy has `remediation.allow_forks is False` |
| T20 | a valid config sets `policy.remediation.allow_forks: true` | the returned snapshot policy preserves `allow_forks is True` |
| T21 | a config sets `policy.remediation.allow_forks` to a non-boolean or gives `policy.remediation` an additional key | `ValidationFailure` contains respectively `BAD_TYPE` or `UNKNOWN_KEY` at the remediation path |
| T22 | `onboard(repo)` on a repo with no existing `.rqa/config.json` | `Written(path)`; the file re-read through `validate()` produces zero errors; all six `authority` values are `false`; `routes == ()`; `policy.remediation.allow_forks is False` |
| T23 | `onboard(repo)` on a repo where `.rqa/config.json` already exists | `OnboardRefusal(ALREADY_EXISTS)`; the file's bytes on disk are unchanged (compared before/after) |
| T24 | `onboard(repo, migrate=True)` on an old-shape config with `authority: {review: true, fix: true, triage: true}`, a `notifications` block, a `retention` key, and `budget.per_model_daily_tokens: 500` | `Written(path)`; the migrated file's `authority` is exactly `{review: true, comment: false, approve: false, request_changes: false, remediate: true, merge: false}`; no `notifications` or `retention` key remains; `budget.per_model_daily_tokens == 500`; re-validating the written file produces zero errors |
| T25 | `onboard(repo, migrate=True)` on a repo with no existing config | `OnboardRefusal(NO_CONFIG_TO_MIGRATE)`; nothing written |
| T26 | `onboard(repo, migrate=True)` where the old config, after conversion, still has a key `validate()` rejects | `OnboardRefusal(MIGRATED_CONFIG_INVALID)` naming that error; the original file's bytes on disk are unchanged |

## 9. Requirements this part answers for

Accountable: RQA-FR-003, RQA-FR-004, RQA-NFR-005, RQA-NFR-008, RQA-NFR-013, RQA-NFR-023.

- **RQA-FR-003** — fit criterion: "The same diff submitted under two differently configured repository
  policies produces two blocking outcomes, and the difference is attributable to the policy
  configuration." P-03 is what makes the difference attributable at all: each repo's `policy` section
  is read, validated and pinned exactly as that repo wrote it, never merged with or defaulted from
  another repo's (§3 E-03 step 2–3; T1–T6 prove faithful, per-repo rejection; T7–T8 prove two repos'
  results never leak into each other).
- **RQA-FR-004** — fit criterion: "After a policy configuration change, the very next review on that
  repository reflects the new policy without any build, install or deployment step having been
  performed in between." §3 E-03 step 2 re-reads the file, unconditionally, on every call that is not
  branch 1's cached pin; T10 is the direct proof, T11 is its necessary complement (an *already-pinned*
  job must not see the edit, or "next review" would have no boundary at all).
- **RQA-NFR-005** — fit criterion: "A policy or configuration change is applied and takes effect
  without any build or deployment step being run." Same mechanism as RQA-FR-004: a plain file read, no
  process restart, no cache invalidation step of any kind (§3 E-03 step 2; T10).
- **RQA-NFR-008** — fit criterion: "Two repositories can independently be set to merge-after-review or
  not, and each behaves as configured." P-03 parses and validates `authority.merge` as one of the six
  independent activity keys and carries it, per repo, into `Snapshot.authority[Activity.MERGE]` (§2
  Types, §3 E-03 step 3/6); T7 proves independence directly.
- **RQA-NFR-013** — fit criterion: "An operator can select, per repository, a review path that avoids
  sending that repository's content to an external provider, distinct from one that permits it." P-03
  parses and validates `external.allowed` per repo into `Snapshot.external.allowed` (§2 Types); T8
  proves two repos differ independently.
- **RQA-NFR-023** — fit criterion: "Configuring one repository to permit external-provider sends and a
  second to forbid it produces different sending behaviour on each, from one shared installation."
  Same mechanism and same test as RQA-NFR-013 — one process, `Snapshot.external` differing per repo
  because the underlying config differs per repo, never a process-wide flag (§3 E-03 step 3/6; T8).

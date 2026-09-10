# P-05 Reviewer supply — code-level contract

This is the implementation contract for one part of the design in
[`../architecture.md`](../architecture.md). An agent implementing P-05 builds exactly what is here;
an agent implementing a neighbour calls exactly what is here. Anything not stated is the implementer's
choice, provided the stated shape, behaviour and tests hold. Contract ids (`E-NN`) and record names
are those of [`../components.md`](../components.md) §6 and [`../container.md`](../container.md) §5.

**Responsibility, in one sentence.** Decide *which configured route may run next, and how much of a
configured budget may be spent before it does* — walking only the ladder the operator configured,
respecting every axis inclusively, and telling a measured cost apart from an estimate — never from
anything else.

**Depends on.** No ADR: none of the four accepted drafts (D, E, F, G) governs routing, budget or
breaker behaviour. No other part's internals.

## 1. Modules

```
rqa/supply/
  __init__.py     re-exports: route, reserve, consumed, Route, RouteCursor, Reservation, Refusal,
                  RouteUnavailable, Spend
  aliases.py      the closed alias registry: every recognised (harness, model) pair and its
                  subscription tier (U-POLICY-11)
  ladder.py       candidate filtering and the subscription-first sort shared by route() and
                  reserve(); route(): the ladder walk and probe (E-06, E-24)
  breakers.py     the `providers` cooldown table and the `circuit_breakers` family breaker
                  (U-RESILIENCE-02)
  budget.py       reserve(): per-axis inclusive bound checking against the spend store (E-06)
  spend.py        consumed(): the spend store and the `spend` record entry (E-15)
  probe.py        HarnessProber: the E-24 liveness-probe adapter
```

No other module in RQA imports from `rqa.supply` except through `__init__`. No module in `rqa.supply`
imports from any other part except `rqa.record` (to append) and, inside `probe.py` only, the process
primitive that spawns the harness named by a route's `harness` field (E-24; no network, no repository
content — the probe carries no PR-derived byte). In particular it never imports `rqa.lifecycle`,
`rqa.policy`, `rqa.harness` or `rqa.judgement`: `job`, `plan`, `facts` and `snapshot` all arrive as
arguments, exactly as they do for P-08's `grant()`.

## 2. Types

All shared types used or provided by P-05 — `Route`, `RouteCursor`, `Reservation`, `Refusal`,
`RouteUnavailable`, and `Spend` — are defined only in [`CONTRACTS.md`](CONTRACTS.md) §5 and are used
verbatim here. `RouteCursor` is opaque to the caller: P-05 reads its exclusions, while P-06 advances
it after a failed or refused attempt as specified in §3.1.

```python
# breakers.py — internal only, not a shared-contract type
@dataclass(frozen=True)
class BreakerState:
    scope: str                      # a provider family, e.g. "anthropic"
    failures: int
    status: Literal["closed", "open"]
    open_until: datetime | None     # set only while status == "open"

class SupplyError(Exception):
    """Programming or storage fault inside P-05 — a SpendStore/BreakerStore read or write that
    itself fails, or an internal invariant violation. Never raised for a policy, availability or
    budget reason; those are shared-contract values. Not caught by Lifecycle's containment boundary."""
```


Foreign types, consumed here read-only. The fields P-05 reads, and the only ones:

```python
job.id            # str — used as the record entry's job_id and the spend row's job_id
job.repo          # str — per_pr_tokens and per_repo_daily_tokens scope
job.number        # int — per_pr_tokens scope

plan.participants # int — sizes the reservation; nothing else on Plan is read

snapshot.routes                        # tuple[Route, ...] — the configured ladder, in order
snapshot.external.allowed              # bool
snapshot.external.deny_label           # str
snapshot.budget.per_pr_tokens          # int | None
snapshot.budget.per_repo_daily_tokens  # int | None
snapshot.budget.per_model_daily_tokens # int | None

facts.pr.labels    # frozenset[str] — read once, compared by value, never parsed as instructions

attempt.id         # str — spend row / record payload correlation
attempt.route      # Route — whose .model/.provider/.family drive the spend row and breaker update
attempt.outcome    # Verdict | AttemptFailure — inspected only to classify "succeeded" vs
                   # "PROVIDER_TERMINAL" vs "everything else" for the breaker; never opened further
```

## 3. Entry points

### 3.1 `route()` — E-06

```python

def route(*, job: Job, obligation: str, snapshot: Snapshot, facts: Facts, cursor: RouteCursor,
          prober: HarnessProber, breakers: BreakerStore) -> tuple[Route, RouteCursor] | RouteUnavailable: ...
```


**Behaviour, in order.**

1. `may_send_external = snapshot.external.allowed and snapshot.external.deny_label not in
   facts.pr.labels`. Computed once; `facts.pr.labels` is read as data and compared for membership only
   (RQA-NFR-027, RQA-NFR-029).
2. Build `eligible`: walk `snapshot.routes` in configured order and keep a `candidate` only if **all**
   hold: not (`candidate.external` and not `may_send_external`); `candidate.family not in
   cursor.excluded_families`; `candidate not in cursor.excluded_routes`; and
   **either** `(candidate.harness, candidate.model)` is a key of the alias registry (`aliases.py`)
   **or** `candidate.command` is non-empty. Eligibility here is not admission to invocation: P-06
   §3.2 step 2 runs the conformance pair against that argv before any PR content reaches it, and
   excludes the route through the cursor if it fails. The second disjunct is what RQA-FR-030 requires: a
   conforming harness RQA ships no alias for participates because the operator configured its argv,
   not because RQA's source was edited (AC15). A candidate failing every test is dropped silently
   here — never probed, never returned (RQA-FR-024, RQA-NFR-009): P-05 hands out only routes the
   operator configured, never a nearby substitute, and an operator-declared route is configured.
3. Stable-sort `eligible` by the registry entry's `subscription` flag, `True` before `False`,
   preserving each tier's configured relative order (U-RESILIENCE-03, U-POLICY-14).
4. `tried: list[Route] = []`.
5. For each `candidate` in the sorted `eligible` list, in order:
   a. `key = route_key(candidate)` (`f"{harness}:{provider}:{model}"`). If
      `breakers.cooldown(key)` is not `None` and greater than `utcnow()` → still cooling down from a
      recent probe failure; continue to the next candidate, `tried` unchanged.
   b. `state = breakers.breaker(candidate.family)`. If `state.status == "open"` and
      `state.open_until` is not `None` and greater than `utcnow()` → this family's breaker is open;
      continue to the next candidate, `tried` unchanged.
   c. Append `candidate` to `tried`.
   d. `alive = prober.probe(candidate, timeout=PROBE_TIMEOUT_SECONDS)` (E-24).
      - `alive` is `True` → `breakers.set_cooldown(key, until=None, error="")`; **return**
        `(candidate, RouteCursor(excluded_families=cursor.excluded_families,
        excluded_routes=cursor.excluded_routes | frozenset({candidate})))`.
      - `alive` is `False` → `breakers.set_cooldown(key, until=utcnow() + PROBE_COOLDOWN,
        error="probe failed")`; continue to the next candidate.
6. The loop exhausts without a step-5d success — whether `snapshot.routes` was empty, every candidate
   was filtered at step 2, every remaining candidate was cooling down or breaker-open, or every probed
   candidate's probe failed — **return** `RouteUnavailable(no_fallback=True, tried=tuple(tried))`
   (RQA-FR-023's continuation happens inside this same loop, at step 5's "continue"; exhaustion is
   this one terminal branch, RQA-FR-038).

The returned cursor always excludes the returned route. Thus, passing that cursor back to `route()`
returns a different route or `RouteUnavailable`; its excluded-route set is monotonically growing. Every
branch of `route()` returns; none raises for a routing or availability reason. `route()` never calls
`record.append` — see §6.

### 3.2 `reserve()` — E-06

```python
def reserve(*, job: Job, plan: Plan, route: Route, snapshot: Snapshot, spend: SpendStore) -> Reservation | Refusal: ...
```


```python
TOKENS_PER_PARTICIPANT: int = 150_000     # generous but finite, per-attempt reservation ceiling
ROLLING_WINDOW = timedelta(hours=24)       # both daily axes; not a UTC calendar-day boundary
```

**Behaviour, in order.**

1. `tokens = plan.participants * TOKENS_PER_PARTICIPANT`. A fixed, conservative per-attempt ceiling
   (`budget.py`'s own constant; operator-tunable in a real deployment, fixed here) — not a promise that
   the panel will spend this much, an upper bound it must not exceed (U-DISPATCH-12).
2. `window_start = utcnow() - ROLLING_WINDOW` (a rolling 24-hour window for both daily axes).
3. **`per_pr_tokens` axis.** If `snapshot.budget.per_pr_tokens is not None`:
   `already = spend.pr_total(job.repo, job.number)`. If `already + tokens >=
   snapshot.budget.per_pr_tokens` → **return** `Refusal(downgrade="incomplete",
   axis="per_pr_tokens")`. No model on the ladder has its own separate PR-scoped budget, so no
   fallback route escapes this bound.
4. **`per_repo_daily_tokens` axis.** If `snapshot.budget.per_repo_daily_tokens is not None`:
   `already = spend.repo_total_since(job.repo, window_start)`. If `already + tokens >=
   snapshot.budget.per_repo_daily_tokens` → **return** `Refusal(downgrade="incomplete",
   axis="per_repo_daily_tokens")`. Same reasoning: repo-scoped, shared by every model.
5. **`per_model_daily_tokens` axis.** If `snapshot.budget.per_model_daily_tokens is not None`:
   `already = spend.model_total_since(route.model, window_start)`. If `already + tokens >=
   snapshot.budget.per_model_daily_tokens` → **return** `Refusal(downgrade="fallback",
   axis="per_model_daily_tokens")`. Unlike the other two axes, a different configured route has a
   separate model cap, so P-06 advances the cursor past `route.family` before asking `route()` again.
6. Every checked axis passed (an axis whose bound is `None` is never checked) → **return**
   `Reservation(id=new_reservation_id(), tokens=tokens)`.

Every branch returns. `reserve()` raises only `SupplyError` if `spend` itself fails to answer a
counter query — a storage fault, never a budget decision.

### 3.3 `consumed()` — E-15

```python
def consumed(*, job: Job, attempt: Attempt, reading: int | None, reservation: Reservation,
             record: RecordWriter, spend: SpendStore, breakers: BreakerStore) -> Spend: ...
```


**Behaviour, in order.**

1. `measured = reading is not None`; `tokens = reading if measured else reservation.tokens`;
   `source = "harness" if measured else "reservation"`. This is the entire measured/estimated
   decision (RQA-FR-021): an exposed actual reading always wins; the reservation's token ceiling
   stands in only when none was exposed, and is always marked `estimated`, never conflated with a
   measurement (U-DISPATCH-13).
2. `record.append(job.id, kind="spend", payload={"tokens": tokens, "measured": measured, "source":
   source, "model": attempt.route.model, "provider": attempt.route.provider, "repo": job.repo,
   "number": job.number, "attempt_id": attempt.id, "reservation_id": reservation.id})`. If this
   **raises** `AppendFailed` → propagate uncaught; nothing below runs — no local counter is updated
   and no breaker is touched for an attempt whose cost the durable record does not hold (E-13's
   contract: `AppendFailed` always propagates).
3. `spend.append(job_id=job.id, repo=job.repo, number=job.number, model=attempt.route.model,
   tokens=tokens, measured=measured, source=source, recorded_at=utcnow())` — the local projection,
   updated only after the authoritative append has already succeeded.
4. Update the family breaker from `attempt.outcome`:
   - `attempt.outcome` is an `AttemptFailure` with `.kind == "PROVIDER_TERMINAL"` →
     `breakers.record_failure(attempt.route.family, attempt.outcome.detail)`.
   - `attempt.outcome` is a `Verdict` → `breakers.record_success(attempt.route.family)`.
   - `attempt.outcome` is an `AttemptFailure` with `.kind` `"TRANSIENT"` or `"CANDIDATE_TERMINAL"` →
     no breaker call; neither reflects on the *provider's* health (§7).
5. **Return** `Spend(tokens=tokens, measured=measured, source=source)`.

Every branch returns or (step 2 only) raises; the raise is the one exception this contract names as
always propagating.

## 4. Harness probe — E-24

```python
PROBE_TIMEOUT_SECONDS: float = 300     # matches the real invocation's own timeout: a cold container
                                        # or a cold model can legitimately take this long to answer
PROBE_COOLDOWN = timedelta(seconds=300)  # `providers` cooldown set on a failed probe
```

`HarnessProber` is defined only in [`CONTRACTS.md`](CONTRACTS.md) §9 (E-24) and is consumed here
verbatim.

E-24's published shape (components.md §6, and E-19's interaction contract): the harness named by
`route.harness` is invoked with an **empty** bundle directory and a probe marker file in its place —
no PR content, no protocol definition, nothing to review — and the call is judged on exactly two
things: the process exits `0`, and no `verdict.json` is written to the (empty) output path. Both hold
→ `probe()` returns `True`. Either fails — non-zero exit, a verdict written despite the marker
(a harness that does not honour E-19's published contract), or the process exceeding `timeout` →
`probe()` returns `False`. `route()` never inspects *why* a probe failed: a slow, crashing or
non-compliant harness is unavailable exactly like an absent one (U-POLICY-13's reasoning for probing
through the real transport rather than a cheaper liveness check applies unchanged: a ping or a
credential check would pass for a harness that then cannot produce a schema-valid verdict, which is
not the question a routing decision needs answered).

`probe()` touches no GitHub API and sends no repository content — the marker directory is the entire
input. It never raises for a transport reason; only a genuine implementer bug (invoking a
`route.harness` value the alias registry in `route()` step 2 should already have excluded) is a
programming error and is not this contract's concern to enumerate further.

## 5. Store

**`spend`** — a flat, append-only projection of every `consumed()` call, one row per call (mirroring
the `spend` record entry it is written alongside, per container.md §5's "rows carried via
`record_entries`"). It exists so the three budget axes can be summed locally without re-scanning the
hash-chained record on every `reserve()` call.

```sql
CREATE TABLE IF NOT EXISTS spend (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  job_id      TEXT NOT NULL,
  repo        TEXT NOT NULL,
  number      INTEGER NOT NULL,
  model       TEXT NOT NULL,
  tokens      INTEGER NOT NULL,
  measured    INTEGER NOT NULL,       -- 0 or 1
  source      TEXT NOT NULL,          -- "harness" | "reservation"
  recorded_at TEXT NOT NULL           -- ISO-8601 UTC
);
CREATE INDEX IF NOT EXISTS spend_by_pr        ON spend(repo, number);
CREATE INDEX IF NOT EXISTS spend_by_repo_time ON spend(repo, recorded_at);
CREATE INDEX IF NOT EXISTS spend_by_model_time ON spend(model, recorded_at);
```

```python
class SpendStore(Protocol):
    def pr_total(self, repo: str, number: int) -> int: ...
    def repo_total_since(self, repo: str, since: datetime) -> int: ...
    def model_total_since(self, model: str, since: datetime) -> int: ...
    def append(self, *, job_id: str, repo: str, number: int, model: str, tokens: int,
               measured: bool, source: str, recorded_at: datetime) -> None: ...
```

**`breakers`** — two tables, carried unchanged in shape from the incumbent (U-DISPATCH-05's
"providers" and "circuit_breakers"), scoped differently on purpose: `providers` is a short, exact-route
cooldown driven by probe outcomes; `circuit_breakers` is a coarser, escalating per-family breaker
driven by attempt outcomes (§3.3 step 4). No row in either table is ever deleted or reset by an
operator command — see §7.

```python
FAILURE_THRESHOLD: int = 3               # consecutive PROVIDER_TERMINAL failures before a family opens
BREAKER_COOLDOWN = timedelta(seconds=900)  # matches the incumbent's default exactly (carried unchanged)
```

```sql
CREATE TABLE IF NOT EXISTS providers (
  key               TEXT PRIMARY KEY,     -- f"{harness}:{provider}:{model}"
  unavailable_until TEXT,                 -- ISO-8601 UTC; NULL/empty = no active cooldown
  last_error        TEXT,
  updated_at        TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS circuit_breakers (
  scope       TEXT PRIMARY KEY,           -- a provider family, e.g. "anthropic"
  failures    INTEGER NOT NULL DEFAULT 0,
  status      TEXT NOT NULL DEFAULT 'closed',   -- 'closed' | 'open'
  open_until  TEXT,                       -- ISO-8601 UTC; set only while status='open'
  last_error  TEXT,
  updated_at  TEXT NOT NULL
);
```

```python
class BreakerStore(Protocol):
    def cooldown(self, route_key: str) -> datetime | None: ...
    def set_cooldown(self, route_key: str, *, until: datetime | None, error: str) -> None: ...
    def breaker(self, scope: str) -> BreakerState: ...       # half-opens an expired "open" row on
                                                                # read; never writes on read (U-DISPATCH-05)
    def record_failure(self, scope: str, error: str) -> BreakerState: ...  # opens at FAILURE_THRESHOLD
    def record_success(self, scope: str) -> BreakerState: ...              # failures=0, status=closed
```

Both stores are written only by P-05 and read only by P-05 (container.md §5: readers `-` for both
`spend` and `breakers`). No other part queries either table directly.

## 6. Record entries written

| kind | when | payload |
|---|---|---|
| `spend` | every call to `consumed()` that reaches the append (§3.3 step 2, before any local bookkeeping) | `tokens`, `measured`, `source`, `model`, `provider`, `repo`, `number`, `attempt_id`, `reservation_id` |

P-05 writes no `transition`, `grant`, `judgement`, or any other kind. `route()` and `reserve()` never
call `record.append`: no record kind exists for "a route was resolved" or "a reservation was granted
or refused" (architecture.md §8's kind vocabulary has no such entry), and a reservation is never
written as a spend (§7) — only what was actually consumed, measured or estimated, is recorded. Flow
step 6a's "the record shows the substitution" is satisfied downstream, by the `attestation` entry P-06
writes for whichever attempt actually runs on the fallback route (E-15/E-07 territory), not by
anything P-05 itself appends.

## 7. What P-05 does not do

- Does not invoke a harness with real content or a real protocol definition; E-24 sends an empty
  bundle directory and a marker file only. Assembling the real bundle and the real invocation are
  P-06's, through E-19.
- Does not retry inside `route()`: one call inspects the ladder once and returns a route/cursor pair or
  an exhausted `RouteUnavailable`. P-06 owns the panel loop and calls P-05 only through its `SupplyPort`:
  it passes the cursor returned by `route()`, adds an attempted route to its exclusions after a
  failed attempt, and on `Refusal(downgrade="fallback")` also adds that route's family before calling
  `SupplyPort.route()` again. P-02 calls P-06's `run()` exactly once and never resolves routes.
- Does not persist a reservation. A `Reservation` is a value carried by P-06 through `SupplyPort`
  into `run()` and back into `consumed()`; nothing survives a crash between `reserve()` and the first
  `consumed()` call, and nothing needs to, because every axis is checked against tokens already spent
  (the `spend` store), never against outstanding reservations — a reservation that is never spent
  leaves no residue, and the next `reserve()` call recomputes cleanly from what actually happened.
- Does not decide which of "fallback", "incomplete" or "escalate" P-06 ultimately acts on beyond
  stating the axis and one suggested `downgrade`; P-06 owns the cursor and complete panel result.
- Does not apply the external-send filter when `reserve()` checks `per_model_daily_tokens`: the
  check is for the supplied `route.model`, which is already an eligible route selected by `route()`.
  `consumed()`'s per-attempt tracking remains exact.
- Offers no manual breaker or cooldown reset (U-DISPATCH-05, bin). The only ways a scope becomes
  usable again: a passing probe (cooldown cleared, and on a later successful attempt the family
  breaker closed by `consumed()`) or the stored `open_until` / `unavailable_until` deadline passing —
  read fresh on every call, never written back except by a probe or a `consumed()` outcome. An
  unparseable or missing deadline on an `open`/cooling-down row is treated as expired, never as
  pinned open forever.
- Does not invent a route outside `snapshot.routes`; an unrecognised `(harness, model)` pair is
  treated as unavailable and dropped, never substituted with a nearby known one (RQA-NFR-009).
- Does not read PR content itself and does not treat a label as anything but a value compared for
  set membership; `facts.pr.labels` is read once per `route()` call and never parsed for instructions.
- Does not know what a finding, an obligation's evidence state, or a judgement disposition is;
  `attempt.outcome`'s `Verdict` case is inspected only to distinguish "succeeded" from "failed" for
  the breaker (§3.3 step 4), never opened further.
- Does not touch `jobs.status` and writes no `transition` entry.

## 8. Tests that prove it

Each is a unit test with fakes for `RecordWriter`, `SpendStore`, `BreakerStore` and `HarnessProber`.

| # | Given | Then |
|---|---|---|
| T1 | `route()`, `snapshot.routes` empty | `RouteUnavailable(no_fallback=True, tried=())`; zero probe calls |
| T2 | `route()`, the primary candidate's probe succeeds | returns `(primary, next_cursor)`; primary's cooldown cleared and `primary in next_cursor.excluded_routes` |
| T3 | `route()`, the primary candidate's probe fails, a distinct-family fallback is configured | returns `(fallback, next_cursor)`; the prober saw `(primary, fallback)`; primary's cooldown set and fallback excluded by `next_cursor` |
| T4 | `route()`, every configured candidate's probe fails | `RouteUnavailable(no_fallback=True, tried=<every candidate, in order>)` |
| T5 | `route()`, `snapshot.external.allowed=False`, only external candidates configured | `RouteUnavailable(tried=())`; zero probe calls — excluded before any probe |
| T6 | `route()`, `external.allowed=True` but `external.deny_label in facts.pr.labels` | the same external candidates excluded; a non-external candidate, if configured, still returned |
| T7 | `route()`, `cursor.excluded_families={primary.family}` | primary skipped without a probe; the next distinct-family candidate tried first |
| T8 | `route()`, a metered (non-subscription) candidate appears before a subscription candidate in `snapshot.routes` | the subscription candidate is probed first regardless of configured position |
| T9 | `route()`, a candidate's cooldown (`providers`) is unexpired | skipped without a probe call; absent from `tried` |
| T10 | `route()`, a candidate's family breaker is `open` with `open_until` in the past | treated as available and probed (half-open on read; no write occurs from the read itself) |
| T11 | `route()`, `snapshot.routes` names an `(harness, model)` pair absent from the alias registry and carrying no `command` | dropped at step 2; never probed, never returned |
| T11b | the same pair absent from the registry but carrying a non-empty `command` | admitted at step 2, probed through E-24, and returned when the probe succeeds — no RQA source change (RQA-FR-030, AC15) |
| T12 | `route()` via a fake `HarnessProber` that asserts its input | invoked with an empty bundle directory and a probe marker file; exit 0 + no verdict written → `True`; a written verdict despite the marker → `False` |
| T13 | `reserve()`, `spend.pr_total(...) + tokens == snapshot.budget.per_pr_tokens` exactly | `Refusal(downgrade="incomplete", axis="per_pr_tokens")` |
| T14 | `reserve()`, `spend.repo_total_since(...) + tokens == snapshot.budget.per_repo_daily_tokens` exactly | `Refusal(downgrade="incomplete", axis="per_repo_daily_tokens")` |
| T15 | `reserve()`, `spend.model_total_since(route.model, ...) + tokens == snapshot.budget.per_model_daily_tokens` exactly | `Refusal(downgrade="fallback", axis="per_model_daily_tokens")` |
| T16 | `reserve()`, every axis has one token of headroom | `Reservation(tokens=plan.participants * TOKENS_PER_PARTICIPANT)` |
| T17 | `reserve()` called alone, no `consumed()` call follows | `spend`'s counters are unchanged and `record.append` was never called — a reservation is never a spend |
| T18 | `consumed()`, `reading=57_000` | `Spend(tokens=57_000, measured=True, source="harness")`; the `spend` row's `tokens` is `57_000`, not `reservation.tokens` |
| T19 | `consumed()`, `reading=None` | `Spend(tokens=reservation.tokens, measured=False, source="reservation")` |
| T20 | `consumed()`, `attempt.outcome = AttemptFailure(kind="PROVIDER_TERMINAL", ...)` | `breakers.record_failure` called once for `attempt.route.family` |
| T21 | `consumed()`, `attempt.outcome` is a `Verdict` | `breakers.record_success` called once for `attempt.route.family`; a prior `open` breaker for that family closes |
| T22 | `consumed()`, `attempt.outcome = AttemptFailure(kind="TRANSIENT" or "CANDIDATE_TERMINAL", ...)` | no breaker call at all |
| T23 | `consumed()`, `record.append` raises `AppendFailed` | the exception propagates; `spend.append` and every breaker call are never reached |
| T24 | `reserve()`, `snapshot.budget.per_model_daily_tokens=None`, all spend history huge | that axis never checked; the other two still enforced |
| T25 | a chain of calls to `route()`, each with the preceding returned cursor, and every probe succeeds | no returned route repeats; each returned cursor strictly grows `excluded_routes` |
| T26 | a cursor chain over `len(snapshot.routes)` eligible, live routes | the next call returns `RouteUnavailable`; exhaustion occurs in at most `len(snapshot.routes)` calls |
| T27 | `reserve()` returns `Refusal(downgrade="fallback")` for a route and P-06 advances the cursor with that route's family | the next `SupplyPort.route()` result is a route from a different family, or `RouteUnavailable` |

Property that must hold across the suite: `grep -rn 'kind="spend"' rqa/ --include=*.py` returns hits
only inside `rqa/supply/spend.py` — no other part ever writes a `spend` entry.

## 9. Requirements this part answers for

Accountable: RQA-BR-012, RQA-FR-021, RQA-FR-022, RQA-FR-023, RQA-FR-024, RQA-FR-032, RQA-FR-039,
RQA-NFR-009, RQA-NFR-012, RQA-NFR-027, RQA-NFR-029.

Contributes to RQA-FR-030, which P-06 is accountable for: §3.1 step 2's second disjunct is the
literal "with the system's own source held constant" gate — an unregistered `(harness, model)` pair is
admitted for probing because the operator configured a `command`, never because RQA's source was
edited. T11b is the test that discharges this part of it; P-06's T14b and T14c discharge the rest. Each maps to a behaviour above: BR-012 (efficient
shared capacity) → §3.2 steps 1–6, the three-axis check itself, T13–T16; FR-021 (recorded from what is
actually exposed, distinguishable from an estimate) → §3.3 step 1, T18–T19; FR-022 (bound reached →
configured fallback, incomplete review, or escalation) → §3.2 steps 3–5 returning `Refusal(downgrade)`,
T13–T15; FR-023 (fallback configured → continue through it) → §3.1 step 5's loop, T3, T7; FR-024 (no
fallback → invent none) → §3.1 step 2's alias-registry membership test and step 6, T4, T11; FR-032
(active external path identifiable before send) → `Route`'s explicit `provider`/`model` fields
returned before any send, and §3.1 step 1, T5–T6; FR-039 (bound reached → never a successful outcome) →
`Refusal` is a value P-06 turns into an incomplete `PanelResult`, never a successful outcome (§3.2,
entirely), T13–T15; NFR-009
(alternative model/provider only when configured) → §3.1 step 2, T11; NFR-012 (external explicitly
configured → permitted) → §3.1 step 1's `may_send_external` computation admitting external candidates
when both conditions allow it; NFR-027 (no external configured → nothing sent) → §3.1 step 1 and step
2's exclusion, T5; NFR-029 (operator can deny one change's send) → §3.1 step 1's `deny_label` test
against `facts.pr.labels`, T6.

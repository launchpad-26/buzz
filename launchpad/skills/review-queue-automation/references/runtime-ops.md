# Runtime operations: milestone traces

This reference describes the diagnostic trace emitted by the current `rqa`
lifecycle. See [`../OPERATORS.md`](../OPERATORS.md) for command, configuration,
authority, keychain, and failure-handling guidance.

## Location and trust boundary

Each admission writes JSON Lines to:

```text
<state-dir>/jobs/<job-id>/trace.jsonl
```

Every line is one complete JSON object with `job`, `event`, and an aware UTC
`at` timestamp. The trace is diagnostic. It is never an input to a grant,
decision, resume, verification, or explanation. `rqa explain` reconstructs only
from the hash-chained SQLite record.

The writer holds an exclusive lock at
`<state-dir>/jobs/<job-id>/trace.lock`, writes the complete next file through a
same-directory temporary file, flushes and `fsync`s it, then atomically renames
it. Concurrent attempt-number allocation uses that same lock.

Inspect a trace with any JSON Lines reader:

```bash
jq . <state-dir>/jobs/<job-id>/trace.jsonl
```

## Closed event vocabulary

`rqa.record.trace.JOB_EVENTS` is the single registry. `append_trace` rejects an
unregistered name before creating the trace, and caller fields cannot replace
the canonical `job`, `event`, or `at` values.

| Event | Emitted when |
|---|---|
| `queueing` | a lifecycle admission begins |
| `preflight` | snapshot validation and review authority conclude |
| `lease_acquired` | the review lease is claimed |
| `lease_released` | a claimed lease is released successfully |
| `evidence` | coherent GitHub facts are captured for the pinned head |
| `budget` | a panel result reports whether a configured bound was reached |
| `planner` | the deterministic obligation plan is created |
| `strategy` | the plan's reasoning strategy is selected |
| `route_selection` | the routes that actually produced panel attempts are known |
| `rereview` | the job names a predecessor revision |
| `decision` | judgement chooses a disposition |
| `human_queue` | an escalation is durably enqueued |
| `mutation` | a GitHub or remediation mutation is attempted |
| `verify` | coherent facts confirm the captured head |
| `safe_stop` | the lifecycle stops without a successful disposition |

`REQUIRED_JOB_EVENTS` contains the nine milestones a job reaching a disposition
must carry: `queueing`, `preflight`, `evidence`, `budget`, `planner`, `strategy`,
`route_selection`, `decision`, and `verify`. The remaining milestones depend on
the branch taken.

Route diagnostics contain at most four executed routes. A route entry contains
only harness, model, provider, and family identifiers. Milestone fields contain
fixed outcomes, identifiers, hashes, and counts. They do not contain PR bodies,
file contents, credentials, environment values, exception messages, or model
output.

## Failure behavior

An unknown event is a programming error. A filesystem or atomic-write failure
is an `OSError`; the lifecycle's persistence-containment boundary prevents the
review from completing on a trace write it could not make. The previous trace
file remains intact if replacement fails.

An unparseable hand-edited trace line is ignored only by diagnostic attempt
allocation. It cannot affect an authoritative outcome because no trust path
reads this file.

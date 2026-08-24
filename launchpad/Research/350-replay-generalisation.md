---
description: Whether launchpad/review-agent's record-replay pattern can express an agent that takes tool actions — its seam is right but its replay is a constant function, so the storage and matching layer criterion 7 needs does not exist yet.
tags: [testing, agents, record-replay, determinism, criterion-7, research, issue-350]
---

# Can the review agent's record-replay pattern express an agent that takes tool actions?

All source references below are pinned to `5d76799d6e44f2f76aa7bd78c5343d339af98f63`.

## Finding

**The seam is right. The replay is a constant function.**

`launchpad/review-agent/` does have record-and-replay against real code paths with no live
inference, which is criterion 7's stated property. But what it replays is **one fixed value at one
injected seam**, and the replay callable ignores its own input. There is no request keying, no
ordering, and therefore no notion of a cache miss.

An acting agent emits a *sequence* of tool calls where each result feeds the next decision. That
needs request-keyed, ordered playback and a defined miss policy — none of which exists here. So
the answer to #350 is: **the architecture generalises, the mechanism does not.**

## Where inference is substituted

The reviewer is an injected callable, declared at
[`run_dimensions.py:118`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/run_dimensions.py#L118):

```python
Reviewer = Callable[[str], object]
```

The module docstring states the design intent
([`run_dimensions.py:19`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/run_dimensions.py#L19)):

> the reviewer is an **injected callable**, defaulting to [a stub]

and specifies the contract
([`run_dimensions.py:27-28`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/run_dimensions.py#L27-L28)):

> **Reviewer signature: ``Callable[[str], dict | str]``, called as ``reviewer(document)``.**

One document in, one verdict out. That is the entire model surface.

## What replay actually does

From [`test_recordings.py:133-141`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/test_recordings.py#L133-L141):

```python
recorded = _load_recording(fixture, dimension)
content = {"outcome": recorded["outcome"], "findings": recorded["findings"]}
doc = run_dimensions.build_document(
    0, "a" * 40, "b" * 40, surfaces, [dimension], nonce,
    reviewer=lambda document, content=content: content,
)
self.assertEqual(findings.validate(doc), [])
```

The replay reviewer is `lambda document, content=content: content` — it **discards `document`
entirely** and returns the recorded dict. Three consequences follow directly:

- **The recording is not keyed to the request.** Change the document arbitrarily and the same
  verdict comes back. Nothing binds a recorded output to the input that produced it.
- **A cache miss is not representable.** There is no lookup, so there is no miss, and no policy for
  one is needed or defined.
- **There is no sequence.** `build_document` calls the reviewer once per dimension, concurrently
  ([`run_dimensions.py:327`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/run_dimensions.py#L327)), not iteratively.
  Ordering between calls is not modelled because nothing depends on it.

The no-network property is proven by mocking, not by a transport-level recording
([`test_recordings.py:144-162`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/test_recordings.py#L144-L162)):

```python
with mock.patch("fetch.subprocess.run") as fetch_run, \
     mock.patch("run_dimensions.subprocess.run") as runner_run:
    ...
    fetch_run.assert_not_called()
    runner_run.assert_not_called()
```

So "replay makes no network call" means "no subprocess ran during a replay", which is a real and
useful assertion about the harness. It is not an HTTP-level cassette.

## What the pattern does prove, and it is not nothing

The real code exercised on replay is the **runner**: document assembly, the containment envelope,
report validation via `findings.validate()`, and the concurrency path. Those are genuine code
paths and they run with no model involved.

One property is worth carrying into any future harness. The runner assembles trusted fields itself
and treats reviewer output as untrusted
([`run_dimensions.py:32-34`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/review-agent/run_dimensions.py#L32-L34)):

> a reviewer's output is untrusted content, [so the runner] always assembles those itself

Visible in the call above: `head_sha` and `base_sha` are passed as `"a" * 40` and `"b" * 40` by
the *caller*, never read from the recording. A recorded agent transcript is likewise untrusted
input, and the same separation would apply.

## What an acting-agent harness would additionally need

Stated as a gap analysis of the existing mechanism, not as a design proposal:

| Property | Present here | Needed for tool actions |
|---|---|---|
| Model injected at a seam | yes | yes — same idea |
| Real non-model code paths execute | yes | yes — same idea |
| Recording keyed to the request | **no** — input ignored | yes, or replay cannot be trusted to correspond |
| Ordered multi-step playback | **no** — one call per dimension | yes, results feed later decisions |
| Defined behaviour on an unmatched request | **no** — not representable | yes, and it is the hard part |
| Tool *execution* under test | **no** — the reviewer returns a verdict, executes nothing | yes, that is the point of criterion 7 |

The last row is the substantive difference. Here the model's output *is* the artifact under
inspection. For an acting agent the model's output is an *instruction to run real code*, and it is
that code's execution the harness has to make deterministic.

## Recommendations

**Opinion, mine (Claude Opus 5, drafting for @tucktuck101). Not established by any source above.**

1. **I would treat criterion 7 as partly satisfied in architecture and unsatisfied in mechanism,
   rather than as unowned new scope.** #290 lists the agent replay harness among three pieces of
   "genuinely unowned" scope. My reading is that the seam-injection design is already proven here
   and worth reusing; what is missing is a keyed, ordered store with a miss policy.
2. **I would keep the trusted-field separation as a hard requirement** of anything built next. It is
   the property that makes a committed recording safe to replay, and it is easier to preserve from
   the start than to retrofit.
3. **I would treat the miss policy as the design's centre of gravity**, not an edge case. What
   happens when replayed code asks for something the recording does not contain determines whether
   the harness is a deterministic gate or a source of confusing failures — and ADR-0019 only permits
   a deterministic assertion to gate.

I have not designed any of this, and none of the three is a decision I am entitled to take.

## Confidence and what was not checked

**High confidence, read directly from the pinned source:** the reviewer signature, the constant-
function replay, the concurrency (not iteration) of reviewer calls, the mock-based no-network
assertion, and the trusted-field separation.

**Not checked:**

- **I did not run the review agent's suites.** #342 established they are not in CI's `CONTROLS`
  list; I read `test_recordings.py` rather than executing it, so I am reporting what it asserts,
  not that it currently passes.
- **The other 24 production modules in the directory** were not read. Something in
  `contain.py`, `detect.py` or the `check_*.py` controls could contain request-keyed machinery I
  did not find; my search was directed at the reviewer seam and the recordings.
- **Whether the 15 recordings contain anything that should not be public** is #348's question and is
  not addressed here.
- **Whether a keyed, ordered store is the right design at all** — external prior art on
  record-replay harnesses was not surveyed for this document. That is closer to #348's territory,
  and my recommendations above are reasoning from this codebase alone.

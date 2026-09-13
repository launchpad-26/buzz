# RQA review protocol

This is the one published definition of what a managed review is, versioned
alongside [`schema/verdict-1.json`](schema/verdict-1.json) as a single pair under
[#2064](https://github.com/launchpad-26/buzz/issues/2064). Every verdict from every
harness, model or provider is checked against this pair through `validate()`
(`code/P-04-protocol.md` §3); nothing about it depends on which route produced the
verdict being validated (RQA-FR-033). This document is prose: it names the six
concepts RQA-BR-002 requires two reviewers to describe identically, so that no
reviewer can privately redefine any of them. It does not decide a specific job's
outcome — that is `code/P-07-judgement.md`'s responsibility, applying this
vocabulary to one job's evidence.

## 1. Review scope

A review evaluates one pull request at one head commit against the obligations its
pinned policy names for that change (`Snapshot.policy.obligations`, `CONTRACTS.md`
§3). Each `Obligation` names the `PathGlob` patterns that put it in scope
(`Obligation.paths`, matched only by `rqa.protocol.paths.matches` — the sole path
matcher in RQA) and the risk classes it applies to (`required_for`). An empty
`Obligation.paths` is in scope for every file; that policy is implemented by the
obligation's own caller, never by the matcher itself. A review is complete for one
obligation only when that obligation has been assigned one of the seven evidence
states below; it is complete for the job when every obligation in scope for that
job's risk class has been assigned one.

`Obligation.evidence` is the requirement text itself: the free-form statement of
what a reviewer must establish before the obligation can be resolved to any state
other than `unknown` (§3) — for example "the changed public functions have doc
comments" or "the touched migration has a corresponding down-migration". It is
the criterion two independent reviewers read to decide whether they are looking
for the same thing, not a report of what either of them found; what a reviewer
*found* is recorded separately, as `Finding.evidence` on any `Finding` raised
against it. RQA-BR-002's "required evidence" concept is this field: the same
`Obligation.evidence` text, pinned by the same `Snapshot`, is what both readers
in its fit criterion resolve against.

## 2. Finding categories: the two groups

Every `Finding` carries a non-empty `categories: frozenset[Category]`, drawn from
exactly seven values split into two disjoint groups that together are `set(Category)`:

- **`MECHANICAL_GROUP`** — `mechanical`, `procedural`, `creation_time`. Findings a
  registered tool can fix deterministically and a behavior-equivalence check can
  verify, without a substantive judgement about the change's design or correctness.
- **`SUBSTANTIVE_GROUP`** — `correctness`, `security`, `architectural`, `evidence`.
  Findings that require reviewer judgement and are never candidates for automatic
  remediation, however exact their `Remedy` looks syntactically.

A finding may additionally carry `extra_tags: frozenset[str]`, an open vocabulary
(for example `"performance"`) the protocol never closes and never merges with
`categories` — the closed/open split is what keeps mechanical and substantive
findings distinguishable in the record even when a finding also carries open tags
(RQA-BR-005), and only `categories` decides remediation eligibility. A finding whose
categories are a subset of `MECHANICAL_GROUP`, carries a `Remedy`, and whose
`behaviour_changing` is `False` is eligible to be considered a remediation
candidate by `code/P-07-judgement.md`; `behaviour_changing` is only the reviewer's
own nullable assertion and is treated as `True` (never a candidate) when absent —
P-04 does not itself classify or select candidates.

## 3. The seven evidence states

Every obligation resolves to exactly one `EvidenceState`:

| State | Meaning |
|---|---|
| `verified` | Positive evidence supports the obligation; no reviewer or corroboration gap blocks it. |
| `not_verified` | Evidence was collected and reviewed but did not positively support the obligation. |
| `unavailable` | No reviewer could reach the evidence needed (for example a required tool or check never ran). |
| `contradictory` | Independent evidence disagrees about the obligation's state. |
| `failed` | Evidence exists and affirmatively shows the obligation is not met. |
| `incomplete` | Evidence depends on something still outstanding, most commonly a check still `pending` (§6). |
| `unknown` | No qualifying evidence was produced for the obligation at all. |

These seven values are exhaustive and closed: the wire schema's `state` enum (§2)
accepts exactly these seven tokens and no others, so a harness cannot introduce an
eighth state.

## 4. Blocking-condition semantics

Whether a finding blocks a review is a policy decision applied to this protocol's
vocabulary, not something this package decides (`code/P-04-protocol.md` §7): a
corroborated finding blocks when any of its categories blocks under the pinned
policy's `Blocking.categories`/`Blocking.severities` (`CONTRACTS.md` §3), and
corroboration itself requires either two distinct attested provider families or one
PR-attributed failing check citing the same fingerprint. An `InjectionAttempt`
reported by any harness is always converted into a blocking synthetic `EVIDENCE`
finding, unconditionally and independent of policy — an attempt to alter the review
outcome or fabricate evidence is never merely advisory. The same is true of a
detected forged or unbalanced nonce envelope (§6). These conversions, and the
policy-blocking evaluation itself, belong to `code/P-07-judgement.md`; this document
fixes only that the vocabulary they operate on — `Category`, the evidence states,
and `InjectionAttempt` — means the same thing everywhere it is read.

## 5. Review-completion and final-disposition semantics

A review is **complete** once a validated panel result has run to its natural end
(exhausted its candidate routes, hit budget, or a bundle failure) or every planned
obligation has independently reused verified evidence from a predecessor job; a
carry-only run with nothing regenerated still produces a current-job judgement.
Final disposition is chosen, in order, from four values — `approve`,
`request_changes`, `remediate`, `escalate` — as one deterministic function of the
resolved evidence states, findings and their blocking/candidate status: a blocking
finding forces `request_changes`; a behaviour-changing finding or an unresolved
escalation cause forces `escalate`; an otherwise-clean panel with an eligible
remediation candidate resolves to `remediate`; and `approve` requires every
obligation `verified`, sufficient assurance, no injection/envelope/suspicious-clean
finding, and that the panel never hit a configured budget bound (RQA-FR-039: such a
run never ends in a successful disposition). This selection function is
`code/P-07-judgement.md`'s, not P-04's; this protocol fixes only the vocabulary
(evidence states, categories, `Verdict` shape) the selection is computed over, so
that the same panel evidence always resolves the same way regardless of which part
of RQA reads it.

## 6. Check-conclusion vocabulary and pending semantics

Review completion and blocking both read GitHub check attribution through the
canonical vocabulary `code/CONTRACTS.md` §4 defines, which this protocol adopts by
reference rather than restating a second time:

- `FAILING = {failure, timed_out, action_required}` — attributable and blocking.
- `UNSETTLED = {pending}` — never corroborates, never blocks, and is never
  inherited from a merge-base check. An obligation whose evidence depends on a
  `pending` check resolves to `incomplete` (§3) unless independent evidence
  verifies it some other way.
- `PASSING` — every other `CheckConclusion` value (`success`, `neutral`, `skipped`,
  `cancelled`): eligible for attribution but never itself a blocking signal.

## 7. The interaction contract (E-19/E-24)

Every byte in a review bundle that originates in PR facts — title, body, labels,
diff, changed-path names, check names, file bytes — is presented to the harness only
through a per-bundle nonce envelope (`envelope()`/`extract()`, this package's
`envelope.py`), on the data side of the harness's own instruction/data role
separation; RQA's immutable review protocol is the only instruction. `envelope()`
and `extract()` are stateless string functions that define this grammar; P-04 never
applies or enforces it at runtime; P-06 is the mechanism (`code/P-06-harness-interface.md`).
A harness's `Verdict.injection_attempts` is mandatory, even when empty, because the
harness — not P-04 — is positioned to semantically recognize PR text aimed at
altering the review outcome or fabricating evidence.

A distinct, content-free instance of the same interaction contract is the E-24
liveness probe: a harness invoked against a bundle directory containing only the
`PROBE_MARKER` file (this package's `interaction.py`) — no PR content, no protocol
definition, nothing to review — must exit `0` and write no `verdict.json` to the
(empty) output path. `rqa.supply`'s `HarnessProber.probe()` judges exactly those two
facts; this package supplies only the marker name.

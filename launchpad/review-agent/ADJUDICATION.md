# ADJUDICATION.md — the adjudication stage's verdict contract

Normative, and a sibling to `CONTAINMENT.md` and to `FINDINGS.md` in the same voice.
This is the document [#119](https://github.com/launchpad-26/buzz/issues/119) reads to
know what arrives once [#118](https://github.com/launchpad-26/buzz/issues/118)
(adjudication) has run.

## The verdict

Exactly one verdict per finding, from `CONFIRMED | REFUTED | UNPROVEN`. "Exactly one" is
the whole criterion: a finding present on input and absent from output is a defect in
this stage, not a tidy-up — the contract states that the input and output `finding_id`
sets are **equal**, not that output is a subset of input.

**The default is `UNPROVEN`, never `REFUTED`.** Absence of confirmation is not
refutation. An adjudicator that cannot reach the location a finding names, cannot parse
the finding, times out, or returns unusable output yields `UNPROVEN` with a reason. This
is the fail-closed direction: a wrongly-`UNPROVEN` finding still reaches a human; a
wrongly-`REFUTED` one reaches them wearing a dismissal.

## The added finding fields

On top of `FINDINGS.md`'s ten. Names are final here:

| field | meaning |
|---|---|
| `verdict` | `CONFIRMED \| REFUTED \| UNPROVEN` |
| `verdict_evidence` | what the adjudicator established, in its own words — required and non-empty on **all three** verdicts, including `REFUTED` and `UNPROVEN`. An `UNPROVEN` with no reason is indistinguishable from a stage that skipped the finding. |
| `reported_severity` | the reporting dimension's value, preserved verbatim |
| `severity` | the **re-rated** value — `FINDINGS.md`'s field, overwritten here |
| `severity_reason` | required whenever `severity != reported_severity` |
| `duplicate_of` | `finding_id` of the survivor, or null — see § Dedupe, below |

`severity` carries the re-rating and `reported_severity` preserves the original because
#119 ranks by `finding["severity"]`, so this field name decides what the published review
leads with. The dimension's original value stays readable beside it, which is what
#118's issue requires — "readable", not merely "recoverable from history" — and the two
are only the same field if #119 changes what it renders.

**Severity is re-rated on every finding, including `REFUTED` ones.** The rating answers
"how bad if true", which is a separate question from "is it true". Rating only the
confirmed findings would leave `REFUTED` findings carrying an unexamined severity into
#119's sort.

### `severity` and `reported_severity` must both be in `review.SEVERITY_ORDER`

Stated as a guarantee this stage makes to #119, and as **defence in depth** rather than
#119's only defence: #119's plan states it sorts with `.get(severity, 9)` and routes an unrecognised
severity to its own malformed-finding heading, so a bad value is survivable there — but
this stage is the one that **creates** bad values by re-rating, and a producer that
relies on its consumer's default has moved the failure rather than removed it.

The guarantee is on the **effective** severity — the re-rating where one was made,
`reported_severity` where none was. Both must be checked: a finding arriving with an
out-of-ladder `reported_severity` that the judge happens to agree with is never
re-rated at all, so a guard watching only re-ratings never fires and the bad value is
copied into `severity` untouched.

**This cannot happen if the input document is validated first, and this stage does so.**
`run_adjudication.py`'s `main` runs #117's own `findings.validate` against the input
document *before* any adjudication logic touches it, and exits non-zero — adjudicating
nothing — when validation fails. A finding whose `severity` value arrives out-of-ladder
(an `"Info"`, say — this is the dimension's own report, before this stage has re-rated
anything) fails `FINDINGS.md`'s own severity rule and never reaches this stage's
re-rating logic at all. Note the field name: `reported_severity` does not exist on
input at all — #117 emits only `severity` — so this guarantee rests on that field, not
on a field literally named `reported_severity`, which is a name this stage's own
*output* introduces.
This is stronger than "this stage is agnostic about its producer": #119 is agnostic
about *its* producer because #119 cannot re-validate a document it did not assemble from
parts, while this stage *can*, because its input document is exactly #117's own output
shape and the validator that checks it already exists. Refusing outright is also the
only answer that needs no invention: there is no legal value to preserve
`reported_severity` *as*, once it already arrived broken, and inventing one would be this
stage silently deciding what the dimension actually meant.

So an out-of-ladder **effective** severity this stage can still produce — one its own
re-rating created from a legal `reported_severity` — is an adjudication **failure** for
that finding: `UNPROVEN`, with the refusal stated in `severity_reason`, and
`reported_severity` left unchanged (input validation already guarantees it was legal to
begin with). `severity` falls back to `reported_severity` when that is in the ladder,
and to `Blocker` when it is not — the second branch is defence in depth only, since
input validation already guarantees `reported_severity` arrives legal, but there is no
safe value to copy if that guarantee were ever bypassed. This stage may not silently
decide an unrateable finding is a small one, and it is never asked to invent a value for
a field that arrived already broken.

## Escalate, never approve

Stated as three concrete prohibitions rather than a slogan, because a slogan is not
checkable — followed by the structural condition all three turned out to depend on
(§ 4 below, added after a judge was found able to defeat two of them without violating
either as written):

1. **No field in this contract can carry an approval, a merge recommendation, or a
   pass.** There is no `approved`, no `mergeable`, no `verdict: OK`. A judge cannot emit
   what the record cannot hold. This binds field names and enumerated values, **not free
   text**, and the limit is stated because it is otherwise invisible: `verdict_evidence`,
   `severity_reason`, and `notes` are free strings, and nothing mechanical stops a judge
   writing "this looks fine to me, recommend merge" into one. A control that grepped
   them for approving phrasing would itself be a keyword filter — the kind of narrow
   guard the review dimensions exist to find in other people's code. Today the exposure
   is nil: #119 renders none of the three free-text fields. It stops being nil the
   moment #119 renders `verdict_evidence`. The mitigation is placed where it can work —
   the adjudicator's own prompt forbids this phrasing, a recorded before/after pair
   measures whether that prohibition makes a difference, and this is a condition on
   #119 ever rendering that field, not a solved problem independent of it.
2. **A `REFUTED` finding is still published, with its verdict beside it.** This stage
   removes nothing from `reports[].findings`, and `findings_count` is unchanged by
   adjudication.
3. **A downgrade is allowed and must be visible.** `severity` may fall below
   `reported_severity` — an overstated true finding is its own error — but it carries
   `severity_reason`, and the finding is additionally listed in
   `adjudication.downgrades`, so the movement is legible even where a consumer renders
   only `severity`.

The reasoning is #109's, in #122's corrected wording: judges ruling on adversarial
safety claims perform "on average only slightly better than a random coin-flip" against
6,642 human-verified labels, and the AUROC 0.48–0.64 range is one judge on one victim
model under two attacks — not quoted here as anything broader. The phrase "despite high
performance on standard validation sets" is not used, because it is not in the paper.

### 4. An injected callable is given immutable input, or a copy — never the record itself

**Added 2026-08-24.** The three prohibitions above are all enforced by inspecting what a
judge **returns**. That makes them conditional on something this contract had left
unsaid: the judge must not be able to reach the record directly.

It could. `adjudicate()` passed the judge the live output finding and read
`reported_severity` back out of it *after* the call, so a judge doing
`finding["severity"] = "Low"` and returning nothing but a `REFUTED` verdict produced
three `Blocker`s published as `Low`, an empty `adjudication.downgrades`, a
`reported_severity` of `"Low"` — and **no `verdicts.validate` violation**, because every
check ran against a record the judge had already rewritten. Prohibitions 1 and 3 were
both defeated without either being violated as written. Fixed in `5bb984b96`.

**#117 had this right and this stage diverged from it.** `run_dimensions._run_reviewer_into`
takes `document: str` — an immutable object, so a reviewer there can influence the run
only through its return value, which is then validated. This stage took a `dict`, and a
`dict` handed to injected code is a shared mutable reference, not an argument.

So, as a rule binding every stage and not just this one:

> A callable injected into any stage of this pipeline receives immutable input, or a deep
> copy, **in every argument**. Never the object the stage will go on to publish, and never
> the object its own guards will be evaluated against.

**"In every argument" is not padding — the first attempt at this rule failed on exactly
that.** It copied the finding and passed `input_document` through live, which satisfied
the sentence as originally written while leaving the hole it describes open: the runner
re-reads `stages` from that document and evaluates its integrity guard against it, so a
judge appending `{"name": "approval", …, "approved": true}` to `document["stages"]` put
three approval-bearing entries into the output *and* mutated the caller's object, against
`adjudicate()`'s own "never mutates `input_document`" promise. The regression tests
mutated only the copied argument, so they could not see it. Found by a review panel after
the partial fix had already shipped to a pull request. A rule about arguments has to name
all of them, and its tests have to exercise all of them.

Two consequences worth stating, because both were tempting and both are wrong:

- **Copying is not defence in depth here, it is the enforcement.** A guard that reads the
  value it is guarding *after* invoking the component it is guarding against is not a
  guard, however carefully the comparison is written.
- **It is not only about severity.** `finding_id` is what the input/output set-equality
  check is keyed on, so an in-place edit there defeats that check too. Copy at the
  boundary, once, rather than guarding fields individually as each is noticed — the
  fields are open-ended and the boundary is not.

This applies to the judge, the dedupe judge, and any future injected reviewer, renderer or
publisher — #119's included. It was found by cross-model review after four same-model
passes over the same code did not raise it.

## The `adjudication` block

A top-level sibling of `reports` and `containment` in the merged document. **Nine keys**,
and the count is load-bearing for the same reason `FINDINGS.md`'s ten finding fields
are: the control suite builds one control per key, so a key present in the output but
not in this list gets no control at all.

| key | meaning |
|---|---|
| `schema_version` | integer, starts at 1 |
| `verdict_counts` | `{CONFIRMED, REFUTED, UNPROVEN}` — integers |
| `findings_in` | count of findings received |
| `findings_out` | count of findings emitted; **must equal** `findings_in` |
| `duplicate_groups` | array of `{survivor, duplicates: [finding_id]}` |
| `downgrades` | array of `{finding_id, from, to, reason}` |
| `total_refutation` | boolean — see § Total refutation |
| `notes` | array of free-text notes |
| `completion_marker` | **last** key: `BUZZ-ADJUDICATION-COMPLETE:{nonce}`, using the document's own top-level `nonce` — #117's sixth key, passed through unchanged and never re-generated here |

The block carries **no nonce of its own**: a second copy in one document is a second
thing that can disagree, and there is no question a copy would answer that reading the
top-level key does not.

The marker is last and carries the nonce for the same two reasons `FINDINGS.md` gives:
a marker at the end cannot survive truncation, and a fixed string published in a public
repository is one a PR author can type into their own diff. This stage never accepts a
caller-supplied nonce — it verifies the nonce it receives against every report's own
marker and passes the same value through, exactly as it received it.

`findings_out == findings_in` is a necessary but not sufficient check on its own — it
would not catch a drop-and-invent swap (one real finding removed, one fabricated one
substituted, count unchanged). The binding guarantee is the stronger one stated in
§ The verdict: the input and output `finding_id` **sets** are equal, which a
drop-and-invent swap violates even though the count survives it.

## The `stages` entry

This stage adds exactly one entry, `{name: "adjudication", status, reason}`, to whatever
`stages` array arrived (empty, or already carrying earlier entries), and passes every
existing entry through unchanged.

> **Amended 2026-08-24.** This section previously opened with a sentence that is struck
> through here rather than deleted, because it was the asserted contract for ten days:
>
> > ~~#117 does not emit a top-level `stages` array — it is the manifest #119's plan reads
> > for stages that produce no envelope of their own (#116's pre-flight, and this one).~~
>
> That is the wording #119's own plan superseded on 2026-08-14 (`8d47f8764`) and named as
> a defect:
>
> > *"names EVERY stage the review depended on — #116's pre-flight, #117's three
> > dimensions by slug, and #118's adjudication. Not only the stages that emit no
> > envelope of their own, which is what an earlier revision said and which contradicted
> > this step's own condition (7) […] Built to the old definition, the manifest held two
> > entries, neither a dimension, so (7) could never fire: a three-dimension run that
> > produced two reports rendered as COMPLETE."*
> > — `launchpad/plans/2026-08-12-issue-119-publish-one-review.md` STEP 5
>
> **The corrected definition:** `stages` names every stage the review depended on,
> *including each of #117's dimensions by slug*. #119's condition (7) — a dimension named
> by the manifest produced no report at all — is the only check that catches a dimension
> failing so completely that no envelope exists for it, and it has nothing to compare
> `reports` against unless the dimension is named here.
>
> **This stage cannot produce those entries, and must not pretend to.** Deriving them
> from `reports[].dimension` would name only the dimensions that *did* report, so
> condition (7) could still never fire — a report cannot testify to its own absence. The
> expected set is known only to `run_dimensions.list_dimensions()`, which enumerates
> `dimensions/*.py` before dispatch. **Producing the per-dimension entries is #117's, in
> `run_dimensions.py`.** Filed separately; this stage's contribution is the one
> `adjudication` entry described above, and pass-through of whatever else arrived.
>
> Consequence, stated plainly rather than left for a reader to discover: until #117 emits
> them, a `stages` array reaching #119 names no dimension, so condition (7) cannot fire
> and a run that loses a whole dimension can still render as complete. That is a live gap
> in the pipeline, not a property of this stage.

**It never overwrites an existing `adjudication` entry.** A second one on input means a
re-run against a document this stage has already adjudicated, and this stage exits
non-zero rather than silently repeating itself.

`status` is `"complete"` only when every finding received a verdict, the top-level
`nonce` was established (see § The `adjudication` block, above), and § Total
refutation's flag is false.
Otherwise it names the specific reason: `"total_refutation"`, a nonce disagreement, a
missing top-level `nonce`, or (via `run_adjudication.py` exiting before this stage runs
at all) an input that already fails #117's `findings.validate`.

## Dedupe

Findings describing the same defect in different words are grouped, and the grouping
is in the output rather than in the stage's head. `finding_id` cannot do this work: it
is not stable across a model rewording `defect`, and two findings from *different*
dimensions describing one defect have different ids by construction, since `dimension`
is a hash input.

A group is `{survivor, duplicates: [finding_id]}` in `adjudication.duplicate_groups`,
and every duplicate **also** carries `duplicate_of` naming its survivor. Both
directions, so the grouping is discoverable from the finding itself as well as from the
block — a consumer holding one finding should not have to scan a top-level array to
learn it is a duplicate.

**A duplicate still receives its own verdict and is still emitted.** Dedupe changes
presentation, never the count: it groups findings, it does not remove them. Removing a
duplicate's own record would breach the "every finding receives exactly one verdict"
requirement while looking like tidiness.

The survivor is chosen **deterministically**: highest adjudicated severity, then
`CONFIRMED` before `UNPROVEN` before `REFUTED`, then lowest `finding_id`. Stated
explicitly because "the best one" is not a rule, and two runs over the same input must
agree on the same survivor. A run that dedupes nothing emits an **empty**
`duplicate_groups` array rather than omitting the key — the same "empty, not missing"
discipline `FINDINGS.md` uses for `findings` on a clean dimension report.

A finding whose `duplicate_of` names a `finding_id` absent from the document, or names
itself, is invalid.

## Total refutation

`total_refutation` is `true` if and only if `findings_in > 0` and every finding's
verdict is `REFUTED`. Refuting everything is flagged rather than published as a clean
PR — total refutation is likelier a broken adjudicator than a flawless diff, and #109's
own scepticism about this stage exists precisely so a suspicious result gets a second
look rather than a pass.

## Containment findings are passed through, not adjudicated

The `containment` block is emitted byte-identically to what arrived. Three reasons:

1. Containment findings are deterministic catches, not claims needing a judge.
2. An adjudicator able to `REFUTE` one could erase a detected attack, which
   `CONTAINMENT.md` § Severity contract calls worse than never detecting it.
3. Their severity is fixed at `Blocker` by that same contract, so re-rating them here
   would contradict a document this one is a sibling to, not an authority over.

**A known, deliberately unresolved mismatch, not silently fixed here.**
`CONTAINMENT.md`'s "Contract for later stages" table literally binds this stage to call
`contain.findings_for(surfaces, nonce)`, which needs the `Surface` dict and the nonce —
this stage receives a JSON document on stdin and has neither. #117 already places
exactly what that function returns into the merged document's `containment.findings`
key — not the whole `containment` key, which also carries the `states` map #117 builds
separately — so this stage consumes that block verbatim instead of re-deriving it
(re-fetching the surfaces
here would be a second source of truth for one fact, and a second reason for this stage
to touch author text at all — the opposite of what the table's own "must never" column
requires). The pass-through above honours the *intent* of the table's row, but the
table's own literal wording is not corrected by this document — that edit is left for
whoever owns #120, since `CONTAINMENT.md` is a cross-cutting contract this document does
not have unilateral authority to amend.

## PR comment verdict blocks: refusing more than one (#287)

A ` ```verdict ` fence posted in a PR comment (the row shape `review-gate.sh`'s
`cmd_verdict` already validates for a single local file — see that script for the row
grammar) is not unique to one comment on a PR. Reviewers re-post a corrected block after
noticing a mistake, and nothing before #287 distinguished a deliberate correction from
two independent, disagreeing verdicts left standing at once.

**The rule: no amendment marker. The parser deterministically takes the last complete,
closed, well-formed block by comment order (highest `(created_at, comment_id)`), and
refuses anything that does not reduce to exactly one candidate that way** — a malformed
row, an unclosed block, or two-or-more blocks inside the *same* comment are all refused
outright, never resolved by picking one. This was Option B of two readings put to
Serina: Option A would have required a new explicit "supersedes" marker before a later
block could override an earlier one; Option A was not chosen.

**Why B, not A — the evidence, not a preference.** Two real double-block PR threads were
pulled via `gh api repos/launchpad-26/buzz/issues/<n>/comments --paginate --slurp` and
read in full before this decision was recorded, not assumed:

- **PR #261** — comment `5364185647` (2026-08-21T01:45:48Z) and comment `5364261676`
  (2026-08-21T01:58:30Z), same author, 13 minutes apart. Both are full 4-row
  restatements of the same finding set; the second comment's row 2 severity moved
  Medium → Low from the first.
- **PR #264** — comment `5364221899` (2026-08-21T01:51:51Z) and comment `5364504768`
  (2026-08-21T02:36:23Z), same author, 45 minutes apart. Both are full 3-row
  restatements; the second comment's row 1 severity moved High → Blocker from the
  first — the named promotion #287 cites.

In neither real case does the later comment carry any marker referencing the earlier
one — no "supersedes", no "correction to comment `<id>`", nothing machine-parseable. Both
are simply a complete re-post of the whole block, later in the comment stream. Requiring
a marker (Option A) would have made both of these real, already-happened corrections
retroactively unparseable, and would have needed a reviewer-side convention change no
reviewer today follows. Taking the later complete block by comment order (Option B)
resolves both cases exactly as the reviewer who wrote them intended, with no new syntax
to adopt.

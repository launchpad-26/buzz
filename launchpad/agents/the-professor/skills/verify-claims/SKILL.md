---
name: "verify-claims"
description: "Adversarially re-check that each behaviour claim in a gated draft has a citation at all, and that the citation actually supports it — the third, mandatory, unskippable gate before any write, run twice per draft. Use when a draft has passed check-page and screen-sensitive and is about to be written. Not for secrets screening (screen-sensitive) or structural contract compliance (the check-page subcommand of tools/professor.py). Requires $PROFESSOR_VERIFIER_CMD for any draft containing behaviour claims; it fails loud rather than passing a claim it could not check."
---

# Verifying claims, not just citations

`draft-page` and `update-page` both call this as their **third** gate, after
`check-page` (contract/citation-resolution) and `screen-sensitive` (sensitive-data),
never before either and never in parallel with them — cheapest and most
deterministic first, this gate last, because it is by far the most expensive check
in the suite. It only ever runs against content that already passed both cheaper
gates, so it never does expensive work on a draft that was going to be rejected
anyway.

**This gate exists because a resolved citation is not the same claim as a supported
one.** `check-page` proves a citation points at a real path and a real commit,
current as of drafting. It has never proven the cited source actually *says* what
the claim in front of it asserts — a gap
`launchpad/Research/the-professor-skill-suite-redesign.md` §2 (via the original
`the-professor-design.md` §2) named but never solved. **Decided 2026-09-04, by
Serina: this gate is mandatory and unskippable**, the same severity as
`screen-sensitive` — no sampling, no CI-only mode, no configuration flag that turns
it off, even though it is a real model call per claim where every other gate in this
pack is a deterministic script.

**Decided 2026-09-04, by Serina (Open Questions item 9): dispatch itself is still a
plain subprocess call, same shape as every other tool call in this suite.** Run
`$PROFESSOR_VERIFIER_CMD` (a target/session-configured environment variable naming a
headless, single-turn CLI command — no suite-applied default, same override pattern
and same no-default rule as `$PROFESSOR_PACK_ROOT`; `claude --print` is the suite's
recommended value to configure it to, not a fallback the suite applies for you),
feeding it only the cited source span and the claim's exact sentence, and capture its
stdout as the verdict. Confirm `$PROFESSOR_VERIFIER_CMD` resolves before dispatching
anything — same fail-loud requirement as `$PROFESSOR_PACK_ROOT` elsewhere in this
pack, not a silent fallback to a guessed command; **§2a gives the exact message.** A
harness with no headless single-turn CLI available at all cannot run this gate — that
limitation is real and named, not solved by this decision.

**What counts as a verdict, and what a non-answer does, are specified in §2b and §2c.**
Capturing stdout is not the same as having an answer: a response is a verdict only if
the whole of it matches §2b's grammar, and a command that exits non-zero, times out or
stops mid-response has not answered at all, however well-formed the text it printed.

**Decided 2026-09-04, by Serina: this skill runs twice per draft, not once** — once
during drafting (so `draft-page`/`update-page` can fix what it flags), and once more,
independently, as the true final step immediately before a write is finalized or a PR
opens. The first pass is advisory; the second is the actual gate of record — this
doubles the per-claim model-call cost, accepted deliberately for the same reason this
gate is mandatory in the first place (`launchpad/Research/the-professor-skill-suite-
redesign.md` §6's flow-diagram note has the full reasoning).

## 1. Identify the behaviour claims

Read the gated draft content (the same scratch file `screen-sensitive` just cleared —
never the real target path). Extract every **behaviour claim**: a factual statement
about what code *does* — "this function retries three times," "this endpoint returns
404 when the channel doesn't exist," "this flag defaults to `false`" — each already
tied to a specific cited source (the exact commit + path, and a line-range span when
the claim is line-specific rather than about a file's general shape — `draft-page`/
`update-page` wrote all of it into the citation when they drafted the claim;
`check-page` in the earlier gate confirmed it resolves, it didn't invent it).

**Opinion and judgement claims are never checked here, by design.** "This approach is
simpler than the alternative" or "this is the recommended pattern" are attributed
judgement, not a mechanically checkable fact — per the original design's own test
(`the-professor-design.md` §2): "is being wrong silent and mechanically checkable?"
does not hold for a claim that's explicitly framed as judgement. Skip these; do not
invent a verdict for a claim type this gate was never meant to check.

If a draft contains zero behaviour claims (rare — a page that is entirely structural
or opinion content), record that explicitly and pass through to `provenance-log`
without dispatching anything. Do not fabricate a claim to have something to verify.

**Decided 2026-09-04, by Serina: a behaviour claim with no citation at all is an
immediate `UNSOURCED` verdict** — check for this before dispatching anything. There is
nothing to check an absent citation *against*, so `UNSOURCED` costs nothing beyond the
identification pass already required by this step; it is not a reason to skip the
claim, and it is not the same finding as `NOT_SUPPORTED` (which requires a citation
that exists but doesn't hold up).

## 2. Dispatch one independent check per claim that has a citation

For each behaviour claim that has a citation, run `$PROFESSOR_VERIFIER_CMD` as a
subprocess — a genuinely separate check in **fresh context**.

**Send exactly these four things, and nothing about the draft:**

1. The task: decide whether the cited span supports the claim.
2. **The instruction to decide *only* from the span, inferring nothing from anything
   outside it.**
3. The response format §2b requires — the three verdict literals and the two-line
   **reason-first, verdict-on-its-own-last-line** shape, stated explicitly — **and the
   instruction that the reason must not name any verdict literal other than the one on
   line two**, which is what §2d blocks on. Asking for it costs a sentence; not asking
   for it turns §2d into blocks the verifier was never given a chance to avoid.
   **Do not ask for the verdict first.** The ordering is not cosmetic: §2b records
   why it is the difference between `PARTIALLY_SUPPORTED` being reachable and being
   unreachable.
4. The cited source's exact span, and the claim's exact sentence.

Items 1–3 are not context about the draft; they are the question being asked. **Omitting
them does not make the check purer, it makes it not a check** — proven by a real dispatch
on 2026-09-15 (STEP 3), where a verifier sent only a claim and a span invented its own
task, answered `REFUTED` (a verdict this gate does not define), and produced eleven lines
of prose. §2b correctly blocked it — but a gate that blocks every claim is not a gate.

Deliberately withhold:

- the rest of the draft
- the drafting agent's own reasoning or notes
- any other claim's verdict from this same run

**Withholding the draft is not the same as achieving isolation — named 2026-09-15, after
the same dispatch demonstrated it.** A verifier command with access to the repository can
go and read whatever it likes: that run, given no instruction to stay inside the span,
opened four other files, cited line numbers from three of them, and ran `git` against the
working tree. It reached a defensible conclusion by reasoning about code the gate never
showed it.

Two things follow, and both are requirements, not advice:

- **Item 2 above is mandatory in every dispatch.** It is the only part of isolation this
  skill can enforce through the prompt.
- **Prefer a `$PROFESSOR_VERIFIER_CMD` without repository access** where the harness can
  provide one. A verifier that cannot read the target repo cannot silently substitute its
  own evidence for the cited span, whatever the prompt says. Where that is not available,
  isolation rests on item 2 alone — which is an instruction, not a boundary, and should
  be understood as such.

**This isolation is the entire point of the gate.** A verifier that shares context
with the drafter inherits the drafter's own blind spots instead of catching them —
running this check in the same context that produced the draft would make it a
restatement of the drafter's own confidence, not an independent check.

Each dispatched check returns one of three verdicts, plus a one-sentence reason:

- **`SUPPORTED`** — the cited span actually says what the claim asserts.
- **`NOT_SUPPORTED`** — the cited span does not say this; the claim is wrong,
  unrelated to the citation, or invented.
- **`PARTIALLY_SUPPORTED`** — the cited span supports part of the claim but not all
  of it (e.g. the claim states three conditions, the citation only supports two).
  **Never round this up to `SUPPORTED`** — a partially-true claim is exactly the
  silent-wrongness shape this gate exists to catch.

A claim already marked `UNSOURCED` in step 1 is never dispatched here — it already has
its verdict.

### 2a. Before dispatching anything: `$PROFESSOR_VERIFIER_CMD` must resolve

If `$PROFESSOR_VERIFIER_CMD` is unset or empty, stop and emit exactly this, then fail —
matching the shape `professor.py` already uses for `$PROFESSOR_PACK_ROOT`:

```
verify-claims: $PROFESSOR_VERIFIER_CMD is not set. This gate dispatches one
independent check per claim and cannot run without it -- set
$PROFESSOR_VERIFIER_CMD to a headless, single-turn CLI command (the suite applies
no default; `claude --print` is the recommended value) before drafting.
```

**Never fall back to a guessed command, and never skip the gate because the variable is
missing.** A harness with no headless single-turn CLI at all cannot run this gate; that
limitation is named in the redesign doc (§3, §6.7) and is not solved here.

### 2b. What counts as a verdict — the response grammar

**A verdict is recognised by matching the WHOLE response against the grammar below. It
is never found by searching inside a response.** This distinction is the gate, not a
detail of it: every weaker rule that has been tried lets a wrong answer through.

The complete response, after stripping leading and trailing whitespace, must be exactly
two lines:

```
<reason>
<VERDICT>
```

where:

- **`<reason>`** is line one: the reason §2 asks the verifier for, non-empty. Its length
  is not matched against — §2 requests one sentence, nothing here tests for one, and a
  multi-sentence reason is not a parse failure. It may contain any text **except a
  verdict literal other than the one on line two** — see §2d, which explains why that
  single exception exists and what to do when it is hit. The reason is still never *scanned for* the verdict: the verdict is
  always the whole of line two, and §2d is a contradiction check applied after that,
  never a second way to find a verdict.

  **What this grammar does NOT establish about line one — decided 2026-09-17, by
  Serina, after two attempts to test it failed.** **Matching tests line one against the
  requirements stated above in this bullet, and against nothing else.**

  Neither test judges reason quality, so the grammar does not establish that line one is
  a reason at all, that it relates to the claim, or that the verifier reasoned before
  answering. `x`, `.`, and the verdict literal repeated all match.

  That was twice treated as a defect to fix, and both fixes were wrong. Requiring "at
  least one letter" turns on a definition of *letter* that ASCII and Unicode disagree
  about on twelve of twenty-one sampled reasons — under the ASCII reading, which is what
  `grep '[a-zA-Z]'` and C-locale `[[:alpha:]]` give you, a verifier reasoning in CJK,
  Cyrillic, Arabic or Devanagari has every correct verdict blocked as "no reason."
  Requiring line one not to *equal* a verdict literal bans exactly one spelling:
  `SUPPORTED.` defeats it, and so do `**SUPPORTED**` and `"SUPPORTED"` — twenty-one of
  twenty-two measured mutations walked straight through. Worse, that same
  equality-is-brittle property is **load-bearing in the opposite direction** in §2b's
  rejection example 4 below, which relies on a trailing full stop defeating equality on
  line two.

  **Reason quality is a semantic question, and the only robust test for it is another
  model call** — the cost this suite has already refused for cheaper gains. So it is
  stated as a limit, exactly as §2's isolation requirement is stated as "an instruction,
  not a boundary": reason-first ordering makes reasoning the path of least resistance,
  and it is not a guarantee that reasoning happened. §3 acts on the verdict. A verifier
  that answers without thinking produces a verdict this gate cannot distinguish from a
  considered one, and that limitation belongs to the gate, not to this grammar.
- **`<VERDICT>`** is line two, and is one of the three literals `SUPPORTED`,
  `NOT_SUPPORTED`, `PARTIALLY_SUPPORTED`, **matched case-sensitively, in upper case, as
  the entire line.** Not contained in it — equal to it. No colon, no trailing full stop,
  no commentary after it.

Whitespace: leading and trailing whitespace around the whole response, and around each
line, is stripped before matching, and **entirely blank lines are discarded before the
two-line count is taken** — so a verifier that separates its reason from its verdict with
a blank line still matches. **No other flexibility exists.** After blank lines are
discarded, a response of none, of one non-empty line, or of three or more, does not
match — an empty or whitespace-only response has no lines left and is a parse failure.

**The blank-line tolerance is not politeness, it is a measured necessity.** The first run
of this grammar against a real draft returned exactly this:

```
The span shows `_line_number` unconditionally returning `content.count("\n", 0, offset)
+ 1` with no bounds check, no validation, and no raise of any kind.

NOT_SUPPORTED
```

Four earlier dispatches under the same instructions emitted no blank line, so the
behaviour is intermittent rather than consistent — which is worse, because it would make
roughly one run in five fail to parse for a reason that has nothing to do with the claim.
A gate that blocks a correct verdict at random is not stricter, it is noisier, and the
noise would land on exactly the dispatches that did their job. Discarding blank lines
costs none of this grammar's protections: narration lines are not blank, so rejection
example 3 below still fails, and the verdict line must still *equal* a literal.

Because the verdict must *equal* line two in its entirety, `SUPPORTED` being a substring
of `NOT_SUPPORTED` and `PARTIALLY_SUPPORTED` cannot cause a misread. A rule that searched
for `SUPPORTED` anywhere would report a `NOT_SUPPORTED` response as supported — the
gate's own silent-wrongness failure, reproduced inside the mechanism built to catch it.

**Why the verdict comes LAST, and it is the whole point of this ordering — decided
2026-09-16, by Serina, from measurement.** This grammar originally put the verdict first,
`<VERDICT>: <reason>`. That shape requires the answer to be emitted *before* the
reasoning that decides it, and a verifier generating left to right therefore commits to a
literal before it has worked anything out. Real dispatches on 2026-09-16 showed it
then correcting itself inside the reason, where the equality rule gives the correction no
effect:

```
NOT_SUPPORTED: ... — wait, the first two assertions are established, so the correct
verdict is PARTIALLY_SUPPORTED.
```

`PARTIALLY_SUPPORTED` was unreachable under that ordering on every honestly-partial claim
tried. Supplying the three verdicts' definitions did not fix it; supplying an explicit
ordered procedure for composing them did not fix it either, and the `SUPPORTED` /
`NOT_SUPPORTED` controls held throughout, so the cause was positional rather than
wording. **Reason first means the composition happens before the token that reports it.**
Everything the original grammar earned is kept — whole-response matching, equality not
containment, one-line reason, no narration — only the position moved.

**Responses that MUST be accepted, and as what** — these matter as much as the
rejections, because the whole point of the equality rule is that the two longer verdicts
survive it intact:

1. ```
   The span states the retry count as three.
   SUPPORTED
   ```
   → **`SUPPORTED`**.
2. ```
   The citation contradicts the claim.
   NOT_SUPPORTED
   ```
   → **`NOT_SUPPORTED`**, never `SUPPORTED`. Line two is `NOT_SUPPORTED`, which is not
   equal to `SUPPORTED`, so the collision cannot occur.
3. ```
   The span supports two of the three conditions.
   PARTIALLY_SUPPORTED
   ```
   → **`PARTIALLY_SUPPORTED`**, and step 3 blocks on it. Never rounded up.

**Responses that MUST be rejected, not interpreted:**

1. ```
   SUPPORTED: the span states the retry count as three.
   ```
   Rejected: this is the OLD verdict-first shape, and it is one line rather than two.
   Accepting it would reintroduce the exact ordering defect this grammar was changed to
   remove, so it has to fail rather than be tolerated for compatibility.
2. `This claim cannot be classified as SUPPORTED because the citation contradicts it.`
   Rejected: one line, and line two is absent, so there is no verdict at all. **A
   containment check marks this `SUPPORTED`.** It is the exact opposite of what the
   verifier said.
3. ```
   Checking the cited span now...
   The span states the retry count as three.
   SUPPORTED
   Done.
   ```
   Rejected: four lines. A valid verdict line surrounded by other output — the response as
   a whole does not match, and a line-scanning rule would accept it, which means any
   verifier that narrates its work silently becomes trusted.
4. ```
   The span supports two of the three conditions.
   PARTIALLY_SUPPORTED.
   ```
   Rejected: line two is `PARTIALLY_SUPPORTED.` with a trailing full stop, which is not
   *equal* to any literal. Equality is what makes the substring collision impossible, so
   it cannot be relaxed to "starts with" or "contains" for punctuation either.

### 2c. When there is no verdict — parse failure and non-completion

**Disposition for everything in this section: `block`.** Same disposition as any
non-`SUPPORTED` verdict in step 3, reported the same way, and **never `SUPPORTED`**. A
check that did not produce an answer is not an answer.

**Parse failure** — **the response did not match §2b's grammar.** §2b is the whole
definition; apply it, and anything it does not match is a parse failure.

**This clause deliberately does not enumerate the ways a response can fail to match, and
the omission is the point.** It carried such a list until 2026-09-17. Both versions of
that list were measurably wrong — one naming a failure §2b cannot detect, the next naming
a state §2b's normalisation makes unreachable while dropping a constraint §2b does
enforce. A restatement of a grammar is a second copy of that grammar, and two copies
drift. Pointing at §2b cannot drift from §2b. Both failed lists, and the decision to stop
enumerating, are recorded as decision 15 in
`launchpad/Research/the-professor-skill-suite-redesign.md`.

**Non-completion — judged independently of anything stdout contained.** A response can
be perfectly well-formed and still not count, because how the command ended is part of
whether it answered at all:

- **Non-zero exit status.** A command can print a flawless `SUPPORTED: ...` and then
  exit non-zero. Block. Do not read the stdout.
- **Timeout. The default is 120 seconds per dispatch.** Nothing else enforces this:
  dispatch deliberately is not a `tools/professor.py` subcommand (§4), so it does not go
  through `professor_lib/proc.py`, and **the dispatching agent is the only thing that can
  bound the call.** Apply the timeout, kill the command, and block. A hang without an
  enforced bound is an indefinite wait, not a verdict.
- **A response that ends without completing the grammar** — output that stops mid-line,
  or that gives the reason line and then ends with no verdict line. Block.
  **Verdict-last makes truncation safer, not riskier, and this is a real gain from the
  2026-09-16 reordering.** Under the old verdict-first shape a truncated response still
  carried a complete-looking verdict, and only the justification was lost; now a
  truncated response loses the verdict itself and is unambiguously incomplete. A
  half-finished check can no longer look like a decided one.

None of these are recoverable by retrying silently. Report them like any other blocking
finding, naming which claim and which failure.

### 2d. When the reason contradicts its own verdict

**Decided 2026-09-16, by Serina, after five real dispatches demonstrated it.** If the
reason line names any verdict literal **other than** the one on line two, the
response is contradictory: **parse failure, disposition `block`, and never the emitted
verdict.** Match the literals as whole tokens and longest-first, so the `SUPPORTED`
inside `NOT_SUPPORTED` is not mistaken for a competing verdict.

**Matching here is case-sensitive and upper-case, exactly as §2b's verdict line is.**
Only the three literals as spelled count; `not_supported`, `Partially_Supported` and
`partially supported` are not matches and do not trigger this rule. That is deliberate
and it is the boundary of what this check is: it detects a reason that **names** a
competing verdict, never one that merely describes a different conclusion in prose.
Widening it to case-insensitive or to phrases would make it a containment search over
the reason — the precise discipline §2b abandons containment to protect — so the
narrowness is the design, not an omission. §2b's line-two equality test is unaffected
either way.

**This is not hypothetical.** It was observed under the grammar's previous
verdict-first ordering, where the verifier committed to a literal before reasoning and
could only correct itself afterwards, too late to change the parse:

```
NOT_SUPPORTED: The span establishes the 120-character window value and its
sentence-spanning rationale but says nothing about per-repository override via a
`.professor/` configuration file — wait, the first two assertions are established,
so the correct verdict is PARTIALLY_SUPPORTED.
```

**§2b's reordering removed that cause, and this section is deliberately kept anyway.**
Reason-first means the composition now happens before the verdict token, so a verifier
has no structural reason to contradict itself. But "has no reason to" is not "cannot":
the ordering fixed the mechanism that *forced* the contradiction, not every route to
one. A verifier may still reason its way to one conclusion and then emit a different
literal, and if it does, this section is what stops the gate trusting it.

Keeping a guard after removing its cause is intentional here, not belt-and-braces
clutter. The cause was identified by measurement on one verifier command; the contract
is meant to hold for **any** configured `$PROFESSOR_VERIFIER_CMD`, including ones that
behave differently. Deleting the check would make the gate's safety depend on a
behaviour we only ever confirmed for one model.

What this section does is narrow and strictly safe: it refuses to trust a verdict whose
own reason disputes it. The gate cannot tell which of the two the verifier meant, and a
check that did not produce one unambiguous answer has not produced an answer.

**The dispatch prompt must also ask for this**, per §2's item 3: tell the verifier to
emit no verdict literal other than its own in the reason. A rule the verifier is never
told about only produces blocks it could have avoided.

**Accepted cost, stated rather than discovered later.** A verifier that self-corrects
inside its reason is *more* honest than one that does not, and this rule blocks it
anyway. That is deliberate — blocking is recoverable and cheap, and the mirror image is
not: a reason ending "though strictly this is `PARTIALLY_SUPPORTED`" above a line-two
`SUPPORTED` parses as `SUPPORTED` under §2b alone and would otherwise **pass the gate**.
This rule is what catches that shape — a reason that concedes a different verdict **and
names it**.

**What it does NOT catch — named, not solved.** This is a check on *naming*, not on
meaning: it fires only when the reason spells out a competing verdict literal, in upper
case, as a whole token. Two shapes therefore pass it untouched, and both are the same
failure semantically:

- a reason that describes a contradiction **without naming a literal** — "the span
  supports two of the three conditions", above a line-two `SUPPORTED`;
- a reason that names one **in lower case or as prose** — "though strictly this is only
  partially supported", above a line-two `SUPPORTED`. Per the case-sensitivity rule
  above, `partially supported` is not the literal `PARTIALLY_SUPPORTED` and does not
  trigger this check. **This example was wrongly given as a catch in an earlier draft of
  this section; it is not one**, and the correction is recorded rather than quietly
  swapped because the claim was the stated justification for keeping the rule.

Measured on the 2026-09-16 dispatches: of four responses whose reasoning disagreed with
their own emitted verdict, this rule caught the two that named a literal in upper case
and missed the two that only described the disagreement. Detecting either uncaught shape
would mean judging the reason's meaning, which is a second model call per verdict — the
cost the suite already refused for cheaper gains. §2b's reordering is what addresses the
cause; this section is the residue guard, and it is not complete on its own.

## 3. Act on the result

- **All claims `SUPPORTED`** (or zero behaviour claims found, per step 1) — the draft
  passes through to `provenance-log`, same as a `screen-sensitive` `pass` would have.
  This gate does not change what happens after it, only what has to happen before it.
- **Any claim `UNSOURCED`, `NOT_SUPPORTED`, or `PARTIALLY_SUPPORTED`** — the write does
  not proceed, full stop. Report the finding — which claim, which verdict, the
  one-sentence reason, and the citation it was checked against (or that none existed,
  for `UNSOURCED`) — to whichever skill invoked you, in the same shape
  `screen-sensitive`'s `block` and the original design's `check_page` `findings` list
  use, so review has one consistent place to look regardless of which gate produced the
  finding.

There is no partial-write path here. One unsupported or unsourced claim blocks the
whole draft, the same way one `block`-category finding in `screen-sensitive` blocks the
whole write — a page is not "mostly verified."

## 4. Run again, independently, as the final step

**Decided 2026-09-04, by Serina.** Steps 1–3 above run once during drafting so
`draft-page`/`update-page` can fix what gets flagged. That pass does not authorize the
write by itself — immediately before the write is finalized or a PR opens, run this
skill's full procedure again, from scratch, against the finished file. "Unskippable"
above is a prompt instruction to the drafting agent during the first pass, not proof it
actually happened; the second, independent pass is the real gate of record. Do not
special-case this pass as "probably fine since it already passed once" — run it exactly
as thoroughly as the first.

### 4a. Proving the second pass actually re-dispatched

**Decided 2026-09-15, by Serina.** "It ran twice" is unfalsifiable from the outside: a
pass that re-dispatched every claim and a pass that reused the first pass's verdicts look
identical unless something observable distinguishes them. Caching those verdicts is the
obvious optimisation, and it is exactly what this section exists to detect.

**The observable is a per-pass run identifier.** Each pass generates one fresh identifier
before it dispatches anything, and stamps it on every verdict that pass produces. A
verdict carrying the *previous* pass's identifier was not re-checked — it was replayed.

**An identifier alone is not enough, so it is bound to evidence:**

- **One recorded invocation of `$PROFESSOR_VERIFIER_CMD` per cited claim, per pass.** Not
  one per pass. A pass over six cited claims records six invocations; a pass that records
  one has not re-checked the other five, whatever its verdicts are stamped with.
- Each invocation record carries the pass identifier, and **identifies its claim by
  location and citation rather than by reproducing the claim's text** — the same
  discipline `check-page`'s own findings already follow, so this evidence channel does not
  become a way for draft content to outlive the draft.

**What an inspector checks, in order:**

1. Count the cited claims in the finished draft. Count the second pass's invocation
   records. **They must be equal.** Fewer records than cited claims is a replay,
   regardless of what the verdicts say.
2. Every second-pass verdict carries the second pass's identifier — not the first's.
3. Every verdict maps to an invocation record for *that claim* in *that pass*.

**A verdict that fails any of these blocks the write**, with the same disposition as any
other non-`SUPPORTED` outcome in step 3. A replayed verdict is not a verdict; it is the
absence of a second check wearing the first check's answer.

**What this does not prove — named, not solved.** A fresh identifier and a matching
invocation record prove a dispatch *happened*. They do not prove it was *independent*: an
agent could re-dispatch while carrying the first pass's reasoning in context and still
produce a perfectly-shaped record. Isolation remains a property of how step 2 is followed,
not something this observable can enforce. This is the same honest limit as the one
recorded below for claim identification — worth knowing before treating a clean
second-pass record as proof the gate is sound.

## What this gate does not solve

Naming these explicitly so they are never mistaken for silent guarantees:

- **The verifier can be wrong too.** An independent, fresh-context check raises
  confidence that a claim is accurate; it is not proof. Treat a `SUPPORTED` verdict
  as evidence, not certainty.
- **Opinion claims are never checked** (step 1) — this is a deliberate scope limit,
  not a gap to close later.
- **An unreasoned verdict is indistinguishable from a considered one — named
  2026-09-17.** Nothing §2b tests on line one judges whether the verifier reasoned, and
  reason
  quality is a semantic question whose only robust test is a second model call, which
  this suite has refused for cheaper gains. Reason-first ordering (§2b) makes reasoning
  the path of least resistance and is not a guarantee it happened. A verifier that
  answers `Looks fine.` above `SUPPORTED` passes this gate exactly as one that read the
  span carefully does. §2b hands this limit here rather than claiming to solve it.
- **Claim identification itself is not independently verified — named 2026-09-05,
  after a review pointed out this wasn't stated anywhere.** Step 1's extraction (which
  sentences count as behaviour claims at all) is done by the same drafting agent whose
  work is being checked, not by an isolated pass the way step 2's dispatch is. A claim
  the drafting agent mis-classifies as opinion, or simply never notices as a claim,
  never reaches this gate — running the whole procedure twice (step 4) re-runs the
  same extraction twice, which catches a *transient* mistake but not a *systematic*
  one the same agent would make identically both times. This is not solved by this
  gate; it is a real, named limit on what "mandatory and unskippable" actually
  guarantees.

**No longer out of scope for the suite** (though still not this skill's own job):
cross-page contradiction — a claim well-cited and internally consistent on its own page
while contradicting a different page elsewhere in the library — is handled by
`library-index` `sweep`, not here, because it needs the whole library at once, not one
draft in isolation.

## Summary checklist

- [ ] Every behaviour claim in the draft was identified — opinion/judgement claims
      were correctly excluded, not silently skipped alongside them
- [ ] Every claim with no citation was marked `UNSOURCED` — not silently skipped, and
      not sent through the per-claim dispatch it doesn't need
- [ ] Each cited claim was checked in a genuinely fresh, isolated context — not the
      drafting agent's own context, and not batched together with other claims'
      verdicts visible
- [ ] Every dispatch carried the task, the decide-only-from-the-span instruction, and
      §2b's response format — a dispatch sent without them is not a stricter check, it
      is an unanswerable one
- [ ] No `PARTIALLY_SUPPORTED` verdict was rounded up to `SUPPORTED`
- [ ] Any verdict other than `SUPPORTED`, on any single claim, actually blocked the
      entire write — not logged as a warning and allowed through
- [ ] The reported finding names the specific claim, verdict, reason, and citation (or
      that none existed, for `UNSOURCED`). **The reporting agent never substitutes a
      summary of its own** — not a generic "verification failed", and not a tidied-up
      paraphrase. The reason is passed through as the verifier gave it, whatever that
      was: §2b does not require it to be informative, so a reason of `.` satisfies this
      item, and a thin reason is itself a signal about the verifier that a substitution
      would hide.
- [ ] This whole procedure ran a second time, independently, against the finished
      file, immediately before the write — not treated as already satisfied by the
      first, mid-draft pass
- [ ] The second pass carries its own fresh run identifier, and one invocation record
      per cited claim — the record count equals the cited-claim count (§4a), and no
      verdict carries the first pass's identifier
- [ ] `$PROFESSOR_VERIFIER_CMD` was confirmed set before any dispatch — an unset
      variable failed loud with §2a's specific message, not a silent fallback or a
      generic crash
- [ ] Every verdict came from matching a response **whole** against §2b's grammar —
      never from finding a verdict word inside a longer response, and never from a
      case-insensitive or partial match
- [ ] Every dispatch told the verifier not to name a competing verdict literal in its
      reason (§2 item 3), and every response whose reason named one anyway was blocked
      as contradictory under §2d rather than trusted for its emitted literal
- [ ] Every dispatch was bounded by the §2c timeout, and a non-zero exit, a timeout,
      a parse failure or a truncated response each blocked — none of them was read as
      a verdict, and none was silently retried

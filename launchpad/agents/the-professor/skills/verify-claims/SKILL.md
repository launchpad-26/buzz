---
name: "verify-claims"
description: "Adversarially re-check that each behaviour claim in a gated draft has a citation at all, and that the citation actually supports it — the third, mandatory, unskippable gate before any write, run twice per draft."
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
headless, single-turn CLI command — suite default `claude --print`, same override
pattern as `$PROFESSOR_PACK_ROOT`), feeding it only the cited source span and the
claim's exact sentence, and capture its stdout as the verdict. Confirm
`$PROFESSOR_VERIFIER_CMD` resolves before dispatching anything — same fail-loud
requirement as `$PROFESSOR_PACK_ROOT` elsewhere in this pack, not a silent fallback to
a guessed command. A harness with no headless single-turn CLI available at all cannot
run this gate — that limitation is real and named, not solved by this decision.

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
tied to a specific cited source (the exact commit + path + span `check-page` already
resolved for it in the earlier gate).

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
subprocess — a genuinely separate check in **fresh context** — give it only the cited
source's exact span and the claim's exact sentence, nothing else. Deliberately
withhold:

- the rest of the draft
- the drafting agent's own reasoning or notes
- any other claim's verdict from this same run

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

## What this gate does not solve

Naming these explicitly so they are never mistaken for silent guarantees:

- **The verifier can be wrong too.** An independent, fresh-context check raises
  confidence that a claim is accurate; it is not proof. Treat a `SUPPORTED` verdict
  as evidence, not certainty.
- **Opinion claims are never checked** (step 1) — this is a deliberate scope limit,
  not a gap to close later.

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
- [ ] No `PARTIALLY_SUPPORTED` verdict was rounded up to `SUPPORTED`
- [ ] Any verdict other than `SUPPORTED`, on any single claim, actually blocked the
      entire write — not logged as a warning and allowed through
- [ ] The reported finding names the specific claim, verdict, reason, and citation (or
      that none existed, for `UNSOURCED`) — never a generic "verification failed"
- [ ] This whole procedure ran a second time, independently, against the finished
      file, immediately before the write — not treated as already satisfied by the
      first, mid-draft pass
- [ ] `$PROFESSOR_VERIFIER_CMD` was confirmed set before any dispatch — an unset
      variable failed loud with a specific message, not a silent fallback or a
      generic crash

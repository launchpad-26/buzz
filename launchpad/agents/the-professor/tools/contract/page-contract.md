# The Professor's default page contract

This is the suite's **default** documentation contract — used for any target repo
that doesn't define its own at `.professor/contract.md`. See
`launchpad/Research/the-professor-skill-suite-redesign.md` §3 for the resolution
order this file participates in, and §9 for the status of the gate script that will
eventually check a draft against this contract mechanically (not yet built — this
file is the spec, checked by hand today per `screen-sensitive`'s own "run it by hand
until the script exists" instruction, and by `draft-page`/`update-page` following it
directly).

This contract is deliberately smaller than the handbook's own (the one
`launchpad-26/handbook`'s `docs/page-contract.md` defines, and that this pack's
original build read directly): the handbook's contract governs a corpus that
synthesizes claims about five *other* repositories, and needs a taxonomy for which
one each claim is about. A target repo's own documentation is, by default, about
itself — one relevant "which repo," not five — so this contract doesn't carry that
taxonomy. A target repo that wants it back (because it, too, documents claims about
other repos) defines its own contract with that taxonomy restored.

## Required frontmatter

```yaml
---
title: "<page title>"
category: "<resolved by library-index in place mode>"
author: "<the-professor, or a human maintainer's name if a human is credited for the page's judgement calls>"
generated_by: "the-professor"
generated_at: "<ISO 8601, the page's first-draft timestamp — never updated after>"
---
```

`author` is who is accountable for the page's opinion claims (see the claim rule
below) — it does not have to be `the-professor`; a human who reviewed and takes
ownership of the page's judgement calls may be named instead, same as the original
handbook contract's own convention.

## The claim rule

Every sentence in the body that asserts something is either:

- **A behaviour claim** — how the documented unit actually works today. It carries a
  citation to a real path and a real commit in the target repo's own history (or, for
  a genuinely external dependency, a resolved pin in the cited repo — see
  `draft-page`'s procedure for both cases), **and, where the claim describes a
  specific piece of code rather than a whole file's general shape, the line range
  that actually backs it** (fixed 2026-09-05 — `verify-claims` and contradiction
  detection both need this to check *the right lines*, not just that the file and
  commit resolve; see §8's `span` field for the exact format).
- **An opinion claim** — what should be true, or what is worth watching. No citation;
  attributed instead to the page's `author` field.

A claim is never both in the same sentence. This is the one rule this contract keeps
unchanged from the original handbook contract, because it isn't about which repo a
page covers — it's about not letting a fact and a judgement call hide inside the same
sentence, which matters regardless of scope.

## Inline claim tags (mechanical marker for the claim rule)

**Added 2026-09-05, during the fix round for issue #2100's tool-layer build, not by
this contract's original authors reviewing and approving this exact syntax.** The
claim rule above states *what* a behaviour claim and an opinion claim are; it does not
say how a mechanical check tells, sentence by sentence, which kind a given sentence
is — prose alone cannot carry that distinction deterministically. `check-page`'s
implementation already requires an explicit inline tag to make the distinction
mechanical, so this section documents that tag convention as part of the contract,
formalizing what the shipped code already does rather than proposing something new.

A sentence asserting a **behaviour claim** carries a trailing
`(behaviour: <citation>)` tag, where `<citation>` is one of:

- `<path>@<40-hex-sha>` — a citation to the target repo's own tree (whole-file claim)
- `<path>@<40-hex-sha>#L<n>[-L<m>]` — the same, with the line range the claim actually
  describes (see the claim rule's own span requirement above)
- `<repo>:<path>@<40-hex-sha>[#L<n>[-L<m>]]` — a citation to a genuinely external
  repo, for a claim about a dependency rather than the target repo itself
- `(behaviour: none)` — a behaviour claim written with no citation at all,
  deliberately still tagged so a gate can flag it as the specific rule-1 violation it
  is, rather than a claim the gate never noticed was a behaviour claim in the first
  place

A sentence asserting an **opinion claim** carries a trailing `(opinion)` tag, no
citation — attributed to the page's `author` field per the claim rule above.

A sentence carrying neither tag makes no claim a gate can mechanically evaluate (for
example, connective prose, a heading, or a purely structural sentence) and is not
itself a rule violation; a gate checking this contract only evaluates sentences that
carry one of these two tags. See "What a gate checking this contract should flag"
below — its "behaviour claim with no citation" bullet is the `(behaviour: none)` case
above, and its "mixed-claim" bullet is a sentence carrying both tags at once.

## Provenance

Every section carries an inline provenance marker (the HTML comment format
`the-professor-skill-suite-redesign.md` §8 defines) directly above its heading — this
is part of the draft's *content*, written by `draft-page`/`update-page` before either
gate runs, not something the gate waits on a separate ledger write for. **The
mechanically-checkable requirement is narrower than "provenance exists," on purpose:**
a gate running against a not-yet-published scratch file cannot check whether an entry
has been appended to `.professor/provenance/<page-slug>.jsonl`, because nothing has
been appended yet — publication (and the ledger append that goes with it) happens
*after* the gate passes. What the gate checks instead is that the marker is present,
well-formed, and internally consistent with the draft's own citations (below); the
ledger append itself is a downstream fact `library-index`'s `sweep` mode audits
separately, against already-published pages, not something `check-page` can verify at
draft time.

## What a gate checking this contract should flag (spec for §9's script)

Mechanically, "a behaviour claim" and "an opinion claim" below mean a sentence
carrying the `(behaviour: ...)` or `(opinion)` inline tag defined in "Inline claim
tags" above — that section is what makes the two bullets immediately below
mechanically checkable at all, rather than a matter of prose judgement.

- A citation whose path does not exist in the repo/commit it names
- A behaviour claim with no citation at all
- A behaviour claim citing a specific line range (`#L<n>` or `#L<n>-L<m>`) that is out
  of bounds for the cited file at the cited commit (fixed 2026-09-05 alongside the
  claim rule's own span requirement, above)
- A section with no inline provenance marker directly above its heading, or one whose
  `sources` don't match the citations actually present in that section's text
- A sentence that reads as both a behaviour claim and an opinion claim (mixed-claim)
- Frontmatter missing any required field above, or an unparseable frontmatter block
  (treated as *worse* than a finding — it means nothing else in this list could be
  checked either, same as the original design's `skipped` category)

**Deliberately not on this list, fixed 2026-09-05 after a review caught the
contradiction:** "a section with no matching provenance *record*" (the ledger entry,
as opposed to the inline marker two bullets above) cannot be `check-page`'s job — the
"Provenance" section above already explains why: at draft time, against a
not-yet-published scratch file, no ledger entry exists yet for `check-page` to find
missing. Checking that a published page's ledger entry actually exists is
`library-index` `sweep`'s job, against already-published pages, not this gate's.

## What this contract deliberately does not specify

- A fixed category list — `library-index` resolves categories from the target repo's
  own structure; this contract doesn't predetermine them.
- A fixed claim-prefix vocabulary — a target repo whose documentation cites multiple
  other repos should define its own contract with one, rather than stretching this
  default to fit a case it wasn't written for.

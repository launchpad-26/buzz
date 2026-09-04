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
  `draft-page`'s procedure for both cases).
- **An opinion claim** — what should be true, or what is worth watching. No citation;
  attributed instead to the page's `author` field.

A claim is never both in the same sentence. This is the one rule this contract keeps
unchanged from the original handbook contract, because it isn't about which repo a
page covers — it's about not letting a fact and a judgement call hide inside the same
sentence, which matters regardless of scope.

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

- A citation whose path does not exist in the repo/commit it names
- A behaviour claim with no citation at all
- A section with no inline provenance marker directly above its heading, or one whose
  `sources` don't match the citations actually present in that section's text
- A sentence that reads as both a behaviour claim and an opinion claim (mixed-claim)
- A section with no matching provenance record
- Frontmatter missing any required field above, or an unparseable frontmatter block
  (treated as *worse* than a finding — it means nothing else in this list could be
  checked either, same as the original design's `skipped` category)

## What this contract deliberately does not specify

- A fixed category list — `library-index` resolves categories from the target repo's
  own structure; this contract doesn't predetermine them.
- A fixed claim-prefix vocabulary — a target repo whose documentation cites multiple
  other repos should define its own contract with one, rather than stretching this
  default to fit a case it wasn't written for.

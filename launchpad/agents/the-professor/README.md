# The Professor

A mentoring persona pack that drafts documentation pages: it resolves pins,
tags claims with provenance, and writes them up in a single consistent voice.

## Model

`anthropic:claude-sonnet-4-20250514` (`model` field, `provider:model-id` format
per `PERSONA_PACK_SPEC.md` §4/§10). The Professor's `draft-page` skill is a
multi-tool-call job — resolving pins, fetching source content, checking claims
against it — before it ever writes a sentence, so it needs a model capable of
sustained tool-calling and reasoning across that chain, not just prose
generation. This is a starting choice, not a benchmarked one; no comparison
against a cheaper tier has been run.

## Temperature: 0.4 (starting value, not yet validated)

`temperature: 0.4` is set in `personas/the-professor.persona.md`. This is a
**reasoned starting value**, not an empirical one — no real drafting attempt
has happened yet. `the-professor-design.md` §6 lays out the actual tension:

- **Factual synthesis wants it low.** The Professor's job is not just prose —
  it resolves pins, decides whether a source supports the sentence in front of
  it, and tags which claims came from where. Per the design doc, "tools
  resolve metadata, not meaning": fetching a source doesn't stop the model from
  inventing what that source says, which claim to make from it, or what to
  quietly drop. That's the accuracy-sensitive part of the job, and it's the
  part the whole provenance/claim-tagging gate exists to catch.
- **Voice wants room.** The entire point of a fixed persona (rather than
  "whatever model drafted this page") is a consistent, readable author across
  many pages. Too low a temperature risks flat, repetitive prose that reads
  like a template rather than a voice.

**Where this pack lands, and why:** the failure mode that actually damages
trust in a documentation corpus is a fabricated or misattributed claim, not a
slightly less varied sentence. A page with a plain but accurate voice is
recoverable; a page with a fluent but invented claim is not — a reader has no
way to tell it apart from a correct one without redoing the verification work
themselves. So this pack leans toward the factual side of the tension, but
not all the way to it: The Professor's output is longform, multi-paragraph
prose meant to read as one person's writing across a whole corpus, not
terse structured verdicts (contrast the security-reviewer persona in
`examples/meadow-core`, which runs at `0.3`). `0.4` sits below the
`examples/meadow-core` default (`0.7`, used by its conversational
orchestrator) and below its architecture-reviewer persona (`0.5`, prose that
leans more discretionary than ours), reflecting that claim fidelity is this
persona's primary risk — while staying above the most conservative end of
that range so the prose doesn't flatten out.

**This is explicitly not evidence.** `the-professor-design.md` §6 is clear
that the meadow-core numbers are "two downward overrides from a default... a
real pattern, and still two choices in one example pack rather than a law."
`0.4` is a reasoned starting point, chosen before any real drafting attempt
exists to test it against.

**Open dependency:** whether `temperature` (and `model`) reach any runtime at
all is downstream of a runtime decision this plan has not made yet (tracked as
a later step in this plan, not this one). Pack resolution currently projects
`temperature` only to `GOOSE_TEMPERATURE`, per `the-professor-design.md` §6 —
if the eventual runtime isn't Goose, this field may configure nothing. That
open question doesn't block setting the field now (the pack format requires
it), but it does mean this value shouldn't be read as confirmed-effective yet.

**Validation still to come:** per this plan, a real drafting attempt (a later
step) will exercise this persona against actual pages, and the step after that
records what was observed — whether `0.4` produced accurate, consistently
voiced drafts, or needs to move. Nothing in this document should be read as
that observation; it is the reasoning that precedes it.

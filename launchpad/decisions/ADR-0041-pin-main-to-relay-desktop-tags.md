---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#305
decided_in: launchpad-26/buzz#305
supersedes: none
---

# ADR-0041 — Pin `main` to relay/desktop upstream tags with a standing prompt

## Decision

Option A. The vendor branch `launchpad-26/main` is advanced only to
named upstream release tags — `relay-v*` or `desktop-v*` — ignoring the mobile RC stream,
and each pin is recorded as the resolved commit SHA alongside the tag name. A standing
automated report prompts the drop decision; a human takes the drop deliberately.

**The first move is an explicit one-off exception to that rule.** `main` should move to at
least `launchpad`'s merge-base with upstream so it is a truthful baseline, and that
merge-base is not a tag: `git merge-base origin/launchpad upstream/main` resolves to
`f8692fa9b52ddcfeb4b95fb4862109983509f131`, and `git describe --tags --exact-match` on it
answers `fatal: no tag exactly matches`. Nor can a qualifying tag stand in for it — measured on
2026-08-26, no tag in the filter resolves to that commit. Six qualifying tags
(`desktop-v0.5.3`, `.4`, `.5`, `relay-v0.1.1`, `v0.2.0`, `v0.2.1`) *are* ancestors of it,
so they are reachable history rather than substitutes; taking any of them would move `main`
backwards from the baseline, not to it. An earlier revision of this record claimed no
qualifying tag was an ancestor at all, which is false. The one-off is therefore stated as an exception rather
than dressed up as compliance; every move after it goes to a qualifying tag.

## Context

`main` sits exactly on `mobile-v0.9.0-rc.1` (commit `f53bbd115`, 2026-08-06), while
`launchpad`'s merge-base with upstream is 2026-08-17 — eleven days later — so `git diff main
launchpad` mixes upstream's own work into the cohort's divergence. #305 measured `main` as 0
ahead / 228 behind on 2026-08-21; re-measured on 2026-08-26,
`git rev-list --left-right --count origin/main...upstream/main` reports `0 266`. The
"behind" figure moves with every upstream push and should be re-taken before it is relied
on; the durable part is the shape — `main` is strictly behind and never ahead, because the
pin is deliberate and nothing pushes to it.

Tags are the natural pin because upstream publishes and tests them; recording the SHA
defends against tag mutability.

**The frequency argument does not distinguish the options, and this record does not use
it.** #305 rejected Option B ("pin to a tag, any tag") on cost — *"seven drops in fifteen
days on the current tag rate, most of them for a mobile RC the fork does not ship"* — and
described upstream's stream as dominated by mobile RCs. Both halves are wrong on the tag
record. Measured on 2026-08-26 with `git for-each-ref --sort=creatordate` over
`refs/tags/desktop-v*` and `refs/tags/relay-v*`, **fourteen tags matching Option A's own
filter** were created after the current pin: thirteen `desktop-v*`, from `desktop-v0.5.6`
(2026-08-07) through `desktop-v0.5.18` (2026-08-21), plus `relay-v0.2.1` (2026-08-08). Over
the same span upstream created 22 tags in total, of which 8 are `mobile-v*` — so the RC
stream is the *minority*, not the dominant one, and the chosen filter fires at least as
often as the rule it was preferred over. Option A is not the lower-cadence option. What it
actually buys is *coherence of the pin* — every candidate is a relay or desktop release the
fork ships — not fewer prompts. A prompt is not a drop: the standing report notices a
qualifying tag, a human decides whether to take it, and declining fourteen prompts is cheap
in a way taking fourteen drops is not.

Rejected: per arbitrary commit (C, no coherence guarantee), time-boxed HEAD (D, the mirror
behaviour curation rejects), and demand-driven-only (E, what produced the unnoticed
gap — valid as an additional trigger, not as the sole rule).

## Consequences

- `main` becomes a baseline someone can rely on; the first action fixes the current
  inconsistency, as a named exception.
- The gap becomes a stated policy choice with an owner rather than an unnoticed default.
- A tag filter can be wrong the first time upstream tags something important under a name
  it does not match; recording the SHA bounds the risk.
- The standing report will fire often — fourteen qualifying tags in the nineteen days
  between the current pin and 2026-08-26 — so the cost of the rule lands on triaging
  prompts, not on the filter being too narrow to notice anything.

## Security implications

The pin determines how long an upstream security fix waits before it is visible to the
cohort. The standing prompt is wired to the upstream-intelligence work so fixes that should
jump the queue are surfaced; pinning to a published, tested tag is a stronger provenance
position than an arbitrary mid-series commit.

## Supersedes

none

## Provenance

Drafted by an agent from #305's options. Jeffrey (@tucktuck101) made the decision on
2026-08-31 after reviewing options A–E with their positive and negative consequences —
including the record's own correction that Option A does not reduce prompt cadence, and
the named one-off merge-base exception — and the agent's recommendation of Option A; he
replied verbatim: **"a"**. Full alternatives remain in #305. The tag list, the merge-base,
the `describe` result and the ahead/behind counts in this record were measured against the
local clone on 2026-08-26 with the commands shown; #305's own 228 figure is dated
2026-08-21 there. This record does not conflict with ADR-0005, whose Decision is scoped to
the `launchpad/deploy/` wrapper and the five sanctioned image-provenance files.

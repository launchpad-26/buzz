---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#604
decided_in: launchpad-26/buzz#604
supersedes: none
---

# ADR-0029 — Evidence precedence is contextual, not fixed, and escalates on conflict

## Decision

The corpus author/generator ranks evidence contextually by claim type, rather than applying
one fixed hierarchy to every claim, and stops for human escalation on material
contradictions instead of silently resolving them.

For claims about how the system **currently behaves**, executable evidence — code, config,
schema, passing tests — is authoritative over documentation, GitHub history, or inference.
For claims about **intended or authorized behavior**, accepted normative decisions (ADRs,
ratified specs) are authoritative over everything else, including code that has since
drifted from them without a corresponding decision update. GitHub history, team knowledge,
and inference may supply context but are never treated as fact on their own; they stay
attributed to their source and distinguishable from FACT claims (Ruling 4).

When two authoritative sources disagree in a way this ordering doesn't resolve — an accepted
spec and current code both claiming authority but contradicting each other, say — the corpus
author stops and records the contradiction rather than picking a side. The affected node
stays unestablished/flagged until a human resolves it.

This rejects a single fixed hierarchy applied uniformly to every claim (option 2) and
latest-timestamp-wins (option 3).

## Context

#602's corpus is synthesized from sources that routinely disagree with each other: an
accepted ADR can go stale relative to code that changed without updating it; a maintained
doc can lag a schema migration; GitHub discussion can preserve a plan later reversed without
a formal record. #604 asked how the corpus author reconciles that when producing one node's
content.

A single fixed hierarchy — for example, "spec always beats code always beats docs" — was
considered and rejected because no one ordering is correct for every claim type. Behavior
claims need current, executable evidence as the tiebreaker: a spec that hasn't been updated
to match a deliberate code change would let a fixed "spec wins" rule assert wrong behavior as
fact. Intent/authorization claims need the opposite tiebreaker: code that quietly drifted
from an accepted decision should not silently overwrite what was actually authorized,
especially given #604's own security-implications note that incorrect precedence could
present stale or unauthorized behavior as current security policy.

Latest-timestamp-wins was also considered and rejected: recency doesn't establish authority,
and treating it as if it did would let an old, superseded GitHub comment outrank an accepted
spec purely for having been touched more recently.

## Consequences

**Good.** Conflicts stay visible with attributable sources, rather than being silently
resolved by whichever agent happens to author the node — matching the corpus's broader
review-before-trust posture (Ruling 2, Ruling 4).

**Good.** Behavior claims and intent/authorization claims each get the tiebreaker suited to
them, instead of one rule that is right for one claim type and wrong for the other.

**Bad.** More expensive to implement and validate than a single fixed ranking — evidence
collectors and reviewers need to retain enough source identity to classify a claim's type and
replay how it was ranked, and #605's validator has to check that classification rather than a
flat list.

**Bad.** Escalating on material conflict means some nodes stay unestablished/flagged pending
a human decision, rather than the corpus always producing a confident answer. That is
accepted as the safer failure mode.

## Security implications

Incorrect precedence could present stale or unauthorized behavior as current security
policy, so this is a security decision as much as an editorial one. Repository and GitHub
text remain untrusted evidence for ranking purposes only, never instructions to the
authoring agent. Private evidence must not be copied into the public corpus to resolve a
conflict; where evidence can't be published, the claim stays unestablished rather than
asserted from a source that can't be shown.

## Provenance

Decided by Serina McFall in conversation on 2026-08-25, after an agent-drafted
recommendation.

**Her call:** contextual precedence with escalation on conflict (option 1), over a fixed
hierarchy (option 2) and latest-timestamp-wins (option 3, already expected to be rejected).

**The recommendation:** drafted by an AI agent (Claude Sonnet 5) on 2026-08-25, on the
reasoning that a fixed hierarchy can't serve both behavior claims and intent/authorization
claims correctly at once, and that escalating on real contradictions is the safer default
given the security stakes named in the issue itself. The agent drafted the recommendation;
Serina reached the same option independently before it was given, and confirmed it.

---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#296
decided_in: launchpad-26/buzz#296
supersedes: none
---

# ADR-0037 — The sync agent resolves by replay only; all other conflicts escalate to a human

## Decision

Choose Option A (replay only). The change agent may apply `rerere` replays and
configured merge drivers, and nothing else, when resolving vendor-drop conflicts.
Any residual conflict — including a three-way merge the agent believes is
unambiguous — escalates to a human with the context bundle.

This outcome was selected automatically under @tucktuck101's explicit approval for the
2026-08-25 ADR-clearing session. Jeff authorized automated selection of Low and
clear-Medium ADR outcomes; he did not personally select this individual outcome.

## Context

PRD #273 requires a change agent that "resolves what it can safely resolve, and escalates
the rest", but drew no boundary. The current backlog supplies real examples: `Cargo.lock`
(both sides change 18 lines — regenerable), `.github/workflows/ci.yml` (textual but a human
must decide the survival of the fork's step), `lefthook.yml` (fork's one line vs upstream's
near-rewrite), and `desktop/src-tauri/src/managed_agents/runtime.rs` (code-motion vs edit,
needs a build). Upstream's new `bin/.lefthookrc` also merges cleanly while reintroducing a
filed bug (#196), demonstrating that a clean merge is not evidence of a correct merge.

Replay-only is the smallest trust surface: the agent never interprets untrusted upstream
text, only replays hashes of resolutions a human already performed. The cost is that every
novel resolution is done once by a human — which is the point.

## Risk classification

**Clear Medium (6/12), high confidence.** Blast radius 2; reversibility 1;
security/trust 1; data/state 0; contracts/dependencies 1; operations 1. No hard
High-risk trigger applies. This bounds automation authority narrowly and contains the
untrusted-upstream surface; it does not grant the agent interpretive authority.

## Consequences

- The merge workflow and escalation path become writable.
- A replay-only boundary means the agent never reads upstream diffs to decide — the
  containment question (#303) carries a materially smaller load.
- The first drops escalate on all four live conflicts; that is the price of the boundary.
- Task #297's escalation work item is unblocked by this record.

## Security implications

Wider resolution authority would let automation act on untrusted upstream text without a
human reading it, and conflict resolution is an unusually good place to hide a change.
Replay-only bounds that: automation acts only on hashes of prior human resolutions, never
on an interpretation of the upstream diff.

## Supersedes

none

## Provenance

Selected and recorded by an agent under Jeff's explicit, session-only authorization
for lower-risk ADRs. Full alternatives remain in #296.
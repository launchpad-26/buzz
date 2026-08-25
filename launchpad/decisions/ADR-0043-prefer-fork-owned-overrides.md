---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#307
decided_in: launchpad-26/buzz#307
supersedes: none
---

# ADR-0043 — Prefer fork-owned overrides; in-place edits require a recorded justification

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human and #307's *Decision outcome*
is still blank. When a human states the outcome in #307, this record's `status` becomes
`Accepted`.

The proposed option is A. The default for a standing disagreement with upstream is a
fork-owned file that overrides, wraps, or delegates to upstream's — never a copy. The
distinction between *override* (delegates to upstream, keeps receiving upstream's changes)
and *copy* (diverges silently) is explicit: copies are prohibited.

**This rule governs the form a divergence takes, not whether one is permitted.** §3's
exception list stays closed and this record does not add to it; whether a given file may
diverge at all is still decided by §3 and by an ADR per exception. §3 is amended by this
record only to state the override-first preference, so the two documents do not disagree.

**Where the justification lives.** An in-place edit to an upstream file is allowed only
with a recorded justification, and the durable home for that justification is the
divergence ledger row for the file — not the pull-request body, which is not a record
anyone can query later. The PR body is where the reason is *written*; the ledger is where
it *lives*.

**Dependency, stated plainly: the decision is settled but the ledger does not exist yet.**
#294 was settled by a human on 2026-08-26 and defines the ledger's contract, so the
*decision* this rule depends on is not in doubt. What is outstanding is its record
(ADR-0047, pull request #1443, still open) and the ledger file itself, which does not exist
on `launchpad`. Until the file exists, this rule cannot be complied with as written. An
earlier revision described #294 as "proposed rather than settled", which was wrong. In the interim the justification
goes in the pull-request body alone, and every such edit is a row owed to the ledger once
it exists. Whoever accepts ADR-0047 should expect that backlog.

## Context

Measured on 2026-08-21 (#307; the tip moves, so re-measure before relying on these):
of 48 diverged upstream files, 27 are edits to upstream's files — the entire conflict
surface — and 20 of those have no recorded reason.

ADR-0005 already chose a wrapper for `deploy/compose/run.sh` and rejected forking
`docker.yml` into a copy. Its reasoning is that a copy trades *"a conflict that Git shows
you for a divergence that nothing does"*, and it states the principle as *"A conflict you
must resolve is better than a copy you forget to."* This record generalises that
precedent and adds the justification gate. It applies to work not yet done; the 27
existing edits are not worth retrofitting.

## Consequences

- The form of divergence has a governing rule; the 20 silent edits stop being the pattern.
- The justification is owed to the ledger at the moment of divergence — the exact gap the
  ledger exists to fill.
- Rust/TSX often have no override mechanism, so the rule will frequently resolve to "edit
  in place, justification: no alternative" — honest, and it leaves the ledger complete.
- Until ADR-0047 lands there is nowhere durable to put the justification, so compliance is
  partial by construction and a backlog of owed rows accumulates.
- §3 gains a paragraph stating the preference. The exception list is unchanged in length.

## Security implications

An in-place edit means every upstream fix to that file arrives as a visible conflict —
delayable but visible. A durable decline on a wholly fork-owned file means upstream's fixes
to the *upstream* file keep flowing untouched — the safer posture. A copying wrapper
silently stops receiving upstream fixes with nothing reporting the gap: strictly worse than
a conflict and explicitly rejected by this record.

## Supersedes

none

## Provenance

Drafted by an agent from #307's options; the decision itself is pending a human, as stated
at the top of *Decision*. Full alternatives remain in #307.

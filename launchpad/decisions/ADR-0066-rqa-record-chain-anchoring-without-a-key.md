---
status: Accepted
date: 2026-09-16
issue: launchpad-26/buzz#2298
decided_in: agent session — no addressable comment exists; see Provenance
supersedes: ADR-0063
---

# ADR-0066 — The review record is a hash chain with an externally anchored head, and no key

## Decision

RQA's review record is made tamper-evident by a **hash chain over every entry, with the chain head
periodically published outside the operator's machine**, and **no HMAC and no operator-held key**. This
supersedes [ADR-0063](ADR-0063-rqa-record-provenance-integrity.md), which chose a hash chain plus an
operator-held HMAC.

Specifics that are part of the decision:

- **The HMAC key, and every credential store RQA reached to obtain it, are removed.** No key is read,
  written, rotated or held; the operator has no key to keep and none to lose.
- **The hash chain is retained unchanged.** It continues to detect accidental corruption, interrupted
  writes, reordering, and any edit by an actor who does not recompute the chain.
- **The chain head is published to a location the reviewed agent cannot rewrite**, so that a record
  which has been truncated or wholly rebuilt is detectable by comparing the local head against the
  published one. Which location, and how often, is implementation work bounded by the constraints in
  Consequences below — it is not settled here.
- **A missing or stale anchor degrades, it never blocks.** As under ADR-0063, an append that cannot
  reach the anchor succeeds and records itself honestly; verification reports the affected span as
  unattested rather than as a break. A failed publish must be recorded and retried, never silently
  dropped.
- **Only P-12 writes the record**, unchanged from ADR-0063. `RQA-NFR-022` and `RQA-NFR-032` — provenance
  is written by RQA, never by reviewed content or model output — are untouched by this decision.

## Context

ADR-0063 chose a hash chain plus an operator-held HMAC, and recorded at the time that the margin over a
plain hash chain was thin. Implementation and re-examination together showed that the margin is thinner
than estimated, and that it defends the wrong thing.

**The key does not defend the actor this record exists to trace.** ADR-0063 states that RQA must read the
key on every append, so "any process running as the operator can read it too". #2006's Security bullet 4,
as amended on 2026-09-04, bounds the guarantee to the operator's trust boundary and explicitly does not
defend against a compromised operator machine; `RQA-NFR-028`'s fit criterion carries that bound. An agent
running with the operator's authority — the actor most likely to touch this record — is therefore already
outside the threat model, and the key does not stop it.

**The record's purpose is forensic, not adversarial.** What this record is for in this repository is
tracing why something happened after the fact: agents go off the rails, and the record is how anyone
reconstructs what they did. That capability comes from *what is written* — the twelve elements
`RQA-FR-012` reconstructs, read back by `explain` — not from how those entries are protected. No option
considered in #2298 added or removed a single field, so the HMAC contributed nothing to the capability the
record exists for.

**What does matter for that purpose is completeness, and that is where ADR-0063 failed.** An agent that
goes wrong does not forge its log; it crashes, hangs, is killed, or dies mid-write. The entries that
matter most are the last ones, because the end of the log is where it went wrong. ADR-0063 names this
blind spot itself: `verify` "walks the rows that are present and returns `ok=True` on a complete walk,
with nothing to compare an endpoint against", so deleting a job's last entries leaves a prefix that
verifies clean — and "a per-row HMAC authenticates the rows that remain, not their absence". **A truncated
audit log is worse than an absent one, because it looks complete**, and truncation is exactly what a
crashed agent produces. An externally anchored head is the one mechanism considered that detects it.

**The cost of the key had also become disproportionate.** The keychain read was macOS-only, failing every
append on Linux (#2272); PR #2287 added Linux Secret Service support; Windows would have required a third
integration. The proposed remedy — a cross-platform credential abstraction — meant RQA's first third-party
runtime dependency in a deliberately stdlib-only skill whose CI fails collection on any such import, a
dependency-delivery mechanism that does not exist, a CI change, a Windows backend no available runner can
exercise, and a Secret Service daemon that headless operators do not have.

**No requirement changes.** `RQA-NFR-028`'s fit criterion is mechanism-free: tamper-evidence is satisfied
by "a signed **or otherwise integrity-checked** record", and a hash chain is one. #2006's non-goals exclude
prescribing implementation mechanisms. No requirement is retired, renumbered or re-derived, and no PRD
amendment is required by this decision.

Affected part: **P-12** (record). Requirements: RQA-NFR-028, RQA-NFR-022, RQA-NFR-032.

## Consequences

- **Good.** Operators have no key to keep, and losing one can no longer render old records unverifiable.
  RQA stays stdlib-only. macOS, Linux, Windows, headless and containerised environments behave
  identically, with no daemon and no install step; #2272 and its dependency question dissolve rather than
  being solved. Beyond ADR-0063's position, a truncated or wholly rebuilt record becomes detectable up to
  the last published chain head — the failure mode a crashed agent actually produces, and the one
  ADR-0063 explicitly could not catch.
- **Bad, stated plainly.** Between publications there remains a window in which truncation is undetected:
  the guarantee is "complete as at the last anchor", never "complete as at the final entry". Publication
  introduces failure modes the local-only design did not have — an unreachable network, a partial or
  failed publish, and the question of whether a failed publish blocks an append or is recorded and
  retried. Dropping the key forfeits the margin ADR-0063 held against an actor with file access but not
  credential-store access — an unauthenticated harness, a leaked backup or CI artifact, a sandboxed
  process — and within a publication window such an actor can still rebuild the chain undetected. Anyone
  reading this record as proof against a determined local actor is relying on something it does not
  provide, and the documentation must say so rather than implying tamper-*proof*.
- **Bounded for implementation.** The published head must carry no record contents. The publication path
  must not become a route back into the record. An anchor the reviewed agent can rewrite provides
  nothing, which is the point of placing it out of reach. Publishing a chain head is an external send and
  must be checked against `RQA-NFR-023`/`027`/`029` before a path is chosen. Records already written with
  an HMAC must continue to verify, or be reported honestly, rather than being treated as broken.
- **Decomposition.** Unchanged from ADR-0063: E-13's contract (`append` → `Entry(seq, hash)` or
  `AppendFailed`) and P-12's ownership of `record_entries` are identical under this decision; only P-12's
  internals and one new publication path differ.

## Provenance

**This outcome was written by an AI agent exercising `launchpad/AGENTS.md` §5 delegated authority on
behalf of @tucktuck101**, who chose the option in an agent session after being shown the four options
and their trade-offs, verbatim:

> I think option C is the best one for us to go for.

and, on the work this decision creates:

> Yeah, do all three.

**No addressable comment exists.** §5's *Acting on a human's instruction*, condition 2, ends "If the only
place the instruction exists is a conversation, ask for it as a comment first." The agent did ask: it
offered the deciding human the choice between posting the instruction as a comment on #2298 and proceeding
with the deviation disclosed here, and he chose to proceed. That is the step the clause asks for, and this
is its outcome. The same clause states that linking a comment "is fine and sometimes useful, but it is not
required", because a comment posted under the same token carries the same authorship as the artifact
beside it; the verbatim quote above is the attribution that condition 2 actually requires.

`launchpad/decisions/README.md` still says the comment must be linked. That divergence between the README
and the governing `AGENTS.md` §5 is known and filed as #2218; ADR-0063's own Provenance section records
@serina-mcfall's trace on #2175 establishing that
[ADR-0052](ADR-0052-delegated-authority-and-feature-batching.md) withdrew the comment-link requirement "as
ceremony". This record therefore conforms to the governing decision.

**The reasoning is the deciding human's, not the agent's.** The forensic framing in Context above — that
the record exists to trace why something happened rather than to resist a forger — was his, and it is what
moved the choice from Option B to Option C.

## Supersedes

[ADR-0063](ADR-0063-rqa-record-provenance-integrity.md) — The review record is a hash chain plus an
operator-held HMAC. Its hash chain survives this decision; its HMAC, key custody and credential-store
integration do not.

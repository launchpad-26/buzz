---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#296
decided_in: launchpad-26/buzz#296
supersedes: none
---

# ADR-0037 — The sync agent resolves by replay only; all other conflicts escalate to a human

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human — *"You may not decide an ADR
outcome"* — and #296's *Decision outcome* is still blank. When a human states the outcome in
#296, this record's `status` becomes `Accepted`. Everything below is a drafted proposal,
not a settled rule.

The proposed option: Option A (replay only). The change agent may apply `rerere` replays and
configured merge drivers, and nothing else, when resolving vendor-drop conflicts. Any
residual conflict — including a three-way merge the agent believes is unambiguous —
escalates to a human with the context bundle.

**"Configured merge drivers" is bounded, or the boundary is empty.** A merge driver is
arbitrary code invoked at conflict time, so an unconstrained driver would re-grant exactly
the authority this record withholds. Under this proposal:

- Only a human may add, edit, or remove a merge driver or the `.gitattributes` entry that
  binds it to a path. The change agent may invoke drivers; it may never author or modify
  one.
- Each driver is itself a human-written, human-reviewed rule, landing through the ordinary
  pull request path like any other change, and stating in its own text which paths it claims
  and what it does to them.
- The agent may not add a path to an existing driver's scope, and may not fall back to a
  driver for a path the driver's `.gitattributes` entry does not already name.

So the trust claim is narrow and checkable: automation replays hashes of resolutions a human
already performed, or applies rules a human already wrote and reviewed, and the set of such
rules is auditable in the tree.

**The third region — applying the divergence ledger.** #296's premise correction states that
under curation *"'resolve' now includes a third category that did not exist in the original
framing — applying the fork's standing position from the divergence ledger (see #294)"*, and
that *"the boundary this issue asks for now has three regions to separate, not two."* This
record rules on that third region as follows:

- A ledger position that names a **whole-file** outcome counts as replay **only when it has
  been expressed as a merge driver or `.gitattributes` entry** under the constraints above.
  A position that exists only as ledger prose is not something the agent may apply; prose is
  not a rule the agent may interpret.
- A **sub-file** position — #296's *"upstream wins except one line"*, *"which is the real
  shape of `lefthook.yml`"* — is **not** replay and escalates. Nothing in this record
  authorises the agent to reconstruct a one-line re-application from a ledger entry.
- **This record does not settle whether sub-file positions can be made mechanical at all.**
  #294 owns the ledger's format and enforcement. If #294 defines a machine-applicable form
  for a sub-file position, that form must be a human-written driver meeting the constraints
  above, and this boundary should be revisited in a new record rather than read as already
  permitting it.

## Context

PRD #273 requires a change agent that "resolves what it can safely resolve, and escalates
the rest", but drew no boundary. The current backlog supplies real examples: `Cargo.lock`
(both sides change 18 lines — regenerable), `.github/workflows/ci.yml` (textual but a human
must decide the survival of the fork's step), `lefthook.yml` (fork's one line vs upstream's
near-rewrite), and `desktop/src-tauri/src/managed_agents/runtime.rs` (code-motion vs edit,
needs a build). Upstream's new `bin/.lefthookrc` also merges cleanly while reintroducing a
filed bug (#196), demonstrating that a clean merge is not evidence of a correct merge.

Replay-only is the smallest trust surface: the agent never interprets untrusted upstream
text, only replays hashes of resolutions a human already performed, or applies drivers a
human wrote. The cost is that every novel resolution is done once by a human — which is the
point.

## Consequences

- The merge workflow and escalation path become writable.
- A replay-only boundary means the agent never reads upstream diffs to decide — the
  containment question (#303) carries a materially smaller load.
- The first drops escalate on all four live conflicts; that is the price of the boundary.
- Where an escalated conflict is actually resolved is a separate open question, #297, which
  is a `type:adr` issue and not a work item — `launchpad/AGENTS.md` §4 rules that *"An ADR
  is never a work item and never has children."* This record does not unblock a task,
  because no task issue for the merge and escalation workflow exists yet; PRD #273's
  decomposition has not filed one.
- Bounding merge drivers adds a small standing obligation: each driver is a reviewed change,
  so the useful mechanical cases arrive one human-written rule at a time rather than all at
  once.

## Security implications

Wider resolution authority would let automation act on untrusted upstream text without a
human reading it, and conflict resolution is an unusually good place to hide a change.
Replay-only bounds that: automation acts only on hashes of prior human resolutions, or on
rules a human wrote and reviewed, never on an interpretation of the upstream diff.

The merge-driver constraint is part of that control, not decoration. A driver the agent
could author would be a path from "replay only" to arbitrary code executing on untrusted
upstream content, added by the same actor the boundary exists to constrain. Restricting
authorship to humans, through review, keeps the driver set an auditable artefact in the
tree.

## Supersedes

none

## Provenance

Drafted by an agent from #296's options; the decision itself is pending a human, as stated
at the top of *Decision*. Full alternatives, the four measured conflicts, and the 2026-08-22
premise correction remain in #296. The ledger's own format and enforcement are #294's, not
this record's.

Not verified independently in this document: whether any merge driver or `.gitattributes`
entry exists in the fork today, and whether `rerere` is enabled anywhere in the vendor-drop
path — the merge workflow this record bounds has not been written.

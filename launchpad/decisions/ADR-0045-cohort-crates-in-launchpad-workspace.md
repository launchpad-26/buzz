---
status: Accepted
date: 2026-08-27
issue: launchpad-26/buzz#1409
decided_in: launchpad-26/buzz#1409
supersedes: none
---

# ADR-0045 — Cohort crates live under `launchpad/crates/` as workspace members

## Decision

**Option B, selected by @serina-mcfall on 2026-08-27 in #1409.**

Cohort-authored Rust crates live under `launchpad/crates/`, keeping all cohort source
inside the `launchpad/` boundary, and are registered as members of the upstream root Cargo
workspace via an append-only addition to the root `Cargo.toml` `members` list. Upstream's
`crates/` directory is not touched.

This record was drafted `Proposed` on 2026-08-25 because `launchpad/AGENTS.md` §5.1
reserves the choice for a human, and #1409 is explicit that this decision in particular
needs the human instrument: choosing inside a Task *"settles section 3's closed exception
list silently, which section 3 forbids"*. The 2026-08-25 ADR-clearing session did not
supply that instrument — its comment on #1409 records the chosen option as blank and states
the outcome was *"decided automatically"* and *"not personally selected"*. A named human
has now picked between options A–D, so the record is `Accepted` and #1409's *Decision
outcome* is no longer `_No response_`.

**Two upstream files diverge, not one.** The root `Cargo.toml` gains one append-only
members entry, and `Cargo.lock` — also tracked at the repo root — changes whenever a
member is added or its dependencies move. #1409 lists both as affected components.
`Cargo.lock` is the file that will actually conflict on an upstream sync, and it conflicts
on content the fork does not control, so it is the real cost of this option rather than
the members line. An earlier draft of this record described the divergence as
"single-file, append-only"; that was wrong and the correction is the reason this paragraph
exists.

That divergence is granted as a named §3 exception by this record, and §3's exception list
carries the matching bullet so the two documents do not disagree. It is the **sixth**
exception in §3 as it now stands — issue templates, the pull-request template, the Hermit
lefthook pin, deployment image provenance, and root MCP server registration (ADR-0046) are
the five before it. The draft said "fifth"; ADR-0046's bullet landed first, which is
exactly the collision the *Consequences* section below anticipated. (Counted against
#13:decision-2's narrower list of two `.github/` exceptions it is the fourth; §3 as
written is the authority.)

## Context

Two open Tasks require a cohort crate to exist and build (#551, #524), and
`launchpad/AGENTS.md` §3's closed exception list requires an ADR for any exception. The
root `Cargo.toml` declares an explicit 31-path `members` list with no glob, so workspace
membership is an edit to an upstream file in every option except C and D. Option B
confines cohort source to `launchpad/` and keeps the `Cargo.toml` side of the divergence
to one append-only line, reversible by removing it.

Rejected: source under upstream `crates/` (A, puts cohort source inside an upstream-owned
directory and needs a wider exception), a separate cohort workspace (C, second lockfile,
second dependency-audit surface, existing workspace-wide CI does not reach it), and a
separate repository (D, cross-repo release step for every change).

Option B keeps cohort crates inside the root workspace, so root `cargo` commands do reach
them. That is the opposite of the `desktop/src-tauri` situation, which is *excluded* from
the root workspace and therefore not covered by a root `cargo test`; that hazard belongs
to rejected Option C, not to this one.

## Consequences

- Both planned crates get a home inside `launchpad/` and build through the existing
  workspace and CI.
- The root `Cargo.toml` becomes a standing one-line divergence; upstream syncs touching the
  members list are visible conflicts, not silent drift.
- **`Cargo.lock` conflicts on upstream syncs, and that is the bad part.** A lockfile
  conflict is mechanical but recurring, arrives on every sync that moves a shared
  dependency, and is resolved by regenerating rather than by reading — which makes it the
  kind of conflict people resolve without looking. This is a real ongoing cost, accepted
  knowingly.
- Both divergences are owed a row in the divergence ledger once ADR-0047 (#294) provides
  one; the ledger does not exist yet.
- Future cohort crates follow the same path without a new ADR per crate.
- §3 gains a sixth named exception. The collision this bullet anticipated — #1442
  (ADR-0046, root MCP registration) claiming the same fifth slot — resolved in ADR-0046's
  favour: its bullet merged first, so this one is placed sixth and last. No renumbering is
  outstanding.

## Security implications

No security, trust, or authority consequence: the options differ in build topology and
upstream merge cost, not in what anyone can reach or read. The members-list and lockfile
divergences are bounded and visible, whereas rejected Option C's separate workspace would
sit outside the existing workspace-wide CI and dependency-audit surface without anything
reporting the gap.

## Supersedes

none

## Amends

`launchpad/AGENTS.md` §3, by adding the root `Cargo.toml` members entry and `Cargo.lock`
as a named exception. This also extends #13:decision-2's list of two `.github/` exceptions;
that extension is unconditional, and the underlying closed-list rule — that any further
exception needs its own ADR — is untouched.

## Provenance

Drafted by an agent from #1409's options on 2026-08-25 and left `Proposed`. Accepted on
2026-08-27 by @serina-mcfall, who selected option B from the four presented in #1409; the
agent recorded that selection and did not make it. Full alternatives remain in #1409.

Two claims in the 2026-08-25 draft were stale by the time it was accepted and are corrected
above rather than left standing: the exception is §3's sixth, not its fifth, and the
renumbering collision with ADR-0046 has resolved. Both were verified by counting §3's
bullets at `origin/launchpad` rather than by re-reading this record.

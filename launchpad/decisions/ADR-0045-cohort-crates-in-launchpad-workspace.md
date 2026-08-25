---
status: Proposed
date: 2026-08-25
issue: launchpad-26/buzz#1409
decided_in: launchpad-26/buzz#1409
supersedes: none
---

# ADR-0045 — Cohort crates live under `launchpad/crates/` as workspace members

## Decision

**Not yet settled by a human.** This record is `Proposed`, not `Accepted`.
`launchpad/AGENTS.md` §5.1 reserves the choice for a human and #1409's *Decision outcome*
reads `_No response_`. #1409 is explicit that this decision in particular needs the human
instrument, because choosing inside a Task *"settles section 3's closed exception list
silently, which section 3 forbids"*. When a human picks between #1409's options A–D, this
record's `status` becomes `Accepted`.

The proposed option is B. Cohort-authored Rust crates live under `launchpad/crates/`,
keeping all cohort source inside the `launchpad/` boundary, and are registered as members
of the upstream root Cargo workspace via an append-only addition to the root `Cargo.toml`
`members` list. Upstream's `crates/` directory is not touched.

**Two upstream files diverge, not one.** The root `Cargo.toml` gains one append-only
members entry, and `Cargo.lock` — also tracked at the repo root — changes whenever a
member is added or its dependencies move. #1409 lists both as affected components.
`Cargo.lock` is the file that will actually conflict on an upstream sync, and it conflicts
on content the fork does not control, so it is the real cost of this option rather than
the members line. An earlier draft of this record described the divergence as
"single-file, append-only"; that was wrong and the correction is the reason this paragraph
exists.

That divergence is granted as a named §3 exception by this record, and §3's exception list
is amended in the same pull request so the two documents do not disagree. This would be
the **fifth** exception in §3 as it currently stands — issue templates, the pull-request
template, the Hermit lefthook pin, and deployment image provenance are the existing four.
(Counted against #13:decision-2's narrower list of two `.github/` exceptions it is the
third; §3 as written is the authority.)

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
- §3 gains a fifth named exception. Note that #1442 (ADR-0046, root MCP registration)
  proposes another fifth exception against the same §3 list; whichever merges second will
  need to renumber and re-place its bullet.

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

Drafted by an agent from #1409's options; the decision itself is pending a human, as
stated at the top of *Decision*. Full alternatives remain in #1409.

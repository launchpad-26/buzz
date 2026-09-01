---
status: Accepted
date: 2026-08-25
issue: launchpad-26/buzz#298
decided_in: launchpad-26/buzz#298
supersedes: none
---

# ADR-0038 — A small named group of humans may advance `main` to a chosen vendor point

## Decision

Option A. Add a small, named group of humans to the push restriction on
`launchpad-26/main`, limited to the people who may take a vendor drop. The operation
remains fast-forward-only; `allow_force_pushes` and `allow_deletions` stay false.

**Who is on the list — this record does not name it.** Only a repository admin can
change the restriction list (#298: *"Only a repository admin can change the restriction
list"*), so the list is set by an admin acting on #298, and this record deliberately
names no accounts: it has no standing to grant anyone push access. What it proposes is
the shape of the list, not its size or contents — **each holder named individually
rather than by team**, so that widening it is a visible act rather than a side effect of
team membership changing. **The number is the human's to set in #298, not this record's.**
An earlier revision proposed a cap of four; inventing a bound is the same class of act as
inventing the membership, so it is withdrawn. #298 should state both how many accounts
and which, since only an admin can execute either.

**No automation receives a credential for pushing to `main`.** That sentence is scoped
to `main` push and to this decision only. It is **not** a fork-wide rule that automation
holds no credentials: ADR-0039 (#299) proposes a GitHub App installation token to author
the vendor-drop pull request into `launchpad`, and that credential does exist under that
record. The two are complementary — 0039's app token authors a PR; nothing in it permits
a push to `main`, which stays with the named humans here.

**Where the rationale is recorded is unspecified by this record.** Every advance should
record the chosen upstream point and why that point, but no location or mechanism for
that record exists today, and this record does not invent one. #305 (*"what point
`launchpad-26/main` is pinned to, and what advances it"*) is the open question that owns
it. Until that is settled, an advance carries no defined home for its rationale beyond
the reflog, and this record should not be read as having supplied one.

## Context

`main` is a vendor branch — upstream pinned at a chosen point — and today push is
restricted to a single named human who is not the owner of the work. The branch sat
eleven days behind `launchpad`'s own merge-base, so `git diff main launchpad` mixed
upstream's work into the cohort's divergence. The ask is narrow: occasional, deliberate,
attributable fast-forwards by hand, not standing write access for automation.

**On precedent — corrected.** #298's decision drivers attribute a privileged-access
pattern to `launchpad/decisions/ADR-0015`. ADR-0015 does not contain it: its subject is
handbook page authoring mode (*"Every handbook page is hybrid"*, *"v1 review floor: 100%
human review, no sampling"*), and its only mention of tokens is a list of things a page
must not expose — *"no live hostnames, keys, tokens, `.env` bodies, or member rosters"*.
That citation should not be relied on, here or in #298.

The record that does bear on the credential half is
[ADR-0008](./ADR-0008-security-audit-privilege.md), which rejects a long-lived
person-held PAT on the grounds that *"a PAT held by a person outlives that person and is
a standing liability on a public repo"*, keeps the credential surface *"at exactly
zero"* where the work can be done without one, and — where a credential is unavoidable —
requires that *"its scope, owner and expiry recorded where the next person can find
them"*. Option A here needs no credential at all, so it sits comfortably inside that.

The remaining requirement is this record's own, stated de novo rather than borrowed: a
fast-forward of the vendor branch is publicly visible and reversible in principle, so
**attributability to a named individual matters more than reversibility**, and the act
must never be performed by a shared or automated identity.

## Consequences

- The vendor branch can be corrected to at least `launchpad`'s merge-base, making it a
  truthful baseline.
- Availability improves: one person's absence no longer stalls the curation loop.
- The list must stay short and named; a bound stated by the human in #298 is what makes
  "short"
  checkable, and exceeding it should require a new record rather than an admin's
  judgement in the moment.
- Nothing here is executable until an admin acts on #298, and nothing here records a
  rationale until #305 settles where one goes.

## Security implications

The original framing asked for standing push access for a scheduled process; this grants
occasional, attributable, human fast-forwards to a chosen point — a supply-chain trust
choice (who picks the point ~4,300 files of upstream code is pinned to), not a
credential grant. No credential is created by this decision, so this decision creates
nothing to steal. The fork is not credential-free overall; ADR-0039 introduces one for a
different purpose, and a reader must not infer from this record that the drop flow as a
whole holds no secrets.

The residual concern is ordinary and should be named: more accounts with push access to
a protected branch is more accounts whose compromise matters. The cap and the
fast-forward-only constraint are what bound it.

## Supersedes

none

## Provenance

Drafted by an agent from #298's options. Jeffrey (@tucktuck101) made the decision on
2026-08-31 after reviewing options A–D with their positive and negative consequences and
the agent's recommendation of Option A; he replied verbatim: **"A"**. The group's size
and membership remain his to state in #298, and the branch-protection change remains a
repository admin's to execute — this record grants nothing by itself. Full alternatives
and the measured branch-protection state remain in #298.

Verified while drafting: ADR-0015 does not contain the privileged-access pattern #298
attributes to it (read in full on `launchpad`), and ADR-0008 does contain the
credential-surface reasoning cited above.

Not verified independently in this document: the current membership of `main`'s push
restriction beyond the single login #298 recorded on 2026-08-21, and whether any admin
has been asked to act.

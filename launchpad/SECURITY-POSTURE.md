# Security posture

Where the launchpad-26 cohort's security controls actually stand today, which risks have
been accepted with a reason, and the one gap that nothing currently owns.

This document records posture. It applies no control, and it does not settle anything an
open decision owns — where a choice is open it says so and links the issue.

---

## How to read this

Every claim below carries exactly one status marker, read as defined in
[VISION.md § How to read this](VISION.md#how-to-read-this). The legend lives there and is
not restated here.

Read this document as a description of posture, not of controls in force: a marker says
whether a control exists, is agreed, is proposed or is undecided, and only `IMPLEMENTED`
means something is protecting something right now.

---

## What is true today

This section previously listed host-hardening and repository-hygiene controls one by one,
each marked `Open`, `Implemented` or similar, as of 2026-08-11. That table is retired, not
updated.

Two things made retiring it the right call rather than correcting it. First, it had
already drifted from reality — it stated the cohort ran Buzz on `localhost` only, which
stopped being true before anyone caught it, and a stale gap table reads as a current one
to anyone who doesn't check the date. Second, and more fundamentally: a control-by-control
readiness table in a public, world-readable file is a gap map for anyone who reads it,
whether or not it is accurate. Making it accurate would not have closed that problem — an
accurate gap map is worth more to an attacker than a stale one, not less.

Detailed, current security posture is tracked in the cohort's private companion
repository, `buzz-infrastructure`, under the disclosure boundary
[`AGENTS.md` §8](AGENTS.md) states here and that repository inverts for itself. This
document still states what's safe to say publicly and nothing more: accepted risks with
their reasoning ([below](#accepted-risks)), the gap this document exists to surface
([below](#the-gap-this-document-exists-to-surface)), and which decisions remain open
([below](#open-security-decisions)).

The one control-level fact that stays, because it names nothing about the live host and
is independently checkable by any reader: `cargo-deny check` runs in this repository's own
CI and covers its Rust dependency surface, nothing beyond that —
[`.github/workflows/ci.yml`](../.github/workflows/ci.yml).

---

## Accepted risks

Each row is a risk the cohort carries deliberately, with the reason written down and a
source that can be read. Nothing is listed here without one.

A marker in this table describes the standing of the *acceptance*, never of a control:
`DECIDED` means the acceptance is agreed and recorded, which is what makes a risk accepted
rather than merely present. No row here protects anything.

| Risk | Status | Why accepted | Source |
|---|---|---|---|
| This repository is public, so a written architecture is a map for an attacker as much as for a contributor | `DECIDED` | An undocumented architecture hides gaps — including the one below — from the people who could fix them | [#42](https://github.com/launchpad-26/buzz/issues/42) security implications; [`AGENTS.md` §8](AGENTS.md) |
| An initial privileged bootstrap step survives: the deployment's declared input is a bare Ubuntu host with root SSH | `DECIDED` | Something must establish the first identities. Ruling 6 confines root to bootstrap authority rather than an operational identity, and Ruling 7 keeps it from being handed round as a deployment mechanism | [#5](https://github.com/launchpad-26/buzz/issues/5) non-goals: "No requirement to eliminate the initial privileged bootstrap step" |
| Host hardening does not make the application itself invulnerable | `DECIDED` | The objective is "a **reproducible, defensible internet-facing cohort server**, not a complete enterprise security platform"; product defects go upstream under [`AGENTS.md` §1](AGENTS.md) | [#5](https://github.com/launchpad-26/buzz/issues/5) non-goals: "No claim that host hardening makes the application itself invulnerable" |
| No SOC, SIEM or enterprise security operations platform | `DECIDED` | Ruling 13 draws the line where the cohort can still diagnose a failure: "A larger observability or SIEM platform is outside scope; establishing enough evidence to diagnose access and security failures is not." | [#5](https://github.com/launchpad-26/buzz/issues/5) non-goals and Ruling 13 |
| Zero trust is applied proportionately to one cohort server, not as enterprise zero-trust infrastructure | `DECIDED` | Ruling 4 requires the principle — explicit identity, least privilege, no permission granted by location — without requiring the infrastructure | [#5](https://github.com/launchpad-26/buzz/issues/5) Ruling 4 |
| Every repository-level control the cohort can build without admin will detect rather than prevent, and on a public repository detection lands after disclosure; what is accepted here is that shape, not any claim about which such controls currently run | `DECIDED` | Push protection "can only be *enabled* by a repository admin", so detection is deliberately scoped to need none — "closing it is a separate, human, privileged act", requested under [#72](https://github.com/launchpad-26/buzz/issues/72) | [#62](https://github.com/launchpad-26/buzz/issues/62) security implications |
| Secret-shaped material already in git history is not removed by the hygiene work | `DECIDED` | "remediation is a separate decision with its own blast radius — this PRD delivers the finding, not the force-push" | [#62](https://github.com/launchpad-26/buzz/issues/62) non-goals |

The markers above cover only the rows present when this section was written. A risk added
later does not inherit one — it carries its own status marker and its own written source.

---

## The gap this document exists to surface

`OPEN` — [#43](https://github.com/launchpad-26/buzz/issues/43).

Stated plainly: if agents are initiated on the relay and executed on contributors'
machines, **the relay stops being only a service to protect and becomes a distribution
point for code execution.**

[#42](https://github.com/launchpad-26/buzz/issues/42)'s security-implications section is
where that consequence is written down. Of the hardening PRD it says the rulings "all
address protecting the host; none addresses the host as an initiation point."

[#43](https://github.com/launchpad-26/buzz/issues/43) reaches the same place from the
other side: "#5 currently treats the host as an asset to protect, and this makes it a
distribution point whose compromise reaches every connected contributor. #5's scope
should be widened to reflect that, or the gap recorded explicitly." This section is that
explicit record.

What happens at the far end — the exposure on contributors' own machines, and the toolset
an agent starts with there — is owned by
[ARCHITECTURE.md § The execution boundary](ARCHITECTURE.md#the-execution-boundary) and is
not restated here.

This section names the gap and stops. It does not narrow the containment options, rank
them, or point at any of them, because
[#42](https://github.com/launchpad-26/buzz/issues/42)'s non-goals reserve that question
to its ADR: "the agent execution security model in particular is a separate ADR and must
not be pre-empted here."

---

## Open security decisions

Every security decision this posture depends on that has not been taken. Titles are the
issue titles as filed.

| Decision | Status |
|---|---|
| adr: CI/CD deployment identity, privilege boundary and secret storage | `OPEN` — [#25](https://github.com/launchpad-26/buzz/issues/25) |
| adr: administrative access model after bootstrap | `OPEN` — [#26](https://github.com/launchpad-26/buzz/issues/26) |
| adr: security patch and reboot policy | `OPEN` — [#27](https://github.com/launchpad-26/buzz/issues/27) |
| adr: what must survive destruction of the host | `OPEN` — [#28](https://github.com/launchpad-26/buzz/issues/28) |
| adr: agent execution security model — containment for relay-initiated agents on contributor machines | `OPEN` — [#43](https://github.com/launchpad-26/buzz/issues/43) |
| adr: host firewall implementation for the deny-by-default policy | `OPEN` — [#44](https://github.com/launchpad-26/buzz/issues/44) |
| adr: AppArmor and service confinement for the Buzz runtime | `OPEN` — [#45](https://github.com/launchpad-26/buzz/issues/45) |
| adr: which security checks gate deployment in CI/CD | `OPEN` — [#46](https://github.com/launchpad-26/buzz/issues/46) |
| adr: minimum external security smoke test before a deployment is declared healthy | `OPEN` — [#47](https://github.com/launchpad-26/buzz/issues/47) |
| adr: secret-scanning engine for the fork, and where its allowlist lives | `OPEN` — [#63](https://github.com/launchpad-26/buzz/issues/63) |
| adr: dependency update path for this fork — Dependabot, Renovate, or neither | `OPEN` — [#64](https://github.com/launchpad-26/buzz/issues/64) |
| adr: what privilege the repository security audit runs with | `OPEN` — [#65](https://github.com/launchpad-26/buzz/issues/65) |

The last three sit under [#62](https://github.com/launchpad-26/buzz/issues/62), the PRD
for repository security hygiene. The host-hardening decisions above them were raised
under [#5](https://github.com/launchpad-26/buzz/issues/5).
[#43](https://github.com/launchpad-26/buzz/issues/43) is filed standalone — no PRD raised
it — which is why it appears here and in
[ARCHITECTURE.md § Open decisions](ARCHITECTURE.md#open-decisions) without a parent.

Most of the rows above also appear in
[ARCHITECTURE.md § Open decisions](ARCHITECTURE.md#open-decisions), which lists every
decision the target architecture depends on rather than only the security ones. Both
documents carry the shared rows on purpose, so a reader arriving at either sees a complete
list — the cost is that an accepted ADR has to be struck from both, and updating one alone
leaves the other asserting a decision that is closed.

Those markers cover only the rows present when this section was written, all confirmed
`OPEN` against the live issues on 2026-08-11 with `gh issue view`. A decision added later
carries its own marker, and a decision that is taken becomes `DECIDED` with a link to its
accepted ADR in [`decisions/`](decisions) — see [`AGENTS.md`](AGENTS.md) §2.

---

## The public-repository rule

The rule exists and binds — `IMPLEMENTED` — [`AGENTS.md` §8](AGENTS.md). Nothing enforces
it; the last paragraph of this section says what that marker does and does not cover.
Quoted in full:

> - **Never open a public issue for a vulnerability.** Use the private advisory link on
>   the issue chooser page.
> - **This repository is public.** Every file you commit is world-readable. Config is
>   fine; credentials never are. Parameterise secrets out of files from the first commit.
> - Never add a secret, key, token, or private hostname to a tracked file.

Those rules bind this document as tightly as they bind any deployment file, which is why
nothing here names a hostname, a credential or a person. A security posture is exactly
the kind of document that tempts an author to be concrete, and being concrete is how
operational detail reaches a world-readable file.

A vulnerability in Buzz the product, rather than in this cohort's operation of it, routes
as [`SECURITY.md`](../SECURITY.md) directs — still never as a public issue here. That
split is recorded in [#62](https://github.com/launchpad-26/buzz/issues/62)'s non-goals.

`IMPLEMENTED` above marks the rule's existence and its binding force, and nothing beyond
that. **A rule that binds is not a mechanism that checks.** No mechanism described in this
public document detects a violation of §8 — compliance rests on the attention of whoever
is writing, which
[#62](https://github.com/launchpad-26/buzz/issues/62) already measured and declined to
treat as a control. Of the near-misses it records: "All three were caught by human
attention alone." Its verdict on that: "Three catches in one session is not evidence that
attention works; it is evidence of the rate at which this material is generated."

---

## Adding to this document

> Additions arrive by pull request against `launchpad`. Every new claim carries a status
> marker and a link to its evidence. Anything not yet true is an issue, not a line here —
> see [`AGENTS.md` §2](AGENTS.md). Append within a section rather than renumbering
> headings, so links from issues and the handbook keep resolving.

A new accepted risk additionally needs a `Why accepted` entry and a source that can be
read. Without one it is not an accepted risk — it is an undocumented one.

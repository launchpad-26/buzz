# Declines and upstream security fixes

**Title:** How downstreams stop a durable decline from swallowing a security fix, and what this fork can actually watch
**Summary:** Prior art has no mechanism for a declined security fix **because distributions do not decline them** — the local patch bends to accommodate the fix, never the reverse, and Debian's rule is "make as few changes as possible" with the security team coordinating any exception. So the ledger needs a **rule**, not a mechanism. The detection half is worse than expected: **upstream removed its commitment to publish security advisories on 2026-08-17 — inside the current backlog — and publishes none.** The fork therefore has no advisory feed to watch. What it does have: RUSTSEC identifiers in upstream commit subjects, and `cargo audit` in upstream CI. Also records that ADR-0007 covers *dependency* updates only, so upstream **source**-level security fixes are outside the fork's security posture entirely.
**Tags:** `upstream-sync` `vendor-drop` `security` `adr-0007` `prd-273` `decline-ledger`
**Established:** 2026-08-22 · **Answers:** [#364](https://github.com/launchpad-26/buzz/issues/364) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**The question contains an assumption that prior art rejects.** It asks how downstreams stop a durable decline from swallowing a security fix. Distributions do not have that problem, because they do not decline security fixes — the standing rule is that the *local* state accommodates the fix.

Debian's guidance is explicit about direction of travel:

> "The most important guideline when making a new package that fixes a security problem is to make as few changes as possible."

and about the exception, which is a coordination requirement rather than a licence to decline:

> "In some cases it is not possible to backport a security fix, for example when large amounts of source code need to be modified or rewritten. If that happens it might be necessary to move to a new upstream version, but this has to be coordinated with the security team beforehand."

So the shape of the answer for [#294](https://github.com/launchpad-26/buzz/issues/294) is not a durability mechanism. **It is a rule with an escalation path: a security-relevant upstream change is never declined; where the fork's position obstructs it, the position yields and the obstruction is escalated to a named human.** That is a one-line policy, and it is the only thing in this whole PRD family that prior art is unanimous about.

**The hard part is not the rule. It is knowing which changes are security-relevant** — and that is where this fork is worse off than a distribution, for a reason nobody has noticed.

---

## Upstream publishes no security advisories, and stopped promising to during this backlog

```
$ gh api repos/block/buzz/security-advisories --jq 'length'
0
```

That is not an oversight. On **2026-08-17** — a commit inside the current 67-commit drop — upstream removed the promise:

```
$ git show 85bacea52 --format='%h %ad %s' --date=short -- SECURITY.md
85bacea52 2026-08-17 Remove GitHub security advisory commitment (#6144)

    Removes the promise in `SECURITY.md` to publish a GitHub Security
    Advisory after every security fix is released.

--- a/SECURITY.md
+++ b/SECURITY.md
@@ -121,6 +121,4 @@
 We follow [coordinated disclosure](...).
-Once a fix is ready and released, we will publish a security advisory on
-GitHub describing the vulnerability, its impact, and the fix. Reporters will
-be credited unless they request anonymity.
+Reporters will be credited unless they request anonymity.
```

**So the fork has no upstream advisory feed to watch, by upstream's deliberate decision, and the decision itself arrives in the drop this PRD is about.** Any design that assumed "watch upstream's advisories" is void before it is written.

What upstream's `SECURITY.md` still commits to: private reporting to `buzz@block.xyz`, acknowledgement within 48 hours, a full response including a fix timeline within 7 days, coordinated disclosure, and `cargo audit` in CI. **None of those is a signal a downstream can consume.** They are commitments to a reporter, not to a consumer.

### What can be watched instead

Two usable signals, both partial:

**1. RUSTSEC identifiers in commit subjects.** A convention, not a guarantee, but it is consistent — 8 security-related subjects in the last 400 upstream commits:

```
$ git log --format='%h %s' upstream/main -400 | grep -iE 'security|cve|rustsec|advisor|vuln'
cc8a8b0dc fix: bump h2 for RUSTSEC-2026-0258 (#6222)
85bacea52 Remove GitHub security advisory commitment (#6144)
c966b862f fix(deps): bump webbrowser to 1.2.4 for RUSTSEC-2026-0257 (#5659)
d2ebaa95a ci(security): allow retired relay pool advisory (#5404)
8630e58eb fix(desktop): fence localStorage SecurityError from killing the React tree (#5142)
a7ea86cdc fix(desktop): enable the content security policy (#4614)
318fbf896 fix(security): bump nostr crates for RUSTSEC-2026-0225..0232 + default sprig image to published digest (#4392)
9d6726e5b chore(deps): bump nostr-relay-pool for RUSTSEC-2026-0224 (#4139)
```

**Note what that list is mostly made of: dependency bumps.** Six of the eight are `cargo`/`npm` advisories. Only two are code-level, and one of those (`85bacea52`) is the policy change itself. **Grepping subjects finds dependency advisories reliably and code-level security fixes barely at all**, because a code-level fix looks like `fix(relay): stop panicking the ingest worker on reactions to project events` — which is in the current backlog, is arguably a denial-of-service fix for an internet-facing relay, and matches no security keyword.

**2. `cargo audit`, which the fork can run itself.** This is the stronger of the two, because it does not depend on upstream saying anything. It also means the dependency half of the problem is already covered twice over — by upstream's CI and by the fork's own Dependabot path.

---

## The gap this exposes in the fork's own posture

ADR-0007 decides the fork's dependency-update path: **Dependabot** across six ecosystems, with Renovate rejected and `renovate.json` declared upstream-owned and inert. Its own scope statement is narrow and explicit — *"This ADR decides the update path only."*

Searching ADR-0007 and `launchpad/SECURITY-POSTURE.md` for coverage of upstream *source*-level security fixes returns nothing on point. `SECURITY-POSTURE.md`'s only adjacent line pushes the other way:

> "Host hardening does not make the application itself invulnerable … product defects go upstream under `AGENTS.md` §1"

Which is correct as far as it goes, and describes reporting a defect *to* upstream — not adopting a fix *from* upstream.

**So: dependency vulnerabilities are covered (Dependabot + `cargo audit`). Upstream source-level security fixes are covered by nothing.** They arrive only in a vendor drop, and under ADR-0022 a source-level fix in the uncontested 99% is adopted unreviewed — which is the *good* outcome — while one that touches a contested file is adjudicated by whoever reads the drop report, with no signal marking it as different from a refactor.

That is a gap in the fork's security posture that exists independently of #273 and is not #273's to close.

---

## What this means for #273

**#294's security column should be a rule, not a flag.** A boolean nobody knows how to act on is decoration; the actionable version is a standing rule — *no security-relevant change is declined; the fork's position yields and the obstruction is escalated* — plus, per Debian's practice, a named human who owns the exception. The fork already has the escalation half designed ([#296](https://github.com/launchpad-26/buzz/issues/296), [#297](https://github.com/launchpad-26/buzz/issues/297)); what it lacks is the rule that triggers it.

**#306's report has a new hard requirement, and it cannot be met by grepping.** If the drop report is to distinguish a security fix from a refactor, it cannot rely on upstream's labelling, because upstream neither publishes advisories nor marks code-level fixes distinctly. The honest options are: read every commit touching the operational surface — which [#355](https://github.com/launchpad-26/buzz/issues/355) makes tractable at **19 files**, not 796 — or state plainly that the fork does not detect upstream source-level security fixes and accept that. **The 19-file operational surface is what makes the first option affordable**, and that is the strongest argument yet for organising the report around operational tiers rather than conflict count.

**One consequence for ADR-0022 worth stating precisely.** Its scope ruling adopts the uncontested 99% unreviewed. For security fixes that is *protective*, not risky — an unreviewed security fix still lands. The risk is confined to the contested rows, which is 27 files, which is small. **ADR-0022 is safer against this failure mode than it is against the clean-merge-but-wrong one**, and that asymmetry is worth having on the record because the two are easy to conflate.

**And a note on the vendor branch.** `main` holding upstream's content indefinitely (ADR-0021's two-way door) cuts both ways here: it means a declined change can be reviewed later, which is good, and it means the fork can diff its position against upstream's current version at any time to ask "has upstream since fixed something here?" That is the periodic-recheck mechanism [#361](https://github.com/launchpad-26/buzz/issues/361) identified as the standard answer to obsolete divergence, and it applies to security fixes too. Nothing needs building for it — `git diff main launchpad -- <path>` is the whole mechanism.

---

## Confidence and limits

**High** on the repository and upstream facts: the zero advisories, the removal commit and its diff, the eight security-related subjects, ADR-0007's scope, and the absence of source-fix coverage in `SECURITY-POSTURE.md` are all pasted or directly reproducible.

**Medium on the prior-art half.** Debian's security FAQ is authoritative for Debian, and its position is unambiguous. But I read one distribution's policy in detail, not several, and I am inferring the general claim — "distributions do not decline security fixes" — from Debian plus the absence of any contrary practice in the sources surveyed for [#361](https://github.com/launchpad-26/buzz/issues/361). That is a reasonable inference and it is an inference. A counter-example would most likely come from an embedded vendor with a frozen BSP, where declining a fix on compatibility grounds is plausible.

**Not verified.** I did not read Red Hat's, SUSE's or Ubuntu's policies, only search summaries of Red Hat's backporting approach. I did not check whether upstream's `cargo audit` CI lane currently passes, or whether the fork's Dependabot configuration from ADR-0007 has actually been built — ADR-0007 says that is #71 and explicitly not done in that record, so it may not exist. **I did not assess whether any commit in the current backlog is in fact an undisclosed security fix**; I named `fix(relay): stop panicking the ingest worker on reactions to project events` as *arguably* denial-of-service-relevant based on its subject line and the fact that the relay is internet-facing, and I did not read the diff or form a judgement — that would be a security review, which is not this issue's question and not mine to conduct unasked. I have no VPS access, so nothing here is informed by what is actually deployed.

## Sources

- [Debian security FAQ](https://www.debian.org/security/faq) — backport-not-upgrade, "as few changes as possible", and the coordinate-with-the-security-team exception
- [Debian Backports](https://backports.debian.org/) and [FAQ](https://backports.debian.org/FAQ/) — the backports archive's own scope
- [How Red Hat Backports Security Patches](https://scanrook.io/blog/redhat-backporting-explained) — a second distribution's approach (read as summary only)
- [Vulnerability scans miss backported patches](https://sitehost.nz/blog/vulnerability-scans-backported-patches) — why version-based scanning misreports backported fixes, relevant if the fork ever scans its own image
- `block/buzz` `SECURITY.md` at `upstream/main`, and commit `85bacea52`

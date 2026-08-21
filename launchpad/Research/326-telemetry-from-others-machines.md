# Telemetry from machines the operator does not own

**Title:** Accepted practice for collecting telemetry from other people's machines, and why it does not transfer cleanly
**Summary:** Every framework found — the Linux Foundation policy, Go's Transparent Telemetry, ordinary OSS practice — rests its central safeguard on anonymisation and aggregation. #289's acceptance test requires the opposite: naming which member differed. Anonymity is the control these practices depend on and the thing this PRD must not do, so the standard policy cannot be adopted wholesale. Three controls transfer cheaply — documented scope, inspectability, shared access — and criterion 6's filtering policy ends up carrying the weight anonymisation normally carries.
**Tags:** `observability` `privacy` `consent` `telemetry-policy` `prior-art` `byod`
**Reviewed:** 2026-08-22 · **Answers:** [#326](https://github.com/launchpad-26/buzz/issues/326)

---

## Finding

**The established practice cannot be adopted wholesale, and the reason is structural.** Every framework found rests its central safeguard on **anonymisation and aggregation**. #289's criterion 3 exists to say *which member* differed. **Anonymity is the control these practices depend on, and it is precisely what this PRD must not do.**

The useful output is therefore not "copy this policy" but: which controls survive once anonymisation is removed, and what has to replace it. Three of four transfer directly — documented scope, inspectability, withdrawal. The fourth, consent, is where the PRD's current framing deserves a second look.

---
## The three practices

### 1. Linux Foundation Telemetry Data Policy — the governance shape

The most normative source I found, and the obligations are strict:

- **Prior review**: projects *"must first coordinate with members of the legal team of the Linux Foundation to undergo a detailed review"*, and collection is prohibited *"unless and until the legal team approves the proposed collection."*
- **Affirmative consent**: users are *"required to consent prior to any Telemetry Data collection being initiated."*
- **Notice**: projects must show how users are *"notified of all relevant details of the Telemetry Data collection, use and distribution"*, and approved collection *"must be fully documented by the project community in its public documentation."*
- **Anonymisation**: data must be *"fully anonymized, and does not contain anything that can arguably be considered data about an individual"* or *"sensitive or confidential to users."*
- **Shared access**: approved projects must make *"the collected data available to all participants in the project community."*

**What it declines to collect:** anything attributable to an individual. That single line rules out the cohort's use case as written.

**Retention and withdrawal: the policy does not specify either.** That is a gap in the source, not in my reading, and it is worth knowing that even the most formal framework available leaves the two questions #289 will have to answer itself.

### 2. Go's Transparent Telemetry — the best-argued case, and it changed its mind

Go's design was published as opt-out and revised to opt-in after community feedback. Russ Cox: *"By far the most common suggestion was to make the system opt-in (default off) instead of opt-out (default on)."*

The reasons are worth reading against a cohort rather than a language ecosystem:

- Users said *"this is the first system I'd actually opt in to, but I'd still turn it off if it was on by default."*
- Precedent: an opt-out Go might legitimise the same in projects with far less careful data minimisation.
- **Reidentification**: publishing records could reveal which organisations use particular obscure configurations.

He is also honest that opt-in makes each participant *more* exposed, not less: *"The opt-in system is fundamentally more invasive to any given installation than the opt-out system"* — because with fewer participants, each must report more often.

**What it refuses to collect:** *"uploaded reports do not contain any identifying information or any strings not already known to the collection system"*, and he rejects detailed command logs, geolocation and fine-grained metrics with *"we simply don't need all that information to inform our decisions."*

**Inspectability** comes from the implementation being open source and the distributed binaries being verifiable against it.

### 3. Ordinary OSS practice — the mechanics

The common pattern, across projects: collect feature-usage counts, performance metrics and anonymous error reports; **do not** collect personal information, IP addresses, file contents, or unique identifiers. Opt out instantly via an environment variable (`PROJECTNAME_TELEMETRY=0`), a flag (`--no-telemetry`), or a setting. Inspect with a debug mode that prints every event **before transmission**.

That last one is the cheapest and most transferable idea in this whole answer.

---

## Where the sources disagree

**Opt-in versus opt-out is genuinely contested, and both sides have a real argument.** Go moved to opt-in on consent grounds. The counter-argument, stated plainly in the survey literature, is that opt-in rates typically fall **below 3%**, which makes the resulting data statistically useless. Cox's rebuttal is that Go is large enough for even 1% to be representative with proper sampling.

**Neither argument applies to this cohort, and noticing that is the point.** The <3% objection is about *statistical representativeness across a large anonymous population*. The cohort has a handful of known people, and every one who participates is 100% of themselves. There is no sampling problem to trade against consent here — **so the strongest argument for opt-out simply does not exist in this setting**, and opt-in costs the cohort nothing that it costs Go.

---

## What this means for #289


> **Recommendations, not findings.** Everything in this section is my assessment as the author, not behaviour established by the evidence above. Per [ADR-0003]'s claim rule: a claim about how the system *behaves* carries a source reference; a claim about what the cohort *should do* is opinion, attributed. Nothing is both — so nothing below is cited as though it were established.
1. **The anonymisation control cannot be inherited, and something must replace it.** Both formal frameworks make anonymisation the primary safeguard. Criterion 3 requires member attribution. The replacement has to be *scope* — what is collected at all — rather than *identifiability*, which means criterion 6's filtering policy is carrying much more weight than it would in a normal telemetry design. It is the only safeguard left.
2. **"Accepted as a condition of participation" is worth re-examining, factually.** #289 records that Alloy on personal machines was accepted that way. Both frameworks require consent *prior to collection*, and the LF standard is affirmative. Consent obtained by making it a condition of taking part is a different thing from consent to a specific, documented collection — and the cohort's own scope will change over time, which is exactly when a blanket up-front acceptance stops covering what is happening. Not a blocker; a thing to state deliberately rather than inherit.
3. **Three controls transfer cheaply and should be adopted:**
   - **Documented scope** in public documentation, per the LF requirement — which criterion 6 already commits to.
   - **A debug mode that shows a member exactly what leaves their machine, before it leaves.** The single highest-value idea here, and Alloy's configuration being committed to a public repo does *not* substitute for it — a config file is not a list of what was actually sent.
   - **Shared access.** The LF requires collected data be available to all participants; criterion 1 already wants one shared pane. These agree, and it is worth noticing that the cohort's design is *more* transparent than the baseline here, not less.
4. **Withdrawal is unanswered everywhere and will have to be decided locally.** Neither framework specifies what happens to already-collected data when someone leaves. For a cohort with a fixed end date and members who will move on, that is not hypothetical.
5. **Reidentification applies even to a stated-identity system.** Go worried that obscure configurations identify organisations. Here the deliberate identifier is a pubkey, but telemetry would also carry incidental machine detail — hostnames, paths under a home directory, installed tooling. **Open question, not a finding:** whether that incidental detail discloses *more* than the pubkey already does has not been established, and answering it needs the field inventory from [#311](https://github.com/launchpad-26/buzz/issues/311). What can be said without it is narrower and still useful — incidental machine detail is a *different kind* of disclosure from deliberate member attribution, being about the member's machine rather than their Buzz activity, so the filtering policy should treat the two separately rather than as one category.

   <sub>Softened per [#420](https://github.com/launchpad-26/buzz/issues/420): the first version asserted the comparison as fact without evidence.</sub>

---

## Confidence and what is still unknown

**High confidence** on what the three sources say — the LF obligations and Cox's reasoning are quoted directly from the primary documents.

**Moderate confidence** on the "typical OSS practice" summary, which is a synthesis from a search-result overview rather than from reading each project's policy. The specific mechanisms (`PROJECTNAME_TELEMETRY=0`, `--no-telemetry`, `--debug-telemetry`) are patterns rather than a standard, and I did not verify them against named projects.

**A real gap in the prior art, not in my search:** I found **no** framework that addresses telemetry from machines the operator does not own **where attribution to an individual is the point**. Every source assumes anonymised aggregate collection. The closest analogues would be workplace endpoint monitoring and BYOD policy — a different literature with different consent law behind it — **and I did not research it**. If the cohort wants real prior art for its actual shape, that is where to look, and it is the largest thing left unanswered here.

**Not researched:** GDPR or other legal obligations, which are a question for a human and not for an agent; TinaCMS and the other specific project policies the search surfaced, beyond the aggregate summary; whether Grafana Alloy has a "show me what you are about to send" mode, which is the practical form recommendation 3 would take and which I did not check; and how the cohort's own [#43](https://github.com/launchpad-26/buzz/issues/43) agent-containment boundary interacts with this, which #83 already flagged must be decided consistently.

## Sources

- [Telemetry Data Collection and Usage Policy — Linux Foundation](https://www.linuxfoundation.org/legal/telemetry-data-policy) — prior approval, affirmative consent, notice, anonymisation, shared access
- [Opting In to Transparent Telemetry (Transparent Telemetry, Part 4) — Russ Cox](https://research.swtch.com/telemetry-opt-in) — the opt-out→opt-in reversal, reidentification, data minimisation, the invasiveness tradeoff
- [Opt-out telemetry — LWN.net](https://lwn.net/Articles/983704/) — community reception of the opt-out/opt-in debate
- [Why Your Open Source Project Needs Telemetry (And how to do it right) — 1984 Ventures](https://1984.vc/docs/founders-handbook/eng/open-source-telemetry) — the opt-out mechanics, debug-before-send inspection, and the <3% opt-in figure
- [TinaCMS Open Source Telemetry & Privacy Policy](https://tina.io/telemetry) — an example project policy, surfaced but not read in full

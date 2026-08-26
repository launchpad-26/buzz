# What shape of adoption report actually gets read

**Title:** Review-effectiveness evidence applied to the drop report, and the worked precedent the fork already has
**Summary:** Code-review research puts peak defect detection at **200–400 changed lines**, with a sharp decline past 400 and effectiveness below 50% past 1,000. Measured against this fork: the whole drop is **117,113 changed lines** (~290× the threshold), the operational surface is **3,125** (8×), and **the contested surface is 385 — inside the effective band.** So ADR-0022's contested-surface scoping lands almost exactly on the empirically effective review size, which is a strong quantified validation of a decision made on judgement. Names the resulting tension with #364, identifies PR #216's body as a worked precedent nobody has mined, and records that the drop grew from 67 to 80 commits during a single working session.
**Tags:** `upstream-sync` `vendor-drop` `drop-report` `adr-0022` `prd-273` `review-quality`
**Established:** 2026-08-22 · **Answers:** [#365](https://github.com/launchpad-26/buzz/issues/365) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**ADR-0022's skimming claim is correct, and it can now be stated as a number rather than an intuition.**

That record argues that an artifact too long to read produces skimming, and that "a skimmed review is worse than an honest blanket policy, because it looks like review". The research agrees and gives thresholds:

> "Reviewers spot defects most effectively when examining 200-400 lines of code at a time, and once reviews grow past 400 lines, defect detection starts to drop off."

> "at 200 lines, review effectiveness is 80-90%, but it drops below 50% once a PR exceeds 1,000 lines"

> "Reviewers examining more than 400 lines of code per session or spending more than 60 minutes in a single sitting experienced a sharp decline in defect detection rates."

Measured against the three candidate units in [#306](https://github.com/launchpad-26/buzz/issues/306):

| Unit | Files | Changed lines | Against the 400-line threshold | Expected effectiveness |
|---|---|---|---|---|
| **Whole drop** | 912 | **117,113** | **293×** | Far below 50% |
| Operational surface ([#355](https://github.com/launchpad-26/buzz/issues/355)) | 18 (+`Cargo.lock`) | **3,125** | **7.8×** | Below 50% in one sitting |
| **Contested surface** | 8 | **385** | **0.96×** | **80–90%** |

**The contested surface is 385 changed lines. The band where defect detection peaks is 200–400.** That is not an argument for ADR-0022; it is a measurement that happens to land on it.

---

## Evidence

```
$ MB=f8692fa9b52ddcfeb4b95fb4862109983509f131

$ git diff --shortstat $MB upstream/main
 912 files changed, 96617 insertions(+), 20496 deletions(-)

# the 19 operationally-live files from #355, excluding generated Cargo.lock
$ git diff --shortstat $MB upstream/main -- <18 live paths>
 18 files changed, 2940 insertions(+), 185 deletions(-)

# the 8 files both sides touched
$ git diff --shortstat $MB upstream/main -- .github/workflows/ci.yml AGENTS.md \
    Cargo.lock crates/buzz-cli/src/lib.rs \
    desktop/src-tauri/src/managed_agents/restore.rs \
    desktop/src-tauri/src/managed_agents/runtime.rs Justfile lefthook.yml
 8 files changed, 271 insertions(+), 114 deletions(-)
```

### The drop is a moving target, and here is the rate

Measured at the start of this session and again a few hours later, both after fetching `upstream/main`:

```
# earlier today
$ git rev-list --count $MB..upstream/main
67

# later the same session
$ git rev-list --count $MB..upstream/main
80
$ git log -1 --format='%h %ad %s' --date=iso upstream/main
025425591 2026-08-21 16:09:14 -0400 fix(benchmarks): wait for scripted event delivery (#6487)
```

**Thirteen commits — a 19% growth in the drop — within one working session.** At the measured ~18 commits/day ([#356](https://github.com/launchpad-26/buzz/issues/356)) the whole-drop unit does not merely exceed the effective review size; it grows faster than anyone reads it. **That is a second, independent argument against per-commit or per-file adjudication, and it is stronger than the size argument** because size is a fixed cost and drift is a race.

---

## The worked precedent nobody has mined

[#306](https://github.com/launchpad-26/buzz/issues/306) describes the drop report as an artifact nobody has specified. **One already exists.** PR #216's body — written by a person taking a 113-commit / 981-file drop by hand — contains, unprompted, a complete instance of the shape:

1. **"Why now"** — five notable upstream changes, each with its upstream PR number and a sentence on why it matters *to this fork* (not what it does in general). Example: *"`fix(acp): gate relay-signed workflow messages on their attributed author` (#6129) — … Touches the ACP plumbing this cohort's agent harness runs on."*
2. **"Risk analysis"** — a per-file table of the four files where upstream's changes overlapped the fork's, each row naming the fork's change and whether it survived the merge, with the check that established it.
3. **"A second fix, made on top of the merge"** — the consequential work the merge itself caused, explained and justified.
4. **"Verification"** — a gate table with raw results.
5. **An explicit pre-existing-failure carve-out** — four `mobile-test` failures, with the evidence that they pre-date the merge (the same tests run against `origin/launchpad`'s tip) and the issue tracking them.

Every element of that maps onto something #306 is trying to decide, and it was produced by someone doing the job rather than designing the process. **It should be the starting template.** Its notable-changes section is also the answer to "how do you present 900 files without listing them": you don't — you present the handful that matter and state the policy covering the rest.

## Upstream supplies the narrative layer for free

[#356](https://github.com/launchpad-26/buzz/issues/356) established that upstream publishes a structured `CHANGELOG.md`: one section per desktop version, entries carrying a conventional-commit title, a PR link and a full commit SHA. It updates on essentially every drop.

So the report does not need to derive a human-readable narrative from `git log` — it can take upstream's own entries between the two pins and annotate them. **With one caveat that matters:** the changelog's only categories are "Desktop and shared changes" and "Other repository changes", so a relay change lands in either. It is a good *source* and a bad *organising principle* for this fork, which must re-sort it against its own operational tiers.

---

## The tension this creates, stated rather than resolved

[#364](https://github.com/launchpad-26/buzz/issues/364) established that upstream publishes no security advisories and that grepping commit subjects finds dependency advisories but barely finds code-level security fixes. Its affordable remedy was to read the commits touching the **operational surface**.

That is 3,125 changed lines — **7.8× the threshold at which defect detection sharply declines.** So the two requirements pull apart:

- **Adjudication** wants the contested surface: 385 lines, in the effective band, and that is what ADR-0022 scopes.
- **Security awareness** wants the operational surface: 3,125 lines, which cannot be read effectively in one sitting.

**Three honest ways out, offered as input to #306 rather than as a recommendation:**

1. **Two artifacts, two purposes.** A short adjudication section (contested surface, ~385 lines, reviewed properly) plus a longer operational-surface digest read for awareness rather than approval — explicitly labelled as not-a-review, so it cannot masquerade as one.
2. **Chunk the operational surface.** 3,125 lines is ~8 sittings at 400. Affordable if drops are infrequent, and drops are deliberate under the corrected premise. But 8 sittings is real human time and someone must agree to spend it.
3. **State that the fork does not detect upstream source-level security fixes**, and accept it. The least satisfying and the most honest of the three if nobody will spend the time — and far better than a digest nobody reads that implies otherwise.

**What must not happen is option 1 without the label.** A long digest presented alongside a short review reads as though both were reviewed, which is precisely the failure ADR-0022 was written to avoid, reintroduced inside the artifact meant to prevent it.

---

## What this means for #273

**ADR-0022 should carry the numbers.** Its reasoning currently rests on a stated intuition about skimming. 385 versus 3,125 versus 117,113, against a 200–400 band, is the same argument with evidence, and it will survive challenge from the next person who reads it.

**#306 should start from PR #216's body, not a blank page**, and should take upstream's `CHANGELOG.md` entries as its narrative source rather than deriving one from diffs.

**One thing the research does not support, and I want to be careful about it.** The 200–400 figures come from studies of *code review for defects* — Cisco/SmartBear and Google-derived guidance. A drop report is not quite that: much of it is adopt/decline judgement rather than defect hunting, and the reviewer's question is "does this collide with something we own" rather than "is this code correct". The thresholds are the best available quantification and they are being applied slightly outside the setting that produced them. I would rather say that than let a borrowed number look load-bearing.

**And a caution on the moving-target finding.** Because the drop grows ~18 commits/day, any report is stale on arrival. That argues for computing the report *at the moment the drop is taken* rather than on a schedule — which is consistent with the corrected premise's deliberate, human-triggered drops, and is an argument against the scheduled-report half of [#295](https://github.com/launchpad-26/buzz/issues/295)/[#305](https://github.com/launchpad-26/buzz/issues/305) being the thing that produces the adjudication artifact.

---

## Confidence and limits

**High** on the measurements — all four line counts are `git diff --shortstat` output, reproducible from the commands above, and the 67→80 growth was observed twice in one session.

**Medium on the thresholds, and this is the document's main weakness.** The 200–400 band, the >400 decline and the <50%-past-1,000 figure are consistently reported across the sources I read, but I reached them through secondary summaries — practitioner and vendor blog posts citing the Cisco/SmartBear study and Google guidance — **not through the primary studies themselves.** I did not read the original Cisco/SmartBear report. Numbers that travel through several blog posts acquire false precision, and I would treat "a few hundred lines" as the robust claim and the exact figures as indicative.

**Not verified.** I did not examine any real Renovate or Dependabot PR body, so the claim in #365 as filed that those are "the most-acted-on adoption artifacts in existence" is not something I established — I have dropped it rather than repeat it. I found no research on whether people act on **machine-written** summaries specifically, which was part of the issue's definition of done; that half is unanswered, and it bears on #306's "whether a model writes any of it" and on [#303](https://github.com/launchpad-26/buzz/issues/303). I did not measure how long PR #216's body takes to read, nor ask its author how long the drop took. I did not test any report format on a human, which is the only way to actually answer "does this get read" — everything here is inference from published thresholds plus one precedent.

## Sources

- [Empirically supported code review best practices — Graphite](https://graphite.com/blog/code-review-best-practices) — 200–400 line band, decline past 400
- [The Impact of PR Size on Code Review Quality — Propel Code](https://www.propelcode.ai/blog/pr-size-impact-code-review-quality-data-study) — 80–90% at 200 lines, below 50% past 1,000
- [Proof your thousand-line pull requests result in more bugs — tekin.co.uk](https://tekin.co.uk/2020/05/proof-your-thousand-line-pull-requests-create-more-bugs) — defect density falling above 300, tailing off above 500
- [Pull Request Size: Ideal Limits — Engineering Manager Tools](https://www.em-tools.io/engineering-metrics/pull-request-size) — the 60-minute sitting limit
- PR [#216](https://github.com/launchpad-26/buzz/pull/216) in this repository — the worked precedent

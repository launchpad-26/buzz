# Enforcing "a change to an upstream-owned file requires a ledger row"

**Title:** Five enforcement mechanisms, their cost to contributors, and a tested CODEOWNERS pattern set
**Summary:** **CODEOWNERS expresses the boundary in six lines** — tested against the real 4,351-file tree, it partitions 4,029 upstream-owned from 322 fork-owned with a **two-file residue that is arguably correct**. GitHub has no `!` negation, but "a pattern with no owners" plus last-match-wins does the job. Measured the CI-check option's real cost: **11 of 60 merged PRs touched an upstream path** — 8 correctly, 2 false positives CODEOWNERS gets right, and **1 catastrophic: the 981-file drop PR**. That is the finding — the CI check's cost is O(files) and CODEOWNERS' is O(1) per PR, and the check is useless exactly when the ledger matters most.
**Tags:** `upstream-sync` `ledger` `codeowners` `ci` `prd-273` `adr-0022`
**Established:** 2026-08-22 · **Answers:** [#369](https://github.com/launchpad-26/buzz/issues/369) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

**References are pinned.** Every claim about a file in this fork cites `launchpad-26/buzz` at
[`5d76799d6e44f2f76aa7bd78c5343d339af98f63`](https://github.com/launchpad-26/buzz/tree/5d76799d6e44f2f76aa7bd78c5343d339af98f63). The CODEOWNERS partition was computed
against that same tree. Paths inside fenced blocks are command *output* and are left unlinked
deliberately — the file lists are what the commands printed.

---

## Finding

**The cheapest mechanism is also the most accurate, and it was not in [#301](https://github.com/launchpad-26/buzz/issues/301)'s options.**

| Mechanism | What it assures | Cost to a contributor | Can it block today? | Failure mode |
|---|---|---|---|---|
| **CODEOWNERS** | The boundary was *reviewed* | **O(1)** — one review request per PR | No — needs `require_code_owner_reviews`, currently `false` | Reviewer rubber-stamps |
| CI check for a ledger row | The boundary is *documented* | **O(files)** — a row per touched file | No — no required checks exist | **Breaks on drop PRs (981 files)** |
| `lefthook` pre-push hook | Same, earlier | O(files), plus local run time | No — bypassable with `--no-verify` | Silently skipped |
| Post-merge assertion | Divergence is *noticed* | Zero | N/A — reports, does not gate | Report nobody reads |
| Nothing + scheduled drift report | Drift is *visible* | Zero | N/A | Same, plus latency |

---

## CODEOWNERS: tested, not read about

GitHub's CODEOWNERS has no negation — *"using `!` to negate a pattern doesn't work"*, alongside two other gitignore features that also do not work (escaping `#`, and `[ ]` character ranges). But it has the mechanism that matters:

> "you can exclude a subdirectory by adding a pattern for it without specifying any owners"

with last-match-wins precedence. So "own everything, then un-own what the fork owns" is expressible.

### The pattern set

*Authored by me for this assessment. It is a proposal, not something the repository contains.*

```
*                                    @launchpad-26/boundary-reviewers
/launchpad/
/.github/workflows/launchpad-*.yml
/.claude/
/.github/ISSUE_TEMPLATE/
/LAUNCHPAD.md
```

### Tested against the real tree

Implemented the documented semantics — gitignore-style globs minus negation and character ranges, last matching line wins, a line with no owners removes ownership — and ran it over every tracked file on `launchpad`:

```
tracked files:            4351
CODEOWNERS-owned:         4029
CODEOWNERS-unowned:        322

fork-added files STILL owned (would trigger a review request): 2
    desktop/src-tauri/src/managed_agents/runtime/summary.rs
    scripts/test-ci-changed-paths-filter.sh
```

**Six lines, and a residue of two files out of 321 fork additions.**

**And the residue is arguably correct rather than a defect.** Both files are fork-only additions that live *inside upstream's directory structure* — [`summary.rs`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/desktop/src-tauri/src/managed_agents/runtime/summary.rs) in upstream's `managed_agents/` tree, `test-ci-changed-paths-filter.sh` in upstream's `scripts/`. A change to either genuinely touches the upstream boundary. `summary.rs` is the strongest case: [#360](https://github.com/launchpad-26/buzz/issues/360) found that the drop's one semantic conflict landed exactly there, because it holds code extracted from an upstream-owned file. If any two fork files deserve boundary review, these are they.

Excluding them anyway would take two more no-owner lines. **I would not**, and that is the point worth carrying to #301: the pattern set is not merely expressible, it lands on a defensible boundary on the first attempt.

## The CI check's real cost, measured

[#301](https://github.com/launchpad-26/buzz/issues/301) weighs "a contributor fixing a typo in an upstream-owned file gets a red check". Measured against the last 60 merged PRs into `launchpad`:

```
merged PRs sampled: 60
PRs touching an upstream-owned path: 11
```

| # | Upstream files | What it was | Would a ledger-row check be right to fire? |
|---|---|---|---|
| #259 | 1 | h2 RUSTSEC bump | **Yes** — created the `Cargo.lock` divergence |
| #257 | 3 | `--format json` for pack inspect (#239) | **Yes** — created 3 product-code divergences |
| #221 | 2 | `cfg(unix)` gating for Windows | **Yes** |
| #205 | 2 | Windows sidecar stubs | **Yes** |
| #192 | 3 | lefthook 2.1.10 pin | **Yes** |
| #182 | 2 | ci.yml paths-filter fix | **Yes** |
| #169 | 1 | branch-skew redirect | **Yes** |
| #238 | 1 | `AGENTS.md` | **Yes** |
| #194 | 1 | `.claude/skills/agentic-debugging/SKILL.md` | **No — false positive** |
| #189 | 5 | `.claude/skills/review-final/*` | **No — false positive** |
| **#216** | **981** | **the upstream sync** | **No — catastrophic** |

**So the naive check is more accurate than #301 assumes on ordinary PRs — 8 of 10 firings are correct — and it is broken in two specific ways.**

**The false positives are fork-only additions living outside `launchpad/`.** `.claude/skills/*` are fork files at an upstream-owned path prefix. A path-based check flags them; **CODEOWNERS does not**, because the pattern set un-owns `/.claude/`. That is a concrete accuracy win for CODEOWNERS, not a tie.

**The catastrophic case is the one that matters.** A drop PR touches 981 upstream-owned files and creates no new divergence. A check demanding a ledger row per touched file would demand 981 rows on every drop — so it must exempt drop PRs, and **the drop is precisely when divergence is most likely to be silently lost.** A gate that switches itself off during the event it exists to guard is not a gate.

CODEOWNERS has no equivalent failure: a 981-file drop PR produces **one review request**. Its cost is O(1) in the size of the change; the CI check's is O(files). For a fork whose largest PRs are drops, that difference is the whole comparison.

## Neither can block today

From [#358](https://github.com/launchpad-26/buzz/issues/358)'s measurement of `launchpad`'s protection:

```
{"approvals":1,"checks":null,"codeowners":false,"enforce_admins":false, ...}
```

- `checks: null` — no required status check, so a CI check reports and cannot block.
- `codeowners: false` — `require_code_owner_reviews` is off, so CODEOWNERS would **auto-request review from the owning team and not require it**.

Both are one admin action away, and #358 established that four people including the owner of this work already hold repository admin. **So "can it block" is not a discriminator between the two options** — it is the same single toggle either way, and the "needs an org admin" premise that shaped #301 is false.

One asymmetry worth noting: with `require_code_owner_reviews` on, CODEOWNERS blocks by requiring a *human*, which cannot be satisfied by writing a row. That is stronger assurance than a check that a row exists, and weaker assurance that the row exists. They assure different things — **"someone looked" versus "it is written down"** — and #301 is really choosing between those two properties, not between two implementations.

## The other three, briefly

**[`lefthook`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/lefthook.yml) pre-push hook.** Same assurance as the CI check, earlier and cheaper to iterate on, and bypassable — `git commit --no-verify` and `git push --no-verify`, and [`lefthook.yml:14-15`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/lefthook.yml#L14-L15) documents that `git rebase` and `git cherry-pick` do not run `commit-msg` at all. PR #216 was itself pushed with `--no-verify`, which is the empirical answer to whether the bypass gets used. Also `lefthook.yml` is one of the 27 contested files, so the enforcement mechanism would live in a file the boundary it enforces is about.

**Post-merge assertion.** Reports rather than gates, so it cannot block a PR — but it is the only option that catches divergence arriving by a path no gate covers, including inside a drop. Zero contributor cost. Same shape as the mechanism [#362](https://github.com/launchpad-26/buzz/issues/362) and [#366](https://github.com/launchpad-26/buzz/issues/366) recommend for position durability, which means one mechanism could serve both.

**Nothing, plus a scheduled drift report.** The option #301 does not list, and it has a precedent in this repository: [#293](https://github.com/launchpad-26/buzz/issues/293) argues for exactly this shape for project-board membership, on the ground that *"an auto-add that stops working looks exactly like an auto-add that is working"* and that *"a control whose failure is invisible provides no assurance"*. The same argument transfers: a ledger check that is exempted on drop PRs looks exactly like a ledger check that is working. #293's remedy — compare the two sets and fail loudly when they diverge — maps directly onto comparing the ledger's rows against the computed contested set, which [#368](https://github.com/launchpad-26/buzz/issues/368) established is two git commands.

**Assessed on merits rather than as a null option:** it is the only choice that costs contributors nothing, cannot be bypassed, and works during a drop. It gives up pre-merge prevention entirely, which is a real loss, and #293's own framing is that detection you can trust beats prevention you cannot.

---

## What this means for #273

*This section is my recommendation as the author, not a finding — including the claim that neither mechanism alone closes the drop-PR hole, and the pattern set itself, which I authored rather than found. The measurements above are the evidence; the judgement is mine and carries no source reference.*

**#301's options are missing the cheapest and most accurate one.** CODEOWNERS was not in that issue. Six lines, tested, O(1) cost, and it correctly excludes the `.claude/skills/*` class that a path-based check gets wrong.

**#301 is choosing between two different assurances, and should say which it wants.** "Someone reviewed the boundary" (CODEOWNERS) and "the divergence is written down" (ledger check) are not the same property, and neither implies the other. The framing as an implementation choice obscures that.

**The drop-PR exemption is the hole to design around, whichever way it goes.** Under ADR-0022 a contested file with no ledger row is never presented for adjudication at all — so a missing row is a lost decision, and the mechanism that must not fail is precisely the one that fails on drops. The combination that covers it is CODEOWNERS (pre-merge, O(1), survives drops) plus a post-merge or scheduled comparison of ledger rows against the computed contested set (catches what review missed). That is not a recommendation — #301 owns it — but neither half alone closes the hole.

**One thing that is now cheap and was assumed expensive.** #301 asks "what does it cost contributors". For CODEOWNERS the measured answer is: 11 of 60 recent PRs would have triggered a review request, 8 of them for changes that genuinely created divergence. That is roughly one extra review a fortnight at this repository's rate, not a tax on ordinary work.

---

## Revised for the fork's horizon (#357)

Added after @tucktuck101 decided on 2026-08-22 that the fork ends with the cohort project on
2026-09-17. An enforcement mechanism is a control that pays off over time, so the horizon changes
what is worth building.

**The measurements are unchanged.** The CODEOWNERS partition (4,029 / 322, two-file residue) and the
11-of-60 firing rate with its 8 correct / 2 false / 1 catastrophic split both stand.

*The rest of this section is my recommendation as the author, not a finding.*

**CODEOWNERS goes from cheapest to clearly correct.** Six lines, no build, no script to maintain, and
it can be shown working by opening one PR that touches an upstream file. That is the shape a
demonstrative target wants. Its one prerequisite — a team to own the paths — is the only real cost and
it is minutes.

**The CI-check option should now be rejected rather than weighed.** It needs a script, a required
check, a drop-PR exemption and ledger rows to check against. All of that is infrastructure whose
benefit accrues per PR over months. With weeks left it costs more to build than it can return, and
#301's comparison can be settled on that basis without further analysis.

**The drop-PR hole shrinks to something a person covers.** I wrote that a check exempting drop PRs
"is not a gate" and that neither mechanism alone closes the hole. True over many drops. With two or
three left, each taken deliberately by a human who reads the report, the hole is covered by the person
rather than by a mechanism — and [#365](https://github.com/launchpad-26/buzz/issues/365) established
that the adjudication surface is 385 changed lines, which is inside the band where a human review is
actually effective.

**What the ledger is now for.** Not preventing lost decisions over years, but recording the positions
the cohort took, so the reasoning survives as evidence even though the fork does not. That argues for
completeness of *reasoning* over completeness of *coverage* — consistent with
[#352](https://github.com/launchpad-26/buzz/issues/352) being closed on the ground that `unrecorded`
is the honest entry for the 19 files that have never conflicted.

## Confidence and limits

**High** on the measured PR figures and the classification of all 11 — each is a real merged PR whose files I listed and whose title states what it did, and the eight correct firings map onto divergences [#352](https://github.com/launchpad-26/buzz/issues/352) independently established.

**Medium-high on the CODEOWNERS result, and the limit is specific.** I tested the *pattern set* against the real file list using a local implementation of the documented semantics. **I did not validate it against GitHub's own parser.** GitHub exposes `GET /repos/{owner}/{repo}/codeowners/errors`, but that validates a CODEOWNERS file committed to the repository, and committing one is a change I am not making. So the partition is correct per the documented rules; whether GitHub's implementation agrees on every edge — particularly `/.github/workflows/launchpad-*.yml`, the only pattern using a wildcard — is unconfirmed. **That is the one thing worth checking before adopting it**, and it costs one commit on a throwaway branch.

**Not verified.** I sampled the 60 most recent merged PRs into `launchpad`, not all of them, so the 11/60 rate is recent-history and the repository has ~216 PRs. I did not check whether `@launchpad-26/boundary-reviewers` exists as a team — it does not; the pattern set names a team that would have to be created, and I did not check whether the org permits repository admins to create teams. I did not test `require_code_owner_reviews` behaviour by enabling it. I did not test the `lefthook` hook option at all — the bypass claim rests on `--no-verify` being documented and on PR #216 having used it, not on my running it. I did not measure how long a boundary reviewer would take on a drop PR, which is the real cost of the CODEOWNERS option and the one number I would most want. No builds were run; disk on this machine is at 99% capacity with 5.2 GiB free and nothing here needed one.

## Sources

- [About code owners — GitHub Docs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners) — no `!` negation, no `[ ]` ranges, no `#` escaping; exclude-by-no-owners; last-match-wins
- [Examples of CODEOWNERS `!` negation — github/docs#19818](https://github.com/github/docs/issues/19818) — the negation limitation as reported
- [#293](https://github.com/launchpad-26/buzz/issues/293) in this repository — the drift-report precedent and the invisible-failure argument
- [`launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/launchpad/decisions/ADR-0017-lefthook-pin-upstream-boundary-exception.md) and [`lefthook.yml:14-15`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/lefthook.yml#L14-L15) — hook coverage gaps

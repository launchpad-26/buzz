# How long-lived downstream forks structure divergence, and what goes wrong

**Title:** Prior art on long-lived fork maintenance, and where it contradicts PRD #273
**Summary:** Surveys four genuinely different maintenance models — patch-series-over-pristine-upstream (Debian, Yocto, Electron), merge-based long-lived branch, rebase-the-stack-per-release, and the three-branch vendor layout — with the failure modes their maintainers document. Finds one convention the fork should adopt almost verbatim (Yocto's `Upstream-Status`), one place where prior art unanimously contradicts a #273 non-goal (never upstreaming), and one documented failure mode that independently confirms what #360 found empirically. Also records where the sources disagree rather than averaging them.
**Tags:** `upstream-sync` `vendor-branch` `prior-art` `patch-series` `prd-273` `adr-0021`
**Established:** 2026-08-22 · **Answers:** [#361](https://github.com/launchpad-26/buzz/issues/361) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**The fork's mechanism choices are mostly defensible. Its *policy* choice — never send anything upstream — is the one thing every source surveyed treats as the primary lever, and #273 rules it out in a non-goal.**

Three things worth acting on, in order of value:

1. **Yocto's `Upstream-Status` convention is the missing column in the divergence ledger.** Eight named values that classify each divergence by its relationship to upstream. [#352](https://github.com/launchpad-26/buzz/issues/352) established that 11 of this fork's 27 contested files are unsent upstream bug fixes and that **zero of 27 record any upstream intent**. That is precisely the gap `Upstream-Status` exists to close, and it has been solved and refined in a shipping project for over a decade.
2. **The clean-merge-but-wrong failure mode is documented prior art, not a local discovery.** Electron: *"When upstream code changes, patches can break—sometimes without even a patch conflict or a compilation error."* [#360](https://github.com/launchpad-26/buzz/issues/360) found exactly this by compiling. Two independent confirmations should end the argument about whether [#363](https://github.com/launchpad-26/buzz/issues/363)'s class is real.
3. **Every source says minimise the divergence and upstream what you can.** Electron: *"We should aim to upstream changes whenever we can, and avoid indefinite-lifetime patches."* The ArgoCD guide: *"every custom patch you maintain is technical debt"*, and forking should be *"the last resort"*. A Lobsters commenter with fork experience: *"always upstream your patches, and failing that, favor adding features at your own layer of abstraction over hastily adding them to a patched fork."*

That third point is not a mechanism note. **It is the load-bearing disagreement between prior art and this PRD**, and it is discussed at the end.

---

## The four models

### 1. Patch series over pristine upstream

Divergence lives as **files in a directory**, never as commits on a branch. Upstream is imported untouched; the local delta is a numbered, ordered series re-applied on each import.

- **Debian** — the `3.0 (quilt)` source format. *"Most Debian source packages are using the '3.0 (quilt)' format, which means that Debian changes to upstream files are managed in a quilt patch series"*, kept as files in `debian/patches`.
- **Yocto/OpenEmbedded** — patches per recipe, each carrying an `Upstream-Status` tag.
- **Electron** — *"All patches to upstream projects in Electron are contained in the patches/ directory"*, each subdirectory with a `.patches` file giving apply order, plus `git-import-patches` / `git-export-patches` to move between patch files and commits.

**What it buys:** the divergence is enumerable, reviewable and individually deletable. You can see the whole disagreement in one directory listing.

**Documented failure modes.** Fuzz and refresh churn: *"if you have quilt patches that only apply with fuzz … quilt applies those without failing but dpkg-source doesn't"*, requiring a pop-all/push/refresh cycle on every import. And the deep one, from Electron: *"When upstream code changes, patches can break—sometimes without even a patch conflict or a compilation error."*

**Why it partly does not fit here.** This model assumes you *build from* upstream rather than *operate* a branch of it, and it requires the patch series to be re-applied — which is the same work as resolving conflicts, differently packaged. Its real advantage is bookkeeping, not less work.

### 2. Merge-based long-lived branch

Upstream is merged into a long-lived branch; local changes are ordinary commits on it. This is [ADR-0021](https://github.com/launchpad-26/buzz/pull/308)'s choice.

**Documented failure modes**, and they are the most severe of any model surveyed:

- *"Merging upstream code into a fork can result in numerous conflicts with feature code that may take weeks to resolve, and the process must be repeated every time updates from upstream are needed."*
- **Obsolete divergence accumulates invisibly.** *"Long-lived forks may accumulate obsolete changes where similar changes have been made upstream, or early changes were superseded by later changes, making it harder to keep track of differences between fork and upstream."*
- At the extreme, it stops working: an LLVM fork maintainer reports *"it was prohibitively difficult to merge from upstream (I tried once and gave up)."*

The second is the one this fork should worry about, because it is already happening — [#352](https://github.com/launchpad-26/buzz/issues/352) found `Cargo.lock` diverging only because both sides bumped h2 independently, which is an obsolete divergence in the making.

### 3. Rebase the local stack onto each upstream release

Keep local work as a stack of commits and recreate it on each new upstream version. SIP.js: *"our own branch with our set of patches applied on top. Any time we upgraded, we'd recreate the branch."*

**Documented failure modes:** requires force-push, so it breaks anyone who has pulled; and rebase conflicts need manual intervention every cycle. The Linux kernel's maintainer documentation is emphatic about the first: *"History that has been exposed to the world beyond your private system should usually not be changed"*, because *"Others may have pulled a copy of your tree and built on it; modifying your tree will create pain for them"*, and *"Do not rebase a branch that contains history created by others."*

**Already correctly excluded here** — #273's non-goals rule out rebasing shared branches, and `launchpad` has eleven people working off it. Prior art agrees with that call.

### 4. The three-branch vendor layout

The closest published analogue to this fork's design, from a guide on maintaining an internal ArgoCD fork:

- `upstream-v2.10` — *"Mirror of upstream release-2.10 (never modify)"*
- `custom-v2.10` — the customised version
- `custom-patches` — individual commits for cherry-picking

**This independently validates the two-stage design.** A never-modified upstream branch beside a customised one is exactly `main` + `launchpad`, arrived at by someone solving the same problem. The two earlier reviews that recommended collapsing it because `main` "has no consumer" were reading against the grain of the standard pattern.

Its other specifics are worth noting because they are concrete: a scheduled trigger (*"Every Monday at 6 AM"* a pipeline detects new releases), patch files exported with `git format-patch upstream/release-2.10..custom-v2.10 -o .internal/patches/`, explicit tracking of *"which patches have been submitted upstream"*, and a `v<upstream-version>-custom.<patch-number>` tag scheme.

---

## Yocto's `Upstream-Status`, in full

The convention describes *"how each patch relates to the upstream project"*, and exists to *"track whether patches should be upstreamed"*, *"identify patches removable after source upgrades"*, *"reduce rebase effort"*, and *"avoid duplicated or obsolete patches"*.

| Value | Meaning |
|---|---|
| `Accepted` | Already merged upstream (optionally with commit id) |
| `Backport` | Exists upstream; backported to an older version |
| `Inappropriate` | Product-specific; will never be accepted upstream |
| `Denied` | Submitted and rejected |
| `Pending` | Under active review |
| `Submitted` | Sent upstream, not yet reviewed |
| `Submitted [Not-Accepted]` | Known to be unacceptable |
| `Unknown` | Status unclear — *"discouraged for production"* |

**Mapped onto this fork's 27 contested files** using #352's classification:

| This fork's class | Count | `Upstream-Status` |
|---|---|---|
| Unsent upstream bug fixes | 10 | `Unknown` today; should be `Submitted` or `Inappropriate` |
| Security bump (h2) | 1 | `Accepted` pending — upstream is bumping it independently |
| ADR-0005 deployment identity | 5 | `Inappropriate` — fork identity, never upstreamable |
| ADR-0017 lefthook pin | 2 | `Inappropriate` — caused by the fork's own branch name |
| Cohort process files | 6 | `Inappropriate` |
| Fork feature (#239 pack JSON) | 3 | `Unknown` — nobody has decided |

**Every row is currently `Unknown`, and 11 of them should not be.** That is the single cheapest improvement to the ledger available, and it is a column, not a project.

The two conventions that go with it are equally cheap. Electron: *"Every patch must describe its reason for existence in its commit message."* Yocto discourages `Unknown` in production. Both are exactly what #352 found missing.

---

## Where the sources disagree

Reported rather than averaged, because the disagreements are substantive.

**Merge versus don't-merge.** The kernel documentation argues against routine back-merges from upstream: they *"muddy the development history of your own branch"*, *"significantly increase your chances of encountering bugs from elsewhere in the community"*, *"make it hard to ensure that the work you are managing is stable"*, and *"can hide interactions with other trees that should not be happening"*. The ArgoCD guide and the long-lived-fork blog post both merge or reset-and-cherry-pick without apology.

**This is a real disagreement but it does not transfer cleanly, and it would be dishonest to score ADR-0021 against it.** The kernel guidance addresses a maintainer *feeding* upstream, whose branch will be pulled by Linus; "muddying history" is a cost paid at the point of contribution. A fork that never contributes upstream — this one, by its own non-goal — has no such point. The kernel's third objection does bite, though: *"can hide interactions with other trees"* is a general description of the clean-merge-but-wrong class, and it applies here.

**Whether the fork is avoidable at all.** Lobsters commenters split. One argued most "secret sauce" justifications prove false: *"if it actually is valuable, upstream will implement the same feature in a different way."* Others defended forking for regulatory requirements and experimental research. This fork's case is different again — it forks to *operate*, not to differentiate — which none of the surveyed sources addresses directly. The 21 fork-only additions under `launchpad/` are exactly the "add features at your own layer of abstraction" advice already being followed, and they cost nothing per drop.

**Cadence.** The ArgoCD guide schedules weekly and treats automation failure as the signal. The patch-series projects import on upstream's release cadence. Nothing surveyed supports the deliberate-and-unscheduled model in the corrected premise — but nothing argues against it either; the question simply is not addressed, because none of these projects has a vendor branch whose purpose is comparison.

---

## What this means for #273

**Adopt `Upstream-Status` as a ledger column.** Concrete, cheap, proven, and it directly fills the gap #352 measured. It also does something no current column does: it gives a divergence a **termination condition**. `Submitted` becomes `Accepted` and the row is deleted. That is the mechanism by which a patch set shrinks instead of growing, and #273 currently has no such mechanism.

**The non-goal "No PRs sent back to `block/buzz`" is the fork's largest unpriced cost.** Every source surveyed treats upstreaming as the primary way to reduce maintenance load — not a nice-to-have. Combined with #352's finding that **11 of 27 contested files are bug fixes upstream would very likely take**, the fork is paying permanent conflict cost for changes it could stop owning. That non-goal was recorded on the ground that ADR-0017 says the cohort is not currently sending changes upstream; it has never been costed against the alternative. **This is a decision, not a documentation fix**, and it may be the highest-leverage one left in the PRD.

**Two of the fork's design choices are validated by prior art and should stop being re-litigated.** The three-branch vendor layout is a standard pattern, and not rebasing a shared branch is unanimous.

**One warning the fork should take seriously.** Obsolete divergence accumulating invisibly is the documented failure of the merge-based model, it is already visible here in `Cargo.lock`, and nothing in #273 detects it. A ledger with `Upstream-Status` plus a periodic check of "does upstream now contain an equivalent of this row?" is the standard answer.

---

## Confidence and limits

**Medium-high.** The four models are described from primary or near-primary sources — Electron's own documentation, Debian's own wiki and maintainer guides, the kernel's own maintainer documentation. Every quotation is verbatim from the linked page.

**The weakest sources are the two blog posts and the Lobsters thread**, used for reported experience rather than for policy. The ArgoCD guide is a third-party post, not ArgoCD's own documentation, so its three-branch layout is one practitioner's recommendation, not a project standard — its value here is as an independent arrival at the same design, and it should not be cited as authority.

**Not checked.** Whether Yocto machine-checks `Upstream-Status` values — the source I read explicitly does not say, and it matters to [#369](https://github.com/launchpad-26/buzz/issues/369). I did not read Debian Policy or the Developer's Reference directly, only the wiki and maintainer howtos. I did not examine AOSP, Chromium's own downstream tooling, Gentoo, RHEL or the BSD ports systems, all of which would likely add models — the survey covers four models well rather than eight badly, and a second pass would most usefully start with AOSP, since Android's kernel fork is the largest long-lived fork in existence. I did not quantify any cost claim: no source I found publishes measured per-import effort, so all cost statements here are practitioner report, not data. I did not contact any maintainer.

## Sources

- [Patches in Electron](https://www.electronjs.org/docs/latest/development/patches) — Electron's patch policy and the break-without-conflict failure mode
- [Rebasing and merging — The Linux Kernel documentation](https://docs.kernel.org/maintainer/rebasing-and-merging.html) — the case against rebasing published history and against routine back-merges
- [Understanding `Upstream-Status` in Yocto Patches](https://www.mitkov-systems.de/en/blog/understanding-Upstream-Status-in-Yocto-Patches) — the eight-value classification
- [How to use quilt to manage patches in Debian packages](https://raphaelhertzog.com/2012/08/08/how-to-use-quilt-to-manage-patches-in-debian-packages/) and [UsingQuilt — Debian Wiki](https://wiki.debian.org/UsingQuilt) — the `3.0 (quilt)` model and fuzz/refresh churn
- [How to Maintain an Internal ArgoCD Fork](https://oneuptime.com/blog/post/2026-02-26-argocd-maintain-internal-fork/view) — the three-branch vendor layout, scheduled trigger, patch-debt framing
- [Those who have maintained forks of OSS at work, what was your experience like? — Lobsters](https://lobste.rs/s/yav1ky/those_who_have_maintained_forks_oss_at) — practitioner reports, including the LLVM "tried once and gave up"
- [Git Tricks for Maintaining a Long-Lived Fork](https://die-antwort.eu/techblog/2016-08-git-tricks-for-maintaining-a-long-lived-fork/) — reset-to-upstream plus cherry-pick
- [Downstream (software development) — Wikipedia](https://en.wikipedia.org/wiki/Downstream_(software_development)) — obsolete-divergence accumulation

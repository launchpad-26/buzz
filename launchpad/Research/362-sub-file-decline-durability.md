# Making a sub-file decline survive repeated merges

**Title:** How other projects keep a hunk-level position durable across upstream imports, and two corrections to ADR-0021
**Summary:** Answers the question with three practices from prior art plus one nobody in the #273 thread has named. In doing so it corrects two claims in ADR-0021's recorded reasoning, both from primary documentation: a custom merge driver is **an arbitrary program** receiving all three versions, so it is not limited to file-granular *decisions* — only the attribute mapping is file-granular. **Demonstrated by building one and running it against the real `lefthook.yml` conflict: it merges cleanly, adopts all 66 of upstream's changed lines, preserves the fork's one-line position, and fails loudly when its anchor disappears.** And `rerere`'s failure mode is mis-stated: declining to replay is **loud** (you get a normal conflict); the silent hazard is `rerere` **succeeding** with a resolution that has gone stale.
**Tags:** `upstream-sync` `vendor-drop` `rerere` `merge-driver` `adr-0021` `prd-273`
**Established:** 2026-08-22 · **Answers:** [#362](https://github.com/launchpad-26/buzz/issues/362) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**Nobody has a cheap answer, and everyone pays per import — but the fork's option list is shorter than it needs to be, for two reasons that are both documentation errors rather than design constraints.**

Four practices, ordered by how well they fit `lefthook.yml` — the fork's worked case, "upstream wins on all of it except one line":

| Practice | Expresses a one-line exception? | Cost per import | Failure mode |
|---|---|---|---|
| **Transforming merge driver** | **Yes** | Zero once written | Silent if upstream renames the thing it anchors on |
| Post-merge invariant assertion | Yes (detects, does not resolve) | Zero | None silent — it either passes or fails |
| Patch re-application (quilt/Electron) | Yes | Refresh churn every import | Breaks "without even a patch conflict or a compilation error" |
| `rerere` replay | Partially | Zero when it fires | **Loud when it declines; silent when it fires stale** |

The first is the one ADR-0021 says does not exist. It does.

---

## Correction 1 — a merge driver is an arbitrary program, not a file-level verdict

ADR-0021 records, as accepted reasoning, that "a merge driver is durable but only file-granular". That conflates two different things, and the distinction is load-bearing.

**File-granular:** which files a driver applies to. `.gitattributes` maps paths to drivers, and *"When more than one pattern matches the path, a later line overrides an earlier line"* — one driver per file, last match wins.

**Not file-granular:** what the driver *does*. From git's own documentation:

> "The `merge.*.driver` variable's value is used to construct a command to run to common ancestor's version (`%O`), current version (`%A`) and the other branches' version (`%B`). These three tokens are replaced with the names of temporary files that hold the contents of these versions when the command line is built."

> "The merge driver is expected to leave the result of the merge in the file named with `%A` by overwriting it, and exit with zero status if it managed to merge them cleanly, or non-zero if there were conflicts."

It is *"an arbitrary program"* with all three versions on disk and free rein over the output. So a driver for `lefthook.yml` can:

1. copy `%B` (upstream's version) over `%A` — upstream wins the whole file, wholesale;
2. re-apply the fork's single change to it — `sed`, a patch, a YAML edit, whatever;
3. exit 0 if the re-application succeeded, non-zero if it did not.

That is exactly "upstream wins on all of `lefthook.yml` except one line", durably, with no `rerere` cache and no per-import work. **`merge=ours` is not the only option; it is the only *built-in* option.** The three built-ins are `text`, `binary` and `union`, and `union` *"take[s] lines from both versions"* with the caveat *"Do not use this if you do not understand the implications"* — none of them fit, which is presumably where the file-granular reading came from.

### Demonstrated, not inferred

Built the driver and ran it against the real three versions of `lefthook.yml` — merge-base `f8692fa9b`, `launchpad/launchpad`, and `upstream/main` — in a throwaway repository.

The fork's entire divergence is one line plus its comment:

```
$ diff base.yml ours.yml
53c53,57
<       run: ./scripts/check-branch-skew.sh
---
>       # launchpad-26/buzz#15: the upstream script assumes origin/main is the PR
>       # base, which is wrong for this fork (base is `launchpad`, remote name
>       # varies by contributor). launchpad/scripts/check-branch-skew.sh carries
>       # the cohort-correct logic without touching the upstream script itself.
>       run: ./launchpad/scripts/check-branch-skew.sh

$ diff base.yml theirs.yml | grep -c '^[<>]'
66
```

**Without the driver — the conflict the fork has today:**

```
$ git merge --no-commit theirs
Auto-merging lefthook.yml
CONFLICT (content): Merge conflict in lefthook.yml
Automatic merge failed; fix conflicts and then commit the result.
```

**With the driver:**

```
$ git config merge.lefthook-fork.driver "lefthook-driver.sh %O %A %B"
$ echo 'lefthook.yml merge=lefthook-fork' > .gitattributes
$ git merge --no-commit theirs
Auto-merging lefthook.yml
Automatic merge went well; stopped before committing as requested
```

The merged result is byte-identical to upstream's version except the fork's five-line block:

```
$ diff theirs.yml lefthook.yml
82c82,86
<       run: ./scripts/check-branch-skew.sh
---
>       # launchpad-26/buzz#15: the upstream script assumes origin/main is the PR
>       ... (4 more lines)
>       run: ./launchpad/scripts/check-branch-skew.sh

$ grep -n 'push-head-scope\|file-size-check\|rc: bin/.lefthookrc\|mobile-fmt\|mobile-checks' lefthook.yml
41:rc: bin/.lefthookrc
65:    mobile-fmt:
87:    push-head-scope:
94:    file-size-check:
124:    mobile-checks:
```

Every one of upstream's new lanes is adopted. The fork's position survives. There is no conflict.

The driver is about twenty lines: copy `%B` over `%A`, assert the anchor line is present, substitute the fork's block, assert the postcondition, exit 0.

**And it fails loudly when the anchor disappears.** Simulated upstream renaming the lane:

```
$ git commit -am "upstream: rename check-branch-skew.sh -> check-branch-divergence.sh"
$ git merge --no-commit theirs
lefthook-driver: anchor line not found in upstream version — fork position cannot be re-applied
Auto-merging lefthook.yml
CONFLICT (content): Merge conflict in lefthook.yml
Automatic merge failed; fix conflicts and then commit the result.
--- git merge exit: 1
$ git status --short lefthook.yml
UU lefthook.yml
```

A non-zero exit leaves the file conflicted and the merge failed — exactly the escalation the fork wants, rather than a silently dropped position.

**The catch, stated honestly.** A transforming driver is only as durable as its anchor. Step 2 has to locate the thing to change; if upstream renames the `branch-skew` lane, a `sed` finds nothing and the driver either fails loudly (good, if it checks) or silently drops the fork's position (bad, if it does not). So the driver must **verify its own postcondition and exit non-zero when the anchor is gone.** That is a five-line discipline, not a design problem, and it converts the failure from silent to loud — which is the property the fork actually wants.

Also worth stating: the driver definition lives in git config, not in the repository, so it is inert until every clone and every CI runner defines it. That part of ADR-0021 and [#300](https://github.com/launchpad-26/buzz/issues/300) is correct and unaffected.

## Correction 2 — `rerere`'s failure mode is the opposite of the one recorded

ADR-0021 records that `rerere` *"matches on a hash of the conflict preimage; when upstream evolves the code around a declined hunk the preimage changes and the replay **silently stops firing** — precisely when upstream is most active."*

The mechanism is not a bare hash lookup. From git's own documentation:

> "Next time, after seeing the same conflicted automerge, running _git rerere_ will perform a three-way merge between the earlier conflicted automerge, the earlier manual resolution, and the current conflicted automerge. If this three-way merge resolves cleanly, the result is written out to your working tree file, so you do not have to manually resolve it."

Two consequences, both material:

- **`rerere` absorbs some context drift.** It is a three-way merge, not an equality test, so modest movement around the hunk still replays. The recorded claim overstates the fragility.
- **When it does not resolve cleanly, nothing is written and you get an ordinary conflict.** That is *loud*, not silent. A conflict is exactly the signal the fork wants.

**The real silent hazard is the reverse, and it is not recorded anywhere.** If the three-way merge *does* resolve cleanly but upstream's intent has changed underneath, `rerere` writes the stale resolution into the working tree — and with `rerere.autoUpdate` it stages it too. That is a wrong answer applied automatically with no conflict shown. Git's own tooling acknowledges the case by providing `git rerere forget <pathspec>` to *"Reset the conflict resolutions which rerere has recorded for the current conflicts in paths that match <pathspec>"* — a command that only makes sense because bad resolutions persist and reapply.

Practitioner accounts corroborate both directions: *"If you modified a line too close to a diff in the preimage, rerere will refuse to consider that image+fix pair"* (declines, loud), and *"If for any reason you solve the conflict in a wrong way, you have to remove the resolution manually, otherwise it will be applied again and again"* (fires stale, silent).

There is also a documented recording failure worth knowing: *"git rerere relies on the conflict markers in the file to detect the conflict. If the file already contains lines that look the same as lines with conflict markers, git rerere may fail to record a conflict resolution."*

**So the honest statement for the record is:** `rerere` is a labour-saver whose replay may decline (loud, harmless) or fire stale (silent, harmful). ADR-0021's conclusion — that it is not a durability mechanism — survives; its stated reason does not.

---

## The two practices from prior art

### Patch re-application

The Debian/Yocto/Electron model, covered in [#361](https://github.com/launchpad-26/buzz/issues/361): the divergence is a patch file, re-applied on every import. It expresses a one-line exception perfectly, because a one-line exception *is* a one-line patch.

**Cost is real and recurring.** Debian's `3.0 (quilt)` format needs a refresh cycle whenever context drifts — *"if you have quilt patches that only apply with fuzz … quilt applies those without failing but dpkg-source doesn't"*, fixed by popping the whole series and re-pushing with `quilt refresh`. Electron ships `git-import-patches` / `git-export-patches` specifically to move between patch files and commits, which is the same work automated.

**And it fails in the way this fork should care about most:** *"When upstream code changes, patches can break—sometimes without even a patch conflict or a compilation error."* Patch re-application does not solve the clean-but-wrong class either.

### Upstream-Status as a termination condition

Not a durability mechanism — the opposite, and that is the point. Yocto's classification (see #361) makes each divergence carry its relationship to upstream, so `Submitted` becomes `Accepted` and the row is **deleted**. The cheapest way to make a sub-file position durable is to stop needing it.

For this fork that is not abstract: [#352](https://github.com/launchpad-26/buzz/issues/352) established that 11 of the 27 contested files are unsent upstream bug fixes. Eleven positions that could terminate rather than be maintained forever.

### The fourth practice: assert, don't preserve

Absent from the #273 thread entirely. Instead of asking git to carry the position through the merge, **check after the merge that the position still holds**:

```
# illustrative, not proposed
grep -q 'launchpad/scripts/check-branch-skew.sh' lefthook.yml
```

Properties that make it worth considering seriously:

- **Not file-granular, not hunk-granular — arbitrary.** It can assert anything checkable.
- **Cannot fail silently.** It passes or it fails.
- **Catches the clean-merge case**, which no merge-time mechanism does — including the `relay_url` defect [#360](https://github.com/launchpad-26/buzz/issues/360) found by compiling, had someone written an assertion for it.
- **Needs no git configuration**, so it has no bootstrap problem and works identically on a contributor machine and a CI runner.

It does not *resolve* anything, so it is a complement to a driver rather than a replacement. But "notice when our position was lost" is a strictly easier problem than "make git preserve it", and the fork has one measured instance where it would have been the only thing that worked.

---

## What this means for #273

**[#294](https://github.com/launchpad-26/buzz/issues/294)'s mechanism column should have four values, not two.** `merge=ours` / `always escalate` is a false binary. The candidates are: transforming driver, post-merge assertion, `rerere` replay, always-escalate — and for the fork's actual rows, most of the 27 need none of them, because 21 fork-only additions cannot conflict and the ADR-0005 five are whole-file positions that `merge=ours` genuinely does fit.

**`lefthook.yml` is solvable and has been treated as unsolvable.** It is the standing counter-example in ADR-0021, #294 and #300 for "no mechanism can hold this". A transforming merge driver holds it, demonstrated above on the real file. That does not reopen ADR-0021 — merge-based adoption is unaffected — but it removes the example those records lean on.

**ADR-0021's `rerere` reasoning should be corrected, not reversed.** Its conclusion is right and its stated mechanism is wrong, and the difference matters because the *correct* hazard (fires stale, silently, with `autoUpdate`) argues for a policy the record does not contain: **do not enable `rerere.autoUpdate` on drop merges.** An unattended stale replay that stages itself is the worst available outcome.

**The honest overall answer to the question as asked:** everyone pays per import, nobody has found a way not to, and the fork's specific relief is not a better durability mechanism — it is having eleven fewer rows to keep durable.

---

## Confidence and limits

**High** on both corrections. Each rests on git's own reference documentation, quoted verbatim: `gitattributes(5)` for the driver contract and pattern precedence, `git-rerere(1)` for the three-way replay and `forget`. These are the authoritative sources for exactly these claims.

**The transforming-driver claim is demonstrated, not inferred** — see the section above. What that test does *not* establish: it ran in a synthetic two-branch repository, not against the real 912-file drop, and the driver was defined in local git config, so it says nothing about the bootstrap problem (#300) beyond confirming the problem exists. It also tested one anchor shape — an exact-match line — and a driver anchoring on something fuzzier (indentation, a YAML key path) could behave differently.

I did not test `rerere` empirically at all — neither the three-way replay nor the stale-fire hazard — that is [#367](https://github.com/launchpad-26/buzz/issues/367)'s question and I have deliberately left it there rather than pre-empting it with untested claims. I did not measure any per-import cost; the quilt and Electron costs are described by their projects, not quantified by me, and no source I found publishes numbers. The practitioner quotations about `rerere` come from a Medium article I could not fetch directly (HTTP 403) and are reproduced from search-result excerpts, so they are weaker evidence than the git documentation quotes and should be treated as corroboration only. I did not investigate `git replace`, `git notes`, structure-aware merge tools such as `mergiraf`, or Copybara-style transform pipelines — those belong to [#366](https://github.com/launchpad-26/buzz/issues/366) and [#368](https://github.com/launchpad-26/buzz/issues/368).

## Sources

- [gitattributes(5)](https://git-scm.com/docs/gitattributes) — custom merge driver contract, `%O %A %B %L %P`, exit-status semantics, built-in `text`/`binary`/`union`, last-match-wins
- [git-rerere(1)](https://git-scm.com/docs/git-rerere) — three-way replay, conflict-marker detection caveat, `rerere.enabled`, `git rerere forget`
- [Patches in Electron](https://www.electronjs.org/docs/latest/development/patches) — patch re-application tooling and the break-without-conflict failure mode
- [How to use quilt to manage patches in Debian packages](https://raphaelhertzog.com/2012/08/08/how-to-use-quilt-to-manage-patches-in-debian-packages/) — fuzz and the refresh cycle
- [Fix conflicts only once with git rerere](https://medium.com/@porteneuve/fix-conflicts-only-once-with-git-rerere-7d116b2cec67) — practitioner limitations (quoted from search excerpts; direct fetch returned HTTP 403)
- [Git merge drivers — Graphite](https://graphite.com/guides/git-merge-driver) — driver definition and attribute mapping in practice

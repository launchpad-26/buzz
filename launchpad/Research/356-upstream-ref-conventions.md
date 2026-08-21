# Upstream's ref conventions, and whether `block/buzz` rewrites history

**Title:** What `block/buzz`'s branches and tags mean, and whether a vendor pin is safe against them
**Summary:** Establishes that `main` is upstream's only protected long-lived branch — there is no stable, LTS or `release` branch — and that upstream's tag and release machinery is organised around the **desktop** release train, not the relay. The relay gets a `relay-v*` tag roughly monthly with no GitHub Release and no changelog section. No evidence of history rewriting: five historical points spanning 2026-06-24 to 2026-08-17 are all still ancestors of `upstream/main`. Upstream also publishes a structured, machine-readable `CHANGELOG.md` with PR links and commit SHAs, which is a ready-made input for the drop report.
**Tags:** `upstream-sync` `vendor-branch` `tags` `releases` `changelog` `prd-273`
**Established:** 2026-08-22 · **Answers:** [#356](https://github.com/launchpad-26/buzz/issues/356) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**A vendor pin is safe against upstream's history, and badly served by upstream's tags.**

1. **No history rewriting observed.** Every historical point tested — including the current merge-base, the current `main` pin, and all three `relay-v*` tags going back to 2026-06-24 — is still an ancestor of `upstream/main`.
2. **`main` is the only protected long-lived branch.** Of 793 branches, exactly three are protected: `main` and two `mobile-release/0.4.x`. **There is no stable branch, no LTS branch, and no `release` branch** — which also means this fork's `ci.yml` trigger on `push: [main, release]` names a branch that exists in neither repository.
3. **The release machinery is a desktop release train.** 112 of the 116 GitHub Releases are desktop; `CHANGELOG.md` is versioned by desktop version (`## v0.5.18` ↔ tag `desktop-v0.5.18`) and has exactly two categories: "Desktop and shared changes" and "Other repository changes". **The relay has 3 tags in two months, no GitHub Release, and no changelog section of its own.**
4. **Upstream publishes structured release notes anyway**, and they are better than anything the fork would build: every entry carries a title, a PR link and a full commit SHA.

The practical consequence for [#305](https://github.com/launchpad-26/buzz/issues/305): **the only relay-specific signal upstream emits is the `relay-v*` tag**, and there have been three of them. Pinning to anything else means pinning to a statement about a product this fork does not ship — which is exactly what has already happened, since `main` currently sits on `mobile-v0.9.0-rc.1`.

---

## Evidence

### No history rewriting

```
$ for ref in f8692fa9b f53bbd1152464ecbb1de495e2d1d959e156138f0 68a0cc850 0d9be2fde 6e5c462ac; do
    git merge-base --is-ancestor $ref upstream/main && echo "ANCESTOR $ref $(git log -1 --format='%ad' --date=short $ref)"
  done
ANCESTOR  f8692fa9b  2026-08-17     # current merge-base with launchpad
ANCESTOR  f53bbd115  2026-08-06     # what launchpad-26/main is pinned to
ANCESTOR  68a0cc850  2026-06-24     # relay-v0.1.1
ANCESTOR  0d9be2fde  2026-07-10     # relay-v0.2.0
ANCESTOR  6e5c462ac  2026-08-08     # relay-v0.2.1
```

Five points across two months, all still reachable. If upstream had force-pushed `main` in that window, at least one would have been orphaned.

`main` is protected upstream, which is consistent:

```
$ gh api repos/block/buzz/branches --paginate --jq '.[] | select(.protected) | .name'
main
mobile-release/0.4.10
mobile-release/0.4.11
```

### Branch structure: one trunk, 790 topic branches

```
$ gh api repos/block/buzz/branches --paginate --jq '.[].name' | wc -l
     793
$ gh api repos/block/buzz --jq .default_branch
main
$ gh api repos/block/buzz/branches/release --jq '.name'
{"message":"Branch not found",...,"status":"404"}
```

The 793 are `main`, two `mobile-release/*`, and hundreds of feature and `agent-screenshots/*` branches. **There is nothing to pin to except `main` or a tag.**

### Tag namespaces

```
$ git tag -l | wc -l
     176
$ git tag -l | sed -E 's/[-_]?v?[0-9].*$//' | sort | uniq -c | sort -rn
 103 (bare semver, e.g. v0.5.2)
  29 mobile
  28 desktop  (16 "desktop-vX" + 12 "desktop/...")
   7 chart
   3 relay
   1 each: sprout-desktop-latest, sprout-agent-bundle-latest, sprig-latest,
           push-chart, canary, buzz-desktop-latest
```

The twelve most recent tags, by date:

```
2026-08-21 desktop-v0.5.18
2026-08-19 mobile-v0.13.0-rc.2
2026-08-19 mobile-v0.13.0-rc.1
2026-08-19 mobile-v0.12.0-rc.1
2026-08-18 desktop-v0.5.17
2026-08-17 desktop-v0.5.16
2026-08-17 desktop-v0.5.15
2026-08-14 desktop-v0.5.14
2026-08-14 desktop-v0.5.13
2026-08-14 desktop-v0.5.12
2026-08-14 mobile-v0.11.0-rc.2
2026-08-13 mobile-v0.11.0-rc.1
```

Not one relay tag in the last two weeks. The relay stream in full:

```
relay-v0.1.1  68a0cc850  2026-06-24
relay-v0.2.0  0d9be2fde  2026-07-10
relay-v0.2.1  6e5c462ac  2026-08-08
```

All three are lightweight tags on commits reachable from `main`.

### Releases are a desktop train

```
$ gh api repos/block/buzz/releases --paginate --jq '.[].tag_name' \
    | sed -E 's/[-/]?v?[0-9].*$//' | sort | uniq -c | sort -rn
 100 (bare semver)
  12 desktop
   1 each: sprout-desktop-latest, sprout-agent-bundle-latest, sprig-latest, buzz-desktop-latest
```

No release carries a `relay-` tag. Querying for one returns nothing:

```
$ gh api repos/block/buzz/releases --paginate \
    --jq '.[] | select(.tag_name|startswith("relay")) | .tag_name'
(no output)
```

### But there is a structured changelog

```
$ git show upstream/main:CHANGELOG.md | head -8
# Changelog

## v0.5.18

### Desktop and shared changes

- fix(desktop): simplify duplicate agent provenance ([#6401](https://github.com/block/buzz/pull/6401)) ([`aea0ef8df9fc24d9aa8bf5c761ab2910026a601b`](https://github.com/block/buzz/commit/aea0ef8df9fc24d9aa8bf5c761ab2910026a601b))
- fix(desktop): sender names in notifications + macOS click-through routing ([#6427](https://github.com/block/buzz/pull/6427)) ([`4e3c9e619c93dd26677b392ad1f8cf0d12c8f855`](https://github.com/block/buzz/commit/4e3c9e619c93dd26677b392ad1f8cf0d12c8f855))
```

Its structure is exactly two heading levels, repeated per desktop version:

```
$ git show upstream/main:CHANGELOG.md | grep -nE '^#{2,3} ' | head -9
3:## v0.5.18
5:### Desktop and shared changes
48:### Other repository changes
79:## v0.5.17
81:### Desktop and shared changes
88:### Other repository changes
94:## v0.5.16
...
```

Every entry has a conventional-commit prefix, a PR number and a commit SHA. `CHANGELOG.md` is in the current 796-file backlog, so it updates on essentially every drop.

### Upstream's tempo, for the record

```
$ git log --format='%ad' --date=short upstream/main --since=21.days | sort | uniq -c
   ...
  18 2026-08-17
  22 2026-08-18
  17 2026-08-19
  25 2026-08-20
  14 2026-08-21
```

Median ≈ 18 commits/day, ~125/week. The 67-commit backlog is roughly four days of upstream, not a lapse.

---

## What this means for #273

**#305 has a smaller menu than it thinks.** There is no stable branch to track. The choices are: a `relay-v*` tag (relay-specific but only ~monthly and with no notes), a `desktop-v*` tag (frequent but a statement about a different product), or a plain commit on `main` chosen by date or by review. The tag-noise finding in #305 was right and this sharpens it: the noise is not incidental, it is that **upstream's release machinery is not built for a relay consumer.**

**Pin criteria that would work, given these facts** — offered as input to #305, not as a choice:
- `relay-v*` gives a genuine upstream statement about the thing this fork ships, at the cost of pinning ~2 weeks stale on average and being unable to advance between tags.
- A commit on `main` chosen at drop time, recorded with its `CHANGELOG.md` version heading as the human-readable label, gives freedom of timing and a citable name. This is closest to what the vendor-branch requirement actually asks for.
- Whatever is chosen must be **at or after `launchpad`'s merge-base**, or `git diff main launchpad` keeps mixing upstream's own work into the picture — the live defect #305 already records.

**#306 gets a free input it was not counting on.** `CHANGELOG.md` is a curated, categorised, PR-linked and SHA-linked summary of upstream's own changes, updated every drop, written by the people who made them. A drop report that derives its narrative from `git diff` when upstream already publishes this is doing avoidable work — and doing it worse. The right shape is probably: take the changelog entries between the old pin and the new one, and annotate them with the fork's own tier and ledger information.

**One caveat on that, and it matters.** The changelog's categories are "Desktop and shared changes" and "Other repository changes". A relay change lands in either, with no relay category. So the changelog is a good *source* and a bad *organising principle* for this fork — the fork must re-sort it against its own operational tiers ([#355](https://github.com/launchpad-26/buzz/issues/355)), not adopt upstream's grouping.

**The `release` branch in `ci.yml` is dead.** `ci.yml` triggers on `push: [main, release]` and no `release` branch exists in `block/buzz` or `launchpad-26/buzz`. Harmless today, but it is a trigger nobody can rely on, and #299's analysis should not treat it as a live path.

---

## Confidence and limits

**High confidence** on branch and tag structure, the absence of relay releases, and the changelog's shape — all direct API and `git` output.

**Medium confidence on "no history rewriting", and the limit is important.** Five reachability probes across two months is evidence of stability, not proof of a policy. Upstream could rewrite tomorrow, and I could not see a rewrite that happened and was then restored. **I could not read upstream's branch protection settings** — `GET repos/block/buzz/branches/main/protection` returns 404 for this token, which needs push access on that repository — so I cannot confirm that force-pushes are actually disallowed on `main`, only that the branch is marked protected.

**Not checked.** I did not establish whether the `*-latest` and `canary` tags move. Their names imply mutability, and they currently point at commits from 2026-04-17, 2026-06-11 and 2026-07-20, which is consistent either with tags that moved and then went stale or with one-shot tags that were never moved. Observing movement needs two fetches separated by time, which I have not done — a pin should simply not use them either way. I did not read upstream's contributing or release documentation, only its refs and changelog; if upstream states a ref policy in prose somewhere, I have not seen it. I did not contact any upstream maintainer. I did not verify that the 103 bare-semver tags correspond to the desktop train rather than something else — the `CHANGELOG.md` heading/tag correspondence (`## v0.5.18` ↔ `desktop-v0.5.18`) is the basis for that reading and it is an inference.

**A correction I made mid-investigation, recorded so the method is auditable.** I first tested history stability by checking whether `de1c127fb^2` — the second parent of the previous sync's merge commit — was still an ancestor of `upstream/main`. It is not, and for a moment that looked like evidence of rewriting. It is not: `^2` is the *fork's* sync-branch head (`43366affa`, the file-size-ratchet commit), not upstream's tip. The valid test is the merge-base, which is an ancestor. Reported because a reader could easily repeat the same mistake.

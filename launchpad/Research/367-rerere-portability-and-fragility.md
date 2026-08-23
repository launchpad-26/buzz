# `rerere` tested: portability, fragility, and the actual silent hazard

**Title:** Five experiments on `git rerere` against the fork's real conflict
**Summary:** **The `rr-cache` is portable** — copied into a fresh clone it replays, so every remedy #300 considers is viable. Replay depends on the conflicted hunk, not physical line distance: drift inside the hunk changes the preimage and declines loudly, while drift outside it can still replay a stale resolution silently. A resolution recorded wrongly also reapplies silently. And a finding that matters for automation: **`rerere` never turns a conflicted merge into a clean one** — every replay still ends "Automatic merge failed".
**Tags:** `upstream-sync` `vendor-drop` `rerere` `adr-0021` `prd-273` `experiment`
**Established:** 2026-08-22 · **Answers:** [#367](https://github.com/launchpad-26/buzz/issues/367) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

**References are pinned.** The three revisions the experiments used are
fork [`5d76799d6e44f2f76aa7bd78c5343d339af98f63`](https://github.com/launchpad-26/buzz/tree/5d76799d6e44f2f76aa7bd78c5343d339af98f63),
upstream [`025425591ed67518a63870316f1473ffd02dd520`](https://github.com/block/buzz/tree/025425591ed67518a63870316f1473ffd02dd520),
and merge-base [`f8692fa9b52ddcfeb4b95fb4862109983509f131`](https://github.com/block/buzz/tree/f8692fa9b52ddcfeb4b95fb4862109983509f131).
Paths inside fenced blocks are command *output* and are left unlinked deliberately.

---

## Finding

Five experiments, all against the fork's real conflict in `lefthook.yml` ([fork](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/lefthook.yml) vs [upstream](https://github.com/block/buzz/blob/025425591ed67518a63870316f1473ffd02dd520/lefthook.yml)) — merge-base `f8692fa9b52ddcfeb4b95fb4862109983509f131`, `launchpad/launchpad` and `upstream/main` — in throwaway repositories.

| Experiment | Result |
|---|---|
| 1. Record a resolution, discard, re-merge in the same clone | **Replays** |
| 2. Fresh clone, empty cache | Conflicts, as expected |
| 3. **Copy `rr-cache` into that clone, retry** | **Replays — the cache is portable** |
| 4a. Upstream edits a line far from the hunk | **Replays** |
| 4b. Upstream edits a line ~5 lines away, but inside this conflict hunk | **Does not replay** — records a new preimage, leaves markers |
| 5. Record a *wrong* resolution, discard, re-merge | **Reapplies silently, no warning** |

Two of these change what the fork's records say.

---

## 1–3. Portability: the assumption holds

`rerere` recorded the resolution:

```
$ git config rerere.enabled true
$ git merge --no-commit theirs
Recorded preimage for 'lefthook.yml'
Automatic merge failed; fix conflicts and then commit the result.

# resolve by hand: take upstream, re-apply the fork's redirect line
$ git add lefthook.yml && git commit -m "merge upstream, resolved"
Recorded resolution for 'lefthook.yml'.

$ find .git/rr-cache -type f | sed 's|.*rr-cache/||'
e8ed5ba8467bd3f9adbcaaa9df6d6f4498bdcfbc/preimage
e8ed5ba8467bd3f9adbcaaa9df6d6f4498bdcfbc/postimage
```

Same clone, merge discarded and retried:

```
$ git reset --hard HEAD~1 && git merge --no-commit theirs
CONFLICT (content): Merge conflict in lefthook.yml
Resolved 'lefthook.yml' using previous resolution.
Automatic merge failed; fix conflicts and then commit the result.
--- fork position present without hand-resolution? 2
--- conflict markers left? 0
```

Fresh clone, empty cache — the baseline:

```
$ git clone repoA repoB && cd repoB && git config rerere.enabled true
$ ls .git/rr-cache | wc -l
0
$ git merge --no-commit theirs
Recorded preimage for 'lefthook.yml'
Automatic merge failed; fix conflicts and then commit the result.
--- markers present (no cache)? 1
```

**Now copy the cache across:**

```
$ mkdir -p .git/rr-cache && cp -R ../repoA/.git/rr-cache/. .git/rr-cache/
$ git merge --no-commit theirs
CONFLICT (content): Merge conflict in lefthook.yml
Resolved 'lefthook.yml' using previous resolution.
Automatic merge failed; fix conflicts and then commit the result.
--- fork position present? 2
--- markers left? 0
```

**The cache is portable.** Nothing in it is clone-local. So `actions/cache`, a dedicated branch, or any other transport works — [#300](https://github.com/launchpad-26/buzz/issues/300)'s options were all resting on this and it holds.

## 4. Fragility follows hunk membership, not line distance

**Far edit — upstream changes a comment near the top of the file, ~70 lines from the conflict:**

```
$ git commit -am "upstream: unrelated comment edit far from the hunk"
$ git merge --no-commit theirs
Resolved 'lefthook.yml' using previous resolution.
--- replayed? markers=0 forkpos=2
```

**Adjacent edit — upstream appends a trailing comment to `push-head-scope:`, about five lines from the conflicting lane:**

```
$ git commit -am "upstream: edit adjacent to the branch-skew lane"
$ git merge --no-commit theirs
Recorded preimage for 'lefthook.yml'
--- replayed? markers=1 forkpos=2
```

`Recorded preimage` rather than `Resolved … using previous resolution`: the match declined and git treated it as a new conflict.

This experiment establishes that changing content inside this conflicted hunk changes the preimage. It does **not** establish a distance threshold: a separate controlled review experiment replayed after an edit 45 lines away because that edit was outside the conflicted hunk. Git computes the reusable conflict from the hunk content, so physical distance is only an unreliable proxy for whether drift participates in the preimage.

**But note how it fails: markers in the file, merge stopped.** That is loud. Which brings us to the correction.

## 5. The actual silent hazard — and a correction to my own #362 answer

On [#362](https://github.com/launchpad-26/buzz/issues/362) I wrote that ADR-0021's stated mechanism was wrong and that a silent hazard was `rerere` "firing stale" when *upstream's intent changed underneath*. That mechanism **can** happen when the drift falls outside the conflicted hunk: the conflict preimage remains unchanged and the old resolution replays. Experiment 4b demonstrates only the narrower case where the edit changed this hunk and therefore caused the match to decline.

**The real silent hazard is human error persisting.** Recorded a deliberately wrong resolution — upstream wins, the fork's position dropped:

```
--- fork position after the wrong resolution: 0
$ git commit -m "merge (WRONGLY resolved)"

$ git reset --hard HEAD~1 && git merge --no-commit theirs
Resolved 'lefthook.yml' using previous resolution.
Automatic merge failed; fix conflicts and then commit the result.
--- fork position: 0        <- silently dropped again
--- conflict markers: 0
```

**The fork's position is dropped, the file looks clean, and the only message is the same benign `Resolved … using previous resolution.`** There is no warning, no marker, and nothing distinguishes this from a correct replay. That is what `git rerere forget` exists for, and it requires someone to already suspect the resolution is wrong.

**So the honest statement for the record:** `rerere` declines loudly when drift changes the conflicted hunk, but can replay silently when drift is outside that hunk. It also reapplies a resolution that was recorded wrongly the first time. A *shared* cache is therefore higher-stakes than a per-clone one: one stale or mistaken resolution can propagate to everyone and to CI.

## A finding for automation that nobody has stated

**`rerere` never turns a conflicted merge into a clean one.** Every single replay above still ended:

```
Automatic merge failed; fix conflicts and then commit the result.
```

The file content is resolved in the working tree; the merge remains stopped, and with `rerere.autoUpdate false` the path is not even staged. So an unattended pipeline still sees a non-zero exit and still stops. `rerere` saves a human's *typing*, not a human's *presence*.

That matters for success criterion 2 and for [#296](https://github.com/launchpad-26/buzz/issues/296): a drop whose only conflicts are `rerere`-replayable is **not** an unattended clean merge. It is a conflicted merge with the answers pre-filled.

---

## What this means for #273

*This section is my recommendation as the author, not a finding — including the `rerere.autoUpdate` position. The experiments above are the evidence; what should follow from them is my judgement and carries no source reference.*

**#300's central assumption is confirmed and its question narrows.** The cache is portable, so the decision is purely about transport and trust — and experiment 5 makes the trust half sharper than #300 currently frames it: a shared cache shares mistakes. A wrong resolution committed to a shared `rr-cache` branch is a wrong resolution applied silently on eleven machines and in CI.

**ADR-0021's `rerere` reasoning needs narrowing.** A replay that declines does so loudly, but upstream drift does not necessarily force a decline: only drift that changes the conflicted hunk changes the preimage. Drift outside it can leave a stale replay eligible. Recorded-wrong resolutions are a second silent hazard. The record's conclusion (`rerere` is a labour-saver, not a durability mechanism) remains right, but its mechanism should distinguish these cases.

**Do not enable `rerere.autoUpdate` for drop merges.** With `autoUpdate false` a replayed resolution sits unstaged, so `git status` shows it and a human has to look. With it true, a silently-wrong replay is staged and one `git commit` away from the branch. This is the one concrete configuration recommendation the experiments support, and I am stating it as input to #300 rather than deciding it.

**Hunk-sensitive fragility argues for caution on exactly the files the fork cares about most.** `lefthook.yml` is a file upstream rewrites; `runtime.rs` is a file upstream restructures. A stored resolution may decline if those edits change the hunk, or replay stale if intent changes elsewhere while the hunk remains stable. #294's mechanism column should account for both outcomes.

---

## Revised for the fork's horizon (#357)

Added after @tucktuck101 decided on 2026-08-22 that the fork has no expected lifetime beyond the
cohort project and nobody owns upstream adoption after it ends, with a hard end of 2026-09-17. That
decision names this document's fragility finding directly, so the revision belongs here rather than
in a reader's head.

**The evidence above is unchanged.** All five experiments stand exactly as recorded. What changes is
what should be done about them, and one of my recommendations reverses.

*The rest of this section is my recommendation as the author, not a finding.*

**My recommendation that `rerere` be kept away from `lefthook.yml` and `runtime.rs` was wrong under
the real horizon, and I withdraw it.** It rested on repeated upstream drift mattering — on
upstream drifting around a stored resolution over many drops. With at most a handful of drops left,
the preimage very likely never drifts. So the calculation inverts: record the four resolutions from
the current drop once, and replay them on the two or three remaining. `rerere` is now the *cheapest*
correct option for exactly the files I argued against, because the failure mode I was pricing does
not have time to arrive.

**The portability finding stays useful and its infrastructure does not.** The cache is portable, so
sharing works — but `actions/cache` wiring or a dedicated `rr-cache` branch is longevity spend. For
two or three drops resolved by one or two people, `cp -R` between clones is sufficient and
demonstrably correct. That narrows #300 considerably: the transport question is nearly moot, and what
survives is the trust question.

**Two recommendations are unaffected, because they are correctness points rather than durability
points.** Do not enable `rerere.autoUpdate` for drop merges — a silently-wrong replay that stages
itself is bad on drop one, not on drop fifty. And a shared cache still shares mistakes, which is why
the trust half of #300 is the half that survives.

**One consequence for how this is judged.** `rerere` never turns a conflicted merge into a clean one,
so it cannot deliver an unattended drop. Under a demonstrative target that is fine: the thing worth
showing is that a resolution recorded once replays correctly, which experiments 1–4 already show.

## Confidence and limits

**High for the recorded experiments; limited for generalisation.** Each recorded result has pasted output and used the real three versions of `lefthook.yml`. The broader rule about hunk membership also incorporates the reviewer's controlled counterexample, which refuted this note's original distance-based generalisation.

**Not verified.** I tested one file and one conflict shape. `rerere`'s documented behaviour with *multiple* conflicts in one file — where practitioner accounts say it becomes stricter and may re-ask for the whole set — was not tested, and the fork's `runtime.rs` conflict is the case that would exercise it. I did not test the `conflict-marker-size` interaction that `git-rerere(1)` warns about for files containing marker-like lines. The ~70-line replay and ~5-line decline do not define a distance window; I did not inspect the exact hunk boundaries in those runs or systematically vary edits inside and outside them. I did not test a cache shared through `actions/cache` or a git branch, only a direct filesystem copy — that is the mechanism those transports reduce to, but I have not run the transports themselves. I did not test whether a `postimage` recorded on one platform replays on another. Nothing here was run in CI. I did not run `just ci`; the only repository change is one markdown file.

## Sources

- [git-rerere(1)](https://git-scm.com/docs/git-rerere) — replay semantics, `rerere.enabled`, `git rerere forget`, the conflict-marker caveat
- [gitattributes(5)](https://git-scm.com/docs/gitattributes) — `conflict-marker-size`
- Experiments run in this session against `lefthook.yml` at merge-base `f8692fa9b`, `launchpad/launchpad` and `upstream/main`

# Mechanisms for expressing a standing position across merges

**Title:** The full candidate set, what each can and cannot express, and a correction to the "hybrid-by-scope is inexpressible" claim
**Summary:** Enumerates ten mechanisms and tests the two that matter. **Hybrid-by-scope is expressible in git** — demonstrated with three different per-path policies resolving in a single merge — and #304's recorded reason ("there is no per-path merge-base") is true of merge *bases* while being misleading about per-path *policy*, which `.gitattributes` expresses fully. Confirms from #362 that a transforming driver holds a sub-file position. Rules out four candidates with reasons rather than by silence, and draws the distinction the thread has been missing: **reducing conflict volume and expressing a durable position are different jobs, and structure-aware merge does only the first.**
**Tags:** `upstream-sync` `vendor-drop` `merge-driver` `rerere` `tooling` `prd-273` `adr-0021`
**Established:** 2026-08-22 · **Answers:** [#366](https://github.com/launchpad-26/buzz/issues/366) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

---

## Finding

**Ten candidates. Four can express a standing position, two reduce conflict volume without expressing anything, four cannot do the job at all.**

| Mechanism | Expresses a position? | Granularity | Bootstrap needed | Failure mode |
|---|---|---|---|---|
| **Trivial `ours` driver** (`driver = true`) | Yes | Whole file | git config | Discards all upstream work in that file, silently |
| **Transforming driver** | **Yes** | **Sub-file** | git config | Silent if it does not verify its own postcondition |
| **Per-path driver assignment** | **Yes — hybrid-by-scope** | Per path | git config | Last-match-wins surprises in `.gitattributes` |
| **Post-merge assertion** | Yes — detects, does not resolve | Arbitrary | None | Cannot fail silently |
| `rerere` replay | Partially | Hunk | git config + cache | Declines loudly; **fires stale silently** |
| Structure-aware merge (Mergiraf) | **No** — reduces noise only | Syntax node | git config + install | Not applicable to this problem |
| built-in `union` | No | Whole file | None | *"leave[s] the added lines … in random order"* |
| built-in `binary` | No | Whole file | None | Always conflicts |
| `git replace` / `git notes` | No | — | — | Wrong layer entirely |
| clean/smudge filters | No | — | — | Do not run during merge |

The two entries in bold that the #273 thread has not considered are the transforming driver (established in [#362](https://github.com/launchpad-26/buzz/issues/362)) and per-path assignment — which is the thing #304 recorded as impossible.

---

## Correction: hybrid-by-scope is expressible

[#304](https://github.com/launchpad-26/buzz/issues/304) records that hybrid-by-scope "turns out not to be expressible in git: there is no per-path merge-base."

**The merge-base half is true. The conclusion does not follow.** A per-path merge *base* — treating one path as though it merged from an older ancestor — is genuinely not a thing git offers. But per-path merge *policy* is exactly what `.gitattributes` is for, and it composes freely within one merge.

Demonstrated: three files, three different policies, one merge.

```
$ git config merge.keepours.driver   'true'         # leaves %A untouched -> ours wins
$ git config merge.keeptheirs.driver 'cp %B %A'     # theirs wins
$ cat .gitattributes
fileA.txt merge=keepours
fileB.txt merge=keeptheirs
                                                    # fileC.txt: no attribute -> default

$ git merge --no-commit theirs
Auto-merging fileB.txt
Auto-merging fileC.txt
CONFLICT (content): Merge conflict in fileC.txt
Automatic merge failed; fix conflicts and then commit the result.

--- results:
  fileA.txt    OURS-A          # ours won
  fileB.txt    THEIRS-B        # theirs won
  fileC.txt    <<<<<<< HEAD    # normal conflict

--- conflicted paths:
fileC.txt
```

Three policies, applied simultaneously, per path, in one merge. **So "the fork wins on process and deployment files, upstream wins on product code, and these three files always escalate" is directly expressible** — which is the shape [#294](https://github.com/launchpad-26/buzz/issues/294) is trying to record.

Two caveats worth carrying into #294 rather than discovering later:

- **Last match wins**, per `gitattributes(5)`: *"When more than one pattern matches the path, a later line overrides an earlier line."* A broad `crates/** merge=X` followed by a narrow exception works; the reverse silently does not.
- **One driver per file.** If a file needs two behaviours, that must be handled inside a single driver script.

## Confirmation: a transforming driver holds a sub-file position

Established in #362 and not repeated here in full: a driver is *"an arbitrary program"* receiving `%O`, `%A`, `%B` and writing `%A`, with exit status signalling conflict. Built one for the real `lefthook.yml` case — the fork's one-line divergence against upstream's 66-line rewrite. It merged cleanly, kept all of upstream's new lanes, preserved the fork's line, and **failed loudly** (`UU`, merge exit 1) when its anchor was removed.

That removes the standing counter-example. `lefthook.yml` is not a case no mechanism can hold.

---

## The distinction the thread is missing

**Reducing conflict volume and expressing a durable position are different jobs**, and conflating them is why the candidate set has looked shorter than it is.

**Mergiraf** is the clearest example. It is *"a syntax-aware git merge driver"* that *"relies on the tree-sitter incremental parsing library"*, matches syntax trees with GumTree, and — importantly for cost — *"starts by doing a regular line-based merge; if that succeeds, the program doesn't need to resort to the more expensive tree-based merging algorithm."* It is a drop-in driver for `git merge`, `rebase` and `cherry-pick`.

What it does: resolves conflicts that are textual artifacts rather than real disagreements — reordered imports, adjacent-but-independent edits, formatting churn.

**What it does not do: express any position at all.** It has no idea the fork wants `launchpad/scripts/check-branch-skew.sh`. It would reduce the *number* of conflicts the fork has to resolve and change nothing about which side wins any of them.

That makes it potentially valuable and entirely orthogonal. Worth noting for this fork specifically: three of its four current conflicts are in YAML, TOML-ish lockfile and Rust — all formats where structured merge plausibly helps — but `Cargo.lock` is generated and better handled by "take the higher version", and the `runtime.rs` conflict is code motion against an in-place edit, which is the case structured merge is *least* likely to resolve safely. So the expected benefit here is modest.

---

## Ruled out, with reasons

Recorded so the next person does not re-enumerate.

**`git replace`** — rewrites object lookups for the whole repository view. It can make a commit *appear* to have different content, which is a history-presentation tool, not a merge-policy tool. It also requires the replacement refs to be distributed to be effective, which has the same bootstrap problem as a driver with none of the benefit.

**`git notes`** — attaches metadata to objects. It could *record* a position (it is a plausible carrier for a ledger, in fact) but it has no effect on merge resolution whatsoever.

**clean/smudge filters** (`filter=` in `.gitattributes`) — the most tempting wrong answer, because they *do* transform file content per path. But they run on checkout and check-in, between the working tree and the index. **A merge operates on blobs, and the filter never sees it.** Using one here would make the working tree disagree with what is committed, which is worse than the problem.

**`git merge -X ours` / `-X theirs`** — whole-merge strategy options, not per-path. `-X ours` also does not mean "our file wins"; it means "prefer our side *in conflicting hunks*", which is a different and more dangerous thing than the trivial `ours` driver. Confusing the two is an easy way to silently lose upstream work.

**built-in `union`** — takes lines from both sides. Per `gitattributes(5)` it *"tends to leave the added lines in the resulting file in random order and the user should verify the result. Do not use this if you do not understand the implications."* No use for a position, though it is occasionally right for append-only lists.

---

## What this means for #273

**#304's reasoning should be corrected on this point, and its decision is unaffected.** Merge-based adoption is settled and nothing here bears on it. But "hybrid-by-scope is inexpressible" is the reason that option was rejected *as inexpressible*, and it is expressible — so if anyone revisits it, the ground has changed. The precise true statement is: *per-path merge policy is expressible; per-path merge base is not.*

**#294's mechanism column has four viable values**, and now with tested granularity: trivial `ours` driver (whole file), transforming driver (sub-file), post-merge assertion (arbitrary, detect-only), always-escalate. `rerere` is a fifth but as a labour-saver, not a position.

**The bootstrap problem is unchanged and now applies to more things.** Every driver — trivial, transforming, or Mergiraf — lives in git config, not in the repository. A `.gitattributes` line without the matching config is **inert and looks like it works**. That is [#300](https://github.com/launchpad-26/buzz/issues/300)'s question and this document does not answer it; it just raises the stakes, because four of the ten candidates depend on it.

**One recommendation-shaped observation, offered as input not decision.** Of the four position-expressing mechanisms, only the post-merge assertion has no bootstrap requirement and cannot fail silently. For a fork with eleven contributors on assorted machines and a CI runner that starts empty, that combination is worth more than it looks — and it is the one candidate nobody in the thread had named.

---

## Confidence and limits

**High** on the per-path demonstration and on the built-in semantics — the former is pasted output from a real merge, the latter verbatim from `gitattributes(5)`.

**High** on the transforming-driver result, carried from #362 where it was built and run against the real file.

**Medium on Mergiraf.** I read its documentation and coverage, **not its source, and I did not install or run it.** Its usefulness for this fork's actual conflicts is my judgement from the shape of those conflicts, not a measurement. If someone wants that answered properly, running it against the four real conflicts from [#360](https://github.com/launchpad-26/buzz/issues/360) is an afternoon's work and would settle it.

**Not verified.** The per-path demonstration used a synthetic three-file repository, not the real drop — it establishes that git supports the mechanism, not that the fork's specific 27-row policy set is conflict-free to express. I did not test the last-match-wins ordering trap, only quote the documentation for it. I did not test `git replace`, `git notes`, clean/smudge filters or `-X ours` — those are ruled out on documented behaviour and reasoning, which is weaker than testing, though for the filter case the reason (filters do not participate in merges) is structural rather than empirical. I did not investigate `jj`'s structured-merge work, Copybara, or any transform-pipeline approach — Copybara belongs to [#368](https://github.com/launchpad-26/buzz/issues/368). I did not test `rerere` at all; that is [#367](https://github.com/launchpad-26/buzz/issues/367). I did not run `just ci`; the only repository change is one markdown file.

## Sources

- [gitattributes(5)](https://git-scm.com/docs/gitattributes) — driver contract, `%O %A %B`, exit status, built-in `text`/`binary`/`union`, last-match-wins
- [git-rerere(1)](https://git-scm.com/docs/git-rerere) — replay semantics
- [Mergiraf](https://mergiraf.org/) and [Architecture](https://mergiraf.org/architecture.html) — tree-sitter parsing, GumTree matching, line-merge-first optimisation
- [Mergiraf: syntax-aware merging for Git — LWN](https://lwn.net/Articles/1042355/) — independent coverage
- [mergiraf/mergiraf — Codeberg](https://codeberg.org/mergiraf/mergiraf) — the project itself

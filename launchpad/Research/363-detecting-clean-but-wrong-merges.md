# Detecting a clean merge that is wrong, and how large that class is here

**Title:** The clean-merge-but-broken class — detection practice, and its size in this fork
**Summary:** The class is real, well-studied and **not automatically solvable**: the best published tool detects 32% of semantic conflicts, and its authors conclude "developers cannot rely solely on such semantic merge tools". Sizes the class here: **23 of the fork's 27 contested files are in-place edits and therefore coupled to upstream structure by construction**; 4 are not. One instance is demonstrated (#360's `relay_url`), one alleged instance is refuted (`bin/.lefthookrc`), and an anchor-survival test across 16 dependencies finds all currently intact — so no *additional* clean break is pending in this drop. Proposes the two cheap mechanical pre-flights that would have caught what was findable.
**Tags:** `upstream-sync` `vendor-drop` `semantic-conflict` `adr-0022` `prd-273` `detection`
**Established:** 2026-08-22 · **Answers:** [#363](https://github.com/launchpad-26/buzz/issues/363) · **Parent:** [#273](https://github.com/launchpad-26/buzz/issues/273)

**References are pinned.** Fork-side claims cite `launchpad-26/buzz` at
[`5d76799d6e44f2f76aa7bd78c5343d339af98f63`](https://github.com/launchpad-26/buzz/tree/5d76799d6e44f2f76aa7bd78c5343d339af98f63); upstream-side claims cite `block/buzz` at
[`025425591ed67518a63870316f1473ffd02dd520`](https://github.com/block/buzz/tree/025425591ed67518a63870316f1473ffd02dd520). Paths inside fenced blocks are command
*output* and are left unlinked deliberately.

---

## Finding

**Nobody has solved this, and the research says plainly that nobody is close.** The honest answer to "how do downstreams detect it" is: partially, with tests, at a recall the literature measures at roughly a third.

But the fork's specific situation is better than that sounds, for a reason worth stating up front: **most of what makes this class dangerous in the literature is invisible interference between two feature changes. This fork's version is narrower** — an upstream restructuring that invalidates a fork edit — and two of its three shapes are mechanically checkable.

| Shape | Detectable by | Instance here |
|---|---|---|
| Fork edit references something upstream deleted | **Compiler / build** | **Demonstrated** — #360's `relay_url` |
| Fork edit anchors on structure upstream renamed | **Anchor-survival grep** | None pending — 16 anchors tested, all intact |
| Fork edit still applies but no longer means what it did | Tests, at ~32% recall | Unknown, and unknowable cheaply |

The first two are cheap pre-flights the fork does not currently run. The third is the genuinely hard residue, and it is smaller than the class as a whole.

---

## How the class is detected: the state of the art

The research definition, from *Detecting Semantic Conflicts with Unit Tests*:

> "two contributions (sets of changes) to a base program semantically conflict—that is, interfere in an unplanned way—when the specifications they are individually supposed to satisfy are not jointly satisfied by the program that integrates them."

and the operational version:

> "semantic conflicts occur when textual merging succeeds and code compiles, yet the integrated changes exhibit undesired behavioral interference"

**The measured effectiveness is the important part.** Evaluating SAM — a tool that generates unit tests with four generators (EvoSuite, Differential EvoSuite, Randoop, Randoop Clean) and runs them against Base, Left, Right and Merge — across 85 change pairs from 51 merge scenarios:

- detected **9 of 28 conflicts** — recall **0.32**
- **3 false positives** in 57 non-conflict cases. The paper reports no overall precision for
  SAM — only per-tool, per-configuration values in its Table 2 (0.66 to 1.0) — so none is
  quoted here.
- 19 false negatives, of which manual analysis suggested 13 were theoretically reachable with better test generation

The authors' own conclusion:

> "developers cannot rely solely on such semantic merge tools for detecting conflicts"

**So the answer to "how do downstreams detect this" is: they mostly don't, and the ones who try catch about a third.** Anyone proposing a mechanism for #273 that claims to close this hole is overclaiming.

Practitioner sources agree from the other direction. Electron, which maintains one of the largest downstream patch sets in existence, states it as a fact of life rather than a solved problem: *"When upstream code changes, patches can break—sometimes without even a patch conflict or a compilation error."* And the literature notes the scale problem for exactly this shape of fork: *"For large upstream repositories like Chromium (of which Microsoft Edge is a downstream divergent fork), searching through thousands of upstream commits is tedious and error-prone."*

### What actually works, in descending order of cost-effectiveness

1. **Build the merge.** Catches the whole first shape. #360 found the `relay_url` defect this way, and `merge-tree` — which is what every figure in the #273 thread was derived from — could not have.
2. **Run the downstream's own tests.** This is the literature's technique without the automated generation: tests that encode *the fork's* invariants, not upstream's. The fork has one already in [`scripts/test-ci-changed-paths-filter.sh`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/scripts/test-ci-changed-paths-filter.sh) — a contract test for a fork divergence — which is exactly the right pattern.
3. **Assert the position survived.** Cheap, arbitrary, and cannot fail silently (see [#362](https://github.com/launchpad-26/buzz/issues/362)).
4. **Generated-test tooling.** ~32% recall, and the tools in the study are Java-only. Not applicable to a Rust/TypeScript/Dart codebase without substantial work, and not worth it at that recall.
5. **Staged or canary adoption.** Standard in distributions; requires somewhere to stage, which for this fork means the VPS, and is out of scope here.

---

## How large the class is in this fork

### Coupling is determined by the *form* of the divergence

A divergence that is **append-only or fenced** has no structural dependency on upstream — upstream can rewrite everything around it. An **in-place edit** depends by construction on the surrounding structure still being there and still meaning the same thing.

Classifying the 27 contested files by form:

| Form | Count | Files | Coupled? |
|---|---|---|---|
| Fenced append-only block | 1 | `AGENTS.md` | **No** |
| Whole-file replacement | 1 | `.github/ISSUE_TEMPLATE/config.yml` (upstream's was one line) | **No** |
| Deletion | 2 | the two legacy issue templates | **No** |
| **In-place edit** | **23** | everything else | **Yes, by construction** |

**So 23 of 27 are exposed to this class, and 4 are not.** That is not a probability estimate — it is a structural statement: an in-place edit *can* be invalidated by upstream restructuring, a fenced block cannot.

[`AGENTS.md`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/AGENTS.md) is the proof of the distinction and it is empirical, not theoretical: it is one of the 8 files both sides touched, and it **auto-merged cleanly in both of the fork's two drops** (#12 and #216), because the fork's change is a delimited append with `<!-- launchpad-26 fork: begin/end -->` markers. **This is the strongest available argument for [#307](https://github.com/launchpad-26/buzz/issues/307)'s fork-owned-override direction**, and it does not even require a separate file — a fence inside a shared file is enough.

### Anchor-survival test: nothing else is pending in this drop

For each in-place edit, checked whether the upstream structure it depends on still exists in `upstream/main`:

```
  lefthook.yml branch-skew lane                  anchor PRESENT (1)
  lefthook.yml upstream skew script              anchor PRESENT (1)
  Justfile SIDECARS array                        anchor PRESENT (3)
  Justfile _ensure-sidecar-stubs                 anchor PRESENT (10)
  ci.yml desktop paths-filter group              anchor PRESENT (3)
  ci.yml file-size step region                   anchor PRESENT (1)
  dev-setup.sh redis guard fn                    anchor PRESENT (2)
  instance-env.sh BUZZ_RELAY_PORT                anchor PRESENT (2)
  instance-env.sh vite invocation                anchor PRESENT (2)
  compose.yml BUZZ_IMAGE var                     anchor PRESENT (1)
  Dockerfile OCI source label                    anchor PRESENT (2)
  seed-local-community authority logic           anchor PRESENT (3)
  buzz-terminal lifecycle io import              anchor PRESENT (1)
  runtime.rs persona_drift_state                 anchor PRESENT (1)
  restore.rs spawn_agent_child call              anchor PRESENT (1)
  pack.rs inspect command                        anchor PRESENT (2)
```

All sixteen intact. **No anchor-disappearance break is pending in this drop.**

**But note carefully what this test does and does not catch.** #360's `relay_url` defect was *not* an anchor disappearance — the anchor (`spawn_agent_child(`) is present, as the table shows. What upstream deleted was a *local binding* used 28 lines away. Anchor survival is necessary and not sufficient, and saying otherwise would be exactly the kind of false assurance this document is about.

### The two instances on the record

**Demonstrated (#360): `relay_url`.** Upstream deleted a binding the fork's fix uses; git merged both hunks cleanly; the desktop crate failed to compile. And the resolution that compiles — upstream's own `&key.relay_url` — silently reintroduces the fork's bug, because `ManagedAgentRuntimeKey::new` normalises the URL. **That is the archetype: not merely clean-but-broken, but clean-but-broken with a plausible wrong fix.**

**Refuted (#360): `bin/.lefthookrc`.** ADR-0022 and #296 both carry this as the worked counter-example. It does not pin lefthook 2.1.3 — it resolves [`bin/lefthook`](https://github.com/launchpad-26/buzz/blob/5d76799d6e44f2f76aa7bd78c5343d339af98f63/bin/lefthook), which the fork points at 2.1.10, and upstream never touched the symlink. Tested in the merged tree: `LEFTHOOK_BIN` resolves and reports `2.1.10`. The mechanism is protective, not hazardous. Only the file's *comment* mentions 2.1.3.

**So the fork's risk register currently contains one item that is not real and omits the one that is.**

---

## What this means for #273

*This section is my recommendation as the author, not a finding. It carries no source reference because no source endorses it: the evidence is above, the judgement is mine.*

**ADR-0022's declared hole is real, and its size is 23 rows rather than 1 file.** That record says the scope ruling "does not solve that and should not be read as claiming it does" — correct, and now quantified. What changes is the *example*: `.lefthookrc` should be replaced with `relay_url`, which is worse in the way that matters (compiles, plausible wrong fix, no CI lane catches it).

**Two cheap pre-flights fall out, and neither needs a decision.** Both are mechanical, model-free, and would run in seconds on a drop:

- **Build the merge before proposing it.** This is the single highest-value change available and it is already how PR #216 was done by hand. The gap is that no automation does it and `merge-tree` is what the PRD's figures rest on.
- **Anchor-survival grep per ledger row.** Requires the ledger to record *what upstream structure each row depends on* — a column [#294](https://github.com/launchpad-26/buzz/issues/294) does not currently have, and the natural companion to the `Upstream-Status` column [#361](https://github.com/launchpad-26/buzz/issues/361) recommends.

**#296's boundary gets a defensible rule from the research rather than from taste.** Since detection tops out near a third even with dedicated tooling, "the agent may resolve it if a build passes" is not a safe boundary. The `relay_url` case is the proof: a build passes on the wrong resolution.

**And #307 has its empirical argument.** A fenced append inside a shared file survived two drops untouched while 23 in-place edits remain structurally exposed. That is the cheapest available reduction in this class's size, it costs nothing per drop, and it only governs divergences not yet created — which is why #361 flagged it as getting more expensive to adopt every week.

---

## Revised for the fork's horizon (#357)

Added after @tucktuck101 decided on 2026-08-22 that the fork ends with the cohort project on
2026-09-17, with no post-cohort maintainer. Two things in this document were sized against a future
that will not arrive.

**The evidence is unchanged.** The 32% recall figure, the 23-of-27 structural exposure, the
anchor-survival results and the two instances all stand.

*The rest of this section is my recommendation as the author, not a finding.*

**"23 of 27 rows are exposed" is still true and much less alarming.** It is a structural statement —
those rows *can* be invalidated by upstream restructuring. With at most a handful of drops left, and
with [#352](https://github.com/launchpad-26/buzz/issues/352) closed on the ground that the 19
never-conflicted files will very likely never collide, most of that exposure never gets tested. The
number to act on is not 23; it is the 8 files upstream has actually touched, of which 4 conflict.

**One of my two pre-flights survives and one becomes over-engineering.** *Build the merge before
proposing it* gets stronger: it is cheap, it caught the one real defect, and it is exactly the kind of
demonstrable check a demonstrative target wants. *An anchor-survival grep per ledger row* does not:
it asks #294 to carry a new column describing what upstream structure each row depends on, to guard
rows that will not be touched again. For four live files a person reading the drop covers it.

**#307's leverage largely collapses, and that is worth saying plainly.** Its argument — express
disagreement as a fenced append rather than an in-place edit — governs only divergences *not yet
created*. With weeks remaining, very few new divergences will be created, so the mechanism has almost
nothing left to govern. The `AGENTS.md` evidence stands as a demonstration that the pattern works; it
no longer supports "adopt this before it gets more expensive", because the compounding it was priced
against has run out. I flagged #307 as high-leverage in
[#361](https://github.com/launchpad-26/buzz/issues/361) on exactly that compounding argument, and I
withdraw that framing.

**What the class is still worth for.** Not risk management over time, but a worked example: the
`relay_url` defect is a concrete, reproducible instance of a clean merge that compiles and is wrong,
with a plausible wrong fix. That is evidence the cohort understood the failure mode, which is the
deliverable now.

## Confidence and limits

**High** on the research findings — figures and quotations are from the paper, and the authors' own conclusion is quoted rather than paraphrased. **High** on the anchor-survival results and the form-based classification: both are reproducible from the commands in this document and in #352.

**The form-based classification is a structural statement, not a risk estimate.** "23 of 27 are coupled" means 23 *can* be invalidated by upstream restructuring. It does not say how likely that is, and I have no basis for estimating it — nothing in the literature I found gives a per-import rate, and this fork has two drops of history, which is not a sample.

**Not verified.** The anchor patterns are my own choice of what each edit depends on; a different reading would pick different anchors and could reach a different count. I checked 16 dependencies, not one per in-place edit for all 23 — the remaining ones are the ADR-0005 deployment files and the templates, where the coupling is to values rather than structure. **I did not attempt to detect any third-shape conflict** — an edit that still applies but no longer means what it did — because the literature says the available techniques catch about a third and none of them apply to this codebase without substantial work; that residue remains unmeasured and unmeasurable at this cost. I did not run the fork's test suites at all (disk exhaustion, see #360), so my own second-shape detection was compilation only. I did not read the second and third papers the search surfaced, only the one quoted. I did not investigate structure-aware merge tools or staged-adoption tooling — #366 and #368.

## Sources

- [Detecting Semantic Conflicts with Unit Tests](https://arxiv.org/html/2310.02395) — the definition, the SAM tool, recall 0.32 (9 of 28 detected), 3 false positives in 57 non-conflict cases, and the authors' conclusion
- [Detecting semantic conflicts with unit tests — ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0164121224001158) — journal version of the same work
- [Patches in Electron](https://www.electronjs.org/docs/latest/development/patches) — *"patches can break—sometimes without even a patch conflict or a compilation error"*
- [Using Pre-trained Language Models to Resolve Textual and Semantic Merge Conflicts](https://www.microsoft.com/en-us/research/wp-content/uploads/2022/07/issta22-merge-conflicts-llm.pdf) — the Chromium/Edge downstream-fork framing

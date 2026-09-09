# Temporal and revision coherence

| Metadata | Value |
|---|---|
| Topic number | 03 |
| Exact research question | How do agents combine evidence from incompatible commits, branches, releases, dependencies, or time periods, and how should generated documentation remain coherent as the underlying system changes? |
| Primary model | Claude |
| Research date | 2026-09-08 |
| Scope | Agent-authored technical documentation generated from repository evidence (source, configuration, tests, command output, history, issues) in git-hosted projects. Local evidence is `launchpad-26/buzz` at HEAD `4bac39fe512c9b289992951de1222abd61d5790c`, branch `topic-03-temporal-coherence`, inspected 2026-09-08. External evidence covers empirical software-engineering studies of documentation staleness, LLM knowledge-cutoff and knowledge-conflict research, and primary tool and style-guide documentation. Excludes the topics assigned to other reports (see Exclusions) and excludes non-git version-control systems, binary artifact registries, and documentation genres with no repository referent. |
| Evidence limitations | The single-repository local sample is deep but not representative: its two staleness checkers are unusually explicit about their own limits, so it over-represents good practice rather than typical practice. No experiment was run in which an agent authored documentation across deliberately mixed revisions; the mechanism claims about agent behaviour rest on external studies of code completion and knowledge conflict plus mechanically verified properties of the tools agents use, not on direct observation of documentation agents. One local claim (ADR-0004's own reproduction commits) could not be verified because the commits are unreachable in this checkout. Quantitative external figures come from pre-agent-era corpora (2003-2022) and describe human-maintained documentation; they bound the ambient problem, not the agent-specific increment. |

## Executive answer

Agents combine evidence from incompatible revisions because **nothing in an
ordinary agent's evidence pipeline carries a revision, and the three places
evidence comes from are pinned to three different times.** The model's own prior
is fixed at a training cutoff that is itself non-uniform and not reliably the one
published ([Cheng et al. 2024](https://arxiv.org/abs/2403.12958)); the working
tree the agent greps is a mutable, possibly partial materialisation of one
commit; and the history, issues, and command output it reads describe other
commits entirely. Text retrieved from any of these arrives as undated prose. The
agent then does what models demonstrably do with conflicting context: it follows
the version signal present in the surrounding text and its parametric prior,
rather than any explicit revision. The sharpest external measurement of this is
[Wang et al., ICSE 2025](https://arxiv.org/abs/2406.09834): across seven LLMs,
145 API mappings and 28,125 prompts, deprecated-API usage ran 25-38% overall,
but **70-90% when the surrounding context was written against the old API and
9-18% when it was written against the new one** — the same models, the same
libraries, the outcome decided by which revision the visible context came from.

Three findings from this repository sharpen what "incompatible" means in a git
context, and all three are mechanically verified below:

1. **Wall-clock order and reachability order diverge, and the divergence is
   large.** Commit `24ec6a468` (authored 2026-08-20) is *not* an ancestor of the
   revision `338b4d0cf` (2026-08-28) that 108 corpus citations of
   `crates/buzz-relay/src/main.rs` are pinned to, yet it is an ancestor of HEAD.
   It became reachable through merge `d555ec95f`
   (2026-08-31), which brought 204 upstream commits authored 2026-08-17 to
   2026-08-29 and changed 1,855 files in one event. An agent reasoning "this
   change is dated before my pin, so my pin already covers it" is wrong in this
   repository today, by eight days.
2. **A pinned revision decays fast enough to saturate its own signal.** Running
   this repository's own `stale.py` at HEAD on 2026-09-08 returned **350 nodes:
   304 stale, 18 fresh, 28 unestablished** — 86.9% stale for a corpus whose
   newest pin is six days old and whose oldest is thirteen.
3. **The checkout is not the revision.** This worktree has 6,287 files tracked at
   HEAD and 5,675 of them (90.3%) marked skip-worktree by sparse-checkout. An
   agent that searches the filesystem sees 612 files and would report the other
   5,675 as absent; they are present at HEAD and readable with `git show`.

On the second half of the question — how generated documentation should stay
coherent — the supported answer is narrower than the pipeline of mitigations
usually implies. **Recording a revision per claim is cheap, mechanically
checkable, and the precondition for everything else**, and this repository shows
two independent implementations of it. But mechanical checking establishes
*movement, not meaning*: both local checkers say so in their own words, and both
are right to. A `fresh` verdict does not mean a claim still holds, a `stale`
verdict does not mean it fails, and the classes of evidence that cannot be
checked at all are not marginal — 642 of 1,168 unestablished citations in the run
above name no openable file. Prompting the agent to use the current version is
the weakest of the available controls: in Wang et al.'s own evaluation the
prompt-level fix (INSERTPROMPT) "does not currently achieve sufficient
effectiveness", while the decoding-level constraint (REPLACEAPI) achieved fix
rates exceeding 85%.

The material qualification on all of the above: staleness is not uniformly
costly, and treating it as such produces the wrong mitigation. Lethbridge,
Singer and Forward found that 81% of surveyed engineers agreed (53% somewhat,
28% strongly, n=45) that "Software documentation can be useful, even though it
might not always be the most up-to-date", because "the high-level abstractions
tend to remain useful when the details become outdated"
([IEEE Software, Nov 2003](https://courses.cs.duke.edu/fall11/cps196.1/classwork/Lethbridge-Singer-Forward-2003.pdf)).
The design consequence is not "pin harder" but **write claims at the abstraction
level whose decay rate you can afford, and pin the ones that are genuinely
revision-bound** — which is exactly what a `path:line` citation is and an
architectural statement is not.

## Question, scope, and method

### Subquestions

- What distinct forms does revision incoherence take in agent-authored
  documentation, and which are specific to agents rather than inherited from
  human documentation practice?
- Through which concrete mechanisms does evidence from incompatible revisions
  reach an agent's context without a revision label attached?
- What does git's own model make easy to get wrong — ranges, ancestry,
  reachability, merges, reverts, partial checkouts?
- How does an agent resolve a conflict once incompatible evidence is in context,
  and what predicts which side wins?
- What can mechanical detection establish about revision coherence, and what
  can it provably not establish?
- Which mitigations have supporting evidence, at what cost, and under what
  boundary conditions do they fail or become counterproductive?
- Where is staleness not a defect?

### Exclusions

- The general question of whether the evidence assembled was sufficient (topic
  01) and of tool-mediated evidence failure such as truncation and ignored
  command errors (topic 02). Revision-bound instances of both are in scope here
  only where the revision is the thing that fails.
- Fabricated citations as such (topic 05) and circular provenance (topic 05,
  15). This report covers citations that were true at a revision and are no
  longer, not citations that were never true.
- Freshness signalling, change-impact triage and staleness policy as a
  documentation-quality property (covered by the sibling `documentation-corpus-review`
  report 07). This report treats staleness only as it bears on agents combining
  incompatible revisions.
- Detection tooling design in general (topic 19). Detection appears here only
  with respect to revision coherence and its limits.
- Non-git version control, and documentation with no repository referent.
- Any synthesis across the 20-topic program.

### Evidence and source plan

Local inspection covered: the two independent revision-pinning and
staleness-checking implementations in this repository
(`launchpad/project-intelligence/corpus/stale.py` and
`launchpad/skills/review-queue-automation/gap/validate.py`), their governing
methodology and decision records, the pinned-revision front matter of 374
Markdown files under `launchpad/docs/corpus/`, and the commit history of the
merges that invalidated them. Every mutable local claim below records the
command, the revision, and the date. Because this worktree is sparse, several
files were read with `git show HEAD:<path>` rather than from the filesystem;
that is stated where it applies, and is itself one of the report's findings.

External sources were prioritised as: primary tool and specification
documentation (git's `gitrevisions`, `actions/checkout`), peer-reviewed or
archival empirical studies with published methods and figures, and primary style
guidance from documentation-producing organisations. Secondary summaries were
used only to locate primary material; where a figure is reported through an
intermediary it is labelled as such and not counted as independent
confirmation.

Triangulation ran in both directions. External study findings were checked
against mechanically reproducible behaviour in this repository (the deprecated-API
context effect against the observed pin/merge divergence; the outdated-reference
survival data against this corpus's measured stale rate), and local documented
rationale was checked against the primary specification and against direct
experiment — which is how the counterevidence in "Detection and validation"
below was found. Counterevidence was sought specifically for the premise that
staleness is harmful and for the premise that pinning is the right control;
both searches returned material that is reported.

Stopping condition: reached on coverage and saturation. Every subquestion has a
supported answer or a stated gap; additional searching on API evolution
benchmarks, temporal-misalignment benchmarks, and comment-code inconsistency
detection returned further instances of the same mechanisms rather than new
failure classes, mitigations, or changes in confidence.

## Failure taxonomy

| Failure class | Description | Evidence and boundary conditions |
|---|---|---|
| **Prior-versus-repository conflict** | The agent's parametric knowledge of a dependency, API, or convention is fixed at a training cutoff and contradicts the revision in front of it. | Measured: deprecated-API usage rates of 25-38% across seven LLMs, 145 API mappings, eight libraries, 28,125 prompts ([Wang et al., ICSE 2025](https://arxiv.org/abs/2406.09834), §RQ1). Boundary: the cutoff is not a single date — effective cutoffs "often drastically differ from reported cutoffs" and vary by sub-resource ([Cheng et al. 2024](https://arxiv.org/abs/2403.12958)), so "the model knows up to date D" is not a usable premise. |
| **Context-version capture** | The agent adopts whichever revision the surrounding retrieved text was written against, regardless of the target revision. | Measured and large: DUR 70-90% for prompts drawn from outdated functions versus 9-18% for up-to-date ones, same models and libraries ([Wang et al. 2025](https://arxiv.org/abs/2406.09834), Summary 5). Interpretation: this makes context assembly, not model choice, the dominant control. |
| **Reachability/date confusion** | The agent treats commit timestamps as an ordering over what its pinned revision includes. | Verified locally: `24ec6a468` (authored 2026-08-20) is not an ancestor of pin `338b4d0cf` (2026-08-28) but is an ancestor of HEAD; `git merge-base --is-ancestor 24ec6a468 338b4d0cf` exits 1. Boundary: only arises in merge-based histories; a strictly linear, rebase-only history collapses the two orders. |
| **Merge-import invalidation** | Evidence changes wholesale not because anyone edited it, but because a merge made a different branch's version of it reachable. | Verified locally: merge `d555ec95f` (2026-08-31, "chore: sync launchpad with upstream block/buzz main (204 commits)") changed 1,855 files, 182 of them under `crates/`. The four commits that moved `crates/buzz-relay/src/main.rs` past the corpus pins are authored by upstream contributors and carry upstream PR numbers (#6251, #6729, #3777, #6269). |
| **Checkout-shape divergence** | The filesystem the agent searches is not the revision it thinks it is reading: sparse checkout, shallow clone, uninitialised submodules, LFS pointers, uncommitted work. | Verified locally: 6,287 files tracked at HEAD, 5,675 skip-worktree (`git ls-files -t \| grep -c '^S'`), so `launchpad/skills/review-queue-automation/gap/validate.py` is absent from the filesystem and present at HEAD. Corroborated for CI: `actions/checkout` defaults `fetch-depth: 1`, "Only a single commit is fetched by default" ([README](https://github.com/actions/checkout)) — which is why `stale.py` predicts it "will report almost every node `unestablished` under CI's depth-1 checkout". |
| **Cross-artifact release skew** | Documentation mixes a manifest version, a lockfile version, a released artifact, and a running deployment, which are four different revisions of "the system". | Local instance: this fork deploys its own build under five named files that deliberately diverge from upstream (`launchpad/AGENTS.md` §3, ADR-0005), so "what the relay does" has a fork answer and an upstream answer at the same moment. Gap: not separately quantified here. |
| **Pin decay to saturation** | Per-claim pins are recorded correctly, then age until nearly every claim is flagged and the flag stops discriminating. | Measured locally: 304 of 350 nodes stale after 6-13 days (`stale.py`, run 2026-09-08 at HEAD `4bac39fe5`). Interpretation: at 86.9% the verdict no longer ranks anything; the same run is more useful read per-citation than per-node. |
| **Unpinnable evidence** | A material share of citations name nothing a revision-scoped check can resolve. | Measured locally: of 1,168 unestablished citations, 642 are "graph-edge or tool-result" citations naming no openable file, 205 are URLs the checker does not verify, 12 are commit references, and 309 name a path that did not exist at the recorded revision. |
| **False staleness from history-shaped checks** | A check that asks "which commit last touched this file" fires on reverts, merges that reintroduce identical bytes, and mode changes. | Verified locally, with a documented incident: commit `3bbbd8367` records "three rows citing SKILL.md failed while every cited line still pointed exactly where it did", and `git rev-parse` confirms the pin blob and the HEAD blob of `SKILL.md` are the identical object `1fac6a6f8`. Independently corroborated: Tan et al. report seven negative timestamp differences in `babel/babel` "caused by reverting README.md to an earlier version" ([2212.01479](https://arxiv.org/abs/2212.01479), footnote 19). |
| **Time-anchored prose** | Text that says "currently", "new", "now", or "the latest version" cannot be evaluated against any revision at all. | Primary guidance: Google's style guide names exactly these words as anchoring documentation to a point in time and prescribes "a reference point such as a date or version release number" ([developers.google.com/style/timeless-documentation](https://developers.google.com/style/timeless-documentation)). Boundary: the same guide exempts release notes, blog posts and other time-stamped genres. |

## Causes and mechanisms

### The pipeline has three clocks and one output format

**Sourced.** An agent authoring from a repository draws on (a) parametric
knowledge fixed at training, (b) a working tree, and (c) tool output about
history, issues, dependencies and command results. Cheng et al. establish that
(a) is not a single date and not reliably the published one, attributing this to
old data in new CommonCrawl dumps and to deduplication behaviour
([2403.12958](https://arxiv.org/abs/2403.12958)). Xu et al.'s survey names the
resulting collision precisely: *context-memory conflict*, whose two main causes
they give as "temporal misalignment" and misinformation, and *inter-context
conflict*, whose causes include the case where "retrieved documents may contain
updated and outdated information ... simultaneously"
([2403.08319](https://arxiv.org/abs/2403.08319), §2-3).

**Interpretation.** The failure is not that three clocks exist; it is that the
output of all three arrives in context as undifferentiated prose. A file read
returns bytes, not `<path>@<commit>`. A `git log` excerpt describes commits that
may or may not be ancestors of the tree just read. An issue thread describes
intent at the time it was written. Nothing in the transcript records which of
these a given sentence came from, so by the time the agent is composing, the
revision information required to detect the conflict has already been discarded.

### Which side wins is decided by the context, not by the agent's judgement

**Sourced.** Wang et al.'s RQ2 is the cleanest measurement available: holding
model and library fixed, deprecated-API usage was 70-90% when the completion
prompt came from a function still written against the old API and 9-18% when it
came from an updated one, which they attribute to "contextual characteristics of
the prompts, such as specific variables and function calls"
([2406.09834](https://arxiv.org/abs/2406.09834), §V-B). The knowledge-conflict
literature reports the same directionality from the other side: models exhibit
"a significant bias to evidence that aligns with the model's parametric memory",
favour evidence "that appears most frequently within the context", and show
"significant sensitivity to the order in which data is introduced"
([Xu et al. 2024](https://arxiv.org/abs/2403.08319), §3.2, summarising Chen et
al. 2022, Xie et al. 2023, Jin et al. 2024).

**Interpretation.** Applied to documentation, this predicts that an agent given
one paragraph of current code and five paragraphs of older design notes will
write the older system, fluently, with no signal that a conflict was resolved.
It also predicts that the effective control is upstream of generation: what goes
into context, in what proportion, and in what order.

### Git's own model supplies the two traps

**Sourced and verified.** First, **reachability is not chronology**. Ranges are
defined by reachability: `r1..r2` means "commits that are reachable from r2
excluding those that are reachable from r1"
([gitrevisions](https://git-scm.com/docs/gitrevisions)). In a merge-based
history a commit authored earlier can therefore be outside a later pin's
ancestry. Verified in this repository on 2026-09-08:

```
$ git merge-base --is-ancestor 24ec6a468 338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5; echo $?
1
$ git log -1 --format='%as %h %s' 24ec6a468
2026-08-20 24ec6a468 Repair stale large channel roster snapshots (#6251)
$ git log -1 --format='%cs %h %s' d555ec95f
2026-08-31 d555ec95f chore: sync launchpad with upstream block/buzz main (204 commits)
```

Second, **the working tree is not the revision**. Verified in this worktree:

```
$ git ls-tree -r HEAD --name-only | wc -l
6287
$ git ls-files -t | grep -c '^S'
5675
$ test -e launchpad/skills/review-queue-automation/gap/validate.py || echo absent
absent
$ git cat-file -e HEAD:launchpad/skills/review-queue-automation/gap/validate.py && echo present-at-HEAD
present-at-HEAD
```

**Interpretation.** These two traps explain most of the local incidents without
appealing to model behaviour at all. An agent that searched this worktree with
`find` or `grep` and reported "there is no staleness checker under
`launchpad/skills/`" would be making a true statement about the filesystem and a
false statement about the revision — and, critically, would have no error to
notice, because the search succeeded.

### Merges relocate evidence without editing it

**Verified.** The corpus nodes pinned at `338b4d0cf` and `a44cf52fc` cite
`crates/buzz-relay/src/main.rs`. Four commits moved that file past those pins;
all four are upstream work (authors Tom Brow, Will Pfleger, Jordan Mecom, Wes;
PR numbers #6269, #3777, #6729, #6251), and none of them was made in this fork.
They entered this branch's ancestry through merge `d555ec95f`, which brought 204
commits authored between 2026-08-17 and 2026-08-29 and changed 1,855 files.

**Interpretation.** For a fork or any repository that integrates from upstream,
the unit of documentation invalidation is not the commit but the sync. This is
also the case that most cleanly defeats date-based reasoning, because the
invalidating commits are older than the pins they invalidate.

## Detection and validation

### What the two local implementations do, and what they explicitly refuse to claim

**Sourced.** `launchpad/project-intelligence/corpus/stale.py` resolves each
node's recorded revision, then for each file-naming citation asks whether the
path changed between that revision and HEAD, reporting `stale`, `fresh` or
`unestablished` — and states in its own module docstring that it reports
"movement, never 'the node is wrong'", that "a `fresh` verdict does not mean any
claim in the node still holds", and that "a whitespace commit flags a node
exactly as a rewrite does".

`launchpad/skills/review-queue-automation/gap/validate.py` runs the same idea at
citation granularity for a fit/gap analysis pinned to a single revision
(`eb1cedb19`, per `gap/methodology.md`), where "a citation means 'line N of that
file at `eb1cedb19`'" and each register row carries its own `revision` cell that
"records when this row was last *evaluated*, not when the register file was last
touched".

**Measured.** Running `stale.py` at HEAD `4bac39fe5` on 2026-09-08:

```
$ python3 launchpad/project-intelligence/corpus/stale.py
...
SUMMARY  350 node(s): 304 stale, 18 fresh, 28 unestablished
```

2,803 stale citation lines and 1,168 unestablished ones. The most-cited moved
files are `launchpad/docs/corpus/AGENTS.md` (179), the checker's own sibling
`launchpad/project-intelligence/corpus/validate.py` (148),
`crates/buzz-relay/src/main.rs` (142), `crates/buzz-relay/src/handlers/ingest.rs`
(129) and `crates/buzz-relay/src/config.rs` (105).

### What mechanical checking cannot establish

1. **Truth.** Both tools disclaim it, and the disclaimer is not modesty: the
   claim "handler X validates the `h` tag" can be falsified by a change to a
   *caller* that the citation never named. No file-citation check detects that.
2. **Coverage of the evidence base.** 642 of 1,168 unestablished citations name
   no openable file. A corpus can be 100% `fresh` on its checkable citations
   while the majority of its support is unverifiable in principle.
3. **Anything at all under a shallow checkout.** With `actions/checkout`'s
   default `fetch-depth: 1`, the recorded revision is not in the object store
   and the check fails closed to `unestablished` for every node — a wall of
   `unestablished` that reads like corpus-wide rot and is a fetch configuration.
4. **The difference between a real edit and a round trip.** History-shaped
   checks fire on reverts and identical-content merges. Local incident chain,
   verified: merge work put `SKILL.md` ahead of the pin; commit `c835cdc62`
   reverted the four-line edit to restore the pinned bytes; the check *still*
   failed, because `last_touch_commit` was now the revert itself; commit
   `3bbbd8367` replaced the ancestry test with a blob-identity test. Confirmed
   at HEAD: `git rev-parse eb1cedb19...:SKILL.md` and `git rev-parse
   HEAD:SKILL.md` both return `1fac6a6f896a30a4cd3a637c49858a2459915c3d`, while
   `git log -1 --format=%h -- <path>` returns `c835cdc62`.

### Counterevidence found inside the local rationale

**This one cuts against a local document, and it is reported because the
contract requires counterevidence to be sought rather than avoided.**
`stale.py`'s ancestor gate is justified, in both the module docstring and
[ADR-0004](../../../decisions/ADR-0004-handbook-staleness-detection-mechanism.md),
by the claim that "`git log A..B` returns **empty and exits 0** when `A` is not
an ancestor of `B`". As a general statement this is **false**, and the
specification says why: `r1..r2` is "commits that are reachable from r2
excluding those that are reachable from r1"
([gitrevisions](https://git-scm.com/docs/gitrevisions)), so the range is empty
exactly when `r2` is reachable from `r1` — which covers the case where the
recorded revision is a *descendant* of HEAD, and does not cover the divergent
case. Direct experiment in a throwaway repository on 2026-09-08:

```
# A on a divergent branch, B = HEAD
$ git log --oneline $A..$B
8580626 mainedit                 # NOT empty
$ git merge-base --is-ancestor $A $B; echo $?
1
# C a descendant of B
$ git log --oneline $C..$B       # empty, exit 0
$ echo $?
0
```

The gate itself is correct and conservative — it fails closed in both cases, so
no verdict is wrong — but the stated reason is not, and it has been carried
forward verbatim from ADR-0004 into `stale.py`'s docstring without re-derivation.
ADR-0004's own reproduction (`git log c060e936c..32f0988c8`) could not be checked
here: neither commit is reachable in this checkout (`git cat-file -e` fails for
both), which is consistent with an unfetched or deleted branch and is **not**
evidence that the reproduction was wrong. This is a worked instance of the
report's own subject — a temporally-bound rationale, true or false of one
history, copied forward as timeless prose.

## Mitigations

**Ordered by strength of supporting evidence, with the boundary condition that
limits each.**

1. **Constrain generation mechanically rather than by instruction.** Wang et
   al. built both: REPLACEAPI intervenes in decoding and "achiev[es] fix rates
   exceeding 85% with acceptable accuracy"; INSERTPROMPT adds a prompt telling
   the model to use the replacement and "does not currently achieve sufficient
   effectiveness and accuracy"
   ([2406.09834](https://arxiv.org/abs/2406.09834), §I, §RQ4). *Interpretation
   for documentation:* the documentation analogue of REPLACEAPI is a validator
   that rejects a claim whose citation does not resolve at the recorded
   revision, not a system prompt asking the agent to check versions. *Boundary:*
   their intervention needs a known correct target (an API mapping). Prose
   claims have no such mapping, so this transfers to citation form, not to claim
   content.
2. **Record a revision per claim, not per document.** Both local
   implementations do this, and the reason the register's design gives is the
   operative one: the cell "records when this row was last *evaluated*, not when
   the register file was last touched ... A row still reading an older SHA than
   its siblings is a row nobody has re-checked". *Boundary:* it is only as good
   as the discipline that bumps it exclusively on re-reading, which no check can
   enforce; and it decays — 86.9% stale here after under two weeks.
3. **Compare content, not history.** The blob-identity test is strictly more
   accurate than the last-touch test for the question "did the cited lines
   move", and commit `3bbbd8367` states the reason and the limit together:
   "identical blobs prove no line moved, and any real edit changes the blob, so
   this narrows nothing that matters. It is an accuracy fix, not a relaxation --
   do not extend it to 'close enough' comparisons such as line counts or
   timestamps." *Boundary:* file-level identity still over-fires (any edit
   anywhere in the file flags every citation into it) and under-detects
   semantic change elsewhere.
4. **Fail closed on every unverifiable precondition.** The four gates in
   `stale.py` — commit exists, commit is an ancestor of head, path existed at the
   recorded revision, path is repository-contained — exist because a check that
   can quietly pass is worse than none. *Boundary:* fail-closed converts a silent
   false negative into a loud false positive, which is the right trade only while
   someone still reads the output; at 1,168 unestablished lines that assumption
   is doing work.
5. **Separate detection from triage.** Both tools report movement and refuse to
   report wrongness. *Interpretation:* this is what keeps the check cheap and
   trustworthy, and it is also what makes the check insufficient on its own —
   the human or agent re-read is not optional, it is the second half of the
   mechanism.
6. **Write revision-independent claims at a revision-independent altitude.**
   Google's timeless-documentation guidance bans "currently / new / now /
   latest" and asks for "a reference point such as a date or version release
   number" instead
   ([Google developer style guide](https://developers.google.com/style/timeless-documentation)).
   Lethbridge et al. supply the reason this works: "the high-level abstractions
   tend to remain useful when the details become outdated". *Boundary:* the same
   Google page exempts release notes and other time-stamped genres, and altitude
   is not free — a document that says only what stays true may say nothing a
   reader can act on.
7. **Version the documentation set only when the product is genuinely
   multi-version.** Docusaurus, a primary implementation of documentation
   versioning, warns against it in its own manual: "Most of the time, you don't
   need versioning as it will just increase your build time, and introduce
   complexity to your codebase", and "Try to keep the number of your versions
   below 10"
   ([docusaurus.io/docs/versioning](https://docusaurus.io/docs/versioning)).
   *Interpretation:* for an operations-facing corpus with one deployed system,
   per-claim pinning is the cheaper control and version silos are the expensive
   one.
8. **Treat integration merges as documentation events.** The local evidence
   makes this specific: one sync merge changed 1,855 files. *Interpretation, not
   yet evidenced by an outcome measurement:* running change-impact mapping over
   the merge range at merge time targets re-checking far better than a periodic
   sweep does, because it identifies the small set of nodes the merge actually
   touched. This repository has the mapping tool
   (`launchpad/project-intelligence/corpus/impact.py`); whether running it at
   merge time reduces stale-claim survival is untested here.

**One trap worth naming inside mitigation design.** `impact.py`'s own docstring
records that it uses the literal two-dot `git diff <base> <head>` rather than
merge-base-relative three-dot, deliberately, and that it pins
`-c core.quotepath=false --find-renames` explicitly because those are
user-settable and "would otherwise make the same range produce different output
on different machines". A revision-scoped check whose answer depends on the
reader's git config is not revision-scoped.

## Limits and open questions

- **No direct observation of documentation agents mixing revisions.** The
  strongest quantitative mechanism evidence (Wang et al.) measures *code
  completion*, not documentation authoring. The transfer is an inference: both
  are next-token generation conditioned on retrieved repository text, and the
  measured effect is a property of the context, not of the output genre. It is a
  well-motivated inference and it is still an inference. Directly measuring
  context-version capture in a documentation-authoring setting is the single
  highest-value experiment this report could not run.
- **The stale-rate figure measures this corpus, not corpora in general.** 86.9%
  after 6-13 days reflects a repository that merges 204 upstream commits at a
  time. A repository with a quieter history would show a lower rate without
  anything about the mechanism differing.
- **Staleness is not uniformly a defect, and the counterevidence is strong.**
  Lethbridge et al.'s 81% agreement that documentation can be useful while not
  up-to-date, and their observation that projects fail through "poor management
  and failure to gather requirements, not with out-of-date or incomplete
  documentation", both cut against treating every stale verdict as damage. The
  survey is n=45, from 2003, and predates both docs-as-code and agent authorship
  — but no evidence found in this research contradicts its central claim about
  abstraction level, and Tan et al.'s modern figures are consistent with it:
  outdated references persisted an average of 4.7 years in the top-1000 GitHub
  projects without those projects failing.
- **The ambient-rate figures are pre-agent.** Tan et al. analysed over 3,000
  GitHub projects and found 28.9% of top-1000 projects currently carried at
  least one outdated code-element reference and 82.3% had at some point in their
  history, with references surviving about a month at ~55% probability
  ([2212.01479](https://arxiv.org/abs/2212.01479), RQ1-RQ2). These bound the
  human baseline. Whether agent authorship raises, lowers, or merely accelerates
  that rate is **unmeasured**, and nothing found in this research measures it.
  The 39% "up-to-dateness" share of documentation content issues frequently
  quoted from Aghajani et al. (2019) is reported here **as relayed by Tan et al.**;
  the primary paper was not obtained, so it is one evidentiary chain, not two.
- **ADR-0004's reproduction is unverifiable in this checkout.** Recorded as a
  gap, not as a finding against it.
- **Cross-artifact release skew is identified but not quantified.** No local
  measurement was made of how often documentation mixes manifest, lockfile,
  released-artifact and deployed-instance versions.
- **Open: what a per-claim pin should reference for unpinnable evidence.** 642
  of 1,168 unestablished citations here name no openable file. Whether such
  evidence should be excluded from claims that need revision coherence, or
  captured differently (a recorded tool invocation with its output hash, say),
  is unresolved and not answered by anything found in this research.

## Practical review checks

Candidates derived from this report, offered as research output rather than
adopted policy.

- Does each revision-bound claim (`path:line`, "the handler does X", a config
  default) carry a revision, and does the revision resolve to a commit in the
  repository as checked out?
- Was the recorded revision confirmed to be an **ancestor** of the revision
  being documented, rather than merely older by date? A date comparison is not
  an ancestry test, and in a merge-based history the two disagree.
- If a claim was checked against the working tree, was the checkout confirmed
  complete for the paths in question — not sparse, not shallow, submodules
  initialised? `git ls-tree -r HEAD --name-only` versus what the filesystem
  shows is a two-command test.
- Where a claim rests on a dependency's or upstream's behaviour, does the
  document name which version or which upstream revision, or does it silently
  assume the agent's prior?
- Does any claim's support consist only of citations a revision-scoped check
  cannot resolve (URLs, tool results, graph edges)? If so, is that stated at the
  claim rather than in a closing caveat?
- Does the document use "currently", "new", "now", "latest", or "recently" where
  a date or version could stand instead?
- After a merge that integrates another branch or upstream, was change-impact
  run over the merge range before the documentation was treated as current?
- When a staleness check fires, was the distinction between *movement* and
  *wrongness* preserved in what was recorded — and when it clears, was the
  absence of movement recorded as such rather than as confirmation that the
  claim still holds?
- Does a rationale sentence carried forward from an earlier decision record
  still hold at the current revision, or has it been copied without
  re-derivation?

## References

- [Detecting Outdated Code Element References in Software Repository Documentation](https://arxiv.org/abs/2212.01479) — Wen Siang Tan, Markus Wagner, Christoph Treude; arXiv:2212.01479v1, submitted 2 Dec 2022 (Empirical Software Engineering manuscript). Supports the ambient outdated-reference rates (28.9% of top-1000 projects currently, 82.3% ever, 4.7-year average duration, ~55% one-month survival), the resolution breakdown (RQ3), and the revert-induced negative-timestamp case (footnote 19).
- [LLMs Meet Library Evolution: Evaluating Deprecated API Usage in LLM-based Code Completion](https://arxiv.org/abs/2406.09834) — Chong Wang, Kaifeng Huang, Jian Zhang, Yebo Feng, Lyuye Zhang, Yang Liu, Xin Peng; arXiv:2406.09834, submitted 14 Jun 2024, latest version 13 Feb 2025; published at ICSE 2025. Supports the 25-38% overall deprecated-usage rate, the 70-90% vs 9-18% context effect, and the REPLACEAPI (>85% fix rate) vs INSERTPROMPT (insufficient) comparison.
- [Dated Data: Tracing Knowledge Cutoffs in Large Language Models](https://arxiv.org/abs/2403.12958) — Jeffrey Cheng, Marc Marone, Orion Weller, Dawn Lawrie, Daniel Khashabi, Benjamin Van Durme; arXiv:2403.12958, submitted 19 Mar 2024, revised 17 Sep 2024 (v2). Supports effective-versus-reported cutoff and per-sub-resource cutoff variation.
- [Knowledge Conflicts for LLMs: A Survey](https://arxiv.org/abs/2403.08319) — Rongwu Xu, Zehan Qi, Zhijiang Guo, Cunxiang Wang, Hongru Wang, Yue Zhang, Wei Xu; arXiv:2403.08319, submitted 13 Mar 2024, revised 22 Jun 2024. Supports the context-memory / inter-context conflict taxonomy, temporal misalignment as a named cause, and the model-behaviour findings on parametric bias, frequency, and ordering sensitivity (§2, §3).
- [How Software Engineers Use Documentation: The State of the Practice](https://courses.cs.duke.edu/fall11/cps196.1/classwork/Lethbridge-Singer-Forward-2003.pdf) — Timothy C. Lethbridge, Janice Singer, Andrew Forward; IEEE Software, November/December 2003, pp. 35-39. Counterevidence: 53% somewhat agreed and 28% strongly agreed (n=45) that documentation can be useful while not up-to-date; "the high-level abstractions tend to remain useful when the details become outdated".
- [gitrevisions — specifying revisions and ranges for Git](https://git-scm.com/docs/gitrevisions) — Git project documentation, read 2026-09-08 (local `git version 2.52.0`). Supports the reachability definition of `r1..r2` used to correct the local rationale for the ancestor gate.
- [actions/checkout](https://github.com/actions/checkout) — GitHub, README read 2026-09-08. Supports `fetch-depth` default of 1 and "Only a single commit is fetched by default", the basis for the shallow-checkout detection limit.
- [Timeless documentation](https://developers.google.com/style/timeless-documentation) — Google developer documentation style guide, read 2026-09-08. Supports the time-anchored-prose failure class and the date/version reference-point mitigation, including its release-notes exemption.
- [Versioning](https://docusaurus.io/docs/versioning) — Docusaurus documentation, read 2026-09-08. Supports the counterweight against documentation versioning as a default ("Most of the time, you don't need versioning"; "keep the number of your versions below 10").
- `launchpad/project-intelligence/corpus/stale.py` — this repository at HEAD `4bac39fe512c9b289992951de1222abd61d5790c`, read 2026-09-08. Supports the four gates, the "movement, not meaning" limit, the `fresh`-is-not-correct limit, and the predicted depth-1 CI behaviour. Run on 2026-09-08: `350 node(s): 304 stale, 18 fresh, 28 unestablished`.
- `launchpad/project-intelligence/corpus/impact.py` — same revision, read 2026-09-08. Supports the two-dot versus three-dot range decision and the explicit `core.quotepath` / `--find-renames` pinning for cross-machine determinism.
- `launchpad/skills/review-queue-automation/gap/validate.py`, `gap/methodology.md`, `gap/manifest.md`, `gap/register/fr.md` — same revision, read via `git show HEAD:<path>` because this worktree is sparse. Support single-revision pinning (`eb1cedb19`), revision-bound line citations, the per-row `revision` cell contract, and the deliberately unchecked citation classes.
- Commit `c835cdc62fcc9f55887e145bbf4b0032ad8115f8` (2026-09-08), "gap(#2070): restore SKILL.md to the pinned revision after merging local work" — supports the merge-past-the-pin incident and its revert.
- Commit `3bbbd8367f01db971c581e10f36b21cb2055dc3a` (2026-09-08), "gap(#2070): stale-check compares content, not last-touch commit" — supports the false-staleness class and the blob-identity fix, including its own stated non-extension boundary.
- Commit `d555ec95f` (2026-08-31), "chore: sync launchpad with upstream block/buzz main (204 commits)" — supports merge-import invalidation: 204 commits authored 2026-08-17 to 2026-08-29, 1,855 files changed.
- `launchpad/decisions/ADR-0004-handbook-staleness-detection-mechanism.md` — same revision, read via `git show`. Source of the ancestor-gate rationale examined and partially corrected in Detection and validation; its reproduction commits `c060e936c` and `32f0988c8` are unreachable in this checkout.

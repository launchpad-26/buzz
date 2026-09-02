---
id: ingestion-commits
type: ingestion
status: draft
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "standards/provenance.md, an active corpus node, already fully owns the mandatory per-node recorded-revision entry: its statement shape ('This node was authored and checked against repository revision <sha>'), its single commit citation, the git cat-file -e <sha> check that establishes the cited revision exists, and the four-branch rule for whether a later edit may move that entry forward. This node does not restate any of that."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "AGENTS.md's citation-shape table lists 'Commit reference' as one of six citation shapes, verdict 'Reported UNVERIFIED. Nothing on disk to open.', and states plainly under 'Nothing enforces this' that the checker treats every commit citation identically -- a second, third or tenth FACT resting only on commit <sha> produces nothing but extra non-fatal UNVERIFIED notices and still exits 0, so distinguishing a provenance entry from any other commit-cited claim in the same ledger is a convention a reviewer holds, not a rule validate.py enforces."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md's evidence section states the one conventional exception to 'UNVERIFIED is not a pass': the provenance entry recording the revision cites a commit id 'which no file can corroborate because the citation is the claim', checkable only by git cat-file -e <sha>; and separately states 'a commit citation attached to a claim about repository content is not covered -- that claim needs the file, at that revision', drawing the line this node's own subject sits on the other side of: a claim about a commit's own message or diff, where the commit itself -- not a file at that revision -- is the thing being cited."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41 ('fix(lefthook): resolve file-size-check base from origin/launchpad, not origin/main') states its own rationale directly in its message body: scripts/check-file-sizes-core.mjs resolves the file-size ratchet's base via merge-base origin/main HEAD, correct upstream but wrong for this fork (whose base is launchpad, diverged from main), and the message records that this was 'confirmed repo-wide, not branch-specific' by reproducing the failure on origin/launchpad's own tip against an unmodified 1000-line file -- a rationale an agent could cite as a FACT directly from the message, without inferring intent from the diff alone."
    entry_class: FACT
    evidence:
      - "commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41"
  - statement: "commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41 is reachable from origin/launchpad (git merge-base --is-ancestor 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41 origin/launchpad exits 0), so it is a stable citation target rather than a commit only reachable from a private branch."
    entry_class: FACT
    evidence:
      - "git_merge_base_is_ancestor(commit='3eb5243ba9e8b90e4330976bea6ad5c9424e3d41', ref='origin/launchpad') -> exit 0 (is an ancestor)"
  - statement: "commit 6d45f98665004d314468d98e50084996f4046cdf ('ci: make file-size policy a first-class gate (#6187)'), also reachable from origin/launchpad, carries an explicit '## Why' section in its message stating the rationale directly: the Desktop file-size ratchet had grown to govern desktop/src-tauri/crates/** while the pre-push desktop-check command stayed path-filtered to non-Tauri files, and that contract drift 'allowed a Tauri Rust file-size regression through local validation' -- a second real, independently-reachable example of a commit whose message states design rationale outright rather than requiring inference from its diff."
    entry_class: FACT
    evidence:
      - "commit 6d45f98665004d314468d98e50084996f4046cdf"
      - "git_merge_base_is_ancestor(commit='6d45f98665004d314468d98e50084996f4046cdf', ref='origin/launchpad') -> exit 0 (is an ancestor)"
  - statement: "A commit whose message states only what changed, with no rationale sentence, still carries intent recoverable from its diff (which lines moved, what a surrounding comment or test already says, what the commit's own diff removes as well as adds) -- but a claim built that way is the agent's own reasoning about the diff, not a quotation from the commit, so it takes entry_class INFERENCE with a stated confidence rather than FACT, per AGENTS.md's own FACT/INFERENCE distinction ('INFERENCE -- you reasoned to it from evidence. Reasoning is not fact, however good it is.')."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.75
  - statement: "Sibling agents/repository-navigation.md (#650, unmerged local commit, read directly from __worktrees/task-650-agents-repository-navigation), covers using git log, git log --follow, git log --diff-filter=R, and git blame to locate a symbol's history and the commit(s) that renamed or touched a file -- a search/location technique over the repository's history, not citing one commit's own message or diff as the evidentiary content of a claim about why something is the way it is. This node's subject begins where that one's search ends: once a candidate commit is located, whether and how to cite its message/diff as evidence."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#650 (unmerged local commit, __worktrees/task-650-agents-repository-navigation, read directly)"
  - statement: "Sibling ingestion/git-history.md (#960) is a later, not-yet-built task in this same batch run under Feature #620; no coordination with its actual content is possible. This node's working boundary, stated so a conflict is visible rather than silently resolved by building the broader subject: commits.md is citing one specific commit's own message or diff as evidence of intent; git-history.md, once built, is expected to own the broader git-log/blame/bisect toolset for locating and dating changes generally (the search technique agents/repository-navigation.md already partly covers) -- a real overlap risk between the two names, flagged here rather than assumed away."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body (Feature #620 child-task list) and #960's own issue title"
  - statement: "Issue #954's own Definition of Done text is the same standards-track boilerplate ('states scope and authority/source of the policy', 'separates MUST requirements from SHOULD guidance', 'defines enforcement/checks and exception/escalation process', 'links decisions or higher-order policy instead of duplicating them') that corpus-template-policy, corpus-template-procedure, and corpus-template-reference each independently found copied across many corpus-plan tasks regardless of the node's actual shape, and each overrode with its own 'Note on Definition of Done' once that boilerplate did not fit. This node's subject -- a sequenced technique for locating and citing a commit's own rationale -- has no corpus-wide MUST/SHOULD rule of its own to state; AGENTS.md and standards/provenance.md already own the only binding rules about commit citations. This node is built as a procedure/how-to node against Feature #620's real acceptance criteria (schema/graph/provenance validation, a genuinely-fitting template, concrete source start points, no broad-overview duplication, independent traversability) rather than against #954's copied-over checklist."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#954 definition of done; launchpad-26/buzz#620 acceptance criteria"
---

# Citing a commit's message and diff as evidence: how-to

How an agent finds the commit that explains *why* something in this repository is
the way it is, and cites that commit's own message or diff as the evidentiary content
of a claim -- distinct from the one mandatory commit citation every corpus node
already carries recording the revision it was checked against (`standards/provenance.md`'s
subject, not this one).

## Before you start

- Know the difference this node draws: `standards/provenance.md` governs the single
  `evidence` entry every node carries stating "this node was authored and checked
  against repository revision `<sha>`" -- a claim about the whole ledger's currency.
  This node is about a *different, ordinary* claim in the same ledger: a claim that
  cites a commit's message or diff as the reason a design, field, or fix exists. Both
  end up cited the same way (`commit <sha>`) and the checker cannot tell them apart
  (see the evidence entry above) -- a reviewer has to.
- Know `AGENTS.md`'s citation-shape table: a `commit <sha>` citation is always
  reported `UNVERIFIED` by `validate.py`. It is never opened, never compared against
  the statement it supports. The one thing a human can check is that the revision
  exists at all (`git cat-file -e <sha>`); nothing checks that the commit actually
  says what the claim says it does.
- Know `AGENTS.md`'s `FACT`/`INFERENCE` distinction before starting: it decides which
  class a commit-message-derived claim gets, in Task 2 below.

## Task 1: Locate the commit that explains the design choice

1. Start from the file or symbol the claim is about, using
   `agents/repository-navigation.md`'s techniques (`git grep`, `git log --follow`,
   `git blame`) to find candidate commits -- that node's subject is finding the
   commit; this node's subject starts once you have one.
2. If a nearby comment, PR description, or issue reference names a rationale
   directly, follow it to the commit it names rather than re-deriving the reasoning
   from a blind `git log`.
3. Prefer a commit reachable from the branch you are merging into
   (`git merge-base --is-ancestor <sha> origin/launchpad`) over one that only exists
   on a private branch -- a citation that resolves today but disappears once a
   feature branch is deleted is a citation that silently rots, even though
   `validate.py` cannot detect the difference either way.
4. When more than one commit plausibly touches the subject (a fix, then a follow-up
   fix, then a rename), read each rather than citing the first match -- the same
   "expect more than one definition" discipline `agents/repository-navigation.md`
   states for symbols applies to commits too.

## Task 2: Read the commit and decide the claim's class

1. Read the full commit message body, not only its subject line --
   `git log -1 --format='%H%n%s%n%n%b' <sha>` or `git show <sha>`. A rationale is
   often in the body (a `## Why` section, a paragraph of prose) and never in the
   one-line subject.
2. **If the message states the rationale directly**, the claim is a `FACT`: you
   opened the source and it says so. `commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41`
   is a worked example -- its message states outright that the file-size ratchet's
   `merge-base origin/main HEAD` is wrong for a fork whose base is `launchpad`, and
   records how that was confirmed. `commit 6d45f98665004d314468d98e50084996f4046cdf`
   is a second, independent example: an explicit `## Why` section states the
   rationale (a path-filter contract drift between a lint command and the file-size
   ratchet's actual scope) in so many words.
3. **If the message says only what changed, and the "why" has to be read out of the
   diff itself** (what surrounding code the change interacts with, what a removed
   line used to do, what a nearby test now asserts that it did not before), the
   resulting claim is your own reasoning about the diff, not a quotation from the
   commit. Classify it `INFERENCE` with a stated `confidence`, per the evidence entry
   above -- never promote a diff-only reading to `FACT` because the commit itself is
   real and opened. The commit being real does not make your interpretation of it a
   fact.
4. If neither the message nor the diff supports the claim you wanted to make, the
   commit is the wrong citation. Do not stretch the classification to fit; look
   for a different commit, or drop the claim.

## Task 3: Write the citation

1. Cite the commit as `commit <full 40-character sha>`, the same shape
   `AGENTS.md`'s table names -- a short SHA is not the citation shape the corpus's
   own convention (and `git cat-file -e`) expects.
2. State, in the node's evidence entry or nearby prose if the ledger entry alone
   would be ambiguous, which kind of commit citation this is -- the recorded-revision
   entry, or an ordinary claim like this one -- so a reviewer checking a ledger with
   more than one commit-only entry (a state `AGENTS.md`'s "Nothing enforces this"
   subsection names as unchecked by tooling) does not have to guess.
3. Expect the citation to render as `UNVERIFIED` when `validate.py` runs. That is
   correct and does not mean the claim is unchecked -- it means the checker cannot
   open a commit the way it opens a file; the human act of reading the commit already
   happened in Task 2, and `git cat-file -e <sha>` remains available to confirm the
   revision itself still exists.

## See also

- `launchpad/docs/corpus/standards/provenance.md` -- the one mandatory commit
  citation every node carries, its shape, and the revision-move rule. Read this
  first if unsure whether a claim is that entry or an ordinary one like the kind
  this node covers.
- `launchpad/docs/corpus/AGENTS.md` -- the citation-shape table, the `FACT`/
  `INFERENCE`/`TEAM_KNOWLEDGE` contract, and the "Nothing enforces this" subsection
  this node's own evidence ledger cites directly.
- `agents/repository-navigation.md` (#650, unmerged as of this writing) -- locating
  the commit and the code path in the first place, before this node's Task 2 begins.

## Boundary

This node does not describe:

- **A lookup catalogue of commit-citation facts** (the six citation shapes, which
  ones a checker opens) -- that is information-oriented reference content, and
  `AGENTS.md`'s own citation-shape table already is that catalogue. This node is
  sequenced technique (find the commit, read it, classify the claim, cite it), not
  a table to consult mid-task.
- **Acquiring the underlying skill of reading a commit message or a diff from
  scratch**, for someone who has never done either -- that is a tutorial, a
  Diátaxis form no corpus template currently covers; this node assumes an
  already-competent reader, the same assumption `agents/repository-navigation.md`
  states for itself.
- **Why commit-message rationale matters as a concept**, or a discursive treatment
  of provenance and evidence in the abstract -- that is understanding-oriented
  explanation, and this node's own evidence ledger already cites `AGENTS.md` and
  `standards/provenance.md` for the concepts it depends on rather than re-arguing
  them here.
- **The mandatory recorded-revision commit citation every node carries.** That is
  `standards/provenance.md`'s subject in full -- what it asserts, when it may move,
  what a partial re-verification owes it. This node's subject is a different,
  ordinary claim that happens to use the identical citation shape.
- **Locating a commit or a symbol's history in the repository generally** (`git log
  --follow`, `--diff-filter=R`, `git blame` across a rename). That is
  `agents/repository-navigation.md`'s subject; this node assumes a candidate commit
  is already in hand and covers only what happens next.
- **The broader git-log/blame/bisect toolset for locating and dating changes**,
  which sibling `ingestion/git-history.md` (#960) is expected to own once it is
  built later in this same batch run. No coordination with that node's actual text
  was possible while writing this one -- see *Scope and omissions* for the
  unresolved tension this leaves.
- **The six citation shapes generally, or what a passing `validate.py` run does and
  does not establish.** `AGENTS.md` owns that in full; this node only draws on the
  one row (commit reference) relevant to its own subject.
- **Any repository-specific commit-message convention** (Conventional Commits
  prefixes, `Signed-off-by` trailers, `Fixes #N` linkage) beyond what the two worked
  examples happen to use. Those are development/git-workflow conventions, not this
  node's subject.

## Relationships

**Declared: none.** Checked against `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`: `standards/provenance.md` and `AGENTS.md` are both merged and
real relationship targets, and this node's body depends on both for the boundary it
draws against them. A `references` edge toward each would be legitimate the same way
`agents/repository-navigation.md` declares `depends-on: corpus-agents` for an
analogous reason -- but none of Feature #620's 32 sibling `agents/*.md` /
`ingestion/*.md` tasks are merged at this node's recorded revision (confirmed by the
same `git ls-tree` run), and this batch-author pass targets exactly one document per
issue without editing another node's front matter, so no edge is added here. The
natural moment to add `references: corpus-agents` and `references:
corpus-standard-provenance` is either this node's next edit or the batch's later
relationship-wiring pass, whichever comes first once both targets and this node
coexist in the same validated tree.

## Scope and omissions

**This node covers** locating the commit that explains a design choice's rationale,
reading its message and diff to decide whether the resulting claim is `FACT` or
`INFERENCE`, and writing the resulting `commit <sha>` citation so it is
distinguishable, by a reviewer, from the one mandatory recorded-revision entry every
node already carries.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The mandatory recorded-revision commit citation, its shape, and the revision-move rule | `launchpad/docs/corpus/standards/provenance.md` |
| Locating a commit or symbol's history generally (`git log --follow`, `--diff-filter=R`, `git blame`) | `agents/repository-navigation.md` (#650, unmerged) |
| The broader git-log/blame/bisect toolset for locating and dating changes | `ingestion/git-history.md` (#960, not yet built -- see *Boundary* above) |
| The full six-shape citation table and what `validate.py` does with each | `launchpad/docs/corpus/AGENTS.md` |
| The `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` contract itself | `launchpad/docs/corpus/AGENTS.md`; `launchpad/project-intelligence/CONTRACT.md` |
| Repository-specific commit-message conventions (Conventional Commits, `Signed-off-by`, issue linkage) | Not a corpus-node subject found; a repository git-workflow convention rather than an ingestion technique |

**Expected but not verified when this node was written:**

- **Whether `ingestion/git-history.md` (#960), once built, draws the boundary against
  this node the same way this node draws it from its own side** could not be checked
  -- that sibling has no text yet in this batch run. If its eventual scope turns out
  to also cover citing a single commit's message/diff as evidentiary content, the two
  nodes overlap and one should be narrowed; this is named as a real risk, not resolved
  here.
- **Whether `agents/repository-navigation.md` (#650), once merged, still describes
  only search/location and not also commit-message citation** was checked against its
  current unmerged local-commit text, not a possibly-revised merged version.
- **No reader has yet followed Task 1 through Task 3 end-to-end against a real,
  previously unseen claim** to confirm the two worked examples generalize; both are
  drawn from this same repository's file-size-check history, which happens to state
  its rationale unusually explicitly and may not be representative of terser commit
  messages elsewhere in the repository.

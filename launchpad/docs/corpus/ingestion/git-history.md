---
id: ingestion-git-history
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
  - statement: "AGENTS.md's citation-shape table names 'Commit reference' as one of six shapes, verdict 'Reported UNVERIFIED. Nothing on disk to open.', and states under 'Nothing enforces this' that the checker treats every commit citation identically regardless of what claim it supports; separately, AGENTS.md's evidence section defines FACT as 'you opened the cited source and it says so', INFERENCE as reasoning rated with a confidence, and TEAM_KNOWLEDGE as an uncorroborated statement attributed to whoever said it -- the three-way contract this node's MUST rules apply specifically to git-history-derived claims."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "validate.py's _load_frontmatter splits a node's text on the frontmatter delimiter and assigns the remainder to _body (line 200), which no other function in the module reads -- confirmed directly, not assumed from a sibling document's say-so. Separately, _COMMIT_CITATION_RE (line 566) matches 'commit <7-to-40-hex-chars>' and the checker's own message (line 738) reports any such citation 'unverified ... is a commit reference, which names no openable file', applied identically no matter which claim the citation is attached to."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:200"
      - "launchpad/project-intelligence/corpus/validate.py:566"
      - "launchpad/project-intelligence/corpus/validate.py:738"
  - statement: "ADR-0029 decides that evidence is ranked contextually by claim type rather than by one fixed hierarchy: for claims about current behavior, executable evidence (code, config, schema, passing tests) is authoritative over documentation, GitHub history, or inference; for claims about intended or authorized behavior, accepted decisions are authoritative over code that has since drifted without a corresponding update; GitHub history and inference may supply context but are never fact on their own; latest-timestamp-wins is explicitly rejected as a tiebreaker; and two authoritative sources of the same claim type in material conflict are recorded and left for a human (the flagged state) rather than silently resolved."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "standards/decision-references.md (merged, active) applies ADR-0029's intent/authorization-versus-current-behavior split specifically to citing accepted decision records against code, and its own scope-and-omissions table assigns 'Citing code, tests, config and schema' to a different node (code-references.md) without naming git-history artifacts -- commit messages, git log output, git blame attribution -- anywhere in its scope. The same split has not previously been written down for that evidence type."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "standards/provenance.md (merged, active) governs exactly one commit citation per node -- the mandatory recorded-revision entry, its 'commit <sha>' shape, the git cat-file -e <sha> check, and the four-branch revision-move rule -- and states explicitly that its own scope stops there; it does not address an ordinary claim that happens to cite a commit for the commit's own content, which is this node's subject and #954/ingestion-commits.md's."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/provenance.md"
  - statement: "standards/code-references.md and standards/test-references.md each reject a GitHub link whose view-verb is 'blame', 'commits', 'tree' or 'edit' as a hard error, on the stated grounds that 'a view of a file is not a citation of it' -- a rule about a link's URL shape, distinct from this node's subject of using git log/blame *output* (not a URL to a blame view) as the evidentiary content of a claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
      - "launchpad/docs/corpus/standards/test-references.md"
  - statement: "This repository checkout is a shallow git clone: git rev-parse --is-shallow-repository reports true at this node's recorded revision. Separately (and independently, reused directly from crates/buzz-db/src/store/thread.rs, already opened for this fact by sibling agents/repository-navigation.md): git log --oneline for that path returns exactly 1 commit, while git log --oneline --follow for the identical path returns 15, at the same repository revision -- a concrete demonstration that a commit-count claim taken from the plain form is not merely incomplete in principle but wrong by a factor of fifteen in this repository, for a file that is not unusual within it."
    entry_class: FACT
    evidence:
      - "git_rev_parse(flag='--is-shallow-repository') -> true"
      - "git_log(pathspec='crates/buzz-db/src/store/thread.rs', follow=false) -> 1 commit"
      - "git_log(pathspec='crates/buzz-db/src/store/thread.rs', follow=true) -> 15 commits"
  - statement: "commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41 ('fix(lefthook): resolve file-size-check base from origin/launchpad, not origin/main') states directly in its message body that scripts/check-file-sizes-core.mjs resolves the ratchet's base via merge-base origin/main HEAD, correct upstream but wrong for this fork, and that the fix adds a lefthook-local.yml override rather than editing the upstream-owned script; reachable from origin/launchpad (git merge-base --is-ancestor confirms exit 0)."
    entry_class: FACT
    evidence:
      - "commit 3eb5243ba9e8b90e4330976bea6ad5c9424e3d41"
      - "git_merge_base_is_ancestor(commit='3eb5243ba9e8b90e4330976bea6ad5c9424e3d41', ref='origin/launchpad') -> exit 0"
  - statement: "At this node's recorded revision, the current files the commit above describes still show the fix live: lefthook-local.yml:5 sets CHECK_FILE_SIZES_BASE: origin/launchpad, and scripts/check-file-sizes-core.mjs:45-46 reads that override before falling back to its own merge-base origin/main HEAD default at line 55 -- checked directly against the current file rather than assumed to still hold because the commit message said so, which is the independent current-source check MUST 2 below requires."
    entry_class: FACT
    evidence:
      - "lefthook-local.yml:5"
      - "scripts/check-file-sizes-core.mjs:45"
      - "scripts/check-file-sizes-core.mjs:46"
      - "scripts/check-file-sizes-core.mjs:55"
  - statement: "This node's type is ingestion, matching sibling ingestion-commits (#954), because its subject -- how a claim derived from a git-history artifact is weighed and admitted into a corpus node's evidence ledger -- is an ingestion-surface technique (gathering and classifying evidence for authoring), not the corpus's own meta-authoring-rules surface AGENTS.md and the standards/ track carry as governance; the same type-by-subject-surface reasoning node.schema.json's own description states and templates/policy.md's 'A note on type' section applies to itself."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/templates/policy.md"
    confidence: 0.75
  - statement: "Sibling agents/repository-navigation.md (#650, unmerged local commit, __worktrees/task-650-agents-repository-navigation, read in full) covers locating a symbol, a commit, or a rename in the wider repository using git grep, git log --follow, --diff-filter=R and git blame -- a search/location procedure. It does not state any rule for how much evidentiary weight the thing found, once found, carries for a FACT versus an INFERENCE, nor whether a shallow clone changes what a count derived that way may claim."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#650 (unmerged local commit, __worktrees/task-650-agents-repository-navigation, read directly)"
  - statement: "Sibling ingestion/commits.md (#954, unmerged local commit, __worktrees/task-954-ingestion-commits, read in full) covers the how-to procedure for citing one specific commit's message or diff as evidence of a design rationale -- locate the commit, read message and diff, decide FACT versus INFERENCE for that one artifact, write the citation -- and its own evidence ledger names this node (#960) as expected to own 'the broader git-log/blame/bisect toolset for locating and dating changes generally,' flagging the overlap as a real, unresolved risk since no coordination was possible. Read in full rather than assumed from that flag alone, #954 does not state a rule for whether a commit-message-derived intent claim may be read as a current-behavior claim, nor any rule about git blame-derived attribution, age or count claims, nor the shallow-clone risk -- so this node's actual content narrows the flagged overlap to those three gaps rather than rebuilding #954's own single-commit-citation procedure or #650's search technique."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#954 (unmerged local commit, __worktrees/task-954-ingestion-commits, read directly)"
  - statement: "Issue #960's own Definition of Done carries the same standards-track boilerplate ('states scope and authority/source of the policy', 'separates MUST requirements from SHOULD guidance', 'defines enforcement/checks and exception/escalation process', 'links decisions or higher-order policy instead of duplicating them') that templates/policy.md itself records as copied across many corpus-plan tasks regardless of a node's real shape; this node is built against Feature #620's real acceptance bar (schema/graph/provenance validation, a genuinely-fitting template, concrete source start points, no broad-overview duplication, independent traversability) with the coincidental fit to #960's own DoD noted rather than assumed deliberate."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#960 definition of done; launchpad-26/buzz#620 acceptance criteria"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-decision-references
  - type: references
    target: corpus-standard-provenance
---

# Policy: evidentiary weight of git-history-derived claims

This node states binding requirements on when a claim derived from a git-history
artifact -- a commit's message or diff, `git log` output, or `git blame` attribution --
may be classified `FACT` for a *current*-behavior assertion versus only for a
*past*-revision or attribution assertion, and how a same-claim-type conflict between two
such claims is handled. It binds any corpus node whose `evidence` array cites a commit,
a `git log` result, or a `git blame` result.

## Scope and authority

**This node governs** the evidentiary weight and admissibility of a claim, in another
corpus node's `evidence` array, that is derived from a git-history artifact rather than
from the current state of a file: a commit's message or diff cited for what it says about
design rationale or intent, a `git log`/`git log --follow`/`--diff-filter=R` result cited
for a count or a rename history, or a `git blame` result cited for attribution or age.

**Its authority comes from** `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md`,
the accepted decision that ranks evidence contextually by claim type and escalates rather
than resolves a same-claim-type conflict. **Where this node and ADR-0029 disagree, ADR-0029
wins** -- this document applies ADR-0029's existing rule to one evidence type it does not
itself name, and adds nothing ADR-0029 would not already license.

**It does not cover** locating a commit, a symbol, or a rename in the repository
(`agents/repository-navigation.md`, #650, unmerged); the how-to procedure for citing one
specific commit's message or diff as evidence of a design rationale
(`ingestion/commits.md`, #954, unmerged); citing an accepted decision record against code
(`standards/decision-references.md`); the mandatory recorded-revision commit citation
every node carries (`standards/provenance.md`); or citing a code or test file itself
(`standards/code-references.md`, `standards/test-references.md`). See *Scope and
omissions* for what each of those owns instead.

| For | Read |
|---|---|
| Ranking conflicting evidence by claim type, and the `flagged` state | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Locating a commit, symbol or rename in the repository | `launchpad/docs/corpus/agents/repository-navigation.md` (#650, unmerged) |
| Citing one commit's message/diff as design-rationale evidence | `launchpad/docs/corpus/ingestion/commits.md` (#954, unmerged) |
| Citing an accepted decision record | `launchpad/docs/corpus/standards/decision-references.md` |
| The mandatory recorded-revision commit citation | `launchpad/docs/corpus/standards/provenance.md` |
| Citing a code or test file itself | `launchpad/docs/corpus/standards/code-references.md`, `launchpad/docs/corpus/standards/test-references.md` |
| The FACT/INFERENCE/TEAM_KNOWLEDGE contract and the six citation shapes | `launchpad/docs/corpus/AGENTS.md` |

## MUST

| # | Requirement |
|---|---|
| **G1** | A claim that quotes or paraphrases what a commit message, PR description, or issue discussion states about rationale, intent, or design at the time of that commit MUST be classified `FACT` only for what it asserts as of that revision. It MUST NOT, without further checking, be read as also asserting that the same is true of the repository's *current* behavior at `HEAD` -- the commit message describes the world at the moment it was written and has no way of knowing what changed afterward. |
| **G2** | A claim asserting the repository's *current* behavior MUST cite the current executable source (code, config, schema, or a passing test) that the behavior is claimed to still show, even when a git-history citation for the same subject already exists. A `FACT` about current behavior MUST NOT rest on a git-history citation alone. This is ADR-0029's current-behavior tiebreaker (executable evidence outranks history) applied to this evidence type: `validate.py` never opens a commit citation or compares it against anything (per the `_COMMIT_CITATION_RE` evidence above), so nothing but this check at authoring time catches a claim that quietly stopped being true. |
| **G3** | A claim built from `git blame` attribution -- which commit last touched a line or range, how old that commit is, how many distinct commits or authors touched a file or range -- MUST be classified as evidence only of that attribution or history fact (who, when, how many). It MUST NOT be extended to a claim about behavioral stability, correctness, or ongoing design intent ("unchanged for two years, so it must be deliberate/stable/correct") without a separately cited justification for that inferential step; the step itself, if made, is `INFERENCE` with a stated `confidence`, never `FACT`. |
| **G4** | A commit-count, author-count, or file-age claim derived from `git log` or `git blame` MUST first confirm the repository clone is not silently truncating the history being counted -- run `git rev-parse --is-shallow-repository`, and if it reports `true`, confirm the count was taken with `--follow` (for a possibly-renamed file) or against a source known to hold full history. A count taken without this check is not a citable `FACT` about "how many": a shallow clone returns a real, well-formed, wrong number, not an error a careless author would notice. |
| **G5** | Two git-history-derived claims of the same claim type that materially disagree (for example, two commits each purporting to state the repository's current design intent for the same subject) MUST NOT be resolved by preferring the more recent commit. Per ADR-0029, recency is not a tiebreaker; the conflict is recorded in the affected node, and its `status` is set to `flagged` if the conflict is not otherwise resolved. |

## SHOULD

| # | Guidance |
|---|---|
| **H1** | A claim implying that a historical rationale still holds SHOULD pair the git-history citation with the current-source citation required by G2 in the same evidence entry, rather than splitting them across two entries a reader has to reassemble. |
| **H2** | When a `git blame`/`git log` citation is offered only as corroborating context for a claim whose real evidentiary weight comes from elsewhere, the evidence entry SHOULD say so, rather than leaving a reader to assume the git-history citation alone was the whole basis. |
| **H3** | A commit-count, author-count, or age figure SHOULD be stated as of the revision recorded in the node's provenance entry, since the identical `git log`/`git blame` command run again later returns a different number as `HEAD` advances. |

## Enforcement

**Nothing automated enforces G1-G5, or H1-H3.** Verified directly: `validate.py`'s
`_load_frontmatter` (`validate.py:200`) splits a node's text on the frontmatter delimiter
and discards the remainder into `_body`, which no other function in the module reads --
every requirement above lives in body prose, so none of it is inspected by any check.

**The checker cannot distinguish a G1/G2-compliant claim from a violation, either.**
`_COMMIT_CITATION_RE` (`validate.py:566`) matches any citation shaped `commit <sha>` and
reports it `unverified` (`validate.py:738`) with no awareness of which claim type the
citation is attached to -- a commit citation correctly scoped to a past-revision claim and
one incorrectly stretched to a current-behavior claim print the identical notice and the
identical exit status.

**What a green `validate.py` run does not establish about a git-history-derived claim:**

| Not established | Consequence |
|---|---|
| That a commit-message-derived claim is scoped to the revision it describes (G1) | A claim silently promoted to a current-behavior assertion validates |
| That a current-behavior claim also cites current executable source (G2) | A `FACT` resting on history alone validates |
| That a blame-derived attribution claim is not stretched into a stability claim (G3) | The stretch validates identically to the narrower, honest claim |
| That a count was checked against shallow-clone truncation (G4) | A wrong count from a shallow clone validates exactly like a correct one from a full clone |
| That two git-history claims of the same claim type were reconciled rather than the newer one silently preferred (G5) | Either resolution validates |

**Enforcement is the pull-request review**, the same posture every other policy-shaped
node in this corpus takes (`templates/policy.md`, `standards/provenance.md`): ADR-0028
chose Markdown so the corpus would be reviewed as a human-read diff, and that review is
what this document gives something concrete to check a git-history-derived claim against.

## Exceptions and escalation

**There is no exemption from G1-G5.** They are direct applications of ADR-0029's already-
accepted rule to one evidence type; an author cannot widen what a commit citation may
assert by agreeing among themselves to do so -- that would be a proposal against ADR-0029
itself, decided the way any accepted decision is revisited, not an exception granted here.

**H1-H3 are departed from in the open, not waived.** A node may do otherwise, but says
which guidance it departed from and why, in the section the guidance would have applied
to.

**A disputed application of G1-G5 is a reviewer judgment call, not an exception.** The
author records the tension in the pull request; if author and reviewer disagree, the
disagreement is filed as an issue against this node, because a rule two people read
differently is a defect in the rule, not a reason to route around it quietly.

**A same-claim-type conflict this node's G5 does not resolve** -- because, for example,
resolving it requires information outside this repository, or the conflict is between two
accepted normative sources rather than two git-history artifacts -- is ADR-0029's own
escalation path: record it, set `status: flagged`, and raise it as an issue against the
parent Feature (#620) or PRD (#605) describing what could not be settled here.

**`status: flagged` is not a substitute for meeting G1-G5.** It names an unresolved
conflict ADR-0029 defines; it is not a way to publish a claim this node's requirements
would otherwise block.

## Relationships

**Declared:** `depends-on: corpus-agents` -- this node's FACT/INFERENCE/TEAM_KNOWLEDGE
contract and its citation-shape table (a commit reference is always `UNVERIFIED`) are
`AGENTS.md`'s, not original to this node; G1-G5 apply that contract to one evidence type
rather than restating it. `implements: corpus-template-policy` -- this node is built from
that template's six-section shape. `references: corpus-standard-decision-references` --
the merged sibling already applying ADR-0029's same current-behavior/intent split to a
different evidence type (decision records versus code), read for conceptual grounding
without this node depending on its specific content. `references:
corpus-standard-provenance` -- the merged sibling this node's own Scope and authority
distinguishes itself from (the one mandatory recorded-revision commit citation, versus
this node's ordinary git-history-derived claims).

**Checked and not declared:** none of Feature #620's 32 sibling `agents/*.md` /
`ingestion/*.md` tasks, including #650 and #954, are merged on `origin/launchpad` at this
node's recorded revision (confirmed by `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`), so none is a valid `relationships[].target`.

## Scope and omissions

**This node covers** when a claim derived from a git-history artifact -- a commit
message/diff, `git log` output, or `git blame` attribution -- may be classified `FACT` for
a current-behavior assertion versus only for a past-revision or attribution assertion; the
distinct evidentiary status of blame-derived attribution/age/count claims; the shallow-
clone risk to any count derived from `git log`/`git blame`; and how a same-claim-type
conflict between two such claims is handled, per ADR-0029.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Locating a commit, symbol, or rename in the repository (`git grep`, `git log --follow`, `--diff-filter=R`, `git blame` as search) | `launchpad/docs/corpus/agents/repository-navigation.md` (#650, unmerged) |
| The how-to procedure for citing one specific commit's message/diff as design-rationale evidence | `launchpad/docs/corpus/ingestion/commits.md` (#954, unmerged) |
| Citing an accepted decision record against code, and ADR-0029's split applied to that evidence type | `launchpad/docs/corpus/standards/decision-references.md` |
| The mandatory recorded-revision commit citation, its shape, and the revision-move rule | `launchpad/docs/corpus/standards/provenance.md` |
| Citing a code or test file itself as evidence of current behavior | `launchpad/docs/corpus/standards/code-references.md`, `launchpad/docs/corpus/standards/test-references.md` |
| The general FACT/INFERENCE/TEAM_KNOWLEDGE contract, the six citation shapes, and how to choose a class in general | `launchpad/docs/corpus/AGENTS.md` |
| The `confidence` field's meaning and bands | `launchpad/docs/corpus/standards/confidence.md` |
| Verifying a citation's line number against the file it names | #1459 |
| Encoding G1-G5 into `validate.py` | Not filed; this document intentionally states a review-enforced convention, the posture every other policy-shaped node in this corpus takes for its own review-only rules |

**Expected but not verified when this node was written:**

- **Whether any already-merged corpus node violates G1-G5** was not audited -- this node
  states the rule prospectively; a sweep of existing evidence ledgers for a git-history
  citation stretched past what it can support is a separate task this node does not
  attempt.
- **Whether `ingestion/commits.md` (#954), once merged, still leaves G1-G5 as genuinely
  uncovered ground**, or gains overlapping text of its own, was checked against its current
  unmerged local-commit text only, not a possibly-revised merged version.
- **Whether `agents/repository-navigation.md` (#650), once merged, adds any statement
  about evidentiary weight beyond locating history** was checked against its current
  unmerged local-commit text only, for the same reason.
- **No reader has yet applied G1-G5 to a claim this node's own author did not already
  construct** -- the worked examples above (the `origin/launchpad`/`origin/main`
  file-size-check fix, the shallow-clone/`--follow` discrepancy on `thread.rs`) are real
  and independently verified, but both were chosen because they were already available
  from this session's own evidence-gathering, not sampled at random from the repository's
  full commit history.

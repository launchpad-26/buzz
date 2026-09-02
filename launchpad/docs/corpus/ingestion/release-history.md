---
id: ingestion-release-history
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
  - statement: "RELEASING.md states that Buzz has three independent release lanes -- desktop, relay and mobile -- each with its own entry point and artifact (`just release-desktop <version>`, `just release-relay`, `scripts/mobile-release.sh candidate X.Y.Z`), and that 'the lanes version independently': desktop reads its own manifests, relay reads its own crate manifest, and mobile derives both source and marketing version from the exact candidate tag."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's own Version Sources table names desktop's release version authority as `desktop/package.json` and synchronized desktop manifests, relay's as `crates/buzz-relay/Cargo.toml`, and mobile's as the exact `mobile-vX.Y.Z-rc.N` remote tag -- three distinct authorities, none interchangeable with another."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "RELEASING.md's 'What Gets Published' section states desktop publishes two separate GitHub Releases: `desktop-v<version>`, an immutable, user-facing release with installers, and `buzz-desktop-latest`, a rolling auto-updater release whose `latest.json` 'changes only through the manual promotion workflow' -- so 'the current release' and a specific named `desktop-v<version>` release are documented as two different things, one mutable and one not."
    entry_class: FACT
    evidence:
      - "RELEASING.md"
  - statement: "Measured directly with `git for-each-ref --format='%(creatordate:iso) %(creatordate:unix) %(refname)'` against this repository's own tags: `desktop-v0.5.12`'s creatordate prints as `2026-08-14 13:54:39 -0600` (unix 1786737279) and `mobile-v0.11.0-rc.2`'s prints as `2026-08-14 14:31:30 +0000` (unix 1786717890). Lexicographic string comparison of the two ISO strings orders `desktop-v0.5.12` first (`\"13\" < \"14\"` at the hour position); comparing the unix values orders `mobile-v0.11.0-rc.2` first, because 1786717890 < 1786737279 -- the string order is the wrong order for these two tags."
    entry_class: FACT
    evidence:
      - "git_for_each_ref(format='%(creatordate:iso) %(creatordate:unix) %(refname)', refs='refs/tags/desktop-v0.5.12,refs/tags/mobile-v0.11.0-rc.2') -> desktop-v0.5.12: 2026-08-14 13:54:39 -0600 (unix 1786737279); mobile-v0.11.0-rc.2: 2026-08-14 14:31:30 +0000 (unix 1786717890)"
  - statement: "validate.py's `_COMMIT_CITATION_RE` matches only the literal shape `commit <7-to-40-hex-chars>`; a bare tag name such as `desktop-v0.5.18` does not match it, does not match the graph-edge or tool-result shapes either, and is not a `path:line` position, so `_classify_citation` falls it through to `_classify_repo_path`, where it is resolved as a repository path, found not to exist, and reported a hard error ('does not resolve to a real file in the repository') -- a bare tag name is not a citable string in this schema's evidence forms."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:566"
      - "launchpad/project-intelligence/corpus/validate.py:701-755"
  - statement: "validate.py's `_GITHUB_URL_RE` requires the URL's verb segment to be one of `blob|raw|tree|blame|commits|edit`; a GitHub Releases page (`.../releases/tag/<name>`) does not match any of them, so `_classify_url` falls through to its final branch and reports the link `unverified` as a generic external URL, the identical verdict a non-GitHub URL receives -- a Release page proves nothing more, to this checker, than any other external link."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:551-559"
      - "launchpad/project-intelligence/corpus/validate.py:648-650"
  - statement: "Measured on this session's date: `git ls-remote --tags upstream` (block/buzz) lists `desktop-v0.5.19` at commit `ab691bcdaeccaa6698a2199beaba3f6e93daae81` and `desktop-v0.5.20` at `95154bee4034ca7a40b33095c2ddbde8c9aa1614`. After `git fetch origin --tags` against this fork's own `origin` remote (launchpad-26/buzz), neither tag is present locally, even though the corresponding release commits -- `7a1b7d8e0 chore(release): release Buzz Desktop version 0.5.19 (#6828)` and `52621c09b chore(release): release Buzz Desktop version 0.5.20 (#6839)` -- are ancestors of this node's recorded revision. A release-process commit landing in history is not proof that every remote carries the matching tag."
    entry_class: FACT
    evidence:
      - "git_ls_remote(remote='upstream', refs='tags/desktop-v0.5.19,tags/desktop-v0.5.20') -> ab691bcdaeccaa6698a2199beaba3f6e93daae81 refs/tags/desktop-v0.5.19; 95154bee4034ca7a40b33095c2ddbde8c9aa1614 refs/tags/desktop-v0.5.20"
      - "git_tag(pattern='desktop-v0.5.19,desktop-v0.5.20', remote='origin', after='git fetch origin --tags') -> no matching refs (commits 7a1b7d8e0 and 52621c09b are ancestors of HEAD aef93f2c2)"
  - statement: "`standards/code-references.md`, an active merged corpus standard, states its own scope as governing 'every citation, in any node's evidence ledger, that names code in a repository' and explicitly does not govern which evidence class a claim carries or the graph-edge/tool-result forms -- a narrower, general standard this node builds on rather than restates."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "`standards/decision-references.md`, an active merged corpus standard, states its governing question as 'if the code and the decision said different things, which one would a reader call the defect?' and requires an intent claim -- what was decided, intended or authorized -- to cite the accepted decision itself rather than code that happens to agree with it."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "ADR-0041 ('Pin main to relay/desktop upstream tags with a standing prompt'), an accepted decision, states as an intent claim that `launchpad-26/main` is advanced only to named `relay-v*`/`desktop-v*` tags with the resolved commit SHA recorded alongside the tag name, and separately documents its own prior miscount corrected on review: 'An earlier revision of this record claimed no qualifying tag was an ancestor at all, which is false,' with the corrected tag list re-measured by `git for-each-ref --sort=creatordate` rather than trusted from the earlier draft."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0041-pin-main-to-relay-desktop-tags.md"
  - statement: "This node's `type` is `ingestion` rather than `release`, on the reasoning that its subject is how a corpus author or reviewer treats this repository's release/version history as evidence for a claim -- the same ingestion-process surface every other merged or drafted `ingestion/*.md` sibling in this batch carries -- and not the separate `release` surface `node.schema.json`'s enum reserves for documenting Buzz's own release engineering as a subject in its own right."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "git_show(ref='task/965-ingestion-provenance-records', path='launchpad/docs/corpus/ingestion/provenance-records.md') -> front matter carries type: ingestion, an unmerged sibling under this same batch's ingestion/ family"
    confidence: 0.85
  - statement: "Parent Feature #620 lists this task among 32 child document tasks under an `agents/` and `ingestion/` path family with the stated outcome 'Agents can deterministically navigate, evidence, draft, validate and maintain corpus nodes using documented procedures'; its sibling ingestion tasks (#953-#972) name other specific evidence-source types -- commits, git history, issues, pull requests, migrations -- and none of their own issue titles names release/version history as their subject, distinguishing this node's subject from every sibling's."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body and launchpad-26/buzz#953-#972 issue titles"
  - statement: "Issue #969's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#969 definition of done"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: implements
    target: corpus-template-policy
  - type: references
    target: corpus-standard-code-references
  - type: references
    target: corpus-standard-decision-references
---

# Policy: citing release/version history as corpus evidence

How a corpus node cites this repository's release and version history -- git release
tags, `RELEASING.md`'s documented process, per-lane changelogs and GitHub Releases -- as
evidence for a claim such as "this shipped in version X" or "this behavior has been
stable since release Y." It exists because a release-history citation fails in ways
none of the general citation standards catch: a bare tag name is not itself a citable
string in this schema (see MUST 4), tag dates in this repository carry mixed UTC
offsets that break naive string sorting (see MUST 2), and "the current release" is a
moving target in a way a specific named release is not (see MUST 3).

## Scope and authority

**This node governs** how a claim in a corpus node's `evidence` ledger may cite Buzz's
own release/version history: which citation shape and evidence class a "shipped in
version X" or "stable since release Y" claim may honestly carry, how to compare or order
releases by date without a formatting artifact deciding the answer, and how a claim
about "the current release" must be distinguished from a claim about one specific named
release.

**Its authority comes from** `RELEASING.md` (the authoritative description of the three
release lanes and what each publishes), `standards/code-references.md` (the general
citation-shape rules this node narrows for one domain), and
`launchpad/project-intelligence/corpus/validate.py` (what the checker actually does with
any citation this node's claims would use). **Where this node and any of those three
disagree, they win** -- this node has drifted and should be fixed.

**It does not cover** general code-citation rules for non-release claims (owned by
`standards/code-references.md`), evidence classification in general (owned by
`standards/evidence.md`), how to cite an accepted decision such as an ADR (owned by
`standards/decision-references.md` -- this node applies that standard's intent/behaviour
split to one ADR in its own evidence ledger below, rather than restating the split), the
corpus's own recorded-revision provenance entry (owned by `standards/provenance.md`), or
`RELEASING.md`'s process content itself, which this node cites and does not repeat.

| For | Read |
|---|---|
| The three release lanes, their entry points and what each publishes | `RELEASING.md` |
| General rules for citing code/commits in a corpus evidence ledger | `launchpad/docs/corpus/standards/code-references.md` |
| Citing an accepted decision (an ADR) as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| What the checker does with any citation shape | `launchpad/project-intelligence/corpus/validate.py` |
| The general policy-node shape this document instantiates | `launchpad/docs/corpus/templates/policy.md` |
| A worked accepted decision about this repository's own tags | `launchpad/decisions/ADR-0041-pin-main-to-relay-desktop-tags.md` |

## MUST

| # | Requirement |
|---|---|
| **R1** | A claim that a feature or behavior "shipped in version X" MUST name the specific immutable release identity for its lane -- a `desktop-v<version>` tag, a `relay-v<version>` tag, or an exact `mobile-vX.Y.Z-rc.N` tag -- never a branch name, never "latest," and never a bare marketing version number with no lane or tag attached. `RELEASING.md`'s own Version Sources table is the reason: the three lanes version independently, so "version 0.5.12" alone does not say which artifact it names. |
| **R2** | Comparing or ordering two or more release tags by date MUST use each ref's unix timestamp (`%(creatordate:unix)`), never a lexicographic comparison of a formatted date string (`%(creatordate:iso)` or similar). This repository's own tags carry the tagger's local UTC offset, and mixed offsets break string ordering: `desktop-v0.5.12` (`13:54:39 -0600`) string-sorts before `mobile-v0.11.0-rc.2` (`14:31:30 +0000`), while the unix values (1786737279 vs 1786717890) place `mobile-v0.11.0-rc.2` first -- the true order. A count or "most recent" claim built on the string order is not a rounding error; it is the wrong tag. |
| **R3** | A claim about "the current release" or "the latest version" MUST record the date (or commit) it was checked as-of, in the claim's own `statement`, and MUST NOT be given the same evidentiary weight as a claim naming one specific tagged release. `RELEASING.md` documents `buzz-desktop-latest` as a rolling release whose `latest.json` "changes only through the manual promotion workflow" -- the target can move without this corpus being told, which a claim about a named, immutable `desktop-v<version>` tag cannot do. |
| **R4** | A bare tag name (`desktop-v0.5.18`) MUST NOT be used as a citation string on its own. It matches none of `validate.py`'s recognised citation shapes and falls through to the repository-path rule, where it is reported a hard error rather than an `UNVERIFIED` notice. Cite `commit <full-or-abbreviated-sha>` (naming the tag in the `statement` text) or a real repository file that documents the release (`RELEASING.md`, a per-lane `CHANGELOG.md`) instead. |
| **R5** | A changelog entry or a `chore(release)` commit message MUST NOT be treated, alone, as proof that the corresponding tag was actually created. A release-process commit landing in this repository's history does not guarantee every remote carries the matching tag -- verify the tag object directly (`git tag -l <name>` or `git ls-remote --tags <remote> <name>`) before citing "released as `<tag>`" as settled. |
| **R6** | A citation MUST name the correct lane's version authority for the claim it supports, and MUST NOT substitute one lane's authority for another's -- `crates/buzz-relay/Cargo.toml`'s version is not evidence for a desktop release claim, and a `desktop-v<version>` tag is not evidence for a relay or mobile one. |

## SHOULD

| # | Guidance |
|---|---|
| **Q1** | Prefer citing a real repository file (`RELEASING.md`, a per-lane `CHANGELOG.md`) over a GitHub Releases page URL. The file is resolved on disk and reported `ok`; a Releases page matches none of the checker's recognised GitHub file verbs (`blob`, `raw`, `tree`, `blame`, `commits`, `edit`) and is reported `unverified` -- the identical verdict any unrelated external link receives. |
| **Q2** | When a claim's real evidence is a specific tag (per R4, cited as `commit <sha>`), name the tag explicitly in the `statement` text. The citation alone cannot carry the tag name; a reader (or a future author re-verifying the claim) needs it written in prose to know what to re-check. |
| **Q3** | When citing an accepted decision about release tags (for example `ADR-0041`) as evidence, apply `standards/decision-references.md`'s intent/behaviour split explicitly: the decision is the right citation for what was authorized (which tags `main` is pinned to), and the wrong citation, alone, for what the repository's tags currently look like -- that needs a directly measured citation, per the FACTs recorded in this node's own ledger above. |

## Enforcement

**Nothing automated checks any requirement on this page.** `validate.py` never opens a
citation's target and compares it against the claim's `statement` (per `AGENTS.md`'s
"three things a passing run does not mean"), never computes or compares a date, and
never resolves a git tag to confirm it exists on any particular remote. Every MUST
above is upheld by the pull-request reviewer, not by a mechanical check.

**What a green `validate.py` run does NOT establish about a release-history claim**,
named here because R1-R6 are exactly the kind of requirement no schema field encodes:

| Not established | Consequence |
|---|---|
| That a cited tag name resolves to a real, existing ref on any remote | R1/R5's requirement is unchecked; a typo'd or invented tag name passes as a "commit" citation exactly like a real one, both landing on the same non-fatal `UNVERIFIED` notice |
| That a date comparison behind a claim used unix time rather than a formatted string | R2 is unchecked; a miscounted or mis-ordered release claim validates identically to a correct one |
| That "the current release" and a specific named release were not conflated | R3 is unchecked; nothing in the schema distinguishes a time-relative claim from a pinned one |
| That the correct lane's authority was cited | R6 is unchecked; a relay version cited for a desktop claim passes structurally |

**The one thing that is checked**, and only structurally: if a release-history claim
resolves to a `commit <sha>` citation (R4), `_COMMIT_CITATION_RE`'s shape is enforced --
`commit` followed by 7-40 hex characters -- and if it resolves to a repository-file
citation (`RELEASING.md`, a `CHANGELOG.md`), the file's existence on disk is enforced.
Neither check touches the claim's actual truth.

## Exceptions and escalation

**There is no exemption from R1-R6.** They describe what the release-history evidence
already available in this repository can honestly support; a claim that cannot meet one
of them is not ready to cite that evidence, not a candidate for a waiver.

**A SHOULD is departed from in the open, not silently.** If Q1-Q3 do not fit a
particular claim -- for example, no repository file documents a release still only
announced as a GitHub Release -- the author says so in the claim's own `statement` or in
this node's Scope and omissions, rather than quietly citing the weaker form without
comment.

**A disputed application of R1-R6 is a judgement, not an exception.** If an author and a
reviewer disagree about whether a given claim is "about the current release" (R3) or
about one specific named release, the author records the tension in the pull request and
the reviewer decides. A repeated disagreement is filed as an issue against this node.

**A case none of R1-R6 covers is escalated, not invented.** Raise it as an issue against
parent Feature #620, describing the release-history claim that was needed and could not
be honestly cited. Do not widen this policy locally to fit.

**`status: flagged` is `ADR-0029`'s mechanism for an unresolved evidence conflict, not a
substitute for meeting R1-R6.**

## Scope and omissions

**This node covers** how a corpus claim cites this repository's release/version
history -- named-release identity, date ordering, the current-vs-specific-release
distinction, the citable forms a tag actually supports, and the lane-authority
boundary -- and what a passing validation run does and does not establish about any of
it.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| General rules for citing code, commits and files in an evidence ledger | `standards/code-references.md` |
| Evidence classification (`FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`) in general | `standards/evidence.md` |
| Citing an accepted decision as evidence, and the intent/behaviour split | `standards/decision-references.md` |
| The corpus's own recorded-revision provenance entry | `standards/provenance.md` |
| `RELEASING.md`'s release process itself -- how a release is actually cut, reviewed and published | `RELEASING.md` |
| Whether this repository's own tags will ever be renamed or re-tagged in a way that changes the offsets cited in R2's evidence | not this node's to predict; R2's rule (compare by unix time) holds regardless |

**Whether this fork's `origin` remote is expected to eventually mirror every upstream
release tag, or whether the gap this node measured (`desktop-v0.5.19`/`desktop-v0.5.20`
present on `upstream` and absent from `origin` even after `git fetch origin --tags`) is
permanent fork behavior, was not established here.** It is recorded as a dated
observation supporting R5, not as a claim about why the gap exists or whether it will
close. That question belongs to whoever operates this fork's mirroring, not to this
corpus-authoring task.

**This node's own relationships.** Declared: `depends-on: corpus-agents` -- real and
resolvable on `origin/launchpad`, and a genuine dependency: this node's own authority for
creating/citing evidence at all is derived from `AGENTS.md`, not original to itself.
Declared: `implements: corpus-template-policy` -- real and resolvable; this node is a
policy-shaped instance of that template, carrying its six required sections. Declared:
`references: corpus-standard-code-references` -- real and resolvable; this node narrows
that standard's general citation rules for one domain (release tags) without restating
them. Declared: `references: corpus-standard-decision-references` -- real and
resolvable; this node's own evidence ledger applies that standard's intent/behaviour
split to `ADR-0041`. No edge to any other Feature #620 sibling (`agents/*.md`, other
`ingestion/*.md`): none besides `agents-invariants` is merged on `origin/launchpad` at
this node's authoring time, so none is a valid relationship target, per `AGENTS.md`'s
own "check before you justify it" warning.

**Evidence expectations specific to this node's subject.** The corpus-wide rules in
`AGENTS.md` apply unchanged. Two follow specifically from a release-history claim's own
shape: a claim about a *specific* named release (a tag) is stable evidence in the same
sense any pinned commit citation is -- it does not go stale merely because time passes;
a claim about "the current" or "the latest" release is evidence that goes stale the
moment a new one ships, and R3 exists because that difference is easy to lose once both
kinds of claim sit in the same evidence ledger looking equally confident.

**Expected but not verified when this node was written:**

- **No claim in this node's own ledger rests on a bare tag-name citation**, because R4
  establishes that form does not work; every tag-derived fact above is cited as a
  tool-result-shaped observation (`git_for_each_ref(...)`, `git_ls_remote(...)`) or as a
  bare repository path (`RELEASING.md`), never as `commit <sha>` -- this node had no
  occasion to exercise R4's own suggested citation form (`commit <sha>` naming a tag in
  prose) and has not tested it end to end.
- **No CI run has exercised this node.** All validator evidence above is local to this
  worktree.
- **Whether any other merged or future corpus node already makes a "shipped in version
  X" claim that violates R1-R6** was not audited; this node states the rule going
  forward and does not retroactively check the existing corpus against it.

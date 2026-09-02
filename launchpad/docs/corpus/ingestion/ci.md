---
id: ingestion-ci
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
  - statement: "The launchpad -- corpus validate workflow runs validate.py's unit tests and then the validator itself against the real corpus root, triggered on pull_request and on push to the launchpad branch, scoped to paths under launchpad/project-intelligence/corpus/**, launchpad/project-intelligence/requirements.txt, launchpad/docs/corpus/** and the workflow file itself -- so a local failure of the identical command is a CI failure for any corpus change."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "gh run list --repo launchpad-26/buzz --workflow=launchpad-corpus-validate.yml returned three real, completed runs (databaseId 33587159237, 33584645648, 33582802437), each with conclusion success and a distinct headSha; gh run view against the first returned full job and per-step timing and conclusion detail (job 'validate', seven named steps from checkout through 'Validate the real corpus')."
    entry_class: FACT
    evidence:
      - "gh_run_list(repo='launchpad-26/buzz', workflow='launchpad-corpus-validate.yml', limit=3) -> 3 runs, all conclusion=success"
      - "gh_run_view(run_id=33587159237, repo='launchpad-26/buzz') -> job 'validate', 7 named steps, all conclusion=success, headSha=848155845d45b6d0d16d53cd19df6e08eb2b342e"
  - statement: "AGENTS.md's citation-shape table classifies a tool result as UNVERIFIED -- nothing on disk to open, nothing the checker can check -- and validate.py implements no citation form specific to a CI run, a check conclusion, or a workflow-dispatch result; any such citation is classified through the same generic tool-result, commit, or URL branches used for any other command output."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
      - "grep_repo(pattern='workflow_run|check_run|ci_result|actions/runs|github actions', scope='launchpad/project-intelligence/corpus/validate.py') -> 0 matches"
  - statement: "A GitHub Actions run URL (https://github.com/<owner>/<repo>/actions/runs/<id>) does not match validate.py's repository-file-link pattern -- which requires a blob, raw, tree, blame, commits or edit view segment naming a file -- so it falls through to the generic external-URL branch and is reported UNVERIFIED, identically to a non-GitHub URL or an issue/pull-request link."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py:553-565"
  - statement: "This repository sets an explicit, short, and varying retention-days on every uploaded GitHub Actions artifact found: .github/workflows/ci.yml's desktop-e2e-relay artifact is 1 day, .github/workflows/linux-canary.yml, windows-canary.yml and signed-macos-canary.yml's canary packages are each 7 days, and .github/workflows/sprig.yml's workflow artifact is 30 days -- none is left at GitHub's own longer default, and none is unlimited."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml:408"
      - ".github/workflows/linux-canary.yml:265"
      - ".github/workflows/windows-canary.yml:172"
      - ".github/workflows/signed-macos-canary.yml:233"
      - ".github/workflows/sprig.yml:106"
  - statement: "linux-canary.yml, windows-canary.yml and signed-macos-canary.yml each open with a header comment stating, in near-identical words, that the workflow's own build output is 'available ... as a short-lived GitHub Actions artifact for explicit testing' rather than a durable release -- this repository's own authors already describe CI-produced output as ephemeral by design, independent of and prior to this node making the same observation."
    entry_class: FACT
    evidence:
      - ".github/workflows/linux-canary.yml:4-5"
      - ".github/workflows/windows-canary.yml:4-5"
      - ".github/workflows/signed-macos-canary.yml:4-5"
  - statement: "AGENTS.md documents the one permitted exception to 'a FACT MUST rest on at least one citation the validator can open': the single evidence entry recording the node's own checked revision, which cites a commit and nothing else because the citation is the claim -- and states this exception is narrow, applying to no other claim."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "corpus-standard-evidence's MUST 4 requires a FACT to rest on at least one citation the validator can open, with exactly the same one exception, and its MUST 5 requires a node to carry at most one commit-only FACT -- both stated generically, not scoped to any particular tool-result source such as CI."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/evidence.md"
  - statement: "corpus-standard-test-references states that a test's pass is 'not a timeless fact about the system; it is an observation at a moment, of one invocation, that may or may not repeat', and that a FACT about current behavior resting on a test's pass MUST be grounded near the node's recorded revision, not on a historical pass -- the same reasoning this node applies to a CI run's conclusion, generalized past testing specifically to any CI-produced result."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/test-references.md"
  - statement: "corpus-standard-code-references governs the mechanics of citing a file in this repository -- a bare repository path, a path:line position, a pinned GitHub blob link -- and states plainly that a file in this repository MUST NOT be cited as a GitHub link when a repository path would name the same file, because the path form is checked against the filesystem and the link form only against a regular expression; a workflow YAML file under .github/workflows/ is such a file, and this node's preference for citing it by path rather than by a GitHub link to the same file follows directly from that existing rule rather than inventing a new one."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/code-references.md"
  - statement: "ADR-0029 names passing tests, alongside code, configuration and schema, as executable evidence authoritative for a claim about how the system currently behaves, and requires that GitHub history, team knowledge and inference are never treated as fact on their own -- a CI run's conclusion is drawn from that same family of executable evidence, subject to the same discipline: authoritative for current behavior at the moment it ran, never a substitute for opening the workflow definition that produced it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Feature #620's body describes 32 child document tasks under agents/*.md and ingestion/*.md, states that implementation of a knowledge-crate ingestion pipeline runtime is out of scope, and frames the ingestion/ family as documenting how an agent draws evidence from each kind of source -- git history, issues, PRs, commits, CI -- when authoring a corpus node, not a data-ingestion pipeline this repository runs."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#620 body"
  - statement: "Issue #953's own Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and exception/escalation process, and link decisions or higher-order policy instead of duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#953 definition of done"
  - statement: "This node declares no relationship to any other Feature #620 sibling task besides the already-merged agents-invariants, and does not target agents-invariants either, because that node's subject -- general node-authoring invariants (I1-I10) -- is not CI-specific and this node's own dispatch instructions named the general batch practice of not targeting in-flight or newly-merged siblings during parallel authoring; every other relationship target this node declares (corpus-agents, corpus-standard-evidence, corpus-standard-code-references, corpus-standard-test-references) was independently confirmed present via git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus at the recorded revision, not assumed from this node's own dispatch brief."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "the batch dispatch brief for issue #953, and git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') run at this node's recorded revision"
relationships:
  - type: depends-on
    target: corpus-agents
  - type: depends-on
    target: corpus-standard-evidence
  - type: references
    target: corpus-standard-code-references
  - type: references
    target: corpus-standard-test-references
---

# Policy: citing a CI result as evidence

This node states what MUST and SHOULD govern citing a CI result -- a workflow run, a
check's pass/fail, a build or lint log -- as evidence for a claim in a corpus node's
`evidence` ledger. It exists because a CI result is always the least-verifiable citation
shape the corpus recognizes (`UNVERIFIED`, nothing the checker opens) and, distinctly, one
of the least *permanent*: this repository's own workflows delete the artifacts a CI run
produces within days, not years, unlike a file the corpus can cite by path and expect to
still be there at the next revision.

## Scope and authority

**This node governs** citing a CI result as evidence: which claim such a citation can
actually support, which citation shape fits which of those claims, why a CI result is
ephemeral in a way a committed repository file is not, and what follows from that for
classification and phrasing. It applies to any corpus node, on any subject, that reaches
for "CI enforces this," "this workflow run showed X," or "this check passed" as its
evidence -- not only to nodes about the corpus itself.

**Its authority comes from** its own task's definition of done (#953, under parent
Feature #620), which asks this node to state scope and authority, separate MUST from
SHOULD, define enforcement and an escalation process, and link rather than duplicate
higher-order policy. The MUST/SHOULD rules below are this document's own normative
statements issued under that delegation, not findings derived from a source -- the same
authority basis `corpus-standard-evidence` and `corpus-standard-test-references` each
state for themselves.

**It does not re-govern the general mechanics already owned elsewhere**, and this is the
boundary to read before drafting a citation:

| Subject | Owned by |
|---|---|
| The tool-result and commit citation shapes in general, evidence classification (`FACT`/`INFERENCE`/`TEAM_KNOWLEDGE`), what `UNVERIFIED` means, and the one permitted commit-only-`FACT` exception | `corpus-standard-evidence` |
| Citing a file in this repository -- bare path resolution, `path:line` positions, pinned GitHub links, and why a path beats a link to the same file | `corpus-standard-code-references` |
| Citing a **test** specifically -- existence vs. run-result vs. current-behavior claims, and this repository's own flaky-retry signal | `corpus-standard-test-references` |
| Creating, updating and retiring any corpus node procedurally | `launchpad/docs/corpus/AGENTS.md` |
| How conflicting evidence is ranked, and why passing CI counts as evidence at all | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |

What is left, and what this node actually adds, is the part specific to **CI** as the
thing being cited: which of the shared shapes fits which CI-shaped claim, and the
ephemerality discipline neither `corpus-standard-evidence` nor `corpus-standard-code-references`
states, because neither is about a result that this repository's own workflows delete
within days.

**Where this node and any of the documents in that table disagree, they win** -- this one
has drifted and should be fixed.

## What "CI" means here, concretely

There is no knowledge-crate ingestion pipeline that consumes CI events; Feature #620
states that runtime is out of scope. "CI" in this node means the ordinary thing: a
GitHub Actions workflow defined under `.github/workflows/*.yml`, its individual jobs and
steps, and the runs it produces on `pull_request` and `push`. The concrete example this
node was checked against is `.github/workflows/launchpad-corpus-validate.yml` itself --
the workflow that validates this very corpus, triggered on `pull_request` and on `push`
to `launchpad`, scoped to `launchpad/project-intelligence/corpus/**`,
`launchpad/project-intelligence/requirements.txt`, `launchpad/docs/corpus/**` and the
workflow file itself. `gh run list --repo launchpad-26/buzz --workflow=launchpad-corpus-validate.yml`
and `gh run view <id>` were both exercised against it while drafting this node and
returned real, dated, per-job and per-step data -- confirming what a CI citation could
name, and, separately, that none of that data lives inside this repository's own git
history.

## Which claim is a CI citation actually making?

The same workflow run can sit under different claims, and, exactly as
`corpus-standard-test-references` found for a test, conflating them is the specific
failure this node exists to prevent:

| The claim | Example statement | The right shape |
|---|---|---|
| **A check exists** that enforces some rule going forward | "CI validates every corpus change against the schema." | Bare repository path to the workflow file (e.g. `.github/workflows/launchpad-corpus-validate.yml`) |
| **A specific run occurred and produced a result** | "Run 33587159237 of the corpus-validate workflow passed against headSha 848155845d..." | Tool-result citation, or the run's URL -- both `UNVERIFIED` |
| **The system currently behaves a certain way**, using a CI pass as the evidence | "The corpus validates cleanly at this node's recorded revision." | Tool-result citation naming the run, grounded at or near the recorded revision, per *Current behavior and ephemerality* below |

A `FACT` that a workflow *exists and is wired to run* proves nothing about whether any
particular run of it passed; a `FACT` that one run *passed once* is not, by itself, the
same claim as "the system behaves this way now." The middle row is also the row a reader
should expect to become unopenable soonest -- see the next section.

## Current behavior and ephemerality

**A committed file and a CI run are not the same kind of evidence, and the difference is
not merely that one is `UNVERIFIED` and the other might be `FACT`.** Both a workflow
result and a repository path can be cited honestly; what differs is how long the cited
thing is expected to still be there.

A bare repository path -- `.github/workflows/launchpad-corpus-validate.yml` -- is checked
into git. It has full history, survives as long as the repository does, and a future
reader opens the identical file `validate.py` resolves today (modulo the file having
since changed, which is a separate, ordinary staleness concern every code citation
carries). A specific CI run's logs and artifacts carry no such guarantee **in this
repository, concretely**: every uploaded artifact this node found sets an explicit, short
`retention-days` -- 1 day for `ci.yml`'s desktop E2E relay build, 7 days for each of the
three canary packages, 30 days for `sprig.yml`'s workflow artifact -- and three of those
same canary workflows say so about themselves in their own header comments, calling their
own output "a short-lived GitHub Actions artifact for explicit testing," not a durable
release. Nothing here asserts a specific retention window for a **workflow run's own
logs** as opposed to an uploaded artifact -- that is a platform/organization setting this
node did not verify; see *Scope and omissions*. What is verified, directly, is that this
repository's authors already treat CI-produced output as short-lived by design, and a
corpus node citing a CI result inherits that same ceiling whether or not any particular
run happens to still be viewable when a reader checks.

That asymmetry is why a `FACT` about current behavior resting on a CI pass needs the same
discipline `corpus-standard-test-references` states for a test's pass, generalized past
testing: it is an observation at a moment, of one run, that may or may not still be open
to a reader by the time they check it -- and, unlike a test file sitting in the tree
today, the run itself may already be gone.

## MUST

1. **A claim that CI enforces some rule going forward MUST cite the workflow file
   itself**, as a bare repository path (`corpus-standard-code-references` governs the
   path mechanics; this rule only says which claim needs which target). Citing a specific
   run for this claim substitutes an ephemeral, one-time result for the durable thing that
   actually keeps enforcing the rule after that run is gone.
2. **A claim that a specific CI run occurred and produced an observed result MUST use a
   tool-result citation or the run's URL**, and MUST NOT be classified `FACT` on the
   strength of that citation alone being present -- both shapes are `UNVERIFIED` per
   `corpus-standard-evidence`; the run's own conclusion was not opened by anything the
   validator does, and a repository-link pattern match on a GitHub Actions run URL fails
   for the same reason it would for any other URL the pattern does not recognize as a file
   view: it names no file to open.
3. **A CI-result citation MUST NOT be used as the one permitted commit-only-`FACT`
   exception `corpus-standard-evidence` names.** That exception is reserved for the single
   entry recording *this node's own* checked revision, because there the citation is the
   claim. A CI run's conclusion is a claim *about* something else -- the corpus, the code,
   a check -- and needs its own citation on its own merits, not a borrowed exemption.
4. **A `FACT` about current system behavior that cites a CI pass as its evidence MUST be
   grounded at or near the node's recorded revision**, not on a historical run against an
   earlier commit. `corpus-standard-test-references`' MUST 5 states the identical rule for
   a test's pass; this node applies it without restating the reasoning, because nothing
   about it is specific to testing rather than CI generally.
5. **When a specific run is cited, the citation MUST name that run explicitly** -- the
   full run URL or an unambiguous tool-result invocation such as
   `gh_run_view(run_id=33587159237) -> conclusion: success` -- never an unqualified "CI
   passed." An unqualified claim gives a reader nothing to check even while the run is
   still viewable, and nothing to reconstruct once it is not.
6. **When a specific run is cited, the `statement` MUST note that the citation may not
   remain openable**, rather than silently relying on the reader never checking. Node
   front matter has no field for this caveat -- `corpus-standard-test-references`' MUST 8
   states the identical constraint for a test-run reliability caveat, and it applies
   here unchanged: omitting the caveat from the `statement` is the same as not recording
   it.
7. **A CI-result-only claim MUST NOT be worded to imply it is more durable than the log
   or artifact it depends on.** Where this repository's own retention window is known
   (an uploaded artifact's `retention-days`), prefer naming it in the `statement` over
   leaving durability unstated.

## SHOULD

1. **Prefer citing the workflow file over a specific run whenever the claim is about
   what CI enforces, not about one occurrence.** The file survives; the run may not.
2. **When citing a specific run, record enough context in the `statement` that the claim
   still means something after the run itself becomes unopenable** -- the workflow name,
   the date, and the commit SHA the run validated, not only a bare run ID or URL.
3. **Prefer a permanent, committed source over a CI result when both could support the
   same behavioral claim.** A config value, a schema constraint, or an assertion actually
   read in a test file outlasts any run that happened to exercise it once; reach for the
   CI result only when the behavior genuinely cannot be established by opening something
   that stays in the tree.
4. **Do not cite a bare `#<run-id>` or a check name alone.** Use the full run URL or a
   tool-result form naming the workflow and run explicitly, per MUST 5 -- the same
   discipline `corpus-standard-code-references`' MUST 7 requires for an issue or pull
   request, applied here to a run identifier for the identical reason: a bare number
   matches no recognized citation shape and, unlike an issue or PR, has no stable web
   address a reader can reconstruct from the number alone without also knowing the
   workflow and repository.

## Enforcement

**Nothing in `validate.py` is specific to a CI-result citation.** It is classified through
the same generic branches used for any tool result, commit reference, or URL: a
`gh_run_view(...) -> ...` form matches the tool-result pattern and is reported
`UNVERIFIED`; a GitHub Actions run URL matches no repository-file-link pattern and falls
through to the generic external-URL branch, also `UNVERIFIED`; a bare workflow-file path is
checked exactly as any other repository path, `ok` if it resolves. Nothing about this is
mechanically enforced beyond what `corpus-standard-evidence` and
`corpus-standard-code-references` already enforce for those shapes in general.

**What a green validation run does NOT establish about a CI-result citation**, stated here
because MUSTs 1 through 7 above are enforced by review only:

| Not established | Consequence |
|---|---|
| That a cited run actually occurred, or produced the conclusion the statement claims | `UNVERIFIED` is printed and the run still exits 0 either way |
| That the workflow file cited for MUST 1 still performs the same check it did at the recorded revision | A workflow's own YAML can change like any other code; the path resolving proves the file exists, not that its current content matches |
| That a citation naming a specific run also disclosed its non-permanence (MUST 6) | Nothing reads the `statement`'s prose; a citation naming a run without the caveat validates identically to one that includes it |
| That a claim about current behavior was grounded near the recorded revision rather than an old run (MUST 4) | Nothing compares a citation's implied date against the node's own recorded revision |

**Enforcement is the pull-request review**, exactly as `corpus-standard-evidence` and
`corpus-standard-test-references` each state for their own review-only halves. This node
gives that reviewer a specific thing to check for a CI-shaped citation: does the claim
match one of the three rows in *Which claim is a CI citation actually making?*, and, if it
names a specific run, does the `statement` say so honestly and note the run may not stay
retrievable.

## Exceptions and escalation

**There is no exemption from MUSTs 1 through 7.** They restate and specialize rules
`corpus-standard-evidence` already enforces generically (the `UNVERIFIED` treatment, the
single commit-only-`FACT` exception, current-behavior grounding) plus this node's own
CI-specific ephemerality rules; a node that cannot meet them is not a candidate for an
exception under this document.

**When the only available evidence for a claim is a since-expired CI run** -- an artifact
past its `retention-days` window, or a run whose logs are simply no longer viewable --
withdraw the claim rather than citing a run nobody can open to check, per
`corpus-standard-evidence`'s own *Three outcomes, not two* for a claim that cannot honestly
sit in any class. Record the gap in *Scope and omissions* instead.

**A disputed application of these rules is a judgement, not an exception.** The author
records the tension in the pull request; the reviewer decides. A repeated disagreement is
filed as an issue against this node, because a rule two people read differently is a
defect in the rule.

**A case none of MUSTs 1 through 7 covers is escalated, not invented.** Raise it as an
issue against parent Feature #620, describing the CI-citation shape that seemed to be
missing and why existing tooling or the general standards did not already cover it.

## Scope and omissions

**This node covers** which claim a CI-result citation supports, which of the shared
citation shapes fits which CI-shaped claim, why a CI result is ephemeral in this
repository concretely (uploaded-artifact `retention-days`, the canaries' own "short-lived"
language) and not merely `UNVERIFIED` in the abstract, and the MUST/SHOULD rules that
follow from both.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The tool-result and commit citation shapes in general, and evidence classification | `corpus-standard-evidence` |
| Citing a file in this repository generally -- path resolution, pinning, GitHub links | `corpus-standard-code-references` |
| Citing a **test** specifically, and this repository's test-flakiness signal | `corpus-standard-test-references` |
| Whether GitHub's own platform/organization-level retention setting for a workflow **run's logs** (as opposed to an uploaded artifact's explicit `retention-days`) is documented anywhere for this repository | Not established here -- no committed file governs it, and asserting a number without opening a primary source would be exactly the unsupported claim `corpus-standard-evidence` warns against |
| A knowledge-crate ingestion pipeline that consumes CI events as data | No such runtime exists; Feature #620 states it is out of scope |
| Naming, identifiers, taxonomy, status, diagrams and the remaining per-type templates | somewhere in #1307-#1351 |

**This node's own relationships.** Declared: `depends-on` toward `corpus-agents` and
toward `corpus-standard-evidence` -- both real and resolvable on `origin/launchpad` at the
recorded revision (confirmed by `git ls-tree -r --name-only origin/launchpad --
launchpad/docs/corpus`), and genuine dependencies: this node's MUSTs 2, 3 and 4 restate
and specialize rules those two documents already state generically, so a change to either
document's `UNVERIFIED`/commit-only-`FACT` treatment would require revisiting this node's
own rules. Declared: `references` toward `corpus-standard-code-references` and toward
`corpus-standard-test-references` -- both also resolvable, and supporting context rather
than dependencies: this node's claims would not break if either document's own specific
mechanics changed, but a reader comparing a CI-file citation against a test-run citation
benefits from being pointed at both. No edge to `agents-invariants`, the one other
Feature #620 sibling merged at this node's recorded revision: its subject (general
node-authoring invariants I1-I10) is not CI-specific, and this node's own dispatch
instructions named the practice of not targeting in-flight or freshly-merged siblings
during this batch's parallel authoring.

**Expected but not verified when this node was written:**

- **No corpus node yet cites a CI result as evidence of any claim.** Everything above is
  derived from `validate.py`'s own citation-classification behavior (read, not newly
  exercised beyond the `gh run list`/`gh run view` calls recorded in the ledger), from
  this repository's real workflow files, and from the sibling standards' own stated rules
  -- not from a worked example already inside the corpus.
- **Whether GitHub's platform-level retention window for a workflow run's logs (distinct
  from the artifact `retention-days` this node did verify) is configured anywhere for this
  organization or repository** was not established. No committed file was found governing
  it, and no attempt was made to look it up outside the repository, since a platform
  default not evidenced by anything this repository controls would not be a citable FACT
  about this repository.
- **No CI run has exercised this node.** The `gh run list`/`gh run view` evidence above is
  about the corpus-validate workflow generally, gathered while researching this node's own
  subject -- it is not a validation run of this node itself, which has not yet been
  through CI.

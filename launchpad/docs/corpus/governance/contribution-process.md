---
id: governance-contribution-process
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "launchpad/AGENTS.md declares itself the normative spec for how work is filed, reviewed and merged in this fork, and states that it supersedes the root CLAUDE.md and AGENTS.md for anything under launchpad/, .github/workflows/launchpad-*, and all cohort process work."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 1 states 'We operate Buzz. We do not develop Buzz.' and routes genuine upstream product bugs to block/buzz/issues rather than to this fork."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: ".github/ISSUE_TEMPLATE/config.yml sets blank_issues_enabled: false and offers three contact links -- a private security advisory form, launchpad/AGENTS.md, and block/buzz/issues described as where upstream product bugs go -- so the fork-versus-upstream routing is stated on the issue chooser page itself."
    entry_class: FACT
    evidence:
      - ".github/ISSUE_TEMPLATE/config.yml"
  - statement: "launchpad/AGENTS.md section 4 enumerates six issue types in a first-yes-wins order -- ADR, Bug, Enhancement, PRD, Feature, Task -- and requires exactly one type: label per issue."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: ".github/workflows/launchpad-issue-check.yml runs on issues opened, edited, labeled and unlabeled; it fails when an issue carries zero or more than one type: label, and it carries a REQUIRED map naming the '### Heading' sections each of the six types must have present and non-empty."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-issue-check.yml"
  - statement: "On failure the issue body check adds the needs-triage label and posts a comment naming each missing or empty section, then exits 1; on success it removes needs-triage."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-issue-check.yml"
  - statement: "The issue body check requires a type:bug issue to contain a fenced code block, rejecting a paraphrase of raw output."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-issue-check.yml"
  - statement: "Each .github/ISSUE_TEMPLATE/*.yml form declares its own type: label in a labels: list and opens with an AGENT INSTRUCTIONS comment block; 02-task.yml declares labels: [\"type:task\"] and instructs that a Task lands in its parent Feature's batch pull request rather than a pull request of its own."
    entry_class: FACT
    evidence:
      - ".github/ISSUE_TEMPLATE/02-task.yml"
  - statement: "launchpad/AGENTS.md records that issue-form template labels apply only through the web UI, so an ADR filed with gh issue create does not receive the needs-decision label its template declares and must have it added explicitly."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 6 prescribes branching from the launchpad branch, committing with git commit -s, and opening the pull request with --base launchpad."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "The repository's default branch is launchpad, it is a fork whose parent is block/buzz, allow_squash_merge and allow_rebase_merge are both false while allow_merge_commit is true, merge_commit_title is MERGE_MESSAGE and merge_commit_message is PR_TITLE."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz') -> default_branch=launchpad, fork=true, parent=block/buzz, allow_squash_merge=false, allow_rebase_merge=false, allow_merge_commit=true, merge_commit_title=MERGE_MESSAGE, merge_commit_message=PR_TITLE"
  - statement: "ADR-0055 settles merge commit as the only merge method for this fork and ADR-0054 withdrew ADR-0052 part C's size cap so that one Feature lands in one pull request whatever its size; both decision records exist under launchpad/decisions/."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0055-merge-commit-is-the-merge-strategy.md"
      - "launchpad/decisions/ADR-0054-one-feature-one-pr-no-size-cap.md"
  - statement: "lefthook.yml's commit-msg hook runs a single command that appends a Signed-off-by trailer with git interpret-trailers --if-exists doNothing, and its own comment states this appends the trailer the required 'DCO Check' enforces."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "lefthook.yml's own comment records that Git runs commit-msg only for git commit and git merge, so git rebase --signoff and git cherry-pick -s are needed for those flows."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "CONTRIBUTING.md states that every commit needs a DCO sign-off and that 'The DCO Check will block your PR without it'."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "No check named 'DCO Check' appears in the status check rollup of launchpad-26/buzz pull requests 1997, 1978, 1970 or 1941, while 'DCO Check' does appear in the rollup of block/buzz pull request 7214 -- the DCO app reports on the upstream repository and not on this fork."
    entry_class: FACT
    evidence:
      - "gh_pr_view(repo='launchpad-26/buzz', numbers='1997,1978,1970,1941', field='statusCheckRollup') -> no check named DCO Check in any of the four rollups"
      - "gh_pr_view(repo='block/buzz', number=7214, field='statusCheckRollup') -> DCO Check present"
  - statement: "lefthook.yml defines five pre-commit lanes (rust-fmt, desktop-tauri-fmt, desktop-fix, web-fix, mobile-fmt), one commit-msg lane (signoff), and nine pre-push lanes (branch-skew, push-head-scope, file-size-check, rust-tests, desktop-check, desktop-typecheck, desktop-test, desktop-tauri-checks, mobile-checks)."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "The Justfile's hooks recipe installs the git hooks using the Hermit-pinned lefthook in bin/ rather than whatever lefthook happens to be on PATH."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "No lefthook pre-push lane runs workspace-wide clippy: rust-tests runs just test-unit, and the only clippy invocation in the file is just desktop-tauri-clippy inside the desktop-tauri-checks lane, which is globbed to desktop/src-tauri and the Rust build inputs."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "Every globbed pre-push lane sets files: git diff --name-only origin/main...HEAD, so its file set is the branch's merge-base diff against origin/main rather than against this fork's launchpad base branch."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "Three pre-push lanes are unglobbed and therefore run on every push regardless of what changed: branch-skew, which runs launchpad/scripts/check-branch-skew.sh, file-size-check, which runs just file-size-check, and push-head-scope, which runs scripts/check-push-head-scope.sh -- but only the first two can fail a push; push-head-scope is warn-only and never fails one."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "launchpad/scripts/check-branch-skew.sh is the cohort variant of the upstream skew guard because the upstream script assumes origin/main is the pull request base, which is not true in this fork; it searches every configured remote for a ref named launchpad and exits 0 immediately when the checked-out branch is launchpad or HEAD."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/check-branch-skew.sh"
  - statement: "just file-size-check runs node --test on scripts/check-file-sizes-core.test.mjs followed by the desktop, web and mobile check-file-sizes.mjs scripts; it covers no path under launchpad/."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: ".github/workflows/ci.yml triggers on push to main and release and on every pull_request, and gates almost every job behind a dorny/paths-filter changes job whose filters name crates/, desktop/, web/, mobile/ and the Rust build inputs -- no filter names launchpad/."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: "On launchpad-26/buzz pull request 1997, which changed lefthook.yml only, every path-filtered ci.yml job reported SKIPPED while Detect Changed Paths and Dead Token Reference Guard ran, confirming that a cohort-only change executes almost none of ci.yml."
    entry_class: FACT
    evidence:
      - "gh_pr_view(repo='launchpad-26/buzz', number=1997, field='statusCheckRollup') -> Rust Lint, Unit Tests, Desktop Core, Web, Mobile, Security and the remaining path-filtered jobs all SKIPPED; Detect Changed Paths and Dead Token Reference Guard SUCCESS"
  - statement: "ci.yml's dead-token-guard job carries no needs: changes condition and no if:, so it runs on every pull request regardless of which paths changed."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
  - statement: ".github/workflows/launchpad-pr-check.yml runs on pull_request opened, edited, reopened, labeled, unlabeled, synchronize and ready_for_review; its check job asks GitHub's GraphQL closingIssuesReferences for the issues the pull request closes and the sub_issues REST endpoint for the named Feature's children, then runs launchpad/scripts/pr_body_check.py."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-pr-check.yml"
  - statement: "launchpad-pr-check.yml carries a second job, scripts, which runs the launchpad/scripts unit suite and then launchpad/scripts/mutation_harness.py, whose stated purpose is to prove the controls can fail."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-pr-check.yml"
  - statement: "launchpad/scripts/pr_body_check.py's check() rejects an empty body, a missing or unrecognised '### Issue type' section, a reference problem reported by check_reference, and a batch-membership problem reported by check_batch; for an agent-authored body it additionally requires every provenance table field to carry a value, a non-empty and specific '### Not verified' section, and at least one fenced code block."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/pr_body_check.py"
  - statement: "pr_body_check.py keys its strict checks on the body as well as the label: looks_agent_authored() switches them on, and a body carrying agent provenance or an Authority claim without the by:agent label is itself an error, so removing the label does not remove the requirements."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/pr_body_check.py"
  - statement: "The PR body check asks GitHub which issues a pull request closes rather than pattern-matching the body, because a regex cannot distinguish a real reference from one written inside code; an empty answer is read as 'unknown' rather than 'none' and reported as unverified."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-pr-check.yml"
      - "launchpad/scripts/pr_body_check.py"
  - statement: ".github/workflows/launchpad-adr-check.yml is deliberately unfiltered by path so that it can be marked required without stalling pull requests that do not touch the ADR, and it fails closed when its checker, ADR-0005 or launchpad/AGENTS.md is missing from the commit under check."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
  - statement: "launchpad/scripts/adr_boundary_check.py checks only ADR-0005's deployment-image-provenance list -- that the ADR's table, the ADR's prose count and launchpad/AGENTS.md section 3's entry name the same files, and that each sanctioned file actually carries a Launchpad value -- so it does not check the rest of section 3's upstream-boundary rules."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/adr_boundary_check.py"
  - statement: ".github/workflows/launchpad-corpus-validate.yml runs on pull requests and on pushes to launchpad that touch launchpad/docs/corpus/**, launchpad/project-intelligence/corpus/**, that suite's requirements file, or the workflow itself; it runs the unit tests and then the validator against the real corpus tree."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The launchpad-* workflow family contributes these job identifiers to a pull request: adr-boundary, check and scripts (PR body check), validate (corpus validate), tests (agents, corpus schema and review-queue-automation suites), controls (review agent containment), guard and publish (review agent publish), and audit (security audit)."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-adr-check.yml"
      - ".github/workflows/launchpad-pr-check.yml"
      - ".github/workflows/launchpad-corpus-validate.yml"
      - ".github/workflows/launchpad-security-audit.yml"
  - statement: ".github/workflows/launchpad-security-audit.yml is unfiltered by path on pull_request because a leaked credential is as real in crates/ or desktop/ as under launchpad/, and it also runs on a daily schedule and on workflow_dispatch."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-security-audit.yml"
  - statement: "The branch launchpad reports protected: true, while the repository ruleset list and the effective rules for that branch are both empty, and the legacy branch-protection endpoint returns 404 for a token whose repository permissions are maintain rather than admin."
    entry_class: FACT
    evidence:
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad') -> name=launchpad, protected=true"
      - "gh_api('repos/launchpad-26/buzz/rulesets') -> empty list"
      - "gh_api('repos/launchpad-26/buzz/rules/branches/launchpad') -> empty list"
      - "gh_api('repos/launchpad-26/buzz/branches/launchpad/protection') -> HTTP 404 Not Found; repository permissions admin=false, maintain=true"
  - statement: "Pull request 1997 merged on 2026-08-31 with the launchpad PR body check reporting FAILURE, so no status check blocked that merge."
    entry_class: FACT
    evidence:
      - "gh_pr_view(repo='launchpad-26/buzz', number=1997, fields='state,mergedAt,statusCheckRollup') -> MERGED at 2026-08-31T22:00:25Z with check=FAILURE from the launchpad PR body check workflow"
  - statement: "launchpad/AGENTS.md section 6 records a 2026-08-28 measurement of the launchpad branch's protection: one approving review required, dismiss_stale_reviews on, required_status_checks empty, enforce_admins off, and push restricted to 11 users."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad/AGENTS.md section 6, recording a measurement taken 2026-08-28"
  - statement: ".github/CODEOWNERS assigns every path to @block/buzz-oss-team, an upstream organisation team rather than a launchpad-26 one."
    entry_class: FACT
    evidence:
      - ".github/CODEOWNERS"
  - statement: "launchpad/AGENT_PR_TEMPLATE.md is a schema an agent fills and submits with gh pr create -F, not a body pasted with --template, and it forbids adding or removing headings, requires N/A - <reason> for an inapplicable field, and forbids the words 'tests pass' or 'verified' in place of raw command output."
    entry_class: FACT
    evidence:
      - "launchpad/AGENT_PR_TEMPLATE.md"
  - statement: ".github/PULL_REQUEST_TEMPLATE.md carries Summary, Feature, Related issue, Issue type, Testing, Authority and Deferred blockers sections and ends with a comment directing agent-authored pull requests to launchpad/AGENT_PR_TEMPLATE.md instead."
    entry_class: FACT
    evidence:
      - ".github/PULL_REQUEST_TEMPLATE.md"
  - statement: "launchpad/AGENTS.md section 6 states that a defect found while preparing or reviewing a batch is filed as a child of that pull request's Feature, labelled deferred-blocker and named in the pull request body, and that four classes are never deferrable: a credential, secret or password hash in the diff; a disclosure-boundary violation; a failing deterministic check; and anything that leaves launchpad broken for other agents."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 8 forbids opening a public issue for a vulnerability and directs the reporter to the private advisory link on the issue chooser page."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 6 requires gh repo set-default launchpad-26/buzz once per clone, because without it gh resolves to the parent repository block/buzz for any command with no explicit --repo."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "CONTRIBUTING.md states 'We squash-merge, so your PR title becomes the commit subject in main', directs contributors to open issues at block/buzz, and describes a Table of Contents built around Rust crates, event kinds, MCP tools and API endpoints."
    entry_class: FACT
    evidence:
      - "CONTRIBUTING.md"
  - statement: "The corpus already carries a standard stating what a reviewer of a pull request touching launchpad/docs/corpus/** must additionally check, so corpus pull requests inherit a review step narrower than this node's."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "launchpad/AGENTS.md section 6 requires activating the Hermit toolchain with . ./bin/activate-hermit before running any git command, because the hooks otherwise fail on PATH."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "lefthook.yml's rc: bin/.lefthookrc line points the generated .git/hooks dispatchers at a file that sets LEFTHOOK_BIN to the Hermit-pinned binary and prepends the repository's Hermit bin/ to PATH, so a hook's lane subprocesses resolve the pinned toolchain even from an unactivated shell."
    entry_class: FACT
    evidence:
      - "lefthook.yml"
  - statement: "launchpad/AGENTS.md section 6 states that a Feature may not close while it holds open deferred-blocker issues and that a Feature holding more than five has its next batch refused; it also directs agents to prefer gh pr merge --auto and not to approve or merge while checks are failing or still running."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 4's 'When to raise at all' sets the filing threshold -- a small fix in a file already being touched is made and noted in the pull request body, anything else gets an issue -- and its section 5 rule 2 requires an unclear type to be filed as a Task with needs-triage and the ambiguity stated in Objective."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md section 5 records the event ADR-0052 cites as its motivation: on 2026-08-28, 132 pull requests were merged with --admin past 77 changes-requested reviews and unresolved CI."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
  - statement: "ADR-0019 is marked 'Superseded by ADR-0052' in its own front matter, and rules that a required status check may only ever be a deterministic script, that a human approval remains required always, and that marking checks as required is deferred until the CI/CD pipeline programme lands -- so issues #153 and #146 stay open by decision rather than by obstruction."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
  - statement: "ADR-0019 records that enforce_admins stays off as a deliberate acceptance, and names the four repository admins measured 2026-08-24 as able to bypass required checks once such checks exist."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
  - statement: "Because ci.yml's path filters name no directory under launchpad/ and the launchpad-* workflows are the only ones that run unconditionally on a cohort-only pull request, the machine-checkable surface for a documentation or process change in this fork is the PR body check, the ADR boundary check, the security audit, the dead-token guard, and -- for corpus changes only -- the corpus validator."
    entry_class: INFERENCE
    evidence:
      - ".github/workflows/ci.yml"
      - ".github/workflows/launchpad-pr-check.yml"
      - ".github/workflows/launchpad-adr-check.yml"
      - ".github/workflows/launchpad-security-audit.yml"
      - ".github/workflows/launchpad-corpus-validate.yml"
    confidence: 0.85
  - statement: "Because the DCO app reports on block/buzz and not on this fork, and no workflow in .github/workflows/ mentions DCO or Signed-off-by, the sign-off requirement in this fork is held by the local commit-msg hook and by review rather than by any check that can fail a pull request here."
    entry_class: INFERENCE
    evidence:
      - "lefthook.yml"
      - "CONTRIBUTING.md"
      - "launchpad/AGENTS.md"
    confidence: 0.8
  - statement: "Because every globbed pre-push lane derives its file set from origin/main...HEAD while this fork's base branch is launchpad, a branch cut from launchpad is diffed against a base it did not branch from, so the lanes that fire locally need not match the lanes CI would consider changed."
    entry_class: INFERENCE
    evidence:
      - "lefthook.yml"
      - "gh_api('repos/launchpad-26/buzz') -> default_branch=launchpad"
    confidence: 0.75
relationships:
  - type: references
    target: corpus-standard-review-requirements
  - type: references
    target: development-hermit
---

# Policy: contribution process in the launchpad-26 fork

How a change gets from an idea to a merged commit in `launchpad-26/buzz`: which
artifact it becomes, which branch it is cut from, what a pull request body must
carry, and which of those steps a machine actually enforces. Written for anyone —
human or agent — making a change in this fork. **This node is the process. Who is
permitted to decide, approve or merge is a different subject**; see *Scope and
omissions*.

## Scope and authority

**This node governs** the route a change takes through this fork: choosing an
issue type and filing it, branching, committing, opening a pull request, passing
the checks that run, and what happens when a defect is found late. It covers the
route for **cohort work** — deployment, CI/CD, documentation and process — which
is what this fork exists to do.

**Its authority is derived, not original.** Every requirement below is already
stated somewhere else, and this node's job is to name that somewhere and to say
whether a machine holds it. `launchpad/AGENTS.md` declares itself the normative
spec for how work is filed, reviewed and merged here. The decision records under
`launchpad/decisions/` settle the questions that spec defers. The workflows under
`.github/workflows/` and `lefthook.yml` are the parts a machine executes. This
node invents nothing.

**Precedence.** Where this node and `launchpad/AGENTS.md`, an accepted ADR, a
workflow file, or `lefthook.yml` disagree, **they win** — this node has drifted
and should be fixed. Where `launchpad/AGENTS.md` and the root `CLAUDE.md` /
`AGENTS.md` disagree about cohort work, **`launchpad/AGENTS.md` wins**: it states
that it supersedes them for anything under `launchpad/`,
`.github/workflows/launchpad-*`, and all cohort process work, and that their
guidance is *wrong, not merely irrelevant* for that work. Where a narrower
standard governs one kind of change — corpus nodes have their own review
requirements — **the narrower one wins for its subject.**

| For | Read |
|---|---|
| The normative process spec this node describes | `launchpad/AGENTS.md` |
| Delegated authority, batching, and who may approve or merge | `launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md` |
| Why one Feature is one pull request whatever its size | `launchpad/decisions/ADR-0054-one-feature-one-pr-no-size-cap.md` |
| Why merge commit is the only merge method | `launchpad/decisions/ADR-0055-merge-commit-is-the-merge-strategy.md` |
| Why a review check gates only when deterministic (superseded by ADR-0052, still the record of why required checks are empty) | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md` |
| The pull request body schema an agent fills | `launchpad/AGENT_PR_TEMPLATE.md` |
| The pull request body a human fills | `.github/PULL_REQUEST_TEMPLATE.md` |
| The six issue forms and their required fields | `.github/ISSUE_TEMPLATE/` |
| What the local hooks actually run | `lefthook.yml` |
| What the pull request body check actually rejects | `launchpad/scripts/pr_body_check.py` |
| Extra review requirements for a corpus change | `launchpad/docs/corpus/standards/review-requirements.md` |
| Activating the pinned toolchain the hooks need | `launchpad/docs/corpus/development/hermit.md` |
| Building and testing the upstream product itself | `CONTRIBUTING.md` — and see *The upstream guide is the wrong map* |

### The upstream guide is the wrong map for cohort work

`CONTRIBUTING.md` is upstream's contributor guide, correct for changing Buzz
itself and misleading here. Three of its statements are false in this fork, and
each has been checked rather than assumed:

- It says *"We squash-merge, so your PR title becomes the commit subject in
  `main`."* This repository has `allow_squash_merge: false` and
  `allow_rebase_merge: false`; only `allow_merge_commit` is true, the default
  branch is `launchpad`, and `merge_commit_title` is `MERGE_MESSAGE` — so the
  subject on the trunk is `Merge pull request #N from <branch>`, not the pull
  request title.
- It directs contributors to open issues at `block/buzz`. Cohort work is filed
  here; only genuine upstream product bugs go there.
- It says *"The **DCO Check** will block your PR without it."* No check by that
  name appears on this fork's pull requests — see *Enforcement*.

The routing is stated on the issue chooser page as well as in
`launchpad/AGENTS.md`: `.github/ISSUE_TEMPLATE/config.yml` disables blank issues
and offers three links, one of which is `block/buzz/issues`, described as where
upstream product bugs go because *"This fork operates Buzz, it does not develop
it."*

## The route a change takes

Six stages. Each is stated as a requirement below, with its identifier.

1. **Decide what the change is.** Work down `launchpad/AGENTS.md` section 4's
   six-type list; the first "yes" wins. ADR is first on purpose — a decision that
   changes nothing in the repository when it closes is not a Task. (**C1**, **C2**)
2. **File it.** Fill the matching form in `.github/ISSUE_TEMPLATE/`, apply exactly
   one `type:` label, link the parent with `--parent`. (**C3**, **C4**, **C5**)
3. **Branch and work.** Cut from `launchpad`, activate Hermit, commit with `-s`
   and a conventional title, one commit per child Task. (**C6**–**C9**)
4. **Push.** The pre-push lanes run on the checked-out `HEAD`. (**C10**)
5. **Open the pull request.** One Feature, one pull request; fill the right
   template; write closing references as plain text outside code. (**C11**–**C15**)
6. **Merge.** As a merge commit, through the platform's own gates, never around
   them. A late defect becomes a `deferred-blocker` issue rather than a silent
   omission. (**C16**–**C18**)

## MUST

Identifiers are this node's own and stable. The **Held by** column names what
actually enforces the requirement, or says that nothing does — read it as the
load-bearing column, not a footnote.

| # | Requirement | Held by |
|---|---|---|
| **C1** | An issue MUST carry exactly one `type:` label. A type never modifies another type. | **Machine** — `launchpad-issue-check.yml` fails on zero or more than one `type:` label |
| **C2** | The type MUST be chosen by working `launchpad/AGENTS.md` section 4's list in order and taking the first "yes"; an ADR MUST NOT be filed as a Task because it looks like work. | **Convention** — nothing checks the ordering, only that a label exists |
| **C3** | An issue body MUST carry every `### Heading` its type requires, each non-empty. | **Machine** — `launchpad-issue-check.yml`'s `REQUIRED` map; failure adds `needs-triage` and comments |
| **C4** | A `type:bug` issue MUST paste raw output in a fenced code block, not a paraphrase. | **Machine** — same workflow |
| **C5** | A Task MUST be linked to its Feature, a Feature to its PRD, and an ADR raised by either to that parent, using `gh issue create --parent`. | **Convention** — the PR body check reads sub-issues later, but nothing checks the link at filing time |
| **C6** | A branch MUST be cut from `launchpad`, and the pull request MUST target `launchpad`. | **Partly machine** — `launchpad` is the repository default branch, so an omitted `--base` resolves correctly; nothing rejects a branch cut from elsewhere |
| **C7** | The Hermit toolchain MUST be activated (`. ./bin/activate-hermit`) before running git commands, or the hooks fail on `PATH`. | **Partly machine** — `bin/.lefthookrc` self-pins `LEFTHOOK_BIN` and prepends Hermit's `bin/` for hook subprocesses; commands outside a hook are unprotected |
| **C8** | Every commit MUST carry a `Signed-off-by` trailer (`git commit -s`). | **Local machine only** — `lefthook.yml`'s `commit-msg` `signoff` lane appends it for `git commit` and `git merge`; `git rebase --signoff` and `git cherry-pick -s` are needed for those flows, and **no CI check enforces it on this fork** |
| **C9** | Commit titles MUST follow Conventional Commits, and a batch MUST keep one commit per child Task — those commits are the review unit and what `git bisect` gets. | **Convention** — nothing checks either |
| **C10** | A branch MUST NOT be force-pushed during review, and MUST NOT be rebased once pushed; merge `launchpad` in instead. | **Convention** — nothing checks; `dismiss_stale_reviews` makes the cost visible only after the fact |
| **C11** | A pull request body MUST be the filled template — the agent schema `launchpad/AGENT_PR_TEMPLATE.md` for agent-authored work, `.github/PULL_REQUEST_TEMPLATE.md` otherwise — with no headings added or removed and `N/A - <reason>` for anything inapplicable. | **Partly machine** — `pr_body_check.py` rejects an empty body and a missing `### Issue type`; heading fidelity beyond the sections it names is convention |
| **C12** | Closing references MUST be plain text outside backticks and fences, one keyword per line; `Refs #n` for a pull request that completes nothing. | **Machine** — the workflow asks GitHub's `closingIssuesReferences` rather than pattern-matching, precisely because a regex cannot tell a real reference from one inside code |
| **C13** | One Feature, one pull request: every issue a batch closes MUST be a child of the Feature it names, or be that Feature. A Feature MUST NOT be split because it is large. | **Machine** — `check_batch()` against the Feature's `sub_issues`; an unreadable answer is reported as unverified, not passed |
| **C14** | An agent-authored pull request MUST carry `by:agent`, every provenance table field filled, a specific non-empty `### Not verified`, and raw command output in a fenced block. | **Machine** — `pr_body_check.py`; the strict checks are keyed on the body as well as the label, so removing `by:agent` does not remove them |
| **C15** | An agent MUST NOT claim a check it did not run or an instruction it did not receive; paste the command and its raw output. | **Partly machine** — the fenced-block and `Not verified` rules make the omission visible; whether the pasted output is real is unenforceable |
| **C16** | A pull request MUST land as a merge commit. | **Machine** — `allow_squash_merge` and `allow_rebase_merge` are both `false`, so the platform offers no other method |
| **C17** | A merge MUST go through the platform's gates. No `gh pr merge --admin`, no merging past failing or pending checks, no dismissing reviews, no editing branch protection, required checks or rulesets to get a change in. | **Convention** — `enforce_admins` is recorded off, so a token holding admin *can*; the prohibition is the only control |
| **C18** | A defect found while preparing or reviewing a batch MUST become an open issue parented to that Feature, labelled `deferred-blocker` and named in the body — **except** the four never-deferrable classes: a credential, secret or password hash in the diff; a disclosure-boundary violation; a failing deterministic check; anything that leaves `launchpad` broken for other agents. | **Convention** — nothing checks that the named issues exist or carry the label |
| **C19** | A vulnerability MUST NOT be filed as a public issue; use the private advisory link on the chooser page. | **Partly machine** — `blank_issues_enabled: false` forces the chooser, which carries the advisory link first; nothing stops a public issue being filed anyway |
| **C20** | A genuine upstream product bug MUST be filed at `block/buzz/issues`, not here. | **Convention** — stated on the chooser page and in `launchpad/AGENTS.md` section 1 |
| **C21** | `gh repo set-default launchpad-26/buzz` MUST be run once per clone before the first `gh issue create` or `gh pr create`, or a write with no explicit `--repo` lands on the parent repository's public tracker. | **Convention** — nothing checks; the mistake is invisible until someone looks upstream |

## SHOULD

| # | Guidance |
|---|---|
| **G1** | A fix small enough to make inside a file you are already touching SHOULD be made and noted in the pull request body rather than filed. `launchpad/AGENTS.md` sets that threshold deliberately: without one you get either invisible work or issue spam. |
| **G2** | An issue whose type is genuinely unclear SHOULD be filed as a Task with `needs-triage` and the ambiguity stated in *Objective*, never guessed silently between PRD and Task. |
| **G3** | An ADR filed from the CLI SHOULD have `needs-decision` added explicitly — issue-form labels apply only through the web UI, so `gh issue create` does not receive it. |
| **G4** | A merge SHOULD be queued with `gh pr merge --auto` so the platform merges when the gates go green, rather than watched and merged by hand. |
| **G5** | A pull request body SHOULD name what was *not* verified specifically enough that a reviewer can act on it. "Nothing" is not an answer; there is always something. |
| **G6** | Local hook results SHOULD NOT be read as a prediction of CI. The pre-push lanes diff against `origin/main` while this fork's base is `launchpad`, so which lanes fire locally need not match what CI considers changed. |
| **G7** | A change touching `launchpad/docs/corpus/**` SHOULD be reviewed against `launchpad/docs/corpus/standards/review-requirements.md` in addition to this process, and validated locally with `python3 launchpad/project-intelligence/corpus/validate.py` before pushing. |

## Enforcement

Three layers act, and they are not equally strong. Read this section before
trusting any green tick.

### Layer 1 — local hooks (`lefthook.yml`)

Installed by `just hooks`. **Pre-commit** runs five formatting lanes, each globbed
to its own tree, with `stage_fixed: true`: `rust-fmt`, `desktop-tauri-fmt`,
`desktop-fix`, `web-fix`, `mobile-fmt`. **`commit-msg`** runs one lane, `signoff`,
which appends the DCO trailer idempotently. **Pre-push** runs `branch-skew`,
`push-head-scope`, `file-size-check`, `rust-tests`, `desktop-check`,
`desktop-typecheck`, `desktop-test`, `desktop-tauri-checks` and `mobile-checks`.

Three things about that list are easy to get wrong, so they are stated rather than
summarised:

- **No lane runs workspace-wide clippy.** `rust-tests` runs `just test-unit`. The
  only clippy invocation in the whole file is `just desktop-tauri-clippy`, inside
  `desktop-tauri-checks`. Prose elsewhere in this repository describes pre-push as
  running "clippy (workspace + Tauri)"; the file does not.
- **Only `branch-skew` and `file-size-check` fail on every push.** Every other
  substantive lane is globbed, and none of those globs names a path under
  `launchpad/`. `push-head-scope` is unglobbed but warn-only and never fails a
  push. **So a cohort-only change runs two blocking local lanes, and
  `file-size-check` covers only `desktop/`, `web/` and `mobile/`.**
- **The globbed lanes diff against the wrong base.** Each sets
  `files: git diff --name-only origin/main...HEAD`, but this fork's base branch is
  `launchpad`.

### Layer 2 — CI

`ci.yml` triggers on push to `main` and `release` and on every pull request, but
gates almost every job behind a `dorny/paths-filter` job whose filters name
`crates/`, `desktop/`, `web/`, `mobile/` and the Rust build inputs — **and no path
under `launchpad/`**. Measured rather than assumed: on pull request #1997, which
changed `lefthook.yml` only, every path-filtered job reported `SKIPPED`, while
`Detect Changed Paths` and `Dead Token Reference Guard` ran. `dead-token-guard`
carries no `if:` at all, which is why it is the exception.

The checks that actually run on a cohort pull request come from the `launchpad-*`
family:

| Job | Workflow | What it does |
|---|---|---|
| `check` | PR body check | Runs `pr_body_check.py` against the body, GitHub's closing references, and the named Feature's sub-issues |
| `scripts` | PR body check | Runs the `launchpad/scripts` unit suite, then `mutation_harness.py` to prove those controls can fail |
| `adr-boundary` | ADR boundary check | Unfiltered by path, fails closed on a missing checker or document, then runs `adr_boundary_check.py` |
| `audit` | Security audit | Unfiltered by path — a leaked credential is as real in `crates/` as under `launchpad/` — plus a daily schedule |
| `validate` | Corpus validate | Path-triggered on `launchpad/docs/corpus/**`; runs the unit tests, then the validator against the real corpus tree |
| `tests` | Agents / corpus-schema / RQA suites | Path-triggered on their own subtrees |
| `controls`, `guard`, `publish` | Review agent workflows | Containment controls and publish guard |

`adr_boundary_check.py` is narrower than its name suggests: it checks that
ADR-0005's deployment-image-provenance list agrees with itself across the ADR's
table, the ADR's prose count and `launchpad/AGENTS.md` section 3's entry, and that
each sanctioned file actually carries a Launchpad value. **It does not check the
rest of section 3's upstream-boundary rules.**

### Layer 3 — human review

`launchpad` reports `protected: true`. Beyond that, this node could not measure
the protection: the repository ruleset list and the effective rules for the branch
are both empty, and the legacy branch-protection endpoint returns **404** for a
token whose repository permission is `maintain` rather than `admin`.
`launchpad/AGENTS.md` records a 2026-08-28 measurement — one approving review
required, `dismiss_stale_reviews` on, `required_status_checks` **empty**,
`enforce_admins` off, push restricted to 11 users — and that figure is carried
here as attributed knowledge, not as a fact this node re-established.

`.github/CODEOWNERS` assigns every path to `@block/buzz-oss-team`, an **upstream**
organisation team. Whether code-owner review is required on this fork could not be
read.

### What a green pull request does not establish

| Not established | Why |
|---|---|
| That any check gated the merge | Pull request #1997 merged on 2026-08-31 with the PR body check reporting FAILURE. The checks on a pull request here are informational unless the protection recorded in `launchpad/AGENTS.md` has since changed. |
| That commits carry `Signed-off-by` | No check named `DCO Check` appears on this fork's pull requests (#1997, #1978, #1970, #1941 all checked), though it does appear on `block/buzz` #7214. The trailer is added by a local hook and confirmed by review. |
| That the Rust workspace lints or builds | `ci.yml`'s Rust jobs skip for a cohort-only change, and no local lane runs workspace clippy. |
| That the upstream boundary in section 3 was respected | `adr_boundary_check.py` checks ADR-0005's list only. |
| That pasted command output is real | Nothing compares it to anything. `launchpad/AGENTS.md` rule 4 is the only control, and it is unenforceable. |
| That a named `deferred-blocker` issue exists or carries the label | Nothing verifies the reference. |
| That an issue's type is the *right* one | The issue check counts `type:` labels and matches headings; the first-yes-wins ordering is unchecked. |
| That local hooks predicted CI | The globbed lanes diff against `origin/main`, not `launchpad`. |

**This is deliberate, not neglect.** ADR-0019 — since superseded by ADR-0052, but
still the record of why the required-checks list is empty — rules three things: a
required status check may only ever be a deterministic script; a human approval
remains required always; and *marking* checks as required is deferred until the
CI/CD pipeline programme lands, which is why issues #153 and #146 stay open **by
decision rather than by obstruction**. The same ADR records `enforce_admins`
staying off as a deliberate acceptance, naming the four repository admins who can
therefore bypass required checks once any exist.

The launchpad workflows are built to that first ruling: `pr_body_check.py` reports
an unreadable GraphQL answer as *unverified* rather than passing it, and
`mutation_harness.py` exists to prove the controls can fail. The consequence is
that **review carries most of this process today**, and a reviewer should know
which rows of the MUST table above say "Convention".

## Exceptions and escalation

**There is no exemption from the four never-deferrable classes.** A credential,
secret or password hash in the diff; a disclosure-boundary violation; a failing
deterministic check; anything that leaves `launchpad` broken for other agents.
The list is closed. The first two are unrecoverable once merged — a pushed secret
is on every clone, and rotation becomes the remedy.

**Everything else is deferred in the open, not waived.** File it as a child of the
pull request's Feature, label it `deferred-blocker`, name it in the body's
*Deferred blockers* section, then merge. A Feature may not close while it holds
open `deferred-blocker` issues, and one holding more than five has its next batch
refused.

**A blocked merge is an answer.** Fix the change or escalate to a human. Reaching
for a stronger credential is the failure mode `launchpad/AGENTS.md` and ADR-0052
exist to prevent, and the reason given is a real event: on 2026-08-28, 132 pull
requests were merged with `--admin` past 77 changes-requested reviews and
unresolved CI.

**An unclear issue type is filed, not guessed.** Task plus `needs-triage`, with
the ambiguity written into *Objective*. Misfiling a PRD as a Task hides an
approval gate, which is the specific harm the rule names.

**A departure from a SHOULD is stated where it applies.** G1–G7 are guidance; say
which one you departed from and why, in the section it would have governed.

**A case none of this covers is escalated, not invented.** Raise it as an issue in
this repository rather than widening the process locally. If the gap is a decision
rather than work — if nothing in the repository changes when it closes — it is an
ADR issue, per `launchpad/AGENTS.md` section 4's first row.

**Adding an upstream-boundary exception is not a pull-request decision.** Section
3's list of permitted divergences is closed; a further exception needs its own
ADR.

## Scope and omissions

**This node covers** the route a change takes from idea to merge in this fork:
issue type and filing, branching and committing, the pull request body contract,
the local and CI checks that run, and how a late defect is handled — with each
requirement marked as machine-enforced or convention.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| **Who decides** — approval authority, ADR outcome authority, the five conditions of delegated authority, who may merge | `governance/decision-authority.md` and `launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md` |
| The additional checklist a reviewer of a corpus change works to | `launchpad/docs/corpus/standards/review-requirements.md` |
| How to create, update or retire a corpus node | `launchpad/docs/corpus/AGENTS.md` |
| The upstream-boundary rules of `launchpad/AGENTS.md` section 3 beyond ADR-0005's deployment list | `launchpad/AGENTS.md` section 3 and `launchpad/decisions/ADR-0043-prefer-fork-owned-overrides.md` |
| How to build, test or debug the Buzz product itself | `CONTRIBUTING.md`, and the corpus `development/` nodes |
| The label vocabulary and how it is applied | `launchpad/labels.yml` and `launchpad/sync-labels.sh` |
| Sprint and milestone scheduling | `launchpad/AGENTS.md` section 4's *Sprints and iterations* |
| The contribution process for `launchpad-26/buzz-infrastructure`, which has its own rules for live hosts | That repository's own `AGENTS.md` and ADR-0015 |

**It does not restate the sources it defers to.** The MUST table names what
enforces each requirement; the requirement's full reasoning stays in
`launchpad/AGENTS.md` and the ADRs, because a second copy drifts silently and
nothing here would notice.

**Expected but not verified when this node was written:**

- **The `launchpad` branch's protection settings could not be read.**
  `repos/launchpad-26/buzz/branches/launchpad/protection` returns HTTP 404 for
  this session's token (`admin: false`, `maintain: true`). Both the repository
  ruleset list and `rules/branches/launchpad` return empty, so no ruleset is in
  play and protection must be the legacy kind — but the required-review count,
  the required-status-check list and `enforce_admins` are all carried from
  `launchpad/AGENTS.md`'s 2026-08-28 measurement, not re-measured here. The
  observation that #1997 merged with a failing check is consistent with an empty
  required-checks list; it does not prove one.
- **Whether `@block/buzz-oss-team` resolves in the launchpad-26 organisation was
  not checked**, so the practical effect of `.github/CODEOWNERS` on this fork is
  unknown.
- **No `governance/` node existed in the corpus before this one**, so the
  boundary against `governance/decision-authority.md` was originally drawn from
  that issue's stated subject rather than from a merged document. That sibling
  has since landed in this same integration, so the natural edge to it now
  resolves; it is not added here, since wiring it in under the pressure of a
  pre-merge fix pass risks the same kind of error this fix pass exists to catch.
  Adding it belongs to a dedicated pass across the whole
  `development`/`governance`/`releases` shelf once all 37 nodes are stable.
- **Local hook behaviour was read from `lefthook.yml`, not executed.** No push
  was made from this worktree, so which lanes fire for a `launchpad/`-only change
  is inferred from the globs rather than observed.
- **The four pull requests sampled for the DCO check** (#1997, #1978, #1970,
  #1941) are recent and consecutive, not a census. A `DCO Check` configured
  after this revision, or reporting only on some pull requests, would not appear
  in that sample.
- **`pr_body_check.py` was read, not run against a real body.** Its `check()`
  logic is quoted from the source; no fixture was executed here.

**Findings this node records but does not fix.** Each is a divergence between a
document's prose and the behaviour of the file it describes, found while gathering
evidence, and none is this node's to repair:

1. `CONTRIBUTING.md` states this project squash-merges and that the pull request
   title becomes the trunk commit subject. Both are false for this fork.
2. `CONTRIBUTING.md` and `launchpad/AGENTS.md` both describe the DCO check as
   blocking a pull request here. No such check runs on this fork.
3. Prose elsewhere in this repository describes the pre-push hook as running
   workspace clippy. `lefthook.yml` runs clippy only for the Tauri crate.
4. Every globbed pre-push lane diffs against `origin/main` while this fork's base
   branch is `launchpad`.

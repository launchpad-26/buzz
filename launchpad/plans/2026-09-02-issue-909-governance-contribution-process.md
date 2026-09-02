# Issue #909 — governance/contribution-process.md

ALREADY TRUE: `origin/launchpad` is at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`. `launchpad/docs/corpus/` holds 200+ merged nodes, but **no `governance/` directory exists yet** — this is the first node under it. Sibling #910 (`governance/decision-authority.md`) is not merged and is therefore not a legal `relationships` target. `launchpad/AGENTS.md`, `launchpad/AGENT_PR_TEMPLATE.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/*.yml`, `lefthook.yml`, `.github/workflows/ci.yml` and `.github/workflows/launchpad-*.yml` all exist at that revision.

STEP 1  Gather enforcement evidence directly, never from prose. Open `lefthook.yml` and enumerate the actual `pre-commit` / `commit-msg` / `pre-push` lanes; open `.github/workflows/ci.yml` for its `on:` triggers and `changes` paths-filter; enumerate every `.github/workflows/launchpad-*.yml` trigger and job id; read `launchpad/scripts/pr_body_check.py`'s `check()` for what the PR body check actually rejects; read `launchpad-issue-check.yml`'s `REQUIRED` map. Query **both** `gh api repos/launchpad-26/buzz/rulesets` and `repos/launchpad-26/buzz/branches/launchpad/protection`, plus `repos/launchpad-26/buzz/rules/branches/launchpad`, and record what each returns rather than what any document claims. ← DONE

STEP 2  [needs 1] Falsify or confirm the two headline enforcement claims: (a) does a **DCO Check** run on this fork's PRs? — compare `statusCheckRollup` on recent `launchpad-26/buzz` PRs against a recent `block/buzz` PR; (b) can a PR merge with a failing launchpad check? — inspect a merged PR's rollup. ← DONE (both falsify the prose: no DCO Check on the fork; PR #1997 merged with `check` FAILURE)

STEP 3  [needs 2] Write front matter — id `governance-contribution-process`, type `governance`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, one evidence entry per substantive claim with the first FACT recording revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`; `relationships` only toward ids confirmed present via `git show origin/launchpad:<path>`.

STEP 4  [needs 3] Write the body to the **policy** template shape (`launchpad/docs/corpus/templates/policy.md`): six required sections in order — Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions — with RFC 2119 keywords, stable requirement identifiers, `# Policy: <subject>` H1, and authority stated as **derived** from `launchpad/AGENTS.md` + the ADRs, not original. Every enforcement claim labelled machine-enforced vs convention, citing the lane or workflow that does it.

STEP 5  [needs 4] Run `python3 launchpad/project-intelligence/corpus/validate.py` until PASS; then run the corpus unittest suite as the sole prior command; then commit plan + document with `git commit -s`. Stop at the commit.

PARALLEL: none — one document, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK, run bare and unpiped as the sole command in its call. No push, no PR.

BUDGET: small — one document. Evidence is ~10 configuration/workflow files plus four GitHub API reads.

OPEN: The `branches/launchpad/protection` endpoint returns **404** for this session's token (`permissions.admin: false`, `maintain: true`), so `launchpad/AGENTS.md` §6's measured protection figures — one approving review, empty `required_status_checks`, `enforce_admins` off, push restricted to 11 users — **cannot be re-verified here**. `branches/launchpad` does report `protected: true`, and both `rulesets` and `rules/branches/launchpad` return `[]`, so protection is legacy branch protection with no ruleset. The node records the readable measurements as FACT, records AGENTS.md's unreadable figures as TEAM_KNOWLEDGE attributed to that file, and names the unreadable endpoint as a gap. This node does not resolve it.

LEFT OUT: **Who decides** — approval authority, ADR outcome authority, delegated authority conditions — is sibling #910 (`governance/decision-authority.md`) and is linked, not restated. No edit to `launchpad/AGENTS.md`, `CONTRIBUTING.md`, `lefthook.yml` or any workflow, even where this node records that their prose disagrees with their own behaviour; those divergences are named as findings, not fixed. No new policy is invented — where the process has a gap, the gap is named.

# Issue #910 — governance/decision-authority.md

ALREADY TRUE: `origin/launchpad` (HEAD `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`) carries a large merged corpus — `AGENTS.md`, `README.md`, `agents/invariants.md`, `architecture/**`, `capabilities/**`, `development/**`, `layers/**`, `standards/**` (19 nodes) and `templates/**` (26 nodes). `launchpad/docs/corpus/governance/` does **not** exist; every governance sibling (#907–#915) is unmerged. `launchpad/docs/corpus/templates/policy.md` (`corpus-template-policy`) is merged and is this node's shape. `launchpad/AGENTS.md` §3–§6, `launchpad/decisions/README.md`, ADR-0019 (Superseded by ADR-0052) and ADR-0052 (Accepted) are all merged and readable.

STEP 1  Gather authority evidence: read `launchpad/AGENTS.md` §3 (closed exception list), §4 (issue types, ADR-first, rules 1–7), §5 rule 1 + *Acting on a human's instruction* (five conditions, never-route-around-the-platform), §6 (branch/commit/PR, protection figures dated 2026-08-28); `launchpad/decisions/README.md` (lifecycle, what "Accepted" means, superseding); ADR-0019 and ADR-0052 in full; ADR-0054/0055 for the merge-unit rules that §6 cites. ← RUNS HERE

STEP 2  [needs 1] Verify every enforcement claim against the artefact rather than the prose. Platform: `gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name,protected}'` (specific branch, never the paginated listing), `.../protection`, `rulesets?includes_parents=true`, `repos/launchpad-26/buzz --jq .permissions`. Repository: `launchpad/scripts/pr_body_check.py` (`check_delegated`, `looks_agent_authored`, `PROVENANCE_FIELDS`, `DEFERRED_CEILING`), `launchpad/scripts/adr_boundary_check.py`, `.github/workflows/launchpad-pr-check.yml`, `launchpad-issue-check.yml`, `launchpad-adr-check.yml`, `.github/CODEOWNERS`, `grep '^status:' launchpad/decisions/ADR-*.md`, `gh pr checks` on #1997/#1978. Record every unknown as an unknown.

STEP 3  [needs 2] Confirm relationship targets exist on the merge target with `git show origin/launchpad:<path>` before declaring any edge; take the ids from the files, not from memory.

STEP 4  [needs 3] Write front matter (`id: governance-decision-authority`, `type: governance`, `status: draft`, `origin: launchpad`, audiences `[agent, developer, reviewer]`, evidence ledger with the revision as its first FACT) and the body on the `policy.md` skeleton — six required sections in order, RFC 2119 framing, authority stated as derived, a MUST/SHOULD split that records only what exists.

STEP 5  [needs 4] `python3 launchpad/project-intelligence/corpus/validate.py` until exit 0; then, as the sole command in its own call, `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`; then `git add` document + plan and `git commit -s`. Stop at the commit.

PARALLEL: STEP 2's platform queries and repository greps are independent of each other and were issued together; everything else is strictly sequential — one file, one author.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` exits 0. The corpus unittest suite reports OK, run bare and unpiped as the sole command in its own call. No push, no PR, no other branch. `review-adjudicate` and the cross-model final pass belong to the batch owner, not to this run.

BUDGET: small — one corpus node plus this plan. No code changes. Evidence gathering is bounded by `launchpad/AGENTS.md`, four ADRs, two checker scripts, four workflows and five platform API reads.

OPEN:
- **`required_approving_review_count`, `require_code_owner_reviews` and `enforce_admins` are unreadable.** `repos/launchpad-26/buzz/branches/launchpad/protection` returns 404 under this token (`admin: false, maintain: true`) — a permissions artefact, not evidence of absence. The branch **is** protected (`protected: true` on the specific-branch read) and `rulesets?includes_parents=true` is `[]`, which means enforcement is classic, not that there is none. The node states each of the three as an explicit unknown, names the command an admin would run, and carries §6's dated 2026-08-28 figures only as attributed TEAM_KNOWLEDGE.
- **`status: Proposed` on ADR-0046**, which `launchpad/AGENTS.md` §3 cites as the authority for a member of its closed exception list, while `launchpad/decisions/README.md` says accepted ADRs live in that directory. Recorded as a gap in the node; not resolved here, and no issue filed from this run.
- **No `DCO Check` runs on this fork** although §6 and `CONTRIBUTING.md` both say it blocks. Already filed at #2044; the node records the state and points at the issue.

LEFT OUT:
- **The process a change moves through** — branch, commit convention, PR body shape, batch size, merge method. That is sibling #909 `governance/contribution-process.md`. This node is about **who may decide**, not the pipeline the decision travels down.
- **`.github/CODEOWNERS` as a subject** (#907) and **the maintainer/push-restriction roster by name** (#913, #914). Named as boundaries with their owners, never enumerated.
- **Corpus-internal review duties**, already owned by the merged `corpus-standard-review-requirements`, which itself defers "review count, DCO, who may approve" to `launchpad/AGENTS.md` §5–§6 — the exact seam this node fills.
- **Deciding any open ADR question**, widening §3's closed list, or filing issues for the gaps found. Findings are reported to the caller; filing is not this run's to do.

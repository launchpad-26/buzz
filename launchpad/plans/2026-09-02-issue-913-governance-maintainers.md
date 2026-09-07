# Issue #913 — governance/maintainers.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/policy.md` (id `corpus-template-policy`) and the `standards/` track are merged on `origin/launchpad`. `launchpad/docs/corpus/governance/` **does not exist** on `origin/launchpad` — verified with `git ls-tree origin/launchpad --name-only launchpad/docs/corpus/`, which lists `agents architecture capabilities development layers schema standards templates` and no `governance`. Siblings #907 (`governance/codeowners.md`) and #910 (`governance/decision-authority.md`) are OPEN and unmerged, so neither is a relationship target.

STEP 1  Establish ground truth on who maintains this fork, assuming nothing. Check `MAINTAINERS`, `MAINTAINERS.md`, `GOVERNANCE.md`, `.github/CODEOWNERS`, and any roster under `launchpad/`. Probe the platform for the mechanisms a tracked file cannot show: repository permission levels, org teams, branch protection. ← RUNS HERE

Findings, all verified:
- No `MAINTAINERS` or `MAINTAINERS.md` exists at any path (`git ls-files` + `ls`).
- `GOVERNANCE.md` exists and is a **one-line redirect** to `block/.github`'s governance document — upstream's, not this fork's.
- `.github/CODEOWNERS` is one line, `* @block/buzz-oss-team`, and is **invalid in this fork**: `gh api repos/launchpad-26/buzz/codeowners/errors` reports `Unknown owner` on line 1, while the same endpoint on `block/buzz` returns `{"errors":[]}`. #1428 already owns fixing it — do not file a duplicate.
- The roster is **GitHub org/team membership, not a tracked file**: `gh api orgs/launchpad-26/teams --jq '.[].slug'` returns `maintainers` and `students`, corroborating ADR-0056's provenance note.
- `launchpad` is branch-protected (`gh api repos/launchpad-26/buzz/branches/launchpad --jq '{name,protected}'` → `protected: true`). The `/protection` endpoint 404s because this token is `maintain`, not `admin` — a permissions artefact, not absence. Record the review-count and code-owner-review settings as explicit unknowns with the admin command.

STEP 2  [needs 1] Write the front matter — schema-valid per `node.schema.json`: id `governance-maintainers`, type `governance`, status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`. Relationships only to ids CONFIRMED with `git show origin/launchpad:<path>`: `implements: corpus-template-policy`, `depends-on: corpus-agents`, `references: corpus-standard-normative-language`. First evidence entry records revision `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`git cat-file -e` exits 0). FACT/INFERENCE carry `evidence`; INFERENCE additionally `confidence`; TEAM_KNOWLEDGE carries `provided_by` and no `confidence`.

STEP 3  [needs 2] Write the body on the **policy** template's six required sections in order — Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and omissions — with RFC 2119 framing, requirement identifiers (M1…/S1…), and authority stated as **derived**. Record what exists and name gaps; invent no policy.

**Privacy boundary, applied deliberately.** `launchpad-26/buzz` is public. Name the *mechanism* (org teams `maintainers` and `students`, administered in GitHub org settings) and aggregate, non-identifying counts. **Enumerate no individual's name, username or email beyond what the repository's own tracked files already publish.** Team membership is readable with this token; not publishing it is the deliberate outcome, recorded as an omission in the body, not a failure.

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until it reports PASS.

STEP 5  [needs 4] Run the corpus unittest suite bare and unpiped as the sole command in its own call, confirm OK, then `git add` document + plan and `git commit -s` in a separate call. **Stop at the commit** — no push, no PR, no other branch.

PARALLEL: none — one document, one task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must report PASS. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report OK. Review passes are deferred to the batch owner.

BUDGET: small — one document, no code changes.

OPEN: The number of approvals `launchpad` requires and whether it requires code-owner review are **unreadable with a `maintain` token** and are recorded as explicit unknowns naming the admin command, not guessed. Whether the invalid `CODEOWNERS` means the fork currently has *no* effective review routing at all is stated as an INFERENCE, not a FACT, because the protection settings that would confirm it are the unreadable ones.

LEFT OUT: Review routing itself (#907's subject) and who holds decision authority (#910's subject) — this node names the boundary and links nothing, since neither is merged. No fix to `CODEOWNERS` (#1428 owns it). No fix to `GOVERNANCE.md`'s upstream redirect. No new policy invented where the fork has none.

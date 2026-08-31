# Runtime contracts

## Job identity and states

Identity: `repo + pull_number + head_sha + lane`.

States:

`detected -> preflight -> held | evidence -> assurance -> degraded_draft | adjudication -> action -> completed`

Any phase may enter `retryable` with a bounded retry count. `human_required` is terminal until an operator supplies the named input. Only `completed` consumes the transition. A changed head creates a new job and makes every older nonterminal job `superseded`.

Lanes:

- `incoming_review`: read-only reviewers; advisory comment and finding issues only.
- `author_triage`: evaluates feedback on the operator's PR, then may modify and push the PR branch.

## GitHub transport

- Every per-PR read uses REST GET through `github_rest.py`, including the
  mandatory revalidation immediately before an approval mutation.
- Bulk queue inventory uses one allowlisted, read-only GraphQL query per page of
  open pull requests, through `github_query.py`. Amended 2026-08-31 (#1962): the
  earlier rule was "every read uses REST GET". Assembling the same facts over
  REST cost one list call plus five per-PR calls — about 151 calls for thirty
  open pull requests, on every sweep. `github_query.py` carries no mutation
  vocabulary, shares no code with `github_mutate.py`, refuses any document
  outside its named allowlist, and fails closed on a truncated connection rather
  than reconciling a partial queue. Reads and mutations remain separate
  chokepoints; only the read transport for bulk inventory changed.
- Every GitHub mutation uses a named template in `github_mutate.py`.
- REST responses use ETags, maximum supported page size, conditional requests, and recorded rate headers.
- GraphQL mutations use cached REST `node_id` values, variables, `clientMutationId`, and the smallest useful selection set.
- Every mutation is verified with REST.
- `approve_review` (event APPROVE) requires a persisted, eligible decision
  record and runs only on the deterministic live path (`approval_evaluate.py`
  gates + final revalidation); agents never call it directly. `add_comment_review`
  is the always-`COMMENT` advisory mutation.
- Unsupported operations enter `human_required`; agents never construct an API call.
- Local Git transport for fetch/push is outside the GitHub API transport split.

REST cannot establish review-thread `isResolved`. Author-triage records `resolution_state: unknown` and enters `human_required` before evaluation until the operator supplies the actionable comment IDs.

## Assurance router

Axes:

- Capability: `economy < workhorse < frontier`
- Effort: `low < medium < high < xhigh`
- Independence: `single < challenger < panel < human`

Minimum profiles:

| Situation | Capability | Effort | Independence |
|---|---|---|---|
| Narrow re-review of known fixes | workhorse | medium | single |
| First incoming review | workhorse | medium | challenger |
| Security, migration, workflow, deployment, or broad cross-system change | frontier | high | challenger |
| Author-triage before branch mutation | workhorse; frontier for sensitive paths | high | challenger |
| Material model disagreement | frontier | xhigh | panel |
| Reserved authority or unresolved panel | n/a | n/a | human |

Panel completeness: a panel is `complete` only when every required slot produced a freshly written verdict this attempt. A slot with fewer fresh verdicts than the profile requires (for example, one reviewer where `challenger` wants two) must never be treated as approval — it is `MISSING_EVIDENCE` / not-complete, and the dispatcher escalates rather than treating a lone `SUPPORTED` as success. Each escalated attempt clears prior slot files so a stale (lower-profile) verdict is never consumed.

Fallbacks:

Fallbacks:

- `models.primary` and `models.secondary` are two ordered reviewer lanes. The
  first successful candidate in each lane is used; candidates after it are
  failovers, not additional reviewers.
- Default preference is native Claude, then native Codex. OpenRouter candidates
  follow only when that lane's preferred native runner is unavailable.
- A candidate may meet a lower minimum capability (for example, a frontier model
  may serve a workhorse review); the router never lowers the recorded minimum.
- OpenRouter fallbacks must use exact, non-alias model slugs and span distinct
  model-provider families. Configure value-oriented coding/reasoning models
  first, then a higher-quality independent alternative.
- Two reviewers must have different concrete provider/model identities and different independence families.
- Network/5xx failures retry once. Auth, quota, unavailable-model, and capability failures immediately advance.
- Failed candidates receive a cooldown. Successful probes restore preferred order.
- A first-review panel with one result saves `degraded_draft`; it performs no GitHub mutation and files no issue.
- A mechanically narrow re-review may intentionally complete with one reviewer.

## Severity and authority

- `blocker`: wrong now or violates a stated rule. Always an advisory comment. May
  additionally become a formal `CHANGES_REQUESTED` review, but only when the
  finding is CORROBORATED and `authority.request_changes` is `live` (see below).
- `high`: wrong when the next planned dependency lands.
- `medium`: works, but a maintainer will predictably infer the wrong contract.
- `low`: bounded clarity or maintainability defect.

Confirmed High/Medium/Low findings create one deduplicated `by:agent` issue each. Incoming review actions are always advisory comments. Automated approval happens only on the deterministic live path: every gate in `approval_evaluate.py` passes, a persisted approval-eligible decision record exists, and final revalidation reconfirms SHA/draft/checks/protected triggers before one `APPROVE` review is posted. It never merges changes, arms auto-merge, dismisses a review, bypasses protection, force-pushes, or approves the automation identity's own PR.

### Completed review that located defects

A reviewer that finds a real defect returns signal `DEFECTS_FOUND` with at least
one finding and a non-`clean` recommendation. When every completed reviewer
returns `DEFECTS_FOUND`, the assurance decision is `REQUEST_CHANGES`; raising
effort or capability is not attempted, because escalation cannot make a located
defect disappear. A mix of `DEFECTS_FOUND` and `SUPPORTED` is a disagreement
about the core question and escalates (panel, then human) rather than acting.

`REQUEST_CHANGES` is a *candidate* action, never an entitlement. Before any
mutation:

1. **Corroboration.** A blocking finding is verified only when the same finding
   (fingerprinted by severity + normalised location) is reported by two DISTINCT
   provider families, OR is reported by one family and cites a check that
   actually failed. Two models from the same provider family are not
   independent. A finding cannot borrow credibility from an unrelated failing
   check. Findings lacking evidence or a primary source are dropped.
2. **Authority.** `authority.request_changes` must be `live`. It is `disabled` by
   default, so verified defects escalate to a human until an operator enables it.
3. **Gate.** `action_gate.request_changes_gate` must pass, including a fresh
   revalidation that the head SHA is unchanged and the PR is not a draft.
   Revalidation fails closed: a transport error is a denial, never a pass, and
   never aborts the sweep.

Only corroborated findings appear in the posted review body; uncorroborated ones
are escalated to a human instead. The mutation is REST-verified after posting; an
unconfirmable mutation stops the job (`safe_stop`) and is never retried blind.

## Canary

1. One incoming-review job runs end to end. Continuous dispatch remains disabled until human inspection.
2. One author-triage job runs end to end. Continuous author dispatch remains disabled until human inspection.
3. Continuous dispatch may start only after both approvals are recorded in local state.

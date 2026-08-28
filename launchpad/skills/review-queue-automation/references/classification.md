# Deterministic and judgment boundaries

| Operation | Owner | Completion condition |
|---|---|---|
| Poll repositories, cache ETags, paginate, record rate limits | Script | REST snapshot committed transactionally |
| Detect queue transitions and current-head re-reviews | Script | One idempotent job per repo, PR, head, and lane |
| Run `pr_review_batch.py` and enforce holds | Script | Briefing saved; blocked jobs never dispatch |
| Claim, arbitrate, release, and verify assignee lease | Script | GitHub state and local lease record agree |
| Gather PR, diff, reviews, comments, issue, checks, and changed files | Script | Immutable nonce-enveloped evidence manifest saved |
| Select assurance profile | Script | Minimum capability, effort, and independence recorded |
| Resolve models, fallbacks, cooldowns, and distinct providers | Script | Required independent outputs or degraded draft saved |
| Interpret issue contract and surrounding implementation | AI | Structured claims cite local file and line evidence |
| Judge correctness, test adequacy, and severity | AI | Every finding is falsifiable and actionable |
| Adjudicate reviewer disagreement | AI | Surviving findings verified against a primary source |
| Select targeted missing evidence | AI | Narrow evidence request returned as structured data |
| Execute allowlisted GitHub reads | Script | REST response cached and rate headers recorded |
| Post the one allowed approval mutation (`approve_review`, event APPROVE) | Script | Persisted eligible decision + `approval_evaluate.py` gates + final revalidation pass; never by agent judgment |
| Run shadow backtest / current-head shadow | Script | Read-only report; forces shadow mode in memory; no mutation, no decision record |
| Label historical outcomes clean/adverse/contested/unknown | Script (input) | Independently sourced label + evidence source + cutoff; never derived from evaluator output or `merged` |
| Deduplicate and create finding issues | Script + AI | AI supplies issue content/type; script proves no fingerprint duplicate and creates once |
| Set up and remove isolated author worktrees | Script | Worktree inventory returns to its initial state |
| Implement confirmed author fixes and rebut invalid findings | AI | Changed code or evidence-backed rebuttal covers every finding |
| Run selected repository verification | Script | Raw command, exit status, and output saved |
| Commit, push, reply, and re-request | Script | Remote head equals pushed commit and reviewer request is visible |
| Resolve policy or authority questions | Human | Explicit human decision recorded |

Agents never call GitHub directly. Unsupported script operations become held jobs; they are not improvised with `gh`, REST, GraphQL, curl, MCP, or browser actions.

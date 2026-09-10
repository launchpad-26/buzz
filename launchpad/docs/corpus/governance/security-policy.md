---
id: governance-security-policy
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - operator
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "SECURITY.md, at the repository root, documents vulnerability reporting (GitHub private security advisory at github.com/block/buzz/security/advisories/new, or email buzz@block.xyz as fallback), an acknowledgment target of 48 hours and a full-response target of 7 days, supported-versions policy (main only; pre-1.0; no LTS branches), a set of security design principles (NIP-42/NIP-98 authentication, channel membership as the sole authorization mechanism, a hash-chained append-only audit log, OS-keyring desktop secret storage, input validation rules, TLS left to the deployer, and dependency scanning), and a coordinated-disclosure policy."
    entry_class: FACT
    evidence:
      - "SECURITY.md"
  - statement: "SECURITY.md's reporting channel is upstream's own: the private-advisory link and the fallback email both resolve to block/buzz, not to launchpad-26/buzz specifically, and this fork's own private vulnerability reporting is disabled."
    entry_class: FACT
    evidence:
      - "SECURITY.md"
      - "gh_api(repos/launchpad-26/buzz/private-vulnerability-reporting) -> {\"enabled\":false}"
  - statement: "SECURITY.md states, under Dependency Management, 'We use cargo audit in CI to scan for known vulnerabilities in dependencies,' and separately that '#![deny(unsafe_code)] is enforced across all crates.'"
    entry_class: FACT
    evidence:
      - "SECURITY.md"
  - statement: "The CI job actually named Security (.github/workflows/ci.yml) runs 'cargo-deny check' against deny.toml, not the cargo-audit tool SECURITY.md names; deny.toml carries an [advisories] table with a reasoned per-advisory ignore list (RUSTSEC-2024-0384, RUSTSEC-2024-0436, RUSTSEC-2026-0194, RUSTSEC-2026-0195), confirming cargo-deny is configured to check the RustSec advisory database, just under a different tool name than the one documented."
    entry_class: FACT
    evidence:
      - ".github/workflows/ci.yml"
      - "deny.toml"
  - statement: "SECURITY.md's 'cargo audit' sentence is stale or imprecise relative to what this fork's CI actually runs for dependency-vulnerability scanning; the two tools (cargo-audit, cargo-deny) are related but distinct, and nothing in the inspected files explains which came first or why the document was not updated."
    entry_class: INFERENCE
    evidence:
      - "SECURITY.md"
      - ".github/workflows/ci.yml"
      - "deny.toml"
    confidence: 0.7
  - statement: "launchpad/AGENTS.md §8 states three binding rules under the heading 'Security': never open a public issue for a vulnerability (use the private advisory link on the issue chooser page); this repository is public, so config is fine but credentials never are, and secrets must be parameterised out of files from the first commit; and never add a secret, key, token, or private hostname to a tracked file."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/SECURITY-POSTURE.md records the cohort's accepted risks (each with a DECIDED status marker, a stated reason, and a linked source issue), names one open, undecided gap (#43 — agent execution on the relay turning the host into a code-distribution point) that its own text says is deliberately not narrowed here because #42/#43 reserve that question to a separate ADR, and lists twelve open security-related ADR decisions (#25, #26, #27, #28, #43, #44, #45, #46, #47, #63, #64, #65) as of the date it records."
    entry_class: FACT
    evidence:
      - "launchpad/SECURITY-POSTURE.md"
  - statement: "launchpad/SECURITY-POSTURE.md states that detailed, current security posture is tracked in a private companion repository, buzz-infrastructure, and that this public document deliberately does not restate a control-by-control readiness table because 'a table's shape is what makes it a gap map, not the accuracy of what it currently says.'"
    entry_class: FACT
    evidence:
      - "launchpad/SECURITY-POSTURE.md"
  - statement: "ADR-0006 (accepted, 2026-08-13) decided gitleaks as the fork's secret-scanning engine, run both on the PR-diff path and on a scheduled full-history scan, with detection rules and the allowlist held together in one repo-root .gitleaks.toml extending gitleaks' default ruleset; the allowlist is required to be hand-maintained TOML blocks each carrying a comment stating why a match is safe, and gitleaks' auto-generated --baseline-path mechanism is explicitly rejected as unsafe because it can silently accept a real finding."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md"
  - statement: "ADR-0006 explicitly scopes itself to the CI-side detection engine only and does not decide whether GitHub's native secret scanning and push protection are enabled, because enabling those requires repository admin; it records that request as tracked separately under #72."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md"
  - statement: "ADR-0006's own Consequences section states plainly that a green gitleaks run only means 'no new uncaught pattern, never no secrets,' and that an over-broad allowlist entry silences detection without looking like it changed anything, which is why the decision requires each entry scoped to a rule or specific match and never a whole file or path."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md"
  - statement: ".gitleaks.toml extends gitleaks' default ruleset (useDefault = true) with fork-specific rules for Nostr nsec1 private keys, a BUZZ_PRIVATE_KEY/NSEC/SECKEY hex-key assignment shape, glibc/Unix crypt hashes, BUZZ_S3_ACCESS_KEY/SECRET_KEY assignments, and a Postgres URL carrying an embedded password (with a scoped allowlist for the known-safe localhost dev credential and for .env.example placeholder files); a top-level [allowlist] additionally excludes the scanner's own synthetic test fixtures and one literal documented placeholder value."
    entry_class: FACT
    evidence:
      - ".gitleaks.toml"
  - statement: ".github/workflows/launchpad-security-audit.yml runs on a daily schedule, on workflow_dispatch, and on every pull_request unfiltered by path (deliberately, per its own comment, because a leaked credential is exactly as real in crates/ or desktop/ as anywhere else); it installs a pinned, checksum-verified gitleaks binary, runs the harness's own test suite with REQUIRE_GITLEAKS_RULESET=1 so a broken gitleaks install fails the job rather than silently skipping the ruleset test, and then runs launchpad/scripts/security_audit.py, all with contents: read permission only and no repository secret referenced anywhere in the file."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-security-audit.yml"
  - statement: "launchpad/scripts/security_audit_registry.py registers exactly five checks that security_audit.py runs: harness_self_test, secret_material_scan, ignore_coverage, tracked_sensitive_files, and agent_surface_secret_scan; its own docstring states that further #62 checks (Actions hygiene, settings attestation) are not yet landed."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/security_audit_registry.py"
  - statement: "ADR-0008 (accepted, 2026-08-15) decided the repository security audit runs with the bare GITHUB_TOKEN only, with no admin-scoped credential added; where a setting cannot be read at that privilege (secret-scanning-alert status and branch-protection status both 404 ambiguously at this privilege level), the audit is required to report indeterminate rather than guess, and the decision states plainly that indeterminate must never render as pass."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0008-security-audit-privilege.md"
  - statement: "ADR-0008 records a pre-agreed upgrade path (a GitHub App scoped to administration: read, installed on this repository specifically) for if the ambiguous-privilege limitation is ever triggered, and states that until then the repository owner's own direct admin access is the safety net for checking those two settings manually."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0008-security-audit-privilege.md"
  - statement: ".github/workflows/codex-security-review.yml runs an AI-generated security/correctness review (via openai/codex-action) against every non-draft pull request targeting main, but every job in the file is gated on github.repository == 'block/buzz'; on launchpad-26/buzz that condition is never true, so this workflow — present in this fork's tree because it is inherited, unmodified, from upstream — never actually executes here."
    entry_class: FACT
    evidence:
      - ".github/workflows/codex-security-review.yml"
  - statement: "The launchpad branch on launchpad-26/buzz is one of exactly two protected branches (of 687 total) in this repository, confirmed by name rather than by paging an unfiltered branch list."
    entry_class: FACT
    evidence:
      - "gh_api(repos/launchpad-26/buzz/branches/launchpad) -> {\"name\":\"launchpad\",\"protected\":true}"
  - statement: "The specific branch-protection rules in force on launchpad (required approving review count, code-owner review requirement, admin enforcement) are not readable at this task's privilege level: repos/launchpad-26/buzz/branches/launchpad/protection returns 404, the repository rulesets endpoint returns an empty array under this token, and this token's own permissions are {admin: false, maintain: true, push: true} — the same ambiguous-404 shape ADR-0008 already documents for a different pair of settings, so these three rules are recorded here as unknown, not as absent."
    entry_class: FACT
    evidence:
      - "gh_api(repos/launchpad-26/buzz/branches/launchpad/protection) -> 404"
      - "gh_api(repos/launchpad-26/buzz/rulesets) -> []"
      - "gh_api(repos/launchpad-26/buzz) -> .permissions = {\"admin\":false,\"maintain\":true,\"pull\":true,\"push\":true,\"triage\":true}"
  - statement: ".github/CODEOWNERS's sole rule, '* @block/buzz-oss-team', is invalid: the GitHub codeowners-errors endpoint reports 'Unknown owner' for that team on that line, so CODEOWNERS asserts no enforceable review requirement on this fork today regardless of what branch protection separately requires."
    entry_class: FACT
    evidence:
      - "gh_api(repos/launchpad-26/buzz/codeowners/errors) -> {\"errors\":[{\"line\":1,\"message\":\"Unknown owner on line 1...\",\"path\":\".github/CODEOWNERS\"}]}"
  - statement: "No DCO Check status check runs on this fork: a recently merged pull request's (#1978) full statusCheckRollup lists no check by that name, in contrast with upstream block/buzz where such a check is confirmed present on its own PRs."
    entry_class: FACT
    evidence:
      - "gh_pr_view(launchpad-26/buzz#1978, statusCheckRollup) -> no entry named 'DCO Check'"
  - statement: "crates/buzz-auth implements the technical authentication surface SECURITY.md describes at a policy level: NIP-42 challenge/response over WebSocket and NIP-98 HTTP Auth are implemented in separate modules, alongside channel access checking, per-connection rate limiting, and NIP-98 replay protection; the crate's own module doc states that AUTH events (kind:22242) are never stored or logged and that there is no JWT validation, token management, or IdP runtime dependency."
    entry_class: FACT
    evidence:
      - "crates/buzz-auth/src/lib.rs"
  - statement: "architecture-principles-community-is-security-boundary is a merged corpus node (status: draft) documenting that every request's community/tenant is bound once, fails closed on an unmapped or unresolvable host, and is never derived from client-supplied input — the architectural mechanism this policy node's Scope and authority section explicitly declines to restate."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/architecture/principles/community-is-security-boundary.md"
  - statement: "Issue #915's Definition of Done requires this node to state scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define enforcement/checks and an exception/escalation process, and link decisions or higher-order policy instead of duplicating them — the same four clauses launchpad/docs/corpus/templates/policy.md's own Required sections already structure this document around."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#915 definition of done"
relationships:
  - type: implements
    target: corpus-template-policy
  - type: references
    target: architecture-principles-community-is-security-boundary
---

# Policy: Security disclosure, scanning, and review process

What this fork requires for handling a security vulnerability, for keeping secrets out
of a public repository, and for reviewing changes before they merge — the governance
and process half of security, not the technical mechanism that implements it.

## Scope and authority

**This node governs** three things for `launchpad-26/buzz`: how a vulnerability is
reported and disclosed, how secret material is kept out of tracked files and detected
if it slips in, and what review a change goes through before it merges. It states what
is required, what currently checks each requirement, and where the process has open
gaps rather than a settled answer.

**It does not govern** the technical mechanism any of this rests on. `crates/buzz-auth`
implements the authentication and authorization Buzz actually performs at connection
time (NIP-42, NIP-98, channel-membership checks, rate limiting, replay protection) —
that is architecture and code, reviewed and changed like any other crate, not a
governance requirement. `architecture-principles-community-is-security-boundary`
documents the specific invariant that a request's community/tenant is bound once and
fails closed — again, a technical mechanism, not a process rule. This node references
that node rather than restating it, and neither of those two is this node's subject.

**Its authority is derived, not original**, matching every corpus node built from
`launchpad/docs/corpus/templates/policy.md` (this node `implements` that template).
Three sources carry the actual rules this document reports:

- `launchpad/AGENTS.md` §8 — the fork's own binding rules on public disclosure and
  never committing a secret.
- `SECURITY.md` (repository root) — vulnerability-reporting process, supported
  versions, and (at a policy level, not an implementation level) the security design
  principles the relay follows.
- `launchpad/decisions/ADR-0006` and `ADR-0008` — the accepted decisions governing the
  secret-scanning engine, its allowlist, and the privilege the security-audit workflow
  runs with.

**Where this node and any of those three disagree, they win** — this is a description
of what they require, not a fourth, independent source of authority. Where this node
and `launchpad/docs/corpus/AGENTS.md` disagree about corpus mechanics (front matter,
evidence classification, node creation), `AGENTS.md` wins, per its own stated
precedence rule.

| For | Read |
|---|---|
| Vulnerability reporting and disclosure | `SECURITY.md` |
| The public-repository secret rule | `launchpad/AGENTS.md` §8 |
| Secret-scanning engine and allowlist | `launchpad/decisions/ADR-0006-secret-scanning-engine-and-allowlist-location.md`, `.gitleaks.toml` |
| What privilege the security audit runs with | `launchpad/decisions/ADR-0008-security-audit-privilege.md` |
| Current, cohort-specific accepted risks and open decisions | `launchpad/SECURITY-POSTURE.md` |
| The technical authentication/authorization mechanism | `crates/buzz-auth/src/lib.rs` |
| The community/tenant isolation invariant | `architecture-principles-community-is-security-boundary` |

## MUST

| # | Requirement |
|---|---|
| **S1** | A security vulnerability MUST NOT be reported through a public GitHub issue, pull request, or discussion. It MUST be reported through a private channel — `SECURITY.md`'s GitHub private security advisory link, or its fallback email if that is unavailable. Enforced by nothing mechanical; a reporter who does not read `SECURITY.md` or `AGENTS.md` §8 first can still open a public issue, and no check here catches that after the fact. |
| **S2** | A secret, key, token, or private hostname MUST NOT be added to a tracked file in this repository. Enforced partially and after the fact: `.github/workflows/launchpad-security-audit.yml` runs a gitleaks-based scan on every pull request and on a daily schedule (see Enforcement), which can catch a violation once committed, but nothing blocks the commit itself — GitHub's native push protection, the one *preventive* control available, is an admin-only setting whose current on/off state this node cannot establish (see Scope and omissions). |
| **S3** | A `.gitleaks.toml` allowlist entry MUST be a hand-maintained TOML `[allowlist]` or per-rule `allowlist` block carrying a comment stating why the match is safe. The auto-generated `--baseline-path` mechanism MUST NOT be used, per ADR-0006's own reasoning: it "requires nothing" from a human and can silently accept a real finding. Enforced by review only — nothing mechanical checks that an allowlist entry carries a reason or checks its scope. |
| **S4** | The security audit MUST report `indeterminate`, never `pass`, for a setting it cannot read at its current privilege (bare `GITHUB_TOKEN`, no admin). This is ADR-0008's own decision, stated there in those terms. Enforced by the audit's design, not by a separate check on the audit itself — nothing here re-verifies that the audit code actually honors this on every ambiguous case. |

## SHOULD

| # | Guidance |
|---|---|
| **T1** | A reporter SHOULD give the maintainers reasonable time to fix a vulnerability before any public disclosure, SHOULD avoid accessing or modifying data that is not theirs, and SHOULD NOT perform denial-of-service testing against production systems — `SECURITY.md`'s own coordinated-disclosure asks. Departing from these is the reporter's own judgment call in an adversarial situation; nothing in this repository can compel a reporter's conduct. |
| **T2** | A production deployment SHOULD terminate TLS at the relay or a reverse proxy in front of it — `SECURITY.md`'s own guidance, stated there as intentional: the relay does not enforce TLS itself, to stay flexible behind different load balancers and ingress controllers. |
| **T3** | Dependency vulnerabilities SHOULD be caught by an automated advisory scan in CI before merge. This currently happens — `cargo-deny check` runs an `[advisories]` check against `deny.toml` in the `Security` CI job — but see Scope and omissions for the mismatch between that and what `SECURITY.md`'s own text names. |

## Enforcement

**Mechanical, and confirmed by reading the workflow rather than assumed from its
name:**

- `.github/workflows/launchpad-security-audit.yml` runs gitleaks (pinned, checksum
  verified) plus five registered checks
  (`launchpad/scripts/security_audit_registry.py`: `harness_self_test`,
  `secret_material_scan`, `ignore_coverage`, `tracked_sensitive_files`,
  `agent_surface_secret_scan`) on every pull request, unfiltered by path, and on a
  daily schedule.
- `.github/workflows/ci.yml`'s `Security` job runs `cargo-deny check` against
  `deny.toml`'s `[advisories]` table on every push and on any PR touching Rust.

**Review-only, or not enforced at all:**

- `launchpad/AGENTS.md` §8's "never commit a secret" rule has no pre-commit
  mechanical check in this repository; the gitleaks-based audit above is the only
  automated backstop, and it runs *after* a commit exists, not before one is made.
- Whether GitHub's native secret scanning and push protection — the one genuinely
  *preventive* control available — are enabled cannot be established at this task's
  privilege (see Scope and omissions); `ADR-0006` records this as a separate,
  admin-gated ask tracked under `#72`, not as something this audit itself turns on.
- `.github/CODEOWNERS`'s single rule is invalid (`Unknown owner`, confirmed via the
  GitHub API), so it currently enforces no code-owner review requirement on any pull
  request, regardless of what the `launchpad` branch's own protection settings
  separately require.
- No `DCO Check` runs on this fork's pull requests, confirmed absent from a recently
  merged PR's status checks, unlike upstream `block/buzz` where that check is
  present.
- `.github/workflows/codex-security-review.yml` — an AI-generated per-PR security
  review — is present in this fork's file tree (inherited from upstream) but every
  job in it is gated `github.repository == 'block/buzz'`; that condition is never
  true here, so it never runs on this fork's own pull requests despite being visible
  in `git log` and in the workflow list.

**What a passing run does NOT establish**, named because both this template and
`ADR-0006` require it stated rather than implied:

| Passing check | Does NOT establish |
|---|---|
| Green `launchpad-security-audit.yml` run | That no secret exists in the repository — only that no pattern any current rule recognizes was found. `ADR-0006`'s own words: "a green run only means 'no *new* uncaught pattern,' never 'no secrets.'" A genuinely novel secret shape not yet written into `.gitleaks.toml` passes silently. |
| Green `Security` (`cargo-deny`) CI job | That every dependency is free of known vulnerabilities — only that none of the *unignored* advisories in the RustSec database match, and `deny.toml` carries four explicit, reasoned ignores. |
| `launchpad` branch showing `protected: true` | Which specific rules that protection enforces — required review count, code-owner review, admin enforcement are all unread at this privilege (see Scope and omissions). |
| `.github/CODEOWNERS` existing in the tree | That it enforces anything — its one rule is invalid and asserts no owner GitHub recognizes. |

## Exceptions and escalation

**There is no exemption from S1 or S2.** A vulnerability report or a secret does not
get a "just this once" public exception; the private channel and the never-commit
rule apply unconditionally.

**A `.gitleaks.toml` allowlist entry is the one place a departure is legitimate, and
it is departed from in the open, not silently.** `ADR-0006` requires every entry to
carry a `#` comment naming the reason, scoped to a rule or a specific match — never a
whole file or path — so a reviewer reading `.gitleaks.toml` can see exactly what was
excluded and why, in the same pull request that adds it.

**A disputed classification (is this actually a secret, is this allowlist entry too
broad) is a review judgment, not an automated gate.** Nothing here decides it
mechanically; it is raised on the pull request, and if reviewer and author disagree,
it is filed as an issue against the relevant ADR (`ADR-0006` for scanning scope,
`ADR-0008` for audit privilege) rather than resolved by whoever is more insistent.

**A security question this document does not reach is escalated through
`launchpad/SECURITY-POSTURE.md`'s own list of open ADRs** (`#25`, `#26`, `#27`, `#28`,
`#43`, `#44`, `#45`, `#46`, `#47`, `#63`, `#64`, `#65` as of that document's own
recorded date), not invented here. A genuinely new gap not already tracked there is
raised as a new issue against the cohort, following `launchpad/AGENTS.md`'s own issue
routing.

**`status: flagged` is not in use on this node.** No two authoritative sources of the
same claim type were found in conflict while drafting it; if one is found later,
`ADR-0029`'s rule governs, not a local workaround here.

## Scope and omissions

**This node covers** vulnerability disclosure, keeping secrets out of tracked files
and detecting them if they slip in, the privilege the automated security audit runs
with, and what review currently gates a merge — for `launchpad-26/buzz` specifically.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The technical authentication/authorization mechanism (NIP-42, NIP-98, channel access, rate limiting, replay protection) | `crates/buzz-auth`, and any future corpus node documenting it directly |
| The community/tenant isolation invariant | `architecture-principles-community-is-security-boundary` |
| Host and infrastructure hardening, deployment-time controls | `launchpad/SECURITY-POSTURE.md`, the private `buzz-infrastructure` companion repository, and the open ADRs it lists (`#25`–`#47`) |
| Which specific rules the `launchpad` branch's protection enforces | Unreadable at this task's GitHub API privilege; an admin (the repository owner holds direct admin access per `ADR-0008`) can check this in the GitHub UI |
| Fixing the invalid `.github/CODEOWNERS` entry | `#1428` |
| The missing `DCO Check` on this fork | `#2044` |
| Whether GitHub's native secret scanning and push protection are enabled | Admin-only setting; tracked as a request under `#72` per `ADR-0006` |
| Reconciling `SECURITY.md`'s "cargo audit" sentence against the `cargo-deny`-based check this fork's CI actually runs | Not filed as an issue by this task; named here as a documentation/reality mismatch |

**Expected but not verified when this node was written:**

- **Whether `SECURITY.md`'s "cargo audit" line reflects a genuine historical tool
  change (cargo-audit once ran, then was replaced by cargo-deny, and the doc was
  never updated) or was simply always inaccurate.** Neither this file nor
  `.github/workflows/ci.yml`'s history was read far enough back to distinguish the
  two; it is reported here as a mismatch between documentation and current CI, not as
  a dated regression.
- **Whether `.github/workflows/codex-security-review.yml`'s condition
  (`github.repository == 'block/buzz'`) has ever been intentionally considered for
  this fork**, or is simply carried over unmodified because nobody has needed it to
  run here yet. Its file presence in the tree, confirmed directly, does not by itself
  answer that.
- **Whether the `launchpad` branch's specific protection rules (required approving
  review count, code-owner review requirement, admin enforcement) match what this
  document's `Enforcement` section assumes them to plausibly be.** They were not
  established — `/protection` 404s and the rulesets endpoint returned an empty array
  under this task's token, and per `ADR-0008`'s own precedent for exactly this shape
  of ambiguity, that is recorded as unknown, not as "no protection."
- **Whether GitHub's native secret scanning and push protection are currently
  enabled on this fork.** `ADR-0006` names this as a live, actionable ask directed at
  whoever on the cohort holds admin; this node did not re-check its current state.

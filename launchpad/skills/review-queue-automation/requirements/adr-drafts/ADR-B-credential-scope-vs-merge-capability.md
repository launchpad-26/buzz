adr: does the security section's credential scope admit the merge write C6/AC14 require AND the remediation push Security bullet 3 describes

## Question

Can a single credential scoped, as the Security implications section states, to "pull-requests write and contents
read" perform **both** of the two write-shaped capabilities #2006 elsewhere asks RQA to have: (a) merging a pull
request where a repository is configured to merge after review (C6, AC14), and (b) modifying and pushing a branch
to remediate a mechanical finding (Security bullet 3, contingent on [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) resolving toward direct code
modification) — or does either capability need a broader scope than the Security section enumerates?

## Why the extract cannot settle it

#2006 (pinned `updated_at` 2026-09-01T06:34:12Z, body SHA-256
`12bb2a6d5ca0f55446332e9f4300faa1a392b835f6457f49c303ea5f1ef596dd`) states all of the following without
reconciling them:

- C6: **"End-to-end GitHub review responsibility. Must manage the lifecycle through authoritative APPROVED or
  CHANGES_REQUESTED. Whether RQA also merges is configurable per repository."**
- AC14: **"...one repository can be configured to merge after review and another configured not to, with both
  behaving accordingly."**
- Security implications, bullet 3: **"AC09 asks RQA to modify and push a branch"** (remediation).
- Security implications, bullet 6: **"Credentials stay narrow. A GitHub token scoped to the target repositories
  with pull-requests write and contents read; no deploy keys, no relay or VPS credentials, no access to a
  contributor's machine."**

**This is not a textual self-contradiction the way [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) is.** Nothing in #2006's own words asserts that
"pull-requests write and contents read" is insufficient for a merge write or a branch push — that claim depends on
an external premise: how GitHub's own permission model gates those two actions. [INFERENCE — this premise (that
merging and pushing a commit ordinarily require a write-level permission on repository contents, not a read-level
one) is domain knowledge about GitHub's product, not a fact stated anywhere in the pinned extract; verifying it
would mean reading GitHub's own permission documentation, which this clean-room task does not admit.] The
Security section enumerates exactly two scopes and never says whether merge-configured or remediation-authorised
repositories carry a broader credential than others. The extract gives no basis, on its own text alone, for
choosing between "the enumeration is exhaustive and both capabilities are achievable within it" and "one or both
capabilities need more than the enumeration states."

## Affected requirement rows

In [`requirements-specification.md`](../requirements-specification.md):

- [RQA-NFR-024](../requirements-specification.md#rqa-nfr-024) — "The credential the system holds shall carry pull-request write and repository-content read on
  the repositories it manages." (round 4: the floor half of a row split that previously combined floor and
  ceiling in one two-`shall` statement.)
- [RQA-NFR-030](../requirements-specification.md#rqa-nfr-030) — "The credential the system holds shall have no permission broader than pull-request write and
  repository-content read, and no permission on any repository outside those it manages." (round 4: the ceiling
  half of the same split; round 5 added the repository-scope ceiling clause.)
- (For context, not itself blocked on this question: RQA-NFR-008 and RQA-FR-029, which state the per-repository
  merge-configurability obligation independently of what credential scope satisfies it; and RQA-NFR-019/020/021,
  which state remediation-authority bounds independently of whether [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) resolves toward RQA performing the
  push at all.)

## Options

1. **The enumeration is exhaustive; both capabilities are achieved within it.** GitHub's merge and branch-push
   operations are treated as reachable under "contents read" plus whatever "pull-requests write" already covers,
   with no separate contents-write grant — RQA-NFR-024/RQA-NFR-030 stand as written, and both a merge-configured
   repository and a remediation-authorised one hold the same credential shape as any other.
2. **Merge-configured and/or remediation-authorised repositories carry a broader credential than the Security
   section enumerates**, and RQA-NFR-030's "no permission broader than pull-request write and repository-content
   read" applies only to a repository configured for neither; the broader ceiling for one or both cases is a
   separate, currently unstated requirement.
3. **RQA never itself performs the write.** For merging, "whether RQA also merges" (C6) is satisfied by RQA
   driving GitHub's own auto-merge feature or an equivalent mechanism that does not require RQA's own credential
   to hold a contents-write scope. For remediation, this option coincides with [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) option 1 (RQA never
   directly modifies code), which removes the push capability from scope entirely rather than reconciling it with
   bullet 6.

No option is recommended here.

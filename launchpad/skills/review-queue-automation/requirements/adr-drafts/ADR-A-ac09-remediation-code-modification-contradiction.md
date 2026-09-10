adr: does AC09's mechanical-finding remediation require RQA to directly modify and push code, or not

## Question

Does resolving a mechanical, policy-permitted finding (AC09) require RQA itself to modify a pull request's code
and push a branch, or does it not?

## Why the extract cannot settle it

Two clauses of #2006 (pinned `updated_at` 2026-09-01T06:34:12Z, body SHA-256
`12bb2a6d5ca0f55446332e9f4300faa1a392b835f6457f49c303ea5f1ef596dd`) state opposite answers to the same question:

- AC09's own closing sentence: **"Per the baseline, this does not require RQA to modify code directly."**
- The Security implications section, bullet 3: **"Remediation authority is the largest new exposure. AC09 asks
  RQA to modify and push a branch."**

The first says direct code modification is not required by AC09; the second says AC09 asks for exactly that, and
goes on to specify authority controls (separately gated, bounded to mechanical categories, isolated from the
working tree, never able to force-push, merge, bypass protection or touch a protected branch) that only make sense
if RQA *does* modify and push code. Nothing else in the extract explains the discrepancy — no third clause
distinguishes "modifying code" from "supplying a remedy that something else applies", and no clause says the
Security section's remediation-authority bullet describes a superseded or optional path.

This is a genuine textual self-contradiction within #2006, independent of any fact outside the extract — unlike
[`ADR-B`](ADR-B-credential-scope-vs-merge-capability.md) below, which rests on an external premise, or [`ADR-C`](ADR-C-external-harness-provenance-authentication.md), which is a design choice rather than a conflict.

## Affected requirement rows

In [`requirements-specification.md`](../requirements-specification.md):

- [RQA-FR-017](../requirements-specification.md#rqa-fr-017) — "A finding classified as mechanical and permitted by policy shall be resolved without unnecessarily
  creating human intervention or a complete re-review cycle."
- [RQA-FR-018](../requirements-specification.md#rqa-fr-018) — "Resolving a mechanical finding shall not invalidate unrelated review work that remains valid."
- [RQA-NFR-019](../requirements-specification.md#rqa-nfr-019) — "Remediation authority shall be bounded to only the finding categories a repository's policy
  names as mechanical."
- [RQA-NFR-020](../requirements-specification.md#rqa-nfr-020) — "Remediation shall be isolated from the repository's working tree."
- [RQA-NFR-021](../requirements-specification.md#rqa-nfr-021) — "Remediation shall never force-push, merge, bypass branch protection, or touch a protected
  branch."

All five hold as agreed obligations (status `DECIDED`) under every option below — resolving a mechanical finding
without unnecessary escalation, and not invalidating unrelated valid work, are required regardless of which answer
this question gets. What this question decides is narrower: whether RQA-NFR-019/020/021 constrain a real,
exercised capability (RQA modifying and pushing code) or describe authority controls on a capability #2006 does
not, in this scope, actually grant.

## Options

1. **Scope amendment: RQA never directly modifies code.** Mechanical-finding resolution is limited to actions
   that do not push a branch (for example, surfacing the exact remedy for someone or something else to apply).
   AC09's own text says direct modification is not *required* — narrower than "never happens" — so choosing this
   option reads AC09 as also foreclosing the option, not merely declining to mandate it, which goes beyond what
   AC09 itself states and is therefore a deliberate scope amendment, not a plain reading. Under this option, the
   Security section's remediation-authority bullet describes a capability #2006 does not actually grant under
   this scope, and RQA-NFR-019/020/021 have no live case to constrain unless a later PRD grants push authority.
2. **The Security section governs: RQA does directly modify and push code for mechanical findings.** AC09's
   closing sentence is read as narrower than it states — meaning "this does not *require* direct modification as
   the only path" rather than "direct modification does not happen" — and RQA-NFR-019/020/021 become live,
   binding constraints on a remediation capability that does write to a branch. (If this option is chosen, [`ADR-B`](ADR-B-credential-scope-vs-merge-capability.md)
   below extends to ask whether the Security section's own credential-scope enumeration can perform the push this
   option grants.)
3. **Source-minimal: direct modification is not required, and #2006 does not decide whether it happens.** AC09
   says only that direct modification is not *required* by the baseline; it neither mandates nor forbids RQA
   from having that capability. Under this option, this specification takes no position on whether RQA modifies
   code — that becomes a later feature's own scope decision — and RQA-NFR-019/020/021 stand as pre-emptive
   authority controls: *if* a later feature grants remediation the capability to modify and push code, CL-057's
   bounds govern it automatically, without this ADR having had to decide the question in advance. This is the
   option that adds the least to AC09's own stated language.
4. **Split by finding sub-category.** Some mechanical findings are resolved without code modification (e.g.
   re-running review) and others require it; #2006 does not state where that line falls, and this option would
   require drawing one not present in the extract.

No option is recommended here.

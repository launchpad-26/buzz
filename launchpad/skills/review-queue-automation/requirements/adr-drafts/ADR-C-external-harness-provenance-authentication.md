adr: how should an externally-supplied harness's provenance claim be authenticated, given AC15's no-source-change rule

## Question

AC15 requires that a harness not built into RQA be able to participate in a review "by satisfying the published
interaction contract alone, with no change to RQA's own source." The Security implications section requires that
a provenance record (reviewer identity, harness, model, provider — AC06) never be writable by the reviewed content
or by an unauthenticated model response. #2006 never says how an externally-supplied harness's self-reported
identity is authenticated to satisfy the second requirement while satisfying the first — this is an **undecided
design choice at the intersection of the two**, not a conflict between them: nothing in AC15 or Security bullet 4
asserts that an external harness's identity must go unauthenticated, and nothing forecloses a published contract
that itself carries an authentication mechanism (AC15's option 1 below demonstrates the two are compatible in
principle). The gap is that #2006 does not say which shape that mechanism takes.

## Why the extract cannot settle it

#2006 (pinned `updated_at` 2026-09-01T06:34:12Z, body SHA-256
`12bb2a6d5ca0f55446332e9f4300faa1a392b835f6457f49c303ea5f1ef596dd`) states both obligations without addressing
their intersection:

- AC15: **"A harness not built into RQA participates in a review by satisfying the published interaction contract
  alone, with no change to RQA's own source."**
- Security implications, bullet 4: **"Provenance must be forgeable-proof. AC06 records reviewer identity, harness,
  model and provider. If that record can be written by the reviewed content or by an unauthenticated model
  response, the audit trail is worse than none."**

A harness "not built into RQA" is, by definition, external to RQA and reports its own identity as part of
participating. Authenticating that self-report against forgery ordinarily requires *some* capability to verify
it — a shared secret, a signature check, a registration step — and #2006 does not say whether that capability
lives in the published contract itself (harness-agnostic, built once) or requires something specific to each new
harness. It also does not say whether "no change to RQA's own source" was meant to exclude configuration (as
opposed to code) changes. Neither AC15 nor bullet 4, read on its own terms, rules any of this out or in — which is
exactly why this is a design choice for #2006's implementer to make, not a contradiction for this specification to
flag as unresolved in the source text.

## Affected requirement rows

In [`requirements-specification.md`](../requirements-specification.md):

- [RQA-FR-030](../requirements-specification.md#rqa-fr-030) — "A harness not built into the system shall be able to participate in a review by satisfying the
  published interaction contract alone, with no change to the system's own source."
- [RQA-NFR-022](../requirements-specification.md#rqa-nfr-022) — "A provenance record shall never be writable by the reviewed content or by an unauthenticated
  model response."
- [RQA-NFR-028](../requirements-specification.md#rqa-nfr-028) — "A provenance record shall be protected against forgery or alteration by any actor lacking
  authority to write it." (appended round 2: the general, mechanism-free provenance-integrity obligation CL-058
  also carries, split out from RQA-NFR-022's specific untrusted-writer case.)

## Options

1. **The published interaction contract itself carries the authentication mechanism** (e.g. every conformant
   harness signs its report against a key the operator configures once, outside RQA's source), so a new harness
   never requires an RQA source change and every harness's report is still authenticated. Source-conforming: both
   AC15 and Security bullet 4/RQA-NFR-028 hold as stated.
2. **"No change to RQA's own source" excludes configuration**, and registering a new harness's verification
   material is a configuration step, not a source change — narrowing AC15's guarantee to "no code change" rather
   than "no change of any kind." Source-conforming: both AC15 (under this narrower reading) and Security bullet
   4/RQA-NFR-028 hold as stated.
3. **Self-reported harness identity is accepted as advisory, not authenticated**, with RQA-NFR-022's/RQA-NFR-028's
   forgeable-proof guarantee read as applying only to the fields RQA itself derives (e.g. which credential
   performed a write), not to a harness's free-text self-description. **This option is not a source-conforming
   resolution as it stands** — round 2 adversarial review noted that AC06 expressly includes harness/model/
   provider in the provenance record CL-058 requires be forgeable-proof, and Security bullet 4 draws no
   carve-out for self-reported fields; treating those fields as merely advisory lets an external harness write a
   false identity into an authoritative reconstruction, which is exactly the failure bullet 4 names. Choosing
   this option is therefore not a reading available within #2006 as extracted — it would require an explicit
   amendment to CL-058/AC06 narrowing what "provenance" covers, which is a decision beyond this ADR's scope to
   make unilaterally.

No option is recommended here.

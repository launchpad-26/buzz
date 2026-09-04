# ADR drafts

These are drafted decision records for questions that
[`requirements-specification.md`](../requirements-specification.md)'s derivation from
[#2006](https://github.com/launchpad-26/buzz/issues/2006) surfaced but does not settle: a genuine textual
contradiction in the source (`ADR-A`), a question that rests on a premise external to the source text (`ADR-B`),
and a design choice the source leaves open (`ADR-C`).

**None of these has been filed as a GitHub issue.** Filing is deferred until this requirements set is confirmed.
Each draft will become an ADR issue parented to #2006, and every `ADR-A`/`ADR-B`/`ADR-C` token in the
specification and its supporting documents will be replaced by the filed issue number at that point.

| Draft | Question |
|---|---|
| [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) | Does resolving a mechanical, policy-permitted finding require RQA to directly modify and push code, or not? |
| [`ADR-B`](ADR-B-credential-scope-vs-merge-capability.md) | Can the credential scope the Security implications section states perform both the merge write and the remediation push #2006 elsewhere asks for? |
| [`ADR-C`](ADR-C-external-harness-provenance-authentication.md) | How should an externally-supplied harness's provenance claim be authenticated, given the no-source-change rule for non-built-in harnesses? |

Each draft states the question, why the extract cannot settle it, the requirement rows it affects, and the
options — without recommending one.

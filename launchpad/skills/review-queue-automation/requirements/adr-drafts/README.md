# ADR drafts

These are the decision-record drafts the first derivation of
[`requirements-specification.md`](../requirements-specification.md) wrote when it found three questions
[#2006](https://github.com/launchpad-26/buzz/issues/2006)'s text could not settle on its own: a genuine textual
contradiction (`ADR-A`), a question resting on a premise external to the source text (`ADR-B`), and a design
choice the source left open (`ADR-C`).

**All three were resolved at the source, not by an ADR issue.** On 2026-09-04 the maintainer amended #2006 —
drafted by an agent from the maintainer's dictated resolutions and applied on the maintainer's instruction — and
that amendment settled all three questions directly in the PRD text. **No ADR issue was ever filed for any of
them, and none now will be.** The three files below are kept as the historical record of what was once open and
why; no row in the current requirements specification carries an ADR pointer.

| Draft | Question it asked | How #2006's 2026-09-04 amendment resolved it |
|---|---|---|
| [`ADR-A`](ADR-A-ac09-remediation-code-modification-contradiction.md) | Does resolving a mechanical, policy-permitted finding require RQA to directly modify and push code, or not? | AC09 now states RQA may apply and push a fix directly where the finding is mechanical — deterministic and non-behavioural; a finding whose remedy would change behaviour is never mechanical and always requires human attention. |
| [`ADR-B`](ADR-B-credential-scope-vs-merge-capability.md) | Can the credential scope the Security implications section states perform both the merge write and the remediation push #2006 elsewhere asks for? | Security bullet 6 now states the credential scope directly grows with configured authority: a repository additionally configured for remediation push or merge-after-review carries the additional write scope those operations require, and no more; an advisory-only repository carries no write scope beyond pull-requests. The scope is no longer a fixed enumeration asserted to somehow suffice — it is stated to expand exactly as configured authority requires. |
| [`ADR-C`](ADR-C-external-harness-provenance-authentication.md) | How should an externally-supplied harness's provenance claim be authenticated, given the no-source-change rule for non-built-in harnesses? | Security bullet 4 now states provenance is written by RQA itself, never by reviewed content or model output — a harness's self-reported identity is input RQA acts on, not an authoritative write of its own. The bullet also now states the tamper-evidence guarantee holds within the operator's trust boundary and does not defend against a compromised operator machine. |

Each draft's body is left as originally written — the question, why the extract could not settle it, the
requirement rows it affected, and the options considered, without a recommendation — because that is the
historical record of what was open before the amendment, not a live document. See
[revision-history.md](../revision-history.md)'s round 9 for the full account of the amendment and its effect on
the requirements specification.

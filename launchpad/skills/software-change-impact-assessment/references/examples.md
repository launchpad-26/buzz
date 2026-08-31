# Representative Examples

These are calibration examples, not claims about any repository.

## Documentation-only

Evidence: only `docs/` files changed; no executable/configuration manifests changed. Assessment: `LOW`, concise, with documentation review. Do not claim technical impact from file count.

## Dependency upgrade

Evidence: lockfile and manifest show `library 1.4 → 1.5`; package-manager resolution is `UNAVAILABLE`. Interpretation: runtime/build compatibility and transitive supply-chain impact are possible. Assessment: `MEDIUM` or `UNKNOWN` dependency details; do not invent a CVE or claim clean resolution.

## CI trust boundary

Evidence: workflow adds `pull_request_target`, broad token permissions, and executes checkout content. Finding `CIA-SEC-001`, `CONFIRMED`; impact is elevated execution context for untrusted input. Assessment is at least `HIGH` pending focused security review, regardless of diff size.

## Textual conflict

Evidence: merge/rebase reports overlapping hunks in `src/session.rs`. Report textual conflict `CONFIRMED`. Do not call it semantic conflict unless behaviour analysis supports that separate conclusion.

## Semantic conflict

Evidence: upstream changes session close/reconnect sequencing; downstream modifies a consumer that relies on the old lifecycle but not the same lines; merge is clean. Report semantic conflict `POTENTIAL`, cite both revisions and consumer, and state runtime incompatibility is unproven.

## Policy conflict

Evidence: downstream ADR requires the relay to remain internal; incoming configuration exposes it publicly. Report policy conflict separately, cite ADR and config, and make the recommendation advisory.

## Missing evidence

Evidence: source SHA is known but scanner output and runtime tests are unavailable. State security/test evidence `UNAVAILABLE` and relevant impacts `UNKNOWN`; never write “no security impact” or “tests pass.”

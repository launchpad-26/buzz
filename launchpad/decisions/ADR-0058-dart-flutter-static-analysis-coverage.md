---
status: Accepted
date: 2026-09-10
issue: launchpad-26/buzz#2149
decided_in: launchpad-26/buzz#2149
supersedes: none
---

# ADR-0058 — Dart/Flutter static analysis runs via `dart analyze` + Semgrep, not CodeQL

## Decision

Dart/Flutter static analysis ships as a **separate CI job**, not as a language leg in
`launchpad-codeql.yml`, running two tools with different footing:

1. `dart analyze` (or `flutter analyze`) with `flutter_lints`/`package:lints` and strict-mode
   options (`strict-casts`, `strict-inference`, `strict-raw-types`) ships **unconditionally** —
   a correctness/style floor, independent of how the Semgrep piece turns out.
2. `semgrep --config=p/dart` ships **as a validation spike, not a settled coverage claim**. The
   first iteration validates which Dart security rules actually execute successfully against
   this codebase, records the vulnerability classes genuinely covered versus known gaps, and
   notes false-positive/false-negative limitations found in practice — rather than asserting
   "Dart is covered" on the strength of Semgrep merely being able to parse Dart. Coverage stays
   labelled partial/experimental until that validation is done.

The job runs **advisory, not required**, matching `launchpad-codeql.yml`'s own precedent: a first
run against a codebase this size will surface an untriaged backlog, and a check that starts out
red teaches everyone to ignore it.

This rejects wiring the community CodeQL extractor (`AFASResearch/codeql-dart`) into the existing
workflow, and rejects deferring the gap indefinitely. It does not claim parity with CodeQL's
`security-extended` suite — Semgrep's Dart support is documented as an experimental tier, with a
thinner ruleset and weaker dataflow/taint guarantees than the GA languages this repo's CodeQL
workflow already covers. That gap between "covered" and "covered as well as everything else"
stays real, and per the amendment above is treated as an open question to validate, not a claim
to make on day one.

## Context

`launchpad-codeql.yml` (#2135, PR #2136) runs CodeQL across every language GitHub's own
`code-scanning/default-setup` endpoint reports as supported for this repo — rust,
javascript-typescript, python, swift, actions — and explicitly names Dart as a gap it leaves
uncovered. Dart is roughly 5.4M characters of this repo (`dart: 5455158` via
`gh api repos/launchpad-26/buzz/languages`), presumably the Flutter mobile app, and by the same
logic the workflow already applies to Kotlin/Swift ("often just the shell"), the
security-relevant logic likely lives in this uncovered code. Every other first-class language in
the repo gets dataflow-level SAST; Dart gets none.

Investigation for this decision (#2149) found:

- CodeQL has no official Dart support and no roadmap signal — dart-lang/sdk#52953,
  flutter/flutter#130703, and github community discussion #175533 are multi-year-old asks with
  no commitment from either side.
- The only third-party CodeQL Dart extractor, `AFASResearch/codeql-dart`, is a 16-commit
  prototype: 0 stars, 0 forks, no releases, no documented users, no production-readiness claims.
- Writing a first-party CodeQL extractor is a multi-month compiler-frontend project, out of
  proportion to this gap.
- Semgrep supports Dart via a generated tree-sitter parser (`semgrep/semgrep-dart`) but marks it
  "Experimental" tier in its own docs.
- `dart analyze`/`flutter analyze` is free and official but is a correctness/style linter, not a
  security scanner — it does not catch injection, path traversal, or unsafe-deserialization
  classes of bugs on its own.
- Commercial SAST tools with real Dart/Flutter maturity exist (Veracode, Black Duck) but require
  procurement and budget — a different kind of decision than a CI workflow change.

## Consequences

**Good.** Closes a real, currently-zero-coverage security-pattern gap for the largest
single-language body of code in the repo after Rust/TS, using free, actively-maintained tooling,
without taking on an unmaintained CodeQL extractor's risk. Follows the same advisory-first
posture `launchpad-codeql.yml` already established, so a first noisy run doesn't become a
precedent for ignoring the check.

**Bad.** Semgrep's Dart tier is explicitly experimental: expect false positives and false
negatives, and a materially thinner ruleset than CodeQL's `security-extended` suite gives the
other languages. This is real security-pattern coverage, not CodeQL parity, and the follow-up
implementation should say so rather than presenting the new job as closing the gap outright.

**Follow-up.** launchpad-26/buzz#2165 tracks adding the actual workflow file
(`.github/workflows/launchpad-dart-analysis.yml`) and running the Semgrep validation spike; this
ADR settles which tools to standardize on and the terms of adoption, not the workflow YAML or
the spike's findings themselves.

## Provenance

Decided in launchpad-26/buzz#2149, drafted by an agent per that issue's ADR template
(options A–D). @tucktuck101 proposed the validation-spike amendment in
[this comment](https://github.com/launchpad-26/buzz/issues/2149#issuecomment-5610337555)
(unconditional `dart analyze`, Semgrep treated as unvalidated until proven, explicit
partial/experimental labelling). Decision recorded by @benmitchell11, quoted verbatim from
[this comment](https://github.com/launchpad-26/buzz/issues/2149#issuecomment-5610474756):
"Confirmed, going with option C with the amendments suggested by Jeff." Follows from and extends
the gap named in launchpad-26/buzz#2135 / PR #2136.

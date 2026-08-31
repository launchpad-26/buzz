# Issue #934 — implementation/crates/buzz-push-gateway.md

Stated size: issue #934 carries no Size label or line -> cap: 5 steps.

ALREADY TRUE: `launchpad/docs/corpus/templates/implementation-reference.md`,
`launchpad/docs/corpus/architecture/containers/push-gateway.md`, and
`launchpad/docs/corpus/architecture/flows/push-notification.md` are merged on
`origin/launchpad`, at commit `76a0a4ebbe4bc4d852b0d04362ed768620da34b3`.
`launchpad/docs/corpus/implementation/crates/buzz-push-gateway.md` does not exist yet.
`crates/buzz-push-gateway` exists with `src/{lib,main,apns,app_attest,authority,config,
grant,http,metrics,model,postgres,strict_json,token}.rs`, 4 migrations, and inline
`#[cfg(test)]` suites (no separate `tests/*.rs` integration file). Evidence has
already been gathered this session by direct `Read`/`grep` against this worktree
(full reads of `apns.rs`, `config.rs`, `authority.rs`, `model.rs`, `grant.rs`,
`token.rs`, `app_attest.rs`, `metrics.rs`; targeted reads of `http.rs`'s `AppState`,
router table, and `challenge`/`enroll`/`deliver` handlers, and of `main.rs`; `wc -l`
for file sizes; `grep` for test counts and CI/Justfile wiring
(`cargo nextest run -p buzz-push-gateway`, Justfile:346); and cross-checking
`docs/nips/NIP-PL.md`'s "Public APNs Gateway Profile (Buzz, normative)" section
against the code). RepoQL's structural index for this crate is confirmed **stale**
against this worktree (it reports a JWT-based `ApnsTransport` with a
`RefreshCredential` outcome and a `profile` parameter on `PushTransport::send`;
direct file reads show a client-certificate-based `ApnsTransport`, no
`RefreshCredential` variant, and no `profile` parameter) — every citation in this
node's evidence ledger is grounded in direct reads, not RepoQL. One real,
verified divergence was found: `docs/nips/NIP-PL.md:420` normatively requires "an
APNs expired-provider-token response permits one credential refresh and one retry,"
but `apns.rs`'s current `ApnsTransport` carries no credential/JWT concept and
`DeliveryOutcome` has no refresh-and-retry variant.

STEP 1  [independent] Write the front matter (id
`implementation-crates-buzz-push-gateway`, type `implementation`, status `draft`,
origin `launchpad`, audiences `[agent, developer, reviewer]`, one commit-provenance
`FACT` plus one `FACT`/`INFERENCE` entry per substantive body claim, citing only
sources actually opened this session) and the body using the
`implementation-reference` template's exact required sections (Realization
statement, Target, Implementation surface, Divergences, Verification,
Relationships, Scope and omissions). Target: `docs/nips/NIP-PL.md`'s "Public APNs
Gateway Profile" section (no corpus node id yet — name it by path, declare no
`implements` edge). Report the credential-refresh divergence from ALREADY TRUE in
the Divergences section, citing both `docs/nips/NIP-PL.md:420` and `apns.rs`. Go
one layer deeper than the merged `architecture-containers-push-gateway` and
`architecture-flows-push-notification` nodes (concrete modules/functions/tests);
do not restate their canonical container/flow claims, and do not copy their
now-stale claims (JWT auth, `BUZZ_PUSH_ENABLED_PROFILES`, two app profiles) as if
current. ← RUNS HERE
done when: `launchpad/docs/corpus/implementation/crates/buzz-push-gateway.md`
exists, contains every template-required section, and every DoD bullet from issue
#934 is satisfied by some part of the body or front matter.

STEP 2  [needs 1] Run `python3 launchpad/project-intelligence/corpus/validate.py`
from the repo root; fix and re-run until exit 0. If nonzero, diff against the
pre-existing ~21-failure baseline on `origin/launchpad` (via `git stash`) before
assuming this node broke something.
done when: the validator exits 0 and prints no FAIL line naming this node.

STEP 3  [needs 2] Run `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in
its own tool call to earn the verification stamp; confirm `OK`. Then, in a separate
tool call, `git add` the plan + node and `git commit -s`.
done when: the unittest run prints `OK` and `git log -1` shows the new commit with
both files staged.

STEP 4  [needs 3] Re-read the committed diff against issue #934's Definition of
Done line by line; confirm every citation was actually opened. Run `corpus-review`
if reachable in-session; otherwise do a careful self-review and say so in the final
report. Do not push, do not open a PR (integration happens later in a separate
Feature-level pass).
done when: each DoD bullet is explicitly checked off against the committed diff, and
the report states whether `corpus-review` ran or a self-review substituted for it.

PARALLEL: none — single file, single task, no dependency on sibling batch documents.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 for
this node (pre-existing unrelated failures on `origin/launchpad` are not this task's
to fix). `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` must report `OK` before commit.

BUDGET: small — one document, no runtime code changes, evidence gathering scoped to
one crate's 13 source files plus one NIP spec file already read in full.

OPEN: Whether the credential-refresh divergence found while gathering evidence is a
known, accepted simplification (cert-based APNs auth doesn't need JWT refresh, so
the NIP-PL clause may itself be stale against an earlier JWT-based design this crate
has since moved away from) or an unnoticed spec/code drift is not resolved here —
the Divergences section reports it as an observed fact citing both sides, without
adjudicating which side is "correct." Filing a follow-up issue about it is not this
task's job per the issue's own out-of-scope list ("broad while-here cleanup").

LEFT OUT: No `implements` edge (NIP-PL.md has no corpus node id yet). No
relationship to `architecture-containers-push-gateway` or
`architecture-flows-push-notification` unless a genuine `references`/`part-of` fit
is confirmed while writing — both are architecture-surface nodes about a different
concern (container boundary, end-to-end flow) than this node's job (implementation-
to-spec traceability), so a fit is not assumed. No attempt to correct the two
architecture nodes' now-stale claims (JWT/provider-token APNs auth,
`BUZZ_PUSH_ENABLED_PROFILES`, `BUZZ_PUSH_APNS_KEY_ID`/`TEAM_ID`, two app profiles,
7-series metrics) — that is separate work belonging to whoever owns those nodes,
not this task.

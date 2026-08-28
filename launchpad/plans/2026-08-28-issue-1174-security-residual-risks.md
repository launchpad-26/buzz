# Issue #1174 — layers/security/residual-risks.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
are merged on `origin/launchpad`. `launchpad/docs/corpus/layers/` has no `security/` subdirectory
at all yet (`layers/security/provider-boundary.md` and `layers/identity/identity-archive.md` are
only open, unmerged PRs — #1822 and #1812 — not present on `origin/launchpad`), so no `layers-*`
id exists to relate to. No template named `residual-risks` or equivalent exists in
`launchpad/docs/corpus/templates/`; `threat-model.md` is the closest sibling but is explicitly
scoped to the full attacker-perspective catalogue (STRIDE table, DFD, mitigations) that issue
#1180 owns separately — this node is deliberately narrower: only the risks that remain *after*
mitigation, not a threat catalogue. Two already-merged architecture-principle nodes exist to cite
as supporting context: `architecture-principles-community-is-security-boundary` and
`architecture-principles-fail-closed-boundaries`. Sibling tasks #1107 (identity-archive) and
#1171 (provider-boundary) each independently found and verified concrete security-relevant gaps
in this same revision (338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5) that this node re-verifies
directly rather than trusting: `crates/buzz-test-client/tests/conformance_multitenant.rs`'s
`archive_in_a_does_not_affect_b` is a `#[ignore]`d `todo!()` stub, and `docs/remote-agents.md`'s
own Non-Goals section states the provider-boundary protocol "cannot make a hostile provider safe."

STEP 1 [done] Gather and re-verify evidence directly (not trusting #1107/#1171's prose): read
`crates/buzz-test-client/tests/conformance_multitenant.rs` in full for its module doc, the
`archive_in_a_does_not_affect_b` stub, and the `unmapped_host_fails_closed_generically` test;
count `#[ignore]`/`pending_lane` occurrences; grep every CI workflow and the `Justfile` for
`conformance_multitenant` (none found — the suite never runs, implemented or not). Read
`docs/remote-agents.md`'s System Model, Non-Goals, Discovery, and "Known Defects (at 28ae6cd21)"
sections. Re-verify two "Known Defects" entries against current code rather than reusing them
as-is: defect 5 (protocol-version check) is fixed (`backend.rs`'s `provider_deploy` now stages,
hashes, calls `info`, checks `protocol_version` before `deploy`) and defect 3's "Security
follow-through" note is fixed (`env_secrets_from_request` in `backend.rs` now reads
`agent.env_vars`, `launch.env`, and `launch.policy_env`) — both are stale on the doc's own page
at this revision, so neither is cited as an open risk. Confirm no end-to-end test exercises a
real `buzz-backend-*` binary (`backend_tests.rs` uses only a stub shell-script provider; no
`crates/buzz-test-client/tests/` or `desktop/tests/e2e/` file references `buzz-backend`).

STEP 2 [needs 1] Write front matter: `id: layers-security-residual-risks`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, operator, reviewer]`, a
commit-citation FACT for the revision, one FACT per re-verified claim above (citing the actual
files opened), and TEAM_KNOWLEDGE entries for the issue's own DoD and #607/#1180's scope split.
`relationships: [{type: references, target: architecture-principles-community-is-security-boundary}]`
— `references` because this node cites that principle as supporting context for what the
isolation guarantee is designed to be, without depending on its currency for this node's own
(narrower) claims about test coverage.

STEP 3 [needs 2] Write the body against `node.schema.json` directly (no template exists): scope
statement distinguishing this node from #1180's full threat catalogue; a residual-risks table
(risk, evidence, why it is residual/accepted rather than mitigated); the three grounded risks —
(a) the multi-tenant A/B isolation conformance suite never runs in any CI workflow and roughly
half its obligations, including cross-community archived-identity isolation, are unimplemented
`todo!()` stubs; (b) the provider-boundary protections in `docs/remote-agents.md` are verified
only at the unit level against a stub provider, with no end-to-end test against a real
`buzz-backend-*` binary; (c) the explicitly accepted risk that a deployed provider is trusted
with the agent's live key by design ("cannot make a hostile provider safe") — plus a boundary
section and the mandatory scope-and-omissions section (owner table + what was expected but not
verified).

STEP 4 [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root; fix anything it names; re-run until exit 0.

STEP 5 [needs 4] Run the corpus unittest suite as the sole command in its own call
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`),
confirm `OK`, then commit with `git commit -s`, push, and open the PR as a draft per the task's
own template — no `review-code` skill invocation; verification is self-review only.

GATES: `validate.py` exits 0 (STEP 4). Corpus unittest suite prints `OK` (STEP 5). Every FACT's
source was opened directly in this session, not copied from #1107/#1171/#1188's prose.

OPEN: Whether `layers-security-provider-boundary` and `layers-identity-identity-archive` merge
before this PR — if they do first, a later edit could add `references` edges to them, but this
node does not wait on that (per `AGENTS.md`, relationships resolve against the merge-target
branch, not this worktree).

LEFT OUT: The five other "Known Defects" entries in `docs/remote-agents.md` (Windows discovery
suffix, provider env inheritance, the I5 reaper, the clean-exit contract, the shutdown-tail
budget, cleared numeric config fields) were spot-checked only where cited above (defects 1 and 4
both also appear fixed at this revision) and are not re-litigated here — this node cites only the
risks it re-verified as still open, not a transcription of that document's defect list. The full
STRIDE threat catalogue for these same subsystems is #1180's node, not this one.

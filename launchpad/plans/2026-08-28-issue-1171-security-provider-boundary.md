# Issue #1171: corpus doc — layers/security/provider-boundary.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
and the `invariant.md` template (`corpus-template-invariant`) are merged on
`origin/launchpad`. `launchpad/docs/corpus/layers/security/provider-boundary.md` does not
exist yet, and no `layers/` directory exists in the corpus tree at all — this is the
first `type: layers` node. `docs/remote-agents.md` is a merged, in-repo formal spec
naming exactly one boundary that fits this task's title: the trust boundary between
Buzz Desktop and a `buzz-backend-<id>` **provider** binary, across which the agent's
private key crosses "by design" (the doc's own words). `crates/buzz-backend-kubernetes`
is the one conforming provider implementation. Investigated and ruled out: ADR-0012
("inference provider boundary") is the *launchpad cohort's own tooling* credential
policy for its GitHub Actions synthesis workflow, not a Buzz product security
boundary — wrong "provider" for this task.

STEP 1 (RUNS HERE): Gather evidence — already done in this session. Read
`docs/remote-agents.md` in full (Abstract, System Model, Invariants, Provider Protocol
§Discovery/§Invocation/§Provider Output Is Untrusted/§info/§deploy, §Conformance L2,
§Known Defects); read the implementing code: `desktop/src-tauri/src/managed_agents/
backend.rs` (stage_provider digest+read-only staging, validate_provider_info protocol
gate, validate_provider_config I2 secret-name lint, redact_secrets_with, discovery/
resolve_provider_binary id validation), `reserved_env_keys.rs` (RESERVED_ENV_KEYS),
`commands/agents_deploy.rs` (build_deploy_payload calling spawn_key_refusal,
deploy_payload_json), `managed_agents/storage.rs` (spawn_key_refusal), and
`crates/buzz-backend-kubernetes/src/env.rs` (build_env's top-level-fields-only
identity, AUTHORITATIVE_KEYS clear-then-write). Confirmed test-enforced tier via
`backend_tests.rs` (`provider_deploy_refuses_mismatch_before_sending_agent_secret`,
the two staged-bytes-integrity tests, `validate_provider_config_rejects_*`) and
`buzz-backend-kubernetes/src/env.rs`'s `lower_tiers_cannot_spoof_authoritative_values`.
Noted: `docs/remote-agents.md`'s own "Known Defect 5" (pre-secret negotiation gate
"does not exist" at commit `28ae6cd21`) is stale against current code — the gate
ships and is test-enforced today (commit `6530b58a6`, after `28ae6cd21`, both landed
`stage_provider`/`provider_deploy`'s current shape and is the same commit that last
touched the doc without updating that defect entry). This is a current-behavior
question the corpus's own code-outranks-docs precedence rule resolves, not a same-type
conflict requiring `status: flagged`.

STEP 2: Write front matter (`id: layers-security-provider-boundary`, `type: layers`,
`status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
evidence ledger with FACT entries citing the files above — each opened and read this
session — and one `relationships: [{type: implements, target:
corpus-template-invariant}]` edge, since that template node is confirmed present on
`origin/launchpad`) and the body, following `invariant.md`'s required sections
(Invariant statement / Scope / Enforcement today, naming the weakest true tier honestly
— test-enforced, with the specific tests / Consequence of violation / Boundary / no
`references` back to a topical neighbor — no sibling `layers/` node exists yet, matching
`AGENTS.md`'s precedent for "none is a legitimate answer while the corpus is being built
out" / Scope and omissions, naming the K8s-specific deploy-state-machine/GC mechanics,
the `launch` block resolution details, and the still-open Known Defects (2, 3, 8) as
explicitly out of scope for this atomic node).

STEP 3: Run `python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root; fix and re-run until it exits 0.

STEP 4: Earn the commit-gate stamp with
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as its own command, confirm `OK`, then commit the plan and the new node together with
`git commit -s`.

PARALLEL: none — one file, one commit.

GATES: `validate.py` must exit 0. `review-adjudicate` and the cross-model review pass
are explicitly deferred to the batch owner's review before merge — not run in this
session, and the PR is opened as a draft saying so.

BUDGET: single session; no iteration expected beyond validator fix-up.

OPEN: `docs/remote-agents.md` covers five invariants (I1–I5) across ~1800 lines; this
node covers only the piece that is genuinely "the provider boundary" per the atomicity
standard's single-sentence test — what crosses the desktop↔provider process boundary
and what bounds the desktop's exposure to an untrusted provider binary (I1's
payload-construction half, I2 in full, the pre-secret negotiation gate, output
redaction, and the reserved-key rule's provider-side realization). I3 (presence
staleness), I4 (at-most-one-live-instance), and I5 (intentional-termination-is-final)
are lifecycle/uniqueness properties of the *deployed agent*, not properties of the
boundary itself, and are left for their own future nodes (sibling issues already exist
for `trust-boundaries.md`, `relay-boundary.md`, `secret-management.md`,
`ssrf-protection.md` etc. in this same batch, #1168-#1192) rather than folded in here.

LEFT OUT: The Kubernetes binding's own deploy-state-machine/GC mechanics (§Deploy State
Machine, §K8s Secrets, §K8s GC) are a distinct, already-flagged concept in a prior
sibling plan (`launchpad/plans/2026-08-27-issue-670-corpus-doc.md`'s LEFT OUT: "a
compute provider for agents, not the relay's own deployment topology" — its own future
node). This task documents the *protocol boundary* the Kubernetes binding is one
conforming instance of, and cites the K8s-side reserved-key realization only as
corroborating evidence, not as its own subject.

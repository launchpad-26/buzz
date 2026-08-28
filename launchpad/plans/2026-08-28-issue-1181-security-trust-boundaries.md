# Issue #1181 — layers/security/trust-boundaries.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md` are
merged on `origin/launchpad`; `launchpad/docs/corpus/layers/security/` does not exist yet (confirmed:
`ls launchpad/docs/corpus/layers/security/` -> no such directory). None of the five sibling boundary
docs this node indexes (#1168 admin-boundary, #1169 cryptographic-boundary, #1171 provider-boundary,
#1172 relay-boundary, #1179 tenancy-boundary) or #1182 trust-model / #1180 threat-model exist on disk
in this worktree — all six issues are still OPEN. Three real, already-merged corpus nodes sit adjacent
to this subject: `architecture-principles-community-is-security-boundary`,
`architecture-principles-fail-closed-boundaries`, `architecture-principles-subsystem-isolation`.

STEP 1  Gather primary-source evidence for each trust boundary this index enumerates, grounded in code
and the repo's own formal-spec docs rather than invented: tenancy/community boundary
(`docs/multi-tenant-relay.md`, `crates/buzz-relay/src/tenant.rs`, the merged `community-is-security-boundary`
node), the relay's external network door (`crates/buzz-relay/src/router.rs`,
`crates/buzz-relay/src/handlers/auth.rs`), the cryptographic verification boundary
(`crates/buzz-core/src/verification.rs`, its call sites in `ingest.rs`/`event.rs`), the admin ingress
boundary (`docs/admin/README.md`), and the provider/substrate boundary for remote agents
(`docs/remote-agents.md`). Also note the agent-harness/operator trust boundary described in
`crates/buzz-agent/README.md`'s Security Model as a trust-relevant boundary not currently assigned to
any of the five named child docs. ← RUNS HERE

STEP 2  [needs 1] Write front matter (id `layers-security-trust-boundaries`, type `layers`, status
`draft`, origin `launchpad`, audiences `[agent, developer, operator, reviewer]`, `relationships: references`
targeting the three already-merged `architecture-principles-*` nodes above — no target from the five
sibling boundary docs, since none exists on disk) and the body: purpose/scope naming this as the
index/map distinct from #1180's threat-model and #1182's trust-model, assumptions and protected assets,
a Mermaid data-flow view locating each boundary, an enumeration table (boundary name, expected corpus
id, one-line description, primary source, disk status), a lightweight per-boundary threat-category
summary (STRIDE-labelled, deferring deep analysis to #1180), a mitigations/verification table citing
real enforcement code and the existing conformance mechanisms (`conformance_multitenant.rs`,
`docs/spec/MultiTenantRelay.tla`), and a residual-risks/open-issues section that states proposed-but-
unbuilt items as such (the five child docs, #1180, #1182) rather than as implemented controls.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run until
exit 0.

STEP 4  [needs 3] Run the corpus unittest suite as the sole prior command to earn the verification
stamp, then commit the plan + document in a separate call, push, and open a draft PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. `review-adjudicate` and
the cross-model final review pass are deferred to the batch owner's review — not run here.

BUDGET: small-to-medium — one document, no code changes; evidence gathering spans roughly six source
files/docs and three already-merged corpus nodes, no live systems stood up.

OPEN: The DoD's "typed relationships appropriate to the node" is satisfiable now (unlike several sibling
tasks) because three genuinely on-topic `architecture` nodes are already merged; whether `references`
(supporting context, no ownership/currency dependency) rather than `depends-on` is the right type for
all three is a judgment call — `depends-on` was rejected because this index's own claims do not require
those nodes to stay current for its claims to hold, it merely cites them as evidence. None of the five
sibling boundary docs, the trust-model doc, or the threat-model doc can be linked — they do not exist on
`origin/launchpad` and adding a `relationships` target naming an unmerged id is a hard validation error;
this is stated in prose (expected ids) instead, per the task brief's explicit instruction.

LEFT OUT: No deep STRIDE-style threat enumeration per boundary (owned by #1180's threat-model.md, which
has its own template and template-instance relationship). No WHO/WHAT-is-trusted-at-each-level content
(owned by #1182's trust-model.md). No new corpus nodes for the five child boundary docs — creating those
is explicitly out of scope for this task and would violate "exactly one hand-authored canonical document
per task." No attempt to resolve which of the observed additional trust-relevant boundaries (agent-harness
operator boundary, git-on-object-storage's S3-axiom boundary) get their own future corpus task — noted as
an open gap in Scope and omissions instead of silently folded into an existing boundary's scope.

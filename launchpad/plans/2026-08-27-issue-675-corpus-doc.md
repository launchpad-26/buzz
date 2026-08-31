# Issue #675 -- corpus doc: architecture-flows-agent-turn

ALREADY TRUE: node.schema.json is merged and authoritative, corpus/AGENTS.md says write against
the schema with no per-type template yet, and `launchpad/docs/corpus/architecture/flows/agent-turn.md`
does not exist on `origin/launchpad`.

STEP 1 -- Gather evidence: read `crates/buzz-acp/src/{acp,pool,queue,observer}.rs`,
`crates/buzz-acp/README.md`, and representative tests for the ACP prompt-turn lifecycle
(trigger, session resolution, context fetch, `session/prompt`, `StopReason`, cancel/timeout/
dead-letter paths, NIP-AM turn metric, inbound author gate). RUNS HERE.

STEP 2 -- Write front matter (id, type: architecture, status: draft, origin: launchpad,
audiences, evidence ledger with commit-pinned provenance) and a body satisfying issue #675's
DoD checklist plus the flows category tail (trigger/preconditions/termination, ordered
interactions, trust-boundary crossings, failure/abort/rollback + verification links).

STEP 3 -- Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and re-run
until it exits 0.

STEP 4 -- Run the corpus unittest suite as the sole command to earn the verification stamp,
then commit the plan + the new document and open a draft PR.

PARALLEL: none -- single file, single agent.

GATES: `validate.py` must exit 0. `review-adjudicate` and the cross-model review pass are
deferred to the batch owner's morning review; they do not run in this task.

BUDGET: small -- one document, no code changes, target under ~250 lines of Markdown.

OPEN: the issue's DoD asks for "typed relationships appropriate to the node," but no merged
corpus node (`corpus-readme`, `corpus-agents`, `corpus-standard-confidence`,
`corpus-standard-decision-references`) describes anything this flow depends on, implements, or
references, so `relationships` is omitted per the REPO FACTS guidance (never invent a target
id). This is a real gap the issue leaves unresolved, not a decision made here.

LEFT OUT: no second canonical document; no runtime/product code changes; no per-type template
invention; no resolution of corpus decisions (#1321 provenance-update policy, #1307-#1351
per-type standards) left open elsewhere.

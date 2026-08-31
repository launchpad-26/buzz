# Issue #706 — capabilities/agents/agent-mention.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`
and `launchpad/docs/corpus/templates/capability.md` are merged on `origin/launchpad`;
`launchpad/docs/corpus/capabilities/agents/agent-mention.md` does not exist yet. No
`capabilities/` node has ever been merged — this is the first. Three merged `architecture`
nodes already document adjacent territory: `architecture-flows-agent-turn` (the harness's
event loop), `architecture-containers-agent-runtime` (the buzz-acp/buzz-agent/buzz-dev-mcp
crates), `architecture-context-ai-agent` (agents as first-class Nostr identities).

STEP 1  Gather evidence for the mechanism end to end, confirmed by direct read: outbound
`p`-tag construction (`crates/buzz-sdk/src/builders.rs:193-205` `mention_tags`, called from
`build_message` at line 237); the harness's own documented flow
(`crates/buzz-acp/README.md:251-262` "How It Works", `:132-162` Inbound Author Gate,
`:223-249` Forum Channels showing `require_mention` is the default and can be disabled);
the actual match logic (`crates/buzz-acp/src/filter.rs:368-399` `match_event`, the `p` tag
check at `:390-398`); the default wiring of that flag from config
(`crates/buzz-acp/src/config.rs:1304`, `:1409` `require_mention = !config.no_mention_filter`);
the dispatch call site (`crates/buzz-acp/src/lib.rs:2898-2927`); the event kind
(`crates/buzz-core/src/kind.rs:479` `KIND_STREAM_MESSAGE = 9`); and the agent-facing
mentioning conventions (`crates/buzz-acp/src/base_prompt.md:56-68` Mentions/Callback
Mentions). Separately note the desktop `agent-address` `mention` tag
(`desktop/src/features/messages/lib/agentAddressMention.mjs:1-9`) is UI display metadata,
not the wake mechanism — its own comment says the `p` tag remains the notification path.
← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `capabilities-agents-agent-mention`,
type `capabilities`, status `draft`, origin `launchpad`, audiences
`[agent, developer, reviewer]`, `references` relationships to the two merged architecture
nodes that realize this capability — `architecture-flows-agent-turn` and
`architecture-containers-agent-runtime` — both confirmed present on `origin/launchpad`)
and the body per the capability template's required sections: Capability statement,
Maturity (shipped, cited to the code above), Boundary (not the event-loop mechanics, not
the harness container, not the step-by-step turn sequence — those are the two referenced
architecture nodes' territory), behavioral rules/variants (default `require_mention` gate,
`--no-mention-filter`/forum-channel opt-out, owner-only author gate ordering, `!shutdown`/
`!cancel`/`!rotate` control-message convention riding the same mechanism), Relationships,
Scope and omissions.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0, confirming zero new FAIL entries beyond the known 21 pre-existing
ones (#1951).

STEP 4  [needs 3] Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
as the sole command in its own call to earn the commit-gate stamp; confirm `OK`.

STEP 5  [needs 4] `git add` the new document and this plan file, commit with
`git commit -s`. Stop there — no push, no PR (integration lands via the Feature-wide PR).

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0 with no new
FAIL entries. The corpus unittest suite must print `OK` before the commit is made.
`review-adjudicate` and the cross-model final review pass are deferred to the batch owner's
integration review — not run here.

BUDGET: small — one document, no code changes, evidence gathering scoped to the six files/
line ranges named in STEP 1.

OPEN: whether `capabilities-agents-agent-mention` should also `references` a future
interface node for `buzz-cli`'s `messages send --mention` surface — no `interfaces-events`
node is merged yet, so this is left for the interface template's own author to link back,
per `AGENTS.md`'s rule that relationships resolve against the merge-target branch, not the
author's worktree.

LEFT OUT: no relationship to `architecture-context-ai-agent` — it establishes agents as
peer Nostr identities generally, not the mention-wake mechanism specifically, and citing it
would be a weaker/looser edge than the two `references` above. No claim about mobile or
Blossom-media mention handling — out of scope; this capability is scoped to the desktop/
CLI → relay → buzz-acp harness path actually traced. No attempt to reconcile or fix the
pre-existing 21 validate.py FAIL entries (#1951) — not this task's scope.

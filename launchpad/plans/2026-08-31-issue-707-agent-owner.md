# Plan: issue #707 — corpus node `capabilities-agents-agent-owner`

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`,
`launchpad/docs/corpus/AGENTS.md`, `launchpad/docs/corpus/templates/capability.md`, and
the `architecture/` subtree (including `architecture-context-ai-agent`,
`architecture-containers-cli`, `architecture-flows-git-push`) are merged on
`origin/launchpad`. No `capabilities/` subtree exists yet under
`launchpad/docs/corpus/`, and `launchpad/docs/corpus/capabilities/agents/agent-owner.md`
does not exist. `architecture-context-ai-agent`'s own Scope and omissions table
explicitly names an unfilled gap this node addresses: "Whether/how a human reviews or
approves an agent-originated event before it reaches other users... A gap. If one
exists, it was not located."

STEP 1 — Gather evidence. Read `docs/nips/NIP-OA.md`, `crates/buzz-sdk/src/nip_oa.rs`,
`crates/buzz-db/src/store/user.rs` (`set_agent_owner`, `is_agent_owner`,
`get_agent_channel_policy`), `migrations/0001_initial_schema.sql`
(`agent_owner_pubkey`, `channel_add_policy`), `crates/buzz-relay/src/api/mod.rs`
(`extract_nip_oa_owner`, `materialize_nip_oa_owner`), `crates/buzz-relay/src/handlers/
side_effects.rs` (`owner_only` channel-add policy, message-edit-by-owner), `crates/
buzz-relay/src/api/git/policy.rs` (managed-agent-owner push authority),
`crates/buzz-cli/src/commands/agents.rs` (`draft-create`/`draft-update`, `require_owner`,
`resolve_auth`/`classify_owner_auth_tag`), `crates/buzz-cli/src/agent_management.rs`
(owner-reviewed draft request encoding), `crates/buzz-cli/src/client.rs`
(`auth_tag_owner_hex`), `VISION_PROJECTS.md` (agent reputation / NIP-OA framing), and
`desktop/src-tauri/src/managed_agents/nest_skill.md` (owner-reviewed drafts framing) for
the capability's statement, maturity, and enforcement points. RUNS HERE.

STEP 2 — Write front matter (id `capabilities-agents-agent-owner`, type `capabilities`,
status `draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`, one
evidence entry per substantive claim, classified FACT/INFERENCE/TEAM_KNOWLEDGE honestly)
and the body per `templates/capability.md`'s required sections: capability statement,
maturity (cited to code), boundary (not architecture/interface/flow/operations), scope
and omissions, and `references` relationships to `architecture-context-ai-agent`,
`architecture-containers-cli`, and `architecture-flows-git-push` (all three already
merged on `origin/launchpad`, all three already discuss this capability's supporting
architecture). RUNS HERE.

STEP 3 — Validate: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0, and must add zero new FAIL entries beyond the 21 pre-existing ones tracked in
issue #1951. RUNS HERE.

STEP 4 — Earn the commit gate:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p
"test_*.py"` as the sole command in its own call, confirm `OK`. RUNS HERE.

STEP 5 — Commit locally only (plan + node together). Do not push, do not open a PR — a
later integration phase folds this commit into the Feature #613 PR. RUNS HERE.

PARALLEL: none — single file, single worktree, no fan-out.

GATES: `validate.py` exit 0 with zero new FAIL entries; the unittest discovery command
exits with `OK` as the sole command in its call, before `git add`/`git commit -s` runs
in a separate call. Adjudication and cross-model review are deferred to the batch
owner's integration pass, not run in this session.

BUDGET: one new file (`capabilities/agents/agent-owner.md`), the plan file, one local
commit. No code changes, no generated-index regeneration (none exists to regenerate).

OPEN: whether a capability node should additionally reference a not-yet-existing
`interfaces-events`-type node for the CLI subcommand surface (`buzz agents
draft-create`/`draft-update`) is left to whichever task authors that interface node —
no such node is merged today, so no edge is added per `AGENTS.md`'s own rule. Whether
NIP-PMA's private-managed-agent encryption (`crates/buzz-core/src/private_managed_agent.
rs`) belongs in this node or its own capability node is also open; it is named as an
explicit exclusion in this node's Boundary/Scope sections rather than folded in, per
the "second concept gets its own task" rule.

LEFT OUT: NIP-PMA private managed-agent definition storage/encryption (a distinct
concept — how an agent's config/secrets are stored, not who owns the agent); the
step-by-step flow of a draft-create/draft-update request reaching Buzz Desktop and back
(flow-level, not in this batch, per `templates/capability.md`'s own flow exclusion);
the CLI/interface surface's full command reference (interface-level, no template merged
yet); any change to product code, NIPs, or ADRs — this task documents an existing
capability, it does not modify it.

# Plan: issue #710 — document capabilities/agents/agent-turn.md

## ALREADY TRUE

- `launchpad/docs/corpus/architecture/flows/agent-turn.md` (id
  `architecture-flows-agent-turn`) is merged on `origin/launchpad`
  (confirmed via `git ls-tree -r --name-only origin/launchpad`) and already
  narrates the per-turn lifecycle end to end: trigger, queueing, the
  `run_prompt_task` sequence, termination `StopReason`/`PromptOutcome`
  values, trust boundaries, failure/retry/dead-letter behavior, and cleanup
  guards. This task must not re-narrate that.
- `launchpad/docs/corpus/architecture/containers/agent-runtime.md` (id
  `architecture-containers-agent-runtime`) is also merged and documents how
  the agent runtime (`buzz-acp`, `buzz-agent`, `buzz-dev-mcp`, `sprig`) is
  built as a container — the "how it's built" half a capability node must
  not duplicate either.
- `launchpad/docs/corpus/templates/capability.md` (id
  `corpus-template-capability`) is the template: capability statement,
  maturity (cited), boundary statement (not architecture/interface/flow/
  operations), relationships, scope and omissions.
- `node.schema.json`'s `type` enum has no `capability` singular value — the
  correct value is `capabilities` (plural).
- No `launchpad/docs/corpus/capabilities/` directory exists yet on
  `origin/launchpad` or in this worktree — this is the first capability
  node in the corpus.
- `VISION_PROJECTS.md:251` records "MCP server + ACP agent harness" as
  "✅ Ships today" in the product Status table — the maturity citation.
- `crates/buzz-core/src/kind.rs:545` defines `KIND_AGENT_TURN_METRIC = 44200`,
  the turn-completion telemetry event a turn's capability-level outcome
  produces.

## STEP 1 — Confirm target absence and gather independent evidence

Confirm `launchpad/docs/corpus/capabilities/agents/agent-turn.md` does not
exist (done — no `capabilities/` dir at all). Re-read `buzz-acp/README.md`
top section and `VISION_PROJECTS.md`'s Status table directly (not only via
the flow node's citations) so this node's own evidence ledger is
independently checked, not copied.

Done-when: have primary-source line citations for the capability
statement, maturity, and the two relationship targets.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/agents/agent-turn.md` with://
- `id: capabilities-agents-agent-turn`, `type: capabilities`, `status: draft`,
  `origin: launchpad`, `audiences: [agent, developer, operator]`.
- Evidence ledger: revision commit citation, capability statement facts,
  maturity fact (VISION_PROJECTS.md:251), boundary-supporting facts.
- Body: Capability statement / Maturity / Boundary / Relationships /
  Scope and omissions, per the template skeleton.
- `relationships`: `references` → `architecture-flows-agent-turn` (the
  step-by-step flow) and `references` → `architecture-containers-agent-runtime`
  (how it's built) — both confirmed present on `origin/launchpad`.

Done-when: every DoD bullet in issue #710 is satisfied; no step-by-step
mechanism from the flow node is re-narrated.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Confirm
zero new FAIL entries beyond the known 21 pre-existing ones (issue #1951).

Done-when: exit 0 or only the known baseline failures remain, none touching
the new file.

## STEP 4 — Earn the commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`, then in a separate call `git add` the new node + this plan
file and `git commit -s`.

Done-when: commit created locally; no push, no PR.

## STEP 5 — Self-review

Re-read the diff against issue #710's DoD line by line. Re-open every cited
source. Confirm exactly one hand-authored canonical document was created.

## GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` — zero new
  FAIL entries.
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — must print `OK`, run alone, before commit.

## BUDGET

Single document, capped at 5 steps above. No code changes.

## OPEN

- Whether `architecture-containers-agent-runtime` is the right architecture
  reference or whether a narrower node should exist later — left as a
  `references` edge, not asserted as the only correct one.

## LEFT OUT

- Any second capability, contract, or procedure surfaced while drafting —
  none was found; if one turns up during STEP 2 it becomes a new task, not
  a section here.
- Editing the flow or container nodes this task references.

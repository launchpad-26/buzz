# Issue #796: document capabilities/onboarding/first-channel.md

## ALREADY TRUE

- The `capability` corpus template is merged at `launchpad/docs/corpus/templates/capability.md`
  and prescribes: Capability statement, Maturity, Boundary, Relationships, Scope and omissions.
- `type: capabilities` exists in `node.schema.json`'s enum and is the dedicated PRD #602
  surface for this document.
- `origin/launchpad`'s corpus tree carries no `capabilities/` subtree yet -- no sibling
  onboarding node (#797 first-community, #798 first-identity, #799 onboarding) is merged,
  so no `relationships` target in that family exists yet. `architecture-containers-desktop`
  (a merged architecture node) is a valid `references` target for platform implementation.
- The target file `launchpad/docs/corpus/capabilities/onboarding/first-channel.md` does not
  exist on `origin/launchpad` or in this worktree.
- Desktop's onboarding code (`desktop/src/features/onboarding/`) already implements a
  "first channel" moment distinct from identity setup (#798) and community join/create
  (#797): after the onboarding gate completes, `initializeStarterChannels` (hooks.ts) calls
  `ensureStarterChannels` (deterministic, relay-scoped `#general` + `#welcome-everyone`
  open channels, seeded server-side in `desktop/src-tauri/src/commands/channels.rs`) and
  `ensureWelcomeChannel` (a private per-member "Welcome" channel, `welcome.ts`), then
  focuses the user on the private Welcome channel and seeds an agent-led kickoff message
  (`welcomeKickoff.ts`, `useWelcomeKickoffStage.ts`).
- Mobile (`mobile/lib/`) has no equivalent onboarding directory or starter/welcome-channel
  concept -- confirmed by grep; this is a desktop-only capability today.

## STEP 1 -- Draft the node

Create `launchpad/docs/corpus/capabilities/onboarding/first-channel.md` using the
`capability` template's skeleton. `id: capabilities-onboarding-first-channel`,
`type: capabilities`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, reviewer]`. Cite only paths (no `#symbol=`/`#line=`
fragments, per the batch's known validate.py incompatibility). One `references`
relationship to `architecture-containers-desktop`; no relationship to sibling onboarding
nodes since none are merged on `origin/launchpad` yet -- state that explicitly in Scope.

Body covers: capability statement (landing a new member in their first working channel,
oriented and able to participate), maturity (shipped, cited to the hooks.ts/welcome.ts/
channels.rs code), boundary (not identity setup #798, not community join/create #797, not
the overall onboarding capability #799, not how channels are architected, not an interface
contract, not a step-by-step flow), relationships, scope and omissions (mobile has no
equivalent; the agent-kickoff experience's *content* is a distinct concern only referenced
here, not restated).

**Done when:** file exists, front matter is schema-shaped by inspection, every FACT cites
an opened path.

## STEP 2 -- Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Fix anything it names.

**Done when:** exit 0, and comparing against the known 21 pre-existing FAIL baseline
(issue #1951) shows zero new FAIL entries attributable to this node.

## STEP 3 -- Commit gate and commit

Run, alone, as its own tool call: `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"`. Confirm `OK`. Then `git add`
the new node + this plan file and commit with `-s`.

**Done when:** commit exists on `task/796-first-channel`, nothing pushed.

## GATES

- `validate.py` exit 0, zero new FAIL entries beyond the tracked baseline.
- `unittest discover` on the corpus test suite prints `OK`, run alone with no pipe/redirect.

## BUDGET

Single node, single commit. No code changes. Expect 3-5 tool-call rounds beyond research
already done.

## OPEN

- Whether `capabilities-onboarding-onboarding` (#799) will later declare a `part-of`
  edge from this node, once merged -- not this task's call.

## LEFT OUT

- Any edit to onboarding code, tests, or a second corpus document.
- Relationships to #797/#798/#799 (unmerged siblings) -- named as a gap instead.

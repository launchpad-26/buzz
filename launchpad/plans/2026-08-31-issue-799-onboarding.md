# Plan: issue #799 — document capabilities/onboarding/onboarding.md

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/onboarding/onboarding.md` does not exist; no `capabilities/` directory exists in the corpus yet.
- The `capability` template exists at `launchpad/docs/corpus/templates/capability.md` (node id `corpus-template-capability`, `type: capabilities`, required sections: Capability statement, Maturity, Boundary, Relationships, Scope and omissions).
- `node.schema.json`'s `type` enum spells the surface `capabilities` (plural), not `capability`.
- Siblings #796 (first-channel), #797 (first-community), #798 (first-identity) are unmerged — no relationship targets are available to or from them.
- The overall flow is glued together in `desktop/src/app/App.tsx`: `MachineBootstrap` (machine-level: identity/backup/setup, `useMachineOnboardingState` in `machineOnboarding.ts`) renders `MachineOnboardingFlow` until `stage === "ready"`, then renders `CommunityApp`, which renders `CommunityOnboardingFlow` (community-level: claim/connect/profile/team-intro/finalize, `communityOnboarding.tsx`) atop the mounting app when a transaction exists, and `AppReady` (`useAppOnboardingState` in `hooks.ts`) additionally gates a relay-scoped profile step (`OnboardingFlow.tsx`) and starter-channel initialization (`initializeStarterChannels`, `hooks.ts:74`).

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/onboarding/onboarding.md` against the capability template:
front matter (`id: capabilities-onboarding-onboarding`, `type: capabilities`, `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`, evidence ledger with a commit citation for HEAD plus one FACT/INFERENCE per body claim), then body sections: Capability statement, Maturity, Boundary (explicitly excluding first-identity/first-community/first-channel's own procedural detail, architecture, interface, operations), Relationships (none — no merged siblings), Scope and omissions.

**Done when:** file exists, front matter is schema-shaped, every claim has a citation.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.

**Done when:** exit 0, no new FAIL entries beyond the known 21 pre-existing baseline failures (issue #1951).

## STEP 3 — Commit gate

Run, as the sole command in its own tool call: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.

**Done when:** output ends `OK`.

## STEP 4 — Commit

`git add` the new doc + this plan; `git commit -s`. No push, no PR.

## GATES

- validate.py exits 0 with zero new FAIL entries.
- Unit test discovery prints `OK`.

## BUDGET

Single doc, ~1 sitting. No code changes.

## OPEN

- Exact boundary wording between this node and #796/#797/#798 will likely need a `references`/`part-of` pass once those merge — left as a documented gap, not resolved here.

## LEFT OUT

- No relationships to unmerged siblings.
- No changes to `desktop/src/features/onboarding/**` runtime code.

# Plan: issue #1249 — platforms/desktop/state-management corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/desktop/state-management.md` does not exist yet
  (confirmed: `find launchpad/docs/corpus/platforms` reports no such directory at
  `origin/launchpad`).
- `launchpad/docs/corpus/schema/node.schema.json` and `launchpad/docs/corpus/AGENTS.md`
  define the front-matter contract and authoring procedure; no per-type template for
  `type: platforms` exists yet among `launchpad/docs/corpus/templates/*.md` (13 template
  files, none named `platforms*`).
- The closest-fitting existing template is `templates/component.md` — its required
  sections (Responsibility, Public interface, Dependencies, Boundary, Relationships,
  Scope and omissions) match issue #1249's Definition of Done bullets ("states
  responsibility and well-defined interface/boundary", "names dependencies and
  collaborators", "links source implementation and tests", "explains only
  component-level behavior") almost verbatim, but that template directs `type:
  implementation`.
- Per the orchestrator's finding #4, sibling nodes already committed elsewhere in
  Feature #614 (not visible in this worktree) use `type: platforms` for documents under
  `platforms/**`, as an inference since no platforms-specific template exists. This node
  follows that same convention for consistency rather than `type: implementation`.
- `desktop/src/app/App.tsx` and `desktop/src/features/communities/useCommunityInit.ts`
  contain the real state-management source: two `QueryClient` instances (app/machine-level
  in `App()`, community-scoped in `CommunityQueryProvider`), the `resetCommunityState()`
  singleton-reset inventory, and the `communityKey`-based remount contract described in
  root `CLAUDE.md`'s "Community Switching" section.
- Sibling issues #1241 (frontend-backend-bridge), #1245 (react), #1243 (navigation) own
  IPC/bridge, general React patterns, and routing/navigation respectively — this node
  stays scoped to state management proper (query-client scoping, singleton reset
  inventory, remount interaction) and does not restate their subjects.

## STEP 1 — Confirm schema, templates, and non-existence (done during investigation)

Read `node.schema.json`, `AGENTS.md`, `templates/component.md`, and
`standards/taxonomy.md`; confirmed no `platforms/` directory exists in this worktree.
Done-when: understood which fields/enums are mandatory and which template shape to
imitate.

## STEP 2 — Investigate real desktop state-management source

Read `desktop/src/app/App.tsx` (both `QueryClient` construction sites, `communityKey`
composition, `AppReady`/`CommunityQueryProvider` remount keying),
`desktop/src/features/communities/useCommunityInit.ts` (`resetCommunityState()`, its
call sites, `hasInitializedRef` gating), `desktop/src/shared/api/queryClient.ts`
(`createBuzzQueryClient`), `desktop/src/shared/api/hooks.ts` (`useIdentityQuery` — proof
that query keys are not pubkey-namespaced, so per-community isolation comes from having
a separate `QueryClient` instance, not from key scoping), and
`desktop/src/features/agents/activeAgentTurnsStore.ts` (a module singleton with a
save-before-reset / restore-after-apply pattern, the one documented exception to plain
reset-on-switch). Done-when: every claim in the document is backed by a real path/line
I opened.

## STEP 3 — Draft the document

Write `launchpad/docs/corpus/platforms/desktop/state-management.md` using
`templates/component.md`'s section shape (Responsibility, Public interface / contract
surface, Dependencies, Boundary, Relationships, Scope and omissions), `type: platforms`,
`status: draft`, `origin: launchpad`, evidence entries classed FACT/INFERENCE/
TEAM_KNOWLEDGE per `AGENTS.md`'s rules, no `relationships` (no existing corpus node to
target — `find` above found none). Cover: the two-QueryClient scoping strategy,
`resetCommunityState()`'s current inventory (cite the real call list, do not hand-copy
it verbatim per root `CLAUDE.md`'s own instruction not to duplicate that list), the
hook-managed-singleton exception (`ChannelMuteSyncManager`/`ChannelSectionSyncManager`),
the `activeAgentTurnsStore` save/restore exception, and how `communityKey`-driven
remounting in `App.tsx` interacts with both. Explicitly exclude IPC/bridge mechanics
(#1241), general React patterns (#1245), and routing (#1243) in a Boundary section.
Done-when: every DoD bullet in #1249 is satisfied by a specific section.

## STEP 4 — Earn the commit gate

Run the corpus unit tests as a lone Bash call, then `git add` + `git commit -s`. Retry
once per finding #5 if the stamp is refused.

## STEP 5 — Verify

Re-run `validate.py` with the new file stashed vs. present to confirm zero new FAIL
lines; re-open every cited file/line one more time against the finished document text.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK, as its own lone Bash call.
- `python3 launchpad/project-intelligence/corpus/validate.py` → identical FAIL set with and without the new file present (pre-existing ~21-22 FAILs untouched; only new `UNVERIFIED` notices from this node's own commit-citation provenance entry are acceptable).
- Every DoD checkbox in issue #1249 satisfied by a specific section of the document.

## OPEN

- Whether a platforms-specific template lands later (per `AGENTS.md`'s own gap table,
  §1307-1351) that would ask this node to be reshaped; not resolved here.
- Whether any sibling `platforms/desktop/*` node (frontend-backend-bridge, react,
  navigation) has already merged with an id this node could `references` — not visible
  in this worktree, so no relationship is declared, consistent with `AGENTS.md`'s
  explicit warning against carrying forward a stale "nothing to point at" justification.

## LEFT OUT

- No second corpus document, no edits to `validate.py`, no edits to desktop source.
- No `relationships` entries (nothing in this worktree's merged corpus tree to target).
- No attempt to fix the two module-level stores found during investigation
  (`cardMintStore.ts`'s `resetCardMintStore`, `terminalPanelStore.ts`'s
  `resetTerminalPanelForTests`) that are not wired into `resetCommunityState()` — noted
  as an observed, low-confidence gap in the document's own Scope and omissions section,
  not fixed or filed as a new issue, since that is a runtime-behavior change out of this
  task's scope.

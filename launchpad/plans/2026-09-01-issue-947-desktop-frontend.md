Issue #947 — corpus node: implementation/desktop/frontend.md
Stated size: not stated on the issue; dispatch brief for this batch caps it at 5 steps  →  cap: 5 steps

ALREADY TRUE  (verified against git, not notes)
  `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md` and
  `launchpad/docs/corpus/templates/implementation-reference.md` are merged on
  `origin/launchpad` (HEAD 76a0a4ebbe4bc4d852b0d04362ed768620da34b3). The target file
  `launchpad/docs/corpus/implementation/desktop/frontend.md` does not exist yet (`ls`
  confirms `No such file or directory`). `launchpad/docs/corpus/architecture/containers/desktop.md`
  (id `architecture-containers-desktop`) exists and explicitly disclaims the frontend's
  internal structure ("only its existence and IPC-only relationship to the backend is
  claimed here"), leaving this node's territory genuinely open. `git ls-tree -r --name-only
  HEAD -- launchpad/docs/corpus` shows no `implementation/` node exists yet anywhere in the
  corpus, so `architecture-containers-desktop` is the only plausible relationship target.

STEP 1  [independent]
        Verify each frontend claim from CLAUDE.md against real code rather than
        restating it: `desktop/package.json` (React/Vite/Tailwind/@tauri-apps/api/
        @tanstack versions), `desktop/src/main.tsx` (provider hierarchy),
        `desktop/src/app/App.tsx` (`communityKey`/`AppReady` remount),
        `desktop/src/features/communities/useCommunityInit.ts` (`resetCommunityState`),
        `desktop/src/app/useWebviewZoomShortcuts.ts` and `desktop/scripts/check-px-text.mjs`
        (rem zoom + CI guard), `desktop/src/shared/hooks/useStableReference.ts` plus one
        real `mutateAsync`-stability caller. Already done in this session (read directly,
        not from memory) — this step records it as a plan step for traceability.
        done when: each of the 6 CLAUDE.md claims (a–d above, provider hierarchy,
        singleton reset) has a specific file:line or symbol citation opened this
        session, not merely CLAUDE.md's own text.

STEP 2  [needs 1] ← RUNS HERE
        Write the corpus node body against `implementation-reference.md`'s required
        sections (Realization statement, Target, Implementation surface, Divergences,
        Verification, Relationships, Scope and omissions) plus schema-valid front
        matter: id `implementation-desktop-frontend`, type `implementation`, status
        `draft`, origin `launchpad`, audiences `[developer, agent, reviewer]`, evidence
        entries classified FACT/INFERENCE/TEAM_KNOWLEDGE per what was actually opened
        in Step 1, and a `part-of` relationship to `architecture-containers-desktop`
        (the only existing corpus node this frontend node is a constituent piece of).
        Target for the realization statement is `CLAUDE.md`'s "Desktop App" section
        itself (a repo convention doc, not a spec/decision with a corpus id) — state
        plainly that no `implements` edge is declared because the target carries no
        corpus node id yet, per `AGENTS.md`'s rule against inventing one.
        done when: `launchpad/docs/corpus/implementation/desktop/frontend.md` exists,
        has all 7 required template sections, and every substantive claim has an
        evidence entry citing a path this session actually opened.

STEP 3  [needs 2]
        Run `python3 launchpad/project-intelligence/corpus/validate.py` against the
        full tree; fix and re-run until it reports zero FAIL entries for this node (a
        pre-existing baseline of ~21 unrelated failures on `origin/launchpad` is
        expected and not this task's to fix — confirm via `git stash`/diff if the exit
        code is nonzero).
        done when: `validate.py` produces no FAIL line whose file path is
        `launchpad/docs/corpus/implementation/desktop/frontend.md`.

STEP 4  [needs 3]
        Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` as the sole command in its own tool call and confirm `OK`. In a
        separate tool call, `git add` the node and this plan file, then
        `git commit -s -m "docs(corpus): add desktop frontend implementation reference (#947)"`.
        Do not push, do not open a PR — this batch integrates into one Feature-level PR
        later.
        done when: the unittest run prints `OK` and `git log -1` shows the new commit
        with both files staged.

STEP 5  [needs 4]
        Self-review the finished diff line-by-line against issue #947's Definition of
        Done checklist, and against every DoD bullet (states responsibility/non-ownership,
        names public interfaces, links owned paths and tests, avoids restating
        `architecture-containers-desktop`'s canonical claims). Report residual concerns
        honestly rather than silently.
        done when: a written pass confirms each DoD bullet is met or explicitly notes
        why not, before final report.

PARALLEL  none — one file, one worktree, each step's output is the input to the next;
          no independent subagent fan-out is warranted for a single corpus document.
GATES     `python3 launchpad/project-intelligence/corpus/validate.py` (Step 3) must
          exit clean for this node; `python3 -m unittest discover -s
          launchpad/project-intelligence/corpus/tests -p "test_*.py"` (Step 4) must
          report OK before commit. `corpus-review` is the fit-for-purpose review skill
          for a docs-only corpus node (not `review-code`); use it in Step 5 if reachable
          in-session, otherwise a careful self-review stands in and is reported as such.
          `qa` explore mode does not apply — no runtime UI/CLI surface is produced by
          this task, only a Markdown document.
BUDGET    Step 1/2 (evidence-gathering and drafting the Implementation surface table)
          is the step most likely to eat the budget — the desktop frontend is a large
          surface (`desktop/src/features/` alone has 29 feature directories), so the
          node deliberately scopes to CLAUDE.md's own named conventions rather than
          attempting exhaustive feature-by-feature coverage.
OPEN      The issue's DoD does not say whether "frontend" should attempt to catalogue
          the `desktop/src/features/` tree exhaustively or scope to the
          cross-cutting conventions CLAUDE.md already names (rem sizing, community-key
          remount, render-perf gotchas, provider hierarchy). This plan takes the
          narrower, evidence-dense reading and says so in Scope and omissions, since
          the issue explicitly warns against folding a second concept into one node —
          a full feature-by-feature catalogue would be several nodes' worth of content,
          not one.
LEFT OUT  No `implements` edge (the realization target — CLAUDE.md's own frontend
          conventions section — is not itself a corpus node with an id, and AGENTS.md
          bars inventing one). No attempt to document the ~29 individual feature
          modules under `desktop/src/features/` — each is its own future node's
          subject, per the corpus's one-idea-per-node rule. No `git push` / `gh pr
          create` — this batch integrates into one Feature-level PR in a later,
          separate phase, per explicit task instructions.

# Plan: issue #751 — document capabilities/git/repository-browser.md

Parent: Feature #613. Batch mode: local commit only, no push/PR (integration phase
assembles the Feature-wide PR later).

## ALREADY TRUE

- `launchpad/docs/corpus/templates/capability.md` exists and is the template to
  follow for a `type: capabilities` node (required sections: Capability statement,
  Maturity, Boundary, Relationships, Scope and omissions).
- `launchpad/docs/corpus/capabilities/git/repository-browser.md` does not exist on
  `origin/launchpad` or in this worktree.
- No `capabilities/` directory exists in the corpus at all yet — this is the first
  node under that surface. Nine sibling tasks (#744-750, #752-753) cover other
  `capabilities/git/*` docs and are being authored in parallel, isolated worktrees;
  none are confirmed merged to `origin/launchpad`, so none are valid relationship
  targets per `AGENTS.md` step 9 (must resolve against the merge-target branch, not
  the author's own worktree).
- Issue #1290 ("document platforms/web/repository-browser.md") is a distinct sibling
  node (different `type`: `platforms`, not `capabilities`) — not this task, and also
  unmerged, so not a valid relationship target either.
- VISION_PROJECTS.md's Status table (line 256) already marks "Git hosting (smart
  HTTP + NIP-34)" as "Ships today" — usable as a maturity citation for the parent
  git-hosting capability, though this node's subject is narrower (the browsing UI,
  not the hosting/push transport `architecture-flows-git-push` already documents).
- `web/` is the browser web client served by the relay (per root CLAUDE.md); the
  repository browser is a UI feature there, reading repos over the relay's git
  smart-HTTP + REST surface.

## STEP 1 — Gather evidence on the actual repository-browser feature

Identify the concrete `web/` entry point(s)/component(s) implementing the
repository browser (file tree, file content view, commit/branch navigation), any
relay endpoints it calls, auth/visibility constraints, and existing tests
(Playwright/unit). Record exact paths and line ranges for citation. Note anything
expected but not verifiable (e.g., untested UI states).

Done when: a concrete list of cited source paths + line ranges backs each planned
claim, and gaps are named explicitly rather than glossed over.

## STEP 2 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/repository-browser.md` against
`node.schema.json` + `templates/capability.md`:
- Front matter: `id: capabilities-git-repository-browser`, `type: capabilities`,
  `status: draft`, `origin: launchpad`, `audiences: [agent, developer, reviewer]`,
  `evidence` ledger (commit citation + one entry per claim, classified honestly).
- No `relationships` (nothing valid to target yet — see ALREADY TRUE).
- Body: Capability statement, Maturity (cited), Boundary (excludes architecture/
  interface/flow/operations per template), Relationships (declared: none, and why),
  Scope and omissions (what's covered / gaps table / expected-but-not-verified).

Done when: the file exists, is schema-shaped per the template, and every
substantive claim traces to a real cited source.

## STEP 3 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Confirm exit 0 (or, if pre-existing baseline FAILs from #1951 are present, confirm
this new node contributes zero new FAIL entries).

Done when: validator output shows no new FAIL attributable to this node.

## STEP 4 — Earn commit gate and commit

Run, as the sole command in its own tool call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`
Confirm `OK`. Then, in a separate call, stage the new doc + this plan file and
commit with `git commit -s -m "docs(corpus): document capabilities/git/repository-browser (#751)"`.

Done when: commit exists on `task/751-repository-browser`, gate passed, no push/PR.

## STEP 5 — Self-review

Re-read the diff against #751's DoD checklist line by line. Re-open every cited
source to confirm the evidence backs the claim. Confirm exactly one canonical doc
was created and no new validate.py FAIL entries were introduced. Note that
`review-code`/`review-adjudicate` were deliberately not run (deferred per batch
mode) — this self-review substitutes for them.

## PARALLEL

None — this is a single-file, single-agent task with no concurrent work in this
worktree.

## GATES

1. `python3 launchpad/project-intelligence/corpus/validate.py` — zero new FAIL.
2. `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` — must print `OK` before any `git commit`.

## BUDGET

Single node, single commit. No push, no PR — stop at commit per batch-mode
instructions.

## OPEN

- Whether the repository-browser feature has any dedicated Playwright/e2e test
  coverage, or only manual/mock-bridge screenshot tooling — resolved during STEP 1.
- Exact maturity framing (shipped vs in-progress) for the browsing UI specifically,
  as distinct from the git-hosting transport capability VISION_PROJECTS.md marks
  "Ships today."

## LEFT OUT

- Any `capabilities/git/*` sibling node (git-hosting, smart-http, patch, etc.) —
  each is its own task (#744-750, #752-753).
- The `platforms/web/repository-browser.md` node (#1290) — different `type`, a
  different task.
- Architecture/interface/flow-level detail about how the browser is built, what
  boundary it's exposed through, or the step-by-step flow through it — explicitly
  out of scope per `templates/capability.md`'s Boundary section.
- Adding `relationships` — nothing valid to target yet on `origin/launchpad`.

# Plan: issue #745 — document capabilities/git/git-hosting.md

Parent: Feature #613. Batch mode: local commit only, no push/PR.

## ALREADY TRUE

- `launchpad/docs/corpus/capabilities/` does not exist yet on `origin/launchpad` —
  this will be the corpus's first `type: capabilities` instance node.
- `launchpad/docs/corpus/templates/capability.md` (id `corpus-template-capability`,
  merged, `type: governance`) fully specifies the required body shape: Capability
  statement, Maturity, Boundary, Relationships, Scope and omissions — this plan
  builds directly against it rather than re-deriving structure.
- `launchpad/docs/corpus/architecture/flows/git-push.md` (merged, `type: architecture`)
  already documents the push transport flow in depth. This node must **not**
  duplicate that — it cites it as the flow-level companion and stays at the
  "what the product can do" altitude.
- VISION_PROJECTS.md's Status table (`VISION_PROJECTS.md:256`) already marks
  "Git hosting (smart HTTP + NIP-34)" as "✅ Ships today" — usable as Maturity
  evidence.
- Sibling issues #746-#753 cover adjacent, more specific slices (object storage,
  signing, auth, patch, repo-announcement, browser, repository, smart-http). None
  are confirmed merged to `origin/launchpad` at this revision, so no `references`
  edges to them are possible; the Boundary section names them by subject only.
- `corpus-template-capability` itself IS merged on `origin/launchpad`, so an
  `implements` relationship targeting `corpus-template-capability` is a valid edge.

## STEP 1 — Draft the node

Write `launchpad/docs/corpus/capabilities/git/git-hosting.md`, `id:
capabilities-git-git-hosting`, `type: capabilities`, `status: draft`, `origin:
launchpad`, `audiences: [agent, developer, operator, reviewer]`.

Body follows the template skeleton: Capability statement (git clone/push over
smart HTTP, backed by NIP-34 repo-announcement/state events, so a repo survives
without Buzz per VISION.md's sovereignty framing) / Maturity (ships today, cited
to `crates/buzz-relay/src/api/git/transport.rs` module doc + VISION_PROJECTS.md
status row) / Boundary (not the transport/auth internals — cites
`architecture-flows-git-push`; not object storage, signing, patches, browser,
etc. — names the sibling issues' subject matter only, no unmerged-id edges) /
Relationships (`implements: corpus-template-capability`; no `references` — no
architecture/interface node for git hosting specifically is confirmed merged
apart from the flow node, which is cited in prose per template guidance, not
declared as an edge unless its id is verified merged) / Scope and omissions.

Evidence ledger: provenance commit citation (HEAD at worktree creation), FACT
entries for each code/doc citation opened directly (transport.rs route table,
kind.rs kind constants, git-push.md flow node, VISION_PROJECTS.md status row,
buzz-cli repos.rs, web repo-browser files, e2e_git.rs test names), TEAM_KNOWLEDGE
for issue-sourced scoping claims (the sibling-issue boundary), no INFERENCE
expected unless a reasoning step is needed for the capability/architecture
boundary call.

**Done when:** file exists, front matter is schema-shaped by inspection, every
FACT cites an opened source.

## STEP 2 — Validate

Run `python3 launchpad/project-intelligence/corpus/validate.py` from repo root.
Confirm exit 0 and zero new FAIL entries beyond the known 21 pre-existing ones
(tracked in #1951).

**Done when:** validator output shows this node passing and the FAIL count is
unchanged from the `origin/launchpad` baseline.

## STEP 3 — Earn the gate and commit

Run, as the sole command in its own call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm `OK`. Then, in a separate call, stage the new doc + this plan file and
commit with `git commit -s`.

**Done when:** commit exists on `task/745-git-hosting`, nothing pushed.

## STEP 4 — Self-review

Re-read the DoD checklist line by line against the diff. Re-open every cited
source. Confirm exactly one hand-authored canonical doc was created. Confirm no
new validate.py FAIL entries.

## GATES

- `validate.py` exit 0, no new FAIL entries.
- `unittest discover` on corpus tests: `OK`.
- Every FACT/INFERENCE evidence entry cites a real, opened path.

## BUDGET

4 steps, single node, no code changes.

## OPEN

- Whether `architecture-flows-git-push` should be a declared `references` edge:
  left undeclared per AGENTS.md step 9 unless independently reconfirmed merged
  at commit time (it appeared in this worktree's `origin/launchpad` checkout, so
  it is in fact eligible — confirm at Step 1 and add the edge if so).

## LEFT OUT

- No changes to `architecture-flows-git-push` or any other existing node.
- No new relationships from other nodes back to this one (out of scope; a later
  pass may add them once siblings land).

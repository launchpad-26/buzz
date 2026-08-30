Issue #1042 (launchpad-26/buzz) — document layers/compute/kubernetes-provider.md
Parent PRD #611.
Stated size: issue carries no explicit Size line; dispatch brief caps a single corpus document task at 5 steps -> cap: 5 steps

ALREADY TRUE

- Worktree `__worktrees/task-1042-kubernetes-provider` exists on branch
  `task/1042-kubernetes-provider`, checked out from `origin/launchpad` at
  `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`.
- Target path `launchpad/docs/corpus/layers/compute/kubernetes-provider.md`
  does not exist yet (confirmed with `test -f`) and no PR references issue
  #1042 (`gh pr list --search "1042"` returns empty) — nothing to collide
  with.
- `launchpad/docs/corpus/templates/concept.md` is merged and present, so
  the "single canonical concept node" from the issue's Objective maps to a
  real, merged template — no no-template fallback needed.
- The real subject exists in the repo: crate `crates/buzz-backend-kubernetes`
  (a conforming `buzz-backend-<id>` provider per `docs/remote-agents.md`),
  its module docs, `wire.rs`, `config.rs`, `pod.rs`, `reconcile.rs`, `gc.rs`
  read and confirmed against the spec's Kubernetes Binding section
  (`docs/remote-agents.md:991-1335`).
- Two existing corpus nodes already name this gap explicitly and defer to
  a future node: `architecture-deployment-kubernetes` (out-of-scope note,
  "It belongs in its own node") and `architecture-containers-agent-runtime`
  (cites `docs/remote-agents.md` for the provider protocol generally). Both
  ids confirmed present in `git ls-tree -r origin/launchpad -- launchpad/docs/corpus`.
- `node.schema.json` read in full: seven top-level keys, evidence entry_class
  rules (FACT/INFERENCE/TEAM_KNOWLEDGE with their required/forbidden
  sibling fields), relationships enum (`depends-on`, `supersedes`,
  `implements`, `references`, `part-of`).
- `launchpad/docs/corpus/AGENTS.md` read in full (governing procedure).

STEP 1 — Draft front matter and provenance [independent]

Write the YAML front matter: `id: layers-compute-kubernetes-provider`,
`type: layers`, `status: draft`, `origin: launchpad`,
`audiences: [agent, developer, operator]`, and a first evidence entry
recording the provenance FACT (commit `338b4d0cf2dd76cc43964bb717ce9f0a94a9c7a5`).
Add `relationships` entries (type `references`) to
`architecture-deployment-kubernetes` and `architecture-containers-agent-runtime`
only — both confirmed to exist on `origin/launchpad`.

done when: the file has valid YAML front matter with exactly those seven
permitted top-level keys and the two `references` relationships present.

STEP 2 — Write the body per concept.md's required sections [needs 1]

Definition (what the Kubernetes provider is, one sentence first), boundary/
non-goals (relay's own Helm deployment topology is a different node; agent
conversational behavior is the ACP harness's; substrate/RBAC security and
malicious-provider containment are explicitly out of scope per
`docs/remote-agents.md`'s own Scope and Non-Goals section), use cases
(deploying a managed agent as a pod instead of local spawn; at-most-one-live
-instance reconciliation; auto-stop via `inactivity_seconds`), an optional
comparison (this binding vs. the spec's other named binding, the systemd/SSH
deployer of PR #3449, and vs. local spawn), related resources expressed as
the Step 1 relationships plus a citation to `docs/remote-agents.md`, and the
required scope-and-omissions section (what's not covered + what was
expected but not verified, e.g. the desktop-side Known Defect 3 gap in
`launch` payload wiring, and the gated `OnFailure`/indefinite-lifetime
combination).

done when: every claim in the body has a corresponding `evidence` entry in
front matter classified FACT/INFERENCE/TEAM_KNOWLEDGE honestly, each FACT
citing a source actually opened this session (crate source, `docs/remote-
agents.md`, or its inline tests).

STEP 3 — Validate [needs 2] <- RUNS HERE

Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root and fix anything it names, iterating to a clean exit.

done when: `validate.py` exits 0.

STEP 4 — Earn the verify-gate stamp and commit [needs 3]

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` as the sole command in its own tool call, confirm `OK`,
then commit with `git commit -s -m "docs(corpus): document kubernetes provider (#1042)"`.

done when: the test run reports `OK` and `git log -1` on the branch shows
the new commit with the corpus file staged.

STEP 5 — Self-review against the issue's DoD checklist [needs 4]

Re-read the diff line by line against every DoD bullet in issue #1042 (one
document only, schema-valid front matter, one independently maintainable
node, FACT/INFERENCE/TEAM_KNOWLEDGE not conflated, links instead of
duplicated content, checked against the recorded revision, clean
`validate.py`, definition-in-one-sentence, boundaries stated, related
concepts linked, examples that don't introduce a second concept). Confirm
no second hand-authored corpus document was created.

done when: each DoD bullet is confirmed satisfied or an honest gap is
recorded in the final report as "not verified".

PARALLEL

None of the steps above are safely parallel with each other — this is a
single small document built sequentially (front matter needs the evidence
gathered before it; body needs front matter's relationship targets decided;
validate needs the body; commit needs a clean validate; review needs the
commit). Step 1 is tagged `[independent]` only in the sense that it does not
depend on a *prior plan step* — its own inputs (repo investigation) are
already done, per ALREADY TRUE.

GATES

- `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0
  before commit (Step 3).
- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` must report `OK`, run as the sole command in its own
  tool call, before commit (Step 4) — this is the verify-gate stamp
  requirement from the dispatch brief.
- No `git push`, no `gh pr create` — this branch is folded into a later
  shared batch PR by a separate process.

BUDGET

One document (~150-250 lines of body prose), one commit. No code changes,
no changes outside `launchpad/docs/corpus/layers/compute/kubernetes-
provider.md` and this plan file.

OPEN

- Whether `audiences` should include `reviewer` in addition to
  `agent, developer, operator` — left to the drafting step's judgment
  against what the body actually says, not decided here.
- Exact wording of the comparison section (systemd/SSH deployer vs. local
  spawn vs. this binding) — content judgment, not a planning decision.

LEFT OUT

- Documenting the full provider wire protocol (`info`/`deploy` payload
  schema, the seven-row deploy state machine, GC internals) in exhaustive
  reference detail — that duplicates `docs/remote-agents.md` itself, which
  a concept node must link to, not restate (`AGENTS.md`'s "links instead of
  duplication" rule, and `concept.md`'s boundary against reference-shaped
  content, issue #1346's territory).
- Editing `architecture-deployment-kubernetes` or `architecture-containers-
  agent-runtime` to add inbound `referenced-by` edges back to this new
  node — out of scope per the issue ("second hand-authored canonical
  corpus document"); this task only adds outbound `references` from the
  new node.
- Filing any follow-up issue for a second concept — investigation so far
  found none; if drafting reveals one, it is filed and named in the final
  report, not folded in here.

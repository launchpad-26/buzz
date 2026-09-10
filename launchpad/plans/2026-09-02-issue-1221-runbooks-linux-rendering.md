# Plan — issue #1221: operations runbook, Linux desktop rendering

Issue #1221 (task, no stated Size line in the DoD body). Treating an
unsized single-document corpus task the same way merged sibling plans in
this batch have (one hand-authored file, capped low).

Stated size: unsized task, single corpus document -> cap: 5 steps

ALREADY TRUE: worktree `/home/serina/Launchpad/buzz/__worktrees/task-1221-runbooks-linux-rendering`
exists, is on branch `task/1221-runbooks-linux-rendering`, tracks
`origin/launchpad`, and is clean at `git rev-parse HEAD` =
`473205a7457b208455f188847bfb27b01aa83cac`. The target file
`launchpad/docs/corpus/operations/runbooks/linux-rendering.md` does not exist
(confirmed with `ls`: no `operations/` directory exists anywhere under
`launchpad/docs/corpus/` yet). The runbook template
(`launchpad/docs/corpus/templates/runbook.md`, id `corpus-template-runbook`)
is merged on `origin/launchpad` (present in `existing-node-ids.txt`) and
defines the required sections: Trigger, Severity and impact, Diagnosis,
Mitigation and resolution, Escalation, Scope and omissions. This repository
already documents this exact failure class in two real, openable sources:
`docs/linux-rendering-troubleshooting.md` (a full troubleshooting guide —
symptom table, root causes, fixes, per-GPU workarounds) and
`desktop/src-tauri/src/webkit_rendering.rs` (the Rust module that decides and
applies the `WEBKIT_DMABUF_RENDERER_FORCE_SHM` / `--safe-rendering`
workaround at process start, called from `desktop/src-tauri/src/main.rs`),
plus its test suite `desktop/src-tauri/src/webkit_rendering/tests.rs`. CI's
`.github/workflows/ci.yml` builds and tests the desktop app on
`ubuntu-latest` for every PR in this fork; by contrast
`.github/workflows/linux-canary.yml` and `.github/workflows/release.yml` —
the jobs that produce a distributable `.AppImage`/`.deb` — are gated
`if: github.repository == 'block/buzz'` and do not run in this fork
(`launchpad-26/buzz`). `launchpad/README.md` and `launchpad/AGENTS.md` state
this fork operates and deploys Buzz for rhizomorph but does not develop it.
Existing merged corpus nodes `development-prerequisites`,
`layers-lifecycle-startup`, and `architecture-containers-desktop` are on
`origin/launchpad` (confirmed in `existing-node-ids.txt`) and are topically
adjacent.

STEP 1 [independent] — Gather and cross-check evidence: open and read in
full `docs/linux-rendering-troubleshooting.md`,
`desktop/src-tauri/src/webkit_rendering.rs`,
`desktop/src-tauri/src/webkit_rendering/tests.rs`,
`desktop/src-tauri/src/main.rs`, `.github/workflows/ci.yml` (desktop job),
`.github/workflows/linux-canary.yml` (repository gate), `CONTRIBUTING.md`
(Linux Tauri system libraries section), `launchpad/README.md` and
`launchpad/AGENTS.md` (fork operating scope). RUNS HERE. done when: every
source above has been opened this session and its relevant statement
located, ready to cite.

STEP 2 [needs 1] — Write the corpus node
`launchpad/docs/corpus/operations/runbooks/linux-rendering.md` with
`id: operations-runbooks-linux-rendering`, `type: operations`,
`status: draft`, `origin: launchpad`, `audiences: [operator, developer,
agent]`. Body follows the runbook template's required sections: Trigger,
Severity and impact, Prerequisites, Diagnosis, Mitigation and resolution,
Verification of recovery, Escalation, Evidence to preserve, Scope and
omissions (two distinct parts: what it does not cover / who owns it, and
what was expected but could not be verified). Declare relationships to
`layers-lifecycle-startup` and `development-prerequisites` (type
`references`) and `corpus-template-runbook` (type `implements`) — all three
ids confirmed present in `existing-node-ids.txt`. State plainly, in Scope
and authority, that this fork does not itself build or distribute a Linux
desktop package, citing the `if: github.repository == 'block/buzz'` gates.
done when: the file exists, front matter parses as YAML, and every Required
section from the template has real prose (not a placeholder).

STEP 3 [needs 2] — Validate: run
`python3 launchpad/project-intelligence/corpus/validate.py` from the repo
root. Fix any error named. Re-run until exit 0. done when: the command
exits 0.

STEP 4 [needs 3] — Self-review against the issue DoD: re-read the drafted
node against every DoD bullet in issue #1221. Fix anything unmet.
done when: every DoD bullet is either satisfied by a named section, or
recorded as unsatisfiable in the report.

STEP 5 [needs 4] — Commit: run the corpus test suite as the sole command in
its own Bash call:
`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`.
Confirm OK. Then, in a separate call, `git add -A && git commit -s -m
"docs(corpus): add operations runbook for Linux desktop rendering failures
(#1221)"`. done when: the commit exists locally on
`task/1221-runbooks-linux-rendering`, with `-s` (DCO), and nothing pushed.

PARALLEL: none — this is a single-document task with sequential
dependencies (evidence before drafting, draft before validating, validation
before commit).

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must
exit 0 before commit. `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` must print OK,
run as the sole command in its own Bash call, before `git commit -s`.
`git commit -s` (DCO trailer) is mandatory; no `--no-verify`.

BUDGET: one document, one plan file. No code changes. Expected total: under
250 lines of body prose plus front matter, well under the 1000-line
file-size gate.

OPEN: whether `audiences` should also include `reviewer` — the template's
own front matter includes it, but this node's task (#1221) does not name a
reviewer-specific concern beyond ordinary corpus review, so it is left off
unless drafting reveals a reviewer-specific section.

LEFT OUT: no second corpus document — if drafting surfaces a second concept
(e.g. a general "desktop build troubleshooting" node distinct from
rendering), it is filed as its own issue, not folded in here. No
relationship to `corpus-template-runbook`'s sibling standards
(`normative-language`, `evidence`) beyond what MUST/SHOULD phrasing already
implies — this node introduces no new normative-keyword convention. No
change to `docs/linux-rendering-troubleshooting.md` or
`desktop/src-tauri/src/webkit_rendering.rs` — this task documents them, it
does not edit upstream product code or docs.

# Plan — issue #847: document `development/change-impact.md`

Issue: [launchpad-26/buzz#847](https://github.com/launchpad-26/buzz/issues/847)
Parent feature: #619 · Repository revision planned against: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`
Branch: `task/847-development-change-impact` · Worktree:
`/home/serina/Launchpad/buzz/__worktrees/task-847-development-change-impact`

## ALREADY TRUE

Verified in this worktree at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`:

- `launchpad/docs/corpus/development/change-impact.md` **does not exist**. The
  `development/` directory holds exactly four merged nodes: `build.md`,
  `debugging.md`, `hermit.md`, `prerequisites.md`.
- The node shape is a **reference node**; the structural model is
  `launchpad/docs/corpus/templates/reference.md` (Diátaxis Reference form + The
  Good Docs Project's three-section template).
- The front-matter contract is `launchpad/docs/corpus/schema/node.schema.json`:
  seven permitted fields, six required, `additionalProperties: false`;
  `type: development` and `origin: launchpad` are both legal enum members.
- `python3 launchpad/project-intelligence/corpus/validate.py` is the
  deterministic checker; `.github/workflows/launchpad-corpus-validate.yml` runs
  it on every PR touching `launchpad/docs/corpus/**`.
- The two already-merged siblings in this feature use ids `development-hermit`
  and `development-prerequisites` — `<directory>-<filename-stem>`, no `corpus-`
  prefix. `development/build.md` (`corpus-development-build`) and
  `development/debugging.md` (`debugging`) deviate; they are outliers, not the
  convention.
- Evidence for the subject already exists on disk and has been read:
  `.github/workflows/ci.yml` (the `changes` job's `dorny/paths-filter` groups and
  every job's `if:`), `lefthook.yml` (pre-commit / commit-msg / pre-push lanes and
  their globs), `scripts/check-file-sizes-core.mjs` +
  `desktop|web|mobile/scripts/check-file-sizes.mjs`, `Justfile`,
  `scripts/test-ci-changed-paths-filter.sh`, `CONTRIBUTING.md`, `AGENTS.md`,
  `launchpad/AGENTS.md` §3, and the `launchpad-*.yml` workflow triggers.
- Issue **#442** (OPEN) already records the `'justfile'` / `Justfile` casing
  defect in CI's `rust` filter. No new issue is needed for it.

## STEP 1 — fix scope so the node stays atomic

Scope the node to **one idea**: *given a changed path, which automated gates
evaluate it, and which companion files must change with it.* Explicitly defer
every per-domain change procedure to its own sibling task (#848
configuration-changes, #855 database-changes, #858 event-kind-changes, #861
protocol-changes, #862 public-api-changes) and the build/run procedure to #846.

**Done when:** the boundary section names those siblings and the node contains no
step-ordered task instruction.

## STEP 2 — write the provenance ledger first

One `evidence` entry per substantive claim, classified honestly:

- First entry: `FACT`, `commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` — the
  recorded revision (`git cat-file -e` confirms it exists).
- Every path-filter, lane, job-condition and ratchet-rule claim: `FACT` citing the
  bare repository path actually opened.
- The `Justfile` casing consequence: the literal strings are `FACT`; the
  "therefore the lane never fires" consequence is `INFERENCE` with `confidence`,
  because dorny/paths-filter's pinned picomatch version was not executed.
- Issue-sourced claims (#442, #847's own DoD): `TEAM_KNOWLEDGE` with
  `provided_by` and **no** `confidence` — an issue URL is not an openable file.

**Done when:** every body claim maps to a ledger entry and no `FACT` rests only on
a commit citation except the provenance entry.

## STEP 3 — write the body in reference form

Sections, in this order: reference description; CI path-filter groups table;
CI job → trigger condition table; local hook lane table; always-on/unfiltered
gates; companion-change contracts (change X → also change Y); fork-specific
impact (`launchpad/AGENTS.md` §3, `launchpad-*.yml`, `branches: [main]` gating);
known CI-vs-local asymmetries; boundary; relationships; scope and omissions.

Constraints: exactly one level-1 `#` heading as the first line after the front
matter; "front matter" spelled as two words; the `evidence` array called the
"provenance ledger"; generated-vs-authored values labelled; hard ceiling 1000
lines.

**Done when:** the file exists, is under 1000 lines, and every DoD bullet in #847
maps to a section.

## STEP 4 — declare no relationships, with the real reason

Enumerate merged corpus ids on `origin/launchpad` (not this worktree). Declare
`relationships: none` and state in prose which candidate nodes were checked and
why none is a resolving target, plus a prose "See also" naming sibling paths.

**Done when:** the front matter carries no `relationships` key and the body
records what was enumerated.

## STEP 5 — validate, gate, commit

Run `python3 launchpad/project-intelligence/corpus/validate.py` → PASS.
Then, as a lone command, `python3 -m unittest discover -s
launchpad/project-intelligence/corpus/tests -p "test_*.py"` → OK.
Then `git add` + `git commit -s` in a separate call. Stop at the commit.

**Done when:** validate.py exits 0, the corpus test suite reports OK, and one
commit exists on `task/847-development-change-impact`.

## PARALLEL

None — the steps are strictly sequential (ledger before body, body before
validation).

## GATES

| Gate | Command | Must report |
|---|---|---|
| Corpus validation | `python3 launchpad/project-intelligence/corpus/validate.py` | `PASS` (UNVERIFIED notices are acceptable) |
| Commit gate | `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` | `OK` |
| File size | node body under 1000 lines | — |

## BUDGET

One new corpus node plus this plan. No source file, workflow, hook or script is
modified. No push, no PR, no branch other than
`task/847-development-change-impact`.

## OPEN

- Whether dorny/paths-filter v4's pinned picomatch matches case-sensitively was
  not executed against that exact version; only picomatch 2.3.2 outside this
  repository was. The node records this as an inference and as an omission.
- Whether any tooling enforces the desktop `kinds.ts` ↔ mobile
  `nostr_models.dart` ↔ `buzz-core/src/kind.rs` sync: a repository-wide search
  found no such script. Recorded as a negative result, not as proof of absence.

## LEFT OUT

- Per-domain change procedures (configuration, database, event kinds, protocol,
  public API) — owned by #848, #855, #858, #861, #862.
- How to run the build or the app — #846, #864–#867.
- Any edit to `ci.yml`, `lefthook.yml` or the ratchet. Issue #442 already owns the
  casing defect; this node documents it, it does not fix it.
- Filing new issues. #442 already exists; no duplicate is opened.

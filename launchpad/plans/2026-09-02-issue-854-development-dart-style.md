# Plan — issue #854: document `development/dart-style.md`

Repository revision: `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90` (`origin/launchpad`).
Worktree: `__worktrees/task-854-development-dart-style`, branch
`task/854-development-dart-style`.

## ALREADY TRUE

- `launchpad/docs/corpus/development/` exists and holds four merged nodes:
  `build.md`, `debugging.md`, `hermit.md`, `prerequisites.md`. The target
  `dart-style.md` does **not** exist — confirmed by `ls`.
- `origin/launchpad` carries 229 corpus Markdown nodes. `development-hermit` and
  `development-prerequisites` are real, resolvable ids; `build.md` carries
  `corpus-development-build` and `debugging.md` carries `debugging`, so the
  directory itself already shows three different id conventions.
- The subject matter is fully present in this checkout and readable without any
  build: `mobile/analysis_options.yaml`, `mobile/pubspec.yaml`,
  `mobile/pubspec.lock`, `AGENTS.md` §Mobile App, `Justfile` mobile recipes,
  `lefthook.yml` mobile lanes, `.github/workflows/ci.yml` `mobile` job,
  `mobile/scripts/check-file-sizes.mjs`, `scripts/check-file-sizes-core.mjs`,
  `mobile/lib/shared/theme/{theme_extensions,grid,app_theme}.dart`.
- `python3 launchpad/project-intelligence/corpus/validate.py` runs without the
  Hermit environment.

## STEP 1 — read the contract before drafting

Read `launchpad/docs/corpus/AGENTS.md`, `schema/node.schema.json`, and
`templates/reference.md`. Done-when: the front-matter field set, the three
evidence classes and their conditional fields, and the reference template's six
required body sections are all known and not guessed.

## STEP 2 — collect evidence

Open every source that will back a claim and record what it literally says.
Done-when: each intended claim has a repo-relative path (preferred over any URL
form) that was actually opened, and anything expected-but-unverifiable is on a
list for the omissions section.

Known unverifiable up front: `flutter_lints` 6.0.0's own `flutter.yaml` rule
list is not vendored in this repo and no pub cache is present, so the specific
lints it enables (e.g. `avoid_print`) cannot be established here.

## STEP 3 — write the node

Write `launchpad/docs/corpus/development/dart-style.md` in the reference shape:
one `#` heading, reference description, structured tables of rules keyed to
their enforcing artefact, a commands table, a boundary section, and a scope-and-
omissions section carrying both the boundary and the confidence disclosure.

Front matter: `id: development-dart-style`, `type: development`,
`status: draft`, `origin: launchpad`, audiences, evidence ledger whose first
entry is the commit citation for the recorded revision.

Done-when: every substantive claim in the body has a matching ledger entry, and
no ledger entry backs a claim the body does not make.

## STEP 4 — validate

Run `python3 launchpad/project-intelligence/corpus/validate.py`. Done-when: exit
status 0. `UNVERIFIED` notices are acceptable; errors are not.

## STEP 5 — earn the gate and commit

Run `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
-p "test_*.py"` as its own command, confirm `OK`, then `git add` and
`git commit -s` in a separate call. Done-when: one commit exists carrying
exactly the plan file and the new node.

## PARALLEL

Steps 1 and 2 overlap: the schema read and the source reads are independent.
Everything from step 3 on is strictly sequential.

## GATES

| Gate | Command | Blocking |
|---|---|---|
| Corpus schema + citation validation | `python3 launchpad/project-intelligence/corpus/validate.py` | yes |
| Commit gate test suite | `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` | yes |
| File-size ceiling (1000 lines) | `node mobile/scripts/check-file-sizes.mjs` covers `mobile/lib` only; this node is Markdown under `launchpad/`, so no rule matches it | no |

## BUDGET

Two files changed: the new node and this plan. No source, config, workflow or
generated index is touched. No push, no PR.

## OPEN

- **Relationship edges.** `development-hermit` and `development-prerequisites`
  resolve on `origin/launchpad`, so an edge is *possible*. Whether this node
  should carry one is not settled by any standard; the plan is to declare none
  and name the siblings in prose, stating the real reason rather than the false
  "nothing to point at".
- **Id convention.** `standards/naming.md` MUST 3 prescribes a `corpus-` prefix;
  corpus-wide practice for content nodes does not use one, and the two merged
  siblings in this Feature are `development-hermit` /
  `development-prerequisites`. The plan follows practice and records the tension
  in the report rather than filing an issue.

## LEFT OUT

- Any second hand-authored corpus document.
- Editing `mobile/analysis_options.yaml`, the Justfile, lefthook or CI to make a
  documented convention machine-enforced. Documenting that a convention is
  review-enforced rather than tool-enforced is in scope; changing that fact is
  not.
- Desktop/web TypeScript style, Rust style, and mobile testing conventions —
  different subjects, different nodes.
- Running `flutter analyze` or `flutter test`. The node describes what the gates
  are, not what they currently report; the Flutter SDK is Hermit-pinned and
  running it is unnecessary to read the configuration that defines the rules.

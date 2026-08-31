# Plan: issue #1260 — platforms/mobile/release-candidate corpus node

## ALREADY TRUE

- `launchpad/docs/corpus/platforms/` does not exist yet on `origin/launchpad`
  (`131b02f989684117d9ab1dd426f1673fa638e523`) — this is the first node under
  `platforms/**`.
- `node.schema.json` requires `id`, `type`, `status`, `origin`, `audiences`,
  `evidence`; `type` enum includes `platforms`; `relationships` is optional
  and every target must resolve on the branch being merged into.
- `launchpad/docs/corpus/templates/component.md` (merged) is the closest
  template match — its Required sections (Responsibility, Public interface,
  Dependencies both directions, Boundary, Relationships, Scope and omissions)
  map directly onto issue #1260's DoD bullets ("states responsibility and
  well-defined interface/boundary", "names dependencies and collaborators",
  "links source implementation and tests", "explains only component-level
  behavior, not the entire containing platform"). That template itself
  prescribes `type: implementation`, but per orchestrator guidance sibling
  nodes under `platforms/**` in this Feature use `type: platforms` instead —
  an inference since no platforms-specific template exists yet.
- The real mobile release-candidate process is implemented by:
  `scripts/mobile-release.sh` (operator entry point), `scripts/release-rulesets.sh`
  (`require_canonical_repository`), `.github/workflows/mobile-release-candidate.yml`
  (App-backed dispatch target), `scripts/publish-mobile-release-candidate.sh`
  (the actual tag-publishing logic run inside that workflow), and is documented
  in `RELEASING.md`'s Mobile sections. Tests:
  `scripts/test-mobile-release-contract.sh`,
  `scripts/test-mobile-release-candidate-publisher.sh`, both wired into
  `.github/workflows/ci.yml`'s `mobile` changed-paths lane. All landed in one
  commit, `21573b6cb chore(mobile): lighter-weight release process (#2144)`.

## STEP 1 — Confirm scope and template fit

Read `node.schema.json`, `AGENTS.md`, `templates/component.md`,
`templates/architecture-component.md`, and confirm no
`platforms/mobile/release-candidate.md` exists yet. Done when the component
template's required sections are mapped 1:1 against issue #1260's DoD.

## STEP 2 — Gather evidence from the real implementation

Read `scripts/mobile-release.sh`, `scripts/publish-mobile-release-candidate.sh`,
`scripts/release-rulesets.sh`, `.github/workflows/mobile-release-candidate.yml`,
`RELEASING.md` (Mobile section, Prerequisites, Troubleshooting), the two test
scripts, and `.github/workflows/ci.yml`'s mobile lane. Done when every claim
the document will make has an opened, citable source.

## STEP 3 — Draft the node

Write `launchpad/docs/corpus/platforms/mobile/release-candidate.md` with
front matter (`id: platforms-mobile-release-candidate`, `type: platforms`,
`status: draft`, `origin: launchpad`, `audiences`) and a body covering:
responsibility (publish an immutable `mobile-vX.Y.Z-rc.N` tag from the exact
current `origin/main` commit), public interface (the `candidate` subcommand
and its arguments/exit behavior), dependencies in both directions
(`buzz-release-bot` App, Release tag ruleset 14378754, `mobile-release-candidate.yml`
workflow / depended on by the private Buildkite mobile pipeline and
`RELEASING.md`'s documented operator flow), boundary (not the build/sign/promote
steps, not desktop/relay release lanes, not the mobile app's own runtime
architecture), and scope-and-omissions. Done when every DoD bullet is
addressed and every evidence entry cites an opened file.

## STEP 4 — Validate and commit

Run the corpus unit tests, run `validate.py` with and without the new file to
confirm zero new FAILs, then commit both the node and this plan in the exact
two-call sequence the task specifies. Done when the commit lands with a
verification stamp (or BLOCKED is reported per finding #5).

## STEP 5 — Verify

Re-read the diff against the DoD checklist and re-open every cited file/line
to confirm the citations are accurate. Done when this plan's own checklist is
satisfied.

## GATES

- `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"` → `OK`.
- `python3 launchpad/project-intelligence/corpus/validate.py` produces the
  identical pre-existing FAIL set with the new file present vs. removed (zero
  new FAILs attributable to this node).
- Every evidence citation resolves to a real file opened during drafting;
  line-range citations use `path:A-B` form.
- No `relationships` target declared unless confirmed to resolve on
  `origin/launchpad` (expected: none, since `platforms/` does not exist there
  yet).

## OPEN

- Whether a future `platforms`-type template will formalize the section shape
  used here (borrowed from `component.md`) is not this task's decision.
- Whether other in-flight `platforms/**` siblings in this Feature will
  converge on identical section headings is unknown until they merge.

## LEFT OUT

- The desktop and relay release lanes (separate DoD scope, separate tasks).
- The private Buildkite `buzz-mobile-releases` pipeline's internal build/sign
  steps — out of reach of this OSS repository and out of scope per the
  issue's "Out of scope" list.
- Any runtime behavior change to `scripts/mobile-release.sh` or its
  workflow — this is a documentation-only node.

Issue #622 — task: implement the corpus metadata schema and relationship enums
Stated size: none given (no `Size` line/label) → asked Serina; she chose 30–60 minutes → cap: 8 steps

ALREADY TRUE  (verified against git, not notes)
  launchpad/docs/corpus/ does not exist yet — this task is greenfield, nothing to avoid re-doing.
  ADR-0028 (launchpad/decisions/ADR-0028-corpus-canonical-representation.md, on origin/docs/adr-603-corpus-representation,
    status: Accepted, not yet merged to launchpad) decides Markdown+YAML-frontmatter is the one canonical
    corpus representation; frontmatter carries stable ID, provenance, typed relationships, status,
    "and whatever other schema fields #605 defines" — this schema is that definition.
  ADR-0029 (launchpad/decisions/ADR-0029-corpus-evidence-precedence.md, on origin/docs/adr-604-corpus-evidence-precedence,
    status: Accepted, not yet merged) decides evidence precedence is contextual by claim type and escalates
    to a human on real conflict, leaving affected nodes "unestablished/flagged" — the schema must be able to
    represent that flagged state, not just a clean pass/fail.
  launchpad/project-intelligence/CONTRACT.md:26-28 and memory.py:82-83 define the FACT / INFERENCE /
    TEAM_KNOWLEDGE claim classes and their enforced companion fields — verified against the code, not just
    the prose table: **evidence is required for both FACT and INFERENCE** (memory.py raises if either lacks
    it), confidence is required additionally for INFERENCE, and provided_by for TEAM_KNOWLEDGE. Reuse this
    classification rather than inventing a new one.
  ADR-0003 (launchpad/decisions/ADR-0003-handbook-page-provenance-contract.md) is a sibling frontmatter
    contract for a different corpus (the handbook) — same shape family (frontmatter + per-claim origin),
    useful precedent, not something this schema extends or is bound by.
  Parent PRD #602's own success criteria describe "a documentation standard, machine-readable schema and
    deterministic validator" as three separate artifacts — the standard doc and the validator are not
    this issue's job (validator is #623; standard/AGENTS.md is #636/#639, both declared as depending on
    #622's schema existing first).
  No existing JSON Schema tooling exists in launchpad/ yet. launchpad/project-intelligence/ is the closest
    precedent for Python test conventions in this tree, and its convention is stdlib `unittest`
    (`python3 -m unittest test_module`), NOT pytest — pytest is not installed anywhere in this environment
    and no launchpad/ requirements file names it; verified with `python3 -c "import pytest"` (ModuleNotFoundError).
    `jsonschema` (4.10.3) is importable here but is likewise undeclared in any launchpad/ requirements file.
  .github/workflows/launchpad-agents-tests.yml is the established pattern for wiring a new launchpad/ Python
    test directory into CI: path-triggered on pull_request + push to launchpad, pip-installs a
    requirements.txt, then a "confirm test cases were discovered" guard (counts cases via
    `unittest.defaultTestLoader.discover(...).countTestCases()`, fails the job on zero — a file-counting
    guard was tried first and missed a rename-every-method regression) before running the suite. Its own
    header documents that the identical "tests exist but nothing in CI runs them" defect was found twice
    independently on #260 and #262 before this workflow closed it, and CONTRACT.md §7 discloses the same
    gap is still open elsewhere in this repo (307 tests behind that interface, none run in CI, #270) — this
    plan does not want to be the third instance.

STEP 1  Write launchpad/docs/corpus/schema/node.schema.json (JSON Schema, draft 2020-12).       [independent]
        Encode the required identity, type, status, origin, audiences, and provenance/evidence fields.
        Type/status/origin are closed enums. Provenance/evidence entries reuse CONTRACT.md's FACT/
        INFERENCE/TEAM_KNOWLEDGE classes: evidence is required for FACT **and** INFERENCE, confidence is
        required additionally for INFERENCE, provided_by for TEAM_KNOWLEDGE — plus a flagged/unestablished
        status value per ADR-0029.
        done when: file exists and
        `python3 -c "import json,jsonschema;jsonschema.Draft202012Validator.check_schema(json.load(open('launchpad/docs/corpus/schema/node.schema.json')))"`
        exits 0.

STEP 2  Write launchpad/docs/corpus/schema/relationships.schema.json.                                [needs 1]
        Define the finite relationship-type enum. Each relationship type states its directionality (what
        source→target means) and whether its inverse edge is authored or generated.
        done when: file exists, passes the same jsonschema.check_schema command as step 1, and every
        relationship enum member has both a directionality and an inverse (authored|generated) descriptor.

STEP 3  Add one valid fixture and a passing test.                                     [needs 1, 2]  ← RUNS HERE
        launchpad/docs/corpus/schema/fixtures/valid/node-minimal.md — one valid corpus node fixture,
        Markdown with YAML frontmatter per ADR-0028 — plus a stdlib-`unittest` test
        (launchpad/docs/corpus/schema/tests/test_schema.py) that parses its frontmatter and validates it
        against node.schema.json + relationships.schema.json.
        done when: `python3 -m unittest launchpad.docs.corpus.schema.tests.test_schema -v` (or
        `python3 -m unittest discover -s launchpad/docs/corpus/schema/tests -p "test_*.py"`) passes with
        the valid-fixture case present and green.

STEP 4  Add one invalid fixture per failure class, each with a rejecting test.                     [needs 3]
        Under fixtures/invalid/: missing identity, unknown type, unknown status, unknown origin, missing
        audiences, missing evidence for a FACT claim, **missing evidence for an INFERENCE claim**, unknown
        relationship type, wrong-direction relationship. Pair each with a test asserting schema validation
        rejects it and names why.
        done when: the same unittest invocation as step 3 passes with one named test per listed failure
        class (9 classes, none skipped).

STEP 5  Wire the new test suite into CI and declare its one new dependency.                       [needs 4]
        Add .github/workflows/launchpad-corpus-schema-tests.yml mirroring launchpad-agents-tests.yml's
        pattern exactly: path-triggered on launchpad/docs/corpus/schema/** (pull_request + push to
        launchpad), pip-installs a new launchpad/docs/corpus/schema/requirements.txt declaring `jsonschema`
        (pinned the way launchpad/agents/requirements.txt pins ruamel.yaml, with a reason comment), a
        "confirm test cases were discovered" guard using
        `unittest.defaultTestLoader.discover(...).countTestCases()` that fails the job on zero, then runs
        the suite. This closes the exact gap named in ALREADY TRUE: a test suite nothing in CI runs is a
        claim, not a check.
        done when: the workflow file exists with the path trigger above, `requirements.txt` names
        `jsonschema`, and running the discovery-guard command from the workflow locally
        (`python3 -c "import unittest; s=unittest.defaultTestLoader.discover('launchpad/docs/corpus/schema/tests', pattern='test_*.py'); print(s.countTestCases()); import sys; sys.exit(1 if s.countTestCases()==0 else 0)"`)
        prints a nonzero count and exits 0.

STEP 6  Write launchpad/docs/corpus/schema/README.md.                                           [needs 4, 5]
        Document every field, both enum files, and the fixtures directory — the reference point #636/#639's
        corpus documentation standard will link to.
        done when: README.md exists and every top-level node.schema.json field name appears in it followed
        by a one-line description (not merely present as a bare substring — a field name pasted only inside
        a raw JSON dump does not satisfy this).

STEP 7  Write launchpad/docs/corpus/schema/COMPATIBILITY.md.                                       [needs 6]
        Record this as schema v1 and state the compatibility rule: any future field/enum removal or
        type-narrowing is breaking and requires a dated compatibility note here plus a re-validation pass
        of existing corpus nodes before merge.
        done when: COMPATIBILITY.md exists with a "v1 — initial" entry and the compatibility rule text.

PARALLEL  Only step 1 has no dependency. Steps 2-7 each consume a file (or field list, or test suite) their
          predecessor produced in the same small directory tree, so this plan is effectively sequential —
          there is no genuine second independent branch to fan out to a second subagent.
GATES     review-code and review-tests apply, after step 7 (schema + Python fixtures/tests + CI workflow
          all read as code). review-adjudicate runs after those two. review-final runs once before merge,
          per this repo's standing pre-push review-gate convention. review-a11y: not applicable, no UI
          surface. qa explore mode: not applicable — no runtime or interactive interface; the schema is
          exercised through unittest, not something to click through.
BUDGET    Step 4 — enumerating every distinct failure class and getting each invalid fixture to fail for
          its intended reason (not a different, accidental one) is the fiddliest part of this plan.
OPEN      DoD line "Schema files ... are referenced by the documentation standard" cannot be fully closed
          by #622 alone: the standard doc is #636/#639's, and both are declared as depending on #622
          existing first. This plan produces a README.md ready to be linked but the actual backlink from
          the standard doc happens in that later issue — flag this on the DoD checkbox rather than
          claiming it closed.
          "Audiences" is treated as a non-empty array drawn from a small closed enum; the issue does not
          say whether it should be a closed enum or free-text tags — flagged as a design choice, not an
          unambiguous read.
          Whether claim classification (FACT/INFERENCE/TEAM_KNOWLEDGE) applies per-node or per-claim-
          within-a-node is explicitly left open by ADR-0028 itself ("exactly the corpus-shape question
          CONTRACT.md §9.1 leaves open — it is #605's to decide"). This plan defaults to per-evidence-entry
          classification (the node's evidence array carries the class per entry) since the DoD's "provenance/
          evidence... fields" reads as plural/per-entry — flagged as a design choice.
LEFT OUT  The deterministic validator CLI/tool itself — #623's job.
          Authoring the full corpus documentation standard, AGENTS.md, or README.md — #636/#639's job.
          Any actual corpus content nodes — out of scope per the issue's own "Out of scope" section.

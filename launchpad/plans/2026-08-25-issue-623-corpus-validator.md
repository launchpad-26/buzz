Issue #623 — task: implement deterministic corpus validation and CI entry point
Stated size: none given (no `Size` line/label) → asked Serina; she chose 30–60 minutes → cap: 8 steps

ALREADY TRUE  (verified against git, not notes)
  #622 is merged (a1d997578, PR #1416): launchpad/docs/corpus/schema/node.schema.json and
    relationships.schema.json exist and are the schema this validator enforces — reused
    directly, not reimplemented. Their inlined-relationship-$defs design (no cross-file
    $ref) means a plain jsonschema.validate() call works with no custom resolver.
  ADR-0028 and ADR-0029 are both merged to launchpad (d29d08ec6, ce9da16b8) — no longer
    "Accepted but unmerged" as they were during #622's planning.
  launchpad/docs/corpus/ contains only schema/ today, and schema/ itself is NOT empty:
    it holds 24 .md files (verified: README.md and COMPATIBILITY.md, both plain prose
    with no frontmatter; 2 valid + 20 deliberately-invalid schema-test fixtures under
    fixtures/). None of these are real corpus content nodes -- they are #622's own
    schema-testing infrastructure. An independent review-plan pass caught that this
    plan's first draft did not exclude schema/ from the validator's scan, which would
    have crashed STEP 1 (no-frontmatter parse failure) and broken STEP 6/7's own
    done-when (20 fixtures are invalid on purpose) on the very first real run. STEP 1
    now excludes launchpad/docs/corpus/schema/ explicitly, by name -- it is
    infrastructure the corpus schema itself depends on, not content governed by it, the
    same way a JSON-Schema repository's own schema/ folder is not data the schema
    validates. With that exclusion, a scan of the real corpus root today finds zero real
    nodes and passes cleanly; that is not "missing input" (see STEP 5).
  launchpad/project-intelligence/ has no requirements.txt, no CI workflow, and does not
    import jsonschema or yaml anywhere yet — this task's new dependency needs its own
    manifest and CI wiring, the same gap #622 closed for launchpad/docs/corpus/schema/.
    (Project-intelligence's own 15+ existing test_*.py files also have no CI workflow —
    a real, pre-existing gap, but not this issue's to fix; out of scope.)
  launchpad/project-intelligence/CONTRACT.md and memory.py define the FACT/INFERENCE/
    TEAM_KNOWLEDGE classification #622's schema already encodes structurally — this
    validator does not re-derive it, only enforces what the schema already states.
  No launchpad/project-intelligence/corpus/ directory exists yet — greenfield, matches
    the issue's own stated impacted components.

STEP 1  Write launchpad/project-intelligence/corpus/validate.py's core.        [independent]  ← RUNS HERE
        Given a corpus root path, recursively load every *.md file EXCEPT anything under
        a top-level `schema/` directory (that subtree is #622's schema-testing
        infrastructure, not corpus content -- see ALREADY TRUE), parse its YAML
        frontmatter (same `---\n`-delimited parsing #622's test_schema.py uses), and
        validate each against node.schema.json (which already covers relationships
        structurally via its inlined $defs). Add
        launchpad/project-intelligence/corpus/tests/fixtures/valid/ and .../invalid/ (a
        small fixture corpus tree, distinct from #622's schema fixtures -- this
        validator's tests never point at the real launchpad/docs/corpus/ root).
        done when: `python3 launchpad/project-intelligence/corpus/validate.py --root
        launchpad/project-intelligence/corpus/tests/fixtures/valid` exits 0, and the same
        command against `.../fixtures/invalid` exits non-zero and names the failing
        node's id in its output.

STEP 2  Add cross-node checks: duplicate IDs and unresolved relationship targets.  [needs 1]
        After loading all nodes (step 1), check every `id` is unique across the corpus,
        and every `relationships[].target` matches some loaded node's `id`. Add one
        invalid fixture per class (two node files sharing an id; a relationship target
        naming an id nothing in the fixture set has) with tests asserting each is
        rejected and the error names the offending id.
        done when: `python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests
        -p "test_*.py"` passes, including one named test per class.

STEP 3  Add reference-existence and prohibited-content checks.                   [needs 1]
        Repo root is determined once via `git rev-parse --show-toplevel` from the
        corpus root's own location, never the process's raw cwd (this repo's own
        documented worktree cwd-scoping gotcha -- AGENTS.md's "Common Gotchas" #4 -- is
        exactly the failure mode of trusting cwd instead).

        Every `evidence[].evidence[]` citation starting with `http://` or `https://` is
        accepted as-is (ADR-0003's citation convention is a commit-pinned markdown
        link -- a URL -- not a bare commit hash; this validator does not invent a third
        "bare SHA" category, and a bare hash that isn't a URL is correctly treated as the
        next case and rejected as a non-existent path, since it isn't an ADR-0003-
        compliant citation either way). Everything else must resolve to a real file
        relative to that repo root — "invalid source paths" from #602/#636/#639's own DoD
        language.

        > **SUPERSEDED during review, kept for the record.** "Accepted as-is" was wrong
        > in both directions and this plan's own reasoning is where the error entered.
        > ADR-0003 does not merely *use* URLs, it requires the full commit SHA and
        > forbids `blob/main`, so accepting every URL unchecked let mutable evidence pass
        > a green run — the failure mode provenance exists to prevent. And "everything
        > else must resolve to a real file" ignored CONTRACT.md section 3, which
        > enumerates six citation forms, only three of them openable paths. As built,
        > citations are parsed by form first: repository file links must be
        > commit-pinned, repo-relative paths must resolve to a real file *inside* the
        > repository, and the unopenable forms are reported through a non-fatal
        > UNVERIFIED channel rather than misreported as missing files. A cross-model
        > review panel and a later cross-model review-final pass found these between
        > them; see the fix-round commits on this branch.

        Separately, reject any citation matching a SHORT, EXACT list of credential-shaped
        filenames/extensions — exact basename `.env` or matching `.env.*`, basename
        matching `id_rsa*` or `id_ed25519*`, extension `.pem` or `.key`, or a path
        segment exactly `.ssh` — deliberately NOT the broader substring words
        (`*auth*`/`*token*`/`*secret*`/`*credential*`) an earlier draft of this plan
        proposed: `*auth*` alone would reject `crates/buzz-auth/...`, a real, ordinary,
        non-secret crate this repo publicly ships (AGENTS.md's own crate table), which an
        independent review-plan pass caught. Short substring wildcards over legitimate
        source paths are exactly the "match on exact names, never sweep with a wildcard"
        mistake this session's own credential-handling rule warns about -- applying it
        here without narrowing would have reproduced that mistake one layer down. When
        rejecting either class, name the failing node's id WITHOUT echoing the offending
        path or value in the error message — the DoD's own "without leaking private
        source content" line, taken literally: the error must not re-print what it is
        refusing to print.
        done when: the same unittest invocation as step 2 passes, with a named test per
        class -- including one asserting a citation of `crates/buzz-auth/src/lib.rs` (or
        an equivalent real, ordinary path containing "auth") is accepted, not rejected --
        and the prohibited-content test asserts the matched path/value string itself does
        NOT appear anywhere in the captured error output.

STEP 4  Add the generated/manual ownership check.                                [needs 1]
        Within the same scan STEP 1 already scopes (corpus root, excluding schema/ --
        without that exclusion this check would flag node.schema.json,
        relationships.schema.json, requirements.txt and test_schema.py themselves, an
        independent review-plan pass's second Blocker), any file that is not `*.md` (e.g.
        a stray `.json` index) is flagged unless it lives under a `generated/`
        subdirectory — ADR-0028's canonical-vs-generated boundary, enforced as:
        hand-authored content is Markdown+frontmatter, anything else in the tree must be
        clearly segregated as a generated projection, never interleaved. Add one fixture
        (a `.json` file sitting directly beside `.md` nodes, outside `generated/`) with a
        test asserting rejection.
        done when: the same unittest invocation as step 2 passes, with a named test for
        this class.

STEP 5  Add the fail-closed missing-input behavior.                              [needs 1]
        Running the validator against a corpus root path that does not exist at all must
        exit non-zero naming the missing path — never silently pass. Running it against a
        root that exists but contains zero `.md` nodes (today's real state of
        launchpad/docs/corpus/, per ALREADY TRUE) must exit 0 — an empty, not-yet-authored
        corpus is a true state, not a missing input, and treating it as failure would make
        this validator permanently red until #636/#639 land content. This distinction is
        this plan's own reading of the DoD's "missing expected input reports failure,
        never PASS" line, which the issue itself does not disambiguate between "the root
        path is wrong" and "the root is empty" — flagged here rather than picked silently.
        done when: the same unittest invocation as step 2 passes, with a named test for
        each of the two cases above.

STEP 6  Add the CLI entry point and a `just` recipe.                        [needs 2,3,4,5]
        `python3 launchpad/project-intelligence/corpus/validate.py` with no `--root`
        defaults to `launchpad/docs/corpus`, argparse-based, proper exit codes. Add a
        `corpus-validate` recipe to the repo's `Justfile` calling it.
        done when: `just corpus-validate` runs from the repo root and exits 0 (the real
        corpus root has zero nodes today, per ALREADY TRUE, so a clean pass is the
        correct and only honest result available before #636/#639 exist).

STEP 7  Wire CI: a new workflow plus a declared dependency manifest.              [needs 6]
        Add launchpad/project-intelligence/requirements.txt declaring `jsonschema` and
        `PyYAML` (this task's first use of either in project-intelligence), and
        .github/workflows/launchpad-corpus-validate.yml mirroring
        launchpad-corpus-schema-tests.yml's pattern: path-triggered on
        launchpad/project-intelligence/corpus/** and launchpad/docs/corpus/**, a
        zero-test-case discovery guard, then the unit test suite, then `just
        corpus-validate` itself as a separate step so a real-corpus-root regression is
        caught even if the unit tests (which only ever touch fixtures) would not.
        done when: the workflow file exists with those two path triggers,
        requirements.txt names both packages, and running the workflow's constituent
        commands locally (discovery guard, unit tests, `just corpus-validate`) all
        succeed.

PARALLEL  Only step 1 has no dependency. Steps 2-5 all extend the same validate.py/
          tests/fixtures produced in step 1 -- touching the same files, so none is
          independent of step 1, and none of 2-5 can run before it. Steps 2, 3, 4 and 5
          are conceptually separate check classes over the same loaded-node data
          structure step 1 builds, but they all edit the same validate.py and the same
          test_validate.py file, so they are sequential with each other too, not fanned
          out. Step 6 needs all four check classes done so the CLI wraps a complete
          validator, not a partial one; step 7 needs step 6's just recipe to exist before
          CI can call it.
GATES     review-code and review-tests apply, after step 7 (validator + fixtures/tests +
          CI workflow all read as code). review-adjudicate runs after those two.
          review-final runs once before merge, per this repo's standing pre-push
          review-gate convention. review-a11y: not applicable, no UI surface.
          qa explore mode: applies narrowly — the CLI takes one real argument (`--root`)
          worth trying with a handful of adversarial paths (a symlink loop, a path
          containing `..`, a root that is a file not a directory) beyond what steps 1-5's
          fixtures cover; not a full interactive exploration since there is no UI, but
          there is a real argument surface to try.
BUDGET    Step 3 (reference-existence + prohibited-content, two distinct sub-checks in one
          step to fit the cap) is the step most likely to overrun — getting the "name the
          node, never echo the offending value" requirement right needs care in the error
          message construction, not just the rejection logic.
OPEN      Whether "missing expected input" (DoD) means an unreadable/nonexistent corpus
          root path, or also includes a root that exists but is empty of nodes, is not
          disambiguated by the issue. STEP 5 reads it as the former only, because the
          latter is today's real, honest state of launchpad/docs/corpus/ and treating it
          as failure would make this validator permanently red before #636/#639 exist.
          Flagged as a design choice, not an unambiguous read of the issue.
          "Generated/manual ownership" (STEP 4) has no established convention anywhere in
          this repo to reuse — this plan invents the "any non-.md file outside
          generated/" rule as the minimal enforceable reading of ADR-0028's
          canonical-vs-generated boundary. A different convention (e.g. an explicit
          frontmatter marker) is equally plausible and not something this plan can verify
          against prior art, because there is none yet.
LEFT OUT  Authoring any real corpus content under launchpad/docs/corpus/ (#636/#639's job,
          explicitly out of scope per the issue's own "Out of scope" section).
          Wiring CI for project-intelligence's existing 15+ test_*.py files unrelated to
          corpus/ — a real, pre-existing gap, but not this issue's to fix.
          Deciding unresolved ADR outcomes (none currently unresolved for this task; both
          relevant ADRs are merged, per ALREADY TRUE).

# Issue #953 — ingestion/ci.md

ALREADY TRUE: `launchpad/docs/corpus/AGENTS.md` (`corpus-agents`), `launchpad/docs/corpus/standards/evidence.md`
(`corpus-standard-evidence`), `launchpad/docs/corpus/standards/code-references.md`
(`corpus-standard-code-references`), and `launchpad/docs/corpus/standards/test-references.md`
(`corpus-standard-test-references`) are all merged on `origin/launchpad`. No `ingestion/*.md` or
sibling `agents/*.md` node under Feature #620 other than the already-merged
`agents/invariants.md` (`agents-invariants`) exists on `origin/launchpad`.
`launchpad/docs/corpus/ingestion/ci.md` does not exist yet. `.github/workflows/launchpad-corpus-validate.yml`
is the real CI workflow validating this corpus; `gh run list`/`gh run view` against it were
exercised live and confirmed working (three recent successful runs, full job/step detail
available per run).

STEP 1  Gather evidence: read `standards/evidence.md` and `standards/code-references.md` in
full (done — both already own the general tool-result/UNVERIFIED/commit-citation shapes) and
`standards/test-references.md` (done — closest analog: same "which claim is being cited"
problem for a different tool-result family). Confirm no existing node covers CI-specific
policy (grepped the corpus — none does). Collect concrete in-repo CI facts: the corpus-validate
workflow's trigger/path scoping, `gh run list`/`gh run view` output shape for a real run, and
this repo's own `retention-days` values for uploaded artifacts (`ci.yml:408` = 1 day,
`linux-canary.yml:265`/`windows-canary.yml:172`/`signed-macos-canary.yml:233` = 7 days,
`sprig.yml:106` = 30 days) plus the canary workflows' own header comments calling their
artifacts "short-lived ... for explicit testing" — the concrete, citable grounding for CI
being ephemeral in a way a committed file is not. ← RUNS HERE

STEP 2  [needs 1] Write front matter (schema-valid: id `ingestion-ci`, type `ingestion`, status
`draft`, origin `launchpad`, audiences `[agent, reviewer]`, relationships: `depends-on` →
`corpus-agents` and → `corpus-standard-evidence` (this node's core claims about tool-result/
UNVERIFIED/FACT treatment are extensions of that node's, not original), `references` →
`corpus-standard-code-references` and → `corpus-standard-test-references` (supporting-context
neighbors whose boundary this node states explicitly, not dependencies this node's own claims
would break without)) and the body, using the policy template's six required sections (Scope
and authority; MUST; SHOULD; Enforcement; Exceptions and escalation; Scope and omissions), plus
one additional non-required section naming what "CI" concretely means in this repo and which
claim a CI citation is actually making (existence-of-a-check vs. a-specific-run-occurred vs.
current-behavior-via-a-pass) — mirroring `test-references.md`'s own pattern for the parallel
problem. Core normative content: never promote a CI-result-only citation to FACT beyond
citing it (it is always UNVERIFIED, same as any tool-result/commit citation); prefer citing the
workflow file (a real, permanent repo path) over a specific run when the claim is "CI enforces
X"; when a specific run is cited, name it explicitly (full URL or `gh run view` form) and note
its non-permanence in the statement itself, since this repo's own artifact retention windows
(1–30 days) and canary workflows' own "short-lived" language are concrete evidence that CI
output here is not treated as durable.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
as the sole prior command to earn the verification stamp, confirm `OK`, then commit the plan +
document in a separate call. Per the batch's own instructions this is a build-only task: no
push, no PR.

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. Unit test
suite must report `OK`. `review-code` (or self-review, if the skill is unreachable) before
calling the work done. Cross-model final review is deferred to the batch owner, per the
dispatch brief.

BUDGET: small — one document, no code changes, evidence gathering already scoped and mostly
complete from research done before this plan was written.

OPEN: Whether GitHub's own platform-level retention window for a workflow *run's logs*
(distinct from the explicit `retention-days:` this repo sets for uploaded *artifacts*) is
documented anywhere authoritative for this org/repo was not established — no committed file
governs it, and asserting a specific number without opening a primary source would be exactly
the unsupported-claim failure `standards/evidence.md` warns against. The node states the
ephemerality claim on the concrete, verified evidence that exists (retention-days values, the
canaries' own "short-lived" language) and names the log-retention question as an explicit gap
rather than guessing at it.

LEFT OUT: No relationship to any unmerged Feature #620 sibling (none exist besides
`agents-invariants`, which is a different subject — general node-authoring invariants, not
CI-as-evidence — and is not targeted, consistent with the batch's own instruction not to
target in-flight siblings). No attempt to build or describe an ingestion *pipeline* runtime —
none exists, and Feature #620 explicitly excludes that from scope. No restatement of the
general tool-result/UNVERIFIED/commit-citation mechanics already owned by `standards/evidence.md`
and `standards/code-references.md`, or of test-flakiness handling already owned by
`standards/test-references.md` — this node links to all three rather than duplicating them.

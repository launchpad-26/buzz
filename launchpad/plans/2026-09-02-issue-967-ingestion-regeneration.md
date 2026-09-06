# Issue #967 — ingestion/regeneration.md

ALREADY TRUE: `launchpad/docs/corpus/schema/node.schema.json`, `launchpad/docs/corpus/AGENTS.md`,
`launchpad/docs/corpus/templates/policy.md`, `launchpad/docs/corpus/standards/generated-content.md`
(id `corpus-standard-generated-content`) and `launchpad/docs/corpus/agents/invariants.md` (id
`agents-invariants`) are merged on `origin/launchpad` at `aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90`
(worktree HEAD == `origin/launchpad` HEAD, confirmed by `git rev-parse`). No `ingestion/*.md`
node exists on `origin/launchpad` yet — confirmed by `git ls-tree -r --name-only origin/launchpad
-- launchpad/docs/corpus`. No corpus generator exists (`validate.py`'s `find_ownership_violations`,
read in full, rejects a non-`.md` file even inside `generated/`, "because no generator exists yet
to reproduce it from canonical Markdown"; owned by #1316). `corpus-standard-generated-content`
already comprehensively covers what "generated" means, where a non-Markdown artifact must live,
and the interim ownership-rejection rule (its own MUST 1-6) — this task's node must not duplicate
that ground.

STEP 1  Gather evidence: read `ADR-0028-corpus-canonical-representation.md` in full (done) —
its Decision section ("always reproducible from the canonical Markdown") and Security
implications section ("Generated views must not silently drop whatever security-relevant
provenance their source node carries") are this node's primary source. Read
`standards/evidence.md`'s own ledger entry restating that same ADR-0028 provenance-non-drop
requirement, and `validate.py`'s `find_ownership_violations` docstring + body (read in full) for
the real, checkable "don't hand-author in `generated/` today" behavior. Confirm relationship
targets against `origin/launchpad`: `corpus-agents`, `corpus-standard-generated-content`,
`corpus-template-policy` all present; no `ingestion/*.md` sibling exists to target. ← RUNS HERE
(evidence gathered above in this session)

STEP 2  [needs 1] Write front matter: id `ingestion-regeneration` (kebab-case, matching the
`<dir>-<subject>` convention `agents-invariants` set for this same Feature #620 batch), type
`ingestion` (per the issue's own instruction and the schema's surface-naming convention), status
`draft`, origin `launchpad`, audiences `[agent, developer, reviewer]`. Relationships: `depends-on
corpus-agents` (baseline authoring authority, same as every sibling), `depends-on
corpus-standard-generated-content` (this node's "don't hand-author in the meantime" MUST leans
entirely on that node's already-established rules rather than re-deriving them), `implements
corpus-template-policy` (this node follows the policy template's six required sections). Evidence
ledger: one FACT per claim above (ADR-0028's reproducibility + provenance-non-drop text, the
`find_ownership_violations` behavior, `standards/evidence.md`'s corroborating restatement,
`corpus-standard-generated-content`'s already-settled placement rules), plus TEAM_KNOWLEDGE
entries for #967's and #620's own stated scope/DoD.

STEP 3  [needs 2] Write the body using `templates/policy.md`'s six required sections in order
(Scope and authority / MUST / SHOULD / Enforcement / Exceptions and escalation / Scope and
omissions), title `# Policy: regeneration of generated corpus views`. Content stays narrowly
about *regeneration itself*, honestly framed as policy for a not-yet-built capability (#1316):
what triggers it (a canonical node changing — stated as this node's own INFERENCE, not
duplicated from elsewhere), what it must preserve (ADR-0028's provenance-non-drop MUST, cited
directly), and what MUST NOT happen meanwhile (hand-authoring inside `generated/` — deferred to
`corpus-standard-generated-content`'s MUST 2-4 by link, not restated). Scope-and-omissions
explicitly states no generator exists, cites #1316 as its owner, and separately lists what was
expected but could not be verified (no regeneration has ever run).

STEP 4  [needs 3] Run `python3 launchpad/project-intelligence/corpus/validate.py`; fix and
re-run until exit 0.

STEP 5  [needs 4] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
as the sole command to earn the verification stamp, confirm `OK`, then commit the plan + document
in a separate `git commit -s` call. Dispatch an independent `review-code` pass on the diff; fix
any real finding raised. Do not push, do not open a PR (per this task's own instructions).

PARALLEL: none — single file, single task.

GATES: `python3 launchpad/project-intelligence/corpus/validate.py` must exit 0. The corpus
unittest suite must report `OK`. `review-adjudicate` and any cross-model final review pass are
deferred to the batch owner — not run here; independent review is via a dispatched `review-code`
subagent instead.

BUDGET: small — one document, no code changes, evidence already gathered from ADR-0028,
`validate.py`, `standards/evidence.md`, `standards/generated-content.md`, `templates/policy.md`
and `agents/invariants.md` (the gold-standard sibling example) in this session.

OPEN: Whether "a canonical node changing" is stated as the regeneration trigger as a FACT or an
INFERENCE — decided as INFERENCE (confidence ~0.8), because no source states it as a rule in so
many words; it is reasoned from ADR-0028's "always reproducible from the canonical Markdown"
requirement, the same way this corpus's own confidence standard expects a reasoned-but-not-quoted
conclusion to be classified. Whether to also declare `references: corpus-standard-provenance` —
decided against: that node governs how a node's *own* checked-revision citation is recorded, not
what regenerating a *derived view* from a canonical node must do: a real but different subject,
so no relationship is added for it.

LEFT OUT: No restatement of `corpus-standard-generated-content`'s placement/ownership MUSTs —
linked instead, per this corpus's own D9-style non-duplication convention and per `templates/
policy.md`'s MUST P9. No description of the generator's actual implementation (crate, CLI,
config) — that is #633's and #1316's to build, not this node's to predict. No relationship to any
other Feature #620 sibling task (`agents/*.md` beyond the merged `agents-invariants`, or any other
`ingestion/*.md`) — none of them are merged on `origin/launchpad` as of this check, so none is a
legitimate relationship target.

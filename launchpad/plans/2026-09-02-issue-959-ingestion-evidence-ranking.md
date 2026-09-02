# Issue #959 — ingestion/evidence-ranking.md

ALREADY TRUE: `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` (accepted) and
`launchpad/docs/corpus/standards/evidence.md` (id `corpus-standard-evidence`, merged) both
already state normative rules on ranking conflicting evidence: ADR-0029 ranks by claim type
(behavior vs. intent/authorization) and requires escalation (`status: flagged`) when two
same-claim-type authorities disagree; `corpus-standard-evidence`'s own Scope and authority
explicitly claims "how conflicting evidence is ranked" as part of "the canonical treatment of
those subjects for the corpus," and its SHOULD 2 already states "cite the narrowest source
that actually supports the claim, and only that." `git ls-tree -r --name-only origin/launchpad
-- launchpad/docs/corpus` confirms no `ingestion/` directory exists yet on the merge target —
none of Feature #620's 32 sibling tasks (including #958, `ingestion/evidence-conflicts.md`) are
merged. `launchpad/docs/corpus/templates/policy.md` (id `corpus-template-policy`) and
`launchpad/docs/corpus/agents/invariants.md` (a landed policy-shaped instance) are both merged
and give the required six-section shape and precedent. Issue #959's own DoD literally
reproduces the policy-template's four required-content clauses (scope/authority, MUST/SHOULD
split, enforcement/exceptions, link-not-duplicate), confirming type `ingestion` + policy shape
is the right combination, not a procedure/how-to.

**The narrow, non-duplicative scope found:** neither ADR-0029 nor `corpus-standard-evidence`
covers what an ingesting agent does when it has already resolved claim type and classification
and holds **multiple candidate sources of the *same* `entry_class`, all genuinely supporting
the identical claim, with no contradiction between them** — i.e., redundancy narrowing, not
conflict resolution. ADR-0029 ranks *across* claim types and mandates escalation only for a
*contradiction* between two same-type authorities. `corpus-standard-evidence` states the
narrowing preference once, as one SHOULD line, with no MUST, no worked criterion, and no
statement of when *not* narrowing (i.e., splitting into separate entries) is itself required.
This node states that ingestion-time narrowing procedure as binding MUST/SHOULD rules, scoped
explicitly against both sources by name, and explicitly hands off actual disagreement between
sources to ADR-0029's escalation rule and to #958's future conflict-handling node (not yet
merged, so no relationship target declared) rather than restating either. Issue #620's stated
objective text ("the single canonical policy node for evidence ranking") is addressed head-on
in the node's own Scope and authority section as an overstatement to correct: this node is
explicitly *not* canonical over ranking generally — `corpus-standard-evidence` already holds
that status by its own text — and this node's authority is limited to the redundancy-narrowing
question alone.

STEP 1  Write front matter: id `corpus-ingestion-evidence-ranking` (per
`standards/naming.md` MUST 3: strip `.md`, prefix `corpus-`, insert the singular form of the
one-level-below-root subdirectory — `ingestion/evidence-ranking.md` → `corpus-ingestion-
evidence-ranking`), type `ingestion`, status `draft`, origin `launchpad`, audiences `[agent,
developer, reviewer]` (matches `corpus-standard-evidence`'s audience list for the same subject
family). `relationships`: `depends-on` → `corpus-agents` and `corpus-standard-evidence`
(both merged, both load-bearing — this node narrows what evidence.md leaves as one SHOULD
line and inherits ADR-0029's rule through it rather than re-deriving it); `implements` →
`corpus-template-policy` (merged; this is a policy-shaped instance, same relationship
`agents/invariants.md` declares toward the same target). No edge to `corpus-standard-code-
references`, `corpus-standard-confidence`, `corpus-standard-provenance`, or `corpus-standard-
atomicity` — checked each one's own Scope and authority and none claims the redundancy-
narrowing question (code-references owns citation *forms* for code; confidence owns the
`confidence` *number*; provenance owns the recorded-revision entry; atomicity owns one-node-
vs-many). No edge to #958/`evidence-conflicts` — not merged, would validate locally and hard-
error on `origin/launchpad` per `AGENTS.md` step 9's own merge-order trap. ← RUNS HERE

STEP 2  [needs 1] Write the body against `templates/policy.md`'s six required sections in
order (Scope and authority, MUST, SHOULD, Enforcement, Exceptions and escalation, Scope and
omissions). Scope and authority states the narrow subject verbatim as above, names ADR-0029
and `corpus-standard-evidence` by id/path as the sources this node depends on and does not
restate, and explicitly disclaims the "canonical for ranking generally" reading of #959's own
issue-objective text. MUST/SHOULD state the redundancy-narrowing procedure: when multiple
same-`entry_class` candidates support one claim with no contradiction among them, narrow to
the citation(s) that actually belong in the ledger per a stated test (does dropping this
citation change what the entry could support?); when narrowing is not honest (sources
partially disagree, or support different sub-claims), split per `corpus-standard-evidence`'s
own SHOULD 4 rather than force one entry. Every substantive claim about what ADR-0029 /
`corpus-standard-evidence` / the schema / `validate.py` actually say gets a ledger entry citing
the real file, opened and read in this session (already done above) — no invented citations,
no issue-to-subject mapping guesses per `AGENTS.md`'s named trap.

STEP 3  [needs 2] Run `python3 launchpad/project-intelligence/corpus/validate.py` from the
worktree root; fix whatever it names (schema shape, citation forms, relationship targets) and
re-run until exit 0.

STEP 4  [needs 3] Run the corpus unittest suite
(`python3 -m unittest discover -s launchpad/project-intelligence/corpus/tests -p "test_*.py"`)
as the sole command in its own call to earn the commit gate; confirm `OK`. Then, in a separate
call, `git commit -s` the plan and the document together.

PARALLEL: none — single file, single task, no code changes.

GATES: `validate.py` must exit 0. The unittest suite must report `OK` before committing.
`review-code` (or self-review if unreachable) runs after the commit, per the build loop; no
push, no PR — this task stops at a reviewed local commit.

BUDGET: small — one ~150-200-line document, no code changes, evidence already gathered by
reading ADR-0029, `corpus-standard-evidence`, `AGENTS.md`, `agents/invariants.md`,
`templates/policy.md`, `templates/procedure.md`, `standards/naming.md`,
`standards/atomicity.md`, `standards/provenance.md`, and `node.schema.json` in full this
session.

OPEN: none — the scope question this plan exists to answer is resolved above, not deferred.

LEFT OUT: restating ADR-0029's claim-type ranking or escalation rule (cited, not repeated);
restating `corpus-standard-evidence`'s classification rules, ledger structure, or citation-
shape tables (cited, not repeated); any treatment of genuine cross-source *contradiction* —
that is ADR-0029's existing escalation rule and #958's future subject, not narrowed here; any
relationship edge to an unmerged Feature #620 sibling.

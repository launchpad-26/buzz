---
id: governance-documentation-governance
type: governance
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90, which is both the local HEAD and origin/launchpad at authoring time."
    entry_class: FACT
    evidence:
      - "commit aef93f2c2acfe9dfe66d22d33f5abb4ac12baa90"
  - statement: "ADR-0050 makes the canonical documentation corpus the authority for cohort system knowledge, requires new canonical documentation to be authored in the corpus belonging to the system it documents, retires the handbook and forbids it receiving new canonical documentation."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0050-canonical-corpus-supersedes-handbook.md"
  - statement: "ADR-0028 makes Markdown with YAML front matter the one canonical authored representation of a corpus node, and chose that format specifically because the corpus is audited in the pull-request diff a human reads rather than after the fact."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "ADR-0029 is an accepted decision record dated 2026-08-25, decided in launchpad-26/buzz#604, and node.schema.json describes the status value 'flagged' as ADR-0029's unresolved-conflict state rather than a generic low-confidence marker."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "node.schema.json requires exactly six front-matter fields -- id, type, status, origin, audiences, evidence -- additionally permits relationships, sets additionalProperties to false, and describes the evidence array as the node's provenance ledger."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "validate.py's _load_frontmatter splits a node's text on the front-matter delimiter and binds the remainder to a variable named _body; the identifier _body appears exactly once in the whole module and the word 'body' appears nowhere else in it, so the Markdown body is discarded before any check runs."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py's only directory-keyed exclusion is EXCLUDED_TOP_LEVEL_DIRS = {\"schema\"}, so schema/ is never validated and every other directory under the corpus root is treated identically."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate_corpus composes exactly six error producers plus the per-node load-and-schema errors: find_duplicate_ids, find_unresolved_relationship_targets, find_non_finite_confidence, find_citation_problems, find_non_canonical_nodes and find_ownership_violations."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "find_citation_problems reports errors and unverified notices in two channels, and main prints unverified notices on every run while exiting 0 for them, so a PASS can coexist with citations nothing opened."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "find_ownership_violations rejects every non-.md file under the corpus root today, including one placed under generated/, because no generator exists to reproduce it from canonical Markdown."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "standards/naming.md MUST 3 requires a document's id to be the filename stem prefixed with corpus- plus, for a document one directory below the corpus root, that directory's singular form, and grounds itself in 'the two precedents this document was written against'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
  - statement: "At the recorded revision the merged corpus outside schema/ holds 205 Markdown nodes, 48 of whose ids carry the corpus- prefix; 47 of those 48 are meta documents (19 under standards/, 26 under templates/, plus AGENTS.md and README.md), leaving development/build.md as the only one of the 158 content nodes that carries the prefix naming.md MUST 3 requires of every corpus document."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/build.md"
      - "launchpad/docs/corpus/standards/naming.md"
      - "git_ls_tree(origin/launchpad, path='launchpad/docs/corpus') -> 205 .md nodes outside schema/, 48 ids prefixed corpus-, 47 of them meta documents"
  - statement: "standards/naming.md MUST 2 forbids a filename re-encoding its own directory as a prefix or suffix, and 42 of the 205 merged nodes do so anyway, including standards/documentation-standard.md, the node that states the shape of a corpus standard."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
      - "launchpad/docs/corpus/standards/documentation-standard.md"
      - "git_ls_tree(origin/launchpad, path='launchpad/docs/corpus') -> 42 of 205 node filenames repeat their parent directory name or its singular form"
  - statement: "standards/naming.md MUST 4 (exactly one level-1 heading), MUST 5 (spell the YAML block 'front matter' as two words) and MUST 6 (call the evidence array the 'provenance ledger') are all rules about a node's Markdown body, and MUST 4 states in its own text that validate.py never reads a node's body at all."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/naming.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "development/hermit.md carries a FACT-classed ledger entry stating the repository's Justfile 'contains no reference to Hermit anywhere in its text', and the Justfile contains four such references, at lines 25, 30, 32 and 57."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/development/hermit.md"
      - "Justfile"
  - statement: "standards/review-requirements.md carries nine reviewer MUSTs, states that no check in validate.py reaches any of them, and states that validate.py is not currently a required status check."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/review-requirements.md"
  - statement: "standards/documentation-standard.md scopes its D1-D10 to documents under launchpad/docs/corpus/standards/, and records that of three candidate readings of 'documentation standard' named in #1486 it carries only the meta-standard reading, the apex-charter reading having not been adopted for that node."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/documentation-standard.md"
  - statement: "templates/policy.md requires a policy-shaped node to carry six sections in a fixed relative order, requires every requirement to carry a stable identifier and to name what enforces it or state that nothing does, and requires the enforcement section to say what a passing validation run does not establish."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/templates/policy.md"
  - statement: "AGENTS.md's node-creation procedure sends the recorded revision to a commit citation in the ledger, the inspected sources to citations on the claims they support, and everything expected but unverified to the body's scope-and-omissions section, and its step 9 requires relationship targets to be resolved against the branch the change merges into."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: ".github/workflows/launchpad-corpus-validate.yml runs the corpus unit tests and then validate.py against the real corpus root, on pull_request and on push to launchpad, path-filtered to the corpus tree, the validator sources and the workflow itself, and fails the job if the suite discovers zero test cases."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
  - statement: "The corpus validator's unit suite is six modules totalling 2455 lines, of which test_validate.py alone defines 82 test functions."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/tests/test_validate.py"
      - "launchpad/project-intelligence/corpus/tests/test_evidence.py"
  - statement: "ADR-0052 supersedes ADR-0019 in full and restates two of its rulings unchanged: a required status check may only ever be a deterministic script, and enforcement of required checks stays deferred until the buzz-infrastructure #105 CI/CD pipeline programme is live, with a 2026-09-05 revisit date."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0052-delegated-authority-and-feature-batching.md"
      - "launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md"
  - statement: "The Justfile recipe corpus-validate runs python3 launchpad/project-intelligence/corpus/validate.py and nothing else."
    entry_class: FACT
    evidence:
      - "Justfile"
  - statement: "launchpad/AGENTS.md section 3 describes launchpad/docs/ as the 'MkDocs knowledge layer', and no mkdocs.yml or mkdocs.yaml file exists anywhere in the repository at the recorded revision."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
      - "find_files(patterns='mkdocs*.yml|mkdocs*.yaml', root='.') -> no matches, tracked or untracked, at the recorded revision"
  - statement: "launchpad/AGENTS.md section 5 rule 1 states that an agent may draft any issue, pull request or ADR in full but may not decide an ADR outcome, approve a pull request, merge one, or close another agent's escalation on its own judgement."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "Because validate.py discards the Markdown body before any check runs, every requirement that any corpus standard states about a node's body is held by pull-request review and by nothing else."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/standards/naming.md"
      - "launchpad/docs/corpus/standards/review-requirements.md"
    confidence: 0.95
  - statement: "The corpus's governance therefore has exactly two tiers -- a front-matter tier the schema and validator hold mechanically, and a prose tier only a human reviewer holds -- and every governance defect measured in this corpus so far sits in the second tier."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/standards/review-requirements.md"
      - "launchpad/docs/corpus/standards/naming.md"
    confidence: 0.8
  - statement: "No merged corpus node states the corpus-wide authority ordering or the machine-held/review-held boundary as its own subject: README.md owns which file owns which rule, AGENTS.md owns the create/update/retire procedures, review-requirements.md owns the reviewer's checklist, and documentation-standard.md scopes itself to the shape of a standards/ document."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/standards/review-requirements.md"
      - "launchpad/docs/corpus/standards/documentation-standard.md"
    confidence: 0.75
  - statement: "Issue #2029 records that naming.md MUST 3's corpus- prefix is omitted by 179 of 229 merged content nodes measured at a later revision, and attributes the divergence to MUST 3 generalising from a two-document sample drawn entirely from the standards/ shelf."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2029"
  - statement: "Issue #2030 records that each of the four merged nodes under launchpad/docs/corpus/development/ carries at least one FACT-classed claim that is false against the source the entry itself cites, and that corpus validation passes on all four."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#2030"
relationships:
  - type: implements
    target: corpus-template-policy
  - type: depends-on
    target: corpus-agents
  - type: references
    target: corpus-readme
  - type: references
    target: corpus-standard-review-requirements
  - type: references
    target: corpus-standard-documentation-standard
---

# Policy: how the documentation corpus is governed

This node states binding requirements about **the governance of the corpus itself** — which
authorities bind a corpus change, in what order they win, and which of their requirements
are held by a machine versus held only by a human reading a pull-request diff. It is written
for the agent authoring a node, the developer changing one, and the reviewer who is, today,
the only enforcement mechanism most of these rules have.

It states no rule about any node's *subject*. It invents no policy: everything below is
either recorded elsewhere and linked, or measured here and cited.

## Scope and authority

**This node governs** the authority ordering across the corpus's governing documents, and
the boundary between what `launchpad/project-intelligence/corpus/validate.py` mechanically
holds and what only pull-request review holds.

**Its authority is derived, not original.** It comes from three accepted decision records —
`ADR-0050` (the corpus supersedes the handbook as the authority for cohort system
knowledge), `ADR-0028` (Markdown with YAML front matter is canonical, and the pull-request
diff is the audit) and `ADR-0029` (how conflicting evidence is ranked, and the `flagged`
state) — together with `launchpad/docs/corpus/AGENTS.md`, which this corpus resolves as
governing instructions for every change beneath its root.

**Where this node and any of those disagree, they win** and this one has drifted. The same
applies to `node.schema.json` and to `validate.py`: a document describing a check is never
authority over the check. Where this node and a topic standard disagree about that
standard's own subject, **the topic standard wins**.

**Two same-claim-type authorities in conflict are not this node's to settle.** `ADR-0029`'s
escalation applies, and the node carrying the conflict takes `status: flagged`.

## For X, read Y

This node owns none of the following and restates none of them.

| For | Read |
|---|---|
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| Which file owns which rule, and what the corpus contains today | `launchpad/docs/corpus/README.md` |
| The front-matter contract — fields, enums, conditional rules | `launchpad/docs/corpus/schema/node.schema.json` |
| Those fields in prose | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| What the reviewer of a corpus change must actually do | `launchpad/docs/corpus/standards/review-requirements.md` |
| The required shape of a document under `standards/` | `launchpad/docs/corpus/standards/documentation-standard.md` |
| The required shape of a policy-shaped node such as this one | `launchpad/docs/corpus/templates/policy.md` |
| What the checker actually enforces | `launchpad/project-intelligence/corpus/validate.py` |
| Where the check runs in CI | `.github/workflows/launchpad-corpus-validate.yml` |

## The authority chain

Read top to bottom; each row is authority over every row beneath it for the subject named.

| Rank | Authority | Governs |
|---|---|---|
| 1 | `ADR-0050` | That the corpus, not the handbook, is where canonical cohort system knowledge is authored at all |
| 2 | `ADR-0028`, `ADR-0029` | The canonical representation, and how conflicting evidence is ranked |
| 3 | `launchpad/docs/corpus/schema/node.schema.json` | The front-matter contract, mechanically |
| 4 | `launchpad/project-intelligence/corpus/validate.py` | What is actually checked, mechanically — and therefore what "green" means |
| 5 | `launchpad/docs/corpus/AGENTS.md` | The create/update/retire procedures, and the evidence discipline |
| 6 | `launchpad/docs/corpus/standards/*` | Per-subject rules; the topic standard wins on its own subject |
| 7 | `launchpad/docs/corpus/templates/*` | The required shape of each kind of node |
| 8 | This node, `README.md`, and any other summary | Nothing that rows 1–7 already own |

**Rank 4 is not a typo.** `validate.py` outranks the prose documents because it is what
actually runs. A standard stating that something is enforced does not enforce it; the
distinction is this node's whole subject, and G9 below exists because it has already been
got wrong.

## MUST

Identifiers G1–G10 are this node's own and are stable once published. Each names what holds
it. "Review only" is a frequent and honest answer here — see *Enforcement* for why.

| # | Requirement | Held by |
|---|---|---|
| **G1** | New canonical cohort system knowledge MUST be authored in the corpus for the system it documents. The handbook MUST NOT receive new canonical documentation; handbook material is source material, not an authority (`ADR-0050`). | Review only |
| **G2** | A corpus node MUST be a Markdown file with YAML front matter, and MUST NOT be hand-authored in any other serialization (`ADR-0028`). | Mechanical — `find_ownership_violations` rejects every non-`.md` file under the corpus root, and a file with no leading `---` fails to load |
| **G3** | Front matter MUST satisfy `node.schema.json`, which permits exactly seven fields and rejects any eighth. | Mechanical — schema validation in `load_nodes` |
| **G4** | Every substantive claim in a node's body MUST have a corresponding entry in the node's provenance ledger, classified `FACT`, `INFERENCE` or `TEAM_KNOWLEDGE` per `AGENTS.md`'s definitions. | Review only — nothing pairs body prose with ledger entries, because the body is discarded before any check runs |
| **G5** | A node MUST NOT restate content owned by a higher rank in *The authority chain*. It links instead. A copy that goes stale stays green forever, because nothing reads it. | Review only |
| **G6** | Every `relationships[].target` MUST resolve against the branch the change merges into, not the author's worktree (`AGENTS.md` step 9). | Partial — `find_unresolved_relationship_targets` resolves targets against whatever tree the run walks; that the tree is the merge target is the author's and reviewer's to establish |
| **G7** | Where a governing document and merged practice contradict each other, the contradiction MUST be recorded and escalated, not silently resolved in either direction. Where two same-claim-type authorities conflict, the node takes `status: flagged` and a human decides (`ADR-0029`). | Review only |
| **G8** | A node's `id` MUST NOT be renamed once merged, and a retired id MUST NOT be reused. Retirement is a `status` change; deletion breaks every inbound edge. | Partial — uniqueness within one run is mechanical; permanence across runs is not, because the validator has no memory of a previous run |
| **G9** | A claim that some rule *is enforced* MUST be checked against the artefact that would enforce it — the validator, the workflow, the schema — and MUST NOT be repeated from a document that asserts it. | Review only |
| **G10** | A defect in a governing document MUST be filed as an issue against the corpus. It MUST NOT be resolved by widening or reinterpreting the rule locally so that the change in hand slips under it. | Review only |

## SHOULD

| # | Guidance |
|---|---|
| **S1** | Evidence SHOULD cite a repo-relative path rather than a GitHub link. The validator opens the former against the filesystem and reads the latter as a string, so a pinned link naming a file that never existed passes exactly as cleanly as a correct one (`AGENTS.md`, *The GitHub row is the trap*). |
| **S2** | A citation SHOULD name a bare path rather than a line or range until line bounds are verified. A position that has silently drifted is worse than no position, because it looks precise. |
| **S3** | Where a requirement could cheaply be given a mechanical holder, the change that states the requirement SHOULD propose one, or record why it did not. Every rule left to review is a rule that depends on a reviewer's attention on a particular afternoon. |
| **S4** | A new MUST SHOULD be measured against merged practice before it is written, not generalised from the nearest two examples. *Worked examples* below is what happens when it is not. |
| **S5** | A node SHOULD declare its relationships when it is authored rather than deferring them to a later pass. "There was nothing to point at" was true when the corpus held one node; at the recorded revision it holds 205, and `AGENTS.md` warns explicitly that copying that justification forward produced a false claim twice. |

## Enforcement

**One deterministic check governs the whole corpus.** `python3
launchpad/project-intelligence/corpus/validate.py`, also reachable as `just
corpus-validate`, which runs that command and nothing else. Exit 0 is a pass, exit 1 names
every failing node. `.github/workflows/launchpad-corpus-validate.yml` runs the validator's
unit suite and then the validator against the real corpus tree, on `pull_request` and on
`push` to `launchpad`, path-filtered to the corpus, the validator sources and the workflow
itself — and fails the job outright if the suite discovers zero test cases, so a vacuous
green is not available. The suite behind it is six modules and 2455 lines, `test_validate.py`
alone defining 82 test functions.

### What it holds

`validate_corpus` composes exactly six error producers plus the per-node load-and-schema
errors:

| Check | What it establishes |
|---|---|
| Front-matter load | A leading `---` delimiter, parseable YAML, a mapping at the top level, no duplicate YAML key |
| Schema validation | Every rule in `node.schema.json`, including the `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` conditional field rules |
| `find_duplicate_ids` | No two loaded nodes share an `id` |
| `find_unresolved_relationship_targets` | Every `relationships[].target` matches some loaded node's `id` |
| `find_non_finite_confidence` | `confidence` is finite — `NaN` satisfies the schema's `minimum`/`maximum` and is rejected here instead |
| `find_citation_problems` | Each citation matches a known shape; a repo-relative path resolves to a real file inside the repository; a GitHub file link is pinned to a full 40-character SHA, uses `blob` or `raw`, and names a path; no citation matches a credential-shaped pattern |
| `find_non_canonical_nodes` | No `.md` file inside the corpus resolves outside it via symlink |
| `find_ownership_violations` | No non-`.md` file exists under the corpus root at all today, `generated/` included |

Its only directory-keyed rule is `EXCLUDED_TOP_LEVEL_DIRS = {"schema"}`. Everything else
beneath the corpus root — `standards/`, `templates/`, `governance/`, `capabilities/` — is
validated identically. Those directories are conventions authors hold, not namespaces the
tooling recognises.

### What a green run does not establish

**The Markdown body is discarded before any check runs.** `_load_frontmatter` splits the
file on the front-matter delimiter and binds the remainder to `_body`; that identifier
appears exactly once in the module, and the word "body" appears nowhere else in it. Not
"not currently inspected" — discarded, for every node, in every directory.

| Not established | Consequence |
|---|---|
| That a `FACT`'s cited source supports the statement | Checking is structural. A `FACT` citing a real, unrelated file passes cleanly |
| That an `UNVERIFIED` citation was checked by anything | Those notices print on every run and are never fatal; a `PASS` line reports their count and still exits 0 |
| That a cited line number exists | The path is opened; the line is never compared against the file's length |
| That a GitHub link's file exists | The URL is read as a string; the validator never contacts GitHub |
| Anything at all about the body | The one-H1 rule, the "front matter" spelling rule and the "provenance ledger" term rule from `standards/naming.md` MUST 4, 5 and 6 are all body rules, and MUST 4 says so in its own text |
| That a relationship's declared `type` points the right way | Only that the target names a known id |
| That the node is one independently maintainable idea | Nothing mechanical can see this |
| That the run was a required status check | It is not — see below |

**It is not a required status check, by decision.** `ADR-0052` supersedes `ADR-0019` in full
and restates two rulings unchanged: a required status check may only ever be a deterministic
script, and *enforcement* of required checks stays deferred until the
`buzz-infrastructure` #105 CI/CD pipeline programme is live, with a 2026-09-05 revisit date.
So a red corpus run does not block a merge today; a reviewer noticing it is what stands in
the way.

**Enforcement is therefore the pull-request review, by design.** `ADR-0028` chose Markdown
precisely so the corpus would be audited in a diff a human reads, and named that review as
the mechanism the rest of the contract depends on.
`standards/review-requirements.md` is what that review must include; it carries nine
reviewer MUSTs and states plainly that no check in `validate.py` reaches any of them. This
node does not restate that list — it names where the boundary falls, and that document says
what to do on the far side of it.

## Worked examples: two rules review did not hold

Both are drawn from this repository, both were re-measured here rather than quoted, and both
are open issues at the recorded revision. They are cited as evidence for the two-tier
finding above, not as a survey of naming defects — `standards/naming.md` owns its own
subject and this node has no opinion on it.

**1. A MUST that 157 of 158 content nodes do not follow.** `standards/naming.md` MUST 3
requires every corpus document's `id` to carry a `corpus-` prefix. At the recorded revision
the merged corpus holds 205 nodes outside `schema/`; 48 ids carry the prefix, and 47 of
those are meta documents — the 19 under `standards/`, the 26 under `templates/`, plus
`AGENTS.md` and `README.md`. That leaves `development/build.md` as the only one of the 158
content nodes complying. MUST 3 hedges its own reach — "at the recorded revision this
means" — and grounds itself in "the two precedents this document was written against", both
of which are `standards/` documents, the one shelf where the prefix is right. Issue #2029
tracks it and reports the same divergence at 179 of 229 content nodes measured later.

`standards/naming.md` MUST 2, on the same page, forbids a filename re-encoding its own
directory. 42 of the 205 merged nodes do exactly that, among them
`standards/documentation-standard.md` — the node that states what a corpus standard must be.

**2. Four merged nodes whose `FACT` entries are false against their own citations.** Issue
#2030 records that each of the four nodes under `launchpad/docs/corpus/development/` carries
at least one `FACT`-classed claim contradicted by the source the entry itself cites, and
that corpus validation passes on all four. One was re-verified directly here rather than
taken on the issue's word: `development/hermit.md`'s ledger states that the repository's
`Justfile` "contains no reference to Hermit anywhere in its text". It contains four, at
lines 25, 30, 32 and 57.

**What these two share** is the tier they sit in. Neither is a schema violation, a broken
citation, an unresolved edge or a duplicate id — the validator is correct to pass all of
them, and would pass them again. They are exactly the class of defect G4, G5 and G9 name and
that only a reviewer opening the cited source can catch. A knowledge corpus that asserts a
false fact with a resolving citation attached is worse than one that says nothing, because
the citation is what makes the claim look checked.

## Exceptions and escalation

**There is no exemption from G1, G2, G3 or G8.** They are the corpus's identity: where
knowledge is authored, in what form, against what contract, under what permanent name. A
change that cannot meet them is a change to the decision records that set them, and that is
an ADR, not a pull-request judgement.

**G4, G5, G7, G9 and G10 have no exemption either, but they have no mechanical floor.** A
node that departs from one of them departs in the open: the pull request says which
requirement, and why, in the body section the requirement applies to. A silent departure is
indistinguishable from an oversight, which is precisely what the reviewer cannot afford.

**G6 has one recognised failure mode rather than an exception.** An edge that resolves in
the author's worktree and not on the merge target is a hard CI error, not a judgement call.
Re-resolve against the merge target before pushing.

**A `SHOULD` is departed from in the open, not waived.** S1–S5 are guidance; say which one
and why, where the reader will look for it.

**A disputed application is a judgement, not an exception.** The author records the tension
and names it in the pull request; the reviewer decides. If they do not agree, the
disagreement is filed as an issue against this node, because a rule two people read
differently is a defect in the rule.

**A rule that merged practice contradicts is escalated, never quietly reinterpreted.** File
an issue naming the rule, the practice, and the measurement that shows the gap — #2029 and
#2030 are the worked shape of that. Deciding which side wins is a human's, per
`launchpad/AGENTS.md` §5 rule 1: agents draft decisions, they do not make them.

**`status: flagged` is not the escape hatch.** It means what `ADR-0029` says it means — read
it there. It names an unresolved conflict between two same-claim-type authorities; it is not
a way to ship a requirement unmet.

**A case none of this covers** is raised as an issue against the corpus rather than settled
locally. Do not widen this node to fit the change in hand; that is the failure G10 exists to
name.

## Scope and omissions

**This node covers** the corpus's authority ordering, the boundary between mechanically-held
and review-held requirements, and how a divergence between a governing document and merged
practice is escalated.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How to create, update or retire a node | `launchpad/docs/corpus/AGENTS.md` |
| Which file owns which rule, and what the corpus holds today | `launchpad/docs/corpus/README.md` |
| The front-matter contract, and adding a value to a closed enum | `launchpad/docs/corpus/schema/node.schema.json`, `schema/COMPATIBILITY.md` |
| What a reviewer of a corpus change must actually do, clause by clause | `launchpad/docs/corpus/standards/review-requirements.md` |
| The required shape of a document under `standards/` | `launchpad/docs/corpus/standards/documentation-standard.md` |
| The required shape of each kind of node | `launchpad/docs/corpus/templates/*` |
| Naming, identifiers, linking, provenance, status, taxonomy, evidence, confidence, atomicity and the other per-subject rules | the corresponding node under `launchpad/docs/corpus/standards/` |
| How generated artifacts prove their provenance | `launchpad/docs/corpus/standards/generated-content.md`, and #1316 |
| Line numbers in citations not being verified against file length | #1459 |
| Whether `naming.md` MUST 3's `corpus-` prefix or merged practice is the rule going forward | #2029 |
| Fixing the false `FACT` entries in the four `development/` nodes | #2030 |
| Governance of documentation outside `launchpad/docs/corpus/` — `launchpad/decisions/`, `launchpad/plans/`, upstream's `docs/` | nothing in the corpus; see *not verified* below |

**It does not govern content nodes' subjects.** A capability, architecture or layers node is
bound by G1–G10 as a corpus node, and by nothing here as a description of Buzz.

**This node's own divergences, disclosed rather than hidden.** Two, both against
`standards/naming.md`, both consequences of the path and `id` this node was commissioned
with:

- Its `id`, `governance-documentation-governance`, carries no `corpus-` prefix and so fails
  MUST 3. It matches the `<directory>-<stem>` shape 157 of the 158 merged content nodes use.
  Which of the two is the rule is #2029's to settle; complying with the standard here would
  have produced an id inconsistent with every neighbouring node, and `id`s are permanent.
- Its filename, `documentation-governance.md`, re-encodes its directory `governance/` as a
  suffix and so fails MUST 2, alongside the 42 merged nodes that do the same.

**Relationships, all resolved against `origin/launchpad` at the recorded revision.**
`implements: corpus-template-policy`, because this node is a concrete instance of that
template's six-section shape, which is the schema's own worked example for that edge.
`depends-on: corpus-agents`, because this node's authority over evidence discipline is
derived from `AGENTS.md` rather than original to it. `references` toward `corpus-readme`,
`corpus-standard-review-requirements` and `corpus-standard-documentation-standard`, the three
neighbours whose boundaries this node states and whose content it deliberately does not
restate. No edge toward `standards/naming.md`: it is cited as measured evidence, not depended
on, and this node takes no position on its subject.

**Expected but not verified when this node was written:**

- **No CI run has exercised this node.** Every validator result reported here is from a
  local run in the authoring worktree.
- **Whether the CI job's checkout resolves the pull-request merge result** was not checked.
  G6's mechanical half therefore rests on `AGENTS.md` step 9 and
  `review-requirements.md` MUST 5, both of which assign the merge-target check to a human,
  rather than on any claim about what the workflow's checkout produces.
- **No `mkdocs.yml` or `mkdocs.yaml` exists anywhere in the repository**, although
  `launchpad/AGENTS.md` §3 describes `launchpad/docs/` as the "MkDocs knowledge layer".
  Whether a site build is planned, abandoned, or lives in another repository was not
  established, so no claim is made here about how the corpus is published for reading.
- **Whether required status checks have been configured since `ADR-0052`** was not checked
  against the live repository settings. The deferral above is quoted from the accepted
  record, not measured against GitHub, and that record sets its own revisit date of
  2026-09-05.
- **Issues #2029 and #2030 were read and are open**, but their own measurements were taken
  at a revision this node did not reproduce in full. The counts stated in *Worked examples*
  are this node's own, taken at the recorded revision; where they differ from the issues',
  both are reported rather than reconciled.
- **Whether `governance/` becomes the home for further policy nodes** is not settled here.
  This node creates the directory; the corpus has no rule assigning meaning to a top-level
  directory name, and `validate.py` treats them all alike.

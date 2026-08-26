---
id: corpus-standard-evidence
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109."
    entry_class: FACT
    evidence:
      - "commit ebe2daf721c7d7a96fdd84eba0a0a5d37eefa109"
  - statement: "A node's evidence array is its provenance ledger: the schema requires the array, requires at least one entry in it, and defines no other field anywhere in a node in which a citation or a classification may live."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every entry carries a statement and an entry_class, and the class chosen decides which of evidence, confidence and provided_by the schema then requires and which it forbids, a matrix node.schema.json encodes and the schema README explains in prose."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/schema/README.md"
  - statement: "FACT and INFERENCE each require at least one citation, while TEAM_KNOWLEDGE requires none and is permitted to carry them without being required to."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/memory.py"
  - statement: "The same three-class contract is enforced a second time and independently by memory.py's __post_init__, which validate.py never imports, so the two are parallel enforcement paths rather than one calling the other."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/memory.py"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "In memory.py's store, live repository evidence contradicting a FACT or an INFERENCE supersedes it with a new FACT entry, while the same code-only observation never supersedes a TEAM_KNOWLEDGE entry -- only a later explicit statement from a person can retire one."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/memory.py"
  - statement: "The corpus node schema defines no supersession or temporal fields on an evidence entry, so a corpus ledger records claims and not their history."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Citation checking is structural: the validator confirms that a cited repository path resolves to a real file inside the repository and never opens that file, so a FACT citing a real file that says nothing on its subject passes with no notice at all."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The commit, graph-edge and tool-result citation forms are reported on a non-fatal UNVERIFIED channel that always prints and never changes the exit status."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A commit citation is never checked against the repository's object store and never compared against HEAD, so a commit id that exists and one that does not are both reported UNVERIFIED and are indistinguishable in the output."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation matching no recognised form is a hard error rather than an UNVERIFIED notice."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Nothing limits a node to one commit-only FACT: a second, third or tenth produces only further non-fatal notices and the run still exits 0."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "CONTRACT.md section 3 enumerates six citation shapes -- file range, file line, bare path, graph edge, tool result and commit -- and contains no URL form at all."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "A URL the validator's repository-link pattern does not match, including a GitHub issue or pull-request URL and any non-GitHub URL, is reported UNVERIFIED."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A URL matching the validator's repository-link pattern is accepted only as a blob or raw view whose ref is forty lowercase hexadecimal characters and whose path segment is non-empty; the check is on the URL's shape alone, so a link naming an owner, repository and file that do not exist is accepted."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "A repository link whose ref is not forty lowercase hexadecimal characters, including an uppercase full SHA, and one whose view verb is tree, blame, commits or edit rather than blob or raw, and one that is pinned but carries no path segment, are each a hard error rather than an UNVERIFIED notice."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "validate.py implements a URL branch that CONTRACT.md section 3 does not describe, while its own module docstring says citations are parsed against section 3's six forms."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md states that CONTRACT.md section 3 enumerates six shapes and contains no URL form, that its own table is seven rows because it adds two URL forms section 3 does not enumerate, and that the table is therefore not a summary of section 3; it also records that an earlier version of that sentence claimed otherwise and that an agent authoring a sibling node built a scope argument on the miscount."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "AGENTS.md states that its citation-shape table is provisional reference material that belongs in the evidence standard once that standard lands."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "AGENTS.md states that TEAM_KNOWLEDGE is not a place to park a decision the author made themselves, and that attributing an extrapolation to the thing it started from does not make it something the author was told."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "ADR-0029 ranks evidence contextually by claim type, rejecting both a single fixed hierarchy applied to every claim and a latest-timestamp-wins rule, and holds that GitHub history, team knowledge and inference are never treated as fact on their own but stay attributed to their source."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "ADR-0029 requires a node whose two same-claim-type authoritative sources contradict each other to be left unestablished and flagged for a human rather than resolved by its author, and node.schema.json provides flagged as a status value for exactly that state, describing it as naming an unresolved conflict rather than simple low confidence."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "ADR-0028 requires claim classification to stay structurally encoded and validator-checkable rather than asserted only in free-form body prose, requires that generated views must not silently drop security-relevant provenance their source node carries, and leaves the question of how many claims one node holds open."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "ADR-0029 requires that private evidence must not be copied into the public corpus to resolve a conflict, and that where evidence cannot be published the claim stays unestablished rather than being asserted from a source that cannot be shown."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "COMPATIBILITY.md governs changes to the node and relationship schemas, treating any change that removes a field, removes an enum value or narrows a type as breaking and requiring a dated entry plus a re-validation pass of every existing node in the same pull request."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "The schema constrains provided_by only to a non-empty string and status only to membership of its enum, so neither whether an attribution names a real source nor whether a flagged state was warranted is checkable."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "No corpus generator exists yet, so no generated view can be regenerated from a node and compared against it."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md records that generated-artifact provenance is #1316's, encoding ADR-0029's claim-type classification is #1410's, the human-facing entry point is #639's, the unchecked line-number bound is #1459's, and whether a recorded revision may stay put across edits is #1321's."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Whether ADR-0003's markdown-link wrapper should be required on corpus evidence is #605's contract to decide and is deliberately not enforced by the validator."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The validator never reads a node's body, so a body claim carrying no ledger entry, and a ledger entry supporting no body claim, are both invisible to every check that exists."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The same validator command that runs locally runs in CI on every pull request and every push to the launchpad branch that touches the corpus root, so a local failure is a CI failure, and the just recipe wrapping it invokes exactly that command while needing the Hermit environment activated first."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
      - "launchpad/project-intelligence/corpus/validate.py"
      - "Justfile"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "On issue #636 an authored policy claim was classified INFERENCE citing a schema silent on the subject, reclassified TEAM_KNOWLEDGE attributed to an issue's definition of done, and refused in both forms by three successive cross-model review passes on the same condition, and the accepted fix was for the document to stop making the claim rather than to relabel it again."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#636, recorded in the message of commit a1e8bbcd0846321c6f6684acfe551096da4d974a"
  - statement: "The issue raising the ownership overlap delegates the choice, stating that whichever way #1314 decides, the two documents should end up with one owner for the class rules, and it records that the code-references node declares no relationships so nothing links the two."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1476, Expected and Risk sections"
  - statement: "The code-references standard's own section 1 allocates the forms that name tool output rather than code -- graph edges and tool results -- to the evidence standard, and keeps the code-naming forms itself."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1476, quoting launchpad/docs/corpus/standards/code-references.md section 1"
  - statement: "The code-references standard states normative rules about when a claim may carry the class FACT and about how many commit-only FACTs a node may hold, while declaring that classification belongs to this node, and the open question of which of the two owns those rules is filed as an issue asking whichever claims the subject to leave the other an explicit marker."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1476 'task: settle whether code-references or evidence (#1314) owns the FACT and ledger-composition rules'"
  - statement: "The confidence standard owns what an INFERENCE's confidence value means and how to choose one, the code-references standard owns the citation forms that name code, and the divergence between CONTRACT.md, AGENTS.md and validate.py on the citation forms is filed separately."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1309, #1308 and #1478 -- the issues that define each subject"
  - statement: "An earlier revision of this node's own ledger asserted that AGENTS.md introduces its citation table as CONTRACT.md's shapes, which is the claim AGENTS.md disclaims in the paragraph introducing that table, and the error survived validation because the citation resolved to a real file that discusses the subject."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "the source-verification audit of this node, recorded in this branch's review history and in the commit that corrected it"
  - statement: "The problem statement of the issue filed against the citation-form divergence quotes an earlier revision of AGENTS.md that has since been corrected, so its AGENTS.md limb is stale while its CONTRACT.md and validate.py limbs stand."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1478, compared against launchpad/docs/corpus/AGENTS.md at the revision this node records"
  - statement: "This node's authority to issue the MUST and SHOULD rules below comes from its task, which asks it to state scope and authority, separate MUST requirements from SHOULD guidance, and define enforcement and an exception process; the rules are this document's own normative statements rather than findings derived from a source."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1314 definition of done, under parent PRD #605"
  - statement: "This node's task requires an audiences field among the front-matter fields it asks to be appropriate to the node, without enumerating which audiences, so the selection is delegated to the author; the author named agents, developers and reviewers, and that selection is the author's own rather than a finding derived from any source."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1314 definition of done: 'schema-valid front matter with a stable node ID, type, status, origin, audiences, provenance/evidence and typed relationships appropriate to the node'"
  - statement: "Declaring a relationship to any node loadable from this branch would validate here and become a hard error the moment this node reached the launchpad branch ahead of the branch introducing that node, so this node declares no relationships."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
    confidence: 0.9
---

# Standard: evidence

What a corpus node's `evidence` ledger is, how a claim is classified, what a citation
establishes, and what a passing validation run does and does not mean. Look up the
section you need; this is reference material, not a tutorial.

## Scope and authority

**This node governs the ledger.** Which class a claim carries and why; what each class
is *for*; how a ledger is composed; how conflicting evidence is ranked; the citation
forms that name **no openable file**; and what validation establishes about any of it.
It is the canonical treatment of those subjects for the corpus.

**Its authority over the structural half is derived, not original.** The field rules —
which class requires `evidence`, which requires `confidence`, which requires
`provided_by` — are already law in `launchpad/docs/corpus/schema/node.schema.json`,
enforced through `launchpad/project-intelligence/corpus/validate.py`, and run in CI. This
document neither creates those rules nor can relax them, and it does not restate them:
the checker never reads body prose, so a copy here would stay green forever after going
stale. What this document adds is the half no schema can hold — the judgement about which
class is honest — and that half is enforced by review alone.

**On ranking conflicting evidence, `ADR-0029` outranks this document.** It is the
accepted decision; this is a standard written under it. Where the two appear to differ,
the ADR is right.

**Where this document and `validate.py` disagree about behaviour, the program wins** and
this document has drifted. Every verdict quoted below was taken from the program's own
behaviour at the revision this node records, not from another document's summary of it.
Reproduce them rather than trusting the tables — the author's run is not itself in the
ledger, because no citation form can express "I ran this":

```python
import sys; sys.path.insert(0, "launchpad/project-intelligence/corpus")
import validate as v
print(v._classify_citation("https://github.com/o/r/blob/main/Justfile", v.repo_root()))
```

**The citation forms are split with the code-references standard (#1308), deliberately.**
`AGENTS.md` says its own citation-shape table is provisional and "belongs in the evidence
standard once that lands (#1314)". This node takes half of it: the forms that name no
openable file — commit, graph edge, tool result, and any URL the validator cannot open,
which includes issue and pull-request URLs — together with what any verdict means for an
entry's class. The forms that name **code** — a repository path, a `path:line` position, a
pinned GitHub link, and how each is pinned and resolved — stay with #1308, which owns
them. Copying them
here would create the second stale copy this corpus's conventions exist to prevent. That
is not this node overriding `AGENTS.md`: the code-references standard's own section 1
already allocates the code-naming forms to itself and the tool-output forms here, as #1476
records. `AGENTS.md`'s pointer predates that allocation and now sends a reader to one place
for a subject with two owners. This node may not edit `AGENTS.md`, so the discrepancy is
reported rather than corrected.

**The `confidence` number is not this node's subject.** Once an entry is honestly an
`INFERENCE`, how strongly to rate it belongs to the confidence standard (#1309). This
node decides *which class*; that one decides *what number*.

**Who this is for.** Agents, developers and reviewers. That selection is the author's, and
the task delegates it — its definition of done requires `audiences` among the front-matter
fields it wants "appropriate to the node", without saying which audiences. The reasoning, offered as reasoning rather than as a sourced claim: #605's outcome
has both a developer and an agent authoring nodes, so both write ledgers; and reviewers
are named because the largest part of this document is rules no check can hold, which
makes a reviewer the only thing standing behind them.

Note what that paragraph is **not**. An earlier revision of this node classified the
audience choice `TEAM_KNOWLEDGE` and attributed it to #605's outcome. That outcome says a
developer can *create* a node; it says nothing about who this standard is written *for*.
Attributing the choice to it was attributing an extrapolation to the thing it started
from — a breach of this document's own MUST 9, inside this document's own ledger, found by
review and not by any check, because the schema only requires `provided_by` to be a
non-empty string.

## The ledger

**One array, one job.** A node's `evidence` array is its provenance ledger. The schema
requires it, requires at least one entry, and defines no other field in which a citation
or a classification may live — so there is no separate provenance block, no footnote
convention, and nowhere else for a source to go. The revision a node was checked against
goes in there too, as a commit citation.

**One entry, one claim.** Each entry pairs a `statement` with an `entry_class`, and the
class decides which further fields the schema then requires and which it forbids. That
matrix lives in `node.schema.json` and is explained in
`launchpad/docs/corpus/schema/README.md`. It is not reproduced here.

**The ledger and the body are two halves of one document.** Every substantive claim the
body makes needs an entry; every entry needs a claim in the body it supports. Nothing
checks either direction — the validator splits a node on its front-matter delimiters and
discards the body without reading a character of it. A claim with no entry and an entry
with no claim are equally invisible, and equally defects.

**A ledger is a snapshot, not a history.** The node schema defines no supersession field
and no temporal state on an entry, so a corpus ledger records what is claimed now. It
does not record what was claimed before, or that anything changed. `memory.py` — the
in-process store that enforces the same three classes at runtime — does carry that
machinery, and the difference is discussed in *The three classes, and what each is for*.

## The three classes, and what each is for

**The class records how you came to know the thing.** Not how sure you are, not how
important the claim is, and not how good the source looks. Three routes to knowing, three
classes, and the route you actually took decides which one is honest.

- **`FACT` — you opened the cited source and it says so.** Not "a source exists that
  probably says so", not "this is the sort of thing that file would say", and not "I read
  something like this somewhere". You opened it, at the revision the node records, and the
  words are there.
- **`INFERENCE` — you reasoned to it from cited evidence.** The sources are real and you
  read them; the conclusion is a step past what any of them states. Reasoning is not fact,
  however good the reasoning is. An `INFERENCE` also carries a `confidence`; what that
  number means and how to choose one is the confidence standard's (#1309), not this
  document's.
- **`TEAM_KNOWLEDGE` — something told to the corpus that no openable source corroborates**,
  with `provided_by` naming who or what said it: a person, an issue, a pull request, a
  decision record, a commit message. It is the class that exists for uncorroborated
  statements, and using it honestly beats promoting a recollection to `FACT`.

`AGENTS.md` puts the constraint on that last class sharply, and this document adopts it:
`TEAM_KNOWLEDGE` is not a place to park a decision the author made themselves, and
attributing an extrapolation to the thing it started from does not make it something the
author was told.

Which further fields each class then requires and forbids is the schema's business, in
`node.schema.json` and `launchpad/docs/corpus/schema/README.md`. Two properties of that
matrix are worth knowing without looking it up, because authors get both wrong:
`INFERENCE` needs citations just as `FACT` does — reasoning from nothing is not reasoning
— and `TEAM_KNOWLEDGE` needs none, which is precisely the case it exists for. It may still
carry them.

**The class is a structural field, not a note.** `ADR-0028` requires classification to
stay validator-checkable rather than asserted in body prose, so a claim's class is a
front-matter value that tooling can read, never an adjective in a sentence.

### Class is not a ranking

`FACT` is not the good one and `TEAM_KNOWLEDGE` is not the weak one. They answer a
different question from "how much should I trust this". A `FACT` cited to a file whose
author was wrong is a faithfully-recorded error; a `TEAM_KNOWLEDGE` entry attributed to
the person who made the decision is the most authoritative record that will ever exist of
why it was made. Reaching for `FACT` because it sounds stronger is the single most common
way this ledger goes wrong, and it converts an honest attribution into an unattributable
assertion.

### The one place class has a mechanical consequence

Within the corpus, class changes nothing at runtime — it is a label the validator checks
the shape of. In `launchpad/project-intelligence/memory.py`, the in-process store that
enforces the same three classes, it decides what may overwrite what:

| Stored entry | Contradicted by live repository evidence | Contradicted by a person's later statement |
|---|---|---|
| `FACT` or `INFERENCE` | Superseded by a **new `FACT`**; the old entry is flagged stale, never deleted or silently rewritten | Superseded |
| `TEAM_KNOWLEDGE` | **Nothing happens.** The observation does not supersede it and the entry is left exactly as stored | Superseded |

The asymmetry is the point, and it is the clearest statement anywhere of what the classes
mean. "This subsystem is being migrated off" can be true while the code that runs it is
untouched, so code alone cannot retire it — only the person who said it can. Code, on the
other hand, does outrank a stored `FACT` about how the system currently behaves, which is
`ADR-0029`'s contextual ranking showing up as executable behaviour.

**Do not read that table as corpus behaviour.** It is `memory.py`'s, for its own store.
The corpus node schema defines no supersession field and no temporal state on an entry, so
a corpus ledger has no mechanism of this kind at all: an entry is edited or removed by a
person editing the file, and nothing records that it used to say something else. Git does.
The ledger does not.

## Reasoning from evidence, and dressing up a decision

**This is the section worth reading twice.** Everything else here is a rule; this is the
failure the rules exist to catch, and neither the schema nor the deterministic validator
will catch it for you. Something can: a reader comparing the statement against the source.
That is a review, not a check, and it is the only thing standing here.

Two entries can be identical in front matter — a class, some citations, a well-written
statement — and be completely different objects:

- **Reasoning from evidence.** The sources constrain the conclusion. The claim is a step
  past what any one of them states, but the step is forced by what they say.
- **Dressing up a decision.** Somebody chose something. A citation was then attached that
  is *about the same subject* and does not compel the choice at all. The class makes the
  claim look derived. It was not derived; it was decided, and the decision has now been
  laundered into something that reads as a finding.

The second is the more dangerous artefact, and the reason is not that it might be wrong.
It is that **the choice becomes unattributable**. A reader who believes the claim came
from the evidence will not go looking for the person who made the call, so nobody can be
asked why, and the decision cannot be revisited — only rediscovered.

### The test

Read the `statement` and the citations. Nothing else — not the body, not what you know,
not what the team wanted.

> **Does the cited source say this, or does it merely concern this?**

A source that discusses the subject while saying nothing about the specific thing being
asserted is the tell. It will feel like support, because it is *relevant*; relevance is
not entailment. Read your own citation the way an adversary would read it, and assume
they will not extend you the benefit of the doubt.

The `INFERENCE`-specific version of this question — given that the class is honest, how
strongly do the sources support it — is the confidence standard's (#1309). What follows
here is the prior question: **which class, or none at all.**

### Three outcomes, not two

Most treatments of this offer a binary: if it is not really an `INFERENCE`, make it
`TEAM_KNOWLEDGE` and attribute it. That is right most of the time and **it is not the
whole rule**, because it assumes there is always somebody to attribute it to.

1. **The sources compel the claim** -> `INFERENCE`. Rate it per #1309.
2. **The sources leave the choice open, and somebody made it** -> `TEAM_KNOWLEDGE`,
   with `provided_by` naming that person, issue, decision record or commit. Only if
   somebody really did — a real source you can name, not a rationalisation.
3. **The sources leave the choice open and there is nobody to name, because the author
   made it while writing** -> **withdraw the claim.** No class is honest here. The
   honest artefact is not a relabelled assertion but a named gap in the node's
   scope-and-omissions section: *this was expected and could not be established.* A gap
   sends the reader to find out. A misclassified claim invites them to rely on it.

Outcome 3 is the one that gets missed, and missing it is what turns a classification
problem into three rounds of review.

### The worked example, from this repository

`AGENTS.md` was written under this contract and got this wrong twice before getting it
right. The record is in the branch's history, and it is worth reading rather than taking
on trust — `git log -1 a1e8bbcd0846321c6f6684acfe551096da4d974a` is the commit that
settled it.

| Round | What the entry claimed | Class | Why it was refused |
|---|---|---|---|
| 1 | A corpus-wide policy about provenance | `INFERENCE` | Cited a schema that is silent on the subject. Relevant, not entailing. |
| 2 | The same policy | `TEAM_KNOWLEDGE` | Attributed to an issue's definition of done, which required something narrower. Attributing an extrapolation to the thing it started from does not make it something you were told. |
| 3 | — | — | **The document stopped making the claim**, deferred the subject to the standard that owns it, and stated its own approach as working practice rather than as a rule others must follow. |

Three cross-model review passes refused the first two rounds on the same condition, and
the third refusal is what identified why the first two fixes had failed: the node was
writing policy it had no authority to write, and **reclassifying it only changed the label
on an unsourced decision.** Nothing about the front matter had ever been invalid, and nothing
about it could have been: a schema checks shape, and the defect was that a real,
resolvable, on-topic source did not say the thing above it. Only a person comparing the
statement against the source could tell the difference — which is why the rounds were
review passes rather than checker runs.

**The lesson generalises past classification.** When a claim will not sit honestly in any
class, the problem is usually not the class. It is that the document is asserting
something it is not entitled to assert, and the repair is to stop asserting it.

## When sources disagree

`ADR-0029` is the rule and this section does not restate it. What it does is say which
question you are answering, because the ADR's ranking is contextual and picking the wrong
context gives the wrong answer confidently.

**First decide what kind of claim you are making**, because that decides which source
wins:

- **How the system currently behaves** — executable evidence is authoritative: code,
  configuration, schema, passing tests. Documentation and history lose. A specification
  that was never updated after a deliberate change does not get to assert wrong behaviour
  as fact.
- **What is intended or authorized** — accepted normative decisions are authoritative:
  ADRs, ratified specifications. Code that quietly drifted from an authorized decision
  does not silently overwrite what was actually authorized.

Most apparent conflicts dissolve here, because the two sources are answering different
questions and each has its own tiebreaker. "The spec says X, the code does Y" is usually
not a conflict at all: it is one FACT about intent and one FACT about behaviour, and both
belong in the ledger as separate entries with separate statements.

**Two rankings the ADR rejects, and so does this document.** Do not apply one fixed
hierarchy to every claim, and do not let the most recently touched source win. Recency is
not authority.

**GitHub history, team knowledge and inference are never treated as fact on their own.**
They may supply context; they stay attributed to their source and distinguishable from
`FACT`. That is not a stylistic preference — it is the ADR's text, and `provided_by` is
the field that carries the attribution it requires.

**A real conflict is escalated, not resolved.** Two sources with authority over the *same*
claim type contradicting each other — two accepted decisions, or a decision and a ratified
specification, both governing the same intent — is where an author stops. Record the
contradiction, set the node's `status` to `flagged`, and leave it for a human. `flagged`
exists in the schema for exactly this state and means an unresolved conflict between
authorities, not "low confidence" and not "still a draft". Do not express a conflict as a
hedge in the prose or as a middling number: a node that reads as merely tentative when it
is actually unresolved is worse than one that admits it, because it invites use.

## What a citation establishes

**Citation checking is structural, and that is the single most important thing on this
page.** The validator confirms that a cited repository path resolves to a real file inside
the repository. It never opens that file. Nothing anywhere compares a source against the
`statement` sitting above it, so **a `FACT` citing a real file that says nothing on its
subject passes with no notice at all** — not an error, not an `UNVERIFIED` line, nothing.
Only a person reading the source establishes a `FACT`. The checker establishes that you
cited something.

### The forms that name no openable file

These are this node's half of the citation vocabulary; the forms that name **code** — a
repository path, a `path:line` position, a pinned GitHub link — belong to #1308, which
states what each proves and how each is pinned.

| Form | Example | Verdict | What it establishes |
|---|---|---|---|
| Commit reference | `commit 0f3a…` | `unverified` | **Nothing.** Not even that the commit exists — a commit id that has never been in this repository is reported identically to one that has. |
| Graph edge | `is_shared_gated_kind -> is_unshared_gated_event (1 hop)` | `unverified` | Nothing. |
| Tool result | `find_references('x', crate='buzz-core') -> no callers here` | `unverified` | Nothing. |
| A URL the repository-link pattern does not match — any non-GitHub URL, and GitHub issue and pull-request URLs | `https://example.com/spec`, `…/buzz/issues/1314` | `unverified` | Nothing. The pattern requires a `blob`, `raw`, `tree`, `blame`, `commits` or `edit` segment, so an issue URL never enters that branch and falls through here. |
| A repository link satisfying **all three** rules below | `…/blob/<40-lowercase-hex>/Justfile` | `ok` | **Only that the URL has that shape. Nothing is fetched.** A link whose owner, repository and file do not exist is accepted. This is #1308's form; it is here to complete the verdict picture. |
| A repository link breaking **any** of the three | `…/blob/main/Justfile` | **`error`** | — a hard failure. A *recognised* shape can still fail hard. |
| Free text matching none of the six forms | `as discussed in the meeting last week` | **`error`** | — "matches none of CONTRACT.md's six supported citation forms". |
| A bare path that does not resolve, or resolves outside the repository | `launchpad/does-not-exist.md` | **`error`** | — a different error from the row above, and #1308's subject. |

**`UNVERIFIED` is not a pass and it is not a failure.** It means the validator recognised
the shape and could not open it, and it prints on passing runs precisely so that a `PASS`
never claims more than it checked. A `FACT` resting only on `UNVERIFIED` citations has
been checked by nothing at all. Open the source and keep the class, or change the class.

**These three rules are #1308's, restated here with a reason, because SHOULD 6 requires one.**
The verdict table above is unusable without them: it distinguishes `ok` from `error` for
repository links, and a reader cannot apply that distinction without knowing which links
are well-formed. They are reproduced as **provisional** — #1308 owns them, and where the
merged text differs, it wins and this block is the stale copy to delete.

The three rules, all measured rather than read off another document — get any one wrong and
the node does not merge:

1. **The host and shape must match** — a `github.com/<owner>/<repo>/<verb>/<ref>/<path>`
   URL, or a `raw.githubusercontent.com/<owner>/<repo>/<ref>/<path>` URL.
2. **The verb must be `blob` or `raw`.** `tree`, `blame`, `commits` and `edit` are
   recognised and rejected — four verbs, each with its own error message.
3. **The ref must be forty *lowercase* hexadecimal characters, and the path must be
   non-empty.** An uppercase full SHA is rejected, and its message says "pinned to a
   mutable ref", which is misleading — the SHA is fine, its case is not.

**The channel is for forms unverifiable by nature.** It is not a soft-failure bucket. A
form the validator merely failed to establish is an error rather than a notice — which is
why free text fails hard, and, less obviously, why a **recognised** URL shape that is
malformed fails hard too. Do not read `unverified` as "the lenient outcome for URLs": a URL
the pattern does not match is a notice, while a URL it *does* match and finds malformed is
an error that stops your node merging.

### The one permitted exception

The entry recording **the revision the node was checked against** cites a commit and
nothing else, and stays a `FACT`, because there the citation *is* the claim: the statement
asserts the revision, and no file can corroborate an assertion about which revision it is.
It is still checkable, just not by this checker:

```bash
git cat-file -e <sha>   # exit 0 means that revision exists in this repository
```

Run that and the entry is honest. **A commit citation attached to any claim about
repository content is not covered** — that claim needs the file, at that revision. And
note the asymmetry the exception depends on: the validator itself never runs the command
above, so nothing but the author's diligence distinguishes a real revision from a typo.

**Nothing enforces the "one" in one permitted exception.** A second, third or tenth
commit-only `FACT` produces nothing but further non-fatal notices and the run still exits
0. This is a rule a reviewer holds; more than one commit-only `FACT` in a ledger is the
signal, and no check will ever raise it.

### When the only source is an issue, a pull request, or a conversation

You have no openable file and no way to pin one. Do not force it into a `FACT` on a URL or
a tool-result citation — that produces an `UNVERIFIED` `FACT`, which is a claim checked by
nothing wearing the strongest class. Use `TEAM_KNOWLEDGE` with `provided_by` naming the
issue, the pull request or the person. That is what the class is for, and `ADR-0029`
requires GitHub history to stay attributed rather than be promoted to fact.

### The forms do not agree across three documents, and this node states which is which

`launchpad/project-intelligence/CONTRACT.md` §3 enumerates **six** shapes — file range,
file line, bare path, graph edge, tool result, commit — and contains **no URL form at
all**; the section has zero occurrences of `http`. `validate.py` implements a URL branch
regardless — a whole URL branch, with three hard-error conditions of its own — while its own
module docstring says citations are parsed against §3's six forms.

**`AGENTS.md` is not part of the divergence, and this document said it was.** It states
that §3 has six shapes and no URL form, that its own table is **seven** rows because it
adds the two URL forms `validate.py` recognises, and that the table "is not a summary of
§3". It goes further and records that an earlier version of its own sentence *did* claim
that, and that an agent authoring a sibling node built a scope argument on the miscount
before a plan review caught it.

**This node is that sibling node, and it re-introduced the same miscount.** An earlier
revision of the ledger above asserted that `AGENTS.md` "introduces its citation table as
`CONTRACT.md`'s shapes" — the exact claim `AGENTS.md` disclaims in the paragraph
introducing the table. It survived because the citation resolved: `AGENTS.md` is a real
file that genuinely discusses the subject, so every check passed. Only opening it and
reading the sentence caught it. That is this document's own thesis failing on this
document, and it is left recorded here rather than quietly corrected.

**So the divergence is two-way, not three-way:** `CONTRACT.md` §3 and `validate.py`
disagree, and `AGENTS.md` describes both accurately. **#1478** is filed against the
divergence and its problem statement quotes an older `AGENTS.md`; that limb of it is now
stale, and this node reports rather than edits it.

This node does not resolve any of it and may not edit the other documents. What it does is
take a side about *derivation*: **the verdicts above come from `validate.py`'s behaviour**,
because the program is what decides whether a node merges. §3 supplies the vocabulary of
shapes and is not a complete list of what the checker accepts. An author who reads §3
alone will conclude a GitHub link is not a legal citation and be wrong.

### Three things a green run does not mean

1. **That a citation supports its claim.** Structural checking, as above.
2. **That the ledger and the body agree.** The validator splits a node on its front-matter
   delimiters and discards the body unread. A body claim with no entry, and an entry
   supporting no body claim, are both invisible. This is the drift that ends a node's
   honesty, and no automated check exists for it in either direction.
3. **That the recorded revision is current, or real.** It is neither fetched nor compared
   against `HEAD`.

## MUST

These are requirements. Where one is mechanically enforced it says so; the rest are held
by review, and a reviewer who waves one through has approved a defect.

1. **Every substantive claim of fact in the body MUST have a ledger entry, and every ledger
   entry MUST support a claim the body makes.** Both directions. Neither is checked. The
   rule covers assertions about what some file, tool, decision or process does or says. It
   does **not** cover the normative rules a standard issues under its own authority — a
   MUST is not a finding, and manufacturing a citation for one is the very laundering this
   document warns against. Where that authority comes from belongs in the ledger, and for
   this node it is there as an attributed entry; the individual rules do not each need one.
2. **A claim MUST be classified by how it came to be known**, never by how strongly it is
   held, how important it is, or how authoritative the class sounds.
3. **A `FACT` MUST rest on a source the author opened**, at the revision the node records,
   and that source MUST say what the statement says. Enforced by nobody.
4. **A `FACT` MUST rest on at least one citation the validator can open**, with exactly
   one exception: the entry recording the node's revision.
5. **A node MUST carry at most one commit-only `FACT`.** Not enforced; a second produces
   only another notice.
6. **An entry whose citations concern the claim's subject without compelling the claim
   MUST NOT be a `FACT` or an `INFERENCE`.** That is a decision, not a derivation.
7. **When the choice was the author's own and no person, issue or record can honestly be
   named, the claim MUST be withdrawn** rather than relabelled. See *Three outcomes, not
   two*.
8. **`provided_by` MUST name a source a reader could go to** — a person, an issue, a pull
   request, a decision record, a commit. Not "the team", not "prior discussion", not the
   author of the node.
9. **`TEAM_KNOWLEDGE` MUST NOT be used to attribute an extrapolation to the thing it
   started from.** Attribution records what you were told, not what you built on top of
   it.
10. **Two authorities of the same claim type in conflict MUST leave the node
    `status: flagged`** for a human, rather than being resolved by its author.
11. **A claim re-verified at a new revision MUST have its entry updated in the same
    edit.** A ledger that lags the body is the failure mode both are there to prevent.
12. **Private or unpublishable evidence MUST NOT be copied into the corpus to support a
    claim.** Where the evidence cannot be shown, the claim stays unestablished. This is
    `ADR-0029`'s security clause, not a stylistic preference.

## SHOULD

Depart from these with a reason, and say what it was.

1. **Write the ledger before the body.** A claim invented while drafting prose is the one
   most likely to reach the page without an entry, because by then the ledger feels
   finished. Deciding what you can support first also tends to shorten what you write.
2. **Cite the narrowest source that actually supports the claim, and only that.** A second
   citation added "for context" is a second thing that can rot, and the checker will never
   tell you which one did.
3. **Prefer a source you can open to one you cannot.** Between a repository path and an
   issue URL that both bear on a claim, the path is checked and the URL is not.
4. **Split a compound claim into separate entries.** If one half rests on code and the
   other on a conversation, one entry cannot be classified honestly and the class you pick
   will misdescribe half of it.
5. **Prefer withdrawing a weak claim to publishing it.** A gap in *Scope and omissions*
   sends a reader to find out; a thin claim invites them to rely on it. This costs nothing
   and is almost never chosen.
6. **Link another document's rules rather than restating them.** The checker never reads
   body prose, so a copy stays green forever after going stale — the ledger cannot keep a
   restatement honest, because the restatement is not a claim anyone is auditing.
7. **Re-read every `FACT`'s citation adversarially before the pull request opens**, asking
   only whether the source says the statement. This is the single highest-yield review
   step, and it is the one nothing else in the pipeline performs.

## Enforcement, and where it stops

Run it locally, from the repository root:

```bash
python3 launchpad/project-intelligence/corpus/validate.py
```

Exit 0 passes; 1 means at least one error, each naming the node it came from.
`just corpus-validate` is the same command but needs the Hermit environment activated
first; the interpreter form above does not. CI runs it on every pull request and on every
push to `launchpad` that touches the corpus root, so a local failure is a CI failure.

**Enforced by `node.schema.json` through `validate.py`:**

- Every entry has a `statement` and a legal `entry_class`.
- `FACT` and `INFERENCE` each carry at least one citation; `TEAM_KNOWLEDGE` carries
  `provided_by`.
- The forbidden-field rules in both directions: no `confidence` outside `INFERENCE`, no
  `provided_by` outside `TEAM_KNOWLEDGE`.
- Every citation matches a recognised form, and every repository path resolves to a real
  file inside the repository.

**Mirrored by `memory.py`'s `__post_init__` for the in-process store — the first three
bullets only.** It is a parallel path rather than one calling the other, and it is
narrower than it looks: it requires each citation to be a non-empty string and stops
there. It does **not** parse citation forms and does not resolve paths, so a `FACT`
carrying free prose, or a path to a file that does not exist, is accepted by `MemoryEntry`
and rejected by `validate.py`. The two also disagree in the other direction on at least one
value — the subject of #1463. Treat them as overlapping, not equivalent.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Whether a citation supports its claim | A `FACT` citing a real file silent on the subject passes with no notice. |
| Whether an `INFERENCE` is really a decision | Invisible to every check that exists. The failure this document is mostly about. |
| Whether `provided_by` names a real source | Any non-empty string satisfies the schema. |
| Whether the body and the ledger agree | The body is discarded unread, in both directions. |
| Whether the recorded revision exists, or is current | Never fetched, never compared to `HEAD`. |
| How many commit-only `FACT`s a node carries | Only further non-fatal notices. |
| Whether a genuine conflict was flagged rather than resolved | `status` is a free choice from an enum. |

The pattern across that table: **everything a schema can hold is held, and everything that
requires reading is not.** Reviewing a ledger means opening the sources. There is no
cheaper check, and a green run is not one.

## Exceptions and escalation

**There is no exception process for the structural requirements.** They are enforced
before merge and cannot be waived by agreement. Changing them means changing
`node.schema.json`, which `launchpad/docs/corpus/schema/COMPATIBILITY.md` governs: a change
that removes a field, removes an enum value or narrows a type is breaking, and needs a
dated entry there plus a re-validation pass of every existing node in the same pull
request. That is a schema change, not an exception.

**When a claim will not sit honestly in any class**, work down this list and stop at the
first that applies:

1. **Can a source settle it?** Open it. The entry becomes a `FACT` and the question goes
   away. This is nearly always available and nearly never taken.
2. **Is it two claims?** Split it, and classify each.
3. **Did somebody actually decide it?** `TEAM_KNOWLEDGE`, naming them.
4. **None of those?** Withdraw the claim and record it as a gap. That is the answer, not
   a failure to find one.

**When two authorities of the same claim type contradict each other**, set the node's
`status` to `flagged`, record the contradiction, and leave it for a human. `flagged` is
`ADR-0029`'s accepted safer failure mode, not a defect to be tidied away — and it is not
an escape hatch for a rule you find inconvenient.

**When a rule here cannot be met**, do not relax it locally. A standard that one node
quietly widens has stopped being a standard, and no check will notice. Raise an issue
against **#605** describing the entry you needed and could not write honestly.

**When this document and `validate.py` disagree about behaviour**, the program is right
and this document is the defect. Fix it here, with a newly measured verdict, rather than
working around it in a node.

## Read these rather than trusting a copy here

| For | Read |
|---|---|
| The front-matter contract — fields, enums, and which class requires or forbids what | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose explanation of those fields | `launchpad/docs/corpus/schema/README.md` |
| Adding a value to a closed enum | `launchpad/docs/corpus/schema/COMPATIBILITY.md` |
| How to rank conflicting evidence, and when to stop | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Why classification must be structural rather than prose | `launchpad/decisions/ADR-0028-corpus-canonical-representation.md` |
| The citation shapes as vocabulary | `launchpad/project-intelligence/CONTRACT.md` §3 |
| What the checker actually does — the authority for every verdict here | `launchpad/project-intelligence/corpus/validate.py` |
| The same three-class contract enforced at runtime, and the supersession rules | `launchpad/project-intelligence/memory.py` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The citation forms that name **code**, and how each is pinned and resolved | the code-references standard (#1308) |
| What an `INFERENCE`'s `confidence` number means and how to choose one | the confidence standard (#1309) |

**Enum member lists and the schema's field-combination matrix are deliberately not
reproduced above.** See SHOULD 6 for why.

## Scope and omissions

**This document covers** what a node's `evidence` ledger is, the three classes and what
each is for, how to tell reasoning from a disguised decision, which of three outcomes an
unsupportable claim takes, how conflicting evidence is ranked and when to escalate, the
citation forms that name no openable file, and what a passing validation run does and does
not establish.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The citation forms that name **code** — repository paths, positions, pinned links, and how each resolves | #1308 |
| What an `INFERENCE`'s `confidence` value means and how to pick one, and the NaN question raised against it | #1309 and #1463 |
| Provenance for generated artifacts and the exception process for them | #1316 |
| Whether a recorded revision may stay put across edits, and what to do when only some claims are re-verified | #1321 |
| Encoding `ADR-0029`'s claim-type classification and the flagged state in the schema and checker | #1410 |
| Line numbers in citations not being checked against file length | #1459 |
| Reconciling `CONTRACT.md`, `AGENTS.md` and `validate.py` on the citation forms | #1478 |
| Whether `ADR-0003`'s markdown-link wrapper is required on corpus evidence | #605 |
| The human-facing entry point to the corpus | #639 |
| Whether one node holds one claim or several | left open by `ADR-0028`; #605's to decide |

**One position taken without a source, and named as such.** MUST 8 lists a commit among the
things `provided_by` may name, and this node uses that form. `AGENTS.md` says the field
names "who or what said it: a person, an issue, a decision record" and does not mention a
commit message. Nothing settles whether a commit message counts, so this is the author's
reading — a commit message is a record written by a person — issued as a rule under this
node's own authority rather than presented as a finding. If #605 rules otherwise, MUST 8
changes.

### The boundary with the code-references standard, stated rather than left implicit

**#1476** records that the code-references standard declares classification to be this
node's subject and then states normative rules about it — when a claim may carry the class
`FACT`, and how many commit-only `FACT`s a node may hold — and asks that whichever
document claims the subject leaves the other an explicit marker.

**This node claims it, and #1476 is what lets it.** That issue's Expected section delegates
the choice — "whichever #1314 chooses, the two documents should end up with one owner for
class rules" — so this is an attributed decision, not one invented while writing. Class
assignment and ledger composition are stated here as MUSTs 1 through 11, and this node is
their owner. (MUST 12 is `ADR-0029`'s security clause,
restated under the ADR's authority rather than this node's.) Where the code-references
standard states the same rules, treat them as provisional and this node as authoritative;
where it states the **citation-quality** side of the same boundary — that a `FACT` needs a
citation something can open — the two agree and no precedence is needed.

**That declaration is prose, and prose is not a mechanism.** This node declares no
`relationships`, for the reason below, and #1476 records that the code-references node
declares none either, so nothing machine-readable sends a reader from here to the other
document or back. Two governance nodes carrying rules on one subject
with no machine-readable precedence between them is the risk #1476 names, and this node
reduces it by naming an owner rather than eliminating it. Declaring the edge is a
follow-up, once both have merged.

**`AGENTS.md`'s pointer is now imprecise, and this node did not cause that.** It says its
citation-shape table "belongs in the evidence standard once that lands (#1314)" — the whole
table. But the code-references standard's section 1, quoted in #1476, already claims the
code-naming forms and assigns only the tool-output forms here. So the table has two
destinations and `AGENTS.md` names one. This node takes what nothing else claims and leaves
the rest; it may not edit `AGENTS.md`, so the discrepancy is reported.

### No `relationships` in this node's front matter

The reason is **merge order**, not an empty corpus. `corpus-agents` is loadable from this
branch, so an edge to it would validate here — and would become a hard error the moment
this node reached `launchpad` ahead of the branch that introduces it, because a
`relationships[].target` matching no loaded node's id fails. Do not take that on this
document's word — check what the merge target actually carries, which is the command
`AGENTS.md` gives for the same purpose:

```bash
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

The edges get declared in one pass once the set has landed, which is a follow-up rather
than an oversight.

### Expected but not verified when this node was written

- **No generated view was tested consuming a ledger.** `validate.py` records that no
  corpus generator exists yet, so how a projection would render or rank the three classes —
  and in particular whether it would preserve the distinction at all — is unknown.
  `ADR-0028` requires that generated views must not silently drop provenance their source
  node carries; nothing existed to test that against.
- **The citation verdicts were produced by calling `validate.py`'s classifier directly on
  constructed citations, and that run is not in the ledger.** No citation form expresses an
  execution, so the entries behind those verdicts cite the program's source and the tables
  are reproducible by the snippet in *Scope and authority* rather than by a recorded
  result. An earlier revision of this node stated two of those verdicts wrongly, and the
  ledger passed every check while it did.
- **`memory.py` was executed for its field contract, but its supersession behaviour was
  read, not run.** A cross-model review constructed `MemoryEntry` values directly and found
  it accepts citations `validate.py` rejects, which is why *Enforcement* now describes the
  two as overlapping rather than equivalent. The class-asymmetry table in *The one place
  class has a mechanical consequence* still comes from `record_code_contradiction` and
  `record_team_statement` as written; those two functions were not run.
- **No claim here was checked against a second consumer of the ledger format.** The
  schema, the validator and `memory.py` were all read. Whether anything else parses an
  `evidence` array, and whether it shares their rules, was not established.
- **The two sibling standards were read on their unmerged branches and are cited to the
  issues that describe them, not to their files.** Their files do not exist on this branch,
  so no citation to them could resolve and none was written. If either changes before
  merging, the boundary stated above needs re-checking against the merged text rather than
  against this node's description of it.

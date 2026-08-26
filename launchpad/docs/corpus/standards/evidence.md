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
  - statement: "Every entry carries a statement and an entry_class, and the class chosen decides which of evidence, confidence and provided_by the schema then requires and which it forbids."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
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
  - statement: "The citation forms that name no openable file -- a commit reference, a graph edge, a tool result, and any URL that is not a pinned GitHub file link -- are reported on a non-fatal UNVERIFIED channel that always prints and never changes the exit status."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A commit citation is never checked against the repository's object store, so a commit id that exists and one that does not are both reported UNVERIFIED and are indistinguishable in the output."
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
  - statement: "validate.py implements a URL branch regardless, accepting a GitHub blob or raw link pinned to a full commit SHA and reporting every other URL UNVERIFIED, while its own module docstring says citations are parsed against CONTRACT.md section 3's six forms."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "AGENTS.md introduces its citation table as CONTRACT.md's shapes and then lists seven rows, two of which are the URL forms section 3 does not contain, and says so about itself."
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
  - statement: "ADR-0029 ranks evidence contextually by claim type rather than by one fixed hierarchy, and holds that GitHub history, team knowledge and inference are never treated as fact on their own but stay attributed to their source."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "ADR-0029 requires a node whose two same-claim-type authoritative sources contradict each other to be left unestablished and flagged for a human rather than resolved by its author, and node.schema.json provides flagged as a status value for exactly that state."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "ADR-0028 requires claim classification to stay structurally encoded and validator-checkable rather than asserted only in free-form body prose, and leaves the question of how many claims one node holds open."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The validator never reads a node's body, so a body claim carrying no ledger entry, and a ledger entry supporting no body claim, are both invisible to every check that exists."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The same validator command that runs locally runs in CI on every pull request and every push to the launchpad branch that touches the corpus root, so a local failure is a CI failure."
    entry_class: FACT
    evidence:
      - ".github/workflows/launchpad-corpus-validate.yml"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "On issue #636 an authored policy claim was classified INFERENCE citing a schema silent on the subject, reclassified TEAM_KNOWLEDGE attributed to an issue's definition of done, and refused in both forms by successive cross-model reviews, and the accepted fix was for the document to stop making the claim."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#636, recorded in the message of commit a1e8bbcd0846321c6f6684acfe551096da4d974a"
  - statement: "The code-references standard states normative rules about when a claim may carry the class FACT and about how many commit-only FACTs a node may hold, while declaring that classification belongs to this node, and the open question of which of the two owns those rules is filed as an issue asking whichever claims the subject to leave the other an explicit marker."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1476 'task: settle whether code-references or evidence (#1314) owns the FACT and ledger-composition rules'"
  - statement: "This standard addresses developers as well as agents and reviewers, because a developer is one of the two authors the parent feature's outcome names."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 outcome: 'A developer or agent can create one atomic corpus node and deterministic validation accepts or rejects it against one documented contract.'"
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
this document has drifted. Every verdict quoted below was measured by running it at the
revision this node records, not read out of another document.

**The citation forms are split with the code-references standard (#1308), deliberately.**
`AGENTS.md` says its own citation-shape table is provisional and "belongs in the evidence
standard once that lands (#1314)". This node takes half of it: the forms that name no
openable file — commit, graph edge, tool result, and non-GitHub URL — together with what
any verdict means for an entry's class. The forms that name **code** — a repository path,
a `path:line` position, a pinned GitHub link, and how each is pinned and resolved — stay
with #1308, which already treats them in more detail than this node would. Copying them
here would create the second stale copy this corpus's conventions exist to prevent. That
leaves `AGENTS.md`'s pointer half right and half wrong; this node may not edit
`AGENTS.md`, so the correction is filed rather than made.

**The `confidence` number is not this node's subject.** Once an entry is honestly an
`INFERENCE`, how strongly to rate it belongs to the confidence standard (#1309). This
node decides *which class*; that one decides *what number*.

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

## When sources disagree

## What a citation establishes

## MUST

## SHOULD

## Enforcement, and where it stops

## Exceptions and escalation

## Read these rather than trusting a copy here

## Scope and omissions

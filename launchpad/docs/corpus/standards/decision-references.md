---
id: corpus-standard-decision-references
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a1e8bbcd0846321c6f6684acfe551096da4d974a."
    entry_class: FACT
    evidence:
      - "commit a1e8bbcd0846321c6f6684acfe551096da4d974a"
  - statement: "Evidence is ranked by claim type rather than by one fixed hierarchy: for a claim about how the system currently behaves, executable evidence is authoritative over documentation and history; for a claim about intended or authorized behaviour, an accepted normative decision is authoritative over everything else, including code that has drifted from it without a corresponding decision update."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Two sources with authority over the same claim type that contradict each other are not reconciled by the authoring agent; the contradiction is recorded and the affected node stays unestablished or flagged until a human resolves it."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "GitHub history, team knowledge and inference may supply context for a decision claim but are never treated as fact on their own, and stay attributed to their source."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Incorrect precedence between a decision and code is treated as a security concern, because it can present stale or unauthorized behaviour as current policy."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "flagged is a node status the schema defines specifically for ADR-0029's unestablished state, distinguished there from ordinary low confidence."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Accepted decisions for this repository are recorded one file per decision under launchpad/decisions/, named ADR-XXXX-slug.md, numbered in the order they were accepted, and numbers are never reused."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "A decision record carries its lifecycle state in a front-matter status field, and accepted, proposed and superseded records all sit in launchpad/decisions/ under the same filename pattern."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/decisions/ADR-0005-launchpad-deployment-boundary.md"
      - "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md"
  - statement: "The Decision section is the load-bearing part of a decision record; Context and Consequences exist to make it understandable, not to carry the normative statement."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "Superseding a decision does not edit it: a new record is written, the superseded record's status becomes Superseded by ADR-YYYY, and the new record names what it supersedes."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
      - "launchpad/decisions/ADR-0050-canonical-corpus-supersedes-handbook.md"
      - "launchpad/decisions/ADR-0001-handbook-repository-location-and-publication-target.md"
  - statement: "A decision is written in the same pull request that closes the issue where it was argued, because a decision recorded only in a closed issue is lost."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "An open question becomes a type:adr issue parented to the PRD that raised it, and its decision outcome stays blank until a human settles it; agents draft decisions, they do not make them."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/README.md"
  - statement: "ADR-0028 is an accepted decision authorizing Markdown with YAML front matter as the one canonical authored representation of a corpus node, with every other serialization a generated derived view."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0028-corpus-canonical-representation.md"
  - statement: "The corpus checker accepts a bare repository-relative citation only when it resolves, inside the repository, to a real file, and it never opens that file's contents."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "A citation carrying a line position has its path component checked against the filesystem exactly as a bare path is, and only the line number itself goes unchecked."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "A relationships entry whose target names an id no loaded node carries is a hard validation error."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The repository's automated ADR check is scoped to ADR-0005's sanctioned-file list and reads no other decision record's front matter."
    entry_class: FACT
    evidence:
      - "launchpad/scripts/adr_boundary_check.py"
      - ".github/workflows/launchpad-adr-check.yml"
  - statement: "Node front matter rejects any field beyond the seven the schema names, so a citation-level exception has nowhere to live except the evidence entry's own statement."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "ADR-0029 grants intent and authorization authority to accepted normative decisions, naming ADRs and ratified specifications together."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "launchpad/project-intelligence/CONTRACT.md describes its own status as proposed and not ratified."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/CONTRACT.md"
  - statement: "The corpus checker treats the flagged status exactly as it treats any other status, and compares no two decision records against each other, so nothing in it detects an unresolved conflict."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "Because the checker resolves a decision citation as a path and never reads the record's front matter, an intent claim citing a proposed or superseded record validates exactly as cleanly as one citing an accepted record, so a record's status is a reviewer's responsibility and not the checker's."
    entry_class: INFERENCE
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/decisions/README.md"
    confidence: 0.95
  - statement: "Ratification is therefore a state a specification can be in without any repository document defining how it is conferred, so a specification cannot today be shown to meet ADR-0029's bar the way a decision record's status field shows it."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
      - "launchpad/project-intelligence/CONTRACT.md"
    confidence: 0.6
  - statement: "Issue #1310 requires this node to state its scope and the authority its policy rests on, to separate MUST requirements from SHOULD guidance, and to define enforcement and an exception or escalation process."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1310 definition of done"
  - statement: "Issue #1410 owns encoding ADR-0029's claim-type classification and unestablished or flagged state in the corpus schema and validator."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1410"
---

# Citing a decision
  - statement: "Per Serina's decision on launchpad-26/buzz#1486, this node reconciles to #1313's documentation-standard: the H1 is now 'Standard: decision references', and the enforcement section's name now uses the word 'Enforcement'."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1486, decided 2026-08-27"
---

# Standard: decision references

How a corpus node cites an **accepted decision** — an ADR, or a ratified specification —
as evidence for a claim, and when a decision is the wrong citation entirely.

This is a policy node. Look up the section you need.

## Scope and authority

**This node covers** which claims a decision record may be cited for, how to cite one,
what to do when two accepted decisions conflict, what to do when a cited decision is
superseded, and what the deterministic check does and does not establish about any of it.

**The authority is `ADR-0029`, not this file.** ADR-0029 decides that evidence is ranked
contextually by claim type and that conflicts escalate rather than resolve. This node
turns that rule into something an author can apply without already knowing the answer.
`launchpad/decisions/README.md` owns the decision-record lifecycle — naming, numbering,
front matter, supersession — and this node duplicates none of it.

If this file and either of those disagree, **they win**; this one has drifted and should
be fixed.

| For | Read |
|---|---|
| How evidence is ranked, and why conflicts escalate | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| The decision-record lifecycle, numbering and supersession | `launchpad/decisions/README.md` |
| The front-matter contract for a corpus node | `launchpad/docs/corpus/schema/node.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| The citation shapes and what the checker does with each | `launchpad/docs/corpus/AGENTS.md` |

## Which kind of claim are you making?

Everything else here depends on this answer, and the same decision record is the right
citation for one claim and the wrong one for another.

**The question that decides it:** *if the code and the decision said different things,
which one would a reader call the defect?*

| If the answer is | The claim is | Authoritative evidence |
|---|---|---|
| "the decision is out of date" | a **behaviour** claim — how the system acts today | code, config, schema, a passing test |
| "the code has drifted" | an **intent** claim — what was decided, intended or authorized | the accepted decision, *even over the code* |

That asymmetry is the first half of ADR-0029 — the second half is what happens when two
sources of the *same* claim type disagree, and it has its own section below. Neither
ordering is right for both claim types:
a fixed "the decision always wins" rule would assert wrong behaviour as fact after a
deliberate code change, and a fixed "the code always wins" rule would let quiet drift
overwrite what was actually authorized.

### Worked examples from this repository

**A behaviour claim.** *"A citation that does not resolve to a real file in the repository
is a hard error."* This describes what runs. Cite
`launchpad/project-intelligence/corpus/validate.py`. No decision record establishes it,
and one that agreed with it would still not be the evidence.

**An intent claim.** *"Markdown with YAML front matter is the one canonical authored
representation of a corpus node."* This describes what was authorized. Cite
`launchpad/decisions/ADR-0028-corpus-canonical-representation.md`. If a hand-authored JSON
node turned up on disk tomorrow, that file would be the defect — it would not redefine the
claim, and it would not become the evidence.

**The same record, on both sides of the line.** `ADR-0029` is the correct citation for
*"the corpus is required to record a same-claim-type contradiction rather than resolve
it"* — an intent claim about what is authorized. It is the **wrong** citation for *"a node
sitting on an unresolved contradiction is flagged by validation"*, which is a behaviour
claim, and which is false: nothing checks it yet. Citing the ADR there would assert a
behaviour from a source that only ever authorized it.

**The mistake this catches.** A sentence about what the system *does*, resting only on a
decision record, is a behaviour claim wearing an intent citation. It passes validation, it
reads as sourced, and it is the failure mode ADR-0029 calls a security concern: stale or
unauthorized behaviour presented as current policy. Either recite it to the code, or
reword it as the intent claim it can actually support.

## MUST

1. An **intent claim** governed by an accepted decision **MUST** cite that decision — not
   code that happens to agree with it, and not the issue where it was argued.
2. A **behaviour claim MUST NOT** rest on a decision record alone. It needs executable
   evidence; a decision may accompany it as a *separate* entry making a *separate*
   statement.
3. A decision **MUST** be cited by repository-relative path —
   `launchpad/decisions/ADR-NNNN-slug.md` — and that path **MUST NOT** carry a line
   position. The path component is checked against the filesystem either way, so a typo in
   the path fails loudly whichever form is used; what a line position adds is a precision
   nothing verifies. A record is edited in place, so a position drifts silently, and a
   citation that looks precise while pointing at the wrong paragraph is worse than one
   that points at the file.
4. Before citing a decision for an intent claim, the author **MUST** open the record and
   read its front-matter `status`. A record that is not accepted **MUST NOT** be cited as
   authority for an intent claim. Proposed and superseded records live in the same
   directory under the same filename pattern as accepted ones, so the path alone tells you
   nothing.
5. A `FACT` asserting **what is authorized** **MUST** rest on the record's **Decision**
   section — that is the load-bearing part. Every other section is a legitimate source
   for a claim about something *other than* authorization — rationale from Context,
   expected effect from Consequences, where the decision was really made from
   Provenance, and so on — and such a claim **MUST** be worded as the kind of claim it
   is. `launchpad/decisions/README.md` lists the sections a record carries; individual
   records add their own, so do not assume the list is closed.
6. When two accepted decisions of the **same claim type** contradict each other, the author
   **MUST** stop, **MUST** record the contradiction and both records in the ledger, and
   **MUST NOT** pick a side. See *When two accepted decisions conflict*.
7. A node citing a **superseded** record **for an intent claim MUST** say so in the
   entry's `statement`, and **MUST** say why that record is still the right source.
   Silence there asserts current authorization from a record that no longer carries any.
   The rule is scoped to intent claims deliberately: an entry whose claim is *about* the
   record — that it exists, that it is superseded, what its status field says — is
   already disclosing the thing MUST 7 exists to force, and this node's own ledger cites
   `ADR-0001` twice on exactly that basis.

## SHOULD

- **Name the ADR number and its subject in the `statement`.** The ledger is what a later
  reader greps when a decision is superseded; a statement that names only the claim leaves
  them opening every citation to find out which nodes are affected.
- **Cite the decision record, not the issue that argued it.** The record exists precisely
  because a decision left only in a closed issue is lost to the noise. Where the issue adds
  argument the record omits, cite it as a *second* entry making a claim about **rationale**
  — attributed, and not as `FACT`. MUST 1 still holds for the authorization claim itself.
- **Keep the intent claim and the matching behaviour claim as two entries.** "ADR-0028
  requires X" and "the checker enforces X" are different claims with different evidence and
  different failure modes. Merged into one sentence, the weaker half inherits the stronger
  half's citation.
- **Quote the sentence you are relying on in the `statement`** rather than reaching for a
  line position to point at it. MUST 3 rules the position out; a short quotation survives
  the record being reflowed, and it is what a later reader needs anyway.
- **Re-read the record rather than the memory of it.** A record's status changes without
  its path changing, and nothing about the citation will look different afterwards.

## When two accepted decisions conflict

ADR-0029 resolves the ordinary case by claim type. What it deliberately does **not**
resolve is two sources with authority over the *same* claim type saying different things —
two accepted ADRs, or an accepted ADR and a ratified specification, both governing the same
intent claim.

**The author's behaviour is fixed:** stop, record the contradiction, and leave the node
unestablished until a human resolves it. Concretely:

1. Write **one evidence entry per contradicting record**, each citing its own record, each
   stating what that record says. Do not write a third entry stating the resolution.
2. State the contradiction in the body — both records, and the claim they disagree about.
3. Set the node's `status` to `flagged`. The schema defines that value for exactly this
   state, and describes it as naming an unresolved conflict rather than mere low
   confidence.
4. Escalate it the way this repository turns an open question into a decision: a `type:adr`
   issue parented to the PRD that raised it, with the decision outcome left blank. **Agents
   draft decisions; they do not make them.** Choosing between two accepted records is
   making one.

**Enforcement of this is deferred, and that matters.** No check compares two decisions, and
the checker treats the flagged status exactly as it treats any other — a flagged node
validates green. Encoding claim-type classification and the flagged state in the schema and
checker is [#1410][i1410]'s work, not this node's. Until it lands, everything in this
section is an authoring convention held by an author and a reviewer, and nothing will raise
it for you.

## When a cited decision is superseded

Superseding does not edit the old record. It stays on disk, its `status` becomes
`Superseded by ADR-YYYY`, and the new record names what it replaced —
`ADR-0050` and the five records it superseded are the worked example in this repository.

**So a citation to a superseded record does not break. It goes quietly wrong.** The path
still resolves, the checker still passes it, and the only thing that changed is the meaning
of citing it.

When a decision a node cites is superseded, re-read the claim against the **superseding**
record and take one of three routes:

| What the new record does to the claim | What the node does |
|---|---|
| Says the same thing | Move the citation to the new record. The claim is unchanged. |
| Changes what is authorized | The claim is now wrong. Update the claim and the citation **in the same edit** — a body updated without its ledger, or the reverse, is how the two drift apart. |
| Does not reach it — the claim is genuinely about what *was* authorized then | Keep the superseded citation, and say in the `statement` that the record is superseded and why it is still the right source. |

The third route is the only one that leaves a superseded citation in place, and it is only
available to a claim that is explicitly historical.

## What the checks establish, and what they do not
## Enforcement, and what the checks establish

The checker's verdict on a decision citation is **structural**. A repository path — bare,
or carrying a line position — is resolved, and must be a real file inside the repository;
the file is never opened, and a line position's number is never compared against the
file. From that, four consequences follow, and all four are load-bearing:

1. **It cannot tell an accepted record from a proposed or superseded one.** Every ADR path
   under `launchpad/decisions/` looks identical to it.
2. **It cannot tell whether the record says what your `statement` says.** A `FACT` citing a
   real decision that is silent on the subject passes cleanly.
3. **It cannot tell an intent claim from a behaviour claim**, so it cannot tell that a
   decision is the wrong evidence for the claim it sits under.
4. **It cannot tell that two cited decisions contradict each other.** It compares no two
   records, and it never reads a node's `status`, so a node flagged for an unresolved
   conflict and a node asserting a settled answer validate identically.

The repository's separate automated ADR check does not close any of this: it is scoped to
one ADR's sanctioned-file list and reads no other record's front matter.

**Every MUST in this node is therefore held by a human reviewer.** A reviewer checking a
node that cites `launchpad/decisions/`:

- opens each cited record and reads its front-matter `status` (MUST 4);
- confirms the claim is an intent claim, not a behaviour claim in intent clothing
  (MUSTs 1 and 2), and that an authorization claim does not cite the issue instead of the
  record (MUST 1);
- confirms the record's **Decision** section supports an authorization `statement`, and
  that a claim drawn from any other section is worded as the kind of claim it is (MUST 5);
- confirms **two cited decisions do not contradict each other**, and that where they do
  the node records both and picks neither (MUST 6). Nothing else will catch this, and it
  is the failure ADR-0029 calls a security concern;
- confirms a superseded intent citation says it is superseded and why it stands (MUST 7);
- confirms no decision citation carries a line position (MUST 3). The checker accepts
  one — it checks the path and ignores the number — so MUST 3 is unenforced too.

A green validation run answers none of these questions and does not claim to.

## Exceptions and escalation

There is **one standing exception** to the accepted-status rule in MUST 4: a claim that is
explicitly *about* a proposed or superseded decision — its existence, its content, or the
fact that it is pending — may cite that record, because the record's own state is the
subject. The `statement` must say so. A claim about what is authorized *today* never
qualifies.

**An exception lives in the evidence `statement`, and nowhere else.** Node front matter
rejects any field the schema does not name, so there is no exception field to add and no
place to hide one.

**Anything else is escalated, not invented.** A situation these rules do not cover is an
open question, and this repository has one route for those: a `type:adr` issue parented to
the PRD that raised it, argued in the issue, decided by a human, and written up as a record
in the pull request that closes it. Do not resolve it in a node's body and do not widen this
standard by precedent.

## Scope and omissions

**This node covers** which claims a decision record may be cited for, how to cite one, what
to do when two accepted decisions conflict, what to do when a cited decision is superseded,
what the deterministic check does and does not establish about any of that, and the one
standing exception.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| Citing code, tests, config and schema | [#1308][i1308] |
| The general evidence contract and how classes are chosen | [#1314][i1314] |
| Deprecating or retiring a **corpus node** — distinct from superseding a decision | [#1311][i1311] |
| Encoding claim type and the flagged state in the schema and checker | [#1410][i1410] |
| Fixing the unverified line number itself, for citations generally | [#1459][i1459] |
| Whether a non-accepted record may be cited as *context* generally | [#1314][i1314] |
| How a specification becomes "ratified" | Undefined in this repository — see below |

**Two boundaries worth naming explicitly**, because this node settles a slice of each:

- MUST 3 closes the line-position gap **for decision citations only**, by prohibition. It
  does not close it anywhere else, and [#1459][i1459] still owns making the number
  verifiable rather than merely forbidden.
- The standing exception above settles when a proposed or superseded record may be cited
  **for a claim about that record**. Whether such a record may be cited as *context* for
  some other claim is [#1314][i1314]'s, and this node deliberately does not answer it. If
  #1314 rules differently, it supersedes the exception rather than sitting beside it.

**No `relationships` in this node's front matter.** None of the sibling standards this node
would point at exist yet, and a `relationships[].target` naming an id no node carries is a
hard validation error, so declaring none is the correct answer rather than an oversight.
Do not take that on this document's word — `ls launchpad/docs/corpus/standards/` is the
check. Edges belong in a follow-up once the standards have landed.

**Expected but not verified when this node was written**, per the rule in *Creating a node*
step 3 of `launchpad/docs/corpus/AGENTS.md`:

- **No node anywhere carries the flagged status.** The conflict procedure above is written
  from the schema's own description of that status and from ADR-0029, never from a worked
  instance. The first real conflict will test it.
- **No ratified specification was found to check against.** ADR-0029 grants intent
  authority to accepted decisions and ratified specifications together, but nothing in this
  repository defines how a specification becomes ratified, and the nearest candidate —
  `launchpad/project-intelligence/CONTRACT.md` — describes itself as proposed and not
  ratified. Until that is settled, a decision record's `status` field is the only evidence
  of accepted status this standard can actually ask an author to read.
- **No author or harness has applied this standard.** Whether the MUST list is followable
  in practice, rather than merely correct, is untested.

[i1308]: https://github.com/launchpad-26/buzz/issues/1308
[i1311]: https://github.com/launchpad-26/buzz/issues/1311
[i1314]: https://github.com/launchpad-26/buzz/issues/1314
[i1410]: https://github.com/launchpad-26/buzz/issues/1410
[i1459]: https://github.com/launchpad-26/buzz/issues/1459

---
id: corpus-standard-normative-language
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 919886b4192df6251de50c547548ecae5d85afce."
    entry_class: FACT
    evidence:
      - "commit 919886b4192df6251de50c547548ecae5d85afce"
  - statement: "RFC 2119 defines MUST, REQUIRED and SHALL to mean that the definition is an absolute requirement of the specification, and defines MUST NOT and SHALL NOT to mean that the definition is an absolute prohibition of the specification."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
  - statement: "RFC 2119 defines SHOULD and RECOMMENDED to mean there may exist valid reasons in particular circumstances to ignore a particular item, but the full implications must be understood and carefully weighed before choosing a different course, and defines SHOULD NOT and NOT RECOMMENDED to mean there may exist valid reasons in particular circumstances when the particular behavior is acceptable or even useful, but the full implications should be understood and the case carefully weighed before implementing any behavior described with that label."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
  - statement: "RFC 2119 defines MAY and OPTIONAL to mean an item is truly optional, illustrated by one implementation choosing to include an item while another omits the same item with no compliance consequence either way."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
  - statement: "RFC 2119 states that its keywords must be used with care and sparingly, and MUST only be used where actually required for interoperation or to limit behavior with potential for causing harm, not to impose a particular method where the method is not required for interoperability."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc2119"
  - statement: "RFC 8174 clarifies RFC 2119 by stating that when its keywords are not capitalized they have their normal English meanings and are not affected by that document, and that the defined meanings apply only when the words are in all capitals."
    entry_class: FACT
    evidence:
      - "https://www.rfc-editor.org/rfc/rfc8174"
  - statement: "Four accepted decision records in this repository -- ADR-0047, ADR-0048, ADR-0049 and ADR-0050 -- state requirements using MUST, MUST NOT and MAY, and none of the four defines or cites a source for what those words mean."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0047-standing-divergence-ledger.md"
      - "launchpad/decisions/ADR-0048-upstream-content-containment.md"
      - "launchpad/decisions/ADR-0049-project-memory-community-store.md"
      - "launchpad/decisions/ADR-0050-canonical-corpus-supersedes-handbook.md"
  - statement: "The two existing corpus standards each separate MUST-class statements from SHOULD-class statements, but under two different heading conventions: corpus-standard-confidence uses the headings '## Requirements' (introduced by the prose 'These are MUSTs') and '## Guidance' (introduced by 'These are SHOULDs'), while corpus-standard-decision-references uses the literal headings '## MUST' and '## SHOULD'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "No file under launchpad/docs/corpus or launchpad/decisions defines what MUST, MUST NOT, SHOULD, SHOULD NOT or MAY mean in this repository, or requires them to be capitalized, and the repository's only existing mention of RFC 2119 is in launchpad/Research/493-otel-instrumentation-best-practices.md, which defines a distinct, OpenTelemetry-specification-scoped sense of 'normative requirement' unrelated to corpus or decision-record authoring."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='RFC 2119|RFC2119', scope='launchpad/') -> 1 match, launchpad/Research/493-otel-instrumentation-best-practices.md:52"
  - statement: "node.schema.json has no field governing normative-keyword capitalization, closed-set membership, or MUST/SHOULD separation, and validate.py contains no check matching the words MUST, SHOULD, MAY or 'normative'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The exact lowercase spellings 'must', 'should' and 'may' appear as ordinary English words, not as normative keywords, throughout already-merged corpus documents alongside their capitalized normative use: launchpad/docs/corpus/AGENTS.md, launchpad/docs/corpus/standards/confidence.md and launchpad/docs/corpus/standards/decision-references.md contain 11, 15 and 11 such lowercase occurrences respectively, and AGENTS.md additionally contains one title-case 'Must' that is likewise ordinary English rather than a normative keyword."
    entry_class: FACT
    evidence:
      - "grep_word_count(pattern='\\bmust\\b|\\bshould\\b|\\bmay\\b', case_sensitive_exact_lowercase=true, files=['launchpad/docs/corpus/AGENTS.md', 'launchpad/docs/corpus/standards/confidence.md', 'launchpad/docs/corpus/standards/decision-references.md']) -> 11, 15, 11 respectively"
  - statement: "launchpad/Research/493-otel-instrumentation-best-practices.md defines a 'Normative OTel requirement' as an RFC 2119/8174 requirement in the versioned OpenTelemetry specification that becomes a Buzz requirement only when Buzz adopts or implements that surface -- an existing worked case in this repository of an external specification's own MUST needing to stay distinguished from a requirement this repository imposes."
    entry_class: FACT
    evidence:
      - "launchpad/Research/493-otel-instrumentation-best-practices.md"
  - statement: "launchpad/AGENTS.md describes itself, in its opening section, as 'the normative spec for how work is filed, reviewed and merged in this fork' -- a use of 'normative' describing a whole document's authority, distinct from the RFC 2119 sense of one keyword-marked requirement that this node governs."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "launchpad/AGENTS.md's issue-type decision tree classifies an issue as an ADR only when its output is a decision plus rationale with nothing in the repository changing when it closes."
    entry_class: FACT
    evidence:
      - "launchpad/AGENTS.md"
  - statement: "Because this task's own output is a corpus document -- something in the repository that changes when the issue closes -- rather than a decision with nothing else moving, adopting RFC 2119 as this document's normative-keyword vocabulary is this document's own authored content and not a decision that required a separate ADR first; a future ADR addressing normative-keyword usage differently would supersede this document's choice rather than this document needing to have waited for one."
    entry_class: INFERENCE
    evidence:
      - "launchpad/AGENTS.md"
    confidence: 0.8
  - statement: "Issue #1320 requires this node to state the scope and authority/source of the policy, separate MUST requirements from SHOULD guidance, define an enforcement/checks and exception/escalation process, and link to decisions or higher-order policy rather than duplicating them."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1320 definition of done"
relationships:
  - type: references
    target: corpus-agents
  - type: references
    target: corpus-standard-confidence
  - type: references
    target: corpus-standard-decision-references
---

# Standard: normative language (MUST / SHOULD / MAY)

What the keywords MUST, MUST NOT, SHOULD, SHOULD NOT and MAY mean when they appear
in a corpus node or a decision record in this repository, how they must be written,
and what "normative" does and does not mean here.

This is a policy node. Look up the section you need.

## Scope and authority

**This node governs** how MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are spelled,
capitalized and used to phrase a requirement inside a hand-authored corpus node
(`launchpad/docs/corpus/`) or decision record (`launchpad/decisions/`) in this
repository. It does not govern the same words used as ordinary English in
descriptive prose — see *What "normative" means here*, below.

**Its authority is external, not an existing accepted decision.** This document
adopts [RFC 2119][rfc2119], clarified by [RFC 8174][rfc8174], as the source of the
definitions below — the industry-standard vocabulary for exactly this purpose, and
the same vocabulary four accepted decision records and both existing corpus
standards already use without ever citing where it comes from (see the evidence
ledger). **No accepted decision in this repository currently governs
normative-keyword usage.** Unlike `corpus-standard-confidence` and
`corpus-standard-decision-references`, which sit under `ADR-0029`, this document is
not a restatement of an existing ADR — it is the first place this repository states
the rule at all. If a future ADR addresses normative-keyword usage differently, that
ADR supersedes this document's choice, and this document's `status` would move to
`retired` with a `supersedes`-carrying successor, per the retiring procedure in
`launchpad/docs/corpus/AGENTS.md`.

| For | Read |
|---|---|
| The formal source this document adopts | [RFC 2119][rfc2119], clarified by [RFC 8174][rfc8174] |
| Creating, updating and retiring a corpus node | `launchpad/docs/corpus/AGENTS.md` |
| The front-matter contract | `launchpad/docs/corpus/schema/node.schema.json` |
| Two worked examples of a corpus document separating MUST from SHOULD | `launchpad/docs/corpus/standards/confidence.md`, `launchpad/docs/corpus/standards/decision-references.md` |
| The decision-record lifecycle | `launchpad/decisions/README.md` |
| How evidence is classified and cited | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` |

If this file and any of those disagree, **they win** — this one has drifted and
should be fixed.

### What "normative" means here

"Normative" is already used in this repository in a broader sense than the one this
node governs: `launchpad/AGENTS.md` calls itself "the normative spec for how work is
filed, reviewed and merged in this fork," meaning the whole document is authoritative
and supersedes conflicting guidance. This node's subject is narrower — the specific
keyword vocabulary (MUST, SHOULD, MAY, and their variants) used to mark one sentence
as a binding requirement rather than descriptive prose. A document can be normative in
the broad sense — `AGENTS.md` plainly is — without using a single RFC 2119 keyword;
`AGENTS.md` and `launchpad/docs/corpus/README.md` both contain zero capitalized
instances of MUST, SHOULD or MAY at the recorded revision. This document does not
require every normative document to adopt RFC 2119 phrasing; it governs the documents
that already do, or that choose to going forward.

## What the keywords mean

The definitions below are [RFC 2119][rfc2119]'s, quoted and clarified by
[RFC 8174][rfc8174]. Both are external, non-GitHub URLs, so a citation to either
resolves `UNVERIFIED` under this repository's checker — expected, per
`launchpad/docs/corpus/AGENTS.md`'s citation-shape table, and not the same as
unchecked: these quotations were fetched and read against the live RFC text, not
copied from memory or from a secondary source.

| Keyword | RFC 2119's meaning |
|---|---|
| **MUST** / REQUIRED / SHALL | "the definition is an absolute requirement of the specification" |
| **MUST NOT** / SHALL NOT | "the definition is an absolute prohibition of the specification" |
| **SHOULD** / RECOMMENDED | "there may exist valid reasons in particular circumstances to ignore a particular item, but the full implications must be understood and carefully weighed before choosing a different course" |
| **SHOULD NOT** / NOT RECOMMENDED | "there may exist valid reasons in particular circumstances when the particular behavior is acceptable or even useful, but the full implications should be understood and the case carefully weighed before implementing any behavior described with this label" |
| **MAY** / OPTIONAL | "an item is truly optional" — one author may include it, another may omit it, with no compliance consequence either way |

**Only the fully capitalized spelling carries this meaning.** RFC 8174 is explicit:
lowercase "must," "should" and "may" "have their normal English meanings and are not
affected by this document," and the defined meanings apply "only when they are in
all capitals." This repository already relies on that distinction whether or not it
names it — `launchpad/docs/corpus/AGENTS.md`, `confidence.md` and
`decision-references.md` each use the lowercase spellings more than ten times as
ordinary English, sitting a few lines from their capitalized, binding use of the
same words. Nothing before this document said the two were different in kind.

**REQUIRED, SHALL, SHALL NOT, RECOMMENDED, NOT RECOMMENDED and OPTIONAL are
RFC 2119's synonyms** for MUST, MUST NOT, SHOULD, SHOULD NOT, SHOULD NOT and MAY
respectively. None of them appears anywhere in this repository's corpus or decision
documents today — see *Guidance*, below, for what that means for a new document.

## MUST

These bind every corpus node and decision record in this repository that uses these
keywords at all. Enforcement is described in full, honestly, in *Enforcement, and
where it stops* — most of this list is not checked by anything mechanical.

1. A statement intended to bind an author or a reviewer of this repository's own
   corpus or decision documents **MUST** use one of MUST, MUST NOT, SHOULD, SHOULD
   NOT or MAY, written in full capitals. A lowercase or partially capitalized
   spelling **MUST NOT** be relied on to carry that meaning — per RFC 8174, it will
   not.
2. A capitalized keyword from that set **MUST NOT** be used to state or imply an
   obligation this repository is not actually imposing. In particular, quoting or
   paraphrasing a requirement from an external specification — an IETF RFC, the
   OpenTelemetry specification, or similar — **MUST** be visibly attributed to that
   source (by name, in the surrounding sentence or in a citation) and **MUST NOT**
   be phrased as though this repository's own process required it.
   `launchpad/Research/493-otel-instrumentation-best-practices.md`'s "Normative OTel
   requirement" is the existing worked case this rule is written from: an
   OpenTelemetry MUST becomes a Buzz requirement only when Buzz adopts that surface,
   and the document says so rather than letting the OTel MUST read as Buzz's own.
3. Lowercase and mixed-case spellings of "must," "should" and "may" carry their
   ordinary English meaning only. An author or reviewer **MUST NOT** treat one as
   expressing a requirement of a document governed by this standard, and **MUST
   NOT** write one where a binding requirement is actually intended.
4. A document that states requirements under both MUST-class and SHOULD-class
   keywords **MUST** separate the two classes so a reader can tell, without reading
   every sentence, which class a given statement belongs to. A MUST and a SHOULD
   **MUST NOT** sit together in one undifferentiated list. Requirement 4 does not
   prescribe a single heading style — see *Guidance* for the two already in use.
5. A corpus node or decision record introducing a new normative-keyword convention
   for this repository — a new keyword, a new capitalization rule, or a new
   synonym not named above — **MUST NOT** do so silently. It **MUST** amend this
   document in the same change, or supersede it outright per
   `launchpad/docs/corpus/AGENTS.md`'s retiring procedure. A second, unreconciled
   normative-language convention would leave a reader with no way to know which
   document's rule a given MUST answers to.

## SHOULD

These are guidance. Depart from them with a stated reason; nothing blocks a merge
over any of them.

- **New normative prose SHOULD use MUST, MUST NOT, SHOULD, SHOULD NOT and MAY, and
  SHOULD NOT introduce their RFC 2119 synonyms** (REQUIRED, SHALL, SHALL NOT,
  RECOMMENDED, NOT RECOMMENDED, OPTIONAL). Both spellings are equally valid under
  RFC 2119; the reason to prefer one is that this repository has, so far, used only
  one, and a second spelling for the same meaning is a convention a reader has to
  learn for no benefit. If a synonym is ever genuinely needed, extend this document
  first rather than letting the two coexist unremarked.
- **A normative keyword SHOULD be bolded in running prose** (`**MUST**`,
  `**SHOULD NOT**`) so it is visually distinguishable from the surrounding sentence.
  Both existing corpus standards already do this; nothing checks it, and an
  unbolded keyword is still binding under Requirement 1 as long as it is
  capitalized.
- **Keywords SHOULD be used sparingly, reserved for statements a reviewer can
  actually check.** This restates RFC 2119's own restraint principle: imprecise or
  decorative use of MUST erodes the signal a reader relies on when scanning a long
  document for the handful of sentences that actually bind them. This is guidance,
  not Requirement 1's bright line, because "sparingly" has no bright line to
  enforce.
- **A statement's scope SHOULD be named when it is not obvious from the heading or
  surrounding paragraph** — "every corpus node," "this node only," "every decision
  record" are different reaches, and a bare MUST whose reach is ambiguous is
  difficult for a reviewer to check.
- **A new document SHOULD reuse one of the two heading conventions already in this
  repository** for separating MUST from SHOULD — `confidence.md`'s
  `## Requirements` / `## Guidance` framing, or `decision-references.md`'s literal
  `## MUST` / `## SHOULD` headings — rather than inventing a third. Either already
  satisfies Requirement 4; this document uses the literal-heading form because its
  own subject is these two words, and a heading that names the class directly is
  the more legible choice for a document about exactly this. That is a reason for
  this document's own choice, not a claim that it is the better convention in
  general — no evidence here compares the two for legibility, and neither existing
  standard is asked to change.

## This document, held to its own rule

The issue that requested this node asked, explicitly, whether its own structure
demonstrates the convention it prescribes rather than merely stating it. Checked
against the MUST list above:

- **Requirement 1** — every normative keyword in this document is one of MUST, MUST
  NOT, SHOULD or MAY, in full capitals. SHOULD NOT does not appear as a keyword here
  because no statement in this document needed it.
- **Requirement 2** — the RFC 2119 quotations in *What the keywords mean* are
  presented as a table of "RFC 2119's meaning," attributed by name and citation, not
  phrased as this document's own MUST list; the two are visually and structurally
  separate.
- **Requirement 3** — this document's own MUST and SHOULD items do not rely on a
  lowercase "must" or "should" to carry weight; where the prose uses those words
  lowercase (for example, in this sentence), it is ordinary English, consistent with
  Requirement 3 itself.
- **Requirement 4** — MUST-class and SHOULD-class statements sit under two
  literal, separate headings, `## MUST` and `## SHOULD`, with no item shared between
  them.
- **Requirement 5** — this document introduces no keyword, capitalization rule or
  synonym beyond the set RFC 2119 already defines and *What the keywords mean*
  already states.

## Enforcement, and where it stops

**Enforced mechanically: nothing.** `node.schema.json` has no field for
normative-keyword usage, and `validate.py` has no check matching MUST, SHOULD, MAY
or "normative" — confirmed by reading both files at the recorded revision, not by
their absence from a summary. A corpus node or decision record that violates every
requirement above still passes `python3 launchpad/project-intelligence/corpus/validate.py`
cleanly.

**Enforced by review, in full:**

| Requirement | What a reviewer checks |
|---|---|
| 1, 3 | The keyword is one of the closed set, in full capitals; a lowercase "must"/"should"/"may" nearby is read as English, not as a requirement |
| 2 | A quoted or paraphrased external MUST is attributed to its source and not phrased as this repository's own |
| 4 | MUST-class and SHOULD-class statements are visibly separated |
| 5 | No new keyword, capitalization rule or synonym was introduced without amending this document |

**Not enforced by anything, and this document does not invent a check for it:**
whether a keyword was used sparingly, per RFC 2119's own restraint principle in
*Guidance*. That judgment has no bright line; a reviewer's discretion is the only
mechanism, exactly as it is for the confidence values `corpus-standard-confidence`
governs.

## Exceptions and escalation

**One standing exception to Requirement 2's attribution rule:** a quotation of an
external specification's own keyword set inside a Markdown blockquote or fenced code
block, immediately accompanied by a citation to that specification, satisfies
Requirement 2 without a separate attribution sentence — the quotation marks and the
citation together are the attribution. The table in *What the keywords mean* above
relies on exactly this: it is introduced as "RFC 2119's meaning," not phrased as a
requirement of this repository.

**There is no exception process for the structural requirements**, because there is
no mechanical enforcement to except from — every requirement above is held by
review, and a reviewer may always ask an author to fix a violation before merge.

**When a reviewer and an author disagree** about whether a statement should be a
MUST or a SHOULD, whether an attribution is adequate under Requirement 2, or which
document's normative-language rule a shared subject falls under, escalate the way
this repository escalates any open question it cannot resolve in the moment: file a
`type:adr` issue parented to the PRD that raised it (`launchpad/AGENTS.md` §4),
argue it there, and let a human decide. **Agents draft; they do not decide.** Do not
resolve the disagreement by silently editing this document's MUST list, and do not
widen this document's scope by precedent from one contested case.

## Scope and omissions

**This document covers** what MUST, MUST NOT, SHOULD, SHOULD NOT and MAY mean in
this repository's corpus and decision documents, where that meaning comes from, how
a keyword must be written and used, how MUST is to be kept separate from SHOULD, and
what enforcement does and does not reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The evidence-entry classes (FACT, INFERENCE, TEAM_KNOWLEDGE), their required fields, and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md`, and the evidence standard, #1314 |
| The `confidence` field's meaning and requirements | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Per-type templates and standards for other corpus node kinds | #1307–#1351, none merged at the recorded revision |
| Whether `launchpad/decisions/` ADR authoring is formally bound by a corpus standard, as opposed to a corpus node being formally bound by one | Unsettled — see below |

**This standard's home is the corpus, and its reach into `launchpad/decisions/` is
recommendation, not authority.** `launchpad/decisions/README.md` owns the ADR
lifecycle and does not name this document. The evidence above shows four ADRs
already using this exact keyword set, which is why *Guidance* and *Enforcement*
speak to decision records too — but nothing in `launchpad/decisions/README.md`
currently defers to `launchpad/docs/corpus/`, so an ADR author who departs from this
document's MUST list is not violating a rule that document has adopted. Making that
binding, if it is wanted, is a change to `launchpad/decisions/README.md` or a new
ADR, not something this corpus node can reach into on its own.

**`references` relationships, and how they were checked.** This node declares three:
`corpus-agents` (the corpus's node-creation authority, which this document sits
under the same way both existing standards do), `corpus-standard-confidence` and
`corpus-standard-decision-references` (the two worked examples this document reads
directly, cites for their heading conventions, and holds itself against in
*Guidance*). All three are `references` because this document cites each as
supporting context without asserting ownership over it or a currency dependency on
it. Verified immediately before finalizing this front matter, not from memory:

```
git fetch origin launchpad
git ls-tree -r --name-only origin/launchpad -- launchpad/docs/corpus
```

At the time this was run, `origin/launchpad`'s corpus tree contained exactly four
authored nodes — `launchpad/docs/corpus/AGENTS.md` (`corpus-agents`),
`launchpad/docs/corpus/README.md` (`corpus-readme`),
`launchpad/docs/corpus/standards/confidence.md` (`corpus-standard-confidence`) and
`launchpad/docs/corpus/standards/decision-references.md`
(`corpus-standard-decision-references`) — the same set present when this batch was
dispatched. No relationship above targets a sibling from this same five-document
batch (generated-content, identifiers, naming, status), because none of those had
merged into `launchpad` when this check ran, and a `relationships[].target` naming an
id no node on the merge-target branch carries is a hard validation error there even
if it resolves in this worktree. `corpus-readme` was read and considered, but no
claim in this document rests on it, so no edge to it is declared.

**Expected but not verified when this node was written:**

- **Requirement 2's attribution rule has not been applied against a real corpus
  node or decision record that quotes an external specification.**
  `launchpad/Research/493-otel-instrumentation-best-practices.md` is a Research
  document, not a corpus node or an ADR, so it is the rule's motivating precedent,
  not a tested application of this standard inside the tree this standard actually
  governs.
- **The RFC 2119 and RFC 8174 quotations above were retrieved with an automated
  fetch-and-summarize tool, not read character-by-character against the published
  RFC text by a human or by this document's author line by line.** The quoted
  passages are the well-known, stable definitional sentences from both documents
  and were cross-checked against that tool's extraction, but a full independent
  read of either RFC's complete text was not performed.
- **No harness or generated view was tested for whether it treats MUST/SHOULD/MAY
  case-sensitively for any tooling purpose.** No such tooling exists in this
  repository today; this document's requirements are held by human and agent
  reviewers, not by any parser.
- **Whether `launchpad/decisions/README.md` should be amended to defer to this
  document is not decided here.** *Scope and omissions*, above, states the gap;
  resolving it is an open question for whoever owns that file next, escalated the
  normal way if it is contested.

[rfc2119]: https://www.rfc-editor.org/rfc/rfc2119
[rfc8174]: https://www.rfc-editor.org/rfc/rfc8174

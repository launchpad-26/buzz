---
description: Research into reviewing terminology and conceptual consistency in the Buzz documentation corpus.
tags: [documentation, corpus, terminology, concepts, definitions, vocabulary, consistency, research]
---

# Terminology and conceptual consistency

Researched 2026-09-07. This is research, not an adopted corpus standard.

## Research question

How should Buzz determine whether important concepts have stable, usable meanings and
traceable names across documentation, code, user interfaces, protocols, and audiences,
without erasing legitimate domain-specific vocabulary?

The investigation considered ten subquestions:

1. What is the difference between a concept, its term, its definition, and its stable
   identifier?
2. Which kinds of consistency matter beyond spelling and capitalization?
3. When should one preferred term be enforced, and when are alternate terms legitimate?
4. How should homonyms, synonyms, abbreviations, jargon, and overloaded terms be handled?
5. What makes a definition precise enough to guide readers and reviewers?
6. How should concepts be related to one another and mapped across product, code,
   protocol, and operational vocabularies?
7. How should terminology changes, deprecations, and compatibility constraints be
   recorded?
8. Which terminology checks can be automated, and which require domain judgment?
9. What evidence would show that terminology helps readers rather than merely satisfying
   a word list?
10. What does the current Buzz corpus make easy or difficult to establish?

## Bottom line

Terminology quality is not uniform wording by itself. It is the reader's ability to
identify the intended concept, distinguish it from neighboring concepts, find its
definition, recognize its other legitimate labels, and follow it across system surfaces
and over time.

The strongest practical model is **concept-first**:

> **Mention in context → stable concept identity → preferred or admitted label for that
> scope → definition and boundary → relationships to other concepts → mappings to code,
> UI, and protocol names → lifecycle and provenance.**

This model resolves two rules that otherwise appear contradictory:

- Within a declared language and scope, use one preferred label for one concept wherever
  doing so improves recognition, search, translation, and maintenance.
- Across genuinely different audiences or system surfaces, do not force one label when
  the product, code, protocol, or profession has a legitimate established term. Preserve
  the labels and map them explicitly to the concept.

“One term, one concept” is therefore a useful local authoring rule, not a universal ban on
homonyms. “One concept, one written form” is also too strong: a concept may need a full
form and acronym, a product label and code identifier, or current and deprecated terms.
The consistency target is stable identity and explicit mapping, not a corpus in which
every surface uses identical text.

A glossary is a useful reader-facing projection, but it is not by itself a terminology
control system. A controlled terminology record needs enough structure to distinguish a
concept from its labels and to represent scope, alternative or deprecated labels,
definitions, relations, mappings, provenance, and change. Buzz need not adopt RDF, SKOS,
or TBX to use this design lesson.

The current corpus has good foundations: permanent node identifiers, a naming standard,
a glossary-term template, a concept template, and several documents that explicitly
disambiguate overloaded words. It does not yet have an observable glossary-term instance,
a concept-oriented terminology schema, semantic relations between terms, or mechanical
enforcement of prose-level terminology. Its active naming standard also selects
“provenance ledger” while the corpus body predominantly says “evidence ledger.” This is
evidence of incomplete lexical convergence, not proof that either phrase is conceptually
wrong.

## Scope and method

This report concerns vocabulary that carries technical or project-specific meaning:
product concepts, architecture elements, protocol concepts, operational terms, role
names, document-governance terms, abbreviations, and labels exposed in code or interfaces.
It considers both individual documents and consistency across the corpus.

It does not:

- create or approve a Buzz glossary or terminology database;
- decide which existing label should win in every conflict;
- prescribe RDF, SKOS, TBX, or an ontology implementation;
- require ordinary dictionary words to become corpus concepts;
- treat every repeated filename or word as a defect;
- redesign the corpus schema or templates;
- conduct a full manual term-by-term audit; or
- introduce LLM-specific controls, which remain set aside for this research sequence.

Local inspection covered all 205 Markdown nodes under `launchpad/docs/corpus/` with
`schema/` excluded, the active naming, taxonomy, identifier, and status standards, the
glossary-term and concept templates, the node and relationship schemas, and representative
documents that qualify or map overloaded terms. Counts came from read-only structural and
case-insensitive lexical scans of the current working tree. Lexical matches can identify
review candidates; they cannot establish intended meaning.

External sources were selected in this order:

1. ISO terminology standards and public ISO terminology-entry guidance;
2. the W3C SKOS Recommendation as a concept-oriented knowledge-organization model;
3. W3C accessibility guidance for unusual words and glossaries;
4. current Microsoft and Google technical-writing guidance;
5. Vale's official description of deterministic prose linting; and
6. a systematic mapping study of controlled vocabularies in requirements engineering.

The complete normative texts of ISO 704, ISO 1087, ISO 860, and ISO 30042 were not
publicly accessible during this research. Claims about them are limited to ISO's public
abstracts, lifecycle metadata, and public ISO schema guidance. ISO 30042:2019 is currently
published but marked “to be revised,” so it is evidence of a mature terminology-resource
model rather than a recommendation to freeze Buzz to that edition.

## Core distinctions

### A concept is not its term

[ISO 704:2022](https://www.iso.org/standard/79077.html) describes terminology work as
linking objects, concepts, definitions, and designations. [ISO 1087:2019](https://www.iso.org/standard/62330.html)
supplies the basic vocabulary for that work. The practical distinction for documentation
review is:

| Element | Review meaning | Example shape |
|---|---|---|
| Object or referent | The thing or state in the world or system | a running relay process |
| Concept | The unit of knowledge used to reason about a class of objects | relay process liveness |
| Designation | A sign used to represent a concept | a term, proper name, symbol, or code |
| Term or label | A linguistic designation | “liveness” or “relay process liveness” |
| Definition | A statement that identifies the concept and distinguishes it from neighbors | what condition counts as live, and what does not |
| Identifier or notation | A stable, often machine-oriented reference independent of display wording | a corpus node ID or classification code |

This separation prevents two common mistakes. Renaming a term does not necessarily change
the concept, and reusing the same word does not prove that two documents mean the same
concept. Stable concept identity lets wording evolve without silently changing meaning.

The [W3C SKOS Recommendation](https://www.w3.org/TR/2009/REC-skos-reference-20090818/)
provides a concrete example: concepts have URI identities separate from lexical labels;
they may have preferred, alternative, and hidden labels, notations, definitions, scope
notes, history and change notes, semantic relations, and mappings to other concept schemes.
Buzz can borrow that separation without adopting SKOS's serialization.

### A glossary, termbase, concept scheme, and ontology solve different problems

| Artifact | Primary job | What it does not establish by itself |
|---|---|---|
| Word list or style sheet | Prescribe spelling, capitalization, and allowed or discouraged forms | concept identity or definition correctness |
| Glossary | Let readers look up short definitions | complete synonym, relationship, mapping, and lifecycle control |
| Terminology record or termbase | Manage concepts, labels, definitions, status, sources, and reuse | formal axioms about the domain |
| Concept scheme, taxonomy, or thesaurus | Organize concepts through hierarchy and association | necessarily prove facts about how the world works |
| Ontology | Represent formal classes, properties, constraints, and axioms | reader-friendly terminology guidance automatically |

SKOS explicitly positions itself as a semi-formal knowledge-organization model, not a
formal knowledge-representation language. [ISO 30042:2019](https://www.iso.org/standard/62510.html)
defines a metamodel and data categories for exchanging terminology resources used in
authoring and translation. These are useful reference models, but adopting either in full
would be a separate architecture decision requiring demonstrated need.

Buzz's glossary-term template already recognizes part of this boundary: it defines a
short lookup document and deliberately excludes the richer fields of a terminology
system. That is coherent as a document-type decision. It becomes a corpus-level gap if no
other structure records the excluded relationships and label mappings.

## Six dimensions of consistency

Terminology review should name the dimension being tested. Otherwise a spelling scan and
a conceptual review collapse into one vague verdict.

| Dimension | Review question | Typical defect | Useful evidence |
|---|---|---|---|
| Lexical | Is the permitted label spelled, cased, hyphenated, and pluralized consistently in this scope? | `front matter`, `front-matter`, and `frontmatter` used without a grammatical rule | word list, exact scan, style lint |
| Referential | Does each mention point to the intended concept? | “provider” could mean inference provider or compute provider | contextual qualification, links, stable IDs |
| Definitional | Do authoritative definitions express compatible essential meaning and boundaries? | two nodes give incompatible conditions for “live” | side-by-side definition and evidence review |
| Relational | Are broader, narrower, part-whole, related, and disjoint concepts represented coherently? | a role is treated as both a community role and a channel role | concept map, relationship review, domain expert judgment |
| Cross-surface | Can the same concept be followed across product wording, UI labels, code identifiers, configuration, protocols, and operations? | UI says “community,” storage says “tenant,” with no mapping | source mappings and task-based trace |
| Lifecycle | Can readers tell which labels and meanings are current, admitted, deprecated, or replaced? | a renamed term disappears while code and old links still use it | status, replacement target, effective date, change note |

A document may be lexically inconsistent yet conceptually clear because it explicitly
maps two labels. It may be lexically uniform yet conceptually inconsistent because the
same word silently shifts meaning. Review conclusions should not infer one dimension from
the other.

## What good terminology control contains

### Stable concept identity

The terminology unit should be the concept, not the spelling. One record should describe
one concept; different meanings of the same word should be separate records. Public ISO
[terminology-entry guidance](https://www.iso.org/schema/isosts/v0.5/doc/tbx/ISO-TBX_xsd_Guidelines.html)
uses exactly this shape: one entry describes one concept, synonymous terms belong in that
entry, and multiple meanings of the same term belong in separate entries, normally with
different subject fields.

For Buzz, the existing permanent node `id` could help provide stable identity, but a node
ID is not automatically a concept ID. Some nodes document procedures, implementations, or
views of the same subject. A later design must decide whether a concept is a dedicated
node, an entity referenced by several nodes, or a limited hybrid. Filename equality is
not a safe substitute.

### Labels with declared roles and scope

A minimal controlled record should be able to distinguish:

- a preferred label for a declared language and scope;
- admitted or alternate labels that readers may encounter;
- deprecated labels and their replacement;
- abbreviations and their full forms;
- hidden search labels, if misspellings or legacy forms must remain findable; and
- code, UI, protocol, configuration, or external-standard designations.

SKOS allows no more than one preferred label per language tag and keeps preferred,
alternative, and hidden label roles disjoint. This is a useful integrity pattern, not a
requirement that every context display the same text. Scope might be the whole Buzz
product, the Nostr protocol, Rust code, mobile UI, or corpus governance. That scope must
be explicit before a “duplicate” can be judged.

Microsoft's [technical-term guidance](https://learn.microsoft.com/en-us/style-guide/word-choice/use-technical-terms-carefully)
advises “one term, one concept,” using established industry vocabulary and not inventing
a new term when one exists. Google's [style guide](https://developers.google.com/style)
adds the necessary qualification: project and audience clarity can justify a different
form, provided the choice stays consistent in its document or domain. Together these
support controlled preference with explicit exceptions, not global text replacement.

### Definitions with boundaries

A useful definition should let a reader identify the concept and distinguish it from the
closest likely confusion. For a technical corpus, review should ask whether it:

- states the concept's defining characteristics rather than only a purpose, example, or
  circular restatement;
- declares the domain or subject field in which the meaning applies;
- names relevant exclusions or nonexamples;
- differentiates neighboring and overloaded concepts;
- agrees with the authoritative product, protocol, code, or decision source;
- avoids adding requirements that belong in normative policy; and
- is short enough for lookup or deliberately links to a longer concept explanation.

Buzz's concept template is strong on scope, boundary, what a concept is not, use cases,
and comparisons. The glossary-term template is strong on a local, one-to-three-sentence
definition plus scope and omissions. The review problem is not primarily their prose
shape; it is the absence of instantiated, connected terminology records.

### Explicit concept relations and mappings

Concepts gain precision through their neighborhood. Useful relation types include:

- broader and narrower meaning;
- part and whole, when that relation is genuinely intended;
- associative “related” links;
- distinctions or incompatibilities that prevent category errors;
- exact and close mappings to concepts in another vocabulary; and
- the code, UI, protocol, or configuration designation that realizes or exposes the
  concept.

[ISO 860:2007](https://www.iso.org/standard/40130.html) treats harmonization as work on
concepts, concept systems, definitions, and terms, including multilingual contexts. SKOS
similarly separates internal semantic relations from mappings between concept schemes
and distinguishes exact from close matches. That distinction matters: “community” and
“relay tenant” may be usefully mapped without claiming that the words are interchangeable
in every product and infrastructure sentence.

Buzz's generic `references` relationship cannot currently carry this semantic load. Its
own schema says only that the source cites the target as supporting context, with no
ownership or currency dependency. Using it for synonymy, identity, hierarchy, or a close
mapping would hide the exact relationship a terminology review needs to inspect.

### Lifecycle and migration

Terminology changes should be treated as compatibility changes, not silent search-and-
replace exercises. A controlled change record should answer:

- What concept is affected: did only the label change, or did the meaning change too?
- Which label is preferred now, in which scope, and from what date or version?
- Which prior labels remain admitted, deprecated, searchable, or visible in old code?
- What is the replacement and migration path?
- Which documentation, UI, APIs, schemas, configuration, examples, and search aliases are
  affected?
- What evidence or decision authorized the change?

If an old term is embedded in an API, command, event field, or filename, exact technical
accuracy can require retaining it in code formatting while explaining the preferred
reader-facing term. Google's [jargon guidance](https://developers.google.com/style/jargon)
uses this pattern for legacy code terminology. Removing every old string can make current
instructions false and historical material undiscoverable.

## Reader access is part of terminology quality

Controlled terminology does not help if readers cannot reach the definition at the
moment of need. Google's current guidance recommends plain language where possible,
using audience-recognized jargon when it is valuable, and defining or linking unfamiliar
terms on first use. Its [global-audience guidance](https://developers.google.com/style/translation)
also connects stable terminology and capitalization to reduced ambiguity in translation.

WCAG 2.2's [Understanding 3.1.3](https://www.w3.org/WAI/WCAG22/Understanding/unusual-words.html)
explains why definitions of technical jargon and restricted usage matter, especially for
people with cognitive, language, or learning disabilities. It allows audience and context
to inform what counts as unusual. The criterion is Level AAA, and its documented
techniques are examples rather than mandatory implementations; it should inform a Buzz
quality review, not be misreported as a universal AA glossary requirement.

A glossary is one sufficient technique, not the only one. W3C's
[glossary technique G62](https://www.w3.org/WAI/WCAG22/Techniques/general/G62) warns that
a glossary with several definitions for the same item is insufficient when the page does
not guide the reader to the correct sense. Contextual qualification and concept-specific
links are therefore as important as building the glossary page.

## A review method for Buzz

### 1. Select concepts by risk, not word frequency alone

Prioritize terms whose ambiguity can change behavior, authority, data interpretation, or
reader action:

- security, identity, authorization, role, trust, and tenancy terms;
- protocol event, channel, thread, and community concepts;
- deployment, liveness, readiness, provider, backend, and environment concepts;
- normative corpus-governance vocabulary;
- UI labels that users must match to procedures; and
- terms that appear across three or more surfaces or have undergone a rename.

Frequency, capitalization variation, duplicate stems, acronym density, and search misses
are discovery signals. A rare term at a trust boundary can be more important than a
frequent harmless variant.

### 2. Build a concept card before judging wording

For each selected concept, record at least:

1. stable concept ID or an explicit temporary review key;
2. definition, domain, boundary, and nonexamples;
3. preferred label in the relevant language and scope;
4. admitted, abbreviated, hidden, and deprecated labels;
5. broader, narrower, related, or distinct concepts;
6. code, UI, protocol, configuration, and external-standard mappings;
7. authoritative source, evidence, owner, and confidence or unresolved conflict;
8. lifecycle state, replacement, and review trigger; and
9. representative correct and incorrect uses.

These are candidate information requirements, not a recommendation to add all nine as
front-matter fields. Buzz should prove which need machine-readable structure during the
later synthesis and design work.

### 3. Trace real mentions to the concept

Sample high-risk mentions across document genres and surfaces. For each mention ask:

- Can the intended audience identify the correct concept from context?
- Does it use the preferred label or an admitted contextual label?
- If the label is overloaded, is it qualified or linked?
- Does the local claim agree with the concept's definition and boundary?
- If it names a code or UI token, does it reproduce that token exactly?
- Can a reader reach the definition without guessing between senses?

This is a traceability test. It is stronger than checking that a term appears in a
glossary somewhere.

### 4. Compare definitions and concept relationships

Collect all authoritative or definitional passages for the concept and its closest
neighbors. Classify disagreements as:

- harmless paraphrase;
- different valid scopes;
- incomplete boundary;
- terminology drift after a rename;
- conflicting definitions;
- one word representing two concepts; or
- two labels representing one concept without a mapping.

Do not “fix” a conflict until its class and authoritative source are known. Terminology
harmonization can otherwise overwrite a useful distinction.

### 5. Exercise audience tasks

Use representative tasks to test whether the terminology system works:

- Can a new developer distinguish a compute provider from an inference provider?
- Can an operator distinguish relay liveness, compute liveness, and readiness?
- Can a contributor map the product word “community” to its host-derived relay tenancy
  boundary?
- Can a reviewer tell community roles from channel-level roles?
- Can a search for an old or alternate term reach the current concept and replacement?

Record success, hesitation, wrong-sense selection, unresolved lookup, and time to reach
the intended definition. These measures assess use; raw term counts assess inventory.

## Automation and human judgment

### Good candidates for deterministic checks

A linter or validator can reliably test structured or exact rules such as:

- prohibited spelling and capitalization variants outside declared exclusions;
- use of a deprecated label when an exact replacement is safe;
- undefined or unexpanded abbreviations under a documented first-use rule;
- more than one preferred label for the same concept, language, and scope;
- the same label assigned to several concepts in a scope that requires uniqueness;
- missing replacement targets or lifecycle metadata for deprecated labels;
- broken concept IDs and code/UI/protocol mappings;
- impossible or disallowed structured relation combinations; and
- glossary entries or concept records not reachable from any actual mention.

[Vale's official documentation](https://docs.vale.sh/) describes the correct boundary:
it supplies a framework for enforcing custom prose rules and consistency, not its own
general correctness judgment. Substitution, capitalization, existence, conditional, and
consistency rules can operationalize a decided word list. They cannot decide what Buzz
means by “provider.”

### Human review remains necessary for

- deciding whether two passages refer to the same concept;
- judging whether a definition captures the correct distinguishing characteristics;
- separating legitimate domain variation from accidental synonym drift;
- choosing the right preferred label for an audience;
- deciding whether an exact or merely close mapping is warranted;
- resolving conflicts among product language, implementation, protocol, and precedent;
- assessing whether terminology supports a real task; and
- determining whether a term change is safe for compatibility and search.

Automated findings should therefore say “candidate variant,” “unmapped label,” or
“structure violation,” not “conceptually wrong,” unless the relevant meaning has already
been encoded as a deterministic rule.

## Findings in the current Buzz corpus

### Existing foundations

The corpus already has several useful pieces:

- `node.schema.json` requires permanent, stable node IDs.
- The active [naming standard](../../docs/corpus/standards/naming.md) governs filenames,
  titles, and selected cross-document prose terms.
- The active [identifier standard](../../docs/corpus/standards/identifiers.md) separates
  persistent identity from mutable wording.
- The [glossary-term template](../../docs/corpus/templates/glossary-term.md) requires an
  exact natural form, abbreviation where relevant, a short local definition, scope and
  omissions, and evidence.
- The [concept template](../../docs/corpus/templates/concept.md) requires definition,
  boundary, nonmeaning, use cases, and optional comparison and related resources.
- The [status standard](../../docs/corpus/standards/status.md) explicitly distinguishes
  separate status vocabularies for corpus nodes, ADRs, and the project-intelligence
  contract. This is a good example of scope preventing false synonymy.

These elements can support terminology control, but they do not yet compose one.

### No observable glossary-term implementation

In the inspected 205-node snapshot:

- 20 nodes contain an exact `## Definition` heading;
- no filename outside `templates/` contains `glossary`; and
- no other node declares an `implements` target of
  `corpus-template-glossary-term`.

This does **not** mean the corpus has no definitions. It means there is no observable
reader-facing glossary-term instance using the template's explicit filename or
`implements` mechanism. The corpus has designed a lookup form but has not visibly
populated that form.

### The naming standard and corpus usage have not converged

The active naming standard selects “provenance ledger” and says not to introduce a
synonym. A body-only, case-insensitive scan found:

| Form | Nodes | Occurrences |
|---|---:|---:|
| `provenance ledger` | 4 | 7 |
| `evidence ledger` | 68 | 123 |
| `front matter` | 65 | 187 |
| `front-matter` | 55 | 132 |
| `frontmatter` | 6 | 11 |

The noun/adjective distinction between `front matter` and `front-matter` is intentional
in the standard. Some `frontmatter` matches are metalinguistic references to parser or
schema names and may be technically correct. Likewise, some “evidence ledger” uses may
quote historical terminology or predate the standard. These counts do not establish 134
defects. They establish that a human must classify the variants and that the chosen
“provenance ledger” form has not become the corpus's dominant body usage.

The naming standard says prose-level reuse is human-reviewed; the validator does not read
body terminology. Its rule is therefore declared but not mechanically converged.

### The schema models documents and generic links, not terminology

`node.schema.json` has fields for ID, document type, status, origin, audience, evidence,
and generic document relationships. It has no fields for preferred, alternate, hidden, or
deprecated labels; language or subject field; a concept definition; scope note; semantic
concept relations; external vocabulary mapping; or term lifecycle.

`relationships.schema.json` permits `depends-on`, `supersedes`, `implements`,
`references`, and `part-of`. It has no relation for same concept, broader, narrower,
related concept, distinct-from, exact mapping, or close mapping. This is not a schema bug:
the current schema was designed for corpus-node relationships. It means terminology
semantics cannot currently be inferred from those edges.

The glossary-term template deliberately says alternative terms should be separate nodes
that `reference` a canonical term. Because `references` carries no equivalence,
preference, or lifecycle semantics, a consumer cannot distinguish “synonym,” “supporting
context,” and “neighboring concept” from that edge alone. This is the clearest local
design tension found by this research.

### A closed taxonomy lacks definitions for its members

The active [taxonomy standard](../../docs/corpus/standards/taxonomy.md) records a
13-member closed `type` vocabulary, but it also says no document defines what each
individual value means. Authors are told to use plain English and precedent when
choosing among them.

Mechanical enum validation therefore establishes lexical membership, not conceptual
classification consistency. The system can reject a fourteenth spelling while remaining
unable to prove that two reviewers mean the same thing by `layers`, `implementation`, or
`governance`. This is a high-value candidate for future concept definitions because the
terms drive corpus organization and coverage measures.

### Repeated labels include both valid views and real overload

Three filename stems occur in more than one directory: `liveness.md`,
`push-notification.md`, and `search-query.md`. Duplication is not itself a defect.
Capability and architecture-flow nodes can be different document views of the same
subject. The two liveness nodes represent distinct scoped concepts.

Several documents already model good disambiguation:

- [backend provider](../../docs/corpus/layers/compute/backend-provider.md) states that
  “provider” is overloaded between an LLM inference provider and a backend/compute
  provider.
- [compute liveness](../../docs/corpus/layers/compute/liveness.md) defines its concept and
  distinguishes it from relay process liveness.
- [relay liveness](../../docs/corpus/layers/observability/liveness.md) qualifies its title
  and compares liveness with readiness and compute liveness.
- [community creation](../../docs/corpus/capabilities/communities/community-creation.md)
  maps the product term “community” to a relay tenant in that context.
- [community roles](../../docs/corpus/capabilities/communities/community-roles.md)
  distinguishes a three-value community-wide role model from the channel-scoped
  `MemberRole` hierarchy.

These are evidence against a naive global synonym ban. Qualification, boundary
statements, and cross-surface mappings preserve distinctions that uniform replacement
would erase.

## Candidate checklist criteria

These are research outputs for later synthesis, not approved requirements.

For each important concept or high-risk term, a reviewer could ask:

- [ ] Is the intended concept identifiable independently of the current display term?
- [ ] Is the term's domain, audience, language, or system surface clear enough to select
      the correct sense?
- [ ] Does the concept have one preferred label in each scope where uniqueness matters?
- [ ] Are abbreviations, admitted alternatives, legacy forms, and deprecated labels
      explicitly related to the same concept?
- [ ] If the same label denotes different concepts, are the senses separated and
      qualified at each ambiguous use?
- [ ] Does the definition state distinguishing characteristics, boundary, and important
      nonexamples rather than merely restating the label?
- [ ] Do all authoritative definitions agree, or is disagreement classified and visible?
- [ ] Are broader, narrower, related, part-whole, and distinct concepts represented with
      the intended semantics rather than a generic link?
- [ ] Are product, UI, code, protocol, configuration, and operational names mapped without
      claiming stronger equivalence than the evidence supports?
- [ ] Can the intended reader reach the correct definition from the point of use?
- [ ] Are unfamiliar jargon and abbreviations defined, expanded, linked, or replaced in a
      way appropriate to the audience?
- [ ] Are code, command, schema, and UI labels reproduced exactly when technical accuracy
      requires the legacy or surface-specific form?
- [ ] Does a terminology change distinguish label change from concept change and record
      replacement, compatibility impact, effective scope, and provenance?
- [ ] Can searches for alternate and deprecated forms reach the current concept?
- [ ] Are automated term findings treated as candidates unless concept semantics make the
      verdict deterministic?
- [ ] Has at least one representative audience task shown that readers choose the intended
      concept rather than merely find a matching word?

## Measures that could support later review

No single metric is a quality score. A balanced evidence set could include:

- percentage of prioritized concepts with definition, scope, owner, and source;
- percentage with explicit cross-surface mappings where multiple designations exist;
- unresolved same-label/multiple-concept collisions by risk;
- unclassified alternate labels and deprecated labels without replacements;
- authoritative definition conflicts and median age of unresolved conflicts;
- exact prohibited-form findings after exclusions;
- percentage of jargon and abbreviations with reachable first-use definitions;
- searches for legacy terms that fail to reach the current concept;
- sampled mentions that readers assign to the intended sense; and
- task time and error rate for terminology-dependent workflows.

Coverage denominators must be a declared set of prioritized concepts, not every noun in
the repository. Otherwise the measurement encourages glossary growth rather than risk
reduction.

## Common failure modes

- **Word-list reduction:** treating spelling and capitalization compliance as proof of
  conceptual consistency.
- **Glossary theatre:** accumulating definitions without linking uses to the correct
  senses or maintaining them with the product.
- **Term-as-identity:** renaming a concept's label and accidentally breaking history,
  links, or mappings.
- **Global synonym ban:** forcing product, protocol, code, and operational language into
  one wording even when their distinctions matter.
- **Uncontrolled synonymy:** varying labels for style when no audience or domain reason
  exists, increasing ambiguity and translation cost.
- **Unqualified homonymy:** using one word for several concepts without scope or
  qualification.
- **Circular definition:** explaining a term with the term itself or a near-equivalent.
- **Definition by example only:** showing an instance without stating what makes it an
  instance.
- **Generic-edge overloading:** using `references` to imply equivalence, hierarchy,
  replacement, or realization.
- **Overstrong mapping:** treating similar concepts as exactly identical and propagating
  false equivalence.
- **Silent deprecation:** replacing a label without preserving search, code compatibility,
  effective date, or migration guidance.
- **Lint absolutism:** auto-replacing a token that is an exact API, UI, configuration, or
  historical name.
- **Ontology overreach:** building formal machinery before the corpus has agreed on its
  high-risk concepts and review tasks.

## Competing positions and reconciliations

### “Use exactly one term” versus “use the audience's language”

Stable wording helps recognition, search, translation, and reuse. Audience vocabulary
helps comprehension and aligns documentation with the system a reader sees. The
reconciliation is one preferred label **per declared scope**, plus explicit mappings
where scopes differ. Variation without a reason is drift; variation with a mapped domain
reason can be correct.

### “Avoid jargon” versus “preserve domain vocabulary”

Jargon can exclude readers and conceal ambiguity. It can also be the precise industry
term users search for and must recognize in code or incidents. Prefer plain language when
it retains meaning; otherwise keep the established term and define or link it at the
point of need. Audience evidence, not a blanket rule, decides.

### “One atomic glossary node per term” versus “one entry per concept”

Atomic files improve independent maintenance. Term-centered files become awkward when
several labels denote one concept or one label denotes several concepts. The two goals
can coexist if the atomic unit is the **concept record**, with labels inside it, and a
generated or navigable glossary projects label-to-concept lookup. Whether Buzz should
adopt that model is a later design decision; the current template is term-centered.

### “Automate consistency” versus “meaning requires review”

Automation is valuable after a decision has been encoded: exact variants, required
fields, broken IDs, disallowed label states, and known deprecations. It is unreliable as
the authority for intended concept identity, definition truth, or contextual synonymy.
Use tools to narrow the review surface and humans to settle meaning.

### “Adopt a standard model” versus “keep the corpus simple”

SKOS, TBX, and ISO terminology principles expose mature distinctions that prevent local
reinvention. Full implementation would add fields, workflow, expertise, and maintenance
cost. Buzz should first adopt the conceptual distinctions and a small high-risk concept
inventory. A formal exchange model is justified only if translation, interoperability,
generation, or scale creates a tested requirement.

## Claim ledger

| Claim | Support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Concept identity should be separated from labels and definitions. | ISO 704 public abstract; ISO terminology-entry guidance; SKOS concept/label model | Buzz's current unit is a document node, not necessarily a concept | High |
| One preferred label per declared language and scope is a useful control. | SKOS integrity condition; Microsoft and Google style guidance | Different audiences and surfaces can legitimately need different labels | High |
| A glossary alone is insufficient for terminology governance. | SKOS/TBX richer models; WCAG G62's multiple-sense warning; Buzz template exclusions | A small, stable, single-domain corpus may need only a glossary and word list | High |
| Cross-surface mapping is more accurate than global replacement. | SKOS cross-scheme mappings; Buzz's provider, liveness, community, and role examples | Some variants are pure drift and should simply be removed | High |
| Controlled vocabularies can improve guidance, understanding, automation, and defect detection in software requirements. | [Systematic mapping study](https://doi.org/10.3390/app10217749): 90 selected primary studies, with evidence concentrated in elicitation and specification | The evidence base is requirements-engineering-heavy, dominated by ontologies and taxonomies, and has limited industry collaboration; it does not prove the effect size for Buzz documentation | Medium |
| Terminology lint can enforce decided lexical rules but not semantic correctness. | Vale's stated scope and rule model; local validator inspection | More sophisticated semantic tooling can assist discovery, but still needs an authoritative model and review | High |
| Buzz has designed terminology-related templates but no observable glossary-term instance using their explicit mechanism. | Local filename, heading, and `implements` scans | Definitions exist in other document forms; the scan may miss an undeclared conceptual equivalent | High |
| The corpus has not converged on the naming standard's chosen ledger term. | Body-only counts: 4 nodes use “provenance ledger”; 68 use “evidence ledger” | Historical quotation, deliberate discussion, and pre-standard content require classification before calling individual matches defects | High |
| Buzz's current relationship types cannot express terminology semantics unambiguously. | Relationship enum and its declared directionality | Semantics could remain in prose, though they would not be mechanically queryable | High |
| A concept-first record is the best candidate architecture for later synthesis. | Convergence of ISO entry guidance, SKOS, TBX, accessibility needs, and local overload examples | Implementation cost and the correct fit with atomic corpus nodes remain untested | Medium-high |

## Implications for the later corpus checklist

This topic should contribute at least five separate review concerns:

1. **Lexical control:** preferred written forms and exact surface names.
2. **Concept integrity:** stable identity, correct definition, and clear boundary.
3. **Semantic organization:** explicit neighboring concepts and scoped meanings.
4. **Cross-surface traceability:** mappings among product, code, UI, protocol,
   configuration, and operations.
5. **Reader and lifecycle usability:** reachable definitions, search aliases, and safe
   evolution.

These concerns intersect earlier research without replacing it. Atomic information
architecture determines where concept records live; usability determines whether readers
can reach them; freshness determines when code or vocabulary changes trigger review;
normative-writing quality prevents definitions from silently becoming policy; and
architecture quality depends on stable names and correspondences across views. See the
reports on [atomic information architecture](05-information-architecture-for-atomic-documentation.md),
[usability and findability](06-documentation-usability-and-findability.md),
[freshness and change impact](07-freshness-staleness-and-change-impact.md),
[normative versus descriptive writing](09-normative-versus-descriptive-technical-writing.md),
and [architecture-documentation quality](10-architecture-documentation-quality.md).

## Limitations and open questions

- No complete manual inventory of Buzz concepts or definition conflicts was attempted.
- Lexical counts do not distinguish quotation, history, code identifiers, or deliberate
  metalinguistic discussion from authorial use.
- The research did not test readers or analyze search logs, so usability recommendations
  remain evidence-informed hypotheses for Buzz.
- Public ISO abstracts do not expose every normative requirement of the paid standards.
- The empirical study concerns controlled vocabularies in requirements engineering, not
  documentation-corpus review as a whole.
- SKOS is a 2009 Recommendation. It remains a strong reference model, but Buzz's needs
  should govern any implementation choice.
- The correct identity boundary between a corpus node and a concept is unresolved.
- The project must decide whether terminology records belong in front matter, dedicated
  concept nodes, a separate source file, or a generated projection.
- Ownership, approval authority, and review cadence for preferred terms have not been
  assigned.
- Multilingual terminology is structurally relevant but may be premature until Buzz has
  an explicit localization requirement.

Questions for synthesis:

1. Which Buzz concepts are sufficiently risky or cross-surface to enter the initial
   controlled inventory?
2. Should the canonical atomic unit be a term node, a concept node with several labels,
   or a separate concept registry linked to documents?
3. Which terminology facts must be machine-readable, and which should remain prose?
4. Which scopes need their own preferred labels: product, code, UI, protocol, operations,
   corpus governance, and language?
5. Which semantic relationships are necessary before extending the generic corpus graph?
6. Who can approve a definition or preferred-label change, and what evidence is required?
7. Which term variants can be linted immediately without producing unsafe replacements?
8. How will a reader searching an alternate or deprecated term reach the current concept?

## Sources

Primary and authoritative sources:

- [ISO 704:2022 — Terminology work: Principles and methods](https://www.iso.org/standard/79077.html)
- [ISO 1087:2019 — Terminology work and terminology science: Vocabulary](https://www.iso.org/standard/62330.html)
- [ISO 860:2007 — Terminology work: Harmonization of concepts and terms](https://www.iso.org/standard/40130.html)
- [ISO 30042:2019 — Management of terminology resources: TBX](https://www.iso.org/standard/62510.html)
- [ISO public terminology-entry schema guidance](https://www.iso.org/schema/isosts/v0.5/doc/tbx/ISO-TBX_xsd_Guidelines.html)
- [W3C SKOS Reference, Recommendation](https://www.w3.org/TR/2009/REC-skos-reference-20090818/)
- [WCAG 2.2 Understanding 3.1.3: Unusual Words](https://www.w3.org/WAI/WCAG22/Understanding/unusual-words.html)
- [WCAG technique G62: Providing a glossary](https://www.w3.org/WAI/WCAG22/Techniques/general/G62)
- [Microsoft Style Guide: Use technical terms carefully](https://learn.microsoft.com/en-us/style-guide/word-choice/use-technical-terms-carefully)
- [Google developer documentation style guide](https://developers.google.com/style)
- [Google: Jargon](https://developers.google.com/style/jargon)
- [Google: Write for a global audience](https://developers.google.com/style/translation)
- [Vale documentation](https://docs.vale.sh/)

Empirical synthesis:

- Ahmad, Justo, Feng, and Khan, [“The Impact of Controlled Vocabularies on
  Requirements Engineering Activities: A Systematic Mapping Study”](https://doi.org/10.3390/app10217749),
  *Applied Sciences* 10(21), 2020.

Local evidence:

- [Corpus naming standard](../../docs/corpus/standards/naming.md)
- [Corpus taxonomy standard](../../docs/corpus/standards/taxonomy.md)
- [Corpus identifier standard](../../docs/corpus/standards/identifiers.md)
- [Corpus status standard](../../docs/corpus/standards/status.md)
- [Glossary-term template](../../docs/corpus/templates/glossary-term.md)
- [Concept template](../../docs/corpus/templates/concept.md)
- [Node schema](../../docs/corpus/schema/node.schema.json)
- [Relationship schema](../../docs/corpus/schema/relationships.schema.json)

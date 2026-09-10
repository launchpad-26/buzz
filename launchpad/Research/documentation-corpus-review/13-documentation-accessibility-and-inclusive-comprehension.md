---
description: Research into reviewing accessibility and inclusive comprehension across the Buzz documentation corpus.
tags: [documentation, corpus, accessibility, comprehension, plain-language, cognitive-accessibility, inclusion, localization, research]
---

# Documentation accessibility and inclusive comprehension

Researched 2026-09-08. This is research, not an adopted corpus standard or a WCAG
conformance assessment.

## Research question

How should Buzz review its documentation corpus so that intended readers with different
abilities, assistive technologies, language backgrounds, domain knowledge, devices, and
working conditions can perceive, navigate, understand, and use the information without
losing technical precision?

The investigation considered twelve subquestions:

1. How do accessibility, legibility, readability, comprehension, usability, inclusion,
   and localization differ?
2. Which accessibility requirements apply to authored Markdown, rendered pages, diagrams,
   tables, code, and media?
3. How should Buzz use WCAG without making an unsupported conformance claim about the
   corpus or its hosting platform?
4. What makes technical prose understandable without removing necessary domain language?
5. How should headings, links, lists, tables, and long documents support navigation and
   orientation?
6. What constitutes an equivalent text alternative for a diagram or other non-text
   information?
7. How should documentation account for cognitive and learning disabilities, temporary
   stress, interruptions, and limited working memory?
8. How should content support readers whose primary language is not English and possible
   future translation?
9. What makes terminology, examples, and descriptions socially inclusive without
   replacing exact code or protocol names?
10. Which accessibility and readability checks can be automated, and where is human
    judgment indispensable?
11. What evidence establishes conformance, technical access, comprehension, or successful
    use, and what does each fail to prove?
12. What does the current Buzz corpus make easy or difficult to establish?

## Bottom line

Accessible documentation is not merely simple prose, valid Markdown, alternative text,
or a passing automated scan. It is an end-to-end property of the information, its
structure, the renderer, the user agent and assistive technology, and the reader's task.
Inclusive comprehension adds a further question: once a reader can technically reach the
content, can they find the needed part, build the intended meaning, decide what applies,
and act correctly?

The strongest review model for Buzz is:

> **Intended readers and task → access path and delivery format → perceivable equivalent
> content → semantic structure and orientation → precise, audience-appropriate language →
> usable action and recovery → evaluation with standards, tools, and representative
> people.**

Seven conclusions should govern the later checklist:

1. **Review the delivered experience, not Markdown source alone.** Canonical Markdown is
   one input. GitHub, a generated site, a terminal viewer, a pull-request diff, or another
   projection can expose different semantics, navigation, table behavior, language
   metadata, and assistive-technology support. Source checks and rendered checks answer
   different questions.
2. **Separate WCAG conformance from broader comprehension.** WCAG 2.2 supplies normative
   success criteria for web content, including non-text alternatives, information and
   relationships, link purpose, headings, language, and color use. Cognitive
   accessibility and plain-language guidance extends beyond many conformance criteria.
   A conforming page can still be hard for its intended reader to understand or use.
3. **Preserve meaning across modes.** Important information cannot exist only in a
   picture, color, position, punctuation pattern, or two-dimensional table. Text
   alternatives must convey the same purpose and material relationships, not merely name
   the artifact as “a diagram.”
4. **Make structure do real work.** Descriptive headings, coherent hierarchy, meaningful
   links, short logical sections, genuine lists, and appropriately simple tables help
   readers scan, navigate by assistive technology, resume after interruption, and retain
   context.
5. **Plain language is audience-appropriate precision.** It does not prohibit technical
   terms or impose a universal grade level. Prefer direct and unambiguous wording, define
   unfamiliar concepts, expose prerequisites and scope, use examples, and preserve exact
   identifiers where accuracy requires them.
6. **Do not use a readability formula as the verdict.** Sentence and word-length signals
   can route review, but they do not measure domain knowledge, coherence, task success,
   conceptual difficulty, or actual comprehension. Technical communication research has
   warned against formula-driven rewriting for decades.
7. **Combine automation, expert inspection, assistive-technology exercise, and user
   evaluation.** W3C explicitly states that no tool alone can determine accessibility.
   User testing also cannot establish standards conformance across disabilities by
   itself. The methods are complementary.

The current Buzz corpus has useful foundations: canonical text, role-based audience
metadata, stable headings, descriptive links, a diagram-as-text standard, and some
documents that record product accessibility behavior. It does not have a corpus-wide
accessibility, plain-language, localization, or inclusive-content contract. It is highly
table-dependent, and its 28 Mermaid blocks have no Mermaid `accTitle` or `accDescr`
metadata. The diagram standard requires diagram claims to exist in prose, which may
provide a valuable textual route, but it neither defines equivalent descriptions nor
tests the rendered diagrams. Body content is outside the validator entirely. A green
corpus-validation run therefore establishes no accessibility or comprehension result.

## Scope and method

This report concerns the authored documentation corpus and the reader experiences
derived from it. It covers text, headings, links, lists, tables, diagrams, code and
terminal content, media references, language and terminology, examples, instructions,
and accessibility evaluation. It treats permanent, temporary, and situational barriers
as relevant to design while keeping disability accessibility conceptually distinct from
general convenience.

It does not:

- claim that the current corpus, repository, GitHub rendering, or a future generated
  site conforms to WCAG;
- perform a formal WCAG audit, legal-compliance assessment, or assistive-technology test;
- prescribe a target conformance level or an accessibility policy owner;
- redesign the renderer, schema, Markdown dialect, or diagram standard;
- assign a universal reading age or prohibit specialist vocabulary;
- conduct reader research or speak on behalf of any disability community;
- review the accessibility of the Buzz product interfaces themselves; or
- introduce LLM-specific controls, which remain set aside for this research sequence.

Local inspection covered all 205 Markdown nodes under `launchpad/docs/corpus/` with the
`schema/` subtree excluded, the canonical-representation and validation boundaries, the
audience schema, naming and diagram standards, relevant templates, and representative
nodes that describe accessibility behavior or omissions. Structural counts came from
read-only lexical scans. They identify review surfaces, not conformance failures.
Templates contain examples of Markdown inside Markdown, and a source feature can render
differently across consumers.

External sources were selected in this order:

1. the normative [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
   and W3C's explanatory and evaluation resources;
2. W3C cognitive-accessibility, table, and media guidance;
3. ISO 24495-1:2023 on plain language and ISO/IEC/IEEE 26514:2022 on information for
   software users, limited to publicly accessible material;
4. current Google and Microsoft technical-writing guidance;
5. the official GitHub Flavored Markdown and Mermaid specifications; and
6. peer-reviewed technical-communication research on readability formulas.

WCAG is authoritative for web-content conformance, not a complete documentation-quality
model. Its Understanding pages and techniques are informative, not normative. W3C's
cognitive guidance is a Working Group Note that explicitly supplements rather than
defines WCAG conformance. Vendor style guides are practitioner guidance. Only public ISO
abstracts and previews were available, so this report does not attribute unseen clauses
to those standards.

## Core distinctions

Accessibility reviews become incoherent when several different qualities are collapsed
into “readable.”

| Quality | Review question | Evidence that can address it | What that evidence does not prove |
|---|---|---|---|
| Perceivability | Can the information be obtained through the reader's available senses and presentation? | alternatives, contrast inspection, text resizing, media checks | correct interpretation |
| Operability | Can interactive documentation be navigated and controlled without a particular input method? | keyboard and focus exercise, control semantics | prose comprehension |
| Semantic accessibility | Can structure and relationships be programmatically determined and transformed? | accessibility tree, heading, list, table and landmark inspection | that labels and groupings are meaningful |
| Legibility | Can visual text and symbols be distinguished at the actual size, contrast, spacing, and display conditions? | visual inspection, zoom/reflow and contrast checks | linguistic or conceptual ease |
| Readability | How difficult is the wording and sentence structure for a particular population? | linguistic review, limited metrics, reader evidence | task completion or technical correctness |
| Comprehension | Does the reader construct the intended meaning and distinguish boundaries, conditions, and consequences? | explanation, recall, interpretation and scenario questions | ability to perform the task |
| Usability | Can the intended reader find and use the information to achieve the intended outcome efficiently and safely? | task-based evaluation in context | standards conformance across untested needs |
| Inclusion | Does content avoid preventable exclusion, bias, stereotyping, and culture-specific assumptions? | community-informed editorial review and reader feedback | technical accessibility automatically |
| Localization readiness | Can meaning survive translation and locale adaptation without hidden assumptions? | terminology, ambiguity, format, expansion and translation review | that a translation is accurate |

These qualities reinforce one another but are not substitutes. An accessible table can
carry incomprehensible prose. A plain-language paragraph can sit behind an inaccessible
diagram-only control. Inclusive terminology does not fix a skipped heading hierarchy.
A reader can understand a procedure yet be unable to operate a mouse-only interactive
example.

## Establish the conformance target first

WCAG applies to web content as delivered through web technologies and user agents. The
normative success criteria, not the explanatory examples, determine conformance. A source
repository can help or hinder conformance, but “the Markdown passes WCAG” is not a
well-formed conclusion without identifying the rendered page, technology use, scope,
level, and accessibility-supported environment.

For Buzz, a review should first record:

- the canonical source being assessed;
- each reader-facing projection in scope: raw source, GitHub file view, pull-request
  diff, generated web page, terminal renderer, PDF, or other format;
- the intended readers and priority tasks for each projection;
- renderer-controlled behavior that corpus authors cannot directly change;
- content features authors can change, such as headings, labels, link text, table shape,
  diagram descriptions, and language; and
- whether the result is an editorial review, preliminary check, targeted test, or formal
  conformance evaluation.

The [WCAG 2 overview](https://www.w3.org/WAI/standards-guidelines/wcag/) states that
success criteria determine WCAG conformance. W3C's
[Understanding WCAG introduction](https://www.w3.org/WAI/WCAG22/Understanding/intro)
states that its explanations and techniques are non-normative and that other techniques
can satisfy a criterion. A later Buzz policy should therefore reference criteria and
declared outcomes, not elevate one vendor's authoring recipe into the only compliant
method.

### Source quality and rendered quality are separate gates

Canonical source can be structurally clean while a renderer discards semantics or
creates an inaccessible interactive element. A rendered page can compensate for limited
source syntax, while the same source remains difficult in a pull-request diff or terminal
viewer. Conversions can also lose table, language, heading, and alternative-text
metadata.

Review should inspect at least:

1. **source semantics:** the intended structure is present and does not depend on visual
   spacing alone;
2. **conversion semantics:** the renderer maps that structure into the intended HTML,
   accessibility tree, or target-format tags;
3. **interaction:** keyboard, focus, link, disclosure, copy, and navigation behavior;
4. **adaptation:** zoom, reflow, high contrast, text-only or raw-source use, and relevant
   assistive technologies; and
5. **task:** an intended reader can locate, interpret, and apply the information.

The current corpus README already acknowledges this boundary when it says the canonical
representation is Markdown with front matter, other serializations are generated views,
and GitHub rendering of the human entry point was not verified when written. That is an
honest limitation and evidence that the eventual checklist needs delivery-format scope.

## Preserve information across modes

### Images and diagrams need equivalent purpose, not labels

WCAG 2.2 [Success Criterion 1.1.1](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html)
requires non-text content to have a text alternative that serves the equivalent purpose,
subject to its listed cases. For a complex chart or diagram, W3C describes a short
identification together with a longer description capable of carrying the material
information. “Architecture diagram” is a label, not an account of its components,
relationships, sequence, or conclusion.

For each diagram, review:

- the question it answers and the conclusion or orientation a reader should take from
  it;
- an accessible name that distinguishes it from other diagrams;
- a nearby or programmatically associated description of its material nodes,
  relationships, order, legend, states, and exceptions;
- whether equivalent facts are available in prose, a list, or a simple data table;
- whether color, line style, position, shape, or animation is the only carrier of a
  distinction;
- reading and focus order in the rendered output; and
- whether the raw diagram syntax is useful or merely punctuation noise outside its
  visual renderer.

Mermaid's official [accessibility options](https://mermaid.js.org/config/accessibility.html)
support `accTitle` and one-line or multiline `accDescr`, producing SVG title and
description associations. Those fields are useful but not automatically sufficient for
a complex diagram: the description must still convey the purpose and relationships, and
renderer support must be verified. Text in surrounding prose can be the stronger
alternative when it is complete.

### Do not depend on sensory position or color

WCAG 2.2 [Success Criterion 1.4.1](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)
prohibits using color as the only visual means of conveying information, an action, a
prompt, or a distinction. The broader content principle is that “the red path,” “the box
on the right,” “as shown above,” a dashed edge, or bold type alone cannot carry a fact
that disappears in another presentation.

Use a visible and textual label in addition to a sensory cue. Direction can be helpful as
secondary orientation when the stable object or section is named. It should not be the
only reference because layout changes under reflow and screen readers expose a linear
order. Microsoft's
[writing-for-all-abilities guidance](https://learn.microsoft.com/en-us/style-guide/accessibility/writing-all-abilities)
similarly recommends specific contextual references instead of directional terms alone
and asks product documentation to cover supported alternative interaction methods.

### Media needs planned alternatives

If the corpus later includes audio, video, or animated demonstrations, accessibility is
not satisfied by adding a title. W3C's
[media accessibility guidance](https://www.w3.org/WAI/media/av/) distinguishes captions,
audio or visual description, transcripts, sign-language provision where needed, and
accessible players. A transcript represents speech and relevant non-speech audio; a
descriptive transcript also carries visual information. The precise WCAG requirement
varies with prerecorded versus live, audio-only versus video, and conformance level.

The corpus currently forbids non-Markdown files under its root, so media is not an
observed authored corpus surface. The later checklist should retain a conditional branch
rather than burden every text-only node with irrelevant media items.

## Make structure support navigation and orientation

### Headings are both labels and navigation

WCAG 2.2 separates two concerns:

- [Info and Relationships, 1.3.1](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html)
  requires structure and relationships conveyed by presentation to be programmatically
  determinable or available in text.
- [Headings and Labels, 2.4.6](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html)
  requires headings and labels to describe their topic or purpose.

For corpus review, that means checking more than sequential `#` characters:

- one descriptive page title aligned with the document's promised scope;
- section headings that predict the content beneath them;
- a hierarchy that reflects conceptual nesting rather than visual size;
- no skipped levels, empty headings, or fake headings made only with bold text;
- stable and distinctive heading text where readers navigate lists of headings;
- sufficiently short sections for scanning and resuming; and
- a useful outline for long documents, whether supplied by the renderer or the content.

Heading correctness can be linted structurally. Whether “Details,” “Other,” or “Notes”
actually describes the section requires contextual review.

### Links must make their destination and behavior predictable

WCAG 2.2 [Link Purpose in Context, 2.4.4](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html)
requires a link's purpose to be determinable from its text or programmatically determined
context, except where it is ambiguous to users generally. Descriptive links help both
screen-reader users navigating a link list and readers scanning visually.

Review for:

- short, unique text naming the destination or action;
- sufficient context without requiring a reader to move focus away;
- indication of unexpected behavior such as download, external system, format, or large
  file;
- consistent labels for the same destination where that consistency helps recognition;
- no dependence on “here,” a raw URL, or an issue number whose purpose is not stated; and
- a destination that begins with a title or heading consistent with the link's promise.

Exact code identifiers and issue numbers can remain in a link, but they need a descriptive
noun or surrounding context when the identifier alone does not express purpose.

### Lists and paragraphs should expose logical shape

Use semantic ordered lists for sequences, unordered lists for sets, and prose where the
relationship is genuinely discursive. Parallel list items reduce the work of determining
which properties are comparable. Conditions should precede the actions they govern.
Short sections and paragraphs help scanning, but splitting every sentence into a bullet
can destroy relationships and produce a fragmented outline.

W3C's
[cognitive and learning disability guidance](https://www.w3.org/TR/coga-usable/)
emphasizes clear headings, boundaries, regions, familiar terms, easy-to-understand text,
focus, and recovery of context after distraction. It is a Working Group Note and
explicitly supplements rather than determines WCAG conformance. Its patterns are best
used as hypotheses to test with readers, not as unqualified normative requirements.

### Tables require both a reason and preserved relationships

Tables are appropriate when readers must compare data across two dimensions. They become
barriers when used to compress prose, encode nested logic, or create visual layout.
W3C's [tables tutorial](https://www.w3.org/WAI/tutorials/tables/) explains that header and
data-cell relationships need structural markup so assistive technology can preserve
context one cell at a time. Complex, irregular, or multi-level headers require stronger
associations than a simple top row.

Review each table for:

- a preceding introduction that states its subject and purpose;
- a genuine row-and-column comparison need;
- concise and specific column and row headings;
- programmatic header associations in the delivered format;
- a caption or nearby orientation for complex data;
- meaningful reading order when linearized or viewed on a narrow screen;
- no information expressed only by blank cells, symbols, color, or typography;
- manageable width and cell length under zoom and reflow; and
- a list, definition list, or separate subsections where those structures are easier.

The [GitHub Flavored Markdown specification](https://github.github.com/gfm/#tables-extension-)
defines a table as one header row followed by data rows. Plain GFM has no syntax for a
caption, row headers, or complex header associations. GitHub's own documentation system
adds a nonstandard Liquid `rowheaders` extension for its content, demonstrating that
basic GFM is not enough for every accessible table. Buzz cannot assume that extension
exists in its renderers. A complex Markdown table may need simplification, accompanying
text, a different format, or renderer-specific support.

## Make technical language understandable

### Plain language is an outcome for a declared audience

[ISO 24495-1:2023](https://www.iso.org/standard/78907.html) establishes plain-language
principles and guidance and explicitly says they are applicable to technical writing.
Its public abstract also limits the standard to information primarily in text form and
provides examples only in English. The full normative guidance was not publicly
accessible during this research, so no unseen clause is attributed here.

For Buzz, a plain-language review should ask whether intended readers can:

1. identify whether the document is relevant to their goal;
2. find the applicable section and prerequisite information;
3. understand concepts, conditions, distinctions, and consequences; and
4. use the information to make the intended decision or complete the task.

That outcome model fits technical experts as well as newcomers. Experts also benefit
from direct structure and unambiguous scope; they simply need different assumed knowledge
and can tolerate necessary specialist vocabulary.

Practical checks include:

- state purpose, scope, audience, prerequisites, and promised outcome early;
- put the condition before the instruction or rule it qualifies;
- use direct subjects and verbs so responsibility is visible;
- prefer common words when they preserve the exact meaning;
- keep one primary proposition per sentence when several conditions do not need to be
  reasoned about together;
- avoid nested negatives, remote pronoun references, idioms, metaphors, jokes, and
  unexplained abbreviations;
- define domain terms at the needed point and distinguish neighboring concepts;
- introduce examples after the general rule rather than asking the reader to infer the
  rule from examples alone;
- use summaries and progressive disclosure without hiding safety or applicability; and
- retain exact code, command, UI, protocol, and configuration names in code formatting.

This connects directly to the report on
[terminology and conceptual consistency](11-terminology-and-conceptual-consistency.md).
Replacing every technical term with an everyday approximation can make documentation
less comprehensible because the reader can no longer map it to the system.

### Reading level is not comprehension

WCAG 2.2's Reading Level success criterion is Level AAA and provides for supplemental
content or a lower-secondary-level version when the criterion's conditions apply. It
should not be paraphrased as “all technical documentation must score at grade X.” The
broader [Readable guideline](https://www.w3.org/WAI/WCAG22/Understanding/readable.html)
also covers language identification, unusual words, abbreviations, and pronunciation.

Redish and Selzer's peer-reviewed article,
[“The Place of Readability Formulas in Technical Communication”](https://pure.psu.edu/en/publications/place-of-readability-formulas-in-technical-communication/),
argues that formulas are inadequate measures of difficulty for adult readers, can direct
attention away from the sources of reader problems, and should be replaced by reader
testing for the decision they are often asked to make. The study is from 1985, but its
central measurement objection remains valid: formulas primarily observe surface features
such as word and sentence length, not relevance, coherence, prior knowledge, conceptual
density, or task success.

A readability metric can be a discovery signal for unusually dense passages if its
formula, preprocessing, language, and threshold are disclosed. It should not be a quality
score, a blocking proxy for comprehension, or an incentive to replace precise terms with
shorter ambiguous words.

### Technical artifacts need explanatory access

Code, protocol traces, commands, configuration, formulas, and schemas often require exact
syntax that cannot be simplified. Accessibility comes from the surrounding route:

- explain the artifact's purpose before it appears;
- distinguish input, output, placeholders, and omissions;
- describe the material pattern or result in prose;
- break long examples into meaningful parts without destroying copyability;
- avoid screenshots of code or terminal text;
- make horizontal scrolling and line wrapping tolerable in the renderer; and
- offer a complete copyable form when annotations interrupt literal use.

The earlier report on
[examples, commands, code, and configuration](12-examples-commands-code-and-configuration.md)
covers correctness and reproducibility. This topic adds the question of whether the same
artifact can be perceived, navigated, and explained through the reader's access mode.

## Support cognitive access and task recovery

Documentation is often used under interruption, time pressure, fatigue, unfamiliarity,
or incident stress. Those conditions can temporarily create the same needs served by
clear cognitive-accessibility patterns, but they should not be used to erase the specific
experiences of people with cognitive and learning disabilities.

For important documents, review whether readers can:

- recognize where they are and what the current section is for;
- see prerequisites and applicability before committing to an action;
- distinguish required, optional, conditional, and explanatory content;
- keep related condition, action, expected result, and exception close together;
- resume from a stable labeled step or state after interruption;
- avoid remembering values or rules that can remain visible;
- recognize errors and use a concrete recovery or escalation path;
- choose among a bounded number of clearly differentiated alternatives; and
- obtain the same essential information without decoding a dense visual or table.

The W3C cognitive guidance recommends integrating the needs of people with cognitive and
learning disabilities into requirements, research, and usability testing. It also warns
that design, structure, and language can create barriers. This supports testing real
tasks and recovery, not inferring cognitive accessibility from short sentences alone.

## Write for global and inclusive use

### Language and locale

WCAG 2.2 requires the default human language of a web page to be programmatically
determinable at Level A and the language of passages to be determinable at Level AA,
with stated exceptions for technical terms, proper names, and vernacular borrowings. The
renderer may set the page language globally, but corpus authors must still identify
language changes or avoid unexplained foreign-language content where relevant.

Google's current
[global-audience guidance](https://developers.google.com/style/translation) recommends
clear, concise, unambiguous language; direct address; active voice; standard sentence
structure; consistent terminology; and avoidance of unexplained idioms, slang, humor,
seasonal assumptions, and culture-specific references. These choices help readers using
English as an additional language and reduce ambiguity in translation, but they do not
constitute a localization process.

Review locale-sensitive content for:

- unambiguous dates, times, time zones, and durations;
- units, decimal and thousands separators, currencies, addresses, and phone formats;
- text direction and mixed-language passages;
- examples that do not assume one country's institutions, laws, holidays, seasons, or
  infrastructure;
- screenshots and UI names that may differ by locale;
- text expansion and narrow-screen behavior in a generated presentation; and
- terminology records or notes where translators need a concept boundary rather than a
  string substitution.

The corpus is currently English and has no declared localization requirement. Translation
readiness should therefore be a proportionate design consideration, not a claim that all
nodes must be translated or carry locale metadata immediately.

### Inclusive language and representation

Inclusive review should look for unnecessary assumptions about bodies, senses, gender,
race, culture, family, location, economic access, and technical privilege. Google's
[inclusive-documentation guidance](https://developers.google.com/style/inclusive-documentation)
correctly treats community preference as contextual: people-first language can be a
default, while some blind, Deaf, and autistic communities commonly prefer identity-first
language. A global replacement rule cannot settle those preferences.

For Buzz, review whether:

- people are described neutrally and with the terms their communities prefer;
- disability is not framed as abnormality, tragedy, inspiration, or defect;
- examples distribute names, roles, locations, and identities without stereotyping;
- metaphors and jokes do not introduce violence, ableism, or cultural opacity;
- “user,” “developer,” and “operator” do not silently imply one body, input method,
  locale, privilege level, or experience path; and
- exact legacy code or protocol terms remain exact while nearby prose explains any
  inclusive reader-facing alternative.

This is an editorial and community-informed judgment. A prohibited-word list can enforce
a decided replacement in safe contexts, but it cannot determine identity preference,
quotation, code accuracy, or whether a scenario is representative.

## Evidence and evaluation

Accessibility and comprehension need several evidence lanes rather than one linear test
score.

| Method | Strong evidence for | Does not establish by itself |
|---|---|---|
| Source lint | heading order, empty labels, missing alt fields, vague-link candidates, table shape, disallowed terms | rendered semantics, equivalence, comprehension |
| Rendered DOM or format inspection | actual headings, labels, language, table semantics, reading order, accessibility tree | usefulness of descriptions or task success |
| Automated accessibility scan | deterministic rule failures and high-volume regressions | complete WCAG conformance or meaningful prose |
| Keyboard, zoom, reflow, color and contrast exercise | operability and presentation behavior in named conditions | other assistive technologies or cognitive access |
| Screen-reader exercise | navigation, announcements, reading order, labels, and alternative text in a named stack | every screen reader, disability, or comprehension outcome |
| Expert WCAG evaluation | criterion-level findings in a declared conformance scope | broader plain-language usability automatically |
| Comprehension check | whether sampled readers can explain scope, concepts, conditions, and consequences | successful task performance or universal accessibility |
| Task-based user evaluation | whether representative readers can find and use the information in context | formal conformance across needs not represented in the sample |
| Translation or bilingual review | preservation of intended meaning and locale suitability | accessibility of the rendered translation |

W3C's [evaluation overview](https://www.w3.org/WAI/test-evaluate/) states that no tool
alone can determine whether a site meets accessibility standards and that knowledgeable
human evaluation is required. Its guidance on
[involving users](https://www.w3.org/WAI/test-evaluate/involving-users/) supplies the
other boundary: user evaluation reveals important accessibility and general usability
problems, but a few participants cannot establish conformance or represent all people
with the same or different disabilities. Combine standards evaluation and appropriately
scoped user involvement; report the technologies, tasks, participant characteristics,
and limitations.

### A practical review sequence

For a selected node and delivery surface:

1. **Declare the reader and task.** Include assumed domain knowledge, language, access
   path, and use context rather than only a job-role label.
2. **Inventory content modes.** Text, code, tables, diagrams, media, interactive elements,
   links, and generated projections each create different checks.
3. **Inspect source structure.** Verify headings, lists, labels, link purpose, logical
   order, text alternatives, language, and non-sensory equivalents.
4. **Render in the target presentation.** Inspect semantics, order, resizing, reflow,
   contrast, table behavior, diagram output, and any renderer-added controls.
5. **Exercise assistive paths.** Use keyboard-only and at least the relevant
   assistive-technology combinations for the content and audience.
6. **Test interpretation.** Ask readers to locate a fact, explain a boundary, choose an
   applicable branch, and predict a consequence without leading them.
7. **Test use.** For action content, observe task completion, errors, recovery, and
   confidence in a representative environment.
8. **Classify findings.** Separate standard violation, renderer defect, source defect,
   comprehension problem, inclusive-language concern, and untested uncertainty.
9. **Retest affected projections.** A source fix can improve one renderer and damage
   another; preserve the evidence scope.

## Automation and human judgment

### Good candidates for deterministic checks

Tools can usefully detect or report:

- missing or duplicate page titles and skipped heading levels;
- empty headings and links, duplicate anchors, and exact vague-link labels;
- Markdown image syntax without an alt field and known image-of-text patterns;
- Mermaid blocks without `accTitle` or `accDescr` where the renderer supports them;
- color names, directional references, emoji, symbols, and ASCII art as review candidates;
- table width, missing introductions, empty header labels, and structures that basic GFM
  cannot express accessibly;
- missing document or passage language in a renderer that exposes language metadata;
- unexpanded abbreviations and known jargon or deprecated terminology;
- unusually long sentences, paragraphs, sections, link text, and noun strings;
- known non-inclusive terms outside quoted, historical, code, and protocol contexts;
- locale-sensitive date, time, unit, currency, and address patterns;
- rendered HTML failures detected by accessibility engines; and
- regressions in stored accessibility trees, headings, landmarks, or link lists.

Every finding needs the right label. “Long sentence” is a review candidate, not a
comprehension failure. “Missing Mermaid description” is a metadata fact, not proof that
the surrounding prose lacks an equivalent. “Automated WCAG pass” is not a valid
conformance verdict.

### Human review remains necessary for

- identifying the actual intended reader, knowledge, and task;
- deciding whether a heading, link, definition, example, or alternative is meaningful;
- judging whether visual information has a genuinely equivalent text route;
- preserving technical precision while simplifying presentation;
- determining whether a table's relationships remain intelligible when linearized;
- recognizing hidden domain, privilege, cultural, sensory, and interaction assumptions;
- deciding whether identity language respects the relevant community and context;
- evaluating conceptual coherence, ambiguity, and recovery after interruption;
- operating real assistive technologies and distinguishing author from renderer defects;
- testing comprehension and task success; and
- determining the severity and priority of barriers.

## Findings in the current Buzz corpus

### Audience metadata is a useful but shallow start

Every node must declare one or more values from the closed `audiences` enum: `agent`,
`developer`, `operator`, and `reviewer`. That enables role filtering and forces an author
to name at least one intended group. It does not record a primary audience, assumed
knowledge, task, language, disability-related access needs, device, context of use, or
conflict between audience needs.

Those facts do not all belong in front matter. Procedures already have a place for
prerequisites, and other genres can state assumptions in scope or opening context. The
gap is the absence of a shared review question connecting the role label to knowledge,
access, and task.

The schema has no document-language or localization field. That is not automatically a
defect: the corpus is presently English, and the renderer may set a page language. It
means language accessibility cannot be inferred from the canonical node model and must
be resolved at the delivery layer before conformance is assessed.

### There is no corpus-wide accessibility or comprehension standard

No active corpus filename is dedicated to accessibility, plain language, inclusive
content, cognitive accessibility, or localization. Relevant observations are scattered:

- the glossary-term template cites accessibility and translation as benefits of
  glossaries but deliberately excludes localization notes from its form;
- the typing-indicator node records an `aria-live="polite"` implementation detail;
- the mention node explicitly excludes the autocomplete popup's accessibility from its
  audit scope; and
- the moderation node says the desktop moderation UI's accessibility was not audited.

These are healthy examples of scoped evidence and disclosed omissions. They describe
product behavior or local template boundaries, not a rule for making the corpus itself
accessible.

### Canonical source and reader presentation are unresolved

The corpus README says Markdown with YAML front matter is the single canonical authored
representation and all other serializations are generated views. It also says human
review occurs in the pull-request diff and explicitly records GitHub rendering of its
own front matter as “expected but not verified” when written.

This produces at least two reader experiences:

1. maintainers and reviewers read canonical source and diffs, including a potentially
   large evidence ledger before the body; and
2. later users may read a generated projection intended to foreground the body and hide
   or reorganize machine metadata.

The first cannot be ignored because it is the governance mechanism. The second cannot be
assumed because no generated accessibility contract is established. A corpus review must
name which experience it tested.

### The heading baseline is promising but only lexical

The active naming standard requires one body-level H1 at the beginning of each document,
but the validator never reads the body. A lexical scan across current node bodies found
no transition that jumps upward by more than one Markdown heading level. Template files
contain embedded example documents, so counts of H1 headings themselves are not a clean
measure.

This supports a good structural baseline, not an accessibility verdict. The scan does not
establish that headings describe their sections, that a renderer preserves the hierarchy,
or that long nodes are easy to navigate.

### Links avoid the most obvious vague labels

An exact case-insensitive scan found no Markdown link whose entire label was `here`,
`click here`, `read more`, `this`, or `link`. This is positive lexical evidence only.
Issue numbers, filenames, code identifiers, repeated labels, and links whose purpose
depends on distant context still require review, as does the rendered destination.

### Tables are the largest structural review hotspot

A source scan found at least one GFM-style table delimiter in 194 of 205 nodes. Many
documents contain several tables, especially evidence-heavy standards and reference
material. This does not mean 194 files are inaccessible: simple tables with clear column
headings can work well, and some tables are the right structure.

It does mean table accessibility cannot be a marginal checklist item. Basic GFM provides
one header row but no native caption, row-header, or complex-header syntax. Several
corpus tables visually use the first column as a row label or contain long prose in many
columns. Review must inspect the target rendering, linearized meaning, header association,
width, and whether a list or subsections would reduce cognitive and assistive-technology
load.

### Diagram rules preserve textual provenance but not accessible presentation

The current corpus contains 28 exact `mermaid` fence openings across 27 nodes. No corpus
node contains an exact Mermaid `accTitle` or `accDescr` declaration. The active diagram
standard requires diagrams to be text inside fenced Markdown, requires every diagram
claim to appear in prose, and prohibits image files under the corpus root. It also says
no tool checks diagram syntax, truth, or freshness.

That design has real accessibility strengths:

- source is diffable text rather than an opaque bitmap;
- important claims should be available outside the diagram; and
- prohibiting screenshots avoids image-only text.

It also leaves unresolved barriers:

- Mermaid source is not necessarily comprehensible when spoken as code;
- surrounding evidentiary prose may not function as an equivalent, navigable diagram
  description;
- rendered SVGs have no authored accessible title or description in the inspected
  blocks;
- color, line style, spatial position, and rendered reading order are not reviewed; and
- the corpus validator does not inspect any of them.

The appropriate conclusion is “unassessed and missing a shared alternative-text
contract,” not “all diagrams fail WCAG.” Renderer behavior and the completeness of
surrounding prose must be examined before a criterion-level verdict.

### Body validation establishes no accessibility result

The validator checks front matter, evidence shapes, and relationships, then discards the
body for validation purposes. It cannot detect skipped headings, vague links, table
semantics, missing diagram descriptions, sensory-only language, untranslated passages,
readability signals, or non-inclusive prose. Nor does it render or exercise a page.

Accessibility automation would therefore be a new validation surface with its own
authority, exceptions, renderer, and evidence. It should not be implied by the existing
green corpus check.

## Candidate checklist criteria

These are research outputs for later synthesis, not approved requirements.

For each node and material delivery surface, a reviewer could ask:

- [ ] Are the intended primary readers, task, assumed knowledge, language, access path,
      and use conditions clear enough to judge the content?
- [ ] Is the reviewed object identified precisely: canonical source, GitHub view, diff,
      generated page, terminal rendering, PDF, or another projection?
- [ ] If WCAG conformance is claimed, are the version, level, page scope, technologies,
      and evaluation method stated without treating advisory techniques as mandatory?
- [ ] Does the rendered page expose a descriptive title and correct default language?
- [ ] Do headings describe their sections and form a semantic hierarchy without skipped
      levels, empty sections, or visual-only substitutes?
- [ ] Can readers scan the outline, locate the relevant section, and resume after an
      interruption?
- [ ] Does each link identify its purpose and any unexpected behavior from its label or
      programmatically available context?
- [ ] Are ordered steps, unordered sets, prose relationships, and tabular comparisons
      expressed with the structure that matches their meaning?
- [ ] Is each table introduced, necessary, simple enough, supplied with meaningful row
      and column context, intelligible when linearized, and usable under zoom or narrow
      display?
- [ ] Does every meaningful image, diagram, symbol, animation, or visual state have an
      equivalent text route that conveys purpose and material information?
- [ ] Do Mermaid diagrams carry useful accessible names and descriptions when the
      renderer supports them, with longer nearby explanations where needed?
- [ ] Is no distinction carried only by color, position, shape, line style, typography,
      punctuation, or sensory-direction wording?
- [ ] Are code, commands, configuration, formulas, and protocol traces real text with an
      explanation of their purpose and result rather than screenshots or unexplained
      syntax?
- [ ] For audio or video, are the required captions, descriptions, transcripts, and
      accessible player behavior provided for the media type and declared target?
- [ ] Does the opening establish purpose, applicability, scope, prerequisites, and the
      outcome appropriate to the document genre?
- [ ] Are sentences, paragraphs, sections, lists, and noun strings as direct as the
      technical meaning permits?
- [ ] Are conditions placed near the rule or action they govern, with responsibility and
      exceptions explicit?
- [ ] Are unfamiliar terms, abbreviations, symbols, and overloaded concepts defined or
      linked at the point of need while exact system identifiers remain exact?
- [ ] Are examples sufficient to clarify difficult concepts without requiring readers to
      infer the general rule from the example alone?
- [ ] Does the content avoid unexplained idioms, jokes, metaphors, culture-specific
      references, and ambiguous locale-dependent dates, times, units, or formats?
- [ ] Are people and communities described neutrally and according to contextual naming
      preferences rather than a blind global substitution rule?
- [ ] Are alternative input methods documented where a procedure involves a user
      interface, rather than assuming a mouse, touch, vision, or one device?
- [ ] Are automated findings reported as exact observations rather than proof of
      comprehension or complete conformance?
- [ ] Has the target rendering been exercised with keyboard, zoom, reflow, color and
      contrast changes, and relevant assistive technologies?
- [ ] Have representative readers been asked to find, explain, choose, perform, and
      recover using the content, with participant and task limits recorded?
- [ ] Are accessibility defects, comprehension failures, renderer limitations, and
      untested uncertainty classified separately and assigned an owner?

## Measures that could support later review

No single metric is an accessibility or comprehension score. A balanced evidence set
could include:

- delivery surfaces inventoried with accessibility ownership and test status;
- applicable WCAG criteria evaluated by level, severity, and projection;
- deterministic source and rendered accessibility findings by rule and recurrence;
- headings that fail to predict sampled section content;
- links that readers cannot identify or destinations that violate their promise;
- diagrams with an accessible name, useful description, and equivalent prose route;
- tables requiring row headers or complex associations unsupported by their renderer;
- keyboard, screen-reader, zoom, reflow, and high-contrast task results by named stack;
- prioritized terms and abbreviations with reachable definitions;
- passages flagged for density that human review confirms as difficult;
- comprehension accuracy for scope, prerequisites, conditions, distinctions, and
  consequences;
- task success, time, error, abandonment, recovery, and assistance requested by audience;
- translation defects caused by ambiguity, unstable terminology, or locale assumptions;
- accessibility-related support incidents and time to remediation; and
- coverage of high-risk nodes rather than raw corpus-wide pass percentages.

Do not average high-severity access failures into a reassuring score. A single missing
alternative on an essential architecture diagram or an unusable production runbook can
matter more than many cosmetic passes.

## Common failure modes

- **Source-only assurance:** linting Markdown and never inspecting the delivered page.
- **Renderer absolution:** blaming the platform for content labels, structure, or
  alternatives the author controls.
- **WCAG theatre:** listing criteria or an automated score without a declared scope,
  level, technologies, and human evaluation.
- **Tool-pass equivalence:** treating zero automated findings as proof of accessibility.
- **Participant overgeneralization:** treating one person's successful use as evidence
  for every person with the same or a different disability.
- **Alt-text presence:** checking that text exists without checking equivalent purpose.
- **Diagram duplication:** repeating visible node labels in alt text while omitting the
  relationships and conclusion.
- **Prose-nearby assumption:** treating any paragraph near a diagram as its equivalent.
- **Code-as-alternative:** assuming Mermaid or ASCII source is intelligible because it is
  text.
- **Sensory-only instruction:** relying on color, right/left, above/below, shape, or
  punctuation without stable text.
- **Heading cosmetics:** using bold or a heading level for appearance rather than
  hierarchy.
- **Generic headings:** technically valid structure whose labels do not support
  navigation.
- **Link-list failure:** links labeled only with `here`, a number, or a filename that has
  no meaning out of context.
- **Table compression:** forcing prose, nested decisions, or long evidence into a wide
  grid because it looks compact visually.
- **First-row sufficiency:** assuming a GFM header row supplies row headings, captions,
  and complex cell associations.
- **Short-sentence metric:** splitting prose until a grade score improves while logical
  relationships become harder to follow.
- **Plain-language dilution:** replacing exact technical distinctions with familiar but
  false approximations.
- **Expert exemption:** assuming technical expertise removes disability, language,
  attention, device, or stress-related barriers.
- **One-language assumption:** treating English source as proof that locale, language,
  terminology, and format choices are universal.
- **Inclusive-word-list absolutism:** replacing quoted, historical, code, or
  community-preferred identity language without context.
- **Accessibility add-on:** reviewing access only at publication, after information
  architecture and format choices are expensive to change.

## Competing positions and reconciliations

### “Meet WCAG” versus “make the documentation understandable”

WCAG provides an essential, testable shared standard for web accessibility. It does not
fully specify plain language, domain learning, scenario fit, or successful technical
work. Use WCAG for its intended conformance question and supplement it with cognitive,
comprehension, and task-based evaluation. Do not weaken WCAG into a general aspiration or
inflate usability findings into conformance.

### “Plain language” versus “technical precision”

Unnecessary complexity excludes readers; necessary terminology carries exact domain
meaning. Simplify sentence structure, scope, navigation, and explanation first. Retain
the precise term, define it, distinguish neighboring concepts, and map it to code or
protocol names. A shorter inaccurate word is not plainer.

### “Set a reading-grade threshold” versus “test comprehension”

A threshold is cheap, repeatable, and useful for routing unusually dense prose. It is
also insensitive to prior knowledge, coherence, code, lists, concepts, and tasks. Use
disclosed metrics as warning signals only. Judge important content with audience-specific
interpretation and task evidence.

### “Put everything in prose” versus “use diagrams and tables”

Prose linearizes well and can carry accessible alternatives. Diagrams reveal topology,
sequence, and spatial relationships; tables accelerate comparison. Use each for the
relationship it represents best, then preserve essential meaning in another accessible
route. Equivalence does not require word-for-word duplication.

### “Diagram-as-text is accessible” versus “diagram source is code”

Text source is diffable and transformable, but punctuation-heavy Mermaid or box drawing
can be unusable through speech. Keep the source for governance, add accessible diagram
metadata for supported renderers, and provide a human-readable description of purpose
and material relationships.

### “Avoid tables” versus “tables are semantic structure”

Tables are the correct structure for genuine two-dimensional relationships and can be
accessible with proper headers and associations. They are poor containers for linear
prose or nested decisions, particularly under GFM's limited semantics. Decide from the
information relationship and the actual renderer, not from a blanket ban.

### “User testing is decisive” versus “standards inspection is decisive”

Users reveal barriers and task failures that rules and tools miss. A small sample cannot
represent every disability or establish criterion-level conformance. Combine
representative user evaluation with standards-based expert review and automated checks;
report the scope of each.

### “One accessible version” versus “multiple equivalent presentations”

A single well-structured text route reduces drift. Some readers benefit from diagrams,
audio, simplified summaries, raw code, or translated views. Maintain one canonical set
of facts, but permit several task-appropriate projections whose equivalence, provenance,
and accessibility can be tested.

## Claim ledger

| Claim | Support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Accessibility is a property of delivered content, technology, user agents, assistive technology, and use, not source text alone. | WCAG conformance model; W3C evaluation and user-involvement guidance; local source/projection model | Authors may control only part of the delivery stack, so ownership must be divided | High |
| WCAG supplies necessary web-accessibility criteria but not a complete comprehension model. | WCAG 2.2; COGA's explicit supplemental status; ISO plain-language scope | WCAG includes readable and understandable criteria, including several Level AAA provisions | High |
| Meaningful non-text content needs an equivalent-purpose text route. | WCAG 1.1.1 Understanding guidance; W3C complex-content patterns | Decorative content appropriately has an empty or ignored alternative | High |
| Semantic and descriptive headings support navigation and orientation. | WCAG 1.3.1 and 2.4.6; COGA guidance | A structurally valid heading can still be vague or unnecessary | High |
| Basic GFM cannot express every accessible table relationship. | GFM table specification; W3C table guidance; GitHub Docs' separate row-header extension | Simple one-header-row tables may be sufficient and accessible in a supporting renderer | High |
| Plain-language principles apply to technical writing without prohibiting technical terms. | ISO 24495-1 public abstract; Google global-audience guidance | The complete ISO normative text was unavailable; exact implementation remains audience-specific | Medium-high |
| Formula-driven readability is not a valid proxy for adult technical comprehension. | Redish and Selzer peer-reviewed technical-communication article; W3C user-centered cognitive guidance | Surface metrics can still identify candidates for review and compare controlled revisions | High |
| Automated accessibility tools cannot determine complete accessibility. | W3C evaluation overview | Automation can decisively find violations of rules within its supported scope | High |
| User evaluation and standards evaluation are complementary. | W3C involving-users guidance | User samples require careful recruitment and cannot generalize to every population | High |
| Buzz has role-based audience metadata but no access, knowledge, task, or language profile. | Local node schema and corpus scan | Those details may be better in genre-specific prose than schema | High |
| Buzz's tables are a corpus-scale review hotspot. | 194 of 205 current nodes contain a GFM-style table delimiter | Presence does not establish complexity or a barrier; many tables may be appropriate | High |
| Buzz's Mermaid diagrams lack authored Mermaid accessibility metadata in the current snapshot. | 28 exact Mermaid fences across 27 nodes; zero exact `accTitle` or `accDescr` declarations | Surrounding prose may already provide equivalent information; renderer behavior is untested | High |
| Buzz's diagram standard has accessibility strengths but no equivalent-description or rendered-access contract. | Local diagram standard and validator inspection | Its prose-duplication rule may satisfy much of the substantive need in individual nodes | High |
| A green corpus-validation run establishes no body-level accessibility result. | Local validator and standards explicitly say the body is not inspected | Separate CI or hosting checks could evaluate a derived view outside this validator | High |

## Implications for the later corpus checklist

This topic should contribute at least seven separate concerns:

1. **Reader and task inclusion:** role, knowledge, language, access path, and context.
2. **Delivery-surface scope:** source, renderer, user agent, and assistive technology.
3. **Perceivable equivalence:** diagrams, tables, code, media, sensory cues, and text
   alternatives.
4. **Semantic navigation:** titles, headings, links, lists, order, and orientation.
5. **Inclusive comprehension:** purpose, plain language, concepts, prerequisites,
   examples, decisions, and recovery.
6. **Global and social inclusion:** language, locale, translation readiness,
   representation, and community-informed terminology.
7. **Triangulated evidence:** automation, expert inspection, assistive-technology
   exercise, standards evaluation, and representative task testing.

These should be risk-tiered. A short glossary term, a wide security configuration table,
a complex architecture diagram, and an incident runbook do not need identical evaluation,
but each needs an accessible path to its essential purpose.

This topic overlaps without replacing earlier work on
[information architecture](05-information-architecture-for-atomic-documentation.md),
[usability and findability](06-documentation-usability-and-findability.md),
[procedural and operational documentation](08-reviewing-procedural-and-operational-documentation.md),
[terminology](11-terminology-and-conceptual-consistency.md), and
[executable content](12-examples-commands-code-and-configuration.md). Accessibility asks
whether those structures and meanings survive different modes of perception and action;
inclusive comprehension asks whether the intended reader can make use of them.

## Limitations and open questions

- No rendered corpus page was inspected with an accessibility tree, keyboard, screen
  reader, zoom, reflow, high-contrast mode, or narrow viewport.
- No formal WCAG conformance scope, target level, supported technology set, or legal
  obligation was established.
- Structural scans do not determine whether headings, links, tables, or prose are
  meaningful.
- The diagram scan does not determine whether surrounding prose already supplies an
  adequate equivalent description.
- The table count does not distinguish simple accessible comparisons from complex or
  unsuitable layouts.
- No readability formula was run because this research rejects such a score as a verdict;
  no reader study replaced it.
- No people with disabilities or readers using English as an additional language were
  consulted during this topic.
- Public ISO material did not expose the complete normative text of ISO 24495-1 or
  ISO/IEC/IEEE 26514.
- The W3C cognitive guidance is supplemental, evolving guidance rather than a normative
  Recommendation.
- The corpus's intended reader-facing renderer and treatment of large front-matter
  evidence ledgers remain unresolved.
- The cost, ownership, tooling, and cadence for assistive-technology and user testing have
  not been designed.
- Translation may not be a current product requirement; preparation should be
  proportionate until that decision exists.

Questions for synthesis:

1. Which corpus presentations are official reader-facing delivery surfaces, and which
   are maintainer-only views?
2. What WCAG version and level, if any, should govern each web presentation, and who owns
   renderer-controlled failures?
3. Which accessibility facts belong in canonical Markdown, generated metadata, tests, or
   publication infrastructure?
4. What minimum text-equivalent contract should apply to Mermaid and box-drawing
   diagrams?
5. Which existing tables require row headers, captions, simplification, or conversion to
   lists and subsections?
6. How should audience declarations include assumed knowledge and tasks without expanding
   front matter into a persona database?
7. Which readability signals are useful for routing review without becoming a score or
   target?
8. Which high-risk nodes should receive keyboard, screen-reader, cognitive, and task-based
   evaluation first?
9. How will findings identify the tested renderer, browser, assistive technology,
   participants, tasks, and limitations?
10. What inclusive-language decisions need community input or exact-code exceptions?
11. What localization readiness is valuable before the corpus has an approved translation
    requirement?

## Sources

Standards and authoritative W3C guidance:

- [Web Content Accessibility Guidelines 2.2](https://www.w3.org/TR/WCAG22/)
- [WCAG 2 overview](https://www.w3.org/WAI/standards-guidelines/wcag/)
- [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/intro)
- [Understanding 1.1.1: Non-text Content](https://www.w3.org/WAI/WCAG22/Understanding/non-text-content.html)
- [Understanding 1.3.1: Info and Relationships](https://www.w3.org/WAI/WCAG22/Understanding/info-and-relationships.html)
- [Understanding 1.4.1: Use of Color](https://www.w3.org/WAI/WCAG22/Understanding/use-of-color)
- [Understanding 2.4.4: Link Purpose in Context](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html)
- [Understanding 2.4.6: Headings and Labels](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels.html)
- [Understanding Guideline 3.1: Readable](https://www.w3.org/WAI/WCAG22/Understanding/readable.html)
- [Making Content Usable for People with Cognitive and Learning Disabilities](https://www.w3.org/TR/coga-usable/)
- [WAI Tables Tutorial](https://www.w3.org/WAI/tutorials/tables/)
- [Evaluating Web Accessibility Overview](https://www.w3.org/WAI/test-evaluate/)
- [Involving Users in Evaluating Web Accessibility](https://www.w3.org/WAI/test-evaluate/involving-users/)
- [Making Audio and Video Media Accessible](https://www.w3.org/WAI/media/av/)
- [ISO 24495-1:2023 — Plain language: Governing principles and guidelines](https://www.iso.org/standard/78907.html)
- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/standard/77451.html)

Technical-writing and format guidance:

- [Google: Write accessible documentation](https://developers.google.com/style/accessibility)
- [Google: Write for a global audience](https://developers.google.com/style/translation)
- [Google: Write inclusive documentation](https://developers.google.com/style/inclusive-documentation)
- [Microsoft: Writing for all abilities](https://learn.microsoft.com/en-us/style-guide/accessibility/writing-all-abilities)
- [GitHub Flavored Markdown specification: Tables](https://github.github.com/gfm/#tables-extension-)
- [GitHub Docs: Markdown and Liquid, including table row headers](https://docs.github.com/en/contributing/writing-for-github-docs/using-markdown-and-liquid-in-github-docs)
- [Mermaid accessibility options](https://mermaid.js.org/config/accessibility.html)

Research:

- Redish and Selzer,
  [“The Place of Readability Formulas in Technical Communication”](https://pure.psu.edu/en/publications/place-of-readability-formulas-in-technical-communication/),
  *Technical Communication* 32(4), 1985, pp. 46–52.

Local evidence:

- [Corpus README](../../docs/corpus/README.md)
- [Corpus node schema](../../docs/corpus/schema/node.schema.json)
- [Corpus agent instructions](../../docs/corpus/AGENTS.md)
- [Corpus naming standard](../../docs/corpus/standards/naming.md)
- [Corpus diagram standard](../../docs/corpus/standards/diagrams.md)
- [Corpus glossary-term template](../../docs/corpus/templates/glossary-term.md)
- [Corpus procedure template](../../docs/corpus/templates/procedure.md)
- [Typing-indicator node](../../docs/corpus/capabilities/presence/typing-indicator.md)
- [Mention node](../../docs/corpus/capabilities/messaging/mention.md)
- [Moderation node](../../docs/corpus/capabilities/moderation/moderation.md)
- [Corpus validator](../../project-intelligence/corpus/validate.py)

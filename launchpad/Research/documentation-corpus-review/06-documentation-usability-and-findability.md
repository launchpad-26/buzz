---
description: Research into defining, reviewing, and testing the usability and findability of the Buzz documentation corpus.
tags: [documentation, corpus, usability, findability, search, navigation, user-testing, research]
---

# Documentation usability and findability

Researched 2026-09-06. This is research, not an adopted corpus standard.

## Research question

How should Buzz define, review, and test documentation usability and findability so
that a specified reader can locate the right corpus content, recognize that it is the
right content, extract what matters, and accomplish an information or task goal with
acceptable effort, error, and confidence?

The investigation considered eight subquestions:

1. What is the relationship between usability, findability, information architecture,
   accessibility, and prose quality?
2. At what points can a documentation search or navigation journey fail?
3. Which cues help a reader predict that a search result, link, or section contains the
   answer they need?
4. How should the corpus support readers who arrive by search, browse from a known
   entry point, or land directly on an atomic node?
5. How do audience, prior experience, and information-seeking strategy change what is
   usable?
6. Which review methods can be applied before publication, and which outcomes require
   representative readers performing real tasks?
7. Which measures reveal effective and efficient use, and which common analytics are
   merely ambiguous activity signals?
8. What should a future Buzz content-review checklist ask at cue, node, journey, and
   corpus levels?

## Bottom line

Usability is not a document attribute that an editor can certify from prose alone. It
is an outcome of use: specified users achieving specified goals with effectiveness,
efficiency, and satisfaction in a specified context. This framing comes directly from
[ISO 9241-11:2018](https://www.iso.org/standard/63500.html) and is reused for software
information by
[ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen).
It rules out a universal verdict such as “the corpus is usable” without naming the
audience, goal, starting state, delivery surface, and conditions of use.

Findability is a necessary part of that outcome, but it is not the same as search
availability. For this report, content is findable only when the intended reader can:

1. reach a plausible access surface;
2. express or browse from their information need using language they know;
3. notice a promising result, heading, category, or link;
4. predict the target accurately enough to choose it;
5. recognize after arrival that the target is applicable and authoritative; and
6. recover quickly if it is not.

A page can therefore be indexed but not findable, found but not recognizable, clear
but not actionable, or successful for an expert and unusable for a newcomer. Search,
browse, direct links, maps, and contextual cross-references are complementary access
routes. The right test is not whether all of them exist; it is whether representative
reader-goal combinations reliably reach correct outcomes.

For Buzz, the largest content-level risk is that the information needed to discriminate
between 205 atomic nodes is not yet represented canonically. The schema contains
stable identity, corpus surface, lifecycle state, origin, audiences, evidence, and
relationships, but no title, short description, task or question, product/platform
applicability, preferred terms, or synonyms. Human-facing titles and opening context
exist only in Markdown bodies that the validator does not inspect. No exhaustive
generated index is present. A future search or navigation layer could scrape prose,
but without a declared contract it would be guessing which text is the canonical cue.

The evidence supports a two-part quality regime:

- **Inspection and automated checks** can verify the presence, uniqueness, structure,
  consistency, resolution, and likely usefulness of cues.
- **Task-based evaluation** is needed to establish that people can actually find and
  use the content. It should measure correct completion, time or effort, errors,
  abandonment, false success, confidence, and satisfaction—not page views alone.

The eventual checklist should preserve this distinction. “Has descriptive H1” is an
inspectable design criterion. “A representative operator can find the correct recovery
instruction and identify when it applies” is a usability claim requiring observed
evidence.

## Scope and method

This report addresses content usability and the ability to find content within a
documentation system. It does not decide:

- the corpus information architecture or map representation, covered by topic 5;
- freshness and change-impact policy, deferred to topic 7;
- the detailed quality of operational procedures, architecture descriptions,
  terminology, examples, accessibility, or public security disclosure, covered by
  later topics;
- a publishing platform, search engine, analytics product, or schema migration;
- visual interaction design beyond the content cues that navigation depends on; or
- LLM-specific retrieval, generation, or evaluation controls, which remain set aside
  for this research sequence.

Local inspection covered the corpus README, node schema, naming and linking rules,
documentation and review standards, templates, validator, current Markdown bodies,
and the findings of topic 5. A read-only body scan excluded schema fixtures, recognized
fenced code, counted level-one headings, checked first-title duplication, and inspected
whether common discovery fields were present in front matter.

External sources were selected in this order:

1. ISO usability and software-information standards for definitions and scope;
2. NIST's Common Industry Format for usability-test measures;
3. government usability-testing and benchmarking guidance for applied study design;
4. W3C accessibility guidance where headings, links, and multiple access routes bear
   directly on findability;
5. OASIS DITA for the relationship between a topic opening and search/link previews;
6. information-retrieval literature for query sets, relevance judgments, precision,
   recall, and ranking evaluation;
7. empirical research on information scent and technical-documentation use; and
8. maintained Google and Microsoft documentation guidance as practitioner evidence
   for titles, headings, and scanning.

Standards establish concepts and practitioner guides propose useful design tactics;
neither replaces observation of Buzz's readers. Findings from web navigation and cloud
API documentation are transferred cautiously rather than treated as universal laws.

## Definitions

| Term | Meaning here |
|---|---|
| Usability | The outcome for specified users pursuing specified goals with effectiveness, efficiency, and satisfaction in a specified context |
| Effectiveness | Accuracy and completeness of the achieved result |
| Efficiency | Resources expended in relation to the result, including time, attention, steps, and assistance |
| Satisfaction | The user's cognitive and emotional response relative to needs and expectations |
| Findability | The ability to locate and recognize applicable content from a realistic starting state |
| Discoverability | Whether an access route or cue is available and noticeable; one component of findability |
| Information need | The underlying question, decision, or goal; it is not necessarily the literal query typed |
| Information scent | The reader's estimate, from a label or contextual cue, that following a path will lead toward the goal |
| Cue | A title, description, heading, link label, category, synonym, status, audience label, or other signal used to predict relevance |
| Direct arrival | Landing on a node from search, code, an issue, a bookmark, or another external context rather than following a corpus map |
| False success | The reader believes the goal is complete or the answer is correct when it is not |
| Search relevance set | Representative information needs and queries paired with human judgments about which nodes answer them |
| Diagnostic metric | A signal that helps locate a problem but does not itself establish a successful reader outcome |

Accessibility and usability overlap but are not interchangeable. W3C's multiple-way,
heading, and link-purpose guidance is used here because those provisions change whether
people can locate and predict content. Topic 13 will address the broader range of
inclusive access and comprehension requirements.

## A findability-to-outcome model

The following chain is a synthesis for Buzz, not a published standard. Each stage can
fail independently, so a useful review records where the failure occurred.

| Stage | Reader question | Typical failure | Evidence to collect |
|---|---|---|---|
| Exposure | “Where can I look?” | Needed node is absent from search, index, map, or contextual links | Index/map coverage, entry-point tests |
| Expression | “How do I describe this in words I know?” | Corpus uses an internal term or acronym unknown to the reader | Query corpus, terminology interviews, zero-result and reformulation logs |
| Prediction | “Which result or path is likely to help?” | Generic title, missing summary, ambiguous category, vague link text | First-choice correctness, tree paths, result-selection comments |
| Recognition | “Am I in the right place?” | Opening omits purpose, scope, audience, status, or applicability | Correct rejection/acceptance, false-success rate, confidence |
| Extraction | “Where is the exact answer?” | Dense prose, weak headings, buried constraints, inconsistent patterns | Answer accuracy, time to answer, scanning path, backtracking |
| Application | “Can I use this to decide or act?” | Missing prerequisite, ambiguous instruction, unusable example, no outcome check | Task completion, errors, retries, assists, verification result |
| Recovery | “What do I do if this is wrong or insufficient?” | Dead end, no alternative, no escalation, no route back | Abandonment, recovery time, successful alternate route |

This model prevents several category errors:

- search ranking cannot repair content that is correctly found but impossible to
  recognize or apply;
- excellent prose cannot repair a node that no relevant route exposes;
- a successful click is not a successful information task;
- a long visit may mean engagement, confusion, interruption, or abandonment; and
- a short visit may mean immediate success or immediate rejection.

## What the local system establishes

### The product intent requires question-led access

The root and launchpad vision documents describe a cohort that should be able to answer
“What is changing?” and “How does this work?” without first knowing the responsible
person, repository, service name, or file location. That is a findability requirement
expressed from the user's starting state: a question precedes knowledge of the storage
structure.

The current corpus README is a useful door into corpus rules, schemas, and broad
directories. It is not an exhaustive content index and says that generated indexes,
graphs, stale reports, and other projections are planned. As topic 5 found, no current
`generated/` directory or exhaustive generated index supplies that access layer.
Repository browsing and `rg` remain practical for an informed maintainer, but they are
not evidence that a reader who lacks the canonical filename or vocabulary can find an
answer.

### Current metadata supports filtering, but not result discrimination

The node schema allows exactly these top-level fields:

- `id`;
- `type`;
- `status`;
- `origin`;
- `audiences`;
- `evidence`; and
- optional `relationships`.

Those fields can answer useful questions about identity, subject surface, lifecycle,
provenance, intended audience, support, and graph membership. They do not supply a
reader-facing title, concise description, task or question, product/platform/version
applicability, preferred term, acronym expansion, or search synonym.

The body scan found 205 non-fixture corpus nodes and zero uses of `title`,
`description`, `keywords`, or `tags` in node front matter. This is expected because
`additionalProperties: false` prohibits them; it is not an authoring omission under the
current contract. The implication is narrower: a future index or search-result preview
cannot obtain those cues from canonical metadata without a contract change or a
defined body-extraction rule.

OASIS DITA demonstrates one possible design principle, not a required format: its
[`shortdesc`](https://docs.oasis-open.org/dita/dita/v1.3/os/part2-tech-content/langRef/base/shortdesc.html)
represents a topic's purpose or theme and is intended for both link previews and search
results. It is normally also the opening paragraph, while a map can supply a
context-specific preview. The transferable point is that a reusable discovery cue has
an explicit owner and rendering behavior. Buzz currently has neither for summaries.

### Titles are strong in aggregate but outside deterministic validation

All 205 scanned nodes had at least one level-one heading, and the first H1 value was
unique across the corpus. That is a positive baseline. The naming standard also
requires one H1 and recommends a standalone, reader- or task-oriented title whose
filename contains a useful search term.

However, the validator parses only the YAML front-matter region. It does not check an
H1's presence, count, position, wording, or uniqueness, and it does not make the title
available as structured output. A body-aware scan found two nodes with more than one
rendered H1:

- `corpus-standard-decision-references`; and
- `corpus-standard-confidence`.

The two standards contain front-matter-like material and a delimiter between their
first and second H1s. The current loader stops at the first closing delimiter, so this
material is body content from the validator's perspective even though it resembles
metadata to an author. This report does not repair those nodes, but the observation is
important: schema validity and a manual convention do not currently establish the
title structure that findability depends on.

### Human-visible and machine-visible navigation remain different

Body links can use surrounding prose to explain why a destination matters. Typed
`relationships[]` edges can be resolved and projected by tooling. The local linking
standard correctly treats them as separate channels, but the validator checks only
relationship targets, not Markdown links or link labels.

Topic 5 measured 192 explicit edges, of which 167 were the broad `references` type,
and found 81 nodes with neither incoming nor outgoing structured edges. Those values
do not prove poor findability because body links, direct search, and legitimate
standalone nodes are omitted. They do show that the structured graph alone cannot be
treated as the current navigation system or as a relevance judgment for search.

### Audience labels are necessary but too coarse to prove context fit

The schema's controlled audiences—`agent`, `developer`, `operator`, and `reviewer`—are
valuable filter facets. They do not capture experience, current task, prior product
knowledge, permissions, operating environment, urgency, or whether the reader seeks
orientation, troubleshooting, exact reference detail, or evidence for a review.

The labels should therefore be treated as audience hypotheses, not usability proof.
For example, two operators may need different entry points when one is learning the
system and the other is responding to an incident. The same node can be applicable to
both while the journey and success threshold differ.

## What the external evidence establishes

### Usability must be evaluated in a specified context

[ISO 9241-11:2018](https://www.iso.org/standard/63500.html) describes usability as an
outcome of use and explicitly does not prescribe one evaluation method. The public
definition reproduced in
[ISO 9241-115:2024](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A9241%3A-115%3Aed-1%3Av1%3Aen)
binds usability to specified users, goals, and context, with effectiveness, efficiency,
and satisfaction as the outcome dimensions.

[ISO/IEC/IEEE 26514:2022](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
applies that definition to information for software users. Its public introduction
connects accurate, easy-to-find, understandable information with becoming proficient,
and its vocabulary distinguishes navigation, signposts, reference information, and
topics. The current
[ISO/IEC/IEEE 26513:2017](https://www.iso.org/standard/67417.html) separately covers
testing and reviewing information for users. That separation matters: editorial
review can find likely defects, but an outcome claim needs evaluative testing.

For Buzz, “usable for operators” is underspecified. A defensible test statement looks
more like: “An operator with stated Buzz and Kubernetes experience, starting from the
published documentation home during a non-production exercise, can identify the
applicable relay recovery procedure, state its prerequisites, and determine the success
condition without assistance.” The exact scenario should come from real cohort work,
not be invented solely to make a document pass.

### Findability begins with an information need, not an exact query

The standard information-retrieval evaluation model uses a document collection, a
test suite of information needs, and human relevance judgments. The
[Stanford *Introduction to Information Retrieval*](https://nlp.stanford.edu/IR-book/html/htmledition/information-retrieval-system-evaluation-1.html)
emphasizes that relevance is judged against the underlying need, not merely the words
typed in a query.

This distinction is critical for a corpus with project-specific vocabulary. A search
test that copies “NIP-29 channel scoping” from an existing title measures literal
matching. A reader may instead ask why channel queries use an `h` tag. The test set
should preserve the reader's wording and desired outcome, then record acceptable
canonical nodes and misleading near-matches.

For unranked results, precision asks how much retrieved material is relevant and
recall asks how much relevant material was retrieved
([Stanford IR, precision and recall](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-unranked-retrieval-sets-1.html)).
Ranked search also needs attention to where relevant material appears; measures such as
precision at a small cutoff or the rank of the first correct result fit a reader who
will inspect only a few choices
([Stanford IR, ranked retrieval](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-of-ranked-retrieval-results-1.html)).
These offline measures test retrieval behavior, not whether the selected document can
be understood or used.

### Titles, summaries, headings, and link labels are prediction tools

Information-foraging research offers a useful explanatory model. Fu and Pirolli's
[SNIF-ACT study](https://www.peterpirolli.com/Professional/About_Me_files/FuPirolli%20HCI%20SNIF-ACT%20(final).pdf)
modeled how people assess link-text cues, select paths, backtrack, and abandon a search.
Its web-navigation datasets supported a combination of semantic cue strength and
position rather than position alone. The study concerns general web tasks, not Buzz,
so it supports the principle that labels predict destinations—not a fixed wording rule.

The practical sources agree on the cue characteristics:

- [Google's developer-documentation guide](https://developers.google.com/style/headings)
  recommends a unique H1 based on the page's primary purpose, task-oriented wording
  for tasks, conceptual wording for concepts, and a logical heading hierarchy.
- [Microsoft's scannable-content guidance](https://learn.microsoft.com/en-us/style-guide/scannable-content/)
  recommends leading headings and paragraphs with important information, using
  consistent patterns, and providing within-document navigation for long material.
- [W3C's headings-and-labels guidance](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels)
  explains that accurate descriptive headings let readers predict section content;
  semantic heading structure and descriptive wording are distinct requirements.
- [W3C's link-purpose guidance](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html)
  requires a link's purpose to be determinable from its text or programmatically
  determined context.
- DITA's `shortdesc` gives search results and link previews a concise statement of
  purpose rather than a repeated title.

The synthesis is that a useful cue must both **match the reader's language** and
**discriminate the destination**. Adding every synonym to every title would harm
scanning and terminology consistency. Better mechanisms include a canonical title,
concise purpose/applicability description, controlled preferred term, and separately
maintained aliases where a real retrieval need has been observed.

### More than one access route is justified, but route count is not the goal

[WCAG 2.2's Multiple Ways explanation](https://www.w3.org/WAI/WCAG22/Understanding/multiple-ways.html)
recognizes that people may prefer search, a hierarchy, a table of contents, or an
index, and that different access needs make different routes effective. A
[Digital.gov case study](https://digital.gov/2022/01/06/open-source-information-architecture-design-using-the-tools-you-have-to-conduct-card-sorting-and-tree-testing)
used card sorting to explore expected groupings and tree testing to see whether users
could find items and understand category labels.

These sources support search plus curated browse and contextual links, not an arbitrary
minimum number of routes. Duplicate menus with the same labels and blind spots do not
create resilience. Each access mode should serve a known starting state:

- search for a reader who can express the need but not its location;
- a goal or audience map for a reader who knows the outcome but not the canonical
  vocabulary;
- a reference index for a reader who knows the subject class;
- contextual links for a reader already inside an explanation or workflow; and
- direct-arrival orientation for external links and bookmarks.

### Different documentation users take different paths

Meng, Steinhardt, and Schubert's
[study of API-documentation needs](https://journals.sagepub.com/doi/10.1177/0047281617721853)
used interviews and a follow-up questionnaire. Its abstract reports that developers
first sought a global view of an API's purpose and features, then followed either
concept-oriented or code-oriented learning strategies. The finding is API-specific,
but it challenges a single ideal path even within one broad audience.

A 2024 CHI mixed-methods study analyzed documentation page-view logs for more than
100,000 users across four cloud services. It found diverse visit patterns correlated
with factors including prior product experience and later API use
([Nam et al., paper](https://cmustrudel.github.io/papers/chi2024doc_logs.pdf);
[publication record](https://research.google/pubs/understanding-documentation-usage-through-log-analysis-an-exploratory-case-study-of-four-cloud-services/)).
The authors present log analysis as complementary to interviews and laboratory studies,
not a replacement. They also note missing task, role, expertise, and page-content data
and limited generalizability beyond the four products.

Buzz should therefore segment tests by meaningful context rather than average all
readers together. Declared audience is a starting facet; prior Buzz knowledge, task
urgency, repository familiarity, and conceptual versus action-oriented intent may be
more predictive in a particular study.

### Task performance needs effectiveness, efficiency, and satisfaction measures

NIST's
[Common Industry Format for Usability Test Reports](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=151449)
organizes metrics around effectiveness, efficiency, and satisfaction. It treats
correct task completion, errors, assists, and access to help as effectiveness evidence;
time relative to successful completion as efficiency evidence; and questionnaires as
satisfaction evidence. It warns by example that time alone cannot distinguish a fast,
error-prone experience from a slower, safer one.

[GOV.UK's usability-benchmarking guidance](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service)
recommends believable tasks with clear correct answers, periodic repetition, and
measurement of completion, time, abandonment, false success, perceived ease, and
confidence. Its
[qualitative testing guidance](https://www.gov.uk/guidance/usability-testing-qualitative-studies)
similarly requires clear tasks and success criteria with potential users. Moderated
testing can reveal why a failure occurs by observing the path and asking participants
to think aloud
([GOV.UK moderated testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing)).

No single metric is sufficient. For safety-, security-, or production-sensitive
documentation, correct rejection of an inapplicable instruction and avoidance of a
harmful action can be more important than speed. Partial completion may also need an
explicit scoring rubric rather than being silently counted as success.

### Analytics can select review targets but cannot certify success

Nam et al. show that privacy-preserving page-view logs can expose usage patterns at a
scale that small studies cannot. The paper also makes the limitation clear: its data
did not include the users' actual tasks, roles, expertise, or page contents, and logs
were proposed as a first pass alongside richer human methods.

This supports a disciplined interpretation of documentation analytics:

| Signal | Plausible interpretations |
|---|---|
| High page views | High need, good discoverability, a common failure, or a mandatory step |
| Low page views | Low need, poor exposure, wrong vocabulary, or a highly specific reference |
| Long dwell time | Careful study, complexity, confusion, interruption, or a copied browser tab |
| Short dwell time | Immediate answer, obvious mismatch, broken content, or accidental visit |
| Repeated searches | Iterative learning, query refinement, poor result cues, or failed answers |
| High click-through | Attractive result wording; not necessarily correct or usable content |
| High exit rate | Successful completion or abandonment |

Analytics should generate hypotheses and recruit cases for task testing. Where future
publication introduces telemetry, collection also needs a legitimate purpose,
privacy review, retention rule, and an analysis plan tied to reader outcomes. This
report does not recommend collecting individual-level telemetry by default.

## A candidate evaluation framework for Buzz

### 1. Define a context-of-use statement

Before judging a corpus slice, record:

- audience and relevant experience;
- information or task goal;
- realistic trigger and starting knowledge;
- starting surface, such as repository root, generated docs home, search box, issue,
  code link, or direct node URL;
- allowed tools and assistance;
- environment, permissions, product baseline, and urgency where relevant;
- correct outcome, acceptable partial outcomes, and dangerous false outcomes; and
- why the task matters often enough or is risky enough to test.

This statement keeps the test from teaching the corpus's own vocabulary to the reader.

### 2. Build an information-need and relevance set

Use real questions from issues, onboarding, reviews, incidents, support requests, and
work sessions. Preserve both the natural wording and the desired outcome. For each
need, reviewers should identify:

- one or more correct canonical nodes;
- acceptable supporting nodes;
- plausible but wrong or inapplicable near-matches;
- terms, acronyms, and synonyms actually used by readers;
- whether freshness, status, product, or platform changes relevance; and
- what evidence would show that the answer was understood, not merely opened.

This set can test titles, indexes, maps, local or hosted search, and future publishing
changes. It should be versioned because relevance changes with the product and corpus.

### 3. Inspect the content cues before testing people

For every node in the test slice, inspect:

- one unique and descriptive H1;
- a concise opening that states purpose and differentiates the node from near-matches;
- audience, assumed knowledge, applicability, and scope cues where ambiguity matters;
- headings that predict the content beneath them and preserve logical hierarchy;
- important constraints and keywords early enough to scan;
- link text and surrounding context that predict the target and reason to follow it;
- stable canonical terminology plus observed aliases in an appropriate retrieval
  mechanism; and
- visible status, provenance, and authority where readers must choose between similar
  answers.

Automated checks should cover syntax and structure. Human review should judge meaning.

### 4. Test the access route separately from the content

Use the lightest method that isolates the question:

| Question | Suitable method |
|---|---|
| Do category names match reader expectations? | Open/closed card sort as exploratory evidence |
| Can users find a target through a proposed hierarchy? | Tree test with realistic tasks |
| Does search retrieve and rank correct nodes? | Offline relevance set plus representative query testing |
| Can readers predict a result from title and summary? | First-choice or result-recognition test without opening every result |
| Can a direct-arrival reader orient correctly? | Show the node without repository breadcrumbs and ask purpose/applicability questions |
| Can a reader complete the whole information task? | Moderated or unmoderated end-to-end task test |
| Did a redesign improve stable high-value tasks? | Repeated usability benchmark with the same outcome definitions |
| Where should deeper investigation start? | Aggregated search/navigation analytics, issue history, and support themes |

Do not test a hierarchy and then claim search quality, or test result recognition and
then claim task completion. Each method answers a bounded question.

### 5. Measure outcomes as a bundle

For each task, record at least:

- **effectiveness:** correct, partial, incorrect, or abandoned outcome; answer
  completeness; critical errors; false success; and required assistance;
- **efficiency:** time to first correct node, time to correct answer or completed task,
  number of inspected nodes, query reformulations, backtracks, and retries;
- **satisfaction:** perceived ease, confidence, and concise qualitative comments; and
- **path evidence:** first choice, route taken, misleading cue, recovery behavior, and
  the stage in the findability-to-outcome chain where difficulty began.

For search evaluation, also record whether a correct node appears within the few
results a reader will realistically inspect, how much irrelevant material surrounds
it, and which high-value needs return no acceptable result. Do not collapse critical
and routine tasks into one average without reporting them separately.

### 6. Diagnose the failure before changing content

Map each failed task to one or more causes:

- missing canonical content;
- absent exposure from an index, map, search corpus, or local link;
- vocabulary mismatch;
- ambiguous title or preview;
- incorrect classification or audience/applicability metadata;
- weak direct-arrival orientation;
- poor within-node scanning or extraction;
- incomplete, incorrect, or unusable content;
- stale or conflicting content;
- delivery-surface or accessibility defect; or
- test-design problem.

Different causes need different owners. Adding keywords cannot repair a wrong answer;
rewriting a procedure cannot repair an index that omits it.

### 7. Repeat after material change

Keep stable benchmark tasks for longitudinal comparison, but add new tasks as the
product and cohort's work change. Re-run affected tasks when titles, navigation,
taxonomy, search, maps, publishing, or high-risk content changes. Preserve the test
context and scoring rules so apparent improvement is not caused by easier prompts or
more experienced participants.

## Candidate checklist criteria

These are candidates for the eventual synthesis, not requirements in force.

### Context and intended outcome

- [ ] The review names a specific audience, goal, starting state, and context of use.
- [ ] The node or journey supports a real information need, decision, or action.
- [ ] Success, partial success, failure, false success, and dangerous outcomes are
      distinguishable before testing.
- [ ] The task prompt uses reader language and does not reveal the canonical title,
      category, filename, or route.
- [ ] High-risk and high-frequency tasks are reported separately rather than hidden in
      a corpus-wide average.

### Exposure and access routes

- [ ] A reader has an intentional route from an appropriate starting surface to the
      node or journey.
- [ ] Search, browse, map, index, contextual-link, and direct-arrival routes are not
      assumed to be interchangeable.
- [ ] A node required by a tested journey is not silently absent because of status,
      taxonomy, generation, or indexing rules.
- [ ] More than one route exists when different reader needs justify it, not merely to
      increase route count.
- [ ] A failed route provides a usable way to reformulate, backtrack, choose an
      alternative, or escalate.

### Titles, previews, and terminology

- [ ] The node has exactly one unique H1 whose wording states its primary purpose or
      subject.
- [ ] Task titles describe the action or outcome; concept and reference titles name the
      subject precisely.
- [ ] A concise description differentiates the node from likely near-matches and says
      when or why it is useful.
- [ ] Search and link previews have a declared canonical source rather than an
      undocumented prose-scraping heuristic.
- [ ] Important reader vocabulary, canonical terminology, acronyms, and observed
      synonyms have an intentional retrieval strategy.
- [ ] Aliases improve retrieval without creating competing canonical terms or bloated
      titles.
- [ ] Status, origin, audience, and applicability cues help readers reject an
      inapplicable result before acting on it.

### Node orientation and extraction

- [ ] A direct-arrival reader can identify the node's purpose, scope, audience,
      assumptions, and applicability promptly.
- [ ] The opening confirms what outcome or understanding the node provides without
      merely repeating the title.
- [ ] Headings describe their sections, follow a logical hierarchy, and support
      scanning out of context.
- [ ] Important qualifications, prerequisites, warnings, and constraints are visible
      before the content that depends on them.
- [ ] Similar information uses consistent section and sentence patterns where that
      helps comparison or rapid extraction.
- [ ] Long nodes provide proportionate within-node navigation.
- [ ] Tables and lists improve lookup or comparison rather than fragmenting an
      explanation that must be read sequentially.

### Links and transitions

- [ ] Link text or its determined context predicts the destination and reason to
      follow it.
- [ ] The destination's title and opening confirm the promise made by the source cue.
- [ ] Generic labels such as “here,” “more,” or an unexplained raw path do not carry the
      only meaning of an important transition.
- [ ] Related links are selected for the current reader decision rather than appended
      as an exhaustive undifferentiated list.
- [ ] A link to a prerequisite, deeper explanation, evidence source, alternative, next
      step, and recovery path makes that role clear.
- [ ] Body links and machine-readable relationships are each checked for the distinct
      purpose they serve.

### Search and browse evaluation

- [ ] The test set contains representative information needs, natural queries, correct
      nodes, acceptable alternatives, and misleading near-matches.
- [ ] Relevance is judged against the reader's need, not literal query-term overlap.
- [ ] Correct results appear within the number of choices readers realistically inspect.
- [ ] High-value zero-result, low-precision, and low-recall cases enter a review queue.
- [ ] Hierarchy labels and placements are tested with users when browse is a required
      route.
- [ ] Search and navigation changes are compared on a stable benchmark as well as new
      or changed needs.

### End-to-end usability evidence

- [ ] Representative readers attempt realistic tasks without being taught the answer.
- [ ] Tests record correctness and completeness, not only page arrival or clicks.
- [ ] Time and path length are interpreted relative to successful outcomes.
- [ ] Errors, assists, retries, abandonment, and false success are visible.
- [ ] Confidence and perceived ease supplement observed performance rather than replace
      it.
- [ ] Different audiences, experience levels, and task intents are segmented when they
      plausibly change results.
- [ ] The report preserves context, task wording, participant characteristics, scoring
      rules, and uncertainty so a later result can be compared fairly.

### Analytics and governance

- [ ] Each analytic signal has a stated hypothesis and cannot be mistaken for task
      success by itself.
- [ ] Page views, dwell time, click-through, and exit rate are treated as ambiguous
      diagnostics.
- [ ] Telemetry, if introduced, has purpose limitation, privacy review, retention rules,
      and proportionality.
- [ ] Automated structural checks, expert review, search evaluation, and reader testing
      remain separate evidence classes.
- [ ] Findings identify the failure stage and responsible content or platform surface
      rather than issuing one undifferentiated “usability” score.

## Misleading metrics and review shortcuts

| Shortcut | Why it fails |
|---|---|
| “The page is in the repository, so it is findable” | Presence says nothing about a reader's route or vocabulary |
| “Search returns results” | Results can omit the right node, rank it too low, or surround it with plausible wrong answers |
| “The exact title query works” | The test gives the system canonical language the reader may not know |
| “Every node has an H1” | Presence does not establish uniqueness, predictiveness, applicability, or body validity |
| “The README links to each directory” | A directory map does not prove goal-based access across directories |
| “Users clicked the first result” | The cue may be attractive but misleading |
| “Time on task fell” | Users may be failing faster; success and errors must be paired with time |
| “People spent a long time on this page” | Dwell time cannot distinguish learning from confusion or interruption |
| “No support ticket mentions it” | Readers may abandon, work around, ask elsewhere, or not know documentation exists |
| “The expert reviewer understood it” | Familiarity can hide vocabulary, prerequisite, and orientation failures for the intended audience |
| “Five users found no problem” | Small qualitative rounds discover issues; they do not prove a population success rate |
| “One average score improved” | Gains on easy tasks can hide regressions on critical or minority-audience tasks |
| “Add every synonym as a keyword” | Uncontrolled aliases add noise and terminology drift; observed needs and relevance tests should govern additions |
| “Personalize every path” | Personalization adds opacity, privacy cost, and maintenance burden before a stable baseline exists |

## Competing positions and unresolved decisions

### “Good writing is usable documentation”

Clear, concise, well-structured writing is an important designed attribute. ISO's
definition still makes usability an outcome for a user, goal, and context. Recommended
resolution: inspect writing quality as a contributor, and reserve usability claims for
task evidence.

### “Findability is the search engine's job”

Ranking matters, but it relies on useful titles, descriptions, terminology, scope, and
applicability signals. Readers also browse, follow links, and arrive directly.
Recommended resolution: treat findability as a joint property of content cues,
architecture, delivery, and reader context, with failures assigned to the actual layer.

### “Canonical terminology should replace synonyms”

Consistency reduces ambiguity, but newcomers cannot search with a term they have not
learned. Recommended resolution: keep one preferred term in authoritative prose while
recording evidence-based aliases in a controlled retrieval mechanism. Do not make every
variant an equal editorial term.

### “A summary duplicates the body”

A poor summary can drift or merely repeat the title. A canonical short description can
also let readers discriminate between similar results before opening them. Recommended
resolution: define the summary's job and ownership, keep it concise, and validate it
against the body and actual result-recognition tasks.

### “One navigation hierarchy is simpler”

One hierarchy is easier to maintain, but the evidence shows different users prefer and
need different access routes. Recommended resolution: maintain a predictable default
structure plus only those alternate routes justified by a known audience or task.

### “Analytics scale better than user studies”

Logs expose population patterns cheaply after use has accumulated, but they often lack
the user's actual goal and cannot reveal whether an answer was correct. Recommended
resolution: use analytics to form hypotheses and select tasks; use observed task
performance and qualitative evidence to explain and validate them.

### “Small usability tests prove quality”

Small moderated studies are effective for finding and explaining problems. They do not
estimate success rates reliably for a broad population. Recommended resolution: use
iterative qualitative tests for discovery, larger repeated benchmarks when a numeric
claim matters, and always report the sample and context.

### “The same success threshold should apply to every document”

A glossary lookup, architecture orientation, and destructive recovery procedure have
different stakes and acceptable costs. Recommended resolution: keep the same outcome
dimensions but set task-specific correctness, efficiency, and risk thresholds.

### “Agent and human audiences can share one usability test”

The corpus declares both human roles and an `agent` audience, but the current research
sequence has put LLM-specific concerns aside. Human task evidence cannot establish
machine retrieval or generation performance, and an automated benchmark cannot
establish human comprehension. Recommended resolution: keep the evidence streams
separate and reconcile them only in a later LLM-specific pass.

## Claim ledger

| Claim | Main support | Counterevidence or boundary | Confidence |
|---|---|---|---|
| Documentation usability is an outcome for specified users, goals, and context, not a prose property | ISO 9241-11; ISO/IEC/IEEE 26514; NIST CIF | Inspection can identify attributes strongly associated with better use | High |
| Findability includes recognition and applicability, not only indexing or retrieval | Information-scent research; DITA short descriptions; W3C headings and link purpose; synthesis of task stages | No single cited standard defines findability with this exact six-stage model | High for principle; moderate for the model |
| Search evaluation should begin with information needs and relevance judgments | Stanford IR evaluation model | Large relevance sets are costly and relevance can be graded or disputed | High |
| Multiple access routes are justified when users have different needs | WCAG Multiple Ways; Digital.gov case study; heterogeneous documentation-use research | More routes increase maintenance cost and can reproduce the same blind spots | High for principle; moderate for the right Buzz set |
| Titles, summaries, headings, and link labels materially affect path prediction and scanning | SNIF-ACT; W3C; DITA; Google and Microsoft practitioner guidance | The strongest empirical navigation work is general web research, not this corpus | High for general principle |
| Effectiveness, efficiency, and satisfaction need complementary measures | ISO 9241-11; NIST CIF; GOV.UK benchmarking | Individual tasks can make a particular metric, especially time, inappropriate | High |
| Page-view and navigation logs are useful diagnostic evidence but not task-success proof | Nam et al. CHI 2024, including stated limitations | Instrumented end-to-end workflows could connect logs to stronger outcome data | High |
| Different experience and information-seeking strategies justify segmented tests | Meng et al.; Nam et al.; WCAG multiple ways | Evidence is concentrated in API/cloud documentation and accessibility contexts | Moderate to high |
| Buzz's current structured model lacks canonical search-preview and synonym fields | Direct node-schema and corpus-front-matter inspection | A future system could define deterministic body extraction without adding fields | High |
| Current validation cannot establish the corpus title contract | Direct validator and body inspection; two multiple-H1 nodes in the snapshot | A separate unpublished check could exist outside the inspected corpus tooling | High for the inspected tree |
| The proposed findability-to-outcome chain is a useful basis for the final checklist | Synthesis across ISO, NIST, IR, information scent, and local architecture | It has not been piloted with Buzz readers | Moderate |

## Limitations

- The local observations describe the working tree on 2026-09-06, not a release tag or
  a published documentation site. The research directory and an unrelated script were
  already untracked; no claim is made that this is a clean repository state.
- The count of 205 excludes schema fixtures and includes standards and templates that
  are themselves corpus nodes. The H1 scan ignored fenced code but was not a full
  CommonMark parser.
- The scan did not score title quality, heading predictiveness, link labels, reading
  level, or the semantic accuracy of relationships across all nodes. Those require
  sampled human review.
- No Buzz cohort member or other representative reader performed a task for this
  report. Local usability conclusions are therefore diagnoses of missing evidence and
  testability, not measured user performance.
- No live documentation search or generated navigation system exists in the inspected
  tree, so search metrics are a future evaluation design rather than a baseline result.
- ISO 9241-11 and ISO/IEC/IEEE 26514 expose definitions and limited public material;
  this report does not claim conformance to paid clauses.
- ISO/IEC/IEEE 26513:2017 is being revised. Its current replacement was at final-draft
  stage on the research date, so this report cites the published 2017 scope and does
  not adopt draft requirements.
- Information-scent experiments and the documentation-use studies involve general web
  or cloud/API contexts. Buzz's repository-oriented, operator-heavy context may produce
  different paths.
- GOV.UK sample-size and benchmarking guidance fits public digital services and is not
  adopted as a universal Buzz requirement. Study size should follow the question and
  the strength of claim needed.
- This report does not decide whether titles, descriptions, aliases, or task goals
  belong in front matter, a separate map record, a generated search index, or a
  deterministic body convention.
- Accessibility is addressed only where it directly changes navigation and content
  prediction. Topic 13 must broaden that analysis.

## Implications for the final synthesis

The final content-review checklist should have two visibly different layers:

1. **Designed-content checks** that an author, reviewer, or deterministic tool can
   perform: title structure, purpose cue, heading hierarchy, terminology, applicability,
   link purpose, index exposure, and testable metadata.
2. **Outcome evidence** from representative information needs and users: correct
   retrieval, recognition, answer or task completion, effort, error, recovery,
   confidence, and satisfaction.

Passing layer 1 should mean “the content contains the agreed contributors to usability
and is ready to test,” not “the documentation is usable.”

Before adopting new corpus fields or a search implementation, Buzz should pilot this
model on one bounded vertical slice with meaningful consequences. The pilot should:

1. select a small set of real developer, operator, and reviewer questions from current
   work;
2. preserve their natural wording and define correct, partial, wrong, and dangerous
   outcomes;
3. identify canonical and near-match nodes;
4. inspect titles, openings, headings, terminology, links, status, and audience cues;
5. create the smallest search/index/map prototype needed to expose those nodes;
6. run an offline relevance test and a small moderated task study;
7. record where each task failed in the findability-to-outcome chain;
8. change the responsible cue, content, architecture, or delivery layer;
9. repeat the same tasks; and
10. decide from observed value whether a canonical description, alias, applicability,
    or goal field is warranted.

This would test the central conclusion of the research: documentation becomes findable
and usable when its content supplies reliable cues and correct help, its delivery
exposes those cues from realistic starting points, and representative readers can turn
the result into a correct outcome.

## Sources

### Local corpus sources

- [`README.md`](../../docs/corpus/README.md)
- [`AGENTS.md`](../../docs/corpus/AGENTS.md)
- [`node.schema.json`](../../docs/corpus/schema/node.schema.json)
- [`naming.md`](../../docs/corpus/standards/naming.md)
- [`linking.md`](../../docs/corpus/standards/linking.md)
- [`documentation-standard.md`](../../docs/corpus/standards/documentation-standard.md)
- [`review-requirements.md`](../../docs/corpus/standards/review-requirements.md)
- [`generated-content.md`](../../docs/corpus/standards/generated-content.md)
- [`generated-index.md`](../../docs/corpus/templates/generated-index.md)
- [`confidence.md`](../../docs/corpus/standards/confidence.md)
- [`decision-references.md`](../../docs/corpus/standards/decision-references.md)
- [`validate.py`](../../project-intelligence/corpus/validate.py)
- [`VISION.md`](../../../VISION.md)
- [`launchpad/VISION.md`](../../VISION.md)
- [`05-information-architecture-for-atomic-documentation.md`](05-information-architecture-for-atomic-documentation.md)

### External standards and public-sector guidance

- [ISO 9241-11:2018 — Usability: Definitions and concepts](https://www.iso.org/standard/63500.html)
- [ISO 9241-115:2024 — Interaction and navigation design](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso%3A9241%3A-115%3Aed-1%3Av1%3Aen)
- [ISO/IEC/IEEE 26514:2022 — Design and development of information for users](https://www.iso.org/obp/ui?_escaped_fragment_=iso%3Astd%3Aiso-iec-ieee%3A26514%3Aed-1%3Av1%3Aen)
- [ISO/IEC/IEEE 26513:2017 — Requirements for testers and reviewers of information for users](https://www.iso.org/standard/67417.html)
- [NIST — Common Industry Format for Usability Test Reports](https://tsapps.nist.gov/publication/get_pdf.cfm?pub_id=151449)
- [GOV.UK — Usability benchmarking a website or whole service](https://www.gov.uk/service-manual/measuring-success/usability-benchmarking-a-website-or-whole-service)
- [GOV.UK — Usability testing: qualitative studies](https://www.gov.uk/guidance/usability-testing-qualitative-studies)
- [GOV.UK — Using moderated usability testing](https://www.gov.uk/service-manual/user-research/using-moderated-usability-testing)
- [Digital.gov — Card sorting and tree testing case study](https://digital.gov/2022/01/06/open-source-information-architecture-design-using-the-tools-you-have-to-conduct-card-sorting-and-tree-testing)
- [W3C — WCAG 2.2, Multiple Ways](https://www.w3.org/WAI/WCAG22/Understanding/multiple-ways.html)
- [W3C — WCAG 2.2, Headings and Labels](https://www.w3.org/WAI/WCAG22/Understanding/headings-and-labels)
- [W3C — WCAG 2.2, Link Purpose (In Context)](https://www.w3.org/WAI/WCAG22/Understanding/link-purpose-in-context.html)
- [OASIS DITA 1.3 — `shortdesc`](https://docs.oasis-open.org/dita/dita/v1.3/os/part2-tech-content/langRef/base/shortdesc.html)

### Research and practitioner sources

- [Manning, Raghavan, and Schütze — *Introduction to Information Retrieval*, evaluation](https://nlp.stanford.edu/IR-book/html/htmledition/evaluation-in-information-retrieval-1.html)
- [Fu and Pirolli — SNIF-ACT: A Cognitive Model of User Navigation on the World Wide Web](https://www.peterpirolli.com/Professional/About_Me_files/FuPirolli%20HCI%20SNIF-ACT%20(final).pdf)
- [Meng, Steinhardt, and Schubert — Application Programming Interface Documentation: What Do Software Developers Want?](https://journals.sagepub.com/doi/10.1177/0047281617721853)
- [Nam et al. — Understanding Documentation Use Through Log Analysis](https://cmustrudel.github.io/papers/chi2024doc_logs.pdf)
- [Google developer documentation style guide — Headings and titles](https://developers.google.com/style/headings)
- [Microsoft Style Guide — Scannable content](https://learn.microsoft.com/en-us/style-guide/scannable-content/)

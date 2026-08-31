---
id: corpus-template-test-strategy
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision a44cf52fc740ebebbdd671427480d14f0bce0115."
    entry_class: FACT
    evidence:
      - "commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "node.schema.json's type field is a closed enum of thirteen corpus surfaces (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion); none of the thirteen is template or policy, because the enum names the corpus surface a node documents, not the prose form its body takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every existing corpus node about how to author corpus content, rather than about a piece of verification/architecture/capability content itself, uses type: governance (README.md, standards/confidence.md, standards/decision-references.md, and the already-drafted templates/test-contract.md, templates/capability.md)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "The already-drafted templates/test-contract.md (issue #1349, unmerged PR #1540) states that a node built from it -- a single testable obligation paired with the specific test(s) that verify it -- carries type: verification, not type: governance; the template document describing that shape is itself governance, mirroring the same split this template makes for test-strategy instances."
    entry_class: FACT
    evidence:
      - "git_show('origin/task/1349-corpus-template-test-contract:launchpad/docs/corpus/templates/test-contract.md') -> front matter type: governance, body states 'Nodes authored from this template carry type: verification ... not type: governance', read 2026-08-27"
  - statement: "TESTING.md at the repository root documents just test-unit (no infrastructure) and just test (unit plus Postgres/Redis-backed integration, starting Docker if needed) as the two automated-test entry points, and states that neither runs the E2E suites in buzz-test-client, which are marked #[ignore] and require a running relay invoked as cargo test -p buzz-test-client -- --ignored."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "ADR-0020 records that upstream's testing methodology -- adopted unchanged by this repository -- has five levels separated by the infrastructure they need: unit (just test-unit, no infrastructure), integration (just test, Postgres and Redis started automatically), relay E2E (cargo test -p buzz-test-client -- --ignored, needs a running relay), desktop E2E smoke, and desktop E2E integration; every test needing a live relay is marked #[ignore] so a plain cargo test is safe everywhere and E2E execution is opt-in."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 states as a bad consequence, stated honestly, that required_status_checks on the launchpad branch returns 404 -- not configured -- so upstream's own words ('PRs that fail just ci will not be merged') are an honour system, not an enforced gate, and that ADR-0019 already ruled on what may gate and deferred enforcement to the CI/CD pipeline programme rather than reopening it here."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "ADR-0020 measured, on 2026-08-21 at launchpad tip db4305a4a, 4,615 Rust test functions across 28 of 30 crates, 37 integration test files, 19 relay E2E suites, 146 Playwright specs, 481 desktop *.test.mjs files, and 123 Flutter tests, and states this count explicitly as a snapshot at that revision rather than a timeless fact."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
  - statement: "crates/buzz-cli/TESTING.md is a manual live-testing runbook -- an agent or developer follows it step by step, running each CLI command against a locally started relay and checking the output -- distinct in kind from the automated just test-unit / just test / --ignored levels ADR-0020 and root TESTING.md describe."
    entry_class: FACT
    evidence:
      - "crates/buzz-cli/TESTING.md"
  - statement: "crates/buzz-test-client/tests/e2e_relay.rs's own module doc-comment states these are end-to-end integration tests requiring a running relay instance, marked #[ignore] by default so cargo test does not fail in CI when no relay is available, invoked as cargo test --test e2e_relay -- --ignored with RELAY_URL overridable."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/e2e_relay.rs"
  - statement: "The ISTQB Glossary defines test strategy as 'a high-level description of the test levels to be performed and the testing within those levels for an organization or programme (one or more projects)', and separately defines an analytical test strategy as one where the test team analyzes the test basis (e.g. product risk) to identify test conditions, and a methodical test strategy as one using a pre-determined set of test conditions such as a quality standard, checklist, or generalized domain-specific conditions."
    entry_class: FACT
    evidence:
      - "https://glossary.istqb.org/en_US/term/test-strategy"
  - statement: "The official ISTQB Glossary site (glossary.istqb.org) returned no readable page content when fetched directly for this node; the definition above was read from istqb-glossary.page's mirror of the same term, which itself states 'Original definition: Test Strategy @ISTQB Glossary' and links back to the official source -- the same shape of secondhand-citation disclosure #1329/capability.md made for TOGAF and #1348 made for ISO/IEC/IEEE 29148:2018, both blocked outright."
    entry_class: FACT
    evidence:
      - "https://istqb-glossary.page/test-strategy/"
  - statement: "Software Engineering at Google (the book, freely readable at abseil.io/resources/swe-book) states that small tests must run in a single process (in many languages, a single thread), may not sleep, perform I/O, or make blocking calls, and therefore may not access the network or disk; medium tests may span multiple processes and threads and may make blocking network calls, but only to localhost; large tests remove the localhost restriction, letting the test and the system under test span multiple machines -- a classification by infrastructure footprint (\"test size\"), independent of and orthogonal to naming a test \"unit\", \"integration\", or \"end-to-end\"."
    entry_class: FACT
    evidence:
      - "https://abseil.io/resources/swe-book/html/ch11.html"
  - statement: "ADR-0020's five levels -- unit/no infrastructure, integration/Postgres+Redis on localhost via Docker, relay E2E and desktop E2E/a live multi-process relay -- map onto Google's small/medium/large test-size axis in the same order (small, medium, large respectively), even though ADR-0020 does not itself use or cite Google's size vocabulary anywhere in its text."
    entry_class: INFERENCE
    evidence:
      - "launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md"
      - "https://abseil.io/resources/swe-book/html/ch11.html"
    confidence: 0.75
  - statement: "A grep of the unmerged research note (launchpad/Research/project-documentation-templates.md, branch docs/research-project-doc-templates, tip b0553469d9dff25eb3636ce1d0400e60dca1b559) for 'test strategy' and 'test-strategy' case-insensitively returns zero matches, so #1350's topic is not covered by that note at all."
    entry_class: FACT
    evidence:
      - "grep_case_insensitive('test strategy|test-strategy', path='launchpad/Research/project-documentation-templates.md', ref='b0553469d9dff25eb3636ce1d0400e60dca1b559') -> zero matches, run 2026-08-27"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of the batch-1/2/3/4 template PRs (#1527-#1548) nor this batch's own siblings (#1330, #1338, #1339, #1341, #1344) nor #1349 (test-contract, PR #1540) nor #1325 (test-references, PR #1524) are merged, so none of them are valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/**, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1350's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1350's Definition of Done carries the same generic-policy DoD bullets (states scope and authority/source of the policy, separates MUST from SHOULD, defines enforcement/checks and exception/escalation, links decisions or higher-order policy instead of duplicating them) as the standards-track issues (#1307-#1325), even though #1350 is a template task rather than a policy task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1350 definition of done, compared against #1309's and #1312's"
  - statement: "Issue #1349 (test-contract, unmerged PR #1540) is the open task for a narrower, differently-scoped node type -- one testable obligation paired with the specific automated test(s) that verify it -- not the overall multi-tier testing approach for a system or component that this template's issue title (test-strategy) names."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1349 title and PR #1540 body, compared against this template's #1350 title"
  - statement: "Issue #1325 (test-references, unmerged PR #1524) is the open task for a corpus-wide standard governing how any node cites a test as evidence -- citation shapes, flakiness and staleness caveats -- not a node type of its own, and not scoped to a strategy-shaped node specifically."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1325 title and PR #1524 body, compared against this template's #1350 title"
---

# Template: `test-strategy`

How to author a corpus node that documents the overall **multi-tier testing approach**
for a system or a component within it: which test levels apply, what each needs to run,
what is deliberately left untested and why, and how those levels together are meant to
build confidence. This document does not produce a policy: it produces a shape a real
test-strategy node must fill in, and this document names that shape.

## Note on this document's structure

Issue #1350's definition-of-done text -- "states scope and authority/source of the
policy," "separates MUST requirements from SHOULD guidance," "defines
enforcement/checks and exception/escalation process," "links decisions or
higher-order policy instead of duplicating them" -- describes a **policy/standard**
node (compare it to issues #1309 and #1312, which carry the identical bullets and
produced `standards/confidence.md` and `standards/decision-references.md`). A
template is not a policy: it does not regulate corpus-wide behaviour, and it has no
MUST/SHOULD split of its own to state. This document is built against #605's real
acceptance criterion for a template instead -- *purpose, required sections, evidence
expectations, and the industry model/standard it adapts* -- and the section headings
below map to those four things directly. The DoD's other bullets (one hand-authored
document, schema-valid front matter, one independently maintainable idea, traceable
claims, links instead of duplication, checked against provenance, clean validation)
are generic to any corpus node and this document satisfies them the same way any node
does.

## Purpose

A node built from this template answers one question: **for this system or
component, what is the plan for testing it, tier by tier?** It is not one test, and
it is not one obligation -- it is the map that says which levels exist, what
infrastructure each needs, what gates a merge today and what does not, and what is
deliberately out of scope at every level (not merely "not gotten to yet").

**Nodes authored from this template carry `type: verification`** -- the
corpus-surface enum value PRD #602 defines for verification content -- not
`type: governance`. This template document itself is `governance`, because it is a
meta-document about *how to write* a test-strategy node, mirroring `templates/
test-contract.md`'s identical split for its own instance type. Do not copy this
document's own front-matter `type` into a node built from it.

If what is being documented is one testable obligation and the specific test that
proves it, or the general mechanics of how any corpus node cites a test as evidence,
that is not this template -- see *Boundary against neighboring corpus content* below.

## The industry model(s) this template adapts

**Two distinct industry concepts are relevant here, and they answer different
questions.** Conflating them is the specific mistake this section exists to prevent.

**ISTQB's `test strategy`** is "a high-level description of the test levels to be
performed and the testing within those levels for an organization or programme" --
deliberately about *which levels exist and what happens within them*, not about a
single test's technical constraints. ISTQB also names named strategy *types* --
analytical (test conditions derived from analyzing the test basis, commonly
risk-based), methodical (a pre-determined set of conditions such as a checklist or
domain-specific standard), and others -- as ways an organization arrives at its
levels and priorities. This template adapts ISTQB's core framing (a strategy names
levels and what happens within them) but does not adopt its fuller strategy-type
taxonomy; see *Scope and omissions* for why.

**Google's `test size`** (documented in *Software Engineering at Google*, freely
readable) is a different, narrower idea that is easy to mistake for the same thing:
small, medium and large tests are classified strictly by their **infrastructure
footprint** -- small tests run single-process (often single-thread) with no sleep,
I/O, network, or disk access; medium tests may span processes and threads and may
make blocking network calls, but only to `localhost`; large tests drop even that
restriction and may span multiple machines. This is orthogonal to calling a test
"unit," "integration," or "end-to-end" by name -- it is a classification by what a
test is *allowed to touch*, not by what layer of the system it exercises.

**This repository already has a real, accepted, already-written test strategy at the
whole-repository level, and this template adapts its shape rather than importing
either industry model wholesale.** ADR-0020 records upstream's testing methodology,
adopted unchanged: five levels **separated by the infrastructure they need** -- unit
(`just test-unit`, none), integration (`just test`, Postgres and Redis on
`localhost`), relay E2E and desktop E2E (a live, multi-process relay). Read against
Google's size axis, those five levels line up small → medium → large in the same
order ADR-0020 already orders them in, even though ADR-0020 itself never invokes
Google's vocabulary -- that alignment is this template's own inference, not a claim
ADR-0020 makes about itself. **What this template actually adapts is ADR-0020's own
shape**: name each level, state the infrastructure it needs, state the command that
invokes it, state whether it currently gates a merge, and say so honestly when it
does not -- ADR-0020 itself records, as a stated bad consequence, that
`required_status_checks` on `launchpad` returns 404 (not configured), so upstream's
own "PRs that fail `just ci` will not be merged" is an honour system today, not an
enforced gate. A test-strategy node that claims enforcement it does not have would
repeat exactly the gap ADR-0020 was written to make visible.

## Boundary against neighboring corpus content

This template covers **the overall shape of a system or component's testing
approach, across levels**. It does not cover:

- **One testable obligation and the specific test(s) that verify it.** That is
  `#1349`'s template (`test-contract`, unmerged PR #1540) -- the corpus's smallest
  verification unit, narrower than a whole strategy or a whole level. A
  test-strategy node names that such obligations exist at a given level and may
  `references` the `test-contract` nodes that instantiate them once they exist; it
  does not restate any one obligation's own detail.
- **How any corpus node should cite a test as evidence.** That is `#1325`'s open,
  unlanded standard (`test-references`, unmerged PR #1524) -- general citation
  mechanics (shapes, flakiness and staleness caveats) for the whole corpus, not a
  node type. A test-strategy node cites its levels' tests and counts the same way
  any corpus node cites evidence today, per `AGENTS.md`; once #1325 lands, it
  governs those citations more specifically, and this template does not restate its
  rules.
- **Developer-facing runbooks for how to actually run tests.** `TESTING.md` (root)
  and `crates/buzz-cli/TESTING.md` are step-by-step instructions a developer or
  agent follows directly. A test-strategy node cites them as the source for what a
  level's invocation command is; it does not reproduce their command-by-command
  content.
- **The decision that established a testing methodology.** `ADR-0020` is an accepted
  decision record documenting *why* this repository's methodology looks the way it
  does and what the cohort chose to adopt versus design. A corpus node about Buzz's
  own overall test strategy would `references` `ADR-0020` rather than restate its
  reasoning, per `AGENTS.md`'s links-not-duplication rule -- the same move
  `templates/test-contract.md` and `templates/capability.md` both already make for
  their own adjacent decision records and design docs.

## Required sections

A node built from this template MUST contain the following. These are structural
requirements on the node's shape, not a corpus-wide MUST/SHOULD policy -- see *Note
on this document's structure* above for why this document does not carry one of
those.

1. **A scope statement** naming the exact system or component this strategy covers
   (a crate, a client, or the whole repository), and stating explicitly that the
   node's strategy applies to that scope only.

2. **A levels table**, one row per test level in scope, each row naming: the level's
   purpose, the infrastructure it needs (none, `localhost` services, a live
   multi-process system -- the same infrastructure-footprint axis Google's test-size
   framework and ADR-0020's own level split both use), the exact command that
   invokes it, and whether it is gated (`#[ignore]`, an opt-in flag, manual-only) or
   runs unconditionally.

3. **Current enforcement status per level**, stated honestly: which levels currently
   run in CI, which of those are required checks a PR cannot merge past, and which
   run in CI but are not (yet) required. Do not claim a level "gates merges" unless
   it is a required status check -- ADR-0020's own finding that `launchpad` has none
   configured is the concrete reason this distinction matters here specifically.

4. **What is deliberately out of scope, and why.** A level or a kind of coverage the
   strategy has consciously chosen not to build (a risk/coverage tradeoff), not a gap
   the author simply has not gotten to. Say what risk is accepted by leaving it out.

5. **Relationships**, per the guidance below.

6. **A scope-and-omissions section**, per `AGENTS.md`'s own required step 8: what the
   node does not cover and who owns it, and separately, what was expected to be
   verified when the node was written and could not be.

### A minimal worked skeleton

Illustrative only -- this is not itself a validated corpus node, and the bracketed
placeholders are not literal content.

```markdown
---
id: test-strategy-<system-or-component-slug>
type: verification
status: draft
origin: launchpad
audiences:
  - agent
  - developer
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision <sha>."
    entry_class: FACT
    evidence:
      - "commit <sha>"
relationships:
  - type: references
    target: <adr-or-design-doc-id, once one exists as a corpus node>
---

# <System or component> — test strategy

## Scope

[One paragraph: the exact system or component this strategy covers, and that it
covers that scope only.]

## Levels

| Level | Purpose | Infrastructure | Command | Gating |
|---|---|---|---|---|
| [unit] | [what it exercises] | [none / localhost / live system] | [\`just test-unit\`] | [runs unconditionally / #[ignore]d / opt-in] |
| ... | ... | ... | ... | ... |

## Current enforcement

[Which of the levels above are required status checks today, which run in CI but
are not required, and which are manual-only. Say so even when the honest answer is
"none are required yet."]

## Deliberately out of scope

[What this strategy does not test, and the risk accepted by leaving it out. Not
"not done yet" -- a conscious choice, stated as one.]

## Relationships

- references: <the ADR, design doc, or higher corpus node this strategy's choices
  trace back to, if one exists>
- references: <test-contract nodes instantiating specific obligations at one of the
  levels above, once they exist>

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
```

## Evidence expectations

The corpus-wide `FACT`/`INFERENCE`/`TEAM_KNOWLEDGE` rules in `AGENTS.md` apply
unchanged. Two things are specific to a test-strategy node and worth stating
plainly:

- **A level's test count, or "N tests exist at this level," is a claim with a short
  shelf life.** `ADR-0020`'s own count is dated explicitly ("Measured on
  2026-08-21 at launchpad tip `db4305a4a`") rather than stated as timeless -- follow
  that convention. A count cited without the revision it was measured at is a stale
  claim waiting to happen.
- **"This level currently gates merges" is a `FACT` or nothing**, and it needs
  evidence beyond a CI workflow file existing -- a workflow running a check and that
  check being *required* before merge are different facts (branch protection or
  ruleset configuration, not the workflow file alone). ADR-0020's own 404 finding
  for `required_status_checks` on `launchpad` is exactly the citation shape this
  claim needs: check the actual gate, not the presence of a job.

## Relationships

**Checked, not assumed absent.** Per `AGENTS.md`, "no relationships, because nothing
exists to point at" is a false justification this corpus has already produced
before, so this section names what was actually checked: at the recorded revision,
`origin/launchpad`'s corpus tree carries `corpus-agents`, `corpus-readme`,
`corpus-standard-confidence` and `corpus-standard-decision-references`, and no other
node. None of the four is specific to test-strategy content over any other node's
evidence, so an edge from this template to any of them would say nothing a reader
does not already get from `AGENTS.md`'s own cross-references.

**This template declares none.** The two most relevant future edges --
`#1349`/`test-contract` (a test-strategy node would `references` the
`test-contract` nodes that instantiate its levels' obligations) and `#1325`/
`test-references` (a test-strategy node's citation discipline would lean on that
standard directly, the same way `templates/test-contract.md` leans on it) -- both
name open, unmerged issues with no corresponding node on `origin/launchpad` yet.
None is a valid answer while the targets do not exist; the first of those two to
land is the moment to revisit this template's own relationships.

**A node built from this template** should expect to declare `references` toward
whatever ADR, design document or higher corpus node its level choices trace back to
(for Buzz's own overall strategy, that would be `ADR-0020` once accepted-decision
citation lands a node for it), toward `test-contract` nodes instantiating specific
obligations at one of its levels, and possibly `implements` toward this template
node itself once template nodes carry a stable enough identity for that
directionality to make sense. This template does not mandate specific edges -- the
corpus is still too sparse for a rule about what must exist to make sense.

## Scope and omissions

**This document covers** the purpose of a `test-strategy` corpus node, the two
industry models considered (ISTQB's strategy framing and Google's test-size axis)
and how they differ, the real precedent this repository already has (ADR-0020) and
why this template adapts its shape rather than importing either industry model
wholesale, its boundary against `test-contract` (one obligation), `test-references`
(citation mechanics), the developer-facing testing runbooks, and ADR-0020 itself,
its required sections, what evidence a test-strategy node needs, and what
relationships this template document itself does and does not declare.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| One testable obligation and its verifying test | `#1349` (`test-contract`), open, unmerged |
| How any corpus node should cite a test as evidence, generally | `#1325` (`test-references`), open, unmerged |
| Step-by-step instructions for running tests | `TESTING.md`, `crates/buzz-cli/TESTING.md` |
| Why this repository's testing methodology looks the way it does | `launchpad/decisions/ADR-0020-adopt-upstream-testing-methodology.md` |
| What may gate a merge at all | `launchpad/decisions/ADR-0019-review-checks-gate-only-when-deterministic.md`, deferred further by ADR-0020 to the CI/CD pipeline programme |
| The corpus's general evidence contract and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| Creating, updating and retiring any corpus node, including one built from this template | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No real `test-strategy` node has been built from this template yet.** Whether
  the required-sections list holds up for a component much smaller or much larger
  than "the whole repository" (the scale ADR-0020 operates at) is untested.
- **ISTQB's fuller strategy-type taxonomy (analytical, methodical, process-
  compliant, reactive/exploratory, consultative) was read at the term-definition
  level only, not adopted into this template's required sections**, because this
  repository's own real precedent (ADR-0020) does not name or organize itself
  around those types; if a future test-strategy node wants to state which ISTQB
  strategy type it follows, this template does not prevent that, it simply does
  not require it.
- **The official ISTQB Glossary site (`glossary.istqb.org`) could not be read
  directly** -- it returned no usable page content when fetched for this node. The
  ISTQB definition cited above was read via a mirror (`istqb-glossary.page`) that
  itself attributes the definition to ISTQB's glossary; the mirror's wording was
  not independently cross-checked against the original site.
- **Google's test-size framework was read from the *Software Engineering at
  Google* book (`abseil.io`), not from Google's original 2010 Testing Blog post**,
  which returned only its title and comment thread when fetched, not its body
  text. The book is the same organization's own later, fuller restatement of the
  same concept, but the two were not diffed against each other for wording drift.
- **Whether ADR-0020's five levels actually align one-to-one with Google's small/
  medium/large axis was reasoned from each document's own description of
  infrastructure needs, not from running any test and classifying it directly.**
  That alignment is recorded above as an `INFERENCE`, not a `FACT`, for that reason.

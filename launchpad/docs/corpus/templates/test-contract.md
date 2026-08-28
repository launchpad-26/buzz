---
id: corpus-template-test-contract
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
  - statement: "node.schema.json's type field is a closed enum of thirteen corpus surfaces (architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion), and contains no template or policy member."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Every existing corpus node about how to author corpus content, rather than about a piece of architecture/capability/etc. content itself, uses type: governance (README.md, standards/confidence.md, standards/decision-references.md) or type: agent (AGENTS.md, the one node that is itself an agent-facing procedure)."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "PRD #602's success criteria list verification as one of the in-scope corpus surfaces, alongside architecture, layers, capabilities, platforms, implementation, interfaces/events, operations, development, release, governance, agent and ingestion, and node.schema.json's type enum reuses that same list verbatim."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#602 success criteria, compared against node.schema.json's type enum"
  - statement: "schema/COMPATIBILITY.md's rule governs adding a field, enum value or narrowed type to node.schema.json or relationships.schema.json, and records no prior addition or precedent of a template or policy type value."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/COMPATIBILITY.md"
  - statement: "At the recorded revision, origin/launchpad's launchpad/docs/corpus subtree contains exactly four validated nodes outside schema/: AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md."
    entry_class: FACT
    evidence:
      - "git_ls_tree(origin/launchpad, 'launchpad/docs/corpus') -> AGENTS.md, README.md, schema/** (excluded from validation), standards/confidence.md, standards/decision-references.md"
  - statement: "validate.py excludes only the schema/ top-level subdirectory from corpus discovery and validation, so a node placed under launchpad/docs/corpus/templates/ is discovered and validated exactly like any other corpus node."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "TESTING.md documents this repository's actual test practice as unit tests, Postgres/Redis-backed integration tests, and #[ignore]-gated end-to-end suites in buzz-test-client run against a live relay built from the same source tree and the same release binaries the CLI, desktop and mobile clients ship; it names no separately-deployed provider verified against a consumer-published contract file."
    entry_class: FACT
    evidence:
      - "TESTING.md"
  - statement: "crates/buzz-test-client/tests/conformance_multitenant.rs is, in its own module doc-comment, described as mirroring the obligation table in docs/multi-tenant-conformance.md one row per module, and is called 'the executable form of the conformance contract.'"
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "docs/multi-tenant-conformance.md is a prose table of conformance obligations (one row per relay surface), each row stating today's observable behavior, the required scoping change, and an 'Open decision/test' column naming what a test still has to prove."
    entry_class: FACT
    evidence:
      - "docs/multi-tenant-conformance.md"
  - statement: "conformance_multitenant.rs implements one Rust module per obligation row (e.g. mod row_zero_host_binding), marks not-yet-landed obligations #[ignore] by default, and stubs them with a pending_lane(...) helper that panics via todo!() naming the exact obligation, so an empty test body can never pass as a completed obligation."
    entry_class: FACT
    evidence:
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
  - statement: "crates/buzz-conformance/TRACE_SCHEMA.md opens by calling itself 'the contract between the relay's emitter and the independent replay checker,' grounded in docs/spec/MultiTenantRelay.tla, and states the rule that changing the schema requires changing that document in the same commit."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/TRACE_SCHEMA.md"
  - statement: "buzz-conformance's checker re-implements the TLA+ spec's transition relation independently of the relay's production reducer, specifically so a bug shared between an emitter and a checker built from the same helpers cannot hide from both, and crates/buzz-conformance/LIMITS.md states the gate proves only that traced executions matched the spec, not that every code path was exercised."
    entry_class: FACT
    evidence:
      - "crates/buzz-conformance/src/lib.rs"
      - "crates/buzz-conformance/LIMITS.md"
  - statement: "Pact (docs.pact.io) describes itself as a code-first consumer-driven contract testing tool: a consumer application's own tests generate the contract, and a separate provider application is verified against it independently, most often through a shared Pact Broker; the Pact Specification is a real versioned artifact currently at version 4."
    entry_class: FACT
    evidence:
      - "https://docs.pact.io/"
      - "https://github.com/pact-foundation/pact-specification"
  - statement: "AGENTS.md's 'Nostr-first HTTP surface' section and TESTING.md both describe Buzz as one relay binary tested end-to-end against its own CLI/desktop/mobile clients built from the same source tree, not as a set of independently deployed services each owned by a separate consumer or provider team publishing a contract file to a broker for independent verification."
    entry_class: FACT
    evidence:
      - "AGENTS.md"
      - "TESTING.md"
  - statement: "Pact's consumer-driven model does not fit this repository's actual test-contract precedent, because Buzz has no separately-deployed provider verified independently from its consumers against a broker-published contract file; the closer, already-real, already-verified model is this repository's own obligation-table-plus-executable-test pairing (docs/multi-tenant-conformance.md / conformance_multitenant.rs) and its trace-schema-as-contract pairing (buzz-conformance/TRACE_SCHEMA.md / checker.rs), so this template adapts those rather than importing Pact's broker/consumer/provider vocabulary."
    entry_class: INFERENCE
    evidence:
      - "https://docs.pact.io/"
      - "docs/multi-tenant-conformance.md"
      - "crates/buzz-test-client/tests/conformance_multitenant.rs"
      - "crates/buzz-conformance/TRACE_SCHEMA.md"
    confidence: 0.85
  - statement: "type: governance is the closest true fit for this node, because it is a meta-document about how to author a test-contract corpus node rather than itself being verification content, mirroring the same reasoning README.md, standards/confidence.md and standards/decision-references.md already apply to their own meta-documents against the same enum."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/docs/corpus/README.md"
    confidence: 0.8
  - statement: "Parent Feature #605 states, as one of its own acceptance criteria, that every template states its purpose, required sections, evidence expectations and the industry model or standard it adapts."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605 acceptance criteria"
  - statement: "Issue #1349's definition of done carries the same generic-policy DoD bullets (scope/authority, MUST-vs-SHOULD, enforcement/escalation, links-not-duplication) as the standards-track issues, even though #1349 is a template task rather than a policy task."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1349 definition of done, compared against launchpad-26/buzz#1309's and #1312's"
  - statement: "Issue #1325 is the open, unlanded task to document the corpus standard for how any node cites a test as evidence generally, and is a different, narrower concern than this template's subject: one node type whose entire content is a single obligation and the specific test(s) that verify it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1325 title, compared against this template's scope"
---

# Template: `test-contract`

How to author a corpus node that documents one **testable obligation** a piece of Buzz
must satisfy, paired with the specific automated test(s) that verify it and that
obligation's current enforcement status. This document does not produce a policy: it
produces a shape a real test-contract node must fill in, and this document names that
shape.

## Note on this document's structure

Issue #1349's definition-of-done text — "states scope and authority/source of the
policy," "separates MUST requirements from SHOULD guidance," "defines
enforcement/checks and exception/escalation process," "links decisions or
higher-order policy instead of duplicating them" — describes a **policy/standard**
node (compare it to issues #1309 and #1312, which carry the identical bullets and
produced `standards/confidence.md` and the still-open diagrams standard). A template is
not a policy: it does not regulate corpus-wide behaviour, and it has no MUST/SHOULD
split of its own to state. This document is built against #605's real acceptance
criterion for a template instead — *purpose, required sections, evidence expectations,
and the industry model/standard it adapts* — and the section headings below map to
those four things directly. The DoD's other bullets (one hand-authored document,
schema-valid front matter, one independently maintainable idea, traceable claims, links
instead of duplication, checked against provenance, clean validation) are generic to any
corpus node and this document satisfies them the same way any node does.

## Purpose

A node built from this template answers one question: **what must stay true, and which
test proves it stays true?** It is the corpus's smallest verification unit — narrower
than a whole test suite or a testing policy, and narrower than the system-level
`verification` surface generally. One test-contract node covers **one obligation**: a
single testable statement about behaviour (an invariant, an isolation guarantee, a
compatibility promise) plus the concrete test(s) that currently exercise it and whether
those tests currently pass, are gated (`#[ignore]`), or are still stubbed pending
unlanded work.

**Nodes authored from this template carry `type: verification`** — the corpus-surface
enum value PRD #602 defines for verification content — not `type: governance`. This
template document itself is `governance`, because it is a meta-document about *how to
write* a test-contract node, not a piece of verification content. Do not copy this
document's own front matter `type` into a node built from it.

If what is being documented is a whole test suite's shape, a general testing policy
("how we write integration tests in this repo"), or a citation mechanic for referencing
tests as evidence from *any* corpus node, that is not this template — see *Boundary
against neighboring corpus content* below.

## The industry model this template adapts

**The obvious candidate does not fit, and this section says so rather than forcing it.**
Pact (`docs.pact.io`) is real, actively maintained, and genuinely versioned — the Pact
Specification is at version 4 — and it is the closest thing the industry has to a named
standard for "a contract a test proves." But Pact's actual mechanism is
**consumer-driven contract testing**: a consumer application's own tests generate a
contract file, and a *separately deployed* provider application is verified against
that file independently, typically through a shared Pact Broker. That model assumes two
things this repository does not have: a provider that ships and is deployed separately
from its consumers, and a consumer whose only access to the provider's real behaviour is
the contract file rather than the provider's own source.

Buzz does not look like that. `TESTING.md` and `AGENTS.md`'s "Nostr-first HTTP surface"
section both describe one relay binary, built from this same source tree, tested
end-to-end against the CLI, desktop and mobile clients that are *also* built from this
same source tree — `crates/buzz-test-client`'s e2e suites run a real relay and a real
client in the same repository, the same commit, the same CI run. There is no separately
versioned provider a consumer verifies against out-of-band. Forcing Pact's
consumer/provider/broker vocabulary onto that shape would misdescribe it.

**What this repository already has, and what this template adapts instead**, is two
real, already-built precedents for exactly the thing a "test contract" needs to be:

1. **`docs/multi-tenant-conformance.md` paired with
   `crates/buzz-test-client/tests/conformance_multitenant.rs`.** The Markdown document
   is a table of obligations, one row per relay surface, each stating today's observable
   behaviour and what a test still has to prove. The Rust file mirrors it **one module
   per row** and calls itself, in its own doc-comment, "the executable form of the
   conformance contract." An obligation not yet backed by a real test is not silently
   missing — it is `#[ignore]`d and stubbed with a `pending_lane(...)` helper that
   panics via `todo!()` naming the exact obligation, so a green run can never be faked by
   an empty test body.
2. **`crates/buzz-conformance/TRACE_SCHEMA.md` paired with `checker.rs` and
   `transitions.rs`.** This document opens by calling itself, verbatim, "the contract
   between the relay's emitter and the independent replay checker." It documents a
   schema, the actions that can appear in a trace, and a rule that changing the schema
   requires changing this document in the same commit. The checker deliberately
   re-implements the specification's transition relation rather than reusing the
   relay's own helpers, specifically so a bug shared between production code and its own
   checker cannot hide from both — and `LIMITS.md` states plainly what a green run does
   and does not prove (only the executions that were actually traced, never full code-path
   coverage).

Both precedents share the same shape a Pact contract has in spirit — a documented
promise, checked by an automated test, with an explicit statement of what "checked"
does and does not mean — without either of Pact's two structural assumptions
(a separately deployed provider, a broker-mediated handoff). This template adapts that
shared shape: **obligation statement, verifying test, current enforcement status,
explicit limits**, rather than importing consumer/provider/broker terms that do not
name anything in this codebase.

## Boundary against neighboring corpus content

This template covers **one obligation and its verifying test(s)**. It does not cover:

- **A whole test suite's structure or how to write tests generally** — that is
  developer-facing testing guidance (`TESTING.md` at the repo root,
  `crates/buzz-cli/TESTING.md` for the CLI), not a corpus node.
- **How any corpus node should cite a test as evidence** — that is issue #1325's open,
  unlanded standard (`document corpus standard for test references`), which is
  general citation mechanics for the whole corpus, not a node type. This template does
  not depend on #1325 landing; a test-contract node cites its verifying test the same
  way any corpus node cites executable evidence today, per `AGENTS.md`.
- **A whole conformance table like `docs/multi-tenant-conformance.md` itself** — that
  document covers many obligations across many relay surfaces in one file, by design,
  because it is a migration checklist. A corpus test-contract node is the opposite
  granularity: it exists precisely so **one** obligation gets its own independently
  maintainable node, per `AGENTS.md`'s one-node-one-idea rule. A large conformance
  document like that one is a *source* a test-contract node cites, not a shape this
  template asks a node to reproduce wholesale.
- **A decision about whether an obligation should exist at all** — that is an ADR or a
  PRD, referenced by a test-contract node via a `references` edge once one exists to
  point at, not restated inside it.

## Required sections

A node built from this template MUST contain the following. These are structural
requirements on the node's shape, not a corpus-wide MUST/SHOULD policy — see *Note on
this document's structure* above for why this document does not carry one of those.

1. **A purpose and boundary statement.** One paragraph naming the single obligation in
   scope and stating explicitly that the node covers that obligation only.

2. **The obligation statement itself**, as one precise, testable sentence — the same
   register as a row in `docs/multi-tenant-conformance.md`'s table (e.g. "an
   unknown/unmapped host fails closed with a generic rejection and never falls through
   to a default tenant"). A vague obligation ("the system should be secure") is not
   testable and does not belong in this template.

3. **The verifying test(s)**, named exactly — file path, and the test function or
   module name, not a paraphrase. If more than one test contributes (a unit test plus an
   integration test, for example), list all of them and say what each one covers.

4. **How to run the verifying test(s)**, as a copy-pasteable command. If the test is
   gated (`#[ignore]`, requires infrastructure, requires a live relay), name the gate and
   how to satisfy it, following the pattern `conformance_multitenant.rs`'s own module
   doc-comment already uses for its `--ignored` suite.

5. **Current enforcement status**, stated honestly as one of: verified (the test exists,
   runs unconditionally in CI, and currently passes), gated (the test exists but is
   `#[ignore]`d or otherwise conditionally skipped, naming the condition), or pending
   (no real test exists yet; the obligation is stubbed, `todo!()`-panicking, or tracked
   only by an issue). A pending obligation documented here is not weaker for saying so —
   claiming "verified" for a stubbed obligation is the one failure mode this section
   exists to prevent.

6. **An evidence ledger entry for the obligation claim and for the test's current
   behaviour**, each independently checked — do not cite the test file as evidence that
   the obligation is *true*; the test file is evidence of what is *checked*, and running
   it (or reading its current pass/fail/ignore state) is what establishes enforcement
   status. Follow `launchpad/docs/corpus/AGENTS.md`'s FACT/INFERENCE/TEAM_KNOWLEDGE rules
   exactly as any other corpus node does; this template adds no second evidence
   contract.

7. **A limits/scope-and-omissions section** naming, explicitly, what the verifying
   test does and does not prove — mirroring `buzz-conformance/LIMITS.md`'s own move of
   stating plainly what a green run does not mean. A test that runs against one
   scenario does not prove the obligation for every scenario; say which scenarios were
   actually exercised.

## Evidence expectations

Two things are specific to a test-contract node and worth stating plainly, on top of the
general FACT/INFERENCE/TEAM_KNOWLEDGE rules `AGENTS.md` already owns:

- **"This test currently passes" is a behaviour claim with a short shelf life.** It
  needs executable evidence checked at the node's recorded revision — the actual test
  run, or the test file's current `#[ignore]`/`todo!()` state — not a memory of it
  passing once. `standards/decision-references.md`'s behaviour-versus-intent test
  applies here unchanged: if a design document says an obligation is enforced and the
  test file shows it `#[ignore]`d and stubbed, the test file is the one a reader would
  call correct.
- **"This is the right test for this obligation" can legitimately be an INFERENCE.**
  Deciding that a given test actually exercises the stated obligation, rather than
  something adjacent to it, sometimes takes judgement the test's own assertions do not
  fully close on their own — rate that judgement honestly per
  `standards/confidence.md`'s bands rather than defaulting to FACT because the test name
  sounds right.

## Relationships

**Checked, not assumed absent.** Per `AGENTS.md`, "no relationships, because nothing
exists to point at" is the exact false justification this corpus has already produced
twice, so this section names what was actually checked: at the recorded revision,
`origin/launchpad`'s corpus tree carries `corpus-agents`, `corpus-readme`,
`corpus-standard-confidence` and `corpus-standard-decision-references`, and no other
node. A `references` edge from this template to `corpus-agents` would validate today —
this template's evidence-expectations section leans on `AGENTS.md`'s rules directly.

**This template declares none anyway.** None of `corpus-standard-confidence` or
`corpus-standard-decision-references` is specific to test-contract content over any
other node's evidence, so an edge here would say nothing a reader does not already get
from `AGENTS.md`'s own cross-references. Issue #1325 (test-reference citation standard)
would be the most relevant future edge, but it is open and unlanded, so no node exists
yet to target — the standard boundary rule applies: none is a valid answer while the
target does not exist. The first landed node that is specific to test-contract content
is the moment to revisit this.

**A node built from this template** should expect to declare `implements` (pointing at
this template, once template nodes carry a stable enough identity for `implements`'
"template instance of a standard" directionality to make sense) and possibly
`references` toward a decision or PRD that established the obligation. This template
does not mandate specific edges — the corpus is still too sparse for a rule about what
must exist to make sense.

## A minimal worked skeleton

Illustrative only — this is not itself a validated corpus node, and the ellipses are not
literal.

```markdown
---
id: test-contract-<obligation-slug>
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
  - statement: "<obligation, stated as one testable sentence>."
    entry_class: FACT
    evidence:
      - "<path/to/verifying_test.rs>"
  - statement: "<verifying test>'s current state is <passing unconditionally in CI | #[ignore]d pending X | todo!()-stubbed pending lane Y>."
    entry_class: FACT
    evidence:
      - "<path/to/verifying_test.rs>"
---

# <Obligation name> — test contract

## Purpose and boundary

One paragraph: the single obligation this node documents, and that this node covers
only that obligation.

## Obligation

> <One precise, testable sentence.>

## Verifying test(s)

- `<path/to/verifying_test.rs>` — `<module::test_fn>` — covers <what>.

## How to run it

\`\`\`bash
cargo test -p <crate> --test <test-binary> -- <filter>
\`\`\`

## Current enforcement status

<verified | gated | pending>, as of <sha>. <One sentence saying why.>

## Limits

What this test does and does not prove. Name the scenarios actually exercised, and any
scenario the obligation statement implies but the test does not reach.

## Scope and omissions

This node covers <obligation> only. It does not cover <related obligation>, tracked at
<link once it exists>.
```

## Scope and omissions

**This document covers** the purpose of a `test-contract` corpus node, the industry
model it adapts (and the one it explicitly rejected, with the reasoning for why), its
boundary against test-suite documentation, the test-reference citation standard, whole
conformance tables, and decision records, its required sections, what evidence a
test-contract node needs, and what relationships this template document itself does and
does not declare.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| How any corpus node should cite a test as evidence, generally | Issue #1325, open, unlanded |
| Developer-facing guidance on writing tests in this repository | `TESTING.md`, `crates/buzz-cli/TESTING.md` |
| The corpus's general evidence contract and citation shapes | `launchpad/docs/corpus/AGENTS.md`, `launchpad/project-intelligence/CONTRACT.md` §3 |
| The `confidence` field's meaning and bands | `launchpad/docs/corpus/standards/confidence.md` |
| Citing an accepted decision as evidence | `launchpad/docs/corpus/standards/decision-references.md` |
| Creating, updating and retiring any corpus node, including one built from this template | `launchpad/docs/corpus/AGENTS.md` |

**Expected but not verified when this node was written:**

- **No real `test-contract` node has been built from this template yet.** Whether the
  required-sections list actually holds up for an obligation simpler or more complex
  than the multi-tenant-conformance and trace-schema examples used to ground it is
  untested. The first node built from this template is the real test of it.
- **Whether every existing conformance obligation in `docs/multi-tenant-conformance.md`
  should eventually become its own `test-contract` node, versus staying inside that one
  migration-checklist document, was not decided here.** This template documents the
  shape such a node would take if and when one is written; it does not itself propose
  migrating that document's content into the corpus.
- **`crates/buzz-conformance`'s property tests (`tests/proptest_checker.rs`) and
  fixture-replay tests (`tests/replay_fixtures.rs`) were read for structure and cited
  for TRACE_SCHEMA.md's own self-description, but were not executed as part of authoring
  this template.** Whether they currently pass is not asserted by any claim above; only
  the documents' own words are cited as FACT.
- **Pact's Pact Broker workflow and its newer bi-directional contract testing mode
  (for cases without a consumer-side mock) were not researched in depth**, because the
  consumer/provider mismatch identified above already rules Pact out as this template's
  primary adapted model before those details would matter. If Buzz ever grows a
  genuinely separate, independently-deployed provider/consumer boundary — for instance,
  a third-party integration consuming a stable Buzz API independently of this
  repository's own release cadence — that mismatch should be re-examined rather than
  assumed permanent.

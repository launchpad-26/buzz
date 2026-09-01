---
id: corpus-template-invariant
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
  - statement: "node.schema.json's type enum has thirteen members -- architecture, layers, capabilities, platforms, implementation, interfaces-events, verification, operations, development, release, governance, agent, ingestion -- and none of them is template, policy, or invariant; the enum names the corpus surface a node documents, not the prose form its body takes."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Of the corpus's four nodes merged to origin/launchpad at the recorded revision, AGENTS.md carries type: agent while README.md, standards/confidence.md and standards/decision-references.md all carry type: governance -- the precedent for a node documenting the corpus's own authoring rules rather than a piece of architecture/capability/etc. content."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/docs/corpus/README.md"
      - "launchpad/docs/corpus/standards/confidence.md"
      - "launchpad/docs/corpus/standards/decision-references.md"
  - statement: "relationships.schema.json defines five relationship types -- depends-on, supersedes, implements, references, part-of -- and states implements' directionality as 'source is the concrete realization of target (e.g. a template instance of a standard)' and references' directionality as 'source cites target as supporting context; no ownership or currency dependency implied'."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/relationships.schema.json"
  - statement: "At repository revision a44cf52fc740ebebbdd671427480d14f0bce0115, the corpus tree on origin/launchpad contains exactly four validated nodes -- AGENTS.md, README.md, standards/confidence.md and standards/decision-references.md -- plus the schema/ subtree, which validate.py excludes from checking; none of this batch's siblings (#1329, #1333, #1334, #1348) nor the already-open template/standard PRs #1541 (interface) or #1518 (normative-language) are merged, so none of them are valid relationship targets."
    entry_class: FACT
    evidence:
      - "git_ls_tree(ref='origin/launchpad', path='launchpad/docs/corpus') -> AGENTS.md, README.md, schema/COMPATIBILITY.md, schema/README.md, schema/fixtures/**, schema/node.schema.json, schema/relationships.schema.json, schema/requirements.txt, schema/tests/test_schema.py, standards/confidence.md, standards/decision-references.md, at commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Parent Feature #605's acceptance criteria require that 'every template states its purpose, required sections, evidence expectations and the industry model/standard it adapts', and this is the acceptance bar this node is built against rather than issue #1343's own copied-over standards-track Definition of Done."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#605"
  - statement: "Issue #1343's own Definition of Done is byte-identical to the standards-track boilerplate ('States scope and authority/source of the policy. Separates MUST requirements from SHOULD guidance. Defines enforcement/checks and exception/escalation process. Links decisions or higher-order policy instead of duplicating them.'), the same text independently found copied across #1326-#1351 by prior batches in this same task set."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1343 definition of done"
  - statement: "This repository's root AGENTS.md states, under 'Thread counters': 'reply_count and descendant_count are materialized on thread root events. Any code that inserts replies must update these counters -- check existing reply handlers for the pattern.'"
    entry_class: FACT
    evidence:
      - "AGENTS.md:182"
  - statement: "buzz-db's thread.rs implements that gotcha as two functions, increment_reply_count and decrement_reply_count, each of which always bumps or decrements both the parent's reply_count and the root's descendant_count in one call (decrement floored at zero via GREATEST(count - 1, 0)); nothing in the type system stops a future call site for inserting or deleting a reply from skipping these functions -- the invariant holds only if every such call site actually calls them."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/thread.rs:250-287"
      - "crates/buzz-db/src/store/thread.rs:289-327"
  - statement: "buzz-core's tenant.rs states, in its module doc under '## The fence': 'The whole multi-tenant safety story rests on one invariant from the formal model (conformance \"row zero\"): a request's community is resolved from the connection host by the server, never supplied or influenced by the client', and explicitly calls this 'a lint-and-review fence, not a compiler fence' because TenantContext::resolved and CommunityId::from_uuid are public and a determined caller elsewhere could call them; the type system removes only the accidental path (deserializing a client-chosen community), and a migration-lint harness plus review closes the deliberate one."
    entry_class: FACT
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-25"
  - statement: "buzz-audit's hash.rs carries a test, storage_precision_timestamps_survive_a_database_round_trip, whose comment names 'the invariant the write path must hold: hash what will be stored, so recomputing from the row reproduces the digest', and asserts it with assert_eq!(compute_hash(&written), compute_hash(&read_back)) after simulating the storage round-trip -- an invariant with a test that would fail if it were violated, not merely a comment asserting it."
    entry_class: FACT
    evidence:
      - "crates/buzz-audit/src/hash.rs:201-214"
  - statement: "buzz-relay's state.rs documents run_registered_community_connection with: 'The ordering is the archival admission invariant: archive-before-query is observed by the query, while archive-after-registration sees the token' -- an ordering guarantee between two operations, not a state property of one value."
    entry_class: FACT
    evidence:
      - "crates/buzz-relay/src/state.rs:185-188"
  - statement: "buzz-db's push.rs documents disable_endpoint_generation with: 'Strict generation monotonicity is the underlying safety invariant. The current-generation predicate makes stale responses clean no-ops' -- enforced by a WHERE-clause predicate comparing the caller's generation against the stored one, not by a type or a test visible at this citation."
    entry_class: FACT
    evidence:
      - "crates/buzz-db/src/store/push.rs:1195-1198"
  - statement: "buzz-acp's pool.rs documents send_prompt_result with: 'Clearing steer_rx here -- rather than per-arm -- makes the install_steer_rx invariant (steer_rx.is_none() at dispatch) structurally unviolatable: a receiver installed for a turn that ends before the read loop's take() ... is always dropped before the agent re-enters the pool, so the next dispatch can never trigger the assert' -- an invariant enforced by concentrating the clearing logic in one shared return path rather than by the type system, backed by a runtime assert as a second line of defense."
    entry_class: FACT
    evidence:
      - "crates/buzz-acp/src/pool.rs:1434-1446"
  - statement: "Bertrand Meyer's own page, hosted at ETH Zurich, states that Design by Contract's basic constructs are 'Routine precondition', 'Routine postcondition' and 'Class invariant', tightly integrated with the Eiffel language, and that under inheritance a precondition can only be weakened (require else) while a postcondition can only be strengthened (ensure then)."
    entry_class: FACT
    evidence:
      - "https://se.inf.ethz.ch/~meyer/publications/online/eiffel/basic.html"
  - statement: "Eiffel Software's own definitional page states: 'Design by Contract(TM) is a method for building software in which the expected behavior of every component is explicitly defined, checked, and enforced', and defines a precondition as 'what must be true before a component is used', a postcondition as 'what the component guarantees after execution', and an invariant as 'conditions that must always remain true for the system to be valid'."
    entry_class: FACT
    evidence:
      - "https://www.eiffel.com/values/design-by-contract/"
  - statement: "Neither of the two web sources above is a citation this repository's checker can open or pin -- both are external, non-GitHub URLs, so a citation to either resolves UNVERIFIED under validate.py, per AGENTS.md's own citation-shape table. They were nonetheless fetched and read directly this session, not copied from memory or a secondary summary."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "Grepping the unmerged research note launchpad/Research/project-documentation-templates.md (branch docs/research-project-doc-templates, PR #1466) for 'invariant', 'design by contract', 'precondition', 'postcondition', 'eiffel' and 'bertrand meyer' returns zero matches, confirming it does not cover this template's subject at all."
    entry_class: FACT
    evidence:
      - "grep_repo(pattern='invariant|design by contract|precondition|postcondition|eiffel|bertrand meyer', ref='origin/docs/research-project-doc-templates', path='launchpad/Research/project-documentation-templates.md', case_insensitive=true) -> zero matches, verified 2026-08-27 against commit a44cf52fc740ebebbdd671427480d14f0bce0115"
  - statement: "Issue #1320 (PR #1518, unmerged branch task/1320-corpus-standard-normative-language, not present in this worktree's filesystem) proposes launchpad/docs/corpus/standards/normative-language.md, which states it 'governs how MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are spelled, capitalized and used to phrase a requirement inside a hand-authored corpus node ... or decision record' -- a rule about the wording of corpus prose itself, not a claim about Buzz's own runtime behavior."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1320, PR #1518 (unmerged branch task/1320-corpus-standard-normative-language)"
  - statement: "Issue #1344 exists, titled 'task: define the policy corpus template', targeting launchpad/docs/corpus/templates/policy.md as its own Objective; it is not in this batch and templates/policy.md does not exist yet anywhere in this repository."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#1344"
  - statement: "Reasoning from Meyer's and Eiffel Software's definitions above (an invariant as a state property true of every instance/for the system to be valid) against the ordinary meaning of 'policy' (a rule governing what participants do), an invariant node and a policy node make categorically different claims: an invariant is falsifiable by inspecting the system's state or behavior directly, while a policy is falsifiable only by inspecting whether participants complied with it. tenant.rs's fence is the sharpest test case available in this repository: it reads almost like a policy ('never accept a client-supplied community') but AGENTS.md's actual text states it as a property of which CommunityId values can come to exist, not as an instruction to a developer -- which is why it is evidence for this node's boundary rather than for a policy template."
    entry_class: INFERENCE
    evidence:
      - "crates/buzz-core/src/tenant.rs:1-25"
      - "https://www.eiffel.com/values/design-by-contract/"
    confidence: 0.6
---

# Template: invariant

How to write a corpus node documenting one **invariant** -- a condition about this
system's state or behavior that always holds (or is claimed to), independent of
whether any corpus document ever states it. This template adapts vocabulary from
Bertrand Meyer's Design by Contract rather than adopting its full mechanism;
*Industry model adapted* below explains what is kept and what is reshaped. This is
a template node, not a policy node -- it prescribes the shape of a future
document's *body*, not a MUST/SHOULD rule about corpus-wide behavior. See *Note on
Definition of Done* for why that distinction matters for this specific node.

## Scope and authority

**This node covers** what a corpus node's body must contain when it documents one
system invariant: the required sections, the evidence expectations for an
enforcement claim, and the industry model this template adapts (and what changes in
the adaptation).

**It does not cover:**
- The front-matter contract itself (`node.schema.json` governs that, unconditionally,
  for every node type) or how to create/update/retire a node procedurally
  (`AGENTS.md` governs that).
- How MUST/SHOULD/MAY keywords are spelled and used inside corpus prose --
  `#1320`'s normative-language standard (PR #1518, unmerged) governs that, and it
  is a rule about document wording, not a system property. See *Boundary* below.
- What a participant (developer, agent, reviewer) must or must not do -- a
  **policy** node's territory, owned by `corpus-template-policy` (#1344). See
  *Boundary* below.
- A full interface contract's versioning/compatibility/error-semantics guarantees
  -- `#1342`'s template (interface), which may `references` an invariant node this
  template produces rather than restate it.

**Its authority is derived, not original.** The structural half is already law:
`node.schema.json` enforces front matter, `validate.py` runs that schema, and CI
runs `validate.py` on every corpus change. What this node adds is the half no
schema can hold -- which sections an invariant-shaped node needs, what evidence
backs an enforcement claim, and which industry model was adapted and how. That
half is enforced by review, the same way the existing corpus standards describe
their own review-enforced half.

| For | Read |
|---|---|
| The front-matter contract itself | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of those fields | `launchpad/docs/corpus/schema/README.md` |
| Relationship types and their directionality | `launchpad/docs/corpus/schema/relationships.schema.json` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |
| MUST/SHOULD/MAY wording inside corpus prose | `#1320`'s standard (PR #1518, unmerged) |
| What a participant must do | `corpus-template-policy` (#1344) |
| An interface's operations and stability contract | `#1342`'s template (interface, PR #1541) |

If this node and any of those disagree, **they win** -- this one has drifted and
should be fixed.

## Industry model adapted: Design by Contract

**What this template borrows.** Bertrand Meyer's Design by Contract names a class
invariant as one of three basic constructs, alongside a routine's precondition and
postcondition. Eiffel Software's own definitional page states an invariant as
"conditions that must always remain true for the system to be valid" -- exactly the
shape this template's *Invariant statement* required section asks an author to
write down: a condition, not a goal, not an instruction.

**What does not transfer, and why this template reshapes it rather than adopting
it whole.**

1. **Meyer's invariant is scoped to one class.** Every instance of that class
   satisfies it, checked automatically by the Eiffel runtime on entry and exit of
   every exported routine. This repository has no such language feature: nothing
   in Rust, SQL or this codebase's own tooling automatically checks an arbitrary
   invariant on every call boundary. The invariants actually documented in this
   codebase's own comments (see the evidence ledger above) are each held by a
   *different* mechanism -- a type that cannot be constructed the wrong way
   (`tenant.rs`), a function whose structure makes violation unreachable
   (`pool.rs`), a unit test that would fail (`hash.rs`), a `WHERE`-clause
   predicate (`push.rs`), an ordering convention between two call sites
   (`state.rs`), or nothing but the discipline of every caller remembering to call
   the right function (`thread.rs`). **This template's *Enforcement today* required
   section exists because Buzz has no uniform contract mechanism** -- an author
   must say which of these tiers actually holds the invariant, rather than
   implying Eiffel-style automatic enforcement that does not exist here.
2. **Meyer's invariant may be temporarily false mid-routine, restored before the
   object is next visible to another object.** That "temporarily broken, always
   restored before external visibility" shape recurs directly in this repository:
   `thread.rs`'s two-statement update (parent's `reply_count`, then root's
   `descendant_count`) is momentarily inconsistent between the two `UPDATE`
   statements, and `pool.rs`'s `send_prompt_result` is written specifically so
   `steer_rx` is cleared before the agent "re-enters the pool" -- i.e. before it is
   next visible to another dispatch. This template keeps that shape as part of
   *Scope*, below: an author states not just the invariant but the boundary across
   which it must hold (every externally-visible state, not necessarily every
   intermediate instruction).
3. **Precondition and postcondition are not adopted as separate required
   sections.** They describe one routine's calling contract; this template's
   sibling `#1342` (interface) already owns operation-level contracts. An
   invariant node may be the shared premise several interfaces or operations rely
   on (`tenant.rs`'s fence underpins every scoped query across `buzz-db`,
   `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit` and `buzz-media`) rather
   than belonging to one routine's contract, so this template asks for *Scope*
   (which states/types/operations it binds) instead of a precondition/postcondition
   pair.

## A note on `type`

Unlike `#1342`'s `interfaces-events` value, no single enum member names "documents
one invariant" the way that combined value names interface-and-event documentation.
An invariant is a property that can belong to *any* corpus surface depending on
which layer of the system it concerns: a security boundary invariant like
`tenant.rs`'s fence is architecture- or verification-shaped; a data-consistency
invariant like the thread-counter one is implementation-shaped. **A node built from
this template therefore chooses `type` by the subject matter the invariant
concerns**, using `node.schema.json`'s existing thirteen-member enum, not by a
single fixed value the way an interface-shaped node does. This template node
itself carries `type: governance` because it documents the corpus's own authoring
rules, per the precedent in the evidence ledger above, not because invariant nodes
in general use `governance`.

## Boundary: what this template is not

Read this section before drafting.

- **Not `#1320`'s normative-language standard (PR #1518, unmerged).** That
  document governs how the words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY are
  spelled and used *inside corpus prose* -- a rule about how a corpus document is
  *written*. This template's subject is a property of *Buzz itself*, true or false
  in production regardless of whether any corpus document ever mentions it. **The
  test**: could the claim be true or false even if the corpus did not exist? Yes
  -- system invariant, this template. No, because the claim is only meaningful as
  a rule about how a document is phrased -- `#1320`'s territory. A node built from
  this template may itself use MUST/SHOULD language when stating enforcement
  expectations (as this template does, below) without becoming a normative-language
  document itself; using those words is not the same as governing their usage
  corpus-wide.
- **Not `corpus-template-policy`'s territory (#1344).** A policy
  states what a participant -- developer, agent, reviewer -- must or must not do.
  An invariant states what always holds, independent of anyone's compliance. The
  sharpest case in this repository's own evidence is `tenant.rs`'s fence: it reads
  almost like an instruction ("never accept a client-supplied community"), but
  `tenant.rs`'s own words state it as a property of which `CommunityId` values can
  come to exist, not as a rule addressed to a developer. **The test**: is the
  claim falsified by inspecting the system's state or behavior directly (an
  invariant), or only by inspecting whether someone complied with a rule (a
  policy)? A node that finds itself listing who must do what, rather than what is
  true, has picked the wrong template.
- **Not `#1342`'s interface template (PR #1541).** An interface node's *Contract
  and stability* section states what a caller may rely on for one boundary. An
  invariant node may underpin several such contracts at once (see *Industry model
  adapted* point 3) and is the deeper claim an interface's contract can point at
  via `references`, rather than a contract itself.
- **Not `#1349`'s test-contract template.** A test-contract node's whole content
  *is* one obligation paired with a named verifying test and a runnable command to
  run it, fixed at `type: verification`. An invariant node states a property that
  always holds, across whichever of five enforcement tiers actually holds it
  (type-system-enforced, structurally enforced, test-enforced, predicate-enforced,
  or convention-and-review only) — only one of those tiers is test-enforced, and
  `type` is picked by the subject matter the invariant concerns rather than fixed
  to `verification`. **The test**: is the node's job to name and run one specific
  test (test-contract), or to state a property true of the system and say which
  tier — possibly, but not necessarily, a test — actually holds it (invariant)?
- **Not the front-matter contract or corpus procedure.** Those are
  `node.schema.json` and `AGENTS.md`'s territory, unconditionally, for every node
  type including this one's own instances.

A node built from this template that drifts into any of these neighbors has picked
the wrong template, not merely written prose that needs tightening.

## Required sections

A corpus node using this template must carry the following in its body, in
addition to whatever schema-required front matter `node.schema.json` demands of
every node:

1. **Invariant statement.** One or two sentences stating the condition as a
   condition -- "X always equals Y", "Z can never be observed in state W" -- not
   as a goal ("X should stay consistent") and not as an instruction to a person.
   If the sentence cannot be falsified by inspecting the system directly, it has
   drifted into *Boundary*'s policy territory.
2. **Scope.** Which states, types, operations or call paths the invariant binds
   -- every row in a table, every instance of a type after construction, every
   externally-visible moment (per *Industry model adapted* point 2, an invariant
   may be momentarily false between two statements of one operation without being
   violated).
3. **Enforcement today.** Name which tier actually holds the invariant, honestly,
   citing the code: type-system-enforced (construction is impossible any other
   way), structurally enforced (the code's shape makes violation unreachable, but
   nothing stops a rewrite from reintroducing it), test-enforced (a test would
   fail), predicate-enforced (a query-level guard, e.g. a `WHERE` clause), or
   convention-and-review only (no compiler, type or test backstop -- every caller
   must simply remember). The evidence ledger above cites one worked example of
   each tier in this repository. **Naming the weakest true tier is the point of
   this section** -- a node that rounds "convention-and-review only" up to
   "enforced" misrepresents exactly the risk this section exists to surface.
4. **Consequence of violation.** What actually breaks if the invariant fails --
   grounded in what the code, a test, or a comment says (a security boundary
   crossed, data corruption, an assertion firing, a customer-visible count going
   wrong), not in what the author assumes would be bad.
5. **Boundary statement.** An explicit paragraph naming what this node does not
   cover, using the exclusions in *Boundary: what this template is not* above as
   the checklist, plus any node-specific exclusion the author found.
6. **Relationships**, per the guidance below.
7. **Scope and omissions**, per `AGENTS.md`'s own required step 8: what the node
   does not cover, who owns it, and separately, what was expected but could not be
   verified when the node was written.

### Template skeleton

Copy this structure; the bracketed placeholders are not literal content.

````markdown
# [Invariant name]: invariant

[One or two sentences: the condition, stated as a condition that always holds --
not a goal, not an instruction to a person.]

## Scope

[Which states/types/operations/call paths this binds, and whether it must hold at
every instant or only at every externally-visible moment.]

## Enforcement today

[Name the weakest true tier: type-system-enforced / structurally enforced /
test-enforced / predicate-enforced / convention-and-review only. Cite the code
that actually holds it.]

## Consequence of violation

[What breaks, grounded in code, a test, or a comment -- not assumed.]

## Boundary

This node does not describe:
- [a rule about corpus document wording -- see corpus-standard-normative-language,
  if the claim drifted there]
- [a rule about what a participant must do -- see the policy node for <subject>,
  if one exists]
- [an interface's full operation/versioning contract -- see the interface node
  for <subject>, if one exists]
- [any node-specific exclusion]

## Relationships

- depends-on: <another invariant node(s) this one's own claim requires, if any>
- implements: corpus-template-invariant  <!-- optional; see Relationships below -->
<!-- Do not declare `references` toward an interface node this invariant underpins --
     the interface node declares that edge, pointing at this one. See Relationships
     below for why the direction runs that way. -->

## Scope and omissions

**This node covers** ...

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| ... | ... |

**Expected but not verified when this node was written:**
- ...
````

## Evidence expectations

The corpus-wide evidence rules in `AGENTS.md` apply unchanged: `FACT` means the
author opened the cited source, `INFERENCE` means the author reasoned to the claim
and rated the reasoning, `TEAM_KNOWLEDGE` means an uncorroborated statement
attributed to whoever said it. Nothing about this template relaxes or narrows
that. Three expectations follow specifically from the industry model adapted
above:

- **An *Enforcement today* claim is a `FACT` only if the cited source actually
  enforces the invariant, not merely mentions it.** A code comment saying
  "invariant: X" is evidence that the invariant is *intended* -- it is not, by
  itself, evidence that anything *enforces* X. `hash.rs`'s worked example in the
  evidence ledger above is the strong case: the comment names the invariant and a
  test asserts it. `thread.rs`'s is the honest weak case: the comment states the
  rule, and no type or test stops a new call site from skipping it -- the node
  must say "convention-and-review only," not round it up.
- **Do not imply this repository has Design by Contract's automatic checking.**
  Citing Meyer's or Eiffel Software's vocabulary to describe an invariant's
  *shape* is this template's own move (see *Industry model adapted*); citing it as
  though Buzz enforces every invariant the way Eiffel's runtime enforces a class
  invariant would misrepresent the codebase. Say which of the tiers in *Required
  sections* item 3 actually applies.
- **A *Consequence of violation* claim needs the actual failure, not an assumed
  one.** Cite a test that would fail, an assertion in the code, or a comment
  naming the concrete harm -- not what "would probably" go wrong absent a
  citation.

## Relationships

A node built from this template:

- **is typically the *target*, not the source, of a `references` edge from an
  interface node** (`#1342`'s template) whose *Contract and stability* section
  relies on this invariant -- per `relationships.schema.json`'s stated
  directionality for `references`, "source cites target as supporting context;
  no ownership or currency dependency implied," and per *Boundary* above, an
  invariant is "the deeper claim an interface's contract can point at." The
  interface node declares the edge, not this one: the loose coupling that
  direction gives is that the invariant's own claim stays accurate even if an
  interface built on it is later revised, which would not hold if the coupling
  ran the other way. A node built from this template does not need to declare
  anything itself for this edge to exist -- it is a legitimate `referenced-by`
  target once an interface node cites it.
- **may** declare `depends-on` toward another invariant node this one's own
  claim requires to be true or current, per that type's directionality: "source
  requires target to be true/current for source's own claims to hold."
- **may** declare `implements` toward this template node itself (target:
  `corpus-template-invariant`), once this node is merged, if the author wants the
  generated `implemented-by` edge -- optional either way, since a node's own
  shape (Invariant statement / Scope / Enforcement today) already shows which
  template it followed. **This is a corpus-graph relationship, not a claim about
  code.** A statement like "tenant.rs enforces the fence invariant" belongs in the
  node's own evidence ledger as a cited `FACT`, never as a `relationships` edge --
  that field's target must be another corpus node's `id`, and no corpus node for
  `tenant.rs` itself exists or is proposed.
- **must**, per `AGENTS.md`'s own rule, resolve every declared target against
  `origin/launchpad` (or whatever the merge-target branch is at the time), never
  against the author's own worktree.

**This node's own relationships.** Declared: none. Checked: the four nodes
present in `origin/launchpad`'s corpus tree at the recorded revision --
`corpus-agents`, `corpus-readme`, `corpus-standard-confidence`,
`corpus-standard-decision-references` -- are all procedural/meta-documents about
the corpus itself, not invariant-shaped subject matter this template about
invariant documentation would `references`, `depends-on`, or `implements`. None
of this batch's four sibling templates (`#1329`, `#1333`, `#1334`, `#1348`), nor
the already-open `#1342` (interface, PR #1541) or `#1320` (normative-language, PR
#1518), target this node or are targeted by it, deliberately: none of them are
merged to `origin/launchpad`, and a `relationships[].target` naming an id no node
on the merge-target branch carries is a hard validation error there even if it
resolves in a local worktree. The first invariant-shaped instance node is the
natural moment to add a `references` or `implements` edge back to this template,
once it exists.

## Note on Definition of Done

Issue `#1343`'s own Definition of Done carries the same four bullets found copied
across `#1326`-`#1351` -- "states scope and authority/source of the policy,"
"separates MUST requirements from SHOULD guidance," "defines enforcement/checks
and exception/escalation process," "links decisions or higher-order policy
instead of duplicating them" -- verbatim from the standards-track issues that
produced `standards/confidence.md` and `standards/decision-references.md`. Those
describe a **policy/standard** node (a MUST/SHOULD normative document over
existing corpus behavior); this node is a **template** (a prescription for the
shape of a future document's body, describing a *system* property, not a corpus
authoring rule). The real acceptance criterion, from parent Feature `#605`
itself, is: *"every template states its purpose, required sections, evidence
expectations and the industry model/standard it adapts."* This node is built
against that sentence -- *Required sections*, *Evidence expectations* and
*Industry model adapted* above answer it directly -- rather than against the
standards-track checklist, which does not fit a document with no MUST/SHOULD
normative claims about existing system behavior to separate. (This template does
use MUST language in *Required sections* and *Evidence expectations* to state
what an author must do to use the template correctly -- that is ordinary
technical writing, not this node claiming to be `#1320`'s normative-language
standard; see *Boundary*, above.)

## Scope and omissions

**This node covers** what a corpus node's body must contain when it documents one
system invariant: the required sections, the evidence expectations for an
enforcement or consequence claim, the industry model adapted (Design by Contract's
invariant/precondition/postcondition vocabulary) and what changes in the
adaptation, the note that `type` tracks subject matter rather than a fixed value,
the explicit boundary against the normative-language standard and the
not-yet-existing policy and interface templates, and the relationship types a node
built from this template should use.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| MUST/SHOULD/MAY wording inside corpus prose | `#1320` (normative-language standard, PR #1518, unmerged) |
| What a participant must or must not do | `corpus-template-policy` (#1344) |
| An interface's operations and versioning/compatibility contract | `#1342` (interface template, PR #1541) |
| A single Nostr event kind's own wire contract | `#1337` (event-kind template) |
| The front-matter contract itself | `node.schema.json` |
| Creating, updating and retiring a node procedurally | `AGENTS.md` |

**Expected but not verified when this node was written:**
- **No corpus node instance has yet been drafted from this template.** Every
  required section and the skeleton above is validated only against this
  repository's own code comments naming invariants (`tenant.rs`, `thread.rs`,
  `hash.rs`, `state.rs`, `push.rs`, `pool.rs`) and against Design by Contract's
  own vocabulary, not against a real instance node passing `validate.py` end to
  end. The first invariant node drafted from this template may surface a required
  section that does not fit every invariant shape cleanly -- in particular,
  whether an invariant spanning many crates (like `tenant.rs`'s fence, which
  affects `buzz-db`, `buzz-auth`, `buzz-pubsub`, `buzz-search`, `buzz-audit` and
  `buzz-media`) should be one node or whether `AGENTS.md`'s "one node is one
  independently maintainable idea" rule would eventually split it per-layer is
  not settled here.
- **Bertrand Meyer's original 1992 IEEE Computer paper, "Applying Design by
  Contract," was not read as text.** This environment has no PDF-to-text tool
  (`pdftotext`/`poppler-utils` absent, no `pypdf`/`PyPDF2` importable, and
  automated web-fetch summarization of the PDF returned only a binary-content
  notice, not extracted text). The two sources actually cited above -- Meyer's
  own ETH Zurich-hosted HTML page and Eiffel Software's own definitional page --
  were fetched and read directly, and are primary in the sense of being Meyer's
  and his company's own words, but the paper most commonly cited as the origin of
  this vocabulary was not independently verified here.
- **Whether `implements` (this template's choice, matching `#1342`'s) or
  `references` is the corpus-wide convention for a node's optional self-link to
  its own template is not settled anywhere outside this node's own reasoning,**
  same open question `#1342` already noted for itself.
- **The INFERENCE distinguishing an invariant from a policy (evidence ledger,
  final entry) has not been tested against an actual policy-template instance,**
  since `#1344` has not been written. Whether every invariant/policy pair in this
  repository sorts as cleanly as `tenant.rs`'s fence did is unverified.

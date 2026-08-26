---
id: corpus-standard-confidence
type: governance
status: active
origin: launchpad
audiences:
  - agent
  - reviewer
evidence:
  - statement: "This node was authored and checked against repository revision 60d4947b7145a6ef25f185b9c25d43e43d99de3c."
    entry_class: FACT
    evidence:
      - "commit 60d4947b7145a6ef25f185b9c25d43e43d99de3c"
  - statement: "confidence is a number between 0.0 and 1.0, required for INFERENCE entries only, and forbidden on FACT and TEAM_KNOWLEDGE entries."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "Both bounds are inclusive, an integer is accepted as a number, and a boolean or a quoted string is rejected on type before the range is ever considered."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "memory.py's __post_init__ raises when confidence is missing from an INFERENCE, present on any other class, not a real number, or outside the closed interval."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/memory.py"
  - statement: "The corpus check enforces the confidence rule through node.schema.json alone; validate.py never imports memory.py, so the two are independent enforcement paths rather than one calling the other."
    entry_class: FACT
    evidence:
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/docs/corpus/schema/node.schema.json"
  - statement: "A confidence of NaN satisfies node.schema.json and passes corpus validation, while memory.py rejects the same value as outside the interval."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/memory.py"
  - statement: "Inference and team knowledge may supply context but are never treated as fact on their own, and stay attributed to their source and distinguishable from FACT claims."
    entry_class: FACT
    evidence:
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "The flagged status names two same-claim-type authoritative sources contradicting each other with no human resolution yet, and is explicitly not a generic low-confidence marker."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/decisions/ADR-0029-corpus-evidence-precedence.md"
  - statement: "Citation checking is structural: the check confirms a cited path resolves to a real file and never that the file supports the statement it sits under."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
      - "launchpad/project-intelligence/corpus/validate.py"
  - statement: "The only INFERENCE in the corpus at the recorded revision is AGENTS.md's claim that retirement is a status change rather than a deletion, carried at confidence 0.8."
    entry_class: FACT
    evidence:
      - "launchpad/docs/corpus/AGENTS.md"
  - statement: "No corpus mechanism records whether a past inference turned out to be correct, so a confidence value can only express the author's assessed strength of reasoning and never an observed frequency."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
      - "launchpad/project-intelligence/corpus/validate.py"
      - "launchpad/project-intelligence/memory.py"
    confidence: 0.7
  - statement: "Because the schema accepts any in-range value without recording how it was chosen, two entries carrying the same number need not represent comparable strength, so values are not safely comparable between authors or nodes."
    entry_class: INFERENCE
    evidence:
      - "launchpad/docs/corpus/schema/node.schema.json"
    confidence: 0.8
  - statement: "An INFERENCE whose citation supports the subject of the claim but not the choice the claim makes is a decision in disguise, and belongs in TEAM_KNOWLEDGE attributed to whoever decided it."
    entry_class: TEAM_KNOWLEDGE
    provided_by: "launchpad-26/buzz#636 cross-model final review, relayed in the #1309 task brief: a second INFERENCE on AGENTS.md was rejected as laundering an unsourced policy choice into a class that made it look derived, and was reclassified to TEAM_KNOWLEDGE attributed to the issue's definition of done"
---

# Standard: `confidence`

What the `confidence` number on an evidence entry means, when it is required, how an
author picks one, and what a reader may conclude from it.

This is a policy node. Look up the section you need.

| For | Read |
|---|---|
| The field's machine contract — type, range, which class requires or forbids it | `launchpad/docs/corpus/schema/node.schema.json` |
| Prose walkthrough of the front-matter fields | `launchpad/docs/corpus/schema/README.md` |
| The same rule enforced at runtime on the in-process store | `launchpad/project-intelligence/memory.py` |
| How to rank conflicting evidence, and when to stop and escalate | `launchpad/decisions/ADR-0029-corpus-evidence-precedence.md` |
| Creating, updating and retiring a node | `launchpad/docs/corpus/AGENTS.md` |

Those files are authoritative. Where this document and any of them disagree, **they
win** — this one has drifted and should be fixed. The field-combination rules and the
enum members are deliberately not copied here: the check never reads body prose, so a
second copy would stay green forever after it went stale.

## Scope and authority

**This standard governs** the `confidence` key on an entry in a corpus node's
`evidence` ledger — the one place the field exists.

**Its authority is derived, not original.** The structural half of this standard is
already law: `node.schema.json` enforces it, `validate.py` runs that schema, and CI runs
`validate.py`. This document does not create those rules and cannot relax them. What it
adds is the half no schema can hold — what the number is *for*, how to choose one
honestly, and what a reader is entitled to conclude. That half is enforced by review.

**On the interpretation of an INFERENCE, ADR-0029 outranks this document.** It is the
accepted decision; this is a standard written under it.

## What the number is for

An INFERENCE is a claim you reasoned to rather than read. `confidence` is **the
author's own rating of how strongly the cited evidence supports the statement** — a
declared strength of reasoning, published so a reader can weigh the claim and a reviewer
can challenge it.

That is the whole of it. In particular:

- It is **not a probability**, and not a frequency. Nothing in the corpus records
  whether a past inference turned out to be right, so no number here has ever been
  scored against an outcome. There is no calibration behind it and none is collected.
- It is **not a quality score** for the node, the author, or the citation.
- It is **not a promotion path**. A confidence of 0.99 does not make an INFERENCE into a
  FACT. Class is decided by *how you came to know the thing*, never by how sure you feel
  about it, and ADR-0029 is explicit that inference is never treated as fact on its own.
- It is **not a conflict marker**. Two authoritative sources of the same claim type
  saying different things is `status: flagged`, not a low number. See *Exceptions and
  escalation*.

**The failure this field exists to prevent.** A number between 0 and 1 with no stated
meaning is decoration. The specific way that goes wrong: an author writes `0.8` because
it feels about right, and a reader — or a generated view, or a later agent — treats it
as calibrated and reasons onward from it. The number then carries more weight than
anything that produced it. Everything below is aimed at that.

## Requirements

These are MUSTs. The first three are enforced mechanically; the rest are enforced by
review, and a reviewer who lets one through has approved a defect.

1. **Every INFERENCE entry MUST carry a `confidence`, and no FACT or TEAM_KNOWLEDGE
   entry may carry one.** This is structural and there is no exception to seek — the
   schema rejects the node either way.
2. **The value MUST be a number within the closed interval the schema defines.** Both
   bounds are inclusive. A quoted string is not a number and is rejected on type.
3. **The value MUST be finite.** The schema does not currently enforce this — see
   *Enforcement, and where it stops* — so this one is on the author and the reviewer.
4. **The reasoning the number rates MUST be visible.** The reader has to be able to see
   what was reasoned from what: in the `statement`, in the body section the entry
   supports, or in both. A number attached to reasoning nobody can inspect cannot be
   challenged, and an unchallengeable claim is the thing this corpus exists to avoid.
5. **An entry MUST NOT be an INFERENCE if its citation supports the subject of the claim
   but not the choice the claim makes.** That is a decision, not a derivation. Reclassify
   it to TEAM_KNOWLEDGE and name who decided. See *Reasoning versus deciding*.
6. **A number MUST NOT be moved because someone pushed back on it.** Re-verify the claim
   or reclassify the entry. Adjusting the number to settle an argument records agreement
   where there was none.
7. **When a claim is re-verified at a new revision, its confidence MUST be re-considered
   in the same edit.** A number that outlived the reasoning it rated is worse than no
   number, because it still looks current.

## Guidance

These are SHOULDs. Depart from them with a reason.

**Use a coarse scale.** Three bands carry everything this field can honestly express:

| Band | Means | Typical shape |
|---|---|---|
| High | The cited sources constrain the conclusion; a competent reader would reach the same one. | Two independent sources agree, and the step from them to the claim is short. |
| Medium | The reasoning is sound but rests on a step the sources do not fully close. | One source, plus a general principle. Or an absence-of-evidence argument over a scope you actually checked. |
| Low | You believe it, and you can see how it could be wrong. | A single weak source, or a long inferential chain. |

**Two decimal places are not warranted.** The scale has no calibration behind it, so
`0.83` claims a precision that nothing supports. Pick one number per band and reuse it.

**Prefer removing the inference to rating it.** If a source would settle the claim, open
the source and make it a FACT. High confidence is not a substitute for five minutes of
reading, and it is the cheaper-looking of the two only until someone relies on it.

**Split compound claims rather than averaging.** If one half is solid and the other is a
guess, a middling number describes neither. Two entries, two numbers.

**Do not publish a claim you would rate very low.** At that point the honest artefact is
not a weak INFERENCE but a named gap in the node's scope-and-omissions section — "this
was expected and could not be verified." A gap tells a reader to go and find out; a
low-confidence claim invites them to use it anyway.

**Keep the number stable.** It moves when the reasoning or the evidence moves, and at no
other time.

## Reasoning versus deciding

**This is the distinction most worth getting right, and the one nothing will catch for
you.**

Two entries can look identical in front matter — an `INFERENCE`, some citations, a
number — while being completely different objects:

- **Reasoning from evidence.** The sources constrain the conclusion. Someone else,
  handed only those sources, could get there.
- **Dressing up a decision.** Someone chose something. A citation was then attached that
  is *about the same subject* but does not compel the choice. The class makes it look
  derived. It was not derived; it was decided.

The second is the more dangerous artefact, because `INFERENCE` implies the claim came
from the evidence, and a reader who trusts that will not go looking for the person who
actually made the call. The choice becomes unattributable — and an unattributable
decision cannot be revisited, because nobody can be asked why.

**The test.** Read the statement and the citations, and nothing else. *Could a competent
reader, without knowing what the team wanted, arrive at this statement from these
sources?*

- Yes → INFERENCE. Rate it.
- No, because the statement contains a choice the sources leave open → TEAM_KNOWLEDGE,
  with `provided_by` naming the person, issue or decision that made it.

**The tell** is a citation that supports the *topic* of the claim while saying nothing
about the *specific* thing being asserted. Read your own citation as an adversary would:
does it say this, or does it merely concern this?

**Worked example — a legitimate INFERENCE.** `AGENTS.md` claims that retiring a node is
a status change rather than a deletion, at confidence 0.8, citing the checker and
ADR-0028. Both citations do real work: the checker's behaviour establishes that deleting
a node breaks every relationship targeting it, and ADR-0028's requirement that generated
projections derive reproducibly from a stable id establishes that the id cannot be
released. The conclusion follows from the two together. Neither source says "retirement
is a status change" — that step is the author's, which is exactly why it is an INFERENCE
and not a FACT, and why 0.8 rather than higher.

**Worked example — the move to avoid.** That same node originally carried a second
INFERENCE, which a cross-model review rejected: it stated a policy choice and cited a
file that did not discuss the policy. It was reclassified to TEAM_KNOWLEDGE and
attributed to the issue's definition of done, which is where the choice had actually come
from. Nothing about the front matter had been invalid. The schema was satisfied, the
citation resolved, the check passed. Only a reader comparing the statement against the
source caught it.

**This is the load-bearing point of the whole standard.** No number, however carefully
chosen, repairs a misclassified entry — a decision at confidence 0.4 is still a decision
wearing the wrong clothes. Get the class right first; the number is the smaller question.

## What a reader may conclude

**You may** read it as the author's rating of how strongly the cited evidence supports
the statement, and use it to decide what to check first.

**You may not:**

- Treat it as a probability that the claim is true.
- **Compare it across entries, nodes or authors.** The schema accepts any in-range value
  and records nothing about how it was chosen, so one author's high band and another's
  need not mean the same thing. Two entries at the same number are not thereby equally
  strong.
- Aggregate, average or multiply values. They are not measurements and the arithmetic
  means nothing.
- Read a high value as "nearly a FACT". The class is the load-bearing signal; the number
  ranks entries within a class, and even that only against the same author's other work.
- Rely on it having been reviewed. A number that no reviewer questioned is a number
  nobody objected to, which is not the same as a number anyone confirmed.

**What a passing validation tells you about a confidence value:** that it is present
where required, absent where forbidden, and numerically in range. Nothing else. Checking
is structural — a citation is confirmed to resolve to a real file, never to support the
statement it sits under.

## Enforcement, and where it stops

**Enforced mechanically**, by `node.schema.json` through `validate.py`, and in CI on
every change under the corpus root: presence on INFERENCE, absence on the other two
classes, numeric type, and the closed range. A node violating any of these does not
merge.

**Enforced separately at runtime**, by `memory.py`'s `__post_init__`, for the in-process
store. These are two independent paths to the same rule, not one calling the other —
`validate.py` does not import `memory.py`. Both must be satisfied by anything that
travels between them, and where they differ the stricter one is the safe assumption.

**Not enforced by anything:**

| Gap | Consequence |
|---|---|
| Whether the number is justified, or was reasoned at all | An arbitrary value passes cleanly. This standard's judgement rules are review-enforced only. |
| Whether the citation supports the claim | Checking is structural. A FACT or an INFERENCE citing a real file that says nothing on the subject passes. |
| Whether an INFERENCE is really a decision | The move described in *Reasoning versus deciding* is invisible to every check that exists. |
| **A non-finite value** | `confidence: .nan` satisfies the schema and passes corpus validation, while `memory.py` rejects the identical value as out of range. The schema's own description points at `memory.py` as the enforced rule, so this is a real divergence between the two paths and not a deliberate relaxation. Requirement 3 exists to cover it. |

The pattern across that table: everything a schema can hold is held, and everything that
requires reading is not. Reviewing a confidence value means reading the sources. There
is no cheaper check, and a green run is not one.

## Exceptions and escalation

**There is no exception process for the structural requirements.** They are enforced
before merge and cannot be waived by agreement. Changing them means changing
`node.schema.json` under `launchpad/docs/corpus/schema/COMPATIBILITY.md`, which is a
schema change, not an exception.

**When you cannot pick a number honestly**, that is a signal about the entry, not a
reason to guess. In order:

1. **Can a source settle it?** Open it. The entry becomes a FACT and the question goes
   away.
2. **Is it two claims?** Split it, and rate each.
3. **Is it actually a decision?** Reclassify to TEAM_KNOWLEDGE and attribute it.
4. **Is it none of those, and still not something you would stand behind?** Do not
   publish it as a claim. Record it as a gap in the node's scope-and-omissions section.

**When two authoritative sources of the same claim type contradict each other**, do not
express the disagreement as a middling confidence. That hides a conflict inside a number
and produces a node that looks merely tentative when it is actually unresolved. Record
the contradiction, set the node's `status` to `flagged`, and leave it for a human.
ADR-0029 is the governing rule and its escalation is deliberate: a flagged node is the
accepted safer failure mode, not a defect to be tidied away.

**When a reviewer disputes a value**, the author re-verifies and then either moves the
number with a stated reason or reclassifies the entry. Requirement 6 forbids splitting
the difference. If it stays unresolved, it escalates as a conflict rather than settling
at an average nobody believes.

## Scope and omissions

**This document covers** what `confidence` means, its requirements and guidance, how to
choose a value, how to tell reasoning from a disguised decision, what a reader may
conclude, and what enforcement does and does not reach.

**It does not cover, and these are gaps rather than silence:**

| Not covered here | Owned by |
|---|---|
| The other evidence-entry fields — `entry_class`, `evidence`, `provided_by` — and the citation shapes | The evidence standard, #1314 |
| The field-combination matrix and the enum members themselves | `launchpad/docs/corpus/schema/node.schema.json` |
| Encoding ADR-0029's claim-type classification and the flagged state in the schema and checker | #1410 |
| Whether a node's classification is per-node or per-claim | Settled as per-entry by the schema; the wider question sits with #605 |
| Any numeric scale with real calibration behind it | Nothing. No such thing exists here, and this document does not invent one. |

**No `relationships` in this node's front matter.** Every sibling standard is unmerged
at the recorded revision, and a `relationships[].target` naming an id no loaded node
carries is a hard validation error — so there is nothing this node could legally point
at. `AGENTS.md` is the only other authored node and is the natural first edge. The
absence is deliberate, and the moment the sibling standards land is the moment to
revisit it.

**Expected but not verified when this node was written:**

- **The bands in *Guidance* are not derived from anything.** They are a proposed
  convention for keeping values coarse, offered because unbounded precision is the
  observed failure. No study, no sample, and only one INFERENCE existed in the corpus to
  look at. Treat them as a starting convention that practice should correct.
- **No generated view was tested consuming a `confidence` value.** No generator exists
  yet, so how a projection renders or ranks these numbers is unknown, and the
  "not comparable" rule above has not been tested against a consumer that might assume
  otherwise.
- **The NaN divergence was measured against the current schema and `memory.py` only.**
  Whether any other consumer of the field shares the schema's permissiveness or
  `memory.py`'s strictness was not established.

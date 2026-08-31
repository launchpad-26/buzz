---
name: root-cause-analysis
description: Investigate a fault to its root cause and build the evidence chain that proves it. Use for recurring faults, intermittent failures, outages and major incidents, for "why does this keep happening", for a service that broke and nobody knows why, and whenever an RCA, postmortem or problem record is asked for.
---

# Root cause analysis

The spine of the investigation. It owns the sequence and nothing else: techniques come from
`analysis-technique`, evidence preparation from `evidence-reduce`, the write-up from `rca-report`.
Invoke those as skills — do not read across into their directories, because these skills are
symlinked into several harnesses and relative paths break there.

A root cause here is one with an unbroken chain from evidence to conclusion. Every step below ends
on a criterion you can check before moving on.

## Step 1 — Establish the tempo

Ask, in these words or close to them: **is the incident live right now, or is service already
restored?** Tempo sets the depth of every step that follows, so it is established explicitly, from
the answer or from the evidence — and never from how urgent the request sounds or from the format of
write-up it asks for.

- **Live** — service is still impaired. Time-boxed. Bias toward bounding the blast radius, finding
  a workaround, and naming the next highest-yield diagnostic. Three hypotheses is enough, and
  "untested — would take 20 minutes" is an acceptable verdict.
- **Retrospective** — service is restored. Full evidence chain, the full hypothesis set, and a
  refutation attempt recorded against each one.

**Where there is nobody to ask** — a headless or one-shot run with no reachable reporter — read the
tempo off the evidence:

- Impact still ongoing where the evidence window ends, with no mitigation or restoration recorded
  → **live**.
- Restoration or mitigation visible in the evidence → **retrospective**.

**Done when** the tempo is stated in one line — from the answer, or inferred with the deciding
evidence named in that same line — and the rest of the investigation is scoped to it.

## Step 2 — Fix the symptom shape and the timeline anchors

Capture the problem in the reporter's own words, not your paraphrase — routing in step 5 matches on
that register. Then pin three facts: **when it started, who or what is affected, and who or what is
unaffected.** The unaffected half is evidence, not background.

Where onset time is uncertain, invoke `evidence-reduce` with `first-occurrence` rather than
estimating it. Onset is the highest-value single fact in an incident and it is a strict function of
the evidence.

**Done when** you can write one sentence of the form *"X fails for A but not for B, starting at T"*,
with T sourced from evidence or explicitly marked unknown.

## Step 3 — The evidence gate

Before analysing anything, ask the questions whose answers unlock the next step. A targeted question
names what it would settle — *"was the 09:40 config push applied to all three regions or one?"*
settles a hypothesis; *"can you send more detail?"* settles nothing and costs a round trip.

- **For what to ask about in the layer in play, read the matching file in `domains/`.** Run
  `ls domains/` and open the one file whose layer matches the symptom — application, network, cloud,
  identity/access, database, storage or endpoint. Each carries the first five checks ordered by
  yield, the evidence sources worth pulling, and the escalation signals that say the fault is not in
  that layer. Read a second domain file only when a signal from the first sends you there.
- **Where evidence is large or multi-file, invoke `evidence-reduce` before opening any of it.** It
  sizes the sources first and reduces what does not fit a single read, so what enters this
  investigation is a reduction with a receipt, not raw logs.

**Done when** either every open question has an answer, or the ones still open are listed with what
would answer each — and every piece of evidence in hand has been sized, with anything over a single
read reduced by a script rather than opened.

## Step 4 — Generate hypotheses, then try to refute each one

Write **three to five** candidate causes. Fewer than three and you have committed early; more than
five and none will be tested properly. Spread them across layers — where every hypothesis names the
same component, the domain file for the layer below it will suggest the missing one.

Then take each in turn and **attempt to refute it.** Ask what would have to be true in the evidence
if this hypothesis were correct, and what would have to be absent — then go looking for the absence.
A hypothesis survives only when an honest attempt to refute it fails.

Record a verdict against every hypothesis:

| Verdict | Means |
|---|---|
| **Refuted** | Evidence contradicts it. Name the evidence. |
| **Supported** | A refutation attempt was made and failed. Name what you looked for and did not find. |
| **Untested** | No attempt made. Say why — evidence unavailable, out of time box, needs a team you do not have. |

**Done when** every hypothesis carries one of those three verdicts and the evidence that decided it.
"Supported" with no refutation attempt behind it is untested; label it that way.

## Step 5 — Route the analysis out

Do not reason about which technique to use inline. **Invoke `analysis-technique`, passing the symptom
shape from step 2 in the reporter's words** and any hypothesis you need settled. It owns the routing
table and the eleven technique files; naming a technique yourself bypasses the routing that makes the
library worth having.

Where it names a technique you already know the answer for, run it anyway — the technique produces
the chain, and the chain is the deliverable.

**Done when** at least one technique has been run through `analysis-technique`, its `## Done when`
condition is met, and its output is attached to a specific hypothesis from step 4.

## Step 6 — The recurrence test

The investigation closes on two questions, and a candidate cause has to pass both:

1. **If this cause is addressed, would the problem recur?** If it could, you have found a
   contributing factor or a trigger, not the root cause — keep going, and record what you found as
   the trigger.
2. **Does the evidence explain all observed symptoms?** Any symptom left unexplained is either a
   second cause or a sign the chain is wrong. Name it either way.

**Done when** both questions are answered in writing, and the cause named survives both. Where a
symptom stays unexplained, that goes to `rca-report` as an open question rather than being dropped.

## Step 7 — Hand off to the report

**Invoke `rca-report`, telling it the tempo from step 1** — live tempo produces a problem record,
retrospective produces the postmortem. Pass it the timeline, the hypothesis table with verdicts, the
technique output, and the recurrence-test answers. It owns the format and the output handling; this
skill does not restate either.

**Done when** `rca-report` has been invoked with the tempo named, and the hypothesis table with its
verdicts has reached it intact — that table is the evidence chain, and it is the difference between
an RCA and an incident log.

## Boundary — investigate, propose, hand over

This skill runs **read-only diagnostics**: the commands in `domains/` are safe to run on a production
system mid-incident, and the reduction scripts never mutate their input.

When the investigation finds a fix, it goes into the resolution plan in the report — stated as a
specific proposed change, with the evidence that supports it, the blast radius it would touch, and
how to verify it worked. Applying it is the change owner's call, made with that plan in hand.

---
name: analysis-technique
description: Run one structured analysis technique against the evidence in hand — 5 whys, fishbone/Ishikawa, IS/IS NOT, Pareto, fault tree, bisection, timeline reconstruction, change analysis, correlation, trend analysis, dependency and blast radius. Use when one of those is named, when a symptom shape needs routing to the right one, or when root-cause-analysis asks for a technique.
---

# Analysis technique

`techniques/` holds the library; this skill picks exactly one file out of it and runs it. Load the
one technique you are going to run and no others — the whole library in context is the cost this
skill exists to avoid.

Two ways in. A technique was named, or it was not.

## Path A — a technique was named

The name arrives as `/analysis-technique <name>`, as a phrase in the request ("run a 5 whys on
this"), or from the `root-cause-analysis` spine. There need be no RCA in progress and no incident:
run it on whatever the user is looking at.

1. **Resolve the name to a file.** `ls techniques/` and match the argument against filenames,
   ignoring case, spaces and punctuation — `5 whys`, `five whys` and `five-whys` all resolve to
   `techniques/five-whys.md`. On no match, show the filename list and ask which was meant. On more
   than one match, ask; do not pick.
2. **Read that one file.**
3. **Check `evidence-required`.** Each entry is a precondition, not a wish. Where one is missing,
   say which entry it is and what would supply it, and get it before step 5 rather than running the
   technique on an assumption.
4. **Reduce first if `reduces-with` names a script** — see below.
5. **Follow `## How to run it`** in order. The steps are written to be executable without prior
   experience of the technique, so run them as written rather than from memory of the method.
6. **Check `## Don't use it for`** against what you are actually looking at. Where the case you have
   is the anti-pattern that section names, say so and return to Path B rather than producing a
   confident answer the technique cannot support.

**Done when** the file's `## Done when` condition holds and your output states how it was met — or
you have named the missing `evidence-required` entry and what would supply it.

## Path B — no technique was named

The user typed `/analysis-technique` bare, or described a problem without naming a method.

1. **Read `ROUTING.md`.** It maps symptom shape → technique and is generated from the library, so it
   is the current answer to what exists. If it is absent, run `scripts/build-routing` and use its
   output.
2. **Get the symptom shape in the reporter's own words** — how the problem was described on the
   bridge call or in the ticket, not your paraphrase of it. Ask for it if you have only a system
   name. The rows are phrased in that register, so a paraphrase routes worse than the raw sentence.
3. **Match the sentence against the rows.** Several rows may point at the same technique; that
   strengthens the match rather than duplicating it.
4. **Where two techniques match on different rows, name both**, say what each would settle, and run
   the cheaper one first — `cost` in the technique's frontmatter tells you which.
5. **Where nothing matches**, say that the shape is not in the table and ask one question that would
   discriminate between the two closest rows. Guessing here spends a whole technique on the wrong
   problem.

**Done when** one technique is named together with the routing row that selected it. Then run
Path A on it.

## Reduce before you reason

A technique's frontmatter carries `reduces-with`, naming the `evidence-reduce` script that
mechanically prepares that technique's input. Where it is anything other than `none`, **invoke the
`evidence-reduce` skill with that script name and the evidence paths, and run the technique on its
output.** Reading the raw source instead puts a day of logs through a context window to answer a
question a script answers exactly.

Invoke `evidence-reduce` as a skill. Do not reach into `../evidence-reduce/scripts/` by path — these
directories are symlinked into several harnesses and relative paths across skills break there.

Where `reduces-with` is `none`, the technique's input is judgement rather than volume, and there is
nothing to reduce.

**Done when** the technique ran on the reduction, and the reduction receipt the script printed is
carried into your output so the evidence chain names what was read and what it came from.

## Adding a technique

Write `techniques/<name>.md` against `techniques/_TEMPLATE.md`, then run
`scripts/check-techniques` and `scripts/build-routing -o`. The routing table is generated from
frontmatter, so a technique whose `reach-for-when` entries are phrased as symptom shapes routes
itself, and one phrased as a technique name never gets reached.

**Done when** `check-techniques` exits 0 and the new technique's rows appear in `ROUTING.md`.

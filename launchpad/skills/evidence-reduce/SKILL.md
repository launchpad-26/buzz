---
name: evidence-reduce
description: Reduce logs, traces, metrics and diagnostic dumps to something small enough to reason about, before reading any of it. Use when evidence arrives as a large or multi-file log, trace or metric export, when an investigation needs a timeline, an onset time, a top-signature ranking or a working-vs-broken diff, and whenever root-cause-analysis or analysis-technique needs raw evidence prepared for a technique.
---

# Evidence reduce

**Scripts narrow the haystack; agents read the needle.** Raw evidence never enters
the context window — a reduction does.

## Step 1 — Size before you open

Count every evidence file before reading any of it:

```bash
wc -l evidence/*
```

**Done when** every evidence source has a line count and none has been opened.

A source over 2,000 lines does not fit one read, so it is reduced, never read.
Under 2,000, reduce anyway when the question is a pattern, a ranking, an onset
time or a comparison — a read answers "what does line 400 say", not "what is
happening in here".

## Step 2 — Decide: script or agent

Run the three tests on the operation in front of you. It is **script** work when
all three hold:

1. **The output is a strict function of the input** — same input, same output,
   every run.
2. **Correctness is checkable without domain judgement** — you can tell it worked
   without knowing anything about the incident.
3. **It must be exact, or it materially shrinks the input.**

Any one failing makes it **agent** work: deciding what is anomalous *for this
system*, choosing between hypotheses, judging whether evidence refutes a claim,
naming a root cause.

**The corollary that pays:** when the task is agent work and the input is large,
a script runs **first**. Ranking signatures is mechanical; deciding which
signature is abnormal here is yours. Run the script, then judge its output.

**Done when** you can name, for the operation you are about to perform, which of
the three tests it passes and which script (or none) therefore runs first.

## Step 3 — Select the script

Scripts live in this skill's `scripts/` directory. Each takes file paths or
stdin, never mutates input, prints a table on stdout (`--json` for structured
output), and writes a file only with `-o`.

| Situation | Script | Output is good for |
|---|---|---|
| Evidence spans far more time than the incident | `window --from T1 --to T2` | Every later step — window first, then reduce again; multi-line records stay attached to their timestamped line |
| You need the onset time, or the first appearance of an error | `first-occurrence --pattern RE [--before N --after N]` | Fixing "when did this start", then testing a change record against it |
| One huge log, no idea what is in it | `frequency --top N` | A ranked signature table with IDs, timestamps and addresses normalised out — the input to Pareto and to "which of these is abnormal here" |
| A working case and a broken one, or before and after | `delta A B [--threshold PCT]` | Signatures only in A, only in B, and those whose share shifted — the input to change analysis and the IS / IS NOT grid |
| Several sources plus a change record, and order matters | `timeline app=a.log lb=b.log [--bucket 5m --tz UTC]` | One ordered, source-tagged, timezone-normalised table — the sequence a timeline reconstruction reads |
| Two series that may or may not move together | `correlate a.log b.log [--bucket SECONDS]` | Bucketed co-movement between the two — evidence of alignment only; which causes which stays your call |

Chain them: `window` to the incident hour, then `frequency` or `delta` on the
slice. Reducing twice is cheaper than reading once.

**Exit codes carry meaning.** `0` succeeded; `1` found nothing — for
`first-occurrence` that is itself a finding, that the pattern never occurs in
this source; `2` is bad usage, so fix the command.

**Done when** the reduction is on screen and the raw source is still unread.

## Step 4 — Report the receipt

Every script prints a reduction receipt to stderr:

```
read 1,240,331 lines -> 34 signatures (99.997% reduction)
```

Keep stderr visible — a receipt swallowed by `2>/dev/null` cannot be reported.
Quote each receipt verbatim in your findings, one line per script run, beside the
command that produced it.

**Done when** every script you ran has its receipt quoted, and the total lines
read by the scripts exceeds the lines you read yourself by at least an order of
magnitude. If it does not, a raw read happened that a script should have done —
name it and replace it.

## Handing the reduction on

The reduction is the evidence from here on. Cite it as
`frequency evidence/app.log --top 20` plus the rows you relied on, so anyone can
re-run the exact command and get the exact table. Where a technique named a
`reduces-with` script, that script's output is the input the technique expects.

---
name: rca-report
description: Write up an incident as a postmortem or an ITIL problem record, with the hypotheses that were ruled out and the evidence that ruled them out. Use when a postmortem, incident report, problem record or RCA write-up is asked for, when an investigation has closed and needs documenting, when the cause is already known and only the document is missing, and when root-cause-analysis reaches its write-up step.
---

# RCA report

The template is opened at the end of the investigation, not the start. A heading
in view before the evidence supports it gets filled in anyway.

## Step 1 — Establish the tempo

The tempo decides the format, so it is settled before a template is opened.

- **Live** — the incident is still running, service is not restored.
- **Retrospective** — service is restored and the investigation has closed.

When `root-cause-analysis` invoked this skill, the tempo is already fixed; carry
it over rather than asking again. Invoked standalone, ask which it is unless the
request states it outright ("we're still down" is live, "write the postmortem"
is retrospective).

**Done when** you have said which tempo this report is in, and why.

## Step 2 — Open the matching template

| Tempo | Template |
|---|---|
| Live | `templates/problem-record.md` |
| Retrospective | `templates/postmortem.md` |

Read the file and follow it. Its headings, order and the guidance under each one
are the specification for the document — this skill does not repeat them, so a
report written from memory of "the usual sections" will be missing fields.

**Done when** the template file is read and its headings are the headings of your
draft.

## Step 3 — Fill each heading from evidence you can cite

Every claim in the document traces to something a reader can go and look at: a
log line, a metric, a change record, a ticket note, a command and its output. A
heading with no evidence behind it gets the sentence *"Not established — <what
would establish it>"*, which is a finding about the investigation rather than a
gap in the paperwork.

Keep the trigger, the process breakdown and the root cause in their own fields as
the template separates them. Collapsing them into one paragraph is what turns a
postmortem into a narrative — the deployment is the trigger, the missing review
control is the process breakdown, the leak it let through is the root cause.

**Done when** every heading in the template is either backed by a citation or
carries an explicit "Not established" line, and none is blank.

## Step 4 — Fill Hypotheses Considered and Ruled Out

In a retrospective report this section is required. It is the evidence chain, and
a report without it is an incident log — the reader cannot tell a conclusion that
survived refutation from a first guess that happened to stick.

One row per hypothesis that was raised during the investigation, including the
ones that turned out to be wrong, each with the specific evidence that decided
it. Where a hypothesis was never formally tested, keep the row and mark it
`Untested` — an omitted row reads as a hypothesis nobody thought of.

**Done when** the table has a row for every hypothesis raised, each with a
verdict and the evidence behind that verdict, and the surviving cause in "What
caused the incident?" is one of them.

## Step 5 — Get the time metrics from `scripts/intervals`

TTD, TTM and TTR are date arithmetic across timezones and DST boundaries. Supply
the timestamps; the script returns the durations:

```bash
scripts/intervals --start <T> --detection <T> --mitigation <T> --resolution <T>
```

It accepts ISO 8601, syslog, Apache and epoch timestamps, and `--json` for
structured output. Copy what it returns into the report verbatim.

**Done when** the durations in the report are the strings the script printed, and
no duration anywhere in the document was worked out in prose.

## Step 6 — Print the report to the console

Print the finished document in full before offering to put it anywhere. The
reader corrects it here, while it is still cheap to change.

**Done when** the whole report is on screen.

## Step 7 — Ask where it goes, then send it there

Ask which of the three, and wait for the answer:

1. **Save it as a `.md` file** — `scripts/emit <report.md> --save <archive-dir>`
2. **Raise it as a repo issue** — `scripts/emit <report.md> --raise`
3. **Leave it in the console** — nothing further runs.

`scripts/emit` owns the dated path, the slug and the `gh` invocation, so pass it
the report and the destination and let it build the rest. `--dry-run` shows the
path or title it would use without writing anything; `--force` is what overwrites
an existing file, so a refusal to overwrite is a real collision worth reading.

Then report the path or URL the script printed. "Saved" without a location leaves
the reader hunting for their own report.

**Done when** the chosen destination has been carried out by the script and you
have quoted back where the report landed — or the reader chose the console and
you said so.

---
name: fishbone-ishikawa
summary: Categorised brainstorm of candidate causes across People, Process, Technology, Environment, Measurement and Supplier, to widen a search that has no leading suspect
reach-for-when:
  - we have no idea where to even start looking
  - one clear symptom and no candidate cause anyone can name
  - the incident spans multiple layers and nobody owns the whole picture
evidence-required:
  - a clear, single statement of the effect (the "fish head") that all participants agree on
  - representation from each team touching the affected system, in the room or in the thread
reduces-with: none
cost: medium
---

# Fishbone (Ishikawa)

## Reach for it when

Reach for this when the bridge call has no leading theory at all — not "which of these three
causes is it" but "we don't know what kind of cause this even is." It is the right first move
when there is one clear symptom and no candidate cause anyone can name — app, network and platform
teams each have a theory about someone else's system, but no evidence yet narrows the search to
one layer. Fishbone's job is to force a wide, structured sweep across categories before anyone
commits to a hypothesis, so that the team stops guessing inside one team's blind spot and starts
covering the whole space on purpose. Where multiple services are actually down, reach for
dependency and blast radius mapping instead — that shape has a discriminating fact (concrete
services failing together) that fishbone's diffuse "no suspect" shape does not.

## Evidence it needs

- A single, precise statement of the effect everyone is investigating — vague or compound
  statements ("things are slow and also sometimes fail") produce a fishbone that sprawls into two
  unrelated diagrams.
- One representative per category who can speak to that category's normal state (a person who
  knows the deploy calendar, a person who knows the network topology, a person who knows the
  storage layer, and so on) — this technique runs on domain knowledge in the room, not on a log
  file.
- Nothing quantitative is required to start. Fishbone precedes evidence-gathering; it decides
  where to point the evidence-gathering next.

## How to run it

1. Write the effect in a box at the head of the diagram, in one sentence, agreed by everyone on
   the call before any cause is proposed.
2. Draw six ribs off the spine, labelled People, Process, Technology, Environment, Measurement,
   Supplier — the IT adaptation of the manufacturing 6M's.
3. For each rib in turn, ask "what about this category could produce the effect?" and capture
   every answer as a twig off that rib, without judging or filtering yet. Do not stop at the first
   plausible answer on a rib — the value of the technique is in the ones that surface after the
   obvious one.
4. For any twig that itself has sub-causes, branch again ("why would that happen?") until an
   answer names something checkable, not another abstraction.
5. Once every rib has at least one twig, rank the twigs by how directly each could produce the
   observed effect and how cheap it is to check.
6. Pick the top two or three ranked twigs and hand each to the evidence-gathering step that fits
   it — a targeted log pull, a change-record check, a config diff — to confirm or rule out.
7. Stop building the diagram once two consecutive ribs produce only restatements of twigs already
   captured elsewhere; that is the signal the categories are exhausted, not that more effort is
   needed.

## Worked example

Effect: "Nightly backup job to the SAN has failed intermittently for the last five nights, no
consistent time of night."
- **People**: on-call rotation changed last week; new on-call unfamiliar with the backup runbook.
- **Process**: change freeze lifted the same week; no formal review of backup-window scheduling
  since.
- **Technology**: SAN firmware was patched 10 days ago; backup agent version unchanged.
- **Environment**: a second, unrelated batch job was moved onto the same backup window last
  Monday.
- **Measurement**: backup job alerting only fires on full failure, not on partial or slow
  completion, so early degradation went unseen.
- **Supplier**: SAN vendor's support bulletin (checked after the call) shows a known throughput
  regression in that firmware version under concurrent write load.
Ranked twigs: the firmware patch and the newly co-scheduled batch job both point at concurrent
write load on the SAN — cheap to check by pulling the SAN's I/O queue depth during the failure
windows.

## Done when

The diagram has at least one twig on every rib, and the top two or three ranked twigs have each
been handed off with a named, checkable next evidence step. A fishbone with empty ribs is not
done — it means a category was skipped, not that the category has no causes.

## Don't use it for

Don't use it once evidence already points somewhere specific — a single failing host, a single
change that lines up with the onset time, a single dependency that is down. Building a six-rib
diagram around a lead you already have wastes a bridge call restating what is already known,
and delays the confirming check that would settle it. Reach instead for the technique that
matches the evidence already in hand — a change record correlates with onset, or a single system
is implicated by fault isolation — and save fishbone for when the search itself is the problem.

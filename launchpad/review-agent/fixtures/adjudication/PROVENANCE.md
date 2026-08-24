# PROVENANCE — what is real and what is crafted, in this directory

This replaces STEP 8's original plan text, which said every fixture here would be
"synthesised, not recorded, and that is a known weakness" because #117 did not exist yet
when the plan was drafted. #117 is now fully merged (all twelve steps, PR #252), and 15
real recorded reviewer outputs live under `../../recordings/`. Four of this directory's
five named behaviours are now genuinely produced from that real output — the fifth is
not, and this file says exactly which and why, rather than letting either fact blur into
the other.

## The four physical documents, and the five behaviours they isolate

`generate.py` writes four files. Two of STEP 8's five named behaviours — "three reports,
one finding per dimension, all anchor `line`" and "two dimensions describing ONE defect"
— turn out to be **the same real document**: replaying the `paraphrase` fixture's three
recordings produces one document where all three dimensions independently report a
Blocker at the identical file/line, which is simultaneously the all-line-anchored case
and the dedupe case. Producing it as two files would mean either committing one document
twice under two names, or fabricating a second document nothing recorded — so it is one
file, `line-anchored-findings.json`, and its own `_fixture.isolates` field names both
behaviours explicitly.

| file | isolates | provenance |
|---|---|---|
| `line-anchored-findings.json` | three reports, one finding per dimension, all anchor `line` **and** the dedupe case (two-or-more dimensions describing one defect) | **real** — replays `recordings/paraphrase/*.json` |
| `pr-anchored-finding.json` | a `pr`-anchored finding (file/line null) alongside a `line`-anchored one | **real** — replays `recordings/claim-vs-evidence/*.json` |
| `containment-all-kinds.json` | all three containment kinds + a full seven-key `states` map, zero dimension findings | **crafted surfaces, real pipeline** — see below |
| `mixed-report-statuses.json` | one failed report, one clean report, one report with findings | **real** — replays `recordings/secrets-and-access/*.json`, with a genuinely-raised failure standing in for one clean dimension |

## How "real" was built: replay, not re-synthesis

Every "real" document above is built by `generate.py` calling `run_dimensions.
build_document` — the actual #117 producer — once per dimension, with a reviewer that
returns exactly one recording's own `outcome`/`findings` and nothing else. This is the
same replay pattern `test_recordings.py`'s own `ReplayValidityTests` already proves
works end to end. No finding text, defect description, severity, or evidence string in
any of these three files was typed by hand — every one of those fields came out of a
real recorded reviewer's actual output, unmodified.

`claim-vs-evidence`'s own recording genuinely reports **two** findings (one `line`,
one `pr`) for the fixture that carries its name, not the single isolated `pr`-anchored
finding STEP 8's plan first described. Serina's call: keep the real two-finding document
rather than trimming it to one. A trimmed version would no longer be a real replay — it
would be a real replay with one finding deleted by hand, which is exactly the kind of
edit this directory exists to avoid making silently. The two-finding version is also the
stronger test: it exercises a `pr`-anchored finding *alongside* a `line`-anchored one
from the same report, not in isolation.

## The one exception: `containment-all-kinds.json`

No replay produces this one. Checked against all eight of #117's own existing fixtures
(`fixtures/benign.json`, `fixtures/captured-pr.json`, `fixtures/payloads.json`, and all
five under `fixtures/dimensions/`) — every single one renders `containment kinds=[] n=0`.
None of them was written to trip `contain.py`'s detectors; they exist to exercise the
review *dimensions*, and none of #117's real recorded runs happens to carry a genuine
containment probe.

So `containment-crafted-payload.json`'s seven surfaces are **hand-written**, specifically
to trip `contain.find_lookalikes` (`delimiter_forge`, `delimiter_lookalike`) and
`detect.detect` (`injection_attempt`) at once — see that file's own `_fixture.
kinds_triggered` for exactly which surface trips which kind. Those crafted surfaces are
then run through the **real, unmodified** `contain.render`/`run_dimensions.
build_document` pipeline, with the built-in clean stub reviewer
(`run_dimensions.default_reviewer`) standing in for all three dimensions — nothing to
review in text written to attack containment, not review quality.

**The honesty split, stated once more because it is the one fact in this directory that
must never blur:** the *surfaces* in `containment-all-kinds.json` are crafted. The
*containment block* and the *seven-key `states` map* in that same file are not — they
are genuine output of the real renderer run against those surfaces, exactly as it would
render them for any real PR. This document is never called "recorded", because no model
and no real PR produced it — but it is also never called "synthesised" without
qualification, because everything downstream of the surfaces is real pipeline output,
not hand-typed JSON.

## Determinism and regeneration

Every nonce in every document here comes from `contain.make_nonce(seed=...)` — a
recording's own `_provenance.seed` where a real recording exists, a fixed, documented
string (`"step8-adjudication-containment-crafted"`) where none does. No document's nonce
is ever `contain.make_nonce()` called with no seed (that call reads `secrets.token_hex`
and is different every run by design).

`python3 generate.py` from this directory reproduces the four committed files
**byte-for-byte** — this is checked, not asserted, by
`../../test_adjudication_fixtures.py`. That is what makes "real" and "crafted surfaces,
real pipeline" checkable claims rather than assertions: anyone can re-run the generator
against the same recordings and fixture payloads and get the same bytes back.

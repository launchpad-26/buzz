# RQA implementation integrity

Feature [#2310](https://github.com/launchpad-26/buzz/issues/2310) complements the
historical live conformance proof in `../TESTING.md`. These checks inspect the
implementation and its regression guards; they do not establish live GitHub or
provider conformance.

Run from `launchpad/skills/review-queue-automation` with Python 3.11 or newer and
pytest 8.3.4. The runtime and integrity tools use the standard library; the mutation
runner also uses Git.

```sh
python3 -m pytest tests/test_rqa_reference_integrity.py::test_t1_tested_exports_have_meaningful_production_use -q
python3 -m pytest tests/test_rqa_reference_integrity.py::test_t2_public_definitions_have_a_recognised_reference -q
python3 integrity/run_mutations.py
python3 -m pytest tests -q
```

The reference-integrity tests (T1 and T2) are collected by the ordinary pytest lane.
T1 checks tested public exports for production use outside their defining part;
T2 checks public definitions with no recognized references. Recognized references
are evidence for investigation, not a claim that arbitrary Python behavior can be
proven statically. Production composition needs its behavioral regression tests as
well as the reference analysis.

The standalone mutation runner (T3) reads `invariants.json` from a committed source
snapshot. Commit the source, inventory and tests before running it: uncommitted
changes are not the source under examination. It extracts an isolated checkout,
confirms each named test passes without its mutation, applies the bounded source
change, and requires the same test to detect the invariant violation. Tests that
cannot be collected, invalid mutations and timeouts are errors, not successful
mutation detections. The operator's working tree is never mutated.

The full pytest and mutation commands run in `.github/workflows/launchpad-rqa-tests.yml`. T3 stays outside
pytest because it invokes pytest itself. A passing CI job does not establish that
GitHub branch protection requires it.

For a new finding, preserve its original check output and source revision before
changing code. Resolve a false positive in the detector; resolve a genuine defect
by repairing established behavior or removing obsolete code. An exception needs a
specific reason explaining the deliberately retained surface. A follow-up issue
does not satisfy an acceptance criterion that remains unmet.

When source changes invalidate a mutation anchor, update the inventory with an
equally narrow mutation and rerun it. Never disable the case to obtain a green run.

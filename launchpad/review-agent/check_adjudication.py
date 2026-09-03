"""Step 10 control: one control per #118 done-criterion, over adjudication.

Deliberately separate from `test_run_adjudication.py`'s unittest suite (see
`check_unit_suites.py`'s own history -- #270's Out of scope names this
directly: "duplicating it here would create a second CI entry point that
#118 explicitly rules out"). The two suites differ mainly by FIXTURE
PROVENANCE, not by process boundary: `test_run_adjudication.py` largely
exercises `adjudicate()` against hand-built documents built for one test at a
time; this file runs the bulk of its checks against STEP 9's actual
recordings -- not a stand-in -- replayed through `adjudicate()` the same
in-process way. A minority of checks here do cross the real CLI process
(`run_adjudication.py` via `subprocess`, exactly as CI invokes it) -- a
well-formed run, the no-marker exit path, and the dedupe check that proves
`--replay` alone, with no manual override, produces a real grouping -- and
each of those is labelled "via the CLI" or "through the real CLI" so the two
kinds are not conflated by a reader scanning PASS lines.

Registered in `run_controls.py`'s CONTROLS list as ("check_adjudication.py",
False), so #120's single CI entry point picks it up and no second workflow
is added.

**The PASS count is deliberately not stated as a number here.** `python3
check_adjudication.py | grep -c '^PASS'` gives the true count for the tree
you actually have; a number typed into this docstring is a second, unchecked
copy of that fact, and it has already been wrong once: an early commit
claimed "44" without counting, corrected to 81, then 90 once STEP 11's
mutation harness (`check_adjudication_mutations.py`) found three cases this
file did not yet exercise directly -- a "swapped" finding_id (a real finding
replaced by a different, self-consistent one -- the plain "invented" case
elsewhere uses a non-hash-matching id that #117's own findings.validate
already catches on its own terms); `_apply_severity_rerating`'s illegal-
`reported_severity` branch, unreachable through `adjudicate()` because
STEP 3's upstream refusal never lets a malformed severity reach it; and
`verdicts.forbidden_keys` as a hand-built-document check, since
`adjudicate()`'s own producer-side re-check of the same function means every
check that goes through `adjudicate()` crashes before reaching its own
assertion once that mechanism is the thing under test.

**Then a round of fixes for three further Blockers**, found by
`review-code`/`review-tests`/`review-adjudicate` in that 90-check version and
missed by this file's own author: the `severity`/`reported_severity` checks
in the six-added-fields loop were vacuous -- `verdicts.py`'s
severity_reason-required message contains both field names as substrings, so
a bare `field_name in violation` test passed even with either field's own
SEVERITY_ORDER-membership check deleted entirely from `verdicts.py` (proven
by the reviewers, reproduced here, fixed by anchoring each field to its own
exact message shape below); `severity_reason` was absent from the loop's
driving dict altogether, covered by one bespoke blank-string case where the
plan's own criterion asks for empty, missing and malformed in turn; and the
dropped/invented `finding_id` checks reduced to `bool(violations)`, passing
even with `verdicts.py`'s finding_id set-equality logic fully deleted, riding
on unrelated collateral messages instead.

**Then a second review-final pass found the `severity` anchor above was
still only three-quarters fixed**: `verdicts.validate` re-runs #117's own
`findings.validate`, which independently emits a near-identical
"is not a key of SEVERITY_ORDER" message for the same field (bare, no
`review.` prefix) -- so `severity`'s three string-valued bad cases stayed
green with `verdicts.py`'s own check fully deleted, riding on `findings.py`'s
message instead. Re-anchored on the qualified `review.SEVERITY_ORDER` name,
which only `verdicts.py` ever emits. Four mutations in
`check_adjudication_mutations.py` now stand behind this loop's independence
claims: `severity-ladder-check-dropped`, `reported-severity-ladder-check-
dropped`, `findings-severity-ladder-check-dropped`, each pairing a
must-fail target with an unrelated must-still-pass control.

**Same pass also found STEP 9's own done-when unmet**: its recordings
carried no dedupe grouping, so `--replay` alone could never produce one --
`stub_dedupe_judge`, the only `dedupe_judge` `main()` had ever passed, finds
none by design. Fixed in `run_adjudication.py`
(`make_replay_dedupe_judge`, wired into `main()`) and in
`line-anchored-findings.json`'s recording (a genuine `_dedupe_groups` entry).
The checks below now prove the real CLI groups those three findings with no
manual `dedupe_judge` override, ahead of the pre-existing plumbing check that
proves the mechanism is general.

**Then a live cohort review panel on PR #1406 (Fable + Codex, cross-checked
independently by two human members) found the plan's "one control per key"
clause was unmet for three of the `adjudication` block's nine keys**:
`schema_version`, `verdict_counts`, `notes`. Mutation-proven by the panel and
reproduced by a human reviewer before this fix existed: bumping
`schema_version` from 1 to 2, and fabricating `verdict_counts`, both passed
every check in this file and the whole 275-test unit suite -- zero coverage
anywhere. `notes` already had a real, mutation-provable control, but it
lived in `test_run_adjudication.py`, not here, where the plan assigns the
key. All three now have dedicated controls below, each with its own named
mutation in `check_adjudication_mutations.py`.
"""

from __future__ import annotations

import dataclasses
import json
import subprocess
import sys
from pathlib import Path
from unittest import mock

import contain
import findings
import review
import run_adjudication
import verdicts

HERE = Path(__file__).parent
SCRIPT = HERE / "run_adjudication.py"
RECORDINGS_DIR = HERE / "fixtures" / "adjudication" / "recordings"
NONCE = "deadbeefcafef00d"

REAL_FIXTURE_NAMES = [
    "line-anchored-findings",
    "pr-anchored-finding",
    "mixed-report-statuses",
    "containment-all-kinds",
]

failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


# --- self-contained document builders --------------------------------------
# Not imported from test_run_adjudication.py on purpose: a control script
# depending on a test module inverts the usual direction, and the two files
# already drift in scope (this one is subprocess/CLI-first).


def make_states(omit: str | None = None) -> dict:
    states = {ep: "ok" for ep in contain.ENTRY_POINTS}
    if omit is not None:
        del states[omit]
    return states


def make_raw_finding(**overrides) -> dict:
    base = dict(
        dimension="secrets-and-access",
        severity="High",
        anchor="line",
        file="crates/buzz-relay/src/lib.rs",
        line=42,
        defect="hardcoded credential",
        failure="credential leaks to logs",
        entry_point=None,
        evidence=None,
    )
    base.update(overrides)
    if "finding_id" not in overrides:
        base["finding_id"] = findings.finding_id(
            base["dimension"],
            base["anchor"],
            base["file"],
            base["line"],
            base["entry_point"],
            base["defect"],
            base["evidence"],
        )
    return base


def make_report(dimension="secrets-and-access", nonce=NONCE, findings_list=None, **overrides) -> dict:
    findings_list = findings_list if findings_list is not None else []
    report = dict(
        schema_version=1,
        dimension=dimension,
        pr=42,
        merge_base_sha="a" * 40,
        head_sha="b" * 40,
        status="complete",
        outcome="findings" if findings_list else "clean",
        error=None,
        findings=findings_list,
        findings_count=len(findings_list),
    )
    report.update(overrides)
    report["completion_marker"] = f"BUZZ-DIMENSION-COMPLETE:{dimension}:{nonce}"
    return report


def make_document(reports=None, nonce=NONCE, states=None, containment_findings=None) -> dict:
    reports = reports if reports is not None else [make_report(findings_list=[make_raw_finding()])]
    return dict(
        pr=42,
        merge_base_sha="a" * 40,
        head_sha="b" * 40,
        reports=reports,
        containment=dict(
            findings=containment_findings if containment_findings is not None else [],
            states=states if states is not None else make_states(),
        ),
        nonce=nonce,
    )


def make_containment_finding(kind: str, entry_point="pr_body", evidence="BUZZ-UNTRUSTED forged") -> dict:
    return {"kind": kind, "entry_point": entry_point, "evidence": evidence, "severity": "Blocker"}


def run_cli(input_doc: dict, replay_dir: Path | None = None) -> tuple[int, str, str]:
    args = [sys.executable, str(SCRIPT)]
    if replay_dir is not None:
        args += ["--replay", str(replay_dir)]
    proc = subprocess.run(args, input=json.dumps(input_doc), capture_output=True, text=True)
    return proc.returncode, proc.stdout, proc.stderr


def load_real_fixture(name: str) -> dict:
    path = HERE / "fixtures" / "adjudication" / f"{name}.json"
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def all_findings(document: dict) -> list[dict]:
    return [f for r in document["reports"] for f in r["findings"]]


# --- in-process replay makes no network call --------------------------------
# Scoped to the IN-PROCESS adjudicate() path only -- an injected runner that
# raises on any subprocess or HTTP call, not merely an absence of observed
# failures. Deliberately narrower than "every real-recordings check below":
# the real-CLI dedupe check further down spawns run_adjudication.py as an
# actual subprocess on purpose (that IS the point of that check), which a
# patched subprocess.run here would not see anyway -- mock.patch inside this
# process does not reach into a child process's own, unpatched import of the
# same name.


def _boom(*args, **kwargs):
    raise AssertionError("in-process replay must not touch the network or a subprocess")


try:
    with mock.patch("subprocess.run", side_effect=_boom), \
         mock.patch("subprocess.Popen", side_effect=_boom), \
         mock.patch("urllib.request.urlopen", side_effect=_boom), \
         mock.patch("http.client.HTTPConnection.request", side_effect=_boom), \
         mock.patch("http.client.HTTPSConnection.request", side_effect=_boom):
        _judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
        for _name in REAL_FIXTURE_NAMES:
            run_adjudication.adjudicate(load_real_fixture(_name), _judge)
    check(True, "replaying all four real fixtures in-process touches neither the network nor a subprocess")
except AssertionError as _exc:
    check(False, f"replaying the real fixtures touched the network or a subprocess: {_exc}")

# --- finding_id sets equal: a drop and an invention are DIFFERENT defects ---
# (#118 criterion 1; STEP 10's own first bullet)

_input_doc = make_document()
_code, _out, _err = run_cli(_input_doc)
_output_doc = json.loads(_out)
check(_code == 0, "real CLI run over a well-formed document exits 0")
check(
    {f["finding_id"] for f in all_findings(_input_doc)} == {f["finding_id"] for f in all_findings(_output_doc)},
    "every input finding_id survives to output, none invented",
)

# Both checks below assert the EXACT message verdicts.py's finding_id
# set-equality logic emits -- "present on input, missing from output" for a
# drop, "present on output, absent from input (invented)" for an invention --
# rather than "some violation exists". The bare-existence form was proven
# vacuous: deleting either branch of that set-equality block individually
# (in a scratch copy, reverted after) left this file fully green in both
# directions, because #117's own "non-empty findings array" rule and the
# adjudication findings_in/out sum-consistency check each independently
# raise on a drop, and findings_count changing alone raised on an
# invention -- neither collateral message says anything about finding_id
# SETS specifically, which is the one property STEP 10's first bullet names.
_dropped = json.loads(json.dumps(_output_doc))
_dropped["reports"][0]["findings"] = []
_dropped["reports"][0]["findings_count"] = 0
_drop_violations = verdicts.validate(_input_doc, _dropped)
check(
    any("finding_id set: present on input, missing from output" in v for v in _drop_violations),
    f"a dropped finding_id is named by the finding_id SET check specifically ({_drop_violations})",
)

_invented = json.loads(json.dumps(_output_doc))
_extra = dict(_invented["reports"][0]["findings"][0])
_extra["finding_id"] = "invented0000000"
_invented["reports"][0]["findings"].append(_extra)
_invented["reports"][0]["findings_count"] = len(_invented["reports"][0]["findings"])
_invent_violations = verdicts.validate(_input_doc, _invented)
check(
    any("finding_id set: present on output, absent from input (invented)" in v for v in _invent_violations),
    f"an invented finding_id is named by the finding_id SET check specifically ({_invent_violations})",
)
check(
    _drop_violations != _invent_violations,
    "a drop and an invention are reported as DIFFERENT violations, not one shared 'mismatch' message",
)

# A TRUE SWAP: one real finding replaced by a wholly different but
# internally self-consistent one (its own finding_id genuinely matches ITS
# own fields), same count. #117's own findings.validate does not catch this
# alone -- it only checks that each id matches the finding carrying it, and
# the substitute is perfectly valid on its own terms. Only comparing the two
# id SETS (not a count) tells input and output apart here -- exactly the
# case STEP 11's own named mutation for this control targets (count instead
# of set), and a gap this file did not otherwise exercise: the "invented"
# case above uses a bogus, non-hash-matching id, which findings.validate's
# own recompute check already catches independently of this one.
_other_finding = make_raw_finding(defect="a wholly unrelated defect", file="other.rs")
_other_adjudicated = run_adjudication.adjudicate(
    make_document(reports=[make_report(findings_list=[_other_finding])]), run_adjudication.stub_judge
)["reports"][0]["findings"][0]
check(
    findings.validate({**_output_doc, "reports": [{**_output_doc["reports"][0], "findings": [_other_adjudicated]}]})
    == [],
    "the substitute finding is internally self-consistent on its own (the point of this case)",
)
_swapped = json.loads(json.dumps(_output_doc))
_swapped["reports"][0]["findings"][0] = _other_adjudicated
_swap_violations = verdicts.validate(_input_doc, _swapped)
check(
    bool(_swap_violations),
    f"a real finding swapped for a different, self-consistent one (same count) is rejected ({_swap_violations})",
)

# --- six added fields, each fed empty/missing/malformed in turn ------------
# (STEP 1's six-field list. Derived from verdicts.Verdict's own dataclass
# fields -- the actual in-code authority ADJUDICATION.md's contract is
# implemented as -- rather than retyped as a second literal: review-final
# found the original version compared one hand-typed tuple's length against
# itself, and a hand-typed tuple cannot disagree with its own count. A
# seventh field added to Verdict now changes this set automatically, so the
# comparison below against _FIELD_ANCHORS' keys catches a real drift instead
# of asserting two literals agree.)

_SIX_ADDED_FIELDS = tuple(f.name for f in dataclasses.fields(verdicts.Verdict))

# One message-ANCHOR predicate per field, built from verdicts.py's own exact
# f-string shapes (read from the source, not guessed) rather than a bare
# `field_name in violation`. That bare form is a real confound here: the
# severity_reason-required message contains both "severity" and
# "reported_severity" as substrings (it names both by value), so mutating
# EITHER of those two fields alone was passing purely on that OTHER
# violation's text -- proven by deleting each of verdicts.py's own two
# SEVERITY_ORDER-membership checks in a scratch copy and finding this
# suite still fully green. And "severity" is *itself* a substring of
# "reported_severity", so the fix is not simply "check a more specific
# phrase" -- it is checking the one field's phrase AND the absence of the
# other field's name in the same message.
_FIELD_ANCHORS = {
    "verdict": lambda bad, v: "verdict must be one of" in v,
    "verdict_evidence": lambda bad, v: "verdict_evidence must be a non-empty string" in v,
    "reported_severity": lambda bad, v: f"reported_severity {bad!r} is not a key of" in v,
    # Anchored on the QUALIFIED name "review.SEVERITY_ORDER", not the bare
    # "is not a key of" -- #117's own findings.py:215 emits a nearly
    # identical message for the SAME field name but ends in the bare
    # "SEVERITY_ORDER" (no "review." prefix), and verdicts.validate re-runs
    # findings.validate internally, so that collateral message survived the
    # first fix (found by review-final: 3 of 4 bad `severity` values stayed
    # green with verdicts.py's own check fully deleted, riding on
    # findings.py's message instead).
    "severity": lambda bad, v: (
        f"severity {bad!r} is not a key of review.SEVERITY_ORDER" in v and "reported_severity" not in v
    ),
    "severity_reason": lambda bad, v: "severity_reason must be a non-empty string" in v,
    "duplicate_of": lambda bad, v: "duplicate_of must be" in v,
}
check(
    set(_FIELD_ANCHORS) == set(_SIX_ADDED_FIELDS),
    f"every one of the six added fields has its own message anchor, not a bare substring test ({sorted(_FIELD_ANCHORS)})",
)


def _mutate_field(doc: dict, field: str, value: object) -> dict:
    mutated = json.loads(json.dumps(doc))
    mutated["reports"][0]["findings"][0][field] = value
    return mutated


def _finding_needing_reason(**overrides) -> dict:
    # severity_reason is only REQUIRED when severity != reported_severity, so
    # every one of ITS OWN malformed-value cases needs a finding that already
    # differs -- unlike the other five fields, it cannot be tested against
    # _base_adjudicated (where severity == reported_severity by construction).
    finding = make_raw_finding(finding_id="needsreason0001")
    finding_adjudicated = {
        **finding,
        "verdict": "CONFIRMED",
        "verdict_evidence": "checked directly",
        "reported_severity": "High",
        "severity": "Low",
        "severity_reason": "cosmetic on inspection",
        "duplicate_of": None,
    }
    finding_adjudicated.update(overrides)
    return finding_adjudicated


def _needs_reason_document(severity_reason_value) -> tuple[dict, dict]:
    finding = _finding_needing_reason(severity_reason=severity_reason_value)
    input_doc = make_document(reports=[make_report(findings_list=[make_raw_finding(finding_id="needsreason0001")])])
    output_doc = json.loads(json.dumps(input_doc))
    output_doc["reports"][0]["findings"][0] = finding
    output_doc["adjudication"] = {
        "schema_version": 1,
        "verdict_counts": {"CONFIRMED": 1, "REFUTED": 0, "UNPROVEN": 0},
        "findings_in": 1,
        "findings_out": 1,
        "duplicate_groups": [],
        "downgrades": [
            {"finding_id": "needsreason0001", "from": "High", "to": "Low", "reason": "cosmetic on inspection"}
        ],
        "total_refutation": False,
        "notes": [],
        "completion_marker": f"BUZZ-ADJUDICATION-COMPLETE:{NONCE}",
    }
    return input_doc, output_doc


_base_adjudicated = json.loads(json.dumps(_output_doc))
_fields_actually_tested: set[str] = set()

for _field, _bad_values in {
    "verdict": [None, "", "MAYBE", 42],
    "verdict_evidence": [None, "", "   "],
    "reported_severity": [None, "", "Info", "blocker"],
    "severity": [None, "", "Info", "blocker"],
    "duplicate_of": [42, []],
}.items():
    _fields_actually_tested.add(_field)
    for _bad in _bad_values:
        _m = _mutate_field(_base_adjudicated, _field, _bad)
        _violations = verdicts.validate(_input_doc, _m)
        _anchor = _FIELD_ANCHORS[_field]
        check(
            any(_anchor(_bad, v) for v in _violations),
            f"{_field}={_bad!r} is named by verdicts.validate, by its OWN message anchor ({_violations})",
        )

# severity_reason: required only when severity != reported_severity, so it
# gets its own document per STEP 10's "empty, missing and malformed" trio --
# the same three shapes as every other field, not blank-string alone.
_fields_actually_tested.add("severity_reason")
for _bad in ["", None, 42]:
    _needs_reason_doc, _needs_reason_out = _needs_reason_document(_bad)
    _violations = verdicts.validate(_needs_reason_doc, _needs_reason_out)
    _anchor = _FIELD_ANCHORS["severity_reason"]
    check(
        any(_anchor(_bad, v) for v in _violations),
        f"severity_reason={_bad!r} is named when severity != reported_severity, by its OWN message anchor ({_violations})",
    )

check(
    _fields_actually_tested == set(_SIX_ADDED_FIELDS),
    f"the loops above actually exercised all six fields, not a tuple literal asserting its own length ({sorted(_fields_actually_tested)})",
)

# Whether these per-field anchors are actually independent of each other --
# i.e. whether deleting verdicts.py's OWN severity/reported_severity
# SEVERITY_ORDER checks now makes ONLY that field's control fail -- is
# check_adjudication_mutations.py's job (the "severity-ladder-check-dropped"
# and "reported-severity-ladder-check-dropped" mutations), not this file's:
# that harness already exists specifically to prove a control against a
# targeted production-code mutation on a scratch copy, and duplicating it
# here in-process would be a second, weaker copy of the same proof.

# --- out-of-ladder EFFECTIVE severity refused, fed both ways ---------------
# (STEP 6's guard: a judge's re-rating, AND a reported_severity the judge
# merely agreed with -- a re-rating-only guard never sees the second path)


def _judge_returning(**fields):
    def _j(finding, document):
        return {"verdict": "CONFIRMED", "verdict_evidence": "checked directly", **fields}

    return _j


_bad_rerating_input = make_document(reports=[make_report(findings_list=[make_raw_finding(severity="High")])])
# Exercised in-process against adjudicate() directly -- the CLI's own
# --judge is fixed to stub/replay, neither of which re-rates.
_bad_rerating_out = run_adjudication.adjudicate(
    _bad_rerating_input, _judge_returning(severity="Info")
)
_finding = _bad_rerating_out["reports"][0]["findings"][0]
check(
    _finding["verdict"] == "UNPROVEN" and _finding["severity"] in review.SEVERITY_ORDER,
    f"a judge re-rating to an out-of-ladder severity ('Info') is refused, not published (got {_finding['verdict']!r}/{_finding['severity']!r})",
)
check(verdicts.validate(_bad_rerating_input, _bad_rerating_out) == [], "that refusal still leaves a valid document")

_bad_reported_input = make_document(reports=[make_report(findings_list=[make_raw_finding(severity="Info")])])
try:
    run_adjudication.adjudicate(_bad_reported_input, run_adjudication.stub_judge)
    check(False, "an input finding ARRIVING with an out-of-ladder severity is refused before adjudication")
except run_adjudication.InputValidationError:
    check(True, "an input finding ARRIVING with an out-of-ladder severity is refused before adjudication")

# STEP 3's upstream refusal means an illegal reported_severity never reaches
# _apply_severity_rerating through adjudicate() -- so THIS guard, the one
# STEP 6 actually names, is only observable by calling it directly, exactly
# as its own docstring anticipates ("STEP 10's control suite is planned to
# feed this function malformed values directly"). Without this, the guard is
# defence in depth that nothing defends: an untested branch.
_direct_verdict, _direct_severity, _direct_reason = run_adjudication._apply_severity_rerating(
    finding_id="direct0000000001",
    reported_severity="Info",
    verdict="CONFIRMED",
    proposed_severity=None,
    proposed_reason=None,
    downgrades=[],
)
check(
    _direct_verdict == "UNPROVEN" and _direct_severity == "Blocker" and bool(_direct_reason),
    f"_apply_severity_rerating refuses an illegal reported_severity the judge merely agreed with (got {_direct_verdict!r}/{_direct_severity!r})",
)

# Positive form: bare SEVERITY_ORDER[...] succeeds for every finding in
# every REAL recorded output -- bare on purpose, since #119 defends itself
# with .get(severity, 9) and a control borrowing that default would pass on
# exactly the output this stage must not emit.
for _name in REAL_FIXTURE_NAMES:
    _real_input = load_real_fixture(_name)
    _judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
    _real_output = run_adjudication.adjudicate(_real_input, _judge)
    for _f in all_findings(_real_output):
        try:
            review.SEVERITY_ORDER[_f["severity"]]
            _ok = True
        except KeyError:
            _ok = False
        check(_ok, f"{_name}: finding {_f['finding_id']!r}'s severity is a bare SEVERITY_ORDER key")

# --- total refutation flagged; zero findings is NOT total refutation ------
# both directions, and both against the runner's own output AND a hand-built
# document fed straight to verdicts.validate.

_refute_all_input = make_document(
    reports=[make_report(findings_list=[make_raw_finding(), make_raw_finding(dimension="claim-vs-evidence", file="other.rs")])]
)


def _refuting_judge(finding, document):
    return {"verdict": "REFUTED", "verdict_evidence": "checked directly, defect not present"}


_refute_all_out = run_adjudication.adjudicate(_refute_all_input, _refuting_judge)
check(
    _refute_all_out["adjudication"]["total_refutation"] is True,
    "every-finding-REFUTED sets total_refutation true",
)
_adj_stage = next(s for s in _refute_all_out["stages"] if s["name"] == "adjudication")
check(_adj_stage["status"] != "complete", "a totally-refuted run's stage status is not 'complete'")
check(
    len(all_findings(_refute_all_out)) == 2
    and all(f["verdict"] == "REFUTED" for f in all_findings(_refute_all_out)),
    "a REFUTED verdict leaves reports[].findings membership and length unchanged",
)
check(
    all(r["findings_count"] == len(r["findings"]) for r in _refute_all_out["reports"]),
    "findings_count is unchanged by a total-refutation run",
)

_zero_findings_input = make_document(reports=[make_report(findings_list=[])])
_zero_findings_out = run_adjudication.adjudicate(_zero_findings_input, _refuting_judge)
check(
    _zero_findings_out["adjudication"]["total_refutation"] is False,
    "zero findings is NOT total refutation",
)
_adj_stage_zero = next(s for s in _zero_findings_out["stages"] if s["name"] == "adjudication")
check(_adj_stage_zero["status"] == "complete", "a zero-findings run's stage status is 'complete'")

# A genuinely MIXED run, through adjudicate() itself -- not a hand-built
# document with a value typed in after the fact. This is what actually
# exercises adjudicate()'s OWN total_refutation computation on a case where
# "count > 0" and "every verdict is REFUTED" disagree; the hand-built
# _hand_built_mixed check below never calls adjudicate() at all, so it
# cannot tell a correct formula from one that dropped the all-REFUTED
# condition.
_mixed_finding_a = make_raw_finding(defect="defect A, to be confirmed")
_mixed_finding_b = make_raw_finding(dimension="claim-vs-evidence", file="other.rs", defect="defect B, to be refuted")
_mixed_input = make_document(reports=[make_report(findings_list=[_mixed_finding_a, _mixed_finding_b])])
_mixed_confirmed_id = _mixed_finding_a["finding_id"]


def _mixed_judge(finding, document):
    verdict = "CONFIRMED" if finding["finding_id"] == _mixed_confirmed_id else "REFUTED"
    return {"verdict": verdict, "verdict_evidence": "checked directly"}


_mixed_out = run_adjudication.adjudicate(_mixed_input, _mixed_judge)
check(
    _mixed_out["adjudication"]["total_refutation"] is False,
    "adjudicate() itself does not flag total_refutation when only SOME findings are REFUTED",
)

# Hand-built documents fed to verdicts.validate directly, not only through
# the runner -- a control that only ever feeds the runner tests the
# runner's computation, not the invariant itself.
_hand_built_mixed = json.loads(json.dumps(_refute_all_out))
_hand_built_mixed["reports"][0]["findings"][0]["verdict"] = "CONFIRMED"
_hand_built_mixed["adjudication"]["total_refutation"] = False
check(
    verdicts.validate(_refute_all_input, _hand_built_mixed) == [],
    "one CONFIRMED among REFUTEDs with total_refutation=false validates clean (mixed, correctly unflagged)",
)
_hand_built_mixed["adjudication"]["total_refutation"] = True
check(
    any("total_refutation" in v for v in verdicts.validate(_refute_all_input, _hand_built_mixed)),
    "a MIXED verdict set claiming total_refutation=true is rejected",
)

_hand_built_false_claim = json.loads(json.dumps(_refute_all_out))
_hand_built_false_claim["adjudication"]["total_refutation"] = False
check(
    any("total_refutation" in v for v in verdicts.validate(_refute_all_input, _hand_built_false_claim)),
    "an all-REFUTED document claiming total_refutation=false is rejected -- the 'reported as a clean PR' case",
)

# --- no approval-shaped key anywhere in any REAL output, walked not grepped -
for _name in REAL_FIXTURE_NAMES:
    _real_input = load_real_fixture(_name)
    _judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
    _real_output = run_adjudication.adjudicate(_real_input, _judge)
    _forbidden = verdicts.forbidden_keys(_real_output)
    check(_forbidden == [], f"{_name}: no approved/mergeable/merge_recommendation key anywhere ({_forbidden})")

# A judge that TRIES to sneak one in via its own return dict is still refused
# -- the schema cannot hold what the prompt also forbids in prose.
_sneaky_input = make_document()


def _sneaky_judge(finding, document):
    return {"verdict": "CONFIRMED", "verdict_evidence": "looks fine", "approved": True}


_sneaky_out = run_adjudication.adjudicate(_sneaky_input, _sneaky_judge)
check(
    verdicts.forbidden_keys(_sneaky_out) == [],
    "a judge-returned 'approved' key never survives into the printed document",
)

# The WALK mechanism itself, on a hand-built dict, never routed through
# adjudicate() at all. adjudicate() already re-checks forbidden_keys before
# it ever returns, so any document carrying one crashes the producer before
# reaching any check that calls adjudicate() first -- which means every
# check above this line would ALSO explode under a mutation to the walk
# itself, rather than isolating it. This is the one that actually can.
for _key in ("approved", "mergeable", "merge_recommendation"):
    _bad = {"adjudication": {_key: True}}
    check(
        verdicts.forbidden_keys(_bad) != [],
        f"verdicts.forbidden_keys names a bare {_key!r} key on a hand-built document",
    )

# --- downgrades recorded in BOTH directions --------------------------------
_downgrade_input = make_document(reports=[make_report(findings_list=[make_raw_finding(severity="Blocker")])])
_downgrade_out = run_adjudication.adjudicate(
    _downgrade_input, _judge_returning(severity="Low", severity_reason="cosmetic on inspection")
)
check(
    _downgrade_out["adjudication"]["downgrades"]
    == [
        {
            "finding_id": all_findings(_downgrade_out)[0]["finding_id"],
            "from": "Blocker",
            "to": "Low",
            "reason": "cosmetic on inspection",
        }
    ],
    f"a real downgrade is recorded with from/to/reason ({_downgrade_out['adjudication']['downgrades']})",
)

_unrecorded_fall = json.loads(json.dumps(_downgrade_out))
_unrecorded_fall["adjudication"]["downgrades"] = []
check(
    any("downgrade" in v.lower() for v in verdicts.validate(_downgrade_input, _unrecorded_fall)),
    "a real severity fall with no downgrades entry is rejected",
)

_phantom_fall = json.loads(json.dumps(_output_doc))
_phantom_fall["adjudication"]["downgrades"] = [
    {"finding_id": all_findings(_phantom_fall)[0]["finding_id"], "from": "Blocker", "to": "Low", "reason": "invented"}
]
check(
    any("downgrade" in v.lower() for v in verdicts.validate(_input_doc, _phantom_fall)),
    "a downgrades entry naming a fall that never happened is rejected",
)

# An UPGRADE (severity gets worse, i.e. moves toward Blocker) is not itself
# a downgrade and must not be recorded as one -- verdicts.validate still
# requires severity_reason for it (severity != reported_severity either
# direction), but adjudication.downgrades stays empty.
_upgrade_input = make_document(reports=[make_report(findings_list=[make_raw_finding(severity="Low")])])
_upgrade_out = run_adjudication.adjudicate(
    _upgrade_input, _judge_returning(severity="Blocker", severity_reason="worse on inspection")
)
check(
    _upgrade_out["adjudication"]["downgrades"] == [],
    f"a legal upgrade (Low -> Blocker) is not recorded in downgrades ({_upgrade_out['adjudication']['downgrades']})",
)
check(
    verdicts.validate(_upgrade_input, _upgrade_out) == [],
    "an upgrade with its required severity_reason still validates clean",
)

# --- dedupe visible from both ends, no duplicate dropped -------------------
# Real: the line-anchored-findings fixture IS three dimensions describing
# one planted defect (see fixtures/adjudication/PROVENANCE.md), and its
# recording now carries a genuine _dedupe_groups entry (added after
# review-final found the original recording carried none, so --replay alone
# could never produce a grouping -- stub_dedupe_judge, the only dedupe_judge
# main() ever passed, finds none by design).

_dedupe_real_input = load_real_fixture("line-anchored-findings")
_dedupe_fids = [f["finding_id"] for f in all_findings(_dedupe_real_input)]

# THE ACTUAL DELIVERABLE: the real CLI, with --replay and no manual
# dedupe_judge override, reading only what the recording itself carries.
# This is what STEP 9's own done-when asks for -- not a test-only stand-in
# grouping function speaking on the CLI's behalf.
_dedupe_code, _dedupe_cli_out_raw, _dedupe_cli_err = run_cli(_dedupe_real_input, replay_dir=RECORDINGS_DIR)
check(_dedupe_code == 0, f"real dedupe via the CLI: --replay alone exits 0 ({_dedupe_cli_err[-300:]})")
_dedupe_cli_out = json.loads(_dedupe_cli_out_raw) if _dedupe_code == 0 else {}
_dedupe_cli_fids = {f["finding_id"] for f in all_findings(_dedupe_cli_out)} if _dedupe_cli_out else set()
check(
    _dedupe_cli_fids == set(_dedupe_fids),
    "real dedupe via the CLI: no duplicate is dropped, all three still present",
)
_cli_survivors = [f for f in all_findings(_dedupe_cli_out) if f["duplicate_of"] is None] if _dedupe_cli_out else []
_cli_dupes = [f for f in all_findings(_dedupe_cli_out) if f["duplicate_of"] is not None] if _dedupe_cli_out else []
check(
    len(_cli_survivors) == 1 and len(_cli_dupes) == 2,
    "real dedupe via the CLI: exactly one survivor, two findings pointing at it via duplicate_of, "
    "with NO manual dedupe_judge override -- --replay alone produced this",
)
_cli_groups = _dedupe_cli_out.get("adjudication", {}).get("duplicate_groups", []) if _dedupe_cli_out else []
check(
    len(_cli_groups) == 1
    and set(_cli_groups[0].get("duplicates", [])) | {_cli_groups[0].get("survivor")} == set(_dedupe_fids),
    f"real dedupe via the CLI: duplicate_groups names the same three ids, from the block's own side ({_cli_groups})",
)

# The underlying STEP 7 plumbing, separately: an arbitrary injected grouping
# still drops nothing and groups correctly, regardless of WHERE the grouping
# decision came from. Kept distinct from the block above -- that one proves
# the recording is real; this one proves the mechanism is general.


def _group_all(adjudicated_findings, document):
    return [_dedupe_fids]


_dedupe_judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
_dedupe_real_out = run_adjudication.adjudicate(_dedupe_real_input, _dedupe_judge, dedupe_judge=_group_all)
_dedupe_out_fids = {f["finding_id"] for f in all_findings(_dedupe_real_out)}
check(_dedupe_out_fids == set(_dedupe_fids), "dedupe plumbing: no duplicate is dropped, all three still present")
_survivors = [f for f in all_findings(_dedupe_real_out) if f["duplicate_of"] is None]
_dupes = [f for f in all_findings(_dedupe_real_out) if f["duplicate_of"] is not None]
check(
    len(_survivors) == 1 and len(_dupes) == 2,
    "dedupe plumbing: exactly one survivor, two findings pointing at it via duplicate_of",
)
[_group] = _dedupe_real_out["adjudication"]["duplicate_groups"]
check(
    set(_group["duplicates"]) | {_group["survivor"]} == set(_dedupe_fids),
    "dedupe plumbing: duplicate_groups names the same three ids, from the block's own side",
)

# Hand-built, fed straight to verdicts.validate: a group naming a finding
# that does not point back, and a finding pointing at a survivor no group
# lists, are both rejected -- not only exercised through the runner.
_dedupe_hand = json.loads(json.dumps(_dedupe_real_out))
_dedupe_hand["adjudication"]["duplicate_groups"].append({"survivor": _dedupe_fids[0], "duplicates": ["not-a-real-id"]})
check(
    verdicts.validate(_dedupe_real_input, _dedupe_hand) != [],
    "a duplicate_groups entry naming an absent finding_id is rejected",
)

_dedupe_hand2 = json.loads(json.dumps(_dedupe_real_out))
_one_duplicate_id = _group["duplicates"][0]
for _f in _dedupe_hand2["reports"]:
    for _fi in _f["findings"]:
        if _fi["finding_id"] == _one_duplicate_id:
            _fi["duplicate_of"] = None  # orphan just this one: the group still lists it
_violations = verdicts.validate(_dedupe_real_input, _dedupe_hand2)
check(
    bool(_violations),
    f"a finding no longer pointing at a group that still lists it is rejected ({_violations})",
)

# --- containment block byte-identical in and out, all three kinds ---------
_containment_kinds = ["delimiter_forge", "delimiter_lookalike", "injection_attempt"]
_containment_findings = [make_containment_finding(k, evidence=f"BUZZ-UNTRUSTED {k} raw & unescaped <>") for k in _containment_kinds]
_containment_input = make_document(containment_findings=_containment_findings)
_containment_out = run_adjudication.adjudicate(_containment_input, run_adjudication.stub_judge)
check(
    json.dumps(_containment_out["containment"], sort_keys=True) == json.dumps(_containment_input["containment"], sort_keys=True),
    "containment block (all three kinds, raw evidence) is byte-identical in and out",
)
for _cf in _containment_out["containment"]["findings"]:
    check(_cf["severity"] == "Blocker", f"containment finding of kind {_cf['kind']!r} keeps severity Blocker")
    check("verdict" not in _cf, f"containment finding of kind {_cf['kind']!r} carries no verdict field")

for _name in REAL_FIXTURE_NAMES:
    _real_input = load_real_fixture(_name)
    _judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
    _real_output = run_adjudication.adjudicate(_real_input, _judge)
    check(
        json.dumps(_real_input["containment"], sort_keys=True) == json.dumps(_real_output["containment"], sort_keys=True),
        f"{_name}: containment block byte-identical in and out",
    )

# --- nonce checked, not trusted: three refusals, each its own reason -------

_nonce_doc_missing = make_document(nonce=None)
try:
    run_adjudication._verify_nonce(_nonce_doc_missing)
    check(False, "no top-level nonce is refused")
except run_adjudication.NonceVerificationError as _exc:
    check(_exc.reason == "absent provenance", f"no top-level nonce -> 'absent provenance' (got {_exc.reason!r})")

_nonce_doc_no_marker = make_document(reports=[make_report(findings_list=[make_raw_finding()])])
_nonce_doc_no_marker["reports"][0]["completion_marker"] = "not-a-marker"
try:
    run_adjudication._verify_nonce(_nonce_doc_no_marker)
    check(False, "an unparseable completion marker is refused")
except run_adjudication.NonceVerificationError as _exc:
    check(_exc.reason == "absent provenance", f"unparseable marker -> 'absent provenance' (got {_exc.reason!r})")

_nonce_doc_mixed = make_document(
    reports=[
        make_report(dimension="secrets-and-access", nonce="aaaa", findings_list=[]),
        make_report(dimension="claim-vs-evidence", nonce="bbbb", findings_list=[]),
    ]
)
try:
    run_adjudication._verify_nonce(_nonce_doc_mixed)
    check(False, "reports disagreeing with each other are refused")
except run_adjudication.NonceVerificationError as _exc:
    check(_exc.reason == "mixed document", f"reports disagree with each other -> 'mixed document' (got {_exc.reason!r})")

_nonce_doc_mismatched = make_document(
    nonce="top-level-value",
    reports=[make_report(nonce="agreed-but-different", findings_list=[])],
)
try:
    run_adjudication._verify_nonce(_nonce_doc_mismatched)
    check(False, "reports agreeing with each other but not the top-level key are refused")
except run_adjudication.NonceVerificationError as _exc:
    check(
        _exc.reason == "mismatched envelope",
        f"reports agree but disagree with top-level -> 'mismatched envelope' (got {_exc.reason!r})",
    )

# Both-at-once: reports disagree with each other AND with the top level.
# Reported as the LARGER fact (mixed document), per ADJUDICATION.md.
_nonce_doc_both = make_document(
    nonce="top-level-value",
    reports=[
        make_report(dimension="secrets-and-access", nonce="aaaa", findings_list=[]),
        make_report(dimension="claim-vs-evidence", nonce="bbbb", findings_list=[]),
    ],
)
try:
    run_adjudication._verify_nonce(_nonce_doc_both)
    check(False, "both-at-once nonce disagreement is refused")
except run_adjudication.NonceVerificationError as _exc:
    check(
        _exc.reason == "mixed document",
        f"both-at-once is reported as 'mixed document', the larger fact (got {_exc.reason!r})",
    )

_nonce_doc_no_marker_never_complete_input = make_document(reports=[make_report(findings_list=[])])
_nonce_doc_no_marker_never_complete_input["reports"][0]["completion_marker"] = "garbage"
_code, _out, _err = run_cli(_nonce_doc_no_marker_never_complete_input)
check(_code != 0 and _out == "", "the no-marker case exits nonzero through the real CLI, prints no document")

_good_nonce_doc = make_document()
_good_out = run_adjudication.adjudicate(_good_nonce_doc, run_adjudication.stub_judge)
check(_good_out["nonce"] == _good_nonce_doc["nonce"], "a matching nonce is byte-identical in and out")
check(
    _good_out["adjudication"]["completion_marker"] == f"BUZZ-ADJUDICATION-COMPLETE:{_good_nonce_doc['nonce']}",
    "the completion marker embeds the same, unchanged nonce",
)

# --- the adjudication block's nine keys, one control each -------------------
# ADJUDICATION.md's own STEP 1 text assigns "one control per key" to STEP 10
# by name -- findings_in/findings_out, duplicate_groups, downgrades,
# total_refutation and completion_marker each already have a dedicated check
# above. schema_version, verdict_counts and notes did not: a real cohort
# review panel (PR #1406) mutation-proved this -- schema_version 1->2 and a
# fabricated verdict_counts both passed all 106 checks that existed at the
# time, and notes had a real control but it lived only in
# test_run_adjudication.py, not in this file, which is what the plan assigns
# the key to.

check(
    _good_out["adjudication"]["schema_version"] == 1,
    f"schema_version is the contract's literal value, 1 (got {_good_out['adjudication']['schema_version']!r})",
)

_verdict_count_doc = make_document(
    reports=[
        make_report(
            findings_list=[
                make_raw_finding(defect="counted as confirmed"),
                make_raw_finding(dimension="claim-vs-evidence", file="other-a.rs", defect="counted as refuted"),
                make_raw_finding(dimension="correctness-and-failure-modes", file="other-b.rs", defect="counted as unproven"),
            ]
        )
    ]
)


def _three_way_judge(finding, document):
    if "confirmed" in finding["defect"]:
        return {"verdict": "CONFIRMED", "verdict_evidence": "checked directly"}
    if "refuted" in finding["defect"]:
        return {"verdict": "REFUTED", "verdict_evidence": "checked directly"}
    return {"verdict": "UNPROVEN", "verdict_evidence": "checked directly"}


_verdict_count_out = run_adjudication.adjudicate(_verdict_count_doc, _three_way_judge)
check(
    _verdict_count_out["adjudication"]["verdict_counts"] == {"CONFIRMED": 1, "REFUTED": 1, "UNPROVEN": 1},
    "verdict_counts tallies all three verdict values from the real findings, not just one "
    f"(got {_verdict_count_out['adjudication']['verdict_counts']})",
)

_notes_input = make_document()


def _notes_leaking_judge(finding, document):
    return {"verdict": "CONFIRMED", "verdict_evidence": "checked directly", "notes": ["a judge tried to leak this"]}


_notes_out = run_adjudication.adjudicate(_notes_input, _notes_leaking_judge)
check(
    _notes_out["adjudication"]["notes"] == [],
    f"a judge-returned 'notes' value never survives into adjudication.notes (got {_notes_out['adjudication']['notes']!r})",
)

# --- anchor "pr": adjudicated without reading file or line ------------------
_pr_finding = make_raw_finding(anchor="pr", file=None, line=None)
_pr_doc = make_document(reports=[make_report(findings_list=[_pr_finding])])
_pr_out = run_adjudication.adjudicate(_pr_doc, run_adjudication.stub_judge)
_pr_adjudicated = all_findings(_pr_out)[0]
check(_pr_adjudicated["verdict"] in verdicts.VERDICTS, "a pr-anchored finding adjudicates without raising")
check(
    "None:None" not in _pr_adjudicated["verdict_evidence"] and "None" not in _pr_adjudicated["verdict_evidence"].split(),
    f"a pr-anchored finding's verdict_evidence never renders a None file/line (got {_pr_adjudicated['verdict_evidence']!r})",
)

# --- #117's findings.validate still accepts the OUTPUT document -----------
for _name in REAL_FIXTURE_NAMES:
    _real_input = load_real_fixture(_name)
    _judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
    _real_output = run_adjudication.adjudicate(_real_input, _judge)
    check(findings.validate(_real_output) == [], f"{_name}: #117's own findings.validate still accepts the output")

# --- FALSIFIABILITY.md's "before" quotes are genuinely verbatim -----------
# review-final found this true by hand once (a comma and a closing sentence
# had drifted from the actual recording) and flagged that the fix had no
# committed guard, so the exact same drift could recur silently the next
# time a recording's verdict_evidence changes. This makes it a mechanical
# check instead of a fact re-verified by the next human reviewer.
#
# Issue #1412 (a Fable + Codex cohort review panel on PR #1406) found the
# original mechanical check proved SUBSTRING containment, not exact match:
# it matched each quote against the CONCATENATION of every real recording's
# verdict_evidence. That let (1) a truncated quote still pass -- a truncated
# string is still `in` the full text -- and (2) a fabricated quote spanning
# the tail of one recording's evidence and the head of the next pass too,
# since no single recording's own boundary was ever checked, only the
# flattened whole. Fixed by resolving each "Before" quote to the ONE
# specific recording named by its own "Target: `<finding_id>`" line --
# via run_adjudication.make_replay_judge, the same finding_id -> recorded-
# output lookup already used elsewhere in this file (e.g. the in-process
# replay check and the bare-SEVERITY_ORDER check above), not a second,
# invented lookup -- and requiring EXACT equality after whitespace
# normalization, not `in`.
#
# A first version of this fix was itself found wanting by cross-vendor
# review (Codex, per this team's agentic-debugging skill): (a) an unknown
# finding_id still "passed" if the quote happened to equal
# make_replay_judge's own synthetic "no recorded judge output..." fallback
# text -- that fallback exists so a real adjudication run degrades to
# UNPROVEN instead of crashing, which is the right behaviour THERE, but
# wrong here, where "no real recording" must mean "reject", not "compare
# against placeholder text"; (b) the Target-to-Before span was not bounded
# to its own "## Pair N" section, so a malformed document (a pair missing
# its own Before block) could let extraction cross into the NEXT pair's
# Target/Before instead of failing closed. Both are fixed below: presence
# in the real recordings is checked independently of what the judge
# returns, and extraction is scoped to one "## Pair" section at a time.
import re as _re  # noqa: E402 -- single-use, local to this one check


def _normalize_whitespace(text: str) -> str:
    return " ".join(_re.sub(r"\s+", " ", text).split()).strip()


def _load_real_recording_ids(replay_dir: Path) -> set[str]:
    """The set of finding_ids that have an ACTUAL entry in some `*.json`
    under `replay_dir` -- the same file-glob and `_`-prefix-skipping
    semantics run_adjudication.make_replay_judge's own loading step uses,
    kept as an independent presence check so this guard can tell "no
    recording exists for this finding_id" apart from make_replay_judge's
    own deliberate fail-open UNPROVEN response for a missing id (correct
    for letting an actual adjudication run continue past a gap, wrong for
    asserting a quote is genuinely verbatim against something real).
    """
    ids: set[str] = set()
    if replay_dir.is_dir():
        for _path in sorted(replay_dir.glob("*.json")):
            with _path.open("r", encoding="utf-8") as _handle:
                _data = json.load(_handle)
            if isinstance(_data, dict):
                ids.update(_k for _k in _data if not _k.startswith("_"))
    return ids


def _extract_before_pairs(markdown_text: str) -> list[tuple[str, str]]:
    """Return (finding_id, quoted_text) for every '## Pair N' section, in
    document order -- exactly one entry per heading found, ALWAYS, so a
    malformed section can never simply vanish from the result. Each section
    is bounded by the next '## Pair' heading (or the end of the document)
    BEFORE the Target/Before pattern is searched for, so a malformed section
    -- e.g. one missing its own 'Before' block -- can never have its Target
    line pair up with a LATER section's Before block; both must come from
    the SAME bounded section.

    A section review-found (Codex, on an earlier version of this fix) could
    otherwise be silently DROPPED rather than borrowed: if the surrounding
    document happened to carry exactly four other well-formed sections, a
    dropped fifth would still leave "found four" true, hiding the
    malformation instead of failing on it. So a section with no match
    inside its own bounds contributes an explicit sentinel pair,
    `("", "")`, rather than nothing -- it still counts toward the total,
    and its empty finding_id/quoted_text then fail the per-pair checks
    below on their own terms (finding_id "" is never a real recording;
    quoted_text "" is never a quote), so the malformation surfaces as a
    named FAIL rather than a missing count that might coincidentally still
    read as correct.

    finding_id comes from that section's own 'Target: `<finding_id>`' line;
    quoted_text is whatever sits inside the first/last double-quote of the
    joined, whitespace-normalized 'Before' blockquote.
    """
    section_heading_re = _re.compile(r"^## Pair \d+.*$", _re.MULTILINE)
    section_starts = [m.start() for m in section_heading_re.finditer(markdown_text)]
    section_bounds = list(zip(section_starts, section_starts[1:] + [len(markdown_text)]))

    pair_re = _re.compile(
        r"Target: `([0-9a-f]+)`[\s\S]*?"
        r"\*\*Before \(full adjudicator\.md\), the actual recorded verdict:\*\*\n\n"
        r"((?:> .*\n?)+)"
    )
    pairs: list[tuple[str, str]] = []
    for _start, _end in section_bounds:
        _section_match = pair_re.search(markdown_text, _start, _end)
        if _section_match is None:
            pairs.append(("", ""))
            continue
        _finding_id, _block = _section_match.group(1), _section_match.group(2)
        _joined = " ".join(line[2:] if line.startswith("> ") else line for line in _block.splitlines())
        _joined = _normalize_whitespace(_joined)
        _quote_match = _re.search(r'"(.*)"', _joined)
        pairs.append((_finding_id, _quote_match.group(1) if _quote_match else ""))
    return pairs


def _falsifiability_pair_ok(quoted_text: str, finding_id: str, judge, real_recording_ids: set[str]) -> bool:
    """True only when `finding_id` names an ACTUAL recording (never a
    missing one that merely got a fail-open placeholder response) and
    `quoted_text` is byte-verbatim (after whitespace normalization) against
    that ONE recording's verdict_evidence -- the one `judge` resolves for
    `finding_id` -- never against any other recording or a concatenation of
    several.
    """
    if not quoted_text or finding_id not in real_recording_ids:
        return False
    recorded = judge({"finding_id": finding_id}, {})
    target_evidence = recorded.get("verdict_evidence", "") if recorded else ""
    return _normalize_whitespace(quoted_text) == _normalize_whitespace(target_evidence)


_falsifiability_path = HERE / "fixtures" / "adjudication" / "recordings" / "FALSIFIABILITY.md"
_falsifiability_text = _falsifiability_path.read_text(encoding="utf-8")
_falsifiability_judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
_falsifiability_real_ids = _load_real_recording_ids(RECORDINGS_DIR)

_before_pairs = _extract_before_pairs(_falsifiability_text)
check(len(_before_pairs) == 4, f"FALSIFIABILITY.md names exactly four 'Before' blocks (found {len(_before_pairs)})")

for _index, (_finding_id, _quoted_text) in enumerate(_before_pairs, start=1):
    check(bool(_quoted_text), f"pair {_index}: the 'Before' block contains a quoted verdict_evidence")
    check(
        _finding_id in _falsifiability_real_ids,
        f"pair {_index}: the 'Before' block's Target ({_finding_id!r}) names an ACTUAL real recording",
    )
    check(
        _falsifiability_pair_ok(_quoted_text, _finding_id, _falsifiability_judge, _falsifiability_real_ids),
        f"pair {_index}: the 'Before' quote is byte-verbatim against its own target ({_finding_id!r})'s "
        "recorded verdict_evidence, not merely a substring of every recording concatenated",
    )

check(
    all(_falsifiability_pair_ok(_q, _f, _falsifiability_judge, _falsifiability_real_ids) for _f, _q in _before_pairs),
    "all four real FALSIFIABILITY.md pairs still validate against their own targets under the stricter "
    "per-target exact-equality check (issue #1412's fix does not regress the legitimate, already-correct case)",
)

# --- regression coverage for issue #1412's two named gaps -------------------
# Neither case below touches the real FALSIFIABILITY.md or any real
# recording file -- both feed hand-built quoted_text through the SAME
# _falsifiability_pair_ok/_falsifiability_judge used by the guard above,
# exactly this file's own established idiom (see e.g. the dedupe and
# downgrades checks further up: hand-built input fed straight to the real
# function under test, not a second, weaker stand-in).

# (1) A truncated quote: take a REAL target's verdict_evidence and drop its
# final clause. Under the pre-#1412 substring-of-the-concatenation check
# this was proven (during investigation) to still read as `in` the full
# corpus text; the byte-verbatim-per-target check must reject it.
_pair1_finding_id = "74046c6b01333e4b"  # Pair 1's target, line-anchored-findings.json
_pair1_real_evidence = _falsifiability_judge({"finding_id": _pair1_finding_id}, {})["verdict_evidence"]
_pair1_words = _pair1_real_evidence.split()
_truncated_quote = " ".join(_pair1_words[: len(_pair1_words) - 12])
check(
    len(_truncated_quote) < len(_pair1_real_evidence),
    "the truncated-quote fixture below is actually shorter than the real evidence (sanity check on the test itself)",
)
check(
    not _falsifiability_pair_ok(_truncated_quote, _pair1_finding_id, _falsifiability_judge, _falsifiability_real_ids),
    "issue #1412 gap 1: a truncated 'Before' quote (final clause dropped) is REJECTED by the "
    "byte-verbatim-per-target check, where the old substring-of-the-concatenation check let it pass",
)

# (2) A cross-recording boundary quote: fabricate a string from the tail of
# one real recording's evidence plus the head of a DIFFERENT real
# recording's evidence. Under the pre-#1412 check, joining every recording
# into one search haystack made this construction read as `in` the full
# corpus text even though it is absent from either recording alone; the
# byte-verbatim-per-target check, which never builds that haystack, must
# reject it against its own declared target.
_boundary_target_id = "0d4a625fa2227bcc"  # pr-anchored-finding.json
_boundary_other_id = "f699b70a97ebb6e5"  # pr-anchored-finding.json, a DIFFERENT finding
_boundary_target_evidence = _falsifiability_judge({"finding_id": _boundary_target_id}, {})["verdict_evidence"]
_boundary_other_evidence = _falsifiability_judge({"finding_id": _boundary_other_id}, {})["verdict_evidence"]
_boundary_crossing_quote = (
    _normalize_whitespace(_boundary_target_evidence)[-40:] + " " + _normalize_whitespace(_boundary_other_evidence)[:40]
)
check(
    _boundary_crossing_quote not in _boundary_target_evidence,
    "the boundary-crossing fixture below is actually absent from its declared target's own evidence "
    "(sanity check on the test itself)",
)
check(
    not _falsifiability_pair_ok(
        _boundary_crossing_quote, _boundary_target_id, _falsifiability_judge, _falsifiability_real_ids
    ),
    "issue #1412 gap 2: a quote fabricated from the tail of one recording's evidence and the head of a "
    "DIFFERENT recording's evidence is REJECTED against its declared target, where matching against the "
    "concatenation of every recording could have masked exactly this boundary-crossing case",
)

# --- cross-vendor review coverage (Codex, on the first version of this fix) -
# Both cases below were found by an independent Codex review of the first
# version of this fix and are fail-open gaps THAT version of
# _falsifiability_pair_ok/_extract_before_pairs did not catch, distinct from
# issue #1412's own two named gaps above.

# (3) An unknown finding_id must never "pass" merely because the quote
# happens to equal make_replay_judge's own synthetic "no recorded judge
# output for finding_id ..." fallback text -- that fallback exists so a
# real adjudication run degrades to UNPROVEN past a missing recording
# instead of crashing, which says nothing about whether a quote is
# genuinely verbatim against something real.
_missing_finding_id = "deadbeefdeadbeef"
check(
    _missing_finding_id not in _falsifiability_real_ids,
    "the missing-target fixture below actually names a finding_id absent from every real recording "
    "(sanity check on the test itself)",
)
_missing_target_synthetic_evidence = _falsifiability_judge({"finding_id": _missing_finding_id}, {})[
    "verdict_evidence"
]
check(
    not _falsifiability_pair_ok(
        _missing_target_synthetic_evidence, _missing_finding_id, _falsifiability_judge, _falsifiability_real_ids
    ),
    "a quote equal to make_replay_judge's own synthetic 'no recording' fallback text is REJECTED when its "
    "declared target names no real recording at all, not accepted as if that fallback were real evidence",
)

# (4) Target/Before extraction must not cross a '## Pair' section boundary:
# a malformed document where one pair is missing its own 'Before' block
# must not let its Target line pair up with the NEXT pair's Before block.
### The quote-extraction regex (r'"(.*)"', greedy) matches from the FIRST to
# the LAST double-quote on the joined line, so the "Before" text needs to be
# wrapped in its own explicit outer quotes here -- the same shape every real
# entry in FALSIFIABILITY.md uses (`CONFIRMED. "..."`) -- not left bare, or
# the internal quote marks already present inside real evidence text (e.g.
# `action="store_true"`) would be mistaken for the outer pair instead.
_malformed_falsifiability_text = (
    "## Pair 1 — malformed, no Before block at all\n\n"
    f"Target: `{_pair1_finding_id}`\n\n"
    "(no Before block here on purpose)\n\n"
    "---\n\n"
    "## Pair 2 — a real pair, quoted so its own Before block is unambiguous\n\n"
    f"Target: `{_boundary_target_id}`\n\n"
    "**Before (full adjudicator.md), the actual recorded verdict:**\n\n"
    f'> CONFIRMED. "{_boundary_target_evidence}"\n'
)
_malformed_pairs = _extract_before_pairs(_malformed_falsifiability_text)
check(
    _pair1_finding_id not in {_fid for _fid, _ in _malformed_pairs},
    "a '## Pair' section with no Before block of its own never pairs its own Target with a LATER "
    f"section's Before block (extracted: {_malformed_pairs})",
)
check(
    _malformed_pairs == [("", ""), (_boundary_target_id, _boundary_target_evidence)],
    "the malformed Pair 1 section yields an explicit empty sentinel (not silently dropped) and the "
    f"well-formed Pair 2 section is still extracted correctly alongside it (got {_malformed_pairs})",
)
check(
    not _falsifiability_pair_ok("", "", _falsifiability_judge, _falsifiability_real_ids),
    "the empty sentinel for a malformed section never validates as a genuine match",
)

# (5) A first version of THIS fix (cross-vendor review found this too, same
# round) bounded extraction to '## Pair' sections but silently DROPPED a
# section with no match inside its own bounds, rather than counting it --
# so a document with one malformed section plus exactly four well-formed
# ones still extracted to exactly four pairs, and the "exactly four"
# top-level check read that as fine. Reproduced here directly: a
# five-heading document (Pair 1 malformed, Pairs 2-5 each a REAL target)
# must extract to five entries, not four, so the malformation cannot hide
# behind a coincidentally-matching count.
_five_heading_text = (
    "## Pair 1 — malformed, no Before block at all\n\n"
    f"Target: `{_pair1_finding_id}`\n\n"
    "(no Before block here on purpose)\n\n"
    "---\n\n"
)
for _n, _fid in enumerate(
    ["74046c6b01333e4b", "0d4a625fa2227bcc", "1c947d53116f5737", "f699b70a97ebb6e5"], start=2
):
    _evidence = _falsifiability_judge({"finding_id": _fid}, {})["verdict_evidence"]
    _five_heading_text += (
        f"## Pair {_n} — a real, well-formed pair\n\n"
        f"Target: `{_fid}`\n\n"
        "**Before (full adjudicator.md), the actual recorded verdict:**\n\n"
        f'> CONFIRMED. "{_evidence}"\n\n'
        "---\n\n"
    )
_five_heading_pairs = _extract_before_pairs(_five_heading_text)
check(
    len(_five_heading_pairs) == 5,
    "a five-'## Pair'-heading document (one malformed, four real) extracts to FIVE entries, not four -- "
    f"the malformed section cannot hide behind an otherwise-matching count (got {len(_five_heading_pairs)})",
)

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)

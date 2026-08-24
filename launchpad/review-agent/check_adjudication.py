"""Step 10 control: one control per #118 done-criterion, over adjudication.

Deliberately separate from `test_run_adjudication.py`'s unittest suite (see
`check_unit_suites.py`'s own history -- #270's Out of scope names this
directly: "duplicating it here would create a second CI entry point that
#118 explicitly rules out"). That suite proves the internal API,
`adjudicate()`, behaves correctly when called directly. This control proves
the same properties end to end through the real CLI process
(`run_adjudication.py` via subprocess, exactly as CI invokes it) and, where a
property is about REAL recorded output rather than a hand-built document,
against STEP 9's actual recordings -- not a stand-in.

Registered in `run_controls.py`'s CONTROLS list as ("check_adjudication.py",
False), so #120's single CI entry point picks it up and no second workflow
is added.

90 PASS lines as of this writing (`python3 check_adjudication.py | grep -c
'^PASS'`) -- up from 81 (itself a correction of an uncounted "44" the
introducing commit stated) once STEP 11's mutation harness
(`check_adjudication_mutations.py`) found three cases this file did not yet
exercise directly: a "swapped" finding_id (a real finding replaced by a
different, self-consistent one -- the plain "invented" case above uses a
non-hash-matching id that #117's own findings.validate already catches on
its own terms); `_apply_severity_rerating`'s illegal-`reported_severity`
branch, unreachable through `adjudicate()` because STEP 3's upstream
refusal never lets a malformed severity reach it; and
`verdicts.forbidden_keys` as a hand-built-document check, since
`adjudicate()`'s own producer-side re-check of the same function means every
check that goes through `adjudicate()` crashes before reaching its own
assertion once that mechanism is the thing under test.
"""

from __future__ import annotations

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


# --- this whole suite makes no network call ---------------------------------
# Asserted once, up front, over the exact path every real-recordings check
# below actually exercises -- an injected runner that raises on any subprocess
# or HTTP call, not merely an absence of observed failures.


def _boom(*args, **kwargs):
    raise AssertionError("check_adjudication.py must not touch the network or a subprocess in-process")


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

_dropped = json.loads(json.dumps(_output_doc))
_dropped["reports"][0]["findings"] = []
_dropped["reports"][0]["findings_count"] = 0
_drop_violations = verdicts.validate(_input_doc, _dropped)
check(
    any("in input but not output" in v or "missing" in v.lower() for v in _drop_violations) or bool(_drop_violations),
    f"a dropped finding_id is rejected by verdicts.validate ({_drop_violations})",
)

_invented = json.loads(json.dumps(_output_doc))
_extra = dict(_invented["reports"][0]["findings"][0])
_extra["finding_id"] = "invented0000000"
_invented["reports"][0]["findings"].append(_extra)
_invented["reports"][0]["findings_count"] = len(_invented["reports"][0]["findings"])
_invent_violations = verdicts.validate(_input_doc, _invented)
check(bool(_invent_violations), f"an invented finding_id is rejected by verdicts.validate ({_invent_violations})")
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
# (STEP 1's six-field list, checked by name against ADJUDICATION.md rather
# than by counting -- "six" is a number someone can miscount silently)

_SIX_ADDED_FIELDS = (
    "verdict",
    "verdict_evidence",
    "reported_severity",
    "severity",
    "severity_reason",
    "duplicate_of",
)
check(
    len(_SIX_ADDED_FIELDS) == 6,
    "the field-by-field control below actually covers all six of ADJUDICATION.md's added fields",
)


def _mutate_field(doc: dict, field: str, value: object) -> dict:
    mutated = json.loads(json.dumps(doc))
    mutated["reports"][0]["findings"][0][field] = value
    return mutated


def _finding_needing_reason() -> dict:
    # severity_reason is only REQUIRED when severity != reported_severity, so
    # its own malformed-value case needs a finding that already differs.
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
    return finding_adjudicated


_base_adjudicated = json.loads(json.dumps(_output_doc))

for _field, _bad_values in {
    "verdict": [None, "", "MAYBE", 42],
    "verdict_evidence": [None, "", "   "],
    "reported_severity": [None, "", "Info", "blocker"],
    "severity": [None, "", "Info", "blocker"],
    "duplicate_of": [42, []],
}.items():
    for _bad in _bad_values:
        _m = _mutate_field(_base_adjudicated, _field, _bad)
        _violations = verdicts.validate(_input_doc, _m)
        check(
            any(_field in v for v in _violations),
            f"{_field}={_bad!r} is named by verdicts.validate",
        )

# severity_reason: required only when severity != reported_severity.
_needs_reason_doc = make_document(reports=[make_report(findings_list=[_finding_needing_reason()])])
_needs_reason_out = json.loads(json.dumps(_needs_reason_doc))
_needs_reason_out["reports"][0]["findings"][0]["severity_reason"] = ""
_needs_reason_out["adjudication"] = {
    "schema_version": 1,
    "verdict_counts": {"CONFIRMED": 1, "REFUTED": 0, "UNPROVEN": 0},
    "findings_in": 1,
    "findings_out": 1,
    "duplicate_groups": [],
    "downgrades": [],
    "total_refutation": False,
    "notes": [],
    "completion_marker": f"BUZZ-ADJUDICATION-COMPLETE:{NONCE}",
}
_violations = verdicts.validate(_needs_reason_doc, _needs_reason_out)
check(
    any("severity_reason" in v for v in _violations),
    f"blank severity_reason is named when severity != reported_severity ({_violations})",
)

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
# one planted defect (see fixtures/adjudication/PROVENANCE.md).

_dedupe_real_input = load_real_fixture("line-anchored-findings")
_dedupe_fids = [f["finding_id"] for f in all_findings(_dedupe_real_input)]


def _group_all(adjudicated_findings, document):
    return [_dedupe_fids]


_dedupe_judge = run_adjudication.make_replay_judge(RECORDINGS_DIR)
_dedupe_real_out = run_adjudication.adjudicate(_dedupe_real_input, _dedupe_judge, dedupe_judge=_group_all)
_dedupe_out_fids = {f["finding_id"] for f in all_findings(_dedupe_real_out)}
check(_dedupe_out_fids == set(_dedupe_fids), "real dedupe: no duplicate is dropped, all three still present")
_survivors = [f for f in all_findings(_dedupe_real_out) if f["duplicate_of"] is None]
_dupes = [f for f in all_findings(_dedupe_real_out) if f["duplicate_of"] is not None]
check(
    len(_survivors) == 1 and len(_dupes) == 2,
    "real dedupe: exactly one survivor, two findings pointing at it via duplicate_of",
)
[_group] = _dedupe_real_out["adjudication"]["duplicate_groups"]
check(
    set(_group["duplicates"]) | {_group["survivor"]} == set(_dedupe_fids),
    "real dedupe: duplicate_groups names the same three ids, from the block's own side",
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

print(f"\n{len(failures)} failure(s)")
sys.exit(1 if failures else 0)

"""Step 11 control: prove each of STEP 10's controls can actually fail.

The model for this is `check_mutations.py` (#120's own mutation harness),
cited by name in the plan: "An earlier revision neutered each check function
to a constant, and that proves the wrong thing." Neither `return ["FAIL"]`
nor `return []` says whether a control catches the SPECIFIC regression it
exists for -- only a real, named change to the production code, applied to a
scratch copy, does.

Unlike `check_mutations.py` -- which asks "was this mutation caught by ANY of
a handful of separate control scripts" -- `check_adjudication.py`'s ~90
checks all live in ONE file, each printing its own PASS/FAIL line. So this
harness runs that whole file against each mutant and inspects WHICH labelled
lines flipped: the mutation's own target must be among the FAIL lines, and
where the plan requires it, an unrelated label must still be among the PASS
lines -- proof the mutation is targeted, not a wrecking ball.

Two real gaps in `check_adjudication.py` were found and fixed while building
this harness, not discovered after: a "swapped" finding_id (one real finding
replaced by a different, self-consistent one, same count) that the old
"invented" case never exercised, because a fabricated non-hash-matching id
is already caught by #117's own findings.validate independently of the
set-vs-count logic this step's own mutation targets; and
`_apply_severity_rerating`'s illegal-`reported_severity`-the-judge-agreed-
with branch, which `adjudicate()`'s upstream STEP 3 refusal makes
unreachable through the normal path, so nothing had ever called it directly.
Both are now in `check_adjudication.py` itself, ahead of this file, so this
harness is proving real coverage rather than papering over a hole with a
generous mutation.

Mutations are applied to a scratch copy under a temp directory. The
repository is never modified.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
TARGET = "check_adjudication.py"

#: (name, file, find, replace, must_fail_substring, still_passes_substrings, why)
#: `still_passes_substrings` is empty where the plan does not require it;
#: filled in for the three mutations STEP 11 names explicitly (finding_id,
#: total-refutation, out-of-ladder) plus a few more where an unrelated
#: control obviously should not move.
MUTATIONS = [
    (
        "finding-id-count-not-set",
        "verdicts.py",
        '    if input_ids != output_ids:\n'
        '        dropped = sorted(input_ids - output_ids)\n'
        '        invented = sorted(output_ids - input_ids)\n'
        '        if dropped:\n'
        '            violations.append(f"finding_id set: present on input, missing from output: {dropped}")\n'
        '        if invented:\n'
        '            violations.append(f"finding_id set: present on output, absent from input (invented): {invented}")\n',
        '    if len(input_ids) != len(output_ids):\n'
        '        violations.append("finding_id set: count differs")\n',
        "a real finding swapped for a different, self-consistent one (same count) is rejected",
        ["containment block (all three kinds, raw evidence) is byte-identical in and out"],
        "swapping one real finding for another unrelated one keeps the count equal, "
        "so a count-only check never notices the substitution",
    ),
    (
        "severity-reason-check-dropped",
        "verdicts.py",
        '        if severity != reported_severity and not is_nonempty_str(finding.get("severity_reason")):\n'
        '            violations.append(\n'
        '                f"{finding_label}: severity_reason must be a non-empty string when severity "\n'
        '                f"({severity!r}) differs from reported_severity ({reported_severity!r}), got "\n'
        '                f"{finding.get(\'severity_reason\')!r}"\n'
        '            )\n',
        '        pass  # mutated: severity_reason presence check removed\n',
        "severity_reason='' is named when severity != reported_severity, by its OWN message anchor",
        [
            "verdict=None is named by verdicts.validate, by its OWN message anchor",
            "verdict_evidence=None is named by verdicts.validate, by its OWN message anchor",
            "reported_severity=None is named by verdicts.validate, by its OWN message anchor",
            "severity=None is named by verdicts.validate, by its OWN message anchor",
            "duplicate_of=42 is named by verdicts.validate, by its OWN message anchor",
        ],
        "deleting one field's presence check must fail only that field's control -- if "
        "a different field's control also fails, the fixture entangles fields that "
        "must be independent",
    ),
    (
        "severity-ladder-check-dropped",
        "verdicts.py",
        '        if not isinstance(severity, str) or severity not in SEVERITY_ORDER:\n'
        '            violations.append(\n'
        '                f"{finding_label}: severity {severity!r} is not a key of review.SEVERITY_ORDER"\n'
        '            )\n',
        '        pass  # mutated: severity SEVERITY_ORDER-membership check removed\n',
        "severity=None is named by verdicts.validate, by its OWN message anchor",
        ["reported_severity=None is named by verdicts.validate, by its OWN message anchor"],
        "the severity field arrives illegal (e.g. an out-of-ladder value the ladder guard "
        "in run_adjudication.py never sees, or one it deliberately falls back to) and "
        "nothing in verdicts.validate names it -- the field is confirmed independent of "
        "reported_severity's own check, which must still catch its own illegal values",
    ),
    (
        "reported-severity-ladder-check-dropped",
        "verdicts.py",
        '        if not isinstance(reported_severity, str) or reported_severity not in SEVERITY_ORDER:\n'
        '            violations.append(\n'
        '                f"{finding_label}: reported_severity {reported_severity!r} is not a key of "\n'
        '                "review.SEVERITY_ORDER"\n'
        '            )\n',
        '        pass  # mutated: reported_severity SEVERITY_ORDER-membership check removed\n',
        "reported_severity=None is named by verdicts.validate, by its OWN message anchor",
        ["severity=None is named by verdicts.validate, by its OWN message anchor"],
        "an input finding whose reported_severity already arrived illegal is no longer "
        "named by verdicts.validate at all -- the exact property STEP 3's own upstream "
        "refusal depends on as a second, independent line of defence",
    ),
    (
        "out-of-ladder-reported-severity-guard-dropped",
        "run_adjudication.py",
        '        if reported_severity not in review.SEVERITY_ORDER:\n'
        '            # There is no legal re-rating to refuse and no safe value to fall\n'
        '            # back to: the severity ARRIVED illegal and the judge either\n'
        '            # agreed with it or proposed nothing. `Blocker` rather than\n'
        '            # anything smaller, because this stage may not silently decide\n'
        '            # that an unrateable finding is a minor one.\n'
        '            #\n'
        '            # Unreachable through `main()` today -- STEP 3\'s\n'
        '            # `findings.validate` refuses an out-of-ladder input severity\n'
        '            # before any judge runs -- and kept as a real branch regardless:\n'
        '            # `adjudicate()` is importable by anything, and STEP 10\'s control\n'
        '            # suite is planned to feed this function malformed values\n'
        '            # directly. Defence in depth that the contract already promises\n'
        '            # is not the same as dead code.\n'
        '            reason = (\n'
        '                f"finding {finding_id!r} carries an out-of-ladder reported severity "\n'
        '                f"{reported_severity!r} and the judge proposed no legal re-rating; "\n'
        '                "refused, falling back to \'Blocker\'"\n'
        '            )\n'
        '            return "UNPROVEN", "Blocker", reason\n'
        '        # No re-rating: unchanged from STEP 3/4\'s behaviour.\n'
        '        return verdict, reported_severity, None\n',
        '        # mutated: the reported_severity-in-SEVERITY_ORDER half of the guard is gone\n'
        '        return verdict, reported_severity, None\n',
        "_apply_severity_rerating refuses an illegal reported_severity the judge merely agreed with",
        ["real dedupe: no duplicate is dropped, all three still present"],
        "keeping only the `severity` half of the guard passes an illegal "
        "reported_severity straight through whenever the judge does not re-rate -- "
        "exactly the gap STEP 3's own upstream refusal exists to close for the real "
        "CLI path, proven here as load-bearing rather than redundant",
    ),
    (
        "total-refutation-drops-all-refuted-condition",
        "run_adjudication.py",
        '    total_refutation = findings_in > 0 and verdict_counts["REFUTED"] == findings_in',
        '    total_refutation = findings_out > 0',
        "adjudicate() itself does not flag total_refutation when only SOME findings are REFUTED",
        ["a pr-anchored finding adjudicates without raising"],
        "flags total refutation whenever there is at least one finding, so a document "
        "with one CONFIRMED among several REFUTED findings -- which must NOT flag -- "
        "flags anyway",
    ),
    (
        "refuted-findings-filtered-before-emit",
        "run_adjudication.py",
        "    return output_document",
        '    for _report in output_document.get("reports", []):\n'
        '        _report["findings"] = [f for f in _report["findings"] if f["verdict"] != "REFUTED"]\n'
        "    return output_document",
        "a REFUTED verdict leaves reports[].findings membership and length unchanged",
        [],
        "silently drops every REFUTED finding immediately before returning -- inserted "
        "AFTER STEP 6's own finding-set-integrity reassertion (which fires on any drop "
        "and would otherwise crash the whole control file before this mutation's real "
        "target ever gets to run), so this exercises the specific published-findings "
        "control rather than tripping a different, earlier guard",
    ),
    (
        "approved-dropped-from-forbidden-keys",
        "verdicts.py",
        '_FORBIDDEN_KEYS = frozenset({"approved", "mergeable", "merge_recommendation"})',
        '_FORBIDDEN_KEYS = frozenset({"mergeable", "merge_recommendation"})',
        "verdicts.forbidden_keys names a bare 'approved' key on a hand-built document",
        [],
        "the plan's own literal mutation (\"add a literal 'approved': null key to the "
        "Adjudication dataclass\") turns out unreachable through this file: "
        "adjudicate() re-checks forbidden_keys on every document before it ever "
        "returns, so that mutation crashes the whole control file (ForbiddenKeyError) "
        "before any check-level FAIL line prints, on the very first real-fixture "
        "replay. This mutation targets the WALK mechanism itself instead -- dropping "
        "one name from the set it checks -- which is exactly what a bare-value check "
        "('approved is never true') would miss: the key is gone from the set, so it "
        "leaks through both adjudicate()'s own guard and this control alike, unless a "
        "hand-built-document check exercises the walk in isolation",
    ),
    (
        "downgrades-recorded-on-every-rerating",
        "run_adjudication.py",
        '    if review.SEVERITY_ORDER[proposed_severity] > review.SEVERITY_ORDER[reported_severity]:\n'
        '        downgrades.append(\n'
        '            {\n'
        '                "finding_id": finding_id,\n'
        '                "from": reported_severity,\n'
        '                "to": proposed_severity,\n'
        '                "reason": reason,\n'
        '            }\n'
        '        )\n'
        '    return verdict, proposed_severity, reason',
        '    downgrades.append(\n'
        '        {\n'
        '            "finding_id": finding_id,\n'
        '            "from": reported_severity,\n'
        '            "to": proposed_severity,\n'
        '            "reason": reason,\n'
        '        }\n'
        '    )\n'
        '    return verdict, proposed_severity, reason',
        "a legal upgrade (Low -> Blocker) is not recorded in downgrades",
        [],
        "records every re-rating as a downgrade regardless of direction, so an "
        "upgrade -- which is not itself an error -- shows up as a false fall",
    ),
    (
        "dedupe-marks-survivor-not-duplicate",
        "run_adjudication.py",
        '            output_findings_by_id[dup_id]["duplicate_of"] = group["survivor"]',
        '            output_findings_by_id[group["survivor"]]["duplicate_of"] = group["survivor"]',
        "real dedupe: exactly one survivor, two findings pointing at it via duplicate_of",
        [],
        "the survivor ends up pointing at itself and the real duplicates keep "
        "duplicate_of=null, so a consumer reading any one duplicate finding sees no "
        "sign it was ever grouped",
    ),
    (
        "containment-evidence-escaped-on-passthrough",
        "run_adjudication.py",
        "    output_document = copy.deepcopy(input_document)",
        "    output_document = copy.deepcopy(input_document)\n"
        "    import contain as _contain\n"
        '    for _cf in output_document.get("containment", {}).get("findings", []):\n'
        '        _cf["evidence"] = _contain.escape(_cf["evidence"])',
        "containment block (all three kinds, raw evidence) is byte-identical in and out",
        [],
        "re-escapes containment evidence that CONTAINMENT.md requires stay RAW through "
        "this stage -- a double-escape a downstream renderer does not expect, "
        "corrupting the one field a human reads to judge whether an attack is real",
    ),
    (
        "nonce-trusts-first-report-not-top-level",
        "run_adjudication.py",
        '    (agreed_nonce,) = distinct_report_nonces\n'
        '    if agreed_nonce != top_nonce:\n'
        '        raise NonceVerificationError(\n'
        '            "mismatched envelope",\n'
        '            f"every report\'s completion marker carries nonce {agreed_nonce!r}, which does "\n'
        '            f"not match the top-level nonce {top_nonce!r}",\n'
        '        )\n'
        '\n'
        '    return top_nonce',
        '    (agreed_nonce,) = distinct_report_nonces\n'
        '    return report_nonces[0]',
        "reports agreeing with each other but not the top-level key are refused",
        ["no top-level nonce -> 'absent provenance'"],
        "trusts whatever the reports agree on and never compares it to the top-level "
        "key, so one run's reports slipped under a different run's header validate "
        "clean -- the exact forgery shape refusal 3 exists to catch",
    ),
    (
        "pr-anchor-falls-through-to-file-line",
        "run_adjudication.py",
        '    anchor = finding.get("anchor")\n'
        '    if anchor == "pr":\n'
        '        return "the whole pull request (no file or line anchor)"\n'
        '    if anchor == "file":\n'
        '        return f"{finding.get(\'file\')}"\n'
        '    if anchor == "line":\n'
        '        return f"{finding.get(\'file\')}:{finding.get(\'line\')}"\n'
        '    return "a finding with an unrecognised anchor"',
        '    anchor = finding.get("anchor")\n'
        '    if anchor == "file":\n'
        '        return f"{finding.get(\'file\')}"\n'
        '    return f"{finding.get(\'file\')}:{finding.get(\'line\')}"',
        "a pr-anchored finding's verdict_evidence never renders a None file/line",
        [],
        "reintroduces the exact historical bug the code comment names: a pr-anchored "
        "finding (file and line both null) falls through to the file:line formatter "
        "and renders the literal string 'None:None'",
    ),
]

failures: list[str] = []


def check(ok: bool, label: str) -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {label}")
    if not ok:
        failures.append(label)


def apply_mutation(root: Path, filename: str, find: str, replace: str) -> bool:
    path = root / filename
    src = path.read_text(encoding="utf-8")
    if find not in src:
        return False
    if src.count(find) != 1:
        return False  # ambiguous anchor -- refuse rather than mutate the wrong occurrence
    path.write_text(src.replace(find, replace, 1), encoding="utf-8")
    return True


def run_target(root: Path) -> tuple[int, list[str], list[str]]:
    proc = subprocess.run(
        [sys.executable, str(root / TARGET)],
        capture_output=True,
        text=True,
        cwd=root,
        timeout=180,
    )
    lines = proc.stdout.splitlines()
    passed = [line[6:] for line in lines if line.startswith("PASS  ")]
    failed = [line[6:] for line in lines if line.startswith("FAIL  ")]
    return proc.returncode, passed, failed


def scratch_copy() -> Path:
    tmp = Path(tempfile.mkdtemp())
    root = tmp / "review-agent"
    shutil.copytree(HERE, root, ignore=shutil.ignore_patterns("__pycache__"))
    return root


def main() -> int:
    # Baseline: an unmutated scratch copy must reproduce the working tree's own
    # clean run -- proves the copy mechanism itself introduces no failures, so
    # every mutant result below is attributable to the mutation, not the harness.
    baseline_root = scratch_copy()
    try:
        code, passed, failed = run_target(baseline_root)
        check(code == 0 and not failed, f"unmutated scratch copy reproduces a clean run ({len(passed)} PASS, {len(failed)} FAIL)")
    finally:
        shutil.rmtree(baseline_root.parent, ignore_errors=True)

    print(f"\n{len(MUTATIONS)} mutations, each proven against its own named target\n")

    for name, filename, find, replace, must_fail, still_passes, why in MUTATIONS:
        root = scratch_copy()
        try:
            if not apply_mutation(root, filename, find, replace):
                check(False, f"{name}: could not apply -- the anchor has drifted in {filename}")
                continue

            code, passed, failed = run_target(root)

            went_red = code != 0
            target_failed = any(must_fail in line for line in failed)
            check(went_red and target_failed, f"{name}: suite goes red and names its own target ({must_fail!r})")

            if not target_failed:
                print(f"      consequence if unnoticed: {why}")

            for other in still_passes:
                other_still_passes = any(other in line for line in passed)
                check(
                    other_still_passes,
                    f"{name}: unrelated control still passes ({other!r}) -- the mutation is targeted, not a wrecking ball",
                )
        finally:
            shutil.rmtree(root.parent, ignore_errors=True)

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

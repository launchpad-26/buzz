#!/usr/bin/env python3
"""T1/T2 reference-integrity guards for #2311 and #2312.

No pytest fixtures: every test remains runnable by ``tests/run_all.py``.  The fixture
package is generated in a temporary directory so each supported static-reference shape
is tested independently of RQA's current implementation.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile

_SKILL_ROOT = pathlib.Path(__file__).resolve().parent.parent
_TEST_ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(_SKILL_ROOT / "integrity"))

from reference_analysis import ReferenceAnalysis, format_findings  # noqa: E402

RQA = _SKILL_ROOT / "rqa"

# Exact, intentional non-production surfaces allowed by #2311. New findings fail,
# and stale exceptions fail, so this cannot grow silently.
T1_JUSTIFIED_EXCEPTIONS = {
    "rqa.authority.GateError": "P-08's documented public programming-error vocabulary; production raises and catches it inside the authority part",
    "rqa.authority.grant": "E-04 itself (`EDGES[\"E-04\"]`, CONTRACTS.md §9): P-08's published entry point for a caller that does not hold the managed-repository set. The composition root does hold it, so production injects a bound `Gate.grant` — the same code path this function constructs",
    "rqa.cli.main": "external process entry point reached by `python -m rqa.cli` through the package's __main__ module",
    "rqa.github.AdapterError": "P-09's documented public adapter programming error; GitHub write implementations consume it inside the part",
    "rqa.github.MutationKind": "P-09's documented adapter discriminator for callers and fixture transports; mutation dispatch remains inside the part",
    "rqa.github.PASSING": "P-09 intentionally republishes the shared conclusion taxonomy for adapter consumers; production classification is internal",
    "rqa.github.UNSETTLED": "P-09 intentionally republishes the shared conclusion taxonomy for adapter consumers; production classification is internal",
    "rqa.harness.HarnessAdapter": "P-06's public adapter-extension contract; built-in adapters are selected and invoked inside the harness part",
    "rqa.harness.HarnessError": "P-06's public programming-error contract; production raises and handles it within the harness boundary",
    "rqa.intake.AdmissionRefusal": "P-01's public result vocabulary retained for typed callers and alternate composition roots",
    "rqa.intake.IntakeError": "P-01's public programming-error contract; production propagation starts inside the intake part",
    "rqa.intake.JobFailure": "P-01's public per-job failure value carried in TickResult for external callers",
    "rqa.intake.JobStore": "P-01's public injected-store Protocol for alternate composition roots",
    "rqa.intake.LeaseRow": "P-01's public store-row vocabulary for alternate stores and diagnostics",
    "rqa.intake.LeaseStore": "P-01's public injected-store Protocol for alternate composition roots",
    "rqa.intake.PrFactsRow": "P-01's public store-row vocabulary for alternate stores and diagnostics",
    "rqa.intake.PrFactsStore": "P-01's public injected-store Protocol for alternate composition roots",
    "rqa.intake.TickResult": "E-21's public scheduler result contract; the CLI renders it without naming the type",
    "rqa.intake.job_id": "P-01's public deterministic identity helper for ingestion and migration tooling",
    "rqa.judgement.JudgementError": "P-07's public programming-error contract; judgement raises it within its own boundary",
    "rqa.judgement.render": "P-07's documented pure rendering seam for independent judgement consumers",
    "rqa.lifecycle.DISPOSITION": "P-02's public state-to-disposition contract retained for status consumers and conformance checks",
    "rqa.lifecycle.Disposition": "P-02's public status vocabulary retained for typed integration consumers",
    "rqa.lifecycle.IllegalTransitionError": "P-02's public transition-error subtype; production raises it inside the lifecycle part",
    "rqa.lifecycle.StaleDecisionError": "P-02's public resume-error subtype; production raises it inside the lifecycle part",
    "rqa.lifecycle.StatusReport": "E-17's public status result type; the CLI renders it without naming the class",
    "rqa.lifecycle.TRANSITIONS": "P-02's published finite-state contract retained for conformance and external inspection",
    "rqa.lifecycle.UnknownJobError": "P-02's public transition-error subtype; production raises it inside the lifecycle part",
    "rqa.lifecycle.transition": "P-02's documented state-transition seam for alternate lifecycle compositions",
    "rqa.policy.OnboardRefusalReason": "E-17's public structured onboarding-refusal vocabulary",
    "rqa.policy.OnboardResult": "E-17's public onboarding result union for typed callers",
    "rqa.policy.PolicyError": "P-03's public programming-error contract; production raises it inside the policy part",
    "rqa.policy.SnapshotStoreCorrupted": "P-03's public fail-closed store error for alternate composition roots",
    "rqa.policy.Written": "E-17's public successful onboarding result value",
    "rqa.protocol.HarnessIdentity": "P-04's published protocol-schema type for independently implemented harnesses",
    "rqa.protocol.ProtocolError": "P-04's public protocol programming-error contract; validation raises it inside the part",
    "rqa.protocol.SUBSTANTIVE_GROUP": "P-04's published category taxonomy for harness and protocol implementers",
    "rqa.protocol.extract": "published E-19 nonce-envelope decoder for independently implemented review harnesses",
    "rqa.record.AmbiguousHead": "P-12's public offline-resolution result vocabulary",
    "rqa.record.AnchorResult": "P-12's public anchoring result contract for operator integrations",
    "rqa.record.BreakKind": "P-12's public verification-break taxonomy for diagnostic consumers",
    "rqa.record.ENTRY_KINDS": "P-12 intentionally republishes the shared closed entry-kind contract",
    "rqa.record.Explanation": "AC06's public reconstructed-explanation value returned to operator integrations",
    "rqa.record.LegacySource": "P-12's retained one-time legacy-migration Protocol",
    "rqa.record.MigrationSummary": "P-12's retained one-time legacy-migration result",
    "rqa.record.MigrationTableResult": "P-12's retained one-time per-table migration result",
    "rqa.record.NoRecord": "P-12's public offline-resolution result vocabulary",
    "rqa.record.PayloadNotSerializable": "P-12's public canonicalisation failure contract",
    "rqa.record.RecordProgrammingError": "P-12's public record programming-error base class",
    "rqa.record.ResolvedJob": "P-12's public offline-resolution result vocabulary",
    "rqa.record.UnknownEntryKind": "P-12's public closed-kind programming error",
    "rqa.record.VerifyResult": "P-12's public verification result for offline diagnostic consumers",
    "rqa.record.migrate_legacy": "explicit one-time P-12 migration seam retained across the #2188 cutover boundary",
    "rqa.record.resolve_job": "P-12's public offline job-resolution seam for diagnostic consumers",
    "rqa.record.verify": "public offline P-12 integrity-verification seam for operator and diagnostic integrations",
    "rqa.remediation.RemediationError": "P-10's public programming-error contract; production raises it inside the remediation part",
    "rqa.remediation.ToolSpec": "P-10's public deterministic tool-description type for policy and extension authors",
    "rqa.reuse.Reason": "P-13's public reuse-refusal taxonomy for diagnostics and alternate callers",
    "rqa.reuse.ReuseError": "P-13's public programming-error contract; production raises it inside the reuse part",
}


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture_analysis(
    *, remove_direct_wiring: bool = False, add_internal_wiring: bool = False
) -> ReferenceAnalysis:
    temporary = tempfile.TemporaryDirectory()
    # Keep the directory alive for the duration of analysis; every source is parsed
    # eagerly by the constructor.
    root = pathlib.Path(temporary.name)
    production = root / "sample"
    tests = root / "tests"
    _write(production / "__init__.py", "")
    _write(
        production / "part" / "__init__.py",
        "from sample.part.api import (\n"
        "    AliasTarget, AnnotatedOnly, Direct, Dynamic, ImportedOnly, RegistryTarget,\n"
        ")\n"
        "__all__ = [\n"
        "    'Direct', 'AnnotatedOnly', 'Dynamic', 'RegistryTarget', 'AliasTarget',\n"
        "    'ImportedOnly',\n"
        "]\n",
    )
    _write(
        production / "part" / "api.py",
        "class Direct: pass\n"
        "class AnnotatedOnly: pass\n"
        "class Dynamic: pass\n"
        "class RegistryTarget: pass\n"
        "class AliasTarget: pass\n"
        "class ImportedOnly: pass\n"
        "class UnusedImport: pass\n"
        "class Orphan: pass\n",
    )
    direct_use = "" if remove_direct_wiring else "Direct()"
    _write(
        production / "composition.py",
        "from __future__ import annotations\n"
        "import sample.part as part\n"
        "from sample.part import AliasTarget, AnnotatedOnly, Direct, ImportedOnly, RegistryTarget\n"
        "from sample.part.api import UnusedImport\n"
        "\n"
        "Alias = AliasTarget\n"
        "_HANDLER_REGISTRY = {'registry': RegistryTarget}\n"
        "def _compose(value: AnnotatedOnly) -> None:\n"
        f"    {direct_use or 'pass'}\n"
        "    Alias()\n"
        "    getattr(part, 'Dynamic')()\n",
    )
    if add_internal_wiring:
        _write(
            production / "part" / "runtime.py",
            "from sample.part import Direct\n"
            "def use_inside_part():\n"
            "    return Direct()\n",
        )
    _write(
        tests / "test_surface.py",
        "import sample.part as part\n"
        "from sample.part import AliasTarget, AnnotatedOnly, Direct, Dynamic, ImportedOnly, RegistryTarget\n"
        "def test_surface():\n"
        "    assert part.__all__\n"
        "    assert all((AliasTarget, AnnotatedOnly, Direct, Dynamic, ImportedOnly, RegistryTarget))\n",
    )
    analysis = ReferenceAnalysis(production, tests, package="sample")
    temporary.cleanup()
    return analysis


def test_reference_analysis_distinguishes_wiring_from_imports_and_annotations() -> None:
    analysis = _fixture_analysis()
    t1 = {finding.symbol for finding in analysis.t1_findings()}
    assert t1 == {"sample.part.ImportedOnly"}, sorted(t1)

    # An annotation is a recognised production reference for both guards. A test
    # reference also clears T2, while a production import that is never used does not.
    t2 = {finding.symbol for finding in analysis.t2_findings()}
    assert "sample.part.api.AnnotatedOnly" not in t2
    assert "sample.part.api.ImportedOnly" not in t2
    assert t2 == {"sample.part.api.Orphan", "sample.part.api.UnusedImport"}, sorted(t2)

def test_removing_production_wiring_creates_a_t1_finding() -> None:
    analysis = _fixture_analysis(remove_direct_wiring=True)
    t1 = {finding.symbol for finding in analysis.t1_findings()}
    assert "sample.part.Direct" in t1


def test_supported_dynamic_and_alias_patterns_are_runtime_wiring() -> None:
    analysis = _fixture_analysis()
    t1 = {finding.symbol for finding in analysis.t1_findings()}
    assert "sample.part.Dynamic" not in t1  # literal getattr
    assert "sample.part.RegistryTarget" not in t1  # string-keyed dispatch table
    assert "sample.part.AliasTarget" not in t1  # used through an alias


def test_runtime_use_inside_the_exporting_part_does_not_justify_a_public_export() -> None:
    analysis = _fixture_analysis(remove_direct_wiring=True, add_internal_wiring=True)
    t1 = {finding.symbol for finding in analysis.t1_findings()}
    assert "sample.part.Direct" in t1


def test_t1_tested_exports_have_meaningful_production_use() -> None:
    analysis = ReferenceAnalysis(RQA, _TEST_ROOT)
    findings = analysis.t1_findings()
    assert all(reason.strip() for reason in T1_JUSTIFIED_EXCEPTIONS.values())
    symbols = {finding.symbol for finding in findings}
    unexpected = tuple(
        finding for finding in findings if finding.symbol not in T1_JUSTIFIED_EXCEPTIONS
    )
    stale = sorted(set(T1_JUSTIFIED_EXCEPTIONS) - symbols)
    assert unexpected == (), "T1 unexplained tested exports lacking production wiring:\n" + format_findings(
        unexpected, _SKILL_ROOT
    )
    assert stale == [], f"T1 exception entries no longer matching a finding: {stale}"


def test_t2_public_definitions_have_a_recognised_reference() -> None:
    analysis = ReferenceAnalysis(RQA, _TEST_ROOT)
    findings = analysis.t2_findings()
    assert findings == (), "T2 public definitions with zero recognised references:\n" + format_findings(
        findings, _SKILL_ROOT
    )

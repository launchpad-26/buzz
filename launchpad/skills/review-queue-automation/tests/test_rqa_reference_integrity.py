#!/usr/bin/env python3
"""T1 reference-integrity guard for #2311.

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
sys.path.insert(0, str(_TEST_ROOT))

from reference_analysis import ReferenceAnalysis, format_findings  # noqa: E402

RQA = _SKILL_ROOT / "rqa"


def _write(path: pathlib.Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture_analysis(*, remove_direct_wiring: bool = False) -> ReferenceAnalysis:
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
        "class UnusedImport: pass\n",
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
    assert t1 == {"sample.part.AnnotatedOnly", "sample.part.ImportedOnly"}, sorted(t1)

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


def test_t1_tested_exports_have_meaningful_production_use() -> None:
    analysis = ReferenceAnalysis(RQA, _TEST_ROOT)
    findings = analysis.t1_findings()
    assert findings == (), "T1 tested exports lacking production wiring:\n" + format_findings(
        findings, _SKILL_ROOT
    )

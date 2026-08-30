"""Structural and calibration tests for the assessment skill."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SkillContractTests(unittest.TestCase):
    def test_skill_has_valid_spine_and_references(self):
        skill = (ROOT / "SKILL.md").read_text()
        self.assertTrue(skill.startswith("---\nname: software-change-impact-assessment\n"))
        self.assertLess(len(skill.splitlines()), 500)
        for ref in ("report-template.md", "assessment-method.md", "change-categories.md",
                    "conflict-model.md", "evidence-guidance.md", "risk-model.md", "examples.md"):
            self.assertTrue((ROOT / "references" / ref).is_file(), ref)
            self.assertIn(f"references/{ref}", skill)

    def test_report_template_covers_required_sections(self):
        text = (ROOT / "references/report-template.md").read_text()
        headings = set(re.findall(r"^## (?:\d+\. )?(.*)$", text, re.MULTILINE))
        for section in ("Change Identification", "Executive Summary", "Change Scope",
                        "Significant Functional Changes", "Architecture and Technical Impact",
                        "API and Interface Impact", "Data and Schema Impact", "Configuration Impact",
                        "Dependency and Supply-Chain Impact", "Build and Toolchain Impact", "CI/CD Impact",
                        "Security Impact", "Operational and Observability Impact", "Downstream Impact",
                        "Conflict Assessment", "Risk Assessment", "Required Attention and Verification",
                        "Unknowns and Limitations", "Assessment Recommendation", "Evidence"):
            self.assertIn(section, headings, section)

    def test_methodology_pins_evidence_unknowns_and_boundaries(self):
        skill = (ROOT / "SKILL.md").read_text()
        refs = "\n".join(p.read_text() for p in (ROOT / "references").glob("*.md"))
        for phrase in ("immutable", "UNKNOWN", "semantic", "policy", "supply chain", "advisory"):
            self.assertIn(phrase.lower(), (skill + refs).lower(), phrase)
        self.assertIn("never synchronize, merge, approve, deploy", skill.lower())
        self.assertIn("does not authorize", (skill + refs).lower())

class ScenarioCalibrationTests(unittest.TestCase):
    def test_examples_cover_requested_calibration_scenarios(self):
        text = (ROOT / "references/examples.md").read_text().lower()
        for phrase in ("documentation-only", "dependency upgrade", "ci trust boundary",
                       "textual conflict", "semantic conflict", "policy conflict", "missing evidence"):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()

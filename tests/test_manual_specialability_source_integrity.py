import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "rules" / "manual-specialability-source.txt"
CATALOGUE = ROOT / "data" / "rules" / "fm1-skill-catalog-v1.json"


class ManualSpecialAbilitySourceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_text = SOURCE.read_text(encoding="utf-8")
        cls.catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
        cls.manual_skills = [
            rule for rule in cls.catalogue["rules"]
            if rule.get("authority") == "manual"
            and rule.get("source", {}).get("member") == "specialability.htm"
        ]

    @staticmethod
    def norm(value):
        return re.sub(r"\s+", "", value).replace("·", "").replace("ㆍ", "")

    def test_source_snapshot_has_exact_27_numbered_skill_sections(self):
        headings = re.findall(r"(?m)^\s*(\d+)\.\s*([^\n]+)", self.source_text)
        self.assertEqual([int(number) for number, _ in headings], list(range(1, 28)))
        self.assertEqual(len(headings), 27)

    def test_manual_skill_catalogue_count_matches_source_sections(self):
        self.assertEqual(len(self.manual_skills), 27)

    def test_each_catalogue_rule_retains_manual_archive_provenance(self):
        for rule in self.manual_skills:
            with self.subTest(rule=rule["id"]):
                source = rule.get("source", {})
                self.assertEqual(source.get("bundle"), "Manual.zip")
                self.assertEqual(source.get("member"), "specialability.htm")
                self.assertEqual(source.get("section"), "특수기술목록표")
                self.assertEqual(source.get("priority"), 1)
                self.assertEqual(rule.get("authority"), "manual")
                self.assertEqual(rule.get("verificationStatus"), "manual_verified")
                self.assertEqual(rule.get("implementationStatus"), "pending_engine_test")

    def test_community_or_inferred_entries_are_not_promoted_by_manual_source_count(self):
        non_manual = [
            rule for rule in self.catalogue["rules"]
            if rule.get("authority") != "manual"
        ]
        self.assertTrue(non_manual)
        self.assertTrue(all(rule.get("playableByDefault") is False for rule in non_manual))

    def test_each_numbered_manual_heading_resolves_to_exactly_one_catalogue_rule(self):
        headings = re.findall(r"(?m)^\s*(\d+)\.\s*([^\n]+)", self.source_text)
        for number, heading in headings:
            matches = [
                rule for rule in self.manual_skills
                if any(self.norm(alias) == self.norm(heading.strip()) for alias in [rule["name"], *rule["aliases"]])
            ]
            with self.subTest(section=number, heading=heading.strip()):
                self.assertEqual(len(matches), 1, f"heading should map uniquely: {heading}")

    def test_manual_catalogue_aliases_are_unique_within_manual_inventory(self):
        aliases = {}
        for rule in self.manual_skills:
            for alias in [rule["name"], *rule["aliases"]]:
                key = self.norm(alias)
                previous = aliases.get(key)
                self.assertTrue(previous is None or previous == rule["id"], f"duplicate alias {alias}: {previous}, {rule['id']}")
                aliases[key] = rule["id"]


if __name__ == "__main__":
    unittest.main()

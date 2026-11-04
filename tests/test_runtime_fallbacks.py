"""Regression tests for the provenance-preserving runtime fallback layer."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply_runtime_fallbacks.py"


class RuntimeFallbackTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "fixture.sqlite"
        self.pack = self.root / "pack.json"
        con = sqlite3.connect(self.db)
        con.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE cards(card_id TEXT PRIMARY KEY, name TEXT NOT NULL);
            CREATE TABLE card_fields(
                field_id INTEGER PRIMARY KEY,
                card_id TEXT NOT NULL REFERENCES cards(card_id),
                field_key TEXT NOT NULL,
                source_value_json TEXT
            );
            INSERT INTO cards(card_id,name) VALUES ('c1','Fixture');
        """)
        con.commit()
        con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def run_pack(self, rules, pack_id="fixture-v1"):
        self.pack.write_text(json.dumps({"id": pack_id, "rules": rules}), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--db", str(self.db), "--rule-pack", str(self.pack)],
            cwd=ROOT, text=True, capture_output=True,
        )

    def rule(self, **overrides):
        row = {
            "card_id": "c1", "field_key": "Skill1", "value": {"runtime": "passive"},
            "rationale": "Fixture-only rule for regression coverage", "confidence": "medium",
            "fallback_kind": "inferred", "evidence": ["test-fixture"],
        }
        row.update(overrides)
        return row

    def test_apply_creates_separate_layer_and_preserves_raw_source(self):
        con = sqlite3.connect(self.db)
        con.execute("ALTER TABLE cards ADD COLUMN raw_payload_json TEXT")
        con.execute("UPDATE cards SET raw_payload_json='{\"Skill1\":\"source\"}' WHERE card_id='c1'")
        con.commit()
        con.close()

        result = self.run_pack([self.rule()])
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["rules_applied"], 1)
        self.assertEqual(report["foreign_key_errors"], 0)

        con = sqlite3.connect(self.db)
        raw = con.execute("SELECT raw_payload_json FROM cards WHERE card_id='c1'").fetchone()[0]
        fallback = con.execute(
            "SELECT fallback_value_json,confidence,rule_pack_id FROM runtime_fallbacks"
        ).fetchone()
        con.close()
        self.assertEqual(raw, '{"Skill1":"source"}')
        self.assertEqual(json.loads(fallback[0]), {"runtime": "passive"})
        self.assertEqual(fallback[1:], ("medium", "fixture-v1"))

    def test_source_value_requires_explicit_override_acknowledgement(self):
        con = sqlite3.connect(self.db)
        con.execute("INSERT INTO card_fields(card_id,field_key,source_value_json) VALUES ('c1','Skill1','\"source\"')")
        con.commit()
        con.close()
        result = self.run_pack([self.rule()])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Source value exists", result.stderr)

        result = self.run_pack([self.rule(allow_source_override=True)])
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_unknown_card_is_rejected(self):
        result = self.run_pack([self.rule(card_id="missing")])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown card_id", result.stderr)

    def test_same_pack_is_idempotent(self):
        self.assertEqual(self.run_pack([self.rule()]).returncode, 0)
        self.assertEqual(self.run_pack([self.rule(value={"runtime": "updated"})]).returncode, 0)
        con = sqlite3.connect(self.db)
        count = con.execute("SELECT COUNT(*) FROM runtime_fallbacks").fetchone()[0]
        value = con.execute("SELECT fallback_value_json FROM runtime_fallbacks").fetchone()[0]
        con.close()
        self.assertEqual(count, 1)
        self.assertEqual(json.loads(value), {"runtime": "updated"})


if __name__ == "__main__":
    unittest.main()

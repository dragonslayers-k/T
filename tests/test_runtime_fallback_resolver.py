"""Tests for source-first runtime field resolution."""
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.resolve_runtime_fallbacks import resolve_field


class RuntimeFallbackResolverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db = Path(self.tmp.name) / "resolver.sqlite"
        con = sqlite3.connect(self.db)
        con.executescript("""
          PRAGMA foreign_keys=ON;
          CREATE TABLE cards(card_id TEXT PRIMARY KEY, raw_payload_json TEXT NOT NULL);
          CREATE TABLE runtime_fallbacks(
            card_id TEXT NOT NULL REFERENCES cards(card_id), field_key TEXT NOT NULL,
            fallback_value_json TEXT NOT NULL, source_value_json TEXT,
            fallback_kind TEXT NOT NULL, rationale TEXT NOT NULL, confidence TEXT NOT NULL,
            evidence_json TEXT NOT NULL, rule_pack_id TEXT NOT NULL, rule_pack_sha256 TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY(card_id,field_key,rule_pack_id)
          );
          INSERT INTO cards(card_id,raw_payload_json) VALUES
            ('source','{"Skill1":"official source"}'),
            ('null-source','{"Skill1":null}'),
            ('missing','{}');
          INSERT INTO runtime_fallbacks
            (card_id,field_key,fallback_value_json,source_value_json,fallback_kind,
             rationale,confidence,evidence_json,rule_pack_id,rule_pack_sha256)
          VALUES
            ('source','Skill1','"inferred"','"official source"','inferred','fallback fixture','high','[]','pack-a','abc'),
            ('null-source','Skill1','"filled"','null','safe_default','null source fallback','medium','["fixture"]','pack-a','abc'),
            ('missing','Skill1','"added"','null','inferred','missing field fallback','low','[]','pack-a','abc');
        """)
        con.commit()
        con.close()

    def tearDown(self):
        self.tmp.cleanup()

    def test_source_value_wins_over_fallback(self):
        result = resolve_field(self.db, "source", "Skill1")
        self.assertEqual(result["value"], "official source")
        self.assertEqual(result["resolved_from"], "source")
        self.assertFalse(result["fallback_used"])

    def test_json_null_uses_fallback_with_provenance(self):
        result = resolve_field(self.db, "null-source", "Skill1")
        self.assertEqual(result["value"], "filled")
        self.assertEqual(result["resolved_from"], "runtime_fallback")
        self.assertEqual(result["provenance"]["confidence"], "medium")
        self.assertEqual(result["provenance"]["evidence"], ["fixture"])

    def test_missing_source_uses_fallback(self):
        result = resolve_field(self.db, "missing", "Skill1")
        self.assertEqual(result["value"], "added")
        self.assertTrue(result["fallback_used"])

    def test_unknown_card_is_rejected(self):
        with self.assertRaises(KeyError):
            resolve_field(self.db, "not-a-card", "Skill1")

    def test_pack_filter_and_missing_fallback(self):
        result = resolve_field(self.db, "missing", "Skill1", "other-pack")
        self.assertIsNone(result["value"])
        self.assertEqual(result["resolved_from"], "missing")


if __name__ == "__main__":
    unittest.main()

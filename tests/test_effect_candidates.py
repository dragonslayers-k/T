import sqlite3
import unittest

from scripts.build_effect_candidates import build


class EffectCandidateDatabaseTests(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
        CREATE TABLE cards(card_id TEXT PRIMARY KEY, source_card_url TEXT);
        CREATE TABLE card_texts(
            text_id INTEGER PRIMARY KEY, card_id TEXT, text_type TEXT,
            source_text TEXT, plain_text TEXT
        );
        INSERT INTO cards VALUES('c-1','https://fmlunatic.com/card/c-1');
        INSERT INTO card_texts VALUES(
          1,'c-1','card_text','아군 AP+1.\n\n※ 적 HP-2','아군 AP+1.\n\n※ 적 HP-2'
        );
        """)

    def tearDown(self):
        self.db.close()

    def test_build_preserves_source_spans_and_separators(self):
        result = build(self.db)
        self.assertEqual(result["candidateSummaryRows"], 1)
        rows = self.db.execute(
            "SELECT segment_type,segment_text FROM card_effect_clauses ORDER BY clause_index"
        ).fetchall()
        self.assertEqual("".join(text for _, text in rows), "아군 AP+1.\n\n※ 적 HP-2")
        self.assertTrue(any(kind == "separator" for kind, _ in rows))

    def test_candidates_are_not_marked_executable(self):
        build(self.db)
        statuses = {
            row[0] for row in self.db.execute(
                "SELECT verification_status FROM card_effect_candidate_summaries "
                "UNION SELECT verification_status FROM card_effect_clauses"
            )
        }
        self.assertEqual(statuses, {"pattern_candidate"})

    def test_actual_source_card_url_is_joined(self):
        build(self.db)
        self.assertEqual(
            self.db.execute(
                "SELECT source_detail_url FROM card_effect_candidate_summaries"
            ).fetchone()[0],
            "https://fmlunatic.com/card/c-1",
        )

    def test_rebuild_is_idempotent(self):
        first = build(self.db)
        second = build(self.db)
        self.assertEqual(first["candidateSummaryRows"], second["candidateSummaryRows"])
        self.assertEqual(first["clauseRows"], second["clauseRows"])
        self.assertEqual(
            self.db.execute("SELECT COUNT(*) FROM card_effect_candidate_summaries").fetchone()[0],
            1,
        )


if __name__ == "__main__":
    unittest.main()

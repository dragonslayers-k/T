import gzip
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from build_card_semantic_ledger import build


class CardSemanticLedgerTests(unittest.TestCase):
    def test_emits_one_pending_semantic_row_per_card_and_preserves_source_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "mini.sqlite"
            db = sqlite3.connect(db_path)
            db.executescript("""
                CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT,card_type TEXT,attribute TEXT,
                    source_list_url TEXT,source_card_url TEXT,detail_url_status TEXT,raw_payload_json TEXT,
                    content_hash TEXT,collected_at TEXT,verification_status TEXT);
                CREATE TABLE card_fields(field_id INTEGER PRIMARY KEY,card_id TEXT,field_key TEXT,
                    source_value_json TEXT,normalized_value TEXT,source_location TEXT,verification_status TEXT);
                CREATE TABLE card_texts(text_id INTEGER PRIMARY KEY,card_id TEXT,text_type TEXT,
                    source_text TEXT,plain_text TEXT,source_location TEXT);
                CREATE TABLE card_costs(card_id TEXT PRIMARY KEY,lp_value REAL,lp_known INTEGER,soul_json TEXT,
                    soul_known INTEGER,semantic_review INTEGER,mapping_review INTEGER,source_text TEXT,verification_status TEXT);
                CREATE TABLE card_soul_cost_tokens(token_id INTEGER PRIMARY KEY,card_id TEXT,ordinal INTEGER,
                    raw_token TEXT,code INTEGER,count INTEGER,symbol TEXT,icon_path TEXT,normalized_color TEXT,parse_status TEXT);
                CREATE TABLE card_images(image_id INTEGER PRIMARY KEY,card_id TEXT,image_type TEXT,source_url TEXT,
                    local_path TEXT,archive_path TEXT,mime_type TEXT,byte_size INTEGER,sha256 TEXT,download_status TEXT);
                CREATE TABLE card_effects(effect_id INTEGER PRIMARY KEY,card_id TEXT,effect_index INTEGER,
                    source_key TEXT,effect_text TEXT,trigger_text TEXT,target_text TEXT,condition_text TEXT,duration_text TEXT,verification_status TEXT);
                CREATE TABLE source_pages(page_id INTEGER PRIMARY KEY,card_id TEXT,page_type TEXT,url TEXT,
                    http_status INTEGER,collected_at TEXT,content_hash TEXT);
                CREATE TABLE verification(verification_id INTEGER PRIMARY KEY,card_id TEXT,field_key TEXT,
                    status TEXT,evidence TEXT,verified_by TEXT,verified_at TEXT);
                CREATE TABLE card_rule_mappings(mapping_id INTEGER PRIMARY KEY,card_id TEXT,source_field TEXT,mapping_status TEXT);
                CREATE TABLE card_field_coverage(coverage_id INTEGER PRIMARY KEY,card_id TEXT,field_key TEXT,
                    coverage_status TEXT,source_payload_match INTEGER);
                CREATE TABLE card_effect_candidate_summaries(candidate_id INTEGER PRIMARY KEY,text_id INTEGER,card_id TEXT,
                    text_type TEXT,source_text_sha256 TEXT,source_detail_url TEXT,source_text_class_candidate TEXT,
                    topic_candidates_json TEXT,trigger_candidates_json TEXT,actor_candidates_json TEXT,target_candidates_json TEXT,
                    operation_candidates_json TEXT,number_candidates_json TEXT,special_token_candidates_json TEXT,analysis_json TEXT,
                    verification_status TEXT,span_integrity_status TEXT);
                CREATE TABLE card_effect_clauses(clause_id TEXT PRIMARY KEY,card_id TEXT,source_text TEXT);
                CREATE TABLE card_effect_interpretations(clause_id TEXT,verification_status TEXT,confidence TEXT);
            """)
            for card_id, name, raw in [
                ("1", "A", {"Skill1": 1, "TextBase": "원문 효과"}),
                ("2", "B", {"TextExtra": "보조 원문"}),
            ]:
                db.execute("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (card_id, name, "유닛", "불", "https://fmlunatic.com/cardlist",
                     f"https://fmlunatic.com/card/{card_id}", "source_url_present",
                     json.dumps(raw, ensure_ascii=False), "hash", "date", "extracted_unverified"))
            db.execute("INSERT INTO card_fields VALUES(1,'1','Skill1','1','skill','firestore','extracted_unverified')")
            db.execute("INSERT INTO card_texts VALUES(1,'1','card_text','원문 효과','원문 효과','Firestore')")
            db.execute("INSERT INTO card_costs VALUES('1',1,1,'{}',1,1,0,'8201','semantic_review')")
            db.execute("INSERT INTO card_soul_cost_tokens VALUES(1,'1',0,'8201',82,1,'NCS',NULL,'ncs','semantic_review')")
            db.execute("INSERT INTO card_images VALUES(1,'1','large','url',NULL,'archive','image/webp',10,'sha','archive_verified')")
            db.execute("INSERT INTO card_effects VALUES(1,'1',0,'TextBase','원문 효과',NULL,NULL,NULL,NULL,'extracted_unverified')")
            db.execute("""INSERT INTO card_effect_candidate_summaries VALUES(
                1,1,'1','card_text','sha','https://fmlunatic.com/card/1','candidate',
                '[]','[]','[]','[]','[]','[]','[]','{}','pattern_candidate','exact')""")
            db.execute("INSERT INTO card_effect_clauses VALUES('cl1','1','원문 효과')")
            db.execute("INSERT INTO card_effect_interpretations VALUES('cl1','pending','low')")
            db.commit()
            db.close()

            summary = build(db_path, root / "ledger.jsonl.gz", root / "index.csv", root / "summary.json", expected=2)
            self.assertEqual(summary["unique_cards"], 2)
            self.assertEqual(summary["metrics"]["semantic_review_cards"], 1)
            with gzip.open(root / "ledger.jsonl.gz", "rt", encoding="utf-8") as stream:
                rows = [json.loads(line) for line in stream]
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["card_id"], "1")
            self.assertEqual(rows[0]["axis_status"]["cost"], "semantic_review_blocked")
            self.assertEqual(rows[0]["axis_status"]["semantic_review"], "pending_card_level_adjudication")
            self.assertEqual(rows[0]["cost_tokens"][0]["raw_token"], "8201")
            self.assertEqual(rows[0]["effect_candidate_summaries"][0]["candidate_id"], 1)
            self.assertEqual(rows[0]["axis_status"]["effects"], "clauses_and_candidate_summaries_not_verified")
            self.assertEqual(rows[1]["axis_status"]["identity"], "source_card_url_present")


if __name__ == "__main__":
    unittest.main()

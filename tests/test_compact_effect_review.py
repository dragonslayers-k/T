import csv
import json
import tempfile
import unittest
from pathlib import Path

from scripts.compact_effect_review import build


class CompactEffectReviewTests(unittest.TestCase):
    def test_preserves_card_text_source_and_reports_group_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "input.jsonl"
            source.write_text(
                json.dumps({
                    "card_id": "1001", "name": "검토 카드", "card_type": "유닛",
                    "clause_index": 2, "confidence": "low",
                    "interpretation_json": json.dumps({"classification": "condition"}, ensure_ascii=False),
                    "segment_text": "  조건 효과\n원문  ", "source_detail_url": "https://fmlunatic.com/card/1001",
                    "verification_status": "pending"
                }, ensure_ascii=False) + "\n" +
                json.dumps({
                    "card_id": "1002", "name": "다른 카드", "card_type": "마법",
                    "clause_index": 1, "confidence": "low", "interpretation_json": "{bad",
                    "segment_text": "조건 효과 원문", "source_detail_url": "https://fmlunatic.com/card/1002",
                    "verification_status": "pending"
                }, ensure_ascii=False) + "\n",
                encoding="utf-8"
            )
            output = root / "compact.csv"
            summary_path = root / "summary.json"
            summary = build(source, output, summary_path)
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(summary["rows"], 2)
            self.assertEqual(summary["unique_card_ids"], 2)
            self.assertEqual(summary["unique_text_patterns"], 1)
            self.assertEqual(summary["classification_counts"], {"condition": 1, "unknown": 1})
            self.assertEqual(rows[0]["card_id"], "1001")
            self.assertEqual(rows[0]["segment_text"], "  조건 효과\n원문  ")
            self.assertEqual(rows[0]["source_detail_url"], "https://fmlunatic.com/card/1001")
            self.assertEqual(json.loads(summary_path.read_text(encoding="utf-8"))["rows"], 2)


if __name__ == "__main__":
    unittest.main()

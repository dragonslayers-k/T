import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from scripts.export_soul_review_images import build_target_cards, export_archive


def webp_bytes(color):
    stream = io.BytesIO()
    Image.new("RGB", (8, 8), color).save(stream, format="WEBP")
    return stream.getvalue()


class SoulReviewImageExportTests(unittest.TestCase):
    def rows(self):
        return [
            {
                "card_id": "ncs-card",
                "name": "NCS card",
                "type": "unit",
                "source_card_url": "https://fmlunatic.com/card/ncs-card",
                "raw_payload": {"RequireSoul": "8201"},
            },
            {
                "card_id": "bonus-card",
                "name": "BONUS card",
                "type": "item",
                "raw_payload": {"RequireSoul": "8302"},
            },
            {
                "card_id": "hybrid-card",
                "name": "Hybrid card",
                "type": "spell",
                "raw_payload": {"RequireSoul": "1201"},
            },
            {
                "card_id": "mu-only-card",
                "name": "MU-only card",
                "type": "unit",
                "raw_payload": {"RequireSoul": "8101"},
            },
        ]

    def test_target_population_keeps_special_and_hybrid_separate(self):
        targets = build_target_cards(self.rows(), expected_cards=3)
        self.assertEqual(set(targets), {"ncs-card", "bonus-card", "hybrid-card"})
        self.assertEqual(targets["ncs-card"]["review_groups"], ["NCS"])
        self.assertEqual(targets["bonus-card"]["review_groups"], ["BONUS"])
        self.assertEqual(targets["hybrid-card"]["review_groups"], ["hybrid:DARK_EARTH"])
        self.assertEqual(targets["ncs-card"]["source_card_url"], "https://fmlunatic.com/card/ncs-card")


    def test_earnsoul_namespace_does_not_select_require_soul_review(self):
        rows = [
            {
                "card_id": "earn-mu02-only",
                "name": "EarnSoul MU02 only",
                "type": "unit",
                "raw_payload": {"RequireSoul": "8101", "EarnSoul": "8201"},
            },
            {
                "card_id": "require-ncs",
                "name": "RequireSoul NCS",
                "type": "unit",
                "raw_payload": {"RequireSoul": "8201", "EarnSoul": "0101"},
            },
        ]
        targets = build_target_cards(rows, expected_cards=1)
        self.assertEqual(set(targets), {"require-ncs"})
        self.assertEqual(targets["require-ncs"]["review_groups"], ["NCS"])

    def test_stream_extracts_only_target_cards_and_verifies_all_six_images(self):
        rows = self.rows()
        targets = build_target_cards(rows, expected_cards=3)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "images.tar.gz"
            output_dir = root / "output"
            with tarfile.open(archive_path, "w:gz") as archive:
                for card_id in targets:
                    for image_type in ("small", "large"):
                        data = webp_bytes((40, 80, 120))
                        info = tarfile.TarInfo(f"./{image_type}/{card_id}.webp")
                        info.size = len(data)
                        archive.addfile(info, io.BytesIO(data))
                unrelated = webp_bytes((0, 0, 0))
                info = tarfile.TarInfo("./small/mu-only-card.webp")
                info.size = len(unrelated)
                archive.addfile(info, io.BytesIO(unrelated))

            summary = export_archive(archive_path, rows, output_dir, expected_cards=3)
            self.assertTrue(summary["complete"])
            self.assertEqual(summary["expected_images"], 6)
            self.assertEqual(summary["verified_images"], 6)
            self.assertEqual(summary["small_images"], 3)
            self.assertEqual(summary["large_images"], 3)
            self.assertFalse((output_dir / "images/small/mu-only-card.webp").exists())
            target_rows = [
                json.loads(line)
                for line in (output_dir / "target-cards.jsonl").read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(len(target_rows), 3)

    def test_missing_target_image_fails_closed(self):
        rows = self.rows()
        targets = build_target_cards(rows, expected_cards=3)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive_path = root / "images.tar.gz"
            with tarfile.open(archive_path, "w:gz") as archive:
                for card_id in targets:
                    data = webp_bytes((10, 20, 30))
                    info = tarfile.TarInfo(f"./small/{card_id}.webp")
                    info.size = len(data)
                    archive.addfile(info, io.BytesIO(data))
            with self.assertRaises(RuntimeError):
                export_archive(archive_path, rows, root / "output", expected_cards=3)


if __name__ == "__main__":
    unittest.main()

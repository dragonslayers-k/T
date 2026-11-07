import unittest
from scripts.full_card_visual_ocr_inventory import normalize_text, parse_member
class FullCardVisualOCRInventoryTests(unittest.TestCase):
    def test_normalize_whitespace(self): self.assertEqual(normalize_text(" a  \n b "),"a b")
    def test_parse_valid_image_path(self): self.assertEqual(parse_member("data/images/large/1001.webp",{"1001"}),("1001","large","data/images/large/1001.webp"))
    def test_ignore_unknown_card(self): self.assertIsNone(parse_member("data/images/small/9999.webp",{"1001"}))
    def test_ignore_non_image_size_path(self): self.assertIsNone(parse_member("data/images/medium/1001.webp",{"1001"}))
if __name__=="__main__": unittest.main()

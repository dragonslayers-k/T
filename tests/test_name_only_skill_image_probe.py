import unittest

from scripts.probe_name_only_skill_images import contains_skill_name, fuzzy_skill_name_match, normalize_text


class NameOnlySkillImageProbeTests(unittest.TestCase):
    def test_normalizes_whitespace_for_korean_skill_name_match(self):
        self.assertEqual(normalize_text("그레이브 파워"), normalize_text("그레이브파워"))

    def test_detects_skill_name_in_ocr_text(self):
        self.assertTrue(contains_skill_name("특수기술: 눈덩이 연타 발동", "눈덩이연타"))

    def test_fuzzy_match_is_only_a_candidate(self):
        result = fuzzy_skill_name_match("그레이브파와", "그레이브파워")
        self.assertTrue(result["matched"])
        self.assertGreaterEqual(result["score"], 0.78)
        self.assertEqual(result["matchedText"], "그레이브파와")

    def test_does_not_match_unrelated_ocr_text(self):
        self.assertFalse(contains_skill_name("아군 AP +1", "눈덩이연타"))


if __name__ == "__main__":
    unittest.main()

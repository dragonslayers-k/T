import unittest

from scripts.probe_name_only_skill_images import (classify_image_match, contains_skill_name, fuzzy_skill_name_match, normalize_text)


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

    def test_exact_skill_text_is_not_confused_with_same_card_title(self):
        status, context, has_slash, collision = classify_image_match(
            "다크아레아", "다크아레아", True, False, "다크아레아", "다크아레아"
        )
        self.assertEqual(status, "name_collision")
        self.assertTrue(collision)
        self.assertFalse(has_slash)

    def test_slash_context_is_strong_skill_label_evidence(self):
        status, context, has_slash, collision = classify_image_match(
            "개화하는소질", "정원의소녀", True, False,
            "개화하는소질", "정원의소녀\n개화하는소질/만개하는재능"
        )
        self.assertEqual(status, "image_text_exact")
        self.assertTrue(has_slash)
        self.assertFalse(collision)
        self.assertIn("개화하는소질", context)

    def test_fuzzy_match_never_becomes_semantic_verification(self):
        status, context, has_slash, collision = classify_image_match(
            "그레이브파워", "다브노자에", False, True,
            "그레0브파워", "다브노자에\n그레0브파워"
        )
        self.assertEqual(status, "fuzzy_candidate")



if __name__ == "__main__":
    unittest.main()

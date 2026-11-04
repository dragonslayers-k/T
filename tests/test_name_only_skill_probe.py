import unittest

from scripts.probe_name_only_skill_pages import contexts, parse_page


class NameOnlySkillPageProbeTests(unittest.TestCase):
    def test_extracts_visible_text_and_title_but_skips_scripts(self):
        title, text = parse_page(
            "<html><head><title>정원의소녀</title><script>개화하는소질 hidden</script></head>"
            "<body><h1>카드 정보</h1><p>개화하는소질</p></body></html>"
        )
        self.assertEqual(title, "정원의소녀")
        self.assertIn("개화하는소질", text)
        self.assertNotIn("hidden", text)

    def test_contexts_preserve_source_near_skill_name(self):
        text = "앞부분 설명 " + ("중간 문장 " * 10) + "그레이브파워 발동 시 효과"
        found = contexts(text, "그레이브파워")
        self.assertEqual(len(found), 1)
        self.assertIn("그레이브파워", found[0])
        self.assertIn("효과", found[0])


if __name__ == "__main__":
    unittest.main()

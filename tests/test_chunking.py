import unittest

from plc_rag.chunking import chunk_markdown, content_role


class ChunkingTests(unittest.TestCase):
    def test_indented_example(self):
        text = "    CLASS Motor\n        VAR\n            running : BOOL;\n        END_VAR\n    END_CLASS"
        chunks = chunk_markdown("# Class\n" + text, "local", "Reference")
        self.assertEqual(chunks[0]["content_role"], "examples")
        self.assertEqual(chunks[0]["text"], text.strip())

    def test_rules_and_mixed(self):
        self.assertEqual(content_role("Classes can declare only a static section."), "rules")
        self.assertEqual(content_role("Only static fields.\nCLASS Motor\nEND_CLASS"), "mixed")
        self.assertEqual(content_role("Unclassified explanatory material."), "mixed")

    def test_fence_stays_whole(self):
        code = "```iecst\nCLASS Motor\n\n    METHOD Start\n    END_METHOD\nEND_CLASS\n```"
        chunks = chunk_markdown("# Example\n" + code, "local", "Reference", max_chars=45)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0]["text"], code)


if __name__ == "__main__":
    unittest.main()
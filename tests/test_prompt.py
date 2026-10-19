import unittest
from unittest.mock import patch

from plc_rag.prompt import SYSTEM, build_messages, est_tokens


class PromptTests(unittest.TestCase):
    def test_skip_oversized_hit_and_number_used_sources(self):
        hits = [
            {"heading_path": "Huge", "text": "x" * 30000},
            {"heading_path": "Enumeration", "text": "TYPE Colors : (Red, Green); END_TYPE"},
        ]
        messages, used = build_messages("Write an enumeration", hits, "generate")
        self.assertEqual(used, hits[1:])
        self.assertIn("[DOC 1] Enumeration", messages[-1]["content"])
        self.assertNotIn("[DOC 2]", messages[-1]["content"])

    def test_documentation_precedes_history_in_generation_budget(self):
        hits = [{"heading_path": "Class declaration", "text": "Only static VAR. " * 20}]
        with patch("plc_rag.prompt.NUM_CTX", 1500), patch("plc_rag.prompt.MAX_NEW_TOKENS", 200):
            messages, used = build_messages("Create a class", hits, "generate", [{"role": "user", "content": "h" * 5000}])
            self.assertEqual(used, hits)
            self.assertLessEqual(sum(est_tokens(msg["content"]) + 8 for msg in messages) + 200, 1500)

    def test_oversized_request_is_rejected(self):
        with self.assertRaises(ValueError):
            build_messages("x" * 30000, [], "generate")

    def test_missing_evidence_retains_refusal_and_no_vendor_templates(self):
        messages, used = build_messages("Use RTRIG_P", [], "generate")
        self.assertFalse(used)
        self.assertIn("(no documentation found)", messages[-1]["content"])
        self.assertIn("Not found in the provided documentation.", SYSTEM)
        self.assertNotIn("PROGRAM Name", SYSTEM)


if __name__ == "__main__":
    unittest.main()
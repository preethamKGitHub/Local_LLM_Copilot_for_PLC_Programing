import unittest
from unittest.mock import MagicMock, patch

from eval.run_eval import evaluate_generation
from plc_rag.validation import REFUSAL


class EvaluationTests(unittest.TestCase):
    @patch("eval.run_eval.chat_stream", return_value=iter(["```iecst\nTYPE Colors : (Red, Green); END_TYPE\n```\n[DOC 1]"]))
    def test_evidence_uses_included_not_all_retrieved_hits(self, _chat_stream):
        retriever = MagicMock()
        retriever.search_generation.return_value = [
            {"heading_path": "Enumeration", "text": "x" * 30000, "url": "local"},
            {"heading_path": "Other", "text": "A short excerpt", "url": "local"},
        ]
        result = evaluate_generation(retriever, {"question": "Enumeration", "expect_headings": ["Enumeration"]})
        self.assertFalse(result["evidence_coverage"])
        self.assertEqual(result["validation"]["compilation_status"], "not_run")
        self.assertTrue(result["expert_review_required"])
        _chat_stream.assert_called_once()

    @patch("eval.run_eval.chat_stream")
    def test_expected_refusal_is_observed(self, chat_stream):
        retriever = MagicMock()
        retriever.search_generation.return_value = []
        result = evaluate_generation(retriever, {"question": "Missing", "expect_refusal": True})
        self.assertEqual(result["answer"], REFUSAL)
        self.assertTrue(result["refusal_matched"])
        self.assertIsNone(result["evidence_coverage"])
        chat_stream.assert_not_called()


if __name__ == "__main__":
    unittest.main()
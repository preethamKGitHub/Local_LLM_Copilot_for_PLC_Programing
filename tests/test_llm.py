import json
import unittest
from unittest.mock import MagicMock, patch

from plc_rag.llm import chat_stream


class StreamTests(unittest.TestCase):
    def stream(self, rows):
        response = MagicMock()
        response.iter_lines.return_value = [json.dumps(row) for row in rows]
        context = MagicMock()
        context.__enter__.return_value = response
        return patch("plc_rag.llm.httpx.stream", return_value=context)

    def test_last_packet_content_is_preserved(self):
        with self.stream([{"message": {"content": "last"}, "done": True, "done_reason": "stop"}]):
            self.assertEqual(list(chat_stream([])), ["last"])

    def test_limit_and_missing_done_are_errors(self):
        for rows in [[{"done": True, "done_reason": "length"}], [{"message": {"content": "partial"}}]]:
            with self.subTest(rows=rows), self.stream(rows), self.assertRaises(RuntimeError):
                list(chat_stream([]))


if __name__ == "__main__":
    unittest.main()
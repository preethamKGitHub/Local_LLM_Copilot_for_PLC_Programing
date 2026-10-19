import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from plc_rag.api import app
from plc_rag.validation import REFUSAL


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.hit = {"heading_path": "Class declaration", "text": "CLASS Motor END_CLASS", "url": "local"}

    def events(self, response):
        import json
        return [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: ")]

    @patch("plc_rag.api.chat_stream", return_value=iter(["```iecst\nCLASS Motor END_CLASS\n```\n[DOC 1]"]))
    @patch("plc_rag.api.retriever")
    def test_generate_event_order_and_sources(self, retriever, _chat_stream):
        retriever.return_value.search_generation.return_value = [self.hit]
        events = self.events(self.client.post("/chat", json={"question": "Create a class", "mode": "generate"}))
        self.assertEqual([event["type"] for event in events], ["sources", "token", "validation", "done"])
        self.assertEqual(events[2]["compilation_status"], "not_run")
        self.assertEqual(events[2]["status"], "passed_checks")
        self.assertEqual(events[0]["sources"][0]["n"], 1)
        retriever.return_value.search.assert_not_called()
        _chat_stream.assert_called_once()

    @patch("plc_rag.api.chat_stream")
    @patch("plc_rag.api.retriever")
    def test_no_evidence_refuses_without_model_call(self, retriever, chat_stream):
        retriever.return_value.search_generation.return_value = []
        events = self.events(self.client.post("/chat", json={"question": "Use unknown block", "mode": "generate"}))
        self.assertEqual(events[1]["text"], REFUSAL)
        self.assertEqual(events[2]["status"], "not_applicable")
        chat_stream.assert_not_called()

    @patch("plc_rag.api.chat_stream")
    @patch("plc_rag.api.retriever")
    def test_model_error_has_no_validation_success(self, retriever, chat_stream):
        def broken_stream():
            yield "```iecst\nCLASS Motor"
            raise RuntimeError("truncated")
        retriever.return_value.search_generation.return_value = [self.hit]
        chat_stream.return_value = broken_stream()
        events = self.events(self.client.post("/chat", json={"question": "class", "mode": "generate"}))
        self.assertEqual([event["type"] for event in events], ["sources", "token", "error", "done"])

    @patch("plc_rag.api.chat_stream", return_value=iter(["answer"]))
    @patch("plc_rag.api.retriever")
    def test_ask_unchanged(self, retriever, _chat_stream):
        retriever.return_value.search.return_value = [self.hit]
        events = self.events(self.client.post("/chat", json={"question": "class"}))
        self.assertEqual([event["type"] for event in events], ["sources", "token", "done"])
        retriever.return_value.search_generation.assert_not_called()
        _chat_stream.assert_called_once()

    @patch("plc_rag.api.retriever")
    def test_oversized_prompt_returns_422(self, retriever):
        retriever.return_value.search.return_value = []
        response = self.client.post("/chat", json={"question": "x" * 30000})
        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
import unittest
from unittest.mock import MagicMock, patch

from plc_rag.retriever import Retriever


class RetrieverTests(unittest.TestCase):
    def setUp(self):
        self.retriever = Retriever.__new__(Retriever)
        self.retriever.chunks = [
            {"heading_path": "Other", "text": "irrelevant", "url": "doc", "content_role": "rules"},
            {"heading_path": "Class declaration", "text": "CLASS Motor END_CLASS", "url": "doc", "content_role": "examples"},
            {"heading_path": "Class declaration", "text": "Only static VAR sections", "url": "doc"},
        ]
        self.retriever.bm25 = MagicMock()
        self.retriever.bm25.get_scores.return_value = [100, 3, 2]
        self.collection = MagicMock()
        self.collection.metadata = {}
        self.collection.query.return_value = {"ids": [["0", "2", "1"]]}
        self.retriever.col = self.collection

    @patch("plc_rag.retriever.embed", return_value=[[0.1]])
    def test_filter_preserves_global_ids_in_both_arms(self, _embed):
        hits = self.retriever.search("class", roles=("examples",), pool=1)
        self.assertEqual(hits, [self.retriever.chunks[1]])
        self.assertEqual(self.collection.query.call_args.kwargs["n_results"], 3)
        _embed.assert_called_once()

    @patch("plc_rag.retriever.embed", return_value=[[0.1]])
    def test_new_index_pushes_filter_to_vector_store(self, _embed):
        self.collection.metadata = {"evidence_roles": True}
        self.collection.query.return_value = {"ids": [["1"]]}
        self.retriever.search("class", roles=("examples",))
        self.assertEqual(self.collection.query.call_args.kwargs["where"], {"content_role": {"$in": ["examples"]}})
        self.assertEqual(self.collection.query.call_args.kwargs["n_results"], 1)
        _embed.assert_called_once()

    @patch("plc_rag.retriever.embed", return_value=[[0.1]])
    def test_legacy_missing_role_is_mixed(self, _embed):
        self.assertEqual(self.retriever.search("class", roles=("mixed",)), [self.retriever.chunks[2]])
        _embed.assert_called_once()

    def test_empty_filter_does_not_call_services(self):
        self.assertEqual(self.retriever.search("class", roles=("absent",)), [])
        self.collection.query.assert_not_called()

    def test_directed_evidence_deduplicated_and_capped(self):
        ordinary, example, rules = self.retriever.chunks
        with patch.object(self.retriever, "search", side_effect=[[ordinary, example], [rules, example]]):
            self.assertEqual(self.retriever.search_generation("Create a class", k=3), [rules, example, ordinary])

    def test_unknown_topic_uses_single_search(self):
        with patch.object(self.retriever, "search", return_value=[]) as search:
            self.assertEqual(self.retriever.search_generation("Missing library XYZ"), [])
            self.assertEqual(search.call_count, 1)


if __name__ == "__main__":
    unittest.main()
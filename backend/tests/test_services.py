"""Unit tests for deterministic service logic; no external model downloads."""
import tempfile
import unittest
from pathlib import Path
from app.services.parser import detect_file_type, extract_text
from app.services.rag import chunk_text
from app.services.llm import stream_response, NO_CONTEXT

class ParserAndRetrievalUnitTests(unittest.TestCase):
    def test_detects_supported_extensions_case_insensitively(self):
        self.assertEqual(detect_file_type("LECTURE.PDF"), "pdf")
        self.assertEqual(detect_file_type("notes.TXT"), "txt")
        self.assertEqual(detect_file_type("slides.pptx"), "pptx")

    def test_rejects_unsupported_legacy_binary_document(self):
        with self.assertRaises(ValueError):
            detect_file_type("old-format.doc")

    def test_extracts_utf8_text_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "notes.txt"
            path.write_text("Cellular respiration creates ATP.", encoding="utf-8")
            self.assertEqual(extract_text(str(path), "txt"), "Cellular respiration creates ATP.")

    def test_chunking_preserves_content_and_bounds_chunk_size(self):
        source = ("A sentence about learning. " * 180).strip()
        chunks = chunk_text(source)
        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(0 < len(part) <= 1200 for part in chunks))
        self.assertIn("A sentence about learning.", " ".join(chunks))

    def test_empty_retrieval_context_does_not_call_external_llm(self):
        self.assertEqual(list(stream_response("Question?", [], [])), [NO_CONTEXT])

if __name__ == "__main__":
    unittest.main(verbosity=2)

import importlib
import os
import sys
import unittest

# Ensure the project root (parent of tests/) is importable regardless of how
# the test is invoked (e.g. `python tests/test_imports.py`).
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


class ImportSafetyTests(unittest.TestCase):
    def test_core_modules_import(self):
        modules = [
            "app",
            "core.transcriber",
            "core.summarizer",
            "core.extractor",
            "core.rag_engine",
            "core.vector_store",
            "utils.audio_processor",
        ]
        for module_name in modules:
            with self.subTest(module=module_name):
                module = importlib.import_module(module_name)
                self.assertIsNotNone(module)


if __name__ == "__main__":
    unittest.main()


import importlib
import unittest


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

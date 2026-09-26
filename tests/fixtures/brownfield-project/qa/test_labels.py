import unittest
from legacy_app.labels import normalize_label


class LabelTests(unittest.TestCase):
    def test_normalizes_case_and_edges(self):
        self.assertEqual(normalize_label("  Existing Project  "), "existing project")


if __name__ == "__main__":
    unittest.main()

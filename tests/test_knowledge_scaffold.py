from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class KnowledgeScaffoldTest(unittest.TestCase):
    def test_knowledge_scaffold_structure_exists(self) -> None:
        expected_paths = [
            ROOT / "templates" / "knowledge.md",
            ROOT / "templates" / "method.md",
            ROOT / "tests" / "fixtures" / "example-markov-chain.md",
        ]

        missing = [str(path.relative_to(ROOT)) for path in expected_paths if not path.exists()]
        self.assertEqual([], missing, f"Missing expected scaffold paths: {missing}")


if __name__ == "__main__":
    unittest.main()

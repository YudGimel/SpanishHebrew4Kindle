import tempfile
from pathlib import Path
import unittest
import unicodedata

from spanish_hebrew_kindle.audit import audit
from spanish_hebrew_kindle.generator import archive_source, generate
from spanish_hebrew_kindle.importer import attach_spanish_forms, import_translation_export, read_entries, write_entries
from spanish_hebrew_kindle.validator import validate_entries, validate_source

FIXTURES = Path(__file__).parent / "fixtures"


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.entries = import_translation_export(FIXTURES / "translations.jsonl")
        attach_spanish_forms(self.entries, FIXTURES / "forms.jsonl")

    def test_representative_resolutions(self):
        lookup = validate_entries(self.entries)
        expected = {
            "casa": "casa", "casas": "casa", "hablar": "hablar", "hablo": "hablar",
            "habló": "hablar", "hablando": "hablar", "tener": "tener", "tuvo": "tener",
            "hacer": "hacer", "hizo": "hacer", "ser": "ser", "mejor": "mejor",
            "mejores": "mejor", "todavía": "todavía", "aunque": "aunque",
            "desarrollar": "desarrollar",
        }
        for form, lemma in expected.items():
            self.assertIn(lemma, lookup[form], form)
        self.assertEqual({"ser", "ir"}, set(lookup["fue"]))

    def test_unicode_duplicates_and_empty_values(self):
        for entry in self.entries.values():
            self.assertEqual(entry.headword, unicodedata.normalize("NFC", entry.headword))
            self.assertEqual(len(entry.senses), len(set(entry.senses)))
            self.assertTrue(all(s.strip() for s in entry.senses))
            self.assertTrue(any("\u0590" <= c <= "\u05ff" for s in entry.senses for c in s))
        self.assertIn("habló", self.entries["hablar"].forms)
        self.assertIn("todavía", self.entries)

    def test_roundtrip_and_generated_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "entries.jsonl"
            write_entries(self.entries, processed)
            loaded = read_entries(processed)
            self.assertEqual(set(self.entries), set(loaded))
            source = generate(loaded, root / "source", partition_size=3)
            validate_source(source)
            documents = sorted((source / "OEBPS").glob("dictionary-*.xhtml"))
            self.assertEqual(4, len(documents))
            xhtml = "".join(path.read_text(encoding="utf-8") for path in documents)
            self.assertIn('dir="rtl"', xhtml)
            self.assertIn('idx:iform value="habló"', xhtml)
            self.assertIn("בית", xhtml)
            report = audit(loaded)
            self.assertEqual(10, report.headwords)
            self.assertEqual(["ir", "ser"], report.required_resolutions["fue"])
            first = archive_source(source, root / "one.zip").read_bytes()
            second = archive_source(source, root / "two.zip").read_bytes()
            self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()

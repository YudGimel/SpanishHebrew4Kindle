import json
import tempfile
from pathlib import Path
import unittest
import unicodedata
import xml.etree.ElementTree as ET

from spanish_hebrew_kindle.audit import audit
from spanish_hebrew_kindle.generator import archive_source, generate
from spanish_hebrew_kindle.importer import attach_spanish_forms, import_translation_export, read_entries, write_entries
from spanish_hebrew_kindle.validator import validate_entries, validate_source

FIXTURES = Path(__file__).parent / "fixtures"
PROJECT_ROOT = Path(__file__).parents[1]


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

    def test_record_level_translations_are_grouped_by_sense(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "translations.jsonl"
            source.write_text(
                '{"word":"home","pos":"noun","senses":[{"glosses":["residence"]}],'
                '"translations":['
                '{"lang_code":"es","word":"casa","sense_index":1},'
                '{"lang_code":"he","word":"בית","sense_index":1},'
                '{"lang_code":"es","word":"hogar","sense":"family home"},'
                '{"lang_code":"he","word":"משפחה","sense":"family home"}]}' + "\n",
                encoding="utf-8",
            )
            entries = import_translation_export(source)
        self.assertEqual(["בית"], entries["casa"].senses)
        self.assertEqual(["משפחה"], entries["hogar"].senses)

    def test_spanish_forms_export_provenance(self):
        config = json.loads((PROJECT_ROOT / "config" / "sources.json").read_text(encoding="utf-8"))
        forms = config["spanish_forms"]
        self.assertIn("/dictionary/Spanish/", forms["url"])
        self.assertEqual("English Wiktionary (Spanish-language entries)", forms["source"])

    def test_roundtrip_and_generated_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            processed = root / "entries.jsonl"
            write_entries(self.entries, processed)
            loaded = read_entries(processed)
            self.assertEqual(set(self.entries), set(loaded))
            source = generate(loaded, root / "source", partition_size=3)
            validate_source(source)
            opf = ET.parse(source / "OEBPS" / "dictionary.opf")
            css = opf.find(
                './/{http://www.idpf.org/2007/opf}manifest/'
                '{http://www.idpf.org/2007/opf}item[@href="dictionary.css"]'
            )
            self.assertIsNotNone(css)
            self.assertEqual("text/css", css.get("media-type"))
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

    def test_validator_rejects_unmanifested_stylesheet(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = generate(self.entries, Path(tmp) / "source")
            opf_path = source / "OEBPS" / "dictionary.opf"
            opf_path.write_text(
                opf_path.read_text(encoding="utf-8").replace(
                    '<item id="dictionary-css" href="dictionary.css" media-type="text/css"/>', ""
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "dictionary.css"):
                validate_source(source)


if __name__ == "__main__":
    unittest.main()

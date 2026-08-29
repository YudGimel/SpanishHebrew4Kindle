from __future__ import annotations

from collections import defaultdict
from pathlib import Path
import xml.etree.ElementTree as ET

from .model import Entry, contains_hebrew


def validate_entries(entries: dict[str, Entry]) -> dict[str, list[str]]:
    errors = []
    forms: dict[str, list[str]] = defaultdict(list)
    for key, entry in entries.items():
        if key != entry.headword or not entry.headword:
            errors.append(f"invalid headword: {key!r}")
        if not entry.senses or any(not contains_hebrew(x) for x in entry.senses):
            errors.append(f"missing Hebrew definition: {key}")
        if len(entry.senses) != len(set(entry.senses)):
            errors.append(f"duplicate sense: {key}")
        forms[key].append(key)
        for form in entry.forms:
            forms[form].append(key)
    if errors:
        raise ValueError("\n".join(errors))
    return dict(forms)


def validate_source(directory: Path) -> None:
    opf = ET.parse(directory / "OEBPS" / "dictionary.opf")
    raw = (directory / "OEBPS" / "dictionary.opf").read_text(encoding="utf-8")
    for expected in ('<dc:type>dictionary</dc:type>', '<DictionaryInLanguage>es</DictionaryInLanguage>',
                     '<DictionaryOutLanguage>he</DictionaryOutLanguage>'):
        if expected not in raw:
            raise ValueError(f"missing metadata: {expected}")
    documents = sorted((directory / "OEBPS").glob("dictionary-*.xhtml"))
    if not documents:
        raise ValueError("dictionary contains no XHTML partitions")
    for document in documents:
        ET.parse(document)

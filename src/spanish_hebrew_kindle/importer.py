from __future__ import annotations

from collections import defaultdict
import gzip
import json
from pathlib import Path
from typing import Iterable, Iterator, TextIO

from .model import Entry, clean, contains_hebrew


def open_text(path: Path) -> TextIO:
    return gzip.open(path, "rt", encoding="utf-8") if path.suffix == ".gz" else path.open(encoding="utf-8")


def records(path: Path) -> Iterator[dict]:
    with open_text(path) as stream:
        for number, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{number}: malformed JSON: {exc}") from exc


def _terms(items: Iterable[dict], language: str) -> list[str]:
    result = []
    for item in items:
        if item.get("lang_code") == language or item.get("code") == language:
            word = clean(item.get("word", ""))
            if word:
                result.append(word)
    return list(dict.fromkeys(result))


def import_translation_export(path: Path) -> dict[str, Entry]:
    """Pair Spanish and Hebrew translations occurring in the same Wiktionary sense.

    Accepts Kaikki/Wiktextract English JSONL and a compact fixture schema. Pairing
    only terms in one sense avoids falsely combining unrelated translations.
    """
    entries: dict[str, Entry] = {}
    for record in records(path):
        pos = clean(record.get("pos", ""))
        senses = record.get("senses") or [record]
        for sense in senses:
            translations = sense.get("translations", [])
            spanish = _terms(translations, "es")
            hebrew = [x for x in _terms(translations, "he") if contains_hebrew(x)]
            if not spanish or not hebrew:
                continue
            definition = "; ".join(hebrew)
            for word in spanish:
                entry = entries.setdefault(word, Entry(word))
                entry.senses.append(definition)
                if pos:
                    entry.pos.add(pos)
    for entry in entries.values():
        entry.normalize()
    return entries


SKIP_FORM_TAGS = {"romanization", "alternative", "misspelling", "nonstandard"}


def attach_spanish_forms(entries: dict[str, Entry], path: Path) -> None:
    """Attach source-attested forms from a Spanish Wiktextract JSONL export."""
    for record in records(path):
        lemma = clean(record.get("word", ""))
        entry = entries.get(lemma)
        if not entry:
            continue
        for form_record in record.get("forms", []):
            tags = set(form_record.get("tags", []))
            if tags & SKIP_FORM_TAGS:
                continue
            form = clean(form_record.get("form", ""))
            if form and form != "-":
                entry.forms.add(form)
        entry.normalize()


def write_entries(entries: dict[str, Entry], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        for word in sorted(entries, key=lambda x: (x.casefold(), x)):
            entry = entries[word]
            json.dump({"headword": entry.headword, "senses": entry.senses,
                       "pos": sorted(entry.pos), "forms": sorted(entry.forms)},
                      stream, ensure_ascii=False, sort_keys=True)
            stream.write("\n")


def read_entries(path: Path) -> dict[str, Entry]:
    output = {}
    for item in records(path):
        entry = Entry(item["headword"], item.get("senses", []),
                      set(item.get("pos", [])), set(item.get("forms", [])))
        entry.normalize()
        if not entry.headword or not entry.senses:
            raise ValueError(f"invalid processed entry: {item!r}")
        output[entry.headword] = entry
    return output

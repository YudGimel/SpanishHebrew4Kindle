from __future__ import annotations

from dataclasses import dataclass, field
import unicodedata


def clean(value: str) -> str:
    """Return NFC text with whitespace collapsed and unsafe controls removed."""
    value = unicodedata.normalize("NFC", value or "")
    value = " ".join(value.split())
    return "".join(c for c in value if unicodedata.category(c) != "Cc")


def contains_hebrew(value: str) -> bool:
    return any("\u0590" <= c <= "\u05ff" for c in value)


@dataclass
class Entry:
    headword: str
    senses: list[str] = field(default_factory=list)
    pos: set[str] = field(default_factory=set)
    forms: set[str] = field(default_factory=set)

    def normalize(self) -> None:
        self.headword = clean(self.headword)
        self.senses = list(dict.fromkeys(clean(x) for x in self.senses if clean(x)))
        self.pos = {clean(x) for x in self.pos if clean(x)}
        self.forms = {clean(x) for x in self.forms if clean(x) and clean(x) != self.headword}

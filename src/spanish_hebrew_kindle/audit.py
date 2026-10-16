from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .model import Entry


REQUIRED = ("casa", "casas", "hablar", "hablo", "habló", "hablando", "tener",
            "tuvo", "hacer", "hizo", "ser", "fue", "mejor", "mejores",
            "todavía", "aunque", "desarrollar")


@dataclass(frozen=True)
class Audit:
    headwords: int
    senses: int
    attached_forms: int
    unique_lookup_forms: int
    ambiguous_lookup_forms: int
    parts_of_speech: dict[str, int]
    required_resolutions: dict[str, list[str]]


def audit(entries: dict[str, Entry]) -> Audit:
    lookups: dict[str, set[str]] = defaultdict(set)
    pos = Counter()
    for word, entry in entries.items():
        lookups[word].add(word)
        for form in entry.forms:
            lookups[form].add(word)
        pos.update(entry.pos or {"unknown"})
    return Audit(
        headwords=len(entries),
        senses=sum(len(entry.senses) for entry in entries.values()),
        attached_forms=sum(len(entry.forms) for entry in entries.values()),
        unique_lookup_forms=len(lookups),
        ambiguous_lookup_forms=sum(len(lemmas) > 1 for lemmas in lookups.values()),
        parts_of_speech=dict(sorted(pos.items())),
        required_resolutions={word: sorted(lookups.get(word, set())) for word in REQUIRED},
    )


def write_audit(entries: dict[str, Entry], path: Path) -> Audit:
    report = audit(entries)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report

#!/usr/bin/env python3
"""Quickly verify source schemas before starting a multi-gigabyte build."""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

from spanish_hebrew_kindle.importer import records, translation_groups
from spanish_hebrew_kindle.model import contains_hebrew


def inspect_translations(path: Path, limit: int) -> dict:
    counts = Counter()
    examples = []
    for number, record in enumerate(records(path), 1):
        counts["records"] += 1
        if record.get("lang_code") not in (None, "en"):
            counts["non_english_records"] += 1
            if number >= limit:
                break
            continue
        for translations in translation_groups(record):
            counts["translation_groups"] += 1
            spanish = [item.get("word") for item in translations
                       if item.get("lang_code", item.get("code")) == "es" and item.get("word")]
            hebrew = [item.get("word") for item in translations
                      if item.get("lang_code", item.get("code")) == "he"
                      and item.get("word") and contains_hebrew(item["word"])]
            if spanish:
                counts["senses_with_spanish"] += 1
            if hebrew:
                counts["senses_with_hebrew"] += 1
            if spanish and hebrew:
                counts["paired_senses"] += 1
                if len(examples) < 10:
                    examples.append({"pivot": record.get("word"), "spanish": spanish, "hebrew": hebrew})
        if number >= limit:
            break
    if not counts["records"]:
        raise ValueError(f"{path} contains no records")
    return {"counts": dict(counts), "examples": examples}


def inspect_forms(path: Path, limit: int) -> dict:
    counts = Counter()
    examples = []
    for number, record in enumerate(records(path), 1):
        counts["records"] += 1
        if record.get("lang_code") not in (None, "es"):
            counts["non_spanish_records"] += 1
            if number >= limit:
                break
            continue
        forms = [item.get("form") for item in record.get("forms", []) if item.get("form")]
        if forms:
            counts["records_with_forms"] += 1
            counts["forms"] += len(forms)
            if len(examples) < 10:
                examples.append({"lemma": record.get("word"), "forms": forms[:10]})
        if number >= limit:
            break
    if not counts["records"]:
        raise ValueError(f"{path} contains no records")
    return {"counts": dict(counts), "examples": examples}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--translations", type=Path, required=True)
    parser.add_argument("--forms", type=Path, required=True)
    parser.add_argument("--limit", type=int, default=100_000)
    parser.add_argument("--output", type=Path, default=Path("build/reports/source-inspection.json"))
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    report = {
        "translations": inspect_translations(args.translations, args.limit),
        "spanish_forms": inspect_forms(args.forms, args.limit),
        "records_limit_per_source": args.limit,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    print(f"report={args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

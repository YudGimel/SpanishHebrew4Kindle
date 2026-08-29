from __future__ import annotations

import argparse
from pathlib import Path

from .generator import generate
from .importer import attach_spanish_forms, import_translation_export, read_entries, write_entries
from .validator import validate_entries, validate_source


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a Spanish-Hebrew Kindle dictionary")
    sub = parser.add_subparsers(dest="command", required=True)
    build = sub.add_parser("build-source", help="import data and generate Kindle source")
    build.add_argument("--translations", type=Path, required=True)
    build.add_argument("--forms", type=Path, required=True)
    build.add_argument("--processed", type=Path, default=Path("data/processed/entries.jsonl"))
    build.add_argument("--output", type=Path, default=Path("build/kindle-source"))
    check = sub.add_parser("validate", help="validate processed data and generated source")
    check.add_argument("--processed", type=Path, default=Path("data/processed/entries.jsonl"))
    check.add_argument("--source", type=Path, default=Path("build/kindle-source"))
    args = parser.parse_args(argv)
    if args.command == "build-source":
        entries = import_translation_export(args.translations)
        attach_spanish_forms(entries, args.forms)
        validate_entries(entries)
        write_entries(entries, args.processed)
        generate(entries, args.output)
        validate_source(args.output)
        print(f"headwords={len(entries)} forms={sum(len(e.forms) for e in entries.values())}")
    else:
        entries = read_entries(args.processed)
        lookup = validate_entries(entries)
        validate_source(args.source)
        print(f"headwords={len(entries)} lookup_forms={len(lookup)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

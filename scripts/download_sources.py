#!/usr/bin/env python3
"""Download configured source snapshots without silently accepting partial files."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/sources.json"))
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, source in config.items():
        destination = args.output / f"{name}.jsonl"
        temporary = destination.with_suffix(".part")
        digest = hashlib.sha256()
        with urlopen(source["url"]) as response, temporary.open("wb") as stream:
            while chunk := response.read(1024 * 1024):
                stream.write(chunk)
                digest.update(chunk)
        expected = source["sha256"]
        actual = digest.hexdigest()
        if len(expected) == 64 and actual != expected:
            temporary.unlink()
            raise SystemExit(f"checksum mismatch for {name}: expected {expected}, got {actual}")
        temporary.replace(destination)
        print(f"{actual}  {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

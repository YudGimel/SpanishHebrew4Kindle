#!/usr/bin/env python3
"""Download configured source snapshots without silently accepting partial files."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen


def valid_checksum(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdefABCDEF" for c in value)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("config/sources.json"))
    parser.add_argument("--output", type=Path, default=Path("data/raw"))
    parser.add_argument("--allow-unpinned", action="store_true",
                        help="development only: accept sources without a configured SHA-256")
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)
    for name, source in config.items():
        expected = source["sha256"]
        if not valid_checksum(expected) and not args.allow_unpinned:
            raise SystemExit(f"{name} has no pinned SHA-256; set it or pass --allow-unpinned for an audit")
        filename = source.get("filename")
        if not filename or Path(filename).name != filename:
            raise SystemExit(f"{name} has an invalid filename: {filename!r}")
        destination = args.output / filename
        temporary = destination.with_name(destination.name + ".part")
        digest = hashlib.sha256()
        request = Request(source["url"], headers={"User-Agent": "SpanishHebrew4Kindle/0.1"})
        with urlopen(request) as response, temporary.open("wb") as stream:
            while chunk := response.read(1024 * 1024):
                stream.write(chunk)
                digest.update(chunk)
        actual = digest.hexdigest()
        if valid_checksum(expected) and actual.lower() != expected.lower():
            temporary.unlink()
            raise SystemExit(f"checksum mismatch for {name}: expected {expected}, got {actual}")
        temporary.replace(destination)
        print(f"{actual}  {destination}")
        source["downloaded_at"] = datetime.now(timezone.utc).isoformat()
        source["downloaded_sha256"] = actual
        source["bytes"] = destination.stat().st_size
    manifest = args.output / "manifest.json"
    manifest.write_text(json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"manifest={manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

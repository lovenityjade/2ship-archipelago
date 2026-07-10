#!/usr/bin/env python3
"""Build the distributable 2Ship APWorld container."""

from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "twoship"
OUTPUT = ROOT / "dist/twoship.apworld"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((SOURCE / "archipelago.json").read_text(encoding="utf-8"))
    manifest.update({"version": 7, "compatible_version": 7})

    with ZipFile(OUTPUT, "w", ZIP_DEFLATED) as archive:
        for path in sorted(SOURCE.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            archive_name = Path("twoship") / path.relative_to(SOURCE)
            if path.name == "archipelago.json":
                archive.writestr(str(archive_name), json.dumps(manifest, indent=2) + "\n")
            else:
                archive.write(path, str(archive_name))

    print(OUTPUT)


if __name__ == "__main__":
    main()

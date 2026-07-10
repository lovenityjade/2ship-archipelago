#!/usr/bin/env python3
"""Generate APWorld tables from 2Ship's canonical randomizer enums."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def enum_members(source: str, enum_name: str) -> list[str]:
    match = re.search(r"typedef enum \{(?P<body>[^}]*)\}\s*" + re.escape(enum_name) + r";", source, re.S)
    if not match:
        raise ValueError(f"could not find {enum_name}")
    members = []
    for raw_line in match.group("body").splitlines():
        line = raw_line.split("//", 1)[0].strip().rstrip(",")
        if line and re.fullmatch(r"[A-Z][A-Z0-9_]*", line):
            members.append(line)
    return members


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("2ship2harkinian"))
    parser.add_argument("--output", type=Path, default=Path("twoship/data.py"))
    args = parser.parse_args()

    types = (args.source / "mm/2s2h/Rando/Types.h").read_text(encoding="utf-8")
    checks_cpp = (args.source / "mm/2s2h/Rando/StaticData/Checks.cpp").read_text(encoding="utf-8")
    items_cpp = (args.source / "mm/2s2h/Rando/StaticData/Items.cpp").read_text(encoding="utf-8")

    check_ids = enum_members(types, "RandoCheckId")
    item_ids = enum_members(types, "RandoItemId")
    check_ordinals = {name: index for index, name in enumerate(check_ids)}
    item_ordinals = {name: index for index, name in enumerate(item_ids)}

    check_rows = {}
    for match in re.finditer(
        r"RC\((RC_[A-Z0-9_]+),\s*(RCTYPE_[A-Z0-9_]+),\s*[^,]+,\s*[^,]+,\s*[^,]+,\s*(RI_[A-Z0-9_]+)\)",
        checks_cpp,
    ):
        check_rows[match.group(1)] = (match.group(2), match.group(3))

    item_rows = {}
    for match in re.finditer(
        r'RI\((RI_[A-Z0-9_]+),\s*"[^"]*",\s*"[^"]*",\s*(RITYPE_[A-Z0-9_]+)',
        items_cpp,
    ):
        item_rows[match.group(1)] = match.group(2)

    checks = []
    for name in check_ids:
        if name in {"RC_UNKNOWN", "RC_MAX"} or name not in check_rows:
            continue
        check_type, vanilla_item = check_rows[name]
        checks.append((name, check_ordinals[name], check_type, vanilla_item))

    items = []
    for name in item_ids:
        if name in {"RI_UNKNOWN", "RI_MAX", "RI_MAX_TRAP"} or name not in item_rows:
            continue
        items.append((name, item_ordinals[name], item_rows[name]))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        output.write('"""Generated from 2Ship randomizer data. Do not edit by hand."""\n\n')
        output.write("CHECKS = (\n")
        for row in checks:
            output.write(f"    {row!r},\n")
        output.write(")\n\nITEMS = (\n")
        for row in items:
            output.write(f"    {row!r},\n")
        output.write(")\n")

    print(f"generated {len(checks)} checks and {len(items)} items in {args.output}")


if __name__ == "__main__":
    main()

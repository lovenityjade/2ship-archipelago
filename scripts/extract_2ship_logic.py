#!/usr/bin/env python3
"""Extract 2Ship's native glitchless region graph without interpreting C++."""

from __future__ import annotations

import argparse
import pprint
import re
from dataclasses import dataclass
from pathlib import Path


MACROS = ("CHECK", "CONNECTION", "EVENT", "EXIT", "STAY")

# These three one-way destinations have no reverse entrance registered in the
# native table, so GetRegionIdFromEntrance relies on the game entrance map.
ONE_WAY_DESTINATIONS = {
    "ENTRANCE(WOODFALL, 4)": "RR_WOODFALL_OWL_STATUE_PLATFORM",
    "ENTRANCE(MOUNTAIN_VILLAGE_SPRING, 7)": "RR_MOUNTAIN_VILLAGE",
    "ENTRANCE(ZORA_HALL, 1)": "RR_ZORA_HALL",
}


def skip_ignored(source: str, index: int) -> int:
    if source.startswith("//", index):
        end = source.find("\n", index + 2)
        return len(source) if end < 0 else end + 1
    if source.startswith("/*", index):
        end = source.find("*/", index + 2)
        if end < 0:
            raise ValueError("unterminated block comment")
        return end + 2
    if source[index] in {'"', "'"}:
        quote = source[index]
        index += 1
        while index < len(source):
            if source[index] == "\\":
                index += 2
            elif source[index] == quote:
                return index + 1
            else:
                index += 1
        raise ValueError("unterminated string literal")
    return index


def matching_delimiter(source: str, start: int, opening: str, closing: str) -> int:
    depth = 0
    index = start
    while index < len(source):
        skipped = skip_ignored(source, index)
        if skipped != index:
            index = skipped
            continue
        char = source[index]
        if char == opening:
            depth += 1
        elif char == closing:
            depth -= 1
            if depth == 0:
                return index
        index += 1
    raise ValueError(f"unterminated {opening}{closing} block at offset {start}")


def split_arguments(arguments: str) -> list[str]:
    result: list[str] = []
    start = 0
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    index = 0
    while index < len(arguments):
        skipped = skip_ignored(arguments, index)
        if skipped != index:
            index = skipped
            continue
        char = arguments[index]
        if char in pairs:
            stack.append(pairs[char])
        elif stack and char == stack[-1]:
            stack.pop()
        elif char == "," and not stack:
            result.append(normalize(arguments[start:index]))
            start = index + 1
        index += 1
    result.append(normalize(arguments[start:]))
    return result


def normalize(value: str) -> str:
    value = re.sub(r"//[^\n]*", " ", value)
    value = re.sub(r"/\*.*?\*/", " ", value, flags=re.S)
    return re.sub(r"\s+", " ", value).strip()


def macro_calls(source: str, macro: str) -> list[list[str]]:
    calls: list[list[str]] = []
    pattern = re.compile(r"\b" + re.escape(macro) + r"\s*\(")
    index = 0
    while match := pattern.search(source, index):
        # A macro name inside a comment is ignored by walking from the previous
        # cursor and checking whether the match is crossed by an ignored span.
        cursor = index
        ignored = False
        while cursor < match.start():
            skipped = skip_ignored(source, cursor)
            if skipped != cursor:
                if skipped > match.start():
                    ignored = True
                    break
                cursor = skipped
            else:
                cursor += 1
        if ignored:
            index = skipped
            continue
        opening = source.find("(", match.start(), match.end())
        closing = matching_delimiter(source, opening, "(", ")")
        calls.append(split_arguments(source[opening + 1:closing]))
        index = closing + 1
    return calls


@dataclass(frozen=True)
class RegionSource:
    symbol: str
    body: str
    source_file: str


def region_blocks(source: str, source_file: str) -> list[RegionSource]:
    blocks: list[RegionSource] = []
    pattern = re.compile(r"Regions\[(RR_[A-Z0-9_]+)\]\s*=\s*RandoRegion\s*\{")
    index = 0
    while match := pattern.search(source, index):
        opening = source.find("{", match.start(), match.end())
        closing = matching_delimiter(source, opening, "{", "}")
        blocks.append(RegionSource(match.group(1), source[opening + 1:closing], source_file))
        index = closing + 1
    return blocks


def extract_set_field(body: str, field: str) -> list[str]:
    match = re.search(r"\." + re.escape(field) + r"\s*=\s*\{", body)
    if not match:
        return []
    opening = body.find("{", match.start(), match.end())
    closing = matching_delimiter(body, opening, "{", "}")
    return [value for value in split_arguments(body[opening + 1:closing]) if value]


def enum_members(source: str, enum_name: str) -> list[str]:
    match = re.search(r"typedef enum \{(?P<body>[^}]*)\}\s*" + re.escape(enum_name) + r";", source, re.S)
    if not match:
        raise ValueError(f"could not find {enum_name}")
    return re.findall(r"^\s*(R[RCIE]_[A-Z0-9_]+)\s*,?", match.group("body"), re.M)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path("2ship2harkinian"))
    parser.add_argument("--output", type=Path, default=Path("twoship/logic_data.py"))
    args = parser.parse_args()

    logic_root = args.source / "mm/2s2h/Rando/Logic"
    paths = [logic_root / "Logic.cpp", *sorted((logic_root / "Regions").glob("*.cpp"))]
    blocks: list[RegionSource] = []
    for path in paths:
        blocks.extend(region_blocks(path.read_text(encoding="utf-8"), str(path.relative_to(args.source))))

    if len(blocks) != 315:
        raise ValueError(f"expected 315 native regions, extracted {len(blocks)}")
    if len({block.symbol for block in blocks}) != len(blocks):
        raise ValueError("duplicate native region definitions")

    types_source = (args.source / "mm/2s2h/Rando/Types.h").read_text(encoding="utf-8")
    region_order = {symbol: index for index, symbol in enumerate(enum_members(types_source, "RandoRegionId"))}
    blocks.sort(key=lambda block: region_order[block.symbol])

    entrance_to_region: dict[str, str] = {}
    for block in blocks:
        for args_ in macro_calls(block.body, "EXIT"):
            if len(args_) != 3:
                raise ValueError(f"invalid EXIT in {block.symbol}: {args_}")
            if args_[1] != "ONE_WAY_EXIT":
                entrance_to_region[args_[1]] = block.symbol
        for entrance in extract_set_field(block.body, "oneWayEntrances"):
            entrance_to_region[entrance] = block.symbol

    regions: dict[str, dict] = {}
    unresolved_exits: set[str] = set()
    totals = {macro.lower(): 0 for macro in MACROS}
    for block in blocks:
        checks = []
        for args_ in macro_calls(block.body, "CHECK"):
            checks.append(tuple(args_))
        connections = []
        for args_ in macro_calls(block.body, "CONNECTION"):
            connections.append(tuple(args_))
        events = []
        for args_ in macro_calls(block.body, "EVENT"):
            events.append(tuple(args_))
        stays = []
        for args_ in macro_calls(block.body, "STAY"):
            stays.append(tuple(args_))
        exits = []
        for args_ in macro_calls(block.body, "EXIT"):
            target = entrance_to_region.get(args_[0], ONE_WAY_DESTINATIONS.get(args_[0]))
            if target is None:
                unresolved_exits.add(args_[0])
            exits.append((target, args_[0], args_[1], args_[2]))

        for name, values in (("check", checks), ("connection", connections), ("event", events),
                             ("exit", exits), ("stay", stays)):
            totals[name] += len(values)
        name_match = re.search(r'\.name\s*=\s*"([^"]*)"', block.body)
        regions[block.symbol] = {
            "name": name_match.group(1) if name_match else block.symbol,
            "source": block.source_file,
            "checks": tuple(checks),
            "connections": tuple(connections),
            "events": tuple(events),
            "exits": tuple(exits),
            "stays": tuple(stays),
        }

    if unresolved_exits:
        raise ValueError(f"unresolved exit destinations: {sorted(unresolved_exits)}")
    expected_totals = {"check": 2478, "connection": 388, "event": 117, "exit": 326, "stay": 37}
    if totals != expected_totals:
        raise ValueError(f"native logic count changed: expected {expected_totals}, extracted {totals}")

    logic_header = (logic_root / "Logic.h").read_text(encoding="utf-8")
    time_body = re.search(r"enum TimeSlice\s*\{(.*?)\};", logic_header, re.S)
    if not time_body:
        raise ValueError("could not extract TimeSlice")
    time_slices = tuple(re.findall(r"\b(TIME_[A-Z0-9_]+)\b", time_body.group(1)))

    kill_switch = re.search(r"inline bool CanKillEnemy\(.*?switch \(EnemyId\)\s*\{", logic_header, re.S)
    if not kill_switch:
        raise ValueError("could not extract CanKillEnemy")
    kill_opening = logic_header.find("{", kill_switch.start() + kill_switch.group(0).rfind("switch"))
    kill_closing = matching_delimiter(logic_header, kill_opening, "{", "}")
    kill_body = logic_header[kill_opening + 1:kill_closing]
    enemy_rules: dict[str, str] = {}
    pending_actors: list[str] = []
    token = re.compile(r"case\s+(ACTOR_[A-Z0-9_]+)\s*:|return\s+(.*?);", re.S)
    for match in token.finditer(kill_body):
        if match.group(1):
            pending_actors.append(match.group(1))
        elif pending_actors:
            condition = normalize(match.group(2))
            for actor in pending_actors:
                enemy_rules[actor] = condition
            pending_actors.clear()

    souls_cpp = (args.source / "mm/2s2h/Rando/ActorBehavior/Souls.cpp").read_text(encoding="utf-8")
    enemy_souls = dict(re.findall(r"\{\s*(ACTOR_[A-Z0-9_]+)\s*,\s*(RI_SOUL_[A-Z0-9_]+)\s*\}", souls_cpp))
    if len(time_slices) != 45 or len(enemy_rules) != 64 or len(enemy_souls) != 64:
        raise ValueError("native time or enemy logic count changed")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="\n") as output:
        output.write('"""Generated from 2Ship native glitchless logic. Do not edit by hand."""\n\n')
        output.write("REGIONS = ")
        output.write(pprint.pformat(regions, width=140, sort_dicts=False))
        output.write("\n\nCOUNTS = ")
        output.write(repr({"regions": len(regions), **totals}))
        output.write("\n\nTIME_SLICES = ")
        output.write(repr(time_slices))
        output.write("\n\nENEMY_RULES = ")
        output.write(pprint.pformat(enemy_rules, width=140, sort_dicts=False))
        output.write("\n\nENEMY_SOULS = ")
        output.write(pprint.pformat(enemy_souls, width=140, sort_dicts=False))
        output.write("\n")

    print(f"generated {len(regions)} regions in {args.output}: {totals}")


if __name__ == "__main__":
    main()

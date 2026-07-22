from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable

from BaseClasses import CollectionState

from .data import CHECKS, ITEMS
from .logic_data import ENEMY_RULES, ENEMY_SOULS, REGIONS, TIME_SLICES


Rule = Callable[[CollectionState], bool]
EVENT_PREFIX = "2Ship Event: "
REGION_PREFIX = "2Ship Region: "

RI_NAMES = {symbol: symbol.removeprefix("RI_").replace("_", " ").title()
            for symbol, _, _, _ in ITEMS}
CHECK_SYMBOL_TO_ID = {symbol: ordinal for symbol, ordinal, _, _ in CHECKS}
NATIVE_ITEMS: dict[str, set[str]] = defaultdict(set)
for symbol, _, _, native_item in ITEMS:
    if native_item != "ITEM_NONE":
        NATIVE_ITEMS[native_item].add(symbol)

TIME_INDEX = {name: index for index, name in enumerate(TIME_SLICES)}
HALF_DAYS = ((0, 6), (7, 15), (16, 22), (23, 30), (31, 36), (37, 44))

SONGS = {
    "SONATA": "RI_SONG_SONATA", "LULLABY": "RI_SONG_LULLABY", "LULLABY_INTRO": "RI_SONG_LULLABY_INTRO",
    "BOSSA_NOVA": "RI_SONG_NOVA", "ELEGY": "RI_SONG_ELEGY", "OATH": "RI_SONG_OATH",
    "TIME": "RI_SONG_TIME", "HEALING": "RI_SONG_HEALING", "EPONA": "RI_SONG_EPONA",
    "SOARING": "RI_SONG_SOARING", "STORMS": "RI_SONG_STORMS",
}
SONG_BUTTONS = {
    "SONATA": ("C_UP", "C_LEFT", "A", "C_RIGHT"),
    "LULLABY": ("A", "C_RIGHT", "C_LEFT"), "LULLABY_INTRO": ("A", "C_RIGHT", "C_LEFT"),
    "BOSSA_NOVA": ("C_LEFT", "C_UP", "C_RIGHT", "C_DOWN"),
    "ELEGY": ("C_LEFT", "C_UP", "C_RIGHT", "C_DOWN"),
    "OATH": ("C_RIGHT", "C_LEFT", "C_DOWN", "A", "C_UP"),
    "TIME": ("C_RIGHT", "A", "C_DOWN"), "HEALING": ("C_LEFT", "C_RIGHT", "C_DOWN"),
    "EPONA": ("C_UP", "C_LEFT", "C_RIGHT"), "SOARING": ("C_DOWN", "C_LEFT", "C_UP"),
    "STORMS": ("A", "C_DOWN", "C_UP"),
}
OCARINA_SONG_ALIASES = {
    "OCARINA_SONG_EVAN_PART1": "TIME", "OCARINA_SONG_EVAN_PART2": "HEALING",
    "OCARINA_SONG_WIND_FISH_DEKU": "WIND_FISH_DEKU", "OCARINA_SONG_WIND_FISH_GORON": "TIME",
    "OCARINA_SONG_WIND_FISH_HUMAN": "EPONA", "OCARINA_SONG_WIND_FISH_ZORA": "OATH",
}
SONG_BUTTONS["WIND_FISH_DEKU"] = ("C_RIGHT", "A", "C_DOWN", "C_LEFT")

MASK_ITEMS = tuple(symbol for symbol in RI_NAMES if symbol.startswith("RI_MASK_") and symbol not in {
    "RI_MASK_DEKU", "RI_MASK_GORON", "RI_MASK_ZORA", "RI_MASK_FIERCE_DEITY",
})
REMAINS = ("RI_REMAINS_ODOLWA", "RI_REMAINS_GOHT", "RI_REMAINS_GYORG", "RI_REMAINS_TWINMOLD")
DUNGEON_NAMES = {
    "DUNGEON_SCENE_INDEX_WOODFALL_TEMPLE": "WOODFALL",
    "DUNGEON_SCENE_INDEX_SNOWHEAD_TEMPLE": "SNOWHEAD",
    "DUNGEON_SCENE_INDEX_GREAT_BAY_TEMPLE": "GREAT_BAY",
    "DUNGEON_SCENE_INDEX_STONE_TOWER_TEMPLE": "STONE_TOWER",
}
INF_ITEMS = {
    "RANDO_INF_OBTAINED_MOONS_TEAR": "RI_MOONS_TEAR",
    "RANDO_INF_OBTAINED_DEED_LAND": "RI_DEED_LAND", "RANDO_INF_OBTAINED_DEED_SWAMP": "RI_DEED_SWAMP",
    "RANDO_INF_OBTAINED_DEED_MOUNTAIN": "RI_DEED_MOUNTAIN", "RANDO_INF_OBTAINED_DEED_OCEAN": "RI_DEED_OCEAN",
    "RANDO_INF_OBTAINED_LETTER_TO_KAFEI": "RI_LETTER_TO_KAFEI",
    "RANDO_INF_OBTAINED_LETTER_TO_MAMA": "RI_LETTER_TO_MAMA",
    "RANDO_INF_OBTAINED_PENDANT_OF_MEMORIES": "RI_PENDANT_OF_MEMORIES",
    "RANDO_INF_OBTAINED_ROOM_KEY": "RI_ROOM_KEY",
    "RANDO_INF_OBTAINED_SOUL_OF_ENEMY_OCTOROKS": "RI_SOUL_ENEMY_OCTOROK",
}
OWL_ITEMS = {
    "OWL_WARP_CLOCK_TOWN": "RI_OWL_CLOCK_TOWN_SOUTH", "OWL_WARP_SOUTHERN_SWAMP": "RI_OWL_SOUTHERN_SWAMP",
    "OWL_WARP_WOODFALL": "RI_OWL_WOODFALL", "OWL_WARP_MILK_ROAD": "RI_OWL_MILK_ROAD",
    "OWL_WARP_MOUNTAIN_VILLAGE": "RI_OWL_MOUNTAIN_VILLAGE", "OWL_WARP_SNOWHEAD": "RI_OWL_SNOWHEAD",
    "OWL_WARP_GREAT_BAY_COAST": "RI_OWL_GREAT_BAY_COAST", "OWL_WARP_ZORA_CAPE": "RI_OWL_ZORA_CAPE",
    "OWL_WARP_IKANA_CANYON": "RI_OWL_IKANA_CANYON", "OWL_WARP_STONE_TOWER": "RI_OWL_STONE_TOWER",
}


def _python_expression(expression: str) -> str:
    expression = expression.replace("&&", " and ").replace("||", " or ")
    expression = re.sub(r"!(?!=)", " not ", expression)
    expression = re.sub(r"\btrue\b", "True", expression)
    expression = re.sub(r"\bfalse\b", "False", expression)
    return expression.strip()


ALL_EXPRESSIONS = []
EVENT_SYMBOLS = set()
for region in REGIONS.values():
    for field in ("checks", "connections", "events", "stays"):
        ALL_EXPRESSIONS.extend(row[-1] for row in region[field])
    ALL_EXPRESSIONS.extend(row[-1] for row in region["exits"])
    EVENT_SYMBOLS.update(row[0] for row in region["events"])
ALL_EXPRESSIONS.extend(ENEMY_RULES.values())
COMPILED = {expression: compile(_python_expression(expression), "<2Ship native logic>", "eval")
            for expression in set(ALL_EXPRESSIONS)}
EXPRESSION_CONSTANTS = {
    expression: {token: token for token in re.findall(r"\b[A-Z][A-Z0-9_]*\b", expression)}
    for expression in COMPILED
}


class _LazyEventCounts(dict[str, int]):
    def __init__(self, state: CollectionState, player: int):
        super().__init__()
        self.state = state
        self.player = player

    def __missing__(self, event: str) -> int:
        value = self.state.count(EVENT_PREFIX + event, self.player)
        self[event] = value
        return value


class _LazyEnvironment(dict[str, object]):
    def __init__(self, values: dict[str, object], providers: dict[str, Callable[[], object]]):
        super().__init__(values)
        self.providers = providers

    def __missing__(self, name: str) -> object:
        provider = self.providers.get(name)
        if provider is None:
            raise KeyError(name)
        value = provider()
        self[name] = value
        return value


class NativeLogic:
    def __init__(self, player: int, options, shop_prices: dict[int, int] | None = None):
        self.player = player
        self.options = options
        self.shop_prices = shop_prices or {}

    def has_ri(self, state: CollectionState, symbol: str, count: int = 1) -> bool:
        if symbol == "RI_SONG_LULLABY_INTRO":
            return state.has(RI_NAMES["RI_PROGRESSIVE_LULLABY"], self.player, count) or state.has(
                RI_NAMES[symbol], self.player, count)
        if symbol == "RI_SONG_LULLABY":
            return state.has(RI_NAMES["RI_PROGRESSIVE_LULLABY"], self.player, count + 1) or state.has(
                RI_NAMES[symbol], self.player, count)
        name = RI_NAMES.get(symbol)
        return bool(name and state.has(name, self.player, count))

    def count_ri(self, state: CollectionState, symbol: str) -> int:
        name = RI_NAMES.get(symbol)
        return state.count(name, self.player) if name else 0

    def event_count(self, state: CollectionState, event: str) -> int:
        return state.count(EVENT_PREFIX + event, self.player)

    def progressive_count(self, state: CollectionState, progressive: str, *concrete: str) -> int:
        return self.count_ri(state, progressive) + sum(self.count_ri(state, item) for item in concrete)

    def sword_level(self, state: CollectionState) -> int:
        return self.progressive_count(state, "RI_PROGRESSIVE_SWORD", "RI_SWORD_KOKIRI", "RI_SWORD_RAZOR", "RI_SWORD_GILDED")

    def shield_level(self, state: CollectionState) -> int:
        if self.has_ri(state, "RI_SHIELD_MIRROR"):
            return 2
        return int(self.has_ri(state, "RI_SHIELD_HERO"))

    def wallet_level(self, state: CollectionState) -> int:
        return self.progressive_count(state, "RI_PROGRESSIVE_WALLET", "RI_WALLET_ADULT", "RI_WALLET_GIANT", "RI_WALLET_TYCOON")

    def bow_level(self, state: CollectionState) -> int:
        return self.progressive_count(state, "RI_PROGRESSIVE_BOW", "RI_BOW", "RI_QUIVER_40", "RI_QUIVER_50")

    def bomb_level(self, state: CollectionState) -> int:
        return self.progressive_count(state, "RI_PROGRESSIVE_BOMB_BAG", "RI_BOMB_BAG_20", "RI_BOMB_BAG_30", "RI_BOMB_BAG_40")

    def magic(self, state: CollectionState) -> bool:
        return self.progressive_count(state, "RI_PROGRESSIVE_MAGIC", "RI_SINGLE_MAGIC", "RI_DOUBLE_MAGIC") > 0

    def bottle(self, state: CollectionState) -> bool:
        return any(self.has_ri(state, symbol) for symbol in RI_NAMES if symbol.startswith("RI_BOTTLE_"))

    def has_item(self, state: CollectionState, item: str) -> bool:
        if item == "ITEM_BOW":
            return self.bow_level(state) > 0
        if item in {"ITEM_BOMB", "ITEM_BOMBCHU"}:
            return self.bomb_level(state) > 0 or self.has_ri(state, "RI_BOMBCHU")
        if item == "ITEM_DEKU_STICK":
            return bool(self.options.starting_consumables.value or self.has_ri(state, "RI_DEKU_STICK"))
        if item == "ITEM_DEKU_NUT":
            return bool(self.options.starting_consumables.value or self.has_ri(state, "RI_DEKU_NUT"))
        return any(self.has_ri(state, symbol) for symbol in NATIVE_ITEMS.get(item, ()))

    def ocarina_buttons(self, state: CollectionState, song: str) -> bool:
        song = OCARINA_SONG_ALIASES.get(song, song.removeprefix("OCARINA_SONG_"))
        buttons = SONG_BUTTONS.get(song, ())
        if not self.options.shuffle_ocarina_buttons.value:
            return True
        return all(self.has_ri(state, "RI_OCARINA_BUTTON_" + button) for button in buttons)

    def can_play_song(self, state: CollectionState, song: str) -> bool:
        symbol = SONGS.get(song)
        if not symbol or not self.has_item(state, "ITEM_OCARINA_OF_TIME") or not self.has_ri(state, symbol):
            return False
        return self.ocarina_buttons(state, song)

    def half_days(self, state: CollectionState) -> tuple[bool, ...]:
        if not self.options.shuffle_time.value:
            return (True,) * 6
        if self.options.clock_progression.value == 0:
            symbols = ("RI_TIME_DAY_1", "RI_TIME_NIGHT_1", "RI_TIME_DAY_2", "RI_TIME_NIGHT_2",
                       "RI_TIME_DAY_3", "RI_TIME_NIGHT_3")
            return tuple(self.has_ri(state, symbol) for symbol in symbols)
        count = self.count_ri(state, "RI_TIME_PROGRESSIVE")
        if self.options.clock_progression.value == 1:
            return tuple(index < count for index in range(6))
        return tuple(index >= 6 - count for index in range(6))

    def time_mask(self, state: CollectionState) -> int:
        mask = 0
        for owned, (start, end) in zip(self.half_days(state), HALF_DAYS):
            if owned:
                for index in range(start, end + 1):
                    mask |= 1 << index
        return mask

    def can_afford(self, state: CollectionState, check: str) -> bool:
        check_id = CHECK_SYMBOL_TO_ID.get(check)
        price = self.shop_prices.get(check_id, 0) if check_id is not None else 0
        wallet = self.wallet_level(state)
        return price < 100 or price <= 200 and wallet >= 1 or wallet >= 2

    def time_range(self, state: CollectionState, start: int, end: int) -> bool:
        return bool(self.time_mask(state) & sum(1 << index for index in range(start, end)))

    def remains_count(self, state: CollectionState) -> int:
        return sum(self.has_ri(state, item) for item in REMAINS)

    def mask_count(self, state: CollectionState) -> int:
        return sum(self.has_ri(state, item) for item in MASK_ITEMS)

    def key_count(self, state: CollectionState, dungeon: str) -> int:
        if self.has_ri(state, "RI_SKELETON_KEY"):
            return 99
        return self.count_ri(state, f"RI_{dungeon.removesuffix('_TEMPLE')}_SMALL_KEY")

    def can_access_dungeon(self, state: CollectionState, dungeon_index: str) -> bool:
        dungeon = DUNGEON_NAMES[dungeon_index]
        song, form = {
            "WOODFALL": ("SONATA", "RI_MASK_DEKU"), "SNOWHEAD": ("LULLABY", "RI_MASK_GORON"),
            "GREAT_BAY": ("BOSSA_NOVA", "RI_MASK_ZORA"),
        }.get(dungeon, (None, None))
        if song is None:
            return False
        song_access = self.can_play_song(state, song)
        form_access = self.has_ri(state, form) and self.has_item(state, "ITEM_OCARINA_OF_TIME")
        mode = self.options.dungeon_access.value
        return ((form_access and song_access) if mode == 0 else (form_access or song_access) if mode == 1
                else form_access if mode == 2 else song_access if mode == 3 else True)

    def can_kill_enemy(self, state: CollectionState, actor: str) -> bool:
        if self.options.shuffle_enemy_souls.value:
            soul = ENEMY_SOULS.get(actor)
            if soul and not self.has_ri(state, soul):
                return False
        boss_souls = {
            "ACTOR_BOSS_01": "RI_SOUL_BOSS_ODOLWA", "ACTOR_BOSS_HAKUGIN": "RI_SOUL_BOSS_GOHT",
            "ACTOR_BOSS_03": "RI_SOUL_BOSS_GYORG", "ACTOR_BOSS_02": "RI_SOUL_BOSS_TWINMOLD",
        }
        soul = boss_souls.get(actor)
        if soul and self.options.shuffle_boss_souls.value and not self.has_ri(state, soul):
            return False
        expression = ENEMY_RULES.get(actor)
        return bool(expression and self.evaluate(state, expression))

    def has_rando_inf(self, state: CollectionState, flag: str) -> bool:
        if flag.startswith("RANDO_INF_OBTAINED_SOUL_OF_ENEMY_") and not self.options.shuffle_enemy_souls.value:
            return True
        if flag.startswith("RANDO_INF_OBTAINED_SOUL_OF_BOSS_") and not self.options.shuffle_boss_souls.value:
            return True
        if flag.startswith("RANDO_INF_OBTAINED_SOUL_OF_BOSS_"):
            return self.has_ri(state, "RI_SOUL_BOSS_" + flag.removeprefix("RANDO_INF_OBTAINED_SOUL_OF_BOSS_"))
        return self.has_ri(state, INF_ITEMS.get(flag, ""))

    def evaluate(self, state: CollectionState, expression: str) -> bool:
        events = _LazyEventCounts(state, self.player)
        half_days_value: tuple[bool, ...] | None = None
        time_mask_value: int | None = None

        def half_days() -> tuple[bool, ...]:
            nonlocal half_days_value
            if half_days_value is None:
                half_days_value = self.half_days(state)
            return half_days_value

        def time_mask() -> int:
            nonlocal time_mask_value
            if time_mask_value is None:
                time_mask_value = 0
                for owned, (start, end) in zip(half_days(), HALF_DAYS):
                    if owned:
                        for index in range(start, end + 1):
                            time_mask_value |= 1 << index
            return time_mask_value

        def time_range(start: int, end: int) -> bool:
            return bool(time_mask() & sum(1 << index for index in range(start, end)))

        option_values = {
            "RO_ACCESS_MAJORA_MASKS_COUNT": self.options.majora_masks_required.value,
            "RO_ACCESS_MAJORA_REMAINS_COUNT": self.options.majora_remains_required.value,
            "RO_ACCESS_TRIALS": self.options.trials_access.value,
            "RO_SHUFFLE_BOSS_SOULS": self.options.shuffle_boss_souls.value,
        }
        providers: dict[str, Callable[[], object]] = {
            "HAS_MAGIC": lambda: self.magic(state),
            "HAS_BOTTLE": lambda: self.bottle(state),
            "CAN_BE_DEKU": lambda: self.has_ri(state, "RI_MASK_DEKU"),
            "CAN_BE_GORON": lambda: self.has_ri(state, "RI_MASK_GORON"),
            "CAN_BE_ZORA": lambda: self.has_ri(state, "RI_MASK_ZORA"),
            "CAN_BE_DEITY": lambda: self.has_ri(state, "RI_MASK_FIERCE_DEITY"),
            "CAN_USE_HUMAN_SWORD": lambda: self.sword_level(state) > 0,
            "CAN_USE_SWORD": lambda: self.sword_level(state) > 0 or self.has_ri(
                state, "RI_GREAT_FAIRY_SWORD") or self.has_ri(state, "RI_MASK_FIERCE_DEITY"),
            "CAN_USE_EXPLOSIVE": lambda: self.bomb_level(state) > 0 or (
                self.has_ri(state, "RI_MASK_BLAST") and self.shield_level(state) > 0),
            "CAN_USE_PROJECTILE": lambda: self.bow_level(state) > 0 or self.has_ri(
                state, "RI_HOOKSHOT") or self.has_ri(state, "RI_MASK_DEKU") and bool(env["HAS_MAGIC"]) or
                self.has_ri(state, "RI_MASK_ZORA"),
            "CAN_RIDE_EPONA": lambda: self.can_play_song(state, "EPONA"),
            "CAN_HOOK_SCARECROW": lambda: self.has_ri(state, "RI_OCARINA") and self.has_ri(
                state, "RI_HOOKSHOT") and sum(self.has_ri(state, "RI_OCARINA_BUTTON_" + button)
                                               for button in ("A", "C_DOWN", "C_RIGHT", "C_LEFT", "C_UP")) >=
                (2 if self.options.shuffle_ocarina_buttons.value else 0),
            "CAN_LIGHT_TORCH_NEAR_ANOTHER": lambda: self.has_item(state, "ITEM_DEKU_STICK") or (
                self.bow_level(state) > 0 and self.has_ri(state, "RI_ARROW_FIRE") and bool(env["HAS_MAGIC"])),
            "CAN_TRAVERSE_WAIST_DEEP_WATER": lambda: not self.options.shuffle_swim.value or self.has_ri(
                state, "RI_ABILITY_SWIM") or self.has_ri(state, "RI_MASK_DEKU") or self.has_ri(
                state, "RI_MASK_ZORA") or self.has_ri(state, "RI_MASK_GORON"),
            "CAN_GROW_BEAN_PLANT": lambda: self.has_ri(state, "RI_MAGIC_BEAN") and (
                self.can_play_song(state, "STORMS") or bool(env["HAS_BOTTLE"]) and (
                    events["RE_ACCESS_SPRING_WATER"] or events["RE_ACCESS_HOT_SPRING_WATER"])),
            "CAN_USE_DAY2_RAIN_BEAN": lambda: self.has_ri(state, "RI_MAGIC_BEAN") and (
                self.can_play_song(state, "STORMS") or bool(env["HAS_BOTTLE"]) and (
                    events["RE_ACCESS_SPRING_WATER"] or events["RE_ACCESS_HOT_SPRING_WATER"]) or half_days()[2]),
            "FOUND_ALL_FROGS": lambda: all(self.has_ri(state, item) for item in (
                "RI_FROG_BLUE", "RI_FROG_CYAN", "RI_FROG_PINK", "RI_FROG_WHITE")),
            "GBT_CAN_REVERSE_WATER_FLOW": lambda: bool(events["RE_GREAT_BAY_RED_SWITCH_1"] and
                                                        events["RE_GREAT_BAY_RED_SWITCH_2"] and
                                                        self.has_ri(state, "RI_HOOKSHOT")),
            "GBT_GREEN_SWITCH_FLOW": lambda: all(events[event] for event in (
                "RE_GREAT_BAY_GREEN_SWITCH_1", "RE_GREAT_BAY_GREEN_SWITCH_2", "RE_GREAT_BAY_GREEN_SWITCH_3")),
            "BREAK_BOULDER_BEFORE_OR_BEAT_ALIENS_DAY": lambda: bool(
                half_days()[0] and self.has_ri(state, "RI_MASK_GORON") and self.has_ri(
                    state, "RI_POWDER_KEG") or events["RE_COWS_FROM_ALIENS"]),
            "BREAK_BOULDER_BEFORE_OR_BEAT_ALIENS_NIGHT": lambda: bool(
                half_days()[1] and self.has_ri(state, "RI_MASK_GORON") and self.has_ri(
                    state, "RI_POWDER_KEG") or events["RE_COWS_FROM_ALIENS"]),
        }
        env = _LazyEnvironment(dict(EXPRESSION_CONSTANTS[expression]), providers)
        env.update({
            "RANDO_EVENTS": events, "RANDO_SAVE_OPTIONS": option_values,
            "RO_ACCESS_TRIALS_20_MASKS": 0, "RO_ACCESS_TRIALS_REMAINS": 1,
            "RO_ACCESS_TRIALS_FORMS": 2, "RO_ACCESS_TRIALS_OPEN": 3,
            "RO_GENERIC_NO": 0,
            "HAS_ITEM": lambda item: self.has_item(state, item),
            "CAN_BE_HUMAN": True,
            "CAN_PLAY_SONG": lambda song: self.can_play_song(state, song),
            "canPlaySong": lambda song: self.ocarina_buttons(state, song),
            "CAN_USE_MAGIC_ARROW": lambda arrow: self.bow_level(state) > 0 and self.has_ri(
                state, f"RI_ARROW_{arrow}") and bool(env["HAS_MAGIC"]),
            "CAN_USE_ABILITY": lambda ability: ability != "SWIM" or not self.options.shuffle_swim.value or self.has_ri(state, "RI_ABILITY_SWIM"),
            "CAN_ACCESS": lambda access: bool(events["RE_ACCESS_" + access]),
            "CAN_OWL_WARP": lambda owl: self.has_ri(state, OWL_ITEMS[owl]),
            "CAN_AFFORD": lambda check: self.can_afford(state, check),
            "KEY_COUNT": lambda dungeon: self.key_count(state, dungeon),
            "HAS_ENOUGH_STRAY_FAIRIES": lambda dungeon: self.count_ri(state, f"RI_{DUNGEON_NAMES[dungeon]}_STRAY_FAIRY") >= self.options.stray_fairies_required.value,
            "HAS_ENOUGH_SKULLTULA_TOKENS": lambda scene: self.count_ri(state, "RI_GS_TOKEN_OCEAN" if scene == "SCENE_KINDAN2" else "RI_GS_TOKEN_SWAMP") >= self.options.skulltula_tokens_required.value,
            "CHECK_MAX_HP": lambda hearts: self.options.starting_health.value + self.count_ri(state, "RI_HEART_CONTAINER") + self.count_ri(state, "RI_HEART_PIECE") // 4 >= hearts,
            "Flags_GetRandoInf": lambda flag: self.has_rando_inf(state, flag),
            "CHECK_WEEKEVENTREG": lambda flag: flag == "WEEKEVENTREG_08_80" and self.has_ri(state, "RI_CLOCK_TOWN_STRAY_FAIRY"),
            "CHECK_QUEST_ITEM": lambda quest: self.has_ri(state, "RI_" + quest.removeprefix("QUEST_")),
            "CHECK_DUNGEON_ITEM": lambda item, dungeon: item == "DUNGEON_BOSS_KEY" and (self.has_ri(state, "RI_SKELETON_KEY") or self.has_ri(state, f"RI_{DUNGEON_NAMES[dungeon]}_BOSS_KEY")),
            "CUR_UPG_VALUE": lambda upgrade: self.wallet_level(state) if upgrade == "UPG_WALLET" else 0,
            "GET_CUR_UPG_VALUE": lambda upgrade: self.wallet_level(state) if upgrade == "UPG_WALLET" else 0,
            "GET_CUR_EQUIP_VALUE": lambda equip: self.shield_level(state) if equip == "EQUIP_TYPE_SHIELD" else self.sword_level(state),
            "EQUIP_VALUE_SHIELD_MIRROR": 2,
            "CanAccessDungeon": lambda dungeon: self.can_access_dungeon(state, dungeon),
            "CanKillEnemy": lambda actor: self.can_kill_enemy(state, actor),
            "CanGetPastBigOctoWithoutBoat": lambda: bool(events["RE_SOUTHERN_SWAMP_KILL_OCTOROK"] and
                self.has_ri(state, "RI_MASK_DEKU") or events["RE_CLEARED_WOODFALL_TEMPLE"] and
                bool(env["CAN_TRAVERSE_WAIST_DEEP_WATER"])),
            "CanGetPastBigOcto": lambda: bool(events["RE_SOUTHERN_SWAMP_RIDE_BOAT"] or
                events["RE_SOUTHERN_SWAMP_KILL_OCTOROK"] and self.has_ri(state, "RI_MASK_DEKU") or
                events["RE_CLEARED_WOODFALL_TEMPLE"] and bool(env["CAN_TRAVERSE_WAIST_DEEP_WATER"])),
            "MoonMaskCount": lambda: self.mask_count(state), "RemainsCount": lambda: self.remains_count(state),
            "MeetsMoonRequirements": lambda: self.remains_count(state) >= self.options.moon_remains_required.value and self.mask_count(state) >= self.options.moon_masks_required.value,
            "AT": lambda when: bool(time_mask() & (1 << TIME_INDEX[when])),
            "BEFORE": lambda when: time_range(0, TIME_INDEX[when]),
            "AFTER": lambda when: time_range(TIME_INDEX[when], 45),
            "BETWEEN": lambda start, end: time_range(TIME_INDEX[start], TIME_INDEX[end]),
        })
        for index, label in enumerate(("DAY1", "NIGHT1", "DAY2", "NIGHT2", "DAY3", "NIGHT3")):
            env["CLOCK_" + label] = lambda i=index: half_days()[i]
            env["IS_" + label] = lambda i=index: half_days()[i]
        env.update({
            "IS_DAY": lambda: any(half_days()[::2]), "IS_NIGHT": lambda: any(half_days()[1::2]),
            "FIRST_DAY": lambda: any(half_days()[:2]), "SECOND_DAY": lambda: any(half_days()[2:4]),
            "FINAL_DAY": lambda: any(half_days()[4:]),
            "MIDNIGHT": lambda: any(half_days()[index] for index in (1, 3, 5)),
        })
        return bool(eval(COMPILED[expression], {"__builtins__": {}}, env))

    def rule(self, expression: str) -> Rule:
        if self.options.logic_mode.value == 1:
            return lambda state: True
        return lambda state: self.evaluate(state, expression)

    def location_rule(self, occurrences: tuple[tuple[str, str], ...]) -> Rule:
        if self.options.logic_mode.value == 1:
            return lambda state: True
        return lambda state: any(state.can_reach(REGION_PREFIX + region, "Region", self.player)
                                 and self.evaluate(state, condition) for region, condition in occurrences)

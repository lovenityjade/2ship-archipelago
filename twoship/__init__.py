from __future__ import annotations

from typing import ClassVar

import settings
from BaseClasses import Item, ItemClassification, Location, Region, Tutorial
from Options import OptionError
from worlds.AutoWorld import WebWorld, World
from worlds.LauncherComponents import Component, Type, components, launch as launch_component

from .Options import RO_OPTION_FIELDS, TwoShipOptions, option_groups
from .data import CHECKS, ITEMS


GAME_NAME = "2 Ship 2 Harkinian"
ITEM_ID_BASE = 74_200_000
LOCATION_ID_BASE = 74_210_000
CLIENT_VERSION = "0.2.0"

CONDITIONAL_LOCATION_OPTIONS = {
    "RCTYPE_BARREL": "shuffle_barrel_drops",
    "RCTYPE_COW": "shuffle_cows",
    "RCTYPE_CRATE": "shuffle_crate_drops",
    "RCTYPE_ENEMY_DROP": "shuffle_enemy_drops",
    "RCTYPE_FREESTANDING": "shuffle_freestanding_items",
    "RCTYPE_FROG": "shuffle_frogs",
    "RCTYPE_GRASS": "shuffle_grass_drops",
    "RCTYPE_OWL": "shuffle_owl_statues",
    "RCTYPE_POT": "shuffle_pot_drops",
    "RCTYPE_REMAINS": "shuffle_boss_remains",
    "RCTYPE_SHOP": "shuffle_shops",
    "RCTYPE_SKULL_TOKEN": "shuffle_gold_skulltulas",
    "RCTYPE_SNOWBALL": "shuffle_snowball_drops",
    "RCTYPE_TINGLE_SHOP": "shuffle_tingle_shops",
    "RCTYPE_TREE": "shuffle_tree_drops",
}

LOCATION_OPTION_RO = {
    "shuffle_barrel_drops": "RO_SHUFFLE_BARREL_DROPS",
    "shuffle_cows": "RO_SHUFFLE_COWS",
    "shuffle_crate_drops": "RO_SHUFFLE_CRATE_DROPS",
    "shuffle_enemy_drops": "RO_SHUFFLE_ENEMY_DROPS",
    "shuffle_freestanding_items": "RO_SHUFFLE_FREESTANDING_ITEMS",
    "shuffle_frogs": "RO_SHUFFLE_FROGS",
    "shuffle_grass_drops": "RO_SHUFFLE_GRASS_DROPS",
    "shuffle_owl_statues": "RO_SHUFFLE_OWL_STATUES",
    "shuffle_pot_drops": "RO_SHUFFLE_POT_DROPS",
    "shuffle_boss_remains": "RO_SHUFFLE_BOSS_REMAINS",
    "shuffle_shops": "RO_SHUFFLE_SHOPS",
    "shuffle_gold_skulltulas": "RO_SHUFFLE_GOLD_SKULLTULAS",
    "shuffle_snowball_drops": "RO_SHUFFLE_SNOWBALL_DROPS",
    "shuffle_tingle_shops": "RO_SHUFFLE_TINGLE_SHOPS",
    "shuffle_tree_drops": "RO_SHUFFLE_TREE_DROPS",
}

ALWAYS_SHUFFLED_SHOPS = {
    "RC_CURIOSITY_SHOP_SPECIAL_ITEM",
    "RC_BOMB_SHOP_ITEM_04_OR_CURIOSITY_SHOP_ITEM",
}

UNAVAILABLE_CHECKS = {
    "RC_MOON_MAJORA_POT_01",
    "RC_MOON_MAJORA_POT_02",
}


def pretty_name(symbol: str) -> str:
    return symbol.removeprefix("RC_").removeprefix("RI_").replace("_", " ").title()


ITEM_DATA = {name: (ordinal, item_type) for name, ordinal, item_type in ITEMS}
ITEM_NAME_TO_SYMBOL = {pretty_name(name): name for name, _, _ in ITEMS}
ITEM_SYMBOL_TO_NAME = {symbol: name for name, symbol in ITEM_NAME_TO_SYMBOL.items()}
ITEM_NAME_TO_ID = {name: ITEM_ID_BASE + ITEM_DATA[symbol][0] for name, symbol in ITEM_NAME_TO_SYMBOL.items()}

LOCATION_DATA = {pretty_name(name): (name, ordinal, check_type, vanilla_item)
                 for name, ordinal, check_type, vanilla_item in CHECKS if name not in UNAVAILABLE_CHECKS}
LOCATION_NAME_TO_ID = {name: LOCATION_ID_BASE + data[1] for name, data in LOCATION_DATA.items()}


class TwoShipItem(Item):
    game = GAME_NAME


class TwoShipLocation(Location):
    game = GAME_NAME


class TwoShipSettings(settings.Group):
    class ExecutablePath(str):
        """Path to the Archipelago-enabled 2Ship executable or AppImage."""

    class SettingsFolder(str):
        """Folder containing 2ship2harkinian.json, saves, and O2R files."""

    executable_path: ExecutablePath | None = None
    settings_folder: SettingsFolder | None = None


class TwoShipWeb(WebWorld):
    option_groups = option_groups
    options_presets = {
        "Core Checks": {
            "progression_balancing": 50,
            "accessibility": "full",
            "check_scope": "core",
        },
        "All Checks": {
            "progression_balancing": 50,
            "accessibility": "full",
            "check_scope": "all",
        },
    }
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to connecting 2 Ship 2 Harkinian to an Archipelago room.",
        "English",
        "setup_en.md",
        "setup/en",
        ["TheLovenityJade"],
    )]


def classification_for(item_type: str) -> ItemClassification:
    if item_type in {"RITYPE_MAJOR", "RITYPE_BOSS_KEY", "RITYPE_SMALL_KEY", "RITYPE_MASK"}:
        return ItemClassification.progression
    if item_type in {"RITYPE_LESSER", "RITYPE_HEALTH", "RITYPE_STRAY_FAIRY", "RITYPE_SKULLTULA_TOKEN"}:
        return ItemClassification.useful
    return ItemClassification.filler


class TwoShipWorld(World):
    """The native PC port of The Legend of Zelda: Majora's Mask."""

    game = GAME_NAME
    web = TwoShipWeb()
    options_dataclass = TwoShipOptions
    options: TwoShipOptions
    settings: ClassVar[TwoShipSettings]
    item_name_to_id = ITEM_NAME_TO_ID
    location_name_to_id = LOCATION_NAME_TO_ID

    def included_locations(self):
        if self.options.check_scope.value == 1:
            return list(LOCATION_DATA.items())

        included = []
        for name, data in LOCATION_DATA.items():
            symbol, _, check_type, _ = data
            option_name = CONDITIONAL_LOCATION_OPTIONS.get(check_type)
            if option_name is None or getattr(self.options, option_name).value:
                included.append((name, data))
            elif check_type == "RCTYPE_SHOP" and symbol in ALWAYS_SHUFFLED_SHOPS:
                included.append((name, data))
        return included

    def active_locations(self):
        excluded = self.options.exclude_locations.value
        return [(name, data) for name, data in self.included_locations() if name not in excluded]

    def native_option_values(self) -> dict[str, int]:
        values = {ro_name: getattr(self.options, field_name).value
                  for ro_name, field_name in RO_OPTION_FIELDS.items()}
        if self.options.check_scope.value == 1:
            for field_name, ro_name in LOCATION_OPTION_RO.items():
                values[ro_name] = 1
        return values

    def generate_early(self) -> None:
        if self.options.skulltula_tokens_required.value > self.options.skulltula_tokens_in_pool.value:
            raise OptionError("Skulltula tokens required cannot exceed the number placed in the pool.")
        if self.options.stray_fairies_required.value > self.options.stray_fairies_in_pool.value:
            raise OptionError("Stray fairies required cannot exceed the number placed in the pool.")
        if self.options.triforce_pieces_required.value > self.options.triforce_pieces_in_pool.value:
            raise OptionError("Triforce pieces required cannot exceed the number placed in the pool.")

        vanilla_incompatible = (
            "shuffle_boss_souls", "shuffle_swim", "shuffle_enemy_souls", "shuffle_ocarina_buttons",
            "plentiful_items", "shuffle_time", "shuffle_tycoon_wallet",
        )
        if self.options.logic_mode.value == 3 and any(getattr(self.options, name).value
                                                       for name in vanilla_incompatible):
            raise OptionError("Vanilla logic is incompatible with options that add items to the pool.")

    def create_regions(self) -> None:
        menu = Region("Menu", self.player, self.multiworld)
        termina = Region("Termina", self.player, self.multiworld)
        menu.connect(termina)
        for name, data in self.included_locations():
            location = TwoShipLocation(self.player, name, LOCATION_ID_BASE + data[1], termina)
            if name in self.options.exclude_locations.value:
                location.place_locked_item(self.create_item("Junk"))
            termina.locations.append(location)
        self.multiworld.regions += [menu, termina]

    def create_item(self, name: str) -> TwoShipItem:
        symbol = ITEM_NAME_TO_SYMBOL[name]
        ordinal, item_type = ITEM_DATA[symbol]
        return TwoShipItem(name, classification_for(item_type), ITEM_ID_BASE + ordinal, self.player)

    def create_items(self) -> None:
        pool: list[str] = []
        for _, (_, _, _, vanilla_item) in self.active_locations():
            symbol = vanilla_item if vanilla_item in ITEM_SYMBOL_TO_NAME else "RI_JUNK"
            pool.append(symbol)

        limited_items = {
            "RI_GREAT_BAY_STRAY_FAIRY": self.options.stray_fairies_in_pool.value,
            "RI_SNOWHEAD_STRAY_FAIRY": self.options.stray_fairies_in_pool.value,
            "RI_STONE_TOWER_STRAY_FAIRY": self.options.stray_fairies_in_pool.value,
            "RI_WOODFALL_STRAY_FAIRY": self.options.stray_fairies_in_pool.value,
            "RI_GS_TOKEN_OCEAN": self.options.skulltula_tokens_in_pool.value,
            "RI_GS_TOKEN_SWAMP": self.options.skulltula_tokens_in_pool.value,
        }
        for symbol, maximum in limited_items.items():
            seen = 0
            for index, pool_symbol in enumerate(pool):
                if pool_symbol == symbol:
                    seen += 1
                    if seen > maximum:
                        pool[index] = "RI_JUNK"

        extras = ["RI_PROGRESSIVE_SWORD", "RI_SHIELD_HERO"]
        if self.options.skeleton_key.value:
            extras.append("RI_SKELETON_KEY")
        if self.options.shuffle_boss_souls.value:
            extras.extend(symbol for symbol in ITEM_DATA if symbol.startswith("RI_SOUL_BOSS_"))
            if self.options.triforce_hunt.value and "RI_SOUL_BOSS_MAJORA" in extras:
                extras.remove("RI_SOUL_BOSS_MAJORA")
        if self.options.shuffle_enemy_souls.value:
            extras.extend(symbol for symbol in ITEM_DATA if symbol.startswith("RI_SOUL_ENEMY_"))
        if self.options.shuffle_time.value:
            if self.options.clock_progression.value == 0:
                extras.extend(("RI_TIME_DAY_1", "RI_TIME_NIGHT_1", "RI_TIME_DAY_2",
                               "RI_TIME_NIGHT_2", "RI_TIME_DAY_3", "RI_TIME_NIGHT_3"))
            else:
                extras.extend(["RI_TIME_PROGRESSIVE"] * 6)
        if self.options.shuffle_swim.value:
            extras.append("RI_ABILITY_SWIM")
        if self.options.shuffle_ocarina_buttons.value:
            extras.extend(("RI_OCARINA_BUTTON_A", "RI_OCARINA_BUTTON_C_DOWN", "RI_OCARINA_BUTTON_C_RIGHT",
                           "RI_OCARINA_BUTTON_C_LEFT", "RI_OCARINA_BUTTON_C_UP"))
        for option_name, symbol in (
            ("shuffle_song_sun", "RI_SONG_SUN"),
            ("shuffle_song_double_time", "RI_SONG_DOUBLE_TIME"),
            ("shuffle_song_inverted_time", "RI_SONG_INVERTED_TIME"),
            ("shuffle_song_saria", "RI_SONG_SARIA"),
            ("shuffle_tycoon_wallet", "RI_PROGRESSIVE_WALLET"),
        ):
            if getattr(self.options, option_name).value:
                extras.append(symbol)
        if self.options.triforce_hunt.value:
            extras.extend(["RI_TRIFORCE_PIECE"] * self.options.triforce_pieces_in_pool.value)
        if self.options.shuffle_traps.value:
            extras.extend(["RI_TRAP"] * self.options.trap_amount.value)

        if self.options.starting_health.value < 3:
            extras.extend(["RI_HEART_PIECE"] * (4 * (3 - self.options.starting_health.value)))
        elif self.options.starting_health.value > 3:
            remove_count = 4 * (self.options.starting_health.value - 3)
            for _ in range(remove_count):
                if "RI_HEART_PIECE" in pool:
                    pool.remove("RI_HEART_PIECE")
                    pool.append("RI_JUNK")

        if self.options.plentiful_items.value:
            extras.extend(symbol for symbol in pool if ITEM_DATA[symbol][1] in {
                "RITYPE_MAJOR", "RITYPE_BOSS_KEY", "RITYPE_SMALL_KEY", "RITYPE_MASK",
            })

        for extra in extras:
            replacement = next((index for index, symbol in enumerate(pool)
                                if ITEM_DATA[symbol][1] == "RITYPE_JUNK"), None)
            if replacement is None:
                replacement = next((index for index, symbol in enumerate(pool)
                                    if classification_for(ITEM_DATA[symbol][1]) != ItemClassification.progression), None)
            if replacement is None:
                raise OptionError(f"Not enough replaceable items to add {extra} to the item pool.")
            pool[replacement] = extra
        self.multiworld.itempool += [self.create_item(ITEM_SYMBOL_TO_NAME[symbol]) for symbol in pool]

    def set_rules(self) -> None:
        if self.options.triforce_hunt.value:
            required = self.options.triforce_pieces_required.value
            self.multiworld.completion_condition[self.player] = \
                lambda state: state.has("Triforce Piece", self.player, required)
        elif self.options.shuffle_boss_remains.value:
            remains = {"Remains Odolwa", "Remains Goht", "Remains Gyorg", "Remains Twinmold"}
            self.multiworld.completion_condition[self.player] = lambda state: state.has_all(remains, self.player)
        else:
            self.multiworld.completion_condition[self.player] = lambda state: True

    def fill_slot_data(self) -> dict:
        return {
            "client_version": CLIENT_VERSION,
            "check_scope": self.options.check_scope.value,
            "item_id_base": ITEM_ID_BASE,
            "location_id_base": LOCATION_ID_BASE,
            "active_locations": [data[1] for _, data in self.active_locations()],
            "rando_options": self.native_option_values(),
        }


def launch_client(*args: str) -> None:
    from .Client import launch
    launch_component(launch, name="2Ship Client", args=args)


components.append(Component("2Ship Client", game_name=GAME_NAME, func=launch_client,
                            component_type=Type.CLIENT, supports_uri=True))

from __future__ import annotations

from collections.abc import Callable

from BaseClasses import CollectionState


Rule = Callable[[CollectionState], bool]


REGION_PREFIXES = (
    ("MOON_", "The Moon"),
    ("WOODFALL_TEMPLE_", "Woodfall Temple"),
    ("SNOWHEAD_TEMPLE_", "Snowhead Temple"),
    ("GREAT_BAY_TEMPLE_", "Great Bay Temple"),
    ("STONE_TOWER_TEMPLE_", "Stone Tower Temple"),
    ("PIRATE_FORTRESS_", "Pirates' Fortress"),
    ("BENEATH_THE_WELL_", "Ikana Canyon"),
    ("ANCIENT_CASTLE_OF_IKANA_", "Ikana Canyon"),
    ("IKANA_CASTLE_", "Ikana Canyon"),
    ("IKANA_", "Ikana Canyon"),
    ("ROAD_TO_IKANA_", "Ikana Canyon"),
    ("SECRET_SHRINE_", "Ikana Canyon"),
    ("STONE_TOWER_", "Ikana Canyon"),
    ("OCEAN_SKULLTULA_", "Great Bay Coast"),
    ("GREAT_BAY_", "Great Bay Coast"),
    ("ZORA_", "Great Bay Coast"),
    ("PINNACLE_ROCK_", "Great Bay Coast"),
    ("WATERFALL_RAPIDS_", "Great Bay Coast"),
    ("FISHERMANS_HUT_", "Great Bay Coast"),
    ("SWAMP_SKULLTULA_", "Southern Swamp"),
    ("DEKU_", "Southern Swamp"),
    ("WOODS_OF_MYSTERY_", "Southern Swamp"),
    ("SOUTHERN_SWAMP_", "Southern Swamp"),
    ("ROAD_TO_SOUTHERN_SWAMP_", "Southern Swamp"),
    ("WOODFALL_", "Southern Swamp"),
    ("GORON_", "Snowhead"),
    ("MOUNTAIN_", "Snowhead"),
    ("PATH_TO_GORON_", "Snowhead"),
    ("PATH_TO_SNOWHEAD_", "Snowhead"),
    ("SNOWHEAD_", "Snowhead"),
    ("ROMANI_", "Romani Ranch"),
    ("MILK_ROAD_", "Romani Ranch"),
    ("DOGGY_RACETRACK_", "Romani Ranch"),
    ("GORMAN_", "Romani Ranch"),
    ("CUCCO_SHACK_", "Romani Ranch"),
)


# These items participate in access rules even when native 2Ship categorizes
# them as lesser items. Archipelago must treat them as progression.
LOGIC_ITEM_SYMBOLS = {
    "RI_ARROW_FIRE", "RI_ARROW_ICE", "RI_ARROW_LIGHT", "RI_BOMBERS_NOTEBOOK",
    "RI_BOTTLE_EMPTY", "RI_BOW", "RI_HOOKSHOT", "RI_LENS", "RI_MAGIC_BEAN",
    "RI_GREAT_BAY_STRAY_FAIRY", "RI_GS_TOKEN_OCEAN", "RI_GS_TOKEN_SWAMP",
    "RI_MASK_ALL_NIGHT", "RI_MASK_BLAST", "RI_MASK_BREMEN", "RI_MASK_CAPTAIN",
    "RI_MASK_COUPLE", "RI_MASK_DEKU", "RI_MASK_DON_GERO", "RI_MASK_GARO",
    "RI_MASK_GIBDO", "RI_MASK_GORON", "RI_MASK_KAFEIS_MASK", "RI_MASK_KEATON",
    "RI_MASK_POSTMAN", "RI_MASK_ROMANI", "RI_MASK_SCENTS", "RI_MASK_STONE",
    "RI_MASK_TRUTH", "RI_MASK_ZORA", "RI_OCARINA", "RI_PICTOGRAPH_BOX",
    "RI_POWDER_KEG", "RI_PROGRESSIVE_BOMB_BAG", "RI_PROGRESSIVE_BOW",
    "RI_PROGRESSIVE_MAGIC", "RI_PROGRESSIVE_SWORD", "RI_PROGRESSIVE_WALLET",
    "RI_REMAINS_GOHT", "RI_REMAINS_GYORG", "RI_REMAINS_ODOLWA", "RI_REMAINS_TWINMOLD",
    "RI_PROGRESSIVE_LULLABY", "RI_ROOM_KEY", "RI_SHIELD_MIRROR", "RI_SKELETON_KEY",
    "RI_SNOWHEAD_BOSS_KEY", "RI_SNOWHEAD_SMALL_KEY", "RI_SONG_ELEGY",
    "RI_SONG_EPONA", "RI_SONG_HEALING", "RI_SONG_LULLABY_INTRO", "RI_SONG_LULLABY",
    "RI_SONG_NOVA", "RI_SONG_OATH", "RI_SONG_SOARING", "RI_SONG_SONATA",
    "RI_SONG_STORMS", "RI_SONG_TIME", "RI_STONE_TOWER_BOSS_KEY",
    "RI_SNOWHEAD_STRAY_FAIRY", "RI_STONE_TOWER_STRAY_FAIRY", "RI_WOODFALL_STRAY_FAIRY",
    "RI_STONE_TOWER_SMALL_KEY", "RI_WOODFALL_BOSS_KEY", "RI_WOODFALL_SMALL_KEY",
    "RI_CLOCK_TOWN_STRAY_FAIRY", "RI_FROG_BLUE", "RI_FROG_CYAN", "RI_FROG_PINK", "RI_FROG_WHITE",
    "RI_HEART_CONTAINER", "RI_HEART_PIECE",
}


def region_for(symbol: str) -> str:
    for prefix, region in REGION_PREFIXES:
        if symbol.startswith("RC_" + prefix):
            return region
    if symbol.startswith(("RC_TERMINA_FIELD_", "RC_ASTRAL_OBSERVATORY_")):
        return "Termina Field"
    return "Clock Town"


class Logic:
    def __init__(self, player: int, options):
        self.player = player
        self.options = options

    def has(self, state: CollectionState, item: str, count: int = 1) -> bool:
        return state.has(item, self.player, count)

    def any(self, state: CollectionState, *items: str) -> bool:
        return state.has_any(set(items), self.player)

    def all(self, state: CollectionState, *items: str) -> bool:
        return state.has_all(set(items), self.player)

    def ocarina_song(self, state: CollectionState, song: str) -> bool:
        return self.has(state, "Ocarina") and self.has(state, song)

    def goron_lullaby(self, state: CollectionState) -> bool:
        return self.has(state, "Ocarina") and (
            self.has(state, "Song Lullaby") or self.has(state, "Progressive Lullaby", 2)
        )

    def explosive(self, state: CollectionState) -> bool:
        return self.any(state, "Progressive Bomb Bag", "Bomb Bag 20", "Bombchu", "Mask Blast")

    def bow(self, state: CollectionState) -> bool:
        return self.any(state, "Bow", "Progressive Bow")

    def magic(self, state: CollectionState) -> bool:
        return self.any(state, "Progressive Magic", "Single Magic", "Double Magic")

    def bottle(self, state: CollectionState) -> bool:
        return any(self.has(state, item) for item in (
            "Bottle Empty", "Bottle Red Potion", "Bottle Milk", "Bottle Chateau Romani", "Bottle Gold Dust"
        ))

    def boss_key(self, state: CollectionState, dungeon: str) -> bool:
        return self.any(state, f"{dungeon} Boss Key", "Skeleton Key")

    def small_keys(self, state: CollectionState, dungeon: str, count: int) -> bool:
        return self.has(state, "Skeleton Key") or self.has(state, f"{dungeon} Small Key", count)

    def region_rule(self, name: str) -> Rule:
        if self.options.logic_mode.value == 1:
            return lambda state: True

        rules: dict[str, Rule] = {
            "Clock Town": lambda state: True,
            "Termina Field": lambda state: True,
            "Southern Swamp": lambda state: True,
            "Romani Ranch": lambda state: self.has(state, "Powder Keg"),
            "Snowhead": lambda state: self.bow(state) or self.explosive(state),
            "Great Bay Coast": lambda state: (
                self.ocarina_song(state, "Song Epona")
                or (self.has(state, "Mask Goron") and self.has(state, "Powder Keg"))
            ),
            "Ikana Canyon": lambda state: (
                self.ocarina_song(state, "Song Epona")
                and self.has(state, "Mask Garo")
                and self.has(state, "Hookshot")
            ),
            "Woodfall Temple": lambda state: (
                self.has(state, "Mask Deku") and self.ocarina_song(state, "Song Sonata")
            ),
            "Snowhead Temple": lambda state: (
                self.has(state, "Mask Goron") and self.goron_lullaby(state)
            ),
            "Pirates' Fortress": lambda state: self.has(state, "Mask Zora") or self.has(state, "Hookshot"),
            "Great Bay Temple": lambda state: (
                self.has(state, "Mask Zora") and self.has(state, "Hookshot")
                and self.ocarina_song(state, "Song Nova")
            ),
            "Stone Tower Temple": lambda state: (
                self.has(state, "Hookshot") and self.ocarina_song(state, "Song Elegy")
                and self.all(state, "Mask Deku", "Mask Goron", "Mask Zora")
            ),
            "The Moon": self.meets_moon_requirements,
        }
        return rules[name]

    def meets_moon_requirements(self, state: CollectionState) -> bool:
        remains = ("Remains Odolwa", "Remains Goht", "Remains Gyorg", "Remains Twinmold")
        remains_count = sum(self.has(state, item) for item in remains)
        masks = (
            "Mask Truth", "Mask Kafeis Mask", "Mask All Night", "Mask Bunny", "Mask Keaton",
            "Mask Garo", "Mask Romani", "Mask Circus Leader", "Mask Postman", "Mask Couple",
            "Mask Great Fairy", "Mask Gibdo", "Mask Don Gero", "Mask Kamaro", "Mask Captain",
            "Mask Stone", "Mask Bremen", "Mask Blast", "Mask Scents", "Mask Giant",
        )
        mask_count = sum(self.has(state, item) for item in masks)
        return (remains_count >= self.options.majora_remains_required.value
                and mask_count >= self.options.majora_masks_required.value)

    def can_finish(self, state: CollectionState) -> bool:
        if self.options.logic_mode.value == 1:
            return True
        dungeon_access = self.all(state, "Mask Deku", "Mask Goron", "Mask Zora", "Hookshot")
        songs = (self.ocarina_song(state, "Song Sonata") and self.goron_lullaby(state)
                 and self.ocarina_song(state, "Song Nova") and self.ocarina_song(state, "Song Elegy"))
        combat = self.bow(state) and self.magic(state) and self.has(state, "Arrow Light")
        return dungeon_access and songs and combat and self.meets_moon_requirements(state)

    def location_rule(self, symbol: str) -> Rule:
        if self.options.logic_mode.value == 1:
            return lambda state: True

        requirements: list[Rule] = []
        add = requirements.append

        if any(word in symbol for word in ("SHOOTING_GALLERY", "ARCHERY", "SHOOT_THE_SUN")):
            add(self.bow)
        if "COW" in symbol:
            add(lambda state: self.ocarina_song(state, "Song Epona") and self.bottle(state))
        if "BEAN" in symbol:
            add(lambda state: self.has(state, "Magic Bean") and (self.bottle(state) or self.ocarina_song(state, "Song Storms")))
        if "LENS" in symbol or "INVISIBLE" in symbol:
            add(lambda state: self.has(state, "Lens") and self.magic(state))
        if "PICTOGRAPH" in symbol or "PICTURE" in symbol:
            add(lambda state: self.has(state, "Pictograph Box"))
        if "GREAT_FAIRY" in symbol:
            dungeon = next((name for key, name in (
                ("WOODFALL", "Woodfall"), ("SNOWHEAD", "Snowhead"),
                ("GREAT_BAY", "Great Bay"), ("IKANA", "Stone Tower"),
            ) if key in symbol), None)
            if dungeon:
                count = self.options.stray_fairies_required.value
                add(lambda state, d=dungeon, c=count: self.has(state, f"{d} Stray Fairy", c))
        if "SKULLTULA_HOUSE_REWARD" in symbol or "SPIDER_HOUSE_REWARD" in symbol:
            count = self.options.skulltula_tokens_required.value
            token = "Gs Token Ocean" if "OCEAN" in symbol else "Gs Token Swamp"
            add(lambda state, i=token, c=count: self.has(state, i, c))

        dungeon = next((name for prefix, name in (
            ("RC_WOODFALL_TEMPLE_", "Woodfall"), ("RC_SNOWHEAD_TEMPLE_", "Snowhead"),
            ("RC_GREAT_BAY_TEMPLE_", "Great Bay"), ("RC_STONE_TOWER_TEMPLE_", "Stone Tower"),
        ) if symbol.startswith(prefix)), None)
        if dungeon:
            if "BOSS_" in symbol or "BOSS_WARP" in symbol:
                add(lambda state, d=dungeon: self.boss_key(state, d))
            if dungeon == "Woodfall" and any(x in symbol for x in ("PRE_BOSS", "BOSS_KEY")):
                add(lambda state: self.small_keys(state, "Woodfall", 1) and self.bow(state))
            elif dungeon == "Snowhead" and any(x in symbol for x in ("PRE_BOSS", "BOSS_KEY", "UPPER")):
                add(lambda state: self.small_keys(state, "Snowhead", 3) and self.has(state, "Arrow Fire") and self.magic(state))
            elif dungeon == "Great Bay" and any(x in symbol for x in ("PRE_BOSS", "BOSS_KEY", "GREEN_PIPE")):
                add(lambda state: self.small_keys(state, "Great Bay", 1) and self.has(state, "Arrow Ice") and self.magic(state))
            elif dungeon == "Stone Tower" and any(x in symbol for x in ("PRE_BOSS", "BOSS_KEY", "INVERTED")):
                add(lambda state: self.small_keys(state, "Stone Tower", 4) and self.has(state, "Arrow Light") and self.magic(state))

        if not requirements:
            return lambda state: True
        return lambda state: all(rule(state) for rule in requirements)


def dungeon_item_rule(item_name: str, region_name: str, options) -> bool:
    placements = {
        "Small Key": options.small_key_placement.value,
        "Boss Key": options.boss_key_placement.value,
        "Stray Fairy": options.stray_fairy_placement.value,
    }
    for suffix, own_dungeon in placements.items():
        if item_name.endswith(suffix) and own_dungeon:
            dungeon = item_name.removesuffix(" " + suffix)
            if dungeon not in {"Woodfall", "Snowhead", "Great Bay", "Stone Tower"}:
                return True
            expected = f"{dungeon} Temple"
            return region_name == expected
    return True

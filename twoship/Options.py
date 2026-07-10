from dataclasses import dataclass

from Options import Choice, DefaultOnToggle, OptionGroup, PerGameCommonOptions, Range, Toggle


class CheckScope(Choice):
    """Core follows the shuffle settings below. All enables every supported native 2Ship check."""

    display_name = "Check Scope"
    option_core = 0
    option_all = 1
    default = 0


class LogicMode(Choice):
    """Native 2Ship logic mode. Archipelago logic is still conservative while the full region graph is developed."""

    display_name = "Logic"
    option_glitchless = 0
    option_no_logic = 1
    option_nearly_no_logic = 2
    option_vanilla = 3
    default = 0


class DungeonItemPlacement(Choice):
    option_anywhere = 0
    option_own_dungeon = 1
    default = 0


class DungeonAccess(Choice):
    """Controls which transformation mask and song requirements open the four main dungeons."""

    display_name = "Dungeon Access"
    option_form_and_song = 0
    option_form_or_song = 1
    option_form_only = 2
    option_song_only = 3
    option_open = 4
    default = 0


class TrialsAccess(Choice):
    """Controls access to the four Moon trials."""

    display_name = "Moon Trials Access"
    option_mask_count = 0
    option_associated_remains = 1
    option_associated_transformation = 2
    option_open = 3
    default = 0


class ClockProgression(Choice):
    """Random shuffles six half-days. Progressive modes unlock them in forward or reverse order."""

    display_name = "Time Progression Mode"
    option_individual_half_days = 0
    option_progressive_ascending = 1
    option_progressive_descending = 2
    default = 0


class Count0To4(Range):
    range_start = 0
    range_end = 4
    default = 0


class MaskCount(Range):
    range_start = 0
    range_end = 20
    default = 0


class MoonRemainsRequired(Count0To4):
    display_name = "Moon Access Remains Required"
    default = 4


class SkulltulaCount(Range):
    range_start = 1
    range_end = 30
    default = 30


class StrayFairyCount(Range):
    range_start = 1
    range_end = 15
    default = 15


class TriforcePieceCount(Range):
    range_start = 1
    range_end = 1000
    default = 15


class StartingHealth(Range):
    """Starting heart containers. Native 2Ship supports values from 1 through 20."""

    display_name = "Starting Health"
    range_start = 1
    range_end = 20
    default = 3


class TrapAmount(Range):
    display_name = "Trap Amount"
    range_start = 1
    range_end = 100
    default = 5


class ClockTerminalTime(Range):
    """Minute of the six-hour Final Hours clock at which the terminal period begins. 350 is 05:50."""

    display_name = "Final Hours Start Time"
    range_start = 0
    range_end = 359
    default = 350


class HintStrength(Range):
    display_name = "Gossip Stone Hint Strength"
    range_start = 0
    range_end = 100
    default = 50


class ShuffleBossRemains(DefaultOnToggle):
    """Places the four boss remains in the Archipelago item pool."""

    display_name = "Shuffle Boss Remains"


class NativeToggle(Toggle):
    default = 0


def toggle(name: str, display_name: str, doc: str = "") -> type[NativeToggle]:
    return type(name, (NativeToggle,), {"display_name": display_name, "__doc__": doc, "__module__": __name__})


ShuffleOwlStatues = toggle("ShuffleOwlStatues", "Shuffle Owl Statues")
ShuffleShops = toggle("ShuffleShops", "Shuffle Shops")
ShuffleTingleShops = toggle("ShuffleTingleShops", "Shuffle Tingle Maps")
ShuffleCows = toggle("ShuffleCows", "Shuffle Cows")
ShuffleGoldSkulltulas = toggle("ShuffleGoldSkulltulas", "Shuffle Gold Skulltula Tokens")
ShufflePotDrops = toggle("ShufflePotDrops", "Shuffle Pot Drops")
ShuffleCrateDrops = toggle("ShuffleCrateDrops", "Shuffle Crate Drops")
ShuffleBarrelDrops = toggle("ShuffleBarrelDrops", "Shuffle Barrel Drops")
ShuffleSnowballDrops = toggle("ShuffleSnowballDrops", "Shuffle Snowball Drops")
ShuffleGrassDrops = toggle("ShuffleGrassDrops", "Shuffle Grass Drops")
ShuffleTreeDrops = toggle("ShuffleTreeDrops", "Shuffle Tree Drops")
ShuffleFrogs = toggle("ShuffleFrogs", "Shuffle Frogs")
ShuffleFreestandingItems = toggle("ShuffleFreestandingItems", "Shuffle Freestanding Items")
ShuffleEnemyDrops = toggle("ShuffleEnemyDrops", "Shuffle Enemy Drops", "Shuffles the first drop from non-boss enemies.")

ShuffleSwim = toggle("ShuffleSwim", "Shuffle Swim")
ShuffleOcarinaButtons = toggle("ShuffleOcarinaButtons", "Shuffle Ocarina Buttons")
ShuffleSongDoubleTime = toggle("ShuffleSongDoubleTime", "Song of Double Time")
ShuffleSongInvertedTime = toggle("ShuffleSongInvertedTime", "Inverted Song of Time")
ShuffleSongSun = toggle("ShuffleSongSun", "Sun's Song")
ShuffleSongSaria = toggle("ShuffleSongSaria", "Saria's Song")
ShuffleTycoonWallet = toggle("ShuffleTycoonWallet", "Tycoon's Wallet")
PlentifulItems = toggle("PlentifulItems", "Plentiful Items")
ShuffleBossSouls = toggle("ShuffleBossSouls", "Boss Souls")
ShuffleEnemySouls = toggle("ShuffleEnemySouls", "Enemy Souls")
ShuffleTime = toggle("ShuffleTime", "Shuffle Time")
ShuffleTraps = toggle("ShuffleTraps", "Shuffle Traps")
TriforceHunt = toggle("TriforceHunt", "Triforce Hunt")

StartingRupees = toggle("StartingRupees", "Wallet Full")
StartingConsumables = toggle("StartingConsumables", "Consumables Full")
StartingMapsCompasses = toggle("StartingMapsCompasses", "Maps and Compasses")

HintSpiderHouses = toggle("HintSpiderHouses", "Spider House Hints")
HintGossipStones = toggle("HintGossipStones", "Gossip Stone Static Hints")
HintPurchasable = toggle("HintPurchasable", "Purchasable Gossip Hints")
HintBossRemains = toggle("HintBossRemains", "Boss Remains Hints")
HintOathToOrder = toggle("HintOathToOrder", "Oath to Order Hint")
HintTransformations = toggle("HintTransformations", "Transformation Mask Hints")
HintSongSoaring = toggle("HintSongSoaring", "Song of Soaring Hint")
HintHookshot = toggle("HintHookshot", "Hookshot Hint")
HintBankSign = toggle("HintBankSign", "Bank Reward Hint")


@dataclass
class TwoShipOptions(PerGameCommonOptions):
    check_scope: CheckScope

    logic_mode: LogicMode
    small_key_placement: DungeonItemPlacement
    boss_key_placement: DungeonItemPlacement
    stray_fairy_placement: DungeonItemPlacement
    dungeon_access: DungeonAccess
    majora_remains_required: Count0To4
    majora_masks_required: MaskCount
    moon_remains_required: MoonRemainsRequired
    moon_masks_required: MaskCount
    trials_access: TrialsAccess

    shuffle_owl_statues: ShuffleOwlStatues
    shuffle_shops: ShuffleShops
    shuffle_tingle_shops: ShuffleTingleShops
    shuffle_boss_remains: ShuffleBossRemains
    shuffle_cows: ShuffleCows
    shuffle_gold_skulltulas: ShuffleGoldSkulltulas
    skulltula_tokens_required: SkulltulaCount
    skulltula_tokens_in_pool: SkulltulaCount
    stray_fairies_required: StrayFairyCount
    stray_fairies_in_pool: StrayFairyCount
    shuffle_pot_drops: ShufflePotDrops
    shuffle_crate_drops: ShuffleCrateDrops
    shuffle_barrel_drops: ShuffleBarrelDrops
    shuffle_snowball_drops: ShuffleSnowballDrops
    shuffle_grass_drops: ShuffleGrassDrops
    shuffle_tree_drops: ShuffleTreeDrops
    shuffle_frogs: ShuffleFrogs
    shuffle_freestanding_items: ShuffleFreestandingItems
    shuffle_enemy_drops: ShuffleEnemyDrops

    shuffle_swim: ShuffleSwim
    shuffle_ocarina_buttons: ShuffleOcarinaButtons
    shuffle_song_double_time: ShuffleSongDoubleTime
    shuffle_song_inverted_time: ShuffleSongInvertedTime
    shuffle_song_sun: ShuffleSongSun
    shuffle_song_saria: ShuffleSongSaria
    shuffle_tycoon_wallet: ShuffleTycoonWallet
    plentiful_items: PlentifulItems
    shuffle_boss_souls: ShuffleBossSouls
    shuffle_enemy_souls: ShuffleEnemySouls
    shuffle_time: ShuffleTime
    clock_progression: ClockProgression
    clock_terminal_time: ClockTerminalTime
    shuffle_traps: ShuffleTraps
    trap_amount: TrapAmount
    triforce_hunt: TriforceHunt
    triforce_pieces_required: TriforcePieceCount
    triforce_pieces_in_pool: TriforcePieceCount

    starting_rupees: StartingRupees
    starting_consumables: StartingConsumables
    starting_maps_compasses: StartingMapsCompasses
    starting_health: StartingHealth

    hint_spider_houses: HintSpiderHouses
    hint_gossip_stones: HintGossipStones
    gossip_hint_strength: HintStrength
    hint_purchasable: HintPurchasable
    hint_boss_remains: HintBossRemains
    hint_oath_to_order: HintOathToOrder
    hint_transformations: HintTransformations
    hint_song_soaring: HintSongSoaring
    hint_hookshot: HintHookshot
    hint_bank_sign: HintBankSign


RO_OPTION_FIELDS = {
    "RO_ACCESS_DUNGEONS": "dungeon_access",
    "RO_ACCESS_MAJORA_MASKS_COUNT": "majora_masks_required",
    "RO_ACCESS_MAJORA_REMAINS_COUNT": "majora_remains_required",
    "RO_ACCESS_MOON_MASKS_COUNT": "moon_masks_required",
    "RO_ACCESS_MOON_REMAINS_COUNT": "moon_remains_required",
    "RO_ACCESS_TRIALS": "trials_access",
    "RO_CLOCK_SHUFFLE_PROGRESSIVE": "clock_progression",
    "RO_CLOCK_SHUFFLE": "shuffle_time",
    "RO_CLOCK_TERMINAL_TIME": "clock_terminal_time",
    "RO_HINTS_BANK_SIGN": "hint_bank_sign",
    "RO_HINTS_BOSS_REMAINS": "hint_boss_remains",
    "RO_HINTS_GOSSIP_STONE_STRENGTH": "gossip_hint_strength",
    "RO_HINTS_GOSSIP_STONES": "hint_gossip_stones",
    "RO_HINTS_HOOKSHOT": "hint_hookshot",
    "RO_HINTS_OATH_TO_ORDER": "hint_oath_to_order",
    "RO_HINTS_PURCHASEABLE": "hint_purchasable",
    "RO_HINTS_SONG_OF_SOARING": "hint_song_soaring",
    "RO_HINTS_SPIDER_HOUSES": "hint_spider_houses",
    "RO_HINTS_TRANSFORMATIONS": "hint_transformations",
    "RO_LOGIC": "logic_mode",
    "RO_PLACEMENT_BOSS_KEYS": "boss_key_placement",
    "RO_PLACEMENT_SMALL_KEYS": "small_key_placement",
    "RO_PLACEMENT_STRAY_FAIRIES": "stray_fairy_placement",
    "RO_PLENTIFUL_ITEMS": "plentiful_items",
    "RO_SHUFFLE_BARREL_DROPS": "shuffle_barrel_drops",
    "RO_SHUFFLE_BOSS_REMAINS": "shuffle_boss_remains",
    "RO_SHUFFLE_BOSS_SOULS": "shuffle_boss_souls",
    "RO_SHUFFLE_COWS": "shuffle_cows",
    "RO_SHUFFLE_CRATE_DROPS": "shuffle_crate_drops",
    "RO_SHUFFLE_ENEMY_DROPS": "shuffle_enemy_drops",
    "RO_SHUFFLE_ENEMY_SOULS": "shuffle_enemy_souls",
    "RO_SHUFFLE_FREESTANDING_ITEMS": "shuffle_freestanding_items",
    "RO_SHUFFLE_FROGS": "shuffle_frogs",
    "RO_SHUFFLE_GOLD_SKULLTULAS": "shuffle_gold_skulltulas",
    "RO_SHUFFLE_GRASS_DROPS": "shuffle_grass_drops",
    "RO_SHUFFLE_OCARINA_BUTTONS": "shuffle_ocarina_buttons",
    "RO_SHUFFLE_OWL_STATUES": "shuffle_owl_statues",
    "RO_SHUFFLE_POT_DROPS": "shuffle_pot_drops",
    "RO_SHUFFLE_SHOPS": "shuffle_shops",
    "RO_SHUFFLE_SNOWBALL_DROPS": "shuffle_snowball_drops",
    "RO_SHUFFLE_SONG_DOUBLE_TIME": "shuffle_song_double_time",
    "RO_SHUFFLE_SONG_INVERTED_TIME": "shuffle_song_inverted_time",
    "RO_SHUFFLE_SONG_SARIA": "shuffle_song_saria",
    "RO_SHUFFLE_SONG_SUN": "shuffle_song_sun",
    "RO_SHUFFLE_SWIM": "shuffle_swim",
    "RO_SHUFFLE_TINGLE_SHOPS": "shuffle_tingle_shops",
    "RO_SHUFFLE_TRAPS": "shuffle_traps",
    "RO_SHUFFLE_TYCOON_WALLET": "shuffle_tycoon_wallet",
    "RO_SHUFFLE_TREE_DROPS": "shuffle_tree_drops",
    "RO_SHUFFLE_TRIFORCE_PIECES": "triforce_hunt",
    "RO_SKULLTULA_TOKENS_MAX": "skulltula_tokens_in_pool",
    "RO_SKULLTULA_TOKENS_REQUIRED": "skulltula_tokens_required",
    "RO_STARTING_CONSUMABLES": "starting_consumables",
    "RO_STARTING_HEALTH": "starting_health",
    "RO_STARTING_MAPS_AND_COMPASSES": "starting_maps_compasses",
    "RO_STARTING_RUPEES": "starting_rupees",
    "RO_STRAY_FAIRIES_MAX": "stray_fairies_in_pool",
    "RO_STRAY_FAIRIES_REQUIRED": "stray_fairies_required",
    "RO_TRAP_AMOUNT": "trap_amount",
    "RO_TRIFORCE_PIECES_MAX": "triforce_pieces_in_pool",
    "RO_TRIFORCE_PIECES_REQUIRED": "triforce_pieces_required",
}


option_groups = [
    OptionGroup("Logic and Access", [LogicMode, DungeonItemPlacement, DungeonAccess, TrialsAccess,
                                     Count0To4, MaskCount, MoonRemainsRequired]),
    OptionGroup("Location Shuffles", [ShuffleOwlStatues, ShuffleShops, ShuffleTingleShops,
                                       ShuffleBossRemains, ShuffleCows, ShuffleGoldSkulltulas,
                                       SkulltulaCount, StrayFairyCount, ShufflePotDrops, ShuffleCrateDrops,
                                       ShuffleBarrelDrops, ShuffleSnowballDrops, ShuffleGrassDrops,
                                       ShuffleTreeDrops, ShuffleFrogs, ShuffleFreestandingItems, ShuffleEnemyDrops]),
    OptionGroup("Item Pool", [ShuffleSwim, ShuffleOcarinaButtons, ShuffleSongDoubleTime,
                              ShuffleSongInvertedTime, ShuffleSongSun, ShuffleSongSaria,
                              ShuffleTycoonWallet, PlentifulItems, ShuffleBossSouls, ShuffleEnemySouls,
                              ShuffleTraps, TrapAmount, TriforceHunt, TriforcePieceCount]),
    OptionGroup("Time", [ShuffleTime, ClockProgression, ClockTerminalTime]),
    OptionGroup("Starting Inventory", [StartingRupees, StartingConsumables, StartingMapsCompasses, StartingHealth]),
    OptionGroup("Hints", [HintSpiderHouses, HintGossipStones, HintStrength, HintPurchasable,
                           HintBossRemains, HintOathToOrder, HintTransformations, HintSongSoaring,
                           HintHookshot, HintBankSign]),
]

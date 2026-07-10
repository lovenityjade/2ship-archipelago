# 2Ship Archipelago

Prototype APWorld and native Archipelago client for 2 Ship 2 Harkinian.

The native client source is maintained on the
[`archipelago` branch of TheLovenityJade's 2Ship fork](https://github.com/lovenityjade/2ship2harkinian/tree/archipelago).

`default.yaml` is the generation template for a standard core-check seed.

## Current architecture

- AP item IDs are `74200000 + RandoItemId`.
- AP location IDs are `74210000 + RandoCheckId`.
- The APWorld tables are generated from the native 2Ship enums.
- The WebHost exposes the native seed settings in grouped Logic, Location,
  Item Pool, Time, Starting Inventory, and Hint sections.
- APWorld 0.2 sends 2Ship's `RO_*` settings in slot data and the native client
  applies them before a new randomizer save is created.
- The native client connects from `Rando > Archipelago`.
- Archipelago's launcher exposes a `2Ship Client` component and forwards room
  credentials into `2ship2harkinian.json` before launching the game.
- While connected, eligible randomizer checks are sent to Archipelago instead
  of granting their locally placed item.
- Received AP items are applied through `Rando::GiveItem`.

Select Archipelago mode, configure the connection, and return to File Select.
The file screen exposes `Start Archipelago` only after the slot data and
location scout are synchronized. The client then associates the new save with
its server, slot, and seed and applies the native randomizer settings from the
AP slot.
Full glitchless AP region logic remains the next major generation milestone;
the current world uses a conservative minimal completion model.

## Refresh generated data

```sh
python3 scripts/extract_2ship_data.py
```

## Build note

Do not compile on this PC. On the external build machine, keep the executable
and every audio dependency in the 64-bit `x86_64` dependency chain.

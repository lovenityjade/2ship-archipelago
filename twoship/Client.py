from __future__ import annotations

import asyncio
import json
import os

from CommonClient import get_base_parser, handle_url_arg
from Utils import open_filename

from . import TwoShipWorld


def _save_settings() -> None:
    TwoShipWorld.settings.update({"_dirty": True})
    del TwoShipWorld.settings._dirty


def launch(*launch_args: str) -> None:
    async def main() -> None:
        parser = get_base_parser(description="2 Ship 2 Harkinian Client")
        parser.add_argument("--name", default=None, help="Archipelago slot name")
        args, uri = parser.parse_known_args(launch_args)

        hostname = None
        slot_name = args.name
        password = ""
        if uri and uri[0].startswith("archipelago://"):
            args.url = uri[0]
            handle_url_arg(args, parser)
            hostname = f"{args.url.hostname}:{args.url.port}"
            password = "" if args.password == "None" else args.password

        executable = TwoShipWorld.settings.executable_path
        if not executable or not os.path.isfile(executable):
            executable = os.path.abspath(open_filename(
                "Select the Archipelago-enabled 2Ship executable",
                (("2Ship", (".appimage", ".elf", ".exe")), ("Any File", "")),
                "",
            ))
            if not os.path.isfile(executable):
                return
            TwoShipWorld.settings.executable_path = executable
            _save_settings()

        directory = TwoShipWorld.settings.settings_folder
        if not directory or not os.path.isdir(directory):
            directory = os.path.dirname(executable)
            TwoShipWorld.settings.settings_folder = directory
            _save_settings()

        config_path = os.path.join(directory, "2ship2harkinian.json")
        config = {}
        if os.path.isfile(config_path):
            with open(config_path, "r", encoding="utf-8") as config_file:
                config = json.load(config_file)

        if hostname and slot_name:
            archipelago = config.setdefault("CVars", {}).setdefault("gRemote", {}).setdefault("Archipelago", {})
            archipelago["ServerAddress"] = hostname
            archipelago["SlotName"] = slot_name
            archipelago["Password"] = password
            with open(config_path, "w", encoding="utf-8") as config_file:
                json.dump(config, config_file, indent=4)

        process = await asyncio.create_subprocess_exec(executable, cwd=directory)
        await process.wait()

    asyncio.run(main())

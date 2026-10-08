#!/usr/bin/env python3

import os
import re
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path


SECTION = re.compile(r"^\[([^\]]+)\]\s*$")
SETTING = re.compile(r"^\s*([^=]+?)\s*=\s*(.*?)\s*$")


def install_menu(source: Path, destination: Path) -> None:
    root = ET.parse(source).getroot()
    if root.tag != "Menu":
        raise ValueError(f"{source} is not an XDG application menu")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as temp:
        temp_path = Path(temp.name)
    try:
        shutil.copyfile(source, temp_path)
        os.chmod(temp_path, 0o644)
        os.replace(temp_path, destination)
    finally:
        temp_path.unlink(missing_ok=True)


def configure_panel(panel: Path, default_panel: Path, menu: Path) -> None:
    if not panel.exists():
        panel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(default_panel, panel)

    lines = panel.read_text(encoding="utf-8").splitlines()
    sections: dict[str, tuple[int, int]] = {}
    current = None
    for index, line in enumerate(lines):
        match = SECTION.match(line)
        if match:
            if current is not None:
                sections[current] = (sections[current][0], index)
            current = match.group(1)
            sections[current] = (index, len(lines))

    def values(section: str) -> dict[str, str]:
        start, end = sections[section]
        result = {}
        for line in lines[start + 1 : end]:
            match = SETTING.match(line)
            if match:
                result[match.group(1).strip()] = match.group(2)
        return result

    active_plugins = {
        plugin.strip()
        for section in sections
        for key, value in values(section).items()
        if key == "plugins"
        for plugin in value.split(",")
        if plugin.strip()
    }
    menu_sections = []
    for name in active_plugins:
        if name not in sections:
            continue
        plugin_type = values(name).get("type", "").lower()
        if plugin_type in {"fancymenu", "mainmenu"} or name.startswith(
            ("fancymenu", "mainmenu")
        ):
            menu_sections.append(name)

    if not menu_sections:
        raise ValueError(f"No active LXQt application menu plugin found in {panel}")

    for name in sorted(menu_sections, key=lambda item: sections[item][0], reverse=True):
        start, end = sections[name]
        key_lines = [
            index
            for index in range(start + 1, end)
            if (match := SETTING.match(lines[index]))
            and match.group(1).strip() == "menu_file"
        ]
        if key_lines:
            lines[key_lines[0]] = f"menu_file={menu}"
            for index in reversed(key_lines[1:]):
                del lines[index]
        else:
            lines.insert(start + 1, f"menu_file={menu}")

    panel.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit(
            "Usage: configure-lxqt-menu.py PANEL_CONFIG DEFAULT_PANEL MENU_SOURCE MENU_DESTINATION"
        )
    panel, default_panel, menu_source, menu_destination = map(Path, sys.argv[1:])
    install_menu(menu_source, menu_destination)
    configure_panel(panel, default_panel, menu_destination)


if __name__ == "__main__":
    main()

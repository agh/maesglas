"""Load the identity contract without implicit modes or color fallbacks."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from colors import srgb

ROOT = Path(__file__).resolve().parents[1]
MODES = ("chalk", "shale")


def mapping(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("Expected an object with string keys")
    contents = cast(dict[object, object], value)
    if not all(isinstance(k, str) for k in contents):
        raise ValueError("Expected an object with string keys")
    return {str(k): v for k, v in contents.items()}


def sequence(value: object) -> list[object]:
    if not isinstance(value, list):
        raise ValueError("Expected an array")
    contents = cast(list[object], value)
    return contents


def text(value: object) -> str:
    if not isinstance(value, str):
        raise ValueError("Expected a string")
    return value


def number(value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("Expected a number")
    return float(value)


def load_json(path: Path) -> dict[str, object]:
    value: object = json.loads(path.read_text())
    return mapping(value)


@dataclass(frozen=True)
class Design:
    raw: dict[str, object]
    colors: dict[str, dict[str, str]]
    coordinates: dict[str, dict[str, list[float]]]
    roles: dict[str, str]
    ansi: list[str]
    grounds: list[str]

    @property
    def version(self) -> str:
        return text(self.raw["version"])

    def leaf(self, section: str, name: str | None = None) -> object:
        value = mapping(self.raw[section])
        if name is not None:
            value = mapping(value[name])
        if set(value) != {"type", "value", "unit"}:
            raise ValueError(f"Incomplete identity leaf: {section}")
        return value["value"]


def load(path: Path = ROOT / "identity/maesglas.json") -> Design:
    raw = load_json(path)
    if raw["conversion"] != "oklab-d65-2021-srgb-half-up-v1":
        raise ValueError("Unknown color conversion")
    if raw["default"] != "chalk":
        raise ValueError("Chalk is the default")
    palettes = mapping(raw["palette"])
    if set(palettes) != set(MODES):
        raise ValueError("Both complete modes are required")
    coordinates: dict[str, dict[str, list[float]]] = {}
    colors: dict[str, dict[str, str]] = {}
    for mode in MODES:
        coordinates[mode] = {}
        for key, value in mapping(palettes[mode]).items():
            leaf = mapping(value)
            if set(leaf) != {"type", "value", "unit"}:
                raise ValueError(f"Incomplete color leaf: {mode}/{key}")
            if leaf["type"] != "color" or leaf["unit"] != "oklch":
                raise ValueError(f"Invalid color leaf: {mode}/{key}")
            coordinates[mode][key] = [number(v) for v in sequence(leaf["value"])]
        colors[mode] = {key: srgb(value) for key, value in coordinates[mode].items()}
    if colors["chalk"].keys() != colors["shale"].keys():
        raise ValueError("Modes have different roles")
    roles: dict[str, str] = {}
    for key, value in mapping(raw["roles"]).items():
        leaf = mapping(value)
        if leaf["type"] != "color" or leaf["unit"] != "srgb":
            raise ValueError(f"Invalid role: {key}")
        alias = text(leaf["value"])
        if not alias.startswith("{") or not alias.endswith("}"):
            raise ValueError(f"Expected an alias: {key}")
        target = alias[1:-1]
        if target not in colors["chalk"]:
            raise ValueError(f"Missing alias target: {key}")
        roles[key] = target
        for mode in MODES:
            colors[mode][key] = colors[mode][target]
    ansi = [text(v) for v in sequence(raw["ansi"])]
    grounds = [text(v) for v in sequence(raw["grounds"])]
    if len(ansi) != 16 or not grounds or "canvas" not in grounds:
        raise ValueError("Missing ANSI slots or grounds")
    for name in ansi + grounds:
        if name not in coordinates["chalk"]:
            raise ValueError(f"Missing palette entry: {name}")
    expected = set(ansi + grounds + list(roles.values()) + ["boundary"])
    if set(coordinates["chalk"]) != expected:
        raise ValueError("Every primitive must have an audited use")
    return Design(raw, colors, coordinates, roles, ansi, grounds)

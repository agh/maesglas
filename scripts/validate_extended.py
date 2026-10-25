"""Validate additional ports without application windows or personal configuration."""

import argparse
import datetime
import hashlib
import json
import math
import platform
import plistlib
import re
import shutil
import subprocess
import tempfile
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import TypeGuard

from bootstrap_ports import sources
from colors import wcag
from extra_ports import CLAUDE_BACKGROUNDS, CLAUDE_ROLES, METHODS, PORTS, claude_code, highlights
from jsonschema import Draft7Validator, Draft202012Validator, FormatChecker
from jsonschema.protocols import Validator
from model import MODES, ROOT, load, load_json, mapping, sequence, text
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7
from validate_ports import environment, has_color, run, terminal

CACHE = ROOT / ".cache"
MAC_NATIVE = {"alacritty", "kitty", "wezterm", "neovim", "helix", "iterm2"}
SUPPORT = [
    "scripts/validate_extended.py",
    "scripts/vscode_schema.mjs",
    "scripts/probes/k9s.go",
    "scripts/probes/gh_dash.go",
    "scripts/bootstrap_ports.py",
]
EXECUTABLES = {
    "alacritty": "apps/alacritty/Alacritty/Alacritty.app/Contents/MacOS/alacritty",
    "kitty": "apps/kitty/kitty.app/Contents/MacOS/kitty",
    "wezterm": (
        "apps/wezterm/WezTerm-macos-20240203-110809-5046fc22/WezTerm.app/Contents/MacOS/wezterm"
    ),
    "neovim": "apps/neovim/nvim-macos-arm64/bin/nvim",
    "helix": "apps/helix/helix-25.07.1-aarch64-macos/hx",
    "k9s": "tools/bin/maesglas-k9s-validate",
    "gh-dash": "tools/bin/maesglas-gh-dash-validate",
}

type JSONValue = str | int | float | bool | None | dict[str, JSONValue] | list[JSONValue]


def is_dict(value: object) -> TypeGuard[dict[object, object]]:
    return isinstance(value, dict)


def is_list(value: object) -> TypeGuard[list[object]]:
    return isinstance(value, list)


def json_value(value: object) -> JSONValue:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if is_dict(value):
        return {key: json_value(child) for key, child in mapping(value).items()}
    if is_list(value):
        return [json_value(child) for child in value]
    raise ValueError("Schema input is not JSON")


def validate_schema(validator: Validator, data: object) -> None:
    validator.validate(json_value(data))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_colors(value: object, palette: dict[str, str]) -> None:
    if isinstance(value, str):
        if re.fullmatch(r"#[0-9a-fA-F]{6}", value) and value.upper() not in set(palette.values()):
            raise ValueError(f"Color outside the palette: {value}")
    elif is_dict(value):
        for child in mapping(value).values():
            check_colors(child, palette)
    elif is_list(value):
        for child in sequence(value):
            check_colors(child, palette)


def check_skin_colors(value: object, palette: dict[str, str]) -> None:
    if is_dict(value):
        for key, child in mapping(value).items():
            if key != "fgStyle":
                check_skin_colors(child, palette)
    elif is_list(value):
        for child in value:
            check_skin_colors(child, palette)
    elif not isinstance(value, str) or value not in set(palette.values()):
        raise ValueError("FG-K9S-TRUECOLOR: every skin color must be palette hex")


def readable(foreground: str, background: str, label: str) -> None:
    if wcag(foreground, background) < 4.5:
        raise ValueError(f"Contrast below 4.5: {label}")


def audit_matches(data: dict[str, object], mode: str) -> None:
    colors = mapping(data["colors"])
    p = load().colors[mode]
    foregrounds = [
        text(mapping(mapping(rule)["settings"])["foreground"])
        for rule in sequence(data["tokenColors"])
    ]
    foregrounds.extend(text(value) for value in mapping(data["semanticTokenColors"]).values())
    for suffix in ("", "Highlight"):
        ground = text(colors[f"editor.findMatch{suffix}Background"])
        fg = text(colors[f"editor.findMatch{suffix}Foreground"])
        if fg != p["ink"] or ground != p["match-active" if not suffix else "match"]:
            raise ValueError("LEG-01 search roles differ from the palette")
        for foreground in foregrounds + [fg]:
            readable(foreground, ground, f"vscode/{mode}/findMatch{suffix}")


def vscode_schemas(env: dict[str, str], root: Path) -> dict[str, object]:
    schemas = mapping(
        json.loads(
            run(
                [
                    "node",
                    str(ROOT / "scripts/vscode_schema.mjs"),
                    str(CACHE / "apps/vscode-source"),
                ],
                env,
                root,
            )
        )
    )
    registry: set[str] = set()
    for path in (CACHE / "apps/vscode-source/src/vs").rglob("*.ts"):
        content = path.read_text()
        registry.update(re.findall(r"registerColor\(\s*['\"]([^'\"]+)['\"]", content))
        if path.name == "terminalColorRegistry.ts":
            registry.update(re.findall(r"['\"](terminal\.ansi\w+)['\"]", content))
    schemas["workbenchColorsSchema"] = {
        "type": "object",
        "properties": {key: {"type": "string", "format": "color-hex"} for key in registry},
        "additionalProperties": False,
    }
    return schemas


def validate_vscode(data: dict[str, object], schemas: dict[str, object], mode: str) -> None:
    checker = FormatChecker()

    def color_hex(value: object) -> bool:
        return (
            isinstance(value, str)
            and re.fullmatch(r"#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", value)
            is not None
        )

    checker.checks("color-hex")(color_hex)

    registry: Registry[bool | Mapping[str, object]] = Registry()
    for uri, key in (
        ("vscode://schemas/workbench-colors", "workbenchColorsSchema"),
        ("vscode://schemas/textmate-colors", "textmateColorSchema"),
        ("vscode://schemas/token-styling", "tokenStylingSchema"),
    ):
        contents: bool | Mapping[str, object] = mapping(schemas[key])
        resource = Resource.from_contents(contents, default_specification=DRAFT7)
        registry = registry.with_resource(uri, resource)
    # VS Code combines a referenced registry with additionalProperties at the use site.
    schema = mapping(schemas["colorThemeSchema"])
    properties = mapping(schema["properties"])
    properties["colors"] = schemas["workbenchColorsSchema"]
    schema["properties"] = properties
    validate_schema(Draft7Validator(schema, registry=registry, format_checker=checker), data)
    audit_matches(data, mode)


def strict_schema(schema: dict[str, object]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in schema.items():
        if is_dict(value):
            result[key] = strict_schema(mapping(value))
        elif is_list(value):
            result[key] = [
                strict_schema(mapping(child)) if is_dict(child) else child
                for child in sequence(value)
            ]
        else:
            result[key] = value
    if result.get("type") == "object" and "properties" in result:
        result["additionalProperties"] = False
    return result


def lower_keys(value: object) -> object:
    if is_dict(value):
        return {key.lower(): lower_keys(child) for key, child in mapping(value).items()}
    if is_list(value):
        return [lower_keys(child) for child in sequence(value)]
    return value


def check_iterm(path: Path, p: dict[str, str], env: dict[str, str], root: Path) -> None:
    run(["plutil", "-lint", str(path)], env, root)
    presets = mapping(plistlib.loads((CACHE / "upstream/iterm-colors.plist").read_bytes()))
    keys = set(mapping(presets["Regular"]))
    values = mapping(plistlib.loads(path.read_bytes()))
    if not set(values) <= keys or len(values) != 24:
        raise ValueError("Unknown or missing iTerm2 color keys")
    delivered: set[str] = set()
    for value in values.values():
        channels = mapping(value)
        if channels["Color Space"] != "sRGB":
            raise ValueError("iTerm2 profile is not sRGB")
        rgb = [channels[channel + " Component"] for channel in ("Red", "Green", "Blue")]
        if not all(isinstance(channel, float) and 0 <= channel <= 1 for channel in rgb):
            raise ValueError("Invalid iTerm2 channel")
        delivered.add("#" + "".join(f"{round(float(str(channel)) * 255):02X}" for channel in rgb))
    if not delivered <= set(p.values()):
        raise ValueError("iTerm2 color round-trip changed a palette value")


def claude_registry() -> tuple[set[str], str]:
    if platform.system() != "Darwin":
        record = mapping(load_json(ROOT / "identity/port-validation.json")["Darwin"])
        return (
            {text(role) for role in sequence(record["claude_roles"])},
            text(mapping(record["executables"])["installed:claude-code"]),
        )
    binary = shutil.which("claude")
    if binary is None:
        raise ValueError("Missing installed Claude Code token registry")
    payload = Path(binary).read_bytes()
    palettes: list[set[str]] = []
    for match in re.finditer(rb'userMessageBackground:"(?:rgb\(|ansi:)', payload):
        position = match.start()
        start = payload.rfind(b"{", max(0, position - 10000), position)
        end = payload.find(b"}", position)
        palettes.append(
            {key.decode() for key in re.findall(rb'(\w+):"(?:rgb\(|ansi:)', payload[start:end])}
        )
    if len(palettes) != 6 or any(keys != set(CLAUDE_ROLES) for keys in palettes):
        raise ValueError("Installed Claude Code registry was not found")
    for key in ("diffAddedWord", "diffRemovedWord"):
        if f'color:"{key}"'.encode() not in payload:
            raise ValueError("Claude Code shared-token foreground usage changed")
    if b"backgroundColor:P" not in payload:
        raise ValueError("Claude Code word-background renderer changed")
    return palettes[0], hashlib.sha256(payload).hexdigest()


def claude_rejection(keys: set[str]) -> dict[str, object]:
    if keys != set(CLAUDE_ROLES):
        raise ValueError("Claude Code token coverage changed")
    bounds: dict[str, object] = {}
    design = load()
    for mode, p in design.colors.items():
        candidate = mapping(json.loads(claude_code(p, mode)))
        overrides = mapping(candidate["overrides"])
        for key in keys - CLAUDE_BACKGROUNDS:
            for ground in design.grounds:
                readable(text(overrides[key]), p[ground], f"claude-code/{mode}/{key}/{ground}")
        best = math.sqrt(wcag(p["ink"], p["canvas"]))
        if best >= 4.5:
            raise ValueError("Claude Code shared-token blocker changed; reconsider the port")
        bounds[mode] = {
            "ink_canvas_contrast": wcag(p["ink"], p["canvas"]),
            "maximum_simultaneous_contrast": best,
            "candidate_counter_contrast": {
                key: wcag(text(overrides[key]), p["canvas"])
                for key in ("diffAddedWord", "diffRemovedWord")
            },
            "candidate_word_text_contrast": {
                key: wcag(p["ink"], text(overrides[key]))
                for key in ("diffAddedWord", "diffRemovedWord")
            },
        }
    return {
        "version": load_json(ROOT / "tools.lock")["claude-code"],
        "documentation": mapping(load_json(ROOT / "tools.lock")["historical_references"])[
            "claude-code-documentation"
        ],
        "overridden_tokens": len(keys),
        "method": (
            "All six installed base registries and shared renderer roles inspected; "
            "all accepted foregrounds overridden and audited. Counter foregrounds "
            "and word backgrounds use the same two tokens; inline word text inherits "
            "the normal text role, with no independent theme override."
        ),
        "unoverridable_role": "word-diff text independent of the normal text role",
        "bounds": bounds,
    }


def native_neovim(
    binary: str, path: Path, p: dict[str, str], mode: str, env: dict[str, str], root: Path
) -> None:
    runtime = root / "nvim"
    (runtime / "colors").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, runtime / "colors" / path.name)
    lines = [
        f"vim.opt.runtimepath:prepend({json.dumps(str(runtime))})",
        f"vim.cmd.colorscheme('maesglas-{mode}')",
        f"assert(vim.g.colors_name == 'maesglas-{mode}')",
    ]
    for group, (fg, bg) in highlights().items():
        lines.extend(
            [
                f"local h = vim.api.nvim_get_hl(0, {{name={json.dumps(group)}, link=false}})",
                f"assert(h.fg == {int(p[fg][1:], 16)} and h.bg == {int(p[bg][1:], 16)}, "
                f"{json.dumps(group)})",
            ]
        )
    for i, role in enumerate(load().ansi):
        lines.append(f"assert(vim.g.terminal_color_{i} == '{p[role]}')")
    for level, role in (
        ("Error", "error"),
        ("Warn", "warning"),
        ("Info", "type"),
        ("Hint", "comment"),
        ("Ok", "success"),
    ):
        lines.append(
            f"assert(vim.api.nvim_get_hl(0, {{name='DiagnosticUnderline{level}'}}).sp "
            f"== {int(p[role][1:], 16)})"
        )
    allowed = ", ".join(f"[{int(color[1:], 16)}]=true" for color in set(p.values()))
    lines.extend(
        [
            f"local allowed = {{{allowed}}}",
            "for name, group in pairs(vim.api.nvim_get_hl(0, {link=false})) do",
            "  for _, key in ipairs({'fg', 'bg', 'sp'}) do",
            "    assert(not group[key] or allowed[group[key]], name .. '/' .. key)",
            "  end",
            "end",
        ]
    )
    probe = root / f"nvim-{mode}.lua"
    probe.write_text("\n".join(lines) + "\n")
    run([binary, "--headless", "-u", "NONE", "-i", "NONE", "-n", "-l", str(probe)], env, root)


def native_kitty(binary: str, path: Path, env: dict[str, str], root: Path) -> None:
    expected = dict(re.findall(r"^(\w+) (#[0-9A-F]{6})$", path.read_text(), re.M))
    program = (
        "from kitty.config import load_config; "
        f"expected={expected!r}; bad=[]; "
        f"o=load_config({str(path)!r}, accumulate_bad_lines=bad); "
        "assert not bad, bad; "
        "actual={key:getattr(o,key).as_sharp.upper() for key in expected}; "
        "assert actual == expected, (actual,expected)"
    )
    run([binary, "+runpy", program], env, root)


def native_wezterm(binary: str, path: Path, env: dict[str, str], root: Path) -> None:
    data = tomllib.loads(path.read_text())
    colors = mapping(data["colors"])
    lines = [
        "local w = require('wezterm')",
        f"local c = w.color.load_scheme({json.dumps(str(path))})",
    ]
    for key, value in colors.items():
        if isinstance(value, str):
            lines.append(
                f"assert(tostring(w.color.parse(c.{key})) "
                f"== tostring(w.color.parse('{value}')), '{key}')"
            )
        else:
            for i, color in enumerate(sequence(value), 1):
                lines.append(
                    f"assert(tostring(w.color.parse(c.{key}[{i}])) "
                    f"== tostring(w.color.parse('{text(color)}')), '{key}{i}')"
                )
    lines.append("return { color_schemes = { Maesglas = c }, color_scheme = 'Maesglas' }")
    probe = root / "wezterm.lua"
    probe.write_text("\n".join(lines) + "\n")
    run([binary, "--config-file", str(probe), "show-keys", "--lua"], env, root)


def highlighter(path: Path, mode: str, env: dict[str, str], root: Path) -> None:
    work = root / f"fsyh-{mode}"
    work.mkdir()
    (work / "secondary_theme.zsh").write_text("")
    script = root / f"fsyh-{mode}.zsh"
    script.write_text(
        f"source {json.dumps(str(CACHE / 'apps/fsyh/F-Sy-H.plugin.zsh'))}\n"
        f"source {json.dumps(str(path))}\n"
        "-fast-highlight-process '' 'echo $(printf \"%s\" \"$value\") $((12 + 3)) # orchard' 0\n"
        "print -r -- BEGIN_STYLES\n"
        'for key value in ${(kv)FAST_HIGHLIGHT_STYLES}; do print -r -- "$key=$value"; done\n'
        "print -r -- BEGIN_REGIONS\n"
        "print -rl -- $reply\n"
    )
    result = run(
        ["zsh", "-d", "-f", str(script)],
        env | {"ZDOTDIR": str(work), "FAST_WORK_DIR": str(work)},
        root,
    )
    styles, regions = result.split("BEGIN_STYLES\n", 1)[1].split("BEGIN_REGIONS\n", 1)
    if len(styles.splitlines()) < 150 or "fg=" not in regions:
        raise ValueError("Highlighter did not populate and exercise its styles")
    if re.search(r"(?:fg|bg)=(?:\d+|#[0-9a-fA-F]+)", styles + regions):
        raise ValueError("COV-01: highlighter retained a fixed indexed or RGB color")
    if re.search(r"(?:^|[,\s])(?:bg=|reverse\b|standout\b)", styles + regions, re.M):
        raise ValueError("Highlighter inverted text onto an ANSI foreground")
    if f"maesglas-{mode}secondary=maesglas-{mode}" not in styles:
        raise ValueError("Highlighter recursive theme was not replaced")


def validate(root: Path, selected: set[str]) -> dict[str, str]:
    env = environment(root)
    results: dict[str, str] = {}
    schemas = vscode_schemas(env, root) if "vscode" in selected else {}
    zed_schema = strict_schema(load_json(CACHE / "upstream/zed-schema.json"))
    zed_schema["properties"] = mapping(zed_schema["properties"]) | {
        "$schema": {"type": "string"},
    }
    windows_schema = load_json(CACHE / "upstream/terminal-schema.json")
    for mode in MODES:
        p = load().colors[mode]
        for port in sorted(selected):
            path = ROOT / f"ports/{port}/maesglas-{mode}.{PORTS[port][1]}"
            content = path.read_text()
            for color in re.findall(r"#[0-9a-fA-F]{6}\b", content):
                check_colors(color, p)
            data: dict[str, object] = {}
            if path.suffix in (".json", ".yml", ".yaml"):
                data = load_json(path)
                check_colors(data, p)
            binary = str(CACHE / EXECUTABLES[port]) if port in EXECUTABLES else ""
            if port in MAC_NATIVE and platform.system() != "Darwin":
                continue
            if port == "alacritty":
                result = run(
                    [binary, "migrate", "--dry-run", "--config-file", str(path)], env, root
                )
                match = re.search(r"(?s)\n\n(\[colors\..*?)\n\^-----", result)
                if not match or tomllib.loads(match[1]) != tomllib.loads(content):
                    raise ValueError("Alacritty migration changed the generated colors")
            elif port == "kitty":
                native_kitty(binary, path, env, root)
            elif port == "wezterm":
                native_wezterm(binary, path, env, root)
            elif port == "neovim":
                native_neovim(binary, path, p, mode, env, root)
            elif port == "helix":
                allowed = set(
                    re.findall(
                        r"`((?:ui|diagnostic)\.[\w.-]+)`",
                        (CACHE / "upstream/helix-themes.md").read_text(),
                    )
                )
                for key in tomllib.loads(content):
                    if (
                        key.startswith(("ui.", "diagnostic."))
                        and key not in allowed
                        and not any(name.startswith(key + ".") for name in allowed)
                    ):
                        raise ValueError(f"Unknown Helix theme key: {key}")
                config = root / "helix.toml"
                config.write_text(f'theme = "maesglas-{mode}"\n[editor]\ntrue-color = true\n')
                themes = root / "config/helix/themes"
                themes.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, themes / path.name)
                log = root / f"helix-{mode}.log"
                result = terminal(
                    [binary, "-c", str(config), "--log", str(log), str(config)], env, root, b":q!\r"
                )
                if not has_color(result, p["ink"]):
                    raise ValueError("Helix did not apply the theme")
                if log.exists() and re.search(
                    r"(?i)(failed.*theme|invalid.*theme|unknown.*theme)", log.read_text()
                ):
                    raise ValueError("Helix reported a theme loading failure")
            elif port == "vscode":
                validate_vscode(data, schemas, mode)
                package = load_json(ROOT / "ports/vscode/package.json")
                contributions = sequence(mapping(package["contributes"])["themes"])
                if len(contributions) != 2:
                    raise ValueError("VS Code extension must contribute both variants")
                for value in contributions:
                    theme = mapping(value)
                    if not (path.parent / text(theme["path"])).is_file():
                        raise ValueError("VS Code theme contribution is missing")
            elif port == "zed":
                validate_schema(Draft7Validator(zed_schema), data)
            elif port == "iterm2":
                check_iterm(path, p, env, root)
            elif port == "windows-terminal":
                validate_schema(
                    Draft202012Validator(
                        {
                            "$defs": windows_schema["$defs"],
                            "$ref": "#/$defs/SchemeList",
                        }
                    ),
                    [data],
                )
                scheme = mapping(mapping(windows_schema["$defs"])["SchemeList"])
                required = set(mapping(mapping(scheme["items"])["properties"]))
                if set(data) != required:
                    raise ValueError("Windows Terminal scheme is incomplete")
            elif port == "k9s":
                actual = mapping(json.loads(run([binary, str(path)], env, root)))
                if lower_keys(actual) != lower_keys(data):
                    raise ValueError("k9s did not consume every skin field")
                check_skin_colors(actual, p)
            elif port == "gh-dash":
                actual = mapping(json.loads(run([binary, str(path)], env, root)))
                if lower_keys(actual["Colors"]) != lower_keys(mapping(data["theme"])["colors"]):
                    raise ValueError("FG-GHDASH-KEYS: native parser changed or ignored a field")
                rendered = mapping(actual["Theme"])
                for key, value in rendered.items():
                    if is_dict(value):
                        channels = mapping(value)
                        if key == "UnknownRoleIconColor":
                            if channels != {"Light": 178, "Dark": 178}:
                                raise ValueError("gh-dash unknown-role limitation changed")
                            continue
                        colors = {
                            appearance: "#"
                            + "".join(
                                f"{int(str(mapping(color)[channel])):02X}"
                                for channel in ("R", "G", "B")
                            )
                            for appearance, color in channels.items()
                        }
                        if set(colors.values()) - set(p.values()):
                            raise ValueError(f"gh-dash retained an unthemed color: {key}")
                        rendered[key] = colors
                for key, role in (("InvertedText", "ink"), ("WarningText", "warning")):
                    if set(mapping(rendered[key]).values()) != {p[role]}:
                        raise ValueError(f"gh-dash rendered the wrong {key}")
            elif port == "fast-syntax-highlighting":
                highlighter(path, mode, env, root)
            else:
                raise ValueError(f"No validator for {port}")
            results[f"{port}/{mode}"] = "PASS"
    return results


def inputs() -> dict[str, str]:
    paths = [ROOT / name for name in SUPPORT]
    paths.extend(
        path for port in PORTS for path in (ROOT / "ports" / port).rglob("*") if path.is_file()
    )
    return {str(path.relative_to(ROOT)): digest(path) for path in sorted(paths)}


def evidence() -> None:
    records = load_json(ROOT / "identity/port-validation.json")
    lock = load_json(ROOT / "tools.lock")
    record = mapping(records["Darwin"])
    expected = {f"{port}/{mode}": "PASS" for port in PORTS for mode in MODES}
    if record["checks"] != expected or record["inputs"] != inputs():
        raise ValueError("Stale or incomplete extended port evidence; record a complete macOS run")
    if record["versions"] != {port: lock[port] for port in PORTS}:
        raise ValueError("Stale extended port tool pins")
    if record["sources"] != lock["port_sources"]:
        raise ValueError("Stale extended port source pins")
    if record["rejections"] != {"claude-code": claude_rejection(set(CLAUDE_ROLES))}:
        raise ValueError("Stale shared-token contrast rejection")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=PORTS)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    if args.record and (args.only or platform.system() != "Darwin"):
        raise SystemExit("Record a complete macOS run, not selected ports or foreign binaries.")
    sources()
    selected = set(args.only or PORTS)
    native = selected if platform.system() == "Darwin" else selected - MAC_NATIVE
    lock = load_json(ROOT / "tools.lock")
    executables: dict[str, str] = {}
    for port in sorted(native & set(EXECUTABLES)):
        path = CACHE / EXECUTABLES[port]
        if not path.is_file():
            raise SystemExit(f"Missing native validator: {port}; run bootstrap_ports.py")
        executables[EXECUTABLES[port]] = digest(path)
    for tool in ("node", "zsh"):
        result = subprocess.run([tool, "--version"], capture_output=True, text=True, check=True)
        if text(lock[tool]) not in result.stdout:
            raise SystemExit(f"Wrong validator version: {tool}")
    with tempfile.TemporaryDirectory(prefix="extra-ports-", dir=CACHE) as directory:
        root = Path(directory)
        env = environment(root / "version")
        for port in sorted((native & MAC_NATIVE) - {"iterm2"}):
            result_text = run([str(CACHE / EXECUTABLES[port]), "--version"], env, root)
            if text(lock[port]) not in result_text:
                raise SystemExit(f"Wrong native validator version: {port}")
        if platform.system() == "Darwin":
            claude_version = run(["claude", "--version"], env, root)
            if text(lock["claude-code"]) not in claude_version:
                raise SystemExit("Wrong Claude Code version")
        roles, binary_digest = claude_registry()
        executables["installed:claude-code"] = binary_digest
        rejected = claude_rejection(roles)
        results = validate(root / "cases", selected)
    if args.record:
        records = {
            "Darwin": {
                "date": datetime.date.today().isoformat(),
                "checks": results,
                "methods": METHODS,
                "claude_roles": sorted(roles),
                "rejections": {"claude-code": rejected},
                "inputs": inputs(),
                "executables": executables,
                "versions": {port: lock[port] for port in PORTS},
                "sources": lock["port_sources"],
            }
        }
        (ROOT / "identity/port-validation.json").write_text(json.dumps(records, indent=2) + "\n")
    elif not args.only:
        evidence()
        record = mapping(load_json(ROOT / "identity/port-validation.json")["Darwin"])
        if platform.system() == "Darwin" and record["executables"] != executables:
            raise ValueError("Native validator executable changed; record a complete run")
    (CACHE / "extra-ports.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"PASS extended ports: {len(results)} native or schema checks")
    print("PASS Claude Code rejection: shared counter/fill tokens cannot meet both 4.5:1 pairs")
    if platform.system() != "Darwin":
        print("macOS-only native checks are covered by the digest-bound Darwin record")


if __name__ == "__main__":
    main()

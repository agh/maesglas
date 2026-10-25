"""Public prose and measured reference tables derived from the identity."""

import html
import json
import math

import extra_ports
import guidance
from colors import MACHADO, SYNTAX_PAIRS, apca, simulated_distance, wcag
from model import ROOT, Design, load_json, mapping, number, sequence, text
from plates import SCENES, dimensions, mark, plain
from port_renderers import ALL_PORTS as PORTS
from port_renderers import DROPPED


def stamp(port: str) -> str:
    lock = load_json(ROOT / "tools.lock")
    if port == "textmate":
        return (
            f"[checked: bat {text(lock['bat'])} and delta {text(lock['delta'])}, "
            f"{text(lock['checked'])}]"
        )
    key = "bat" if port == "textmate" else port
    label = "Claude Code" if port == "claude-code" else PORTS[port][0]
    return f"[checked: {label} {text(lock[key])}, {text(lock['checked'])}]"


def install_lines(port: str) -> list[str]:
    extension = PORTS[port][1]
    target = f"maesglas-chalk.{extension}"
    prepare = 'mkdir -p "${THEME_DIR:?Choose a destination directory}"'
    if port == "eza":
        target = "theme.yml"
    elif port == "yazi":
        target = "theme.toml"
        prepare = 'mkdir -p "${THEME_DIR:?Choose a destination directory}/flavors"'
    if port == "vscode":
        return [
            'mkdir -p "${THEME_DIR:?Choose an extensions directory}/maesglas"',
            'cp ports/vscode/*.json ports/vscode/LICENSE "$THEME_DIR/maesglas/"',
        ]
    install = f'cp ports/{port}/maesglas-chalk.{extension} "$THEME_DIR/{target}"'
    if port == "yazi":
        install += ' && cp -R ports/yazi/maesglas-chalk.yazi "$THEME_DIR/flavors/"'
    return [prepare, install]


def port_installation(port: str) -> list[str]:
    name, _, note = PORTS[port]
    if port == "gh-dash":
        note += " Fixed status icons are not contrast-certified; see the port notes."
    lines = [
        "<details>",
        f"<summary>{name}</summary>",
        "",
        f"{note} {stamp(port)}",
        "",
        "```sh",
        *install_lines(port),
        "```",
        "",
    ]
    activation = {
        "ghostty": ("text", "config-file = /path/to/maesglas-chalk.conf"),
        "starship": ("sh", 'export STARSHIP_CONFIG="$THEME_DIR/maesglas-chalk.toml"'),
    }
    if port in activation:
        language, setting = activation[port]
        lines.extend(
            [
                "After copying, load the preset with the following setting.",
                "Replace `/path/to` with your chosen directory when editing a configuration file.",
                f"{stamp(port)}",
                "",
                f"```{language}",
                setting,
                "```",
                "",
            ]
        )
    return [*lines, "</details>", ""]


def installation(d: Design) -> str:
    lines = [
        "# Installation",
        "",
        "Choose one variant across the terminal and its tools. The examples use",
        "`chalk`; substitute `shale` for the dark companion. Set `THEME_DIR` to",
        "the destination you chose for that application. Back up existing files",
        "before copying. These files change appearance, not your shell setup.",
        "",
        "Extract the ports archive and run the copy commands from its root, where",
        "the `ports/` directory lives. The same commands work from the repository root.",
        "",
        "Install the face separately using the [typography guide](typography.md).",
        "Fonts are not included in the ports. Maesglas is independent of every",
        "tool listed below.",
        "",
    ]
    for port in PORTS:
        lines.extend(port_installation(port))
    lines.extend(
        [
            "For cache setup, feature composition, validation methods, and limitations,",
            "read the [port notes](ports.md). Unverified formats are omitted.",
            "",
            "## Font setup",
            "",
            *typography(d)
            .split("## Install the face\n\n", 1)[1]
            .split("## Size the pane, not the display", 1)[0]
            .strip()
            .splitlines(),
            "",
            "Continue with [font settings and pane arithmetic](typography.md).",
        ]
    )
    return "\n".join(lines) + "\n"


def palette_report(d: Design) -> str:
    lines = [
        "# Palette and contrast",
        "",
        "The source is `identity/maesglas.json`. Values below are the delivered",
        "8-bit sRGB colors, not unrounded coordinates or sampled antialiasing.",
        "",
        "Every text role and every ANSI foreground is tested on every content ground.",
        "The threshold is 4.5:1 without rounding. Boundaries require 3:1.",
        "The bright bank repeats its corresponding accent; weight does not change hue.",
        "",
        "APCA uses SAPC 0.0.98G-4g. Positive Lc is dark text on a light ground.",
        "Default prose requires absolute Lc 90 on canvas; comments and line numbers",
        "require 75. All three require 60 on emphasis grounds. These are project",
        "targets, not a font certification or a claim of WCAG 3 conformance.",
        "",
        "The macOS reference plate uses 15 CSS px regular type: the settled 15 pt",
        "face has 9-point cells and an 8.1-point x-height, matching 9 CSS px cells",
        "and an 8.1 CSS px x-height on the Mac. Editor guidance uses 16 px regular.",
        "Captions use 16 px regular,",
        "and headings use the real 700 face. The same contrast thresholds hold at",
        "each size. Text remains opaque.",
        "",
        "## Delivered colors",
        "",
        "| Primitive | Chalk | Shale |",
        "| --- | --- | --- |",
    ]
    for key in d.coordinates["chalk"]:
        lines.append(f"| {key} | `{d.colors['chalk'][key]}` | `{d.colors['shale'][key]}` |")
    lines.extend(["", "## ANSI assignments", "", "| Slot | Role |", "| --- | --- |"])
    lines.extend(f"| {i} | {role} |" for i, role in enumerate(d.ansi))
    lines.extend(
        [
            "",
            "All sixteen slots are text colors, including slot 0. A tool that",
            "hard-codes a background from these slots needs a dedicated port. Arbitrary",
            "foreground/background permutations, faded SGR text, and the fixed",
            "256-color cube are not authored combinations.",
            "",
        ]
    )
    for mode, p in d.colors.items():
        lines.extend(
            [
                "",
                f"## {mode.title()} reading pairs",
                "",
                "| Text | Ground | WCAG 2 | APCA Lc |",
                "| --- | --- | ---: | ---: |",
            ]
        )
        texts = dict(d.roles)
        texts.update({f"ANSI {index}": role for index, role in enumerate(d.ansi)})
        for name, role in texts.items():
            for ground in d.grounds:
                lines.append(
                    f"| {name} | {ground} | {wcag(p[role], p[ground]):.3f} "
                    f"| {apca(p[role], p[ground]):+.2f} |"
                )
        lines.extend(
            [
                "",
                f"## {mode.title()} essential boundaries",
                "",
                "| Role | Ground | WCAG 2 |",
                "| --- | --- | ---: |",
            ]
        )
        for role in ("boundary", "type"):
            for ground in d.grounds:
                lines.append(f"| {role} | {ground} | {wcag(p[role], p[ground]):.3f} |")
    lines.extend(
        [
            "",
            "## Color-vision separation",
            "",
            "Machado severity 1.0 matrices act on linear sRGB; simulated channels are",
            "clamped to the display gamut before conversion to OKLab. Each pair must",
            "remain at least 5 units apart in Euclidean OKLab distance multiplied by",
            "100. Status words, diff signs, and syntax remain present without color.",
            "",
            "| Variant | Pair | Protanopia | Deuteranopia | Tritanopia |",
            "| --- | --- | ---: | ---: | ---: |",
        ]
    )
    for mode, p in d.colors.items():
        for a, b in SYNTAX_PAIRS:
            figures = " | ".join(f"{simulated_distance(p[a], p[b], c):.3f}" for c in MACHADO)
            lines.append(f"| {mode.title()} | {a} / {b} | {figures} |")
    return "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"


def readme(d: Design) -> str:
    p = d.colors["chalk"]
    minimum = min(wcag(p[r], p[g]) for r in d.ansi for g in d.grounds)
    lines = [
        "# Maesglas",
        "",
        "A terminal in mineral and ink. Chalk is the light default: cool paper,",
        "green-black text, and a few dark pigments that separate structure from",
        "state. Shale carries the same relationships onto a dark ground.",
        "",
        "*Maesglas* joins the Welsh words *maes*, a field, and *glas*, a color",
        "word spanning blue, green, and gray.",
        "",
        "![Maesglas in Chalk and Shale](identity/banner.svg)",
        "",
        "## The palette",
        "",
        "| Ink | Slate | Petroleum | Mulberry | Juniper | Bronze | Oxide |",
        "| --- | --- | --- | --- | --- | --- | --- |",
        "| "
        + " | ".join(
            f"`{p[k]}`"
            for k in ("ink", "slate", "petroleum", "mulberry", "juniper", "bronze", "oxide")
        )
        + " |",
        "",
        f"The weakest Chalk text pair is {minimum:.3f}:1. Every ANSI slot is",
        "readable text, including black and white. Both variants are checked on",
        "selection, search, and diff grounds as well as the canvas.",
        "[Full contrast report](docs/palette.md).",
        "",
        "![A small diff in Chalk](specimens/chalk/diff.svg)",
        "",
        "The [specimen page](site/index.html) includes prompts, code, a directory",
        "listing, an editor, and a review. These are synthetic drawings, not",
        "application screenshots. [Design rationale](docs/design.md).",
        "",
        "## Install",
        "",
        installation(d)
        .removeprefix("# Installation\n\n")
        .replace("(typography.md)", "(docs/typography.md)")
        .replace("(ports.md)", "(docs/ports.md)")
        .replace("(../THIRD_PARTY_NOTICES.md)", "(THIRD_PARTY_NOTICES.md)"),
    ]
    lines.extend(
        [
            "For cache setup, feature composition, and the validation boundary, read",
            "[port notes](docs/ports.md). Unverified formats are omitted, not presented",
            "as previews.",
            "",
            "## Build",
            "",
            "```sh",
            "python3 scripts/generate.py",
            "scripts/gate.sh",
            "```",
            "",
            "Generation has no package dependencies and makes no network requests.",
            "The gate uses the versions in `tools.lock`; see",
            "[contributing](CONTRIBUTING.md) for setup.",
            "",
            "[MIT license](LICENSE). Version `2026.10.0`.",
            "[Specimen site](https://agh.github.io/maesglas/) and "
            "[release preparation](docs/publishing.md).",
        ]
    )
    return "\n".join(lines) + "\n"


def typography(d: Design) -> str:
    size = number(d.leaf("fonts", "terminal"))
    advance = number(d.leaf("fonts", "advance"))
    lines = [
        "# Typography",
        "",
        "Commit Mono supplies the lettering. Its 600-unit advance on a 1000-unit",
        "em gives a predictable cell width; the regular and bold files are real",
        "400 and 700 outlines. [checked: Commit Mono 1.143, 2026-10-24]",
        "",
        "Use upright regular text for comments, paths, and branch names. Reserve",
        "bold for focus, headings, and urgent state. Programming ligatures are off",
        "so the characters you read are the characters you copy.",
        "",
        "## Install the face",
        "",
        f"Download the [1.143 archive]({text(d.leaf('fonts', 'archive'))}),",
        "verify its SHA-256 below, and install its regular, italic, bold, and",
        "bold italic files with your operating system's font installer.",
        "The family name in the files is `CommitMono`.",
        "[checked: Commit Mono 1.143, 2026-10-24]",
        "",
        "```text",
        text(d.leaf("fonts", "archive-sha256")),
        "```",
        "",
        "The page uses only upright regular and bold. Its local copies and the",
        "shaped outline cache are covered by [the font notice](../THIRD_PARTY_NOTICES.md).",
        "Font installation is a separate, explicit step.",
        "",
        "## Size the pane, not the display",
        "",
        f"The default is {size:g} pt with 12 pt horizontal padding on each side of",
        "each pane. Fit the content in logical display points, not physical pixels:",
        "",
        "```text",
        "panes * (columns * size * advance + 2 * padding) <= display width",
        f"2 * (80 * {size:g} * {advance:g} + 2 * 12) = 1488 pt",
        "```",
        "",
        "| Display width in points | Two 80-column panes | Recommendation |",
        "| ---: | ---: | --- |",
    ]
    for width in (1280, 1440, 1512, 1728, 1920):
        maximum = (width / 2 - 24) / (80 * advance)
        advice = (
            "Use one pane at 15 pt" if maximum < size else "15 pt; zoom for single-pane reading"
        )
        lines.append(f"| {width} | Up to {maximum:.2f} pt | {advice} |")
    lines.extend(
        [
            "",
            "Two panes at 18 pt need 1776 pt. Shrinking below the default to fit",
            "another pane is not the recommended layout.",
            "",
            "## Checked terminal settings",
            "",
            "The Ghostty port sets 15 pt, 12 pt padding, 6% extra cell height,",
            "no synthetic styles, and contextual spacing with `calt=1`.",
            "The `ss01=0`, `ss02=0`, `liga=0`, and `dlig=0` settings preserve",
            "the default letterforms without programming ligatures.",
            "It binds `Super+Shift+Enter` to split zoom. This enlarges the active pane,",
            "not the font. On macOS, the text-size defaults are `Command+=` or",
            "`Command++` to increase, `Command+-` to decrease, and `Command+0`",
            "to reset the active surface. Enlarge the reading pane, then reset",
            "its text size before returning to two panes.",
            f"{stamp('ghostty')}",
            "",
            "The terminal supplies the face to nano, Vim, and the command-line ports.",
            "They do not install or choose a second face.",
            "[checked: nano 9.2 and Vim 9.1, 2026-10-24]",
            "",
            "## Unverified application settings",
            "",
            "These font settings are starting points, separate from the validated",
            "color ports. Each needs a native font and layout check before adoption.",
            "",
            "| Application | Intended setting | Status |",
            "| --- | --- | --- |",
            "| iTerm2 | Text: CommitMono Regular 15; disable ligatures | [unchecked] |",
            "| Terminal.app | Profile font: CommitMono Regular 15 | [unchecked] |",
            '| Alacritty | `font.normal.family = "CommitMono"`; `font.size = 15` | [unchecked] |',
            "| kitty | `font_family CommitMono`; `font_size 15`; "
            "`disable_ligatures always` | [unchecked] |",
            '| WezTerm | `font = wezterm.font("CommitMono")`; `font_size = 15` | [unchecked] |',
            '| Windows Terminal | `font.face: "CommitMono"`; `font.size: 15` | [unchecked] |',
            '| VS Code | `editor.fontFamily: "CommitMono"`; size 16; '
            "line height 26; ligatures off | [unchecked] |",
            '| Zed | `buffer_font_family: "CommitMono"`; size 16; ligatures off | [unchecked] |',
            "| Helix and Neovim | Use the terminal's face and cell geometry | [unchecked] |",
            "",
            "## Measured macOS reference",
            "",
            "CoreText measures the settled 15 pt face as 9-point cells with an",
            "8.1-point x-height. The reference specimen therefore uses 15 CSS px:",
            "9 CSS px cells and an 8.1 CSS px x-height on the Mac, where logical",
            "points and CSS px agree. A 20 CSS px drawing would have 12 CSS px",
            "cells, one-third larger; it is not the macOS terminal reference.",
            "[checked: Commit Mono 1.143, CoreText on macOS, 2026-10-24]",
            "",
            "Browser CSS points use a different unit conversion. Other applications",
            "and platforms require their own measurement; there is no universal",
            "integrated-terminal pixel target. Verify `0O`, `1lI`, quotes, braces,",
            "and arrow punctuation with the delivered font.",
            "",
            "The site, native font-feature settings, and shaped outlines use",
            "`calt=1`, `ss01=0`, `ss02=0`, `liga=0`, and `dlig=0`.",
            "The outline extractor shapes complete lines before applying syntax",
            "colors, so contextual spacing also crosses color boundaries.",
            "Every shaped glyph retains its 600-unit advance and every character",
            "retains its own glyph; no programming ligatures are introduced.",
            "[checked: Commit Mono 1.143 and uharfbuzz 0.57.0, 2026-10-24]",
        ]
    )
    return "\n".join(lines) + "\n"


def port_notes(d: Design) -> str:
    lines = [
        "# Port notes",
        "",
        "Every shipped port is generated. The gate runs native parsers,",
        "renderers, published schemas, or documented key checks in disposable",
        "configuration and cache directories. The method column is the boundary:",
        "a schema check does not establish application import or rendering.",
        "",
        "## Tested scope",
        "",
        "| Port | Validation method | Version and date |",
        "| --- | --- | --- |",
    ]
    methods = {
        "ghostty": "`+validate-config` on both complete files; macOS only",
        "starship": "`print-config` and prompt rendering in a synthetic repository",
        "vim": "Headless load and highlight query",
        "textmate": "Theme cache build, named-theme listing, and syntax rendering",
        "delta": "Named-feature diff rendering using the generated syntax theme",
        "git": "Parse every color with `config --get-color`",
        "nano": "PTY startup for all ten named syntaxes",
        "fzf": "Native picker startup with generated color options",
        "tmux": "Independent server, source file, and option queries",
        "eza": "Classified fixture listing with the generated theme",
        "glow": "Markdown and code rendering through the style loader",
        "lazygit": "PTY startup in a disposable repository",
        "yazi": "PTY startup with isolated configuration",
    } | extra_ports.METHODS
    for port, (name, _, _) in PORTS.items():
        lines.append(f"| {name} | {methods[port]} | {stamp(port)} |")
    lines.extend(
        [
            "",
            "## Additional port installation",
            "",
            "Choose the application-specific destination as `THEME_DIR`. Each example",
            "has one preparation line and one copy line. Substitute `shale` for",
            "`chalk`, except that the editor extension includes both variants.",
            "",
        ]
    )
    for port, (name, _, note) in extra_ports.PORTS.items():
        lines.extend(
            [
                "<details>",
                f"<summary>{name}</summary>",
                "",
                f"{note} {stamp(port)}",
                "",
                "```sh",
                *install_lines(port),
                "```",
                "",
                "</details>",
                "",
            ]
        )
    lines.extend(
        [
            "",
            "## Cache and feature composition",
            "",
            "Place the TextMate files in the `themes` directory below `BAT_CONFIG_DIR`.",
            "Run `bat cache --build`, then select `maesglas-chalk` or `maesglas-shale`",
            "through `BAT_THEME`. A rebuilt cache is required after a palette change.",
            f"{stamp('textmate')}",
            "",
            "Use the same XDG cache root for both tools. Delta reads",
            "`XDG_CACHE_HOME/bat`, not a custom `BAT_CACHE_PATH`. Build the cache",
            f"there when composing the tools. {stamp('textmate')}",
            "",
            "Include the delta file from your Git configuration. Add `maesglas-chalk`",
            "to the existing feature list rather than replacing it. Keep behavior",
            f"features separate from color features. {stamp('delta')}",
            "",
            "```gitconfig",
            "[delta]",
            "    features = review maesglas-chalk",
            '[delta "review"]',
            "    side-by-side = true",
            '[delta "interactive"]',
            "    features = maesglas-chalk",
            "    color-only = true",
            "    side-by-side = false",
            "    line-numbers = false",
            "```",
            "",
            "Interactive patch output must retain its patch structure. The palette",
            "does not install a pager, rewrite `interactive.diffFilter`, or turn on",
            f"side-by-side output by itself. {stamp('delta')}",
            "",
            "The nano port uses terminal slots and default backgrounds. The selected",
            "range is bold rather than inverted onto an ink-colored ANSI background.",
            "Search uses bold bronze. All ten syntaxes are small regular-expression",
            f"rules, not language parsers. {stamp('nano')}",
            "",
            "The fzf fragment leaves color alone under `NO_COLOR`, `TERM=dumb`, or",
            "redirected output. Source it in the interactive shell after other options.",
            f"{stamp('fzf')}",
            "",
            "The glow port renders code blocks in plain ink. Its embedded syntax",
            "formatter reduces colors to the fixed 256-color cube, and the CLI",
            "does not expose the formatter override. Plain code avoids a second,",
            f"uncontrolled palette. {stamp('glow')}",
            "",
            "The Yazi file clears the default colored icon tables. File kinds use",
            "letters, paths, and permission text instead of private-use glyphs.",
            "Its flavor includes the matching syntax theme. Copy the complete",
            f"flavor directory, not just the selection file. {stamp('yazi')}",
            "",
            "## Rulings and limitations",
            "",
            "LEG-01: the editor extension emits `editor.findMatchForeground` and",
            "`editor.findMatchHighlightForeground` as ink. Its `match` and",
            "`match-active` grounds are lighter than the original search grounds.",
            "The gate audits every emitted syntax foreground on both actual match",
            f"fills, not only the replacement ink. {stamp('vscode')}",
            "",
            "FG-CLAUDE-LIGHTBASE was evaluated against all six installed base",
            f"registries and all {len(extra_ports.CLAUDE_ROLES)} accepted color tokens.",
            "A fully overridden candidate fixes every configurable foreground,",
            "including the misleadingly named `background` accent and the two",
            "word-diff tokens used for `+N` and `-N` counters. The same word tokens",
            "also paint inline backgrounds; inline word text inherits the normal",
            "text role, with no independent foreground override. Making the counters",
            "readable therefore makes word-diff text unreadable, so this format is omitted.",
            f"{stamp('claude-code')}",
            "",
            "Claude Code compatibility is a factual product statement, not an",
            "endorsement: Maesglas is independent of Anthropic. The format also",
            "cannot replace `dimColor` or `faint` attributes, literal syntax-formatter",
            "colors, or external-tool output. The check inspected the installed",
            "renderer without starting an authenticated session.",
            f"{stamp('claude-code')}",
            "",
            "| Shared-token bound | Chalk | Shale |",
            "| --- | ---: | ---: |",
            "| Best possible simultaneous counter/word contrast | "
            + " | ".join(
                f"{math.sqrt(wcag(p['ink'], p['canvas'])):.3f}:1" for p in d.colors.values()
            )
            + " |",
            "",
            "The bound is the square root of ink/canvas contrast: a shared color",
            "must contrast with the canvas as foreground and with ink as background.",
            "Both maxima are below 4.5:1. The gate reproduces this blocker instead",
            "of exempting either failing pair. Its inputs and measured candidate",
            "pairs are in `identity/port-validation.json`.",
            f"{stamp('claude-code')}",
            "",
            "FG-K9S-TRUECOLOR: every native skin color, including chart arrays,",
            "resource maps, help, prompt borders, and logo messages, is palette hex.",
            "The parsed skin retains these hex values throughout. The YAML files",
            f"use JSON syntax, a YAML-compatible representation. {stamp('k9s')}",
            "",
            "FG-GHDASH-KEYS uses the actual 4.26 parser fields: `text.actor`,",
            "`background.selected`, the three border fields, and the six author",
            "association icon fields. FG-GHDASH-INVERTED assigns ink to `inverted`;",
            "COV-05 assigns the warning slot to `warning`, not the number or error",
            "slot. Both parsed values and initialized theme colors are queried.",
            f"{stamp('gh-dash')}",
            "",
            "FG-GHDASH-ICONS: issue and pull-request state icons, the merged glyph,",
            "the logo, and API-supplied label colors are not configurable through",
            "the theme. The parser accepts `icon.unknownrole`, but theme initialization",
            "leaves that color at fixed index 178. These upstream colors are not",
            "Maesglas colors, and several fail 4.5:1. The port does not make the",
            f"entire application contrast-compliant. {stamp('gh-dash')}",
            "",
            "COV-01: the shell theme replaces the complete style registry after",
            "the plugin loads. Primary, default, and recursive namespaces use",
            "semantic ANSI foregrounds; there are no fixed xterm-256 indices,",
            "ANSI-background inversions, or unthemed secondary themes. Use the",
            f"matching terminal variant. {stamp('fast-syntax-highlighting')}",
            "",
            "## Omitted formats",
            "",
            "Omitted formats have no shipped draft files and make no compatibility claims.",
            "",
            "| Format | Reason |",
            "| --- | --- |",
        ]
    )
    for name, reason in DROPPED.items():
        marker = "[unchecked]"
        if name == "btop":
            record = mapping(load_json(ROOT / "identity/rejections.json")["btop"])
            marker = f"[checked: btop {text(record['version'])}, {text(record['date'])}]"
            color = text(record["foreground"])
            light = wcag(color, d.colors["chalk"]["canvas"])
            dark = wcag(color, d.colors["shale"]["canvas"])
            reason += (
                f" Observed `{color}` reaches {light:.3f}:1 on Chalk and {dark:.3f}:1 "
                "on Shale. The input and source are in `identity/rejections.json`."
            )
        elif name == "Claude Code":
            marker = stamp("claude-code")
            reason += (
                " The installed-registry digest and proof are in `identity/port-validation.json`."
            )
        lines.append(f"| {name} | {reason} {marker} |")
    return "\n".join(lines).replace("\n\n\n", "\n\n") + "\n"


def appearance(d: Design) -> str:
    blocks: list[str] = []
    family = text(d.leaf("fonts", "family"))
    for role, weight in (("regular", 400), ("bold", 700)):
        path = text(d.leaf("fonts", role)).removeprefix("site/")
        blocks.append(
            "@font-face {\n"
            f"  font-family: {family};\n"
            f'  src: url("{path}") format("opentype");\n'
            "  font-style: normal;\n"
            f"  font-weight: {weight};\n"
            "  font-display: swap;\n}"
        )
    for mode, p in d.colors.items():
        selector = ":root" if mode == "chalk" else ':root[data-theme="shale"]'
        fields = [f"  --{key}: {value.lower()};" for key, value in p.items()]
        fields.append(f"\n  color-scheme: {'light' if mode == 'chalk' else 'dark'};")
        blocks.append(selector + " {\n" + "\n".join(fields) + "\n}")
    spacing = [number(v) for v in sequence(d.leaf("spacing"))]
    fields = [f"  --space-{i}: {v / 16:g}rem;" for i, v in enumerate(spacing)]
    ratio = number(d.leaf("scale", "ratio"))
    fields.extend(f"  --size-{i}: {round(ratio**i, 4):g}rem;" for i in range(8))
    fields.extend(
        [
            f"  --measure: {number(d.leaf('measure')):g}ch;",
            f"  --radius: {number(d.leaf('radius')):g}px;",
            f'  --font-mono: "{family}", ui-monospace, monospace;',
            f"  --page-width: {number(d.leaf('components', 'page-width')):g}px;",
            f"  --plate-width: {number(d.leaf('components', 'plate-width')):g}px;",
        ]
    )
    features = mapping(d.leaf("fonts", "features"))
    fields.append(
        "  --font-features: "
        + ", ".join(f'"{key}" {int(number(value))}' for key, value in features.items())
        + ";"
    )
    blocks[2] = blocks[2].replace(
        "\n\n  color-scheme:", "\n" + "\n".join(fields) + "\n\n  color-scheme:"
    )
    return "\n\n".join(blocks) + "\n"


def page(d: Design) -> str:
    swatches = "\n".join(
        f'<li class="swatch-{role}"><span class="swatch" aria-hidden="true"></span>'
        f'<span>{label}</span><code data-color="{role}">{d.colors["chalk"][role]}</code></li>'
        for role, label in (
            ("ink", "Reading"),
            ("slate", "Paths / functions"),
            ("petroleum", "Links / types"),
            ("mulberry", "Branches / keywords"),
            ("juniper", "Added / strings"),
            ("bronze", "Warning / numbers"),
            ("oxide", "Error / removed"),
        )
    )
    options = "\n".join(
        f'<option value="{key}"{" selected" if key == "code" else ""}>{html.escape(title)}</option>'
        for key, (title, _) in SCENES.items()
    )
    ports = ", ".join(html.escape(name) for name, _, _ in PORTS.values())
    targets = {
        "typography.md": "#type",
        "ports.md": "#port-notes",
        "../THIRD_PARTY_NOTICES.md": "#font-notice",
        "site/fonts/OFL.txt": "fonts/OFL.txt",
    }
    setup = guidance.render(installation(d), "install", targets)
    typography_html = guidance.render(typography(d), "type", targets)
    palette_html = guidance.render(palette_report(d), "contrast", targets)
    notes = guidance.render(port_notes(d), "port-notes", targets)
    notice = (ROOT / "THIRD_PARTY_NOTICES.md").read_text().split("## Color calculations", 1)[0]
    notice_html = guidance.render(notice, "font-notice", targets)
    privacy_html = guidance.render(privacy(), "privacy", {})
    width, height = dimensions(d, "code")
    return f"""<!doctype html>
<html lang="en" data-theme="chalk">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="Maesglas, a terminal design system in mineral and ink.">
    <title>Maesglas</title>
    <script src="choice.js"></script>
    <link rel="icon" href="mark-16.svg" type="image/svg+xml">
    <link rel="stylesheet" href="appearance.css">
    <link rel="stylesheet" href="layout.css">
    <script src="app.js" defer></script>
  </head>
  <body>
    <a class="skip" href="#main">Skip to content</a>
    <header class="masthead">
      <a href="#main" class="home" aria-label="Maesglas home">
        {mark().decode()}
        <span>Maesglas</span>
      </a>
      <nav aria-label="Main navigation">
        <a href="#palette">Palette</a>
        <a href="#type">Type</a>
        <a href="#install">Install</a>
        <button type="button" id="theme">Use Shale</button>
      </nav>
    </header>
    <main id="main" tabindex="-1">
      <section class="opening" aria-labelledby="title">
        <h1 id="title">Maesglas</h1>
        <p class="intro">A terminal in mineral and ink.</p>
        <p>Chalk is light. Shale is dark. Both keep color readable.</p>
      </section>
      <section class="plates" aria-labelledby="specimen-title">
        <div class="plate-controls">
          <h2 id="specimen-title">At the terminal</h2>
          <label for="scene">View
            <select id="scene">{options}</select>
          </label>
        </div>
        <figure>
          <div class="plate-scroll" tabindex="0" role="region"
            aria-label="Scrollable terminal specimen">
            <img id="plate" src="specimens/chalk/code.svg" width="{width}" height="{height}"
              alt="Synthetic code: upright comments, colored syntax, and literal punctuation.">
          </div>
          <figcaption>Drawn from the palette, not captured from an application.
            macOS reference: 15 CSS px, 9 CSS px cells, and an 8.1 CSS px x-height.
            <a href="#type-measured-macos-reference">How the size was measured</a>.</figcaption>
        </figure>
        <details class="transcript">
          <summary>Read the specimen as plain text</summary>
          <pre id="plain">{html.escape(plain("code"))}</pre>
        </details>
      </section>
      <section id="palette" aria-labelledby="palette-title">
        <div class="section-heading">
          <h2 id="palette-title">Palette</h2>
          <p>Meaning stays in the words. Color separates the parts.</p>
        </div>
        <ul class="palette">{swatches}</ul>
        <p>Chalk has a slight green cast. Its dark ink holds a long paragraph.
          Bronze means attention; oxide means an error.
          A branch keeps its mulberry identity wherever it appears.</p>
        <p>Every text role and all sixteen ANSI slots clear 4.5:1 on every
          authored content ground in both variants. Comments are opaque ink,
          not text made faint. <a href="#contrast">Read the measured pairs</a>.</p>
      </section>
      <section id="type" class="type-section" aria-labelledby="type-title">
        <div class="section-heading">
          <h2 id="type-title">Typography</h2>
          <p>Upright text keeps punctuation distinct.</p>
        </div>
        <div class="type-sample" aria-label="Character distinction specimen">
          <p>0O 1lI</p>
          <p class="punctuation">{{ }} [ ] ( ) != &lt;= -&gt;</p>
        </div>
        {typography_html}
        <p><a href="typography.md" download>Download the typography source</a>.</p>
      </section>
      <section id="install" aria-labelledby="install-title">
        <h2 id="install-title">Install</h2>
        <p><a class="download" href="maesglas.zip" download>Download the ports</a>
          <a href="#port-notes">Validation and limitations</a></p>
        {setup}
        <p><a href="installation.md" download>Download the installation source</a>.</p>
        <details>
          <summary>Included ports</summary>
          <p>{ports}. See the installation notes for dated validation methods
            and limitations. [checked: port set 2026.10.0, 2026-10-24]</p>
        </details>
      </section>
      <section id="port-notes" class="guidance" aria-labelledby="port-notes-title">
        <h2 id="port-notes-title">Port reference</h2>
        <details>
          <summary>Validation, cache setup, and limitations</summary>
          {notes}
        </details>
        <p><a href="ports.md" download>Download the port-notes source</a>.</p>
      </section>
      <section id="contrast" class="guidance" aria-labelledby="contrast-title">
        <h2 id="contrast-title">Measured contrast</h2>
        <details>
          <summary>Reading pairs and color-vision separation</summary>
          {palette_html}
        </details>
        <p><a href="palette.md" download>Download the contrast source</a>.</p>
      </section>
      <section id="font-notice" class="guidance" aria-labelledby="font-notice-title">
        <h2 id="font-notice-title">Font rights and source</h2>
        {notice_html}
        <p><a href="THIRD_PARTY_NOTICES.md" download>Download the complete notices</a>.</p>
      </section>
    </main>
    <footer>
      <p>Maesglas joins <span lang="cy">maes</span>, a field, and
        <span lang="cy">glas</span>, a word for blue, green, and gray.</p>
      <section id="privacy" aria-labelledby="privacy-title">
        <h2 id="privacy-title">Privacy</h2>
        {privacy_html}
      </section>
      <p id="storage-notice" role="status" hidden></p>
      <button type="button" id="help">Help</button>
      <p>2026.10.0 / <a href="LICENSE.txt">MIT</a></p>
    </footer>
    <dialog id="shortcuts" aria-labelledby="help-title">
      <h2 id="help-title">Keyboard shortcuts</h2>
      <dl id="shortcut-list"></dl>
      <label class="shortcut-setting">
        <input type="checkbox" id="shortcuts-enabled" checked>
        Enable single-key shortcuts
      </label>
      <p>Shortcuts pause while typing, using modifiers, or holding a key.</p>
      <button type="button" id="close-help" autofocus>Close help</button>
    </dialog>
  </body>
</html>
"""


def render(d: Design) -> dict[str, bytes]:
    palette = palette_report(d)
    type_guide = typography(d)
    notes = port_notes(d)
    setup = installation(d)
    scenes = {
        key: {
            "title": title,
            "plain": plain(key),
            "width": dimensions(d, key)[0],
            "height": dimensions(d, key)[1],
        }
        for key, (title, _) in SCENES.items()
    }
    outputs = {
        "README.md": readme(d),
        "docs/palette.md": palette,
        "docs/typography.md": type_guide,
        "docs/ports.md": notes,
        "docs/installation.md": setup,
        "docs/privacy.md": privacy(),
        "site/privacy.md": privacy(),
        "site/.nojekyll": "",
        "site/installation.md": setup.replace(
            "../THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md"
        ),
        "site/palette.md": palette,
        "site/typography.md": type_guide.replace(
            "../THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md"
        ),
        "site/ports.md": notes,
        "site/appearance.css": appearance(d),
        "site/index.html": page(d),
        "site/data.json": json.dumps(
            {
                "colors": d.colors,
                "scenes": scenes,
                "fontArchive": {
                    "url": d.leaf("fonts", "archive"),
                    "sha256": d.leaf("fonts", "archive-sha256"),
                },
            },
            indent=2,
        )
        + "\n",
    }
    outputs["docs/verification.md"] = verification()
    return {path: value.encode() for path, value in outputs.items()}


def privacy() -> str:
    return "\n".join(
        [
            "# Privacy",
            "",
            "This site sets no cookies, uses no analytics, and makes no third-party",
            "requests. Theme and shortcut preferences stay in this browser.",
            "",
            "GitHub Pages hosts this site. GitHub logs and stores visitors' IP addresses",
            "for security, whether or not they are signed in. "
            "[GitHub's data-collection notice]"
            "(https://docs.github.com/en/pages/getting-started-with-github-pages/"
            "what-is-github-pages#data-collection).",
            "[checked: GitHub Docs, About GitHub Pages, Data collection, 2026-10-24]",
            "",
        ]
    )


def verification() -> str:
    records = load_json(ROOT / "identity/validation.json")
    lines = [
        "# Verification",
        "",
        "Native results are recorded with their input digests in",
        "`identity/validation.json`. The gate rejects a changed input, tool pin,",
        "or validator until the corresponding platform is checked again.",
        "",
        "| Platform | Date | Port and variant cases |",
        "| --- | --- | ---: |",
    ]
    for platform, value in records.items():
        record = mapping(value)
        lines.append(f"| {platform} | {text(record['date'])} | {len(mapping(record['checks']))} |")
    lines.extend(
        [
            "",
            "Additional native and schema evidence is recorded separately in",
            "`identity/port-validation.json`; the original cross-platform native",
            "record remains intact. Both records are required by the gate.",
            "",
            "| Additional checks | Date | Port and variant cases |",
            "| --- | --- | ---: |",
        ]
    )
    additional = load_json(ROOT / "identity/port-validation.json")
    for platform, value in additional.items():
        record = mapping(value)
        lines.append(f"| {platform} | {text(record['date'])} | {len(mapping(record['checks']))} |")
    lines.extend(
        [
            "",
            "```sh",
            "python3 scripts/bootstrap_ports.py",
            "python3 scripts/validate_ports.py --record",
            "python3 scripts/validate_extended.py --record",
            "python3 scripts/generate.py",
            "scripts/gate.sh",
            "```",
            "",
            "The original record covers native loading and exact emitted colors on",
            "the exercised paths. Editor syntax checks cover all ten declared syntaxes.",
            "The file-manager check",
            "answers the terminal's background-color query from the selected palette.",
            "",
            "## Additional validation boundary",
            "",
            "Each download's URL, version, and SHA-256 is in `tools.lock`.",
            "The bootstrap verifies every cached source before extraction and builds",
            "the two Go probes against upstream parsers and their locked modules.",
            "Go caches, application state, temporary files, and browser captures",
            "stay below `.cache/`. No application window is opened or theme installed.",
            "",
            "Alacritty uses its migration command's native TOML parser, not a window.",
            "kitty queries every configured color through its embedded Python loader.",
            "WezTerm loads the TOML scheme with `color.load_scheme` and asserts every",
            "color before `show-keys`. Neovim loads both Lua colorschemes headlessly",
            "and queries all authored highlights and terminal slots; any inherited",
            "highlight color outside the palette fails. Helix loads",
            "each theme in a PTY and checks published keys. These six macOS-specific",
            "checks, including the profile lint, are bound to the Darwin record;",
            "Linux reruns portable checks and verifies that record, not foreign binaries.",
            "[checked: Alacritty 0.17.0, kitty 0.49.2, WezTerm 20240203-110809-5046fc22, "
            "Neovim 0.12.6, Helix 25.07.1, and iTerm2 key set 3.6.6, 2026-10-24]",
            "",
            "VS Code has no supported standalone GUI-theme importer for this check.",
            "The validator evaluates its published TypeScript color-theme and semantic",
            "token schemas with localization stubbed, then checks the official source",
            "color registry. Zed uses its published theme schema; unknown properties",
            "also fail. Windows Terminal uses the scheme definition from Microsoft's",
            "settings schema. iTerm2 uses `plutil -lint`, upstream preset keys, and",
            "exact sRGB round-trips. These are format checks, not profile import or",
            "application rendering evidence.",
            "[checked: VS Code 1.143.1, Zed schema 0.2.0, Windows Terminal 1.25.2733.0, "
            "and iTerm2 key set 3.6.6, 2026-10-24]",
            "",
            "Claude Code exposes no standalone custom-theme validator. Its documented",
            "format and all six installed registries were checked; all 72 tokens",
            "were overridden in an in-memory candidate. The installed binary digest",
            "and shared-token rejection are recorded without a personal path.",
            "`diffAddedWord` and `diffRemovedWord` serve both counter foregrounds",
            "and inline backgrounds, but the format has no separate word-text color.",
            "The maximum simultaneous contrast is 3.845:1 in Chalk and 4.100:1 in",
            "Shale. Both fail 4.5:1; no candidate file is shipped or exempted.",
            "The original live documentation URL and digest remain historical",
            "references in `tools.lock`; its mutable page is not a CI dependency.",
            "The rejection gate uses the exact installed registry or its recorded",
            "keys and the measured shared-token proof, not a fresh documentation fetch.",
            "No authenticated session, transcript, external syntax formatter, or",
            "dimmed rendering path is certified.",
            f"{stamp('claude-code')}",
            "",
            "The k9s probe calls `NewStyles().Load`, including its embedded schema,",
            "and compares every parsed skin field. The gh-dash probe calls",
            "`ParseConfig` and `ParseTheme`, compares every accepted theme key, and",
            "queries light and dark adaptive values. Neither check contacts a cluster",
            "or account. Fixed status icons remain documented upstream limitations,",
            f"not contrast exemptions for authored colors. {stamp('k9s')} {stamp('gh-dash')}",
            "",
            "The shell check loads the pinned fast-syntax-highlighting plugin with",
            "a temporary `ZDOTDIR` and private working directory. It precreates the",
            "secondary-theme cache to prevent the plugin's automatic network fetch,",
            "loads each generated theme, exercises nested substitution and arithmetic,",
            "and rejects fixed indexed colors in all style namespaces and regions.",
            f"{stamp('fast-syntax-highlighting')}",
            "",
            "Application windows, plug-ins, monitor calibration, and assistive",
            "technology are not certified by these checks. The specimens are drawings,",
            "not evidence of a complete application session.",
            "",
            "Browser checks cover saved choice, system preference, keyboard help,",
            "shortcut opt-out, typing guards, focus return, storage failure, local",
            "requests, and all fourteen plates at their full dimensions. Both variants",
            "are exercised at 390x844 and 1512x982 in Chromium. The phone opening",
            "must show specimen glyphs before the fold; the laptop opening must show",
            "the whole specimen. Measured positions and screenshots stay in",
            "`.cache/visual`. Guidance links retain theme, Markdown links are explicit",
            "downloads, and clicking the font link downloads the digest-pinned archive.",
            "",
            "The macOS reference metrics were reproduced with",
            "`scripts/probes/font_metrics.swift`: CoreText reports 15 pt, 9-point",
            "cells, and an 8.1-point x-height. The outline check shapes full lines",
            "with the authored features, checks 600-unit advances and one glyph per",
            "character, and retains context across syntax colors.",
            "Browser canvas measurements allow less than 1/1024 CSS px of platform",
            "rounding around the 9 CSS px cell; outline advances remain exact.",
            "[checked: Commit Mono 1.143, CoreText on macOS, and uharfbuzz 0.57.0, 2026-10-24]",
        ]
    )
    return "\n".join(lines) + "\n"

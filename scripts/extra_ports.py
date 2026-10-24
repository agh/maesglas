"""Additional native and schema-checked appearance ports."""

import json
import plistlib

from model import ROOT, Design

type Palette = dict[str, str]

PORTS = {
    "alacritty": ("Alacritty", "toml", "Import the file from `[general].import`."),
    "kitty": ("kitty", "conf", "Include the file from your configuration."),
    "wezterm": ("WezTerm", "toml", "Put the file in `colors/`; select `Maesglas Chalk`."),
    "neovim": ("Neovim", "lua", "Put the file in `colors/`; run `:colorscheme maesglas-chalk`."),
    "helix": ("Helix", "toml", "Put the file in `themes/`; select `maesglas-chalk`."),
    "vscode": ("VS Code", "json", "Copy the extension folder, then select Maesglas Chalk."),
    "zed": ("Zed", "json", "Put the file in `themes/`, then select Maesglas Chalk."),
    "iterm2": ("iTerm2", "itermcolors", "Import the file through the profile's color presets."),
    "windows-terminal": (
        "Windows Terminal",
        "json",
        "Add the object to `schemes`; select `Maesglas Chalk`.",
    ),
    "k9s": ("k9s", "yaml", "Put the file in `skins/`; set `k9s.ui.skin: maesglas-chalk`."),
    "gh-dash": ("gh-dash", "yml", "Merge the `theme` mapping into your configuration."),
    "fast-syntax-highlighting": (
        "fast-syntax-highlighting",
        "zsh",
        "Source the file after loading the plugin.",
    ),
}

METHODS = {
    "alacritty": "Native `migrate --dry-run` TOML loader",
    "kitty": "Native `+runpy` and `kitty.config.load_config`; every color queried",
    "wezterm": "Native `show-keys` with `color.load_scheme` and exact Lua assertions",
    "neovim": "`--headless` colorscheme load; every authored highlight and ANSI slot queried",
    "helix": "Published theme keys and native PTY theme loading",
    "vscode": "Official color-theme schema evaluated from pinned source, plus color registry",
    "zed": "Published theme schema 0.2.0; unknown properties rejected",
    "iterm2": "`plutil -lint`, upstream preset keys, and exact sRGB round-trip",
    "windows-terminal": "Microsoft settings schema, with the scheme in `schemes`",
    "k9s": "Upstream `NewStyles().Load` parser and embedded schema; all colors queried",
    "gh-dash": "Upstream `ParseConfig` and theme initialization; all theme fields queried",
    "fast-syntax-highlighting": "Pinned plugin loaded in isolated Zsh; active and recursive styles",
}

SYNTAX = {
    "comment": "comment",
    "keyword": "keyword",
    "string": "string",
    "number": "number",
    "constant": "number",
    "function": "function",
    "type": "type",
    "variable": "ink",
    "operator": "ink",
    "punctuation": "ink",
    "attribute": "type",
    "tag": "type",
    "label": "type",
    "constructor": "type",
    "boolean": "number",
}

ANSI_NAMES = (
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
)


def encoded(value: object) -> str:
    return json.dumps(value, indent=2) + "\n"


def alacritty(p: Palette, ansi: list[str]) -> str:
    lines = [
        "[colors.primary]",
        f'background = "{p["canvas"]}"',
        f'foreground = "{p["ink"]}"',
        f'dim_foreground = "{p["ink"]}"',
        f'bright_foreground = "{p["ink"]}"',
        "",
        "[colors.cursor]",
        f'text = "{p["canvas"]}"',
        f'cursor = "{p["type"]}"',
        "",
        "[colors.selection]",
        f'text = "{p["ink"]}"',
        f'background = "{p["selection"]}"',
    ]
    for section, offset in (("normal", 0), ("bright", 8), ("dim", 0)):
        lines.extend(["", f"[colors.{section}]"])
        lines.extend(f'{name} = "{p[ansi[offset + i]]}"' for i, name in enumerate(ANSI_NAMES))
    for name, ground in (("matches", "match"), ("focused_match", "match-active")):
        lines.extend(
            [
                "",
                f"[colors.search.{name}]",
                f'foreground = "{p["ink"]}"',
                f'background = "{p[ground]}"',
            ]
        )
    return "\n".join(lines) + "\n"


def kitty(p: Palette, ansi: list[str]) -> str:
    roles = {
        "foreground": "ink",
        "background": "canvas",
        "cursor": "type",
        "cursor_text_color": "canvas",
        "selection_foreground": "ink",
        "selection_background": "selection",
        "url_color": "link",
        "active_border_color": "type",
        "inactive_border_color": "boundary",
        "bell_border_color": "warning",
        "active_tab_foreground": "ink",
        "active_tab_background": "selection",
        "inactive_tab_foreground": "comment",
        "inactive_tab_background": "surface",
        "tab_bar_background": "surface",
        "mark1_foreground": "ink",
        "mark1_background": "match",
        "mark2_foreground": "ink",
        "mark2_background": "match-active",
        "mark3_foreground": "ink",
        "mark3_background": "selection",
    }
    lines = [f"{key} {p[role]}" for key, role in roles.items()]
    lines.extend(f"color{i} {p[role]}" for i, role in enumerate(ansi))
    lines.extend(
        [
            "background_opacity 1.0",
            "inactive_text_alpha 1.0",
            "active_tab_font_style bold",
            "inactive_tab_font_style normal",
        ]
    )
    return "\n".join(lines) + "\n"


def wezterm(p: Palette, mode: str, ansi: list[str]) -> str:
    colors = {
        "foreground": "ink",
        "background": "canvas",
        "cursor_bg": "type",
        "cursor_fg": "canvas",
        "cursor_border": "type",
        "selection_fg": "ink",
        "selection_bg": "selection",
        "split": "boundary",
        "compose_cursor": "warning",
        "scrollbar_thumb": "boundary",
    }
    return "\n".join(
        [
            "[colors]",
            *(f'{key} = "{p[role]}"' for key, role in colors.items()),
            "ansi = " + json.dumps([p[role] for role in ansi[:8]]),
            "brights = " + json.dumps([p[role] for role in ansi[8:]]),
            "",
            "[metadata]",
            f'name = "Maesglas {mode.title()}"',
            "",
        ]
    )


def highlights() -> dict[str, tuple[str, str]]:
    groups = {
        "Normal": ("ink", "canvas"),
        "NormalNC": ("ink", "canvas"),
        "NormalFloat": ("ink", "surface"),
        "FloatBorder": ("boundary", "surface"),
        "LineNr": ("line-number", "canvas"),
        "CursorLineNr": ("ink", "surface"),
        "CursorLine": ("ink", "surface"),
        "CursorColumn": ("ink", "surface"),
        "ColorColumn": ("ink", "surface"),
        "SignColumn": ("ink", "canvas"),
        "FoldColumn": ("comment", "canvas"),
        "Folded": ("comment", "surface"),
        "Visual": ("ink", "selection"),
        "VisualNOS": ("ink", "selection"),
        "Search": ("ink", "match"),
        "IncSearch": ("ink", "match-active"),
        "CurSearch": ("ink", "match-active"),
        "MatchParen": ("ink", "match-active"),
        "DiffAdd": ("ink", "added"),
        "DiffDelete": ("error", "removed"),
        "DiffChange": ("ink", "changed"),
        "DiffText": ("ink", "added-word"),
        "StatusLine": ("branch", "surface"),
        "StatusLineNC": ("comment", "surface"),
        "WinBar": ("branch", "surface"),
        "WinBarNC": ("comment", "surface"),
        "FloatShadow": ("ink", "surface"),
        "FloatShadowThrough": ("ink", "surface"),
        "Added": ("success", "canvas"),
        "Removed": ("error", "canvas"),
        "Changed": ("warning", "canvas"),
        "OkMsg": ("success", "canvas"),
        "RedrawDebugClear": ("ink", "changed"),
        "RedrawDebugComposed": ("ink", "added"),
        "RedrawDebugRecompose": ("ink", "removed"),
        "DiagnosticDeprecated": ("comment", "canvas"),
        "WinSeparator": ("boundary", "canvas"),
        "Pmenu": ("ink", "surface"),
        "PmenuSel": ("ink", "selection"),
        "PmenuSbar": ("boundary", "surface"),
        "PmenuThumb": ("ink", "surface"),
        "TabLine": ("comment", "surface"),
        "TabLineSel": ("ink", "selection"),
        "TabLineFill": ("comment", "surface"),
        "NonText": ("muted", "canvas"),
        "SpecialKey": ("muted", "canvas"),
        "Whitespace": ("muted", "canvas"),
        "EndOfBuffer": ("muted", "canvas"),
        "Directory": ("directory", "canvas"),
        "Title": ("ink", "canvas"),
        "ErrorMsg": ("error", "canvas"),
        "WarningMsg": ("warning", "canvas"),
        "MoreMsg": ("success", "canvas"),
        "Question": ("type", "canvas"),
        "ModeMsg": ("ink", "canvas"),
        "QuickFixLine": ("ink", "selection"),
        "Conceal": ("comment", "canvas"),
        "Todo": ("warning", "canvas"),
    }
    for group, role in {
        "Comment": "comment",
        "Statement": "keyword",
        "PreProc": "keyword",
        "Identifier": "ink",
        "Constant": "number",
        "Number": "number",
        "String": "string",
        "Character": "string",
        "Boolean": "number",
        "Float": "number",
        "Operator": "ink",
        "Type": "type",
        "Function": "function",
        "Special": "type",
        "Delimiter": "ink",
        "Underlined": "link",
        "Error": "error",
    }.items():
        groups[group] = (role, "canvas")
    groups.update({f"@{group}": (role, "canvas") for group, role in SYNTAX.items()})
    groups["@variable.builtin"] = ("type", "canvas")
    for level, role in (
        ("Error", "error"),
        ("Warn", "warning"),
        ("Info", "type"),
        ("Hint", "comment"),
        ("Ok", "success"),
    ):
        for prefix in (
            "Diagnostic",
            "DiagnosticSign",
            "DiagnosticVirtualText",
            "DiagnosticFloating",
        ):
            groups[prefix + level] = (role, "canvas")
    return groups


def neovim(p: Palette, mode: str, ansi: list[str]) -> str:
    lines = [
        f"vim.o.background = '{'light' if mode == 'chalk' else 'dark'}'",
        "vim.o.termguicolors = true",
        "vim.cmd('highlight clear')",
        "if vim.fn.exists('syntax_on') == 1 then vim.cmd('syntax reset') end",
        f"vim.g.colors_name = 'maesglas-{mode}'",
    ]
    for group, (fg, bg) in highlights().items():
        lines.append(
            f"vim.api.nvim_set_hl(0, '{group}', "
            f"{{ fg = '{p[fg]}', bg = '{p[bg]}', italic = false, bold = false }})"
        )
    for group, role in (
        ("SpellBad", "error"),
        ("SpellCap", "warning"),
        ("SpellRare", "type"),
        ("SpellLocal", "type"),
    ):
        lines.append(
            f"vim.api.nvim_set_hl(0, '{group}', "
            f"{{ fg = '{p['ink']}', bg = '{p['canvas']}', sp = '{p[role]}', "
            "undercurl = true })"
        )
    for level, role in (
        ("Error", "error"),
        ("Warn", "warning"),
        ("Info", "type"),
        ("Hint", "comment"),
        ("Ok", "success"),
    ):
        lines.append(
            f"vim.api.nvim_set_hl(0, 'DiagnosticUnderline{level}', "
            f"{{ sp = '{p[role]}', undercurl = true }})"
        )
    for i, role in enumerate(ansi):
        lines.append(f"vim.g.terminal_color_{i} = '{p[role]}'")
    return "\n".join(lines) + "\n"


def helix(p: Palette) -> str:
    groups = {key: (role, "canvas") for key, role in SYNTAX.items()}
    groups.update(
        {
            "ui.background": ("ink", "canvas"),
            "ui.text": ("ink", "canvas"),
            "ui.text.focus": ("ink", "selection"),
            "ui.text.inactive": ("comment", "canvas"),
            "ui.text.info": ("ink", "surface"),
            "ui.cursor": ("canvas", "type"),
            "ui.cursor.primary": ("canvas", "type"),
            "ui.cursor.match": ("ink", "match-active"),
            "ui.cursorline.primary": ("ink", "surface"),
            "ui.cursorline.secondary": ("ink", "surface"),
            "ui.selection": ("ink", "selection"),
            "ui.selection.primary": ("ink", "selection"),
            "ui.linenr": ("line-number", "canvas"),
            "ui.linenr.selected": ("ink", "surface"),
            "ui.statusline": ("branch", "surface"),
            "ui.statusline.inactive": ("comment", "surface"),
            "ui.statusline.normal": ("ink", "surface"),
            "ui.statusline.insert": ("success", "surface"),
            "ui.statusline.select": ("ink", "selection"),
            "ui.statusline.separator": ("boundary", "surface"),
            "ui.popup": ("ink", "surface"),
            "ui.popup.info": ("ink", "surface"),
            "ui.window": ("boundary", "canvas"),
            "ui.help": ("ink", "surface"),
            "ui.menu": ("ink", "surface"),
            "ui.menu.selected": ("ink", "selection"),
            "ui.menu.scroll": ("boundary", "surface"),
            "ui.virtual": ("muted", "canvas"),
            "ui.virtual.indent-guide": ("boundary", "canvas"),
            "ui.virtual.jump-label": ("type", "canvas"),
            "ui.highlight": ("ink", "match"),
            "ui.highlight.frameline": ("ink", "match"),
            "markup.heading": ("ink", "canvas"),
            "markup.link.text": ("link", "canvas"),
            "markup.link.url": ("link", "canvas"),
            "markup.raw": ("string", "surface"),
            "diff.plus": ("success", "canvas"),
            "diff.minus": ("error", "canvas"),
            "diff.delta": ("warning", "canvas"),
            "warning": ("warning", "canvas"),
            "error": ("error", "canvas"),
            "info": ("type", "canvas"),
            "hint": ("comment", "canvas"),
        }
    )
    lines = [f'"{key}" = {{ fg = "{p[fg]}", bg = "{p[bg]}" }}' for key, (fg, bg) in groups.items()]
    for level, role in (
        ("error", "error"),
        ("warning", "warning"),
        ("info", "type"),
        ("hint", "comment"),
    ):
        lines.append(
            f'"diagnostic.{level}" = {{ underline = {{ color = "{p[role]}", style = "curl" }} }}'
        )
    return "\n".join(lines) + "\n"


def vscode(p: Palette, mode: str, ansi: list[str]) -> str:
    roles = {
        "foreground": "ink",
        "disabledForeground": "comment",
        "descriptionForeground": "comment",
        "errorForeground": "error",
        "focusBorder": "type",
        "contrastBorder": "boundary",
        "editor.background": "canvas",
        "editor.foreground": "ink",
        "editorLineNumber.foreground": "line-number",
        "editorLineNumber.activeForeground": "ink",
        "editorCursor.foreground": "type",
        "editor.selectionBackground": "selection",
        "editor.selectionForeground": "ink",
        "editor.inactiveSelectionBackground": "selection",
        "editor.lineHighlightBackground": "surface",
        "editorWhitespace.foreground": "muted",
        "editor.findMatchBackground": "match-active",
        "editor.findMatchForeground": "ink",
        "editor.findMatchHighlightBackground": "match",
        "editor.findMatchHighlightForeground": "ink",
        "editor.findMatchBorder": "boundary",
        "editor.findMatchHighlightBorder": "boundary",
        "editor.wordHighlightBackground": "match",
        "editor.wordHighlightStrongBackground": "match-active",
        "editorError.foreground": "error",
        "editorWarning.foreground": "warning",
        "editorInfo.foreground": "type",
        "editorHint.foreground": "comment",
        "editorGutter.addedBackground": "success",
        "editorGutter.deletedBackground": "error",
        "editorGutter.modifiedBackground": "warning",
        "diffEditor.insertedTextBackground": "added-word",
        "diffEditor.removedTextBackground": "removed-word",
        "diffEditor.insertedLineBackground": "added",
        "diffEditor.removedLineBackground": "removed",
        "textLink.foreground": "link",
        "textLink.activeForeground": "link",
        "textCodeBlock.background": "surface",
        "textPreformat.foreground": "ink",
        "button.background": "selection",
        "button.foreground": "ink",
        "button.hoverBackground": "surface",
        "button.secondaryBackground": "surface",
        "button.secondaryForeground": "ink",
        "input.background": "surface",
        "input.foreground": "ink",
        "input.border": "boundary",
        "input.placeholderForeground": "comment",
        "dropdown.background": "surface",
        "dropdown.foreground": "ink",
        "dropdown.border": "boundary",
        "list.activeSelectionBackground": "selection",
        "list.activeSelectionForeground": "ink",
        "list.inactiveSelectionBackground": "selection",
        "list.inactiveSelectionForeground": "ink",
        "list.hoverBackground": "surface",
        "list.hoverForeground": "ink",
        "list.highlightForeground": "type",
        "list.warningForeground": "warning",
        "list.errorForeground": "error",
        "sideBar.background": "surface",
        "sideBar.foreground": "ink",
        "sideBar.border": "boundary",
        "activityBar.background": "surface",
        "activityBar.foreground": "ink",
        "activityBar.inactiveForeground": "comment",
        "activityBar.border": "boundary",
        "statusBar.background": "surface",
        "statusBar.foreground": "ink",
        "statusBar.noFolderBackground": "surface",
        "statusBar.noFolderForeground": "ink",
        "statusBar.debuggingBackground": "changed",
        "statusBar.debuggingForeground": "ink",
        "statusBarItem.warningBackground": "changed",
        "statusBarItem.warningForeground": "warning",
        "statusBarItem.errorBackground": "removed",
        "statusBarItem.errorForeground": "error",
        "titleBar.activeBackground": "surface",
        "titleBar.activeForeground": "ink",
        "titleBar.inactiveBackground": "surface",
        "titleBar.inactiveForeground": "comment",
        "tab.activeBackground": "canvas",
        "tab.activeForeground": "ink",
        "tab.inactiveBackground": "surface",
        "tab.inactiveForeground": "comment",
        "panel.background": "canvas",
        "panel.border": "boundary",
        "editorWidget.background": "surface",
        "editorWidget.foreground": "ink",
        "editorWidget.border": "boundary",
        "terminal.background": "canvas",
        "terminal.foreground": "ink",
        "terminalCursor.foreground": "type",
        "terminal.selectionBackground": "selection",
        "terminal.selectionForeground": "ink",
        "terminal.findMatchBackground": "match-active",
        "terminal.findMatchHighlightBackground": "match",
    }
    colors = {key: p[role] for key, role in roles.items()}
    for i, role in enumerate(ansi):
        name = ("Bright" if i >= 8 else "") + ANSI_NAMES[i % 8].title()
        colors["terminal.ansi" + name] = p[role]
    tokens = [
        {"scope": scope, "settings": {"foreground": p[role], "fontStyle": ""}}
        for scope, role in SYNTAX.items()
    ]
    return encoded(
        {
            "$schema": "vscode://schemas/color-theme",
            "name": f"Maesglas {mode.title()}",
            "type": "light" if mode == "chalk" else "dark",
            "colors": colors,
            "tokenColors": tokens,
            "semanticHighlighting": True,
            "semanticTokenColors": {key: p[role] for key, role in SYNTAX.items()},
        }
    )


def zed(p: Palette, mode: str, ansi: list[str]) -> str:
    roles: dict[str, str] = {}
    for role, names in {
        "canvas": (
            "background editor.background editor.gutter.background "
            "terminal.background terminal.ansi.background"
        ),
        "selection": (
            "element.active element.hover element.selected element.disabled ghost_element.active "
            "ghost_element.hover ghost_element.selected ghost_element.disabled "
            "tab.active_background editor.highlighted_line.background "
            "editor.document_highlight.read_background editor.document_highlight.write_background "
            "editor.document_highlight.bracket_background "
            "drop_target.background"
        ),
        "boundary": (
            "border border.variant border.disabled border.transparent pane_group.border "
            "editor.indent_guide editor.wrap_guide panel.indent_guide scrollbar.thumb.border "
            "scrollbar.track.border scrollbar.thumb.background scrollbar.thumb.hover_background"
        ),
        "type": (
            "border.focused border.selected pane.focused_border panel.focused_border "
            "editor.indent_guide_active editor.active_wrap_guide panel.indent_guide_active "
            "panel.indent_guide_hover text.accent icon.accent link_text.hover"
        ),
        "ink": (
            "text icon editor.foreground editor.active_line_number "
            "terminal.foreground terminal.bright_foreground"
        ),
        "comment": (
            "text.muted text.disabled text.placeholder icon.muted icon.disabled icon.placeholder "
            "terminal.dim_foreground editor.invisible editor.line_number"
        ),
        "match": "search.match_background",
        "surface": (
            "surface.background elevated_surface.background panel.background status_bar.background "
            "title_bar.background title_bar.inactive_background toolbar.background "
            "tab_bar.background tab.inactive_background editor.subheader.background "
            "element.background ghost_element.background "
            "scrollbar.track.background editor.active_line.background"
        ),
    }.items():
        roles.update(dict.fromkeys(names.split(), role))
    for name, role, ground in (
        ("conflict", "warning", "changed"),
        ("created", "success", "added"),
        ("deleted", "error", "removed"),
        ("error", "error", "removed"),
        ("hidden", "comment", "surface"),
        ("hint", "comment", "surface"),
        ("ignored", "comment", "surface"),
        ("info", "type", "surface"),
        ("modified", "warning", "changed"),
        ("predictive", "comment", "surface"),
        ("renamed", "type", "surface"),
        ("success", "success", "added"),
        ("unreachable", "comment", "surface"),
        ("warning", "warning", "changed"),
    ):
        roles.update({name: role, name + ".background": ground, name + ".border": "boundary"})
    style: dict[str, object] = {key: p[role] for key, role in roles.items()}
    for bank, offset in (("", 0), ("bright_", 8), ("dim_", 0)):
        for i, name in enumerate(ANSI_NAMES):
            style["terminal.ansi." + bank + name] = p[ansi[offset + i]]
    style["syntax"] = {
        key: {"color": p[role], "font_style": "normal", "font_weight": 400}
        for key, role in SYNTAX.items()
    }
    style["players"] = [
        {"cursor": p["type"], "background": p["selection"], "selection": p["selection"]}
    ]
    style["accents"] = [p["type"]]
    return encoded(
        {
            "$schema": "https://zed.dev/schema/themes/v0.2.0.json",
            "author": "Maesglas",
            "name": f"Maesglas {mode.title()}",
            "themes": [
                {
                    "name": f"Maesglas {mode.title()}",
                    "appearance": "light" if mode == "chalk" else "dark",
                    "style": style,
                }
            ],
        }
    )


def iterm2(p: Palette, ansi: list[str]) -> str:
    colors = {
        "Foreground Color": p["ink"],
        "Background Color": p["canvas"],
        "Bold Color": p["ink"],
        "Cursor Color": p["type"],
        "Cursor Text Color": p["canvas"],
        "Selection Color": p["selection"],
        "Selected Text Color": p["ink"],
        "Link Color": p["link"],
    } | {f"Ansi {i} Color": p[role] for i, role in enumerate(ansi)}
    values = {
        key: {
            "Color Space": "sRGB",
            **{
                channel + " Component": int(color[i : i + 2], 16) / 255
                for channel, i in (("Red", 1), ("Green", 3), ("Blue", 5))
            },
        }
        for key, color in colors.items()
    }
    return plistlib.dumps(values, sort_keys=False).decode()


def windows_terminal(p: Palette, mode: str, ansi: list[str]) -> str:
    scheme = {
        "name": f"Maesglas {mode.title()}",
        "background": p["canvas"],
        "foreground": p["ink"],
        "cursorColor": p["type"],
        "selectionBackground": p["selection"],
    }
    for i, role in enumerate(ansi):
        name = ANSI_NAMES[i % 8]
        name = "purple" if name == "magenta" else name
        scheme[("bright" + name.title()) if i >= 8 else name] = p[role]
    return encoded(scheme)


# This complete candidate map is used only by the shared-token rejection probe.
CLAUDE_ROLES = {
    "autoAccept": "type",
    "autoAcceptShimmer": "type",
    "skill": "type",
    "bashBorder": "keyword",
    "claude": "branch",
    "claudeShimmer": "branch",
    "claudeBlue_FOR_SYSTEM_SPINNER": "function",
    "claudeBlueShimmer_FOR_SYSTEM_SPINNER": "function",
    "permission": "type",
    "permissionShimmer": "type",
    "planMode": "type",
    "ide": "function",
    "promptBorder": "boundary",
    "promptBorderShimmer": "boundary",
    "text": "ink",
    "inverseText": "ink",
    "inactive": "comment",
    "inactiveShimmer": "comment",
    "subtle": "comment",
    "suggestion": "type",
    "remember": "keyword",
    "background": "type",
    "success": "success",
    "error": "error",
    "warning": "warning",
    "merged": "branch",
    "warningShimmer": "warning",
    "diffAdded": "added",
    "diffRemoved": "removed",
    "diffAddedDimmed": "added",
    "diffRemovedDimmed": "removed",
    "diffAddedWord": "success",
    "diffRemovedWord": "error",
    "red_FOR_SUBAGENTS_ONLY": "error",
    "blue_FOR_SUBAGENTS_ONLY": "function",
    "green_FOR_SUBAGENTS_ONLY": "success",
    "yellow_FOR_SUBAGENTS_ONLY": "warning",
    "purple_FOR_SUBAGENTS_ONLY": "branch",
    "orange_FOR_SUBAGENTS_ONLY": "warning",
    "pink_FOR_SUBAGENTS_ONLY": "keyword",
    "cyan_FOR_SUBAGENTS_ONLY": "type",
    "professionalBlue": "function",
    "chromeYellow": "warning",
    "clawd_body": "branch",
    "clawd_background": "canvas",
    "userMessageBackground": "surface",
    "userMessageBackgroundHover": "selection",
    "composerSidebarBackground": "surface",
    "selectionBg": "selection",
    "bashMessageBackgroundColor": "surface",
    "memoryBackgroundColor": "surface",
    "rate_limit_fill": "type",
    "rate_limit_empty": "comment",
    "fastMode": "warning",
    "fastModeShimmer": "warning",
    "effortUltra": "keyword",
    "briefLabelYou": "function",
    "briefLabelClaude": "branch",
}
CLAUDE_BACKGROUNDS = {
    "diffAdded",
    "diffRemoved",
    "diffAddedDimmed",
    "diffRemovedDimmed",
    "clawd_background",
    "userMessageBackground",
    "userMessageBackgroundHover",
    "composerSidebarBackground",
    "selectionBg",
    "bashMessageBackgroundColor",
    "memoryBackgroundColor",
}
for _name, _role in (
    ("red", "error"),
    ("orange", "warning"),
    ("yellow", "warning"),
    ("green", "success"),
    ("blue", "function"),
    ("indigo", "type"),
    ("violet", "keyword"),
):
    CLAUDE_ROLES["rainbow_" + _name] = _role
    CLAUDE_ROLES["rainbow_" + _name + "_shimmer"] = _role


def claude_code(p: Palette, mode: str) -> str:
    return encoded(
        {
            "name": f"Maesglas {mode.title()}",
            "base": "light" if mode == "chalk" else "dark",
            "overrides": {key: p[role] for key, role in CLAUDE_ROLES.items()},
        }
    )


def k9s(p: Palette) -> str:
    def colors(**roles: str) -> dict[str, str]:
        return {key: p[role] for key, role in roles.items()}

    return encoded(
        {
            "k9s": {
                "body": colors(
                    fgColor="ink",
                    bgColor="canvas",
                    logoColor="branch",
                    logoColorMsg="ink",
                    logoColorInfo="type",
                    logoColorWarn="warning",
                    logoColorError="error",
                ),
                "prompt": colors(fgColor="ink", bgColor="surface", suggestColor="type")
                | {"border": colors(command="type", default="boundary")},
                "help": colors(
                    fgColor="ink",
                    bgColor="canvas",
                    sectionColor="type",
                    keyColor="link",
                    numKeyColor="number",
                ),
                "info": colors(
                    sectionColor="type",
                    fgColor="ink",
                    cpuColor="type",
                    memColor="warning",
                    k9sRevColor="branch",
                ),
                "dialog": colors(
                    fgColor="ink",
                    bgColor="surface",
                    buttonFgColor="ink",
                    buttonBgColor="selection",
                    buttonFocusFgColor="ink",
                    buttonFocusBgColor="selection",
                    labelFgColor="type",
                    fieldFgColor="ink",
                ),
                "frame": {
                    "border": colors(fgColor="boundary", focusColor="type"),
                    "menu": colors(fgColor="ink", keyColor="type", numKeyColor="number")
                    | {"fgStyle": "b"},
                    "crumbs": colors(fgColor="ink", bgColor="surface", activeColor="selection"),
                    "status": colors(
                        newColor="type",
                        modifyColor="warning",
                        addColor="success",
                        pendingColor="warning",
                        errorColor="error",
                        highlightColor="type",
                        killColor="error",
                        completedColor="success",
                    ),
                    "title": colors(
                        fgColor="ink",
                        bgColor="surface",
                        highlightColor="type",
                        counterColor="comment",
                        filterColor="warning",
                    ),
                },
                "views": {
                    "table": colors(
                        fgColor="ink",
                        bgColor="canvas",
                        cursorFgColor="ink",
                        cursorBgColor="selection",
                        markColor="warning",
                    )
                    | {
                        "header": colors(
                            fgColor="ink",
                            bgColor="surface",
                            sorterColor="type",
                            selectedSortColumnColor="type",
                        )
                    },
                    "xray": colors(
                        fgColor="ink",
                        bgColor="canvas",
                        cursorColor="selection",
                        cursorTextColor="ink",
                        graphicColor="boundary",
                    ),
                    "charts": colors(
                        bgColor="canvas",
                        dialBgColor="canvas",
                        chartBgColor="canvas",
                        focusFgColor="ink",
                        focusBgColor="selection",
                    )
                    | {
                        "defaultDialColors": [p["success"], p["error"]],
                        "defaultChartColors": [p["success"], p["error"]],
                        "resourceColors": {
                            "cpu": [p["type"], p["comment"]],
                            "mem": [p["warning"], p["comment"]],
                        },
                    },
                    "yaml": colors(keyColor="type", valueColor="ink", colonColor="comment"),
                    "picker": colors(mainColor="ink", focusColor="type", shortcutColor="link"),
                    "logs": colors(fgColor="ink", bgColor="canvas")
                    | {
                        "indicator": colors(
                            fgColor="ink",
                            bgColor="surface",
                            toggleOnColor="success",
                            toggleOffColor="comment",
                        )
                    },
                },
            }
        }
    )


def gh_dash(p: Palette) -> str:
    groups = {
        "text": {
            "primary": "ink",
            "secondary": "comment",
            "inverted": "ink",
            "faint": "comment",
            "warning": "warning",
            "success": "success",
            "error": "error",
            "actor": "branch",
        },
        "background": {"selected": "selection"},
        "border": {"primary": "boundary", "secondary": "boundary", "faint": "boundary"},
        "icon": dict.fromkeys(
            ("newcontributor", "contributor", "collaborator", "member", "owner", "unknownrole"),
            "comment",
        ),
    }
    return encoded(
        {
            "theme": {
                "colors": {
                    section: {key: p[role] for key, role in entries.items()}
                    for section, entries in groups.items()
                }
            }
        }
    )


def fast_syntax_highlighting(mode: str) -> str:
    sections = {
        "base": {
            "default": "default",
            "unknown-token": "red,bold",
            "commandseparator": "default",
            "redirection": "default",
            "here-string-tri": "yellow",
            "here-string-text": "green",
            "here-string-var": "cyan",
            "exec-descriptor": "yellow",
            "comment": "white",
            "correct-subtle": "cyan",
            "incorrect-subtle": "red",
            "subtle-separator": "default",
            "subtle-bg": "default",
            "secondary": "",
            "recursive-base": "default",
        },
        "command-point": {
            "reserved-word": "magenta",
            "subcommand": "blue",
            "alias": "blue",
            "suffix-alias": "blue",
            "global-alias": "blue",
            "builtin": "blue",
            "function": "blue",
            "command": "blue",
            "precommand": "blue",
            "hashed-command": "blue",
            "single-sq-bracket": "default",
            "double-sq-bracket": "default",
            "double-paren": "default",
        },
        "paths": {
            "path": "blue",
            "pathseparator": "default",
            "path-to-dir": "blue,underline",
            "globbing": "cyan",
            "globbing-ext": "cyan",
        },
        "brackets": {
            "paired-bracket": "cyan,underline",
            "bracket-level-1": "default",
            "bracket-level-2": "cyan",
            "bracket-level-3": "magenta",
        },
        "arguments": {
            "single-hyphen-option": "cyan",
            "double-hyphen-option": "cyan",
            "back-quoted-argument": "green",
            "single-quoted-argument": "green",
            "double-quoted-argument": "green",
            "dollar-quoted-argument": "green",
            "optarg-string": "green",
            "optarg-number": "yellow",
        },
        "in-string": {
            "back-dollar-quoted-argument": "cyan",
            "back-or-dollar-double-quoted-argument": "cyan",
        },
        "other": {
            "variable": "default",
            "assign": "default",
            "assign-array-bracket": "default",
            "history-expansion": "magenta",
        },
        "math": {"mathvar": "default", "mathnum": "yellow", "matherr": "red"},
        "for-loop": {
            "forvar": "default",
            "fornum": "yellow",
            "foroper": "magenta",
            "forsep": "default",
        },
        "case": {"case-input": "default", "case-parentheses": "default", "case-condition": "green"},
    }
    aliases = {
        "pathseparator": "path_pathseparator",
        "forvar": "for-loop-variable",
        "fornum": "for-loop-number",
        "foroper": "for-loop-operator",
        "forsep": "for-loop-separator",
    }
    styles = {
        aliases.get(key, key): ",".join(
            value if value in ("bold", "underline") else "fg=" + value for value in style.split(",")
        )
        for entries in sections.values()
        for key, style in entries.items()
        if key != "secondary"
    }
    styles["secondary"] = f"maesglas-{mode}"
    lines = [
        f"typeset -g FAST_THEME_NAME=maesglas-{mode}",
        f"zstyle :plugin:fast-syntax-highlighting theme maesglas-{mode}",
        "typeset -gA FAST_HIGHLIGHT_STYLES",
        "FAST_HIGHLIGHT_STYLES=(",
    ]
    for prefix in ("", "default", f"maesglas-{mode}"):
        lines.extend(f"  '{prefix}{key}' '{value}'" for key, value in styles.items())
    lines.extend([")", ""])
    return "\n".join(lines)


def render(design: Design) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    for mode, p in design.colors.items():
        ansi = design.ansi
        contents = {
            "alacritty": alacritty(p, ansi),
            "kitty": kitty(p, ansi),
            "wezterm": wezterm(p, mode, ansi),
            "neovim": neovim(p, mode, ansi),
            "helix": helix(p),
            "vscode": vscode(p, mode, ansi),
            "zed": zed(p, mode, ansi),
            "iterm2": iterm2(p, ansi),
            "windows-terminal": windows_terminal(p, mode, ansi),
            "k9s": k9s(p),
            "gh-dash": gh_dash(p),
            "fast-syntax-highlighting": fast_syntax_highlighting(mode),
        }
        for port, content in contents.items():
            files[f"ports/{port}/maesglas-{mode}.{PORTS[port][1]}"] = content.encode()
    files["ports/vscode/package.json"] = encoded(
        {
            "name": "maesglas",
            "publisher": "maesglas",
            "displayName": "Maesglas",
            "version": design.version,
            "description": "Independent Chalk and Shale color themes.",
            "license": "MIT",
            "engines": {"vscode": "^1.143.0"},
            "categories": ["Themes"],
            "contributes": {
                "themes": [
                    {
                        "label": f"Maesglas {mode.title()}",
                        "uiTheme": "vs" if mode == "chalk" else "vs-dark",
                        "path": f"./maesglas-{mode}.json",
                    }
                    for mode in design.colors
                ]
            },
        }
    ).encode()
    files["ports/vscode/LICENSE"] = (ROOT / "LICENSE").read_bytes()
    return files

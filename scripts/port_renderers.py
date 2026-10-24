"""Appearance-only ports. No installation, process hooks, or user state."""

import json
import plistlib
from collections.abc import Callable

import extra_ports
from model import Design, mapping, number, text

type Palette = dict[str, str]
type Renderer = Callable[[Palette, str, list[str], Design], str]

PORTS: dict[str, tuple[str, str, str]] = {
    "ghostty": ("Ghostty", "conf", "Load the file with `config-file`."),
    "starship": ("Starship", "toml", "Point `STARSHIP_CONFIG` at the preset."),
    "vim": ("Vim", "vim", "Source the appearance file after your other settings."),
    "textmate": ("bat and delta", "tmTheme", "Build the theme cache before selecting the theme."),
    "delta": ("delta", "gitconfig", "Include the file, then compose the named feature."),
    "git": ("Git", "gitconfig", "Include the file; identity and signing remain unchanged."),
    "nano": ("nano", "nanorc", "Include the file after other appearance settings."),
    "fzf": ("fzf", "sh", "Source the file after other picker options."),
    "tmux": ("tmux", "conf", "Source the file from your configuration."),
    "eza": ("eza", "yml", "Copy the file as `theme.yml` in `EZA_CONFIG_DIR`."),
    "glow": ("glow", "json", "Pass the file to `glow --style`."),
    "lazygit": ("lazygit", "yml", "Merge the `gui` mapping into your configuration."),
    "yazi": ("yazi", "toml", "Copy as `theme.toml`; use the matching terminal variant."),
}

ALL_PORTS = PORTS | extra_ports.PORTS

DROPPED: dict[str, str] = {
    "btop": "Its native banner uses foreground colors that the theme cannot replace.",
    "Claude Code": (
        "Counter foregrounds and word-diff backgrounds share tokens; the format "
        "cannot override word-diff text independently. Shared colors cannot meet "
        "both 4.5:1 pairs with the Maesglas canvas and ink."
    ),
    "Terminal.app": "Archived-color profile import was not verified.",
    "Sublime Text": "The TextMate file was not loaded in this application.",
}


def ghostty(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    lines = [
        f"background = {p['canvas']}",
        f"foreground = {p['ink']}",
        f"selection-background = {p['selection']}",
        f"selection-foreground = {p['ink']}",
        f"cursor-color = {p['type']}",
        "cursor-style = bar",
        "cursor-style-blink = false",
        f"window-theme = {'light' if mode == 'chalk' else 'dark'}",
        "window-colorspace = srgb",
        "alpha-blending = linear-corrected",
        "background-opacity = 1",
        "unfocused-split-opacity = 1",
        f"font-family = {text(design.leaf('fonts', 'family'))}",
        f"font-size = {number(design.leaf('fonts', 'terminal')):g}",
        *(
            f"font-feature = {key}={int(number(value))}"
            for key, value in mapping(design.leaf("fonts", "features")).items()
        ),
        "font-synthetic-style = false",
        f"adjust-cell-height = {number(design.leaf('components', 'cell-height')):g}%",
        f"window-padding-x = {number(design.leaf('components', 'terminal-padding')):g}",
        f"window-padding-y = {number(design.leaf('components', 'terminal-padding')):g}",
        "bold-color =",
        "minimum-contrast = 4.5",
        "custom-shader-animation = false",
        "keybind = super+shift+enter=toggle_split_zoom",
    ]
    lines.extend(f"palette = {index}={p[role]}" for index, role in enumerate(ansi))
    return "\n".join(lines) + "\n"


def starship(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    prompt = (
        "$username$hostname$directory$git_branch$git_status$git_state"
        "$cmd_duration$jobs$line_break$status$character"
    )
    return f"""add_newline = true
format = "{prompt}"
right_format = ""

[username]
show_always = false
format = "[$user]($style) "
style_root = "bold {p["error"]}"
style_user = "{p["comment"]}"

[hostname]
ssh_only = true
format = "[ssh:$hostname]($style) "
style = "{p["comment"]}"

[directory]
style = "{p["directory"]}"
format = "[$path]($style) "
truncation_length = 4
truncate_to_repo = false
home_symbol = "~"

[git_branch]
symbol = ""
style = "{p["branch"]}"
format = "[$branch]($style) "

[git_status]
style = "{p["warning"]}"
format = "([$all_status$ahead_behind]($style) )"
staged = "+$count "
modified = "~$count "
untracked = "?$count "
deleted = "-$count "
renamed = ">$count "
conflicted = "conflict:$count "
stashed = "stash:$count "
ahead = "up$count "
behind = "down$count "
diverged = "up$ahead_count down$behind_count "

[git_state]
style = "{p["warning"]}"
format = "[$state( $progress_current/$progress_total)]($style) "

[cmd_duration]
min_time = 2000
style = "{p["comment"]}"
format = "[$duration]($style) "

[jobs]
style = "{p["comment"]}"
format = "[jobs:$number]($style) "
number_threshold = 1
symbol_threshold = 1

[status]
disabled = false
pipestatus = true
format = "[exit $status]($style) "
style = "{p["error"]}"

[character]
success_symbol = "[>](bold {p["ink"]})"
error_symbol = "[>](bold {p["error"]})"
vimcmd_symbol = "[<](bold {p["ink"]})"
"""


def vim(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    groups = {
        "Normal": ("ink", "canvas"),
        "NormalNC": ("ink", "canvas"),
        "Comment": ("comment", "canvas"),
        "LineNr": ("line-number", "canvas"),
        "CursorLineNr": ("ink", "surface"),
        "CursorLine": ("ink", "surface"),
        "Statement": ("keyword", "canvas"),
        "PreProc": ("keyword", "canvas"),
        "Identifier": ("ink", "canvas"),
        "Constant": ("number", "canvas"),
        "Number": ("number", "canvas"),
        "String": ("string", "canvas"),
        "Character": ("string", "canvas"),
        "Operator": ("ink", "canvas"),
        "SpecialComment": ("comment", "canvas"),
        "Underlined": ("link", "canvas"),
        "Ignore": ("comment", "canvas"),
        "Type": ("type", "canvas"),
        "Function": ("function", "canvas"),
        "Special": ("type", "canvas"),
        "Delimiter": ("ink", "canvas"),
        "NonText": ("muted", "canvas"),
        "SpecialKey": ("muted", "canvas"),
        "Folded": ("comment", "surface"),
        "FoldColumn": ("muted", "canvas"),
        "SignColumn": ("ink", "canvas"),
        "Visual": ("ink", "selection"),
        "Search": ("ink", "search"),
        "IncSearch": ("ink", "search-active"),
        "DiffAdd": ("ink", "added"),
        "DiffDelete": ("error", "removed"),
        "DiffChange": ("ink", "changed"),
        "DiffText": ("ink", "added-word"),
        "StatusLine": ("branch", "surface"),
        "StatusLineNC": ("comment", "surface"),
        "VertSplit": ("boundary", "canvas"),
        "Pmenu": ("ink", "surface"),
        "PmenuSel": ("ink", "selection"),
        "PmenuSbar": ("boundary", "surface"),
        "PmenuThumb": ("ink", "surface"),
        "Error": ("error", "canvas"),
        "ErrorMsg": ("error", "canvas"),
        "WarningMsg": ("warning", "canvas"),
        "Todo": ("warning", "canvas"),
        "Title": ("ink", "canvas"),
        "Directory": ("directory", "canvas"),
        "MatchParen": ("ink", "search-active"),
        "TabLine": ("comment", "surface"),
        "TabLineSel": ("ink", "selection"),
        "TabLineFill": ("comment", "surface"),
        "Conceal": ("comment", "canvas"),
        "CursorColumn": ("ink", "surface"),
        "ColorColumn": ("ink", "surface"),
        "CursorLineSign": ("ink", "surface"),
        "CursorLineFold": ("comment", "surface"),
        "LineNrAbove": ("line-number", "canvas"),
        "LineNrBelow": ("line-number", "canvas"),
        "MoreMsg": ("success", "canvas"),
        "ModeMsg": ("ink", "canvas"),
        "Question": ("type", "canvas"),
        "QuickFixLine": ("ink", "selection"),
        "StatusLineTerm": ("branch", "surface"),
        "StatusLineTermNC": ("comment", "surface"),
        "VisualNOS": ("ink", "selection"),
        "WildMenu": ("ink", "selection"),
        "ToolbarLine": ("ink", "surface"),
        "ToolbarButton": ("ink", "selection"),
        "PmenuMatch": ("type", "surface"),
        "PmenuMatchSel": ("type", "selection"),
        "PmenuKind": ("comment", "surface"),
        "PmenuKindSel": ("comment", "selection"),
        "PmenuExtra": ("comment", "surface"),
        "PmenuExtraSel": ("comment", "selection"),
        "CurSearch": ("ink", "search-active"),
    }
    indices = {p[role]: index for index, role in enumerate(ansi)}
    lines = [
        f"set background={'light' if mode == 'chalk' else 'dark'}",
        "highlight clear",
        "if exists('syntax_on')",
        "  syntax reset",
        "endif",
        "set termguicolors",
        f"let g:colors_name = 'maesglas-{mode}'",
    ]
    for group, (fg, bg) in groups.items():
        index = indices.get(p[fg], 7)
        lines.append(
            f"highlight {group} guifg={p[fg]} guibg={p[bg]} gui=NONE "
            f"ctermfg={index} ctermbg=NONE cterm=NONE"
        )
    for group, role in (
        ("SpellBad", "error"),
        ("SpellCap", "warning"),
        ("SpellRare", "type"),
        ("SpellLocal", "type"),
    ):
        lines.append(
            f"highlight {group} guifg={p['ink']} guibg={p['canvas']} "
            f"guisp={p[role]} gui=undercurl cterm=underline"
        )
    return "\n".join(lines) + "\n"


def textmate(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    settings: list[dict[str, object]] = [
        {
            "settings": {
                "background": p["canvas"],
                "foreground": p["ink"],
                "caret": p["type"],
                "selection": p["selection"],
                "lineHighlight": p["surface"],
                "gutterForeground": p["line-number"],
            }
        }
    ]
    for scope, role in {
        "comment": "comment",
        "keyword, storage": "keyword",
        "string": "string",
        "constant.numeric, constant.language": "number",
        "entity.name.function, support.function": "function",
        "entity.name.type, entity.name.class, support.type, entity.name.tag": "type",
        "variable, punctuation": "ink",
        "invalid": "error",
        "markup.inserted": "success",
        "markup.deleted": "error",
        "markup.changed": "warning",
        "markup.heading": "ink",
        "markup.underline.link": "link",
    }.items():
        settings.append({"scope": scope, "settings": {"foreground": p[role], "fontStyle": ""}})
    return plistlib.dumps(
        {"name": f"Maesglas {mode.title()}", "settings": settings},
        sort_keys=False,
    ).decode()


def delta(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    output = f"""[delta "maesglas-{mode}"]
    {"light" if mode == "chalk" else "dark"} = true
    syntax-theme = maesglas-{mode}
    minus-style = syntax {p["removed"]}
    plus-style = syntax {p["added"]}
    minus-emph-style = {p["ink"]} {p["removed-word"]}
    plus-emph-style = {p["ink"]} {p["added-word"]}
    zero-style = syntax {p["canvas"]}
    line-numbers-minus-style = {p["comment"]}
    line-numbers-plus-style = {p["comment"]}
    line-numbers-zero-style = {p["comment"]}
    line-numbers-left-style = {p["comment"]}
    line-numbers-right-style = {p["comment"]}
    file-style = bold {p["ink"]}
    file-decoration-style = {p["boundary"]} box
    hunk-header-style = {p["function"]}
    hunk-header-decoration-style = {p["boundary"]} box
    keep-plus-minus-markers = true
"""
    return (
        "\n".join(
            f'{line.split(" = ", 1)[0]} = "{line.split(" = ", 1)[1]}"'
            if " = " in line and "#" in line
            else line
            for line in output.splitlines()
        )
        + "\n"
    )


def git_colors(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    sections = {
        "diff": {
            "plain": "ink",
            "meta": "comment",
            "frag": "function",
            "old": "error",
            "new": "success",
            "commit": "branch",
            "whitespace": "error",
        },
        "status": {
            "header": "comment",
            "added": "success",
            "changed": "warning",
            "untracked": "warning",
            "deleted": "error",
            "unmerged": "error",
            "branch": "branch",
        },
        "branch": {"current": "branch", "local": "branch", "remote": "branch"},
        "interactive": {"prompt": "ink", "header": "ink", "help": "comment", "error": "error"},
    }
    return (
        "\n".join(
            f'[color "{section}"]\n'
            + "\n".join(f'    {key} = "{p[role]}"' for key, role in fields.items())
            for section, fields in sections.items()
        )
        + "\n"
    )


def nano(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    lines = [
        "set linenumbers",
        "set tabsize 4",
        "set softwrap",
        "set atblanks",
        "set autoindent",
        "set stateflags",
        "set titlecolor bold,normal,normal",
        "set statuscolor normal,normal",
        "set promptcolor normal,normal",
        "set errorcolor bold,red,normal",
        "set numbercolor gray,normal",
        "set keycolor bold,blue,normal",
        "set functioncolor gray,normal",
        "set selectedcolor bold,normal,normal",
        "set spotlightcolor bold,yellow,normal",
        "set scrollercolor cyan,normal",
        "set stripecolor normal,normal",
        "set minicolor gray,normal",
    ]
    syntaxes = {
        "python": (
            r"\.py$",
            "def|class|return|if|else|for|in|import|from|with|as|raise|try|except",
            "#",
        ),
        "ruby": (r"\.rb$", "def|class|module|end|do|if|else|return|require", "#"),
        "rust": (r"\.rs$", "fn|let|mut|pub|use|impl|struct|enum|match|return", "//"),
        "shell": (r"\.(sh|zsh|bash)$", "if|then|else|fi|for|in|do|done|export|case|esac", "#"),
        "json": (r"\.(json|jsonc)$", "true|false|null", "//"),
        "yaml": (r"\.(yml|yaml)$", "true|false|null", "#"),
        "toml": (r"\.toml$", "true|false", "#"),
        "markdown": (r"\.(md|markdown)$", "", ""),
        "makefile": (r"(^|/)(Makefile|makefile)$", "include|ifdef|ifndef|endif", "#"),
        "diff": (r"\.(diff|patch)$", "", ""),
    }
    for name, (pattern, keywords, comment) in syntaxes.items():
        lines.extend(["", f'syntax "{name}" "{pattern}"'])
        if keywords:
            lines.append(f'color magenta "\\<({keywords})\\>"')
        lines.extend([r'color yellow "\<[0-9]+\>"', r'color green ""([^"\\]|\\.)*""'])
        if comment:
            lines.extend([f'color gray "{comment}.*$"', f'comment "{comment}"'])
        if name == "markdown":
            lines.extend([r'color bold,blue "^#{1,6} .*"', r'color cyan "\[[^]]+\]\([^)]+\)"'])
        if name == "diff":
            lines.extend([r'color green "^\+.*"', r'color red "^-.*"', r'color cyan "^@@.*"'])
        if name == "makefile":
            lines.append('tabgives "\t"')
    return "\n".join(lines) + "\n"


def fzf(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    fields = {
        "fg": "ink",
        "bg": "canvas",
        "fg+": "ink",
        "bg+": "selection",
        "hl": "type",
        "hl+": "type",
        "info": "comment",
        "prompt": "ink",
        "pointer": "branch",
        "marker": "success",
        "spinner": "comment",
        "header": "comment",
        "border": "boundary",
        "label": "ink",
        "gutter": "canvas",
        "preview-fg": "ink",
        "preview-bg": "surface",
    }
    colors = ",".join(f"{key}:{p[role]}" for key, role in fields.items())
    return (
        "#!/bin/sh\n"
        'if [ -z "${NO_COLOR+x}" ] && [ "${TERM:-dumb}" != dumb ] && [ -t 1 ]; then\n'
        f'  export FZF_DEFAULT_OPTS="${{FZF_DEFAULT_OPTS:-}} --color={colors} --pointer=>"\n'
        "fi\n"
    )


def tmux(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    return f"""set -g status-style "fg={p["ink"]},bg={p["surface"]}"
set -g message-style "fg={p["ink"]},bg={p["surface"]}"
set -g message-command-style "fg={p["ink"]},bg={p["surface"]}"
set -g mode-style "fg={p["ink"]},bg={p["selection"]}"
set -g pane-border-style "fg={p["boundary"]}"
set -g pane-active-border-style "fg={p["type"]}"
set -g window-status-style "fg={p["comment"]},bg={p["surface"]}"
set -g window-status-current-style "fg={p["ink"]},bg={p["selection"]},bold"
set -g window-status-activity-style "fg={p["warning"]},bg={p["surface"]}"
set -g window-status-bell-style "fg={p["error"]},bg={p["surface"]}"
set -g status-left " #S "
set -g status-right ""
set -g window-status-format " #I:#W "
set -g window-status-current-format " #I:#W* "
"""


def eza(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    groups = {
        "filekinds": {
            "normal": "ink",
            "directory": "directory",
            "symlink": "link",
            "pipe": "type",
            "block_device": "warning",
            "char_device": "warning",
            "socket": "type",
            "special": "type",
            "executable": "success",
            "mount_point": "directory",
        },
        "perms": dict.fromkeys(
            [
                "user_read",
                "user_write",
                "user_execute_file",
                "user_execute_other",
                "group_read",
                "group_write",
                "group_execute",
                "other_read",
                "other_write",
                "other_execute",
                "special_user_file",
                "special_other",
                "attribute",
            ],
            "comment",
        ),
        "size": dict.fromkeys(
            [
                "major",
                "minor",
                "number_byte",
                "number_kilo",
                "number_mega",
                "number_giga",
                "number_huge",
                "unit_byte",
                "unit_kilo",
                "unit_mega",
                "unit_giga",
                "unit_huge",
            ],
            "comment",
        ),
        "users": dict.fromkeys(
            ["user_you", "user_root", "user_other", "group_yours", "group_other", "group_root"],
            "ink",
        ),
        "links": {"normal": "comment", "multi_link_file": "link"},
        "git": {
            "new": "success",
            "modified": "warning",
            "deleted": "error",
            "renamed": "warning",
            "ignored": "comment",
            "conflicted": "error",
        },
        "git_repo": {
            "branch_main": "branch",
            "branch_other": "branch",
            "git_clean": "comment",
            "git_dirty": "warning",
        },
        "file_type": dict.fromkeys(
            [
                "image",
                "video",
                "music",
                "crypto",
                "document",
                "compressed",
                "temp",
                "compiled",
                "build",
                "source",
            ],
            "ink",
        ),
    }
    lines: list[str] = []
    for group, entries in groups.items():
        lines.append(f"{group}:")
        for key, role in entries.items():
            lines.append(f'  {key}: {{foreground: "{p[role]}", is_bold: false, is_dimmed: false}}')
    for key in [
        "punctuation",
        "date",
        "inode",
        "blocks",
        "header",
        "octal",
        "flags",
        "control_char",
    ]:
        lines.append(f'{key}: {{foreground: "{p["comment"]}"}}')
    lines.extend(
        [
            f'broken_symlink: {{foreground: "{p["error"]}", is_underline: true}}',
            f'broken_path_overlay: {{foreground: "{p["error"]}", is_underline: true}}',
        ]
    )
    lines.extend(
        [
            "security_context:",
            f'  none: {{foreground: "{p["comment"]}"}}',
            "  selinux:",
            *(
                f'    {key}: {{foreground: "{p["comment"]}"}}'
                for key in ("colon", "user", "role", "typ", "range")
            ),
        ]
    )
    return "\n".join(lines) + "\n"


def glow(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    style: dict[str, object] = {
        "document": {"color": p["ink"], "background_color": p["canvas"], "margin": 1},
        "paragraph": {},
        "heading": {"color": p["ink"], "bold": True, "block_suffix": "\n"},
        "block_quote": {"color": p["comment"], "indent": 1, "indent_token": "> "},
        "list": {"level_indent": 2},
        "item": {"block_prefix": "- "},
        "enumeration": {"block_prefix": ". "},
        "task": {"ticked": "[x] ", "unticked": "[ ] "},
        "emph": {"italic": True},
        "strong": {"bold": True},
        "strikethrough": {"crossed_out": True},
        "hr": {"color": p["boundary"], "format": "\n--------\n"},
        "link": {"color": p["link"], "underline": True},
        "link_text": {"color": p["link"], "underline": True},
        "image": {"color": p["link"]},
        "image_text": {"color": p["comment"], "format": "Image: {{.text}}"},
        "code": {"color": p["ink"], "background_color": p["surface"]},
    }
    style["code_block"] = {
        "color": p["ink"],
        "background_color": p["surface"],
        "margin": 1,
        "theme": "",
        "chroma": None,
    }
    for level in range(1, 7):
        style[f"h{level}"] = {"prefix": "#" * level + " "}
    return json.dumps(style, indent=2) + "\n"


def lazygit(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    roles = {
        "activeBorderColor": "type",
        "inactiveBorderColor": "boundary",
        "searchingActiveBorderColor": "warning",
        "optionsTextColor": "link",
        "selectedLineFgColor": "ink",
        "selectedLineBgColor": "selection",
        "inactiveViewSelectedLineBgColor": "selection",
        "cherryPickedCommitFgColor": "ink",
        "cherryPickedCommitBgColor": "added",
        "markedBaseCommitFgColor": "ink",
        "markedBaseCommitBgColor": "changed",
        "unstagedChangesColor": "warning",
        "defaultFgColor": "ink",
    }
    lines = ["gui:", '  nerdFontsVersion: ""', "  theme:"]
    lines.extend(f'    {key}: ["{p[role]}"]' for key, role in roles.items())
    lines.extend(
        [
            f'    authorColors: {{"*": "{p["comment"]}"}}',
            f'    branchColorPatterns: {{".*": "{p["branch"]}"}}',
        ]
    )
    return "\n".join(lines) + "\n"


def yazi(p: Palette, mode: str, ansi: list[str], design: Design) -> str:
    def style(fg: str = "ink", bg: str = "canvas", bold: bool = False) -> str:
        return (
            f'{{ fg = "{p[fg]}", bg = "{p[bg]}", '
            f"bold = {str(bold).lower()}, italic = false, reversed = false }}"
        )

    groups = {
        "app": {"overall": style()},
        "mgr": {
            "cwd": style("directory"),
            "find_keyword": style("ink", "search", True),
            "find_position": style("comment"),
            "symlink_target": style("link"),
            "marker_copied": style("success"),
            "marker_cut": style("error"),
            "marker_marked": style("type"),
            "marker_selected": style("warning"),
            "marker_symbol": '">"',
            "count_copied": style("success", "surface"),
            "count_cut": style("error", "surface"),
            "count_selected": style("warning", "surface"),
            "border_style": style("boundary"),
        },
        "tabs": {
            "active": style("ink", "selection", True),
            "inactive": style("comment", "surface"),
            "sep_inner": '{ open = "", close = "" }',
            "sep_outer": '{ open = "", close = "" }',
        },
        "mode": {
            f"{name}_{part}": style("ink", "surface")
            for name in ("normal", "select", "unset")
            for part in ("main", "alt")
        },
        "indicator": {
            "parent": style("ink", "selection"),
            "current": style("ink", "selection", True),
            "preview": style(),
            "padding": '{ open = "", close = "" }',
        },
        "status": {
            "overall": style("ink", "surface"),
            "sep_left": '{ open = "", close = "" }',
            "sep_right": '{ open = "", close = "" }',
            **{f"perm_{key}": style("comment") for key in ("sep", "type", "read", "write", "exec")},
            "progress_label": style(),
            "progress_normal": style("success", "surface"),
            "progress_error": style("error", "surface"),
        },
        "which": {
            "border": style("boundary"),
            "mask": style(),
            "cand": style("type"),
            "rest": style("comment"),
            "desc": style(),
            "separator": '" > "',
            "separator_style": style("comment"),
        },
        "confirm": {
            "border": style("boundary"),
            "title": style(),
            "body": style(),
            "list": style(),
            "btn_yes": style("ink", "selection", True),
            "btn_no": style(),
        },
        "spot": {
            "border": style("boundary"),
            "title": style(),
            "tbl_col": style("comment"),
            "tbl_cell": style("ink", "selection"),
        },
        "notify": {
            "title_info": style("success"),
            "title_warn": style("warning"),
            "title_error": style("error"),
            "icon_info": '"info"',
            "icon_warn": '"warning"',
            "icon_error": '"error"',
        },
        "pick": {
            "border": style("boundary"),
            "active": style("ink", "selection", True),
            "inactive": style(),
        },
        "input": {
            "border": style("boundary"),
            "title": style(),
            "value": style(),
            "selected": style("ink", "selection"),
        },
        "cmp": {
            "border": style("boundary"),
            "active": style("ink", "selection"),
            "inactive": style(),
            "icon_file": '"f"',
            "icon_folder": '"d"',
            "icon_command": '">"',
        },
        "tasks": {
            "border": style("boundary"),
            "title": style(),
            "hovered": style("ink", "selection", True),
        },
        "help": {
            "border": style("boundary"),
            "chord": style("type"),
            "action": style(),
            "hovered": style("ink", "selection", True),
        },
        "filetype": {
            "rules": "[\n"
            + f'  {{ url = "*", is = "orphan", fg = "{p["error"]}", underline = true }},\n'
            + f'  {{ url = "*", is = "exec", fg = "{p["success"]}" }},\n'
            + f'  {{ url = "*/", fg = "{p["directory"]}" }},\n'
            + f'  {{ url = "*", fg = "{p["ink"]}" }}\n]',
        },
        "icon": {
            "globs": "[]",
            "dirs": "[]",
            "files": "[]",
            "exts": "[]",
            "conds": f'[{{ if = "dir", text = "d", fg = "{p["directory"]}" }}, '
            f'{{ if = "!dir", text = "f", fg = "{p["ink"]}" }}]',
        },
    }
    return (
        "\n\n".join(
            f"[{section}]\n" + "\n".join(f"{key} = {value}" for key, value in entries.items())
            for section, entries in groups.items()
        )
        + "\n"
    )


RENDERERS: dict[str, Renderer] = {
    "ghostty": ghostty,
    "starship": starship,
    "vim": vim,
    "textmate": textmate,
    "delta": delta,
    "git": git_colors,
    "nano": nano,
    "fzf": fzf,
    "tmux": tmux,
    "eza": eza,
    "glow": glow,
    "lazygit": lazygit,
    "yazi": yazi,
}


def render(design: Design) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    for port, renderer in RENDERERS.items():
        extension = PORTS[port][1]
        for mode, palette in design.colors.items():
            path = f"ports/{port}/maesglas-{mode}.{extension}"
            outputs[path] = renderer(palette, mode, design.ansi, design).encode()
            if port == "yazi":
                flavor = f"maesglas-{mode}"
                outputs[path] = (f'[flavor]\ndark = "{flavor}"\nlight = "{flavor}"\n').encode()
                outputs[f"ports/yazi/{flavor}.yazi/flavor.toml"] = renderer(
                    palette, mode, design.ansi, design
                ).encode()
                outputs[f"ports/yazi/{flavor}.yazi/tmtheme.xml"] = textmate(
                    palette, mode, design.ansi, design
                ).encode()
    return outputs | extra_ports.render(design)

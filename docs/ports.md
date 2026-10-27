# Port notes

Every shipped port is generated. The gate runs native parsers,
renderers, published schemas, or documented key checks in disposable
configuration and cache directories. The method column is the boundary:
a schema check does not establish application import or rendering.

Rex's Settings import was checked manually, outside the gate.
[checked: Rex Beta 0.1.0 (1408), 2026-10-26]

## Tested scope

| Port | Validation method | Version and date |
| --- | --- | --- |
| Ghostty | `+validate-config` on both complete files; macOS only | [checked: Ghostty 1.3.1, 2026-10-24] |
| Rex | Settings import of both Ghostty port files; names, appearance, and all 21 colors read back from the stored theme | [checked: Rex Beta 0.1.0 (1408), 2026-10-26] |
| Starship | `print-config` and prompt rendering in a synthetic repository | [checked: Starship 1.27.0, 2026-10-24] |
| Vim | Headless load and highlight query | [checked: Vim 9.1, 2026-10-24] |
| bat and delta | Theme cache build, named-theme listing, and syntax rendering | [checked: bat 0.26.1 and delta 0.20.1, 2026-10-24] |
| delta | Named-feature diff rendering using the generated syntax theme | [checked: delta 0.20.1, 2026-10-24] |
| Git | Parse every color with `config --get-color` | [checked: Git 2.56.0, 2026-10-24] |
| nano | PTY startup for all ten named syntaxes | [checked: nano 9.2, 2026-10-24] |
| fzf | Native picker startup with generated color options | [checked: fzf 0.74.5, 2026-10-24] |
| tmux | Independent server, source file, and option queries | [checked: tmux 3.8, 2026-10-24] |
| eza | Classified fixture listing with the generated theme | [checked: eza 0.23.5, 2026-10-24] |
| glow | Markdown and code rendering through the style loader | [checked: glow 3.0.0, 2026-10-24] |
| lazygit | PTY startup in a disposable repository | [checked: lazygit 0.66.2, 2026-10-24] |
| yazi | PTY startup with isolated configuration | [checked: yazi 26.9.1, 2026-10-24] |
| Alacritty | Native `migrate --dry-run` TOML loader | [checked: Alacritty 0.17.0, 2026-10-24] |
| kitty | Native `+runpy` and `kitty.config.load_config`; every color queried | [checked: kitty 0.49.2, 2026-10-24] |
| WezTerm | Native `show-keys` with `color.load_scheme` and exact Lua assertions | [checked: WezTerm 20240203-110809-5046fc22, 2026-10-24] |
| Neovim | `--headless` colorscheme load; every authored highlight and ANSI slot queried | [checked: Neovim 0.12.6, 2026-10-24] |
| Helix | Published theme keys and native PTY theme loading | [checked: Helix 25.07.1, 2026-10-24] |
| VS Code | Official color-theme schema evaluated from pinned source, plus color registry | [checked: VS Code 1.143.1, 2026-10-24] |
| Zed | Published theme schema 0.2.0; unknown properties rejected | [checked: Zed schema 0.2.0, 2026-10-24] |
| iTerm2 | `plutil -lint`, upstream preset keys, and exact sRGB round-trip | [checked: iTerm2 3.6.6, 2026-10-24] |
| Windows Terminal | Microsoft settings schema, with the scheme in `schemes` | [checked: Windows Terminal 1.25.2733.0, 2026-10-24] |
| k9s | Upstream `NewStyles().Load` parser and embedded schema; all colors queried | [checked: k9s 0.51.0, 2026-10-24] |
| gh-dash | Upstream `ParseConfig` and theme initialization; all theme fields queried | [checked: gh-dash 4.26.0, 2026-10-24] |
| fast-syntax-highlighting | Pinned plugin loaded in isolated Zsh; active and recursive styles | [checked: fast-syntax-highlighting 1.67, 2026-10-24] |

## Additional port installation

For copy examples, choose the application-specific destination as `THEME_DIR`.
Each has one preparation line and one copy line. Substitute `shale` for
`chalk`, except that the editor extension includes both variants.

<details>
<summary>Rex</summary>

Rex reuses the Ghostty files unchanged. Import
`ports/ghostty/maesglas-chalk.conf` and
`ports/ghostty/maesglas-shale.conf` through **Settings > Themes > Import Theme**.
Chalk appears under **Light Mode** and Shale under **Dark Mode**.
[checked: Rex Beta 0.1.0 (1408), 2026-10-26]

Rename the numbered "Imported Theme" entries `Maesglas Chalk` and
`Maesglas Shale` in **Settings > Themes**, and select each in its mode's row
if needed. With **Interface > Color scheme** on **Auto**, Rex follows macOS.
[checked: Rex Beta 0.1.0 (1408), 2026-10-26]

</details>

<details>
<summary>Alacritty</summary>

Import the file from `[general].import`. [checked: Alacritty 0.17.0, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/alacritty/maesglas-chalk.toml "$THEME_DIR/maesglas-chalk.toml"
```

</details>

<details>
<summary>kitty</summary>

Include the file from your configuration. [checked: kitty 0.49.2, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/kitty/maesglas-chalk.conf "$THEME_DIR/maesglas-chalk.conf"
```

</details>

<details>
<summary>WezTerm</summary>

Put the file in `colors/`; select `Maesglas Chalk`. [checked: WezTerm 20240203-110809-5046fc22, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/wezterm/maesglas-chalk.toml "$THEME_DIR/maesglas-chalk.toml"
```

</details>

<details>
<summary>Neovim</summary>

Put the file in `colors/`; run `:colorscheme maesglas-chalk`. [checked: Neovim 0.12.6, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/neovim/maesglas-chalk.lua "$THEME_DIR/maesglas-chalk.lua"
```

</details>

<details>
<summary>Helix</summary>

Put the file in `themes/`; select `maesglas-chalk`. [checked: Helix 25.07.1, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/helix/maesglas-chalk.toml "$THEME_DIR/maesglas-chalk.toml"
```

</details>

<details>
<summary>VS Code</summary>

Copy the extension folder, then select Maesglas Chalk. [checked: VS Code 1.143.1, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose an extensions directory}/maesglas"
cp ports/vscode/*.json ports/vscode/LICENSE "$THEME_DIR/maesglas/"
```

</details>

<details>
<summary>Zed</summary>

Put the file in `themes/`, then select Maesglas Chalk. [checked: Zed schema 0.2.0, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/zed/maesglas-chalk.json "$THEME_DIR/maesglas-chalk.json"
```

</details>

<details>
<summary>iTerm2</summary>

Import the file through the profile's color presets. [checked: iTerm2 3.6.6, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/iterm2/maesglas-chalk.itermcolors "$THEME_DIR/maesglas-chalk.itermcolors"
```

</details>

<details>
<summary>Windows Terminal</summary>

Add the object to `schemes`; select `Maesglas Chalk`. [checked: Windows Terminal 1.25.2733.0, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/windows-terminal/maesglas-chalk.json "$THEME_DIR/maesglas-chalk.json"
```

</details>

<details>
<summary>k9s</summary>

Put the file in `skins/`; set `k9s.ui.skin: maesglas-chalk`. [checked: k9s 0.51.0, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/k9s/maesglas-chalk.yaml "$THEME_DIR/maesglas-chalk.yaml"
```

</details>

<details>
<summary>gh-dash</summary>

Merge the `theme` mapping into your configuration. [checked: gh-dash 4.26.0, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/gh-dash/maesglas-chalk.yml "$THEME_DIR/maesglas-chalk.yml"
```

</details>

<details>
<summary>fast-syntax-highlighting</summary>

Source the file after loading the plugin. [checked: fast-syntax-highlighting 1.67, 2026-10-24]

```sh
mkdir -p "${THEME_DIR:?Choose a destination directory}"
cp ports/fast-syntax-highlighting/maesglas-chalk.zsh "$THEME_DIR/maesglas-chalk.zsh"
```

</details>

## Cache and feature composition

Place the TextMate files in the `themes` directory below `BAT_CONFIG_DIR`.
Run `bat cache --build`, then select `maesglas-chalk` or `maesglas-shale`
through `BAT_THEME`. A rebuilt cache is required after a palette change.
[checked: bat 0.26.1 and delta 0.20.1, 2026-10-24]

Use the same XDG cache root for both tools. Delta reads
`XDG_CACHE_HOME/bat`, not a custom `BAT_CACHE_PATH`. Build the cache
there when composing the tools. [checked: bat 0.26.1 and delta 0.20.1, 2026-10-24]

Include the delta file from your Git configuration. Add `maesglas-chalk`
to the existing feature list rather than replacing it. Keep behavior
features separate from color features. [checked: delta 0.20.1, 2026-10-24]

```gitconfig
[delta]
    features = review maesglas-chalk
[delta "review"]
    side-by-side = true
[delta "interactive"]
    features = maesglas-chalk
    color-only = true
    side-by-side = false
    line-numbers = false
```

Interactive patch output must retain its patch structure. The palette
does not install a pager, rewrite `interactive.diffFilter`, or turn on
side-by-side output by itself. [checked: delta 0.20.1, 2026-10-24]

The nano port uses terminal slots and default backgrounds. The selected
range is bold rather than inverted onto an ink-colored ANSI background.
Search uses bold bronze. All ten syntaxes are small regular-expression
rules, not language parsers. [checked: nano 9.2, 2026-10-24]

The fzf fragment leaves color alone under `NO_COLOR`, `TERM=dumb`, or
redirected output. Source it in the interactive shell after other options.
[checked: fzf 0.74.5, 2026-10-24]

The glow port renders code blocks in plain ink. Its embedded syntax
formatter reduces colors to the fixed 256-color cube, and the CLI
does not expose the formatter override. Plain code avoids a second,
uncontrolled palette. [checked: glow 3.0.0, 2026-10-24]

The Yazi file clears the default colored icon tables. File kinds use
letters, paths, and permission text instead of private-use glyphs.
Its flavor includes the matching syntax theme. Copy the complete
flavor directory, not just the selection file. [checked: yazi 26.9.1, 2026-10-24]

## Rulings and limitations

LEG-01: the editor extension emits `editor.findMatchForeground` and
`editor.findMatchHighlightForeground` as ink. Its `match` and
`match-active` grounds are lighter than the original search grounds.
The gate audits every emitted syntax foreground on both actual match
fills, not only the replacement ink. [checked: VS Code 1.143.1, 2026-10-24]

FG-CLAUDE-LIGHTBASE was evaluated against all six installed base
registries and all 72 accepted color tokens.
A fully overridden candidate fixes every configurable foreground,
including the misleadingly named `background` accent and the two
word-diff tokens used for `+N` and `-N` counters. The same word tokens
also paint inline backgrounds; inline word text inherits the normal
text role, with no independent foreground override. Making the counters
readable therefore makes word-diff text unreadable, so this format is omitted.
[checked: Claude Code 2.1.311, 2026-10-26]

Claude Code compatibility is a factual product statement, not an
endorsement: Maesglas is independent of Anthropic. The format also
cannot replace `dimColor` or `faint` attributes, literal syntax-formatter
colors, or external-tool output. The check inspected the installed
renderer without starting an authenticated session.
[checked: Claude Code 2.1.311, 2026-10-26]

| Shared-token bound | Chalk | Shale |
| --- | ---: | ---: |
| Best possible simultaneous counter/word contrast | 3.845:1 | 4.100:1 |

The bound is the square root of ink/canvas contrast: a shared color
must contrast with the canvas as foreground and with ink as background.
Both maxima are below 4.5:1. The gate reproduces this blocker instead
of exempting either failing pair. Its inputs and measured candidate
pairs are in `identity/port-validation.json`.
[checked: Claude Code 2.1.311, 2026-10-26]

FG-K9S-TRUECOLOR: every native skin color, including chart arrays,
resource maps, help, prompt borders, and logo messages, is palette hex.
The parsed skin retains these hex values throughout. The YAML files
use JSON syntax, a YAML-compatible representation. [checked: k9s 0.51.0, 2026-10-24]

FG-GHDASH-KEYS uses the actual 4.26 parser fields: `text.actor`,
`background.selected`, the three border fields, and the six author
association icon fields. FG-GHDASH-INVERTED assigns ink to `inverted`;
COV-05 assigns the warning slot to `warning`, not the number or error
slot. Both parsed values and initialized theme colors are queried.
[checked: gh-dash 4.26.0, 2026-10-24]

FG-GHDASH-ICONS: issue and pull-request state icons, the merged glyph,
the logo, and API-supplied label colors are not configurable through
the theme. The parser accepts `icon.unknownrole`, but theme initialization
leaves that color at fixed index 178. These upstream colors are not
Maesglas colors, and several fail 4.5:1. The port does not make the
entire application contrast-compliant. [checked: gh-dash 4.26.0, 2026-10-24]

COV-01: the shell theme replaces the complete style registry after
the plugin loads. Primary, default, and recursive namespaces use
semantic ANSI foregrounds; there are no fixed xterm-256 indices,
ANSI-background inversions, or unthemed secondary themes. Use the
matching terminal variant. [checked: fast-syntax-highlighting 1.67, 2026-10-24]

## Omitted formats

Omitted formats have no shipped draft files and make no compatibility claims.

| Format | Reason |
| --- | --- |
| btop | Its native banner uses foreground colors that the theme cannot replace. Observed `#787878` reaches 4.007:1 on Chalk and 4.168:1 on Shale. The input and source are in `identity/rejections.json`. [checked: btop 1.4.7, 2026-10-24] |
| Claude Code | Counter foregrounds and word-diff backgrounds share tokens; the format cannot override word-diff text independently. Shared colors cannot meet both 4.5:1 pairs with the Maesglas canvas and ink. The installed-registry digest and proof are in `identity/port-validation.json`. [checked: Claude Code 2.1.311, 2026-10-26] |
| Terminal.app | Archived-color profile import was not verified. [unchecked] |
| Sublime Text | The TextMate file was not loaded in this application. [unchecked] |

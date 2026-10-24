# Typography

Commit Mono supplies the lettering. Its 600-unit advance on a 1000-unit
em gives a predictable cell width; the regular and bold files are real
400 and 700 outlines. [checked: Commit Mono 1.143, 2026-10-24]

Use upright regular text for comments, paths, and branch names. Reserve
bold for focus, headings, and urgent state. Programming ligatures are off
so the characters you read are the characters you copy.

## Install the face

Download the [1.143 archive](https://github.com/eigilnikolajsen/commit-mono/releases/download/v1.143/CommitMono-1.143.zip),
verify its SHA-256 below, and install its regular, italic, bold, and
bold italic files with your operating system's font installer.
The family name in the files is `CommitMono`.
[checked: Commit Mono 1.143, 2026-10-24]

```text
f7d1f26a7c7554800a996f76f5d706bf0648b936ca2a66b5bc4d46e3a2c49ed0
```

The page uses only upright regular and bold. Its local copies and the
shaped outline cache are covered by [the font notice](THIRD_PARTY_NOTICES.md).
Font installation is a separate, explicit step.

## Size the pane, not the display

The default is 15 pt with 12 pt horizontal padding on each side of
each pane. Fit the content in logical display points, not physical pixels:

```text
panes * (columns * size * advance + 2 * padding) <= display width
2 * (80 * 15 * 0.6 + 2 * 12) = 1488 pt
```

| Display width in points | Two 80-column panes | Recommendation |
| ---: | ---: | --- |
| 1280 | Up to 12.83 pt | Use one pane at 15 pt |
| 1440 | Up to 14.50 pt | Use one pane at 15 pt |
| 1512 | Up to 15.25 pt | 15 pt; zoom for single-pane reading |
| 1728 | Up to 17.50 pt | 15 pt; zoom for single-pane reading |
| 1920 | Up to 19.50 pt | 15 pt; zoom for single-pane reading |

Two panes at 18 pt need 1776 pt. Shrinking below the default to fit
another pane is not the recommended layout.

## Checked terminal settings

The Ghostty port sets 15 pt, 12 pt padding, 6% extra cell height,
no synthetic styles, and contextual spacing with `calt=1`.
The `ss01=0`, `ss02=0`, `liga=0`, and `dlig=0` settings preserve
the default letterforms without programming ligatures.
It binds `Super+Shift+Enter` to split zoom. This enlarges the active pane,
not the font. On macOS, the text-size defaults are `Command+=` or
`Command++` to increase, `Command+-` to decrease, and `Command+0`
to reset the active surface. Enlarge the reading pane, then reset
its text size before returning to two panes.
[checked: Ghostty 1.3.1, 2026-10-24]

The terminal supplies the face to nano, Vim, and the command-line ports.
They do not install or choose a second face.
[checked: nano 9.2 and Vim 9.1, 2026-10-24]

## Unverified application settings

These font settings are starting points, separate from the validated
color ports. Each needs a native font and layout check before adoption.

| Application | Intended setting | Status |
| --- | --- | --- |
| iTerm2 | Text: CommitMono Regular 15; disable ligatures | [unchecked] |
| Terminal.app | Profile font: CommitMono Regular 15 | [unchecked] |
| Alacritty | `font.normal.family = "CommitMono"`; `font.size = 15` | [unchecked] |
| kitty | `font_family CommitMono`; `font_size 15`; `disable_ligatures always` | [unchecked] |
| WezTerm | `font = wezterm.font("CommitMono")`; `font_size = 15` | [unchecked] |
| Windows Terminal | `font.face: "CommitMono"`; `font.size: 15` | [unchecked] |
| VS Code | `editor.fontFamily: "CommitMono"`; size 16; line height 26; ligatures off | [unchecked] |
| Zed | `buffer_font_family: "CommitMono"`; size 16; ligatures off | [unchecked] |
| Helix and Neovim | Use the terminal's face and cell geometry | [unchecked] |

## Measured macOS reference

CoreText measures the settled 15 pt face as 9-point cells with an
8.1-point x-height. The reference specimen therefore uses 15 CSS px:
9 CSS px cells and an 8.1 CSS px x-height on the Mac, where logical
points and CSS px agree. A 20 CSS px drawing would have 12 CSS px
cells, one-third larger; it is not the macOS terminal reference.
[checked: Commit Mono 1.143, CoreText on macOS, 2026-10-24]

Browser CSS points use a different unit conversion. Other applications
and platforms require their own measurement; there is no universal
integrated-terminal pixel target. Verify `0O`, `1lI`, quotes, braces,
and arrow punctuation with the delivered font.

The site, native font-feature settings, and shaped outlines use
`calt=1`, `ss01=0`, `ss02=0`, `liga=0`, and `dlig=0`.
The outline extractor shapes complete lines before applying syntax
colors, so contextual spacing also crosses color boundaries.
Every shaped glyph retains its 600-unit advance and every character
retains its own glyph; no programming ligatures are introduced.
[checked: Commit Mono 1.143 and uharfbuzz 0.57.0, 2026-10-24]

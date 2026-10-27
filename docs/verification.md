# Verification

Native results are recorded with their input digests in
`identity/validation.json`. The gate rejects a changed input, tool pin,
or validator until the corresponding platform is checked again.

| Platform | Date | Port and variant cases |
| --- | --- | ---: |
| Darwin | 2026-10-24 | 26 |
| Linux | 2026-10-24 | 24 |

Additional native and schema evidence is recorded separately in
`identity/port-validation.json`; the original cross-platform native
record remains intact. Both records are required by the gate.

| Additional checks | Date | Port and variant cases |
| --- | --- | ---: |
| Darwin | 2026-10-27 | 24 |

```sh
python3 scripts/bootstrap_ports.py
python3 scripts/validate_ports.py --record
python3 scripts/validate_extended.py --record
python3 scripts/generate.py
scripts/gate.sh
```

The original record covers native loading and exact emitted colors on
the exercised paths. Editor syntax checks cover all ten declared syntaxes.
The file-manager check
answers the terminal's background-color query from the selected palette.

## Additional validation boundary

Each download's URL, version, and SHA-256 is in `tools.lock`.
The bootstrap verifies every cached source before extraction and builds
the two Go probes against upstream parsers and their locked modules.
Go caches, application state, temporary files, and browser captures
stay below `.cache/`. No application window is opened or theme installed.

Alacritty uses its migration command's native TOML parser, not a window.
kitty queries every configured color through its embedded Python loader.
WezTerm loads the TOML scheme with `color.load_scheme` and asserts every
color before `show-keys`. Neovim loads both Lua colorschemes headlessly
and queries all authored highlights and terminal slots; any inherited
highlight color outside the palette fails. Helix loads
each theme in a PTY and checks published keys. These six macOS-specific
checks, including the profile lint, are bound to the Darwin record;
Linux reruns portable checks and verifies that record, not foreign binaries.
[checked: Alacritty 0.17.0, kitty 0.49.2, WezTerm 20240203-110809-5046fc22, Neovim 0.12.6, Helix 25.07.1, and iTerm2 key set 3.6.6, 2026-10-24]

VS Code has no supported standalone GUI-theme importer for this check.
The validator evaluates its published TypeScript color-theme and semantic
token schemas with localization stubbed, then checks the official source
color registry. Zed uses its published theme schema; unknown properties
also fail. Windows Terminal uses the scheme definition from Microsoft's
settings schema. iTerm2 uses `plutil -lint`, upstream preset keys, and
exact sRGB round-trips. These are format checks, not profile import or
application rendering evidence.
[checked: VS Code 1.143.1, Zed schema 0.2.0, Windows Terminal 1.25.2733.0, and iTerm2 key set 3.6.6, 2026-10-24]

Claude Code exposes no standalone custom-theme validator. Its documented
format and all six installed registries were checked; all 72 tokens
were overridden in an in-memory candidate. The installed binary digest
and shared-token rejection are recorded without a personal path.
`diffAddedWord` and `diffRemovedWord` serve both counter foregrounds
and inline backgrounds, but the format has no separate word-text color.
The maximum simultaneous contrast is 3.845:1 in Chalk and 4.100:1 in
Shale. Both fail 4.5:1; no candidate file is shipped or exempted.
The original live documentation URL and digest remain historical
references in `tools.lock`; its mutable page is not a CI dependency.
The rejection gate checks the recorded registry keys and recomputes the
shared-token proof, not a fresh documentation fetch. Only a recording
reads the installed registry, so a Claude Code update needs a deliberate
recheck.
No authenticated session, transcript, external syntax formatter, or
dimmed rendering path is certified.
[checked: Claude Code 2.1.311, 2026-10-26]

The k9s probe calls `NewStyles().Load`, including its embedded schema,
and compares every parsed skin field. The gh-dash probe calls
`ParseConfig` and `ParseTheme`, compares every accepted theme key, and
queries light and dark adaptive values. Neither check contacts a cluster
or account. Fixed status icons remain documented upstream limitations,
not contrast exemptions for authored colors. [checked: k9s 0.51.0, 2026-10-24] [checked: gh-dash 4.26.0, 2026-10-24]

The shell check loads the pinned fast-syntax-highlighting plugin with
a temporary `ZDOTDIR` and private working directory. It precreates the
secondary-theme cache to prevent the plugin's automatic network fetch,
loads each generated theme, exercises nested substitution and arithmetic,
and rejects fixed indexed colors in all style namespaces and regions.
[checked: fast-syntax-highlighting 1.67, 2026-10-24]

Application windows, plug-ins, monitor calibration, and assistive
technology are not certified by these checks. The specimens are drawings,
not evidence of a complete application session.

Browser checks cover saved choice, system preference, keyboard help,
shortcut opt-out, typing guards, focus return, storage failure, local
requests, and all fourteen plates at their full dimensions. Both variants
are exercised at 390x844 and 1512x982 in Chromium. The phone opening
must show specimen glyphs before the fold; the laptop opening must show
the whole specimen. Measured positions and screenshots stay in
`.cache/visual`. Guidance links retain theme, Markdown links are explicit
downloads, and clicking the font link downloads the digest-pinned archive.

The macOS reference metrics were reproduced with
`scripts/probes/font_metrics.swift`: CoreText reports 15 pt, 9-point
cells, and an 8.1-point x-height. The outline check shapes full lines
with the authored features, checks 600-unit advances and one glyph per
character, and retains context across syntax colors.
Browser canvas measurements allow less than 1/1024 CSS px of platform
rounding around the 9 CSS px cell; outline advances remain exact.
[checked: Commit Mono 1.143, CoreText on macOS, and uharfbuzz 0.57.0, 2026-10-24]

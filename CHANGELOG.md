# Changelog

Maesglas uses calendar versions: year, month, and a monthly counter starting at
zero. Release headings use the Keep a Changelog structure.

## [Unreleased]

## [2026.10.1] - 2026-10-24

### Security

- Security updates to build-only dependencies. The ports, palette, specimen
  outlines, and generated downloads are unchanged.
- Report vulnerabilities privately through GitHub's private vulnerability
  reporting, as `SECURITY.md` now says.

### Fixed

- The specimen site now publishes to GitHub Pages; the deployment for 2026.10.0
  stopped before it was published.

## [2026.10.0] - 2026-10-24

### Added

- Chalk and Shale, with audited text, surface, and boundary colors.
- Generated appearance ports, outlined specimens, and a static specimen page.
- A dependency-free generator and a gate for reproducibility and contrast.
- Generated Alacritty, kitty, and WezTerm color schemes, checked with native
  headless parsers. [checked: Alacritty 0.17.0, kitty 0.49.2, and WezTerm
  20240203-110809-5046fc22, 2026-10-24]
- Neovim Lua colorschemes with headless highlight assertions, and Helix themes
  with native loading and published-key checks. [checked: Neovim 0.12.6 and
  Helix 25.07.1, 2026-10-24]
- A local VS Code extension containing both variants, Zed themes, iTerm2 color
  presets, and Windows Terminal schemes, checked against schemas or upstream
  keys. [checked: VS Code 1.143.1, Zed schema 0.2.0, iTerm2 key set 3.6.6, and
  Windows Terminal 1.25.2733.0, 2026-10-24]
- A recorded Claude Code contrast blocker: counter text and word-diff fills
  share tokens, without an independent word-text override. No failing theme is
  shipped. [checked: Claude Code 2.1.310, 2026-10-24]
- k9s skins and gh-dash themes with upstream parser probes and explicit fixed
  icon limitations. [checked: k9s 0.51.0 and gh-dash 4.26.0, 2026-10-24]
- fast-syntax-highlighting themes with semantic ANSI colors in primary and
  recursive highlighting. [checked: fast-syntax-highlighting 1.67, 2026-10-24]
- Lighter editor match fills, explicit match foregrounds, and syntax contrast
  checks on the delivered fills.
- A GitHub Pages deployment gated by validation, with a short hosting and
  privacy notice.

### Fixed

- DCO guidance now requires contributors' own names and email addresses.
- The macOS reference specimen now uses 15 CSS px, matching the 15 pt terminal's
  9-point cells and 8.1-point x-height rather than a larger universal pixel
  conversion.
- Setup, installation, font, and contrast guidance now reads inside the
  theme-aware specimen page; Markdown remains available as source downloads.
- Keyword/type and keyword/number now join the three existing simulated
  color-vision separation checks, with revised mulberry pigments in both modes.
- The opening shows terminal content on phones and a complete specimen on laptop
  displays; content labels replace decorative selector titles.
- The ports archive now includes a starting guide, activation settings, font
  setup, and archive-relative reference links.
- Contextual spacing stays enabled in native font-feature settings, web text,
  and shaped specimen outlines without programming ligatures.
- Linux CI selects its container architecture from the pinned image index,
  verifies architecture-specific downloads, and builds native parser probes for
  the selected target.
- Browser installation uses pinned Node.js 24 LTS rather than a Node.js 26
  runtime that stalls the pinned ZIP extractor.

[Unreleased]: https://github.com/agh/maesglas/compare/v2026.10.1...HEAD
[2026.10.1]: https://github.com/agh/maesglas/releases/tag/v2026.10.1
[2026.10.0]: https://github.com/agh/maesglas/releases/tag/v2026.10.0

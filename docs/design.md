# Design

Maesglas treats the terminal as a reading surface. The light variant, Chalk,
uses cool mineral paper and green-black ink. Shale is a dark companion with the
same hierarchy, not an inversion of the light values. Chalk remains the starting
point; neither variant follows a clock.

## Material

The canvas has a slight green cast rather than a yellow one. Slate names paths
and functions. Petroleum distinguishes types and links, which are also
underlined where the format supports it. Mulberry carries branch identity and
keywords. Juniper marks additions, bronze marks attention, and oxide marks
errors and removals.

Error and warning, type and function, and keyword and function differ in
lightness as well as hue. The computed report includes full-severity
color-vision simulations for those pairs, keyword/type, and keyword/number.
State still has a name or a sign: a diff keeps `+` and `-`, an error keeps its
message, and a branch keeps its text.

Selection, search, and changed words have their own light or dark grounds. Every
syntax color is tested on every one of them. A port may replace selected text
with the main ink, but passing contrast never depends on that replacement.

## The ANSI decision

All sixteen slots are readable foregrounds. Slot 0 is not paper. Slots 7 and 15
are not literal white in Chalk. The bright accent bank repeats the normal accent
bank, so bold does not quietly become a second palette.

This contract cannot make arbitrary ANSI foreground/background pairs readable: a
color on itself has 1:1 contrast. Ports use explicit surface roles or terminal
defaults for backgrounds instead. Applications that hard-code colors outside
this contract are not covered by the palette's contrast result.

Shell syntax highlighting must use the semantic ANSI slots, not fixed 256-color
indices. A missing highlighter port is not permission to introduce a second
palette.

## Prompt and type

The prompt uses two lines. The first names the directory and, when present, the
branch and outstanding state. The second returns the width to the command. Clean
state has no badge; failure retains its exit code. There is no local machine
name, right-aligned dashboard, or runtime logo.

Default terminal type is 15 pt with 12 pt horizontal padding. Comments are
upright, opaque text. Ligatures, synthetic weight, and ornamental italics do not
belong in code. The typography guide gives the pane arithmetic rather than
assuming every display can fit two panes.

The macOS reference drawing uses 15 CSS px: the settled 15 pt face has 9-point
cells and an 8.1-point x-height in CoreText, matching 9 CSS px cells and an 8.1
CSS px x-height on the Mac. This is a measured platform reference, not a
universal point-to-pixel conversion. Contextual spacing stays enabled with
`calt=1`; `ss01`, `ss02`, `liga`, and `dlig` stay off.

## Identity

The mark is an open M with two upright sides and a descending central fold. Its
silhouette, not its color, identifies the project. The large drawing has a
64-unit grid and an 8-unit stroke. The small drawing has whole-pixel coordinates
and a 2-pixel stroke. Diagonals and end cuts are 45 degrees. Use at least one
stroke of clear space outside the drawing.

`identity/maesglas.json` includes explicit palette modes, font assets, spacing,
type scale, measure, motion, marks, and social artwork. Its upstream release and
digest are null until a release exists. That absence is a publication blocker,
not an invented pin.

## Motion and choice

The cursor is a steady bar, so it needs no inverse text role. There is no
shader, transparency, blurred background, or dimmed neighboring pane. The page
has no animated entrance. Reduced-motion settings remain respected if
transitions are added later.

On the page, saved choice wins over system preference, which wins over Chalk.
Theme choice is applied before styles load. The help dialog lists the single
shortcut registry, and single-key shortcuts can be disabled. Typing, modifiers,
composition, and key repeat never activate them.

## Validation boundary

The specimens are original, synthetic drawings with outlined glyphs. They are
not screenshots or recordings, and they contain no actual session material. They
show typography and role relationships, not proof that a particular application
renders an identical interface.

WCAG and APCA calculations use delivered sRGB values. They do not measure a
monitor, antialiasing, ambient light, or a person's vision. Native port checks
establish loading and the exercised rendering path. They do not cover every
third-party extension.

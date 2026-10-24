# Third-party notices

## Commit Mono

The two font files are unmodified files from Commit Mono 1.143, released under
the SIL Open Font License 1.1. Copyright belongs to the Commit Mono project
authors. The complete upstream notice is in
[`site/fonts/OFL.txt`](site/fonts/OFL.txt). [checked: Commit Mono 1.143 archive,
2026-10-24]

Source:
<https://github.com/eigilnikolajsen/commit-mono/releases/download/v1.143/CommitMono-1.143.zip>

| File                                    | SHA-256                                                            | License |
| --------------------------------------- | ------------------------------------------------------------------ | ------- |
| `site/fonts/CommitMono-400-Regular.otf` | `a0031e19949b928b6ef749775fbd229adb43f4b96a30175d3098fa1fd92e58ee` | OFL-1.1 |
| `site/fonts/CommitMono-700-Regular.otf` | `658d3920e788196d6be9c4f444bb7c305acfbe3b247a527be1424af5ddc3ee6d` | OFL-1.1 |
| `site/fonts/OFL.txt`                    | `2e2dc937707819086e7631d02e6183fbe52316a89da0a611d9b09d3be7d4bd72` | OFL-1.1 |

`identity/letterforms.json` contains derived, flattened outlines and shaped
ASCII runs from those two files. It is an internal drawing cache, not an
installable font. Curves use sixteen subdivisions. Complete lines are shaped
with `calt=1`, `ss01=0`, `ss02=0`, `liga=0`, and `dlig=0`, including context
across syntax-color boundaries. The original fonts are not renamed or modified;
specimens contain their outlines. The cache retains source file digests,
features, and glyph positions and is checked by `scripts/outline_face.py`.

## Color calculations

The OKLab D65 matrices follow <https://bottosson.github.io/posts/oklab/>. The
scalar implementation in `scripts/colors.py` is original. The published matrices
are mathematical data; no upstream software is bundled.

The APCA calculation uses the SAPC 0.0.98G-4g constants, documented at
<https://github.com/Myndex/apca-w3>. No upstream implementation is bundled.
Reference black/white results are checked in `tests/test_colors.py`.

The severity-1.0 color-vision matrices are published with Machado, Oliveira, and
Fernandes, _A Physiologically-based Model for Simulation of Color Vision
Deficiency_ (2009):
<https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html>.
Only the numeric matrices are included.

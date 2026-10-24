"""Rebuild the checked outline cache; only font maintenance needs FontTools."""

import argparse
import hashlib
import json
from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont
from model import load, mapping, number
from plates import lettering

ROOT = Path(__file__).resolve().parents[1]
type Point = tuple[float, float]


class OutlinePen(BasePen):
    def __init__(self, glyphs: object) -> None:
        super().__init__(glyphs)
        self.contours: list[list[Point]] = []
        self.current: list[Point] = []

    def _moveTo(self, point: Point) -> None:
        self.current = [point]

    def _lineTo(self, point: Point) -> None:
        self.current.append(point)

    def _curveToOne(self, a: Point, b: Point, c: Point) -> None:
        start = self.current[-1]
        for step in range(1, 17):
            t = step / 16
            u = 1 - t
            self.current.append(
                (
                    u**3 * start[0] + 3 * u * u * t * a[0] + 3 * u * t * t * b[0] + t**3 * c[0],
                    u**3 * start[1] + 3 * u * u * t * a[1] + 3 * u * t * t * b[1] + t**3 * c[1],
                )
            )

    def _closePath(self) -> None:
        self.contours.append(self.current)
        self.current = []

    def _endPath(self) -> None:
        self._closePath()


def build() -> bytes:
    faces: dict[str, object] = {}
    features = {
        key: int(number(value)) for key, value in mapping(load().leaf("fonts", "features")).items()
    }
    for weight in ("400", "700"):
        path = ROOT / f"site/fonts/CommitMono-{weight}-Regular.otf"
        hb_font = hb.Font(hb.Face(path.read_bytes()))
        with TTFont(path) as font:
            glyphs = font.getGlyphSet()
            outlines: dict[str, object] = {}
            runs: dict[str, object] = {}
            for content in sorted(lettering()[weight]):
                buffer = hb.Buffer()
                buffer.add_str(content)
                buffer.guess_segment_properties()
                hb.shape(hb_font, buffer, features)
                infos = buffer.glyph_infos
                positions = buffer.glyph_positions
                if len(infos) != len(content) or any(p.x_advance != 600 for p in positions):
                    raise ValueError("Shaping changed the fixed 600-unit cells")
                shaped: list[dict[str, object]] = []
                for info, position in zip(infos, positions, strict=True):
                    name = font.getGlyphName(info.codepoint)
                    shaped.append(
                        {
                            "glyph": name,
                            "cluster": info.cluster,
                            "x_advance": position.x_advance,
                            "y_advance": position.y_advance,
                            "x_offset": position.x_offset,
                            "y_offset": position.y_offset,
                        }
                    )
                    outlines[name] = {}
                runs[content] = shaped
            for name in outlines:
                glyph = glyphs[name]
                pen = OutlinePen(glyphs)
                glyph.draw(pen)
                outlines[name] = {
                    "advance": glyph.width,
                    "contours": [
                        [[round(x, 2), round(y, 2)] for x, y in points] for points in pen.contours
                    ],
                }
            faces[weight] = {
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "em": font["head"].unitsPerEm,
                "features": features,
                "shaper": f"uharfbuzz {hb.__version__}",
                "glyphs": outlines,
                "runs": runs,
            }
    return (json.dumps(faces, separators=(",", ":")) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    path = ROOT / "identity/letterforms.json"
    output = build()
    if args.check:
        if path.read_bytes() != output:
            raise SystemExit("Stale letterforms; run uv run scripts/outline_face.py")
        print("PASS font outlines")
    else:
        path.write_bytes(output)


if __name__ == "__main__":
    main()

"""Outline-based SVG and a small deterministic, supersampled PNG writer."""

import hashlib
import html
import math
import struct
import zlib
from dataclasses import dataclass
from functools import cache

from model import ROOT, load, load_json, mapping, number, sequence, text

type Point = tuple[float, float]
type Contours = list[list[Point]]


@dataclass(frozen=True)
class Shape:
    contours: Contours
    color: str


class Drawing:
    def __init__(self, width: int, height: int, background: str, title: str) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.shapes: list[Shape] = []
        self.rect(0, 0, width, height, background)

    def rect(self, x: float, y: float, w: float, h: float, color: str) -> None:
        self.shapes.append(Shape([[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]], color))

    def label(
        self,
        content: str,
        x: float,
        y: float,
        size: float,
        color: str,
        weight: str = "400",
        colors: list[str] | None = None,
    ) -> float:
        face = faces()[weight]
        glyphs = mapping(face["glyphs"])
        scale = size / number(face["em"])
        runs = mapping(face["runs"])
        if content not in runs:
            raise ValueError(f"Missing shaped specimen run: {content!r}; rebuild the outline cache")
        if colors is not None and len(colors) != len(content):
            raise ValueError("Every specimen character needs a color")
        for value in sequence(runs[content]):
            position = mapping(value)
            glyph = mapping(glyphs[text(position["glyph"])])
            dx = number(position["x_offset"]) * scale
            dy = number(position["y_offset"]) * scale
            contours: Contours = []
            for contour in sequence(glyph["contours"]):
                points: list[Point] = []
                for point in sequence(contour):
                    pair = sequence(point)
                    points.append(
                        (
                            x + dx + number(pair[0]) * scale,
                            y - dy - number(pair[1]) * scale,
                        )
                    )
                contours.append(points)
            fill = color if colors is None else colors[int(number(position["cluster"]))]
            self.shapes.append(Shape(contours, fill))
            x += number(position["x_advance"]) * scale
            y -= number(position["y_advance"]) * scale
        if x > self.width - 12:
            raise ValueError(f"Specimen line exceeds drawing: {content}")
        return x

    def svg(self) -> bytes:
        elements = [
            '<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}" role="img" aria-labelledby="title">',
            f'<title id="title">{html.escape(self.title)}</title>',
        ]
        for shape in self.shapes:
            paths: list[str] = []
            for contour in shape.contours:
                if contour:
                    points = " ".join(f"{x:.2f},{y:.2f}" for x, y in contour)
                    paths.append(f"M{points}Z")
            if paths:
                elements.append(
                    f'<path fill="{shape.color}" fill-rule="evenodd" d="{" ".join(paths)}"/>'
                )
        return ("\n".join(elements) + "\n</svg>\n").encode()

    def png(self) -> bytes:
        factor = 2
        width, height = self.width * factor, self.height * factor
        pixels = bytearray(width * height * 3)
        for shape in self.shapes:
            contours = [[(x * factor, y * factor) for x, y in c] for c in shape.contours]
            points = [point for contour in contours for point in contour]
            if not points:
                continue
            color = bytes.fromhex(shape.color[1:])
            first = max(0, math.floor(min(y for _, y in points)))
            last = min(height, math.ceil(max(y for _, y in points)))
            for row in range(first, last):
                scan = row + 0.5
                intersections: list[float] = []
                for contour in contours:
                    for (x1, y1), (x2, y2) in zip(contour, contour[1:] + contour[:1], strict=False):
                        if (y1 <= scan < y2) or (y2 <= scan < y1):
                            intersections.append(x1 + (scan - y1) * (x2 - x1) / (y2 - y1))
                intersections.sort()
                for left, right in zip(intersections[::2], intersections[1::2], strict=False):
                    a = max(0, math.ceil(left - 0.5))
                    b = min(width, math.ceil(right - 0.5))
                    if b > a:
                        start = (row * width + a) * 3
                        pixels[start : start + (b - a) * 3] = color * (b - a)
        rows = bytearray()
        for y in range(self.height):
            rows.append(0)
            for x in range(self.width):
                for channel in range(3):
                    total = sum(
                        pixels[((y * factor + dy) * width + x * factor + dx) * 3 + channel]
                        for dy in range(factor)
                        for dx in range(factor)
                    )
                    rows.append((total + 2) // 4)

        def chunk(kind: bytes, value: bytes) -> bytes:
            return (
                struct.pack(">I", len(value))
                + kind
                + value
                + struct.pack(">I", zlib.crc32(kind + value))
            )

        return (
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9))
            + chunk(b"IEND", b"")
        )


@cache
def faces() -> dict[str, dict[str, object]]:
    result = {
        key: mapping(value) for key, value in load_json(ROOT / "identity/letterforms.json").items()
    }
    for weight, face in result.items():
        path = ROOT / f"site/fonts/CommitMono-{weight}-Regular.otf"
        if hashlib.sha256(path.read_bytes()).hexdigest() != text(face["sha256"]):
            raise ValueError("Font and outline cache differ")
        if face["features"] != load().leaf("fonts", "features"):
            raise ValueError("Font features and shaped outline cache differ")
    return result

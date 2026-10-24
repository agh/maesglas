"""Pinned D65 color conversion and solid-color contrast calculations."""

import math

type RGB = tuple[float, float, float]

SYNTAX_PAIRS = (
    ("error", "warning"),
    ("type", "function"),
    ("keyword", "function"),
    ("keyword", "type"),
    ("keyword", "number"),
)

MACHADO: dict[str, tuple[RGB, RGB, RGB]] = {
    "protanopia": (
        (0.152286, 1.052583, -0.204868),
        (0.114503, 0.786281, 0.099216),
        (-0.003882, -0.048116, 1.051998),
    ),
    "deuteranopia": (
        (0.367322, 0.860646, -0.227968),
        (0.280085, 0.672501, 0.047413),
        (-0.011820, 0.042940, 0.968881),
    ),
    "tritanopia": (
        (1.255528, -0.076749, -0.178779),
        (-0.078411, 0.930809, 0.147602),
        (0.004733, 0.691367, 0.303900),
    ),
}


def linear(value: float) -> float:
    return value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4


def encode(value: float) -> float:
    return 12.92 * value if value <= 0.0031308 else 1.055 * value ** (1 / 2.4) - 0.055


def rgb(value: str) -> RGB:
    if len(value) != 7 or value[0] != "#":
        raise ValueError("Expected an sRGB hex triplet")
    return (int(value[1:3], 16) / 255, int(value[3:5], 16) / 255, int(value[5:7], 16) / 255)


def srgb(coordinates: list[float]) -> str:
    lightness, chroma, hue = coordinates
    if not (0 <= lightness <= 1 and 0 <= chroma <= 0.4 and 0 <= hue < 360):
        raise ValueError("Invalid OKLCH coordinates")
    a = chroma * math.cos(math.radians(hue))
    b = chroma * math.sin(math.radians(hue))
    cone_l = (lightness + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (lightness - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (lightness - 0.0894841775 * a - 1.2914855480 * b) ** 3
    channels = (
        4.0767416621 * cone_l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * cone_l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * cone_l - 0.7034186147 * m + 1.7076147010 * s,
    )
    if any(v < -0.000001 or v > 1.000001 for v in channels):
        raise ValueError(f"Out-of-gamut OKLCH color: {coordinates}")
    return "#" + "".join(f"{math.floor(encode(max(0, v)) * 255 + 0.5):02X}" for v in channels)


def wcag(text: str, ground: str) -> float:
    def y(value: str) -> float:
        return sum(
            c * linear(v) for c, v in zip((0.2126, 0.7152, 0.0722), rgb(value), strict=False)
        )

    lo, hi = sorted((y(text), y(ground)))
    return (hi + 0.05) / (lo + 0.05)


def apca(text: str, ground: str) -> float:
    def y(value: str) -> float:
        result = sum(
            c * math.pow(v, 2.4)
            for c, v in zip((0.2126729, 0.7151522, 0.0721750), rgb(value), strict=True)
        )
        return result if result > 0.022 else result + math.pow(0.022 - result, 1.414)

    t, g = y(text), y(ground)
    if abs(g - t) < 0.0005:
        return 0
    if g > t:
        raw = (g**0.56 - t**0.57) * 1.14
        return 0 if raw < 0.1 else (raw - 0.027) * 100
    raw = (g**0.65 - t**0.62) * 1.14
    return 0 if raw > -0.1 else (raw + 0.027) * 100


def oklab(channels: RGB) -> RGB:
    r, g, b = channels
    cone_l = math.cbrt(0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b)
    m = math.cbrt(0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b)
    s = math.cbrt(0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b)
    return (
        0.2104542553 * cone_l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * cone_l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * cone_l + 0.7827717662 * m - 0.8086757660 * s,
    )


def simulated_distance(first: str, second: str, condition: str) -> float:
    def simulate(color: str) -> RGB:
        channels = [linear(v) for v in rgb(color)]
        result = [
            max(0, min(1, sum(a * b for a, b in zip(row, channels, strict=False))))
            for row in MACHADO[condition]
        ]
        return oklab((result[0], result[1], result[2]))

    return math.dist(simulate(first), simulate(second)) * 100

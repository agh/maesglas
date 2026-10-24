"""Synthetic terminal plates, drawn from the same roles as the ports."""

from drawing import Drawing
from model import Design, number

type Run = tuple[str, str]
type Line = list[Run]

SCENES: dict[str, tuple[str, list[Line]]] = {
    "home": (
        "Home",
        [
            [("comment", "Home directory")],
            [],
            [("directory", "~")],
            [("ink", "> "), ("ink", "printf 'Good morning.\\n'")],
            [("ink", "Good morning.")],
            [],
            [("directory", "~")],
            [("ink", "> ")],
        ],
    ),
    "repository": (
        "Git status",
        [
            [("directory", "orchard"), ("branch", "  main")],
            [("ink", "> git status --short --branch")],
            [("branch", "## main...origin/main")],
            [],
            [("directory", "orchard"), ("branch", "  pruning"), ("warning", " +2 ~3 ?1 up2 down1")],
            [("ink", "> make check")],
            [("error", "error: one assertion failed")],
            [("comment", "Expected 12 rows; received 11.")],
            [],
            [("directory", "orchard"), ("branch", "  pruning"), ("warning", " REBASE 2/5")],
            [("error", "exit 1 "), ("ink", "> ")],
        ],
    ),
    "diff": (
        "Diff",
        [
            [("ink", "orchard / harvest.py")],
            [("comment", "Changed: preserve the last row.")],
            [],
            [("function", "@@ -12,4 +12,4 @@ def harvest(rows):")],
            [("ink", "     basket = []")],
            [("error", "-    for row in rows[:-1]:")],
            [("success", "+    for row in rows:")],
            [("ink", "         basket.extend(row.ripe())")],
            [("ink", "     return basket")],
            [],
            [("comment", "1 line added, 1 line removed")],
        ],
    ),
    "code": (
        "Python",
        [
            [("comment", "# Keep names upright. Let punctuation stay punctuation.")],
            [
                ("keyword", "from "),
                ("ink", "dataclasses "),
                ("keyword", "import "),
                ("type", "dataclass"),
            ],
            [],
            [("keyword", "@dataclass"), ("ink", "(frozen="), ("number", "True"), ("ink", ")")],
            [("keyword", "class "), ("type", "Plot"), ("ink", ":")],
            [("ink", "    name: "), ("type", "str")],
            [("ink", "    rows: "), ("type", "int"), ("ink", " = "), ("number", "12")],
            [],
            [
                ("keyword", "def "),
                ("function", "harvest"),
                ("ink", "(plot: "),
                ("type", "Plot"),
                ("ink", ") -> "),
                ("type", "str"),
                ("ink", ":"),
            ],
            [("ink", "    label = "), ("string", 'f"{plot.name}: {plot.rows} rows"')],
            [("keyword", "    return "), ("ink", "label")],
            [],
            [("comment", "# 0O 1lI  {} [] ()  != <= ->  'single' \"double\"")],
        ],
    ),
    "directory": (
        "Directory",
        [
            [("directory", "orchard"), ("branch", "  main")],
            [("ink", "> eza --long --classify=always --icons=never")],
            [],
            [("comment", "drwxr-xr-x   "), ("directory", "design/")],
            [("comment", "drwxr-xr-x   "), ("directory", "src/")],
            [("comment", "drwxr-xr-x   "), ("directory", "tests/")],
            [("comment", ".rw-r--r--   "), ("ink", "README.md")],
            [("comment", ".rwxr-xr-x   "), ("success", "check*")],
            [("comment", "lrwxr-xr-x   "), ("link", "current@ -> releases/")],
            [],
            [("comment", "Kinds: / directory, * executable, @ symbolic link")],
        ],
    ),
    "nano": (
        "nano",
        [
            [("ink", "nano                       harvest.py                      Modified")],
            [],
            [
                ("line-number", " 1  "),
                ("keyword", "def "),
                ("function", "harvest"),
                ("ink", "(rows):"),
            ],
            [("line-number", " 2  "), ("ink", "    basket = []")],
            [
                ("line-number", " 3  "),
                ("keyword", "    for "),
                ("ink", "row "),
                ("keyword", "in "),
                ("ink", "rows:"),
            ],
            [("line-number", " 4  "), ("ink", "        basket.extend(row.ripe())")],
            [("line-number", " 5  "), ("keyword", "    return "), ("ink", "basket")],
            [],
            [("comment", "Line 3, column 5")],
            [],
            [
                ("function", "^G "),
                ("ink", "Help     "),
                ("function", "^O "),
                ("ink", "Write Out    "),
                ("function", "^F "),
                ("ink", "Where Is    "),
                ("function", "^K "),
                ("ink", "Cut"),
            ],
            [
                ("function", "^X "),
                ("ink", "Exit     "),
                ("function", "^R "),
                ("ink", "Read File    "),
                ("function", "^\\ "),
                ("ink", "Replace     "),
                ("function", "^U "),
                ("ink", "Paste"),
            ],
        ],
    ),
    "review": (
        "Review",
        [
            [("ink", "> Check the last row of the harvest.")],
            [],
            [("branch", "Review")],
            [("ink", "The slice stops before the final row. Removing its upper")],
            [("ink", "bound keeps every row in the iteration.")],
            [],
            [("comment", "harvest.py")],
            [("error", "-    for row in rows[:-1]:")],
            [("success", "+    for row in rows:")],
            [],
            [("success", "Check passed: 12 rows retained.")],
            [("warning", "Waiting for review. No files have been published.")],
            [],
            [("comment", "Context 18%  |  orchard  |  "), ("branch", "pruning")],
        ],
    ),
}

BANNER_LABELS = (
    ("Maesglas", 64, 166, 96, "ink", "700"),
    ("A terminal in mineral and ink.", 68, 232, 24, "ink", "400"),
    ("Chalk / Shale", 68, 304, 20, "comment", "400"),
    ("orchard", 68, 456, 24, "directory", "400"),
    ("main", 198, 456, 24, "branch", "400"),
    ("> make something clear", 68, 496, 24, "ink", "400"),
    ("MIT / 2026", 68, 588, 18, "comment", "400"),
    ("maesglas", 972, 108, 20, "ink", "700"),
)
SWATCH_ROLES = ("ink", "slate", "petroleum", "mulberry", "juniper", "bronze", "oxide")


def lettering() -> dict[str, set[str]]:
    runs: dict[str, set[str]] = {"400": set(SWATCH_ROLES), "700": set()}
    for _, lines in SCENES.values():
        runs["400"].update("".join(content for _, content in line) for line in lines if line)
    for content, _, _, _, _, weight in BANNER_LABELS:
        runs[weight].add(content)
    return runs


def dimensions(design: Design, scene: str) -> tuple[int, int]:
    size = number(design.leaf("fonts", "terminal-web"))
    inset = number(design.leaf("components", "plate-inset"))
    leading = number(design.leaf("components", "plate-leading"))
    width = int(number(design.leaf("components", "plate-width")))
    return width, max(360, int(2 * inset + len(SCENES[scene][1]) * size * leading))


def plain(scene: str) -> str:
    return "\n".join("".join(content for _, content in line) for line in SCENES[scene][1])


def mark(small: bool = False) -> bytes:
    if small:
        size, stroke = 16, 2
        cut = "M1 1H15V14L12 11H4L1 14Z"
        line = "M3 13V4L8 9L13 4V13"
    else:
        size, stroke = 64, 8
        cut = "M6 6H58V54L46 42H18L6 54Z"
        line = "M12 50V14L32 34L52 14V50"
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" '
        f'width="{size}" height="{size}" role="img" aria-label="Maesglas">'
        f'<defs><clipPath id="cut"><path d="{cut}"/></clipPath></defs>'
        f'<path d="{line}" fill="none" stroke="currentColor" stroke-width="{stroke}" '
        'stroke-linecap="butt" stroke-linejoin="bevel" clip-path="url(#cut)"/></svg>\n'
    ).encode()


def render(design: Design) -> dict[str, bytes]:
    outputs: dict[str, bytes] = {}
    size = number(design.leaf("fonts", "terminal-web"))
    inset = number(design.leaf("components", "plate-inset"))
    leading = number(design.leaf("components", "plate-leading"))
    for mode, p in design.colors.items():
        for scene, (title, lines) in SCENES.items():
            width, height = dimensions(design, scene)
            plate = Drawing(width, height, p["canvas"], f"Maesglas {mode.title()}: {title}")
            for index, line in enumerate(lines):
                y = inset + size + index * size * leading
                if scene in ("diff", "review") and line:
                    first = line[0][1]
                    if first.startswith(("+", "-")):
                        ground = "added" if first.startswith("+") else "removed"
                        plate.rect(24, y - size, width - 48, size * leading, p[ground])
                if line:
                    plate.label(
                        "".join(content for _, content in line),
                        inset,
                        y,
                        size,
                        p["ink"],
                        colors=[p[role] for role, content in line for _ in content],
                    )
            outputs[f"specimens/{mode}/{scene}.svg"] = plate.svg()
    p = design.colors["chalk"]
    dark = design.colors["shale"]
    social = Drawing(
        int(number(design.leaf("components", "social-width"))),
        int(number(design.leaf("components", "social-height"))),
        p["canvas"],
        "Maesglas: a terminal in mineral and ink",
    )
    social.rect(928, 0, 352, 640, dark["canvas"])
    for content, x, y, font_size, role, weight in BANNER_LABELS:
        palette = dark if x >= 928 else p
        social.label(content, x, y, font_size, palette[role], weight)
    for index, role in enumerate(SWATCH_ROLES):
        social.rect(976, 178 + index * 48, 40, 8, dark[role])
        social.label(role, 1036, 190 + index * 48, 18, dark["ink"])
    outputs["identity/banner.svg"] = social.svg()
    outputs["identity/social.png"] = social.png()
    outputs["identity/mark.svg"] = mark()
    outputs["identity/mark-16.svg"] = mark(small=True)
    return outputs

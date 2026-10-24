"""Check output coverage and font-independent image delivery."""

import io
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import uharfbuzz as hb
from check import Links
from fontTools.ttLib import TTFont
from generate import outputs
from model import MODES, ROOT, load, load_json, mapping, number, sequence, text
from plates import dimensions, lettering
from port_renderers import ALL_PORTS as PORTS


class GenerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = outputs()

    files: dict[str, bytes]

    def test_each_port_has_both_modes(self) -> None:
        for name, (_, extension, _) in PORTS.items():
            for mode in MODES:
                self.assertIn(f"ports/{name}/maesglas-{mode}.{extension}", self.files)

    def test_every_plate_is_outlined(self) -> None:
        plates = [value for key, value in self.files.items() if key.startswith("specimens/")]
        self.assertEqual(len(plates), 14)
        for value in plates:
            root = ET.fromstring(value)
            self.assertIsNotNone(root.find("{http://www.w3.org/2000/svg}title"))
            self.assertNotIn(b"<text", value)
            self.assertNotIn(b"http:", value.replace(b"http://www.w3.org/2000/svg", b""))

    def test_social_dimensions(self) -> None:
        import struct

        image = self.files["identity/social.png"]
        self.assertEqual(image[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", image[16:24]), (1280, 640))

    def test_git_colors_are_quoted(self) -> None:
        for mode in MODES:
            content = self.files[f"ports/git/maesglas-{mode}.gitconfig"].decode()
            self.assertIn(' = "#', content)
            self.assertNotIn(" = #", content)

    def test_macos_reference_cells_and_specimen_dimensions(self) -> None:
        design = load()
        size = number(design.leaf("fonts", "terminal-web"))
        self.assertEqual(size, 15)
        self.assertEqual(size * number(design.leaf("fonts", "advance")), 9)
        self.assertEqual(design.leaf("fonts", "terminal-x-height"), 8.1)
        root = ET.fromstring(self.files["specimens/chalk/code.svg"])
        self.assertEqual(
            (int(root.attrib["width"]), int(root.attrib["height"])), dimensions(design, "code")
        )

    def test_shaped_lines_preserve_cells_and_context(self) -> None:
        faces = load_json(ROOT / "identity/letterforms.json")
        for weight, contents in lettering().items():
            face = mapping(faces[weight])
            self.assertEqual(face["features"], load().leaf("fonts", "features"))
            for content in contents:
                glyphs = sequence(mapping(face["runs"])[content])
                self.assertEqual(len(glyphs), len(content))
                self.assertEqual(
                    [mapping(glyph)["cluster"] for glyph in glyphs], list(range(len(content)))
                )
                self.assertTrue(all(mapping(glyph)["x_advance"] == 600 for glyph in glyphs))
        regular = mapping(faces["400"])
        glyph_names = {
            text(mapping(glyph)["glyph"])
            for values in mapping(regular["runs"]).values()
            for glyph in sequence(values)
        }
        self.assertTrue(any(".leftS" in name or ".rightS" in name for name in glyph_names))
        content = "         basket.extend(row.ripe())"
        path = ROOT / "site/fonts/CommitMono-400-Regular.otf"
        font = hb.Font(hb.Face(path.read_bytes()))
        buffer = hb.Buffer()
        buffer.add_str(content)
        buffer.guess_segment_properties()
        hb.shape(font, buffer, {"calt": 0, "ss01": 0, "ss02": 0, "liga": 0, "dlig": 0})
        with TTFont(path) as font_file:
            unshaped = [font_file.getGlyphName(info.codepoint) for info in buffer.glyph_infos]
        shaped = [mapping(glyph)["glyph"] for glyph in sequence(mapping(regular["runs"])[content])]
        self.assertNotEqual(shaped, unshaped)

    def test_guidance_links_are_themed_or_explicit_downloads(self) -> None:
        parser = Links()
        content = self.files["site/index.html"].decode()
        parser.feed(content)
        self.assertIn("type-measured-macos-reference", parser.ids)
        self.assertIn("install-font-setup", parser.ids)
        self.assertIn("port-notes", parser.ids)
        for target in parser.links:
            if target.startswith("#"):
                self.assertIn(target[1:], parser.ids)
        for tag in re.findall(r"<a\b[^>]*>", content):
            if '.md"' in tag:
                self.assertIn("download", tag)
        self.assertIn("STARSHIP_CONFIG", content)
        self.assertIn("config-file = /path/to/maesglas-chalk.conf", content)

    def test_archive_has_a_working_starting_guide(self) -> None:
        with zipfile.ZipFile(io.BytesIO(self.files["site/maesglas.zip"])) as archive:
            names = set(archive.namelist())
            install = archive.read("INSTALL.md").decode()
            self.assertIn("STARSHIP_CONFIG", install)
            self.assertIn("config-file = /path/to/maesglas-chalk.conf", install)
            self.assertIn(text(load().leaf("fonts", "archive")), install)
            self.assertIn("ports/ghostty/maesglas-chalk.conf", install)
            for name in ("INSTALL.md", "TYPOGRAPHY.md", "PORTS.md", "THIRD_PARTY_NOTICES.md"):
                source = archive.read(name).decode()
                for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", source):
                    if "://" not in target and not target.startswith("#"):
                        self.assertIn(target, names, (name, target))

    def test_stale_and_orphaned_outputs_fail(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for folder in ("scripts", "site/fonts"):
                shutil.copytree(ROOT / folder, root / folder)
            for name in ("LICENSE", "THIRD_PARTY_NOTICES.md", "tools.lock"):
                shutil.copyfile(ROOT / name, root / name)
            shutil.copytree(ROOT / "identity", root / "identity")
            for name, content in self.files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
            command = [sys.executable, str(root / "scripts/generate.py"), "--check"]
            pristine = subprocess.run(command, cwd=root, capture_output=True, check=False)
            self.assertEqual(pristine.returncode, 0, pristine.stderr.decode())
            target = root / "ports/ghostty/maesglas-chalk.conf"
            target.write_bytes(target.read_bytes() + b"# drift\n")
            (root / "ports/ghostty/orphan.conf").write_text("background = invalid\n")
            stale = subprocess.run(command, cwd=root, capture_output=True, check=False)
            self.assertNotEqual(stale.returncode, 0)
            self.assertIn(b"ports/ghostty/maesglas-chalk.conf", stale.stderr)
            self.assertIn(b"ports/ghostty/orphan.conf", stale.stderr)


if __name__ == "__main__":
    unittest.main()

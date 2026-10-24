"""Port shapes, contrast regressions, and fail-closed native parser checks."""

import copy
import json
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from extra_ports import CLAUDE_ROLES, PORTS, claude_code, render
from jsonschema import Draft7Validator
from jsonschema.exceptions import ValidationError
from model import MODES, ROOT, load, load_json, mapping, sequence, text
from validate_extended import (
    CACHE,
    EXECUTABLES,
    audit_matches,
    check_colors,
    check_skin_colors,
    claude_rejection,
    strict_schema,
    validate_schema,
)
from validate_ports import environment


class PortTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = render(load())

    files: dict[str, bytes]

    def document(self, port: str, mode: str) -> dict[str, object]:
        return mapping(json.loads(self.files[f"ports/{port}/maesglas-{mode}.{PORTS[port][1]}"]))

    def test_both_variants_and_extension_contributions(self) -> None:
        for port, (_, extension, _) in PORTS.items():
            for mode in MODES:
                self.assertIn(f"ports/{port}/maesglas-{mode}.{extension}", self.files)
        package = mapping(json.loads(self.files["ports/vscode/package.json"]))
        self.assertEqual(package["publisher"], "maesglas")
        themes = sequence(mapping(package["contributes"])["themes"])
        self.assertEqual(len(themes), 2)
        for value in themes:
            theme = mapping(value)
            self.assertIn("ports/vscode/" + text(theme["path"]).removeprefix("./"), self.files)
        self.assertEqual(self.files["ports/vscode/LICENSE"], (ROOT / "LICENSE").read_bytes())

    def test_ansi_banks_are_not_conventional_black_and_white(self) -> None:
        design = load()
        for mode in MODES:
            p = design.colors[mode]
            expected = [p[role] for role in design.ansi]
            scheme = tomllib.loads(self.files[f"ports/wezterm/maesglas-{mode}.toml"].decode())
            self.assertEqual(scheme["colors"]["ansi"] + scheme["colors"]["brights"], expected)
            colors = mapping(self.document("vscode", mode)["colors"])
            self.assertEqual(colors["terminal.ansiBlack"], expected[0])
            self.assertEqual(colors["terminal.ansiBrightWhite"], expected[15])

    def test_leg_01_audits_syntax_not_only_match_foreground(self) -> None:
        for mode in MODES:
            data = self.document("vscode", mode)
            audit_matches(data, mode)
            rules = sequence(data["tokenColors"])
            first = mapping(rules[0])
            first["settings"] = {"foreground": load().colors[mode]["match"]}
            rules[0] = first
            data["tokenColors"] = rules
            with self.assertRaisesRegex(ValueError, "Contrast below 4.5"):
                audit_matches(data, mode)

    def test_leg_01_audits_semantic_colors_and_both_foreground_keys(self) -> None:
        for mode in MODES:
            original = self.document("vscode", mode)
            broken = copy.deepcopy(original)
            semantic = mapping(broken["semanticTokenColors"])
            semantic["keyword"] = load().colors[mode]["match-active"]
            broken["semanticTokenColors"] = semantic
            with self.assertRaisesRegex(ValueError, "Contrast below 4.5"):
                audit_matches(broken, mode)
            for key in ("editor.findMatchForeground", "editor.findMatchHighlightForeground"):
                broken = copy.deepcopy(original)
                colors = mapping(broken["colors"])
                del colors[key]
                broken["colors"] = colors
                with self.assertRaises(KeyError):
                    audit_matches(broken, mode)

    def test_claude_light_base_has_no_inherited_color_tokens(self) -> None:
        for mode in MODES:
            data = mapping(json.loads(claude_code(load().colors[mode], mode)))
            overrides = mapping(data["overrides"])
            self.assertEqual(set(overrides), set(CLAUDE_ROLES))
            self.assertEqual(data["base"], "light" if mode == "chalk" else "dark")
            self.assertEqual(
                overrides, {key: load().colors[mode][role] for key, role in CLAUDE_ROLES.items()}
            )
            self.assertEqual(overrides["background"], load().colors[mode]["type"])

    def test_claude_shared_tokens_cannot_satisfy_both_pairs(self) -> None:
        rejected = claude_rejection(set(CLAUDE_ROLES))
        for value in mapping(rejected["bounds"]).values():
            bounds = mapping(value)
            self.assertLess(float(str(bounds["maximum_simultaneous_contrast"])), 4.5)
            for ratio in mapping(bounds["candidate_counter_contrast"]).values():
                self.assertGreaterEqual(float(str(ratio)), 4.5)
            for ratio in mapping(bounds["candidate_word_text_contrast"]).values():
                self.assertLess(float(str(ratio)), 4.5)
        self.assertFalse(any(name.startswith("ports/claude-code/") for name in self.files))

    def test_gh_dash_real_keys_inverted_and_warning(self) -> None:
        for mode in MODES:
            colors = mapping(mapping(self.document("gh-dash", mode)["theme"])["colors"])
            self.assertEqual(set(colors), {"text", "background", "border", "icon"})
            self.assertEqual(set(mapping(colors["background"])), {"selected"})
            fields = mapping(colors["text"])
            self.assertEqual(
                set(fields),
                {
                    "primary",
                    "secondary",
                    "inverted",
                    "faint",
                    "warning",
                    "success",
                    "error",
                    "actor",
                },
            )
            p = load().colors[mode]
            self.assertEqual(fields["inverted"], p["ink"])
            self.assertEqual(fields["warning"], p["warning"])

    def test_k9s_native_parser_rejects_invalid_color_types(self) -> None:
        data = self.document("k9s", "chalk")
        skin = mapping(data["k9s"])
        body = mapping(skin["body"])
        body["fgColor"] = {"invalid": "#123456"}
        skin["body"] = body
        data["k9s"] = skin
        self.assert_native_rejection("k9s", data)

    def test_k9s_named_color_fallback_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "FG-K9S-TRUECOLOR"):
            check_skin_colors({"fgColor": "green"}, load().colors["chalk"])

    def test_gh_dash_native_parser_rejects_invalid_color(self) -> None:
        data = self.document("gh-dash", "chalk")
        data["theme"] = {"colors": {"text": {"warning": "not-a-color"}}}
        self.assert_native_rejection("gh-dash", data)

    def assert_native_rejection(self, port: str, data: dict[str, object]) -> None:
        with tempfile.TemporaryDirectory(prefix="parser-negative-", dir=CACHE) as name:
            root = Path(name)
            path = root / "theme.yml"
            path.write_text(json.dumps(data))
            result = subprocess.run(
                [str(CACHE / EXECUTABLES[port]), str(path)],
                cwd=root,
                env=environment(root),
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertTrue(result.stderr)

    def test_zed_schema_rejects_unknown_style_keys(self) -> None:
        data = self.document("zed", "chalk")
        themes = sequence(data["themes"])
        theme = mapping(themes[0])
        theme["style"] = {"editor.notAColor": "#123456"}
        themes[0] = theme
        data["themes"] = themes
        schema = strict_schema(load_json(CACHE / "upstream/zed-schema.json"))
        schema["properties"] = mapping(schema["properties"]) | {"$schema": {"type": "string"}}
        with self.assertRaises(ValidationError):
            validate_schema(Draft7Validator(schema), data)

    def test_palette_leak_fails(self) -> None:
        with self.assertRaisesRegex(ValueError, "outside the palette"):
            check_colors({"foreground": "#123456"}, load().colors["chalk"])


if __name__ == "__main__":
    unittest.main()

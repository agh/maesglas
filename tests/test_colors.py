"""Reference vectors and negative tests for the delivered color contract."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from check import contrast
from colors import MACHADO, apca, simulated_distance, srgb, wcag
from model import load


class ColorTests(unittest.TestCase):
    def test_reference_vectors(self) -> None:
        self.assertEqual(wcag("#000000", "#FFFFFF"), 21)
        self.assertEqual(wcag("#123456", "#123456"), 1)
        self.assertAlmostEqual(apca("#000000", "#FFFFFF"), 106.04067321268862)
        self.assertAlmostEqual(apca("#FFFFFF", "#000000"), -107.88473318309848)
        self.assertEqual(apca("#555555", "#555555"), 0)
        self.assertEqual(srgb([1, 0, 0]), "#FFFFFF")
        self.assertEqual(srgb([0, 0, 0]), "#000000")
        self.assertEqual(srgb([0.6279553606, 0.2576833077, 29.2338852]), "#FF0000")

    def test_rounding_does_not_rescue_a_failure(self) -> None:
        self.assertLess(wcag("#777777", "#FFFFFF"), 4.5)
        self.assertGreater(wcag("#767676", "#FFFFFF"), 4.5)

    def test_rejects_out_of_gamut(self) -> None:
        with self.assertRaises(ValueError):
            srgb([0.8, 0.4, 120])

    def test_all_roles_and_ansi_are_audited(self) -> None:
        design = load()
        count, minimum = contrast(design)
        self.assertEqual(count, 2 * (len(design.roles) + 16) * len(design.grounds))
        self.assertGreaterEqual(minimum, 4.5)

    def test_bad_slot_zero_fails(self) -> None:
        design = load()
        design.colors["chalk"]["ink"] = design.colors["chalk"]["canvas"]
        with self.assertRaisesRegex(ValueError, "Contrast below"):
            contrast(design)

    def test_weak_selection_fails(self) -> None:
        design = load()
        design.colors["shale"]["selection"] = design.colors["shale"]["keyword"]
        with self.assertRaisesRegex(ValueError, "Contrast below"):
            contrast(design)

    def test_match_fills_are_content_grounds(self) -> None:
        for mode in ("chalk", "shale"):
            for ground in ("match", "match-active"):
                design = load()
                self.assertIn(ground, design.grounds)
                design.colors[mode][ground] = design.colors[mode]["keyword"]
                with self.assertRaisesRegex(ValueError, "Contrast below"):
                    contrast(design)

    def test_missing_mode_fails(self) -> None:
        source = copy.deepcopy(load().raw)
        source["palette"] = {"chalk": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "identity.json"
            path.write_text(json.dumps(source))
            with self.assertRaisesRegex(ValueError, "Both complete modes"):
                load(path)

    def test_keyword_type_and_number_separation(self) -> None:
        for palette in load().colors.values():
            for role in ("type", "number"):
                for condition in MACHADO:
                    self.assertGreaterEqual(
                        simulated_distance(palette["keyword"], palette[role], condition), 5
                    )

    def test_original_mulberry_fails_new_pairings(self) -> None:
        for mode, coordinates in (
            ("chalk", [0.48, 0.071, 337]),
            ("shale", [0.9, 0.054, 337]),
        ):
            design = load()
            design.colors[mode]["keyword"] = srgb(coordinates)
            with self.assertRaisesRegex(ValueError, "Color-vision distance below"):
                contrast(design)


if __name__ == "__main__":
    unittest.main()

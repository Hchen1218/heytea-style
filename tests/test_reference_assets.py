import json
import re
import unittest
from pathlib import Path, PurePosixPath

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "private-assets/reference-cutouts/asset-index.json"
FLAVOR_MONSTER_STYLE_ANCHOR = (
    "examples/desktop-pet/pink-green-flavor-monster-v3/preview.png"
)

CORE_DESKTOP_BOARDS = {
    "contact_sheet_dry_media_wavy_line_v4": "primary",
    "contact_sheet_smudged_paint_structure_v3": "secondary",
    "contact_sheet_figure_actions_v2": "primary",
    "contact_sheet_thin_stroke_anatomy_v2": "primary",
    "contact_sheet_mixed_media_objects_v2": "avoid-default",
}

PUBLIC_TEXT_FILES = (
    ROOT / "README.md",
    ROOT / "SKILL.md",
    ROOT / "references/desktop-pet-environment.md",
    ROOT / "references/desktop-pet-workflow.md",
    ROOT / "references/evaluation.md",
    ROOT / "references/monster-poster-workflow.md",
    ROOT / "references/mixed-media-style-guide.md",
)


class ReferenceAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = json.loads(INDEX_PATH.read_text(encoding="utf-8"))
        cls.by_name = {record["name"]: record for record in cls.records}

    def test_every_indexed_asset_is_safe_and_readable(self):
        self.assertTrue(self.records)
        for record in self.records:
            with self.subTest(name=record.get("name")):
                raw_path = record["path"]
                posix_path = PurePosixPath(raw_path)
                self.assertFalse(posix_path.is_absolute())
                self.assertNotIn("..", posix_path.parts)
                self.assertFalse(re.search(r"(^|/)(tmp|var|Users)(/|$)", raw_path))

                asset_path = ROOT / raw_path
                self.assertTrue(asset_path.is_file(), raw_path)
                with Image.open(asset_path) as image:
                    image.verify()
                with Image.open(asset_path) as image:
                    self.assertGreater(image.width, 0)
                    self.assertGreater(image.height, 0)
                    self.assertIn(image.format, {"PNG", "JPEG", "WEBP"})

    def test_required_desktop_boards_keep_their_roles(self):
        for name, expected_quality in CORE_DESKTOP_BOARDS.items():
            with self.subTest(name=name):
                self.assertIn(name, self.by_name)
                record = self.by_name[name]
                self.assertEqual(record["quality"], expected_quality)
                if expected_quality == "primary":
                    self.assertNotEqual(record["quality"], "avoid-default")

    def test_skill_reference_and_readme_paths_stay_consistent(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        style_text = (ROOT / "references/mixed-media-style-guide.md").read_text(
            encoding="utf-8"
        )
        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("private-assets/reference-cutouts/asset-index.json", skill_text)
        for name in CORE_DESKTOP_BOARDS:
            path = self.by_name[name]["path"]
            self.assertIn(path, style_text)
        for public_path in (
            "assets/examples/poster/source-food.jpg",
            "assets/examples/poster/typography-poster.png",
            "assets/examples/poster/doodle-poster.png",
            "assets/examples/desktop-pet/source-drink.png",
            "assets/examples/desktop-pet/canonical-pet.png",
            "assets/examples/desktop-pet/motion-preview.gif",
            "assets/examples/desktop-pet/contact-sheet.png",
            "assets/examples/desktop-pet/runtime-screenshot.png",
        ):
            self.assertIn(public_path, readme_text)
            self.assertTrue((ROOT / public_path).is_file(), public_path)

    def test_flavor_monster_style_anchor_is_readable_and_referenced(self):
        anchor_path = ROOT / FLAVOR_MONSTER_STYLE_ANCHOR
        self.assertTrue(anchor_path.is_file(), FLAVOR_MONSTER_STYLE_ANCHOR)
        with Image.open(anchor_path) as image:
            image.verify()

        for text_path in (
            ROOT / "SKILL.md",
            ROOT / "references/desktop-pet-character-modes.md",
            ROOT / "references/desktop-pet-workflow.md",
            ROOT / "references/mixed-media-style-guide.md",
            ROOT / "references/evaluation.md",
        ):
            with self.subTest(file=text_path.name):
                self.assertIn(
                    FLAVOR_MONSTER_STYLE_ANCHOR,
                    text_path.read_text(encoding="utf-8"),
                )

    def test_photo_entry_and_runtime_gate_references_stay_connected(self):
        skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        workflow_text = (ROOT / "references/desktop-pet-workflow.md").read_text(
            encoding="utf-8"
        )
        environment_text = (
            ROOT / "references/desktop-pet-environment.md"
        ).read_text(encoding="utf-8")

        self.assertIn("references/monster-poster-workflow.md", skill_text)
        self.assertIn("monster-poster-workflow.md", workflow_text)
        for choice in (
            "生成带字版海报",
            "生成不带字海报",
            "生成一张风味小怪兽",
        ):
            self.assertIn(choice, skill_text)
        self.assertIn("after the user has explicitly approved", environment_text)
        self.assertIn("Do not begin motion generation", environment_text)

    def test_public_docs_have_no_local_machine_paths(self):
        forbidden = ("/Users/", "/var/folders/", "/private/tmp/")
        for text_path in PUBLIC_TEXT_FILES:
            text = text_path.read_text(encoding="utf-8")
            for token in forbidden:
                with self.subTest(file=text_path.name, token=token):
                    self.assertNotIn(token, text)

        readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("outputs/", readme_text)
        self.assertNotIn("素材/", readme_text)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_generated_animation_strips import OPTIONAL_ACTION_FRAMES, REQUIRED_ACTION_FRAMES, prepare_directory


def write_action_board(path: Path, frames: int) -> None:
    image = Image.new("RGBA", (frames * 16, 16), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    for frame in range(frames):
        left = frame * 16 + 4
        draw.rectangle((left, 3, left + 7, 12), fill=(20, 20, 20, 255))
    image.save(path)


class PrepareAnimationStripsTest(unittest.TestCase):
    def make_required_sources(self, source: Path) -> None:
        source.mkdir(parents=True)
        for action, frames in REQUIRED_ACTION_FRAMES.items():
            write_action_board(source / f"{action}.png", frames)

    def test_required_only_sources_succeed_and_skip_optional_actions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source, destination = base / "source", base / "out"
            self.make_required_sources(source)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                prepare_directory(source, destination)
            for action in REQUIRED_ACTION_FRAMES:
                self.assertTrue((destination / f"{action}.webp").is_file())
            for action in OPTIONAL_ACTION_FRAMES:
                self.assertFalse((destination / f"{action}.webp").exists())
                self.assertIn(f"skipped optional {action}", output.getvalue())

    def test_present_optional_actions_are_prepared(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source, destination = base / "source", base / "out"
            self.make_required_sources(source)
            for action, frames in OPTIONAL_ACTION_FRAMES.items():
                write_action_board(source / f"{action}.png", frames)
            prepare_directory(source, destination)
            for action in OPTIONAL_ACTION_FRAMES:
                self.assertTrue((destination / f"{action}.webp").is_file())

    def test_missing_required_action_fails_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            source, destination = base / "source", base / "out"
            self.make_required_sources(source)
            (source / "idle.png").unlink()
            with self.assertRaisesRegex(ValueError, "missing required actions: idle"):
                prepare_directory(source, destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()

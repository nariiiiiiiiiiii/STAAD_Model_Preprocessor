from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "build_windows_icon.py"
SPEC = importlib.util.spec_from_file_location("build_windows_icon", SCRIPT_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Could not load icon builder from {SCRIPT_PATH}")
ICON_BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ICON_BUILDER)


def _save_png(path: Path, size: tuple[int, int] = (300, 300)) -> None:
    Image.new("RGBA", size, (24, 40, 56, 255)).save(path, format="PNG")


def test_builder_generates_all_required_ico_sizes_under_build_root(tmp_path: Path) -> None:
    source = tmp_path / "logo.png"
    build_root = tmp_path / "build"
    output = build_root / "windows" / "staad-model-preprocessor.ico"
    _save_png(source)

    result = ICON_BUILDER.build_icon(source, output, build_root=build_root)

    assert result == output.resolve()
    with Image.open(result) as generated:
        assert generated.format == "ICO"
        assert generated.ico.sizes() == {
            (size, size) for size in ICON_BUILDER.ICON_SIZES
        }
        for size in ICON_BUILDER.ICON_SIZES:
            assert generated.ico.getimage((size, size)).size == (size, size)


def test_builder_rejects_output_outside_build_root(tmp_path: Path) -> None:
    source = tmp_path / "logo.png"
    _save_png(source)

    with pytest.raises(ValueError, match="stay under the project build directory"):
        ICON_BUILDER.build_icon(
            source,
            tmp_path / "outside" / "icon.ico",
            build_root=tmp_path / "build",
        )


def test_builder_rejects_non_png_and_insufficient_source_images(tmp_path: Path) -> None:
    build_root = tmp_path / "build"
    jpeg_source = tmp_path / "logo.jpg"
    Image.new("RGB", (300, 300), (24, 40, 56)).save(jpeg_source, format="JPEG")
    with pytest.raises(ValueError, match="must be a PNG"):
        ICON_BUILDER.build_icon(jpeg_source, build_root / "jpeg.ico", build_root=build_root)

    small_source = tmp_path / "small.png"
    _save_png(small_source, size=(128, 128))
    with pytest.raises(ValueError, match="square and at least 256x256"):
        ICON_BUILDER.build_icon(small_source, build_root / "small.ico", build_root=build_root)


def test_builder_rejects_non_square_source_images(tmp_path: Path) -> None:
    source = tmp_path / "wide.png"
    _save_png(source, size=(512, 300))

    with pytest.raises(ValueError, match="square and at least 256x256"):
        ICON_BUILDER.build_icon(
            source,
            tmp_path / "build" / "wide.ico",
            build_root=tmp_path / "build",
        )

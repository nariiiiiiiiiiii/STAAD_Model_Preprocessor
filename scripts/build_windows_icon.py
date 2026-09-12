"""Build a multi-resolution Windows icon from the tracked STAAD logo."""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, cast

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_ROOT = PROJECT_ROOT / "build"
ICON_SIZES = (16, 24, 32, 48, 64, 128, 256)
MIN_SOURCE_SIZE = 256


def _resolve_output_path(output: Path, build_root: Path) -> Path:
    resolved_root = build_root.expanduser().resolve()
    resolved_output = output.expanduser().resolve()
    try:
        resolved_output.relative_to(resolved_root)
    except ValueError as exc:
        raise ValueError(
            f"Icon output must stay under the project build directory: {resolved_root}"
        ) from exc
    if resolved_output.suffix.lower() != ".ico":
        raise ValueError("Icon output must use the .ico extension.")
    return resolved_output


def build_icon(
    source: Path,
    output: Path,
    *,
    build_root: Path | None = None,
) -> Path:
    """Validate the logo PNG and atomically write a multi-resolution ICO under build/."""
    source_path = source.expanduser().resolve()
    allowed_build_root = BUILD_ROOT if build_root is None else build_root
    output_path = _resolve_output_path(output, allowed_build_root)

    if not source_path.is_file():
        raise FileNotFoundError(f"Icon source does not exist: {source_path}")
    if source_path == output_path:
        raise ValueError("Icon source and output must be different files.")

    with Image.open(source_path) as source_image:
        if source_image.format != "PNG":
            raise ValueError("Icon source must be a PNG image.")
        if (
            source_image.width != source_image.height
            or source_image.width < MIN_SOURCE_SIZE
        ):
            raise ValueError(
                f"Icon source must be square and at least {MIN_SOURCE_SIZE}x{MIN_SOURCE_SIZE}."
            )
        source_image.verify()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        file_descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{output_path.stem}.",
            suffix=".tmp.ico",
            dir=output_path.parent,
        )
        os.close(file_descriptor)
        temporary_path = Path(temporary_name)

        with Image.open(source_path) as source_image:
            source_image.convert("RGBA").save(
                temporary_path,
                format="ICO",
                sizes=[(size, size) for size in ICON_SIZES],
            )

        with Image.open(temporary_path) as generated_icon:
            if generated_icon.format != "ICO":
                raise ValueError("Generated icon is not a valid ICO file.")
            generated_sizes = cast(Any, generated_icon).ico.sizes()
            expected_sizes = {(size, size) for size in ICON_SIZES}
            if generated_sizes != expected_sizes:
                raise ValueError(
                    f"Generated ICO sizes mismatch: expected {expected_sizes}, "
                    f"got {generated_sizes}."
                )

        os.replace(temporary_path, output_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        output_path = build_icon(args.source, args.output)
    except (OSError, ValueError) as exc:
        print(f"Icon build failed: {exc}", file=sys.stderr)
        return 2

    print(f"Generated {output_path} with sizes {', '.join(map(str, ICON_SIZES))}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

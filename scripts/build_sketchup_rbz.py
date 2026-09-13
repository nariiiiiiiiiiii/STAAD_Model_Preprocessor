from __future__ import annotations

import re
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from staadprep.version import __version__  # noqa: E402

SOURCE_ROOT = PROJECT_ROOT / "extensions" / "sketchup_staadprep"
BUILD_ROOT = PROJECT_ROOT / "build" / "sketchup"
STAGE_ROOT = BUILD_ROOT / "stage"
VERSION_PATTERN = re.compile(r"EXTENSION\.version\s*=\s*['\"]([^'\"]+)['\"]")

_REQUIRED_FILES = {
    "staadprep_loader.rb": SOURCE_ROOT / "staadprep_loader.rb",
    "staadprep/exporter.rb": SOURCE_ROOT / "staadprep" / "exporter.rb",
}


def _validated_loader_bytes() -> bytes:
    loader = _REQUIRED_FILES["staadprep_loader.rb"]
    text = loader.read_text(encoding="utf-8")
    match = VERSION_PATTERN.search(text)
    if match is None:
        raise RuntimeError("SketchUp loader does not declare EXTENSION.version")
    if match.group(1) != __version__:
        raise RuntimeError(
            "SketchUp extension version "
            f"{match.group(1)!r} does not match app version {__version__!r}"
        )
    return text.encode("utf-8")


def build_rbz() -> Path:
    """Build the version-matched SketchUp extension below project-local ``build/``."""
    missing = [str(path) for path in _REQUIRED_FILES.values() if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing SketchUp extension source: {', '.join(missing)}")

    loader_bytes = _validated_loader_bytes()
    contents = {
        "staadprep_loader.rb": loader_bytes,
        "staadprep/exporter.rb": _REQUIRED_FILES["staadprep/exporter.rb"].read_bytes(),
    }

    for archive_name, data in contents.items():
        staged = STAGE_ROOT / Path(archive_name)
        staged.parent.mkdir(parents=True, exist_ok=True)
        staged.write_bytes(data)

    BUILD_ROOT.mkdir(parents=True, exist_ok=True)
    output = BUILD_ROOT / f"STAAD_Prep_Bridge_{__version__}.rbz"
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for archive_name in sorted(contents):
            info = zipfile.ZipInfo(archive_name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, contents[archive_name])
    return output


def main() -> int:
    try:
        output = build_rbz()
    except Exception as exc:
        print(f"RBZ build failed: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from staadprep.version import __version__  # noqa: E402

PRODUCT = "STAAD Model Preprocessor"
ENTRYPOINT = "STAAD Model Preprocessor.exe"
PACKAGE_NAME = f"STAAD_Model_Preprocessor_{__version__}_win64_portable"
RBZ_NAME = f"STAAD_Prep_Bridge_{__version__}.rbz"
_VERSION_PATTERN = re.compile(r"EXTENSION\.version\s*=\s*['\"]([^'\"]+)['\"]")
_DATA_DIRS = (
    "Data/Config",
    "Data/Projects",
    "Data/Inbox/SketchUp",
    "Data/Exports",
    "Data/Reports",
    "Data/Logs",
    "Data/Cache",
    "Data/Temp",
    "Data/Backups",
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _render_template(source: Path) -> str:
    return source.read_text(encoding="utf-8").replace("<VERSION>", __version__)


def _validate_rbz(rbz: Path) -> None:
    if rbz.name != RBZ_NAME:
        raise RuntimeError(f"RBZ filename must be {RBZ_NAME}, got {rbz.name}")
    with zipfile.ZipFile(rbz) as archive:
        loader = archive.read("staadprep_loader.rb").decode("utf-8")
    match = _VERSION_PATTERN.search(loader)
    if match is None or match.group(1) != __version__:
        raise RuntimeError("RBZ extension version does not match canonical application version")


def _managed_files(package_root: Path) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    files = [item for item in package_root.rglob("*") if item.is_file()]
    for path in sorted(files, key=lambda item: item.relative_to(package_root).as_posix()):
        relative = path.relative_to(package_root).as_posix()
        if relative.startswith("Data/") or relative == "Update/package-manifest.json":
            continue
        entries.append(
            {
                "path": relative,
                "size": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return entries


def _write_manifest(package_root: Path) -> Path:
    manifest = {
        "manifest_schema": 1,
        "product": PRODUCT,
        "version": __version__,
        "platform": "windows-x64",
        "package_type": "portable-standalone",
        "entrypoint": ENTRYPOINT,
        "data_schema": 1,
        "preserve_roots": ["Data/"],
        "sketchup_extension": f"SketchUp_Extension/{RBZ_NAME}",
        "files": _managed_files(package_root),
    }
    update_dir = package_root / "Update"
    update_dir.mkdir(parents=True, exist_ok=True)
    output = update_dir / "package-manifest.json"
    temporary = update_dir / "package-manifest.json.tmp"
    temporary.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    return output


def _write_zip(package_root: Path, archive_path: Path) -> None:
    if archive_path.exists():
        raise FileExistsError(f"Portable archive already exists: {archive_path}")
    prefix = f"{package_root.name}/"
    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        root_info = zipfile.ZipInfo(prefix, date_time=(1980, 1, 1, 0, 0, 0))
        root_info.external_attr = (0o40755 << 16) | 0x10
        archive.writestr(root_info, b"")
        for directory in _DATA_DIRS:
            info = zipfile.ZipInfo(f"{prefix}{directory}/", date_time=(1980, 1, 1, 0, 0, 0))
            info.external_attr = (0o40755 << 16) | 0x10
            archive.writestr(info, b"")
        for path in sorted(item for item in package_root.rglob("*") if item.is_file()):
            relative = path.relative_to(package_root).as_posix()
            info = zipfile.ZipInfo(f"{prefix}{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def assemble_portable(
    standalone_dir: Path,
    rbz_path: Path,
    dist_root: Path,
) -> tuple[Path, Path]:
    """Assemble a versioned portable folder and ZIP without overwriting existing releases."""
    standalone = standalone_dir.resolve()
    rbz = rbz_path.resolve()
    dist = dist_root.resolve()
    if not standalone.is_dir():
        raise RuntimeError(f"Standalone directory does not exist: {standalone}")
    if not (standalone / ENTRYPOINT).is_file():
        raise RuntimeError(f"Standalone entrypoint missing: {standalone / ENTRYPOINT}")
    if not rbz.is_file():
        raise RuntimeError(f"RBZ package does not exist: {rbz}")
    _validate_rbz(rbz)

    dist.mkdir(parents=True, exist_ok=True)
    package_root = dist / PACKAGE_NAME
    archive_path = dist / f"{PACKAGE_NAME}.zip"
    if package_root.exists():
        raise FileExistsError(f"Portable release already exists: {package_root}")
    if archive_path.exists():
        raise FileExistsError(f"Portable archive already exists: {archive_path}")

    shutil.copytree(standalone, package_root)
    for relative in _DATA_DIRS:
        (package_root / relative).mkdir(parents=True, exist_ok=True)

    sketchup_dir = package_root / "SketchUp_Extension"
    sketchup_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(rbz, sketchup_dir / RBZ_NAME)
    (sketchup_dir / "INSTALL_RBZ.md").write_text(
        _render_template(PROJECT_ROOT / "packaging" / "INSTALL_RBZ.md"),
        encoding="utf-8",
    )

    (package_root / "README_PORTABLE.md").write_text(
        _render_template(PROJECT_ROOT / "packaging" / "README_PORTABLE.md"),
        encoding="utf-8",
    )
    update_dir = package_root / "Update"
    update_dir.mkdir(parents=True, exist_ok=True)
    (update_dir / "UPDATE_MANUAL.md").write_text(
        _render_template(PROJECT_ROOT / "packaging" / "UPDATE_MANUAL.md"),
        encoding="utf-8",
    )

    _write_manifest(package_root)
    _write_zip(package_root, archive_path)
    return package_root, archive_path


def _default_standalone_dir() -> Path:
    candidates = sorted(
        path.parent
        for path in (PROJECT_ROOT / "build" / "windows").rglob(ENTRYPOINT)
        if path.is_file()
    )
    if len(candidates) != 1:
        raise RuntimeError(
            "Expected exactly one built standalone directory containing "
            f"{ENTRYPOINT}; found {len(candidates)}"
        )
    return candidates[0]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Assemble STAAD Prep portable Windows release")
    parser.add_argument("--standalone-dir", type=Path)
    parser.add_argument(
        "--rbz",
        type=Path,
        default=PROJECT_ROOT / "build" / "sketchup" / RBZ_NAME,
    )
    parser.add_argument("--dist-root", type=Path, default=PROJECT_ROOT / "dist")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        standalone = args.standalone_dir or _default_standalone_dir()
        package_root, archive_path = assemble_portable(standalone, args.rbz, args.dist_root)
    except Exception as exc:
        print(f"Portable assembly failed: {exc}", file=sys.stderr)
        return 1
    print(package_root)
    print(archive_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

from staadprep.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSEMBLER = PROJECT_ROOT / "scripts" / "assemble_portable.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_rbz_fixture(tmp_path: Path) -> Path:
    source_root = PROJECT_ROOT / "extensions" / "sketchup_staadprep"
    rbz = tmp_path / "input-rbz" / f"STAAD_Prep_Bridge_{__version__}.rbz"
    rbz.parent.mkdir(parents=True)
    with zipfile.ZipFile(rbz, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(
            "staadprep_loader.rb",
            (source_root / "staadprep_loader.rb").read_bytes(),
        )
        archive.writestr(
            "staadprep/exporter.rb",
            (source_root / "staadprep" / "exporter.rb").read_bytes(),
        )
    return rbz


def _assemble_fixture(tmp_path: Path) -> tuple[Path, Path]:
    standalone = tmp_path / "fake-standalone"
    standalone.mkdir()
    (standalone / "STAAD Model Preprocessor.exe").write_bytes(b"fake-exe")
    (standalone / "Qt6Core.dll").write_bytes(b"fake-qt")
    plugin_dir = standalone / "PySide6" / "plugins"
    plugin_dir.mkdir(parents=True)
    (plugin_dir / "platforms.dll").write_bytes(b"fake-plugin")

    rbz = _write_rbz_fixture(tmp_path)

    dist_root = tmp_path / "dist"
    result = subprocess.run(
        [
            sys.executable,
            str(ASSEMBLER),
            "--standalone-dir",
            str(standalone),
            "--rbz",
            str(rbz),
            "--dist-root",
            str(dist_root),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout

    package = dist_root / f"STAAD_Model_Preprocessor_{__version__}_win64_portable"
    archive = dist_root / f"STAAD_Model_Preprocessor_{__version__}_win64_portable.zip"
    return package, archive


def test_manifest_has_update_ready_contract_and_exact_hashes(tmp_path: Path) -> None:
    package, _archive = _assemble_fixture(tmp_path)
    manifest_path = package / "Update" / "package-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["manifest_schema"] == 1
    assert manifest["product"] == "STAAD Model Preprocessor"
    assert manifest["version"] == __version__
    assert manifest["platform"] == "windows-x64"
    assert manifest["package_type"] == "portable-standalone"
    assert manifest["entrypoint"] == "STAAD Model Preprocessor.exe"
    assert manifest["data_schema"] == 1
    assert manifest["preserve_roots"] == ["Data/"]
    assert manifest["sketchup_extension"] == (
        f"SketchUp_Extension/STAAD_Prep_Bridge_{__version__}.rbz"
    )

    file_entries = manifest["files"]
    assert file_entries
    paths = [entry["path"] for entry in file_entries]
    assert paths == sorted(paths)
    assert all("\\" not in path for path in paths)
    assert all(not path.startswith("Data/") for path in paths)
    assert "Update/package-manifest.json" not in paths

    for entry in file_entries:
        path = package / Path(entry["path"])
        assert path.is_file()
        assert entry["size"] == path.stat().st_size
        assert entry["sha256"] == _sha256(path)
        assert entry["sha256"] == entry["sha256"].lower()
        assert len(entry["sha256"]) == 64


def test_assembler_refuses_to_overwrite_existing_release(tmp_path: Path) -> None:
    standalone = tmp_path / "fake-standalone"
    standalone.mkdir()
    (standalone / "STAAD Model Preprocessor.exe").write_bytes(b"fake-exe")

    rbz = _write_rbz_fixture(tmp_path)

    dist_root = tmp_path / "dist"
    existing = dist_root / f"STAAD_Model_Preprocessor_{__version__}_win64_portable"
    existing.mkdir(parents=True)
    sentinel = existing / "KEEP.txt"
    sentinel.write_text("do-not-touch", encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(ASSEMBLER),
            "--standalone-dir",
            str(standalone),
            "--rbz",
            str(rbz),
            "--dist-root",
            str(dist_root),
        ],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode != 0
    assert sentinel.read_text(encoding="utf-8") == "do-not-touch"


def test_portable_zip_contains_data_layout_rbz_and_manual_docs(tmp_path: Path) -> None:
    package, archive = _assemble_fixture(tmp_path)

    expected_dirs = (
        "Data/Config/",
        "Data/Projects/",
        "Data/Inbox/SketchUp/",
        "Data/Exports/",
        "Data/Reports/",
        "Data/Logs/",
        "Data/Cache/",
        "Data/Temp/",
        "Data/Backups/",
    )
    for relative in expected_dirs:
        assert (package / relative).is_dir()

    assert (package / "README_PORTABLE.md").is_file()
    assert (package / "SketchUp_Extension" / "INSTALL_RBZ.md").is_file()
    assert (package / "Update" / "UPDATE_MANUAL.md").is_file()
    assert (
        package / "SketchUp_Extension" / f"STAAD_Prep_Bridge_{__version__}.rbz"
    ).is_file()

    with zipfile.ZipFile(archive) as zipped:
        names = set(zipped.namelist())
        prefix = f"STAAD_Model_Preprocessor_{__version__}_win64_portable/"
        assert names
        assert all(name.startswith(prefix) for name in names)
        assert f"{prefix}STAAD Model Preprocessor.exe" in names
        assert f"{prefix}SketchUp_Extension/STAAD_Prep_Bridge_{__version__}.rbz" in names
        assert f"{prefix}Update/package-manifest.json" in names
        for relative in expected_dirs:
            assert f"{prefix}{relative}" in names

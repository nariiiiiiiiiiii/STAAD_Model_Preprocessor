from __future__ import annotations

import os
from pathlib import Path

import pytest

import staadprep.portable_paths as portable_paths_module
from staadprep.portable_paths import PortablePaths


def test_portable_layout_is_relative_to_release_root(tmp_path: Path) -> None:
    root = tmp_path / "Portable App ไทย"

    paths = PortablePaths.from_root(root)

    assert paths.root == root.resolve()
    assert paths.data == root.resolve() / "Data"
    assert paths.config == paths.data / "Config"
    assert paths.projects == paths.data / "Projects"
    assert paths.sketchup_inbox == paths.data / "Inbox" / "SketchUp"
    assert paths.exports == paths.data / "Exports"
    assert paths.reports == paths.data / "Reports"
    assert paths.logs == paths.data / "Logs"
    assert paths.cache == paths.data / "Cache"
    assert paths.temp == paths.data / "Temp"
    assert paths.backups == paths.data / "Backups"


def test_all_writable_directories_stay_inside_release_root(tmp_path: Path) -> None:
    paths = PortablePaths.from_root(tmp_path / "release")

    assert paths.writable_dirs
    for path in paths.writable_dirs:
        assert path.is_relative_to(paths.root)


def test_assert_inside_root_rejects_parent_traversal(tmp_path: Path) -> None:
    paths = PortablePaths.from_root(tmp_path / "release")

    with pytest.raises(ValueError, match="escapes portable root"):
        paths.assert_inside_root(Path("../escape.log"))


def test_ensure_layout_creates_exact_writable_tree(tmp_path: Path) -> None:
    paths = PortablePaths.from_root(tmp_path / "release")

    paths.ensure_layout()

    assert all(path.is_dir() for path in paths.writable_dirs)
    assert not (paths.root / "build").exists()
    assert not (paths.root / "dist").exists()
    assert not (paths.root / "vendor").exists()


def test_apply_environment_routes_runtime_writes_under_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = PortablePaths.from_root(tmp_path / "release")
    paths.ensure_layout()
    for name in (
        "TEMP",
        "TMP",
        "PYTHONPYCACHEPREFIX",
        "STAADPREP_CACHE_DIR",
        "STAADPREP_LOG_DIR",
        "STAADPREP_PROJECT_ROOT",
        "STAADPREP_SKETCHUP_INBOX",
    ):
        monkeypatch.delenv(name, raising=False)

    paths.apply_environment()

    assert Path(os.environ["TEMP"]) == paths.temp
    assert Path(os.environ["TMP"]) == paths.temp
    assert Path(os.environ["PYTHONPYCACHEPREFIX"]) == paths.cache / "pycache"
    assert Path(os.environ["STAADPREP_CACHE_DIR"]) == paths.cache
    assert Path(os.environ["STAADPREP_LOG_DIR"]) == paths.logs
    assert Path(os.environ["STAADPREP_PROJECT_ROOT"]) == paths.data
    assert Path(os.environ["STAADPREP_SKETCHUP_INBOX"]) == paths.sketchup_inbox


def test_detect_uses_compiled_containing_directory_not_cwd(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    release_root = tmp_path / "release ไทย"
    unrelated_cwd = tmp_path / "elsewhere"
    unrelated_cwd.mkdir()
    monkeypatch.chdir(unrelated_cwd)
    monkeypatch.setattr(
        portable_paths_module,
        "_compiled_containing_dir",
        lambda: release_root.resolve(),
    )

    paths = PortablePaths.detect()

    assert paths is not None
    assert paths.root == release_root.resolve()
    assert paths.root != unrelated_cwd.resolve()


def test_detect_returns_none_for_uncompiled_development(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(portable_paths_module, "_compiled_containing_dir", lambda: None)

    assert PortablePaths.detect() is None


def test_assert_writable_rejects_unwritable_portable_data(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    paths = PortablePaths.from_root(tmp_path / "release")
    paths.ensure_layout()
    real_access = os.access

    def fake_access(path: os.PathLike[str] | str, mode: int) -> bool:
        candidate = Path(path).resolve()
        if candidate == paths.data:
            return False
        return real_access(path, mode)

    monkeypatch.setattr(os, "access", fake_access)

    with pytest.raises(PermissionError, match="Portable Data directory is not writable"):
        paths.assert_writable()

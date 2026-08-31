from pathlib import Path

import pytest

from staadprep.paths import ProjectPaths


def test_generated_paths_are_under_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)
    paths.ensure_layout()

    assert paths.projects == root.resolve() / "artifacts" / "projects"
    assert paths.projects.is_dir()
    for path in paths.generated_dirs:
        assert path.is_relative_to(root)
        assert path.exists()


def test_rejects_path_outside_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)

    with pytest.raises(ValueError):
        paths.assert_inside_project(tmp_path / "outside.log")


def test_relative_path_is_resolved_under_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)

    resolved = paths.assert_inside_project(Path(".logs/app.log"))

    assert resolved == (root / ".logs" / "app.log").resolve()


def test_parent_traversal_cannot_escape_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)

    with pytest.raises(ValueError):
        paths.assert_inside_project(Path("../escape.log"))


def test_runtime_paths_use_portable_data_directories_without_creating_build_outputs(
    tmp_path: Path,
) -> None:
    data = tmp_path / "Portable" / "Data"

    paths = ProjectPaths.from_runtime_root(data)
    paths.ensure_layout()

    assert paths.root == data.resolve()
    assert paths.tmp == data.resolve() / "Temp"
    assert paths.cache == data.resolve() / "Cache"
    assert paths.logs == data.resolve() / "Logs"
    assert paths.projects == data.resolve() / "Projects"
    assert paths.artifacts == data.resolve()
    assert (data / "Projects").is_dir()
    assert (data / "Temp").is_dir()
    assert (data / "Cache").is_dir()
    assert (data / "Logs").is_dir()
    assert not (data / "build").exists()
    assert not (data / "dist").exists()
    assert not (data / "vendor").exists()

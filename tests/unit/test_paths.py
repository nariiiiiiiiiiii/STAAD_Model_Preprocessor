from pathlib import Path

import pytest

from staadprep.paths import ProjectPaths


def test_generated_paths_are_under_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)
    paths.ensure_layout()

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

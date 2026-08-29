from __future__ import annotations

import os
from pathlib import Path

import pytest

import staadprep.app as app_module
from staadprep.portable_paths import PortablePaths


def test_resolve_runtime_paths_prepares_detected_portable_layout(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    portable = PortablePaths.from_root(tmp_path / "Portable App ไทย")
    monkeypatch.setattr(
        app_module.PortablePaths,
        "detect",
        classmethod(lambda _cls: portable),
    )

    project_paths, inbox = app_module.resolve_runtime_paths()

    assert project_paths is not None
    assert project_paths.root == portable.data
    assert project_paths.development_layout is False
    assert inbox == portable.sketchup_inbox
    assert portable.sketchup_inbox.is_dir()
    assert Path(os.environ["TEMP"]) == portable.temp
    assert Path(os.environ["STAADPREP_PROJECT_ROOT"]) == portable.data


def test_resolve_runtime_paths_leaves_development_mode_uninjected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        app_module.PortablePaths,
        "detect",
        classmethod(lambda _cls: None),
    )

    project_paths, inbox = app_module.resolve_runtime_paths()

    assert project_paths is None
    assert inbox is None

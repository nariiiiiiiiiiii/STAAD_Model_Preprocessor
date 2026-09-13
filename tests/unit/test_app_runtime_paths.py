from __future__ import annotations

import os
from pathlib import Path

import pytest

import staadprep.app as app_module
from staadprep.portable_paths import PortablePaths


def test_main_reports_unwritable_portable_root_without_fallback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    messages: list[tuple[str, str]] = []

    monkeypatch.setattr(app_module, "create_application", lambda: object())
    monkeypatch.setattr(
        app_module,
        "resolve_runtime_paths",
        lambda: (_ for _ in ()).throw(PermissionError("portable Data is not writable")),
    )
    monkeypatch.setattr(
        app_module.QMessageBox,
        "critical",
        lambda _parent, title, message: messages.append((title, message)),
    )

    assert app_module.main() == 2
    assert messages == [
        ("Portable folder is not writable", "portable Data is not writable"),
    ]


def test_packaged_workflow_smoke_hook_runs_only_when_requested(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[object] = []
    window = object()
    monkeypatch.delenv("STAADPREP_PACKAGED_WORKFLOW_SMOKE", raising=False)
    monkeypatch.setattr(
        app_module,
        "run_packaged_workflow_smoke",
        lambda received: calls.append(received),
    )

    app_module.run_optional_packaged_workflow_smoke(window)  # type: ignore[arg-type]
    assert calls == []

    monkeypatch.setenv("STAADPREP_PACKAGED_WORKFLOW_SMOKE", "1")
    app_module.run_optional_packaged_workflow_smoke(window)  # type: ignore[arg-type]
    assert calls == [window]


def test_smoke_mode_injects_non_interactive_exit_confirmation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeApplication:
        def exec(self) -> int:
            return 0

        def quit(self) -> None:
            pass

    class FakeWindow:
        def __init__(self, **kwargs: object) -> None:
            captured.update(kwargs)

        def show(self) -> None:
            pass

    monkeypatch.setenv("STAADPREP_SMOKE_MS", "1")
    monkeypatch.delenv("STAADPREP_DEMO", raising=False)
    monkeypatch.delenv("STAADPREP_PACKAGED_WORKFLOW_SMOKE", raising=False)
    monkeypatch.setattr(app_module, "create_application", lambda: FakeApplication())
    monkeypatch.setattr(app_module, "resolve_runtime_paths", lambda: (None, None))
    monkeypatch.setattr(app_module, "MainWindow", FakeWindow)
    monkeypatch.setattr(app_module.QTimer, "singleShot", lambda *_args: None)

    assert app_module.main() == 0
    confirm_exit = captured.get("confirm_exit")
    assert callable(confirm_exit)
    assert confirm_exit(True) is True


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

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QApplication

from staadprep.ui.panels import ViewportPlaceholder
from staadprep.version import __version__


def test_main_window_has_approved_regions(qtbot) -> None:
    from staadprep.ui.main_window import MainWindow

    window = MainWindow(viewport_factory=ViewportPlaceholder)
    qtbot.addWidget(window)

    assert window.project_explorer.objectName() == "project_explorer"
    assert window.viewport_host.objectName() == "viewport_host"
    assert window.properties_panel.objectName() == "properties_panel"
    assert window.validation_panel.objectName() == "validation_panel"
    assert window.quick_fix_panel.objectName() == "quick_fix_panel"
    assert window.issue_console.objectName() == "issue_console"
    assert window.model_status.objectName() == "model_status"
    assert window.model_status.text() == "MODEL STATUS: NO MODEL"


def test_only_backed_actions_are_enabled(qtbot) -> None:
    from staadprep.ui.main_window import MainWindow

    window = MainWindow(viewport_factory=ViewportPlaceholder)
    qtbot.addWidget(window)

    assert window.import_action.isEnabled() is True
    assert window.unit_check_action.isEnabled() is False
    assert window.repair_action.isEnabled() is False
    assert window.normalize_axis_action.isEnabled() is False
    assert window.renumber_action.isEnabled() is False
    assert window.validate_action.isEnabled() is False
    assert window.export_std_action.isEnabled() is False


def test_application_factory_reuses_qapplication() -> None:
    from staadprep.app import create_application

    app = create_application()

    assert isinstance(app, QApplication)
    assert app.applicationVersion() == __version__
    assert create_application() is app


def test_application_and_window_use_the_selected_brand_icon(qtbot) -> None:
    from staadprep.app import create_application, resolve_application_icon
    from staadprep.ui.main_window import MainWindow

    expected_icon = (
        Path(__file__).resolve().parents[2]
        / "assets"
        / "branding"
        / "staad-model-preprocessor.png"
    )
    icon_path = resolve_application_icon()
    app = create_application()

    assert icon_path == expected_icon
    assert icon_path is not None and icon_path.is_file()
    assert app.windowIcon().isNull() is False

    window = MainWindow(viewport_factory=ViewportPlaceholder)
    qtbot.addWidget(window)
    assert window.windowIcon().isNull() is False
    assert window.windowIcon().cacheKey() == app.windowIcon().cacheKey()


def test_application_icon_resolver_prefers_packaged_asset(tmp_path, monkeypatch) -> None:
    from staadprep import app as app_module

    executable_dir = tmp_path / "portable"
    packaged_icon = executable_dir / "branding" / "staad-model-preprocessor.png"
    packaged_icon.parent.mkdir(parents=True)
    packaged_icon.touch()
    monkeypatch.setattr(
        app_module.sys,
        "executable",
        str(executable_dir / "STAAD Model Preprocessor.exe"),
    )

    assert app_module.resolve_application_icon() == packaged_icon

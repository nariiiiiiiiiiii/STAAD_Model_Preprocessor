"""Keep automated UI teardown from blocking on the production exit prompt."""

from __future__ import annotations

import pytest

from staadprep.ui.main_window import MainWindow


@pytest.fixture(autouse=True)
def auto_confirm_exit_during_ui_teardown(request, monkeypatch) -> None:
    """Inject a non-interactive default except in exit-dialog contract tests."""
    if request.node.path.name != "test_exit_confirmation.py":
        monkeypatch.setattr(
            MainWindow,
            "_confirm_exit_dialog",
            lambda _window, _dirty: True,
        )

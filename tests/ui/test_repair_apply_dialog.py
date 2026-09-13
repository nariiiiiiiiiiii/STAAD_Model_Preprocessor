from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog

from staadprep.ui.repair_apply_dialog import RepairApplyDialog


def test_repair_dialog_requires_apply_before_ok_and_applies_once(qtbot) -> None:
    calls = 0

    def apply_once() -> bool:
        nonlocal calls
        calls += 1
        return True

    dialog = RepairApplyDialog("Delete", "Delete 1 Node", apply_once)
    qtbot.addWidget(dialog)

    assert dialog.applied is False
    assert dialog.ok_button.isEnabled() is False
    assert dialog.apply_button.isEnabled() is True
    assert dialog.cancel_button.isEnabled() is True

    qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)

    assert calls == 1
    assert dialog.applied is True
    assert dialog.apply_button.isEnabled() is False
    assert dialog.cancel_button.isEnabled() is False
    assert dialog.ok_button.isEnabled() is True


def test_repair_dialog_cancel_before_apply_rejects_without_callback(qtbot) -> None:
    calls = 0

    def apply_once() -> bool:
        nonlocal calls
        calls += 1
        return True

    dialog = RepairApplyDialog("Merge", "Merge 2 Members", apply_once)
    qtbot.addWidget(dialog)

    qtbot.mouseClick(dialog.cancel_button, Qt.MouseButton.LeftButton)

    assert calls == 0
    assert dialog.applied is False
    assert dialog.result() == QDialog.DialogCode.Rejected


def test_repair_dialog_failed_apply_keeps_ok_disabled(qtbot) -> None:
    calls = 0

    def reject_apply() -> bool:
        nonlocal calls
        calls += 1
        return False

    dialog = RepairApplyDialog("Auto Fix", "Normalize selected Members", reject_apply)
    qtbot.addWidget(dialog)

    qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)

    assert calls == 1
    assert dialog.applied is False
    assert dialog.apply_button.isEnabled() is True
    assert dialog.cancel_button.isEnabled() is True
    assert dialog.ok_button.isEnabled() is False
    assert dialog.error_label.isVisibleTo(dialog) is True


def test_repair_dialog_close_after_apply_is_accepted_without_second_callback(qtbot) -> None:
    calls = 0

    def apply_once() -> bool:
        nonlocal calls
        calls += 1
        return True

    dialog = RepairApplyDialog("Quick Fix", "Apply selected repair", apply_once)
    qtbot.addWidget(dialog)

    qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
    dialog.reject()

    assert calls == 1
    assert dialog.applied is True
    assert dialog.result() == QDialog.DialogCode.Accepted

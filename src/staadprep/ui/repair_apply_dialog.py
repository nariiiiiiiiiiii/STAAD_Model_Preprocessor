"""Explicit Apply-before-OK dialog for reversible repair commands."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class RepairApplyDialog(QDialog):
    """Require an explicit, exact-once Apply before accepting a repair."""

    def __init__(
        self,
        title: str,
        summary: str,
        apply_callback: Callable[[], bool],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._apply_callback = apply_callback
        self._applied = False
        self._has_error = False

        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumWidth(440)

        self.summary_label = QLabel(summary)
        self.summary_label.setWordWrap(True)
        self.error_label = QLabel("Repair could not be applied. Review the status message.")
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #ff8a80;")
        self.error_label.hide()

        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button.setEnabled(False)

        self.apply_button.clicked.connect(self._apply_once)
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_row = QHBoxLayout()
        button_row.addStretch(1)
        button_row.addWidget(self.apply_button)
        button_row.addWidget(self.ok_button)
        button_row.addWidget(self.cancel_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self.summary_label)
        layout.addWidget(self.error_label)
        layout.addLayout(button_row)

    @property
    def applied(self) -> bool:
        return self._applied

    def show_error(self, message: str) -> None:
        self._has_error = True
        self.error_label.setText(message)
        self.error_label.show()

    def _apply_once(self) -> None:
        if self._applied:
            return
        self._has_error = False
        self.error_label.hide()
        if not self._apply_callback():
            if not self._has_error:
                self.show_error("Repair could not be applied. Review the status message.")
            return
        self._applied = True
        self.apply_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.ok_button.setEnabled(True)
        self.ok_button.setFocus()

    def reject(self) -> None:
        if self._applied:
            self.accept()
            return
        super().reject()

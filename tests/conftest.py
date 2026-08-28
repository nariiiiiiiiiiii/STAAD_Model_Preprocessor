"""Shared test environment configuration.

Qt is forced to its offscreen platform before pytest-qt creates QApplication.
This keeps automated UI/VTK smoke tests non-interactive and prevents Windows
platform-plugin dialogs from blocking the test runner.
"""

from __future__ import annotations

import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_API", "pyside6")

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_precision_create_real_qt_vtk_smoke() -> None:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "windows"
    env["QT_API"] = "pyside6"
    env["PYTHONPATH"] = str(root / "src")

    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "smoke_precision_create.py")],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "PRECISION_CREATE_SMOKE_PASS" in completed.stdout
    assert "exact=pass" in completed.stdout
    assert "relative=pass" in completed.stdout
    assert "repeat=pass" in completed.stdout
    assert "preview=pass" in completed.stdout
    assert "undo=pass" in completed.stdout
    assert "navigation=pass" in completed.stdout
    assert "graph=restored" in completed.stdout

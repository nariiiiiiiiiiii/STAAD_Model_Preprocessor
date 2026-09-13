from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_orientation_smoke_runs_with_real_qt_vtk_viewport() -> None:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "windows"
    env["QT_API"] = "pyside6"
    env["PYTHONPATH"] = str(root / "src")

    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "smoke_orientation.py")],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "ORIENTATION_SMOKE_PASS" in completed.stdout
    assert "preview=2" in completed.stdout
    assert "normalized=0" in completed.stdout
    assert "arrows=pass" in completed.stdout
    assert "revision=2" in completed.stdout

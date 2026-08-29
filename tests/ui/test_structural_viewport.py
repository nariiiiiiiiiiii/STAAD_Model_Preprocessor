from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def test_structural_viewport_smoke_runs_in_isolated_process() -> None:
    root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "windows"
    env["QT_API"] = "pyside6"
    env["PYTHONPATH"] = str(root / "src")

    completed = subprocess.run(
        [sys.executable, str(root / "scripts" / "smoke_viewport.py")],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "VIEWPORT_SMOKE_PASS" in completed.stdout
    assert "nodes=16 members=20" in completed.stdout
    assert "focus=pass" in completed.stdout
    assert "isolate=pass" in completed.stdout
    assert "navigation=pass" in completed.stdout
    assert "selection=pass" in completed.stdout
    assert "labels=pass" in completed.stdout
    assert "revision=stable" in completed.stdout

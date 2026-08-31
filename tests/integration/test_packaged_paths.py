from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from staadprep.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = Path(
    os.environ.get(
        "STAADPREP_PACKAGE_ROOT",
        str(
            PROJECT_ROOT
            / "dist"
            / f"STAAD_Model_Preprocessor_{__version__}_win64_portable"
        ),
    )
)
ENTRYPOINT = "STAAD Model Preprocessor.exe"
_EXPECTED_DATA_DIRS = (
    "Config",
    "Projects",
    "Inbox/SketchUp",
    "Exports",
    "Reports",
    "Logs",
    "Cache",
    "Temp",
    "Backups",
)


def _sanitized_env() -> dict[str, str]:
    env = os.environ.copy()
    system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    env["PATH"] = os.pathsep.join(
        [
            str(system_root / "System32"),
            str(system_root),
        ]
    )
    env.pop("PYTHONHOME", None)
    env.pop("PYTHONPATH", None)
    env.pop("VIRTUAL_ENV", None)
    env["QT_QPA_PLATFORM"] = "windows"
    env["STAADPREP_SMOKE_MS"] = "600"
    return env


def _launch(
    package: Path,
    cwd: Path,
    *,
    packaged_workflow_smoke: bool = False,
) -> subprocess.CompletedProcess[str]:
    executable = package / ENTRYPOINT
    assert executable.is_file()
    cwd.mkdir(parents=True, exist_ok=True)
    env = _sanitized_env()
    if packaged_workflow_smoke:
        env["STAADPREP_PACKAGED_WORKFLOW_SMOKE"] = "1"
    assert shutil.which("python", path=env["PATH"]) is None
    return subprocess.run(
        [str(executable)],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )


def _assert_portable_runtime_layout(package: Path) -> None:
    data = package / "Data"
    for relative in _EXPECTED_DATA_DIRS:
        assert (data / relative).is_dir()
    for forbidden in (".tmp", ".cache", ".logs", "build", "dist", "vendor"):
        assert not (package / forbidden).exists()


def test_final_package_launches_without_python_from_different_cwd(tmp_path: Path) -> None:
    assert PACKAGE_ROOT.is_dir(), "T22 final portable package must be assembled before this gate"
    staged = tmp_path / "Portable App ไทย A"
    shutil.copytree(PACKAGE_ROOT, staged)
    unrelated_cwd = tmp_path / "Different Working Directory"

    result = _launch(staged, unrelated_cwd)

    assert result.returncode == 0, result.stderr or result.stdout
    _assert_portable_runtime_layout(staged)


def test_final_package_relocates_and_reopens_with_existing_data(tmp_path: Path) -> None:
    assert PACKAGE_ROOT.is_dir(), "T22 final portable package must be assembled before this gate"
    location_a = tmp_path / "Portable App ไทย A"
    location_b = tmp_path / "Relocated Portable ไทย B"
    shutil.copytree(PACKAGE_ROOT, location_a)
    shutil.copytree(location_a, location_b)
    unrelated_cwd = tmp_path / "Launcher CWD"

    first = _launch(location_b, unrelated_cwd)
    second = _launch(location_b, unrelated_cwd)

    assert first.returncode == 0, first.stderr or first.stdout
    assert second.returncode == 0, second.stderr or second.stdout
    _assert_portable_runtime_layout(location_b)
    assert (location_a / "Data").resolve() != (location_b / "Data").resolve()


def test_final_package_runs_ready_export_workflow_without_python(tmp_path: Path) -> None:
    assert PACKAGE_ROOT.is_dir(), "T22 final portable package must be assembled before this gate"
    staged = tmp_path / "Portable Workflow ไทย"
    shutil.copytree(PACKAGE_ROOT, staged)
    unrelated_cwd = tmp_path / "Workflow Launcher CWD"

    result = _launch(staged, unrelated_cwd, packaged_workflow_smoke=True)

    assert result.returncode == 0, result.stderr or result.stdout
    report_path = staged / "Data" / "Reports" / "packaged-smoke.json"
    assert report_path.is_file()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["ready"] is True
    assert report["manual_command"] == "ConnectNodes"
    assert report["std"] == "Exports/packaged-smoke.std"
    assert report["validation_report"] == "Exports/packaged-smoke.validation.json"
    assert (staged / "Data" / "Exports" / "packaged-smoke.std").is_file()
    assert (staged / "Data" / "Exports" / "packaged-smoke.validation.json").is_file()

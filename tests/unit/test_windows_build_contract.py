from pathlib import Path

SCRIPT = Path("scripts/build_windows.ps1")


def test_windows_build_is_standalone_only_and_avoids_forcing_entire_vtk_stack() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert "--mode=standalone" in text
    assert "--enable-plugin=pyside6" in text
    assert "--assume-yes-for-downloads" in text
    assert "--mode=onefile" not in text
    assert "windows-create-installer" not in text
    assert "--include-package=vtkmodules" not in text
    assert "--include-package=pyvista" not in text
    assert "--include-package=pyvistaqt" not in text
    assert "--report=" in text


def test_windows_build_keeps_all_outputs_project_local() -> None:
    text = SCRIPT.read_text(encoding="utf-8")

    assert '"build\\windows\\final"' in text
    assert '".tmp\\nuitka"' in text
    assert '".cache\\nuitka"' in text
    assert text.index("$env:NUITKA_CACHE_DIR = $CacheRoot") < text.index("-m nuitka --version")
    assert "$env:TEMP = $TempRoot" in text
    assert "$env:TMP = $TempRoot" in text

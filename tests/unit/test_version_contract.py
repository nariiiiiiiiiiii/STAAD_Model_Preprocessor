from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

from staadprep import __version__ as package_version
from staadprep.version import __version__, validate_release_version

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
RUBY_LOADER = PROJECT_ROOT / "extensions" / "sketchup_staadprep" / "staadprep_loader.rb"


def _ruby_extension_version() -> str:
    text = RUBY_LOADER.read_text(encoding="utf-8")
    match = re.search(r"EXTENSION\.version\s*=\s*['\"]([^'\"]+)['\"]", text)
    assert match is not None
    return match.group(1)


def test_canonical_version_drives_project_metadata_and_sketchup_extension() -> None:
    pyproject = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))

    assert __version__ == "0.2.0"
    assert package_version == __version__
    assert pyproject["project"]["dynamic"] == ["version"]
    assert "version" not in pyproject["project"]
    assert pyproject["tool"]["setuptools"]["dynamic"]["version"] == {
        "attr": "staadprep.version.__version__"
    }
    assert _ruby_extension_version() == __version__


@pytest.mark.parametrize("value", ["", "   ", "1/2", r"1\\2"])
def test_release_version_rejects_blank_or_path_separators(value: str) -> None:
    with pytest.raises(ValueError):
        validate_release_version(value)


def test_release_version_accepts_semantic_version() -> None:
    assert validate_release_version("0.2.0") == "0.2.0"

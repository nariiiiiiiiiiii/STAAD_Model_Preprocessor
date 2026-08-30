from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

from staadprep.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILDER = PROJECT_ROOT / "scripts" / "build_sketchup_rbz.py"
RBZ = PROJECT_ROOT / "build" / "sketchup" / f"STAAD_Prep_Bridge_{__version__}.rbz"


def test_rbz_builder_emits_version_matched_extension_with_exact_required_entries() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert RBZ.is_file()

    with zipfile.ZipFile(RBZ) as archive:
        names = sorted(archive.namelist())
        assert names == ["staadprep/exporter.rb", "staadprep_loader.rb"]
        loader = archive.read("staadprep_loader.rb").decode("utf-8")
        exporter = archive.read("staadprep/exporter.rb").decode("utf-8")

    match = re.search(r"EXTENSION\.version\s*=\s*['\"]([^'\"]+)['\"]", loader)
    assert match is not None
    assert match.group(1) == __version__
    assert "UI::HtmlDialog.new" in exporter
    assert "STAAD Prep Bridge" in exporter
    assert "Export Geometry" in exporter
    assert "Choose Inbox" in exporter
    assert "dialog_ready" in exporter
    assert "SP_#{now.strftime('%Y%m%d_%H%M%S')}" in exporter
    assert "SecureRandom" not in exporter


def test_rbz_builder_stages_only_under_project_build_tree() -> None:
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    stage = PROJECT_ROOT / "build" / "sketchup" / "stage"
    assert (stage / "staadprep_loader.rb").is_file()
    assert (stage / "staadprep" / "exporter.rb").is_file()
    assert RBZ.resolve().is_relative_to((PROJECT_ROOT / "build").resolve())

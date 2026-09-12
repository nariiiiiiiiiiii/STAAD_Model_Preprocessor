from __future__ import annotations

import re
import zipfile
from pathlib import Path

import pytest

from staadprep.version import __version__

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BUILDER = PROJECT_ROOT / "scripts" / "build_sketchup_rbz.py"
RBZ = PROJECT_ROOT / "build" / "sketchup" / f"STAAD_Prep_Bridge_{__version__}.rbz"


def test_existing_rbz_archive_matches_version_and_export_name_contract() -> None:
    if not RBZ.is_file():
        pytest.skip("Build the RBZ explicitly before running archive-level acceptance.")

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
    assert "def safe_source_stem(source_file)" in exporter
    assert "now.strftime('%d%m%Y')" in exporter
    assert "format('%s_%02d.json', base, index)" in exporter
    assert "SecureRandom" not in exporter


def test_rbz_builder_declares_only_project_local_build_outputs() -> None:
    text = BUILDER.read_text(encoding="utf-8")

    assert 'BUILD_ROOT = PROJECT_ROOT / "build" / "sketchup"' in text
    assert 'STAGE_ROOT = BUILD_ROOT / "stage"' in text
    assert 'output = BUILD_ROOT / f"STAAD_Prep_Bridge_{__version__}.rbz"' in text

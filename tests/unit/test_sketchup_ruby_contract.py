from __future__ import annotations

from pathlib import Path


def test_ruby_extension_uses_public_sketchup_api_and_neutral_source_space_contract() -> None:
    root = Path.cwd()
    loader = (root / "extensions/sketchup_staadprep/staadprep_loader.rb").read_text(
        encoding="utf-8"
    )
    exporter = (root / "extensions/sketchup_staadprep/staadprep/exporter.rb").read_text(
        encoding="utf-8"
    )
    combined = loader + "\n" + exporter

    assert "SketchupExtension" in loader
    assert "Sketchup.register_extension" in loader
    assert "Send to STAAD Prep" in exporter
    assert "Sketchup.active_model" in exporter
    assert "Sketchup::Edge" in exporter
    assert "Sketchup::Group" in exporter
    assert "Sketchup::ComponentInstance" in exporter
    assert "parent_transform * entity.transformation" in exporter
    assert "transform * edge.start.position" in exporter
    assert "transform * edge.end.position" in exporter
    assert "persistent_id" in exporter
    assert "source_unit" in exporter and '"in"' in exporter
    assert "Z-UP" in exporter
    assert "File.rename" in exporter
    assert "LEGACY_INBOX_SUFFIX" in exporter
    assert "PORTABLE_INBOX_SUFFIX" in exporter
    assert "Select STAAD Prep inbox" in exporter
    assert "UI::HtmlDialog.new" in exporter
    assert "STAAD Prep Bridge" in exporter
    assert "Export Geometry" in exporter
    assert "Choose Inbox" in exporter
    assert "File.directory?(File.expand_path(path))" in exporter
    assert "Select either Data/Inbox/SketchUp or artifacts/sketchup_bridge/inbox." not in exporter
    assert "dialog_ready" in exporter
    assert "DOMContentLoaded" in exporter
    assert "SP_#{now.strftime('%Y%m%d_%H%M%S')}" in exporter
    assert "File.exist?(candidate)" in exporter
    assert "SecureRandom" not in exporter

    forbidden = ("sketchup_z_up_to_staad_y_up", "STAAD(", "http://", "https://", "SketchUpAPI")
    assert not any(token in combined for token in forbidden)

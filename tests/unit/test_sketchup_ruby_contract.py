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
    assert "source_file = model.path.to_s" in exporter
    assert "source_file = model.title.to_s.empty? ? 'Untitled.skp' : model.title.to_s" in exporter
    assert "'source_file' => source_file" in exporter
    assert "next_output_path(inbox, payload['source_file'])" in exporter
    assert "def safe_source_stem(source_file)" in exporter
    assert r"source_file.to_s.tr('\\\\', '/')" in exporter
    assert "filename = File.basename(normalized_path)" in exporter
    assert "extension = File.extname(filename)" in exporter
    assert "stem = File.basename(filename, extension)" in exporter
    assert r'''stem.gsub(/[<>:"\/\\|?*\x00-\x1F]/, '_')''' in exporter
    assert "stem.strip.gsub(/[. ]+\\z/, '')" in exporter
    assert "COM[1-9]|LPT[1-9]" in exporter
    assert "return 'Untitled' if stem.empty?" in exporter
    assert 'base = "#{safe_source_stem(source_file)}_#{now.strftime(\'%d%m%Y\')}"' in exporter
    assert "File.exist?(candidate)" in exporter
    assert "format('%s_%02d.json', base, index)" in exporter
    assert "SP_#{now.strftime('%Y%m%d_%H%M%S')}" not in exporter
    assert "SecureRandom" not in exporter

    forbidden = ("sketchup_z_up_to_staad_y_up", "STAAD(", "http://", "https://", "SketchUpAPI")
    assert not any(token in combined for token in forbidden)

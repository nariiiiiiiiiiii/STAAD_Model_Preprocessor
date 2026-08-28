from __future__ import annotations

from pathlib import Path


def test_native_scaffold_locks_protocol_and_project_local_sdk_staging() -> None:
    root = Path.cwd()
    header = (root / "native/skp_reader/include/neutral_contract.h").read_text(encoding="utf-8")
    cmake = (root / "native/skp_reader/CMakeLists.txt").read_text(encoding="utf-8")
    main = (root / "native/skp_reader/src/main.cpp").read_text(encoding="utf-8")

    assert "kNeutralProtocolVersion = 1" in header
    assert "vendor/sketchup-sdk" in cmake
    assert "--capabilities" in main
    assert r'\"reader_ready\":false' in main
    assert "Task 15" in main


def test_native_runtime_output_matches_skp_bridge_default_location() -> None:
    root = Path.cwd()
    cmake = (root / "native/skp_reader/CMakeLists.txt").read_text(encoding="utf-8")

    assert '"${STAADPREP_PROJECT_ROOT}/build/native/skp_reader"' in cmake
    assert 'RUNTIME_OUTPUT_DIRECTORY "${SKP_READER_OUTPUT_DIR}"' in cmake


def test_native_scaffold_does_not_guess_sketchup_api_headers_or_download_sdk() -> None:
    root = Path.cwd()
    cmake = (root / "native/skp_reader/CMakeLists.txt").read_text(encoding="utf-8").lower()
    main = (root / "native/skp_reader/src/main.cpp").read_text(encoding="utf-8").lower()

    forbidden = (
        "fetchcontent",
        "externalproject_add",
        "http://",
        "https://",
        "suinitialize",
        "sumodelcreatefromfile",
    )
    combined = cmake + "\n" + main
    assert not any(token in combined for token in forbidden)

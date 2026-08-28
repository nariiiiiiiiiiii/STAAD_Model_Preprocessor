Status: **T14 complete on `task/14-skp-bridge`; T15 is next and not started. V1 plan includes T24 post-acceptance DEL quarantine.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source/temp/cache/log/build/test/generated/exported/quarantine files remain inside this root.

## Completed baseline

- T01-T13 completed through `d6dce33 feat: export validated STAAD geometry model`.
- Manual Editing V1 expansion committed on master at `ae37884`.
- T24 post-acceptance cleanup plan committed on master at `350c4ca`.

Canonical continuation documents:
- main V1 plan: `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`;
- SketchUp Ruby Bridge design: `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`;
- Manual Editing T16-T20 plan: `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md`;
- Manual Editing design: `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`.

## T14 — SKP Bridge Contract + Native Helper Capability Probe

Branch/worktree:
- branch: `task/14-skp-bridge`
- worktree: `.worktrees/task-14-skp-bridge`
- base/planning commit: `350c4ca`
- task commit subject: `feat: define isolated native SKP bridge contract`

Created:
- `src/staadprep/importers/skp_bridge.py`
- `native/skp_reader/CMakeLists.txt`
- `native/skp_reader/include/neutral_contract.h`
- `native/skp_reader/src/main.cpp`
- `tests/unit/test_skp_bridge.py`
- `tests/unit/test_skp_native_scaffold.py`
- `tests/ui/test_skp_capability_ui.py`

Modified:
- `src/staadprep/ui/main_window.py`
- `README.md`
- `docs/CHECKLIST.md`
- `docs/TASK_BOARD.md`
- main V1 implementation plan status.

### Neutral process contract

- protocol version: integer `1`;
- helper capability probe: `skp_reader.exe --capabilities`;
- read CLI: `skp_reader.exe --input <file.skp> --output <project-local-json>`;
- neutral envelope: `protocol_version`, `source_file`, `source_unit`, `source_axis`, `points`, `segments`, `groups`, `tags`, `warnings`;
- Python returns existing raw `ImportBatch`; no SketchUp SDK type crosses into the canonical Python model;
- raw SKP coordinates stay source-space in T14; T06/T07 remain responsible for canonical transform/topology in T15.

### Capability / failure behavior

`SkpBridge.capability()` probes without reading a model or downloading anything.

If helper/SDK reader is absent or not ready:

`SKP importer unavailable — DXF remains available`

The desktop app remains launchable and DXF Import remains enabled. Protocol mismatch and malformed neutral JSON fail closed with `SkpBridgeError` rather than silently accepting incompatible data.

Neutral helper outputs are generated only inside project-local `.tmp/skp_bridge/` (or another path validated by `ProjectPaths.assert_inside_project`). The bridge does not auto-delete those outputs.

### Native scaffold boundary

T14 C++ is capability-only. It intentionally does NOT guess SketchUp C API function/header signatures and contains no SDK download logic.

Future optional official C-SDK staging root remains:

`vendor/sketchup-sdk/`

`CMakeLists.txt` advertises this project-local staging location only for a future direct-SKP backend. The approved V1 T15 Ruby path does not require this SDK.

### Native build verification

On 2026-08-28, Visual Studio 2026 Build Tools became available and the T14 capability-only helper was configured and compiled successfully with:
- CMake `4.3.1-msvc1`;
- MSVC tools `14.51.36231` / compiler `19.51.36256.0`;
- x64 host/target Developer Environment.

The native helper builds project-locally to `build/native/skp_reader/skp_reader.exe`, matching `SkpBridge`'s default helper path. Running `--capabilities` returned protocol `1`, `sketchup_sdk=false`, and `reader_ready=false`. This is a valid preserved future-optional backend state and no longer blocks V1.

No toolchain or SketchUp SDK is downloaded automatically by the project.

## T14 verification evidence

TDD/targeted evidence:
- initial RED: `ModuleNotFoundError: staadprep.importers.skp_bridge`;
- UI RED: old tooltip did not report the required SKP-unavailable/DXF-fallback state;
- final targeted T14: 9 tests passed;
- Ruff targeted passed;
- targeted mypy (`skp_bridge.py`, `main_window.py`) passed.
- native CMake configure/build passed with MSVC x64; capability-only helper executed successfully.
- real built-helper -> `SkpBridge.capability()` integration passed (`protocol=1`, `sdk=False`, `ready=False`).

Regression split after implementation:
- unit: 157 passed;
- UI (includes real Qt/VTK subprocess smokes): 22 passed;
- integration: 3 passed;
- total evidence: 182 tests passed;
- full Ruff `src tests scripts`: passed.

## Important boundary

T14 native direct-SKP capability remains preserved, but V1 no longer depends on official C SDK access. The approved T15 path is SketchUp Ruby Extension -> Neutral JSON v1 plus independent Direct DXF Import.

T14 does not change T13 `.STD` export semantics and does not implement manual editing.

## Next Task

**T15 — SketchUp Ruby Extension + Neutral Import Integration**

Risk: **STRICT HR-1 / HR-2 already covered by the user's approved high-risk envelope.**

Approved V1 input architecture:
- SketchUp open model -> public Ruby Extension `Send to STAAD Prep` -> Neutral JSON v1 -> project-local `artifacts/sketchup_bridge/inbox/` -> shared T06/T07 canonical pipeline;
- Direct DXF Import -> existing `DxfReader` -> shared T06/T07 canonical pipeline;
- Direct `.skp` through T14 C++/C SDK is future optional and no longer blocks V1.

Detailed spec: `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md`.

T15 must preserve the existing DXF route and independently verify nested SketchUp transform coordinates before canonical conversion.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It moves only verified-unused/superseded files into project-local `DEL/`, writes `DEL/UNUSED_FILES_MANIFEST.md`, and never deletes files. Final deletion is user-controlled.

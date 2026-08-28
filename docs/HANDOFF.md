# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T04 implemented on `task/04-viewer`; awaiting user approval before T05.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry; it is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ application target.
- PySide6 desktop UI.
- PyVista/VTK 3D viewport.
- NumPy/SciPy for numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- UI baseline: `docs/UI_BASELINE.md` and `docs/ui/*.svg`.
- STRICT approval already granted for HR-1 through HR-4.

## Execution rule

Normally execute one Task at a time. The user explicitly authorized `Task 3 + 4` in the current run. T03 and T04 were handled sequentially with separate commits. Stop after T04.

## Completed T01

Commit: `4a7551b chore: bootstrap project-local Python runtime`

Key outputs:
- project-local runtime path guard,
- `.tmp/.cache/.logs/artifacts/build/dist/vendor` ownership,
- path escape tests,
- `scripts/run_dev.ps1`.

## Completed T02

Commit: `8e4c2f8 feat: add approved desktop UI shell`

Key outputs:
- locked desktop shell layout,
- toolbar/project explorer/viewport host/right panels/issue console/status,
- engineering actions disabled until backing Tasks exist,
- PySide6 6.11.2 verified on Python 3.14.3.

## Completed T03

Commit: `f97bffe feat: add canonical structural model contract`

Key outputs:
- `Vec3`, `Node`, `Member`, `ProjectModel`, `ModelMetadata`,
- stable UUID identity independent from STAAD-facing numbers,
- versioned project JSON schema `1`,
- non-finite coordinate rejection,
- round-trip project serialization.

Important boundary: T03 does not merge nodes, infer topology, repair connectivity, convert units, or transform axes.

## T04 — completed deliverables

Branch/worktree:
- branch: `task/04-viewer`
- worktree: `.worktrees/task-04-viewer`
- base commit: `f97bffe`

Created/implemented:
- `src/staadprep/viewer/scene.py`
- `src/staadprep/viewer/selection.py`
- `src/staadprep/viewer/widget.py`
- `src/staadprep/viewer/demo.py`
- `src/staadprep/viewer/__init__.py`
- `tests/unit/test_scene_data.py`
- `tests/ui/test_structural_viewport.py`
- `tests/conftest.py`
- `scripts/smoke_viewport.py`

Modified:
- `src/staadprep/ui/main_window.py` — real `StructuralViewport` replaces placeholder by default; viewport factory injection keeps lightweight UI tests isolated from VTK.
- `src/staadprep/app.py` — development demo frame loads only when `STAADPREP_DEMO=1`.
- `scripts/run_dev.ps1` — enables development demo mode.
- `pyproject.toml` — declares `pyvistaqt` runtime dependency.

### Scene contract

`SceneData.from_model(model)` produces deterministic:
- `(N, 3)` point coordinates,
- VTK line connectivity,
- stable UUID ordering,
- rendered-cell-index -> member UUID mapping.

Dangling member references fail closed with `ValueError`.

### Real viewport behavior

`StructuralViewport` provides:
- Y-Up XYZ axes/grid,
- canonical model rendering,
- node/member actors,
- member cell selection callback,
- programmatic member highlighting,
- programmatic node highlighting,
- stable selection state,
- demo multi-bay structural frame in development mode.

Demo fixture currently produces:
- 16 nodes,
- 20 members.

## Qt / VTK diagnostic result

The earlier popup `This application failed to start because no Qt platform plugin could be initialized` was NOT caused by Qt being absent.

Verified on this machine:
- Python `3.14.3`,
- PySide6 `6.11.2`,
- Qt runtime `6.11.2`,
- PyVista `0.48.4`,
- pyvistaqt `0.12.0`,
- VTK `9.6.2`,
- normal `QApplication` uses platform `windows` successfully.

Two actual T04 implementation defects were found and fixed during Windows render smoke testing:
1. Line mesh was initially created as point vertex cells + line cells, causing `member_index` cell-data length mismatch. It now creates line-only `PolyData`.
2. `QtInteractor` accepts `off_screen=` at construction but pyvistaqt 0.12.0 does not expose `.off_screen`. `StructuralViewport` now owns `_off_screen` state itself.

Test-environment policy:
- pytest lightweight Qt tests use `QT_QPA_PLATFORM=offscreen`,
- VTK/PyVista viewport rendering is verified in a separate subprocess using the real Windows Qt platform,
- do not use VTK offscreen rendering as the T04 acceptance path on this Windows stack because it is unstable in the connector environment.

## T04 verification

Verified before commit:
- full pytest regression: 15 passed,
- Ruff: PASS,
- real Windows app demo auto-close: PASS,
- real viewport subprocess smoke: `VIEWPORT_SMOKE_PASS nodes=16 members=20`,
- member cell selection + UUID mapping: PASS,
- node/member highlight state: PASS,
- normal Qt platform initialization: `windows` PASS.

## Next Task

**T05 — DXF Raw-Geometry Vertical Slice**

Risk: STANDARD.

T05 will:
- define raw import contracts,
- read DXF `LINE`, 3D `POLYLINE`, and `POINT`,
- preserve raw coordinates/layers/unit metadata without conversion,
- show `RAW DXF PREVIEW — NOT VALIDATED`,
- wire the first real Import Model flow.

Do not start T05 until the user explicitly says `เริ่ม Task 5` / `Run T05`.

# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T05 complete on `task/05-dxf`; awaiting user approval before T06.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ application target; current machine is Python 3.14.3.
- PySide6 desktop UI.
- PyVista + pyvistaqt + VTK 3D viewport.
- NumPy/SciPy for numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- UI baseline: `docs/UI_BASELINE.md` and `docs/ui/*.svg`.
- STRICT approval already granted for HR-1 through HR-4.

## Completed tasks

- T01 `4a7551b` — project-local Python/runtime bootstrap and path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — real PyVista/VTK viewport + synthetic frame + selection/highlight.

## T05 — DXF raw-geometry vertical slice

Branch/worktree:
- branch: `task/05-dxf`
- worktree: `.worktrees/task-05-dxf`
- base commit: `a38fc97`

Created:
- `src/staadprep/importers/__init__.py`
- `src/staadprep/importers/contracts.py`
- `src/staadprep/importers/dxf_reader.py`
- `src/staadprep/importers/raw_preview.py`
- `tests/golden_models/01_dxf_lines/source.dxf`
- `tests/integration/test_dxf_reader.py`
- `tests/integration/test_raw_dxf_preview.py`
- `tests/ui/test_dxf_import_flow.py`
- `scripts/smoke_dxf_preview.py`

Modified:
- `src/staadprep/ui/main_window.py`
- `src/staadprep/ui/panels.py`
- `tests/ui/test_main_window.py`
- status/checklist/plan docs.

### T05 behavior

`DxfReader` extracts only raw:
- `LINE`,
- 3D `POLYLINE` expanded into segments,
- `POINT`,
- layer names,
- source handles/references,
- `$INSUNITS` metadata.

No T05 operation may:
- convert units,
- transform axes,
- merge coincident endpoints,
- snap/repair geometry,
- detect structures/topology,
- claim the preview is validated.

The temporary raw preview deliberately creates separate endpoint nodes for each raw segment. The golden fixture therefore renders 3 segments as 3 members + 7 nodes (6 segment endpoints + 1 POINT), even where raw coordinates coincide.

UI behavior:
- `Import Model` is enabled for DXF.
- imported raw lines render in the real 3D viewport.
- Project Explorer displays raw node/member counts and declared unit.
- status is exactly `RAW DXF PREVIEW — NOT VALIDATED`.
- Unit Check, Repair, Normalize Axis, Renumber, Validate, and Export STD remain disabled until their backing Tasks exist.

## T05 verification evidence

Golden DXF fixture:
- `$INSUNITS = 4` -> `mm`
- 1 LINE
- 1 3D POLYLINE -> 2 segments
- 1 POINT
- total raw segments = 3
- total raw points = 1

TDD RED observed:
- importer: `ModuleNotFoundError: staadprep.importers`
- raw preview: `ModuleNotFoundError: staadprep.importers.raw_preview`
- summary binding: `ProjectExplorerPanel` lacked `summary_label` before implementation.

Final verification before task close:
- full pytest regression: 18 passed.
- Ruff: pass.
- T04 viewport smoke: `VIEWPORT_SMOKE_PASS nodes=16 members=20`.
- T05 real Windows-render smoke: `DXF_PREVIEW_SMOKE_PASS segments=3 points=1 render_nodes=7 render_members=3 unit=mm`.
- `git diff --check`: pass.

## Important boundaries for T06

T05 captures source unit metadata but does **not** convert it.

Example current fixture coordinates remain raw millimetres:
- `(0,0,0) -> (6000,0,0)` stays exactly `6000` in T05.

T06 is STRICT HR-1 and owns:
- verified unit conversion to canonical metre,
- scale/reference-length logic,
- model extents/dimension checks,
- SketchUp Z-Up -> STAAD Y-Up coordinate transform,
- coordinate tolerance/rounding semantics defined by the T06 plan.

Do not mix topology merge/repair into T06; topology construction remains T07 / HR-2.

## Next task

**T06 — Unit, Scale, Dimension, and Z-Up→Y-Up Engine**

Risk: **STRICT HR-1 / Full TDD already approved by user.**

Do not start T06 until the user explicitly says to continue/run Task 6.

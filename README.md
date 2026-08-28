Desktop preprocessor and focused analytical line-model editor for cleaning structural geometry before STAAD.Pro.

## Product goal

Reduce repeated cleanup inside STAAD.Pro by converting SketchUp/DXF geometry into a clean, validated analytical model before export, while allowing routine Node/Member corrections directly in the app.

Primary workflow:

`SketchUp (.skp) / DXF -> Import -> Unit/Scale -> Validate -> Quick Fix / Manual Edit -> Connectivity -> Direction -> Renumber -> READY -> Export .STD -> STAAD.Pro`

## Current status

- T01-T13 complete; deterministic minimal `.STD` geometry export is implemented.
- T14 complete: isolated SKP process bridge, neutral protocol v1, capability probe, native CMake/C++ scaffold, and fail-soft DXF fallback UI.
- T15 is next: official SketchUp C API edge extraction + canonical transform/topology integration.
- V1 execution plan now runs through T24: Manual Editing T16-T20, READY/packaging/acceptance T21-T23, then non-destructive unused-file quarantine to project-local `DEL/` in T24.
- Primary OS: Windows 11.
- Primary language: Python.
- UI: PySide6.
- 3D: PyVista/VTK.
- DXF: ezdxf.
- SKP: official SketchUp C API helper (C++) behind an importer adapter.
- STAAD output: `.STD`.

## Approved V1 manual-editing direction

V1 will add:
- SketchUp-style Middle-Mouse Orbit / Shift+Middle Pan / Wheel Zoom,
- explicit Select/Create Node/Draw Member/Move-Snap/Delete edit modes,
- snap/inference + X/Y/Z axis locks,
- exact/relative Create Node,
- optional Create Member,
- STAAD-like Translational Repeat for analytical nodes/members,
- Auto Node Number / Auto Member Number / Auto Number All,
- Auto Fix Axis / Flip Selected / Set Direction,
- entity labels, selection filters, ghost preview, atomic Undo/Redo.

V1 intentionally does NOT become a general CAD package: no arbitrary Rotate/Mirror/full Copy Array/Trim/Extend/Offset/solids/section modeling.

## Canonical documents

- `docs/PROJECT_SPEC.md` — requirements and V1 scope
- `docs/ARCHITECTURE.md` — system boundaries/modules
- `docs/WORKFLOW.md` — user/data/editing workflows
- `docs/CHECKLIST.md` — delivery checklist
- `docs/RISK_GATES.md` — verification levels and approval gates
- `docs/UI_BASELINE.md` — approved layout/interaction behavior
- `docs/HANDOFF.md` — continuation context
- `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md` — approved manual-editing design
- `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md` — T16-T20 implementation plan

## Development rule

Do not turn this into a mini STAAD solver or a second SketchUp. V1 exists to clean, inspect, directly correct, and organize analytical line geometry so engineering design can start faster in STAAD.Pro.

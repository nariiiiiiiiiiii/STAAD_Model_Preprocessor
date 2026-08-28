# STAAD Model Preprocessor

Desktop preprocessor for cleaning analytical structural geometry before STAAD.Pro.

## Product goal

Reduce manual cleanup inside STAAD.Pro by converting SketchUp/DXF geometry into a clean, validated analytical model before export.

Primary workflow:

`SketchUp (.skp) / DXF -> Import -> Unit/Scale -> Clean -> Connectivity -> Repair -> Normalize -> Renumber -> Validate -> Export .STD -> STAAD.Pro`

## Status

- Phase: Design baseline / pre-implementation
- UI baseline: locked from the approved dark desktop mockup
- Primary OS: Windows 11
- Primary language: Python
- UI: PySide6
- 3D: PyVista/VTK
- DXF: ezdxf
- SKP: SketchUp C API helper (C++) behind an importer adapter
- STAAD output: `.STD`

## Canonical documents

- `docs/PROJECT_SPEC.md` — requirements and scope
- `docs/ARCHITECTURE.md` — system boundaries and modules
- `docs/WORKFLOW.md` — user and data workflows
- `docs/CHECKLIST.md` — delivery checklist
- `docs/RISK_GATES.md` — verification level and approval gates
- `docs/UI_BASELINE.md` — approved UI behavior/layout
- `docs/HANDOFF.md` — continuation context

## Development rule

Do not turn this into a mini STAAD solver. V1 exists to clean and organize analytical geometry so engineering design can start faster in STAAD.Pro.

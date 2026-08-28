# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: Design package created; implementation not started yet.

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created files, temp, logs, cache, build output, artifacts, test output, and staged dependencies must remain inside this root.

## User goal

Eliminate the repetitive cleanup step between SketchUp and structural design in STAAD.Pro.

The app should prepare a clean analytical geometry model before STAAD.Pro so the user can begin section/load/design work with minimal manual geometry cleanup.

## Approved product direction

Desktop application, not a web app.

Primary workflow:

`SketchUp SKP / DXF -> Preprocessor -> repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

Primary input target: `.skp` directly.
Fallback input: `.dxf`.

Primary output: `.std`.

Do NOT make V1 a structural solver or mini STAAD.

## Approved technology direction

- Python 3.12+ primary language.
- PySide6 desktop UI.
- PyVista/VTK 3D viewer.
- NumPy/SciPy as needed.
- ezdxf for DXF.
- C++ SketchUp C API helper for native SKP reading behind an adapter boundary.
- Nuitka preferred later for Windows distribution after compatibility is proven.

## Approved UI baseline

Dark professional engineering application.

Layout:
- top toolbar/ribbon,
- left Project Explorer,
- central 3D viewport,
- right Properties + Validation + Quick Fix,
- bottom Issue Console,
- status/model summary.

Reference mockups:
- `docs/ui/main_dashboard.svg`
- `docs/ui/unit_check.svg`
- `docs/ui/issue_repair.svg`

Do not redesign V1 unless explicitly requested.

## V1 focus

- import SKP/DXF,
- unit/scale/reference-length verification,
- model extents/measurements,
- canonical node/member graph,
- duplicate/near/orphan detection,
- short/zero/duplicate members,
- gaps and crossing-without-node,
- connected-component/structure count,
- inspect/isolate/highlight issues,
- repair inside app,
- normalize member incidence/local-X direction,
- deterministic renumber,
- final validation,
- export `.STD`,
- audit/repair history,
- Windows executable.

## Deferred patches

After V1 is in real use, possible patches include:
- member property helpers,
- support assignment,
- loads,
- load combinations,
- OpenSTAAD integration,
- IFC/BIM,
- advanced SketchUp component/solid -> analytical centerline extraction.

## Development strategy

Optimize for fastest path to real use.

Use vertical slices and stable interfaces.

Recommended order:
1. foundation/UI shell,
2. canonical model,
3. DXF vertical slice for fast core proof,
4. validator/issue model,
5. repair command framework,
6. viewer integration,
7. normalize/renumber,
8. `.STD` exporter,
9. SKP native adapter,
10. packaging/real-project acceptance.

Although DXF may be implemented first internally, SKP remains the primary V1 user input target.

## Risk / approval gate

Per Serena development policy, these are HIGH-RISK and must NOT be implemented before explicit user approval for STRICT / Full TDD:

1. unit/coordinate/axis transformation semantics,
2. topology/connectivity mutation and automatic repair,
3. STAAD `.STD` exporter semantics,
4. deterministic renumber with reference rewriting.

Reason: defects can create an analytical model that looks clean visually but is structurally/connectively wrong.

See `docs/RISK_GATES.md`.

Low-risk UI/foundation work can proceed after the written-spec review gate.

## Current state

Created:
- isolated project directory,
- project-local Git repository,
- mandatory file-boundary rules,
- product specification,
- architecture,
- workflow,
- checklists,
- risk gates,
- UI baseline,
- three SVG UI mockups.

No production code has been implemented yet.

## Next action

1. User reviews/approves written spec package.
2. Create detailed implementation plan.
3. Begin foundation + UI shell / safe vertical-slice work.
4. Separately obtain explicit STRICT approval before high-risk engineering semantics are implemented.

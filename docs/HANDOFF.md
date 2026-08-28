# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **SPEC APPROVED + STRICT APPROVED; implementation plan ready; T01 is next.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all project-created source files, temp, logs, cache, build output, artifacts, test output, generated reports, and staged dependencies must remain inside this root.

## User goal

Eliminate repetitive structural-geometry cleanup between SketchUp and STAAD.Pro so design work can begin with little or no manual model cleanup in STAAD.Pro.

Primary workflow:

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

Primary input target: `.skp` directly.
Fallback input: `.dxf`.
Primary output: `.std`.

V1 is a geometry/topology preprocessor, not a solver or mini STAAD.

## Approved technology

- Python 3.12+ primary application language.
- PySide6 desktop UI.
- PyVista/VTK 3D viewport.
- NumPy/SciPy for indexed numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- Nuitka preferred for Windows packaging after runtime compatibility is proven.

## Approved UI baseline

Do not redesign V1 unless explicitly requested.

References:
- `docs/UI_BASELINE.md`
- `docs/ui/main_dashboard.svg`
- `docs/ui/unit_check.svg`
- `docs/ui/issue_repair.svg`

Layout:
- toolbar/ribbon,
- Project Explorer,
- central 3D viewport,
- Properties + Validation + Quick Fix,
- Issue Console,
- persistent model summary/status.

## Approval state

User explicitly approved on 2026-08-28:
1. current Project Spec,
2. STRICT / Full TDD for HR-1 through HR-4.

Approved high-risk areas:
- HR-1 unit/scale/coordinate/axis transformations,
- HR-2 topology/connectivity detection and structural graph repair,
- HR-3 STAAD `.STD` exporter semantics,
- HR-4 deterministic node/member numbering and mapping integrity.

Do not request this approval again for the same scoped V1 behavior. If a new high-risk area outside HR-1..HR-4 appears, request a new explicit approval before implementing it.

See `docs/RISK_GATES.md`.

## Execution mode

The user requires **one Task at a time**.

Detailed plan:
`docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`

Operational board:
`docs/TASK_BOARD.md`

Mandatory end-of-Task sequence:
1. targeted verification,
2. update TASK_BOARD/CHECKLIST/HANDOFF,
3. Git commit,
4. report to user,
5. STOP and wait for explicit instruction to run the next Task.

## Current state

Completed design/setup package:
- isolated project directory,
- project-local Git repository,
- project-boundary rules,
- PROJECT_SPEC,
- ARCHITECTURE,
- WORKFLOW,
- CHECKLIST,
- RISK_GATES,
- UI baseline + SVG mockups,
- detailed T01–T18 implementation plan,
- operational TASK_BOARD.

No production application code has been implemented yet.

## Next Task

**T01 — Python Bootstrap + Project-Local Path Guard**

Expected deliverable:
- `pyproject.toml`,
- Python `src/staadprep` bootstrap,
- project-local temp/cache/log/build path service,
- path-escape tests,
- project-local development launcher.

Risk: STANDARD.

Do not start T02 during the same execution.

## Resume instruction

When the user says `เริ่ม Task 1` / `Run T01`, execute only T01 from:
`docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`

After T01 verification + commit, stop.

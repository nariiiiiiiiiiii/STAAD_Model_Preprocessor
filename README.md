Desktop preprocessor and focused analytical line-model editor for cleaning structural geometry before STAAD.Pro.

## Product goal

Reduce repeated cleanup inside STAAD.Pro by converting SketchUp/DXF geometry into a clean, validated analytical model before export, while allowing routine Node/Member corrections directly in the app.

Primary workflow:

`SketchUp Ruby Bridge / Direct DXF -> Import -> Unit/Scale -> Validate -> Quick Fix / Manual Edit -> Connectivity -> Direction -> Renumber -> READY -> Export .STD -> STAAD.Pro`

## Current status

- **Latest source follow-up (2026-09-12):** owner-approved app/package source version is `0.2.0`.
  SketchUp export naming, selected logo integration, unrestricted Project JSON Open with Save-back,
  and multi-issue Quick Fix/intersection routing are source-verified. The high-risk batch scope
  received explicit STRICT / Full TDD approval.
- Focused strict evidence: **345 unit+integration passed**, **1 skipped** (archive-level RBZ test
  awaits an explicitly built package), **3 portable-executable gates deselected** (the `0.2.0`
  executable is not built), and **26/26 affected UI tests passed**; Ruff and strict mypy pass.
- The accepted portable release remains `0.1.0`; no `0.2.0` executable/RBZ/ZIP is available or
  accepted. The owner partially smoke-tested the development app on 2026-09-12: the app-window icon
  changed, and Quick Fix/Undo/Redo work. A source-level Windows taskbar identity/window-icon fix is
  now implemented and focused-tested; owner visual retest and full app acceptance remain pending.
  The existing executable is still version `0.1.0.0` (last modified 2026-09-06). Compile and release
  packaging require a separate explicit user instruction.
- A legacy integration test briefly generated a transient `0.2.0` RBZ during the first full-suite
  run; that file was removed. Its test fixtures now stay under `.tmp/tests`, and the existing
  ignored `build/sketchup/stage/` source copies were refreshed by that run and left in place.

- T01-T13 complete; deterministic minimal `.STD` geometry export is implemented.
- T14 complete: isolated SKP process bridge, neutral protocol v1, capability probe, native CMake/C++ scaffold, and fail-soft DXF fallback UI.
- T15 complete: lightweight SketchUp Ruby Extension -> Neutral JSON v1 -> shared T06/T07 canonical import; Direct DXF remains an independent first-class route.
- T16 complete: safe SketchUp-style viewport navigation, selection filters, overlap cycling, labels, focus/context actions, and non-mutating SELECT foundation.
- T17 complete: deterministic canonical-space Node/Endpoint/Midpoint/Intersection inference, X/Y/Z axis locks, explicit work-plane ray intersection, and viewport keyboard constraint foundation.
- T18 complete: reversible Create/Move, atomic CompositeRepair, Draw/Move-Snap/Delete/Split viewport editing, ghost previews, exact Undo graph restoration, and real Qt/VTK manual-edit smoke.
- T19 complete: click/snap + exact/relative Node creation, collision-safe optional member creation, STAAD-like Translational Repeat, ghost preview, explicit Use Existing/Skip/Cancel resolution, deterministic collision handling, and one-step atomic Undo.
- T20 complete: reversible Auto Node/Member/All numbering with Old->New preview, Auto Fix Axis All/Selected, Flip Selected, and endpoint-driven Set Direction are implemented, verified, and committed on `task/20-model-controls`.
- Final T20 verification: **243 unit + 88 UI + 5 integration = 336 tests passed**. Ruff passed; T20-local strict mypy reports **0 issues in 5 affected source files**. Four inherited `dxf_reader.py` typing errors remain outside T20 when the full import graph is reported.
- T21 complete: authoritative `ReadyGate`/`READY FOR STAAD`, golden 01-11 end-to-end coverage, combined dirty-model repair/manual-edit convergence, direction/numbering invariants, independent `.STD` parser round-trip, and project-local validation/audit JSON are implemented.
- Final T21 verification: **275 unit+integration + 92 UI = 367 tests passed**. UI verification uses the permanent MCP-safe isolated runner (**62 lightweight + 30 VTK/renderer**); Ruff passed, T21-local strict mypy reports **0 issues in 4 affected source/runner files**, and `git diff --check` passed.
- T22 Portable Standalone Windows Packaging is **COMPLETE** on branch `task/22-portable-packaging` in this worktree; T23 acceptance is **PASS** (user-tested 2026-09-01).
- T24 post-acceptance quarantine is **COMPLETE**; the superseded editing-final package is recoverable under `DEL/t24-quarantine-20260901/` and no files were deleted.
- T25 storage audit is **COMPLETE as historical move evidence**; its quarantine contents were later removed by the user. The current manifest remains under `DEL/`.
- Post-move standalone smoke recheck is **PASS (1/1)** from a different CWD with Python removed from PATH; the current executable and ZIP hashes are unchanged.
- T26 space-cleanup move is **COMPLETE**; generated `.tmp`/`.cache` contents and 22 old clean worktrees are under `DEL/t26-storage-cleanup-20260901/`. Nothing was deleted; only T22 remains registered as an active worktree.
- T27 free user-selected paths is **SOURCE + PACKAGE COMPLETE**; SketchUp input/output and STD export accept explicit user-selected locations, with the previous package/build/RBZ archived under `DEL/t27-free-path-selection-20260906/`.
- The post-T22 ten-item editing-correction package is a **VERIFIED HISTORICAL CHECKPOINT**. Its
  Reset/Crop, Properties, Delete, Merge, orphan removal, Member Repeat, Create Node, and edit-mode
  evidence is preserved, but it is superseded for current acceptance by later source follow-ups.
- Current source status (2026-08-31): all agreed follow-ups are **USER ACCEPTED / FULL SOURCE
  VERIFIED** with **332/332 source unit+integration** and **140/140 UI** passing. The user then
  authorized compile step 1; Nuitka standalone compilation completed successfully. Portable
  assembly and ZIP creation completed in `dist/post-t22-refresh-save-final/`; package-only
  verification is **7/7 PASS**. Real user package acceptance is also **PASS** (2026-08-31).
- `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` is the quarantined historical package
  and does not contain every accepted source follow-up.
  Earlier baseline and `post-t22-ux-final` releases are documented as recoverable historical
  archives under `DEL/standalone-archive-20260831/`. The accepted current package is already
  available under `dist/post-t22-refresh-save-final/`.
- The Nuitka standalone `.exe` launches without Python from a different CWD and after relocation to paths containing spaces/Unicode; all runtime state remains under package-local `Data/`.
- Historical editing-final verification: **325/325 unit+integration**, **111/111 UI** (**77 lightweight + 34 isolated VTK**), three real Windows smokes, package gates **4/4**, manifest hashes **811/811**, extracted-ZIP launch without Python, strict mypy **0 issues in 7 affected source files**, Ruff, and `git diff --check` passed; evidence is preserved under `DEL/`.
- Historical editing-final ZIP SHA-256: `5B261CCEC2DD75D88F6DB3456548F15D714190365F5348ADD77481D3CA48E52B`.
- Extract the ZIP to a writable, reasonably short path such as `D:\STAAD_Preprocessor\`; deeply nested paths can exceed the legacy Windows DLL path limit used by bundled VTK modules.
- The synchronized documentation map and live-status entry point is [`docs/INDEX.md`](docs/INDEX.md).
- The complete post-T24 worktree, source/test/package, and RBZ relationship map is
  [`docs/WORKTREE_MINDMAP.md`](docs/WORKTREE_MINDMAP.md).
- Primary OS: Windows 11.
- Primary language: Python.
- UI: PySide6.
- 3D: PyVista/VTK.
- SketchUp V1: lightweight public Ruby Extension with one primary `Send to STAAD Prep` action -> Neutral JSON v1 bridge.
- Direct DXF: ezdxf first-class import route.
- Direct `.skp`: T14 C++ bridge retained as future optional backend if official C SDK access is granted.
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
- `docs/superpowers/specs/2026-08-28-sketchup-ruby-bridge-design.md` — approved V1 SketchUp Ruby + Direct DXF import architecture
- `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md` — approved manual-editing design
- `docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md` — T16-T20 implementation plan

## Development rule

Do not turn this into a mini STAAD solver or a second SketchUp. V1 exists to clean, inspect, directly correct, and organize analytical line geometry so engineering design can start faster in STAAD.Pro.


## 2026-08-31 source handoff checkpoint

Current source includes the accepted post-T22 editing/UI/persistence improvements. The latest
real-user defect was `X -> Yes` not closing the app; the source fix uses equality for the native Qt
Yes result and delegates accepted close events to `QMainWindow.closeEvent()`. Focused exit
regression is **4/4 PASS**, Ruff PASS, strict mypy clean, and `git diff --check` PASS. Real-user
retest accepted the corrected `No`/`Yes` close behavior. Full source verification is **complete**:
**332/332 source unit+integration** and **140/140 UI** pass, together with real Windows source
smokes, Ruff, strict mypy, and diff checks. Nuitka compile step 1 and the new assembled portable
folder/ZIP are complete under `dist/post-t22-refresh-save-final/`; package-only verification is
still pending.

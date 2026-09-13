# Marquee Selection and Zoom in Select Implementation Plan
> Historical plan record: task-date checkboxes and status are preserved as recorded; for current status see [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add filtered drag-rectangle selection and rename the existing crop-camera command without changing model geometry.

**Architecture:** `MainWindow` exposes a checkable Crop to Select mode alongside the existing Node/Member filters and a separate Zoom in Select camera action. `StructuralViewport` draws a `QRubberBand`, projects scene Nodes/Members to viewport coordinates, computes filtered rectangle hits, then updates the existing `SelectionState` and highlights once.

**Tech Stack:** Python 3.12, PySide6, PyVista/VTK, pytest.

**Spec:** `docs/superpowers/specs/2026-09-12-marquee-selection.md`

## Global Constraints

- A marquee is selection-only; do not mutate the canonical model, change member/node geometry, hide geometry, or execute repair commands.
- Reuse `SelectionFilter`, `SelectionState`, and existing selection/highlight signals.
- Ctrl-drag adds selection to match current Ctrl+click behavior; ordinary drag replaces it.
- Middle-mouse navigation and all edit tools retain existing behavior.
- Keep generated/test artifacts under the project root and do not compile/package.
- Execute inline per the owner's previously selected workflow; stop for owner testing before compilation.

---

### Task 1: Wire the two distinct selection/view actions

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`
- Test: `tests/ui/test_viewport_navigation.py`
- Test: `tests/ui/test_viewport_context_menu.py`
- Test: `tests/ui/test_selection_properties.py`

**Interfaces:**
- `MainWindow.crop_to_select_action`: checkable selection-mode action labeled **Crop to Select**.
- `MainWindow.zoom_in_select_action`: existing selected-camera-framing action labeled **Zoom in Select**.
- `StructuralViewport.set_crop_to_select_enabled(enabled: bool) -> None`: turns only the marquee gesture on/off.
- `StructuralViewport.zoom_in_select() -> None`: preserves the previous camera-framing behavior.

- [x] **Step 1: Add failing action/label tests.** Assert the View toolbar contains the new Crop to
  Select action near Nodes/Members filters and Zoom in Select in place of the old Crop to Selection
  label. Assert the old action still calls the viewport's zoom method, and Crop mode toggles the
  viewport flag and exits when another edit mode is selected.

- [x] **Step 2: Run the focused UI tests and confirm the new contract fails.**

Run: `..\..\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.tmp\tests\marquee-actions-red tests\ui\test_viewport_navigation.py tests\ui\test_viewport_context_menu.py tests\ui\test_selection_properties.py -q`

Observed before implementation: **7 failed, 7 passed**, specifically on the missing new/renamed
actions and the old context-menu label.

- [x] **Step 3: Implement action wiring.** Rename the existing action property/label and context-menu
  entry to Zoom in Select while connecting them to the unchanged zoom behavior. Add a checkable Crop
  to Select action next to the Node/Member filter controls; when enabled, force Select mode and call
  `set_crop_to_select_enabled(True)`. When another edit mode starts, uncheck the action and disable
  the marquee.

### Task 2: Implement and verify filtered marquee geometry selection

**Files:**
- Modify: `src/staadprep/viewer/widget.py`
- Test: `tests/unit/test_marquee_selection_geometry.py`
- Test: `tests/ui/test_crop_to_select_events.py`
- Modify: `scripts/smoke_viewport.py`
- Modify: `tests/ui/test_structural_viewport.py`
- Test: `tests/ui/test_viewport_navigation.py`

**Interfaces:**
- `StructuralViewport.set_crop_to_select_enabled(enabled: bool) -> None` controls the active mode.
- `_select_screen_rectangle(start: tuple[float, float], end: tuple[float, float], *, additive: bool) -> None` selects filtered projected entities and emits one selection update.
- `_project_world_point(point: np.ndarray) -> tuple[float, float, float]` converts a world point to interactor-local X/Y plus depth.
- `_segment_intersects_rectangle(start, end, rect) -> bool` uses a Liang–Barsky clip test for projected member segments.

- [x] **Step 1: Add rectangle geometry and isolated VTK smoke assertions.** The pure test covers
  crossing, contained, and outside screen-space Member segments. `scripts/smoke_viewport.py` uses a
  real Qt/VTK process to assert the rubber-band appears during held-left drag, Nodes-only and
  Members-only filters, both-filter endpoint/member selection, Ctrl-drag addition, overlay cleanup,
  and unchanged model revision.

- [ ] **Step 2: Complete real-renderer/owner acceptance after the runtime error is resolved.**

Run: `..\..\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.tmp\tests\marquee-vtk-check tests\ui\test_structural_viewport.py -q`

Attempted once in an isolated process; it failed before the smoke assertions because VTK's Win32
OpenGL backend reported `failed to get valid pixel format`, followed by a Python Application Error.
Do not repeat offscreen or same-process VTK runs in this session. Next evidence must come from the
owner checking the visible development app after dismissing the error dialog. If the app still
errors, stop marquee acceptance and diagnose the Windows VTK/OpenGL runtime separately before any
new renderer smoke.

- [x] **Step 3: Add the visible drag rectangle.** Create a `QRubberBand` parented to
  `plotter.interactor`; capture the start point and Ctrl modifier on left press; while Crop to Select
  is active and left remains held, update a normalized rectangle; hide it on release, Escape, model
  reset, or when the mode is disabled.

- [x] **Step 4: Project scene entities and apply the selection filter.** Convert each Node and each
  Member endpoint from VTK display coordinates to interactor-local coordinates, rejecting projected
  points outside the camera depth range. Include a Node if its point is inside the rectangle and a
  Member if its projected segment intersects the rectangle. Apply `SelectionFilter`; replace sets
  on ordinary drag and append de-duplicated hits on Ctrl-drag; render highlights and emit
  `selection_changed` once.

- [x] **Step 5: Verify non-renderer action and geometry tests.**

Run: `..\..\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.tmp\tests\marquee-isolated-qt-20260912 tests\ui\test_crop_to_select_events.py tests\ui\test_viewport_navigation.py tests\ui\test_selection_properties.py tests\unit\test_marquee_selection_geometry.py -q`

Observed: **13/13 PASS**; Ruff PASS; strict mypy **0 issues** in `main_window.py` and `widget.py`.
This does not replace the VTK smoke or owner visual test.

- [x] **Step 6: Run `git diff --check`; synchronize README, HANDOFF, INDEX, TASK_BOARD, CHECKLIST,
  and this plan; commit the viewport-only checkpoint and pause for owner testing. Do not compile.**

Observed: `git diff --check` passed; the listed status documents and worktree mindmap now record
the source/test evidence, the unresolved VTK/OpenGL runtime smoke, and the approved-but-queued Save
task. The viewport-only checkpoint is being committed with owner acceptance still pending.

# Desktop Interaction Usability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Node/Member selection reliable and visibly highlighted, make right-click actions usable, add Reset View, reorder tools, and mark active modes.

**Architecture:** Correct the Qt-to-VTK coordinate boundary once and route all pickers through it. Keep selection in `StructuralViewport`, synchronize context-requested filters with `MainWindow`, expose Fit and Reset as separate non-mutating commands, and style checked `QAction` tools explicitly.

**Tech Stack:** Python, PySide6, PyVista/VTK, pytest/pytest-qt, isolated Windows renderer runner, Nuitka standalone.

**Spec:** `docs/superpowers/specs/2026-08-30-post-t22-usability-design.md`

## Global Constraints

- Do not change model coordinates, topology, repair commands, numbering, ReadyGate, or `.STD` output.
- Selection, highlights, menus, Fit, and Reset are non-mutating.
- Preserve Ctrl additive selection, deterministic overlap cycling, and `Shift+Z` Fit Model.
- This plan covers requirements 3 through 9.

---

### Task 1: Lock the Qt-to-VTK coordinate contract

**Files:**
- Create: `tests/unit/test_viewport_display_coordinates.py`
- Modify: `scripts/smoke_viewport.py`

**Interfaces:**
- Produces tests for `_scaled_vtk_display_coordinates(...) -> tuple[float, float] | None`

- [ ] **Step 1: Add pure conversion tests**

```python
def test_qt_to_vtk_coordinates_scale_and_flip_y() -> None:
    assert StructuralViewport._scaled_vtk_display_coordinates(
        100.0, 50.0, widget_size=(400, 200), render_size=(800, 400)
    ) == (200.0, 300.0)

def test_qt_to_vtk_coordinates_fail_closed_for_zero_size() -> None:
    assert StructuralViewport._scaled_vtk_display_coordinates(
        10.0, 10.0, widget_size=(0, 200), render_size=(800, 400)
    ) is None
```

- [ ] **Step 2: Extend the real renderer smoke**

Project one Node and one Member midpoint from world to VTK display, convert to Qt logical coordinates, perform real clicks, then assert selected keys and highlight actors:

```python
assert node_key in viewport.selection.selected_nodes
assert viewport._node_highlight_actor is not None
assert member_key in viewport.selection.selected_members
assert viewport._member_highlight_actor is not None
```

- [ ] **Step 3: Confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_viewport_display_coordinates.py -q
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope renderer --run-id post-t22-selection-red
```

### Task 2: Correct every picker coordinate

**Files:**
- Modify: `src/staadprep/viewer/widget.py`

**Interfaces:**
- Produces: `_scaled_vtk_display_coordinates`, `_vtk_display_coordinates`
- Used by: `_pick_candidate_for_actor`, `_pick_world_at`

- [ ] **Step 1: Add the pure helper**

```python
@staticmethod
def _scaled_vtk_display_coordinates(
    x: float,
    y: float,
    *,
    widget_size: tuple[int, int],
    render_size: tuple[int, int],
) -> tuple[float, float] | None:
    widget_width, widget_height = widget_size
    render_width, render_height = render_size
    if min(widget_width, widget_height, render_width, render_height) <= 0:
        return None
    return (
        x * render_width / widget_width,
        (widget_height - y) * render_height / widget_height,
    )
```

- [ ] **Step 2: Add the live-size wrapper**

```python
def _vtk_display_coordinates(self, x: float, y: float) -> tuple[float, float] | None:
    render_width, render_height = self.plotter.render_window.GetSize()
    return self._scaled_vtk_display_coordinates(
        x,
        y,
        widget_size=(self.plotter.interactor.width(), self.plotter.interactor.height()),
        render_size=(int(render_width), int(render_height)),
    )
```

- [ ] **Step 3: Route both pickers through it**

```python
display = self._vtk_display_coordinates(x, y)
if display is None:
    return None
display_x, display_y = display
picker.Pick(display_x, display_y, 0.0, self.plotter.renderer)
```

- [ ] **Step 4: Confirm GREEN**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_viewport_display_coordinates.py tests/unit/test_selection_cycle.py -q
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope renderer --run-id post-t22-selection-green
```

### Task 3: Add Reset View and functional context actions

**Files:**
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `tests/ui/test_viewport_navigation.py`
- Create: `tests/ui/test_viewport_context_menu.py`

**Interfaces:**
- Produces: `reset_view()`, `selection_filter_requested = Signal(object)`, `_build_context_menu()`

- [ ] **Step 1: Add Reset View**

```python
def reset_view(self) -> None:
    if self.scene is None or not self.scene.points.size:
        return
    self.plotter.view_isometric()
    self.plotter.reset_camera()
    self.plotter.reset_camera_clipping_range()
    self.plotter.render()
```

- [ ] **Step 2: Add context selection requests**

Declare `selection_filter_requested = Signal(object)`. Mode actions apply and emit one exact filter:

```python
SelectionFilter(nodes=True, members=False)
SelectionFilter(nodes=False, members=True)
SelectionFilter(nodes=True, members=True)
```

Each action enters `EditMode.SELECT`, removes now-disallowed selection, rerenders highlights, and emits the filter.

- [ ] **Step 3: Build actions before displaying the menu**

`_build_context_menu()` returns a `QMenu` with exact always-available entries:

```text
Select Nodes
Select Members
Select Nodes + Members
Fit Model
Reset View
```

Add Focus/Clear only when meaningful. Connect each `triggered` signal directly; `_show_context_menu` only calls `menu.exec(global_position)`.

- [ ] **Step 4: Select an entity under right-click before menu construction**

```python
def _show_context_menu(self, local_position, global_position) -> None:
    candidates = self._pick_candidates_at(*local_position)
    if candidates:
        self.select_overlap_candidates(candidates)
    self._build_context_menu().exec(global_position)
```

Empty-space right-click leaves selection unchanged and exposes mode/view actions.

- [ ] **Step 5: Test callbacks without automating a native popup**

Build the menu, find actions by text, call `trigger()`, and assert filters, edit mode, Fit/Reset calls, and Focus/Clear availability.

### Task 4: Synchronize order and active highlights

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/ui/theme.py`
- Modify: `tests/ui/test_viewport_navigation.py`
- Modify: `tests/ui/test_main_window.py`

**Interfaces:**
- Consumes: `selection_filter_requested`
- Produces: `reset_view_action`, `_apply_context_selection_filter(filter)`

- [ ] **Step 1: Create Reset View action**

```python
self.reset_view_action = QAction("Reset View", self)
self.reset_view_action.setToolTip("Restore isometric orientation and fit the whole model")
self.reset_view_action.triggered.connect(lambda: self._call_viewport("reset_view"))
```

- [ ] **Step 2: Synchronize context filters**

```python
def _apply_context_selection_filter(self, selection_filter: SelectionFilter) -> None:
    self._activate_select_mode()
    self.select_nodes_action.setChecked(selection_filter.nodes)
    self.select_members_action.setChecked(selection_filter.members)
    self._sync_selection_filter()
```

- [ ] **Step 3: Set exact toolbar order**

Workflow:

```python
(self.import_action, self.unit_check_action, self.repair_action,
 self.auto_fix_axis_action, self.renumber_action, self.validate_action,
 self.export_std_action)
```

Edit & View:

```python
(self.select_mode_action, self.create_node_mode_action,
 self.create_node_dialog_action, self.draw_member_action,
 self.move_snap_action, self.delete_mode_action, self.split_action,
 self.translational_repeat_action, self.auto_fix_selected_action,
 self.flip_selected_action, self.set_direction_action)
```

Then filters, labels, Fit, and Reset groups.

- [ ] **Step 4: Add explicit checked styling**

```css
QToolButton:checked {
    background: #214d70;
    border-color: #4da3ff;
    color: #ffffff;
    font-weight: 700;
}
QToolButton:checked:hover {
    background: #285d86;
    border-color: #6db5ff;
}
```

- [ ] **Step 5: Test order and state**

Assert exact action order, Select checked by default, exactly one edit mode checked after switching, context filters reflected in toolbar, and Reset invoking `viewport.reset_view()`.

### Task 5: Verify and rebuild the portable release

**Files:**
- Generated: `build/windows/post-t22-ux/app.dist/`
- Generated: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/`
- Generated: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`
- Modify: `docs/HANDOFF.md`, `docs/CHECKLIST.md`, `docs/TASK_BOARD.md`, `docs/INDEX.md`

**Interfaces:**
- Consumes: verified source and rebuilt RBZ
- Produces: updated executable, folder, ZIP, manifest, and evidence

- [ ] **Step 1: Run targeted STANDARD verification**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_viewport_display_coordinates.py tests/unit/test_selection_cycle.py tests/unit/test_interaction_state.py tests/ui/test_viewport_navigation.py tests/ui/test_viewport_context_menu.py tests/ui/test_main_window.py -q
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope renderer --run-id post-t22-ux-final
..\..\.venv\Scripts\python.exe -m ruff check src/staadprep/viewer/widget.py src/staadprep/ui/main_window.py src/staadprep/ui/theme.py tests/unit/test_viewport_display_coordinates.py tests/ui/test_viewport_context_menu.py
..\..\.venv\Scripts\python.exe -m mypy --strict --follow-imports=silent src/staadprep/viewer/widget.py src/staadprep/ui/main_window.py
git diff --check
```

- [ ] **Step 2: Run affected regression**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit tests/integration -q
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope all --run-id post-t22-ux-regression
```

- [ ] **Step 3: Build standalone**

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -OutputRoot build/windows/post-t22-ux
```

Confirm the report says `mode="standalone"` and `completion="yes"`, then launch from a different CWD.

- [ ] **Step 4: Assemble and verify package**

```powershell
..\..\.venv\Scripts\python.exe scripts/assemble_portable.py --standalone-root build/windows/post-t22-ux/app.dist --rbz build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz --dist-root dist
..\..\.venv\Scripts\python.exe -m pytest tests/integration/test_package_manifest.py tests/integration/test_packaged_paths.py tests/integration/test_packaged_workflow_smoke.py -q
```

- [ ] **Step 5: Stop for user acceptance**

Verify real Node/Member clicks, highlights, context actions on entity/empty space, active mode highlight, order, Fit, and Reset View.

- [ ] **Step 6: Commit after acceptance**

```powershell
git add src/staadprep/viewer/widget.py src/staadprep/ui/main_window.py src/staadprep/ui/theme.py scripts/smoke_viewport.py tests docs
git commit -m "fix: improve viewport selection and tool usability"
```

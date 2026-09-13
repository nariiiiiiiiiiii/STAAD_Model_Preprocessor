# Post-T22 Editing Corrections Implementation Plan
> Historical plan record: task-date checkboxes and status are preserved as recorded; for current status see [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make viewport editing, deletion, properties, camera controls, Member merge, and selected-Member repeat work predictably in the portable desktop application.

**Architecture:** Keep camera/selection presentation in `StructuralViewport`, entity formatting and QAction orchestration in `MainWindow`/panels, and every analytical mutation in reversible repair commands. STANDARD UI work and STRICT graph/coordinate work are separate checkpoints; the STRICT tasks cannot begin before explicit approval.

**Tech Stack:** Python 3.14, PySide6, PyVista/VTK, pytest/pytest-qt, isolated Windows renderer runner, Nuitka standalone.

**Spec:** `docs/superpowers/specs/2026-08-30-post-t22-editing-corrections-design.md`

**Execution checkpoint (2026-08-31):** implementation and package verification are complete. Evidence: 325/325 unit+integration, 111/111 UI, three real Windows smokes, Ruff, strict mypy, `git diff --check`, package gates 4/4, manifest 811/811, and extracted-ZIP launch. `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` is a superseded historical package; the later consolidated `dist/post-t22-refresh-save-final/` package is the accepted release. Do not start T23 before the accepted release checkpoint is committed.

## Global Constraints

- Do not silently mutate coordinates or connectivity.
- Every graph/coordinate mutation must use `RepairHistory`, produce audit parameters, and be undoable.
- Preserve stable UUID identity and leave new STAAD numbers unset until numbering.
- Do not change ReadyGate, validation meaning, or `.STD` exporter semantics.
- STRICT tasks require explicit user approval before implementation.

---

### Task 1: Lock camera, crop, selection, and Properties contracts (STANDARD)

**Files:**
- Modify: `tests/ui/test_viewport_navigation.py`
- Create: `tests/ui/test_selection_properties.py`
- Modify: `tests/ui/test_viewport_context_menu.py`

**Interfaces:**
- Produces tests for `reset_view()`, `crop_to_selection()`, and `selection_changed(nodes, members)`.

- [x] Write failing tests that assert Reset uses view-up `(0, 1, 0)` and a positive X/Y/Z camera offset from model center.
- [x] Write a failing renderer test that selects one Node and one Member and verifies `crop_to_selection()` frames only their bounds without changing model revision.
- [x] Write failing Qt tests for Node, Member, mixed, and cleared Properties content.
- [x] Run the three files and confirm failures identify missing STAAD camera, crop action, selection signal, and entity rendering.

### Task 2: Implement STAAD Reset View and Crop to Selection (STANDARD)

**Files:**
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `tests/ui/test_viewport_navigation.py`
- Modify: `tests/ui/test_viewport_context_menu.py`

**Interfaces:**
- Produces `StructuralViewport.crop_to_selection() -> None`.
- Reset camera contract: focal point is model center, position is center plus positive equal-span XYZ offset, view-up is Y.

- [x] Implement a pure camera-frame helper returning position/focal/view-up from bounds.
- [x] Route Reset View through the canonical Y-up helper, camera reset, and clipping reset.
- [x] Add `Crop to Selection` to toolbar and right-click menu; disable it with empty selection.
- [x] Run focused camera/context tests and real viewport smoke; confirm model revision is unchanged.

### Task 3: Wire selection to Properties and disambiguate controls (STANDARD)

**Files:**
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/ui/panels.py`
- Modify: `tests/ui/test_selection_properties.py`
- Modify: `tests/ui/test_viewport_navigation.py`

**Interfaces:**
- Produces `selection_changed = Signal(object, object)`.
- Produces `PropertiesPanel.set_selection(model, node_keys, member_keys) -> None`.

- [x] Emit the complete selection after select/toggle/clear/filter/model refresh.
- [x] Connect the signal in `MainWindow` and render Node coordinates/number/UUID or Member endpoints/length/group/source.
- [x] Rename actions to `Create Node (Click)`, `Create Node (XYZ)…`, and `Auto Fix Direction`.
- [x] Run focused Qt tests and verify Properties clears after deletion/model refresh.

### Task 4: Make edit modes select compatible entities (STANDARD wiring; mutation execution remains STRICT)

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `tests/ui/test_manual_edit_ui.py`
- Modify: `tests/ui/test_viewport_navigation.py`

**Interfaces:**
- Produces `_selection_filter_for_mode(mode: EditMode) -> SelectionFilter`.
- Produces `_focus_viewport() -> None`.

- [x] Add failing tests: Create/Draw/Move force Nodes; Delete forces Nodes + Members; Select preserves explicit filter.
- [x] Synchronize toolbar filter actions without intermediate conflicting signals.
- [x] Focus the VTK interactor and show exact next-click guidance when entering each mode.
- [x] Confirm mode highlighting/filter tests pass without executing a mutation.

### Task 5: Delete selection and orphan quick fix (STRICT / Full TDD)

**Files:**
- Modify: `src/staadprep/editing/manual_ops.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `tests/unit/test_manual_edit_commands.py`
- Modify: `tests/unit/test_manual_edit_roundtrip.py`
- Modify: `tests/ui/test_manual_edit_ui.py`
- Modify: `tests/ui/test_issue_console.py`
- Modify: `tests/ui/test_manual_edit_mouse.py`

**Interfaces:**
- Produces `build_delete_selection(model, node_keys, member_keys) -> RepairCommand`.
- Produces `MainWindow.delete_selected_entities() -> None`.

- [x] Write RED tests for one orphan Node, one Member, mixed selected Members plus newly orphaned Nodes, connected-Node rejection, exact confirmation text, Del shortcut, and exact Undo graph/revision restoration.
- [x] Implement deterministic member-first/node-second atomic deletion with no dangling incidence.
- [x] Route toolbar Delete, Delete-mode click, context Delete, orphan quick fix, and keyboard Del through the same MainWindow method.
- [x] Run command, UI, issue-console, and isolated real mouse tests GREEN.

### Task 6: Merge two split Members safely (STRICT / Full TDD)

**Files:**
- Modify: `src/staadprep/repair/commands.py`
- Modify: `src/staadprep/editing/manual_ops.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `tests/unit/test_repair_commands.py`
- Modify: `tests/unit/test_manual_split_ops.py`
- Modify: `tests/ui/test_manual_edit_ui.py`

**Interfaces:**
- Produces `MergeMembers(first_member: UUID, second_member: UUID)`.
- Produces `build_merge_selected_members(model, first, second) -> MergeMembers`.

- [x] Write RED exact-value tests for Split → Merge, retained UUID/direction/metadata, degree-two requirement, collinearity, branch rejection, invalid selection, and exact Undo restoration.
- [x] Implement fail-closed validation before mutation and one-revision apply/revert snapshots.
- [x] Add `Merge Members` action enabled only for exactly two selected Members.
- [x] Run independent graph-incidence tests and affected UI tests GREEN.

### Task 7: Repeat selected Member subgraphs (STRICT / Full TDD)

**Files:**
- Modify: `src/staadprep/editing/create_node.py`
- Modify: `src/staadprep/ui/create_node_dialog.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`
- Create: `tests/unit/test_member_translational_repeat.py`
- Modify: `tests/ui/test_precision_create_integration.py`
- Modify: `tests/ui/test_precision_viewport.py`

**Interfaces:**
- Produces `MemberTranslationalRepeatSpec(member_keys, dx, dy, dz, repeats)`.
- Produces `analyze_member_translational_repeat(...)` and `build_member_translational_repeat(...)`.

- [x] Write RED tests for one Member, a two-Member shared-node chain, metadata preservation, exact preview counts, duplicate-incidence rejection, collision resolution, atomic apply, and exact Undo.
- [x] Implement deterministic per-step Node mapping and Member recreation with no silent collision merge.
- [x] Let Translational Repeat dispatch to Node mode for one selected Node or Member mode for selected Members; reject mixed selection clearly.
- [x] Show exact preview counts and collision handling in the Member Repeat dialog and run unit/UI/renderer tests GREEN.

### Task 8: Prove Draw, Move, and Delete real interaction paths (STRICT / Full TDD)

**Files:**
- Modify: `scripts/smoke_manual_edit.py`
- Modify: `tests/ui/test_manual_edit_mouse.py`
- Modify: `tests/ui/test_manual_edit_real_smoke.py`

**Interfaces:**
- Consumes the mode-filter and deletion contracts from Tasks 4-5.

- [x] Add real projected-click tests for Draw existing endpoints, Move free, Move/Snap, toolbar Delete, and keyboard Del.
- [x] Assert exact UUID-coordinate-incidence graph after each command and after Undo.
- [x] Run every renderer file in an isolated Windows process and confirm no native crash or assertion failure.

### Task 9: Full review, documentation, and rebuilt release

**Files:**
- Modify: `docs/HANDOFF.md`
- Modify: `docs/CHECKLIST.md`
- Modify: `docs/INDEX.md`
- Modify: `docs/TASK_BOARD.md`
- Generated: `build/windows/final/app.dist/`
- Generated: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/`
- Generated: `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`

**Interfaces:**
- Produces a separate verified folder and ZIP; does not overwrite earlier releases.

- [x] Run targeted STRICT command/UI/renderer tests and inspect exact failures.
- [x] Run all unit + integration tests with a fresh project-local basetemp.
- [x] Run all UI tests through `scripts/test_ui_isolated.py` and aggregate 100% PASS.
- [x] Run Ruff, targeted strict mypy, `git diff --check`, and real viewport/manual-edit smokes.
- [x] Rebuild RBZ and Nuitka standalone; require report `mode="standalone" completion="yes"`.
- [x] Assemble under the historical path now preserved at `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/`, verify every manifest hash, no-Python/different-CWD/relocation/workflow gates, and launch a freshly extracted ZIP.
- [x] Stop for real user acceptance before committing the editing checkpoint.

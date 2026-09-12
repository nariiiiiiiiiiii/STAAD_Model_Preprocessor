# Crop to Selection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan inline. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Crop to Selection reliably frame selected Nodes and Members, including a single Node, without changing model state.

**Architecture:** Keep selection bounds derived from `StructuralViewport.scene` and keep the operation in `StructuralViewport.crop_to_selection()`. Replace the fixed near-zero padding for degenerate selections with a scale-aware minimum based on the full scene span, then verify the real PyVista camera in the isolated viewport smoke.

**Tech Stack:** Python 3.12, PySide6, PyVista/VTK, pytest.

**Spec:** `docs/superpowers/specs/2026-09-12-crop-to-selection.md`

## Global Constraints

- This is camera-only behavior; do not mutate the canonical model, hide geometry, alter selection, or change edit mode.
- Use the selected world-space Node/Member coordinates for the crop target.
- Keep all project-generated files inside the canonical project root.
- Do not run Nuitka, rebuild the RBZ, assemble a portable folder, or create a ZIP.
- Continue inline, one checkpoint at a time, then wait for owner acceptance before considering compilation.

---

### Task 1: Reproduce and fix single-Node crop framing

**Files:**
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `scripts/smoke_viewport.py`
- Modify: `tests/ui/test_structural_viewport.py`
- Modify: `tests/ui/test_viewport_navigation.py`
- Update: `docs/HANDOFF.md`, `docs/INDEX.md`, `docs/TASK_BOARD.md`, `docs/CHECKLIST.md`

**Interfaces:**
- `StructuralViewport.crop_to_selection() -> None` remains the public viewport action.
- `MainWindow.crop_selection_action` continues forwarding to `crop_to_selection()` only while a
  canonical model and selection exist.
- The smoke script reports `crop=pass` only when a selected Node becomes the camera focal target,
  crop distance is non-degenerate relative to the scene, and model revision remains unchanged.

- [x] **Step 1: Add the failing real-viewport regression.** In `scripts/smoke_viewport.py`, after
  model setup, fit the complete demo model, select only `scene.point_keys[0]`, capture camera
  distance and model revision, call `crop_to_selection()`, process Qt events, and assert the camera
  focal point is within `max(scene_span * 0.01, 1e-4)` of the selected Node and the resulting camera
  distance is greater than `max(scene_span * 0.005, 1e-4)`. Also assert the model revision is
  unchanged and print `crop=pass` on success.

- [x] **Step 2: Run the isolated viewport regression before implementation.**

Run: `..\..\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.tmp\tests\crop-selection-red tests\ui\test_structural_viewport.py -q`

Observed: FAIL as expected because the first selected Node produced a camera distance near
`0.000006692` on the demo frame, below the scale-aware minimum.

- [x] **Step 3: Add deterministic toolbar-action coverage.** In `tests/ui/test_viewport_navigation.py`,
  give `NavigationViewport` a `selection_changed` signal and `crop_to_selection()` call counter;
  set `window.current_model` to a one-Node model, emit one selected Node and assert the action
  enables and calls the viewport once; emit an empty selection and assert the action disables.

- [x] **Step 4: Use scale-aware crop padding.** In `StructuralViewport.crop_to_selection()`, compute
  the largest selected extent and the full scene extent. Use a selected-extent margin of 8% and a
  minimum margin of 2% of the scene span; when the whole scene has zero span, use a 1.0 world-unit
  reference. Set each crop bound to selected min/max plus/minus the resulting padding, then keep the
  existing `reset_camera`, clipping-range reset, and render sequence.

- [x] **Step 5: Verify focused viewport and navigation tests.**

Run: `..\..\.venv\Scripts\python.exe -m pytest -o addopts= --basetemp=.tmp\tests\crop-selection-green tests\ui\test_structural_viewport.py tests\ui\test_viewport_navigation.py -q`

Observed: viewport/navigation tests **9/9 PASS**; the real viewport emitted `crop=pass`; the
single-Node camera was non-degenerate and centered; the toolbar action enable/forward/disable
contract passed.

- [x] **Step 6: Run source checks and synchronize status.** Run Ruff on the four changed code/test
  files, strict mypy on `src/staadprep/viewer/widget.py`, and `git diff --check`. Record the exact
  result and leave the Save Blocked report as a separate, still-unresolved workflow diagnosis.
  The final combined viewport/navigation/Project-save suite was **15/15 PASS**, including the
  external Project JSON Open→Save-back regression and first-save Projects guard. Observed: Ruff
  PASS; strict mypy **0 issues** in `viewer/widget.py`; `git diff --check` PASS.

- [x] **Step 7: Commit this isolated checkpoint.** The checkpoint was committed as
  `fix: frame degenerate crop selections`.

```powershell
git add README.md src/staadprep/viewer/widget.py scripts/smoke_viewport.py `
  tests/ui/test_structural_viewport.py tests/ui/test_viewport_navigation.py `
  docs/HANDOFF.md docs/INDEX.md docs/TASK_BOARD.md docs/CHECKLIST.md `
  docs/superpowers/specs/2026-09-12-crop-to-selection.md `
  docs/superpowers/plans/2026-09-12-crop-to-selection.md
git commit -m "fix: frame degenerate crop selections"
```

Stop after this checkpoint for owner testing; do not compile.

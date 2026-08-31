# Post-T22 Repair Refresh, Properties, Save, and Exit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an Apply-before-OK repair workflow that refreshes without Undo, concise engineering Properties without UUIDs, canonical project JSON Save/Open, and confirmed application exit.

**Architecture:** Keep graph mutation in existing reversible `RepairCommand` implementations and add one testable dialog/orchestration layer around them. Keep entity formatting in `PropertiesPanel`, canonical persistence in `model/serialization.py`, and writable paths in `ProjectPaths`; MainWindow only coordinates actions, dirty state, dialogs, and refresh. Save/Open uses canonical project schema and never rewrites SketchUp Neutral JSON.

**Tech Stack:** Python 3.14, PySide6, PyVista/VTK, pytest/pytest-qt, existing `RepairHistory`, canonical schema-version-1 JSON, project-local path services, Nuitka standalone.

**Spec:** `docs/superpowers/specs/2026-08-31-post-t22-refresh-properties-save-design.md`

## Global Constraints

- This plan is **COMPILE, PORTABLE ASSEMBLY, PACKAGE VERIFICATION, AND USER ACCEPTANCE COMPLETE**. Tasks 1-6 and the added Project Explorer,
  Member Repeat preview, Local Axes, labels, toolbar, and corrected close behavior are
  source-verified and user accepted. Task 7 Steps 1-5 are complete after explicit compile approval.
  The isolated portable folder and ZIP are at `dist/post-t22-refresh-save-final/`; package-only
  verification is **7/7 PASS**. The user tested the package and reported **PASS** on 2026-08-31.
- Do not execute against an unresolved dirty editing-final checkpoint. First obtain user acceptance/disposition of the current package and preserve its tested state in Git, or create an explicitly approved isolated continuation worktree from that exact state.
- The Apply-before-OK integration for Delete/Merge/Quick Fix/Auto Fix is HIGH-RISK HR-2. Stop and obtain explicit STRICT / Full TDD approval before Task 2.
- Do not change Delete/Merge/Auto-Fix command algorithms, coordinate conversion, ReadyGate meaning, numbering policy, or `.STD` semantics.
- Every applied graph command executes exactly once through `RepairHistory`, remains audited, and remains exactly undoable.
- UUIDs remain stable internal identities and must not be displayed in Properties.
- Neutral JSON remains read-only input; canonical project Save/Open uses a distinct project JSON file under the active runtime root.
- All source/temp/test/build/package outputs remain under the canonical project root.
- Execute user-visible corrections incrementally. After each source checkpoint is testable, report it
  to the user and wait for the user's test result/instruction before advancing to the next correction.
- Do not run Nuitka or assemble a replacement standalone folder/ZIP during source iteration. After
  source acceptance and regression checks, stop at a separate pre-compile gate and require an
  explicit user instruction to compile.
- Do not start T23 or full T24 cleanup.

---

### Task 0: Resume gate and lock the tested baseline

**Files:**
- Read: `docs/HANDOFF.md`
- Read: `docs/CHECKLIST.md`
- Read: `docs/RISK_GATES.md`
- Read: `docs/superpowers/specs/2026-08-31-post-t22-refresh-properties-save-design.md`
- Read: `docs/superpowers/plans/2026-08-31-post-t22-refresh-properties-save.md`

**Interfaces:**
- Consumes: the exact accepted/dispositioned editing-final Git state.
- Produces: an isolated execution baseline and explicit authorization state for Task 2.

- [ ] **Step 1: Verify continuation state without modifying files**

Run:

```powershell
git status --short
git branch --show-current
git log -1 --oneline
```

Expected: the user has explicitly accepted or otherwise dispositioned the prior editing-final checkpoint; unrelated user changes are identified and preserved.

- [ ] **Step 2: Re-run the current focused baseline**

Run:

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit tests/integration -q --basetemp .tmp/tests/refresh-save-baseline
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope all --run-id refresh-save-baseline
..\..\.venv\Scripts\python.exe -m ruff check src tests scripts
git diff --check
```

Expected: 100% PASS before follow-up implementation begins.

- [x] **Step 3: Present the mandatory HR-2 approval gate**

Report the exact Apply-before-OK component, duplicate/stale-topology failure impact, STRICT level, exact graph/revision/audit/Undo tests, affected files, and ask:

```text
Proceed with STRICT / Full TDD for this high-risk component?
```

Expected: do not start Task 2 without explicit approval. Task 1 may be implemented independently only if the user resumes STANDARD work while withholding HR-2 approval.

---

### Task 1: Build the Apply-before-OK dialog contract without graph logic

**Files:**
- Create: `src/staadprep/ui/repair_apply_dialog.py`
- Create: `tests/ui/test_repair_apply_dialog.py`

**Interfaces:**
- Consumes: `apply_callback: Callable[[], bool]` supplied by MainWindow.
- Produces: `RepairApplyDialog(title: str, summary: str, apply_callback: Callable[[], bool], parent: QWidget | None = None)` and read-only `applied: bool`.

- [x] **Step 1: Write failing dialog-state tests**

Create tests that instantiate the dialog and assert:

```python
def test_repair_dialog_requires_apply_before_ok(qtbot) -> None:
    calls = 0

    def apply_once() -> bool:
        nonlocal calls
        calls += 1
        return True

    dialog = RepairApplyDialog("Delete", "Delete 1 Node", apply_once)
    qtbot.addWidget(dialog)
    assert dialog.ok_button.isEnabled() is False
    qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
    assert calls == 1
    assert dialog.applied is True
    assert dialog.apply_button.isEnabled() is False
    assert dialog.cancel_button.isEnabled() is False
    assert dialog.ok_button.isEnabled() is True
```

Also assert Cancel/window-close before Apply rejects without a callback, callback failure keeps OK disabled, and no path can invoke the callback twice.

- [x] **Step 2: Run the dialog tests and confirm RED**

Run:

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_repair_apply_dialog.py -q
```

Expected: collection/import failure because `repair_apply_dialog.py` does not exist.

- [x] **Step 3: Implement the minimal dialog**

Implement a `QDialog` with summary label and explicit Apply, OK, and Cancel buttons. Use this state transition:

```python
def _apply_once(self) -> None:
    if self._applied:
        return
    if not self._apply_callback():
        return
    self._applied = True
    self.apply_button.setEnabled(False)
    self.cancel_button.setEnabled(False)
    self.ok_button.setEnabled(True)

def reject(self) -> None:
    if self._applied:
        self.accept()
        return
    super().reject()
```

OK starts disabled. Apply is the only path to the callback. A false return does not change button state.

- [x] **Step 4: Run focused GREEN and lint**

Run:

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_repair_apply_dialog.py -q
..\..\.venv\Scripts\python.exe -m ruff check src/staadprep/ui/repair_apply_dialog.py tests/ui/test_repair_apply_dialog.py
```

Expected: all dialog tests pass and Ruff reports no errors.

- [ ] **Step 5: Commit the isolated dialog component**

```powershell
git add src/staadprep/ui/repair_apply_dialog.py tests/ui/test_repair_apply_dialog.py
git commit -m "feat: add explicit repair apply dialog"
```

---

### Task 2: Route Delete, Merge, Quick Fix, and Auto Fix through exact-once refresh (STRICT)

**Files:**
- Modify: `src/staadprep/ui/main_window.py:610-765`
- Modify: `src/staadprep/ui/main_window.py:988-1005`
- Modify: `src/staadprep/ui/main_window.py:1255-1318`
- Modify: `src/staadprep/ui/main_window.py:1355-1387`
- Test: `tests/ui/test_manual_edit_ui.py`
- Test: `tests/ui/test_model_controls.py`
- Create: `tests/ui/test_repair_apply_refresh.py`
- Create: `tests/ui/test_repair_apply_refresh_vtk.py`

**Interfaces:**
- Consumes: `RepairApplyDialog` and existing `RepairCommand` builders.
- Produces: `MainWindow._run_repair_apply_dialog(command: RepairCommand, *, title: str, summary: str) -> bool` and `MainWindow._refresh_after_mutation() -> None`.

- [x] **Step 1: Write RED exact-once graph tests**

For Delete, Merge, destructive Quick Fix, Auto Fix All, and Auto Fix Selected, automate Apply then OK and assert:

```python
before_revision = model.revision
before_audit = len(window.repair_history.audit.entries)

qtbot.mouseClick(dialog.apply_button, Qt.MouseButton.LeftButton)
assert model.revision == before_revision + 1
assert len(window.repair_history.audit.entries) == before_audit + 1

qtbot.mouseClick(dialog.ok_button, Qt.MouseButton.LeftButton)
assert model.revision == before_revision + 1
assert len(window.repair_history.audit.entries) == before_audit + 1
```

Assert final exact UUID-coordinate-incidence state, project explorer counts, viewport model/scene counts, validation counts, empty stale Properties, Undo enabled, and exact Undo restoration. Cancel-before-Apply must preserve the entire serialized model byte-for-byte.

- [x] **Step 2: Write the real VTK refresh regression**

Build a visible `StructuralViewport`, select and delete an orphan Node, then merge a split pair in a fresh model. After Apply+OK and without Undo, assert actor/scene point and member counts match the canonical model and `plotter.render_window` remains valid.

- [x] **Step 3: Run focused tests and confirm RED**

Run:

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_repair_apply_refresh.py tests/ui/test_repair_apply_refresh_vtk.py tests/ui/test_manual_edit_ui.py tests/ui/test_model_controls.py -q
```

Expected: failures identify the old Yes/No confirmation path and missing Apply/OK orchestration.

- [x] **Step 4: Implement centralized command execution and refresh**

Implement one callback that executes once and synchronizes immediately:

```python
def apply_once() -> bool:
    try:
        self.repair_history.execute(command)
    except (ValueError, RuntimeError) as exc:
        self.statusBar().showMessage(f"Repair rejected: {exc}")
        return False
    self._refresh_after_mutation()
    return True
```

After `dialog.exec()`, if `dialog.applied`, call `_refresh_after_mutation()` once more and return true. `_refresh_after_mutation()` calls `refresh_validation()`, explicitly renders the viewport when supported, clears stale edit preview/selection, updates history actions, and leaves the canonical model unchanged.

Route all five command families through this method. Remove only their redundant Yes/No destructive prompts; keep invalid-selection/no-op rejection before dialog construction.

- [x] **Step 5: Confirm GREEN and exact Undo**

Run the focused command from Step 3 and require every graph/revision/audit/Undo assertion to pass.

- [x] **Step 6: Run independent affected STRICT regression**

Run:

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_delete_selection.py tests/unit/test_merge_members.py tests/unit/test_member_translational_repeat.py tests/unit/test_repair_history.py tests/ui/test_issue_repair_smoke.py tests/ui/test_manual_edit_mouse.py -q
```

Expected: no existing mutation, incidence, or Undo contract regresses.

- [x] **Step 6a: Fix repeated multi-Orphan Quick Fix selection synchronization**

Real user testing accepted Apply→OK but exposed a stale Issue Console row after the first of two
Orphan Node repairs. Added a RED/GREEN regression for two sequential Quick Fix cycles plus two exact
Undo operations. `IssueConsole.set_issues()` now clears visual/current selection atomically before
rebuild. Focused follow-up regression: **17/17 PASS**; Ruff and strict mypy pass. Real user retest
was accepted before Task 3.

- [ ] **Step 7: Commit the STRICT repair orchestration**

```powershell
git add src/staadprep/ui/main_window.py tests/ui/test_repair_apply_refresh.py tests/ui/test_repair_apply_refresh_vtk.py tests/ui/test_manual_edit_ui.py tests/ui/test_model_controls.py
git commit -m "fix: refresh applied repairs without undo"
```

---

### Task 3: Render exact Node and Member engineering Properties

**Files:**
- Modify: `src/staadprep/ui/panels.py:160-235`
- Modify: `tests/ui/test_selection_properties.py`

**Interfaces:**
- Consumes: `ProjectModel`, one selected Node UUID or one selected Member UUID.
- Produces: deterministic Properties text containing no UUID/source identity.

- [x] **Step 1: Replace current expectations with exact RED text contracts**

Assert Node text contains:

```text
Selected entity

Type Node
Node No. 16
X 1.25 m
Y 3 m
Z -0.5 m
```

Assert Member text contains Member No., start/end Node No. and separate X/Y/Z lines, Length, and `Group / Layer`. Assert `UUID`, UUID strings, and `Source` are absent from both texts.

- [x] **Step 2: Run the Properties tests and confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_selection_properties.py -q
```

Expected: current UUID/endpoint formatting violates the new assertions.

- [x] **Step 3: Implement the exact presentation**

Keep `_number()` and add one coordinate formatter:

```python
@staticmethod
def _coordinate(value: float) -> str:
    return f"{value:g} m"
```

Use `member.group or "—"` for `Group / Layer`. Do not change `Node`, `Member`, topology, serialization schema, or internal UUID use.

- [x] **Step 4: Run GREEN plus selection clearing regression**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_selection_properties.py tests/ui/test_viewport_navigation.py -q
```

Expected: exact fields pass; Properties still clear after model refresh/deletion.

Result: exact RED/GREEN Properties contract passed; affected regression **15/15 PASS**, Ruff clean,
and strict mypy **0 issues** for `panels.py`. User development-app acceptance was recorded on
2026-08-31.

- [ ] **Step 5: Commit Properties presentation**

```powershell
git add src/staadprep/ui/panels.py tests/ui/test_selection_properties.py
git commit -m "fix: show engineering selection properties"
```

---

### Task 4: Add centralized project-file paths and atomic canonical JSON persistence

**Files:**
- Modify: `src/staadprep/paths.py`
- Modify: `src/staadprep/model/serialization.py`
- Modify: `tests/unit/test_paths.py`
- Modify: `tests/unit/test_portable_paths.py`
- Modify: `tests/unit/test_serialization.py`

**Interfaces:**
- Produces: `ProjectPaths.projects: Path` and `save_project_atomic(model: ProjectModel, path: Path, *, temp_dir: Path) -> None`.
- Consumes: existing deterministic `save_project()` and `load_project()` schema-version-1 behavior.

- [x] **Step 1: Write RED path-layout tests**

Assert development paths resolve projects to `artifacts/projects`, runtime paths resolve projects to `Data/Projects`, `ensure_layout()` creates the directory, and `assert_inside_project()` still rejects escapes.

- [x] **Step 2: Write RED atomic-save tests**

Assert successful atomic save round-trips exact nodes, members, metadata, numbering, UUIDs, and revision. Patch `os.replace` to fail and assert an existing destination remains byte-identical and the project-local temporary file is cleaned.

- [x] **Step 3: Run path/serialization tests and confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_paths.py tests/unit/test_portable_paths.py tests/unit/test_serialization.py -q
```

Expected: missing `projects` property and `save_project_atomic` failures.

- [x] **Step 4: Implement the project path and atomic wrapper**

Add `projects` to the immutable path contract and create it in `generated_dirs`. Refactor the existing deterministic payload formatting into an internal `_project_json_text(model: ProjectModel) -> str`, keep `save_project()` backward-compatible, and implement atomic save as:

```python
temp_path = temp_dir / f".{path.name}.{uuid4().hex}.tmp"
try:
    with temp_path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(_project_json_text(model))
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp_path, path)
finally:
    temp_path.unlink(missing_ok=True)
```

Resolve both destination and temp directory through `ProjectPaths` before MainWindow invokes this function.

- [x] **Step 5: Run GREEN, Ruff, and strict mypy**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_paths.py tests/unit/test_portable_paths.py tests/unit/test_serialization.py -q
..\..\.venv\Scripts\python.exe -m ruff check src/staadprep/paths.py src/staadprep/model/serialization.py tests/unit/test_paths.py tests/unit/test_portable_paths.py tests/unit/test_serialization.py
..\..\.venv\Scripts\python.exe -m mypy --strict --follow-imports=silent src/staadprep/paths.py src/staadprep/model/serialization.py
```

- [ ] **Step 6: Commit persistence plumbing**

```powershell
git add src/staadprep/paths.py src/staadprep/model/serialization.py tests/unit/test_paths.py tests/unit/test_portable_paths.py tests/unit/test_serialization.py
git commit -m "feat: save canonical projects atomically"
```

---

### Task 5: Wire Save Project JSON, Open Project JSON, and dirty state

**Files:**
- Modify: `src/staadprep/ui/main_window.py:110-430`
- Modify: `src/staadprep/ui/main_window.py:1105-1195`
- Modify: `src/staadprep/ui/main_window.py:1255-1278`
- Modify: `tests/ui/test_import_routes.py`
- Create: `tests/ui/test_project_save_ui.py`

**Interfaces:**
- Consumes: `ProjectPaths.projects`, `save_project_atomic()`, and `load_project()`.
- Produces: `save_project_action`, `open_project_action`, `save_current_project() -> bool`, `open_project_json(path: Path) -> ProjectModel`, and `has_unsaved_changes() -> bool`.

- [x] **Step 1: Write RED Save/Open action tests**

Assert Import Model includes `Open Project JSON`, workflow toolbar includes `Save Project JSON`, shortcut is `Ctrl+S`, Save is disabled without a canonical model, and first Save requests a path rooted under `projects`.

- [x] **Step 2: Write RED round-trip and dirty-state UI tests**

Load Neutral JSON, mutate one Node through history, Save, reopen into a fresh MainWindow, and compare deterministic serialized payloads. Assert:

```python
assert window.has_unsaved_changes() is True
assert window.save_current_project() is True
assert window.has_unsaved_changes() is False
assert window.windowTitle().endswith("*") is False
```

After another command, the title gains `*`; exact Undo to the saved revision clears it. Reject outside-project Save/Open paths with an actionable `Save Blocked` or `Open Blocked` message.

- [x] **Step 3: Run tests and confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_project_save_ui.py tests/ui/test_import_routes.py -q
```

- [x] **Step 4: Implement MainWindow persistence state**

Add:

```python
self._current_project_path: Path | None = None
self._saved_revision: int | None = None

def has_unsaved_changes(self) -> bool:
    model = self.current_model
    return model is not None and (
        self._current_project_path is None
        or self._saved_revision != model.revision
    )
```

First Save uses the injected/default chooser and `.staadprep.json` suffix, then calls atomic save with `_project_paths.tmp`. Open asserts the file lies within `_project_paths.projects`, calls `load_project()`, attaches it through `set_canonical_model()`, and records path/revision. Neutral/DXF imports clear current project path and saved revision.

- [x] **Step 5: Confirm Save/Open GREEN**

Run the Step 3 command and `tests/unit/test_serialization.py`. Require exact model round-trip and no Neutral JSON overwrite.

- [ ] **Step 6: Commit Save/Open UI**

```powershell
git add src/staadprep/ui/main_window.py tests/ui/test_project_save_ui.py tests/ui/test_import_routes.py
git commit -m "feat: add project json save and open"
```

---

### Task 6: Confirm application exit without blocking packaged smoke

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/app.py:50-78`
- Create: `tests/ui/test_exit_confirmation.py`
- Modify: `tests/integration/test_packaged_paths.py`

**Interfaces:**
- Produces: injected `confirm_exit: Callable[[bool], bool]`, `MainWindow.closeEvent(event: QCloseEvent)`, and an explicit smoke allow-close callback.
- Consumes: `has_unsaved_changes()` from Task 5.

- [x] **Step 1: Write RED close-event tests**

Assert No ignores the close event, Yes accepts it, dirty state is passed to the confirmation callback, and a clean loaded window still asks once. Test the default dialog title/text and default No button by replacing only the dialog function.

- [x] **Step 2: Run exit tests and confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_exit_confirmation.py -q
```

- [x] **Step 3: Implement the close contract**

Use:

```python
def closeEvent(self, event: QCloseEvent) -> None:
    if self._confirm_exit(self.has_unsaved_changes()):
        event.accept()
        return
    event.ignore()
```

The production default uses Yes/No with No selected. `app.main()` passes `lambda _dirty: True` only when `STAADPREP_SMOKE_MS` is explicitly set, keeping packaged smoke non-interactive.

- [x] **Step 4: Run GREEN and packaged launch gate**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/ui/test_exit_confirmation.py tests/integration/test_packaged_paths.py -q --basetemp .tmp/tests/exit-confirmation
```

Expected: interactive tests prove the prompt; sanitized-PATH packaged launch exits 0 without a modal hang.

- [ ] **Step 5: Commit exit confirmation**

```powershell
git add src/staadprep/ui/main_window.py src/staadprep/app.py tests/ui/test_exit_confirmation.py tests/integration/test_packaged_paths.py
git commit -m "feat: confirm application exit"
```

---

### Task 7: Full verification, pre-compile stop, standalone rebuild, and acceptance stop

**Files:**
- Modify: `README.md`
- Modify: `docs/PROJECT_SPEC.md`
- Modify: `docs/ARCHITECTURE.md`
- Modify: `docs/WORKFLOW.md`
- Modify: `docs/CHECKLIST.md`
- Modify: `docs/RISK_GATES.md`
- Modify: `docs/HANDOFF.md`
- Modify: `docs/INDEX.md`
- Modify: `docs/TASK_BOARD.md`
- Generated: `build/windows/final/app.dist/`
- Generated: `dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable/`
- Generated: `dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`

**Interfaces:**
- Consumes: all completed tasks and accepted exact behavior.
- Produces: isolated folder/ZIP for real user acceptance; no overwrite of editing-final.

- [x] **Step 1: Run all source regression with fresh local temp paths**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit tests/integration -q --basetemp .tmp/tests/refresh-save-full
..\..\.venv\Scripts\python.exe scripts/test_ui_isolated.py --scope all --run-id refresh-save-full
```

Expected: 100% PASS, including every renderer file in a separate Windows process.

Result: **332/332 source unit+integration PASS** after excluding only the three explicitly
package-dependent `test_packaged_paths.py` gates; **102/102 lightweight UI PASS** and **38/38
isolated VTK UI PASS**. The package-only suite subsequently ran against the new package and
passed **7/7**.

- [x] **Step 2: Run static and diff gates**

```powershell
..\..\.venv\Scripts\python.exe -m ruff check src tests scripts
..\..\.venv\Scripts\python.exe -m mypy --strict --follow-imports=silent src/staadprep/ui/main_window.py src/staadprep/ui/panels.py src/staadprep/ui/repair_apply_dialog.py src/staadprep/model/serialization.py src/staadprep/paths.py src/staadprep/app.py
git diff --check
```

Result: Ruff PASS for `src`, `tests`, and `scripts`; strict mypy reports **0 issues in 6 source
files**; `git diff --check` PASS with line-ending notices only.

- [x] **Step 3: Run real Windows behavior smokes**

Run viewport, manual-edit, and precision-create smokes, then add one project-save smoke that applies a mutation, saves, reopens, compares exact graph/revision, and closes through the injected non-interactive path.

Result: viewport, manual-edit, precision-create, orientation, issue-repair, and DXF-preview real
Windows smokes all exit 0; focused project Save/Open UI smoke is **5/5 PASS**.

- [x] **Step 4: Stop at the mandatory pre-compile approval gate**

Report the complete source-level evidence and provide the development launch/test instructions.
Wait for the user to finish source testing and explicitly authorize compilation. Do not run
`scripts/build_windows.ps1`, overwrite `build/windows/final/app.dist`, or create a new release
folder/ZIP before that approval.

Historical Step-4 stop was satisfied by the user's explicit authorization. Compile Step 5 is now
complete; no replacement portable folder or ZIP has been assembled.

- [x] **Step 5: Rebuild the standalone application after explicit approval**

```powershell
pwsh -ExecutionPolicy Bypass -File scripts/build_windows.ps1 -Python "..\..\.venv\Scripts\python.exe"
```

Require `build/windows/final/nuitka-report.xml` to contain `mode="standalone" completion="yes"`.

Result: Nuitka **4.2** with Python **3.14.3 x64** and MSVC **14.5** completed successfully. The
report contains `mode="standalone" completion="yes"`; executable size is **160,239,616 bytes** and
SHA-256 is `1C7BB68D12BEFA8A1DBDC5A8A18B031A1E19AEFCFB91C7567441E79DB88F4470`.

- [x] **Step 6: Verify exact contents of the assembled isolated release**

The isolated release was assembled successfully at `dist/post-t22-refresh-save-final/`. Package-only
executable/no-Python/relocation, manifest, workflow, and freshly extracted-ZIP verification passed
**7/7** against the new release.

```powershell
..\..\.venv\Scripts\python.exe scripts/assemble_portable.py --standalone-dir build/windows/final/app.dist --rbz build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz --dist-root dist/post-t22-refresh-save-final
```

Run no-Python/different-CWD, relocation/reopen, packaged READY/STD/report, manifest size/hash, and freshly extracted-ZIP launch gates. Confirm `Data/Projects` exists and Save/Open remains inside it.

Use the exact new package root for package-path gates:

```powershell
$env:STAADPREP_PACKAGE_ROOT = (Resolve-Path 'dist/post-t22-refresh-save-final/STAAD_Model_Preprocessor_0.1.0_win64_portable').Path
..\..\.venv\Scripts\python.exe -m pytest tests/integration/test_package_manifest.py tests/integration/test_packaged_paths.py tests/integration/test_packaged_workflow_smoke.py -q --basetemp .tmp/tests/refresh-save-package
```

- [x] **Step 7: Synchronize every status-bearing Markdown file**

Record exact PASS counts, artifact sizes/hashes, package path, HIGH-RISK evidence, Save/Open schema contract, exit behavior, and remaining user acceptance. Preserve historical evidence and mark the prior editing-final package superseded only after the new package is verified.

- [x] **Step 8: Stop for real package acceptance before final checkpoint commit**

The user tested the rebuilt package and reported **PASS** on 2026-08-31. Do not start T23.

- [ ] **Step 9: Commit acceptance documentation after user approval**

```powershell
git add README.md docs
git commit -m "docs: record refresh and save acceptance"
```

## Self-review result

- Spec coverage: all four user requests map to Tasks 1-6; package and documentation gates are in Task 7.
- Placeholder scan: no implementation step contains deferred markers or unspecified error behavior.
- Type consistency: dialog callback returns `bool`; MainWindow repair runner returns `bool`; project save/open uses `Path`; dirty state uses saved `revision`; exit callback consumes `bool` dirty state.
- Scope boundary: no topology algorithm, coordinate conversion, numbering, ReadyGate, or `.STD` semantic change is planned.


## 2026-08-31 handoff addendum — close defect

- Save/Open UX, Global Axis XYZ, and Exit confirmation UI were user accepted before the latest defect report.
- Real-user defect was `X -> Yes` not closing the development application.
- Root-cause hardening applied: `_confirm_exit_dialog()` now uses equality for the native Qt Yes result; accepted `closeEvent()` delegates to `QMainWindow.closeEvent()`.
- TDD: native integer-equivalent Yes regression failed before the fix and passes after it. Exit suite: **4/4 PASS**.
- Static evidence: Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Latest fix status: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**. Real retest confirmed `No` keeps the app open and `Yes` closes it.
- Task 7 source verification is **COMPLETE**: **332/332 source unit+integration**, **140/140 UI**,
  real Windows smokes, Ruff, strict mypy, and diff checks pass. The package-only suite is also
  **7/7 PASS** against the new assembled package.
- The user explicitly authorized compile step 1 and Nuitka compilation is complete. The isolated
  portable folder and ZIP were assembled under `dist/post-t22-refresh-save-final/`; Step 6
  package-only verification is **7/7 PASS**. **STOP** for real user acceptance before final
  checkpoint commit.

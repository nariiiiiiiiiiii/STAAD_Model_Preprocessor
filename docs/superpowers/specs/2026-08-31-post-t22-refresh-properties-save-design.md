# Post-T22 Repair Refresh, Properties, Save, and Exit Design

**Status:** SOURCE FEATURE SCOPE USER ACCEPTED / FULL SOURCE VERIFIED — Nuitka compile step 1,
portable assembly, ZIP creation, package-only verification, and real user package acceptance
complete (**7/7 PASS**, user accepted 2026-08-31)
**Date:** 2026-08-31
**Risk:** Mixed — STANDARD UI/save/exit work plus STRICT HR-2 repair-command orchestration

## Goal

Remove the need to press Undo merely to make repaired geometry refresh, present useful engineering properties without exposing UUIDs, confirm application exit, and let the user save/reopen the edited canonical model as project JSON.

## Diagnosed current behavior

1. Delete, Merge, Quick Fix, and direction Auto Fix execute through `RepairHistory` and call `refresh_validation()`, but destructive confirmation is a simple Yes/No `QMessageBox`. There is no visible Apply state and no single dialog contract proving that mutation, validation, viewport rebuild, Properties reset, explorer counts, and history controls have all synchronized before the dialog closes.
2. `PropertiesPanel.set_selection()` currently renders entity UUIDs, endpoint UUIDs, and source references. Member endpoint coordinates are not shown.
3. `save_project()` and `load_project()` already serialize canonical schema version 1, but MainWindow exposes neither Save nor Open Project. The current writer writes directly to its destination rather than replacing atomically.
4. MainWindow has no exit-confirmation `closeEvent`. Automated packaged launch uses `STAADPREP_SMOKE_MS`, so a real close prompt must have an explicit non-interactive test bypass.

## Binding behavior

### 1. Apply-before-OK repair dialog

Delete Selected, Merge Members, supported Quick Fix, Auto Fix Direction All, and Auto Fix Direction Selected use one modal repair dialog:

- **Apply** executes the already-built reversible `RepairCommand` exactly once.
- Apply immediately runs validation and viewport/UI synchronization so the hidden main window is never left stale.
- Successful Apply disables Apply and Cancel and enables **OK**.
- **OK** performs one final idempotent UI refresh and closes the dialog; it must not execute the command again.
- Cancel or window-close before Apply leaves model, revision, audit, and history unchanged.
- Window-close after Apply is treated as OK so an applied mutation cannot leave the refresh sequence incomplete.
- A rejected command keeps OK disabled and displays the exact rejection without mutating the model.
- Undo remains available after Apply, but it is not required to refresh the display.

No graph algorithm changes are permitted. Delete/Merge/Quick-Fix/Auto-Fix continue to use the existing command builders and `RepairHistory`.

### 2. Engineering Properties without UUIDs

Single Node selection shows only:

- `Type Node`
- `Node No.`
- `X`, `Y`, and `Z` in metres

Single Member selection shows only:

- `Type Member`
- `Member No.`
- Start Node No. plus Start X/Y/Z in metres
- End Node No. plus End X/Y/Z in metres
- Length in metres
- `Group / Layer`

The canonical `Member.group` value remains the V1 source group/layer field. No model/schema change is introduced merely to split Group and Layer. UUID and source reference remain available internally but are not rendered in Properties. Mixed selection continues to show counts only.

### 3. Canonical project Save/Open

- Add **Save Project JSON** with shortcut `Ctrl+S`.
- First Save opens a file chooser rooted at the centralized project-files directory; later Save writes the same file.
- Add **Open Project JSON** under Import Model so the saved canonical file is usable in the application.
- Use `.staadprep.json` as the suggested suffix while still reading schema-version-1 JSON.
- Never overwrite the SketchUp Neutral JSON input. Neutral input and canonical project JSON are different schemas.
- All project JSON paths remain below the active project/runtime root. Packaged paths resolve to `Data/Projects`; development paths resolve to `artifacts/projects`.
- Saving uses a project-local temporary file, flush + `fsync`, then `os.replace`; failure leaves the previous destination intact and removes the temporary file where possible.
- Track current project path and saved revision. Imported Neutral/DXF models have no current project path until first Save. Opening/saving a project establishes the saved revision.

### 4. Exit confirmation

- Closing the main window asks `Exit STAAD Model Preprocessor?` with Yes/No and defaults to No.
- If a canonical model differs from the saved revision or has never been saved, the message also states that unsaved changes will be lost.
- Yes accepts the close event; No ignores it.
- Automated smoke mode injects an allow-close callback explicitly. Production does not inspect a generic environment variable inside `closeEvent`.

## Risk gate

Repair dialog orchestration is HIGH-RISK HR-2 because duplicate execution, stale command state, or incorrect timing can silently mutate analytical connectivity twice or leave the UI inconsistent with the canonical graph.

Before implementing the STRICT portion, report:

1. Component: Apply-before-OK orchestration for Delete/Merge/Quick Fix/Auto Fix.
2. Failure impact: duplicate/missing nodes or members, hidden stale topology, incorrect Undo/audit state.
3. Level: STRICT / Full TDD.
4. Verification: RED/GREEN exact graph/revision/audit/Undo assertions, dialog state tests, isolated real VTK refresh tests, affected regression, package gates.

Explicitly ask: **Proceed with STRICT / Full TDD for this high-risk component?**

The user explicitly approved STRICT / Full TDD and resumed item 1 on 2026-08-31. Apply/OK,
repeated-Orphan handling, engineering Properties, Project Explorer selection, Member Repeat/Local
Axes, canonical Save/Open, and corrected Exit confirmation are implemented, source-verified, and
user accepted. Task 7 full source verification is complete with **332/332 source
unit+integration** and **140/140 UI** passing, plus real Windows smokes and static gates. The work
passed the separate pre-compile gate and the user explicitly authorized Nuitka compile step 1,
which completed successfully. Portable assembly and ZIP creation then completed under
`dist/post-t22-refresh-save-final/`; package-only verification requires the next explicit user
instruction.

## Out of scope

- changing Delete/Merge/Auto-Fix topology algorithms;
- changing coordinate conversion or `.STD` export semantics;
- exposing or editing UUIDs in the UI;
- overwriting SketchUp Neutral JSON with canonical project schema;
- autosave, background save, recent-file database, cloud sync, or installer integration;
- starting T23 or full T24 cleanup.

## Acceptance summary

- Apply then OK leaves viewport, validation, Properties, explorer counts, history buttons, revision, and audit synchronized without Undo.
- Properties match the exact Node/Member field lists above and contain no `UUID` text.
- Save/Open round-trips the exact canonical model and metadata through project-local atomic JSON.
- Exit always asks in production and never blocks automated packaged smoke.


## 2026-08-31 implementation handoff note

Implementation now includes the approved Save/Open and Exit UX. A real-user close defect was found
after the initial Exit confirmation acceptance: selecting `Yes` did not close the window. The source
hardening now treats native Qt Yes results by equality and forwards accepted close events to the
QMainWindow base close handler. Focused exit regression is 4/4 PASS and the user accepted the real
`No`/`Yes` retest. Full source verification, Nuitka compile step 1, portable assembly, and ZIP
creation and package-only verification are complete (**7/7 PASS**); real user package acceptance
is **PASS** (2026-08-31).

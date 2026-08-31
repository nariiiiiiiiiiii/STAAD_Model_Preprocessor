Status: LOCKED for V1 unless the user explicitly requests a redesign. Current post-T22 source
implementation conforms to this baseline with the user-requested Reset/Crop, selection Properties,
context actions, and active-mode additions; source behavior is user accepted and full source
verification is complete. Replacement packaging awaits explicit compile approval.

The approved baseline remains the dark engineering desktop application, extended on 2026-08-28 with focused manual analytical editing and SketchUp-style viewport controls.

## Main composition

```text
+--------------------------------------------------------------------------------+
| STAAD Model Preprocessor | Project                         window controls       |
+--------------------------------------------------------------------------------+
| FILE | EDIT | MODEL | VIEW | TOOLS                                               |
+----------------------+--------------------------------------+--------------------+
| PROJECT EXPLORER     |                                      | PROPERTIES         |
| Files                |                                      | Selected entity    |
| Model Tree           |            3D VIEWPORT               +--------------------+
| Structures           |                                      | VALIDATION         |
|                      | nodes/members + ghost previews        | PASS/WARN/ERROR    |
| MODEL SUMMARY        | labels + local-X + inference          +--------------------+
| Nodes/Members/etc.   |                                      | QUICK FIX          |
|                      |                                      | Repair actions     |
+----------------------+--------------------------------------+--------------------+
| ISSUE CONSOLE: Type | ID | Description | Action                                  |
+--------------------------------------------------------------+-----------------+
| mode / inference / unit / axis / counts                      | MODEL STATUS    |
+--------------------------------------------------------------------------------+
```

## Toolbar / ribbon grouping

### FILE
- Import Model
  - SketchUp Bridge / `Send to STAAD Prep` inbox — V1 first-class route; SketchUp extension UI stays lightweight with one primary send action
  - Import DXF `.dxf` — V1 first-class direct route
  - Direct SKP `.skp` — future optional when C SDK access is available
- Save
- Export STD

### EDIT
- Select
- Create Node
- Draw Member
- Move / Snap Node
- Delete

### MODEL
- Auto Node No.
- Auto Member No.
- Auto Number All
- Auto Fix Axis
- Auto Fix Selected
- Flip Selected
- Set Direction

### VIEW
- Node No.
- Member No.
- Local-X
- Coordinates
- Fit Model

### TOOLS
- Measure
- Validate

## Interaction baseline

### Explicit edit modes

Default mode is `SELECT`.

`SELECT` must never move structural geometry by mouse drag.

Geometry-changing modes are explicit:
- `CREATE NODE`
- `DRAW MEMBER`
- `MOVE / SNAP NODE`
- `DELETE`
- `SET DIRECTION`

Ghost preview is shown before commit. `Esc` cancels the active preview with no canonical model mutation.

### SketchUp-style navigation

- Middle Mouse drag = Orbit
- Shift + Middle Mouse drag = Pan
- Mouse Wheel = Zoom
- `Shift+Z` = Fit / Zoom Extents

Navigation is an override: it works while an edit tool is active and returns to that edit operation when navigation ends.

Preferred orbit pivot:
1. selected entity center,
2. entity/cursor focal hit,
3. current camera focal point.

### Selection

- Left click = select exact entity.
- Ctrl + Left click = toggle additive selection.
- Node/Member selection filters are available.
- Overlapping entities can be cycled/chosen explicitly.
- Double-click = Focus / Zoom Selected.
- Context menu shows only valid operations for entity type.

### Issue-first workflow

Selecting an issue must:
1. select the affected model entity,
2. zoom/highlight the location,
3. show properties/context,
4. show valid Quick Fix actions,
5. allow transition to a manual edit tool when automatic repair is not appropriate,
6. keep the issue selected until repaired/dismissed/changed.

### Create Node dialog

Supports:
- Exact XYZ,
- Relative to Selected Node,
- Translational Repeat.

Relative layout baseline:

```text
Reference Node: 21
Reference XYZ: ...

STAAD X            [ + / - ] [ distance ] m
STAAD Y (Vertical) [ + / - ] [ distance ] m
STAAD Z            [ + / - ] [ distance ] m

Result XYZ: ...

[ ] Create Member
    From: Reference Node
    To:   New Node

[ Preview ] [ Create ] [ Cancel ]
```

Repeat adds:
- Repeat Count = number of NEW positions,
- Connection Mode = Consecutive / From Reference,
- proposed/reused/skipped counts,
- last-node coordinate.

### Model controls

Numbering actions show an Old -> New mapping preview before Apply.

Set Direction workflow:

```text
Select one Member
 -> Set Direction
 -> click endpoint that shall become Start (i)
 -> preview Local-X arrow
 -> Apply / Cancel
```

### View labels

Toggleable:
- Node Number
- Member Number
- Local-X Arrow
- Coordinates
- XYZ triad
- optional working grid/plane

### Status

- green: PASS/ready,
- amber: warning/review,
- red: error/blocking,
- blue/neutral: informational.

Do not use color as the only status signal; always pair with text/icon.

During editing, status bar also shows:
- active Edit Mode,
- current inference target,
- axis lock,
- current/preview coordinate or distance where relevant.

## 3D viewport functional baseline

Must support:
- SketchUp-style orbit/pan/zoom/fit,
- select node/member,
- selection filters,
- overlap cycling,
- isolate structure,
- show XYZ triad,
- optional grid/working plane,
- issue highlights,
- node/member number labels,
- coordinate labels,
- local-X arrows,
- ghost Node/Member previews,
- snap/inference labels,
- axis locks,
- direct analytical node/member edit modes.

## V1 CAD boundary

The viewport is a focused analytical line-model editor.

Do NOT add in V1:
- arbitrary Rotate geometry,
- Mirror,
- full Copy Array / radial array,
- Trim,
- Extend,
- Offset,
- solids/surfaces,
- section-shape modeling.

Translational Repeat is allowed only as the approved node/member generation workflow.

## Key screens/mockups

Existing implementation references remain:
- `ui/main_dashboard.svg`
- `ui/unit_check.svg`
- `ui/issue_repair.svg`

Manual-editing screens may extend the toolbar/right panels/dialogs while preserving the main composition and dark engineering hierarchy.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect: clicking window `X` and choosing `Yes` did not close the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **102/102
  lightweight UI PASS**, **38/38 isolated VTK UI PASS**, six real Windows source smokes exit 0,
  focused Save/Open **5/5 PASS**, Ruff PASS, strict mypy 0 issues, and diff check PASS.
- The package-only verification suite was run after the user authorized step 3: **7/7 PASS**.
  Nuitka compilation, portable assembly, and ZIP creation completed under
  `dist/post-t22-refresh-save-final/`; real package acceptance is **PASS** (2026-08-31).

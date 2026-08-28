Status: LOCKED for V1 unless the user explicitly requests a redesign.

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
  - SketchUp `.skp` — primary
  - DXF `.dxf` — fallback
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

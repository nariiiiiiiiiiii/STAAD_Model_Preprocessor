# Post-T22 Usability Patch Design

**Date:** 2026-08-30
**Status:** Requirements 1-2 user accepted; requirements 3-9 rebuilt/verified and preserved as historical evidence under `DEL/standalone-archive-20260831/post-t22-ux-final/`. Their separate package acceptance is superseded by the consolidated editing-final checkpoint in `2026-08-30-post-t22-editing-corrections-design.md`.
**Risk:** STANDARD — UI, picking-coordinate, export-name, and packaging changes only

## Goal

Apply the nine usability corrections found while testing the T22 portable package without changing canonical geometry, topology, repair commands, ReadyGate semantics, or STAAD `.STD` export semantics.

## Requirement decisions

| # | Requirement | Binding design |
|---|---|---|
| 1 | Explain the RBZ and its buttons | Open a compact `UI::HtmlDialog` named **STAAD Prep Bridge**. Show purpose, current inbox, last result, and **Export Geometry**, **Choose Inbox…**, **Close** buttons. |
| 2 | Shorter JSON names | Use ASCII-only `SP_YYYYMMDD_HHMMSS.json`; same-second collisions append `_02`, `_03`, etc. Remove random UUID/token text. |
| 3 | Highlight selected objects/Nodes | Preserve blue Member and amber Node highlight actors and prove they appear after a real viewport click. |
| 4 | Reorder tools by usage | Workflow: import/check/repair/direction/number/validate/export. Edit/view: select/create/draw/move/delete/split/repeat/direction/filter/labels/view. |
| 5 | Easy Reset View | Keep **Fit Model** and add **Reset View**, which restores isometric orientation, fits the model, resets clipping, and renders. |
| 6 | Node/Member cannot be clicked | Convert Qt logical mouse coordinates to VTK render-window display coordinates before every pick. Prove both entity types in a real Qt/VTK smoke. |
| 7 | Right-click commands do not work | Connect menu actions directly and test them. Right-clicking an entity selects it before entity actions are evaluated. |
| 8 | Empty-space menu needs mode/reset | Always show **Select Nodes**, **Select Members**, **Select Nodes + Members**, **Fit Model**, and **Reset View**. Mode choices enter safe `SELECT` mode and synchronize toolbar filters. |
| 9 | Active command must be highlighted | Add explicit `QToolButton:checked` styling; preserve exclusive checked state for edit modes and checked state for filters/labels. |

## SketchUp interface contract

The existing toolbar/menu command opens the bridge dialog rather than exporting immediately. It states that the extension exports visible SketchUp edge geometry as Neutral JSON for STAAD Model Preprocessor and does not run structural analysis.

- **Export Geometry** validates or requests the inbox, writes atomically, and reports the final compact filename.
- **Choose Inbox…** accepts only `Data/Inbox/SketchUp` or the legacy development inbox and refreshes the displayed path.
- **Close** closes the dialog.

Compact outputs are chronological and collision-safe:

```text
SP_20260830_140328.json
SP_20260830_140328_02.json
```

Atomic `.tmp` write, flush, fsync, rename, Neutral JSON fields, source coordinates, source unit `in`, and source axis `Z-UP` remain unchanged.

## Desktop interaction contract

Qt reports logical widget coordinates while VTK may render at a different Windows display scale. Every picker uses:

```python
display_x = x * render_width / widget_width
display_y = (widget_height - y) * render_height / widget_height
```

Zero-sized widgets/render windows fail closed. Picking, highlighting, context menus, Fit, and Reset never mutate the model.

Selection behavior remains:

- click selects allowed Node/Member candidates;
- Ctrl-click is additive;
- empty click without Ctrl clears selection;
- overlap cycling remains deterministic;
- Node highlight is amber and Member highlight is blue.

The context menu works on entities and empty space. Mode entries are always enabled; Focus/Clear entries require a selection. **Fit Model** preserves orientation while fitting; **Reset View** restores the approved isometric orientation then fits. `Shift+Z` remains Fit Model.

## Toolbar order

Workflow toolbar:

```text
Import Model → Unit Check → Repair → Auto Fix Axis → Numbering → Validate → Export STD
```

Edit & View toolbar:

```text
Select → Create Node → Create Node… → Draw Member → Move/Snap → Delete → Split
→ Translational Repeat… → Auto Fix Selected → Flip Selected → Set Direction
→ Nodes/Members filters → label toggles → Fit Model → Reset View
```

## Verification boundary

Use STANDARD verification: targeted Ruby/RBZ tests, pure coordinate tests, Qt toolbar/context tests, isolated real Windows Qt/VTK clicks for Node and Member, affected regression, Ruff, targeted strict mypy, `git diff --check`, rebuilt RBZ, rebuilt standalone executable, and rebuilt portable folder/ZIP.

No high-risk structural component is in scope. If implementation reveals a need to change unit conversion affecting coordinates, topology/connectivity, automatic repair, or `.STD` incidence semantics, stop and invoke the HIGH-RISK approval gate.

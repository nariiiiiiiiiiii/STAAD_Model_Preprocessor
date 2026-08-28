# UI BASELINE

Status: LOCKED for V1 unless the user explicitly requests a redesign.

The approved baseline is the dark engineering desktop application mockup discussed on 2026-08-28.

## Main composition

```text
+--------------------------------------------------------------------------------+
| STAAD Model Preprocessor | Project                         window controls       |
+--------------------------------------------------------------------------------+
| Import Model | Unit Check | Repair | Normalize Axis | Renumber | Validate | STD |
+----------------------+--------------------------------------+--------------------+
| PROJECT EXPLORER     |                                      | PROPERTIES         |
| Files                |                                      | Selected entity    |
| Model Tree           |            3D VIEWPORT               +--------------------+
| Structures           |                                      | VALIDATION         |
|                      |   wireframe structural model         | PASS/WARN/ERROR    |
| MODEL SUMMARY        |   nodes, warnings, local-X arrows    +--------------------+
| Nodes/Members/etc.   |                                      | QUICK FIX          |
|                      |                                      | Repair actions     |
+----------------------+--------------------------------------+--------------------+
| ISSUE CONSOLE: Type | ID | Description | Action                                  |
+--------------------------------------------------------------+-----------------+
| status / unit / axis / counts                                | MODEL STATUS    |
+--------------------------------------------------------------------------------+
```

## Toolbar baseline

- Import Model
  - SketchUp `.skp` — primary
  - DXF `.dxf` — fallback
- Unit Check
- Repair
- Normalize Axis
- Renumber
- Validate
- Export STD

## Interaction baseline

### Issue-first workflow
Selecting an issue must:
1. select the affected model entity,
2. zoom/highlight the location,
3. show properties/context,
4. show only valid repair actions,
5. keep the issue selected until repaired/dismissed/changed.

### Status
- green: PASS/ready,
- amber: warning/review,
- red: error/blocking,
- blue/neutral: informational.

Do not use color as the only status signal; always pair with text/icon.

### 3D viewport
Must support:
- orbit,
- pan,
- zoom,
- fit model,
- select node/member,
- isolate structure,
- show XYZ triad,
- optional grid,
- issue highlights,
- local-X direction arrows during normalization.

## Key screens/mockups

- `ui/main_dashboard.svg` — main application baseline.
- `ui/unit_check.svg` — unit/reference-dimension workflow.
- `ui/issue_repair.svg` — issue inspection/repair workflow.

These are implementation references, not pixel-perfect final artwork. Functional hierarchy and panel locations should remain stable through V1.

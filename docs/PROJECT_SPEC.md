Status: APPROVED FOR IMPLEMENTATION — task-gated execution; STRICT approved for HR-1 through HR-4; Manual Editing V1 expansion approved 2026-08-28; SketchUp Ruby Bridge + Direct DXF V1 import architecture approved 2026-08-28.
Date: 2026-08-28

## 1. Problem statement

Current workflow:

1. Build structural line/model geometry in SketchUp.
2. Export DXF.
3. Import DXF into STAAD.Pro.
4. Manually clean geometry before design:
   - orphan/unattached nodes,
   - disconnected structural components,
   - near-but-not-connected nodes,
   - missing members,
   - duplicate or very short members,
   - crossing members without analytical nodes,
   - inconsistent member incidence/local-X direction,
   - unit/scale uncertainty,
   - inconsistent node/member numbering.
5. Only after cleanup can section/load/design work begin.

The application shall move this cleanup work before STAAD.Pro and allow routine analytical line-model corrections directly in the app.

## 2. Product definition

STAAD Model Preprocessor is a Windows desktop application that imports SketchUp/DXF geometry, converts it into a canonical analytical structural graph, detects and repairs geometry/topology problems, allows focused manual node/member editing, normalizes the model, and exports a clean STAAD `.STD` model.

It is NOT a structural analysis solver, NOT a full CAD/BIM authoring package, and NOT a replacement for STAAD.Pro or SketchUp.

## 3. Success criterion

A model that reaches `READY FOR STAAD` shall require little or no geometry cleanup after being opened in STAAD.Pro.

The user must be able to repair common dirty-geometry cases directly in the app when an automatic Quick Fix is not appropriate.

The first production target is not feature breadth. It is a fast, reliable cleanup/editing pipeline that can be used on real projects immediately.

## 4. V1 user workflow

`Import -> Inspect -> Unit/Dimension Check -> Validate -> Quick Fix / Manual Edit -> Connectivity -> Normalize / Direction Control -> Renumber -> Final Validate -> Export .STD`

### Inputs / import routes

V1 first-class routes:
- **SketchUp Ruby Extension** — `Send to STAAD Prep` exports Neutral JSON v1 from the active SketchUp model into the configured project-local inbox.
- **Direct DXF Import** — open AutoCAD/ZWCAD/other `.dxf` line geometry directly in the app without requiring SketchUp.

Future optional:
- Direct `.skp` file import through the T14 native C-SDK bridge if official SketchUp C SDK access becomes available. This is not a V1 dependency.

### Output

Primary:
- STAAD `.std`

Optional/audit:
- cleaned `.dxf`
- project/preprocessor JSON
- validation/repair report

## 5. V1 functional scope

### Import
- Receive SketchUp structural edge geometry from the public SketchUp Ruby API through Neutral JSON protocol v1.
- Import DXF line geometry directly and independently of SketchUp.
- Preserve usable groups/components/tags/layers/source metadata where available.
- SketchUp bridge output stays source-space/Z-Up; canonical conversion occurs only in the shared T06 transform layer.
- Convert both import routes into the same canonical structural model before validation/repair.
- Direct `.skp` C-SDK reading remains a future optional backend, not a V1 blocker.

### Units and dimensions
- Detect/read source unit where reliable.
- Display source unit and working unit.
- Canonical working unit: metre.
- Reference-length check: user selects two points/nodes and enters expected physical length.
- Display model extents X/Y/Z.
- Detect suspicious scale ratios such as 1, 10, 100, 1000, 25.4, 304.8.
- Measure point-to-point and member lengths.
- Identify unusually short members using configurable tolerance.

### Canonical analytical model
- Node = unique structural point.
- Member = edge between two stable node UUIDs.
- Structure = connected component in the member/node graph.
- Internal model is independent from SKP/DXF/STAAD file formats.
- STAAD-facing node/member numbers are attributes, not canonical identity keys.

### Geometry/topology validation
Must detect at minimum:
- duplicate nodes,
- near-duplicate nodes,
- orphan nodes,
- unconnected member ends/gaps,
- zero-length members,
- short members,
- duplicate members,
- crossing members without a node,
- disconnected structures,
- invalid/non-finite coordinates.

### Repair / Quick Fix
User must be able to fix issues inside the app:
- merge nodes,
- snap node to node,
- delete orphan,
- delete duplicate/short member,
- connect nodes,
- split member at intersection,
- reverse member incidence,
- scale model,
- transform coordinate system,
- undo/redo repair commands.

Every repair operation must be explicit, reversible, auditable, and re-run affected validation.

### Manual analytical model editing

The app shall provide explicit editing modes:
- Select,
- Create Node,
- Draw Member,
- Move / Snap Node,
- Delete,
- Measure,
- Set Direction.

Safety rules:
- Select mode MUST NOT move geometry by click-drag.
- Mouse movement/drawing uses ghost preview only until commit.
- `Esc` cancels an in-progress edit with no canonical model mutation.
- Committed geometry changes execute through reversible/auditable commands and revalidate/re-render.
- Destructive delete remains confirmed.

Manual operations include:
- draw a missing member between two existing nodes,
- draw a member from an existing node to a newly created node,
- move a node to a valid new coordinate,
- drag/snap a node onto an existing node using merge/snap semantics,
- select one of overlapping duplicate members and delete only the selected member,
- split a member at midpoint, percentage, distance-from-start, or intersection,
- create nodes directly in-app.

### Create Node

Creation methods:
1. Click / Snap on a valid inference/working plane.
2. Exact canonical XYZ coordinate entry.
3. Relative to selected reference Node using signed `ΔX / ΔY / ΔZ`.
4. Translational Repeat from a reference Node.

Relative Create Node UI must show:
- reference Node ID and coordinates,
- STAAD X,
- STAAD Y (Vertical),
- STAAD Z,
- direction/sign and distance for each axis,
- computed result coordinate,
- optional `Create Member` checkbox from reference Node to new Node,
- Preview / Create / Cancel.

If the computed location matches an existing node within tolerance, the app must report the existing node and must not silently create a duplicate.

### Translational Repeat

A focused STAAD-like Translational Repeat is included for analytical node/member generation:
- per-step `ΔX / ΔY / ΔZ`,
- repeat count means number of NEW node positions and excludes the reference node,
- optional member creation,
- default member mode: Connect Consecutive Nodes,
- alternate member mode: Connect From Reference Node,
- ghost preview of all proposed nodes/members,
- existing-node collision handling before commit,
- entire repeat commits/undoes as one atomic history operation.

This feature is not a general CAD copy-array system.

### Snap / inference / precision controls

Manual drawing and movement shall support:
- Existing Node,
- Member endpoint,
- Member midpoint,
- Member intersection,
- X axis,
- canonical Y axis (vertical),
- Z axis,
- current working plane/grid.

Axis lock shortcuts:
- `X`: constrain to canonical X,
- `Y`: constrain to canonical Y (Vertical),
- `Z`: constrain to canonical Z,
- `Esc`: cancel current edit/lock.

The app must not guess arbitrary 3D depth when no valid inference/working plane exists.

### Structure detection
- Compute connected components.
- Display number of structures.
- List node/member counts per structure.
- Isolate/highlight a selected structure.
- Find closest candidate connection between detached structures.
- Detached-structure connection candidates are suggested, not silently auto-connected.

### Axis normalization and member direction
Canonical target for V1:
- STAAD Y-Up.

Source SketchUp convention:
- Z-Up.

The importer/transform layer converts source coordinates once into canonical Y-Up coordinates.

Member incidence/local-X normalization rules are deterministic.

User controls:
- Auto Fix Axis All,
- Auto Fix Axis Selected,
- Flip Selected,
- Set Direction by selecting a Member then clicking the endpoint that shall become Start `(i)`.

Set Direction changes incidence/local-X only; it does not move geometry.

Local-Y/local-Z/Beta/section rotation are not included in this V1 manual-editing expansion.

### Renumbering / numbering controls
Perform deterministic numbering after cleanup/topology validation.

Node numbering:
- default sort by elevation Y, then X, then Z, then stable UUID tie-break.

Member numbering:
- deterministic classification/order,
- columns,
- X-direction beams,
- Z-direction beams,
- braces/diagonals,
- others,
- sorted by level/position inside each class.

User controls:
- Auto Node Number,
- Auto Member Number,
- Auto Number All,
- Old -> New mapping preview before apply.

Numbering changes only STAAD-facing `.number` fields; stable UUID identities and member endpoint UUID references do not change.

### Viewport navigation and selection

SketchUp-style navigation baseline:
- Middle Mouse drag: Orbit,
- Shift + Middle Mouse drag: Pan,
- Mouse Wheel: Zoom,
- `Shift+Z`: Zoom Extents / Fit Model.

Navigation must work while an edit tool is active and must not cancel the edit preview.

Selection support:
- Node / Member selection filters,
- overlapping-entity cycling/chooser,
- Ctrl additive selection,
- double-click Focus / Zoom Selected,
- context menus with valid entity operations only.

View toggles:
- Node Number,
- Member Number,
- Local-X Arrow,
- Coordinates,
- XYZ triad,
- optional working grid/plane.

### Validation gate
The app must have a final validation view with PASS/WARNING/ERROR.

Normal export shall be blocked while critical geometry/topology errors remain.

A future explicit force-export option may exist but remains out of V1.

## 6. UI baseline

The approved visual baseline remains a professional dark engineering desktop app with:
- top ribbon/toolbar,
- left Project Explorer,
- central 3D structural viewport,
- right Properties + Validation + Quick Fix panels,
- bottom Issue Console,
- persistent model summary/status.

Toolbar groups:

`FILE`
- Import Model
- Save
- Export STD

`EDIT`
- Select
- Create Node
- Draw Member
- Move / Snap Node
- Delete

`MODEL`
- Auto Node No.
- Auto Member No.
- Auto Number All
- Auto Fix Axis
- Flip Selected
- Set Direction

`VIEW`
- Node No.
- Member No.
- Local-X
- Coordinates
- Fit Model

`TOOLS`
- Measure
- Validate

The V1 UI is a focused analytical line-model editor and cleanup tool. It is intentionally not a general CAD authoring environment.

## 7. Technology baseline

Primary application:
- Python 3.12+
- PySide6
- PyVista / VTK
- NumPy
- SciPy spatial/KD-tree where useful
- ezdxf

SketchUp bridge (V1):
- SketchUp Ruby Extension using the public SketchUp Ruby API; V1 UI is intentionally lightweight with one primary `Send to STAAD Prep` toolbar/menu action.
- Emits versioned Neutral JSON v1 into project-local `artifacts/sketchup_bridge/inbox/`.
- Python neutral reader converts the envelope into the same raw `ImportBatch` pipeline used before T06/T07.

Direct SKP adapter (future optional):
- T14 C++ helper/native contract is preserved for use with the official SketchUp C API if access is granted later.
- It is not required to ship or accept V1.

Packaging:
- development: normal Python virtual environment,
- production: Windows executable, preferred Nuitka after compatibility is proven.

## 8. Development priority

V1 treats **SketchUp Ruby Bridge** and **Direct DXF Import** as independent first-class input routes. Neither route may block the other. Direct `.skp` C-SDK import is outside the V1 critical path.

Milestones:
- M0 project foundation
- M1 desktop UI shell
- M2 canonical model + project serialization
- M3 import vertical slice: DXF + SketchUp Ruby Bridge/shared canonical path
- M4 unit / dimension / coordinate transform
- M5 validator / issue model
- M6 repair command framework + undo/redo + issue repair UI
- M7 normalize / deterministic renumber core
- M8 STAAD `.STD` exporter
- M9 SketchUp-style navigation + selection
- M10 snap / inference / axis lock
- M11 manual analytical node/member editing
- M12 precision Create Node + Translational Repeat
- M13 numbering/member-direction controls (T20; COMPLETE)
- M14 end-to-end READY / packaging / real-project acceptance (T21-T23; T21 COMPLETE, T22-T23 pending)
- M15 post-acceptance workspace cleanup / unused-file quarantine (T24)

## 9. Explicitly out of V1

Do not implement yet:
- arbitrary Rotate geometry tool,
- Mirror geometry,
- full Copy Array / radial array / general transform array,
- Trim,
- Extend,
- Offset,
- 3D solids / surfaces,
- section-shape modeling,
- structural solver/FEM,
- member design,
- concrete/steel code checks,
- load generation,
- load combinations,
- analysis results,
- BIM/IFC authoring,
- cloud/login/database,
- AI auto-design,
- automatic solid H-beam/RC member centerline inference.

The approved Translational Repeat is a narrow analytical node/member generation workflow and does not change this boundary.

These larger capabilities may be evaluated later from real-project feedback after V1 acceptance.

## 10. Performance target

V1 should remain interactive for ordinary engineering frame models.

Design baseline:
- 1,000–10,000 members: routine use,
- 50,000 members: target for acceptable inspection/validation with indexed algorithms,
- avoid O(N²) spatial checks when a spatial index can be used.

Interactive editing should avoid rebuilding unnecessary global state during ghost previews; canonical revalidation occurs on commit.

## 11. Safety / correctness principle

Visual appearance is not proof of analytical connectivity.

All export decisions use the canonical node/member graph, not merely rendered lines.

The app must never silently auto-repair a geometry change with meaningful structural implications without recording it in the repair log.

Manual editing must use explicit modes so camera/navigation/select actions cannot accidentally change structural geometry.

## 12. Definition of V1 done

V1 is considered usable when representative SketchUp-via-Ruby and/or direct-DXF structural geometry can:
1. enter the app without losing supported structural line geometry,
2. verify units/reference dimension,
3. expose disconnected/dirty topology visually,
4. repair common topology errors through Quick Fix and direct viewport editing,
5. create missing nodes/members and correct node placement without returning to SketchUp,
6. use relative Create Node and Translational Repeat with optional member creation,
7. normalize/selectively control member incidence/local-X,
8. renumber nodes/members deterministically through explicit controls,
9. pass final validation,
10. export a `.STD` file that opens in the target STAAD.Pro environment with the intended node/member geometry,
11. preserve repair/audit history and reversible manual operations,
12. run as a normal Windows desktop application with SketchUp-style navigation.

## 13. Post-acceptance workspace cleanup

After T23 real-project/STAAD.Pro acceptance, T24 performs a non-destructive workspace audit to reduce stale project clutter.

Rules:
- quarantine root is `STAAD_Model_Preprocessor/DEL/`, never a parent/system folder;
- T24 moves files only; it never deletes them;
- every moved item must be verified unused/superseded by reference/import/config/search evidence;
- a manifest records original path, quarantine path, reason, evidence, and restoration guidance;
- `.git`, active `.worktrees`, the current runtime `.venv`, required `vendor` SDK contents, and T23 acceptance evidence are protected from quarantine;
- generated/cache/build artifacts may be classified separately as regenerable, but must not be confused with obsolete source/documentation;
- after quarantine, relevant regression/lint/type/build/package checks must still pass;
- the user decides whether and when to delete files inside `DEL/`.

T24 is housekeeping after V1 acceptance and must not weaken T23 acceptance criteria or alter structural behavior.

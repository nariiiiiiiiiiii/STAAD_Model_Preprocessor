# PROJECT SPEC — STAAD Model Preprocessor

Status: Approved design baseline, awaiting written-spec review before implementation.
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
   - duplicate or very short members,
   - inconsistent member incidence/local-X direction,
   - unit/scale uncertainty,
   - inconsistent node/member numbering.
5. Only after cleanup can section/load/design work begin.

The application shall move this cleanup work before STAAD.Pro.

## 2. Product definition

STAAD Model Preprocessor is a Windows desktop application that imports SketchUp/DXF geometry, converts it into a canonical analytical structural graph, detects and repairs geometry/topology problems, normalizes the model, and exports a clean STAAD `.STD` model.

It is NOT a structural analysis solver and NOT a replacement for STAAD.Pro.

## 3. Success criterion

A model that reaches `READY FOR STAAD` shall require little or no geometry cleanup after being opened in STAAD.Pro.

The first production target is not feature breadth. It is a fast, reliable cleanup pipeline that can be used on real projects immediately.

## 4. V1 user workflow

`Import -> Inspect -> Unit/Dimension Check -> Clean -> Connectivity -> Repair -> Normalize -> Renumber -> Validate -> Export .STD`

### Inputs

Primary:
- SketchUp `.skp`

Compatibility/fallback:
- AutoCAD `.dxf`

### Output

Primary:
- STAAD `.std`

Optional/audit:
- cleaned `.dxf`
- project/preprocessor JSON
- validation/repair report

## 5. V1 functional scope

### Import
- Import SKP structural edge geometry.
- Import DXF line geometry.
- Preserve usable groups/tags/component metadata where available.
- Convert source coordinates into the canonical coordinate system.

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
- Member = edge between two node IDs.
- Structure = connected component in the member/node graph.
- Internal model is independent from SKP/DXF/STAAD file formats.

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

### Repair
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

Every repair operation must be explicit, reversible, and re-run affected validation.

### Structure detection
- Compute connected components.
- Display number of structures.
- List node/member counts per structure.
- Isolate/highlight a selected structure.
- Find closest candidate connection between detached structures.

### Axis normalization
Canonical target for V1:
- STAAD Y-Up.

Source SketchUp convention:
- Z-Up.

The importer/transform layer converts source coordinates once into canonical Y-Up coordinates.

Member incidence/local-X normalization rules shall be deterministic and configurable.

### Renumbering
Perform only after cleanup/topology validation.

Node numbering:
- spatial/deterministic ordering,
- default sort by elevation then X then Z for Y-Up.

Member numbering:
- deterministic classification/order,
- columns,
- X-direction beams,
- Z-direction beams,
- braces/diagonals,
- others,
- sorted by level/position inside each class.

### Validation gate
The app must have a final validation view with PASS/WARNING/ERROR.

Normal export shall be blocked while critical geometry/topology errors remain.

A future explicit force-export option may exist but is out of V1 unless needed during testing.

## 6. UI baseline

The approved visual baseline is a professional dark engineering desktop app with:
- top ribbon/toolbar,
- left Project Explorer,
- central 3D structural viewport,
- right Properties + Validation + Quick Fix panels,
- bottom Issue Console,
- persistent model summary/status.

Toolbar baseline:
- Import Model
- Unit Check
- Repair
- Normalize Axis
- Renumber
- Validate
- Export STD

The V1 UI must prioritize issue inspection and one-click repair over CAD authoring features.

## 7. Technology baseline

Primary application:
- Python 3.12+
- PySide6
- PyVista / VTK
- NumPy
- SciPy spatial/KD-tree where useful
- ezdxf

SKP adapter:
- C++ helper executable using official SketchUp C API.
- Communicates with Python through a versioned neutral interchange contract.

Packaging:
- development: normal Python virtual environment,
- production: Windows executable, preferred Nuitka after compatibility is proven.

## 8. Development priority

Internal implementation order may use DXF first to prove the canonical model/validator faster, but V1 release target keeps SKP as primary user input.

Milestones:
- M0 project foundation and UI shell
- M1 canonical model + project serialization
- M2 DXF importer vertical slice
- M3 validator/issue model
- M4 repair command framework + undo/redo
- M5 3D issue inspection UI
- M6 normalize + deterministic renumber
- M7 STAAD `.STD` exporter
- M8 SKP native importer adapter
- M9 packaging + real-project acceptance

## 9. Explicitly out of V1

Do not implement yet:
- structural solver/FEM,
- member design,
- concrete/steel code checks,
- load generation,
- load combinations,
- analysis results,
- BIM/IFC,
- cloud/login/database,
- AI auto-design,
- automatic solid H-beam/RC member centerline inference.

These may be added later as patches after V1 is in real use.

## 10. Performance target

V1 should remain interactive for ordinary engineering frame models.

Design baseline:
- 1,000–10,000 members: routine use,
- 50,000 members: target for acceptable inspection/validation with indexed algorithms,
- avoid O(N²) spatial checks when a spatial index can be used.

## 11. Safety / correctness principle

Visual appearance is not proof of analytical connectivity.

All export decisions use the canonical node/member graph, not merely rendered lines.

The app must never silently auto-repair a geometry change with meaningful structural implications without recording it in the repair log.

## 12. Definition of V1 done

V1 is considered usable when a representative real SketchUp/DXF structural model can:
1. import without losing structural line geometry,
2. verify units/reference dimension,
3. expose disconnected/dirty topology visually,
4. repair common topology errors,
5. normalize incidence and numbering deterministically,
6. pass final validation,
7. export a `.STD` file that opens in the target STAAD.Pro environment with the intended node/member geometry,
8. preserve a repair/audit log,
9. run as a normal Windows desktop application.

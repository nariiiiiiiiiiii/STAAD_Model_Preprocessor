## Goal

Keep the application fast to develop, safe to edit, and easy to patch without coupling file formats, viewport interaction, canonical topology, or STAAD export logic together.

## High-level architecture

```text
SKP ---------\
              > Import Adapters -> Canonical Structural Model -> Validation -> Repair/Edit Commands -> Normalize/Direction -> Renumber -> Export
DXF ---------/                                 |                    |                     |                    |          |
                                                +-> 3D Viewer        +-> Audit/Undo         +-> Local-X         +-> Maps  +-> .STD
                                                      |
                                                      +-> Interaction State
                                                      +-> Snap/Inference
                                                      +-> Ghost Preview
```

The 3D viewer never becomes the source of truth. It emits interaction intent and previews; commands mutate the canonical model only on commit.

## Layers

### 1. UI layer
Technology: PySide6.

Responsibilities:
- toolbar/ribbon,
- Project Explorer,
- Properties panel,
- Validation panel,
- Quick Fix panel,
- Issue Console,
- status/model summary,
- Create Node / Repeat / numbering preview dialogs,
- edit-mode controls,
- selection filters and view toggles,
- confirmation dialogs.

The UI must not own topology, inference math, numbering algorithms, or export formatting.

### 2. Viewer / interaction layer
Technology: PyVista / VTK.

Responsibilities:
- render canonical nodes/members,
- select node/member/structure,
- highlight issue locations,
- isolate structures,
- display local-X direction arrows,
- display node/member numbers and coordinate labels,
- SketchUp-style orbit/pan/zoom/fit,
- maintain explicit edit mode,
- ghost node/member previews,
- emit model-space interaction requests.

Interaction invariants:
- `SELECT` drag never changes geometry;
- Middle Mouse navigation temporarily overrides editing without cancelling it;
- preview actors are disposable and non-authoritative;
- `Esc` clears current preview/gesture without model mutation.

### 3. Snap / inference layer

Responsibilities:
- existing-node snap,
- endpoint/midpoint inference,
- member-intersection inference,
- axis constraints X/Y/Z,
- working-plane/grid resolution,
- deterministic candidate tie-breaking.

It operates in canonical metre / STAAD Y-Up coordinates. It does not mutate the model.

### 4. Canonical model layer
Format-independent source of truth.

Core entities:
- `ProjectModel`
- `Node`
- `Member`
- `StructureComponent`
- `Issue`
- `RepairRecord`

Canonical coordinate system:
- Y-Up.

Canonical working length unit:
- metre.

Stable UUID identities are independent from STAAD-facing numbers.

### 5. Import adapters

#### DXF importer
- Python + ezdxf.
- Extract supported line geometry and metadata.
- Convert to neutral/canonical model through a well-defined adapter contract.

#### SKP importer
- C++ helper using official SketchUp C API.
- Reads SKP without requiring SketchUp to be open.
- Emits versioned neutral interchange data.
- Python adapter converts interchange data into the same canonical model used by DXF.

The rest of the application must not depend on SKP SDK types.

### 6. Validation engine
Produces `Issue` objects only. It must not silently mutate geometry.

Validators:
- unit/scale sanity,
- invalid coordinates,
- duplicate/near nodes,
- orphan nodes,
- zero/short members,
- duplicate members,
- gaps/unconnected endpoints,
- intersections without nodes,
- connected-component/structure count,
- incidence/direction consistency,
- numbering readiness.

### 7. Repair / editing engine
Command-based architecture.

Existing/reused commands include:
- `MergeNodes`
- `SnapNode`
- `DeleteNode`
- `DeleteMember`
- `ConnectNodes`
- `SplitMember`
- `ReverseMember`
- `ScaleModel`
- `TransformModel`

Manual-editing additions include:
- `CreateNode`
- `MoveNode`
- atomic `CompositeRepair`
- reversible numbering commands wrapping T12
- explicit member-start/direction commands wrapping T11 reversal semantics.

Every successful mutation records sufficient before/after state for audit and undo. Multi-step operations such as create-node+member, split-at-intersection, or Translational Repeat commit as one atomic history item.

### 8. Manual editing orchestration

The editing layer converts validated user intent into command objects; it does not directly write `model.nodes`, `model.members`, coordinates, numbers, or incidences.

Examples:

```text
DRAW MEMBER
Viewer click intent -> InferenceHit -> editing factory -> ConnectNodes / CompositeRepair -> RepairHistory

MOVE / SNAP NODE
Ghost drag -> final InferenceHit -> MoveNode or MergeNodes -> RepairHistory

TRANSLATIONAL REPEAT
Dialog spec -> deterministic proposal -> collision resolution -> CompositeRepair -> RepairHistory
```

### 9. Normalization / numbering
Deterministic transformations only.

Default Y-Up direction rules:
- columns: low Y -> high Y,
- dominant-X members: low X -> high X,
- dominant-Z members: low Z -> high Z,
- diagonal members: deterministic dominant-axis rule.

Direction UI reuses these rules and adds explicit `Flip Selected` / `Set Direction` without moving geometry.

Default node ordering:
- elevation Y,
- X,
- Z,
- UUID tie-break at precision equality.

Default member ordering:
- columns,
- X beams,
- Z beams,
- braces/diagonals,
- others,
then level/position.

Numbering UI wraps these deterministic functions in reversible history commands. UUID identities/member endpoint UUID references never change during renumbering.

### 10. Export adapters

Primary V1 exporter:
- STAAD `.STD`.

Optional/audit outputs:
- cleaned DXF,
- JSON audit/project data.

Export consumes the canonical model only and never repairs/renumbers it silently.

## Project layout target

```text
STAAD_Model_Preprocessor/
├── AGENTS.md
├── README.md
├── docs/
├── src/
│   └── staadprep/
│       ├── ui/
│       ├── viewer/
│       ├── editing/
│       ├── model/
│       ├── importers/
│       ├── validation/
│       ├── repair/
│       ├── orientation/
│       ├── numbering/
│       ├── exporters/
│       └── paths.py
├── native/
│   └── skp_reader/
├── tests/
│   ├── unit/
│   ├── ui/
│   ├── integration/
│   └── golden_models/
├── scripts/
├── .tmp/
├── .cache/
├── .logs/
├── build/
├── dist/
├── artifacts/
└── vendor/
```

## Architectural invariants

1. UI/viewer never becomes the source of truth for geometry.
2. Importers never perform hidden structural repairs.
3. Validators report; repair/edit commands mutate.
4. Ghost previews never mutate canonical state.
5. Select/navigation actions never mutate geometry.
6. Exporters do not repair/renumber models during export.
7. Writable development/runtime paths remain inside the canonical project root.
8. File-format adapters can be replaced without changing the canonical model API.
9. Stable UUID identity survives numbering changes.
10. V1 remains focused on analytical line-model cleanup/preparation, not structural design, analysis, or general CAD authoring.

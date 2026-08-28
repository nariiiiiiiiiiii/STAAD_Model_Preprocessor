# ARCHITECTURE

## Goal

Keep the application fast to develop, easy to patch, and safe to evolve without coupling file formats, UI, or STAAD export logic together.

## High-level architecture

```text
SKP ---------\
              > Import Adapters -> Canonical Structural Model -> Validation -> Repair Commands -> Normalize -> Renumber -> Export
DXF ---------/                                 |                    |                                 |            |
                                                +-> 3D Viewer        +-> Issue Console                 +-> Audit    +-> .STD
```

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
- dialogs for unit/reference-length/repair confirmation.

The UI must not own topology or export algorithms.

### 2. Viewer layer
Technology: PyVista / VTK.

Responsibilities:
- render canonical nodes/members,
- select node/member/structure,
- highlight issue locations,
- isolate structures,
- display local-X direction arrows,
- camera presets and fit/zoom.

### 3. Canonical model layer
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

### 4. Import adapters

#### DXF importer
- Python + ezdxf.
- Extract supported line geometry and metadata.
- Convert to neutral/canonical model through a well-defined adapter contract.

#### SKP importer
- C++ helper using official SketchUp C API.
- Reads SKP without requiring SketchUp to be open.
- Emits versioned neutral interchange data.
- Python adapter converts the interchange data into the same canonical model used by DXF.

The rest of the application must not depend on SKP SDK types.

### 5. Validation engine
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

### 6. Repair engine
Command-based architecture.

Candidate commands:
- `MergeNodesCommand`
- `SnapNodesCommand`
- `DeleteNodeCommand`
- `DeleteMemberCommand`
- `ConnectNodesCommand`
- `SplitMemberCommand`
- `ReverseMemberCommand`
- `ScaleModelCommand`
- `TransformAxisCommand`
- `RenumberNodesCommand`
- `RenumberMembersCommand`

Each command records before/after data required for audit and undo where practical.

### 7. Normalization / numbering
Deterministic transformations only.

Default Y-Up direction rules:
- columns: low Y -> high Y,
- dominant-X members: low X -> high X,
- dominant-Z members: low Z -> high Z,
- diagonal members: deterministic dominant-axis/elevation rule.

Default node ordering:
- elevation Y,
- X,
- Z.

Default member ordering:
- columns,
- X beams,
- Z beams,
- braces/diagonals,
- others,
then level/position.

### 8. Export adapters

Primary V1 exporter:
- STAAD `.STD`.

Optional:
- cleaned DXF,
- JSON audit/project data.

Export consumes the canonical model only.

## Project layout target

```text
STAAD_Model_Preprocessor/
├── AGENTS.md
├── README.md
├── docs/
├── src/
│   └── staad_preprocessor/
│       ├── app/
│       ├── ui/
│       ├── viewer/
│       ├── model/
│       ├── importers/
│       ├── validation/
│       ├── repair/
│       ├── normalize/
│       ├── numbering/
│       ├── exporters/
│       └── paths/
├── native/
│   └── skp_reader/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── golden_models/
├── .tmp/
├── .cache/
├── .logs/
├── build/
├── dist/
├── artifacts/
└── vendor/
```

## Architectural invariants

1. UI never becomes the source of truth for geometry.
2. Importers never perform hidden structural repairs.
3. Validators report; repair commands mutate.
4. Exporters do not repair models during export.
5. Writable development paths remain inside the canonical project root.
6. File-format adapters can be replaced without changing the canonical model API.
7. V1 must remain focused on cleanup/preparation, not structural design or analysis.

## Goal

Keep the application fast to develop, safe to edit, and easy to patch without coupling file formats, viewport interaction, canonical topology, or STAAD export logic together.

Current implementation checkpoint (2026-09-01): all agreed post-T22 source behavior, the latest
portable package, and T23 target acceptance are user accepted. T24 cleanup is complete, including
the recoverable DEL quarantine and post-move verification. The canonical post-T24 file and RBZ
relationship map is docs/WORKTREE_MINDMAP.md; this document remains the subsystem-boundary view.

## High-level architecture

```text
SketchUp open model -> Ruby Extension -> Neutral JSON v1 --\
                                                         > Shared raw/canonical pipeline -> Validation -> Repair/Edit -> Normalize/Direction -> Renumber -> Export
DXF file ---------------------------> Direct DXF Reader --/                                  |                                         |
                                                                                              +-> 3D Viewer / Audit / Undo               +-> .STD

Future optional: `.skp` -> T14 native C-SDK helper -> Neutral JSON v1 -> same shared pipeline
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

#### SketchUp Ruby bridge — V1
- Runs inside SketchUp using the public Ruby API.
- Recursively exports supported structural edges plus group/component/tag/unit metadata.
- Emits Neutral JSON protocol v1 to project-local `artifacts/sketchup_bridge/inbox/`.
- Does not perform STAAD axis conversion or topology repair.
- A Python neutral reader converts the envelope into the same raw import contract used before T06/T07.

#### Direct SKP native bridge — future optional
- T14 C++ helper/capability contract remains available for an official SketchUp C SDK backend later.
- Direct `.skp` reading is not a V1 dependency.

Downstream canonical/validation/repair code must not depend on SketchUp Ruby or C-SDK types.

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
- `MergeMembers`
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

Selection deletion is built by `build_delete_selection`: selected Members are removed before
explicitly selected Nodes, while any Node retaining an unselected incidence is rejected. Selected-
Member repeat builds one `CompositeRepair` after collision and duplicate-incidence validation.

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

The viewport emits selection state and delete intent; `MainWindow` owns Properties updates,
destructive confirmation, history execution, revalidation, and rerender. This keeps keyboard,
toolbar, mouse, and context-menu deletion on one auditable path.

Project Explorer rebuilds deterministic Node/Member child rows from the canonical model and emits
UUID-only selection requests. `MainWindow` activates the matching selection filter and delegates
clear/highlight rendering to the viewport; the normal viewport selection signal remains the only
path that updates Properties and selection-dependent actions.

`PropertiesPanel` resolves internal UUID selection keys through `ProjectModel` but renders only
engineering-facing Node/Member numbers, coordinates, incidence endpoints, length, and group/layer.
UUIDs and import source references remain model metadata and are deliberately hidden from the panel.

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
├── extensions/
│   └── sketchup_staadprep/
├── native/
│   └── skp_reader/              # future optional direct-SKP backend
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

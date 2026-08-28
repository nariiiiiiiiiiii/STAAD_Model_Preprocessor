# STAAD Model Preprocessor V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows desktop preprocessor that imports SketchUp/DXF structural geometry, exposes and repairs dirty analytical topology, normalizes member incidence/numbering, validates the model, and exports a clean STAAD `.STD` geometry model.

**Architecture:** File-format adapters produce a format-neutral raw geometry batch. Strictly tested unit/coordinate and topology engines convert it into a canonical graph whose entities use stable UUID keys and separate STAAD-facing integer numbers. UI, 3D rendering, repair commands, validation, numbering, and exporters consume that canonical graph; no engineering-semantic logic lives in the GUI.

**Tech Stack:** Python 3.12+, PySide6, PyVista/VTK, NumPy, SciPy, ezdxf, pytest/pytest-qt; C++ + official SketchUp C API for the later SKP helper; Nuitka for production packaging after compatibility is proven.

**Spec:** `docs/superpowers/specs/2026-08-28-staad-model-preprocessor-design.md` and `docs/PROJECT_SPEC.md`

## Global Constraints

- Windows 11 is the V1 target platform.
- Primary input: SketchUp `.skp`; compatibility input: `.dxf`.
- Primary output: STAAD `.std`.
- Canonical working unit: metre.
- Canonical axis: STAAD Y-Up.
- SketchUp source convention: Z-Up.
- All project-generated source, tests, logs, cache, temp, build, dist, artifacts, SDK staging, and reports MUST remain under `STAAD_Model_Preprocessor/`.
- UI baseline is fixed by `docs/UI_BASELINE.md` and `docs/ui/*.svg`; no redesign during MVP.
- V1 does not implement a solver, loads, code design, IFC/BIM, cloud/login/database, AI auto-design, or automatic solid-member centerline inference.
- High-risk HR-1 through HR-4 are approved for STRICT / Full TDD as of 2026-08-28.
- Execute exactly one numbered Task at a time. Every Task ends with verification, documentation/status update, Git commit, and a hard stop for user review.

---

## Locked File Structure

```text
STAAD_Model_Preprocessor/
├── pyproject.toml
├── AGENTS.md
├── README.md
├── src/staadprep/
│   ├── __init__.py
│   ├── app.py
│   ├── paths.py
│   ├── model/
│   │   ├── geometry.py
│   │   ├── entities.py
│   │   ├── project.py
│   │   └── serialization.py
│   ├── importers/
│   │   ├── contracts.py
│   │   ├── dxf_reader.py
│   │   └── skp_bridge.py
│   ├── units/
│   │   └── transforms.py
│   ├── topology/
│   │   ├── builder.py
│   │   └── connectivity.py
│   ├── validation/
│   │   ├── issues.py
│   │   └── validators.py
│   ├── repair/
│   │   ├── commands.py
│   │   ├── history.py
│   │   └── audit.py
│   ├── orientation/
│   │   └── normalize.py
│   ├── numbering/
│   │   └── renumber.py
│   ├── exporters/
│   │   └── staad_std.py
│   ├── viewer/
│   │   ├── scene.py
│   │   └── selection.py
│   └── ui/
│       ├── main_window.py
│       ├── theme.py
│       ├── issue_console.py
│       └── panels.py
├── native/skp_reader/
│   ├── CMakeLists.txt
│   ├── include/neutral_contract.h
│   └── src/main.cpp
├── scripts/
│   ├── run_dev.ps1
│   └── build_windows.ps1
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── ui/
│   └── golden_models/
├── docs/
├── .tmp/
├── .cache/
├── .logs/
├── artifacts/
├── build/
├── dist/
└── vendor/
```

Stable internal entity keys are UUIDs. STAAD node/member numbers are mutable integer attributes and MUST NOT be used as canonical graph identity. This reduces reference-corruption risk during renumbering.

---

### Task 01: Python Bootstrap + Project-Local Path Guard

**Risk:** STANDARD

**Files:**
- Create: `pyproject.toml`
- Create: `src/staadprep/__init__.py`
- Create: `src/staadprep/paths.py`
- Create: `scripts/run_dev.ps1`
- Create: `tests/unit/test_paths.py`
- Modify: `.gitignore`
- Modify: `docs/TASK_BOARD.md`, `docs/CHECKLIST.md`, `docs/HANDOFF.md`

**Interfaces:**
- Produces: `ProjectPaths.from_root(root: Path) -> ProjectPaths`
- Produces: `ProjectPaths.ensure_layout() -> None`
- Produces: `ProjectPaths.assert_inside_project(path: Path) -> Path`

- [x] **Step 1: Add package/test configuration with project-local pytest temp**

Use a `src` layout and configure pytest with `--basetemp=.tmp/pytest`. Dependencies: PySide6, pyvista, vtk, numpy, scipy, ezdxf; dev dependencies: pytest, pytest-qt, ruff, mypy, nuitka.

- [x] **Step 2: Write failing path-boundary tests**

```python
from pathlib import Path
import pytest
from staadprep.paths import ProjectPaths


def test_generated_paths_are_under_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)
    paths.ensure_layout()
    for path in paths.generated_dirs:
        assert path.is_relative_to(root)
        assert path.exists()


def test_rejects_path_outside_project(tmp_path: Path) -> None:
    root = tmp_path / "STAAD_Model_Preprocessor"
    root.mkdir()
    paths = ProjectPaths.from_root(root)
    with pytest.raises(ValueError):
        paths.assert_inside_project(tmp_path / "outside.log")
```

- [x] **Step 3: Run RED**

Run: `python -m pytest tests/unit/test_paths.py -v --basetemp=.tmp/pytest`
Expected: FAIL because `staadprep.paths` does not exist.

- [x] **Step 4: Implement the path service**

`ProjectPaths` owns `.tmp`, `.cache`, `.logs`, `artifacts`, `build`, `dist`, and `vendor`; resolve paths before the `is_relative_to` check so `..` cannot escape the root.

- [x] **Step 5: Add `scripts/run_dev.ps1`**

The script sets `TEMP`, `TMP`, `PYTHONPYCACHEPREFIX`, and app-specific cache/log environment variables to directories under the repository before launching `python -m staadprep.app`.

- [x] **Step 6: Run GREEN + lint**

Run: `python -m pytest tests/unit/test_paths.py -v --basetemp=.tmp/pytest`
Run: `python -m ruff check src tests`
Expected: PASS.

- [x] **Step 7: Update status docs and commit**

Commit: `chore: bootstrap project-local Python runtime`

---

### Task 02: Approved Desktop UI Shell

**Risk:** FAST/STANDARD

**Files:**
- Create: `src/staadprep/app.py`
- Create: `src/staadprep/ui/main_window.py`
- Create: `src/staadprep/ui/theme.py`
- Create: `src/staadprep/ui/panels.py`
- Create: `tests/ui/test_main_window.py`
- Modify: `scripts/run_dev.ps1`

**Interfaces:**
- Produces: `create_application() -> QApplication`
- Produces: `MainWindow(QMainWindow)` with named widgets `project_explorer`, `viewport_host`, `properties_panel`, `validation_panel`, `quick_fix_panel`, `issue_console`, `model_status`.

- [x] **Step 1: Write UI smoke test**

```python
def test_main_window_has_approved_regions(qtbot):
    from staadprep.ui.main_window import MainWindow
    window = MainWindow()
    qtbot.addWidget(window)
    assert window.project_explorer.objectName() == "project_explorer"
    assert window.viewport_host.objectName() == "viewport_host"
    assert window.issue_console.objectName() == "issue_console"
    assert window.model_status.text() == "MODEL STATUS: NO MODEL"
```

- [x] **Step 2: Run RED**

Run: `python -m pytest tests/ui/test_main_window.py -v --basetemp=.tmp/pytest`

- [x] **Step 3: Implement the dark engineering shell**

Match `docs/UI_BASELINE.md`: ribbon actions `Import Model`, `Unit Check`, `Repair`, `Normalize Axis`, `Renumber`, `Validate`, `Export STD`; left explorer; central viewport host; right properties/validation/quick-fix; bottom issue console; persistent summary/status. Engineering actions remain disabled until their backing Tasks exist.

- [x] **Step 4: Run test and launch smoke check**

Run test above, then run `powershell -ExecutionPolicy Bypass -File scripts/run_dev.ps1` and visually compare against `docs/ui/main_dashboard.svg`.

- [x] **Step 5: Commit**

Commit: `feat: add approved desktop UI shell`

---

### Task 03: Canonical Model + Project Serialization

**Risk:** STANDARD

**Files:**
- Create: `src/staadprep/model/geometry.py`
- Create: `src/staadprep/model/entities.py`
- Create: `src/staadprep/model/project.py`
- Create: `src/staadprep/model/serialization.py`
- Create: `tests/unit/test_model.py`
- Create: `tests/unit/test_serialization.py`

**Interfaces:**
- Produces: `Vec3(x: float, y: float, z: float)`
- Produces: `Node(key: UUID, position: Vec3, number: int | None, source_refs: tuple[str, ...])`
- Produces: `Member(key: UUID, start: UUID, end: UUID, number: int | None, source_ref: str | None, group: str | None)`
- Produces: `ProjectModel(nodes: dict[UUID, Node], members: dict[UUID, Member], metadata: ModelMetadata, revision: int)`
- Produces: `save_project(model, path)` / `load_project(path) -> ProjectModel`

- [x] **Step 1: Write tests proving stable UUID identity is independent from STAAD number**

```python
def test_member_references_stable_node_keys():
    a = Node.new(Vec3(0, 0, 0))
    b = Node.new(Vec3(1, 0, 0))
    member = Member.new(a.key, b.key)
    a.number = 100
    b.number = 200
    assert member.start == a.key
    assert member.end == b.key
```

- [x] **Step 2: Write serialization round-trip test**

Save under `.tmp/tests/project.json`, reload, and assert node/member keys, positions, numbers, metadata schema version, and source refs are equal.

- [x] **Step 3: Run RED, implement minimal dataclasses and versioned JSON, run GREEN**

Project JSON schema version starts at integer `1`. Non-finite coordinates are rejected by constructors; topology semantics are not implemented here.

- [x] **Step 4: Commit**

Commit: `feat: add canonical structural model contract`

---

### Task 04: 3D Viewport + Synthetic Frame + Selection

**Risk:** STANDARD

**Files:**
- Create: `src/staadprep/viewer/scene.py`
- Create: `src/staadprep/viewer/selection.py`
- Create: `tests/unit/test_scene_data.py`
- Modify: `src/staadprep/ui/main_window.py`

**Interfaces:**
- Consumes: `ProjectModel`
- Produces: `SceneData.from_model(model) -> SceneData`
- Produces: `StructuralViewport.set_model(model)`
- Produces: `StructuralViewport.highlight_nodes(keys)` / `highlight_members(keys)`

- [ ] **Step 1: Test scene-array generation without GUI**

For a two-member frame, assert point array shape `(3, 3)`, line connectivity count `2`, and stable mapping from rendered cell index to member UUID.

- [ ] **Step 2: Run RED, implement `SceneData`, run GREEN**

- [ ] **Step 3: Embed PyVista/VTK Qt viewport**

Render a synthetic multi-bay frame on startup only in development/demo mode; include Y-Up axis triad and member selection callback.

- [ ] **Step 4: Smoke check selection/highlight and commit**

Commit: `feat: add structural 3D viewport`

---

### Task 05: DXF Raw-Geometry Vertical Slice

**Risk:** STANDARD

**Files:**
- Create: `src/staadprep/importers/contracts.py`
- Create: `src/staadprep/importers/dxf_reader.py`
- Create: `tests/integration/test_dxf_reader.py`
- Create: `tests/golden_models/01_dxf_lines/source.dxf`
- Modify: `src/staadprep/ui/main_window.py`

**Interfaces:**
- Produces: `RawPoint(position: Vec3, source_ref: str)`
- Produces: `RawSegment(start: Vec3, end: Vec3, source_ref: str, layer: str | None)`
- Produces: `ImportBatch(points, segments, source_format, declared_unit, metadata, warnings)`
- Produces: `DxfReader.read(path: Path) -> ImportBatch`

- [x] **Step 1: Create a tiny deterministic DXF fixture**

Fixture contains `LINE`, 3D `POLYLINE`, and `POINT`. Faces are absent. Expected output is known segment/point counts and exact raw coordinates with no coordinate conversion.

- [x] **Step 2: Write RED importer test**

Assert LINE extraction, polyline-to-segment expansion, layer preservation, point extraction, and `$INSUNITS` metadata capture.

- [x] **Step 3: Implement raw reader only**

Do NOT merge endpoints, scale units, transform axes, detect structures, or repair geometry in this Task.

- [x] **Step 4: Wire `Import Model > DXF` to show raw lines through a temporary raw preview adapter**

The status must clearly say `RAW DXF PREVIEW — NOT VALIDATED`.

- [x] **Step 5: Run integration test, UI smoke check, commit**

Commit: `feat: import and preview raw DXF geometry`

**Checkpoint A:** app can launch, import DXF, and display structural lines.

---

### Task 06: Unit, Scale, Dimension, and Z-Up→Y-Up Engine

**Risk:** **STRICT HR-1**

**Files:**
- Create: `src/staadprep/units/transforms.py`
- Create: `tests/unit/test_units_transforms.py`
- Create: `tests/golden_models/07_wrong_scale/case.json`
- Create: `tests/golden_models/08_wrong_axis/case.json`
- Modify: `src/staadprep/importers/contracts.py`

**Interfaces:**
- Produces: `LengthUnit` enum (`METER`, `MILLIMETER`, `CENTIMETER`, `INCH`, `FOOT`, `UNKNOWN`)
- Produces: `to_meters(value: float, unit: LengthUnit) -> float`
- Produces: `sketchup_z_up_to_staad_y_up(p: Vec3) -> Vec3`, exactly `(x, z, -y)` after unit conversion
- Produces: `transform_batch(batch, source_unit, source_axis) -> ImportBatch`
- Produces: `measure(a, b) -> float`
- Produces: `model_extents(points) -> Extents`
- Produces: `reference_scale_ratio(measured_m, expected_m) -> float`

- [x] **Step 1: Write independent conversion tests**

Known cases: `1000 mm = 1 m`, `100 cm = 1 m`, `39.37007874015748 in = 1 m`, `3.280839895013123 ft = 1 m`.

- [x] **Step 2: Run RED**

- [x] **Step 3: Implement conversion table minimally; run GREEN**

- [x] **Step 4: Write axis-transform RED tests from hand-calculated fixtures**

```python
def test_sketchup_to_staad_preserves_length_and_handed_mapping():
    p = Vec3(1.0, 2.0, 3.0)
    assert sketchup_z_up_to_staad_y_up(p) == Vec3(1.0, 3.0, -2.0)
```

Also assert source basis X→+X, Y→-Z, Z→+Y and pairwise distances are preserved.

- [x] **Step 5: Implement transform; run GREEN and inverse round-trip checks**

- [x] **Step 6: Add reference-length/extents tests including suspicious ratios**

Recognize ratios near `10`, `100`, `1000`, `25.4`, and `304.8` as warnings; never silently rescale.

- [x] **Step 7: Run full HR-1 targeted suite + lint/type-check**

Run: `python -m pytest tests/unit/test_units_transforms.py -v --basetemp=.tmp/pytest`

- [x] **Step 8: Commit**

Commit: `feat: add verified unit and coordinate transform engine`

---

### Task 07: Canonical Topology Builder + Structure Count

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/topology/builder.py`
- Create: `src/staadprep/topology/connectivity.py`
- Create: `tests/unit/test_topology_builder.py`
- Create: `tests/unit/test_connectivity.py`
- Create: `tests/golden_models/06_disconnected_structures/case.json`

**Interfaces:**
- Produces: `TopologyPolicy(coincident_tolerance_m: float)` with V1 default `1e-9 m`
- Produces: `build_project(batch: ImportBatch, policy: TopologyPolicy) -> ProjectModel`
- Produces: `connected_components(model) -> list[StructureComponent]`

- [x] **Step 1: Write RED tests for exact/coincident endpoint identity**

Endpoints sharing the same coordinate become one canonical node. A 0.5 mm gap MUST remain two nodes at import because meaningful near-node repair is explicit later.

- [x] **Step 2: Implement deterministic spatial bucket lookup**

Avoid O(N²). Use quantized neighboring buckets while comparing true Euclidean distance against `coincident_tolerance_m`.

- [x] **Step 3: Write RED connected-component fixtures**

A main 4-member frame plus a detached 1-member segment must return exactly two components with expected node/member counts.

- [x] **Step 4: Implement graph traversal and run GREEN**

- [x] **Step 5: Assert graph invariants**

Every member start/end UUID exists; no member references the same node at both ends unless deliberately retained as a zero-length issue; source refs remain auditable.

- [x] **Step 6: Commit**

Commit: `feat: build canonical topology and connected structures`

---

### Task 08: Geometry / Topology Validation Detectors

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/validation/issues.py`
- Create: `src/staadprep/validation/validators.py`
- Create: `tests/unit/test_validators.py`
- Populate: `tests/golden_models/02_orphan_node`, `03_near_nodes`, `04_duplicate_member`, `05_short_member`, `09_crossing_without_node`, `10_combined_dirty_frame`

**Interfaces:**
- Produces: `IssueSeverity(ERROR, WARNING, INFO)`
- Produces: `IssueType(INVALID_COORDINATE, DUPLICATE_NODE, NEAR_NODE, ORPHAN_NODE, ZERO_LENGTH_MEMBER, SHORT_MEMBER, DUPLICATE_MEMBER, UNCONNECTED_GAP, CROSSING_WITHOUT_NODE, DISCONNECTED_STRUCTURE)`
- Produces: `Issue(id, severity, type, entity_keys, location, description, suggested_actions)`
- Produces: `ValidationPolicy(near_node_m, short_member_m, intersection_m)`
- Produces: `validate_model(model, policy) -> list[Issue]`

- [ ] **Step 1: Add one RED test per detector before implementation**

Each fixture asserts exact issue type, affected UUIDs, and severity.

- [ ] **Step 2: Implement finite/duplicate/near/orphan/zero/short/duplicate-member checks**

Near-node detection uses `scipy.spatial.cKDTree` or equivalent indexed search.

- [ ] **Step 3: Implement disconnected-structure issue from `connected_components`**

- [ ] **Step 4: Implement 3D segment-crossing-without-node check**

Use indexed candidate bounding boxes and closest-points-on-segments math; only report when closest distance ≤ `intersection_m`, both closest parameters lie in the interior of the two segments, and no canonical node exists at the intersection.

- [ ] **Step 5: Run every golden dirty fixture and combined regression**

- [ ] **Step 6: Commit**

Commit: `feat: detect structural geometry and topology issues`

---

### Task 09: Repair Commands + Undo/Redo + Audit

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/repair/commands.py`
- Create: `src/staadprep/repair/history.py`
- Create: `src/staadprep/repair/audit.py`
- Create: `tests/unit/test_repair_commands.py`
- Create: `tests/unit/test_repair_history.py`

**Interfaces:**
- Produces protocol: `RepairCommand.apply(model) -> RepairResult`; `RepairCommand.revert(model) -> None`
- Commands: `MergeNodes`, `SnapNode`, `DeleteNode`, `DeleteMember`, `ConnectNodes`, `SplitMember`, `ReverseMember`, `ScaleModel`, `TransformModel`
- Produces: `RepairHistory.execute(command)`, `undo()`, `redo()`
- Produces: append-only `AuditEntry(command_type, before_revision, after_revision, affected_keys, parameters, timestamp)`

- [ ] **Step 1: RED test each graph mutation on a tiny model**

Assert exact nodes/members before and after each command.

- [ ] **Step 2: Implement minimal commands with snapshot/inverse data sufficient for exact revert**

- [ ] **Step 3: RED/GREEN undo round-trip tests**

For every command: serialize model before, apply, undo, serialize again; byte-normalized model payload must equal the original except audit/history metadata.

- [ ] **Step 4: Assert graph referential integrity after every command**

No member may reference a missing node. Merge/split commands must update all affected members atomically.

- [ ] **Step 5: Re-run affected validation automatically and test revision increments**

- [ ] **Step 6: Commit**

Commit: `feat: add reversible structural repair commands`

---

### Task 10: Issue Inspection + Quick-Fix UI

**Risk:** STANDARD (core mutations remain covered by STRICT tests from T09)

**Files:**
- Create: `src/staadprep/ui/issue_console.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/ui/panels.py`
- Modify: `src/staadprep/viewer/scene.py`
- Create: `tests/ui/test_issue_console.py`

**Interfaces:**
- Consumes: `list[Issue]`, `RepairHistory`
- Produces: selecting an issue highlights/zooms its entity keys
- Produces: action buttons dispatch only predefined `RepairCommand` objects

- [ ] **Step 1: UI test binds Issue rows to exact Issue IDs**

- [ ] **Step 2: Implement issue table/filter/severity counts and structure isolate action**

- [ ] **Step 3: Implement Quick Fix actions with confirmation for destructive delete operations**

- [ ] **Step 4: Add Undo/Redo actions and re-render/revalidate after command completion**

- [ ] **Step 5: Smoke check combined dirty fixture interactively and commit**

Commit: `feat: inspect and repair model issues in desktop UI`

**Checkpoint B:** user can detect, inspect, repair, and undo common dirty-geometry problems inside the app.

---

### Task 11: Member Incidence / Local-X Normalization

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/orientation/normalize.py`
- Create: `tests/unit/test_orientation.py`
- Modify: `src/staadprep/viewer/scene.py`
- Modify: `src/staadprep/ui/main_window.py`

**Interfaces:**
- Produces: `MemberClass(COLUMN, BEAM_X, BEAM_Z, BRACE, OTHER)`
- Produces: `classify_member(model, member, tolerance_m) -> MemberClass`
- Produces: `needs_reverse(model, member) -> bool`
- Produces: `NormalizeMemberDirection(member_key)` repair command or command factory

- [ ] **Step 1: RED tests for deterministic dominant-axis rule**

For Y-Up: vertical member points `-Y→+Y`; X-dominant points `-X→+X`; Z-dominant points `-Z→+Z`. For diagonal ties use priority X, then Y, then Z. The implementation controls member incidence/local-X only; it does not claim to normalize STAAD local-Y/local-Z/Beta.

- [ ] **Step 2: Implement classification/reversal decision and run GREEN**

- [ ] **Step 3: Add viewport local-X arrows and preview count**

- [ ] **Step 4: Normalize all through existing reversible repair history, revalidate, commit**

Commit: `feat: normalize deterministic member incidence`

---

### Task 12: Deterministic Node / Member Renumbering

**Risk:** **STRICT HR-4**

**Files:**
- Create: `src/staadprep/numbering/renumber.py`
- Create: `tests/unit/test_renumber.py`
- Modify: `src/staadprep/model/entities.py`

**Interfaces:**
- Produces: `NumberingPolicy(node_precision_m=1e-9, class_order=...)`
- Produces: `renumber_nodes(model, policy) -> NumberingMap`
- Produces: `renumber_members(model, policy) -> NumberingMap`
- `NumberingMap` exposes `node_numbers: dict[UUID, int]`, `member_numbers: dict[UUID, int]`.

- [ ] **Step 1: RED tests: node order**

Default Y-Up sort is elevation `Y`, then `X`, then `Z`; ties are broken by stable UUID string only after coordinate equality at policy precision.

- [ ] **Step 2: RED tests: member order**

Class order: COLUMN, BEAM_X, BEAM_Z, BRACE, OTHER; then midpoint elevation/position; then stable UUID tie-break.

- [ ] **Step 3: Implement numbering by changing only `.number` attributes**

Stable node/member UUID keys and member endpoint UUID references MUST NOT change.

- [ ] **Step 4: Determinism test**

Clone same model with different dictionary insertion order; repeated renumbering must produce identical UUID→number maps.

- [ ] **Step 5: Referential-integrity and audit tests, then commit**

Commit: `feat: add deterministic STAAD-facing numbering`

---

### Task 13: Minimal STAAD `.STD` Geometry Exporter

**Risk:** **STRICT HR-3**

**Files:**
- Create: `src/staadprep/exporters/staad_std.py`
- Create: `tests/unit/test_staad_exporter.py`
- Create: `tests/golden_models/01_clean_frame/expected.std`
- Modify: `src/staadprep/ui/main_window.py`

**Interfaces:**
- Produces: `export_staad_std(model: ProjectModel, path: Path) -> ExportReport`
- Export subset exactly: `STAAD SPACE`, `UNIT METER KN`, `JOINT COORDINATES`, `MEMBER INCIDENCES`, `FINISH`.
- Requires every node/member to have a positive unique `.number` and final critical validation to pass.

- [ ] **Step 1: Write exact text-golden RED test**

Expected form:

```text
STAAD SPACE
UNIT METER KN
JOINT COORDINATES
1 0 0 0;
2 6 0 0;
MEMBER INCIDENCES
1 1 2;
FINISH
```

- [ ] **Step 2: Implement deterministic numeric formatting**

Use fixed canonical formatting that strips insignificant trailing zeros but never emits locale commas, NaN, or Infinity.

- [ ] **Step 3: Reject missing/duplicate numbers and dangling references with explicit export errors**

- [ ] **Step 4: Independently parse generated sections in test code and compare back to the canonical coordinates/incidences**

The parser used for test verification must be test-only and independent from exporter formatting functions.

- [ ] **Step 5: Wire Export STD button behind validation gate and commit**

Commit: `feat: export validated STAAD geometry model`

**Checkpoint C:** cleaned DXF workflow can generate deterministic `.STD` geometry.

---

### Task 14: SKP Bridge Contract + Native Helper Capability Probe

**Risk:** STANDARD

**Files:**
- Create: `src/staadprep/importers/skp_bridge.py`
- Create: `native/skp_reader/CMakeLists.txt`
- Create: `native/skp_reader/include/neutral_contract.h`
- Create: `native/skp_reader/src/main.cpp`
- Create: `tests/unit/test_skp_bridge.py`
- Modify: `docs/HANDOFF.md`

**Interfaces:**
- Neutral protocol version: integer `1`.
- Helper CLI: `skp_reader.exe --input <file.skp> --output <project-local-json>`.
- JSON envelope fields: `protocol_version`, `source_file`, `source_unit`, `source_axis`, `points`, `segments`, `groups`, `tags`, `warnings`.
- Produces: `SkpBridge.is_available() -> bool`; `SkpBridge.read(path) -> ImportBatch`.

- [ ] **Step 1: Test Python bridge with a fake project-local helper executable/script fixture**

Assert protocol-version mismatch fails closed and helper output outside the project is rejected.

- [ ] **Step 2: Implement Python process bridge and capability status**

If the official SketchUp SDK is absent, UI reports `SKP importer unavailable — DXF remains available`; no crash and no network download occurs automatically.

- [ ] **Step 3: Add CMake scaffold that expects the official SDK only under `vendor/sketchup-sdk/`**

No SDK binaries are committed to Git.

- [ ] **Step 4: Commit**

Commit: `feat: define isolated native SKP bridge contract`

---

### Task 15: Direct SKP Edge Extraction + Transform Integration

**Risk:** **STRICT HR-1 / HR-2**

**Files:**
- Modify: `native/skp_reader/src/main.cpp`
- Modify: `src/staadprep/importers/skp_bridge.py`
- Create: `tests/integration/test_skp_import.py`
- Create: `tests/golden_models/11_skp_simple_frame/expected.json`

**Interfaces:**
- C++ helper recursively walks model entities/groups/component instances, composes instance transforms, and emits structural edges as raw source-space segments plus tag/group metadata.
- Python then applies the already-tested T06 unit/axis engine and T07 topology builder; C++ does not duplicate canonical conversion logic.

- [ ] **Step 1: Obtain/use official SketchUp C API from `vendor/sketchup-sdk/` and verify exact API signatures against installed SDK headers**

Do not guess SDK function signatures.

- [ ] **Step 2: RED fixture for one line, one group transform, one nested component transform**

Expected world-space source coordinates are hand-calculated and stored in the golden expected JSON.

- [ ] **Step 3: Implement recursive edge extraction with transform composition**

Ignore faces for V1. Preserve group/component/tag names as metadata only. Structural member inference from solids is explicitly excluded.

- [ ] **Step 4: Run native→neutral→Python transform→topology end-to-end test**

Assert known final Y-Up metre coordinates and member count.

- [ ] **Step 5: Commit**

Commit: `feat: import SketchUp structural edges directly`

---

### Task 16: End-to-End READY Gate + Golden Suite + Audit Report

**Risk:** **STRICT HR-1 through HR-4**

**Files:**
- Create: `src/staadprep/validation/ready_gate.py`
- Create: `tests/integration/test_full_pipeline.py`
- Complete: `tests/golden_models/01..11`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/repair/audit.py`

**Interfaces:**
- Produces: `ReadyGate.evaluate(model, issues) -> ReadyStatus`
- `ReadyStatus.ready` is false when any critical ERROR exists, unit/reference dimension is unverified when required by policy, or numbering is incomplete.
- Produces project-local validation report JSON with import metadata, transforms, issue summary, repairs, numbering maps, and export status.

- [ ] **Step 1: Define exact gate tests**

Clean model = READY. Orphan, disconnected critical component, invalid coordinate, zero-length, unresolved crossing, or missing numbering = NOT READY. Warnings alone do not block unless policy says otherwise.

- [ ] **Step 2: Execute all golden fixtures through import→transform→topology→validate**

Dirty fixtures must produce exact expected issue sets. Clean/repaired variants must converge to expected structure count and geometry.

- [ ] **Step 3: Repair combined dirty fixture through commands and verify final model graph independently**

Compare node/member coordinate/incidence sets against a hand-authored expected canonical fixture before export.

- [ ] **Step 4: Export and test model→STD→independent test parser round-trip**

- [ ] **Step 5: Update UI status to `READY FOR STAAD` only from `ReadyGate` result**

- [ ] **Step 6: Commit**

Commit: `test: verify end-to-end clean model readiness`

**Checkpoint D:** direct SKP/DXF→repair→validated `.STD` V1 pipeline is functionally complete.

---

### Task 17: Windows Executable Packaging

**Risk:** STANDARD

**Files:**
- Create: `scripts/build_windows.ps1`
- Modify: `pyproject.toml`
- Create: `tests/integration/test_packaged_paths.py`
- Modify: `README.md`

**Interfaces:**
- Output only under `dist/` and `build/`.
- Runtime logs/cache/temp remain under the application/project-owned directories, never system temp by app choice.

- [ ] **Step 1: Add packaging-path test**

- [ ] **Step 2: Add Nuitka build script with PySide6/VTK data inclusion proven by local build**

- [ ] **Step 3: Build from clean environment and launch executable**

- [ ] **Step 4: Import a golden DXF, validate, export `.STD`, close/reopen app**

- [ ] **Step 5: Commit**

Commit: `build: package Windows desktop application`

---

### Task 18: Real-Project Acceptance + STAAD.Pro Verification

**Risk:** **STRICT acceptance**

**Files:**
- Create/update only project-local acceptance artifacts under `artifacts/acceptance/`
- Modify: `docs/HANDOFF.md`, `docs/CHECKLIST.md`, `docs/TASK_BOARD.md`

**Interfaces:**
- Acceptance input: representative real user SKP/DXF structural model.
- Acceptance outputs: preprocessor report, exported `.STD`, screenshots/logs as needed, target STAAD.Pro open result.

- [ ] **Step 1: Copy/reference a real test model into the project-local acceptance area without modifying the user's source file**

- [ ] **Step 2: Run full import/repair/normalize/renumber/validate/export workflow and preserve audit report**

- [ ] **Step 3: Open exported `.STD` in target STAAD.Pro environment**

Verify: intended node coordinates, member incidences, structure count, member local-X incidence direction, numbering, and absence of parser/import geometry errors.

- [ ] **Step 4: Record any discrepancy as a narrowly scoped patch item; do not silently change acceptance criteria**

- [ ] **Step 5: Re-run only affected STRICT regression plus full golden pipeline after fixes**

- [ ] **Step 6: Mark V1 production-usable only after target STAAD.Pro verification succeeds and commit acceptance docs**

Commit: `docs: record V1 real-project acceptance`

**Checkpoint E:** V1 is accepted for real use.

---

## Per-Task Stop Protocol

At the end of every Task the executor MUST:

1. Run the exact targeted verification for that Task.
2. Update `docs/TASK_BOARD.md` status and `docs/CHECKLIST.md` relevant boxes.
3. Update `docs/HANDOFF.md` with current commit, completed Task, next Task, known issues, and exact resume command/entry point.
4. Commit only the completed Task's files.
5. Report results to the user.
6. **STOP. Do not begin the next Task until the user explicitly says to continue/run it.**

## Plan Self-Review Result

- Spec coverage: all V1 functional requirements map to T01–T18.
- Project-boundary rule: enforced from T01 and carried through every Task.
- UI baseline: T02/T04/T10.
- Direct SKP path: T14/T15; DXF remains fallback through T05.
- HR-1: T06/T15/T16.
- HR-2: T07/T08/T09/T11/T15/T16.
- HR-3: T13/T16/T18.
- HR-4: T12/T16/T18.
- Stable identity strategy prevents renumbering from rewriting canonical graph references.
- No V1 out-of-scope solver/design/BIM/cloud features are scheduled.

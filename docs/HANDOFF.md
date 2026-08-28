# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T08 implemented on `task/08-validation`; awaiting user approval before T09.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ application target; current machine is Python 3.14.3.
- PySide6 desktop UI.
- PyVista + pyvistaqt + VTK 3D viewport.
- NumPy/SciPy for numerical/spatial work.
- ezdxf for DXF.
- C++ + official SketchUp C API helper behind an isolated SKP bridge.
- STRICT approval already granted for HR-1 through HR-4.

## Completed tasks

- T01 `4a7551b` — project-local Python/runtime bootstrap and path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — real PyVista/VTK viewport + synthetic frame + selection/highlight.
- T05 `9fcf6be` — raw DXF import + real 3D preview.
- T06 `8bf1b25` — verified metre conversion, scale/reference checks, Z-Up -> Y-Up transform.
- T07 `ce24224` — canonical topology + connected structure count.

## T08 — Geometry / Topology Validation Detectors

Branch/worktree:
- branch: `task/08-validation`
- worktree: `.worktrees/task-08-validation`
- base commit: `ce24224`

Created:
- `src/staadprep/validation/__init__.py`
- `src/staadprep/validation/issues.py`
- `src/staadprep/validation/validators.py`
- `tests/unit/test_validators.py`
- `tests/unit/test_validation_edges.py`
- golden cases:
  - `02_orphan_node`
  - `03_near_nodes`
  - `04_duplicate_member`
  - `05_short_member`
  - `09_crossing_without_node`
  - `10_combined_dirty_frame`

### T08 contracts

`IssueSeverity`:
- ERROR
- WARNING
- INFO

`IssueType`:
- INVALID_COORDINATE
- DUPLICATE_NODE
- NEAR_NODE
- ORPHAN_NODE
- ZERO_LENGTH_MEMBER
- SHORT_MEMBER
- DUPLICATE_MEMBER
- UNCONNECTED_GAP
- CROSSING_WITHOUT_NODE
- DISCONNECTED_STRUCTURE

`ValidationPolicy` V1 defaults:
- `near_node_m = 0.001` (1 mm)
- `short_member_m = 0.010` (10 mm)
- `intersection_m = 1e-6` (1 micrometre)
- exact duplicate-node tolerance remains `1e-9 m`, aligned with T07 topology identity.

### Detector behavior

- Invalid coordinate: ERROR.
- Duplicate node: ERROR.
- Near node: WARNING.
- Orphan node: ERROR.
- Zero-length member: ERROR.
- Short member: WARNING.
- Duplicate/reversed-incidence member: ERROR.
- Unconnected near-node gap across different connected components: ERROR.
- Crossing without canonical node: ERROR.
- Secondary member-bearing disconnected structure: WARNING.

Near-node detection uses `scipy.spatial.cKDTree`.

Crossing detection uses sweep-style AABB candidate filtering and 3D closest-points-on-segments math. A crossing is reported only when:
- closest separation <= `intersection_m`,
- both closest parameters are interior to their members,
- members do not share a canonical endpoint,
- no canonical node exists at the crossing location.

Parallel members, endpoint-only contacts, and crossings already split by a canonical node are not reported as crossing-without-node.

### Important scope boundary

T08 is read-only. It must not:
- merge/snap nodes,
- delete members/nodes,
- split members,
- connect gaps,
- modify UUID identities,
- alter model revision/topology.

Those operations belong to T09.

## STRICT T08 verification evidence

TDD RED evidence:
- validator tests initially failed with `ModuleNotFoundError: staadprep.validation`.

Targeted detector suite:
- 15 tests passed after implementation and edge checks.

Full regression before task close:
- 75 tests passed.
- Ruff passed.
- targeted mypy for validation module passed.

Independent scale/false-positive sanity:
- clean 5,001-node / 5,000-member chain -> `issues=0`.
- output: `VALIDATION_SCALE_PASS nodes=5001 members=5000 issues=0`.

Golden combined dirty frame confirms the expected detector families are all present without mutating the model.

## Environment note

The shared project-local venv used for development contains SciPy 1.18.1 and NumPy 2.5.2. A transient first import attempt reported SciPy missing, but a direct interpreter import confirmed SciPy exists in the project-local venv; subsequent validator runs were stable.

## Next task

**T09 — Repair Commands + Undo/Redo + Audit Log**

Risk: **STRICT HR-2 / Full TDD already approved by user.**

T09 owns actual graph mutation and must preserve exact undo/redo and auditability. Do not start T09 until the user explicitly requests it.

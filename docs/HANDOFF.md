# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T07 implemented on `task/07-topology`; awaiting user approval before T08.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ target; current machine Python 3.14.3.
- PySide6 + PyVista/pyvistaqt/VTK desktop stack.
- ezdxf raw import.
- Canonical analytical coordinate space: metre + Y-Up.
- STRICT approval already granted for HR-1 through HR-4.

## Completed tasks

- T01 `4a7551b` — project-local runtime/path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — real 3D structural viewport + selection/highlight.
- T05 `9fcf6be` — raw DXF import + real 3D preview.
- T06 `8bf1b25` — verified unit/scale/dimension and Z-Up->Y-Up engine.

## T07 — Canonical Topology Builder + Structure Count

Branch/worktree:
- branch: `task/07-topology`
- worktree: `.worktrees/task-07-topology`
- base commit: `8bf1b25`

Created:
- `src/staadprep/topology/__init__.py`
- `src/staadprep/topology/builder.py`
- `src/staadprep/topology/connectivity.py`
- `tests/unit/test_topology_builder.py`
- `tests/unit/test_connectivity.py`
- `tests/integration/test_canonical_topology_pipeline.py`
- `tests/golden_models/06_disconnected_structures/case.json`

### T07 behavior

`TopologyPolicy`:
- default `coincident_tolerance_m = 1e-9 m`.
- non-finite or non-positive tolerance fails closed.

`build_project()`:
- accepts only canonical metre/Y-Up coordinate batches.
- recognizes canonical coordinate metadata from T06 while preserving original source unit/axis for audit.
- uses quantized 3D spatial buckets and searches only the 27 neighboring buckets.
- confirms true Euclidean distance before merging an endpoint.
- points within tolerance become one canonical Node.
- a 0.5 mm gap remains separate; near-node repair is not performed in T07.
- raw POINT entities are retained as Nodes so T08 can identify orphan nodes.
- zero-length segments are deliberately retained as Members so T08 can flag them; T07 does not silently delete them.
- Node source references aggregate deterministically and Member source refs/layers remain auditable.

`connected_components()`:
- validates all member start/end references exist.
- returns every connected graph component, including isolated zero-member nodes.
- zero-length members remain attached to their one-node component.
- components are ordered with larger member-bearing structures first, then deterministically by geometry.

## STRICT T07 verification evidence

TDD RED evidence:
- topology builder initially failed with `ModuleNotFoundError: staadprep.topology`.
- connectivity initially failed with `ModuleNotFoundError: staadprep.topology.connectivity`.

Targeted verification:
- T07 topology/connectivity/cross-task suite: 12 passed.
- Ruff: pass.
- mypy on `src/staadprep/topology`: pass.

Independent checks:
- hand-authored disconnected golden model: main frame 4 members + detached member -> exactly 2 components with `(4 nodes,4 members)` and `(2 nodes,1 member)`.
- T05 DXF -> T06 mm/Z-Up transform -> T07 canonical topology: raw 7 preview nodes collapse to exactly 5 canonical nodes / 3 members / 2 components, with hand-calculated metre/Y-Up coordinates.
- negative spatial-bucket boundary case within tolerance merges correctly.
- 5,000-member chain sanity: `TOPOLOGY_SCALE_PASS nodes=5001 members=5000 structures=1`.

Final regression before status update:
- full pytest: 60 passed.
- Ruff full source/tests: pass.

## Important T07 boundaries

T07 does NOT:
- merge near nodes beyond the strict coincident tolerance,
- detect duplicate/short/orphan/crossing issues,
- repair geometry,
- normalize member direction,
- renumber nodes/members.

Those behaviors remain T08 onward.

## Next task

**T08 — Geometry / Topology Validation Detectors**

Risk: **STRICT HR-2 / Full TDD already approved by user.**

T08 will detect invalid/duplicate/near/orphan/zero-length/short/duplicate-member/unconnected-gap/crossing/disconnected-structure issues without mutating the model.

Do not start T08 until the user explicitly asks to continue/run Task 8.

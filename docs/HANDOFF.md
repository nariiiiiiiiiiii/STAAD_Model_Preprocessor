# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T06 implemented on `task/06-units`; awaiting user approval before T07.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Locked baselines

- Python 3.12+ target; current machine Python 3.14.3.
- PySide6 desktop UI.
- PyVista + pyvistaqt + VTK 3D viewport.
- ezdxf DXF input.
- C++ + official SketchUp C API helper planned for direct SKP input.
- STRICT/Full TDD approval already granted for HR-1 through HR-4.

## Completed task commits before T06

- T01 `4a7551b` — project-local runtime/path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical model + project serialization.
- T04 `a38fc97` — real 3D viewport + synthetic frame + selection/highlight.
- T05 `9fcf6be` — raw DXF import + real 3D preview.

## T06 — Unit / Scale / Dimension / Axis Engine

Risk: **STRICT HR-1**.
Branch/worktree:
- branch: `task/06-units`
- worktree: `.worktrees/task-06-units`
- base commit: `9fcf6be`

Created:
- `src/staadprep/units/__init__.py`
- `src/staadprep/units/transforms.py`
- `tests/unit/test_units_transforms.py`
- `tests/unit/test_import_batch_axis_contract.py`
- `tests/golden_models/07_wrong_scale/case.json`
- `tests/golden_models/08_wrong_axis/case.json`

Modified:
- `src/staadprep/importers/contracts.py` adds `ImportBatch.source_axis`.
- task/checklist/plan/handoff docs.

### Verified public behavior

Length units:
- `LengthUnit.METER`
- `LengthUnit.MILLIMETER`
- `LengthUnit.CENTIMETER`
- `LengthUnit.INCH`
- `LengthUnit.FOOT`
- `LengthUnit.UNKNOWN`
- `to_meters(value, unit)` fails closed for UNKNOWN.

Reference conversions independently checked:
- 1000 mm = 1 m
- 100 cm = 1 m
- 39.37007874015748 in = 1 m
- 3.280839895013123 ft = 1 m

Coordinate convention:
- SketchUp/source Z-Up -> STAAD Y-Up exactly `(x, y, z) -> (x, z, -y)`.
- basis mapping: X -> +X, Y -> -Z, Z -> +Y.
- mapping is right-handed and preserves Euclidean distance.

Dimension utilities:
- `measure(a, b)` Euclidean 3D distance.
- `model_extents(points)` -> minimum / maximum / size.
- empty extents fail closed.

Reference-scale workflow:
- `reference_scale_ratio = measured / expected`.
- suspicious factors near 10, 25.4, 100, 304.8, 1000 produce warnings.
- warnings never rescale geometry automatically.
- invalid expected reference length fails closed.

Batch transform:
- `transform_batch(batch, source_unit, source_axis)` converts unit to canonical metres first.
- Z-Up then maps to Y-Up; Y-Up remains oriented and is only unit-scaled.
- source refs, layers, source format, warnings, and metadata are preserved.
- transformed batch records source unit/axis and canonical `m` / `Y-UP` metadata.
- source batch is immutable/not mutated.
- unknown unit or unsupported axis fails closed.
- T06 does not merge/snap endpoints or create topology.

## STRICT TDD evidence

Observed RED stages:
1. unit engine missing: `ModuleNotFoundError: staadprep.units`.
2. axis function missing: import failure for `sketchup_z_up_to_staad_y_up`.
3. extents/measurement/reference/batch interfaces missing: import failure for `Extents` and related APIs.
4. `ImportBatch.source_axis` missing: constructor rejected `source_axis`.

Final targeted HR-1 suite:
- 30/30 tests passed before full regression.

Final repository regression:
- 48/48 tests passed.
- Ruff: PASS.
- mypy strict targeted check: PASS on `units/transforms.py` + `importers/contracts.py`.
- independent sanity: `HR1_INDEPENDENT_PASS right_handed=True inch_to_m=1 ratio=1000 warning=True`.

## Important scope boundary

T06 is the verified engine layer only. The existing Unit Check toolbar action is still not wired to a dedicated dimension/reference-length UI. The checklist records this explicitly so the project does not claim UI functionality that is not implemented.

T07 must consume metre/Y-Up geometry and is responsible for canonical endpoint identity and connected structures. It must not reimplement unit or axis conversion.

## Next task

**T07 — Canonical Topology Builder + Structure Count**

Risk: **STRICT HR-2 / Full TDD already approved by user.**

Do not begin T07 until the user explicitly asks to continue/run Task 7.

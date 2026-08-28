Date: 2026-08-28
Status: **T12 complete on `task/12-renumber`; awaiting user approval before T13.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all source/temp/cache/log/build/test/generated files remain inside this root.

## Product pipeline

`SketchUp SKP / DXF -> unit/axis gate -> canonical topology -> validate/repair -> normalize incidence -> renumber -> STAAD .STD -> STAAD.Pro`

Canonical geometry entering T12 is metre / Y-Up. T12 MUST NOT transform axes or coordinates.

## Completed task commits before T12

- T01 `4a7551b`
- T02 `8e4c2f8`
- T03 `f97bffe`
- T04 `a38fc97`
- T05 `9fcf6be`
- T06 `8bf1b25`
- T07 `ce24224`
- T08 `adde44b`
- T09 `7bfeb94`
- T10 `b3e7d4e`
- T11 `a4fc572`

## T12 — Deterministic numbering

Branch/worktree:
- branch: `task/12-renumber`
- worktree: `.worktrees/task-12-renumber`
- base: `a4fc572`

Created:
- `src/staadprep/numbering/__init__.py`
- `src/staadprep/numbering/renumber.py`
- `tests/unit/test_renumber.py`
- `tests/unit/test_renumber_edges.py`
- `tests/unit/test_numbering_policy.py`

`Node.number` and `Member.number` already existed from T03, so no entity-schema change was required despite the original plan listing `model/entities.py` as a modification target.

### Node numbering

Default sort in canonical Y-Up coordinates:
1. quantized elevation `Y`
2. quantized `X`
3. quantized `Z`
4. stable UUID string

Default coordinate precision: `1e-9 m`.

### Member numbering

Default class order:
1. COLUMN
2. BEAM_X
3. BEAM_Z
4. BRACE
5. OTHER

Within a class, sort by quantized midpoint:
1. midpoint `Y`
2. midpoint `X`
3. midpoint `Z`
4. stable UUID string

Member classification reuses the T11 canonical orientation classifier.

### Mutation / integrity contract

- numbering changes only STAAD-facing `.number` fields plus model `revision`;
- node/member UUID dictionary keys never change;
- member `start/end` UUID references never change;
- geometry/source metadata never change;
- mapping is precomputed before mutation, so missing member-node references fail before partial member numbering;
- every numbering call returns `NumberingMap`, an auditable UUID -> STAAD-facing number mapping;
- stale/duplicate/negative old numbers are overwritten with deterministic positive `1..N` sequences.

### Policy safety

`node_precision_m` must be finite and positive. `NaN`, `+inf`, `-inf`, zero and negative values fail closed.

`class_order` must contain every `MemberClass` exactly once.

## T12 verification evidence

TDD RED evidence:
- numbering package initially missing (`ModuleNotFoundError`).
- non-finite precision tests initially showed `NaN` and `+inf` were accepted; guard was corrected to finite + positive.

Targeted T12 suite:
- 12 tests passed.
- Ruff passed.
- targeted mypy passed.

Independent HR-4 sanity:
- 5,001 nodes / 5,000 members;
- shuffled dictionary insertion order produced identical numbering maps;
- node numbers were unique 1..5001;
- member numbers were unique 1..5000;
- endpoint UUID references were unchanged.

Full regression before documentation update:
- 150 non-smoke tests passed;
- T04 real Qt/VTK viewport smoke passed;
- T10 real issue/repair smoke passed;
- T11 real orientation smoke passed;
- total 153 tests passed.

## Important boundary

T12 does not write `.STD` and does not rewrite canonical UUID identities. T13 consumes these deterministic positive numbers to emit STAAD `JOINT COORDINATES` and `MEMBER INCIDENCES`.

## Next task

**T13 — Minimal STAAD `.STD` Geometry Exporter**

Risk: **STRICT HR-3 / Full TDD already approved by user.**

Do not start T13 until the user explicitly requests it.

Date: 2026-08-28
Status: **T13 complete on `task/13-std`; T14 is next and not started.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all source/temp/cache/log/build/test/generated/exported files remain inside this root. Test `.STD` outputs are under `.tmp/tests/t13/`; user-facing export is guarded by `ProjectPaths.assert_inside_project()`.

## Product pipeline

`SketchUp SKP / DXF -> unit/axis gate -> canonical topology -> validate/repair -> normalize incidence -> renumber -> STAAD .STD -> STAAD.Pro`

Canonical export contract entering T13:
- metre,
- Y-Up,
- deterministic member incidence/local-X from T11,
- positive deterministic STAAD-facing node/member numbers from T12.

T13 does not transform axes, renumber, repair, analyze, or design the structure.

## Completed task commits through T12

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
- T12 `9ab269f`

## T13 — Minimal STAAD `.STD` geometry exporter

Branch/worktree:
- branch: `task/13-std`
- worktree: `.worktrees/task-13-std`
- base: `9ab269f`

Created:
- `src/staadprep/exporters/__init__.py`
- `src/staadprep/exporters/staad_std.py`
- `tests/unit/test_staad_exporter.py`
- `tests/ui/test_export_ui.py`
- `tests/golden_models/01_clean_frame/expected.std`

Modified:
- `src/staadprep/ui/main_window.py`
- `docs/CHECKLIST.md`
- `docs/TASK_BOARD.md`
- implementation plan status.

## Locked exported subset

T13 emits exactly this geometry-level subset:

```text
STAAD SPACE
UNIT METER KN
JOINT COORDINATES
<node-number> <X> <Y> <Z>;
MEMBER INCIDENCES
<member-number> <start-node-number> <end-node-number>;
FINISH
```

No supports, properties, materials, loads, load combinations, analysis commands, design commands, Beta angles, releases, or section definitions are emitted in T13.

## Export safety / validation contract

`export_staad_std(model, path) -> ExportReport` fails closed before writing when:
- model has no nodes,
- any node/member STAAD number is missing,
- any number is non-integer, non-positive, or duplicated within its namespace,
- any member references a missing canonical node,
- final T08 validation contains any `ERROR` issue.

Validation `WARNING` issues do not block export; their issue IDs are returned in `ExportReport.warning_issue_ids`.

Exporter does not auto-renumber or auto-repair. T12/T08/T09 remain the authorities for those operations.

## Numeric formatting

Coordinates are emitted as locale-independent fixed decimal text:
- no locale thousands/decimal commas,
- no NaN/Infinity,
- negative zero becomes `0`,
- no scientific notation,
- insignificant fractional trailing zeros are stripped,
- conversion uses the shortest Python float decimal representation as input to `Decimal`, then fixed-decimal rendering, preserving tested float round-trip values.

Output ordering is by STAAD-facing `.number`, never dictionary insertion order.

## UI export gate

`Export STD` is enabled only when:
- a canonical model is loaded,
- the model is non-empty,
- current validation has no `ERROR`,
- node numbering is complete, positive, integer and unique,
- member numbering is complete, positive, integer and unique.

Warnings are allowed.

The Save dialog defaults to project-local `artifacts/model.std`. `export_current_std()` guards the selected path through `ProjectPaths.assert_inside_project()`, so paths outside the project root are rejected before file creation.

## T13 STRICT verification evidence

TDD RED evidence:
- exporter package initially missing (`ModuleNotFoundError`).
- UI action initially stayed disabled and `export_current_std()` did not exist.
- empty model initially enabled the UI export action and was corrected.
- empty model initially exported and was corrected to fail closed.
- initial numeric formatter emitted exponent notation; fixed-decimal tests forced the final canonical formatter.

Targeted T13 suite after all edge fixes:
- 20 tests passed.
- Ruff passed.
- targeted mypy passed.

Independent HR-3 verification:
- T12 numbering -> T13 export -> independent test-only section parser;
- 4 canonical nodes / 4 members parsed back exactly to canonical coordinates/incidences;
- output subset headers/terminator verified independently;
- result: `STAAD_EXPORT_INDEPENDENT_PASS nodes=4 members=4 subset=5 deterministic=True`.

Final regression after implementation/docs status update:
- 170 non-smoke tests passed;
- T04 real Qt/VTK viewport smoke passed;
- T10 real issue/repair smoke passed;
- T11 real orientation smoke passed;
- total: 173 tests passed;
- Ruff passed;
- targeted mypy passed;
- `git diff --check` passed before HANDOFF write.

## Important acceptance limitation

T13 verifies deterministic syntax and independently parses its own locked geometry subset, but **the generated `.STD` has not yet been opened/accepted in the target STAAD.Pro installation**.

`Verify with target STAAD.Pro environment` remains intentionally unchecked in `CHECKLIST.md` and belongs to T18 real-project acceptance. Do not claim STAAD.Pro acceptance before T18 evidence exists.

## Checkpoint C

The canonical cleaned/normalized/numbered model can now generate deterministic minimal STAAD `.STD` geometry. The current raw DXF UI path still has the previously documented Unit/Axis-to-canonical wiring gap; full direct workflow closure is handled by later integration tasks.

## Next task

**T14 — SKP Bridge Contract + Native Helper Capability Probe**

Risk: STANDARD.

T14 must not modify T13 export semantics. It defines an isolated SKP helper contract and must fail gracefully when the official SketchUp SDK is absent.

Do not start T14 until the user explicitly requests it.

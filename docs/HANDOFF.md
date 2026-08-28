# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T09 complete on `task/09-repair`; T10 is next and not started.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Completed tasks

- T01 `4a7551b` — project-local bootstrap/path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — PyVista/VTK 3D viewport + selection/highlight.
- T05 `9fcf6be` — raw DXF import/preview.
- T06 `8bf1b25` — STRICT unit/scale/axis engine.
- T07 `ce24224` — STRICT topology + connected structures.
- T08 `adde44b` — STRICT validation detectors.

## T09 — Repair Commands + Undo/Redo + Audit

Branch/worktree:
- branch: `task/09-repair`
- worktree: `.worktrees/task-09-repair`
- base commit: `adde44b`

Created:
- `src/staadprep/repair/__init__.py`
- `src/staadprep/repair/commands.py`
- `src/staadprep/repair/history.py`
- `src/staadprep/repair/audit.py`
- `tests/unit/test_repair_commands.py`
- `tests/unit/test_repair_history.py`
- `tests/unit/test_repair_edges.py`

### Repair command contract

Every command mutates `ProjectModel` in place, increments revision once on successful apply, validates graph integrity, reruns T08 validation, and returns `RepairResult` containing affected UUIDs and current issues.

Implemented commands:
- `MergeNodes`
- `SnapNode`
- `DeleteNode`
- `DeleteMember`
- `ConnectNodes`
- `SplitMember`
- `ReverseMember`
- `ScaleModel`
- `TransformModel`

Safety semantics:
- `DeleteNode` rejects connected nodes; core repair never creates dangling references intentionally.
- `MergeNodes` redirects every affected member atomically and retains zero-length outcomes for validator visibility rather than silently deleting them.
- `SplitMember` requires a point on the member and strictly inside its endpoints.
- `ConnectNodes` requires two existing distinct nodes.
- `ScaleModel` rejects non-finite/non-positive factors.
- command failures before mutation do not advance revision/history/audit.

### Undo / redo

`RepairHistory`:
- `execute()` applies command, clears redo stack, appends audit entry.
- `undo()` restores exact pre-command model state including revision.
- `redo()` reuses the same command-created UUID identities and reproduces the same serialized result.
- undo/redo stack movement happens only after mutation succeeds; a failed revert does not lose the recovery entry.

For all nine commands, serialized JSON after `execute -> undo` equals the original byte-normalized project payload. `redo` reproduces the original post-command payload.

### Audit

`AuditLog` is append-only through its public API and exposes entries as a tuple.
Each `AuditEntry` records:
- command type,
- before/after revision,
- affected UUIDs,
- command parameters,
- timezone-aware UTC timestamp.

Undo/redo are also logged as `UNDO:<Command>` / `REDO:<Command>` events without embedding audit state into `ProjectModel`.

## STRICT T09 verification evidence

TDD RED evidence:
- repair tests initially failed with `ModuleNotFoundError: staadprep.repair`.
- edge regression later caught an undo-stack atomicity bug where a failed revert removed the undo entry; fixed by peek -> revert -> stack move.

Targeted T09 suite:
- 35 tests passed.
- Ruff passed.
- mypy passed for `commands.py`, `history.py`, `audit.py`.

Independent repair check:
- two structures separated by a 0.5 mm near-node gap.
- before repair: 2 structures + NEAR_NODE issue.
- `MergeNodes`: 1 structure, NEAR_NODE and DISCONNECTED_STRUCTURE removed.
- undo: 2 structures restored.
- redo: 1 structure restored again.
- audit entries after execute/undo/redo: 3.

Full project regression before documentation update:
- 110 tests passed.
- Ruff passed.

## Important T10 boundary

T09 provides only safe core mutations/history/audit. It does **not** wire destructive actions to UI yet.

T10 owns:
- Issue Console rows bound to exact Issue IDs,
- selecting issue -> highlight/zoom,
- Quick Fix buttons dispatching predefined `RepairCommand` objects only,
- confirmation before destructive delete actions,
- Undo/Redo UI,
- re-render/revalidate after command completion.

Do not implement T11 orientation normalization during T10.

## Next task

**T10 — Issue Console + inspect/zoom/quick-fix UI integration**

Risk: STANDARD for UI integration; mutation safety remains covered by STRICT T09 tests.

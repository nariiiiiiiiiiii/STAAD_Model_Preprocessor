# HANDOFF — STAAD Model Preprocessor

Date: 2026-08-28
Status: **T11 implemented on `task/11-orientation`; awaiting user approval before T12.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: every project-created source file, worktree, temp, cache, log, build output, artifact, test output, generated report, and staged dependency must remain inside this root.

## Product goal

`SketchUp SKP / DXF -> Preprocessor -> inspect/repair/normalize/renumber/validate -> STAAD .STD -> STAAD.Pro`

V1 prepares clean analytical geometry before STAAD.Pro. It is not a structural solver or mini STAAD.

## Completed task commits before T11

- T01 `4a7551b` — project-local Python/runtime bootstrap and path guard.
- T02 `8e4c2f8` — approved desktop UI shell.
- T03 `f97bffe` — canonical Node/Member/Project model + serialization.
- T04 `a38fc97` — real PyVista/VTK viewport + selection/highlight.
- T05 `9fcf6be` — raw DXF import + preview.
- T06 `8bf1b25` — STRICT unit/scale/axis transform engine.
- T07 `ce24224` — STRICT canonical topology + connected structures.
- T08 `adde44b` — STRICT read-only geometry/topology validators.
- T09 `7bfeb94` — STRICT reversible repair commands + undo/redo + audit.
- T10 `b3e7d4e` — Issue Console, viewport focus/isolate, Quick Fix and Undo/Redo UI.

## T11 — Member Incidence / Local-X Normalization

Branch/worktree:
- branch: `task/11-orientation`
- worktree: `.worktrees/task-11-orientation`
- base commit: `b3e7d4e`

Created:
- `src/staadprep/orientation/__init__.py`
- `src/staadprep/orientation/normalize.py`
- `tests/unit/test_orientation.py`
- `tests/unit/test_scene_orientation.py`
- `tests/unit/test_orientation_invariants.py`
- `tests/ui/test_orientation_ui.py`
- `tests/ui/test_orientation_smoke.py`
- `scripts/smoke_orientation.py`

Modified:
- `src/staadprep/viewer/scene.py`
- `src/staadprep/viewer/widget.py`
- `src/staadprep/ui/main_window.py`
- `src/staadprep/ui/panels.py`
- task/checklist/plan docs.

## Locked T11 semantics

Canonical coordinates are Y-Up.

`MemberClass`:
- `COLUMN`: axis-aligned Y member within classification tolerance.
- `BEAM_X`: axis-aligned X member within classification tolerance.
- `BEAM_Z`: axis-aligned Z member within classification tolerance.
- `BRACE`: non-axis-aligned / multi-axis member.
- `OTHER`: zero/near-zero member at the supplied classification tolerance.

Deterministic incidence/local-X direction rule:
- dominant Y / columns: low Y -> high Y,
- dominant X: low X -> high X,
- dominant Z: low Z -> high Z,
- dominant-axis magnitude ties use priority `X`, then `Y`, then `Z`,
- zero-length member has no meaningful direction and is not reversed.

T11 controls only member `i -> j` incidence, which defines analytical local-X.

T11 explicitly does **not** claim to normalize:
- STAAD local-Y,
- STAAD local-Z,
- Beta angle,
- section orientation,
- releases,
- supports,
- node/member numbering.

Those must not be inferred from T11 behavior.

## Reversible normalization

`NormalizeMemberDirection(member_key)` is a factory that returns the already-STRICT-tested T09 `ReverseMember` command only when a member violates the deterministic rule.

`normalization_commands(model)`:
- returns only required `ReverseMember` commands,
- sorts by stable member UUID integer order,
- performs no mutation by itself.

MainWindow `Normalize Axis` action now means **Normalize member incidence/local-X** while preserving the locked toolbar label.

When a canonical model is loaded:
- local-X arrows are rendered at member midpoints,
- Validation panel shows `N reverse / M total`,
- toolbar tooltip shows the number requiring reversal,
- Normalize action is enabled only when at least one member needs reversal.

Normalize-all execution:
- builds deterministic commands,
- executes each command through existing `RepairHistory`,
- therefore increments revision/audit per reversed member,
- re-renders and re-runs validation once after the batch,
- Undo/Redo continues to operate one reversible `ReverseMember` command at a time.

No composite T11 repair command was introduced; existing T09 mutation semantics remain unchanged.

## Viewport local-X arrows

`SceneData` now exposes arrays aligned with `member_keys`:
- `member_midpoints`,
- normalized `local_x_vectors`.

Zero-length members use a zero vector.

`StructuralViewport.show_local_x_arrows(True/False)`:
- renders local-X arrows for nonzero members,
- preserves the arrow preview across `set_model()` refreshes,
- hides the global arrow actor during structure isolation and restores it afterward.

## STRICT T11 verification evidence

TDD RED evidence:
- `staadprep.orientation` initially did not exist.
- `SceneData.member_midpoints/local_x_vectors` initially did not exist.
- MainWindow initially had no orientation preview count or normalize method.
- real orientation smoke initially failed because `smoke_orientation.py` did not exist.

Targeted T11 verification before documentation update:
- 25 T11 tests passed.
- Ruff passed.
- real Windows Qt/VTK orientation smoke passed.
- invariant tests proved node identity/positions, member keys, lengths, source metadata, connected components, and validation issue types are unchanged by normalization except intended `start/end` swaps.
- normalize -> undo-all returns the exact original `ProjectModel`, including revision.

Independent hand-case sanity:
- X/Y magnitude tie chooses X.
- Y/Z magnitude tie chooses Y.
- 2 required reversals normalize to zero and undo back to revision 0.
- evidence marker: `ORIENTATION_INDEPENDENT_PASS tie_xy=X tie_yz=Y normalized=2 undo_revision=0`.

Full test execution is split because the combined suite plus three real Qt/VTK subprocess smokes exceeds the Serena shell execution window:
- non-smoke suite: 138 passed,
- T04 viewport smoke: 1 passed,
- T10 issue-repair smoke: 1 passed,
- T11 orientation smoke: 1 passed,
- effective total: 141 passed.

Type checking:
- Ruff is clean.
- targeted mypy with `--follow-imports=silent` passes T11 orientation/scene/UI modules.
- unrestricted mypy import traversal still surfaces pre-existing T05 `ezdxf` typing diagnostics and PyVista/VTK stub mismatches in the renderer; these are not T11 behavior failures and were not expanded into this task.

## Current product boundary

T01-T11 functionality is implemented.

The app can inspect and repair canonical models, preview local-X arrows, deterministically normalize member incidence, and undo/redo those reversals.

The raw DXF UI path still stops at `RAW DXF PREVIEW — NOT VALIDATED`; Unit Check/reference-dimension UI has not yet been wired into a complete raw-DXF -> canonical topology pipeline. Do not silently assume source unit/axis to bypass that gate.

## Next task

**T12 — Deterministic Node / Member Renumbering + Reference Rewrite**

Risk: **STRICT HR-4 / Full TDD already approved by user.**

T12 may change only STAAD-facing `.number` attributes and numbering maps. Stable UUID identities and member endpoint UUID references must remain unchanged.

Do not start T12 until the user explicitly requests it.

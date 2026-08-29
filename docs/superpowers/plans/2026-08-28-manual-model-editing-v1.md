# Manual Model Editing V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add safe SketchUp-style viewport navigation plus direct analytical node/member editing, precision node creation/repeat, numbering controls, and member-direction controls before the final V1 READY/packaging/acceptance stages.

**Architecture:** The viewer owns interaction state and ghost previews but never canonical geometry. All committed edits become reversible repair/model commands executed through `RepairHistory` or an equivalent atomic history command, followed by validation and re-render. Existing T11 orientation and T12 numbering algorithms remain the deterministic source of truth; new UI controls wrap them rather than reimplementing them.

**Tech Stack:** Python 3.14 runtime currently verified in project, PySide6 6.11.x, PyVista/VTK, NumPy, pytest/pytest-qt, existing `ProjectModel`, `RepairHistory`, validation, orientation, and numbering packages.

**Spec:** `docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`

## Global Constraints

- Canonical project root: `D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`.
- Every temp/cache/log/build/test/generated artifact stays inside the canonical project root.
- Canonical geometry is metre / STAAD Y-Up; `Y` is vertical.
- `SELECT` mode must never mutate node/member geometry from a mouse drag.
- Viewer previews are non-authoritative; canonical mutation occurs only on explicit commit.
- All topology/coordinate edits are reversible, auditable, revalidated, and re-rendered.
- Existing delete confirmation remains mandatory for destructive delete.
- HR-1/HR-2/HR-4 portions use STRICT/Full TDD under the user's existing approval.
- No arbitrary Rotate, Mirror, full Copy Array, Trim, Extend, Offset, 3D solids, or section modeling in V1.
- Translational Repeat is limited to analytical node/member generation.
- Do not change source SketchUp coordinates during manual editing; operate only in canonical metre/Y-Up space.

---

### Task 16: SketchUp-Style Navigation + Selection Foundation

**Risk:** STANDARD

**Files:**
- Create: `src/staadprep/viewer/interaction.py`
- Create: `tests/unit/test_interaction_state.py`
- Create: `tests/ui/test_viewport_navigation.py`
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `src/staadprep/viewer/selection.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/ui/panels.py`

**Interfaces:**
- Produces `EditMode(StrEnum)`: `SELECT`, `CREATE_NODE`, `DRAW_MEMBER`, `MOVE_SNAP_NODE`, `DELETE`, `MEASURE`, `SET_DIRECTION`.
- Produces `SelectionFilter(nodes: bool = True, members: bool = True)`.
- Produces `LabelVisibility(node_numbers=False, member_numbers=False, local_x=False, coordinates=False)`.
- `StructuralViewport.set_edit_mode(mode: EditMode) -> None`.
- `StructuralViewport.set_selection_filter(filter: SelectionFilter) -> None`.
- `StructuralViewport.set_label_visibility(visibility: LabelVisibility) -> None`.
- Navigation contract: middle-drag orbit, Shift+middle-drag pan, wheel zoom, `Shift+Z` fit model; navigation does not change edit mode.

- [x] **Step 1: RED — lock interaction state and no-edit SELECT contract**

Create `tests/unit/test_interaction_state.py` with tests equivalent to:

```python
from staadprep.viewer.interaction import EditMode, InteractionState, SelectionFilter


def test_select_is_default_and_not_geometry_editing() -> None:
    state = InteractionState()
    assert state.mode is EditMode.SELECT
    assert not state.allows_geometry_drag


def test_move_snap_is_the_only_node_drag_mode() -> None:
    assert InteractionState(EditMode.MOVE_SNAP_NODE).allows_geometry_drag
    assert not InteractionState(EditMode.DRAW_MEMBER).allows_geometry_drag


def test_selection_filter_can_restrict_to_members() -> None:
    filter_ = SelectionFilter(nodes=False, members=True)
    assert not filter_.nodes
    assert filter_.members
```

Run:
`set PYTHONPATH=src&& <python> -m pytest -q tests/unit/test_interaction_state.py`

Expected RED: import/module/symbol missing.

- [x] **Step 2: GREEN — implement immutable interaction state**

Implement `viewer/interaction.py` using frozen dataclasses/enums; `allows_geometry_drag` returns true only for `MOVE_SNAP_NODE`.

Run the Step 1 command; expected PASS.

- [x] **Step 3: RED — navigation override and selection filters**

Create UI tests using a lightweight viewport test double plus a real-VTK subprocess smoke where needed. Assert:
- middle-button navigation callbacks do not change `EditMode`;
- Shift modifier selects pan behavior;
- selection filter blocks node selection when `nodes=False` and blocks member selection when `members=False`;
- overlapping pick candidates can be cycled deterministically;
- double-click focuses selected entity without model mutation.

Expected RED: viewport methods/state absent.

- [x] **Step 4: GREEN — wire navigation/selection/labels**

In `StructuralViewport`:
- preserve existing T10 picking lifecycle (`disable_picking()` before clear/rebuild);
- add interaction state only; do not add geometry mutation;
- map middle mouse / Shift+middle / wheel / fit-model to camera operations;
- use selected entity center as preferred orbit/focus pivot where supported by VTK/PyVista;
- add label actors driven from canonical numbers/coordinates;
- add deterministic overlap-candidate cycle order by entity type + stable UUID.

In `MainWindow`/panels:
- expose Node/Member selection toggles;
- expose Node No./Member No./Local-X/Coordinates view toggles;
- keep default mode `SELECT`.

- [x] **Step 5: Verify and commit**

Run targeted tests, real viewport smoke, Ruff, targeted mypy, and confirm a drag in SELECT produces no `ProjectModel.revision` change.

Commit:
`feat: add safe SketchUp-style viewport controls`

---

### Task 17: Snap / Inference + Axis Lock Engine

**Risk:** **STRICT HR-1 / HR-2**

**Files:**
- Create: `src/staadprep/editing/__init__.py`
- Create: `src/staadprep/editing/inference.py`
- Create: `tests/unit/test_inference.py`
- Create: `tests/unit/test_axis_lock.py`
- Modify: `src/staadprep/viewer/scene.py`
- Modify: `src/staadprep/viewer/widget.py`

**Interfaces:**
- Produces `SnapKind(StrEnum)`: `NODE`, `ENDPOINT`, `MIDPOINT`, `INTERSECTION`, `AXIS_X`, `AXIS_Y`, `AXIS_Z`, `WORK_PLANE`.
- Produces `AxisLock(StrEnum)`: `NONE`, `X`, `Y`, `Z`.
- Produces frozen `InferenceHit(position: Vec3, kind: SnapKind, entity_keys: tuple[UUID, ...], label: str)`.
- Produces `InferenceEngine.resolve(model, candidate_position, *, tolerance_m, axis_lock, reference_position=None) -> InferenceHit | None` for canonical-space deterministic inference; viewer projection only supplies the candidate/model-space ray hit.
- Axis locks constrain the final candidate in canonical STAAD X/Y/Z; Y is vertical.

- [x] **Step 1: RED — exact node/endpoint/midpoint inference**

Hand-author nodes and members and assert:
- within tolerance of existing node -> `NODE` at exact canonical node coordinate;
- midpoint request/hit -> exact member midpoint;
- outside tolerance -> no false node snap.

Run targeted test and confirm RED because engine is missing.

- [x] **Step 2: GREEN — deterministic spatial inference primitives**

Implement finite canonical-space calculations. Tie-break equal-distance candidates by stable UUID. Never mutate the model.

- [x] **Step 3: RED — intersection and axis lock**

Tests must independently calculate:
- two crossing line segments produce exact intersection hit;
- parallel/skew non-intersecting segments do not fabricate a hit;
- X lock preserves reference Y/Z and changes only X;
- Y lock preserves X/Z and changes only vertical Y;
- Z lock preserves X/Y and changes only Z.

- [x] **Step 4: GREEN — intersection/work-plane/axis labels**

Implement axis labels exactly `X AXIS`, `Y AXIS`, `Z AXIS`; Y UI helper text includes `Vertical`. Work-plane resolution must require an explicit plane/ray intersection; unresolved depth returns no committable hit.

- [x] **Step 5: Independent verification and commit**

Add a hand-calculated diagonal/intersection case independent from production helpers. Verify inference has no model revision/mutation. Run affected regression + Ruff + mypy.

Commit:
`feat: add deterministic structural snap inference`

---

### Task 18: Manual Node / Member Editing

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/repair/composite.py`
- Create: `src/staadprep/editing/manual_ops.py`
- Create: `tests/unit/test_manual_edit_commands.py`
- Create: `tests/unit/test_composite_repair.py`
- Create: `tests/ui/test_manual_edit_ui.py`
- Create: `tests/ui/test_manual_edit_smoke.py`
- Create: `scripts/smoke_manual_edit.py`
- Modify: `src/staadprep/repair/commands.py`
- Modify: `src/staadprep/repair/history.py`
- Modify: `src/staadprep/viewer/widget.py`
- Modify: `src/staadprep/ui/main_window.py`

**Interfaces:**
- Produces reversible `CreateNode(position: Vec3, node_key: UUID | None = None)`.
- Produces reversible `MoveNode(node_key: UUID, target: Vec3)`.
- Produces `CompositeRepair(commands: tuple[RepairCommand, ...], label: str)` with all-or-nothing apply and one history entry/Undo.
- Reuses existing `ConnectNodes`, `MergeNodes`, `DeleteNode`, `DeleteMember`, `SplitMember`, `ReverseMember`.
- Produces editing factories in `manual_ops.py` that return commands; UI must not mutate dictionaries/positions directly.

- [x] **Step 1: RED — CreateNode / MoveNode reversible invariants**

Tests assert CreateNode/MoveNode:
- increment revision once on apply;
- restore exact previous model/revision on revert;
- preserve unrelated UUIDs, member references, metadata;
- reject non-finite/invalid targets before mutation;
- `MoveNode` does not implicitly merge with another node.

- [x] **Step 2: GREEN — minimal reversible commands**

Implement using the existing `_ReversibleCommand` audit/revision conventions from T09.

- [x] **Step 3: RED — atomic composite operations**

Cover:
- create new node + connect member succeeds as one history entry;
- if connect would create duplicate/invalid member, created node is rolled back;
- split both crossing members around one intersection is atomic;
- one Undo restores the entire composite.

- [x] **Step 4: GREEN — CompositeRepair transaction**

Apply child commands in order; on failure revert already-applied children in reverse order before propagating the original error. Revert the successful composite in reverse child order. Audit exposes one parent operation plus child detail without losing command traceability.

- [x] **Step 5: RED — viewport manual-edit workflow**

UI tests assert:
- SELECT drag never mutates model/revision;
- DRAW MEMBER start-node -> existing end-node dispatches `ConnectNodes`;
- DRAW MEMBER to a valid new inference position dispatches one `CompositeRepair(CreateNode, ConnectNodes)`;
- MOVE/SNAP free release dispatches `MoveNode`;
- MOVE/SNAP release on existing node dispatches `MergeNodes`/snap semantics rather than co-located duplicate nodes;
- DELETE selected duplicate member removes only the selected member after confirmation;
- `Esc` cancels preview with no model mutation;
- middle-mouse navigation during an active draw/move preview does not cancel it.

- [x] **Step 6: GREEN — ghost preview + explicit commit**

Viewer owns ghost actors and edit gesture state only. Mouse move updates ghost geometry. Mouse release/click emits an operation request to `MainWindow`; `MainWindow` executes command through `RepairHistory`, then calls existing refresh/revalidate/rerender flow once.

- [x] **Step 7: Real smoke + strict verification + commit**

Real Qt/VTK smoke sequence:
1. load canonical dirty fixture;
2. draw one missing member;
3. move/snap one node;
4. select/delete one duplicate member;
5. Undo each operation and verify exact canonical graph restoration;
6. confirm navigation still works.

Run full relevant regression, Ruff, targeted mypy, independent graph comparison.

Commit:
`feat: edit analytical nodes and members in viewport`

---

### Task 19: Precision Create Node + Translational Repeat

**Risk:** **STRICT HR-2**

**Files:**
- Create: `src/staadprep/editing/create_node.py`
- Create: `src/staadprep/ui/create_node_dialog.py`
- Create: `tests/unit/test_create_node_specs.py`
- Create: `tests/unit/test_translational_repeat.py`
- Create: `tests/ui/test_create_node_dialog.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`

**Interfaces:**
- Produces `RelativeNodeSpec(reference_node: UUID, dx: float, dy: float, dz: float, create_member: bool)`.
- Produces `RepeatConnectionMode(StrEnum)`: `NONE`, `CONSECUTIVE`, `FROM_REFERENCE`.
- Produces `ExistingNodeResolution(StrEnum)`: `USE_EXISTING`, `SKIP_STEP`, `CANCEL`.
- Produces `TranslationalRepeatSpec(reference_node: UUID, dx: float, dy: float, dz: float, repeats: int, connection_mode: RepeatConnectionMode)`.
- Produces `build_relative_create(model, spec, tolerance_m) -> RepairCommand`.
- Produces `build_translational_repeat(model, spec, resolutions, tolerance_m) -> CompositeRepair`.

- [x] **Step 1: RED — exact XYZ and relative-coordinate math**

Independent expected-value tests use reference `(10,4,3)` and offset `(+1, -0, +0)` to require `(11,4,3)`. Reject non-finite values and a zero-length all-zero relative offset when it would create a duplicate reference node.

- [x] **Step 2: GREEN — pure spec-to-position calculation**

No UI/VTK dependency. Canonical Y remains vertical. Return/construct commands only after collision analysis succeeds.

- [x] **Step 3: RED — Create Member checkbox atomic behavior**

Assert unchecked creates only one node; checked creates node + reference->new member as one Undo item. If target matches existing node, do not create a duplicate; return a resolution-required result before mutation.

- [x] **Step 4: GREEN — relative-create command factory + dialog preview**

Dialog labels coordinates `STAAD X`, `STAAD Y (Vertical)`, `STAAD Z`, shows reference/current/result coordinates, `Create Member` checkbox, `Preview/Create/Cancel`. Preview uses ghost geometry only.

- [x] **Step 5: RED — Translational Repeat semantics**

For reference `(0,0,0)`, `dx=1`, repeats=5 require new positions exactly `1,2,3,4,5` metres and count excludes the reference. Test diagonal vector repeat. Test `CONSECUTIVE` incidence chain and `FROM_REFERENCE` star incidences independently.

Test collision resolution:
- `USE_EXISTING` reuses exact existing UUID;
- `SKIP_STEP` creates no node/member for that step and preserves deterministic subsequent positions;
- `CANCEL` returns no command and model stays unchanged.

- [x] **Step 6: GREEN — one atomic repeat history item**

Build the complete repeat command before applying it. Preview reports new-node count, new-member count, reused/skipped nodes, and final coordinate. One Undo reverts all repeat-created topology.

- [x] **Step 7: Strict verification and commit**

Use an independent frame-line test to compare exact UUID-coordinate/incidence sets after repeat and after Undo. Run targeted UI tests, Ruff, mypy, affected real viewport smoke.

Commit:
`feat: create precise repeated structural nodes`

---

### Task 20: Numbering + Member Direction Controls

**Risk:** **STRICT HR-2 / HR-4**

**Files:**
- Create: `src/staadprep/numbering/commands.py`
- Create: `src/staadprep/orientation/commands.py`
- Create: `src/staadprep/ui/model_controls.py`
- Create: `tests/unit/test_numbering_commands.py`
- Create: `tests/unit/test_orientation_commands.py`
- Create: `tests/ui/test_model_controls.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/viewer/widget.py`

**Interfaces:**
- Produces reversible `RenumberNodesCommand(policy: NumberingPolicy)`.
- Produces reversible `RenumberMembersCommand(policy: NumberingPolicy)`.
- Produces reversible `RenumberAllCommand(policy: NumberingPolicy)` as one history item.
- Commands expose preview maps before apply and reuse T12 `renumber_nodes` / `renumber_members` ordering; stable UUID keys and member endpoint UUID references never change.
- Produces `SetMemberStart(member_key: UUID, start_node_key: UUID)`; accepts only one of the member's existing endpoints and reverses incidence only when required.
- Produces factories for `Flip Selected`, `Auto Fix Selected`, `Auto Fix All` using existing T11 `ReverseMember`/normalization rules.

- [x] **Step 1: RED — reversible numbering maps**

Tests start from deliberately stale/random numbers. Assert preview UUID->new-number maps equal direct T12 deterministic maps; apply changes `.number` only; one Undo restores all previous numbers/revision; insertion order does not affect result.

- [x] **Step 2: GREEN — numbering commands**

Snapshot old numbers before apply. `RenumberAllCommand` performs node+member numbering as one atomic history entry. Do not rewrite UUID dictionary keys or member endpoints.

- [x] **Step 3: RED — explicit direction selection**

For member `i=A,j=B`:
- selecting `A` as Start is a no-op;
- selecting `B` as Start reverses to `i=B,j=A`;
- selecting unrelated node raises before mutation;
- geometry coordinates/UUID identities remain unchanged;
- Undo restores original incidence.

- [x] **Step 4: GREEN — direction commands + batch factories**

Reuse `ReverseMember`; do not invent new local-axis math. `Auto Fix All/Selected` follows T11 deterministic dominant-axis rules. Batch execution is atomic at the UI history level.

- [x] **Step 5: RED — model-controls UI**

Assert toolbar/menu exposes:
- Auto Node Number
- Auto Member Number
- Auto Number All
- Auto Fix Axis
- Auto Fix Selected
- Flip Selected
- Set Direction

Numbering opens Old->New preview before Apply. `Set Direction` requires one selected member, enters `SET_DIRECTION` mode, and endpoint click determines Start `(i)`. Local-X arrow preview is visible before apply.

- [x] **Step 6: GREEN — UI wiring + status refresh**

All actions route through commands/history, then revalidate/re-render once. No direct `.number`, `.start`, or `.end` assignments in UI code.

- [x] **Step 7: Strict verification and commit**

Independent test compares pre/post coordinate and topology sets to prove numbering changes only numbers and direction changes only incidence. Run T11/T12 regression, manual-edit regression, real viewport smoke, Ruff, mypy.

Final checkpoint 2026-08-29:
- independent invariants: passed;
- T20 targeted tests: **21 passed**;
- T11/T12 + manual-edit targeted unit regression: **54 passed**;
- fresh full regression, using isolated Windows-renderer processes where needed: **243 unit + 88 UI + 5 integration = 336 passed**;
- Ruff: passed;
- T20-local strict mypy: **0 issues in 5 affected source files** using `--follow-imports=silent`; four inherited `dxf_reader.py` errors remain outside T20 under full import-graph reporting;
- `git diff --check`: passed;
- task commit subject: `feat: control STAAD numbering and member direction`;
- T20 complete; do not start T21 until explicitly requested by the user.

Commit:
`feat: control STAAD numbering and member direction`

---

## Downstream V1 Tasks

After Task 20:

- **T21 — End-to-End READY Gate + Golden Suite + Audit Report** (renumbered from former T16). It must now exercise SketchUp-Ruby/Direct-DXF -> validate -> manual repair -> normalize/direction controls -> renumber controls -> READY -> `.STD` independent parser round-trip.
- **T22 — Windows Executable Packaging** (renumbered from former T17).
- **T23 — Real-Project Acceptance + STAAD.Pro Verification** (renumbered from former T18). Acceptance must include at least one manual geometry repair and confirm no unintended geometry edit from navigation/select operations.

## Plan Self-Review

- Spec coverage: navigation, explicit edit modes, selection filters/labels, snap/inference, axis locks, create/draw/move/snap/delete/split, exact/relative node creation, optional Create Member, Translational Repeat, numbering controls, member-direction controls, batch controls, atomicity/audit/undo are mapped to T16-T20.
- Scope boundary: Rotate/Mirror/full Copy Array/Trim/Extend/Offset/solids/section modeling remain excluded.
- Type consistency: T16 interaction types feed T17/T18; T17 inference types feed T18/T19; T18 `CompositeRepair` is consumed by T19/T20; T20 wraps the existing T11/T12 algorithms.
- Risk consistency: navigation-only T16 is STANDARD; coordinate/topology/direction/numbering mutation tasks remain STRICT under already approved HR-1/HR-2/HR-4.
- No implementation placeholders are intended; each Task defines named interfaces, RED behavior, GREEN implementation boundary, independent verification, and commit boundary.

## Downstream housekeeping

After T23 acceptance, main V1 plan Task 24 performs a non-destructive unused-file audit and moves verified-unused/superseded files to project-local `DEL/` with a manifest. Manual-editing implementation artifacts are eligible only when reference scans prove they are superseded; active implementation/tests remain protected.

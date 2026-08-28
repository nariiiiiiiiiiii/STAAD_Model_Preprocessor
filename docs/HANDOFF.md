Status: **T13 complete and merged to `master` at `d6dce33`; approved V1 plan has been expanded through T24, including post-acceptance unused-file quarantine. T14 is next and not started.**

## Canonical project root

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

HARD RULE: all source/temp/cache/log/build/test/generated/exported files remain inside this root.

## Product pipeline — approved V1 continuation

`SKP / DXF -> unit/axis -> canonical topology -> validate -> Quick Fix / Manual Edit -> direction -> numbering -> READY -> STAAD .STD -> STAAD.Pro`

The app is now explicitly planned as a **focused analytical line-model editor + preprocessor**, not only an issue console. It must still NOT become a general CAD/BIM/solver application.

Canonical model/editing space:
- metre,
- STAAD Y-Up (`Y` vertical),
- stable Node/Member UUID identities,
- STAAD-facing numbers are attributes only.

## Completed commits T01-T13

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
- T13 `d6dce33` — `feat: export validated STAAD geometry model`

T13 was fast-forwarded into `master` before the V1 planning expansion.

## T13 locked exporter contract

Minimal deterministic geometry subset:

```text
STAAD SPACE
UNIT METER KN
JOINT COORDINATES
<node-number> <X> <Y> <Z>;
MEMBER INCIDENCES
<member-number> <start-node-number> <end-node-number>;
FINISH
```

Exporter fails closed for empty model, invalid/missing/duplicate numbering, dangling references, or validation `ERROR`. It never auto-repairs or auto-renumbers. Warnings are reported but may export.

Latest T13 completion evidence before commit:
- 173 pytest regression tests passed in the fresh non-interactive run;
- real Qt/VTK viewport / issue-repair / orientation smoke trio: 3 passed;
- Ruff passed;
- targeted mypy passed;
- independent T12 -> T13 parse check passed;
- T13 doc gate passed;
- `git diff --check` passed.

Target STAAD.Pro open/acceptance is still intentionally pending and now belongs to **T23**.

## Approved Manual Editing design

Canonical design:
`docs/superpowers/specs/2026-08-28-manual-model-editing-design.md`

Detailed implementation plan:
`docs/superpowers/plans/2026-08-28-manual-model-editing-v1.md`

### Navigation

SketchUp-style baseline:
- Middle Mouse drag = Orbit
- Shift + Middle Mouse drag = Pan
- Wheel = Zoom
- Shift+Z = Fit / Zoom Extents

Navigation works as an override during edit tools and must not cancel active ghost preview.

**Critical safety rule:** default `SELECT` mode cannot move structural geometry by drag.

### Editing modes

- SELECT
- CREATE NODE
- DRAW MEMBER
- MOVE / SNAP NODE
- DELETE
- MEASURE
- SET DIRECTION

Ghost preview is non-canonical. `Esc` cancels without model mutation. Commit always routes through reversible/auditable command/history and triggers revalidation/rerender.

### Manual geometry baseline

User must be able to:
- draw a missing Member between existing Nodes;
- draw from an existing Node to a newly created Node atomically;
- move a Node;
- drag/snap/merge a floating Node onto an existing Node;
- select exact overlapping Member and delete only that Member;
- split Member at midpoint/percentage/distance/intersection;
- Undo/Redo manual operations.

### Snap / inference

Targets:
- existing Node,
- endpoint,
- midpoint,
- intersection,
- X / Y / Z axis,
- active working plane/grid.

Axis locks: X, Y (Vertical), Z. Unresolved 3D depth must not be guessed.

### Create Node

Supported:
1. Click / Snap
2. Exact STAAD XYZ
3. Relative to selected reference Node
4. Translational Repeat

Relative dialog example:

```text
Reference Node: 21
X [ + ] [ 1.000 ] m
Y [ - ] [ 0.000 ] m
Z [ + ] [ 0.000 ] m

[ ] Create Member
```

If `Create Member` is checked, Reference Node -> New Node is created atomically with the Node.

### Translational Repeat

- per-step ΔX/ΔY/ΔZ;
- repeat count = NEW positions only, excluding reference Node;
- optional member creation;
- default `Connect Consecutive Nodes`;
- optional `Connect From Reference Node`;
- collision preview/resolution before commit;
- one atomic history item / one Undo.

This is intentionally narrow and is NOT a full CAD Copy Array.

### Numbering controls

- Auto Node Number
- Auto Member Number
- Auto Number All
- Old -> New preview
- reversible history operation

Reuses T12 deterministic rules. UUID identities and endpoint UUID references never change.

### Member direction controls

- Auto Fix Axis All
- Auto Fix Axis Selected
- Flip Selected
- Set Direction by selecting Member then clicking endpoint that shall become Start `(i)`

Reuses T11 incidence/local-X logic; geometry does not move.

### View / selection support

- Node / Member selection filter
- overlap candidate cycling/chooser
- Ctrl additive selection
- double-click Focus/Zoom
- Node Number / Member Number / Local-X / Coordinates toggles
- context menu by entity type

## V1 scope boundary — explicitly remain OUT

Do not add before V1 acceptance:
- arbitrary Rotate geometry,
- Mirror,
- full Copy Array / radial/general transform array,
- Trim,
- Extend,
- Offset,
- 3D solids/surfaces,
- section-shape modeling,
- solver/FEM,
- load/design systems,
- BIM/IFC authoring.

## Revised task sequence

T01-T13 COMPLETE.

Next sequence:
- T14 — SKP bridge contract + native helper probe — STANDARD
- T15 — Direct SKP extraction + transform/topology integration — STRICT HR-1/HR-2
- T16 — SketchUp-style navigation + selection/labels — STANDARD
- T17 — Snap/inference + working plane + axis locks — STRICT HR-1/HR-2
- T18 — Manual Node/Member editing + atomic repair UI — STRICT HR-2
- T19 — Exact/Relative Create Node + Translational Repeat — STRICT HR-2
- T20 — Numbering + member-direction controls — STRICT HR-2/HR-4
- T21 — End-to-End READY gate + golden suite + audit — STRICT HR-1..HR-4
- T22 — Windows executable packaging — STANDARD
- T23 — Real-project + target STAAD.Pro acceptance — STRICT acceptance
- T24 — unused/superseded file audit + move to project-local `DEL/` for user deletion — STANDARD

## Important risk/approval state

The user's existing explicit STRICT approvals for HR-1 through HR-4 remain applicable. The new manual-editing tasks are classified within those existing risk domains:
- coordinate/inference: HR-1/HR-2,
- topology/manual repair: HR-2,
- direction/incidence: HR-2,
- numbering: HR-4.

If implementation discovers a new high-risk behavior outside those approved categories, stop and request a new approval.

## Next task

**T14 — SKP Bridge Contract + Native Helper Capability Probe**

Risk: STANDARD.

T14 must remain isolated from exporter/manual-edit semantics. It defines the native-helper boundary and must fail gracefully if the official SketchUp SDK is absent.

## T24 cleanup boundary

T24 runs only after T23 acceptance. It audits the accepted workspace, proves candidates unused/superseded, and moves only those candidates to `STAAD_Model_Preprocessor/DEL/`. It never deletes files. `DEL/UNUSED_FILES_MANIFEST.md` must preserve original paths/reasons/evidence so the user can review and delete later. Protected: `.git`, active `.worktrees`, current `.venv`, required `vendor` SDK, and acceptance evidence.

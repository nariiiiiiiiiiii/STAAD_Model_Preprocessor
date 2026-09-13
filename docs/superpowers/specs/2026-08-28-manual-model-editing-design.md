# Manual Model Editing + SketchUp-Style Viewport Design
> Historical design record: approved scope and decisions are preserved as recorded; current implementation/release status is in [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

Date: 2026-08-28
Status: **APPROVED design baseline for V1 continuation**

## Goal

Extend STAAD Model Preprocessor from issue-first cleanup into a focused analytical line-model editor so the user can repair missing/incorrect nodes and members directly in the 3D viewport without returning to SketchUp or STAAD.Pro for routine geometry cleanup.

The application remains a preprocessor, not a general CAD/BIM modeler.

## Canonical safety boundary

- The canonical `ProjectModel` remains the only geometry source of truth.
- Manual edits MUST execute through reversible/auditable commands; viewport actors are previews only.
- Dragging or drawing MUST NOT mutate the canonical model until commit/release.
- `Esc` cancels an in-progress edit without changing the model.
- Every committed edit revalidates and re-renders the affected model.
- Destructive delete remains confirmed.
- Manual topology/coordinate editing is covered by approved **STRICT HR-1 / HR-2** verification.
- Numbering controls are covered by approved **STRICT HR-4** verification.
- Member incidence/local-X controls are covered by approved **STRICT HR-2** verification.

## Interaction modes

The viewport has explicit editing modes:

- `SELECT` — default; never moves geometry.
- `CREATE NODE`
- `DRAW MEMBER`
- `MOVE / SNAP NODE`
- `DELETE`
- `MEASURE`
- `SET DIRECTION`

Entering an edit mode is required before a left-drag can change geometry. A normal select click/drag can never move a node.

## SketchUp-style navigation

Navigation is available regardless of edit mode and temporarily overrides the active editing interaction:

- Middle Mouse drag: Orbit.
- Shift + Middle Mouse drag: Pan.
- Mouse Wheel: Zoom.
- `Shift+Z`: Zoom Extents / Fit Model.
- Orbit pivot preference: selected entity center -> entity under cursor/focal hit -> current camera focal point.
- Wheel zoom targets the current cursor/focal region where practical.
- Releasing Middle Mouse returns to the previous edit operation without cancelling its preview.

## Selection behavior

- Left click selects an entity in `SELECT` mode.
- Ctrl + Left click toggles additive selection.
- Selection filters allow `Node`, `Member`, or both.
- When multiple entities overlap under the cursor, the user can cycle or choose the exact entity.
- Double-click entity: Focus / Zoom Selected.
- Context menus expose only valid operations for the selected entity.

Member context menu baseline:
- Reverse Direction
- Set Start Node
- Delete Member
- Zoom Selected
- Properties

Node context menu baseline:
- Move Node
- Connect Member From Here
- Create Node Relative To This Node
- Delete Node when valid
- Zoom Selected
- Properties

## View labels and visual aids

Toggleable overlays:
- Node Number
- Member Number
- Local-X Arrow
- Coordinates
- XYZ triad
- optional working grid/plane

Ghost nodes/members are visually distinct from committed geometry.

## Snap / inference

Manual drawing and movement use an inference engine rather than guessing 3D depth.

Supported targets:
- existing Node
- member endpoint
- member midpoint
- member intersection
- X axis
- canonical Y axis (vertical)
- Z axis
- current working plane / grid

The cursor shows the active inference label, e.g. `NODE 25`, `MIDPOINT`, `INTERSECTION`, `X AXIS`, or `Y = 4.000 m`.

Axis lock shortcuts:
- `X`: lock movement/drawing to canonical X
- `Y`: lock to canonical Y (vertical)
- `Z`: lock to canonical Z
- `Esc`: cancel current edit/lock operation

Distance entry while axis-locked is supported for precise placement.

The UI must explicitly label the coordinate convention as `STAAD X / STAAD Y (Vertical) / STAAD Z` to avoid confusion with SketchUp Z-Up source axes.

## Manual geometry operations

### Draw Member

1. Activate `DRAW MEMBER`.
2. Select/click start node.
3. Show ghost member to cursor/inference target.
4. Click existing end node or a valid new-node position.
5. Commit atomically.

If a new end node is required, node creation + member creation is one atomic operation. If member creation fails, the new node is rolled back.

Duplicate member creation fails closed and reports the existing member.

### Move / Snap Node

- Available only in `MOVE / SNAP NODE` mode.
- Left-drag shows a ghost node/connected-member preview; canonical coordinates remain unchanged until mouse release.
- Release in free valid space -> move node.
- Release on an existing node -> Snap/Merge operation, not two canonical nodes at one coordinate.
- `Esc` cancels and restores the visual preview without model mutation.
- Middle Mouse navigation remains available during the drag workflow.

### Delete selected geometry

- Select exact node/member, including cycling overlapping entities.
- `Delete` or Delete tool invokes the appropriate repair command.
- Destructive confirmation remains required.
- Deleting one of two overlapping duplicate members is supported directly.
- Undo restores the deleted entity.

### Split at midpoint / distance / intersection

For a selected member:
- At Midpoint
- At Percentage
- At Distance from Start
- At Intersection

Each operation is atomic and results in correct canonical nodes/member incidences.

## Create Node

`CREATE NODE` supports four creation paths.

### 1. Click / Snap

- Existing node hit: use existing node; do not create a duplicate.
- Member hit: create/split at the inferred point.
- Intersection hit: create canonical intersection node and split affected member(s) atomically.
- Free-space hit: create on the active working plane/inference constraint only; never guess arbitrary depth.

### 2. Exact XYZ

Dialog accepts exact canonical metre coordinates:
- STAAD X
- STAAD Y (Vertical)
- STAAD Z

Preview is shown before commit.

### 3. Relative to selected Node

Example reference: Node 21.

Inputs use per-axis direction + distance:

```text
Reference Node: 21
X [ + ] [ 1.000 ] m
Y [ - ] [ 0.000 ] m
Z [ + ] [ 0.000 ] m
```

The dialog shows reference coordinates and computed result coordinates before creation.

Optional checkbox:

`Create Member — From: Reference Node -> To: New Node`

If checked, node + member creation is one atomic operation.

If the target coordinate matches an existing node within model tolerance, the UI reports the matching node and offers `Use Existing Node` or `Cancel`; it must not silently create a duplicate.

### 4. Translational Repeat

A focused STAAD-like translational repeat is included only for node/member creation; it is NOT a general CAD copy-array system.

Inputs:
- per-step `ΔX / ΔY / ΔZ`
- repeat count = number of new node positions, excluding the reference node
- optional `Create Member`
- connection mode:
  - `Connect Consecutive Nodes` — default
  - `Connect From Reference Node`

Example: `ΔX=+1m`, repeat=5 creates five new nodes at +1,+2,+3,+4,+5 m.

The viewport previews all ghost nodes/members plus counts and last-node coordinates.

If a repeated target coincides with an existing node, the preview identifies it and requires a defined resolution (`Use Existing`, `Skip Step`, or `Cancel Repeat`) before commit.

The entire repeat is one atomic history item: one Undo removes/reverts the whole repeat.

## Numbering controls

Provide separate commands:
- `Auto Node Number`
- `Auto Member Number`
- `Auto Number All`

Behavior:
- reuses deterministic T12 ordering/policy;
- shows an `Old -> New` mapping preview before apply;
- changes STAAD-facing `.number` only; stable UUID identities/member endpoint UUID references never change;
- is reversible as one history action per requested numbering operation.

## Member incidence / local-X controls

Provide:
- `Auto Fix All` — T11 deterministic direction rule over all applicable members.
- `Auto Fix Selected` — same rule for selected members.
- `Flip Selected` — reverse incidence for selected member(s).
- `Set Direction` — select one member then click the endpoint that must become Start `(i)`; the other endpoint becomes End `(j)`.

The viewport previews local-X arrows before apply. `Set Direction` changes incidence only and never moves geometry.

Local-Y/local-Z/Beta/section rotation remain outside this V1 manual-editing addition unless required by a separate approved scope.

## Batch operations

V1 batch operations are deliberately narrow:

Members:
- Delete Selected
- Flip Selected
- Auto Fix Axis Selected

Nodes:
- Delete Selected when structurally valid
- Move selected nodes by exact `ΔX / ΔY / ΔZ` only if included by the Task implementation and covered by the same atomic safety rules

No general arbitrary CAD transform stack is introduced.

## Toolbar grouping

```text
FILE
Import | Save | Export STD

EDIT
Select | Create Node | Draw Member | Move/Snap | Delete

MODEL
Auto Node No. | Auto Member No. | Auto Number All
Auto Fix Axis | Flip Selected | Set Direction

VIEW
Node No. | Member No. | Local-X | Coordinates | Fit Model

TOOLS
Measure | Validate
```

## Explicitly out of V1

The following remain out of scope even after this addition:
- arbitrary Rotate geometry tool
- Mirror geometry
- full Copy Array / radial array / general transform array
- Trim
- Extend
- Offset
- 3D solids / surfaces
- section-shape modeling
- BIM/IFC authoring
- structural analysis/solver
- load generation/combinations/design

The approved `Translational Repeat` is a narrow node/member generation workflow, not a general copy-array feature.

## Acceptance criteria

The manual-editing subsystem is V1-ready when all are true:

1. Select mode cannot accidentally drag/move a node.
2. SketchUp-style orbit/pan/zoom works while edit tools are active.
3. User can create a node, draw a missing member, move/snap a node, and delete an overlapping duplicate member entirely in-app.
4. User can create exact/relative nodes and translational repeats with optional members.
5. Snap/inference never commits arbitrary unresolvable 3D depth.
6. Manual mutations are atomic, auditable, undoable, revalidated, and re-rendered.
7. Node/member numbering can be applied separately or together with mapping preview.
8. User can auto-fix all/selected member incidence, flip selected, and explicitly choose Start `(i)` by endpoint.
9. Labels/filters make entity identity unambiguous during editing.
10. End-to-end clean model still passes final READY gate and deterministic `.STD` export.

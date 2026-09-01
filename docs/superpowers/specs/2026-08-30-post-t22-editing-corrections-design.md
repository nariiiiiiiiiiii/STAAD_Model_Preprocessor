# Post-T22 Editing Corrections Design

**Status:** STRICT implementation and package verification complete; historical package checkpoint
superseded for current acceptance by later user-accepted, fully verified source follow-ups
**Risk:** Mixed — STANDARD UI/view work plus STRICT analytical graph/coordinate mutation work

**Historical evidence (2026-08-31):** 325/325 unit+integration, 111/111 UI, real
viewport/manual/precision smokes, Ruff, strict mypy, package gates 4/4, manifest 811/811, and
extracted-ZIP launch pass. The quarantined `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` does not contain every later accepted
source follow-up and is not the current acceptance target; checkpoint changes remain uncommitted.

## Goal

Correct the ten behaviors reported during real portable-package testing without silently changing structural connectivity, coordinates, numbering, ReadyGate rules, or `.STD` semantics.

## Diagnosed causes and required behavior

| # | Reported behavior | Diagnosed cause | Required behavior |
|---|---|---|---|
| 1 | Reset View must follow STAAD.Pro axes | Current code calls generic `view_isometric()` | Reset to canonical Y-up isometric: camera in positive X/Y/Z octant, focal point at model center, view-up `(0, 1, 0)`, then fit and reset clipping. |
| 2 | Created Node cannot be deleted | Delete command exists, but selection filter/mode can prevent selecting the Node | Delete an orphan selected Node through one confirmed reversible command. Connected Nodes remain fail-closed unless their selected incident Members are deleted in the same atomic operation. |
| 3 | Delete key does nothing | No Delete-key action is registered | `Del` routes to the same confirmed deletion command as toolbar/context Delete; text-entry widgets keep normal Delete behavior. |
| 4 | Add Crop to Selection | Only Focus Selected exists and is context-menu-only | Add `Crop to Selection` to toolbar/context; frame the selected Node/Member bounds without mutating or hiding model data. |
| 5 | Properties stays blank | viewport selection signals are not connected to the panel; panel supports issues only | Show exact Node/Member type, STAAD number, UUID, coordinates/endpoints, length, group/source, and a compact mixed-selection summary. Clear after model refresh/deletion. |
| 6 | Split cannot be merged; Member cannot be deleted | Delete path is difficult to reach; no inverse merge command exists | Delete selected Member(s). Merge exactly two collinear Members sharing one degree-2 Node; reject branches, non-collinearity, incompatible selection, or missing entities. Command is atomic and undoable. |
| 7 | Orphan Node cannot be removed/fixed | toolbar `Auto Fix Selected` means direction normalization, not issue repair | Rename direction command to remove ambiguity. Orphan issue quick fix and selected-orphan Delete both execute the same safe `DeleteNode` path with confirmation and Undo. |
| 8 | Translational Repeat cannot use Member | dialog requires exactly one selected reference Node | Add selected-Member repeat that copies the selected subgraph by STAAD ΔX/ΔY/ΔZ and repeat count, preserves shared incidence inside the selection, creates no duplicate incidence, previews exact counts, and applies as one reversible history item. |
| 9 | Create Node appears twice | mouse mode and exact-coordinate dialog share nearly identical labels | Rename to `Create Node (Click)` and `Create Node (XYZ)…`; keep both because they are distinct workflows. |
| 10 | Draw/Move/Delete modes appear unusable | mode activation does not set a compatible selection filter; screenshot has Members-only while Node-driven mode is active | Activating Draw or Move enables Node picking; Delete enables Node + Member picking; mode obtains viewport keyboard focus and displays an instruction/status message. |

## Selection and action contract

- Selection changes emit one `selection_changed(nodes, members)` signal after select, toggle, clear, filter pruning, model refresh, and command refresh.
- Properties reads immutable model entities from `MainWindow`; the viewport never formats engineering properties.
- `Create Node (Click)`, Draw Member, and Move/Snap force a Node-capable filter.
- Delete forces Nodes + Members and accepts current selection without requiring a second destructive click.
- `Del` is ignored while focus is inside `QLineEdit`, `QTextEdit`, `QPlainTextEdit`, spin boxes, or editable combo boxes.
- Every mutation runs through `RepairHistory`, is confirmed when destructive, refreshes validation, and remains undoable.

## Merge Members contract

- Exactly two Members are selected.
- They share exactly one Node.
- The shared Node has model degree exactly two.
- Their vectors are collinear within the existing metre tolerance and extend in opposite directions from the shared Node.
- The lower UUID Member is retained. Its number, group, source reference, and direction determine the merged Member identity/direction.
- The second Member and shared Node are removed atomically.
- Undo restores the exact two Members, shared Node, metadata, UUIDs, and prior model revision.

## Selected-Member Translational Repeat contract

- One or more selected Members define a source subgraph and its unique endpoint Nodes.
- Each repeat step translates every source Node by the same finite STAAD ΔX/ΔY/ΔZ.
- Each source Member is recreated between the translated endpoint mapping; shared Nodes stay shared.
- New Members preserve `group` and `source_ref`; STAAD numbers remain unset until numbering.
- Any collision with an existing Node/Member is previewed and requires explicit resolution; no silent merge, overwrite, or duplicate incidence is allowed.
- Apply and Undo each form one atomic history item and restore the exact graph/revision.

## Verification level

STANDARD:
- canonical camera/reset and Crop to Selection;
- selection signal and Properties rendering;
- distinct toolbar labels, active mode/filter synchronization, status guidance.

STRICT / Full TDD after explicit approval:
- Delete Node/Member and Delete-key execution;
- Draw Member and Move/Snap end-to-end mutation paths;
- orphan quick fix;
- Merge Members;
- selected-Member Translational Repeat.

STRICT evidence must include RED/GREEN tests, exact UUID-coordinate-incidence assertions, exact revision/audit/Undo restoration, invalid-selection and branch/collision rejection, isolated real Qt/VTK interaction tests, relevant regression, Ruff, strict mypy, standalone rebuild, exact manifest verification, and extracted-ZIP launch.

## Out of scope

- deleting a connected Node while silently retaining or rewiring unselected Members;
- merging non-collinear Members or a Node with degree other than two;
- structural analysis/design calculations;
- changes to coordinate conversion, ReadyGate, numbering policy, or `.STD` output semantics.

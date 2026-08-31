# Project Explorer Entity Selection Design

**Date:** 2026-08-31  
**Status:** Source implemented, verified, and user accepted  
**Verification level:** STANDARD

## Goal

Make the Project Explorer useful for locating and selecting canonical Nodes and
Members without changing model geometry or connectivity.

## Behavior contract

- `Nodes (N)` and `Members (N)` are expandable tree groups.
- Their children are rebuilt from the current canonical model after import,
  repair, undo, redo, or validation refresh.
- Numbered entities are listed in ascending STAAD number order. Unnumbered
  entities follow in stable UUID order and display `No. —`.
- Clicking a Node child selects and highlights exactly that Node.
- Clicking a Member child selects and highlights exactly that Member.
- Clicking the `Nodes (N)` group expands it when collapsed and selects all
  Nodes. `Members (N)` behaves the same way.
- Explorer selection activates Select mode and the matching Node/Member filter.
- The existing viewport selection callback updates Properties and action state.
- The feature does not crop, reset, or otherwise move the camera.
- Selection from the viewport does not need to synchronize the current tree row
  in this patch.
- No compiler or portable package rebuild is performed until the user approves
  the source behavior.

## Safety

This feature only changes UI selection state. It does not execute commands,
mutate topology, edit coordinates, renumber entities, or write model data.

## Acceptance checks

1. Node and Member child labels and ordering match the current model.
2. Clicking one child highlights only its entity and updates Properties.
3. Clicking a group highlights every entity of that kind.
4. Repeated model refresh does not duplicate child rows.
5. Existing UI selection, repair-refresh, and import-flow tests still pass.

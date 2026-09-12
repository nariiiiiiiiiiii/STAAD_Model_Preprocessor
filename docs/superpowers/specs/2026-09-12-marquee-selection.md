# Marquee Selection and Zoom in Select — Behavior Specification

## User request

Add a **Crop to Select** viewport mode: the user chooses Nodes, Members, or both with the existing
selection-filter controls, then holds the left mouse button and drags a rectangular marquee in the
model view. Rename the existing camera-framing command **Zoom in Select** and preserve its current
behavior.

## Expected behavior

- Existing `Nodes` and `Members` filters determine which entity types a marquee may select. Both
  enabled selects both types.
- With **Crop to Select** active, left-drag draws a visible rectangle and selects eligible Nodes
  whose projected positions lie in it and Members whose projected line segments intersect it.
- A normal drag replaces selection; Ctrl-drag adds to the existing selection, matching the current
  Ctrl+click convention. A click shorter than the drag threshold keeps existing point-pick behavior.
- Escape cancels the in-progress rectangle without changing selection. Middle-drag orbit/pan and
  all non-Select editing tools retain their current behavior.
- The operation updates only selection/highlights/Properties; it must not mutate or hide model data.
- The old camera-framing action and viewport-context-menu command are named **Zoom in Select** and
  continue to frame selected Nodes/Members without hiding geometry.

## Scope boundary

This is selection and camera UI only. Do not modify topology, geometry, repair commands, export
semantics, file paths, or package version. Do not compile or package.

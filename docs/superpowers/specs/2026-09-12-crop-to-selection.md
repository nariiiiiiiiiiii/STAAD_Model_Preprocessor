# Crop to Selection — Behavior Specification

## User-reported issue

The owner reports that **Crop to Selection** does not work in the desktop app.

## Expected behavior

- With one or more Nodes or Members selected, Crop to Selection frames the selected world-space
  bounds in the viewport.
- A single Node or another degenerate/small selection remains visible at a useful zoom level; the
  camera must not collapse to an effectively zero distance.
- The operation changes only the camera. It does not hide unselected geometry, mutate the canonical
  model, alter selection, or change the active edit mode.
- With no selection, the action remains disabled or safely performs no operation.

## Current reproduction evidence

In the real PyVista viewport on the demo frame, selecting its first Node and cropping moved the
camera distance from **40.291960753** to **0.000006692** world units. The current absolute padding
floor (`1e-6`) is too small for a point-only selection. Cropping a selected Member reduced the
camera distance from 40.291961 to 9.132735 and did visibly reframe it. The source fix uses an 8%
selected-span margin and a 2% full-scene minimum; the isolated smoke now asserts a selected-Node
focal target, non-degenerate camera distance, and unchanged model revision. Owner visual retest is
still pending.

## Scope boundary

This is a viewport-only correction. Do not change analytical geometry, selection semantics, model
visibility, file persistence, or package version. Do not compile or package.

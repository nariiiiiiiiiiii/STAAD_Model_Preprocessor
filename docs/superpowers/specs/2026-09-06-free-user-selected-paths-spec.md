# Free User-Selected Import and STD Export Paths
> Historical design record: approved scope and decisions are preserved as recorded; current implementation/release status is in [HANDOFF](../../HANDOFF.md) and [INDEX](../../INDEX.md).

**Scope:** SketchUp Bridge JSON import/output and STAAD `.STD` export.

The default inbox and export locations remain unchanged, but an explicit path chosen by the user
may be outside the project root. Project JSON Save/Open and application-managed runtime files remain
project-local. Geometry, topology, validation, ReadyGate, numbering, and `.STD` serialization are
unchanged. Source verification must complete before a new portable package is assembled.

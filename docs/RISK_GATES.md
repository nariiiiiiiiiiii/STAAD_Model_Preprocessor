# RISK GATES

Verification policy: risk-based.

## FAST
Use for:
- wording,
- colors/layout spacing,
- icons,
- non-functional UI polish,
- documentation-only corrections.

Verification:
- launch/build affected UI,
- focused visual smoke check.

## STANDARD — default
Use for:
- normal UI behavior,
- project save/load plumbing,
- file-selection flow,
- viewer selection/highlighting,
- issue-console binding,
- adapter orchestration that does not alter engineering semantics,
- packaging/configuration.

Verification:
- targeted tests where useful,
- lint/type-check,
- affected-component launch/build,
- focused regression checks.

## STRICT / Full TDD — mandatory approval gate

The following are high-risk because a defect may produce an apparently clean model whose analytical geometry is actually wrong.

### HR-1 Unit / coordinate transformation
Scope:
- source-unit conversion,
- scale correction,
- SketchUp Z-Up -> canonical STAAD Y-Up transform,
- coordinate rounding/tolerance policy.

Failure impact:
- wrong member lengths,
- mirrored/flipped structure,
- wrong elevations,
- unsafe downstream engineering assumptions.

Proposed verification:
- RED/GREEN tests,
- hand-calculated coordinate/length fixtures,
- inverse-transform checks,
- known mm/m/inch conversion cases,
- axis-direction fixtures,
- golden model extents.

### HR-2 Topology / connectivity detection and automatic repair
Scope:
- node merging/snap,
- connected components,
- split-at-intersection,
- gap repair/connect,
- duplicate handling,
- orphan handling where deletion/connectivity is automated,
- mutation commands affecting the analytical graph.

Failure impact:
- unintended member connectivity,
- missing or extra nodes/members,
- structure that looks visually connected but is analytically wrong,
- incorrect load path after import into STAAD.Pro.

Proposed verification:
- RED/GREEN tests for each graph mutation,
- independent graph invariants before/after,
- golden dirty models,
- undo round-trip checks,
- property-based invariants where useful,
- manual inspection of representative fixtures.

### HR-3 STAAD `.STD` exporter semantics
Scope:
- UNIT output,
- JOINT COORDINATES,
- MEMBER INCIDENCES,
- numbering/reference mapping,
- supported syntax subset.

Failure impact:
- STAAD parser errors,
- wrong analytical geometry,
- member/node references pointing to the wrong entities.

Proposed verification:
- RED/GREEN exporter tests,
- byte/text golden expected `.STD` files,
- independent model->text->parsed-fixture consistency checks,
- target STAAD.Pro open/import verification before calling the exporter production-ready.

### HR-4 Deterministic renumber/reference rewrite
Scope:
- node renumber,
- member renumber,
- atomic update of all references,
- old->new mapping.

Failure impact:
- stale member incidences,
- wrong references,
- exported geometry corruption.

Proposed verification:
- permutation fixtures,
- referential-integrity invariants,
- stable/deterministic repeated-run test,
- mapping audit verification.

## Approval state

Current state: NOT YET APPROVED FOR HIGH-RISK IMPLEMENTATION.

Low-risk/standard foundation and UI shell may proceed after written-spec review.

Before implementing HR-1 through HR-4, explicitly ask the user:

`Proceed with STRICT / Full TDD for these high-risk components?`

Do not implement or test their real engineering semantics until approval is received.

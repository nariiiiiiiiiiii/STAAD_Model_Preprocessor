# RISK GATES

Verification policy: risk-based.

Current gate state (2026-08-31): the explicitly approved post-T22 HR-2 correction scope completed
STRICT source verification and its source behavior is user accepted. Full source verification is
complete; the user authorized compile step 1 and Nuitka compilation completed successfully.
Portable assembly and ZIP creation are complete under `dist/post-t22-refresh-save-final/`;
package-only verification is **7/7 PASS**; real package acceptance is PASS and T23 target-STAAD.Pro
acceptance is **PASS by user report (2026-09-01)**. T24 inventory and reference/evidence mapping are
complete; the approved Step 4 move, post-move reference scan, targeted package verification, and
final documentation synchronization are complete, no files were deleted. The post-T24 worktree
mindmap is recorded at `docs/WORKTREE_MINDMAP.md`; no new implementation task is started by it.

The Project Explorer entity inventory/select-one/select-all increment is STANDARD because it only
changes UI selection/highlighting and does not execute a repair or mutate the analytical model.
The UUID-free engineering Properties increment is also STANDARD because it formats existing model
values for display and does not calculate or mutate engineering data.

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

## STRICT / Full TDD

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

Verification:
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

Verification:
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

Verification:
- RED/GREEN exporter tests,
- byte/text golden expected `.STD` files,
- independent model->text->parsed-fixture consistency checks,
- target STAAD.Pro open/import verification before calling the exporter production-ready.

### HR-4 Deterministic renumber/reference rewrite
Scope:
- node renumber,
- member renumber,
- atomic reference integrity,
- old->new / UUID->STAAD-number mapping.

Failure impact:
- stale member incidences,
- wrong references,
- exported geometry corruption.

Verification:
- permutation fixtures,
- referential-integrity invariants,
- stable/deterministic repeated-run test,
- mapping audit verification.

## Approval state

Current state: **APPROVED**.

Approval received from the user on **2026-08-28** for:
- the current `PROJECT_SPEC`, and
- STRICT / Full TDD implementation of HR-1 through HR-4 defined in this document.

Additional explicit approval was received on **2026-08-30** for the post-T22 HR-2 correction
scope: multi-selection delete, orphan removal, Merge Members, and selected-Member Translational
Repeat. Those changes require graph invariants, duplicate-incidence rejection, exact Undo
round-trips, focused integration tests, and relevant regression before packaging.

This approval applies to the scoped V1 behaviors above. If implementation discovers a new high-risk behavior outside HR-1 through HR-4, stop and request a new explicit approval before implementing that new risk area.

Execution remains task-gated: complete one Task, verify, commit, update HANDOFF, then stop for user review before starting the next Task.


## 2026-08-31 source handoff checkpoint

- User-accepted source behavior before handoff: Member Translational Repeat preview, engineering Properties, Project Explorer entity selection, Member Local Axes XYZ, three-row toolbar with visible View controls, Save/Open Project JSON, import-derived save filename, `SAVED` / `NOT SAVED` title state, Ctrl+S save confirmation, readable Node/Member/Coordinate labels, Global Axis X/Y/Z labels, and Exit confirmation UI.
- Latest real-user defect: clicking window `X` and choosing `Yes` did not close the application.
- Latest source fix: exit dialog now compares the native Qt button result with equality (`==`) and the accepted close path delegates to `QMainWindow.closeEvent()`.
- Exit regression evidence after fix: `tests/ui/test_exit_confirmation.py` **4/4 PASS**; Ruff PASS; strict mypy 0 issues for `main_window.py`; `git diff --check` PASS.
- Status of latest close fix: **SOURCE VERIFIED / USER ACCEPTED — 2026-08-31**.
- Full source verification is **COMPLETE**: **332/332 source unit+integration PASS**, **102/102
  lightweight UI PASS**, **38/38 isolated VTK UI PASS**, six real Windows source smokes exit 0,
  focused Save/Open **5/5 PASS**, Ruff PASS, strict mypy 0 issues, and diff check PASS.
- The package-only verification suite was run after the user authorized step 3: **7/7 PASS**.
  Nuitka compilation, portable assembly, and ZIP creation completed under
  `dist/post-t22-refresh-save-final/`; real package acceptance is **PASS** (2026-08-31).

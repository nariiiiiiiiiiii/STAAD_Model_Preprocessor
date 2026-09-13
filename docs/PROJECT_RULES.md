# PROJECT RULES

Canonical root: the repository clone root containing `.git` and `.worktrees/`. The active checkout
may be a nested Git worktree; all project-local support paths must remain inside this repository
root or its contained worktrees. Resolve paths from Git metadata rather than hard-coding a
machine-specific absolute path.

## Mandatory file-boundary rule

Every project-related file must stay inside the canonical root, including:
- source code,
- documentation,
- screenshots/mockups,
- test fixtures,
- golden models,
- logs,
- cache,
- temporary files,
- downloaded/staged SDK assets,
- build intermediates,
- packaged executables,
- exported test `.std` / `.dxf` / `.json` artifacts.

Project-local locations:

| Purpose | Path |
|---|---|
| Temp | `.tmp/` |
| Cache | `.cache/` |
| Logs | `.logs/` |
| Build | `build/` |
| Distribution | `dist/` |
| Generated artifacts | `artifacts/` |
| Test temp | `.tmp/tests/` |
| Vendor/SDK staging | `vendor/` |

No manual project artifact may be created in the parent `gpt_mcp_workshop` root or elsewhere.

## Engineering scope rule

V1 is a preprocessing/cleanup application. It does not perform structural analysis or design.

## Source-of-truth rule

The canonical analytical graph is the source of truth. Visual lines in the viewer are representations only.

## Change rule

All geometry repairs that affect topology or coordinates must be explicit, logged, and reviewable.

## Development-speed rule

Prefer vertical slices, targeted tests, and stable interfaces over speculative infrastructure. Do not build future patch features before the V1 cleanup workflow works end-to-end.

## DEL quarantine rule

Use the project-local `DEL/` directory as a non-destructive quarantine for files proven unused or superseded after the relevant current package checks.

- T24 MUST NOT delete files.
- Every moved file requires a manifest entry with its original path and reason.
- If a reference scan is ambiguous, keep the file in its original location.
- Do not manually move `.git`, active `.worktrees`, the current `.venv`, required `vendor` SDK files, or acceptance evidence into `DEL/`.
- Final deletion from `DEL/` is a separate user-controlled action and follows the project's delete-confirmation policy.


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

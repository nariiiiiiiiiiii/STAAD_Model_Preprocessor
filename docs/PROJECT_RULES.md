# PROJECT RULES

Canonical root:

`D:\Dizayn59\CLICodex\gpt_mcp_workshop\STAAD_Model_Preprocessor`

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

T24 uses `STAAD_Model_Preprocessor/DEL/` as a non-destructive quarantine area for files proven unused or superseded after final acceptance.

- T24 MUST NOT delete files.
- Every moved file requires a manifest entry with its original path and reason.
- If a reference scan is ambiguous, keep the file in its original location.
- Do not manually move `.git`, active `.worktrees`, the current `.venv`, required `vendor` SDK files, or acceptance evidence into `DEL/`.
- Final deletion from `DEL/` is a separate user-controlled action and follows the project's delete-confirmation policy.

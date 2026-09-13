# PolyForm Noncommercial License Migration

## Goal

Change the repository's current license to the unmodified PolyForm Noncommercial License 1.0.0, with a separate required copyright notice, and make the repository's README and Python package metadata agree.

## User-approved requirements

- The full license body must match the official PolyForm Noncommercial License 1.0.0 text.
- Add the separate line `Required Notice: Copyright (c) 2026 nariiiiiiiiii` without changing the license body.
- Keep the canonical filename `LICENSE`.
- State `License: PolyForm Noncommercial 1.0.0` in the README and include the user's noncommercial-use summary and commercial-permission warning.
- Use the SPDX identifier `PolyForm-Noncommercial-1.0.0` in package metadata.
- All repository license labels must identify only the requested PolyForm license.
- Do not change application source code or behavior.
- Do not commit or push until the user approves.

## Scope

Only licensing and documentation files may change. Build/package output and the unrelated pre-existing edit in `tests/ui/test_manual_edit_mouse.py` are out of scope.

## Compatibility caveat for owner review

The official `Noncommercial Organizations` section expressly permits use by charitable, educational, public research, public safety/health, environmental-protection, and government organizations regardless of funding source or obligations resulting from funding. This may be broader than a blanket prohibition on every paid or income-generating use. Preserve the official wording as requested and disclose this exception in the README and PR. Owner review/approval remains necessary before merging PR #1 into `main` if this conflicts with the intended blanket restriction.

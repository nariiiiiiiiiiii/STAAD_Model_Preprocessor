# Project Explorer Entity Selection Implementation Plan

**Status:** COMPLETE / SOURCE USER ACCEPTED — 2026-08-31  
**Compile status:** Deferred; no replacement standalone/ZIP authorized

> **For Codex:** Follow this plan inline, stop before compilation/package build,
> and wait for user source-test acceptance.

**Goal:** Add expandable Node/Member inventories to Project Explorer and route
individual or group clicks to exact viewport highlighting.

**Architecture:** `ProjectExplorerPanel` owns display rows and emits UUID-only
selection requests. `MainWindow` translates those requests into Select mode,
the matching selection filter, and viewport clear/highlight calls. The viewport
remains the single source of selection-change notifications, so Properties and
action availability continue to update through the existing callback.

**Tech Stack:** Python 3.11+, PySide6, pytest/pytest-qt, existing VTK viewport
adapter.

**Spec:** `docs/superpowers/specs/2026-08-31-project-explorer-entity-selection-design.md`

---

## Task 1: Lock Project Explorer list behavior

**Files:**
- Modify: `src/staadprep/ui/panels.py`
- Create: `tests/ui/test_project_explorer_selection.py`

1. Add failing tests for ordered Node/Member rows and emitted UUID tuples.
2. Add entity roles, selection request signals, and deterministic child rebuild.
3. Preserve group expansion state and avoid duplicate rows across refreshes.
4. Run the focused panel tests.

## Task 2: Wire Explorer requests to viewport selection

**Files:**
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `tests/ui/test_project_explorer_selection.py`

1. Add failing integration tests for individual and select-all requests.
2. Connect panel signals in workspace construction.
3. Activate Select mode and matching filter, clear stale cross-type selection,
   and call the viewport Node or Member highlight API.
4. Verify Properties is updated by the existing viewport callback.

## Task 3: Focused regression and documentation

**Files:**
- Modify: `docs/HANDOFF.md`
- Modify: `docs/CHECKLIST.md`
- Modify: `docs/INDEX.md` if present

1. Run the new tests plus affected selection, import-flow, and repair-refresh
   regression tests.
2. Run Ruff on changed Python files.
3. Update current T22 source-test status and document the new plan/spec.
4. Launch the development source app for user testing.
5. Stop and wait. Do not compile, package, or commit before user approval.

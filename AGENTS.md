# AGENTS.md — STAAD Model Preprocessor

These rules apply to every agent, tool, script, test, build, and generated artifact working on this project.

## 1. Immutable project boundary

The project boundary is the repository clone root that owns `.git` and `.worktrees/`. The active
checkout may be a nested Git worktree below `.worktrees/<name>/`; project-local support directories
under the clone root are still inside the boundary. Resolve locations from Git worktree metadata
rather than relying on a machine-specific absolute path.

### HARD RULE

ALL files created, modified, generated, downloaded, extracted, cached, logged, built, tested, or temporarily staged for this project MUST remain inside the repository clone root or its contained active worktrees.

Do not create project files in:
- the parent directory of the active checkout or an unrelated workspace root,
- Windows `%TEMP%` or `%TMP%`, when the tool/runtime allows an explicit project-local temp directory,
- Desktop/Documents/Downloads,
- user profile folders,
- sibling projects,
- arbitrary absolute paths outside the canonical project root.

If a third-party tool unavoidably uses OS-managed temporary storage internally, do not manually place or persist project artifacts there. Configure project-controlled temp/cache/build outputs locally whenever supported.

## 2. Project-local runtime directories

Use these paths:

- temporary files: `.tmp/`
- caches: `.cache/`
- logs: `.logs/`
- generated artifacts: `artifacts/`
- build output: `build/`
- distributables: `dist/`
- test temporary output: `.tmp/tests/`
- downloaded SDK/package staging owned by the project: `vendor/` or `.cache/downloads/`

Never use the parent workspace as a staging area.

## 3. Path handling

Application code must centralize writable paths through a project path/config service. Do not scatter absolute writable paths throughout the codebase.

Development defaults must resolve writable data to project-local directories.

Production-installed application data paths may be designed later as a separate explicit patch; V1 development remains project-local.

## 4. Scope discipline

V1 solves analytical-model cleanup before STAAD.Pro. Do not add structural analysis, design-code calculations, cloud services, database systems, BIM/IFC, or unrelated features unless explicitly approved as a later patch.

## 5. Risk-based development

Default: STANDARD verification.

FAST is allowed for cosmetic/isolated UI changes.

The following are HIGH-RISK and require explicit user approval before implementation/testing under STRICT / Full TDD:
- unit and coordinate conversion logic that affects exported geometry,
- topology/connectivity algorithms that can silently alter structural connectivity,
- automatic repair operations that change the analytical graph,
- STAAD `.STD` exporter semantics / node-member incidence output.

Do not bypass the approval gate.

## 6. No silent structural mutation

Any repair that changes model topology or coordinates must be represented as an explicit command, recorded in the repair/audit log, and be undoable where technically practical.

## 7. UI baseline

Do not redesign the approved UI during V1 unless explicitly requested. Preserve the dark engineering desktop baseline documented in `docs/UI_BASELINE.md`.

## 8. Documentation / handoff

Keep these current whenever behavior or architecture changes materially:
- `docs/PROJECT_SPEC.md`
- `docs/ARCHITECTURE.md`
- `docs/WORKFLOW.md`
- `docs/CHECKLIST.md`
- `docs/RISK_GATES.md`
- `docs/HANDOFF.md`

## 9. Destructive actions

Do not delete or move existing user files outside this project. Project cleanup must stay within the canonical project root and follow normal confirmation/safety rules.

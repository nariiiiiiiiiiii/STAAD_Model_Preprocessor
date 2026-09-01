# T22 Portable Standalone Windows Packaging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Windows x64 portable standalone release that the user can extract into any **writable** folder and run immediately without installing Python, while keeping all implicit runtime data under subfolders beside the application, bundling the SketchUp `.rbz`, and establishing version/manual-patch/update-ready contracts without creating a Setup installer or automatic updater yet.

**Architecture:** T22 keeps Nuitka `--mode=standalone` as the production baseline and assembles its verified output into a versioned portable release folder plus `.zip`. Runtime location is resolved from the compiled application's containing directory, never from the current working directory; all application-managed writable state is routed to a `Data/` hierarchy under the portable root. The SketchUp Ruby bridge is built as a version-matched `.rbz` and shipped inside the same portable package. Update readiness is achieved through strict separation of application-managed files and preserved `Data/`, a versioned package manifest with hashes/schema fields, and documented manual replacement; no network updater, installer, registry integration, or one-file packaging is part of T22.

**Tech Stack:** Python >=3.12 x64 build environment, Nuitka standalone, PySide6, PyVista/VTK, PowerShell build orchestration, Python `zipfile`/`hashlib`/`json` for release assembly and manifests, SketchUp Ruby Extension `.rbz` packaging, pytest/pytest-qt, Ruff, mypy.

**Spec:** `docs/PROJECT_SPEC.md` plus the T22 entry in `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`.

## Final execution checkpoint — 2026-08-30

**Status:** T22 is **COMPLETE** on branch `task/22-portable-packaging` / worktree `.worktrees/task-22-portable-packaging`. T21 remains complete and unchanged; T23 is **COMPLETE / PASS** by user report (2026-09-01); T24 manifest review and the approved Step 4 move are complete, with the post-move reference scan next.

**Current post-T22 checkpoint (2026-08-31):** all agreed source follow-ups are user accepted and
full source verification passes **332/332 source unit+integration** plus **140/140 UI**. The
verified `DEL/t24-quarantine-20260901/dist/post-t22-editing-final/` folder/ZIP is historical and lacks later follow-ups. The
user authorized compile step 1 and a fresh Nuitka standalone build completed; portable assembly
and ZIP creation also completed under `dist/post-t22-refresh-save-final/`. Package-only gates
passed **7/7**, and T23 acceptance was subsequently reported PASS by the user on 2026-09-01.
T24 is active: inventory, reference/evidence mapping, manifest review, the approved Step 4 move,
and the post-move reference scan are complete; affected verification is next.

Completed committed checkpoints:

- `7d0ee2b` — `feat: add portable runtime path boundary`
- `ec04b46` — `build: establish portable release version contract`
- `6afaea9` — `build: package SketchUp bridge extension`
- `22510bc` — `build: assemble update-ready portable release`
- `056d906` — `fix: support portable SketchUp inbox`
- `dcc2d6e` — `build: package Windows desktop application`

Final verified behavior:

- portable `Data/` runtime layout and compiled-root/CWD separation are implemented;
- canonical version remains `0.1.0` until T23 acceptance decides production V1 promotion;
- version-matched `.rbz` builds successfully and accepts portable `Data/Inbox/SketchUp` plus the legacy development inbox;
- portable folder/ZIP assembler, preserved `Data/`, manual update docs, manifest schema, deterministic normalized file ordering, and per-file SHA-256 contract are implemented;
- source-level packaged workflow smoke reuses production Neutral import, `ConnectNodes`, renumbering, ReadyGate, `.STD`, and `.validation.json` paths;
- final source regression: **307/307 unit+integration PASS**;
- affected UI regression: **3/3 PASS**;
- final-package gates: **6/6 PASS**;
- T22-local strict mypy: **0 issues in 4 affected source files**;
- relevant Ruff checks pass.

Final build and release evidence:

- Nuitka **4.2**, Python **3.14.3 x64**, and MSVC `cl 14.5` completed a real standalone build;
- successful report: `build/windows/final/nuitka-report.xml` with `completion="yes"`;
- executable: `build/windows/final/app.dist/STAAD Model Preprocessor.exe`;
- executable size: **159,788,032 bytes**; SHA-256: `2401E9C0689CE6ACFDA0E7E7BBE6859F6848780CD79792322CCCADAC2ADB1A57`;
- final folder: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable/`;
- final ZIP: `dist/STAAD_Model_Preprocessor_0.1.0_win64_portable.zip`, **225,136,191 bytes**, SHA-256 `D31A70005D7F0B2C09B467D6A5591892868E9E56AC35874434BA38CFC4687115`;
- real Qt/VTK, sanitized-PATH/no-Python, different-CWD, relocation with spaces/Unicode, existing-`Data`, packaged workflow, freshly extracted ZIP launch, and 811/811 manifest hash gates passed;
- no Setup/MSI/NSIS/automatic-updater/one-file production artifact exists.

**Next action:** obtain real user acceptance of the new isolated standalone/ZIP. Package-only
verification is **7/7 PASS**. Start T23 only after explicit user instruction and package acceptance.

### USER ACTION REQUIRED

**Next user action: test and accept the new package.** Nuitka compile step 1, isolated
portable-folder/ZIP assembly, and package-only verification (**7/7 PASS**) are complete under
`dist/post-t22-refresh-save-final/`; the editing-final standalone folder/ZIP is a historical
checkpoint and not the current acceptance target. Do not download or install additional
Python/toolchain/runtime packages preemptively. If a later build error proves a missing external
prerequisite, record the exact prerequisite/version/source/reason here and ask the user to perform
the manual download/install only when that is simpler or safer than automated handling.

## User-approved packaging contract — 2026-08-29

The following requirements are binding for T22:

1. Distribution is **Portable Standalone**, not an installer.
2. The user receives a `.zip`, extracts it to any **writable** Windows folder/drive, and launches `STAAD Model Preprocessor.exe` directly.
3. The target machine must not require Python, pip, PySide6, VTK, or project source installation.
4. Application-managed config/projects/inbox/exports/reports/logs/cache/temp/backups stay in clearly named subfolders under the portable package.
5. No hard-coded `C:\...`, user profile, repository path, or launch CWD may be required at runtime.
6. The same release includes a ready-to-install SketchUp `.rbz` under `SketchUp_Extension/`.
7. Version metadata is established now and the `.exe`, portable folder/archive, package manifest, and `.rbz` must agree on the same application version.
8. Manual patching is supported without destroying `Data/`.
9. A machine-readable update/package manifest and per-file SHA-256 hashes are generated now so a future updater can use the same contract.
10. **Not in T22:** Setup.exe/MSI/NSIS, automatic download/install updater, server/channel infrastructure, Start Menu/registry integration, admin-required installation, and Nuitka one-file mode.
11. T22 remains **STANDARD risk**. It must not change structural/model/ReadyGate mathematics or validation semantics.
12. T23 remains responsible for real-project + target STAAD.Pro production acceptance; T22 packages and proves the desktop runtime only.

## Final checkpoint — 2026-08-30

T22 is **COMPLETE** on `task/22-portable-packaging` in `.worktrees/task-22-portable-packaging`.

Completed and evidenced in the active worktree:

- portable runtime path policy and `Data/` hierarchy;
- version contract `0.1.0`;
- deterministic SketchUp `.rbz` builder and portable inbox support;
- portable assembler, manual-update contract, ZIP/manifest/hash logic;
- source-level packaged T21 workflow smoke;
- **307/307** unit+integration regression pass;
- **3/3** affected UI regression pass and **6/6** final-package gates pass;
- T22-local strict mypy **0 issues** and relevant Ruff checks passed;
- real Nuitka standalone `.exe` emitted with successful completion report.

The real `.exe` Qt/VTK launch, no-Python launch, different-CWD launch, relocation to spaces/Unicode paths, runtime-write containment under `Data/`, final portable ZIP assembly, manifest hashes, and packaged T21 READY/STD/report workflow are all evidenced.

The synchronized documentation entry point is [`docs/INDEX.md`](../../INDEX.md). T23 acceptance is
recorded as user-reported PASS on 2026-09-01; T24 inventory and reference/evidence mapping are
complete, with pre-move manifest review next.

## Important portability boundary

“Extract anywhere and run” means **any writable location** supported by Windows. A protected/read-only directory cannot satisfy the requirement to save `Data/` beside the executable. The app must detect an unwritable portable root at startup and show a clear error; it must **not silently fall back** to `%TEMP%`, `%APPDATA%`, registry state, or another hidden location.

Official Nuitka guidance for standalone deployment is relevant to this design: files beside a standalone executable must not be located via `os.getcwd()`; use the compiled containing directory / executable location instead. T22 must therefore explicitly prove launch from a different CWD and relocation of the whole portable folder.

## Target release layout

T22 must produce both the extracted directory and a ZIP archive under project-local `dist/`:

```text
dist/
├─ STAAD_Model_Preprocessor_<VERSION>_win64_portable/
│  ├─ STAAD Model Preprocessor.exe
│  ├─ <Nuitka standalone DLL/runtime/plugin files and folders>
│  │
│  ├─ Data/
│  │  ├─ Config/
│  │  ├─ Projects/
│  │  ├─ Inbox/
│  │  │  └─ SketchUp/
│  │  ├─ Exports/
│  │  ├─ Reports/
│  │  ├─ Logs/
│  │  ├─ Cache/
│  │  ├─ Temp/
│  │  └─ Backups/
│  │
│  ├─ SketchUp_Extension/
│  │  ├─ STAAD_Prep_Bridge_<VERSION>.rbz
│  │  └─ INSTALL_RBZ.md
│  │
│  ├─ Update/
│  │  ├─ package-manifest.json
│  │  └─ UPDATE_MANUAL.md
│  │
│  └─ README_PORTABLE.md
│
└─ STAAD_Model_Preprocessor_<VERSION>_win64_portable.zip
```

Rules for this layout:

- Nuitka-generated dependency structure is preserved unless a build-proven packaging option safely relocates it; never manually shuffle DLLs simply for aesthetics.
- `Data/` is user-preserved state and is never listed as an application-managed replacement root.
- Runtime-created files must default below `Data/`.
- Explicit user-selected export destinations may be outside the portable root only when the user deliberately chooses that path through Save/Export UI; implicit runtime writes may not escape `Data/`.
- `SketchUp_Extension/` is distribution content, not the installed SketchUp Plugins directory.
- Installing `.rbz` into SketchUp is a one-time user product action; the portable app itself remains install-free.

## File map

### Create

- `src/staadprep/version.py` — canonical application version constant/API used by runtime and build tooling.
- `src/staadprep/portable_paths.py` — portable-root detection, writable `Data/` layout, environment routing, and path assertions.
- `scripts/build_windows.ps1` — clean, non-interactive Windows standalone build orchestrator.
- `scripts/build_sketchup_rbz.py` — creates a valid `.rbz` from `extensions/sketchup_staadprep/` and synchronizes package version evidence.
- `scripts/assemble_portable.py` — assembles the release directory, creates manifest/hashes, and creates the portable ZIP.
- `packaging/README_PORTABLE.md` — source template copied into release root.
- `packaging/INSTALL_RBZ.md` — source template copied under `SketchUp_Extension/`.
- `packaging/UPDATE_MANUAL.md` — source template describing safe manual upgrades that preserve `Data/`.
- `tests/unit/test_portable_paths.py` — portable root/path contract tests.
- `tests/unit/test_version_contract.py` — Python/package/Ruby version consistency tests.
- `tests/integration/test_rbz_package.py` — validates RBZ archive structure and version metadata.
- `tests/integration/test_package_manifest.py` — validates manifest schema, hashes, managed/preserved boundaries.
- `tests/integration/test_packaged_paths.py` — launches/relocates the packaged app and verifies writable paths.

### Modify

- `pyproject.toml` — canonical package version plumbing and T22 build/test metadata only; no installer config.
- `src/staadprep/app.py` — resolve/apply portable paths before constructing `MainWindow` when compiled.
- `src/staadprep/paths.py` — separate runtime-writable directories from development-only build/dist/vendor concerns without breaking development mode.
- `src/staadprep/ui/main_window.py` — accept/inject the resolved project/runtime path object rather than deriving production paths from CWD.
- `src/staadprep/importers/neutral_reader.py` — use the injected SketchUp inbox path contract.
- `src/staadprep/importers/skp_bridge.py` — preserve fail-soft optional native bridge behavior under portable paths.
- `extensions/sketchup_staadprep/staadprep_loader.rb` — synchronize extension version with the canonical application version for release builds.
- `README.md` — portable launch/install/update instructions and build command.
- `docs/HANDOFF.md`, `docs/CHECKLIST.md`, `docs/TASK_BOARD.md` — T22 completion evidence only after all gates pass.

---

### Task 1: Lock the portable path contract before packaging

**Files:**
- Create: `src/staadprep/portable_paths.py`
- Create: `tests/unit/test_portable_paths.py`
- Modify: `src/staadprep/paths.py`
- Modify: `src/staadprep/app.py`
- Modify: `src/staadprep/ui/main_window.py`
- Modify: `src/staadprep/importers/neutral_reader.py`

**Interfaces:**
- Produces: `PortablePaths.from_root(root: Path) -> PortablePaths`
- Produces: `PortablePaths.detect() -> PortablePaths`
- Produces: `PortablePaths.ensure_layout() -> None`
- Produces: `PortablePaths.apply_environment() -> None`
- Produces: `PortablePaths.assert_writable() -> None`
- Consumes: existing `ProjectPaths`/`MainWindow`/`NeutralReader` behavior without changing model semantics.

- [x] **Step 1: Write failing unit tests for exact portable directories**

```python
from pathlib import Path

from staadprep.portable_paths import PortablePaths


def test_portable_layout_is_relative_to_release_root(tmp_path: Path) -> None:
    root = tmp_path / "Portable App ไทย"
    paths = PortablePaths.from_root(root)

    assert paths.root == root.resolve()
    assert paths.data == root.resolve() / "Data"
    assert paths.config == paths.data / "Config"
    assert paths.projects == paths.data / "Projects"
    assert paths.sketchup_inbox == paths.data / "Inbox" / "SketchUp"
    assert paths.exports == paths.data / "Exports"
    assert paths.reports == paths.data / "Reports"
    assert paths.logs == paths.data / "Logs"
    assert paths.cache == paths.data / "Cache"
    assert paths.temp == paths.data / "Temp"
    assert paths.backups == paths.data / "Backups"
```

Add a second test proving every writable path is inside `root`, and a third proving a path traversal/escape is rejected.

- [x] **Step 2: Run the new tests and confirm RED**

Run:

```powershell
python -m pytest -q tests/unit/test_portable_paths.py
```

Expected: FAIL because `staadprep.portable_paths` does not exist.

- [x] **Step 3: Implement the minimum immutable path object**

The implementation must derive paths only from an explicit root and must not touch the filesystem in `from_root`.

```python
@dataclass(frozen=True, slots=True)
class PortablePaths:
    root: Path
    data: Path
    config: Path
    projects: Path
    sketchup_inbox: Path
    exports: Path
    reports: Path
    logs: Path
    cache: Path
    temp: Path
    backups: Path

    @classmethod
    def from_root(cls, root: Path) -> "PortablePaths": ...
```

- [x] **Step 4: Add compiled-root detection that never depends on CWD**

Production detection must use Nuitka's containing-directory mechanism when available. Uncompiled development keeps the explicit `STAADPREP_PROJECT_ROOT`/development behavior.

Conceptual implementation:

```python
def _compiled_containing_dir() -> Path | None:
    try:
        return Path(__compiled__.containing_dir).resolve()  # type: ignore[name-defined]
    except NameError:
        return None


def detect_portable_root() -> Path | None:
    return _compiled_containing_dir()
```

Do **not** use `Path.cwd()` as the packaged application's portable root.

- [x] **Step 5: Add writeability and environment routing tests**

Tests must verify `apply_environment()` routes at least `TEMP`, `TMP`, `PYTHONPYCACHEPREFIX`, `STAADPREP_CACHE_DIR`, `STAADPREP_LOG_DIR`, and the app's project/runtime root under `Data/`.

No production fallback to system temp/AppData is allowed.

- [x] **Step 6: Inject production paths before the UI is constructed**

`app.main()` must resolve portable paths before `MainWindow()` in compiled mode. Development/test injection remains possible and existing tests must not require a compiled executable.

`MainWindow` must consume injected paths/root rather than independently deriving packaged paths from CWD.

- [x] **Step 7: Keep development paths backward-compatible**

`ProjectPaths.from_root(project_root)` remains the canonical development/test behavior. Refactor `ensure_layout()` only as needed to avoid production creation of development-only `build/dist/vendor` directories.

- [x] **Step 8: Run focused regression**

Run:

```powershell
python -m pytest -q tests/unit/test_portable_paths.py tests/unit tests/integration
python -m ruff check src/staadprep/portable_paths.py src/staadprep/paths.py src/staadprep/app.py src/staadprep/ui/main_window.py tests/unit/test_portable_paths.py
```

Expected: PASS.

- [x] **Step 9: Commit the path boundary**

```bash
git add src/staadprep/portable_paths.py src/staadprep/paths.py src/staadprep/app.py src/staadprep/ui/main_window.py src/staadprep/importers/neutral_reader.py tests/unit/test_portable_paths.py
git commit -m "feat: add portable runtime path policy"
```

---

### Task 2: Establish one release version contract

**Files:**
- Create: `src/staadprep/version.py`
- Create: `tests/unit/test_version_contract.py`
- Modify: `pyproject.toml`
- Modify: `extensions/sketchup_staadprep/staadprep_loader.rb`

**Interfaces:**
- Produces: `staadprep.version.__version__: str`
- Build scripts consume the same version for executable metadata, folder/archive names, RBZ name, and manifest.

- [x] **Step 1: Write failing version consistency tests**

The test must verify:

```text
Python canonical version
= project/package version
= SketchUp extension version
```

It must reject blank versions and versions containing path separators.

- [x] **Step 2: Confirm RED**

Run:

```powershell
python -m pytest -q tests/unit/test_version_contract.py
```

Expected: FAIL because no canonical runtime version module exists.

- [x] **Step 3: Add canonical version module and package plumbing**

Keep the canonical value in a tiny dependency-free module:

```python
__version__ = "0.1.0"
```

Configure `pyproject.toml` so project metadata obtains the version from that module rather than maintaining an unrelated duplicate literal.

T22 must **not** automatically declare production `1.0.0` acceptance; T23 remains the gate that can promote the accepted V1 release version.

- [x] **Step 4: Make the Ruby extension contract testable against that version**

The Ruby loader's `EXTENSION.version` must match the canonical app version used for the package being assembled. Build tooling may substitute the value in a staged copy, but it must never silently emit a mismatched RBZ.

- [x] **Step 5: Run tests/lint**

```powershell
python -m pytest -q tests/unit/test_version_contract.py tests/unit/test_sketchup_ruby_contract.py
python -m ruff check src/staadprep/version.py tests/unit/test_version_contract.py
```

- [x] **Step 6: Commit**

```bash
git add src/staadprep/version.py pyproject.toml extensions/sketchup_staadprep/staadprep_loader.rb tests/unit/test_version_contract.py
git commit -m "build: establish portable release version contract"
```

---

### Task 3: Build and validate the SketchUp `.rbz`

**Files:**
- Create: `scripts/build_sketchup_rbz.py`
- Create: `tests/integration/test_rbz_package.py`
- Create: `packaging/INSTALL_RBZ.md`
- Read/package: `extensions/sketchup_staadprep/staadprep_loader.rb`
- Read/package: `extensions/sketchup_staadprep/staadprep/exporter.rb`

**Interfaces:**
- Produces: `build/sketchup/STAAD_Prep_Bridge_<VERSION>.rbz`
- The RBZ archive root contains `staadprep_loader.rb` and `staadprep/exporter.rb` with no extra parent directory.

- [x] **Step 1: Write failing RBZ archive test**

Use `zipfile.ZipFile` to assert exact required entries and inspect `staadprep_loader.rb` inside the archive for the expected version.

- [x] **Step 2: Confirm RED**

```powershell
python -m pytest -q tests/integration/test_rbz_package.py
```

Expected: FAIL because the RBZ builder does not exist.

- [x] **Step 3: Implement deterministic project-local RBZ build**

`scripts/build_sketchup_rbz.py` must:

1. read the canonical application version;
2. stage files only under project-local `build/sketchup/stage/`;
3. ensure staged loader version matches the canonical version;
4. write `.rbz` under `build/sketchup/`;
5. never write into SketchUp's real Plugins directory;
6. return non-zero on missing/mismatched required files.

- [x] **Step 4: Run RBZ test and existing Ruby contract test**

```powershell
python scripts/build_sketchup_rbz.py
python -m pytest -q tests/integration/test_rbz_package.py tests/unit/test_sketchup_ruby_contract.py
```

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add scripts/build_sketchup_rbz.py tests/integration/test_rbz_package.py packaging/INSTALL_RBZ.md
git commit -m "build: package SketchUp bridge extension"
```

---

### Task 4: Build the Windows standalone executable with Nuitka

**Files:**
- Create: `scripts/build_windows.ps1`
- Modify: `pyproject.toml` only if a build dependency/setting is required and proven.

**Interfaces:**
- Produces an unassembled Nuitka standalone directory under `build/windows/`.
- Final distribution is assembled later; the build script must not create Setup/MSI/NSIS output.

- [x] **Step 1: Make the script fail fast on the wrong environment**

The script validates:

- Windows x64 host;
- selected Python is x64 and satisfies project version requirements;
- `python -m nuitka --version` succeeds;
- source tree/project root is resolved from the script location;
- all `TEMP/TMP` and build outputs are redirected under project-local `.tmp/`, `.cache/`, and `build/`.

- [x] **Step 2: Build standalone, not accelerated/onefile**

The command must be equivalent to:

```powershell
python -m nuitka `
  --mode=standalone `
  --enable-plugin=pyside6 `
  --windows-console-mode=disable `
  --output-dir=<project-root>\build\windows `
  --output-filename="STAAD Model Preprocessor.exe" `
  --include-package=pyvista `
  --include-package=pyvistaqt `
  --include-package=vtkmodules `
  --include-package-data=pyvista `
  src\staadprep\app.py
```

The build script must source product/file version flags from the canonical version contract.

Do not manually copy missing DLLs after the build. Missing Qt/VTK/native dependencies must be solved through supported Nuitka/package configuration and then regression-tested.

- [x] **Step 3: Prove the standalone executable launches**

Use existing smoke support (`STAADPREP_SMOKE_MS`) or an equivalent explicit packaged smoke hook so the executable opens Qt/VTK and exits itself without user interaction.

- [x] **Step 4: Prove no Python runtime installation is required by the app**

Launch the built `.exe` with a sanitized child `PATH` that does not expose the development Python/venv. The smoke must still exit successfully.

This test does not claim that every Windows installation is identical; final acceptance must also use a clean/representative Windows environment. If compiler runtime libraries are absent on the target, T22 must resolve that using app-local/standalone-compatible distribution or a different proven build toolchain — never by requiring the user to install Python or the development environment.

- [x] **Step 5: Prove PySide6/VTK packaged behavior**

Launch real viewport smoke against the executable. A package that starts but cannot create the real Qt/VTK viewport is a failed build.

- [x] **Step 6: Commit**

```bash
git add scripts/build_windows.ps1 pyproject.toml
git commit -m "build: compile Windows standalone application"
```

---

### Task 5: Assemble the portable release folder, update manifest, and ZIP

**Files:**
- Create: `scripts/assemble_portable.py`
- Create: `packaging/README_PORTABLE.md`
- Create: `packaging/UPDATE_MANUAL.md`
- Create: `tests/integration/test_package_manifest.py`

**Interfaces:**
- Consumes: Nuitka standalone directory + built RBZ + canonical version.
- Produces: `dist/STAAD_Model_Preprocessor_<VERSION>_win64_portable/`
- Produces: `dist/STAAD_Model_Preprocessor_<VERSION>_win64_portable.zip`
- Produces: `Update/package-manifest.json` inside the portable folder.

- [x] **Step 1: Write failing manifest contract test**

The generated manifest must contain at least:

```json
{
  "manifest_schema": 1,
  "product": "STAAD Model Preprocessor",
  "version": "<VERSION>",
  "platform": "windows-x64",
  "package_type": "portable-standalone",
  "entrypoint": "STAAD Model Preprocessor.exe",
  "data_schema": 1,
  "preserve_roots": ["Data/"],
  "sketchup_extension": "SketchUp_Extension/STAAD_Prep_Bridge_<VERSION>.rbz",
  "files": []
}
```

Every application-managed file entry must contain normalized relative `path`, byte `size`, and lowercase SHA-256 `sha256`.

`Data/` must not appear as a replace-managed application root.

- [x] **Step 2: Confirm RED**

```powershell
python -m pytest -q tests/integration/test_package_manifest.py
```

- [x] **Step 3: Implement release assembly**

`assemble_portable.py` must:

1. create only under project-local `dist/`;
2. copy the verified Nuitka standalone tree without reorganizing native dependencies;
3. create the required `Data/` hierarchy;
4. copy the version-matched RBZ and install instructions;
5. copy portable/readme/manual-update docs;
6. hash application-managed release files;
7. write `Update/package-manifest.json` atomically;
8. create the portable ZIP;
9. fail if package version, RBZ version, manifest version, or executable metadata input disagree.

- [x] **Step 4: Define manual update semantics now**

`UPDATE_MANUAL.md` must document the safe V1 procedure:

1. close the old app;
2. extract the new portable release into a **new folder**;
3. copy the old release's `Data/` directory into the new release;
4. launch the new `.exe`;
5. verify version and open/import/export as normal;
6. keep the old release as rollback until satisfied.

The future automatic updater must follow the same `preserve_roots`/manifest contract. T22 does not download or install updates itself.

- [x] **Step 5: Validate hashes and archive contents**

```powershell
python scripts/assemble_portable.py
python -m pytest -q tests/integration/test_package_manifest.py tests/integration/test_rbz_package.py
```

Expected: PASS, and every manifest hash recomputes exactly.

- [x] **Step 6: Commit**

```bash
git add scripts/assemble_portable.py packaging/README_PORTABLE.md packaging/UPDATE_MANUAL.md tests/integration/test_package_manifest.py
git commit -m "build: assemble update-ready portable release"
```

---

### Task 6: Prove relocation and all runtime writes stay portable

**Files:**
- Create: `tests/integration/test_packaged_paths.py`
- Modify affected runtime code only if these tests expose a real escape/CWD dependency.

**Interfaces:**
- Consumes assembled portable release.
- Proves the product behaves as portable software rather than a repository-bound Python app.

- [x] **Step 1: Add a packaged-path smoke under a path with spaces and Unicode**

Test/staging location must remain project-local, for example:

```text
.tmp/tests/t22/Portable App ไทย A/
```

Run the `.exe` while the child process CWD is a different directory. Verify startup succeeds and runtime state is written under that release's `Data/`.

- [x] **Step 2: Add a relocation test**

Copy the exact assembled release to a second project-local location:

```text
.tmp/tests/t22/Relocated Portable ไทย B/
```

Launch without rebuilding/reconfiguring. Verify the new release root is used and no path points back to location A.

- [x] **Step 3: Assert runtime containment**

After smoke activity, enumerate new runtime-created files. Every implicit write must resolve below the relocated release's `Data/` hierarchy.

Reject any implicit write to:

- repository root outside the staged release;
- `%TEMP%`/`%TMP%` chosen by the app;
- `%APPDATA%`;
- `%LOCALAPPDATA%`;
- user home;
- old package path;
- hard-coded `D:\Dizayn59\...`.

- [x] **Step 4: Prove unwritable-root behavior**

Use an injectable/path-level unit boundary rather than changing real system ACLs where practical. `PortablePaths.assert_writable()` must raise a specific error that the app converts into a clear startup message. No hidden fallback is permitted.

- [x] **Step 5: Run packaged path integration**

```powershell
python -m pytest -q tests/integration/test_packaged_paths.py
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add tests/integration/test_packaged_paths.py src/staadprep/portable_paths.py src/staadprep/app.py src/staadprep/ui/main_window.py src/staadprep/importers/neutral_reader.py
git commit -m "test: verify relocatable portable runtime"
```

---

### Task 7: Packaged end-to-end application smoke

**Files:**
- Reuse: `tests/golden_models/`
- Reuse/extend: `tests/integration/test_packaged_paths.py`
- Modify: `README.md`

**Interfaces:**
- Proves the compiled app can execute the already-approved T21 workflow without structural logic changes.

- [x] **Step 1: Launch packaged executable with real Qt/VTK UI**

Use a non-interactive smoke hook only for automation. The normal executable remains a GUI app.

- [x] **Step 2: Exercise one representative golden import**

Import a known golden DXF/Neutral model through production code from a project-local staged path.

- [x] **Step 3: Perform one existing manual edit command**

Use an already-tested T18/T19 command path; do not invent a packaging-only mutation path.

- [x] **Step 4: Validate and export**

The model must reach the same T21 `ReadyGate`, export `.STD`, and emit `.validation.json`. Default smoke outputs go under portable `Data/Exports` and `Data/Reports` (or the explicitly defined production equivalents).

- [x] **Step 5: Close and reopen the packaged app**

Verify the package remains launchable after generated Data exists and that the SketchUp inbox remains under `Data/Inbox/SketchUp`.

- [x] **Step 6: Document actual user workflow**

`README.md` and `packaging/README_PORTABLE.md` must state clearly:

```text
1. Download/copy STAAD_Model_Preprocessor_<VERSION>_win64_portable.zip
2. Extract to any writable folder
3. Open STAAD Model Preprocessor.exe
4. No Python installation required
5. Optional SketchUp integration: install SketchUp_Extension/STAAD_Prep_Bridge_<VERSION>.rbz once
6. Keep the whole portable folder together when moving it
7. Data is stored under Data/
8. For manual updates, preserve/copy Data/ into the new release
```

- [x] **Step 7: Run regression gates appropriate to T22**

Run fresh:

```powershell
python -m pytest -q tests/unit tests/integration
python scripts/test_ui_isolated.py --scope lightweight --run-id t22-final
```

Run renderer-heavy UI through the established single-file MCP-safe strategy when execution is through MCP; aggregate with the runner's `--summary-only` evidence.

Also run Ruff, T22-local mypy, and `git diff --check`.

- [x] **Step 8: Commit documentation/runtime smoke changes**

```bash
git add README.md packaging/README_PORTABLE.md tests/integration/test_packaged_paths.py
git commit -m "test: verify packaged Windows workflow"
```

---

### Task 8: Final T22 release gate and checkpoint

**Files:**
- Modify: `docs/HANDOFF.md`
- Modify: `docs/CHECKLIST.md`
- Modify: `docs/TASK_BOARD.md`
- Modify: `docs/superpowers/plans/2026-08-28-staad-model-preprocessor-v1.md`

**Interfaces:**
- Produces the exact T22 evidence T23 will consume.
- Does not start T23.

- [x] **Step 1: Verify package artifacts exist**

Required:

```text
dist/STAAD_Model_Preprocessor_<VERSION>_win64_portable/
dist/STAAD_Model_Preprocessor_<VERSION>_win64_portable.zip
.../STAAD Model Preprocessor.exe
.../SketchUp_Extension/STAAD_Prep_Bridge_<VERSION>.rbz
.../Update/package-manifest.json
.../README_PORTABLE.md
.../Update/UPDATE_MANUAL.md
```

- [x] **Step 2: Verify release manifest/hashes**

Recompute SHA-256 from the final release tree. Any mismatch fails T22.

- [x] **Step 3: Verify portable relocation one final time on final artifacts**

The exact final package, not a pre-final build, must launch from a second writable path and different CWD.

- [x] **Step 4: Verify no forbidden installer/updater artifacts were introduced**

There must be no T22-produced `Setup.exe`, `.msi`, NSIS output, automatic update downloader/service, registry installation action, or one-file build replacing the standalone baseline.

- [x] **Step 5: Record limitations truthfully**

Documentation must state:

- portable release requires a writable directory for local `Data/`;
- SketchUp `.rbz` installation is a separate one-time action when SketchUp integration is desired;
- T22 provides manual patch/update readiness, not an automatic updater;
- T23 real-project + target STAAD.Pro acceptance is still required before declaring production V1 accepted.

- [x] **Step 6: Commit T22**

Final required task commit subject from the main plan remains:

```text
build: package Windows desktop application
```

If intermediate commits were used, finish with a docs/checkpoint commit after the implementation commit rather than rewriting tested history.

- [x] **Step 7: Stop**

Set T22 to COMPLETE, T23 to READY/not started, and stop for user review. Do not start T23 automatically.

---

## Future update/patch interface intentionally reserved by T22

T22 does **not** implement the updater, but it must avoid architecture that blocks one later.

A future updater may safely add:

```text
Check manifest URL
→ compare semantic version
→ download new portable package/patch
→ verify SHA-256 and later signature
→ close app
→ replace only manifest-managed application files
→ preserve Data/
→ reopen
→ rollback on failure
```

The following T22 contracts must therefore remain stable:

- canonical app version API;
- `Data/` as preserved user state root;
- `manifest_schema` and `data_schema` fields;
- normalized relative file paths;
- per-file SHA-256;
- application-managed vs preserved roots;
- version-matched `.rbz` evidence;
- no runtime dependency on installation path/CWD.

A future signed-update design may add signature/public-key fields to a newer manifest schema. T22 does not need signing keys, remote endpoints, credentials, or an update server.

## Explicitly deferred

The following are **not** part of T22 and must not be added opportunistically:

- Setup.exe / MSI / NSIS installer;
- Windows service/background updater;
- automatic network update check;
- update server/cloud storage/channel backend;
- registry-based install state;
- Start Menu/Desktop shortcut installer;
- admin/UAC installation workflow;
- Nuitka `--mode=onefile` as the production package;
- Microsoft Store/MSIX packaging;
- macOS packaging;
- code-signing certificate procurement;
- changes to structural validation/repair/numbering/direction algorithms.

## T22 definition of done

T22 is complete only when all of the following are evidenced on the final tree:

- [x] Portable standalone folder builds successfully.
- [x] Portable ZIP builds successfully.
- [x] Final `.exe` launches with real PySide6/VTK without Python on PATH.
- [x] Final package launches when CWD differs from package root.
- [x] Final package launches after being copied/relocated to another writable path containing spaces/Unicode.
- [x] All implicit runtime writes remain below portable `Data/`.
- [x] Unwritable-root behavior is explicit and has no hidden fallback.
- [x] SketchUp `.rbz` is included and archive contract passes.
- [x] App/RBZ/package/manifest versions agree.
- [x] Package manifest hashes verify exactly.
- [x] Manual update procedure preserves `Data/`.
- [x] No Setup/MSI/NSIS/automatic updater/onefile production artifact is created.
- [x] Existing T21 READY/STD workflow passes from the packaged app.
- [x] Relevant unit/integration/UI regression is green.
- [x] Ruff passes.
- [x] T22-local strict mypy passes for affected typed Python files.
- [x] `git diff --check` passes.
- [x] README/HANDOFF/CHECKLIST/TASK_BOARD reflect exact tested package behavior.
- [x] T23 remains not started until explicit user continuation.

## Reference notes

- Nuitka standalone mode is the intended copy-to-another-machine distribution mode; one-file is intentionally deferred until standalone behavior is proven.
- Runtime resources beside a Nuitka executable must not be located from CWD; the compiled containing directory/executable directory is the appropriate anchor.
- Build-only Python/Nuitka requirements are not target-machine installation requirements.
- The SketchUp `.rbz` remains a normal SketchUp Extension Manager installation artifact even though the Windows app itself is portable/no-install.

Official implementation references:

- Nuitka standalone distribution/use cases: https://nuitka.net/user-documentation/use-cases.html
- Nuitka standalone file-location guidance / `__compiled__.containing_dir`: https://nuitka.net/user-documentation/common-issue-solutions.html
- Nuitka Windows version metadata (`--product-version`, `--file-version`): https://nuitka.net/user-documentation/user-manual.html

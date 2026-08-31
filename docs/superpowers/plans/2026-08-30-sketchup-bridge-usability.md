# SketchUp Bridge Usability Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the SketchUp RBZ a clear bridge interface and replace long random JSON names with compact collision-safe ASCII names.

**Architecture:** Keep geometry traversal and Neutral JSON v1 unchanged. Add one cached `UI::HtmlDialog` around the existing exporter, separate inbox selection from export, and isolate compact filename selection in one Ruby method while preserving atomic writes.

**Tech Stack:** SketchUp Ruby API, `UI::HtmlDialog`, Ruby JSON/FileUtils, Python pytest source-contract checks, deterministic `.rbz` builder.

**Spec:** `docs/superpowers/specs/2026-08-30-post-t22-usability-design.md`

**Status:** COMPLETE, USER ACCEPTED, and committed as `e7ce6ad`. The accepted RBZ is included in the current editing-final portable package.

## Global Constraints

- Do not change geometry traversal, coordinates, source unit `in`, source axis `Z-UP`, protocol version `1`, or Neutral JSON fields.
- Accept only `Data/Inbox/SketchUp` and the legacy project-local bridge inbox.
- Preserve atomic write, flush, fsync, rename, and cleanup.
- This plan covers user requirements 1 and 2 only.

## Inline execution checkpoint — 2026-08-30

- [x] Contract tests added and observed RED against the previous exporter.
- [x] `UI::HtmlDialog` bridge interface implemented with purpose/inbox/result text and three actions.
- [x] Compact `SP_YYYYMMDD_HHMMSS.json` naming with `_02` collision suffix implemented.
- [x] Version-matched RBZ rebuilt under `build/sketchup/`.
- [x] User installed and accepted the rebuilt RBZ in real SketchUp; the bridge window opened and was usable.
- [x] Feature checkpoint committed as `e7ce6ad` (`feat: add SketchUp bridge interface`).

---

### Task 1: Lock the dialog and compact-name contracts

**Files:**
- Modify: `tests/unit/test_sketchup_ruby_contract.py`
- Modify: `tests/integration/test_rbz_package.py`

**Interfaces:**
- Consumes: `extensions/sketchup_staadprep/staadprep/exporter.rb`
- Produces: executable assertions for dialog callbacks and compact filenames

- [x] **Step 1: Add source-contract assertions**

```python
assert "UI::HtmlDialog.new" in exporter
assert "Export Geometry" in exporter
assert "Choose Inbox" in exporter
assert "STAAD Prep Bridge" in exporter
assert "SP_#{now.strftime('%Y%m%d_%H%M%S')}" in exporter
assert "SecureRandom" not in exporter
assert "File.exist?(candidate)" in exporter
```

- [x] **Step 2: Assert the generated RBZ contains the same source**

```python
with ZipFile(rbz_path) as archive:
    bundled = archive.read("staadprep/exporter.rb").decode("utf-8")
assert "UI::HtmlDialog.new" in bundled
assert "Export Geometry" in bundled
assert "SP_#{now.strftime('%Y%m%d_%H%M%S')}" in bundled
```

- [x] **Step 3: Run focused tests and confirm RED**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_sketchup_ruby_contract.py tests/integration/test_rbz_package.py -q
```

Expected: failures because the current exporter has no HtmlDialog and still uses `SecureRandom.hex(6)`.

### Task 2: Implement the SketchUp bridge dialog

**Files:**
- Modify: `extensions/sketchup_staadprep/staadprep/exporter.rb`

**Interfaces:**
- Consumes: `configured_inbox`, `build_payload`, `write_atomic`
- Produces: `show_bridge_dialog`, `bridge_dialog`, `bridge_html`, `choose_inbox`, `update_dialog_status(message)`

- [x] **Step 1: Remove the random-token dependency and separate inbox choice**

Remove `require 'securerandom'`. Add:

```ruby
def choose_inbox
  selected = UI.select_directory(title: 'Select STAAD Prep inbox')
  return nil unless selected
  expanded = File.expand_path(selected)
  unless valid_inbox_path?(expanded)
    UI.messagebox('Select either Data/Inbox/SketchUp or artifacts/sketchup_bridge/inbox.')
    return nil
  end
  Sketchup.write_default(PREF_SECTION, PREF_INBOX_KEY, expanded)
  expanded
end
```

- [x] **Step 2: Add one cached HtmlDialog**

```ruby
def bridge_dialog
  @bridge_dialog ||= UI::HtmlDialog.new(
    dialog_title: 'STAAD Prep Bridge',
    preferences_key: 'StaadPrepBridgeDialog',
    scrollable: false,
    resizable: true,
    width: 520,
    height: 430,
    style: UI::HtmlDialog::STYLE_DIALOG
  )
end
```

The HTML must explain the geometry handoff, display current inbox and last result, and include buttons **Export Geometry**, **Choose Inbox…**, and **Close**.

- [x] **Step 3: Bind exact callbacks**

```ruby
dialog.add_action_callback('export_geometry') do |_context|
  output = send_to_staad_prep
  update_dialog_status(output ? "Exported: #{File.basename(output)}" : 'Export cancelled.')
end
dialog.add_action_callback('choose_inbox') do |_context|
  selected = choose_inbox
  update_dialog_status(selected ? "Inbox: #{selected}" : 'Inbox unchanged.')
end
dialog.add_action_callback('close_dialog') { |_context| dialog.close }
```

Make `send_to_staad_prep` return the final path on success and `nil` on cancellation/failure while retaining concise SketchUp success/error messages.

- [x] **Step 4: Route menu and toolbar to the dialog**

```ruby
command = UI::Command.new('STAAD Prep Bridge') { show_bridge_dialog }
command.menu_text = 'STAAD Prep Bridge…'
command.tooltip = 'Export structural edge geometry to STAAD Model Preprocessor'
```

### Task 3: Implement compact collision-safe filenames

**Files:**
- Modify: `extensions/sketchup_staadprep/staadprep/exporter.rb`

**Interfaces:**
- Produces: `next_output_path(inbox, now = Time.now) -> String`

- [x] **Step 1: Add the compact path generator**

```ruby
def next_output_path(inbox, now = Time.now)
  base = "SP_#{now.strftime('%Y%m%d_%H%M%S')}"
  candidate = File.join(inbox, "#{base}.json")
  index = 2
  while File.exist?(candidate)
    candidate = File.join(inbox, format('%s_%02d.json', base, index))
    index += 1
  end
  candidate
end
```

- [x] **Step 2: Use it in the atomic writer**

```ruby
final_path = next_output_path(inbox)
temp_path = "#{final_path}.tmp"
```

Do not change JSON generation, flush, fsync, rename, or ensure cleanup.

- [x] **Step 3: Confirm focused GREEN**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_sketchup_ruby_contract.py tests/integration/test_rbz_package.py tests/integration/test_sketchup_ruby_pipeline.py -q
```

### Task 4: Rebuild and hand off the RBZ checkpoint

**Files:**
- Generated: `build/sketchup/STAAD_Prep_Bridge_0.1.0.rbz`
- Modify if instructions change: `packaging/INSTALL_RBZ.md`

**Interfaces:**
- Consumes: updated Ruby source
- Produces: reinstallable version-matched RBZ

- [x] **Step 1: Build the RBZ**

```powershell
..\..\.venv\Scripts\python.exe scripts/build_sketchup_rbz.py
```

- [x] **Step 2: Verify**

```powershell
..\..\.venv\Scripts\python.exe -m pytest tests/unit/test_sketchup_ruby_contract.py tests/integration/test_rbz_package.py tests/integration/test_sketchup_ruby_pipeline.py -q
..\..\.venv\Scripts\python.exe -m ruff check tests/unit/test_sketchup_ruby_contract.py tests/integration/test_rbz_package.py
git diff --check
```

- [x] **Step 3: Stop for user acceptance**

Deliver the rebuilt RBZ. Acceptance: dialog opens; the three buttons are understandable and usable; export succeeds; output resembles `SP_20260830_140328.json`.

- [x] **Step 4: Commit after acceptance**

```powershell
git add extensions/sketchup_staadprep tests/unit/test_sketchup_ruby_contract.py tests/integration/test_rbz_package.py packaging/INSTALL_RBZ.md docs/superpowers/specs/2026-08-30-post-t22-usability-design.md docs/superpowers/plans/2026-08-30-sketchup-bridge-usability.md
git commit -m "feat: clarify SketchUp bridge export workflow"
```

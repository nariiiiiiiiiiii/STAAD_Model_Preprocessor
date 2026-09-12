# Install STAAD Prep Bridge in SketchUp

The portable Windows application itself does not require installation. SketchUp integration is optional and uses the bundled `.rbz` extension package.

1. Open SketchUp.
2. Open **Extension Manager**.
3. Choose **Install Extension**.
4. Select the bundled `STAAD_Prep_Bridge_<VERSION>.rbz` from the portable package's `SketchUp_Extension/` folder.
5. Restart SketchUp if requested.
6. Open **STAAD Prep Bridge...** from the extension toolbar/menu.
7. The bridge window explains the geometry handoff and displays the configured inbox.
8. Use **Choose Inbox...** to select any existing output folder; the portable `Data/Inbox/SketchUp` folder is only the default.
9. Use **Export Geometry** to write a file named after the SketchUp model and export date, such as `13-DIZ-SD11-09-69_12092026.json`.

The date uses `DDMMYYYY` in the computer's local time. If the model has not been saved, its SketchUp title is used (or `Untitled` when blank). Re-exporting the same model on the same day adds `_02`, `_03`, and so on to avoid overwriting an existing JSON.

The extension writes Neutral JSON to the configured STAAD Prep inbox. It transfers geometry only and does not perform structural analysis. Installing or updating the `.rbz` is a SketchUp action separate from the no-install portable Windows application.

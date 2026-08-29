# Manual Update — STAAD Model Preprocessor <VERSION>

T22 intentionally does not install or download updates automatically. Use this safe portable update procedure:

1. Close the old STAAD Model Preprocessor application.
2. Extract the new portable ZIP into a **new writable folder**.
3. Copy the complete `Data/` directory from the old release into the new release, preserving its directory structure.
4. Launch the new `STAAD Model Preprocessor.exe`.
5. Verify the displayed/release version and perform the normal open/import/validate/export workflow.
6. Keep the old portable release as rollback until the new release has been verified to your satisfaction.

Do not copy old application DLLs or executable files into the new release. `Data/` is the preserved state root; application files are version-managed by `package-manifest.json`.

A future automatic updater may automate these steps, but it must preserve every root listed in the manifest's `preserve_roots` field and verify package hashes before replacement.

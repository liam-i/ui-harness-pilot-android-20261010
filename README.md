# Approved-design native Android menu trial

This isolated Java/Android Views project consumes the fixed Figma design package in `design-inputs/`. The actual human design and engineering approvals are retained under `evidence/engineering-review/` and the fixed Git references in the current Change. The sole implementation tasks are in `openspec/changes/archive/2026-10-10-consume-approved-android-menu/tasks.md`.

The trial covers a menu, a reset confirmation and a static session preview. It has no full gameplay, network service or cross-process persistence. Verified scope is the two declared Android emulator configurations at font scale 1.0 and 1.3; this is not a general claim about other platforms, font scales or API levels.

## Local validation

Use the reviewed Java 17, Gradle 8.13, AGP 8.13.2 and existing dedicated AVDs. Host configuration stays outside this repository and supplies `jdk`, `gradle`, `gradle_home`, `sdk`, `gradle_cache`, `android_user`, `emulator_home` and `avds`. Run the shared current UI check before dependent execution. The native entry requires a clean, fixed source SHA:

```bash
python3 harness/ui-design/ci/android-native.py   --root "$PWD" --head "$(git rev-parse HEAD)"   --config harness/ui-ci/android-native.json   --host-config /absolute/path/to/reviewed-host.json   --output /absolute/path/to/new-evidence-directory
```

The driver performs real touches and key events, reads debug-only native observations and system accessibility nodes, captures screenshots and restores the original device settings. The fixed 32-case denominator, timing limits, source/APK identities and all failures remain explicit. No test API injects application state.

The required CI scenarios were verified across six actual runs. Attempt 5 failed and remains recorded as such; the approved driver repair passed in attempt 6. Hosted CI, real human runtime acceptance and local archival have separate evidence.

## Verified trial and local archive

Final native-tested source: `22ba5e4faf2ed031c83c8abad95c82dcbc1535cd`; APK SHA-256: `1c59d3e92134df751d480d567a8fbe5db51d8ae635e97461f44ca317903ab73b`. Actual human runtime acceptance and local archive authorization are retained in `evidence/engineering-review/`. The Change has been archived locally after that approval; product, tests, workflow and fixed D/A remain the reviewed bytes. Subsequent local evidence and archive commits are not claimed as new native CI runs. The public PR remains unmerged.

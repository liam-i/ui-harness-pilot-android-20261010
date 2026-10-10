# Approved-design native Android menu trial

This isolated Java/Android Views project consumes the fixed Figma design package in `design-inputs/`. The actual human design and engineering approvals are retained under `evidence/engineering-review/` and the fixed Git references in the current Change. The sole implementation tasks are in `openspec/changes/consume-approved-android-menu/tasks.md`.

The trial covers a menu, a reset confirmation and a static session preview. It has no full gameplay, network service or cross-process persistence. Verified scope is the two declared Android emulator configurations at font scale 1.0 and 1.3; this is not a general claim about other platforms, font scales or API levels.

## Local validation

Use the reviewed Java 17, Gradle 8.13, AGP 8.13.2 and existing dedicated AVDs. Host configuration stays outside this repository and supplies `jdk`, `gradle`, `gradle_home`, `sdk`, `gradle_cache`, `android_user`, `emulator_home` and `avds`. Run the shared current UI check before dependent execution. The native entry requires a clean, fixed source SHA:

```bash
python3 harness/ui-design/ci/android-native.py   --root "$PWD" --head "$(git rev-parse HEAD)"   --config harness/ui-ci/android-native.json   --host-config /absolute/path/to/reviewed-host.json   --output /absolute/path/to/new-evidence-directory
```

The driver performs real touches and key events, reads debug-only native observations and system accessibility nodes, captures screenshots and restores the original device settings. The fixed 32-case denominator, timing limits, source/APK identities and all failures remain explicit. No test API injects application state.

The GitHub workflow is a reviewed candidate until separately authorized. Hosted CI, actual human runtime acceptance and archival remain distinct from the local results.

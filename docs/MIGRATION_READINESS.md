# MCU Dev Tools migration readiness

Audited 2026-10-02 against read-only Reader master
`82caa0997e913f01c1f5f9ab942d056bc9f04a82`; external base
`70fd3ad39eaacdb736a16de5f351c128b208f255`. The three current source deltas
are manifest-only version advances. Their C sources and recorded helper are
unchanged from the external base; the external Stream/UI API snapshots remain
untouched, including their existing local differences.

| Tool | Source/manifest status | Version | Published package / nested ELF identity | External profile |
| --- | --- | --- | --- | --- |
| [Serial Monitor](apps/serial_monitor.md) | C and include unchanged; current manifest synchronized | 1.2.7 | ZIP `b30f9eb1…`; ELF `c3b95464…` / 20,952 B | strip-unneeded |
| [USB Debug](apps/usb_debug.md) | C unchanged; current manifest synchronized | 0.1.2 | ZIP `07984001…`; ELF `09d8498d…` / 21,048 B | strip-unneeded |
| [Firmware Flasher](apps/esp_rom_flasher.md) | C and tracked helper unchanged; current manifest synchronized | 1.1.1 | ZIP `ce934123…`; ELF `970cf848…` / 12,504 B | strip-unneeded |

The release ZIP digests and sizes match Reader release-index commit
`5caf9b7fd98700f9e7ee5b69406c6c163c6e7206` and the public non-draft release
assets. The index's nested ELF identities are the independent pipeline's exact
published-byte gates. Previous unstripped versions and hashes remain in
`sdk/release-baseline.json` for lineage. The profile is selected from exact app
ID/version records, so the three new releases do not overwrite historical byte
identity. Source drift and current per-tool release metadata are in
[source-drift.json](source-drift.json) and
[release-parity.json](release-parity.json).

The PR's full independent build, host fixtures, ELF validation and nested
published-byte comparisons must pass on the exact head before merge. The pinned
SDK/compiler, provider fixtures, external app implementations, and external
T5Stream/T5Ui SDK variants are preserved. No broad SDK rebase is implied.

## Daily tool behavior

The scope only updates package manifest identities and the version-aware ELF
build profile. Serial terminal/reconnect behavior, USB descriptor/logging paths,
and ESP/MSP flasher source behavior remain unchanged. Passing host tests or
artifact parity does not establish physical programming, serial transport,
device hotplug, or hardware behavior.

## Readiness boundary

This documents current Reader master source parity and published artifact
identity only. It does not authorize or claim U1 package-format migration, live
catalog publication, provider runtime cutover, source deletion, or device
qualification. Those remain separate milestones. External readiness criteria
and their required runtime/hardware evidence are retained below.

## Existing external runtime/removal requirements

1. Freeze the accepted firmware/SDK/provider baseline and reconcile future
   master/U1 changes without discarding external fixes.
2. Separately authorize and validate per-app `.rte.zip`, generic manifests,
   index entries, per-ID install layout, and any resource packaging.
3. Verify target-runtime discovery, install/update, rollback/recovery, and
   removal with the actual external provider set.
4. Establish daily-use acceptance for serial send/receive, baud changes,
   unplug/reconnect, USB descriptors and logging, and intended ESP/MSP images,
   cancellation, connection loss, and successful programming on hardware.
5. Verify external asset availability and rollback before any live catalog
   change; obtain explicit owner authorization before external-provider cutover
   or duplicate Reader source/build/catalog removal.

No releases, live catalog changes, U1 writes, actual flashing, Reader edits, or
cutover occur in this parity refresh.

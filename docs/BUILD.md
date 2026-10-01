# Independent MCU Dev Tools build

Requirements: Python 3.11+, host C compiler, pinned public Xtensa S3 toolchain.

```sh
python -m pip install platformio==6.1.19
pio pkg install --global --tool 'espressif/toolchain-xtensa-esp32s3@8.4.0+2021r2-patch5'
python -m unittest discover -s tests -v
python scripts/test_apps.py
python scripts/test_regressions.py
python scripts/build_all_apps.py
python scripts/check_release_parity.py
```

`PLATFORMIO_CORE_DIR` selects another compiler package directory;
`NATIVE_APP_CC` selects the executable. A selective builder invocation such as
`--id serial_monitor` clears prior generated outputs and builds only that tool.
The release-parity check deliberately requires the full three-tool inventory.

## Published-build profile and version integrity

These three releases predate Reader's symbol-stripping change. The current
Reader default strips unneeded symbols; that produces smaller, different ELFs
under unchanged app versions. This repository intentionally uses the historical
**unstripped C11/PIC/shared/SysV-hash profile** to reproduce the existing released
bytes exactly. It still checks all dynamic imports and validates actual ELF
structure. It does not publish new stripped payloads under old versions.

Serial Monitor remains 1.2.6, USB Debug 0.1.1 and Firmware Flasher 1.1.0: all
app/helper source and installed manifest metadata are unchanged, and all three
produced ELFs match their published sizes/SHA-256. A future source, metadata or
payload-changing build profile must advance the corresponding app version before
publication. No release is performed by this development workflow.

## SDK provenance and outputs

`sdk/baseline.json` pins required API and transitive provider headers, limited
compiler helpers, manifest/integrity checks, real firmware ELF validator and
five upstream fixtures by Git blob and SHA-256. Source is Reader
`3300229d0a232b4e6047a7c93b2f518c033c3cfa`. Original license/comments are retained.
The public app/libc/compat export list is derived from the recorded source table
blobs; it does not use the privileged-provider inventory or grant capability
access. Build/audit wrappers are adapted from Productivity main `0a2d189f` and
System-Apps main `b64e1c99`, with this repository's `tools` inventory and helper
filenames handled explicitly.

Full output contains three ELF+JSON pairs, `build-evidence.json` and
`release-parity.json`. Evidence records source/manifest/helper blobs, version,
actual compiler and build profile, SDK/repository commits and dirty state,
length and SHA-256. CI uploads a 14-day development artifact, never an install
catalog. Baseline changes, unsafe/duplicate inventory entries, unknown imports,
manifest/version mismatch, invalid ELF structure and published-byte drift fail.
The structural validator also exercises malformed-header, section and relocation
mutations against each built ELF.

## Focused host test coverage

- Ten Python pipeline tests: hashes, manifests, inventory safety, three-way drift,
  imports, integrity and complete-cohort byte comparisons.
- Four unchanged upstream Serial Monitor fixtures: session/terminal behavior,
  baud application/reacquisition, interactive no-device behavior, and startup
  rendering/source ordering. The startup contract is source inspection, not a
  runtime fixture.
- Unchanged upstream USB Debug fixture: descriptor capture, safe HID probing,
  interface cleanup, fallback identifiers and SD log path.
- New UBSan-enabled Firmware Flasher fixture calls real app functions with
  mock streams/programmer: split-token TI-TXT reads, valid multiple address
  segments, malformed/out-of-bounds/missing-terminator input, cancellation,
  bounded stalled input, oversized provider counts, and ESP stream cleanup on
  success/failure. No real device is accessed or programmed.

These checks do not prove electrical flashing, transport/hotplug behavior,
provider quiescence on hardware, actual SD persistence or U1 acceptance. ESP
ROM protocol/provider implementation tests in Reader are outside this app-only
snapshot. The retained `esp_rom_md5.h` helper is tracked for source parity but
is not included by the current Firmware Flasher implementation.

## Source-aware maintenance

```sh
python scripts/check_baseline.py --reader /path/to/read-only/Reader \
  --ref FULL_COMMIT_SHA --output docs/source-drift.json
```

This optional audit reads immutable Reader Git objects only. It classifies
unchanged/converged/upstream-only/external-only/conflicting source, manifest and
helper inputs. Without Reader it establishes local agreement only. It never
rewrites apps. Preserve external fixes, reconcile conflicts, inspect SDK/ABI
changes and rerun all checks before advancing any baseline.

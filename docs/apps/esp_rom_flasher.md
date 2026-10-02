# Firmware Flasher

## Purpose

Firmware Flasher programs firmware images into supported external microcontrollers through RiscRTE programming providers. Its manifest identifies `esp_rom_flasher.elf`, version **1.1.1**, minimum firmware **1.2.69**, categories `Firmware`, `Developer`, and `Hardware`.

Despite the historical source filename, the current app supports both ESP ROM-bootloader programming and MSP430FR TI-TXT programming.

## RiscRTE interfaces

The app uses:

- `T5AppApi`
- `T5ProgramEspRomApi`
- `T5ProviderCapabilityApi`
- `T5StreamApi`
- `T5UiApi`
- `RiscProgramMspV1`

The manifest declares `program.msp >=1` as an optional capability. ESP programming is obtained through the ESP ROM programming API; MSP programming is obtained through the provider-capability mechanism.

## Supported image types

The app scans SD-visible files and recognizes:

- ESP merged binary images (`.bin`)
- MSP430 TI-TXT text images (`.txt` interpreted as TI-TXT when selected for MSP programming)

The current UI supports up to 64 image entries.

ESP programming expects a merged ESP image positioned for programming from address 0. The app opens the image through `T5StreamApi` and passes the stream and image size to the current runtime ESP programming API. The current-master API boundary is preserved here; this does not establish prospective U1 provider ownership.

MSP TI-TXT input is parsed incrementally from a stream. The parser validates address records, byte tokens, bounds, and the terminating `q` record before programming.

## Programming UI

The app renders a selectable image list. Each entry indicates whether it is treated as an ESP merged BIN or MSP430FR TI-TXT image.

Programming progress is presented by stage. Recognized ESP stages include validation, hashing, connect, configure, erase, write, verify, reset, and complete. During long write/hash operations the UI includes percentage progress.

The app deliberately reduces redraw frequency by only updating on stage changes, meaningful message changes, 5-percent progress increments, or completion.

## Cancellation and safety

Back/exit input is checked during programming and parsing. The progress callback returns false when cancellation is requested so the provider can stop cooperatively.

MSP image parsing is bounded to a maximum of 1 MiB of programmed data and rejects malformed or out-of-range TI-TXT data before mutation/programming proceeds.

Failures preserve and display provider/programmer messages when available; otherwise the app reports a bounded generic error.

## Provider/hardware dependencies

Actual electrical transport and target programming are not implemented in the app. ESP serial programming depends on the runtime ESP programming provider and its underlying serial transport (for example FTDI/CDC/CP210x/CH34x as available). MSP programming depends on the `program.msp` provider and corresponding probe support.

## Source

- `Apps/esp_rom_flasher.c`
- `Apps/esp_rom_flasher.json`
- `Apps/esp_rom_md5.h` — retained historical helper; the current app does not include it or implement ESP MD5 locally

## Current master and published artifact

Reader master `82caa0997e913f01c1f5f9ab942d056bc9f04a82` advances this package manifest from 1.1.0 to 1.1.1 (manifest blob `9b1e80f73d4ff102f6675c54b799c54612b8c82d`). The C source plus tracked helper `Apps/esp_rom_md5.h` remains byte-identical to the external baseline; no application behavior or API source is copied. Its current published [release tag](https://github.com/michaelrolphone-cmyk/T5S3-Reader/releases/tag/app-esp_rom_flasher-v1.1.1) contains `application-esp_rom_flasher-1.1.1-xtensa-esp32s3.rte.zip` (13,668 bytes, SHA-256 `ce934123869cd7ddba774af741841c1ad3c8e2d0716c72335971a5228044c9d0`). The package index records the nested ELF as 12,504 bytes, SHA-256 `970cf8483e8c7efcb35c73fb498e0b74d035ec24d60cf694433648c5bb44d508`.

The independent build selects the current `strip-unneeded` ELF profile by exact app manifest version and checks the finished file against the nested published ELF identity. Historical pre-strip versions remain recorded as `unstripped` in `sdk/release-baseline.json`. The exact-head Actions check validates the profile and actual bytes; this evidence is source/build parity only, not U1 ZIP/cutover or hardware qualification.


## Master parity note

The external build snapshot carries Reader master `T5UiApi.h`'s append-only optional `get_viewport` member (source commit `82caa0997e913f01c1f5f9ab942d056bc9f04a82`). This app does not call that optional member. The external `T5StreamApi.h` service-borrowing behavior is retained.

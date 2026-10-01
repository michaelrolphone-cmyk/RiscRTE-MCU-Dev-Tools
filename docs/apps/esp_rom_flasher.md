# Firmware Flasher

## Purpose

Firmware Flasher programs firmware images into supported external microcontrollers through RiscRTE programming providers. Its manifest identifies `esp_rom_flasher.elf`, version **1.1.0**, minimum firmware **1.2.69**, categories `Firmware`, `Developer`, and `Hardware`.

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

## Independent migration verification

Source, manifest and recorded helpers match Reader master
`3300229d0a232b4e6047a7c93b2f518c033c3cfa`. Independent builds preserve the
historical unstripped build profile and exactly reproduce this app's existing
published ELF. Versions remain unchanged because source, installed metadata and
published payload bytes are unchanged. See [build/tests](../BUILD.md),
[artifact comparison](../release-parity.json) and
[readiness/removal criteria](../MIGRATION_READINESS.md). Current-master parity
does not imply future U1 packaging/runtime acceptance or hardware qualification.

# Serial Monitor

## Purpose

Serial Monitor is an interactive RiscRTE terminal for serial devices exposed through the runtime's serial-port capability layer. Its manifest identifies `serial_monitor.elf`, version **1.2.7**, minimum firmware **1.2.31**, categories `Developer`, `Diagnostics`, and `Connectivity`.

The application itself does not implement USB host controllers or USB serial class drivers. It consumes the runtime serial API and reports provider/capability failures to the user.

## RiscRTE interfaces

The app uses:

- `T5SerialPortApi`
- `T5UiApi`
- `T5AppApi`
- `T5StreamApi`
- `T5SystemUiApi` (keyboard handoff)

The implementation obtains the provider-owned serial API and wraps selected functions before handing them to the shared Serial Monitor implementation.

The wrapper intercepts:

- `acquire` — to keep the existing terminal UI alive across temporary provider failures, expose detailed provider diagnostics, and rate-limit repeated failed acquisition attempts.
- `read_status` — to surface asynchronous runtime/provider errors in the terminal.
- UI `render_list` and `render_text_view` — to avoid replacing an already usable terminal with a reconnect spinner during retry cycles and to track when the terminal has been rendered.

## Failure/reconnect behavior

After a failed serial acquisition the app skips four immediate retry cycles before asking the provider again. This prevents an absent/unavailable serial device from trapping the app in continuous synchronous activation/retry work.

When `last_diagnostic` is available in the serial API, its detail string is appended to the terminal. Otherwise the app reports the numeric acquire result.

Recognized runtime errors include:

- `-1240` — a USB device enumerated but no matching serial class ELF bound; the app specifically directs the user to check CH34x/CDC/CP210x/FTDI driver installation.
- `-1241` — the USB device attached but its configuration descriptor was unavailable.
- Other errors are reported generically as USB serial provider errors.

Repeated identical failures are suppressed so the terminal does not fill with duplicate diagnostics.

## UI behavior

The shared implementation is included from `serial_monitor_implementation.inc`. The wrapper preserves that implementation's normal terminal behavior while adding capability/provider diagnostics. The terminal remains interactive when the provider is temporarily unavailable rather than being permanently replaced by a loading screen.

## Terminal controls and limits

The included implementation starts at 115200 baud, 8 data bits, no parity, one
stop bit and no flow control. It exposes baud, data-bit, parity and stop-bit
selection, custom baud entry (300–3000000), and an automatic baud/framing probe.
Applying a new configuration requires provider success rather than merely
changing the displayed settings.

The terminal buffer is 12,288 bytes; keyboard send input is capped at 256
characters plus termination; autodetection samples up to 320 bytes per candidate.
The app uses generic streams for received/transmitted data and firmware keyboard
handoffs for send/custom-baud input. Its terminal state is in memory, with no
app-owned persistent log file in this source.

## Hardware/provider dependencies

Serial Monitor requires a working `serial.port` provider. For USB serial hardware, that provider in turn depends on the relevant installed USB host/controller/class-driver stack. Those drivers are outside this application.

## Source

- `Apps/serial_monitor.c`
- `Apps/serial_monitor_implementation.inc`
- `Apps/serial_monitor.json`

## Current master and published artifact

Reader master `82caa0997e913f01c1f5f9ab942d056bc9f04a82` advances this package manifest from 1.2.6 to 1.2.7 (manifest blob `71977dc7608651136f1a26a37c4416cd4eb03be1`). The C source plus implementation include `Apps/serial_monitor_implementation.inc` remains byte-identical to the external baseline; no application behavior or API source is copied. Its current published [release tag](https://github.com/michaelrolphone-cmyk/T5S3-Reader/releases/tag/app-serial_monitor-v1.2.7) contains `application-serial_monitor-1.2.7-xtensa-esp32s3.rte.zip` (22,058 bytes, SHA-256 `b30f9eb12c1cfea80463816abcf35ec9358b6c43cdff642eeba45eba72409206`). The package index records the nested ELF as 20,952 bytes, SHA-256 `c3b95464ade5005e98d060fd84d93d7682f72d1bdb7a502b0e4f4f6d76d2c67a`.

The independent build selects the current `strip-unneeded` ELF profile by exact app manifest version and checks the finished file against the nested published ELF identity. Historical pre-strip versions remain recorded as `unstripped` in `sdk/release-baseline.json`. The exact-head Actions check validates the profile and actual bytes; this evidence is source/build parity only, not U1 ZIP/cutover or hardware qualification.


## Master parity note

The external build snapshot carries Reader master `T5UiApi.h`'s append-only optional `get_viewport` member (source commit `82caa0997e913f01c1f5f9ab942d056bc9f04a82`). This app does not call that optional member. The external `T5StreamApi.h` service-borrowing behavior is retained.

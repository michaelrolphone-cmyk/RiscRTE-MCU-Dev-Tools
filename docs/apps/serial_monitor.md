# Serial Monitor

## Purpose

Serial Monitor is an interactive RiscRTE terminal for serial devices exposed through the runtime's serial-port capability layer. Its manifest identifies `serial_monitor.elf`, version **1.2.6**, minimum firmware **1.2.31**, categories `Developer`, `Diagnostics`, and `Connectivity`.

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

## Independent migration verification

Source, manifest and recorded helpers match Reader master
`3300229d0a232b4e6047a7c93b2f518c033c3cfa`. Independent builds preserve the
historical unstripped build profile and exactly reproduce this app's existing
published ELF. Versions remain unchanged because source, installed metadata and
published payload bytes are unchanged. See [build/tests](../BUILD.md),
[artifact comparison](../release-parity.json) and
[readiness/removal criteria](../MIGRATION_READINESS.md). Current-master parity
does not imply future U1 packaging/runtime acceptance or hardware qualification.

# Serial Monitor

## Purpose

Serial Monitor is an interactive RiscRTE terminal for serial devices exposed through the runtime's serial-port capability layer. Its manifest identifies `serial_monitor.elf`, version **1.2.6**, minimum firmware **1.2.31**, categories `Developer`, `Diagnostics`, and `Connectivity`.

The application itself does not implement USB host controllers or USB serial class drivers. It consumes the runtime serial API and reports provider/capability failures to the user.

## RiscRTE interfaces

The app uses:

- `T5SerialPortApi`
- `T5UiApi`

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

## Hardware/provider dependencies

Serial Monitor requires a working `serial.port` provider. For USB serial hardware, that provider in turn depends on the relevant installed USB host/controller/class-driver stack. Those drivers are outside this application.

## Source

- `Apps/serial_monitor.c`
- `Apps/serial_monitor_implementation.inc`
- `Apps/serial_monitor.json`

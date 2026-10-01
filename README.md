# RiscRTE MCU Dev Tools

Independent source repository for optional RiscRTE microcontroller development, diagnostics, programming, and hardware-debug applications.

## Scope

This repository is intentionally separate from `RiscRTE-System-Apps`. It contains applications whose primary purpose is communicating with, inspecting, diagnosing, debugging, or programming external microcontrollers and attached development hardware.

During migration, `michaelrolphone-cmyk/T5S3-Reader` is a strictly read-only upstream source of truth.

## Application documentation

- [Serial Monitor](docs/apps/serial_monitor.md) — serial-port terminal, provider acquisition/retry behavior, and USB serial diagnostics.
- [USB Debug](docs/apps/usb_debug.md) — USB device/descriptor inspection and diagnostic logging.
- [Firmware Flasher](docs/apps/esp_rom_flasher.md) — ESP ROM and MSP430FR programming workflows.

## Independent builds and migration readiness

- [Pinned build instructions and focused test coverage](docs/BUILD.md)
- [Readiness index and safe Reader removal criteria](docs/MIGRATION_READINESS.md)
- [Eight-file source/helper drift audit](docs/source-drift.json)
- [Published ELF byte-parity evidence](docs/release-parity.json)

Builds need no Reader checkout. CI emits development artifacts only, using the
historical unstripped profile that reproduces all three current app releases.
No live catalog or release is written.

## Documentation and parity policy

Each tool has a dedicated source-derived page covering interfaces/capabilities,
workflows, dependencies, limits, persistence and failure handling. Treat future
U1 requirements separately from implemented current-master behavior. Source,
manifest, build/release bytes and documentation must all be audited before
parity is claimed. Record source baselines, preserve external-only fixes and
reconcile conflicts instead of blindly copying upstream.

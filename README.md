# RiscRTE MCU Dev Tools

Independent source repository for optional RiscRTE microcontroller development, diagnostics, programming, and hardware-debug applications.

## Scope

This repository is intentionally separate from `RiscRTE-System-Apps`. It contains applications whose primary purpose is communicating with, inspecting, diagnosing, debugging, or programming external microcontrollers and attached development hardware.

During migration, `michaelrolphone-cmyk/T5S3-Reader` is a strictly read-only upstream source of truth.

## Application documentation

- [Serial Monitor](docs/apps/serial_monitor.md) — serial-port terminal, provider acquisition/retry behavior, and USB serial diagnostics.
- [USB Debug](docs/apps/usb_debug.md) — USB device/descriptor inspection and diagnostic logging.
- [Firmware Flasher](docs/apps/esp_rom_flasher.md) — ESP ROM and MSP430FR programming workflows.

## Repository tree

```text
Apps/
  esp_rom_flasher.c
  esp_rom_flasher.json
  esp_rom_md5.h
  serial_monitor.c
  serial_monitor.json
  serial_monitor_implementation.inc
  usb_debug.c
  usb_debug.json

docs/
  apps/
    esp_rom_flasher.md
    serial_monitor.md
    usb_debug.md

mcu-dev-tools-manifest.json
```

## Documentation and parity policy

Each migrated tool must have one dedicated documentation page derived from its current source, manifest, ABI headers, and actual behavior. The page must document interfaces/capabilities, workflows, dependencies, limits, persistence, failure handling, and helper files where applicable. Unimplemented or future behavior is not treated as specification.

A tool is not parity-complete until source, manifest/version, build/release behavior, and documentation are aligned with the read-only upstream source.

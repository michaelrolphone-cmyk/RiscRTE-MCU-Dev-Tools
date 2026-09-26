# RiscRTE MCU Dev Tools

Independent source repository for optional RiscRTE microcontroller development, diagnostics, programming, and hardware-debug applications.

## Scope

This repository is intentionally separate from `RiscRTE-System-Apps`.

It contains tools used to inspect, debug, communicate with, or program external microcontrollers and attached development hardware. During migration, `michaelrolphone-cmyk/T5S3-Reader` is treated as a strictly read-only upstream source of truth.

Initial migrated tool set:

- Serial Monitor
- USB Debug
- Firmware Flasher

Additional upstream apps are included only when they fit this MCU development/debug scope.

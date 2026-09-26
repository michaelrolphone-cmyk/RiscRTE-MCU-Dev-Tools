# USB Debug

## Purpose

USB Debug is a hardware-inspection and logging tool for USB devices attached through the RiscRTE USB host stack. Its manifest identifies `usb_debug.elf`, version **0.1.1**, minimum firmware **1.2.67**, categories `Developer`, `Diagnostics`, and `Hardware`.

The manifest declares `usb.host >=1` as an optional capability. The app is designed to inspect devices when that capability/provider is available.

## RiscRTE interfaces

The app uses:

- `T5AppApi`
- `T5ProviderCapabilityApi`
- `T5StorageApi`
- `T5UiApi`
- `RiscUsbDiscoveryDiagnosticsV1`

It acquires the USB host capability through the provider-capability API and uses the returned USB host/discovery/diagnostic interfaces rather than directly owning the controller.

## Device inspection

The app supports up to eight devices in its local device table. For each device it can collect and display identifiers and descriptor-derived fields including VID, PID, USB/device BCD values, device class/subclass/protocol, manufacturer/product/serial strings, configuration count, and a generated stable-ish log identifier based on VID/PID and serial string when available.

USB class values are translated to readable labels for common standard classes such as HID, CDC, mass storage, hub, video, and vendor-specific devices.

## Descriptor inspection

The implementation issues standard control requests through the host API, including GET_DESCRIPTOR, GET_STATUS, and GET_CONFIGURATION.

Descriptor parsing recognizes at least:

- Device
- Configuration
- String
- Interface
- Endpoint
- Device qualifier
- Interface Association
- BOS
- HID
- HID report
- Class-specific interface/endpoint descriptors

Configuration descriptors use the runtime-defined `RISC_USB_CONFIG_LIMIT` buffer. HID report reads use a separate 1024-byte buffer so they do not overwrite the configuration descriptor while it is being parsed.

String descriptors are decoded from UTF-16LE into bounded UTF-8 output. The app attempts the device's preferred language and falls back to US English (`0x0409`) when necessary.

## Logging

The app maintains an in-memory diagnostic log capped at 24 KiB. Hex dumps are emitted in 16-byte rows. Formatting uses bounded local buffers because the native app ABI does not expose arbitrary libc formatting helpers such as `vsnprintf`.

The source includes storage support for persisting logs; filenames are sanitized and incorporate the USB device identifier.

## Implementation limits

- Maximum tracked devices: 8
- Diagnostic log buffer: 24 KiB
- USB string descriptor buffer: 255 bytes
- HID report buffer: 1024 bytes
- Control transfer timeout: 100 ms

These are implementation limits in the current source, not general RiscRTE USB limits.

## Source

- `Apps/usb_debug.c`
- `Apps/usb_debug.json`

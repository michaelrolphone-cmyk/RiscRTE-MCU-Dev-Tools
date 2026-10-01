# MCU Dev Tools migration readiness

Audited 2026-10-01 against read-only Reader master
`3300229d0a232b4e6047a7c93b2f518c033c3cfa`.
Rechecked newer master `a5e2db59077cc889079668dc9cd7428b08bc32a1`: all
app inputs, pinned SDK/fixtures and export-source inputs are unchanged.

| Tool | Current-master source/manifest/helper | Version | Independent published-byte build | Documentation |
| --- | --- | --- | --- | --- |
| [Serial Monitor](apps/serial_monitor.md) | Exact, 3 inputs | 1.2.6 unchanged | Pass, historical unstripped profile | Interfaces, terminal limits, failure/retry behavior |
| [USB Debug](apps/usb_debug.md) | Exact, 2 inputs | 0.1.1 unchanged | Pass, historical unstripped profile | Descriptor/claim/log behavior |
| [Firmware Flasher](apps/esp_rom_flasher.md) | Exact, 3 inputs | 1.1.0 unchanged | Pass, historical unstripped profile | ESP/MSP boundaries, parser/cancellation, unused helper |

All eight existing external inputs already matched Reader; no blind source copy,
external fix overwrite or app version change was necessary. See the exact
[blob audit](source-drift.json). [Build/test instructions](BUILD.md) explain the
pinned SDK and historical profile; [release comparison](release-parity.json)
records actual built and published hashes. CI must validate the final PR head;
local evidence alone is not a claim that CI/merge passed.

## Why this matters for daily tools

Independent builds now preserve the usable Serial Monitor terminal and baud
configuration behavior, USB inspection/logging, and ESP/MSP programming front
end without requiring a firmware checkout. Focused fixtures exercise those
boundaries and failure cases, but a passing mock test does not prove a physical
programming session. The current-master API dependencies remain explicit.

## Open requirements before safe Reader removal

None of these apps is approved for Reader removal or live external cutover.

1. Freeze the accepted firmware/SDK/provider baseline and reconcile master/U1
   changes without discarding external fixes. Serial Monitor's current serial
   facade, USB Debug's host diagnostic interface, and Flasher's ESP/MSP paths
   must each be checked; do not assume identical capability declarations.
2. Implement/validate the accepted U1 per-app `.rte.zip`, generic manifests/index,
   per-ID install layout and resource packaging in a separately authorized
   external release pipeline. Current output remains development ELF+JSON.
3. Verify target-runtime discovery, install/update, rollback/recovery and removal
   with the actual external provider set. Preserve app identity/version ordering.
4. Establish daily-use acceptance: serial send/receive, baud changes, unplug/
   reconnect and missing class drivers; USB descriptors/claim cleanup and saved
   logs; intended ESP/MSP image validation, explicit programming confirmation,
   cancellation, connection loss and successful verification on intended hardware.
5. Verify external asset availability/digests and a safe rollback before changing
   any live catalog. Obtain explicit owner authorization for the external-provider
   switch and Reader duplicate source/build/catalog deletion.

Prospective U1 ABI/package/runtime compatibility remains unverified. No provider
ownership claim is inferred from the legacy app facades, and no permanent
firmware-side substitute is established by this snapshot. No releases, actual
flashing, Reader edits, live catalog changes or cutover occur here.

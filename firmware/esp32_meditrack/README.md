# MediTrack ESP32 firmware (Part 2)

This self-contained PlatformIO project implements a fail-closed, non-blocking
`millis()` state machine for the Part 1 three-cylinder dispenser. It uses the
SH1106 on I2C 21/22, lid GPIO18, optional chute GPIO27, buzzer GPIO19, buttons
4/16/17, LEDs 2/15, and servos 23/25/26. `include/config.h` contains safe
placeholders; copy `config.example.h` and edit local values without committing
credentials.

## Build, upload, and monitor

Install PlatformIO Core locally (or use the PlatformIO IDE), then from this
directory run:

```bash
pio pkg install
pio run
pio run --target upload --upload-port /dev/cu.usbserial-XXXX
pio device monitor --port /dev/cu.usbserial-XXXX --baud 115200
```

Linux ports are commonly `/dev/ttyUSB0` or `/dev/ttyACM0`. The project pins the
Espressif platform and all external Arduino libraries in `platformio.ini`.

## Behavior and telemetry

At the configured UTC/local-TZ time, the device requests local confirmation,
checks the lid, opens exactly one selected gate, waits for an optional chute
transition, and closes the gate. A reset during any active operation enters
`FAULT` and never retries automatically. The confirm button clears a fault only
after inspection; mute/snooze abandons a due dose and records `DOSE_SNOOZED`.
Telemetry uses the existing backend `POST /api/v1/telemetry` event names. Failed
requests are newline-delimited JSON in LittleFS, bounded to 64 KiB, and replayed
FIFO after Wi-Fi returns. Preferences persists the state/day/compartment.

## Offline validation

`python3 tools/validate_firmware.py` checks the pin mapping, required states,
non-blocking source patterns, pinned dependencies, and safe config placeholders.
It requires only the Python standard library. `pio run` is the hardware compile
check and requires PlatformIO's package cache; no network is needed after the
first dependency resolution.

## Safety

Use only a certified isolated 5 V supply, a fused servo rail, common ground, and
a bulk capacitor near the servos. GPIO19 drives a MOSFET gate, never the buzzer
load. Verify GPIO2/GPIO15 boot strap behavior on the exact ESP32 board. Test
with inert objects and a mechanically fail-closed gate; chute confirmation only
means an object passed and never proves identity, dose correctness, or ingestion.

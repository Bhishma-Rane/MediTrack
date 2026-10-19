# Power and fail-safe design

## Design assumptions

The prototype uses a certified isolated 5 V, 2 A USB supply. The figures below
are conservative design estimates; measure the final parts rather than treating
them as certification evidence.

| Load | Typical | Design peak | Rail |
| --- | ---: | ---: | --- |
| ESP32 Wi-Fi and MCU | 160 mA | 500 mA | 5 V input via board regulator |
| SH1106 OLED | 25 mA | 40 mA | 3.3 V |
| Lid microswitch / Hall / reed sensor | 0–10 mA | 15 mA | 3.3 V |
| Active buzzer | 25 mA | 80 mA | 3.3/5 V per selected part |
| Servo motor | 100 mA | 700–1000 mA stall/startup | 5 V dedicated branch |
| LEDs and buttons | 10 mA | 20 mA | 3.3 V |
| **Estimated total** | **335 mA** | **1.6 A** | **5 V input equivalent** |

A certified 5 V, 2–3 A adapter is recommended after the exact servo is chosen.
Select F1/F2 after measuring the assembled product; the BOM ratings are
starting points, not guarantees. A servo startup pulse must not share a thin
wire or weak regulator path with the ESP32.

## Protection and decoupling

The power path is `5V_IN -> F1 -> D1 -> 5V_PROTECTED`. The ESP32 board's
documented 5 V/VIN input and 3.3 V regulator are used only if the exact board
datasheet supports this path. Otherwise add a dedicated, thermally-rated
3.3 V regulator in the next hardware revision.

- C1–C5: 100 nF ceramic at each module or rail entry.
- C6: 470 µF, 10 V low-ESR bulk capacitor near the ESP32/buzzer entry.
- C7: 1000 µF, 10 V low-ESR capacitor at the servo connector; increase after
  measuring servo startup and stall behavior.
- Q1's 100 kΩ gate pulldown ensures the buzzer is off while GPIO19 is reset.
- A magnetic buzzer requires flyback protection; verify the selected part.

## Fail-safe behavior

- Power loss leaves the compartment mechanically closed/unchanged; there is no
  motor, latch, heater, or dispensing actuator in this Part 1 design.
- A missing, noisy, disconnected, or out-of-range sensor cannot be treated as
  `DOSE_TAKEN`. Firmware must require the defined stable transitions.
- A local button must be able to mute/snooze an alarm without Wi-Fi. Network
  availability is not a safety dependency for the local reminder.
- The hardware must indicate a sensor/power fault locally and preserve the
  last known event for later synchronization in the firmware layer.
- Keep mains voltage outside the product. Use only a certified low-voltage
  adapter and inspect the USB cable for strain damage.

## Sensor logic

For the default normally-open microswitch, a stable `LOW` means the lid is
closed and a stable `HIGH` means the lid is open only after the pull-up and
mechanical actuation have been verified. Require three consistent samples over
at least 300 ms before a state change. Hall and reed sensors need the same
debounce and a calibration of their magnet gap.

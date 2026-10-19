# Power and fail-safe design

## Design assumptions

The prototype uses a certified isolated 5 V, 2 A USB supply. The figures below
are conservative design estimates; measure the final parts rather than treating
them as certification evidence.

| Load | Typical | Design peak | Rail |
| --- | ---: | ---: | --- |
| ESP32 Wi-Fi and MCU | 160 mA | 500 mA | 5 V input via board regulator |
| SH1106 OLED | 25 mA | 40 mA | 3.3 V |
| HC-SR04 | 15 mA | 20 mA | 5 V |
| Active buzzer | 25 mA | 80 mA | 3.3/5 V per selected part |
| LEDs and buttons | 10 mA | 20 mA | 3.3 V |
| **Estimated total** | **235 mA** | **660 mA** | **5 V input equivalent** |

A 2 A adapter gives margin for Wi-Fi bursts and regulator losses. Select the
polyfuse after measuring the assembled product; the BOM's 500 mA hold rating
is a starting point, not a guarantee.

## Protection and decoupling

The power path is `5V_IN -> F1 -> D1 -> 5V_PROTECTED`. The ESP32 board's
documented 5 V/VIN input and 3.3 V regulator are used only if the exact board
datasheet supports this path. Otherwise add a dedicated, thermally-rated
3.3 V regulator in the next hardware revision.

- C1–C5: 100 nF ceramic at each module or rail entry.
- C6: 470 µF, 10 V low-ESR bulk capacitor near the ESP32/buzzer entry.
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

## Sensor thresholds

Ultrasonic starting thresholds:

- distance `< 5 cm`: closed
- distance `> 8 cm`: open
- 5–8 cm: uncertain; hold the prior state and do not log a dose

Require three consistent samples over at least 300 ms before a state change.
The final threshold must be measured with the real compartment, lid material,
sensor angle, and medication insert installed.

For microswitch mode, a stable `LOW` means contact closed and `HIGH` means
compartment open only when the pull-up and switch wiring have been verified.

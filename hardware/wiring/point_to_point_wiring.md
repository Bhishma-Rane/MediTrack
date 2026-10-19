# Point-to-point wiring and harness specification

Use keyed connectors where possible. Connector pin numbers below are the
controller-side numbers, viewed from the wire-entry side. Keep all harnesses
under 300 mm in the prototype; longer external cables need ESD and filtering
review.

## J1 — OLED (4-pin)

| J1 pin | Net | ESP32 destination | Suggested wire |
| ---: | --- | --- | --- |
| 1 | `POWER_3V3` | 3V3 | red |
| 2 | `I2C_SDA` | GPIO21 | blue |
| 3 | `I2C_SCL` | GPIO22 | yellow |
| 4 | `GROUND` | GND | black |

Confirm the OLED module's silk-screen order. Some inexpensive modules expose
`GND/VCC/SCL/SDA` in a different order.

## J2 — lid/compartment sensor (3-pin)

| J2 pin | Net | Destination |
| ---: | --- | --- |
| 1 | `COMPARTMENT_SENSE` | Normally-open lid switch, Hall sensor output, or reed sensor output to GPIO18 |
| 2 | `POWER_3V3` | Sensor VCC when the selected sensor needs power |
| 3 | `GROUND` | Sensor ground; a microswitch COM contact returns here |

For the default microswitch, use the ESP32 internal pull-up and wire the
normally-open contact between J2-1 and J2-3. A disconnected switch must resolve
to open/unknown, never to a successful dose.

## J3 — buzzer (2-pin)

| J3 pin | Net | Destination |
| ---: | --- | --- |
| 1 | `BUZZER+` | protected 5 V or 3.3 V, matching B1 rating |
| 2 | `BUZZER-` | Q1 drain; Q1 source returns to GND |

GPIO19 connects only to Q1 gate through the gate resistor/trace. Add a diode
across B1 if the selected buzzer is magnetic or otherwise inductive.

## J4 — buttons (4-pin)

Each button is normally open and shorts its signal to ground when pressed.

| J4 pin | Net | ESP32 GPIO |
| ---: | --- | ---: |
| 1 | `BTN_CONFIRM` | 4 |
| 2 | `BTN_MUTE_SNOOZE` | 16 |
| 3 | `BTN_SNOOZE` | 17 |
| 4 | `GROUND` | GND |

Firmware must accept a stable transition for 50 ms before changing state.
Releasing a button must also be debounced. For a user-accessible production
harness, add an ESD review and optional 100 Ω series resistors at the GPIO end.

## J5 — status LEDs (3-pin)

| J5 pin | Net | ESP32 path |
| ---: | --- | --- |
| 1 | `LED_GREEN` | GPIO2 -> R4 680 Ω -> LED1 anode; LED1 cathode -> GND |
| 2 | `LED_RED` | GPIO15 -> R5 680 Ω -> LED2 anode; LED2 cathode -> GND |
| 3 | `GROUND` | GND |

Check boot behavior with LEDs attached because GPIO2 and GPIO15 are ESP32
strapping pins. If the chosen board cannot boot reliably, keep the specified
logical nets but move the LED load to a transistor/expander in a future PCB
revision; do not solve it by forcing a boot pin with a strong external pull.

## J6 — dispenser servo (3-pin)

| J6 pin | Net | Destination |
| ---: | --- | --- |
| 1 | `DISPENSER_SERVO` | Servo signal from GPIO23 through optional 220 Ω resistor |
| 2 | `POWER_5V` | Dedicated fused servo branch; never an ESP32 GPIO or 3.3 V rail |
| 3 | `GROUND` | Common ground/star return near power entry |

The servo actuates a one-dose gate. It does not count pills by itself. Use 50 Hz
hardware PWM, calibrated endpoints, and a positive mechanical closed stop. Add
C7 (typically 1000 µF) near the connector and size F2 from the exact servo
stall current.

## J7 — optional chute confirmation sensor (3-pin)

| J7 pin | Net | Destination |
| ---: | --- | --- |
| 1 | `DISPENSE_CONFIRM` | 3.3 V-safe optical output or chute flap switch to GPIO27 |
| 2 | `POWER_3V3` | Sensor supply when required |
| 3 | `GROUND` | Sensor return |

This confirms that an object passed through the chute. It does not prove the
correct medication was dispensed or swallowed.

## Grounding and routing

- Use a common ground, with the buzzer return routed directly to the power
  entry rather than through the OLED or sensor return.
- Place C1–C5 at module power pins, C6 near the ESP32/buzzer power entry, and
  C7 near the servo connector.
- Twist each signal with a ground return in longer sensor/button harnesses.
- Add strain relief at the enclosure wall; the connector must not carry cable
  pull forces into the ESP32 header.

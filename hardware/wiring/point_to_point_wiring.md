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

## J6/J8/J9 — medicine-cylinder servos (three 3-pin connectors)

| Connector/pin | Net | Destination |
| ---: | --- | --- |
| J6-1 | `SERVO_CYLINDER_1` | Cylinder 1 servo signal from GPIO23 |
| J8-1 | `SERVO_CYLINDER_2` | Cylinder 2 servo signal from GPIO25 |
| J9-1 | `SERVO_CYLINDER_3` | Cylinder 3 servo signal from GPIO26 |
| J6/J8/J9-2 | `POWER_5V` | Shared dedicated fused servo branch; never an ESP32 GPIO or 3.3 V rail |
| J6/J8/J9-3 | `GROUND` | Common ground/star return near power entry |

Each 180-degree servo actuates the gate for one cylinder. The cylinder itself
does not need to rotate. Use 50 Hz hardware PWM, calibrated endpoints, and a
positive mechanical closed stop for every cylinder. Add C7 near the three-servo
power distribution and size F2 from the exact servo stall current. Do not
command all three servos to move simultaneously until the supply is verified.

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

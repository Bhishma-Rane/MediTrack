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

## J2 — mutually exclusive compartment sensor (4-pin)

| J2 pin | Ultrasonic mode | Microswitch mode |
| ---: | --- | --- |
| 1 | `POWER_5V` to HC-SR04 VCC | leave unpopulated |
| 2 | `ULTRASONIC_TRIG` to HC-SR04 TRIG | leave unpopulated |
| 3 | HC-SR04 ECHO -> R1/R2/R3 divider -> GPIO18 | microswitch NO contact -> GPIO18; configure pull-up/pull-down intentionally |
| 4 | `GROUND` to HC-SR04 GND | microswitch COM -> GND |

In ultrasonic mode, wire `ECHO—R1 (10 kΩ)—SENSE_NODE—R2 (20 kΩ)—GND`, then
`SENSE_NODE—R3 (1 kΩ)—GPIO18`. Measure `SENSE_NODE` before connecting the
ESP32. In switch mode, do not leave the sense input floating: use the ESP32
internal pull-up and a normally-open contact to ground, or fit an external
10 kΩ pull-up at the controller.

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

## Grounding and routing

- Use a common ground, with the buzzer return routed directly to the power
  entry rather than through the OLED or sensor return.
- Place C1–C5 at module power pins and C6 near the ESP32/buzzer power entry.
- Twist each signal with a ground return in longer sensor/button harnesses.
- Add strain relief at the enclosure wall; the connector must not carry cable
  pull forces into the ESP32 header.

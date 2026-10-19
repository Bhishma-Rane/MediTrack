# Part 2 ESP32 wiring quick reference

This is the point-to-point wiring for the firmware in
`firmware/esp32_meditrack`. Keep the ESP32 unpowered while checking continuity.
All grounds must be common, but route the servo and buzzer returns directly to
the power-entry/star-ground point rather than through the OLED ground lead.

## Signal wiring

| Function | ESP32 pin | Connect to | Electrical requirement |
| --- | ---: | --- | --- |
| SH1106 SDA | GPIO21 | OLED SDA | 3.3 V I2C |
| SH1106 SCL | GPIO22 | OLED SCL | 3.3 V I2C |
| Lid switch | GPIO18 | Normally-open switch to GND | `INPUT_PULLUP`; LOW means lid closed |
| Optional chute sensor | GPIO27 | 3.3 V-safe sensor output | `INPUT_PULLUP`; LOW means object detected |
| Buzzer control | GPIO19 | 100 Ω–1 kΩ resistor to Q1 MOSFET gate | GPIO drives gate only |
| Confirm button | GPIO4 | Normally-open button to GND | `INPUT_PULLUP`, 50 ms debounce |
| Mute/snooze button | GPIO16 | Normally-open button to GND | `INPUT_PULLUP`, 50 ms debounce |
| Snooze button | GPIO17 | Normally-open button to GND | `INPUT_PULLUP`, 50 ms debounce |
| Green status LED | GPIO2 | 680 Ω resistor, then LED anode | Verify boot strap behavior |
| Red status LED | GPIO15 | 680 Ω resistor, then LED anode | Verify boot strap behavior |
| Cylinder 1 servo signal | GPIO23 | Servo signal wire | 50 Hz PWM |
| Cylinder 2 servo signal | GPIO25 | Servo signal wire | 50 Hz PWM |
| Cylinder 3 servo signal | GPIO26 | Servo signal wire | 50 Hz PWM |

OLED VCC goes to 3.3 V and OLED GND to GND. For a microswitch, connect COM
to GND and NO to GPIO18; do not connect a switch contact to 5 V.

## Power wiring

```text
Certified isolated 5 V supply
  ├── protected logic branch ── ESP32 VIN/5V
  │                             └── ESP32 3V3 → OLED/sensor logic
  └── F2 fused servo branch ─── servo red wires (5 V)
                                  └── 2200 µF bulk capacitor at servo rail

ESP32 GND ───── servo brown/black wires ───── buzzer/MOSFET source ───── sensor GND
```

Use a logic-level N-MOSFET for an active buzzer: buzzer negative to drain,
source to GND, and a 100 kΩ gate-to-source pulldown. Add a flyback diode if the
chosen buzzer is magnetic/inductive. Never power a servo from an ESP32 GPIO or
the 3.3 V pin. Do not put mains voltage inside the enclosure.

## Bring-up order

1. Verify the 5 V and 3.3 V rails and common ground with a meter.
2. Test the ESP32, OLED, buttons, and lid switch with the servo branch
   disconnected.
3. Attach one servo at a time. Calibrate its closed endpoint against a positive
   mechanical stop using inert test objects.
4. Attach the chute sensor and confirm that a sensor transition only reports an
   object-passed event; it does not prove medication identity or ingestion.
5. Only after all checks pass, connect the backend and run the full demo.

The complete connector-level harness is in
[`point_to_point_wiring.md`](point_to_point_wiring.md). This prototype is not a
validated medical device.
